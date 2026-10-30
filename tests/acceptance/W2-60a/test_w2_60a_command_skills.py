"""W2-60a, KPI success 2 and failure 1, round 2 -- the project's command files are skills, and the record names each.

KPI success 2 [DEC-826 Q1, DEC-832 item 1, lens E F15]: "The skills the
session can load are in the launch record, each with its name, version and
content hash, taken from the copy the session loads". KPI failure 1: "A launch
that starts with ... an unrecorded skill".

Review 1's finding F1, as a behaviour (DEC-136, DEC-802): the CLI loads every
Markdown file under the tree's ``.claude/commands/`` as a skill,
``.claude/commands/<name>.md`` as ``<name>`` and
``.claude/commands/<namespace>/<name>.md`` as ``<namespace>:<name>`` (this
repository tracks six, ``.claude/commands/opsx/apply.md`` as ``opsx:apply``
...; their front matter's ``name: 'OPSX: Apply'`` is not the skill's name).
The record's ``skills`` holds one entry for each such file, taken from that
file: its name in that form, its path, its version (the front matter's
``version`` as written, else ``no version``), its sha256 and ``named: false``.
The ``.claude/skills/`` entries stay as they are. A command file that is a
link, a folder under ``.claude/commands/`` that is a link, or a command file
whose front matter (when it has one) is not YAML refuses the launch, as the
same faults in ``.claude/skills/`` do (``test_w2_60a_skills.py``). No
``.claude/commands/`` adds nothing. A role's skills line still names only
``.claude/skills/`` skills.

A refusal is held to ``LAUNCH_REFUSED`` and the name of the file or folder it
refuses for; the entry's ``path`` to the command file, relative to the tree or
absolute.
"""

from __future__ import annotations

import os
import shutil

import pytest

import w2_60a_support as s


def _by_name(record):
    skills = record.get("skills")
    assert isinstance(skills, list), f"the record's skills is not a list: {skills!r}"
    found = {}
    for entry in skills:
        assert isinstance(entry, dict) and "name" in entry, f"a skills entry without a name: {entry!r}"
        assert entry["name"] not in found, f"the skill {entry['name']} is recorded twice"
        found[entry["name"]] = entry
    return found


def _path_names(entry, project, command):
    rel = f"{s.COMMANDS_REL}/{command.rel}"
    return str(entry.get("path")) in {rel, os.path.join(os.path.realpath(project), rel)}


def _command_path(project, command):
    return project / s.COMMANDS_REL / command.rel


def test_every_command_file_is_recorded_as_a_skill_from_that_file(project, launch):
    s.add_commands(project)
    s.write_role(project, s.ENGINEER, skills=(s.BACKEND.folder,))
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    found = _by_name(result.record())
    expected = {skill.recorded_name for skill in s.SKILLS} | {command.recorded_name for command in s.COMMANDS}
    assert set(found) == expected, (
        f"the record's skills are not the {s.SKILLS_REL}/ folders and the {s.COMMANDS_REL}/ Markdown files: "
        f"recorded {sorted(found)}, loadable {sorted(expected)}")
    for command in s.COMMANDS:
        entry = found[command.recorded_name]
        assert entry.get("version") == command.recorded_version, (
            f"{command.rel}: version {entry.get('version')!r}, not the file's {command.recorded_version!r}")
        assert entry.get("sha256") == s.sha256_file(_command_path(project, command)), (
            f"{command.rel}: sha256 is not the command file's")
        assert entry.get("named") is False, f"{command.rel} is recorded as named: {entry!r}"
        assert _path_names(entry, project, command), (
            f"{command.rel}: the recorded path {entry.get('path')!r} is not the command file's")
    assert found[s.BACKEND.recorded_name].get("named") is True, "the skill the role names is not recorded as named"
    assert not [name for name in found if "notes" in name], (
        f"a file of {s.COMMANDS_REL}/ that is not Markdown is recorded as a skill: {sorted(found)}")
    assert not [name for name in found if "W260A" in name], (
        f"a command is recorded under its front matter's name, not as the CLI loads it: {sorted(found)}")


def test_a_command_entry_follows_the_file_as_it_stands_at_the_launch(project, launch):
    s.add_commands(project)
    first = launch(s.ENGINEER)
    s.assert_launched(first)
    changed = s.Command(s.TOP_COMMAND.rel, "1.3.0", title=s.TOP_COMMAND.title)
    s.write(_command_path(project, changed), changed.text())
    second = launch(s.ENGINEER)
    s.assert_launched(second)
    before = _by_name(first.record()).get(s.TOP_COMMAND.recorded_name)
    after = _by_name(second.record()).get(s.TOP_COMMAND.recorded_name)
    assert before is not None and after is not None, (
        f"the command {s.TOP_COMMAND.recorded_name} is not recorded: {before!r}, {after!r}")
    assert (after.get("version"), after.get("sha256")) == ("1.3.0", s.sha256_file(_command_path(project, changed))), (
        f"the entry is not the command file's as it stood at the second launch: {after!r}")
    assert after.get("sha256") != before.get("sha256"), "a changed command file left its sha256 as it was"


def test_the_skills_folder_s_entries_stay_as_they_are(project, launch):
    without = launch(s.ENGINEER)
    s.assert_launched(without)
    s.add_commands(project)
    beside = launch(s.ENGINEER)
    s.assert_launched(beside)
    before, after = _by_name(without.record()), _by_name(beside.record())
    for skill in s.SKILLS:
        assert after.get(skill.recorded_name) == before.get(skill.recorded_name), (
            f"{skill.folder}'s entry changed when command files were added: {before.get(skill.recorded_name)!r} "
            f"became {after.get(skill.recorded_name)!r}")
    added = sorted(set(after) - set(before))
    assert added == sorted(command.recorded_name for command in s.COMMANDS), (
        f"the entries added beside the {s.SKILLS_REL}/ entries are not the command files: {added}")


def test_command_files_with_no_skills_folder_are_recorded(project, launch):
    shutil.rmtree(project / s.SKILLS_REL)
    s.add_commands(project)
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    assert set(_by_name(result.record())) == {command.recorded_name for command in s.COMMANDS}, (
        f"no {s.SKILLS_REL}/: the record's skills are not the command files: {result.record().get('skills')!r}")


@pytest.mark.parametrize("folder", ("missing", "empty"))
def test_no_command_file_adds_nothing(project, launch, folder):
    if folder == "empty":
        (project / s.COMMANDS_REL).mkdir(parents=True)
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    assert set(_by_name(result.record())) == {skill.recorded_name for skill in s.SKILLS}, (
        f"{s.COMMANDS_REL}/ {folder}: the record's skills are not the {s.SKILLS_REL}/ folders alone")


# --------------------------------------------------------------------------
# Refusals: a command file the record could not describe
# --------------------------------------------------------------------------

def _file_is_a_link(project, sandbox):
    target = s.write(sandbox.elsewhere / "linked-command.md", s.Command("w260a-linked.md", "1.0.0").text())
    os.symlink(target, project / s.COMMANDS_REL / "w260a-linked.md")
    return "w260a-linked"


def _file_in_a_namespace_is_a_link(project, sandbox):
    target = s.write(sandbox.elsewhere / "linked-in-ns.md", s.Command("w260a-ns/x.md", "1.0.0").text())
    os.symlink(target, project / s.COMMANDS_REL / "w260a-ns" / "w260a-linked-in-ns.md")
    return "w260a-linked-in-ns"


def _namespace_is_a_link(project, sandbox):
    target = sandbox.elsewhere / "linked-namespace"
    s.write(target / "inside.md", s.Command("w260a-linked-ns/inside.md", "1.0.0").text())
    os.symlink(target, project / s.COMMANDS_REL / "w260a-linked-ns")
    return "w260a-linked-ns"


def _front_matter_not_yaml(project, sandbox):
    s.write(project / s.COMMANDS_REL / "w260a-ns" / "w260a-broken.md",
            "---\ndescription: : :\nversion: [1.0.0\n---\n\nbroken\n")
    return "w260a-broken"


UNDESCRIBABLE = {
    "command-file-is-a-link": _file_is_a_link,
    "command-file-in-a-namespace-is-a-link": _file_in_a_namespace_is_a_link,
    "namespace-folder-is-a-link": _namespace_is_a_link,
    "front-matter-not-yaml": _front_matter_not_yaml,
}


@pytest.mark.parametrize("case", sorted(UNDESCRIBABLE))
def test_a_command_file_the_record_could_not_describe_refuses_the_launch(sandbox, project, launch, case):
    """The record could not say what the session may load. The role names no skill; the other commands launch."""
    s.add_commands(project)
    s.assert_launched(launch(s.ENGINEER))
    word = UNDESCRIBABLE[case](project, sandbox)
    s.assert_refused(launch(s.ENGINEER), "LAUNCH_REFUSED", word)


@pytest.mark.parametrize("named, words", (
    (s.TOP_COMMAND.recorded_name, (s.TOP_COMMAND.recorded_name,)),
    (s.UNVERSIONED_COMMAND.recorded_name, ()),
), ids=("top-level", "namespaced"))
def test_a_role_s_skills_line_names_only_skills_folder_skills(project, launch, named, words):
    """A command's name in the skills line is a named skill with no ``.claude/skills/<name>/SKILL.md`` (or, with
    its ``:``, a line that is not a skills line): refused either way."""
    s.add_commands(project)
    s.assert_launched(launch(s.ENGINEER))
    s.write_role(project, s.ENGINEER, skills=(named,))
    s.assert_refused(launch(s.ENGINEER), "LAUNCH_REFUSED", "skill", *words)
