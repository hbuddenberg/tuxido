"""Tests for self-healing engine."""

from __future__ import annotations

from tuxido.core.healing import IssueType, RulesEngine, SelfHealingEngine


def test_rules_engine_loads_rules():
    engine = RulesEngine()
    assert len(engine.rules) > 0


def test_rules_engine_gets_applicable_rules():
    engine = RulesEngine()
    rules = engine.get_applicable_rules(IssueType.UNUSED_IMPORT)
    assert len(rules) == 1
    assert rules[0].name == "fix_unused_import"


def test_self_healing_engine_initializes():
    engine = SelfHealingEngine(max_iterations=3)
    assert engine.max_iterations == 3
    assert engine.iteration_count == 0


def test_self_healing_removes_unused_import():
    code = """import os
from textual.app import App

class MyApp(App):
    pass
"""
    engine = SelfHealingEngine()
    issues = [{"type": "unused_import", "import": "os"}]

    healed, success = engine.heal(code, issues)

    assert "import os" not in healed
    assert "from textual.app" in healed


def test_self_healing_adds_widget_id():
    code = """from textual.app import App, ComposeResult
from textual.widgets import Static

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield Static("Hello")
"""
    engine = SelfHealingEngine()
    issues = [
        {
            "type": "widget_id_mismatch",
            "widget_type": "Static",
            "widget_id": "static_1",
            "label": "Hello",
        }
    ]

    healed, success = engine.heal(code, issues)

    assert 'id="static_1"' in healed


def test_self_healing_respects_max_iterations():
    engine = SelfHealingEngine(max_iterations=1)
    issues = [
        {"type": "unused_import", "import": "os"},
        {"type": "unused_import", "import": "subprocess"},
    ]

    code = "import os\nimport subprocess\nprint('hello')"
    healed, success = engine.heal(code, issues)

    assert engine.iteration_count <= 1


def test_healing_report():
    engine = SelfHealingEngine()
    code = "import os\nprint('hello')"
    issues = [{"type": "unused_import", "import": "os"}]

    engine.heal(code, issues)
    report = engine.get_healing_report()

    assert "iterations" in report
    assert "fixes_applied" in report
    assert "fixes" in report
