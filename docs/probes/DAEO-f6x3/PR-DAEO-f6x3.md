---
type: probe
task: DAEO-f6x3
reviewer_session: 48f4f52d-2120-40ad-9241-3a24197b79c2
implementer_session: b31977b3-9b4c-4200-813e-008cb7a9f938
test_designer_session: f9699e70-ce75-418f-baa3-e62654ad7852
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 908a6c2527edb0c0d2a7cdc5ff44ae38ec3e4fa3
decisions_applied: [DEC-1071, DEC-1099, DEC-1052, DEC-1010]
---

# Probe record: W2-146 (DAEO-f6x3), STANDARD review round 1

## Summary

- **What was probed.** Head `908a6c2527edb0c0d2a7cdc5ff44ae38ec3e4fa3` of `w2/W2-146` (merge base with `w2/integrate`
  `3556fd7d1825`). The change: the kernel's path-map schema gains `id_forms` / `$defs/id_form`;
  `gov.retrieval.lexical` gains `id_forms(root)` and `ids_in(text, forms=())`; `gov.retrieve.command._nowhere` passes
  the forms. Implementer commits `de8378720`, `ed8aaa8ca`, `2cbac9246` (engineer, session
  `b31977b3-9b4c-4200-813e-008cb7a9f938`); acceptance tests `ccf9b4446` (independent test designer, session
  `f9699e70-ce75-418f-baa3-e62654ad7852`), merged by the lead in `908a6c252`. Interface: the ticket's `## Interface`
  (P-W2-146-1 (a), accepted by the CTO 2026-11-12 09:25).
- **Who probed.** A fresh read-only reviewer: role `independent-auditor`, session
  `48f4f52d-2120-40ad-9241-3a24197b79c2`, 2026-11-12, Opus 5.5 effort high (class C2), started through `gov launch`
  under its OS sandbox (trial file write refused, as it should be). It wrote nothing in this worktree: the lead's
  tripwire shows changes only in other sessions' trees (the main tree's and the stores' heads, W2-115, W2-159), none
  in W2-146, and `git status` was empty at its end.
- **Threat model (DEC-801, DEC-808).** Honest mistakes in ordinary work. Only a finding that is in scope, reachable in
  ordinary work and fails open or loses work fails the review.
- **Verdict: PASS**, 5 findings, all recorded rows; no new round.

## The reviewer's verdict block

```verdict
verdict: PASS
probed_commit: 908a6c2527edb0c0d2a7cdc5ff44ae38ec3e4fa3
findings: 5
```

Per KPI: S1 pass (R2, R3, R4), S2 pass, S3 pass (R1, R5), S4 pass, F1 pass, F2 pass, F3 pass.

## The lead's six questions, as answered

1. **Fail-open paths:** none in ordinary work. `id_forms(root)` is called at `src/gov/retrieve/command.py:60`, outside
   the records check's try/except (:66-70), so `CONFIG_INVALID` is never swallowed and is raised before any search
   (:72). Every malformed entry raises `CONFIG_INVALID` naming `id_forms[i]` (`src/gov/retrieval/lexical.py:204-214`).
2. **No form declared:** `forms=()` runs the old expression (`lexical.py:228-229`); 20,000 random texts compared old
   and new, with no form and with a form matching nothing: 0 differences. Only `command.py:61,63` pass forms;
   `_lead_id`, `_words`, `_ranked`, `memaudit/preflight.py:378` unchanged.
3. **Whole-token and overlap rules** match Interface point 3 (`lexical.py:218,230-239`): `SPEC-4.2` read whole;
   `XREQ12`, `REQ123a`, `rq-7-b` not read.
4. **F2:** a present id of each planted form is found by the per-name search (tokenizer `porter unicode61 tokenchars
   '_'`, `_ranked`'s substring check, `whole_id`), confirmed end to end by the acceptance suite.
5. **Tests check each KPI line**, none vacuous: removing the forms in `_nowhere`, the overlap rule, the whole-token
   check or the loud error turns tests red.
6. **Schema:** only `id_forms` and `$defs/id_form` added; refuses nameless, patternless, non-compiling, empty,
   non-string, extra-key entries and a non-list under `FormatChecker`.

## Findings and the lead's judgement

| Row | Finding | Ordinary work | Consequence | Scope | Lead's judgement |
|---|---|---|---|---|---|
| R1 | A misspelled top-level key (`id_form:`) declares nothing, silently; the JSON schema is not run at load time and the top level stays open | yes | fails open | out (Interface point 1 keeps the top level open and the loader untouched, accepted by the CTO) | Residual, not this ticket's: the same holds for every optional path-map key today. Follow-up for the CTO/owner: check `path-map.yaml` against the JSON schema in an ordinary check (e.g. `gov check`), which also closes R2 and R3 |
| R2 | A YAML null `id_forms` declares nothing at run time | no | fails open | in | Row (the lead's known judgement; reviewer agrees) |
| R3 | Extra keys in an entry (e.g. `flags:`) ignored at run time | no | fails open (case variants) | in | Row (known judgement; inline flags are the documented way) |
| R4 | `re.compile` raising `OverflowError` (e.g. `a{4294967296}`) crashes instead of `CONFIG_INVALID` | no | other (fails closed) | in | Row |
| R5 | A loose repository pattern that swallows trailing punctuation (`SPEC-[\d.]+` on "SPEC-4.2.") can stop on an existing id | no | other (fails closed) | in | Row; depends on the repository's own pattern |

No finding is in scope, reachable in ordinary work and failing open or losing work: the review passes (DEC-1010: one
round, no FAIL decided away; the verdict is the reviewer's).

## The reviewer's test runs

Inside its sandbox, `heavy_slot.sh` could not take its lock in a read-only `/tmp`, so it ran serially without it
(`-p no:xdist`, TMPDIR under its own temporary folder, empty HOME, the exclusion filter): the four W2-146 files together
175 passed, 39 deselected (the opt-in breadth rule; `--optin=breadth` on the unit file: 57 passed);
`tests/acceptance/W2-146/test_w2_146_stop.py` 63 passed, 0 skipped.

## Records

- Reviewer's full return: `.gov-runtime/scratch/lead/log/rv-1.json` (worktree scratch); brief `briefs/rv-1.md`.
- Lead's verification: see `docs/changes/W2-146-CIT-P.md` §6.
