# TUXIDO KNOWLEDGE BASE

**Generated:** 2026-02-17
**Commit:** 4a0e4f2
**Branch:** main

## OVERVIEW

AI-Native Framework Validator for Textual TUI applications. Catches errors before runtime via 4-level validation pipeline (L1 Syntax → L4 Sandbox), generates code from ASCII mockups, and provides MCP integration for AI assistants.

## STRUCTURE

```
tuxido/
├── src/tuxido/
│   ├── cli/app.py          # Typer CLI entry point (check, fix, heal, generate, mcp)
│   ├── core/               # Validation pipeline, generators, healing engine
│   │   ├── validators/     # L1-L4 validators (syntax, static, DOM, sandbox)
│   │   ├── generator.py    # ASCII art → Textual code generator
│   │   ├── healing.py      # Self-healing engine with correction rules
│   │   └── pipeline.py     # Main validate() orchestration
│   └── mcp/                # MCP server (stdio + FastMCP support)
├── tests/                  # Pytest suite (core, validators)
└── pyproject.toml          # Hatchling build, ruff config, CLI script
```

## WHERE TO LOOK

| Task                         | Location                            | Notes                              |
| ---------------------------- | ----------------------------------- | ---------------------------------- |
| Add new validation rule      | `src/tuxido/core/validators/`       | Inherit base pattern, add to init  |
| Extend ASCII generator       | `src/tuxido/core/generator.py`      | WidgetType enum + parse functions  |
| Add healing rule             | `src/tuxido/core/healing.py`        | RulesEngine._load_builtin_rules()  |
| Modify CLI command           | `src/tuxido/cli/app.py`             | Typer @app.command() decorators    |
| MCP integration              | `src/tuxido/mcp/server.py`          | MCP_TOOLS dict + handlers          |
| Add error code               | `src/tuxido/core/validators/l2_*.py`| FORBIDDEN_IMPORTS dict             |

## CODE MAP

| Symbol               | Type   | Location                      | Role                             |
| -------------------- | ------ | ----------------------------- | -------------------------------- |
| `validate()`         | func   | core/pipeline.py:15           | Main validation orchestrator     |
| `validate_static()`  | func   | core/validators/l2_static.py  | L2: import/blocking call checks  |
| `validate_sandbox()` | func   | core/validators/l4_sandbox.py | L4: runtime testing in isolation |
| `ascii_to_textual()` | func   | core/generator.py:201         | ASCII art → Python code          |
| `SelfHealingEngine`  | class  | core/healing.py:134           | Iterative code correction        |
| `RulesEngine`        | class  | core/healing.py:32            | Correction rule registry         |
| `FORBIDDEN_IMPORTS`  | const  | core/validators/l2_static.py  | E201: os, subprocess, socket, eval|
| `StaticAnalyzer`     | class  | core/validators/l2_static.py  | AST visitor for L2 analysis      |

## CONVENTIONS

**Imports:** `from __future__ import annotations` required (ruff enforces). Use absolute imports.

**Type hints:** Modern syntax (`str | None`, `list[str]`). Pydantic models for data structures.

**Error handling:** Return `ValidationResult` with `ValidationError` list. Include `llm_action` field for AI fix suggestions.

**CLI patterns:** Use Typer with `Annotated` types. Rich Console for output tables.

**Testing:** pytest with `asyncio_mode = "auto"`. Test files: `test_*.py` in `tests/`.

## ANTI-PATTERNS (THIS PROJECT)

| Code | Prohibition                                              | Fix                                  |
| ---- | -------------------------------------------------------- | ------------------------------------ |
| E201 | Forbidden imports: `os`, `subprocess`, `socket`, `eval`  | Use pathlib, httpx, Textual APIs     |
| E202 | Blocking calls in async: `time.sleep()`, `requests.get()`| Use `asyncio.sleep()`, `httpx`       |
| E101 | Python syntax errors                                     | Fix AST parsing                      |
| W201 | Missing `from textual.app import App`                    | Add required import                  |
| D301 | Widget missing `id` attribute                            | Add `id="widget-name"`               |

**Never:** Suppress type errors, expose secrets, use blocking I/O in async.

## COMMANDS

```bash
# Install
uv sync

# Run tests
uv run pytest tests/ -v

# Linting
uv run ruff check . --fix
uv run ruff format .

# CLI usage
uv run tuxido check app.py              # Fast (L1+L2)
uv run tuxido check app.py --depth=full # Full (L1-L4)
uv run tuxido generate layout.txt -o app.py
uv run tuxido heal app.py --max-iterations=5
uv run tuxido mcp --fastmcp             # Start MCP server

# Build
uv build
```

## NOTES

- **Windows:** L3 DOM and L4 Sandbox have limited functionality on Windows (warning, not error)
- **MCP:** Use `--fastmcp` flag for FastMCP server with SkillsProvider (requires `tuxido[mcp]`)
- **Textual dependency:** Optional. Validator works without Textual installed (L1-L2 always work)
- **Error codes:** Prefix indicates level (E=error, W=warning, D=DOM). Number indicates category.
