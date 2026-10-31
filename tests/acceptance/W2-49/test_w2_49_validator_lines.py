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
own output.  No test needs any other item to move, or fixes its wave.
"""

from __future__ import annotations

import re

import pytest

from w2_49_support import (
    CHECK_APPLIED,
    CHECK_MOVED,
    CONTRACT_YAML,
    MOVED_ITEMS,
    ROOT,
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
    checks, output = run_validator(ROOT)
    assert_pass(checks, output, CHECK_MOVED)
    assert_pass(checks, output, CHECK_APPLIED)


def test_a_tree_of_the_validators_inputs_alone_passes_both_cit_p_checks(tmp_path, inputs):
    """The control: the files the two checks read, copied as they are, pass both (the failing cases differ by one change)."""
    checks, output = run_validator(build(tmp_path, inputs))
    assert_pass(checks, output, CHECK_MOVED)
    assert_pass(checks, output, CHECK_APPLIED)


# --------------------------------------------------------------------------
# The failure line, and the accounting of the three items and the six lines


@pytest.mark.parametrize("cid", MOVED_ITEMS)
def test_an_item_moved_to_wave_2_without_its_cit_p_line_fails_naming_it(tmp_path, inputs, cid):
    """Failure (i): a Contract item moved to Wave 2 with no CIT-P line makes cit-p-moved-items fail, naming it."""
    files, dropped = dict(inputs), 0
    for rel in cit_p_files():
        files[rel], n = drop_cit_p_line(files[rel], cid)
        dropped += n
    assert dropped >= 1, f"no CIT-P in this tree has a line for {cid}: the moved item has no line to remove"
    checks, output = run_validator(build(tmp_path, files))
    others = [o for o in MOVED_ITEMS if o != cid]
    assert_fails_naming(checks, output, CHECK_MOVED, cid, others)
    assert_pass(checks, output, CHECK_APPLIED)


@pytest.mark.parametrize("cid", sorted(CIT_P_LINES))
def test_a_cit_p_line_with_no_change_in_the_contract_fails_naming_it(tmp_path, inputs, cid):
    """Failure (ii): a CIT-P line whose change the Contract lacks makes cit-p-lines-applied fail, naming its id."""
    wave = CIT_P_LINES[cid]
    files = dict(inputs)
    files[CONTRACT_YAML], changed = undo_in_contract(inputs[CONTRACT_YAML], cid, wave)
    assert changed == 1, f"contract.yaml: {changed} changes made to undo {cid} (wave {wave}); expected exactly one"
    checks, output = run_validator(build(tmp_path, files))
    others = [o for o in CIT_P_LINES if o != cid]
    assert_fails_naming(checks, output, CHECK_APPLIED, cid, others)
    assert_pass(checks, output, CHECK_MOVED)


def test_a_cit_p_line_for_an_item_the_contract_does_not_change_fails_naming_it(tmp_path, inputs):
    """Failure (ii), edge: a CIT-P line the Contract never applied (CAP-45.a to W3; it is W2) fails, naming it."""
    files = dict(inputs)
    rel = "docs/changes/W2-49-CIT-P.md"
    assert rel in files, f"{rel} is not in this tree"
    files[rel] = inputs[rel] + "\n```yaml\n  - id: CAP-45.a\n    wave: W3\n```\n"
    checks, output = run_validator(build(tmp_path, files))
    assert_fails_naming(checks, output, CHECK_APPLIED, "CAP-45.a", list(CIT_P_LINES))
    assert_pass(checks, output, CHECK_MOVED)
