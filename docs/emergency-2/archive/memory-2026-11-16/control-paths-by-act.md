---
name: control-paths-by-act
description: "before briefing a helper to edit a committed tool, check class-rules.yaml; watchers, guard, settings, hooks change only by an ACT"
metadata:
  node_type: memory
  type: feedback
  originSessionId: ad44f5fe-276d-46b7-85cd-df9f8d97a3ec
  modified: 2026-11-10T11:41:28.956Z
---

Before a brief tells a helper to edit any committed file under governance/project/orchestration/tools/, .claude/,
the path map, settings, hooks or the operator's install, check ~/gov-os-operator/install/class-rules.yaml for its
class. A (b) or (O) path (e.g. deadman.py, a watcher) changes only by an ACT with the owner's yes; the CTO's own
scratch tools (.gov-runtime/scratch/orchestrator/tools/) are free.

**Why:** 2026-11-10 the CTO briefed a helper to edit deadman.py directly; the landing check raised a P1 (b0eb21f1a),
reverted in 09e1ff6e1 and rebuilt as ACT-DEADMAN-WAKE-1.

**How to apply:** in every brief that touches a committed tool, name its class and, for (b)/(O), ask for an ACT
package (drafts, apply.sh, rehearsal, review, exact yes line). Related: [[merge-never-staged]].
