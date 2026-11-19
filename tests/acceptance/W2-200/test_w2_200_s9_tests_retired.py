"""S9: every test that asserted the context command is retired or rewritten, and the work is listed.

A repository-state test: it reads this tree's ``tests/`` folder and this folder's README, not a fixture. It walks every
Python file under ``tests/`` outside this folder (and outside the README's "Retired" list) and fails on each of the
four patterns; it checks that each retired file is deleted and that each rewritten case carries its
``Rewrite-Reason:`` naming DEC-1214 M1.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

import w2_200_support as s

TESTS = s.REPO_ROOT / "tests"
OWN = s.HERE
README = s.HERE / "README.md"

# The four patterns of S9. A string or comment counts as much as code: a test that names the retired command, its
# library, its check family or its setting asserts it, or reads like it does. One exemption, explicit and reviewable:
# a line that itself names "DEC-1214 M1" states the retirement (a decided removal, a deny rule kept in a non-goal
# file), so it does not name the retired thing as live (README, "S9's walk").
EXEMPT_MARK = "DEC-1214 M1"
PATTERNS = {
    "imports gov.context": re.compile(r"\bgov\.context\b|\bfrom\s+gov\s+import\s+context\b"),
    "runs gov context": re.compile(
        r"\bgov\s+context\b"                                                   # the command line in text
        r"|[\"']gov\.cli\.main[\"']\s*,\s*[\"']context[\"']"                   # python -m gov.cli.main context
        r"|\b(?:\w+\.)*(?:gov|_gov|run_gov|call|main)\(\s*\[?\s*(?:[^()\n\"']*,\s*)*[\"']context[\"']\s*[,)\]]"
        r"|[\"']context[\"']\s*,\s*[\"'](?:--in-force|--json|--dry-run|--brief|--budget|--role)[\"']"
        r"|[\"']context[\"']\s*,\s*[\"'][^\"'\n]*[\"']\s*,\s*[\"']--(?:dry-run|json|brief|budget)[\"']"),
    "names context-reproducibility as a family": re.compile(r"context[-_ ]reproducibility", re.IGNORECASE),
    "reads budgets.close_context_tokens": re.compile(r"close_context_tokens"),
}


def _section_table(name: str) -> list[list[str]]:
    """The rows of the first table under the README's ``## <name>`` heading, each a list of its cells."""
    text = README.read_text(encoding="utf-8")
    hit = re.search(rf"(?m)^## {re.escape(name)}\b.*$", text)
    assert hit, f"the README has no '## {name}' section"
    rows = []
    for line in text[hit.end():].split("\n"):
        if line.startswith("## "):
            break
        if line.startswith("|") and not re.match(r"\|\s*-", line):
            rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    assert len(rows) > 1, f"the README's '## {name}' section holds no table rows"
    return rows[1:]   # without the header row


def _spans(cell: str) -> list[str]:
    return re.findall(r"`([^`]+)`", cell)


def retired_paths() -> list[str]:
    return [span for row in _section_table("Retired") for span in _spans(row[0])]


def rewritten_cases() -> list[str]:
    return [span for row in _section_table("Rewritten") for span in _spans(row[0]) if "::" in span]


def _hits(pattern: re.Pattern) -> list[str]:
    exempt = {str((s.REPO_ROOT / rel).resolve()) for rel in retired_paths()}
    found = []
    for path in sorted(TESTS.rglob("*.py")):
        if OWN in path.resolve().parents or str(path.resolve()) in exempt or "__pycache__" in path.parts:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if pattern.search(line) and EXEMPT_MARK not in line:
                found.append(f"{path.relative_to(s.REPO_ROOT)}:{number}: {line.strip()[:140]}")
    return found


@pytest.mark.parametrize("what", list(PATTERNS))
def test_s9_no_test_file_outside_w2_200_matches_a_retired_pattern(what):
    found = _hits(PATTERNS[what])
    assert not found, f"{len(found)} lines {what}:\n" + "\n".join(found[:60])


def test_s9_every_retired_file_listed_is_deleted():
    paths = retired_paths()
    assert paths, "the README lists no retired file"
    left = [rel for rel in paths if (s.REPO_ROOT / rel).exists()]
    assert not left, f"files listed as retired still exist: {left}"


def _docstring(path: Path, name: str) -> str | None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.get_docstring(node) or ""
    return None


def test_s9_every_rewritten_case_listed_carries_its_rewrite_reason():
    cases = rewritten_cases()
    assert cases, "the README lists no rewritten case"
    wrong = []
    for case in cases:
        rel, _, name = case.partition("::")
        name = name.split("::")[-1].split("[")[0]
        path = s.REPO_ROOT / rel
        if not path.is_file():
            wrong.append(f"{case}: no such file")
            continue
        doc = _docstring(path, name)
        if doc is None:
            wrong.append(f"{case}: no such test function")
        elif not re.search(r"Rewrite-Reason:.*DEC-1214 M1", doc, flags=re.DOTALL):
            wrong.append(f"{case}: its docstring has no 'Rewrite-Reason:' naming DEC-1214 M1")
    assert not wrong, "\n".join(wrong)
