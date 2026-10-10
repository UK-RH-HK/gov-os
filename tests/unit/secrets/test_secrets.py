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


SHELTERED = "_".join(["ARGUS", "fal" + "se", "CAN" + "ARY", "4WM8"])  # gitleaks' default allowlist passes this one


def test_the_allowlist_of_the_gitleaks_defaults_shelters_no_project_rule(project):
    clean = _write(project, "notes/clean.md", "The flag is false, true or null; abcdefghijklmnopqrstuvwxyz.\n")
    planted = _write(project, "notes/planted.md", f"The value is {SHELTERED} today.\n")
    assert secrets.indexable(project, [planted, clean]) == [clean]
    assert secrets.path_holds_secret(project, f"notes/{SHELTERED}.md") is True
    assert secrets.path_holds_secret(project, "notes/false/null.md") is False
    _write(project, ".gov-runtime/index/rows.txt", f"{SHELTERED}\n")
    assert secrets.stores_with_secrets(project) == [".gov-runtime/index/rows.txt"]


def test_a_second_scan_that_does_not_decide_lets_nothing_through(project, monkeypatch):
    clean = _write(project, "notes/clean.md", "Ordinary text.\n")
    run = secrets.subprocess.run

    def failing_alone(command, **options):
        done = run(command, **options)
        if "extend" not in options["env"]["GITLEAKS_CONFIG_TOML"]:
            done.returncode = 1
        return done

    monkeypatch.setattr(secrets.subprocess, "run", failing_alone)
    with pytest.raises(RuntimeError):
        secrets.indexable(project, [clean])
    with pytest.raises(RuntimeError):
        secrets.path_holds_secret(project, clean)


def test_a_file_with_no_rule_for_the_second_scan_is_judged_as_before(project):
    clean = _write(project, "notes/clean.md", "Ordinary text.\n")
    key = _write(project, "notes/key.md", "-----BEGIN RSA PRIVATE KEY-----\n" + "MIIEow" + "9aZ3" * 20 + "\n-----END RSA PRIVATE KEY-----\n")
    config = project / ".gitleaks.toml"
    for rules in ("", "[[rules]]\nid = 'generic-api-key'\nentropy = 4.0\n"):  # none, and one that only changes a default
        config.write_text("[extend]\nuseDefault = true\n" + rules, encoding="utf-8")
        assert len(secrets._rules(project)) == 1
        assert secrets.indexable(project, [key, clean]) == [clean]


def test_a_project_without_a_gitleaks_configuration_is_refused(project):
    (project / ".gitleaks.toml").unlink()
    clean = _write(project, "notes/clean.md", "Ordinary text.\n")
    with pytest.raises(RuntimeError):
        secrets.indexable(project, [clean])


def test_the_parallel_scan_reads_every_store_file_once_and_keeps_the_order_of_the_paths(project, monkeypatch):
    rels = [_write(project, f".gov-runtime/{folder}/{number:02d}.md", f"{folder} {number} ordinary text.\n")
            for folder in ("pair", "pair-b", "store") for number in range(12)]
    planted = [_write(project, f".gov-runtime/{name}", f"The value is {PLANTED} today.\n")
               for name in ("pair/zz.md", "pair-b/00a.md")]
    scanned = []
    real = secrets._holds_secret
    monkeypatch.setattr(secrets, "_holds_secret", lambda rules, content: scanned.append(content) or real(rules, content))
    assert secrets.stores_with_secrets(project) == planted
    assert sorted(scanned) == sorted((project / rel).read_bytes() for rel in rels + planted)
