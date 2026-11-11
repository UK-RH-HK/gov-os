"""Reads a repository's accepted_reds ratchet with the pinned judge's own reader (gov.close.ratchet), as `gov close` does.
Run with the pin's interpreter:  <pin python> -I ratchet_probe.py <repo root> <mode>

modes (each prints what the reader says; exit 0 when the expectation of the mode holds, 1 otherwise):
  counted      expects both ACT-ACCEPTED-REDS-1 tests counted and no finding
  pending      expects no test counted and, for each, the one refusal "no commit of the history ... adds it"
  not-owner    expects no test counted and, for each, the refusal "added it without Role: owner"
  both-red     apply_accepted_reds with both tests failed: expects ok true, each reported "failed"
  one-passes   apply_accepted_reds with the first test passed: expects a finding ACCEPTED_RED_PASSES for it
  other-red    apply_accepted_reds with both failed and another test failed: expects a RED_NOT_ACCEPTED finding for the other
"""
import sys

from gov.close import ratchet

T1 = "tests/acceptance/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95"
T2 = "tests/acceptance/W2-13/test_w2_13_latency.py::test_a_warm_retrieval_with_the_real_models_answers_within_the_budget"
OTHER = "tests/acceptance/W9-99/test_other.py::test_some_other_red"

root, mode = sys.argv[1], sys.argv[2]
counted, findings = ratchet.counted_entries(root, "accepted_reds")
for e in counted:
    print("counted:", e["test"], "|", e["decision"], "|", e["fixed_by"])
for f in findings:
    print("finding:", f["code"], f["test"], "|", f["message"][:230])
ok = False
if mode == "counted":
    ok = [e["test"] for e in counted] == [T1, T2] and not findings
elif mode in ("pending", "not-owner"):
    why = "no commit of the history" if mode == "pending" else "without Role: owner"
    ok = not counted and sorted(f["test"] for f in findings) == sorted([T1, T2]) and all(why in f["message"] for f in findings)
else:
    results = {"both-red": {T1: "failed", T2: "failed"},
               "one-passes": {T1: "passed", T2: "failed"},
               "other-red": {T1: "failed", T2: "failed", OTHER: "failed"}}[mode]
    r = ratchet.apply_accepted_reds(root, results)
    print("apply_accepted_reds:", {"ok": r["ok"], "reports": [(x["test"].split("::")[1][:40], x["result"]) for x in r["accepted_reds"]],
                                   "findings": [(x["code"], x["test"].split("::")[-1][:40]) for x in r["findings"]]})
    if mode == "both-red":
        ok = r["ok"] and [x["result"] for x in r["accepted_reds"]] == ["failed", "failed"]
    elif mode == "one-passes":
        ok = (not r["ok"]) and [(x["code"], x["test"]) for x in r["findings"]] == [("ACCEPTED_RED_PASSES", T1)]
    else:
        ok = (not r["ok"]) and [(x["code"], x["test"]) for x in r["findings"]] == [("RED_NOT_ACCEPTED", OTHER)]
print("expectation", mode, "holds" if ok else "FAILS")
sys.exit(0 if ok else 1)
