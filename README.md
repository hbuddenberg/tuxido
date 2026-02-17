<p align="center">
  <img src="tuxido.png" alt="Tuxido Logo" width="150">
</p>

<h1 align="center">Tuxido</h1>

<p align="center">
  <strong>Suit up your terminal apps.</strong><br>
  <em>AI-Native Framework Validator for Textual TUI Applications</em>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%20|%203.11%20|%203.12%20|%203.13-blue?logo=python&logoColor=white">
  <img alt="CI" src="https://img.shields.io/badge/CI-passing-brightgreen?logo=github&logoColor=white">
  <img alt="Platforms" src="https://img.shields.io/badge/OS-Linux%20|%20macOS%20|%20Windows-241F31?logo=gnometerminal&logoColor=white">
  <a href="LICENSE">
    <img alt="License" src="https://img.shields.io/badge/License-MIT-green?logo=open-source-initiative&logoColor=white">
  </a>
  <br>
  <a href="README.es.md">
    <img alt="Español" src="https://img.shields.io/badge/Lang-Español-yellow">
  </a>
</p>

---

## About

Tuxido helps developers build reliable Textual TUI applications by catching errors before runtime and generating code from ASCII mockups. It provides four levels of validation, self-healing capabilities, and seamless integration with AI assistants through MCP.

---

## What is Tuxido?

Tuxido is a validator and code generator for **Textual** TUI applications. It catches errors before runtime and generates working code from ASCII mockups.

### Why Use It?

| Problem                                 | Tuxido Solution                      |
| --------------------------------------- | ------------------------------------ |
| Syntax errors at runtime                | L1 validation catches them instantly |
| Unsafe imports (`os`, `subprocess`) | L2 static analysis detects them      |
| Widget structure issues                 | L3 DOM validation                    |
| Runtime crashes                         | L4 sandbox testing                   |
| Writing boilerplate code                | Generate from ASCII art              |
| Manual error fixing                     | Auto-heal with iterative correction  |

### Example: Validate

```python
# app.py - Has a forbidden import
import os  # ← Problem!
from textual.app import App
from textual.widgets import Static

class MyApp(App):
    def compose(self):
        yield Static("Hello")
```

```bash
$ tuxido check app.py

✗ app.py
  Status: fail

  E201 FORBIDDEN_IMPORT (L2)
    import os
    │
  ⚠ Forbidden import: 'os'
    Fix: Remove os import or use Textual alternatives
    LLM Action: Use pathlib.Path for file operations
```

### Example: Generate from ASCII

```
╭────────────────────────────╮
│ Username: [______________] │
│ Password: [______________] │
│                            │
│     [Login]   [Cancel]     │
╰────────────────────────────╯
```

```bash
$ tuxido generate mockup.txt --output login.py
```

Generates:

```python
from textual.app import App, ComposeResult
from textual.widgets import Input, Button
from textual.containers import Vertical, Horizontal

class LoginApp(App):
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(placeholder="Username", id="username")
            yield Input(placeholder="Password", password=True, id="password")
            with Horizontal():
                yield Button("Login", variant="primary")
                yield Button("Cancel")
```

### Example: Self-Heal

```bash
$ tuxido heal app.py --max-iterations=5

Analyzing app.py...
Found 3 issues

Iteration 1:
  ✓ fix_unused_import: Removed 'os'
  ✓ fix_widget_id: Added id="username" to Input
  ✓ fix_missing_import: Added 'from textual.containers import Vertical'

Iteration 2:
  ✓ Validation passed

Applied 3 fixes in 2 iterations
```

---

## Install

### Run without installing (uvx)

```bash
uvx tuxido check app.py
uvx tuxido generate layout.txt --output app.py
```

### Install with uv

```bash
uv tool install tuxido

# With MCP support
uv tool install "tuxido[mcp]"
```

### Install with pip

```bash
pip install tuxido

# With MCP support
pip install tuxido[mcp]
```

---

## Terminal Usage

### Validate

```bash
tuxido check app.py              # Fast (L1+L2)
tuxido check app.py --depth=full # Full (L1-L4)
tuxido check app.py --json       # JSON output
```

### Generate from ASCII

```bash
tuxido generate layout.txt --output app.py
```

```
╭─────────────╮     →     class GeneratedApp(App):
│ [Search...] │             def compose(self):
│ [Submit]    │                 yield Input(placeholder="Search...")
╰─────────────╯                 yield Button("Submit")
```

### Self-Heal

```bash
tuxido heal app.py --max-iterations=5
```

### Other Commands

```bash
tuxido version          # Version info
tuxido info --verbose   # Textual widgets & APIs
tuxido fix app.py       # Auto-fix issues
```

---

## MCP Server

### Install MCP

**OpenCode** (`~/.config/opencode/opencode.json`):

```json
{
  "mcp": {
    "tuxido": {
      "enabled": true,
      "command": ["tuxido", "mcp", "--fastmcp"]
    }
  }
}
```

**Claude Code** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "tuxido": {
      "command": "tuxido",
      "args": ["mcp", "--fastmcp"]
    }
  }
}
```

**Cursor** (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "tuxido": {
      "command": "tuxido",
      "args": ["mcp"]
    }
  }
}
```

### MCP Tools

| Tool                   | Description                           |
| ---------------------- | ------------------------------------- |
| `validate_tui`       | Validate TUI code (L1-L4)             |
| `get_framework_info` | Get Textual widgets & deprecated APIs |

### Usage Example

```python
# In your AI assistant
result = validate_tui(code="...", depth="fast")
# Returns: status, errors, summary, metadata
```

---

## OpenCode Skill

Tuxido includes a skill with Textual widget reference, code patterns, and Rich integration.

### Install Skill

```bash
# The skill auto-installs with the package
# Or manually:
python scripts/install_skill.py
```

**Skill locations** (auto-discovered):

- `~/.claude/skills/tuxido/SKILL.md`
- `~/.config/opencode/skills/tuxido/SKILL.md`

### Skill Features

- **20+ Widget Reference** - Core, Data, Input, Layout widgets with examples
- **Rich Integration** - Styled text, tables, syntax highlighting
- **Code Patterns** - Form, Master-Detail, DataTable, Reactive
- **CSS Guide** - Layouts, docking, reactive styling
- **Context7 IDs** - Dynamic doc access for Textual & Rich

### Use Skill

The skill auto-loads when you mention TUI/Textual topics:

```
"Create a login form with Textual"
"Generate a DataTable with sorting"
"Add Rich formatting to my TUI"
```

---

## Validation Levels

| Level | Name    | Checks         | Speed   |
| ----- | ------- | -------------- | ------- |
| L1    | Syntax  | AST parsing    | Instant |
| L2    | Static  | Imports, async | Fast    |
| L3    | DOM     | Widget tree    | Medium  |
| L4    | Sandbox | Runtime        | Slower  |

## Error Codes

| Code | Fix                                    |
| ---- | -------------------------------------- |
| E101 | Fix Python syntax                      |
| E201 | Remove `os`, `sys`, `subprocess` |
| E202 | Use `@work` decorator                |
| W201 | Add `from textual.app import App`    |
| W202 | Remove unused import                   |
| D301 | Add `id="widget-name"`               |

---

## Quick Reference

```python
# Common imports
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Input, DataTable
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
```

---

## Links

- **Docs**: https://textual.textualize.io
- **Context7**: `/websites/textual_textualize_io`
- **Issues**: https://github.com/hbuddenberg/tuxido/issues

---

## License

MIT
