import base64
import hashlib
import html
import json
import subprocess
import sys
import urllib.parse

import click
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text

from txtool.utils import resolve_files, read_lines, compile_pattern

console = Console()


# ---------------------------------------------------------------------------
# encode
# ---------------------------------------------------------------------------

@click.command("encode")
@click.argument("method", type=click.Choice(["base64", "url", "html"]))
@click.argument("files", nargs=-1)
@click.option("--decode", is_flag=True, help="Decode instead of encode")
@click.option("--text", "text_input", default=None, help="Encode/decode text directly")
def encode_cmd(method, files, decode, text_input):
    """Encode or decode text using base64, URL, or HTML encoding."""
    def process(text):
        if method == "base64":
            if decode:
                return base64.b64decode(text.strip()).decode("utf-8", errors="replace")
            else:
                return base64.b64encode(text.encode("utf-8")).decode("ascii")
        elif method == "url":
            if decode:
                return urllib.parse.unquote(text)
            else:
                return urllib.parse.quote(text)
        elif method == "html":
            if decode:
                return html.unescape(text)
            else:
                return html.escape(text)

    if text_input is not None:
        result = process(text_input)
        sys.stdout.write(result + "\n")
        return

    if not files:
        # Read from stdin
        text = sys.stdin.read()
        result = process(text)
        sys.stdout.write(result + "\n")
        return

    paths = resolve_files(list(files))
    if not paths:
        click.echo("No files found.", err=True)
        raise SystemExit(1)

    for path in paths:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except Exception as e:
            click.echo(f"Error reading {path}: {e}", err=True)
            continue
        result = process(text)
        sys.stdout.write(result + "\n")


# ---------------------------------------------------------------------------
# hash
# ---------------------------------------------------------------------------

def _hash_file(path, algo):
    h = hashlib.new(algo)
    try:
        with open(path, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        console.print(f"[red]Error reading {path}: {e}[/red]")
        return None


@click.command("hash")
@click.argument("files", nargs=-1, required=True)
@click.option("--algo", type=click.Choice(["md5", "sha1", "sha256", "sha512"]), default="sha256")
@click.option("--compare", is_flag=True, help="Check if all files have the same hash")
def hash_cmd(files, algo, compare):
    """Hash files and optionally compare them."""
    paths = resolve_files(list(files))
    if not paths:
        click.echo("No files found.", err=True)
        raise SystemExit(1)

    hashes = []
    for path in paths:
        digest = _hash_file(str(path), algo)
        if digest is not None:
            hashes.append((digest, str(path)))
            sys.stdout.write(f"{digest}  {path}\n")

    if compare and hashes:
        unique_hashes = set(h for h, _ in hashes)
        if len(unique_hashes) == 1:
            console.print("[green]MATCH[/green]")
        else:
            console.print("[red]MISMATCH[/red]")


# ---------------------------------------------------------------------------
# copy
# ---------------------------------------------------------------------------

@click.command("copy")
@click.argument("files", nargs=-1)
@click.option("--text", "text_input", default=None, help="Copy text directly")
def copy_cmd(files, text_input):
    """Copy file contents or text to clipboard."""
    if text_input is not None:
        content = text_input
    elif files:
        paths = resolve_files(list(files))
        if not paths:
            click.echo("No files found.", err=True)
            raise SystemExit(1)
        parts = []
        for path in paths:
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    parts.append(f.read())
            except Exception as e:
                click.echo(f"Error reading {path}: {e}", err=True)
        content = "".join(parts)
    else:
        content = sys.stdin.read()

    import platform
    plat = sys.platform
    try:
        if plat == "darwin":
            subprocess.run(["pbcopy"], input=content.encode("utf-8"), check=True)
        elif plat == "win32":
            subprocess.run(["clip"], input=content.encode("utf-8"), check=True)
        else:
            try:
                subprocess.run(["xclip", "-selection", "clipboard"],
                               input=content.encode("utf-8"), check=True)
            except FileNotFoundError:
                subprocess.run(["xsel", "--clipboard", "--input"],
                               input=content.encode("utf-8"), check=True)
        click.echo(f"Copied {len(content)} characters to clipboard")
    except Exception as e:
        console.print(f"[red]Clipboard error: {e}[/red]")
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# wc
# ---------------------------------------------------------------------------

@click.command("wc")
@click.argument("files", nargs=-1, required=True)
@click.option("--format", "output_format", type=click.Choice(["table", "plain", "json"]), default="table")
def wc(files, output_format):
    """Word/line/char count across files."""
    paths = resolve_files(list(files))
    if not paths:
        click.echo("No files found.", err=True)
        raise SystemExit(1)

    rows = []
    for path in paths:
        try:
            lines = read_lines(path)
        except Exception as e:
            click.echo(f"Error reading {path}: {e}", err=True)
            continue

        text = "".join(lines)
        line_count = len(lines)
        word_count = len(text.split())
        char_count = len(text)
        rows.append({"file": str(path), "lines": line_count, "words": word_count, "chars": char_count})

    if not rows:
        return

    total_lines = sum(r["lines"] for r in rows)
    total_words = sum(r["words"] for r in rows)
    total_chars = sum(r["chars"] for r in rows)

    if output_format == "json":
        output = rows[:]
        if len(rows) > 1:
            output.append({"file": "TOTAL", "lines": total_lines, "words": total_words, "chars": total_chars})
        sys.stdout.write(json.dumps(output, indent=2) + "\n")
    elif output_format == "plain":
        for r in rows:
            sys.stdout.write(f"{r['lines']}\t{r['words']}\t{r['chars']}\t{r['file']}\n")
        if len(rows) > 1:
            sys.stdout.write(f"{total_lines}\t{total_words}\t{total_chars}\tTOTAL\n")
    else:
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column("File", style="cyan")
        table.add_column("Lines", justify="right")
        table.add_column("Words", justify="right")
        table.add_column("Chars", justify="right")
        for r in rows:
            table.add_row(r["file"], str(r["lines"]), str(r["words"]), str(r["chars"]))
        if len(rows) > 1:
            table.add_row("[bold]TOTAL[/bold]", str(total_lines), str(total_words), str(total_chars))
        console.print(table)


# ---------------------------------------------------------------------------
# grep-replace
# ---------------------------------------------------------------------------

@click.command("grep-replace")
@click.argument("pattern")
@click.argument("replacement")
@click.argument("files", nargs=-1, required=True)
@click.option("--regex/--no-regex", default=True, help="Treat pattern as regex (default: on)")
@click.option("-i", "--ignore-case", is_flag=True, help="Case-insensitive matching")
@click.option("--confirm", is_flag=True, help="Ask before applying changes to each file")
@click.option("--dry-run", is_flag=True, help="Show diff only, don't write")
def grep_replace(pattern, replacement, files, regex, ignore_case, confirm, dry_run):
    """Search for pattern and replace it, showing diff before writing."""
    compiled = compile_pattern(pattern, regex, ignore_case)
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

        new_lines = []
        changed = False
        for line in lines:
            new_line = compiled.sub(replacement, line)
            new_lines.append(new_line)
            if new_line != line:
                changed = True

        if not changed:
            continue

        # Show diff
        import difflib
        diff = list(difflib.unified_diff(lines, new_lines, fromfile=str(path), tofile=str(path) + " (modified)"))
        for dline in diff:
            dline_stripped = dline.rstrip("\n")
            if dline_stripped.startswith("---") or dline_stripped.startswith("+++"):
                console.print(Text(dline_stripped, style="bold"))
            elif dline_stripped.startswith("@@"):
                console.print(Text(dline_stripped, style="cyan"))
            elif dline_stripped.startswith("-"):
                console.print(Text(dline_stripped, style="red"))
            elif dline_stripped.startswith("+"):
                console.print(Text(dline_stripped, style="green"))
            else:
                console.print(Text(dline_stripped, style="dim"))

        if dry_run:
            continue

        if confirm:
            answer = click.prompt(f"Apply changes to {path}? [y/N]", default="N")
            if answer.lower() != "y":
                continue

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
