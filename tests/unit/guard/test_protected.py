"""Builder tests for the W1-02 follow-up: reads of the settings file and
of the held-out file are refused (DEC-508, DEC-525), and the helper that
lists the registered hooks.

Regression evidence only (DEC-136).  Both files are stand-ins in a
temporary project; their paths come from the guard's own constants.
"""

from __future__ import annotations

import json
import os
import random
import re
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from gov.guard.decide import LONG_REFUSAL, MOST_READ, decide  # noqa: E402
from gov.guard.heldout import CONFIG_KEY, CONFIG_REL, SETTINGS_REL  # noqa: E402
from gov.guard.hooks import REDACTED, listing  # noqa: E402
from gov.guard.protected import (NUL_REFUSAL, READ_REFUSAL,  # noqa: E402
                                 SEARCH_REFUSAL, _braces, _glob_rx, _options,
                                 _shell_search, _substitutions, _takes_folder,
                                 read_refusal)

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
        # DEC-557: the unrestricted search from the root.
        ("Grep", {"pattern": "x", "path": str(project)}),
        ("Grep", {"pattern": "x"}),
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
        "grep -rn x .",  # DEC-557: the unrestricted search from the root
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
    {"file_path": "", "path": "", "glob": "", "pattern": "", "command": ""},
    {"pattern": "{[*", "glob": "}{,[", "command": "cat '{[* < > | && ; cd"},
    {"pattern": "/*", "path": "/", "command": "cd && cd - && cat ~nobody-here/x $"},
    {"file_path": "src/missing/deep.py", "path": "src/missing", "pattern": "src/missing/*",
     "command": "cat src/missing/deep.py"},
])
def test_an_odd_input_is_decided_without_an_error(project, tool_name, tool_input):
    # DEC-557: a Grep call that gives no path and no glob searches from the root.
    path, glob = tool_input.get("path"), tool_input.get("glob")
    from_the_root = tool_name == "Grep" and not (isinstance(path, str) and path) and not (
        isinstance(glob, str) and glob)
    assert _refused(project, tool_name, tool_input) == from_the_root


NUL_INPUT = {"file_path": "a\x00b", "path": "a\x00b", "pattern": "a\x00b/*",
             "command": "cat a\x00b"}


@pytest.mark.parametrize("tool_name", ["Read", "Grep", "Glob", "Bash", "Write", "Other"])
def test_a_nul_byte_in_a_path_or_a_command_is_refused_in_every_project(
        project, tmp_path, monkeypatch, tool_name):
    """DEC-562.  A writing tool's path is the allow-list's, as before."""
    expected = NUL_REFUSAL if tool_name in ("Read", "Grep", "Glob", "Bash") else ""
    for root in (project, tmp_path):
        assert read_refusal(tool_name, NUL_INPUT, str(root), str(root)) == expected
    monkeypatch.delenv("HOME")
    assert read_refusal(tool_name, NUL_INPUT, str(tmp_path), str(tmp_path)) == expected


def test_a_nul_byte_is_refused_in_each_field_that_is_a_path_a_glob_or_a_command(tmp_path):
    for tool_name, tool_input in (
        ("Read", {"file_path": "\x00"}), ("Grep", {"pattern": "x", "path": "src\x00"}),
        ("Grep", {"pattern": "x", "path": "src", "glob": "*.py\x00"}),
        ("Glob", {"pattern": "\x00**"}), ("Glob", {"pattern": "*", "path": "\x00src"}),
        ("Bash", {"command": "ls ~\x00"}), ("Bash", {"command": "\x00"}),
        ("Bash", {"command": "git commit -m 'one\x00two'"}),
    ):
        assert read_refusal(tool_name, tool_input, str(tmp_path), str(tmp_path)) == NUL_REFUSAL
    # The text a search looks for is no path, and a spelled byte is none.
    for tool_name, tool_input in (
        ("Grep", {"pattern": "a\x00b", "path": "src", "glob": "*.py"}),
        ("Grep", {"pattern": "\\0", "path": "src"}),
        ("Bash", {"command": "printf 'a\\0b' | wc -c"}),
        ("Bash", {"command": "git ls-files -z src"}),
    ):
        assert not _refused(tmp_path, tool_name, tool_input), (tool_name, tool_input)


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
        f"cd {project} && rg VALUE",  # DEC-557: the unrestricted search from the root
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


# -- copies and second names (DEC-548) -----------------------------------------

@pytest.fixture()
def site(project, tmp_path):
    """A folder beside the project, and the stand-in home, with copies."""
    site = tmp_path / "site"
    for root, rels in ((site, FILES), (tmp_path / "home", (SETTINGS_REL,))):
        for rel in rels:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text("x\n", encoding="utf-8")
            (root / rel).with_name("neighbour.md").write_text("x\n", encoding="utf-8")
    (site / "src").mkdir()
    return site


@pytest.mark.parametrize("rel", FILES)
def test_a_copy_is_refused_as_the_file_is(project, site, rel):
    copy, folder, name = site / rel, site / _folder(rel), os.path.basename(rel)
    for tool_name, tool_input, cwd in (
        ("Read", {"file_path": str(copy)}, None),
        ("Read", {"file_path": rel}, site),
        ("Grep", {"pattern": "x", "path": str(folder)}, None),
        ("Grep", {"pattern": "x", "path": str(site), "glob": f"*{_ext(rel)}"}, None),
        ("Grep", {"pattern": "x", "path": str(site), "glob": name}, None),
        ("Glob", {"pattern": f"**/{name}", "path": str(site)}, None),
        ("Glob", {"pattern": f"{folder}/*"}, None),
        ("Glob", {"pattern": "**/*", "path": str(site)}, None),
        ("Bash", {"command": f"cat {copy}"}, None),
        ("Bash", {"command": f"cd {site} && cat {rel}"}, None),
        ("Bash", {"command": f"wc -c < {copy}"}, None),
        ("Bash", {"command": f"ls -la {folder}"}, None),
        ("Bash", {"command": f"python3 -c \"open('{copy}')\""}, None),
        ("Bash", {"command": f"mv {copy} docs/moved"}, None),
        # DEC-557: the unrestricted search from the copy's folder.
        ("Grep", {"pattern": "x", "path": str(site)}, None),
        ("Bash", {"command": f"grep -rn x {site}"}, None),
    ):
        assert _refused(project, tool_name, tool_input, cwd), (tool_name, tool_input)


def test_the_user_level_settings_file_is_a_copy(project, site):
    for command in (f"cat ~/{SETTINGS_REL}", f"cat $HOME/{SETTINGS_REL}",
                    f"ls ~/{_folder(SETTINGS_REL)}", f"ln -s ~/{SETTINGS_REL} docs/second"):
        assert _refused(project, "Bash", {"command": command}), command
    for command in ("ls ~", f"cat ~/{_folder(SETTINGS_REL)}/neighbour.md",
                    f"echo x > ~/{SETTINGS_REL}"):
        assert not _refused(project, "Bash", {"command": command}), command


@pytest.mark.parametrize("rel", FILES)
def test_what_is_beside_or_above_a_copy_is_let_through(project, site, rel):
    copy = site / rel
    for tool_name, tool_input in (
        ("Read", {"file_path": str(copy.with_name("neighbour.md"))}),
        ("Read", {"file_path": str(copy.with_name("missing")) + "/" + rel}),
        ("Grep", {"pattern": "x", "path": str(site), "glob": "*.py"}),
        ("Grep", {"pattern": "x", "path": str(site / "src")}),
        ("Glob", {"pattern": "**/*.py", "path": str(site)}),
        ("Bash", {"command": f"ls -la {site}"}),
        ("Bash", {"command": f"cd {site} && ls && git status --short"}),
        ("Bash", {"command": f"git diff --stat {copy}"}),
        ("Bash", {"command": f"echo x > {copy}"}),
        ("Write", {"file_path": str(copy), "content": "x"}),
    ):
        assert not _refused(project, tool_name, tool_input), (tool_name, tool_input)


@pytest.mark.parametrize("rel", FILES)
def test_a_second_name_for_a_file_is_a_read(project, rel):
    for command in (
        f"mv {rel} docs/moved", f"mv -t docs {rel}", f"mv {project / rel} docs",
        f"mv {_folder(rel)}/* docs", f"ln {rel} docs/second", f"link {rel} docs/second",
        f"ln -s {project / rel} docs/second", f"cp -l {rel} docs/linked",
        f"cp --link {rel} docs/linked", f"cp -al {rel} docs/linked",
        f"sed -i.bak s/a/b/ {rel}", f"sed -i .bak s/a/b/ {rel}",
        f"sed --in-place=.bak s/a/b/ {rel}", f"echo $(mv {rel} docs/moved)",
    ):
        assert _refused(project, "Bash", {"command": command}), command


@pytest.mark.parametrize("rel", FILES)
def test_a_plain_write_or_a_second_name_for_another_file_is_no_read(project, rel):
    beside = f"{_folder(rel)}/neighbour.md"
    for command in (
        f"mv docs/new {rel}", f"cp docs/new {rel}", f"cp -l docs/new {rel}",
        f"sed -i s/a/b/ {rel}", f"sed --in-place s/a/b/ {rel}", f"echo x > {rel}",
        "mv docs/a docs/b", "git mv docs/a docs/b", "ln -s docs/a docs/b", "ln docs/a",
        "cp -al docs src/copy", "sed -i.bak s/a/b/ docs/a", "sed -i .bak s/a/b/ docs/a",
        f"mv {beside} docs/b", f"ln {beside} docs/b", f"sed -i.bak s/a/b/ {beside}",
        "mv", "ln", "cp -l", "sed -i", "mv --t", "mv -t",
    ):
        assert not _refused(project, "Bash", {"command": command}), command


# -- wildcards alone from a copy's folder, a holding folder's second name (DEC-553) --

def test_wildcards_alone_from_a_copy_s_folder_are_refused_as_from_the_root(project, site):
    home = os.environ["HOME"]
    depth = "/".join("*" * len(SETTINGS_REL.split("/")))
    for start in (project, site, home):
        for tool_name, tool_input in (
            ("Glob", {"pattern": "**/*", "path": str(start)}),
            ("Glob", {"pattern": f"{start}/{depth}"}),
            ("Grep", {"pattern": "x", "path": str(start), "glob": "*"}),
            ("Grep", {"pattern": "x", "path": str(start), "glob": f"/{depth}"}),
            ("Bash", {"command": f"cat {start}/**"}),
            ("Bash", {"command": f"cd {start} && ls -d */**"}),
        ):
            assert _refused(project, tool_name, tool_input), (tool_name, tool_input)
        for tool_name, tool_input in (
            ("Glob", {"pattern": "*", "path": str(start)}),
            ("Glob", {"pattern": "*/*/*/*/*/*", "path": str(start)}),
            ("Glob", {"pattern": "**/*", "path": f"{start}/src"}),
            ("Bash", {"command": f"ls {start}/*"}),
            ("Bash", {"command": f"cat {start}/src/**/*"}),
        ):
            assert not _refused(project, tool_name, tool_input), (tool_name, tool_input)
    for command in ("cat ~/**/*", "cat $HOME/**", "cd && cat */*"):
        assert _refused(project, "Bash", {"command": command}), command


@pytest.mark.parametrize("rel", FILES)
def test_a_second_name_for_a_holding_folder_is_a_read(project, site, rel):
    parts = rel.split("/")
    for root in (project, site):
        for n in range(1, len(parts)):
            folder = "/".join([str(root)] + parts[:n])
            for command in (
                f"mv {folder} docs/moved", f"mv {folder}/ docs/moved", f"mv -t docs {folder}",
                f"mv {folder} {folder}-renamed", f"ln {folder} docs/second",
                f"ln -s {folder} docs/second", f"cp -rl {folder} docs/linked",
                f"cp -al {folder} docs/linked", f"cp -r --link {folder} docs/linked",
                f"cd {root} && mv {'/'.join(parts[:n])} moved",
            ):
                assert _refused(project, "Bash", {"command": command}), command
    for command in (f"mv ~/{_folder(SETTINGS_REL)} docs/moved",
                    f'cp -al "${{HOME}}/{_folder(SETTINGS_REL)}" docs/linked'):
        assert _refused(project, "Bash", {"command": command}), command
    for command in ("mv docs src/docs", "ln -s docs src/docs", "cp -al src docs/src",
                    "mv -t docs src", f"mv {site}/src docs/moved", f"ln {site} docs/second",
                    f"mv {site} docs/moved", "mv ~ docs/moved", "git mv docs src/docs"):
        assert not _refused(project, "Bash", {"command": command}), command


@pytest.mark.parametrize("tool_input", [
    {"file_path": "\udcff/x", "path": "\udcff", "pattern": "\udcff/*", "glob": "\udcff",
     "command": "mv \udcff docs/b"},
    {"file_path": "x" * 70000, "path": "x/" * 9000, "pattern": "x" * 70000 + "/*",
     "command": "ln " + "x" * 70000 + " docs/b"},
    {"file_path": 1, "path": None, "pattern": [], "glob": {}, "command": 2},
    {"command": "mv 'a docs/b"}, {"command": "sed -i.bak ((( $("}, {},
])
def test_an_odd_input_is_decided_without_an_error_with_or_without_a_home(
        tmp_path, monkeypatch, tool_input):
    for home in (str(tmp_path / "missing"), None):
        if home is None:
            monkeypatch.delenv("HOME")
        else:
            monkeypatch.setenv("HOME", home)
        for tool_name in ("Read", "Grep", "Glob", "Bash", "Write"):
            assert not _refused(tmp_path, tool_name, tool_input)
        for command in ("cd && ls", "cat ~/notes.md", "ls $HOME"):
            assert not _refused(tmp_path, "Bash", {"command": command})


# -- a search from the root, a name filter, an answer in bounded time (DEC-557, DEC-562) --

def _old_glob_rx(pattern):
    """The matcher this round replaced, as it was: what the new one is compared with."""
    out = []
    depth = i = 0
    while i < len(pattern):
        c = pattern[i]
        i += 1
        if pattern.startswith("**/", i - 1):
            out.append("(?:.*/)?")
            i += 2
        elif c == "*":
            out.append(".*" if pattern.startswith("*", i) else "[^/]*")
            i += pattern.startswith("*", i)
        elif c == "?":
            out.append("[^/]")
        elif c == "[" and "]" in pattern[i + 1:]:
            out.append("[^/]")
            i = pattern.index("]", i + 1) + 1
        elif c == "{":
            out.append("(?:")
            depth += 1
        elif c == "}" and depth:
            out.append(")")
            depth -= 1
        elif c == "," and depth:
            out.append("|")
        else:
            out.append(re.escape(c))
    return re.compile("".join(out) + ")" * depth + r"\Z", re.S)


def test_the_matcher_answers_as_the_one_it_replaced():
    rng = random.Random(557)
    matched = 0
    for _ in range(60000):
        pattern = "".join(rng.choice("**??[]{{}},,//ab.") for _ in range(rng.randint(0, 9)))
        path = "".join(rng.choice("ab./\n,{}]") for _ in range(rng.randint(0, 7)))
        old = bool(_old_glob_rx(pattern).match(path))
        assert _glob_rx(pattern).match(path) == old, (pattern, path)
        matched += old
    assert matched > 2000  # the comparison is of matches too, not of misses alone
    for rel in FILES:
        name, ext = os.path.basename(rel), _ext(rel)
        for pattern in (rel, f"**/{name}", f"**/*{ext}", "**/*", "**", f"*/**/{name[0]}?[a-z]*",
                        f"{{x,{rel}}}", f"{_folder(rel)}/{{a,*}}", f"**{name}", "*", f"*{ext}",
                        "**/*.py", "src/**", f"{rel}x", f"x{rel}", ""):
            assert _glob_rx(pattern).match(rel) == bool(_old_glob_rx(pattern).match(rel)), pattern


def test_the_matcher_answers_a_pattern_of_any_length_and_any_stars():
    path = "a/b/" * 20 + "c.md"
    for pattern, matches in (
        ("**" * 60 + "zz", False), ("**" * 60 + "c.md", True), ("**/" * 60 + "*.py", False),
        ("**/" * 60 + "*", True), ("**e" * 60 + "zz", False), ("*" * 60 + "/**", True),
        ("**" * 30000, True), ("*a" * 30000, False), ("[" * 30000, False),
        ("{a," * 20000, False), ("{**," * 20000, True), ("?" * 60000, False),
    ):
        assert _glob_rx(pattern).match(path) == matches, pattern[:8]


def test_the_operands_and_the_valued_options_of_a_command_are_told_apart():
    valued = frozenset({"-e", "-g", "--include"})
    for command, expected in (
        ("x src", (["x", "src"], [])),
        ("-rn x --include=*.py --include '*.md' .",
         (["x", "."], [("--include", "*.py"), ("--include", "*.md")])),
        ("-rne x .", (["."], [("-e", "x")])),
        ("-ex -g'*.py' -g a b", (["b"], [("-e", "x"), ("-g", "*.py"), ("-g", "a")])),
        ("-rn -- --off src/", (["--off", "src/"], [])),
        ("--include= --other=1 --flag - x", (["-", "x"], [("--include", "")])),
        ("-e", ([], [("-e", "")])), ("", ([], [])),
    ):
        assert _options(shlex.split(command), valued) == expected, command


def test_the_paths_and_the_name_filters_of_a_shell_search_are_found():
    for command, expected in (
        ("grep -r x", (["."], [], [])),
        ("grep -rn x src tests", (["src", "tests"], [], [])),
        ("grep --dereference-recursive -e x -e y .", (["."], [], [])),
        ("grep -rn -- --off src/", (["src/"], [], [])),
        ("grep -rn x --include=*.py --include '*.md' --exclude=a .", (["."], ["*.py", "*.md"], [])),
        ("grep -r x *", (["."], [], [])),
        ("grep -rn x ./* src/*", ([".", "src/*"], [], [])),
        ("rg x", (["."], [], [])),
        ("rg --files", (["."], [], [])),
        ("rg -n -e x src", (["src"], [], [])),
        ("rg x -g '*.py' -g'!a' --glob=b --glob c --iglob=D --iglob E src docs",
         (["src", "docs"], ["*.py", "!a", "b", "c"], ["D", "E"])),
        ("find", (["."], [], [])),
        ("find -type f", (["."], [], [])),
        ("find -L src . -type f", (["src", "."], [], [])),
        ("ls -laR", (["."], [], [])),
        ("ls -R src docs", (["src", "docs"], [], [])),
    ):
        name, *args = shlex.split(command)
        assert _shell_search(name, args, False) == expected, command
    for command in ("grep x README.md", "grep -n x", "ls", "ls -la src", "cat a", "git grep x"):
        name, *args = shlex.split(command)
        assert _shell_search(name, args, False) is None, command
    # A find in a command that holds a test on a name is not judged.
    assert _shell_search("find", [".", "-name", "*.py"], True) is None


def test_a_search_that_nothing_narrows_is_refused_from_the_root_and_from_a_copy_s_folder(
        project, site):
    home = os.environ["HOME"]
    for start in (project, site, home):
        for tool_name, tool_input, cwd in (
            ("Grep", {"pattern": "x", "path": str(start)}, None),
            ("Grep", {"pattern": "x", "path": f"{start}/"}, None),
            ("Grep", {"pattern": "x"}, start),
            ("Grep", {"pattern": "x", "path": ".."}, f"{start}/src"),
            ("Grep", {"pattern": "x", "path": f"{start}/src/..", "type": "py"}, None),
            ("Grep", {"pattern": "x", "path": str(start), "glob": "!*.md"}, None),
            ("Bash", {"command": f"grep -r x {start}"}, None),
            ("Bash", {"command": "grep -Rn x"}, start),
            ("Bash", {"command": "grep -inr x ."}, start),
            ("Bash", {"command": f"grep -rn -e x src {start}"}, None),
            ("Bash", {"command": f"cd {start} && grep --recursive x"}, None),
            ("Bash", {"command": "grep -r x *"}, start),
            ("Bash", {"command": "grep -rn x ./*"}, start),
            ("Bash", {"command": f"grep -rn x --exclude='*.md' {start}"}, None),
            ("Bash", {"command": f"rg x {start}"}, None),
            ("Bash", {"command": "rg -l x"}, start),
            ("Bash", {"command": "rg --files"}, start),
            ("Bash", {"command": f"rg x -g '!*.md' src {start}"}, None),
            ("Bash", {"command": f"find {start}"}, None),
            ("Bash", {"command": "find -type f"}, start),
            ("Bash", {"command": f"cd {start} && find . -type f"}, None),
            ("Bash", {"command": f"ls -R {start}"}, None),
            ("Bash", {"command": "ls -laR"}, start),
            ("Bash", {"command": f"echo $(grep -r x {start})"}, None),
        ):
            assert read_refusal(tool_name, tool_input, str(project),
                                str(cwd or project)) == SEARCH_REFUSAL, (tool_name, tool_input)
    for command in ("grep -r x ~", "rg x $HOME", "cd && grep -r x", "find ~ -type f", "ls -R ~/"):
        assert read_refusal("Bash", {"command": command}, str(project),
                            str(project)) == SEARCH_REFUSAL, command


def test_a_search_with_a_path_or_a_glob_that_keeps_both_files_out_is_let_through(project, site):
    home = os.environ["HOME"]
    for start in (project, site, home):
        for tool_input in (
            {"pattern": "x", "path": f"{start}/src"},
            {"pattern": "x", "path": str(start), "glob": "*.py"},
            {"pattern": "x", "path": str(start), "glob": "**/*.py", "type": "py"},
            {"pattern": "x", "path": str(start), "glob": "src/**"},
        ):
            assert not _refused(project, "Grep", tool_input), tool_input
        for command in (
            "grep -rn x src tests", "rg x src", "find src -name '*.py'", "ls -R src",
            "git grep x -- src", "grep x README.md", "ls", "ls -la", "grep -rn -- --off src/",
            "grep -rn x --include='*.py' .", "grep -rn x --include=*.py", "rg x -g '*.py'",
            "rg x -g'*.py' -g '!test_*'", "rg --glob '*.py' x .", "rg x --iglob '*.PY'",
            "git status --short", "git add -A", "git diff --stat", "python3 -m pytest tests -q",
            f"cd {start} && git status --short", f"ls -la {start}", f"grep -rn x {start}/src",
            # No case either way in this round (the residuals): decided as before.
            "find . -name '*.py'", "git grep x", "rg x *", "ls -R *", f"grep -r x {start}/*",
        ):
            assert not _refused(project, "Bash", {"command": command}, start), command


@pytest.mark.parametrize("rel", FILES)
def test_a_shell_search_whose_name_filter_takes_a_file_in_is_refused(project, site, rel):
    name, ext = os.path.basename(rel), _ext(rel)
    for start in (project, site):
        for f in (name, f"*{ext}", name[:4] + "*", "*"):
            for command in (
                f"grep -rn x --include={f} .", f"grep -rn x --include '{f}' .",
                f"grep -rn --include='{f}' x", f"rg x -g '{f}'", f"rg x -g'{f}'",
                f"rg x --glob='{f}'", f"rg --glob '{f}' x .", f"rg x --iglob='{f.upper()}'",
                f"rg x --iglob '{f}'", f"grep -rn x --include='*.py' --include='{f}' {start}",
                f"rg -g '*.py' -g '{f}' x", f"rg x --glob='{f}' --glob='!*.md'",
                f"cd {start} && rg x -g '{f}'", f"rg x -g '{f}' ..",
            ):
                cwd = f"{start}/src" if command.endswith("..") else start
                assert _refused(project, "Bash", {"command": command}, cwd), command
        # The filter names the file; the search cannot reach it.
        for command in (f"grep -rn x --include='{name}' src", f"rg x -g '{name}' {start}/src",
                        f"rg x --iglob '{name.upper()}' src", f"rg x --glob='*{ext}' docs"):
            assert not _refused(project, "Bash", {"command": command}, start), command
    # The same filter in another case of letter is another name.
    assert not _refused(project, "Bash", {"command": f"rg x -g '{name.upper()}'"})


def test_a_command_whose_substitutions_hold_more_than_the_rule_reads_is_refused(project, tmp_path):
    for command in ("echo " + "$(" * 3000, "echo " + "$(echo a " * 1000, "cat " + "<(" * 10000,
                    "echo " + "$(echo " * 1000 + ")" * 1000,
                    "echo `" + "a " * MOST_READ + "`"):
        for root in (project, tmp_path):
            assert read_refusal("Bash", {"command": command}, str(root),
                                str(root)) == LONG_REFUSAL, command[:12]
    for command in ("echo " + "`" * 10000, "echo " + "$(true) " * 1000,
                    'git commit -m "' + "word `tick` $(x) " * 400 + '"',
                    "echo $(echo " + "a" * (MOST_READ - 5) + ")"):
        assert not _refused(project, "Bash", {"command": command}), command[:12]


def test_a_search_of_more_paths_times_filters_than_the_rule_reads_is_refused(project, tmp_path):
    wide = "{a,b}" * 8
    for command in ("rg x -g '" + wide + "' " + "src " * 17,
                    "rg x " + "-g '*.py' " * 2049 + "src tests",
                    "grep -r x --include='" + wide + "' " + "src " * 17):
        for root in (project, tmp_path):
            assert read_refusal("Bash", {"command": command}, str(root),
                                str(root)) == LONG_REFUSAL, command[:12]
    # Nor are the brace expansions of one call, in or out of a substitution.
    for command in ("echo " + (wide + " ") * 17, "echo $(echo " + (wide + " ") * 17 + ")",
                    "echo " + ("$(echo " + wide + ") ") * 17):
        assert read_refusal("Bash", {"command": command}, str(project),
                            str(project)) == LONG_REFUSAL, command[:12]
    for command in ("echo " + (wide + " ") * 15, "mkdir -p " + "src/{a,b,c}/{d,e} " * 40,
                    "rg x -g '" + wide + "' " + "src " * 15,
                    "rg x -g '*.py' -g '*.md' " + "src " * 40,
                    "grep -rn x --include='*.py' " + "src " * 40):
        assert not _refused(project, "Bash", {"command": command}), command[:12]


def test_the_decision_refuses_a_command_longer_than_the_guard_reads(project, tmp_path):
    for root in (project, tmp_path):
        for role in (None, "orchestrator", "engineer"):
            for command in ("echo " + "a " * (MOST_READ // 2), "a" * (MOST_READ + 1),
                            f"cat {SETTINGS_REL} && echo " + "a " * MOST_READ):
                assert decide("Bash", {"command": command}, str(root), role, None,
                              cwd=str(root), flag="absent") == ("deny", LONG_REFUSAL)
    for command in ("echo " + "a" * (MOST_READ - 5),
                    "git commit -m '" + "word " * 800 + "'"):
        assert decide("Bash", {"command": command}, str(project), "orchestrator", None,
                      cwd=str(project), flag="absent") == ("allow", "")
    # Only a command is bounded: a file tool's text is not read word by word.
    assert decide("Write", {"file_path": str(project / "docs" / "a.md"),
                            "content": "a " * MOST_READ}, str(project), "orchestrator", None,
                  cwd=str(project), flag="absent") == ("allow", "")


def test_the_refusals_of_the_round_name_a_decision_and_no_path():
    for reason, decision in ((SEARCH_REFUSAL, "DEC-557"), (NUL_REFUSAL, "DEC-562"),
                             (LONG_REFUSAL, "DEC-562")):
        assert decision in reason
        for rel in FILES:
            assert rel not in reason and os.path.basename(rel) not in reason


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


def test_the_listing_redacts_an_absolute_path_a_deny_rule_carries():
    def commands(deny, *held):
        return [row["command"] for row in listing({
            "permissions": {"deny": deny},
            "hooks": {"Stop": [{"hooks": [{"command": c} for c in held]}]}})]

    for rule in ("Read(//w/held/**)", "Read(//w/held)", "Read(//w/held/)",
                 "Read( //w/held/**)", "Edit(//w/held/**)"):
        assert commands([rule], "cat /w/held x", "ls /w/held/a /w/held", "ls /w /w/other") == [
            f"cat {REDACTED} x", f"ls {REDACTED}/a {REDACTED}", "ls /w /w/other"]
    assert commands(["Read(//w/held/**)", "Read(//w/held-two/**)"],
                    "ls /w/held-two /w/held") == [f"ls {REDACTED} {REDACTED}"]
    for rule in ("Bash(ls:*)", "Read(./w/**)", "Read(**/*.key)", "Read(//)", "Read(//**)",
                 "Read(/w/held/**)", "Read(~)", "Read(~/)", "Read(~/**)", "Read", "(//w)"):
        assert commands([rule], f"ls w /w/held ./w **/*.key / {rule} ~/w") == [
            f"ls w /w/held ./w **/*.key / {REDACTED} ~/w"], rule


def test_the_listing_redacts_a_path_a_deny_rule_spells_from_the_home_folder(monkeypatch):
    def commands(deny, *held):
        return [row["command"] for row in listing({
            "permissions": {"deny": deny},
            "hooks": {"Stop": [{"hooks": [{"command": c} for c in held]}]}})]

    monkeypatch.setenv("HOME", "/h/me")
    for rule in ("Read(~/w/**)", "Read(~/w)", "Read(~/w/)", "Read( ~/w/**)", "Edit(~/w/**)"):
        assert commands([rule], f"ls w /w/held ./w **/*.key / {rule} ~/w") == [
            f"ls w /w/held ./w **/*.key / {REDACTED} {REDACTED}"], rule
        assert commands([rule], "cat ~/w /h/me/w x", "ls ~ /h/me ~/other /h/me/other /w w") == [
            f"cat {REDACTED} {REDACTED} x", "ls ~ /h/me ~/other /h/me/other /w w"], rule
    assert commands(["Read(~/w/**)", "Read(~/w-two/**)"], "ls /h/me/w-two ~/w-two ~/w") == [
        f"ls {REDACTED} {REDACTED} {REDACTED}"]
    assert commands(["Read(~/a)"], "ls ~/a /h/me/a a /a") == [
        f"ls {REDACTED} {REDACTED} a /a"]
    # No home folder, an empty one, the root: the path as written only.
    for home in (None, "", "/", "//"):
        if home is None:
            monkeypatch.delenv("HOME")
        else:
            monkeypatch.setenv("HOME", home)
        assert commands(["Read(~/w/**)", "Read(~/**)"], "ls ~/w /w / /h/me/w ~") == [
            f"ls {REDACTED} /w / /h/me/w ~"], home


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
