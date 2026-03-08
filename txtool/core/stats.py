import re
from collections import Counter
from typing import List

from txtool.utils import read_lines


def compute_stats(paths, top=10) -> List[dict]:
    """Compute statistics for paths.

    Returns list of dicts:
    {"file": str, "lines": int, "words": int, "chars": int, "top_words": List[tuple]}
    """
    results = []
    for path in paths:
        lines = read_lines(path)
        content = "".join(lines)
        words = re.findall(r"\b\w+\b", content.lower())
        results.append({
            "file": str(path),
            "lines": len(lines),
            "words": len(words),
            "chars": len(content),
            "top_words": Counter(words).most_common(top),
        })
    return results
