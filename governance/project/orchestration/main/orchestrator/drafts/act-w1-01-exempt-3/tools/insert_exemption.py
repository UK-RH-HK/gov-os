#!/usr/bin/env python3
"""ACT-W1-01-EXEMPT-3: add one entry to the path map's `acceptance_exemptions` list, after its last entry, and change
nothing else. Used to build the bundles' after copies; apply.sh never runs it (it puts the frozen copy in).

  python3 -I insert_exemption.py <path-map.yaml> --out <file>     writes the result to --out
  python3 -I insert_exemption.py --check <path-map.yaml>          prints "state before|applied|other: ..."; exit 0, 0, 3

It refuses (exit 3) unless the list `acceptance_exemptions:` is written once as a key at the start of a line, its last
entry is followed by the comment line that opens the next block, the entry is not yet listed, and, after the insertion,
the file parses, the list is the old list plus exactly this entry at the end, and every other key of the map is equal.
"""
import os
import sys
import tempfile

import yaml

COMMIT = "6fbe73b1adde40571f00d490b4b478cf86b70a52"
DECISION = "DEC-1136"
ENTRY = (f'  - commit: "{COMMIT}"\n'
         f"    decision: {DECISION}  # the owner's ACT-OPERATOR-ROUNDS-1 commit changed the acceptance support file "
         "tests/acceptance/W2-148/w2_148_support.py (DEC-1136 (1)); not a test designer's commit\n")
KEY = "acceptance_exemptions:"
NEXT_BLOCK = "# gov close of this project (DEC-549, DEC-554)"


def listed(d):
    return [e.get("commit") for e in (d.get("acceptance_exemptions") or []) if isinstance(e, dict)]


def state(text):
    d = yaml.safe_load(text)
    if not isinstance(d, dict) or not isinstance(d.get("acceptance_exemptions"), list):
        return "other", "acceptance_exemptions is not a list"
    return ("applied", "") if COMMIT in listed(d) else ("before", "")


def insert(text):
    st, why = state(text)
    if st != "before":
        raise ValueError(f"state {st}: {why}".strip())
    lines = text.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    keys = [i for i, l in enumerate(lines) if l.startswith(KEY)]
    nexts = [i for i, l in enumerate(lines) if l.startswith(NEXT_BLOCK)]
    if len(keys) != 1 or len(nexts) != 1 or nexts[0] <= keys[0]:
        raise ValueError("the list's key or the comment that follows it is not written exactly once")
    out = "".join(lines[:nexts[0]]) + ENTRY + "".join(lines[nexts[0]:])
    old, new = yaml.safe_load(text), yaml.safe_load(out)
    want = old["acceptance_exemptions"] + [{"commit": COMMIT, "decision": DECISION}]
    if new["acceptance_exemptions"] != want:
        raise ValueError("the result's list is not the old list plus the one entry")
    if {k: v for k, v in old.items() if k != "acceptance_exemptions"} != \
            {k: v for k, v in new.items() if k != "acceptance_exemptions"}:
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
        result = insert(text)
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
