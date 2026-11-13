"""Judging for S19 and S20: the variants differ from the Gov OS briefs only in the domain table and the blind list (a diff
test), and ``src/gov/adopt/`` holds no second copy of the pre-flight, the use-once marker or the figures (an AST test).
Both are functions, so a bite check can feed each a good and a bad input."""

from __future__ import annotations

import ast
import difflib
import re
from pathlib import Path

import w2_88_support as W

GOV_BRIEFS = W.REPO_ROOT / "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs"
KINDS = ("writer", "checker", "auditor")
# S20: the names of a pre-flight, a use-once marker and the figures (gov.memaudit's own are preflight.*, declare's
# ``_write_used``/``is_used``, figures.*): any def or assignment in src/gov/adopt/ whose name holds one of these words.
FORBIDDEN_WORD = re.compile(r"(?i)(pre_?flight|used|figure)")


def _first(lines, start, pred):
    for number in range(start, len(lines)):
        if pred(lines[number]):
            return number
    return len(lines)


def allowed_regions(kind: str, text: str) -> list[tuple[int, int]]:
    """Base line ranges (start inclusive, end exclusive) the variant may change: the blind list (§4, "What you must never
    read"), and the domain table: the writer's §5 items 1 and 3, the checker's §5a. The auditor's has the blind list only."""
    lines = text.splitlines()
    regions = []
    blind = _first(lines, 0, lambda l: l.startswith("## ") and "never read" in l)
    if blind < len(lines):
        regions.append((blind + 1, _first(lines, blind + 1, lambda l: l.startswith("## "))))
    if kind == "writer":
        one = _first(lines, 0, lambda l: l.startswith("1. **Size and categories"))
        regions.append((one, _first(lines, one + 1, lambda l: l.startswith("2. **"))))
        three = _first(lines, 0, lambda l: l.startswith("3. **The set"))
        regions.append((three, _first(lines, three + 1, lambda l: l.startswith("4. **"))))
    if kind == "checker":
        five_a = _first(lines, 0, lambda l: l.startswith("### 5a"))
        regions.append((five_a, _first(lines, five_a + 1, lambda l: l.startswith("## "))))
    return [r for r in regions if r[0] < len(lines)]


def diff_outside(kind: str, base: str, variant: str) -> list[str]:
    """The hunks of ``variant`` against ``base`` that touch a line outside the allowed regions (empty: none)."""
    base_lines, variant_lines = base.splitlines(), variant.splitlines()
    regions = allowed_regions(kind, base)
    bad = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, base_lines, variant_lines, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        inside = any(start <= i1 and max(i2, i1) <= end for start, end in regions)
        if not inside:
            bad.append(f"{tag} base lines {i1 + 1}-{i2}: {' | '.join(base_lines[i1:i2])[:80]!r}")
    return bad


def gov_brief(kind: str) -> str:
    return (GOV_BRIEFS / f"{kind}.md").read_text(encoding="utf-8")


def variant_files(folder: Path) -> dict:
    """``{kind: path}`` of the three variant briefs under ``folder`` (the file name holds the role's word)."""
    found = {}
    for path in sorted(Path(folder).rglob("*")):
        if path.is_file():
            for kind in KINDS:
                if kind in path.name.lower():
                    found.setdefault(kind, path)
    return found


def second_copies(source: str, filename: str) -> list[str]:
    """Names defined (def, class or assignment) in ``source`` that hold the pre-flight, use-once or figures words, outside
    an import from ``gov.memaudit``. The module's imports from ``gov.memaudit`` are never a definition."""
    tree = ast.parse(source, filename=filename)
    bad = []
    for node in ast.walk(tree):
        names = []
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names = [node.name]
        elif isinstance(node, ast.Assign):
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)) and isinstance(node.target, ast.Name):
            names = [node.target.id]
        bad += [f"{filename}:{node.lineno} defines {name}" for name in names if FORBIDDEN_WORD.search(name)]
    return bad


def imports_from_memaudit(source: str) -> bool:
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[:2] == ["gov", "memaudit"]:
            return True
        if isinstance(node, ast.Import) and any(a.name.split(".")[:2] == ["gov", "memaudit"] for a in node.names):
            return True
    return False
