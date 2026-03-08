import csv
import io
import json
import re
from typing import Any, List


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------

def json_pretty(text) -> str:
    data = json.loads(text)
    return json.dumps(data, indent=2)


def json_minify(text) -> str:
    data = json.loads(text)
    return json.dumps(data, separators=(",", ":"))


def json_validate(text) -> tuple:
    """Returns (valid: bool, error_msg: str)."""
    try:
        json.loads(text)
        return (True, "")
    except json.JSONDecodeError as e:
        return (False, str(e))


def _json_get_value(data, tokens):
    for token in tokens:
        if isinstance(data, dict):
            data = data[token]
        elif isinstance(data, list):
            data = data[int(token)]
        else:
            raise KeyError(f"Cannot traverse into {type(data)} with key {token!r}")
    return data


def json_get(text, path) -> Any:
    """Extract value from JSON using dot-notation path like 'users[0].name'."""
    data = json.loads(text)
    clean_tokens = []
    for part in re.split(r'\.', path):
        sub = re.split(r'\[|\]', part)
        for s in sub:
            if s:
                clean_tokens.append(s)
    value = _json_get_value(data, clean_tokens)
    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2)
    return str(value)


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

def csv_to_table(text, delimiter=",") -> List[dict]:
    """Parse CSV text into list of row dicts."""
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    return list(reader)


def _evaluate_condition(value, op, operand):
    if op == "=":
        return value == operand
    elif op == "!=":
        return value != operand
    elif op == "~":
        return bool(re.search(operand, value))
    else:
        try:
            v = float(value)
            o = float(operand)
        except ValueError:
            return False
        if op == ">":
            return v > o
        elif op == "<":
            return v < o
        elif op == ">=":
            return v >= o
        elif op == "<=":
            return v <= o
    return False


def csv_filter(text, condition, delimiter=",") -> str:
    """Filter CSV rows by condition like 'status=active' or 'age>30'."""
    m = re.match(r'^(\w+)\s*(>=|<=|!=|>|<|=|~)\s*(.+)$', condition)
    if not m:
        raise ValueError(f"Invalid condition: {condition}")
    col_name, op, operand = m.group(1), m.group(2), m.group(3)

    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)
    if not rows:
        return ""

    headers = rows[0]
    if col_name in headers:
        col_idx = headers.index(col_name)
    else:
        col_idx = int(col_name) - 1

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(headers)
    for row in rows[1:]:
        if col_idx < len(row) and _evaluate_condition(row[col_idx], op, operand):
            writer.writerow(row)
    return out.getvalue()


def csv_select(text, columns, delimiter=",") -> str:
    """Keep only specified columns."""
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)
    if not rows:
        return ""

    headers = rows[0]
    col_specs = [c.strip() for c in columns.split(",")]
    col_indices = []
    for spec in col_specs:
        if spec in headers:
            col_indices.append(headers.index(spec))
        else:
            col_indices.append(int(spec) - 1)

    out = io.StringIO()
    writer = csv.writer(out)
    for row in rows:
        writer.writerow([row[i] if 0 <= i < len(row) else "" for i in col_indices])
    return out.getvalue()


def csv_to_json(text, delimiter=",") -> str:
    """Convert CSV to JSON array string."""
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)
    return json.dumps(rows, indent=2)


# ---------------------------------------------------------------------------
# ENV
# ---------------------------------------------------------------------------

def parse_env(text) -> dict:
    """Parse .env text and return dict of KEY: VALUE."""
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            result[key] = value
    return result


def env_diff(text1, text2) -> dict:
    """Diff two .env texts.

    Returns {"added": dict, "removed": dict, "changed": dict}
    Each changed entry is {"old": str, "new": str}.
    """
    data1 = parse_env(text1)
    data2 = parse_env(text2)
    all_keys = set(data1) | set(data2)
    added = {}
    removed = {}
    changed = {}
    for key in sorted(all_keys):
        if key not in data1:
            added[key] = data2[key]
        elif key not in data2:
            removed[key] = data1[key]
        elif data1[key] != data2[key]:
            changed[key] = {"old": data1[key], "new": data2[key]}
    return {"added": added, "removed": removed, "changed": changed}


def render_template(text, variables) -> str:
    """Replace {{VAR}} placeholders. variables: dict or 'KEY=val KEY2=val2' string."""
    if isinstance(variables, str):
        subs = {}
        for token in variables.split():
            if "=" in token:
                k, _, v = token.partition("=")
                subs[k.strip()] = v.strip()
    else:
        subs = dict(variables)

    def replace_var(m):
        key = m.group(1).strip()
        return subs.get(key, m.group(0))

    return re.sub(r'\{\{(\w+)\}\}', replace_var, text)
