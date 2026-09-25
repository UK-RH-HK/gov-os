#!/usr/bin/env python3
"""Verify every anchor of a held-out oracle against the Git blob it names (run BR-AR-0002, DAG node TA).

For every mapping in the oracle that carries kind + commit + path (chain stage anchors, traps, wrong entries,
alternative enforcement points, effective-behaviour evidence, side-by-side points, both-ways anchors, query and
control items, written_from), this runs the equivalent of `git show <commit>:<path> | sed -n <start>,<end>p` and
checks:
  * the blob exists at that commit;
  * when `lines` is given: 1 <= start <= end <= the blob's line count, and the slice is non-empty;
  * when `symbol` is given: its last component (after `::` or `.`) occurs in the slice (or in the blob if no lines);
  * when `record_id` is given: each `#`-separated part occurs in the blob;
  * when `section` is given: the section text occurs in the blob.

Output is deliberately minimal so it can be saved as evidence without echoing oracle content: one line per anchor,
`<anchor_id> OK|FAIL`, where anchor_id is the anchor's key path inside the oracle; then a count line.
`--why` adds a failure reason (interactive diagnosis only; never save that output). Exit 0 iff every anchor is OK.
Stdlib + PyYAML only; generic, nothing specific to any demonstration case.
"""
import argparse
import os
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))


def walk(node, path=""):
    if isinstance(node, dict):
        if {"kind", "commit", "path"} <= set(node):
            yield path, node
        for k, v in node.items():
            yield from walk(v, f"{path}.{k}" if path else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[{i}]")


class Blobs:
    def __init__(self, repo):
        self.repo = repo
        self.cache = {}

    def get(self, commit, path):
        key = (commit, path)
        if key not in self.cache:
            r = subprocess.run(["git", "-C", self.repo, "show", f"{commit}:{path}"], capture_output=True)
            self.cache[key] = r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None
        return self.cache[key]


def check(a, blobs):
    text = blobs.get(str(a["commit"]), str(a["path"]))
    if text is None:
        return "blob not found at commit"
    lines = text.splitlines()
    scope = text
    if "lines" in a:
        s, e = a["lines"]
        if not (1 <= s <= e <= len(lines)):
            return f"line range outside blob (blob has {len(lines)} lines)"
        scope = "\n".join(lines[s - 1:e])
        if not scope.strip():
            return "line range is empty"
    sym = a.get("symbol")
    if sym:
        last = sym.replace("::", ".").split(".")[-1].strip("()")
        if last not in scope:
            return "symbol not found in range"
    rid = a.get("record_id")
    if rid:
        for part in str(rid).split("#"):
            if part and part not in text:
                return "record_id not found in blob"
    sec = a.get("section")
    if sec and sec not in text:
        return "section not found in blob"
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("oracle")
    ap.add_argument("--repo", default=ROOT)
    ap.add_argument("--why", action="store_true")
    args = ap.parse_args()
    with open(args.oracle, "rb") as f:
        doc = yaml.safe_load(f.read().decode("utf-8"))
    blobs = Blobs(args.repo)
    ok = fail = 0
    for aid, a in walk(doc):
        reason = check(a, blobs)
        if reason is None:
            ok += 1
            print(f"{aid} OK")
        else:
            fail += 1
            print(f"{aid} FAIL" + (f"  ({reason})" if args.why else ""))
    print(f"anchors: {ok + fail}; OK: {ok}; FAIL: {fail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
