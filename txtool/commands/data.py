import csv
import json
import os
import re
import sys

import click
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


def _read_stdin_or_file(file):
    if file is None or file == "-":
        return sys.stdin.read()
    with open(file, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _read_stdin_or_file_lines(file):
    if file is None or file == "-":
        return sys.stdin.readlines()
    with open(file, "r", encoding="utf-8", errors="replace") as f:
        return f.readlines()


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
        data = json.loads(text)
        sys.stdout.write(json.dumps(data, indent=2) + "\n")
    except json.JSONDecodeError as e:
        console.print(f"[red]JSON error: {e}[/red]")
        raise SystemExit(1)


@json_cmd.command("minify")
@click.argument("file", required=False)
def json_minify(file):
    """Minify JSON."""
    text = _read_stdin_or_file(file)
    try:
        data = json.loads(text)
        sys.stdout.write(json.dumps(data, separators=(",", ":")) + "\n")
    except json.JSONDecodeError as e:
        console.print(f"[red]JSON error: {e}[/red]")
        raise SystemExit(1)


@json_cmd.command("validate")
@click.argument("file", required=False)
def json_validate(file):
    """Validate JSON."""
    text = _read_stdin_or_file(file)
    try:
        json.loads(text)
        console.print("[green]Valid[/green]")
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON: {e}[/red]")
        raise SystemExit(1)


def _json_get(data, tokens):
    for token in tokens:
        if isinstance(data, dict):
            data = data[token]
        elif isinstance(data, list):
            data = data[int(token)]
        else:
            raise KeyError(f"Cannot traverse into {type(data)} with key {token!r}")
    return data


@json_cmd.command("get")
@click.argument("path")
@click.argument("file", required=False)
def json_get(path, file):
    """Extract value by dot-notation path e.g. 'users[0].name'."""
    text = _read_stdin_or_file(file)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        console.print(f"[red]JSON error: {e}[/red]")
        raise SystemExit(1)

    # Parse path like "users[0].name" into ["users", "0", "name"]
    clean_tokens = []
    for part in re.split(r'\.', path):
        # Split each part on brackets: "users[0]" -> ["users", "0"]
        sub = re.split(r'\[|\]', part)
        for s in sub:
            if s:
                clean_tokens.append(s)

    try:
        value = _json_get(data, clean_tokens)
        if isinstance(value, (dict, list)):
            sys.stdout.write(json.dumps(value, indent=2) + "\n")
        else:
            sys.stdout.write(str(value) + "\n")
    except (KeyError, IndexError, TypeError, ValueError) as e:
        console.print(f"[red]Path error: {e}[/red]")
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
        # Pad row to match header count
        padded = row + [""] * max(0, len(headers) - len(row))
        table.add_row(*padded[:len(headers)])
    console.print(table)


def _evaluate_condition(value, op, operand):
    if op == "=":
        return value == operand
    elif op == "!=":
        return value != operand
    elif op == "~":
        return bool(re.search(operand, value))
    else:
        try:
            v = float(value)
            o = float(operand)
        except ValueError:
            return False
        if op == ">":
            return v > o
        elif op == "<":
            return v < o
        elif op == ">=":
            return v >= o
        elif op == "<=":
            return v <= o
    return False


@csv_cmd.command("filter")
@click.argument("condition")
@click.argument("file")
@click.option("-d", "--delimiter", default=",", help="Field separator (default: ',')")
def csv_filter(condition, file, delimiter):
    """Filter CSV rows by condition like 'status=active' or 'age>30'."""
    # Parse condition
    m = re.match(r'^(\w+)\s*(>=|<=|!=|>|<|=|~)\s*(.+)$', condition)
    if not m:
        console.print(f"[red]Invalid condition: {condition}[/red]")
        raise SystemExit(1)
    col_name, op, operand = m.group(1), m.group(2), m.group(3)

    try:
        with open(file, "r", encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.reader(f, delimiter=delimiter)
            rows = list(reader)
    except Exception as e:
        console.print(f"[red]Error reading {file}: {e}[/red]")
        raise SystemExit(1)

    if not rows:
        return

    headers = rows[0]
    if col_name in headers:
        col_idx = headers.index(col_name)
    else:
        try:
            col_idx = int(col_name) - 1
        except ValueError:
            console.print(f"[red]Column not found: {col_name}[/red]")
            raise SystemExit(1)

    writer = csv.writer(sys.stdout)
    writer.writerow(headers)
    for row in rows[1:]:
        if col_idx < len(row):
            if _evaluate_condition(row[col_idx], op, operand):
                writer.writerow(row)


@csv_cmd.command("select")
@click.argument("columns")
@click.argument("file")
@click.option("-d", "--delimiter", default=",", help="Field separator (default: ',')")
def csv_select(columns, file, delimiter):
    """Keep only specified columns (comma-separated names or 1-indexed numbers)."""
    try:
        with open(file, "r", encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.reader(f, delimiter=delimiter)
            rows = list(reader)
    except Exception as e:
        console.print(f"[red]Error reading {file}: {e}[/red]")
        raise SystemExit(1)

    if not rows:
        return

    headers = rows[0]
    col_specs = [c.strip() for c in columns.split(",")]
    col_indices = []
    for spec in col_specs:
        if spec in headers:
            col_indices.append(headers.index(spec))
        else:
            try:
                col_indices.append(int(spec) - 1)
            except ValueError:
                console.print(f"[red]Unknown column: {spec}[/red]", err=True)

    writer = csv.writer(sys.stdout)
    for row in rows:
        writer.writerow([row[i] if 0 <= i < len(row) else "" for i in col_indices])


@csv_cmd.command("to-json")
@click.argument("file")
@click.option("-d", "--delimiter", default=",", help="Field separator (default: ',')")
def csv_to_json(file, delimiter):
    """Convert CSV to JSON array."""
    try:
        with open(file, "r", encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            rows = list(reader)
    except Exception as e:
        console.print(f"[red]Error reading {file}: {e}[/red]")
        raise SystemExit(1)

    sys.stdout.write(json.dumps(rows, indent=2) + "\n")


# ---------------------------------------------------------------------------
# env group
# ---------------------------------------------------------------------------

def _parse_env_file(path):
    """Parse a .env file and return dict of KEY: VALUE."""
    result = {}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    result[key] = value
    except Exception as e:
        console.print(f"[red]Error reading {path}: {e}[/red]")
    return result


@click.group("env")
def env_cmd():
    """Env file utilities: show, diff, check."""
    pass


@env_cmd.command("show")
@click.argument("file", default=".env")
def env_show(file):
    """Pretty-print .env file as a table."""
    data = _parse_env_file(file)
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
    data1 = _parse_env_file(file1)
    data2 = _parse_env_file(file2)

    all_keys = sorted(set(data1) | set(data2))
    found_diff = False
    for key in all_keys:
        if key not in data1:
            console.print(f"[green]+ {key}={data2[key]}[/green]")
            found_diff = True
        elif key not in data2:
            console.print(f"[red]- {key}={data1[key]}[/red]")
            found_diff = True
        elif data1[key] != data2[key]:
            console.print(f"[yellow]~ {key}: {data1[key]!r} → {data2[key]!r}[/yellow]")
            found_diff = True

    if not found_diff:
        console.print("[dim]No differences.[/dim]")


@env_cmd.command("check")
@click.argument("template")
@click.argument("file")
def env_check(template, file):
    """Check that all keys in template exist in file."""
    template_keys = _parse_env_file(template)
    file_keys = _parse_env_file(file)

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

    def replace_var(m):
        key = m.group(1).strip()
        return substitutions.get(key, m.group(0))

    result = re.sub(r'\{\{(\w+)\}\}', replace_var, text)

    if in_place:
        with open(file, "w", encoding="utf-8") as f:
            f.write(result)
    else:
        sys.stdout.write(result)
