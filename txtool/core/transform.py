import re
import textwrap


def fmt_text(text, trim=False, line_endings=None, wrap=None, indent=None, dedent=False) -> str:
    """Format text: trim, wrap, indent, line endings."""
    if dedent:
        text = textwrap.dedent(text)

    lines = text.splitlines(keepends=True)

    if trim:
        new_trim = []
        for l in lines:
            content = l.rstrip("\n")
            newline = l[len(content):]
            new_trim.append(content.rstrip(" \t") + newline)
        lines = new_trim

    if wrap is not None:
        new_lines = []
        for line in lines:
            stripped = line.rstrip("\n")
            wrapped = textwrap.fill(stripped, width=wrap)
            new_lines.append(wrapped + "\n")
        lines = new_lines

    if indent is not None:
        prefix = " " * indent
        lines = [prefix + l for l in lines]

    text = "".join(lines)

    if line_endings == "lf":
        text = text.replace("\r\n", "\n").replace("\r", "\n")
    elif line_endings == "crlf":
        text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")
    elif line_endings == "cr":
        text = text.replace("\r\n", "\n").replace("\n", "\r")

    return text


def _split_token(token):
    token = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', token)
    words = re.split(r'[_\-\s]+', token)
    return [w for w in words if w]


def _to_snake(token):
    return "_".join(w.lower() for w in _split_token(token))


def _to_camel(token):
    words = _split_token(token)
    if not words:
        return token
    return words[0].lower() + "".join(w.capitalize() for w in words[1:])


def _to_pascal(token):
    return "".join(w.capitalize() for w in _split_token(token))


def _to_kebab(token):
    return "-".join(w.lower() for w in _split_token(token))


_CASE_CONVERTERS = {
    "snake": _to_snake,
    "camel": _to_camel,
    "pascal": _to_pascal,
    "kebab": _to_kebab,
}

_TOKEN_RE = re.compile(r'[a-zA-Z][a-zA-Z0-9_-]*')


def convert_case(text, style) -> str:
    """Convert case. style: snake/camel/pascal/kebab/upper/lower/title"""
    lines = text.splitlines(keepends=True)
    out_lines = []
    for line in lines:
        content = line.rstrip("\n")
        newline = line[len(content):]
        if style == "upper":
            out_lines.append(content.upper() + newline)
        elif style == "lower":
            out_lines.append(content.lower() + newline)
        elif style == "title":
            out_lines.append(content.title() + newline)
        else:
            converter = _CASE_CONVERTERS[style]
            converted = _TOKEN_RE.sub(lambda m: converter(m.group()), content)
            out_lines.append(converted + newline)
    return "".join(out_lines)


def _numeric_key(line):
    m = re.search(r'-?\d+(?:\.\d+)?', line)
    if m:
        try:
            return float(m.group())
        except ValueError:
            pass
    return 0.0


def sort_lines(text, numeric=False, by_length=False, reverse=False, unique=False) -> str:
    """Sort lines in text."""
    stripped = [l.rstrip("\n") for l in text.splitlines(keepends=True)]

    if numeric:
        stripped.sort(key=_numeric_key, reverse=reverse)
    elif by_length:
        stripped.sort(key=len, reverse=reverse)
    else:
        stripped.sort(reverse=reverse)

    if unique:
        seen = set()
        deduped = []
        for l in stripped:
            if l not in seen:
                seen.add(l)
                deduped.append(l)
        stripped = deduped

    return "\n".join(stripped) + ("\n" if stripped else "")


def dedup_lines(text) -> str:
    """Remove duplicate lines, preserving insertion order."""
    lines = text.splitlines(keepends=True)
    seen = set()
    out_lines = []
    for line in lines:
        key = line.rstrip("\n")
        if key not in seen:
            seen.add(key)
            out_lines.append(line)
    return "".join(out_lines)


def truncate_lines(text, head=None, tail=None) -> str:
    """Keep first/last N lines."""
    lines = text.splitlines(keepends=True)
    if head is not None:
        lines = lines[:head]
    elif tail is not None:
        lines = lines[-tail:] if tail > 0 else []
    return "".join(lines)
