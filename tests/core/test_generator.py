"""Tests for ASCII to Textual generator."""

from __future__ import annotations

from tuxido.core.generator import ascii_to_textual, parse_ascii_layout


def test_parse_simple_button():
    ascii_art = "[Click Me]"
    layout = parse_ascii_layout(ascii_art)

    assert len(layout.widgets) == 1
    assert layout.widgets[0].widget_type.value == "button"
    assert layout.widgets[0].label == "Click Me"


def test_parse_input_field():
    ascii_art = "[_______]"
    layout = parse_ascii_layout(ascii_art)

    assert len(layout.widgets) == 1
    assert layout.widgets[0].widget_type.value == "input"


def test_parse_labeled_input():
    ascii_art = "[Search...]"
    layout = parse_ascii_layout(ascii_art)

    assert len(layout.widgets) == 1
    assert layout.widgets[0].widget_type.value == "input"


def test_generate_produces_valid_python():
    ascii_art = """
╭─────────╮
│ [OK]    │
╰─────────╯
"""
    code = ascii_to_textual(ascii_art, app_name="TestApp")

    assert "class TestApp(App)" in code
    assert "def compose" in code
    assert 'Button("OK"' in code


def test_generate_with_multiple_widgets():
    ascii_art = """
╭──────────────────╮
│ [Search...]      │
│ [Submit] [Cancel]│
╰──────────────────╯
"""
    code = ascii_to_textual(ascii_art, app_name="FormApp")

    assert "Input" in code
    assert "Button" in code


def test_generate_includes_ids():
    ascii_art = "[Test]"
    code = ascii_to_textual(ascii_art)

    assert 'id="' in code
    assert "btn_1" in code
