"""Simple TUI with L1 error - syntax error."""

from textual.app import App, ComposeResult
from textual.widgets import Static


class BrokenApp(App):
    def compose(self) -> ComposeResult:
        yield Static("Hello  # missing quote
