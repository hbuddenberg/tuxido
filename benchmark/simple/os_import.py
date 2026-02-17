"""Simple TUI with L2 error - forbidden import."""

import os
from textual.app import App, ComposeResult
from textual.widgets import Static


class OsImportApp(App):
    def compose(self) -> ComposeResult:
        yield Static("Hello!")
