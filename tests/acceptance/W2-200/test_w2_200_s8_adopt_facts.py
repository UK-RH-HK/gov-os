"""S8: ``gov adopt --facts`` writes no context entry in the facts.

The facts file ``gov adopt --facts`` writes for a fixture folder (the kernel's templates and one READY ticket),
parsed. Then the commands it leaves unset are filled, as the project's CTO fills them, every other entry left as adopt
wrote it, and ``gov brief lead <ticket> --run build`` is asked for (the lead's brief needs its run kind).
"""

from __future__ import annotations

import json

import yaml

import w2_200_support as s


def _adopted(tmp_path, env):
    root = s.adopted_project(tmp_path, env)
    run = s.gov(["adopt", "--facts", "--root", root, "--json"], env=env, cwd=tmp_path)
    assert run.code == 0 and run.result().get("written") is True, run.describe()
    return root, (root / s.FACTS_REL).read_text(encoding="utf-8")


def test_s8_the_facts_file_holds_no_context_command_and_no_gov_context_text(tmp_path, env):
    _, text = _adopted(tmp_path, env)
    data = yaml.safe_load(text)
    commands = data.get("commands") or {}
    assert "context" not in commands, f"commands.context is written: {commands.get('context')!r}"
    assert "context_ceiling" not in commands, f"commands.context_ceiling is written: {commands.get('context_ceiling')!r}"
    lines = [line for line in text.splitlines() if "gov context" in line]
    assert not lines, f"the facts file names gov context: {lines}"


def test_s8_the_context_ceiling_step_stays_off_with_a_line_naming_no_command(tmp_path, env):
    _, text = _adopted(tmp_path, env)
    step = (yaml.safe_load(text).get("steps") or {}).get("context_ceiling")
    assert isinstance(step, dict), "the step context_ceiling is not kept (the lead templates still carry it)"
    assert step.get("on") is False, f"steps.context_ceiling.on is {step.get('on')!r}, not false"
    line = str(step.get("line", ""))
    assert line.strip(), "the step's line is empty"
    assert "{CMD:" not in line and "gov context" not in line, f"the step's line names a command: {line!r}"


def test_s8_gov_brief_lead_on_the_adopted_facts_leaves_no_placeholder(tmp_path, env):
    """Green on the base by design (a guard): the lead's brief, on the adopted facts with their unset commands
    filled, is built with no ``PLACEHOLDER_LEFT`` and names no ``gov context``."""
    root, _ = _adopted(tmp_path, env)
    s.fill_unset_commands(root)
    run = s.gov(["brief", "lead", s.BRIEF_TICKET, "--run", "build", "--root", root, "--json"], env=env, cwd=tmp_path)
    data = run.envelope()
    text = json.dumps(data)
    assert "PLACEHOLDER_LEFT" not in text and "PLACEHOLDER_LEFT" not in run.err, \
        f"the lead's brief leaves a placeholder\n{run.describe()}"
    assert run.code == 0 and data["ok"] is True, f"the lead's brief was refused\n{run.describe()}"
    assert "gov context" not in run.both, f"the lead's brief names gov context\n{run.describe()}"
