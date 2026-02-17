"""Auto-fix functionality for tuxido validation errors."""

from __future__ import annotations

import ast
import re


class Fixer:
    """Handles auto-fixing of validation errors."""

    def __init__(self, source: str, filename: str):
        self.source = source
        self.filename = filename
        self.fixes_applied: list[dict] = []

    def fix_all(self) -> str:
        """Apply all auto-fixable errors.

        Returns:
            Fixed source code
        """
        source = self.source

        source = self.fix_unused_imports(source)
        source = self.fix_missing_widget_ids(source)

        return source

    def fix_unused_imports(self, source: str) -> str:
        """Remove unused imports from source code.

        Args:
            source: Source code to fix

        Returns:
            Source code with unused imports removed
        """
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return source

        used_names: set[str] = set()

        class NameCollector(ast.NodeVisitor):
            def visit_Name(self, node: ast.Name) -> None:
                used_names.add(node.id)
                self.generic_visit(node)

            def visit_Attribute(self, node: ast.Attribute) -> None:
                used_names.add(node.attr)
                self.generic_visit(node)

        tree_visitor = NameCollector()
        tree_visitor.visit(tree)

        lines = source.split("\n")
        new_lines = []
        imports_removed = []
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if stripped.startswith("from "):
                match = re.match(r"from\s+(\S+)\s+import\s+(.+)", stripped)
                if match:
                    module = match.group(1)
                    imports_str = match.group(2)

                    imports = []
                    for imp in imports_str.split(","):
                        imp = imp.strip()
                        if " as " in imp:
                            imp = imp.split(" as ")[0].strip()
                        imports.append(imp)

                    used_imports = [imp for imp in imports if imp in used_names]

                    if not used_imports:
                        imports_removed.append(stripped)
                    else:
                        used_imports_str = ", ".join(used_imports)
                        indent = len(line) - len(line.lstrip())
                        new_line = " " * indent + f"from {module} import {used_imports_str}"
                        new_lines.append(new_line)

                    i += 1
                    continue

            elif stripped.startswith("import "):
                module = stripped.replace("import ", "").strip()

                if "," in module:
                    mods = [m.strip() for m in module.split(",")]
                    used_mods = [
                        m for m in mods if m in used_names or m.split(".")[0] in used_names
                    ]

                    if not used_mods:
                        imports_removed.append(stripped)
                    else:
                        indent = len(line) - len(line.lstrip())
                        new_line = " " * indent + "import " + ", ".join(used_mods)
                        new_lines.append(new_line)

                    i += 1
                    continue

                else:
                    if module in used_names or module.split(".")[0] in used_names:
                        new_lines.append(line)
                    else:
                        imports_removed.append(stripped)

                    i += 1
                    continue

            new_lines.append(line)
            i += 1

        if imports_removed:
            self.fixes_applied.append(
                {
                    "type": "unused_imports",
                    "count": len(imports_removed),
                    "removed": imports_removed,
                }
            )

        return "\n".join(new_lines)

    def _process_import_line(
        self,
        imp_line: str,
        imp_line_idx: int,
        used_names: set[str],
        original_lines: list[str],
        new_lines: list[str],
        imports_removed: list[str],
    ) -> None:
        """Process a single import line to check if it's unused."""
        stripped = imp_line.strip()

        if stripped.startswith("from "):
            match = re.match(r"from\s+(\S+)\s+import\s+(.+)", stripped)
            if match:
                module = match.group(1)
                imports = [i.strip() for i in match.group(2).split(",")]

                for imp in imports:
                    if imp in used_names:
                        new_lines.append(original_lines[imp_line_idx])
                        return

                imports_removed.append(stripped)
                self.fixes_applied.append(
                    {
                        "type": "unused_import",
                        "import": stripped,
                    }
                )
            else:
                new_lines.append(original_lines[imp_line_idx])

        elif stripped.startswith("import "):
            module = stripped.replace("import ", "").strip()
            if "," in module:
                modules = [m.strip() for m in module.split(",")]
                kept = []
                for mod in modules:
                    if mod in used_names or mod.split(".")[0] in used_names:
                        kept.append(mod)
                    else:
                        imports_removed.append(f"import {mod}")

                if kept:
                    new_lines.append(f"import {', '.join(kept)}")
                else:
                    imports_removed.append(stripped)
            else:
                if module in used_names or module.split(".")[0] in used_names:
                    new_lines.append(original_lines[imp_line_idx])
                else:
                    imports_removed.append(stripped)
        else:
            new_lines.append(original_lines[imp_line_idx])

    def fix_missing_widget_ids(self, source: str) -> str:
        """Add missing IDs to widgets.

        Args:
            source: Source code to fix

        Returns:
            Source code with widget IDs added
        """
        lines = source.split("\n")
        new_lines = []
        widget_counter: dict[str, int] = {}
        ids_added = []

        for line in lines:
            widget_match = re.search(
                r"(yield\s+(Button|Static|Input|TextArea|Header|Footer)\s*)(\(.+\))",
                line,
            )
            if widget_match:
                widget_type = widget_match.group(2)
                widget_start = widget_match.group(1)
                widget_args = widget_match.group(3)

                has_id = re.search(r"id\s*=", line)
                if not has_id:
                    widget_counter[widget_type] = widget_counter.get(widget_type, 0) + 1
                    new_id = widget_type.lower() + "_" + str(widget_counter[widget_type])

                    indent = len(line) - len(line.lstrip())
                    widget_args_inner = widget_args[1:-1]
                    if widget_args_inner.strip():
                        line = (
                            " " * indent
                            + widget_start
                            + "("
                            + widget_args_inner
                            + ', id="'
                            + new_id
                            + '")'
                        )
                    else:
                        line = " " * indent + widget_start + '(id="' + new_id + '")'

                    ids_added.append(
                        {
                            "widget": widget_type,
                            "id": new_id,
                        }
                    )

            new_lines.append(line)

        if ids_added:
            self.fixes_applied.append(
                {
                    "type": "widget_ids",
                    "count": len(ids_added),
                    "added": ids_added,
                }
            )

        return "\n".join(new_lines)

    def get_fixes_summary(self) -> dict:
        """Get summary of fixes applied.

        Returns:
            Summary of fixes
        """
        return {
            "total_fixes": len(self.fixes_applied),
            "fixes": self.fixes_applied,
        }


def fix_code(source: str, filename: str) -> tuple[str, dict]:
    """Apply auto-fixes to source code.

    Args:
        source: Source code to fix
        filename: Name of the file

    Returns:
        Tuple of (fixed_source, fixes_summary)
    """
    fixer = Fixer(source, filename)
    fixed_source = fixer.fix_all()
    summary = fixer.get_fixes_summary()

    return fixed_source, summary
