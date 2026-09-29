"""The mandatory-input resolver on the fixture repo: MandatoryItem construction, a sha256 mismatch gives BLOCKED,
state_ref [*] expansion, id_form/path_form resolution, and the directory-path (paths[]) case."""
import dataclasses

from govbridge.authority import resolver


def _task_spec(view_path, required_inputs):
    return {
        "schema": "govbridge-task-spec/1", "task_id": "T-1", "role": "test", "objective": "test",
        "view": view_path, "required_inputs": required_inputs, "mutation_scope": [], "prohibitions": [],
        "required_checks": [], "completion_vocabulary": ["ANSWERED"], "budget_profile": "bounded-builder",
    }


def test_state_ref_star_expansion_resolves_all_mandatory_items(fixture_repo, view_path):
    task_spec = _task_spec(view_path, [
        {"state_ref": "state:bridge#mandatory_bridge_inputs.items[*]", "reason": "test"},
    ])
    result = resolver.resolve(task_spec, repo=str(fixture_repo.root), registry_path="tests/fixtures/authority/fixture-authority-registry.yaml")
    assert result.status == "OK", result.blocked_reasons
    ids = {i.id for i in result.items}
    assert ids == {"FX-0010A", "FX-0010B", "FX-DIRECTION", "FX-HYPOTHESIS"}
    for item in result.items:
        assert isinstance(item, resolver.MandatoryItem)
        assert dataclasses.is_dataclass(item)


def test_six_way_section_scoping_generic_four_items(fixture_repo, view_path):
    """The fixture analog of node B5's 'six OD-P2-10A/B items resolve to six distinct heading sections' check: our
    four FX items each resolve to a DISTINCT, non-overlapping line range in the shared disposition file."""
    task_spec = _task_spec(view_path, [
        {"state_ref": "state:bridge#mandatory_bridge_inputs.items[*]", "reason": "test"},
    ])
    result = resolver.resolve(task_spec, repo=str(fixture_repo.root), registry_path="tests/fixtures/authority/fixture-authority-registry.yaml")
    spans = {(i.line_start, i.line_end) for i in result.items}
    assert len(spans) == 4  # four distinct sections, none collapsed onto the file-level span


def test_sha256_mismatch_gives_blocked(fixture_repo, view_path):
    from govbridge.authority import registry as registrymod
    from govbridge.core import view as viewmod

    # a required_inputs row shaped like a mandatory_bridge_inputs item, with a deliberately wrong sha256
    row = {"id": "FX-0001-DECISION", "class": "ARCHITECTURE_DECISION", "path": "spec/decisions/FX-0001.yaml",
           "sha256": "0" * 64}
    reg = registrymod.load("tests/fixtures/authority/fixture-authority-registry.yaml", verify_commit="records",
                            view_path=view_path, repo=str(fixture_repo.root))
    resolved_view = viewmod.resolve_view(viewmod.load_view(view_path), repo=str(fixture_repo.root))
    item, reason = resolver._mandatory_item_from_row(row, resolved_view, reg, {}, "test-row", "test reason",
                                                       repo=str(fixture_repo.root))
    assert item is None
    assert "sha256 mismatch" in reason


def test_id_form_required_input(fixture_repo, view_path):
    task_spec = _task_spec(view_path, [
        {"id": "FX-0002", "reason": "test", "required_status": "ACTIVE"},
    ])
    result = resolver.resolve(task_spec, repo=str(fixture_repo.root), registry_path="tests/fixtures/authority/fixture-authority-registry.yaml")
    assert result.status == "OK", result.blocked_reasons
    assert result.items[0].id == "FX-0002"
    assert result.items[0].lifecycle == "ACTIVE"


def test_id_form_wrong_required_status_blocks(fixture_repo, view_path):
    task_spec = _task_spec(view_path, [
        {"id": "FX-0001", "reason": "test", "required_status": "ACTIVE"},  # FX-0001 is SUPERSEDED
    ])
    result = resolver.resolve(task_spec, repo=str(fixture_repo.root), registry_path="tests/fixtures/authority/fixture-authority-registry.yaml")
    assert result.status == "BLOCKED"


def test_path_form_required_input(fixture_repo, view_path):
    import authority_repobuilder as repobuilder
    task_spec = _task_spec(view_path, [
        {"path": f"{repobuilder.LEDGER_PATH}@records", "reason": "test"},
    ])
    result = resolver.resolve(task_spec, repo=str(fixture_repo.root), registry_path="tests/fixtures/authority/fixture-authority-registry.yaml")
    assert result.status == "OK", result.blocked_reasons
    assert result.items[0].path == repobuilder.LEDGER_PATH


def test_id_form_uses_the_resolved_view_passed_in_even_if_the_records_ref_moves_after_it_was_resolved(
        fixture_repo, view_path):
    """BR-DAG-AMEND-R1-23 reopening (pass 5, an independent re-audit's own finding, confirmed empirically before
    this fix -- a `resolve_view` call-counting probe showed 2 resolutions for one `resolve()` call, not 1): the
    id-form branch used to call `lifecycle._find_definition` WITHOUT threading `resolved_view` through, even
    though `resolve()`'s own OTHER two branches (state_ref/path-form, exercised by the tests above) already did.
    A "records" ref that moves between `resolve()`'s own one resolution and this branch's own separate one could
    build the returned MandatoryItem from a DIFFERENT commit than the view a compile or `packet verify` had
    already resolved once -- exactly the "recorded view, never the moving tip" property BR-DAG-AMEND-R1-1 already
    requires for every OTHER form. An empty commit (never touching tracked content) stands in for "another agent
    commits to the shared orchestration branch between this compile's own resolution and this one lookup"."""
    import subprocess

    from govbridge.core import view as viewmod

    def _git(root, *args):
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"git {args} failed: {r.stderr}")
        return r

    resolved_view = viewmod.resolve_view(viewmod.load_view(view_path), repo=str(fixture_repo.root))
    original_commit = resolved_view.named["records"].commit

    _git(fixture_repo.root, "commit", "--allow-empty", "-q", "-m", "simulated concurrent commit (BR-DAG-AMEND-R1-23)")
    moved_commit = _git(fixture_repo.root, "rev-parse", "HEAD").stdout.strip()
    assert moved_commit != original_commit

    task_spec = _task_spec(view_path, [
        {"id": "FX-0002", "reason": "test", "required_status": "ACTIVE"},
    ])
    result = resolver.resolve(task_spec, repo=str(fixture_repo.root),
                               registry_path="tests/fixtures/authority/fixture-authority-registry.yaml",
                               resolved_view=resolved_view)
    assert result.status == "OK", result.blocked_reasons
    item = result.items[0]
    assert item.id == "FX-0002"
    assert item.commit == original_commit, (
        f"id-form item {item.id!r} carries commit {item.commit!r}, not the pinned view's own {original_commit!r}"
        f" -- resolve() re-resolved the records ref live instead of reusing the resolved_view it was given"
    )
