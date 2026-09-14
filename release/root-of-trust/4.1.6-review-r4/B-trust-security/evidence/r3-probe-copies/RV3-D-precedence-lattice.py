#!/usr/bin/env python3
"""AR-0004 (review r3 synthesis D) held-out probe on the pack's OWN precedence lattice (constitutional-surface/csi_lib.py).

RV3-D-A01  Class soundness of the `23` §4 order. For every pair of precedence modes, compare the lattice relation
           rule_ge(a, b) ("a at least as strong as b for the project layer") with what the 4.1.5 runtime
           (runtime/src/policy_precedence.rs evaluate) actually admits as project STRENGTHENING under each mode.
           A pair is unsound when rule_ge(a, b) holds but a admits strictly less project strengthening than b.
RV3-D-A02  Root-signed TPS tightening. TPS v2 registers `immutable` where TPS v1 registered `floor`/`additive`/`ceiling`.
           Is that a computed reduction (19 §10.6, lowering_history + per-project `policy_lowering` gate)? What happens to an
           older kernel registered under v1, and what is the effective project-layer rule?
No subprocesses, no writes. Output: JSON on stdout.
"""
import json, os, sys

W = os.environ.get("REVIEW_REPO") or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", ".."))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(W, "release/root-of-trust/4.1.6/constitutional-surface"))
import csi_lib as L  # noqa: E402

# What a project layer may do under each mode, per runtime/src/policy_precedence.rs evaluate (4.1.5):
#   overridable: anything; immutable: nothing; floor: raise (nr >= kr); ceiling: lower (nr <= kr);
#   additive: add entries (no removal); shrink_only: remove entries (no additions); strengthen_only_bool: set strict value.
# Each mode's registered classification (23 §5.1) fixes which direction is "stronger"; the project strengthening a mode
# admits is exactly the set below. `overridable` also admits weakening, which the order already accounts for.
STRENGTHENING_ADMITTED = {
    "overridable": {"raise_level", "lower_ceiling", "add_entry", "remove_entry", "set_strict_bool"},
    "immutable": set(),
    "floor": {"raise_level"},
    "ceiling": {"lower_ceiling"},
    "additive": {"add_entry"},
    "shrink_only": {"remove_entry"},
    "strengthen_only_bool": {"set_strict_bool"},
}


def rule(mode, kind=None):
    return {"key": "K", "mode": mode, "kind": kind, "order": None, "strict_value": True if mode == "strengthen_only_bool" else None, "exception_relaxable": False}


modes = ["immutable", "floor", "ceiling", "additive", "shrink_only", "strengthen_only_bool", "overridable"]
pairs, unsound = [], []
for a in modes:
    for b in modes:
        if a == b:
            continue
        ra, rb = rule(a, "level" if a in ("floor", "ceiling") else None), rule(b, "level" if b in ("floor", "ceiling") else None)
        ge = L.rule_ge(L.rule_tuple(ra), L.rule_tuple(rb))
        if b == "overridable":
            continue  # overridable also admits weakening; not a strengthening comparison
        lost = sorted(STRENGTHENING_ADMITTED[b] - STRENGTHENING_ADMITTED[a])
        row = {"installed": a, "registered": b, "lattice_installed_ge_registered": ge, "project_strengthening_lost_if_installed": lost}
        pairs.append(row)
        if ge and lost:
            unsound.append(row)

A01 = {"pairs_evaluated": len(pairs), "unsound_pairs": unsound,
       "verdict": "order is refusal-only: every move to `immutable` is ranked as at-least-as-strong although it removes all admitted project strengthening"
       if unsound else "no unsound pair"}

A02 = {}
for reg_mode, strengthening in (("floor", "raise_level"), ("additive", "add_entry"), ("ceiling", "lower_ceiling"), ("shrink_only", "remove_entry"), ("strengthen_only_bool", "set_strict_bool")):
    v1 = L.rule_tuple(rule(reg_mode, "level" if reg_mode in ("floor", "ceiling") else None))
    v2 = L.rule_tuple(rule("immutable"))
    computed_reduction_v1_to_v2 = not L.rule_ge(v2, v1)
    older_kernel_rule = v1  # a kernel registered under v1 still carries the v1 rule
    older_kernel_precedence_weakened_under_v2 = not L.rule_ge(older_kernel_rule, v2)
    effective = L.rule_join(older_kernel_rule, v2)
    A02[reg_mode] = {"TPS_v2_registers_immutable_is_computed_reduction": computed_reduction_v1_to_v2,
                     "needs_lowering_history_and_policy_lowering_gate": computed_reduction_v1_to_v2,
                     "older_v1_kernel_E7_precedence_weakened_under_v2": older_kernel_precedence_weakened_under_v2,
                     "effective_project_layer_mode": effective["mode"],
                     "project_strengthening_removed": sorted(STRENGTHENING_ADMITTED[reg_mode] - STRENGTHENING_ADMITTED[effective["mode"]])}

print(json.dumps({"probe": "RV3-D precedence lattice", "lattice": "release/root-of-trust/4.1.6/constitutional-surface/csi_lib.py rule_ge/rule_join (unmodified)",
                  "runtime_reference": "runtime/src/policy_precedence.rs evaluate (4.1.5)",
                  "RV3-D-A01_lattice_soundness": A01, "RV3-D-A02_root_signed_tps_tightening": A02}, indent=1, sort_keys=True))
