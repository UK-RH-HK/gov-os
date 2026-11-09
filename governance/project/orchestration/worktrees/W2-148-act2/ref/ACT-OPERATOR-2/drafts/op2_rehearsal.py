#!/usr/bin/env python3
"""ACT-OPERATOR-2's rehearsal driver: the re-installed operator agent in a planted HOME, driven through its queue in the
clone (after ACT-OPERATOR-1's op_rehearsal.py; the bundle, queue, owner, launch and undo steps are its own).

    python3 op2_rehearsal.py <step> <clone> <planted home> <base> [args]

Steps:
  bundle-p <ACT> <set>   a class-(a) path-map ACT: one glob `fixtures/evaluation/<set>/hidden/**` added to
                         sets_root_hidden.hidden in the clone's governance/project/path-map.yaml (a refusal added, so it
                         tightens: OPERATOR-AGENT-1 §2); its planted review (class a); prints the manifest sha
  plant-replay [mode]    the CTO's call set (<base>/replay/calls.jsonl, the install's `calls`) and the guard's call log
                         (<home>/.gov-os/guard-calls/<UTC day>.jsonl): a 48.5-hour window ending 30 min ago, three calls
                         and one dropped call, each logged once. mode `missing`: one more logged live call the set does
                         not hold (the log-to-set check must refuse); mode `nolog`: one set call the log does not hold
  queue <ACT>            the CTO's only act: one request line into <home>/gov-os-operator/queue/
  owner <text>           one owner turn appended to the CTO session's planted transcript
  launch                 the launcher as the cron line runs it (env -i, HOME the planted one, python3 -I, no --config)
  undo <ACT>             the owner's undo step, by hand, from the install
  show <ACT>             the log lines and notices of an ACT
  real-check <set file>  the installed agent's own check (read_call_set, check_against_log) of a call set built by the
                         CTO's builder from the real transcripts against the real guard log, read only; prints counts
"""
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

STEP, R, PH, BASE = sys.argv[1], os.path.realpath(sys.argv[2]), os.path.realpath(sys.argv[3]), os.path.realpath(sys.argv[4])
ARGS = sys.argv[5:]
SCR = os.path.join(R, ".gov-runtime/scratch/orchestrator")
OP = os.path.join(PH, "gov-os-operator")
INST = os.path.join(OP, "install")
SID = "0a1b2c3d-op2r-4e5f-8a9b-rehearsal0002"
TX = os.path.join(PH, ".claude/projects/-home-usain-Dynamic-Agentic-Engineering-OS")
LIVE_SID = "5d2c1b0a-9e8f-4a7b-8c6d-0e1f2a3b4c5d"      # a live session id (a lower-case UUID), as the check requires
OTHER_SID = "6e3d2c1b-0a9f-4b8c-9d7e-1f2a3b4c5d6e"
APPLY_SH = r'''#!/bin/bash
# The rehearsal bundle's apply.sh: check, apply, undo by list.txt from its own folder (cwd the repository, HOME the HOME).
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
    log = (f"{act}: built by ACT-OPERATOR-2's rehearsal ({note})\n"
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
    write(os.path.join(b, "review.md"), "# ACT-OPERATOR-2's rehearsal: the planted review of a rehearsal ACT\n\n"
          "```verdict\n" + json.dumps(block) + "\n```\n")
    write(os.path.join(SCR, "log/cto-session.txt"), SID + "\n")
    os.makedirs(TX, exist_ok=True)
    open(os.path.join(TX, f"{SID}.jsonl"), "a").close()
    print(json.dumps({"act": act, "manifest_sha256": msha, "bundle": b, "touched": [f"{r}:{p}" for r, p, _, _ in touched]}))


# -- the call set and the guard's call log (W2-148's forms; the hash is the guard's action_bytes) --------------------
def action_sha(tool, inp):
    return sha(json.dumps({"tool": tool, "input": inp}, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False).encode("utf-8"))


NOW = datetime.now(timezone.utc)


def ago(h):
    return NOW - timedelta(hours=h)


def log_time(at):
    u = at.astimezone(timezone.utc)
    return u.strftime("%Y-%m-%dT%H:%M:%S.") + f"{u.microsecond // 1000:03d}Z"


def set_call(cid, h, path, session=LIVE_SID, role="engineer", ticket="W2-999"):
    inp = {"file_path": path}
    return {"id": cid, "time": ago(h).isoformat(), "session": session, "role": role, "ticket": ticket, "agent": "",
            "sha256": action_sha("Read", inp), "event": {"tool_name": "Read", "tool_input": inp, "cwd": "."}}


def log_line(at, shav, session=LIVE_SID, role="engineer", ticket="W2-999", tree="worktree"):
    return {"v": 1, "time": log_time(at), "session": session, "role": role, "agent": "", "ticket": ticket,
            "tool": "Read", "decision": "allow", "rule": "none", "tree": tree, "ms": 71, "sha256": shav, "keyed": None}


if STEP == "bundle-p":
    act, setname = ARGS[0], ARGS[1]
    p = "governance/project/path-map.yaml"
    before = open(os.path.join(R, p), "rb").read()
    anchor = b'           "fixtures/evaluation/sandbox-guard-exp-1/hidden/**", "indep-walls/**"'
    assert before.count(anchor) == 1, "the sets_root_hidden anchor moved"
    glob = f'"fixtures/evaluation/{setname}/hidden/**"'.encode()
    assert glob not in before
    after = before.replace(anchor, anchor + b", " + glob)
    import yaml
    n_after = len(yaml.safe_load(after)["sets_root_hidden"]["hidden"])
    bundle(act, [("repo", p, before, after)], "a", "DEC-1101",
           [{"cmd": f"python3 -c \"import yaml; print(len(yaml.safe_load(open('{p}'))['sets_root_hidden']['hidden']))\"",
             "exit": 0, "count": n_after}],
           [f"python3 apply.py  # one refusal glob added to sets_root_hidden.hidden in {p}"],
           f"one refusal glob, fixtures/evaluation/{setname}/hidden/**, added to sets_root_hidden (a tightening)")
elif STEP == "plant-replay":
    mode = ARGS[0] if ARGS else "agree"
    calls_file = os.path.join(BASE, "replay", "calls.jsonl")
    logdir = os.path.join(PH, ".gov-os", "guard-calls")
    if os.path.isdir(logdir):
        subprocess.run(["rm", "-rf", logdir], check=True)
    os.makedirs(logdir)
    header = {"v": 1, "window": {"since": ago(48.5).isoformat(), "until": ago(0.5).isoformat()},
              "built_by": "planted (ACT-OPERATOR-2 rehearsal)"}
    calls = [set_call("call-readme", 40, "README.md"), set_call("call-notes", 2, "docs/notes.md"),
             set_call("call-ticket", 10, ".tickets/DAEO-52ku.md", role="orchestrator", ticket="DAEO-sdxk")]
    dropped_sha = action_sha("Read", {"file_path": "/planted/sets-root/transcripts/t.jsonl"})
    dropped = {"id": "call-dropped", "time": ago(30).isoformat(), "session": LIVE_SID, "sha256": dropped_sha,
               "dropped": "names the sets root"}
    log = [log_line(datetime.fromisoformat(c["time"]), c["sha256"], role=c["role"], ticket=c["ticket"]) for c in calls]
    log.append(log_line(datetime.fromisoformat(dropped["time"]), dropped_sha))
    lines = calls + [dropped]
    if mode == "missing":   # a live call the guard logged that the set does not hold
        log.append(log_line(ago(5), action_sha("Read", {"file_path": "docs/plan/missing.md"}), session=OTHER_SID))
    elif mode == "nolog":   # a set call the guard never logged
        lines.append(set_call("call-unlogged", 6, "docs/plan/unlogged.md"))
    write(calls_file, "".join(json.dumps(r) + "\n" for r in [header] + lines), 0o600)
    for line in sorted(log, key=lambda x: x["time"]):
        with open(os.path.join(logdir, f"{line['time'][:10]}.jsonl"), "a") as f:
            f.write(json.dumps(line, separators=(",", ":")) + "\n")
    print(json.dumps({"mode": mode, "set_lines": len(lines), "log_lines": len(log),
                      "log_days": sorted(os.listdir(logdir)), "calls": calls_file}))
elif STEP == "queue":
    act = ARGS[0]
    msha = sha(open(os.path.join(SCR, "acts", act, "manifest.json"), "rb").read())
    name = f"{time.strftime('%Y%m%dT%H%M%S')}-{act}.req"
    write(os.path.join(OP, "queue", name), f"{act} {msha}\n")
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
           "TMPDIR": os.environ.get("OP2_TMP", "/tmp")}
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
    print(last[:2000])
    if r.stderr.strip():
        print("stderr: " + r.stderr.decode("utf-8", "replace").strip()[-600:])
elif STEP == "show":
    act = ARGS[0]
    for ln in open(os.path.join(OP, "log/operator.jsonl")):
        e = json.loads(ln)
        if e.get("act") == act:
            rp = e.get("replay") or {}
            extra = f" replay(calls={rp.get('calls')}, turned={rp.get('turned')}, dropped={rp.get('dropped')})" if rp else ""
            print(f"  log {e.get('gate')} {e.get('result')} votes={e.get('votes')} commit={(e.get('commit') or '')[:12]}"
                  f" undo={e.get('undo')}{extra} {(e.get('reason') or '')[:240]}")
    pl = os.path.join(PH, ".config/gov-os-notify/pings.log")
    if os.path.exists(pl):
        for ln in open(pl):
            e = json.loads(ln)
            if e.get("act") == act:
                print(f"  notice {e.get('priority')} {e.get('kind')}: {str(e.get('line'))[:240]}")
elif STEP == "real-check":
    sys.path.insert(0, INST)
    import opcommon as oc        # the planted install's own code, as re-installed
    import operator_run as orun
    s = oc.load_settings(None)
    s["calls"] = os.path.realpath(ARGS[0])
    s["guard_calls"] = os.path.join("/home/usain", ".gov-os", "guard-calls")   # the real log, read only
    try:
        since, until, lines = orun.read_call_set(s)
        matched = orun.check_against_log(s, since, until, lines)
        days = sorted(f for f in os.listdir(s["guard_calls"]) if f.endswith(".jsonl"))
        first = None
        if days:
            with open(os.path.join(s["guard_calls"], days[0]), encoding="utf-8") as f:
                first = json.loads(f.readline()).get("time")
        print(json.dumps({"result": "the check passed", "window": [oc.iso(since), oc.iso(until)],
                          "set_lines": len(lines), "calls": sum(1 for c in lines if "event" in c),
                          "dropped": sum(1 for c in lines if "event" not in c), "matched": len(matched),
                          "log_days": days, "log_first_line": first}))
    except Exception as exc:     # a refusal: its reason (counts and hash prefixes only)
        print(json.dumps({"result": "refused", "reason": str(exc)[:600], "kind": type(exc).__name__}))
else:
    sys.exit(f"unknown step {STEP}")
