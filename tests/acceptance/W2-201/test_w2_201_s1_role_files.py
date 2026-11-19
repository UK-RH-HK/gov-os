"""W2-201 S1: the role files carry the rubric (audit 4 Table 3 with DEC-1212 (3) and DEC-1214 K1).

Every role file, in the kernel folder and in each generated copy (``.rulesync/subagents``,
``template/.rulesync/subagents``, ``.claude/agents``), is read with the launcher's role reader (``gov.launch.role``:
``launch_default`` for the ``Launch default`` line, ``read_by_criticality`` for the ``Launch by criticality`` line), the
copy planted alone where the reader reads a role file; the model and effort per class, on a FULL ticket and otherwise,
must equal S1's table (``w2_201_support.TABLE``). A copy that differs from it, so from the kernel file, fails.
"""

from __future__ import annotations

import pytest

import w2_201_support as k

CASES = [pytest.param(role, location, id=f"{role}::{location}") for role in k.TABLE for location in k.LOCATIONS]


def _per_class(default, table):
    """``{(class, "full" | "other"): (model, effort)}``: the table's entry where there is a table, else the default."""
    out = {}
    for cls in k.CLASSES:
        for key in ("full", "other"):
            out[(cls, key)] = tuple(table[cls][key]) if table is not None else tuple(default)
    return out


@pytest.mark.parametrize("role, location", CASES)
def test_s1_each_role_file_and_copy_gives_the_table_s_model_and_effort_per_class(tmp_path, role, location):
    from gov.launch import role as reader

    tree = k.plant_role_copy(tmp_path, location, role)
    default = tuple(reader.launch_default(tree, role))
    table = reader.read_by_criticality(tree, role)
    want_default, want_table = k.TABLE[role]
    got = {"Launch default": default, "Launch by criticality": None if table is None else "present"}
    want = {"Launch default": want_default, "Launch by criticality": None if want_table is None else "present"}
    assert got == want, (f"{location}/{role}.md: S1 gives Launch default {want_default} and "
                         f"{'a' if want_table else 'no'} Launch by criticality line; the reader reads {got}")
    expected = {(cls, key): want_table[cls] for cls in k.CLASSES for key in ("full", "other")} if want_table \
        else _per_class(want_default, None)
    assert _per_class(default, table) == expected, (
        f"{location}/{role}.md: the model and effort per class (FULL and otherwise) differ from S1's table:\n"
        f"expected {expected}\ngot      {_per_class(default, table)}")


def test_s1_the_kernel_folder_holds_the_nine_roles_of_the_table():
    """Guard: the table names every kernel role file, so no role file escapes the case above."""
    names = sorted(p.stem for p in (k.REPO_ROOT / k.ROLES_REL).glob("*.md") if p.name.lower() != "readme.md")
    assert names == sorted(k.TABLE), f"the kernel role files are {names}; S1's table names {sorted(k.TABLE)}"
