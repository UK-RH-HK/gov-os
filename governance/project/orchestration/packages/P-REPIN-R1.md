# P-REPIN-R1 — Eight base reds since the settings regeneration refuse every close; the queue stopped after W2-70's refusal

- **Priority:** P1 (it gates every close). **Raised:** 2026-10-27 11:10 GMT, by the orchestrator.

## 1. Context

- The first re-pin (DEC-922) was smoke-tested with the pinned `gov check` and the guard, both green. No full regression ran on the regenerated settings before the closes.
- The close queue started for seven tickets (DEC-923). Its first close, W2-70's, ran 68 minutes. It was then refused (exit 3, count 1; repair ticket DAEO-2upp, committed by the close). The queue stopped there, as it does on any refusal.
- W2-57's lead, verifying on the same base, met the same eight reds.

## 2. What happened

The full regression had 16,199 passed, 32 skipped and 9 failed. One red is already fixed; eight remain. None is W2-70's work.

| Reds | Cause | Fix |
|---|---|---|
| W1-01 `test_docs_source_deny_rules_survive_the_change` ×4; W1-47 `test_the_other_deny_rules_are_in_place[Read(./docs/source/**)]`, `[Edit(./docs/source/**)]` | They enforce the two `docs/source` deny rules that the regeneration removed (P-I1-2, DEC-899, done in DEC-922 Part B). The DEC-866 sweep before the ACT missed them; that miss is the orchestrator's. | A test designer retires the six `docs/source` cases: the folder left the tree on 2026-10-01. Retiring a test is the owner's decision. |
| W1-49 `test_without_tk_the_block_says_so_and_holds_the_rest[not on PATH]` | The test's sandbox has neither tk nor gov. The new lifecycle hook line (DEC-917, W2-65) ends with 1 when it finds no pinned gov, and the test expects 0. | The test designer gives the sandbox a gov (a link to the pinned one), so only tk is missing (`Rewrite-Reason: DEC-917`). |
| W1-06 `test_every_entry_outside_the_stack_cites_a_decision_that_names_the_tool` | The re-pin's registry entry for `gov` cites `approved_by: DEC-921`, whose text does not name gov. The orchestrator's `repin_registry.py` wrote it before DEC-922 existed. | One line: `approved_by: "DEC-922"` (DEC-922 records the re-pin of gov). |
| W2-69 `test_the_unit_folder_named_secrets_is_gone` | A leftover `tests/unit/secrets/` that held only git-ignored `__pycache__` files. | **Done:** removed on 2026-10-27. |

**Also found, and fixed in the orchestrator's own tools:**
- **The skip guard** compared test ids in two forms (the known list is dotted, the pinned close's evidence uses paths), so it would have stopped after every passing close. It now reads both forms.
- **Two skips added to the known list** (DEC-915 item 2), both effects of the pinned interpreter:
  - W1-03 `[the-gov-package-is-missing]`;
  - the govbridge parity case, whose message is now longer.
  The guard now passes on this close's 32 skips.
- **The queue's collection log** now keeps only errors and the summary.

**Still open, for the owner:** one of W2-69's acceptance cases has row W2-L423's keyword in its own name. So every full run's JUnit XML holds it, with no hash beside it. The close writes that XML under `.gov-runtime/close/`, and the warning (DEC-923) would stop the next queue on it.

## 3. Why it matters

No close can pass until these eight are fixed. W2-70's next refusal for the same reds would be its second, which goes to the owner as an escalation.

## 4. Options

- **(a) Recommended: one LITE test-revision ticket, W2-74.** A fresh test designer:
  - retires the six `docs/source` cases (`Rewrite-Reason: DEC-899 P-IS-5, DEC-922`);
  - revises W1-49's case (`Rewrite-Reason: DEC-917`);
  - renames W2-69's case id so the keyword is not in it (`Rewrite-Reason: DEC-911`), with its input unchanged.

  Its paths: `tests/acceptance/W1-01/test_w1_01_settings_deny.py`, `tests/acceptance/W1-47/test_w1_47_settings_rules.py`, `tests/acceptance/W1-49/test_w1_49_precompact.py` and the W2-69 file. None is held by W2-57, W2-07 or W2-67.

  The orchestrator commits the registry line itself, under this decision.

  Until W2-74 merges, the keyword warning also leaves out the close's own JUnit evidence (`.gov-runtime/close/`), which the judge writes and which holds no hash.

  Then the queue runs again, W2-70 first. About 2–3 hours to merge, plus the queue.
- **(b) The same, but `accepted_reds` entries for the eight now,** by the owner's commit, so the queue can run before W2-74. That grows a list that only shrinks (DEC-766), and the entries come out again a few hours later.
- **(c) Re-baseline:** put the two `docs/source` deny rules back in the settings. That undoes P-I1-2 for a folder that no longer exists.

## 5. Recommendation

(a). Confidence: high.

Classification (DEC-809):
- **The six `docs/source` cases and the W1-49 case:** `Ordinary work: yes, because every close runs them; Consequence: other (they refuse; they fail closed).`
- **The registry line:** the same classification.

## 6. What it blocks, and what waiting costs

- **It blocks** all closes: the seven queued and every later one.
- **It does not block** W2-07's round 2 (running) or W2-57's run 2 (waiting on B1, below).
- **Waiting costs** the whole close pipeline: about 1 hour per close, once unblocked.

---

# P-W2-57-B — W2-57's run 1 returned PACKAGES: the nightly route needs `command.py`

- **Priority:** P2 (it gates W2-57's run 2). **Raised:** 2026-10-27 11:10 GMT.

## 1. Context

DEC-889 item 5 takes the live and real-model files out of the close and into the nightly.

## 2. What happened

- **Done:** run 1 did the rulesync probe fix (four parallel runs, 0 silent skips), the doctor probes and the reworked serial list. Review 1 passed.
- **Blocked:** the route out of the close needs the serial phase's call in `src/gov/close/command.py`, which is outside W2-57's paths. DEC-924 gave `command.py`'s gate (h) line to W2-07's round 2.

## 3. Why it matters

Without the route, the live and real-model files stay in every close: about 300 s and paid sessions. W1-46's 23 `load_sensitive` entries and W1-19's warm-p95 entry cannot come off the list.

## 4. Options

- **B1 (a), recommended.** Widen W2-57 to `command.py`, for the serial phase's call to `serial.py` only. W2-07's round 2 keeps gate (h)'s line. Both are in `command.py` but in different functions, and whichever merges second merges back (DEC-924 item 3).
- **B1 (c).** Defer the route; this changes DEC-889 item 5 for W2-57.
- **B2 (b), recommended.** KPI 6's second half (the guard's 20-second deadline under load) is left to the resource gate and the quiet window rather than new serial entries. It was seen once at load 52 and never in a close.
- **For the orchestrator to decide as delegated unless the owner objects:**
  - B3 (a): W1-19's real-model file is named for W2-57's test designer (W2-M332's sampler);
  - R1: the doctor-budget fix rides along in run 2 (DEC-802);
  - R2: W1-30's r15 file is named for the test designer (a masked timeout, as in W1-38);
  - A1 (a): the doctor exception case stays strict.

## 5. Recommendation

B1 (a) and B2 (b). Confidence: high for B1, medium-high for B2.

Classification: `Ordinary work: yes; Consequence: other` (the route is missing; nothing fails open).

## 6. What it blocks

W2-57's run 2 (the route, the review on its new head, and the two `load_sensitive` removals that wait on the route).
