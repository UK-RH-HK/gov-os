#!/usr/bin/env python3
"""Incremental freshness/invalidation (ARCHITECTURE.md section 3). Change detection uses Git object ids and config
hashes only -- no model call is ever part of determining or acting on NOOP/INCREMENTAL/FULL.

Layer-builder registration mirrors ``manifest.register_layer``: B1 registers its own builder (the ``core`` layer:
occurrence + blob + chunk) below; B2-B5 register their own builders from their own packages at import time, so
``freshness rebuild --layer <name>`` can reach them without this file ever being edited again.
"""
from __future__ import annotations

import argparse
import json
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


def compute_fingerprint(view_path: str, rules_path: str, repo: Optional[str] = None) -> tuple[dict, "viewmod.ResolvedView"]:
    config = viewmod.load_view(view_path)
    resolved = viewmod.resolve_view(config, repo=repo)
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
    if changed:
        return TRIGGER_INCREMENTAL, changed
    return TRIGGER_NOOP, []


# ---------------------------------------------------------------------------------------------------------------
# The "core" layer builder: occurrence + blob + chunk, over every resolved ref.
# ---------------------------------------------------------------------------------------------------------------

def _rules_path_for(view_path: str) -> str:
    return str(Path(view_path).parent / "corpus-rules.yaml")


def _index_one_ref(conn, ref_name: str, commit: str, rules, repo, seen_blobs: set, stats: dict) -> None:
    with gitobj.CatFileBatch(repo=repo) as cat:
        sniffer = corpus.ContentSniffer(cat)
        for entry in gitobj.ls_tree(commit, repo=repo):
            if entry.type == "blob":
                store.put_occurrence(conn, ref_name, commit, entry.path, entry.oid, entry.mode)
                stats["occurrences"] += 1
            if entry.type != "blob" or entry.oid in seen_blobs:
                continue
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


def core_layer_builder(conn, resolved: viewmod.ResolvedView, rules, repo, from_clean: bool,
                        changed_refs: Optional[list[str]] = None) -> dict:
    stats = {"occurrences": 0, "blobs": 0, "chunks": 0}
    seen_blobs: set = set()
    if from_clean:
        store.clear_layer_tables(conn)
        ref_iter = resolved.all_ref_commits()
    else:
        # INCREMENTAL: only refs whose commit moved are re-walked (git ls-tree of that one ref, a single fast git
        # call), and every blob already known to the store is skipped without a content read -- so only genuinely
        # new blobs are chunked, exactly the section-3 contract, without needing a separate diff-tree pass.
        wanted = set(changed_refs or [])
        ref_iter = [(n, c) for n, c in resolved.all_ref_commits() if n in wanted]
        for ref_name, commit in ref_iter:
            conn.execute("DELETE FROM occurrence WHERE ref_name=? AND commit_id!=?", (ref_name, commit))
        seen_blobs = {row[0] for row in conn.execute("SELECT blob_id FROM blob").fetchall()}
    for ref_name, commit in ref_iter:
        _index_one_ref(conn, ref_name, commit, rules, repo, seen_blobs, stats)
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
        layer: Optional[str] = None, repo: Optional[str] = None, timings: bool = False) -> dict:
    t0 = time.monotonic()
    view_path = view_path or _default_view_path(repo)
    rules_path = rules_path or _rules_path_for(view_path)
    fingerprint, resolved = compute_fingerprint(view_path, rules_path, repo=repo)
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

    args = p.parse_args(argv)
    if args.cmd == "update":
        result = run(view_path=args.view, rules_path=args.rules, from_clean=False)
    elif args.cmd == "rebuild":
        result = run(view_path=args.view, rules_path=args.rules, from_clean=args.from_clean, layer=args.layer,
                      timings=args.timings)
    else:
        return 2
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
