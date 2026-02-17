"""Complex TUI - Dashboard with multiple widgets without IDs."""

from textual.app import App, ComposeResult
from textual.widgets import Static, Button, ProgressBar, Label
from textual.containers import Vertical, Horizontal, Grid
from textual import work
import time


class MetricsData:
    def __init__(self):
        self.cpu = 0
        self.memory = 0
        self.disk = 0


class Dashboard(App):
    CSS = """
    Grid {
        grid-size: 3;
        grid-gutter: 1;
    }
    .metric {
        border: solid blue;
        padding: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.data = MetricsData()

    def compose(self) -> ComposeResult:
        yield Static("System Dashboard")
        with Grid():
            yield Static("CPU", classes="metric")
            yield Static("Memory", classes="metric")
            yield Static("Disk", classes="metric")
        yield ProgressBar(total=100, show_eta=False)
        with Horizontal():
            yield Button("Start", id="start")
            yield Button("Stop", id="stop")
            yield Button("Reset", id="reset")

    def on_mount(self) -> None:
        self.update_metrics()

    @work
    async def update_metrics(self) -> None:
        while True:
            self.data.cpu = (self.data.cpu + 10) % 100
            self.data.memory = (self.data.memory + 5) % 100
            self.data.disk = 75
            await self.sleep(1)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start":
            self.notify("Monitoring started")
        elif event.button.id == "stop":
            self.notify("Monitoring stopped")
        elif event.button.id == "reset":
            self.data = MetricsData()
            self.notify("Metrics reset")
