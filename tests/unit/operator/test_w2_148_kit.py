"""W2-148's planted kit (the engineer's unit tests): an operator root with the install and its APPROVED, a repository,
a HOME, the CTO's scratch with ACT bundles, a transcript, a clock and stub channels, all under a temporary folder.
Nothing here touches ~/gov-os-operator, ~/.claude, the crontab or this repository's live files."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

OPDIR = Path(__file__).resolve().parents[3] / "governance" / "project" / "operator"
DAY = "2026-11-10"

GUARD = r'''#!/usr/bin/env python3
import fnmatch, json, os, sys, yaml
root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
pm = yaml.safe_load(open(os.path.join(root, "governance/project/path-map.yaml")))
ev = json.loads(sys.stdin.read())
globs = (pm.get("sets_root_hidden") or {}).get("hidden") or []
tin = ev.get("tool_input") or {}
p = tin.get("file_path") or tin.get("path") or ""
full = os.path.realpath(os.path.join(ev.get("cwd") or root, p))
rel = os.path.relpath(full, os.path.realpath(root))
if ev.get("tool_name") == "Read" and any(fnmatch.fnmatch(rel, g.replace("**", "*")) for g in globs):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny"}}))
sys.exit(0)
'''

PATH_MAP = """version: 1
decision_register: docs/DECISION_REGISTER.md
acceptance_exemptions: []
sets_root_hidden:
  root: "~/gov-os-eval"
  hidden: ["fixtures/a/**"]
  refused_roles: [engineer]
role_paths:
  engineer:
    reads_denied: ["{ticket_tests}"]
"""

TEST_MAP = """version: 1
shared_core:
  - "src/core/**"
record_only:
  - "docs/**.md"
couplings:
  - paths: ["src/a.py"]
    suites: ["tests/test_a.py"]
    why: "x"
per_test_timeout: 900
"""

REGISTER = """# Register

### DEC-1 — accepted
- **Status:** ACCEPTED (owner)

### DEC-2 — proposed
- **Status:** PROPOSED

### DEC-10 — accepted ten
- **Status:** ACCEPTED
"""

APPLY_SH = r'''#!/bin/bash
# A planted ACT's apply.sh: reads its bundle from its own folder; check, apply, undo by list.txt.
set -u
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
step="${1:-}"
while IFS='|' read -r root path before after; do
  [ -z "$root" ] && continue
  case "$root" in repo) f="$PWD/$path" ;; home) f="$HOME/$path" ;; *) exit 9 ;; esac
  case "$step" in
    check)
      if [ -f "$f" ]; then h=$(sha256sum "$f" | cut -c1-64); else h=null; fi
      [ "$h" = "$before" ] || { echo "moved: $path" >&2; exit 3; } ;;
    apply)
      if [ "$after" = null ]; then rm -f "$f"; else mkdir -p "$(dirname "$f")"; rm -f "$f"; cat "$B/after/$root/$path" > "$f"; fi ;;
    undo)
      if [ "$before" = null ]; then rm -f "$f"; else mkdir -p "$(dirname "$f")"; rm -f "$f"; cat "$B/before/$root/$path" > "$f"; fi ;;
    *) exit 2 ;;
  esac
done < "$B/list.txt"
EXTRA_LINES
exit 0
'''

STUB_CLAUDE = r'''#!/usr/bin/env python3
import json, os, sys
rec = os.environ.get("HOME", "/tmp") + "/../claude-calls.jsonl"
argv = sys.argv[1:]
with open(os.path.realpath(rec), "a") as f:
    f.write(json.dumps({"argv": argv, "cwd": os.getcwd(), "env": dict(os.environ)}) + "\n")
prompt = argv[-1] if argv else ""
settings = argv[argv.index("--settings") + 1] if "--settings" in argv else None
loaded = False
try:
    s = json.load(open(settings))
    loaded = bool(s.get("permissions", {}).get("deny"))
except Exception:
    loaded = False
if "canary-target" in prompt:
    target = [w for w in prompt.split() if "canary-target" in w][0]
    print(json.dumps({"permission_denials": [{"tool_name": "Read", "tool_input": {"file_path": target}}] if loaded else []}))
else:
    print(json.dumps({"result": "ok", "permission_denials": []}))
'''


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sh(*cmd, cwd=None, env=None, check=True):
    r = subprocess.run(list(cmd), cwd=cwd, env=env, capture_output=True)
    if check and r.returncode != 0:
        raise AssertionError(f"{cmd}: {r.stderr.decode()}")
    return r


def write(p, data, mode=None):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data if isinstance(data, bytes) else data.encode())
    if mode:
        os.chmod(p, mode)
    return p


def approve(install):
    lines = []
    for f in sorted(Path(install).rglob("*")):
        if f.is_file() and "__pycache__" not in f.parts and f.name != "APPROVED":
            lines.append(f"{sha(f.read_bytes())}  {f.relative_to(install).as_posix()}")
    write(Path(install) / "APPROVED", "\n".join(lines) + "\n")


class Kit:
    def __init__(self, tmp):
        tmp = Path(tmp)
        self.tmp = tmp
        self.root = tmp / "op"
        self.install = self.root / "install"
        shutil.copytree(OPDIR, self.install, ignore=shutil.ignore_patterns("__pycache__"))
        approve(self.install)
        self.repo = tmp / "repo"
        self.home = tmp / "home"
        self.scratch = tmp / "scratch"
        self.tx = tmp / "tx"
        self.home.mkdir()
        self.tx.mkdir()
        (self.scratch / "log").mkdir(parents=True)
        write(self.scratch / "log/cto-session.txt", "sess-1\n")
        self.clock = write(tmp / "clock.txt", f"{DAY}T12:00:00+01:00\n")
        self.pings = tmp / "pings.log"
        self.pushes = tmp / "pushes.log"
        write(tmp / "push.sh", f'#!/bin/bash\necho "$1" >> {self.pushes}\n', 0o755)
        self.bin = tmp / "bin"
        write(self.bin / "claude", STUB_CLAUDE, 0o755)
        write(self.bin / "crontab", "#!/bin/bash\n[ \"$1\" = -l ] && exit 1\nexit 0\n", 0o755)
        self.repo.mkdir()
        sh("git", "init", "-q", "-b", "main", cwd=self.repo)
        sh("git", "config", "user.email", "t@t", cwd=self.repo)
        sh("git", "config", "user.name", "t", cwd=self.repo)
        write(self.repo / "docs/DECISION_REGISTER.md", REGISTER)
        write(self.repo / "governance/project/path-map.yaml", PATH_MAP)
        write(self.repo / "governance/project/test-map.yaml", TEST_MAP)
        write(self.repo / "tests/optin-x.txt", "one\ntwo\nthree\n")
        write(self.repo / ".claude/hooks/pretooluse.py", GUARD)
        write(self.repo / ".claude/settings.json", json.dumps({"permissions": {"deny": ["Bash(sudo *)"]}}, indent=1))
        write(self.repo / "data/plain.txt", "plain\n")
        sh("git", "add", "-A", cwd=self.repo)
        sh("git", "commit", "-q", "-m", "base", cwd=self.repo)
        write(self.repo / ".live-marker", "live\n")
        with open(self.repo / ".git/info/exclude", "a") as f:
            f.write(".live-marker\n")
        self.config = write(tmp / "config.json", json.dumps({
            "operator_root": str(self.root), "repo": str(self.repo), "home": str(self.home),
            "scratch": str(self.scratch), "transcripts": str(self.tx), "clock": str(self.clock),
            "pings_log": str(self.pings), "push_cmd": [str(tmp / "push.sh")], "poll_s": 0.1,
            "nightly_window": "03:50-08:00", "close_flag": str(self.scratch / "CLOSE-RUNNING")}))

    def env(self):
        e = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
        e["PATH"] = f"{self.bin}{os.pathsep}{e.get('PATH', '')}"
        e.pop("PYTHONPATH", None)
        return e

    def set_clock(self, t):
        write(self.clock, t + "\n")

    def bundle(self, act, changes, claimed="a", review_class=None, extra_apply="", checks=None, commands=None,
               dec="DEC-1", author="cto", rounds=1, reviewer="rev", rehearsal="ok\nfailures: 0\n", rtime=None,
               brief_sha=None, replay_refused=None):
        """changes: {(root, path): new bytes or None}. Returns the manifest sha."""
        b = self.scratch / "acts" / act
        if b.exists():
            shutil.rmtree(b)
        b.mkdir(parents=True)
        touched, files, lines = [], {}, []
        for (root, path), new in changes.items():
            base = self.repo if root == "repo" else self.home
            cur = (base / path).read_bytes() if (base / path).is_file() else None
            before = sha(cur) if cur is not None else None
            after = sha(new) if new is not None else None
            if cur is not None:
                files[f"before/{root}/{path}"] = sha(write(b / "before" / root / path, cur).read_bytes())
            if new is not None:
                files[f"after/{root}/{path}"] = sha(write(b / "after" / root / path, new).read_bytes())
            touched.append({"root": root, "path": path, "before": before, "after": after})
            lines.append(f"{root}|{path}|{before or 'null'}|{after or 'null'}")
        files["list.txt"] = sha(write(b / "list.txt", "\n".join(lines) + "\n").read_bytes())
        files["apply.sh"] = sha(write(b / "apply.sh", APPLY_SH.replace("EXTRA_LINES", extra_apply)).read_bytes())
        files["rehearsal.log"] = sha(write(b / "rehearsal.log", rehearsal).read_bytes())
        m = {"act": act, "dec": dec, "author": author, "claimed_class": claimed, "touched": touched, "files": files,
             "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]},
             "checks": checks if checks is not None else [{"cmd": "true", "exit": 0, "count": None}],
             "commands": commands or []}
        raw = json.dumps(m, indent=1).encode()
        write(b / "manifest.json", raw)
        msha = sha(raw)
        block = {"kpis": [{"kpi": "K1", "verdict": "pass", "findings": []}], "manifest_sha256": msha,
                 "class": review_class or claimed, "reviewer": reviewer,
                 "reviewer_brief_sha256": brief_sha or sha((self.install / "reviewer-brief.md").read_bytes()),
                 "time": rtime or f"{DAY}T10:00:00+01:00"}
        if replay_refused is not None:
            block["replay_refused"] = replay_refused
        text = "# review\n" + "".join("\n```verdict\n" + json.dumps(block) + "\n```\n" for _ in range(rounds))
        write(b / "review.md", text)
        return msha

    def run(self, *args, env=None, timeout=120):
        r = subprocess.run([sys.executable, str(self.install / "operator_run.py"), "--config", str(self.config)]
                           + list(args), capture_output=True, env=env or self.env(), timeout=timeout)
        return r.returncode, json.loads(r.stdout.decode().strip().splitlines()[-1]), r

    def launch(self, timeout=120):
        r = subprocess.run([sys.executable, str(self.install / "operator_launch.py"), "--config", str(self.config)],
                           capture_output=True, env=self.env(), timeout=timeout)
        return r.returncode, json.loads(r.stdout.decode().strip().splitlines()[-1]), r

    def log(self):
        p = self.root / "log/operator.jsonl"
        return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []

    def notices(self):
        return [json.loads(x) for x in self.pings.read_text().splitlines() if x.strip()] if self.pings.exists() else []

    def say(self, text, ts, kind="human", **extra):
        e = {"type": "user", "timestamp": ts, "message": {"role": "user", "content": text}}
        if kind:
            e["origin"] = {"kind": kind}
        e.update(extra)
        with open(self.tx / "sess-1.jsonl", "a") as f:
            f.write(json.dumps(e) + "\n")

    def head(self):
        return sh("git", "rev-parse", "HEAD", cwd=self.repo).stdout.decode().strip()

    def trailers(self, rev="HEAD"):
        return sh("git", "log", "-1", "--format=%(trailers)", rev, cwd=self.repo).stdout.decode()
