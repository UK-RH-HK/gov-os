"""W1-42 acceptance tests: the Wave 1 exit report held to the ticket's KPI lines (DAEO-gjjf).

The cases read ``docs/plan/wave-1-exit/EXIT-REPORT.md`` and the kept answers under
``docs/plan/wave-1-exit/evidence/``. The form both must have is in this folder's README.
"""

from __future__ import annotations

import json
import re

import pytest

PROGRAMMES = ("ORION", "ARGUS")
PERCENT = re.compile(r"(\d+(?:\.\d+)?)\s*%")


def _row(rows, column, key, where, read):
    """The one row whose ``column`` cell begins with ``key`` as whole words."""
    begins = re.compile(re.escape(read.norm(key)) + r"(?![a-z0-9])")
    hits = [row for row in rows if begins.match(read.norm(row[column]))]
    assert len(hits) == 1, f"{where}: {len(hits)} rows for '{key}', expected one"
    return hits[0]


def _programme(report, read, programme):
    title = f"Programme {programme}"
    return title, read.section(report, title)


def _cycle(report, read, programme):
    title, text = _programme(report, read, programme)
    return title, text, read.table(text, title, "Step", "Result", "Ticket ids", "Evidence")


def _share_rows(report, read):
    text = read.section(report, "Governance share")
    rows = read.table(text, "Governance share", "Programme", "Share", "Cache reads", "Record")
    return {programme: _row(rows, "programme", programme, "Governance share", read) for programme in PROGRAMMES}


def _stated_share(cell, read):
    """The figure a Share cell states, or None when it says 'not measured' with a reason."""
    hit = PERCENT.match(read.norm(cell))
    if hit:
        return float(hit.group(1))
    assert read.norm(cell).startswith("not measured") and read.reason_after(cell, "not measured"), (
        f"Governance share: the cell '{cell}' is neither a figure in % nor 'not measured: <reason>'")
    return None


# ---------------------------------------------------------------------------
# WAVE_1_WBS section 4: the exit criteria
# ---------------------------------------------------------------------------

def test_every_exit_criterion_is_answered_with_its_evidence(report, read):
    text = read.section(report, "Exit criteria")
    rows = read.table(text, "Exit criteria", "Criterion", "Verdict", "Evidence")
    assert [read.norm(row["criterion"]).split(" ")[0].rstrip(".:") for row in rows] == list(read.CRITERIA), (
        f"Exit criteria: the rows must be, in this order, {', '.join(read.CRITERIA)}")
    for row in rows:
        name = row["criterion"]
        assert row["verdict"].replace("*", "").strip() in read.VERDICTS, (
            f"criterion {name}: verdict '{row['verdict']}' is not one of {', '.join(read.VERDICTS)}")
        assert not read.is_blank(row["evidence"]), f"criterion {name}: no evidence and no reason is given"
        if read.norm(row["verdict"]) == "met":
            assert read.paths_in(row["evidence"]), f"criterion {name}: MET, but its evidence names no path"


def test_every_path_the_report_names_exists(report, read):
    named = read.paths_in(report)
    assert any(path.startswith(read.EVIDENCE_REL + "/") for path in named), (
        f"the report names no kept answer under {read.EVIDENCE_REL}/")
    globbed = sorted({path for path in named if any(sign in path for sign in "*?[<")})
    assert not globbed, f"the report names patterns, not paths: {globbed}"
    missing = sorted({path for path in named if not (read.ROOT / path).exists()})
    assert not missing, f"the report names paths that do not exist in the repository: {missing}"


# ---------------------------------------------------------------------------
# KPI 1: the cycle on both programmes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("programme", PROGRAMMES)
def test_programme_cycle_is_stated_step_by_step(report, read, programme):
    title, text, rows = _cycle(report, read, programme)
    read.field(text, title, "Feature")
    stage = read.field(text, title, "Adoption stage reached")
    reached = re.match(r"A(\d+)\b", read.norm(stage).upper())
    assert reached, f"{title}: 'Adoption stage reached' must begin with a stage, A0 to A8, not '{stage}'"
    if int(reached.group(1)) < 8:  # DEC-658: adopted fully, or the stage reached with the reason
        assert read.reason_after(stage, reached.group(0)), f"{title}: adopted to {reached.group(0)} only, no reason given"
    read.field(text, title, "Close result")

    assert [read.norm(row["step"]) for row in rows] == [read.norm(step) for step in read.STEPS], (
        f"{title}: the cycle table must hold exactly these steps in this order: {', '.join(read.STEPS)}")
    for row in rows:
        step, result = row["step"], read.norm(row["result"])
        if result == "done":
            ids = re.findall(rf"\b{programme}-[A-Za-z0-9]+\b", row["ticket ids"])
            assert ids, f"{title}, step '{step}': done, but no ticket id of the clone ({programme}-...) is given"
            assert read.paths_in(row["evidence"]), f"{title}, step '{step}': done, but its evidence names no path"
        else:
            assert read.not_reached(result) and read.reason_after(result, "not reached"), (
                f"{title}, step '{step}': the result must be 'done' or 'not reached: <reason>', not '{row['result']}'")


@pytest.mark.parametrize("programme", PROGRAMMES)
def test_programme_close_is_stated_as_the_kept_answer_says(report, read, programme):
    title, text, rows = _cycle(report, read, programme)
    close = _row(rows, "step", "close", title, read)
    stated = read.norm(read.field(text, title, "Close result"))
    if read.norm(close["result"]) != "done":
        assert "clean gov close" not in stated and not read.is_blank(stated), (
            f"{title}: the close step was not reached, yet 'Close result' says '{stated}'")
        return
    answer = read.load_json(read.evidence_path(close["evidence"], f"{title}, step 'close'"))
    assert isinstance(answer, dict) and answer.get("command") == "close", (
        f"{title}: the kept answer of the close is not the answer of gov close under --json")
    assert answer.get("ok") is True and not answer.get("error"), (
        f"{title}: the close step is stated as done, the kept answer of gov close has ok={answer.get('ok')!r}: "
        "a close that gov close refused is 'not reached: <reason>'")
    closed = (answer.get("result") or {}).get("ticket")
    assert closed and closed in close["ticket ids"], (
        f"{title}: the kept answer closes '{closed}', the close step names '{close['ticket ids']}'")
    assert "clean gov close" in stated, f"{title}: 'Close result' must say 'clean gov close', not '{stated}'"


# ---------------------------------------------------------------------------
# KPI 13: one real ticket closed by a clean gov close (DEC-511, DEC-658)
# ---------------------------------------------------------------------------

def test_one_real_ticket_closed_by_a_clean_gov_close(report, read):
    text = read.section(report, "Clean close")
    ticket = read.field(text, "Clean close", "Ticket").strip("` ")
    kept = read.evidence_path(read.field(text, "Clean close", "Kept answer"), "section 'Clean close'")
    assert read.norm(read.field(text, "Clean close", "Exception")) == "none", (
        "Clean close: the line 'Exception' must say 'none' (DEC-511: no exception)")
    assert re.fullmatch(r"ORION-[A-Za-z0-9]+", ticket), (
        f"Clean close: the proof uses a-dev's implementation ticket (DEC-658), not '{ticket}'")
    answer = read.load_json(kept)
    assert isinstance(answer, dict) and answer.get("command") == "close", f"{kept} is not an answer of gov close"
    assert answer.get("ok") is True and not answer.get("error"), f"{kept}: the close did not succeed"
    result = answer.get("result") or {}
    assert result.get("ticket") == ticket, f"{kept} closes '{result.get('ticket')}', the report names '{ticket}'"
    assert result.get("close_record"), f"{kept}: the answer names no close record"
    _, _, rows = _cycle(report, read, "ORION")
    implementation = _row(rows, "step", "implementation", "Programme ORION", read)
    assert ticket in implementation["ticket ids"], (
        f"Clean close: '{ticket}' is not the implementation ticket of the ORION cycle table")


# ---------------------------------------------------------------------------
# KPI 8 and 9: the retrieval figures (DEC-377, DEC-414)
# ---------------------------------------------------------------------------

def _figure_row(report, read, measure, figure, baseline):
    text = read.section(report, "Retrieval")
    rows = read.table(text, "Retrieval", "Measure", "Figure", "Baseline", "Comparison")
    row = _row(rows, "measure", measure, "Retrieval", read)
    for column, value in (("figure", figure), ("baseline", baseline)):
        shown = re.search(r"\d+(?:\.\d+)?", row[column])
        assert shown and abs(float(shown.group(0)) - value) < 0.05, (
            f"Retrieval, '{measure}': the report gives {column} '{row[column]}', the kept figures give {value}")
    wanted = "below" if figure < baseline else "at or above"
    assert read.norm(row["comparison"]).startswith(wanted), (
        f"Retrieval, '{measure}': {figure} against {baseline} is '{wanted}', the report says '{row['comparison']}'")


def _percent(read, part, key, name):
    value = read.number(part.get(key))
    assert value is not None and 0 <= value <= 100, f"retrieval-hit5.json: {name}.{key} is not a figure from 0 to 100"
    return value


def test_dev_query_set_mean_hit5_is_remeasured_against_85(report, read):
    part = read.load_json("retrieval-hit5.json").get("dev_query_set") or {}
    figure = _percent(read, part, "mean_hit_at_5", "dev_query_set")
    assert part.get("baseline") == 85, "retrieval-hit5.json: dev_query_set.baseline must be 85 (DEC-414)"
    assert type(part.get("queries")) is int and part["queries"] > 0, "retrieval-hit5.json: dev_query_set.queries"
    _figure_row(report, read, "mean hit@5", figure, 85)


def test_callers_impact_hit5_is_measured_on_the_code_classes(report, read):
    part = read.load_json("retrieval-hit5.json").get("code_classes") or {}
    figure = _percent(read, part, "callers_impact_hit_at_5", "code_classes")
    baseline = _percent(read, part, "baseline", "code_classes")
    assert isinstance(part.get("classes"), list) and part["classes"] and all(
        isinstance(name, str) and name.strip() for name in part["classes"]), (
        "retrieval-hit5.json: code_classes.classes must name the code classes measured")
    assert type(part.get("queries")) is int and part["queries"] > 0, "retrieval-hit5.json: code_classes.queries"
    assert "codeintel" in str(part.get("baseline_source", "")), (
        "retrieval-hit5.json: code_classes.baseline_source must name the S0b2 code-intelligence report (DEC-377)")
    _figure_row(report, read, "callers/impact hit@5", figure, baseline)


# ---------------------------------------------------------------------------
# KPI 2: RETR-A-04 and RETR-X-02
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("query", ("RETR-A-04", "RETR-X-02"))
def test_retrieval_query_ran_with_bundles_expansions_notes_and_stopping_reason(report, read, query):
    name = f"{query}.json"
    kept = read.load_json(name)
    assert kept.get("query_id") == query, f"{name}: query_id must be {query}"
    bundles = kept.get("bundles")
    assert isinstance(bundles, list) and bundles and all(isinstance(bundle, dict) for bundle in bundles), (
        f"{name}: 'bundles' must hold the bundles as gov retrieve returned them")
    batches = sum(len(bundle.get("batches") or []) for bundle in bundles)
    assert batches >= 2, f"{name}: {batches} batches in all, the query must be answered in more than one"
    for i, bundle in enumerate(bundles):
        assert bundle.get("stopping_reason") in read.STOPPING_REASONS, (
            f"{name}: bundle {i} has no stopping reason from the fixed list")
        evidence = bundle.get("evidence")
        assert isinstance(evidence, list) and evidence, f"{name}: bundle {i} holds no evidence"
        for item in evidence:
            assert item.get("id") and re.fullmatch(r"[0-9a-f]{64}", str(item.get("sha256", ""))), (
                f"{name}: bundle {i} has an evidence item not cited by id and hash")
    expansions = [expansion for bundle in bundles for expansion in bundle.get("expansions") or []]
    assert expansions and all(expansion.get("parent_id") for expansion in expansions), (
        f"{name}: no named parent expansion (DEC-091)")
    assert kept.get("validator_errors") == [], f"{name}: 'validator_errors' must be the validator's empty list"
    exceeded, notes = kept.get("packet_ceiling_exceeded"), kept.get("synthesis_notes")
    assert type(exceeded) is bool and isinstance(notes, list), (
        f"{name}: 'packet_ceiling_exceeded' (true or false) and 'synthesis_notes' (a list of paths) are required")
    if exceeded:
        assert notes, f"{name}: the evidence exceeded the packet ceiling and no synthesis note is named"
    absent = [note for note in notes if not (read.ROOT / str(note)).is_file()]
    assert not absent, f"{name}: synthesis notes that are not files of the repository: {absent}"

    text = read.section(report, "Retrieval")
    rows = read.table(text, "Retrieval", "Query", "Kept bundles", "Batches", "Parent expansions",
                      "Synthesis notes", "Stopping reason")
    row = _row(rows, "query", query, "Retrieval", read)
    assert f"{read.EVIDENCE_REL}/{name}" in read.paths_in(row["kept bundles"]), f"Retrieval, {query}: {name} not named"
    assert row["stopping reason"].strip("` ") == bundles[-1]["stopping_reason"], (
        f"Retrieval, {query}: the report's stopping reason is not the last bundle's")
    for column, count in (("batches", batches), ("parent expansions", len(expansions)), ("synthesis notes", len(notes))):
        shown = re.match(r"\d+", read.norm(row[column]))
        assert shown and int(shown.group(0)) == count, (
            f"Retrieval, {query}: the report gives {column} '{row[column]}', the kept bundles give {count}")


# ---------------------------------------------------------------------------
# KPI 3 [CAP-38.b] and KPI 4 [CAP-28.b]
# ---------------------------------------------------------------------------

def _check_answer(read):
    answer = read.load_json("gov-check.json")
    assert isinstance(answer, dict) and answer.get("command") == "check", (
        "gov-check.json is not the answer of gov check under --json")
    result = answer.get("result") or (answer.get("error") or {}).get("details") or {}
    assert isinstance(result.get("families"), dict) and isinstance(result.get("checks"), list), (
        "gov-check.json holds no 'families' and no 'checks'")
    return answer, result


def test_gov_check_reports_17_of_17_families_with_an_executable_check(report, read):
    """[CAP-38.b]"""
    _, result = _check_answer(read)
    families = result["families"]
    assert len(families) == 17, f"gov-check.json: {len(families)} governance test families, expected 17"
    checked = {read.family_key(check.get("family", "")) for check in result["checks"] if check.get("id")}
    bare = sorted(name for name, family in families.items()
                  if family.get("reason") == "no registered check" or read.family_key(name) not in checked)
    assert not bare, f"gov-check.json: families with no executable check: {bare}"
    text = read.section(report, "gov check and the twelve commands")
    assert "17 of 17" in read.norm(text), "the report does not state '17 of 17' families beside the kept answer"
    assert f"{read.EVIDENCE_REL}/gov-check.json" in read.paths_in(text), "the report does not name gov-check.json"


def test_all_twelve_wave_1_commands_are_implemented(report, read):
    """[CAP-28.b]"""
    names = read.reserved_commands()
    assert len(names) == 12, f"src/gov/cli/main.py reserves {len(names)} commands, expected twelve"
    kept = read.load_json("gov-commands.json")
    assert isinstance(kept, dict) and sorted(kept) == sorted(names), (
        f"gov-commands.json must hold exactly the twelve commands: {', '.join(names)}")
    for name in names:
        entry = kept[name]
        argv = entry.get("argv") if isinstance(entry, dict) else None
        assert isinstance(argv, list) and argv[:2] == ["gov", name], f"gov-commands.json, {name}: argv must begin gov {name}"
        assert not {"-h", "--help"} & set(argv), f"gov-commands.json, {name}: a help call does not reach the command"
        assert type(entry.get("exit_code")) is int and "answer" in entry and entry["answer"] not in ("", None, {}), (
            f"gov-commands.json, {name}: 'exit_code' and the kept 'answer' are required")
        assert "NOT_IMPLEMENTED" not in json.dumps(entry), f"gov {name} answered NOT_IMPLEMENTED"
        assert read.command_module(name), f"gov {name} has no command module: it would answer NOT_IMPLEMENTED"
    text = read.section(report, "gov check and the twelve commands")
    assert f"{read.EVIDENCE_REL}/gov-commands.json" in read.paths_in(text), "the report does not name gov-commands.json"


# ---------------------------------------------------------------------------
# KPI 5: worker sessions through gov launch (DEC-161)
# ---------------------------------------------------------------------------

def test_worker_sessions_were_started_through_gov_launch(report, read):
    text = read.section(report, "Worker sessions")
    rows = read.table(text, "Worker sessions", "Programme", "Role", "Session id", "Ticket", "Started through",
                      "Sandbox", "Network profile", "Launch record")
    ids = [read.norm(row["session id"]) for row in rows]
    assert rows and len(set(ids)) == len(ids), "Worker sessions: every row is one session with its own session id"
    for row in rows:
        where = f"Worker sessions, session '{row['session id']}'"
        blank = [column for column, cell in row.items() if read.is_blank(cell)]
        assert not blank, f"{where}: empty cells {blank}"
        assert read.norm(row["started through"]) == "gov launch", f"{where}: not started through gov launch"
        assert read.norm(row["sandbox"]) == "sandboxed", f"{where}: the Sandbox cell must say 'sandboxed'"
        assert read.evidence_path(row["launch record"], where)
    for programme in PROGRAMMES:
        mine = [row for row in rows if read.norm(row["programme"]).startswith(programme.lower())]
        roles = {read.norm(row["role"]) for row in mine}
        lacking = [role for role in read.WORKER_ROLES if role not in roles]
        assert not lacking, f"Worker sessions, {programme}: no session of the roles {lacking}"
        stray = [row["ticket"] for row in mine if not re.search(rf"\b{programme}-[A-Za-z0-9]+\b", row["ticket"])]
        assert not stray, f"Worker sessions, {programme}: tickets that are not the clone's: {stray}"


# ---------------------------------------------------------------------------
# KPI 2 and the failure lines: governance share, MR-3
# ---------------------------------------------------------------------------

def test_governance_share_is_measured_and_at_most_15_percent_on_each_programme(report, read):
    """Waits for a record: the measured share (DEC-655)."""
    kept = read.load_json("governance-share.json")
    rows = _share_rows(report, read)
    for programme in PROGRAMMES:
        part = kept.get(programme) if isinstance(kept, dict) else None
        assert isinstance(part, dict), f"governance-share.json: no entry for {programme}"
        share = read.number(part.get("share_percent"))
        assert share is not None and 0 <= share <= 100, (
            f"governance-share.json, {programme}: share_percent is not a measured figure from 0 to 100")
        assert type(part.get("cache_read_tokens")) is int, (
            f"governance-share.json, {programme}: cache_read_tokens (reported separately, DEC-086) is not a count")
        record = str(part.get("record", ""))
        assert record.startswith(read.EVIDENCE_REL + "/") and (read.ROOT / record).is_file(), (
            f"governance-share.json, {programme}: 'record' must be the kept answer of the counter, a file under "
            f"{read.EVIDENCE_REL}/")
        stated = _stated_share(rows[programme]["share"], read)
        assert stated is not None and abs(stated - share) < 0.05, (
            f"Governance share, {programme}: the report says '{rows[programme]['share']}', the record {share}")
        assert record in read.paths_in(rows[programme]["record"]), f"Governance share, {programme}: record not named"
        assert share <= read.SHARE_LIMIT, f"{programme}: governance share {share} % is above {read.SHARE_LIMIT} %"


def test_zero_mr3_breaches_with_what_was_checked(report, read):
    kept = read.load_json("mr3.json")
    assert isinstance(kept, dict) and kept.get("breaches") == [], "mr3.json: 'breaches' must be the empty list"
    checked = kept.get("checked")
    assert isinstance(checked, list) and checked, "mr3.json: 'checked' must list what was checked"
    for entry in checked:
        lacking = [key for key in ("repository", "check", "method", "result") if read.is_blank(entry.get(key, ""))]
        assert not lacking, f"mr3.json: an entry of 'checked' lacks {lacking}"
    covered = {read.norm(entry["repository"]) for entry in checked}
    lacking = [clone for clone in read.PROGRAMMES.values() if clone not in covered]
    assert not lacking, f"mr3.json: nothing was checked on {lacking}"
    text = read.section(report, "MR-3")
    assert read.norm(read.field(text, "MR-3", "Breaches")) == "0", "MR-3: the line 'Breaches' must say 0"
    assert f"{read.EVIDENCE_REL}/mr3.json" in read.paths_in(text), "MR-3: the report does not name mr3.json"


# ---------------------------------------------------------------------------
# KPI 6 [CAP-40.c]: the three learning metrics per ticket (DEC-106)
# ---------------------------------------------------------------------------

def test_learning_metrics_table_has_a_full_row_for_every_wave_1_ticket(report, read):
    """[CAP-40.c]"""
    tickets = read.wave_1_tickets()
    assert len(tickets) == 50, f".tickets/ holds {len(tickets)} Wave 1 tickets, expected 50"
    text = read.section(report, "Learning metrics")
    rewritten = "Tests rewritten after implementation began"
    rows = read.table(text, "Learning metrics", "Ticket", "KPI disputes", rewritten, "Governance share")
    listed = [(re.search(r"W1-\d+", row["ticket"]) or [""])[0] for row in rows]
    assert sorted(listed) == sorted(tickets), (
        f"Learning metrics: one row per Wave 1 ticket; missing {sorted(set(tickets) - set(listed))}, "
        f"not a Wave 1 ticket or listed twice {sorted(name for name in listed if listed.count(name) > 1 or name not in tickets)}")
    for row, name in zip(rows, listed):
        for column in ("kpi disputes", read.norm(rewritten), "governance share"):
            cell = read.norm(row[column])
            assert not read.is_blank(cell), f"Learning metrics, {name}: '{column}' is empty"
            for words in ("not recorded", "not measured"):
                if cell.startswith(words):
                    assert read.reason_after(cell, words), f"Learning metrics, {name}: '{column}' says '{words}' with no reason"
        count = re.fullmatch(r"(\d+)\W*", read.norm(row[read.norm(rewritten)]))
        assert not (count and int(count.group(1)) > 0), (
            f"Learning metrics, {name}: tests were rewritten after implementation began and no reason is given")


# ---------------------------------------------------------------------------
# KPI 7 [CAP-23.c]: parallel tickets in the light form (DEC-235)
# ---------------------------------------------------------------------------

def test_parallel_tickets_ran_in_worktrees_and_were_merged_by_the_main_orchestrator(report, read):
    """[CAP-23.c]"""
    tickets = read.wave_1_tickets()
    text = read.section(report, "Parallel tickets")
    rows = read.table(text, "Parallel tickets", "Ticket", "Worktree", "Branch", "Ticket lead", "Merged by",
                      "Merge commit", "Suites re-run after the merge")
    assert len(rows) >= 2, "Parallel tickets: fewer than two tickets listed shows nothing run in parallel"
    for row in rows:
        name = (re.search(r"W1-\d+", row["ticket"]) or [""])[0]
        where = f"Parallel tickets, '{row['ticket']}'"
        assert name in tickets, f"{where}: not a Wave 1 ticket"
        assert name in row["worktree"], f"{where}: the worktree is not the ticket's own"
        assert row["branch"].strip("` ").startswith(f"w1/{name}"), f"{where}: the branch is not w1/{name}"
        assert not read.is_blank(row["ticket lead"]), f"{where}: no ticket lead"
        assert "main orchestrator" in read.norm(row["merged by"]), f"{where}: not merged by the main orchestrator"
        commit = read.commit_of(row["merge commit"])
        assert commit and read.is_ancestor(commit, "HEAD"), (
            f"{where}: '{row['merge commit']}' is not a commit in the history of this branch")
        cell = row["suites re-run after the merge"]
        assert not read.is_blank(cell) and read.paths_in(cell), f"{where}: no record of the suites re-run after the merge"


def test_git_worktree_list_shows_no_ticket_worktree_left(report, read):
    """[CAP-23.c] Waits for a record: the worktree list after this ticket's own worktree is removed."""
    text = read.section(report, "Parallel tickets")
    name = f"{read.EVIDENCE_REL}/git-worktree-list.txt"
    assert name in read.paths_in(read.field(text, "Parallel tickets", "git worktree list")), f"{name} is not named"
    lines = [line for line in read.load_text("git-worktree-list.txt").splitlines() if line.strip()]
    assert lines and all(re.search(r"\s[0-9a-f]{7,40}\s|\(bare\)", line) for line in lines), (
        "git-worktree-list.txt is not the output of git worktree list")
    left = [line for line in lines if re.search(r"gov-os-worktrees/|\[w1/W1-", line)]
    assert not left, f"git-worktree-list.txt: ticket worktrees are left: {left}"


# ---------------------------------------------------------------------------
# KPI 10: the owner's freeze, pause and lift (DEC-428, DEC-660)
# ---------------------------------------------------------------------------

def test_owner_steps_are_each_stated_with_their_result(report, read):
    text = read.section(report, "Owner's steps")
    rows = read.table(text, "Owner's steps", "Step", "Result", "Record")
    for step in ("B1", "B2", "B3"):
        row = _row(rows, "step", step, "Owner's steps", read)
        result = read.norm(row["result"])
        if result == "done":
            assert read.paths_in(row["record"]), f"Owner's steps, {step}: done, but no record is named"
        else:
            assert result.startswith("not done") and read.reason_after(result, "not done"), (
                f"Owner's steps, {step}: the result must be 'done' or 'not done: <reason>', not '{row['result']}'")


def test_owner_froze_paused_and_lifted_on_a_throwaway_repository_and_on_this_one(report, read):
    """Waits for a record: the owner's own check from a plain terminal (step B2)."""
    kept = read.load_json("owner-freeze-check.json")
    for where in ("throwaway", "this"):
        part = kept.get(where) if isinstance(kept, dict) else None
        assert isinstance(part, dict), f"owner-freeze-check.json: no entry '{where}'"
        assert not read.is_blank(part.get("repository", "")), f"owner-freeze-check.json, {where}: no repository"
        assert read.norm(part.get("terminal", "")) == "plain", (
            f"owner-freeze-check.json, {where}: 'terminal' must say 'plain' (not an agent session)")
        steps = part.get("steps")
        assert isinstance(steps, list) and len(steps) == 4 and all(isinstance(step, dict) for step in steps), (
            f"owner-freeze-check.json, {where}: four steps are required: {', '.join(read.OWNER_COMMANDS)}")
        for step, command in zip(steps, read.OWNER_COMMANDS):
            assert read.norm(step.get("command", "")).startswith(command), (
                f"owner-freeze-check.json, {where}: the steps must be, in order, {', '.join(read.OWNER_COMMANDS)}")
            assert step.get("answer") not in ("", None, {}), f"owner-freeze-check.json, {where}: a step has no answer"
        assert "--off" not in steps[0]["command"] and "--off" in steps[2]["command"]
        assert read.find_key(steps[1]["answer"], "paused") == [True], (
            f"owner-freeze-check.json, {where}: gov status after the freeze does not report paused")
        assert read.find_key(steps[3]["answer"], "paused") == [False], (
            f"owner-freeze-check.json, {where}: gov status after the lift still reports a freeze")
    assert not read.is_blank(kept["this"].get("refused_write", "")), (
        "owner-freeze-check.json, this: 'refused_write' must hold the text of the refusal of a write under the freeze")
    text = read.section(report, "Owner's steps")
    row = _row(read.table(text, "Owner's steps", "Step", "Result", "Record"), "step", "B2", "Owner's steps", read)
    assert read.norm(row["result"]) == "done", "Owner's steps: B2 is not stated as done"
    assert f"{read.EVIDENCE_REL}/owner-freeze-check.json" in read.paths_in(row["record"]), "B2: the record is not named"


# ---------------------------------------------------------------------------
# KPI 11 and 12: the baseline is empty, the adoption was complete (DEC-467, DEC-472, DEC-511, DEC-522)
# ---------------------------------------------------------------------------

def test_baseline_is_empty_and_adoption_was_complete_before_the_exit_run(report, read):
    answer, result = _check_answer(read)
    red = sorted(str(check.get("id")) for check in result["checks"] if check.get("status") == "RED")
    red += sorted(name for name, family in result["families"].items() if family.get("status") == "RED")
    assert answer.get("ok") is True and not red, (
        f"gov-check.json: the baseline is not empty, red at the exit run: {red} (DEC-472: a decision package)")
    text = read.section(report, "Baseline and adoption")
    rows = read.table(text, "Baseline and adoption", "Fact", "Result", "Evidence")
    for fact in ("gov adopt --lite run", "gov check baseline empty", "capability records present"):
        row = _row(rows, "fact", fact, "Baseline and adoption", read)
        assert read.norm(row["result"]) == "yes", f"Baseline and adoption: '{fact}' is not answered 'yes'"
        assert read.paths_in(row["evidence"]), f"Baseline and adoption: '{fact}' names no evidence path"
    adopted = read.commit_of(read.field(text, "Baseline and adoption", "Adoption complete at"))
    started = read.commit_of(read.field(text, "Baseline and adoption", "Exit run started at"))
    assert adopted and started, "Baseline and adoption: the two lines must each name a commit of this repository"
    assert read.is_ancestor(adopted, started), (
        f"the adoption's commit {adopted} is not in the history of the exit run's start {started}")


# ---------------------------------------------------------------------------
# KPI 14: run from the kernel's orchestration skill and brief templates (DEC-537)
# ---------------------------------------------------------------------------

def test_exit_run_was_run_from_the_kernel_skill_and_brief_templates(report, read):
    where = "How the run was run"
    text = read.section(report, where)
    skill = read.paths_in(read.field(text, where, "Orchestration skill"))
    assert len(skill) == 1 and "governance/kernel/skills/orchestration/" in skill[0] and (read.ROOT / skill[0]).is_file(), (
        f"{where}: 'Orchestration skill' must name the kernel's skill file")
    templates = read.paths_in(read.field(text, where, "Brief templates"))
    assert templates and all(re.search(r"governance/kernel/templates/brief-[a-z-]+\.md$", path) and
                             (read.ROOT / path).is_file() for path in templates), (
        f"{where}: 'Brief templates' must name brief templates of the kernel")
    for kind in ("test-designer", "engineer"):
        assert any(path.endswith(f"brief-{kind}.md") for path in templates), f"{where}: brief-{kind}.md is not named"
    briefs = [path for path in read.paths_in(read.field(text, where, "Kept briefs"))
              if path.startswith(read.EVIDENCE_REL + "/")]
    assert briefs and all((read.ROOT / path).is_file() for path in briefs), (
        f"{where}: 'Kept briefs' must name at least one brief of the run, kept under {read.EVIDENCE_REL}/")
    assert read.norm(read.field(text, where, "Repository orchestrator prompt")).startswith("not used"), (
        f"{where}: 'Repository orchestrator prompt' must say 'not used'")


# ---------------------------------------------------------------------------
# The failure lines: a forbidden outcome or a share above 15 % is never a pass
# ---------------------------------------------------------------------------

def test_a_forbidden_outcome_or_a_share_above_15_percent_is_never_reported_as_a_pass(report, read):
    overall = read.field(report, "the head of the report", "Overall verdict").replace("*", "").strip()
    assert overall in ("MET", "NOT MET"), f"'Overall verdict' must be MET or NOT MET, not '{overall}'"
    rows = read.table(read.section(report, "Exit criteria"), "Exit criteria", "Criterion", "Verdict", "Evidence")
    verdict = {read.norm(row["criterion"]).split(" ")[0].rstrip(".:"): read.norm(row["verdict"]) for row in rows}
    unmet = sorted(name for name in read.CRITERIA if name != "5" and verdict.get(name) != "met")

    shares = {programme: _stated_share(row["share"], read) for programme, row in _share_rows(report, read).items()}
    if any(share is None or share > read.SHARE_LIMIT for share in shares.values()):
        assert verdict.get("4") != "met", f"criterion 4 is reported MET with the shares {shares}"
        unmet.append("4")

    text = read.section(report, "Forbidden outcomes")
    stated = read.norm(read.field(text, "Forbidden outcomes", "Forbidden outcomes"))
    breaches = read.load_json("mr3.json").get("breaches")
    if breaches:
        assert stated != "none" and verdict.get("3") != "met", "an MR-3 breach is kept and the report does not say so"
    if stated != "none":
        unmet.append("a forbidden outcome")
    if unmet:
        assert overall == "NOT MET", f"'Overall verdict' is MET although these are not met: {sorted(set(unmet))}"
