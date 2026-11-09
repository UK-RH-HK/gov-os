"""ACT-SETS-GLOBS-1's replay: drafts/indep-walls/replay_walls.py (itself drafts/sets-root-guard/replay_sets.py's reader:
inputs only, never a result; every spelling of the real sets root rewritten to the planted root, the main tree to the
clone; a call still naming the real root skipped and never shown to the hook), with one addition: each call is marked,
from its whole input, as naming the new globs or not, so compare can show that no call that does not name them changed.
  python3 replay_globs.py pass <clone> <planted root> <hook> <pin python> <since ISO> <until ISO> <out.json>
  python3 replay_globs.py compare <before.json> <after.json>
A call names the new globs when its input holds a set's hidden/ folder (<name>/hidden as a path), an XCHECK-r<n>.md,
miss-classes.json or misses.jsonl, or names a planted destination folder (memory-verdict-4, memory-verdict-3, audit-sg, audit-1). compare
prints the counts, each changed call cut to its first line (a heredoc's body never shown), and exits 1 when a call that
does not name the new globs changed or the two passes judged different calls.
"""
import collections
import concurrent.futures
import hashlib
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("replay_walls", os.path.join(HERE, "..", "indep-walls", "replay_walls.py"))
rw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rw)
NEW = re.compile(r"[^/\s'\"\\]+/hidden(?![\w.-])|XCHECK-r[^/\s'\"\\]*\.md|miss-classes\.json|misses\.jsonl|"
                 r"memory-verdict-[34](?![\w.-])|audit-(?:sg|1)(?![\w.-])")


def do_pass(clone, planted, hook, py, since, until, out):
    orig = rw.rs.calls

    def bounded(path, s):
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                if '"tool_use"' not in line:
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                ts = d.get("timestamp") or ""
                if d.get("type") != "assistant" or ts < s or ts >= until:
                    continue
                for x in (d.get("message") or {}).get("content") or []:
                    if isinstance(x, dict) and x.get("type") == "tool_use" and x.get("name") in rw.rs.TOOLS:
                        tin = x.get("input") if isinstance(x.get("input"), dict) else {}
                        yield x["name"], tin, d.get("cwd") or rw.rs.MAIN
    rw.rs.calls = bounded
    try:
        todo, counts = rw.gather(clone, planted, since, until)
    finally:
        rw.rs.calls = orig
    counts["unique judged"] = len(todo)
    res = {}
    with concurrent.futures.ThreadPoolExecutor(int(os.environ.get("REPLAY_WORKERS", "8"))) as ex:
        futs = {ex.submit(rw.judge, hook, py, clone, t[1], t[2], t[3], t[4], t[5]): t for t in todo}
        for fu in concurrent.futures.as_completed(futs):
            key, tool, tin, cwd, role, agent = futs[fu]
            d, why = fu.result()
            form = tin.get("command") or tin.get("file_path") or tin.get("notebook_path") or \
                f"{tin.get('path', '.')} {tin.get('pattern', '')}"
            if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
                form = tin.get("file_path") or tin.get("notebook_path") or ""
            form = (str(form).splitlines() or [""])[0].replace(planted, "<SR>").replace(clone, "<repo>")[:140]
            res[hashlib.sha256(key.encode()).hexdigest()] = {
                "d": d, "why": why[:150], "tool": tool, "role": role, "agent": agent, "form": form,
                "new": bool(NEW.search(json.dumps(tin, ensure_ascii=False)))}
    counts["calls naming the new globs"] = sum(1 for v in res.values() if v["new"])
    json.dump({"since": since, "until": until, "counts": dict(counts), "answers": res}, open(out, "w"))
    print(json.dumps({"since": since, "until": until, "counts": dict(counts),
                      "decisions": dict(collections.Counter(v["d"] for v in res.values()))}, indent=1))


def compare(a, b):
    A, B = json.load(open(a)), json.load(open(b))
    ka, kb = set(A["answers"]), set(B["answers"])
    print(f"window {A['since']} .. {A['until']}; calls judged before {len(ka)}, after {len(kb)}, in both {len(ka & kb)}")
    by, diffs = collections.Counter(), []
    for k in sorted(ka & kb):
        x, y = A["answers"][k], B["answers"][k]
        by[f"{x['d']}->{y['d']}"] += 1
        if x["d"] != y["d"]:
            diffs.append((x, y))
    named = sum(1 for k in ka & kb if B["answers"][k]["new"])
    print("answers:", dict(sorted(by.items())), f"; calls naming the new globs: {named}")
    for x, y in diffs:
        print(f"  {x['d']}->{y['d']} [{'names the new globs' if y['new'] else 'OTHER'}] {y['role']}/{y['agent']} "
              f"{y['tool']} | {y['form'][:100]} | after: {y['why'][:60]}")
    other = sum(1 for _x, y in diffs if not y["new"])
    print(f"differences: {len(diffs)}; naming the new globs: {len(diffs) - other}; other: {other}")
    return 0 if ka == kb and other == 0 and not any(x["d"] == "deny" and y["d"] == "allow" for x, y in diffs) else 1


if __name__ == "__main__":
    if sys.argv[1] == "pass":
        do_pass(*sys.argv[2:9])
    elif sys.argv[1] == "compare":
        sys.exit(compare(sys.argv[2], sys.argv[3]))
    else:
        sys.exit("usage: replay_globs.py pass ... | compare before.json after.json")
