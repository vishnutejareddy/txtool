import re
from collections import Counter
from datetime import datetime
from typing import List

from txtool.utils import read_lines


LOG_LEVEL_RE = re.compile(r'\b(DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL|FATAL)\b')

LEVEL_STYLES = {
    "DEBUG": "dim",
    "INFO": "green",
    "WARN": "yellow",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "red bold",
    "FATAL": "red bold",
}

TIMESTAMP_FORMATS = [
    ("%Y-%m-%dT%H:%M:%S", re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')),
    ("%Y-%m-%d %H:%M:%S", re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')),
    ("%d/%m/%Y %H:%M:%S", re.compile(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}')),
    ("%b %d %H:%M:%S", re.compile(r'[A-Z][a-z]{2}\s+\d{1,2} \d{2}:\d{2}:\d{2}')),
]


def tail_lines(path, n=10) -> List[str]:
    """Return last n lines of file as list of strings (no trailing newline)."""
    lines = read_lines(path)
    return [l.rstrip("\n") for l in lines[-n:]]


def parse_log_levels(paths) -> List[dict]:
    """Parse log files and return level counts and top errors.

    Returns list of dicts:
    {"file": str, "total": int, "counts": dict, "top_errors": List[str]}
    """
    results = []
    for path in paths:
        lines = read_lines(path)
        total = len(lines)
        level_counts = Counter()
        error_messages = []

        for line in lines:
            stripped = line.rstrip("\n")
            m = LOG_LEVEL_RE.search(stripped)
            if m:
                level = m.group(1).upper()
                if level == "WARNING":
                    level = "WARN"
                level_counts[level] += 1
                if level in ("ERROR", "CRITICAL", "FATAL"):
                    error_messages.append(stripped)

        top_errors = [msg for msg, _ in Counter(error_messages).most_common(5)]
        results.append({
            "file": str(path),
            "total": total,
            "counts": dict(level_counts),
            "top_errors": top_errors,
        })
    return results


def normalize_timestamps(text, to_format="%Y-%m-%d %H:%M:%S") -> str:
    """Normalize timestamps in text to to_format."""
    lines = text.splitlines(keepends=True)
    out_lines = []
    for line in lines:
        new_line = line
        for fmt, ts_re in TIMESTAMP_FORMATS:
            def replace_ts(m, fmt=fmt):
                try:
                    dt = datetime.strptime(m.group(), fmt)
                    return dt.strftime(to_format)
                except ValueError:
                    return m.group()
            new_line = ts_re.sub(replace_ts, new_line)
        out_lines.append(new_line)
    return "".join(out_lines)
