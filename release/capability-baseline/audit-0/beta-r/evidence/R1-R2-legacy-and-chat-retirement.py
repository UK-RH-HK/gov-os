"""R1 Legacy governance retirement (Contract v3 lines 872-879) and R2 Chat-memory retirement (lines 881-885).

Brownfield fixture + auditor additions the product authors did not see:
  * src/app/rules_loader.py — ACTIVE code that reads the legacy rules file and the chat DB at runtime (a live
    dependency on mechanisms the adoption will retire), wired into main.py so it is not dead code;
  * extra legacy chat knowledge of kinds other than decisions/lessons: a research measurement, a procedure (skill),
    evidence, and a unique durable fact with no cue words.
The adoption is then driven A0..A11 with the product's role separation.
"""
import json
import sqlite3
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from govprobe import *  # noqa
import brownfield  # noqa

MAIN = '''"""Entry point for shipping-quotes."""
from app.retry import with_retry
from app.billing import quote_price
from app.config import GATEWAY_URL
from app.rules_loader import load_rules, recent_answers


def main() -> str:
    price = with_retry(lambda: quote_price(weight_kg=2.0, zone="B"))
    rules = load_rules()
    return f"{GATEWAY_URL}: {price} ({len(rules)} rule chars, {len(recent_answers())} chat answers)"


if __name__ == "__main__":
    print(main())
'''
LOADER = '''"""Runtime loader for the assistant rules and the chat answer cache (legacy behaviour kept alive)."""
import sqlite3

RULES_PATH = ".cursorrules"
CHAT_DB = "memory/chat_history.sqlite"


def load_rules() -> str:
    with open(RULES_PATH) as f:
        return f.read()


def recent_answers():
    return sqlite3.connect(CHAT_DB).execute("select content from messages where role='assistant'").fetchall()
'''
EXTRA_CHAT = [
    {"session": "s3", "messages": [{"role": "assistant", "content": "Research: we benchmarked the carrier gateway at 50 rps; p95 latency was 180 ms (measured February 2025, n=12000 requests)."}]},
    {"session": "s4", "messages": [{"role": "assistant", "content": "Procedure for releasing quote changes: 1) freeze the quote cache 2) run the smoke suite against staging 3) flip the release flag 4) watch error budget for 30 minutes."}]},
    {"session": "s5", "messages": [{"role": "assistant", "content": "The staging carrier gateway host is gw-stg-7.internal and it requires mutual TLS with the ops client certificate."}]},
    {"session": "s6", "messages": [{"role": "assistant", "content": "Evidence: the load test report LT-2025-03 shows zero dropped quotes at 2x peak traffic."}]},
]
fx = (WT / "fixtures/brownfield/project/.chat/sessions.jsonl").read_text()
chat = fx.rstrip("\n") + "\n" + "\n".join(json.dumps(e) for e in EXTRA_CHAT) + "\n"
root = brownfield.prepare("r12", extra_files={"src/app/main.py": MAIN, "src/app/rules_loader.py": LOADER, ".chat/sessions.jsonl": chat})
R = brownfield.roles(root)
EV = root / "spec/audits/GOVERNANCE-ADOPTION"

section("R1-b3 inventory (A0/A1/A2)")
out = brownfield.run_stages(root, "A2")
inv = [json.loads(l) for l in (EV / "01-COLD-INVENTORY.jsonl").read_text().splitlines()]
cls = {json.loads(l)["path"]: json.loads(l) for l in (EV / "02-CLASSIFICATION.jsonl").read_text().splitlines()}
legacy_inv = [(i["path"], i.get("kinds")) for i in inv if set(i.get("kinds", [])) & {"provider_rules", "chat_store", "index_store", "old_governance"}]
log("A1 inventory: files", len(inv), "| legacy mechanisms inventoried:", legacy_inv)
log("A2 classification of legacy/dependent paths:", {p: (cls[p]["class"], cls[p]["authority"]) for p in
    [".cursorrules", "AGENT_RULES_v2.md", ".github/copilot-instructions.md", "memory/chat_history.sqlite", ".chat/sessions.jsonl", ".index/vectors.json", "src/app/rules_loader.py", "docs/DECISIONS.md"] if p in cls})
check("R1-b3", {".cursorrules", "AGENT_RULES_v2.md", "memory/chat_history.sqlite", ".chat/sessions.jsonl"} <= {p for p, _ in legacy_inv},
      "every legacy governance/memory mechanism is inventoried with its kind")

section("R1-b2 mark old governance LEGACY")
leg_marked = {p: cls[p]["authority"] for p in [".cursorrules", "AGENT_RULES_v2.md", ".github/copilot-instructions.md"]}
log("authority assigned at A2:", leg_marked, "| 03-LEGACY-GOVERNANCE-MAP.md present:", (EV / "03-LEGACY-GOVERNANCE-MAP.md").exists())

section("A3..A7")
out.update(brownfield.run_stages(root, "A7"))
cat = [json.loads(l) for l in (EV / "04-TARGET-PATH-MAP.jsonl").read_text().splitlines()]
ent = {e["current_path"]: e for e in cat}
log("A3 actions:", {p: (ent[p]["action"], ent[p]["target_path"]) for p in [".cursorrules", "AGENT_RULES_v2.md", "memory/chat_history.sqlite", ".chat/sessions.jsonl", ".index/vectors.json", "src/app/rules_loader.py"] if p in ent})
log("catalogue consumers/references recorded for the legacy files:", {p: ent[p].get("consumers") for p in [".cursorrules", "memory/chat_history.sqlite"] if p in ent})
loader_after = (root / "src/app/rules_loader.py").read_text() if (root / "src/app/rules_loader.py").exists() else None
log("src/app/rules_loader.py after A6 migration:\n" + (loader_after or "<absent>"))
log("A7 verdict:", out["A7"]["verdict"], "| legacy_in_active_tree:", out["A7"]["legacy_in_active_tree"], "| broken_links:", out["A7"]["broken_links"])

section("A8 legacy memory extraction / retirement")
out.update(brownfield.run_stages(root, "A8"))
a8 = out["A8"]
log("A8 stores:", [(s["path"], s["kind"], s["strings"], s["extracted"], s["disposition"]) for s in a8["stores"]])
created = a8["created_records"]
kinds = sorted({p.split("/")[1] for p in created})
log("records created:", created, "| record directories:", kinds)
texts = {p: (root / p).read_text() for p in created}
def extracted(needle):
    return [p for p, t in texts.items() if needle in t]
for label, needle in [("research measurement", "p95 latency was 180 ms"), ("procedure/skill", "freeze the quote cache"),
                      ("unique fact without cue words", "gw-stg-7"), ("evidence", "LT-2025-03"), ("chat decision", "cap gateway retries at 5")]:
    log(f"  extracted {label!r}:", extracted(needle))
leg = yaml.safe_load((root / "archive/governance/LEG-0001.yaml").read_text())
log("LEG-0001:", {k: leg.get(k) for k in ["status", "state_class", "paths", "archived"]})
check("R1-b2", all(v == "LEGACY" for v in leg_marked.values()) and leg.get("status") == "LEGACY",
      "legacy governance is marked LEGACY at classification and registered in a LEGACY record after retirement")
check("R1-b4-decisions-lessons", bool(extracted("cap gateway retries at 5")) and any("/lessons/" in p for p in created),
      "useful decisions and lessons are extracted from legacy stores into PROVISIONAL records with provenance")
check("R1-b4-skills-research-evidence", bool(extracted("freeze the quote cache")) and bool(extracted("p95 latency was 180 ms")) and bool(extracted("LT-2025-03")),
      "useful skills, research and evidence are extracted too (framework §69: decisions, lessons, skills, evidence, research)")
check("R2-b2", bool(extracted("gw-stg-7")) and bool(extracted("p95 latency was 180 ms")),
      "unique durable knowledge is extracted even when it carries no decision/lesson cue words")

section("R2-b3 dependency proof before retirement")
loader_now = (root / "src/app/rules_loader.py").read_text()
live_refs = [l.strip() for l in loader_now.splitlines() if "chat_history" in l or "cursorrules" in l]
log("active code references to retired stores after A8:", live_refs)
log("retired chat DB exists at original path:", (root / "memory/chat_history.sqlite").exists(), "| at archive:", (root / "archive/governance/memory-stores/chat_history.sqlite").exists())
log("A8 output keys (any dependency-proof field?):", sorted(a8.keys()))
check("R2-b3", not live_refs,
      "retirement of a chat store is preceded by a proof that no active functionality depends on it")

section("A9..A11 and contradiction reconciliation")
out.update(brownfield.run_stages(root, "A10"))
ex = R["executor"]
au1 = ex.ok("adopt", "audit")
log("A11 first audit:", au1["verdict"], au1["findings"], [m["message"][:110] for m in au1["finding_messages"]])
qa = ex.ok("memory", "query", "how many times should gateway calls be retried", "--k", "6")
log("retry question after A10 -> hits:", [(h["artifact_id"], h["status"], h["state_class"]) for h in qa["hits"]])
mf = root / ".governance-runtime/r12-remediate.json"
mf.write_text(json.dumps([{"op": "set_status", "target": "D-0001", "value": "SUPERSEDED", "by": "D-0002"},
                          {"op": "delete_file", "path": "spec/decisions/decision-2-copy.yaml", "reason": "duplicate id"},
                          {"op": "write_file", "path": "src/app/config.py", "content": "import os\nGATEWAY_URL = \"https://gateway.example.internal\"\nGATEWAY_API_KEY = os.environ.get(\"GATEWAY_API_KEY\", \"\")\n"}]))
c = ex.ok("cit", "propose", "--proposal", "Resolve D-0001/D-0002 supersession conflict, remove duplicate decision copy, move secret out of source",
          "--trigger", "governance_change", "--targets", "D-0001,D-0002", "--manifest", str(mf))
sim = ex.ok("cit", "simulate", c["id"])
ex.ok("gate", "present", sim["human_gate"])
ex.ok("decide", sim["human_gate"], "--option", "A", "--by", "owner")
ex.ok("cit", "approve", c["id"], "--by", "owner", "--method", "human")
ex.ok("cit", "execute", c["id"])
au2 = ex.ok("adopt", "audit")
log("A11 after CIT remediation:", au2["verdict"], au2["findings"])
contra = lambda a: [m["message"] for m in a["finding_messages"] if "superseded by" in m["message"] or "duplicate record id" in m["message"]]  # noqa
log("contradiction findings before/after the CIT:", contra(au1), contra(au2), "| remaining findings after:", [m["message"][:100] for m in au2["finding_messages"]])
check("R1-b5", au1["verdict"] == "NOT_ADOPTED_HEALTHY" and len(contra(au1)) >= 2 and not contra(au2) and au2["findings"]["high"] == 0,
      "authority contradictions (superseded-but-ACTIVE, duplicate ids) are detected, block acceptance, and are reconciled through a gated CIT")
log("NOTE: content-level contradictions between retired legacy rules ('Retries: never more than 3') and active decisions are not analysed;"
    " the rules are retired as LEGACY and extracted chat decisions enter as PROVISIONAL (lower precedence than ACTIVE)")

section("R1-b1 activate current authority")
st = ex.ok("status")
doc = body_of(ex.run("doctor"))
log("framework:", st["framework"], "| doctor D001/D003/D013:", [(c["id"], c["ok"]) for c in doc.get("checks", []) if c["id"] in ("D001", "D003", "D013")])
check("R1-b1", (root / "governance/framework.lock").exists() and st["framework"]["version"] and all(c["ok"] for c in doc.get("checks", []) if c["id"] in ("D001", "D003", "D013")),
      "the v4 authority baseline (kernel + lock + overlay) is installed and verified")

section("R1-b6 retire/remove duplicate mechanisms")
gone = {p: (root / p).exists() for p in [".cursorrules", "AGENT_RULES_v2.md", ".github/copilot-instructions.md", ".index/vectors.json", "memory/chat_history.sqlite", ".chat/sessions.jsonl"]}
log("legacy mechanism still at original path:", gone, "| archive listing:", sorted(str(p.relative_to(root)) for p in (root / "archive/governance").rglob("*") if p.is_file())[:12])
check("R1-b6", not any(gone.values()), "duplicate legacy mechanisms (provider rules, old index, chat stores) are removed from the active tree")

section("R1-b7 verify no active dependency remains")
d13 = [c for c in doc.get("checks", []) if c["id"] == "D013"]
a11_checks = {c["criterion"]: c["ok"] for c in au2["checks"]}
log("A11 'legacy governance has no accidental authority':", a11_checks.get("legacy governance has no accidental authority"), "| D013:", d13)
log("active code still reading legacy mechanisms:", live_refs)
check("R1-b7", not live_refs or any("rules_loader" in json.dumps(x) for x in (au2.get("finding_messages", []) + d13)),
      "no active code/config dependency on a retired legacy mechanism remains undetected")

section("R2-b1 raw chat DB is not active/default truth")
rq = ex.ok("memory", "query", "quotes are cached for 10 minutes", "--k", "6")
rqh = ex.ok("memory", "query", "quotes are cached for 10 minutes", "--k", "8", "--include-historical")
log("default retrieval:", [(h["artifact_id"], h["status"]) for h in rq["hits"]])
log("with --include-historical:", [(h["artifact_id"], h["status"]) for h in rqh["hits"]])
arch = q(root, "SELECT path, path_class, default_retrieval, semantic, lexical FROM artifacts WHERE path LIKE 'archive/governance/memory-stores/%'")
log("archived chat stores in the index:", arch, "| excluded:", q(root, "SELECT path, reason FROM excluded WHERE path LIKE '%chat%'"))
check("R2-b1", not any("memory-stores" in h["path"] for h in rq["hits"]) and all(r[2] == 0 for r in arch),
      "the raw chat store is retired to archive, never default-retrieved; only extracted PROVISIONAL records are active")

section("R2-b4 CIT-E / index refresh / regression on retirement")
cits = sorted(p.name for p in (root / "spec/decisions").glob("CIT-*.yaml"))
bl = yaml.safe_load((EV / "00-BASELINE.yaml").read_text())
log("CIT records in the project:", cits, "| A9/A10 verdicts:", bl.get("verdicts", {}).get("A9"), bl.get("verdicts", {}).get("A10"))
retire_cit = [p for p in cits if "memory-stores" in (root / "spec/decisions" / p).read_text() or "chat_history" in (root / "spec/decisions" / p).read_text()]
log("CIT records covering the chat-store retirement:", retire_cit)
check("R2-b4-cit", bool(retire_cit), "the chat-store retirement is executed as a CIT-E transaction")
check("R2-b4-index-regression", (bl.get("verdicts", {}).get("A10") or {}).get("verdict") == "MEMORY_ACCEPTED_FOR_V4_AUDIT",
      "memory indexes are rebuilt (A9) and independently regression-verified (A10) after retirement")
summary()
