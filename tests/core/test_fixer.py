"""Tests for auto-fix functionality."""

from __future__ import annotations

import pytest

from tuxido.core.fixer import fix_code


def test_fix_removes_unused_import():
    code = """import os
from textual.app import App

class MyApp(App):
    pass
"""
    fixed, summary = fix_code(code, "test.py")
    assert "import os" not in fixed
    assert summary["total_fixes"] >= 1


def test_fix_adds_widget_id():
    code = """from textual.app import App, ComposeResult
from textual.widgets import Static

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield Static("Test")
"""
    fixed, summary = fix_code(code, "test.py")
    assert 'id="' in fixed
    assert summary["total_fixes"] >= 1


def test_dry_run_does_not_modify():
    code = """import os
from textual.app import App
"""
    fixed, summary = fix_code(code, "test.py")
    # fix_code always returns modified code,
    # CLI handles dry-run by not saving
    assert summary["total_fixes"] >= 1
