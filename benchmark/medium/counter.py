"""Medium TUI - Counter app with multiple widgets."""

from textual.app import App, ComposeResult
from textual.widgets import Button, Static, Input
from textual.containers import Vertical


class CounterApp(App):
    CSS = """
    Vertical {
        height: 100%;
        align: center middle;
    }
    Button {
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Counter App")
            yield Input(value="0", id="count")
            yield Button("Increment", id="inc")
            yield Button("Decrement", id="dec")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        input_widget = self.query_one("#count", Input)
        count = int(input_widget.value)
        if event.button.id == "inc":
            count += 1
        else:
            count -= 1
        input_widget.value = str(count)
