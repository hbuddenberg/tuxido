from __future__ import annotations

import pytest

from tuxido.core.pipeline import validate


def test_pipeline_passes_valid_code():
    code = "x = 1"
    result = validate(code)
    assert result.status == "pass"
    assert len(result.errors) == 0


def test_pipeline_early_exit_on_syntax_error():
    code = "def foo("
    result = validate(code)
    assert result.status == "fail"
    assert len(result.errors) == 1
    assert result.errors[0].level == "L1"
    assert result.errors[0].code == "E101"


def test_pipeline_runs_l2_after_l1_pass():
    code = "import os"
    result = validate(code)
    assert result.status == "fail"
    assert len(result.errors) == 1
    assert result.errors[0].level == "L2"
    assert result.errors[0].code == "E201"


def test_pipeline_combines_errors():
    code = """
import os
import subprocess
x = 1
"""
    result = validate(code)
    assert result.status == "fail"
    assert len(result.errors) == 2


def test_pipeline_summary_counts():
    code = "import os"
    result = validate(code)
    assert result.summary.total == 1
    assert result.summary.errors == 1
    assert result.summary.warnings == 0


def test_pipeline_empty_code_fails():
    code = ""
    result = validate(code)
    assert result.status == "fail"


def test_pipeline_metadata():
    code = "x = 1"
    result = validate(code)
    assert result.metadata.version is not None
    assert result.metadata.python is not None
