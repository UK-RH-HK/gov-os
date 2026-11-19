"""W2-201 F3: a role file with a missing or malformed line still fails its check, and a table line whose C0 or C1
entry is missing is refused by the reader as before.

The launcher's role reader (``gov.launch.role``) on this repository's kernel engineer file (S1's table line), planted
in a temporary tree with one line taken out or broken: each is refused with ``LAUNCH_REFUSED`` naming the file. The
Verify's own cases are W2-33's F2 (``tests/acceptance/W2-33/test_w2_33_planted.py``) and W2-184's line cases
(``test_w2_184_s1_table.py``, ``test_w2_184_s1_no_criticality_file.py``); these are guards beside them.
"""

from __future__ import annotations

import re

import pytest

import w2_201_support as k

ROLE = k.ENGINEER
DEFAULT_HEAD, TABLE_HEAD = "- **Launch default:**", "- **Launch by criticality:**"


def _drop_entry(cls):
    return lambda line: re.sub(rf"; {cls} [^;]*" if cls != "C3" else r" C3 [^;]*;", "", line, count=1)


BREAKS = {
    "default-line-missing": (DEFAULT_HEAD, None),
    "default-line-without-comma": (DEFAULT_HEAD, lambda line: line.replace(", effort", " effort")),
    "default-line-twice": (DEFAULT_HEAD, lambda line: line + "\n" + line),
    "table-c0-missing": (TABLE_HEAD, _drop_entry("C0")),
    "table-c1-missing": (TABLE_HEAD, _drop_entry("C1")),
}


def _broken(tmp_path, case):
    head, change = BREAKS[case]
    tree = k.plant_role_copy(tmp_path, k.ROLES_REL, ROLE)
    path = tree / k.ROLES_REL / f"{ROLE}.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    index = next((i for i, line in enumerate(lines) if line.startswith(head)), None)
    assert index is not None, f"the kernel {ROLE}.md has no line '{head}' to break"
    if change is None:
        del lines[index]
    else:
        new = change(lines[index])
        assert new != lines[index], f"the break {case} changed nothing in {lines[index]!r}"
        lines[index] = new
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return tree


@pytest.mark.parametrize("case", sorted(BREAKS))
def test_f3_a_missing_or_malformed_line_is_refused_by_the_role_reader(tmp_path, case):
    from gov.cli.errors import GovError
    from gov.launch import role as reader

    tree = _broken(tmp_path, case)
    read = reader.launch_default if BREAKS[case][0] == DEFAULT_HEAD else reader.read_by_criticality
    with pytest.raises(GovError) as raised:
        read(tree, ROLE)
    assert raised.value.code == "LAUNCH_REFUSED", raised.value.code
    assert f"{ROLE}.md" in raised.value.message, f"the refusal does not name {ROLE}.md: {raised.value.message}"
