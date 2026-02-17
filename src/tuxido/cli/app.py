from __future__ import annotations

from pathlib import Path
import sys
from typing import Annotated, Any

from rich.console import Console
from rich.table import Table
import typer

from tuxido.core._metadata import get_versions
from tuxido.core.fixer import fix_code
from tuxido.core.generator import ascii_to_textual
from tuxido.core.healing import SelfHealingEngine
from tuxido.core.oracle import get_framework_info
from tuxido.core.pipeline import validate
from tuxido.core.report import generate_html_report, generate_markdown_report, save_report

app = typer.Typer(
    name="tuxido",
    help="AI-Native Framework Validator for Textual TUI Applications",
)
console = Console()


def validate_file(
    path: Path,
    depth: str,
    json_output: bool,
    timeout: int | None = None,
    report: str | None = None,
) -> int:
    """Validate a single file and return exit code."""
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        console.print(f"[red]Error:[/red] Encoding error in {path}: {e}")
        return 2

    result = validate(source, filename=str(path), depth=depth, timeout=timeout)

    if report:
        report_filename = str(path)
        if report == "html":
            html_content = generate_html_report(result, report_filename)
            output_path = Path(str(path).replace(".py", ".html"))
            save_report(html_content, output_path)
            console.print(f"[green]✓[/green] Report saved to: {output_path}")
        elif report == "markdown":
            md_content = generate_markdown_report(result, report_filename)
            output_path = Path(str(path).replace(".py", ".md"))
            save_report(md_content, output_path)
            console.print(f"[green]✓[/green] Report saved to: {output_path}")
        else:
            console.print(
                f"[yellow]Warning:[/yellow] Unknown report format: {report}. Use 'html' or 'markdown'."
            )
    elif json_output:
        import orjson

        console.print(orjson.dumps(result.model_dump(), option=orjson.OPT_INDENT_2).decode())
    elif result.status == "pass":
        console.print(f"[green]✓[/green] {path}: Valid")
    else:
        table = Table(title=f"Validation Results for {path}")
        table.add_column("Line", style="cyan")
        table.add_column("Code", style="yellow")
        table.add_column("Message", style="white")
        table.add_column("Severity", style="red")

        for error in result.errors:
            table.add_row(
                str(error.line or "-"),
                error.code,
                error.message,
                error.severity,
            )

        console.print(table)

    return 0 if result.status == "pass" else 1


@app.command()
def check(
    path: Annotated[list[Path], typer.Argument(help="Python file(s), '-' for stdin, or directory")],
    depth: Annotated[
        str,
        typer.Option("--depth", help="Validation depth: fast (L1+L2) or full (L1-L4)"),
    ] = "fast",
    timeout: Annotated[
        int | None,
        typer.Option("--timeout", help="Timeout for L4 sandbox in seconds"),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output JSON instead of formatted table"),
    ] = False,
    no_color: Annotated[
        bool,
        typer.Option("--no-color", help="Disable colored output"),
    ] = False,
    report: Annotated[
        str | None,
        typer.Option("--report", "-r", help="Generate report: html or markdown"),
    ] = None,
) -> None:
    """Validate a Textual TUI application."""
    if not path:
        if sys.stdin.isatty():
            console.print("[red]Error:[/red] No input file specified.")
            raise typer.Exit(code=2)
        source = sys.stdin.read()
        result = validate(source, filename="stdin", depth=depth, timeout=timeout)

        if json_output:
            import orjson

            console.print(orjson.dumps(result.model_dump(), option=orjson.OPT_INDENT_2).decode())
        elif result.status == "pass":
            console.print("[green]✓[/green] stdin: Valid")
        else:
            table = Table(title="Validation Results for stdin")
            table.add_column("Line", style="cyan")
            table.add_column("Code", style="yellow")
            table.add_column("Message", style="white")
            table.add_column("Severity", style="red")

            for error in result.errors:
                table.add_row(
                    str(error.line or "-"),
                    error.code,
                    error.message,
                    error.severity,
                )

            console.print(table)

        raise typer.Exit(code=0 if result.status == "pass" else 1)

    exit_code = 0
    for p in path:
        if str(p) == "-":
            if sys.stdin.isatty():
                console.print("[red]Error:[/red] No stdin data available")
                exit_code = 2
            else:
                source = sys.stdin.read()
                result = validate(source, filename="stdin", depth=depth, timeout=timeout)
                if result.status != "pass":
                    exit_code = 1
                if json_output:
                    import orjson

                    console.print(
                        orjson.dumps(result.model_dump(), option=orjson.OPT_INDENT_2).decode(),
                    )
                elif result.status == "pass":
                    console.print("[green]✓[/green] stdin: Valid")
                else:
                    table = Table(title="Validation Results for stdin")
                    table.add_column("Line", style="cyan")
                    table.add_column("Code", style="yellow")
                    table.add_column("Message", style="white")
                    table.add_column("Severity", style="red")

                    for error in result.errors:
                        table.add_row(
                            str(error.line or "-"),
                            error.code,
                            error.message,
                            error.severity,
                        )

                    console.print(table)
        elif p.is_dir():
            py_files = list(p.rglob("*.py"))
            if not py_files:
                console.print(f"[yellow]Warning:[/yellow] No .py files found in {p}")
                continue

            console.print(f"[cyan]Validating {len(py_files)} files in {p}/[/cyan]")
            for py_file in py_files:
                file_exit = validate_file(py_file, depth, json_output, timeout, report)
                if file_exit != 0:
                    exit_code = file_exit
        elif p.exists():
            file_exit = validate_file(p, depth, json_output, timeout, report)
            if file_exit != 0:
                exit_code = file_exit
        else:
            console.print(f"[red]Error:[/red] File not found: {p}")
            exit_code = 2

    raise typer.Exit(code=exit_code)


@app.command()
def fix(
    path: Annotated[Path, typer.Argument(help="Python file to fix")],
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", "-n", help="Show what would be fixed without making changes"),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed output"),
    ] = False,
) -> None:
    """Auto-fix validation errors in a TUI application."""
    if not path.exists():
        console.print(f"[red]Error:[/red] File not found: {path}")
        raise typer.Exit(code=2)

    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        console.print(f"[red]Error:[/red] Encoding error in {path}: {e}")
        raise typer.Exit(code=2)

    console.print(f"[cyan]Analyzing:[/cyan] {path}")

    fixed_source, summary = fix_code(source, str(path))

    if summary["total_fixes"] == 0:
        console.print("[green]✓[/green] No issues to fix!")
        raise typer.Exit(code=0)

    if verbose or summary["total_fixes"] > 0:
        table = Table(title="Fixes Applied")
        table.add_column("Type", style="cyan")
        table.add_column("Count", style="yellow")
        table.add_column("Details", style="white")

        for fix in summary["fixes"]:
            fix_type = fix.get("type", "unknown")
            count = fix.get("count", 1)
            details = str(fix.get("removed", fix.get("added", "")))
            table.add_row(fix_type, str(count), details)

        console.print(table)

    if dry_run:
        console.print("\n[yellow]Dry run mode - no changes made[/yellow]")
        console.print(f"[cyan]Would apply {summary['total_fixes']} fix(es)[/cyan]")
    else:
        path.write_text(fixed_source, encoding="utf-8")
        console.print(f"\n[green]✓[/green] Applied {summary['total_fixes']} fix(es)")

        result = validate(fixed_source, filename=str(path), depth="fast")

        if result.status == "pass":
            console.print("[green]✓[/green] Validation passed after fixes!")
        else:
            console.print(f"[yellow]Warning:[/yellow] {result.summary.errors} error(s) remain")


@app.command()
def version() -> None:
    """Show version information."""
    versions = get_versions()
    table = Table(title="tuxido Version Information")
    table.add_column("Component", style="cyan")
    table.add_column("Version", style="green")

    table.add_row("tuxido", versions["tuxido"] or "unknown")
    table.add_row("Python", versions["python"] or "unknown")
    table.add_row("Textual", versions["textual"] or "not installed")

    console.print(table)


@app.command()
def info(
    verbose: bool = False,
) -> None:
    """Show Textual framework information."""
    info = get_framework_info(detail_level="full" if verbose else "minimal")

    table = Table(title="Textual Framework Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Textual Version", info.textual_version or "not installed")
    table.add_row("Python Version", info.python_version)
    table.add_row("Platform", info.platform)

    console.print(table)

    if verbose and info.widgets:
        console.print(f"\n[cyan]Available Widgets ({len(info.widgets)}):[/cyan]")
        console.print(", ".join(info.widgets[:20]))
        if len(info.widgets) > 20:
            console.print(f"  ... and {len(info.widgets) - 20} more")

    if verbose and info.deprecated:
        console.print(f"\n[yellow]Deprecated APIs ({len(info.deprecated)}):[/yellow]")
        console.print(", ".join(info.deprecated))


@app.command()
def heal(
    path: Annotated[Path, typer.Argument(help="Python file to heal")],
    max_iterations: Annotated[
        int,
        typer.Option("--max-iterations", "-i", help="Maximum healing iterations"),
    ] = 5,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", "-n", help="Show what would be healed without making changes"),
    ] = False,
) -> None:
    """Self-heal validation errors with iterative correction."""
    if not path.exists():
        console.print(f"[red]Error:[/red] File not found: {path}")
        raise typer.Exit(code=2)

    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        console.print(f"[red]Error:[/red] Encoding error in {path}: {e}")
        raise typer.Exit(code=2)

    console.print(f"[cyan]Analyzing:[/cyan] {path}")

    result = validate(source, filename=str(path), depth="fast")

    if result.status == "pass":
        console.print("[green]✓[/green] No issues to heal!")
        raise typer.Exit(code=0)

    issues = []
    for error in result.errors:
        issue_type = error.code[:3] if error.code else "UNK"
        issues.append(
            {
                "type": issue_type,
                "code": error.code,
                "message": error.message,
                "line": error.line,
            }
        )

    console.print(f"[yellow]Found {len(issues)} issues, starting healing...[/yellow]")

    engine = SelfHealingEngine(max_iterations=max_iterations)
    healed_code, success = engine.heal(source, issues)
    report = engine.get_healing_report()

    if report["fixes_applied"] > 0:
        table = Table(title="Healing Report")
        table.add_column("Iteration", style="cyan")
        table.add_column("Rule", style="yellow")
        table.add_column("Success Rate", style="green")

        for fix in report["fixes"]:
            table.add_row(
                str(fix["iteration"]),
                fix["rule"],
                f"{fix['success_rate'] * 100:.0f}%",
            )

        console.print(table)

    if dry_run:
        console.print("\n[yellow]Dry run mode - no changes made[/yellow]")
        console.print(
            f"[cyan]Would apply {report['fixes_applied']} fix(es) in {report['iterations']} iteration(s)[/cyan]"
        )
    else:
        path.write_text(healed_code, encoding="utf-8")
        console.print(
            f"\n[green]✓[/green] Applied {report['fixes_applied']} fix(es) in {report['iterations']} iteration(s)"
        )

        new_result = validate(healed_code, filename=str(path), depth="fast")

        if new_result.status == "pass":
            console.print("[green]✓[/green] All issues healed!")
        else:
            console.print(f"[yellow]Warning:[/yellow] {new_result.summary.total} issue(s) remain")


@app.command()
def generate(
    ascii_file: Annotated[
        Path | None,
        typer.Argument(help="ASCII art file to convert (or use --text)"),
    ] = None,
    text: Annotated[
        str | None,
        typer.Option("--text", "-t", help="ASCII art as string"),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output file path"),
    ] = None,
    name: Annotated[
        str,
        typer.Option("--name", "-n", help="App class name"),
    ] = "GeneratedApp",
    validate_output: Annotated[
        bool,
        typer.Option("--validate/--no-validate", help="Validate generated code"),
    ] = True,
) -> None:
    """Generate Textual TUI code from ASCII art layout."""
    ascii_content = None

    if text:
        ascii_content = text
    elif ascii_file and ascii_file.exists():
        ascii_content = ascii_file.read_text(encoding="utf-8")
    else:
        console.print("[red]Error:[/red] Provide ASCII art via --text or a file path")
        raise typer.Exit(code=2)

    console.print("[cyan]Generating Textual code from ASCII art...[/cyan]")

    try:
        code = ascii_to_textual(ascii_content, app_name=name)
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to generate code: {e}")
        raise typer.Exit(code=1)

    if validate_output:
        console.print("[cyan]Validating generated code...[/cyan]")
        result = validate(code, filename="generated.py", depth="fast")

        if result.status == "pass":
            console.print("[green]✓[/green] Generated code is valid!")
        else:
            console.print("[yellow]Warning:[/yellow] Generated code has issues:")
            for error in result.errors:
                console.print(f"  - {error.code}: {error.message}")

    if output:
        output.write_text(code, encoding="utf-8")
        console.print(f"\n[green]✓[/green] Code saved to: {output}")
    else:
        console.print("\n[cyan]Generated code:[/cyan]")
        console.print("[dim]─" * 40 + "[/dim]")
        console.print(code)


@app.command()
def mcp(
    fastmcp: Annotated[
        bool,
        typer.Option("--fastmcp", help="Use FastMCP server with SkillsProvider (requires: pip install tuxido[mcp])"),
    ] = False,
) -> None:
    """Start MCP server (stdio protocol)."""
    if fastmcp:
        from tuxido.mcp import run_fastmcp_server
        run_fastmcp_server()
        return

    import json
    import sys

    from tuxido.mcp.server import MCP_TOOLS, get_framework_info, validate_tui

    def handle_request(request: dict[str, Any]) -> dict[str, Any]:
        method = request.get("method")
        request_id = request.get("id")

        if method == "tools/list":
            tools = []
            for name, spec in MCP_TOOLS.items():
                tools.append(
                    {
                        "name": name,
                        "description": spec["description"],
                        "inputSchema": spec["input_schema"],
                    },
                )
            return {"id": request_id, "result": {"tools": tools}}

        if method == "tools/call":
            tool_name = request.get("params", {}).get("name")
            args = request.get("params", {}).get("arguments", {})

            if tool_name == "validate_tui":
                result = validate_tui(
                    code=args.get("code", ""),
                    depth=args.get("depth", "fast"),
                    filename=args.get("filename", "app.py"),
                )
            elif tool_name == "get_framework_info":
                result = get_framework_info(detail_level=args.get("detail_level", "minimal"))
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            return {
                "id": request_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result)}]},
            }

        return {"id": request_id, "error": {"code": "method_not_found"}}

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            request = json.loads(line)
            response = handle_request(request)
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except EOFError:
            break
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.stderr.flush()


@app.command()
def completion(
    shell: str = typer.Argument(..., help="Shell: bash, zsh, or fish"),
) -> None:
    """Install shell completion for tuxido."""
    console.print("[yellow]Shell completion installation:[/yellow]")
    console.print("")
    console.print("For bash:")
    console.print("  tuxido --install-completion bash >> ~/.bashrc")
    console.print("")
    console.print("For zsh:")
    console.print("  tuxido --install-completion zsh >> ~/.zshrc")
    console.print("")
    console.print("For fish:")
    console.print("  tuxido --install-completion fish > ~/.config/fish/completions/tuxido.fish")


@app.command()
def install_completion(
    shell: str = typer.Argument(..., help="Shell: bash, zsh, or fish"),
) -> None:
    """Install shell completion (alias for completion)."""
    console.print(f"Installing completion for {shell}...")

    if shell == "bash":
        script = """# tuxido completion for bash
_tuxido_completion() {
    local cur prev
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    case ${COMP_CWORD} in
        1)
            COMPREPLY=($(compgen -W "check version info mcp completion install-completion" -- ${cur}))
            ;;
        2)
            case ${prev} in
                check)
                    _filedir '@(.py)'
                    ;;
                --depth)
                    COMPREPLY=($(compgen -W "fast full" -- ${cur}))
                    ;;
                --json|--no-color)
                    COMPREPLY=($(compgen -W "true false" -- ${cur}))
                    ;;
            esac
            ;;
    esac
    return 0
}
complete -F _tuxido_completion tuxido
"""
        console.print(script)
    elif shell == "zsh":
        script = """# tuxido completion for zsh
_tuxido() {
    local -a commands
    commands=(
        'check:Validate a TUI application'
        'version:Show version information'
        'info:Show Textual framework information'
        'mcp:Start MCP server'
        'completion:Install shell completion'
    )
    _describe 'command' commands
}
compdef _tuxido tuxido
"""
        console.print(script)
    else:
        console.print(f"[yellow]Completion for {shell} not implemented yet.[/yellow]")


def main() -> None:
    app()
