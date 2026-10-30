"""Builder tests for ``python3 -m gov.close.batch refresh`` (W2-68).

Regression evidence only (DEC-136): the envelope and the exit code of the incremental record load, fresh after a
record-only commit, refused with ``STORE_CODE_CHANGED`` after a code commit.
"""
from __future__ import annotations

import json
from pathlib import Path

from gov import store
from gov.close import batch

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_REL = "template/governance/kernel/schemas/test-map.schema.json"
MAP = 'version: 1\nshared_core: ["src/core/**"]\nrecord_only:\n  - "docs/close/**.md"\n'


def _refresh(root, capsys):
    code = batch.main(["refresh", "--root", str(root), "--json"])
    return code, json.loads(capsys.readouterr().out)


def _project(repo):
    repo.commit("the project", files={".gitignore": ".gov-runtime/\n", "governance/project/test-map.yaml": MAP,
                                      SCHEMA_REL: (REPO_ROOT / SCHEMA_REL).read_text(encoding="utf-8"),
                                      "src/a.py": "A = 1\n"})
    store.load(repo.root)


def test_refresh_after_a_record_only_commit_is_fresh(repo, capsys):
    _project(repo)
    head = repo.commit("a record", files={"docs/close/T/CL-1.md": "one\n"})
    code, envelope = _refresh(repo.root, capsys)
    assert code == 0 and envelope["ok"] is True and envelope["command"] == "batch"
    assert envelope["result"]["fresh"] is True
    assert envelope["result"]["load"]["head"] == head and envelope["result"]["load"]["kind"] == "records"


def test_refresh_after_a_code_commit_refuses_with_exit_1(repo, capsys):
    _project(repo)
    repo.commit("code", files={"src/a.py": "A = 2\n"})
    code, envelope = _refresh(repo.root, capsys)
    assert code == 1 and envelope["ok"] is False
    assert envelope["error"]["code"] == "STORE_CODE_CHANGED"
