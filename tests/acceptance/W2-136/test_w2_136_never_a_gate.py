"""S10: never a gate elsewhere. No close, landing, claim, readiness or hook module imports or calls gov plan; only
gov launch's check (S9) and the CTO use it. Verify: a source scan of the tree under test (DEC-1052).

What is scanned (relative to the tree): close ``src/gov/close/**``; landing, the merge queue and the dispatcher that
lands and starts (``governance/project/orchestration/tools/merge_queue.py``, ``.../tools/dispatch/*.py|*.sh``); claim
``src/gov/tasks/claims.py``, ``src/gov/check/claims.py``; readiness ``src/gov/readiness/**``; hooks
``src/gov/hooks/**``, ``template/governance/kernel/hooks/*.py``, ``.claude/hooks/*.py``; and every module of
``src/gov`` outside ``src/gov/plan/`` and ``src/gov/launch/``."""

from __future__ import annotations

import pytest

import w2_136_support as support

CATEGORIES = {
    "close": ["src/gov/close/**/*.py"],
    "landing": ["governance/project/orchestration/tools/merge_queue.py",
                "governance/project/orchestration/tools/dispatch/*.py",
                "governance/project/orchestration/tools/dispatch/*.sh"],
    "claim": ["src/gov/tasks/claims.py", "src/gov/check/claims.py"],
    "readiness": ["src/gov/readiness/**/*.py"],
    "hooks": ["src/gov/hooks/**/*.py", "template/governance/kernel/hooks/*.py", ".claude/hooks/*.py"],
}


def _files(patterns):
    return sorted({p for pattern in patterns for p in support.TREE.glob(pattern) if p.is_file()})


def test_s10_premise_the_scan_finds_each_way_of_using_gov_plan():
    found = {
        "import gov.plan": "import gov.plan\n",
        "import gov.plan.command as c": "import gov.plan.command as c\n",
        "from gov.plan import x": "from gov.plan import x\n",
        "from gov.plan.engine import y": "from gov.plan.engine import y\n",
        "from gov import plan": "from gov import plan\n",
        "import_module": "import importlib\nimportlib.import_module('gov.plan.command')\n",
        "command list": "import subprocess\nsubprocess.run(['gov', 'plan', '--open'])\n",
        "command list by path": "run(['/home/u/.local/bin/gov', 'plan'])\n",
        "module command list": "run([sys.executable, '-m', 'gov.cli.main', 'plan'])\n",
        "command string": "os.system('gov plan --open --ready x')\n",
    }
    for name, text in found.items():
        assert support.uses_plan_text(text), name
    clean = {
        "a docstring": '"""Never calls gov plan (S10)."""\n',
        "a planner word": "import gov.planner\nfrom gov.tasks import planning\nx = 'gov planning'\n",
        "another command": "subprocess.run(['gov', 'close', 'plan'])\n",
    }
    for name, text in clean.items():
        assert not support.uses_plan_text(text), name


@pytest.mark.parametrize("category", list(CATEGORIES))
def test_s10_no_module_of_the_category_imports_or_calls_gov_plan(category):
    files = _files(CATEGORIES[category])
    assert files, f"nothing found for {category}: the scan would prove nothing"
    used = {str(p.relative_to(support.TREE)): hits for p in files if (hits := support.uses_plan(p))}
    assert used == {}, used


def test_s10_no_module_of_gov_outside_plan_and_launch_imports_or_calls_gov_plan():
    allowed = (support.SRC / "gov" / "plan", support.SRC / "gov" / "launch")
    files = [p for p in _files(["src/gov/**/*.py"]) if not any(p.is_relative_to(a) for a in allowed)]
    assert len(files) > 100, len(files)
    used = {str(p.relative_to(support.TREE)): hits for p in files if (hits := support.uses_plan(p))}
    assert used == {}, used
