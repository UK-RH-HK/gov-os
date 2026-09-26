#!/usr/bin/env python3
"""Incremental freshness/invalidation (ARCHITECTURE.md section 3). Change detection uses Git object ids and config
hashes only -- no model call is ever part of determining or acting on NOOP/INCREMENTAL/FULL.

Layer-builder registration mirrors ``manifest.register_layer``: B1 registers its own builder (the ``core`` layer:
occurrence + blob + chunk) below; B2-B5 register their own builders from their own packages at import time, so
``freshness rebuild --layer <name>`` can reach them without this file ever being edited again.
"""
from __future__ import annotations

import argparse
import dataclasses
import importlib
import json
import pkgutil
import sys
import time
from pathlib import Path
from typing import Callable, Optional

from govbridge.core import corpus, gitobj, manifest as manifestmod, store, telemetry, view as viewmod
from govbridge.core.chunking import CHUNKER_VERSION, chunk_id, chunk_text, text_sha256
from govbridge.core.yamlutil import canonical_json, sha256_file, sha256_text

TRIGGER_NOOP = "NOOP"
TRIGGER_INCREMENTAL = "INCREMENTAL"
TRIGGER_FULL = "FULL"

BuilderFn = Callable[..., dict]
_LAYER_BUILDERS: dict[str, BuilderFn] = {}


def register_layer_builder(name: str, fn: BuilderFn) -> None:
    _LAYER_BUILDERS[name] = fn


def get_layer_builders() -> dict[str, BuilderFn]:
    return dict(_LAYER_BUILDERS)


_LAYER_PACKAGES_IMPORTED = False


def ensure_all_layer_packages_imported() -> list[str]:
    """Import every sibling package under ``govbridge/`` once, so each layer's OWN ``register_layer_builder``/
    ``register_layer`` calls (which run at ITS import time -- B2's own documented extension point) have happened
    before a caller asks for a layer by name in a process that has not otherwise imported it (B2 OI-1/B4 OI-1:
    a bare ``freshness rebuild --layer lexical`` raises ``KeyError`` unless something already imported
    ``govbridge.lexical``). Generic and central (routed to I1/BR-DAG-AMEND-2: "the CLI, and core freshness,
    discover and import every layer package deterministically"): this function names no specific layer package,
    ever -- it discovers them by walking ``govbridge``'s own immediate subpackages and skipping only ``core``
    (this package, already imported by definition). A package that raises on import (or registers nothing, like
    ``route``/``compile``) is skipped without failing the caller's actual request."""
    global _LAYER_PACKAGES_IMPORTED
    if _LAYER_PACKAGES_IMPORTED:
        return []
    import govbridge
    imported = []
    for modinfo in pkgutil.iter_modules(govbridge.__path__):
        if not modinfo.ispkg or modinfo.name == "core":
            continue
        try:
            importlib.import_module(f"govbridge.{modinfo.name}")
            imported.append(modinfo.name)
        except Exception:
            continue
    _LAYER_PACKAGES_IMPORTED = True
    return imported


# ---------------------------------------------------------------------------------------------------------------
# Fingerprint: the cheap, Git-only comparison that decides the trigger.
# ---------------------------------------------------------------------------------------------------------------

def _config_sha256(view_path: str, rules_path: str) -> dict:
    """sha256 of every config file that affects this build: everything in view_path's own directory (so a future
    layer's config -- id-grammar.yaml, embed-profile.yaml, ... -- is picked up automatically once it lands there),
    PLUS the actual rules_path in use, explicitly (it can live elsewhere, e.g. in a test fixture)."""
    out: dict = {}
    config_dir = Path(view_path).parent
    if config_dir.is_dir():
        for f in sorted(config_dir.iterdir()):
            if f.is_file() and (f.suffix in (".yaml", ".yml") or f.name == "requirements.lock"):
                out[f.name] = sha256_file(str(f))
    rp = Path(rules_path)
    if rp.is_file():
        out[rp.name] = sha256_file(str(rp))
    return out


def compute_fingerprint(view_path: str, rules_path: str, repo: Optional[str] = None,
                         records_ref: Optional[str] = None) -> tuple[dict, "viewmod.ResolvedView"]:
    """``records_ref``, if given, overrides the resolved ``records`` ref's commit (the DAG's own I1 acceptance
    check: "index rebuild --from-clean --records-ref <earlier bridge commit> then index update to the current
    view", proving incremental == full from an EARLIER point in this bridge's own history, not just from an
    already-current one). It never touches any other named ref or the history glob; "records" is used by NAME
    here, the same established convention every other module in this package already uses
    (``resolved_view.ref_commit("records")``, throughout govbridge.authority/.compile/.graph)."""
    config = viewmod.load_view(view_path)
    resolved = viewmod.resolve_view(config, repo=repo)
    if records_ref:
        old = resolved.named.get("records")
        if old is None:
            raise ValueError("canonical-view has no ref named 'records' to override with --records-ref")
        commit = gitobj.resolve_commit(records_ref, repo=repo)
        if commit is None:
            raise ValueError(f"--records-ref {records_ref!r} does not resolve")
        resolved.named["records"] = dataclasses.replace(old, commit=commit)
    refs = {name: r.commit for name, r in resolved.named.items()}
    history = sorted(resolved.history)
    return {
        "view_id": resolved.view_id,
        "refs": refs,
        "history": history,
        "config_sha256": _config_sha256(view_path, rules_path),
        "code_tree": manifestmod.bridge_code_tree(repo=repo),
        "chunker_version": CHUNKER_VERSION,
    }, resolved


def _manifest_path() -> Path:
    return store.store_root() / "manifest.json"


def load_previous_manifest() -> Optional[dict]:
    p = _manifest_path()
    if not p.exists():
        return None
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_manifest(m: dict) -> None:
    p = _manifest_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(canonical_json(m))


def determine_trigger(fingerprint: dict, previous: Optional[dict], from_clean: bool) -> tuple[str, list[str]]:
    if from_clean or previous is None:
        return TRIGGER_FULL, []
    prev_fp = previous.get("fingerprint")
    if prev_fp is None:
        return TRIGGER_FULL, []
    if (prev_fp.get("config_sha256") != fingerprint["config_sha256"]
            or prev_fp.get("code_tree") != fingerprint["code_tree"]
            or prev_fp.get("chunker_version") != fingerprint["chunker_version"]):
        return TRIGGER_FULL, []
    changed = []
    if prev_fp.get("refs") != fingerprint["refs"]:
        for name, commit in fingerprint["refs"].items():
            if prev_fp.get("refs", {}).get(name) != commit:
                changed.append(name)
    prev_hist = dict(prev_fp.get("history") or [])
    cur_hist = dict(fingerprint["history"])
    if prev_hist != cur_hist:
        for name, commit in cur_hist.items():
            if prev_hist.get(name) != commit:
                changed.append(name)
    # B1 OI-5: a history ref (e.g. a phase2/* tip) that existed in the previous build's fingerprint and is simply
    # GONE from the current one (deleted, never renamed -- a rename is itself just "one name disappears, another
    # appears", already covered by the comparison above) is a change too, even though nothing in `changed` above
    # can see it (it is absent from `fingerprint["history"]` entirely, so the loop over CURRENT names never visits
    # it). Detected here, and threaded through as a distinct list so `core_layer_builder` can drop its stale
    # occurrence rows -- see `_removed_history_refs` there -- without needing to re-walk any tree for it.
    removed_history = sorted(set(prev_hist) - set(cur_hist))
    if changed or removed_history:
        return TRIGGER_INCREMENTAL, changed
    return TRIGGER_NOOP, []


# ---------------------------------------------------------------------------------------------------------------
# The "core" layer builder: occurrence + blob + chunk, over every resolved ref.
# ---------------------------------------------------------------------------------------------------------------

def _rules_path_for(view_path: str) -> str:
    return str(Path(view_path).parent / "corpus-rules.yaml")


def _process_new_blob(conn, entry: "gitobj.TreeEntry", rules, sniffer, seen_blobs: set, stats: dict) -> None:
    """Classify, store and chunk ``entry``'s blob -- but only the FIRST time this build sees it (``seen_blobs``).
    Shared by both the full walk (``_index_one_ref``) and the diff-tree-scoped incremental walk
    (``_index_one_ref_incremental``), so a blob is chunked identically -- and exactly once -- by either path."""
    if entry.oid in seen_blobs:
        return
    seen_blobs.add(entry.oid)
    verdict = corpus.classify_entry(entry, rules, sniffer)
    chunkable_text: Optional[str] = None
    sha256_hex = ""
    if verdict.effect != "EXCLUDE" and entry.mode != "120000":
        is_binary, text = sniffer.get(entry.oid)
        if not is_binary:
            chunkable_text = text
            sha256_hex = sha256_text(text)
    store.put_blob(conn, entry.oid, sha256_hex, entry.size or 0,
                    is_text=(chunkable_text is not None), corpus_rule=verdict.rule_id,
                    corpus_effect=verdict.effect)
    stats["blobs"] += 1
    if chunkable_text is not None:
        for ch in chunk_text(chunkable_text):
            cid = chunk_id(entry.oid, ch.start_line, ch.end_line, CHUNKER_VERSION)
            store.put_chunk(conn, cid, entry.oid, CHUNKER_VERSION, ch.start_line, ch.end_line,
                             text_sha256(ch.text), ch.text)
            stats["chunks"] += 1


def _index_one_ref(conn, ref_name: str, commit: str, rules, repo, seen_blobs: set, stats: dict) -> None:
    """A FULL walk of ``ref_name``@``commit``: every path gets an occurrence row, and every not-yet-seen blob is
    processed via ``_process_new_blob``. Used for a from-clean build, and as the safe fallback for an INCREMENTAL
    ref whose diff-tree-scoped update (``_index_one_ref_incremental``) is unavailable or fails."""
    with gitobj.CatFileBatch(repo=repo) as cat:
        sniffer = corpus.ContentSniffer(cat)
        for entry in gitobj.ls_tree(commit, repo=repo):
            if entry.type == "blob":
                store.put_occurrence(conn, ref_name, commit, entry.path, entry.oid, entry.mode)
                stats["occurrences"] += 1
            if entry.type == "blob":
                _process_new_blob(conn, entry, rules, sniffer, seen_blobs, stats)


def _index_one_ref_incremental(conn, ref_name: str, old_commit: str, new_commit: str, rules, repo,
                                seen_blobs: set, stats: dict) -> None:
    """B1 OI-4: INCREMENTAL, tightened to touch only what ``git diff-tree`` reports changed between ``old_commit``
    and ``new_commit`` (ARCHITECTURE.md section 3's own INCREMENTAL rule: "git diff-tree -r --no-renames old new
    gives the changed paths; only new blobs are chunked... removed occurrences are dropped"). Every UNCHANGED
    path's occurrence row is carried forward to ``new_commit`` by one SQL UPDATE (no git call, no re-read, no
    re-classification) instead of being re-derived by a full ``git ls-tree``; a changed/added path is upserted from
    a targeted ``ls-tree`` of just that one path. This is provably incremental == full: diff-tree (--no-renames)
    partitions ref_name's tree into exactly "changed" and "everything else", and "everything else" is BY
    DEFINITION byte-identical at both commits, so carrying its existing (path, blob_id, mode) row forward is
    exactly what a full walk of ``new_commit`` would also compute for that path. Raises ``gitobj.GitError`` (never
    caught here) if diff-tree itself fails; the caller falls back to ``_index_one_ref`` in that case."""
    diffs = gitobj.diff_tree(old_commit, new_commit, repo=repo)
    changed_paths = [path for _status, path, _old_oid, _new_oid in diffs]

    conn.execute("CREATE TEMP TABLE IF NOT EXISTS _incr_changed_paths(path TEXT PRIMARY KEY)")
    conn.execute("DELETE FROM _incr_changed_paths")
    conn.executemany("INSERT OR IGNORE INTO _incr_changed_paths(path) VALUES (?)", [(p,) for p in changed_paths])
    # every occurrence row for an UNCHANGED path simply moves to the new commit id (same path/blob/mode -- diff-tree
    # guarantees it, so no git call is needed to confirm it)
    conn.execute(
        "UPDATE occurrence SET commit_id=? WHERE ref_name=? AND commit_id=? "
        "AND path NOT IN (SELECT path FROM _incr_changed_paths)",
        (new_commit, ref_name, old_commit),
    )
    # whatever is left at old_commit for this ref is exactly the changed/removed paths -- drop it; a changed path's
    # new row (if any) is written fresh below
    conn.execute("DELETE FROM occurrence WHERE ref_name=? AND commit_id=?", (ref_name, old_commit))
    # REPAIR_DAG.yaml node R1-GA1 (second reopening): a (blob_id, path) pair the delete above just orphaned must
    # not survive in occurrence_distinct_path (INSERT OR IGNORE alone never removes one) -- same transaction,
    # committed together with the rest of this function's own work, never separately.
    store.prune_stale_distinct_paths(conn)

    with gitobj.CatFileBatch(repo=repo) as cat:
        sniffer = corpus.ContentSniffer(cat)
        for status, path, _old_oid, _new_oid in diffs:
            stats["occurrences"] += 1
            if status == "D":
                continue  # deleted: no new occurrence row (already dropped above)
            entry = gitobj.ls_tree_path(new_commit, path, repo=repo)
            if entry is None or entry.type != "blob":
                continue  # became a directory/submodule, or a race with a concurrent mutation -- skip defensively
            store.put_occurrence(conn, ref_name, new_commit, path, entry.oid, entry.mode)
            _process_new_blob(conn, entry, rules, sniffer, seen_blobs, stats)


def _previous_ref_commits() -> dict[str, str]:
    """name -> old commit, from the previous build's OWN fingerprint (named refs and history refs together). Used
    only to decide whether an INCREMENTAL ref-move can use the diff-tree path (a moved ref needs to know what it
    moved FROM); never used for anything the manifest itself depends on."""
    prev = load_previous_manifest()
    prev_fp = (prev or {}).get("fingerprint") or {}
    out = dict(prev_fp.get("refs") or {})
    out.update(dict(prev_fp.get("history") or []))
    return out


def _removed_history_refs(resolved: "viewmod.ResolvedView") -> list[str]:
    """History ref names present in the PREVIOUS build's fingerprint but absent from the CURRENT resolved view --
    B1 OI-5 ("a removed history ref is not detected"): a deleted phase2/*-style tip. Detected here (not in
    ``determine_trigger``, which only needs to know THAT something changed) because dropping the stale occurrence
    rows is core's own job."""
    prev = load_previous_manifest()
    prev_fp = (prev or {}).get("fingerprint") or {}
    prev_hist_names = {name for name, _commit in (prev_fp.get("history") or [])}
    cur_hist_names = {name for name, _commit in resolved.history}
    return sorted(prev_hist_names - cur_hist_names)


def core_layer_builder(conn, resolved: viewmod.ResolvedView, rules, repo, from_clean: bool,
                        changed_refs: Optional[list[str]] = None) -> dict:
    stats = {"occurrences": 0, "blobs": 0, "chunks": 0}
    seen_blobs: set = set()

    if from_clean:
        store.clear_layer_tables(conn)
        for ref_name, commit in resolved.all_ref_commits():
            _index_one_ref(conn, ref_name, commit, rules, repo, seen_blobs, stats)
        conn.commit()
        return stats

    wanted = set(changed_refs or [])
    ref_iter = [(n, c) for n, c in resolved.all_ref_commits() if n in wanted]
    seen_blobs = {row[0] for row in conn.execute("SELECT blob_id FROM blob").fetchall()}
    old_commit_for = _previous_ref_commits()
    for ref_name, new_commit in ref_iter:
        old_commit = old_commit_for.get(ref_name)
        used_diff = False
        if old_commit and old_commit != new_commit and gitobj.rev_parse(old_commit, repo=repo):
            try:
                _index_one_ref_incremental(conn, ref_name, old_commit, new_commit, rules, repo, seen_blobs, stats)
                used_diff = True
            except gitobj.GitError:
                used_diff = False
        if not used_diff:
            conn.execute("DELETE FROM occurrence WHERE ref_name=? AND commit_id!=?", (ref_name, new_commit))
            store.prune_stale_distinct_paths(conn)  # see the incremental path's own comment above
            _index_one_ref(conn, ref_name, new_commit, rules, repo, seen_blobs, stats)

    removed = _removed_history_refs(resolved)
    if removed:
        removed_count = 0
        for ref_name in removed:
            removed_count += conn.execute(
                "SELECT COUNT(*) FROM occurrence WHERE ref_name=?", (ref_name,)
            ).fetchone()[0]
            conn.execute("DELETE FROM occurrence WHERE ref_name=?", (ref_name,))
        store.prune_stale_distinct_paths(conn)  # see the incremental path's own comment above (once for the whole loop)
        stats["occurrences_removed"] = removed_count
        stats["history_refs_removed"] = removed

    conn.commit()
    return stats


register_layer_builder("core", core_layer_builder)


# ---------------------------------------------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------------------------------------------

def _default_view_path(repo: Optional[str] = None) -> str:
    from govbridge import GOV_BRIDGE_DOMAIN
    return str(Path(GOV_BRIDGE_DOMAIN) / "config" / "canonical-view.yaml")


def run(view_path: Optional[str] = None, rules_path: Optional[str] = None, from_clean: bool = False,
        layer: Optional[str] = None, repo: Optional[str] = None, timings: bool = False,
        records_ref: Optional[str] = None) -> dict:
    t0 = time.monotonic()
    ensure_all_layer_packages_imported()  # B2/B4 OI-1: a bare `--layer <name>` must not KeyError
    view_path = view_path or _default_view_path(repo)
    rules_path = rules_path or _rules_path_for(view_path)
    fingerprint, resolved = compute_fingerprint(view_path, rules_path, repo=repo, records_ref=records_ref)
    previous = load_previous_manifest()
    trigger, changed_refs = determine_trigger(fingerprint, previous, from_clean)

    result = {
        "trigger": trigger, "refs_changed": changed_refs, "blobs_processed": 0, "occurrences_processed": 0,
        "chunks_processed": 0, "llm_invocations": 0, "layer": layer or "core",
    }

    if trigger == TRIGGER_NOOP:
        result["manifest_sha256"] = previous["manifest"]["manifest_sha256"] if previous else None
        result["wall_seconds"] = round(time.monotonic() - t0, 3)
        return result

    if trigger == TRIGGER_FULL and store.store_root().exists():
        store.move_store_aside()

    conn = store.open_db()
    rules = corpus.load_rules(rules_path)
    builders = get_layer_builders() if layer is None else {layer: _LAYER_BUILDERS[layer]}
    layer_stats: dict = {}
    layer_seconds: dict = {}
    for name, fn in builders.items():
        lt0 = time.monotonic()
        stats = fn(conn, resolved, rules, repo, from_clean=(trigger == TRIGGER_FULL), changed_refs=changed_refs)
        layer_seconds[name] = round(time.monotonic() - lt0, 3)
        layer_stats[name] = stats
        result["blobs_processed"] += stats.get("blobs", 0)
        result["occurrences_processed"] += stats.get("occurrences", 0)
        result["chunks_processed"] += stats.get("chunks", 0)

    view_block = [
        {"name": n, "commit": c, "role": next((r.role for r in resolved.config.refs if r.name == n), "history")}
        for n, c in resolved.all_ref_commits()
    ]
    pins = {"chunker_version": CHUNKER_VERSION}
    cov = {"note": "coverage is computed by govbridge.core.corpus; not duplicated in the build manifest body"}
    built_manifest = manifestmod.build_manifest(conn, view_block, fingerprint["config_sha256"], pins, cov, repo=repo)
    conn.close()

    combined = {"fingerprint": fingerprint, "manifest": built_manifest}
    save_manifest(combined)

    result["manifest_sha256"] = built_manifest["manifest_sha256"]
    result["wall_seconds"] = round(time.monotonic() - t0, 3)
    if timings:
        result["layer_seconds"] = layer_seconds
        result["layer_stats"] = layer_stats

    telemetry.write_row("builds", {
        "build_id": telemetry.build_id(built_manifest["manifest_sha256"], trigger),
        "trigger": trigger.lower(),
        "manifest_sha256": built_manifest["manifest_sha256"],
        "prev_manifest_sha256": (previous or {}).get("manifest", {}).get("manifest_sha256"),
        "blobs_added": result["blobs_processed"],
        "occurrences_added": result["occurrences_processed"],
        "chunks_added": result["chunks_processed"],
        "wall_seconds": result["wall_seconds"],
        "llm_invocations": 0,
    })
    return result


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.core.freshness")
    sub = p.add_subparsers(dest="cmd", required=True)

    upd = sub.add_parser("update")
    upd.add_argument("--view")
    upd.add_argument("--rules")

    reb = sub.add_parser("rebuild")
    reb.add_argument("--view")
    reb.add_argument("--rules")
    reb.add_argument("--layer")
    reb.add_argument("--from-clean", action="store_true")
    reb.add_argument("--timings", action="store_true")
    reb.add_argument("--records-ref", help="override the resolved 'records' ref's commit for this build (I1's "
                                            "incremental==full proof: build from-clean at an earlier records "
                                            "commit, then `index update` to the current view)")

    args = p.parse_args(argv)
    if args.cmd == "update":
        result = run(view_path=args.view, rules_path=args.rules, from_clean=False)
    elif args.cmd == "rebuild":
        result = run(view_path=args.view, rules_path=args.rules, from_clean=args.from_clean, layer=args.layer,
                      timings=args.timings, records_ref=args.records_ref)
    else:
        return 2
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
