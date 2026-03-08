import sys
import click
from rich.console import Console

from txtool.core.replace import replace as core_replace, apply_replace
from txtool.utils import resolve_files

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
    paths = resolve_files(list(files))

    if not paths:
        console.print("[yellow]No files found.[/yellow]")
        return

    results = core_replace(pattern, replacement, paths, regex, ignore_case)

    for r in results:
        if dry_run:
            if r["changed"]:
                console.print(f"[bold cyan]{r['file']}[/bold cyan] [yellow](would change)[/yellow]")
                _print_diff(r["old_lines"], r["new_lines"])
            else:
                console.print(f"[bold cyan]{r['file']}[/bold cyan] [dim](no changes)[/dim]")
        elif in_place:
            if r["changed"]:
                apply_replace(r)
                console.print(f"[bold cyan]{r['file']}[/bold cyan] [green]updated[/green]")
            else:
                console.print(f"[bold cyan]{r['file']}[/bold cyan] [dim](no changes)[/dim]")
        else:
            sys.stdout.writelines(r["new_lines"])


def _print_diff(old_lines, new_lines):
    for old, new in zip(old_lines, new_lines):
        if old != new:
            console.print(f"  [red]- {old.rstrip()}[/red]")
            console.print(f"  [green]+ {new.rstrip()}[/green]")
