"""The integration store a launched session searches (W2-116 S3; DEC-963, DEC-983, DEC-1087 (3)).

- **The place** is the absolute path ``integration_store`` of the project's ``governance/project/rebuild.yaml`` (W2-122's
  key): a link to the ready half of the store ``gov rebuild --integration <branch>`` keeps (``gov.rebuild.integration``).
- **The session's variable** ``ENV`` (``GOV_STORE``) is set by ``gov launch`` in every worker session's env to that path,
  the link itself and never the half it points to, so each search follows the link at the time it runs.
- **What reads it:** a plain ``gov retrieve`` (no ``--root``) answers from the folder ``ENV`` names, never from the
  working tree it runs in, so a session's retrieval never reads a ticket worktree's store. With the variable set and
  nothing at that place, the search answers ``STORE_MISSING`` for that place: it never falls back to the working tree.
"""

from __future__ import annotations

import os
from pathlib import Path

ENV = "GOV_STORE"
KEY = "integration_store"
SETTINGS_REL = "governance/project/rebuild.yaml"


class StoreSettingError(ValueError):
    """``integration_store`` is set but cannot be used; the message names why."""


def configured(root: Path) -> str | None:
    """The configured place of the integration store, as written (an absolute path); None where the project's
    ``rebuild.yaml`` is absent or names no ``integration_store``. ``StoreSettingError`` where the file cannot be read as
    a map or the value is not an absolute path: never a guess."""
    from gov.cli.errors import GovError
    from gov.config.loader import read_yaml

    path = Path(root) / SETTINGS_REL
    if not path.is_file():
        return None
    try:
        document = read_yaml(path, "STORE_SETTING_INVALID", SETTINGS_REL)
    except (GovError, OSError) as error:
        raise StoreSettingError(f"{SETTINGS_REL} cannot be read: {getattr(error, 'message', error)}") from None
    if document is None:
        return None
    if not isinstance(document, dict):
        raise StoreSettingError(f"{SETTINGS_REL} is not a map")
    if KEY not in document:
        return None
    value = document[KEY]
    if not isinstance(value, str) or not os.path.isabs(value):
        raise StoreSettingError(f"{SETTINGS_REL}: {KEY} must be an absolute path, not {value!r}")
    return value


def session_root(value: str | None) -> Path | None:
    """The folder a plain search answers from, from the session's ``ENV`` value; None where it is unset or empty.
    ``StoreSettingError`` where it is not an absolute path."""
    if not value:
        return None
    if not os.path.isabs(value):
        raise StoreSettingError(f"{ENV} must be an absolute path, not {value!r}")
    return Path(value)
