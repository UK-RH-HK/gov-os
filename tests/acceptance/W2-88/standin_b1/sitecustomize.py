"""Stand-ins of run 4's three seams, used only to show that the new cases bite (README, "Bite checks, run 4"). Never imported by a case,
never part of the product: Python loads it as ``sitecustomize`` when this folder is first on ``PYTHONPATH`` (the parent, for the
in-process cases) and when ``W2_88_STANDIN`` names it (the children ``w2_88_support.env`` starts). The mode is ``W2_88_STANDIN_MODE``.

It replaces, on the product's own ``gov.adopt.fabric`` and ``gov.store.loader`` modules, only what the interface of run 4 states:

(1) B-1.2 / B-1.4, the standard: ``settings_of(doc)`` (``reranker`` from ``rerank.MODEL``'s last ``/`` part, ``bundle_tokens`` from
    ``retrieve.BUNDLE_BUDGET``, ``reranker_service`` ``"shared"`` or ``"<CACHE_REL>/<SOCKET>"``), ``departures(doc)`` (the pool is the
    whole shipped block; value the file's block, or false) and ``read_standard(root, decisions)``; and a stage ``A9`` of ``gov adopt --lite``
    that does the standard's departure check, the scan seam (RV1-2: ``fabric.vector_scan`` -> ``vector_scan_ms`` a figure only when the
    route answered ``available: true``, else null and ``vector_scan_reason``; ``SCALE-PROPOSAL.md`` only for a measured figure over the
    budget) and commits a record under ``governance/adoption/``. It builds no store and copies nothing: only the cases that read those
    two blocks run against it.
(2) RV1-6: ``gov.store.loader.load`` stamps a store only when ``layout.check`` finds it current (or it is new).

Modes. ``good``: as the interface states. B-1.4: ``pool-meaning-only`` (the pool departs only when ``meaning_uncut`` is not true: run 3's
reading). B-1.2: ``constants-ignored`` (the reranker and the bundle read from ``retrieval.yaml``'s ``rerank``/``bundle`` keys, never the
pin's constants). RV1-2: ``scan-always-a-figure`` (the scan's time is a figure whatever the route answered). RV1-6: ``stamps-always``
(the load stamps every store current).
"""

import os
import subprocess
import sys
import time
from pathlib import Path

MODE = os.environ.get("W2_88_STANDIN_MODE", "good")


def _install():
    import yaml
    import gov.adopt  # noqa: F401
    from gov.adopt import command, fabric, stages
    from gov.cli.errors import GovError
    from gov.store import layout, loader

    standard = fabric.STANDARD

    # ---- (1) the standard ----------------------------------------------------------------------------------------
    def settings_of(document):
        from gov.retrieval import rerank, retrieve
        if MODE == "constants-ignored":
            return {"reranker": (document.get("rerank") or {}).get("model", standard["reranker"]),
                    "reranker_service": (document.get("rerank") or {}).get("service", "shared"),
                    "pool": document.get("pool"), "bundle_tokens": (document.get("bundle") or {}).get("tokens", 6000),
                    "widen": "sections"}
        service = "shared" if (rerank.CACHE_REL, rerank.SOCKET) == (".cache/gov-os", "rerank.sock") \
            else f"{rerank.CACHE_REL}/{rerank.SOCKET}"
        return {"reranker": rerank.MODEL.rsplit("/", 1)[-1], "reranker_service": service, "pool": document.get("pool"),
                "bundle_tokens": retrieve.BUNDLE_BUDGET, "widen": "sections"}

    def departures(document):
        found, settings = [], settings_of(document)
        pool = document.get("pool")
        on = isinstance(pool, dict) and pool.get("meaning_uncut") is True
        if (not on) if MODE == "pool-meaning-only" else (pool != standard["pool"]):
            found.append({"setting": "pool", "value": pool if on else False})
        for name in ("reranker", "reranker_service", "bundle_tokens"):
            if settings[name] != standard[name]:
                found.append({"setting": name, "value": settings[name]})
        return found

    def _document(root):
        path = Path(root) / "governance/project/retrieval.yaml"
        return (yaml.safe_load(path.read_text(encoding="utf-8")) or {}) if path.is_file() else {}

    def _decided(found, decisions):
        cited = {}
        for item in decisions:
            decision, _, setting = str(item).partition(":")
            cited[setting or None] = decision
        return [{**d, "decision": cited.get(d["setting"], cited.get(None))} for d in found]

    def read_standard(root, decisions):
        found = _decided(departures(_document(root)), list(decisions or ()))
        open_ = [d["setting"] for d in found if not d["decision"]]
        if open_:
            raise GovError("STANDARD_DEPARTURE", "settings differ from the standard: " + ", ".join(open_), {"settings": open_})
        return {**settings_of(_document(root)), "departures": found}

    fabric.settings_of, fabric.departures, fabric.read_standard = settings_of, departures, read_standard

    def a9(root, args):
        root = Path(root)
        decisions = list(getattr(args, "decision", None) or [])
        block = read_standard(root, decisions)
        budget = getattr(args, "budget_ms", None) or 2000
        started, figure, reason = time.perf_counter(), None, None
        try:
            reply = fabric.vector_scan(root, "where is the guide?")
            elapsed = (time.perf_counter() - started) * 1000
            if isinstance(reply, dict) and reply.get("available") is True:
                figure = elapsed
            else:
                reason = (reply or {}).get("reason") or "unavailable"
        except Exception as error:  # noqa: BLE001
            elapsed, reason = (time.perf_counter() - started) * 1000, type(error).__name__
        if MODE == "scan-always-a-figure" and figure is None:
            figure = elapsed
        scale = {"routes": {"record": 1.0, "lexical": 1.0, "vectors": 1.0}, "vector_scan_ms": figure, "vector_scan_reason": reason,
                 "budget_ms": budget, "envelope": "DEC-078"}
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        if figure is not None and figure > budget:
            (out / "SCALE-PROPOSAL.md").write_text(f"# A proposal (CIT-P): the vector scan is over the budget\n\n## Evidence\n\n"
                                                   f"The vector scan took {figure:.1f} ms against a budget of {budget} ms (measure).\n\n"
                                                   f"## Proposal\n\nThe owner decides.\n", encoding="utf-8")
        rel = "governance/adoption/A9-fabric.md"
        (root / "governance/adoption").mkdir(parents=True, exist_ok=True)
        front = yaml.safe_dump({"id": "ADOPT-A9", "stage": "A9", "standard": block, "scale": scale}, sort_keys=False)
        (root / rel).write_text("---\n" + front + "---\n\n# ADOPT-A9\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", rel], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "A9 stand-in record"], check=True, capture_output=True)
        return {"stage": "A9", "record": rel}

    original_run = stages.run

    def run(root, args, config):
        if args.stage == "A9":
            return a9(Path(root), args)
        return original_run(root, args, config)

    stages.run = run

    # ---- (2) a load does not make a stale store current ------------------------------------------------------------
    real_load = loader.load

    def load(root, *more, **keywords):
        import sqlite3
        db = Path(root) / ".gov-runtime" / "store.db"
        stale, before = False, None
        if db.is_file():
            conn = sqlite3.connect(db)
            try:
                before = layout.version_of(conn)
                try:
                    layout.check(conn, str(db))
                except GovError:
                    stale = True
            finally:
                conn.close()
        result = real_load(root, *more, **keywords)
        conn = sqlite3.connect(db)
        try:
            if MODE == "stamps-always":
                layout.stamp(conn)
            elif stale:
                table = layout.STAMP_TABLE
                if before is None:
                    conn.execute(f"DROP TABLE IF EXISTS {table}")
                else:
                    columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]
                    rows = conn.execute(f"SELECT * FROM {table}").fetchall()
                    for index, column in enumerate(columns):
                        if rows and rows[0][index] == layout.LAYOUT_VERSION:
                            conn.execute(f"UPDATE {table} SET {column} = ?", (before,))
            conn.commit()
        finally:
            conn.close()
        return result

    loader.load = load


try:
    _install()
except Exception as exc:  # noqa: BLE001
    sys.stderr.write(f"standin_b1: not installed: {exc!r}\n")
