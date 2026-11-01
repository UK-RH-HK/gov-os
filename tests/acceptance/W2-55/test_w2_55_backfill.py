"""KPI 4 and failure 4: the backfill is a proposal, ``docs/research/W2-55-backfill.md`` (S6).

These cases read the tree they run in: the proposal file, and the register at the ticket's base (the merge base of
``HEAD`` with ``w2/integrate``). The proposal has one row per entry of that register, in its order, each with a domain
of the closed list, a scope, a lands-in, a status note and a reason; every Amends and Refines relation the register's
status lines record (the about 120 DEC-825 item 4 left for W2-55); a sample for the owner that can be drawn again.
Nothing is written to the register: the branch changes nothing in ``docs/DECISION_REGISTER.md`` against its base.
"""

from __future__ import annotations

import re
import subprocess

import pytest

import w2_55_support as s

PROPOSAL = s.REPO_ROOT / "docs" / "research" / "W2-55-backfill.md"
INTEGRATION = "w2/integrate"
COLUMNS = ["id", "domain", "scope", "lands in", "status", "reason"]
HEADINGS = {"tags": "Proposed tags", "relations": "Amends and refines", "sample": "Sample for the owner's review"}
STATUS_NOTE = re.compile(r"(in force|done|SUPERSEDED by DEC-[0-9]+|Changed by:? DEC-[0-9]+)\b")


def repo_git(*args):
    done = subprocess.run(["git", "-C", str(s.REPO_ROOT), *args], capture_output=True, text=True, timeout=120)
    return done


@pytest.fixture(scope="module")
def base():
    """The merge base of HEAD with the integration branch, and the register it holds."""
    if repo_git("rev-parse", "--verify", "--quiet", f"{INTEGRATION}^{{commit}}").returncode != 0:
        pytest.skip(f"this clone has no branch {INTEGRATION}: the ticket's base cannot be found")
    done = repo_git("merge-base", "HEAD", INTEGRATION)
    assert done.returncode == 0, f"git merge-base failed:\n{done.stderr}"
    commit = done.stdout.strip()
    shown = repo_git("show", f"{commit}:{s.REGISTER}")
    assert shown.returncode == 0, f"the base does not hold {s.REGISTER}:\n{shown.stderr}"
    return commit, shown.stdout


@pytest.fixture(scope="module")
def proposal():
    """``() -> the proposal's text``, read in the case, so a missing file fails the case."""
    def read():
        assert PROPOSAL.is_file(), f"the backfill proposal {PROPOSAL.relative_to(s.REPO_ROOT)} does not exist"
        return PROPOSAL.read_text(encoding="utf-8")
    return read


def plain(text):
    return text.replace("`", "").replace("*", "").strip()


def sections(text):
    """``heading -> its lines`` of the level-2 sections."""
    found, current = {}, None
    for line in text.split("\n"):
        hit = re.match(r"## (.+?)\s*$", line)
        if hit:
            current = plain(hit.group(1)).replace("’", "'")
            found[current] = []
        elif current is not None:
            found[current].append(line)
    return found


def section(text, key):
    found = sections(text)
    assert HEADINGS[key] in found, f"the proposal has no section `## {HEADINGS[key]}`; its sections: {list(found)}"
    return found[HEADINGS[key]]


def cells(line):
    parts = [part.strip() for part in re.split(r"(?<!\\)\|", line.strip())]
    return parts[1:-1] if line.strip().endswith("|") else parts[1:]


def table(text):
    rows = [line for line in section(text, "tags") if line.strip().startswith("|")]
    assert len(rows) >= 2, "the section `## Proposed tags` holds no table"
    header = [plain(cell).lower() for cell in cells(rows[0])]
    assert header == COLUMNS, f"the table's columns are {header}, not {COLUMNS}"
    assert all(set(cell) <= set(":- ") for cell in cells(rows[1])), "the table's second row is not its separator"
    return [dict(zip(COLUMNS, (plain(cell) for cell in cells(row)))) for row in rows[2:]]


def status_word(register_text, entry_id):
    first, last = s.entry_spans(register_text)[entry_id]
    lines = register_text.split("\n")[first:last]
    status = next((line for line in lines if line.strip()), "")
    hit = re.match(r"\s*(?:[-*+]\s+)?\*\*Status:\*\*\s*([A-Za-z][A-Za-z_-]*)", status)
    return (hit.group(1) if hit else None), status


def recorded_relations(register_text):
    """``(new, old)`` of every Amends or Refines field on an entry's status line naming another entry."""
    spans, pairs = s.entry_spans(register_text), set()
    for entry_id in spans:
        _, status = status_word(register_text, entry_id)
        for field in re.finditer(r"\*\*(Amends|Refines):\*\*([^·\n]*)", status):
            pairs.update((entry_id, old) for old in re.findall(r"DEC-[0-9]+", field.group(2))
                         if old in spans and old != entry_id)
    return pairs


# --------------------------------------------------------------------------
# Failure 4: nothing is applied to the register
# --------------------------------------------------------------------------

def test_the_branch_changes_nothing_in_the_register_against_its_base(base):
    commit, _ = base
    done = repo_git("diff", "--stat", commit, "--", s.REGISTER)
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == "", (f"{s.REGISTER} differs from the ticket's base {commit[:12]}: the backfill is a "
                                       f"proposal until the owner accepts it\n{done.stdout}")


# --------------------------------------------------------------------------
# KPI 4: the proposal
# --------------------------------------------------------------------------

def test_the_proposal_has_its_three_sections(proposal):
    found = sections(proposal())
    missing = [heading for heading in HEADINGS.values() if heading not in found]
    assert not missing, f"the proposal lacks the sections {missing}; it has {list(found)}"


def test_one_row_per_register_entry_at_the_base_in_its_order(proposal, base):
    _, register_text = base
    expected = s.heading_ids(register_text)
    got = [row["id"] for row in table(proposal())]
    missing = [i for i in expected if i not in got]
    extra = [i for i in got if i not in expected]
    twice = sorted({i for i in got if got.count(i) > 1})
    assert not missing and not extra and not twice, (
        f"the table's rows are not the register's {len(expected)} entries: {len(missing)} missing "
        f"({missing[:10]}), {len(extra)} not in the register ({extra[:10]}), twice: {twice[:10]}")
    assert got == expected, "the rows are not in the register's order"


def test_every_row_has_a_domain_a_scope_a_lands_in_a_status_and_a_reason(proposal, base):
    _, register_text = base
    ids = set(s.heading_ids(register_text))
    held = set(repo_git("ls-tree", "-r", "--name-only", "HEAD").stdout.split("\n"))
    wrong = []
    for row in table(proposal()):
        why = []
        if row.get("domain") not in s.DOMAINS:
            why.append(f"domain {row.get('domain')!r} is not of the closed list")
        if row.get("scope") not in s.SCOPES:
            why.append(f"scope {row.get('scope')!r} is neither repository nor kernel")
        places = row.get("lands in", "")
        if places != "none":
            named = [place.strip() for place in places.split(",") if place.strip()]
            if not named:
                why.append("lands in is empty")
            why += [f"lands in {place!r} is no file HEAD holds" for place in named if place not in held]
        note = row.get("status", "")
        if not STATUS_NOTE.match(note):
            why.append(f"status {note!r} is none of: in force, done, SUPERSEDED by DEC-<n>, Changed by: DEC-<n>")
        why += [f"status names {other}, which the register does not hold"
                for other in re.findall(r"DEC-[0-9]+", note) if other not in ids]
        if not row.get("reason"):
            why.append("no reason")
        if why:
            wrong.append(f"{row.get('id')}: {'; '.join(why)}")
    assert not wrong, f"{len(wrong)} rows are not complete:\n" + "\n".join(wrong[:25])


def test_an_entry_the_register_marks_superseded_is_proposed_superseded_by_its_successor(proposal, base):
    _, register_text = base
    rows = {row["id"]: row for row in table(proposal())}
    wrong = []
    for entry_id in s.heading_ids(register_text):
        word, _ = status_word(register_text, entry_id)
        if word == "SUPERSEDED" and not rows.get(entry_id, {}).get("status", "").startswith("SUPERSEDED by DEC-"):
            wrong.append(f"{entry_id}: {rows.get(entry_id, {}).get('status')!r}")
    assert not wrong, f"entries the register marks SUPERSEDED, not proposed `SUPERSEDED by DEC-<n>`: {wrong}"


def test_every_amends_and_refines_relation_is_listed_with_the_old_entrys_status_note(proposal, base):
    _, register_text = base
    ids = set(s.heading_ids(register_text))
    listed, wrong = set(), []
    for line in section(proposal(), "relations"):
        text = plain(line)
        hit = re.search(r"(DEC-[0-9]+) (amends|refines) (DEC-[0-9]+)", text)
        if not hit:
            continue
        new, old = hit.group(1), hit.group(3)
        listed.add((new, old))
        rest = text[hit.end():]
        if new not in ids or old not in ids or new == old:
            wrong.append(f"{text}: an id the register does not hold, or an entry relating to itself")
        elif not re.search(rf"\bby:?\s+(?:DEC-[0-9]+,\s*)*{new}\b", rest):
            wrong.append(f"{text}: no status note for {old} naming {new}")
    assert listed, "the section `## Amends and refines` lists no `DEC-<new> amends|refines DEC-<old>` line"
    assert not wrong, "relation lines that are not right:\n" + "\n".join(wrong[:25])
    missing = sorted(recorded_relations(register_text) - listed)
    assert not missing, (f"{len(missing)} Amends or Refines relations of the register's status lines are not listed "
                         f"(DEC-825 item 4): {missing[:15]}")


def test_the_sample_can_be_drawn_again_and_says_what_the_owner_checks(proposal, base):
    _, register_text = base
    ids = set(s.heading_ids(register_text))
    text = "\n".join(section(proposal(), "sample"))
    drawn = set(re.findall(r"DEC-[0-9]+", text))
    assert drawn, "the sample names no entry"
    assert drawn <= ids, f"the sample names entries the register does not hold: {sorted(drawn - ids)}"
    assert re.search(r"(?i)\b(seed|rule)\b", text), "the sample states no seed or rule by which it was drawn"
    assert re.search(r"(?i)\bcheck", text), "the sample does not say what the owner is asked to check"


def test_the_proposal_states_how_it_was_made(proposal):
    prose = "\n".join(line for line in proposal().split("\n") if not line.strip().startswith("|"))
    assert re.search(r"(?i)\b(script|rules|method)\b", prose), \
        "the proposal does not state how it was made (the script or the rules), so it cannot be made again"
