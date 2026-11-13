"""S10 (success-10), S4's layout half (success-4) and F3 (failure-3, layout half); I5, I6: the store layout is stated once
(``store/layout.py``), a store of another layout version is never read as missing or as current, ``gov rebuild``
replaces it and says so.

The planted stores are made by the product's own load in a child (``plant_store.py``) and by hand (a store from before
W2-03's ``register_entries.span``); ``open_store.py`` opens each through ``gov.store.loader.connect``.
"""

from __future__ import annotations

import json
import re
import sqlite3
import subprocess
import sys

import pytest

import w2_88_support as W

LAYOUT_PY = W.SRC / "gov" / "store" / "layout.py"


def child(box, host, script, *args):
    done = subprocess.run([sys.executable, str(W.HERE / script), *map(str, args)], env=W.env(box, host), capture_output=True,
                          text=True, timeout=300, stdin=subprocess.DEVNULL, cwd=str(box.base))
    return done


def outcome(box, host, project) -> dict:
    done = child(box, host, "open_store.py", project)
    assert done.returncode == 0 and done.stdout.strip(), f"open_store.py failed: {done.stderr[-800:]}"
    return json.loads(done.stdout.strip().splitlines()[-1])


def plant(box, host, mode, name="stale"):
    project = W.S124.plant(box, name, files=3)
    done = child(box, host, "plant_store.py", project, mode)
    assert done.returncode == 0, (f"the store could not be planted in state {mode!r} (no gov.store.layout on this head?): "
                                  f"{done.stderr.strip().splitlines()[-1:]}")
    return project, json.loads(done.stdout.strip().splitlines()[-1])


def pre_span_store(box, name="prespan"):
    """A store built before W2-03's ``register_entries.span`` column: a hand-built database, no stamp."""
    project = W.S124.plant(box, name, files=1)
    db = project / ".gov-runtime" / "store.db"
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE register_entries (id TEXT PRIMARY KEY, heading TEXT NOT NULL, title TEXT NOT NULL, "
                 "content_hash TEXT NOT NULL)")
    conn.execute("INSERT INTO register_entries VALUES ('DEC-001', 'DEC-001: a', 'a', 'x')")
    conn.commit()
    conn.close()
    return project


# ---- S4: the layout is stated once ---------------------------------------------------------------------------

def test_s4_layout_py_states_the_version_and_each_store_with_its_tables():
    text = LAYOUT_PY.read_text(encoding="utf-8")        # red: no src/gov/store/layout.py on the base
    assert re.search(r"^LAYOUT_VERSION\s*=\s*2\b", text, re.M), "layout.py does not state LAYOUT_VERSION = 2"
    for needle in ("store_layout", ".gov-runtime/store.db", ".gov-runtime/codeintel", "register_entries", "span"):
        assert needle in text, f"layout.py does not mention {needle!r}"
    from gov.store import layout
    assert set(layout.STORES) == set(W.STORES), f"STORES holds {sorted(layout.STORES)}, I5 names {sorted(W.STORES)}"
    assert layout.STAMP_TABLE == "store_layout"
    assert all("file" in layout.STORES[name] and "tables" in layout.STORES[name] for name in W.STORES)
    assert "span" in json.dumps({k: list(v) if not isinstance(v, str) else v
                                 for k, v in dict(layout.STORES["record"]["tables"]).items()}.get("register_entries"))
    assert all(str(t).startswith("lexical_") for t in layout.STORES["lexical"]["tables"])
    assert all(str(t).startswith("semantic_") for t in layout.STORES["vectors"]["tables"])
    assert tuple(layout.STORES["codegraph"]["tables"]) == ()


def test_s4_every_table_the_layout_names_for_the_record_store_exists_in_a_loaded_store(box, host):
    project, planted = plant(box, host, "load")
    assert planted.get("version") == planted.get("expected") == 2, f"the load did not stamp version 2: {planted}"
    from gov.store import layout
    conn = sqlite3.connect(project / ".gov-runtime" / "store.db")
    have = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    missing = [t for t in layout.STORES["record"]["tables"] if t not in have]
    assert not missing, f"the layout names tables the load does not build: {missing}"


# ---- S10 / F3: another layout version is never read as current -----------------------------------------------

def test_s10_a_current_store_opens_with_no_refusal(box, host):
    project, planted = plant(box, host, "load", "current")
    assert planted.get("version") == planted.get("expected") == 2, f"a loaded store carries no current stamp (layout 2): {planted}"
    seen = outcome(box, host, project)
    assert seen["outcome"] == "opened", f"a current store was refused: {seen}"


@pytest.mark.parametrize("mode", ["older", "newer"])
def test_s10_f3_an_older_or_newer_stamp_is_refused_naming_both_versions(box, host, mode):
    project, planted = plant(box, host, mode, mode)
    expected = outcome(box, host, project).get("layout_version") or 2
    seen = outcome(box, host, project)
    assert seen["outcome"] == "error", f"a store of layout {planted['version']} was opened as current: {seen}"
    assert seen["code"] == "STORE_LAYOUT_STALE", f"the refusal is {seen['code']}, not STORE_LAYOUT_STALE"
    assert seen["details"] == {"found": planted["version"], "expected": expected}, f"details {seen['details']}"
    assert str(planted["version"]) in seen["message"] and str(expected) in seen["message"], \
        f"the message does not name both versions: {seen['message']}"
    assert seen["code"] != "STORE_MISSING"


def test_s10_a_store_from_before_w2_03s_span_column_is_stale_never_missing(box, host):
    project = pre_span_store(box, "prespan")
    seen = outcome(box, host, project)
    assert seen["outcome"] == "error", f"a store without register_entries.span was opened: {seen}"
    assert seen["code"] == "STORE_LAYOUT_STALE", f"got {seen['code']}: the 2026-10-30 case must be STALE, never STORE_MISSING"
    assert seen["details"].get("found") == 0, f"an unstamped store missing a column is found 0: {seen['details']}"
    assert seen["details"].get("expected") == seen.get("layout_version")


def test_s10_an_unstamped_store_whose_tables_are_complete_opens_as_current(box, host):
    """GUARD (green on the base, as it must stay): the 35 test files that build a store.db by hand have no stamp; I5 reads
    one as current unless a table STORES names lacks one of its columns."""
    project = W.S124.plant(box, "unstamped", files=2)
    done = subprocess.run([sys.executable, "-c", "import sys; from pathlib import Path; from gov.store import loader; "
                           "loader.load(Path(sys.argv[1]))", str(project)], env=W.env(box, host), capture_output=True,
                          text=True, timeout=300)
    assert done.returncode == 0, done.stderr[-500:]
    conn = sqlite3.connect(project / ".gov-runtime" / "store.db")
    conn.execute("DROP TABLE IF EXISTS store_layout")
    conn.commit()
    conn.close()
    seen = outcome(box, host, project)
    assert seen["outcome"] == "opened", f"an unstamped store with complete tables was refused: {seen}"


def test_s10_no_store_at_all_is_still_store_missing(box, host):
    """GUARD (green on the base): ``connect`` checks the layout after its STORE_MISSING check, so no store stays missing."""
    project = W.S124.plant(box, "nostore", files=1)
    seen = outcome(box, host, project)
    assert seen["outcome"] == "error" and seen["code"] == "STORE_MISSING", seen


# ---- S10: gov rebuild replaces it and says so ----------------------------------------------------------------

@pytest.mark.parametrize("case", ["older", "newer", "prespan"])
def test_s10_gov_rebuild_replaces_a_stale_store_and_reports_the_layout(box, host, case):
    if case == "prespan":
        project, found = pre_span_store(box, "rebuild-prespan"), 0
    else:
        project, planted = plant(box, host, case, f"rebuild-{case}")
        found = planted["version"]
    run = W.S124.rebuild(project, box, host, "--json", "--no-embeddings")
    assert run.prints_ok, f"gov rebuild on a stale store ({case}) did not print ok\n{run.describe()}"
    layout = run.result.get("layout")
    expected = outcome(box, host, project).get("layout_version")
    assert layout == {"found": found, "expected": expected, "rebuilt": True}, f"the rebuild reports layout {layout}"
    seen = outcome(box, host, project)
    assert seen["outcome"] == "opened", f"the store is still refused after the rebuild: {seen}"


def test_f3_a_rebuild_digest_set_has_four_digests(box, host):
    """I6: the rebuild's result carries ``digests: {record, lexical, vectors, codegraph_bytes}``; ``digest`` is unchanged."""
    project = W.S124.plant(box, "digests", files=3)
    run = W.S124.rebuild(project, box, host, "--json")
    assert run.prints_ok, run.describe()
    digests = run.result.get("digests")
    assert isinstance(digests, dict) and set(W.DIGESTS) <= set(digests), f"digests {digests}"
    assert run.result.get("digest") == digests["record"], "``digest`` (the record graph's) stays as it is and equals digests.record"
    for key in ("record", "lexical", "vectors"):
        assert re.fullmatch(r"[0-9a-f]{64}", str(digests[key])), f"digests.{key} is no sha256: {digests[key]!r}"
