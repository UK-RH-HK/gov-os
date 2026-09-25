#!/usr/bin/env python3
"""Checkpoint and renewal (ARCHITECTURE.md section 7.6, ``schemas/packet-checkpoint.yaml``): ``govbridge renew
--checkpoint <file>``. Satisfies W9: the checkpoint records input ids, versions and hashes, so a long-running
worker renews context at a cost proportional to WHAT CHANGED, never to the corpus.

Renewal:

1. **Freshness check.** If the view/build/task-spec are unchanged, the new ``manifest_sha256`` equals the
   checkpoint's own -- ``RENEW_NOOP``, same packet id, no model call and no re-read.
2. Otherwise the task spec is recompiled and the new manifest diffed against the OLD one (by ``(item_id,
   content_sha256)``) -- ``RENEW_DELTA``: added/changed items in full, removed items by id, and unchanged A items
   by reference (the prior receipt already proved they were consumed). The diff needs the OLD manifest itself (the
   checkpoint alone only proves its hash); callers that kept it pass it as ``old_manifest``.
3. If the recompile is BLOCKED (a mandatory input now missing or mismatched) or BLOCKED_BUDGET, the outcome is
   ``RENEW_BLOCKED``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from typing import Optional

from govbridge.compile import packet as packetmod
from govbridge.compile import render as rendermod
from govbridge.core.yamlutil import load_yaml_file

RENEW_NOOP = "RENEW_NOOP"
RENEW_DELTA = "RENEW_DELTA"
RENEW_BLOCKED = "RENEW_BLOCKED"


def make_checkpoint(run_id: str, compile_result: dict, done: list, open_questions: list, next_action: str,
                     items_relied_on: Optional[list] = None) -> dict:
    manifest = compile_result["manifest"]
    m_sha = manifest["manifest_sha256"]
    read_tokens = {letter: hashlib.sha256((m_sha + letter).encode()).hexdigest()[:12]
                   for letter in rendermod.SECTION_LETTERS}
    view_commits = {row["name"]: row["commit"] for row in manifest["view"]}
    return {
        "run_id": run_id,
        "packet_id": compile_result["packet_id"],
        "manifest_sha256": m_sha,
        "view_commits": view_commits,
        "build_manifest_sha256": manifest.get("build_manifest_sha256"),
        "read_tokens": read_tokens,
        "items_relied_on": list(items_relied_on or []),
        "done": list(done),
        "open_questions": list(open_questions),
        "next_action": next_action,
    }


def _flatten(manifest: dict) -> dict:
    out = {}
    for letter, sec in manifest["sections"].items():
        if letter == "D":
            for sub in sec["subblocks"].values():
                for row in sub["items"]:
                    out[row["item_id"]] = row
        else:
            for row in sec["items"]:
                out[row["item_id"]] = row
    return out


def compute_delta(old_manifest: dict, new_manifest: dict) -> dict:
    old_items, new_items = _flatten(old_manifest), _flatten(new_manifest)
    added_or_changed, unchanged_a_by_reference = [], []
    for item_id, row in new_items.items():
        old_row = old_items.get(item_id)
        if old_row is None or old_row.get("content_sha256") != row.get("content_sha256"):
            added_or_changed.append(row)
        elif row["delivery"] == "MANDATORY":
            unchanged_a_by_reference.append(
                {"item_id": item_id, "unit": row["unit"], "content_sha256": row["content_sha256"]})
    removed = [item_id for item_id in old_items if item_id not in new_items]
    return {"added_or_changed": added_or_changed, "removed": removed,
            "unchanged_a_by_reference": unchanged_a_by_reference}


def renew(task_spec: dict, checkpoint: dict, old_manifest: Optional[dict] = None, routes=None,
          repo: Optional[str] = None, registry_path: Optional[str] = None, budgets_path: Optional[str] = None) -> dict:
    result = packetmod.compile_packet(task_spec, routes=routes or packetmod.FAKE_ROUTES, repo=repo,
                                       registry_path=registry_path, budgets_path=budgets_path)
    new_manifest = result["manifest"]

    if result["status"] in (packetmod.STATUS_BLOCKED, packetmod.STATUS_BLOCKED_BUDGET):
        return {"outcome": RENEW_BLOCKED, "status": result["status"],
                "blocked_reasons": list(result["resolve_result"].blocked_reasons), "manifest": new_manifest,
                "rendered": result["rendered"]}

    if new_manifest["manifest_sha256"] == checkpoint.get("manifest_sha256"):
        return {"outcome": RENEW_NOOP, "packet_id": checkpoint.get("packet_id"),
                "manifest_sha256": checkpoint["manifest_sha256"], "manifest": new_manifest,
                "rendered": result["rendered"]}

    delta = compute_delta(old_manifest, new_manifest) if old_manifest is not None else None
    out = {"outcome": RENEW_DELTA, "new_manifest_sha256": new_manifest["manifest_sha256"],
           "new_packet_id": result["packet_id"], "delta": delta, "manifest": new_manifest,
           "rendered": result["rendered"]}
    if delta is None:
        out["note"] = "no old_manifest supplied: outcome is RENEW_DELTA but the delta itself could not be computed"
    return out


def _load_json_or_yaml(path: str):
    if path.endswith((".yaml", ".yml")):
        return load_yaml_file(path)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.compile.renewal")
    p.add_argument("task_spec")
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--old-manifest")
    p.add_argument("--registry")
    p.add_argument("--budgets")
    args = p.parse_args(argv)

    task_spec = load_yaml_file(args.task_spec)
    checkpoint = _load_json_or_yaml(args.checkpoint)
    old_manifest = _load_json_or_yaml(args.old_manifest) if args.old_manifest else None
    result = renew(task_spec, checkpoint, old_manifest=old_manifest, routes=packetmod.FAKE_ROUTES,
                    registry_path=args.registry, budgets_path=args.budgets)
    printable = {k: v for k, v in result.items() if k not in ("manifest", "rendered")}
    print(json.dumps(printable, indent=1, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
