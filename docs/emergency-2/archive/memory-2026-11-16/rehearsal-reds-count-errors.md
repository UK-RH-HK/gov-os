---
name: rehearsal-reds-count-errors
description: "ACT rehearsal \"no new red\" cases must compare FAILED and ERROR ids; G3 needs the log's last line \"failures: 0\""
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-16T16:40:20.073Z
---

An ACT rehearsal's suite case compares the reds as FAILED **and** ERROR ids, before against after. On 11-16 my ACT-GOLDEN-RULE-1 builder counted only FAILED lines. W2-106 had the same 14 ERROR lines before and after the apply (an environment red), and the case went FAIL. The operator's G3 refuses any rehearsal log whose last line is not `failures: 0`, so an addendum cannot fix it; the whole rehearsal had to run again (about 30 min of slot waits).

**Why:** pytest reports a fixture error as ERROR, not FAILED, and G3 reads only the log's last line.

**How to apply:** in every builder, write `re.findall(r"^(?:FAILED|ERROR) (\S+)", ...)`. Never append lines after `failures: <n>`. See also [[rehearse-every-handed-command]] and [[pytest-through-heavy-slot]].
