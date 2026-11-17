---
name: memory-bar-is-end-to-end-judged
description: "the owner's 95 % memory bar is the end-to-end judged figure (DEC-1097/1098 config), never hit@5; every fresh 80 measured end to end with hit@5/10/20 and stacked share as diagnostics"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-16T17:04:52.832Z
---

The owner, 2026-11-16 ~17:1x: "My 95 % bar is the end-to-end judged figure, by the configuration DEC-1097 and DEC-1098 accepted: the reader reads the whole ranked bundle as a second reranker, may search once more in its own words, Opus grades and Sonnet checks agreement, and both the answer and its citation must be right. W2-15a's hit@5 is a component figure, not that bar." Every fresh 80 (the fresh-80 rule, DEC-1207) is measured end to end, and reports hit@5, hit@10, hit@20 and the stacked share per mode beside it as diagnostics.

**Why:** I reported W2-15a's hit@5 against the 95 % bar as if it were the bar.

**How to apply:** never compare a hit@k or stacked figure with 95 %. Call them diagnostics. The figure for the bar is the judged end-to-end one, answer and citation both right. Related: [[status-counts-fresh-every-report]].
