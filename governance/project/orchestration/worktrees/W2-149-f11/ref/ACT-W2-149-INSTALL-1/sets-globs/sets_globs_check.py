"""ACT-SETS-GLOBS-1: the guard check cases for the three new hidden globs, by class of action (never a worked bypass).

  python3 sets_globs_check.py <tree> [hook]     the tree's hook (default <tree>/.claude/hooks/pretooluse.py) under the
                                                pinned judge, with event JSON, as guard4_check.py and walls_check.py do

The globs (the main tree's sets_root_hidden): fixtures/evaluation/*/hidden/** (a writer's new set), fixtures/evaluation/
*/XCHECK-r*.md (the checker's notes), runs/*/miss-classes.json (an audit's classes) and runs/*/misses.jsonl (an
audit's misses: they name the questions missed).
  N   each new destination refused to the six roles, the CTO, a lead, their subagents and the tuner: Read, Bash, Grep,
      Glob, Write, a Bash write; under the sets root and in every tree
  L   the line rule: a line naming the root together with a new destination (or its last name quoted) refused
  S   the launch script's own lines (only --sets-root <root>) allowed, before and after
  O   nothing else changed: a set's other files (visible/, README, the manual XCHECK.md, hidden-notes.md, a deeper
      XCHECK-r1.md), every other file under runs/ (classes.json, report.md, counts.txt, a deeper miss-classes.json or
      misses.jsonl, misses.jsonl.bak),
      the folders above (fixtures/evaluation, runs) read, listed and named on a line with the root: allowed, before and
      after; the sessions no rule names; prose naming the globs without the root
SG_EXPECT=before expects the answers before the ACT (each N and L case an allow: the gap). SETS_PLANTED=1 runs the R
cases (they need the planted files of PLANTED below under the root). A case naming ~ or $HOME runs only when the block's
root is ~/gov-os-eval as this HOME expands it. SG_TREE2: a second tree (a worktree) for the every-tree cases.
Prints one line per case and a last line PASS or FAIL. Reads no file: the hook decides from names alone.
"""
import json
import os
import subprocess
import sys

PY = os.environ.get("GOV_PIN_PY") or open(os.path.expanduser("~/.local/bin/gov")).readline()[2:].strip()
BEFORE = os.environ.get("SG_EXPECT") == "before"
PLANTED = os.environ.get("SETS_PLANTED") == "1"
HOME_NOW = os.path.realpath(os.path.expanduser("~"))
CASES = []
# The planted files the R cases name (relative to the sets root); rehearse.sh plants exactly these (dummy lines).
PLANTED_FILES = ["fixtures/evaluation/memory-verdict-4/hidden/q01.yaml",
                 "fixtures/evaluation/memory-verdict-4/visible/q01.yaml",
                 "fixtures/evaluation/memory-verdict-4/XCHECK-r1.md",
                 "fixtures/evaluation/memory-verdict-4/XCHECK.md",
                 "fixtures/evaluation/memory-verdict-4/README.md",
                 "runs/audit-sg/miss-classes.json", "runs/audit-sg/misses.jsonl", "runs/audit-sg/classes.json"]


def case(cid, roles, tool, tins, want, tag, before=None, **extra):
    b = before or ("allow" if want == "deny" else want)
    for label, role, agent in roles:
        for tin in tins:
            form = tin.get("command") or tin.get("file_path") or f"{tin.get('path')} {tin.get('pattern', '')}"
            CASES.append((f"{cid} {label} {tool}: {form}", role, tool, tin, b if BEFORE else want,
                          dict(extra, tag=tag, agent=agent)))


def R_(p):
    return {"file_path": p}


def B_(c):
    return {"command": c}


def W_(p):
    return {"file_path": p, "content": "x"}


def cases(tree):
    import yaml
    block = yaml.safe_load(open(tree + "/governance/project/path-map.yaml")).get("sets_root_hidden") or {}
    sr = os.path.realpath(os.path.expanduser(block.get("root", "~/gov-os-eval")))
    same_home = sr == os.path.realpath(os.path.expanduser("~/gov-os-eval"))
    E = sr + "/fixtures/evaluation"
    NS = E + "/zz-sg-new"            # a new set (L: nothing there)
    NA = sr + "/runs/zz-sg-audit"    # a new audit (L)
    PS = E + "/memory-verdict-4"     # a delivered set (R: planted)
    PA = sr + "/runs/audit-sg"       # a delivered audit (R: planted)
    NX = "zz-sg-none.txt"
    LX = "governance/project/orchestration/tools/indep_launch.py"  # the launch script, named only
    trees = [tree] + ([os.environ["SG_TREE2"]] if os.environ.get("SG_TREE2") else [])
    M = [("engineer", "engineer", None), ("research", "research", None), ("orchestrator (the CTO)", "orchestrator", None),
         ("lead", "orchestrator@DAEO-0uhh", None), ("product-spec", "product-spec", None),
         ("test designer", "independent-test-designer", None), ("auditor", "independent-auditor", None),
         ("CTO's engineer subagent", "orchestrator", "engineer"),
         ("CTO's general-purpose subagent", "orchestrator", "general-purpose"),
         ("the tuner (engineer@DAEO-wnnz)", "engineer@DAEO-wnnz", None)]
    U = [("no GOV_ROLE", "", None), ("ticket-lead", "ticket-lead", None)]
    pick = lambda *names: [r for r in M if r[0] in names]  # noqa: E731
    ERO = pick("engineer", "research", "orchestrator (the CTO)", "the tuner (engineer@DAEO-wnnz)")
    OL = pick("orchestrator (the CTO)", "lead")

    # N: each new destination refused, every measured role
    case("N1", M, "Read", [R_(f"{NS}/hidden/{NX}"), R_(f"{NS}/hidden/sub/{NX}"), R_(f"{NS}/XCHECK-r1.md"),
                           R_(f"{NS}/XCHECK-r12.md"), R_(f"{NA}/miss-classes.json"),
                           R_(f"{NA}/misses.jsonl")], "deny", "L")
    case("N1t", M, "Read", [R_(f"{t}/fixtures/evaluation/zz-sg-new/hidden/{NX}") for t in trees] +
         [R_(f"{t}/fixtures/evaluation/zz-sg-new/XCHECK-r2.md") for t in trees] +
         [R_(f"{t}/runs/zz-sg-audit/miss-classes.json") for t in trees] +
         [R_(f"{t}/runs/zz-sg-audit/misses.jsonl") for t in trees], "deny", "L")
    case("N1r", M, "Read", [R_(f"{PS}/hidden/q01.yaml"), R_(f"{PS}/XCHECK-r1.md"), R_(f"{PA}/miss-classes.json"),
                            R_(f"{PA}/misses.jsonl")], "deny", "R")
    case("N2", ERO, "Bash", [B_(f"cat {NS}/hidden/{NX}"), B_(f"head -3 {NS}/XCHECK-r2.md"),
                             B_(f"python3 -c \"print(open('{NA}/miss-classes.json').read())\""),
                             B_(f"wc -l {NA}/misses.jsonl")], "deny", "L")
    case("N2r", ERO, "Bash", [B_(f"cat {PS}/XCHECK-r1.md"), B_(f"ls {PS}/hidden"), B_(f"ls {PA}"),
                              B_(f"grep -rn x {PS}"), B_(f"wc -l {PA}/miss-classes.json"),
                              B_(f"tail -1 {PS}/hidden/q01.yaml"), B_(f"cat {PA}/misses.jsonl")], "deny", "R")
    case("N3", ERO, "Grep", [{"pattern": "x", "path": PS}, {"pattern": "x", "path": PA},
                             {"pattern": "x", "path": f"{PS}/hidden"}], "deny", "R")
    case("N3g", ERO, "Glob", [{"path": f"{sr}/runs", "pattern": "*/miss-classes.json"},
                              {"path": PS, "pattern": "*.md"}, {"path": PS, "pattern": "hidden/*"},
                              {"path": PA, "pattern": "*.jsonl"}], "deny", "R")
    case("N4", [r for r in M if r[0] != "auditor"], "Write",
         [W_(f"{NS}/hidden/{NX}"), W_(f"{NS}/XCHECK-r1.md"), W_(f"{NA}/miss-classes.json"),
          W_(f"{NA}/misses.jsonl")], "deny", "L")
    case("N4a", pick("auditor"), "Write", [W_(f"{NS}/XCHECK-r1.md")], "deny", "L", before="deny")
    case("N4b", pick("engineer", "orchestrator (the CTO)", "lead"), "Bash",
         [B_(f"echo x > {NS}/XCHECK-r1.md"), B_(f"cp /tmp/zz-sg-a {NA}/miss-classes.json"),
          B_(f"mkdir -p {NS}/hidden && : > {NS}/hidden/{NX}"), B_(f"echo x >> {NA}/misses.jsonl")], "deny", "L")
    # L: the line rule (the judge cannot place a path the shell or a tool's code builds from the root)
    case("L1", OL, "Bash", [B_(f"python3 x.py --sets-root ~/gov-os-eval --file fixtures/evaluation/zz-sg-new/hidden/q01.yaml"),
                            B_("python3 x.py --sets-root ~/gov-os-eval --notes fixtures/evaluation/zz-sg-new/XCHECK-r1.md"),
                            B_("python3 x.py --sets-root ~/gov-os-eval --classes runs/zz-sg-audit/miss-classes.json"),
                            B_("python3 x.py --sets-root ~/gov-os-eval --name 'miss-classes.json'"),
                            B_("python3 x.py --sets-root ~/gov-os-eval --misses runs/zz-sg-audit/misses.jsonl"),
                            B_("python3 x.py --sets-root ~/gov-os-eval --name 'misses.jsonl'")],
         "deny", "L", home=True)
    case("L1a", OL, "Bash", [B_(f"python3 x.py --sets-root {sr} --file zz-sg-new/hidden/q01.yaml"),
                             B_(f"python3 x.py --sets-root={sr} --notes zz-sg-new/XCHECK-r3.md"),
                             B_(f"python3 x.py --sets-root {sr} --classes runs/zz-sg-audit/miss-classes.json"),
                             B_(f"python3 x.py --sets-root {sr} --misses runs/audit-sg/misses.jsonl")],
         "deny", "L")
    # S: the launch script's own lines: only --sets-root <root>; allowed before and after
    case("S1", OL, "Bash", [B_(f"python3 {LX} --sets-root ~/gov-os-eval --kind writer --brief "
                               "governance/project/indep-briefs/writer.md --commit 6ff398a28 --set zz-sg-new"),
                            B_(f"python3 {LX} --sets-root ~/gov-os-eval --kind checker --set memory-verdict-4 --round 2 "
                               "--commit 6ff398a28"),
                            B_(f"python3 {LX} --sets-root ~/gov-os-eval --kind auditor --audit zz-sg-audit --set "
                               "memory-verdict-4 --commit 6ff398a28"),
                            B_(f"python3 {LX} --sets-root ~/gov-os-eval --counts-only --run 20261110T010203Z-writer-r1 "
                               "> /tmp/zz-sg-counts.json 2>&1")], "allow", "L", home=True)
    case("S1a", OL, "Bash", [B_(f"python3 {LX} --sets-root {sr} --kind writer --set zz-sg-new --round 2"),
                             B_(f"python3 {LX} --sets-root={sr} --kind auditor --audit audit-sg --dry")], "allow", "L")
    # O: nothing else changed
    case("O1", M, "Read", [R_(f"{NS}/visible/{NX}"), R_(f"{NS}/README.md"), R_(f"{NS}/XCHECK.md"),
                           R_(f"{NS}/hidden-notes.md"), R_(f"{NS}/XCHECK-r1.md.bak"), R_(f"{NS}/sub/XCHECK-r1.md"),
                           R_(f"{NA}/report.md"), R_(f"{NA}/classes.json"), R_(f"{NA}/sub/miss-classes.json"),
                           R_(f"{NA}/sub/misses.jsonl"), R_(f"{NA}/misses.jsonl.bak"), R_(f"{sr}/runs/misses.jsonl"),
                           R_(f"{sr}/runs/miss-classes.json"), R_(f"{E}/hidden/{NX}")], "allow", "L")
    case("O1t", M, "Read", [R_(f"{t}/fixtures/evaluation/memory-retrieval/visible/q03.yaml") for t in trees] +
         [R_(f"{t}/runs/zz-sg-audit/classes.json") for t in trees], "allow", "L")
    case("O2r", ERO, "Bash", [B_(f"cat {PS}/visible/q01.yaml"), B_(f"cat {PS}/XCHECK.md"), B_(f"cat {PS}/README.md"),
                              B_(f"cat {PA}/classes.json"), B_(f"ls {PS}/visible"), B_(f"ls {sr}/runs"),
                              B_(f"cat {sr}/runs/e0/counts.txt")], "allow", "R")
    case("O2g", ERO, "Grep", [{"pattern": "x", "path": f"{PS}/visible"}], "allow", "R")
    case("O2", OL, "Bash", [B_(f"cat {E}/zz-sg-new/visible/{NX}"), B_(f"cat {sr}/runs/zz-sg-audit/classes.json"),
                            B_(f"python3 x.py --sets-root {sr} --out runs/zz-sg-audit/report.md")], "allow", "L")
    case("O3", ERO, "Bash", [B_("ls fixtures/evaluation"), B_("grep -rln question fixtures/evaluation/memory-retrieval/visible"),
                             B_("git log --oneline -1 -- fixtures/evaluation")], "allow", "L", cwd=tree)
    case("O4", U, "Read", [R_(f"{NS}/hidden/{NX}"), R_(f"{NA}/miss-classes.json")], "allow", "L")
    case("O5", OL, "Bash", [B_("cat > /tmp/zz-sg-note.md <<'EOF'\nfixtures/evaluation/*/hidden/** and "
                               "runs/*/miss-classes.json, runs/*/misses.jsonl, XCHECK-r1.md\nEOF"),
                            B_("echo the hidden folder, XCHECK-r1.md, miss-classes.json and misses.jsonl"),
                            B_("grep -rn miss-classes docs/contract")], "allow", "L")
    return same_home


def main(tree, hook):
    same_home = cases(tree)

    def decide(role, tool, tin, agent=None, cwd=None):
        event = {"tool_name": tool, "tool_input": tin, "cwd": cwd or tree, "session_id": "sets-globs-check",
                 "agent_type": agent}
        role, _, ticket = role.partition("@")
        env = dict(os.environ, GOV_ROLE=role, GOV_TICKET=ticket or "W2-00", CLAUDE_PROJECT_DIR=tree)
        env.pop("PYTHONPATH", None)
        if not role:
            env.pop("GOV_ROLE")
        p = subprocess.run([PY, "-E", hook], input=json.dumps(event), capture_output=True, text=True, env=env,
                           timeout=60)
        if p.returncode == 2:
            return "deny(exit 2)", p.stderr
        if p.stdout.strip():
            out = json.loads(p.stdout)["hookSpecificOutput"]
            return out["permissionDecision"], out["permissionDecisionReason"]
        return "allow", p.stderr

    ok, fails, runs, skipped = True, 0, 0, {}
    for name, role, tool, tin, want, x in CASES:
        if x["tag"] == "R" and not PLANTED:
            skipped["R"] = skipped.get("R", 0) + 1
            continue
        if x.get("home") and not same_home:
            skipped["~ forms"] = skipped.get("~ forms", 0) + 1
            continue
        runs += 1
        got, why = decide(role, tool, tin, x.get("agent"), x.get("cwd"))
        good = got == want or (want == "deny" and got.startswith("deny"))
        ok &= good
        fails += not good
        print(("ok   " if good else "FAIL ") + f"[{x['tag']}] {name.splitlines()[0]}: want {want}, got {got}"
              + ("" if good else f" | {(why or '')[-200:]}"))
    print(f"cases: {len(CASES)}, run: {runs}, failed: {fails}, expect: {'before' if BEFORE else 'after'}, "
          "skipped: " + (", ".join(f"{k}: {v}" for k, v in skipped.items()) or "none"))
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    t = os.path.realpath(sys.argv[1])
    sys.exit(main(t, sys.argv[2] if len(sys.argv) > 2 else t + "/.claude/hooks/pretooluse.py"))
