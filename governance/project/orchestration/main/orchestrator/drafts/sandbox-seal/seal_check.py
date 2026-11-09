"""ACT-SANDBOX-SEAL-1 (DEC-1099 (1) Q6): the seal's guard check cases. Runs the tested tree's hook under the pinned
judge's interpreter with event JSON, as guard4_check.py does, and checks that the sandbox experiment's sealed folder
(<sets root>/fixtures/evaluation/sandbox-guard-exp-1/hidden/) is refused to the tuner and every measured role, the CTO
and leads included, under the sets root and in every tree, while the harness's own lines (only --sets-root <root> on
them), the sessions no rule names, the open siblings and the tuning folder stay allowed.

  python3 seal_check.py [hook path]            a hook judged against the main tree
  python3 seal_check.py --settings <tree>      the tree's registered hook line, as Claude Code runs it

Environment: SEAL_EXPECT=before expects the answers before the patch (every case the seal adds is then an allow: the
gap the seal closes); SETS_PLANTED=1 runs the R cases (they need the planted files of the rehearsal); GOV_PIN_PY names
the judge's interpreter; SEAL_TREE names a second tree of the repository (a worktree) for the every-tree case. A case
naming ~ or $HOME runs only when the block's root is ~/gov-os-eval as this HOME expands it. Prints one line per case
and a last line PASS or FAIL. It reads no file under the sets root; R cases only name planted files to the hook.
"""
import json
import os
import subprocess
import sys

import yaml

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS"
HOOK = ROOT + "/.claude/hooks/pretooluse.py"
LINE, PROJECT = None, ROOT
if len(sys.argv) > 2 and sys.argv[1] == "--settings":
    PROJECT = sys.argv[2]
    LINE = json.load(open(PROJECT + "/.claude/settings.json"))["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    ROOT = PROJECT
elif len(sys.argv) > 1:
    HOOK = sys.argv[1]
PY = os.environ.get("GOV_PIN_PY") or open(os.path.expanduser("~/.local/bin/gov")).readline()[2:].strip()
BEFORE = os.environ.get("SEAL_EXPECT") == "before"
PLANTED = os.environ.get("SETS_PLANTED") == "1"
BLOCK = yaml.safe_load(open(PROJECT + "/governance/project/path-map.yaml")).get("sets_root_hidden") or {}
SR = os.path.realpath(os.path.expanduser(BLOCK.get("root", "~/gov-os-eval")))
SAME_HOME = SR == os.path.realpath(os.path.expanduser("~/gov-os-eval"))
E = SR + "/fixtures/evaluation"
SET = "sandbox-guard-exp-1"
X = f"{E}/{SET}/hidden"
NX = "zz-seal-none.jsonl"
NXD = "zz-seal-none.d"
HOME_NOW = os.path.realpath(os.path.expanduser("~"))
TREE2 = os.environ.get("SEAL_TREE") or ""
HX = ".gov-runtime/scratch/orchestrator/drafts/sandbox-exp"  # the harness, named only (need not exist)
TUNING = "/home/usain/gov-os-runs/SANDBOX-GUARD-EXP-1/tuning"

M = [("engineer", "engineer", None), ("research", "research", None), ("orchestrator (the CTO)", "orchestrator", None),
     ("lead", "orchestrator@DAEO-0uhh", None), ("product-spec", "product-spec", None),
     ("test designer", "independent-test-designer", None), ("auditor", "independent-auditor", None),
     ("CTO's engineer subagent", "orchestrator", "engineer"),
     ("CTO's general-purpose subagent", "orchestrator", "general-purpose"),
     ("the tuner (engineer on W2-56)", "engineer@DAEO-wnnz", None)]
U = [("no GOV_ROLE", "", None), ("ticket-lead", "ticket-lead", None)]
ERO = [r for r in M if r[0] in ("engineer", "research", "orchestrator (the CTO)", "the tuner (engineer on W2-56)")]
EO = [r for r in M if r[0] in ("engineer", "orchestrator (the CTO)")]
O = [r for r in M if r[0] == "orchestrator (the CTO)"]
OL = [r for r in M if r[0] in ("orchestrator (the CTO)", "lead")]
ENG = [r for r in M if r[0] in ("engineer", "the tuner (engineer on W2-56)")]
CASES = []


def case(cid, roles, tool, tins, want, tag, before=None, **extra):
    """want: the answer after the patch; before: the answer before it (default: allow if the seal adds a deny)."""
    b = before or ("allow" if want == "deny" else want)
    for label, role, agent in roles:
        for tin in tins:
            form = tin.get("command") or tin.get("file_path") or f"{tin.get('path')} {tin.get('pattern', '')}"
            CASES.append((f"seal {cid} {label} {tool}: {form}", role, tool, tin, b if BEFORE else want,
                          dict(extra, tag=tag, agent=agent)))


def R_(p):
    return {"file_path": p}


def B_(c):
    return {"command": c}


# The sealed folder under the sets root: refused to every measured role, the CTO, leads and the tuner
case("K1", M, "Read", [R_(f"{X}/{NX}"), R_(f"{X}/corpus/{NX}")], "deny", "L")
case("K2", M, "Read", [R_(f"{X}/corpus/actions.jsonl"), R_(f"{X}/planted/cases.jsonl"),
                       R_(f"{X}/labels/labels.jsonl")], "deny", "R")
case("K3", ERO, "Bash", [B_(f"cat {X}/{NX}"), B_(f"ls {X}/{NXD}")], "deny", "L")
case("K4", ERO, "Bash", [B_(f"head -3 {X}/corpus/actions.jsonl"), B_(f"ls {X}"), B_(f"wc -l {X}/planted/cases.jsonl"),
                         B_(f"grep -rn x {E}/{SET}"), B_(f"python3 -c \"print(open('{X}/labels/labels.jsonl').read())\"")],
     "deny", "R")
case("K5", ERO, "Grep", [{"pattern": "x", "path": f"{X}/{NXD}"}], "deny", "L")
case("K6", ERO, "Grep", [{"pattern": "x", "path": X}, {"pattern": "x", "path": f"{E}/{SET}"}], "deny", "R")
case("K7", ERO, "Glob", [{"path": f"{E}/{SET}", "pattern": "hidden/*"}, {"path": f"{X}/{NXD}", "pattern": "*"}],
     "deny", "L")
# writes into it (those the guard resolves)
case("K8", [r for r in M if r[0] != "auditor"], "Write", [{"file_path": f"{X}/{NX}", "content": "x"}], "deny", "L")
# the auditor's write there is refused by rule 5 before the seal too (it writes only its records, scratch or /tmp)
case("K8a", [r for r in M if r[0] == "auditor"], "Write", [{"file_path": f"{X}/{NX}", "content": "x"}], "deny", "L",
     before="deny")
case("K9", ENG, "Bash", [B_(f"echo x > {X}/{NX}")], "deny", "L")
case("K10", O, "Bash", [B_(f"cp /tmp/zz-seal-a {X}/{NX}"), B_(f"mkdir -p {X}/{NXD} && : > {X}/{NXD}/.n")], "deny", "L")
# in every tree (the glob holds in this tree, a worktree and run clones), for the measured roles and the CTO
case("K11", EO + ENG[1:], "Read", [R_(f"{ROOT}/fixtures/evaluation/{SET}/hidden/{NX}")], "deny", "L")
if TREE2:
    case("K12", EO, "Read", [R_(f"{TREE2}/fixtures/evaluation/{SET}/hidden/{NX}")], "deny", "L")
# the line rule (DEC-1097 (2)): the root named with the sealed folder, in every spelling, refused to the CTO and leads
case("K13", OL, "Bash", [B_(f"python3 {HX}/setup_a.py --sets-root ~/gov-os-eval --out "
                            f"~/gov-os-eval/fixtures/evaluation/{SET}/hidden/{NXD}"),
                         B_(f"cat ~/gov-os-eval/fixtures/evaluation/{SET}/hidden/{NX}"),
                         B_(f'ls "$HOME/gov-os-eval/fixtures/evaluation/{SET}/hidden/{NXD}"')], "deny", "L", home=True)
case("K14", OL, "Bash", [B_(f"python3 {HX}/score.py --sets-root {SR} --labels {X}/labels/{NX}"),
                         B_(f"cat {X}/{NX}")], "deny", "L")
# the root in a variable or with a cd: refused before the seal too (the line rule as it is)
case("K15", EO, "Bash", [B_(f"D={SR}; cat $D/fixtures/evaluation/{SET}/hidden/{NX}"),
                         B_(f"cd {SR} && cat fixtures/evaluation/{SET}/hidden/{NX}")], "deny", "L", before="deny")
# the harness's own lines: only --sets-root <root> (a set name bare, variables only before it), allowed to the CTO and a
# lead, before and after
case("K16", OL, "Bash", [B_(f"python3 {HX}/extract_corpus.py --sets-root ~/gov-os-eval --dry"),
                         B_(f"python3 {HX}/extract_corpus.py --sets-root ~/gov-os-eval > /tmp/zz-seal-x.txt 2>&1"),
                         B_(f"PY=~/.local/share/gov-os/pin-bcea09060ebc/bin/python; $PY {HX}/score.py --sets-root "
                            "~/gov-os-eval --half held-out --counts-only"),
                         B_(f"python3 {HX}/setup_a.py --set {SET} --sets-root ~/gov-os-eval --half held-out --once")],
     "allow", "L", home=True)
case("K17", OL, "Bash", [B_(f"python3 {HX}/extract_corpus.py --sets-root {SR}"),
                         B_(f"python3 {HX}/control_run.py --sets-root={SR} --half held-out")], "allow", "L")
# the sessions no rule names (the operator's outside sessions run outside the guard altogether)
case("K18", U, "Read", [R_(f"{X}/{NX}")], "allow", "L")
case("K19", U, "Read", [R_(f"{X}/corpus/actions.jsonl")], "allow", "R")
# open: a sibling of the sealed folder, a names-only listing of its parent, the tuning folder
case("K20", M, "Read", [R_(f"{E}/{SET}/{NX}"), R_(f"{TUNING}/{NX}")], "allow", "L")
case("K21", ERO, "Bash", [B_(f"ls {E}/{SET}"), B_(f"cat {E}/{SET}/README.txt")], "allow", "R")
case("K22", ENG, "Bash", [B_(f"cat {TUNING}/{NX}"), B_(f"ls {TUNING}")], "allow", "L")


def decide(role, tool, tin, agent=None):
    event = {"tool_name": tool, "tool_input": tin, "cwd": ROOT, "session_id": "seal-check", "agent_type": agent}
    role, _, ticket = role.partition("@")
    env = dict(os.environ, GOV_ROLE=role, GOV_TICKET=ticket or "DAEO-sdxk", CLAUDE_PROJECT_DIR=ROOT)
    env.pop("PYTHONPATH", None)
    if not role:
        env.pop("GOV_ROLE")
    if LINE:
        p = subprocess.run(["sh", "-c", LINE], input=json.dumps(event), capture_output=True, text=True, env=env,
                           timeout=60)
    else:
        p = subprocess.run([PY, "-E", HOOK], input=json.dumps(event), capture_output=True, text=True, env=env,
                           timeout=60)
    if p.returncode == 2:
        return "deny(exit 2)", p.stderr
    if p.stdout.strip():
        out = json.loads(p.stdout)["hookSpecificOutput"]
        return out["permissionDecision"], out["permissionDecisionReason"]
    return "allow", p.stderr


def main():
    if not BLOCK:
        print("no sets_root_hidden block in the tested tree's map\nFAIL")
        return 1
    ok, fails, runs, skipped = True, 0, 0, {}
    for name, role, tool, tin, want, x in CASES:
        if x["tag"] == "R" and not PLANTED:
            skipped["R (SETS_PLANTED unset)"] = skipped.get("R (SETS_PLANTED unset)", 0) + 1
            continue
        if x.get("home") and not SAME_HOME:
            skipped["names ~ or $HOME, root not ~/gov-os-eval"] = skipped.get(
                "names ~ or $HOME, root not ~/gov-os-eval", 0) + 1
            continue
        runs += 1
        got, why = decide(role, tool, tin, x.get("agent"))
        good = got == want or (want == "deny" and got.startswith("deny"))
        ok &= good
        fails += not good
        print(("ok   " if good else "FAIL ") + f"[{x['tag']}] {name}: want {want}, got {got}"
              + ("" if good else f" | {why[-200:]}"))
    print(f"seal cases: {len(CASES)}, run: {runs}, failed: {fails}, expect: {'before' if BEFORE else 'after'}, skipped: "
          + (", ".join(f"{k}: {v}" for k, v in skipped.items()) or "none"))
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
