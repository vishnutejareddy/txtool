import sys
import click
from rich.console import Console

from txtool.utils import resolve_files, compile_pattern, read_lines

console = Console()


@click.command("filter")
@click.argument("pattern")
@click.argument("files", nargs=-1, required=True)
@click.option("-v", "--invert", is_flag=True, help="Exclude matching lines (keep non-matching)")
@click.option("--regex/--no-regex", default=True, help="Treat pattern as regex (default: on)")
@click.option("-i", "--ignore-case", is_flag=True, help="Case-insensitive matching")
def filter_cmd(pattern, files, invert, regex, ignore_case):
    """Filter lines matching PATTERN in FILES."""
    compiled = compile_pattern(pattern, regex, ignore_case)
    paths = resolve_files(list(files))

    if not paths:
        console.print("[yellow]No files found.[/yellow]")
        return

    for path in paths:
        try:
            lines = read_lines(path)
        except Exception as e:
            console.print(f"[red]Error reading {path}: {e}[/red]", file=sys.stderr)
            continue

        for line in lines:
            matched = bool(compiled.search(line.rstrip("\n")))
            keep = (not matched) if invert else matched
            if keep:
                sys.stdout.write(line)
