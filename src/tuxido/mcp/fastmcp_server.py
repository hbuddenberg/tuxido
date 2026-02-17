from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

from tuxido.core.oracle import get_framework_info as oracle_framework_info
from tuxido.core.pipeline import validate


class ValidateInput(BaseModel):
    code: str
    depth: Literal["fast", "full"] = "fast"
    filename: str = "app.py"


class ValidateResult(BaseModel):
    status: str
    errors: list[dict[str, Any]]
    summary: dict[str, int]
    metadata: dict[str, Any]


def validate_tui(code: str, depth: str = "fast", filename: str = "app.py") -> dict[str, Any]:
    """Validate a Textual TUI application.

    Args:
        code: Python source code to validate.
        depth: Validation depth - "fast" (L1+L2) or "full" (L1-L4).
        filename: Name of the file being validated.

    Returns:
        ValidationResult as a dictionary.

    Use when:
    - You generate Python code for Textual apps
    - You want to check for syntax errors before running
    - You need static analysis of imports and async patterns

    Do NOT use when:
    - The code is not related to Textual/TUI applications
    - You need runtime behavior testing (use L3/L4 instead)

    """
    if not code or not code.strip():
        return {
            "status": "error",
            "errors": [{"message": "Code cannot be empty", "code": "E103"}],
            "summary": {"total": 1, "errors": 1, "warnings": 0},
        }

    result = validate(code, filename=filename, depth=depth)
    return {
        "status": result.status,
        "errors": [
            {
                "level": e.level,
                "code": e.code,
                "message": e.message,
                "line": e.line,
                "column": e.column,
                "severity": e.severity,
                "llm_action": e.llm_action,
            }
            for e in result.errors
        ],
        "summary": {
            "total": result.summary.total,
            "errors": result.summary.errors,
            "warnings": result.summary.warnings,
        },
        "metadata": {
            "version": result.metadata.version,
            "python": result.metadata.python,
            "textual": result.metadata.textual,
        },
    }


def get_framework_info(detail_level: str = "minimal") -> dict[str, Any]:
    """Get information about the installed Textual framework.

    Args:
        detail_level: "minimal" for basic info, "full" for complete details.

    Returns:
        FrameworkInfo including version, available widgets, and deprecated APIs.

    Use when:
    - Before generating Textual code to check available widgets
    - To avoid using deprecated APIs
    - To verify Textual is installed and which version

    """
    info = oracle_framework_info(detail_level=detail_level)
    return {
        "textual_version": info.textual_version,
        "python_version": info.python_version,
        "widgets": info.widgets,
        "deprecated": info.deprecated,
        "platform": info.platform,
    }


def create_fastmcp_server():
    from fastmcp import FastMCP
    from fastmcp.server.providers.skills import SkillsDirectoryProvider

    mcp = FastMCP("Tuxido")

    skills_dir = Path(__file__).parent.parent / "skills"
    if skills_dir.exists():
        mcp.add_provider(SkillsDirectoryProvider(roots=skills_dir, reload=True))

    @mcp.tool
    def validate_tui_tool(
        code: str,
        depth: Literal["fast", "full"] = "fast",
        filename: str = "app.py",
    ) -> dict[str, Any]:
        """Validate a Textual TUI application.

        Use this tool after generating Python code for Textual apps to check
        for syntax errors, forbidden imports, and async patterns.

        Args:
            code: Python source code to validate.
            depth: Validation depth - "fast" (L1+L2) or "full" (L1-L4).
            filename: Name of the file being validated.

        """
        return validate_tui(code=code, depth=depth, filename=filename)

    @mcp.tool
    def get_framework_info_tool(detail_level: str = "minimal") -> dict[str, Any]:
        """Get information about the installed Textual framework.

        Use this before generating Textual code to ensure you're using
        valid widgets and avoiding deprecated APIs.

        Args:
            detail_level: "minimal" for basic info, "full" for complete details.

        """
        return get_framework_info(detail_level=detail_level)

    return mcp


def run_fastmcp_server():
    mcp = create_fastmcp_server()
    mcp.run()


MCP_TOOLS = {
    "validate_tui": {
        "description": "Validate a Textual TUI application for syntax errors, forbidden imports, and async patterns. Use this tool after generating Python code to check for common issues.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python source code to validate"},
                "depth": {"type": "string", "enum": ["fast", "full"], "default": "fast"},
                "filename": {"type": "string", "default": "app.py"},
            },
            "required": ["code"],
        },
    },
    "get_framework_info": {
        "description": "Get information about the installed Textual framework including version, available widgets, and deprecated APIs. Use this before generating code to ensure you're using valid APIs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "detail_level": {
                    "type": "string",
                    "enum": ["minimal", "full"],
                    "default": "minimal",
                },
            },
        },
    },
}
