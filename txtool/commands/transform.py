import sys
import click

from txtool.core.transform import (
    fmt_text, convert_case, sort_lines, dedup_lines, truncate_lines
)
from txtool.utils import resolve_files, read_lines


def _write_output(content, path, in_place):
    if in_place:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        sys.stdout.write(content)


# ---------------------------------------------------------------------------
# fmt
# ---------------------------------------------------------------------------

@click.command("fmt")
@click.argument("files", nargs=-1, required=True)
@click.option("--trim", is_flag=True, help="Trim trailing whitespace from each line")
@click.option("--line-endings", type=click.Choice(["lf", "crlf", "cr"]), default=None, help="Normalize line endings")
@click.option("--wrap", "wrap_width", type=int, default=None, help="Wrap lines at N characters")
@click.option("--indent", "indent_width", type=int, default=None, help="Add N spaces indent to each line")
@click.option("--dedent", "do_dedent", is_flag=True, help="Remove common leading whitespace")
@click.option("--in-place", is_flag=True, help="Write back to file instead of stdout")
def fmt(files, trim, line_endings, wrap_width, indent_width, do_dedent, in_place):
    """Format text files: trim, wrap, indent, line endings."""
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

        text = fmt_text("".join(lines), trim=trim, line_endings=line_endings,
                        wrap=wrap_width, indent=indent_width, dedent=do_dedent)
        _write_output(text, path, in_place)


# ---------------------------------------------------------------------------
# case
# ---------------------------------------------------------------------------

@click.command("case")
@click.argument("style", type=click.Choice(["snake", "camel", "pascal", "kebab", "upper", "lower", "title"]))
@click.argument("files", nargs=-1, required=True)
@click.option("--in-place", is_flag=True, help="Write back to file instead of stdout")
def case_cmd(style, files, in_place):
    """Convert text case: snake, camel, pascal, kebab, upper, lower, title."""
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

        text = convert_case("".join(lines), style)
        _write_output(text, path, in_place)


# ---------------------------------------------------------------------------
# sort
# ---------------------------------------------------------------------------

@click.command("sort")
@click.argument("files", nargs=-1, required=True)
@click.option("-n", "--numeric", is_flag=True, help="Sort by numeric value found in line")
@click.option("--by-length", is_flag=True, help="Sort by line length")
@click.option("-r", "--reverse", is_flag=True, help="Reverse order")
@click.option("-u", "--unique", is_flag=True, help="Deduplicate after sorting")
@click.option("--in-place", is_flag=True, help="Write back to file instead of stdout")
def sort_cmd(files, numeric, by_length, reverse, unique, in_place):
    """Sort lines in files."""
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

        text = sort_lines("".join(lines), numeric=numeric, by_length=by_length,
                          reverse=reverse, unique=unique)
        _write_output(text, path, in_place)


# ---------------------------------------------------------------------------
# dedup
# ---------------------------------------------------------------------------

@click.command("dedup")
@click.argument("files", nargs=-1, required=True)
@click.option("--in-place", is_flag=True, help="Write back to file instead of stdout")
def dedup(files, in_place):
    """Remove duplicate lines, preserving insertion order."""
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

        text = dedup_lines("".join(lines))
        _write_output(text, path, in_place)


# ---------------------------------------------------------------------------
# truncate
# ---------------------------------------------------------------------------

@click.command("truncate")
@click.argument("files", nargs=-1, required=True)
@click.option("--head", "head_n", type=int, default=None, help="Keep first N lines")
@click.option("--tail", "tail_n", type=int, default=None, help="Keep last N lines")
def truncate(files, head_n, tail_n):
    """Keep first/last N lines of files."""
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

        text = truncate_lines("".join(lines), head=head_n, tail=tail_n)
        sys.stdout.write(text)
