"""ACT-EXAMIN-SETS-1: the guard's cases for the two new evaluation sets. Runs a clone's PreToolUse hook (the pinned
interpreter, event JSON on stdin, as the earlier ACTs' seal_check.py did) with HOME set to a PLANTED home whose
gov-os-eval folder is a stand-in made in the rehearsal, so the real sets root is never named to the hook and never opened.

  python3 examin_check.py <clone> <planted home> [--expect before|after]

after (default): the two sets' hidden halves are refused to the engineer, the research role, the test designer, the
product-spec role, the auditor, the CTO and a lead, under the sets root and in a tree; the visible folder of a set under
the sets root, the proving ground's visible questions folder and the harness's own `--sets-root <root>` line stay
allowed. before: the same cases on the map without the entries give the same answers: sets_root_hidden's
`fixtures/evaluation/*/hidden/**` (ACT-SETS-GLOBS-1) already refuses any new set's hidden folder, under the root and in
every tree, to those roles. The entries are therefore declarative for the guard (they close no gap); they are what the
measure and `check_sets` read.
Prints one line per case and a last line PASS or FAIL; exit 0 or 1.
"""
import json
import os
import subprocess
import sys

CLONE = os.path.realpath(sys.argv[1])
HOME = os.path.realpath(sys.argv[2])
EXPECT = "before" if "--expect" in sys.argv and sys.argv[sys.argv.index("--expect") + 1] == "before" else "after"
HOOK = CLONE + "/.claude/hooks/pretooluse.py"
PY = open("/home/usain/.local/bin/gov").readline()[2:].strip()
SR = HOME + "/gov-os-eval"
E = SR + "/fixtures/evaluation"
SETS = ("examin", "adoption-proving-ground")

ROLES = [("engineer", "engineer"), ("research", "research"), ("product-spec", "product-spec"),
         ("test designer", "independent-test-designer"), ("auditor", "independent-auditor"),
         ("orchestrator (the CTO)", "orchestrator"), ("lead", "orchestrator@DAEO-0uhh")]
MEASURED = [r for r in ROLES if r[0] not in ("orchestrator (the CTO)", "lead")]
CTO = [r for r in ROLES if r[0] in ("orchestrator (the CTO)", "lead")]
CASES = []


def case(cid, roles, tool, tin, want, before=None):
    for label, role in roles:
        CASES.append((f"{cid} {label} {tool}: {tin.get('command') or tin.get('file_path') or tin.get('path')}", role,
                      tool, tin, (before or want) if EXPECT == "before" else want))


for s in SETS:
    h = f"{E}/{s}/hidden"
    # under the sets root: refused to every role before and after (sets_root_hidden's wildcard already covers a new set)
    case(f"S1[{s}]", ROLES, "Read", {"file_path": f"{h}/q01.yaml"}, "deny", before="deny")
    case(f"S2[{s}]", ROLES, "Read", {"file_path": f"{h}/visible/q01.yaml"}, "deny", before="deny")
    case(f"S3[{s}]", ROLES, "Grep", {"pattern": "x", "path": h}, "deny", before="deny")
    case(f"S4[{s}]", ROLES, "Glob", {"path": h, "pattern": "*.yaml"}, "deny", before="deny")
    case(f"S5[{s}]", ROLES, "Bash", {"command": f"cat {h}/q01.yaml"}, "deny", before="deny")
    case(f"S6[{s}]", ROLES, "Write", {"file_path": f"{h}/q99.yaml", "content": "x"}, "deny", before="deny")
    case(f"S7[{s}]", ROLES, "Read", {"file_path": f"{E}/{s}/XCHECK-r1.md"}, "deny", before="deny")
    # the visible folder and the other files of the set under the sets root stay open
    case(f"V1[{s}]", ROLES, "Read", {"file_path": f"{E}/{s}/visible/q01.yaml"}, "allow")
    # in a tree (this clone, or any worktree): sets_root_hidden's `fixtures/evaluation/*/hidden/**` applies in every tree to
    # every role it names (the six and the orchestrator), so the hidden glob is refused before the entries as well; the
    # entries add the declaration (the measure's, check_sets') and the roles-based refusal in role_reads, not a new denial
    case(f"T1[{s}]", ROLES, "Read", {"file_path": f"{CLONE}/fixtures/evaluation/{s}/hidden/q01.yaml"}, "deny",
         before="deny")
# the proving ground's visible half and a neighbour stay readable
case("P1", ROLES, "Read", {"file_path": f"{CLONE}/tests/acceptance/W2-81/questions/python-app.yaml"}, "allow")
# the harness's own line (only --sets-root <root>) stays allowed to the CTO and a lead
case("H1", CTO, "Bash", {"command": f"python3 .gov-runtime/scratch/orchestrator/tools/x.py --sets-root {SR}"}, "allow")
# a line that names the root with a set's hidden folder is refused to the CTO and a lead (the line rule)
case("H2", CTO, "Bash", {"command": f"python3 x.py --sets-root {SR} --out {E}/examin/hidden/z"}, "deny", before="deny")


def decide(role, tool, tin):
    event = {"tool_name": tool, "tool_input": tin, "cwd": CLONE, "session_id": "examin-check", "agent_type": None}
    role, _, ticket = role.partition("@")
    env = {k: os.environ[k] for k in ("PATH", "LANG") if k in os.environ}
    env.update(HOME=HOME, GOV_ROLE=role, GOV_TICKET=ticket or "DAEO-sdxk", CLAUDE_PROJECT_DIR=CLONE)
    p = subprocess.run([PY, "-E", HOOK], input=json.dumps(event), capture_output=True, text=True, env=env, timeout=60,
                       cwd=CLONE)
    if p.returncode == 2:
        return "deny", p.stderr
    if p.stdout.strip():
        out = json.loads(p.stdout)["hookSpecificOutput"]
        return out["permissionDecision"], out["permissionDecisionReason"]
    return "allow", p.stderr


def main():
    if not os.path.isdir(SR):
        print("the planted sets root does not exist: " + SR + "\nFAIL")
        return 1
    fails = 0
    for name, role, tool, tin, want in CASES:
        got, why = decide(role, tool, tin)
        good = got == want or (want == "deny" and got.startswith("deny"))
        fails += not good
        print(("ok   " if good else "FAIL ") + f"{name}: want {want}, got {got}" + ("" if good else f" | {why[-160:]}"))
    print(f"examin cases: {len(CASES)}, failed: {fails}, expect: {EXPECT}")
    print("PASS" if not fails else "FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
