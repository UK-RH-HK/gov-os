---
type: probe
task: DAEO-wi46
reviewer_session: 94bd151d-d1d8-4871-8c76-aaa71f5fe88f
narrow_check_session: b50d44f5-62fd-49c6-bb2b-ce325f70d477
implementer_session: c373daad-ed0e-4f33-96ee-99c90f253460
fix_implementer_session: ace0ce13-5ad5-4d78-94a7-3c20fea6e686
reviewer_wrote_nothing: false
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
narrow_check_judgement: pass
probed_commit: c530a0a1a2365cff3ea136182a8c604ab6c8e1b6
narrow_check_commit: f0259229e2b5eb386e8786588a1720ae7cd4b833
---

# Probe record: W2-98 (DAEO-wi46), the spec-writing skill for product-spec: two review rounds (STANDARD)

## The lead's judgement

**Then: pass on the narrow check (2026-11-13).** The owner chose option (a) below (P-W2-98-R2 (a)): one fix batch,
then a narrow independent check of exactly that fix. The check passed on `f0259229e2b5`; see "Narrow independent
check" at the end. Round 2's verdict stands as written; nothing below it is changed.

**Fail, after the last round.** Round 2 found three findings that are in scope, reachable in ordinary work and fail
open (F1-F3 below). They are near variants of round 1's F1 and F2, next to the forms that round's fix closed. The
lead does not decide a FAIL away and runs no third round (DEC-1010). The next step goes to the owner as a package
with options. No finding loses work. The guard and the sandbox are untouched: the change is a method skill and a
standard-library script that only prints, plus one P1 file it writes beside the spec it reads.

Threat model (DEC-801, DEC-808): honest agent mistakes and plausible accidents in ordinary work. Only "ordinary work:
yes" together with "fails open" or "loses work" fails a round.

## What was probed

- **Branch:** `w2/W2-98`, base `6c2c3ed93bee`, which holds the run 2 acceptance tests.
- **The ticket's change, by three product-spec sessions:**
  - `61b4de632827` (session `9f74f79c-01fb-47cb-8d88-159ab82b0683`): the skill and its `.rulesync` copies.
  - `384c92b8b429` (session `31945b94-eb2e-4ea5-be98-a7874568f0cb`): the lead's hand check found that a wrapped KPI line went unjudged; this commit fixes it.
  - `55b360a5e80c` (session `c373daad-ed0e-4f33-96ee-99c90f253460`): the round 1 fix, B1-B6.
- **Tests, by independent test designers:**
  - `1957fd5d16ab`: 94 cases.
  - `7b08042ee`, `20f9c02ec`: 172 cases for B1-B6, red on `384c92b8b429`, merged in `c530a0a1a236`.
- **Round 1:** a fresh read-only reviewer probed `384c92b8b429`. Role `independent-auditor`, Opus, high effort; session `0cb438cd-d2d4-498b-a8c6-14750f2de799`.
- **Round 2:** a fresh read-only reviewer probed `c530a0a1a236`. Same role and settings; session `94bd151d-d1d8-4871-8c76-aaa71f5fe88f`.
- **How both reviewers worked:** each was started through `gov launch` under its OS sandbox. Each step 0 write outside the worktree failed. `gov.__file__` was this worktree's `src/gov/__init__.py`.
- **What round 2 wrote:** importing `check_spec.py` in memory wrote an ignored `__pycache__/` in the kernel skill folder. It turned three W2-98 cases and eleven W1-38 cases red. The guard refused the reviewer's own `rm`. The lead removed the folder and re-ran those cases (see Evidence). Nothing tracked was written.

## Round 1 (head 384c92b8b429): FAIL on F1 and F2

| Id | Finding | Ordinary work / consequence | The lead's triage |
|---|---|---|---|
| F1 | A KPI line slightly off the form went unjudged, so the spec passed with code or no failure line. Examples: `- K2 :`, `2. K2:`, `- K2a:`, `- K3 (new):`, `- **K2** —`, a column-0 wrap | yes / fails open | Fixed: B1, B2 |
| F2 | Empty privacy and secrets cells passed. So did placeholder owner, source and licence cells (`TBD`, `—`, `-`, `unknown`, `n/a`) | yes / fails open | Fixed: B3, B4 |
| F3 | Ordinary Markdown was refused: `**Fails if:**`, `_Fails if:_`, failure text on the next line, `_word_` emphasis. Prose like `example.com`, `Node.js` and `member(s)` was taken as code | yes / other (fails closed) | The `Fails if:` labels and emphasis are fixed (B6). The prose forms stay a row |
| F4 | Imports: records outside `imports:` were counted, and an allowed record outweighed a forbidden one for the same part. Flow style failed closed | no / fails open | Fixed anyway: B5 (cheap, in S5) |
| F5 | The front matter lacks the template's `output:` key; qa-review lacks it too | yes / other | Row |
| F6 | A measuring source with hidden half `no` passes | yes / other | Row (the yes/no/n/a values are P-W2-98-IF-1's reading) |

The fix went as described behaviours B1-B6 (DEC-136): one batch to a test designer, one to an implementer.

## Round 2 (head c530a0a1a236): FAIL on F1, F2 and F3

All of round 1's reproductions of F1, F2 and F4 are now refused.

| Id | Finding | Ordinary work / consequence | Triage |
|---|---|---|---|
| F1 | A KPI whose `Fails if:` text is only a placeholder passes: `TBD`, `-`, `—`, `n/a`, `?`, `TODO`, `none`, `(none)`, `**TBD**`, `to be written`. So does an empty or placeholder behaviour (`- K1: TBD`, `- K1:`) | yes / fails open | **Blocks**, to the owner |
| F2 | A KPI id line with no bullet (`K2: …`, `**K2:** …`, `  K2: …`, `K2. …`) is read as more of K1's failure text. K2's missing failure line is never noticed, and code in it is named under K1 | yes / fails open | **Blocks**, to the owner |
| F3 | Owner placeholders just outside B4's list pass: `TBC`, `Tbd.`, `N/A.`, `NA`, `nobody`, `to be decided`, `` `TBD` ``, `...`, `<owner>`. So do the licence cells `unlicensed` and `none found` | yes / fails open | **Blocks**, to the owner |
| F4 | Placeholders in the privacy and secrets cells pass (B3 accepts any stated text) | yes / fails open; out of scope (S2's verify line does not name them) | Row |
| F5 | Imports: a capital-I `<!-- Imported: -->` marker is not read, a nested `licence:` key wins, and a part named `<tdd>` is skipped | no / fails open | Row (Wave 3) |
| F6 | Ordinary forms are refused: `**Fails if**:`, sub-bullets under a KPI (B1's design), `1. K1:`, `## 5. KPIs`, bold header words, and prose such as `example.com`, `README.md`, `x86_64` | yes / other (fails closed) | Row |
| F7 | `send\_welcome` (an escaped underscore) is not caught. CamelCase, `::` and `->` are not caught either; they are outside I3 | no / fails open | Row |
| F8 | Round 1's F5 and F6, carried over | yes / other | Row |
| F9 | A `## Accepted by` heading inside a code fence counts as the part | no / fails open | Row |

Round 2 also found these sound:
- PASS is never printed beside a REFUSED or P1 line, and P1 always gives exit 2 or 1.
- None of about 70 plain-prose forms is taken as code.
- Off-form list items and continuation lines are judged.
- The Test data table's columns may come in any order.
- The imports reader handles case, quoting, comments, CRLF and tabs.
- The code has no special case for the planted text.
- SKILL.md matches the template: the sections in order with Sources last, the twelve fields, P3/P2/P1/Emergency, a 98-line body, and the reference one level down.
- The validator exits 0. Both `.rulesync` copies are byte-equal to the kernel source.

## Options for the owner (round 2's F1-F3)

- **(a) One fix batch, then a narrow independent check.** Recommended. Each fix is a few lines and keeps I2/I3's words. Placeholder text in a KPI's behaviour or failure line is refused like an empty one. An unbulleted line starting with a KPI id is refused, quoted, like an off-form list item. The placeholder match ignores trailing punctuation and code spans, and adds `TBC`, `NA`, `nobody`, `to be decided` / `to be confirmed` and a lone `<…>` slot. Cost: one test-design batch and one fix batch (about 40 minutes each, run in parallel), lead_verify, and a narrow check (about 20 minutes).
- **(b) Merge now; F1-F3 land as rows for a later wave.** Cost: until then, a spec can pass with `Fails if: TBD`, an unbulleted KPI or an owner `TBC`.
- **(c) Re-word I2** so that placeholder text and off-form id lines are the reviewer's to catch, not the check's. Cost: an interface change for the owner, and the check's PASS means less.

## Evidence

- **Acceptance:** `gov accept W2-98` at `c530a0a1a236`: 264 passed, 2 failed (success-6 and failure-5, the two `.claude` copy cases), 0 unmapped.
- **lead_verify at `c530a0a1a236`:** 5312 tests, 17 failed. Every failure has one of two causes:
  - The `.claude/skills/spec-writing/` copy is absent until the copies ACT (DEC-1112 (3)). This accounts for W2-98's `test_the_claude_copy_matches_the_kernel_source` and `test_the_adapter_check_finds_no_generated_drift_in_the_real_skill`, and W2-11's `test_the_skill_carries_one_version_in_all_four_places[spec-writing]` (`tests/acceptance/W2-11/test_w2_11_skills.py:140`).
  - Round 2's stray `__pycache__` accounts for the other 14 (three W2-98 copy cases, eleven W1-38 cases).
- **lead_verify at `384c92b8b429`:** 5140 tests; 3 failed, the same three copies-ACT cases.
- **Validator:** `gov.check.skill_validator` on SKILL.md: `{"findings": []}`, exit 0.
- **Copies:** `diff -r` of each `.rulesync` copy against the kernel source is empty. The adapter check reports only `GENERATED_DIFFERS` for the four `.claude/skills/spec-writing/` files.

## Narrow independent check (head f0259229e2b5): PASS

- **The owner's decision:** P-W2-98-R2 (a), 2026-11-13: one fix batch for round 2's F1-F3, then a narrow independent
  check of exactly that fix (no third review round, DEC-1010).
- **The fix, as described behaviours C1-C3** (DEC-136): a placeholder class (empty or no letter or digit; a lone
  `<...>` slot; a deferral such as TBD, TBC, TODO or `to be <word>`; an absence word alone such as none, nobody, n/a)
  refused in a KPI's behaviour and `Fails if:` text (C1) and in the owner, source and licence-or-recipe cells (C3, with
  the "no licence found" forms); an unbulleted line under KPIs that starts with a KPI id refused, quoted (C2).
  - Tests: `6a1290b8eb7d`, `9cf504f573df` (independent test designer, session `d32e0706-2007-4ab3-a739-af272ddecdad`):
    `test_w2_98_review_r2.py`, 236 cases, 186 red at `c0f68478a` for the stated reasons, 50 controls green; merged in
    `f0259229e2b5`.
  - Code: `0b6d3e07746b` (product-spec, session `ace0ce13-5ad5-4d78-94a7-3c20fea6e686`, without reading the tests):
    one `plain()` normalisation and one `is_placeholder()` test used for every text and cell, and a shape rule for a
    KPI-id line; `spec-form.md` states both; the two `.rulesync` copies are byte copies.
- **The check:** a fresh read-only session (independent-auditor, Opus, high; session
  `b50d44f5-62fd-49c6-bb2b-ce325f70d477`) of `git diff c530a0a1a236 f0259229e2b5` on the skill folders and
  `tests/acceptance/W2-98`. It probed in memory with bytecode writing off and wrote nothing (`git status` empty,
  no `__pycache__`).
  - All 29 round 2 reproductions of F1-F3 are refused, exit 1, no PASS.
  - C1-C3 hold as a class: about 230 unplanted variants (case, punctuation, emphasis, backticks, brackets, other
    `to be` phrases and slots, KPI-id shapes such as `K12:`, `K2 -`, tabs, `_K2_:`) are refused.
  - Nothing broken: ordinary owners (`NASA data office`, `None Ltd`, `Na Li`), licences (`Unlicense`), sentences with
    a placeholder word, `Kiosk`/`K8s` continuation lines, prose before the first KPI and `none` in privacy and
    secrets pass; round 1's B1-B6 still hold.
  - The tests test C1-C3, and the code passes them with no special case for the planted text.

| Id | Observation | Ordinary work / consequence | Triage |
|---|---|---|---|
| N1 | Licence wordings outside C3's six forms pass: `licence not found`, `license unknown`, `not licensed`, `no licence stated` | yes / fails open; outside the stated class | Row |
| N2 | A placeholder with extra words passes: `TBC by Friday`, `to be decided later`, `none yet`, `TBD (later)`; also quoted, struck-through or dotted forms (`"TBD"`, `~~TBD~~`, `T.B.D.`) | yes for the first group, no for the rest / fails open; outside the stated class (the whole text is matched, never a word in a sentence) | Row |
| N3 | A KPI id after a heading or quote marker (`### K2: ...`, `> K2: ...`), `k2:` and `K 2:` are not refused | no / fails open | Row |
| N4 | `K12 students see it too.` as a continuation, and an owner of just `Na` or `Nil`, are refused | yes, rare / other (fails closed) | Row |

- **The lead's judgement: pass.** No finding is in the fix's scope with ordinary work and fail open; N1-N4 are rows
  for a later wave (N1 and N2 widen the class beyond the owner's stated behaviours).
- **Evidence at `f0259229e2b5`:**
  - `gov accept W2-98`: 500 passed, 2 failed (success-6 and failure-5, the two `.claude` copy cases), 0 unmapped.
  - lead_verify: 5644 tests, 5634 passed, 3 failed, 7 skipped. The three failures are the copies-ACT cases named
    above (W2-98's `test_the_claude_copy_matches_the_kernel_source` and
    `test_the_adapter_check_finds_no_generated_drift_in_the_real_skill`; W2-11's
    `test_the_skill_carries_one_version_in_all_four_places[spec-writing]`, `tests/acceptance/W2-11/test_w2_11_skills.py:140`).
  - The check's own suite run: 500 passed, 2 failed (the same two). Validator: `{"findings": []}`, exit 0. `diff -r`
    of each `.rulesync` copy against the kernel source: empty.
