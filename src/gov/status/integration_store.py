"""``gov status``'s ``integration_store`` part (W2-116 pass 2b, S2; P-W2-116-S2-INTERFACE Q1 (a), DEC-1157 (12)): the
store ``gov rebuild --integration`` keeps, its head and age, and whether it is stale.

``{link, half, head, branch, branch_head, built_at, age_seconds, stale, stale_reason, last_refresh}``:

- ``link`` the configured ``integration_store``; ``half`` the folder it points at; ``head`` that half's HEAD;
  ``branch`` and ``branch_head`` ``integration_refresh.branch`` and its commit in the project; ``built_at`` the
  ``written_at`` of the half's warm-base record (W2-122, ``gov.rebuild.seed.RECORD_REL``); ``age_seconds`` ``now`` (the
  clock of ``gov.rebuild.integration``, ``GOV_NOW`` honoured) less it; ``last_refresh`` ``<link>.refresh.json``.
- **Stale** where the store's head is not the branch's (``behind_branch``) or it was built before the last time a
  refresh fell due (``built_before_due``, ``gov.rebuild.integration.last_due``); ``stale_reason`` is the reasons that
  hold, each starting with its code, joined by ``"; "``.
- No ``integration_store`` configured, no link, or a link that leads to no folder: the part is
  ``{"read": false, "reason": ...}``. Where ``integration_refresh`` is missing or invalid, ``branch``, ``branch_head``,
  ``stale`` and ``stale_reason`` are each ``{"read": false, "reason": ...}`` naming the key and the rest is given. A
  figure that cannot be read is never replaced by an answer: ``stale`` is not ``false`` while a reason it could hold
  has not been read. The part never raises.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path


def _unread(reason: str) -> dict:
    return {"read": False, "reason": reason}


def _tried(read, *args):
    """What ``read`` gives; the reason it did not, as an unread entry."""
    try:
        return read(*args)
    except Exception as error:  # noqa: BLE001 - whatever stopped it is the reason, never a default answer
        return _unread(getattr(error, "message", None) or f"{type(error).__name__}: {error}")


def _ok(value) -> bool:
    return not (isinstance(value, dict) and value.get("read") is False)


def _head_of(folder: Path) -> str:
    from gov.rebuild.integration import _head

    head = _head(folder)
    if head is None:
        raise LookupError(f"{folder} has no HEAD commit that can be read")
    return head


def _branch_head(root: Path, branch: str) -> str:
    from gov.rebuild.integration import _git

    done = _git(root, "rev-parse", "--verify", "-q", f"{branch}^{{commit}}", check=False)
    if done.returncode != 0 or not done.stdout.strip():
        raise LookupError(f"the branch {branch!r} is not known in {root}")
    return done.stdout.strip()


def _built_at(half: Path) -> datetime:
    from gov.rebuild.seed import RECORD_REL

    path = half / RECORD_REL
    try:
        written = json.loads(path.read_text(encoding="utf-8")).get("written_at")
        return datetime.fromisoformat(written).astimezone()
    except (OSError, ValueError, AttributeError, TypeError):
        raise LookupError(f"{path} holds no written_at that can be read: the build's time is not known") from None


def _reasons(branch, branch_head, head, built, settings, verdicts, when) -> tuple[list[str], list[str]]:
    """The stale reasons that hold, and what could not be read to judge the others."""
    from gov.rebuild.integration import last_due

    holds, unknown = [], []
    if not _ok(branch_head) or not _ok(head):
        unknown.append("behind_branch: " + (branch_head if not _ok(branch_head) else head)["reason"])
    elif head != branch_head:
        holds.append(f"behind_branch: the store's head {head[:12]} is not the branch {branch}'s head "
                     f"{branch_head[:12]}")
    if not _ok(built) or not _ok(verdicts) or not _ok(when):
        unknown.append("built_before_due: " + next(x for x in (built, verdicts, when) if not _ok(x))["reason"])
    else:
        due = last_due(settings, when, verdicts)
        if due is not None and built < due[0]:
            holds.append(f"built_before_due: built at {built.isoformat()}, before a refresh fell due at "
                         f"{due[0].isoformat()} ({due[1]})")
    return holds, unknown


def read(root: Path) -> dict:
    """The part for the project at ``root`` (module docstring)."""
    from gov.launch.store import StoreSettingError, configured
    from gov.rebuild import integration

    root = Path(root)
    try:
        value = configured(root)
    except StoreSettingError as error:
        return _unread(f"{error}")
    if value is None:
        return _unread("governance/project/rebuild.yaml names no integration_store: there is no integration store")
    link = Path(value)
    if not os.path.lexists(link):
        return _unread(f"there is no link at {link}: no refresh has built the integration store")
    half = Path(os.path.realpath(link))
    if not half.is_dir():
        return _unread(f"the link {link} leads to {half}, which is no folder")

    settings = _tried(integration.refresh_settings, root)
    when = _tried(integration.now)
    head = _tried(_head_of, half)
    built = _tried(_built_at, half)
    part = {"link": str(link), "half": str(half), "head": head,
            "built_at": built.isoformat() if _ok(built) else built}
    if _ok(built) and _ok(when):
        part["age_seconds"] = int((when - built).total_seconds())
    else:
        part["age_seconds"] = _unread("; ".join(x["reason"] for x in (built, when) if not _ok(x)))
    part["last_refresh"] = integration.read_record(link)
    if not _ok(settings):
        why = f"integration_refresh: {settings['reason']}"
        return {**part, "branch": _unread(why), "branch_head": _unread(why), "stale": _unread(why),
                "stale_reason": _unread(why)}
    branch_head = _tried(_branch_head, root, settings.branch)
    verdicts = _tried(integration.verdict_times, root, settings.verdict)
    holds, unknown = _reasons(settings.branch, branch_head, head, built, settings, verdicts, when)
    part |= {"branch": settings.branch, "branch_head": branch_head}
    if holds:
        part |= {"stale": True, "stale_reason": "; ".join(holds)}
    elif unknown:
        why = "; ".join(unknown)
        part |= {"stale": _unread(why), "stale_reason": _unread(why)}
    else:
        part |= {"stale": False, "stale_reason": None}
    return part
