# DND sweep 11-14: the 8 notes settled with evidence (read-only check, 2026-11-14)

Source file: `governance/project/orchestration/packages/DECIDED-NOT-DONE.md` (DND), tree at `w2/integrate` (HEAD `18a279055`; sweep commit `494d5c933`). Nothing tracked was edited; nothing under `~/gov-os-eval`, `hidden/` or any held-out material was opened. Form of every new leading text: `<new state> (sweep 11-14 notes, DEC-1180 (4); evidence: ...) · was: <old leading words>`.

Verdicts: row 122 NOT STARTED (trigger met); row 123 NOT STARTED (trigger met); row 125 DONE (`f48697a0e`, live at the next re-pin); row 137 open (list made, edits not made; trigger met); row 4 redundant (SUPERSEDED by row 34); row 136 stays IN PROGRESS (nothing newer); row 154 stays DONE for the working size but "Left" must add the two peaks (not measurable today); row 85 wording confirmed; row 166 wording needs one correction (the 99 % push is not superseded).

---

## Note 2: rows 122, 123, 125

### Row 122 (D1: git diff of two blob refs refused) -> NOT STARTED, trigger met

Finding: W2-42a's fixes do not cover D1.
- W2-42a is `.tickets/DAEO-03ub.md` (status closed). Its KPIs are the Bash write parser (`bash_writes.py`: heredoc, here-string, apostrophe, variables, globs, `git checkout`/`dd`/`sort -o` as writes) and the read judge's literal-path misreads (KPI 6, 7, 10). None names a revision-colon-path diff.
- The close you cite, `77220f814` ("merged and closed in one step by the merge queue (DEC-989)"), touches only `.tickets/DAEO-03ub.md` and `closes/W2-42a-DAEO-03ub.md`. The work behind it (`git log --grep W2-42a`): `f16075e43`, `669d87c91`, `fa77bb331`, `1388fcec6`, `07fb14799` (apostrophe, DEC-1174 (1)); `df7468015`, `885b0d0f6`, `9196ce961` (here-string, DEC-1164 (18) R3 F1). Their `--stat` lists `src/gov/guard/bash_writes.py`, `src/gov/guard/decide.py` (two commits) and `tests/unit/guard/test_w2_42a_*`. No W2-42a commit after `94c85f361`/`aac18cca0` (11-02) changes `src/gov/guard/reads.py` (the only other W2-42a-grep commit on `reads.py` is the merge `4caf8475f` of w2/integrate into the branch).
- D1's cause is still in the code: `src/gov/guard/reads.py:1721-1725` ("Each revision must be a commit: git log passes over a blob or tree"): every revision word gets `^{commit}` in `rev-parse`, so `<rev>:<path>` on both sides of `git diff` fails and is refused. D1 appears only in W2-141's ticket (`.tickets/DAEO-xwro.md:104`, closed) and DND; no test in `tests/unit/guard/` names a blob-ref diff.
- Trigger "after the lift": met. DEC-1158 lifts the emergency (11-13); re-pin `8f00bb90810b` (11-11 13:31).
- Route: W2-141 (`DAEO-xwro`) and W2-42a are closed; `reads.py` is already in W2-42a's `allowed_paths`, so reopening W2-42a is within its purpose (DEC-1157 (12), as DEC-1164 (18) did); a new ticket is the owner's (DEC-974). A fix to a guard's own fault goes by ACT (DEC-1133 (1)-(2)).

Proposed new leading text (state cell):
`NOT STARTED, trigger met (the lift: DEC-1158; the re-pin 8f00bb90810b): an engineer round, a reopening of W2-42a (reads.py is in its allowed_paths) or a ticket from the owner; W2-42a's closes 77220f814 did not touch reads.py (sweep 11-14 notes, DEC-1180 (4); evidence: reads.py:1721-1725 still resolves each revision word with ^{commit}; W2-42a's commits 9196ce961, df7468015, 885b0d0f6, 07fb14799, 1388fcec6, fa77bb331, 669d87c91, f16075e43 change bash_writes.py and decide.py only) · was: NOT STARTED: after the lift`

### Row 123 (the guard's `error` refusals) -> NOT STARTED, trigger met

Finding: not covered by W2-42a.
- `list index out of range`: no `IndexError` handling or case in `src/gov/guard/` apart from `containment.py`; nothing in `tests/unit/guard` or `tests/acceptance/W2-42a`. W2-42a's KPIs never name the error path. The "revision it cannot classify" half is the same `reads.py:1721-1725` / `_REV_FAULT` code as D1 (three of the 15 error-path refusals are an auditor's `git diff rev:path`, `packages/SETUP-A-BAR.md:269-270`).
- Triggers: "after the lift" met (DEC-1158). DEC-1128 (3): "the guard's own error-path faults (DECIDED-NOT-DONE row 123) are fixed first after the lift" (`docs/DECISION_REGISTER.md:14410`). DEC-1133 (2): "the error path and the listing rule are fixed first, each by ACT; set-up A runs after they land". SETUP-A-BAR sizes the fix as "small and testable (replay the 15 calls)". No ticket and no ACT package exists for it (`.tickets/` has only DAEO-xwro mentioning D1; `packages/` has no ACT-GUARD-FIX-5). The row's "W2-42a holds the parser" is spent (W2-42a closed `77220f814`); only SETUP-A-BAR's listing rule (item 2) may have gained from W2-42a, a separate check.
- The wider harvest filter and `guard_refusals.py`: no commit; `log/guard-refusals.jsonl` is CTO scratch, not checked here.

Proposed new leading text (the whole state cell is the old text):
old: `NOT STARTED: after the lift, a guard ticket (W2-42a holds the parser) and a wider harvest filter; \`guard_refusals.py\` by hand at the next quiet hour`
new: `NOT STARTED, trigger met (the lift: DEC-1158; DEC-1128 (3) fixes the error path first after it; DEC-1133 (2): each by ACT): a guard fix with a replay of the 15 logged calls and a wider harvest filter, by ACT; guard_refusals.py by hand at the next quiet hour (sweep 11-14 notes, DEC-1180 (4); evidence: no IndexError case under src/gov/guard or tests/unit/guard; reads.py:1721-1725; no ticket or ACT package; W2-42a closed 77220f814 without the error path) · was: NOT STARTED: after the lift, a guard ticket (W2-42a holds the parser) and a wider harvest filter`

### Row 125 (W2-05's close: `role_paths.py` not on `git_env`/`git_binary`) -> DONE

Finding: done by W2-05 itself on 11-11, after the audit.
- `f48697a0e` 2026-11-11 19:35 "W2-05: role_paths' four git calls take git_env(<folder>, pinned=True) and git_binary() (sweep row 71)" (`Task: DAEO-0z8c`): `src/gov/util/role_paths.py` (+25/-7) and `tests/unit/gitenv/test_role_paths_env.py` (210 lines). Now `src/gov/util/role_paths.py:39` imports both, `:61-65` calls `git_binary()` and `env=git_env(where, pinned=True)`.
- W2-05 review round 2 (the last) READY, probe record `52de591b8`; merged and closed `7a809e63b` (merge `764495164`); `.tickets/DAEO-0z8c.md` closed.
- "the next pin carries it": the only re-pin is `8f00bb90810b` (11-11 13:31, before `f48697a0e`); no later re-pin commit exists. The code is on `w2/integrate` but not in the live gov until tonight's re-pin (DEC-1180 (3)). "then a probe": the review's probe record is `52de591b8`; no separate post-pin probe seen.

Proposed new leading text:
`DONE f48697a0e (W2-05, 11-11 19:35; merged and closed 7a809e63b); live at the next re-pin (none since 8f00bb90810b) (sweep 11-14 notes, DEC-1180 (4); evidence: role_paths.py:39 and :61-65; probe record 52de591b8; ticket DAEO-0z8c closed) · was: NOT STARTED: after the re-pin, a small engineer round, then a probe; the next pin carries it`

---

## Note 3: row 137 (set-up B dropped entirely: the sweep)

Finding: open, not done. Row 135 is DONE, so the trigger ("with row 135's helper") is met, but `packages/SWITCHED-OFF-1.md` §5 (lines 171-201) is a list only: line 173 says "Lists only; nothing edited". It also does not claim to cover "every ticket, row, package and brief"; it lists S1-S20 and line 201 says "no ticket, brief or prompt in `governance/project/briefs/` plans sandboxed leads beyond S15 and S16".
Evidence the edits were not made (checked at HEAD):
- S1 `docs/plan/WAVE_3_PARKING.md:36` W3-P30 still reads "Set-up B (the sandbox generated from the path map), built by a different route" (the list says Retire).
- S6 `governance/project/orchestration/DECISIONS-IN-FORCE.md:456` (was :395) still reads "(set-up B a Wave 3 row)".
- S8 `packages/LIFT-1/P1-PLAN.md:191` still "set-up B a Wave 3 row".
- S11 `packages/ACT-INDEP-WALLS-1.md:103, 204` still "set-up B's sandbox".
- S12 `.tickets/DAEO-wnnz.md:33, 44, 115, 118, 145` still "Set-up B is a Wave 3 row" (a reviewed ticket: marked KPI-line edit, DEC-757 (6)).
- S13 `docs/changes/W2-56-CIT-E.md:29, 214` still "is Wave 3's" / "deferred to Wave 3 with set-up B".
- S7 DND row 66 (line 107) item text still "set-up B a Wave 3 row".
- S15 DEC-769's status line has no DEC-1128 (4) mark (it reads "Changed by: DEC-953 (item 2)"); DEC-1099 is marked only "Changed by: DEC-1176" (S5). `governance/project/prompts/w2-orchestrator.md:143` still has "After W2-21 closes: gov launch lead ... sandboxed" (S16 re-word).
- Owner-to-say items S14 (W2-40's lifted lines) and S18 (retire `drafts/sandbox-exp/`) have no decision in the register.
Missing: the apply step of S1, S5-S8, S10-S16 (re-words, marks, retire W3-P30, header notes), the two owner items, and a closing re-grep over tickets, rows, packages and briefs.
Route: DEC-866 marks and re-words are the CTO's (W2-56's reviewed ticket by a marked edit, DEC-757 (6)); S14 and S18 go to the owner as one package at once (DEC-1180 (4)).

Proposed new leading text:
`NOT STARTED, trigger met (row 135 DONE 11-11): the list S1-S20 exists (packages/SWITCHED-OFF-1.md §5, "Lists only; nothing edited") and its edits are not made; next: apply S1, S5-S8, S10-S16 (marks, re-words, W3-P30 retired), the owner's S14 and S18, then a closing re-grep of tickets, rows, packages and briefs (sweep 11-14 notes, DEC-1180 (4); evidence: WAVE_3_PARKING.md:36, DECISIONS-IN-FORCE.md:456, P1-PLAN.md:191, ACT-INDEP-WALLS-1.md:103/204, W2-56-CIT-E.md:29/214, DAEO-wnnz.md:33/44/115/118/145 and DND row 66 all still say set-up B is Wave 3; DEC-769 and DEC-1099 carry no DEC-1128 (4) mark) · was: NOT STARTED: with row 135's helper`

---

## Note 4: rows 4 and 34

Finding: row 4 is the redundant one; row 34 is the live row.
- Row 4 = DEC-1097 (10) (11-08): "G1's 'fewer scored pairs' (DEC-1094 (1)): not before the 80; brought to the owner after the lift as an option, the 138 re-measured if adopted" (`docs/DECISION_REGISTER.md:13884-13885`). Trigger: the lift.
- Row 34 = DEC-1099 (3) (11-09), FORECAST-W2-1's proposals: "G1's fewer scored pairs deferred until after EXAMIN's copy" (`docs/DECISION_REGISTER.md:13952-13953`). It is later and moves the same item's trigger from the lift to EXAMIN's copy.
- The sweep's row 4 text ("trigger met, next: the G1 option") therefore contradicts DEC-1099 (3). EXAMIN's copy has not started: DEC-1180 (3) starts the EXAMIN CTO tonight after the re-pin and the operator's setup.
- Row 4 carries one thing row 34 lacks, "the 138 re-measured if adopted"; move it onto row 34.

Proposed new leading text, row 4 (replaces the leading span; the rest of the row stays after it):
`SUPERSEDED by row 34 (DEC-1099 (3), 11-09, deferred G1's fewer scored pairs from the lift to after EXAMIN's copy; DEC-1097 (10)'s "138 re-measured if adopted" goes with it) (sweep 11-14 notes, DEC-1180 (4); evidence: docs/DECISION_REGISTER.md:13884-13885 and :13952-13953; EXAMIN's copy not yet started, DEC-1180 (3)) · was: NOT STARTED: the lift is recorded (DEC-1158); next: the G1 option and the 138 re-measure (see row 34: still WAITS: EXAMIN's copy)`

Proposed new leading text, row 34:
`WAITS: EXAMIN's copy (the EXAMIN CTO starts tonight, DEC-1180 (3)); then the G1 option to the owner, the 138 re-measured if adopted (DEC-1097 (10), folded from row 4) (sweep 11-14 notes, DEC-1180 (4); evidence: DEC-1099 (3) is later than DEC-1097 (10) and sets the trigger) · was: WAITS: EXAMIN's copy`

---

## Note 5: row 136 (CIT-P-ONE-BAR)

Finding: confirmed, no progress after `56580afc6` (2026-11-11 15:32, "CIT-P-ONE-BAR draft and its round-1 review (READY WITH FIXES, FX1-FX9)").
- Files named one-bar: `.gov-runtime/scratch/orchestrator/drafts/citp-one-bar/CIT-P-ONE-BAR.md` (mtime 11-11 15:19:35, 52,284 bytes, `cmp` byte-identical to the committed `governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md`); `.gov-runtime/scratch/orchestrator/reviews/CIT-P-ONE-BAR-review.md` (11-11 15:31, 23,831 bytes, the committed review's size); `briefs/LIFT-citp-one-bar.md` (11-11 15:11); `drafts/citp-one-bar/tmp/` is empty. None is newer than 11-11 15:32.
- `git log 56580afc6..HEAD -- packages/CIT-P-ONE-BAR*` is empty. Later commits that mention DEC-1131/FX: `6fbe73b1a` (ACT-OPERATOR-ROUNDS-1 applied 11-11 17:41, already in the row), `75a5af14b`/`6ba5a6eda` (W2-170 uses the rule, not the CIT-P), `433b34f8c` (DEC-1133 (4): FX6 = one fix pass per round). `CHECKPOINT.md:524` still lists "the CIT-P fixes FX1-FX9 ... round 2".
- Verdict stays IN PROGRESS: next FX1-FX9 fixes, round-2 review, then the owner.

Proposed edit (one phrase): `(no later commit found)` -> `(no later commit or draft found 11-14: the scratch copy drafts/citp-one-bar/CIT-P-ONE-BAR.md is byte-identical to the committed draft of 56580afc6)`.

---

## Note 6: row 154 and DEC-1149 (4)

Finding. Due by 2026-11-19 (DEC-1149 (4), "the ledger keeps running; the two peak figures (`verification_peak_bytes`, `rebuild_peak_bytes`) are re-measured from it and brought to the owner within the week"; row 177 repeats it): the two peak figures re-measured and brought to the owner. DEC-1149 (4) also asks the CTO to report how many leads the gate admits and what binds first (the cap of five is gone, DEC-1157 (8)).
- Current `~/.gov-os/machine/gate.json`: `working_size_bytes` 805306368 (2026-11-12, DEC-1149 (1)); `verification_peak_bytes` 7582199808 dated 2026-10-29 (DEC-947 item 1); `rebuild_peak_bytes` 7582199808 dated 2026-11-01, source "not yet measured; the verification peak until the re-measure". The product's gate reads only `working_size_bytes` and the floor; the peaks are read by `gate_check.py`, `gov resources --json` and the owner.
- Tool: ACT-P95-1's own `.gov-runtime/scratch/orchestrator/drafts/act-p95/tools/p95_remeasure.py` (`figures` read-only; `build --out DIR --since ISO`; `manifest`; `verify`), by the ACT route (class (b), `~/.gov-os/machine/**`: independent review, the owner's `yes <ACT> <sha8>`, the CTO applies). The product's `gov resources --remeasure` (`src/gov/resources/measure.py:109`, unchanged since 11-09) still writes the maximum, not the p95; DEC-1133 (3)'s p95 is met only through ACT-P95-1's tool.
- Can it run today? Not as a measurement. `p95_remeasure.py figures` (read-only, run 11-14): "2 sample lines, 0 session samples ... verification_peak_bytes: LEFT as it is: 0 verification-run sample(s), fewer than the 3 needed ... rebuild_peak_bytes: same". The live `~/.gov-os/machine/samples.jsonl` holds 2 empty lines from 11-09. No `gov resources --sample` loop is running; the only sampler is `tools/mem_sampler.sh` (pid 31771), which writes the CTO ledger `log/lead-mem.jsonl` (19,471 lines of leads' process-tree KB, with no verification or slot-holder marks, so it cannot give a rebuild figure). The 11-12 working-size figure was taken by hand from that ledger (1,265 samples), not through `samples.jsonl`.
- What it needs: (a) a `gov resources --sample` sampler running across at least 3 verification runs (`kind` test, or the verification lock held) and at least 3 rebuild slot holders (the tool's `--min-peak-samples`), started today by pid (rebuilds are rare; 5 days left; DEC-1180 (4) no deferral); then `p95_remeasure.py build/manifest/verify`, the independent review and the owner's yes; or (b) an owner-approved other source: `lead_mem.py --summary`'s peak per lead (largest about 9.81 GB, DAEO-s9qc), which is a lead's whole tree rather than a run's peak and has no rebuild figure. The choice between (a) and (b) goes to the owner as one package at once.
- Also left on row 154: `.gov-runtime/scratch/orchestrator/dispatch/launch_now.sh` (mtime 2026-11-01) still exists. Commit `5808126c6` is the decision-record commit (DEC-1149, DEC-1150); the applied bundle is `.gov-runtime/scratch/orchestrator/acts/ACT-P95-1/`.

Proposed new leading text (the row stays DONE for the working size; the existing sweep tail follows unchanged):
`DONE for the working size: ACT-P95-1 applied (5808126c6dfa, DEC-1149); the manual cap max_leads removed by DEC-1157 (8). Left: the two peaks (verification_peak_bytes 7582199808 of 10-29, rebuild_peak_bytes "not yet measured" of 11-01) re-measured and brought to the owner by 2026-11-19 (DEC-1149 (4); row 177): needs gov resources --sample over 3 or more verification runs and 3 or more rebuild holders, then p95_remeasure.py build, review and the owner's yes, since the live samples file has 0 session samples and measure.py:109 still writes the maximum; and remove stale scratch dispatch/launch_now.sh`

---

## Note 7: rows 85 and 166

Row 85 ("past 80 % of the week's usage before the lift, only the lift's critical path runs"): the sweep's wording is right: `SUPERSEDED by DEC-1149 (3) and DEC-1157 (11)`. DEC-1149 (3): "Usage never stops leads ... no lead or worker is held, refused or stopped because of usage or spend"; DEC-1157 (11): "The usage stop stays removed (DEC-1149 (3))"; DEC-1126 (2): "Usage rule (A) ends at the lift (DEC-1122 (2) ended)" (the row's "usage (A) ended by DEC-1126 (2)"); DEC-1164 (22) marks DEC-847's usage limit changed by DEC-1149 (3) and DEC-1122 (2) ended by DEC-1126 (2). Keep as is.

Row 166 (DEC-1140 (5)-(6): five leads this week; 97 % stop, 99 % push): the sweep's wording is too wide. Item numbers: DEC-1140 (5)'s five leads -> `DEC-1157 (8)` (lead cap removed; DEC-1157's header "Changes: DEC-1140 (2), (5)"); DEC-1140 (6)'s 97 % stop -> `DEC-1149 (3)` (report only; restated by DEC-1157 (11)). But DEC-1140's own status line says "item (6)'s 97 % line changed by DEC-1149 (3) (report only; the 99 % push stays, report only)" and DEC-1149 (3) says "the 99 % push to the owner stays, as a report only". `usage_lines.sh` still prints the 99 line ("push the owner (report only, no stop; DEC-1149 (3))") and `usage_log.sh` runs (pid 3309492). So the 99 % half is not superseded and the row's "re-arm each session" half is live as a report. (DEC-1164 (1) B5 already names DEC-1157 (2), (8) for the DEC-866 marks of DEC-1140 (2), (5); nothing more to mark.)

Proposed new leading text, row 166 (replaces the sweep's span `SUPERSEDED by DEC-1157 (8) (lead cap removed) and DEC-1149 (3) / DEC-1157 (11) (usage never stops a lead)`; the sweep tail stays):
`SUPERSEDED by DEC-1157 (8) (the lead cap) and DEC-1149 (3) (the 97 % stop; usage never stops a lead, DEC-1157 (11)), except the 99 % push to the owner, which stays as a report only (DEC-1149 (3)): re-arm the 99 line each session`

---

## Python triples (row, old leading text, new leading text)

Apply: find the line starting `| {n} |`, assert `old` occurs once in it, replace it by `new`. Rows 154 and 166 already carry the sweep's own "(sweep ...) · was: ..." tail, so their `new` has none; row 85 needs no change.

```python
SW = "sweep 11-14 notes, DEC-1180 (4)"
TRIPLES = [
 (122,
  "NOT STARTED: after the lift, an engineer round under W2-141's follow-up or W2-42a",
  "NOT STARTED, trigger met (the lift: DEC-1158; the re-pin 8f00bb90810b): an engineer round, a reopening of W2-42a (reads.py is in its allowed_paths) or a ticket from the owner; W2-42a's closes 77220f814 did not touch reads.py "
  f"({SW}; evidence: reads.py:1721-1725 still resolves each revision word with ^{{commit}}; W2-42a's commits 9196ce961, df7468015, 885b0d0f6, 07fb14799, 1388fcec6, fa77bb331, 669d87c91, f16075e43 change bash_writes.py and decide.py only) "
  "· was: NOT STARTED: after the lift"),
 (123,
  "NOT STARTED: after the lift, a guard ticket (W2-42a holds the parser) and a wider harvest filter; `guard_refusals.py` by hand at the next quiet hour",
  "NOT STARTED, trigger met (the lift: DEC-1158; DEC-1128 (3) fixes the error path first after it; DEC-1133 (2): each by ACT): a guard fix with a replay of the 15 logged calls and a wider harvest filter, by ACT; guard_refusals.py by hand at the next quiet hour "
  f"({SW}; evidence: no IndexError case under src/gov/guard or tests/unit/guard; reads.py:1721-1725; no ticket or ACT package; W2-42a closed 77220f814 without the error path) "
  "· was: NOT STARTED: after the lift, a guard ticket (W2-42a holds the parser) and a wider harvest filter"),
 (125,
  "NOT STARTED: after the re-pin, a small engineer round, then a probe; the next pin carries it",
  "DONE f48697a0e (W2-05, 11-11 19:35; merged and closed 7a809e63b); live at the next re-pin (none since 8f00bb90810b) "
  f"({SW}; evidence: role_paths.py:39 and :61-65; probe record 52de591b8; ticket DAEO-0z8c closed) "
  "· was: NOT STARTED: after the re-pin, a small engineer round, then a probe; the next pin carries it"),
 (137,
  "NOT STARTED: with row 135's helper",
  "NOT STARTED, trigger met (row 135 DONE 11-11): the list S1-S20 exists (packages/SWITCHED-OFF-1.md §5, \"Lists only; nothing edited\") and its edits are not made; next: apply S1, S5-S8, S10-S16 (marks, re-words, W3-P30 retired), the owner's S14 and S18, then a closing re-grep of tickets, rows, packages and briefs "
  f"({SW}; evidence: WAVE_3_PARKING.md:36, DECISIONS-IN-FORCE.md:456, P1-PLAN.md:191, ACT-INDEP-WALLS-1.md:103/204, W2-56-CIT-E.md:29/214, DAEO-wnnz.md:33/44/115/118/145 and DND row 66 all still say set-up B is Wave 3; DEC-769 and DEC-1099 carry no DEC-1128 (4) mark) "
  "· was: NOT STARTED: with row 135's helper"),
 (4,
  "NOT STARTED: the lift is recorded (DEC-1158); next: the G1 option and the 138 re-measure (see row 34: still WAITS: EXAMIN's copy)",
  "SUPERSEDED by row 34 (DEC-1099 (3), 11-09, deferred G1's fewer scored pairs from the lift to after EXAMIN's copy; DEC-1097 (10)'s \"138 re-measured if adopted\" goes with it) "
  f"({SW}; evidence: docs/DECISION_REGISTER.md:13884-13885 and :13952-13953; EXAMIN's copy not yet started, DEC-1180 (3)) "
  "· was: NOT STARTED: the lift is recorded (DEC-1158); next: the G1 option and the 138 re-measure (see row 34: still WAITS: EXAMIN's copy)"),
 (34,
  "WAITS: EXAMIN's copy",
  "WAITS: EXAMIN's copy (the EXAMIN CTO starts tonight, DEC-1180 (3)); then the G1 option to the owner, the 138 re-measured if adopted (DEC-1097 (10), folded from row 4) "
  f"({SW}; evidence: DEC-1099 (3) is later than DEC-1097 (10) and sets the trigger) "
  "· was: WAITS: EXAMIN's copy"),
 (136,
  "(no later commit found)",
  "(no later commit or draft found 11-14: the scratch copy drafts/citp-one-bar/CIT-P-ONE-BAR.md is byte-identical to the committed draft of 56580afc6)"),
 (154,
  "DONE: ACT-P95-1 applied (`5808126c6dfa`, DEC-1149); the manual cap `max_leads` removed by DEC-1157 (8). Left: remove stale scratch `dispatch/launch_now.sh`",
  "DONE for the working size: ACT-P95-1 applied (`5808126c6dfa`, DEC-1149); the manual cap `max_leads` removed by DEC-1157 (8). Left: the two peaks (verification_peak_bytes 7582199808 of 10-29, rebuild_peak_bytes \"not yet measured\" of 11-01) re-measured and brought to the owner by 2026-11-19 (DEC-1149 (4); row 177): needs gov resources --sample over 3 or more verification runs and 3 or more rebuild holders, then p95_remeasure.py build, review and the owner's yes, since the live samples file has 0 session samples and measure.py:109 still writes the maximum; and remove stale scratch `dispatch/launch_now.sh`"),
 (166,
  "SUPERSEDED by DEC-1157 (8) (lead cap removed) and DEC-1149 (3) / DEC-1157 (11) (usage never stops a lead)",
  "SUPERSEDED by DEC-1157 (8) (the lead cap) and DEC-1149 (3) (the 97 % stop; usage never stops a lead, DEC-1157 (11)), except the 99 % push to the owner, which stays as a report only (DEC-1149 (3)): re-arm the 99 line each session"),
 # row 85: no change; "SUPERSEDED by DEC-1149 (3) and DEC-1157 (11)" is confirmed.
]
# for n, old, new in TRIPLES:
#     line = next(l for l in lines if l.startswith(f"| {n} |"))
#     assert line.count(old) == 1, n
#     lines[lines.index(line)] = line.replace(old, new, 1)
```

Caution for row 154's old string: the file's text is the sweep's output; if a quote or backtick differs, match on the shorter span `DONE: ACT-P95-1 applied` and `Left: remove stale scratch` instead.
