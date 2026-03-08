import sys
import click
from rich.console import Console

from txtool.core.filter import filter_lines as core_filter
from txtool.utils import resolve_files

console = Console()


@click.command("filter")
@click.argument("pattern")
@click.argument("files", nargs=-1, required=True)
@click.option("-v", "--invert", is_flag=True, help="Exclude matching lines (keep non-matching)")
@click.option("--regex/--no-regex", default=True, help="Treat pattern as regex (default: on)")
@click.option("-i", "--ignore-case", is_flag=True, help="Case-insensitive matching")
def filter_cmd(pattern, files, invert, regex, ignore_case):
    """Filter lines matching PATTERN in FILES."""
    paths = resolve_files(list(files))

    if not paths:
        console.print("[yellow]No files found.[/yellow]")
        return

    results = core_filter(pattern, paths, invert, regex, ignore_case)
    for r in results:
        for line in r["lines"]:
            sys.stdout.write(line + "\n")
