"""Builder tests for the two fingerprints of a commit (W2-68, ``gov.close.fingerprint``).

Regression evidence only (DEC-136): a record-only commit keeps the code fingerprint and moves the records one; a
code commit, a change to the path map and a change to the ``record_only`` list itself move the code fingerprint;
the fingerprints are read from the commit, never the working tree; what cannot be computed is None.
"""
from __future__ import annotations

from pathlib import Path

from gov.close.fingerprint import of_commit

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_REL = "template/governance/kernel/schemas/test-map.schema.json"
MAP_REL = "governance/project/test-map.yaml"
MAP = 'version: 1\nshared_core: ["src/core/**"]\nrecord_only:\n  - "docs/close/**.md"\n  - "governance/project/**"\n'


def _project(repo):
    repo.commit("the project", files={SCHEMA_REL: (REPO_ROOT / SCHEMA_REL).read_text(encoding="utf-8"),
                                      MAP_REL: MAP, "src/a.py": "A = 1\n", "docs/close/T/CL-1.md": "one\n",
                                      "governance/project/path-map.yaml": "namespaces: {}\n"})
    return of_commit(repo.root)


def test_a_record_only_commit_keeps_the_code_fingerprint_and_moves_the_records_one(repo):
    before = _project(repo)
    repo.commit("a record", files={"docs/close/T/CL-2.md": "two\n"})
    after = of_commit(repo.root)
    assert after["code"] == before["code"] and after["records"] != before["records"]
    assert before["code"].startswith("sha256:")


def test_a_code_commit_moves_the_code_fingerprint(repo):
    before = _project(repo)
    repo.commit("code", files={"src/a.py": "A = 2\n"})
    assert of_commit(repo.root)["code"] != before["code"]


def test_the_path_map_and_the_test_map_are_code_though_a_record_only_pattern_matches_them(repo):
    before = _project(repo)
    repo.commit("the path map", files={"governance/project/path-map.yaml": "namespaces: {x: {}}\n"})
    moved = of_commit(repo.root)
    assert moved["code"] != before["code"] and moved["records"] == before["records"]
    repo.commit("the record-only list", files={MAP_REL: MAP + '  - "src/**"\n'})
    assert of_commit(repo.root)["code"] != moved["code"]


def test_the_fingerprints_are_of_the_commit_not_of_the_working_tree(repo):
    before = _project(repo)
    (repo.root / "src/a.py").write_text("A = 3\n", encoding="utf-8")
    (repo.root / MAP_REL).unlink()
    assert of_commit(repo.root) == before
    assert of_commit(repo.root, repo.git("rev-parse", "HEAD").strip()) == before


def test_what_cannot_be_computed_is_none_never_an_empty_list(repo):
    repo.commit("no test map", files={"src/a.py": "A = 1\n"})
    assert of_commit(repo.root) is None
    repo.commit("a map its schema refuses", files={MAP_REL: 'version: 2\nshared_core: ["src/core/**"]\n'})
    assert of_commit(repo.root) is None
    repo.commit("a map that does not parse", files={MAP_REL: "version: [1\n"})
    assert of_commit(repo.root) is None
    assert of_commit(repo.root, "0" * 40) is None


def test_a_map_without_a_record_only_list_counts_every_path_as_code(repo):
    repo.commit("a map", files={MAP_REL: 'version: 1\nshared_core: ["src/core/**"]\n',
                                "docs/close/T/CL-1.md": "one\n"})
    before = of_commit(repo.root)
    repo.commit("a record", files={"docs/close/T/CL-2.md": "two\n"})
    assert of_commit(repo.root)["code"] != before["code"]
