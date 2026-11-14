"""Builds and rehearses ACT-CLAUDE-COPIES-10 (the generated .claude/skills/{backend,api,data,security}/ copies of W2-100's
four new kernel skills; under the owner's CIT-P approval of W2-100, pending: "yes W2-100-CIT-P 7bb4f1ac"; DEC-315,
DEC-1112 (3), CAP-33). Adapted from drafts/claude-copies-9/build_claude_copies_act_9.py (not edited), with the new-file
handling of drafts/claude-copies-7/build_claude_copies_act_7.py (not edited). Changes from COPIES-9's builder:

  * the targets are new (absent on integrate and on the merged tree): before is null in list.txt and the manifest, no
    before/ file is written (as COPIES-7), and undo removes the files;
  * BASE is a clone of integrate with refs/heads/w2/W2-100 (head cdac25763613, asserted) merged by one --no-ff commit,
    exactly what the operator sees after the CTO's hand merge (Task: DAEO-uw5h). The builder asserts that the commits
    after the verified product head f7637bd03e25 touch only docs/probes/ and docs/changes/, and that the CIT-P file at
    the branch head is 7bb4f1ac...;
  * W2-100 itself carries the root .rulesync/skills/<skill>/ and template/.rulesync/skills/<skill>/ copies: there is no
    root .rulesync copy step (COPIES-9's step 1 is dropped) and no template patch. The sources (check 2) are the sixty
    files: the five files of each of the four skills in the kernel, the root .rulesync and template/.rulesync, each at
    the sha256 of W2-100's CIT-P section 3 (red on plain integrate: absent there, so the operator's G8 refuses a run
    before the hand merge);
  * rulesync 24.0.0 runs from the merged tree's root .rulesync/ (portability's own GENERATE form). The touched set is
    rulesync's output under the four skills' .claude/skills/ folders, required to be every file of each kernel folder
    (what rulesync renders for a skill folder is logged); each non-SKILL.md file is required byte-equal to its kernel
    source. No lead's expected file exists for these copies, so COPIES-9's expected-bytes stop is replaced by that
    assertion and by the acceptance cases themselves;
  * the adopt skill is gone from the ACT (COPIES-9 regenerated it; integrate now holds it): the only other rulesync
    output that may differ is .claude/settings.json (DEC-616), never written;
  * the gated runs: W2-100 replaces W2-37 at the head of the list (W2-37 kept, tests/unit/impact dropped); plus a
    targeted run of the three named acceptance cases (W2-100's claude-copy and generated-drift cases, W2-11's
    four-places case) on the window and the landed tree, with each case's status;
  * gated outputs and the operator-gate evidence go to drafts/claude-copies-10/evidence/; pytest's TMPDIR is
    /tmp/gov-os-cto-f388 (the CTO's rule).

    python3 -I build_claude_copies_act_10.py <INTEGRATE clone> <bundle dir> <scratch dir> [ACT id]
"""
import hashlib, json, os, re, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

INTEG, BUNDLE, SCRATCH = (Path(a).resolve() for a in sys.argv[1:4])
ACT = sys.argv[4] if len(sys.argv) > 4 else "ACT-CLAUDE-COPIES-10"
LIVE_TREE = Path("/home/usain/Dynamic-Agentic-Engineering-OS")      # read-only: the branch to merge, and proof the rehearsal left it alone
ORCH = LIVE_TREE / ".gov-runtime/scratch/orchestrator"
HEAVY = str(ORCH / "tools/heavy_slot.sh")
EVID = ORCH / "drafts/claude-copies-10/evidence"
C7 = ORCH / "acts/ACT-CLAUDE-COPIES-7"
C9 = ORCH / "acts/ACT-CLAUDE-COPIES-9"
W2100 = "cdac25763613"
PRODUCT_HEAD = "f7637bd03e25"
CITP = "docs/changes/W2-100-CIT-P.md"
CITP_SHA = "7bb4f1ac4b0b14bc15440f189447be02c8dd80710289c1f0153dbcaa0e08e515"
SKILLS = ("backend", "api", "data", "security")
CHECK_PY = "538a11b5959753b5a9f145d8752d9e776a40245f57cfc9e0371ad248e4459382"
SRC_SHA = {   # W2-100's CIT-P section 3, "after" at f7637bd03e25 (kernel = root .rulesync = template/.rulesync)
    "backend": {"SKILL.md": "8c4e9e9d9a7e5e1f8a4bc0ba8bfe07e98d3187ea8c1026219fbdff8bcdc0b0da",
                "check_domain_skill.py": CHECK_PY,
                "scenario-records.yaml": "cf20652e825386ca82b763e811bcd93f94cba6e5ab77a4d5d0de1ac20b8f5476",
                "scenario-summaries.md": "509f68994fa29bc06f1065ff4b6ee3d62c219374efcafe1bdc82da7afe51014d",
                "scenarios.md": "84b71aed50416474ecda06b9d927893b071f7ee190859b982dfe088b7d82409a"},
    "api": {"SKILL.md": "f6956285fd93785fe91534b0c5f76d1ce8bb2cff4d49775f7590cca567e5e965",
            "check_domain_skill.py": CHECK_PY,
            "scenario-records.yaml": "a78358a1ffd994e9f8497c08b3cbc3b1fe5f1947095ceda0d5f3995e522bd880",
            "scenario-summaries.md": "7c0bc6fa0f15653b3381f3047b911f09fdfb3224d1c41e2982573f1b6007505f",
            "scenarios.md": "65b6460ce7b4fb628f9646e03369a40b466b1a12bf475b1a91e4de397c5fbae3"},
    "data": {"SKILL.md": "f388e1a605e2afd57bcc3277b240b3429b804f35bd69e977c8b09fc11843d03e",
             "check_domain_skill.py": CHECK_PY,
             "scenario-records.yaml": "11436b7a7ec6ab9000c6ff1f15a9f1082e72cd2ae39c80e3016c202cb6e89589",
             "scenario-summaries.md": "cf701bd3ed5523426f1d1e9e2a82f18b309fcddf925c69b34d9fe346d110b135",
             "scenarios.md": "514c5e473f2ef48346c9a69b5c30de3122ce997a65095bc0754ca302ef711418"},
    "security": {"SKILL.md": "610371cfbc3410104fe3bfdd52cf8757402b22aaab550e15c5bb49618dcb93a1",
                 "check_domain_skill.py": CHECK_PY,
                 "scenario-records.yaml": "dfcebf97d06b2d1709e7250d72fa2dbfe029e212aefb2a9270a867a4625359df",
                 "scenario-summaries.md": "4791045bd5b06fac8b4b6eb7d4f9f81f012030e4caed11b8d75ce2a86552e7c6",
                 "scenarios.md": "477d93046c27d03668d98e848fd248c45d0cdcc59d57050cabd9737e179cb3ea"},
}
SOURCE_ROOTS = ("template/governance/kernel/skills", ".rulesync/skills", "template/.rulesync/skills")
PINS = {f"{root}/{sk}/{name}": h for root in SOURCE_ROOTS for sk in SKILLS for name, h in SRC_SHA[sk].items()}
EXPECTED_TOUCHED = sorted(f".claude/skills/{sk}/{name}" for sk in SKILLS for name in SRC_SHA[sk])
OUR_PREFIXES = tuple(f"{root}/{sk}/" for sk in SKILLS for root in (*SOURCE_ROOTS, ".claude/skills"))
GENERATED_FOLDERS = (".claude/agents", ".claude/skills", ".claude/commands")
GENERATE = ["generate", "--targets", "claudecode,agentsmd", "--features",
            "rules,hooks,permissions,subagents,commands,skills", "--input-roots"]
RULESYNC = shutil.which("rulesync") or str(Path.home() / ".local/bin/rulesync")
GATED = ["tests/acceptance/W2-100", "tests/acceptance/W2-11", "tests/unit/adapters", "tests/acceptance/W1-33",
         "tests/acceptance/W1-38", "tests/acceptance/W2-153", "tests/acceptance/W2-98", "tests/acceptance/W2-88a",
         "tests/acceptance/W2-52", "tests/acceptance/W2-37"]
TARGETED = [("tests/acceptance/W2-100",
             ["tests/acceptance/W2-100/test_w2_100_copies.py::test_the_claude_copy_matches_the_kernel_source",
              "tests/acceptance/W2-100/test_w2_100_copies.py::test_the_adapter_check_finds_no_generated_drift_in_the_real_skill"]),
            ("tests/acceptance/W2-11",
             ["tests/acceptance/W2-11/test_w2_11_skills.py::test_the_skill_carries_one_version_in_all_four_places"])]
TMP = Path("/tmp/gov-os-cto-f388")
HOME_RX = re.compile(r"/home/[A-Za-z0-9_.-]+/")
APPLY_SH = (C9 / "apply.sh").read_text()   # the same apply.sh as ACT-CLAUDE-COPIES-1 to -9
assert APPLY_SH == (C7 / "apply.sh").read_text()


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
SCRATCH.mkdir(parents=True, exist_ok=True)
TMP.mkdir(exist_ok=True)
EVID.mkdir(parents=True, exist_ok=True)
INTEG_HEAD = run(["git", "rev-parse", "HEAD"], INTEG)[1]
assert run(["git", "status", "--porcelain", "--untracked-files=all"], INTEG)[1] == ""
LIVE_INTEG = run(["git", "rev-parse", "refs/heads/w2/integrate"], LIVE_TREE)[1]
assert INTEG_HEAD == LIVE_INTEG, f"the integrate clone is at {INTEG_HEAD[:12]}, live w2/integrate at {LIVE_INTEG[:12]}"

# BASE: integrate with w2/W2-100 merged by one commit, as after the CTO's hand merge
BASE = SCRATCH / "base-merged"
clone(INTEG, BASE)
assert run(["git", "fetch", "-q", str(LIVE_TREE), "refs/heads/w2/W2-100:refs/heads/w2/W2-100"], BASE)[0] == 0
w2100_head = run(["git", "rev-parse", "--short=12", "refs/heads/w2/W2-100"], BASE)[1]
assert w2100_head == W2100, f"w2/W2-100 is at {w2100_head}, not the approved {W2100}"
late = run(["git", "diff", "--name-only", PRODUCT_HEAD, "refs/heads/w2/W2-100"], BASE)[1].splitlines()
assert late and all(p.startswith(("docs/probes/", "docs/changes/")) for p in late), late
citp = subprocess.run(["git", "show", f"refs/heads/w2/W2-100:{CITP}"], cwd=BASE, capture_output=True).stdout
assert sha(citp) == CITP_SHA, f"the CIT-P at the branch head is {sha(citp)}"
mbase = run(["git", "merge-base", "HEAD", "refs/heads/w2/W2-100"], BASE)[1]
code, out = run(["git", "-c", "user.name=rehearsal", "-c", "user.email=rehearsal@example.invalid", "merge", "--no-ff", "-q",
                 "-m", "Merge w2/W2-100 (rehearsal of the CTO's hand merge)", "refs/heads/w2/W2-100"], BASE)
assert code == 0, out
assert run(["git", "status", "--porcelain", "--untracked-files=all"], BASE)[1] == ""
merged_names = run(["git", "diff", "--name-only", "HEAD^1", "HEAD"], BASE)[1].splitlines()
gen = SCRATCH / "gen-clone"
clone(BASE, gen)
say(f"{ACT} rehearsal; base: integrate {INTEG_HEAD[:12]} with w2/W2-100 {W2100} merged (one --no-ff commit, clean: no "
    f"conflict, merge base {mbase[:12]}, {len(merged_names)} files brought); rulesync {run([RULESYNC, '--version'], SCRATCH)[1]}")
say(f"the commits after the verified product head {PRODUCT_HEAD} touch only {late}; the CIT-P at the branch head is "
    f"{CITP_SHA[:8]}")
assert not any(p.startswith(".claude/") for p in merged_names), "the merge brings a .claude file"

# the sources at W2-100's approved bytes, on the merged tree and in the branch's own objects
for rel, h in PINS.items():
    assert sha((gen / rel).read_bytes()) == h, f"{rel} is not at {h}"
    shown = subprocess.run(["git", "show", f"refs/heads/w2/W2-100:{rel}"], cwd=BASE, capture_output=True).stdout
    assert sha(shown) == h, f"the branch's {rel} is not the approved bytes"
for sk in SKILLS:
    for root in SOURCE_ROOTS:
        on_disk = sorted(p.name for p in (gen / root / sk).rglob("*") if p.is_file())
        assert on_disk == sorted(SRC_SHA[sk]), f"{root}/{sk} holds {on_disk}"
    for root in (*SOURCE_ROOTS, ".claude/skills"):
        assert not (INTEG / root / sk).exists(), f"{root}/{sk} is on integrate"
say(f"the {len(PINS)} sources (the five files of each of {list(SKILLS)} in {list(SOURCE_ROOTS)}) are at W2-100's CIT-P "
    f"section 3 hashes, on the merged tree and in w2/W2-100 {W2100}; none is on plain integrate")


def portability(tree, rulesync=True):
    env = dict(os.environ, PYTHONPATH=str(gen / "src"), RULESYNC_BIN=RULESYNC if rulesync else "/nonexistent/rulesync")
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
    f"of them the four skills': {len(BASE_OURS)} ({tally(ours(base_found))})")
BASE_OTHERS = others(base_found)
assert BASE_OTHERS == OTHERS_INTEG, "W2-100's merge changes a finding that is not the four skills'"
assert BASE_OURS == sorted(("GENERATED_DIFFERS", p) for p in EXPECTED_TOUCHED), BASE_OURS
say(f"  the four skills' findings are GENERATED_DIFFERS for exactly the {len(EXPECTED_TOUCHED)} absent .claude copies; "
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
say(f"portability in the generation clone after the {len(TOUCHED)} copies: exit {code}; the four skills' findings "
    f"{ours(after)}; the others unchanged: {others(after) == BASE_OTHERS}")
assert not ours(after) and others(after) == BASE_OTHERS, after
tcode, tfound = portability(gen / "template", rulesync=False)
say(f"portability on template/ (as an adopted project, no rulesync): {len(ours(tfound))} findings for the four skills; "
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
say(f"check 1: the {len(copies)} copies; check 2: the {len(sources)} sources (W2-100's CIT-P section 3, kernel, root "
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


def gated_all(tree, label):
    with ThreadPoolExecutor(max_workers=3) as pool:
        return list(pool.map(lambda f: gated(tree, f, label), GATED))


def targeted(tree, label):
    """The three named cases, one run per folder, with each case's own status (-rA)."""
    status = {}
    for folder, ids in TARGETED:
        code, out = run(pytest_cmd(tree, [*ids, "-q", "-rA"]), tree, pytest_env(tree))
        (EVID / f"{label}-targeted-{folder.replace('/', '_')}.txt").write_text(out + "\n")
        for ln in out.splitlines():
            mm = STATUS_LINE.match(ln.strip())
            if mm:
                status[mm.group(2)] = mm.group(1)
    return status


# 1. apply, verify, undo, re-apply on the merged tree
say("--- rehearsal on integrate with W2-100 merged (the tree after the hand merge's merge commit); HOME planted")
reh = SCRATCH / "rehearsal-merged"
clone(BASE, reh)
win = SCRATCH / "window-merged"
clone(BASE, win)
before_state = tree_state(reh)
step(reh, "apply.sh check (every target at its stated before state: absent)", f"bash {BUNDLE}/apply.sh check")
step(reh, "check 1 before the apply (red, as intended: the copies are absent)", checks[0]["cmd"], expect=1)
step(reh, "check 2 before the apply (green: W2-100's sixty sources at the approved bytes)", checks[1]["cmd"])
step(reh, "apply.sh apply", f"bash {BUNDLE}/apply.sh apply")
for i, c in enumerate(checks, 1):
    step(reh, f"check {i} (sha256sum -c, {len(c['cmd'].splitlines()) - 2} files)", c["cmd"])
mark(changed_set(reh) == TOUCHED, f"the changed set equals the touched list ({len(TOUCHED)} files)")
after_state = tree_state(reh)
mark(all(sha(after_state[t["path"]]) == t["after"] for t in touched), "every target is at its stated after sha256")
pcode, pfound = portability(reh)
mark(not ours(pfound) and others(pfound) == BASE_OTHERS,
     f"portability after the apply: exit {pcode}; the four skills' findings {ours(pfound)}; the {len(BASE_OTHERS)} "
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
say("--- plain integrate (W2-100 not merged)")
ri = SCRATCH / "rehearsal-integrate"
clone(INTEG, ri)
step(ri, "apply.sh check passes on plain integrate (the twenty copies are absent there as on the merged tree)",
     f"bash {BUNDLE}/apply.sh check")
step(ri, "check 2 is red on plain integrate (W2-100's sources are absent: the order is held)", checks[1]["cmd"], expect=1)
mark(changed_set(ri) == [], "check changed nothing")
# a moved target is refused: a file planted where a copy is to go
mv = SCRATCH / "rehearsal-moved"
clone(BASE, mv)
(mv / EXPECTED_TOUCHED[0]).parent.mkdir(parents=True, exist_ok=True)
(mv / EXPECTED_TOUCHED[0]).write_bytes(b"x\n")
step(mv, f"apply.sh check refuses a moved target (a file planted at {EXPECTED_TOUCHED[0]}; exit 3)",
     f"bash {BUNDLE}/apply.sh check", expect=3)

# 3. the gated runs: window and landed on the merged tree
say("--- the gated runs, one folder per run through the heavy-job gate: on the merged tree (W2-100's merge alone, then "
    "with this ACT)")
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
say("--- the three named acceptance cases (W2-100's claude-copy and generated-drift cases, W2-11's four-places case)")
tw, ta = targeted(win, "merged-window"), targeted(reh, "merged-landed")
ours_ids = sorted(i for i in ta if any(f"[{sk}]" in i for sk in SKILLS))
for i in ours_ids:
    say(f"     {i}: window {tw.get(i, 'absent')}, landed {ta[i]}")
others_ids = sorted(i for i in ta if i not in ours_ids)
mark(len(ours_ids) == 12 and all(ta[i] == "PASSED" for i in ours_ids),
     f"the twelve named cases for the four skills PASSED after the ACT ({sum(ta[i] == 'PASSED' for i in ours_ids)} of "
     f"{len(ours_ids)}); in the window {sum(tw.get(i) == 'FAILED' for i in ours_ids)} FAILED")
mark(all(ta[i] == "PASSED" for i in others_ids),
     f"the four-places case for the other {len(others_ids)} kernel skills PASSED after the ACT")

# 4. the by-hand steps literally: stage, commit, undo, commit (on the merged tree)
say("--- the by-hand steps literally on the merged tree")
paths = " ".join(TOUCHED)
step(reh, "git add the touched paths", f"git add {paths}")
step(reh, "staged count equals the touched list", f"test \"$(git diff --cached --name-only | wc -l)\" = {len(TOUCHED)}")
step(reh, "commit", f"{GIT} commit -q -m '{ACT}: rehearsal' --trailer 'Task: DAEO-uw5h' --trailer 'Role: owner'")
pcode, pfound = portability(reh)
mark(not ours(pfound) and others(pfound) == BASE_OTHERS, f"portability after the commit: exit {pcode}; findings {pfound}")
step(reh, "apply.sh undo", f"bash {BUNDLE}/apply.sh undo")
step(reh, "git add the touched paths (undo)", f"git add -A {paths}")
step(reh, "commit the undo", f"{GIT} commit -q -m '{ACT} undone' --trailer 'Task: DAEO-uw5h' --trailer 'Role: owner'")
step(reh, "the undo commit returns the tree to the start (empty diff over the touched paths)",
     f"git diff --quiet HEAD~2 HEAD -- {paths}")

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
