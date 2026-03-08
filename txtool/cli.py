import click
from rich.console import Console
from rich.table import Table
from rich import box

from txtool.commands.search import search
from txtool.commands.replace import replace
from txtool.commands.filter import filter_cmd
from txtool.commands.stats import stats

console = Console()


@click.group()
def cli():
    """txtool — a text processing CLI for search, replace, filter, and stats."""
    pass


@cli.command("help")
def help_cmd():
    """Show detailed usage guide for all commands."""
    console.print("\n[bold cyan]txtool[/bold cyan] — text processing CLI\n")

    commands = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    commands.add_column("Command", style="bold yellow")
    commands.add_column("Usage")
    commands.add_column("Description")
    commands.add_row("search",  "txtool search <pattern> <files...>",              "Grep-style search across files")
    commands.add_row("replace", "txtool replace <pattern> <replacement> <files...>", "Find and replace in files")
    commands.add_row("filter",  "txtool filter <pattern> <files...>",              "Keep or remove matching lines")
    commands.add_row("stats",   "txtool stats <files...>",                         "Line/word/char counts + top words")
    console.print(commands)

    console.print("\n[bold]Common flags (all commands)[/bold]")
    flags = Table(box=box.SIMPLE, show_header=False)
    flags.add_column("Flag", style="green")
    flags.add_column("Description")
    flags.add_row("--regex / --no-regex", "Regex mode (default: on)")
    flags.add_row("-i, --ignore-case",    "Case-insensitive matching")
    console.print(flags)

    console.print("[bold]search flags[/bold]")
    s = Table(box=box.SIMPLE, show_header=False)
    s.add_column("Flag", style="green")
    s.add_column("Description")
    s.add_row("-n, --line-numbers",  "Show line numbers in output")
    s.add_row("--color / --no-color", "Colorize matched text")
    console.print(s)

    console.print("[bold]replace flags[/bold]")
    r = Table(box=box.SIMPLE, show_header=False)
    r.add_column("Flag", style="green")
    r.add_column("Description")
    r.add_row("--in-place", "Write changes back to file")
    r.add_row("--dry-run",  "Preview changes without writing")
    console.print(r)

    console.print("[bold]filter flags[/bold]")
    f = Table(box=box.SIMPLE, show_header=False)
    f.add_column("Flag", style="green")
    f.add_column("Description")
    f.add_row("-v, --invert", "Exclude matching lines instead")
    console.print(f)

    console.print("[bold]stats flags[/bold]")
    st = Table(box=box.SIMPLE, show_header=False)
    st.add_column("Flag", style="green")
    st.add_column("Description")
    st.add_row("--top N",    "Number of top words (default: 10)")
    st.add_row("--format",   "Output format: table | json | plain")
    console.print(st)

    console.print("[bold]Examples[/bold]")
    examples = [
        ("txtool search \"TODO\" \"**/*.py\" -n",          "Find TODOs with line numbers"),
        ("txtool replace \"foo\" \"bar\" *.txt --dry-run", "Preview replacements"),
        ("txtool filter -v \"DEBUG\" app.log",             "Remove DEBUG lines"),
        ("txtool stats *.txt --format table",              "Stats with rich table"),
    ]
    ex = Table(box=box.SIMPLE, show_header=False)
    ex.add_column("Command", style="cyan")
    ex.add_column("Description")
    for cmd, desc in examples:
        ex.add_row(cmd, desc)
    console.print(ex)

    console.print("Run [cyan]txtool <command> --help[/cyan] for full options on any command.\n")


cli.add_command(search)
cli.add_command(replace)
cli.add_command(filter_cmd, name="filter")
cli.add_command(stats)


if __name__ == "__main__":
    cli()
