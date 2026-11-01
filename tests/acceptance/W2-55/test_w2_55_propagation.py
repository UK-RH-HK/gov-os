"""KPI 5 and failure 3: supersession propagates (S3, DEC-866).

``gov.decisions.check_propagation(root)`` and ``python3 -m gov.decisions.propagation`` find each line of a searched
place (``tests/``, ``src/``, ``template/``, the prompts, the briefs, the path map, a ticket not closed) that cites a
superseded entry by id, in a file that does not cite its successor, or holds a recorded value of a superseded or
changed entry; a kept place with its reason gives none. Its first fixture is the sweep of 2026-10-20
(``governance/project/orchestration/packages/SWEEP-2026-10-20.md``): W1-49's two window cases (DEC-636 and DEC-665
against DEC-838) and W2-59's three earlier cases (DEC-605 against DEC-822 and DEC-835), planted from the sweep's
description.
"""

from __future__ import annotations

import pytest

import w2_55_support as s

# --------------------------------------------------------------------------
# The planted harbour: one superseded pair, one changed pair, a place of every searched kind
# --------------------------------------------------------------------------

OLD, NEW, CHANGED, CHANGER = "DEC-201", "DEC-202", "DEC-301", "DEC-302"
VALUE, CHANGED_VALUE = "LANTERN_LIMIT = 7", "BELL_MODE_SINGLE"
KEPT_ON_OLD = "tests/acceptance/kept/test_kept_old.py"
KEPT_ON_NEW = "src/harbour/legacy.py"

REGISTER_TEXT = s.register(
    s.entry(OLD, "The lantern limit", f"SUPERSEDED by {NEW} · **Basis:** OWNER",
            s.tags("plan", "repository", "none"),
            more=[f'- **Values:** "{VALUE}"',
                  f"- **Kept:** {KEPT_ON_OLD} — the record of how the old limit was tested"],
            body="At most seven lanterns are lit."),
    s.entry(NEW, "The lantern limit, raised", f"ACCEPTED · **Basis:** OWNER · **Supersedes:** {OLD}",
            s.tags("plan", "repository", s.PROJECT_PLACE),
            more=[f"- **Kept:** {KEPT_ON_NEW} — the legacy reader keeps the old limit for the old logs"],
            body="At most twelve lanterns are lit."),
    s.entry(CHANGED, "The bell", f"ACCEPTED · **Basis:** OWNER · **Changed by:** {CHANGER}",
            s.tags("roles", "kernel", s.KERNEL_PLACE), more=[f'- **Values:** "{CHANGED_VALUE}"'],
            body="The bell rings once, at noon, from the tower."),
    s.entry(CHANGER, "The bell rings twice", f"ACCEPTED · **Basis:** OWNER · **Changes:** {CHANGED}",
            s.tags("roles", "kernel", s.KERNEL_PLACE), body="The bell rings twice; the rest of DEC-301 stands."),
    s.entry("DEC-401", "The tide gauge", tags_line=s.tags("records", "kernel", s.KERNEL_PLACE),
            body="The tide gauge is read at dawn."),
)


def ticket(ticket_id, status, kpi):
    return (f"---\nid: {ticket_id}\nstatus: {status}\ntype: task\ntitle: 'A harbour ticket'\n"
            f"kpis:\n  success:\n  - '{kpi}'\n---\n# {ticket_id}\n\nBody.\n")


PATH_MAP_COMMENT = f"lanterns: {OLD} holds the limit"

# place -> (its text, the needle on the line that enforces, the old entry, the one that replaced or changed it)
ENFORCING = {
    "tests/acceptance/HARB/test_lanterns.py": (
        f'"""The lantern cases."""\n\n\ndef test_lanterns():\n    # {OLD}: at most seven lanterns\n'
        f"    assert 7 == 7\n", f"# {OLD}:", OLD, NEW),
    "src/harbour/lanterns.py": (f'"""Lanterns."""\n\n{VALUE}\n', VALUE, OLD, NEW),
    "template/governance/kernel/skills/lanterns/SKILL.md": (
        f"# The lantern skill\n\nLight at most seven lanterns ({OLD}).\n", f"({OLD})", OLD, NEW),
    "governance/project/briefs/LEAD-lanterns.md": (
        f"# The lantern brief\n\nEvery lead sets {VALUE} in the harbour.\n", VALUE, OLD, NEW),
    ".tickets/HARB-0002.md": (ticket("HARB-0002", "open", f"Seven lanterns at most [{OLD}]"), f"[{OLD}]", OLD, NEW),
    s.PROMPT_PLACE: (f"# The orchestrator's prompt\n\nHold the lantern limit of {OLD}.\n", f"of {OLD}.", OLD, NEW),
    "src/harbour/bells.py": (f'"""Bells."""\n\nMODE = "{CHANGED_VALUE}"\n', CHANGED_VALUE, CHANGED, CHANGER),
}
KINDS = {
    "tests/acceptance/HARB/test_lanterns.py": "a test, by id",
    "src/harbour/lanterns.py": "code, by value",
    "template/governance/kernel/skills/lanterns/SKILL.md": "a skill, by id",
    "governance/project/briefs/LEAD-lanterns.md": "a brief, by value",
    ".tickets/HARB-0002.md": "a non-closed ticket's KPI, by id",
    s.PROMPT_PLACE: "the prompt, by id",
    "src/harbour/bells.py": "a changed entry's value",
}

QUIET = {
    ".tickets/HARB-0003.md": ticket("HARB-0003", "closed", f"Seven lanterns at most [{OLD}], {VALUE}"),
    "docs/notes/lanterns.md": f"# Notes\n\n{OLD} set the limit: {VALUE}.\n",
    "governance/project/orchestration/lanterns-log.md": f"# A record\n\n{OLD} set {VALUE}.\n",
    "tests/acceptance/HARB/test_updated.py": f'"""Follows {NEW}, which replaced {OLD}."""\n',
    KEPT_ON_OLD: f'"""The old limit, {OLD}."""\n\n{VALUE}\n',
    KEPT_ON_NEW: f'"""The legacy reader."""\n\n{VALUE}\n',
    "tests/acceptance/HARB/test_bells.py": f'"""The bell cases ({CHANGED})."""\n',
    "tests/acceptance/HARB/test_whole_word.py": '"""DEC-2010 and DEC-20 are other entries."""\n',
}
QUIET_WHY = {
    ".tickets/HARB-0003.md": "a closed ticket is a record, not searched",
    "docs/notes/lanterns.md": "docs/ is not searched",
    "governance/project/orchestration/lanterns-log.md": "the orchestration record is not searched",
    "tests/acceptance/HARB/test_updated.py": "the file cites the successor",
    KEPT_ON_OLD: "kept, with its reason on the old entry",
    KEPT_ON_NEW: "kept, with its reason on the new entry",
    "tests/acceptance/HARB/test_bells.py": "a changed entry's id alone is no finding",
    "tests/acceptance/HARB/test_whole_word.py": "an id is cited as a whole word only",
}
LOOSE = "tests/acceptance/HARB/test_loose.py"   # in the working tree only: HEAD does not hold it


@pytest.fixture(scope="module")
def harbour(api, tmp_path_factory):
    files = {rel: text for rel, (text, *_) in ENFORCING.items()}
    files.update(QUIET)
    project = s.build_project(tmp_path_factory.mktemp("w2-55-propagation") / "repo", REGISTER_TEXT, files,
                              path_map_comment=PATH_MAP_COMMENT)
    project.write(LOOSE, f'"""Not committed: {OLD}, {VALUE}."""\n')
    return lazy_findings(api, project)


def lazy_findings(api, project):
    """``() -> (project, findings)``: the check is called in the case, once, so a refusal fails the case."""
    memo = {}

    def found():
        if "found" not in memo:
            memo["found"] = api.findings(project.root, "check_propagation")
        return project, memo["found"]

    return found


def finding_at(found, rel, line, old, new):
    return [f for f in found if f["code"] == s.ENFORCES and f["paths"] == [rel] and f["ids"][:1] == [old]
            and (new is None or f["ids"] == [old, new]) and s.names_line(f["message"], rel, line)]


@pytest.mark.parametrize("rel", list(ENFORCING), ids=[KINDS[rel] for rel in ENFORCING])
def test_a_place_that_enforces_an_old_decision_is_found_naming_both_and_the_line(harbour, rel):
    project, found = harbour()
    text, needle, old, new = ENFORCING[rel]
    line = s.line_number(text, needle)
    hits = finding_at(found, rel, line, old, new)
    assert hits, (f"{KINDS[rel]}: no {s.ENFORCES} finding with ids [{old}, {new}], paths [{rel}] and line {line} "
                  f"in its message:\n{s.show(found)}")
    for finding in hits:
        assert old in finding["message"] and new in finding["message"] and rel in finding["message"], \
            f"the message does not name both decisions and the place: {finding['message']!r}"


def test_the_path_map_that_enforces_an_old_decision_is_found(harbour):
    project, found = harbour()
    text = (project.root / s.PATH_MAP_REL).read_text(encoding="utf-8")
    line = s.line_number(text, PATH_MAP_COMMENT)
    assert finding_at(found, s.PATH_MAP_REL, line, OLD, NEW), \
        f"the path map's line {line} citing {OLD} is not found:\n{s.show(found)}"


@pytest.mark.parametrize("rel", list(QUIET), ids=[QUIET_WHY[rel] for rel in QUIET])
def test_a_place_that_does_not_enforce_gives_no_finding(harbour, rel):
    project, found = harbour()
    wrong = [f for f in found if rel in f["paths"]]
    assert not wrong, f"{QUIET_WHY[rel]}, yet:\n{s.show(wrong)}"


def test_the_register_and_the_working_tree_are_not_searched(harbour):
    project, found = harbour()
    wrong = [f for f in found if s.REGISTER in f["paths"] or LOOSE in f["paths"]]
    assert not wrong, f"the register or a file HEAD does not hold gave findings:\n{s.show(wrong)}"
    assert found, "the propagation check found nothing in the planted harbour"


def test_the_propagation_command_exits_1_and_names_the_place(api, harbour):
    project, _ = harbour()
    answer = api.module(project.root, "gov.decisions.propagation")
    out = answer.stdout + answer.stderr
    assert answer.returncode == 1, answer.describe()
    assert s.ENFORCES in out and "src/harbour/lanterns.py" in out and OLD in out and NEW in out, \
        f"the command's output does not name the finding, the place and both decisions\n{answer.describe()}"


def test_a_project_with_nothing_enforcing_an_old_decision_passes(api, tmp_path):
    files = {"tests/acceptance/HARB/test_updated.py": QUIET["tests/acceptance/HARB/test_updated.py"],
             "tests/acceptance/HARB/test_bells.py": QUIET["tests/acceptance/HARB/test_bells.py"]}
    project = s.build_project(tmp_path / "repo", REGISTER_TEXT, files)
    found = api.findings(project.root, "check_propagation")
    assert found == [], f"nothing enforces an old decision, yet:\n{s.show(found)}"
    answer = api.module(project.root, "gov.decisions.propagation")
    assert answer.returncode == 0, answer.describe()


# --------------------------------------------------------------------------
# The first fixture: the sweep of 2026-10-20, reproduced from its description
# --------------------------------------------------------------------------

SWEEP_REGISTER = s.register(
    s.entry("DEC-605", "P-40: `gov` is installed for this user, by the owner",
            "ACCEPTED (owner, 2026-10-10) · **Basis:** OWNER · **Changed by:** DEC-822, DEC-835",
            s.tags("release", "repository", s.PROJECT_PLACE),
            more=['- **Values:** "PYTHONPATH=judged/src"',
                  "- **Kept:** tests/acceptance/W1-26/test_w1_26_dec436.py — they pass under W2-59's change; "
                  "W2-59's lead re-checks them at its merge-back"]),
    s.entry("DEC-636", "P-44, env block: the auto-compact entry moves to the owner's user-level settings",
            "SUPERSEDED by DEC-838 (2026-10-19; marked by DEC-866) · **Basis:** OWNER",
            s.tags("launch", "kernel", "none"), more=['- **Values:** "300_000", "300000", "LEAD_CHECKPOINT"']),
    s.entry("DEC-665", "The six red cases on the integration branch",
            "ACCEPTED (owner, 2026-10-13) · **Basis:** the orchestrator's finding · **Changed by:** DEC-838",
            s.tags("checks", "repository", s.PROJECT_PLACE), more=['- **Values:** "300_000", "300000"']),
    s.entry("DEC-822", "P-S1 (a): this repository is governed by a pinned release, in two steps",
            "ACCEPTED (owner, 2026-10-19) · **Basis:** P-S1 · **Changes:** DEC-605",
            s.tags("release", "repository", s.PROJECT_PLACE)),
    s.entry("DEC-835", "W2-59's scope is approved, with the two packaging gaps",
            "ACCEPTED (owner, 2026-10-19) · **Basis:** OWNER · **Changes:** DEC-605",
            s.tags("release", "repository", s.PROJECT_PLACE)),
    s.entry("DEC-838", "Context windows: every session uses its model's full window; usage is the limit",
            "ACCEPTED (owner, 2026-10-19; standing) · **Basis:** OWNER · **Supersedes:** DEC-636 · "
            "**Changes:** DEC-665", s.tags("launch", "kernel", s.KERNEL_PLACE)),
)

W1_49_THRESHOLD = "tests/acceptance/W1-49/test_w1_49_threshold.py"
W1_49_LIVE = "tests/acceptance/W1-49/test_w1_49_live_session.py"
W1_26 = "tests/acceptance/W1-26/test_w1_26_planted_defects.py"
W1_22 = "tests/acceptance/W1-22/test_w1_22_canaries.py"
W1_26_KEPT = "tests/acceptance/W1-26/test_w1_26_dec436.py"
BRIEF_LEAD = "template/governance/kernel/templates/brief-lead.md"
CLOSED_W1 = ".tickets/DAEO-32n6.md"

SWEEP_FILES = {
    W1_49_THRESHOLD: ('"""W1-49: the compaction threshold (DEC-636)."""\n\n\n'
                      "def test_the_window_is_set_for_every_session(window):\n"
                      "    assert window == 300000\n"),
    W1_49_LIVE: ('"""W1-49: a live session (DEC-665)."""\n\n\n'
                 "def test_a_live_session_compacts_at_the_window(env):\n"
                 '    assert int(env["CLAUDE_CODE_AUTO_COMPACT_WINDOW"]) == 300000\n'),
    W1_26: ('"""W1-26: planted defects."""\n\n\n'
            "def test_planted_authority_defect_decision_checker_exception_not_swallowed(run):\n"
            '    judged = run(env="PYTHONPATH=judged/src")  # the judge imports the judged code (DEC-605)\n'
            "    assert judged.returncode == 1\n"),
    W1_22: ('"""W1-22: canaries."""\n\n\n'
            "class TestCanaryRunner:\n\n"
            "    def test_runner_returns_per_index_results(self, run):\n"
            '        assert run(path="PYTHONPATH=judged/src#results")\n\n'
            "    def test_runner_reports_a_failing_canary(self, run):\n"
            '        assert run(path="PYTHONPATH=judged/src#failing")\n'),
    W1_26_KEPT: '"""W1-26: DEC-436 cases."""\n\nENV = "PYTHONPATH=judged/src"\n',
    BRIEF_LEAD: "# The lead's brief\n\nWrite LEAD_CHECKPOINT when the session reaches its window.\n",
    CLOSED_W1: ("---\nid: DAEO-32n6\nstatus: closed\ntype: task\ntitle: 'A closed Wave 1 ticket'\nkpis:\n"
                "  success:\n  - 'Every session compacts at about 300000 tokens'\n---\n# DAEO-32n6\n"),
}

# (place, needle, old, the entries that may be named as the one that replaced or changed it)
SWEEP_CASES = {
    "W1-49 threshold (DEC-636 against DEC-838)": (W1_49_THRESHOLD, "== 300000", "DEC-636", {"DEC-838"}),
    "W1-49 live session (DEC-665 against DEC-838)": (W1_49_LIVE, "== 300000", "DEC-665", {"DEC-838"}),
    "W1-26 planted authority defect (DEC-605)": (W1_26, "PYTHONPATH=judged/src", "DEC-605", {"DEC-822", "DEC-835"}),
    "W1-22 TestCanaryRunner, first (DEC-605)": (W1_22, "judged/src#results", "DEC-605", {"DEC-822", "DEC-835"}),
    "W1-22 TestCanaryRunner, second (DEC-605)": (W1_22, "judged/src#failing", "DEC-605", {"DEC-822", "DEC-835"}),
    "LEAD_CHECKPOINT taught in a template (DEC-636)": (BRIEF_LEAD, "LEAD_CHECKPOINT", "DEC-636", {"DEC-838"}),
}


@pytest.fixture(scope="module")
def sweep(api, tmp_path_factory):
    project = s.build_project(tmp_path_factory.mktemp("w2-55-sweep") / "repo", SWEEP_REGISTER, SWEEP_FILES)
    found = lazy_findings(api, project)
    return lambda: found()[1]


@pytest.mark.parametrize("case", list(SWEEP_CASES))
def test_the_sweep_of_2026_10_20_is_found(sweep, case):
    sweep = sweep()
    rel, needle, old, new = SWEEP_CASES[case]
    line = s.line_number(SWEEP_FILES[rel], needle)
    hits = [f for f in finding_at(sweep, rel, line, old, None) if len(f["ids"]) == 2 and f["ids"][1] in new]
    assert hits, f"{case}: no {s.ENFORCES} finding [{old}, one of {sorted(new)}] at {rel}:{line}:\n{s.show(sweep)}"


@pytest.mark.parametrize("rel", [W1_26_KEPT, CLOSED_W1], ids=["kept with its reason", "a closed ticket"])
def test_the_sweeps_kept_and_closed_places_give_no_finding(sweep, rel):
    sweep = sweep()
    wrong = [f for f in sweep if rel in f["paths"]]
    assert not wrong, f"{rel} gave findings:\n{s.show(wrong)}"


def test_a_changed_entrys_id_alone_in_the_sweep_is_no_finding(sweep):
    sweep = sweep()
    # W1-49's live case cites DEC-665 (changed, not superseded) on its first line, with no value beside it
    line = s.line_number(SWEEP_FILES[W1_49_LIVE], "(DEC-665)")
    wrong = finding_at(sweep, W1_49_LIVE, line, "DEC-665", None)
    assert not wrong, f"the id of a changed entry alone gave a finding:\n{s.show(wrong)}"
