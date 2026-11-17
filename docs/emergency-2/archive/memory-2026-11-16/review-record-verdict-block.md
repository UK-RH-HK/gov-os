---
name: review-record-verdict-block
description: "an ACT bundle's review.md must carry the reviewer's fenced verdict block, or the operator agent's G4 refuses"
metadata:
  node_type: memory
  type: feedback
  originSessionId: b2f0511f-891b-4874-8930-6d34ca5972ea
  modified: 2026-11-12T00:40:11.631Z
---

When filing an ACT review into its bundle (`review.md`) and `reviews/`, copy the REVIEW_MD section **and** append the
reviewer's fenced ```verdict block verbatim (it sits after REVIEW_MD_END in the return). Check with the operator's own
reader before queueing: `~/gov-os-operator/install/verdict.py`'s `BLOCK.findall` must find at least one block.

**Why:** on 2026-11-11 23:40 the operator agent refused ACT-LOAD-BALANCER-A at G4 ("the review record holds no verdict
block") after the owner's yes; G1 then reuses the frozen copy (`~/gov-os-operator/acts/<ACT>-<sha12>/`) and never
replaces it, so a corrected bundle alone cannot pass: the owner's operator has to remove or fix the frozen copy.

**How to apply:** extract both blocks in one step; never queue a `.req` before the reader check passes. Related:
[[act-in-progress-holds-operator]], [[check-before-ready-line]].

**Probe record form (11-15 15:55, W2-60a ejected):** every narrow-check or review brief names the record's front-matter fields (type: probe, task, reviewer_session, implementer_session, reviewer_wrote_nothing, commissioned_by, judged_by, judgement, probed_commit, decisions_applied), or the land queue ejects the ticket on the W1-26/W1-08/W2-02 schema cases.

**The owner's yes must be its own line (11-15 17:10):** the operator's G6 (`opcommon.find_owner_line`) counts only a transcript line that equals `yes ACT-<id> <sha8>` exactly once stripped. "B: yes ACT-GUARD-FIX-6 6e6c3927. Right after…" was refused. When giving an owner a yes line, say "send it alone, on its own line"; check the transcript before queueing the .req.

**Replies-file text (11-15 17:31):** a Bash heredoc that quotes the harness deny rule with a sets-root placeholder is refused as a hidden-half read. Write REPLIES.md with the Edit tool, and never quote that rule's text.
