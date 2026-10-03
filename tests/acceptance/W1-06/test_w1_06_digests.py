"""W1-06 — gitleaks 8.30.1 is a pin, and a single-file tool's sha256 is its binary's.

DEC-195 (DP-1): the ten pins of ADR-0002 §2 stay as ``test_w1_06_pins.py`` has
them, and "gitleaks 8.30.1 is added now (already installed; W1-15 uses it),
with the sha256 of its binary".

DEC-196 (DP-2): "``sha256`` covers the one downloaded artefact (npm tarball,
release tarball, distribution package), or the binary itself for a single-file
tool."

A digest is recomputed only where that needs no network and no install: the
single-file binaries that are on this machine. Those cases are ``local_only``;
they hash a file that is already there and fail, not skip, when it is absent.
For every other entry the form of the digest stays asserted
(``test_w1_06_registry.py``, ``test_w1_06_pins.py``, ``test_w1_06_ccusage.py``).
"""

from __future__ import annotations

import re
import shutil
import subprocess

import pytest

import w1_06_support as support

GITLEAKS = ("gitleaks",)

# pin -> (names accepted for the entry, the command on PATH or the path under the home directory)
SINGLE_FILE = {
    "gitleaks": (GITLEAKS, "gitleaks"),
    "ticket": (("ticket", "wedow/ticket", "tk"), "tk"),
    "codebase-memory-mcp": (("codebase-memory-mcp",), "codebase-memory-mcp"),
    "rulesync": (("rulesync",), "rulesync"),
    "lefthook": (("lefthook",), "lefthook"),
    "uv": (("uv",), "uv"),
    # ADR-0002 §2: "the nvm default stays v18.20.8", so Node 22 is not the `node` on PATH
    "node": (("node", "nodejs", "node.js"), support.NODE_22_PREFIX / "bin" / "node"),
}


def _binary(where):
    """The file of a single-file tool on this machine; None when it is not there."""
    if isinstance(where, str):
        return shutil.which(where)
    return str(where) if where.is_file() else None


def test_gitleaks_is_recorded_at_8_30_1(registry):
    """DEC-195."""
    entry = support.one(registry, GITLEAKS)
    found = support.norm_version(entry.get("version", ""))
    assert found == "8.30.1", f"the registry records gitleaks at {found!r}; DEC-195 pins 8.30.1"


def test_gitleaks_is_recorded_with_a_sha256_digest(registry):
    """DEC-195: "with the sha256 of its binary"; which binary is checked by the ``local_only`` case below."""
    digest = str(support.one(registry, GITLEAKS).get("sha256", "")).strip()
    assert support.SHA256.fullmatch(digest), f"the gitleaks entry's sha256 is not a SHA-256 digest: {digest!r}"


@pytest.mark.local_only
@pytest.mark.parametrize("pin", sorted(SINGLE_FILE))
def test_a_single_file_tool_is_recorded_with_the_sha256_of_its_binary(registry, pin):
    """DEC-196: for a single-file tool the registry's sha256 is the binary's own."""
    names, where = SINGLE_FILE[pin]
    entry = support.one(registry, names)
    path = _binary(where)
    assert path is not None, f"{pin} is not on this machine ({where}): its recorded sha256 cannot be compared"
    recorded = str(entry.get("sha256", "")).strip().lower()
    found = support.file_sha256(path)
    assert recorded == found, f"the registry records sha256 {recorded} for {pin}; {path} has {found}"


@pytest.mark.local_only
def test_the_gitleaks_on_this_machine_is_the_pinned_version(registry):
    """DEC-195: "already installed". ``gitleaks version`` prints the version and touches nothing."""
    pinned = support.norm_version(support.one(registry, GITLEAKS).get("version", ""))
    path = shutil.which("gitleaks")
    assert path is not None, "there is no `gitleaks` on PATH: gitleaks is not installed on this machine"
    result = subprocess.run([path, "version"], capture_output=True, text=True, timeout=20, check=False)
    printed = (result.stdout + result.stderr).strip()
    versions = [support.norm_version(token) for token in re.findall(r"v?\d+(?:\.\d+)+", printed)]
    assert pinned in versions, f"{path} is gitleaks {printed!r}; the registry pins {pinned!r}"
