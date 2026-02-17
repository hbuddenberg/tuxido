# VALIDATORS MODULE

4-level validation pipeline: Syntax → Static → DOM → Sandbox.

## OVERVIEW

L1 (Syntax): AST parsing, instant fail on syntax errors.
L2 (Static): Import analysis, blocking call detection, forbidden patterns.
L3 (DOM): Widget tree validation (requires Textual).
L4 (Sandbox): Runtime testing in isolated environment.

## STRUCTURE

```
validators/
├── __init__.py    # Exports: validate_syntax, validate_static, validate_dom, validate_sandbox
├── l1_syntax.py   # AST parsing, syntax error detection
├── l2_static.py   # Import analysis, forbidden imports, blocking calls
├── l3_dom.py      # Widget tree validation
└── l4_sandbox.py  # Runtime testing in subprocess isolation
```

## WHERE TO LOOK

| Task                      | File           | Location                    |
| ------------------------- | -------------- | --------------------------  |
| Add forbidden import      | l2_static.py   | `FORBIDDEN_IMPORTS` dict    |
| Add required import check | l2_static.py   | `REQUIRED_IMPORTS` dict     |
| Detect blocking call      | l2_static.py   | `StaticAnalyzer.visit_Call()`|
| Change sandbox timeout    | l4_sandbox.py  | `validate_sandbox(timeout=)` |
| Add DOM validation rule   | l3_dom.py      | `validate_dom()`            |

## ERROR CODES

| Code | Level | Description                           |
| ---- | ----- | ------------------------------------- |
| E101 | L1    | Python syntax error                   |
| E201 | L2    | Forbidden import (os, subprocess...)  |
| E202 | L2    | Blocking call in async context        |
| DOM* | L3    | DOM/widget structure issues           |
| S*   | L4    | Sandbox runtime errors                |

## CONVENTIONS

**Return type:** All validators return `ValidationResult`.

**Early exit:** L1 must pass before L2 runs (see pipeline.py).

**L2 patterns:** Use AST visitor pattern (`ast.NodeVisitor`). Add `llm_action` to errors.

**L4 isolation:** Run in subprocess with timeout. Platform-specific (limited on Windows).

## ANTI-PATTERNS

- **Never** import `os`, `subprocess`, `socket`, `eval`, `exec` in TUI apps
- **Never** use `time.sleep()` or `requests` in async functions (use `asyncio`, `httpx`)
- **Never** call `__import__()` dynamically
