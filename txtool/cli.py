import click
from rich.console import Console
from rich.table import Table
from rich import box

from txtool.commands.search import search
from txtool.commands.replace import replace
from txtool.commands.filter import filter_cmd
from txtool.commands.stats import stats

from txtool.commands.transform import fmt, case_cmd, sort_cmd, dedup, truncate
from txtool.commands.extract import extract, between, columns
from txtool.commands.fileops import diff_cmd, unique_cmd, concat
from txtool.commands.data import json_cmd, csv_cmd, env_cmd, template_cmd
from txtool.commands.logtools import tail_cmd, parse_log, timestamp_cmd
from txtool.commands.misc import encode_cmd, hash_cmd, copy_cmd, wc, grep_replace

console = Console()


@click.group()
def cli():
    """txtool — a text processing CLI for search, replace, filter, stats, and much more."""
    pass


@cli.command("help")
def help_cmd():
    """Show detailed usage guide for all commands."""
    console.print("\n[bold cyan]txtool[/bold cyan] — text processing CLI\n")

    def section(title, rows):
        t = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta", title=title, title_style="bold yellow")
        t.add_column("Command", style="bold yellow")
        t.add_column("Usage")
        t.add_column("Description")
        for row in rows:
            t.add_row(*row)
        console.print(t)

    section("Search/Replace", [
        ("search",  "txtool search <pattern> <files...>",              "Grep-style search across files"),
        ("replace", "txtool replace <pattern> <replacement> <files...>", "Find and replace in files"),
        ("filter",  "txtool filter <pattern> <files...>",              "Keep or remove matching lines"),
        ("stats",   "txtool stats <files...>",                         "Line/word/char counts + top words"),
    ])

    section("Text Transform", [
        ("fmt",      "txtool fmt <files...>",              "Format: trim, wrap, indent, line endings"),
        ("case",     "txtool case <style> <files...>",     "Convert case: snake/camel/pascal/kebab/upper/lower/title"),
        ("sort",     "txtool sort <files...>",             "Sort lines (alpha, numeric, by length)"),
        ("dedup",    "txtool dedup <files...>",            "Remove duplicate lines (preserve order)"),
        ("truncate", "txtool truncate <files...>",         "Keep first/last N lines"),
    ])

    section("Extraction", [
        ("extract", "txtool extract <files...>",           "Extract emails, URLs, IPs, dates, numbers"),
        ("between", "txtool between <start> <end> <files...>", "Extract lines between two patterns"),
        ("columns", "txtool columns <files...>",           "Extract specific columns"),
    ])

    section("File Operations", [
        ("diff",   "txtool diff <file1> <file2>",  "Line/word/char-level diff with colors"),
        ("unique", "txtool unique <file1> <file2>", "Set operations on lines of two files"),
        ("concat", "txtool concat <files...>",      "Concatenate files to stdout"),
    ])

    section("Data Formats", [
        ("json pretty",    "txtool json pretty <file>",          "Pretty-print JSON"),
        ("json minify",    "txtool json minify <file>",          "Minify JSON"),
        ("json validate",  "txtool json validate <file>",        "Validate JSON"),
        ("json get",       "txtool json get <path> <file>",      "Extract value by dot-notation path"),
        ("csv view",       "txtool csv view <file>",             "Render CSV as rich table"),
        ("csv filter",     "txtool csv filter <cond> <file>",    "Filter CSV rows by condition"),
        ("csv select",     "txtool csv select <cols> <file>",    "Keep only specified columns"),
        ("csv to-json",    "txtool csv to-json <file>",          "Convert CSV to JSON array"),
        ("env show",       "txtool env show [file]",             "Pretty-print .env file"),
        ("env diff",       "txtool env diff <f1> <f2>",          "Diff two env files"),
        ("env check",      "txtool env check <tmpl> <file>",     "Check all template keys exist"),
        ("template",       "txtool template <file> [KEY=val...]", "Replace {{VAR}} placeholders"),
    ])

    section("Log Tools", [
        ("tail",      "txtool tail <file>",       "Show/follow last N lines with log coloring"),
        ("parse-log", "txtool parse-log <files...>", "Count log levels and top errors"),
        ("timestamp", "txtool timestamp <files...>", "Normalize timestamps in log files"),
    ])

    section("Utilities", [
        ("encode",       "txtool encode <method> [files...]", "Base64/URL/HTML encode or decode"),
        ("hash",         "txtool hash <files...>",            "Hash files (md5/sha1/sha256/sha512)"),
        ("copy",         "txtool copy [files...]",            "Copy file/text to clipboard"),
        ("wc",           "txtool wc <files...>",              "Word/line/char counts"),
        ("grep-replace", "txtool grep-replace <pat> <rep> <files...>", "Search+replace with diff preview"),
    ])

    console.print("Run [cyan]txtool <command> --help[/cyan] for full options on any command.\n")


cli.add_command(search)
cli.add_command(replace)
cli.add_command(filter_cmd, name="filter")
cli.add_command(stats)

cli.add_command(fmt)
cli.add_command(case_cmd, name="case")
cli.add_command(sort_cmd, name="sort")
cli.add_command(dedup)
cli.add_command(truncate)

cli.add_command(extract)
cli.add_command(between)
cli.add_command(columns)

cli.add_command(diff_cmd, name="diff")
cli.add_command(unique_cmd, name="unique")
cli.add_command(concat)

cli.add_command(json_cmd, name="json")
cli.add_command(csv_cmd, name="csv")
cli.add_command(env_cmd, name="env")
cli.add_command(template_cmd, name="template")

cli.add_command(tail_cmd, name="tail")
cli.add_command(parse_log, name="parse-log")
cli.add_command(timestamp_cmd, name="timestamp")

cli.add_command(encode_cmd, name="encode")
cli.add_command(hash_cmd, name="hash")
cli.add_command(copy_cmd, name="copy")
cli.add_command(wc)
cli.add_command(grep_replace, name="grep-replace")


if __name__ == "__main__":
    cli()
