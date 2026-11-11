"""W2-129 S8 (one source of patterns) and S13 (never a gate), read from the tree under test's source.

S8: ``src/gov/links/`` reads the register's statements through the loader's ``register_statements`` and compiles no
pattern of its own for them (no regular expression naming a change verb or a change label).
S13: no module of the close, the merge queue, the landing, ``gov launch``, ``gov claim``, the readiness check or a
hook imports ``gov.links`` or runs ``gov links``. It is a guard, green today: it goes red only if a gate takes it up.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest
import w2_129_support as support

SRC = support.src_dir()
TREE = SRC.parent if (SRC.parent / "governance").is_dir() else support.WORKTREE  # a scratch src: this worktree's rest
STATEMENT_WORDS = ("supersed", "amend", "Changed by", "Changes:", "Supersedes", "replac", "withdr")
RE_CALLS = ("compile", "search", "match", "fullmatch", "findall", "finditer", "sub", "subn", "split")


def links_sources() -> list[Path]:
    package = SRC / "gov" / "links"
    files = sorted(package.rglob("*.py")) if package.is_dir() else []
    if not files or not (package / "command.py").is_file():
        pytest.fail(f"there is no gov.links package with a command module under {package}")
    return files


def pattern_literals(path: Path) -> list[str]:
    """The string literals given as the pattern of a ``re`` call in ``path``."""
    found = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in RE_CALLS \
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "re" and node.args:
            found += [n.value for n in ast.walk(node.args[0]) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    return found


def test_s8_links_reads_the_register_s_statements_through_register_statements():
    text = "\n".join(path.read_text(encoding="utf-8") for path in links_sources())
    assert "register_statements" in text


def test_s8_links_compiles_no_second_pattern_set_for_the_register_s_statements():
    own = [(path.name, literal) for path in links_sources() for literal in pattern_literals(path)
           if any(word in literal for word in STATEMENT_WORDS)]
    assert own == [], own


GATES = ("src/gov/close", "src/gov/launch", "src/gov/readiness", "src/gov/hooks", "src/gov/guard",
         "src/gov/tasks/claims.py", "src/gov/check/claims.py", "template/governance/kernel/hooks",
         "governance/project/orchestration/tools/merge_queue.py", "governance/project/orchestration/tools/dispatch",
         "lefthook.yml", "template/lefthook.yml.jinja", ".claude/settings.json", "template/.claude")
CALLS = re.compile(r"gov\.links\b|from\s+gov\s+import\s+(?:[\w, ]*\b)?links\b|\bgov\s+links\b"
                   r"|['\"]gov['\"]\s*,\s*['\"]links['\"]|main\(\s*\[\s*['\"]links['\"]")


def where(rel: str) -> Path:
    """``src/...`` in the tree under test's ``src``; the rest in its tree."""
    return SRC / rel[len("src/"):] if rel.startswith("src/") else TREE / rel


def named(path: Path) -> str:
    return "src/" + path.relative_to(SRC).as_posix() if path.is_relative_to(SRC) else path.relative_to(TREE).as_posix()


def gate_files() -> list[Path]:
    files = []
    for rel in GATES:
        path = where(rel)
        files += sorted(p for p in path.rglob("*") if p.is_file()) if path.is_dir() else [path] if path.is_file() else []
    return files


def test_s13_premise_the_gate_modules_are_there_to_read():
    names = {named(p) for p in gate_files()}
    for rel in ("src/gov/close", "src/gov/launch", "src/gov/readiness", "src/gov/tasks/claims.py",
                "governance/project/orchestration/tools/merge_queue.py", "template/governance/kernel/hooks"):
        assert any(name == rel or name.startswith(rel + "/") for name in names), rel


def test_s13_no_close_queue_landing_launch_claim_readiness_or_hook_module_calls_gov_links():
    calling = []
    for path in gate_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        calling += [f"{named(path)}: {m.group(0)}" for m in CALLS.finditer(text)]
    assert calling == [], calling
