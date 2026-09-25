import json
import subprocess
import sys

import pytest

from govbridge.semantic import modelpin, runner


def _raw(adapter_path: str, payload: dict) -> dict:
    proc = subprocess.run([sys.executable, adapter_path], input=json.dumps(payload).encode("utf-8"),
                           capture_output=True, timeout=60)
    assert proc.returncode == 0, proc.stderr.decode(errors="replace")
    return json.loads(proc.stdout.decode("utf-8"))


def test_protocol_mismatch(adapter_path):
    resp = _raw(adapter_path, {"protocol": "not-gov-capability/1", "capability": "embed", "inputs": {"texts": ["x"]}})
    assert resp["ok"] is False
    assert resp["error"]["code"] == "PROTOCOL_MISMATCH"


def test_capability_mismatch(adapter_path):
    resp = _raw(adapter_path, {"protocol": "gov-capability/1", "capability": "rerank", "inputs": {"texts": ["x"]}})
    assert resp["ok"] is False
    assert resp["error"]["code"] == "CAPABILITY_MISMATCH"


def test_bad_request_on_invalid_json(adapter_path):
    proc = subprocess.run([sys.executable, adapter_path], input=b"{not json", capture_output=True, timeout=60)
    resp = json.loads(proc.stdout.decode("utf-8"))
    assert resp["ok"] is False
    assert resp["error"]["code"] == "BAD_REQUEST"


def test_model_unavailable_with_model_dir_moved_aside(adapter_path, missing_model_dir):
    with pytest.raises(runner.EmbedError) as ei:
        runner.embed(["hello"], adapter_path=adapter_path, extra_args=["--model-dir", str(missing_model_dir)])
    assert ei.value.code == "MODEL_UNAVAILABLE"


def test_pin_mismatch_when_the_model_dir_is_tampered(adapter_path, tamper_model_dir):
    with pytest.raises(runner.EmbedError) as ei:
        runner.embed(["hello"], adapter_path=adapter_path, extra_args=["--model-dir", str(tamper_model_dir)])
    assert ei.value.code == "PIN_MISMATCH"


def test_pin_mismatch_on_a_caller_asserted_wrong_pin_id(adapter_path, real_model_dir):
    with pytest.raises(runner.EmbedError) as ei:
        runner.embed(["hello"], adapter_path=adapter_path, pin_id="not-the-real-pin-id")
    assert ei.value.code == "PIN_MISMATCH"


def test_dimension_mismatch_against_the_real_model(adapter_path, real_model_dir):
    with pytest.raises(runner.EmbedError) as ei:
        runner.embed(["hello"], adapter_path=adapter_path, dimensions=999)
    assert ei.value.code == "DIMENSION_MISMATCH"


def test_dimension_mismatch_via_hashed_ngram_test_double(hashed_ngram_adapter):
    """SEMANTIC_ROUTE.md/node-B4 acceptance: 'the hashed-ngram plugin used only as a test double'. It has no
    native dimensionality (it happily produces whatever `inputs.dimensions` asks for, defaulting to 512 when
    unspecified) -- so here the request deliberately omits `dimensions` and lets ``expect_dim`` enforce the pin's
    required 384 on the CALLER side (runner.embed), proving that check is generic across any embed plugin, not
    specific to the ONNX adapter."""
    path, pythonpath = hashed_ngram_adapter
    with pytest.raises(runner.EmbedError) as ei:
        runner.embed(["hello", "world"], adapter_path=path, extra_pythonpath=pythonpath, expect_dim=384)
    assert ei.value.code == "DIMENSION_MISMATCH"


def test_hashed_ngram_double_itself_is_protocol_conformant(hashed_ngram_adapter):
    path, pythonpath = hashed_ngram_adapter
    outputs = runner.embed(["hello", "world"], adapter_path=path, extra_pythonpath=pythonpath,
                            dimensions=384, expect_dim=384)
    assert outputs["dim"] == 384
    assert len(outputs["vectors"]) == 2


def test_successful_passage_embedding_real_model(adapter_path, real_model_dir):
    outputs = runner.embed(["a governance decision"], mode="passage", adapter_path=adapter_path, dimensions=384)
    assert outputs["dim"] == 384
    assert len(outputs["vectors"]) == 1
    vec = outputs["vectors"][0]
    assert len(vec) == 384
    norm = sum(x * x for x in vec) ** 0.5
    assert abs(norm - 1.0) < 1e-3  # L2-normalised (SEMANTIC_ROUTE.md section 2)
    pin = modelpin.load_model_pin(modelpin.default_pin_path())
    assert outputs["pin_id"] == modelpin.compute_pin_id(pin)


def test_successful_query_embedding_real_model(adapter_path, real_model_dir):
    outputs = runner.embed(["how is a checkpoint made mandatory"], mode="query", adapter_path=adapter_path,
                            dimensions=384)
    assert outputs["dim"] == 384
    assert len(outputs["vectors"][0]) == 384


def test_unknown_mode_is_bad_request(adapter_path, real_model_dir):
    with pytest.raises(runner.EmbedError) as ei:
        runner.embed(["x"], mode="not-a-real-mode", adapter_path=adapter_path)
    assert ei.value.code == "BAD_REQUEST"
