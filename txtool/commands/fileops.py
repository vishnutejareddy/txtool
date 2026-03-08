import sys
import click
from rich.console import Console
from rich.text import Text

from txtool.core.fileops import diff_files as core_diff, set_operations, concat_files

console = Console()


# ---------------------------------------------------------------------------
# diff
# ---------------------------------------------------------------------------

@click.command("diff")
@click.argument("file1")
@click.argument("file2")
@click.option("--word", "diff_level", flag_value="word", help="Word-level diff")
@click.option("--char", "diff_level", flag_value="char", help="Char-level diff")
def diff_cmd(file1, file2, diff_level):
    """Show diff between two files."""
    try:
        result = core_diff(file1, file2, level=diff_level or "line")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise SystemExit(1)

    if not result:
        console.print("[dim]No differences.[/dim]")
        return

    for line in result.splitlines():
        if line.startswith("---") or line.startswith("+++"):
            console.print(Text(line, style="bold"))
        elif line.startswith("@@"):
            console.print(Text(line, style="cyan"))
        elif line.startswith("- ") or line.startswith("-"):
            console.print(Text(line, style="red"))
        elif line.startswith("+ ") or line.startswith("+"):
            console.print(Text(line, style="green"))
        else:
            console.print(Text(line, style="dim"))


# ---------------------------------------------------------------------------
# unique
# ---------------------------------------------------------------------------

@click.command("unique")
@click.argument("file1")
@click.argument("file2")
@click.option("--only-in-a", "mode", flag_value="only_a", help="Lines in file1 but not file2")
@click.option("--only-in-b", "mode", flag_value="only_b", help="Lines in file2 but not file1")
@click.option("--common", "mode", flag_value="common", help="Lines in both files")
def unique_cmd(file1, file2, mode):
    """Set operations on lines of two files."""
    try:
        ops = set_operations(file1, file2)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise SystemExit(1)

    if mode == "only_a":
        for l in ops["only_a"]:
            sys.stdout.write(l + "\n")
    elif mode == "only_b":
        for l in ops["only_b"]:
            sys.stdout.write(l + "\n")
    elif mode == "common":
        for l in ops["common"]:
            sys.stdout.write(l + "\n")
    else:
        if ops["only_a"]:
            console.print(f"[bold]Only in {file1}:[/bold]")
            for l in ops["only_a"]:
                console.print(f"  [red]{l}[/red]")
        if ops["only_b"]:
            console.print(f"[bold]Only in {file2}:[/bold]")
            for l in ops["only_b"]:
                console.print(f"  [green]{l}[/green]")
        if ops["common"]:
            console.print("[bold]Common:[/bold]")
            for l in ops["common"]:
                console.print(f"  [dim]{l}[/dim]")


# ---------------------------------------------------------------------------
# concat
# ---------------------------------------------------------------------------

@click.command("concat")
@click.argument("files", nargs=-1, required=True)
@click.option("--separator", default="", help="Text to print between files")
@click.option("--with-headers", is_flag=True, help="Print === filename === before each file")
def concat(files, separator, with_headers):
    """Concatenate files to stdout."""
    from txtool.utils import resolve_files
    paths = resolve_files(list(files))
    if not paths:
        click.echo("No files found.", err=True)
        raise SystemExit(1)

    try:
        result = concat_files(paths, separator=separator, with_headers=with_headers)
        sys.stdout.write(result)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
