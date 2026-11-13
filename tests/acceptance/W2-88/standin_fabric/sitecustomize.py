"""A stand-in for two of the engineer's seams (P-4 ``fabric.check_coverage`` and P-10 the ``retrieval.yaml`` keys of the standard),
used only to show that the cases built on them bite (README, "Bite checks"). It is not the product's code and is never imported by a
case: Python loads it as ``sitecustomize`` when this folder is first on ``PYTHONPATH`` (the parent, for the in-process cases) and
when ``W2_88_STANDIN`` names it (the children ``w2_88_support.env`` starts). The mode is ``W2_88_STANDIN_MODE``.

It installs (1) a module ``gov.adopt.fabric`` holding only ``check_coverage(record, tracked)`` as the seam states it: ``None``, or
``GovError("FABRIC_INCOMPLETE", ..., {"missing": [<sorted paths>]})`` for a tracked path in neither the indexed nor the refused
list of the lexical store (which judges every tracked file; a lexical store absent from the record leaves every path out); and
(2) the stage ``A9`` of ``gov adopt --lite`` (``--out``, ``--decision``) doing the standard's departure check only, with the keys the
engineer named: ``pool.meaning_uncut`` (off: ``false``), ``rerank.service`` (absent ``shared``), ``rerank.model`` (absent: the pin's),
``bundle.tokens`` (absent 6000), ``bundle.widen`` (absent ``sections``); not ok with ``STANDARD_DEPARTURE`` unless ``--decision``
is given; the record committed under ``governance/adoption/`` holds ``standard.departures[{setting, value, decision}]``.

Modes. ``good``: as the seams state (and ``gov.config.loader`` taking the ``rerank`` and ``bundle`` keys, package P-W2-88-B-1);
``loader-as-is``: the same stand-in with the loader as it is on the base (it refuses those two keys). Coverage: ``coverage-never-raises`` (returns None always), ``coverage-wrong-code`` (another
code), ``coverage-no-details`` (the right code, no ``missing``), ``coverage-refused-is-missing`` (a path only in a refused list is
reported), ``coverage-absent-store-ok`` (a record with no lexical store passes). A9: ``blind`` (reads the keys of run 2's plant:
``reranker``, ``bundle_tokens``, no ``pool``: it does not see the planted departures), ``never-refuses`` (names the departure, never
refuses).
"""

import os
import subprocess
import sys
import types
from pathlib import Path

MODE = os.environ.get("W2_88_STANDIN_MODE", "good")
PIN = "Qwen/Qwen3-Reranker-0.6B"


# ---- (1) fabric.check_coverage ---------------------------------------------------------------------------------------

def check_coverage(record, tracked):
    from gov.cli.errors import GovError
    tracked = sorted(set(tracked))
    if MODE == "coverage-never-raises":
        return None
    stores = record.get("stores") or {}
    lexical = stores.get("lexical")
    if lexical is None:
        if MODE == "coverage-absent-store-ok":
            return None
        missing = tracked
    else:
        named = set(lexical.get("indexed") or ())
        if MODE != "coverage-refused-is-missing":
            named |= {item["path"] for item in lexical.get("refused") or ()}
        missing = [path for path in tracked if path not in named]
    if missing:
        code = "FABRIC_BROKEN" if MODE == "coverage-wrong-code" else "FABRIC_INCOMPLETE"
        details = {} if MODE == "coverage-no-details" else {"missing": missing}
        raise GovError(code, f"{len(missing)} tracked file(s) in neither list", details)
    return None


# ---- (2) the A9 stage: the standard's departure check ------------------------------------------------------------------

def departures(document):
    if MODE == "blind":
        found = [("reranker", document[k]) for k in ("reranker",) if k in document]
        found += [("bundle_tokens", document[k]) for k in ("bundle_tokens",) if k in document]
        found += [("pool", None)] if "pool" not in document else []
        return found
    found = []
    pool = document.get("pool") or {}
    if pool.get("meaning_uncut") is not True:
        found.append(("pool", pool))
    rerank = document.get("rerank") or {}
    if rerank.get("service", "shared") != "shared":
        found.append(("reranker_service", rerank["service"]))
    if rerank.get("model", PIN) != PIN:
        found.append(("reranker", rerank["model"]))
    bundle = document.get("bundle") or {}
    if bundle.get("tokens", 6000) != 6000:
        found.append(("bundle_tokens", bundle["tokens"]))
    if bundle.get("widen", "sections") != "sections":
        found.append(("widen", bundle["widen"]))
    return found


def a9(root, args):
    import yaml
    from gov.adopt.project import refuse
    document = yaml.safe_load((root / "governance/project/retrieval.yaml").read_text(encoding="utf-8")) or {}
    found = departures(document)
    decisions = list(getattr(args, "decision", None) or [])
    if found and not decisions and MODE != "never-refuses":
        raise refuse("STANDARD_DEPARTURE", "settings differ from the standard: " + ", ".join(name for name, _ in found))
    entries = [{"setting": name, "value": value, "decision": decisions[0] if decisions else None} for name, value in found]
    rel = "governance/adoption/A9-fabric.md"
    (root / "governance/adoption").mkdir(parents=True, exist_ok=True)
    front = yaml.safe_dump({"id": "ADOPT-A9", "stage": "A9", "standard": {"departures": entries}}, sort_keys=False)
    (root / rel).write_text("---\n" + front + "---\n\n# ADOPT-A9\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", rel], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "A9 stand-in record"], check=True, capture_output=True)
    return {"stage": "A9", "record": rel}


def _relax_loader():
    """Package P-W2-88-B-1 as the stand-in: ``gov.config.loader`` takes a top-level ``rerank`` and ``bundle`` key of
    ``retrieval.yaml`` (it refuses both today, ``CONFIG_INVALID``). Not done in mode ``loader-as-is``."""
    from gov.config import loader
    loader.RETRIEVAL_SCHEMA = {**loader.RETRIEVAL_SCHEMA, "rerank": {"required": False, "type": dict},
                               "bundle": {"required": False, "type": dict}}


def _install():
    import gov.adopt
    if MODE != "loader-as-is":
        _relax_loader()
    module = types.ModuleType("gov.adopt.fabric")
    module.check_coverage = check_coverage
    sys.modules["gov.adopt.fabric"] = module
    gov.adopt.fabric = module
    from gov.adopt import command, stages
    command.STAGES = (*command.STAGES, "A9")
    original_arguments = command.add_arguments

    def add_arguments(parser):
        original_arguments(parser)
        parser.add_argument("--out", metavar="<folder>")
        parser.add_argument("--decision", action="append", default=[], metavar="DEC-n")
        for action in parser._actions:
            if action.dest == "stage":
                action.choices = tuple(action.choices) + ("A9",)

    command.add_arguments = add_arguments
    original_run = stages.run

    def run(root, args, config):
        if args.stage == "A9":
            return a9(Path(root), args)
        return original_run(root, args, config)

    stages.run = run


try:
    _install()
except Exception as exc:  # noqa: BLE001
    sys.stderr.write(f"standin_fabric: not installed: {exc!r}\n")
