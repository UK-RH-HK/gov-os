"""W2-60a, KPI success 1 -- the session starts as its role: the role file's text is appended at its start.

KPI success 1 [DEC-826 Q1, lens E F2]: "gov launch <role> <ticket> starts the
session as its role: the role's text (its generated agent, or the role file's
text appended) is in the session's context at its start, shown by a launched
session's log; the launch record holds the role file's path, version and
content hash". KPI failure 1: "A launch that starts with no role text".

The route the design takes is the role file's text appended: the launcher
writes the bytes of ``template/governance/kernel/roles/<role>.md`` of the tree
into ``role-<role>.md`` in the session's own temp folder and names it with
``--append-system-prompt-file``. The generated agent ``.claude/agents/<role>.md``
is not the session's text and is left as it is. A missing or unreadable role
file, or one without its version line, refuses the launch (Behaviour 10). An
``agent`` key in the repository's settings would change the session's prompt,
and refuses the launch.

What the stand-in shows is the line and the file's bytes at the moment the
session started; that the text is then in the session's context is the live
file's (``test_w2_60a_live_sessions.py``).
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

import w2_60a_support as s


@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_the_role_file_s_text_is_appended_at_the_session_s_start(sandbox, project, launch, role):
    agent_before = (project / s.AGENTS_REL / f"{role}.md").read_bytes()
    result = launch(role)
    s.assert_launched(result)
    appended = result.appended()
    role_bytes = s.role_path(project, role).read_text(encoding="utf-8")
    assert appended["text"].startswith(role_bytes), (
        f"the file handed with --append-system-prompt-file does not begin with the role file's text, as the launcher "
        f"read it (Behaviour 1)\nhanded: {appended['text'][:600]!r}")
    assert s.AGENT_WORD not in appended["text"], "the appended text is the generated agent's, not the role file's"
    assert Path(appended["path"]).name == f"role-{role}.md", (
        f"the appended file is {appended['path']}, not role-{role}.md (Behaviour 1)")
    tmpdir = result.env_block().get("TMPDIR")
    assert tmpdir and os.path.dirname(appended["path"]) == tmpdir, (
        f"role-{role}.md is not in the session's own temp folder {tmpdir!r}: {appended['path']} (DEC-386)")
    assert s.occurrences(result.args, "--agent") == 0, f"the line starts the session as an agent: {result.args}"
    for replacing in ("--system-prompt", "--system-prompt-file"):
        assert s.occurrences(result.args, replacing) == 0, (
            f"the line replaces the CLI's default system prompt with {replacing}: {result.args}")
    assert (project / s.AGENTS_REL / f"{role}.md").read_bytes() == agent_before, (
        "the generated agent was changed by the launch")


@pytest.mark.parametrize("role", (s.ENGINEER, s.AUDITOR))
def test_the_record_holds_the_role_file_s_path_version_and_hash(project, launch, role):
    result = launch(role)
    s.assert_launched(result)
    record = result.record()
    expected = {"path": f"{s.ROLES_REL}/{role}.md", "version": s.VERSIONS[role],
                "sha256": s.sha256_file(s.role_path(project, role))}
    assert record.get("role_text") == expected, (
        f"the record's role_text is not the role file's path, version and hash\nrecord: {record.get('role_text')}\n"
        f"expected: {expected}")
    assert record.get("appended_sha256") == result.appended()["sha256"], (
        "the record's appended_sha256 is not the sha256 of the file the session was handed")


def test_the_role_text_is_the_file_as_it_stands_at_each_launch(project, launch):
    """The copy the session loads is the role file as the launcher read it at launch (Behaviour 1), not a copy kept
    from an earlier launch or generated from it."""
    first = launch(s.ENGINEER)
    s.assert_launched(first)
    s.write_role(project, s.ENGINEER, version=s.version_line("1.4.3"), word="zq60a-role-text-changed")
    second = launch(s.ENGINEER)
    s.assert_launched(second)
    assert "zq60a-role-text-changed" in second.appended()["text"], "the second launch was handed the old role text"
    assert second.record().get("role_text", {}).get("version") == "1.4.3", (
        f"the second record does not hold the changed file's version: {second.record().get('role_text')}")
    assert second.record()["role_text"].get("sha256") == s.sha256_file(s.role_path(project, s.ENGINEER))


def test_the_appended_copy_goes_with_the_session_s_temp_folder(launch):
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    path = result.appended()["path"]
    assert not os.path.lexists(path), f"role-engineer.md is still there after the session ended: {path} (DEC-386)"


# --------------------------------------------------------------------------
# No session without its role text
# --------------------------------------------------------------------------

def _no_file(project):
    s.role_path(project, s.ENGINEER).unlink()


def _a_folder(project):
    path = s.role_path(project, s.ENGINEER)
    path.unlink()
    path.mkdir()


def _no_version(project):
    s.write_role(project, s.ENGINEER, version="")


def _short_version(project):
    s.write_role(project, s.ENGINEER, version="- **Version:** 1.4")


UNREADABLE = {
    "no-role-file": _no_file,
    "role-file-is-a-folder": _a_folder,
    "no-version-line": _no_version,
    "version-not-major-minor-patch": _short_version,
}


@pytest.mark.parametrize("case", sorted(UNREADABLE))
def test_a_launch_without_its_role_text_or_version_is_refused(project, launch, case):
    """Behaviour 10: "A missing or unreadable role file, version line ... refuses the launch"; no fallback stands in."""
    UNREADABLE[case](project)
    s.assert_refused(launch(s.ENGINEER), "engineer.md")


@pytest.mark.parametrize("rel", (s.SETTINGS_REL, s.LOCAL_SETTINGS_REL), ids=("committed", "local"))
def test_an_agent_key_in_the_repository_s_settings_is_refused(project, launch, rel):
    """Behaviour 10, step 4: an ``agent`` key would start the session as another prompt than its role's."""
    s.rewrite_settings(project, lambda data: data.update({"agent": s.ENGINEER}), rel)
    s.assert_refused(launch(s.ENGINEER), "agent")
