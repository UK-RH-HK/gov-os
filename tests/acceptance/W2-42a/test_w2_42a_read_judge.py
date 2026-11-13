"""W2-42a, the product's read judge (``gov.guard.reads.policy_refusal``, which runs ``_set_aside`` and
``_Judge.tool``/``command``, as gov.guard exposes it today): KPI lines 6, 7 and 10, and failure line 2.

Each case judges a Bash call of a research session in a project of its own (``w2_42a_support.project``) whose
evaluation set measures the research role and whose hidden part holds a file, so the listing rule (DEC-820 (d),
"the call reads files whose names another command gives at run time") is live, as for the sessions it refused
(log lines 61, 75, 78 to 80). HOME is a folder of the case's own, so no real run clone is looked at.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w2_42a_support as s  # noqa: E402


@pytest.fixture
def root(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    (tmp_path / "home").mkdir()
    for name in s._SESSION:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv("n", raising=False)
    return s.project(tmp_path)


@pytest.fixture
def out(tmp_path):
    folder = tmp_path / "out"
    folder.mkdir()
    (folder / "out.txt").write_text("passed\n")
    return os.path.realpath(str(folder))


def refused(why):
    return bool(why)


# -- KPI line 6: $((...)) is no substitution; a data heredoc's body is no command --------------------------------

@pytest.mark.parametrize("command", [
    'n=5; sed -n "${n},$((n+6))p" docs/DECISION_REGISTER.md',
    'for n in 3 9; do sed -n "${n},$((n+2))p" docs/DECISION_REGISTER.md | cut -c1-70; echo ====; done',
], ids=["arithmetic-in-sed", "arithmetic-in-a-read-loop"])
def test_kpi6_arithmetic_is_no_command_substitution(root, command):
    assert s.judge(command, root) == ""


def test_kpi6_a_data_body_naming_a_secret_is_no_read(root, out):
    assert s.judge(f"cat > {out}/p.py <<'EOF'\n# stages a stand-in\ncat .env\nEOF", root) == ""


def test_kpi6_a_data_body_for_tee_naming_a_key_is_no_read(root, out):
    assert s.judge(f"tee {out}/x.txt <<'EOF'\ncat ~/.ssh/id_ed25519\nEOF", root) == ""


def test_kpi6_a_data_body_holding_a_listing_loop_is_no_listing(root, out):
    command = f"cat > {out}/n.md <<'EOF'\nfor f in $(ls fixtures); do cat $f; done\nEOF"
    assert s.judge(command, root) == ""


def test_kpi6_a_shell_body_is_still_read(root):
    _, secret, _ = s.refusal_texts()
    assert s.judge("bash <<'EOF'\ncat .env\nEOF", root) == secret


def test_kpi6_an_unquoted_data_body_s_substitution_is_still_read(root, out):
    _, secret, _ = s.refusal_texts()
    assert s.judge(f"cat > {out}/x <<EOF\n$(cat .env)\nEOF", root) == secret


def test_kpi6_a_substitution_inside_arithmetic_is_still_read(root):
    _, secret, _ = s.refusal_texts()
    assert s.judge("echo $(( $(cat .env | wc -l) + 1 ))", root) == secret


def test_kpi6_a_plain_secret_read_is_still_refused(root):
    _, secret, _ = s.refusal_texts()
    assert s.judge("cat .env", root) == secret


# -- KPI line 7: a backslash-newline is removed before the command is read ---------------------------------------

def test_kpi7_a_secret_named_across_a_continued_line_is_refused(root):
    _, secret, _ = s.refusal_texts()
    assert s.judge("cat .e\\\nnv", root) == secret


def test_kpi7_a_hidden_file_named_across_a_continued_line_is_refused(root):
    _, _, hidden = s.refusal_texts()
    assert s.judge("cat fixtures/evaluation/w242a/hid\\\nden/q01.txt", root) == hidden


# -- KPI line 10: a literal path is not a run-time listing --------------------------------------------------------

def test_kpi10_a_loop_over_seq_reading_a_literal_file_is_judged_by_that_file(root, out):
    command = f'for i in $(seq 1 16); do grep -q "passed\\|failed" {out}/out.txt 2>/dev/null && break; sleep 1; done'
    assert s.judge(command, root) == ""


@pytest.mark.parametrize("command", [
    "head -n $(wc -l < docs/visible.md) docs/DECISION_REGISTER.md",
    'tail -n "$(nproc)" docs/DECISION_REGISTER.md',
    "sed -n \"$(date +%d)p\" docs/DECISION_REGISTER.md",
], ids=["wc-count", "nproc", "date"])
def test_kpi10_a_substitution_that_yields_no_file_name_leaves_the_literal_files(root, command):
    assert s.judge(command, root) == ""


def test_kpi10_a_python_heredoc_naming_its_files_literally_is_judged_by_them(root):
    command = ("python3 - <<'EOF'\nfrom pathlib import Path\np = Path(\"docs/visible.md\")\ns = p.read_text()\n"
               "reps = [('''budget \"$s\" \"$(ncpus \"$s\")\" \"$WORKERS\"''', 'x')]\n"
               "for a, b in reps:\n    s = s.replace(a, b)\nprint(len(s))\nEOF\n"
               "grep -n budget docs/visible.md")
    assert s.judge(command, root) == ""


def test_kpi10_a_data_heredoc_appended_to_a_record_is_judged_by_its_file(root, out):
    command = (f"cat >> {out}/incident.md <<'EOF'\n\n## Fix\n- **Built:** the check's pools (`c1257869b963`); "
               "each slot's `taskset -c` share; for s in $(ls fixtures); do cat $s; done\n"
               "- the gate's `--held` form, it's the nightly's\nEOF")
    assert s.judge(command, root) == ""


@pytest.mark.parametrize("command", [
    "for f in $(cat {out}/list.txt); do cat \"$f\"; done",
    "cat $(find . -name '*.txt')",
    "for f in $(ls fixtures/evaluation/w242a/hidden); do cat fixtures/evaluation/w242a/hidden/$f; done",
    "find . -type f | xargs cat",
], ids=["names-from-a-file", "find-substitution", "ls-of-the-hidden-folder", "xargs-from-find"])
def test_kpi10_names_given_at_run_time_are_still_judged_as_a_listing(root, out, command):
    with open(f"{out}/list.txt", "w") as f:
        f.write("fixtures/evaluation/w242a/hidden/q01.txt\n")
    assert refused(s.judge(command.replace("{out}", out), root))


def test_kpi10_a_literal_hidden_file_is_still_refused(root):
    _, _, hidden = s.refusal_texts()
    assert s.judge("cat fixtures/evaluation/w242a/hidden/q01.txt", root) == hidden


# -- failure line 2: an unparseable read still fails closed --------------------------------------------------------

def test_failure2_an_unparseable_command_naming_a_secret_is_refused(root):
    _, secret, _ = s.refusal_texts()
    assert s.judge('cat .env "unclosed', root) == secret
