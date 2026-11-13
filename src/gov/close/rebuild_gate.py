"""The rebuild's semantic-store gate (W2-124; DEC-1027 C, DEC-1015 item 4): a rebuild whose semantic store was asked for
and not recreated is failed, never ok.

``semantic_failure`` is the rule of the CTO's ``rebuild_semantic_check.py`` (the merge queue's ``rebuild_slot.sh``): the
store's status is not ``recreated`` and it was not declared not asked for (``requested: false``: ``--no-embeddings``,
or a project with nothing to embed); an absent semantic entry is a failure. ``check`` raises the ``REBUILD_FAILED`` that
``gov rebuild`` (and so the close's rebuild and the queue's prepare) answers with.
"""

from __future__ import annotations

from gov.cli.errors import GovError


def semantic_failure(result: dict) -> str | None:
    """Why the semantic store, where it was asked for, is not recreated; None where it is, or was not asked for.
    ``result`` is a ``gov rebuild --json`` envelope (``{"result": {...}}``) or its result (``{"stores": {...}}``)."""
    body = result.get("result") if isinstance(result, dict) and "stores" not in result else result
    stores = body.get("stores") if isinstance(body, dict) else None
    semantic = (stores.get("semantic") if isinstance(stores, dict) else None) or {}
    if not isinstance(semantic, dict):
        semantic = {}
    if semantic.get("status") == "recreated" or semantic.get("requested", True) is False:
        return None
    return f"semantic store {semantic.get('status', 'absent')}: {semantic.get('reason', 'no reason given')}"


def check(result: dict) -> None:
    """Raise ``REBUILD_FAILED`` (``store: semantic``, the reason, the stores) where ``semantic_failure`` finds one."""
    why = semantic_failure(result)
    if why is None:
        return
    body = result.get("result") if "stores" not in result else result
    stores = (body or {}).get("stores") or {}
    reason = (stores.get("semantic") or {}).get("reason", "no reason given")
    raise GovError("REBUILD_FAILED",
                   f"rebuild failed on the semantic store, which was asked for and not recreated (store: semantic): "
                   f"{why}", {"store": "semantic", "reason": reason, "stores": stores})
