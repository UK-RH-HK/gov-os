"""Builder tests for the launch record (W2-60a).

Regression evidence only (DEC-136). They cover what the acceptance tests leave
to the builder: the folder found from a worktree's ``.git`` file, the exclusive
write, the resumed session's record and the CLI's version read from its link;
and (round 3) the main checkout's local settings judged for a worktree's launch.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.launch import launcher, record  # noqa: E402

SID = "1ecc24ab-3710-4228-8258-619022e4b679"


def test_a_worktree_finds_the_main_checkout_s_folder(tmp_path):
    main, tree = tmp_path / "main", tmp_path / "tree"
    (main / ".git" / "worktrees" / "tree").mkdir(parents=True)
    (main / ".git" / "worktrees" / "tree" / "commondir").write_text("../..\n", encoding="utf-8")
    tree.mkdir()
    (tree / ".git").write_text(f"gitdir: {main}/.git/worktrees/tree\n", encoding="utf-8")
    assert record.folder(tree) == main / ".gov-runtime" / "launches"
    assert (main / ".gov-runtime" / "launches").is_dir() and not (tree / ".gov-runtime").exists()


def test_a_bare_common_directory_refuses(tmp_path):
    (tmp_path / "repo.git").mkdir()
    (tmp_path / "tree").mkdir()
    (tmp_path / "tree" / ".git").write_text(f"gitdir: {tmp_path}/repo.git\n", encoding="utf-8")
    with pytest.raises(GovError):
        record.folder(tmp_path / "tree")


def test_a_record_is_written_once_and_never_over_another(tmp_path):
    path = record.write(tmp_path, {"session_id": SID, "role": "engineer"})
    assert json.loads(path.read_text(encoding="utf-8")) == {"session_id": SID, "role": "engineer"}
    with pytest.raises(GovError):
        record.write(tmp_path, {"session_id": SID, "role": "research"})
    assert json.loads(path.read_text(encoding="utf-8"))["role"] == "engineer"


@pytest.mark.parametrize("data, refused", (
    (None, True),
    ("not json", True),
    ({"record": "gov-launch", "role": "engineer", "ticket": "T-1", "role_text": {}, "skills": []}, False),
    ({"record": "gov-launch", "role": "engineer", "ticket": "T-2", "role_text": {}, "skills": []}, True),
    ({"record": "gov-launch", "role": "engineer", "ticket": "T-1"}, True),
))
def test_a_resume_needs_the_original_s_record_of_this_role_and_ticket(tmp_path, data, refused):
    if data is not None:
        (tmp_path / f"{SID}.json").write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")
    if refused:
        with pytest.raises(GovError):
            record.original(tmp_path, SID, "engineer", "T-1")
    else:
        assert record.original(tmp_path, SID, "engineer", "T-1")["ticket"] == "T-1"


def test_the_cli_s_version_is_the_name_its_link_resolves_to(tmp_path):
    (tmp_path / "versions").mkdir()
    (tmp_path / "versions" / "2.1.292").write_text("", encoding="utf-8")
    (tmp_path / "claude").symlink_to(tmp_path / "versions" / "2.1.292")
    (tmp_path / "plain").write_text("", encoding="utf-8")
    assert record.cli_version(tmp_path / "claude") == "2.1.292"
    assert record.cli_version(tmp_path / "plain").startswith("not measured: ")


# Round 3 (review 2, F1; DEC-951 item 4): a worktree's launch also checks the main checkout's local settings file,
# which the CLI loads for a worktree session; the main checkout found as the record's folder is.
WIRED = {"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [{"type": "command",
                                                               "command": "python3 .claude/hooks/pretooluse.py"}]}]}}


def _worktree(tmp_path, main_local=None):
    """A main checkout and one linked worktree whose own settings wire the guard; ``main_local`` the main's local file."""
    main, tree = tmp_path / "main", tmp_path / "tree"
    (main / ".git" / "worktrees" / "tree").mkdir(parents=True)
    (main / ".git" / "worktrees" / "tree" / "commondir").write_text("../..\n", encoding="utf-8")
    (tree / ".claude").mkdir(parents=True)
    (tree / ".git").write_text(f"gitdir: {main}/.git/worktrees/tree\n", encoding="utf-8")
    (tree / ".claude" / "settings.json").write_text(json.dumps(WIRED), encoding="utf-8")
    (main / ".claude").mkdir()
    if main_local is not None:
        local = main / ".claude" / "settings.local.json"
        local.write_text(main_local if isinstance(main_local, str) else json.dumps(main_local), encoding="utf-8")
    return main, tree


@pytest.mark.parametrize("data", (
    {"sandbox": {"enabled": False}},
    {"disableAllHooks": True},
    {"permissions": {"defaultMode": "bypassPermissions"}},
    {"permissions": {"additionalDirectories": ["/elsewhere"]}},
    {"permissions": []},
    {"agent": "engineer"},
    {"autoCompactWindow": 1},
    {"env": {"CLAUDE_CODE_AUTO_COMPACT_WINDOW": "1"}},
    {"env": {"CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50"}},
    {"env": []},
    {"modelSettings": {"claude-opus-5-5": {"autoCompactWindow": 1}}},
    [],
    "{",
))
def test_the_main_checkout_s_local_file_is_judged_for_a_worktree(tmp_path, data):
    main, tree = _worktree(tmp_path, data)
    with pytest.raises(GovError) as refused:
        launcher._check_repository_settings(tree)
    assert f"{main}/.claude/settings.local.json" in refused.value.message


def test_a_worktree_launches_when_the_main_checkout_has_no_local_file_or_a_clean_one(tmp_path):
    main, tree = _worktree(tmp_path)
    launcher._check_repository_settings(tree)
    (main / ".claude" / "settings.local.json").write_text('{"permissions": {"allow": ["Bash(ls:*)"]}}',
                                                         encoding="utf-8")
    launcher._check_repository_settings(tree)


def test_the_worktree_s_own_local_file_is_still_judged(tmp_path):
    _, tree = _worktree(tmp_path)
    (tree / ".claude" / "settings.local.json").write_text('{"agent": "x"}', encoding="utf-8")
    with pytest.raises(GovError, match=r"^\.claude/settings\.local\.json carries an agent key"):
        launcher._check_repository_settings(tree)


def test_the_main_checkout_s_file_is_read_through_a_link_as_the_tree_s_own_is(tmp_path):
    main, tree = _worktree(tmp_path)
    (tmp_path / "elsewhere.json").write_text('{"disableAllHooks": true}', encoding="utf-8")
    (main / ".claude" / "settings.local.json").symlink_to(tmp_path / "elsewhere.json")
    with pytest.raises(GovError, match="disableAllHooks"):
        launcher._check_repository_settings(tree)
    (tmp_path / "elsewhere.json").unlink()  # a link to nothing cannot be read: refused
    with pytest.raises(GovError, match="cannot be read"):
        launcher._check_repository_settings(tree)


def test_a_worktree_whose_main_checkout_cannot_be_found_refuses(tmp_path):
    main, tree = _worktree(tmp_path)
    (tree / ".git").write_text(f"gitdir: {tmp_path}/nowhere\n", encoding="utf-8")
    with pytest.raises(GovError, match="local settings file the CLI loads"):
        launcher._check_repository_settings(tree)
    (tmp_path / "repo.git").mkdir()
    (tree / ".git").write_text(f"gitdir: {tmp_path}/repo.git\n", encoding="utf-8")
    with pytest.raises(GovError, match="bare repository"):
        launcher._check_repository_settings(tree)


def test_the_main_checkout_s_own_launch_is_unchanged(tmp_path):
    main, _ = _worktree(tmp_path)
    (main / ".claude" / "settings.json").write_text(json.dumps(WIRED), encoding="utf-8")
    launcher._check_repository_settings(main)
    (main / ".claude" / "settings.local.json").write_text('{"agent": "x"}', encoding="utf-8")
    with pytest.raises(GovError, match=r"^\.claude/settings\.local\.json carries an agent key"):
        launcher._check_repository_settings(main)


def test_the_deny_list_is_the_same_before_and_after_the_record_folder_exists(tmp_path):
    """W2-56 S3 with W2-60a S8: the first launch makes ``.gov-runtime/launches``; the next launch's deny list holds the
    same rules in the same order, each once, the folder named by its two literal rules."""
    root = tmp_path.resolve()
    records = root / ".gov-runtime" / "launches"
    before = launcher.build_settings(root, "engineer", "T-1")["permissions"]["deny"]
    assert record.folder(root) == records
    after = launcher.build_settings(root, "engineer", "T-1")["permissions"]["deny"]
    merged = [launcher._worker_deny(deny, records, ["Edit(/elsewhere)"]) for deny in (before, after)]
    assert merged[0] == merged[1]
    assert len(merged[0]) == len(set(merged[0]))
    assert all(merged[0].count(rule) == 1 for rule in record.deny_rules(records))


def test_the_record_s_folder_keeps_its_messages(tmp_path):
    (tmp_path / "tree").mkdir()
    (tmp_path / "tree" / ".git").write_text(f"gitdir: {tmp_path}/nowhere\n", encoding="utf-8")
    with pytest.raises(GovError, match="so the launch record's folder cannot be found"):
        record.folder(tmp_path / "tree")
