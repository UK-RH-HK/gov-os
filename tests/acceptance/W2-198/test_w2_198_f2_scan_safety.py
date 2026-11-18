"""F2: the scan never prints a question's text, and an unreadable transcript is never read as clean."""

from __future__ import annotations

import os

import pytest

import w2_198_support as s

SINCE, UNTIL, IN = "2026-11-10T00:00:00Z", "2026-11-12T00:00:00Z", "2026-11-11T20:00:00Z"
QUESTION = "Which zebra-violet clause governs the quorum of sevenfold lanterns?"
GOLD = "The Marigold Accord of 1987 sets nine lanterns at dusk."
Q01 = f"id: q01\nquestion: \"{QUESTION}\"\ngold: \"{GOLD}\"\n"


def _set(home):
    return s.make_set(home, texts={"q01": Q01})


def _scan(set_root, projects, env, cwd, *extra, json_form):
    args = ["memaudit", "scan", "--set", set_root, "--since", SINCE, "--until", UNTIL, "--projects", projects, *extra]
    return s.gov(args + (["--json"] if json_form else []), env=env, cwd=cwd)


@pytest.mark.parametrize("json_form", [False, True], ids=["text", "json"])
@pytest.mark.parametrize("finding", [True, False], ids=["finding", "no-finding"])
def test_f2_no_output_holds_a_line_of_a_set_file_but_its_id(tmp_path, home, env, json_form, finding):
    set_root = _set(home)
    projects = home / ".claude" / "projects"
    s.transcript(projects / "-p" / "sess-leak.jsonl", [
        s.say("2026-11-10T09:00:00Z", "sess-leak", f"q01 asks: {QUESTION} The answer: {GOLD}"),
    ], IN)
    extra = [] if finding else ["--id", "zz9"]
    run = _scan(set_root, projects, env, tmp_path, *extra, json_form=json_form)
    assert run.code == (1 if finding else 0), f"exit {run.code}: {run.both[-600:]}"
    if json_form:
        assert isinstance(run.envelope()["result"]["findings"], list)
    for text in (QUESTION, GOLD, "zebra-violet", "Marigold Accord", *Q01.splitlines()[1:]):
        assert text not in run.out and text not in run.err, f"the output holds {text!r}"


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads a mode 000 file")
@pytest.mark.parametrize("json_form", [False, True], ids=["text", "json"])
def test_f2_an_unreadable_transcript_and_no_finding_exits_3_naming_it(tmp_path, home, env, json_form):
    set_root = _set(home)
    projects = home / ".claude" / "projects"
    s.transcript(projects / "-p" / "sess-clean.jsonl", [s.say("2026-11-10T09:00:00Z", "sess-clean", "all fine")], IN)
    locked = s.transcript(projects / "-p" / "sess-locked.jsonl",
                          [s.say("2026-11-10T09:00:00Z", "sess-locked", "q01 here")], IN)
    locked.chmod(0)
    run = _scan(set_root, projects, env, tmp_path, json_form=json_form)
    assert run.code == 3, f"exit {run.code}, not 3: {run.both[-600:]}"
    if json_form:
        envelope = run.envelope()
        assert "SCAN_INCOMPLETE" in str(envelope)
        assert "sess-locked.jsonl" in str(envelope["result"]["problems"])
        assert envelope["result"]["findings"] == []
    else:
        assert "SCAN_INCOMPLETE" in run.both and "sess-locked.jsonl" in run.both, run.both[-600:]


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads a mode 000 file")
def test_f2_an_unreadable_transcript_beside_a_finding_is_named_in_problems(tmp_path, home, env):
    set_root = _set(home)
    projects = home / ".claude" / "projects"
    s.transcript(projects / "-p" / "sess-named.jsonl", [s.say("2026-11-10T09:00:00Z", "sess-named", "q03 here")], IN)
    locked = s.transcript(projects / "-p" / "sess-locked.jsonl",
                          [s.say("2026-11-10T09:00:00Z", "sess-locked", "nothing")], IN)
    locked.chmod(0)
    run = _scan(set_root, projects, env, tmp_path, json_form=True)
    assert run.code == 1, f"exit {run.code}, not 1: {run.both[-600:]}"
    result = run.envelope()["result"]
    assert [item["match"] for item in result["findings"]] == ["q03"]
    assert "sess-locked.jsonl" in str(result["problems"])
