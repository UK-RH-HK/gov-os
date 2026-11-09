"""ACT-SANDBOX-SEAL-1's replay: recent tool calls judged by the clone's hook with the map before the seal, then after.

Reads the tool calls exactly as drafts/sets-root-guard/replay_sets.py does (inputs only, never a result; every spelling
of the real sets root rewritten to the planted root, the main tree to the clone; a call still naming the real root is
skipped and never shown to the hook). The window is fixed by two UTC times, so both passes judge the same calls.
  python3 replay_seal.py pass <clone> <planted root> <hook> <pin python> <since ISO> <until ISO> <out.json>
  python3 replay_seal.py compare <before.json> <after.json>
compare prints the counts and each call whose answer differs, cut to its first line (a heredoc's body never shown).
"""
import calendar
import collections
import concurrent.futures
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "replay_sets", os.path.join(HERE, "..", "sets-root-guard", "replay_sets.py"))
rs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rs)


def gather(clone, planted, since, until):
    cut = calendar.timegm(time.strptime(since, "%Y-%m-%dT%H:%M:%S")) - 3600  # files touched since (an hour's margin)

    def rw(v):
        if isinstance(v, str):
            for s in rs.REAL:
                v = v.replace(s, planted)
            return v.replace(rs.MAIN, clone)
        if isinstance(v, list):
            return [rw(x) for x in v]
        if isinstance(v, dict):
            return {k: rw(x) for k, x in v.items()}
        return v

    seen, todo, counts = set(), [], collections.Counter()
    for f, role, agent in rs.sessions(cut):
        for tool, tin, cwd in rs.calls(f, since):
            counts["calls in the window, to the start"] += 1
            tin2, cwd2 = rw(tin), rw(cwd)
            text = json.dumps(tin2) + cwd2
            if "gov-os-eval" in text.replace(planted, ""):
                counts["skipped: names the real sets root in a form not rewritten"] += 1
                continue
            key = json.dumps([tool, tin2, cwd2, role, agent], sort_keys=True)
            if key in seen:
                counts["duplicates"] += 1
                continue
            seen.add(key)
            todo.append((key, tool, tin2, cwd2, role, agent))
    return todo, counts


def judge(hook, py, clone, tool, tin, cwd, role, agent):
    event = {"tool_name": tool, "tool_input": tin, "cwd": cwd, "session_id": "seal-replay", "agent_type": agent}
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "GOV_ROLE", "GOV_TICKET")}
    env.update(CLAUDE_PROJECT_DIR=clone, GOV_TICKET="DAEO-sdxk")
    if role and role != "unknown":
        env["GOV_ROLE"] = role
    p = subprocess.run([py, "-E", hook], input=json.dumps(event), capture_output=True, text=True, env=env, timeout=90)
    if p.returncode == 2:
        return "deny", "exit 2: " + p.stderr.strip()[-160:]
    if p.stdout.strip():
        o = json.loads(p.stdout)["hookSpecificOutput"]
        return o["permissionDecision"], o["permissionDecisionReason"]
    return "allow", ""


def do_pass(clone, planted, hook, py, since, until, out):
    # the window's end: records after `until` are left out by filtering on the record's own timestamp
    orig = rs.calls

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
                    if isinstance(x, dict) and x.get("type") == "tool_use" and x.get("name") in rs.TOOLS:
                        tin = x.get("input") if isinstance(x.get("input"), dict) else {}
                        yield x["name"], tin, d.get("cwd") or rs.MAIN
    rs.calls = bounded
    try:
        todo, counts = gather(clone, planted, since, until)
    finally:
        rs.calls = orig
    counts["unique judged"] = len(todo)
    res = {}
    with concurrent.futures.ThreadPoolExecutor(int(os.environ.get("REPLAY_WORKERS", "8"))) as ex:
        futs = {ex.submit(judge, hook, py, clone, t[1], t[2], t[3], t[4], t[5]): t for t in todo}
        for fu in concurrent.futures.as_completed(futs):
            key, tool, tin, cwd, role, agent = futs[fu]
            d, why = fu.result()
            form = tin.get("command") or tin.get("file_path") or tin.get("notebook_path") or \
                f"{tin.get('path', '.')} {tin.get('pattern', '')}"
            if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
                form = tin.get("file_path") or tin.get("notebook_path") or ""
            form = (str(form).splitlines() or [""])[0].replace(planted, "<SR>").replace(clone, "<repo>")[:140]
            res[hashlib.sha256(key.encode()).hexdigest()] = {"d": d, "why": why[:150], "tool": tool, "role": role,
                                                            "agent": agent, "form": form}
    json.dump({"since": since, "until": until, "counts": dict(counts), "answers": res}, open(out, "w"))
    print(json.dumps({"since": since, "until": until, "counts": dict(counts),
                      "decisions": dict(collections.Counter(v["d"] for v in res.values()))}, indent=1))


def compare(a, b):
    A, B = json.load(open(a)), json.load(open(b))
    ka, kb = set(A["answers"]), set(B["answers"])
    print(f"window {A['since']} .. {A['until']}; calls judged before {len(ka)}, after {len(kb)}, "
          f"in both {len(ka & kb)}")
    by, diffs = collections.Counter(), []
    for k in sorted(ka & kb):
        x, y = A["answers"][k], B["answers"][k]
        by[f"{x['d']}->{y['d']}"] += 1
        if x["d"] != y["d"]:
            diffs.append((x, y))
    print("answers:", dict(sorted(by.items())))
    for x, y in diffs:
        print(f"  {x['d']}->{y['d']} {y['role']}/{y['agent']} {y['tool']} | {y['form'][:110]} | after: {y['why'][:60]}")
    print(f"differences: {len(diffs)}")
    return 0 if ka == kb else 1


if __name__ == "__main__":
    if sys.argv[1] == "pass":
        do_pass(*sys.argv[2:9])
    elif sys.argv[1] == "compare":
        sys.exit(compare(sys.argv[2], sys.argv[3]))
    else:
        sys.exit("usage: replay_seal.py pass ... | compare before.json after.json")
