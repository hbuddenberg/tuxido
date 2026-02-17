from __future__ import annotations

import os
import subprocess
import sys
import tempfile

from tuxido.core._metadata import get_versions
from tuxido.core.models import (
    ValidationError,
    ValidationMetadata,
    ValidationResult,
    ValidationSummary,
)


def validate_sandbox(
    source: str,
    filename: str = "app.py",
    timeout: int = 5,
) -> ValidationResult:
    """Execute code in sandbox with timeout and security restrictions."""
    if not source or not source.strip():
        return ValidationResult(
            status="fail",
            errors=[
                ValidationError(
                    level="L4",
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

    with tempfile.TemporaryDirectory() as tmpdir:
        app_path = os.path.join(tmpdir, "test_app.py")

        sandbox_code = f"""import sys
import os

os.chdir("/tmp")
os.environ.clear()

sys.stdout = open(os.devnull, "w")
sys.stderr = open(os.devnull, "w")

{source}

if __name__ == "__main__":
    try:
        if "app" in dir():
            app = app()
            print("APP_CREATED", flush=True)
    except Exception as e:
        print(f"ERROR: {{e}}", flush=True)
"""

        with open(app_path, "w") as f:
            f.write(sandbox_code)

        try:
            proc = subprocess.Popen(
                [sys.executable, app_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=tmpdir,
                env={},
            )

            try:
                stdout, stderr = proc.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                return ValidationResult(
                    status="fail",
                    errors=[
                        ValidationError(
                            level="L4",
                            code="S001",
                            message=f"Execution timeout after {timeout}s. Possible infinite loop detected.",
                            line=None,
                            column=None,
                            severity="error",
                            llm_action="Check for infinite loops in your code. Consider adding early exit conditions.",
                        ),
                    ],
                    summary=ValidationSummary(total=1, errors=1, warnings=0),
                    metadata=_build_metadata(),
                )

            if proc.returncode != 0:
                stderr_text = stderr.decode("utf-8", errors="ignore")
                return ValidationResult(
                    status="fail",
                    errors=[
                        ValidationError(
                            level="L4",
                            code="S002",
                            message=f"Execution failed: {stderr_text[:200]}",
                            line=None,
                            column=None,
                            severity="error",
                            llm_action="Fix the runtime error in your code.",
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

        except OSError as e:
            return ValidationResult(
                status="fail",
                errors=[
                    ValidationError(
                        level="L4",
                        code="S003",
                        message=f"Security restriction triggered: {e}",
                        line=None,
                        column=None,
                        severity="error",
                        llm_action="Your code attempted a restricted operation. Use Textual APIs instead.",
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
