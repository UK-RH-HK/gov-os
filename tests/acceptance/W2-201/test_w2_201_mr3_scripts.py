"""Fix MR-3 (DEC-1246 (3)(b)): the start scripts match the table.

``python3 -m gov.launch.role_table --scripts <dir>`` prints each of ``start_lead.sh``, ``start_cto.sh``,
``start_audit.sh`` with its ``--model`` and ``--effort`` beside the table's row (``lead``, ``orchestrator``,
``audit-wide``); exit 0 when they agree, 1 when not. The scripts are planted as copies in the forms the CTO's have.
"""

from __future__ import annotations

import pytest

import w2_201_mr_support as m


@pytest.fixture()
def root(tmp_path):
    root = tmp_path / "root"
    m.write_table(root)
    return root


def _run(root, scripts):
    return m.python_m(["--scripts", scripts], root)


def _fails(done, *words):
    text = m.said(done)
    assert done.returncode == 1, f"exit {done.returncode}\n{text}"
    missing = [w for w in words if w.lower() not in text.lower()]
    assert not missing, f"the output does not name {missing}\n{text}"


def test_mr3_scripts_that_agree_with_the_table_print_each_line_and_exit_0(tmp_path, root):
    """Red on the base: ``gov.launch.role_table`` does not exist."""
    done = _run(root, m.plant_scripts(tmp_path / "scripts"))
    assert done.returncode == 0, m.said(done)
    for name in m.SCRIPTS:
        assert name in done.stdout, done.stdout
    assert "claude-opus-5-5" in done.stdout and "claude-sonnet-5-5" in done.stdout


def test_mr3_check_scripts_returns_lines_and_ok(tmp_path, root):
    from gov.launch import role_table
    lines, ok = role_table.check_scripts(m.plant_scripts(tmp_path / "scripts"), root)
    assert ok is True and len(lines) >= 3
    lines, ok = role_table.check_scripts(m.plant_scripts(tmp_path / "bad", start_cto=("--effort high", "--effort medium")), root)
    assert ok is False


def test_mr3_a_cto_script_with_effort_medium_is_reported_naming_it_and_the_tables_value(tmp_path, root):
    done = _run(root, m.plant_scripts(tmp_path / "scripts", start_cto=("--effort high", "--effort medium")))
    _fails(done, "start_cto.sh", "medium", "high")


def test_mr3_an_audit_script_naming_sonnet_for_the_wide_audit_is_reported(tmp_path, root):
    done = _run(root, m.plant_scripts(tmp_path / "scripts", start_audit=("claude-opus-5-5", "claude-sonnet-5-5")))
    _fails(done, "start_audit.sh", "claude-sonnet-5-5", "claude-opus-5-5")


def test_mr3_a_changed_table_row_is_reported_against_the_unchanged_script(tmp_path):
    m.write_table(tmp_path / "root", lead=(m.SONNET, "high"))
    _fails(_run(tmp_path / "root", m.plant_scripts(tmp_path / "scripts")), "start_lead.sh", "medium", "high")


def test_mr3_an_effort_default_in_the_environment_form_is_read_as_its_value(tmp_path, root):
    ok = _run(root, m.plant_scripts(tmp_path / "ok"))
    assert ok.returncode == 0, m.said(ok)
    bad = m.plant_scripts(tmp_path / "bad", start_lead=("${EFFORT:-medium}\" --permission", "${EFFORT:-high}\" --permission"))
    _fails(_run(root, bad), "start_lead.sh", "high", "medium")


def test_mr3_a_cto_script_that_still_calls_the_substitution_reader_is_reported(tmp_path, root):
    text = m.CTO.replace("tmux new-session", 'M=$(python3 "$R/tools/read_model_substitution.py")\ntmux new-session')
    _fails(_run(root, m.plant_scripts(tmp_path / "scripts", start_cto=text)), "start_cto.sh", "substitution")


@pytest.mark.parametrize("flag", ["--model claude-opus-5-5 ", "--effort high "])
@pytest.mark.parametrize("script", ["start_cto", "start_audit"])
def test_mr3_a_script_with_no_model_or_no_effort_is_reported_not_skipped(tmp_path, root, script, flag):
    _fails(_run(root, m.plant_scripts(tmp_path / "scripts", **{script: (flag, "")})), f"{script}.sh", flag.split()[0])


def test_mr3_the_real_three_scripts_agree_with_this_repositorys_table():
    """Red on the base: no table, no module. Skipped where the CTO's folder is absent."""
    from pathlib import Path
    real = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools")
    if not all((real / name).is_file() for name in m.SCRIPTS):
        pytest.skip("the CTO's start scripts are not on this machine")
    done = m.python_m(["--scripts", real], m.REPO)
    assert done.returncode == 0, m.said(done)
