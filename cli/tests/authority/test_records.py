"""The id-grammar definition/mention rules, exercised on the synthetic fixture repo: DR-YAML-TOP-ID, DR-MD-TABLE-ID,
DR-MD-HEADING-SEVERITY-family rules (via DR-MD-LEDGER-HEADING here), DR-FILE-STEM, fixtures/** never defines, and
census resolution counts."""
from govbridge.authority import records


def test_yaml_top_id_definition(fixture_repo, grammar_path):
    grammar = records.load_grammar(grammar_path)
    text = "id: FX-0001\nstatus: SUPERSEDED\nsuperseded_by: FX-0002\n"
    defs = records.extract_definitions_yaml(text, "spec/decisions/FX-0001.yaml", grammar)
    assert any(d.id == "FX-0001" for d in defs)


def test_md_table_id_with_ids_plural_and_emphasis(fixture_repo, grammar_path):
    import authority_repobuilder as repobuilder
    grammar = records.load_grammar(grammar_path)
    defs = records.extract_definitions_markdown(repobuilder.DISPOSITION_TEXT, repobuilder.DISPOSITION_PATH, grammar)
    ids = {d.id for d in defs}
    assert "FX-0010A" in ids and "FX-0010B" in ids


def test_md_table_id_singular(fixture_repo, grammar_path):
    import authority_repobuilder as repobuilder
    grammar = records.load_grammar(grammar_path)
    defs = records.extract_definitions_markdown(repobuilder.OWNER_AUTH_TEXT, repobuilder.OWNER_AUTH_PATH, grammar)
    assert any(d.id == "OA-FX-06" for d in defs)


def test_ledger_heading_definition(fixture_repo, grammar_path):
    import authority_repobuilder as repobuilder
    grammar = records.load_grammar(grammar_path)
    defs = records.extract_definitions_markdown(repobuilder.LEDGER_TEXT, repobuilder.LEDGER_PATH, grammar)
    ids = {d.id for d in defs}
    assert "X-L-0001" in ids and "X-L-0002" in ids


def test_file_stem_definition_stops_at_free_text():
    grammar = records.load_grammar("config/id-grammar.yaml")
    defs = records.extract_definitions_file_stem(
        "release/orchestration/phase-2/GATES/P2-ADJ-0004-SUBJECTLESS-REVIEW-FALLBACK.md", grammar, 20)
    assert [d.id for d in defs] == ["P2-ADJ-0004"]


def test_file_stem_definition_lowercase_suffix_excluded():
    grammar = records.load_grammar("config/id-grammar.yaml")
    defs = records.extract_definitions_file_stem(
        "release/orchestration/phase-2-context-bridge/HANDOFFS/BR-HO-0007-b5-0007.md", grammar, 20)
    assert [d.id for d in defs] == ["BR-HO-0007"]


def test_census_on_fixture_repo(fixture_repo, view_path, grammar_path):
    report = records.census(view_path=view_path, rules_path="config/corpus-rules.yaml", grammar_path=grammar_path,
                             repo=str(fixture_repo.root))
    # FX-0001/FX-0002 are decisions (not a run/handoff/ledger/owner_record family); the census must still run clean.
    assert report["total_mentions_censused"] >= 0
    assert "families" in report


def test_fixtures_never_define(fixture_repo, view_path, grammar_path):
    """The fixtures/greenfield/spec/decisions/FX-0001.yaml copy must never be selected as FX-0001's definition."""
    grammar = records.load_grammar(grammar_path)
    from govbridge.core import view as viewmod
    vc = viewmod.load_view(view_path)
    rv = viewmod.resolve_view(vc, repo=str(fixture_repo.root))
    commit = rv.ref_commit("records")
    scan = records.scan_ref(commit, grammar, "config/corpus-rules.yaml", repo=str(fixture_repo.root))
    real_defs = scan.definitions.get("FX-0001", [])
    assert all("fixtures/" not in d.path for d in real_defs)
    assert "FX-0001" in scan.fixture_definitions


def test_scan_ref_keep_text_matches_git_content(fixture_repo, view_path, grammar_path):
    grammar = records.load_grammar(grammar_path)
    from govbridge.core import view as viewmod, gitobj
    vc = viewmod.load_view(view_path)
    rv = viewmod.resolve_view(vc, repo=str(fixture_repo.root))
    commit = rv.ref_commit("records")
    scan = records.scan_ref(commit, grammar, "config/corpus-rules.yaml", repo=str(fixture_repo.root),
                             keep_text=True)
    import authority_repobuilder as repobuilder
    assert scan.text_by_path[repobuilder.OWNER_AUTH_PATH] == repobuilder.OWNER_AUTH_TEXT
    expected_blob = gitobj.blob_at(commit, repobuilder.OWNER_AUTH_PATH, repo=str(fixture_repo.root))
    assert scan.blob_by_path[repobuilder.OWNER_AUTH_PATH] == expected_blob
