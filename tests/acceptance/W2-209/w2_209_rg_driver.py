"""One call of the code under test, in a child process of its own (W2-209 fix tests; the driver of
``w2_209_driver`` with the stand-ins of ``w2_209_rg_standins``, which add to the base ones). Not collected as a test."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_209_rg_standins as standins  # noqa: E402

MARK = "W2-209-OUTCOME: "


def _value(value):
    if isinstance(value, dict) and set(value) == {"path"}:
        return Path(value["path"])
    if isinstance(value, dict) and "standin" in value:
        return standins.make(value)
    if isinstance(value, list):
        return [_value(item) for item in value]
    return value


def _out(data):
    sys.stdout.write("\n" + MARK + json.dumps(data, default=str) + "\n")
    sys.stdout.flush()


def main():
    spec = json.loads(sys.stdin.read())
    module_name, _, name = spec["call"].partition(":")
    try:
        target = getattr(importlib.import_module(module_name), name)
    except (ImportError, AttributeError) as exc:
        _out({"kind": "missing", "error": {"type": type(exc).__name__, "message": f"{spec['call']}: {exc}"}})
        return 0
    args = [_value(a) for a in spec.get("args", [])]
    kwargs = {key: _value(v) for key, v in (spec.get("kwargs") or {}).items()}
    try:
        result = target(*args, **kwargs)
    except BaseException as exc:  # noqa: BLE001 - every outcome is reported, a SystemExit included
        _out({"kind": "raised", "error": {"type": type(exc).__name__, "code": getattr(exc, "code", None),
                                          "message": str(getattr(exc, "message", exc)),
                                          "details": getattr(exc, "details", None),
                                          "reason": getattr(exc, "reason", None)}})
        return 0
    if isinstance(result, Path):
        result = str(result)
    elif isinstance(result, tuple):
        result = [str(r) if isinstance(r, Path) else r for r in result]
    _out({"kind": "returned", "result": result})
    return 0


if __name__ == "__main__":
    sys.exit(main())
