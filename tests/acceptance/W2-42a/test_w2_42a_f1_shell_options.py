"""W2-42a, the FULL review's finding F1 (round 1), with F4's ride-along: a shell that reads its commands from standard
input is a shell, whatever options it is given (KPI lines S1 and S6; failure line F1, a write the base parser catches
is not to be missed).

Driven by ``fixtures/f1_shell_options.json``: each case's command, whether its heredoc body writes (a shell's body is
commands) or not (a body that cat, tee, grep or a named script takes as data), and the paths it writes, relative to
the case's folder. The JSON is plain data so the live hook's own fix can be checked with it too.

- **Product, write parser** (``parse``, must pass): in a ``tmp_path`` of its own with no session variable set, a
  ``write`` case gives each of its targets or the unresolvable target; a ``no-write`` case gives its own targets and
  nothing else.
- **Product, read judge** (``judge``, must pass): the same head with a body naming the hidden file of the case's
  project; under a shell it is refused with the hidden-part refusal, as data it is not refused.
- **Hook fixture** (``run_hook``, not in the must-pass set): an engineer's shell-with-options heredoc writing the
  acceptance folder is refused by rule 1. The fixture (``fixtures/hook/``, not changed here) has its own reading of
  the command (``bash_writes.py``) with the same gap, so these cases are ``xfail`` (not strict): they judge the hook
  fixture, not the product.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w2_42a_support as s  # noqa: E402

U = s.UNRESOLVABLE
DATA = os.path.join(s.HERE, "fixtures", "f1_shell_options.json")
CASES = s.load(DATA)["cases"]
WRITES = [c for c in CASES if c["expect"] == "write"]
CONTROLS = [c for c in CASES if c["expect"] == "no-write"]
HIDDEN_READ = "cat fixtures/evaluation/w242a/hidden/q01.txt"


def ids(cases):
    return [c["id"] for c in cases]


@pytest.fixture
def at(tmp_path, monkeypatch):
    """The case's folder (real path), holding the files the commands name; no session variable set."""
    for name in s._SESSION:
        monkeypatch.delenv(name, raising=False)
    root = tmp_path / "case"
    (root / "tests" / "acceptance" / "X").mkdir(parents=True)
    (root / "tests" / "acceptance" / "X" / "t.py").write_text("a = 'a'\n")
    (root / "src").mkdir()
    (root / "x.py").write_text("x = 1\n")
    (root / "script.sh").write_text("echo hi\n")
    return os.path.realpath(str(root))


@pytest.fixture
def root(tmp_path, monkeypatch):
    """A project of the case's own whose evaluation set measures research and whose hidden part holds a file."""
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    (tmp_path / "home").mkdir()
    for name in s._SESSION:
        monkeypatch.delenv(name, raising=False)
    return s.project(tmp_path)


def head_and_delimiter(command):
    """The command's first line (the head) and its last (the heredoc's delimiter)."""
    lines = command.split("\n")
    return lines[0], lines[-1]


# -- the product's write parser: a shell's body is commands, whatever its options --------------------------------

def test_review_f1_the_data_file_holds_every_spelling_of_the_finding():
    assert len(WRITES) == 15 and len(CONTROLS) == 4
    assert len(set(ids(CASES))) == len(CASES)
    for c in CASES:
        assert set(c) >= {"id", "command", "expect", "targets_include", "note"}
        assert all(not t.startswith("/") for t in c["targets_include"])


@pytest.mark.parametrize("case", WRITES, ids=ids(WRITES))
def test_review_f1_a_shell_with_options_reading_a_heredoc_judges_its_body_as_commands(at, case):
    got = set(s.parse(case["command"], at) or [])
    want = {s.real(at, t) for t in case["targets_include"]}
    assert got, f"no write for a shell's body ({case['note']})"
    assert U in got or want <= got, f"missing {sorted(want - got)} ({case['note']}); got {sorted(got)}"


@pytest.mark.parametrize("case", CONTROLS, ids=ids(CONTROLS))
def test_review_f1_a_data_body_stays_data(at, case):
    got = set(s.parse(case["command"], at) or [])
    want = {s.real(at, t) for t in case["targets_include"]}
    assert got == want, f"want only {sorted(want)} ({case['note']}); got {sorted(got)}"


# -- the product's read judge: the same body is read as commands under a shell, not as data -------------------------

@pytest.mark.parametrize("case", WRITES, ids=ids(WRITES))
def test_review_f1_a_shell_with_options_body_naming_a_hidden_file_is_refused(root, case):
    _, _, hidden = s.refusal_texts()
    head, end = head_and_delimiter(case["command"])
    assert s.judge(f"{head}\n{HIDDEN_READ}\n{end}", root) == hidden


@pytest.mark.parametrize("case", CONTROLS, ids=ids(CONTROLS))
def test_review_f1_a_data_body_naming_a_hidden_file_is_no_read(root, case):
    head, end = head_and_delimiter(case["command"])
    assert s.judge(f"{head}\n{HIDDEN_READ}\n{end}", root) == ""


# -- the hook fixture (not the product; outside the must-pass set) ---------------------------------------------------

HOOK_CASES = [
    "bash -euo pipefail <<'EOT'\necho start\ntouch tests/acceptance/W2-42a/t_f1_probe.py\nEOT",
    "cat <<'EOT' | bash -o pipefail\necho start\necho x > tests/acceptance/W2-42a/t_f1_probe.py\nEOT",
]


@pytest.mark.xfail(strict=False, reason="judges the hook fixture (fixtures/hook/bash_writes.py has the F1 gap "
                                        "itself and is not changed here), not the product")
@pytest.mark.parametrize("command", HOOK_CASES, ids=["bash-euo-pipefail", "cat-pipe-bash-o-pipefail"])
def test_review_f1_hook_an_engineer_s_shell_with_options_writing_the_tests_is_refused_by_rule_1(command):
    got, why, code = s.run_hook("Bash", {"command": command}, s.REPO, s.REPO, "engineer")
    assert (got, code) == ("deny", 0), f"want refused by rule 1, got {got} ({why[:400]})"
    assert why in s.write_rule_reasons("engineer"), f"refused by another rule: {why[:400]}"
