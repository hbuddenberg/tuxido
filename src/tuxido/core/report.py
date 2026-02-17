"""Report generation for tuxido validation results."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from tuxido.core.models import ValidationResult


def generate_html_report(result: ValidationResult, filename: str = "validation.html") -> str:
    """Generate HTML report from validation result.

    Args:
        result: ValidationResult to convert to HTML
        filename: Name of the validated file

    Returns:
        HTML string
    """
    status_badge = "✅ Pass" if result.status == "pass" else "❌ Fail"
    status_class = "pass" if result.status == "pass" else "fail"

    errors_html = ""
    if result.errors:
        for error in result.errors:
            severity_icon = "🔴" if error.severity == "error" else "🟡"
            errors_html += f"""
        <tr>
            <td>{error.line or "-"}</td>
            <td><code>{error.code}</code></td>
            <td>{error.message}</td>
            <td>{severity_icon} {error.severity}</td>
        </tr>"""
    else:
        errors_html = """
        <tr>
            <td colspan="4" style="text-align: center; color: #666;">No errors found</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tuxido Validation Report - {filename}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 40px;
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .status {{
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 16px;
        }}
        .status.pass {{ background: #10b981; color: white; }}
        .status.fail {{ background: #ef4444; color: white; }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            padding: 30px 40px;
            background: #f8fafc;
        }}
        .summary-item {{
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }}
        .summary-item .value {{
            font-size: 36px;
            font-weight: bold;
            color: #1e293b;
        }}
        .summary-item .label {{
            font-size: 14px;
            color: #64748b;
            margin-top: 5px;
        }}
        .summary-item.errors .value {{ color: #ef4444; }}
        .summary-item.warnings .value {{ color: #f59e0b; }}
        .summary-item.total .value {{ color: #3b82f6; }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .errors-table {{
            padding: 0 40px 40px;
        }}
        .errors-table h2 {{
            font-size: 20px;
            color: #1e293b;
            margin: 30px 0 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        }}
        .errors-table th {{
            text-align: left;
            padding: 15px;
            background: #f1f5f9;
            color: #475569;
            font-weight: 600;
            font-size: 14px;
        }}
        .errors-table td {{
            padding: 15px;
            border-bottom: 1px solid #e2e8f0;
            color: #334155;
        }}
        .errors-table tr:hover {{ background: #f8fafc; }}
        .errors-table code {{
            background: #f1f5f9;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 13px;
            color: #7c3aed;
        }}
        .metadata {{
            padding: 20px 40px;
            background: #1e293b;
            color: #94a3b8;
            font-size: 13px;
        }}
        .metadata-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Tuxido Validation Report</h1>
            <p style="opacity: 0.9; font-size: 16px;">{filename}</p>
            <span class="status {status_class}" style="margin-top: 15px;">{status_badge}</span>
        </div>

        <div class="summary">
            <div class="summary-item total">
                <div class="value">{result.summary.total}</div>
                <div class="label">Total Findings</div>
            </div>
            <div class="summary-item errors">
                <div class="value">{result.summary.errors}</div>
                <div class="label">Errors</div>
            </div>
            <div class="summary-item warnings">
                <div class="value">{result.summary.warnings}</div>
                <div class="label">Warnings</div>
            </div>
        </div>

        <div class="errors-table">
            <h2>📋 Validation Findings</h2>
            <table>
                <thead>
                    <tr>
                        <th>Line</th>
                        <th>Code</th>
                        <th>Message</th>
                        <th>Severity</th>
                    </tr>
                </thead>
                <tbody>
                    {errors_html}
                </tbody>
            </table>
        </div>

        <div class="metadata">
            <div class="metadata-grid">
                <div><strong>tuxido:</strong> {result.metadata.version}</div>
                <div><strong>Python:</strong> {result.metadata.python}</div>
                <div><strong>Textual:</strong> {result.metadata.textual or "N/A"}</div>
                <div><strong>Date:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
            </div>
        </div>
    </div>
</body>
</html>"""

    return html


def generate_markdown_report(result: ValidationResult, filename: str = "validation.md") -> str:
    """Generate Markdown report from validation result.

    Args:
        result: ValidationResult to convert to Markdown
        filename: Name of the validated file

    Returns:
        Markdown string
    """
    status_badge = "✅ PASS" if result.status == "pass" else "❌ FAIL"

    errors_md = ""
    if result.errors:
        errors_md = """
## 📋 Validation Findings

| Line | Code | Message | Severity |
|------|------|---------|----------|
"""
        for error in result.errors:
            severity_badge = "🔴 error" if error.severity == "error" else "🟡 warning"
            line = str(error.line) if error.line else "-"
            errors_md += f"| {line} | `{error.code}` | {error.message} | {severity_badge} |\n"
    else:
        errors_md = "\n## 📋 Validation Findings\n\n*No errors found*\n"

    markdown = f"""# 🔍 Tuxido Validation Report

**File:** `{filename}`
**Status:** {status_badge}

---

## 📊 Summary

- **Total:** {result.summary.total}
- **Errors:** {result.summary.errors}
- **Warnings:** {result.summary.warnings}

{errors_md}

---

## 🔧 Metadata

- **tuxido:** {result.metadata.version}
- **Python:** {result.metadata.python}
- **Textual:** {result.metadata.textual or "N/A"}
- **Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

*Generated by [Tuxido](https://github.com/hubuddenberg/tuxido) - AI-Native Framework Validator*
"""

    return markdown


def save_report(content: str, output_path: Path) -> None:
    """Save report content to file.

    Args:
        content: Report content
        output_path: Path to save the report
    """
    output_path.write_text(content, encoding="utf-8")
