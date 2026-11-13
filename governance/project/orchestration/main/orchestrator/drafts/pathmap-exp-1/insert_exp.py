#!/usr/bin/env python3
"""ACT-PATHMAP-EXP-1 (round 3 builder): add the one line `      - "experiments/**"` after `      - "docs/probes/**"` in the
paths of the namespace `doc-records` of a path map, and change nothing else. Round 1 and 2 made this line by one exact-text
replacement (the package, section 2); this file is that replacement written down, so a round 3 or later is a re-run, not a
re-typing. Used to build the bundle's after copy; apply.sh never runs it (it puts the frozen copy in).

  python3 -I insert_exp.py <path-map.yaml> --out <file>      writes the result to --out
  python3 -I insert_exp.py --check <path-map.yaml>           prints "state before|applied|other: ..."; exit 0, 0, 3

It refuses (exit 3) unless the exact line `      - "docs/probes/**"` is written exactly once in the whole file, `experiments/**` is in
no namespace yet, and, after the insertion, the file parses, `doc-records.paths` is the old list plus `experiments/**` at the
end, and every other key of the map and every other namespace is equal to the old map's.
"""
import os
import sys
import tempfile

import yaml

OLD = '      - "docs/probes/**"\n'
NEW = OLD + '      - "experiments/**"\n'
NS = "doc-records"
GLOB = "experiments/**"


def state(text):
    d = yaml.safe_load(text)
    ns = d.get("namespaces") if isinstance(d, dict) else None
    if not isinstance(ns, dict) or NS not in ns:
        return "other", "no doc-records namespace"
    holders = [k for k, v in ns.items() if GLOB in (v.get("paths") or [])]
    if not holders:
        return "before", ""
    if holders == [NS] and ns[NS]["paths"][-1] == GLOB:
        return "applied", ""
    return "other", f"{GLOB} is in {holders}"


def insert(text):
    st, why = state(text)
    if st != "before":
        raise ValueError(f"state {st}: {why}".strip())
    lines = text.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    hits = [i for i, l in enumerate(lines) if l == OLD]
    if len(hits) != 1:
        raise ValueError(f'the line {OLD.strip()} is written {len(hits)} times, not once')
    out = "".join(lines[:hits[0]]) + NEW + "".join(lines[hits[0] + 1:])
    old, new = yaml.safe_load(text), yaml.safe_load(out)
    if new["namespaces"][NS]["paths"] != old["namespaces"][NS]["paths"] + [GLOB]:
        raise ValueError("doc-records.paths is not the old list plus the one glob")
    strip = lambda d: {k: v for k, v in d["namespaces"].items() if k != NS}
    if strip(old) != strip(new):
        raise ValueError("another namespace changed")
    if {k: v for k, v in old.items() if k != "namespaces"} != {k: v for k, v in new.items() if k != "namespaces"}:
        raise ValueError("another key of the map changed")
    if {k: v for k, v in old["namespaces"][NS].items() if k != "paths"} != {k: v for k, v in new["namespaces"][NS].items() if k != "paths"}:
        raise ValueError("another field of doc-records changed")
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
