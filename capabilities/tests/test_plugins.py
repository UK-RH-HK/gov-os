"""pytest coverage for the Python capability plugins (gov-capability/1)."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(HERE, "..", "python")


def run(module: str, req: dict) -> dict:
    out = subprocess.run([sys.executable, "-m", module], input=json.dumps(req), capture_output=True, text=True, cwd=PY, env={**os.environ, "PYTHONPATH": PY})
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_embed_plugin_deterministic_and_normalised():
    req = {"protocol": "gov-capability/1", "capability": "embed", "inputs": {"texts": ["hello world", "hello world"], "dimensions": 32}}
    r = run("govos_capabilities.embedder_hashed_ngram", req)
    assert r["ok"] and r["provider"]["id"] == "hashed-ngram-python"
    v = r["outputs"]["vectors"]
    assert v[0] == v[1] and len(v[0]) == 32
    assert abs(sum(x * x for x in v[0]) - 1.0) < 1e-4


def test_protocol_mismatch_is_reported_not_crashed():
    r = run("govos_capabilities.embedder_hashed_ngram", {"protocol": "other/9", "capability": "embed", "inputs": {}})
    assert r["ok"] is False and r["error"]["code"] == "PROTOCOL_MISMATCH"
    r2 = run("govos_capabilities.embedder_hashed_ngram", {"protocol": "gov-capability/1", "capability": "rerank", "inputs": {}})
    assert r2["ok"] is False and r2["error"]["code"] == "CAPABILITY_MISMATCH"


def test_code_intel_python_ast():
    src = "import os\nfrom pkg.mod import thing\n\nclass A:\n    def f(self):\n        return os.getcwd()\n\ndef g(x):\n    return thing(x)\n"
    r = run("govos_capabilities.code_intel_python_ast", {"protocol": "gov-capability/1", "capability": "code_intel", "inputs": {"path": "a.py", "language": "python", "source": src}})
    assert r["ok"] and r["provider"]["id"] == "python-ast"
    o = r["outputs"]
    names = {(s["qualname"], s["kind"]) for s in o["symbols"]}
    assert ("A", "class") in names and ("A.f", "method") in names and ("g", "function") in names
    assert "os" in o["imports"] and "pkg.mod" in o["imports"]
    assert any(c["from"] == "A.f" and c["name"] == "getcwd" for c in o["calls"])
    assert [c["qualname"] for c in o["chunks"]][:1] == ["__module__"]


def test_code_intel_syntax_error_is_reported():
    r = run("govos_capabilities.code_intel_python_ast", {"protocol": "gov-capability/1", "capability": "code_intel", "inputs": {"path": "b.py", "language": "python", "source": "def (:\n"}})
    assert r["ok"] and r["outputs"]["ok_parse"] is False and r["outputs"]["symbols"] == []
