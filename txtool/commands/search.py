import click
from rich.console import Console
from rich.text import Text

from txtool.utils import resolve_files, compile_pattern, read_lines

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
    compiled = compile_pattern(pattern, regex, ignore_case)
    paths = resolve_files(list(files))

    if not paths:
        console.print("[yellow]No files found.[/yellow]")
        raise SystemExit(1)

    found_any = False
    for path in paths:
        try:
            lines = read_lines(path)
        except Exception as e:
            console.print(f"[red]Error reading {path}: {e}[/red]")
            continue

        for lineno, line in enumerate(lines, 1):
            stripped = line.rstrip("\n")
            if compiled.search(stripped):
                found_any = True
                if color:
                    _print_colored_match(str(path), lineno, stripped, compiled, line_numbers)
                else:
                    prefix = f"{path}:{lineno}: " if line_numbers else f"{path}: "
                    click.echo(prefix + stripped)

    if not found_any:
        raise SystemExit(1)


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
