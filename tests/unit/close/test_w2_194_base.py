"""W2-194 (DAEO-kq8b) S2 (--base resolved as git rev-parse resolves it: a short hash that names one commit; an
unknown prefix BASE_UNKNOWN, an ambiguous one BASE_AMBIGUOUS) and S3 (the scoped close's owner-accepted base reds)."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import subprocess

import pytest
import yaml

from gov.cli.errors import GovError
from gov.close import attribution, command, ratchet, select

from .test_w2_115_support import OWN_SUITE, TICKET, change, project

CONFIG = {"path-map.yaml": {"close_workers": 1}}


def _ambiguous(repo, digits: int = 5) -> str:
    """Two commit objects whose ids share their first ``digits`` digits, written loose; the shared prefix."""
    tree = repo.git("rev-parse", "HEAD^{tree}").strip()
    seen: dict[str, bytes] = {}
    for n in itertools.count():
        body = f"tree {tree}\nauthor A <a@x> 0 +0000\ncommitter A <a@x> 0 +0000\n\nn {n}\n".encode()
        sha = hashlib.sha1(b"commit %d\0" % len(body) + body).hexdigest()
        prefix = sha[:digits]
        if prefix in seen and seen[prefix] != body:
            for one in (seen[prefix], body):
                subprocess.run(["git", "-C", str(repo.root), "hash-object", "-w", "-t", "commit", "--stdin"],
                               input=one, check=True, capture_output=True)
            return prefix
        seen[prefix] = body


def test_s2_a_short_hash_naming_one_commit_resolves_to_its_full_id(tmp_path):
    repo = project(tmp_path)
    head = repo.git("rev-parse", "HEAD").strip()
    assert select.resolve_base(repo.root, head[:9]) == (head, None)
    assert select.resolve_base(repo.root, head) == (head, None)


def test_s2_an_unknown_prefix_is_base_unknown(tmp_path):
    repo = project(tmp_path)
    head = repo.git("rev-parse", "HEAD").strip()
    unknown = ("0" if head[0] != "0" else "1") * 9
    assert select.resolve_base(repo.root, unknown) == (None, "BASE_UNKNOWN")
    assert select.resolve_base(repo.root, "--all") == (None, "BASE_UNKNOWN")
    assert select.resolve_base(repo.root, "") == (None, "BASE_UNKNOWN")


def test_s2_an_ambiguous_prefix_is_base_ambiguous(tmp_path):
    repo = project(tmp_path)
    prefix = _ambiguous(repo)
    assert select.resolve_base(repo.root, prefix) == (None, "BASE_AMBIGUOUS")


def _args(**more):
    base = {"ticket": TICKET, "select": False, "verify": False, "full": False, "timeout": None, "base": None,
            "disposition": None, "owner_decision": None, "out": None}
    base.update(more)
    return argparse.Namespace(**base)


def test_s2_the_close_refuses_each_by_its_code_naming_what_was_given(tmp_path):
    repo = project(tmp_path)
    prefix = _ambiguous(repo)
    change(repo, {"src/pkg/other.py": "def other():\n    return 1  # c\n"})
    for given, code in ((prefix, "BASE_AMBIGUOUS"), ("abcdef0123", "BASE_UNKNOWN")):
        with pytest.raises(GovError) as raised:
            command.run(repo.root, _args(base=given), CONFIG)
        assert raised.value.code == code and given in raised.value.message


# --- S3: a counted accepted_reds entry for a red red at the base ------------------------------------------------

RED_TEST = f"{OWN_SUITE}test_broken.py::test_broken"


def _record(repo):
    text = (repo.root / f"docs/close/{TICKET}/CL-{TICKET}.md").read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---\n")[1])


def _listed(monkeypatch, counted: list, findings: list | None = None):
    seen = []

    def entries(root, key, commit="HEAD"):
        seen.append(key)
        assert key == ratchet.ACCEPTED_REDS
        return counted, list(findings or [])
    monkeypatch.setattr(ratchet, "counted_entries", entries)
    return seen


def test_s3_a_counted_entry_accepts_a_red_red_at_the_base_with_another_type(tmp_path, monkeypatch):
    repo = project(tmp_path, extra={f"{OWN_SUITE}test_broken.py": "def test_broken():\n    raise ValueError(1)\n"})
    change(repo, {f"{OWN_SUITE}test_broken.py": "def test_broken():\n    assert 1 == 2\n"})
    entry = {"test": RED_TEST, "decision": "DEC-9", "reason": "known", "fixed_by": "T-9"}
    seen = _listed(monkeypatch, [entry], [{"code": "ACCEPTED_RED_REFUSED", "test": "x::y", "message": "no"}])
    command.run(repo.root, _args(), CONFIG)
    assert seen == [ratchet.ACCEPTED_REDS]
    record = _record(repo)
    [red] = record["reds"]
    assert red["test"] == RED_TEST and red["caused"] is False and red["accepted"] == "DEC-9"
    assert red["repair_ticket"] is None
    assert record["accepted_reds"] == [{**entry, "result": "failed"}]
    assert record["accepted_red_findings"] == [{"code": "ACCEPTED_RED_REFUSED", "test": "x::y", "message": "no"}]
    assert sorted(p.name for p in (repo.root / ".tickets").glob("*.md")) == [f"{TICKET}.md"]


def test_s3_a_listed_red_green_at_the_base_is_never_accepted(tmp_path, monkeypatch):
    repo = project(tmp_path)
    change(repo, {f"{OWN_SUITE}test_broken.py": "def test_broken():\n    assert 1 == 2\n"})
    _listed(monkeypatch, [{"test": RED_TEST, "decision": "DEC-9", "reason": "known", "fixed_by": "T-9"}])
    with pytest.raises(GovError) as raised:
        command.run(repo.root, _args(), CONFIG)
    assert raised.value.code == "RED_CAUSED"
    [red] = raised.value.details["reds"]
    assert red["caused"] is True and not red.get("accepted")


def test_s3_red_at_the_base_reads_the_alone_run_there_or_the_base_run():
    assert attribution.red_at_base(["ValueError"], None)
    assert attribution.red_at_base([attribution.ABSENT], "ValueError")
    assert not attribution.red_at_base([None], None)
    assert not attribution.red_at_base([attribution.ABSENT], attribution.NOT_COLLECTED)
    assert not attribution.red_at_base([attribution.UNKNOWN], None)
    assert not attribution.red_at_base([attribution.ABSENT], attribution.SKIPPED)
