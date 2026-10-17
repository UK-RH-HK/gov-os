"""``gov release``: build an immutable, hash-pinned release (W2-16, CAP-43.b lite, DEC-722).

``gov release <version>`` writes the record under ``docs/releases/<version>/`` and nothing else: the owner
commits it and tags the release commit (agents never tag; nothing is signed). ``gov release --lock-from
<template>`` is the template's Copier task: it verifies the installed release and writes the project's
``governance/framework.lock`` (W2-M175: the task needs ``gov``, not a ``python3`` that imports it).

Both forms run only for the orchestrator or the owner (DEC-761). The caller is ``GOV_ROLE`` (DEC-365): the
orchestrator is ``GOV_ROLE=orchestrator``, the owner is ``GOV_ROLE`` unset (a plain terminal); every other value,
the empty one among them, is refused before anything is read or written.
"""

from __future__ import annotations

import os
from pathlib import Path

HELP = "build the release <version> under docs/releases/ (the owner tags it)"
CLASS = "act"
ACT_PATHS = ("docs/releases/**", "governance/framework.lock")
ORCHESTRATOR = "orchestrator"


def add_arguments(parser) -> None:
    parser.add_argument("version", nargs="?", metavar="<version>", help="the semantic version of the release")
    parser.add_argument("--lock-from", metavar="<template>",
                        help="the template's Copier task: verify the installed release and write framework.lock")


def run(root: Path, args, config: dict) -> dict:
    from gov.cli.errors import GovError
    from gov.lock import LockError
    from gov.release import ReleaseError, build, lock_from

    role = os.environ.get("GOV_ROLE")  # DEC-365: the caller; unset, the owner
    if role is not None and role != ORCHESTRATOR:
        raise GovError("RELEASE_REFUSED", f"gov release is refused for GOV_ROLE={role!r}: only the orchestrator "
                       "(GOV_ROLE=orchestrator) or the owner (GOV_ROLE unset, a plain terminal) may release",
                       {"caller": role})
    try:
        if args.lock_from is not None:
            if args.version is not None:
                raise ReleaseError("--lock-from takes no version: the project's answers name the release")
            path, version = lock_from(root, Path(args.lock_from))
            return {"lock": str(path), "release": version}
        if args.version is None:
            raise ReleaseError("no version given: gov release <version>")
        folder = build(root, args.version)
    except (ReleaseError, LockError) as exc:
        raise GovError("RELEASE_REFUSED", f"framework.lock not written: {exc}" if args.lock_from is not None
                       else f"no release built: {exc}") from None
    return {"version": args.version, "record": str(folder)}
