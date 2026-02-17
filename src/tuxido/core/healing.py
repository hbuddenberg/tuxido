"""Self-healing engine for autonomous code correction."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Callable


class IssueType(Enum):
    MISSING_WIDGET = "missing_widget_in_dom"
    WIDGET_ID_MISMATCH = "widget_id_mismatch"
    WIDGET_LABEL_MISMATCH = "widget_label_mismatch"
    WIDGET_POSITION_MISMATCH = "widget_position_mismatch"
    WIDGET_TYPE_MISMATCH = "widget_type_mismatch"
    UNUSED_IMPORT = "unused_import"
    FORBIDDEN_IMPORT = "forbidden_import"
    SYNTAX_ERROR = "syntax_error"
    ASYNC_PATTERN = "async_pattern"


@dataclass
class CorrectionRule:
    name: str
    pattern: IssueType
    priority: int
    success_rate: float
    fix_func: Callable[[str, dict], str]


class RulesEngine:
    """Engine for applying correction rules."""

    def __init__(self) -> None:
        self.rules = self._load_builtin_rules()

    def _load_builtin_rules(self) -> list[CorrectionRule]:
        return [
            CorrectionRule(
                name="fix_unused_import",
                pattern=IssueType.UNUSED_IMPORT,
                priority=1,
                success_rate=0.95,
                fix_func=self._fix_unused_import,
            ),
            CorrectionRule(
                name="fix_widget_id",
                pattern=IssueType.WIDGET_ID_MISMATCH,
                priority=2,
                success_rate=0.92,
                fix_func=self._fix_widget_id,
            ),
            CorrectionRule(
                name="fix_forbidden_import",
                pattern=IssueType.FORBIDDEN_IMPORT,
                priority=1,
                success_rate=0.85,
                fix_func=self._fix_forbidden_import,
            ),
            CorrectionRule(
                name="fix_widget_label",
                pattern=IssueType.WIDGET_LABEL_MISMATCH,
                priority=3,
                success_rate=0.88,
                fix_func=self._fix_widget_label,
            ),
        ]

    def get_applicable_rules(self, issue_type: IssueType) -> list[CorrectionRule]:
        applicable = [r for r in self.rules if r.pattern == issue_type]
        return sorted(applicable, key=lambda r: r.priority)

    def _fix_unused_import(self, code: str, context: dict) -> str:
        lines = code.split("\n")
        import_to_remove = context.get("import", "")
        new_lines = []
        for line in lines:
            if (
                import_to_remove
                and import_to_remove in line
                and line.strip().startswith(("import ", "from "))
            ):
                continue
            new_lines.append(line)
        return "\n".join(new_lines)

    def _fix_widget_id(self, code: str, context: dict) -> str:
        widget_type = context.get("widget_type", "Widget")
        widget_id = context.get("widget_id", f"{widget_type.lower()}_1")
        widget_label = context.get("label", "")

        pattern = rf'(yield\s+{widget_type}\s*\(\s*["\'][^"\']*["\']?\s*\))'
        match = re.search(pattern, code)
        if match:
            old_yield = match.group(1)
            if "id=" not in old_yield:
                if widget_label:
                    new_yield = f'yield {widget_type}("{widget_label}", id="{widget_id}")'
                else:
                    new_yield = f'yield {widget_type}(id="{widget_id}")'
                code = code.replace(old_yield, new_yield)
        return code

    def _fix_forbidden_import(self, code: str, context: dict) -> str:
        forbidden = context.get("import", "")
        lines = code.split("\n")
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(("import ", "from ")):
                if forbidden in stripped:
                    continue
            new_lines.append(line)
        return "\n".join(new_lines)

    def _fix_widget_label(self, code: str, context: dict) -> str:
        widget_id = context.get("widget_id", "")
        new_label = context.get("new_label", "")

        if widget_id and new_label:
            pattern = rf'(yield\s+\w+\s*\(\s*["\'][^"\']*["\']?\s*,\s*id\s*=\s*["\']{widget_id}["\']\s*\))'
            match = re.search(pattern, code)
            if match:
                old_yield = match.group(1)
                widget_match = re.search(r"yield\s+(\w+)", old_yield)
                if widget_match:
                    widget_type = widget_match.group(1)
                    new_yield = f'yield {widget_type}("{new_label}", id="{widget_id}")'
                    code = code.replace(old_yield, new_yield)
        return code


class SelfHealingEngine:
    """Main self-healing engine for iterative code correction."""

    def __init__(self, max_iterations: int = 5) -> None:
        self.rules_engine = RulesEngine()
        self.max_iterations = max_iterations
        self.iteration_count = 0
        self.fixes_applied: list[dict] = []

    def heal(
        self,
        code: str,
        issues: list[dict],
    ) -> tuple[str, bool]:
        """Apply healing iterations until code is fixed or max iterations reached.

        Args:
            code: Source code to heal
            issues: List of issues to fix

        Returns:
            Tuple of (healed_code, success)
        """
        self.iteration_count = 0
        self.fixes_applied = []

        current_code = code
        remaining_issues = issues.copy()

        while remaining_issues and self.iteration_count < self.max_iterations:
            self.iteration_count += 1
            fixed_this_iteration = False

            for issue in remaining_issues.copy():
                issue_type_str = issue.get("type", "")
                try:
                    issue_type = IssueType(issue_type_str)
                except ValueError:
                    continue

                rules = self.rules_engine.get_applicable_rules(issue_type)

                for rule in rules:
                    try:
                        new_code = rule.fix_func(current_code, issue)
                        if new_code != current_code:
                            current_code = new_code
                            remaining_issues.remove(issue)
                            self.fixes_applied.append(
                                {
                                    "iteration": self.iteration_count,
                                    "rule": rule.name,
                                    "issue": issue,
                                    "success_rate": rule.success_rate,
                                }
                            )
                            fixed_this_iteration = True
                            break
                    except Exception:
                        continue

            if not fixed_this_iteration:
                break

        success = len(remaining_issues) == 0
        return current_code, success

    def get_healing_report(self) -> dict:
        """Get report of healing process.

        Returns:
            Healing report with iterations and fixes
        """
        return {
            "iterations": self.iteration_count,
            "max_iterations": self.max_iterations,
            "fixes_applied": len(self.fixes_applied),
            "fixes": self.fixes_applied,
        }
