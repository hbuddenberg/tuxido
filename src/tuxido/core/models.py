"""Tuxido core models - ValidationResult schema."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ValidationError(BaseModel):
    """Single validation finding."""

    level: Literal["L1", "L2", "L3", "L4"] = Field(
        description="Validation layer that produced this error",
    )
    code: str = Field(
        pattern=r"^[EWDS]\d{3}$", description="Error code (e.g., E101, W201, D003, S001)",
    )
    message: str = Field(description="Human-readable message in Problem-Impact-Solution format")
    line: int | None = Field(default=None, description="Line number where error found")
    column: int | None = Field(default=None, description="Column number where error found")
    severity: Literal["error", "warning"] = Field(description="Severity level")
    llm_action: str = Field(description="LLM instruction for auto-correction")


class ValidationSummary(BaseModel):
    """Aggregate counts for validation results."""

    total: int = Field(description="Total number of findings")
    errors: int = Field(description="Number of errors")
    warnings: int = Field(description="Number of warnings")


class ValidationMetadata(BaseModel):
    """Runtime context for validation."""

    version: str = Field(description="tuxido version")
    python: str = Field(description="Python version")
    textual: str | None = Field(default=None, description="Textual version if installed")


class ValidationResult(BaseModel):
    """Canonical output format. ALL validators produce this."""

    status: Literal["pass", "fail", "error", "skipped"] = Field(
        description="Overall validation status",
    )
    errors: list[ValidationError] = Field(
        default_factory=list, description="List of validation errors/warnings",
    )
    summary: ValidationSummary = Field(description="Aggregate summary of findings")
    metadata: ValidationMetadata = Field(description="Runtime metadata")
