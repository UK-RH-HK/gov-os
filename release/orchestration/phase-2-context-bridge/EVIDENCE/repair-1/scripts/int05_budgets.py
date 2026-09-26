"""BR-AR-0028 check 5: section-by-section budget audit of a compiled packet directory.

Usage: $PY int05_budgets.py <packet_dir> [<budgets.yaml>]
Measures each section's RENDERED bytes straight from packet.md (split on the exact "## <L>. <TITLE>" header lines
govbridge.compile.render emits, each section ending at its own read_token line), and the manifest's own per-item
bytes, then compares with the task's budget profile in config/budgets.yaml. A cap is the profile's
section_caps_kb * 1024; the config's section_header_bytes is reported as the per-section allowance the compiler
adds on top of item bytes. Also reports: A (never truncated) and J sizes, main packet bytes vs total_kb, every
supplementary packet's bytes, the delivery mix of each over-cap section, and where section I was assembled.
"""
import json
import sys
from pathlib import Path

import yaml

D = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(D))
from govbridge.compile import render as rendermod  # noqa: E402


def main():
    pdir = Path(sys.argv[1])
    budgets = Path(sys.argv[2]) if len(sys.argv) > 2 else D / "config" / "budgets.yaml"
    cfg = yaml.safe_load(budgets.read_text())
    manifest = json.loads((pdir / "manifest.json").read_text())
    ts = yaml.safe_load((pdir / "task_spec.yaml").read_text())
    profile = cfg["profiles"][ts["budget_profile"]]
    caps = {k: (v * 1024 if v is not None else None) for k, v in profile["section_caps_kb"].items()}
    header_allow = cfg.get("section_header_bytes", 0)
    text = (pdir / "packet.md").read_text(encoding="utf-8")
    lines = text.split("\n")
    headers = {f"## {L}. {rendermod.SECTION_TITLES[L]}": L for L in rendermod.SECTION_LETTERS}
    starts = [(i, headers[l]) for i, l in enumerate(lines) if l in headers]
    rendered = {}
    for n, (i, L) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        rendered[L] = len(("\n".join(lines[i:end]) + "\n").encode("utf-8"))

    def rows_of(L):
        sec = manifest["sections"].get(L) or {}
        if L == "D":
            return [r for sub in (sec.get("subblocks") or {}).values() for r in (sub.get("items") or [])]
        return sec.get("items") or []

    out = {"packet_dir": str(pdir), "profile": ts["budget_profile"], "total_kb": profile["total_kb"],
           "section_header_bytes_allowance": header_allow, "main_packet_bytes": len(text.encode("utf-8")),
           "sections": {}}
    for L in rendermod.SECTION_LETTERS:
        rows = rows_of(L)
        deliveries = {}
        for r in rows:
            deliveries[r.get("delivery")] = deliveries.get(r.get("delivery"), 0) + 1
        item_bytes = sum(int(r.get("bytes") or 0) for r in rows)
        cap = caps.get(L)
        rb = rendered.get(L)
        exempt = cap is None
        out["sections"][L] = {
            "rendered_bytes": rb, "manifest_item_bytes": item_bytes, "items": len(rows), "deliveries": deliveries,
            "cap_bytes": cap, "exempt": exempt,
            "within_cap_rendered": None if exempt or rb is None else rb <= cap,
            "within_cap_plus_header_allowance": None if exempt or rb is None else rb <= cap + header_allow,
            "dropped": manifest["sections"].get(L, {}).get("dropped"),
        }
    out["main_exceeds_total"] = out["main_packet_bytes"] > profile["total_kb"] * 1024
    supp = []
    sroot = pdir / "supplementary"
    if sroot.is_dir():
        for q in sorted(p for p in sroot.iterdir() if p.is_dir()):
            b = (q / "packet.md").stat().st_size
            sm = json.loads((q / "manifest.json").read_text())
            supp.append({"query_id": q.name, "packet_bytes": b, "items": sum(len(s.get("items") or [])
                                                                               for s in sm.get("sections", {}).values())})
    out["supplementary"] = supp
    out["supplementary_bytes_total"] = sum(s["packet_bytes"] for s in supp)
    notes = pdir / "notes"
    out["notes_bytes_total"] = sum(p.stat().st_size for p in notes.iterdir()) if notes.is_dir() else 0
    out["main_plus_supplementary_bytes"] = out["main_packet_bytes"] + out["supplementary_bytes_total"]
    over = [L for L, s in out["sections"].items() if s["within_cap_plus_header_allowance"] is False]
    out["non_exempt_sections_over_cap_plus_allowance"] = over
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
