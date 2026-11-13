"""W2-150 S2: E-2's four coupling edges, each gone (DAEO-ijf5; INVESTIGATION-1 part E, E-2).

One case per edge, through the same static walk as S1 (``w2_150_walk``). A failure prints the import path.
"""

from __future__ import annotations

from w2_150_walk import Walk, in_package


def test_s2_store_loader_imports_no_close_and_no_tickets():
    """Edge 1: ``store/loader.py``'s own import statements (any level) name no ``gov.close.*`` and no
    ``gov.tasks.tickets``."""
    walk = Walk()
    bad = [(target, line) for target, line in walk.direct_imports("gov.store.loader")
           if in_package(target, "gov.close") or target == "gov.tasks.tickets"]
    assert not bad, "gov.store.loader still imports:\n" + "\n".join(
        f"  {target} [src/gov/store/loader.py:{line}]" for target, line in bad)


def _closure_free(start: str, bad, label: str):
    walk = Walk()
    reached = walk.closure([start])
    hits = walk.report(reached, bad)
    assert not hits, f"{start}'s import closure reaches {label}; the import path to each:\n{hits}"


def test_s2_retrieve_command_closure_reaches_no_decisions_checker():
    """Edge 2: ``retrieve/command.py`` no longer pulls ``gov.decisions.checker``."""
    _closure_free("gov.retrieve.command", lambda m: m == "gov.decisions.checker", "gov.decisions.checker")


def test_s2_secrets_closure_reaches_no_guard():
    """Edge 3: ``secrets/__init__.py`` no longer pulls ``gov.guard`` (``guard.runs`` and on to ``guard.decide``)."""
    _closure_free("gov.secrets", lambda m: in_package(m, "gov.guard"), "gov.guard")


def test_s2_retrieval_measure_closure_reaches_no_guard():
    """Edge 4: ``retrieval/measure.py`` no longer pulls ``gov.guard`` (``guard.reads``)."""
    _closure_free("gov.retrieval.measure", lambda m: in_package(m, "gov.guard"), "gov.guard")
