"""Builder tests for ``gov checkpoint`` (W1-25). Regression evidence only (DEC-136)."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.checkpoint import command, record  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402

TICKET = "DAEO-zq31"


@pytest.fixture()
def project(tmp_path):
    (tmp_path / ".tickets").mkdir()
    (tmp_path / ".tickets" / f"{TICKET}.md").write_text(f"---\nid: {TICKET}\nstatus: in_progress\n---\n# t\n",
                                                        encoding="utf-8")
    for args in (("init", "-q"), ("add", "-A"),
                 ("-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-m", "fixture")):
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True)
    return tmp_path


def test_the_watchdog_defaults_are_those_of_dec_321():
    """4 hours, 20 commits on the branch, 30 % of the context window; context is not judged unless given."""
    parser = argparse.ArgumentParser()
    command.add_arguments(parser)
    args = parser.parse_args(["--watch"])
    assert (args.max_age_minutes, args.max_commits, args.max_context) == (240, 20, 0.30)
    assert args.context_utilisation is None
    assert command.EXIT_CODES == {3: command.EXIT_CODES[3]}


def test_the_latest_checkpoint_is_the_highest_number_not_the_last_name(project):
    for number in range(1, 11):
        written = record.write(project, TICKET, "stop", f"step {number}", [])
    assert written["id"] == f"CP-{TICKET}-0010"
    assert record.brief(project, TICKET)["next_action"] == "step 10"
    assert record.watch(project, TICKET, 240, 20, 0.30, None)["stale"] is False


def test_an_input_outside_the_project_is_refused_and_nothing_is_written(project, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside") / "note.md"
    outside.write_text("x", encoding="utf-8")
    with pytest.raises(GovError):
        record.write(project, TICKET, "stop", "next", [str(outside)])
    assert not (project / record.CHECKPOINTS_REL).exists()


def test_a_checkpoint_without_the_recorded_ticket_status_is_stale(project):
    """The watchdog does not pass a transition it cannot judge."""
    path = project / record.write(project, TICKET, "stop", "next", [])["path"]
    path.write_text(path.read_text(encoding="utf-8").replace("task_status: in_progress\n", ""), encoding="utf-8")
    with pytest.raises(GovError) as raised:
        record.watch(project, TICKET, 240, 20, 0.30, None)
    assert raised.value.exit_code == 3 and raised.value.details["reasons"] == ["ticket-transition"]
