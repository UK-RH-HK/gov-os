"""Structured current-state lookup on the fixture repo: value + provenance (path, commit, blob, key_path, lines),
seal status (SEAL_OK/SEAL_MISMATCH/UNSEALED), and the last-changed commit/date."""
import hashlib

from govbridge.authority import state


def test_unsealed_state_file(fixture_repo, view_path):
    result = state.get("bridge", "running_work", repo=str(fixture_repo.root), view_path=view_path)
    assert result.value == {"status": "fixture value"}
    assert result.path == "release/orchestration/phase-2-context-bridge/ORCHESTRATOR_STATE.yaml"
    assert result.seal_status == "UNSEALED"
    assert result.recorded_state_hash is None
    assert result.last_changed_commit is not None


def test_key_path_with_list_index(fixture_repo, view_path):
    result = state.get("bridge", "mandatory_bridge_inputs.items[0]", repo=str(fixture_repo.root),
                        view_path=view_path)
    assert result.value["id"] == "FX-0010A"
    assert result.line_start <= result.line_end


def test_canonical_hash_matches_check_state_rule():
    text = "state_hash: abc123\nfoo: bar\n"
    # the rule: sha256 of the text with the state_hash line blanked to null
    expected = hashlib.sha256(b"state_hash: null\nfoo: bar\n").hexdigest()
    assert state.canonical_hash(text) == expected


def test_seal_ok_and_mismatch(tmp_path):
    body = "foo: bar\nbaz: qux\n"
    good_hash = state.canonical_hash("state_hash: null\n" + body)
    sealed_text = f"state_hash: {good_hash}\n" + body
    assert state.canonical_hash(sealed_text) == good_hash

    tampered = sealed_text.replace("qux", "TAMPERED")
    assert state.canonical_hash(tampered) != good_hash
