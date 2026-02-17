"""Medium TUI with async error."""

import time
from textual.app import App, ComposeResult
from textual.widgets import Static, Button
from textual.containers import Vertical


class AsyncErrorApp(App):
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Async Demo")
            yield Button("Start", id="start")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        time.sleep(1)
        await self.notify("Done!")
