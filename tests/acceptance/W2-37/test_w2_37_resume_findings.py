"""The second review's findings A, B, C, E and F4 (DEC-812 (1) and (2), DEC-136): behaviours the suite did not hold,
each as ``gov impact``'s output already names it (``graphs``, ``complete``, ``gaps``, ``--out``, ``--compare``,
``matches``, ``differences``).

A. ``--compare`` checks the CIT-E against the CIT-P as the repository holds it (the store, HEAD), not against a file
   edited since: a CIT-P with DEC-002 removed in the working tree, not committed, never turns a difference into a match.
B. A decision register that had no entries when the store was loaded and has one now, not committed, is a record graph
   that does not match the tree: ``graphs.record`` reads ``stale`` and names the register, whichever namespace of the
   path map the register sits in; and the report is never ``complete`` then.
C. A match against a proposal written as incomplete carries its incompleteness (``complete: false`` and its gaps).
E. A refusal names its real cause: a file that is missing, a path that is empty, a folder that is no file.
F4. ``--out`` whose file stem is an id the store already holds is refused, naming the clash.

Readings taken (README, "Third batch"): the result of ``--compare`` carries ``complete`` and ``gaps`` under the same
keys an assessment does; "names the clash", "names the real cause" and "names the file as missing" are said by a
word of the lists below, in the refusal's ``error``.

The cases that build a code index are ``local_only``: they cannot run in a worker's sandbox (P-W2-38).
"""

from __future__ import annotations

import pytest

import w2_37_support as support

CITE_REL = f"docs/changes/{support.CITE}.md"
CITP_REL = f"docs/changes/{support.CITP}.md"

NO_DEC2 = {kind: [i for i in ids if i != support.OTHER_DECISION] for kind, ids in support.PROPOSED.items()}

MISSING_WORDS = ("missing", "not exist", "no such", "not found", "cannot find", "can't find", "could not find")
EMPTY_WORDS = ("empty", "blank", "no path", "not a path")
FOLDER_WORDS = ("folder", "directory", "not a file", "is a dir")
CLASH_WORDS = ("already", "exist", "clash", "duplicate", "taken", "in use", "same id", "collide", "conflict")


def as_project(root):
    made = support.Project.__new__(support.Project)
    made.root, made.minute = root, 100
    return made


def said_by(document):
    return support.text_of(document.get("error")).lower()


def difference_ids(found):
    return sorted(entry.get("id") for entry in found.get("differences") or [] if isinstance(entry, dict))


def gap_ids_in(value):
    gaps = value if isinstance(value, list) else []
    return sorted(str(gap.get("id")) if isinstance(gap, dict) else str(gap) for gap in gaps)


def unchanged(before, after, what):
    changed = sorted(k for k in set(before[0]) | set(after[0]) if before[0].get(k) != after[0].get(k))
    assert not changed and before[1] == after[1], f"{what} changed {changed or 'git'}"


# --------------------------------------------------------------------------
# A. --compare against the proposal as committed
# --------------------------------------------------------------------------

def an_execution_record_that_leaves_out_dec_002(project, box):
    """The CIT-P (DEC-002 among its affected decisions) and a CIT-E without DEC-002, committed, the store loaded."""
    project.write(CITP_REL, support.proposal_file())
    project.write(CITE_REL, support.execution_file(affected=NO_DEC2))
    project.commit("the change's records")
    support.load_store(project.root, box)
    found = support.result(support.compare(project.root, CITE_REL, box))
    assert found.get("matches") is False and support.OTHER_DECISION in difference_ids(found), \
        f"the fixture is wrong: a CIT-E without {support.OTHER_DECISION} does not differ from its CIT-P: {found}"


def test_a_proposal_edited_after_it_was_committed_never_turns_a_difference_into_a_match(project, box):
    """DEC-002 is removed from the CIT-P file in the working tree, not committed. Either the comparison keeps the
    proposal as the store holds it (DEC-002 is still a difference), or it refuses or reports not matching, naming the
    CIT-P file that differs from HEAD."""
    an_execution_record_that_leaves_out_dec_002(project, box)
    project.write(CITP_REL, support.proposal_file(affected=NO_DEC2))                   # not committed
    run = support.compare(project.root, CITE_REL, box)
    document = support.envelope(run)
    show = run.describe()
    if document["ok"] is not True:
        support.assert_refused(run, f"{support.CITP}.md")                              # the file, named
        return
    found = document["result"]
    assert found.get("matches") is not True, \
        f"a CIT-P edited since it was committed makes the CIT-E match: {found.get('matches')!r}, " \
        f"differences {found.get('differences')!r}\n{show}"
    assert support.OTHER_DECISION in difference_ids(found) or f"{support.CITP}.md" in support.text_of(found), \
        f"the result neither keeps {support.OTHER_DECISION} as a difference nor names the CIT-P file that " \
        f"differs from HEAD\n{show}"


def test_a_proposal_edited_and_committed_is_the_one_compared(project, box):
    """The success: the same edit, committed and the store loaded again: the CIT-E now matches."""
    an_execution_record_that_leaves_out_dec_002(project, box)
    project.write(CITP_REL, support.proposal_file(affected=NO_DEC2))
    project.commit("the proposal revised")
    support.load_store(project.root, box)
    run = support.compare(project.root, CITE_REL, box)
    found = support.result(run)
    assert found.get("matches") is True and found.get("differences") == [], \
        f"a CIT-P revised and committed is not the one the CIT-E is checked against\n{run.describe()}"


# --------------------------------------------------------------------------
# B. A register's first uncommitted entry
# --------------------------------------------------------------------------

REGISTER_EMPTY = "# Decision log\n\nNo entries yet.\n"
FIRST_ENTRY = ("\n### DEC-090 — A first entry\n"
               "- **Status:** ACCEPTED (owner, 2026-10-09) · **Basis:** a fixture\n"
               "- **Supersedes:** DEC-001\n"
               "- **Decision:** the register's first entry.\n")
ENTRY_ID = "DEC-090"
# The register in a namespace of product memory: not a governance namespace of the path map.
SPLIT = {
    "gov": ([".gitignore", "governance/project/**", "docs/**", ".gitleaks.toml", "app/**"], "governance"),
    "ledger": (["records/**"], "product"),
}


def register_project(root, box, register_text, namespaces=None, code=False):
    """A repository whose path map names ``records/decision-log.md`` as the register (``register_text`` at HEAD),
    DEC-001 as a decision file, and, with ``code``, one function; committed, the store loaded."""
    project = support.Project(root)
    project.write(".gitignore", ".gov-runtime/\n")
    project.write(support.PATH_MAP_REL, support.path_map(namespaces, code=code, register=support.REGISTER_REL))
    project.write(support.REGISTER_REL, register_text)
    project.write("docs/adr/DEC-001.md", support.decision("DEC-001"))
    if code:
        project.write(".gitleaks.toml", support.GITLEAKS_TEMPLATE.read_text(encoding="utf-8"))
        project.write("app/__init__.py", "")
        project.write("app/solo.py", "def w37_solo(value):\n    return value + 1\n")
    project.commit("register fixture")
    support.load_store(project.root, box)
    return project


def assert_record_graph_stale_naming_the_register(run):
    """``graphs.record`` is not ``ok``, reads ``stale``, and the report names the register's path; ``complete`` is
    false (a refusal: the record graph named, ``stale`` and the register's path)."""
    found = support.assert_incomplete(run, "record", word="stale")
    show = run.describe()
    if found is None:
        said = said_by(support.envelope(run))
    else:
        assert "stale" in found["graphs"]["record"].lower(), \
            f"`graphs.record` does not read stale: {found['graphs']['record']!r}\n{show}"
        said = (support.text_of(found["graphs"]) + support.text_of(found["gaps"])
                + support.text_of(found.get("warnings", []))).lower()
    assert support.REGISTER_REL in said, \
        f"the report does not name the register {support.REGISTER_REL} that differs from the tree\n{show}"


def test_a_register_with_no_entry_at_head_and_a_first_one_uncommitted_reads_stale(tmp_path, built, box):
    project = register_project(tmp_path / "repo", box, REGISTER_EMPTY)
    clean = support.assessment(support.impact(project.root, "DEC-001", box))
    assert clean["graphs"]["record"] == support.GRAPH_OK, \
        f"the fixture is wrong: a store loaded from the clean tree is not current: {clean['graphs']}"
    project.write(support.REGISTER_REL, REGISTER_EMPTY + FIRST_ENTRY)                  # not committed
    assert_record_graph_stale_naming_the_register(support.impact(project.root, "DEC-001", box))


def test_a_register_in_a_non_governance_namespace_with_a_first_entry_uncommitted_reads_stale(tmp_path, built, box):
    """The path map puts ``records/**`` (the register) in product memory; the store is loaded, then the register's
    first entry is written and not committed."""
    project = register_project(tmp_path / "repo", box, REGISTER_EMPTY, namespaces=SPLIT)
    clean = support.assessment(support.impact(project.root, "DEC-001", box))
    assert clean["graphs"]["record"] == support.GRAPH_OK, \
        f"the fixture is wrong: a store loaded from the clean tree is not current: {clean['graphs']}"
    project.write(support.REGISTER_REL, REGISTER_EMPTY + FIRST_ENTRY)                  # not committed
    assert_record_graph_stale_naming_the_register(support.impact(project.root, "DEC-001", box))


def test_a_register_that_held_one_entry_at_head_and_gets_a_further_one_uncommitted_reads_stale(project, box):
    """The already-right case, kept as a guard: the fixture's register holds DEC-070 at HEAD."""
    project.write(support.REGISTER_REL, support.REGISTER + FIRST_ENTRY)                # not committed
    assert_record_graph_stale_naming_the_register(support.impact(project.root, "DEC-001", box))


def test_a_register_entry_committed_and_the_store_loaded_again_reads_the_record_graph_current(tmp_path, built, box):
    """The success: the first entry committed, the store loaded again: ``ok`` for DEC-001, and the entry itself is a
    decision the command knows (a stated change of its own)."""
    project = register_project(tmp_path / "repo", box, REGISTER_EMPTY)
    project.write(support.REGISTER_REL, REGISTER_EMPTY + FIRST_ENTRY)
    project.commit("the register's first entry")
    support.load_store(project.root, box)
    run = support.impact(project.root, "DEC-001", box)
    found = support.assessment(run)
    assert found["graphs"]["record"] == support.GRAPH_OK, \
        f"a store loaded from the tree as it is is not reported current: {found['graphs']}\n{run.describe()}"
    entry = support.assessment(support.impact(project.root, ENTRY_ID, box))
    assert [item["id"] for item in entry["change"]] == [ENTRY_ID] and entry["graphs"]["record"] == support.GRAPH_OK, \
        f"{ENTRY_ID}, committed in the register and loaded, is not a stated change read from a current record graph: " \
        f"{entry['change']}, {entry['graphs']}"


INDEXED = set()


@pytest.fixture(scope="module", autouse=True)
def remove_daemons(box):
    yield
    support.remove_daemon_dirs(box, INDEXED)


@pytest.fixture()
def indexed_split_register(built, tools, box, tmp_path):
    """The register in a non-governance namespace and empty at HEAD, the store loaded and the code index built:
    both graphs current."""
    project = register_project(tmp_path / "repo", box, REGISTER_EMPTY, namespaces=SPLIT, code=True)
    INDEXED.add(str(project.root))
    support.build_index(project.root, box)
    found = support.ask(project.root, "DEC-001", box, path=box.full)
    assert all(found["graphs"][g] == support.GRAPH_OK for g in support.GRAPHS), \
        f"the fixture is wrong: both graphs are not current before the entry is written: {found['graphs']}"
    if not found["gaps"]:
        assert found["complete"] is True, "the fixture is wrong: both graphs read, no gap, and not complete"
    return project


@pytest.mark.local_only
def test_with_a_current_code_graph_a_first_register_entry_uncommitted_is_never_complete(indexed_split_register, box):
    """With a current code graph, ``complete`` turns on the record graph alone: the register's first entry, in a
    non-governance namespace, written and not committed."""
    project = indexed_split_register
    project.write(support.REGISTER_REL, REGISTER_EMPTY + FIRST_ENTRY)                  # not committed
    run = support.impact(project.root, "DEC-001", box, path=box.full)
    assert_record_graph_stale_naming_the_register(run)


# --------------------------------------------------------------------------
# C. An incomplete proposal's match carries its incompleteness
# --------------------------------------------------------------------------

def proposal_written_as(complete, gaps):
    """A CIT-P whose frontmatter says whether the assessment it was written from was complete, and its gaps."""
    return support.frontmatter(
        {"id": support.CITP, "type": support.CITP_TYPE, "status": "ACCEPTED", "state_class": "EVIDENCE",
         "change": [support.CHANGED], "radius": "R2", "depth": 3, "affected": support.PROPOSED,
         "complete": complete, "graphs": {"record": "ok", "code": "ok" if complete else "unreadable"},
         "gaps": gaps},
        title=f"{support.CITP}: the impact of changing {support.CHANGED}")


def compared_with(project, box, proposal):
    """``proposal`` and a CIT-E with the same lists, committed, the store loaded, compared."""
    project.write(CITP_REL, proposal)
    project.write(CITE_REL, support.execution_file())
    project.commit("the change's records")
    support.load_store(project.root, box)
    run = support.compare(project.root, CITE_REL, box)
    return support.result(run), run


def test_a_match_with_a_proposal_written_as_incomplete_carries_its_incompleteness(project, box):
    gaps = [{"id": support.FAR_SPEC, "reason": "beyond the depth"}]
    found, run = compared_with(project, box, proposal_written_as(False, gaps))
    show = run.describe()
    assert isinstance(found.get("matches"), bool), f"`matches` is not true or false\n{show}"
    assert found.get("complete") is False, \
        f"the CIT-P says `complete: false` and the result does not carry it: {found.get('complete')!r}\n{show}"
    assert gap_ids_in(found.get("gaps")) == [support.FAR_SPEC], \
        f"the result does not carry the CIT-P's gaps ({support.FAR_SPEC}): {found.get('gaps')!r}\n{show}"


def test_a_match_with_a_proposal_the_assessment_wrote_as_incomplete_carries_it_end_to_end(project, box):
    """No code tool on PATH, so ``--out`` writes a CIT-P that says ``complete: false`` (the first review's finding 3);
    a CIT-E recording just its lists, compared, carries that."""
    out = project.root / "docs" / "changes" / "CITP-910.md"
    support.assessment(support.impact(project.root, support.CHANGED, box, out=out))
    front, _ = support.read_frontmatter(out)
    assert front.get("complete") is False, f"the fixture is wrong: the written CIT-P does not say it is incomplete"
    project.write(CITE_REL, support.execution_file(proposal=front["id"], affected=front["affected"]))
    project.commit("the written proposal and its execution record")
    support.load_store(project.root, box)
    run = support.compare(project.root, CITE_REL, box)
    found = support.result(run)
    assert found.get("complete") is False, \
        f"the CIT-P written as incomplete is compared and the result does not carry it: {found}\n{run.describe()}"


def test_a_match_with_a_proposal_written_as_complete_says_no_incompleteness(project, box):
    """The success: ``complete: true`` and no gaps: the result does not say incomplete and lists no gap."""
    found, run = compared_with(project, box, proposal_written_as(True, []))
    assert found.get("matches") is True and found.get("differences") == [], f"agreeing records: {found}"
    assert found.get("complete") is not False, f"a complete CIT-P is carried as incomplete\n{run.describe()}"
    assert gap_ids_in(found.get("gaps")) == [], f"a complete CIT-P's result lists gaps: {found.get('gaps')!r}"


# --------------------------------------------------------------------------
# E. Refusals name their real cause
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", ["CITP-404", "CITE-404"])
def test_comparing_a_file_that_does_not_exist_is_refused_as_missing(project, box, name):
    """Neither a CIT-P nor a CIT-E file is there: the refusal names the file and says it is missing; it does not say
    that the record lists nothing under ``affected``."""
    before = support.snapshot(project.root)
    run = support.compare(project.root, f"docs/changes/{name}.md", box)
    document = support.assert_refused(run, name)
    show = run.describe()
    assert run.returncode == 1, f"the refusal does not exit 1: {run.returncode}\n{show}"
    said = said_by(document) if document else (run.stdout + run.stderr).lower()
    assert any(word in said for word in MISSING_WORDS), \
        f"the refusal does not say the file is missing (one of {MISSING_WORDS}): {said}\n{show}"
    assert "lists nothing" not in said and "under affected" not in said and "under `affected`" not in said, \
        f"the refusal blames the file's lists, not its absence: {said}\n{show}"
    unchanged(before, support.snapshot(project.root), "a refused --compare")


def test_comparing_against_a_proposal_whose_file_is_gone_is_refused_as_missing(project, box):
    """The CIT-P was committed and the store loaded; its file is then removed from the working tree. The CIT-E names
    it: the refusal names the proposal's file and says it is missing, not that it lists nothing under ``affected``."""
    project.write(CITP_REL, support.proposal_file())
    project.write(CITE_REL, support.execution_file())
    project.commit("the change's records")
    support.load_store(project.root, box)
    (project.root / CITP_REL).unlink()
    before = support.snapshot(project.root)
    run = support.compare(project.root, CITE_REL, box)
    document = support.assert_refused(run, support.CITP)                       # the proposal, by id or by its path
    show = run.describe()
    assert run.returncode == 1, f"the refusal does not exit 1: {run.returncode}\n{show}"
    said = said_by(document) if document else (run.stdout + run.stderr).lower()
    assert any(word in said for word in MISSING_WORDS), \
        f"the refusal does not say the proposal's file is missing (one of {MISSING_WORDS}): {said}\n{show}"
    assert "lists nothing" not in said and "under affected" not in said and "under `affected`" not in said, \
        f"the refusal blames the file's lists, not its absence: {said}\n{show}"
    unchanged(before, support.snapshot(project.root), "a refused --compare")


def test_out_with_an_empty_path_is_refused_as_empty(repo, box):
    before = support.snapshot(repo)
    run = support.impact(repo, support.CHANGED, box, out="")
    document = support.assert_refused(run)
    show = run.describe()
    assert run.returncode == 1, f"the refusal does not exit 1: {run.returncode}\n{show}"
    said = said_by(document) if document else (run.stdout + run.stderr).lower()
    assert any(word in said for word in EMPTY_WORDS), \
        f"the refusal does not say the path is empty (one of {EMPTY_WORDS}): {said}\n{show}"
    assert "already" not in said and "a file is there" not in said, \
        f"the refusal says a file is there already, which is not the cause: {said}\n{show}"
    unchanged(before, support.snapshot(repo), "a refused --out with an empty path")


def test_out_naming_an_existing_folder_is_refused_as_a_folder(repo, box):
    before = support.snapshot(repo)
    run = support.impact(repo, support.CHANGED, box, out=repo / "docs" / "adr")
    document = support.assert_refused(run)
    show = run.describe()
    assert run.returncode == 1, f"the refusal does not exit 1: {run.returncode}\n{show}"
    said = said_by(document) if document else (run.stdout + run.stderr).lower()
    assert any(word in said for word in FOLDER_WORDS), \
        f"the refusal does not say the path is a folder (one of {FOLDER_WORDS}): {said}\n{show}"
    assert "already" not in said and "a file is there" not in said, \
        f"the refusal says a file is there already, which is not the cause: {said}\n{show}"
    unchanged(before, support.snapshot(repo), "a refused --out naming a folder")


def test_out_naming_a_file_that_is_there_already_is_refused_as_that(project, box):
    """The success (kept as a guard): a file is there, which no record holds; the refusal names it and says it is
    there already; the file is not touched."""
    rel = "docs/changes/CITP-905.md"
    project.write(rel, "occupied\n")
    project.commit("a file where the proposal would go")
    support.load_store(project.root, box)
    before = support.snapshot(project.root)
    run = support.impact(project.root, support.CHANGED, box, out=project.root / rel)
    document = support.assert_refused(run, "CITP-905.md")
    show = run.describe()
    assert run.returncode == 1, f"the refusal does not exit 1: {run.returncode}\n{show}"
    said = said_by(document) if document else (run.stdout + run.stderr).lower()
    assert "already" in said or "exist" in said, f"the refusal does not say the file is there already: {said}\n{show}"
    unchanged(before, support.snapshot(project.root), "a refused --out naming a file that is there")


# --------------------------------------------------------------------------
# F4. --out's stem against existing ids
# --------------------------------------------------------------------------

@pytest.mark.parametrize("stem", [support.CITP, support.CHANGED], ids=["a-cit-p", "a-decision"])
def test_out_whose_stem_is_an_id_the_store_holds_is_refused_naming_the_clash(project, box, stem):
    """CITP-001 is a stored record (committed, the store loaded); so is DEC-001. The file ``--out`` names is a new
    path whose stem is that id."""
    project.write(CITP_REL, support.proposal_file())
    project.commit("a stored proposal")
    support.load_store(project.root, box)
    before = support.snapshot(project.root)
    out = project.root / "docs" / "proposals" / f"{stem}.md"
    run = support.impact(project.root, support.CHANGED, box, out=out)
    document = support.assert_refused(run, stem)
    show = run.describe()
    assert run.returncode == 1, f"the refusal does not exit 1: {run.returncode}\n{show}"
    said = said_by(document) if document else (run.stdout + run.stderr).lower()
    assert any(word in said for word in CLASH_WORDS), \
        f"the refusal names {stem} but does not say it clashes with a record the store holds " \
        f"(one of {CLASH_WORDS}): {said}\n{show}"
    assert not out.exists(), f"a refused --out still wrote {out}\n{show}"
    unchanged(before, support.snapshot(project.root), "a refused --out whose stem is an existing id")


def test_out_whose_stem_is_a_new_id_is_written(project, box):
    """The success: a stem no record holds, in a folder that is new."""
    out = project.root / "docs" / "proposals" / "CITP-950.md"
    support.assessment(support.impact(project.root, support.CHANGED, box, out=out))
    assert out.is_file(), f"--out wrote no file at {out}"
    front, _ = support.read_frontmatter(out)
    support.check_frontmatter(front, support.CITP_TYPE)
