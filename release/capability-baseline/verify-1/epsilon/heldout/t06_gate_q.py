#!/usr/bin/env python3
"""Gate Q (Q1-Q4) held-out probes — P2-AR-0050, family epsilon.

Q1 lesson lifecycle (Contract v3:844-852), Q2 decision vs lesson (:854-856), Q3 PROJECT/PRODUCT/FRAMEWORK scope
(:858-859), Q4 the Upstream Export Gate (:861-866).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import check, main  # noqa: E402
from t01_ac5_scheduler import provisioned, converge, res  # noqa: E402
import srr  # noqa: E402

Q1_STAGES = ["candidate", "corroborated", "classified", "proposed", "validated", "approved", "promoted"]

CLEAN = """id: {id}
type: lesson
title: {title}
status: ACTIVE
state_class: EVIDENCE
created: '2026-09-20'
scope: {scope}
lifecycle: {lifecycle}
category: memory-freshness
problem_statement: A generic governance failure mode observed twice.
generic_failure_mode: Index freshness was advisory rather than enforced at close time.
impact: Two sessions retrieved superseded evidence.
evidence_strength: high
suggested_change: Make the freshness check blocking at task close.
sources: [RPT-0001, RPT-0002]
corroboration: [RPT-0001, RPT-0002]
synthetic_reproducer:
  synthetic: true
  description: Minimal repository where a record changes after indexing and a close is attempted.
  files:
    scenario.yaml: |
      steps:
        - gov rebuild-memory
        - edit a governed record
        - gov task close   # expect INDEX_STALE
"""

DIRTY = """id: {id}
type: lesson
title: Zone-B tariff incident at Contoso Freight
status: ACTIVE
state_class: EVIDENCE
created: '2026-09-20'
scope: FRAMEWORK
lifecycle: corroborated
category: product-data
problem_statement: |
  Contoso Freight's zone-B tariff table was wrong. The key AKIAIOSFODNN7EXAMPLE was used by
  /home/contoso/app/src/pricing/tariff.py to reach the internal gateway, and the vector store rows were
  dumped below.
generic_failure_mode: A pricing table went unvalidated.
impact: 41 mispriced quotes for Contoso Freight
evidence_strength: high
suggested_change: |
  Add a data test. The verbatim source follows:
  ```python
  SECRET_KEY = "AKIAIOSFODNN7EXAMPLE"
  def price(zone): return TARIFF[zone] * 1.07
  ```
sources: [RPT-0003]
corroboration: [RPT-0003]
"""


def run():
    p, pub = provisioned("gateq")
    converge(p)
    hc = res(p.run("trust", "human-channel"))
    check("Q-human-channel-available", hc.get("available") is True,
          f"an authenticated human channel exists on this provisioned machine: anchor="
          f"{json.dumps(hc.get('anchor'))[:130]}")

    # ================================================================ Q1 lesson lifecycle
    sch = json.loads(p.read("governance/kernel/schemas/lesson.schema.json"))
    states = sch["properties"]["lifecycle"]["enum"]
    missing = [s for s in Q1_STAGES if s not in states]
    check("Q1-lifecycle-stages-modelled", not missing,
          f"the lesson record models the Contract v3:845-852 stages: {states}; missing={missing}")
    for f, stage in [("sources", "execution/report"), ("corroboration", "corroboration"),
                     ("scope", "scope classification"), ("suggested_change", "rule/skill/retrieval/tool proposal"),
                     ("validated_by", "independent validation")]:
        check(f"Q1-field-{f}", f in sch["properties"],
              f"stage '{stage}' has a record field: {f}")

    # a lesson that has not reached the stages the export needs is refused
    p.write("spec/lessons/L-CAND.yaml", CLEAN.format(id="L-CAND", title="A candidate lesson",
                                                     scope="FRAMEWORK", lifecycle="candidate"))
    p.commit("candidate lesson")
    p.run("rebuild-memory", "--incremental")
    cand = p.run("upstream", "prepare", "L-CAND")
    check("Q1-lifecycle-enforced-at-export",
          (not cand.ok) or (res(cand).get("lifecycle") in ("proposed", "validated", "approved")),
          f"a `candidate` lesson at the export gate: ok={cand.ok} code={cand.error_code} "
          f"{str(cand.error.get('message'))[:180] if not cand.ok else json.dumps(res(cand))[:180]}")

    # ================================================================ Q2 lessons are evidence, not authority
    p.write("spec/lessons/L-AUTH.yaml",
            CLEAN.format(id="L-AUTH", title="A lesson claiming authority", scope="FRAMEWORK",
                         lifecycle="corroborated").replace("state_class: EVIDENCE",
                                                           "state_class: AUTHORITATIVE"))
    p.commit("lesson claiming AUTHORITATIVE")
    p.run("rebuild-memory", "--incremental")
    o = p.run("health", "run", "--no-cache", "--event", "q2")
    fams = res(o)["families"]
    hits = [k for k, v in fams.items()
            if "L-AUTH" in json.dumps(v.get("detail") or {}) or
            ("AUTHORITATIVE" in json.dumps(v.get("detail") or {}) and not v["ok"])]
    st = res(p.run("health", "status"))
    check("Q2-lesson-cannot-claim-authority", bool(hits),
          f"a lesson recorded state_class AUTHORITATIVE: flagged by {hits}; health state={st['state']}; "
          f"schema state_class enum={sch['properties']['state_class']['enum']}")
    aside = p.root.parent / "q-aside"
    aside.mkdir(exist_ok=True)
    (p.root / "spec/lessons/L-AUTH.yaml").rename(aside / "L-AUTH.yaml")  # `rm` denied: MOVED ASIDE
    p.commit("lesson moved aside")
    p.run("rebuild-memory", "--incremental")

    dec = json.loads(p.read("governance/kernel/schemas/decision.schema.json"))
    check("Q2-decision-records-chosen-action",
          any(k in dec["properties"] for k in ("decision", "chosen_option", "outcome")),
          f"the decision record carries the chosen action: "
          f"{[k for k in ('decision', 'chosen_option', 'outcome', 'rationale') if k in dec['properties']]}")

    # ================================================================ Q3 scope eligibility
    for scope, eligible in (("PROJECT", False), ("PRODUCT", False), ("FRAMEWORK", True)):
        lid = f"L-{scope}"
        p.write(f"spec/lessons/{lid}.yaml",
                CLEAN.format(id=lid, title=f"A {scope} lesson", scope=scope, lifecycle="corroborated"))
        p.commit(f"{scope} lesson")
        p.run("rebuild-memory", "--incremental")
        o = p.run("upstream", "prepare", lid)
        if eligible:
            check(f"Q3-{scope}-eligible", o.ok,
                  f"a FRAMEWORK lesson prepares: ok={o.ok} packet={res(o).get('packet_id')} "
                  f"gate={res(o).get('approval_gate') or res(o).get('human_gate')}")
            packet = res(o)
        else:
            check(f"Q3-{scope}-refused", (not o.ok) and "SCOPE" in (o.error_code or ""),
                  f"a {scope} lesson is never eligible for upstream export: ok={o.ok} code={o.error_code}")

    # ================================================================ Q4 Upstream Export Gate
    check("Q4-packet-prepared", isinstance(packet, dict) and packet.get("packet_id"),
          f"packet fields: {sorted(packet)[:12]}")

    # sanitisation: the packet text carries no project/customer identifier and no path
    ptxt = json.dumps(packet)
    scans = packet.get("scans") or {}
    check("Q4-sanitisation-reported", bool(scans),
          f"the gate reports every scan it applied and what it removed: {json.dumps(scans)[:400]}")

    # secret / sensitivity scan and no raw project source or vector-store export
    p.write("spec/lessons/L-DIRTY.yaml", DIRTY.format(id="L-DIRTY"))
    p.commit("lesson carrying a secret, a customer name, a path and raw source")
    p.run("rebuild-memory", "--incremental")
    d = p.run("upstream", "prepare", "L-DIRTY")
    blocked = (not d.ok) or any(k in json.dumps(res(d)) for k in ("BLOCKED", "blocked"))
    check("Q4-secret-scan-blocks", blocked,
          f"a lesson carrying an AWS key, a customer name, an absolute path and verbatim source: "
          f"ok={d.ok} code={d.error_code} {str(d.error.get('message'))[:220] if not d.ok else json.dumps(res(d))[:220]}")
    if not d.ok:
        det = json.dumps(d.details)
        for kind, needle in (("secret", "secret pattern"), ("customer/project identifier", "Contoso"),
                             ("raw code", "code"), ("path", "path")):
            check(f"Q4-reason-{kind.split('/')[0]}", needle.lower() in det.lower(),
                  f"the refusal names the {kind} reason: {det[:200]}")

    # outbound allowlist / default deny
    remote = p.run("upstream", "submit", packet["packet_id"], "--destination", "https://example.invalid/inbox")
    check("Q4-outbound-default-deny", not remote.ok,
          f"a remote destination is refused by default: ok={remote.ok} code={remote.error_code} "
          f"{str(remote.error.get('message'))[:160]}")
    baddir = p.root.parent / "not-an-inbox"
    baddir.mkdir(exist_ok=True)
    bad = p.run("upstream", "submit", packet["packet_id"], "--destination", str(baddir))
    check("Q4-destination-allowlist", not bad.ok,
          f"a destination that is not a canonical lessons/inbox is refused: ok={bad.ok} code={bad.error_code}")

    # human approval is an answered Human Decision Gate, not a caller-asserted string
    inbox = p.root.parent / "canonical" / "lessons" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    asserted = p.run("upstream", "submit", packet["packet_id"], "--destination", str(inbox),
                     "--approved-by", "me, the agent")
    check("Q4-approval-not-caller-asserted", not asserted.ok,
          f"`--approved-by <string>` does not stand in for an answered Human Decision Gate: "
          f"ok={asserted.ok} code={asserted.error_code} {str(asserted.error.get('message'))[:170]}")

    # the owner-signed answer is the only route through
    gate = packet.get("approval_gate") or packet.get("human_gate")
    if gate:
        pres = res(p.run("gate", "present", gate))
        g = pres.get("gate") or {}
        ans = p.root.parent / f"{gate}-answer.json"
        ans.write_text(pub.gate_answer(gate, g.get("gate_instance", ""), g.get("package_sha256", ""),
                                       "A", f"eps-{gate}"))
        dec_o = p.run("decide", gate, "--option", "A", "--answer-file", str(ans))
        check("Q4-owner-signed-approval-accepted", dec_o.ok,
              f"the owner-signed answer verified against the provisioned `human-gate` delegation: "
              f"ok={dec_o.ok} code={dec_o.error_code} {str(dec_o.error.get('message'))[:170]}")
        sub = p.run("upstream", "submit", packet["packet_id"], "--destination", str(inbox))
        check("Q4-submit-after-approval", sub.ok,
              f"submission to a canonical lessons/inbox after the owner's answer: ok={sub.ok} "
              f"code={sub.error_code} {json.dumps(res(sub))[:200]}")
        if sub.ok:
            files = sorted(str(x.relative_to(inbox)) for x in inbox.rglob("*") if x.is_file())
            body = "\n".join((inbox / f).read_text(errors="replace") for f in files)
            leaks = [n for n in ("AKIA", "Contoso", str(p.root), p.root.name) if n in body]
            check("Q4-no-raw-project-or-secret-in-inbox", not leaks,
                  f"the inbox holds {files}; no secret, customer identifier or project path found "
                  f"(searched AKIA, Contoso, the project path and name); leaks={leaks}")
            check("Q4-synthetic-reproducer-preferred",
                  any("scenario" in f or "synthetic" in body for f in files) or "synthetic" in body,
                  f"the packet carries the declared synthetic reproducer rather than project material: {files}")


if __name__ == "__main__":
    main(run, "GATE-Q")
