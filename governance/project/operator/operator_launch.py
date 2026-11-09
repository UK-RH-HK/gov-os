#!/usr/bin/env python3
"""The operator agent's launcher (OPERATOR-AGENT-1 §1, S17, S18, DEC-1104 (2)), run by the dispatcher's cron line.

    python3 operator_launch.py [--config <file.json>]

In order: the APPROVED check (any install file off its line refuses every launch); the lock of a failed undo (held:
nothing runs); the journal first (a session that died mid-apply: its ACT undone, a P1 pushed); then the oldest
request in queue/*.req (one line `ACT-<id> <64 hex>`; a malformed one is refused and moved aside to queue/rejected/);
the holds (it does not start a session while G9 would hold); the wall built in <operator root>/wall/ from the
install's wall template (never the root itself); the canary (a one-turn session in the wall whose Read outside the
wall must come back in its permission_denials, else the launch refuses before the real session); then the walled
session: `claude -p --restricted --settings <wall>/.claude/settings.json ...` from the wall, with a clean environment
(no GOV_*, no CLAUDE_PROJECT_DIR), in its own process group, its pid and pgid recorded, waited on by its pid and
stopped only by its pgid (L-0075). The request is the only input the CTO gives; the session can pass no gate the
program refuses. The result is the last line of stdout, one JSON object; exit 0 when launched (or idle, held, busy).
"""
import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import opcommon as oc  # noqa: E402
import operator_run  # noqa: E402

REQ_RE = re.compile(r"^(ACT-[A-Za-z0-9][A-Za-z0-9._-]{0,80}) ([0-9a-f]{64})\n?$")
TOOLS = "Bash,Read,Grep,Glob,TodoWrite"
PROMPT = ("Follow brief.md in this folder exactly. The request is in request.txt: run the one command it names and "
          "report the program's last line.")
CANARY_PROMPT = "Use the Read tool to read the file {target} and reply with its first line only."


def base_cmd(s, wall, budget, model):
    return [s["claude"], "-p", "--restricted", "--settings", os.path.join(wall, ".claude", "settings.json"),
            "--no-session-persistence", "--strict-mcp-config", "--max-budget-usd", budget,
            "--disable-slash-commands", "--permission-prompts", "none", "--tools", TOOLS, "--model", model,
            "--output-format", "json"]


def oldest_request(s):
    q = os.path.join(s["operator_root"], "queue")
    if not os.path.isdir(q):
        return None
    entries = []
    with os.scandir(q) as it:
        for e in it:
            if e.name.endswith(".req"):
                try:
                    st = e.stat(follow_symlinks=False)
                except OSError:
                    continue
                entries.append((st.st_mtime_ns, e.name, e.path, e))
    if not entries:
        return None
    entries.sort(key=lambda x: (x[0], x[1]))
    return entries[0]


def read_request(entry):
    path, e = entry[2], entry[3]
    if e.is_symlink() or not e.is_file(follow_symlinks=False):
        return None
    try:
        with open(path, "rb") as f:
            raw = f.read(4097)
        m = REQ_RE.match(raw.decode("ascii")) if len(raw) <= 4096 else None
    except (OSError, UnicodeDecodeError):
        return None
    return (m.group(1), m.group(2)) if m else None


def move(path, folder, s):
    """Moved under queue/<folder>/<stamp>-<pid>/, keeping its own name (never the queue's top level)."""
    stamp = time.strftime("%Y%m%dT%H%M%S")
    dst_dir = oc.ensure_dir(os.path.join(s["operator_root"], "queue", folder, f"{stamp}-{os.getpid()}"))
    dst = os.path.join(dst_dir, os.path.basename(path))
    os.rename(path, dst)
    return dst


def fill(template, values):
    out = template
    for k, v in values.items():
        out = out.replace(f"@{k}@", json.dumps(str(v))[1:-1])
    if re.search(r"@[A-Z_]+@", out):
        raise ValueError("the wall template holds an unfilled field")
    return out


def build_wall(s, act, sha):
    """The wall: <operator root>/wall/, its .claude/settings.json (a non-empty deny list and the PreToolUse hook), the
    hook, wall.json, the brief and the request; read-only. Never the operator root itself."""
    root = s["operator_root"]
    wall = os.path.join(root, "wall")
    if os.path.realpath(wall) == os.path.realpath(root):
        raise ValueError("the wall would be the operator root")
    oc.remove_tree(wall)
    os.makedirs(os.path.join(wall, ".claude"))
    inst = s["install"]
    frozen = os.path.join(root, "acts", f"{act}-{sha[:12]}")
    sid, transcript = oc.transcript_path(s)
    values = {"MODEL": s["model"], "INSTALL": inst, "ACT": act, "SHA": sha, "FROZEN": frozen, "WALL": wall,
              "TRANSCRIPT": transcript or os.path.join(wall, "no-transcript"), "HOME": s["home"], "REPO": s["repo"]}
    with open(os.path.join(inst, "wall", "settings.json.tmpl"), encoding="utf-8") as f:
        settings = fill(f.read(), values)
    parsed = json.loads(settings)
    if not parsed.get("permissions", {}).get("deny") or not parsed.get("hooks", {}).get("PreToolUse"):
        raise ValueError("the wall's settings have no deny list or no PreToolUse hook")
    files = {
        os.path.join(wall, ".claude", "settings.json"): settings.encode("utf-8"),
        os.path.join(wall, ".claude", "operator_wall_hook.py"):
            open(os.path.join(inst, "wall", "operator_wall_hook.py"), "rb").read(),
        os.path.join(wall, ".claude", "wall.json"): json.dumps({
            "install": inst, "operator_root": root, "repo": s["repo"], "home": s["home"], "act": act, "sha": sha,
            "frozen": frozen, "bundle": os.path.join(s["scratch"], "acts", act), "transcript": transcript,
            "session": sid}, indent=1).encode("utf-8"),
        os.path.join(wall, "brief.md"): open(os.path.join(inst, "brief.md"), "rb").read(),
        os.path.join(wall, "request.txt"): (
            f"{act} {sha}\ninstall {inst}\ncommand: python3 {inst}/operator_run.py run {act} {sha}\n").encode(),
        os.path.join(wall, "CLAUDE.md"): (
            "This session is the Gov OS operator agent (OPERATOR-AGENT-1, DEC-1104 (2)), in its own walled folder.\n"
            "It follows brief.md in this folder exactly; the brief is fixed and approved by the owner (sha256 "
            f"{oc.sha256_file(os.path.join(inst, 'brief.md'))}).\n"
            "It runs one program on one request and reports its last line; it writes nothing.\n").encode(),
    }
    for p, data in files.items():
        with open(p, "wb") as f:
            f.write(data)
    oc.make_read_only(wall)
    return wall


def denied_outside(out_bytes, wall):
    """True when the session's JSON output holds a Read outside the wall in its permission_denials."""
    text = out_bytes.decode("utf-8", "replace").strip()
    docs = []
    try:
        docs.append(json.loads(text))
    except ValueError:
        for ln in text.splitlines():
            try:
                docs.append(json.loads(ln))
            except ValueError:
                continue
    wall = os.path.realpath(wall)
    for d in docs:
        items = d if isinstance(d, list) else [d]
        for doc in items:
            if not isinstance(doc, dict):
                continue
            for den in doc.get("permission_denials") or []:
                if not isinstance(den, dict) or den.get("tool_name") != "Read":
                    continue
                tin = den.get("tool_input") or {}
                p = tin.get("file_path") or tin.get("path")
                if isinstance(p, str) and p:
                    rp = os.path.realpath(os.path.join(wall, os.path.expanduser(p)))
                    if not (rp == wall or rp.startswith(wall + "/")):
                        return True
    return False


def start(cmd, wall, env, record=None):
    p = subprocess.Popen(cmd, cwd=wall, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, start_new_session=True)
    pgid = os.getpgid(p.pid)
    if record:
        oc.write_atomic(record, json.dumps({"pid": p.pid, "pgid": pgid, "argv": cmd, "cwd": wall,
                                            "started": time.strftime("%Y-%m-%dT%H:%M:%S%z")}) + "\n")
    return p, pgid


def wait(p, timeout):
    """Wait on the child by its own pid; on a timeout stop its group by its pgid only (never a name match)."""
    try:
        out, err = p.communicate(timeout=timeout)
        return p.returncode, out, err
    except subprocess.TimeoutExpired:
        oc.stop_group(p.pid)
        try:
            out, err = p.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            out, err = b"", b""
        return 124, out, err


def canary(s, wall, env):
    tmp = tempfile.mkdtemp(prefix="gov-operator-canary-")
    try:
        target = os.path.join(tmp, "canary-target.txt")
        with open(target, "w") as f:
            f.write("canary: this Read must be refused by the wall\n")
        cmd = base_cmd(s, wall, s["canary_budget_usd"], s["canary_model"]) + [CANARY_PROMPT.format(target=target)]
        p, _ = start(cmd, wall, env)
        rc, out, err = wait(p, s["canary_timeout_s"])
        return denied_outside(out, wall), rc
    finally:
        oc.remove_tree(tmp)


def main(argv):
    approved = oc.approved_state()
    base = {"approved_sha256": approved[1]}
    try:
        config = None
        if argv[:1] == ["--config"] and len(argv) == 2:
            config = argv[1]
        elif len(argv) == 1 and argv[0].startswith("--config="):
            config = argv[0].split("=", 1)[1]
        elif argv:
            raise ValueError("usage: operator_launch.py [--config <file.json>]")
        s = oc.load_settings(config)
    except (ValueError, OSError) as exc:
        oc.finish(dict(base, result="refused", gate="request", reason=str(exc)), 2)
    if not approved[0]:
        oc.log_event(s, None, None, "approved", "refused", reason=approved[2])
        oc.finish(dict(base, result="refused", gate="approved", reason="APPROVED mismatch: " + approved[2]), 1)
    if os.path.exists(operator_run.lock_path(s)):
        oc.finish(dict(base, result="refused", gate="lock",
                       reason="an undo failed earlier: the lock is held; nothing is launched"), 1)
    oc.ensure_dir(s["log_dir"])
    lockf = open(os.path.join(s["log_dir"], "launch.lock"), "a")
    try:
        fcntl.flock(lockf.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        oc.finish(dict(base, result="busy", reason="another launch is running"), 0)
    recovered = None
    if os.path.exists(operator_run.journal_path(s)):
        res, code = operator_run.recover(s, approved)
        if code != 0:
            oc.finish(dict(res, approved_sha256=approved[1]), code)
        recovered = res
    extra = {"recovered": recovered} if recovered else {}
    entry = oldest_request(s)
    if entry is None:
        oc.finish(dict(base, result="recovered" if recovered else "idle", **extra), 0)
    req = read_request(entry)
    if req is None:
        moved = move(entry[2], "rejected", s)
        oc.log_event(s, None, None, "queue", "refused", reason="a malformed request, moved aside",
                     request=os.path.basename(entry[2]), moved_to=os.path.relpath(moved, s["operator_root"]))
        oc.finish(dict(base, result="refused", gate="queue", reason="a malformed request line, moved aside",
                       request=None, moved_to=os.path.relpath(moved, s["operator_root"]), **extra), 1)
    act, sha = req
    request = {"act": act, "sha256": sha}
    why = oc.holds(s)
    if why:
        oc.finish(dict(base, result="held", gate="G9", reason="; ".join(why), request=request, **extra), 0)
    try:
        wall = build_wall(s, act, sha)
    except (OSError, ValueError) as exc:
        oc.log_event(s, act, sha, "wall", "refused", reason=str(exc))
        oc.finish(dict(base, result="refused", gate="wall", reason=f"the wall cannot be built ({exc})",
                       request=request, **extra), 1)
    env = oc.clean_env(s, s["home"])
    ok, crc = canary(s, wall, env)
    if not ok:
        oc.log_event(s, act, sha, "canary", "refused", reason="the canary's Read outside the wall was not refused",
                     notice="canary")
        oc.notify(s, act, "P1", "canary", f"{act}: the wall's settings did not load (the canary's Read was not "
                                          "refused); no session started", manifest_sha256=sha)
        oc.finish(dict(base, result="refused", gate="canary",
                       reason="the canary's Read outside the wall was not refused: the wall's settings did not load",
                       request=request, **extra), 1)
    taken = move(entry[2], "taken", s)
    record = os.path.join(s["log_dir"], "session.json")
    cmd = base_cmd(s, wall, s["budget_usd"], s["model"]) + [PROMPT + f" Request: {act} {sha}."]
    p, pgid = start(cmd, wall, env, record)
    rc, out, err = wait(p, s["session_timeout_s"])
    try:
        oc.write_atomic(os.path.join(s["log_dir"], "session-output.json"), out or b"")
    except OSError:
        pass
    try:
        move(taken, "done", s)
    except OSError:
        pass
    session = {"pid": p.pid, "pgid": pgid, "exit": rc}
    oc.log_event(s, act, sha, "launch", "launched", session=session)
    oc.finish(dict(base, result="launched", request=request, session=session, **extra), 0)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except SystemExit:
        raise
    except Exception as exc:  # fail closed
        oc.finish({"result": "refused", "gate": "error", "reason": f"{exc.__class__.__name__}: {exc}",
                   "approved_sha256": oc.approved_state()[1]}, 1)
