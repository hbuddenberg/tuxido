from __future__ import annotations

import ast

from tuxido.core._metadata import get_versions
from tuxido.core.models import (
    ValidationError,
    ValidationMetadata,
    ValidationResult,
    ValidationSummary,
)


def validate_syntax(source: str, filename: str = "app.py") -> ValidationResult:
    """Validate Python syntax using AST parsing.

    Args:
        source: Python source code to validate.
        filename: Name of file being validated (for error messages).

    Returns:
        ValidationResult with syntax errors if any.

    """
    if not source or not source.strip():
        return ValidationResult(
            status="fail",
            errors=[
                ValidationError(
                    level="L1",
                    code="E103",
                    message="Code cannot be empty",
                    line=None,
                    column=None,
                    severity="error",
                    llm_action="Add Python code to the file",
                ),
            ],
            summary=ValidationSummary(total=1, errors=1, warnings=0),
            metadata=_build_metadata(),
        )

    try:
        ast.parse(source)
    except SyntaxError as e:
        return ValidationResult(
            status="fail",
            errors=[
                ValidationError(
                    level="L1",
                    code="E101",
                    message=f"Syntax error at line {e.lineno}: {e.msg}",
                    line=e.lineno,
                    column=e.offset,
                    severity="error",
                    llm_action=f"Fix syntax error at line {e.lineno}: {e.msg}",
                ),
            ],
            summary=ValidationSummary(total=1, errors=1, warnings=0),
            metadata=_build_metadata(),
        )
    except UnicodeDecodeError as e:
        return ValidationResult(
            status="fail",
            errors=[
                ValidationError(
                    level="L1",
                    code="E102",
                    message=f"Encoding error: {e.reason}",
                    line=None,
                    column=None,
                    severity="error",
                    llm_action="Ensure file is UTF-8 encoded",
                ),
            ],
            summary=ValidationSummary(total=1, errors=1, warnings=0),
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
