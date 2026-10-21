"""Write share-table.md from log/share-*.json: one row per measured ticket (DEC-677)."""
import json

S = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/"
ROWS = [
    ("a-dev", "ORION-sp01", "ORION-sp01"), ("a-dev", "ORION-ad01", "ORION-ad01"), ("a-dev", "ORION-ad02", "ORION-ad02"),
    ("a-dev", "ORION-gp09 (run 2 session)", "ORION-gp09"), ("a-dev", "ORION-gp09 (run 3 session)", "ORION-gp09-r3"),
    ("a-dev", "ORION-im01", "ORION-im01"),
    ("b-dev", "ARGUS-sp01", "ARGUS-sp01"), ("b-dev", "ARGUS-ad01", "ARGUS-ad01"), ("b-dev", "ARGUS-gp13", "ARGUS-gp13"),
    ("b-dev", "ARGUS-im01", "ARGUS-im01"),
    ("this repository", "DAEO-gjjf (test designer)", "DAEO-gjjf"),
]
PARTS = ("sessionstart_packet", "hook_output", "gov_output", "checkpoint_records", "close_records")
out = [
    "# Governance share of the exit run's worker sessions (measured by the main orchestrator, 2026-10-13, DEC-655, DEC-677)",
    "",
    "Command: `gov telemetry <ticket> --json --root <clone> --ticket-session <session id>=<role>` with the merged reader, "
    "Claude Code 2.1.292 read on every ticket, no refusal. Sessions of runs 1 and 2 and the implementation and "
    "test-design sessions of run 3. Tokens are the command's figures; cache reads are reported separately by it.",
    "",
    "| Programme | Ticket | Sessions | Estimated share | Measured parts (packet / hooks / gov output / checkpoints / close) | Measured total | Why not measured | Output tokens | Cache read tokens | Cost |",
    "|---|---|---|---|---|---|---|---|---|---|",
]
for programme, label, name in ROWS:
    r = json.load(open(S + "log/share-" + name + ".json", encoding="utf-8"))["result"]
    g = r["governance_tokens"]
    parts = " / ".join(str(g.get(p)) for p in PARTS)
    why = "; ".join(f"{n['name']}: {n['reason']}" for n in r.get("not_measured", []))
    est = r["governance_share"]["estimated"]
    est = f"{est * 100:.2f} %" if isinstance(est, (int, float)) else str(est)
    out.append(
        f"| {programme} | {label} | {len(r.get('sessions', []))} | {est} | {parts} | {g.get('total')} | {why} | "
        f"{r.get('tokens_out')} | {r.get('cache_read_tokens')} | {r.get('cost'):.2f} |"
    )
open(S + "share-table.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
