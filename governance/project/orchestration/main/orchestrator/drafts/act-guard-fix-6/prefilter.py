"""ACT-GUARD-FIX-6's decision diff, step 1: what each hook's parser makes of every Bash call of a call set, in process.

  <pin python> -E -B prefilter.py <hooks dir> <project> <calls.jsonl> <out.jsonl> [<max calls>]

Imports the hook's own pretooluse.py (and its bash_writes.py) from <hooks dir> and, per Bash call, records a digest of
what the hook's judgement gives: the writes the guard resolves (shell and code), the folders made, rm's verdict,
whether the scan read the command, and the command as the read rules see it. Prints nothing of the commands. The
calls file is the 48-hour set of tools/build_replay_calls.py. A call that raises is recorded as the exception's type."""
import hashlib
import importlib.util
import json
import os
import sys

hooks, project, calls, out = sys.argv[1:5]
limit = int(sys.argv[5]) if len(sys.argv) > 5 else None
sys.path.insert(0, hooks)
os.environ["CLAUDE_PROJECT_DIR"] = project
os.environ.setdefault("GOV_GUARD_CALLS_DIR", os.path.join(os.environ.get("TMPDIR", "/tmp"), "prefilter-calls"))
spec = importlib.util.spec_from_file_location("pretooluse_under_test", os.path.join(hooks, "pretooluse.py"))
pt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pt)
import bash_writes  # noqa: E402  (beside the hook)


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


RAW = bool(os.environ.get("PREFILTER_RAW"))  # also the raw lists (the file then holds paths: keep it in scratch)
n = 0
with open(calls) as src, open(out, "w") as dst:
    for line in src:
        try:
            c = json.loads(line)
        except ValueError:
            continue
        ev = c.get("event") or {}
        cmd = (ev.get("tool_input") or {}).get("command")
        if ev.get("tool_name") != "Bash" or not isinstance(cmd, str):
            continue
        cwd = ev.get("cwd") or project
        row = {"id": c.get("id")}
        for name, fn in (
                ("writes", lambda: [list(x) for x in pt.bash_writes_of(cmd, cwd)]),
                ("made", lambda: sorted(pt.bash_made(cmd, cwd))),
                ("rm", lambda: pt.rm_refusal(cmd, cwd, project)),
                ("read", lambda: pt.bash_judgement(cmd, cwd) is not None),
                ("view", lambda: bash_writes.reads_view(cmd))):
            try:
                value = fn()
                row[name] = digest(value)
                if RAW and name in ("writes", "made", "rm", "read"):
                    row.setdefault("raw", {})[name] = value
            except Exception as exc:  # noqa: BLE001
                row[name] = "EXC:" + type(exc).__name__
        dst.write(json.dumps(row) + "\n")
        n += 1
        if limit and n >= limit:
            break
print(n)
