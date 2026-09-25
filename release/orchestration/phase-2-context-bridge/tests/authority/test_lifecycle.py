"""The precedence order (ARCHITECTURE.md section 5.2), on the fixture repo: mandatory_bridge_inputs items,
section-scoping (unanchored lines/whole-file UNCLASSIFIED), structured metadata, registry supersessions/overrides,
class_rules, and the UNCLASSIFIED/UNKNOWN fallback."""
from govbridge.authority import lifecycle, registry


def _reg(fixture_repo, registry_path, view_path):
    return registry.load(registry_path, verify_commit="records", view_path=view_path, repo=str(fixture_repo.root))


def _mandatory(fixture_repo, view_path):
    return lifecycle._load_mandatory_items(repo=str(fixture_repo.root), view_path=view_path)


def test_mandatory_bridge_input_class_is_exact(fixture_repo, registry_path, view_path):
    reg = _reg(fixture_repo, registry_path, view_path)
    mandatory = _mandatory(fixture_repo, view_path)
    c = lifecycle.classify("FX-DIRECTION", reg=reg, mandatory_items=mandatory, repo=str(fixture_repo.root),
                            view_path=view_path)
    assert c.cls == "OWNER_DIRECTION_TO_TEST"
    assert c.derivation in ("MANDATORY_BRIDGE_INPUT", "REGISTRY_CITED")


def test_section_scoped_ids_resolve_to_distinct_sections(fixture_repo, registry_path, view_path):
    reg = _reg(fixture_repo, registry_path, view_path)
    mandatory = _mandatory(fixture_repo, view_path)
    a = lifecycle.classify("FX-0010A", reg=reg, mandatory_items=mandatory, repo=str(fixture_repo.root),
                            view_path=view_path)
    b = lifecycle.classify("FX-0010B", reg=reg, mandatory_items=mandatory, repo=str(fixture_repo.root),
                            view_path=view_path)
    assert (a.line_start, a.line_end) != (b.line_start, b.line_end)
    assert a.cls == "OWNER_DECISION" and b.cls == "OWNER_DECISION"


def test_unanchored_line_is_unclassified(fixture_repo, registry_path, view_path):
    import authority_repobuilder as repobuilder
    reg = _reg(fixture_repo, registry_path, view_path)
    mandatory = _mandatory(fixture_repo, view_path)
    c = lifecycle.classify("some-unanchored-line", path=repobuilder.DISPOSITION_PATH, commit="HEAD", line_start=3,
                            line_end=3, reg=reg, mandatory_items=mandatory, repo=str(fixture_repo.root),
                            view_path=view_path)
    assert c.cls == "UNCLASSIFIED"


def test_whole_file_request_on_anchored_file_is_unclassified(fixture_repo, registry_path, view_path):
    import authority_repobuilder as repobuilder
    reg = _reg(fixture_repo, registry_path, view_path)
    mandatory = _mandatory(fixture_repo, view_path)
    c = lifecycle.classify("FX-0010A/B-whole-file", path=repobuilder.DISPOSITION_PATH, commit="HEAD", reg=reg,
                            mandatory_items=mandatory, repo=str(fixture_repo.root), view_path=view_path)
    assert c.cls == "UNCLASSIFIED"


def test_structured_metadata_supersession(fixture_repo, registry_path, view_path):
    reg = _reg(fixture_repo, registry_path, view_path)
    c1 = lifecycle.classify("FX-0001", reg=reg, repo=str(fixture_repo.root), view_path=view_path)
    assert c1.cls == "ARCHITECTURE_DECISION"
    assert c1.lifecycle == "SUPERSEDED"
    assert c1.derivation == "EXACT_METADATA"

    c2 = lifecycle.classify("FX-0002", reg=reg, repo=str(fixture_repo.root), view_path=view_path)
    assert c2.lifecycle == "ACTIVE"


def test_scoped_supersession_note_only(fixture_repo, registry_path, view_path):
    reg = _reg(fixture_repo, registry_path, view_path)
    c = lifecycle.classify("OA-FX-06", reg=reg, repo=str(fixture_repo.root), view_path=view_path)
    assert c.cls == "OWNER_DECISION"
    assert c.lifecycle == "ACTIVE"
    assert any("partially superseded" in n for n in c.notes)


def test_whole_scope_supersession_flips_lifecycle(fixture_repo, registry_path, view_path):
    reg = _reg(fixture_repo, registry_path, view_path)
    c = lifecycle.classify("FX-GEN-1", reg=reg, repo=str(fixture_repo.root), view_path=view_path)
    assert c.lifecycle == "SUPERSEDED"  # no recognisable status word in the quote -> defaults SUPERSEDED
    assert c.derivation == "REGISTRY_CITED"


def test_lifecycle_override_restricts_to_withdrawn(fixture_repo, registry_path, view_path):
    reg = _reg(fixture_repo, registry_path, view_path)
    c = lifecycle.classify("FX-WITHDRAWN-0001", reg=reg, repo=str(fixture_repo.root), view_path=view_path)
    assert c.cls == "EVIDENCE_WITHDRAWN"
    assert c.lifecycle == "WITHDRAWN"


def test_class_rule_fallback(fixture_repo, registry_path, view_path):
    import authority_repobuilder as repobuilder
    reg = _reg(fixture_repo, registry_path, view_path)
    c = lifecycle.classify("FX-RES-0001", path=repobuilder.LESSON_PATH, commit="HEAD", reg=reg,
                            repo=str(fixture_repo.root), view_path=view_path)
    assert c.cls == "EVIDENCE"


def test_totally_unknown_id_is_unclassified(fixture_repo, registry_path, view_path):
    reg = _reg(fixture_repo, registry_path, view_path)
    c = lifecycle.classify("NOTHING-LIKE-THIS-EXISTS-9999", reg=reg, repo=str(fixture_repo.root),
                            view_path=view_path)
    assert c.cls == "UNCLASSIFIED"
    assert c.lifecycle == "UNKNOWN"


def test_pre_text_matches_live_read(fixture_repo, registry_path, view_path):
    """govbridge.authority.layer's persisted class_lifecycle rows must equal classify()'s live computation -- the
    SAME function is used either way; pre_text is a caller-side read-reuse, never a different code path."""
    import authority_repobuilder as repobuilder
    from govbridge.core import view as viewmod, gitobj
    reg = _reg(fixture_repo, registry_path, view_path)
    mandatory = _mandatory(fixture_repo, view_path)
    vc = viewmod.load_view(view_path)
    rv = viewmod.resolve_view(vc, repo=str(fixture_repo.root))
    commit = rv.ref_commit("records")
    text = gitobj.read_path(commit, repobuilder.OWNER_AUTH_PATH, repo=str(fixture_repo.root)).decode("utf-8")

    live = lifecycle.classify("OA-FX-06", path=repobuilder.OWNER_AUTH_PATH, commit=commit, reg=reg,
                               mandatory_items=mandatory, repo=str(fixture_repo.root), view_path=view_path)
    via_pretext = lifecycle.classify("OA-FX-06", path=repobuilder.OWNER_AUTH_PATH, commit=commit, reg=reg,
                                      mandatory_items=mandatory, repo=str(fixture_repo.root), view_path=view_path,
                                      pre_text=text)
    assert live.to_dict() == via_pretext.to_dict()
