---
name: probe-record-one-verdict-block
description: "a probe record with a quoted \"> ```verdict\" copy fails land.py's verdict.ready (fail closed); one unquoted block; run ready() before committing"
metadata:
  node_type: memory
  type: feedback
  originSessionId: ecf5d5f4-9e16-4a15-92ce-9a7b9f8a718c
  modified: 2026-11-16T10:11:42.611Z
---

A probe record must hold exactly one fenced `verdict` block, unquoted. W2-111's PR-DAEO-qvff-r4.md held a `> ```verdict` copy above the real one; `verdict.ready()` returned "the verdict block is not the structured form (fail closed)", so land.py refused the FULL ticket (11-15 17:07). The refusal named the head, and it was read as "the head moved since the review"; the real cause was the record's format.

**Why:** land.py precheck parses each docs/probes/<id>/*.md with verdict.ready from the CTO's tools; a quoted block breaks the parse, and the refusal text doesn't say so.
**How to apply:** before committing any probe record, run `python3 -I -c "import sys; sys.path.insert(0,'<orch tools>'); from verdict import ready; print(ready(open('<record>').read()))"` and expect `(True, [])`. Related: [[review-record-verdict-block]].

**Also the frontmatter (11-16, W2-189):** a record that opens with `# PR-…` and has no `---` probe frontmatter passes ready() but reddens W1-08 `test_the_probe_schema_accepts_this_repository_s_probe_records` and W1-26 `test_this_repository_s_probe_records_are_well_formed` in the next scoped run. Open every record with the probe schema's keys (type: probe, task, reviewer_session, implementer_session, reviewer_wrote_nothing, commissioned_by, judged_by, judgement, probed_commit as a full 40-hex id; copy the form of docs/probes/DAEO-l78m/PR-DAEO-l78m-narrow-s-stages.md), then run those two cases by node id before committing.
