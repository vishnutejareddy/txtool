import json
import re
import sys
import time

import click
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text

from txtool.core.logtools import (
    tail_lines as core_tail,
    parse_log_levels,
    normalize_timestamps,
    LOG_LEVEL_RE,
    LEVEL_STYLES,
)
from txtool.utils import resolve_files, read_lines

console = Console()


# ---------------------------------------------------------------------------
# tail
# ---------------------------------------------------------------------------

def _style_for_line(line):
    m = LOG_LEVEL_RE.search(line)
    if m:
        return LEVEL_STYLES.get(m.group(1), "")
    return ""


@click.command("tail")
@click.argument("file")
@click.option("-n", "--lines", "n_lines", type=int, default=10, help="Number of last lines to show")
@click.option("-f", "--follow", is_flag=True, help="Follow file, printing new lines as added")
@click.option("--filter", "filter_pattern", default=None, help="Only show lines matching pattern")
@click.option("--highlight", "highlight_pattern", default=None, help="Highlight matching text in lines")
def tail_cmd(file, n_lines, follow, filter_pattern, highlight_pattern):
    """Show last N lines of a file, optionally following it."""
    filter_re = re.compile(filter_pattern) if filter_pattern else None
    highlight_re = re.compile(highlight_pattern) if highlight_pattern else None

    def print_line(line):
        stripped = line.rstrip("\n") if isinstance(line, str) and line.endswith("\n") else line
        if filter_re and not filter_re.search(stripped):
            return
        style = _style_for_line(stripped)
        if highlight_re:
            text = Text()
            last = 0
            for m in highlight_re.finditer(stripped):
                text.append(stripped[last:m.start()], style=style)
                text.append(m.group(), style="bold yellow on black")
                last = m.end()
            text.append(stripped[last:], style=style)
            console.print(text)
        else:
            console.print(Text(stripped, style=style))

    try:
        lines = core_tail(file, n_lines)
    except Exception as e:
        console.print(f"[red]Error reading {file}: {e}[/red]")
        raise SystemExit(1)

    for line in lines:
        print_line(line)

    if follow:
        try:
            with open(file, "r", encoding="utf-8", errors="replace") as f:
                f.seek(0, 2)
                while True:
                    line = f.readline()
                    if line:
                        print_line(line)
                    else:
                        time.sleep(0.1)
        except KeyboardInterrupt:
            pass


# ---------------------------------------------------------------------------
# parse-log
# ---------------------------------------------------------------------------

@click.command("parse-log")
@click.argument("files", nargs=-1, required=True)
@click.option("--format", "output_format", type=click.Choice(["table", "json"]), default="table")
def parse_log(files, output_format):
    """Parse log files and show level counts and top errors."""
    paths = resolve_files(list(files))
    if not paths:
        click.echo("No files found.", err=True)
        raise SystemExit(1)

    results = parse_log_levels(paths)

    if output_format == "json":
        output = []
        for r in results:
            output.append({
                "file": r["file"],
                "total": r["total"],
                "levels": r["counts"],
                "top_errors": [{"message": msg, "count": 1} for msg in r["top_errors"]],
            })
        sys.stdout.write(json.dumps(output, indent=2) + "\n")
    else:
        for r in results:
            console.print(f"\n[bold cyan]{r['file']}[/bold cyan]")
            t = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
            t.add_column("Metric")
            t.add_column("Value")
            t.add_row("Total lines", str(r["total"]))
            for level, count in sorted(r["counts"].items()):
                style = LEVEL_STYLES.get(level, "")
                t.add_row(f"[{style}]{level}[/{style}]" if style else level, str(count))
            console.print(t)

            if r["top_errors"]:
                console.print("[bold]Top errors:[/bold]")
                for msg in r["top_errors"]:
                    console.print(f"  [red]{msg}[/red]")


# ---------------------------------------------------------------------------
# timestamp
# ---------------------------------------------------------------------------

@click.command("timestamp")
@click.argument("files", nargs=-1, required=True)
@click.option("--to-format", "to_fmt", default="%Y-%m-%d %H:%M:%S", help="Output datetime format")
@click.option("--in-place", is_flag=True, help="Write back to file instead of stdout")
def timestamp_cmd(files, to_fmt, in_place):
    """Normalize timestamps in log files."""
    paths = resolve_files(list(files))
    if not paths:
        click.echo("No files found.", err=True)
        raise SystemExit(1)

    for path in paths:
        try:
            lines = read_lines(path)
        except Exception as e:
            click.echo(f"Error reading {path}: {e}", err=True)
            continue

        text = normalize_timestamps("".join(lines), to_format=to_fmt)
        if in_place:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
        else:
            sys.stdout.write(text)
