import sys
import click
from rich.console import Console

from txtool.utils import resolve_files, compile_pattern, read_lines

console = Console()


@click.command("replace")
@click.argument("pattern")
@click.argument("replacement")
@click.argument("files", nargs=-1, required=True)
@click.option("--regex/--no-regex", default=True, help="Treat pattern as regex (default: on)")
@click.option("-i", "--ignore-case", is_flag=True, help="Case-insensitive matching")
@click.option("--in-place", is_flag=True, help="Edit files in place")
@click.option("--dry-run", is_flag=True, help="Show what would change without writing")
def replace(pattern, replacement, files, regex, ignore_case, in_place, dry_run):
    """Replace PATTERN with REPLACEMENT in FILES."""
    compiled = compile_pattern(pattern, regex, ignore_case)
    paths = resolve_files(list(files))

    if not paths:
        console.print("[yellow]No files found.[/yellow]")
        return

    for path in paths:
        try:
            lines = read_lines(path)
        except Exception as e:
            console.print(f"[red]Error reading {path}: {e}[/red]")
            continue

        new_lines = [compiled.sub(replacement, line) for line in lines]
        changed = new_lines != lines

        if dry_run:
            if changed:
                console.print(f"[bold cyan]{path}[/bold cyan] [yellow](would change)[/yellow]")
                _print_diff(lines, new_lines)
            else:
                console.print(f"[bold cyan]{path}[/bold cyan] [dim](no changes)[/dim]")
        elif in_place:
            if changed:
                with open(path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                console.print(f"[bold cyan]{path}[/bold cyan] [green]updated[/green]")
            else:
                console.print(f"[bold cyan]{path}[/bold cyan] [dim](no changes)[/dim]")
        else:
            sys.stdout.writelines(new_lines)


def _print_diff(old_lines, new_lines):
    for old, new in zip(old_lines, new_lines):
        if old != new:
            console.print(f"  [red]- {old.rstrip()}[/red]")
            console.print(f"  [green]+ {new.rstrip()}[/green]")
