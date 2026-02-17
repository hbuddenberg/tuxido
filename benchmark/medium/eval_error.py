"""Medium TUI with eval error."""

from textual.app import App, ComposeResult
from textual.widgets import Static, Input
from textual.containers import Vertical


class EvalApp(App):
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Calculator")
            yield Input(id="expr")

    def on_input_changed(self, event: Input.Changed) -> None:
        result = eval(event.input.value)
        self.notify(f"Result: {result}")
