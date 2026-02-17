from __future__ import annotations

import pytest

from tuxido.core.validators import validate_syntax


def test_l1_accepts_valid_code():
    code = 'print("hello")'
    result = validate_syntax(code)
    assert result.status == "pass"
    assert len(result.errors) == 0


def test_l1_rejects_syntax_error():
    code = "def foo("
    result = validate_syntax(code)
    assert result.status == "fail"
    assert len(result.errors) == 1
    assert result.errors[0].code == "E101"
    assert result.errors[0].severity == "error"


def test_l1_rejects_empty_code():
    code = ""
    result = validate_syntax(code)
    assert result.status == "fail"
    assert result.errors[0].code == "E103"


def test_l1_rejects_whitespace_only():
    code = "   \n  \n  "
    result = validate_syntax(code)
    assert result.status == "fail"
    assert result.errors[0].code == "E103"


def test_l1_returns_metadata():
    code = "x = 1"
    result = validate_syntax(code)
    assert result.metadata.version is not None
    assert result.metadata.python is not None


def test_l1_valid_textual_app():
    code = '''from textual.app import App, ComposeResult
from textual.widgets import Static

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield Static("Hello")
'''
    result = validate_syntax(code)
    assert result.status == "pass"
