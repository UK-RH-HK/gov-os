#!/usr/bin/env python3
"""ACT-EXAMIN-SETS-1: insert the two evaluation_sets entries (entries.yaml, beside this file) at the end of the
`evaluation_sets:` block of a path map, and nothing else.

  python3 -I insert_entries.py <path-map.yaml> [--out <file>]     writes the result to --out (default: in place, atomically)
  python3 -I insert_entries.py --check <path-map.yaml>            prints "state before|applied|other: ..."; exit 0, 0, 3

The block ends where the parser of gov.util.parts.evaluation_sets ends it (the next line that starts with a character
other than a space, tab, '#' or a newline); the entries go before the comment lines and blank lines that precede that
next key, so a trailing comment stays with its key. It refuses (exit 3) unless `evaluation_sets:` is written once, as a
key at the start of a line, neither entry exists yet, and, after the insertion, the whole file still parses, every old
entry of the block is unchanged and exactly `examin` and `adoption-proving-ground` are new.
"""
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
NEW = ("examin", "adoption-proving-ground")


def load(text):
    return yaml.safe_load(text)


def block_bounds(lines):
    at = [i for i, l in enumerate(lines) if l.startswith("evaluation_sets:")]
    if len(at) != 1:
        raise ValueError("evaluation_sets is not written once as a key at the start of a line")
    end = next((j for j in range(at[0] + 1, len(lines)) if lines[j][:1] not in ("", " ", "\t", "#", "\n", "\r")),
               len(lines))
    ins = end
    while ins > at[0] + 1 and (lines[ins - 1].startswith("#") or not lines[ins - 1].strip()):
        ins -= 1
    return at[0], ins, end


def state(text):
    d = load(text)
    sets = d.get("evaluation_sets") if isinstance(d, dict) else None
    if not isinstance(sets, dict):
        return "other", "no evaluation_sets map"
    have = [n for n in NEW if n in sets]
    if not have:
        return "before", ""
    if len(have) == len(NEW):
        return "applied", ""
    return "other", "only " + have[0] + " is present"


def insert(text, entries):
    st, why = state(text)
    if st != "before":
        raise ValueError(f"state {st}: {why}".strip())
    lines = text.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    _a, ins, _e = block_bounds(lines)
    out = "".join(lines[:ins]) + entries + "".join(lines[ins:])
    old, new = load(text)["evaluation_sets"], load(out)["evaluation_sets"]
    if set(new) != set(old) | set(NEW) or any(new[k] != old[k] for k in old):
        raise ValueError("the result does not hold the old entries unchanged and the two new ones")
    rest_old = {k: v for k, v in load(text).items() if k != "evaluation_sets"}
    rest_new = {k: v for k, v in load(out).items() if k != "evaluation_sets"}
    if rest_old != rest_new:
        raise ValueError("another key of the map changed")
    return out


def main(argv):
    check = "--check" in argv
    args = [a for a in argv if a != "--check"]
    out_to = None
    if "--out" in args:
        i = args.index("--out")
        out_to = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        print(__doc__)
        return 2
    path = args[0]
    with open(path, encoding="utf-8") as f:
        text = f.read()
    try:
        if check:
            st, why = state(text)
            print(f"state {st}" + (f": {why}" if why else ""))
            return 0 if st in ("before", "applied") else 3
        with open(os.path.join(HERE, "entries.yaml"), encoding="utf-8") as f:
            entries = f.read()
        result = insert(text, entries)
    except (ValueError, yaml.YAMLError, OSError) as e:
        print(f"refused: {e}", file=sys.stderr)
        return 3
    dest = out_to or path
    mode = os.stat(path).st_mode & 0o777
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(dest)), prefix=".act-tmp-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(result)
    os.chmod(tmp, mode)
    os.replace(tmp, dest)
    print(f"written {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
