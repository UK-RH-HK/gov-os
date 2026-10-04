"""Support for the W1-34 acceptance tests (decision-package template).

The tests read only what the template publishes: the files named ``decision-package*`` and
``decision-record*`` under the kernel templates folder, their frontmatter and their text.
Nothing is imported from the implementation, and nothing is written.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
TEMPLATES_REL = "template/governance/kernel/templates"
PACKAGE_PREFIX = "decision-package"
RECORD_PREFIX = "decision-record"
PACKAGE_TYPE = "decision-package"
GATE_TYPES = ("gate", "decision-package")

# KPI success 1: the ten fields, each as (name, pattern a heading of the form must match).
TEN_FIELDS = (
    ("question", r"\bquestion\b"),
    ("why now", r"\bwhy now\b"),
    ("current state", r"\bcurrent state\b"),
    ("options", r"\boptions\b"),
    ("impact", r"\bimpact\b"),
    ("reversibility", r"\breversib"),
    ("cost of rework", r"\bcost\b"),
    ("recommendation", r"\brecommendation\b"),
    ("confidence", r"\bconfidence\b"),
    ("exact permitted next actions", r"\bpermitted next actions\b"),
)
RANKS = ("P1", "P2", "P3")
# KPI success 4: the five states of a gate record.
GATE_STATES = ("open", "answered", "declined", "revoked", "stale")
# DEC-328: the state lives in `status` alone; each value of `status` with the gate state it stands for.
STATUS_STATES = (
    ("PROPOSED", "open"),
    ("ACCEPTED", "answered"),
    ("DECLINED", "declined"),
    ("REVOKED", "revoked"),
    ("STALE", "stale"),
)
STATE_KEY = "status"
CIT_KEY = "cit"
# Shared frontmatter of every record (W1-08); it classes the record, not the gate.
NOT_A_GATE_STATE_KEY = ("state_class",)
CONFIDENCE_LEVELS = ("low", "medium", "high")

DECISION_ID = re.compile(r"\b(?:ADR|DEC)-[0-9]{3,}\b")
# "ACCEPTED (owner, 2026-10-04)": the word and what stands in its brackets.
ACCEPTED_FORM = re.compile(r"\bACCEPTED\b\s*\(([^()]*)\)")
DATE_SLOT = re.compile(r"\bYYYY-MM-DD\b|\b[0-9]{4}-[0-9]{2}-[0-9]{2}\b")
OBLIGATION = re.compile(r"\b(required|must|mandatory|never (?:empty|blank|omitted|left out))\b", re.IGNORECASE)
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")


def _files(prefix):
    folder = REPO_ROOT / TEMPLATES_REL
    assert folder.is_dir(), f"there is no {TEMPLATES_REL}/"
    found = sorted(path for path in folder.rglob("*") if path.is_file() and path.name.startswith(prefix))
    assert found, f"no file named {prefix}* under {TEMPLATES_REL}/"
    return found


def package_files():
    return _files(PACKAGE_PREFIX)


def record_files():
    return _files(RECORD_PREFIX)


def joined(paths):
    return "\n\n".join(path.read_text(encoding="utf-8") for path in paths)


def split(path):
    """``(frontmatter map, body text)`` of a template file; the map is empty when the file has no frontmatter."""
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                loaded = yaml.safe_load("\n".join(lines[1:index])) or {}
                assert isinstance(loaded, dict), f"{Path(path).name}: the frontmatter is not a map"
                return loaded, "\n".join(lines[index + 1:])
        raise AssertionError(f"{Path(path).name}: the frontmatter that opens with '---' is never closed")
    return {}, text


class Form:
    """The decision-package template: its frontmatter and the sections of its body."""

    def __init__(self, path):
        self.path = path
        self.name = path.name
        self.frontmatter, self.body = split(path)
        self.text = path.read_text(encoding="utf-8")

    def headings(self):
        found = []
        for line in self.body.splitlines():
            match = HEADING.match(line)
            if match:
                found.append(match.group(2))
        return found

    def section(self, pattern):
        """The text under the first heading that matches ``pattern``, up to the next heading of the same or a
        higher level; ``None`` when no heading matches."""
        lines = self.body.splitlines()
        for index, line in enumerate(lines):
            match = HEADING.match(line)
            if not match or not re.search(pattern, match.group(2), re.IGNORECASE):
                continue
            level = len(match.group(1))
            taken = []
            for later in lines[index + 1:]:
                other = HEADING.match(later)
                if other and len(other.group(1)) <= level:
                    break
                taken.append(later)
            return "\n".join(taken).strip()
        return None


def form():
    """The one ``decision-package*`` file whose frontmatter ``type`` is ``decision-package``."""
    forms = [path for path in package_files() if split(path)[0].get("type") == PACKAGE_TYPE]
    names = [path.name for path in package_files()]
    assert forms, f"no {PACKAGE_PREFIX}* file under {TEMPLATES_REL}/ has the type {PACKAGE_TYPE} (found: {names})"
    assert len(forms) == 1, (f"more than one {PACKAGE_PREFIX}* file has the type {PACKAGE_TYPE}: "
                             f"{[path.name for path in forms]}; a package is written from one form")
    return Form(forms[0])


def gate_frontmatters():
    """``file name -> frontmatter`` of every ``decision-package*`` file that is a gate or decision-package record."""
    found = {}
    for path in package_files():
        frontmatter = split(path)[0]
        if frontmatter.get("type") in GATE_TYPES:
            found[path.name] = frontmatter
    return found


def paragraphs(text):
    """Blocks of consecutive non-blank lines."""
    return [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]


def paragraphs_with(text, pattern):
    return [block for block in paragraphs(text) if re.search(pattern, block, re.IGNORECASE)]


def has_word(text, word):
    return re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE) is not None


def key_tokens(key):
    return [token for token in re.split(r"[^a-z0-9]+", str(key).lower()) if token]


def status_and_state_words(block):
    """The `status` values (upper case, as written) and the gate state words (lower case or capitalised) of a
    block, in the order they stand in it. ``STALE`` is a value and ``stale`` a state word."""
    values = {value for value, _ in STATUS_STATES}
    states = {state for _, state in STATUS_STATES}
    found = []
    for word in re.findall(r"[A-Za-z]+", block):
        if word in values:
            found.append(word)
        elif word in states or (word.lower() in states and word == word.capitalize()):
            found.append(word.lower())
    return found


def unpaired_statuses(text):
    """The ``(value, state)`` pairs of DEC-328 that no paragraph of ``text`` states. A pair is stated when the
    value and its state word stand next to each other, with no other value or state word between them:
    "`ACCEPTED` is answered", "answered is `status: ACCEPTED`", or a table row with the two."""
    stated = set()
    for block in paragraphs(text):
        words = status_and_state_words(block)
        stated.update(frozenset(pair) for pair in zip(words, words[1:]))
    return [(value, state) for value, state in STATUS_STATES if frozenset((value, state)) not in stated]


def second_state_keys(frontmatter):
    """The keys, other than ``status``, that would hold a gate state: a key named for a state or a status, or a
    key whose value is one of the five state words or one of the five `status` values."""
    words = {word.lower() for pair in STATUS_STATES for word in pair}
    found = []
    for key, value in frontmatter.items():
        if key == STATE_KEY or key in NOT_A_GATE_STATE_KEY:
            continue
        named = {"state", "status"} & set(key_tokens(key))
        valued = isinstance(value, str) and value.strip().lower() in words
        if named or valued:
            found.append(key)
    return found
