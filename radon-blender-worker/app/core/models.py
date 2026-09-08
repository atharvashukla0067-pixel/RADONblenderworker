"""Request and response models for the RADON Blender Worker API."""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator


MAX_ENTITY_LEN = 200
MAX_DESCRIPTION_LEN = 2000
MAX_REQUEST_ID_LEN = 256
VALID_OUTPUT_FORMATS = {"glb", "gltf"}
VALID_QUALITY_LEVELS = {"preview", "standard", "high"}


class GenerateRequest(BaseModel):
    requestId: str = Field(..., max_length=MAX_REQUEST_ID_LEN)
    entity: str = Field(..., max_length=MAX_ENTITY_LEN)
    category: str = Field(..., max_length=100)
    description: str = Field(default="", max_length=MAX_DESCRIPTION_LEN)
    quality: str = Field(default="standard")
    outputFormat: str = Field(default="glb")

    @field_validator("requestId", "entity", "category", "description")
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("must be a string")
        # Reject control characters and null bytes (path traversal / injection guard)
        cleaned = v.replace("\x00", "").replace("\r", "").replace("\n", " ")
        return cleaned.strip()

    @field_validator("outputFormat")
    @classmethod
    def validate_format(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in VALID_OUTPUT_FORMATS:
            raise ValueError(f"outputFormat must be one of {VALID_OUTPUT_FORMATS}")
        return v

    @field_validator("quality")
    @classmethod
    def validate_quality(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in VALID_QUALITY_LEVELS:
            raise ValueError(f"quality must be one of {VALID_QUALITY_LEVELS}")
        return v


class HealthResponse(BaseModel):
    status: str
    blender: str
    blender_path: Optional[str] = None
    version: Optional[str] = None
    worker: str
    capabilities: list[str] = []
    glb_export: bool = False


class GenerationMetadata(BaseModel):
    blender_version: str = ""
    generation_strategy: str = ""
    quality: str = ""
    category: str = ""
    entity: str = ""
    blender_scene_objects: int = 0
    generation_time_seconds: float = 0.0


class GenerateResponse(BaseModel):
    success: bool
    requestId: str
    origin: str = "BLENDER_GENERATED"
    verification: str
    outputFormat: str
    assetUrl: str
    assetPath: str
    fileSizeBytes: int
    metadata: GenerationMetadata
    limitations: list[str] = []


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    requestId: Optional[str] = None
    detail: Optional[Any] = None
