"""Simple TUI - 1 file, no errors."""

from textual.app import App, ComposeResult
from textual.widgets import Static


class HelloApp(App):
    def compose(self) -> ComposeResult:
        yield Static("Hello, World!")
