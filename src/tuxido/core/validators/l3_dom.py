from __future__ import annotations

import ast

from tuxido.core._metadata import get_versions
from tuxido.core.models import (
    ValidationError,
    ValidationMetadata,
    ValidationResult,
    ValidationSummary,
)

VALID_TEXTUAL_WIDGETS = {
    "App",
    "Static",
    "Button",
    "Input",
    "Label",
    "ListView",
    "ListItem",
    "TextArea",
    "Checkbox",
    "RadioSet",
    "RadioButton",
    "Switch",
    "Slider",
    "ProgressBar",
    "DataTable",
    "Tree",
    "TreeNode",
    "DirectoryTree",
    "FileTree",
    "Tabs",
    "Tab",
    "TabbedContent",
    "ContentSwitcher",
    "SplitView",
    "HSplit",
    "VSplit",
    "Panel",
    "Header",
    "Footer",
    "Sidebar",
    "Sparkline",
    "BarChart",
    "LineChart",
    "Histogram",
    "Logging",
    "RichLog",
    "TextLog",
    "Pretty",
    "Rule",
    "LoadingIndicator",
    "Placeholder",
    "Badge",
    "Tag",
    "Notify",
    "Markdown",
    "MarkdownViewer",
    "Code",
    "CodePane",
    "Json",
    "Yaml",
}

WEB_ONLY_CSS = {
    "flex",
    "flex-grow",
    "flex-shrink",
    "flex-basis",
    "grid-template-columns",
    "grid-template-rows",
}


class DOMAnalyzer(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: list[ValidationError] = []
        self.widgets: list[dict[str, str | None]] = []  # type: ignore[valid-type]
        self.compose_methods: set[str] = set()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for base in node.bases:
            if isinstance(base, ast.Attribute):
                if isinstance(base.value, ast.Name):
                    if base.value.id == "App" or base.value.id == "Widget":
                        self._analyze_widget_class(node)
            elif isinstance(base, ast.Name):
                if base.id in ("App", "Widget"):
                    self._analyze_widget_class(node)
        self.generic_visit(node)

    def _analyze_widget_class(self, node: ast.ClassDef) -> None:
        widget_name = node.name

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name == "compose":
                    for stmt in ast.walk(item):
                        if isinstance(stmt, ast.Yield) or isinstance(stmt, ast.YieldFrom):
                            yield_expr = stmt.value
                            if yield_expr and isinstance(yield_expr, ast.Call):
                                widget = self._extract_widget(yield_expr)
                                if widget:
                                    self.widgets.append(widget)
                                    if "id" not in widget or not widget["id"]:
                                        self.errors.append(
                                            _create_error(
                                                code="D003",
                                                message=f"Widget {widget['type']} without ID in {widget_name}.compose(). Widgets should have IDs for testing.",
                                                line=yield_expr.lineno,
                                                llm_action=f"Add id='some_id' to the {widget['type']} widget on line {yield_expr.lineno}",
                                            ),
                                        )

    def _extract_widget(self, call: ast.Call) -> dict[str, str | None] | None:
        if isinstance(call.func, ast.Name):
            widget_type = call.func.id
        elif isinstance(call.func, ast.Attribute):
            widget_type = call.func.attr
        else:
            return None

        widget_id: str | None = None
        for keyword in call.keywords:
            if keyword.arg == "id":
                if isinstance(keyword.value, ast.Constant):
                    widget_id = str(keyword.value.value)

        return {"type": widget_type, "id": widget_id}


def _create_error(
    code: str,
    message: str,
    line: int | None,
    llm_action: str,
) -> ValidationError:
    return ValidationError(
        level="L3",
        code=code,
        message=message,
        line=line,
        column=None,
        severity="warning" if code.startswith("DOM003") else "error",
        llm_action=llm_action,
    )


def validate_dom(source: str, filename: str = "app.py") -> ValidationResult:
    """Validate DOM structure of Textual app."""
    if not source or not source.strip():
        return ValidationResult(
            status="fail",
            errors=[
                ValidationError(
                    level="L3",
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
            status="skipped",
            errors=[],
            summary=ValidationSummary(total=0, errors=0, warnings=0),
            metadata=_build_metadata(),
        )

    analyzer = DOMAnalyzer()
    analyzer.visit(tree)

    if analyzer.errors:
        return ValidationResult(
            status="fail",
            errors=analyzer.errors,
            summary=ValidationSummary(
                total=len(analyzer.errors),
                errors=0,
                warnings=len(analyzer.errors),
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
