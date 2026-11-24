"""Support for the W2-212 acceptance tests (DAEO-d3sr, the stale route). Planted repositories in ``tmp_path`` only; no
network, no model, no embedder (the semantic route is a stand-in that names the chunks it is given)."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "src"
sys.path.insert(0, str(SRC))

PATH_MAP = "governance/project/path-map.yaml"
CLASSES = ("superseded", "historical", "legacy")
OLD, NEW = "docs/design/lending.md", "docs/design/lending-v2.md"
OLD_WORD, NEW_WORD = "zanzibarcovenant", "quokkaledger"
QUESTION = "how does lending work"
_ENV = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t.invalid", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}


def git(root, *args):
    done = subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True,
                          env={**_ENV, "HOME": str(root)})
    return done.stdout.strip()


def write(root, rel, text):
    (Path(root) / rel).parent.mkdir(parents=True, exist_ok=True)
    (Path(root) / rel).write_text(text, encoding="utf-8")


def commit(root, files, message="a change"):
    for rel, text in files.items():
        write(root, rel, text)
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", message)


def init(root):
    Path(root).mkdir(parents=True, exist_ok=True)
    git(root, "init", "-q", "-b", "main")


def path_map(stale=None, *, lexical="not indexed", embedding="not embedded", old_paths=("docs/design/lending.md",),
             old_name="old-design"):
    """Minimal-form path map: the old design in its own namespace (``stale`` its class, None: unclassed and indexed),
    everything else in current namespaces."""
    old = {"paths": list(old_paths)}
    if stale is not None:
        old.update({"stale_class": stale, "lexical_policy": lexical, "embedding_policy": embedding})
    spaces = {old_name: old,
              "current": {"paths": [NEW, "docs/other/**", "docs/*.md", "governance/**", ".gitignore"]}}
    return yaml.safe_dump({"namespaces": spaces}, sort_keys=False)


# ---------------------------------------------------------------- the retrieval plant

RETRIEVE_FILES = {
    ".gitignore": ".gov-runtime/\n",
    OLD: f"# Lending design\n\nThe lending design of the old system: the {OLD_WORD} rules for lending.\n",
    NEW: f"# Lending design v2\n\nThe current lending design: the {NEW_WORD} rules for lending.\n",
    "docs/other/pier.md": "# Pier\n\nThe harbour pier is repainted every spring.\n",
}


def build_retrieval(tmp_path, monkeypatch, stale="superseded"):
    """An indexed repository (keyword index and store loaded) whose path map has ``stale`` on the old design's
    namespace from the start (None: unclassed and indexed). The semantic route names every chunk the keyword index
    held when it was built, as vectors built then would; no model runs. Returns (root, chunks_held_at_build)."""
    from gov import store
    from gov.retrieval import code_route, lexical, semantic
    from gov.retrieval import retrieve as retrieve_module

    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))  # no gitleaks needed
    root = Path(tmp_path) / "project"
    init(root)
    commit(root, {**RETRIEVE_FILES, PATH_MAP: path_map(stale)}, "fixture")
    lexical.refresh(root)
    store.load(root)
    held = list(lexical.chunks(root))
    monkeypatch.setattr(semantic, "search", lambda r, _q, **_k: {"available": True, "reason": None, "hits": list(held)})
    monkeypatch.setattr(code_route, "route", lambda *_a: None)
    monkeypatch.setattr(retrieve_module, "rerank", lambda _q, candidates, _r=None: candidates)
    for name in ("GOV_ROLE", "GOV_TICKET", "GOV_STORE"):
        monkeypatch.delenv(name, raising=False)
    return root, held


def bundle_paths(bundle):
    return {item["path"] for item in bundle.get("evidence", [])} | {gap.get("path") for gap in bundle.get("gaps", [])} \
        - {None}


def ask(root, query=QUESTION, **more):
    from gov.retrieval.retrieve import retrieve
    return retrieve(root, query, reranker=lambda: None, **more)


def cli_args(query, *flags):
    """``gov retrieve``'s own parser (``gov.retrieve.command.add_arguments``) on ``flags`` and the question."""
    from gov.retrieve import command
    parser = argparse.ArgumentParser()
    command.add_arguments(parser)
    args = parser.parse_args([*flags, query])
    args.role = None
    return args


# ---------------------------------------------------------------- the adoption plant (as tests/unit/adopt's)

ADOPT_FILES = {"lib/util.py": "def helper():\n    return 1\n", "README.md": "# p\n", ".gitignore": ".gov-runtime/\n",
               "docs/legacy/old.md": "old\n", "docs/archive/older.md": "older\n", "docs/Historical/h.md": "h\n",
               "docs/plans/p.md": "plan\n", "docs/notes/n.md": "notes\n"}
EMBEDDED_PATHS = ["lib/**", "README.md", ".gitignore"]


def adopt_config(*extra):
    """A path map: ``all`` embedded, then each ``(name, fields)`` of ``extra`` (fields: paths and the rest)."""
    spaces = {"all": {"paths": list(EMBEDDED_PATHS), "embedding_policy": "embedded"}}
    for name, fields in extra:
        spaces[name] = {"embedding_policy": "not embedded", **fields}
    return {"path-map.yaml": {"namespaces": spaces, "capabilities": {"code_intelligence": {"enabled": False}}}}


@pytest.fixture()
def adopt_root(tmp_path, monkeypatch):
    from gov.adopt import stages
    root = tmp_path / "project"
    init(root)
    git(root, "config", "user.name", "t")
    git(root, "config", "user.email", "t@t.invalid")
    commit(root, ADOPT_FILES, "fixture")
    monkeypatch.setattr(stages, "_importers", lambda r, paths: {rel: [] for rel in paths})
    monkeypatch.setattr(stages, "rebuild", lambda run, result: {**result, "rebuild": "replaced in this test"})
    return root.resolve()


def stage(root, name, conf, **more):
    """One adopt stage; a successful A2 is followed by stage AS, as the unit tests' helper does."""
    from gov.adopt import stages
    args = SimpleNamespace(**{"lite": True, "stage": name, "map": None, "verdict": None, "session": "adopter", **more})
    result = stages.run(root, args, conf)
    if name == "A2":
        stages.run(root, SimpleNamespace(lite=True, stage="AS", map=None, verdict=None, session="adopter"), conf)
    return result


def a3(root, conf, before_a3=None):
    """A0 to A2 (and AS), then A3 with a proposal that keeps README.md; the result, or the GovError raised."""
    for name in ("A0", "A1", "A2"):
        stage(root, name, conf)
    proposal = root.parent / "proposal.yaml"
    proposal.write_text(yaml.safe_dump({"artefacts": [{"path": "README.md", "action": "KEEP"}]}), encoding="utf-8")
    if before_a3:
        before_a3()
    return stage(root, "A3", conf, map=str(proposal))


# ---------------------------------------------------------------- the doctor plant

def doctor(root):
    """``gov doctor --json --root <root>``: (exit code, the envelope's result map or the error's details, text)."""
    env = {**os.environ, "PYTHONPATH": str(SRC)}
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", "doctor", "--json", "--root", str(root)],
                          capture_output=True, text=True, env=env, timeout=300)
    text = done.stdout + "\n" + done.stderr
    body = json.loads(done.stdout) if done.stdout.strip().startswith("{") else {}
    result = body.get("result") or (body.get("error") or {}).get("details") or {}
    return done.returncode, result, text
