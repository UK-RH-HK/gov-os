#!/usr/bin/env python3
"""BA12r7 — brute-force search over key subsets below the CP-1 thresholds (reviewer B's RV6-B-A12, AR-0016, re-expressed on CS7) (AR-0019).
Computed; scratch-free.

Instrument: `CS7-derivation-calculator.py`, loaded by path; only its acceptance function `accepted` is called, so the search is independent
of CS7's minimal-set enumeration and invariant code. For every CS7 configuration, every subset of at most 3 key atoms is tried with every
subset of the infrastructure atoms present (pipeline, transport, repo, fcpub, carrier, mirror). Reported: accepted subsets holding at most one
key; accepted subsets whose keys are only release-candidate, release-final and trust-state keys; accepted subsets holding one key of a 2-of-N
purpose and no other key of that purpose together with infrastructure only.
Output: JSON on stdout.
"""
import importlib.util, itertools, json, os, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("cs7", os.path.join(HERE, "CS7-derivation-calculator.py"))
CS7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS7)
INFRA = ["pipeline", "transport", "repo", "fcpub", "carrier", "mirror"]
out = {"probe": "BA12r7 key subsets below the CP-1 thresholds (AR-0019; after RV6-B-A12)", "configurations": 0, "subsets_tried": 0, "one_key_accepts": [], "release_and_trust_state_keys_only_accepts": []}
for goal, cfg in CS7.configs():
    atoms = CS7.atoms_for(goal, cfg)
    keys = [a for a in atoms if a in CS7.KEYS]
    infra = [a for a in atoms if a in INFRA]
    out["configurations"] += 1
    for r in range(0, 4):
        for ks in itertools.combinations(keys, r):
            for ir in range(0, len(infra) + 1):
                for inf in itertools.combinations(infra, ir):
                    caps = frozenset(ks + inf)
                    out["subsets_tried"] += 1
                    if not CS7.accepted(goal, caps, cfg, CS7.R7):
                        continue
                    rec = {"goal": goal, "config": CS7.cfg_key(goal, cfg), "caps": sorted(caps)}
                    if len(ks) <= 1 and len(out["one_key_accepts"]) < 50:
                        out["one_key_accepts"].append(rec)
                    if set(ks) <= {"rck", "rfk1", "rfk2", "tsk1", "tsk2"} and len(out["release_and_trust_state_keys_only_accepts"]) < 50:
                        out["release_and_trust_state_keys_only_accepts"].append(rec)
out["verdicts"] = {"no_accept_with_at_most_one_key": not out["one_key_accepts"], "no_accept_with_release_and_trust_state_keys_and_infrastructure_only": not out["release_and_trust_state_keys_only_accepts"]}
print(json.dumps(out, indent=1, sort_keys=True))
