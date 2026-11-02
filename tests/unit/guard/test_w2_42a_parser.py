"""Builder tests for W2-42a: the product's write parser reads what a Bash command writes (DEC-1028 item 4,
ACT-GUARD-FIX-3 §7's eight lines), and never misses a write the parser before it caught.

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
from gov.guard.decide import (_UNRESOLVABLE, _extract_bash_write_targets,  # noqa: E402
                              _line_write_targets, decide)

A = "tests/" + "acceptance"
SENT = _UNRESOLVABLE


@pytest.fixture()
def root(tmp_path, monkeypatch):
    r = tmp_path / "proj"
    (r / A / "W1").mkdir(parents=True)
    (r / A / "W1" / "test_a.py").write_text("x\n")
    (r / "src").mkdir()
    (r / "src" / "m.py").write_text("x\n")
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-qm", "base"]):
        subprocess.run(["git", "-C", str(r), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True,
                       capture_output=True)
    monkeypatch.delenv("B", raising=False)
    return str(os.path.realpath(r))


def got(command, root):
    return [t.replace(root, "R") for t in (_extract_bash_write_targets(command, root) or [])]


# -- KPI 1: heredocs ------------------------------------------------------------------------------------------------

def test_a_data_heredoc_body_is_no_write(root):
    assert got(f"cat > /tmp/w242a.txt <<'EOF'\ntouch {A}/x it's > {A}/y\nEOF", root) == ["/tmp/w242a.txt"]


@pytest.mark.parametrize("reader", ["cat", "tee /tmp/w242a.t", "grep -c x"])
def test_data_readers_take_the_body_as_data(root, reader):
    assert SENT not in got(f"{reader} <<'EOF'\nrm -rf {A}\nEOF", root)
    assert "R/" + A not in got(f"{reader} <<'EOF'\nrm -rf {A}\nEOF", root)


def test_an_unquoted_data_body_substitution_is_judged(root):
    assert "R/" + A + "/g" in got(f"cat > /tmp/w242a.t <<EOF\n$(touch {A}/g)\nEOF", root)


def test_a_shell_body_is_judged_as_commands(root):
    assert got(f"bash <<'EOF'\ntouch {A}/h\nEOF", root) == ["R/" + A + "/h"]
    assert "R/" + A + "/h2" in got(f"sh -s <<EOF\ntouch {A}/h2\nEOF", root)


def test_a_shell_heredoc_inside_a_substitution_is_judged(root):
    assert "R/" + A + "/sub" in got(f"x=$(bash <<'EOF'\ntouch {A}/sub\nEOF\n)", root)


def test_an_unknown_reader_that_may_run_its_input_is_read_as_before(root):
    # flock, make, docker exec ...: the body may run as shell; the parser before W2-42a read it so.
    assert "R/" + A + "/w" in got(f"flock /tmp/l bash <<'EOF'\ntouch {A}/w\nEOF", root)
    assert SENT in got("make -f - <<'EOF'\nit's\nEOF", root)


def test_a_commit_message_heredoc_is_no_write(root):
    assert got(f"git commit -F - <<'EOF'\nit's done > {A}/v\nEOF", root) == []


# -- KPI 2: the command's own variables, literal loops -----------------------------------------------------------

def test_a_variable_set_once_before_use_is_expanded(root):
    assert got("B=/tmp/w242a; mkdir $B/r", root) == ["/tmp/w242a/r"]
    assert got(f"T={A}; touch $T/x", root) == ["R/" + A + "/x"]


def test_a_literal_loop_is_judged_word_by_word(root):
    assert sorted(got(f"for f in a b; do touch {A}/$f; done", root)) == ["R/" + A + "/a", "R/" + A + "/b"]


def test_any_other_binding_is_unresolvable(root):
    assert SENT in got("read B; touch $B/x", root)
    assert SENT in got("B=/tmp/a; B=/tmp/b; touch $B/x", root)
    assert SENT in got("source env.sh; touch $B/x", root)


# -- KPI 3: substitutions, sh -c, eval, keywords and prefixes ----------------------------------------------------

@pytest.mark.parametrize("command", [
    f'echo "$(rm {A}/i)"', f'echo "`rm {A}/i`"', f"sh -c 'rm {A}/i'", f"bash -c \"rm {A}/i\"", f"eval rm {A}/i",
    f"timeout 5 rm {A}/i", f"env -i rm {A}/i", f"nohup rm {A}/i", f"nice -n 5 rm {A}/i", f"command rm {A}/i",
    f"if true; then rm {A}/i; fi", f"while false; do rm {A}/i; done", f"! rm {A}/i", f"{{ rm {A}/i; }}"])
def test_nested_and_prefixed_commands_are_read(root, command):
    assert "R/" + A + "/i" in got(command, root)


# -- KPI 4: an unmatched glob -----------------------------------------------------------------------------------

def test_an_unmatched_glob_is_the_literal_word(root):
    assert got("rm -f /tmp/w242a-none-*.json", root) == ["/tmp/w242a-none-*.json"]
    assert got(f"rm -f {A}/W1/*.none", root) == ["R/" + A + "/W1/*.none"]


def test_a_matched_glob_is_its_files(root):
    assert got(f"rm {A}/W1/*.py", root) == ["R/" + A + "/W1/test_a.py"]


def test_glob_options_keep_an_unmatched_glob_unresolvable(root):
    assert got("shopt -s nocaseglob; rm Tests/*/zz", root) == [SENT]
    assert got("rm tests/**/zz", root) == [SENT]
    assert got("set -f; rm x*", root) == [SENT] or got("set -f; rm x*", root) == ["R/x*"]


# -- KPI 5: writes the line parser did not read -----------------------------------------------------------------

@pytest.mark.parametrize("command,want", [
    (f"git checkout -- {A}/n", "R/" + A + "/n"),
    (f"git checkout HEAD {A}/o", "R/" + A + "/o"),
    (f"git checkout {A}/W1/test_a.py", "R/" + A + "/W1/test_a.py"),
    (f"git restore {A}/W1", "R/" + A + "/W1"),
    (f"git rm -q {A}/W1/test_a.py", "R/" + A + "/W1/test_a.py"),
    (f"git mv src/m.py {A}/W1/m.py", "R/" + A + "/W1/m.py"),
    (f"dd if=/dev/zero of={A}/p", "R/" + A + "/p"),
    (f"truncate -s0 {A}/q", "R/" + A + "/q"),
    (f"sort -o {A}/r x", "R/" + A + "/r"),
    (f"sort --output={A}/r x", "R/" + A + "/r"),
    (f"rsync -a x/ {A}/", "R/" + A),
])
def test_writes_the_line_parser_did_not_read(root, command, want):
    assert want in got(command, root)


def test_git_checkout_of_a_revision_alone_writes_no_path(root):
    assert got("git checkout HEAD", root) == []
    assert got("git checkout main", root) == []


@pytest.mark.parametrize("command", ["git apply /tmp/p.patch", "git am /tmp/p.mbox", "patch -p1 < /tmp/p",
                                     "git -C . apply x.patch"])
def test_patch_appliers_write_unknown_targets(root, command):
    assert SENT in got(command, root)


def test_dry_runs_and_checks_apply_nothing(root):
    assert SENT not in got("git apply --check /tmp/p.patch", root)
    assert SENT not in got("patch --dry-run -p1 < /tmp/p", root)


# -- KPI 7: line continuations ---------------------------------------------------------------------------------

def test_a_backslash_newline_is_removed(root):
    assert "R/" + A + "/s" in got(f"cp /tmp/x \\\n{A}/s", root)
    assert SENT in got(f"cp /tmp/x \\\n{A}/s 'it''s", root)  # unreadable: refused


# -- KPI 8: a heredoc written to a file the command runs ------------------------------------------------------

def test_a_script_run_by_bash_is_judged_as_its_code(root):
    t = got(f"cat > s.sh <<'EOF'\ntouch {A}/t\nEOF\nbash s.sh", root)
    assert "R/" + A + "/t" in t and SENT not in t
    assert "R/" + A + "/t2" in got(f"cat > s.sh <<'EOF'\n#!/bin/sh\ntouch {A}/t2\nEOF\nchmod +x s.sh; ./s.sh", root)


def test_a_run_the_parser_cannot_read_is_unresolvable(root):
    assert SENT in got(f"cat > s.sh <<'EOF'\ntouch x\nEOF\nfor f in s.sh; do bash $f; done", root)
    assert SENT in got("cat > s.sh <<'EOF'\ntouch x\nEOF\nchmod +x s.sh; ./s.sh", root)  # no #! line


def test_a_python_script_written_and_run_is_judged_as_its_code(root):
    t = got(f"cat > s.py <<'EOF'\nopen('{A}/py', 'w').write('x')\nEOF\npython3 s.py", root)
    assert "R/" + A + "/py" in t
    assert SENT in got("cat > s.py <<'EOF'\nimport sys\nopen(sys.argv[1] + 'x', 'w')\nEOF\npython3 s.py $Q", root)


def test_a_python_heredoc_the_shell_rewrites_unpredictably_is_unresolvable(root):
    assert SENT in got("python3 - <<EOF\nprint('$(echo x | sed s/x/y/)')\nEOF", root)
    assert got("python3 - <<'EOF'\nprint('it''s $(x)')\nEOF", root) == []


@pytest.mark.parametrize("command", ['eval "$W242A_UNSET"', 'sh -c "$W242A_UNSET"', "bash -c 'echo \"x > f'"])
def test_an_inner_command_the_guard_cannot_read_is_unresolvable(root, command, monkeypatch):
    monkeypatch.delenv("W242A_UNSET", raising=False)
    assert SENT in got(command, root)


def test_an_inner_command_from_a_known_variable_is_judged(root, monkeypatch):
    monkeypatch.setenv("W242A_SET", f"touch {A}/e")
    assert "R/" + A + "/e" in got('eval "$W242A_SET"', root)


def test_a_script_only_read_is_no_run(root):
    assert got("cat > /tmp/w242a.md <<'EOF'\nrm -rf src\nEOF\ntail -3 /tmp/w242a.md", root) == ["/tmp/w242a.md"]


# -- failure lines: no fail-open, unknown forms refuse ---------------------------------------------------------

LINE = [f"touch {A}/a", f"echo x > {A}/b", f"cp /tmp/x {A}/c", f"mv /tmp/x {A}/", f"tee {A}/d < /tmp/x",
        f"sed -i s/a/b/ {A}/W1/test_a.py", f"mkdir -p {A}/e", f"ln -s /tmp/x {A}/f", f"install /tmp/x {A}/g",
        f"cd {A} && touch h", f"cd {A}/W1; rm -f *.py", f"rm -rf {A}", f"rm {A}/W1/*.none",
        f"B={A}; touch $B/x", f"touch {A}/$(date +%s)", f"touch {A}/`id -u`", f"cp -t {A} /tmp/x",
        f"X=1 touch {A}/j", f"echo a | tee -a {A}/k", f"echo x >> {A}/l"]


@pytest.mark.parametrize("command", LINE)
def test_every_write_the_line_parser_catches_is_still_caught(root, command):
    before = _line_write_targets(command, root) or []
    after = _extract_bash_write_targets(command, root) or []
    assert set(before) - {SENT} <= set(after)
    # An unresolvable write stays unresolvable, or is now resolved to its place in the tests.
    assert SENT not in before or SENT in after or all(A in t for t in after)


@pytest.mark.parametrize("command", ["echo 'unbalanced", "touch \"$(",
                                     f"cat > /tmp/w242a <<'EOF'\nx\nEOF\ntouch $(rm {A}/z"])
def test_an_unparseable_form_still_refuses(root, command):
    assert SENT in got(command, root)


@pytest.mark.parametrize("command", [f"cat <<EOF > /tmp/w242a\ntouch {A}/u", "cat <<$X > y\ntouch src/q\n$X",
                                     f"cat > /tmp/w242a <<EOF\n$(touch {A}/z\nEOF"])
def test_a_heredoc_the_scan_cannot_read_is_read_as_before(root, command):
    assert set(_line_write_targets(command, root)) <= set(_extract_bash_write_targets(command, root))


def test_unparseable_forms_refuse_in_decide(root):
    tid = "DAEO-t42a"
    os.makedirs(os.path.join(root, ".tickets"), exist_ok=True)
    with open(os.path.join(root, ".tickets", tid + ".md"), "w") as f:
        f.write(f"---\nid: {tid}\nstatus: in_progress\nrole: engineer\nallowed_paths:\n- src/**\n---\n")
    deny = decide("Bash", {"command": "echo 'unbalanced > src/x"}, root, "engineer", tid, cwd=root, flag="open")
    assert deny[0] == "deny"
    ok = decide("Bash", {"command": f"cat > src/n.py <<'EOF'\nprint('it''s {A}')\nEOF"}, root, "engineer", tid,
                cwd=root, flag="open")
    assert ok == ("allow", "")
    no = decide("Bash", {"command": f"bash <<'EOF'\ntouch {A}/x\nEOF"}, root, "engineer", tid, cwd=root, flag="open")
    assert no[0] == "deny"


def test_the_sentinel_is_shared():
    assert bash_writes.SENT == _UNRESOLVABLE


def test_the_hooks_parser_text_reads_the_same(root, monkeypatch):
    """The five-rule hook hands the parser its own parser text (heredocs cut, its marks in it, its variables in the
    environment): the parser reads it as the line parser did, and does not fail on the marks."""
    monkeypatch.setenv("B", "/tmp/w242a")
    text = "B=/tmp/w242a ; mkdir '$B/r' < __gov_heredoc_0__ ; echo '`__gov_sub_0__`' ; touch '`__gov_sub_3__`'"
    t = _extract_bash_write_targets(text, root)
    assert "/tmp/w242a/r" in t and SENT in t
