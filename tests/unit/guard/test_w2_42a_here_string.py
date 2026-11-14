"""Builder tests for W2-42a's R3 round (DEC-1164 (18)): the word after ``<<<`` is the here-string's text, never the
command's end; the text a shell or ``xargs`` is given is judged; a body-less heredoc loses no write before it.

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
from gov.guard.decide import _UNRESOLVABLE, _extract_bash_write_targets, _line_write_targets  # noqa: E402

A = "tests/" + "acceptance"
T = A + "/W1/t.py"
SENT = _UNRESOLVABLE


@pytest.fixture()
def root(tmp_path, monkeypatch):
    r = tmp_path / "proj"
    (r / A / "W1").mkdir(parents=True)
    (r / A / "W1" / "test_a.py").write_text("x\n")
    (r / "src").mkdir()
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-qm", "base"]):
        subprocess.run(["git", "-C", str(r), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True,
                       capture_output=True)
    monkeypatch.delenv("X", raising=False)
    return str(os.path.realpath(r))


def got(command, root):
    return [t.replace(root, "R") for t in (_extract_bash_write_targets(command, root) or [])]


# -- R3: the words after a here-string stay the command's arguments ---------------------------------------------------

@pytest.mark.parametrize("template", [
    'tee <<< "x" {w}', 'tee -a <<< "x" {w}', "tee <<< x {w}", "cp <<< x src/a.py {w}", 'tee <<< "x" {w}; echo ok',
    'true && tee <<< "x" {w}', '(tee <<< "x" {w})', '<<< "x" tee {w}', 'echo a | tee <<< "x" {w}',
])
def test_r3_a_write_argument_after_a_here_string_is_a_target(root, template):
    assert f"R/{T}" in got(template.replace("{w}", T), root)
    assert "R/src/ok.py" in got(template.replace("{w}", "src/ok.py"), root)


def test_r3_the_line_parser_reads_the_words_after_the_here_string(root):
    assert _line_write_targets(f'tee <<< "x" {T}', root) == [os.path.join(root, T)]


@pytest.mark.parametrize("command", ['grep -c b <<< "a"', 'wc -l <<< "$v"', "cat <<< T", "bash <<< 'echo hi'",
                                     'cat <<< "x" > /dev/null', "sh <<< ls", "tee <<< x /dev/null"])
def test_r3_the_read_only_forms_stay_free(root, command):
    assert got(command, root) == []


# -- the here-string's text, to a shell or to xargs -------------------------------------------------------------------

@pytest.mark.parametrize("template", [
    "bash <<< 'touch {w}'", 'sh <<< "touch {w}"', "bash <<< 'echo a; touch {w}'", "cat <<< 'touch {w}' | bash",
    "bash -s <<< 'touch {w}'", "echo x; sh <<< \"echo y > {w}\"", "xargs touch <<< {w}", "xargs -r touch <<< '{w}'",
    "xargs -n 1 touch <<< '{w} {w}'", "xargs touch <<< \"{w}\"", "cat <<< '{w}' | xargs touch",
])
def test_the_text_a_shell_or_xargs_is_given_is_judged(root, template):
    assert f"R/{T}" in got(template.replace("{w}", T), root)
    assert "R/src/ok.py" in got(template.replace("{w}", "src/ok.py"), root)
    assert got(template.replace("{w}", "/dev/null"), root) == []


@pytest.mark.parametrize("command", ['bash <<< "$X"', 'sh <<< "$(echo hi)"', "sh <<< \"`echo hi`\"",
                                     'bash <<< "touch $X"', 'xargs touch <<< "$X"', 'python3 <<< "$X"',
                                     "xargs -I{} touch {} <<< a", 'xargs touch <<< "a $(echo b)"'])
def test_a_text_the_guard_cannot_know_is_unresolvable(root, command):
    assert SENT in got(command, root)


def test_a_variable_the_command_sets_is_a_known_text(root):
    assert f"R/{T}" in got(f'X="touch {T}"; bash <<< "$X"', root)
    assert got('X="echo hi"; bash <<< "$X"', root) == []


def test_python_here_string_is_read_as_its_heredoc_is(root):
    # rule 5 never read the code a Python heredoc body holds (it stays opaque to the product, KPI 8); a here-string to
    # Python is the same body, so the answer is the heredoc's
    heredoc = got(f"python3 <<'EOF'\nopen('{T}','w')\nEOF", root)
    assert got(f"python3 <<< \"open('{T}','w')\"", root) == heredoc


def test_a_substitution_in_a_here_string_to_a_shell_is_judged(root):
    assert f"R/{T}" in got(f'sh <<< "$(touch {T})"', root)


def test_a_here_string_word_with_escapes_and_nested_quotes_ends_where_the_shell_ends_it(root):
    assert f"R/{T}" in got(f"bash <<< \"echo \\\"a b\\\"; touch {T}\" ; echo done", root)
    assert f"R/{T}" in got(f"bash <<< \"$(echo '(' )\" ; touch {T}", root)


# -- a body-less or unterminated heredoc loses no write before it -----------------------------------------------------

@pytest.mark.parametrize("template", [
    "python3 -c \"open('{w}','w').write('x')\"; cat <<EOF",
    "python3 -c \"open('{w}','w').write('x')\"; cat <<'EOF'",
    "python3 -c \"open('{w}','w').write('x')\"; cat <<EOF\nbody without an end line",
    "python3 -c \"open('{w}','w').write('x')\"; cat <<-EOF",
])
def test_a_heredoc_with_no_body_or_end_line_keeps_the_write_before_it(root, template):
    assert f"R/{T}" in got(template.replace("{w}", T), root)
    assert "R/src/ok.py" in got(template.replace("{w}", "src/ok.py"), root)


def test_an_unterminated_shell_heredoc_body_is_judged_as_commands(root):
    assert f"R/{T}" in got(f"bash <<EOF\ntouch {T}", root)


def test_the_unterminated_data_body_keeps_what_the_line_parser_read_before(root):
    assert f"R/{T}" in got(f"cat <<EOF\ntouch {T}", root)


def test_the_default_scan_still_reports_a_bodyless_heredoc_unreadable():
    with pytest.raises(bash_writes.Unreadable):
        bash_writes.heredocs("cat <<EOF")
    with pytest.raises(bash_writes.Unreadable):
        bash_writes.heredocs("cat <<EOF\nx")


# -- nothing the base read is lost ------------------------------------------------------------------------------------

@pytest.mark.parametrize("command", [
    "echo x > src/ok.py; bash <<< ls # it's", f"python3 -c \"open('{T}','w')\"; xargs touch <<< {T}",
    f"python3 -c \"open('{T}','w')\"; bash <<< ls", "grep x <<< 'a' > src/ok.py",
])
def test_a_target_the_base_gave_is_kept(root, command):
    out = got(command, root)
    assert out and (f"R/{T}" in out or "R/src/ok.py" in out)
