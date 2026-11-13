"""S10: the close's clean clone is a warm one kept between closes (reset, stores kept), replaced by a fresh one when
it cannot be reset; the record says so.

Two planted closes in a row: PROJ-aaaa, then PROJ-ffff (both change the widget; W2-bb's known red, red on the green
base, needs the head without the change, so the clone is used). Between them the clone is dirtied (a tracked file changed)
and a file is put in its stores folder (``.gov-runtime/``, which git ignores); or its ``.git`` is broken.

Red on today's code: today's close keeps no clone at ``.gov-runtime/close/clone`` and its record has no ``clone``;
it refuses the planted red.
"""

import pytest

import w2_115_support as support

STORE_MARK = ".gov-runtime/w2-115-store-mark.txt"


def _first_close(base):
    """The first close. The green base is the initial commit (one green nightly record names it; the known red is
    red there already), an ancestor of HEAD in both closes.

    Rewrite-Reason: DEC-1150 (2): the planted project needs a green base on HEAD's line under the owner's P1-K (a).
    Before, the project had no nightly record, so the known red was judged against the parent of the ticket's oldest
    own commit, the fallback the owner dropped (R2-1)."""
    sandbox = support.cli_support.make_sandbox(base / "sandbox")
    told = base / "told"
    known = support.node_of("W2-bb", "bb_known", "test_bb_known")
    project = support.Smart(base / "project", told, nightly="green",
                            reds={known.split("::")[0]: support.telling("test_bb_known", told, support.KNOWN_RED)})
    project.work({support.WIDGET: "# the widget, CHANGED\n"})
    project.ready(sandbox)
    first = project.close(sandbox)
    support.passed(first)
    project.commit_what_the_close_left()
    return sandbox, project


def _second_close(sandbox, project):
    project.work({support.WIDGET: "# the widget, CHANGED again\n"}, ticket=support.SECOND)
    project.ready(sandbox, ticket=support.SECOND)
    run = project.close(sandbox, ticket=support.SECOND)
    support.passed(run)
    return project.record(support.SECOND).get("clone")


def _two_closes(base):
    sandbox, project = _first_close(base)
    clone = project.root / support.CLONE_REL
    first = project.record().get("clone")
    assert clone.is_dir(), f"no clone at {support.CLONE_REL} after the first close"
    (clone / "README.md").write_text("dirtied between the closes\n", encoding="utf-8")
    support.close_support.write(clone, STORE_MARK, "kept\n")
    second = _second_close(sandbox, project)
    return project, first, second


@pytest.fixture(scope="module")
def two_closes(tmp_path_factory):
    """The two closes in a row, or the AssertionError that stopped them (raised again in each case that reads them,
    so a case fails rather than errs in its setup)."""
    try:
        return _two_closes(tmp_path_factory.mktemp("w2_115_clone_reused"))
    except AssertionError as why:
        return why


def _read(two_closes):
    if isinstance(two_closes, AssertionError):
        raise two_closes
    return two_closes


def test_the_first_close_keeps_its_clone_at_the_named_place(two_closes):
    """S10: the first close's record names the clone at ``.gov-runtime/close/clone``."""
    _, first, _ = _read(two_closes)
    assert isinstance(first, dict) and first.get("path") == support.CLONE_REL, f"clone: {first!r}"


def test_the_second_close_reuses_the_first_s_clone_reset_with_its_stores_kept(two_closes):
    """S10: the second close reuses the same folder (``reused: true``), reset (the dirtied file is back to the
    commit's text) and with its stores kept (the file in its stores folder is still there)."""
    project, _, second = _read(two_closes)
    clone = project.root / support.CLONE_REL
    assert isinstance(second, dict) and second.get("path") == support.CLONE_REL and second.get("reused") is True, \
        f"the second close did not reuse the clone: {second!r}"
    assert (clone / "README.md").read_text(encoding="utf-8") == "# A project\n", "the clone was not reset"
    assert (clone / STORE_MARK).is_file(), "the clone's stores were not kept"


def test_a_clone_that_cannot_be_reset_is_replaced_and_the_record_says_so(tmp_path_factory):
    """S10: a clone whose ``.git`` is broken cannot be reset: the next close replaces it with a fresh one (a working
    repository at the same place) and its record says so (``reused: false``, a reason under ``replaced``)."""
    sandbox, project = _first_close(tmp_path_factory.mktemp("w2_115_clone_replaced"))
    clone = project.root / support.CLONE_REL
    assert clone.is_dir(), f"no clone at {support.CLONE_REL} after the first close"
    dot_git = clone / ".git"
    if dot_git.is_dir():
        (dot_git / "HEAD").write_text("not a ref\n", encoding="utf-8")
    else:
        dot_git.write_text("gitdir: /nonexistent/w2-115\n", encoding="utf-8")
    second = _second_close(sandbox, project)
    assert isinstance(second, dict) and second.get("reused") is False, f"clone: {second!r}"
    assert str(second.get("replaced") or "").strip(), f"the record does not say why the clone was replaced: {second!r}"
    assert support.close_support.git(clone, "rev-parse", "HEAD", check=False).strip(), "the fresh clone is no repository"
