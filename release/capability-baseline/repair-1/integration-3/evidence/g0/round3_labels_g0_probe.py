#!/usr/bin/env python3
"""P2-AR-0041 (round-3 integration) — G0 behaviour of the command labels round 3 added or re-classified, observed
through the integrated binary (integration evidence only, Contract v3 O3). Labels: `trust reseal` (Write,
reseal_t2_bindings L4), `trust reseal --dry-run` (Read), `task generate` (Write, replan_tasks L2), `task generate
--dry-run` (Read), `release record` (Write, record_release L2), and a research write (`research record`, Write,
record_research_evidence L1). `trust bind` is outside the project domain (machine trust) and not driven here.

R1  under FREEZE_WRITES and under PAUSE: every Write label is refused FROZEN / PAUSED and changes no tracked file;
    the Read labels are not refused by the control and change no tracked file.
R2  unfrozen: an undeclared invocation (no role) of a Write label is refused AUTHORITY_DENIED (no default role).
R3  the post-command work generation does not run after a refused command (no new task record appears).
Env: GOV, SCRATCH. Private unprovisioned machine under SCRATCH; bootstrap install of the binary's embedded payload.
"""
import hashlib, json, os, subprocess

GOV, SCR = os.environ["GOV"], os.environ["SCRATCH"]
os.makedirs(SCR, exist_ok=True)
proj = None
env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_") and not k.startswith("XDG_")}
env.update({"HOME": os.path.join(SCR, "home"), "XDG_STATE_HOME": os.path.join(SCR, "state"),
            "XDG_CACHE_HOME": os.path.join(SCR, "cache"), "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_AUTHOR_NAME": "p", "GIT_AUTHOR_EMAIL": "p@example.invalid",
            "GIT_COMMITTER_NAME": "p", "GIT_COMMITTER_EMAIL": "p@example.invalid"})
os.makedirs(env["HOME"], exist_ok=True)
RES = []


def check(name, ok, what, detail=""):
    RES.append((name, bool(ok)))
    print(f"CHECK {name} {'PASS' if ok else 'FAIL'} {what} -- {json.dumps(detail)[:300]}", flush=True)


def git(*a):
    return subprocess.run(["git", *a], cwd=proj, env=env, capture_output=True, text=True)


def g(*a, role="orchestrator"):
    base = [GOV, "--json", "--root", proj, "--session", "S-g0r3"] + (["--role", role] if role else [])
    r = subprocess.run(base + list(a), cwd=proj, env=env, capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except Exception:
        d = {"ok": False, "error": {"code": "NO_JSON", "message": (r.stdout + r.stderr)[-300:]}}
    return d


def code(d):
    return (d.get("error") or {}).get("code")


def tracked_digest():
    files = git("ls-files", "-co", "--exclude-standard").stdout.split()
    h = hashlib.sha256()
    for f in sorted(files):
        if f.startswith(".governance-runtime/") or f.startswith(".governance-state/"):
            continue
        try:
            h.update(f.encode() + b"\0" + open(os.path.join(proj, f), "rb").read())
        except FileNotFoundError:
            pass
    return h.hexdigest()


def tasks():
    return sorted(x for x in os.listdir(os.path.join(proj, "spec", "tasks")) if x.startswith("TASK-")) \
        if os.path.isdir(os.path.join(proj, "spec", "tasks")) else []


def fresh(tag):
    global proj
    proj = os.path.join(SCR, tag)
    os.makedirs(os.path.join(proj, "src"), exist_ok=True)
    open(os.path.join(proj, "README.md"), "w").write("# g0 probe\n")
    open(os.path.join(proj, "src", "lib.rs"), "w").write("pub fn f() {}\n")
    git("init", "-q"); git("add", "-A"); git("commit", "-qm", "baseline")
    assert g("init", "--name", tag, "--alias", tag).get("ok")
    git("add", "-A"); git("commit", "-qm", "installed")
    assert g("rebuild-memory").get("ok")


RESEARCH = json.dumps({"question": "why?", "reason": "probe", "method": "reading", "sources": ["README.md"],
                       "measurements": {}, "uncertainty": "low", "conclusion": "because", "confidence": 0.5})
WRITES = {
    "trust reseal": (["trust", "reseal"], "orchestrator"),
    "task generate": (["task", "generate"], "orchestrator"),
    "release record": (["release", "record", "--version", "0.1.0", "--title", "first"], "release-agent"),
    "research record": (["research", "record", "--fields", RESEARCH], "research-agent"),
}
READS = {
    "trust reseal --dry-run": ["trust", "reseal", "--dry-run"],
    "task generate --dry-run": ["task", "generate", "--dry-run"],
}
for control, expect in (("freeze-writes", "FROZEN"), ("pause", "PAUSED")):
    fresh(f"g0r3-{expect.lower()}")
    d = g(control, "--reason", "g0 probe")
    print(f"# {control}: ok={d.get('ok')} code={code(d)}", flush=True)
    check(f"R1.{expect}.control", d.get("ok"), f"`{control}` in force", code(d))
    before, t_before = tracked_digest(), tasks()
    for label, (args, role) in WRITES.items():
        r = g(*args, role=role)
        check(f"R1.{expect}.{label}", code(r) == expect and tracked_digest() == before,
              f"`{label}` (Write) is refused {expect} under {control} and changes no tracked file", code(r))
    for label, args in READS.items():
        r = g(*args)
        check(f"R1.{expect}.{label}", code(r) not in ("FROZEN", "PAUSED", "G0_UNCLASSIFIED") and tracked_digest() == before,
              f"`{label}` (Read) is not refused by {control} and changes no tracked file", {"ok": r.get("ok"), "code": code(r)})
    check(f"R3.{expect}", tasks() == t_before, f"no work generated after the commands refused under {control}", tasks())
fresh("g0r3-authority")
before = tracked_digest()
for label, (args, role) in WRITES.items():
    r = g(*args, role=None)
    check(f"R2.{label}", code(r) == "AUTHORITY_DENIED" and tracked_digest() == before,
          f"`{label}` without a declared role is refused AUTHORITY_DENIED (no default role)", code(r))
p = sum(1 for _, ok in RES if ok)
print(f"SUMMARY total={len(RES)} pass={p} fail={len(RES) - p} failed={[n for n, ok in RES if not ok]}", flush=True)
