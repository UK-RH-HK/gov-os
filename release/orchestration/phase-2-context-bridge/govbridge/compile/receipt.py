#!/usr/bin/env python3
"""``govbridge receipt check`` (ARCHITECTURE.md section 7.4, ``schemas/receipt.yaml``): runs the independent
validator on the named packet(s), then checks the worker's consumption receipt against the packet's own manifest.
Diligence evidence, not security: the read tokens prove POSSESSION of the exact bytes, not comprehension.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from typing import Optional

from govbridge.compile import validate as validatemod
from govbridge.core import gitobj
from govbridge.core.yamlutil import load_yaml_file


def _all_items(manifest: dict) -> dict:
    """``item_id -> manifest row``, across every section and D's three sub-blocks."""
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


def check(manifest: dict, receipt: dict, task_spec: dict, repo: Optional[str] = None,
          registry_path: Optional[str] = None) -> dict:
    problems: list = []

    problems += [f"packet verify: {p}" for p in
                 validatemod.verify_packet(manifest, task_spec, repo=repo, registry_path=registry_path)]

    packet_hash = receipt.get("context_packet_hash")
    hashes = packet_hash if isinstance(packet_hash, list) else [packet_hash]
    if manifest.get("packet_sha256") not in hashes:
        problems.append(f"context_packet_hash {hashes!r} does not include this packet's {manifest.get('packet_sha256')!r}")

    manifest_hash = receipt.get("manifest_sha256")
    m_hashes = manifest_hash if isinstance(manifest_hash, list) else [manifest_hash]
    if manifest.get("manifest_sha256") not in m_hashes:
        problems.append(f"manifest_sha256 {m_hashes!r} does not include this packet's {manifest.get('manifest_sha256')!r}")

    m_sha = manifest.get("manifest_sha256") or ""
    for letter, token in (receipt.get("read_tokens") or {}).items():
        expected = hashlib.sha256((m_sha + letter).encode()).hexdigest()[:12]
        if token != expected:
            problems.append(f"read_tokens[{letter!r}] = {token!r}, expected {expected!r} (recomputed from "
                             f"manifest_sha256 -- a worker can only produce this by holding this exact packet "
                             f"version and reaching the end of that section)")

    a_rows = manifest["sections"]["A"]["items"]
    consumed = set(receipt.get("inputs_consumed") or [])
    for row in a_rows:
        tag = f"{row['unit']['id']}@{row['content_sha256']}"
        if tag not in consumed:
            problems.append(f"section A item not acknowledged in inputs_consumed: {tag!r}")

    all_items = _all_items(manifest)
    for item_id in receipt.get("items_relied_on") or []:
        if item_id not in all_items:
            problems.append(f"items_relied_on cites unknown item_id {item_id!r}")

    external_read_files = 0
    external_read_bytes = 0
    for ext in receipt.get("external_reads") or []:
        path, commit, claimed_blob = ext.get("path"), ext.get("commit"), ext.get("blob")
        blob = gitobj.blob_at(commit, path, repo=repo) if (path and commit) else None
        if blob is None or (claimed_blob and blob != claimed_blob):
            problems.append(f"external_read does not resolve to a real blob in the view: {ext!r}")
            continue
        external_read_files += 1
        raw = gitobj.read_blob(blob, repo=repo)
        external_read_bytes += len(raw) if raw else 0

    return {
        "status": "PASS" if not problems else "FAIL",
        "problems": problems,
        "external_read_files": external_read_files,
        "external_read_bytes": external_read_bytes,
    }


def _load_json_or_yaml(path: str):
    if path.endswith((".yaml", ".yml")):
        return load_yaml_file(path)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.compile.receipt")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--manifest", required=True)
    c.add_argument("--receipt", required=True)
    c.add_argument("--task-spec", required=True)
    args = p.parse_args(argv)

    manifest = _load_json_or_yaml(args.manifest)
    receipt = _load_json_or_yaml(args.receipt)
    task_spec = load_yaml_file(args.task_spec)
    result = check(manifest, receipt, task_spec)
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
