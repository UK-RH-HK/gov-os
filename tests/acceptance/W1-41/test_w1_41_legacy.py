"""Stage A8: the legacy importer and legacy retirement [CAP-42.a, CAP-42.b, CAP-42.c, CAP-44.e].

Success lines 3, 5 and 6; failure line 3 ("A legacy rule file stays loaded after retirement"). The proposals here
retire and delete; they move nothing, so no artefact needs the code graph.

The import is held by its result (what is under ``.rulesync/`` afterwards), not by its way: rulesync 24.0.0's own
``import`` was measured in a temporary folder and brings in only part of the five kinds (README, package P-3).
"""

from __future__ import annotations

import json
import re

import pytest

import w1_41_support as support

LEGACY_PATHS = [item["path"] for item in support.legacy_proposal()]


def _proposal():
    return support.legacy_proposal() + [support.entry(support.NOTES, "DELETE_FROM_ACTIVE_TREE")]


@pytest.fixture(scope="module")
def retired(tmp_path_factory, interface):
    """One adoption carried through A8, for the cases that only read what it left. Never changed."""
    base = tmp_path_factory.mktemp("w1-41-retired")
    project = support.build_project(base / "harbour")
    adoption = support.Adoption(project, support.make_sandbox(base / "sandbox"), interface)
    adoption.baseline = support.tree(project)
    adoption.baseline_commit = support.head(project)
    adoption.through("A8", _proposal())
    return adoption


def _dispositions(adoption):
    """Path -> the entry that records its disposition, from the A6 and A8 records."""
    found = {}
    for stage in ("A6", "A8"):
        for item in support.base.find_records(adoption.stages[stage].front, key="disposition"):
            if isinstance(item.get("path"), str):
                found[item["path"]] = item
    return found


def _not_retired(run, project, interface, baseline, paths, *names):
    """The stage answered (whatever its exit code), named every one of ``names``, and left ``paths`` in place."""
    assert not support.not_built(run), f"gov adopt --lite is not built\n{run.describe()}"
    support.base.assert_envelope(run, interface, command="adopt")
    for name in names:
        assert name in run.stdout, f"the answer does not name {name!r}\n{run.describe()}"
    problems = support.moved_nothing(project, baseline, paths)
    assert not problems, f"retired although it must not be: {problems}\n{run.describe()}"


def _before_a8(adopt_in, project, entries=None):
    adoption = adopt_in(project)
    adoption.through("A6", entries if entries is not None else support.legacy_proposal())
    return adoption, support.tree(project)


# --------------------------------------------------------------------------
# The import into .rulesync/ [CAP-42.a]
# --------------------------------------------------------------------------

@pytest.mark.parametrize("kind", sorted(support.RULE_KINDS))
def test_each_kind_of_legacy_rule_file_is_imported_into_rulesync(retired, kind):
    """AGENTS.md role sections, .cursorrules, .windsurfrules, .cursor/rules/*.mdc and .mcp/tools.json: what each
    file says is found under ``.rulesync/`` afterwards, committed."""
    files, phrases = support.RULE_KINDS[kind]
    for phrase in phrases:
        assert support.phrase_under_rulesync(retired.project, phrase), \
            f"{kind}: nothing under {support.RULESYNC_REL}/ holds {phrase!r} from {list(files)}"


def test_the_imported_mcp_server_keeps_its_command(retired):
    together = [rel for rel, text in support.under_rulesync(retired.project).items()
                if re.search(rf'"{support.MCP_SERVER}"', text) and support.MCP_COMMAND in text]
    assert together, f"no file under {support.RULESYNC_REL}/ holds the server {support.MCP_SERVER!r} with its command"


def test_the_two_role_sections_of_agents_md_are_both_imported(retired):
    for phrase in (support.ROLE_REVIEWER_PHRASE, support.ROLE_BUILDER_PHRASE):
        assert support.phrase_under_rulesync(retired.project, phrase), f"the role section with {phrase!r} is lost"


def test_the_a8_record_names_what_each_legacy_rule_file_was_imported_into(retired):
    stage = retired.stages["A8"]
    imported = stage.front.get("imported")
    assert isinstance(imported, list) and imported, f"{stage.record}: no list 'imported'"
    sources = {item.get("source"): item for item in imported if isinstance(item, dict)}
    for rel in support.RULE_FILES:
        assert rel in sources, f"{stage.record}: 'imported' does not name {rel}"
        into = sources[rel].get("into")
        assert isinstance(into, list) and into and all(
            isinstance(path, str) and path.startswith(support.RULESYNC_REL + "/")
            and support.at_head(retired.project, path) is not None for path in into), \
            f"{stage.record}: {rel} is not imported into committed files under {support.RULESYNC_REL}/ ({into!r})"


# --------------------------------------------------------------------------
# Failure line 3: no legacy rule file stays loaded
# --------------------------------------------------------------------------

def test_no_legacy_rule_file_stays_where_an_agent_tool_loads_instructions(retired):
    project, now = retired.project, support.tree(retired.project)
    for rel in (".cursorrules", ".windsurfrules", ".cursor/rules/style.mdc", ".cursor/rules/review.mdc",
                ".mcp/tools.json"):
        assert rel not in now, f"{rel} is still tracked after retirement"
        assert not (project / rel).exists(), f"{rel} is still in the working tree after retirement"
    assert not list((project / ".cursor").rglob("*.mdc")), "a .mdc rule file is still under .cursor/"
    # AGENTS.md is also a path rulesync generates (ADR-0002 section 5). The legacy file is not there any more:
    # the path is empty, or holds another text.
    agents = project / "AGENTS.md"
    legacy = support.AGENTS_MD.encode("utf-8")
    assert not agents.exists() or agents.read_bytes() != legacy, "the legacy AGENTS.md is still in the working tree"
    assert support.at_head(project, "AGENTS.md") != legacy, "the legacy AGENTS.md is still at HEAD"


def test_adapter_generation_is_run_or_named(retired):
    """DEC-488: generating AGENTS.md, CLAUDE.md and .claude/ from .rulesync/ is a step after the install;
    "W1-41's adoption runs or names the step"."""
    stage = retired.stages["A8"]
    said = json.dumps(stage.result) + (retired.project / stage.record).read_text(encoding="utf-8")
    ran = (retired.project / "CLAUDE.md").is_file()
    assert ran or "rulesync generate" in said, \
        "A8 neither generated the adapters nor names the step `rulesync generate`"


def test_a_legacy_rule_file_that_cannot_be_parsed_is_not_retired(tmp_path, adopt_in, interface):
    """DEC-449: a tools file that is not JSON was not imported; it is not retired as if it had been."""
    project = support.build_project(tmp_path / "bad-tools",
                                    extra={".mcp/tools.json": '{"mcpServers": {"ledger": {"command": \n'})
    adoption, baseline = _before_a8(adopt_in, project)
    run = adoption.run("A8")
    _not_retired(run, project, interface, baseline, [".mcp/tools.json"], ".mcp/tools.json")
    assert run.returncode in support.REFUSAL_EXIT_CODES, f"A8 reports success\n{run.describe()}"


def test_a_legacy_rule_file_that_cannot_be_read_is_not_retired(tmp_path, adopt_in, interface):
    if not support.can_be_made_unreadable(tmp_path):
        pytest.skip("this user is not held by file permissions: no file can be made unreadable")
    project = support.build_project(tmp_path / "unreadable-rules")
    adoption, baseline = _before_a8(adopt_in, project)
    restore = support.make_unreadable(project / ".cursorrules")
    try:
        run = adoption.run("A8")
    finally:
        restore()
    _not_retired(run, project, interface, baseline, [".cursorrules"], ".cursorrules")
    assert run.returncode in support.REFUSAL_EXIT_CODES, f"A8 reports success\n{run.describe()}"
    assert not support.phrase_under_rulesync(project, support.CURSORRULES_PHRASE), \
        "the unreadable file's text is under .rulesync/: it was not read by the tool"


# --------------------------------------------------------------------------
# The raw chat database [CAP-42.b, CAP-44.e]
# --------------------------------------------------------------------------

def test_the_chat_database_is_marked_non_authoritative(retired):
    recorded = retired.map_entries()[support.CHAT_DB]
    authority = str(recorded.get("authority", "")).lower().replace("-", "_")
    assert authority == "non_authoritative", \
        f"{support.CHAT_DB}: the path map does not mark it non-authoritative (authority: {recorded.get('authority')!r})"


def test_the_chat_database_is_retired_after_its_knowledge_is_in_records(retired):
    project = retired.project
    assert support.CHAT_DB not in support.tree(project) and not (project / support.CHAT_DB).exists(), \
        f"{support.CHAT_DB} is still in the active tree"
    assert support.at_head(project, support.EXTRACTION_REL) is not None, "the extracted record did not stay"
    item = _dispositions(retired).get(support.CHAT_DB)
    assert item is not None, f"no disposition is recorded for {support.CHAT_DB}"
    said = json.dumps(item)
    assert support.EXTRACTION_ID in said or support.EXTRACTION_REL in said, \
        f"the record of the retirement does not name the record its knowledge was extracted to ({said})"


def test_a_chat_database_with_nothing_extracted_is_not_retired(tmp_path, adopt_in, interface):
    """"Its unique knowledge is extracted to records before retirement": no record cites the database as its
    source, so it stays."""
    project = support.build_project(tmp_path / "no-extraction", extraction=False)
    adoption, baseline = _before_a8(adopt_in, project)
    run = adoption.run("A8")
    _not_retired(run, project, interface, baseline, [support.CHAT_DB], support.CHAT_DB)


def test_an_extraction_from_another_content_of_the_database_does_not_count(tmp_path, adopt_in, interface):
    """The extraction record cites the database by path and content hash. A record made from other bytes says
    nothing about the database that is there now."""
    stale = support.extraction_record(b"an earlier database")
    project = support.build_project(tmp_path / "stale-extraction", extraction=False,
                                    extra={support.EXTRACTION_REL: stale})
    adoption, baseline = _before_a8(adopt_in, project)
    run = adoption.run("A8")
    _not_retired(run, project, interface, baseline, [support.CHAT_DB], support.CHAT_DB)


def test_a_chat_database_that_cannot_be_read_is_not_retired(tmp_path, adopt_in, interface):
    if not support.can_be_made_unreadable(tmp_path):
        pytest.skip("this user is not held by file permissions: no file can be made unreadable")
    project = support.build_project(tmp_path / "unreadable-chat")
    adoption, baseline = _before_a8(adopt_in, project)
    restore = support.make_unreadable(project / support.CHAT_DB)
    try:
        run = adoption.run("A8")
    finally:
        restore()
    _not_retired(run, project, interface, baseline, [support.CHAT_DB], support.CHAT_DB)
    assert run.returncode in support.REFUSAL_EXIT_CODES, f"A8 reports success\n{run.describe()}"


# --------------------------------------------------------------------------
# The legacy memory store: dependency proof, CIT-E, index refresh [CAP-42.b]
# --------------------------------------------------------------------------

def test_a_memory_store_nothing_cites_is_retired(retired):
    now = support.tree(retired.project)
    left = [rel for rel in support.MEMORY_FILES if rel in now or (retired.project / rel).exists()]
    assert not left, f"the legacy memory store is still in the active tree: {left}"


def test_the_dependency_proof_is_recorded(retired):
    """The A8 record says what the proof read and that it found no citer; it is not left unsaid."""
    stage = retired.stages["A8"]
    proof = stage.front.get("dependency_proof")
    assert isinstance(proof, dict), f"{stage.record}: no 'dependency_proof'"
    assert proof.get("citers") == [], f"{stage.record}: the proof does not record an empty list of citers"
    read = json.dumps(proof)
    assert "record" in read and "rule" in read, \
        f"{stage.record}: the proof does not say that it read the records and the rules ({read})"


CITER_RECORD = "spec/decisions/dec-400.md"
CITER_RULE = f"{support.RULESYNC_REL}/rules/memory.md"
BROKEN_RECORD = "spec/decisions/dec-402.md"


def test_a_memory_store_an_active_record_cites_is_not_retired(tmp_path, adopt_in, interface):
    citer = support.record_text("DEC-400", "decision", "ACTIVE", "Votes follow the legacy quorum.",
                                depends_on=["LEG-001"])
    project = support.build_project(tmp_path / "cited-by-record", extra={CITER_RECORD: citer})
    adoption, baseline = _before_a8(adopt_in, project)
    run = adoption.run("A8")
    _not_retired(run, project, interface, baseline, list(support.MEMORY_FILES))
    assert "DEC-400" in run.stdout or CITER_RECORD in run.stdout, f"the citing record is not named\n{run.describe()}"


def test_a_memory_store_a_rule_cites_is_not_retired(tmp_path, adopt_in, interface):
    rule = "---\nroot: false\ntargets:\n  - '*'\n---\nBefore a vote, read legacy/memory/index.md.\n"
    project = support.build_project(tmp_path / "cited-by-rule", extra={CITER_RULE: rule})
    adoption, baseline = _before_a8(adopt_in, project)
    run = adoption.run("A8")
    _not_retired(run, project, interface, baseline, list(support.MEMORY_FILES), CITER_RULE)


def test_a_record_that_is_not_active_does_not_keep_the_store(tmp_path, adopt_in):
    """"No active record or rule cites it": a deprecated record's citation is no dependency."""
    citer = support.record_text("DEC-401", "decision", "DEPRECATED", "An older vote rule.", depends_on=["LEG-002"])
    project = support.build_project(tmp_path / "cited-by-deprecated", extra={"spec/decisions/dec-401.md": citer})
    adoption = adopt_in(project)
    adoption.through("A8", support.legacy_proposal())
    left = [rel for rel in support.MEMORY_FILES if rel in support.tree(project)]
    assert not left, f"the store was kept for a record that is not active: {left}"


def test_a_record_that_cannot_be_read_is_no_proof_of_no_dependency(tmp_path, adopt_in, interface):
    """DEC-449: a record whose frontmatter cannot be read may be active and may cite the store. The proof is not
    established, the store stays, and the record is named."""
    broken = "---\nid: DEC-402\ntype: decision\nstatus: [ACTIVE\n---\n\n# DEC-402\n\nSee legacy/memory/index.md.\n"
    project = support.build_project(tmp_path / "unreadable-record", extra={BROKEN_RECORD: broken})
    adoption, baseline = _before_a8(adopt_in, project)
    run = adoption.run("A8")
    _not_retired(run, project, interface, baseline, list(support.MEMORY_FILES), BROKEN_RECORD)


def test_the_retirement_of_the_memory_store_is_a_cit_e(retired):
    stage = retired.stages["A8"]
    rel = stage.front.get("cit_e")
    assert isinstance(rel, str) and rel, f"{stage.record}: no 'cit_e'"
    data = support.at_head(retired.project, rel)
    assert data is not None, f"the CIT-E record {rel} is not committed"
    text = data.decode("utf-8")
    front = support.frontmatter(text, rel)
    assert front.get("type") == "change-execution-record", \
        f"{rel}: type is not 'change-execution-record' (the form of this repository's CIT-E records)"
    missing = [path for path in support.MEMORY_FILES if path not in text]
    assert not missing, f"{rel}: the CIT-E does not record the retirement of {missing}"


def test_the_index_is_refreshed_after_the_retirement(retired):
    """"A CIT-E followed by an index refresh": measured by ``gov doctor`` in the temporary project, the index is
    fresh at the commit that no longer holds the store."""
    section = support.doctor_section(retired.project, retired.sandbox, "index_freshness")
    assert section.get("index_status") == "fresh", \
        f"after the retirement the index is not fresh ({section.get('index_status')!r}, stale: {section.get('stale')})"


# --------------------------------------------------------------------------
# Zero ACTIVE decisions from retired systems [CAP-42.a]
# --------------------------------------------------------------------------

def test_retired_systems_contribute_no_active_decision(retired):
    project = retired.project
    active = []
    for rel in support.tree(project):
        if not rel.endswith(".md"):
            continue
        text = (support.at_head(project, rel) or b"").decode("utf-8", "replace")
        if not text.startswith("---"):
            continue
        try:
            front = support.frontmatter(text, rel)
        except AssertionError:
            continue
        if front.get("status") == "ACTIVE" and (front.get("id") in support.MEMORY_DECISION_IDS
                                                or rel.startswith("legacy/")):
            active.append((rel, front.get("id")))
    assert not active, f"a decision of the retired memory store is still ACTIVE at HEAD: {active}"


# --------------------------------------------------------------------------
# Archive policy [CAP-42.c]
# --------------------------------------------------------------------------

def test_retired_material_stays_reachable_as_it_was(retired):
    """Each retired artefact's record names where it can still be read (a commit or an archive ref); there the
    path holds byte for byte what it held before the adoption."""
    recorded = _dispositions(retired)
    for rel in LEGACY_PATHS:
        item = recorded.get(rel)
        assert item is not None, f"no disposition is recorded for {rel}"
        where = item.get("reachable_at")
        commit = support.resolve(retired.project, where) if isinstance(where, str) and where else None
        assert commit, f"{rel}: 'reachable_at' ({where!r}) does not resolve in the project"
        assert support.tree(retired.project, commit).get(rel) == retired.baseline[rel], \
            f"{rel}: not reachable at {where} with the content it had"


def test_nothing_left_the_tree_without_a_recorded_disposition(retired):
    now = support.tree(retired.project)
    recorded = _dispositions(retired)
    gone = sorted(rel for rel in retired.baseline if rel not in now)
    assert support.NOTES in gone, f"{support.NOTES} (DELETE_FROM_ACTIVE_TREE) is still in the tree"
    without = [rel for rel in gone
               if not (isinstance(recorded.get(rel, {}).get("disposition"), str) and recorded[rel]["disposition"])]
    assert not without, f"left the active tree without a recorded disposition: {without}"
    unplanned = sorted(set(gone) - {item["path"] for item in _proposal()})
    assert not unplanned, f"left the active tree although the path map keeps them: {unplanned}"


def test_what_the_path_map_keeps_is_untouched_by_the_retirement(retired):
    """The import may write under ``.rulesync/``; nothing else that the path map keeps changes or leaves."""
    now = support.tree(retired.project)
    planned = {item["path"] for item in _proposal()}
    changed = sorted(rel for rel, blob in retired.baseline.items()
                     if rel not in planned and not rel.startswith(support.RULESYNC_REL + "/") and now.get(rel) != blob)
    assert not changed, f"kept artefacts changed or left during the retirement: {changed}"


def test_a_file_deleted_from_the_active_tree_stays_reachable_too(retired):
    item = _dispositions(retired).get(support.NOTES)
    assert item is not None, f"no disposition is recorded for {support.NOTES}"
    commit = support.resolve(retired.project, item.get("reachable_at") or "")
    assert commit and support.tree(retired.project, commit).get(support.NOTES) == retired.baseline[support.NOTES], \
        f"{support.NOTES}: not reachable at {item.get('reachable_at')!r} with the content it had"
