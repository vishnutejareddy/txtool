import glob
import re
from pathlib import Path


def resolve_files(patterns):
    """Expand globs, recurse into dirs, return list of Path objects."""
    result = []
    for pattern in patterns:
        p = Path(pattern)
        if p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and not is_binary(f):
                    result.append(f)
        else:
            matched = glob.glob(pattern, recursive=True)
            if matched:
                for m in matched:
                    mp = Path(m)
                    if mp.is_file() and not is_binary(mp):
                        result.append(mp)
            elif p.exists() and p.is_file():
                if not is_binary(p):
                    result.append(p)
    return result


def is_binary(path):
    """Return True if file appears to be binary (contains null bytes in first 1024 bytes)."""
    try:
        with open(path, "rb") as f:
            chunk = f.read(1024)
        return b"\x00" in chunk
    except (OSError, PermissionError):
        return True


def compile_pattern(pattern, regex, ignore_case):
    """Compile a regex pattern from user input."""
    flags = re.IGNORECASE if ignore_case else 0
    if regex:
        return re.compile(pattern, flags)
    else:
        return re.compile(re.escape(pattern), flags)


def read_lines(path):
    """Read lines from a file, returning list of strings."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.readlines()
