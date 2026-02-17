#!/usr/bin/env python3
"""Benchmark runner for tuxido validation."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tuxido.core.pipeline import validate


BENCHMARK_CASES = {
    "simple/hello.py": {
        "expected": "pass",
        "errors": [],
        "description": "Simple hello world - no errors",
    },
    "simple/syntax_error.py": {
        "expected": "fail",
        "errors": ["E101"],
        "description": "Syntax error",
    },
    "simple/os_import.py": {
        "expected": "fail",
        "errors": ["E201"],
        "description": "Forbidden import os",
    },
    "medium/counter.py": {
        "expected": "pass",
        "errors": [],
        "description": "Counter app - no errors",
    },
    "medium/async_error.py": {
        "expected": "fail",
        "errors": ["E202"],
        "description": "time.sleep in async",
    },
    "medium/eval_error.py": {
        "expected": "fail",
        "errors": ["E201"],
        "description": "eval usage",
    },
    "medium/system_error.py": {
        "expected": "fail",
        "errors": ["E201"],
        "description": "os.system usage",
    },
    "complex/todo_app.py": {
        "expected": "pass",
        "errors": [],
        "description": "Todo app - no errors",
    },
    "complex/file_manager.py": {
        "expected": "fail",
        "errors": ["E201"],
        "description": "subprocess usage",
    },
    "complex/dashboard.py": {
        "expected": "pass",
        "errors": [],
        "description": "Dashboard - no errors (L3 warnings expected)",
    },
}


def run_benchmark() -> dict:
    benchmark_dir = Path(__file__).parent
    results = {
        "total": len(BENCHMARK_CASES),
        "passed": 0,
        "failed": 0,
        "false_positives": 0,
        "false_negatives": 0,
        "cases": [],
    }

    for case_path, expected in BENCHMARK_CASES.items():
        file_path = benchmark_dir / case_path
        if not file_path.exists():
            print(f"Warning: {case_path} not found")
            continue

        code = file_path.read_text()

        start = time.time()
        result = validate(code, filename=case_path, depth="fast")
        elapsed = time.time() - start

        actual_errors = [e.code for e in result.errors]
        expected_errors = expected["errors"]

        case_passed = (result.status == "pass" and expected["expected"] == "pass") or (
            result.status == "fail"
            and expected["expected"] == "fail"
            and all(e in actual_errors for e in expected_errors)
        )

        is_fp = result.status == "fail" and expected["expected"] == "pass"
        is_fn = result.status == "pass" and expected["expected"] == "fail"

        if case_passed:
            results["passed"] += 1
        else:
            results["failed"] += 1

        if is_fp:
            results["false_positives"] += 1
        if is_fn:
            results["false_negatives"] += 1

        results["cases"].append(
            {
                "name": case_path,
                "expected": expected["expected"],
                "actual": result.status,
                "expected_errors": expected_errors,
                "actual_errors": actual_errors,
                "elapsed_ms": round(elapsed * 1000, 2),
                "passed": case_passed,
            }
        )

    return results


if __name__ == "__main__":
    results = run_benchmark()

    print("\n" + "=" * 60)
    print("TUXIDO BENCHMARK RESULTS")
    print("=" * 60)
    print(f"Total: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"False Positives: {results['false_positives']}")
    print(f"False Negatives: {results['false_negatives']}")

    fp_rate = (results["false_positives"] / results["total"]) * 100
    print(f"False Positive Rate: {fp_rate:.1f}%")

    print("\nDetailed Results:")
    print("-" * 60)
    for case in results["cases"]:
        status = "✓" if case["passed"] else "✗"
        print(f"{status} {case['name']}: {case['elapsed_ms']}ms")
        if not case["passed"]:
            print(f"  Expected: {case['expected']}, Got: {case['actual']}")
            print(f"  Expected errors: {case['expected_errors']}")
            print(f"  Actual errors: {case['actual_errors']}")

    print("=" * 60)

    with open("benchmark/results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nResults saved to benchmark/results.json")
