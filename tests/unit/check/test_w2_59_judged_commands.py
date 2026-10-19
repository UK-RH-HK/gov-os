"""Builder tests for W2-59: a declared check runs with the judge's own interpreter and package (DEC-822 item 3).

Regression evidence only (DEC-136); the acceptance tests prove it from an installed wheel.
"""
from __future__ import annotations

import os
import shlex
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

import gov  # noqa: E402
from gov.check import runner  # noqa: E402


def test_a_leading_python3_or_gov_is_the_judge_s_own_interpreter():
    python = shlex.quote(sys.executable)
    assert runner._judged("python3 -m gov.check.schema") == f"{python} -P -m gov.check.schema"
    assert runner._judged("gov checkpoint --resume --json") == f"{python} -P -m gov.cli.main checkpoint --resume --json"


def test_any_other_command_is_left_as_declared():
    assert runner._judged("openspec validate --strict") == "openspec validate --strict"
    assert runner._judged("python3.12 -m x") == "python3.12 -m x"
    assert runner._judged("governor --x") == "governor --x"


def test_the_check_gets_no_pythonpath_naming_the_project(tmp_path, monkeypatch):
    monkeypatch.delenv("PYTHONPATH", raising=False)
    code, out, _ = runner._run_command('python3 -c "import os; print(os.environ.get(\'PYTHONPATH\', \'\'))"', tmp_path)
    assert code == 0 and str(tmp_path) not in out


def test_a_gov_package_at_the_project_s_root_is_not_imported(tmp_path, monkeypatch):
    (tmp_path / "gov").mkdir()
    (tmp_path / "gov" / "__init__.py").write_text("", encoding="utf-8")
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join([str(Path(gov.__file__).parents[1])]))
    code, out, _ = runner._run_command('python3 -c "import gov; print(gov.__file__)"', tmp_path)
    assert code == 0 and out.strip() == gov.__file__
