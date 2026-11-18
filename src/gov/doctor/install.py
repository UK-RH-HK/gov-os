"""``gov doctor``'s section ``install`` (W2-18, DAEO-057v; CAP-43, W2-H021): the gov a product runs is its pin.

- No pin (``<common>/gov/pin.json`` absent): ``unmeasured``, naming ``gov install <version>``.
- A pin: fails, naming its ``case``, in this order:
  - ``editable``: the pin's gov is an editable install (``direct_url.json`` says ``dir_info.editable``), or the
    environment holds no installed distribution of gov, or the doctor runs from the pin and imported a gov that is not
    the environment's installed one. An editable install of a source tree is ``editable`` (the ticket lead's call);
  - ``source_tree``: the gov running doctor was imported from a source tree's ``src/gov``; the reason names the path;
  - ``session``: the gov running doctor is neither the pin's nor a source tree's: another installed gov, named;
  - ``lock``: the pin's version or wheel sha256 differs from the release ``governance/framework.lock`` records (its
    ``release.version``, and the wheel sha256 of the manifest the lock holds), or the lock records no release.
- Passes (``version``, ``environment``) when the doctor runs from the pin and the pin matches the lock.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import os
import sys
from pathlib import Path

from gov.install import probe
from gov.install.locate import common_dir, pin_root


def _inside(path: Path, folder: Path) -> bool:
    try:
        Path(os.path.realpath(path)).relative_to(os.path.realpath(folder))
        return True
    except ValueError:
        return False


def _locked(root: Path) -> tuple[str | None, str | None, str | None]:
    """``(version, wheel sha256, why not)`` of the release the project's lock records."""
    from gov import lock
    data = lock._read_map(root / lock.LOCK_REL)
    if data is None:
        return None, None, f"{lock.LOCK_REL} is absent or not a readable map: it records no release"
    entry = data.get("release")
    if not isinstance(entry, dict):
        return None, None, f"{lock.LOCK_REL} records no release"
    try:
        manifest_bytes = base64.b64decode(entry.get("manifest"), validate=True)
        manifest = json.loads(manifest_bytes)
    except (TypeError, ValueError, binascii.Error):
        return None, None, f"the release manifest in {lock.LOCK_REL} cannot be read"
    if hashlib.sha256(manifest_bytes).hexdigest() != entry.get("manifest_sha256"):
        return None, None, f"the release manifest in {lock.LOCK_REL} does not hash to its manifest_sha256"
    wheel = manifest.get("wheel") if isinstance(manifest, dict) else None
    sha = wheel.get("sha256") if isinstance(wheel, dict) else None
    return entry.get("version"), sha, None


def check(root, prefix: str | None = None, package=None) -> dict:
    """The section for the project at ``root``; ``prefix`` and ``package`` are the running gov's (``sys.prefix`` and
    its imported ``gov`` folder by default)."""
    root = Path(root)
    common = common_dir(root)
    record_path = pin_root(common) / "pin.json" if common is not None else None
    if record_path is None or not os.path.lexists(record_path):
        return {"status": "unmeasured", "reason": "no pinned gov in this repository (<git common dir>/gov/pin.json): "
                                                  "run `gov install <version>` to pin the release framework.lock names"}
    if prefix is None:
        prefix = sys.prefix
    if package is None:
        import gov
        package = Path(gov.__file__).resolve().parent
    package = Path(os.path.realpath(package))
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
        env = Path(record["environment"])
        version, wheel_sha = record.get("version"), (record.get("wheel") or {}).get("sha256")
    except (OSError, UnicodeDecodeError, ValueError, KeyError, TypeError, AttributeError):
        return {"status": "fail", "case": "lock", "reason": f"{record_path} cannot be read: the pin is not known"}
    from_pin = os.path.realpath(prefix) == os.path.realpath(env)
    dist = probe.distribution(env)
    if dist is None:
        return {"status": "fail", "case": "editable",
                "reason": f"the pin's environment {env} holds no installed distribution of gov"}
    if dist["editable"]:
        return {"status": "fail", "case": "editable",
                "reason": f"the pin's gov in {env} is an editable install ({dist['url']}), not the release's wheel"}
    if from_pin and not _inside(package, dist["site"]):
        return {"status": "fail", "case": "editable",
                "reason": f"the pin's python imports gov from {package}, which no distribution installed in {env} "
                          "holds"}
    if probe.source_tree(package):
        return {"status": "fail", "case": "source_tree",
                "reason": f"the gov running doctor is imported from a source tree: {package}; a product runs its "
                          f"pinned gov ({record_path.parent / 'bin' / 'gov'})"}
    if not from_pin:
        return {"status": "fail", "case": "session",
                "reason": f"the gov running doctor ({package}, environment {prefix}) is not the pin's ({env})"}
    locked_version, locked_sha, why = _locked(root)
    if why:
        return {"status": "fail", "case": "lock", "reason": why}
    if version != locked_version or wheel_sha != locked_sha:
        return {"status": "fail", "case": "lock",
                "reason": f"the pin is release {version} with wheel sha256 {wheel_sha}; framework.lock records release "
                          f"{locked_version} with wheel sha256 {locked_sha}"}
    return {"status": "pass", "version": version, "environment": str(env)}
