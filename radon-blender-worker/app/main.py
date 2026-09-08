"""RADON Blender Worker — FastAPI application.

A standalone service that generates 3D assets using a real headless Blender runtime.
This service is separate from the RADON frontend and serves as the BLENDER_WORKER_URL target.
"""

from __future__ import annotations

import os
import re
import time
import uuid
import logging
import threading
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .core.config import settings
from .core.models import (
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
    GenerationMetadata,
    ErrorResponse,
)
from .core.blender_runner import blender_runner, BlenderNotFoundError
from .core.workspace import JobWorkspace
from .strategies.registry import strategy_registry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("radon-blender-worker")

app = FastAPI(
    title="RADON Blender Worker",
    description="Standalone 3D asset generation worker using real headless Blender.",
    version="1.0.0",
)

# Ensure output directory exists
settings.output_dir.mkdir(parents=True, exist_ok=True)

# Mount output directory for static file access (so generated GLBs are retrievable via HTTP)
app.mount("/assets", StaticFiles(directory=str(settings.output_dir)), name="assets")

# Thread lock for concurrent job safety
_job_lock = threading.Lock()


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Check the health of the worker and verify the real Blender executable."""
    blender_available = blender_runner.is_available()
    version = blender_runner.get_version() if blender_available else None
    exe_path = blender_runner.executable_path if blender_available else None

    return HealthResponse(
        status="healthy" if blender_available else "unavailable",
        blender="available" if blender_available else "unavailable",
        blender_path=exe_path,
        version=version,
        worker=settings.worker_name,
        capabilities=strategy_registry.list_categories() if blender_available else [],
        glb_export=blender_available,
    )


@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest) -> GenerateResponse:
    """Generate a 3D asset using real Blender.

    1. Validates the request.
    2. Creates an isolated temporary job directory.
    3. Selects a generation strategy based on category.
    4. Runs Blender headlessly with the generated Python script.
    5. Exports the result as GLB.
    6. Validates the GLB exists and is non-empty.
    7. Returns structured JSON with provenance and metadata.
    """
    # Verify Blender is available
    if not blender_runner.is_available():
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error="Blender runtime is not available on this worker.",
                requestId=req.requestId,
            ).model_dump(),
        )

    # Generate unique job ID
    job_id = uuid.uuid4().hex[:12]
    start_time = time.time()

    # Set env vars for the Blender subprocess (passed via environment, not CLI args)
    os.environ["QUALITY"] = req.quality
    os.environ["ENTITY"] = req.entity[:200]
    os.environ["CATEGORY"] = req.category[:100]

    workspace = JobWorkspace(job_id)

    try:
        # Select generation strategy
        strategy = strategy_registry.get_or_default(req.category)
        strategy_name = strategy.get_strategy_name()
        logger.info(
            "Job %s: entity='%s' category='%s' strategy=%s quality=%s",
            job_id, req.entity, req.category, strategy_name, req.quality,
        )

        # Build the Blender Python script
        script = strategy.build_script(req.entity, req.description, req.quality)
        workspace.write_script(script)

        # Run Blender headlessly (thread-safe with lock)
        with _job_lock:
            try:
                result = blender_runner.run_script(
                    script_path=str(workspace.script_path),
                    output_path=str(workspace.output_path),
                    timeout=settings.job_timeout,
                )
            except BlenderNotFoundError as exc:
                raise HTTPException(
                    status_code=503,
                    detail=ErrorResponse(
                        error=str(exc),
                        requestId=req.requestId,
                    ).model_dump(),
                )

        # Check Blender process output
        combined_output = result.stdout + result.stderr
        if result.returncode != 0:
            logger.error("Job %s: Blender exited with code %d", job_id, result.returncode)
            # Extract last meaningful lines for error detail
            error_lines = [l for l in combined_output.strip().split("\n") if "Error" in l or "ERROR" in l][-5:]
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    error="Blender generation failed.",
                    requestId=req.requestId,
                    detail=error_lines if error_lines else combined_output[-500:],
                ).model_dump(),
            )

        # Validate the output GLB
        valid, size = workspace.validate_output()
        if not valid:
            if size == -1:
                raise HTTPException(
                    status_code=413,
                    detail=ErrorResponse(
                        error="Generated GLB exceeds maximum allowed size.",
                        requestId=req.requestId,
                    ).model_dump(),
                )
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    error="GLB output file is missing or empty.",
                    requestId=req.requestId,
                ).model_dump(),
            )

        # Parse mesh count from Blender output
        mesh_count = 0
        mesh_match = re.search(r"MESH_COUNT:\s*(\d+)", combined_output)
        if mesh_match:
            mesh_count = int(mesh_match.group(1))

        generation_time = time.time() - start_time
        blender_version = blender_runner.get_version() or "unknown"

        # Build the asset URL
        asset_url = f"/assets/{job_id}/output.glb"

        metadata = GenerationMetadata(
            blender_version=blender_version,
            generation_strategy=strategy_name,
            quality=req.quality,
            category=req.category,
            entity=req.entity,
            blender_scene_objects=mesh_count,
            generation_time_seconds=round(generation_time, 3),
        )

        limitations = strategy.get_limitations(req.entity)

        logger.info(
            "Job %s: SUCCESS — %d bytes, %d meshes, %.2fs",
            job_id, size, mesh_count, generation_time,
        )

        return GenerateResponse(
            success=True,
            requestId=req.requestId,
            origin="BLENDER_GENERATED",
            verification="BLENDER_GENERATED_APPROXIMATION",
            outputFormat="glb",
            assetUrl=asset_url,
            assetPath=str(workspace.output_path),
            fileSizeBytes=size,
            metadata=metadata,
            limitations=limitations,
        )

    except HTTPException:
        # Clean up on error
        workspace.cleanup_output()
        raise

    except Exception as exc:
        logger.exception("Job %s: Unexpected error", job_id)
        workspace.cleanup_output()
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="An unexpected error occurred during generation.",
                requestId=req.requestId,
                detail=str(exc)[:500],
            ).model_dump(),
        )

    finally:
        # Always clean up the temporary working directory (keep output for retrieval)
        workspace.cleanup_work_dir()


@app.get("/categories")
async def list_categories() -> dict[str, Any]:
    """List all supported generation categories."""
    return {
        "categories": strategy_registry.list_categories(),
        "worker": settings.worker_name,
    }


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with service info."""
    return {
        "service": settings.worker_name,
        "version": "1.0.0",
        "endpoints": "/health, /generate, /categories",
    }
