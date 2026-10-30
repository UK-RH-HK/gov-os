"""The pre-close gate's collection (DEC-868 item 1 (a)) and the repair ticket's fingerprint (W2-M252)."""
from __future__ import annotations

import re
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from gov.cli.errors import GovError
from gov.close import gates
from gov.close.command import DEFAULT_TIMEOUT
from gov.close.tool import FINGERPRINT_KEY, open_repair_ticket
from gov.tasks.tickets import frontmatter

from .conftest import TICKET


def _suite(root):
    folder = root / "tests" / "unit"
    folder.mkdir(parents=True)
    (folder / "test_a.py").write_text("def test_a():\n    assert True\n", encoding="utf-8")
    return root / "tests"


def test_the_collection_is_not_held_to_the_time_limit_of_the_tests(tmp_path):
    given = []

    def started(root, cmd, env, timeout=None):
        given.append(timeout)
        return SimpleNamespace(returncode=0, stdout="1 test collected\n", stderr="")

    with patch("gov.close.command._started", started):
        gates.check_collection(tmp_path, [(_suite(tmp_path), None)], 1)
        gates.check_collection(tmp_path, [(tmp_path / "tests", None)], DEFAULT_TIMEOUT * 3)
    assert given == [DEFAULT_TIMEOUT, DEFAULT_TIMEOUT * 3]


def test_without_pytest_the_collection_says_the_test_runner_is_absent(tmp_path):
    with patch("importlib.util.find_spec", return_value=None):
        with pytest.raises(GovError) as refused:
            gates.check_collection(tmp_path, [(_suite(tmp_path), None)], 60)
    assert refused.value.code == "TEST_RUNNER_ABSENT"


def test_pytest_from_the_callers_path_alone_is_the_test_runner_absent(tmp_path):
    answer = SimpleNamespace(returncode=1, stdout="", stderr="/usr/bin/python3: No module named pytest\n")
    with patch("gov.close.command._started", return_value=answer):
        with pytest.raises(GovError) as refused:
            gates.check_collection(tmp_path, [(_suite(tmp_path), None)], 60)
    assert refused.value.code == "TEST_RUNNER_ABSENT"


def test_the_findings_fingerprint_is_no_hash_a_reader_takes_for_the_context_hash(root):
    repair = open_repair_ticket(root, TICKET, ["a finding"])
    front = frontmatter(root / ".tickets" / f"{repair}.md")
    assert front[FINGERPRINT_KEY].startswith("findings-")
    assert not re.search(r"\b[0-9a-f]{64}\b", (root / ".tickets" / f"{repair}.md").read_text(encoding="utf-8"))
