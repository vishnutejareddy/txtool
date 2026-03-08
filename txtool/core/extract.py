import re
from typing import List, Optional


PATTERNS = {
    "email": re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
    "url": re.compile(r'https?://[^\s<>"()]+'),
    "ip": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
    "date": re.compile(r'\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b'),
    "phone": re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
    "number": re.compile(r'\b-?\d+(?:\.\d+)?\b'),
}

ALL_TYPES = list(PATTERNS.keys())


def extract_patterns(text, types=None, unique=False) -> List[dict]:
    """Extract patterns from text.

    Returns list of dicts: {"type": str, "value": str}
    """
    active_types = list(types) if types else ALL_TYPES
    seen = set()
    results = []
    for t in active_types:
        for m in PATTERNS[t].finditer(text):
            val = m.group()
            if unique:
                key = (t, val)
                if key in seen:
                    continue
                seen.add(key)
            results.append({"type": t, "value": val})
    return results


def extract_between(text, start, end, inclusive=False, regex=False) -> str:
    """Extract lines between start and end pattern matches."""
    if regex:
        start_re = re.compile(start)
        end_re = re.compile(end)
    else:
        start_re = re.compile(re.escape(start))
        end_re = re.compile(re.escape(end))

    lines = text.splitlines(keepends=True)
    inside = False
    out = []
    for line in lines:
        stripped = line.rstrip("\n")
        if not inside:
            if start_re.search(stripped):
                inside = True
                if inclusive:
                    out.append(line)
        else:
            if end_re.search(stripped):
                inside = False
                if inclusive:
                    out.append(line)
            else:
                out.append(line)
    return "".join(out)


def extract_columns(text, fields, delimiter=None, header=False) -> str:
    """Extract specific columns from delimited text."""
    lines = text.splitlines(keepends=True)
    if not lines:
        return ""

    header_row = None
    if header:
        header_line = lines[0].rstrip("\n")
        header_row = header_line.split(delimiter) if delimiter else header_line.split()
        data_lines = lines[1:]
    else:
        data_lines = lines

    field_indices = None
    if fields:
        field_specs = [f.strip() for f in fields.split(",")]
        field_indices = []
        for spec in field_specs:
            if header_row and spec in header_row:
                field_indices.append(header_row.index(spec))
            else:
                field_indices.append(int(spec) - 1)

    sep = delimiter if delimiter else "\t"
    out = []
    if header and field_indices is not None:
        selected_headers = [header_row[i] for i in field_indices if 0 <= i < len(header_row)]
        out.append(sep.join(selected_headers) + "\n")

    for line in data_lines:
        stripped = line.rstrip("\n")
        parts = stripped.split(delimiter) if delimiter else stripped.split()
        if field_indices is not None:
            selected = [parts[i] if 0 <= i < len(parts) else "" for i in field_indices]
        else:
            selected = parts
        out.append(sep.join(selected) + "\n")

    return "".join(out)
