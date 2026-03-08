import re
import sys

import click

from txtool.utils import resolve_files, read_lines


PATTERNS = {
    "email": re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
    "url": re.compile(r'https?://[^\s<>"()]+'),
    "ip": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
    "date": re.compile(r'\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b'),
    "phone": re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
    "number": re.compile(r'\b-?\d+(?:\.\d+)?\b'),
}

ALL_TYPES = list(PATTERNS.keys())


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

    seen = set()
    for path in paths:
        try:
            lines = read_lines(path)
        except Exception as e:
            click.echo(f"Error reading {path}: {e}", err=True)
            continue

        text = "".join(lines)
        for t in active_types:
            for m in PATTERNS[t].finditer(text):
                val = m.group()
                if do_unique:
                    key = (t, val)
                    if key in seen:
                        continue
                    seen.add(key)
                if multi:
                    sys.stdout.write(f"{t}: {val}\n")
                else:
                    sys.stdout.write(val + "\n")


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

    if use_regex:
        start_re = re.compile(start)
        end_re = re.compile(end)
    else:
        start_re = re.compile(re.escape(start))
        end_re = re.compile(re.escape(end))

    for path in paths:
        try:
            lines = read_lines(path)
        except Exception as e:
            click.echo(f"Error reading {path}: {e}", err=True)
            continue

        inside = False
        for line in lines:
            stripped = line.rstrip("\n")
            if not inside:
                if start_re.search(stripped):
                    inside = True
                    if inclusive:
                        sys.stdout.write(line)
            else:
                if end_re.search(stripped):
                    inside = False
                    if inclusive:
                        sys.stdout.write(line)
                else:
                    sys.stdout.write(line)


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

        if not lines:
            continue

        header_row = None
        if header:
            header_line = lines[0].rstrip("\n")
            if delimiter:
                header_row = header_line.split(delimiter)
            else:
                header_row = header_line.split()
            data_lines = lines[1:]
        else:
            data_lines = lines

        # Parse field indices
        field_indices = None
        if fields:
            field_specs = [f.strip() for f in fields.split(",")]
            field_indices = []
            for spec in field_specs:
                if header_row and spec in header_row:
                    field_indices.append(header_row.index(spec))
                else:
                    try:
                        field_indices.append(int(spec) - 1)
                    except ValueError:
                        click.echo(f"Unknown field: {spec}", err=True)
                        continue

        if header and field_indices is not None:
            selected_headers = [header_row[i] for i in field_indices if 0 <= i < len(header_row)]
            sep = delimiter if delimiter else "\t"
            sys.stdout.write(sep.join(selected_headers) + "\n")

        for line in data_lines:
            stripped = line.rstrip("\n")
            if delimiter:
                parts = stripped.split(delimiter)
            else:
                parts = stripped.split()

            if field_indices is not None:
                selected = [parts[i] if 0 <= i < len(parts) else "" for i in field_indices]
            else:
                selected = parts

            sep = delimiter if delimiter else "\t"
            sys.stdout.write(sep.join(selected) + "\n")
