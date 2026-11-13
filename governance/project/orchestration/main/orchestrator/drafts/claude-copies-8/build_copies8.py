"""Builds and rehearses ACT-CLAUDE-COPIES-8 (the "until W2-56" line deleted from four generated copies; W2-56 closed,
the owner's approval 2026-11-13; DEC-1052, DEC-1163, DEC-315, CAP-33) in two forms:

  * ACT-CLAUDE-COPIES-8 (default): the four copies only, for the tree where the CTO's source commit b88a76172 stands;
  * ACT-CLAUDE-COPIES-8-with-sources: the four copies and the three sources (the two kernel templates and the
    template's orchestrator source), for the tree where b88a76172 is reverted.

Adapted from drafts/claude-copies-6/build_v2.py (not edited). Changes:
  * the copies are generated twice, never by hand: (A) from a clone of W2-33's merge commit with w2/W2-33 merged
    (a no-op), the COPIES-6 template patch applied by its own apply.sh, the line deleted literally from the three
    sources, COPIES-6 applied; (B) from a clone of integrate at b88a76172 with COPIES-6 applied. In each: every root
    role source by the clone's own compose(root, role), .claude/agents by the clone's rulesync 24.0.0 from the root
    .rulesync (portability's GENERATE form), .claude/templates by the clone's own
    ``python3 -m gov.adapters.portability --write-templates .claude/templates`` (byte copies of the kernel templates);
    both must give exactly the four expected after hashes, or the build stops (never forced);
  * the checks are the same for both forms: check 1 the four copies; check 2 the order: the nine kernel role files,
    the two kernel templates after the deletion, the nine template role sources (COPIES-6's patch, the orchestrator
    after the deletion) and COPIES-6's sixteen other copies, so a run before COPIES-6, before the template patch or
    before the sources' deletion is red at the operator's G8;
  * the rehearsal names no live HOME path in a check (asserted by pattern).

    python3 -I build_copies8.py <scratch dir>
"""
import hashlib, json, os, re, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SCRATCH = Path(sys.argv[1]).resolve()
LIVE_TREE = Path("/home/usain/Dynamic-Agentic-Engineering-OS")      # read-only: cloned, and re-hashed at the end
ORCH = LIVE_TREE / ".gov-runtime/scratch/orchestrator"
ACTS = ORCH / "acts"
C6 = ACTS / "ACT-CLAUDE-COPIES-6"
C6PATCH = ORCH / "drafts/claude-copies-6/template-patch"
HEAVY = str(ORCH / "tools/heavy_slot.sh")
PRE_C, PATCH_C, SRC_C = "f6163461e", "d172bc71f", "b88a76172"
LINE = "- Run `gov accept` for a ticket whose suites need the code index outside the sandbox, until W2-56 [DEC-1052].\n"
KERNEL_ROLES = "template/governance/kernel/roles"
COPIES = {  # path: (before, after)
    ".claude/templates/role-lead.md": ("4e8e46b097797d13f70c8828f41562b768bfb19f06160dac87ee7e308aa590a9",
                                       "c731503e7f643dc0b4377358dd09876d7dedaf688ec79ffb6e021776bf86e799"),
    ".claude/templates/role-cto.md": ("013d4d85bc5d55b2d858f6f07f10f949bccdc85e20458c2c45e4c3d6cfd67abd",
                                      "dbcc9d8ccc925acd4f783cb1d359943eb564297cd7685433d98892956979d789"),
    ".rulesync/subagents/orchestrator.md": ("ef15ea7d3ea78b674f4e4480e521c43db4ad43eb8bcbc7a8be66f83f582d266c",
                                            "5db8f0cbac35e30ebb81757bb8b92001c611a8080ba8dba9402bd6a4b6a222ba"),
    ".claude/agents/orchestrator.md": ("d46907b92776244721dceca7d8f8b33ec7352bde113068c54a638d3da3d7200c",
                                       "20fd6d04a3cbf08c788790a6202965ec9163c1de56290a376976d33c797e802f"),
}
SOURCES = {
    "template/governance/kernel/templates/role-lead.md": ("4e8e46b097797d13f70c8828f41562b768bfb19f06160dac87ee7e308aa590a9",
                                                          "c731503e7f643dc0b4377358dd09876d7dedaf688ec79ffb6e021776bf86e799"),
    "template/governance/kernel/templates/role-cto.md": ("013d4d85bc5d55b2d858f6f07f10f949bccdc85e20458c2c45e4c3d6cfd67abd",
                                                         "dbcc9d8ccc925acd4f783cb1d359943eb564297cd7685433d98892956979d789"),
    "template/.rulesync/subagents/orchestrator.md": ("ef15ea7d3ea78b674f4e4480e521c43db4ad43eb8bcbc7a8be66f83f582d266c",
                                                     "5db8f0cbac35e30ebb81757bb8b92001c611a8080ba8dba9402bd6a4b6a222ba"),
}
VARIANTS = {
    "ACT-CLAUDE-COPIES-8": {"touched": dict(COPIES)},
    "ACT-CLAUDE-COPIES-8-with-sources": {"touched": {**COPIES, **SOURCES}},
}
DEC = "DEC-1052, DEC-1163, DEC-315, CAP-33"
GENERATED_FOLDERS = (".claude/agents", ".claude/skills", ".claude/commands")
GENERATE = ["generate", "--targets", "claudecode,agentsmd", "--features",
            "rules,hooks,permissions,subagents,commands,skills", "--input-roots"]
RULESYNC = shutil.which("rulesync") or str(Path.home() / ".local/bin/rulesync")
GATED = ["tests/acceptance/W2-153", "tests/unit/adapters", "tests/unit/launch", "tests/unit/brief",
         "tests/acceptance/W2-152", "tests/acceptance/W1-38", "tests/acceptance/W2-128", "tests/acceptance/W1-35"]
if os.environ.get("COPIES8_NO_GATED"):
    GATED = []
APPLY_SH = (C6 / "apply.sh").read_text()        # the same apply.sh as ACT-CLAUDE-COPIES-1 to -6
GIT = "git -c user.name=rehearsal -c user.email=rehearsal@example.invalid"
HOME_RX = re.compile(r"/home/[A-Za-z0-9_.-]+/")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def run(cmd, cwd, env=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    return r.returncode, (r.stdout + r.stderr).strip()


def must(cmd, cwd, env=None):
    code, out = run(cmd, cwd, env)
    assert code == 0, f"{cmd} in {cwd}: {out[-400:]}"
    return out


SCRATCH.mkdir(parents=True, exist_ok=True)
TMP = SCRATCH / "tmp"
TMP.mkdir(exist_ok=True)
MIRROR = SCRATCH / "mirror"
if not MIRROR.exists():
    must(["git", "clone", "-q", "--no-hardlinks", "--no-checkout", str(LIVE_TREE), str(MIRROR)], SCRATCH)
LIVE_HEAD = must(["git", "rev-parse", "HEAD"], LIVE_TREE)          # read-only
must(["git", "fetch", "-q", "origin"], MIRROR)
REV = {c: must(["git", "rev-parse", c], MIRROR) for c in (PRE_C, PATCH_C, SRC_C, LIVE_HEAD)}
W233 = must(["git", "rev-parse", "origin/w2/W2-33"], MIRROR)


def clone(name, at):
    dest = SCRATCH / name
    if dest.exists():
        shutil.rmtree(dest)
    must(["git", "clone", "-q", "--shared", "--no-checkout", str(MIRROR), str(dest)], SCRATCH)
    must(["git", "checkout", "-q", "-b", "work", REV[at]], dest)
    return dest


def commit(tree, msg, paths=None):
    must(["bash", "-c", f"git add -A {' '.join(paths) if paths else '.'} && {GIT} commit -q -m '{msg}'"], tree)


log = []
def say(line):
    log.append(line)
    print(line, flush=True)


def tally(found):
    n = {}
    for f in found:
        n[f["code"]] = n.get(f["code"], 0) + 1
    return ", ".join(f"{k} {v}" for k, v in sorted(n.items())) or "none"


def portability(tree):
    env = dict(os.environ, PYTHONPATH=str(tree / "src"), RULESYNC_BIN=RULESYNC)
    code, out = run([sys.executable, "-m", "gov.adapters.portability"], tree, env)
    return code, (json.loads(out)["findings"] if out.startswith("{") else [{"code": "UNREADABLE", "message": out[-300:]}])


def compose(tree, root, role):
    probe = ("import sys, json; sys.path.insert(0, sys.argv[1] + '/src'); from gov.adapters import portability as p; "
             "from pathlib import Path; print(json.dumps(p.compose(Path(sys.argv[2]), sys.argv[3])))")
    return json.loads(must([sys.executable, "-I", "-c", probe, str(tree), str(root), role], tree))


def apply_c6(tree):
    must(["bash", "-c", f"bash {C6}/apply.sh check && bash {C6}/apply.sh apply"], tree)
    commit(tree, "ACT-CLAUDE-COPIES-6 (rehearsal)", [l.split("|")[1] for l in (C6 / "list.txt").read_text().splitlines() if l])


def changed_set(tree):
    st = run(["git", "status", "--porcelain", "--untracked-files=all"], tree)[1].splitlines()
    return sorted(l.strip().split(None, 1)[1] for l in st)


def generate(tree, label):
    """compose() for every root role source, rulesync for .claude/agents, --write-templates for .claude/templates."""
    roles = sorted(p.stem for p in (tree / KERNEL_ROLES).glob("*.md"))
    for role in roles:
        assert compose(tree, tree / "template", role) == \
            (tree / "template/.rulesync/subagents" / f"{role}.md").read_text(encoding="utf-8"), f"{label}: template {role}"
        (tree / ".rulesync/subagents" / f"{role}.md").write_text(compose(tree, tree, role), encoding="utf-8")
    others = []
    with tempfile.TemporaryDirectory(dir=TMP) as fresh:
        code, out = run([RULESYNC, *GENERATE, str((tree / ".rulesync").resolve())], fresh)
        assert code == 0, out
        for path in sorted(Path(fresh).rglob("*")):
            rel = str(path.relative_to(fresh))
            if not path.is_file() or ((tree / rel).is_file() and (tree / rel).read_bytes() == path.read_bytes()):
                continue
            if rel.startswith(GENERATED_FOLDERS):
                (tree / rel).parent.mkdir(parents=True, exist_ok=True)
                (tree / rel).write_bytes(path.read_bytes())
            else:
                others.append(rel)
    out = must([sys.executable, "-m", "gov.adapters.portability", "--write-templates", ".claude/templates"], tree,
               dict(os.environ, PYTHONPATH=str(tree / "src")))
    written = len(json.loads(out)["written"])
    return roles, others, written


say(f"ACT-CLAUDE-COPIES-8 build and rehearsal; integrate commits: W2-33's merge {REV[PRE_C][:12]}, the COPIES-6 template "
    f"patch {REV[PATCH_C][:12]}, the sources' deletion {REV[SRC_C][:12]}; w2/W2-33 {W233[:12]}; rulesync "
    f"{run([RULESYNC, '--version'], SCRATCH)[1]}")

# ------------------------------------------------------------------------------------------------- the generation
say("--- generation A: W2-33's merge commit, w2/W2-33 merged, the COPIES-6 template patch by its apply.sh, the line "
    "deleted literally from the three sources, COPIES-6 applied")
ga = clone("gen-a", PRE_C)
mo = must(["bash", "-c", f"{GIT} merge --no-edit {W233}"], ga)
say(f"git merge w2/W2-33: {mo.splitlines()[-1] if mo else 'ok'}")
must(["bash", "-c", f"bash {C6PATCH}/apply.sh check && bash {C6PATCH}/apply.sh apply"], ga)
commit(ga, "the COPIES-6 template patch")
same_patch = run(["git", "diff", "--quiet", REV[PATCH_C], "HEAD", "--", "template/.rulesync"], ga)[0] == 0
say(f"the template patch's tree equals integrate's {REV[PATCH_C][:12]} over template/.rulesync: {same_patch}")
assert same_patch
for rel in SOURCES:
    text = (ga / rel).read_text(encoding="utf-8")
    assert text.count(LINE) == 1, f"{rel}: the line occurs {text.count(LINE)} times"
    assert sha(text.encode()) == SOURCES[rel][0], rel
    (ga / rel).write_text(text.replace(LINE, ""), encoding="utf-8")
    assert sha((ga / rel).read_bytes()) == SOURCES[rel][1], f"{rel}: {sha((ga / rel).read_bytes())}"
commit(ga, "the line deleted from the three sources")
same_src = run(["git", "diff", "--quiet", REV[SRC_C], "HEAD", "--", *SOURCES], ga)[0] == 0
say(f"the three sources after the literal deletion: at their stated after sha256 and equal to {REV[SRC_C][:12]}'s: {same_src}")
assert same_src
apply_c6(ga)
roles, others, written = generate(ga, "A")
say(f"composed {len(roles)} root role sources (the template's nine already equal compose()); rulesync's other output "
    f"not written: {others}; --write-templates wrote {written} copies")
ca = changed_set(ga)
got_a = {rel: sha((ga / rel).read_bytes()) for rel in ca}
say(f"generation A changed: {ca}")
for rel in ca:
    say(f"  {rel}: {got_a[rel]} " + ("= the stated after" if COPIES.get(rel, (0, 0))[1] == got_a[rel] else "DIFFERS"))

say("--- generation B: integrate at the sources' deletion commit, COPIES-6 applied")
gb = clone("gen-b", SRC_C)
mo = must(["bash", "-c", f"{GIT} merge --no-edit {W233}"], gb)
say(f"git merge w2/W2-33: {mo.splitlines()[-1] if mo else 'ok'}")
patch_in = all(sha((gb / l.split("|")[1]).read_bytes()) == l.split("|")[3]
               for l in (C6PATCH / "list.txt").read_text().splitlines() if l)
say(f"the COPIES-6 template patch's eight after hashes hold on {REV[SRC_C][:12]}: {patch_in}")
assert patch_in
apply_c6(gb)
generate(gb, "B")
cb = changed_set(gb)
got_b = {rel: sha((gb / rel).read_bytes()) for rel in cb}
say(f"generation B changed: {cb}; byte-equal to generation A: "
    f"{cb == ca and all((ga / r).read_bytes() == (gb / r).read_bytes() for r in cb)}")
match = ca == sorted(COPIES) and cb == sorted(COPIES) and all(got_a[r] == COPIES[r][1] == got_b[r] for r in COPIES)
say(f"generation reproduces the four stated after hashes byte for byte: {match}")
if not match:
    say("STOP: the generation does not give the stated hashes; nothing is built (never forced)")
    (SCRATCH / "build.log").write_text("\n".join(log) + "\n")
    sys.exit(1)
code, found = portability(gb)
say(f"portability in generation B after the copies: exit {code}; findings {found}")
assert code == 0 and not found, found

# the check texts, shared by both forms
c6_other = [l.split("|") for l in (C6 / "list.txt").read_text().splitlines() if l]
c6_other = [(p, a) for _, p, b, a in c6_other if p not in COPIES]
order = [(f"{KERNEL_ROLES}/{r}.md", sha((gb / KERNEL_ROLES / f"{r}.md").read_bytes())) for r in roles]
order += [(rel, SOURCES[rel][1]) for rel in SOURCES if rel.startswith("template/governance/")]
order += [(f"template/.rulesync/subagents/{r}.md", sha((gb / "template/.rulesync/subagents" / f"{r}.md").read_bytes()))
          for r in roles]
order += c6_other
assert len(c6_other) == 16 and dict(order)["template/.rulesync/subagents/orchestrator.md"] == SOURCES[
    "template/.rulesync/subagents/orchestrator.md"][1]


def sha_check(pairs):
    return "sha256sum -c - <<'EOF'\n" + "\n".join(f"{h}  {p}" for p, h in pairs) + "\nEOF"


CHECKS = [{"cmd": sha_check(sorted((p, a) for p, (b, a) in COPIES.items())), "exit": 0, "count": None},
          {"cmd": sha_check(sorted(order)), "exit": 0, "count": None}]
assert not any(HOME_RX.search(c["cmd"]) for c in CHECKS)
say(f"the checks (both forms): check 1 the four copies; check 2 the order, {len(order)} files (9 kernel role files, "
    f"2 kernel templates, 9 template role sources, COPIES-6's 16 other copies); no live HOME path in either")

# ------------------------------------------------------------------------------------------- the rehearsal trees
say("--- the rehearsal trees")
full_default = clone("full-default", SRC_C)               # integrate as it is, then COPIES-6
apply_c6(full_default)
full_ws = clone("full-with-sources", SRC_C)                # integrate with b88a76172 reverted, then COPIES-6
must(["bash", "-c", f"{GIT} revert --no-edit {REV[SRC_C]}"], full_ws)
rev_ok = run(["git", "diff", "--quiet", REV[PATCH_C], "HEAD"], full_ws)[0] == 0
say(f"the revert of {REV[SRC_C][:12]} gives {REV[PATCH_C][:12]}'s tree exactly: {rev_ok}")
assert rev_ok
c6c2 = json.loads((C6 / "manifest.json").read_text())["checks"][1]["cmd"]
plain = clone("c6-on-integrate", SRC_C)
c6code = run(["bash", "-c", c6c2], plain)[0]
say(f"FINDING: COPIES-6's own check 2 on integrate at {REV[SRC_C][:12]} (the sources' deletion committed): exit {c6code} "
    "(it pins template/.rulesync/subagents/orchestrator.md at ef15ea7d; G8 would refuse COPIES-6 there)")
apply_c6(full_ws)
say(f"COPIES-6's own check 2 on the reverted tree after COPIES-6: exit {run(['bash', '-c', c6c2], full_ws)[0]}")

# ------------------------------------------------------------------------------------------ the bundles, each form
built = {}
for act, spec in VARIANTS.items():
    bundle = ACTS / act
    if bundle.exists():
        shutil.rmtree(bundle)
    bundle.mkdir(parents=True)
    base = full_default if act == "ACT-CLAUDE-COPIES-8" else full_ws
    files, touched, lines = {}, [], []

    def put(rel, data, bundle=bundle, files=files):
        p = bundle / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        files[rel] = sha(data)

    for rel in sorted(spec["touched"]):
        b, a = spec["touched"][rel]
        cur, new = (base / rel).read_bytes(), (gb / rel).read_bytes()
        assert sha(cur) == b and sha(new) == a, (act, rel)
        if rel in COPIES and rel.startswith(".rulesync/") or rel == ".claude/agents/orchestrator.md":
            assert cur == (C6 / "after/repo" / rel).read_bytes(), rel     # COPIES-6's after, byte for byte
        put(f"before/repo/{rel}", cur)
        put(f"after/repo/{rel}", new)
        touched.append({"root": "repo", "path": rel, "before": b, "after": a})
        lines.append(f"repo|{rel}|{b}|{a}")
    put("list.txt", ("\n".join(lines) + "\n").encode())
    put("apply.sh", APPLY_SH.encode())
    os.chmod(bundle / "apply.sh", 0o755)
    built[act] = (bundle, base, files, touched)

planted = Path(tempfile.mkdtemp(prefix="planted-home-", dir=SCRATCH))
ALLREL = sorted({**COPIES, **SOURCES})
live_state = lambda: {rel: sha((LIVE_TREE / rel).read_bytes()) for rel in ALLREL}
live_before = live_state()

SUMMARY = re.compile(r"^(?:\d+ (?:passed|failed|errors?|skipped|xfailed|xpassed|deselected|warnings?)(?:, )?)+ in [\d.]+s(?: \(.*\))?$")
FAILED_LINE = re.compile(r"^(?:FAILED|ERROR) (\S+)")


# Red on the landed tree for a reason outside this ACT (named in the package): W2-128's row 8 pins the line this ACT
# deletes (the owner's decision, DEC-1163 (1)); its revision is the CTO's (a decided-behaviour test revision, DEC-1156 (7)).
EXPECTED_AFTER = {
    "tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_gov_accept_runs_outside_the_sandbox_until_w2_56[role-lead]":
        "row 8 pins the \"until W2-56\" line in the kernel template role-lead.md (:72-75); the owner deleted it "
        "(DEC-1163 (1)); red from the sources' deletion (b88a76172, or the with-sources form's own), not from the copies; "
        "the case's revision is the CTO's",
    "tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_gov_accept_runs_outside_the_sandbox_until_w2_56[role-cto]":
        "the same row 8 for role-cto.md",
    "tests/acceptance/W2-152/test_w2_152_facts.py::test_s10_gov_accept_w2_128_still_passes":
        "runs gov accept W2-128 (:61-75), so red while row 8 is",
}
REUSE = bool(os.environ.get("COPIES8_REUSE"))


def gated(tree, folder, label):
    f = SCRATCH / f"{label}-{folder.replace('/', '_')}.txt"
    if REUSE and f.is_file():          # the first build's run of the same commit's bytes: re-read, not re-run
        out = f.read_text()
        summary = [ln.strip() for ln in out.splitlines() if SUMMARY.match(ln.strip())]
        m = {k.rstrip("s") if k.startswith("error") else k: int(v)
             for v, k in re.findall(r"(\d+) (passed|failed|errors?|skipped)", summary[-1] if summary else "")}
        failed = sorted({mm.group(1) for ln in out.splitlines() if (mm := FAILED_LINE.match(ln.strip()))})
        code = (1 if (m.get("failed") or m.get("error")) else 0) if summary else 2
        return folder, code, m, bool(summary), failed
    env = dict(os.environ, PYTHONPATH=str(tree / "src"), TMPDIR=str(TMP), PYTHONUSERBASE="/home/usain/.local")
    code, out = run(["bash", HEAVY, "env", f"TMPDIR={TMP}", f"PYTHONPATH={tree / 'src'}", "PYTHONUSERBASE=/home/usain/.local",
                     "python3", "-m", "pytest", folder, "-q", "-rfE", "-p", "no:cacheprovider",
                     "-o", "tmp_path_retention_policy=failed"], tree, env)
    summary = [ln.strip() for ln in out.splitlines() if SUMMARY.match(ln.strip())]
    m = {k.rstrip("s") if k.startswith("error") else k: int(v)
         for v, k in re.findall(r"(\d+) (passed|failed|errors?|skipped)", summary[-1] if summary else "")}
    failed = sorted({mm.group(1) for ln in out.splitlines() if (mm := FAILED_LINE.match(ln.strip()))})
    (SCRATCH / f"{label}-{folder.replace('/', '_')}.txt").write_text(out + "\n")
    return folder, code, m, bool(summary), failed


# the window trees (each form's tree before its ACT) and one landed tree (both forms land the same bytes)
win_default = clone("window-default", SRC_C); apply_c6(win_default)
win_ws = clone("window-with-sources", SRC_C)
must(["bash", "-c", f"{GIT} revert --no-edit {REV[SRC_C]}"], win_ws); apply_c6(win_ws)
landed = clone("landed", SRC_C); apply_c6(landed)
must(["bash", "-c", f"bash {built['ACT-CLAUDE-COPIES-8'][0]}/apply.sh apply"], landed)
jobs = [(win_default, f, "window-default") for f in GATED] + [(win_ws, f, "window-with-sources") for f in GATED] + \
       [(landed, f, "landed") for f in GATED]
with ThreadPoolExecutor(max_workers=3) as pool:
    res = list(pool.map(lambda j: (j[2], gated(*j)), jobs))
R = {(lab, r[0]): r for lab, r in res}


def gated_lines(window_label):
    out, red_w, red_l, bad = [], set(), set(), 0
    for f in GATED:
        _, code, m, ok, failed = R[(window_label, f)]
        red_w |= set(failed)
        out.append(("", f"window {f}: exit {code}; {m.get('passed', 0)} passed, {m.get('failed', 0) + m.get('error', 0)} failed"
                    + (f", {m['skipped']} skipped" if m.get("skipped") else "")))
    for f in GATED:
        _, code, m, ok, failed = R[("landed", f)]
        red_l |= set(failed)
        unexpected = [t for t in failed if t not in EXPECTED_AFTER]
        good = ok and m.get("passed", 0) > 0 and not unexpected
        out.append(("ok" if good else "FAIL", f"landed {f}: exit {code}; {m.get('passed', 0)} passed, "
                    f"{m.get('failed', 0) + m.get('error', 0)} failed" + (f", {m['skipped']} skipped" if m.get("skipped") else "")
                    + (f"; unexpected: {unexpected}" if unexpected else "")))
    for t in sorted(red_w):
        out.append(("", f"     red in the window: {t}"))
    for t in sorted(red_l):
        out.append(("", f"     red on the landed tree: {t}" + (f" (expected: {EXPECTED_AFTER[t]})" if t in EXPECTED_AFTER else "")))
    out.append(("", f"red in the window: {len(red_w)}; made green by the ACT: {len(red_w - red_l)}; red after: "
                    f"{len(red_l)}; new red brought by the ACT: {sorted(red_l - red_w)}"))
    return out


def rehearse(act):
    bundle, base, files, touched = built[act]
    TOUCHED = sorted(t["path"] for t in touched)
    vlog, fails = [], 0

    def sayv(line):
        vlog.append(line)
        print(line, flush=True)

    def mark(ok, text):
        nonlocal fails
        fails += 0 if ok else 1
        sayv(f"{'ok  ' if ok else 'FAIL'} {text}")

    def step(tree, name, cmd, expect=0):
        code, out = run(["bash", "-c", cmd], tree, dict(os.environ, HOME=str(planted)))
        mark(code == expect, f"{name}: exit {code}{(' ' + out[-300:]) if out and code != expect else ''}")
        return code

    state = lambda tree: {rel: ((tree / rel).read_bytes() if (tree / rel).is_file() else None) for rel in TOUCHED}
    for line in log[:1]:
        sayv(line.replace("ACT-CLAUDE-COPIES-8 build", f"{act} build"))
    for line in log[1:]:
        if line.startswith(("---", "git merge", "the ", "composed", "generation", "  .", "portability in", "FINDING",
                            "COPIES-6's own")):
            sayv(line)
    sayv(f"--- {act}: {len(TOUCHED)} files; rehearsal on " +
         ("integrate at the sources' deletion commit, then COPIES-6 (the order: W2-33's merge, the template patch, "
          "the sources' commit, COPIES-6, this ACT)" if act == "ACT-CLAUDE-COPIES-8" else
          "integrate with the sources' deletion commit reverted (the template patch's tree), then COPIES-6 (the order: "
          "W2-33's merge, the template patch, the revert, COPIES-6, this ACT)") + "; HOME planted")
    reh = SCRATCH / f"rehearsal-{act}"
    if reh.exists():
        shutil.rmtree(reh)
    must(["git", "clone", "-q", "--shared", str(base), str(reh)], SCRATCH)
    pc, pf = portability(reh)
    sayv(f"     portability before the apply: exit {pc}; {len(pf)} findings: {tally(pf)}")
    before_state = state(reh)
    step(reh, "apply.sh check (every target at its stated before sha256)", f"bash {bundle}/apply.sh check")
    step(reh, "check 1 before the apply (red, as intended: the copies still carry the line)", CHECKS[0]["cmd"], 1)
    step(reh, "check 2 before the apply " + ("(green: the template patch, the sources' commit and COPIES-6 are in)"
         if act == "ACT-CLAUDE-COPIES-8" else "(red, as intended: the three sources are this ACT's)"),
         CHECKS[1]["cmd"], 0 if act == "ACT-CLAUDE-COPIES-8" else 1)
    step(reh, "apply.sh apply", f"bash {bundle}/apply.sh apply")
    for i, c in enumerate(CHECKS, 1):
        step(reh, f"check {i} (sha256sum -c, {len(c['cmd'].splitlines()) - 2} files)", c["cmd"])
    mark(changed_set(reh) == TOUCHED, f"the changed set equals the touched list ({len(TOUCHED)} files)")
    after_state = state(reh)
    mark(all(sha(after_state[t["path"]]) == t["after"] for t in touched), "every target is at its stated after sha256")
    mark(all(after_state[r] == (gb / r).read_bytes() for r in TOUCHED), "the applied bytes are the generation's")
    pc, pf = portability(reh)
    mark(pc == 0 and not pf, f"portability after the apply: exit {pc}; findings {pf}")
    step(reh, "apply.sh undo", f"bash {bundle}/apply.sh undo")
    mark(state(reh) == before_state and changed_set(reh) == [], "undo: every file byte for byte back, the tree clean")
    pc, pf = portability(reh)
    sayv(f"     portability after the undo: exit {pc}; {len(pf)} findings: {tally(pf)} (the window's own reading)")
    step(reh, "apply.sh check after the undo", f"bash {bundle}/apply.sh check")
    step(reh, "apply.sh apply (re-apply)", f"bash {bundle}/apply.sh apply")
    mark(state(reh) == after_state and changed_set(reh) == TOUCHED, "the re-apply gives the same bytes and the same changed set")
    must(["bash", "-c", f"bash {bundle}/apply.sh undo"], reh)

    sayv(f"--- integrate at its head when built ({LIVE_HEAD[:12]}; COPIES-6 landed by hand at 36d1a151b): as G7/G8 run it")
    now = clone(f"t-now-{act}", LIVE_HEAD)
    if act == "ACT-CLAUDE-COPIES-8":
        step(now, "apply.sh check", f"bash {bundle}/apply.sh check")
        step(now, "check 2 before the apply (green)", CHECKS[1]["cmd"])
        step(now, "apply.sh apply", f"bash {bundle}/apply.sh apply")
        for i, c in enumerate(CHECKS, 1):
            step(now, f"check {i}", c["cmd"])
        mark(changed_set(now) == TOUCHED, f"the changed set equals the touched list ({len(TOUCHED)} files)")
        pc, pf = portability(now)
        mark(pc == 0 and not pf, f"portability after the apply: exit {pc}; findings {pf}")
        step(now, "apply.sh undo, the tree clean", f"bash {bundle}/apply.sh undo && test -z \"$(git status --porcelain)\"")
    else:
        step(now, "apply.sh check (refused at G7 while b88a76172 stands: the sources are at their after bytes)",
             f"bash {bundle}/apply.sh check", 3)
        step(now, "the same head with b88a76172 reverted: apply.sh check, apply, both checks, undo",
             f"{GIT} revert --no-edit {REV[SRC_C]} >/dev/null && bash {bundle}/apply.sh check && bash {bundle}/apply.sh apply"
             f" && ({CHECKS[0]['cmd']}\n) >/dev/null && ({CHECKS[1]['cmd']}\n) >/dev/null && bash {bundle}/apply.sh undo")

    sayv("--- out of order: each tree is a dry run as G7/G8 runs it (check, apply, checks); every one must be refused")

    def out_of_order(name, tree):
        t = SCRATCH / f"ooo-{act}-{len(vlog)}"
        if t.exists():
            shutil.rmtree(t)
        must(["git", "clone", "-q", "--shared", str(tree), str(t)], SCRATCH)
        code = run(["bash", "-c", f"bash {bundle}/apply.sh check"], t)[0]
        if code != 0:
            mark(True, f"{name}: apply.sh check exit {code} (G7 refuses)")
            return
        run(["bash", "-c", f"bash {bundle}/apply.sh apply"], t)
        c1 = run(["bash", "-c", CHECKS[0]["cmd"]], t)[0]
        c2 = run(["bash", "-c", CHECKS[1]["cmd"]], t)[0]
        mark(c2 == 1, f"{name}: apply.sh check exit 0; after the apply check 1 exit {c1}, check 2 exit {c2} (G8 refuses)")

    pre = clone(f"t-pre-{act}", PRE_C)
    pre_c6 = clone(f"t-pre-c6-{act}", PRE_C); apply_c6(pre_c6)
    pat = clone(f"t-patch-{act}", PATCH_C)
    pat_c6 = clone(f"t-patch-c6-{act}", PATCH_C); apply_c6(pat_c6)
    src = clone(f"t-src-{act}", SRC_C)
    src_c6 = full_default
    if act == "ACT-CLAUDE-COPIES-8":
        out_of_order("W2-33's merge alone (no template patch, no sources' commit, no COPIES-6)", pre)
        out_of_order("W2-33's merge and COPIES-6 (no template patch, no sources' commit)", pre_c6)
        out_of_order("the template patch and COPIES-6, before the sources' commit", pat_c6)
        out_of_order("integrate at the sources' commit, before COPIES-6", src)
    else:
        out_of_order("W2-33's merge alone", pre)
        out_of_order("W2-33's merge and COPIES-6, before the template patch", pre_c6)
        out_of_order("the template patch, before COPIES-6", pat)
        out_of_order("integrate at the sources' commit (not reverted), before COPIES-6", src)
        out_of_order("integrate at the sources' commit (not reverted), after COPIES-6", src_c6)

    sayv("--- the gated runs, one folder per pytest run through the heavy-job gate: the window (this form's tree before "
         "the ACT) and the landed tree (both forms land the same bytes)" +
         ("; re-read from the first build's output files in the same scratch folder (the same commits' bytes)" if REUSE else ""))
    for st, text in gated_lines("window-default" if act == "ACT-CLAUDE-COPIES-8" else "window-with-sources"):
        if st:
            mark(st == "ok", text)
        else:
            sayv(text)

    sayv("--- the by-hand steps literally")
    paths = " ".join(TOUCHED)
    step(reh, "apply.sh check, apply", f"bash {bundle}/apply.sh check && bash {bundle}/apply.sh apply")
    step(reh, "git add the touched paths", f"git add {paths}")
    step(reh, "staged count equals the touched list", f"test \"$(git diff --cached --name-only | wc -l)\" = {len(TOUCHED)}")
    step(reh, "commit", f"{GIT} commit -q -m '{act}: rehearsal' --trailer 'Task: DAEO-sdxk' --trailer 'Role: owner'")
    pc, pf = portability(reh)
    mark(pc == 0 and not pf, f"portability after the commit: exit {pc}; findings {pf}")
    step(reh, "apply.sh undo", f"bash {bundle}/apply.sh undo")
    step(reh, "git add the touched paths (undo)", f"git add -A {paths}")
    step(reh, "commit the undo", f"{GIT} commit -q -m '{act} undone' --trailer 'Task: DAEO-sdxk' --trailer 'Role: owner'")
    step(reh, "the undo commit returns the tree to the start (empty diff over the touched paths)",
         f"git diff --quiet HEAD~2 HEAD -- {paths}")
    def live_ok(rel):  # unchanged, or moved by a live commit (another actor's), never an uncommitted write
        if live_state()[rel] == live_before[rel]:
            return True
        code, _ = run(["bash", "-c", f"git diff --quiet HEAD -- {rel} && git diff --cached --quiet -- {rel}"], LIVE_TREE)
        return code == 0
    moved = [r for r in ALLREL if live_state()[r] != live_before[r]]
    mark(all(live_ok(r) for r in ALLREL) and not any(planted.iterdir()),
         "the live files not written by the rehearsal (unchanged, or moved only by a live commit"
         + (f": {moved}, committed by another actor during the build" if moved else "") + "), nothing written to the planted HOME")
    sayv(f"failures: {fails}")
    return vlog, fails


summary = {}
for act in VARIANTS:
    vlog, fails = rehearse(act)
    bundle, base, files, touched = built[act]
    data = ("\n".join(vlog) + "\n").encode()
    (bundle / "rehearsal.log").write_bytes(data)
    files["rehearsal.log"] = sha(data)
    mf = {"act": act, "dec": DEC, "author": "cto", "claimed_class": "b", "touched": touched, "files": files,
          "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]}, "checks": CHECKS, "commands": []}
    raw = json.dumps(mf, indent=1).encode()
    assert not HOME_RX.search(json.dumps(CHECKS))
    (bundle / "manifest.json").write_bytes(raw)
    summary[act] = {"manifest_sha256": sha(raw), "touched": len(touched), "failures": fails}
(SCRATCH / "build.log").write_text("\n".join(log) + "\n")
print(json.dumps(summary))
