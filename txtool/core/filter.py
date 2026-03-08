from typing import List

from txtool.utils import compile_pattern, read_lines


def filter_lines(pattern, paths, invert=False, regex=True, ignore_case=False) -> List[dict]:
    """Filter lines matching pattern in paths.

    Returns list of dicts: {"file": str, "lines": List[str]}
    """
    compiled = compile_pattern(pattern, regex, ignore_case)
    results = []
    for path in paths:
        lines = read_lines(path)
        kept = []
        for line in lines:
            matched = bool(compiled.search(line.rstrip("\n")))
            keep = (not matched) if invert else matched
            if keep:
                kept.append(line.rstrip("\n"))
        results.append({"file": str(path), "lines": kept})
    return results
