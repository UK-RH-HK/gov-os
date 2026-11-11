"""W2-148's trial on past ACTs (S23, OPERATOR-AGENT-1 §7 step 3): the classifier on every ACT file, 8 applied ACTs
replayed end to end, 7 planted faults, and the live files hashed before and after. Everything runs in temporary
folders: clones of this repository, a planted operator root, HOME, scratch, transcript and clock, stub push and
crontab channels. Nothing live is written; no `claude` is started.

    python3 tests/unit/operator/test_w2_148_unit_trial.py --out <result.json> [--part classify|replays|faults|all]

The pytest test below runs the classification part only (cheap): no ACT file classed lower than the table.

How each ACT becomes a manifest (read from its own files and commits): the repository files of its applying commits
(test_w2_148_trial_acts.json, extracted from the ACT files and `git log`) with their bytes before and after from git;
the paths it names outside a commit (untracked repository files, HOME files, crontab) with placeholder bytes (so a
list-shaped one is never (a)); its fenced code blocks as `commands`; and one stand-in command line per step its text
names that a code block does not show (a Windows-side step, sudo, an install, a download, a deletion outside the
project), marked as such.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OPDIR = REPO / "governance" / "project" / "operator"
PKG = REPO / "governance" / "project" / "orchestration" / "packages"
ACTS_JSON = HERE / "test_w2_148_trial_acts.json"
COUNTED_AT = "116c2b413"
CLOCK = "2026-11-10T12:00:00+01:00"
REVIEW_TIME = "2026-11-10T10:00:00+01:00"
YES_TIME = "2026-11-10T10:30:00+00:00"
sys.path.insert(0, str(OPDIR))
sys.dont_write_bytecode = True
import act_class  # noqa: E402

RANK = {"a": 0, "b": 1, "O": 2}
# OPERATOR-AGENT-1 §2's example column, at its row's class (N-6): the pinned subset.
TABLE = {}
for a in ("1-GUARD", "GUARD-FIX-1", "GUARD-FIX-2", "GUARD-FIX-3", "GUARD-FIX-4", "G14", "G14b", "INDEP-WALLS-1",
          "GUARD-SETS-1", "PERMISSIONS-1", "PERMISSIONS-2", "QUIET-DENY-1", "STOP-WAITER-1", "PUSH-INPUT-1",
          "SELECT-HOOK-1", "SELECT-FIXES-1", "GATE-CONFIG-1", "NIGHTLY-1", "NIGHTLY-STOP-1", "SCHEDULE-STOP-2",
          "DISPATCH-CRON-2", "DISPATCHER-1", "RUNS-SWEEP-1", "DEADMAN-1", "SENTINEL-1", "RERANK-TRIAL-1",
          "RERANK-TRIAL-2"):
    TABLE["ACT-" + a] = "b"
for a in ("W1-01-EXEMPT-1", "W2-57-LS-1", "P-TRACE-IMPL-1", "REPIN-1", "REPIN-2", "REPIN-EMERGENCY-1", "REPIN-W2",
          "REPIN-W3", "REPIN-W4", "WSL-INTEROP-1", "NIGHTLY-0400", "D8"):
    TABLE["ACT-" + a] = "O"
# Not pinned (N-6): the servers' and SANDBOX-SEAL-1's (a) rows and the walled sessions' "none" rows; and the ACTs
# the table does not name. Their table reading, for the rises' list only.
UNPINNED = {"ACT-OLLAMA-CAP-1": "a", "ACT-QUERY-CPUS-1": "a", "ACT-QUERY-GPU-1": "a", "ACT-QUERY-GPU-2": "a",
            "ACT-RERANK-GPU-SLOTS-1": "a", "ACT-RERANK-WAIT-1": "a", "ACT-RERANK-CPU-1": "a",
            "ACT-SANDBOX-SEAL-1": "a", "ACT-HLABEL-1": "none", "ACT-HLABEL-2": "none", "ACT-HLABEL-3": "none",
            "ACT-HNEW-1": "none", "ACT-MSET-1": "none", "ACT-MSET-2": "none", "ACT-MSET-3": "none",
            "ACT-MSET-4": "none", "ACT-D4-RESTORE-1": "a", "ACT-GATE-CONFIG-1": "b", "ACT-PATHMAP-NS-1": "b"}
FLAG_LINES = {
    "sudo": "sudo true  # stand-in: the ACT's text names a sudo step",
    "windows": "powershell.exe -NoProfile -Command x  # stand-in: the ACT's text names a Windows-side step",
    "push": "git push  # stand-in: the ACT's text names a push",
    "tag": "git tag x  # stand-in: the ACT's text names a tag",
    "install": "pip install x  # stand-in: the ACT's text names an install",
    "network": "curl -s https://example.org/x  # stand-in: the ACT's text names a download",
    "rm-outside": "rm -rf ~/x  # stand-in: the ACT's text names a deletion outside the project",
}
REPLAYS = [("ACT-SELECT-FIXES-1", "b"), ("ACT-SELECT-HOOK-1", "b"), ("ACT-GUARD-SETS-1", "b"),
           ("ACT-PERMISSIONS-2", "b"), ("ACT-NIGHTLY-STOP-1", "b"), ("ACT-OLLAMA-CAP-1", "a"),
           ("ACT-W1-01-EXEMPT-1", "O"), ("ACT-D8", "O")]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def git(*args, cwd=REPO, check=True):
    r = subprocess.run(["git", "-C", str(cwd)] + list(args), capture_output=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {args}: {r.stderr.decode()[:300]}")
    return r.stdout


def write(p, data, mode=None):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data if isinstance(data, bytes) else data.encode())
    if mode:
        os.chmod(p, mode)
    return p


def code_blocks(text):
    return re.findall(r"```[^\n]*\n(.*?)```", text, re.S)


def act_files():
    return sorted(p for p in PKG.glob("ACT-*.md"))


def counted():
    out = git("ls-tree", "--name-only", f"{COUNTED_AT}:governance/project/orchestration/packages/").decode().split()
    return {n[:-3] for n in out if n.startswith("ACT-") and n.endswith(".md")}


def commit_changes(commits):
    """{path: (before bytes or None, after bytes or None)} over the applying commits (first parent each)."""
    out = {}
    for c in commits:
        for ln in git("show", "--no-renames", "--name-status", "--format=", c).decode().splitlines():
            parts = ln.split("\t")
            if len(parts) != 2:
                continue
            st, path = parts
            before = None if st.startswith("A") else git("show", f"{c}^:{path}")
            after = None if st.startswith("D") else git("show", f"{c}:{path}")
            if path in out:
                out[path] = (out[path][0], after)
            else:
                out[path] = (before, after)
    return out


def act_manifest(entry, bundle, text, repo_only_commit=False):
    """A manifest for one ACT, its before/ and after/ in the bundle folder."""
    changes = commit_changes(entry["commits"])
    touched = []

    def add(root, path, before, after):
        path = path.rstrip("/")
        if not path or any((t["root"], t["path"]) == (root, path) for t in touched):
            return
        if before is not None:
            write(bundle / "before" / root / path, before)
        if after is not None:
            write(bundle / "after" / root / path, after)
        touched.append({"root": root, "path": path, "before": sha(before) if before is not None else None,
                        "after": sha(after) if after is not None else None})

    for path, (b, a) in changes.items():
        add("repo", path, b, a)
    for path in entry["repo_paths"]:
        if path.rstrip("/") not in changes:
            add("repo", path, b"before: " + path.encode(), b"after: " + path.encode())
    for path in entry["home_paths"]:
        add("home", path, b"before: " + path.encode(), b"after: " + path.encode())
    if entry["crontab"]:
        add("crontab", "crontab", b"before: crontab\n", b"after: crontab\n")
    commands = [blk for blk in code_blocks(text)]
    commands += [FLAG_LINES[f] for f in entry["flags"] if f in FLAG_LINES]
    return {"act": entry["act"], "touched": touched, "commands": commands, "checks": []}


# ------------------------------------------------------------------------------------------------- A: classification
def classify_all():
    entries = {e["act"]: e for e in json.loads(ACTS_JSON.read_text())}
    at = counted()
    rows, rises, lower = [], [], []
    tmp = Path(tempfile.mkdtemp(prefix="w2-148-trial-classify-"))
    try:
        for f in act_files():
            act = f.stem
            entry = entries.get(act) or {"act": act, "commits": [], "repo_paths": [], "home_paths": [],
                                         "crontab": False, "flags": [], "kind": "(not in the extraction)"}
            bundle = tmp / act
            m = act_manifest(entry, bundle, f.read_text(errors="replace"))
            res = act_class.classify_manifest(m, str(bundle))
            want = TABLE.get(act)
            rows.append({"act": act, "class": res["class"], "table": want or UNPINNED.get(act, "not named"),
                         "pinned": want is not None, "in_54": act in at, "kind": entry["kind"], "why": res["why"]})
            ref = want or UNPINNED.get(act)
            if want is not None and RANK[res["class"]] < RANK[want]:
                lower.append(act)
            if ref in RANK and RANK[res["class"]] > RANK[ref]:
                rises.append({"act": act, "from": ref, "to": res["class"], "pinned": want is not None,
                              "why": res["why"]})
            elif ref == "none":
                rises.append({"act": act, "from": "none", "to": res["class"], "pinned": False, "why": res["why"]})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    counts = {c: sum(1 for r in rows if r["class"] == c) for c in ("a", "b", "O")}
    return {"rows": rows, "counts": counts, "rises": rises, "lower": lower, "files": len(rows),
            "in_54": sum(1 for r in rows if r["in_54"]), "later": sorted(r["act"] for r in rows if not r["in_54"])}


# ---------------------------------------------------------------------------------------------- the planted operator
APPLY_SH = r'''#!/bin/bash
# The trial's apply.sh: check, apply, undo by list.txt from its own folder (cwd the repository, HOME the HOME).
set -u
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
step="${1:-}"
h() { if [ -f "$1" ]; then sha256sum "$1" | cut -c1-64; else echo null; fi; }
while IFS='|' read -r root path before after; do
  [ -z "$root" ] && continue
  if [ "$root" = crontab ]; then
    cur=$(crontab -l 2>/dev/null | sha256sum | cut -c1-64); crontab -l >/dev/null 2>&1 || cur=null
    case "$step" in
      check) [ "$cur" = "$before" ] || exit 3 ;;
      apply) crontab "$B/after/crontab/crontab" ;;
      undo) if [ "$before" = null ]; then crontab -r; else crontab "$B/before/crontab/crontab"; fi ;;
    esac
    continue
  fi
  case "$root" in repo) f="$PWD/$path" ;; home) f="$HOME/$path" ;; *) exit 9 ;; esac
  case "$step" in
    check) [ "$(h "$f")" = "$before" ] || { echo "moved: $path" >&2; exit 3; } ;;
    apply) if [ "$after" = null ]; then rm -f "$f"; else mkdir -p "$(dirname "$f")"; rm -f "$f"; cat "$B/after/$root/$path" > "$f"; fi ;;
    undo) if [ "$before" = null ]; then rm -f "$f"; else mkdir -p "$(dirname "$f")"; rm -f "$f"; cat "$B/before/$root/$path" > "$f"; fi ;;
    *) exit 2 ;;
  esac
done < "$B/list.txt"
EXTRA
exit 0
'''
CRONTAB_STUB = """#!/bin/bash
f="@FILE@"
case "${1:-}" in
  -l) [ -f "$f" ] && { cat "$f"; exit 0; }; exit 1 ;;
  -r) rm -f "$f"; exit 0 ;;
  -|"") cat > "$f"; exit 0 ;;
  *) cat "$1" > "$f"; exit 0 ;;
esac
"""


def plant_calls(calls, guard_calls):
    """S15's replay inputs (DEC-1108 (2)): the CTO's call set (a header with a 48.5-hour window ending 30 minutes
    before the trial's clock, one call) and the guard's call log (that call's line), agreeing both ways."""
    session, tin = "7d3c2b1a-0f9e-4d8c-b7a6-958473625140", {"file_path": "README.md"}
    digest = sha(json.dumps({"tool": "Read", "input": tin}, sort_keys=True, separators=(",", ":"),
                            ensure_ascii=False).encode())
    head = {"v": 1, "window": {"since": "2026-11-08T10:00:00+00:00", "until": "2026-11-10T10:30:00+00:00"}}
    call = {"id": "trial-c1", "time": "2026-11-10T09:00:00+00:00", "session": session, "role": "engineer",
            "ticket": "W2-1", "agent": "", "sha256": digest, "event": {"tool_name": "Read", "tool_input": tin, "cwd": "."}}
    write(calls, json.dumps(head) + "\n" + json.dumps(call) + "\n")
    write(Path(guard_calls) / "2026-11-10.jsonl", json.dumps({
        "v": 1, "time": "2026-11-10T09:00:00.200Z", "session": session, "role": "engineer", "agent": "",
        "ticket": "W2-1", "tool": "Read", "decision": "allow", "rule": "", "tree": "main", "ms": 2, "sha256": digest,
        "keyed": None}) + "\n")


class Planted:
    """One planted world: an operator root with the install, a repository clone at a commit, HOME, scratch, and
    S15's replay inputs (the CTO's call set, the guard's call log)."""

    def __init__(self, base, commit):
        self.base = Path(base)
        self.root = self.base / "op"
        self.install = self.root / "install"
        shutil.copytree(OPDIR, self.install, ignore=shutil.ignore_patterns("__pycache__"))
        lines = [f"{sha(p.read_bytes())}  {p.relative_to(self.install).as_posix()}"
                 for p in sorted(self.install.rglob("*")) if p.is_file()]
        write(self.install / "APPROVED", "\n".join(lines) + "\n")
        self.repo = self.base / "repo"
        git("clone", "-q", "--no-checkout", str(REPO), str(self.repo))
        git("checkout", "-q", "--detach", commit, cwd=self.repo)
        git("config", "user.email", "trial@localhost", cwd=self.repo)
        git("config", "user.name", "trial", cwd=self.repo)
        for hook in (self.repo / ".git/hooks").glob("*"):
            if hook.is_file() and not hook.name.endswith(".sample"):
                hook.unlink()
        write(self.repo / ".live-marker", "live\n")
        with open(self.repo / ".git/info/exclude", "a") as f:
            f.write(".live-marker\n")
        self.home = self.base / "home"
        self.home.mkdir()
        self.scratch = self.base / "scratch"
        write(self.scratch / "log/cto-session.txt", "trial-session\n")
        self.tx = self.base / "tx"
        self.tx.mkdir()
        self.bin = self.base / "bin"
        self.cron = self.base / "crontab.txt"
        write(self.bin / "crontab", CRONTAB_STUB.replace("@FILE@", str(self.cron)), 0o755)
        write(self.cron, "0 4 * * * /bin/true # a planted crontab\n")
        self.pushes = self.base / "pushes.log"
        write(self.base / "push.sh", f'#!/bin/bash\necho "$1" >> {self.pushes}\n', 0o755)
        self.clock = write(self.base / "clock.txt", CLOCK + "\n")
        self.calls, self.guard_calls = self.base / "calls.jsonl", self.base / "guard-calls"
        plant_calls(self.calls, self.guard_calls)
        self.config = write(self.base / "config.json", json.dumps({
            "operator_root": str(self.root), "repo": str(self.repo), "home": str(self.home),
            "scratch": str(self.scratch), "transcripts": str(self.tx), "clock": str(self.clock),
            "pings_log": str(self.base / "pings.log"), "push_cmd": [str(self.base / "push.sh")], "poll_s": 0.2,
            "close_flag": str(self.scratch / "CLOSE-RUNNING"), "calls": str(self.calls),
            "guard_calls": str(self.guard_calls)}))

    def env(self):
        e = {k: v for k, v in os.environ.items() if not k.startswith("GOV_") and k != "CLAUDE_PROJECT_DIR"}
        e["PATH"] = f"{self.bin}{os.pathsep}{e.get('PATH', '')}"
        e["TRIAL_CRONTAB"] = str(self.cron)
        e.pop("PYTHONPATH", None)
        return e

    def bundle(self, act, touched_bytes, claimed, review_class, dec, commands=(), checks=None, extra=""):
        """touched_bytes: [(root, path, before bytes or None, after bytes or None)] -> manifest sha."""
        b = self.scratch / "acts" / act
        if b.exists():
            shutil.rmtree(b)
        b.mkdir(parents=True)
        touched, files, lines = [], {}, []
        for root, path, before, after in touched_bytes:
            if before is not None:
                files[f"before/{root}/{path}"] = sha(write(b / "before" / root / path, before).read_bytes())
            if after is not None:
                files[f"after/{root}/{path}"] = sha(write(b / "after" / root / path, after).read_bytes())
            bs, as_ = (sha(before) if before is not None else None), (sha(after) if after is not None else None)
            touched.append({"root": root, "path": path, "before": bs, "after": as_})
            lines.append(f"{root}|{path}|{bs or 'null'}|{as_ or 'null'}")
        files["list.txt"] = sha(write(b / "list.txt", "\n".join(lines) + "\n").read_bytes())
        files["apply.sh"] = sha(write(b / "apply.sh", APPLY_SH.replace("EXTRA", extra)).read_bytes())
        files["rehearsal.log"] = sha(write(b / "rehearsal.log", "trial rehearsal\nfailures: 0\n").read_bytes())
        m = {"act": act, "dec": dec, "author": "cto", "claimed_class": claimed, "touched": touched, "files": files,
             "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]},
             "checks": checks if checks is not None else [{"cmd": "true", "exit": 0, "count": None}],
             "commands": list(commands)}
        raw = json.dumps(m, indent=1).encode()
        write(b / "manifest.json", raw)
        msha = sha(raw)
        self.review(act, msha, review_class)
        return msha

    def review(self, act, msha, cls):
        block = {"kpis": [{"kpi": f"K{i}", "verdict": "pass", "findings": []} for i in range(1, 7)],
                 "manifest_sha256": msha, "class": cls, "reviewer": "trial-reviewer",
                 "reviewer_brief_sha256": sha((self.install / "reviewer-brief.md").read_bytes()), "time": REVIEW_TIME}
        write(self.scratch / "acts" / act / "review.md", "# the trial's planted review\n\n```verdict\n"
              + json.dumps(block) + "\n```\n")

    def yes(self, text):
        e = {"type": "user", "origin": {"kind": "human"}, "timestamp": YES_TIME,
             "message": {"role": "user", "content": text}}
        with open(self.tx / "trial-session.jsonl", "a") as f:
            f.write(json.dumps(e) + "\n")

    def run(self, act, msha):
        r = subprocess.run([sys.executable, str(self.install / "operator_run.py"), "--config", str(self.config),
                            "run", act, msha], capture_output=True, env=self.env(), timeout=1800)
        res = json.loads(r.stdout.decode().strip().splitlines()[-1])
        return res

    def live(self, path):
        p = self.repo / path
        return p.read_bytes() if p.is_file() else None


def act_dec(act, repo):
    """The first DEC id the ACT file cites that the register at the replay's commit holds as ACCEPTED."""
    ids = list(dict.fromkeys(re.findall(r"DEC-\d+", (PKG / f"{act}.md").read_text(errors="replace"))))
    reg = (Path(repo) / "docs/DECISION_REGISTER.md").read_text(errors="replace")
    for d in ids:
        m = re.search(r"^###\s+" + re.escape(d) + r"(?!\d).*\n(?:.*\n){0,3}?.*\*\*Status:?\*\*:?\s*(\w+)", reg, re.M)
        if m and m.group(1) == "ACCEPTED":
            return d
    return ids[0] if ids else "DEC-1104"


def rm(path):
    for top, dirs, files in os.walk(path):
        for n in dirs + files:
            p = os.path.join(top, n)
            if not os.path.islink(p):
                os.chmod(p, 0o700)
    shutil.rmtree(path, ignore_errors=True)


def first_commit_of(act):
    out = git("log", "--diff-filter=A", "--format=%H", "--", f"governance/project/orchestration/packages/{act}.md")
    return out.decode().split()[-1]


def outcome(res):
    if res.get("undo") == "failed":
        return "lock held"
    return {"applied": "applied", "undone": "undone"}.get(res.get("result"), "refused")


# -------------------------------------------------------------------------------------------------------- B: replays
def replay_one(act, want, tmp, part=None):
    entries = {e["act"]: e for e in json.loads(ACTS_JSON.read_text())}
    e = entries[act]
    text = (PKG / f"{act}.md").read_text(errors="replace")
    commands = code_blocks(text) + [FLAG_LINES[f] for f in e["flags"] if f in FLAG_LINES]
    commit = (e["commits"][0] + "^") if e["commits"] else first_commit_of(act)
    w = Planted(tmp, git("rev-parse", commit).decode().strip())
    touched, note, checks = [], "", None
    if e["commits"]:
        for path, (b, a) in commit_changes(e["commits"]).items():
            if part == "control" and path.startswith("tests/") and not re.match(r"^tests/optin-[^/]*\.txt$", path):
                continue
            touched.append(("repo", path, b, a))
        note = f"the applying commit{'s' if len(e['commits']) > 1 else ''} {', '.join(c[:12] for c in e['commits'])}"
        ymls = [p for _, p, _, a in touched if p.endswith(".yaml") and a is not None]
        if ymls:
            checks = [{"cmd": "python3 -c \"import sys,yaml;[yaml.safe_load(open(p)) for p in sys.argv[1:]]\" "
                              + " ".join(ymls), "exit": 0, "count": None}]
    elif act == "ACT-SELECT-HOOK-1":
        before = (b"#!/bin/bash\n# the reference-transaction hook (W2-116's), as planted for the trial\n"
                  b"[ \"$1\" = committed ] || exit 0\nexit 0\n")
        after = before[:-7] + b": # DEC-1100 (2)-(3), ACT-SELECT-HOOK-1 line (command neutralised in the trial)\nexit 0\n"
        write(w.repo / ".git/hooks/reference-transaction", before, 0o755)
        touched.append(("repo", ".git/hooks/reference-transaction", before, after))
        note = "a planted hook; the ACT's one line added (its command neutralised: the trial never starts the live selection)"
    elif act == "ACT-PERMISSIONS-2":
        before = json.dumps({"permissions": {"allow": ["Bash(git status)"], "deny": []}}, indent=2).encode() + b"\n"
        after = json.dumps({"permissions": {"allow": ["Bash(git status)"], "deny": ["Read(//home/usain/.ssh/**)"],
                                            "additionalDirectories": ["/home/usain/gov-os-worktrees"]}},
                           indent=2).encode() + b"\n"
        write(w.repo / ".claude/settings.local.json", before)
        touched.append(("repo", ".claude/settings.local.json", before, after))
        note = "a planted settings.local.json; the ACT's change (additional directories and read deny rules) as its apply.py makes it"
    elif act == "ACT-NIGHTLY-STOP-1":
        before = w.cron.read_bytes()
        after = b"# " + before
        touched.append(("crontab", "crontab", before, after))
        note = "the planted crontab (a stub: never the live one); its nightly line commented out"
    elif act == "ACT-OLLAMA-CAP-1":
        touched.append(("home", ".ollama/serve-11434.log", None, b"ollama serve, capped to CPUs 12-19 at nice 10\n"))
        note = "the server's restart as its log in the planted HOME (the trial restarts no server)"
    elif act == "ACT-D8":
        for path in e["repo_paths"]:
            touched.append(("repo", path.rstrip("/"), b"before: " + path.encode(), None))
        for path in e["home_paths"]:
            touched.append(("home", path.rstrip("/"), b"before: " + path.encode(), None))
        note = "its deletions as listed (placeholders), its commands from its text"
    msha = w.bundle(act, touched, want, want, act_dec(act, w.repo), commands=commands, checks=checks)
    if want == "b":
        w.yes(f"yes {act} {msha[:8]}")
    res = w.run(act, msha)
    return {"replay": act + (" (control part)" if part else ""), "expected": want, "class": res.get("class"),
            "votes": res.get("votes"), "outcome": outcome(res), "gate": res.get("gate"),
            "reason": (res.get("reason") or "")[:240], "commit": res.get("commit"), "at": commit, "note": note}


def replays(base):
    out = []
    for act, want in REPLAYS:
        tmp = Path(tempfile.mkdtemp(prefix="w2-148-replay-", dir=base))
        try:
            out.append(replay_one(act, want, tmp))
            if act == "ACT-GUARD-SETS-1" and out[-1]["class"] != want:
                rm(tmp)
                tmp.mkdir()
                out.append(replay_one(act, want, tmp, part="control"))
        except Exception as exc:  # recorded, never hidden
            out.append({"replay": act, "expected": want, "outcome": f"error: {exc}"})
        finally:
            rm(tmp)
    return out


# --------------------------------------------------------------------------------------------------------- C: faults
def base_a(w):
    """An (a) ACT of the kind of the first live (a) run (DEC-1103 (2)): one line removed from an opt-in list."""
    p = "tests/optin-lifted.txt"
    before = (w.repo / p).read_bytes()
    lines = before.decode().splitlines(keepends=True)
    k = next(i for i, ln in enumerate(lines) if ln.strip() and not ln.startswith("#"))
    return [("repo", p, before, "".join(lines[:k] + lines[k + 1:]).encode())]


def base_b():
    e = {x["act"]: x for x in json.loads(ACTS_JSON.read_text())}["ACT-SELECT-FIXES-1"]
    return e, [("repo", p, b, a) for p, (b, a) in commit_changes(e["commits"]).items()]


def fault(name, tmp):
    sf = {x["act"]: x for x in json.loads(ACTS_JSON.read_text())}["ACT-SELECT-FIXES-1"]["commits"][0]
    if name in ("an edit after review", "an unlisted file touched", "a red check", "a failing undo"):
        w = Planted(tmp, git("rev-parse", "HEAD").decode().strip())
        touched = base_a(w)
        act = "ACT-TRIAL-OPTIN-1"
        if name == "an edit after review":
            msha = w.bundle(act, touched, "a", "a", "DEC-1104")
            p = w.scratch / "acts" / act / "apply.sh"
            p.write_text(p.read_text() + "# an edit after the review\n")
            m = json.loads((w.scratch / "acts" / act / "manifest.json").read_text())
            m["files"]["apply.sh"] = sha(p.read_bytes())
            raw = json.dumps(m, indent=1).encode()
            write(w.scratch / "acts" / act / "manifest.json", raw)
            res = w.run(act, sha(raw))
        elif name == "an unlisted file touched":
            msha = w.bundle(act, touched, "a", "a", "DEC-1104",
                            extra='[ "$step" = apply ] && echo x > "$PWD/docs/unlisted-by-the-trial.txt"')
            res = w.run(act, msha)
        elif name == "a red check":
            msha = w.bundle(act, touched, "a", "a", "DEC-1104",
                            checks=[{"cmd": "test ! -e .live-marker", "exit": 0, "count": None}])
            res = w.run(act, msha)
        else:
            msha = w.bundle(act, touched, "a", "a", "DEC-1104",
                            checks=[{"cmd": "test ! -e .live-marker", "exit": 0, "count": None}],
                            extra='[ "$step" = undo ] && [ -e "$PWD/.live-marker" ] && exit 7')
            res = w.run(act, msha)
    else:
        w = Planted(tmp, git("rev-parse", sf + "^").decode().strip())
        _, touched = base_b()
        touched = [t for t in touched]
        act = "ACT-SELECT-FIXES-1"
        if name == "a wrong class claim":
            msha = w.bundle(act, touched, "a", "a", "DEC-1100")
            res = w.run(act, msha)
        elif name == "a missing yes":
            msha = w.bundle(act, touched, "b", "b", "DEC-1100")
            res = w.run(act, msha)
        else:
            msha = w.bundle(act, touched, "b", "b", "DEC-1100")
            w.yes(f"yes {act} {'0' * 8 if msha[:8] != '0' * 8 else '1' * 8}")
            res = w.run(act, msha)
    return {"fault": name, "outcome": outcome(res), "gate": res.get("gate"), "votes": res.get("votes"),
            "reason": (res.get("reason") or "")[:240]}


FAULTS = ["an edit after review", "a wrong class claim", "an unlisted file touched", "a red check",
          "a failing undo", "a missing yes", "a yes for an older sha"]


def faults(base):
    out = []
    for name in FAULTS:
        tmp = Path(tempfile.mkdtemp(prefix="w2-148-fault-", dir=base))
        try:
            out.append(fault(name, tmp))
        except Exception as exc:
            out.append({"fault": name, "outcome": f"error: {exc}"})
        finally:
            rm(tmp)
    return out


# ---------------------------------------------------------------------------------------------------- D: live hashes
LIVE = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
HOME = Path("/home/usain")
CLAUDE_CONFIG = ("settings.json", "settings.local.json", "CLAUDE.md", "keybindings.json", "hooks", "agents", "skills",
                 "commands", "rules", "output-styles", "workflows")


def tree_digest(paths):
    """(files, sha256 over the sorted 'path<TAB>sha256' lines): names and hashes only, nothing printed."""
    lines = []
    for p in paths:
        p = Path(p)
        if p.is_symlink():
            lines.append(f"{p}\tlink:{os.readlink(p)}")
        elif p.is_file():
            try:
                lines.append(f"{p}\t{sha(p.read_bytes())}")
            except OSError as exc:
                lines.append(f"{p}\tunreadable:{exc.__class__.__name__}")
        elif p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_symlink():
                    lines.append(f"{f}\tlink:{os.readlink(f)}")
                elif f.is_file():
                    try:
                        lines.append(f"{f}\t{sha(f.read_bytes())}")
                    except OSError as exc:
                        lines.append(f"{f}\tunreadable:{exc.__class__.__name__}")
    return len(lines), sha("\n".join(sorted(lines)).encode())


def live_hashes():
    r = subprocess.run(["crontab", "-l"], capture_output=True)
    rows = {
        "live repository: .claude/hooks/**": [LIVE / ".claude/hooks"],
        "live repository: .claude/settings*.json": sorted(LIVE.glob(".claude/settings*.json")),
        "live repository: the rest of .claude/** (agents, skills, commands)": [LIVE / ".claude/agents",
                                                                              LIVE / ".claude/skills",
                                                                              LIVE / ".claude/commands"],
        "live repository: .git/hooks/**": [LIVE / ".git/hooks"],
        "live repository: path map, test map, opt-in lists": [LIVE / "governance/project/path-map.yaml",
                                                              LIVE / "governance/project/test-map.yaml"]
        + sorted(LIVE.glob("tests/optin-*.txt")),
        "live repository: deadman.py, sentinel-brief.md": [LIVE / "governance/project/orchestration/tools/deadman.py",
                                                           LIVE / "governance/project/orchestration/tools/sentinel-brief.md"],
        "the pin ~/.local/bin/gov": [HOME / ".local/bin/gov"],
        "~/gov-os-operator/ (every file)": [HOME / "gov-os-operator"],
        "~/.claude/ (its configuration: settings, CLAUDE.md, hooks, agents, skills, commands, rules)":
            [HOME / ".claude" / n for n in CLAUDE_CONFIG],
    }
    out = {k: tree_digest(v) for k, v in rows.items()}
    out[f"crontab -l (its output; exit {r.returncode})"] = (1, sha(r.stdout))
    return out


def main(argv):
    out_path, part = None, "all"
    if "--out" in argv:
        out_path = argv[argv.index("--out") + 1]
    if "--part" in argv:
        part = argv[argv.index("--part") + 1]
    base = Path(tempfile.mkdtemp(prefix="w2-148-trial-"))
    result = {"before": live_hashes()}
    try:
        if part in ("classify", "all"):
            result["classify"] = classify_all()
        if part in ("replays", "all"):
            result["replays"] = replays(base)
        if part in ("faults", "all"):
            result["faults"] = faults(base)
    finally:
        rm(base)
        result["after"] = live_hashes()
    result["live_unchanged"] = result["before"] == result["after"]
    text = json.dumps(result, indent=1)
    if out_path:
        Path(out_path).write_text(text)
    print(json.dumps({"live_unchanged": result["live_unchanged"],
                      "counts": (result.get("classify") or {}).get("counts"),
                      "replays": [(r["replay"], r.get("outcome")) for r in result.get("replays", [])],
                      "faults": [(f["fault"], f.get("outcome")) for f in result.get("faults", [])]}))
    return 0


def test_no_act_file_is_classed_lower_than_the_table():
    r = classify_all()
    assert r["lower"] == [], r["lower"]
    assert r["files"] == len(act_files()) and sum(r["counts"].values()) == r["files"]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
