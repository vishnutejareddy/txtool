import re
import sys
import textwrap

import click

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

        text = "".join(lines)

        if do_dedent:
            text = textwrap.dedent(text)

        lines = text.splitlines(keepends=True)

        if trim:
            new_trim = []
            for l in lines:
                content = l.rstrip("\n")
                newline = l[len(content):]
                new_trim.append(content.rstrip(" \t") + newline)
            lines = new_trim

        if wrap_width is not None:
            new_lines = []
            for line in lines:
                stripped = line.rstrip("\n")
                wrapped = textwrap.fill(stripped, width=wrap_width)
                new_lines.append(wrapped + "\n")
            lines = new_lines

        if indent_width is not None:
            prefix = " " * indent_width
            lines = [prefix + l for l in lines]

        text = "".join(lines)

        if line_endings == "lf":
            text = text.replace("\r\n", "\n").replace("\r", "\n")
        elif line_endings == "crlf":
            text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")
        elif line_endings == "cr":
            text = text.replace("\r\n", "\n").replace("\n", "\r")

        _write_output(text, path, in_place)


# ---------------------------------------------------------------------------
# case
# ---------------------------------------------------------------------------

def _split_token(token):
    """Split a token into words, handling camelCase, snake_case, kebab-case."""
    # Insert space before uppercase letter following a lowercase letter (camelCase)
    token = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', token)
    # Split on _ and -
    words = re.split(r'[_\-\s]+', token)
    return [w for w in words if w]


def _to_snake(token):
    words = _split_token(token)
    return "_".join(w.lower() for w in words)


def _to_camel(token):
    words = _split_token(token)
    if not words:
        return token
    return words[0].lower() + "".join(w.capitalize() for w in words[1:])


def _to_pascal(token):
    words = _split_token(token)
    return "".join(w.capitalize() for w in words)


def _to_kebab(token):
    words = _split_token(token)
    return "-".join(w.lower() for w in words)


CASE_CONVERTERS = {
    "snake": _to_snake,
    "camel": _to_camel,
    "pascal": _to_pascal,
    "kebab": _to_kebab,
}

TOKEN_RE = re.compile(r'[a-zA-Z][a-zA-Z0-9_-]*')


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

        out_lines = []
        for line in lines:
            content = line.rstrip("\n")
            newline = line[len(content):]

            if style == "upper":
                out_lines.append(content.upper() + newline)
            elif style == "lower":
                out_lines.append(content.lower() + newline)
            elif style == "title":
                out_lines.append(content.title() + newline)
            else:
                converter = CASE_CONVERTERS[style]
                converted = TOKEN_RE.sub(lambda m: converter(m.group()), content)
                out_lines.append(converted + newline)

        text = "".join(out_lines)
        _write_output(text, path, in_place)


# ---------------------------------------------------------------------------
# sort
# ---------------------------------------------------------------------------

def _numeric_key(line):
    m = re.search(r'-?\d+(?:\.\d+)?', line)
    if m:
        try:
            return float(m.group())
        except ValueError:
            pass
    return 0.0


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

        stripped = [l.rstrip("\n") for l in lines]

        if numeric:
            stripped.sort(key=_numeric_key, reverse=reverse)
        elif by_length:
            stripped.sort(key=len, reverse=reverse)
        else:
            stripped.sort(reverse=reverse)

        if unique:
            seen = set()
            deduped = []
            for l in stripped:
                if l not in seen:
                    seen.add(l)
                    deduped.append(l)
            stripped = deduped

        text = "\n".join(stripped) + ("\n" if stripped else "")
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

        seen = set()
        out_lines = []
        for line in lines:
            key = line.rstrip("\n")
            if key not in seen:
                seen.add(key)
                out_lines.append(line)

        text = "".join(out_lines)
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

        if head_n is not None:
            lines = lines[:head_n]
        elif tail_n is not None:
            lines = lines[-tail_n:] if tail_n > 0 else []

        sys.stdout.write("".join(lines))
