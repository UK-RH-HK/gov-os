# DERIVED COPY (P2-AR-0037, WS-6 repair round 3) of release/capability-baseline/audit-0/synthesis/evidence/AC16-X2-authority-gate-chain.py
# ORIGINAL-PROBE-ID: synthesis/AC16-X2-authority-gate-chain
# Changes, and nothing else:
#  1. the sections between the project set-up and the B1/B3 block (L3<->E1, fabrication, E1-01, E3, N4/W5, I4) are
#     removed: on the integrated round-2 tree the unedited probe stops before B1/B3 at `task claim TASK-W`
#     (TASK_NOT_RUNNABLE: WS-5 BC-P2-16, an implementation task needs declared scenarios and acceptance tests), a
#     refusal by design that is not this workstream's. The set-up lines and the B1/B3 block are byte-for-byte the
#     original's, so X2-B1B3-nonrebuildable-state-not-classified-derived is evaluated exactly as the probe states it
#     (the probe's own reading: every overlay rule that matches a store path, fnmatch or prefix).
#!/usr/bin/env python3
"""P2-AR-0007 AC-16, cross-family chain X2: gate presentation <-> authority (L3 <-> E1), followed across E4 (claims),
G2/W5 (task close), K2 (CIT-E) and U/O5 (health), plus cross-family leads the families passed on:

  L3<->E1   an L1 worker, inside its own claimed task, writes an ANSWERED/presented 'human' gate record and a
            human_approved decision; task close accepts; a change-controller's `cit approve --method human` derives
            human approval from the forgery; `cit execute` commits; the suite reports on it or not.
  L3 fabrication by CLI metadata/defaults: no --role/--by; --role human; GOV_ROLE=human.
  Framework s23 'No spawned worker behaves as an orchestrator unless explicitly assigned that role': an invocation
            that declares no role at all acts at L4.
  E1-01     --role on init is ignored (vs GOV_ROLE).
  E3 lead   (delta-r N4.b1.9) a handoff return from a role other than to_role.
  N4/W5 lead (beta-r OBS-3) a worker return that satisfies the worker-return schema, used as the task-close report.
  I4 lead   (delta-r L4.b2.3a) a task set BLOCKED is still offered as runnable.
  B1/B3     where claims, emergency-control state and the plugin registry live, and how the product classifies those paths.

Run from the worktree root after `~/.cargo/bin/cargo build --release`:
  SYNTH_SCRATCH=<scratch> python3 release/capability-baseline/audit-0/synthesis/evidence/AC16-X2-authority-gate-chain.py
"""
import json
import os
import sys

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from synth import *  # noqa

root, g = new_project("x2")
spec_base(root)
commit(root, "spec")
g.ok("rebuild-memory", quiet=True)

# ======================================================================= B1/B3: classification of stores holding non-rebuildable state
rc = yaml.safe_load(read(root, "governance/project/REPOSITORY_CONTRACT.yaml"))
def cls_of(path):
    import fnmatch
    hits = []
    for rule in rc.get("rules", rc.get("paths", [])) if isinstance(rc, dict) else []:
        pat = rule.get("pattern") or rule.get("path") or rule.get("glob")
        if pat and (fnmatch.fnmatch(path, pat) or path.startswith(pat.rstrip("*").rstrip("/") + "/")):
            hits.append((pat, rule.get("class"), rule.get("authority")))
    return hits
stores = {p: os.path.exists(os.path.join(root, p)) for p in (".governance-runtime/claims.db", ".governance-runtime/control.json", "governance/generated/plugin-registry.json")}
note("store locations present: " + json.dumps(stores))
classes = {p: cls_of(p) for p in (".governance-runtime/claims.db", ".governance-runtime/control.json", "governance/generated/plugin-registry.json")}
note("REPOSITORY_CONTRACT rules matching those paths: " + json.dumps(classes))
arch = read(os.path.join(WT, "docs"), "ARCHITECTURE.md") if False else open(os.path.join(WT, "docs/ARCHITECTURE.md")).read()
note("docs/ARCHITECTURE.md says: " + [l for l in arch.splitlines() if ".governance-runtime" in l and "derived" in l][0].strip()[:200])
derivedish = any(c[1] in ("derived", "generated", "runtime") for v in classes.values() for c in v)
x("X2-B1B3-nonrebuildable-state-not-classified-derived", not derivedish,
  "B1:188 / B3:202: claims (C1 current truth), emergency-control state and the OS plugin registry (D-0007 T2) are not stored under paths the product classifies derived/generated",
  classes)
summary()
