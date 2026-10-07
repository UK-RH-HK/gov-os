"""Round 7, KPI failure 1: an entry without a binary passes by a version
compared or a hash computed, never by a folder that exists (DEC-452).

DEC-452 (orchestrator, 2026-10-07, delegated from DEC-448):

  A tool passes only when the version read equals the pin, or, where no
  version can be read, when the file's hash equals the pinned hash; a
  tool for which neither can be established fails, with the reason.

DEC-425 (owner, 2026-10-06):

  A field that says "matched" when nothing was compared is a false
  record.

Predecessor analysis
--------------------
Round 6's ``test_w1_27_doctor_r6.py`` tests that a tool with no readable
version and a mismatched hash is not ``ok``, and that a version mismatch
fails.  Those cases all create fake binaries on PATH (binary tools).  No
case in rounds 1–6 tests the six entries that have no binary
(``NO_BINARY_TOOLS``: superpowers, pyyaml, sqlite-vec, qwen3-embedding,
reranker-venv, reranker).  The current code passes every one of them as
soon as a folder exists (or a module imports), with ``sha256_match: true``
and no hash computed, and with no version comparison for pyyaml.

The six kinds of no-binary entry in the registry
-------------------------------------------------
1. **Vendored folder in the project** (superpowers): ``sha256`` is the
   DEC-199 digest of the committed files under
   ``template/governance/kernel/vendor/superpowers/``.
2. **Python package with readable version** (pyyaml): ``sha256`` is of
   the distribution package (``.deb``), which is not on the machine.
3. **Model blob under the home** (qwen3-embedding): ``sha256`` is of the
   model blob file under ``~/.ollama/models``.
4. **Extension file under the home** (sqlite-vec): ``sha256`` is of
   ``vec0.so`` under ``~/.local/lib/python3.12/site-packages/sqlite_vec``.
5. **Pip-freeze output** (reranker-venv): ``sha256`` is of the output of
   ``uv pip freeze`` for the venv at ``~/.local/share/gov-os/reranker-venv``.
6. **Model file under the home** (reranker): ``sha256`` is of
   ``model.safetensors`` under ``~/.cache/huggingface/hub/models--Qwen--Qwen3-Reranker-0.6B``.

Residual
--------
The four home-based tools (sqlite-vec, qwen3-embedding, reranker-venv,
reranker) can only be tested under the six real names because the code
dispatches on ``name in NO_BINARY_TOOLS``.  Their checks use
``_real_home()`` (``pwd.getpwuid``), which ignores the sandbox's HOME.
On this machine, where the real tools are installed, the code finds the
real installation and falsely says ``sha256_match: true``; on a clean
machine without these tools, the code falls to absent and the tests pass
(masking the bug).  After the fix (the code should use HOME or accept a
configurable home), the tests will reliably use fake content under the
sandbox home.  This is a generic-kernel residual: the command knows six
tool names of this repository.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

import w1_27_support as support


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _doctor_sections(envelope):
    """Extract doctor's full result dict."""
    if envelope.get("ok"):
        return envelope.get("result", {})
    return envelope.get("error", {}).get("details", {})


def _find_tool_entry(sections, tool_name):
    """Find a tool entry by name in the parsed doctor sections."""
    tools_section = sections.get("tools", {})
    entries = tools_section.get("tools", [])
    for entry in entries:
        if isinstance(entry, dict) and entry.get("name") == tool_name:
            return entry
    return None


def _folder_digest(files):
    """DEC-199 digest: sha256 of the sorted lines ``<sha256>  <path>\\n``."""
    lines = sorted(
        f"{hashlib.sha256(content).hexdigest()}  {rel}\n".encode("utf-8")
        for rel, content in files.items()
    )
    return hashlib.sha256(b"".join(lines)).hexdigest()


def _set_vendor_superpowers(project, files):
    """Replace the superpowers vendor folder with ``files`` and commit.

    Returns the DEC-199 digest of the folder.
    """
    vendor = (
        project / "template" / "governance" / "kernel"
        / "vendor" / "superpowers"
    )
    if vendor.exists():
        shutil.rmtree(vendor)
    for rel, content in files.items():
        path = vendor / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    support.commit_all(project, "set superpowers vendor folder")
    return _folder_digest(files)


def _remove_vendor_superpowers(project):
    """Remove the superpowers vendor folder entirely and commit."""
    vendor = (
        project / "template" / "governance" / "kernel"
        / "vendor" / "superpowers"
    )
    if vendor.exists():
        shutil.rmtree(vendor)
        support.commit_all(project, "remove superpowers vendor folder")


# --------------------------------------------------------------------------- #
# Fake vendor content for the superpowers tests.
# --------------------------------------------------------------------------- #

FAKE_VENDOR_FILES = {
    "LICENSE": b"MIT License\nCopyright (c) 2024 Test\n",
    "skills/test-skill/SKILL.md": (
        b"---\nname: test-skill\n---\nA test skill.\n"
    ),
}


# =========================================================================== #
# Part 1: Vendored folder hash (superpowers) — DEC-199, DEC-452, DEC-425
# =========================================================================== #

def test_vendored_folder_wrong_content_sha256_match_false(gov, project):
    """A vendored folder with content that produces a different digest than
    the pinned sha256: ``sha256_match`` is not true, and the entry is not
    ``ok`` (no version can be read for superpowers).

    DEC-452: a tool passes only when the version read equals the pin, or
    the file's hash equals the pinned hash.
    DEC-425: sha256_match must not be true when no hash was computed.
    DEC-199: the sha256 of a vendored folder is the digest of its
    committed files.

    RED: the current code says ``sha256_match: true, ok: true`` as soon
    as the vendor folder exists, without computing the DEC-199 digest.
    """
    actual_digest = _set_vendor_superpowers(project, FAKE_VENDOR_FILES)
    wrong_sha = "0" * 64
    assert wrong_sha != actual_digest

    registry = support.tool_entry_yaml(
        "superpowers", "v6.4.2", wrong_sha,
        install="echo install", uninstall="echo uninstall",
        date="2026-01-01", approved_by="test",
    )
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    envelope = run.envelope()
    sections = _doctor_sections(envelope)
    entry = _find_tool_entry(sections, "superpowers")

    assert entry is not None, (
        f"doctor has no entry for superpowers\n"
        f"tools section: {sections.get('tools', {})}\n{run.describe()}"
    )
    assert entry.get("sha256_match") is not True, (
        f"sha256_match is true but no hash was computed — the vendored "
        f"folder exists but its DEC-199 digest ({actual_digest}) does not "
        f"equal the pinned hash ({wrong_sha}); a field that says 'matched' "
        f"when nothing was compared is a false record (DEC-425)\n"
        f"entry: {entry}\n{run.describe()}"
    )
    assert entry.get("ok") is not True, (
        f"doctor passes for superpowers with a hash mismatch and no "
        f"readable version — DEC-452 says this is not ok\n"
        f"entry: {entry}\n{run.describe()}"
    )


def test_vendored_folder_wrong_content_has_reason(gov, project):
    """When the vendored folder's digest does not match the pin and no
    version is readable, the entry says what could not be verified.

    DEC-452: "a tool for which neither can be established fails, with
    the reason."

    RED: the current code gives no ``reason`` field; the folder's
    existence is enough for ``ok: true``.
    """
    _set_vendor_superpowers(project, FAKE_VENDOR_FILES)
    wrong_sha = "0" * 64

    registry = support.tool_entry_yaml(
        "superpowers", "v6.4.2", wrong_sha,
        install="echo install", uninstall="echo uninstall",
        date="2026-01-01", approved_by="test",
    )
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    envelope = run.envelope()
    sections = _doctor_sections(envelope)
    entry = _find_tool_entry(sections, "superpowers")

    assert entry is not None, (
        f"doctor has no entry for superpowers\n{run.describe()}"
    )
    reason = entry.get("reason", "")
    assert reason, (
        f"the entry for superpowers has no reason, but the vendor folder's "
        f"digest does not match the pin and no version can be read — "
        f"DEC-452 says the entry must say why it is not ok\n"
        f"entry: {entry}\n{run.describe()}"
    )


def test_vendored_folder_right_content_passes(gov, project):
    """A vendored folder whose DEC-199 digest equals the pinned sha256:
    ``sha256_match`` true, ``ok`` true.

    GREEN: the current code says ``sha256_match: true, ok: true``
    whenever the folder exists, so this case happens to pass.  After the
    fix the code computes the digest and gets the same answer.
    """
    correct_digest = _set_vendor_superpowers(project, FAKE_VENDOR_FILES)

    registry = support.tool_entry_yaml(
        "superpowers", "v6.4.2", correct_digest,
        install="echo install", uninstall="echo uninstall",
        date="2026-01-01", approved_by="test",
    )
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    envelope = run.envelope()
    sections = _doctor_sections(envelope)
    entry = _find_tool_entry(sections, "superpowers")

    assert entry is not None, (
        f"doctor has no entry for superpowers\n{run.describe()}"
    )
    assert entry.get("sha256_match") is True, (
        f"sha256_match should be true when the vendored folder's DEC-199 "
        f"digest equals the pinned hash ({correct_digest})\n"
        f"entry: {entry}\n{run.describe()}"
    )
    assert entry.get("ok") is True, (
        f"superpowers should be ok when its vendored folder's digest "
        f"matches the pin\n"
        f"entry: {entry}\n{run.describe()}"
    )


def test_vendored_folder_absent_not_ok(gov, project):
    """The superpowers vendor folder does not exist: not ``ok``.

    GREEN: the existing fallback correctly returns ``ok: false``.
    """
    _remove_vendor_superpowers(project)

    registry = support.tool_entry_yaml(
        "superpowers", "v6.4.2", "0" * 64,
        install="echo install", uninstall="echo uninstall",
        date="2026-01-01", approved_by="test",
    )
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    envelope = run.envelope()
    sections = _doctor_sections(envelope)
    entry = _find_tool_entry(sections, "superpowers")

    assert entry is not None, (
        f"doctor has no entry for superpowers\n{run.describe()}"
    )
    assert entry.get("ok") is not True, (
        f"doctor passes for superpowers when the vendor folder does not "
        f"exist\n"
        f"entry: {entry}\n{run.describe()}"
    )
    assert entry.get("sha256_match") is not True, (
        f"sha256_match should not be true when the vendor folder is "
        f"absent\n"
        f"entry: {entry}\n{run.describe()}"
    )


# =========================================================================== #
# Part 2: Version compared (pyyaml) — DEC-452
# =========================================================================== #

def test_python_package_wrong_version_not_ok(gov, project):
    """A Python-package entry whose module reports another version than
    the pin: not ``ok``, and the tools section does not pass.

    DEC-452: a tool is ``ok`` only when the version read equals the pin.

    RED: the current code reads ``yaml.__version__`` (6.0.1 on this
    machine) but returns ``ok: true`` without comparing it to the pin
    99.99.99.
    """
    registry = support.tool_entry_yaml(
        "pyyaml", "99.99.99", "0" * 64,
        install="echo install", uninstall="echo uninstall",
        date="2026-01-01", approved_by="test",
    )
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    envelope = run.envelope()
    sections = _doctor_sections(envelope)
    entry = _find_tool_entry(sections, "pyyaml")

    assert entry is not None, (
        f"doctor has no entry for pyyaml\n"
        f"tools section: {sections.get('tools', {})}\n{run.describe()}"
    )
    assert entry.get("ok") is not True, (
        f"doctor passes for pyyaml pinned at 99.99.99 when the module "
        f"reports {entry.get('found_version', '?')} — the version must be "
        f"compared (DEC-452)\n"
        f"entry: {entry}\n{run.describe()}"
    )

    tools_section = sections.get("tools", {})
    assert tools_section.get("status") != "pass", (
        f"the tools section passes despite a version mismatch for pyyaml\n"
        f"tools: {tools_section}\n{run.describe()}"
    )


def test_python_package_right_version_ok(gov, project):
    """A Python-package entry whose module reports the pinned version:
    ``ok`` true.

    GREEN: the current code says ``ok: true`` regardless, which is
    correct here because ``yaml.__version__`` is 6.0.1.
    """
    registry = support.tool_entry_yaml(
        "pyyaml", "6.0.1", "0" * 64,
        install="echo install", uninstall="echo uninstall",
        date="2026-01-01", approved_by="test",
    )
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    envelope = run.envelope()
    sections = _doctor_sections(envelope)
    entry = _find_tool_entry(sections, "pyyaml")

    assert entry is not None, (
        f"doctor has no entry for pyyaml\n{run.describe()}"
    )
    assert entry.get("ok") is True, (
        f"pyyaml reports version 6.0.1 and the pin is 6.0.1 — it should "
        f"be ok\n"
        f"entry: {entry}\n{run.describe()}"
    )


# =========================================================================== #
# Part 3: Distribution-package hash — sha256_match not true (DEC-425)
# =========================================================================== #

def test_distribution_package_sha256_match_not_true(gov, project):
    """An entry whose registered sha256 is the hash of a distribution
    package (not on the machine): it passes by its version only;
    ``sha256_match`` is not true.

    DEC-425: a field that says "matched" when nothing was compared is a
    false record.

    The pyyaml entry's note says its sha256 is "of the distribution
    package python3-yaml_6.0.1-2build2_amd64.deb, from the apt package
    index".  That package is not on the machine, so the hash cannot be
    reproduced.  With the right version, pyyaml should be ``ok`` (passes
    by version), but ``sha256_match`` must not be true.

    The expected value of ``sha256_match`` for a distribution-package
    hash is ``false`` or a value that says "not comparable" (e.g.
    ``"not_comparable"`` or ``"skipped"``); the assertion accepts any
    value that is not ``True``.

    RED: the current code says ``sha256_match: true`` without computing
    any hash.
    """
    registry = support.tool_entry_yaml(
        "pyyaml", "6.0.1",
        "315e59500af855f23ee4e95525b99009bd798c4d2658af8eb4b2d66a8a91ec23",
        install="echo install", uninstall="echo uninstall",
        date="2026-01-01", approved_by="test",
        note="sha256 of the distribution package",
    )
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    envelope = run.envelope()
    sections = _doctor_sections(envelope)
    entry = _find_tool_entry(sections, "pyyaml")

    assert entry is not None, (
        f"doctor has no entry for pyyaml\n{run.describe()}"
    )
    assert entry.get("ok") is True, (
        f"pyyaml at the right version (6.0.1) should be ok — it passes "
        f"by version when the hash is of a distribution package\n"
        f"entry: {entry}\n{run.describe()}"
    )
    assert entry.get("sha256_match") is not True, (
        f"sha256_match is true but the registered hash is of a "
        f"distribution package (.deb) that is not on this machine — "
        f"no hash was computed, so sha256_match must not be true "
        f"(DEC-425)\n"
        f"entry: {entry}\n{run.describe()}"
    )


# =========================================================================== #
# Part 4: File under the home with wrong sha256 — DEC-452, DEC-425
#
# Each of the four home-based tools is registered with a wrong sha256.
# Fake content is placed under the sandbox home (where the code should
# look after the fix).  See the module docstring's Residual section for
# why these are machine-dependent.
# =========================================================================== #

HOME_TOOLS = [
    pytest.param(
        "sqlite-vec",
        "0.1.9",
        lambda home: (
            home / ".local" / "lib" / "python3.12"
            / "site-packages" / "sqlite_vec"
        ),
        id="sqlite-vec",
    ),
    pytest.param(
        "qwen3-embedding",
        "0.6b",
        lambda home: home / ".ollama" / "models",
        id="qwen3-embedding",
    ),
    pytest.param(
        "reranker-venv",
        "sentence-transformers 6.1.0, torch 2.14.1+cu130, "
        "transformers 5.18.0, huggingface-hub 1.33.0",
        lambda home: (
            home / ".local" / "share" / "gov-os" / "reranker-venv"
        ),
        id="reranker-venv",
    ),
    pytest.param(
        "reranker",
        "Qwen/Qwen3-Reranker-0.6B@e61197ed45024b0ed8a2d74b80b4d909f1255473",
        lambda home: (
            home / ".cache" / "huggingface" / "hub"
            / "models--Qwen--Qwen3-Reranker-0.6B"
        ),
        id="reranker",
    ),
]


@pytest.mark.parametrize("name,version,home_path_fn", HOME_TOOLS)
def test_home_tool_wrong_sha256_not_ok(
    gov, project, sandbox, name, version, home_path_fn,
):
    """An entry for a tool under the home with a wrong sha256:
    ``sha256_match`` is not true and ``ok`` is not true (no version can
    be read for any of these tools, and the hash does not match).

    Fake content is placed under the sandbox home at the path the code
    should check.  On this machine, the code uses ``_real_home()`` and
    finds the real installation, falsely reporting ``sha256_match: true``;
    on a clean machine, absent → ``sha256_match: false`` (the assertion
    passes, masking the bug).

    DEC-452: a tool passes only when the version read equals the pin, or
    the file's hash equals the pinned hash.
    DEC-425: sha256_match must not be true when no hash was computed.

    RED on this machine (the real tool is installed under the real home).
    """
    fake_dir = home_path_fn(sandbox.home)
    fake_dir.mkdir(parents=True, exist_ok=True)
    (fake_dir / "placeholder").write_text(
        "fake content for testing\n", encoding="utf-8",
    )

    wrong_sha = "0" * 64
    registry = support.tool_entry_yaml(
        name, version, wrong_sha,
        install="echo install", uninstall="echo uninstall",
        date="2026-01-01", approved_by="test",
    )
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    envelope = run.envelope()
    sections = _doctor_sections(envelope)
    entry = _find_tool_entry(sections, name)

    assert entry is not None, (
        f"doctor has no entry for {name}\n"
        f"tools section: {sections.get('tools', {})}\n{run.describe()}"
    )
    assert entry.get("sha256_match") is not True, (
        f"sha256_match is true for {name} with a wrong pin ({wrong_sha}) "
        f"— no hash was computed, so sha256_match must not be true "
        f"(DEC-425)\n"
        f"entry: {entry}\n{run.describe()}"
    )
