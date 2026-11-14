"""Builds and rehearses ACT-CLAUDE-RULES-1 (the "## Guard" paragraph of .rulesync/rules/governance.md made true for this
repository, with CLAUDE.md and AGENTS.md regenerated from it by rulesync 24.0.0; the owner, DEC-1167 (7)).

    python3 -I build_claude_rules_act_1.py build     <repo>            freeze the bundle: the source's after by patch_source.py, the two copies by rulesync
    python3 -I build_claude_rules_act_1.py rehearse  <repo> <scratch>  the rehearsal on fresh clones; writes rehearsal.log
    python3 -I build_claude_rules_act_1.py finalize                    the manifest with the rehearsal log's sha256
    python3 -I build_claude_rules_act_1.py gates     <evidence dir>    the operator's read-only gates over the bundle

CLAUDE.md and AGENTS.md are never edited by hand: rulesync generates them from the new source in an empty folder (the
procedure of gov.adapters.portability: GENERATE, then the held-out step on the generated settings), and the builder
asserts that nothing else the generation writes differs from the tree. .claude/settings.json is not regenerated (the
generation reproduces the live one byte for byte before and after, asserted, and the ACT does not write it). The class
is the classifier's: CLAUDE.md and AGENTS.md are named by no row of the rule table, so it is (O)."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "act-landing-cto-route-1"))
from actkit import INSTALL, LIVE, ORCH, Log, clone, failed_ids, git, pytest, run, sha, shab  # noqa: E402

ACT = "ACT-CLAUDE-RULES-1"
DEC = "DEC-1167 (7), DEC-953 (2), DEC-1128 (4), DEC-820, CAP-33"
BUNDLE = ORCH / "acts" / ACT
SRC = ".rulesync/rules/governance.md"
TEMPLATE_SRC = "template/.rulesync/rules/governance.md"
FILES = [SRC, "CLAUDE.md", "AGENTS.md"]
SETTINGS = ".claude/settings.json"
GENERATE = ["generate", "--targets", "claudecode,agentsmd", "--features", "rules,hooks,permissions,subagents,commands,skills",
            "--input-roots"]
RULESYNC = shutil.which("rulesync") or str(Path.home() / ".local/bin/rulesync")
APPLY_SH = ORCH / "acts/ACT-CLAUDE-COPIES-7/apply.sh"     # the same apply.sh as ACT-CLAUDE-COPIES-1 to -9 (repo rows, $PWD)


def generate(tree, dest):
    """rulesync generate from tree/.rulesync into the empty folder dest, then the held-out step on its settings; {path: bytes}."""
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    code, out = run([RULESYNC, *GENERATE, str((Path(tree) / ".rulesync").resolve())], cwd=dest)
    assert code == 0, out[-400:]
    probe = ("import sys; sys.path.insert(0, sys.argv[1] + '/src'); from gov.guard import heldout; "
             "heldout.write_read_rules(sys.argv[1], sys.argv[2])")
    code, out = run([sys.executable, "-I", "-c", probe, str(tree), str(dest / SETTINGS)])
    assert code == 0, "the held-out step failed (" + out.strip().splitlines()[-1].split(":")[0] + ")"
    return {str(f.relative_to(dest)): f.read_bytes() for f in sorted(dest.rglob("*")) if f.is_file()}


def differing(made, tree):
    return sorted(rel for rel, b in made.items() if not (Path(tree) / rel).is_file() or (Path(tree) / rel).read_bytes() != b)


def write_manifest(rehearsal_sha, tpl):
    rows = [ln.split("|") for ln in (BUNDLE / "list.txt").read_text().splitlines()]
    touched = [{"root": r, "path": p, "before": b, "after": a} for r, p, b, a in rows]
    files = {}
    for side in ("before", "after"):
        for f in sorted((BUNDLE / side).rglob("*")):
            if f.is_file():
                files[str(f.relative_to(BUNDLE))] = sha(f)
    for n in ("apply.sh", "list.txt"):
        files[n] = sha(BUNDLE / n)
    after = {p: a for r, p, b, a in rows}
    c1 = "sha256sum -c - <<'EOF'\n" + "".join(f"{after[p]}  {p}\n" for p in FILES) + "EOF"
    c2 = f"sha256sum -c - <<'EOF'\n{tpl}  {TEMPLATE_SRC}\nEOF"
    gone = f"grep -l -e 'writes stay inside the ticket' -e 'refuses writes outside a ticket' {' '.join(FILES)} | wc -l"
    here = f"grep -l 'OS sandbox of .gov launch.' {' '.join(FILES)} | wc -l"
    m = {"act": ACT, "dec": DEC, "author": "cto", "claimed_class": "O", "touched": touched, "files": files,
         "checks": [{"cmd": c1, "exit": 0, "count": None}, {"cmd": c2, "exit": 0, "count": None},
                    {"cmd": gone, "exit": 0, "count": 0}, {"cmd": here, "exit": 0, "count": 3}],
         "commands": []}
    if rehearsal_sha:
        files["rehearsal.log"] = rehearsal_sha
        m["rehearsal"] = {"log": "rehearsal.log", "sha256": rehearsal_sha}
    (BUNDLE / "manifest.json").write_text(json.dumps(m, indent=1) + "\n")
    return sha(BUNDLE / "manifest.json")


def build(repo, scratch):
    keep_review = None
    if BUNDLE.exists():
        rv = BUNDLE / "review.md"
        assert not rv.exists() or "not written yet" in rv.read_text(), "the bundle holds a written review: move it aside"
        keep_review = rv.read_text() if rv.exists() else None
        shutil.rmtree(BUNDLE)
    scratch.mkdir(parents=True, exist_ok=True)
    head = clone(repo, scratch / "base")
    base, gen1 = scratch / "base", scratch / "gen1"
    clone(repo, gen1, head)
    for f in FILES + [TEMPLATE_SRC, SETTINGS]:
        assert (base / f).read_bytes() == (LIVE / f).read_bytes(), f"the main tree's {f} differs from HEAD"
    before = {f: (base / f).read_bytes() for f in FILES}
    code, out = run([sys.executable, "-I", str(HERE / "patch_source.py"), str(base / SRC), str(gen1 / SRC)])
    assert code == 0, out
    # the generation from the unchanged source: what already differs on the tree (another ACT's window), and that CLAUDE.md,
    # AGENTS.md and the settings are what it writes
    g0 = generate(base, scratch / "out0")
    d0 = differing(g0, base)
    assert "CLAUDE.md" not in d0 and "AGENTS.md" not in d0 and SETTINGS not in d0, d0
    g1 = generate(gen1, scratch / "out1")
    d1 = differing(g1, base)
    assert sorted(set(d1) - set(d0)) == ["AGENTS.md", "CLAUDE.md"] and set(d0) <= set(d1), (d0, d1)
    assert all(g0[k] == g1[k] for k in g0 if k not in ("CLAUDE.md", "AGENTS.md")) and set(g0) == set(g1), \
        "the new source changes more of the generation than CLAUDE.md and AGENTS.md"
    assert g1[SETTINGS] == (base / SETTINGS).read_bytes(), "the generated settings are not the tree's"
    after = {SRC: (gen1 / SRC).read_bytes(), "CLAUDE.md": g1["CLAUDE.md"], "AGENTS.md": g1["AGENTS.md"]}
    lines = []
    for f in FILES:
        for side, data in (("before", before[f]), ("after", after[f])):
            p = BUNDLE / side / "repo" / f
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        assert shab(before[f]) != shab(after[f]), f
        lines.append(f"repo|{f}|{shab(before[f])}|{shab(after[f])}")
    (BUNDLE / "list.txt").write_text("\n".join(lines) + "\n")
    shutil.copy(APPLY_SH, BUNDLE / "apply.sh")
    (BUNDLE / "apply.sh").chmod(0o755)
    (BUNDLE / "review.md").write_text(keep_review or f"# {ACT}: the ACT review\n\nReview: not written yet\n")
    m = write_manifest(None, shab((base / TEMPLATE_SRC).read_bytes()))
    print(f"built {BUNDLE} on {head[:12]}; generation baseline differing {d0}; manifest {m}")
    return head


def rehearse(repo, scratch):
    log = Log(BUNDLE / "rehearsal.log")
    tmp, ev = scratch / "tmp", scratch / "evidence"
    ev.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((BUNDLE / "manifest.json").read_text())
    rows = [ln.split("|") for ln in (BUNDLE / "list.txt").read_text().splitlines()]
    before = {p: b for r, p, b, a in rows}
    after = {p: a for r, p, b, a in rows}
    live = {p: sha(LIVE / p) for p in FILES + [TEMPLATE_SRC, SETTINGS]}
    live_status = git(LIVE, "status", "--porcelain", "--untracked-files=all", "--", *FILES, TEMPLATE_SRC, SETTINGS)[1]
    home = scratch / "home"
    home.mkdir(parents=True, exist_ok=True)
    env_home = dict(os.environ, HOME=str(home))

    def apply(cwd, step):
        code, out = run(["bash", str(BUNDLE / "apply.sh"), step], cwd=cwd, env=env_home)
        return code, out.strip()

    def at(cwd, which):
        want = before if which == "before" else after
        return all((Path(cwd) / p).is_file() and sha(Path(cwd) / p) == want[p] for p in FILES)

    def portability(cwd):
        env = dict(os.environ, PYTHONPATH=str(Path(cwd) / "src"), RULESYNC_BIN=RULESYNC)
        code, out = run([sys.executable, "-m", "gov.adapters.portability"], cwd=cwd, env=env)
        found = json.loads(out)["findings"] if out.strip().startswith("{") else [{"code": "UNREADABLE", "file": out[-200:]}]
        return code, sorted((f["code"], f.get("file", "")) for f in found)

    def run_checks(cwd, manifest):
        res = []
        for c in manifest["checks"]:
            code, out = run(["bash", "-c", c["cmd"]], cwd=cwd, env=env_home)
            last = [ln for ln in out.strip().splitlines() if ln.strip()][-1:] or [""]
            res.append(code == c["exit"] and (c["count"] is None or last[0].strip() == str(c["count"])))
        return res

    log.say(f"{ACT} rehearsal; bundle {BUNDLE}; rulesync {run([RULESYNC, '--version'])[1].strip()}")
    log.head("A. the bundle")
    log.case(all(sha(BUNDLE / p) == h for p, h in manifest["files"].items() if p != "rehearsal.log"), "A1 every file the manifest names hashes as it says")
    log.case([f"{t['root']}|{t['path']}|{t['before']}|{t['after']}" for t in manifest["touched"]] == (BUNDLE / "list.txt").read_text().splitlines(), "A2 list.txt equals the manifest's touched list")
    log.case(all(live[p] == before[p] for p in FILES), "A3 the main tree's three files are at their before hashes")
    log.case(sha(BUNDLE / "apply.sh") == sha(APPLY_SH) and subprocess.run(["bash", "-n", str(BUNDLE / "apply.sh")]).returncode == 0, "A4 apply.sh is the copies ACTs' apply.sh and parses")
    log.case(not list(BUNDLE.rglob("__pycache__")), "A5 no __pycache__ in the bundle")

    log.head("B. a fresh clone of w2/integrate (HOME planted at an empty folder)")
    R = scratch / "clone"
    head = clone(repo, R)
    log.note(f"clone at {head[:12]}")
    log.case(all(sha(R / p) == before[p] for p in FILES), "B1 each of the three is at its before hash (CLAUDE.md, AGENTS.md, .rulesync/rules/governance.md)")
    log.case(sha(R / TEMPLATE_SRC) == live[TEMPLATE_SRC], "B2 the template's rule source is unchanged and is not in the bundle")
    code, base_found = portability(R)
    log.note(f"portability before: exit {code}; findings {base_found}")
    code0, out = apply(R, "check")
    log.case(code0 == 0 and out == "", "B3 apply.sh check: exit 0, prints nothing")
    pre = run_checks(R, manifest)
    log.case(not pre[0] and pre[2] is False and pre[3] is False, f"B4 the manifest's checks before the apply: the after hashes, the gone sentence and the new sentence refuse ({pre})")
    code, out = apply(R, "apply")
    log.case(code == 0 and at(R, "after"), "B5 apply (exit 0): the three files are the frozen after, byte for byte")
    post = run_checks(R, manifest)
    log.case(all(post), f"B6 the manifest's four checks after the apply ({post})")
    st = run(["git", "-C", str(R), "status", "--porcelain", "--untracked-files=all"])[1].splitlines()
    log.case(sorted(ln[3:] for ln in st) == sorted(FILES), "B7 the clone's changed set is the three files", ", ".join(sorted(ln[3:] for ln in st)))
    log.case(sha(R / SETTINGS) == live[SETTINGS] and sha(R / TEMPLATE_SRC) == live[TEMPLATE_SRC], "B8 .claude/settings.json and the template's rule source are not written")
    # an independent generation, never by hand: rulesync and the held-out step again, on the clone's own new source
    g = generate(R, scratch / "out-clone")
    log.case(g["CLAUDE.md"] == (R / "CLAUDE.md").read_bytes() and g["AGENTS.md"] == (R / "AGENTS.md").read_bytes(), "B9 a fresh rulesync generation from the applied source gives CLAUDE.md and AGENTS.md byte for byte")
    log.case(g[SETTINGS] == (R / SETTINGS).read_bytes(), "B10 and the held-out step gives .claude/settings.json byte for byte the tree's: the ACT has nothing to write there")
    codeA, found_after = portability(R)
    log.case(found_after == base_found and not any(f[1] in ("CLAUDE.md", "AGENTS.md", SRC) for f in found_after),
             f"B11 portability after: the same findings as before ({len(found_after)}), none on the three files", str(found_after))
    code, out = apply(R, "check")
    log.case(code == 3 and "moved:" in out, "B12 check after the apply refuses (a file has moved: exit 3)")
    code, out = apply(R, "undo")
    log.case(code == 0 and at(R, "before") and run(["git", "-C", str(R), "status", "--porcelain", "--untracked-files=all"])[1].strip() == "", "B13 undo: byte for byte the before, the tree clean")
    code, out = apply(R, "apply")
    log.case(code == 0 and at(R, "after"), "B14 apply again gives the same bytes")

    log.head("C. why the three go together, and refusals")
    cw = scratch / "c-window"
    clone(repo, cw, head)
    shutil.copyfile(BUNDLE / "after/repo" / SRC, cw / SRC)
    codeW, found_w = portability(cw)
    new = sorted(set(found_w) - set(base_found))
    log.case(new == [("GENERATED_DIFFERS", "AGENTS.md"), ("GENERATED_DIFFERS", "CLAUDE.md")], "C1 the source alone (copies not yet written): portability reads GENERATED_DIFFERS for CLAUDE.md and AGENTS.md", str(new))
    for name, victim in (("claude", "CLAUDE.md"), ("agents", "AGENTS.md"), ("src", SRC)):
        c = scratch / f"c-{name}"
        clone(repo, c, head)
        (c / victim).write_text((c / victim).read_text() + "\nmoved\n")
        code, out = apply(c, "check")
        log.case(code == 3 and f"moved: {victim}" in out, f"C{2 + ['claude', 'agents', 'src'].index(name)} {victim} changed: check refuses naming it (exit 3)")
    code, out = run(["grep", "-rIl", "-e", "writes stay inside the ticket", "-e", "refuses writes outside a ticket", "tests"], cwd=R)
    log.case(code == 1 and out.strip() == "", "C5 no test names the replaced sentences (grep over tests/: no file)")

    log.head("D. the owner's steps literally (the three staged, the commit, the undo)")
    p0 = git(R, "rev-parse", "HEAD")[1]
    code, _ = run(["git", "-C", str(R), "add", *FILES])
    log.case(code == 0 and sorted(git(R, "diff", "--cached", "--name-only")[1].splitlines()) == sorted(FILES), "D1 the three paths staged, and only them")
    code, out = run(["git", "-C", str(R), "commit", "-q", "-m", f"{ACT}: the Guard paragraph of the governance rule is true for this repository", "--trailer", "Task: DAEO-sdxk",
                     "--trailer", "Implements: DEC-1167", "--trailer", "Role: owner", "--", *FILES])
    log.case(code == 0, "D2 the commit with Role: owner", out.strip()[-100:])
    c1 = git(R, "rev-parse", "HEAD")[1]
    code, out = run([sys.executable, "-I", str(INSTALL / "landing_check.py"), "--repo", str(R), f"{p0}..{c1}"])
    log.case(code == 0 and json.loads(out.strip().splitlines()[-1]) == [], "D3 the operator's landing check (Role: owner) raises nothing for the commit")
    code, out = apply(R, "undo")
    log.case(code == 0 and at(R, "before"), "D4 apply.sh undo")
    run(["git", "-C", str(R), "add", "-A", *FILES])
    code, out = run(["git", "-C", str(R), "commit", "-q", "-m", f"{ACT}: undo", "--trailer", "Task: DAEO-sdxk", "--trailer", "Role: owner"])
    log.case(code == 0, "D5 the undo commit")
    log.case(git(R, "diff", "--stat", p0, "HEAD", "--", *FILES)[1] == "", "D6 an empty diff over the three paths against the start")
    code, _ = apply(R, "apply")
    run(["git", "-C", str(R), "add", *FILES])
    run(["git", "-C", str(R), "commit", "-q", "-m", f"{ACT}: again", "--trailer", "Task: DAEO-sdxk", "--trailer", "Role: owner"])
    c2 = git(R, "rev-parse", "HEAD")[1]
    log.case(at(R, "after"), "D7 and the apply and commit go through again")

    log.head("E. the tests (each folder one run through heavy_slot.sh, TMPDIR outside the repository; the clone after the apply)")
    # the suites that read the rules, the generated copies, portability or the rulesync sources; before and after on the same clone
    suites = ["tests/unit/adapters", "tests/acceptance/W1-38", "tests/acceptance/W2-23", "tests/acceptance/W2-153", "tests/acceptance/W2-98",
              "tests/acceptance/W2-106", "tests/acceptance/W1-33"]
    cb = scratch / "tests-before"
    clone(repo, cb, head)
    reds_before, reds_after = {}, {}
    for s in suites:
        tag = s.replace("/", "_")
        c_a, last_a = pytest(R, [s], tmp / f"a-{tag}", ev / f"after-{tag}.txt")
        c_b, last_b = pytest(cb, [s], tmp / f"b-{tag}", ev / f"before-{tag}.txt")
        reds_after[s], reds_before[s] = failed_ids(ev / f"after-{tag}.txt"), failed_ids(ev / f"before-{tag}.txt")
        log.case(set(reds_after[s]) <= set(reds_before[s]) and c_a in (0, 1) and c_b in (0, 1) and (c_a == 0 or reds_after[s]),
                 f"E {s}: before exit {c_b} ({last_b}); after exit {c_a} ({last_a}); no new red", "" if c_a == 0 else f"reds after {len(reds_after[s])}, before {len(reds_before[s])}")
    new_red = {s: sorted(set(reds_after[s]) - set(reds_before[s])) for s in suites}
    log.case(not any(new_red.values()), "E-all new red brought by the ACT: none", str({k: v for k, v in new_red.items() if v}))

    log.head("F. the operator's read-only gates, and the classifier")
    sys.path.insert(0, str(INSTALL))
    sys.dont_write_bytecode = True
    import act_class
    import opcommon as oc
    import operator_run as orun
    try:
        orun.validate_manifest(manifest)
        v = True
    except ValueError as e:
        v = str(e)
    log.case(v is True, "F1 validate_manifest (the operator's own): pass", "" if v is True else v)
    try:
        orun.check_act(manifest, ACT)
        v = True
    except oc.Refused as e:
        v = str(e)
    log.case(v is True, "F2 check_act: pass")
    try:
        orun.path_rule(str(BUNDLE), manifest, oc.load_settings())
        v = True
    except oc.Refused as e:
        v = str(e)
    log.case(v is True, "F3 path_rule: pass", "" if v is True else v)
    cls = act_class.classify(str(BUNDLE))
    rowset = {f["path"]: f["row"] for f in cls["files"]}
    log.case(cls["class"] == "O" and not cls["hits"] and rowset.get(SRC) == "rulesync-other" and rowset.get("CLAUDE.md") == "unknown",
             f"F4 act_class: class {cls['class']} (the manifest claims {manifest['claimed_class']}); rows {rowset}; hits {cls['hits']}")
    unnamed = sorted(str(p.relative_to(BUNDLE)) for p in BUNDLE.rglob("*") if p.is_file()
                     and str(p.relative_to(BUNDLE)) not in set(manifest["files"]) | {"manifest.json", "review.md", "rehearsal.log"})
    log.case(not unnamed and not list(BUNDLE.rglob("__pycache__")), "F5 no unlisted file and no __pycache__ in the bundle", str(unnamed))

    log.head("G. the live files")
    log.case(all(sha(LIVE / p) == live[p] for p in live) and git(LIVE, "status", "--porcelain", "--untracked-files=all", "--", *FILES, TEMPLATE_SRC, SETTINGS)[1] == live_status,
             "G1 the main tree's three files, the template's source and the settings are byte for byte as before")
    log.case(not any(home.iterdir()), "G2 nothing was written to the planted HOME")
    n = log.finish()
    return n


def finalize():
    import re
    old = json.loads((BUNDLE / "manifest.json").read_text())["checks"][1]["cmd"]
    tpl = re.search(r"^([0-9a-f]{64})  ", old, re.M).group(1)
    print("manifest sha256", write_manifest(sha(BUNDLE / "rehearsal.log"), tpl))


def gates(evid):
    sys.path.insert(0, str(INSTALL))
    sys.dont_write_bytecode = True
    import act_class
    import opcommon as oc
    import operator_run as orun
    out = [f"manifest sha256: {sha(BUNDLE / 'manifest.json')}"]
    m = json.loads((BUNDLE / "manifest.json").read_text())
    for name, fn in (("validate_manifest", lambda: orun.validate_manifest(m)), ("check_act", lambda: orun.check_act(m, ACT)),
                     ("path_rule", lambda: orun.path_rule(str(BUNDLE), m, oc.load_settings()))):
        try:
            fn()
            out.append(f"{name}: pass")
        except (ValueError, oc.Refused) as e:
            out.append(f"{name}: FAIL {e}")
    bad = [p for p, h in m["files"].items() if sha(BUNDLE / p) != h]
    named = set(m["files"]) | {"manifest.json", "review.md"}
    unnamed = sorted(str(p.relative_to(BUNDLE)) for p in BUNDLE.rglob("*") if p.is_file() and str(p.relative_to(BUNDLE)) not in named)
    out.append(f"hash mismatches: {bad} ; unnamed on disk: {unnamed}")
    cls = act_class.classify(str(BUNDLE))
    out.append(f"act_class: class {cls['class']}; rows {sorted({f['row'] for f in cls['files']})}; hits {cls['hits']}")
    Path(evid).mkdir(parents=True, exist_ok=True)
    (Path(evid) / "operator_gates.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "build":
        build(Path(sys.argv[2]), Path(sys.argv[3]))
    elif cmd == "rehearse":
        sys.exit(1 if rehearse(Path(sys.argv[2]), Path(sys.argv[3])) else 0)
    elif cmd == "finalize":
        finalize()
    elif cmd == "gates":
        gates(sys.argv[2])
