"""Shared helpers of the W2-175 acceptance tests (README).

Everything here reads files as the tree holds them (the seven role templates, ``brief.md``, the CIT-P record) or as
git holds them at a named base commit. A statement is judged the way W2-128's cases judge one: its ``units`` (a
paragraph, a list item or a table row, wrapped lines joined) and ``fold`` (white space collapsed, lower case). The
interface is the ticket's KPI lines and its "Interface" section (DAEO-wahn); nothing here reads this ticket's
implementation branch.
"""

from __future__ import annotations

import hashlib
import re
import subprocess

import w2_128_support as s

REPO = s.REPO
TEMPLATES = s.TEMPLATES
TEMPLATES_REL = "template/governance/kernel/templates"
RECORD = REPO / "docs/changes/W2-175-CIT-P.md"

SEVEN = ("role-cto", "role-engineer", "role-lead", "role-product-spec", "role-research", "role-reviewer",
         "role-test-designer")
SIX = tuple(stem for stem in SEVEN if stem != "role-cto")  # the record rule's templates (S3)

# The base of each template: the last commit that changed the file before this ticket (W2-128's round 1 or its
# round 1 fixes, both version 1.0.0, approved by DEC-1116). A base is the last commit to change the file before the
# ticket, never an older one, so that "the base's bytes" are the bytes this ticket starts from. The commits are
# named, not read from w2/integrate: after this ticket merges, integrate holds the new bytes, and a pinned commit
# still names the old ones, so these cases read the same base before and after the merge. Each case checks the
# premise (the file at its base is version 1.0.0 and named for its stem) before it judges anything.
BASE = {
    "role-cto": "a6c83d497035",
    "role-engineer": "a6c83d497035",
    "role-product-spec": "a6c83d497035",
    "role-reviewer": "a6c83d497035",
    "role-lead": "baa2696f713f",
    "role-research": "baa2696f713f",
    "role-test-designer": "baa2696f713f",
}

# The stop sentence of brief.md's return section, word for word (DEC-1137 (2); the ticket's S4 line).
STOP = "Refused twice for the same call: stop and say so. Never work around a refusal: report it."

NEGATION = re.compile(r"\b(never|not)\b", re.I)  # the S2 line's negations, as its verify names them
NO_WORD = s.NEGATION  # W2-128's wider set (no, never, not, ...): "no worker puts" (S3)
LAST_BRACKET = re.compile(r"\[([^\[\]]*)\][.)]*\s*$")
HEX64 = re.compile(r"\b[0-9a-f]{64}\b")
DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


# --- the templates ------------------------------------------------------------------------------------------------

def path_of(stem: str):
    return TEMPLATES / f"{stem}.md"


def text_of(stem: str) -> str:
    return s.template(stem)


def statements(stem: str) -> list[str]:
    """The template's statements (W2-128's units of the body, front matter left out)."""
    return s.units(s.body(stem))


def ends_citing(unit: str, dec: str) -> bool:
    """Whether the statement ends with a bracket that cites ``dec`` (``[DEC-820]``, or ``[DEC-820, DEC-957]``),
    a closing full stop or parenthesis after it allowed."""
    found = LAST_BRACKET.search(unit)
    return bool(found) and dec in s.DEC_ID.findall(found.group(1))


def holding(stem: str, *needles: str, negation: re.Pattern | None = None, any_of: tuple[str, ...] = (),
            cites: str | None = None) -> list[str]:
    """The statements of a template that hold every needle (folded), at least one of ``any_of``, a match of
    ``negation`` and, with ``cites``, end with a bracket citing that id."""
    hits = []
    for unit in statements(stem):
        text = s.fold(unit)
        if all(s.fold(needle) in text for needle in needles) \
                and (not any_of or any(s.fold(alt) in text for alt in any_of)) \
                and (negation is None or negation.search(text)) \
                and (cites is None or ends_citing(unit, cites)):
            hits.append(unit)
    return hits


def stop_problem(text: str, where: str) -> str | None:
    """None when ``text`` holds the stop sentence word for word (every character, white space runs folded to one
    space, so a line wrap is no change); else why not. The one check S4 and F1 use."""
    if STOP in " ".join(text.split()):
        return None
    return f"{where} does not hold the stop sentence word for word: {STOP!r}"


# --- git ------------------------------------------------------------------------------------------------------------

def git_show(commit: str, rel: str) -> bytes:
    done = subprocess.run(["git", "-C", str(REPO), "show", f"{commit}:{rel}"], capture_output=True)
    assert done.returncode == 0, \
        f"premise: git show {commit}:{rel} failed: {done.stderr.decode(errors='replace').strip()}"
    return done.stdout


def base_bytes(stem: str) -> bytes:
    return git_show(BASE[stem], f"{TEMPLATES_REL}/{stem}.md")


def base_text(stem: str) -> str:
    text = base_bytes(stem).decode("utf-8")
    front, _ = s.split(text)
    assert isinstance(front, dict) and front.get("name") == stem and front.get("version") == "1.0.0", \
        f"premise: {stem}.md at its base {BASE[stem]} is not the 1.0.0 template named {stem}: {front!r}"
    return text


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --- the CIT-P record (S7) ------------------------------------------------------------------------------------------

# CAP-33's five steps as the S7 line names them, each read loosely from a heading or a table row's first cell.
STEPS = {
    "evidence": re.compile(r"evidence|trigger", re.I),
    "proposal": re.compile(r"propos|what changes|\bdelta\b", re.I),
    "independent review": re.compile(r"review", re.I),
    "owner's approval": re.compile(r"approv", re.I),
    "versioned promotion": re.compile(r"promot", re.I),
}
STATUSES = ("PROPOSED", "ACCEPTED", "APPLIED")
APPROVED = ("ACCEPTED", "APPLIED")
PENDING = re.compile(r"^\W*(pending|awaiting|not yet|to come|tbd|todo|none)\b", re.I)


def record() -> tuple[dict | None, str]:
    assert RECORD.is_file(), "docs/changes/W2-175-CIT-P.md does not exist"
    return s.split(RECORD.read_text(encoding="utf-8"))


def entries(body: str) -> list[tuple[str, str]]:
    """(title, text) of every section and every table row of the record's body: a heading of level 2 or more with
    the lines up to the next heading, and a table row's first cell with its other cells. Header and separator rows
    of a table are left out."""
    found: list[tuple[str, str]] = []
    title, held, fenced, header = None, [], False, True
    for line in body.split("\n"):
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            fenced = not fenced
        if not fenced and re.match(r"^#{2,}\s", stripped):
            if title is not None:
                found.append((title, "\n".join(held).strip()))
            title, held = stripped.lstrip("#").strip(), []
            continue
        if not fenced and stripped.startswith("|"):
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", cell) for cell in cells if cell):
                header = False
            elif header:
                pass  # the row before the separator: the table's header
            else:
                found.append((cells[0], " | ".join(cells[1:]).strip()))
        else:
            header = True
        if title is not None:
            held.append(line)
    if title is not None:
        found.append((title, "\n".join(held).strip()))
    return found


def step_assignment(found: list[tuple[str, str]]) -> dict[str, int] | None:
    """Each CAP-33 step matched to its own entry (no entry serves two steps), or None when that cannot be done."""
    options = {step: [i for i, (title, _) in enumerate(found) if pattern.search(title.replace("*", ""))]
               for step, pattern in STEPS.items()}
    owner: dict[int, str] = {}

    def place(step: str, seen: set[int]) -> bool:
        for i in options[step]:
            if i in seen:
                continue
            seen.add(i)
            if i not in owner or place(owner[i], seen):
                owner[i] = step
                return True
        return False

    for step in STEPS:
        if not place(step, set()):
            return None
    return {step: i for i, step in owner.items()}


def approval_given(text: str) -> bool:
    """An owner's-approval entry that records an approval: not empty, not a 'pending' line, and naming the owner's
    decision (a DEC id) or the date of the approval."""
    plain = text.replace("*", "").strip()
    return bool(plain) and not PENDING.match(plain) and bool(s.DEC_ID.search(plain) or DATE.search(plain))


def ids_in(value) -> set[str]:
    if isinstance(value, list):
        value = " ".join(str(item) for item in value)
    return set(s.DEC_ID.findall(str(value))) if value is not None else set()


def table_rows(body: str) -> list[str]:
    rows, fenced = [], False
    for line in body.split("\n"):
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if not fenced and stripped.startswith("|"):
            rows.append(stripped)
    return rows
