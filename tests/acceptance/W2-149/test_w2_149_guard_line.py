"""S19: the CTO's documented lines pass the guard; the same line naming a folder under the sets root does not.

The tree's own ``.claude/hooks/pretooluse.py`` is driven as walls_check.py's ``repo`` mode drives it (W5/W6): a Bash
event for the orchestrator (``GOV_ROLE=orchestrator``, the CTO's ticket W2-00), with a planted HOME whose
``~/gov-os-eval`` holds a planted ``indep-walls/APPROVED``. The hook reads the sets root block from the main tree's
path map, whose root ``~/gov-os-eval`` this HOME expands to the planted root. The hook cases are green guards today
(the lines are the README's); the script's own code 17 is red until the script exists.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

import w2_149_support as support

X = "python3 governance/project/orchestration/tools/indep_launch.py"
H = "5d41402abc4b2a76b9719d911017c5925d41402abc4b2a76b9719d911017c592"
C = "6ff398a28"
LINES = {
    "writer": f"{X} --sets-root ~/gov-os-eval --kind writer --brief governance/project/indep-briefs/writer.md "
              f"--brief-sha256 {H} --commit {C} --set memory-verdict-3",
    "checker": f"{X} --sets-root ~/gov-os-eval --kind checker --brief governance/project/indep-briefs/checker.md "
               f"--brief-sha256 {H} --commit {C} --set memory-verdict-3 --round 1",
    "auditor": f"{X} --sets-root ~/gov-os-eval --kind auditor --brief governance/project/indep-briefs/auditor.md "
               f"--brief-sha256 {H} --commit {C} --set memory-verdict-3 --audit audit-2026-11",
    "labeller": f"{X} --sets-root ~/gov-os-eval --kind labeller --brief governance/project/indep-briefs/labeller.md "
                f"--brief-sha256 {H} --commit {C} --set sandbox-guard-exp-1 --round 2",
    "dry": f"{X} --sets-root ~/gov-os-eval --kind writer --brief governance/project/indep-briefs/writer.md "
           f"--brief-sha256 {H} --commit {C} --set memory-verdict-3 --seed 12345 --dry",
    "counts-only": f"{X} --sets-root ~/gov-os-eval --kind labeller --run 20261109T190000Z-sandbox-guard-exp-1-r2 "
                   "--counts-only",
}
REFUSED = {
    "brief-in-a-wall": LINES["writer"].replace("governance/project/indep-briefs/writer.md",
                                               "~/gov-os-eval/indep-walls/writer/brief.md"),
    "root-into-the-walls": LINES["checker"].replace("--sets-root ~/gov-os-eval", "--sets-root ~/gov-os-eval/indep-walls"),
    "absolute-approved": LINES["dry"] + " --brief @HOME@/gov-os-eval/indep-walls/APPROVED",
}


def decide(world, command):
    hook = support.TREE / ".claude/hooks/pretooluse.py"
    event = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(support.TREE),
             "session_id": "w2-149-guard", "agent_type": None}
    env = {"HOME": str(world.home), "PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "GOV_ROLE": "orchestrator",
           "GOV_TICKET": "W2-00", "CLAUDE_PROJECT_DIR": str(support.TREE), "PYTHONPATH": str(support.TREE / "src"),
           "GOV_GUARD_CALLS_DIR": str(world.tmp / "guard-calls")}
    p = subprocess.run([sys.executable, str(hook)], input=json.dumps(event), capture_output=True, text=True,
                       env=env, cwd=str(support.TREE), timeout=60)
    if p.returncode == 2:
        return "deny", p.stderr
    if p.stdout.strip():
        out = json.loads(p.stdout)["hookSpecificOutput"]
        return out["permissionDecision"], out.get("permissionDecisionReason", "")
    assert p.returncode == 0, p.stderr
    return "allow", ""


@pytest.mark.parametrize("name", sorted(LINES))
def test_s19_each_documented_line_is_allowed_to_the_orchestrator(world, name):
    assert (world.home / "gov-os-eval/indep-walls/APPROVED").is_file()
    got, why = decide(world, LINES[name])
    assert got == "allow", why


@pytest.mark.parametrize("name", sorted(REFUSED))
def test_s19_the_same_line_naming_a_folder_under_the_sets_root_is_refused(world, name):
    got, why = decide(world, REFUSED[name].replace("@HOME@", str(world.home)))
    assert got == "deny", f"allowed: {REFUSED[name]}"


@pytest.mark.parametrize("how", ["brief-in-a-wall", "root-into-the-walls"])
def test_s19_the_script_refuses_an_argument_naming_a_folder_under_the_sets_root_17(world, how):
    args = world.args("writer", dry=True)
    if how == "brief-in-a-wall":
        args[args.index("--brief") + 1] = str(world.walls / "writer/brief.md")
    else:
        args[args.index("--sets-root") + 1] = str(world.walls)
    before = world.built_state("writer")
    run = world.launch(*args)
    assert run.code == 17, run.why()
    assert run.line and run.line["status"] == "refused" and run.line["reason"] == "argument"
    assert run.line["code"] == 17
    assert world.built_state("writer") == before, "something was built"
    assert world.calls() == []
