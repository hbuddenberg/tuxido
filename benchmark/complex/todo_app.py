"""Complex TUI - Todo app with full CRUD operations."""

from textual.app import App, ComposeResult
from textual.widgets import Button, Static, Input, ListView, ListItem
from textual.containers import Vertical, Horizontal
from textual import work


class TodoItem:
    def __init__(self, text: str, done: bool = False):
        self.text = text
        self.done = done


class TodoApp(App):
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
    }
    # sidebar {
        width: 30%;
        border-right: solid green;
    }
    # main {
        padding: 1;
    }
    ListItem {
        padding: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.todos: list[TodoItem] = []

    def compose(self) -> ComposeResult:
        with Vertical(id="sidebar"):
            yield Static("Todo List")
            yield ListView(id="list")
            with Horizontal():
                yield Input(placeholder="New task...", id="new_task")
                yield Button("Add", id="add")
        with Vertical(id="main"):
            yield Static("Task Details")
            yield Button("Complete", id="complete")
            yield Button("Delete", id="delete")

    def on_mount(self) -> None:
        self.todos = [
            TodoItem("Learn Textual"),
            TodoItem("Build a TUI app"),
            TodoItem("Ship to PyPI"),
        ]
        self.refresh_list()

    def refresh_list(self) -> None:
        list_view = self.query_one("#list", ListView)
        list_view.clear()
        for todo in self.todos:
            prefix = "[x]" if todo.done else "[ ]"
            list_view.append(ListItem(Static(f"{prefix} {todo.text}")))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add":
            new_task = self.query_one("#new_task", Input)
            if new_task.value:
                self.todos.append(TodoItem(new_task.value))
                new_task.value = ""
                self.refresh_list()
        elif event.button.id == "complete":
            self.notify("Marked as complete!")
        elif event.button.id == "delete":
            self.notify("Task deleted")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self.notify(f"Selected: {event.item}")
