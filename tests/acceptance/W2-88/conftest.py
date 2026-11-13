"""Fixtures of the W2-88 acceptance tests: a box (hermetic environment) per case, one stand-in embedder per session, and
a clean-up of every temporary tree a case made (DEC-898: 3 GB and 150,000 files outside the tracked tree)."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import w2_88_support as W  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: needs this machine (the real code-graph tool, a folder outside tmp)")


@pytest.fixture(scope="session")
def embedder():
    """A stand-in embedding endpoint (W2-124's, healthy) on a loopback port: no model, no network."""
    stand_in = W.S124.Embedder("healthy")
    try:
        yield stand_in
    finally:
        stand_in.close()


@pytest.fixture
def box(tmp_path):
    made = W.make_box(tmp_path)
    try:
        yield made
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)   # nothing of a case's planted trees outlives it


@pytest.fixture
def host(embedder):
    return embedder.host


class Nine:
    """One planted adoption through A8 and, unless ``run_a9`` was false, its A9 run (made on first use, kept for the
    module's cases; a case that must write copies nothing: it asks for its own key)."""

    def __init__(self, box, project, adoption, out):
        self.box, self.project, self.adoption, self.out = box, project, adoption, out
        self.chain_failed = None
        self.run = None

    def need_chain(self):
        assert self.chain_failed is None, f"the planted adoption did not reach A8: {self.chain_failed.describe()}"

    def need_a9(self):
        self.need_chain()
        W.assert_offered(self.run, "A9")
        return self.run

    def record(self):
        self.need_a9()
        assert self.run.returncode == 0 and self.run.envelope().get("ok") is True, f"A9 is not ok\n{self.run.describe()}"
        return W.a9_record(self.project, self.run)


class Worlds:
    def __init__(self, factory, host):
        self.factory, self.host, self.done, self.bases = factory, host, {}, []

    def a9(self, key="default", *, decisions=(), retrieval=None, plant_options=None, tools=(), run_a9=True,
           audit_tools=False):
        """``audit_tools``: a logging ``crontab`` first on PATH, a planted sets root and a planted runs folder given to the
        child through ``GOV_MEMAUDIT_SETS_ROOT`` and ``GOV_INDEP_RUNS_DIR`` (what S18, S22 and F9 hold unchanged)."""
        if key not in self.done:
            base = self.factory.mktemp(key.replace(" ", "-"))
            self.bases.append(base)
            box = W.make_box(base)
            options = {"retrieval": retrieval, **(plant_options or {})}
            project = W.plant_adoption(box, "harbour", **options)
            extra = {}
            audit = None
            if audit_tools:
                sets, runs = base / "sets-root", base / "runs"
                (sets / "fixtures").mkdir(parents=True)
                (sets / "fixtures" / "note.txt").write_text("planted sets root\n", encoding="utf-8")
                sets.chmod(0o700)
                (runs / "indep").mkdir(parents=True)
                crontab = W.logging_tool(base / "tools-crontab", "crontab", base / "crontab-calls.log",
                                         answer="# planted crontab\n0 3 * * * echo planted\n")
                tools = (*tools, crontab)
                extra = {"GOV_MEMAUDIT_SETS_ROOT": str(sets), "GOV_INDEP_RUNS_DIR": str(runs)}
                audit = {"sets": sets, "runs": runs, "crontab_log": base / "crontab-calls.log"}
            adoption = W.Adoption(project, box, self.host, tools=tools, extra_env=extra)
            nine = Nine(box, project, adoption, base / "a9-out")
            nine.audit = audit
            nine.chain_failed = adoption.chain("A8")
            if audit:
                audit["before"] = {"sets": W._tree_digest(audit["sets"], False), "runs": W._tree_digest(audit["runs"], False),
                                   "path_map": (project / "governance/project/path-map.yaml").read_bytes(),
                                   "head": W.head(project)}
            if nine.chain_failed is None and run_a9:
                args = [item for d in decisions for item in ("--decision", d)]
                nine.run = adoption.a9(nine.out, *args)
            self.done[key] = nine
        return self.done[key]

    def close(self):
        for base in self.bases:
            shutil.rmtree(base, ignore_errors=True)


@pytest.fixture(scope="module")
def worlds(tmp_path_factory, embedder):
    made = Worlds(tmp_path_factory, embedder.host)
    try:
        yield made
    finally:
        made.close()


@pytest.fixture(scope="session")
def sets_template(tmp_path_factory):
    """W2-170's planted world (a sets root, a repository with three commits, a pool, the store link), built once."""
    import w2_170_world as V
    base = tmp_path_factory.mktemp("w2-88-sets") / "w"
    V.build(base, "standard")
    yield base
    shutil.rmtree(base.parent, ignore_errors=True)


@pytest.fixture
def pworld(sets_template, tmp_path):
    """One case's copy of the planted sets world (W2-170's ``World``): the tuning or verdict set the practice cases plant."""
    import w2_170_world as V
    dest = tmp_path / "world"
    shutil.copytree(sets_template, dest, symlinks=True)
    return V.World(dest)
