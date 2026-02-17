from __future__ import annotations

from tuxido.mcp.server import MCP_TOOLS, get_framework_info, validate_tui

__all__ = ["MCP_TOOLS", "get_framework_info", "validate_tui"]


def run_fastmcp_server():
    """Run the FastMCP server with SkillsProvider. Requires 'mcp' extra."""
    try:
        from tuxido.mcp.fastmcp_server import run_fastmcp_server as _run
        return _run()
    except ImportError as e:
        import sys
        print("Error: FastMCP not installed.", file=sys.stderr)
        print("Install with: pip install tuxido[mcp]", file=sys.stderr)
        raise SystemExit(1) from e
