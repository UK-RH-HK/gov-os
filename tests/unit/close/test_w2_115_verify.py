"""W2-115 S13: ``gov close --verify <ticket>``, a lead's whole verify on today's serial phase."""
from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET

from gov.close import attribution, command

from .test_w2_115_support import OWN_SUITE, TICKET, change, project

CONFIG = {"path-map.yaml": {"close_workers": 1}}
SERIAL_LIST = "tests/acceptance/serial-only.txt"


def _verify(repo, out):
    args = argparse.Namespace(ticket=TICKET, select=False, verify=True, out=str(out), timeout=None)
    return command.run(repo.root, args, CONFIG)


def _cases(xml):
    return [c.get("name") for c in ET.parse(xml).iter("testcase")]


def test_s13_one_red_and_one_serial_entry_exit_1_both_junit_files_and_the_summary(tmp_path, monkeypatch):
    repo = project(tmp_path, extra={
        f"{OWN_SUITE}test_red.py": "def test_red():\n    assert 1 == 2\n",
        f"{OWN_SUITE}test_serial.py": "def test_alone():\n    assert True\n",
        SERIAL_LIST: f"{OWN_SUITE}test_serial.py::test_alone  # serial: timing: runs alone\n"})
    change(repo, {"src/pkg/feature.py": "from pkg.core import add\n\n\ndef twice(x):\n    return add(x, x)  # c\n"})
    order = []
    real = attribution.run_pytest
    monkeypatch.setattr(attribution, "run_pytest", lambda tree, targets, *a, **k: order.append(targets) or real(
        tree, targets, *a, **k))
    out = tmp_path / "verify"
    assert _verify(repo, out) == 1
    assert json.loads((out / "select.json").read_text()) == {
        "ticket": TICKET, "suites": [OWN_SUITE], "pytest_options": command._select.PYTEST_OPTIONS}
    assert "test_alone" not in _cases(out / "parallel.xml") and "test_red" in _cases(out / "parallel.xml")
    assert _cases(out / "serial.xml") == ["test_alone"]
    summary = (out / "summary.txt").read_text().splitlines()
    assert len(summary) == 1 and summary[0].startswith(f"verify {TICKET}: exit 1")
    assert (out / "verify.exit").read_text().strip() == "1"
    assert order == [[OWN_SUITE], [f"{OWN_SUITE}test_serial.py::test_alone"]]  # parallel first, then serial
    names = sorted(p.name for p in out.iterdir())
    assert "verify.exit.tmp" not in names


def test_s13_green_exit_0_and_an_empty_serial_suite(tmp_path):
    repo = project(tmp_path)
    change(repo, {"src/pkg/feature.py": "from pkg.core import add\n\n\ndef twice(x):\n    return add(x, x)  # c\n"})
    out = tmp_path / "verify"
    assert _verify(repo, out) == 0
    assert _cases(out / "serial.xml") == []
    assert (out / "verify.exit").read_text().strip() == "0"


def test_s13_a_refused_selection_exit_2(tmp_path):
    repo = project(tmp_path)
    change(repo, {"src/pkg/lonely.py": "VALUE = 7\n"})
    out = tmp_path / "verify"
    assert _verify(repo, out) == 2
    assert not (out / "select.json").exists()
    assert (out / "verify.exit").read_text().strip() == "2"
    assert "SELECTION_REFUSED" in (out / "summary.txt").read_text()


def test_s13_a_killed_run_exit_3(tmp_path):
    repo = project(tmp_path, extra={f"{OWN_SUITE}test_killed.py": (
        "import os, signal\n\n\ndef test_killed():\n    os.kill(os.getpid(), signal.SIGKILL)\n")})
    change(repo, {"src/pkg/feature.py": "from pkg.core import add\n\n\ndef twice(x):\n    return add(x, x)  # c\n"})
    out = tmp_path / "verify"
    assert _verify(repo, out) == 3
    assert (out / "verify.exit").read_text().strip() == "3"
    assert "did not complete" in (out / "summary.txt").read_text()


def test_s13_the_verify_exit_file_is_written_last(tmp_path, monkeypatch):
    repo = project(tmp_path)
    change(repo, {"src/pkg/feature.py": "from pkg.core import add\n\n\ndef twice(x):\n    return add(x, x)  # c\n"})
    out = tmp_path / "verify"
    written = []
    from pathlib import Path
    real_write, real_replace = Path.write_text, Path.replace
    monkeypatch.setattr(Path, "write_text", lambda self, *a, **k: written.append(self.name) or real_write(
        self, *a, **k))
    monkeypatch.setattr(Path, "replace", lambda self, target: written.append(Path(target).name) or real_replace(
        self, target))
    _verify(repo, out)
    assert written[-1] == "verify.exit" and "summary.txt" in written
