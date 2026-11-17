---
name: research-launch-needs-experiments-folder
description: "gov launch refuses a research worker unless the ticket's allowed_paths is exactly one existing experiments/<x>/** folder (DEC-242, DEC-273); --plan does not check it"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 119a88fb-44c7-4891-86b6-50254f9e1836
  modified: 2026-11-15T16:10:30.736Z
---

A launched `research` worker is refused by launch_worker.sh's dry run ("allowed_paths is not exactly one experiment
folder (DEC-242)") unless the ticket's `allowed_paths` is exactly ONE entry `<folder>/**`, the folder existing and
under `experiments/` (DEC-273). Its writes are then fenced into that folder, so a research worker can never write
`docs/research/...`. `gov launch --plan research <ticket>` prints the model and passes; only the dry run refuses.
Seen 2026-11-15 on W2-15a (DAEO-rd0g: `docs/research/EXP-003/**` + `experiments/EXP-003/**`, the latter missing);
pass 1 of W2-15a ran "research, in the CTO's session", not launched.

**Why:** the W2-15a close brief named "a research worker" for a docs/research edit; the lead's launch was refused and
the run returned LAUNCH_BLOCKED.

**How to apply:** before briefing a launched research worker, check the ticket's allowed_paths against
`experiment_folder()` (src/gov/guard/install.py:194); a docs/research record needs another route (the CTO's own
session in the research role, or the lead, by the CTO's word). See [[brief-worker-model-launcher-picks]].
