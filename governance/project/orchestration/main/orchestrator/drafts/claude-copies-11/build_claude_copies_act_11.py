"""Builds and rehearses ACT-CLAUDE-COPIES-11 (the generated .claude/skills/{frontend,ui-ux,devops}/ copies of W2-101's
three new kernel skills; under the owner's CIT-P approval of W2-101, pending: "yes W2-101-CIT-P 42c1cc38"; DEC-315,
DEC-1112 (3), CAP-33). Copied from drafts/claude-copies-10/build_claude_copies_act_10.py (not edited; nor is COPIES-9's).
Changes from COPIES-10's builder:

  * the skills are W2-101's three (frontend, ui-ux, devops): 15 targets, 45 sources (check 2), 9 named cases; the
    sources' sha256 are W2-101's CIT-P section 3 (docs/changes/W2-101-CIT-P.md at 3bf1c96b47c1, sha256 42c1cc38...,
    asserted), the kernel bytes as at the verified product head 1ef54a70037a; the commits after it are asserted to
    touch only docs/probes/ and docs/changes/;
  * order 1 (BASE): a clone of integrate with refs/heads/w2/W2-101 (head 3bf1c96b47c1, asserted) merged by one --no-ff
    commit (the CTO's hand merge, Task: DAEO-6icv); everything COPIES-10 did on its merged tree is done here on it
    (generation, bundle, apply/undo/re-apply, plain integrate, moved target, gated runs window and landed, the named
    cases, the by-hand steps);
  * order 2 (new): a clone of integrate with refs/heads/w2/W2-100 (cdac25763613, asserted) merged --no-ff, ACT-CLAUDE-
    COPIES-10 applied by its own apply.sh (its check, apply and both manifest checks) and committed, then w2/W2-101
    merged --no-ff, then this bundle (the same bytes) applied. Asserted there: each merge is clean; check 2 red after
    COPIES-10 without W2-101 and green after W2-101's merge (so it stays green with or without W2-100); COPIES-10's
    checks still green after this ACT; rulesync from the landed tree's root .rulesync renders every file of all seven
    skills' folders equal to the tree (only .claude/settings.json differs, as on integrate); portability exits 0 with
    no finding; the gated runs of W2-100, W2-101, W2-11 (the four-places suite) and tests/unit/adapters are clean; the
    named cases for all seven skills PASSED (window: W2-101's nine FAILED, W2-100's twelve PASSED);
  * the gated runs of order 1: W2-101 replaces W2-100 at the head of the list (W2-100's folder is not on that tree);
  * portability() takes the tree's own src/ when asked (order 2's tree), else the generation clone's as before;
  * targeted() takes its list of (folder, ids) and its own label;
  * gated outputs and the operator-gate evidence go to drafts/claude-copies-11/evidence/; pytest's TMPDIR is
    /tmp/gov-os-cto-f388 (the CTO's rule); the rehearsal commits carry Task: DAEO-6icv (W2-101's ticket).

    python3 -I build_claude_copies_act_11.py <INTEGRATE clone> <bundle dir> <scratch dir> [ACT id]
"""
import hashlib, json, os, re, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

INTEG, BUNDLE, SCRATCH = (Path(a).resolve() for a in sys.argv[1:4])
ACT = sys.argv[4] if len(sys.argv) > 4 else "ACT-CLAUDE-COPIES-11"
LIVE_TREE = Path("/home/usain/Dynamic-Agentic-Engineering-OS")      # read-only: the branch to merge, and proof the rehearsal left it alone
ORCH = LIVE_TREE / ".gov-runtime/scratch/orchestrator"
HEAVY = str(ORCH / "tools/heavy_slot.sh")
EVID = ORCH / "drafts/claude-copies-11/evidence"
C7 = ORCH / "acts/ACT-CLAUDE-COPIES-7"
C9 = ORCH / "acts/ACT-CLAUDE-COPIES-9"
C10 = ORCH / "acts/ACT-CLAUDE-COPIES-10"                              # read-only: applied in order 2's clone only
W2101 = "3bf1c96b47c1"
PRODUCT_HEAD = "1ef54a70037a"
W2100 = "cdac25763613"
CITP = "docs/changes/W2-101-CIT-P.md"
CITP_SHA = "42c1cc38f4c985afc23609bb999b95a5207ee6e434b057b40dd4dd7419c5cb27"
SKILLS = ("frontend", "ui-ux", "devops")
W2100_SKILLS = ("backend", "api", "data", "security")
CHECK_PY = "3532f93de84972ded38ef7725dac323f45bab78e5c4735dc90d8ed84ddc9d62a"
SRC_SHA = {   # W2-101's CIT-P section 3, "after" at 1ef54a70037a (kernel = root .rulesync = template/.rulesync)
    "frontend": {"SKILL.md": "ac86c6384f58c1dcf1f94efe93a5490f88d92ea06bc90aae062da96c11805edc",
                 "check_domain_skill.py": CHECK_PY,
                 "scenario-records.yaml": "44f6d05d0f56d526cec2d7c0f2c8e945b5088180ceabbf16d532a495a07cdcfd",
                 "scenario-summaries.md": "a3f597664ece8d9e9e690b8db9cca99360b4988df3d38619d329cfed7fc1a11d",
                 "scenarios.md": "d572be6bb9143e2a70e4499771e554ba2bba16a259c2601417c84f2dac60640a"},
    "ui-ux": {"SKILL.md": "9a50b6f26539936f50775b65eea717a5906c841aa5cf033f04da39c400f8be54",
              "check_domain_skill.py": CHECK_PY,
              "scenario-records.yaml": "9b038c094435183aa0866866222f8f5931f69e9dc0285bd28fa290514eaf146e",
              "scenario-summaries.md": "665707193be00eb7f888a623b55327e043bd95617a1a9279be177363c202895b",
              "scenarios.md": "714ecf9e1d15b597c3dd938fc2427218b52ba403cbd79e4f12cb5d5bf9caabc9"},
    "devops": {"SKILL.md": "468257eb1ee4ee66b1c36cf388ae05b4808ef807533b7655f9c54cf4684b6fd3",
               "check_domain_skill.py": CHECK_PY,
               "scenario-records.yaml": "87f6c71296571252c7bd82b4f0062c03be7f8396a1bf8c13c4d7a5f7edd25b28",
               "scenario-summaries.md": "6b5c340edba9fbee9d2a4664749fe34de99eeae8d4c7d4fbbbd125c0681575f0",
               "scenarios.md": "a6a737c6c2db84d0b905f38c3532337b9387b4d0ab70b87f2c9fe963a19dd5d9"},
}
SOURCE_ROOTS = ("template/governance/kernel/skills", ".rulesync/skills", "template/.rulesync/skills")
PINS = {f"{root}/{sk}/{name}": h for root in SOURCE_ROOTS for sk in SKILLS for name, h in SRC_SHA[sk].items()}
EXPECTED_TOUCHED = sorted(f".claude/skills/{sk}/{name}" for sk in SKILLS for name in SRC_SHA[sk])
OUR_PREFIXES = tuple(f"{root}/{sk}/" for sk in SKILLS for root in (*SOURCE_ROOTS, ".claude/skills"))
GENERATED_FOLDERS = (".claude/agents", ".claude/skills", ".claude/commands")
GENERATE = ["generate", "--targets", "claudecode,agentsmd", "--features",
            "rules,hooks,permissions,subagents,commands,skills", "--input-roots"]
RULESYNC = shutil.which("rulesync") or str(Path.home() / ".local/bin/rulesync")
GATED = ["tests/acceptance/W2-101", "tests/acceptance/W2-11", "tests/unit/adapters", "tests/acceptance/W1-33",
         "tests/acceptance/W1-38", "tests/acceptance/W2-153", "tests/acceptance/W2-98", "tests/acceptance/W2-88a",
         "tests/acceptance/W2-52", "tests/acceptance/W2-37"]
GATED_O2 = ["tests/acceptance/W2-100", "tests/acceptance/W2-101", "tests/acceptance/W2-11", "tests/unit/adapters"]
T101 = ("tests/acceptance/W2-101",
        ["tests/acceptance/W2-101/test_w2_101_copies.py::test_the_claude_copy_matches_the_kernel_source",
         "tests/acceptance/W2-101/test_w2_101_copies.py::test_the_adapter_check_finds_no_generated_drift_in_the_real_skill"])
T100 = ("tests/acceptance/W2-100",
        ["tests/acceptance/W2-100/test_w2_100_copies.py::test_the_claude_copy_matches_the_kernel_source",
         "tests/acceptance/W2-100/test_w2_100_copies.py::test_the_adapter_check_finds_no_generated_drift_in_the_real_skill"])
T11 = ("tests/acceptance/W2-11",
       ["tests/acceptance/W2-11/test_w2_11_skills.py::test_the_skill_carries_one_version_in_all_four_places"])
TARGETED = [T101, T11]
TARGETED_O2 = [T100, T101, T11]
TMP = Path("/tmp/gov-os-cto-f388")
HOME_RX = re.compile(r"/home/[A-Za-z0-9_.-]+/")
APPLY_SH = (C10 / "apply.sh").read_text()   # the same apply.sh as ACT-CLAUDE-COPIES-1 to -10
assert APPLY_SH == (C9 / "apply.sh").read_text() == (C7 / "apply.sh").read_text()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def run(cmd, cwd, env=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    return r.returncode, (r.stdout + r.stderr).strip()


def clone(src, dest):
    if dest.exists():
        shutil.rmtree(dest)
    head = run(["git", "rev-parse", "HEAD"], src)[1]
    assert run(["git", "clone", "-q", "--no-hardlinks", str(src), str(dest)], SCRATCH)[0] == 0
    assert run(["git", "checkout", "-q", head], dest)[0] == 0
    return head


log = []
def say(line):
    log.append(line)
    print(line, flush=True)


GIT = "git -c user.name=rehearsal -c user.email=rehearsal@example.invalid"
GITC = ["git", "-c", "user.name=rehearsal", "-c", "user.email=rehearsal@example.invalid"]
SCRATCH.mkdir(parents=True, exist_ok=True)
TMP.mkdir(exist_ok=True)
EVID.mkdir(parents=True, exist_ok=True)
INTEG_HEAD = run(["git", "rev-parse", "HEAD"], INTEG)[1]
assert run(["git", "status", "--porcelain", "--untracked-files=all"], INTEG)[1] == ""
LIVE_INTEG = run(["git", "rev-parse", "refs/heads/w2/integrate"], LIVE_TREE)[1]
assert INTEG_HEAD == LIVE_INTEG, f"the integrate clone is at {INTEG_HEAD[:12]}, live w2/integrate at {LIVE_INTEG[:12]}"


def merge(tree, ref, name):
    """One --no-ff merge commit; returns (merge base, files brought, conflicts)."""
    mb = run(["git", "merge-base", "HEAD", ref], tree)[1]
    code, out = run([*GITC, "merge", "--no-ff", "-q", "-m", f"Merge {name} (rehearsal of the CTO's hand merge)", ref], tree)
    conflicts = run(["git", "diff", "--name-only", "--diff-filter=U"], tree)[1].splitlines()
    assert code == 0 and not conflicts, (code, out, conflicts)
    assert run(["git", "status", "--porcelain", "--untracked-files=all"], tree)[1] == ""
    return mb, run(["git", "diff", "--name-only", "HEAD^1", "HEAD"], tree)[1].splitlines(), conflicts


# BASE (order 1): integrate with w2/W2-101 merged by one commit, as after the CTO's hand merge
BASE = SCRATCH / "base-merged"
clone(INTEG, BASE)
assert run(["git", "fetch", "-q", str(LIVE_TREE), "refs/heads/w2/W2-101:refs/heads/w2/W2-101"], BASE)[0] == 0
w2101_head = run(["git", "rev-parse", "--short=12", "refs/heads/w2/W2-101"], BASE)[1]
assert w2101_head == W2101, f"w2/W2-101 is at {w2101_head}, not the approved {W2101}"
late = run(["git", "diff", "--name-only", PRODUCT_HEAD, "refs/heads/w2/W2-101"], BASE)[1].splitlines()
assert late and all(p.startswith(("docs/probes/", "docs/changes/")) for p in late), late
citp = subprocess.run(["git", "show", f"refs/heads/w2/W2-101:{CITP}"], cwd=BASE, capture_output=True).stdout
assert sha(citp) == CITP_SHA, f"the CIT-P at the branch head is {sha(citp)}"
mbase, merged_names, _ = merge(BASE, "refs/heads/w2/W2-101", "w2/W2-101")
gen = SCRATCH / "gen-clone"
clone(BASE, gen)
say(f"{ACT} rehearsal; base (order 1): integrate {INTEG_HEAD[:12]} with w2/W2-101 {W2101} merged (one --no-ff commit, "
    f"clean: no conflict, merge base {mbase[:12]}, {len(merged_names)} files brought); rulesync "
    f"{run([RULESYNC, '--version'], SCRATCH)[1]}")
say(f"the commits after the verified product head {PRODUCT_HEAD} touch only {late}; the CIT-P at the branch head is "
    f"{CITP_SHA[:8]}")
assert not any(p.startswith(".claude/") for p in merged_names), "the merge brings a .claude file"

# the sources at W2-101's approved bytes, on the merged tree and in the branch's own objects
for rel, h in PINS.items():
    assert sha((gen / rel).read_bytes()) == h, f"{rel} is not at {h}"
    shown = subprocess.run(["git", "show", f"refs/heads/w2/W2-101:{rel}"], cwd=BASE, capture_output=True).stdout
    assert sha(shown) == h, f"the branch's {rel} is not the approved bytes"
for sk in SKILLS:
    for root in SOURCE_ROOTS:
        on_disk = sorted(p.name for p in (gen / root / sk).rglob("*") if p.is_file())
        assert on_disk == sorted(SRC_SHA[sk]), f"{root}/{sk} holds {on_disk}"
    for root in (*SOURCE_ROOTS, ".claude/skills"):
        assert not (INTEG / root / sk).exists(), f"{root}/{sk} is on integrate"
say(f"the {len(PINS)} sources (the five files of each of {list(SKILLS)} in {list(SOURCE_ROOTS)}) are at W2-101's CIT-P "
    f"section 3 hashes, on the merged tree and in w2/W2-101 {W2101}; none is on plain integrate")


def portability(tree, rulesync=True, src=None):
    env = dict(os.environ, PYTHONPATH=str(src or (gen / "src")), RULESYNC_BIN=RULESYNC if rulesync else "/nonexistent/rulesync")
    code, out = run([sys.executable, "-m", "gov.adapters.portability"], tree, env)
    return code, (json.loads(out)["findings"] if out.startswith("{") else [{"code": "UNREADABLE", "message": out[-300:]}])


def tally(found):
    n = {}
    for f in found:
        n[f["code"]] = n.get(f["code"], 0) + 1
    return ", ".join(f"{k} {v}" for k, v in sorted(n.items())) or "none"


def ours(found):
    return [f for f in found if str(f.get("file", "")).startswith(OUR_PREFIXES)]


def others(found):
    return sorted((f["code"], f.get("file", "")) for f in found if f not in ours(found))


code, int_found = portability(INTEG)
say(f"portability on plain integrate: exit {code}; {len(int_found)} findings: {tally(int_found)}; "
    f"files {sorted(f.get('file') for f in int_found)}")
OTHERS_INTEG = others(int_found)
assert not ours(int_found), int_found
code, base_found = portability(gen)
BASE_OURS = sorted((f["code"], f.get("file")) for f in ours(base_found))
say(f"portability on the merged tree (no copies): exit {code}; {len(base_found)} findings: {tally(base_found)}; "
    f"of them the three skills': {len(BASE_OURS)} ({tally(ours(base_found))})")
BASE_OTHERS = others(base_found)
assert BASE_OTHERS == OTHERS_INTEG, "W2-101's merge changes a finding that is not the three skills'"
assert BASE_OURS == sorted(("GENERATED_DIFFERS", p) for p in EXPECTED_TOUCHED), BASE_OURS
say(f"  the three skills' findings are GENERATED_DIFFERS for exactly the {len(EXPECTED_TOUCHED)} absent .claude copies; "
    f"no SOURCE_ finding; the others ({len(BASE_OTHERS)}) are integrate's own")


def fresh_generation(root):
    """rulesync's output from root/.rulesync into a fresh folder (a TemporaryDirectory)."""
    d = tempfile.TemporaryDirectory()
    code, out = run([RULESYNC, *GENERATE, str((root / ".rulesync").resolve())], d.name)
    assert code == 0, out
    return d


def differing(fresh, tree):
    return sorted(str(p.relative_to(fresh)) for p in Path(fresh).rglob("*")
                  if p.is_file() and not ((tree / p.relative_to(fresh)).is_file()
                                           and (tree / p.relative_to(fresh)).read_bytes() == p.read_bytes()))


# the generation on the unchanged integrate (for the known drift) and on the merged tree
with fresh_generation(INTEG) as fresh:
    differ_int = differing(fresh, INTEG)
say(f"rulesync from plain integrate's root .rulesync: differs from the tree in {differ_int}")
rendered = {}
with fresh_generation(gen) as fresh:
    differ0 = differing(fresh, gen)
    for sk in SKILLS:
        folder = Path(fresh) / ".claude/skills" / sk
        rendered[sk] = sorted(str(p.relative_to(folder)) for p in folder.rglob("*") if p.is_file())
    made = {rel: (Path(fresh) / rel).read_bytes() for rel in EXPECTED_TOUCHED if (Path(fresh) / rel).is_file()}
    wrote_sources = [str(p.relative_to(fresh)) for p in Path(fresh).rglob("*")
                     if p.is_file() and str(p.relative_to(fresh)).startswith(("template/", ".rulesync/"))]
for sk in SKILLS:
    say(f"rulesync renders .claude/skills/{sk}/: {rendered[sk]}")
assert all(rendered[sk] == sorted(SRC_SHA[sk]) for sk in SKILLS), "rulesync does not render every file of a skill folder"
say("  rulesync renders all five files of each skill folder (SKILL.md re-rendered, the other four copied)")
assert sorted(made) == EXPECTED_TOUCHED, sorted(made)
assert not wrote_sources, f"the generation writes under a source folder: {wrote_sources}"
TOUCHED = sorted(r for r in differ0 if r.startswith(GENERATED_FOLDERS))
assert TOUCHED == EXPECTED_TOUCHED, TOUCHED
not_written = [r for r in differ0 if r not in TOUCHED]
assert not_written == differ_int, (not_written, differ_int)
assert all(r == ".claude/settings.json" for r in not_written), not_written
say(f"rulesync's other output that differs from the tree (not written, not this ACT's, the same on plain integrate): "
    f"{not_written}")
for rel in TOUCHED:
    sk, name = rel.split("/")[2], rel.split("/")[3]
    if name != "SKILL.md":
        assert sha(made[rel]) == SRC_SHA[sk][name], f"{rel} is not a byte copy of its kernel file"
    else:
        assert sha(made[rel]) != SRC_SHA[sk][name], f"{rel} is not re-rendered"
        text = made[rel].decode()
        assert text.startswith("---\n") and "metadata:" in text, f"{rel} carries no metadata front matter"
say("  every non-SKILL.md copy is byte-equal to its kernel file; each SKILL.md is rulesync's rendering: " +
    ", ".join(f"{sk} {sha(made[f'.claude/skills/{sk}/SKILL.md'])[:8]} ({len(made[f'.claude/skills/{sk}/SKILL.md'])} bytes)"
              for sk in SKILLS))
before_bytes = {rel: None for rel in TOUCHED}
for rel in TOUCHED:
    assert not (gen / rel).exists()
    (gen / rel).parent.mkdir(parents=True, exist_ok=True)
    (gen / rel).write_bytes(made[rel])
code, after = portability(gen)
say(f"portability in the generation clone after the {len(TOUCHED)} copies: exit {code}; the three skills' findings "
    f"{ours(after)}; the others unchanged: {others(after) == BASE_OTHERS}")
assert not ours(after) and others(after) == BASE_OTHERS, after
tcode, tfound = portability(gen / "template", rulesync=False)
say(f"portability on template/ (as an adopted project, no rulesync): {len(ours(tfound))} findings for the three skills; "
    f"others: {tally([f for f in tfound if f not in ours(tfound)])}")
assert not ours(tfound), tfound
changed = run(["git", "status", "--porcelain", "--untracked-files=all"], gen)[1].splitlines()
assert sorted(l.strip().split(None, 1)[1] for l in changed) == TOUCHED, changed
say(f"generation clone: {len(TOUCHED)} files new: " + ", ".join(TOUCHED))

# the bundle: every target absent on integrate and on the merged tree
if BUNDLE.exists():
    shutil.rmtree(BUNDLE)
BUNDLE.mkdir(parents=True)
files, touched, lines = {}, [], []
def put(rel, data):
    p = BUNDLE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    files[rel] = sha(data)


for rel in TOUCHED:
    assert not (INTEG / rel).exists() and not (BASE / rel).exists(), f"{rel}: present before the ACT"
    new = (gen / rel).read_bytes()
    after_h = sha(new)
    put(f"after/repo/{rel}", new)
    touched.append({"root": "repo", "path": rel, "before": None, "after": after_h})
    lines.append(f"repo|{rel}|null|{after_h}")
say(f"the before-state is absent for all {len(touched)} targets, on integrate and on the merged tree (no before/ file, "
    "as COPIES-7)")
put("list.txt", ("\n".join(lines) + "\n").encode())
put("apply.sh", APPLY_SH.encode())
os.chmod(BUNDLE / "apply.sh", 0o755)


def sha_check(pairs):
    return "sha256sum -c - <<'EOF'\n" + "\n".join(f"{h}  {p}" for p, h in pairs) + "\nEOF"
copies = [(t["path"], t["after"]) for t in touched]
sources = list(PINS.items())
checks = [{"cmd": sha_check(sorted(copies)), "exit": 0, "count": None},
          {"cmd": sha_check(sorted(sources)), "exit": 0, "count": None}]
assert not HOME_RX.search(json.dumps(checks)) and "~" not in json.dumps(checks) and "HOME" not in json.dumps(checks)
say(f"check 1: the {len(copies)} copies; check 2: the {len(sources)} sources (W2-101's CIT-P section 3, kernel, root "
    ".rulesync and template/.rulesync); no live HOME path in either")

planted = Path(tempfile.mkdtemp(prefix="planted-home-", dir=SCRATCH))  # the operator's G8 plants HOME the same way
live_state = lambda: {rel: (sha((LIVE_TREE / rel).read_bytes()) if (LIVE_TREE / rel).is_file() else None) for rel in TOUCHED}
live_before = live_state()
fails = 0


def mark(ok, text):
    global fails
    fails += 0 if ok else 1
    say(f"{'ok  ' if ok else 'FAIL'} {text}")
    return ok


def step(tree, name, cmd, expect=0):
    code, out = run(["bash", "-c", cmd], tree, dict(os.environ, HOME=str(planted)))
    mark(code == expect, f"{name}: exit {code}{(' ' + out[-300:]) if out and code != expect else ''}")
    return code, out


def tree_state(tree):
    return {rel: ((tree / rel).read_bytes() if (tree / rel).is_file() else None) for rel in TOUCHED}


def changed_set(tree):
    st = run(["git", "status", "--porcelain", "--untracked-files=all"], tree)[1].splitlines()
    return sorted(l.strip().split(None, 1)[1] for l in st)


SUMMARY = re.compile(r"^(?:\d+ (?:passed|failed|errors?|skipped|xfailed|xpassed|deselected|warnings?)(?:, )?)+ in [\d.]+s(?: \(.*\))?$")
FAILED_LINE = re.compile(r"^(?:FAILED|ERROR) (\S+)")
STATUS_LINE = re.compile(r"^(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS) (\S+)")


def pytest_env(tree):
    return dict(os.environ, PYTHONPATH=str(tree / "src"), TMPDIR=str(TMP), PYTHONUSERBASE="/home/usain/.local")


def pytest_cmd(tree, args):
    return ["bash", HEAVY, "env", f"TMPDIR={TMP}", f"PYTHONPATH={tree / 'src'}", "PYTHONUSERBASE=/home/usain/.local",
            "python3", "-m", "pytest", *args, "-p", "no:cacheprovider", "-o", "tmp_path_retention_policy=failed"]


def gated(tree, folder, label):
    """One folder, one pytest run, through the heavy-job gate; the result from pytest's own summary line and its -rfE
    lines (anchored at the line's start)."""
    code, out = run(pytest_cmd(tree, [folder, "-q", "-rfE"]), tree, pytest_env(tree))
    summary = [ln.strip() for ln in out.splitlines() if SUMMARY.match(ln.strip())]
    m = {k.rstrip("s") if k.startswith("error") else k: int(v)
         for v, k in re.findall(r"(\d+) (passed|failed|errors?|skipped)", summary[-1] if summary else "")}
    failed = sorted({mm.group(1) for ln in out.splitlines() if (mm := FAILED_LINE.match(ln.strip()))})
    (EVID / f"{label}-{folder.replace('/', '_')}.txt").write_text(out + "\n")
    return folder, code, m, bool(summary), failed


def gated_all(tree, label, folders=GATED):
    with ThreadPoolExecutor(max_workers=3) as pool:
        return list(pool.map(lambda f: gated(tree, f, label), folders))


def targeted(tree, label, targets=TARGETED):
    """The named cases, one run per folder, with each case's own status (-rA)."""
    status = {}
    for folder, ids in targets:
        code, out = run(pytest_cmd(tree, [*ids, "-q", "-rA"]), tree, pytest_env(tree))
        (EVID / f"{label}-targeted-{folder.replace('/', '_')}.txt").write_text(out + "\n")
        for ln in out.splitlines():
            mm = STATUS_LINE.match(ln.strip())
            if mm:
                status[mm.group(2)] = mm.group(1)
    return status


# 1. apply, verify, undo, re-apply on the merged tree
say("--- order 1: rehearsal on integrate with W2-101 merged (the tree after the hand merge's merge commit); HOME planted")
reh = SCRATCH / "rehearsal-merged"
clone(BASE, reh)
win = SCRATCH / "window-merged"
clone(BASE, win)
before_state = tree_state(reh)
step(reh, "apply.sh check (every target at its stated before state: absent)", f"bash {BUNDLE}/apply.sh check")
step(reh, "check 1 before the apply (red, as intended: the copies are absent)", checks[0]["cmd"], expect=1)
step(reh, "check 2 before the apply (green: W2-101's forty-five sources at the approved bytes)", checks[1]["cmd"])
step(reh, "apply.sh apply", f"bash {BUNDLE}/apply.sh apply")
for i, c in enumerate(checks, 1):
    step(reh, f"check {i} (sha256sum -c, {len(c['cmd'].splitlines()) - 2} files)", c["cmd"])
mark(changed_set(reh) == TOUCHED, f"the changed set equals the touched list ({len(TOUCHED)} files)")
after_state = tree_state(reh)
mark(all(sha(after_state[t["path"]]) == t["after"] for t in touched), "every target is at its stated after sha256")
pcode, pfound = portability(reh)
mark(not ours(pfound) and others(pfound) == BASE_OTHERS,
     f"portability after the apply: exit {pcode}; the three skills' findings {ours(pfound)}; the {len(BASE_OTHERS)} "
     "others (integrate's own) unchanged")
step(reh, "apply.sh undo", f"bash {BUNDLE}/apply.sh undo")
mark(tree_state(reh) == before_state and changed_set(reh) == [], "undo: every file removed again, the tree clean")
pcode, pfound = portability(reh)
mark(sorted((f["code"], f.get("file")) for f in pfound) == sorted((f["code"], f.get("file")) for f in base_found),
     f"portability after the undo: exit {pcode}; {len(pfound)} findings: {tally(pfound)} (the merged tree's own reading)")
step(reh, "apply.sh check after the undo", f"bash {BUNDLE}/apply.sh check")
step(reh, "apply.sh apply (re-apply)", f"bash {BUNDLE}/apply.sh apply")
mark(tree_state(reh) == after_state and changed_set(reh) == TOUCHED,
     "the re-apply gives the same bytes and the same changed set as the first apply")

# 2. plain integrate: the check passes (the targets are absent there too); check 2 is red, so G8 refuses
say("--- plain integrate (W2-101 not merged)")
ri = SCRATCH / "rehearsal-integrate"
clone(INTEG, ri)
step(ri, "apply.sh check passes on plain integrate (the fifteen copies are absent there as on the merged tree)",
     f"bash {BUNDLE}/apply.sh check")
step(ri, "check 2 is red on plain integrate (W2-101's sources are absent: the order is held)", checks[1]["cmd"], expect=1)
mark(changed_set(ri) == [], "check changed nothing")
# a moved target is refused: a file planted where a copy is to go
mv = SCRATCH / "rehearsal-moved"
clone(BASE, mv)
(mv / EXPECTED_TOUCHED[0]).parent.mkdir(parents=True, exist_ok=True)
(mv / EXPECTED_TOUCHED[0]).write_bytes(b"x\n")
step(mv, f"apply.sh check refuses a moved target (a file planted at {EXPECTED_TOUCHED[0]}; exit 3)",
     f"bash {BUNDLE}/apply.sh check", expect=3)

# 3. the gated runs: window and landed on the merged tree
say("--- order 1, the gated runs, one folder per run through the heavy-job gate: on the merged tree (W2-101's merge "
    "alone, then with this ACT)")
results = {"window": {r[0]: r for r in gated_all(win, "merged-window")},
           "landed": {r[0]: r for r in gated_all(reh, "merged-landed")}}
rw, ra = results["window"], results["landed"]
red_w, red_a = set(), set()
for folder in GATED:
    _, code, m, ok, failed = rw[folder]
    red_w |= set(failed)
    say(f"merged window {folder}: exit {code}; {m.get('passed', 0)} passed, {m.get('failed', 0) + m.get('error', 0)} failed"
        + (f", {m['skipped']} skipped" if m.get("skipped") else ""))
for folder in GATED:
    _, code, m, ok, failed = ra[folder]
    red_a |= set(failed)
    new = [t for t in failed if t not in red_w]
    mark(ok and m.get("passed", 0) > 0 and not new,
         f"merged landed {folder}: exit {code}; {m.get('passed', 0)} passed, {m.get('failed', 0) + m.get('error', 0)} failed"
         + (f", {m['skipped']} skipped" if m.get("skipped") else "") + (f"; new red: {new}" if new else ""))
for t in sorted(red_w - red_a):
    say(f"     merged: made green by the ACT: {t}")
for t in sorted(red_a):
    say(f"     merged: red after the ACT: {t}")
say(f"merged: red in the window: {len(red_w)}; made green by the ACT: {len(red_w - red_a)}; red after: {len(red_a)}; "
    f"new red brought by the ACT: {sorted(red_a - red_w)}")
(EVID / "red-merged-window.txt").write_text("\n".join(sorted(red_w)) + "\n")
(EVID / "red-merged-landed.txt").write_text("\n".join(sorted(red_a)) + "\n")

# 3b. the three named acceptance cases, each case's status, window and landed
say("--- order 1, the named acceptance cases (W2-101's claude-copy and generated-drift cases, W2-11's four-places case)")
tw, ta = targeted(win, "merged-window"), targeted(reh, "merged-landed")
ours_ids = sorted(i for i in ta if any(f"[{sk}]" in i for sk in SKILLS))
for i in ours_ids:
    say(f"     {i}: window {tw.get(i, 'absent')}, landed {ta[i]}")
others_ids = sorted(i for i in ta if i not in ours_ids)
mark(len(ours_ids) == 9 and all(ta[i] == "PASSED" for i in ours_ids),
     f"the nine named cases for the three skills PASSED after the ACT ({sum(ta[i] == 'PASSED' for i in ours_ids)} of "
     f"{len(ours_ids)}); in the window {sum(tw.get(i) == 'FAILED' for i in ours_ids)} FAILED")
mark(all(ta[i] == "PASSED" for i in others_ids),
     f"the four-places case for the other {len(others_ids)} kernel skills PASSED after the ACT")

# 4. the by-hand steps literally: stage, commit, undo, commit (on the merged tree)
say("--- order 1, the by-hand steps literally on the merged tree")
paths = " ".join(TOUCHED)
step(reh, "git add the touched paths", f"git add {paths}")
step(reh, "staged count equals the touched list", f"test \"$(git diff --cached --name-only | wc -l)\" = {len(TOUCHED)}")
step(reh, "commit", f"{GIT} commit -q -m '{ACT}: rehearsal' --trailer 'Task: DAEO-6icv' --trailer 'Role: owner'")
pcode, pfound = portability(reh)
mark(not ours(pfound) and others(pfound) == BASE_OTHERS, f"portability after the commit: exit {pcode}; findings {pfound}")
step(reh, "apply.sh undo", f"bash {BUNDLE}/apply.sh undo")
step(reh, "git add the touched paths (undo)", f"git add -A {paths}")
step(reh, "commit the undo", f"{GIT} commit -q -m '{ACT} undone' --trailer 'Task: DAEO-6icv' --trailer 'Role: owner'")
step(reh, "the undo commit returns the tree to the start (empty diff over the touched paths)",
     f"git diff --quiet HEAD~2 HEAD -- {paths}")

# 5. order 2: integrate + w2/W2-100 merged, COPIES-10 applied and committed, then w2/W2-101 merged, then this ACT
say("--- order 2: integrate + w2/W2-100 merged, ACT-CLAUDE-COPIES-10 applied (its apply.sh) and committed, then "
    "w2/W2-101 merged, then this ACT; HOME planted")
o2 = SCRATCH / "order2"
clone(INTEG, o2)
for ref in ("refs/heads/w2/W2-100", "refs/heads/w2/W2-101"):
    assert run(["git", "fetch", "-q", str(LIVE_TREE), f"{ref}:{ref}"], o2)[0] == 0
w2100_head = run(["git", "rev-parse", "--short=12", "refs/heads/w2/W2-100"], o2)[1]
assert w2100_head == W2100, f"w2/W2-100 is at {w2100_head}, not {W2100}"
assert run(["git", "rev-parse", "--short=12", "refs/heads/w2/W2-101"], o2)[1] == W2101
mb1, names1, conf1 = merge(o2, "refs/heads/w2/W2-100", "w2/W2-100")
mark(not conf1, f"order 2: w2/W2-100 {W2100} merged --no-ff: clean (no conflict, merge base {mb1[:12]}, "
     f"{len(names1)} files brought)")
c10 = json.loads((C10 / "manifest.json").read_bytes())
c10_paths = [ln.split("|")[1] for ln in (C10 / "list.txt").read_text().splitlines() if ln]
step(o2, "COPIES-10 apply.sh check", f"bash {C10}/apply.sh check")
step(o2, "COPIES-10 apply.sh apply", f"bash {C10}/apply.sh apply")
for i, c in enumerate(c10["checks"], 1):
    step(o2, f"COPIES-10 check {i}", c["cmd"], expect=c["exit"])
step(o2, "COPIES-10 committed (as the operator does)",
     f"git add {' '.join(c10_paths)} && {GIT} commit -q -m 'ACT-CLAUDE-COPIES-10: rehearsal' --trailer 'Task: DAEO-uw5h' "
     "--trailer 'Role: owner'")
step(o2, "this ACT's check 2 is red after COPIES-10 without W2-101 (the order is held)", checks[1]["cmd"], expect=1)
step(o2, "this ACT's apply.sh check passes there (targets absent)", f"bash {BUNDLE}/apply.sh check")
mb2, names2, conf2 = merge(o2, "refs/heads/w2/W2-101", "w2/W2-101")
mark(not conf2 and not any(p.startswith(".claude/") for p in names2),
     f"order 2: w2/W2-101 {W2101} merged --no-ff after them: clean (no conflict, merge base {mb2[:12]}, {len(names2)} "
     "files brought, none under .claude/)")
win2 = SCRATCH / "order2-window"
clone(o2, win2)
step(o2, "apply.sh check (targets absent)", f"bash {BUNDLE}/apply.sh check")
step(o2, "check 1 before the apply (red)", checks[0]["cmd"], expect=1)
step(o2, "check 2 before the apply (green with W2-100 merged as without)", checks[1]["cmd"])
step(o2, "apply.sh apply", f"bash {BUNDLE}/apply.sh apply")
for i, c in enumerate(checks, 1):
    step(o2, f"check {i} after the apply", c["cmd"])
for i, c in enumerate(c10["checks"], 1):
    step(o2, f"COPIES-10 check {i} still green after this ACT", c["cmd"], expect=c["exit"])
mark(changed_set(o2) == TOUCHED, f"order 2: the changed set equals the touched list ({len(TOUCHED)} files)")
with fresh_generation(o2) as fresh:
    differ2 = differing(fresh, o2)
    seven = {sk: sorted(str(p.relative_to(Path(fresh) / ".claude/skills" / sk))
                        for p in (Path(fresh) / ".claude/skills" / sk).rglob("*") if p.is_file())
             for sk in (*W2100_SKILLS, *SKILLS)}
mark(differ2 == differ_int and all(len(v) == 5 for v in seven.values()),
     f"order 2: rulesync from the landed tree's root .rulesync renders all seven skills' folders ({sum(map(len, seven.values()))} "
     f"files) equal to the tree; it differs only in {differ2} (as on plain integrate); so the bundle's bytes are the same "
     "in both orders")
p2code, p2found = portability(o2, src=o2 / "src")
mark(p2code == 0 and not p2found, f"order 2: portability after this ACT: exit {p2code}; {len(p2found)} findings "
     f"({tally(p2found)}), all seven skills")
say("--- order 2, the gated runs (landed) and the named cases for all seven skills (window and landed)")
for folder, code, m, ok, failed in gated_all(o2, "order2-landed", GATED_O2):
    mark(ok and code == 0 and not failed and m.get("passed", 0) > 0,
         f"order 2 landed {folder}: exit {code}; {m.get('passed', 0)} passed, {m.get('failed', 0) + m.get('error', 0)} "
         f"failed" + (f", {m['skipped']} skipped" if m.get("skipped") else "") + (f"; red: {failed}" if failed else ""))
tw2, ta2 = targeted(win2, "order2-window", TARGETED_O2), targeted(o2, "order2-landed", TARGETED_O2)
ids101 = sorted(i for i in ta2 if any(f"[{sk}]" in i for sk in SKILLS))
ids100 = sorted(i for i in ta2 if any(f"[{sk}]" in i for sk in W2100_SKILLS))
rest2 = sorted(i for i in ta2 if i not in ids101 and i not in ids100)
mark(len(ids101) == 9 and all(ta2[i] == "PASSED" for i in ids101) and all(tw2.get(i) == "FAILED" for i in ids101),
     f"order 2: W2-101's nine named cases FAILED in the window ({sum(tw2.get(i) == 'FAILED' for i in ids101)}) and "
     f"PASSED after this ACT ({sum(ta2[i] == 'PASSED' for i in ids101)} of {len(ids101)})")
mark(len(ids100) == 12 and all(ta2[i] == "PASSED" and tw2.get(i) == "PASSED" for i in ids100),
     f"order 2: W2-100's twelve named cases PASSED in the window and after ({sum(ta2[i] == 'PASSED' for i in ids100)} of "
     f"{len(ids100)})")
mark(all(ta2[i] == "PASSED" for i in rest2),
     f"order 2: the four-places case for the other {len(rest2)} kernel skills PASSED after this ACT")

untouched = live_state() == live_before and not any(planted.iterdir())
mark(untouched, "the live files unchanged by the rehearsal, and nothing written to the planted HOME")
say(f"failures: {fails}")
put("rehearsal.log", ("\n".join(log) + "\n").encode())
mf = {"act": ACT, "dec": "DEC-315, DEC-1112 (3), CAP-33", "author": "cto", "claimed_class": "b",
      "touched": touched, "files": files, "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]},
      "checks": checks, "commands": []}
raw = json.dumps(mf, indent=1).encode()
(BUNDLE / "manifest.json").write_bytes(raw)
print(json.dumps({"manifest_sha256": sha(raw), "touched": len(touched), "failures": fails}))
