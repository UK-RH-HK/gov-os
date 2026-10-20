
## W1-23 residuals (hierarchical synthesis notes, 2026-10-06)

- **A note is deterministic and written by no model:** grouped citations with source ids, the hash of each cited
  span and of its file, the path and the lines, and the list of unresolved evidence. A model-written summary is
  not built and no source asked for one.
- **Notes are stored in one file,** `.gov-runtime/synthesis/notes.json`, per project; a second synthesis replaces
  the first.
- **Invalidation is found when `validate_notes(root)` is called,** by hashing the cited files and spans again;
  nothing calls it yet. `gov context` (W1-24) does not import this module; the wave's exit run (W1-42) is the
  first place where notes are derived for evidence above the packet budget.
- **No review round** (STANDARD); the lead read the diff against the two failure lines.
- **Learning metrics:** 0 KPI disputes; 0 acceptance tests rewritten after implementation began; source 114
  lines against an estimate of 100.
- **Interface:** `gov.retrieval.synthesis.synthesize(root, evidence, budget, *, gaps=None)` returns `notes`
  (each with `group` and `citations`) and `unresolved`; `gov.retrieval.synthesis.validate_notes(root)` returns
  `valid` and `errors`.
- **Regression at `c8080e16`:** every suite green, no latency occurrence.
