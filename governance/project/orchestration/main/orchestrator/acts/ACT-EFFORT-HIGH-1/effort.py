#!/usr/bin/env python3
"""ACT-EFFORT-HIGH-1's JSON-aware edit of the top-level "effortLevel" of a settings file.

    effort.py state <file>             prints before | applied | other: <why>   (exit 0 for the first two, 3 otherwise)
    effort.py edit <file> <out>        writes <out>: <file> with ONLY the top-level value "xhigh" replaced by "high"

The edit is a text splice at the value's own span (found by a scanner that tracks strings and nesting depth), so key
order, indentation, line endings and every other byte are kept. The result is parsed and compared with the input: the
only difference may be that one key. A file that does not parse, has no single top-level effortLevel, or has a value
other than "xhigh" (or, for state, "high") is refused.
"""
import json
import sys

KEY = "effortLevel"
WS = " \t\r\n"


def find_top(text, key):
    """The (start, end) spans of every top-level value of `key` that is a string; raises ValueError on a shape not
    understood. Top level means depth 1 inside the one outer object."""
    spans = []
    i, n, depth, expect_key = 0, len(text), 0, False
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            if depth == 1 and expect_key:
                name = json.loads(text[i:j + 1])
                m = j + 1
                while text[m] in WS:
                    m += 1
                if text[m] != ":":
                    raise ValueError("a key without a colon")
                m += 1
                while text[m] in WS:
                    m += 1
                expect_key = False
                if name == key:
                    if text[m] != '"':
                        spans.append((m, None))
                    else:
                        k = m + 1
                        while text[k] != '"':
                            k += 2 if text[k] == "\\" else 1
                        spans.append((m, k + 1))
                i = m
                continue
            i = j + 1
            continue
        if c in "{[":
            depth += 1
            if c == "{" and depth == 1:
                expect_key = True
        elif c in "}]":
            depth -= 1
        elif c == "," and depth == 1:
            expect_key = True
        i += 1
    return spans


def read(path):
    with open(path, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8")
    doc = json.loads(text)
    if not isinstance(doc, dict):
        raise ValueError("the file is not a JSON object")
    return text, doc


def state(path):
    try:
        text, doc = read(path)
        spans = find_top(text, KEY)
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        return "other", f"cannot be read as a settings object ({exc.__class__.__name__})"
    if len(spans) != 1 or spans[0][1] is None:
        return "other", f"no single top-level string {KEY}"
    value = doc.get(KEY)
    if value == "xhigh":
        return "before", "top-level effortLevel is xhigh"
    if value == "high":
        return "applied", "top-level effortLevel is high"
    return "other", f"top-level effortLevel is {value!r}, neither xhigh nor high"


def edit(path, out):
    st, why = state(path)
    if st != "before":
        raise ValueError(f"not the before state ({st}: {why})")
    text, doc = read(path)
    (a, b), = find_top(text, KEY)
    new = text[:a] + '"high"' + text[b:]
    new_doc = json.loads(new)
    want = dict(doc)
    want[KEY] = "high"
    if new_doc != want or list(new_doc) != list(doc):
        raise ValueError("the result differs from the input in more than the one key")
    with open(out, "wb") as f:
        f.write(new.encode("utf-8"))


def main(argv):
    if len(argv) == 3 and argv[1] == "state":
        st, why = state(argv[2])
        print(f"{st}: {why}" if st == "other" else st)
        return 0 if st in ("before", "applied") else 3
    if len(argv) == 4 and argv[1] == "edit":
        try:
            edit(argv[2], argv[3])
        except (OSError, ValueError, UnicodeDecodeError) as exc:
            print(f"refused: {exc}", file=sys.stderr)
            return 3
        return 0
    print("usage: effort.py state <file> | edit <file> <out>", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
