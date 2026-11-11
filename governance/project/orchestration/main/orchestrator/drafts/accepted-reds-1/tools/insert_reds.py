#!/usr/bin/env python3
"""ACT-ACCEPTED-REDS-1: replace the one line `accepted_reds: []` of a path map by the block in entries.yaml (beside this
file), and change nothing else. Used to build the bundle's after copy; apply.sh never runs it (it puts the frozen copy in).

  python3 -I insert_reds.py <path-map.yaml> --out <file>      writes the result to --out
  python3 -I insert_reds.py --check <path-map.yaml>           prints "state before|applied|other: ..."; exit 0, 0, 3

It refuses (exit 3) unless `accepted_reds: []` is written exactly once as a key at the start of a line and no other
`accepted_reds:` key exists, and, after the replacement, the file parses, `accepted_reds` is exactly the entries.yaml
list, and every other key of the map is equal to the old map's.
"""
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
EMPTY = "accepted_reds: []\n"


def state(text):
    d = yaml.safe_load(text)
    reds = d.get("accepted_reds") if isinstance(d, dict) else None
    want = yaml.safe_load(open(os.path.join(HERE, "entries.yaml"), encoding="utf-8").read())["accepted_reds"]
    if reds in ([], None):
        return "before", ""
    if reds == want:
        return "applied", ""
    return "other", "accepted_reds holds other entries"


def insert(text, entries):
    st, why = state(text)
    if st != "before":
        raise ValueError(f"state {st}: {why}".strip())
    lines = text.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    keys = [i for i, l in enumerate(lines) if l.startswith("accepted_reds:")]
    if len(keys) != 1 or lines[keys[0]] != EMPTY:
        raise ValueError("`accepted_reds: []` is not written exactly once as a key at the start of a line")
    out = "".join(lines[:keys[0]]) + entries + "".join(lines[keys[0] + 1:])
    old, new = yaml.safe_load(text), yaml.safe_load(out)
    want = yaml.safe_load(entries)["accepted_reds"]
    if new["accepted_reds"] != want:
        raise ValueError("the result's accepted_reds is not the entries")
    if {k: v for k, v in old.items() if k != "accepted_reds"} != {k: v for k, v in new.items() if k != "accepted_reds"}:
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
    if len(args) != 1 or not (check or out_to):
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
    mode = os.stat(path).st_mode & 0o777
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(out_to)), prefix=".act-tmp-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(result)
    os.chmod(tmp, mode)
    os.replace(tmp, out_to)
    print(f"written {out_to}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
