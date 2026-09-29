import pytest

from govbridge.semantic import modelpin


def test_load_real_pin_and_compute_pin_id_is_deterministic(real_model_pin_path):
    pin1 = modelpin.load_model_pin(real_model_pin_path)
    pin2 = modelpin.load_model_pin(real_model_pin_path)
    assert pin1.model_id == "BAAI/bge-small-en-v1.5"
    assert pin1.dimensions == 384
    assert len(pin1.artefacts) == 6
    id1 = modelpin.compute_pin_id(pin1)
    id2 = modelpin.compute_pin_id(pin2)
    assert id1 == id2
    assert len(id1) == 64  # hex sha256


def test_pin_id_changes_if_any_artefact_sha256_changes(real_model_pin_path):
    pin = modelpin.load_model_pin(real_model_pin_path)
    base = modelpin.compute_pin_id(pin)
    tampered = modelpin.ModelPin(
        model_id=pin.model_id, revision=pin.revision, licence=pin.licence,
        artefacts=(modelpin.Artefact(path=pin.artefacts[0].path, sha256="0" * 64,
                                      local_name=pin.artefacts[0].local_name),) + pin.artefacts[1:],
        dimensions=pin.dimensions, pooling=pin.pooling, normalize=pin.normalize, max_tokens=pin.max_tokens,
        query_prefix=pin.query_prefix, runtime=pin.runtime, raw=pin.raw,
    )
    assert modelpin.compute_pin_id(tampered) != base


def test_resolve_and_verify_against_the_shared_cache_succeeds(real_model_pin_path, real_model_dir):
    pin = modelpin.load_model_pin(real_model_pin_path)
    resolved = modelpin.resolve_and_verify(pin, modelpin.default_models_root())
    assert resolved == real_model_dir


def test_resolve_and_verify_model_unavailable_when_dir_missing(real_model_pin_path, missing_model_dir):
    pin = modelpin.load_model_pin(real_model_pin_path)
    with pytest.raises(modelpin.ModelUnavailable):
        modelpin.resolve_and_verify(pin, modelpin.default_models_root(), override_dir=str(missing_model_dir))


def test_resolve_and_verify_pin_mismatch_when_an_artefact_is_tampered(real_model_pin_path, tamper_model_dir):
    pin = modelpin.load_model_pin(real_model_pin_path)
    with pytest.raises(modelpin.PinMismatch):
        modelpin.resolve_and_verify(pin, modelpin.default_models_root(), override_dir=str(tamper_model_dir))


def test_resolve_and_verify_never_writes_to_the_shared_cache(real_model_pin_path, real_model_dir):
    before = {p: p.stat().st_mtime_ns for p in real_model_dir.rglob("*") if p.is_file()}
    pin = modelpin.load_model_pin(real_model_pin_path)
    modelpin.resolve_and_verify(pin, modelpin.default_models_root())
    after = {p: p.stat().st_mtime_ns for p in real_model_dir.rglob("*") if p.is_file()}
    assert before == after
