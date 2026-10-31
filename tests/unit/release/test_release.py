"""Unit tests for gov.release (DEC-135: regression evidence). Every repository is built from scratch in tmp_path."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import threading

import pytest
import yaml

from gov.lock import ANSWERS_REL, LOCK_REL
from gov.release import HASH_NAME, MANIFEST_NAME, RELEASES_REL, ReleaseError, build, lock_from, verify


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def _repo(root):
    files = {
        "pyproject.toml": '[build-system]\nrequires = ["setuptools"]\nbuild-backend = "setuptools.build_meta"\n'
                          '[project]\nname = "demo"\nversion = "0.7.3"\n'
                          '[tool.setuptools.packages.find]\nwhere = ["src"]\n',
        "src/demo/__init__.py": "",
        "template/governance/kernel/schemas/ticket.schema.json": "{}\n",
        "template/governance/kernel/skills/superpowers/vendored.yaml": 'version: "v6.4.2"\n',
        "template/governance/kernel/vendor/superpowers/LICENSE": "MIT licence text\n",
    }
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    _git(root, "init", "-q", "-b", "w2/integrate")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "add", "-A")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-m", "first")
    return root


def test_a_release_records_its_manifest_and_the_manifest_hash(tmp_path):
    repo = _repo(tmp_path)
    folder = build(repo, "1.4.0")
    data = (folder / MANIFEST_NAME).read_bytes()
    manifest = json.loads(data)
    assert manifest["version"] == "1.4.0" and manifest["commit"] == _git(repo, "rev-parse", "HEAD").strip()
    assert manifest["cli_version"] == "0.7.3" and manifest["schema_versions"] == {
        "ticket": hashlib.sha256(b"{}\n").hexdigest()}
    assert manifest["vendored"]["superpowers"]["version"] == "v6.4.2"
    assert manifest["wheel"]["name"].endswith(".whl") and len(manifest["wheel"]["sha256"]) == 64
    assert (folder / HASH_NAME).read_text().split()[0] == hashlib.sha256(data).hexdigest()
    assert _git(repo, "tag", "--list") == ""
    assert verify(repo, "1.4.0")[1] == hashlib.sha256(data).hexdigest()
    with pytest.raises(ReleaseError, match="immutable"):
        _git(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "add", "-A")
        _git(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-m", "record")
        build(repo, "1.4.0")


@pytest.mark.parametrize("version", ("1.4", "v1.4.0", "01.4.0", "1.4.0-"))
def test_a_version_that_is_not_semantic_is_refused(tmp_path, version):
    with pytest.raises(ReleaseError, match="semantic"):
        build(_repo(tmp_path), version)


def test_an_unclean_tree_or_another_branch_is_refused(tmp_path):
    repo = _repo(tmp_path)
    (repo / "notes.txt").write_text("x\n", encoding="utf-8")
    with pytest.raises(ReleaseError, match="uncommitted"):
        build(repo, "1.4.0")
    (repo / "notes.txt").unlink()
    _git(repo, "checkout", "-q", "-b", "other")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "--allow-empty", "-m", "x")
    with pytest.raises(ReleaseError, match="w2/integrate"):
        build(repo, "1.4.0")
    assert not (repo / RELEASES_REL).exists()


def _commit(repo, message):
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "add", "-A")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "--allow-empty", "-m", message)


@pytest.mark.parametrize("how", ("older head", "record removed", "build metadata"))
def test_a_version_the_repository_already_knows_is_refused(tmp_path, how):
    repo = _repo(tmp_path)
    first = _git(repo, "rev-parse", "HEAD").strip()
    build(repo, "1.4.0")
    _commit(repo, "record")
    version = "1.4.0"
    if how == "older head":
        _git(repo, "checkout", "-q", "--detach", first)
    elif how == "record removed":
        _git(repo, "rm", "-q", "-r", "--", f"{RELEASES_REL}/1.4.0")
        _commit(repo, "removed")
    else:
        version = "1.4.0+build.2"
    with pytest.raises(ReleaseError, match="immutable"):
        build(repo, version)
    assert not (repo / RELEASES_REL / version).exists()


def test_a_version_an_existing_tag_names_is_refused(tmp_path):
    repo = _repo(tmp_path)
    _git(repo, "tag", "v1.4.0")
    _commit(repo, "later")
    with pytest.raises(ReleaseError, match="the tag v1.4.0"):
        build(repo, "1.4.0")
    assert not (repo / RELEASES_REL).exists()


def test_the_files_are_hashed_as_the_commit_holds_them(tmp_path):
    repo = _repo(tmp_path)
    rel = "template/governance/kernel/schemas/ticket.schema.json"
    (repo / rel).write_text("{ }\n", encoding="utf-8")
    _git(repo, "update-index", "--assume-unchanged", "--", rel)
    manifest = json.loads((build(repo, "1.4.0") / MANIFEST_NAME).read_bytes())
    assert manifest["files"]["governance/kernel/schemas/ticket.schema.json"] == hashlib.sha256(b"{}\n").hexdigest()


@pytest.mark.parametrize("how", ("changed", "added", "removed", "manifest hash"))
def test_verify_refuses_a_release_that_does_not_match_its_hashes(tmp_path, how):
    repo = _repo(tmp_path)
    folder = build(repo, "1.4.0")
    schema = repo / "template/governance/kernel/schemas/ticket.schema.json"
    if how == "changed":
        schema.write_text("{ }\n", encoding="utf-8")
    elif how == "added":
        (schema.parent / "added.schema.json").write_text("{}\n", encoding="utf-8")
    elif how == "removed":
        schema.unlink()
    else:
        (folder / HASH_NAME).write_text("0" * 64 + f"  {MANIFEST_NAME}\n", encoding="utf-8")
    with pytest.raises(ReleaseError, match="added.schema.json" if how == "added" else
                       ("manifest" if how == "manifest hash" else "ticket.schema.json")):
        verify(repo, "1.4.0")


def _installed(repo, project, tag):
    """A project as Copier leaves it before the lock task: the template's files and the answers file."""
    for path in (repo / "template").rglob("*"):
        if path.is_file():
            target = project / path.relative_to(repo / "template")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())
    (project / ANSWERS_REL).write_text(f"_commit: {tag}\n_template_commit: \"{'a' * 40}\"\n", encoding="utf-8")
    return project


def _released(tmp_path):
    repo = _repo(tmp_path / "gov-os")
    build(repo, "1.4.0")
    _commit(repo, "record")
    return repo


def _plain(repo, folder):
    """The template source with no release record and no history: copier.yml-less, template/ alone."""
    for path in (repo / "template").rglob("*"):
        if path.is_file():
            target = folder / path.relative_to(repo)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())
    return folder


def test_lock_from_a_plain_source_states_no_release(tmp_path):
    repo = _repo(tmp_path / "gov-os")
    project = _installed(repo, tmp_path / "product", "v0.1.0")
    assert lock_from(project, _plain(repo, tmp_path / "plain")) == (project / LOCK_REL, None)
    assert yaml.safe_load((project / LOCK_REL).read_text(encoding="utf-8"))["release"] is None


@pytest.mark.parametrize("source", ("plain folder", "records removed"))
def test_lock_from_never_rewrites_a_release_lock_without_a_release(tmp_path, source):
    repo = _released(tmp_path)
    project = _installed(repo, tmp_path / "product", "v1.4.0")
    assert lock_from(project, repo)[1] == "1.4.0"
    before = (project / LOCK_REL).read_bytes()
    if source == "plain folder":
        other = _plain(repo, tmp_path / "plain")
    else:
        _git(repo, "rm", "-q", "-r", "--", RELEASES_REL)
        _commit(repo, "removed")
        other = repo
    with pytest.raises(ReleaseError, match="records release 1.4.0"):
        lock_from(project, other)
    assert (project / LOCK_REL).read_bytes() == before


def test_lock_from_a_source_whose_records_were_removed_is_refused(tmp_path):
    repo = _released(tmp_path)
    _git(repo, "rm", "-q", "-r", "--", RELEASES_REL)
    _commit(repo, "removed")
    project = _installed(repo, tmp_path / "product", "v1.6.0")
    with pytest.raises(ReleaseError, match="history"):
        lock_from(project, repo)
    assert not (project / LOCK_REL).exists()


@pytest.mark.parametrize("lock", ("no release key", "not a map"))
def test_lock_from_refuses_a_lock_it_cannot_tell(tmp_path, lock):
    repo = _repo(tmp_path / "gov-os")
    project = _installed(repo, tmp_path / "product", "v0.1.0")
    (project / LOCK_REL).write_text("template_tag: v0.1.0\n" if lock == "no release key" else "- a list\n",
                                    encoding="utf-8")
    with pytest.raises(ReleaseError, match="release"):
        lock_from(project, _plain(repo, tmp_path / "plain"))


@pytest.mark.parametrize("role", ("engineer", "independent-auditor", "ticket-lead", ""))
def test_the_lock_task_refuses_every_role_but_the_orchestrator_and_the_owner(tmp_path, monkeypatch, role):
    from gov.cli.errors import GovError
    from gov.release.command import run

    repo = _repo(tmp_path / "gov-os")
    monkeypatch.setenv("GOV_ROLE", role)
    with pytest.raises(GovError, match="only the orchestrator") as refused:
        run(repo, argparse.Namespace(version=None, lock_from=str(repo)), {})
    assert refused.value.code == "RELEASE_REFUSED" and not (repo / LOCK_REL).exists()


@pytest.mark.parametrize("role", ("orchestrator", None))
def test_the_lock_task_runs_for_the_orchestrator_and_the_owner(tmp_path, monkeypatch, role):
    from gov.release.command import run

    repo = _repo(tmp_path / "gov-os")
    project = _installed(repo, tmp_path / "product", "v0.1.0")
    if role is None:
        monkeypatch.delenv("GOV_ROLE", raising=False)
    else:
        monkeypatch.setenv("GOV_ROLE", role)
    args = argparse.Namespace(version=None, lock_from=str(_plain(repo, tmp_path / "plain")))
    assert run(project, args, {}) == {"lock": str(project / LOCK_REL), "release": None}


# The build form is the owner's alone, in person (DEC-772), driven through the seam as W1-50 drives the lift's.
_WHOLE = [{"pid": 4242, "ppid": 4241, "comm": "python3", "exe": "/usr/bin/python3.12",
           "cmdline": ["python3", "-m", "gov.cli.main", "release", "1.4.0"]},
          {"pid": 4241, "ppid": 1, "comm": "bash", "exe": "/usr/bin/bash", "cmdline": ["-bash"]},
          {"pid": 1, "ppid": 0, "comm": "systemd", "exe": "/usr/lib/systemd/systemd", "cmdline": ["/sbin/init"]}]
_SESSION = {"pid": 4241, "ppid": 1, "comm": "node", "exe": "/usr/bin/node",
            "cmdline": ["node", "/usr/lib/node_modules/@anthropic-ai/claude-code/cli.js"]}


@pytest.fixture
def owner(monkeypatch):
    monkeypatch.delenv("GOV_ROLE", raising=False)
    monkeypatch.delenv("GOV_TICKET", raising=False)


@pytest.fixture
def pty():
    master, slave = os.openpty()
    yield master, slave
    for fd in (master, slave):
        try:
            os.close(fd)
        except OSError:
            pass


def _answer(master, reply):
    """Read the prompt on the pty's other side and type back ``reply(code)``; what was shown, in a list."""
    shown = []

    def typist():
        seen = b""
        try:
            while (found := re.search(rb"RELEASE-\d{4}", seen)) is None:
                chunk = os.read(master, 1024)
                if not chunk:
                    return
                seen += chunk
            shown.append(seen.decode())
            os.write(master, reply(found.group().decode()))
        except OSError:
            pass

    thread = threading.Thread(target=typist, daemon=True)
    thread.start()
    return thread, shown


def _untouched(repo, head):
    assert not (repo / RELEASES_REL).exists()
    assert _git(repo, "status", "--porcelain", "--untracked-files=all", "--ignored") == ""
    assert _git(repo, "rev-parse", "HEAD").strip() == head and _git(repo, "tag", "--list") == ""


def _nothing_shown(master):
    os.set_blocking(master, False)
    with pytest.raises(BlockingIOError):
        os.read(master, 1024)


def _refused(tmp_path, reason, ancestry=_WHOLE, terminal=None, pty=None):
    from gov.cli.errors import GovError
    from gov.release.command import _release_test

    repo = _repo(tmp_path / "gov-os")
    head = _git(repo, "rev-parse", "HEAD").strip()
    with pytest.raises(GovError) as refused:
        _release_test(repo, "1.4.0", ancestry=ancestry, terminal=terminal or (pty[1], pty[1]))
    assert refused.value.code == "RELEASE_REFUSED" and refused.value.details["reason"] == reason
    assert refused.value.message
    _untouched(repo, head)
    return refused.value


def test_the_owner_builds_a_release_with_the_code_typed_back(tmp_path, owner, pty):
    from gov.release.command import _release_test

    repo = _repo(tmp_path / "gov-os")
    head = _git(repo, "rev-parse", "HEAD").strip()
    thread, shown = _answer(pty[0], lambda code: f"  {code} \n".encode())
    result = _release_test(repo, "1.4.0", ancestry=_WHOLE, terminal=(pty[1], pty[1]))
    thread.join(5)
    assert re.search(r"\bRELEASE-\d{4}\b", shown[0]) and "1.4.0" in shown[0]
    assert result == {"version": "1.4.0", "record": str(repo / RELEASES_REL / "1.4.0")}
    assert (repo / RELEASES_REL / "1.4.0" / MANIFEST_NAME).is_file() and verify(repo, "1.4.0")
    assert _git(repo, "rev-parse", "HEAD").strip() == head and _git(repo, "tag", "--list") == ""


@pytest.mark.parametrize("ancestry", (
    [_WHOLE[0], _SESSION, _WHOLE[2]],
    [_WHOLE[0], {**_WHOLE[1], "comm": "claude"}, _WHOLE[2]],
    [_WHOLE[0], {**_WHOLE[1], "exe": "/home/o/.local/share/claude/versions/2.1.3"}, _WHOLE[2]],
), ids=("cli.js", "comm", "version file"))
def test_a_claude_code_session_among_the_ancestors_refuses(tmp_path, owner, pty, ancestry):
    _refused(tmp_path, "session", ancestry=ancestry, pty=pty)
    _nothing_shown(pty[0])


@pytest.mark.parametrize("ancestry", (
    [], _WHOLE[:2], [_WHOLE[0], {**_WHOLE[1], "ppid": 7}, _WHOLE[2]],
    [*_WHOLE[:2], {**_WHOLE[2], "comm": "bwrap"}], [*_WHOLE[:2], {**_WHOLE[2], "cmdline": []}],
    [{"pid": 4242}, *_WHOLE[1:]], {"pid": 1},
), ids=("empty", "short", "broken link", "another first process", "unread process", "malformed", "not a list"))
def test_an_ancestry_not_read_whole_refuses(tmp_path, owner, pty, ancestry):
    _refused(tmp_path, "ancestry", ancestry=ancestry, pty=pty)
    _nothing_shown(pty[0])


@pytest.mark.parametrize("variable, reason", (("GOV_ROLE", "role"), ("GOV_TICKET", "ticket")))
@pytest.mark.parametrize("value", ("orchestrator", "owner", "engineer", "DAEO-49o5", ""))
def test_gov_role_or_gov_ticket_set_to_any_value_refuses(tmp_path, owner, monkeypatch, pty, variable, reason, value):
    monkeypatch.setenv(variable, value)
    _refused(tmp_path, reason, pty=pty)
    _nothing_shown(pty[0])


@pytest.mark.parametrize("which", ("pipes", "input a pipe", "output a pipe", "closed", "not descriptors"))
def test_input_and_output_not_both_a_terminal_refuses(tmp_path, owner, pty, which):
    read, write = os.pipe()
    try:
        terminal = {"pipes": (read, write), "input a pipe": (read, pty[1]), "output a pipe": (pty[1], write),
                    "closed": (987, 988), "not descriptors": ("0", None)}[which]
        _refused(tmp_path, "terminal", terminal=terminal)
    finally:
        os.close(read)
        os.close(write)
    _nothing_shown(pty[0])


@pytest.mark.parametrize("reply", ("wrong", "empty", "end of input", "the code on a later line"))
def test_a_code_typed_back_wrong_refuses(tmp_path, owner, pty, reply):
    typed = {"wrong": lambda code: f"{code}0\n".encode(), "empty": lambda code: b"\n",
             "end of input": lambda code: b"\x04", "the code on a later line": lambda code: f"x\n{code}\n".encode()}
    thread, shown = _answer(pty[0], typed[reply])
    _refused(tmp_path, "code", pty=pty)
    thread.join(5)
    assert shown and re.search(r"RELEASE-\d{4}", shown[0])


def test_the_command_reads_the_real_chain_and_the_real_terminal(tmp_path, monkeypatch):
    from gov.release import command

    seen = []
    monkeypatch.setattr(command, "_release_test", lambda *args, **kwargs: seen.append((args, kwargs)) or {})
    command.run(tmp_path, argparse.Namespace(version="1.4.0", lock_from=None), {})
    assert seen == [((tmp_path, "1.4.0"), {})]


@pytest.mark.parametrize("role", ("orchestrator", None))
def test_the_command_refuses_from_this_process(tmp_path, monkeypatch, role):
    """Run under pytest, with no terminal planted and the real chain read: never built, by whichever check."""
    from gov.cli.errors import GovError
    from gov.release.command import run

    repo = _repo(tmp_path / "gov-os")
    head = _git(repo, "rev-parse", "HEAD").strip()
    monkeypatch.delenv("GOV_TICKET", raising=False)
    if role is None:
        monkeypatch.delenv("GOV_ROLE", raising=False)
    else:
        monkeypatch.setenv("GOV_ROLE", role)
    with pytest.raises(GovError) as refused:
        run(repo, argparse.Namespace(version="1.4.0", lock_from=None), {})
    assert refused.value.details["reason"] in ("session", "ancestry", "role", "terminal")
    _untouched(repo, head)
