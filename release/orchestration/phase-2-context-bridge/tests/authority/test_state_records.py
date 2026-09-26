"""State records (REPAIR_PLAN.md section 4, R1-RL): YAML state files expose nested keys and id:-bearing list
items as addressable records (record_def), so `exact id` resolves them. CAUSE_ANALYSIS measured one state file
with 54 top-level keys but only 2 record_def rows; this closes that gap generically -- via
config/state-aliases.yaml's own closed, generic registry (govbridge.authority.records._state_alias_paths()), never
a hard-coded filename in code (OC-BR-02).

``tests/fixtures/authority/authority_repobuilder.py`` (an existing fixture this node does not own or modify) already
writes a synthetic ORCHESTRATOR_STATE.yaml-shaped document at ``BRIDGE_STATE_PATH`` -- which is EXACTLY the real
"bridge" alias's path (config/state-aliases.yaml). That coincidence is exploited here on purpose: it lets this test
exercise the REAL, unmodified `config/state-aliases.yaml` / `govbridge.authority.lifecycle.find_definition` /
`govbridge.core.exact.id_lookup` pipeline end-to-end, on synthetic fixture content, with no change to any file
outside this node's mutation scope.
"""
from __future__ import annotations

from govbridge.authority import lifecycle as lifecyclemod
from govbridge.authority import records as R
from govbridge.core import exact as exactmod
from govbridge.core import view as viewmod


def _commit(fixture_repo, view_path):
    vc = viewmod.load_view(view_path)
    rv = viewmod.resolve_view(vc, repo=str(fixture_repo.root))
    return rv.ref_commit("records")


# --- unit-level: extract_definitions_state_keys, in isolation (a synthetic alias_paths, no repo needed) ----------

def test_top_level_and_nested_keys_become_definitions():
    grammar = R.load_grammar("config/id-grammar.yaml")
    text = (
        "schema: demo-state/1\n"
        "protocol:\n"
        "  launcher: some/path.md\n"
        "  normative_control_plane: V8.2\n"
        "mandatory_bridge_inputs:\n"
        "  authority_classes:\n"
        "    OWNER_DECISION: binding\n"
    )
    defs = R.extract_definitions_state_keys(text, "fixtures/state/DEMO_STATE.yaml", grammar,
                                             alias_paths={"fixtures/state/DEMO_STATE.yaml": "demo"})
    by_id = {d.id: d for d in defs}
    assert set(by_id) == {"schema", "protocol", "launcher", "normative_control_plane",
                           "mandatory_bridge_inputs", "authority_classes", "OWNER_DECISION"}
    # a whole-document, multi-child span covers every line of its own content, not just its first child
    assert (by_id["protocol"].line_start, by_id["protocol"].line_end) == (2, 4)
    # a single-line leaf's span is exactly its own line
    assert (by_id["launcher"].line_start, by_id["launcher"].line_end) == (3, 3)
    # a nested key's record_path is the full dotted address; a top-level key's is None (it IS its own bare name)
    assert by_id["launcher"].record_path == "protocol.launcher"
    assert by_id["protocol"].record_path is None
    assert by_id["mandatory_bridge_inputs"].rule == "DR-YAML-STATE-KEY"
    # never local -- a state key resolves directly, unlike a RECORD#LOCAL bare token (DR-MD-HEADING-LOCAL)
    assert all(not d.local for d in defs)


def test_list_elements_are_never_descended_into():
    """A list of many rows sharing field names (id, path, content, class, ...) must never explode into one
    definition per row -- only the KEY that HOLDS the list (here, "items") is a definition."""
    grammar = R.load_grammar("config/id-grammar.yaml")
    text = (
        "items:\n"
        "- id: FX-0001\n"
        "  class: OWNER_DECISION\n"
        "  path: elsewhere.md\n"
        "- id: FX-0002\n"
        "  class: EVIDENCE\n"
    )
    defs = R.extract_definitions_state_keys(text, "fixtures/state/DEMO_STATE.yaml", grammar,
                                             alias_paths={"fixtures/state/DEMO_STATE.yaml": "demo"})
    ids = {d.id for d in defs}
    assert ids == {"items"}


def test_non_state_file_yields_no_state_key_definitions():
    grammar = R.load_grammar("config/id-grammar.yaml")
    text = "protocol:\n  launcher: x\n"
    assert R.extract_definitions_state_keys(text, "some/other/file.yaml", grammar,
                                             alias_paths={"fixtures/state/DEMO_STATE.yaml": "demo"}) == []


def test_extract_definitions_yaml_includes_state_keys_when_recognised(monkeypatch):
    """The wiring point: extract_definitions_yaml (called generically by records.scan_ref/layer.build/
    lifecycle._find_definition for EVERY .yaml file) must itself surface state-key definitions -- not only the
    standalone extract_definitions_state_keys function -- for a path the REAL config/state-aliases.yaml registers.
    Monkeypatches the module-level alias cache (never config/state-aliases.yaml itself, outside this node's scope)
    so this is isolated from whatever the real file currently contains."""
    grammar = R.load_grammar("config/id-grammar.yaml")
    monkeypatch.setattr(R, "_STATE_ALIASES_CACHE", {"fixtures/state/DEMO_STATE.yaml": "demo"})
    text = "top_key:\n  nested: value\n"
    defs = R.extract_definitions_yaml(text, "fixtures/state/DEMO_STATE.yaml", grammar)
    assert any(d.id == "top_key" and d.rule == "DR-YAML-STATE-KEY" for d in defs)
    assert any(d.id == "nested" and d.rule == "DR-YAML-STATE-KEY" for d in defs)


# --- end-to-end, on the real config/state-aliases.yaml + the real lifecycle/exact pipeline ------------------------

def test_nested_state_key_resolved_by_exact_id(fixture_repo, view_path):
    """The acceptance criterion in its own words: "a nested YAML key is resolved by `exact id`" -- exercised
    through the REAL, unmodified `govbridge.core.exact.id_lookup` (what `govbridge exact id <token>` runs), never
    a shortcut straight to extract_definitions_state_keys."""
    result = exactmod.id_lookup("authority_classes", ref="records", view_path=view_path,
                                 repo=str(fixture_repo.root))
    assert result["definition_sites"], result
    site = result["definition_sites"][0]
    assert site["path"].endswith("ORCHESTRATOR_STATE.yaml")
    assert site["line_start"] < site["line_end"]
    assert "resolved via config/id-grammar.yaml" in result["note"]


def test_top_level_state_key_resolved_by_find_definition(fixture_repo, view_path):
    for token in ("mandatory_bridge_inputs", "owner_records", "running_work"):
        found = lifecyclemod.find_definition(token, repo=str(fixture_repo.root), view_path=view_path)
        assert found is not None, token
        path, commit, line_start, line_end = found
        assert path.endswith("ORCHESTRATOR_STATE.yaml")
        assert line_start <= line_end


def test_record_def_rows_persist_through_the_authority_layer(fixture_repo, view_path, registry_path):
    """record_def rows for state keys flow into the EXISTING, already-registered "authority" store layer
    (govbridge.authority.layer.build/put_record_def) automatically -- no new layer, no new registration needed --
    exactly like every other kind of definition records.scan_ref already finds."""
    import sqlite3

    from govbridge.authority import layer as layermod
    from govbridge.core import view as viewmod

    conn = sqlite3.connect(":memory:")
    vc = viewmod.load_view(view_path)
    resolved = viewmod.resolve_view(vc, repo=str(fixture_repo.root))
    rules = [{"id": "INCLUDED", "effect": "INCLUDE", "match": {}}]
    stats = layermod.build(conn, resolved, rules, str(fixture_repo.root), from_clean=True,
                            view_path=view_path, registry_path=registry_path)
    assert "skipped_reason" not in stats, stats

    rows = conn.execute(
        "SELECT id, line_start, line_end FROM record_def WHERE path LIKE '%ORCHESTRATOR_STATE.yaml' "
        "AND rule='DR-YAML-STATE-KEY' ORDER BY id"
    ).fetchall()
    ids = {r[0] for r in rows}
    assert {"mandatory_bridge_inputs", "authority_classes", "owner_records", "running_work"} <= ids


def test_authority_layer_digest_is_reproducible_across_two_from_clean_builds(fixture_repo, view_path, registry_path):
    """The state-key addition must not break the existing "identical digests across two from-clean builds"
    property every layer already documents (ARCHITECTURE.md section 8.1)."""
    import sqlite3

    from govbridge.authority import layer as layermod
    from govbridge.core import view as viewmod

    vc = viewmod.load_view(view_path)
    resolved = viewmod.resolve_view(vc, repo=str(fixture_repo.root))
    rules = [{"id": "INCLUDED", "effect": "INCLUDE", "match": {}}]

    digests = []
    for _ in range(2):
        conn = sqlite3.connect(":memory:")
        layermod.build(conn, resolved, rules, str(fixture_repo.root), from_clean=True, view_path=view_path,
                        registry_path=registry_path)
        digests.append(layermod.digest(conn).digest)
    assert digests[0] == digests[1]
