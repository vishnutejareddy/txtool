# txtool

A fast, colorful Python CLI for common text processing tasks — search, replace, filter, and stats — across single files, globs, or entire directories.

## Installation

```bash
pip install txtlvit
```

Then use it as:

```bash
txtool --help
```

---

## Commands

### `txtool search` — grep-style search

```bash
txtool search "TODO" "**/*.py"           # regex search across all .py files
txtool search "error" app.log -n         # show line numbers
txtool search -i "warning" logs/*.log    # case-insensitive
txtool search --no-regex "fo+" file.txt  # literal string (not regex)
txtool search "def " src/ -n --no-color  # search entire directory
```

| Flag | Description |
|------|-------------|
| `--regex / --no-regex` | Regex mode (default: on) |
| `-i, --ignore-case` | Case-insensitive matching |
| `-n, --line-numbers` | Show line numbers in output |
| `--color / --no-color` | Colorize matched text |

---

### `txtool replace` — find & replace

```bash
txtool replace "foo" "bar" file.txt              # print result to stdout
txtool replace "foo" "bar" *.txt --in-place      # edit files in place
txtool replace "foo" "bar" file.txt --dry-run    # preview changes only
txtool replace -i "FOO" "bar" file.txt           # case-insensitive
txtool replace "v\d+" "v2" --no-regex file.txt   # literal replace
```

| Flag | Description |
|------|-------------|
| `--regex / --no-regex` | Regex mode (default: on) |
| `-i, --ignore-case` | Case-insensitive matching |
| `--in-place` | Write changes back to file |
| `--dry-run` | Show diff without writing |

---

### `txtool filter` — keep or remove lines

```bash
txtool filter "ERROR" app.log             # keep only ERROR lines
txtool filter -v "DEBUG" app.log          # remove DEBUG lines (invert)
txtool filter -i "warning" logs/*.log     # case-insensitive filter
txtool filter "^#" config.txt -v          # strip comment lines
```

| Flag | Description |
|------|-------------|
| `-v, --invert` | Exclude matching lines instead |
| `--regex / --no-regex` | Regex mode (default: on) |
| `-i, --ignore-case` | Case-insensitive matching |

---

### `txtool stats` — line, word, char counts + top words

```bash
txtool stats file.txt                        # table output (default)
txtool stats *.txt --format plain            # plain text
txtool stats report.txt --format json        # JSON output
txtool stats notes.txt --top 5               # show top 5 words
```

| Flag | Description |
|------|-------------|
| `--top N` | Number of top words to show (default: 10) |
| `--format` | Output format: `table`, `json`, or `plain` |

---

## File Input

All commands accept any combination of:

| Input | Example |
|-------|---------|
| Single file | `file.txt` |
| Glob pattern | `logs/*.log`, `**/*.py` |
| Directory | `src/` (recurses all text files) |

Binary files are automatically detected and skipped.

---

## Quick Reference

```
txtool search  <pattern> <files...>              Search for pattern
txtool replace <pattern> <replacement> <files...> Find and replace
txtool filter  <pattern> <files...>              Filter lines by pattern
txtool stats   <files...>                        Show file statistics
```

Run `txtool <command> --help` for full options on any command.
