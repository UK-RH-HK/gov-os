"""P2-AR-0009 synthetic repository builder (independent evidence, not a product fixture).

Builds a small multi-language, record-rich project ("Repo A style") so the beta-family probes can exercise the
Knowledge Fabric against content the product authors never saw.
"""
from __future__ import annotations

import yaml
from pathlib import Path

from govprobe import Gov, commit_all, init, new_project, write


def y(root: Path, rel: str, data: dict):
    write(root, rel, yaml.safe_dump(data, sort_keys=False))


PY_MODELS = '''"""Order domain models."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AuditedEntity:
    """Mixin carrying audit columns."""

    def touch(self):
        return "touched"


class Order(Base, AuditedEntity):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    sku = Column(String)

    def total_cents(self, quantity, unit_cents):
        return compute_total(quantity, unit_cents)


def compute_total(quantity, unit_cents):
    if quantity < 0:
        raise ValueError("ERR_NEGATIVE_QUANTITY: quantity must be non-negative")
    return quantity * unit_cents
'''

PY_API = '''"""HTTP API for orders."""
from flask import Flask
from app.models import Order, compute_total

app = Flask(__name__)


@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    return {"id": order_id, "total": compute_total(1, 100)}


@app.post("/orders")
def create_order():
    o = Order()
    return {"total": o.total_cents(2, 250)}
'''

PY_TEST = '''from app.models import compute_total


def test_compute_total_multiplies():
    assert compute_total(2, 250) == 500
'''

TS_API = '''import { Router } from "express";
import { formatCents } from "./format";

export interface OrderRepository {
  find(id: number): Promise<Order | null>;
}

export class Order {
  constructor(public id: number, public cents: number) {}
}

export class SqlOrderRepository implements OrderRepository {
  async find(id: number): Promise<Order | null> {
    return new Order(id, 100);
  }
}

export class CachedOrderRepository extends SqlOrderRepository {}

const router = Router();
router.get("/api/orders/:id", async (req, res) => {
  res.json({ cents: formatCents(100) });
});
export default router;
'''

TS_FORMAT = '''export function formatCents(cents: number): string {
  return (cents / 100).toFixed(2);
}
'''

RS_LEDGER = '''//! Ledger core.
pub trait Ledger {
    fn append(&mut self, cents: i64);
    fn total(&self) -> i64;
}

pub struct MemoryLedger {
    entries: Vec<i64>,
}

impl Ledger for MemoryLedger {
    fn append(&mut self, cents: i64) {
        self.entries.push(cents);
    }
    fn total(&self) -> i64 {
        sum_entries(&self.entries)
    }
}

pub fn sum_entries(entries: &[i64]) -> i64 {
    entries.iter().sum()
}
'''

GO_SERVER = '''package server

import "net/http"

func Ping(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("pong"))
}

func Register() {
	http.HandleFunc("/ping", Ping)
}
'''

DOC_RUNBOOK = '''# Ledger operations runbook

The ledger service reconciles nightly.

## Reconciliation procedure

Operators run the reconciliation job after the settlement window closes. The job compares the append-only
ledger with the payment processor export and raises a discrepancy ticket when totals differ.

## Known error strings

If you see `ERR_LEDGER_DRIFT_4711` the settlement export is incomplete; rerun the export before reconciling.
'''

CONFIG = '''gateway:
  max_retries_per_gateway: 5
  settlement_window_minutes: 90
feature_flags:
  enable_cached_order_repository: true
'''


def build_rich(name: str, extra_files: dict | None = None, contract_extra: list | None = None):
    """Create + init the rich project. Returns (root, gov)."""
    files = {
        "src/app/__init__.py": "",
        "src/app/models.py": PY_MODELS,
        "src/app/api.py": PY_API,
        "src/web/api.ts": TS_API,
        "src/web/format.ts": TS_FORMAT,
        "src/core/ledger.rs": RS_LEDGER,
        "src/server/server.go": GO_SERVER,
        "tests/test_models.py": PY_TEST,
        "docs/runbook.md": DOC_RUNBOOK,
        "config/settings.yaml": CONFIG,
        "README.md": "# orders-ledger\n\nProbe project for P2-AR-0009.\n",
    }
    files.update(extra_files or {})
    root = new_project(name, files=files)
    g = Gov(root)
    init(root, g, name="orders-ledger", alias=name, intent="Order ledger with totals and reconciliation")
    # path map: govern docs/ and config/ explicitly (unmatched paths are class `unknown` and never indexed)
    cpath = root / "governance/project/REPOSITORY_CONTRACT.yaml"
    c = yaml.safe_load(cpath.read_text())
    extra = [
        {"pattern": "docs/**", "class": "narrative", "owner_role": "routine-documentation", "semantic_index": True,
         "lexical_index": True, "graph_index": True, "namespace": "spec"},
        {"pattern": "config/**", "class": "tooling", "owner_role": "devops-engineer", "semantic_index": True,
         "lexical_index": True, "namespace": "product"},
    ] + (contract_extra or [])
    # insert before the secret rules so secret classification still wins (later rules override earlier ones)
    idx = next((i for i, r in enumerate(c["paths"]) if r.get("class") == "secret"), len(c["paths"]))
    c["paths"][idx:idx] = extra
    cpath.write_text(yaml.safe_dump(c, sort_keys=False))
    add_records(root)
    g.ok("adapters", "generate", show=False)  # the overlay changed: regenerate derived adapter views
    commit_all(root, "rich project content")
    return root, g


READINESS_DIMS = ["intent_outcome", "user_actor", "journey_workflow", "scenarios", "inputs", "data_model_schema",
    "representative_test_data", "processing_algorithm", "expected_outputs", "functional_requirements",
    "non_functional_requirements", "ux_interactions", "backend_service_behaviour", "database_state_requirements",
    "interface_api_event_contracts", "security_privacy", "integrations", "devops_runtime", "observability",
    "performance_capacity", "cost_constraints", "recovery_fallback", "success_criteria", "failure_criteria",
    "independent_acceptance_tests", "documentation_operations"]


def readiness_all_present():
    return {d: "PRESENT" for d in READINESS_DIMS}


def add_records(root: Path):
    y(root, "spec/features/F-0001.yaml", {"id": "F-0001", "type": "feature", "title": "Order totals",
      "status": "ACTIVE", "capability_category": "backend", "requirements": ["REQ-0001"], "scenarios": ["SCN-0001"],
      "interfaces": ["API-0101"], "readiness": readiness_all_present()})
    y(root, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement",
      "title": "Order totals are exact integer cents", "status": "ACTIVE", "feature": "F-0001", "kind": "functional",
      "acceptance_criteria": ["total_cents equals quantity times unit_cents"],
      "statement": "The ledger computes order totals as exact integer cents without floating point rounding."})
    y(root, "spec/decisions/D-0101.yaml", {"id": "D-0101", "type": "decision",
      "title": "Store money as floating point dollars", "status": "SUPERSEDED", "state_class": "AUTHORITATIVE",
      "question": "How is money represented?", "chosen_option": "float dollars",
      "rationale": "Early prototype stored money as floating point dollars for convenience of display formatting.",
      "affects": ["F-0001"]})
    y(root, "spec/decisions/D-0102.yaml", {"id": "D-0102", "type": "decision",
      "title": "Store money as integer cents", "status": "ACTIVE", "state_class": "AUTHORITATIVE",
      "supersedes": ["D-0101"], "question": "How is money represented?", "chosen_option": "integer cents",
      "rationale": "Floating point rounding produced reconciliation drift; integer cents make totals exact and auditable.",
      "affects": ["F-0001"]})
    y(root, "spec/scenarios/SCN-0001.yaml", {"id": "SCN-0001", "type": "scenario", "title": "Two orders totalled",
      "status": "ACTIVE", "feature": "F-0001", "actor": "clerk", "given": ["an empty ledger"],
      "when": ["two orders are appended"], "then": ["the total is 750 cents"], "success_criteria": ["exact total"],
      "failure_criteria": ["rounding drift"]})
    y(root, "spec/interfaces/API-0101.yaml", {"id": "API-0101", "type": "interface", "title": "Orders HTTP API",
      "status": "ACTIVE", "version": "1.0", "contract": {"GET /orders/{id}": "returns id and total cents", "POST /orders": "creates an order"},
      "summary": "Orders HTTP API: GET /orders/{id} returns id and total cents; POST /orders creates an order"})
    y(root, "spec/experiments/EXP-0001.yaml", {"id": "EXP-0001", "type": "experiment",
      "title": "Cached repository latency experiment", "status": "ACTIVE", "hypothesis": "Caching order lookups halves p95 latency.",
      "method": "Replay one day of traffic against cached and uncached repositories.", "production_merge_allowed": False,
      "result": "p95 latency dropped from 40 ms to 18 ms"})
    y(root, "spec/research/RES-0101.yaml", {"id": "RES-0101", "type": "research",
      "title": "Payment processor export formats", "status": "ACTIVE",
      "question": "Which settlement export format should reconciliation consume?",
      "conclusion": "Use the CSV settlement export; the JSON export omits refunds.", "confidence": 0.7})
    y(root, "spec/tasks/TST-0001.yaml", {"id": "TST-0001", "type": "test-obligation",
      "title": "Independent acceptance test for order totals", "status": "ACTIVE", "feature": "F-0001",
      "scenario": "SCN-0001", "tests": ["REQ-0001"], "family": "acceptance", "independent_of_implementer": True})
    y(root, "spec/architecture/ARCH-0101.yaml", {"id": "ARCH-0101", "type": "architecture",
      "title": "Append-only ledger architecture", "status": "ACTIVE",
      "summary": "Ledger entries are append-only; totals are derived; reconciliation is a nightly batch."})
    y(root, "spec/lessons/L-0101.yaml", {"id": "L-0101", "type": "lesson", "title": "Float money caused drift",
      "status": "ACTIVE", "scope": "PROJECT", "category": "bug", "lifecycle": "candidate",
      "problem_statement": "Reconciliation drift traced to floating point money arithmetic in the prototype.",
      "generic_failure_mode": "binary floating point cannot represent decimal cents exactly",
      "relations": [{"type": "FAILED_BECAUSE", "target": "D-0101"}]})
