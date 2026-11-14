"""Builder tests for W2-42a's R3 F1 second batch (DEC-1164 (18)): a here-string read as data must not hide a command it
feeds. A variable `read` binds from a here-string, used as a command's name, and a `mapfile`/`readarray -C` callback
are commands the guard judges: the unresolvable target when it cannot know them.

Regression evidence only (DEC-136). Every project is a temporary git repository.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from gov.guard.decide import _UNRESOLVABLE, _extract_bash_write_targets  # noqa: E402

A = "tests/" + "acceptance"
T = A + "/W1/t.py"


@pytest.fixture()
def root(tmp_path):
    r = tmp_path / "proj"
    (r / A / "W1").mkdir(parents=True)
    (r / A / "W1" / "test_a.py").write_text("x\n")
    (r / "src").mkdir()
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-qm", "base"]):
        subprocess.run(["git", "-C", str(r), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True,
                       capture_output=True)
    return str(os.path.realpath(r))


def got(command, root):
    return [t.replace(root, "R") for t in (_extract_bash_write_targets(command, root) or [])]


@pytest.mark.parametrize("command", [
    "while read -r f; do $f; done <<< 'touch {w}'", "while read -r f; do ${f}; done <<< 'touch {w}'",
    "while read -r f; do \"$f\" x; done <<< \"$(ls)\"", "read -r a b <<< \"$v\"; $a $b",
    "read -r f <<< \"$v\"; $f", "read -r f <<< \"$v\"; ${f}", "read f <<< 'x'; \"$f\" y",
    "while read -r f; do env $f; done <<< \"$(ls)\"", "while read -r f; do command $f; done <<< \"$v\"",
    "while read -r f; do time $f; done <<< \"$v\"", "while read -r f; do env -i $f; done <<< \"$v\"",
    "read <<< \"$v\"; $REPLY", "read -a arr <<< \"$v\"; ${arr[0]} x", "read -r f <<< \"$v\"; xargs $f",
    "read -r f <<< \"$v\"; sudo $f", "read -r f <<< \"$v\"; stdbuf -o0 $f",
    "read -r f <<< \"$v\"; eval $f x", "read -r f <<< \"$v\"; echo $($f)",
])
def test_a_command_name_from_a_read_variable_is_unresolvable(root, command):
    out = got(command.replace("{w}", T), root)
    assert _UNRESOLVABLE in out or any(t.endswith(T) for t in out), out
    assert _UNRESOLVABLE in got(command.replace("{w}", "src/ok.py"), root)


@pytest.mark.parametrize("command", [
    "read -r f <<< \"$v\"; echo $f", "while read -r f; do cat \"$f\"; done <<< \"$(ls)\"",
    "while read -r f; do echo \"$f\" x; done <<< \"$v\"", "read -r f <<< \"$v\"; f2=1; echo $f2 $f",
    "read -r a <<< \"$v\"; ls $a", "read -r a <<< \"$v\"; $b",
])
def test_a_read_variable_used_as_an_argument_of_a_reader_stays_free(root, command):
    assert got(command, root) == []


@pytest.mark.parametrize("template", [
    "mapfile -C 'touch {w}' -c 1 L <<< \"$v\"", "readarray -tC 'touch {w}' -c 1 L <<< \"$v\"",
    "mapfile -tC'touch {w}' L <<< \"$v\"", "mapfile -c 1 -C 'touch {w}' L < /dev/null",
])
def test_a_literal_mapfile_callback_is_judged_as_that_command(root, template):
    assert f"R/{T}" in got(template.replace("{w}", T), root)
    assert got(template.replace("{w}", "src/ok.py"), root) == ["R/src/ok.py"]


@pytest.mark.parametrize("command", [
    "mapfile -C cb L <<< \"$v\"", "mapfile -C \"$cb\" -c 1 L <<< \"$v\"", "readarray -tC cb L <<< 'x'",
    "mapfile -C 'cb 1' L <<< \"$v\"", "mapfile -C \"$(echo cb)\" L <<< x",
])
def test_a_callback_the_guard_cannot_know_is_unresolvable(root, command):
    assert _UNRESOLVABLE in got(command, root)


@pytest.mark.parametrize("command", [
    "mapfile -t L <<< \"$v\"", "mapfile -n 2 -O 1 L <<< \"$v\"", "readarray -d : -t L <<< \"$v\"",
    "mapfile -C echo -c 1 L <<< \"$v\"",
])
def test_mapfile_without_a_callback_or_with_a_reader_stays_free(root, command):
    assert got(command, root) == []
