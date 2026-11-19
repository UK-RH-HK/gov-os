"""The landing's after-step (W2-206; L2 section 2 step 8, section 3 A8): after the integration branch moved, the
integration store is refreshed at the new head and the structural pass runs once. It never refuses: each result is
a notice for ``queue.json``, a failure of one is ``ok: false`` with its reason, and neither stops the other.

1. ``gov rebuild --integration <branch>`` (``gov.rebuild.integration.refresh``, by its own code) where
   ``governance/project/rebuild.yaml`` names an ``integration_store``: ``{"ok", "head", "status"}``, or
   ``{"ok": False, "head", "reason"}``. Where it names none: ``"not_configured"``, and nothing runs.
2. ``gov check --structural <base>`` (``gov.check.structural.run_structural``) with the landing's base, each check
   bounded by the pass's own default: ``{"ok", "exit", "lines"}``, with ``reason`` where it could not run.
"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path

NOT_CONFIGURED = "not_configured"
REASON_MAX = 600


def _reason(error: BaseException) -> str:
    code, message = getattr(error, "code", None), getattr(error, "message", None)
    text = f"{code}: {message}" if code and message else f"{type(error).__name__}: {error}"
    return " ".join(text.split())[:REASON_MAX]


def rebuild(root: Path, branch: str):
    """The integration store's refresh at ``branch``'s head, in ``root``; its notice."""
    from gov.launch import store
    from gov.rebuild import integration

    try:
        if store.configured(Path(root)) is None:
            return NOT_CONFIGURED
    except Exception as error:  # noqa: BLE001 - a setting that cannot be used is a notice
        return {"ok": False, "head": None, "reason": _reason(error)}
    said = io.StringIO()
    try:
        with contextlib.redirect_stderr(said):  # the refresh's dated lines: not the landing's answer
            done = integration.refresh(Path(root), branch)
    except Exception as error:  # noqa: BLE001 - never refuses: the landing stands
        details = getattr(error, "details", None)
        head = details.get("head") if isinstance(details, dict) else None
        return {"ok": False, "head": head, "reason": _reason(error)}
    summary = done.get("integration") if isinstance(done, dict) else None
    summary = summary if isinstance(summary, dict) else {}
    return {"ok": True, "head": summary.get("head"), "status": summary.get("status")}


def structural(tree: Path, base: str) -> dict:
    """The structural pass on ``tree`` with ``base``; its notice."""
    from gov.check import structural as _structural

    out, said, code = io.StringIO(), io.StringIO(), None
    notice: dict = {}
    try:
        with contextlib.redirect_stderr(said):
            code = _structural.run_structural(Path(tree), base, _structural.DEFAULT_TIMEOUT, out)
    except Exception as error:  # noqa: BLE001 - never refuses: the landing stands
        notice["reason"] = _reason(error)
    else:
        if code != 0:
            notice["reason"] = " ".join(said.getvalue().split())[:REASON_MAX] or f"the structural pass ended {code}"
    return {"ok": code == 0, "exit": code, "lines": out.getvalue().splitlines(), **notice}


def run(root: Path, branch: str, base: str, tree: Path) -> dict:
    """Both steps, the rebuild first: ``{"rebuild", "structural"}``. ``root``: where the rebuild's settings are
    read and the branch is known; ``tree``: the work tree at the landed head, for the structural pass."""
    return {"rebuild": rebuild(root, branch), "structural": structural(tree, base)}
