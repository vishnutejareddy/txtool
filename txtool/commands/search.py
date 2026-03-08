import click
from rich.console import Console
from rich.text import Text

from txtool.core.search import search as core_search
from txtool.utils import resolve_files, compile_pattern

console = Console()


@click.command("search")
@click.argument("pattern")
@click.argument("files", nargs=-1, required=True)
@click.option("--regex/--no-regex", default=True, help="Treat pattern as regex (default: on)")
@click.option("-i", "--ignore-case", is_flag=True, help="Case-insensitive matching")
@click.option("-n", "--line-numbers", is_flag=True, help="Show line numbers")
@click.option("--color/--no-color", default=True, help="Colorize output")
def search(pattern, files, regex, ignore_case, line_numbers, color):
    """Search for PATTERN in FILES."""
    paths = resolve_files(list(files))

    if not paths:
        console.print("[yellow]No files found.[/yellow]")
        raise SystemExit(1)

    compiled = compile_pattern(pattern, regex, ignore_case)
    results = core_search(pattern, paths, regex, ignore_case)

    if not results:
        raise SystemExit(1)

    for r in results:
        if color:
            _print_colored_match(r["file"], r["line_number"], r["line"], compiled, line_numbers)
        else:
            prefix = f"{r['file']}:{r['line_number']}: " if line_numbers else f"{r['file']}: "
            click.echo(prefix + r["line"])


def _print_colored_match(filename, lineno, line, compiled, show_lineno):
    text = Text()
    text.append(filename, style="bold cyan")
    text.append(":")
    if show_lineno:
        text.append(str(lineno), style="bold green")
        text.append(":")
    text.append(" ")

    last = 0
    for m in compiled.finditer(line):
        text.append(line[last:m.start()])
        text.append(m.group(), style="bold red on yellow")
        last = m.end()
    text.append(line[last:])
    console.print(text)
