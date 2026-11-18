"""W2-201 S7: the 5-minute prompt cache is kept for launched workers and checked.

A worker launch (W2-184's fixture project, the stand-in CLI) puts ``FORCE_PROMPT_CACHING_5M=1`` in the env block of its
``--settings`` and in the CLI process's environment (the stand-in records both), and its launch record holds
``cache_ttl`` ``5m``. A lead started by the launcher (``gov launch lead <ticket>``, admitted by the plan's ready list,
``governance/project/orchestration/ready.txt``) does not get the variable; a lead writes no launch record, so no record
of it can carry ``cache_ttl`` ``5m``. The environment ``gov launch`` is given is built from scratch, without the
variable, so what the CLI holds is the launcher's.
"""

from __future__ import annotations

import pytest

import w2_201_support as k

s = k.s
VARIABLE = "FORCE_PROMPT_CACHING_5M"
READY_REL = "governance/project/orchestration/ready.txt"
LEAD_TICKET = "DAEO-lead"


@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_s7_a_worker_launch_sets_the_5_minute_cache_in_settings_environment_and_record(project, launch, role):
    tk = s.ticket(project, role, "C2")
    result = launch(role, tk)
    s.b.assert_launched(result)
    assert result.env_block().get(VARIABLE) == "1", (
        f"the --settings env block does not hold {VARIABLE}=1: {result.env_block()}")
    assert result.session()["env"].get(VARIABLE) == "1", (
        f"the CLI process's environment does not hold {VARIABLE}=1")
    assert result.record().get("cache_ttl", s.MISSING) == "5m", (
        f"the launch record's cache_ttl is {result.record().get('cache_ttl', s.MISSING)!r}, not '5m'")


def test_s7_a_lead_started_by_the_launcher_does_not_get_the_5_minute_cache(sandbox, project, cli):
    """Guard on the base (nothing sets the variable there); it holds the lead's side of the line once workers get it."""
    s.ticket(project, k.ENGINEER, "C2", tk=LEAD_TICKET)
    # the ready list's line form: <W2> <ticket id> <brief> <log> (gov.launch.plan_check.ready_entries)
    s.b.write(project / READY_REL, f"# batch 1\nW2-201-lead {LEAD_TICKET} brief.md log.json\n")
    s.b.git(project, "add", "-A")
    s.b.git(project, "commit", "-q", "-m", "the lead's ticket and the ready list")
    result = s.cli_launch(sandbox, cli, "lead", LEAD_TICKET)
    s.b.assert_launched(result)
    settings = result.settings()
    assert VARIABLE not in (settings.get("env") or {}), f"the lead's --settings env block holds {VARIABLE}: {settings}"
    assert VARIABLE not in result.session()["env"], f"the lead's CLI process environment holds {VARIABLE}"
    carried = [name for name, text in result.new_records.items() if '"cache_ttl": "5m"' in text.replace("  ", " ")]
    assert not carried, f"a launch record of the lead's launch carries cache_ttl 5m: {carried}"
