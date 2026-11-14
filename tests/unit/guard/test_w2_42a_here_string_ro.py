"""Builder tests for W2-42a's R3 F1 fix (DEC-1164 (18)): the read-only here-string forms with an expanded text stay
free, and every form that runs the text, or whose script writes, keeps its target or the unresolvable target.

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
from gov.guard import bash_writes  # noqa: E402
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
    'read -r a <<< "$v"', 'IFS= read -r a <<< "$(ls)"', 'mapfile -t a <<< "$(ls)"', 'readarray -t a <<< "$v"',
    'while read -r f; do echo "$f"; done <<< "$(ls)"', 'until read -r f; do :; done <<< "$v"',
    'while IFS= read -r f; do echo "$f"; done <<< "$v"', 'sed "s/a/b/" <<< "$v"', 'sed -n -e "/a/p" <<< "$v"',
    "awk '{print $1}' <<< \"$v\"", 'bc <<< "1+$n"', 'grep a <<< "$v"', 'wc -c <<< "$(ls)"',
    'sort <<< "$v" | uniq', 'cut -d: -f1 <<< "$v"', 'tr a b <<< "$v"',
])
def test_the_read_only_forms_with_an_expanded_text_give_no_target(root, command):
    assert got(command, root) == []


@pytest.mark.parametrize("template", [
    'read -r a <<< "$v" > {w}', 'mapfile -t a <<< "$v"; touch {w}', 'while read -r f; do touch {w}; done <<< "$v"',
    'while read -r f; do cp "$f" {w}; done <<< "$(ls)"', 'sed "s/a/b/" <<< "$v" > {w}',
    'read -r a <<< "$(touch {w})"', 'while read -r f; do :; done <<< "$(touch {w})"',
    'sed "s/a/b/" <<< "$(touch {w})"',
])
def test_a_write_beside_a_read_only_form_is_still_a_target(root, template):
    assert f"R/{T}" in got(template.replace("{w}", T), root)
    assert "R/src/ok.py" in got(template.replace("{w}", "src/ok.py"), root)


@pytest.mark.parametrize("command", [
    'bash <<< "$v"', 'sh <<< "$(ls)"', 'zsh <<< "$v"', 'dash <<< "$v"', 'xargs touch <<< "$v"', 'source /dev/stdin <<< "$v"',
    'eval <<< "$v"', 'cat <<< "$v" | sh', 'foo <<< "$v"', 'sed -i "s/a/b/" f <<< "$v"', 'sed "w out" <<< "$v"',
    'sed "s/a/b/w out" <<< "$v"', 'sed "e" <<< "$v"', 'sed -f s.sed <<< "$v"', "awk '{print > \"o\"}' <<< \"$v\"",
    "awk 'BEGIN{system(\"x\")}' <<< \"$v\"", 'awk -f p.awk <<< "$v"',
    'while read -r f; do bash; done <<< "$v"', 'while read -r f; do xargs touch; done <<< "$v"',
    '{ read -r f; } <<< "$v"',
])
def test_a_form_that_may_run_the_text_or_whose_script_writes_stays_unresolvable(root, command):
    assert _UNRESOLVABLE in got(command, root)


@pytest.mark.parametrize("args,ok", [
    (["s/a/b/"], True), (["-n", "/a/p"], True), (["-e", "s/a/b/g", "-e", "p"], True), (["s,a,b,"], True),
    (["s/a/b/w", "out"], False), (["-i", "s/a/b/"], False), (["w out"], False), (["/a/w out"], False),
    (["s/a/b/e"], False), (["-f", "x"], False), ([], False), (["--in-place", "p"], False), (["y/ab/cd/"], True),
])
def test_the_sed_script_scan(args, ok):
    assert bash_writes._sed_reads_only(args) is ok


@pytest.mark.parametrize("args,ok", [
    (["{print $1}"], True), (["-F:", "{print $2}"], True), (["{print > \"x\"}"], False), (["BEGIN{system(\"x\")}"], False),
    (["{print | \"sh\"}"], False), (["-f", "p.awk"], False), (["-i", "inplace", "1"], False),
])
def test_the_awk_script_scan(args, ok):
    assert bash_writes._awk_reads_only(args) is ok
