"""``gov release``: build an immutable, hash-pinned release (W2-16, CAP-43.b lite, DEC-722).

``gov release <version>`` writes the record under ``docs/releases/<version>/`` and nothing else: the owner
commits it and tags the release commit (agents never tag; nothing is signed). ``gov release --lock-from
<template>`` is the template's Copier task: it verifies the installed release and writes the project's
``governance/framework.lock`` (W2-M175: the task needs ``gov``, not a ``python3`` that imports it).

The build form is the owner's alone, in person from a plain terminal (DEC-772), with the freeze lift's checks
(DEC-409): no Claude Code session among the ancestor processes, read whole from ``/proc``; neither ``GOV_ROLE`` nor
``GOV_TICKET`` set, to any value; a terminal on input and output; and a one-time code typed back. Each refusal comes
before anything is read or written. Nothing outside the process reaches those checks: ``run`` calls
``release(root, version)``.

The lock task runs inside ``copier copy`` and ``copier update``, so it keeps its caller rule (DEC-761): the caller is
``GOV_ROLE`` (DEC-365), unset (the owner) or ``orchestrator``; every other value, the empty one among them, is
refused before anything is read or written.
"""

from __future__ import annotations

import os
import random
from pathlib import Path

HELP = "build the release <version> under docs/releases/ (the owner only, from a plain terminal; the owner tags it)"
CLASS = "act"
ACT_PATHS = ("docs/releases/**", "governance/framework.lock")
ORCHESTRATOR = "orchestrator"
CODE_PREFIX = "RELEASE-"
_REASONS = {
    "session": "a Claude Code session is among the ancestor processes",
    "ancestry": "the ancestor processes cannot be read up to the system's first process, so the caller is not "
                "known to be the owner in person",
    "role": "GOV_ROLE is set (to any value, the empty one among them)",
    "ticket": "GOV_TICKET is set (to any value, the empty one among them)",
    "terminal": "its input and its output are not both a terminal",
    "code": "the code typed back is not the code shown, and the next run shows a new code",
}


def add_arguments(parser) -> None:
    parser.add_argument("version", nargs="?", metavar="<version>", help="the semantic version of the release")
    parser.add_argument("--lock-from", metavar="<template>",
                        help="the template's Copier task: verify the installed release and write framework.lock")


def _refused(reason: str):
    from gov.cli.errors import GovError

    return GovError("RELEASE_REFUSED", f"gov release is refused: {_REASONS[reason]}. Only the owner builds a "
                    "release, in person from a plain terminal outside any Claude Code session, with neither GOV_ROLE "
                    "nor GOV_TICKET set (DEC-772): nothing is built", {"reason": reason})


def _release_test(root: Path, version: str | None, ancestry: list[dict] | None = None,
                  terminal: tuple[int, int] | None = None) -> dict:
    """Test seam for ``release``: accepts a planted ``ancestry`` and ``terminal``, as ``gov.pause.command._lift_test``.

    Production code never calls this directly: ``release(root, version)`` does, with no extras, so ``/proc`` is read
    and the terminal is ``(0, 1)``. Both descriptors are asked ``os.isatty`` whatever is passed. ``GOV_ROLE`` and
    ``GOV_TICKET`` are read from the process environment. The code comes from the system's random source and goes to
    the terminal only, after every other check has passed; one line is read, once. Anything that cannot be read or
    asked refuses.
    """
    from gov.cli.errors import GovError
    from gov.lock import LockError
    from gov.pause.command import _caller_refusal, read_ancestry
    from gov.release import ReleaseError, build

    try:
        refusal = _caller_refusal(read_ancestry() if ancestry is None else ancestry)
    except Exception:  # a chain that cannot be read is not the owner's
        refusal = ("ancestry", "")
    if refusal:
        raise _refused("session" if refusal[0] == "session" else "ancestry")
    if "GOV_ROLE" in os.environ:
        raise _refused("role")
    if "GOV_TICKET" in os.environ:
        raise _refused("ticket")
    try:
        source, shown = terminal or (0, 1)
        interactive = os.isatty(source) and os.isatty(shown)
    except Exception:  # a descriptor that cannot be asked is no terminal
        interactive = False
    if not interactive:
        raise _refused("terminal")
    code, typed = f"{CODE_PREFIX}{random.SystemRandom().randrange(10000):04d}", b""
    try:
        os.write(shown, f"type {code} to build release {version or '<no version given>'}: ".encode())
    except OSError:
        raise _refused("terminal") from None
    try:
        while b"\n" not in typed and len(typed) < 64:
            chunk = os.read(source, 64)
            if not chunk:
                break
            typed += chunk
    except OSError:  # the input ended: no code was typed back
        typed = b""
    if typed.split(b"\n", 1)[0].decode("utf-8", "replace").strip() != code:
        raise _refused("code")
    if version is None:  # P-R3-A: the build's own refusal, once the caller is known to be the owner
        raise GovError("RELEASE_REFUSED", "no release built: no version given: gov release <version>")
    try:
        folder = build(root, version)
    except (ReleaseError, LockError) as exc:
        raise GovError("RELEASE_REFUSED", f"no release built: {exc}") from None
    return {"version": version, "record": str(folder)}


def release(root: Path, version: str | None) -> dict:
    """Build release ``version`` as the owner in person (DEC-772): always reads the ancestry from ``/proc`` and uses
    the terminal ``(0, 1)``. It takes no planted ``ancestry`` or ``terminal``: an agent cannot pass the checks by it.
    """
    return _release_test(root, version)


def run(root: Path, args, config: dict) -> dict:
    from gov.cli.errors import GovError
    from gov.lock import LockError
    from gov.release import ReleaseError, lock_from

    if args.lock_from is None:
        return release(root, args.version)  # DEC-772: nothing from outside the process fills its other parameters
    role = os.environ.get("GOV_ROLE")  # DEC-365: the caller; unset, the owner
    if role is not None and role != ORCHESTRATOR:
        raise GovError("RELEASE_REFUSED", f"gov release is refused for GOV_ROLE={role!r}: only the orchestrator "
                       "(GOV_ROLE=orchestrator) or the owner (GOV_ROLE unset, a plain terminal) may release",
                       {"caller": role})
    try:
        if args.version is not None:
            raise ReleaseError("--lock-from takes no version: the project's answers name the release")
        path, version = lock_from(root, Path(args.lock_from))
    except (ReleaseError, LockError) as exc:
        raise GovError("RELEASE_REFUSED", f"framework.lock not written: {exc}") from None
    return {"lock": str(path), "release": version}
