"""W2-149: the engineer's unit tests for the independent sessions' launch script (indep_launch.py).

Everything planted under tmp_path: HOME, the sets root, the repository, and a stub `claude` on PATH that records each
call and models Claude Code for the canary (restricted mode, a settings file it cannot validate ignored, the wall's
PreToolUse hook run as `sh -c`). No real claude, no real ~/gov-os-eval, ~/gov-os-runs, ~/gov-os-wall-trees or ~/.claude.
"""
import hashlib
import json
import math
import os
import random
import signal
import stat
import subprocess
import sys
import tarfile
import fnmatch
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "governance" / "project" / "orchestration" / "tools"
SCRIPT = TOOLS / "indep_launch.py"
SCHEMAS = TOOLS / "indep-schemas"
WALLS = "indep-" + "walls"
TEMPLATE = ROOT / "governance" / "project" / WALLS
TEMPLATE_FILES = ("settings.json.tmpl", "wall_hook.py", "CLAUDE.md.tmpl", "kinds.yaml", "tree-exclude.txt",
                  "README.md")
KINDS = ("writer", "checker", "auditor", "labeller")
SET = "memory-recall-3"
SID = "abcdef12-3456-7890-abcd-ef1234567890"

sys.path.insert(0, str(TOOLS))
import indep_launch  # noqa: E402

PATH_MAP = """\
sets_root_hidden:
  root: "~/gov-os-eval"
  hidden: ["fixtures/evaluation/memory-retrieval/hidden/**", "transcripts/**",
           "fixtures/evaluation/sandbox-guard-exp-1/hidden/**", "indep-walls/**"]
  refused_roles: [orchestrator]
"""

STUB = r'''#!/usr/bin/env python3
import json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(HERE, "stub.json")))
argv = sys.argv[1:]
VALUED = ("--settings", "--tools", "--permission-prompts", "--model", "--max-budget-usd", "--output-format")
flags, adds, i = {}, [], 0
while i < len(argv) - 1:
    a = argv[i]
    if a == "--add-dir":
        adds.append(argv[i + 1]); i += 2
    elif a in VALUED:
        flags[a] = argv[i + 1]; i += 2
    else:
        flags[a] = True; i += 1
prompt = argv[-1] if argv else ""
paths = [w.rstrip(".,;:") for w in prompt.split() if w.startswith("/")]
paths = [p for p in paths if os.path.isfile(p)]
try:
    parent = open("/proc/%d/cmdline" % os.getppid(), "rb").read().split(b"\0")[0].decode()
except OSError:
    parent = ""
inp = os.path.join(os.getcwd(), "input")
rec = {"argv": argv, "flags": flags, "adds": adds, "prompt": prompt, "cwd": os.getcwd(), "env": dict(os.environ),
       "pid": os.getpid(), "pgid": os.getpgid(0), "ppid": os.getppid(), "parent": parent,
       "stdin_null": os.path.realpath("/proc/self/fd/0") == "/dev/null", "canary": bool(paths),
       "input": sorted(os.listdir(inp)) if os.path.isdir(inp) else None}
with open(os.path.join(HERE, "calls.jsonl"), "a") as f:
    f.write(json.dumps(rec) + "\n")

def emit(denials=(), is_error=False, subtype="success", text="done"):
    print(json.dumps({"type": "result", "subtype": subtype, "is_error": is_error, "session_id": cfg.get("sid"),
                      "num_turns": 3, "total_cost_usd": 0.004, "duration_ms": 1500,
                      "permission_denials": list(denials), "result": text}))

if paths:
    mode = cfg.get("canary", "model")
    target = paths[0]
    if mode == "garbage":
        print("not json at all"); sys.exit(0)
    if mode == "sleep":
        time.sleep(300); sys.exit(0)
    if mode == "other":
        emit([{"tool_name": "Bash", "tool_use_id": "t1", "tool_input": {"command": "ls"}}]); sys.exit(0)
    if mode == "error":
        sys.exit(1)
    read = [{"tool_name": "Read", "tool_use_id": "t1", "tool_input": {"file_path": target}}]
    if not any(target.startswith(r.rstrip("/") + "/") for r in [os.getcwd()] + adds):
        emit(read); sys.exit(0)  # restricted mode alone refuses it
    settings = None
    try:
        s = json.load(open(flags.get("--settings", "")))
        if (isinstance(s, dict) and isinstance(s.get("permissions", {}), dict)
                and isinstance(s.get("hooks", {}), dict) and isinstance(s.get("model", ""), str)
                and isinstance(s.get("cleanupPeriodDays", 1), int)):
            settings = s
    except Exception:
        settings = None
    denied = False
    if settings:
        ev = json.dumps({"tool_name": "Read", "tool_input": {"file_path": target}, "cwd": os.getcwd(),
                         "hook_event_name": "PreToolUse"})
        for entry in settings.get("hooks", {}).get("PreToolUse", []):
            for h in entry.get("hooks", []):
                p = subprocess.run(["sh", "-c", h["command"]], input=ev, capture_output=True, text=True)
                if p.returncode == 2:
                    denied = True
                elif p.stdout.strip():
                    try:
                        denied |= json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"
                    except Exception:
                        pass
    emit(read if denied else [])
    sys.exit(0)
mode = cfg.get("session")
if mode is None:
    sys.exit(97)
for rel, text in cfg.get("out", {}).items():
    p = os.path.join(os.getcwd(), rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(text)
if mode == "child":
    subprocess.Popen(["sleep", "300"])
    time.sleep(300)
if mode == "sleep":
    time.sleep(300)
if mode == "budget":
    emit(is_error=True, subtype="error_max_budget_usd"); sys.exit(1)
if mode == "trace":
    d = os.path.join(os.environ["HOME"], ".claude", "projects", "p1")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, cfg["sid"] + ".jsonl"), "w").write("x")
emit([{"tool_name": "Read", "tool_use_id": "t2", "tool_input": {"file_path": "/etc/hostname"}},
      {"tool_name": "ZzTool", "tool_use_id": "t3", "tool_input": {}}], text=cfg.get("marker", "done"))
'''


def sha(b):
    return hashlib.sha256(b).hexdigest()


def tree_hash(top):
    out = {}
    for folder, dirs, names in os.walk(top):
        for n in names:
            p = os.path.join(folder, n)
            out[os.path.relpath(p, top)] = sha(open(p, "rb").read())
        for d in dirs:
            out[os.path.relpath(os.path.join(folder, d), top) + "/"] = "dir"
    return out


class World:
    def __init__(self, tmp):
        self.tmp = tmp
        self.home, self.sets, self.repo, self.bin = tmp / "home", tmp / "sets", tmp / "repo", tmp / "bin"
        for d in (self.home, self.sets, self.repo, self.bin):
            d.mkdir()
        self.git("init", "-q", "-b", "main")
        for n in TEMPLATE_FILES:
            self.put(f"governance/project/{WALLS}/{n}", (TEMPLATE / n).read_bytes())
        self.put("governance/project/path-map.yaml", PATH_MAP)
        for k in KINDS:
            self.put(f"governance/project/indep-briefs/{k}.md", self.brief_text(k))
        for i in range(8):
            self.put(f"docs/note-{i}.md", f"note {i}\n")
            self.put(f"src/mod_{i}.py", f"x = {i}\n")
        self.put("tools/run.sh", "#!/bin/sh\necho run\n", mode=0o755)
        self.put("README.md", "readme\n")
        self.put("fixtures/evaluation/x/hidden/q.yaml", "secret question\n")
        self.put(".gov-runtime/scratch/n.txt", "scratch\n")
        self.put("docs/research/EXP-003/r.md", "measure\n")
        self.commit = self.commit_all("base")
        self.approve()
        (self.sets / "fixtures" / "evaluation" / SET).mkdir(parents=True)
        (self.sets / "fixtures" / "evaluation" / SET / "README.md").write_text("visible\n")
        stub = self.bin / "claude"
        stub.write_text(STUB)
        stub.chmod(0o755)
        self.stub({})

    # -- the repository ------------------------------------------------------------------------------------------
    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                              capture_output=True, text=True, check=True, env=self.env(), timeout=60).stdout.strip()

    def put(self, rel, data, mode=None):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.is_symlink() or p.exists():
            p.unlink()
        p.write_bytes(data.encode() if isinstance(data, str) else data)
        if mode:
            p.chmod(mode)

    def commit_all(self, msg):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)
        return self.git("rev-parse", "HEAD")

    @staticmethod
    def brief_text(kind_, **extra):
        kind = kind_
        fm = {"kind": kind, "sample": 3, "model": "claude-haiku-5-5", "result_schema": f"{kind}-result.schema.json",
              "timeout_s": 20}
        fm.update(extra)
        body = "\n".join(f"{k}: {v}" for k, v in fm.items())
        return f"---\n{body}\n---\nThe {kind}'s brief.\n"

    def blob(self, commit, rel):
        return subprocess.run(["git", "-C", str(self.repo), "cat-file", "blob", f"{commit}:{rel}"],
                              capture_output=True, check=True).stdout

    def approve(self, commit=None, drop_brief=None):
        commit = commit or self.commit
        lines = ["# APPROVED (planted)"]
        for n in TEMPLATE_FILES:
            rel = f"governance/project/{WALLS}/{n}"
            lines.append(f"{sha(self.blob(commit, rel))}  template {rel}")
        for k in KINDS:
            if k != drop_brief:
                rel = f"governance/project/indep-briefs/{k}.md"
                lines.append(f"{sha(self.blob(commit, rel))}  brief {k} {rel}")
        (self.sets / WALLS).mkdir(exist_ok=True)
        (self.sets / WALLS / "APPROVED").write_text("\n".join(lines) + "\n")

    # -- the stub and the runs -----------------------------------------------------------------------------------
    def stub(self, cfg):
        cfg = dict({"sid": SID}, **cfg)
        (self.bin / "stub.json").write_text(json.dumps(cfg))

    def calls(self):
        p = self.bin / "calls.jsonl"
        return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []

    def env(self, extra=None):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
        env.update(HOME=str(self.home), PATH=f"{self.bin}:{os.environ['PATH']}")
        env.update(extra or {})
        return env

    def hook(self, body):
        p = self.tmp / "hook.py"
        p.write_text("#!/usr/bin/env python3\nimport os, sys, time\npoint, wall, tree = sys.argv[1:4]\n" + body)
        p.chmod(0o755)
        return str(p)

    def run(self, *args, extra=None):
        p = subprocess.run([sys.executable, str(SCRIPT), *args], cwd=str(self.repo), env=self.env(extra),
                           capture_output=True, text=True, timeout=180)
        lines = [x for x in p.stdout.splitlines() if x.strip()]
        counts = json.loads(lines[-1]) if lines else None
        return p.returncode, counts, p

    def args(self, kind="writer", commit=None, brief_sha=None, set_name=SET, rnd=None, audit=None, seed=None,
             dry=False):
        commit = commit or self.commit
        rel = f"governance/project/indep-briefs/{kind}.md"
        a = ["--sets-root", str(self.sets), "--kind", kind, "--brief", rel,
             "--brief-sha256", brief_sha or sha(self.blob(commit, rel)), "--commit", commit, "--set", set_name]
        if rnd:
            a += ["--round", str(rnd)]
        if audit:
            a += ["--audit", audit]
        if seed is not None:
            a += ["--seed", str(seed)]
        if dry:
            a.append("--dry")
        return a

    def launch(self, *a, extra=None, **kw):
        return self.run(*self.args(*a, **kw), extra=extra)

    # -- where things are ----------------------------------------------------------------------------------------
    @property
    def runs(self):
        return self.home / "gov-os-runs" / "indep"

    def wall(self, counts):
        return self.sets / WALLS / counts["kind"] / counts["run"]

    def tree(self, counts):
        return self.home / "gov-os-wall-trees" / f"{counts['kind']}-{counts['run']}"

    def seeds(self):
        p = self.runs / "SEEDS.log"
        return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []

    def plant_set(self, files=None, set_name=SET):
        hidden = self.sets / "fixtures" / "evaluation" / set_name / "hidden"
        hidden.mkdir(parents=True, exist_ok=True)
        for rel, text in (files or {"q01.yaml": "question one\n", "sub/q02.yaml": "question two\n"}).items():
            (hidden / rel).parent.mkdir(parents=True, exist_ok=True)
            (hidden / rel).write_text(text)
        return hidden

    def plant_seal(self, n1=23, n2=5):
        seal = self.sets / "fixtures" / "evaluation" / "sandbox-guard-exp-1" / "hidden"
        (seal / "corpus").mkdir(parents=True, exist_ok=True)
        (seal / "rulebook.md").write_text("the rules\n")
        (seal / "corpus" / "actions-r1.jsonl").write_text(
            "".join(json.dumps({"id": f"a{i:03d}", "action": "x"}) + "\n" for i in range(n1)))
        (seal / "corpus" / "actions-r2.jsonl").write_text(
            "".join(json.dumps({"id": f"b{i:03d}", "action": "y"}) + "\n" for i in range(n2)))
        return seal


@pytest.fixture
def w(tmp_path):
    return World(tmp_path)


def schema():
    return json.loads((SCHEMAS / "indep-counts.schema.json").read_text())


def assert_counts(counts, code, status):
    assert counts["code"] == code, counts
    assert counts["status"] == status, counts
    assert indep_launch.schema_ok(counts, schema()), counts


def nothing_built(w):
    walls = w.sets / WALLS
    assert sorted(os.listdir(walls)) == ["APPROVED"]
    assert not (w.home / "gov-os-wall-trees").exists() or not os.listdir(w.home / "gov-os-wall-trees")
    assert w.seeds() == []


# -- the interface ---------------------------------------------------------------------------------------------------
def test_help_offers_exactly_the_options_and_no_path_list(w):
    p = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True, timeout=60)
    assert p.returncode == 0
    import re
    opts = set(re.findall(r"(?<![\w-])(--[a-z][a-z0-9-]*|-h)\b", p.stdout.split("The documented lines")[0]))
    assert opts == {"--sets-root", "--kind", "--brief", "--brief-sha256", "--commit", "--set", "--round", "--audit",
                    "--seed", "--dry", "--counts-only", "--run", "--help", "-h"}
    assert "planted sets roots only" in p.stdout


def test_prompt_is_one_line_without_absolute_path_and_its_sha_is_the_constant():
    assert "\n" not in indep_launch.PROMPT
    assert "brief.md" in indep_launch.PROMPT and "out/result.json" in indep_launch.PROMPT
    assert not any(x.startswith("/") for x in indep_launch.PROMPT.split())
    assert sha(indep_launch.PROMPT.encode()) == indep_launch.PROMPT_SHA256
    src = SCRIPT.read_text()
    assert f'PROMPT_SHA256 = "{indep_launch.PROMPT_SHA256}"' in src


def test_no_name_matched_stop_in_the_script():
    src = SCRIPT.read_text()
    for word in ("p" + "kill", "kill" + "all", "pgrep" + " -f", "p" + "grep"):
        assert word not in src


def test_documented_lines_name_only_the_sets_root():
    lines = [x.strip() for x in indep_launch.__doc__.splitlines() if x.strip().startswith("python3 ")]
    assert len(lines) == 6
    for ln in lines:
        assert WALLS + "/" not in ln and "$" not in ln and not any(c in ln for c in "*?[{<>|;&`")


# -- 17: the argument checks, first --------------------------------------------------------------------------------
@pytest.mark.parametrize("change", ["seed_given", "bad_set", "root_walls", "brief_under_root", "override_relative",
                                    "override_under_root", "bad_kind", "unknown_option", "audit_on_writer",
                                    "bad_round"])
def test_argument_refusals_17_build_nothing(w, change):
    a = w.args()
    extra = None
    if change == "seed_given":
        a += ["--seed", "5"]
    elif change == "bad_set":
        a[a.index("--set") + 1] = "Bad_Set"
    elif change == "root_walls":
        a[1] = str(w.sets / WALLS / "writer")
    elif change == "brief_under_root":
        a[a.index("--brief") + 1] = str(w.sets / "x.md")
    elif change == "override_relative":
        extra = {"GOV_INDEP_RUNS_DIR": "relative/runs"}
    elif change == "override_under_root":
        extra = {"GOV_INDEP_TREES_DIR": str(w.sets / "trees")}
    elif change == "bad_kind":
        a[a.index("--kind") + 1] = "poet"
    elif change == "unknown_option":
        a += ["--paths", "a,b"]
    elif change == "audit_on_writer":
        a += ["--audit", "e0"]
    elif change == "bad_round":
        a += ["--round", "3"]
    rc, counts, p = w.run(*a, extra=extra)
    assert rc == 17
    assert_counts(counts, 17, "refused")
    assert counts["reason"] == "argument"
    nothing_built(w)
    assert w.calls() == []


def test_argument_checks_come_before_the_brief_check(w):
    a = w.args(brief_sha="0" * 64) + ["--seed", "3"]
    rc, counts, _ = w.run(*a)
    assert rc == 17


# -- 14: the commit ------------------------------------------------------------------------------------------------
def test_commit_that_does_not_resolve_or_is_off_the_main_line_14(w):
    rc, counts, _ = w.launch(commit="f" * 40, brief_sha="0" * 64)
    assert rc == 14 and counts["commit"] is None
    w.git("checkout", "-q", "-b", "side")
    w.put("docs/side.md", "side\n")
    side = w.commit_all("side")
    w.git("checkout", "-q", "main")
    rc, counts, _ = w.launch(commit=side)
    assert rc == 14
    assert_counts(counts, 14, "refused")
    nothing_built(w)


def test_commit_holding_a_link_14_before_anything_is_written(w):
    os.symlink("note-0.md", w.repo / "docs" / "link.md")
    c = w.commit_all("link")
    w.approve(c)
    rc, counts, _ = w.launch(commit=c)
    assert rc == 14
    nothing_built(w)


def test_w2_integrate_is_the_main_line_when_it_exists(w):
    w.git("branch", "w2/integrate", w.commit)
    w.put("docs/later.md", "later\n")
    later = w.commit_all("later on main only")
    w.approve(later)
    rc, _, _ = w.launch(commit=later)
    assert rc == 14  # main is not the main line now


# -- 11: the template ----------------------------------------------------------------------------------------------
def test_one_changed_byte_in_each_template_file_11(w):
    base = w.commit
    for n in TEMPLATE_FILES:
        rel = f"governance/project/{WALLS}/{n}"
        orig = w.blob(base, rel)
        w.put(rel, orig + b" ")
        changed = w.commit_all(f"alter {n}")
        w.put(rel, orig)
        w.commit_all(f"restore {n}")
        rc, counts, _ = w.launch(commit=changed)
        assert rc == 11, n
        assert_counts(counts, 11, "refused")
        assert counts["template_ok"] is False
    nothing_built(w)


def test_a_kind_with_a_tool_beyond_the_list_11(w):
    rel = f"governance/project/{WALLS}/kinds.yaml"
    w.put(rel, w.blob(w.commit, rel).replace(b"tools: [Read, Grep, Glob, Write, TodoWrite]\n    input: [set]",
                                             b"tools: [Read, Grep, Glob, Write, TodoWrite, Bash]\n    input: [set]"))
    c = w.commit_all("bash for the checker")
    w.approve(c)
    rc, _, _ = w.launch(commit=c)
    assert rc == 11


# -- 10: the brief -------------------------------------------------------------------------------------------------
def test_brief_bytes_hash_argument_or_line_disagree_10(w):
    rel = "governance/project/indep-briefs/writer.md"
    approved_sha = sha(w.blob(w.commit, rel))
    w.put(rel, w.blob(w.commit, rel) + b"x")
    altered = w.commit_all("alter the brief")
    rc, counts, _ = w.launch(commit=altered, brief_sha=approved_sha)  # the bytes differ from the line
    assert rc == 10
    rc, counts, _ = w.launch(brief_sha="0" * 64)  # a wrong hash argument
    assert rc == 10
    w.approve(drop_brief="writer")  # the line removed
    rc, counts, _ = w.launch()
    assert rc == 10
    assert_counts(counts, 10, "refused")
    assert counts["reason"] == "brief" and counts["template_ok"] is True
    assert counts["approved_sha256"] == sha((w.sets / WALLS / "APPROVED").read_bytes())
    nothing_built(w)


@pytest.mark.parametrize("extra", [{"kind": "checker"}, {"budget_usd": 26}, {"timeout_s": 7201},
                                   {"result_schema": "nothing.schema.json"}, {"sample": -1}])
def test_front_matter_disagreeing_10(w, extra):
    rel = "governance/project/indep-briefs/writer.md"
    w.put(rel, World.brief_text("writer", **extra))
    c = w.commit_all("brief")
    w.approve(c)
    rc, _, _ = w.launch(commit=c)
    assert rc == 10
    nothing_built(w)


def test_a_missing_input_10_before_anything_is_written(w):
    for kind, kw in (("checker", {}), ("auditor", {"audit": "e0"}), ("labeller", {}), ("writer", {"rnd": 2})):
        rc, counts, _ = w.launch(kind, **kw)
        assert rc == 10, kind
    nothing_built(w)


# -- 15: the file budget -------------------------------------------------------------------------------------------
def test_hidden_part_file_budget_15(w):
    tr = w.sets / "transcripts"
    tr.mkdir()
    for i in range(7989):  # with APPROVED: 7,990 hidden files
        (tr / f"t{i:05d}").write_text("")
    rc, counts, _ = w.launch(seed=1, dry=True)  # writer round 1: 7 fixed + 3 = 10 expected: exactly 8,000
    assert rc == 0, counts
    (tr / "t-one-more").write_text("")
    rc, counts, _ = w.launch(seed=1, dry=True)
    assert rc == 15
    assert_counts(counts, 15, "refused")


# -- 12: an empty wall ---------------------------------------------------------------------------------------------
def test_a_planted_wall_entry_or_tree_folder_12_untouched(w):
    hook = w.hook("if point == 'before_wall':\n"
                  "    os.makedirs(wall)\n"
                  "    open(os.path.join(wall, 'planted.txt'), 'w').write('planted')\n")
    rc, counts, _ = w.launch(seed=1, dry=True, extra={"GOV_INDEP_TEST_HOOK": hook})
    assert rc == 12
    assert_counts(counts, 12, "refused")
    wall = w.wall(counts)
    assert os.listdir(wall) == ["planted.txt"] and (wall / "planted.txt").read_text() == "planted"
    assert w.seeds() == [] and not w.tree(counts).exists()
    hook = w.hook("if point == 'before_wall':\n"
                  "    os.makedirs(os.path.join(tree, 'mine'))\n")
    rc, counts, _ = w.launch(seed=1, dry=True, extra={"GOV_INDEP_TEST_HOOK": hook})
    assert rc == 12
    assert os.listdir(w.tree(counts)) == ["mine"] and not w.wall(counts).exists()


# -- the dry build: B1-B6 ------------------------------------------------------------------------------------------
def test_dry_build_writes_the_wall_by_rule(w):
    rc, counts, p = w.launch(seed=17, dry=True)
    assert rc == 0, p.stderr
    assert_counts(counts, 0, "dry")
    assert w.calls() == []
    wall, tree = w.wall(counts), w.tree(counts)
    # the result line equals counts.json
    assert json.loads((w.runs / "writer" / counts["run"] / "counts.json").read_text()) == counts
    # B2: the seed first
    seed = wall / "seed.txt"
    assert seed.read_text() == "17\n" and stat.S_IMODE(seed.stat().st_mode) == 0o444
    line = w.seeds()[-1]
    assert line["seed"] == 17 and line["seed_sha256"] == sha(seed.read_bytes()) == counts["seed_sha256"]
    assert line["run"] == counts["run"] and line["commit"] == w.commit and line["kind"] == "writer"
    seed_ns = seed.stat().st_mtime_ns
    ledger_ns = (w.runs / "SEEDS.log").stat().st_mtime_ns
    content = [os.path.join(dp, n) for top in (wall / "input", tree) for dp, _d, ns in os.walk(top) for n in ns]
    assert content and all(seed_ns < ledger_ns < os.stat(x).st_mtime_ns for x in content)
    # B3: the tree is the archive less the exclusions, plain and read-only
    ex = [x.strip() for x in (TEMPLATE / "tree-exclude.txt").read_text().splitlines()
          if x.strip() and not x.startswith("#")]
    tracked = w.git("ls-tree", "-r", "--name-only", w.commit).splitlines()
    want = {p for p in tracked if not any(fnmatch.fnmatch(p, g) for g in ex)}
    got = {}
    for dp, dns, ns in os.walk(tree):
        assert stat.S_IMODE(os.stat(dp).st_mode) == 0o555
        assert ".git" not in dns
        for n in ns:
            fp = os.path.join(dp, n)
            assert not os.path.islink(fp) and stat.S_IMODE(os.stat(fp).st_mode) == 0o444
            got[os.path.relpath(fp, tree)] = sha(open(fp, "rb").read())
    assert set(got) == want
    assert all(got[p] == sha(w.blob(w.commit, p)) for p in want)
    assert "tools/run.sh" in got
    # B4: the selection by rule
    sel = json.loads((wall / "input" / "selection.json").read_text())
    others = [p for p in tracked if p in want]
    assert sel == {"commit": w.commit, "last_audit": None, "seed_sha256": counts["seed_sha256"], "changed": [],
                   "sample": random.Random(17).sample(others, 3)}
    assert counts["selection"] == {"changed": 0, "sample": 3, "overlap": 0}
    # B5: the session's files
    assert (wall / "brief.md").read_bytes() == w.blob(w.commit, "governance/project/indep-briefs/writer.md")
    assert (wall / ".claude" / "wall_hook.py").read_bytes() == (TEMPLATE / "wall_hook.py").read_bytes()
    claude_md = (wall / "CLAUDE.md").read_text()
    assert "@" + "KIND@" not in claude_md and w.commit in claude_md and str(tree) in claude_md
    s = json.loads((wall / ".claude" / "settings.json").read_text())
    m = json.loads((wall / "WALL.json").read_text())
    walls = str(w.sets / WALLS)
    need = ["Bash", "WebFetch", "WebSearch", "Task", "Agent", "Bash(gov retrieve *)", "Bash(gov context *)",
            "Bash(git *)", f"Read(/{m['runs']}/**)", f"Read(/{m['home']}/.claude/**)", f"Read(/{m['repo']}/**)",
            f"Read(/{w.sets}/runs/**)", f"Read(/{w.sets}/transcripts/**)", f"Read(/{w.sets}/fixtures/**)",
            f"Read(/{walls}/APPROVED)", f"Edit(/{wall}/.claude/**)", f"Edit(/{tree}/**)",
            f"Read(/{m['home']}/gov-os-worktrees/**)"]
    need += [f"Read(/{walls}/{k}/**)" for k in ("checker", "auditor", "labeller")]
    assert not [x for x in need if x not in s["permissions"]["deny"]]
    assert s["model"] == "claude-haiku-5-5"
    hooks = s["hooks"]["PreToolUse"]
    assert len(hooks) == 1 and hooks[0]["matcher"] == "*"
    assert hooks[0]["hooks"][0]["command"] == f"python3 -I {wall}/.claude/wall_hook.py {wall} {tree}"
    assert stat.S_IMODE((wall / "out").stat().st_mode) == 0o700 and os.listdir(wall / "out") == []
    for d in (wall, wall / ".claude", wall / "input"):
        assert stat.S_IMODE(d.stat().st_mode) & 0o222 == 0
    # B6: the manifest
    for k in ("kind run set round commit repo tree runs home sets_root brief_sha256 seed_sha256 settings_sha256 "
              "hook_sha256 template_sha256 approved_sha256 selection seeded_before_content runs_override "
              "trees_override").split():
        assert k in m, k
    assert m["settings_sha256"] == sha((wall / ".claude" / "settings.json").read_bytes())
    assert m["template_sha256"] == {n: sha((TEMPLATE / n).read_bytes()) for n in TEMPLATE_FILES}
    assert m["seeded_before_content"] is True and m["runs_override"] is False
    assert not str(m["tree"]).startswith(str(w.sets) + "/")
    # no path under the wall printed or logged
    log = (w.runs / "writer" / counts["run"] / "launch.log").read_text()
    for text in (p.stdout, p.stderr, log):
        assert str(wall) not in text and str(tree) not in text


def test_the_second_wall_of_a_kind_denies_the_first(w):
    rc, first, _ = w.launch(seed=1, dry=True)
    rc, second, _ = w.launch(seed=2, dry=True)
    assert rc == 0 and first["run"] != second["run"]
    s = json.loads((w.wall(second) / ".claude" / "settings.json").read_text())
    assert f"Read(/{w.wall(first)}/**)" in s["permissions"]["deny"]


def test_same_seed_same_selection_and_changed_paths_from_the_last_audit(w):
    w.put("docs/note-1.md", "changed\n")
    w.put("fixtures/evaluation/x/hidden/q.yaml", "changed secret\n")
    w.put("docs/new.md", "new\n")
    c = w.commit_all("changes")
    w.approve(c)
    w.runs.mkdir(parents=True)
    (w.runs / "AUDITS.log").write_text(json.dumps({"time": "t", "commit": w.commit, "run": "r", "audit": "e0"}) + "\n")
    rc1, a, _ = w.launch(commit=c, seed=99, dry=True)
    rc2, b, _ = w.launch(commit=c, seed=99, dry=True)
    assert rc1 == rc2 == 0
    sa = json.loads((w.wall(a) / "input" / "selection.json").read_text())
    sb = json.loads((w.wall(b) / "input" / "selection.json").read_text())
    assert sa == sb
    assert sa["changed"] == ["docs/new.md", "docs/note-1.md"] and sa["last_audit"] == w.commit
    assert not set(sa["sample"]) & set(sa["changed"])


def test_two_launches_draw_different_seeds(w):
    w.stub({"canary": "error"})
    rc1, a, _ = w.launch()
    rc2, b, _ = w.launch()
    assert rc1 == rc2 == 16
    seeds = [x["seed"] for x in w.seeds()]
    assert len(seeds) == 2 and seeds[0] != seeds[1] and all(0 <= s < 2 ** 63 for s in seeds)


def test_overrides_are_said_in_the_wall_and_the_counts(w, tmp_path):
    runs, trees = tmp_path / "o-runs", tmp_path / "o-trees"
    rc, counts, _ = w.launch(seed=1, dry=True, extra={"GOV_INDEP_RUNS_DIR": str(runs),
                                                       "GOV_INDEP_TREES_DIR": str(trees)})
    assert rc == 0 and counts["override"] is True
    m = json.loads((w.wall(counts) / "WALL.json").read_text())
    assert m["runs_override"] is True and m["trees_override"] is True
    assert (runs / "indep" / "SEEDS.log").exists() and (trees / f"writer-{counts['run']}").is_dir()
    assert not (w.home / "gov-os-runs").exists()


# -- 13: the seed check --------------------------------------------------------------------------------------------
@pytest.mark.parametrize("how", ["old_input", "seed_rewritten", "ledger_line_gone", "input_first"])
def test_a_forced_reordering_13_no_session_wall_packed(w, how):
    body = {
        "old_input": "if point == 'after_input':\n    os.utime(os.path.join(wall, 'input', 'selection.json'), (1, 1))\n",
        "seed_rewritten": "if point == 'after_input':\n    time.sleep(0.02)\n    os.utime(os.path.join(wall, 'seed.txt'))\n",
        "ledger_line_gone": "if point == 'after_input':\n"
                            "    p = os.path.join(os.environ['HOME'], 'gov-os-runs', 'indep', 'SEEDS.log')\n"
                            "    open(p, 'w').write('')\n",
        "input_first": "if point == 'after_seed':\n    os.makedirs(os.path.join(wall, 'input'))\n"
                       "    open(os.path.join(wall, 'input', 'x'), 'w').write('x')\n",
    }[how]
    w.stub({"session": "write"})
    rc, counts, _ = w.launch(extra={"GOV_INDEP_TEST_HOOK": w.hook(body)})
    assert rc == 13
    assert_counts(counts, 13, "refused")
    assert w.calls() == []
    assert not w.wall(counts).exists() and not w.tree(counts).exists()
    tar = w.sets / WALLS / "writer" / (counts["run"] + ".tar")
    assert stat.S_IMODE(tar.stat().st_mode) == 0o400


# -- 16: the canary ------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("mode", ["garbage", "sleep", "other", "error"])
def test_a_canary_that_is_not_a_refused_read_16(w, mode):
    commit = None
    if mode == "sleep":  # the canary's limit is min(60, timeout_s)
        w.put("governance/project/indep-briefs/writer.md", World.brief_text("writer", timeout_s=2))
        commit = w.commit_all("short")
        w.approve(commit)
    w.stub({"canary": mode, "session": "write"})
    rc, counts, _ = w.launch(commit=commit)
    assert rc == 16
    assert_counts(counts, 16, "refused")
    assert [c["canary"] for c in w.calls()] == [True]
    assert not (w.sets / WALLS / "writer" / (counts["run"] + ".session.json")).exists()
    assert (w.sets / WALLS / "writer" / (counts["run"] + ".tar")).exists()
    assert not w.wall(counts).exists() and not w.tree(counts).exists()


def test_settings_that_do_not_validate_let_the_canary_read_16(w):
    rel = f"governance/project/{WALLS}/settings.json.tmpl"
    w.put(rel, w.blob(w.commit, rel).replace(b'"cleanupPeriodDays": 1', b'"cleanupPeriodDays": "one"'))
    c = w.commit_all("a key of the wrong type")
    w.approve(c)
    w.stub({"session": "write"})
    rc, counts, _ = w.launch(commit=c)
    assert rc == 16
    calls = w.calls()
    assert len(calls) == 1 and calls[0]["canary"]
    target = [x for x in calls[0]["prompt"].split() if x.startswith("/")][0]
    # the canary's target lies in a folder added for the canary only, outside the wall, the tree and every root
    added = [d for d in calls[0]["adds"] if target.startswith(d + "/")]
    assert added and added[0] not in (str(w.tree(counts)),)
    for top in (w.sets, w.home, w.repo):
        assert not target.startswith(str(top) + "/")


def test_canary_runs_with_the_session_flags_plus_its_folder(w):
    w.stub({"session": "write", "out": {"out/result.json": json.dumps(
        {"questions": 1, "by_kind": {"fact": 1}, "by_area": {"docs": 1}}), "out/set/q.yaml": "q\n"}})
    rc, counts, _ = w.launch()
    assert rc == 0, counts
    canary, session = w.calls()
    assert canary["canary"] and not session["canary"]
    assert canary["adds"][0] == session["adds"][0] == str(w.tree(counts))
    assert len(canary["adds"]) == 2 and len(session["adds"]) == 1
    assert {k: v for k, v in canary["flags"].items()} == session["flags"]


# -- the session: S10, S13, S16, S17 -------------------------------------------------------------------------------
def writer_out(marker="MARK-TEXT-zz91"):
    return {"out/result.json": json.dumps({"questions": 2, "by_kind": {"fact": 1, "negative": 1},
                                           "by_area": {"docs": 2}, "note": marker}),
            "out/set/q01.yaml": "q one\n", "out/set/deep/q02.yaml": "q two\n"}


def test_writer_session_is_closed_and_delivers_counts_only(w):
    marker = "MARK-TEXT-zz91"
    w.stub({"session": "write", "out": writer_out(marker), "marker": marker})
    before = indep_launch.hidden_count(str(w.sets), ["indep-walls/**", "transcripts/**"])
    rc, counts, p = w.launch()
    assert rc == 0, p.stderr
    assert_counts(counts, 0, "delivered")
    run = counts["run"]
    session = w.calls()[1]
    wall, tree = w.wall(counts), w.tree(counts)
    a = session["argv"]
    assert a[:6] == ["-p", "--restricted", "--settings", f"{wall}/.claude/settings.json", "--add-dir", str(tree)]
    assert a[6:-1] == ["--tools", "Read,Grep,Glob,Write,Edit,TodoWrite", "--no-session-persistence",
                       "--strict-mcp-config", "--disable-slash-commands", "--permission-prompts", "none", "--model",
                       "claude-haiku-5-5", "--max-budget-usd", "25", "--output-format", "json"]
    assert a[-1] == indep_launch.PROMPT
    assert session["cwd"] == str(wall) and session["stdin_null"]
    assert set(session["env"]) <= {"HOME", "PATH", "LANG", "USER"} and "HOME" in session["env"]
    assert session["parent"] == "timeout" and session["pgid"] != os.getpgid(0)
    cdir = w.runs / "writer" / run
    pid = int((cdir / "session.pid").read_text())
    pgid = int((cdir / "session.pgid").read_text())
    assert pgid == session["pgid"] and pid == session["ppid"]
    # the delivery
    hidden = w.sets / "fixtures" / "evaluation" / SET / "hidden"
    assert sorted(tree_hash(hidden)) == ["deep/", "deep/q02.yaml", "q01.yaml"]
    files = {"q01.yaml": "q one\n", "deep/q02.yaml": "q two\n"}
    bundle = sha("".join(f"{sha(files[p].encode())}  {p}\n" for p in sorted(files)).encode())
    assert counts["delivered"] == {"files": 2, "sha256": bundle, "to": "set"}
    assert counts["out"]["questions"] == 2 and counts["out"]["by_kind"] == {"fact": 1, "negative": 1}
    assert counts["out"]["by_area"] == {"docs": 2} and counts["out"]["files"] == 3
    assert counts["session"]["refusals"]["Read"] == 1 and counts["session"]["refusals"]["other"] == 1
    assert counts["session"]["turns"] == 3 and counts["session"]["duration_s"] == 1.5
    # packed: one file, the wall and its tree gone
    tar = w.sets / WALLS / "writer" / (run + ".tar")
    assert stat.S_IMODE(tar.stat().st_mode) == 0o400
    with tarfile.open(tar) as t:
        names = t.getnames()
    assert f"{run}/WALL.json" in names and f"{run}/out/result.json" in names and f"{run}.session.json" in names
    assert all(n == run + ".session.json" or n == run or n.startswith(run + "/") for n in names)
    assert not wall.exists() and not tree.exists()
    assert not (w.sets / WALLS / "writer" / (run + ".session.json")).exists()
    assert indep_launch.hidden_count(str(w.sets), ["indep-walls/**", "transcripts/**"]) == before + 1
    # no free text anywhere
    log = (cdir / "launch.log").read_text()
    for text in (p.stdout, p.stderr, log, (cdir / "counts.json").read_text()):
        assert marker not in text and "done" not in text and str(wall) not in text


@pytest.mark.parametrize("out", [{}, {"out/result.json": "{not json"},
                                 {"out/result.json": json.dumps({"questions": "two", "by_kind": {}, "by_area": {}})},
                                 {"out/result.json": json.dumps({"questions": 1, "by_kind": {"poem": 1},
                                                                 "by_area": {}})},
                                 {"out/result.json": json.dumps({"questions": 1, "by_kind": {}, "by_area": {}})}])
def test_a_bad_result_is_rejected_20_nothing_delivered(w, out):
    w.stub({"session": "write", "out": out})
    setdir = w.sets / "fixtures" / "evaluation" / SET
    before = tree_hash(w.sets / "fixtures")
    rc, counts, _ = w.launch()
    assert rc == 20
    assert_counts(counts, 20, "rejected")
    assert tree_hash(w.sets / "fixtures") == before and not (setdir / "hidden").exists()
    assert counts["delivered"] == {"files": 0, "sha256": None, "to": None}
    assert (w.sets / WALLS / "writer" / (counts["run"] + ".tar")).exists() and not w.wall(counts).exists()


def test_a_session_past_its_timeout_is_stopped_by_its_group_21(w):
    rel = "governance/project/indep-briefs/writer.md"
    w.put(rel, World.brief_text("writer", timeout_s=2))
    c = w.commit_all("short")
    w.approve(c)
    w.stub({"session": "child", "out": writer_out()})
    rc, counts, _ = w.launch(commit=c)
    assert rc == 21
    assert_counts(counts, 21, "stopped")
    pgid = int((w.runs / "writer" / counts["run"] / "session.pgid").read_text())
    with pytest.raises(ProcessLookupError):
        os.killpg(pgid, 0)
    assert not (w.sets / "fixtures" / "evaluation" / SET / "hidden").exists()
    assert counts["session"]["exit"] in (124, 137)
    assert w.calls()[1]["argv"][w.calls()[1]["argv"].index("--max-budget-usd") + 1] == "25"


def test_a_session_ended_by_its_budget_is_stopped_21(w):
    w.stub({"session": "budget", "out": writer_out()})
    rc, counts, _ = w.launch()
    assert rc == 21 and counts["status"] == "stopped"
    assert not (w.sets / "fixtures" / "evaluation" / SET / "hidden").exists()


def test_a_trace_under_dot_claude_is_counted_22(w):
    w.stub({"session": "trace", "out": writer_out()})
    rc, counts, _ = w.launch()
    assert rc == 22
    assert counts["traces"] == 1 and counts["status"] == "delivered" and counts["reason"] == "trace"


# -- the other kinds -----------------------------------------------------------------------------------------------
def test_checker_delivers_its_notes(w):
    w.plant_set()
    w.stub({"session": "write", "out": {"out/result.json": json.dumps(
        {"checked": 2, "accepted": 1, "revise": 1, "rejected": 0}), "out/notes.md": "notes\n"}})
    rc, counts, _ = w.launch("checker")
    assert rc == 0, counts
    assert w.calls()[1]["input"] == ["selection.json", "set"]
    notes = w.sets / "fixtures" / "evaluation" / SET / "XCHECK-r1.md"
    assert notes.read_text() == "notes\n"
    assert counts["delivered"] == {"files": 1, "sha256": sha(b"notes\n"), "to": "notes"}
    assert counts["out"]["checked"] == 2 and counts["out"]["questions"] is None


def test_auditor_delivers_its_classes_and_the_audit_is_logged(w):
    w.plant_set()
    (w.sets / "runs" / "e0").mkdir(parents=True)
    (w.sets / "runs" / "e0" / "misses.jsonl").write_text('{"q": 1}\n')
    w.stub({"session": "write", "out": {"out/result.json": json.dumps({"misses": {"retrieval_miss": 2}}),
                                        "out/classes.json": "{}\n"}})
    rc, counts, _ = w.launch("auditor", audit="e0")
    assert rc == 0, counts
    assert w.calls()[1]["input"] == ["misses.jsonl", "selection.json", "set"]
    assert (w.sets / "runs" / "e0" / "miss-classes.json").read_text() == "{}\n"
    line = json.loads((w.runs / "AUDITS.log").read_text().splitlines()[-1])
    assert line["commit"] == w.commit and line["run"] == counts["run"] and line["audit"] == "e0"
    assert counts["out"]["misses"] == {"retrieval_miss": 2}


def test_labeller_delivers_into_the_sealed_folder(w):
    seal = w.plant_seal()
    w.stub({"session": "write", "out": {"out/result.json": json.dumps({"labelled": 3, "allow": 2, "refuse": 1}),
                                        "out/labels.jsonl": '{"id": "a000"}\n'}})
    rc, counts, _ = w.launch("labeller")
    assert rc == 0, counts
    assert (seal / "labels" / f"{counts['run']}.jsonl").read_text() == '{"id": "a000"}\n'
    assert counts["delivered"]["to"] == "labels" and counts["out"]["agree"] is None


def test_second_labeller_overlap_is_ten_percent_by_the_seed(w):
    seal = w.plant_seal(n1=23, n2=5)
    rc1, a, _ = w.launch("labeller", rnd=2, seed=4242, dry=True)
    rc2, b, _ = w.launch("labeller", rnd=2, seed=4242, dry=True)
    assert rc1 == rc2 == 0
    sa = json.loads((w.wall(a) / "input" / "selection.json").read_text())
    sb = json.loads((w.wall(b) / "input" / "selection.json").read_text())
    ids1 = [f"a{i:03d}" for i in range(23)]
    assert sa["overlap"] == sb["overlap"] == random.Random(4242).sample(ids1, math.ceil(23 / 10))
    assert a["selection"]["overlap"] == 3
    acts = (w.wall(a) / "input" / "actions.jsonl").read_text().splitlines()
    assert [json.loads(x)["id"] for x in acts] == [f"b{i:03d}" for i in range(5)] + sa["overlap"]
    assert (w.wall(a) / "input" / "rulebook.md").read_text() == (seal / "rulebook.md").read_text()
    rc, one, _ = w.launch("labeller", seed=4242, dry=True, set_name="labels-one")
    assert (w.wall(one) / "input" / "actions.jsonl").read_bytes() == (seal / "corpus" / "actions-r1.jsonl").read_bytes()


def test_writer_round_two_replaces_its_set_inside_hidden(w):
    hidden = w.plant_set({"old.yaml": "old\n"})
    (hidden.parent / "XCHECK-r1.md").write_text("check notes\n")
    w.stub({"session": "write", "out": writer_out()})
    rc, counts, _ = w.launch(rnd=2)
    assert rc == 0, counts
    assert w.calls()[1]["input"] == ["notes.md", "selection.json", "set"]
    assert sorted(tree_hash(hidden)) == ["deep/", "deep/q02.yaml", "q01.yaml"]
    assert sorted(os.listdir(hidden.parent)) == ["README.md", "XCHECK-r1.md", "hidden"]
    with tarfile.open(w.sets / WALLS / "writer" / (counts["run"] + ".tar")) as t:
        assert f"{counts['run']}/replaced-hidden/old.yaml" in t.getnames()


def test_writer_round_one_makes_a_new_sets_folder(w):
    w.stub({"session": "write", "out": writer_out()})
    rc, counts, _ = w.launch(set_name="brand-new-set")
    assert rc == 0, counts
    hidden = w.sets / "fixtures" / "evaluation" / "brand-new-set" / "hidden"
    assert sorted(tree_hash(hidden)) == ["deep/", "deep/q02.yaml", "q01.yaml"]


def test_writer_round_one_over_an_existing_hidden_is_rejected_20(w):
    hidden = w.plant_set({"old.yaml": "old\n"})
    before = tree_hash(hidden.parent)
    w.stub({"session": "write", "out": writer_out()})
    rc, counts, _ = w.launch()
    assert rc == 20 and counts["status"] == "rejected"
    assert tree_hash(hidden.parent) == before


# -- --counts-only -------------------------------------------------------------------------------------------------
def test_counts_only_prints_the_runs_counts(w):
    rc, counts, _ = w.launch(seed=3, dry=True)
    rc, again, p = w.run("--sets-root", str(w.sets), "--kind", "writer", "--run", counts["run"], "--counts-only")
    assert rc == 0 and again == counts
    rc, _, _ = w.run("--sets-root", str(w.sets), "--kind", "writer", "--run", "20990101T000000Z-x-r1",
                     "--counts-only")
    assert rc == 17


# -- the schema checker ----------------------------------------------------------------------------------------
def test_schema_checker_is_strict():
    s = json.loads((SCHEMAS / "checker-result.schema.json").read_text())
    assert indep_launch.schema_ok({"checked": 1, "accepted": 1, "revise": 0, "rejected": 0, "x": "y"}, s)
    assert not indep_launch.schema_ok({"checked": True, "accepted": 1, "revise": 0, "rejected": 0}, s)
    assert not indep_launch.schema_ok({"checked": -1, "accepted": 1, "revise": 0, "rejected": 0}, s)
    assert not indep_launch.schema_ok({"checked": 1}, s)
    assert not indep_launch.schema_ok(1, {"type": "integer", "format": "x"})  # an unknown keyword fails closed


def test_counts_schema_closes_every_object_and_string():
    whole = schema()
    out = whole["properties"]["out"]["properties"]
    as_given = [out["by_kind"], out["by_area"], out["misses"]]  # the result's own counts, copied as given

    def walk(node):
        if isinstance(node, dict):
            t = node.get("type")
            types = t if isinstance(t, list) else [t]
            if "object" in types:
                assert node.get("additionalProperties") is False, node
                if not any(node is x for x in as_given):
                    assert set(node.get("required", [])) == set(node.get("properties", {})), node
            if "string" in types:
                assert "enum" in node or "const" in node or node.get("pattern", "").startswith("^"), node
                if "pattern" in node:
                    assert node["pattern"].endswith("$")
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    walk(whole)


def test_a_signal_to_the_script_is_not_needed_for_cleanup_by_name():
    # the stop path is by process group id only (os.killpg), as the timeout case shows
    src = SCRIPT.read_text()
    assert "os.killpg" in src and "signal.SIGKILL" in src
    assert signal.SIGKILL
