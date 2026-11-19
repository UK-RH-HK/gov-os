"""KPI success line 3 and the failure line: the plan validator's two-way check covers the moved parts (DEC-744).

W2-51's Wave 2 plan validator (``docs/plan/tools/validate_w2.py``) is the
public tool.  Only its two CIT-P checks are this ticket's: ``cit-p-moved-items``
(every item moved to Wave 2 has a CIT-P line) and ``cit-p-lines-applied``
(every CIT-P line has its change in the Contract).  Its other checks judge the
whole plan, so the tests read those two lines of its output, never its exit.

- Line 3, on this tree: both checks pass.
- The failure line, on a temporary tree built from the single files the two
  checks read (the WBS, ``contract.yaml``, every ``*-CIT-P.md``): the tree as
  copied passes both, and each failing case changes one thing in it.

The accounting: each of the three items moved to Wave 2, lite, made to lose
its CIT-P line, is named by ``cit-p-moved-items``; each of the six CIT-P lines,
made to lose its change in the Contract, is named by ``cit-p-lines-applied``.
So the passing checks cover exactly these items and lines, by the validator's
own output.

Contract v5 (DEC-1219): the re-baseline moved 36 more items to Wave 2, and a CIT-P line per move is the ceremony EMERGENCY-2
retires.  The validator takes the re-baseline as a second baseline: ``docs/plan/WAVE_2_WBS.md`` carries, in the same section 1
block as "The Contract's N Wave 2 items, by ticket.", a line ``**Contract v5 re-baseline moves to Wave 2 (DEC-1214,
DEC-1219):**`` and ``- CAP-x.y, CAP-z.w -> W2-nnn.`` bullets; an item named there is not "moved" (evidence:
``docs/emergency-2/audits/07-contract-rebaseline.md``).  The cases that need that behaviour build their tree from the
validator's input files and set the block themselves, so they do not depend on the real WBS's own block.
"""

from __future__ import annotations

import re

import pytest
import yaml

from w2_49_support import (
    CHECK_APPLIED,
    CHECK_MOVED,
    CONTRACT_YAML,
    MOVED_ITEMS,
    ROOT,
    WBS,
    cit_p_files,
    names_id,
    run_validator,
    validator_inputs,
)

# The six CIT-P lines of W2-49 (CIT-P §6.1, DEC-741 A (a1)), each with its wave.
CIT_P_LINES = {
    "CAP-43.b": "W2",
    "CAP-44.f": "W2",
    "CAP-44.h": "W2",
    "CAP-43.d": "W3",
    "CAP-44.k": "W3",
    "CAP-44.l": "W3",
}


@pytest.fixture(scope="module")
def inputs():
    files = validator_inputs()
    missing = [rel for rel in files if not (ROOT / rel).is_file()]
    assert not missing, f"the validator's inputs are missing from this tree: {missing}"
    return {rel: (ROOT / rel).read_text(encoding="utf-8") for rel in files}


def build(tmp_path, files):
    for rel, text in files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return tmp_path


def check(checks, output, name):
    assert name in checks, f"the validator printed no {name} line:\n{output}"
    return checks[name]


def assert_pass(checks, output, name):
    status, reason = check(checks, output, name)
    assert status == "PASS", f"{name} is {status}: {reason}"


def assert_fails_naming(checks, output, name, cid, others):
    status, reason = check(checks, output, name)
    assert status == "FAIL", f"{name} is {status} ({reason}), but the tree breaks it for {cid}"
    assert names_id(reason, cid), f"{name} fails without naming {cid}: {reason}"
    named = [o for o in others if names_id(reason, o)]
    assert not named, f"{name} also names {named}, which the one change did not touch: {reason}"


# --------------------------------------------------------------------------
# Changing one thing in a copied input


def drop_cit_p_line(text: str, cid: str) -> tuple[str, int]:
    """Remove the ``wave:`` of every ``- id: <cid>`` entry in a ```yaml block: the entry is then no CIT-P line."""
    out, dropped, in_yaml, current = [], 0, False, None
    for line in text.splitlines(keepends=True):
        if line.startswith("```"):
            in_yaml, current = line.strip() == "```yaml", None
        elif in_yaml and (m := re.match(r"^\s*- id: (CAP-\d+\.[a-z]+)\b", line)):
            current = m.group(1)
        elif in_yaml and current == cid and re.match(r"^\s*wave: \S+\s*$", line):
            dropped += 1
            current = None
            continue
        out.append(line)
    return "".join(out), dropped


REBASELINE_HEADER = "**Contract v5 re-baseline moves to Wave 2 (DEC-1214, DEC-1219):**"
BASELINE_HEADER = re.compile(r"^\*\*The Contract's \d+ Wave 2 items, by ticket\.\*\*")
CAP_ID = re.compile(r"CAP-\d+(?:\.[a-z]+)?")


def covers_waves(files) -> dict[str, str]:
    doc = yaml.safe_load(files[CONTRACT_YAML])
    return {c["id"]: c.get("wave") for cap in doc["capabilities"] for c in cap.get("covers") or []}


def old_baseline(files) -> set[str]:
    """The ids of the bullets under "The Contract's N Wave 2 items, by ticket." in the WBS."""
    found, inside = set(), False
    for line in files[WBS].splitlines():
        if BASELINE_HEADER.match(line):
            inside = True
        elif inside and line.startswith("- "):
            found |= set(CAP_ID.findall(line))
        else:
            inside = False
    return found


def cit_p_wave_2(files) -> set[str]:
    """The ids a CIT-P line moves to W2 (an entry of a ```yaml block with ``wave: W2``)."""
    found = set()
    for rel in cit_p_files():
        in_yaml, current = False, None
        for line in files[rel].splitlines():
            if line.startswith("```"):
                in_yaml, current = line.strip() == "```yaml", None
            elif in_yaml and (m := re.match(r"^\s*- id: (CAP-\d+\.[a-z]+)\b", line)):
                current = m.group(1)
            elif in_yaml and current and (m := re.match(r"^\s*wave: (\S+)\s*$", line)):
                if m.group(1) == "W2":
                    found.add(current)
                current = None
    return found


def rebaseline_moves(files) -> list[str]:
    """What a re-baseline line has to name for the tree's Wave 2 items to be accounted for: every item W2 in contract.yaml
    that is in neither the old baseline nor a CIT-P line (the 36 of audit 7, on this tree)."""
    waves = covers_waves(files)
    return sorted(i for i, w in waves.items() if w == "W2" and i not in old_baseline(files) and i not in cit_p_wave_2(files))


def with_rebaseline(files, names):
    """A copy of ``files`` whose WBS carries exactly one re-baseline block naming ``names`` (none: no block), in the section 1
    block of the baseline list, replacing any block the file has."""
    out, skipping, placed, lines = [], False, False, files[WBS].splitlines(keepends=True)
    kept = []
    for line in lines:
        if line.startswith("**Contract v5 re-baseline moves"):
            skipping = True
        elif skipping and line.startswith("- "):
            pass
        else:
            skipping = False
            kept.append(line)
    names = list(names)
    block = []
    if names:
        block = ["\n", REBASELINE_HEADER + "\n"] + [f"- {', '.join(names[i:i + 4])} \u2192 W2-17.\n" for i in range(0, len(names), 4)]
    inside = False
    for n, line in enumerate(kept):
        out.append(line)
        if BASELINE_HEADER.match(line):
            inside = True
        elif inside and not line.startswith("- "):
            inside = False
        if inside and not placed and (n + 1 >= len(kept) or not kept[n + 1].startswith("- ")):
            out.extend(block)
            placed = True
    assert placed, "the WBS has no baseline block to put the re-baseline line after"
    return {**files, WBS: "".join(out)}


def set_wave(text: str, cid: str, wave: str) -> tuple[str, int]:
    """Set the ``wave:`` of the one covers entry ``- id: <cid>`` of contract.yaml; returns the text and the lines changed."""
    lines = text.splitlines(keepends=True)
    out, changed, i = [], 0, 0
    while i < len(lines):
        m = re.match(r"^(\s*)- id: (\S+)\s*$", lines[i])
        if not (m and m.group(2) == cid):
            out.append(lines[i])
            i += 1
            continue
        indent, j = len(m.group(1)), i + 1
        while j < len(lines) and (not lines[j].strip() or len(lines[j]) - len(lines[j].lstrip()) > indent):
            j += 1
        for line in lines[i:j]:
            new = re.sub(r"^(\s*wave:) \S+(\s*)$", rf"\1 {wave}\2", line)
            changed += new != line
            out.append(new)
        i = j
    return "".join(out), changed


def undo_in_contract(text: str, cid: str, wave: str) -> tuple[str, int]:
    """Take one CIT-P line's change out of contract.yaml, back to the Contract before it.

    A line moving an item to W2 has the item put back in W3 (its wave in 4.1); a
    line adding a W3 split item has the item removed (4.1 has no such item).
    """
    lines = text.splitlines(keepends=True)
    out, changed, i = [], 0, 0
    while i < len(lines):
        m = re.match(r"^(\s*)- id: (\S+)\s*$", lines[i])
        if not (m and m.group(2) == cid):
            out.append(lines[i])
            i += 1
            continue
        indent = len(m.group(1))
        j = i + 1
        while j < len(lines) and (not lines[j].strip() or len(lines[j]) - len(lines[j].lstrip()) > indent):
            j += 1
        entry = lines[i:j]
        if wave == "W2":
            entry = [re.sub(r"^(\s*wave:) W2(\s*)$", r"\1 W3\2", l) for l in entry]
            changed += sum(1 for a, b in zip(lines[i:j], entry) if a != b)
            out.extend(entry)
        else:
            changed += 1
        i = j
    return "".join(out), changed


# --------------------------------------------------------------------------
# Line 3: on this ticket's tree


def test_validator_passes_both_cit_p_checks_on_this_tree():
    """Line 3 (DEC-744): on this tree, cit-p-moved-items and cit-p-lines-applied pass."""
    # DEC-1219: unchanged. It passes once docs/plan/WAVE_2_WBS.md carries the re-baseline line and the validator reads it as a
    # second baseline; until then the 36 items Contract v5 moved to Wave 2 are reported by cit-p-moved-items.
    checks, output = run_validator(ROOT)
    assert_pass(checks, output, CHECK_MOVED)
    assert_pass(checks, output, CHECK_APPLIED)


def test_a_tree_of_the_validators_inputs_alone_passes_both_cit_p_checks(tmp_path, inputs):
    """The control: the files the two checks read, copied as they are, pass both (the failing cases differ by one change)."""
    # DEC-1219: unchanged; it passes on the same condition as the test on this tree.
    checks, output = run_validator(build(tmp_path, inputs))
    assert_pass(checks, output, CHECK_MOVED)
    assert_pass(checks, output, CHECK_APPLIED)


# --------------------------------------------------------------------------
# Contract v5 (DEC-1219): the re-baseline line is a second baseline


def test_a_rebaseline_line_naming_the_items_contract_v5_moved_to_wave_2_passes_both_checks(tmp_path, inputs):
    """DEC-1219 (b): items W2 in contract.yaml and named by the WBS's `Contract v5 re-baseline moves` bullets are not reported."""
    names = rebaseline_moves(inputs)
    assert names, "the premise fails: contract.yaml has no item moved to W2 outside the old baseline and the CIT-P lines"
    checks, output = run_validator(build(tmp_path, with_rebaseline(inputs, names)))
    assert_pass(checks, output, CHECK_MOVED)
    assert_pass(checks, output, CHECK_APPLIED)


def test_an_item_the_rebaseline_line_omits_is_reported_and_the_ones_it_names_are_not(tmp_path, inputs):
    """DEC-1219 (b): the same line without CAP-15.a (W2 in contract.yaml, not in the baseline or a CIT-P line) fails the check
    naming CAP-15.a alone; the items the line still names are not reported."""
    omitted = "CAP-15.a"
    names = rebaseline_moves(inputs)
    assert omitted in names, f"the premise fails: {omitted} is not a Wave 2 item outside the baseline and the CIT-P lines"
    named = [n for n in names if n != omitted]
    checks, output = run_validator(build(tmp_path, with_rebaseline(inputs, named)))
    assert_fails_naming(checks, output, CHECK_MOVED, omitted, named)
    assert_pass(checks, output, CHECK_APPLIED)


STILL_W3 = "CAP-02.c"  # the signed release tag: W3 in contract.yaml (CAP-33's re-baseline keeps it for friction), no CIT-P line


def test_an_item_moved_to_wave_2_in_no_baseline_and_no_cit_p_line_fails_naming_it(tmp_path, inputs):
    """DEC-1219 (c): with the re-baseline line complete, contract.yaml moving a W3 item (CAP-02.c) to W2 makes
    cit-p-moved-items fail, naming it and no item of the baseline, the re-baseline line or the CIT-P lines."""
    waves = covers_waves(inputs)
    assert waves.get(STILL_W3) == "W3", f"the premise fails: {STILL_W3} is {waves.get(STILL_W3)!r} in contract.yaml, not W3"
    names = rebaseline_moves(inputs)
    assert STILL_W3 not in names, f"the premise fails: {STILL_W3} is in the re-baseline names"
    assert STILL_W3 not in cit_p_wave_2(inputs) and STILL_W3 not in old_baseline(inputs), f"the premise fails: {STILL_W3} is covered already"
    files = with_rebaseline(inputs, names)
    files[CONTRACT_YAML], changed = set_wave(inputs[CONTRACT_YAML], STILL_W3, "W2")
    assert changed == 1, f"contract.yaml: {changed} wave lines changed for {STILL_W3}; expected exactly one"
    checks, output = run_validator(build(tmp_path, files))
    assert_fails_naming(checks, output, CHECK_MOVED, STILL_W3, [*names, *sorted(old_baseline(inputs)), *sorted(cit_p_wave_2(inputs))])


# --------------------------------------------------------------------------
# The failure line, and the accounting of the three items and the six lines


@pytest.mark.parametrize("cid", MOVED_ITEMS)
def test_an_item_moved_to_wave_2_without_its_cit_p_line_fails_naming_it(tmp_path, inputs, cid):
    """Failure (i): a Contract item moved to Wave 2 with no CIT-P line makes cit-p-moved-items fail, naming it."""
    # DEC-1219: the tree carries a re-baseline line of the tree's own making (the items outside the baseline and the CIT-P
    # lines, as the tree stood before the line was removed), so the case does not depend on whether the real WBS's line
    # names CAP-43.b, CAP-44.f or CAP-44.h too.
    names = rebaseline_moves(inputs)
    assert cid not in names, f"the premise fails: {cid} has a CIT-P line, so the re-baseline line does not name it"
    files, dropped = dict(inputs), 0
    for rel in cit_p_files():
        files[rel], n = drop_cit_p_line(files[rel], cid)
        dropped += n
    assert dropped >= 1, f"no CIT-P in this tree has a line for {cid}: the moved item has no line to remove"
    checks, output = run_validator(build(tmp_path, with_rebaseline(files, names)))
    others = [o for o in MOVED_ITEMS if o != cid] + names
    assert_fails_naming(checks, output, CHECK_MOVED, cid, others)
    assert_pass(checks, output, CHECK_APPLIED)


@pytest.mark.parametrize("cid", sorted(CIT_P_LINES))
def test_a_cit_p_line_with_no_change_in_the_contract_fails_naming_it(tmp_path, inputs, cid):
    """Failure (ii): a CIT-P line whose change the Contract lacks makes cit-p-lines-applied fail, naming its id."""
    # Rewrite-Reason: DEC-1219 (the owner's approval of Contract v5 on 2026-11-19): the tree carries the re-baseline line
    # (as the tree's own), so cit-p-moved-items passes once the validator reads it, and the case judges one thing.
    wave = CIT_P_LINES[cid]
    files = with_rebaseline(inputs, rebaseline_moves(inputs))
    files[CONTRACT_YAML], changed = undo_in_contract(inputs[CONTRACT_YAML], cid, wave)
    assert changed == 1, f"contract.yaml: {changed} changes made to undo {cid} (wave {wave}); expected exactly one"
    checks, output = run_validator(build(tmp_path, files))
    others = [o for o in CIT_P_LINES if o != cid]
    assert_fails_naming(checks, output, CHECK_APPLIED, cid, others)
    assert_pass(checks, output, CHECK_MOVED)


# An item that is W2 in contract.yaml and in the old baseline of the WBS, and that Contract v5 leaves as it was (audit 7: kept).
STAYS_W2 = "CAP-10.b"


def test_a_cit_p_line_for_an_item_the_contract_does_not_change_fails_naming_it(tmp_path, inputs):
    """Failure (ii), edge: a CIT-P line the Contract never applied (CAP-10.b to W3; it is W2) fails, naming it."""
    # Rewrite-Reason: DEC-1219 (the owner's approval of Contract v5 on 2026-11-19): the edge case was built on CAP-61.f staying
    # W2, which v5 dropped (it is NONE). Rebuilt on CAP-10.b, W2 in contract.yaml and in the WBS's baseline list (both checked
    # first), with the same expectations; the tree carries the re-baseline line so the moved check judges nothing else.
    assert covers_waves(inputs).get(STAYS_W2) == "W2", f"the premise fails: {STAYS_W2} is not W2 in contract.yaml"
    assert STAYS_W2 in old_baseline(inputs), f"the premise fails: {STAYS_W2} is not in the WBS's baseline list"
    assert STAYS_W2 not in cit_p_wave_2(inputs), f"the premise fails: a CIT-P line already moves {STAYS_W2}"
    files = with_rebaseline(inputs, rebaseline_moves(inputs))
    rel = "docs/changes/W2-49-CIT-P.md"
    assert rel in files, f"{rel} is not in this tree"
    files[rel] = inputs[rel] + f"\n```yaml\n  - id: {STAYS_W2}\n    wave: W3\n```\n"
    checks, output = run_validator(build(tmp_path, files))
    assert_fails_naming(checks, output, CHECK_APPLIED, STAYS_W2, list(CIT_P_LINES))
    assert_pass(checks, output, CHECK_MOVED)
