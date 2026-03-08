import csv
import os
import sys

import click
from rich.console import Console
from rich.table import Table
from rich import box

from txtool.core.data import (
    json_pretty as core_json_pretty,
    json_minify as core_json_minify,
    json_validate as core_json_validate,
    json_get as core_json_get,
    csv_filter as core_csv_filter,
    csv_select as core_csv_select,
    csv_to_json as core_csv_to_json,
    parse_env,
    env_diff as core_env_diff,
    render_template,
)

console = Console()


def _read_stdin_or_file(file):
    if file is None or file == "-":
        return sys.stdin.read()
    with open(file, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


# ---------------------------------------------------------------------------
# json group
# ---------------------------------------------------------------------------

@click.group("json")
def json_cmd():
    """JSON utilities: pretty, minify, validate, get."""
    pass


@json_cmd.command("pretty")
@click.argument("file", required=False)
def json_pretty(file):
    """Pretty-print JSON."""
    text = _read_stdin_or_file(file)
    try:
        sys.stdout.write(core_json_pretty(text) + "\n")
    except Exception as e:
        console.print(f"[red]JSON error: {e}[/red]")
        raise SystemExit(1)


@json_cmd.command("minify")
@click.argument("file", required=False)
def json_minify(file):
    """Minify JSON."""
    text = _read_stdin_or_file(file)
    try:
        sys.stdout.write(core_json_minify(text) + "\n")
    except Exception as e:
        console.print(f"[red]JSON error: {e}[/red]")
        raise SystemExit(1)


@json_cmd.command("validate")
@click.argument("file", required=False)
def json_validate(file):
    """Validate JSON."""
    text = _read_stdin_or_file(file)
    valid, error = core_json_validate(text)
    if valid:
        console.print("[green]Valid[/green]")
    else:
        console.print(f"[red]Invalid JSON: {error}[/red]")
        raise SystemExit(1)


@json_cmd.command("get")
@click.argument("path")
@click.argument("file", required=False)
def json_get(path, file):
    """Extract value by dot-notation path e.g. 'users[0].name'."""
    text = _read_stdin_or_file(file)
    try:
        value = core_json_get(text, path)
        sys.stdout.write(value + "\n")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# csv group
# ---------------------------------------------------------------------------

@click.group("csv")
def csv_cmd():
    """CSV utilities: view, filter, select, to-json."""
    pass


@csv_cmd.command("view")
@click.argument("file")
@click.option("-d", "--delimiter", default=",", help="Field separator (default: ',')")
def csv_view(file, delimiter):
    """Render CSV as a rich table."""
    try:
        with open(file, "r", encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.reader(f, delimiter=delimiter)
            rows = list(reader)
    except Exception as e:
        console.print(f"[red]Error reading {file}: {e}[/red]")
        raise SystemExit(1)

    if not rows:
        console.print("[yellow]Empty file.[/yellow]")
        return

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    headers = rows[0]
    for h in headers:
        table.add_column(h)
    for row in rows[1:]:
        padded = row + [""] * max(0, len(headers) - len(row))
        table.add_row(*padded[:len(headers)])
    console.print(table)


@csv_cmd.command("filter")
@click.argument("condition")
@click.argument("file")
@click.option("-d", "--delimiter", default=",", help="Field separator (default: ',')")
def csv_filter(condition, file, delimiter):
    """Filter CSV rows by condition like 'status=active' or 'age>30'."""
    try:
        with open(file, "r", encoding="utf-8", errors="replace", newline="") as f:
            text = f.read()
        result = core_csv_filter(text, condition, delimiter)
        sys.stdout.write(result)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise SystemExit(1)


@csv_cmd.command("select")
@click.argument("columns")
@click.argument("file")
@click.option("-d", "--delimiter", default=",", help="Field separator (default: ',')")
def csv_select(columns, file, delimiter):
    """Keep only specified columns (comma-separated names or 1-indexed numbers)."""
    try:
        with open(file, "r", encoding="utf-8", errors="replace", newline="") as f:
            text = f.read()
        result = core_csv_select(text, columns, delimiter)
        sys.stdout.write(result)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise SystemExit(1)


@csv_cmd.command("to-json")
@click.argument("file")
@click.option("-d", "--delimiter", default=",", help="Field separator (default: ',')")
def csv_to_json(file, delimiter):
    """Convert CSV to JSON array."""
    try:
        with open(file, "r", encoding="utf-8", errors="replace", newline="") as f:
            text = f.read()
        sys.stdout.write(core_csv_to_json(text, delimiter) + "\n")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# env group
# ---------------------------------------------------------------------------

@click.group("env")
def env_cmd():
    """Env file utilities: show, diff, check."""
    pass


@env_cmd.command("show")
@click.argument("file", default=".env")
def env_show(file):
    """Pretty-print .env file as a table."""
    try:
        with open(file, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except Exception as e:
        console.print(f"[red]Error reading {file}: {e}[/red]")
        raise SystemExit(1)

    data = parse_env(text)
    if not data:
        console.print("[yellow]Empty or no valid entries.[/yellow]")
        return

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("KEY", style="bold cyan")
    table.add_column("VALUE")
    for k, v in sorted(data.items()):
        table.add_row(k, v)
    console.print(table)


@env_cmd.command("diff")
@click.argument("file1")
@click.argument("file2")
def env_diff(file1, file2):
    """Show keys added/removed/changed between two env files."""
    try:
        with open(file1, "r", encoding="utf-8", errors="replace") as f:
            text1 = f.read()
        with open(file2, "r", encoding="utf-8", errors="replace") as f:
            text2 = f.read()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise SystemExit(1)

    diff = core_env_diff(text1, text2)
    found_diff = False

    for key, val in diff["added"].items():
        console.print(f"[green]+ {key}={val}[/green]")
        found_diff = True
    for key, val in diff["removed"].items():
        console.print(f"[red]- {key}={val}[/red]")
        found_diff = True
    for key, vals in diff["changed"].items():
        console.print(f"[yellow]~ {key}: {vals['old']!r} → {vals['new']!r}[/yellow]")
        found_diff = True

    if not found_diff:
        console.print("[dim]No differences.[/dim]")


@env_cmd.command("check")
@click.argument("template")
@click.argument("file")
def env_check(template, file):
    """Check that all keys in template exist in file."""
    try:
        with open(template, "r", encoding="utf-8", errors="replace") as f:
            template_keys = parse_env(f.read())
        with open(file, "r", encoding="utf-8", errors="replace") as f:
            file_keys = parse_env(f.read())
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise SystemExit(1)

    missing = [k for k in template_keys if k not in file_keys]
    if missing:
        console.print("[red]Missing keys:[/red]")
        for k in missing:
            console.print(f"  [red]- {k}[/red]")
        raise SystemExit(1)
    else:
        console.print("[green]All keys present.[/green]")


# ---------------------------------------------------------------------------
# template
# ---------------------------------------------------------------------------

@click.command("template")
@click.argument("file")
@click.argument("vars", nargs=-1)
@click.option("--env", "use_env", is_flag=True, help="Also use current environment variables")
@click.option("--in-place", is_flag=True, help="Write back to file instead of stdout")
def template_cmd(file, vars, use_env, in_place):
    """Replace {{VAR}} in file with values from KEY=value pairs."""
    substitutions = {}

    if use_env:
        substitutions.update(os.environ)

    for var in vars:
        if "=" in var:
            key, _, value = var.partition("=")
            substitutions[key.strip()] = value.strip()

    try:
        with open(file, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except Exception as e:
        console.print(f"[red]Error reading {file}: {e}[/red]")
        raise SystemExit(1)

    result = render_template(text, substitutions)

    if in_place:
        with open(file, "w", encoding="utf-8") as f:
            f.write(result)
    else:
        sys.stdout.write(result)
