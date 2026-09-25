#!/usr/bin/env bash
# Pinned bootstrap (SEMANTIC_ROUTE.md section 5.1). Idempotent, writes nothing into Git:
#   1. create/reuse $GOV_BRIDGE_HOME/venv and install config/requirements.lock with --require-hashes --no-deps;
#   2. download config/model-pin.yaml's artefacts into $GOV_BRIDGE_HOME/models/<model>/<revision>/..., verifying
#      each sha256; an artefact ALREADY on disk is re-verified every run -- a mismatch (corruption or tampering)
#      stops the script immediately and nothing further is downloaded; only a MISSING artefact is fetched;
#   3. print one identity line: python version, onnxruntime, tokenizers, tree-sitter and the model pin id.
#
# After this runs once, the venv and model cache are READ-ONLY in use (orchestrator amendment BR-DAG-AMEND-1): no
# later builder installs into them.
set -euo pipefail

DOMAIN="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GOV_BRIDGE_HOME="${GOV_BRIDGE_HOME:-$HOME/.cache/gov-bridge}"
VENV="$GOV_BRIDGE_HOME/venv"
MODELS="$GOV_BRIDGE_HOME/models"
REQ_LOCK="$DOMAIN/config/requirements.lock"
MODEL_PIN="$DOMAIN/config/model-pin.yaml"
STAMP="$VENV/.govbridge-requirements-sha256"

log() { echo "[bootstrap] $*" >&2; }

mkdir -p "$GOV_BRIDGE_HOME" "$MODELS"

# --- 1. venv -------------------------------------------------------------------------------------------------
REQ_SHA="$(sha256sum "$REQ_LOCK" | cut -d' ' -f1)"

if [ -x "$VENV/bin/python" ] && [ -f "$STAMP" ] && [ "$(cat "$STAMP")" = "$REQ_SHA" ]; then
  log "venv at $VENV already matches requirements.lock ($REQ_SHA); skipping install"
else
  log "creating/refreshing venv at $VENV"
  python3 -m venv "$VENV"
  "$VENV/bin/python" -m pip install --upgrade pip --quiet
  "$VENV/bin/python" -m pip install --require-hashes --no-deps -r "$REQ_LOCK"
  echo "$REQ_SHA" > "$STAMP"
fi

PY="$VENV/bin/python"

# --- 2. model artefacts ---------------------------------------------------------------------------------------
"$PY" - "$MODEL_PIN" "$MODELS" <<'PYEOF'
import hashlib
import os
import sys
import urllib.request

import yaml

model_pin_path, models_root = sys.argv[1], sys.argv[2]
with open(model_pin_path, "r", encoding="utf-8") as fh:
    pin = yaml.safe_load(fh)

model = pin["model"]
model_id, revision = model["id"], model["revision"]
slug = model_id.replace("/", "-")
dest_dir = os.path.join(models_root, slug, revision)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


for art in model["artefacts"]:
    remote_path = art["path"]
    expected = art["sha256"]
    dest = os.path.join(dest_dir, remote_path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)

    if os.path.exists(dest):
        got = sha256_of(dest)
        if got != expected:
            print(f"[bootstrap] SHA256 MISMATCH for cached artefact {remote_path}: "
                  f"expected {expected}, got {got} -- refusing to continue (tampered or corrupt cache)",
                  file=sys.stderr)
            sys.exit(1)
        print(f"[bootstrap] model artefact present and verified: {remote_path}")
        continue

    url = pin["download"]["url_template"].format(model_id=model_id, revision=revision, path=remote_path)
    print(f"[bootstrap] downloading {url}")
    tmp = dest + ".part"
    urllib.request.urlretrieve(url, tmp)
    got = sha256_of(tmp)
    if got != expected:
        os.replace(tmp, dest + ".TAMPERED-DOWNLOAD")
        print(f"[bootstrap] SHA256 MISMATCH for downloaded {remote_path}: expected {expected}, got {got} -- "
              f"stopping; nothing further will be downloaded", file=sys.stderr)
        sys.exit(1)
    os.replace(tmp, dest)
    print(f"[bootstrap] verified {remote_path} sha256={got}")
PYEOF

# --- 3. identity line ------------------------------------------------------------------------------------------
"$PY" - "$MODEL_PIN" <<'PYEOF'
import hashlib
import importlib.metadata
import json
import platform
import sys

import yaml

with open(sys.argv[1], "r", encoding="utf-8") as fh:
    pin = yaml.safe_load(fh)
model = pin["model"]
runtime = pin["runtime"]

ort_version = importlib.metadata.version("onnxruntime")
tok_version = importlib.metadata.version("tokenizers")
ts_version = importlib.metadata.version("tree-sitter")

parts = [
    model["id"], model["revision"],
    *sorted(a["sha256"] for a in model["artefacts"]),
    ort_version, tok_version,
    json.dumps(runtime["session"], sort_keys=True),
    model["pooling"], model["query_prefix"],
]
pin_id = hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()

py_ver = platform.python_version()
print(f"python {py_ver}, onnxruntime {ort_version}, tokenizers {tok_version}, tree-sitter {ts_version} "
      f"and the pin id {pin_id}")
PYEOF
