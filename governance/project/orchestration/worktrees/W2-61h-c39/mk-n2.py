from pathlib import Path
base = Path("/home/usain/gov-os-worktrees/W2-61h-c39")
body = (base / ".gov-runtime/scratch/log/nc-3.result.md").read_text(encoding="utf-8")
front = '''---
type: probe
task: DAEO-h2k3
kind: "narrow independent check (DEC-1154) of the N2 (b) and N1 test revision under DEC-1180 (1), (4): a heading-cited section rewritten under a heading still found is listed; a section moved unchanged is not; an entry is listed once; not a round, DEC-1010"
reviewer_session: "0791247d-c8a3-4af8-b9cc-c2befd0648a1 (nc-3, independent-auditor, claude-opus-5-5, high, C2; read from the launch log)"
implementer_session: "e4e7eb41-d905-414a-9b4d-90e1b1fdc91d (td-5, independent-test-designer, claude-sonnet-5-5, high, C2; commit 70aa3a6b7ba3e8c348e2b6a8f502873013f84ab8)"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: dbe1236733f9d63ccccf8fc5435fbdba41617603
date: 2026-11-14
decisions_applied: [DEC-1180, DEC-1178, DEC-1154, DEC-1084, DEC-828]
---

# Narrow check of W2-61h's N2 (b) and N1 revision (DEC-1180 (1), (4))

The lead's triage: R1 is a row (out of scope, ordinary work no, consequence other): the hidden-form (g) plant alone
does not separate N1 from the old rule, but the visible planted p10 does, and both modules call the same
`judge_sources`. No round.

The reviewer's return, word for word:

'''
(base / "docs/probes/DAEO-h2k3/PR-DAEO-h2k3-n2.md").write_text(front + body.rstrip() + "\n", encoding="utf-8")
