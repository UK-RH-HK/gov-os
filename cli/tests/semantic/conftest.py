import os
import sys
from pathlib import Path

import pytest

FIXTURES_CORE = Path(__file__).resolve().parents[1] / "fixtures" / "core"
sys.path.insert(0, str(FIXTURES_CORE))
import repobuilder  # noqa: E402

import govbridge.semantic  # noqa: E402,F401 -- import side effect: registers the "semantic"/"vector" layer,
# process-globally, for every test in this directory (see test_freshness_layer.py's module docstring for why a
# bare freshness.run() in this whole pytest process now also runs the "semantic" builder).
from govbridge.core import freshness, store  # noqa: E402
from govbridge.semantic import modelpin  # noqa: E402

DOMAIN = Path(__file__).resolve().parents[2]
REAL_PIN_PATH = str(DOMAIN / "config" / "model-pin.yaml")
REAL_EMBED_PROFILE_PATH = str(DOMAIN / "config" / "embed-profile.yaml")
ADAPTER_PATH = str(DOMAIN / "govbridge" / "semantic" / "adapters" / "onnx_embed.py")
HASHED_NGRAM_PATH = str(
    DOMAIN.parents[2] / "capabilities" / "python" / "govos_capabilities" / "embedder_hashed_ngram.py"
)


@pytest.fixture(autouse=True)
def _no_env_leak(monkeypatch):
    # every test controls GOVBRIDGE_STORE / GOV_BRIDGE_HOME explicitly; never inherit the developer's real cache,
    # and never let a test accidentally write into the isolation store this run uses for its own checkpoint.
    monkeypatch.delenv("GOVBRIDGE_STORE", raising=False)


@pytest.fixture
def fixture_repo(tmp_path):
    return repobuilder.build(tmp_path / "repo")


@pytest.fixture
def rules_path():
    return str(FIXTURES_CORE / "fixture-corpus-rules.yaml")


def write_canonical_view_with_layers(path: Path, repo, view_id: str = "fixture-view-semantic") -> None:
    """Like tests/core/conftest.py's write_canonical_view, but with the per-ref ``layers:`` field node B4's
    profile.eligible_ref_names reads: every named ref admits "semantic"; the history glob does not -- mirroring
    the real config/canonical-view.yaml's own shape exactly (records/product/evidence carry "semantic", history
    does not)."""
    path.write_text(f"""\
schema: govbridge-canonical-view/1
view_id: {view_id}
refs:
  - name: records
    ref: refs/heads/records
    follow: tip
    role: primary
    layers: [exact, lexical, records, graph, semantic]
  - name: product
    ref: refs/heads/product
    follow: pinned
    pinned_commit: {repo.product_pin}
    role: product
    layers: [exact, lexical, records, graph, semantic]
  - name: evidence
    ref: refs/heads/evidence
    follow: pinned
    pinned_commit: {repo.evidence_pin}
    role: evidence
    layers: [exact, lexical, records, graph, semantic]
  - name: history
    ref_glob: refs/heads/history/*
    follow: tip
    role: history
    layers: [exact, lexical, records, graph]
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


@pytest.fixture
def view_path(tmp_path, fixture_repo):
    p = tmp_path / "canonical-view.yaml"
    write_canonical_view_with_layers(p, fixture_repo)
    return str(p)


@pytest.fixture
def embed_profile_path():
    """The real, committed config/embed-profile.yaml -- exercised as-is, not a fixture copy, so a test failure
    here means the shipped profile is wrong, not a fixture drift."""
    return REAL_EMBED_PROFILE_PATH


@pytest.fixture
def real_model_pin_path():
    return REAL_PIN_PATH


@pytest.fixture
def adapter_path():
    return ADAPTER_PATH


@pytest.fixture
def real_model_dir():
    """The shared, read-only model cache B1's bootstrap already populated. Tests only ever READ from here
    (sha256 verification, loading the ONNX session); a tamper/unavailable scenario always uses a private tmp
    copy (``tamper_model_dir`` / ``missing_model_dir`` below), never this directory."""
    from govbridge.semantic import modelpin

    pin = modelpin.load_model_pin(REAL_PIN_PATH)
    d = modelpin.model_dir(pin, modelpin.default_models_root())
    if not d.is_dir():
        pytest.skip(f"shared model cache not present at {d} (B1 bootstrap not run in this environment)")
    return d


@pytest.fixture
def tamper_model_dir(tmp_path, real_model_dir):
    """A private copy of the model directory (symlinks for every artefact, mirroring
    config/model-pin.yaml's own declared paths exactly, except one small file this fixture corrupts with a real
    copy) -- proves PIN_MISMATCH without ever touching the shared cache another parallel builder may be reading
    at the same time."""
    from govbridge.semantic import modelpin

    pin = modelpin.load_model_pin(REAL_PIN_PATH)
    dest = tmp_path / "tampered-model"
    dest.mkdir()
    tamper_target = pin.artefacts[-1]  # the smallest/least-consequential-to-copy artefact
    for a in pin.artefacts:
        (dest / a.path).parent.mkdir(parents=True, exist_ok=True)
        src = real_model_dir / a.path
        if a is tamper_target:
            (dest / a.path).write_bytes(src.read_bytes() + b"\n// tampered by tests/semantic\n")
        else:
            os.symlink(src, dest / a.path)
    return dest


@pytest.fixture
def missing_model_dir(tmp_path):
    """A model directory that simply does not exist -- MODEL_UNAVAILABLE, functionally equivalent to "the model
    dir moved aside" (the node acceptance check's phrasing) without ever moving the SHARED cache another parallel
    builder may depend on."""
    return tmp_path / "no-such-model-dir"


@pytest.fixture
def built(monkeypatch, tmp_path, fixture_repo, rules_path, view_path, real_model_dir):
    """A from-clean build (core + semantic together, see conftest module docstring) against a hermetic fixture
    repo, in an isolated GOVBRIDGE_STORE. GOV_BRIDGE_HOME is deliberately left at its real default (not
    redirected into tmp_path, unlike tests/core's own fixtures): govbridge.semantic.modelpin resolves the model
    cache from GOV_BRIDGE_HOME too, and that shared, read-only cache is not something a test can populate for
    itself. Telemetry rows this build writes therefore land in the real, shared
    $HOME/.cache/gov-bridge/telemetry/*.jsonl -- an append-only sink other processes write to as well by design
    (ARCHITECTURE.md section 8.3), never read back except by this file's own assertions filtering for rows it
    just wrote. Returns (result, conn, pin_id)."""
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    result = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(fixture_repo.root))
    assert result["trigger"] == "FULL"
    conn = store.open_db()
    pin = modelpin.load_model_pin(modelpin.default_pin_path())
    pin_id = modelpin.compute_pin_id(pin)
    return result, conn, pin_id


@pytest.fixture
def hashed_ngram_adapter():
    """(path, extra_pythonpath) for capabilities/python/govos_capabilities/embedder_hashed_ngram.py, read-only.
    Its ``main()`` does ``from govos_capabilities.plugin import run``, a package-relative import that needs
    ``capabilities/python`` on ``sys.path`` -- its own descriptor documents this as ``cwd: capabilities/python``
    for a ``-m`` invocation; runner.embed() uses a direct file path instead, so the equivalent here is putting
    that same directory on PYTHONPATH. Used only as a protocol-conformance/DIMENSION_MISMATCH test double
    (SEMANTIC_ROUTE.md section 5.5), never as a substitute embedder."""
    if not Path(HASHED_NGRAM_PATH).is_file():
        pytest.skip(f"hashed-ngram double not found at {HASHED_NGRAM_PATH}")
    return HASHED_NGRAM_PATH, str(Path(HASHED_NGRAM_PATH).resolve().parents[1])
