from __future__ import annotations

import ast

from tuxido.core._metadata import get_versions
from tuxido.core.models import (
    ValidationError,
    ValidationMetadata,
    ValidationResult,
    ValidationSummary,
)

FORBIDDEN_IMPORTS = {
    "os": "E201",
    "subprocess": "E201",
    "socket": "E201",
    "eval": "E201",
    "exec": "E201",
    "builtins": "E201",
}

REQUIRED_IMPORTS = {
    "textual.app": ["App"],
}


class StaticAnalyzer(ast.NodeVisitor):
    """AST visitor for static analysis of Python code."""

    def __init__(self) -> None:
        self.errors: list[ValidationError] = []
        self.imports: set[str] = set()
        self.from_imports: dict[str, set[str]] = {}
        self.async_functions: set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.add(alias.name.split(".")[0])

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if module not in self.from_imports:
            self.from_imports[module] = set()
        for alias in node.names:
            self.from_imports[module].add(alias.name)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.async_functions.add(node.name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        func_name = self._get_func_name(node.func)
        if func_name in ("time.sleep",):
            self.errors.append(_create_error(
                code="E202",
                message=f"Blocking call '{func_name}' found. This blocks the event loop.",
                line=node.lineno,
                llm_action=f"Replace time.sleep() with asyncio.sleep() on line {node.lineno}",
            ))
        elif func_name in ("requests.get", "requests.post", "requests.request"):
            self.errors.append(_create_error(
                code="E202",
                message=f"Blocking HTTP call '{func_name}' found in async context.",
                line=node.lineno,
                llm_action=f"Replace requests with httpx or aiohttp on line {node.lineno}",
            ))
        self.generic_visit(node)

    def _get_func_name(self, node: ast.expr) -> str:
        if isinstance(node, ast.Attribute):
            value = node.value
            if isinstance(value, ast.Name):
                return f"{value.id}.{node.attr}"
        elif isinstance(node, ast.Name):
            return node.id
        return ""


def _create_error(
    code: str,
    message: str,
    line: int | None,
    llm_action: str,
) -> ValidationError:
    return ValidationError(
        level="L2",
        code=code,
        message=message,
        line=line,
        column=None,
        severity="error",
        llm_action=llm_action,
    )


def validate_static(source: str, filename: str = "app.py") -> ValidationResult:
    """Validate code using static analysis.

    Args:
        source: Python source code to validate.
        filename: Name of file being validated.

    Returns:
        ValidationResult with static analysis findings.

    """
    if not source or not source.strip():
        return ValidationResult(
            status="fail",
            errors=[
                ValidationError(
                    level="L2",
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
        tree = ast.parse(source)
    except SyntaxError:
        return ValidationResult(
            status="fail",
            errors=[],
            summary=ValidationSummary(total=0, errors=0, warnings=0),
            metadata=_build_metadata(),
        )

    analyzer = StaticAnalyzer()
    analyzer.visit(tree)

    errors: list[ValidationError] = []

    for imp in analyzer.imports:
        if imp in FORBIDDEN_IMPORTS:
            errors.append(_create_error(
                code=FORBIDDEN_IMPORTS[imp],
                message=f"Forbidden import '{imp}' detected. This could be unsafe.",
                line=None,
                llm_action=f"Remove the '{imp}' import. Use Textual APIs instead.",
            ))

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                if node.value.id == "os" and node.attr in ("system", "popen", "spawn"):
                    errors.append(_create_error(
                        code="E201",
                        message=f" Dangerous os.{node.attr}() call detected.",
                        line=node.lineno,
                        llm_action=f"Remove os.{node.attr}() call on line {node.lineno}",
                    ))

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec"):
                errors.append(_create_error(
                    code="E201",
                    message=f"Dangerous {node.func.id}() call detected.",
                    line=node.lineno,
                    llm_action=f"Remove {node.func.id}() call on line {node.lineno}",
                ))
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id == "__import__":
                        errors.append(_create_error(
                            code="E201",
                            message="Dynamic import via __import__ detected.",
                            line=node.lineno,
                            llm_action=f"Replace __import__() with static import on line {node.lineno}",
                        ))

    for func_name in analyzer.async_functions:
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == func_name:
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            func_call = child.func
                            if isinstance(func_call, ast.Attribute):
                                if isinstance(func_call.value, ast.Name):
                                    if func_call.value.id == "time" and func_call.attr == "sleep":
                                        errors.append(_create_error(
                                            code="E202",
                                            message=f"time.sleep() found in function '{func_name}'. This blocks the event loop.",
                                            line=child.lineno,
                                            llm_action=f"Replace time.sleep() with await asyncio.sleep() in function '{func_name}' on line {child.lineno}",
                                        ))

    if errors:
        return ValidationResult(
            status="fail",
            errors=errors,
            summary=ValidationSummary(
                total=len(errors),
                errors=len(errors),
                warnings=0,
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
