import difflib


def _read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.readlines()


def diff_files(path1, path2, level="line") -> str:
    """Compare two files. level: line/word/char. Returns diff as string."""
    lines_a = _read_lines(path1)
    lines_b = _read_lines(path2)

    if level in ("word", "char"):
        out = []
        sm = difflib.SequenceMatcher(None, lines_a, lines_b)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                for line in lines_a[i1:i2]:
                    out.append("  " + line.rstrip("\n"))
            elif tag == "replace":
                for la in lines_a[i1:i2]:
                    out.append("- " + la.rstrip("\n"))
                for lb in lines_b[j1:j2]:
                    out.append("+ " + lb.rstrip("\n"))
            elif tag == "delete":
                for la in lines_a[i1:i2]:
                    out.append("- " + la.rstrip("\n"))
            elif tag == "insert":
                for lb in lines_b[j1:j2]:
                    out.append("+ " + lb.rstrip("\n"))
        return "\n".join(out)
    else:
        diff = list(difflib.unified_diff(lines_a, lines_b, fromfile=str(path1), tofile=str(path2)))
        return "".join(diff) if diff else ""


def set_operations(path1, path2) -> dict:
    """Set operations on file lines.

    Returns {"only_a": List[str], "only_b": List[str], "common": List[str]}
    """
    lines_a = set(l.rstrip("\n") for l in _read_lines(path1))
    lines_b = set(l.rstrip("\n") for l in _read_lines(path2))
    return {
        "only_a": sorted(lines_a - lines_b),
        "only_b": sorted(lines_b - lines_a),
        "common": sorted(lines_a & lines_b),
    }


def concat_files(paths, separator="", with_headers=False) -> str:
    """Concatenate files and return as string."""
    parts = []
    for i, path in enumerate(paths):
        if i > 0 and separator:
            parts.append(separator + "\n")
        if with_headers:
            parts.append(f"=== {path} ===\n")
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            parts.append(f.read())
    return "".join(parts)
