"""What a close reads of the repository before it measures (DEC-487, DEC-490): the commits with the paths they
bring, the working tree against its commit, the commit the record store was built from."""
from __future__ import annotations

import pytest

from gov.cli.errors import GovError
from gov.close import repo as close_repo
from gov.close.repo import (commits_since, names_no_task, read_commits, store_is_of_head, ticket_commits,
                            tickets_of_head, tree_differences)
from gov.store import STORE_REL, load

from .conftest import Repo

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
    assert [names_no_task(c, frozenset({TICKET, "T-0002"})) for c in others] == [True, False, True]
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


# ---- the git asked is not the caller's to bend (DEC-500) ----

PLANTED = "conftest.py"


def _states(root):
    return {path: state for state, path in tree_differences(root)}


def test_a_file_the_commits_own_rules_ignore_differs_in_nothing(project):
    project.commit("rules", files={".gitignore": ".gov-runtime/\nbuild/\n*.log\n", "src/.gitignore": "local.py\n"})
    for rel in ("build/out/a.bin", "run.log", "src/deep/run.log", "src/local.py", ".gov-runtime/x.json"):
        (project.root / rel).parent.mkdir(parents=True, exist_ok=True)
        (project.root / rel).write_text("x\n", encoding="utf-8")
    # an ignore file inside an ignored folder is not read: the folder is the commit's to ignore
    (project.root / "build" / ".gitignore").write_text("*\n", encoding="utf-8")
    assert tree_differences(project.root) == []


def test_a_file_ignored_only_by_the_private_exclude_file_is_named_with_that_file(project):
    (project.root / PLANTED).write_text("x\n", encoding="utf-8")
    (project.root / ".git" / "info").mkdir(exist_ok=True)
    (project.root / ".git" / "info" / "exclude").write_text(f"{PLANTED}\n", encoding="utf-8")
    assert project.git("status", "--porcelain").strip() == ""
    [(state, path)] = tree_differences(project.root)
    assert path == PLANTED and "outside the commit" in state and ".git/info/exclude" in state


def test_a_file_ignored_only_by_an_excludes_file_of_the_configuration_is_named(project, tmp_path):
    excludes = tmp_path / "excludes"
    excludes.write_text(f"{PLANTED}\n", encoding="utf-8")
    (project.root / PLANTED).write_text("x\n", encoding="utf-8")
    project.git("config", "core.excludesFile", str(excludes))
    assert project.git("status", "--porcelain").strip() == ""
    [(state, path)] = tree_differences(project.root)
    assert path == PLANTED and str(excludes) in state


def test_a_file_ignored_only_by_an_untracked_ignore_file_is_named_and_so_is_that_file(project):
    (project.root / "src").mkdir()
    (project.root / "src" / PLANTED).write_text("x\n", encoding="utf-8")
    (project.root / "src" / ".gitignore").write_text(f"{PLANTED}\n.gitignore\n", encoding="utf-8")
    assert project.git("status", "--porcelain").strip() == ""
    states = _states(project.root)
    assert sorted(states) == ["src/.gitignore", f"src/{PLANTED}"]
    assert all("src/.gitignore" in state for state in states.values())


def test_a_file_a_rule_outside_the_commit_takes_out_of_the_commits_rules_is_untracked(project):
    project.commit("rules", files={".gitignore": ".gov-runtime/\n*.log\n"})
    (project.root / "run.log").write_text("x\n", encoding="utf-8")
    (project.root / ".git" / "info").mkdir(exist_ok=True)
    (project.root / ".git" / "info" / "exclude").write_text("!run.log\n*.log\n", encoding="utf-8")
    assert tree_differences(project.root) == []  # the commit's rule decides before the private file's
    (project.root / "new.txt").write_text("x\n", encoding="utf-8")
    (project.root / ".git" / "info" / "exclude").write_text("*.txt\n!new.txt\n", encoding="utf-8")
    assert tree_differences(project.root) == [("??", "new.txt")]


def test_an_excludes_file_named_in_the_callers_environment_is_not_read(project, tmp_path, monkeypatch):
    excludes = tmp_path / "excludes"
    excludes.write_text(f"{PLANTED}\n", encoding="utf-8")
    (project.root / PLANTED).write_text("x\n", encoding="utf-8")
    for name, value in {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.excludesFile",
                        "GIT_CONFIG_VALUE_0": str(excludes)}.items():
        monkeypatch.setenv(name, value)
    assert tree_differences(project.root) == [("??", PLANTED)]


def test_no_variable_of_the_callers_environment_that_speaks_to_git_reaches_git(repo, tmp_path, monkeypatch):
    head = repo.commit("work", *TRAILERS)
    another = Repo(tmp_path / "another")
    another.commit("another repository")
    monkeypatch.setenv("GIT_DIR", str(another.root / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(another.root))
    monkeypatch.setenv("GIT_CONFIG_PARAMETERS", "'core.bare=true'")
    assert close_repo.git(repo.root, "rev-parse", "HEAD").strip() == head
    assert [c["sha"] for c in ticket_commits(repo.root, TICKET)] == [head]


def test_an_answer_of_another_shape_about_the_untracked_files_is_an_error(project, monkeypatch):
    (project.root / PLANTED).write_text("x\n", encoding="utf-8")
    real = close_repo.git

    def answered(root, *args, **keys):
        return "one\0field\0" if args[0] == "check-ignore" else real(root, *args, **keys)

    monkeypatch.setattr(close_repo, "git", answered)
    with pytest.raises(GovError) as raised:
        tree_differences(project.root)
    assert raised.value.code == "GIT_FAILURE"


def test_a_replacement_ref_is_not_followed(repo, tmp_path):
    commit = repo.commit("work", f"Task: {TICKET}", "Role: engineer", files={"src/a.py": "a\n"})
    body = repo.git("cat-file", "commit", commit)
    (tmp_path / "replacement").write_text(body + "Implements: CAP-01\n", encoding="utf-8")
    replacement = repo.git("hash-object", "-t", "commit", "-w", str(tmp_path / "replacement")).strip()
    repo.git("replace", commit, replacement)
    assert "Implements: CAP-01" in repo.git("log", "-1", "--format=%(trailers)", commit)
    [read] = ticket_commits(repo.root, TICKET)
    assert read["sha"] == commit and "Implements" not in read["trailers"]


# ---- a Task: that names no ticket of the project (DEC-500) ----

def test_the_projects_tickets_are_the_ticket_files_of_the_commit(project):
    project.commit("more", files={".tickets/T-0002.md": "---\nid: T-0002\n---\n", ".tickets/notes.txt": "n\n",
                                  ".tickets/sub/T-0009.md": "---\nid: T-0009\n---\n", "docs/T-0003.md": "x\n"})
    (project.root / ".tickets" / "T-0004.md").write_text("---\nid: T-0004\n---\n", encoding="utf-8")  # no commit's
    assert tickets_of_head(project.root) == frozenset({TICKET, "T-0002"})


@pytest.mark.parametrize("named, no_task", [([], True), (["T-0003"], True), (["DEC-000"], True), (["T-000"], True),
                                            ([TICKET], False), (["T-0003", "T-0002"], False)])
def test_a_task_that_names_none_of_the_projects_tickets_names_no_task(named, no_task):
    commit = {"sha": "a" * 40, "trailers": {"Task": named, "Role": ["engineer"]} if named else {"Role": ["engineer"]}}
    assert names_no_task(commit, frozenset({TICKET, "T-0002"})) is no_task


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
