---
name: never-edit-running-bash-script
description: bash reads a script as it runs; editing it under a running instance breaks that instance (syntax errors, skipped records); finish or stop the batch first (11-16)
metadata:
  type: feedback
---

On 2026-11-16 I edited drafts/repin-rel-0.1.1/rehearse_rel.sh twice while a batch was running it (07:50 and 08:07). Both running instances later died with syntax errors (`line 295: elif`, `line 307`) in their outcome blocks, after the operator's script had run, so neither wrote its live after-record. I covered the gap from the next mode's before/after records (the fixed live paths were equal across it).

**Why:** bash reads a script file incrementally by offset, so new bytes shift what the running instance reads next. The same holds for any bundle file a running batch checks by hash (fill_release.sh's BUNDLE.sha256 check refuses after an edit).

**How to apply:** stop the batch (by pid or pgid) before editing any script it runs, or edit a copy and swap it in between runs. Never edit in place under a running loop. Related: [[test-refusal-paths-resolve-first]], [[no-rehearsal-against-live]].
