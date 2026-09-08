"""Secure temporary job directory management with isolation and cleanup."""

from __future__ import annotations

import os
import shutil
import tempfile
import logging
from pathlib import Path
from typing import Optional

from .config import settings

logger = logging.getLogger("radon-blender-worker")


class JobWorkspace:
    """Isolated temporary directory for a single generation job.

    Creates a unique temp directory, provides paths for the Blender script
    and output GLB, and cleans up safely when done.
    """

    def __init__(self, job_id: str) -> None:
        self.job_id: str = job_id
        self._base: Path = Path(tempfile.mkdtemp(prefix=f"radon_job_{job_id}_"))
        self._output_dir: Path = settings.output_dir / job_id
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._cleaned: bool = False

    @property
    def work_dir(self) -> Path:
        return self._base

    @property
    def script_path(self) -> Path:
        return self._base / "generate.py"

    @property
    def output_path(self) -> Path:
        return self._output_dir / "output.glb"

    @property
    def output_dir(self) -> Path:
        return self._output_dir

    def write_script(self, script_content: str) -> Path:
        """Write the Blender Python script to the job directory."""
        path = self.script_path
        path.write_text(script_content, encoding="utf-8")
        return path

    def validate_output(self) -> tuple[bool, int]:
        """Check that the output GLB exists and is non-empty."""
        p = self.output_path
        if not p.exists():
            return False, 0
        size = p.stat().st_size
        if size == 0:
            return False, 0
        if size > settings.max_output_size_mb * 1024 * 1024:
            return False, -1
        return True, size

    def cleanup_work_dir(self) -> None:
        """Remove the temporary working directory (keeps the output dir for retrieval)."""
        if self._cleaned:
            return
        try:
            shutil.rmtree(self._base, ignore_errors=True)
        except Exception as exc:
            logger.warning("Failed to clean work dir %s: %s", self._base, exc)
        self._cleaned = True

    def cleanup_output(self) -> None:
        """Remove the output directory as well (used on error or explicit cleanup)."""
        self.cleanup_work_dir()
        try:
            shutil.rmtree(self._output_dir, ignore_errors=True)
        except Exception as exc:
            logger.warning("Failed to clean output dir %s: %s", self._output_dir, exc)
