"""``gov queue --full`` (W2-206; L2 section 3, A6 S3 and S4): step 5 widened to the nightly's own run.

The selection is the whole ``tests/`` of the tested merge, less the candidates' own acceptance folders (they run
through the runner of ``gov accept``: no test runs twice in a landing), with the options the test map gives every
run (the per-test limit, the retention policy). It runs by the close's two phases (the serial-only list's split),
as the nightly's run does, on each merged result ``gov.close.batch.isolate`` builds, so a red is run again alone,
attributed, or found red at the base as a selection's red is.

**The pool** (the owner, DEC-1216 (5): every run inside the gate, the full suite included, fewer workers rather
than a peak). A full run never asks for ``-n auto`` and never for a pool wider than its slot: its workers are the
smallest of the project path map's ``close_workers`` (where it names a number), ``PYTEST_XDIST_AUTO_NUM_WORKERS``
(where set) and the number of CPUs in ``GOV_HEAVY_CPUS`` (where set); with none of these, one slot's workers by
the product's rules (``gov.resources.slots``, ``gov.dispatch.limits``); at least 1. The run's children get that
number as ``PYTEST_XDIST_AUTO_NUM_WORKERS``, so nothing inside the run widens.
"""

from __future__ import annotations

import contextlib
import os
from pathlib import Path

AUTO_VARIABLE = "PYTEST_XDIST_AUTO_NUM_WORKERS"
CPUS_VARIABLE = "GOV_HEAVY_CPUS"
WORKERS_VARIABLE = "GOV_HEAVY_WORKERS"
PATH_MAP_REL = "governance/project/path-map.yaml"


def _count(value) -> int | None:
    """A positive whole number as written, or None."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 1 else None
    text = str(value).strip() if isinstance(value, str) else ""
    return int(text) if text.isdigit() and int(text) >= 1 else None


def _path_map_workers(root: Path) -> int | None:
    import yaml

    from gov.close.command import WORKERS_KEY

    try:
        settings = yaml.safe_load((Path(root) / PATH_MAP_REL).read_text(encoding="utf-8"))
    except (OSError, ValueError, yaml.YAMLError):
        return None
    value = settings.get(WORKERS_KEY) if isinstance(settings, dict) else None
    return value if isinstance(value, int) and _count(value) else None


def _one_slot() -> int:
    """One slot's workers, as ``gov.resources.slots.run`` sizes a run that names none; 1 where it cannot be told."""
    given = _count(os.environ.get(WORKERS_VARIABLE, ""))
    if given:
        return given
    try:
        from gov.dispatch import admission, limits
        from gov.resources import config as configuration, slots

        count = slots.slot_count(configuration.load(), lambda line: None)
        sized = admission.sized()
        return max(1, int(limits.workers_for(sized["load_limit"], sized["start_below"], sized["margin"], count)))
    except Exception:  # noqa: BLE001 - a machine that cannot be read gives the smallest pool, never a wider one
        return 1


def cap(root: Path) -> dict:
    """``{"workers", "cpus"}``: the full run's pool (module docstring) and the CPU set it runs in (``GOV_HEAVY_CPUS``
    as its slot gave it; None outside a slot)."""
    from gov.resources.config import cpu_list, parse_cpus

    cpus = parse_cpus(os.environ.get(CPUS_VARIABLE, "")) if os.environ.get(CPUS_VARIABLE, "").strip() else None
    named = [n for n in (_path_map_workers(root), _count(os.environ.get(AUTO_VARIABLE, "")),
                         len(cpus) if cpus else None) if n]
    return {"workers": max(1, min(named)) if named else _one_slot(), "cpus": cpu_list(cpus) if cpus else None}


@contextlib.contextmanager
def capped(workers: int):
    """The cap as ``PYTEST_XDIST_AUTO_NUM_WORKERS`` for every run started inside; the caller's value put back."""
    before = os.environ.get(AUTO_VARIABLE)
    os.environ[AUTO_VARIABLE] = str(workers)
    try:
        yield
    finally:
        if before is None:
            os.environ.pop(AUTO_VARIABLE, None)
        else:
            os.environ[AUTO_VARIABLE] = before


def selection(clone: Path, own: list[str]) -> dict:
    """The full run's selection in ``clone``: ``{"suites", "pytest_options", "full"}``; ``own`` the candidates'
    acceptance folders, left out."""
    from gov.close import select

    options = select.pytest_options(select.load_map(Path(clone))[0])
    return {"suites": [select.FULL_TARGET], "full": True,
            "pytest_options": options + [f"--ignore={folder.strip('/')}" for folder in own]}
