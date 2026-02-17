"""Complex TUI - File manager with subprocess."""

import subprocess
from textual.app import App, ComposeResult
from textual.widgets import Button, Static, ListView, ListItem
from textual.containers import Vertical, Horizontal
import os


class FileManager(App):
    CSS = """
    Vertical {
        height: 100%;
    }
    ListView {
        height: 1fr;
    }
    """

    def __init__(self):
        super().__init__()
        self.current_dir = os.getcwd()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("File Manager", id="title")
            yield ListView(id="files")
            with Horizontal():
                yield Button("Refresh", id="refresh")
                yield Button("Open", id="open")
                yield Button("Delete", id="delete")

    def on_mount(self) -> None:
        self.refresh_files()

    def refresh_files(self) -> None:
        try:
            files = os.listdir(self.current_dir)
            list_view = self.query_one("#files", ListView)
            list_view.clear()
            for f in files:
                list_view.append(ListItem(Static(f)))
        except Exception as e:
            self.notify(f"Error: {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "refresh":
            self.refresh_files()
        elif event.button.id == "open":
            subprocess.Popen(["open", "."])
        elif event.button.id == "delete":
            self.notify("Delete not implemented")
