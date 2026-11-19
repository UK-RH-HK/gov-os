"""W2-201 S7: the 5-minute prompt cache is kept for launched workers and checked.

A worker launch (W2-184's fixture project, the stand-in CLI) keeps ``CLAUDE_CODE_PROMPT_CACHE_TTL=5m`` in the env block
of its ``--settings`` and in the CLI process's environment (the stand-in records both), and its launch record holds
``cache_ttl`` ``5m``; no other cache variable is added: ``FORCE_PROMPT_CACHING_5M`` is in neither. One launch per
listed role; the QA engineer's is on this repository's own kernel role file, as S3 launches it. A lead started by the
launcher (``gov launch lead <ticket>``, admitted by the plan's ready list,
``governance/project/orchestration/ready.txt``) gets neither variable and writes no launch record. The environment
``gov launch`` is given is built from scratch, without either variable, so what the CLI holds is the launcher's.
"""

from __future__ import annotations

import pytest

import w2_201_support as k

s = k.s
VARIABLE, VALUE = "CLAUDE_CODE_PROMPT_CACHE_TTL", "5m"
DROPPED = "FORCE_PROMPT_CACHING_5M"
READY_REL = "governance/project/orchestration/ready.txt"
LEAD_TICKET = "DAEO-lead"
ROLES = (k.ENGINEER, k.TEST_DESIGNER, k.AUDITOR, k.QA, k.PRODUCT_SPEC, k.RESEARCH)


@pytest.mark.parametrize("role", ROLES)
def test_s7_a_worker_launch_sets_the_5_minute_cache_in_settings_environment_and_record(project, launch, role):
    if role == k.QA:
        k.plant_real_role(project, k.QA)
        tk = s.ticket(project, k.ENGINEER, "C2", tk="DAEO-qac2")
    else:
        tk = s.ticket(project, role, "C2")
    result = launch(role, tk)
    s.b.assert_launched(result)
    block, env = result.env_block(), result.session()["env"]
    assert block.get(VARIABLE) == VALUE, f"the --settings env block does not hold {VARIABLE}={VALUE}: {block}"
    assert env.get(VARIABLE) == VALUE, (
        f"the CLI process's environment does not hold {VARIABLE}={VALUE}: {env.get(VARIABLE)!r}")
    assert result.record().get("cache_ttl", s.MISSING) == "5m", (
        f"the launch record's cache_ttl is {result.record().get('cache_ttl', s.MISSING)!r}, not '5m'")
    assert DROPPED not in block, f"the --settings env block holds {DROPPED}: {block}"
    assert DROPPED not in env, f"the CLI process's environment holds {DROPPED}"


def test_s7_a_lead_started_by_the_launcher_does_not_get_the_5_minute_cache(sandbox, project, cli):
    s.ticket(project, k.ENGINEER, "C2", tk=LEAD_TICKET)
    # the ready list's line form: <W2> <ticket id> <brief> <log> (gov.launch.plan_check.ready_entries)
    s.b.write(project / READY_REL, f"# batch 1\nW2-201-lead {LEAD_TICKET} brief.md log.json\n")
    s.b.git(project, "add", "-A")
    s.b.git(project, "commit", "-q", "-m", "the lead's ticket and the ready list")
    result = s.cli_launch(sandbox, cli, "lead", LEAD_TICKET)
    s.b.assert_launched(result)
    settings = result.settings()
    for name in (VARIABLE, DROPPED):
        assert name not in (settings.get("env") or {}), f"the lead's --settings env block holds {name}: {settings}"
        assert name not in result.session()["env"], f"the lead's CLI process environment holds {name}"
    assert not result.new_records, f"the lead's launch wrote a launch record: {sorted(result.new_records)}"
