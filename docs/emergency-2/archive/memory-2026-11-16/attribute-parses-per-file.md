---
name: attribute-parses-per-file
description: "when counting YAML parses per hook call, attribute each parse to its file before claiming \"parsed twice\"; a parse of a section's lines or a ticket's front matter looks like a repeat"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 6542ebab-e51e-4053-b0fc-fc69c444d361
  modified: 2026-11-15T19:05:52.489Z
---

W2-111 r5 (2026-11-15): I told the CTO and the TD that a role-set Read made "3 yaml loads for 2 files" (so "parsed once" would be red before). Wrong: the third parse was the session ticket's front matter (`.tickets/<id>.md`), and path-map's was only its `evaluation_sets:` section. The TD found it; behaviour 3 was green before the change (P-W2-111-S9-COUNT).

**Why:** a wrong expected-red sent to the CTO and into a brief costs a package round and the CTO's trust in lead measures.
**How to apply:** in an audit-hook count, record the source of each yaml.load (file path, or caller frame for string loads) before stating a count to anyone. Related: [[kpi-baseline-exists-before-brief]].
