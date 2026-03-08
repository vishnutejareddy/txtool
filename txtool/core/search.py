from pathlib import Path
from typing import List

from txtool.utils import compile_pattern, read_lines


def search(pattern, paths, regex=True, ignore_case=False) -> List[dict]:
    """Search for pattern in paths.

    Returns list of dicts: {"file": str, "line_number": int, "line": str, "matches": List[str]}
    """
    compiled = compile_pattern(pattern, regex, ignore_case)
    results = []
    for path in paths:
        lines = read_lines(path)
        for lineno, line in enumerate(lines, 1):
            stripped = line.rstrip("\n")
            matches = compiled.findall(stripped)
            if matches:
                results.append({
                    "file": str(path),
                    "line_number": lineno,
                    "line": stripped,
                    "matches": matches,
                })
    return results
