# W2-32 test designer, round 3 (the CTO)

Same rules as before (stand-ins only; no `gov retrieve`; the `ps` check in your return; do not merge: the CTO merges
outside the sandbox). The CTO decided your two proposals:
- **P-W2-32-5, strict:** a hidden-half miss is recorded by its **id only**: no root cause, no repair, no free text either
  (free text about a hidden miss could carry its gold path or wording). Revise
  `test_w2_32_s3_memory_quality.py::test_a_hidden_miss_with_its_id_only_is_recorded_without_its_text` (`[id]`, `[part]`):
  today it passes `root_cause` and `repair`, and the engineer's strict rule rightly refuses that (2 red at `2bc918f1`).
  The case should record a hidden miss with the id (or `part: hidden`) only and see the event hold no text; and a hidden
  miss carrying a root cause or repair is refused (if you have no such case, add one).
- **P-W2-32-4, yes:** once the engineer's S10 lands (the CTO tells you), revise the other tickets' stand-ins that report
  the CPU (`size_vram: 0`), as you did for the digests; not in this round.
Commit with `Task: DAEO-0pyc`, `Implements: DEC-1064, DEC-1065`, `Role: independent-test-designer`, `Rewrite-Reason:
P-W2-32-5 (a hidden miss by its id only)`, Co-Authored-By. Return the twelve fields, brief.
