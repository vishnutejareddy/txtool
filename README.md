# txtool

A Python CLI for common text processing tasks: search, replace, filter, and stats.

## Installation

```bash
pip install -e .
```

## Usage

### search

```bash
txtool search "TODO" "**/*.py" -n
txtool search -i "error" logs/*.log --no-color
```

Options:
- `--regex / --no-regex` — regex mode (default: on)
- `-i, --ignore-case` — case-insensitive
- `-n, --line-numbers` — show line numbers
- `--color / --no-color` — colorize output

### replace

```bash
txtool replace "foo" "bar" file.txt --dry-run
txtool replace "foo" "bar" *.txt --in-place
```

Options:
- `--regex / --no-regex` — regex mode (default: on)
- `-i, --ignore-case` — case-insensitive
- `--in-place` — edit files in place
- `--dry-run` — preview changes without writing

### filter

```bash
txtool filter "ERROR" logs/*.log
txtool filter -v "DEBUG" app.log
```

Options:
- `-v, --invert` — exclude matching lines
- `--regex / --no-regex` — regex mode (default: on)
- `-i, --ignore-case` — case-insensitive

### stats

```bash
txtool stats *.txt --format table
txtool stats report.txt --top 5 --format json
```

Options:
- `--top N` — number of top words (default: 10)
- `--format [table|json|plain]` — output format (default: table)

## File Input

All commands accept:
- Individual file paths: `file.txt`
- Glob patterns: `**/*.py`, `logs/*.log`
- Directory paths (recurse all non-binary files)

Binary files are automatically skipped.
