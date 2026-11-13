"""Builder tests for W2-42a's APOS-3/APOS-4 fix (DEC-1174 (1)): a ``#`` inside a parameter expansion ``${...}``
starts no comment (F1), and a here-string ``<<<`` is read, not taken for a heredoc (F4).

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
from gov.guard.decide import _UNRESOLVABLE, _extract_bash_write_targets, lift_refusal  # noqa: E402

A = "tests/" + "acceptance"
T = A + "/W1/t.py"
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
    monkeypatch.delenv("x", raising=False)
    return str(os.path.realpath(r))


def got(command, root):
    return [t.replace(root, "R") for t in (_extract_bash_write_targets(command, root) or [])]


def wrapped(line):
    """The line at the top level, in a quoted bash heredoc body, and in a bash -c string."""
    return [line, f"bash <<'EOF'\n{line}\nEOF", "bash -c '" + line.replace("'", "'\\''") + "'"]


# -- F1: a # inside ${...} starts no comment --------------------------------------------------------------------------

F1_LINES = [
    "v='a # b'; echo ${v%% #*} > {T}",
    "echo ${x:- #a} > {T}",
    "echo ${x:- #a}; touch {T}",
    "echo ${x:-${x:- #in} #out} > {T}",
    "echo \"${x:-\" #q\"}\" > {T}",           # a double quote nested in ${...} inside double quotes
    "echo ${x:-'}' #q} > {T}",                # a quoted } does not close it
    "echo ${x:-$(echo b) #c} > {T}",          # a substitution inside ${...}, then a #
    "echo ${x/ #/-} > {T}",
]


@pytest.mark.parametrize("line", F1_LINES)
def test_f1_a_hash_inside_a_parameter_expansion_keeps_the_write(root, line):
    for command in wrapped(line.replace("{T}", T)):
        assert f"R/{T}" in got(command, root), command


@pytest.mark.parametrize("line", ["echo ${#v} > {T}", "echo ${v#a} > {T}", "echo $# > {T}", "echo ${v##*/} > {T}"])
def test_f1_the_hash_forms_of_bash_are_no_comment(root, line):
    for command in wrapped(line.replace("{T}", T)):
        assert f"R/{T}" in got(command, root), command


def test_f1_the_first_plain_brace_closes_the_expansion_so_a_later_hash_is_a_comment(root):
    # bash: ${y:+{a} closes at the first }; " #b}" is a comment (a later write on that line is not run)
    assert got("echo ${x:+{a} # it's", root) == []
    assert got(f"echo ${{x}} > {T} # it's", root) == [f"R/{T}"]


def test_f1_heredocs_keeps_the_expansion_text_and_drops_a_true_comment():
    found = []
    command = "echo ${v%% #*} ${x:-'}'} # it's\nls"
    text, _ = bash_writes.heredocs(command, found)
    assert "${v%% #*}" in text and "${x:-'}'}" in text and "it's" not in text
    assert [command[a:b] for a, b in found] == ["# it's"]


def test_f1_an_unclosed_expansion_is_an_unclosed_quote(root):
    # bash runs nothing of a line with an unclosed ${ (unexpected EOF): never read as free
    with pytest.raises(bash_writes.UnclosedQuote):
        bash_writes.heredocs("echo ${v # it's\nls")
    with pytest.raises(bash_writes.UnclosedQuote):
        bash_writes.heredocs("echo ${v; touch x")
    assert SENT in got(f"echo ${{v; touch {T}", root)


def test_f1_a_heredoc_operator_inside_an_expansion_is_text(root):
    # bash: ${x:-<<EOF} is the text <<EOF; the next lines are commands
    assert f"R/{T}" in got(f"echo ${{x:-<<EOF}}\ntouch {T}\nEOF", root)


def test_f1_the_lift_form_after_an_expansion_hash_is_refused():
    assert lift_refusal("echo ${v%% #*}; gov pause --off")
    assert lift_refusal("bash <<'EOF'\necho ${v%% #*}; gov pause --off\nEOF")
    assert lift_refusal("echo ${v%% #it's} ; gov pause --off") != ""


# -- F4: a here-string is read ----------------------------------------------------------------------------------------

@pytest.mark.parametrize("command", ['grep -c b <<< "a # b"', "wc -w <<< 'a # b'", 'jq -r . <<< "\\"a # b\\""',
                                     'grep -c b <<< "a # b" | wc -l'])
def test_f4_a_data_here_string_holding_a_hash_is_free(root, command):
    assert got(command, root) == []
    assert lift_refusal(command) == ""


@pytest.mark.parametrize("template", ['grep -c b <<< "a # b" > {w}', "tr a-z A-Z <<< 'a # b' > {w}"])
def test_f4_a_data_here_string_command_writes_its_redirect(root, template):
    assert got(template.replace("{w}", T), root) == [f"R/{T}"]
    assert got(template.replace("{w}", "src/ok.py"), root) == ["R/src/ok.py"]


def test_f4_heredocs_takes_no_here_string_for_a_heredoc():
    text, bodies = bash_writes.heredocs('grep -c b <<< "a # b"')
    assert bodies == [] and '<<< "a # b"' in text


def test_f4_lines_after_a_here_string_are_commands_not_a_body(root):
    # The scan once took "<< EOF" of "<<< EOF" for a heredoc and the next lines for its data body.
    assert f"R/{T}" in got(f"cat <<< EOF\ntouch {T}\nEOF", root)


def test_f4_a_here_string_substitution_is_judged(root):
    assert f"R/{T}" in got(f'grep x <<< "$(touch {T})"', root)


@pytest.mark.parametrize("command", ['bash <<< "touch {T}"', "sh <<< 'touch {T}'", 'python3 <<< "open(1)"',
                                     'cat <<< "touch {T}" | bash', 'xargs touch <<< "{T}"'])
def test_f4_a_here_string_a_command_may_run_is_read_as_before(root, command):
    command = command.replace("{T}", T)
    with pytest.raises(bash_writes.Unreadable):
        bash_writes.judge(command, root, lambda text, where: None, lambda word: word)
    with pytest.raises(bash_writes.Unreadable):
        bash_writes.comment_spans(command)


PY_T = f"python3 -c \"open('{T}','w')\""


@pytest.mark.parametrize("command", [
    PY_T + "; echo ${x:-'}' #q} && xargs touch <<< " + T,     # the here-string a command may run is unreadable
    PY_T + "; echo ${x:-${x:- #in} #out} && cat <<EOF",         # the ${...} once hid a heredoc with no body
    PY_T + "; bash <<< ls",
])
def test_fail_closed_a_target_the_base_read_is_kept_when_the_scan_cannot_read_the_command(root, command):
    assert f"R/{T}" in got(command, root)


def test_fail_closed_the_second_readings_keep_the_unreadable_answer_too(root):
    # the line parser's targets and the unresolvable target for a comment's quote, as for any unreadable command
    command = f"echo x > src/ok.py; bash <<< ls # it's"
    out = got(command, root)
    assert "R/src/ok.py" in out and SENT in out


@pytest.mark.parametrize("comment", ["# note $(touch {T})", "# it's $(touch {T})", "# it's `touch {T}`",
                                     "ls # it's; grep x <<< \"$(touch {T})\""])
def test_fail_closed_a_substitution_in_an_unquoted_shell_body_comment_runs(root, comment):
    # the shell that feeds the body expands it first, comments and all
    body = comment.replace("{T}", T)
    assert f"R/{T}" in got(f"bash <<EOF\n{body}\nEOF", root)
    assert got(f"bash <<'EOF'\n{body}\nEOF", root) == []  # a quoted body is not expanded


def test_f4_a_here_string_to_bash_holding_a_hash_is_refused_as_before():
    assert "cannot be read" in lift_refusal('bash <<< "ls # b"')
    assert lift_refusal('bash <<< "gov pause --off"')
