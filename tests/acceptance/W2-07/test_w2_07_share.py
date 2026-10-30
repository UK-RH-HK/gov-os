"""KPI 9: the close record carries the measured governance share [W2-M166, W2-M286] — of every close.

KPI 9: "The close record carries the measured governance share." The card's title: "a share for every close".
W1-30's round 13 already gives an implementation ticket's close record the share of the sessions the caller names
(``--ticket-session``, DEC-495, DEC-491; ``test_w1_30_r13_governance_share.py``). This case holds it for a close
this ticket newly makes possible: a research ticket closed by its class, with no acceptance tests.

No session log of this machine is read: the logs are W1-31's specimens, written into a temporary
``CLAUDE_CONFIG_DIR``; ``HOME`` is the sandbox's.
"""

import os
import sys
from pathlib import Path

import pytest

import w2_07_support as support

_W1_31 = str(Path(__file__).resolve().parents[1] / "W1-31")
if _W1_31 not in sys.path:
    sys.path.insert(0, _W1_31)

import w1_31_support as telemetry  # noqa: E402

TICKET, WBS = "PROJ-shar", "W9-shar"
RECORD_REL = "docs/research/W9/EXP-shar.md"
SHARE_KEY, SHARE_PARTS = "governance_share", ("measured", "estimated", "total")


@pytest.fixture()
def logs(tmp_path):
    if telemetry.ccusage_dir() is None:
        pytest.skip("ccusage is not installed on this machine: the counter cannot measure a session's tokens")
    folder = tmp_path / "claude-config"
    (folder / "projects").mkdir(parents=True)
    for log in telemetry.full_logs():
        log.write(folder)
    return folder


def test_a_close_by_class_carries_the_measured_governance_share(project, sandbox, interface, logs):
    support.create_ticket(project, TICKET, WBS, cls="research", allowed_paths=("docs/research/W9/**",), tests=False,
                          acceptance=support.judged_by_class("research", [RECORD_REL]))
    support.work(project, TICKET, {RECORD_REL: support.research_record("EXP-shar")}, role="research")
    support.checkpointed(project, TICKET)
    env = {**support.base.sandbox_env(sandbox), "CLAUDE_CONFIG_DIR": str(logs)}
    env["PATH"] = f"{telemetry.ccusage_dir()}{os.pathsep}{env['PATH']}"
    named = [argument for session in telemetry.ROLED for argument in ("--ticket-session", session)]

    run = support.run_close(project, sandbox, TICKET, *named, env=env)

    result = support.closed(run, interface)
    share = support.base.the_close_record(project, TICKET).get(SHARE_KEY)
    assert isinstance(share, dict) and sorted(share) == sorted(SHARE_PARTS), \
        f"the close record states no governance share: {share!r}\n{run.describe()}"
    assert telemetry.is_number(share["measured"]) and 0 < share["measured"] < 1, \
        f"the measured share is {share['measured']!r}, not a fraction the counter measured\n{run.describe()}"
    assert result.get(SHARE_KEY) == share, "the result and the close record state different shares"
