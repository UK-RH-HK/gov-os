"""W2-182 failure line F1: no revised case is lowered, skipped or marked.

The ticket's failure line: "a revised case that no longer catches what it guards, or any case lowered, skipped or
marked". What a run cannot show (that each case fails on its planted break) is the reviewer's, by the README's table.
What it can show is that none of the mapped cases carries a skip, xfail, flaky or rerun mark, a call that skips or
expects a failure, or a module-level mark of the file that holds it, beyond what stood there before the revision
(BASELINE). Read from the files' source, through no internals.
"""
import ast
from collections import Counter
from pathlib import Path

from w2_182_support import ROOT, mapped_node_ids

LOWERING = {"skip", "skipif", "xfail", "flaky", "rerun", "reruns", "importorskip"}

# What stood in a mapped function before run 1 revised it (2bf4430f4), and so is not the revision's: W1-18's case has
# always skipped where ``sqlite_vec`` cannot be imported (commit 2a2738881), one ``pytest.skip`` call.
BASELINE = {
    ("tests/acceptance/W1-18/test_w1_18_on_demand_start.py",
     "test_with_the_server_not_answering_a_retrieval_answers_by_keywords_and_starts_nothing"): Counter(skip=1),
}


def lowering_names(tree: ast.AST) -> Counter:
    """How many times each skip, xfail, flaky or rerun name is used in the tree."""
    names = Counter()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in LOWERING:
            names[node.attr] += 1
        elif isinstance(node, ast.Name) and node.id in LOWERING:
            names[node.id] += 1
    return names


def mapped_functions() -> list[tuple[str, str]]:
    """(file, function) of every mapped case but this file's own."""
    found = []
    for node in mapped_node_ids():
        file, _, name = node.partition("::")
        if Path(file).name != Path(__file__).name:
            found.append((file, name.split("[")[0]))
    return list(dict.fromkeys(found))


def problems_in(source_of, functions) -> list[str]:
    """What lowers a case in ``functions`` (file, name), given ``source_of(file)``: the added marks and calls."""
    problems = []
    for file, name in functions:
        tree = ast.parse(source_of(file))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
                added = lowering_names(ast.Module(body=[node], type_ignores=[])) - BASELINE.get((file, name), Counter())
                if added:
                    problems.append(f"{file}::{name} carries {sorted(added.elements())}")
                break
        else:
            problems.append(f"{file} holds no function {name}")
        for node in tree.body:  # a module-level mark covers every case of the file
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "pytestmark"
                                                    for t in node.targets):
                marks = lowering_names(node.value)
                if marks:
                    problems.append(f"{file} has a module-level mark {sorted(marks.elements())}")
    return problems


def test_no_revised_case_is_lowered_skipped_or_marked():
    functions = mapped_functions()
    assert len(functions) >= 7, functions  # the seven revised functions of the README's map (F's two ids are one)
    problems = problems_in(lambda file: (ROOT / file).read_text(encoding="utf-8"), functions)
    assert not problems, "\n".join(problems)
