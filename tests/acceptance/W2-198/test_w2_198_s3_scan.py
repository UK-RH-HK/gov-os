"""S3: `gov memaudit scan` reports every transcript written in the window that names the set's path or a question id."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import pytest

import w2_198_support as s

SINCE, UNTIL = "2026-11-10T00:00:00Z", "2026-11-12T00:00:00Z"
IN = "2026-11-11T20:00:00Z"  # an mtime in the window


def _world(tmp_path, home):
    """The planted projects root. Returns (projects, set_root, the expected findings as keys)."""
    set_root = s.make_set(home)
    forms = s.path_forms(home, set_root)
    projects = home / ".claude" / "projects"
    proj = projects / "-home-fixture-work-proj"
    main = s.transcript(proj / "sess-main.jsonl", [
        s.user("2026-11-10T09:00:00Z", "sess-main", "start the audit of the retrieval code"),
        s.bash("2026-11-10T09:01:00Z", "sess-main", f"ls {forms['abs']}/hidden"),
        s.bash("2026-11-10T09:02:00Z", "sess-main", f"du -sh {forms['tilde']}"),
        s.user("2026-11-10T09:03:00Z", "sess-main", f"look in {forms['dollar']} later"),
        s.say("2026-11-10T09:04:00Z", "sess-main", f"the set lives under {forms['segment']} in the eval root"),
        s.say("2026-11-10T09:05:00Z", "sess-main", "Notes so far:\nq02 looks like the hardest one"),
        s.say("2026-11-10T09:06:00Z", "sess-main", "compare q020 with xq02 in the old run"),
        '{"type": "assistant", "sessionId": "sess-main", "message": {"content": "partial write of q01 an',
    ], IN)
    agent = s.transcript(proj / "sess-main" / "subagents" / "agent-a1b2.jsonl", [
        s.user("2026-11-10T10:00:00Z", "sess-main", "audit the change"),
        s.bash("2026-11-10T10:01:00Z", "sess-main", "grep -n q03 notes.md"),
    ], IN)
    s.write(proj / "sess-main" / "subagents" / "agent-a1b2.meta.json", '{"agentType": "independent-auditor"}\n')
    expected = {
        (str(main.resolve()), "sess-main", 2, None, "path", forms["abs"]),
        (str(main.resolve()), "sess-main", 3, None, "path", forms["tilde"]),
        (str(main.resolve()), "sess-main", 4, None, "path", forms["dollar"]),
        (str(main.resolve()), "sess-main", 5, None, "path", forms["segment"]),
        (str(main.resolve()), "sess-main", 6, None, "id", "q02"),
        (str(main.resolve()), "sess-main", 8, None, "id", "q01"),
        (str(agent.resolve()), "sess-main", 2, "independent-auditor", "id", "q03"),
    }
    _negatives(proj, forms)
    return projects, set_root, expected


def _negatives(proj, forms):
    """Names outside the window, in a file older than --since, and in the allowed session: no finding."""
    s.transcript(proj / "sess-long.jsonl", [
        s.say("2026-11-09T23:00:00Z", "sess-long", f"q02 is in {forms['abs']}"),
        s.say("2026-11-10T10:00:00Z", "sess-long", "nothing to see"),
        s.say("2026-11-12T01:00:00Z", "sess-long", f"q01 is in {forms['tilde']}"),
    ], "2026-11-12T01:00:00Z")
    s.transcript(proj / "sess-old.jsonl", [
        {"type": "summary", "summary": f"q02 and {forms['segment']}", "leafUuid": "00000000-0000-4000-8000-0000000000aa"},
    ], "2026-11-09T12:00:00Z")
    s.transcript(proj / "sess-writer.jsonl", [
        s.bash("2026-11-10T11:00:00Z", "sess-writer", f"cat {forms['abs']}/hidden/q01.yaml"),
    ], IN)


def _scan(set_root, projects, env, cwd, *extra, json_form=True):
    args = ["memaudit", "scan", "--set", set_root, "--since", SINCE, "--until", UNTIL, "--projects", projects, *extra]
    if json_form:
        args.append("--json")
    return s.gov(args, env=env, cwd=cwd)


def test_s3_each_naming_line_in_the_window_is_one_finding_with_its_fields(tmp_path, home, env):
    projects, set_root, expected = _world(tmp_path, home)
    run = _scan(set_root, projects, env, tmp_path, "--allow-session", "sess-writer")
    assert run.code == 1, f"exit {run.code}, not 1: {run.both[-600:]}"
    result = run.envelope()["result"]
    found = [s.finding_key(item, projects) for item in result["findings"]]
    assert len(found) == len(set(found)), f"a finding is reported twice: {found}"
    assert set(found) == expected, (f"missing {sorted(expected - set(found), key=str)}; "
                                    f"extra {sorted(set(found) - expected, key=str)}")
    assert "sess-writer" in str(result["allowed"])


def test_s3_text_form_says_the_measure_is_void_then_one_line_a_finding(tmp_path, home, env):
    projects, set_root, expected = _world(tmp_path, home)
    run = _scan(set_root, projects, env, tmp_path, "--allow-session", "sess-writer", json_form=False)
    assert run.code == 1, f"exit {run.code}, not 1: {run.both[-600:]}"
    lines = run.text_lines()
    if lines and "void" not in lines[0].lower():  # the void line on stderr, the findings on stdout
        lines = [line for line in run.err.splitlines() if "void" in line.lower()][:1] + lines
    assert lines and "void" in lines[0].lower(), f"the first line does not say the measure is void: {lines}"
    others = lines[1:]
    assert len(others) == len(expected), f"{len(others)} finding lines for {len(expected)} findings: {others}"
    for name in ("sess-main.jsonl", "agent-a1b2.jsonl"):
        assert any(name in line for line in others), f"no finding line names {name}"


def test_s3_names_outside_the_window_in_longer_tokens_or_allowed_give_none(tmp_path, home, env):
    set_root = s.make_set(home)
    forms = s.path_forms(home, set_root)
    projects = home / ".claude" / "projects"
    proj = projects / "-home-fixture-work-proj"
    _negatives(proj, forms)
    s.transcript(proj / "sess-tokens.jsonl", [
        s.say("2026-11-10T09:06:00Z", "sess-tokens", "compare q020 with xq02 and aq01 in the old run"),
    ], IN)
    run = _scan(set_root, projects, env, tmp_path, "--allow-session", "sess-writer")
    assert run.code == 0, f"exit {run.code}, not 0: {run.both[-600:]}"
    result = run.envelope()["result"]
    assert result["findings"] == []
    assert "sess-writer" in str(result["allowed"])
    text = _scan(set_root, projects, env, tmp_path, "--allow-session", "sess-writer", json_form=False)
    assert text.code == 0 and len(text.out.strip().splitlines()) == 1, text.both[-600:]
    unallowed = _scan(set_root, projects, env, tmp_path)
    assert unallowed.code == 1, "without --allow-session the writer's line should void the measure"
    sessions = {item["session"] for item in unallowed.envelope()["result"]["findings"]}
    assert sessions == {"sess-writer"}


def test_s3_id_option_replaces_the_sets_ids_and_until_defaults_to_now(tmp_path, home, env):
    set_root = s.make_set(home)
    projects = home / ".claude" / "projects"
    proj = projects / "-home-fixture-work-proj"
    now = datetime.now(timezone.utc).replace(microsecond=0)
    stamp = lambda days: (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: E731
    path = s.transcript(proj / "sess-ids.jsonl", [
        s.say(stamp(3), "sess-ids", "q02 again"),
        s.say(stamp(1), "sess-ids", "now h7 instead"),
    ], stamp(1))
    args = ["memaudit", "scan", "--set", set_root, "--since", stamp(4), "--projects", projects, "--id", "h7", "--json"]
    run = s.gov(args, env=env, cwd=tmp_path)
    assert run.code == 1, f"exit {run.code}, not 1: {run.both[-600:]}"
    found = {s.finding_key(item, projects) for item in run.envelope()["result"]["findings"]}
    assert found == {(str(path.resolve()), "sess-ids", 2, None, "id", "h7")}


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads a mode 000 file")
def test_s3_question_ids_come_from_file_names_without_opening_the_files(tmp_path, home, env):
    set_root = s.make_set(home)
    for item in (set_root / "hidden").iterdir():
        item.chmod(0)
    projects = home / ".claude" / "projects"
    path = s.transcript(projects / "-p" / "sess-ids.jsonl", [s.say("2026-11-10T09:00:00Z", "sess-ids", "q02 again")],
                        IN)
    run = _scan(set_root, projects, env, tmp_path)
    assert run.code == 1, f"exit {run.code}, not 1: {run.both[-600:]}"
    found = {s.finding_key(item, projects) for item in run.envelope()["result"]["findings"]}
    assert found == {(str(path.resolve()), "sess-ids", 1, None, "id", "q02")}
