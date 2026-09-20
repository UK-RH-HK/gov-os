#!/usr/bin/env bash
# Build the held-out corpus: a disposable governed project carrying records of every C1 kind, multi-language source
# with route registrations / DB models / inheritance, an archive, and content planted only inside list-valued and
# nested record fields. Echoes the project root.
#
# Every distinctive token below is a NEEDLE: a string that occurs in exactly one place in the corpus, so a retrieval
# result that contains it can only have come from that place.
set -uo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

build_corpus() {
  local root; root=$(new_project "${1:-corpus}" greenfield)

  mkdir -p "$root/src/app" "$root/src/web" "$root/src/svc" "$root/archive/governance"
  mkdir -p "$root/spec/product" "$root/spec/features" "$root/spec/requirements" "$root/spec/decisions" \
           "$root/spec/scenarios" "$root/spec/tasks" "$root/spec/interfaces" "$root/spec/releases" \
           "$root/spec/lessons" "$root/spec/experiments" "$root/spec/research" "$root/spec/reports"

  # ---------------- multi-language source (C5, C4, D3) ----------------
  cat > "$root/src/app/orders.py" <<'PY'
"""Order service."""
from flask import Flask
from sqlalchemy import Column, Integer, String
from .base import Base, BaseRepository

app = Flask(__name__)
ERR_LEDGER_UNBALANCED = "ERR_LEDGER_UNBALANCED_7731"

class OrderModel(Base):
    __tablename__ = "orders_table_hx91"
    id = Column(Integer, primary_key=True)
    sku = Column(String)

class OrderRepository(BaseRepository):
    def find_by_sku(self, sku):
        # marker: pyfindbysku_marker_0042
        return self.session.query(OrderModel).filter_by(sku=sku).all()

    def total_cents(self, rows):
        return sum(r.quantity * r.unit_cents for r in rows)

@app.route("/api/v2/orders", methods=["GET", "POST"])
def list_orders():
    return OrderRepository().find_by_sku("x")

def _module_level_helper():
    return ERR_LEDGER_UNBALANCED

CONFIG_KEY_RETRY_BUDGET = "retry.budget.max_attempts"
PY

  cat > "$root/src/app/base.py" <<'PY'
class Base:
    pass

class BaseRepository:
    def __init__(self):
        self.session = None
PY

  cat > "$root/src/web/client.ts" <<'TS'
import { HttpClient } from "./http";

export interface Payer {
  pay(amountCents: number): Promise<void>;
}

export class CardPayer implements Payer {
  async pay(amountCents: number): Promise<void> {
    // marker: tscardpayer_marker_5150
    await new HttpClient().post("/api/v2/pay", { amountCents });
  }
  private auditTrail(): string {
    return "TS_AUDIT_TRAIL_9021";
  }
}

export const router = {
  get: (p: string) => p,
};
router.get("/api/v2/health");
TS

  cat > "$root/src/web/http.ts" <<'TS'
export class HttpClient {
  async post(path: string, body: unknown): Promise<void> {
    void path; void body;
  }
}
TS

  cat > "$root/src/svc/Ledger.java" <<'JAVA'
package svc;

import javax.persistence.Entity;
import javax.persistence.Table;

@Entity
@Table(name = "ledger_entries_jv77")
public class LedgerEntry extends AbstractEntry implements Auditable {
    private long amountCents;

    public long amountCents() {
        // marker: javaamountcents_marker_3310
        return amountCents;
    }
}
JAVA

  cat > "$root/src/svc/handler.go" <<'GO'
package svc

import "net/http"

type LedgerHandler struct{}

func RegisterRoutes(mux *http.ServeMux) {
	mux.HandleFunc("/api/v2/ledger", handleLedger)
}

func handleLedger(w http.ResponseWriter, r *http.Request) {
	// marker: gohandleledger_marker_7788
	_ = w
	_ = r
}
GO

  # ---------------- governed records of every C1 kind ----------------
  cat > "$root/spec/product/PRJ-0001.yaml" <<'Y'
id: PRJ-0001
type: project
title: Held-out ledger project
status: ACTIVE
intent: prove C1 project truth
Y
  cat > "$root/spec/features/F-0001.yaml" <<'Y'
id: F-0001
type: feature
title: Order totals
status: ACTIVE
capability_category: backend
requirements: [REQ-0001]
scenarios: [SCN-0001]
interfaces: [API-0001]
acceptance_tests: [TST-0001]
Y
  # every readiness dimension PRESENT, from the kernel taxonomy itself, so the baseline is legitimately green
  python3 - "$root" "$BETA_WT" <<'PY'
import sys, re, io
root, wt = sys.argv[1], sys.argv[2]
dims = []
for line in open(f"{wt}/framework/taxonomy/READINESS_DIMENSIONS.yaml"):
    m = re.match(r"\s*-\s*\{id:\s*([a-z_]+)", line)
    if m: dims.append(m.group(1))
assert dims, "no readiness dimensions parsed"
with open(f"{root}/spec/features/F-0001.yaml", "a") as f:
    f.write("readiness:\n")
    for d in dims:
        f.write(f"  {d}: PRESENT\n")
PY
  cat > "$root/spec/requirements/REQ-0001.yaml" <<'Y'
id: REQ-0001
type: requirement
title: Ledger totals are exact integer cents
status: ACTIVE
feature: F-0001
kind: functional
governed_by: [D-0001]
acceptance_criteria:
  - the running total NEEDLEACCEPT4417 must equal the sum of quantity times unit_cents
  - rounding is prohibited at every step
Y
  cat > "$root/spec/decisions/D-0001.yaml" <<'Y'
id: D-0001
type: decision
title: Integer cents only
status: ACTIVE
decision: store money as integer cents
options:
  - id: A
    summary: integer cents NEEDLEOPTION8823 chosen for exactness
  - id: B
    summary: decimal floats rejected
rationale: floats lose exactness
Y
  cat > "$root/spec/scenarios/SCN-0001.yaml" <<'Y'
id: SCN-0001
type: scenario
title: Append two orders and total
status: ACTIVE
feature: F-0001
actor: clerk
given:
  - an empty ledger NEEDLEGIVEN2266
when:
  - two orders are appended
then:
  - total_cents is 399
success_criteria: [exact total]
failure_criteria: [duplicate ids accepted]
data_requirements_not_applicable: literal values inside the acceptance test
Y
  cat > "$root/spec/tasks/TST-0001.yaml" <<'Y'
id: TST-0001
type: test-obligation
title: Ledger acceptance tests
status: ACTIVE
feature: F-0001
scenario: SCN-0001
family: acceptance
test_path: tests/ledger_test.rs
author_role: independent-test-designer
independent_of_implementer: true
Y
  cat > "$root/spec/interfaces/API-0001.yaml" <<'Y'
id: API-0001
type: interface
title: Ledger HTTP interface
status: ACTIVE
surface: http
operations:
  - name: listOrders
    method: GET
    path: /api/v2/orders
    note: NEEDLEIFACE9034 listing contract
Y
  cat > "$root/spec/releases/REL-0001.yaml" <<'Y'
id: REL-0001
type: release
title: Ledger 1.0
status: ACTIVE
version: 1.0.0
derived_from: [F-0001]
validated_by: [TST-0001]
Y
  cat > "$root/spec/lessons/L-0001.yaml" <<'Y'
id: L-0001
type: lesson
title: Float totals drifted in production
status: ACTIVE
scope: PROJECT
what_failed: decimal floats accumulated error NEEDLELESSON5512
correction: integer cents
Y
  cat > "$root/spec/research/RES-0100.yaml" <<'Y'
id: RES-0100
type: research
title: Rounding strategies compared
status: ACTIVE
state_class: EVIDENCE
research_state: CONCLUDED
question: which rounding strategy preserves exactness NEEDLERESEARCH6644
reason: the ledger drifted in production
method: replayed ten thousand ledgers
sources: [L-0001]
measurements:
  - drift observed with floats was NEEDLEMEASURE1188 cents over ten thousand rows
uncertainty: bounded by the replay corpus
conclusion: integer cents
confidence: 0.9
Y
  cat > "$root/spec/reports/RPT-0100.yaml" <<'Y'
id: RPT-0100
type: report
title: Ledger close report
status: ACTIVE
summary: the ledger work closed with NEEDLEREPORT9922 outstanding observations
derived_from: [RES-0100]
Y
  mkdir -p "$root/archive/governance"
  cat > "$root/archive/governance/OLD-RULES.md" <<'MD'
# Superseded ledger rules
Historical: totals were stored as floats. NEEDLEARCHIVE7001 is historical-only content.
MD

  ( cd "$root" && git add -A && git commit -q -m corpus ) >/dev/null 2>&1
  echo "$root"
}

# The administrator-domain material for this run: a throw-away Signed Release Root and a signed release of the
# candidate's own payload (OWNER-DECISION-P2-0002's documented "provision, then install" path). Published once per
# RUN-ALL invocation, outside every project. Echoes the admin dir.
admin_domain() {
  local admin="$BETA_SCRATCH/admin-domain"
  if [ ! -f "$admin/root-1.json" ]; then
    mkdir -p "$admin"
    python3 "$(dirname "${BASH_SOURCE[0]}")/provision.py" publish "$BETA_WT" "$BETA_SCRATCH/release-domain" "$admin" 100 \
      > "$admin/published.json" || return 1
  fi
  echo "$admin"
}

# A corpus project on a PROVISIONED machine carrying an authentic, current installation, so its governance record can
# legitimately be green (P2-ADJ-0003: a probe that needs a green baseline builds one that is legitimately green).
build_corpus_provisioned() {
  local admin; admin=$(admin_domain) || { echo "ADMIN_FAILED"; return 1; }
  local root; root=$(build_corpus "${1:-corpusp}")
  gov "$root" trust provision --anchor "$admin/root-1.json" >/dev/null 2>&1
  # P2-ADJ-0002: bind the machine to the owner's T2 binding authority, so OS-written facts it seals are the owner's
  gov "$root" trust bind --authority "$admin/t2-binding-authority.json" --key "$admin/t2-binding-key.json" >/dev/null 2>&1
  gov "$root" init --name "${1:-corpusp}" --source "$BETA_SCRATCH/release-domain/releases/4.1.6" >/dev/null 2>&1
  echo "$root"
}

# Answer a Human Decision Gate as the product owner: present it, sign the exact package the OS rendered, relay it.
# owner_answers <root> <gate id> <option>
owner_answers() {
  local root="$1" gate="$2" option="${3:-A}"
  local admin; admin=$(admin_domain) || return 1
  gov "$root" gate present "$gate" > "$BETA_SCRATCH/$gate.package.json" 2>&1 || return 1
  python3 "$(dirname "${BASH_SOURCE[0]}")/provision.py" answer "$admin" \
    "$BETA_SCRATCH/$gate.package.json" "$option" "$BETA_SCRATCH/$gate.answer.json" >/dev/null || return 1
  gov "$root" decide "$gate" --option "$option" --answer-file "$BETA_SCRATCH/$gate.answer.json"
}
