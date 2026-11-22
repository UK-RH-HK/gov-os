"""W2-201 R4 (DEC-1225 (1), (4)): the memory measure's reader and grader run Sonnet.

The behavioural cases (a judged run whose stub ``claude`` records ``--model`` for a reader, a grader and a check, and
whose ``FIGURES.json`` holds ``models`` with the three, all Sonnet) are unit cases of the memory measure:
``tests/unit/memaudit/test_judge.py::test_each_call_is_the_fresh_80s_argv_with_no_tools_and_the_models_of_item_7`` and
``::test_figures_json_holds_exactly_item_10s_keys_and_counts`` (revised), with ``tests/acceptance/W2-171``'s
``test_s3_the_calls_carry_the_fresh_80s_prompts_models_budgets_and_flags`` and ``test_s6_figures_json_has_exactly_the_keys_of_item_10_and_the_planted_values``
(revised). These cases are the rest: the judge's constants, and the scan of ``src/gov/memaudit/``, the shipped briefs
and the shipped kinds file for ``claude-opus``.

Reading: ``models`` is a map of three entries (the keys name the reader, the grader and the checker; only ``reader`` and
``grader`` are pinned as keys), each ``claude-sonnet-5-5``.
"""

from __future__ import annotations

import pytest

import w2_201_support as k

REPO = k.REPO_ROOT
SHIPPED = REPO / "src/gov/_shipped/governance/project"
BRIEFS = SHIPPED / "orchestration/packages/MEMORY-AUDIT-1/briefs"
KINDS = SHIPPED / "indep-walls/kinds.yaml"


def test_r4_the_reader_the_grader_and_the_check_are_sonnet():
    from gov.memaudit import judge

    got = {"READER": judge.READER, "GRADER": judge.GRADER, "CHECK": judge.CHECK}
    assert got == {"READER": k.SONNET, "GRADER": k.SONNET, "CHECK": k.SONNET}, got


def _text_files(folder):
    return sorted(p for p in folder.rglob("*") if p.is_file() and p.suffix in (".py", ".md", ".yaml", ".yml", ".json", ".txt"))


@pytest.mark.parametrize("path", _text_files(REPO / "src/gov/memaudit"), ids=lambda p: p.name)
def test_r4_no_file_of_src_gov_memaudit_names_claude_opus(path):
    hits = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if "claude-opus" in line]
    assert not hits, f"{path.relative_to(REPO)} names claude-opus: {hits[:3]}"


@pytest.mark.parametrize("path", _text_files(BRIEFS) + [KINDS], ids=lambda p: p.name)
def test_r4_no_shipped_brief_and_no_shipped_kinds_file_names_claude_opus(path):
    hits = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if "claude-opus" in line]
    assert not hits, f"{path.relative_to(REPO)} names claude-opus: {hits[:3]}"


def test_r4_the_shipped_kinds_models_are_sonnet():
    import yaml

    data = yaml.safe_load(KINDS.read_text(encoding="utf-8"))
    models = []

    def walk(node):
        if isinstance(node, dict):
            models.extend(str(v) for key, v in node.items() if key == "model")
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(data)
    assert models and set(models) == {k.SONNET}, f"the shipped kinds file names models {sorted(set(models))}"
