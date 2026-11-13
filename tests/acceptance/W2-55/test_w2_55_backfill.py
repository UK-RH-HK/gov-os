"""KPI 4 and failure 4: the backfill is a proposal, ``docs/research/W2-55-backfill.md`` (S6).

These cases read the tree they run in: the proposal file, and the register **as of the commit that last wrote the
proposal file** (``git log -1 --format=%H -- docs/research/W2-55-backfill.md``; DEC-1028 (2), option (i)). On W2-55's
branch that is the register the proposal was made from; once merged, ``w2/integrate``'s register grows with every
decision, and a fixed proposal compared with it went red for entries recorded after it (D-6, DEC-1109 (2)). No such
commit, or no register in it, fails the case. The proposal has one row per entry of that register, in its order, each
with a domain of the closed list, a scope, a lands-in, a status note and a reason; every Amends and Refines relation
the register's status lines record (the about 120 DEC-825 item 4 left for W2-55); a sample for the owner that can be
drawn again.

Nothing is written to the register: no commit that wrote the proposal changes ``docs/DECISION_REGISTER.md``; the merge
that brought it onto ``HEAD``'s first-parent line changes nothing in it against that merge's first parent; and the tree
(committed and working) changes nothing in it against its merge base with ``w2/integrate`` (on a branch, the branch's
own changes; on ``w2/integrate`` itself, the working tree's).
"""

from __future__ import annotations

import re
import subprocess

import pytest

import w2_55_support as s

PROPOSAL_REL = "docs/research/W2-55-backfill.md"
PROPOSAL = s.REPO_ROOT / PROPOSAL_REL
INTEGRATION = "w2/integrate"
COLUMNS = ["id", "domain", "scope", "lands in", "status", "reason"]
HEADINGS = {"tags": "Proposed tags", "relations": "Amends and refines", "sample": "Sample for the owner's review"}
STATUS_NOTE = re.compile(r"(in force|done|SUPERSEDED by DEC-[0-9]+|Changed by:? DEC-[0-9]+)\b")


def repo_git(*args):
    done = subprocess.run(["git", "-C", str(s.REPO_ROOT), *args], capture_output=True, text=True, timeout=120)
    return done


@pytest.fixture(scope="module")
def written():
    """``() -> (commit, register text)``: the commit that last wrote the proposal file and the register it holds
    (DEC-1028 (2) (i)), read in the case, so a missing commit or register fails the case."""
    held = {}

    def read():
        if not held:
            done = repo_git("log", "-1", "--format=%H", "--", PROPOSAL_REL)
            assert done.returncode == 0, f"git log failed:\n{done.stderr}"
            commit = done.stdout.strip()
            assert commit, f"no commit wrote {PROPOSAL_REL}: the register it was proposed from cannot be found"
            shown = repo_git("show", f"{commit}:{s.REGISTER}")
            assert shown.returncode == 0, \
                f"the proposal's commit {commit[:12]} does not hold {s.REGISTER}:\n{shown.stderr}"
            held["value"] = (commit, shown.stdout)
        return held["value"]
    return read


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


def merge_that_brought(commit):
    """The commit of ``HEAD``'s first-parent line that brought ``commit`` onto it, or None when ``commit`` is on that
    line itself (the branch that wrote it, or a fast-forward)."""
    line = repo_git("rev-list", "--first-parent", "HEAD")
    assert line.returncode == 0, line.stderr
    line = line.stdout.split()
    if commit in line:
        return None
    after = repo_git("rev-list", "--ancestry-path", f"{commit}..HEAD")
    assert after.returncode == 0, after.stderr
    after = set(after.stdout.split())
    brought = [c for c in line if c in after]
    assert brought, f"{commit[:12]} is not reachable from HEAD's first-parent line"
    return brought[-1]


# --------------------------------------------------------------------------
# Failure 4: nothing is applied to the register
# --------------------------------------------------------------------------

def test_the_branch_changes_nothing_in_the_register_against_its_base():
    # The commits that wrote the proposal: none of them writes the register.
    writers = repo_git("log", "--no-merges", "--format=%H", "--", PROPOSAL_REL)
    assert writers.returncode == 0, writers.stderr
    writers = writers.stdout.split()
    assert writers, f"no commit wrote {PROPOSAL_REL}"
    for commit in writers:
        names = repo_git("diff-tree", "--root", "--no-commit-id", "--name-only", "-r", commit)
        assert names.returncode == 0, names.stderr
        assert s.REGISTER not in names.stdout.split("\n"), (
            f"{commit[:12]} wrote the proposal and {s.REGISTER} together: the backfill is a proposal until the owner "
            f"accepts it")
    # The merge that brought each of them onto HEAD's first-parent line (w2/integrate's merge of the branch) changes
    # nothing in the register against its first parent: the branch, merged, wrote nothing there. Decisions recorded
    # on w2/integrate before or after that merge are in its first parent or after it, so they are not counted.
    for commit in writers:
        merge = merge_that_brought(commit)
        if merge is None:
            continue
        done = repo_git("diff", "--stat", f"{merge}^1", merge, "--", s.REGISTER)
        assert done.returncode == 0, done.stderr
        assert done.stdout.strip() == "", (
            f"the merge {merge[:12]} that brought the proposal's commit {commit[:12]} changed {s.REGISTER} against "
            f"its first parent: the branch wrote the register\n{done.stdout}")
    # The tree against its merge base with the integration branch: the branch's own changes, committed or not (on
    # w2/integrate itself, the working tree's).
    if repo_git("rev-parse", "--verify", "--quiet", f"{INTEGRATION}^{{commit}}").returncode != 0:
        pytest.skip(f"the proposal's commits and their merge write nothing; this clone has no branch {INTEGRATION}, "
                    f"so the branch's own changes against its base cannot be found")
    done = repo_git("merge-base", "HEAD", INTEGRATION)
    assert done.returncode == 0, f"git merge-base failed:\n{done.stderr}"
    base = done.stdout.strip()
    done = repo_git("diff", "--stat", base, "--", s.REGISTER)
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == "", (f"{s.REGISTER} differs from the ticket's base {base[:12]}: the backfill is a "
                                       f"proposal until the owner accepts it\n{done.stdout}")


# --------------------------------------------------------------------------
# KPI 4: the proposal
# --------------------------------------------------------------------------

def test_the_proposal_has_its_three_sections(proposal):
    found = sections(proposal())
    missing = [heading for heading in HEADINGS.values() if heading not in found]
    assert not missing, f"the proposal lacks the sections {missing}; it has {list(found)}"


def test_one_row_per_register_entry_at_the_base_in_its_order(proposal, written):
    commit, register_text = written()
    expected = s.heading_ids(register_text)
    got = [row["id"] for row in table(proposal())]
    missing = [i for i in expected if i not in got]
    extra = [i for i in got if i not in expected]
    twice = sorted({i for i in got if got.count(i) > 1})
    assert not missing and not extra and not twice, (
        f"the table's rows are not the {len(expected)} entries of the register at the proposal's commit "
        f"{commit[:12]}: {len(missing)} missing ({missing[:10]}), {len(extra)} not in the register ({extra[:10]}), "
        f"twice: {twice[:10]}")
    assert got == expected, "the rows are not in the register's order"


def test_every_row_has_a_domain_a_scope_a_lands_in_a_status_and_a_reason(proposal, written):
    _, register_text = written()
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


def test_an_entry_the_register_marks_superseded_is_proposed_superseded_by_its_successor(proposal, written):
    _, register_text = written()
    rows = {row["id"]: row for row in table(proposal())}
    wrong = []
    for entry_id in s.heading_ids(register_text):
        word, _ = status_word(register_text, entry_id)
        if word == "SUPERSEDED" and not rows.get(entry_id, {}).get("status", "").startswith("SUPERSEDED by DEC-"):
            wrong.append(f"{entry_id}: {rows.get(entry_id, {}).get('status')!r}")
    assert not wrong, f"entries the register marks SUPERSEDED, not proposed `SUPERSEDED by DEC-<n>`: {wrong}"


def test_every_amends_and_refines_relation_is_listed_with_the_old_entrys_status_note(proposal, written):
    _, register_text = written()
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


def test_the_sample_can_be_drawn_again_and_says_what_the_owner_checks(proposal, written):
    _, register_text = written()
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
