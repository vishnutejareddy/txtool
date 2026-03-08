import click

from txtool.commands.search import search
from txtool.commands.replace import replace
from txtool.commands.filter import filter_cmd
from txtool.commands.stats import stats


@click.group()
def cli():
    """txtool — a text processing CLI for search, replace, filter, and stats."""
    pass


cli.add_command(search)
cli.add_command(replace)
cli.add_command(filter_cmd, name="filter")
cli.add_command(stats)


if __name__ == "__main__":
    cli()
