"""W1-50, KPI line 3 (DEC-399): whole-tree fixtures strip the held-out deny line from the copied settings file.

"Every test fixture that copies the whole tree strips the held-out deny line
from the copied settings file."

Test code about test code, green as soon as the two fixtures are revised.

- **Which fixtures.** "Every fixture that copies the whole tree" is read from
  the sources by W1-28's check (``w1_28_copy_check.whole_tree_copiers``): a
  listing of the whole repository followed by a copy, or a whole-tree route.
  Today that is ``copy_working_tree`` of W1-05 and of W1-07 (W1-25 uses
  W1-07's). A fixture a later suite adds in that form is found and run here
  without a change.
- **How.** Each is called with a **synthetic** source repository as its root:
  a temporary git repository whose ``.claude/settings.json`` is made up here,
  with made-up absolute ``Read`` deny rules. The copy it commits must carry
  none of them and must keep everything else of the file.
- **The line.** The held-out deny line is a ``Read`` deny rule with an absolute
  path, ``Read(//...)``: the form W1-46's and W1-47's fixtures leave out
  (``w1_46_support.make_project``, ``w1_47_support.make_wired_copy``).

Nothing here opens, prints or compares this repository's own settings file or
its held-out file.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_W1_28 = str(Path(__file__).resolve().parents[1] / "W1-28")
if _W1_28 not in sys.path:
    sys.path.insert(0, _W1_28)

import w1_28_copy_check as check  # noqa: E402

SETTINGS_REL = ".claude/settings.json"
MADE_UP = "/w1-50-made-up/not-a-held-out-path"
HELD_OUT_RULES = [f"Read(/{MADE_UP}/**)", f"Read( /{MADE_UP}/cases/**)", f"Read(/{MADE_UP})"]
KEPT_DENY = ["Read(./secrets/**)", "Edit(/tests/acceptance/**)", "Bash(sudo:*)", "Read(~/.ssh/**)"]
SETTINGS = {
    "env": {"W1_50_SYNTHETIC": "1"},
    "permissions": {
        "allow": ["Read(./docs/**)", "Bash(git status:*)"],
        "deny": [KEPT_DENY[0], HELD_OUT_RULES[0], KEPT_DENY[1], HELD_OUT_RULES[1], KEPT_DENY[2], HELD_OUT_RULES[2],
                 KEPT_DENY[3]],
    },
    "hooks": {"PreToolUse": [{"matcher": "Write|Edit|Bash",
                              "hooks": [{"type": "command", "command": "python3 governance/kernel/hooks/pretooluse.py"}]}]},
}
EXPECTED = {**SETTINGS, "permissions": {**SETTINGS["permissions"], "deny": KEPT_DENY}}

WHOLE_TREE = check.whole_tree_copiers()
KNOWN = {"W1-05/w1_05_support.py::copy_working_tree", "W1-07/w1_07_support.py::copy_working_tree"}


def _source(directory, settings=SETTINGS):
    """W1-28's synthetic source repository, with a settings file made up here in its working tree."""
    source = check.make_source(directory)
    (source / SETTINGS_REL).write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    return source


def _left(text):
    """The held-out rules, and the made-up path in any other form, that ``text`` of a settings file still holds."""
    data = json.loads(text)
    deny = data.get("permissions", {}).get("deny", [])
    left = [rule for rule in deny if isinstance(rule, str) and rule.replace(" ", "").startswith("Read(//")]
    return left + (["<the made-up path, outside a deny rule>"] if not left and MADE_UP in text else [])


def test_the_two_whole_tree_fixtures_are_found():
    """A fixture that was renamed, or that the reading no longer finds, is not silently dropped from this check."""
    missing = sorted(KNOWN - {function.label for function in WHOLE_TREE})
    assert not missing, f"the reading of the sources no longer finds these whole-tree fixtures: {missing}"
    unrunnable = sorted(function.label for function in WHOLE_TREE if not function.runnable)
    assert not unrunnable, f"these whole-tree copies cannot be run on a synthetic root: {unrunnable}"


@pytest.mark.parametrize("function", WHOLE_TREE, ids=lambda function: function.label)
def test_a_whole_tree_fixture_strips_the_held_out_deny_rules(function, tmp_path):
    source = _source(tmp_path / "source")
    produced = check.run_copier(function, source, tmp_path / "produced")
    assert check.arrived(produced), f"{function.label} copied nothing from the synthetic root"
    copied = produced / SETTINGS_REL
    assert copied.is_file(), f"{function.label} did not copy {SETTINGS_REL}"
    left = _left(copied.read_text(encoding="utf-8"))
    assert not left, (
        f"{function.label} copied {len(left)} made-up held-out deny rule(s) into the project it built (DEC-399)"
    )
    done = subprocess.run(["git", "-C", str(produced), "show", f"HEAD:{SETTINGS_REL}"], capture_output=True,
                          text=True)
    assert done.returncode == 0, f"{function.label} did not commit {SETTINGS_REL}: {done.stderr.strip()}"
    assert not _left(done.stdout), f"{function.label} committed the made-up held-out deny rules in the copy"


@pytest.mark.parametrize("function", WHOLE_TREE, ids=lambda function: function.label)
def test_a_whole_tree_fixture_keeps_the_rest_of_the_settings_file(function, tmp_path):
    """Only those rules go: the other deny rules in their order, the allow rules, the hooks and the environment."""
    produced = check.run_copier(function, _source(tmp_path / "source"), tmp_path / "produced")
    copied = json.loads((produced / SETTINGS_REL).read_text(encoding="utf-8"))
    assert copied == EXPECTED, f"{function.label} changed more of {SETTINGS_REL} than the held-out deny rules"


@pytest.mark.parametrize("settings", ({"hooks": {}}, {"permissions": {"allow": ["Read(./docs/**)"]}}),
                         ids=("no-permissions", "no-deny-list"))
@pytest.mark.parametrize("function", WHOLE_TREE, ids=lambda function: function.label)
def test_a_settings_file_with_nothing_to_strip_is_copied_as_it_is(function, settings, tmp_path):
    source = _source(tmp_path / "source", settings)
    produced = check.run_copier(function, source, tmp_path / "produced")
    assert (produced / SETTINGS_REL).read_text(encoding="utf-8") == (source / SETTINGS_REL).read_text(
        encoding="utf-8"), f"{function.label} rewrote a settings file that holds no deny rule"


def test_the_check_catches_a_copy_that_keeps_the_rules(tmp_path):
    """The check is a real one: the synthetic file as it is, unstripped, is caught."""
    source = _source(tmp_path / "source")
    left = _left((source / SETTINGS_REL).read_text(encoding="utf-8"))
    assert sorted(left) == sorted(HELD_OUT_RULES), f"the check found {left} in the unstripped synthetic file"
