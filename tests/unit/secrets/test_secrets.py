"""Builder tests for the pre-index filter and the secrets-indexing check (W1-15).

Regression evidence only (DEC-136). They cover what the acceptance tests leave
to the builder: a path allowlist does not shelter a file from the filter
(DEC-290), content gitleaks would skip as binary is still scanned, a path
that leaves the root or sits in two namespaces is judged closed, big-endian
UTF-16 is scanned, and a store file that cannot be read is not a clean store.
No secret stands whole in this file: the planted string is built from parts.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import secrets  # noqa: E402

PLANTED = "_".join(["ARGUS", "TOKEN", "CAN" + "ARY", "4WM8"])
MAP = ("namespaces:\n"
       "  everything: {paths: ['**'], memory_class: governance}\n"
       "  exports: {paths: ['exports/**'], memory_class: product}\n")
ALLOWLIST = "\n[[allowlists]]\ndescription = 'test'\npaths = ['''(^|/)fixtures/''', '''\\.md$''']\n"

pytestmark = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")


def _write(root, rel, data):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else data.encode())
    return rel


@pytest.fixture()
def project(tmp_path):
    _write(tmp_path, "governance/project/path-map.yaml", MAP)
    _write(tmp_path, ".gitleaks.toml", (REPO / "template/.gitleaks.toml").read_text(encoding="utf-8") + ALLOWLIST)
    return tmp_path


def test_a_path_allowlist_does_not_shelter_a_file_from_the_filter(project):
    clean = _write(project, "fixtures/clean.md", "Ordinary text.\n")
    planted = _write(project, "fixtures/planted.md", f"The value is {PLANTED} today.\n")
    assert secrets.indexable(project, [planted, clean]) == [clean]


def test_an_older_allowlist_spelling_or_a_configuration_in_the_environment_shelters_nothing(project, monkeypatch):
    lenient = _write(project, "lenient.toml", "[[rules]]\nid = 'none'\nregex = '''never-matches-anything'''\n")
    monkeypatch.setenv("GITLEAKS_CONFIG", str(project / lenient))
    config = project / ".gitleaks.toml"
    config.write_text(config.read_text(encoding="utf-8").replace("[[rules]]", "[[rules]]\nallowlist = {regexes = ['.']}")
                      + "\n[allowlist]\nstopwords = ['argus']\n", encoding="utf-8")
    clean = _write(project, "notes/clean.md", "Ordinary text.\n")
    planted = _write(project, "notes/planted.md", f"The value is {PLANTED} today.\n")
    assert secrets.indexable(project, [planted, clean]) == [clean]


def test_content_that_looks_binary_is_still_scanned(project):
    planted = _write(project, "notes/blob.bin", b"SQLite format 3\0\x7fELF " + PLANTED.encode() + b"\n")
    assert secrets.indexable(project, [planted]) == []
    _write(project, ".gov-runtime/index/blob.bin", b"\x7fELF\x02\x01\x01 " + PLANTED.encode() + b"\n")
    assert secrets.stores_with_secrets(project) == [".gov-runtime/index/blob.bin"]


def test_a_path_out_of_the_root_or_in_a_product_namespace_too_is_dropped(project, tmp_path):
    clean = _write(project, "notes/clean.md", "Ordinary text.\n")
    both = _write(project, "exports/rows.csv", "id\n1\n")
    assert secrets.indexable(project, ["notes/../exports/rows.csv", both, "/etc/hostname", clean]) == [clean]


def test_big_endian_utf16_text_is_still_scanned(project):
    clean = _write(project, "notes/clean.md", "Ordinary text.\n".encode("utf-16-be"))
    planted = _write(project, "notes/planted.md", f"The value is {PLANTED} today.\n".encode("utf-16-be"))
    assert secrets.indexable(project, [planted, clean]) == [clean]


def test_a_store_file_that_cannot_be_read_is_not_a_clean_store(project):
    _write(project, ".gov-runtime/index/gone.md", "Ordinary text.\n")
    (project / ".gov-runtime/packets").symlink_to(project / "nowhere")  # a link to nothing: it cannot be read
    with pytest.raises(OSError):
        secrets.stores_with_secrets(project)


def test_a_path_name_is_judged_by_each_of_its_names_and_no_allowlist_shelters_it(project):
    assert secrets.path_holds_secret(project, f"fixtures/{PLANTED}/page.md") is True
    assert secrets.path_holds_secret(project, f"fixtures/{PLANTED}.md") is True
    assert secrets.path_holds_secret(project, "fixtures/page.md") is False
    (project / ".gitleaks.toml").unlink()
    with pytest.raises(RuntimeError):  # no rules: no verdict
        secrets.path_holds_secret(project, "fixtures/page.md")


def test_a_project_without_a_gitleaks_configuration_is_refused(project):
    (project / ".gitleaks.toml").unlink()
    clean = _write(project, "notes/clean.md", "Ordinary text.\n")
    with pytest.raises(RuntimeError):
        secrets.indexable(project, [clean])
