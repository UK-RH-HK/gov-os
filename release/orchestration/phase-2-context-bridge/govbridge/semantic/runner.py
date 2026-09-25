"""Invoke a gov-capability/1 ``embed`` plugin as a subprocess and translate its response into Python values or a
typed ``EmbedError`` (ARCHITECTURE.md section 9: "the bridge invokes plugins directly, as subprocesses"). Generic
over which plugin: the default is this node's own ONNX adapter, but a test may point it at
``capabilities/python/govos_capabilities/embedder_hashed_ngram.py`` (read-only, used only as a protocol-conformance
and DIMENSION_MISMATCH test double, never as a substitute embedder -- SEMANTIC_ROUTE.md section 5.5) or at any
other ``embed`` plugin, without this module knowing which.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

PROTOCOL = "gov-capability/1"

DEFAULT_ADAPTER = str(Path(__file__).resolve().parent / "adapters" / "onnx_embed.py")


class EmbedError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def embed(texts: list, mode: str = "passage", dimensions: Optional[int] = None, pin_id: Optional[str] = None,
          adapter_path: str = DEFAULT_ADAPTER, extra_args: Optional[list] = None,
          python: Optional[str] = None, timeout: float = 600.0, cwd: Optional[str] = None,
          extra_pythonpath: Optional[str] = None, expect_dim: Optional[int] = None) -> dict:
    """Run one request/response round trip against ``adapter_path``. Returns the ``outputs`` dict on success;
    raises ``EmbedError`` (with ``.code`` set to the plugin's typed error code) on any ok:false response, a
    protocol violation in the reply, a non-zero exit, or a timeout (``TIMEOUT``, this module's own code -- the
    plugin protocol has no such code because a plugin that hangs never gets to answer).

    ``dimensions``, if given, is sent to the plugin as the PROTOCOL.md ``inputs.dimensions`` hint. ``expect_dim``
    (defaults to ``dimensions`` when omitted) is enforced by THIS caller regardless of what the plugin claims --
    see the comment below on why that is a separate, caller-side check."""
    if expect_dim is None:
        expect_dim = dimensions
    python = python or sys.executable
    req = {"protocol": PROTOCOL, "capability": "embed", "request_id": None,
           "inputs": {"texts": texts, "mode": mode}}
    if dimensions is not None:
        req["inputs"]["dimensions"] = dimensions
    if pin_id is not None:
        req["inputs"]["pin_id"] = pin_id
    cmd = [python, adapter_path] + list(extra_args or [])
    env = None
    if extra_pythonpath:
        env = dict(os.environ)
        env["PYTHONPATH"] = extra_pythonpath + os.pathsep + env.get("PYTHONPATH", "")
    try:
        proc = subprocess.run(cmd, input=json.dumps(req).encode("utf-8"), capture_output=True, timeout=timeout,
                               cwd=cwd, env=env)
    except subprocess.TimeoutExpired as exc:
        raise EmbedError("TIMEOUT", f"{adapter_path} did not answer within {timeout}s: {exc}") from exc
    if proc.returncode != 0:
        raise EmbedError("PLUGIN_ERROR",
                          f"{adapter_path} exited {proc.returncode}: {proc.stderr.decode(errors='replace')[:2000]}")
    try:
        resp = json.loads(proc.stdout.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise EmbedError("PLUGIN_ERROR", f"{adapter_path} produced non-JSON stdout: {exc}") from exc
    if resp.get("protocol") != PROTOCOL:
        raise EmbedError("PROTOCOL_MISMATCH", f"{adapter_path} answered with protocol {resp.get('protocol')!r}")
    if not resp.get("ok"):
        err = resp.get("error") or {}
        raise EmbedError(err.get("code", "PLUGIN_ERROR"), err.get("message", "no message"))
    outputs = resp["outputs"]
    # Enforced here, not just trusted from the plugin's own ``ok`` claim: some embed plugins accept whatever
    # ``dimensions`` they are asked for (the hashed-ngram reference plugin does, by design -- it has no native
    # dimensionality) rather than reporting their OWN dimension and letting the caller compare. A caller that
    # cares which pin is active must still fail closed if the answer's dim disagrees with what it asked for.
    if expect_dim is not None and outputs.get("dim") != expect_dim:
        raise EmbedError("DIMENSION_MISMATCH",
                          f"{adapter_path} answered dim={outputs.get('dim')}, caller pinned {expect_dim}")
    return outputs
