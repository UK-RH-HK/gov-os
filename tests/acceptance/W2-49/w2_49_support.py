"""Shared readers for the W2-49 acceptance tests (Contract v4.2, lite; DEC-722).

The tests read public documents only: the CIT-P and CIT-E records under
``docs/changes/``, the two Contract files under ``docs/contract/`` and the
capability records under ``docs/contract/capabilities/`` (DEC-741 K).  Every
path is found from this file's own location, so the suite reads the files of
the tree it sits in (DEC-732), never the main tree or an installed package.

The Contract at this branch's base (``a02e3485``, version 4.1) is read with
``git show``; it is the reference for "moves exactly those parts".
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]

CIT_P = "docs/changes/W2-49-CIT-P.md"
CIT_E = "docs/changes/W2-49-CIT-E.md"
CONTRACT_YAML = "docs/contract/contract.yaml"
CONTRACT_MD = "docs/contract/CONTRACT_v4.md"

BASE_COMMIT = "a02e3485"

# The covers items DEC-722 names as the ones whose parts move to Wave 2.  Only
# these may change wave, in place, between the base and v4.2.
MOVED_ITEMS = ("CAP-44.f", "CAP-44.h", "CAP-43.b")
# New covers items (a split) may only appear in these capabilities.
SPLIT_CAPABILITIES = ("CAP-43", "CAP-44")

VERDICTS = ("ADOPTED_HEALTHY", "ADOPTED_WITH_ACCEPTED_EXCEPTIONS", "NOT_ADOPTED_HEALTHY")

# "The rest of CAP-43.b": every release content of CAP-43.b but the manifest
# and the file hashes, each with a pattern that survives a light rewording.
CAP_43B_REST = {
    "semantic version": r"semantic version",
    "supported migrations": r"migration",
    "schema versions": r"schema",
    "CLI/runtime versions": r"\bCLI\b|runtime",
    "adapter/capability versions": r"adapter",
    "release notes": r"release notes",
    "affected indexes": r"\bindex",
    "required human decisions": r"human decision",
    "rollback procedure": r"rollback",
}


# --------------------------------------------------------------------------
# Reading files


def read_doc(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        pytest.fail(f"{rel} does not exist yet (W2-49 has not written it)")
    return path.read_text(encoding="utf-8")


def read_base(rel: str) -> str:
    proc = subprocess.run(
        ["git", "show", f"{BASE_COMMIT}:{rel}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        pytest.fail(f"cannot read {rel} at the base {BASE_COMMIT}: {proc.stderr.strip()}")
    return proc.stdout


def load_yaml_text(text: str) -> dict:
    return yaml.safe_load(text)


# --------------------------------------------------------------------------
# Text helpers


def clean(text: str) -> str:
    """Drop Markdown escapes so ``ADOPTED\\_HEALTHY`` reads as ``ADOPTED_HEALTHY``."""
    return text.replace("\\_", "_").replace("\\*", "*")


def wave_token(wave: str) -> re.Pattern:
    """``W2`` / ``Wave 2`` as a word; never the W2 of a ticket id such as ``W2-02``."""
    n = wave[-1]
    return re.compile(rf"(?<![\w-])W{n}(?![\w-])|\bWave {n}\b", re.IGNORECASE)


def gate(name: str) -> str:
    """An adoption stage id as a word: ``A1`` never matches ``A10``."""
    return rf"(?<![\w-]){name}(?!\d)"


def verdict(name: str) -> str:
    """A verdict name as a word: ``ADOPTED_HEALTHY`` never matches ``NOT_ADOPTED_HEALTHY``."""
    return rf"(?<![A-Z_]){name}(?![A-Z_])"


def has(pattern: str, text: str) -> bool:
    return re.search(pattern, clean(text), re.IGNORECASE) is not None


def clauses(text: str) -> list[str]:
    return [c for c in re.split(r";|\.\s|\n", clean(text)) if c.strip()]


# --------------------------------------------------------------------------
# The Contract as a list of covers items, from either file


@dataclass
class Covers:
    cap: str
    id: str
    wave: str
    text: str  # every field but id, wave and provider, joined
    raw: dict = field(default_factory=dict)


@dataclass
class ContractModel:
    source: str  # "yaml" or "markdown"
    version: str
    covers: list[Covers]
    cap_waves: dict[str, str]

    def covers_of(self, cap: str) -> list[Covers]:
        return [c for c in self.covers if c.cap == cap]

    def by_id(self) -> dict[str, Covers]:
        return {c.id: c for c in self.covers}


def _flatten(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return " ".join(_flatten(v) for v in value)
    if isinstance(value, dict):
        return " ".join(_flatten(v) for v in value.values())
    return "" if value is None else str(value)


def yaml_model(text: str) -> ContractModel:
    data = load_yaml_text(text)
    covers, cap_waves = [], {}
    for cap in data.get("capabilities", []):
        cap_waves[cap["id"]] = str(cap.get("wave"))
        for item in cap.get("covers", []) or []:
            body = " ".join(
                _flatten(v) for k, v in item.items() if k not in ("id", "wave", "provider")
            )
            covers.append(Covers(cap["id"], item["id"], str(item.get("wave")), body, item))
    return ContractModel("yaml", str(data.get("version")), covers, cap_waves)


_MD_COVERS = re.compile(r"^(\s*)-\s*`(CAP-\d+\.[A-Za-z0-9]+)`\s*\[(\w+)\]\s*(.*)$")
_MD_CAP = re.compile(r"^###\s+(CAP-\d+)\b")
_MD_WAVE = re.compile(r"^\s*-\s*\*\*Wave:\*\*\s*(\w+)")


def md_version(text: str) -> str:
    m = re.search(r'^version:\s*"?([0-9.]+)"?\s*$', text, re.MULTILINE)
    return m.group(1) if m else ""


def md_model(text: str) -> ContractModel:
    covers, cap_waves = [], {}
    cap = None
    current = None
    indent = 0
    for line in text.splitlines():
        m = _MD_CAP.match(line)
        if m:
            cap, current = m.group(1), None
            continue
        m = _MD_WAVE.match(line)
        if m and cap and cap not in cap_waves:
            cap_waves[cap] = m.group(1)
            continue
        m = _MD_COVERS.match(line)
        if m:
            indent = len(m.group(1))
            current = Covers(m.group(2).rsplit(".", 1)[0], m.group(2), m.group(3), m.group(4))
            covers.append(current)
            continue
        if current is not None:
            stripped = line.strip()
            lead = len(line) - len(line.lstrip())
            if stripped and lead > indent:
                current.text += "\n" + stripped
            else:
                current = None
    return ContractModel("markdown", md_version(text), covers, cap_waves)


def current_model(source: str) -> ContractModel:
    if source == "yaml":
        return yaml_model(read_doc(CONTRACT_YAML))
    return md_model(read_doc(CONTRACT_MD))


def base_yaml_model() -> ContractModel:
    return yaml_model(read_base(CONTRACT_YAML))


def require_v42(model: ContractModel) -> None:
    assert model.version == "4.2", (
        f"the Contract's {model.source} file is version {model.version!r}, not 4.2: "
        "Contract v4.2 is not written yet (it waits for the owner's approval of the CIT-P, CAP-33)"
    )


def placements(model: ContractModel, cap: str, wave: str, pattern: str) -> list[tuple[Covers, str]]:
    """Where the Contract places a part (``pattern``) of ``cap``'s covers items in ``wave``.

    A part is placed in a wave when a covers item of that capability names it and
    either the item's own ``wave`` is that wave, or one clause of the item's text
    (its wording or a note on it) names the part together with that wave.  This
    holds for a split into separate covers items, for an item moved whole with a
    note on what stays, and for an item kept in place with a note on what moves.
    """
    token = wave_token(wave)
    hits = []
    for item in model.covers_of(cap):
        if item.wave == wave and has(pattern, item.text):
            hits.append((item, item.text))
        for clause in clauses(item.text):
            if token.search(clause) and has(pattern, clause):
                hits.append((item, clause))
    return hits


def describe(model: ContractModel, cap: str) -> str:
    return "\n".join(f"  {c.id} [{c.wave}] {c.text[:160]}" for c in model.covers_of(cap))


# --------------------------------------------------------------------------
# Change records: scopes in which two facts must appear together


def units(text: str) -> list[str]:
    """Table rows, list items (with their continuation lines), headings and paragraphs."""
    out, cur = [], []

    def flush():
        if cur:
            out.append(" ".join(cur))
            cur.clear()

    for line in clean(text).splitlines():
        s = line.strip()
        if not s:
            flush()
        elif s.startswith("|") or s.startswith("#"):
            flush()
            out.append(s)
        elif re.match(r"^([-*+]|\d+[.)])\s", s):
            flush()
            cur.append(s)
        else:
            cur.append(s)
    flush()
    return out


def leaf_sections(text: str) -> list[str]:
    """Each heading with the text up to the next heading of any level."""
    out, cur = [], []
    for line in clean(text).splitlines():
        if line.startswith("#") and cur:
            out.append("\n".join(cur))
            cur = []
        cur.append(line)
    if cur:
        out.append("\n".join(cur))
    return out


def scopes(text: str) -> list[str]:
    return units(text) + leaf_sections(text)


def together(text: str, *patterns: str) -> bool:
    """True when one scope (a unit or a leaf section) matches every pattern."""
    return any(all(has(p, s) for p in patterns) for s in scopes(text))


def covers_ids(text: str) -> set[str]:
    return set(re.findall(r"CAP-\d+\.[a-z0-9]+(?![\w])", clean(text)))


# --------------------------------------------------------------------------
# Added for the owner's answers to the CIT-P (DEC-741)

CAPABILITIES = "docs/contract/capabilities"

# Question A (a1): the new ids that carry the Wave 3 rest of a split item.
NEW_SPLIT_IDS = ("CAP-43.d", "CAP-44.k", "CAP-44.l")


def frontmatter(text: str) -> tuple[dict, str]:
    """A Markdown file's YAML frontmatter and the body after it."""
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    return (yaml.safe_load(m.group(1)) or {}), m.group(2)


def contract_status(source: str) -> str:
    if source == "yaml":
        return str(load_yaml_text(read_doc(CONTRACT_YAML)).get("status"))
    return str(frontmatter(read_doc(CONTRACT_MD))[0].get("status"))


def cap_wave_note(source: str, cap: str) -> str:
    """A capability's wave note: ``wave_note`` in the YAML, the ``Wave:`` line in the Markdown."""
    if source == "yaml":
        for c in load_yaml_text(read_doc(CONTRACT_YAML)).get("capabilities", []):
            if c["id"] == cap:
                return _flatten(c.get("wave_note"))
        return ""
    inside = False
    for line in read_doc(CONTRACT_MD).splitlines():
        m = _MD_CAP.match(line)
        if m:
            inside = m.group(1) == cap
            continue
        if inside and _MD_WAVE.match(line):
            return line
    return ""


def record_path(cap_id: str) -> Path:
    return ROOT / CAPABILITIES / f"{cap_id}.md"


def read_record(cap_id: str) -> tuple[dict, str]:
    path = record_path(cap_id)
    if not path.is_file():
        pytest.fail(f"{CAPABILITIES}/{cap_id}.md does not exist")
    return frontmatter(path.read_text(encoding="utf-8"))
