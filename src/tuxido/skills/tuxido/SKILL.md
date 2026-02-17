---
name: tuxido
description: AI-Native Framework Validator for Textual TUI Applications with code generation, validation, and self-healing capabilities
version: 0.1.0
author: Hans Buddenberg
license: MIT
repository: https://github.com/hbuddenberg/tuxido
compatibility: opencode
metadata:
  category: development
  subcategories:
    - tui
    - testing
    - code-generation
    - self-healing
  triggers:
    - validar tui
    - validar interfaz textual
    - generar tui
    - generar interfaz
    - ascii mockup
    - sanar codigo
    - self-healing
    - textual widget
    - rich formatting
    - code pattern
  context7:
    textual: /websites/textual_textualize_io
    rich: /textualize/rich
    rich-docs: /websites/rich_readthedocs_io_en_stable
  official_docs:
    textual: https://textual.textualize.io
    rich: https://rich.readthedocs.io
---

# Tuxido - AI-Native Framework Validator

Suit up your terminal apps. Tuxido validates Textual TUI applications through 4 levels (L1-L4), generates code from ASCII mockups, and autonomously corrects issues.

---

## Widget Reference (Textual)

### Core Widgets

| Widget | Purpose | Example |
|--------|---------|---------|
| `Static` | Static text display | `Static("Hello, World!")` |
| `Label` | Short labels | `Label("Name:")` |
| `Button` | Clickable button | `Button("Submit", variant="primary")` |
| `Header` | Top bar with title | `yield Header()` |
| `Footer` | Bottom bar with keybindings | `yield Footer()` |

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Welcome!")
        yield Button("Click me")
        yield Footer()
```

### Data Widgets

| Widget | Purpose | Use Case |
|--------|---------|----------|
| `DataTable` | Sortable tables | Query results, logs |
| `Tree` | Hierarchical data | File browser, navigation |
| `ListView` | Selectable list | Menus, options |
| `OptionList` | Multi-select options | Settings, filters |

**DataTable Example:**
```python
from textual.widgets import DataTable

class TableApp(App):
    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Name", "Status")
        table.add_rows([
            (1, "Alice", "Active"),
            (2, "Bob", "Inactive"),
        ])
```

**Tree Example:**
```python
from textual.widgets import Tree

def build_tree(self) -> ComposeResult:
    tree: Tree[str] = Tree("Project")
    tree.root.expand()
    src = tree.root.add("src", expand=True)
    src.add_leaf("main.py")
    src.add_leaf("app.py")
    yield tree
```

### Input Widgets

| Widget | Purpose | Features |
|--------|---------|----------|
| `Input` | Text input | Placeholder, validation, password mode |
| `TextArea` | Multiline editor | Syntax highlighting, line numbers |
| `Select` | Dropdown | Searchable options |
| `Checkbox` | Boolean toggle | On/off selection |
| `Switch` | Modern toggle | Settings UI |
| `MaskedInput` | Formatted input | Phone, date patterns |

**Input Example:**
```python
from textual.widgets import Input

yield Input(placeholder="Enter username", id="username")
yield Input(password=True, placeholder="Password", id="password")
```

**TextArea Example:**
```python
from textual.widgets import TextArea

code_editor = TextArea(
    "def hello():\n    print('Hello')",
    language="python",
    theme="monokai",
    show_line_numbers=True
)
```

### Layout Widgets

| Widget | Purpose | CSS Property |
|--------|---------|--------------|
| `Container` | Generic container | Base for layouts |
| `Horizontal` | Left-to-right layout | `layout: horizontal` |
| `Vertical` | Top-to-bottom layout | `layout: vertical` |
| `Grid` | Grid layout | `layout: grid` |
| `Tabs` | Tab bar | Navigation tabs |
| `TabbedContent` | Tab content area | Content per tab |

**Layout Example:**
```python
from textual.containers import Horizontal, Vertical, Container

def compose(self) -> ComposeResult:
    yield Header()
    with Container():
        with Horizontal():
            with Vertical(id="sidebar"):
                yield ListView(...)
            with Vertical(id="main"):
                yield DataTable()
    yield Footer()
```

---

## Rich Integration

Rich integrates natively with Textual for styled output.

### Rich Objects in Widgets

```python
from rich.text import Text
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown

# Styled text
label = Label(Text("Important", style="bold red"))

# Rich in DataTable
table = DataTable()
table.add_column("Status")
table.add_row(Text("Error", style="red"))
table.add_row(Text("Success", style="green"))

# Markdown in Static
yield Static(Markdown("# Title\n\n**Bold** text"))

# Syntax highlighted code
code = Syntax("print('hello')", "python", theme="monokai")
yield Static(code)
```

### Rich Progress

```python
from rich.progress import Progress

with Progress() as progress:
    task = progress.add_task("Processing", total=100)
    for i in range(100):
        progress.update(task, advance=1)
```

---

## CSS & Styling

### Layout CSS

```css
/* Vertical layout (default) */
#main {
    layout: vertical;
}

/* Horizontal layout */
#toolbar {
    layout: horizontal;
}

/* Grid layout */
#grid {
    layout: grid;
    grid-size: 2 2;
    grid-gutter: 1;
}

/* Docking */
#sidebar {
    dock: left;
    width: 20;
}

#status-bar {
    dock: bottom;
    height: 1;
}
```

### Widget Styling

```css
/* Colors */
Button {
    background: $primary;
    color: $text-on-primary;
}

/* Borders */
Container {
    border: solid $accent;
    padding: 1;
}

/* Alignment */
#centered {
    align: center middle;
}

/* Dimensions */
#fixed {
    width: 40;
    height: 10;
}

#flexible {
    width: 1fr;
    height: auto;
}
```

### Reactive Styling

```python
from textual.reactive import reactive

class Counter(Widget):
    count = reactive(0, layout=True)  # layout=True triggers resize

    def render(self) -> str:
        return f"Count: {self.count}"
```

---

## Code Patterns

### Basic App Structure

```python
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Button, Input, Label

class MyApp(App):
    CSS_PATH = "styles.tcss"
    TITLE = "My App"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("s", "save", "Save"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield Label("Enter value:")
            yield Input(placeholder="Type here")
            yield Button("Submit")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        input_value = self.query_one(Input).value
        self.notify(f"Submitted: {input_value}")
```

### Form Pattern

```python
from textual.containers import Vertical, Horizontal

def compose(self) -> ComposeResult:
    yield Header()
    with Vertical(id="form"):
        yield Label("Username:")
        yield Input(placeholder="Enter username", id="username")
        yield Label("Password:")
        yield Input(password=True, placeholder="Enter password", id="password")
        yield Label("Email:")
        yield Input(placeholder="user@example.com", id="email")
        with Horizontal():
            yield Button("Register", variant="primary", id="register")
            yield Button("Cancel", variant="default", id="cancel")
    yield Footer()
```

### Master-Detail Pattern

```python
from textual.widgets import ListView, ListItem, Static

def compose(self) -> ComposeResult:
    yield Header()
    with Horizontal():
        with Vertical(id="master"):
            yield ListView(
                ListItem(Static("Item 1")),
                ListItem(Static("Item 2")),
                ListItem(Static("Item 3")),
                id="item-list"
            )
        with Vertical(id="detail"):
            yield Static("Select an item", id="details")
    yield Footer()

def on_list_view_selected(self, event: ListView.Selected) -> None:
    item = event.item
    self.query_one("#details", Static).update(f"Selected: {item}")
```

### DataTable Pattern

```python
class TableApp(App):
    CSS_PATH = "table.tcss"
    
    def compose(self) -> ComposeResult:
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.zebra_stripes = True
        table.show_cursor = True
        table.add_columns("Name", "Type", "Size")
        table.add_rows(self.get_data())

    def get_data(self) -> list:
        return [
            ("document.pdf", "PDF", "2.4 MB"),
            ("image.png", "Image", "1.2 MB"),
            ("data.csv", "CSV", "340 KB"),
        ]
```

### Reactive State Pattern

```python
from textual.reactive import reactive
from textual.message import Message

class TodoItem(Widget):
    class Completed(Message):
        def __init__(self, item_id: str):
            self.item_id = item_id
            super().__init__()

    done = reactive(False)

    def watch_done(self, old: bool, new: bool) -> None:
        self.styles.opacity = 0.5 if new else 1.0
        if new:
            self.post_message(self.Completed(self.id or ""))

    def render(self) -> str:
        status = "✓" if self.done else "○"
        return f"{status} {self.text}"
```

---

## MCP Tools Reference

### validate_tui

Validate a Textual TUI application for errors.

**Parameters:**
- `code` (required): Python source code to validate
- `depth`: "fast" (L1+L2) or "full" (L1-L4), default: "fast"
- `filename`: File name for error reporting, default: "app.py"

**Returns:**
```json
{
  "status": "pass|fail|error",
  "errors": [{"code": "E101", "message": "...", "line": 10}],
  "summary": {"total": 1, "errors": 1, "warnings": 0},
  "metadata": {"version": "0.1.0", "python": "3.11", "textual": "0.47"}
}
```

### get_framework_info

Get Textual framework information.

**Parameters:**
- `detail_level`: "minimal" or "full"

**Returns:**
```json
{
  "textual_version": "0.47.0",
  "python_version": "3.11.0",
  "widgets": ["Button", "Input", "DataTable", ...],
  "deprecated": ["old_widget", ...],
  "platform": "darwin"
}
```

---

## Validation Levels

| Level | Name | Checks | Speed |
|-------|------|--------|-------|
| L1 | Syntax | Python AST parsing | Instant |
| L2 | Static | Imports, async patterns | Fast |
| L3 | DOM | Widget tree validation | Medium |
| L4 | Sandbox | Safe runtime execution | Slower |

### Error Codes

| Code | Level | Description | Fix |
|------|-------|-------------|-----|
| E101 | L1 | Syntax error | Fix Python syntax |
| E201 | L2 | Forbidden import | Remove `os`, `sys`, `subprocess` |
| E202 | L2 | Async anti-pattern | Use `@work` decorator |
| W201 | L2 | Missing textual import | Add `from textual.app import App` |
| W202 | L2 | Unused import | Remove unused import |
| D301 | L3 | Missing widget ID | Add `id="widget-name"` |
| D302 | L3 | Invalid widget type | Check widget exists in Textual |
| S401 | L4 | Sandbox timeout | Optimize code or increase timeout |
| S402 | L4 | Runtime error | Fix runtime exception |

---

## Usage

### CLI Commands

```bash
# Validate TUI
tuxido check app.py --depth=full

# Generate from ASCII
tuxido generate layout.txt --output app.py

# Self-heal code
tuxido heal app.py --max-iterations=5

# Run MCP server
tuxido mcp --fastmcp
```

### ASCII to Code

```
+--------------------------+
| Username: [____________] |
| Password: [____________] |
|                          |
|      [Login]  [Cancel]   |
+--------------------------+
```

Pattern recognition:
- `[Button]` → Button widget
- `[____]` → Input widget
- `+---+` → Container

---

## Resources

### Official Documentation
- Textual: https://textual.textualize.io
- Rich: https://rich.readthedocs.io
- Context7 IDs: Use `context7_query-docs` tool with IDs from metadata

### Quick Reference

```python
# Common imports
from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Button, Input, Label, Static,
    DataTable, Tree, ListView, TextArea, Select
)
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.reactive import reactive
from textual.binding import Binding
```

### MCP Configuration

**OpenCode** (`~/.config/opencode/opencode.json`):
```json
{
  "mcp": {
    "tuxido": {
      "enabled": true,
      "type": "local",
      "command": ["tuxido", "mcp", "--fastmcp"]
    }
  }
}
```

**Claude Code**:
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

---

## Tips for AI Agents

1. **Always validate generated code** - Use `validate_tui` after generating Textual code
2. **Use fast mode for iterations** - `depth="fast"` is sufficient during development
3. **Check framework info first** - Use `get_framework_info` to know available widgets
4. **Leverage self-healing** - Use `tuxido heal` for autonomous correction
5. **ASCII specs are powerful** - Users can express UI intent naturally with ASCII art
6. **Use Context7 for docs** - Query `context7_query-docs` with IDs from metadata for latest docs
