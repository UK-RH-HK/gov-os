"""The product-traceability check without a record store (W2-L175): a decision of the register the path map names
resolves. Builder tests: regression evidence only (MR-3)."""
from __future__ import annotations

import json

from gov.close import history, traceability

TICKET = "T-0001"
REGISTER = "docs/DECISION_REGISTER.md"


def _project(repo, implements):
    repo.commit("the project", files={
        history.PATH_MAP_REL: f"namespaces: {{}}\n{history.REGISTER_KEY}: {REGISTER}\n",
        REGISTER: "# Decision register\n\n### DEC-900 — A decision\n- **Status:** ACCEPTED (owner, 2026-10-16)\n",
        f".tickets/{TICKET}.md": f"---\nid: {TICKET}\nstatus: closed\n---\n# A ticket\n"})
    repo.commit("work", f"Task: {TICKET}", "Role: engineer", f"Implements: {implements}", files={"a.txt": "a\n"})


def _run(repo, monkeypatch, capsys):
    monkeypatch.chdir(repo.root)
    code = traceability.main()
    return code, json.loads(capsys.readouterr().out)


def test_a_decision_of_the_register_resolves_without_a_store(repo, monkeypatch, capsys):
    _project(repo, "DEC-900")
    code, answer = _run(repo, monkeypatch, capsys)
    assert code == 0 and answer["findings"] == []


def test_an_id_the_register_does_not_hold_still_does_not_resolve(repo, monkeypatch, capsys):
    _project(repo, "DEC-901")
    code, answer = _run(repo, monkeypatch, capsys)
    assert code == 1 and [f["code"] for f in answer["findings"]] == ["IMPLEMENTS_UNRESOLVED"]
