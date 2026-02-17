from __future__ import annotations

import sys

from tuxido.core._metadata import get_versions
from tuxido.core.models import (
    ValidationError,
    ValidationMetadata,
    ValidationResult,
    ValidationSummary,
)
from tuxido.core.validators import validate_dom, validate_sandbox, validate_static, validate_syntax


def validate(
    source: str,
    filename: str = "app.py",
    depth: str = "fast",
    timeout: int | None = None,
) -> ValidationResult:
    """Validate code using the full validation pipeline.

    Args:
        source: Python source code to validate.
        filename: Name of file being validated.
        depth: "fast" (L1+L2) or "full" (L1-L4).
        timeout: Timeout for L4 sandbox in seconds.

    Returns:
        ValidationResult with all validation findings.

    """
    l1_result = validate_syntax(source, filename=filename)

    if l1_result.status != "pass":
        return l1_result

    all_errors = []

    l2_result = validate_static(source, filename=filename)
    all_errors.extend(l2_result.errors)

    is_windows = sys.platform == "win32"

    if depth == "full":
        if is_windows:
            all_errors.append(
                ValidationError(
                    level="L3",
                    code="DOM001",
                    message="Platform: Windows - L3 DOM Testing: Limited functionality",
                    line=None,
                    column=None,
                    severity="warning",
                    llm_action="DOM testing works best on Unix systems",
                ),
            )

        l3_result = validate_dom(source, filename=filename)
        if l3_result.status == "skipped":
            all_errors.append(
                ValidationError(
                    level="L3",
                    code="DOM000",
                    message="L3 DOM Testing skipped: No valid Textual app found",
                    line=None,
                    column=None,
                    severity="warning",
                    llm_action="Ensure your class inherits from App",
                ),
            )
        elif l3_result.errors:
            all_errors.extend(l3_result.errors)

        if is_windows:
            all_errors.append(
                ValidationError(
                    level="L4",
                    code="S000",
                    message="Platform: Windows - L4 Sandbox: Limited isolation. Code will run with reduced security restrictions.",
                    line=None,
                    column=None,
                    severity="warning",
                    llm_action="L4 sandbox works best on Unix systems",
                ),
            )
            l4_result = ValidationResult(
                status="skipped",
                errors=[],
                summary=ValidationSummary(total=0, errors=0, warnings=0),
                metadata=_build_metadata(),
            )
        else:
            sandbox_timeout = timeout or 5
            l4_result = validate_sandbox(source, filename=filename, timeout=sandbox_timeout)

        if l4_result.status != "skipped" and l4_result.errors:
            all_errors.extend(l4_result.errors)

    error_count = sum(1 for e in all_errors if e.severity == "error")
    warn_count = sum(1 for e in all_errors if e.severity == "warning")

    if all_errors:
        return ValidationResult(
            status="fail",
            errors=all_errors,
            summary=ValidationSummary(
                total=len(all_errors),
                errors=error_count,
                warnings=warn_count,
            ),
            metadata=_build_metadata(),
        )

    return ValidationResult(
        status="pass",
        errors=[],
        summary=ValidationSummary(total=0, errors=0, warnings=0),
        metadata=_build_metadata(),
    )


def _build_metadata() -> ValidationMetadata:
    versions = get_versions()
    return ValidationMetadata(
        version=versions["tuxido"] or "unknown",
        python=versions["python"] or "unknown",
        textual=versions["textual"],
    )
