"""W2-42a, the product's write parser (``gov.guard.decide._extract_bash_write_targets``, as gov.guard exposes it
today): KPI lines 1 to 5, 7 and 8, and failure line 2 (an unknown or unparseable form still fails closed).

Each case runs in a folder of its own (``tmp_path``) with no session variable set and none of the command's own
variables in the environment, so a target is resolved only by the command's text. The parser's answer: a list of
real paths written, the sentinel among them for a write it cannot resolve, or None (or no target) for no write.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w2_42a_support as s  # noqa: E402

U = s.UNRESOLVABLE


@pytest.fixture
def at(tmp_path, monkeypatch):
    """The case's folder (real path), with every variable a case's command names unset."""
    for name in ("W242A_B", "W242A_T", "W242A_H", "W242A_D", "W242A_F", "W242A_S", "W242A_X"):
        monkeypatch.delenv(name, raising=False)
    for name in s._SESSION:
        monkeypatch.delenv(name, raising=False)
    return os.path.realpath(str(tmp_path))


def targets(command, cwd):
    got = s.parse(command, cwd)
    return set(got or [])


# -- KPI line 1: a heredoc's body is not read as shell -----------------------------------------------------------

def test_kpi1_a_data_body_for_cat_is_no_write_and_its_quotes_do_not_break_the_reading(at):
    body = "it's a brief: > not a redirect, rm -rf x, touch y\n"
    assert targets(f"cat > {at}/a.md <<'EOF'\n{body}EOF", at) == {f"{at}/a.md"}


def test_kpi1_a_data_body_for_tee_is_no_write(at):
    assert targets(f"tee {at}/a.md <<'EOF'\necho x > {at}/b\ntouch {at}/c\nEOF", at) == {f"{at}/a.md"}


def test_kpi1_a_data_body_for_grep_is_no_write(at):
    assert not s.parse(f"grep -c touch <<'EOF'\ntouch {at}/b\necho x > {at}/c\nEOF", at)


def test_kpi1_a_quoted_data_body_s_substitution_is_text(at):
    assert targets(f"cat > {at}/a.md <<'EOF'\n$(touch {at}/b)\nEOF", at) == {f"{at}/a.md"}


def test_kpi1_an_unquoted_data_body_s_substitution_is_judged(at):
    got = targets(f"cat > {at}/a.md <<EOF\nnote: $(touch {at}/b)\nEOF", at)
    assert f"{at}/a.md" in got and f"{at}/b" in got


@pytest.mark.parametrize("shell", ["bash", "sh"])
def test_kpi1_a_shell_body_is_judged_as_commands(at, shell):
    assert f"{at}/b" in targets(f"{shell} <<'EOF'\necho start\ntouch {at}/b\nEOF", at)


# -- KPI line 2: the command's own variables and literal loops ----------------------------------------------------

def test_kpi2_a_variable_set_once_at_the_top_before_use_is_expanded(at):
    assert targets(f"W242A_B={at}/x; mkdir -p $W242A_B/r && echo x > $W242A_B/r/f", at) == \
        {f"{at}/x/r", f"{at}/x/r/f"}


def test_kpi2_a_variable_built_from_one_set_before_it_is_expanded(at):
    assert targets(f"W242A_T={at}/a; W242A_H=$W242A_T/p; touch $W242A_H", at) == {f"{at}/a/p"}


def test_kpi2_a_literal_for_loop_s_words_are_judged_one_by_one(at):
    assert targets(f"for W242A_F in one two; do touch {at}/$W242A_F.txt; done", at) == \
        {f"{at}/one.txt", f"{at}/two.txt"}


@pytest.mark.parametrize("command", [
    "touch {at}/$W242A_D/f; W242A_D=x",                                  # used before it is set
    "if true; then W242A_D={at}/d; fi; touch $W242A_D/f",               # set inside an if
    "read W242A_D <<< {at}/d; touch $W242A_D/f",                         # set by read
    "W242A_D={at}/d | true; touch $W242A_D/f",                           # set in a pipeline's subshell
    "for W242A_F in $(ls {at}); do touch {at}/$W242A_F; done",           # a loop over a substitution
], ids=["used-before-set", "set-in-if", "set-by-read", "set-in-pipeline", "loop-over-substitution"])
def test_kpi2_any_other_binding_is_unresolvable(at, command):
    assert U in targets(command.replace("{at}", at), at)


# -- KPI line 3: substitutions in quotes, sh -c, eval, keywords and prefixes ---------------------------------------

@pytest.mark.parametrize("command", [
    'echo "$(touch {at}/b)"',
    'echo "`touch {at}/b`"',
    "sh -c 'touch {at}/b'",
    'bash -c "echo x > {at}/b"',
    "eval 'touch {at}/b'",
], ids=["dollar-paren-in-double-quotes", "backticks-in-double-quotes", "sh-c", "bash-c", "eval"])
def test_kpi3_a_substitution_in_quotes_sh_c_and_eval_are_judged_as_commands(at, command):
    assert f"{at}/b" in targets(command.replace("{at}", at), at)


@pytest.mark.parametrize("command", [
    "if true; then rm -f {at}/b; fi",
    "while false; do touch {at}/b; done",
    "{ touch {at}/b; }",
    "! touch {at}/b",
], ids=["then", "do", "brace", "bang"])
def test_kpi3_shell_keywords_are_not_the_command_s_name(at, command):
    assert f"{at}/b" in targets(command.replace("{at}", at), at)


@pytest.mark.parametrize("prefix", ["timeout 5", "env W242A_X=1", "nohup", "nice -n 5", "command"])
def test_kpi3_prefixes_are_not_the_command_s_name(at, prefix):
    assert f"{at}/b" in targets(f"{prefix} touch {at}/b", at)


# -- KPI line 4: an unmatched glob is the literal path bash passes ------------------------------------------------

def test_kpi4_an_unmatched_glob_is_its_literal_path(at):
    assert targets(f"rm -f {at}/nothing-*.json", at) == {f"{at}/nothing-*.json"}


def test_kpi4_an_unmatched_glob_after_a_cd_is_its_literal_path(at):
    os.mkdir(f"{at}/probe")
    assert targets(f"cd {at}/probe && rm -f chain-*.json", at) == {f"{at}/probe/chain-*.json"}


def test_kpi4_a_matched_glob_is_still_its_matches(at):
    for n in ("a", "b"):
        open(f"{at}/{n}.json", "w").close()
    assert targets(f"rm -f {at}/*.json", at) == {f"{at}/a.json", f"{at}/b.json"}


# -- KPI line 5: the writes the parser did not read ---------------------------------------------------------------

@pytest.mark.parametrize("command", [
    "git checkout HEAD -- {at}/f",
    "git checkout -- {at}/f",
    "git restore {at}/f",
    "git restore --source HEAD~1 {at}/f",
    "git rm -q {at}/f",
    "dd if=/dev/zero of={at}/f bs=1 count=1",
    "truncate -s 0 {at}/f",
    "sort -o {at}/f {at}/in.txt",
], ids=["git-checkout-rev", "git-checkout", "git-restore", "git-restore-source", "git-rm", "dd-of", "truncate",
        "sort-o"])
def test_kpi5_the_named_writers_write_their_paths(at, command):
    assert f"{at}/f" in targets(command.replace("{at}", at), at)


def test_kpi5_git_mv_writes_both_paths(at):
    got = targets(f"git mv {at}/a {at}/b", at)
    assert f"{at}/a" in got and f"{at}/b" in got


def test_kpi5_rsync_writes_into_its_destination(at):
    os.mkdir(f"{at}/src")
    open(f"{at}/src/x", "w").close()
    got = targets(f"rsync -a {at}/src/ {at}/dst/", at)
    assert any(t == f"{at}/dst" or t.startswith(f"{at}/dst/") for t in got), got


@pytest.mark.parametrize("command", ["git apply {at}/x.patch", "git am {at}/x.mbox", "patch -p1 < {at}/x.patch"],
                         ids=["git-apply", "git-am", "patch"])
def test_kpi5_patch_appliers_write_unresolvable_targets(at, command):
    assert U in targets(command.replace("{at}", at), at)


# -- KPI line 7: a backslash-newline outside single quotes is removed ------------------------------------------

def test_kpi7_a_continued_word_is_one_word(at):
    assert targets(f"echo a > {at}/accep\\\ntance", at) == {f"{at}/acceptance"}


def test_kpi7_a_continued_command_writes_its_target(at):
    assert targets(f"touch \\\n{at}/f", at) == {f"{at}/f"}


def test_kpi7_a_continued_copy_writes_its_destination_and_nothing_with_a_newline(at):
    got = targets(f"cp {at}/x \\\n  {at}/y", at)
    assert f"{at}/y" in got and not any("\n" in t for t in got), got


def test_kpi7_a_backslash_newline_inside_single_quotes_is_kept(at):
    assert targets(f"printf 'a\\\nb' > {at}/c.txt", at) == {f"{at}/c.txt"}


# -- KPI line 8: a written heredoc body that the command may run ----------------------------------------------

def test_kpi8_a_script_written_then_run_by_bash_is_judged_as_its_code(at):
    got = targets(f"cat > {at}/s.sh <<'EOF'\ntouch {at}/w\nEOF\nbash {at}/s.sh", at)
    assert f"{at}/s.sh" in got and f"{at}/w" in got


def test_kpi8_a_script_written_after_a_cd_then_run_by_its_path_is_judged(at):
    got = targets(f"cd {at} && cat > s.sh <<'EOF'\ntouch {at}/w\nEOF\nchmod +x s.sh && ./s.sh", at)
    assert f"{at}/w" in got or U in got
    assert f"{at}/s.sh" in got


def test_kpi8_a_python_file_written_then_run_is_its_code_or_unresolvable(at):
    got = targets(f"cat > {at}/s.py <<'EOF'\nopen('{at}/w', 'w').write('x')\nEOF\npython3 {at}/s.py", at)
    assert f"{at}/w" in got or U in got


def test_kpi8_a_run_the_parser_cannot_read_is_unresolvable(at):
    got = targets(f"cat > {at}/s.rb <<'EOF'\nFile.write('{at}/w', 'x')\nEOF\nruby {at}/s.rb", at)
    assert U in got


def test_kpi8_a_run_by_a_word_that_does_not_expand_is_unresolvable(at):
    got = targets(f"W242A_S=$(mktemp); cat > $W242A_S <<'EOF'\ntouch {at}/w\nEOF\nbash $W242A_S", at)
    assert U in got


def test_kpi8_a_written_file_that_is_only_read_is_judged_as_data(at):
    got = targets(f"cat > {at}/b.md <<'EOF'\ntouch {at}/w\nEOF\nwc -l {at}/b.md && cat {at}/b.md", at)
    assert got == {f"{at}/b.md"}


# -- failure line 2: an unknown or unparseable form fails closed -------------------------------------------------

@pytest.mark.parametrize("command", [
    'echo "unclosed > {at}/f',
    "eval \"$W242A_X\"",
    "sh -c \"$W242A_X\"",
    "bash -c 'echo \"x > {at}/f'",
], ids=["unbalanced-quotes", "eval-of-an-unknown-word", "sh-c-of-an-unknown-word", "unbalanced-inside-sh-c"])
def test_failure2_an_unparseable_or_unknown_form_is_unresolvable(at, command):
    assert U in targets(command.replace("{at}", at), at)


@pytest.mark.parametrize("command", [
    "cat > {at}/f <<EOF\nno end",
    "echo $((1<<2)) > {at}/f",
], ids=["unterminated-heredoc", "shift-in-arithmetic"])
def test_failure2_a_form_read_uncertainly_keeps_its_write(at, command):
    got = targets(command.replace("{at}", at), at)
    assert f"{at}/f" in got or U in got
