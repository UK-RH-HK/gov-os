"""A tiny synthetic Git repository builder used by tests/core/**. Keeps the pytest suite hermetic and fast (no
dependency on the real, 6,500-file Governance OS tree): every test that needs Git objects builds its own throwaway
repository with a handful of commits and branches that stand in for the records/product/evidence/history roles.
"""
from __future__ import annotations

import dataclasses
import subprocess
from pathlib import Path


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} failed: {r.stderr}")
    return r


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "-A")
    _git(root, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", message)
    return _git(root, "rev-parse", "HEAD").stdout.strip()


def write(root: Path, rel: str, content: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def write_bytes(root: Path, rel: str, content: bytes) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(content)


@dataclasses.dataclass
class FixtureRepo:
    root: Path
    c1: str  # first commit: initial product + records content
    c2: str  # second commit on records: records content changed, product untouched
    c3_moved: str  # a third commit further advancing a branch used for the REF_MOVED test
    product_pin: str  # == c1 (the commit "product" is pinned to)
    evidence_pin: str  # == c2
    history_refs: list[str]


def build(root: Path) -> FixtureRepo:
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "-q", "-b", "records")

    # -- commit 1: product-partition content + records-partition content, plus rule-exercising files -------------
    write(root, "tools/identity.py", 'PRODUCT_CODE = ["runtime", "bin"]\n')
    write(root, "runtime/src/init.rs", "fn native_layout_rules() {\n    // v1\n}\n")
    write(root, "docs/NOTES.md", "# Notes\nversion 1\n")
    write(root, "config/app.toml", "[app]\nname = 'x'\n")
    write(root, "secrets/token.pem", "-----BEGIN RSA PRIVATE KEY-----\nnot-a-real-key\n")
    write(root, ".env", "TOKEN=abc\n")
    write_bytes(root, "bin/blob.dat", bytes(range(256)) * 4)  # contains NUL bytes -> binary
    write(root, "logs/build.out", "line one\nline two\n" * 5)  # L-MACHINE-OUTPUT kind
    write(root, "src/creds.py", "aws_secret_access_key = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'\n")
    write(root, "big/large.txt", "x" * (1024 * 1024 + 10))  # > 1 MiB -> M-LARGE
    c1 = _commit(root, "c1: initial")

    _git(root, "branch", "product")  # pinned partition ref, stays at c1
    _git(root, "branch", "evidence")  # will be advanced to c2 below, then pinned there

    # -- commit 2 on records: records-owned content changes; product-owned path (runtime/) is untouched here -----
    write(root, "docs/NOTES.md", "# Notes\nversion 2\n")
    c2 = _commit(root, "c2: records moves on")
    _git(root, "checkout", "-q", "-b", "evidence-tmp")
    _git(root, "checkout", "-q", "records")
    _git(root, "branch", "-f", "evidence", "records")  # evidence pinned at c2

    # a couple of "history" tips, simulating phase2/* branches
    _git(root, "checkout", "-q", "-b", "history/attempt-1", "records")
    write(root, "docs/NOTES.md", "# Notes\nfailed attempt\n")
    _commit(root, "history attempt 1")
    _git(root, "checkout", "-q", "-b", "history/attempt-2", "records")
    write(root, "docs/NOTES.md", "# Notes\nanother failed attempt\n")
    _commit(root, "history attempt 2")

    _git(root, "checkout", "-q", "records")
    write(root, "docs/NOTES.md", "# Notes\nversion 3 (branch moves further, for REF_MOVED)\n")
    c3_moved = _commit(root, "c3: records moves again")

    return FixtureRepo(
        root=root, c1=c1, c2=c2, c3_moved=c3_moved, product_pin=c1, evidence_pin=c2,
        history_refs=["refs/heads/history/attempt-1", "refs/heads/history/attempt-2"],
    )


def write_canonical_view(path: Path, repo: "FixtureRepo", view_id: str = "fixture-view",
                          product_pin: str = None, evidence_pin: str = None) -> None:
    """Write a config/canonical-view.yaml-shaped file for ``repo``, used by tests/core/conftest.py's ``view_path``
    fixture and by any test that needs a variant (e.g. a deliberately stale pinned_commit for a REF_MOVED case)."""
    product_pin = product_pin or repo.product_pin
    evidence_pin = evidence_pin or repo.evidence_pin
    path.write_text(f"""\
schema: govbridge-canonical-view/1
view_id: {view_id}
refs:
  - name: records
    ref: refs/heads/records
    follow: tip
    role: primary
  - name: product
    ref: refs/heads/product
    follow: pinned
    pinned_commit: {product_pin}
    role: product
  - name: evidence
    ref: refs/heads/evidence
    follow: pinned
    pinned_commit: {evidence_pin}
    role: evidence
  - name: history
    ref_glob: refs/heads/history/*
    follow: tip
    role: history
partitions:
  - name: product
    paths_from: "tools/identity.py#PRODUCT_CODE"
    owner: product
    fallback: [evidence, history]
  - name: records
    paths: ["**"]
    owner: records
    fallback: [product, evidence, history]
""", encoding="utf-8")
