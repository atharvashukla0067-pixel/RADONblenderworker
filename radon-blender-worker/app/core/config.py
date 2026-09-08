"""Application configuration for the RADON Blender Worker."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    blender_path: str = os.environ.get("BLENDER_PATH", "/usr/bin/blender")
    worker_name: str = "radon-blender-worker"
    output_dir: Path = Path(os.environ.get("OUTPUT_DIR", "/tmp/radon-output"))
    job_timeout: int = int(os.environ.get("JOB_TIMEOUT", "120"))
    max_output_size_mb: int = int(os.environ.get("MAX_OUTPUT_SIZE_MB", "100"))
    host: str = os.environ.get("HOST", "0.0.0.0")
    port: int = int(os.environ.get("PORT", "8001"))

    model_config = {"env_prefix": ""}


settings = Settings()
