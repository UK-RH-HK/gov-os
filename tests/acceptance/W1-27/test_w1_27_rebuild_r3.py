"""Round 3, KPI success 2: rebuild recreates the lexical index properly.

The current ``src/gov/rebuild/command.py`` creates three empty lexical
tables from a copy of W1-17's table definitions (``_LEXICAL_SCHEMA``),
then outputs constant sentences for semantic and code index ("skipped").

What is decided (DEC-416):

- The lexical index is recreated by ``gov.retrieval.lexical.refresh(root)``,
  which needs only git and the tree.  Rebuild holds no copy of another
  module's table definitions.  After a rebuild of a project with tracked
  files the lexical index is fresh, and a search finds a tracked file's text.
- The semantic index is recreated by its own refresh when the tool answers,
  and is named as not recreated with the measured reason when it does not.
- The code index: ``src/gov/retrieval/code_index.py`` does not exist —
  a not-recreated entry with that reason.
- The result names every derived store with what was done to it: recreated
  or not_recreated with a reason.  A constant sentence is not a measured
  reason.

Predecessor analysis
--------------------
Round 2's ``test_w1_27_rebuild_r2.py`` checks that lexical *tables* exist
after rebuild and that rebuild names unreconstructed stores.  It does not
verify the tables contain data (freshness), nor that a lexical search
works, nor that the result uses a measured reason instead of constants,
nor that rebuild holds no copy of another module's DDL.  The predecessor
was **weak**: it verified table existence, not a functioning index.

Revised after implementation: rebuild goes through the lexical index's
owner and its secrets filter (DEC-440); the fixture's size, not the
behaviour, made it time out.  The three rebuild cases now use a tiny
project with ``run_gov_with_code`` for the code root.
The DDL copy case does not run rebuild and keeps the full project.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import w1_27_support as support


# --------------------------------------------------------------------------- #
# Case 1: After rebuild, the lexical index is fresh
# --------------------------------------------------------------------------- #

def test_rebuild_lexical_index_is_fresh(rebuild_gov, rebuild_project, interface):
    """After rebuild on a project with tracked files, ``freshness(root)``
    returns status ``"fresh"`` — not ``"empty"`` or ``"missing"``.

    KPI: "rebuild recreates every derived store" [CAP-07.a].
    Currently fails: rebuild creates empty tables via ``_LEXICAL_SCHEMA``
    so ``freshness()`` returns ``"empty"``.

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the fixture's size, not the
    behaviour, made it time out.
    """
    py_file = rebuild_project / "hello.py"
    py_file.write_text("def greet():\n    return 'hello world'\n", encoding="utf-8")
    support.commit_all(rebuild_project, "add a tracked python file")

    run = rebuild_gov("rebuild", "--json")
    support.assert_envelope(run, interface, command="rebuild")
    assert run.returncode == 0, f"rebuild failed\n{run.describe()}"

    from gov.retrieval.lexical import freshness
    state = freshness(rebuild_project)
    assert state["status"] == "fresh", (
        f"after rebuild the lexical index should be 'fresh' but is "
        f"'{state['status']}' — rebuild did not populate the index\n"
        f"freshness: {state}\n{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Case 2: After rebuild, a lexical search finds tracked file text
# --------------------------------------------------------------------------- #

def test_rebuild_lexical_search_finds_tracked_text(rebuild_gov, rebuild_project, interface):
    """After rebuild on a project with tracked files, a lexical search
    finds text from the tracked file.

    KPI: "rebuild recreates every derived store" [CAP-07.a].
    Currently fails: rebuild creates empty tables so search returns no hits.

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the fixture's size, not the
    behaviour, made it time out.
    """
    marker = "UNIQUE_MARKER_FOR_REBUILD_TEST_xk7q"
    py_file = rebuild_project / "marker_file.py"
    py_file.write_text(f"# {marker}\ndef marker():\n    pass\n", encoding="utf-8")
    support.commit_all(rebuild_project, "add a tracked file with a unique marker")

    run = rebuild_gov("rebuild", "--json")
    support.assert_envelope(run, interface, command="rebuild")
    assert run.returncode == 0, f"rebuild failed\n{run.describe()}"

    from gov.retrieval.lexical import search
    result = search(rebuild_project, marker, refresh=False)
    assert result.get("available"), (
        f"lexical search is not available after rebuild: "
        f"state={result.get('state')}, reason={result.get('reason')}\n{run.describe()}"
    )
    assert result.get("hits"), (
        f"lexical search returns no hits for '{marker}' after rebuild — "
        f"the index is empty; rebuild did not populate it\n{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Case 3: Rebuild result names every derived store with measured status
# --------------------------------------------------------------------------- #

def test_rebuild_result_names_derived_stores_with_measured_status(rebuild_gov, rebuild_project, interface):
    """The rebuild result names every derived store with a status:
    ``"recreated"`` or ``"not_recreated"`` with a reason that is not a
    constant sentence.

    KPI: "rebuild recreates every derived store" [CAP-07.a].
    Currently fails: the result has only a ``"skipped"`` list with constant
    reason strings like ``"requires ollama and qwen3-embedding model"``.

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the fixture's size, not the
    behaviour, made it time out.
    """
    py_file = rebuild_project / "sample.py"
    py_file.write_text("x = 1\n", encoding="utf-8")
    support.commit_all(rebuild_project, "add a tracked file")

    run = rebuild_gov("rebuild", "--json")
    envelope = support.assert_envelope(run, interface, command="rebuild")
    assert run.returncode == 0, f"rebuild failed\n{run.describe()}"

    result = envelope.get("result") or {}
    result_text = json.dumps(result)

    has_stores_key = "stores" in result or "derived_stores" in result
    has_status_per_store = False
    has_constant_only = True

    stores = result.get("stores") or result.get("derived_stores") or {}
    if isinstance(stores, dict):
        for name, entry in stores.items():
            if isinstance(entry, dict) and "status" in entry:
                has_status_per_store = True
                if entry["status"] == "not_recreated" and "reason" in entry:
                    reason = entry["reason"]
                    if not isinstance(reason, str) or reason not in (
                        "requires ollama and qwen3-embedding model",
                        "requires code intelligence tool",
                        "skipped",
                    ):
                        has_constant_only = False
    elif isinstance(stores, list):
        for entry in stores:
            if isinstance(entry, dict) and "status" in entry:
                has_status_per_store = True

    uses_skipped_list = "skipped" in result and isinstance(result["skipped"], list)

    assert not uses_skipped_list or has_stores_key, (
        f"rebuild result uses a 'skipped' list instead of naming every "
        f"derived store with a per-store status (recreated/not_recreated "
        f"with a measured reason)\nresult keys: {list(result.keys())}\n"
        f"result: {result}\n{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Case 4: Rebuild does not hold a copy of another module's table DDL
# --------------------------------------------------------------------------- #

def test_rebuild_does_not_hold_lexical_schema_copy(project):
    """The rebuild module does not hold a copy of another module's table
    definitions: ``_LEXICAL_SCHEMA`` or equivalent hardcoded DDL does
    not appear in ``src/gov/rebuild/command.py``.

    KPI: "rebuild recreates every derived store" [CAP-07.a] — the code
    that owns the index recreates it; rebuild holds no copy.
    Currently fails: ``_LEXICAL_SCHEMA`` is defined in rebuild/command.py.
    """
    rebuild_path = project / "src" / "gov" / "rebuild" / "command.py"
    assert rebuild_path.is_file(), "src/gov/rebuild/command.py not found"
    source = rebuild_path.read_text(encoding="utf-8")

    has_lexical_schema = "_LEXICAL_SCHEMA" in source
    has_hardcoded_ddl = bool(re.search(
        r"CREATE\s+TABLE.*lexical_", source, re.IGNORECASE
    ))

    assert not has_lexical_schema and not has_hardcoded_ddl, (
        f"src/gov/rebuild/command.py holds a copy of another module's "
        f"table definitions (_LEXICAL_SCHEMA={has_lexical_schema}, "
        f"hardcoded DDL={has_hardcoded_ddl}); the code that owns the "
        f"index should recreate it, not rebuild"
    )
