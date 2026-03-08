# txtool

A fast, colorful Python CLI for text processing — search, replace, filter, stats, transforms, extraction, file operations, data format tools, log analysis, and more.

## Installation

```bash
pip install txtlvit
```

Then use it as:

```bash
txtool --help
```

---

## Table of Contents

- [Search/Replace](#search--replace)
  - [search](#txtool-search--grep-style-search)
  - [replace](#txtool-replace--find--replace)
  - [filter](#txtool-filter--keep-or-remove-lines)
  - [stats](#txtool-stats--line-word-char-counts--top-words)
- [Text Transform](#text-transform)
  - [fmt](#txtool-fmt--format-text)
  - [case](#txtool-case--convert-case)
  - [sort](#txtool-sort--sort-lines)
  - [dedup](#txtool-dedup--remove-duplicates)
  - [truncate](#txtool-truncate--keep-firstlast-lines)
- [Extraction](#extraction)
  - [extract](#txtool-extract--extract-patterns)
  - [between](#txtool-between--extract-lines-between-markers)
  - [columns](#txtool-columns--extract-columns)
- [File Operations](#file-operations)
  - [diff](#txtool-diff--compare-files)
  - [unique](#txtool-unique--set-operations-on-files)
  - [concat](#txtool-concat--concatenate-files)
- [Data Formats](#data-formats)
  - [json](#txtool-json--json-utilities)
  - [csv](#txtool-csv--csv-utilities)
  - [env](#txtool-env--env-file-utilities)
  - [template](#txtool-template--text-templates)
- [Log Tools](#log-tools)
  - [tail](#txtool-tail--tail-log-files)
  - [parse-log](#txtool-parse-log--parse-log-levels)
  - [timestamp](#txtool-timestamp--normalize-timestamps)
- [Utilities](#utilities)
  - [encode](#txtool-encode--encodedecode-text)
  - [hash](#txtool-hash--hash-files)
  - [copy](#txtool-copy--copy-to-clipboard)
  - [wc](#txtool-wc--word-count)
  - [grep-replace](#txtool-grep-replace--search--replace-with-preview)
- [File Input](#file-input)

---

## Search / Replace

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

## Text Transform

### `txtool fmt` — format text

```bash
txtool fmt --trim file.txt                    # remove trailing whitespace
txtool fmt --line-endings lf file.txt         # normalize to LF
txtool fmt --wrap 80 file.txt                 # wrap lines at 80 chars
txtool fmt --indent 4 file.txt                # add 4-space indent
txtool fmt --dedent file.txt                  # remove common leading whitespace
txtool fmt --trim --wrap 80 --in-place *.txt  # multiple options, edit in place
```

| Flag | Description |
|------|-------------|
| `--trim` | Trim trailing whitespace |
| `--line-endings [lf\|crlf\|cr]` | Normalize line endings |
| `--wrap N` | Wrap lines at N characters |
| `--indent N` | Add N spaces indent to each line |
| `--dedent` | Remove common leading whitespace |
| `--in-place` | Write back to file (default: stdout) |

---

### `txtool case` — convert case

```bash
txtool case snake file.txt     # helloWorld → hello_world
txtool case camel file.txt     # hello_world → helloWorld
txtool case pascal file.txt    # hello_world → HelloWorld
txtool case kebab file.txt     # hello_world → hello-world
txtool case upper file.txt     # hello world → HELLO WORLD
txtool case lower file.txt     # HELLO WORLD → hello world
txtool case title file.txt     # hello world → Hello World
```

| Flag | Description |
|------|-------------|
| `--in-place` | Write back to file (default: stdout) |

---

### `txtool sort` — sort lines

```bash
txtool sort file.txt             # alphabetical sort
txtool sort -r file.txt          # reverse order
txtool sort --numeric file.txt   # sort by numeric value in line
txtool sort --by-length file.txt # sort by line length
txtool sort -u file.txt          # sort and deduplicate
```

| Flag | Description |
|------|-------------|
| `-n, --numeric` | Sort by numeric value found in line |
| `--by-length` | Sort by line length |
| `-r, --reverse` | Reverse order |
| `-u, --unique` | Deduplicate after sorting |
| `--in-place` | Write back to file (default: stdout) |

---

### `txtool dedup` — remove duplicates

```bash
txtool dedup file.txt             # remove duplicate lines, preserve order
txtool dedup --in-place file.txt  # edit in place
```

| Flag | Description |
|------|-------------|
| `--in-place` | Write back to file (default: stdout) |

---

### `txtool truncate` — keep first/last lines

```bash
txtool truncate --head 10 file.txt   # keep first 10 lines
txtool truncate --tail 5 file.txt    # keep last 5 lines
```

| Flag | Description |
|------|-------------|
| `--head N` | Keep first N lines |
| `--tail N` | Keep last N lines |

---

## Extraction

### `txtool extract` — extract patterns

```bash
txtool extract --type email file.txt          # extract email addresses
txtool extract --type url file.txt            # extract URLs
txtool extract --type ip access.log           # extract IP addresses
txtool extract --type date file.txt           # extract dates
txtool extract --type phone contacts.txt      # extract phone numbers
txtool extract --type number data.txt         # extract numbers
txtool extract --unique file.txt              # deduplicate results
```

| Flag | Description |
|------|-------------|
| `--type` | Type to extract: `email url ip date phone number` (multiple allowed) |
| `--unique` | Deduplicate results |

---

### `txtool between` — extract lines between markers

```bash
txtool between START END file.txt              # lines between START and END
txtool between --inclusive START END file.txt  # include delimiter lines
txtool between --regex "^BEGIN" "^END" file.txt # use regex patterns
```

| Flag | Description |
|------|-------------|
| `--inclusive` | Include the delimiter lines themselves |
| `--regex` | Treat start/end as regex (default: literal) |

---

### `txtool columns` — extract columns

```bash
txtool columns -f 1,3 file.txt              # fields 1 and 3 (whitespace-delimited)
txtool columns -d , -f 2,4 file.csv         # CSV fields 2 and 4
txtool columns -d , --header -f name,city data.csv  # by column name
```

| Flag | Description |
|------|-------------|
| `-d, --delimiter` | Field separator (default: whitespace) |
| `-f, --fields` | Comma-separated 1-indexed field numbers |
| `--header` | Treat first row as header; allow field names in --fields |

---

## File Operations

### `txtool diff` — compare files

```bash
txtool diff file1.txt file2.txt        # line-level unified diff
txtool diff --word file1.txt file2.txt # word-level inline diff
txtool diff --char file1.txt file2.txt # character-level inline diff
```

| Flag | Description |
|------|-------------|
| `--word` | Word-level inline diff |
| `--char` | Character-level inline diff |

---

### `txtool unique` — set operations on files

```bash
txtool unique --only-in-a file1.txt file2.txt  # lines only in file1
txtool unique --only-in-b file1.txt file2.txt  # lines only in file2
txtool unique --common file1.txt file2.txt     # lines in both
txtool unique file1.txt file2.txt              # show all sections
```

| Flag | Description |
|------|-------------|
| `--only-in-a` | Lines in file1 but not file2 |
| `--only-in-b` | Lines in file2 but not file1 |
| `--common` | Lines in both files |

---

### `txtool concat` — concatenate files

```bash
txtool concat a.txt b.txt c.txt                    # concatenate to stdout
txtool concat --with-headers a.txt b.txt           # print filename headers
txtool concat --separator "---" a.txt b.txt        # separator between files
```

| Flag | Description |
|------|-------------|
| `--separator TEXT` | Print this text between files |
| `--with-headers` | Print `=== filename ===` before each file |

---

## Data Formats

### `txtool json` — JSON utilities

```bash
txtool json pretty data.json          # pretty-print with indentation
txtool json minify data.json          # minify (remove whitespace)
txtool json validate data.json        # validate and report errors
txtool json get users[0].name data.json  # extract value by dot path
cat data.json | txtool json pretty    # accept stdin
```

---

### `txtool csv` — CSV utilities

```bash
txtool csv view data.csv                        # render as rich table
txtool csv filter "status=active" data.csv      # filter rows
txtool csv filter "age>30" data.csv             # numeric comparison
txtool csv select name,city data.csv            # keep columns
txtool csv to-json data.csv                     # convert to JSON array
txtool csv view -d ";" data.csv                 # custom delimiter
```

Supported filter operators: `=`, `!=`, `>`, `<`, `>=`, `<=`, `~` (regex match)

---

### `txtool env` — env file utilities

```bash
txtool env show .env                        # pretty-print key/value table
txtool env diff .env.example .env           # show added/removed/changed keys
txtool env check .env.example .env          # check all template keys exist
```

---

### `txtool template` — text templates

```bash
txtool template greeting.txt NAME=Alice      # replace {{NAME}} with Alice
txtool template config.txt HOST=localhost PORT=5432  # multiple vars
txtool template --env config.txt             # use environment variables
txtool template --in-place deploy.yaml APP_VERSION=1.2  # edit in place
```

| Flag | Description |
|------|-------------|
| `--env` | Also use current environment variables |
| `--in-place` | Write back to file (default: stdout) |

---

## Log Tools

### `txtool tail` — tail log files

```bash
txtool tail app.log                          # show last 10 lines
txtool tail -n 50 app.log                   # show last 50 lines
txtool tail -f app.log                       # follow file (like tail -f)
txtool tail --filter ERROR app.log           # only show ERROR lines
txtool tail --highlight "timeout" app.log    # highlight matching text
```

Lines are colored by log level: ERROR/CRITICAL=red, WARN=yellow, INFO=green, DEBUG=dim.

| Flag | Description |
|------|-------------|
| `-n, --lines N` | Number of last lines to show (default: 10) |
| `-f, --follow` | Follow file, printing new lines as added |
| `--filter PATTERN` | Only show lines matching pattern |
| `--highlight PATTERN` | Highlight matching text in lines |

---

### `txtool parse-log` — parse log levels

```bash
txtool parse-log app.log                     # table with level counts
txtool parse-log --format json app.log       # JSON output
txtool parse-log *.log                       # multiple files
```

| Flag | Description |
|------|-------------|
| `--format [table\|json]` | Output format (default: table) |

---

### `txtool timestamp` — normalize timestamps

```bash
txtool timestamp app.log                          # normalize to YYYY-MM-DD HH:MM:SS
txtool timestamp --to-format "%d/%m/%Y" app.log   # custom output format
txtool timestamp --in-place app.log               # edit in place
```

Detects formats: ISO 8601, `YYYY-MM-DD HH:MM:SS`, `DD/MM/YYYY HH:MM:SS`, syslog.

| Flag | Description |
|------|-------------|
| `--to-format` | Output datetime format (default: `%Y-%m-%d %H:%M:%S`) |
| `--in-place` | Write back to file (default: stdout) |

---

## Utilities

### `txtool encode` — encode/decode text

```bash
txtool encode base64 --text "hello world"    # encode to base64
txtool encode base64 --decode --text "aGVsbG8="  # decode from base64
txtool encode url --text "hello world"       # URL encode
txtool encode html --text "<b>bold</b>"      # HTML escape
txtool encode base64 file.txt                # encode file
```

| Flag | Description |
|------|-------------|
| `--decode` | Decode instead of encode |
| `--text TEXT` | Encode/decode text directly |

---

### `txtool hash` — hash files

```bash
txtool hash file.txt                         # SHA-256 hash (default)
txtool hash --algo md5 file.txt              # MD5 hash
txtool hash --compare file1.txt file2.txt    # compare hashes
```

| Flag | Description |
|------|-------------|
| `--algo [md5\|sha1\|sha256\|sha512]` | Hash algorithm (default: sha256) |
| `--compare` | Check if all files have the same hash |

---

### `txtool copy` — copy to clipboard

```bash
txtool copy file.txt                  # copy file to clipboard
txtool copy --text "hello world"      # copy text directly
txtool copy a.txt b.txt               # copy multiple files
```

| Flag | Description |
|------|-------------|
| `--text TEXT` | Copy text directly instead of a file |

---

### `txtool wc` — word count

```bash
txtool wc file.txt                    # table output (default)
txtool wc --format plain *.txt        # plain text output
txtool wc --format json *.txt         # JSON output
```

| Flag | Description |
|------|-------------|
| `--format [table\|plain\|json]` | Output format (default: table) |

---

### `txtool grep-replace` — search + replace with preview

```bash
txtool grep-replace "foo" "bar" *.txt         # replace with diff preview
txtool grep-replace "foo" "bar" --dry-run f.txt  # preview only, no write
txtool grep-replace "foo" "bar" --confirm f.txt  # ask before each file
txtool grep-replace -i "FOO" "bar" file.txt   # case-insensitive
```

| Flag | Description |
|------|-------------|
| `--regex / --no-regex` | Regex mode (default: on) |
| `-i, --ignore-case` | Case-insensitive matching |
| `--confirm` | Ask before applying changes to each file |
| `--dry-run` | Show diff only, don't write |

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
txtool search  <pattern> <files...>               Search for pattern
txtool replace <pattern> <replacement> <files...>  Find and replace
txtool filter  <pattern> <files...>               Filter lines by pattern
txtool stats   <files...>                         Show file statistics
txtool fmt     <files...>                         Format text
txtool case    <style> <files...>                 Convert case
txtool sort    <files...>                         Sort lines
txtool dedup   <files...>                         Remove duplicate lines
txtool truncate <files...>                        Keep first/last N lines
txtool extract <files...>                         Extract emails, URLs, etc.
txtool between <start> <end> <files...>           Extract between markers
txtool columns <files...>                         Extract columns
txtool diff    <file1> <file2>                    Compare files
txtool unique  <file1> <file2>                    Set operations on files
txtool concat  <files...>                         Concatenate files
txtool json    <subcommand>                       JSON utilities
txtool csv     <subcommand>                       CSV utilities
txtool env     <subcommand>                       Env file utilities
txtool template <file> [KEY=val...]               Template substitution
txtool tail    <file>                             Tail log file
txtool parse-log <files...>                       Parse log levels
txtool timestamp <files...>                       Normalize timestamps
txtool encode  <method> [files...]                Encode/decode text
txtool hash    <files...>                         Hash files
txtool copy    [files...]                         Copy to clipboard
txtool wc      <files...>                         Word/line/char count
txtool grep-replace <pattern> <replacement> <files...>  Search+replace with diff
```

Run `txtool <command> --help` for full options on any command.
