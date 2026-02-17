#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from tuxido.mcp.server import MCP_TOOLS, get_framework_info, validate_tui


def run_basic_server():
    def handle_request(request: dict) -> dict:
        method = request.get("method")
        request_id = request.get("id")

        if method == "tools/list":
            tools = []
            for name, spec in MCP_TOOLS.items():
                tools.append(
                    {
                        "name": name,
                        "description": spec["description"],
                        "inputSchema": spec["input_schema"],
                    },
                )
            return {"id": request_id, "result": {"tools": tools}}

        if method == "tools/call":
            tool_name = request.get("params", {}).get("name")
            args = request.get("params", {}).get("arguments", {})

            if tool_name == "validate_tui":
                result = validate_tui(
                    code=args.get("code", ""),
                    depth=args.get("depth", "fast"),
                    filename=args.get("filename", "app.py"),
                )
            elif tool_name == "get_framework_info":
                result = get_framework_info(detail_level=args.get("detail_level", "minimal"))
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            return {
                "id": request_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result)}]},
            }

        return {"id": request_id, "error": {"code": "method_not_found"}}

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            request = json.loads(line)
            response = handle_request(request)
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except EOFError:
            break
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.stderr.flush()


def main():
    parser = argparse.ArgumentParser(description="Tuxido MCP Server")
    parser.add_argument(
        "--fastmcp",
        action="store_true",
        help="Use FastMCP server with SkillsProvider (requires: pip install tuxido[mcp])",
    )
    args = parser.parse_args()

    if args.fastmcp:
        from tuxido.mcp import run_fastmcp_server

        run_fastmcp_server()
    else:
        run_basic_server()


if __name__ == "__main__":
    main()
