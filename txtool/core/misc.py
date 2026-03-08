import base64
import hashlib
import html
import urllib.parse
from typing import List

from txtool.utils import compile_pattern, read_lines


def encode_text(text, method, decode=False) -> str:
    """Encode or decode text. method: base64/url/html"""
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
    raise ValueError(f"Unknown method: {method}")


def hash_file(path, algo="sha256") -> str:
    """Compute hash of a file."""
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def word_count(paths) -> List[dict]:
    """Get line/word/char counts for paths.

    Returns list of dicts: {"file": str, "lines": int, "words": int, "chars": int}
    """
    results = []
    for path in paths:
        lines = read_lines(path)
        text = "".join(lines)
        results.append({
            "file": str(path),
            "lines": len(lines),
            "words": len(text.split()),
            "chars": len(text),
        })
    return results


def grep_replace(pattern, replacement, paths, regex=True, ignore_case=False, dry_run=False) -> List[dict]:
    """Search and replace with diff info.

    Returns list of dicts:
    {"file": str, "changed": bool, "old_lines": List[str], "new_lines": List[str]}
    If dry_run=False, writes changes to files.
    """
    compiled = compile_pattern(pattern, regex, ignore_case)
    results = []
    for path in paths:
        old_lines = read_lines(path)
        new_lines = [compiled.sub(replacement, l) for l in old_lines]
        changed = new_lines != old_lines
        results.append({
            "file": str(path),
            "path": path,
            "changed": changed,
            "old_lines": old_lines,
            "new_lines": new_lines,
        })
        if changed and not dry_run:
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
    return results
