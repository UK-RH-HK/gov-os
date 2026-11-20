"""S13 to S16, the fix under W2-204 for EXAMIN's F-033: what counts as having read the set in `gov memaudit scan`.

S13 (M1) a bare question id is no evidence; an id counts only on a line that also names the set by its audit name or
its tag, each a whole token. S14 (M2) a question's text read is evidence (kind `text`, `match` the question's id), by
its key (the first 48 characters of the normalised `question` field; none under 24). S15 (M3) every path form counts
as before and nothing printed holds a question's or an answer's text. S16 (M4) EXAMIN's case: a dummy set of 40 empty
files, a busy window and one typed path. The scan still reads every transcript of the window (EMERGENCY-2 2.7, A-12).

Every case runs `gov memaudit scan` as a child process on a planted home, set and projects folder (the support module).
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone

import pytest

import w2_204_scan_support as M
from w2_204_support import HIDDEN, VISIBLE

QUESTIONS = {
    "q01": "Which brass lantern ordinance of the Velloran harbour board fixes the dusk toll for barges?",
    "q02": "How many tide gauges did the Quillmarsh survey of the eastern breakwater record before the storm?",
    "q03": "What replaced the copper mooring rule that the Ostravel pilot guild adopted after the flood?",
    "q04": "Where does the Brackenhold berth register say that winter anchors must be stored?",
    "q05": "Which clerk of the Tamsworth customs house signed the third amendment on ballast fees?",
}
GOLDS = {
    "q01": "The Zephranel decree of the harbour board sets nine lanterns at dusk.",
    "q02": "Seventeen gauges, as the Corvantle ledger records.",
    "q03": "The Mirelquist accord replaced it in the spring session.",
    "q04": "In the Pellingrove shed on the north quay.",
    "q05": "Clerk Abernathine of the night watch.",
}
WORDS = ("Velloran", "Quillmarsh", "Ostravel", "Brackenhold", "Tamsworth",
         "Zephranel", "Corvantle", "Mirelquist", "Pellingrove", "Abernathine")
OTHER_SET_QUESTION = "Which bronze bell of the Harrowgate signal tower rings when the outer channel closes?"


@pytest.fixture
def home(tmp_path):
    return M.make_home(tmp_path)


@pytest.fixture
def projects(home):
    return home / ".claude" / "projects"


def _sanity_of_the_planted_questions():
    keys = [M.key(q) for q in QUESTIONS.values()]
    assert len(set(keys)) == len(keys) and all(len(k) == 48 and k[-1] != " " for k in keys), keys


_sanity_of_the_planted_questions()


# -- S13 (M1): a bare id is not evidence ------------------------------------------------------------------------------
def _busy_projects(projects, sessions=("sess-busy-a", "sess-busy-b", "sess-busy-c")) -> list:
    """Three busy transcripts (bare q01..q40 as chats, numbered lists, another set's work) and a sub-agent's."""
    planted = [M.transcript(projects / "-home-work-proj" / f"{s}.jsonl", M.busy_lines(s)) for s in sessions]
    planted.append(M.transcript(projects / "-home-work-proj" / "sess-busy-a" / "subagents" / "agent-b7.jsonl",
                                M.busy_lines("sess-busy-a", ids=range(5, 15))))
    planted.append(M.transcript(projects / "-home-other-proj" / "sess-other.jsonl", [
        M.say("sess-other", "Review findings F-1 to F-12; q01 of the checklist and Q07 are open"),
        M.chat("sess-other", "(q08) and [q09] and q10: all three, then q11."),
    ]))
    return planted


def test_s13_bare_ids_in_many_transcripts_and_a_dummy_set_are_no_finding(home, projects):
    dummy = M.audit_set(home, M.dummy_ids())
    planted = _busy_projects(projects)
    run = M.scan(home, dummy, projects)
    assert run.code == 0, run
    assert run.lines() and run.lines()[0].startswith("no transcript in the window names the set"), run
    assert f"{len(planted)} transcripts read" in run.lines()[0], run
    data = M.scan(home, dummy, projects, json_form=True)
    assert data.code == 0 and data.envelope()["result"]["findings"] == [], data


def test_s13_an_id_beside_the_tag_or_the_audit_name_is_a_finding_naming_its_transcript(home, projects):
    dummy = M.audit_set(home, M.dummy_ids())
    _busy_projects(projects)
    tagged = M.transcript(projects / "-home-work-proj" / "sess-tagged.jsonl", [
        M.say("sess-tagged", "nothing here yet"),
        M.chat("sess-tagged", f"{M.TAG} q07"),
    ])
    named = M.transcript(projects / "-home-third-proj" / "sess-named.jsonl", [
        M.bash("sess-named", f"echo 'set {M.NAME}: q07 is the one to look at'"),
    ])
    run = M.scan(home, dummy, projects)
    assert run.code == 1, run
    assert run.lines()[0].startswith("MEASURE VOID: 2 finding(s)"), run
    lines = M.finding_lines(run)
    assert len(lines) == 2, run
    assert any(line.startswith(f"{tagged}:2 ") and "kind=id" in line and line.endswith("match=q07") for line in lines), lines
    assert any(line.startswith(f"{named}:1 ") and "kind=id" in line and line.endswith("match=q07") for line in lines), lines
    data = M.scan(home, dummy, projects, json_form=True)
    assert data.code == 1, data
    assert M.findings(data) == {("sess-tagged.jsonl", "id", "q07"), ("sess-named.jsonl", "id", "q07")}, data


def test_s13_the_name_and_the_tag_count_only_as_whole_tokens(home, projects):
    dummy = M.audit_set(home, M.dummy_ids())
    M.transcript(projects / "-p" / "sess-tokens.jsonl", [
        M.chat("sess-tokens", f"1{M.TAG} q07"),                         # a longer digit run is no tag
        M.chat("sess-tokens", f"{M.TAG}9 q07"),
        M.chat("sess-tokens", f"x{M.TAG} q07"),                         # inside a letter run
        M.chat("sess-tokens", f"{M.TAG}T163111Z q07"),                  # a run folder's stamp
        M.chat("sess-tokens", f"docs/close/nightly/NR-{M.TAG}T230633Z-09143b8c4eab.json q07"),
        M.chat("sess-tokens", f"{M.NAME}5 q07"),                        # another audit's name
        M.chat("sess-tokens", "memory-audit-20261001 q07"),             # another set
        M.chat("sess-tokens", f"set_{M.TAG} q07"),                      # inside an underscore run
        M.chat("sess-tokens", f"({M.TAG}) q09"),                        # the one finding
    ])
    data = M.scan(home, dummy, projects, json_form=True)
    assert data.code == 1, data
    assert M.findings(data) == {("sess-tokens.jsonl", "id", "q09")}, data
    lines = [f["line"] for f in data.envelope()["result"]["findings"]]
    assert lines == [9], lines


@pytest.mark.parametrize("where, evidence", [
    ("standing", "20261108"),
    ("standing-hidden", "memory-standing-20261108"),
    ("audit-hidden", M.TAG),
    ("own-folder", "dummyset-kestrel"),
    ("own-folder-hidden", "dummyset-kestrel"),
])
def test_s13_the_set_s_names_come_from_its_real_path(home, projects, where, evidence):
    """The audit or standing name in the path, its eight digits; else the set's own folder (the parent's when the
    folder is ``hidden``), at least 8 characters, with no tag. A bare id beside the line is still no finding."""
    folder = {"standing": home / "eval" / "fixtures" / "evaluation" / "memory-standing-20261108",
              "standing-hidden": home / "eval" / "fixtures" / "evaluation" / "memory-standing-20261108",
              "audit-hidden": home / "eval" / "fixtures" / "evaluation" / M.NAME,
              "own-folder": home / "sets" / "dummyset-kestrel",
              "own-folder-hidden": home / "sets" / "dummyset-kestrel"}[where]
    M.write_set(folder, M.dummy_ids())
    target = folder / "hidden" if where.endswith("hidden") else folder
    M.transcript(projects / "-p" / "sess-names.jsonl", [
        M.chat("sess-names", "q07 and q08 are bare"),
        M.chat("sess-names", f"{evidence} q08"),
    ])
    data = M.scan(home, target, projects, json_form=True)
    assert data.code == 1, data
    assert M.findings(data) == {("sess-names.jsonl", "id", "q08")}, data
    assert [f["line"] for f in data.envelope()["result"]["findings"]] == [2], data


def test_s13_a_set_folder_name_under_8_characters_names_nothing_so_its_ids_are_no_finding(home, projects):
    folder = M.write_set(home / "sets" / "dset", M.dummy_ids())
    M.transcript(projects / "-p" / "sess-short.jsonl", [
        M.chat("sess-short", "dset q07"),
        M.chat("sess-short", "q08 in dset/hidden"),
    ])
    data = M.scan(home, folder, projects, json_form=True)
    assert data.code == 0 and data.envelope()["result"]["findings"] == [], data


def test_s13_guard_every_transcript_of_the_window_is_read(home, projects):
    """A-12: the fix never narrows which transcripts are read. Green on the base by design (a guard)."""
    dummy = M.audit_set(home, M.dummy_ids())
    forms_abs = str(dummy.resolve())
    in_window = [
        M.transcript(projects / "-a" / "sess-1.jsonl", [M.say("sess-1", "nothing of any set")]),
        M.transcript(projects / "-a" / "sess-1" / "subagents" / "agent-c3.jsonl", [M.say("sess-1", "plain work")]),
        M.transcript(projects / "-b" / "sess-2.jsonl", [M.bash("sess-2", f"ls {forms_abs}")]),
        M.transcript(projects / "-c" / "deep" / "sess-3.jsonl", [M.chat("sess-3", "other words")]),
        M.transcript(projects / "-d" / "sess-4.jsonl", [M.chat("sess-4", "a line outside the window", "2026-11-09T01:00:00Z")]),
    ]
    M.transcript(projects / "-a" / "sess-old.jsonl", [M.say("sess-old", f"ls {forms_abs}")], "2026-11-09T12:00:00Z")
    data = M.scan(home, dummy, projects, json_form=True)
    assert data.code == 1, data
    result = data.envelope()["result"]
    assert result["transcripts_read"] == len(in_window), result
    assert M.findings(data) == {("sess-2.jsonl", "path", forms_abs)}, data


# -- S14 (M2): a question's text read is evidence ---------------------------------------------------------------------
def _text_forms():
    q1, q2, q3, q4, q5 = (QUESTIONS[k] for k in ("q01", "q02", "q03", "q04", "q05"))
    spread = q2.replace(" ", "\n", 3).replace(" ", "   \t ", 2)
    escaped_source = q5.replace(" ", "\n", 2)
    escaped = "".join(f"\\u{ord(c):04x}" if c != "\n" else "\\n" for c in escaped_source)
    first, rest = q1[:70], q1[70:]
    read_tool = (f"     1\tid: q01\n     2\tquestion: {first}\n     3\t  {rest}\n"
                 f"     4\tgold_answer: see the register\n")
    return {
        "other-whitespace": ("q02", M.say("sess-form", f"so it asks:\n{spread}")),
        "other-case": ("q03", M.chat("sess-form", q3.upper())),
        "after-other-text": ("q04", M.bash("sess-form", f"echo 'the hard one: {q4} done' >> notes.md")),
        "json-escaped": ("q05", '{"type": "user", "sessionId": "sess-form", "timestamp": "' + M.AT + '", '
                                '"message": {"role": "user", "content": [{"type": "tool_result", '
                                '"tool_use_id": "toolu_x", "content": "' + escaped + '"}]}}'),
        "tool-result-read": ("q01", M.tool_result("sess-form", read_tool)),
    }


@pytest.mark.parametrize("form", list(_text_forms()))
def test_s14_a_question_s_text_read_is_a_text_finding_whose_match_is_its_id(home, projects, form):
    qid, line = _text_forms()[form]
    folder = M.audit_set(home, QUESTIONS, GOLDS)
    form_file = M.transcript(projects / "-p" / "sess-form.jsonl", [M.chat("sess-form", "start"), line])
    M.transcript(projects / "-p" / "sess-plain.jsonl", [M.say("sess-plain", OTHER_SET_QUESTION)])
    run = M.scan(home, folder, projects)
    assert run.code == 1 and run.lines()[0].startswith("MEASURE VOID: 1 finding(s)"), run
    assert M.finding_lines(run) == [f"{form_file}:2 session=sess-form role=- kind=text match={qid}"], run
    data = M.scan(home, folder, projects, json_form=True)
    assert data.code == 1 and M.findings(data) == {("sess-form.jsonl", "text", qid)}, data


def test_s14_the_key_is_the_first_48_normalised_characters_and_text_of_no_question_is_clean(home, projects):
    folder = M.audit_set(home, QUESTIONS, GOLDS)
    k3 = M.key(QUESTIONS["q03"])
    k4 = M.key(QUESTIONS["q04"])
    cut = QUESTIONS["q03"][:48]             # a line that cuts the text right after the key
    near = QUESTIONS["q04"][:47] + "Z and then something else entirely"   # the key less its last character
    assert M.normalised(cut) == k3 and k4 not in M.normalised(near)
    M.transcript(projects / "-p" / "sess-keys.jsonl", [
        M.say("sess-keys", OTHER_SET_QUESTION),
        M.say("sess-keys", near),
        M.say("sess-keys", "Which brass lantern ordinance"),       # a question's first words only
        M.tool_result("sess-keys", f"…{cut}"),
    ])
    data = M.scan(home, folder, projects, json_form=True)
    assert data.code == 1, data
    assert M.findings(data) == {("sess-keys.jsonl", "text", "q03")}, data
    assert [f["line"] for f in data.envelope()["result"]["findings"]] == [4], data


def test_s14_two_questions_each_read_are_two_findings_each_matching_its_own_id(home, projects):
    folder = M.audit_set(home, QUESTIONS, GOLDS)
    M.transcript(projects / "-p" / "sess-two-a.jsonl", [M.say("sess-two-a", QUESTIONS["q02"])])
    M.transcript(projects / "-q" / "sess-two-b.jsonl", [M.chat("sess-two-b", "x"), M.say("sess-two-b", QUESTIONS["q05"])])
    data = M.scan(home, folder, projects, json_form=True)
    assert data.code == 1, data
    assert M.findings(data) == {("sess-two-a.jsonl", "text", "q02"), ("sess-two-b.jsonl", "text", "q05")}, data


def test_s14_a_question_under_24_normalised_characters_gives_no_text_finding(home, projects):
    at_24, under_24 = "Who keeps the  Ferro  key?", "Who keeps the  Zarn  key?"
    assert len(M.normalised(at_24)) == 24 and len(M.normalised(under_24)) == 23 and len(under_24) >= 24
    folder = M.audit_set(home, {"q01": at_24, "q02": under_24, "q03": "Short one?"})
    M.transcript(projects / "-p" / "sess-short-a.jsonl", [M.say("sess-short-a", "who keeps the zarn key?")])
    M.transcript(projects / "-p" / "sess-short-b.jsonl", [M.say("sess-short-b", "Short one? yes")])
    M.transcript(projects / "-p" / "sess-short-c.jsonl", [M.say("sess-short-c", "who keeps the ferro key? nobody")])
    data = M.scan(home, folder, projects, json_form=True)
    assert data.code == 1, data
    assert M.findings(data) == {("sess-short-c.jsonl", "text", "q01")}, data


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads a mode 000 file")
def test_s14_an_unreadable_question_file_is_a_problem_an_empty_one_is_not(home, projects):
    folder = M.audit_set(home, {"q01": QUESTIONS["q01"], "q02": None, "q03": QUESTIONS["q03"]}, GOLDS)
    M.transcript(projects / "-p" / "sess-clean.jsonl", [M.say("sess-clean", "nothing of the set")])
    clean = M.scan(home, folder, projects)
    assert clean.code == 0, ("an empty question file is no problem", clean)
    locked = folder / "hidden" / "q01.yaml"
    locked.chmod(0)
    try:
        run = M.scan(home, folder, projects)
    finally:
        locked.chmod(0o600)
    assert run.code == 3 and "SCAN INCOMPLETE" in run.both and "q01.yaml" in run.both, run


# -- S15 (M3): the path counts as before; nothing printed holds a question's or an answer's text ------------------------
def test_s15_guard_each_path_form_and_a_question_file_path_is_a_path_finding(home, projects):
    """Green on the base by design (a guard): the path forms are evidence as before."""
    folder = M.audit_set(home, QUESTIONS, GOLDS)
    real = str(folder.resolve())
    rest = real[len(str(home.resolve())) + 1:]
    expected = {"sess-abs.jsonl": real, "sess-tilde.jsonl": f"~/{rest}", "sess-dollar.jsonl": f"$HOME/{rest}",
                "sess-segment.jsonl": M.SEGMENT, "sess-qfile.jsonl": real}
    lines = {"sess-abs.jsonl": M.bash("sess-abs", f"ls {real}"),
             "sess-tilde.jsonl": M.bash("sess-tilde", f"du -sh ~/{rest}"),
             "sess-dollar.jsonl": M.chat("sess-dollar", f"look in $HOME/{rest} later"),
             "sess-segment.jsonl": M.say("sess-segment", f"the set lives under {M.SEGMENT} in the eval root"),
             "sess-qfile.jsonl": M.bash("sess-qfile", f"cat {real}/hidden/q04.yaml")}
    for name, line in lines.items():
        M.transcript(projects / "-p" / name, [line])
    data = M.scan(home, folder, projects, json_form=True)
    assert data.code == 1, data
    assert M.findings(data) == {(name, "path", form) for name, form in expected.items()}, data


@pytest.mark.parametrize("json_form", [False, True], ids=["text", "json"])
def test_s15_a_question_and_its_gold_answer_read_from_a_file_are_printed_nowhere(home, projects, json_form):
    folder = M.audit_set(home, QUESTIONS, GOLDS)
    real = str(folder.resolve())
    body = (folder / "hidden" / "q02.yaml").read_text(encoding="utf-8")
    numbered = "".join(f"{n:>6}\t{line}\n" for n, line in enumerate(body.splitlines(), 1))
    reader = M.transcript(projects / "-p" / "sess-reader.jsonl", [
        M.entry("assistant", "sess-reader", [{"type": "tool_use", "id": "toolu_r", "name": "Read",
                                               "input": {"file_path": f"{real}/hidden/q02.yaml"}}]),
        M.tool_result("sess-reader", numbered),
    ])
    M.transcript(projects / "-p" / "sess-quoter.jsonl", [
        M.say("sess-quoter", f"The question was: {QUESTIONS['q05']} The answer: {GOLDS['q05']}"),
    ])
    run = M.scan(home, folder, projects, json_form=json_form)
    assert run.code == 1, run
    if json_form:
        assert M.findings(run) == {("sess-reader.jsonl", "path", real), ("sess-reader.jsonl", "text", "q02"),
                                   ("sess-quoter.jsonl", "text", "q05")}, run
    else:
        assert run.lines()[0].startswith("MEASURE VOID: 3 finding(s)"), run
        assert f"{reader}:2 session=sess-reader role=- kind=text match=q02" in M.finding_lines(run), run
    for qid in ("q02", "q05"):
        for text in (QUESTIONS[qid], M.normalised(QUESTIONS[qid]), M.key(QUESTIONS[qid]), GOLDS[qid],
                     M.normalised(GOLDS[qid]), QUESTIONS[qid][:30], GOLDS[qid][:24]):
            assert text not in run.out and text not in run.err, f"the output holds {text!r}"
    for word in WORDS:
        assert word not in run.out and word.lower() not in run.out.lower() and word.lower() not in run.err.lower(), word


# -- S16 (M4): EXAMIN's case, end to end ------------------------------------------------------------------------------
def _stamp(delta: timedelta) -> str:
    return (datetime.now(timezone.utc) - delta).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def _examin_window(projects, *, with_path: bool, dummy) -> list:
    at, mtime = _stamp(timedelta(hours=3)), _stamp(timedelta(hours=2))
    planted = []
    for n, session in enumerate(("sess-writer-like", "sess-checker-like", "sess-cto", "sess-lead", "sess-review")):
        lines = M.busy_lines(session, stamp=at)
        lines += [M.say(session, f"Ticket {n}: 1. q0{n + 1} 2. q1{n} 3. q2{n} — 40 questions, 20 findings so far", at)]
        planted.append(M.transcript(projects / f"-home-examin-{n % 2}" / f"{session}.jsonl", lines, mtime))
    planted.append(M.transcript(projects / "-home-examin-0" / "sess-cto" / "subagents" / "agent-d4.jsonl",
                                M.busy_lines("sess-cto", ids=range(1, 21), stamp=at), mtime))
    lines = [M.chat("sess-outside", "make a dummy set to test the scan", at)]
    if with_path:
        rest = str(dummy.resolve())[len(str(dummy.parents[3].resolve())) + 1:]
        lines.append(M.bash("sess-outside", f"ls ~/{rest}/hidden | wc -l", at))
    planted.append(M.transcript(projects / "-home-examin-1" / "sess-outside.jsonl", lines, mtime))
    return planted


def test_s16_examin_s_case_the_one_typed_path_is_the_only_finding_and_without_it_the_window_is_clean(tmp_path, home):
    dummy = M.audit_set(home, M.dummy_ids(), name="memory-audit-20261120")
    assert all((dummy / "hidden" / f"q{k:02d}.yaml").stat().st_size == 0 for k in range(1, 41))
    since = (_stamp(timedelta(days=1)), None)
    with_path, without = tmp_path / "projects-with-path", tmp_path / "projects-without"
    planted = _examin_window(with_path, with_path=True, dummy=dummy)
    _examin_window(without, with_path=False, dummy=dummy)
    rest = str(dummy.resolve())[len(str(home.resolve())) + 1:]

    run = M.scan(home, dummy, with_path, window=since)
    assert run.code == 1 and run.lines()[0].startswith(f"MEASURE VOID: 1 finding(s), {len(planted)} transcripts read"), run
    assert M.finding_lines(run) == [f"{planted[-1]}:2 session=sess-outside role=- kind=path match=~/{rest}"], run
    data = M.scan(home, dummy, with_path, json_form=True, window=since)
    assert data.code == 1 and M.findings(data) == {("sess-outside.jsonl", "path", f"~/{rest}")}, data

    clean = M.scan(home, dummy, without, window=since)
    assert clean.code == 0, clean
    assert clean.lines()[0].startswith(f"no transcript in the window names the set: {len(planted)} transcripts read"), clean


def test_s16_the_fresh_close_agrees_a_busy_window_without_the_path_is_clean(stage):
    """`fresh` on the planted second repository, its window holding busy transcripts (bare ids, numbered lists, another
    set's work) and no line of either half's name, tag, path or question text: both halves scan clean."""
    run = stage("busy")
    planted = sorted(run.world.projects.rglob("*.jsonl"))
    assert len(planted) >= 3 and all(re.search(r"\bq07\b", p.read_text(encoding="utf-8")) for p in planted[:2]), planted
    final = run["final"]
    scans = sorted(x for x in final.lines if x.startswith("SCAN ") or x.startswith("MEASURE VOID"))
    assert scans == [f"SCAN {VISIBLE} clean", f"SCAN {HIDDEN} clean"], final
    assert final.code == 0 and any(x.startswith("FRESH VERDICT") for x in final.lines), final
