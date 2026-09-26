"""BR-AR-0028 check 4: write a SYNTHETIC receipt (schemas/receipt.yaml shape) for a compiled packet directory.

Usage: $PY int04_receipt.py <packet_dir> <out.json> [--omit-supplementary]
The receipt acknowledges the main packet and every DIR/supplementary/<qid>/ packet (packet_sha256 and manifest_sha256
lists), carries the ten read tokens recomputed from manifest_sha256, acknowledges every section-A item by
ID@content_sha256, relies on one real item, and declares one real external read (a 1-line window of a file at the
recorded records commit). --omit-supplementary drops the supplementary acknowledgements (a negative control).
"""
import hashlib
import json
import sys
from pathlib import Path


def main():
    d, out = Path(sys.argv[1]), Path(sys.argv[2])
    omit = "--omit-supplementary" in sys.argv
    m = json.loads((d / "manifest.json").read_text())
    m_sha = m["manifest_sha256"]
    hashes, m_hashes = [m["packet_sha256"]], [m_sha]
    supp_root = d / "supplementary"
    if supp_root.is_dir() and not omit:
        for q in sorted(p for p in supp_root.iterdir() if p.is_dir()):
            sm = json.loads((q / "manifest.json").read_text())
            hashes.append(sm["packet_sha256"])
            m_hashes.append(sm["manifest_sha256"])
    tokens = {L: hashlib.sha256((m_sha + L).encode()).hexdigest()[:12] for L in "ABCDEFGHIJ"}
    a_rows = m["sections"]["A"]["items"]
    relied = None
    for letter, sec in m["sections"].items():
        rows = sec.get("items") or []
        if letter == "D":
            rows = [r for sub in (sec.get("subblocks") or {}).values() for r in (sub.get("items") or [])]
        if rows and letter != "A":
            relied = rows[0]["item_id"]
            break
    records_commit = next(r["commit"] for r in m["view"] if r["name"] == "records")
    receipt = {
        "context_packet_hash": hashes, "manifest_sha256": m_hashes, "read_tokens": tokens,
        "inputs_consumed": [f"{r['unit']['id']}@{r['content_sha256']}" for r in a_rows],
        "items_relied_on": [relied] if relied else [],
        "external_reads": [{"path": "release/orchestration/phase-2-context-bridge/README.md", "commit": records_commit,
                            "lines": [1, 1], "why": "synthetic receipt: one declared external read (R1-INT)"}],
        "outputs_produced": [], "decisions_applied": [], "acceptance_evidence": [], "deviations": [], "unresolved": [],
    }
    out.write_text(json.dumps(receipt, indent=1, sort_keys=True))
    print(json.dumps({"receipt": str(out), "acknowledged_packets": len(hashes), "a_items": len(a_rows),
                      "omit_supplementary": omit}))


if __name__ == "__main__":
    main()
