"""Builder tests for the W1-02 follow-up: reads of the settings file and
of the held-out file are refused (DEC-508, DEC-525), and the helper that
lists the registered hooks.

Regression evidence only (DEC-136).  Both files are stand-ins in a
temporary project; their paths come from the guard's own constants.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from gov.guard.decide import decide  # noqa: E402
from gov.guard.heldout import CONFIG_KEY, CONFIG_REL, SETTINGS_REL  # noqa: E402
from gov.guard.hooks import REDACTED, listing  # noqa: E402
from gov.guard.protected import (READ_REFUSAL, _braces, _glob_rx,  # noqa: E402
                                 _substitutions, _takes_folder, read_refusal)

FILES = (CONFIG_REL, SETTINGS_REL)
DENY = "Read(//stand-in/**)"


@pytest.fixture()
def project(tmp_path, monkeypatch):
    project = tmp_path / "project"
    listed = tmp_path / "elsewhere" / "stand-in"
    listed.mkdir(parents=True)
    for rel, text in ((CONFIG_REL, f"{CONFIG_KEY}:\n- {listed}\n"),
                      (SETTINGS_REL, json.dumps({
                          "permissions": {"deny": [DENY]},
                          "hooks": {"Stop": [{"hooks": [
                              {"type": "command", "command": f"echo {DENY} x"}]}]}}))):
        (project / rel).parent.mkdir(parents=True, exist_ok=True)
        (project / rel).write_text(text, encoding="utf-8")
        (project / rel).with_name("neighbour.md").write_text("x\n", encoding="utf-8")
    (project / "src").mkdir()
    (project / "docs").mkdir()
    (tmp_path / "link").symlink_to(project / SETTINGS_REL)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("STAND_IN_ROOT", str(project))
    monkeypatch.delenv("STAND_IN_UNSET", raising=False)
    return project


def _refused(project, tool_name, tool_input, cwd=None):
    return bool(read_refusal(tool_name, tool_input, str(project),
                             str(cwd or project)))


def _folder(rel):
    return os.path.dirname(rel)


def _ext(rel):
    return os.path.splitext(rel)[1]


# -- the file tools ------------------------------------------------------------

@pytest.mark.parametrize("rel", FILES)
def test_file_tool_reads_are_refused(project, tmp_path, rel):
    folder, name, ext = _folder(rel), os.path.basename(rel), _ext(rel)
    for tool_name, tool_input in (
        ("Read", {"file_path": rel}),
        ("Read", {"file_path": str(project / rel), "limit": 5}),
        ("Read", {"file_path": f"{project}/src/../{rel}"}),
        ("Grep", {"pattern": ".", "path": rel}),
        ("Grep", {"pattern": ".", "path": folder}),
        ("Grep", {"pattern": ".", "path": str(project / folder), "glob": f"*{ext}"}),
        ("Grep", {"pattern": ".", "path": str(project), "glob": f"*{ext}"}),
        ("Grep", {"pattern": ".", "glob": f"*.{{md,{ext[1:]}}}"}),
        ("Grep", {"pattern": ".", "glob": f"*.py *{ext}"}),
        ("Grep", {"pattern": ".", "path": str(project), "glob": f"{folder}/**"}),
        ("Grep", {"pattern": ".", "path": folder, "glob": "!*.py"}),
        ("Glob", {"pattern": "*", "path": str(project / folder)}),
        ("Glob", {"pattern": f"{folder}/*"}),
        ("Glob", {"pattern": f"{project}/{folder}/*{ext}"}),
        ("Glob", {"pattern": f"**/*{ext}", "path": str(project)}),
        ("Glob", {"pattern": f"**/{name}"}),
        ("Glob", {"pattern": f"**/{name[0]}?[a-z]*"}),
        ("Glob", {"pattern": "**/*"}),
        ("Glob", {"pattern": rel}),
    ):
        assert _refused(project, tool_name, tool_input), (tool_name, tool_input)


def test_a_read_through_a_symbolic_link_is_refused(project, tmp_path):
    assert _refused(project, "Read", {"file_path": str(tmp_path / "link")})
    assert _refused(project, "Grep", {"pattern": ".", "path": str(tmp_path / "link")})
    assert _refused(project, "Bash", {"command": f"cat {tmp_path / 'link'}"})


@pytest.mark.parametrize("rel", FILES)
def test_file_tool_calls_that_take_neither_file_in_are_let_through(project, rel):
    folder = _folder(rel)
    for tool_name, tool_input in (
        ("Read", {"file_path": f"{folder}/neighbour.md"}),
        ("Read", {"file_path": "src/missing.py"}),
        ("Grep", {"pattern": "x", "path": f"{folder}/neighbour.md"}),
        ("Grep", {"pattern": os.path.basename(rel), "path": "src"}),
        ("Grep", {"pattern": "x", "path": str(project), "glob": "*.py"}),
        ("Grep", {"pattern": "x", "path": str(project), "glob": "src/**"}),
        # The unrestricted search from the root is decided as before.
        ("Grep", {"pattern": "x", "path": str(project)}),
        ("Grep", {"pattern": "x"}),
        ("Glob", {"pattern": f"{folder}/neighbour.md"}),
        ("Glob", {"pattern": "**/*.py", "path": str(project)}),
        ("Glob", {"pattern": "src/**/*.py"}),
        ("Glob", {"pattern": f"*{_ext(rel)}"}),
        ("Write", {"file_path": str(project / rel), "content": "x"}),
        ("Edit", {"file_path": rel, "old_string": "a", "new_string": "b"}),
        ("Agent", {"prompt": f"Never read {rel}."}),
    ):
        assert not _refused(project, tool_name, tool_input), (tool_name, tool_input)


# -- the shell -----------------------------------------------------------------

@pytest.mark.parametrize("rel", FILES)
def test_shell_reads_are_refused(project, tmp_path, rel):
    folder, name = _folder(rel), os.path.basename(rel)
    for command in (
        f"cat {rel}",
        f"cat '{project / rel}'",
        f'cat "./{rel}"',
        f"cat src/../{rel}",
        f'cat "$STAND_IN_ROOT/{rel}"',
        f"cd {folder} && cat {name}",
        f"cat {folder}/*",
        f"cat README.md {rel}",
        f"X=1 head -20 {rel}",
        f"wc -c < {rel}",
        f"cat {rel} | wc -l",
        f"git status --porcelain && cat {rel}",
        f"grep -rn . {folder}",
        f"ls -la {folder}",
        f"find {folder} -type f",
        f"cp {rel} .gov-runtime/scratch/copy",
        f"cat {rel}; touch {rel}",
        f"sed -n p {rel}",
        f"python3 -c \"print(open('{rel}').read())\"",
        f"python3 -c \"import json; print(json.load(open('{project / rel}'))['hooks'])\"",
        f"jq .hooks {rel}",
        f"git diff {rel}",
        f"git diff --stat -p {rel}",
        f"git show HEAD:{rel}",
        f"git status -v {rel}",
        f"git diff --stat {rel} && cat {rel}",
        f"cat '{rel}",  # cannot be tokenised: the words are still read
    ):
        assert _refused(project, "Bash", {"command": command}), command


@pytest.mark.parametrize("rel", FILES)
def test_shell_commands_that_read_neither_file_are_let_through(project, rel):
    folder = _folder(rel)
    for command in (
        f"git diff --stat {rel}",
        f"git diff --stat -- {project / rel}",
        f"git status --short -- {rel}",
        "git status --porcelain",
        f"cat {folder}/neighbour.md",
        f"grep -n x {folder}/neighbour.md",
        "ls -la",
        "grep -rn x src/",
        "grep -rn x .",
        "find src -name '*.py'",
        "python3 -m gov.guard.hooks",
        # A write is decided by the allow-list, not here.
        f"echo '{{}}' > {rel}",
        f"cp docs/notes.md {rel}",
        f"sed -i s/a/b/ {rel}",
        f"mkdir -p {folder}",
        # What the command cannot be read for is not held (the residuals).
        f"cd $(pwd) && cat {os.path.basename(rel)}",
        f"cat $STAND_IN_UNSET/{rel}x",
    ):
        assert not _refused(project, "Bash", {"command": command}), command


# -- never raises, never refuses an ordinary call ------------------------------

@pytest.mark.parametrize("tool_name", ["Read", "Grep", "Glob", "Bash", "Write", "Other"])
@pytest.mark.parametrize("tool_input", [
    {},
    {"file_path": None, "path": 3, "glob": ["*"], "pattern": {}, "command": 7},
    {"file_path": "a\x00b", "path": "a\x00b", "pattern": "a\x00b/*", "command": "cat a\x00b"},
    {"file_path": "", "path": "", "glob": "", "pattern": "", "command": ""},
    {"pattern": "{[*", "glob": "}{,[", "command": "cat '{[* < > | && ; cd"},
    {"pattern": "/*", "path": "/", "command": "cd && cd - && cat ~nobody-here/x $"},
    {"file_path": "src/missing/deep.py", "path": "src/missing", "pattern": "src/missing/*",
     "command": "cat src/missing/deep.py"},
])
def test_an_odd_input_is_decided_without_an_error(project, tool_name, tool_input):
    assert not _refused(project, tool_name, tool_input)


def test_a_project_without_either_file_refuses_nothing(tmp_path):
    for tool_name, tool_input in (
        ("Read", {"file_path": SETTINGS_REL}),
        ("Glob", {"pattern": "**/*"}),
        ("Bash", {"command": f"cat {SETTINGS_REL}"}),
    ):
        assert not _refused(tmp_path, tool_name, tool_input)


def test_globs_are_matched_as_the_tools_read_them():
    assert _glob_rx("**/*.py").match("a/b/c.py")
    assert _glob_rx("**/*.py").match("c.py")
    assert not _glob_rx("*.py").match("a/c.py")
    assert _glob_rx("a/**").match("a/b/c")
    assert _glob_rx("*.{py,md}").match("c.md")
    assert not _glob_rx("*.{py,md}").match("c.yaml")
    assert _glob_rx("c.[a-z]?").match("c.md")
    assert _glob_rx("{a").match("a")


# -- more spellings of a read --------------------------------------------------

def test_braces_are_expanded_as_the_shell_expands_them():
    assert _braces("a") == ["a"]
    assert sorted(_braces("d/{a,b}")) == ["d/a", "d/b", "d/{a,b}"]
    assert set(_braces("{a,b{c,d}}x")) >= {"ax", "bcx", "bdx"}
    for word in ("{a}", "{a", "a,b}", "${HOME}", "", "{,"):
        assert _braces(word) == [word]
    assert len(_braces("{a,b}" * 40)) < 600


def test_the_commands_inside_substitutions_are_found():
    assert _substitutions("echo a") == []
    assert _substitutions("echo `cat a` \"`cat b`\"") == ["cat a", "cat b"]
    assert _substitutions('echo "$(cat a)" <(cat b) >(cat c)') == ["cat a", "cat b", "cat c"]
    assert sorted(_substitutions("echo $(cat $(cat a))")) == ["cat $(cat a)", "cat a"]
    assert _substitutions("(cd a && ls)") == []
    assert _substitutions("echo $(cat a") == ["cat a"]
    assert _substitutions("echo `cat a") == ["cat a"]
    assert _substitutions(")))($(") == [""]


def test_a_listing_or_a_search_with_no_path_takes_the_folder():
    for name, args in (("ls", []), ("ls", ["-la"]), ("rg", ["x"]), ("rg", ["--files"]),
                       ("grep", ["-r", "x"]), ("grep", ["-rn", "x"]), ("grep", ["x", "-R"]),
                       ("grep", ["--recursive", "x"])):
        assert _takes_folder(name, args), (name, args)
    for name, args in (("ls", ["src"]), ("rg", ["x", "src"]), ("grep", ["x"]),
                       ("grep", ["-n", "x"]), ("grep", ["-rn", "x", "src"]),
                       ("grep", ["--color", "x"]), ("cat", []), ("git", ["status"])):
        assert not _takes_folder(name, args), (name, args)


@pytest.mark.parametrize("rel", FILES)
def test_more_spellings_of_a_read_are_refused(project, rel):
    folder, name = _folder(rel), os.path.basename(rel)
    for tool_name, tool_input in (
        ("Grep", {"pattern": ".", "path": str(project), "glob": name}),
        ("Grep", {"pattern": ".", "glob": name}),
        ("Grep", {"pattern": ".", "path": str(project), "glob": f"/{rel}"}),
        ("Grep", {"pattern": ".", "path": str(project), "glob": f"{{{name},other.md}}"}),
        ("Grep", {"pattern": ".", "path": folder.split("/")[0], "glob": name}),
        ("Glob", {"pattern": f"{folder}/{{{name},other.md}}"}),
    ):
        assert _refused(project, tool_name, tool_input), (tool_name, tool_input)
    for command in (
        f"echo a;<{rel} cat",
        f"(<{rel} cat)",
        f"true&&<{rel} cat",
        f"true|<{rel} cat",
        f"echo $(<{rel})",
        f'echo "$(<{rel})"',
        f"cat <>{rel}",
        f"echo `cat {rel}`",
        f'echo "`cat {rel}`"',
        f"cat {folder}/{{{name},neighbour.md}}",
        f"cat {folder}/{{neighbour.md,{name}}}",
        f'git diff --stat "$(cat {rel})"',
        f"git diff --stat `cat {rel}`",
        f'git status "$(cat {rel})"',
        f"git status `cat {rel}`",
        f"git diff --stat <(cat {rel})",
        f'cat <<< "$(cat {rel})"',
        f"cd {folder} && grep -r VALUE",
        f"cd {folder} && rg VALUE",
        f"cd {folder}; grep -rn VALUE",
        f"cd {folder} && ls",
        f"cd -P {folder} && cat {name}",
        f"cd -- {folder} && cat {name}",
        f"pushd {folder} && cat {name}",
        f"python3 -m pytest @{rel}",
        f"gcc @{rel}",
        f"grep -f{rel} README.md",
    ):
        assert _refused(project, "Bash", {"command": command}), command
    assert _refused(project, "Bash", {"command": "grep -r VALUE"}, cwd=project / folder)


@pytest.mark.parametrize("rel", FILES)
def test_the_same_spellings_beside_the_files_are_let_through(project, rel):
    folder = _folder(rel)
    for tool_name, tool_input in (
        ("Grep", {"pattern": ".", "path": str(project), "glob": "neighbour.md"}),
        ("Grep", {"pattern": ".", "path": str(project), "glob": "/src/**"}),
        ("Glob", {"pattern": f"{folder}/{{neighbour.md,other.md}}"}),
    ):
        assert not _refused(project, tool_name, tool_input), (tool_name, tool_input)
    for command in (
        f"cd {folder} && cat neighbour.md",
        f"wc -c < {folder}/neighbour.md",
        f"cat {folder}/{{neighbour.md,other.md}}",
        'git diff --stat "$(git rev-parse HEAD)"',
        'git status "$(git rev-parse --show-toplevel)"',
        f'git diff --stat "$(git rev-parse HEAD)" -- {rel}',
        "ls -la",
        "git status --short",
        "git add -A",
        'git commit -m "a text (with `ticks` and $(words))"',
        "python3 -m pytest tests/acceptance/W1-02",
        f"cd {project} && ls -la",
        f"cd {project} && rg VALUE",
        "grep -rn VALUE src tests",
        "grep -rn VALUE src | wc -l",
        "echo $(ls src) `ls docs`",
        "wc -c < README.md",
        f"cd {folder} && git status --short",
        "pushd src && ls && popd",
        "cat <<EOF",
        "pushd && pushd +1 && cd -P && cd --",
    ):
        assert not _refused(project, "Bash", {"command": command}), command
    assert not _refused(project, "Bash", {"command": "ls -la"}, cwd=project / "src")


# -- the decision --------------------------------------------------------------

@pytest.mark.parametrize("role", [None, "developer", "orchestrator", "engineer"])
@pytest.mark.parametrize("rel", FILES)
def test_the_decision_refuses_a_read_for_every_role(project, role, rel):
    for tool_name, tool_input in (
        ("Read", {"file_path": str(project / rel)}),
        ("Bash", {"command": f"cat {rel}"}),
    ):
        decision, reason = decide(tool_name, tool_input, str(project), role, None,
                                  cwd=str(project), flag="frozen")
        assert (decision, reason) == ("deny", READ_REFUSAL)
    assert "DEC-508" in READ_REFUSAL and "DEC-525" in READ_REFUSAL
    assert os.path.basename(CONFIG_REL) not in READ_REFUSAL


def test_the_decision_on_a_write_to_the_settings_file_is_the_allow_list_s(project):
    for tool_name, tool_input in (
        ("Write", {"file_path": str(project / SETTINGS_REL), "content": "{}"}),
        ("Bash", {"command": f"cp docs/notes.md {SETTINGS_REL}"}),
    ):
        args = (tool_name, tool_input, str(project))
        assert decide(*args, "orchestrator", None, cwd=str(project), flag="absent")[0] == "allow"
        decision, reason = decide(*args, "engineer", None, cwd=str(project), flag="absent")
        assert decision == "deny" and reason != READ_REFUSAL


# -- the helper ----------------------------------------------------------------

def test_the_listing_holds_the_hooks_with_a_deny_value_redacted(project):
    settings = json.loads((project / SETTINGS_REL).read_text(encoding="utf-8"))
    assert listing(settings) == [
        {"event": "Stop", "matcher": "", "command": f"echo {REDACTED} x"}]


@pytest.mark.parametrize("settings", [
    None, [], {}, {"hooks": []}, {"hooks": {"Stop": "x"}}, {"hooks": {"Stop": ["x"]}},
    {"hooks": {"Stop": [{"hooks": "x"}]}}, {"hooks": {"Stop": [{"hooks": [1, {"command": 2}]}]}},
    {"permissions": [], "hooks": {}}, {"permissions": {"deny": "x"}},
])
def test_a_settings_file_of_another_shape_lists_no_hook(settings):
    assert listing(settings) == []


def test_the_helper_states_a_file_it_cannot_read_in_one_fixed_line(project):
    (project / SETTINGS_REL).write_text(f"deny: {DENY}", encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(REPO / "src"), "CLAUDE_PROJECT_DIR": str(project)}
    run = subprocess.run([sys.executable, "-m", "gov.guard.hooks"], capture_output=True,
                         text=True, env=env, cwd=str(project), check=False)
    assert (run.returncode, run.stdout) == (1, "")
    assert run.stderr == f"{SETTINGS_REL} cannot be read\n"
