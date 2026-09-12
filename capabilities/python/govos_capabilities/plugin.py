"""Minimal gov-capability/1 plugin runner: read one JSON request on stdin, write one JSON response on stdout."""
from __future__ import annotations

import json
import sys
from typing import Callable

PROTOCOL = "gov-capability/1"


def run(capability: str, provider_id: str, provider_version: str, handler: Callable[[dict], dict]) -> int:
    raw = sys.stdin.read()
    try:
        req = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as e:
        _respond(False, provider_id, provider_version, error={"code": "BAD_REQUEST", "message": f"invalid JSON: {e}"})
        return 0
    if req.get("protocol") != PROTOCOL:
        _respond(False, provider_id, provider_version, error={"code": "PROTOCOL_MISMATCH", "message": f"expected {PROTOCOL}"})
        return 0
    if req.get("capability") != capability:
        _respond(False, provider_id, provider_version, error={"code": "CAPABILITY_MISMATCH", "message": f"this plugin provides {capability}"})
        return 0
    try:
        outputs = handler(req.get("inputs") or {})
    except Exception as e:  # noqa: BLE001 - plugin boundary: never crash the host
        _respond(False, provider_id, provider_version, error={"code": "PLUGIN_ERROR", "message": str(e)})
        return 0
    _respond(True, provider_id, provider_version, outputs=outputs, request_id=req.get("request_id"))
    return 0


def _respond(ok: bool, pid: str, pver: str, outputs: dict | None = None, error: dict | None = None, request_id=None) -> None:
    resp = {"protocol": PROTOCOL, "ok": ok, "provider": {"id": pid, "version": pver}, "request_id": request_id}
    if ok:
        resp["outputs"] = outputs or {}
    else:
        resp["error"] = error
    sys.stdout.write(json.dumps(resp))
    sys.stdout.flush()
