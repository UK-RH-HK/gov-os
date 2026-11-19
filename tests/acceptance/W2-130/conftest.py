"""Fixtures for the W2-130 acceptance cases.

``gov links --all --json`` takes seconds, so each run is made once per session, on a clone (``git clone --shared``)
in a temporary folder: the tree under test is never written. A case whose record block is missing fails in its own
body (``Record.block`` calls ``pytest.fail``); no fixture skips.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_130_support as support  # noqa: E402


@pytest.fixture(scope="session")
def record() -> support.Record:
    return support.Record(support.ROOT / support.RECORD)


@pytest.fixture(scope="session")
def home(tmp_path_factory) -> Path:
    return tmp_path_factory.mktemp("w2-130-home")


@pytest.fixture(scope="session")
def clone_at(tmp_path_factory):
    """``clone_at(rev)``: a shared clone checked out at ``rev``, made once."""
    made: dict = {}

    def get(rev: str) -> Path:
        sha = support.full(rev)
        if sha not in made:
            made[sha] = support.make_clone(tmp_path_factory.mktemp("w2-130-clone") / "repo", sha)
        return made[sha]

    return get


@pytest.fixture(scope="session")
def head_tree(clone_at) -> Path:
    """HEAD's files: a clone checked out at HEAD (the cases read the committed tree, as ``gov links`` does)."""
    return clone_at(support.head())


@pytest.fixture(scope="session")
def head_findings(head_tree, home) -> list:
    return support.links_json(head_tree, home)


@pytest.fixture(scope="session")
def whole_tree(head_tree, tmp_path_factory) -> Path:
    """HEAD's files with the register whole again (EMERGENCY-2 11.3, DEC-1214 G4): since the old register moved to
    ``support.OLD_REGISTER``, the entries the clean-up marked stand there, and HEAD's register keeps the decisions in force
    only. A clone at HEAD whose register is ``support.whole_register`` (the archive's entries, then the later ones),
    committed, so the cases about the marks read every entry, and ``gov links`` and the drift script judge them, as
    before the move. Where HEAD holds no archive it is ``head_tree`` itself."""
    text = support.whole_register(head_tree)
    if text is None:
        return head_tree
    tree = support.make_clone(tmp_path_factory.mktemp("w2-130-whole") / "repo", support.head())
    (tree / support.REGISTER).write_text(text, encoding="utf-8")
    support.commit_all(tree, "the register whole: the archive's entries and the later ones")
    return tree


@pytest.fixture(scope="session")
def whole_findings(whole_tree, head_tree, home, request) -> list:
    """``gov links --all --json`` on ``whole_tree``: HEAD's findings where HEAD's register is whole."""
    if whole_tree == head_tree:
        return request.getfixturevalue("head_findings")
    return support.links_json(whole_tree, home)


@pytest.fixture(scope="session")
def pinned_findings(clone_at, home):
    """``pinned_findings(rev)``: ``(tree, findings)`` of ``gov links --all --json`` on the clone at ``rev``, run by the
    clone's own ``src`` (``PYTHONPATH=<clone>/src``), made once. A case pinned to a commit reads its counts here, so
    neither a later ticket edit nor a later change to ``gov links`` on the branch moves them (DEC-1156 (7))."""
    made: dict = {}

    def get(rev: str):
        tree = clone_at(rev)
        if tree not in made:
            made[tree] = support.links_json(tree, home, src=support.pinned_src(tree))
        return tree, made[tree]

    return get


@pytest.fixture(scope="session")
def start_findings(pinned_findings) -> list:
    """The starting head's findings, by the starting head's own ``gov links`` (pinned tree and pinned tool)."""
    return pinned_findings(support.START)[1]


@pytest.fixture(scope="session")
def variant_findings(tmp_path_factory, home):
    """``variant_findings(commit)``: ``gov links --all`` on ``commit``'s tree with the marks it appends taken off. Run by
    the commit's own tool (``PYTHONPATH=<clone>/src``, the variant clone's ``src`` being the commit's own: only the
    register is changed), not the branch's, so a later change to ``gov links`` cannot move which marks are free text
    (DEC-1156 (7), DEC-1164 (18) pin run 3)."""
    made: dict = {}

    def get(commit: str) -> list:
        sha = support.full(commit)
        if sha not in made:
            tree = support.make_clone(tmp_path_factory.mktemp("w2-130-variant") / "repo", sha)
            (tree / support.REGISTER).write_text(support.variant_register(sha), encoding="utf-8")
            support.commit_all(tree, "the register without the marks the commit appends")
            made[sha] = support.links_json(tree, home, src=support.pinned_src(tree))
        return made[sha]

    return get


@pytest.fixture(scope="session")
def propose_sources_at(clone_at, home):
    """``propose_sources_at(commit)``: ``{ticket path: [ids]}`` of ``gov links --propose-sources`` on the commit's
    parent, for the tickets open or in progress there. Run by the parent clone's own ``src`` (pinned tool, pin run 2)."""
    made: dict = {}

    def get(commit: str) -> dict:
        before = support.parent(commit)
        if before not in made:
            tree = clone_at(before)
            done = support.run_links(tree, home, "--propose-sources", "--all", src=support.pinned_src(tree))
            if done.returncode not in (0, 1):
                pytest.fail(f"gov links --propose-sources failed at {before}: {done.stderr.strip()[-300:]}")
            wanted = {}
            for path, ids in support.patch_source_ids(done.stdout).items():
                text = support.show(before, path)
                if text is not None and support.ticket_status(text) in ("open", "in_progress"):
                    wanted[path] = ids
            made[before] = wanted
        return made[before]

    return get
