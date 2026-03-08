import sys
import click

from txtool.core.extract import extract_patterns, extract_between, extract_columns, ALL_TYPES
from txtool.utils import resolve_files, read_lines


# ---------------------------------------------------------------------------
# extract
# ---------------------------------------------------------------------------

@click.command("extract")
@click.argument("files", nargs=-1, required=True)
@click.option("--type", "types", multiple=True, type=click.Choice(ALL_TYPES), help="Type(s) to extract")
@click.option("--unique", "do_unique", is_flag=True, help="Deduplicate results")
def extract(files, types, do_unique):
    """Extract emails, URLs, IPs, dates, phone numbers, or numbers from files."""
    paths = resolve_files(list(files))
    if not paths:
        click.echo("No files found.", err=True)
        raise SystemExit(1)

    active_types = list(types) if types else ALL_TYPES
    multi = len(active_types) > 1

    for path in paths:
        try:
            lines = read_lines(path)
        except Exception as e:
            click.echo(f"Error reading {path}: {e}", err=True)
            continue

        text = "".join(lines)
        results = extract_patterns(text, types=active_types, unique=do_unique)
        for r in results:
            if multi:
                sys.stdout.write(f"{r['type']}: {r['value']}\n")
            else:
                sys.stdout.write(r["value"] + "\n")


# ---------------------------------------------------------------------------
# between
# ---------------------------------------------------------------------------

@click.command("between")
@click.argument("start")
@click.argument("end")
@click.argument("files", nargs=-1, required=True)
@click.option("--inclusive", is_flag=True, help="Include the delimiter lines")
@click.option("--regex", "use_regex", is_flag=True, help="Treat start/end as regex")
def between(start, end, files, inclusive, use_regex):
    """Extract lines between START and END pattern matches."""
    paths = resolve_files(list(files))
    if not paths:
        click.echo("No files found.", err=True)
        raise SystemExit(1)

    for path in paths:
        try:
            lines = read_lines(path)
        except Exception as e:
            click.echo(f"Error reading {path}: {e}", err=True)
            continue

        result = extract_between("".join(lines), start, end, inclusive=inclusive, regex=use_regex)
        sys.stdout.write(result)


# ---------------------------------------------------------------------------
# columns
# ---------------------------------------------------------------------------

@click.command("columns")
@click.argument("files", nargs=-1, required=True)
@click.option("-d", "--delimiter", default=None, help="Field separator (default: whitespace)")
@click.option("-f", "--fields", default=None, help="Comma-separated 1-indexed field numbers e.g. '1,3,5'")
@click.option("--header", is_flag=True, help="Treat first row as header, allow field names in --fields")
def columns(files, delimiter, fields, header):
    """Extract specific columns from delimited text."""
    paths = resolve_files(list(files))
    if not paths:
        click.echo("No files found.", err=True)
        raise SystemExit(1)

    for path in paths:
        try:
            lines = read_lines(path)
        except Exception as e:
            click.echo(f"Error reading {path}: {e}", err=True)
            continue

        result = extract_columns("".join(lines), fields, delimiter=delimiter, header=header)
        sys.stdout.write(result)
