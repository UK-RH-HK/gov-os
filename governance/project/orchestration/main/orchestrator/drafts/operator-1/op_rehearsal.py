#!/usr/bin/env python3
"""ACT-OPERATOR-1's rehearsal: the operator agent installed in a planted HOME, driven through its queue in the clone.

    python3 op_rehearsal.py <step> <clone> <planted home> [args]

Steps:
  bundle-a          ACT-RERANK-GPU-SLOTS-1 (an applied class-(a) ACT, 2026-11-02, DEC-1031) rebuilt as a bundle in the
                    clone's scratch: its module (as committed at d03ce368b) and its .pth line into the planted HOME's
                    reranker environment; its review record (class a) by a planted reviewer; prints the manifest sha
  bundle-b          ACT-SELECT-FIXES-1R: a class-(b) ACT of SELECT-FIXES-1's kind at today's head (one record_only path
                    added to governance/project/test-map.yaml, so fewer tests run); its review (class b)
  queue <ACT>       the CTO's only act: one request line into <home>/gov-os-operator/queue/
  owner <text>      one owner turn (origin human, after the review) appended to the CTO session's planted transcript
  launch            the launcher as the cron line runs it (env -i, HOME the planted one, no --config); prints its result
  undo <ACT>        the owner's undo step, by hand, from the install (its own settings); prints its result
  show <ACT>        the log lines, the notices and the live files of an ACT
The CTO session's id is planted in <clone>/.gov-runtime/scratch/orchestrator/log/cto-session.txt; its transcript is
<home>/.claude/projects/-home-usain-Dynamic-Agentic-Engineering-OS/<id>.jsonl, as the install's default reads it.
"""
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

STEP, R, PH = sys.argv[1], os.path.realpath(sys.argv[2]), os.path.realpath(sys.argv[3])
ARGS = sys.argv[4:]
SCR = os.path.join(R, ".gov-runtime/scratch/orchestrator")
OP = os.path.join(PH, "gov-os-operator")
INST = os.path.join(OP, "install")
SID = "0a1b2c3d-op1r-4e5f-8a9b-rehearsal0001"
TX = os.path.join(PH, ".claude/projects/-home-usain-Dynamic-Agentic-Engineering-OS")
SITE = ".local/share/gov-os/reranker-venv/lib/python3.12/site-packages"
APPLY_SH = r'''#!/bin/bash
# The replayed bundle's apply.sh: check, apply, undo by list.txt from its own folder (cwd the repository, HOME the HOME).
set -u
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
step="${1:-}"
h() { if [ -f "$1" ]; then sha256sum "$1" | cut -c1-64; else echo null; fi; }
while IFS='|' read -r root path before after; do
  [ -z "$root" ] && continue
  case "$root" in repo) f="$PWD/$path" ;; home) f="$HOME/$path" ;; *) exit 9 ;; esac
  case "$step" in
    check) [ "$(h "$f")" = "$before" ] || { echo "moved: $path" >&2; exit 3; } ;;
    apply) if [ "$after" = null ]; then rm -f "$f"; else mkdir -p "$(dirname "$f")"; rm -f "$f"; cat "$B/after/$root/$path" > "$f"; fi ;;
    undo) if [ "$before" = null ]; then rm -f "$f"; else mkdir -p "$(dirname "$f")"; rm -f "$f"; cat "$B/before/$root/$path" > "$f"; fi ;;
    *) exit 2 ;;
  esac
done < "$B/list.txt"
exit 0
'''


def sha(b):
    return hashlib.sha256(b).hexdigest()


def write(p, data, mode=None):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(data if isinstance(data, bytes) else data.encode())
    if mode:
        os.chmod(p, mode)
    return p


def iso(d):
    return d.astimezone().isoformat(timespec="seconds")


def bundle(act, touched, claimed, dec, checks, commands, note):
    b = os.path.join(SCR, "acts", act)
    if os.path.exists(b):
        subprocess.run(["chmod", "-R", "u+w", b])
        subprocess.run(["rm", "-rf", b], check=True)
    files, rows, lines = {}, [], []
    for root, path, before, after in touched:
        if before is not None:
            files[f"before/{root}/{path}"] = sha(before)
            write(os.path.join(b, "before", root, path), before)
        if after is not None:
            files[f"after/{root}/{path}"] = sha(after)
            write(os.path.join(b, "after", root, path), after)
        bs, as_ = (sha(before) if before is not None else None), (sha(after) if after is not None else None)
        rows.append({"root": root, "path": path, "before": bs, "after": as_})
        lines.append(f"{root}|{path}|{bs or 'null'}|{as_ or 'null'}")
    files["list.txt"] = sha(open(write(os.path.join(b, "list.txt"), "\n".join(lines) + "\n"), "rb").read())
    files["apply.sh"] = sha(open(write(os.path.join(b, "apply.sh"), APPLY_SH, 0o755), "rb").read())
    log = (f"{act}: replayed by ACT-OPERATOR-1's rehearsal ({note})\n"
           "check: before as stated; apply; the checks green; undo byte for byte (the rehearsal's own run)\n"
           "failures: 0\n")
    files["rehearsal.log"] = sha(open(write(os.path.join(b, "rehearsal.log"), log), "rb").read())
    m = {"act": act, "dec": dec, "author": "cto", "claimed_class": claimed, "touched": rows, "files": files,
         "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]}, "checks": checks,
         "commands": commands}
    raw = json.dumps(m, indent=1).encode()
    write(os.path.join(b, "manifest.json"), raw)
    msha = sha(raw)
    rb = open(os.path.join(INST, "reviewer-brief.md"), "rb").read()
    block = {"kpis": [{"kpi": f"K{i}", "verdict": "pass", "findings": []} for i in range(1, 7)],
             "manifest_sha256": msha, "class": claimed, "reviewer": "rehearsal-reviewer",
             "reviewer_brief_sha256": sha(rb), "time": iso(datetime.now(timezone.utc) - timedelta(minutes=5))}
    write(os.path.join(b, "review.md"), "# ACT-OPERATOR-1's rehearsal: the planted review of a replayed ACT\n\n"
          "```verdict\n" + json.dumps(block) + "\n```\n")
    write(os.path.join(SCR, "log/cto-session.txt"), SID + "\n")
    os.makedirs(TX, exist_ok=True)
    open(os.path.join(TX, f"{SID}.jsonl"), "a").close()
    print(json.dumps({"act": act, "manifest_sha256": msha, "bundle": b, "touched": [f"{r}:{p}" for r, p, _, _ in touched]}))


if STEP == "bundle-a":
    mod = subprocess.run(["git", "-C", R, "show", "d03ce368b:governance/project/orchestration/tools/gov_reranker_gpu_slot.py"],
                         capture_output=True, check=True).stdout
    pth = b"import gov_reranker_gpu_slot\n"
    chk = (f"python3 -c \"import ast, os; ast.parse(open(os.path.expanduser('~/{SITE}/gov_reranker_gpu_slot.py')).read()); "
           f"print(open(os.path.expanduser('~/{SITE}/gov-reranker-gpu-slot.pth')).read().count('import gov_reranker_gpu_slot'))\"")
    bundle("ACT-RERANK-GPU-SLOTS-1",
           [("home", f"{SITE}/gov_reranker_gpu_slot.py", None, mod), ("home", f"{SITE}/gov-reranker-gpu-slot.pth", None, pth)],
           "a", "DEC-1031", [{"cmd": chk, "exit": 0, "count": 1}],
           ['SP=$($V/bin/python -I -c "import sysconfig; print(sysconfig.get_paths()[\'purelib\'])")',
            'cp /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/gov_reranker_gpu_slot.py "$SP/"',
            "echo 'import gov_reranker_gpu_slot' > \"$SP/gov-reranker-gpu-slot.pth\""],
           "the module at d03ce368b and its .pth line into the planted HOME's reranker environment; no server restarted")
elif STEP == "bundle-b":
    p = "governance/project/test-map.yaml"
    before = open(os.path.join(R, p), "rb").read()
    anchor = b"record_only:\n"
    assert before.count(anchor) == 1
    add = b'  - "docs/research/**/README.md"\n'
    assert add not in before
    after = before.replace(anchor, anchor + add)
    bundle("ACT-SELECT-FIXES-1R", [("repo", p, before, after)], "b", "DEC-1100",
           [{"cmd": f"python3 -c \"import yaml; d = yaml.safe_load(open('{p}')); print(len(d['record_only']))\"",
             "exit": 0, "count": len(__import__("yaml").safe_load(after)["record_only"])}],
           [f"python3 apply.py  # one record_only path added to {p}"],
           "SELECT-FIXES-1's kind at today's head: one record_only path added to the test map")
elif STEP == "queue":
    act = ARGS[0]
    msha = sha(open(os.path.join(SCR, "acts", act, "manifest.json"), "rb").read())
    q = os.path.join(OP, "queue")
    name = f"{time.strftime('%Y%m%dT%H%M%S')}-{act}.req"
    write(os.path.join(q, name), f"{act} {msha}\n")
    print(json.dumps({"queued": name, "line": f"{act} {msha}"}))
elif STEP == "owner":
    text = " ".join(ARGS)
    e = {"type": "user", "origin": {"kind": "human"}, "timestamp": iso(datetime.now(timezone.utc)),
         "sessionId": SID, "message": {"role": "user", "content": text}}
    with open(os.path.join(TX, f"{SID}.jsonl"), "a") as f:
        f.write(json.dumps(e) + "\n")
    print(json.dumps({"owner_line": text}))
elif STEP in ("launch", "undo"):
    env = {"HOME": PH, "PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "USER": "usain", "LOGNAME": "usain",
           "TMPDIR": os.environ.get("OP1_TMP", "/tmp")}
    if STEP == "launch":
        cmd = ["/usr/bin/python3", "-I", os.path.join(INST, "operator_launch.py")]
    else:
        act = ARGS[0]
        msha = sha(open(os.path.join(SCR, "acts", act, "manifest.json"), "rb").read())
        cmd = ["/usr/bin/python3", "-I", os.path.join(INST, "operator_run.py"), "undo", act, msha]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, env=env, timeout=3600)
    last = (r.stdout.decode("utf-8", "replace").strip().splitlines() or ["{}"])[-1]
    print(f"{STEP}: exit {r.returncode} in {time.time() - t0:.0f} s")
    print(last[:1500])
    if r.stderr.strip():
        print("stderr: " + r.stderr.decode("utf-8", "replace").strip()[-600:])
elif STEP == "show":
    act = ARGS[0]
    for ln in open(os.path.join(OP, "log/operator.jsonl")):
        e = json.loads(ln)
        if e.get("act") == act:
            print(f"  log {e.get('gate')} {e.get('result')} votes={e.get('votes')} commit={(e.get('commit') or '')[:12]}"
                  f" undo={e.get('undo')} {(e.get('reason') or '')[:140]}")
    pl = os.path.join(PH, ".config/gov-os-notify/pings.log")
    if os.path.exists(pl):
        for ln in open(pl):
            e = json.loads(ln)
            if e.get("act") == act:
                print(f"  notice {e.get('priority')} {e.get('kind')}: {e.get('line')}")
else:
    sys.exit(f"unknown step {STEP}")
