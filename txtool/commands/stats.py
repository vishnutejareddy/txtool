import json
import click
from rich.console import Console
from rich.table import Table

from txtool.core.stats import compute_stats
from txtool.utils import resolve_files

console = Console()


@click.command("stats")
@click.argument("files", nargs=-1, required=True)
@click.option("--top", default=10, show_default=True, help="Number of top words to show")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["table", "json", "plain"]),
    default="table",
    show_default=True,
    help="Output format",
)
def stats(files, top, fmt):
    """Show statistics for FILES."""
    paths = resolve_files(list(files))

    if not paths:
        console.print("[yellow]No files found.[/yellow]")
        return

    results = compute_stats(paths, top)

    if fmt == "json":
        output = []
        for r in results:
            output.append({
                "file": r["file"],
                "lines": r["lines"],
                "words": r["words"],
                "chars": r["chars"],
                "top_words": [{"word": w, "count": c} for w, c in r["top_words"]],
            })
        click.echo(json.dumps(output, indent=2))

    elif fmt == "plain":
        for r in results:
            click.echo(f"File: {r['file']}")
            click.echo(f"  Lines: {r['lines']}")
            click.echo(f"  Words: {r['words']}")
            click.echo(f"  Chars: {r['chars']}")
            click.echo(f"  Top {top} words:")
            for word, count in r["top_words"]:
                click.echo(f"    {word}: {count}")
            click.echo()

    else:  # table
        for r in results:
            console.print(f"\n[bold cyan]{r['file']}[/bold cyan]")

            summary = Table(show_header=True, header_style="bold magenta")
            summary.add_column("Metric")
            summary.add_column("Value", justify="right")
            summary.add_row("Lines", str(r["lines"]))
            summary.add_row("Words", str(r["words"]))
            summary.add_row("Chars", str(r["chars"]))
            console.print(summary)

            if r["top_words"]:
                word_table = Table(show_header=True, header_style="bold blue", title=f"Top {top} Words")
                word_table.add_column("Word")
                word_table.add_column("Count", justify="right")
                for word, count in r["top_words"]:
                    word_table.add_row(word, str(count))
                console.print(word_table)
