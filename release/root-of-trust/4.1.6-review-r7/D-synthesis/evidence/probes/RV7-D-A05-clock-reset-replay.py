#!/usr/bin/env python3
"""RV7-D-A05 (AR-0022, synthesis reviewer D, held-out) — `bootstrap.clock_reset` replay and persistence.

CP-1 text (`24` §4.5, §8; `17` §13; schema): "A root-signed Trust Policy bootstrap.clock_reset {reset_to, reason} lowers the
high-water after a wrong future clock raised it"; every Trust Policy carries the field (required: null or object). No text binds a
reset to the effective Trust Policy, to one application, or to high-water values recorded before the policy's issuance. The
revision-7 reference executor does not implement clock_reset; the only executable model of it the pack retains is P4r4
(`evidence/P4r4-trust-state-model.py`, cited by `17`). This probe loads that model UNMODIFIED and asks:
  (1) a machine holds TPS v2 (effective, no reset) and a clock high-water of t=1000; the transport replays genuine TPS v1 carrying an
      old clock_reset {reset_to: 100}; what high-water does ingest produce?
  (2) with TPS v1 effective and later statements issued at 1000 and 2000 ingested, does the reset keep lowering the high-water?
Environment: PACK. Output: JSON on stdout.
"""
import importlib.util, json, os, sys
sys.dont_write_bytecode = True
PACK = os.environ["PACK"]
spec = importlib.util.spec_from_file_location("p4r4", os.path.join(PACK, "evidence", "P4r4-trust-state-model.py"))
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
flag = M.R.get("clock_high_water_witness_only")
root1 = M.root(1)
tps1 = M.tps(1, clock_reset=100)
tps2 = M.tps(2, prior={"TPS1"})
tss5 = M.tss(5, "TSS5", issued_at=900)
w = M.witness("W1", 5, "TSS5", issued_at=1000, expires_at=5000)
w2 = M.witness("W2", 5, "TSS5", issued_at=2000, expires_at=5000)
machine = {"vts": {"clock_high_water": 1000}}
res = {}
K, refused, hw = M.ingest([root1, tps2, tss5, w], machine, 1000)
res["control_tps2_only_high_water"] = hw
K, refused, hw = M.ingest([root1, tps2, tss5, w, tps1], machine, 1000)
res["replayed_tps1_with_reset_held_alongside_effective_tps2_high_water"] = hw
res["effective_tps_version_after_replay"] = (M.tps_state(K).get("eff") or {}).get("v")
K, refused, hw = M.ingest([root1, tps1, tss5, w, w2], {"vts": {"clock_high_water": 2000}}, 2000)
res["tps1_effective_later_witness_at_2000_high_water"] = hw
out = {"probe": "RV7-D-A05 clock_reset replay and persistence on the retained P4r4 model (AR-0022)", "model_flag_clock_high_water_witness_only": flag, "results": res,
       "verdicts": {"replayed_non_effective_policy_lowers_the_high_water": res["replayed_tps1_with_reset_held_alongside_effective_tps2_high_water"] == 100 and res["control_tps2_only_high_water"] == 1000,
                    "reset_is_applied_continuously_not_once": res["tps1_effective_later_witness_at_2000_high_water"] == 100}}
print(json.dumps(out, indent=1, sort_keys=True, default=str))
