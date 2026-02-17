from __future__ import annotations

import pytest

from tuxido.core.validators import validate_static


def test_l2_accepts_clean_code():
    code = 'x = 1'
    result = validate_static(code)
    assert result.status == "pass"


def test_l2_detects_os_import():
    code = 'import os'
    result = validate_static(code)
    assert result.status == "fail"
    assert any(e.code == "E201" for e in result.errors)


def test_l2_detects_subprocess():
    code = 'import subprocess'
    result = validate_static(code)
    assert result.status == "fail"


def test_l2_detects_eval():
    code = 'eval("1+1")'
    result = validate_static(code)
    assert result.status == "fail"
    assert any(e.code == "E201" for e in result.errors)


def test_l2_detects_exec():
    code = 'exec("x=1")'
    result = validate_static(code)
    assert result.status == "fail"
    assert any(e.code == "E201" for e in result.errors)


def test_l2_detects_time_sleep():
    code = '''
import time
async def foo():
    time.sleep(1)
'''
    result = validate_static(code)
    assert result.status == "fail"
    assert any(e.code == "E202" for e in result.errors)


def test_l2_detects_os_system():
    code = '''
import os
os.system("ls")
'''
    result = validate_static(code)
    assert result.status == "fail"


def test_l2_empty_code():
    code = ""
    result = validate_static(code)
    assert result.status == "fail"
    assert result.errors[0].code == "E103"
