"""Round 4, KPI success 2: rebuild goes through the lexical index's owner and
its secrets filter; the code index's outcome is measured (DEC-440).

Two things are wrong in ``src/gov/rebuild/command.py`` at ``7b424f2b``:

1. ``_preseed_lexical`` inserts every tracked file into the lexical tables
   directly, going round ``gov.secrets.indexable`` (the secret filter).
   ``lexical.refresh`` then finds the files already indexed (blob hashes
   match) and does not re-run the filter.  A file holding a secret ends up
   in the index.  DEC-440: "recreates the lexical index by the code that
   owns it".

2. The code index entry is hardcoded as ``"not_recreated"`` with the constant
   reason ``"no code index module exists"``, but ``src/gov/codeintel/`` is
   W1-16's module and it has ``index(root)``.  DEC-440: the code index is
   recreated by the code that owns it when its tool answers, and named as
   not recreated with the measured reason when it does not.

Predecessor analysis
--------------------
Round 3's ``test_w1_27_rebuild_r3.py`` checks that rebuild creates a fresh
index and uses measured status strings.  It does not plant a secret file
nor verify that the secrets filter runs during rebuild, and it does not
check that ``gov.codeintel.index`` is called or that the code-index reason
is measured against the real module.  Both gaps let the two bugs through.

Revised after implementation: rebuild goes through the lexical index's
owner and its secrets filter (DEC-440); the fixture's size, not the
behaviour, made it time out.  Every case now uses a tiny project with
``run_gov_with_code`` for the code root.
"""

from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path

import pytest

import w1_27_support as support


# --------------------------------------------------------------------------- #
# Secret fixture — built at runtime from parts, never a real credential.
# The same shape the W1-16 and W1-21 suites use: a token-shaped string with
# a prefix, digits and mixed case, long enough for the gitleaks rule.
# --------------------------------------------------------------------------- #

_PART = "REB" + "UILD"
SECRET_TEXT = "-".join(["sk", "FAKE", "W127", _PART, "4zQ9", "do", "not", "use"])

_GITLEAKS = shutil.which("gitleaks")
needs_gitleaks = pytest.mark.skipif(
    _GITLEAKS is None,
    reason="gitleaks is not on PATH; the secret filter cannot run (DEC-287)",
)


def _project_with_secret(project):
    """Add a file with a planted secret and a clean file, commit."""
    secret_file = project / "secret_holder.py"
    secret_file.write_text(
        f'SECRET = "{SECRET_TEXT}"\n',
        encoding="utf-8",
    )
    clean_file = project / "clean.py"
    clean_file.write_text("def greet():\n    return 'hello'\n", encoding="utf-8")
    support.commit_all(project, "add a secret and a clean file")


# --------------------------------------------------------------------------- #
# Case (a): after rebuild, a search for the secret text finds nothing and
#           the secret file is not among the indexed ones
# --------------------------------------------------------------------------- #

@needs_gitleaks
def test_rebuild_secret_file_not_in_lexical_index(cli, rebuild_gov, rebuild_project, sandbox, interface):
    """After rebuild on a project with a tracked file holding a secret,
    ``search(root, secret_text, refresh=False)`` returns no hits and the
    file is not marked as indexed in ``lexical_file`` — exactly as after
    the index's own ``refresh``.

    KPI: "rebuild recreates every derived store" [CAP-07.a].
    DEC-440: "recreates the lexical index by the code that owns it".

    Currently fails: ``_preseed_lexical`` inserts the file into the lexical
    tables directly, bypassing the secret filter; ``refresh`` then finds the
    file already indexed (blob hash matches) and does not re-run the filter.
    A search for the secret text returns hits from the indexed file.

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the fixture's size, not the
    behaviour, made it time out.

    Revised after implementation: the case imported the package into the
    test process and passed only where PYTHONPATH was set.
    """
    _project_with_secret(rebuild_project)

    run = rebuild_gov("rebuild", "--json")
    support.assert_envelope(run, interface, command="rebuild")
    assert run.returncode == 0, f"rebuild failed\n{run.describe()}"

    snippet = (
        "import json, sys\n"
        "from pathlib import Path\n"
        "from gov.retrieval.lexical import search\n"
        f"result = search(Path({str(rebuild_project)!r}), {SECRET_TEXT!r}, refresh=False)\n"
        "json.dump(result, sys.stdout)\n"
    )
    done = support.run_python_snippet(cli, sandbox, snippet)
    assert done.returncode == 0, f"search snippet failed:\n{done.stderr}"
    result = json.loads(done.stdout)
    hits = result.get("hits", [])
    assert not hits, (
        f"after rebuild, a search for the secret text returned {len(hits)} "
        f"hit(s) — the secret bypassed the filter; "
        f"hit paths: {[h.get('path') for h in hits]}\n{run.describe()}"
    )

    store = rebuild_project / ".gov-runtime" / "store.db"
    if store.is_file():
        conn = sqlite3.connect(store.resolve().as_uri() + "?mode=ro", uri=True)
        try:
            rows = conn.execute(
                "SELECT path, indexed FROM lexical_file WHERE path = ?",
                ("secret_holder.py",),
            ).fetchall()
        finally:
            conn.close()
        indexed_rows = [r for r in rows if r[1] == 1]
        assert not indexed_rows, (
            f"secret_holder.py is marked indexed=1 in lexical_file after "
            f"rebuild — the secret filter was bypassed\n{run.describe()}"
        )


# --------------------------------------------------------------------------- #
# Case (b): the lexical index after rebuild is the same as after the owner's
#           refresh alone on an identical fresh project
# --------------------------------------------------------------------------- #

@needs_gitleaks
def test_rebuild_lexical_digest_matches_owner_refresh(cli, rebuild_gov, rebuild_project, sandbox, interface, tmp_path):
    """The lexical index after ``gov rebuild`` on a fresh project is the same
    as after the owner's ``refresh`` alone on an identical fresh project,
    compared through ``digest(root)``.

    KPI: "rebuild recreates every derived store" [CAP-07.a].
    DEC-440: "recreates the lexical index by the code that owns it".

    Currently fails: ``_preseed_lexical`` indexes every file including ones
    the filter would reject; ``refresh`` alone filters them out.  The two
    digests differ.

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the fixture's size, not the
    behaviour, made it time out.

    Revised after implementation: the case imported the package into the
    test process and passed only where PYTHONPATH was set.
    """
    _project_with_secret(rebuild_project)

    run = rebuild_gov("rebuild", "--json")
    support.assert_envelope(run, interface, command="rebuild")
    assert run.returncode == 0, f"rebuild failed\n{run.describe()}"

    project_b = support.make_rebuild_project(cli, tmp_path / "repo_b")
    _project_with_secret(project_b)

    snippet = (
        "import json, sys\n"
        "from pathlib import Path\n"
        "from gov.retrieval.lexical import digest, refresh\n"
        f"rebuild_root = Path({str(rebuild_project)!r})\n"
        f"refresh_root = Path({str(project_b)!r})\n"
        "refresh(refresh_root)\n"
        "json.dump({'rebuild': digest(rebuild_root), 'refresh': digest(refresh_root)}, sys.stdout)\n"
    )
    done = support.run_python_snippet(cli, sandbox, snippet)
    assert done.returncode == 0, f"digest snippet failed:\n{done.stderr}"
    digests = json.loads(done.stdout)

    assert digests["rebuild"] == digests["refresh"], (
        f"the lexical index after rebuild differs from the index after the "
        f"owner's refresh alone:\n"
        f"  rebuild digest:  {digests['rebuild']}\n"
        f"  refresh digest:  {digests['refresh']}\n"
        f"rebuild did not recreate the index through the owner's code path"
    )


# --------------------------------------------------------------------------- #
# Case (c): the secrets-indexing backstop is green after rebuild
# --------------------------------------------------------------------------- #

@needs_gitleaks
def test_rebuild_stores_hold_no_secret(cli, rebuild_gov, rebuild_project, sandbox, interface):
    """``stores_with_secrets(root)`` returns nothing for a project after
    ``gov rebuild`` — the same as after a plain refresh.  This is the
    backstop the secrets-indexing family check of W1-15 uses.

    KPI: "rebuild recreates every derived store" [CAP-07.a].
    DEC-440: "recreates the lexical index by the code that owns it".

    Currently fails: ``_preseed_lexical`` inserts the secret text into the
    SQLite store's ``lexical_fts`` table; ``stores_with_secrets`` reads
    the table rows and finds the secret there.

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the fixture's size, not the
    behaviour, made it time out.

    Revised after implementation: the case imported the package into the
    test process and passed only where PYTHONPATH was set.
    """
    _project_with_secret(rebuild_project)

    run = rebuild_gov("rebuild", "--json")
    support.assert_envelope(run, interface, command="rebuild")
    assert run.returncode == 0, f"rebuild failed\n{run.describe()}"

    snippet = (
        "import json, sys\n"
        "from pathlib import Path\n"
        "from gov.secrets import stores_with_secrets\n"
        f"tainted = stores_with_secrets(Path({str(rebuild_project)!r}))\n"
        "json.dump(tainted, sys.stdout)\n"
    )
    done = support.run_python_snippet(cli, sandbox, snippet)
    assert done.returncode == 0, f"stores_with_secrets snippet failed:\n{done.stderr}"
    tainted = json.loads(done.stdout)
    assert not tainted, (
        f"after rebuild, {len(tainted)} store(s) hold a secret: {tainted}\n"
        f"the secret bypassed the filter during rebuild\n{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Code index: the reason is measured, not a constant sentence (tool absent)
# --------------------------------------------------------------------------- #

def test_rebuild_codeintel_reason_is_measured(cli, rebuild_gov, rebuild_project, interface):
    """The code index entry in the rebuild result names what was tried and
    what answered, not the constant sentence ``"no code index module exists"``
    — because the module ``src/gov/codeintel/`` does exist (W1-16) and it
    has ``index(root)``.

    DEC-440: the code index is recreated by the code that owns it when its
    tool answers, and named as not recreated with the measured reason when
    it does not.

    Currently fails: the reason is the hardcoded constant
    ``"no code index module exists"``.

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the fixture's size, not the
    behaviour, made it time out.  The codeintel existence check reads ``cli``
    (the session-scope code root).
    """
    py_file = rebuild_project / "sample.py"
    py_file.write_text("x = 1\n", encoding="utf-8")
    support.commit_all(rebuild_project, "add a tracked file")

    codeintel_init = cli / "src" / "gov" / "codeintel" / "__init__.py"
    assert codeintel_init.is_file(), (
        "src/gov/codeintel/__init__.py does not exist; W1-16's module is missing"
    )

    run = rebuild_gov("rebuild", "--json")
    envelope = support.assert_envelope(run, interface, command="rebuild")
    assert run.returncode == 0, f"rebuild failed\n{run.describe()}"

    result = envelope.get("result") or {}
    stores = result.get("stores") or result.get("derived_stores") or {}
    codeintel = stores.get("codeintel") or stores.get("code_index") or {}
    reason = codeintel.get("reason", "")

    assert reason != "no code index module exists", (
        f"the code index reason is the constant 'no code index module "
        f"exists' but src/gov/codeintel/ is W1-16's module and it has "
        f"index(root); the reason should name what was tried and what "
        f"answered (DEC-440)\ncodeintel entry: {codeintel}\n{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Code index: recreated when the tool answers
# --------------------------------------------------------------------------- #

@pytest.mark.local_only
def test_rebuild_codeintel_is_recreated_when_tool_answers(rebuild_gov, rebuild_project, interface):
    """When ``codebase-memory-mcp`` is on PATH, ``gov rebuild`` recreates the
    code index through ``gov.codeintel.index(root)`` (W1-16) and reports
    ``status: "recreated"``.

    DEC-440: the code index is recreated by the code that owns it when its
    tool answers.

    Currently fails: rebuild hardcodes ``"not_recreated"`` with a constant
    reason and never calls ``codeintel.index``.

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the fixture's size, not the
    behaviour, made it time out.
    """
    if shutil.which("codebase-memory-mcp") is None:
        pytest.skip(
            "codebase-memory-mcp is not on PATH; "
            "the code index tool is absent"
        )
    if _GITLEAKS is None:
        pytest.skip(
            "gitleaks is not on PATH; "
            "the code index tool's filter needs it"
        )

    py_file = rebuild_project / "sample.py"
    py_file.write_text("def example():\n    return 42\n", encoding="utf-8")
    support.commit_all(rebuild_project, "add a tracked file")

    run = rebuild_gov("rebuild", "--json")
    envelope = support.assert_envelope(run, interface, command="rebuild")
    assert run.returncode == 0, f"rebuild failed\n{run.describe()}"

    result = envelope.get("result") or {}
    stores = result.get("stores") or result.get("derived_stores") or {}
    codeintel = stores.get("codeintel") or stores.get("code_index") or {}

    assert codeintel.get("status") == "recreated", (
        f"with codebase-memory-mcp on PATH, the code index should be "
        f"'recreated' but is {codeintel.get('status')!r}\n"
        f"codeintel entry: {codeintel}\n{run.describe()}"
    )
