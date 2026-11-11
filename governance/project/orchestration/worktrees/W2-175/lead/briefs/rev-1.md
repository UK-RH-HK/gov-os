# Brief: independent review, round 1 of at most 2, DAEO-wahn (W2-175), the role-template delta

You are a fresh, read-only **independent-auditor** session (template `role-reviewer`, in your system prompt), started by the ticket lead. You write nothing: no file, no commit. Your last message is your record; the lead commits it as the probe record. Where this brief and the copied `EMG-common.md` / `EMG-d4b-launched.md` differ, **this brief holds**. This brief was written by hand: `gov context DAEO-wahn --role independent-auditor` refused (`CONTEXT_OVER_CEILING`, 21213 of 6000 tokens; the CTO's trim, P-3).

## Identity
- Check: `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-wahn`); `git rev-parse --show-toplevel --abbrev-ref HEAD HEAD` (expect `/home/usain/gov-os-worktrees/W2-175`, `w2/W2-175`, head `44d83e22d7e7…`). Different: stop and say so.
- **Step 0, the sandbox check, reported first in your record:** (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-wahn','w').write('x')"` must FAIL; (b) `git update-index --refresh` must work. If (a) wrote the file, stop and return.
- Any probe script goes under your session's temp folder (`printenv TMPDIR`), never in the worktree; if a Write there is refused, run probes as one-line commands and say so.

## What you review (the head `44d83e22d7e7` of `w2/W2-175`)
The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-wahn.md` (read it whole: KPI lines S1-S7, F1, F2, the Interface section, the non-goals, the "Scope amended" line at the end). Base: `7709021ad6cc`. The ticket's own changes (the branch also merged `w2/integrate` at `6dc99e2c1`, which brought W2-170's files; those are not this ticket's):
- `git diff 7709021ad6cc..HEAD -- template/governance/kernel/templates/` — the seven role templates, 1.0.0 to 1.0.1 (product-spec commit `c816990fcdb4`)
- `git diff 7709021ad6cc..HEAD -- template/.rulesync/subagents/` — the six role sources re-composed by `gov.adapters.portability.compose()` (commit `44d83e22d7e7`, the CTO's scope amendment P-2 (a))
- `docs/changes/W2-175-CIT-P.md` — the CIT-P record (commits `c816990fcdb4`, `f0cb5618a`, `44d83e22d7e7`)
- `tests/acceptance/W2-175/` — the independent test designer's cases (`d8dd03839803`, 51 cases). You read everything, tests and code alike [DEC-820].
- `git diff --name-only w2/integrate...HEAD` lists the ticket's paths (F2's close-time check).

## Questions to answer (each KPI line gets a verdict)
1. S1-S4: does each template carry each required statement as one statement (one paragraph, list item or table row), in the Interface section's words (a template may shorten a line, never drop an idea), ending with the right bracketed id? Is the stop sentence byte-equal to `template/governance/kernel/templates/brief.md` line 62? Is role-cto's decision-record line unchanged byte for byte and does role-cto carry no REC line?
2. Non-goals: is any rule a template already carried reworded or dropped, or any rule beyond the three added? Does any added line contradict an existing line of the same template (e.g. role-reviewer's existing read rules vs "You read everything"; role-test-designer's item 4 vs the new designer line)?
3. S5: only `version` changed in each front matter; prose budgets (facts.yaml) held; placeholders all in `keys.yaml`.
4. F1: every bracketed decision id in the added lines is ACCEPTED in `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` (grep the register by id only) and is the decision that governs the rule (DEC-820 for Policy 2, not DEC-508 or DEC-849; DEC-861 for the record rule; DEC-1137 for the stop).
5. The six `.rulesync` files: is each exactly `compose(Path("template"), role)` at the head (a one-line `python3 -c` with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-175/src`, comparing bytes, is enough)? Does the diff add only the template lines?
6. S7: does the CIT-P record have a section per CAP-33 step; does every sha256 in both tables equal `sha256sum` at the head (and every base sha256 equal `git show 7709021ad6cc:<path> | sha256sum`)? Do `decisions_read` and `decisions_carried` cite DEC-1137, DEC-820 and DEC-861? Is `status` PROPOSED (not ACCEPTED before the owner's approval)?
7. The tests: do the W2-175 cases test the KPI lines as written (could one pass while its KPI line is false)? F1's "fails when one file's sentence is changed by a letter": does a case show it?
8. F2 and S6: the lead's own results (below) name what stays red until the copies ACT. Is that reading right (the root `.rulesync/` and `.claude/templates/` copies are out of this ticket's paths by DEC-315)?

## The lead's own results (do not re-run the suites)
- `gov accept DAEO-wahn` at `44d83e22d7e7`: pass, 51 passed, 0 failed (success-1 to -5, -7, failure-1).
- S6 (`tests/acceptance/W2-128 W2-152 W2-153`, heavy slot, empty HOME): 247 passed, 7 failed: the six `test_s3_each_role_source_…[<role>-.rulesync]` (the root sources) and `test_s3_guard_the_check_finds_no_role_source_drift_in_this_repository`. All six `[<role>-template/.rulesync]` cases pass. The seven reds are the root copies, which the copies ACT writes after the owner's approval (the ticket's "Scope amended" line).
- lead_verify: named in the probe record by the lead.

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.

For a template, "fails open" means a launched session is told something that lets it do what a rule forbids, or is no longer told a rule it was told before; "loses work" means a rule's wording now contradicts another so a session stops wrongly. A wording preference is `other`.

## Rules
- Policy 2: (a) never print a secret or key; (b) the held-out qualification material's contents never; (d) the hidden half of an evaluation set (`~/gov-os-eval`) never. You read everything else, tests and code alike.
- DEC-732: any `gov` or Python check runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-175/src` per command.
- Memory: Read and Grep only (no `gov retrieve` in the sandbox, DEC-1065); search again once in different words; two searches in all.
- Command forms: one simple command per Bash call; no `cd ... &&`, here-documents, backticks or `$(...)`.
- Row W2-L423's rule (DEC-911): hashes and sha256 in your record as 12 digits.
- **Refused twice for the same call: stop and say so. Never work around a refusal: report it.**

## Return (your last message; nothing else is read)
The twelve fields first, each a labelled line; then each finding as `RV<n>: <file:line> <what>` with its two lines (`Ordinary work: …`, `Consequence: …`) and `Scope: in|out`; then, last, exactly one fenced block opened by ```verdict holding JSON in this form, one entry per KPI line S1, S2, S3, S4, S5, S6, S7, F1, F2:

```
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "RV1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
In `evidence`: step 0's output, the head at your start and end, `git status --porcelain` at the end, `gov.__file__`, the read refusals you met. Refused twice for the same call: stop and say so.
