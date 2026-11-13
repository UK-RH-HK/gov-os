"""S1 and S2: the skills check (``python3 -m gov.check.skill_validator --both-layouts <skill folder>``, its
required fields, its 2,500-token body budget and its known ``gov`` commands) finds nothing in either skill (README).

Run as a process from the repository's root, on the tree ``PYTHONPATH`` names (else the repository's own ``src``).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

import w2_142_support as support


@pytest.mark.parametrize("skill", ["retrieval", "discovery"])
def test_guard_the_skills_check_finds_nothing(skill):
    env = dict(os.environ)
    env["PYTHONPATH"] = env.get("PYTHONPATH") or str(support.REPO / "src")
    folder = f"template/governance/kernel/skills/{skill}"
    done = subprocess.run(
        [sys.executable, "-m", "gov.check.skill_validator", "--both-layouts", folder],
        cwd=support.REPO, env=env, capture_output=True, text=True, timeout=60, check=False)
    assert done.returncode == 0, f"the skills check on {folder}: exit {done.returncode}: {done.stdout}{done.stderr}"
    assert json.loads(done.stdout.strip().splitlines()[-1]) == {"findings": []}, done.stdout
