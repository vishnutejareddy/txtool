import difflib
import sys

import click
from rich.console import Console
from rich.text import Text

console = Console()


def _read_file_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.readlines()


# ---------------------------------------------------------------------------
# diff
# ---------------------------------------------------------------------------

def _word_or_char_diff(line_a, line_b, level="word"):
    """Return rich Text showing inline diff at word or char level."""
    if level == "word":
        a_parts = line_a.split()
        b_parts = line_b.split()
    else:
        a_parts = list(line_a)
        b_parts = list(line_b)

    sm = difflib.SequenceMatcher(None, a_parts, b_parts)
    result = Text()
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            sep = " " if level == "word" else ""
            result.append(sep.join(a_parts[i1:i2]), style="")
            if level == "word" and i2 < len(a_parts):
                result.append(" ")
        elif tag == "replace":
            sep = " " if level == "word" else ""
            result.append(sep.join(a_parts[i1:i2]), style="red strike")
            result.append(" ")
            result.append(sep.join(b_parts[j1:j2]), style="green")
            if level == "word" and j2 < len(b_parts):
                result.append(" ")
        elif tag == "delete":
            sep = " " if level == "word" else ""
            result.append(sep.join(a_parts[i1:i2]), style="red strike")
            if level == "word":
                result.append(" ")
        elif tag == "insert":
            sep = " " if level == "word" else ""
            result.append(sep.join(b_parts[j1:j2]), style="green")
            if level == "word":
                result.append(" ")
    return result


@click.command("diff")
@click.argument("file1")
@click.argument("file2")
@click.option("--word", "diff_level", flag_value="word", help="Word-level diff")
@click.option("--char", "diff_level", flag_value="char", help="Char-level diff")
def diff_cmd(file1, file2, diff_level):
    """Show diff between two files."""
    try:
        lines_a = _read_file_lines(file1)
    except Exception as e:
        console.print(f"[red]Error reading {file1}: {e}[/red]")
        raise SystemExit(1)
    try:
        lines_b = _read_file_lines(file2)
    except Exception as e:
        console.print(f"[red]Error reading {file2}: {e}[/red]")
        raise SystemExit(1)

    if diff_level in ("word", "char"):
        sm = difflib.SequenceMatcher(None, lines_a, lines_b)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                for line in lines_a[i1:i2]:
                    console.print(Text("  " + line.rstrip("\n"), style="dim"))
            elif tag == "replace":
                for la, lb in zip(lines_a[i1:i2], lines_b[j1:j2]):
                    t = Text("~ ")
                    t.append_text(_word_or_char_diff(la.rstrip("\n"), lb.rstrip("\n"), diff_level))
                    console.print(t)
                for la in lines_a[i1 + min(i2 - i1, j2 - j1):i2]:
                    console.print(Text("- " + la.rstrip("\n"), style="red"))
                for lb in lines_b[j1 + min(i2 - i1, j2 - j1):j2]:
                    console.print(Text("+ " + lb.rstrip("\n"), style="green"))
            elif tag == "delete":
                for la in lines_a[i1:i2]:
                    console.print(Text("- " + la.rstrip("\n"), style="red"))
            elif tag == "insert":
                for lb in lines_b[j1:j2]:
                    console.print(Text("+ " + lb.rstrip("\n"), style="green"))
    else:
        # unified diff
        diff = list(difflib.unified_diff(lines_a, lines_b, fromfile=file1, tofile=file2))
        if not diff:
            console.print("[dim]No differences.[/dim]")
            return
        for line in diff:
            line_stripped = line.rstrip("\n")
            if line_stripped.startswith("---") or line_stripped.startswith("+++"):
                console.print(Text(line_stripped, style="bold"))
            elif line_stripped.startswith("@@"):
                console.print(Text(line_stripped, style="cyan"))
            elif line_stripped.startswith("-"):
                console.print(Text(line_stripped, style="red"))
            elif line_stripped.startswith("+"):
                console.print(Text(line_stripped, style="green"))
            else:
                console.print(Text(line_stripped, style="dim"))


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
        lines_a = set(l.rstrip("\n") for l in _read_file_lines(file1))
    except Exception as e:
        console.print(f"[red]Error reading {file1}: {e}[/red]")
        raise SystemExit(1)
    try:
        lines_b = set(l.rstrip("\n") for l in _read_file_lines(file2))
    except Exception as e:
        console.print(f"[red]Error reading {file2}: {e}[/red]")
        raise SystemExit(1)

    only_a = sorted(lines_a - lines_b)
    only_b = sorted(lines_b - lines_a)
    common = sorted(lines_a & lines_b)

    if mode == "only_a":
        for l in only_a:
            sys.stdout.write(l + "\n")
    elif mode == "only_b":
        for l in only_b:
            sys.stdout.write(l + "\n")
    elif mode == "common":
        for l in common:
            sys.stdout.write(l + "\n")
    else:
        if only_a:
            console.print(f"[bold]Only in {file1}:[/bold]")
            for l in only_a:
                console.print(f"  [red]{l}[/red]")
        if only_b:
            console.print(f"[bold]Only in {file2}:[/bold]")
            for l in only_b:
                console.print(f"  [green]{l}[/green]")
        if common:
            console.print("[bold]Common:[/bold]")
            for l in common:
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
    from txtool.utils import resolve_files, read_lines
    paths = resolve_files(list(files))
    if not paths:
        click.echo("No files found.", err=True)
        raise SystemExit(1)

    for i, path in enumerate(paths):
        if i > 0 and separator:
            sys.stdout.write(separator + "\n")
        if with_headers:
            sys.stdout.write(f"=== {path} ===\n")
        try:
            lines = read_lines(path)
            sys.stdout.write("".join(lines))
        except Exception as e:
            click.echo(f"Error reading {path}: {e}", err=True)
