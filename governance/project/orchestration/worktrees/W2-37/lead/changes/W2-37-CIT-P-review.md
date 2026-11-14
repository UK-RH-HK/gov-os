---
type: review
record: W2-37-CIT-P
task: DAEO-6n5k
reviewer_session: 64d3d4eb-f24c-4f3a-9c76-4f942d1c0066 (independent-auditor, claude-opus-5-5, high, C2; fresh, read-only, not the author)
reviewed_commit: 68d9a917b8db1e4b29980bc313edff36cf67e752 (the skill bytes), at branch head 31bf5ea0747e
reviewer_wrote_nothing: true (tripwire: no change in W2-37's tree)
commissioned_by: orchestrator (W2-37 ticket lead)
judgement: pass
date: 2026-11-13
---

# Independent review of W2-37-CIT-P (the change skill's impact section)

The auditor's review, as returned (its last message, `log/rev-4-2.result.txt`). The lead corrected the CIT-P's text
for rows C1 to C3 after it; the bytes are unchanged (the hashes the reviewer checked hold).

## Checks
- Verbatim lines: sound (the record's fenced diff equals `git show 68d9a917b -- template/governance/kernel/skills/change/SKILL.md` from the `@@` line on; the `.rulesync` template's diff differs only in its path lines).
- sha256 before and after, both files: sound (before `2af36b72…dc982`, after `a25b02a7…932536`; `cmp` byte-equal; root `.rulesync` and `.claude` copies unchanged).
- Expected copies' hashes: sound (recomputed `.claude` expected `017328ec…6658d`).
- Cited ids exist and are ACCEPTED: sound (DEC-167, DEC-816, DEC-1163 (7), DEC-105; CAP-33.a, .d, .f, .g in the Contract; no Supersedes/Changes line names DEC-167 or DEC-816).
- The section matches `gov impact`: sound (`--help`; `gov impact "What is the impact of DEC-510?"` prints change with deletable, radius, depth, affected by the five kinds, graphs, complete, gaps, proposal; the question forms resolve).
- DEC-105 options: sound in form; option 1's cost incomplete (C3, corrected).
- W1-35 lines `:991` and `:845`: sound.
- Nit: the validator reads `GOV_COMMANDS`, built from `RECORDED_GOV_COMMANDS` (corrected).

## Rows (DEC-809: none in scope, ordinary, and failing open or losing work; none blocks)
- **C1** (in, ordinary yes, other): one sentence outside the impact section (`## Tools`, `gov closure` → `gov impact`) changed, disclosed in the record and the diff; DEC-1163 (7) puts both whole files in the paths. Reversed by an owner reading that DEC-816 limits the bytes to the section's own lines.
- **C2** (in, ordinary yes, other): the record's version reasoning misread the skill's step 5 (the version increments on approval; the number is not fixed), and a bump is two lines per file, not one. Corrected in the record; the owner sets the number at the approval.
- **C3** (out, ordinary yes, other; fails closed): the P-7 cost was understated: W1-32's command-set case (`test_w1_32_command_set.py:58`) is red with `impact` unrecorded (with four other tickets' commands), and W1-07's pinned list names the set. Corrected in the record.

Judgement: **pass**. The bytes are what the record says, and the section describes the command truly.

```verdict
{"kpis": [{"kpi": "w2-37-cit-p", "verdict": "pass", "findings": [{"id": "C1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "C2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "C3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}], "reviewer": "independent-auditor, fresh read-only session; not the author"}
```
