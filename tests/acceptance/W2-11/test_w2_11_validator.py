"""W2-11, KPI 16 (failure line): the skill validator refuses a brief without the twelve-field rule.

The validator (``python3 -m gov.check.skill_validator <file>``) runs from the ``src/`` of the repository this file
sits in. Its code is outside this round's implementer's paths: the case may stay red until the orchestrator
decides (README, package P-W2-11-TD-2).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import w2_11_support as s

# The labels whose removal breaks the rule; every other word of the brief stays as it is.
LABELS = ("work_completed", "files_changed", "proposed_decisions", "recommended_next_action")


def _validate(file):
    env = dict(os.environ, PYTHONPATH=str(s.REPO_ROOT / "src"))
    done = subprocess.run([sys.executable, "-m", "gov.check.skill_validator", str(file)], cwd=str(s.REPO_ROOT),
                          env=env, capture_output=True, text=True, timeout=60)
    return done.returncode, done.stdout + done.stderr


def test_the_validator_accepts_the_brief_and_refuses_it_without_the_twelve_fields(tmp_path):
    text = s.read(f"{s.TEMPLATES}/brief-engineer.md")
    whole = tmp_path / "whole" / "brief-engineer.md"
    whole.parent.mkdir()
    whole.write_text(text, encoding="utf-8")
    code, output = _validate(whole)
    assert code == 0, f"the validator refuses the brief as it stands: {output[-400:]}"

    for label in LABELS:
        text = text.replace(label, "")
    broken = tmp_path / "broken" / "brief-engineer.md"
    broken.parent.mkdir()
    broken.write_text(text, encoding="utf-8")
    code, output = _validate(broken)
    assert code != 0, "the validator accepts a brief without the twelve-field rule"
    findings = json.loads(output.splitlines()[0]).get("findings", []) if output.startswith("{") else []
    assert any("twelve" in json.dumps(f).lower() or "return" in json.dumps(f).lower() for f in findings), (
        f"the refusal does not name the twelve-field rule: {output[-400:]}")
