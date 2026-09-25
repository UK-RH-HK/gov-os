from govbridge.core import view as viewmod
from govbridge.semantic import profile as profilemod


def test_real_embed_profile_shape(embed_profile_path):
    prof = profilemod.load_profile(embed_profile_path)
    assert "md" in prof.embed_kinds and "py" in prof.embed_kinds
    assert "out" in prof.lexical_only_kinds and "log" in prof.lexical_only_kinds
    assert prof.embed_kinds.isdisjoint(prof.lexical_only_kinds)
    assert prof.embed_kinds_size_le.get("json") == 65536
    assert prof.history_role_embedded is False


def test_kind_admitted_positive_list_narrower_than_include(embed_profile_path):
    prof = profilemod.load_profile(embed_profile_path)
    assert profilemod.kind_admitted(prof, "docs/NOTES.md", 100)
    assert profilemod.kind_admitted(prof, "config/app.toml", 100)
    assert not profilemod.kind_admitted(prof, "logs/build.out", 100)  # lexical-only kind
    assert not profilemod.kind_admitted(prof, "data/table.csv", 100)  # INCLUDE-effect, but not in embed_kinds
    assert profilemod.kind_admitted(prof, "small.json", 100)
    assert not profilemod.kind_admitted(prof, "big.json", 70000)  # over the json size cap


def test_kind_of():
    assert profilemod.kind_of("a/b/c.MD") == "md"
    assert profilemod.kind_of("a/b/Makefile") == ""


def _bare_profile(history_role_embedded=False):
    return profilemod.EmbedProfile(embed_kinds=frozenset(), embed_kinds_size_le={}, lexical_only_kinds=frozenset(),
                                    lexical_only_kinds_size_gt={}, history_role_embedded=history_role_embedded,
                                    layer_name="semantic", raw={})


def test_eligible_ref_names_excludes_history_when_layers_omit_semantic(fixture_repo, view_path):
    # view_path (conftest.py) writes layers: [...] WITHOUT "semantic" on the history ref, and WITH it on every
    # named ref -- exactly the real config/canonical-view.yaml's shape.
    resolved = viewmod.resolve_view(viewmod.load_view(view_path), repo=str(fixture_repo.root))
    names = profilemod.eligible_ref_names(resolved, _bare_profile())
    assert {"records", "product", "evidence"} <= names
    assert resolved.history  # the fixture repo does carry history/* branches
    for hist_name, _commit in resolved.history:
        assert hist_name not in names


def test_eligible_ref_names_admits_a_ref_with_no_layers_restriction(tmp_path, fixture_repo):
    # a view with no `layers:` field at all: every named ref defaults to admitted; history falls back to the
    # profile's own history_role_embedded default (False here) -- the fixed point for a view that never says.
    view_p = tmp_path / "view-no-layers.yaml"
    view_p.write_text(f"""\
schema: govbridge-canonical-view/1
view_id: fixture-view-no-layers
refs:
  - name: records
    ref: refs/heads/records
    follow: tip
    role: primary
  - name: product
    ref: refs/heads/product
    follow: pinned
    pinned_commit: {fixture_repo.product_pin}
    role: product
  - name: evidence
    ref: refs/heads/evidence
    follow: pinned
    pinned_commit: {fixture_repo.evidence_pin}
    role: evidence
  - name: history
    ref_glob: refs/heads/history/*
    follow: tip
    role: history
partitions:
  - name: product
    paths_from: "tools/identity.py#PRODUCT_CODE"
    owner: product
    fallback: [evidence, history]
  - name: records
    paths: ["**"]
    owner: records
    fallback: [product, evidence, history]
""", encoding="utf-8")
    resolved = viewmod.resolve_view(viewmod.load_view(str(view_p)), repo=str(fixture_repo.root))
    names = profilemod.eligible_ref_names(resolved, _bare_profile(history_role_embedded=False))
    assert {"records", "product", "evidence"} <= names
    for hist_name, _commit in resolved.history:
        assert hist_name not in names

    names_true = profilemod.eligible_ref_names(resolved, _bare_profile(history_role_embedded=True))
    for hist_name, _commit in resolved.history:
        assert hist_name in names_true
