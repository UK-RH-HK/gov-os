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


# --- DEC-444: automatic checkpoints to the scratch folder ---


def test_write_automatic_checkpoint_goes_to_scratch(project):
    """dest='automatic' writes under .gov-runtime/scratch/checkpoints/ (DEC-444)."""
    written = record.write(project, TICKET, "stop", "auto next", [], dest="automatic")
    assert written["path"].startswith(record.SCRATCH_CHECKPOINTS_REL)
    assert (project / written["path"]).is_file()
    assert not (project / record.CHECKPOINTS_REL / TICKET).exists()


def test_write_deliberate_is_the_default(project):
    """dest='deliberate' (the default) writes under docs/checkpoints/ (DEC-444)."""
    written = record.write(project, TICKET, "stop", "next", [])
    assert written["path"].startswith(record.CHECKPOINTS_REL)
    assert not (project / record.SCRATCH_CHECKPOINTS_REL / TICKET).exists()


def test_ids_unique_across_both_locations(project):
    """The next number considers checkpoints in both places (DEC-444)."""
    d = record.write(project, TICKET, "stop", "d1", [])
    a = record.write(project, TICKET, "stop", "a1", [], dest="automatic")
    assert d["id"] != a["id"]
    assert d["id"].endswith("-0001")
    assert a["id"].endswith("-0002")


def test_readers_pick_newer_automatic_over_older_deliberate(project):
    """The readers pick the newer checkpoint by created time (DEC-444)."""
    import time, yaml
    record.write(project, TICKET, "stop", "old deliberate", [])
    time.sleep(1.1)
    record.write(project, TICKET, "stop", "new automatic", [], dest="automatic")
    b = record.brief(project, TICKET)
    assert b["next_action"] == "new automatic"
    assert b["path"].startswith(record.SCRATCH_CHECKPOINTS_REL)


def test_readers_pick_newer_deliberate_over_older_automatic(project):
    """The readers pick the newer checkpoint by created time (DEC-444)."""
    import time
    record.write(project, TICKET, "stop", "old automatic", [], dest="automatic")
    time.sleep(1.1)
    record.write(project, TICKET, "stop", "new deliberate", [])
    b = record.brief(project, TICKET)
    assert b["next_action"] == "new deliberate"
    assert b["path"].startswith(record.CHECKPOINTS_REL)


def test_automatic_record_carries_head_commit(project):
    """Automatic records carry head_commit for the watchdog (DEC-444)."""
    import yaml
    written = record.write(project, TICKET, "stop", "auto", [], dest="automatic")
    text = (project / written["path"]).read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---", 2)[1])
    assert "head_commit" in front
    head = subprocess.run(["git", "-C", str(project), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    assert front["head_commit"] == head


def test_deliberate_record_has_no_head_commit(project):
    """Deliberate records do not carry head_commit (DEC-444)."""
    import yaml
    written = record.write(project, TICKET, "stop", "delib", [])
    text = (project / written["path"]).read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---", 2)[1])
    assert "head_commit" not in front


def test_watchdog_counts_commits_for_automatic_record(project):
    """An automatic record's commit distance uses head_commit, not assumed zero (DEC-444)."""
    record.write(project, TICKET, "stop", "auto", [], dest="automatic")
    (project / "extra.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(project), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(project), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                     "commit", "-q", "-m", "extra"], check=True, capture_output=True)
    result = record.watch(project, TICKET, 240, 99999, 0.30, None)
    assert result["commits"] >= 1


def test_briefs_includes_scratch_only_ticket(project):
    """briefs() lists tickets that have checkpoints only in the scratch folder (DEC-444)."""
    record.write(project, TICKET, "stop", "auto", [], dest="automatic")
    bs = record.briefs(project)
    assert any(b["ticket"] == TICKET for b in bs)
    assert any(b["path"].startswith(record.SCRATCH_CHECKPOINTS_REL) for b in bs)
