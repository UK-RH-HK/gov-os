"""W2-174 F3: the verify pass reads and writes only ``<repo>/.tickets/`` and the answers file; no network, no model."""
from __future__ import annotations

import ast
import datetime

from .test_w2_174_support import DONE, REPO, answers_file, gov_json, repo_with, snapshot, ticket

from gov.adopt import verify_pass

FORBIDDEN = {"socket", "http", "urllib", "requests", "httpx", "anthropic", "openai", "subprocess"}


def test_decoys_outside_the_tickets_folder_are_byte_identical_after_list_and_apply(tmp_path):
    root = repo_with(tmp_path, {"DAEO-a1": ticket("DAEO-a1", success=["one", DONE])})
    for rel in ("README.md", "src/mod.py", "governance/project/facts.yaml", "docs/ticket-copy.md", ".gov-runtime/x.json"):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(f"decoy {rel}\n", encoding="utf-8")
    (root / ".tickets/notes.txt").write_text("not a ticket\n", encoding="utf-8")
    (root / ".tickets/DAEO-a1.md.bak").write_text("a backup\n", encoding="utf-8")
    answers = answers_file(tmp_path, {"DAEO-a1": {"S1": "clause"}})
    before = snapshot(root)
    answers_before = answers.read_bytes()
    gov_json("adopt", "--verify-list", "--root", str(root))
    assert snapshot(root) == before
    gov_json("adopt", "--verify-apply", str(answers), "--root", str(root), "--session", "s")
    after = snapshot(root)
    assert {name for name in after if after.get(name) != before.get(name)} == {".tickets/DAEO-a1.md"}
    assert set(after) == set(before)  # no temporary or other file left anywhere
    assert answers.read_bytes() == answers_before


def test_the_module_imports_no_network_or_model_package():
    tree = ast.parse((REPO / "src/gov/adopt/verify_pass.py").read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported and not imported & FORBIDDEN, imported & FORBIDDEN
    assert imported <= {"__future__", "datetime", "os", "re", "pathlib", "yaml", "gov"}, imported


def test_the_module_opens_no_path_but_a_ticket_or_the_answers_file(tmp_path):
    root = repo_with(tmp_path, {"DAEO-a1": ticket("DAEO-a1", success=["one"])})
    (root / "outside.txt").write_text("outside\n", encoding="utf-8")
    opened = []
    import pathlib

    original_open = pathlib.Path.open
    answers = answers_file(tmp_path, {"DAEO-a1": {"S1": "clause"}})

    def spy(self, *args, **kwargs):
        opened.append(str(self))
        return original_open(self, *args, **kwargs)

    pathlib.Path.open = spy
    try:
        verify_pass.missing(root)
        verify_pass.apply(root, answers, "s", datetime.date(2026, 11, 13))
    finally:
        pathlib.Path.open = original_open
    assert opened  # the spy saw the reads and the writes
    assert all(path.startswith(str(root / ".tickets")) or path == str(answers) for path in opened), opened
