import re
import sys
import time
import json
from collections import Counter
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text

from txtool.utils import resolve_files, read_lines

console = Console()

LOG_LEVEL_RE = re.compile(r'\b(DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL|FATAL)\b')

LEVEL_STYLES = {
    "DEBUG": "dim",
    "INFO": "green",
    "WARN": "yellow",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "red bold",
    "FATAL": "red bold",
}

TIMESTAMP_FORMATS = [
    ("%Y-%m-%dT%H:%M:%S", re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')),
    ("%Y-%m-%d %H:%M:%S", re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')),
    ("%d/%m/%Y %H:%M:%S", re.compile(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}')),
    ("%b %d %H:%M:%S", re.compile(r'[A-Z][a-z]{2}\s+\d{1,2} \d{2}:\d{2}:\d{2}')),
]


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
        stripped = line.rstrip("\n")
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
        lines = read_lines(file)
    except Exception as e:
        console.print(f"[red]Error reading {file}: {e}[/red]")
        raise SystemExit(1)

    for line in lines[-n_lines:]:
        print_line(line)

    if follow:
        try:
            with open(file, "r", encoding="utf-8", errors="replace") as f:
                f.seek(0, 2)  # seek to end
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

    results = []
    for path in paths:
        try:
            lines = read_lines(path)
        except Exception as e:
            click.echo(f"Error reading {path}: {e}", err=True)
            continue

        total = len(lines)
        level_counts = Counter()
        error_messages = []

        for line in lines:
            stripped = line.rstrip("\n")
            m = LOG_LEVEL_RE.search(stripped)
            if m:
                level = m.group(1).upper()
                if level == "WARNING":
                    level = "WARN"
                level_counts[level] += 1
                if level in ("ERROR", "CRITICAL", "FATAL"):
                    error_messages.append(stripped)

        top_errors = Counter(error_messages).most_common(5)
        results.append({
            "file": str(path),
            "total": total,
            "levels": dict(level_counts),
            "top_errors": [{"message": msg, "count": cnt} for msg, cnt in top_errors],
        })

    if output_format == "json":
        sys.stdout.write(json.dumps(results, indent=2) + "\n")
    else:
        for r in results:
            console.print(f"\n[bold cyan]{r['file']}[/bold cyan]")
            t = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
            t.add_column("Metric")
            t.add_column("Value")
            t.add_row("Total lines", str(r["total"]))
            for level, count in sorted(r["levels"].items()):
                style = LEVEL_STYLES.get(level, "")
                t.add_row(f"[{style}]{level}[/{style}]" if style else level, str(count))
            console.print(t)

            if r["top_errors"]:
                console.print("[bold]Top errors:[/bold]")
                for item in r["top_errors"]:
                    console.print(f"  ({item['count']}x) [red]{item['message']}[/red]")


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

        out_lines = []
        for line in lines:
            new_line = line
            for fmt, ts_re in TIMESTAMP_FORMATS:
                def replace_ts(m, fmt=fmt):
                    try:
                        dt = datetime.strptime(m.group(), fmt)
                        return dt.strftime(to_fmt)
                    except ValueError:
                        return m.group()
                new_line = ts_re.sub(replace_ts, new_line)
            out_lines.append(new_line)

        text = "".join(out_lines)
        if in_place:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
        else:
            sys.stdout.write(text)
