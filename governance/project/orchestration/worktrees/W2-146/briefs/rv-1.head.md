# Brief rv-1: independent-auditor (STANDARD review) for DAEO-f6x3 (W2-146), class C2

You are a fresh, read-only reviewer. You write nothing in the repository; your verdict is your last message. Review
head `908a6c2527ed` of branch `w2/W2-146` in /home/usain/gov-os-worktrees/W2-146 against the ticket's KPI lines
(S1-S4, F1-F3) and its binding `## Interface` (P-W2-146-1 (a)): ticket text at
/home/usain/gov-os-worktrees/W2-146/.tickets/DAEO-f6x3.md (and in the context packet below).

## What to probe
- The change (merge base with w2/integrate `3556fd7d1825`; `git diff 3556fd7d1825 908a6c2527ed -- <path>`):
  - `template/governance/kernel/schemas/path-map.schema.json`: `id_forms` and `$defs/id_form` (15 lines added).
  - `src/gov/retrieval/lexical.py`: `id_forms(root)`, `ids_in(text, forms=())`.
  - `src/gov/retrieve/command.py`: `_nowhere` passes the forms.
  - Tests: `tests/acceptance/W2-146/` (independent test designer, `ccf9b4446`), `tests/unit/retrieval/test_w2_146_id_forms.py`,
    `tests/unit/retrieve/test_w2_146_stop.py` (engineer). Evidence: `docs/changes/W2-146-evidence.md`.
- Commits: `de8378720`, `ed8aaa8ca`, `2cbac9246` (engineer, session b31977b3-9b4c-4200-813e-008cb7a9f938), `ccf9b4446`
  (test designer, session f9699e70-ce75-418f-baa3-e62654ad7852), merge `908a6c252` (lead).
- Questions the lead wants answered (with file:line):
  1. Fail-open paths of the stop: can a declared form ever be silently ignored (malformed entry skipped, a GovError
     swallowed by `_nowhere`'s records-check catch, a null `id_forms` at run time, extra keys)? Is a CONFIG_INVALID
     raised before any search?
  2. `forms=()` byte-identical to the old `ids_in` (S2/S4); no other caller of `ids_in` passes forms (Grep `ids_in(` under src/gov).
  3. The whole-token and overlap rules against Interface point 3 (longest at a start wins; `SPEC-4.2` whole under a
     dotted form; a form's match inside a longer token not read).
  4. F2: a declared-form id present as a whole token on one line is retrieved, not stopped, for every planted kind
     (space, lowercase, underscore, dotted, no hyphen): does the per-name `lexical.search` + `whole_id` find it?
  5. Do the tests actually check each KPI line (would they go red if the behaviour broke)? Any test that passes vacuously?
  6. Schema: refuses nameless, patternless, non-compiling (`format: regex` under `FormatChecker`); nothing else moved.
- Already known, judged by the lead (say if you disagree): a null `id_forms` is read as nothing declared at run time
  (the schema refuses null); runtime ignores extra keys in an entry (the schema refuses them); with no form declared a
  dotted id still stops on its fragment (today's behaviour, pinned).

## Verification already run (lead, outside the sandbox, head 908a6c2527ed)
lead_verify: 5248 tests, 6 failed, 8 skipped (parallel); serial 2/2 green. The 6 are all `tests/unit/accept/test_w2_96_*`
signal/timeout cases (not this ticket's paths); re-run alone 2 passed, 4 failed; the same 4 fail on w2/integrate's head
`ee242e55` (shared base reds). You may run pytest on this ticket's files to check a claim; if you do, use exactly:
`mkdir -p /tmp/w2-146-rv && env TMPDIR=/tmp/w2-146-rv HOME=/home/usain/gov-os-worktrees/W2-146/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-146/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <path> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
(every pytest through heavy_slot.sh, TMPDIR outside the repository and outside ~/gov-os-runs).

## Rules
- Read-only: no Write or Edit in the repository, no commit, no install, no network. Search with Read, Grep and Glob;
  if the first search does not answer, search once more in other words (DEC-1065). Sources: DEC-1071, DEC-1099,
  DEC-1098, DEC-1097, DEC-900 (read by id in docs/DECISION_REGISTER.md; grep the register only by id).
- Threat model (DEC-801, DEC-808): honest agent mistakes and plausible accidents in ordinary work, not adversaries.
  Every finding carries `Ordinary work: yes|no, because ...` and `Consequence: fails open|loses work|other`, a
  severity, file:line and a concrete failure scenario. Only "yes" with "fails open" or "loses work" fails the review.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE) / work_completed / files_changed
(none) / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action.
Then a fenced verdict block:
```verdict
verdict: PASS | FAIL
probed_commit: 908a6c2527ed...
findings: <n>
```
then each finding (R1, R2 ...) with the lines above, then `guard_refusals:` (none, or each: time | form | the hook's
reason | true or false-positive).

## The ticket's context packet (gov context DAEO-f6x3 --role independent-auditor)
