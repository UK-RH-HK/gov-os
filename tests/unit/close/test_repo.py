"""What a close reads of the repository before it measures (DEC-487, DEC-490): the commits with the paths they
bring, the working tree against its commit, the commit the record store was built from."""
from __future__ import annotations

import pytest

from gov.cli.errors import GovError
from gov.close import repo as close_repo
from gov.close.repo import (commits_since, names_no_task, read_commits, store_is_of_head, ticket_commits,
                            tree_differences)
from gov.store import STORE_REL, load

TICKET = "T-0001"
TRAILERS = (f"Task: {TICKET}", "Role: engineer", "Implements: CAP-01")


# ---- the commits and the paths they bring ----

def test_a_first_commit_has_every_path_it_holds(repo):
    first = repo.commit("the project", *TRAILERS, files={"src/a.py": "a\n", "governance/project/n.yaml": "n: 1\n"})
    [commit] = read_commits(repo.root, "HEAD")
    assert (commit["sha"], commit["parents"]) == (first, [])
    assert commit["paths"] == ["governance/project/n.yaml", "src/a.py"]


def test_a_merge_commit_has_the_paths_it_brings_to_its_first_parent(repo):
    base = repo.commit("base", files={"README.md": "r\n"})
    repo.git("checkout", "-q", "-b", "side")
    side = repo.commit("on the side", files={"src/side.py": "s\n"})
    repo.git("checkout", "-q", "main")
    main = repo.commit("on main", files={"src/main.py": "m\n"})
    repo.git("merge", "-q", "--no-ff", "--no-gpg-sign", "-m", "merge\n\n" + "\n".join(TRAILERS) + "\n", "side")
    merge, *_ = read_commits(repo.root, "HEAD")
    assert merge["parents"] == [main, side] and merge["paths"] == ["src/side.py"]
    assert merge["trailers"]["Task"] == [TICKET]
    assert {c["sha"] for c in read_commits(repo.root, f"{base}..HEAD")} == {merge["sha"], main, side}


def test_a_path_is_read_as_it_is_named_whatever_bytes_it_holds(repo):
    names = ["src/a b.py", 'src/"quoted".py', "src/ü.py", "src/tab\there.py"]
    repo.commit("names", files={name: "x\n" for name in names})
    assert read_commits(repo.root, "HEAD")[0]["paths"] == sorted(names)


def test_the_trailers_are_read_from_the_final_block_as_written(repo):
    repo.commit("work\n\nTask: in the text, not a trailer\n\nmore text", *TRAILERS, "Role: second")
    [commit] = read_commits(repo.root, "HEAD")
    assert commit["trailers"] == {"Task": [TICKET], "Role": ["engineer", "second"], "Implements": ["CAP-01"]}


def test_output_of_another_shape_is_an_error_and_never_fewer_commits(repo, monkeypatch):
    repo.commit("work")
    for out in ("\x1eabc\x1f\x1f", "\x1e\x1f\x1f\x1f", "\x1eabc\x1f\x1fRole: a\x1fb\x1f\x1f"):
        monkeypatch.setattr(close_repo, "git", lambda *a, out=out, **k: out)
        with pytest.raises(GovError) as raised:
            read_commits(repo.root, "HEAD")
        assert raised.value.code == "GIT_FAILURE"


def test_the_tickets_commits_are_matched_by_the_whole_id(repo):
    repo.commit("another", "Task: T.0001", "Role: engineer")
    mine = repo.commit("mine", *TRAILERS)
    assert [c["sha"] for c in ticket_commits(repo.root, TICKET)] == [mine]
    assert ticket_commits(repo.root, "T.0001")[0]["sha"] != mine


def test_the_commits_of_others_since_the_tickets_first(repo):
    repo.commit("before the ticket")
    first = repo.commit("first", *TRAILERS)
    bare = repo.commit("no trailer")
    theirs = repo.commit("another ticket", "Task: T-0002", "Role: engineer")
    repo.commit("second", *TRAILERS)
    roled = repo.commit("a role and no task", "Role: orchestrator")
    commits = ticket_commits(repo.root, TICKET)
    assert commits[-1]["sha"] == first
    others = commits_since(repo.root, commits)
    assert [c["sha"] for c in others] == [roled, theirs, bare]
    assert [names_no_task(c) for c in others] == [True, False, True]
    assert commits_since(repo.root, []) == []


def test_a_git_failure_is_an_error_not_an_empty_list(tmp_path):
    for read in (lambda: read_commits(tmp_path, "HEAD"), lambda: tree_differences(tmp_path),
                 lambda: store_is_of_head(tmp_path)):
        with pytest.raises(GovError) as raised:
            read()
        assert raised.value.code == "GIT_FAILURE"


# ---- the working tree against its commit ----

def _paths(root):
    return sorted(path for _, path in tree_differences(root))


def test_a_committed_tree_differs_in_nothing(project):
    assert tree_differences(project.root) == []


def test_every_way_a_tree_is_not_its_commit_is_named(project):
    root = project.root
    project.commit("files", files={"src/a.py": "a\n", "src/b.py": "b\n", "src/c.py": "c\n", "src/d.py": "d\n"})
    (root / "src" / "a.py").write_text("changed\n", encoding="utf-8")           # changed, not staged
    (root / "src" / "b.py").unlink()                                              # deleted
    (root / "src" / "c.py").write_text("staged\n", encoding="utf-8")            # staged
    project.git("add", "src/c.py")
    project.git("mv", "src/d.py", "src/e.py")                                    # renamed in the index
    (root / "new dir").mkdir()
    (root / "new dir" / "untracked file.txt").write_text("x\n", encoding="utf-8")
    (root / ".gov-runtime").mkdir()
    (root / ".gov-runtime" / "ignored.json").write_text("{}", encoding="utf-8")  # ignored: differs from no commit
    assert _paths(root) == ["new dir/untracked file.txt", "src/a.py", "src/b.py", "src/c.py", "src/d.py", "src/e.py"]
    assert ("??", "new dir/untracked file.txt") in tree_differences(root)


@pytest.mark.parametrize("flag", ["--assume-unchanged", "--skip-worktree"])
def test_a_file_git_was_told_not_to_compare_is_named(project, flag):
    """git status reports nothing for such a file, whatever the working tree holds."""
    project.commit("a file", files={"src/a.py": "a\n"})
    project.git("update-index", flag, "src/a.py")
    (project.root / "src" / "a.py").write_text("changed\n", encoding="utf-8")
    assert _paths(project.root) == ["src/a.py"]


# ---- the record store against the commit being closed ----

def test_no_store_is_not_an_answer(project):
    assert store_is_of_head(project.root) is None


def test_a_store_is_of_the_head_it_was_loaded_from_and_of_no_later_one(project):
    load(project.root)
    assert store_is_of_head(project.root) is True
    project.commit("one more commit", "Role: owner", files={"docs/adr/DEC-001.md": "---\nid: DEC-001\n---\n"})
    assert store_is_of_head(project.root) is False
    load(project.root)
    assert store_is_of_head(project.root) is True


def test_a_store_loaded_from_a_later_head_is_not_of_this_one(project):
    before = project.git("rev-parse", "HEAD").strip()
    project.commit("later")
    load(project.root)
    project.git("checkout", "-q", "--detach", before)
    assert store_is_of_head(project.root) is False


def test_a_store_of_another_branch_with_as_many_commits_is_not_of_this_one(project):
    base = project.git("rev-parse", "HEAD").strip()
    project.commit("on main")
    load(project.root)
    project.git("checkout", "-q", "-b", "side", base)
    project.commit("on the side")
    assert store_is_of_head(project.root) is False


@pytest.mark.parametrize("content", [b"not a database", b""])
def test_a_store_that_cannot_be_asked_is_an_error_and_names_the_rebuild(project, content):
    store = project.root / STORE_REL
    store.parent.mkdir(parents=True)
    store.write_bytes(content)
    with pytest.raises(GovError) as raised:
        store_is_of_head(project.root)
    assert raised.value.code == "STORE_UNREADABLE" and raised.value.exit_code == 1
    assert "gov rebuild" in raised.value.message
