"""Medium TUI with os.system error."""

import os
from textual.app import App, ComposeResult
from textual.widgets import Static, Button
from textual.containers import Vertical


class SystemApp(App):
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("System Commands")
            yield Button("List Files", id="ls")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ls":
            os.system("ls")
