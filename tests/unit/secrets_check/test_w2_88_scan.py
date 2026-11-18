"""Builder tests for W2-88 S27, revised for run 9's folder mode (DEC-1183 (2)); written in run 8 for the one-per-file
form of a23678e27.

Regression evidence only (DEC-136). ``indexable`` keeps its verdict per file, in the order asked, and no gitleaks
input joins two files' texts (run 7's checks P1-1 and P1R-1: a match crossing from one file's text into the next's):
each text is a file of its own in a batch's folder, one ``gitleaks dir`` per batch and rule set. No secret stands whole
in this file: the planted string is built from parts, and no test prints or records a value.
"""
from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path

import pytest

from gov import secrets

REPO = Path(__file__).resolve().parents[3]
PLANTED = "_".join(["ARGUS", "TOKEN", "CAN" + "ARY", "4WM8"])
MAP = "namespaces:\n  everything: {paths: ['**'], memory_class: governance}\n"

pytestmark = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")


def _write(root: Path, rel: str, data) -> str:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else data.encode())
    return rel


@pytest.fixture()
def project(tmp_path, monkeypatch):
    monkeypatch.delenv("GOV_HEAVY_THREAD_BUDGET", raising=False)
    _write(tmp_path, "governance/project/path-map.yaml", MAP)
    _write(tmp_path, ".gitleaks.toml", (REPO / "template/.gitleaks.toml").read_text(encoding="utf-8"))
    return tmp_path


def _plant(root: Path, count: int, secret_at=()) -> list[str]:
    """``count`` files, those whose number is in ``secret_at`` holding the planted test secret."""
    return [_write(root, f"notes/f{number:03d}.md",
                   (f"Note {number}.\n" + (f"The value is {PLANTED} here.\n" if number in secret_at else "Plain text.\n")) * 3)
            for number in range(count)]


def _one_per_file(root: Path, rels: list[str]) -> list[str]:
    """The one-per-file form's verdict: each file's bytes judged alone by ``_holds_secret``."""
    rules = secrets._rules(root)
    return [rel for rel in dict.fromkeys(rels)
            if (root / rel).exists() and not secrets._holds_secret(rules, (root / rel).read_bytes(), root, "content")]


@pytest.fixture()
def processes(monkeypatch):
    """Each gitleaks process started, by the texts it was given: its standard input, or each file of its folder."""
    seen = []
    real = secrets.subprocess.run

    def spy(command, **options):
        if command and command[0] == "gitleaks":
            if options.get("cwd"):
                folder = Path(options["cwd"])
                seen.append([(folder / name).read_bytes() for name in sorted(os.listdir(folder))])
            else:
                seen.append([options.get("input", b"")])
        return real(command, **options)

    monkeypatch.setattr(secrets.subprocess, "run", spy)
    return seen


def test_no_gitleaks_input_joins_two_files_texts(project, processes, monkeypatch, tmp_path):
    """Each file's text is a gitleaks input of its own (DEC-1183 (2)): one file of a batch's folder, never shared;
    one gitleaks dir per batch and rule set (run 8's one process per file and rule set, now per batch)."""
    monkeypatch.setenv("GOV_SECRETS_CACHE", str(tmp_path / "cache.sqlite"))
    monkeypatch.setenv("GOV_HEAVY_THREAD_BUDGET", "1")
    marks = [f"MARKER{number:03d}Q" for number in range(12)]
    rels = [_write(project, f"notes/m{number:03d}.md", f"Note {mark}.\nPlain text.\n") for number, mark in enumerate(marks)]
    assert secrets.indexable(project, rels) == rels
    assert len(processes) == len(secrets._rules(project))  # one batch at one worker
    for texts in processes:
        assert len(texts) == len(rels)
        for data in texts:
            assert sum(mark.encode() in data for mark in marks) == 1


def test_no_batched_stdin_scan_is_left_in_the_module():
    for name in ("_scan_batch", "_batched", "_BATCH_FILES", "_BATCH_MIN", "_FENCE"):
        assert not hasattr(secrets, name), name
    assert secrets._BATCH_TEXTS >= 1 and secrets._BATCH_BYTES >= 1  # folder mode's caps (run 9)


def test_the_verdict_per_file_is_the_one_per_file_forms_in_the_order_asked(project):
    rels = _plant(project, 30, secret_at={3, 11, 12, 29})
    rels += [_write(project, "big/large.txt", ("filler line of a large file\n" * 60_000) + f"{PLANTED}\n"),
             _write(project, "big/clean-large.txt", "filler line of a large file\n" * 60_000),
             _write(project, "doc/utf16.md", ("Value " + PLANTED + "\n").encode("utf-16-le")),
             _write(project, "doc/utf16-clean.md", "Plain words only\n".encode("utf-16-le")),
             _write(project, "doc/empty.md", b"")]
    asked = [*reversed(rels), rels[5], "notes/missing.md"]  # a repeat and a name with no file
    got = secrets.indexable(project, asked)
    assert got == _one_per_file(project, asked)
    assert "notes/f003.md" not in got and "notes/f004.md" in got and "big/large.txt" not in got
    assert "doc/utf16.md" not in got and "doc/utf16-clean.md" in got and "big/clean-large.txt" in got
    assert got == [rel for rel in dict.fromkeys(asked) if rel in set(got)]  # the order asked, without repeats


def test_a_link_is_judged_by_what_it_points_to(project):
    rels = _plant(project, 6, secret_at={2})
    (project / "notes" / "to-clean.md").symlink_to("f001.md")
    (project / "notes" / "to-secret.md").symlink_to("f002.md")
    (project / "notes" / "dangling.md").symlink_to("nowhere.md")
    asked = [*rels, "notes/to-clean.md", "notes/to-secret.md", "notes/dangling.md"]
    got = secrets.indexable(project, asked)
    assert got == _one_per_file(project, [rel for rel in asked if rel != "notes/dangling.md"]) \
        and "notes/to-clean.md" in got and "notes/to-secret.md" not in got and "notes/dangling.md" not in got


def test_a_file_outside_a_governance_namespace_is_left_out_whatever_it_holds(project):
    _write(project, "governance/project/path-map.yaml",
           "namespaces:\n  gov: {paths: ['notes/**'], memory_class: governance}\n  other: {paths: ['src/**'], memory_class: code}\n")
    rels = [*_plant(project, 5, secret_at={1}), _write(project, "src/code.py", "x = 1\n")]
    assert secrets.indexable(project, rels) == ["notes/f000.md", "notes/f002.md", "notes/f003.md", "notes/f004.md"]


def test_a_gitleaks_that_cannot_run_refuses_and_no_file_is_let_through(project, monkeypatch):
    rels = _plant(project, 5)
    monkeypatch.setenv("PATH", str(project / "no-such-folder"))
    with pytest.raises((RuntimeError, OSError)):
        secrets.indexable(project, rels)


def test_scan_off_gives_no_content_to_gitleaks(project, processes):
    rels = _plant(project, 8, secret_at={2})
    _write(project, "governance/project/secrets.yaml", "scan: off\n")
    assert secrets.indexable(project, rels) == rels
    assert processes == []


def test_scan_counts_stay_one_per_file(project):
    rels = _plant(project, 10, secret_at={6})
    before = secrets.scan_counts()["content"]
    secrets.indexable(project, rels)
    after = secrets.scan_counts()["content"]
    assert after["scanned"] - before["scanned"] == 10 and after["remembered"] == before["remembered"]


def test_a_clean_file_is_remembered_and_not_scanned_again(project, monkeypatch, tmp_path, processes):
    monkeypatch.setenv("GOV_SECRETS_CACHE", str(tmp_path / "cache.sqlite"))
    rels = _plant(project, 10, secret_at={6})
    first = secrets.indexable(project, rels)
    assert first == [rel for rel in rels if rel != "notes/f006.md"]
    processes.clear()
    before = secrets.scan_counts()["content"]
    assert secrets.indexable(project, rels) == first
    after = secrets.scan_counts()["content"]
    assert after["remembered"] - before["remembered"] == 9  # the nine clean files; the finding is scanned every time
    assert after["scanned"] - before["scanned"] == 1
    assert processes and all(texts == [texts[0]] and PLANTED.encode() in texts[0] for texts in processes)  # the finding's file only


VALUE = "".join(["Zq8W", "m4Xk", "2Vn7", "Bp3R", "t9Yh"])  # a generic-key value, built from parts; never printed
TAILS = ["password:", "token =", "secret:", "token:\n\n"]  # a bare generic key at a file's end
HEADS = [f"API_KEY={VALUE}\n", f"api_key = '{VALUE}'\n", f"secret: {VALUE}\n", f"token={VALUE}\nmore text\n"]


def test_a_bare_key_ending_one_file_never_swallows_the_next_files_secret(project):
    """Run 7's P1-1: a bare generic key at one file's end; the next file holds a secret that only that rule finds. Its
    verdict is the one-per-file form's, whatever the order."""
    cases = 0
    for tail in TAILS:
        for head in HEADS:
            root = project / f"case{cases}"
            cases += 1
            _write(root, "governance/project/path-map.yaml", MAP)
            _write(root, ".gitleaks.toml", (REPO / "template/.gitleaks.toml").read_text(encoding="utf-8"))
            a = _write(root, "config/a-tail.txt", "Plain notes.\nMore plain notes.\n" + tail)
            b = _write(root, "config/b-head.env", head)
            c = _write(root, "config/c-clean.txt", "Nothing here.\n")
            for order in ([a, b], [b, a], [c, a, b, c]):
                assert secrets.indexable(root, order) == _one_per_file(root, order), (tail, head, order)
            assert b not in secrets.indexable(root, [a, b, c]), (tail, head)  # it holds a secret by itself


def test_the_pair_in_the_middle_of_a_long_list_is_judged_as_one_per_file(project):
    rels = _plant(project, 14)
    rels.insert(6, _write(project, "config/a-tail.txt", "Plain notes.\npassword:"))
    rels.insert(7, _write(project, "config/b-head.env", f"API_KEY={VALUE}\n"))
    got = secrets.indexable(project, rels)
    assert got == _one_per_file(project, rels) and "config/b-head.env" not in got and "config/a-tail.txt" in got


@pytest.mark.parametrize("old", [4, 5, 6])
def test_a_record_written_under_an_earlier_form_is_not_reused(project, monkeypatch, tmp_path, old):
    """Forms 4 (a23678e27, ef9c773c3), 5 (d766514fd, the batched stdin scan) and 6 (run 8) wrote records; form 7
    (folder mode, run 9) trusts none of them."""
    monkeypatch.setenv("GOV_SECRETS_CACHE", str(tmp_path / "cache.sqlite"))
    rels = [_write(project, "config/b-head.env", f"API_KEY={VALUE}\n")]
    rules = secrets._rules(project)
    digest = hashlib.sha256((project / rels[0]).read_bytes()).hexdigest()
    secrets.cache.remember("content", digest, secrets.cache.engine(rules, old))
    assert secrets.cache.remembered("content", digest, secrets.cache.engine(rules, old))
    assert secrets.indexable(project, rels) == []  # the old record says clean; it is not asked
    assert secrets._FORM == 7


def test_a_commit_hash_of_the_project_is_still_no_finding(project):
    import subprocess

    def git(*args):
        return subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, check=True).stdout.strip()

    git("init", "-q")
    git("add", ".gitleaks.toml")
    git("-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-m", "one")
    commit = git("rev-parse", "HEAD")
    keyword = "".join(("source", "graph"))
    rels = [*_plant(project, 6), _write(project, "notes/review.md", f"The review names {keyword} at {commit} today.\n"),
            _write(project, "notes/random.md", f"The review names {keyword} at {os.urandom(20).hex()} today.\n")]
    got = secrets.indexable(project, rels)
    assert got == _one_per_file(project, rels)
    assert "notes/review.md" in got and "notes/random.md" not in got
