"""W1-06 — every DEC-074 pin is in the registry, with its sha256.

KPI success 2: "The Superpowers v6.4.2 source is available for vendoring; every
DEC-074 pin is recorded in governance/project/tool-registry.yaml with sha256"
[CAP-25.a].

The pins are those of ADR-0002 §2, "Stack (DEC-074, Balanced) — exact pins".
``PINS`` below holds the rows of that table that state both one exact version
and a sha256: the tests ask for exactly what the table states. The table
abbreviates most digests (``ca136f0e…32e797c6``); the registry must hold the
full digest, which begins and ends as the table says.

Rows of the table without a sha256 are not pins of this ticket (DEC-195), but
for gitleaks 8.30.1, which ``test_w1_06_digests.py`` tests. Where the
Superpowers source must be (DEC-194) is tested in ``test_w1_06_vendor.py``.

DEC-191: PyYAML 6.0.1 "is recorded in the tool registry when W1-06 creates it".
"""

from __future__ import annotations

import pytest

import w1_06_support as support

# (names accepted for the entry, pinned version, how the sha256 begins, how it ends) — ADR-0002 §2
PINS = {
    "openspec": (("openspec",), "1.13.2", "ca136f0e", "32e797c6"),
    "check-jsonschema": (("check-jsonschema",), "0.38.2", "9341d731", "12aedd34"),
    "ticket": (("ticket", "wedow/ticket", "tk"), "0.3.2",
               "408f2c113ecc3bc071507593a78386f1b4cc743be6491c9e9f2627efd4d9902b", ""),
    "codebase-memory-mcp": (("codebase-memory-mcp",), "0.11.0", "a831cdca", "4e3302a6"),
    "ollama": (("ollama",), "0.35.0", "0b0650a9", "34c4f8"),
    "rulesync": (("rulesync",), "24.0.0", "64e8ad32", "3297c71"),
    "copier": (("copier",), "9.18.2", "2343959a", "16a98ac3"),
    "lefthook": (("lefthook",), "2.1.15", "df981b47", "32e8fe3"),
    "uv": (("uv",), "0.12.21", "e8a4e7b4", "478eb2076"),
    "node": (("node", "nodejs", "node.js"), "22.23.3", "fde6a4bf", "5e348f48"),
}


@pytest.mark.parametrize("pin", sorted(PINS))
def test_a_dec_074_pin_is_recorded_at_its_pinned_version(registry, pin):
    names, version, _, _ = PINS[pin]
    entry = support.one(registry, names)
    found = support.norm_version(entry.get("version", ""))
    assert found == version, f"the registry records {pin} at {found!r}; ADR-0002 §2 pins {version!r}"


@pytest.mark.parametrize("pin", sorted(PINS))
def test_a_dec_074_pin_is_recorded_with_the_sha256_of_the_stack_table(registry, pin):
    names, _, begins, ends = PINS[pin]
    entry = support.one(registry, names)
    digest = str(entry.get("sha256", "")).strip().lower()
    assert support.SHA256.fullmatch(digest), f"the {pin} entry's sha256 is not a SHA-256 digest: {digest!r}"
    assert digest.startswith(begins) and digest.endswith(ends), (
        f"the {pin} entry's sha256 is {digest}; ADR-0002 §2 gives {begins}…{ends}"
    )


def test_superpowers_is_recorded_at_v6_4_2(registry):
    entry = support.one(registry, ("superpowers",))
    found = support.norm_version(entry.get("version", ""))
    assert found == "6.4.2", f"the registry records Superpowers at {found!r}; the pin is v6.4.2"


def test_superpowers_is_recorded_with_a_sha256_digest(registry):
    digest = str(support.one(registry, ("superpowers",)).get("sha256", "")).strip()
    assert support.SHA256.fullmatch(digest), f"the Superpowers entry's sha256 is not a SHA-256 digest: {digest!r}"


def test_pyyaml_is_recorded_at_6_0_1(registry):
    """DEC-191."""
    entry = support.one(registry, ("pyyaml",))
    found = support.norm_version(entry.get("version", ""))
    assert found == "6.0.1", f"the registry records PyYAML at {found!r}; DEC-191 records 6.0.1"
