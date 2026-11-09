"""ACT-GUARD-CALLLOG-1: the rehearsal's checks of the guard's call log. Each command prints its findings and a last
line PASS or FAIL. Nothing here reads a protected file: the held-out list and the path map give names only, used as
arguments to the hook and never printed; the sets root used is the planted one in the clone's map.

  python3 calllog_check.py validate <log dir> [<expected lines>]
  python3 calllog_check.py planted  <clone> <log dir> <before hook> <pin python>
  python3 calllog_check.py faults   <clone> <work dir> <before hook> <pin python>
  python3 calllog_check.py prune    <clone> <work dir> <pin python>
  python3 calllog_check.py concurrent <clone> <work dir> <pin python>
  python3 calllog_check.py latency  <clone> <work dir> <before hook> <pin python> [runs]
  python3 calllog_check.py micro    <clone> <work dir>
  python3 calllog_check.py replay   <replay_walls.py> <clone> <log dir> <pass args...>   (the replay pass, recording)
  python3 calllog_check.py replaymatch <log dir> <recorded.json>
  python3 calllog_check.py live     <log dir> <stream.jsonl> <salt dir>
"""
import collections
import concurrent.futures
import hashlib
import hmac
import importlib.util
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import time

KEYS = {"v", "time", "session", "role", "agent", "ticket", "tool", "decision", "rule", "tree", "ms", "sha256", "keyed"}
RULES = {"none", "2-heldout", "2-hidden", "3-secret", "2-listing", "2-judge", "2b-line", "2b-write", "2c", "g14", "rm",
         "5", "1", "4-sudo", "4-ask", "4-install", "deadline", "error"}
NAME = re.compile(r"^[A-Za-z0-9._:-]{0,64}$")
HEX = re.compile(r"^[0-9a-f]{64}$")
TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")
MARK = "MARK-CALLLOG"
KEY = "salt" + ".key"
FAILS = []


def bad(msg):
    FAILS.append(msg)
    print("FAIL:", msg)


def finish():
    print("PASS" if not FAILS else f"FAIL ({len(FAILS)})")
    sys.exit(0 if not FAILS else 1)


def action_bytes(tool, tin):  # as the hook's, recomputed independently
    return json.dumps({"tool": tool, "input": tin}, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8", "surrogatepass")


def salt_of(d):
    try:
        s = open(os.path.join(d, KEY), "rb").read().strip()
        return bytes.fromhex(s.decode()) if re.fullmatch(rb"[0-9a-f]{64}", s) else None
    except OSError:
        return None


def rows_of(d):
    out = []
    for name in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if name.endswith(".jsonl"):
            for line in open(os.path.join(d, name), "rb").read().splitlines():
                out.append(line)
    return out


def validate_dir(d, expect=None, quiet=False):
    """Every line has exactly the keys, each value in its form; the folder 0700, its files 0600 (the salt 0400);
    nothing but the salt, day files and cap markers; no marker text anywhere. Returns the parsed rows."""
    st = os.stat(d)
    if st.st_mode & 0o777 != 0o700:
        bad(f"{d}: mode {oct(st.st_mode & 0o777)}, not 0700")
    for name in os.listdir(d):
        p = os.path.join(d, name)
        m = os.lstat(p).st_mode & 0o777
        if name == KEY:
            continue
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}\.jsonl(\.capped)?", name):
            bad(f"an unexpected file in the log folder: {name}")
        elif m != 0o600:
            bad(f"{name}: mode {oct(m)}, not 0600")
        if MARK.encode() in open(p, "rb").read():
            bad(f"{name} holds marker text from an action's input")
    rows = []
    for raw in rows_of(d):
        if len(raw) > 1024:
            bad(f"a line of {len(raw)} bytes")
        try:
            r = json.loads(raw)
        except ValueError:
            bad("a line that is not JSON: " + raw[:60].decode("ascii", "replace"))
            continue
        if set(r) != KEYS:
            bad(f"keys {sorted(set(r) ^ KEYS)}")
            continue
        ok = (r["v"] == 1 and TIME.match(r["time"]) and all(NAME.match(r[k]) for k in
              ("session", "role", "agent", "ticket", "tool")) and r["decision"] in ("allow", "deny", "ask")
              and r["rule"] in RULES and r["tree"] in ("main", "worktree", "run", "scratch", "other")
              and isinstance(r["ms"], int) and r["ms"] >= 0
              and (r["sha256"] is None or HEX.match(r["sha256"])) and (r["keyed"] is None or HEX.match(r["keyed"]))
              and (r["decision"] == "allow") == (r["rule"] == "none"))
        if not ok:
            bad("a line out of form: " + raw[:200].decode("ascii", "replace"))
        rows.append(r)
    if expect is not None and len(rows) != expect:
        bad(f"{len(rows)} lines, expected {expect}")
    if not quiet:
        c = collections.Counter((r["decision"], r["rule"]) for r in rows)
        print(f"{d}: {len(rows)} lines; by decision and rule: {dict(sorted(c.items()))}; "
              f"trees {dict(collections.Counter(r['tree'] for r in rows))}; "
              f"keyed null {sum(1 for r in rows if r['keyed'] is None)}")
    return rows


# -- the planted session ------------------------------------------------------------------------------------------

def setting_line(clone):
    return json.load(open(os.path.join(clone, ".claude", "settings.json")))["hooks"]["PreToolUse"][0]["hooks"][0]["command"]


def cases(clone):
    """(name, role, ticket, agent, tool, input or raw text, the rule expected). Names from the clone's own map and
    held-out list, used only as arguments."""
    import yaml
    home = os.path.realpath(os.path.expanduser("~"))
    pm = yaml.safe_load(open(os.path.join(clone, "governance", "project", "path-map.yaml")))
    sets = pm.get("evaluation_sets") or {}
    hidden_glob, measured = None, "engineer"
    for e in sets.values():
        if isinstance(e, dict) and e.get("hidden"):
            hidden_glob = e["hidden"][0]
            measured = (e.get("measures") or {}).get("roles", ["engineer"])[0]
            break
    hidden_file = hidden_glob.replace("**", "q01.yaml").replace("*", "q01")
    held = (yaml.safe_load(open(os.path.join(clone, "governance", "project", "held-out.yaml"))) or {}).get(
        "held_out_paths") or []
    block = pm["sets_root_hidden"]
    sr = os.path.realpath(os.path.expanduser(block["root"]))
    if not sr.startswith("/tmp/") and "/gov-os-runs/" not in sr:
        raise SystemExit("the clone's sets root is not the planted one: stop")
    refused = block["refused_roles"][0]
    head = block["hidden"][0].split("*")[0].rstrip("/")
    c = os.path.realpath(clone)
    m = "MARK-CALLLOG-"
    return [
        ("A1 Read, allowed", "engineer", "DAEO-sdxk", "", "Read", {"file_path": c + "/README.md"}, "none"),
        ("A2 Bash ls, allowed", "engineer", "DAEO-sdxk", "", "Bash", {"command": "ls docs | head -3"}, "none"),
        ("A3 Bash with marker, allowed", "engineer", "DAEO-sdxk", "", "Bash",
         {"command": f"echo {m}41 > /tmp/gov-calllog-x.txt", "description": f"{m}41b"}, "none"),
        ("A4 Write to /tmp with marker, allowed", "engineer", "DAEO-sdxk", "", "Write",
         {"file_path": "/tmp/gov-calllog-y.txt", "content": f"{m}42 hidden text stand-in"}, "none"),
        ("A5 Glob, allowed", "research", "DAEO-sdxk", "", "Glob", {"pattern": "*.md"}, "none"),
        ("A6 Edit docs by the CTO, allowed", "orchestrator", "DAEO-sdxk", "", "Edit",
         {"file_path": c + "/docs/zz-calllog.md", "old_string": f"{m}46", "new_string": "b"}, "none"),
        ("A7 TodoWrite, allowed", "engineer", "DAEO-sdxk", "", "TodoWrite",
         {"todos": [{"content": f"{m}43", "status": "pending", "activeForm": "x"}]}, "none"),
        ("A8 Grep by a subagent, allowed", "orchestrator", "DAEO-sdxk", "Explore", "Grep",
         {"pattern": f"{m}44", "path": c + "/src"}, "none"),
        ("D1 a secret, refused", "engineer", "DAEO-sdxk", "", "Read", {"file_path": c + "/x/.env"}, "3-secret"),
        ("D2 sudo, refused", "engineer", "DAEO-sdxk", "", "Bash", {"command": "sudo true"}, "4-sudo"),
        ("D3 an install, refused", "engineer", "DAEO-sdxk", "", "Bash", {"command": f"pip install {m.lower()}x"},
         "4-install"),
        ("D4 the acceptance tests by an engineer, refused", "engineer", "DAEO-sdxk", "", "Write",
         {"file_path": c + "/tests/acceptance/W2-64/t.py", "content": f"{m}45"}, "1"),
        ("D5 a reviewer's write outside its records, refused", "independent-auditor", "DAEO-sdxk", "", "Write",
         {"file_path": c + "/docs/zz-calllog.md", "content": "x"}, "5"),
        ("D6 a catastrophic rm, refused", "engineer", "DAEO-sdxk", "", "Bash", {"command": "rm -rf ~"}, "rm"),
        ("D7 an in-tree hidden half, refused", measured, "DAEO-sdxk", "", "Read", {"file_path": c + "/" + hidden_file},
         "2-hidden"),
        ("D8 the held-out material, refused", "engineer", "DAEO-sdxk", "", "Read",
         {"file_path": c + "/" + held[0].rstrip("*").rstrip("/")}, "2-heldout"),
        ("D9 the sets root with a variable after it, refused", refused, "DAEO-sdxk", "", "Bash",
         {"command": f"python3 tool.py --sets-root {sr} --part $PART"}, "2b-line"),
        ("D10 a write into the planted sets root's hidden part, refused", refused, "DAEO-sdxk", "", "Write",
         {"file_path": f"{sr}/{head}/zz-new.txt", "content": "x"}, "2b-write"),
        ("D11 the tuner's transcripts, refused", "engineer", "DAEO-wnnz", "", "Read",
         {"file_path": home + "/.claude/projects/zz-none.jsonl"}, "2c"),
        ("D12 the engineer's own acceptance tests, refused", "engineer", "DAEO-jpr0", "", "Read",
         {"file_path": c + "/tests/acceptance/W2-126/test_zz.py"}, "g14"),
        ("K1 an install in the CTO's session, asked", "orchestrator", "DAEO-sdxk", "", "Bash",
         {"command": "pip install zz-calllog"}, "4-ask"),
        ("E1 input that is not JSON, refused (fail closed)", "engineer", "DAEO-sdxk", "", None, "not json", "error"),
    ]


def event_text(case, sid, clone):
    _n, _r, _t, agent, tool, tin, _x = case
    if tool is None:
        return tin
    ev = {"tool_name": tool, "tool_input": tin, "cwd": os.path.realpath(clone), "session_id": sid,
          "hook_event_name": "PreToolUse", "transcript_path": "/tmp/zz.jsonl"}
    if agent:
        ev["agent_type"] = agent
    return json.dumps(ev)


def run_hook(clone, case, sid, py, hook=None, calls=None, extra=None, prefix="", home=None):
    """One call, as Claude Code makes it (the registered line), or the hook directly (``hook``). Returns (exit,
    stdout, stderr, seconds)."""
    _n, role, ticket, _a, _tool, _tin, _x = case
    env = {k: v for k, v in os.environ.items() if k not in ("GOV_ROLE", "GOV_TICKET", "PYTHONPATH")}
    env.update(CLAUDE_PROJECT_DIR=os.path.realpath(clone), GOV_ROLE=role, GOV_TICKET=ticket)
    env.pop("GOV_GUARD_CALLS_DIR", None)
    if calls is not None:
        env["GOV_GUARD_CALLS_DIR"] = calls
    if home:
        env["HOME"] = home
    env.update(extra or {})
    argv = ["bash", "-c", prefix + setting_line(clone)] if hook is None else [py, "-E", hook]
    t = time.monotonic()
    p = subprocess.run(argv, input=event_text(case, sid, clone), capture_output=True, text=True, env=env,
                       timeout=120, cwd=os.path.realpath(clone))
    return p.returncode, p.stdout, p.stderr, time.monotonic() - t


def decision_of(code, out):
    if code == 2:
        return "deny"
    if out.strip():
        return json.loads(out)["hookSpecificOutput"]["permissionDecision"]
    return "allow"


def planted(clone, d, before, py):
    sid = "calllog-planted-0001"
    cs = cases(clone)
    salt = salt_of(d)
    if salt is None:
        bad("the planted log folder has no valid salt")
    n0 = len(rows_of(d))
    results = []
    for c in cs:
        b = run_hook(clone, c, sid, py, hook=before)
        a = run_hook(clone, c, sid, py, calls=d)
        same = (b[0], b[1]) == (a[0], a[1])
        results.append((c, b, a))
        print(f"{'ok ' if same else 'DIFF'} {c[0]}: before {decision_of(b[0], b[1])}, after {decision_of(a[0], a[1])}")
        if not same:
            bad(f"{c[0]}: the decision changed (before {b[0]} {b[1][:80]!r}, after {a[0]} {a[1][:80]!r})")
        if "call log" in a[2]:
            bad(f"{c[0]}: a call-log warning with a writable folder: {a[2][:120]}")
    rows = validate_dir(d)[n0:]
    if len(rows) != len(cs):
        bad(f"{len(rows)} new lines for {len(cs)} calls")
    for (c, b, a), r in zip(results, rows):
        name, role, ticket, agent, tool, tin, rule = c
        want = {"decision": decision_of(a[0], a[1]), "rule": rule, "role": role, "ticket": ticket, "agent": agent,
                "tool": tool or "", "session": sid if tool else "", "tree": "run"}
        got = {k: r[k] for k in want}
        if got != want:
            bad(f"{name}: line {got} != {want}")
        if tool is None:
            if r["sha256"] is not None or r["keyed"] is not None:
                bad(f"{name}: a hash for input that is not JSON")
            continue
        raw = action_bytes(tool, tin)
        if r["sha256"] != hashlib.sha256(raw).hexdigest():
            bad(f"{name}: sha256 does not match the action recomputed")
        if salt and r["keyed"] != hmac.new(salt, raw, hashlib.sha256).hexdigest():
            bad(f"{name}: the keyed hash does not match")
        print(f"   line: {r['decision']} {r['rule']} {r['tool']} sha256 {r['sha256'][:12]} keyed {str(r['keyed'])[:12]}")
    files = sorted(os.listdir(d))
    print("log folder holds:", files)
    if [f for f in files if f != KEY and not f.endswith(".jsonl")]:
        bad("the log folder holds more than the salt and day files")
    # the same action on another day matches by both hashes: recompute for a case and compare with a second call
    a1 = run_hook(clone, cs[0], "calllog-planted-0002", py, calls=d)
    r2 = validate_dir(d, quiet=True)[-1]
    if r2["sha256"] != rows[0]["sha256"] or r2["keyed"] != rows[0]["keyed"] or r2["session"] != "calllog-planted-0002":
        bad("the same action in another session does not carry the same hashes")
    print(f"planted: {len(cs)} calls, {len(rows)} lines; decisions unchanged {sum(1 for _c, b, a in results if (b[0], b[1]) == (a[0], a[1]))}"
          f"/{len(cs)}; one more call (another session, same action): same sha256 and keyed hash")


# -- the faults ---------------------------------------------------------------------------------------------------

def faults(clone, work, before, py):
    """A log folder that cannot be written never changes a decision: each case's answer (exit, stdout) as with a
    working log, and the call log's one stderr line instead of a line in the log."""
    import pwd  # noqa: F401
    cs = cases(clone)
    sid = "calllog-faults"
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    ok_dir = os.path.join(work, "ok")
    os.makedirs(ok_dir, mode=0o700)
    salt = open(os.path.join(os.path.dirname(work), "calls", KEY)).read()
    open(os.path.join(ok_dir, KEY), "w").write(salt)
    base = {c[0]: run_hook(clone, c, sid, py, calls=ok_dir) for c in cs}
    day = time.strftime("%Y-%m-%d", time.gmtime())

    def mkdir(name, salted=True):
        p = os.path.join(work, name)
        os.makedirs(p, mode=0o700)
        if salted:
            open(os.path.join(p, KEY), "w").write(salt)
        return p

    setups = {}
    p = mkdir("readonly"); open(os.path.join(p, day + ".jsonl"), "w").close(); os.chmod(os.path.join(p, day + ".jsonl"), 0o400)
    os.chmod(p, 0o500); setups["F1 a read-only folder and day file"] = (p, "", None)
    p = mkdir("readonly-empty"); os.chmod(p, 0o500); setups["F1b a read-only folder, no day file yet"] = (p, "", None)
    p = mkdir("full"); open(os.path.join(p, day + ".jsonl"), "wb").write(b"x" * 4096)
    setups["F2 a full disk (the file size limit, EFBIG)"] = (p, "ulimit -f 2; ", None)
    p = mkdir("cap"); f = os.path.join(p, day + ".jsonl"); open(f, "wb").close(); os.truncate(f, 32 * 1024 * 1024)
    setups["F3 the day's cap reached"] = (p, "", None)
    p = os.path.join(work, "a-file"); open(p, "w").write("x"); setups["F4 the folder is a file"] = (p, "", None)
    p = mkdir("daylink"); tgt = os.path.join(work, "link-target.txt"); open(tgt, "w").write("target\n")
    os.symlink(tgt, os.path.join(p, day + ".jsonl")); setups["F5 the day file is a link"] = (p, "", None)
    real = mkdir("dir-target"); p = os.path.join(work, "dirlink"); os.symlink(real, p)
    setups["F6 the folder is a link"] = (p, "", None)
    p = mkdir("fifo"); os.mkfifo(os.path.join(p, day + ".jsonl")); setups["F7 a write that hangs (a FIFO)"] = (p, "", None)
    p = mkdir("nosalt", salted=False); setups["F8 no salt"] = (p, "", None)
    ph = os.path.join(work, "home"); os.makedirs(ph)
    setups["F9 a relative GOV_GUARD_CALLS_DIR (ignored: the default under HOME, planted)"] = ("relative/dir", "", ph)
    ro_home = os.path.join(work, "home-ro"); os.makedirs(ro_home); os.chmod(ro_home, 0o500)
    setups["F10 the default folder cannot be made (HOME read-only, planted)"] = (None, "", ro_home)

    summary = {}
    for name, (calls, prefix, home) in setups.items():
        diffs, warns, slow = 0, 0, 0.0
        for c in cs:
            ref = base[c[0]] if home is None else run_hook(clone, c, sid, py, hook=before, home=home)
            r = (run_hook(clone, c, sid, py, calls=calls, prefix=prefix) if home is None else
                 run_hook(clone, c, sid, py, hook=os.path.join(clone, ".claude", "hooks", "pretooluse.py"),
                          calls=calls, home=home))
            if (r[0], r[1]) != (ref[0], ref[1]):
                diffs += 1
                bad(f"{name}: {c[0]}: the decision changed ({ref[0]} -> {r[0]}; {r[2][-160:]!r})")
            warns += r[2].count("ACT-GUARD-CALLLOG-1")
            slow = max(slow, r[3] - (ref[3] if home is None else 0))
        summary[name] = (diffs, warns)
        print(f"{name}: {len(cs)} calls, decisions changed {diffs}, call-log warnings {warns}, slowest extra {slow:.2f} s")
    # what each fault left
    ro = os.path.join(work, "readonly")
    os.chmod(ro, 0o700)
    if os.path.getsize(os.path.join(ro, day + ".jsonl")) != 0:
        bad("F1: lines were written into a read-only day file")
    if os.listdir(os.path.join(work, "readonly-empty")) != [KEY]:
        bad("F1b: a file appeared in a read-only folder")
    os.chmod(os.path.join(work, "readonly-empty"), 0o700)
    if os.path.getsize(os.path.join(work, "full", day + ".jsonl")) != 4096:
        bad("F2: the full file grew")
    if os.path.getsize(os.path.join(work, "cap", day + ".jsonl")) != 32 * 1024 * 1024:
        bad("F3: the capped file grew")
    if not os.path.exists(os.path.join(work, "cap", day + ".jsonl.capped")):
        bad("F3: no cap marker")
    if open(tgt).read() != "target\n":
        bad("F5: the link's target was written")
    if os.listdir(real) != [KEY]:
        bad("F6: the linked folder's target was written")
    for name, (warn_expected, folder) in {"F1 a read-only folder and day file": (True, None),
                                          "F8 no salt": (False, os.path.join(work, "nosalt"))}.items():
        if warn_expected and summary[name][1] != len(cs):
            bad(f"{name}: {summary[name][1]} warnings for {len(cs)} calls (expected one per call)")
    rows = validate_dir(os.path.join(work, "nosalt"))
    if len(rows) != len(cs) or any(r["keyed"] is not None for r in rows):
        bad("F8: without a salt the lines must still be written, with keyed null")
    dflt = os.path.join(ph, ".gov-os", "guard-calls")
    rows = validate_dir(dflt) if os.path.isdir(dflt) else []
    if len(rows) != len(cs):
        bad(f"F9: {len(rows)} lines in the planted HOME's default folder for {len(cs)} calls")
    if os.path.exists(os.path.join(work, "relative")) or os.path.exists(os.path.join(clone, "relative")):
        bad("F9: a relative folder was made")
    os.chmod(ro_home, 0o700)
    print("faults: every decision as with a working log:", all(v[0] == 0 for v in summary.values()))


def prune(clone, work, py):
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work, mode=0o700)
    now = time.time()
    old = [time.strftime("%Y-%m-%d", time.gmtime(now - d * 86400)) for d in (93, 200, 400)]
    keep = [time.strftime("%Y-%m-%d", time.gmtime(now - d * 86400)) for d in (1, 91)]
    for n in old:
        open(os.path.join(work, n + ".jsonl"), "w").write("{}\n")
    open(os.path.join(work, old[0] + ".jsonl.capped"), "w").close()
    for n in keep:
        open(os.path.join(work, n + ".jsonl"), "w").write("{}\n")
    others = ["notes.txt", old[1] + ".jsonl.bak", "1999-01-01.json"]
    for n in others:
        open(os.path.join(work, n), "w").write("x")
    c = cases(clone)[0]
    run_hook(clone, c, "calllog-prune", py, calls=work)
    left = sorted(os.listdir(work))
    today = time.strftime("%Y-%m-%d", time.gmtime(now)) + ".jsonl"
    want = sorted([n + ".jsonl" for n in keep] + others + [today])
    print("prune: left", left)
    if left != want:
        bad(f"prune: left {left}, expected {want}")
    run_hook(clone, c, "calllog-prune", py, calls=work)  # a second call of the day prunes nothing more
    if sorted(os.listdir(work)) != want:
        bad("prune: the second call changed the folder")


def conc(clone, work, py, procs=8, each=25):
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work, mode=0o700)
    c = cases(clone)[2]  # a Bash call
    t = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(procs) as ex:
        list(ex.map(lambda i: run_hook(clone, c, f"calllog-conc-{i % procs}", py, calls=work), range(procs * each)))
    rows = validate_dir(work, procs * each)
    print(f"concurrent: {procs} at once, {procs * each} calls in {time.monotonic() - t:.1f} s, {len(rows)} whole lines")


def latency(clone, work, before, py, runs=40):
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work, mode=0o700)
    open(os.path.join(work, KEY), "w").write(open(os.path.join(os.path.dirname(work), "calls", KEY)).read())
    after = os.path.join(clone, ".claude", "hooks", "pretooluse.py")
    cs = [cases(clone)[i] for i in (0, 1, 9)]  # a Read and a Bash allowed, sudo refused
    t = {"before": [], "after": []}
    per = collections.defaultdict(lambda: {"before": [], "after": []})
    for i in range(runs):
        for c in cs:
            for which, hook in (("before", before), ("after", after)) if i % 2 == 0 else (("after", after), ("before", before)):
                r = run_hook(clone, c, "calllog-latency", py, hook=hook, calls=work)
                t[which].append(r[3])
                per[c[0]][which].append(r[3])

    def q(xs, p):
        xs = sorted(xs)
        return xs[min(len(xs) - 1, int(p * len(xs)))]

    for k in ("before", "after"):
        print(f"latency {k}: {len(t[k])} calls, median {statistics.median(t[k]) * 1000:.1f} ms, p95 {q(t[k], .95) * 1000:.1f} ms")
    for name, v in per.items():
        print(f"  {name}: median before {statistics.median(v['before']) * 1000:.1f} ms, after "
              f"{statistics.median(v['after']) * 1000:.1f} ms")
    print(f"latency added (median of all): {(statistics.median(t['after']) - statistics.median(t['before'])) * 1000:+.1f} ms")
    validate_dir(work, runs * len(cs))


def micro(clone, work, n=2000):
    """The log's own cost, in the process: _calls_write on a planted event, n times."""
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work, mode=0o700)
    open(os.path.join(work, KEY), "w").write(open(os.path.join(os.path.dirname(work), "calls", KEY)).read())
    os.environ["GOV_GUARD_CALLS_DIR"] = work
    sys.path.insert(0, os.path.join(clone, ".claude", "hooks"))
    spec = importlib.util.spec_from_file_location("calllog_hook", os.path.join(clone, ".claude", "hooks", "pretooluse.py"))
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    h._CALL["event"] = {"tool_name": "Bash", "tool_input": {"command": "ls -la docs | head -40", "description": "x" * 200},
                        "session_id": "calllog-micro"}
    h._CALL["root"] = clone
    t = time.perf_counter()
    for _ in range(n):
        h._calls_write("allow", "none")
    each = (time.perf_counter() - t) / n
    print(f"micro: _calls_write {n} times, {each * 1e6:.0f} us each")
    validate_dir(work, n, quiet=True)


# -- the replay and the live session -----------------------------------------------------------------------------

def replay(rw_path, clone, d, args):
    spec = importlib.util.spec_from_file_location("rw", rw_path)
    rw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rw)
    orig, seen = rw.judge, []

    def judge(hook, py, clone_, tool, tin, cwd, role, agent):
        dec, why = orig(hook, py, clone_, tool, tin, cwd, role, agent)
        seen.append([hashlib.sha256(action_bytes(tool, tin)).hexdigest(), dec])
        return dec, why

    rw.judge = judge
    os.environ["GOV_GUARD_CALLS_DIR"] = d
    rw.do_pass(*args)
    json.dump(seen, open(args[-1] + ".recorded.json", "w"))
    print(f"replay: {len(seen)} calls judged and recorded (sha256, decision)")


def replaymatch(d, recorded):
    seen = collections.Counter(tuple(x) for x in json.load(open(recorded)))
    rows = validate_dir(d)
    logged = collections.Counter((r["sha256"], r["decision"]) for r in rows)
    print(f"replaymatch: {sum(seen.values())} calls judged, {len(rows)} lines; (sha256, decision) pairs equal: "
          f"{seen == logged}; judged not logged {sum((seen - logged).values())}, logged not judged "
          f"{sum((logged - seen).values())}")
    if seen != logged:
        bad("the replay's calls and the log's lines differ")


def live(d, stream, saltdir):
    salt = salt_of(saltdir)
    uses, results, sid = [], {}, None
    for line in open(stream, encoding="utf-8"):
        try:
            m = json.loads(line)
        except ValueError:
            continue
        sid = m.get("session_id") or sid
        msg = m.get("message") or {}
        for x in msg.get("content") or [] if isinstance(msg, dict) else []:
            if isinstance(x, dict) and x.get("type") == "tool_use":
                uses.append((x["id"], x["name"], x.get("input")))
            if isinstance(x, dict) and x.get("type") == "tool_result":
                text = x.get("content") if isinstance(x.get("content"), str) else json.dumps(x.get("content"))
                results[x.get("tool_use_id")] = "deny" if "DEC-953 item 2" in text else "allow"
    rows = [r for r in validate_dir(d) if r["session"] == sid]
    print(f"live: session {sid}: {len(uses)} tool calls in the stream, {len(rows)} lines for the session")
    by = collections.defaultdict(list)
    for r in rows:
        by[r["sha256"]].append(r)
    matched = 0
    for uid, name, tin in uses:
        raw = action_bytes(name, tin)
        h = hashlib.sha256(raw).hexdigest()
        if not by.get(h):
            bad(f"live: {name} call {uid}: no line with its sha256 (the hook's input differs from the stream's)")
            continue
        r = by[h].pop(0)
        matched += 1
        k = hmac.new(salt, raw, hashlib.sha256).hexdigest() if salt else None
        ok = r["tool"] == name and r["keyed"] == k and results.get(uid, r["decision"]) == r["decision"]
        print(f"  {'ok ' if ok else 'BAD'} {name}: line {r['decision']} {r['rule']} (the stream's result: {results.get(uid)})")
        if not ok:
            bad(f"live: {name} call {uid}: line {r} vs result {results.get(uid)}")
    extra = sum(len(v) for v in by.values())
    print(f"live: matched {matched} of {len(uses)} by sha256; lines with no call {extra}; roles "
          f"{sorted({r['role'] for r in rows})}, tickets {sorted({r['ticket'] for r in rows})}")
    if extra:
        bad(f"live: {extra} lines match no call in the stream")
    if not uses:
        bad("live: the session made no tool call")


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a.pop(0)
    if cmd == "validate":
        validate_dir(a[0], int(a[1]) if len(a) > 1 else None)
    elif cmd == "planted":
        planted(*a)
    elif cmd == "faults":
        faults(*a)
    elif cmd == "prune":
        prune(*a)
    elif cmd == "concurrent":
        conc(*a)
    elif cmd == "latency":
        latency(a[0], a[1], a[2], a[3], int(a[4]) if len(a) > 4 else 40)
    elif cmd == "micro":
        micro(*a)
    elif cmd == "replay":
        replay(a[0], a[1], a[2], a[3:])
    elif cmd == "replaymatch":
        replaymatch(*a)
    elif cmd == "live":
        live(*a)
    else:
        sys.exit(__doc__)
    finish()
