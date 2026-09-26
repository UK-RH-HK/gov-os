#!/usr/bin/env python3
"""One ``TaskContext`` (REPAIR-1 node R1-RX, OBS-BR-08 / OD-BR-03 item 1): ``retrieval_exclusions`` applied
AUTOMATICALLY -- by every route (``govbridge.route.real_routes``), every CLI query command (``search``, ``why``,
``impact``, ``history``, ``exact``, ``state``) and every compiler call site that runs a route
(``govbridge.compile.packet``) -- never left to a caller remembering to pass ``--exclude`` by hand.

Run-1 (``ARCHITECTURE/REPAIR-1/CAUSE_ANALYSIS.md`` RC-8) measured 75 excluded-path hits across 11 public queries
under the CLI default, and 0 once the task's exclusions were passed explicitly; two ``govbridge.compile.packet``
call sites (the seed code route, the D.2 both-ways templates) passed no exclusions at all. This module is the ONE
place a task's ``retrieval_exclusions`` are loaded and matched, so every caller shares the same predicate
(``TaskContext.is_excluded`` -- itself a thin, generic wrapper over ``govbridge.core.pathrules.any_glob_match``,
never a second glob-matching implementation).

Two independent, complementary layers use this module:

* **explicit** -- a caller (a CLI command, ``govbridge.compile.packet``) loads/merges a ``TaskContext`` itself and
  passes the merged ``exclude=`` list into whatever it calls;
* **ambient** -- ``govbridge.route.real_routes``'s adapters ALSO merge in ``current()`` themselves, so even a
  caller that passes ``exclude=None`` (the CLI default before this repair; ``ARCHITECTURE/REPAIR-1/evidence/tools/
  exclusion_probe.py``'s own "cli_default_no_exclude" mode) still gets the ambient task's exclusions applied, as
  long as ``GOVBRIDGE_TASK`` names one or ``set_current``/``from_args`` installed one.

Neither layer is a substitute for the other: explicit passing is what ``grep -n 'routes.run(' packet.py`` can
verify mechanically (REPAIR_DAG.yaml's R1-RX acceptance check); the ambient layer is what makes the exclusion hold
even for a caller (a test, a probe script, a future route) that never learns about ``TaskContext`` at all.
"""
from __future__ import annotations

import dataclasses
import os
from typing import Any, Iterable, Optional

from govbridge.core import pathrules
from govbridge.core.yamlutil import load_yaml_file

ENV_VAR = "GOVBRIDGE_TASK"


@dataclasses.dataclass(frozen=True)
class TaskContext:
    """``source`` is the path a non-empty context was loaded from (or a caller-chosen label, e.g. ``"task_spec"``
    for a compile's own inline task spec) -- diagnostic only, never load-bearing. ``retrieval_exclusions`` is a
    tuple of globs, in the SAME shape ``schemas/task-spec.yaml``'s own ``retrieval_exclusions`` field already uses
    (``ARCHITECTURE/schemas/task-spec.yaml``: "applied to every route (not to the resolver); recorded in the
    manifest")."""
    source: Optional[str]
    retrieval_exclusions: tuple = ()

    def is_excluded(self, path: Optional[str]) -> bool:
        """The ONE exclusion predicate (``ARCHITECTURE/REPAIR-1/REPAIR_DAG.yaml`` R1-RX: "with one exclusion
        predicate used everywhere") -- every caller in this repair (routes, CLI commands, the compiler) asks THIS,
        never re-implements its own glob check."""
        if not path or not self.retrieval_exclusions:
            return False
        return pathrules.any_glob_match(path, self.retrieval_exclusions) is not None

    def merge_exclude(self, extra: Optional[Iterable[str]] = None) -> list:
        """This context's own exclusions plus whatever glob list the caller ALSO supplied (e.g. ``search --exclude
        GLOB``), deduplicated and order-preserving (context first). The one merge every route/query call routes
        its final ``exclude=`` argument through."""
        out: list = list(self.retrieval_exclusions)
        for g in (extra or ()):
            if g and g not in out:
                out.append(g)
        return out

    def count_excluded(self, paths: Iterable[Optional[str]]) -> int:
        """How many of ``paths`` this context would exclude -- the ``excluded_hits`` disclosure every command and
        every compile call site attaches to its own output (never a silent drop)."""
        return sum(1 for p in paths if self.is_excluded(p))


EMPTY = TaskContext(source=None, retrieval_exclusions=())


class ExclusionCounter:
    """A tiny mutable counter a route/query call is handed (``exclude_counter=``) so its caller learns, right
    after the call returns, how many candidate hits its own exclusions caused to be dropped -- without changing
    the ``RouteFn``/``RouteSet.run`` contract (``govbridge.route.router``, out of this node's scope): a plain list
    of ``RouteHit`` is still all that ever comes back from ``routes.run``."""
    __slots__ = ("count",)

    def __init__(self) -> None:
        self.count = 0

    def bump(self, n: int = 1) -> None:
        self.count += n


def _coerce_exclusions(doc: Any) -> tuple:
    if isinstance(doc, dict):
        raw = doc.get("retrieval_exclusions") or []
    elif isinstance(doc, list):
        raw = doc
    else:
        raw = []
    return tuple(g for g in raw if isinstance(g, str))


def load(task_path: Optional[str] = None, env: Optional[dict] = None) -> TaskContext:
    """Loads a ``TaskContext`` from an explicit ``--task <spec>`` path, or else ``GOVBRIDGE_TASK`` in ``env``
    (``os.environ`` by default). Neither given, or the file cannot be read/parsed, -> ``EMPTY``: no exclusions,
    every route/command/compile still runs exactly as it did before this repair -- purely additive, never a new
    failure mode. ``task_path`` may name a full ``schemas/task-spec.yaml`` document (only its
    ``retrieval_exclusions`` key is read) or a bare ``{retrieval_exclusions: [...]}`` document."""
    env = os.environ if env is None else env
    path = task_path or env.get(ENV_VAR)
    if not path:
        return EMPTY
    try:
        doc = load_yaml_file(path)
    except Exception:
        return EMPTY
    return TaskContext(source=path, retrieval_exclusions=_coerce_exclusions(doc))


# ---------------------------------------------------------------------------------------------------------------
# Ambient context: consulted by govbridge.route.real_routes so an exclusion holds even for a caller that never
# passes exclude= at all. ``_explicit`` is None until a CLI command actually names ``--task`` (``from_args``) or a
# caller installs one directly (``set_current`` -- mainly tests); it is NEVER set just because GOVBRIDGE_TASK is
# in the environment, so an ordinary test run (no --task, no GOVBRIDGE_TASK) is byte-for-byte unaffected by this
# module's existence. GOVBRIDGE_TASK itself is re-read (and cached per path) on every current() call rather than
# once at import time, so a probe script or test that exports it after this module is already imported still sees
# it (ARCHITECTURE/REPAIR-1/REPAIR_DAG.yaml's R1-RX acceptance check: "totals.cli_default_no_exclude == 0 once the
# task context is set").
# ---------------------------------------------------------------------------------------------------------------

_explicit: Optional[TaskContext] = None
_env_cache: dict = {}


def _from_env() -> TaskContext:
    path = os.environ.get(ENV_VAR)
    if not path:
        return EMPTY
    cached = _env_cache.get(path)
    if cached is None:
        cached = load(path)
        _env_cache[path] = cached
    return cached


def current() -> TaskContext:
    """The ambient ``TaskContext``: whatever ``set_current``/``from_args`` last installed, or else whatever
    ``GOVBRIDGE_TASK`` currently names (re-checked every call; see the module docstring)."""
    if _explicit is not None:
        return _explicit
    return _from_env()


def set_current(ctx: TaskContext) -> TaskContext:
    """Installs ``ctx`` as the ambient context, explicit and permanent for this process (until ``reset``/another
    ``set_current``) -- it wins over ``GOVBRIDGE_TASK`` even if the env var later changes. Returns the PREVIOUS
    ambient context (as ``current()`` would have reported it), so a caller -- mainly a test -- can restore it."""
    global _explicit
    previous = current()
    _explicit = ctx
    return previous


def reset() -> None:
    """Clears any explicitly-installed ambient context, reverting ``current()`` to the ``GOVBRIDGE_TASK``
    fallback. For tests: a test that calls ``set_current``/``from_args`` must restore isolation with this
    afterwards, so a later, unrelated test never inherits it."""
    global _explicit
    _explicit = None


def add_cli_arg(parser) -> None:
    """The one ``--task`` flag definition every CLI query command's parser adds (argparse) -- so its spelling and
    help text never drift between ``search``/``why``/``impact``/``history``/``exact``/``state``."""
    parser.add_argument(
        "--task", help="a task-spec YAML (or a bare {retrieval_exclusions: [...]} document) whose "
                        "retrieval_exclusions are applied automatically to this command; defaults to $GOVBRIDGE_TASK")


def from_args(args) -> TaskContext:
    """The one call every CLI query command makes right after parsing its own ``--task``-bearing arguments:
    installs the ambient context when ``--task`` was actually given (never just because GOVBRIDGE_TASK happens to
    be set -- that is ``current()``'s own, non-sticky fallback), then returns the effective context either way."""
    task_path = getattr(args, "task", None)
    if task_path:
        set_current(load(task_path))
    return current()


# ---------------------------------------------------------------------------------------------------------------
# Generic edge/hop filtering shared by the graph-derived CLI query commands (why/impact/history), whose hops are
# govbridge.graph.edges.Edge (or an already-``.to_dict()``-ed dict of one) rather than a route's RouteHit -- so
# they cannot go through govbridge.route.real_routes's exclude=/exclude_counter= path at all.
# ---------------------------------------------------------------------------------------------------------------

def occurrence_path(evidence_occurrence: Optional[str]) -> Optional[str]:
    """The path component of an ``Edge.evidence_occurrence`` (``"path@commit"`` or ``"path@commit:L1-L2"``), or
    None when the occurrence is not path-shaped (e.g. a shaped code-route hop's own ``"blob:line"`` -- honestly
    not excludable at this layer, the same generic MISSING discipline the rest of this codebase already uses,
    never a guess)."""
    if not evidence_occurrence or "@" not in evidence_occurrence:
        return None
    path, _, _rest = evidence_occurrence.partition("@")
    return path or None


def _edge_occurrence(edge) -> Optional[str]:
    if isinstance(edge, dict):
        return edge.get("evidence_occurrence")
    return getattr(edge, "evidence_occurrence", None)


def filter_edges(edges: Iterable, task: Optional[TaskContext] = None) -> tuple:
    """Drops every edge/hop whose occurrence path ``task`` excludes. ``edges`` may be ``Edge`` dataclass instances
    or already-``.to_dict()``-ed dicts (both carry ``evidence_occurrence``); an edge with no path-shaped occurrence
    is always kept (nothing to exclude by). Returns ``(kept, excluded_count)`` -- ``task`` defaults to the ambient
    ``current()`` so a library call that does not thread a context through explicitly still honours one that is
    set."""
    task = task or current()
    kept: list = []
    excluded = 0
    for e in edges:
        path = occurrence_path(_edge_occurrence(e))
        if path and task.is_excluded(path):
            excluded += 1
            continue
        kept.append(e)
    return kept, excluded
