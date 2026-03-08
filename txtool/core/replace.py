from typing import List

from txtool.utils import compile_pattern, read_lines


def replace(pattern, replacement, paths, regex=True, ignore_case=False) -> List[dict]:
    """Find and replace pattern in paths.

    Returns list of dicts:
    {"file": str, "changed": bool, "old_lines": List[str], "new_lines": List[str]}
    """
    compiled = compile_pattern(pattern, regex, ignore_case)
    results = []
    for path in paths:
        old_lines = read_lines(path)
        new_lines = [compiled.sub(replacement, line) for line in old_lines]
        results.append({
            "file": str(path),
            "path": path,
            "changed": new_lines != old_lines,
            "old_lines": old_lines,
            "new_lines": new_lines,
        })
    return results


def apply_replace(result_item) -> None:
    """Write new_lines back to file."""
    path = result_item.get("path") or result_item["file"]
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(result_item["new_lines"])
