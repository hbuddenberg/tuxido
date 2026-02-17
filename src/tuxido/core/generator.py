"""ASCII art to Textual code generator."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


class WidgetType(Enum):
    BUTTON = "button"
    INPUT = "input"
    STATIC = "static"
    CONTAINER = "container"
    HEADER = "header"
    FOOTER = "footer"
    TAB = "tab"


@dataclass
class ParsedWidget:
    widget_type: WidgetType
    id: str
    label: str | None = None
    placeholder: str | None = None
    row: int = 0
    col: int = 0
    width: int = 0


@dataclass
class ParsedLayout:
    containers: list[dict]
    widgets: list[ParsedWidget]
    raw_lines: list[str]


def parse_ascii_layout(ascii_art: str) -> ParsedLayout:
    """Parse ASCII art into structured layout.

    Args:
        ascii_art: ASCII art string to parse

    Returns:
        ParsedLayout with containers and widgets
    """
    lines = ascii_art.split("\n")
    widgets: list[ParsedWidget] = []
    containers: list[dict] = []

    widget_counter: dict[str, int] = {}

    for row, line in enumerate(lines):
        stripped = line

        # Detect containers (boxes)
        if "╭" in stripped or "╰" in stripped:
            container_match = re.search(r"╭(─+)╮|╰(─+)╯", stripped)
            if container_match:
                containers.append(
                    {
                        "row": row,
                        "type": "box_start" if "╭" in stripped else "box_end",
                        "width": len(container_match.group(1) or container_match.group(2) or ""),
                    }
                )

        # Detect buttons [Button] (letters/spaces only, no dots or underscores)
        button_matches = re.findall(r"\[([A-Za-z][A-Za-z0-9 ]*[A-Za-z0-9])\]", stripped)
        for match in button_matches:
            widget_counter["button"] = widget_counter.get("button", 0) + 1
            widgets.append(
                ParsedWidget(
                    widget_type=WidgetType.BUTTON,
                    id=f"btn_{widget_counter['button']}",
                    label=match,
                    row=row,
                    col=stripped.index(f"[{match}]"),
                    width=len(match) + 2,
                )
            )

        # Detect inputs [___] or [placeholder...]
        input_matches = re.findall(r"\[([_.]+[ _.]*[_.]*)\]", stripped)
        for match in input_matches:
            widget_counter["input"] = widget_counter.get("input", 0) + 1
            placeholder = match.replace("_", "").replace(".", "").strip()
            widgets.append(
                ParsedWidget(
                    widget_type=WidgetType.INPUT,
                    id=f"input_{widget_counter['input']}",
                    placeholder=placeholder,
                    row=row,
                    col=stripped.index(f"[{match}]"),
                    width=len(match) + 2,
                )
            )

        # Detect labeled inputs [Label___] or [Label...]
        labeled_input_matches = re.findall(r"\[([A-Za-z][A-Za-z0-9]*[_.]+)\]", stripped)
        for match in labeled_input_matches:
            widget_counter["input"] = widget_counter.get("input", 0) + 1
            placeholder = "".join(c for c in match if c.isalpha())
            widgets.append(
                ParsedWidget(
                    widget_type=WidgetType.INPUT,
                    id=f"input_{widget_counter['input']}",
                    placeholder=placeholder,
                    row=row,
                    col=stripped.index(f"[{match}]"),
                    width=len(match) + 2,
                )
            )

        # Detect static labels (text in boxes)
        text_in_boxes = re.findall(r"[│|]([^│|\\n]+)[│|]", stripped)
        for match in text_in_boxes:
            text = match.strip()
            if text and not text.startswith("[") and not text.endswith("]"):
                widget_counter["static"] = widget_counter.get("static", 0) + 1
                widgets.append(
                    ParsedWidget(
                        widget_type=WidgetType.STATIC,
                        id=f"static_{widget_counter['static']}",
                        label=text,
                        row=row,
                        col=stripped.index(text) if text in stripped else 0,
                        width=len(text),
                    )
                )

    return ParsedLayout(containers=containers, widgets=widgets, raw_lines=lines)


def generate_textual_code(
    layout: ParsedLayout,
    app_name: str = "GeneratedApp",
    title: str | None = None,
) -> str:
    """Generate Textual Python code from parsed layout.

    Args:
        layout: Parsed ASCII layout
        app_name: Name for the App class
        title: Optional title for the app

    Returns:
        Python source code as string
    """
    imports = set()
    compose_lines = []
    css_lines = []

    imports.add("from textual.app import App, ComposeResult")

    for widget in layout.widgets:
        if widget.widget_type == WidgetType.BUTTON:
            imports.add("from textual.widgets import Button")
            compose_lines.append(f'        yield Button("{widget.label}", id="{widget.id}")')
            css_lines.append(f"#{widget.id} {{ width: {widget.width}; }}")

        elif widget.widget_type == WidgetType.INPUT:
            imports.add("from textual.widgets import Input")
            placeholder = widget.placeholder or ""
            compose_lines.append(
                f'        yield Input(placeholder="{placeholder}", id="{widget.id}")'
            )
            css_lines.append(f"#{widget.id} {{ width: {widget.width}; }}")

        elif widget.widget_type == WidgetType.STATIC:
            imports.add("from textual.widgets import Static")
            label = widget.label or ""
            compose_lines.append(f'        yield Static("{label}", id="{widget.id}")')

    title_line = f'    TITLE = "{title}"' if title else ""
    css_content = "\n    ".join(css_lines) if css_lines else ""

    code = f'''from __future__ import annotations

{"; ".join(sorted(imports))}


class {app_name}(App):
{title_line}
    CSS = """
{css_content}
    """

    def compose(self) -> ComposeResult:
{chr(10).join(compose_lines) if compose_lines else "        pass"}


if __name__ == "__main__":
    app = {app_name}()
    app.run()
'''

    return code


def ascii_to_textual(ascii_art: str, app_name: str = "GeneratedApp") -> str:
    """Convert ASCII art to Textual code.

    Args:
        ascii_art: ASCII art layout
        app_name: Name for the generated App class

    Returns:
        Python source code
    """
    layout = parse_ascii_layout(ascii_art)
    return generate_textual_code(layout, app_name=app_name)
