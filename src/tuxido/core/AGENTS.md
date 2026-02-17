# CORE MODULE

Validation pipeline, code generation, and self-healing engine.

## OVERVIEW

Core logic for Tuxido: 4-level validation (L1-L4), ASCII-to-Textual generator, and iterative healing system.

## STRUCTURE

```
core/
├── pipeline.py        # validate() main orchestrator
├── generator.py       # ASCII art → Textual code
├── healing.py         # SelfHealingEngine + RulesEngine
├── fixer.py           # Auto-fix utilities
├── report.py          # HTML/Markdown report generation
├── models.py          # Pydantic models (ValidationResult, etc.)
├── errors.py          # TuxidoError, SandboxError
├── oracle/            # Framework info provider
└── validators/        # L1-L4 validators (see validators/AGENTS.md)
```

## WHERE TO LOOK

| Task                      | File              | Function/Class           |
| ------------------------- | ----------------- | ------------------------ |
| Run full validation       | pipeline.py       | `validate()`             |
| Add forbidden import      | validators/l2_*.py| `FORBIDDEN_IMPORTS`      |
| Add widget type           | generator.py      | `WidgetType` enum        |
| Add healing rule          | healing.py        | `RulesEngine._load_*()`  |
| Change error format       | models.py         | `ValidationError`        |

## CONVENTIONS

**Validation result:** Always return `ValidationResult` with `status`, `errors`, `summary`, `metadata`.

**Error codes:** Format `{Level}{Category}{Number}` (e.g., E201 = Error, Level 2, code 01).

**L2 errors:** Include `llm_action` field with specific fix instructions for AI.

**Generator output:** Must include `from __future__ import annotations` and be validatable.

## ANTI-PATTERNS

- **Never** skip L1 before L2 (pipeline enforces early exit on syntax errors)
- **Never** raise exceptions from validators (return ValidationResult with errors)
- **Never** block in async validation context
