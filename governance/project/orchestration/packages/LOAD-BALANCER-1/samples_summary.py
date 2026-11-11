"""PROPOSED, NOT RUN. Read-only: what ~/.gov-os/machine/samples.jsonl holds, per role, before --remeasure is run.
Shows the figures --remeasure would write (it takes the MAXIMUM, not the p95) next to the p50 and p95, so the CTO sees
the gap first. Usage: python3 -I samples_summary.py [path]   (default: ~/.gov-os/machine/samples.jsonl)"""
import json
import os
import sys

path = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.gov-os/machine/samples.jsonl")
lines = [json.loads(x) for x in open(path, encoding="utf-8") if x.strip()]
by_role, every, outside, rebuild = {}, [], [], []
for line in lines:
    for s in line.get("samples", []):
        size = s.get("tree_memory_bytes")
        if not isinstance(size, int):
            continue
        if "kind" in s:
            if s["kind"] == "rebuild":
                rebuild.append(size)
            continue
        every.append(size)
        if s.get("verification") is False:
            outside.append(size)
        by_role.setdefault(s.get("role") or "?", []).append(size)


def pct(values, p):
    values = sorted(values)
    return values[max(0, int(len(values) * p) - 1)] if values else None


def mb(v):
    return "none" if v is None else f"{v / 1e6:,.0f} MB"


print(f"{len(lines)} sample lines, {len(every)} session samples, {len(outside)} marked 'outside verification'")
for role, vals in sorted(by_role.items()):
    print(f"  {role:<22} n={len(vals):<5} p50 {mb(pct(vals, .5)):>10}  p95 {mb(pct(vals, .95)):>10}  max {mb(max(vals)):>10}")
print(f"--remeasure would write: working_size {mb(max(outside) if outside else None)} (p95 of those: {mb(pct(outside, .95))}); "
      f"verification_peak {mb(max(every) if every else None)}; rebuild_peak {mb(max(rebuild) if rebuild else None)} (none = kept as it is)")
