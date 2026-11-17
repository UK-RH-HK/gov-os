---
name: dec866-marks-with-every-changes
description: "every register entry whose Changes: names an earlier decision gets a \"· **Changed by DEC-n (x):** …\" mark on that earlier entry's status line in the SAME commit; W2-130's marks test reddens the nightly otherwise"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-15T05:25:21.927Z
---

The 2026-11-15 nightly was red on W2-130's two marks cases. DEC-1182 (Changes: DEC-1180 (2)), DEC-1184 (Changes: DEC-1182 (3), (4)) and DEC-1185 (Changes: DEC-1183 (1)) were recorded without the DEC-866 mark on the earlier entries' status lines. The last two were mine, written tonight. Fixed by 1adde4b8f.

**Why:** DEC-866 (supersession propagates) requires the old entry to name the new one at once, so agents are no longer served it as in force. `gov links` and `tests/acceptance/W2-130/test_w2_130_marks.py` check every pair.

**How to apply:** each DEC apply script, for every decision in **Changes:**, appends ` · **Changed by DEC-<new> (<item>):** <one line>` to the old entry's `- **Status:**` line, in the same commit. Then run `gov links` (no new UNMARKED_CHANGE) before committing. Related: [[narrow-check-after-review]].
