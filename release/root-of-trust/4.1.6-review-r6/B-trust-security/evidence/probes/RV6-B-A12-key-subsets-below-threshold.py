#!/usr/bin/env python3
"""RV6-B-A12 — brute-force search for accepted binaries or effective content from key subsets below the declared thresholds,
including OP-4 "no" (review r6 reviewer B, AR-0016). Computed; scratch-free.

Instrument: `evidence/r6/CS6-derivation-calculator.py`, loaded unmodified; only its acceptance function `accepted` is called.
The search is independent of CS6's minimal-set enumeration and of its invariant code: every subset of size ≤ 3 of the key
atoms, optionally with pipeline, transport and repository input, is tried directly.

Configurations: OP-2 root/delegated × OP-4 sep/shared × OP-8 1/2 × OP-9 n2q2/n3q2/d_n2q2 × victims P1, P2k1, WR, CIR,
FA (a, b, c_either_1) for G_BYTES, G_SRC, G_INPUTS; USE, ING_P1, ING_P2k1, FA (a, b) for G_CONTENT; P1, P2k1 for G_ENV
under OP-16 a/b. Reported: accepted subsets holding at most one key (with or without infrastructure) outside the stated
first-contact root; accepted subsets holding only release-candidate/release-final/shared everyday key, trust-state key and
infrastructure.
Output: JSON on stdout.
"""
import importlib.util, itertools, json, os, sys

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
spec = importlib.util.spec_from_file_location("cs6", os.path.join(REPO, "release", "root-of-trust", "4.1.6", "evidence", "r6", "CS6-derivation-calculator.py"))
CS6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS6)
INFRA = ["pipeline", "transport", "repo"]
out = {"probe": "RV6-B-A12 key subsets below threshold (AR-0016)", "configurations": 0, "subsets_tried": 0, "one_key_accepts": [], "release_keys_only_accepts": []}
cfgs = []
for reg in ("root", "delegated"):
    for op4 in ("sep", "shared"):
        for V in (1, 2):
            for repro in ("n2q2", "n3q2", "d_n2q2"):
                base = {"reg": reg, "V": V, "repro": repro, "op4": op4, "tc": "accept", "env": "a", "fc": "-"}
                for victim, fc in (("P1", "-"), ("P2k1", "-"), ("WR", "-"), ("CIR", "-"), ("FA", "a"), ("FA", "b"), ("FA", "c_either_1")):
                    for goal in ("G_BYTES", "G_SRC", "G_INPUTS"):
                        cfgs.append((goal, dict(base, victim=victim, fc=fc)))
                    if victim in ("P1", "P2k1"):
                        for env in ("a", "b"):
                            cfgs.append(("G_ENV", dict(base, victim=victim, env=env)))
                if repro == "n2q2":
                    for victim, fc in (("USE", "-"), ("ING_P1", "-"), ("ING_P2k1", "-"), ("FA", "a"), ("FA", "b")):
                        cfgs.append(("G_CONTENT", dict(base, victim=victim, fc=fc)))
for goal, cfg in cfgs:
    atoms = CS6.atoms_for(goal, cfg)
    keys = [a for a in atoms if a in CS6.KEYS]
    infra = [a for a in atoms if a in INFRA]
    out["configurations"] += 1
    for r in range(0, 4):
        for ks in itertools.combinations(keys, r):
            for ir in range(0, len(infra) + 1):
                for inf in itertools.combinations(infra, ir):
                    caps = frozenset(ks + inf)
                    out["subsets_tried"] += 1
                    if not CS6.accepted(goal, caps, cfg, CS6.R6):
                        continue
                    rec = {"goal": goal, "config": CS6.cfg_key(goal, cfg), "caps": sorted(caps)}
                    if len(ks) <= 1 and len(out["one_key_accepts"]) < 50:
                        out["one_key_accepts"].append(rec)
                    if set(ks) <= {"rc", "rf", "kc", "ts"} and len(out["release_keys_only_accepts"]) < 50:
                        out["release_keys_only_accepts"].append(rec)
out["verdicts"] = {"no_accept_with_at_most_one_key": not out["one_key_accepts"], "no_accept_with_release_keys_trust_state_and_infrastructure_only": not out["release_keys_only_accepts"]}
print(json.dumps(out, indent=1, sort_keys=True))
