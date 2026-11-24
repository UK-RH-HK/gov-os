"""Fix MR-1 (models and effort by role, from one table, held by code; DEC-1246 (3)(b)): the table in one file.

``governance/project/role-table.yaml`` (byte-equal kit copy), read by ``gov launch`` (record ``model_source`` and
``effort_source`` ``role table``), checked against the role files' ``Launch default`` lines and against owner-less row
changes by ``gov.launch.role_table``. Read: the stand-in CLI's arguments, the launch record, the module as a function
and as ``python3 -m gov.launch.role_table`` in a planted root.
"""

from __future__ import annotations

import pytest

import w2_201_mr_support as m
import w2_201_support as k
import w2_201_x_support as x

s, b = k.s, k.b
LEAD_TK = "DAEO-ldmr"
CALLER = {"GOV_TICKET": x.CALLER_TICKET}
WORKERS = (k.ENGINEER, k.TEST_DESIGNER, k.AUDITOR, k.RESEARCH, k.PRODUCT_SPEC)


@pytest.fixture(autouse=True)
def _no_criticality_file(request):
    """The MR-1 cases launch on a project with no ``criticality.yaml`` (W2-184 interface 1.4: such a launch reads the role
    file's default line), so that what they see comes from the table and not from MR-2's file form."""
    if "project" in request.fixturenames:
        s.drop_criticality(request.getfixturevalue("project"))


def _line(result, model, effort):
    b.assert_launched(result)
    assert {"--model": result.values("--model"), "--effort": result.values("--effort")} == {
        "--model": [model], "--effort": [effort]}, f"the launch line is not {model}, {effort}\n{result.args}"


def _sources(result):
    got = k.record_values(result, "model_source", "effort_source")
    assert got == {"model_source": "role table", "effort_source": "role table"}, f"the record says {got}"


# --------------------------------------------------------------------------------------------------------------------
# The file, its kit copy and its values
# --------------------------------------------------------------------------------------------------------------------

def test_mr1_the_table_holds_the_ten_rows_with_the_values_that_stand():
    """Red on the base: there is no ``governance/project/role-table.yaml``."""
    import yaml
    path = m.REPO / m.TABLE_REL
    assert path.is_file(), f"{m.TABLE_REL} is absent"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data.get("version") == 1 and set(data) == {"version", "rows"}, f"the keys are {sorted(data)}"
    rows = {row["role"]: row for row in data["rows"]}
    assert [row["role"] for row in data["rows"]] == list(m.ROLES) or sorted(rows) == sorted(m.ROLES), sorted(rows)
    assert len(rows) == len(data["rows"]) == 10
    got = {role: (row["model"], row["effort"]) for role, row in rows.items()}
    assert got == m.VALUES, f"the values changed: {got}"
    assert all(set(row) == {"role", "model", "effort", "decided"} and str(row["decided"]).strip() for row in rows.values())


def test_mr1_the_kit_copy_is_byte_equal():
    """Red on the base: the kit holds no copy."""
    kit = m.REPO / m.KIT_TABLE_REL
    assert kit.is_file(), f"{m.KIT_TABLE_REL} is absent"
    assert kit.read_bytes() == (m.REPO / m.TABLE_REL).read_bytes()


def test_mr1_each_role_file_of_this_repository_equals_its_row():
    """Red on the base: ``gov.launch.role_table`` does not exist."""
    from gov.launch import role_table
    assert role_table.check_roles(m.REPO) == []
    done = m.python_m(["--roles"], m.REPO)
    assert done.returncode == 0, m.said(done)


def test_mr1_load_gives_each_role_its_model_effort_and_decision():
    from gov.launch import role_table
    got = role_table.load(m.REPO)
    assert {role: (v["model"], v["effort"]) for role, v in got.items()} == m.VALUES
    assert all(str(v["decided"]).strip() for v in got.values())


# --------------------------------------------------------------------------------------------------------------------
# gov launch reads the row
# --------------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("effort", ["high", "low", "xhigh"])
@pytest.mark.parametrize("role", WORKERS)
def test_mr1_a_worker_launch_takes_the_planted_row_and_a_changed_row_reaches_the_stub(project, launch, role, effort):
    """Red on the base: the launcher knows no table (the fixture's role-file lines and class tables decide)."""
    m.write_table(project, **{role.replace("-", "__"): (m.SONNET, effort)})
    tk = s.ticket(project, role, "C2")
    result = launch(role, tk)
    _line(result, m.SONNET, effort)
    _sources(result)


def test_mr1_the_qa_engineer_takes_its_row(project, launch):
    k.plant_real_role(project, k.QA)
    m.write_table(project, qa_engineer=(m.SONNET, "low"))
    tk = s.ticket(project, k.ENGINEER, "C2")
    result = launch(k.QA, tk)
    _line(result, m.SONNET, "low")
    _sources(result)


@pytest.mark.parametrize("role", x.LEAD_ROLES)
@pytest.mark.parametrize("kind", ["feature", "fix", "chore"])
def test_mr1_a_ticket_fix_or_chore_lead_takes_the_lead_row_not_the_orchestrator_row(sandbox, cli, project, role, kind):
    """Red on the base: the launcher gives a lead its own constants (medium)."""
    x.ticket(project, x.ENGINEER, "C2", "closed", tk="DAEO-ldfx")
    s.ticket(project, x.ENGINEER, "C2", tk=LEAD_TK)
    b.write(project / x.READY_REL, f"# batch 1\nW2-201-ready {LEAD_TK} brief.md log.json\n")
    m.write_table(project, lead=(m.SONNET, "low"), orchestrator=(m.OPUS, "xhigh"))
    x.commit(project, "the leads' tickets, the ready list and the table")
    head = {"feature": (LEAD_TK,), "fix": ("DAEO-ldfx", "--fix", x.FIX_LINE), "chore": ("--chore", x.CHORE_LINE)}[kind]
    result = x.launched(x.launch(sandbox, cli, role, *head, extra_env=CALLER))
    x.assert_line(result, m.SONNET, "low")
    _sources(result)


def test_mr1_with_no_table_file_the_role_file_default_line_is_used_as_before(project, launch):
    """Guard (green on the base): an adopted repository not yet updated."""
    tk = s.ticket(project, k.ENGINEER, "C2")
    result = launch(k.ENGINEER, tk)
    b.assert_launched(result)
    assert result.values("--effort") == ["medium"]  # the fixture role file's own default line
    assert k.record_values(result, "model_source")["model_source"] != "role table"


# --------------------------------------------------------------------------------------------------------------------
# A table that cannot be trusted refuses the launch (fail closed)
# --------------------------------------------------------------------------------------------------------------------

def _row_text(**changes):
    return m.table_text(**changes)


def _twice():
    import yaml
    data = m.table_data()
    data["rows"].append({"role": "engineer", "model": m.SONNET, "effort": "low", "decided": "DEC-1"})
    return yaml.safe_dump(data, sort_keys=False)


BAD = {
    "unreadable": "rows: [unclosed\n  - {role: engineer",
    "not-a-map": "- engineer\n- research\n",
    "a-role-twice": _twice(),
    "fable": _row_text(engineer=("claude-fable-5-2", "high")),
    "fable-alias": _row_text(research=("fable", "high")),
    "unknown-model": _row_text(engineer=("gpt-9-turbo", "high")),
    "unknown-effort": _row_text(engineer=(m.SONNET, "ultra")),
}


@pytest.mark.parametrize("case", sorted(BAD))
def test_mr1_a_table_that_cannot_be_read_or_names_fable_or_an_unknown_value_refuses_the_launch(project, launch, case):
    """Red on the base: the launcher does not read the table, so the launch succeeds."""
    m.write_table(project, text=BAD[case])
    tk = s.ticket(project, k.ENGINEER, "C2")
    s.refused(launch(k.ENGINEER, tk))


@pytest.mark.parametrize("case", sorted(BAD))
def test_mr1_load_refuses_the_same_tables_with_launch_refused(tmp_path, case):
    from gov.cli.errors import GovError
    from gov.launch import role_table
    m.write_table(tmp_path, text=BAD[case])
    with pytest.raises(GovError) as caught:
        role_table.load(tmp_path)
    assert caught.value.code == "LAUNCH_REFUSED"


# --------------------------------------------------------------------------------------------------------------------
# Failure line: a role file that disagrees with the table
# --------------------------------------------------------------------------------------------------------------------

def test_mr1_a_role_file_saying_medium_for_the_engineer_while_the_table_says_high_is_reported(tmp_path):
    from gov.launch import role_table
    tree = m.roles_tree(tmp_path, engineer_line="- **Launch default:** model claude-sonnet-5-5, effort medium")
    found = role_table.check_roles(tree)
    assert found, "the check reported nothing"
    text = " ".join(map(str, found)).lower()
    assert "engineer" in text and "medium" in text and "high" in text, text
    done = m.python_m(["--roles"], tree)
    assert done.returncode == 1 and "engineer" in m.said(done).lower(), m.said(done)


def test_mr1_the_matching_role_files_pass_the_check_in_a_planted_root(tmp_path):
    from gov.launch import role_table
    tree = m.roles_tree(tmp_path)
    assert role_table.check_roles(tree) == []
    assert m.python_m(["--roles"], tree).returncode == 0


def test_mr1_a_role_file_cannot_launch_an_effort_other_than_the_tables(project, launch):
    """Red on the base: the fixture's role file says medium and the launcher uses it."""
    s.write_role(project, k.ENGINEER, table=None, default=(m.SONNET, "medium"))
    m.write_table(project)
    tk = s.ticket(project, k.ENGINEER, "C2")
    result = launch(k.ENGINEER, tk)
    _line(result, m.SONNET, "high")
    _sources(result)


# --------------------------------------------------------------------------------------------------------------------
# A row changed without the owner's trailer is reported
# --------------------------------------------------------------------------------------------------------------------

def test_mr1_a_commit_that_edits_a_row_with_no_trailer_is_reported_with_role_old_and_new(tmp_path):
    from gov.launch import role_table
    root = m.repo_with_table(tmp_path)
    m.edit_row(root, "engineer", "effort", "xhigh")
    found = role_table.check_range(root, "HEAD~1..HEAD")
    assert len(found) == 1, found
    assert {key: found[0][key] for key in ("role", "field", "old", "new")} == {
        "role": "engineer", "field": "effort", "old": "high", "new": "xhigh"}
    done = m.python_m(["--check", "HEAD~1..HEAD"], root)
    assert done.returncode == 1, m.said(done)
    assert all(word in m.said(done) for word in ("engineer", "high", "xhigh")), m.said(done)


def test_mr1_a_commit_that_edits_a_row_with_the_owner_trailer_is_not_reported(tmp_path):
    from gov.launch import role_table
    root = m.repo_with_table(tmp_path)
    m.edit_row(root, "engineer", "effort", "xhigh", trailer="Decided-by: owner")
    assert role_table.check_range(root, "HEAD~1..HEAD") == []
    assert m.python_m(["--check", "HEAD~1..HEAD"], root).returncode == 0


def test_mr1_a_range_that_does_not_touch_the_table_reports_nothing(tmp_path):
    from gov.launch import role_table
    root = m.repo_with_table(tmp_path)
    (root / "note.txt").write_text("x\n", encoding="utf-8")
    m.git(root, "add", "-A")
    m.git(root, "commit", "-q", "-m", "a note")
    assert role_table.check_range(root, "HEAD~1..HEAD") == []
    assert m.python_m(["--check", "HEAD~1..HEAD"], root).returncode == 0


def test_mr1_in_a_range_of_two_commits_only_the_one_without_the_trailer_is_reported(tmp_path):
    from gov.launch import role_table
    root = m.repo_with_table(tmp_path)
    m.edit_row(root, "research", "effort", "low", trailer="Decided-by: owner")
    m.edit_row(root, "qa-engineer", "effort", "low")
    found = role_table.check_range(root, "HEAD~2..HEAD")
    assert [(f["role"], f["old"], f["new"]) for f in found] == [("qa-engineer", "high", "low")]
