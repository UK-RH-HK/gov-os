task: DAEO-wi46 (W2-98). Narrow independent check of the P-W2-98-R2 (a) fix batch at head `f0259229e2b5eb386e8786588a1720ae7cd4b833`.
status: done. Verdict PASS. Every round 2 reproduction of F1–F3 is now refused, and C1–C3 hold as classes. Nothing from round 1 broke. The four findings are all rows; none fails the check.
work_completed: I ran Step 0 and read the diff `c530a0a1a236..f0259229e` for the kernel skill, both `.rulesync` copies and `tests/acceptance/W2-98`. I read `behaviours-r2.md`, `rv-2.return.md`, the probe record's Round 2 table, the whole of `check_spec.py`, `test_w2_98_review_r2.py` and the README map. I re-ran all 29 round 2 reproductions and probed about 230 more inputs: near variants of C1–C3, ordinary specs, and B1–B6 spot checks. I ran `diff -r` on both copies, ran the validator, and ran the suite once through the heavy slot.
files_changed: none. `git status --porcelain` is empty, and `--ignored` on the skill folder is empty too, so no `__pycache__` was written.
evidence: Every probe imported `check_spec.py` in memory after `sys.dont_write_bytecode = True`, under `python3 -B` and `PYTHONDONTWRITEBYTECODE=1`. It called `check_spec()` with a stand-in path object that holds the text and writes nothing. This is the function `main` calls, so the exit codes are the CLI's. I also called `is_placeholder`, `plain`, `KPI_ID_LINE` and `NO_LICENCE` directly to cover the variant classes. Outputs are quoted below.
tests: 2 failed, 500 passed in 14.05s, exactly as expected. The two reds are `test_the_claude_copy_matches_the_kernel_source` and `test_the_adapter_check_finds_no_generated_drift_in_the_real_skill`, because `.claude/skills/spec-writing/` is absent until the copies ACT (DEC-315, DEC-1112 (3)).
discoveries: (1) Two calls were refused once each by the quiet-hours rule (DEC-991) and queued for the 09:00 morning package; I retried neither. The first was the Write tool for a probe script at `$TMPDIR/nc/probe.py`, so I probed in memory as the brief allows. The second was a Monitor call to wait on the suite; I used a background Bash wait instead. (2) The heavy slot printed `rm: cannot remove '/tmp/gov-os-heavy-prio-…': Read-only file system` lines while it waited for a slot (12 in all). The suite still ran normally once a slot opened.
risks: An honest writer can still pass a spec with the four row findings below, chiefly a licence cell that says `licence not found` (N1) or a deferral with extra words such as `TBC by Friday` (N2). Both fall outside the stated class.
lessons: The in-memory probe with `dont_write_bytecode` left no trace in the worktree, so it is safe to brief for later checks.
proposed_decisions: none.
unresolved: the two quiet-hours refusals above (Write in `$TMPDIR`, Monitor), queued for the morning package.
recommended_next_action: The lead lands the fix on this check, records N1–N4 as rows (Wave 3 candidates), and lists the two queued refusals in the morning package.

```verdict
verdict: PASS
head: f0259229e
findings: 4 (failing: none)
```

Classification: 0 findings block. 4 are recorded rows: N1 and N2 are outside the stated class (ordinary work yes, fails open, out of the fix's scope); N3 is ordinary work no (fails open); N4 is other (fails closed).

## 1. Round 2 reproductions at f0259229e: all 29 refused, exit 1, no PASS
- **F1, failure text** (`- K2: A member sees the page.` / `  Fails if: <t>`): `TBD`, `-`, `—`, `n/a`, `?`, `TODO`, `none`, `(none)`, `**TBD**`, `to be written`. Each gives `REFUSED KPIs: K2 has no Fails if: line`, exit 1.
- **F1, behaviour:** `- K2: TBD` and `- K2:` (empty) each give `REFUSED KPIs: K2 has no behaviour`, exit 1.
- **F2, unbulleted id lines** (after a clean K1): each gives `REFUSED KPIs: line "<line>" starts with a KPI id but is not a list item (- K<n>: <behaviour>)`, exit 1.
  - The lines: `K2: The member sees the page.` (directly below, and after a blank line), `**K2:** The member sees the page.`, `  K2: The member sees the page.`, `K2. The member sees the page.`.
  - `K2: send_welcome() runs.` gives the same quoted line and is no longer named under K1.
- **F3, owner cells:** `TBC`, `Tbd.`, `N/A.`, `NA`, `nobody`, `to be decided`, `` `TBD` ``, `...`, `<owner>`. Each gives `REFUSED Test data: public repositories has no owner`, exit 1.
- **F3, licence cells:** `unlicensed` and `none found` each give `REFUSED Test data: public repositories has no licence`, exit 1.

## 2. C1–C3 held as a class
The code matches the stated class: one `plain()` step (lower case, spaces folded, then `*`, `_`, backticks, `()[]{}` and trailing `.,;:!?` peeled however they nest). Then one `is_placeholder()` test checks for:
- no letter or digit;
- a lone `<…>` slot;
- a deferral (TBD, TBC, TBA, TODO, pending, unknown), or the whole text being `to be <word>`;
- an absence word alone (none, nobody, no one, n/a, na, nil, null).

The same test serves the behaviour, the `Fails if:` text and the owner, source and licence-or-recipe cells. Its word sets are the class's words, not the test file's planted text.

**Variants not in the tests, all caught** (each gave `is_placeholder` = True, and spot checks gave exit 1):
- Case and punctuation: `Tbd`, `tBc`, `TBA!`, `ToDo:`, `PENDING.`, `Unknown?`, `TBD...`, `TBD!!`, `TBD?`, `TBD;`, `TBD:`.
- Emphasis: `_TBD_`, `__TBD__`, `*TBD*`, `***TBD***`, ``` ``TBD`` ```, `**TBD**:`.
- Brackets: `[TBD]`, `{TBD}`, `((TBD))`, `**(TBD).**`, `( TBD )`, `(n/a)`, `[none]`.
- `to be` phrases: `To Be Confirmed`, `to be determined.`, `**to be decided**`, `to be filled-in`, `to  be  written`, `To be agreed`.
- Slots: `<fails>`, `<>`, `< >`, `<the failure>`, `` `<behaviour>` ``, `(<owner>)`, `<data owner>`, `<owner>.`.
- Absence words and symbols: `NIL`, `Null`, `No One`, `nobody.`, `none.`, `…`, `--`, `* * *`, a non-breaking space around `TBD`.
- Failure text on the next indented line, after a bold `**Fails if:**`, after a bulleted `- Fails if:`, and with the label in upper case (`FAILS IF:`).
- The same forms in source, licence (imported) and recipe (synthetic) cells; recipe `TBC`, `not found` and `unlicensed` give `… has no recipe`.

**"No licence found" forms, all refused:** `Unlicensed.`, `UNLICENCED`, `un-licensed`, `**none found**`, `Not found.`, `No Licence`, `no license found`, `(no licence)`, `no licence found.`.

**C2, all refused** (each quoted, exit 1):
- `K12:`, `K2 -`, `K2 —`, indented four spaces, a tab, `_K2_:`, `__K2__:`, `*K2:*`, `***K2:***`, `**K2**:`, `**K2** The member…`, `_K2: x_`.
- `K2)`, `K2 (new):`, `K02:`, `K2_:`, `K2:` alone, `K2` alone.
- A loose line between K1 and its `Fails if:`, and one as the last line of the part.

Where variants fail open, they sit outside the stated class: see N1–N3.

## 3. What the fix may have broken: nothing in scope
- **Ordinary owners pass:** `Data team`, `NASA data office`, `Nadia (QA)`, `None Ltd`, `Nobody Inc`, `Na Li`, `Nil Patel`, `Tom (to be confirmed)`, `TBA Analytics`.
- **Ordinary licences pass:** `MIT`, `CC-BY-4.0`, `Apache-2.0`, `Unlicense`, `The Unlicense`, `licence found in LICENSE file`.
- **Sentences with a placeholder word pass, as failure text:** `the member sees none of the page.`, `no page is shown.`, `TBD or the form shows again.`, `nobody sees the page.`, `the status stays pending.`, `No one sees the page.`.
- **The same holds for behaviours:** `Nobody sees an error after sign-up.`, `Pending members see a notice.`, `N/A is never shown as a plan name.`, `To be useful, the page loads in a second.`.
- **Continuation lines starting with K pass:** `Kiosk members see it too.`, `K2nd place…`, `Keys are shown.`, `K-means…`, `K8s clusters…`.
- **Prose before the first KPI passes:** `Key results follow.`.
- **`privacy` and `secrets`:** `none`, `None.`, `TBD` and `n/a` pass; an empty cell is still refused (`… has no privacy` / `… has no secrets`).
- **B1:** `- K2 :`, `2. K2:`, `- K2a:`, `- K2 (new):` and `- **K2** —` are refused, quoted.
- **B2:** a column-0 wrap with code gives `K2 names code (name( call "send_welcome(")`; no `Fails if:` gives `K2 has no Fails if: line`; code in a failure continuation gives `K2 names code in its Fails if: line`.
- **B3 and B4:** empty privacy is refused. An empty owner, `none`, source `-`, licence `unknown` and recipe `n/a` are refused with B4's words.
- **B6:** `**Fails if:**` with its text on the next line, `_Fails if:_` and `- Fails if:` pass.
- **Other forms:** a bold `- **K2:**` passes. `secured: no` gives a P1 line and exit 2; with an owner of `TBC` too, it gives the REFUSED line, the P1 line and exit 1. A placeholder behaviour with a code-naming failure text gives both lines.
- **A small extension:** `plain()` also peels a trailing `?`, which behaviours-r2 does not list (spec-form.md does). It only widens the class, so it is harmless.

## 4. The tests
- `test_w2_98_review_r2.py` holds 236 cases: C1 has 25 placeholders × behaviour and failure text, plus three positions and the next-line and emphasised-label forms. C2 has 7 line shapes, plus last-line, between-lines and not-read-under-K1 cases. C3 has 22 placeholders × 4 cells, plus 6 no-licence words × 2 cells.
- Each group has clean controls: placeholder words inside sentences, real owners, licences and recipes, `privacy`/`secrets` unchanged, `Kiosk`/`K2nd` continuations and prose before the first KPI.
- The commits only add `test_w2_98_review_r2.py` and README text; no existing case changed. The README records 186 of 236 red at the old head.
- The code passes them honestly: there is no special case for the planted text, and the unplanted variants in section 2 behave the same way.

## Findings (all rows)

**N1 (row): Licence-cell wordings outside the six listed forms pass** (`check_spec.py:44`)
- **Done:** an imported row's licence cell set to `licence not found`, `license unknown`, `not licensed`, `no licence stated`, `no licence yet`, `no licence file`, `unlicensed (assumed)` or `none known`. Each passes (`NO_LICENCE` and `is_placeholder` both false).
- **Should happen** (if extended): any cell whose whole text says no licence was found is refused as `<source> has no licence`.
- Scope: out. C3 and spec-form.md list exactly six forms, and the code holds each of them with case, emphasis, punctuation and hyphen variants.
- Ordinary work: yes, because `licence not found` is a natural word order for the same fact.
- Consequence: fails open.
- **Would reverse it:** an owner ruling that C3's "says no licence was found" is a class rather than a closed list. Then N1 fails the check.

**N2 (row): A placeholder with extra words, quotes or a second placeholder passes** (`check_spec.py:47-61`)
- **Done:** owner or failure text set to `TBC by Friday`, `to be decided later`, `none yet`, `nobody yet`, `TBD (later)`, `TBD — later`, `TBD TBD`, or `Fails if: TBD` with `TODO` on the next line. The same for `"TBD"`, `'TBD'`, `“TBD”`, `~~TBD~~`, `T.B.D.`, `n.a.`, `to-be-decided`, `<<owner>>`, `<owner> <team>`. Each passes.
- **Should happen:** the lead decides whether a deferral followed by a date or a note, quotes and strikethrough join the class.
- Scope: out. The class is matched against the whole text, never a word in a sentence, and its peel list names no quotes or strikethrough.
- Ordinary work: yes for `TBC by Friday` and `to be decided later`; no for the quoted, strikethrough and dotted forms.
- Consequence: fails open.
- **Would reverse it:** a ruling that a leading deferral word makes the whole text a placeholder.

**N3 (row): KPI id lines outside C2's stated shapes are not refused** (`check_spec.py:37`)
- **Done:** after a clean K1, a heading `### K2: The member sees the plan.` or a blockquote `> K2: …`, with no `Fails if:` line. Each passes; so do `k2: …` and `K 2: …`. A backticked `` `K2`: … `` line is refused, but under K1 (`K1 names code in its Fails if: line (code span)`).
- **Should happen:** a line that starts with a heading or quote marker and then a KPI id is refused, quoted, like C2's shapes.
- Ordinary work: no. The form shows `- K<n>:`, and one heading or quoted KPI amid list KPIs is rare. A part written wholly as headings is refused (`no K<n> line`).
- Consequence: fails open.
- **Would reverse it:** specs in ordinary use that write KPIs as `### K<n>:` headings.

**N4 (row): A few ordinary texts are now refused (fails closed)**
- **Done:** a continuation or prose line `K12 students see it too.` or `K9 teams are the users.` is refused as a KPI-id line, which is C2's stated rule (a digit, then a non-word character). An owner of just `Na` or `Nil` (real given names) is refused as an absence word.
- **Should happen:** the writer rewords; the refusal quotes the line or names the cell.
- Ordinary work: yes, but rare.
- Consequence: other (fails closed).

## Suite
`2 failed, 500 passed in 14.05s`. The run waited for a heavy slot from 02:14:48 ("all 3 slots taken"). The reds:
- `test_w2_98_copies.py::test_the_claude_copy_matches_the_kernel_source`: `.claude/skills/spec-writing does not exist`
- `test_w2_98_copies.py::test_the_adapter_check_finds_no_generated_drift_in_the_real_skill`: four `GENERATED_DIFFERS` for `.claude/skills/spec-writing/{SKILL.md, check_spec.py, imports.yaml, spec-form.md}`

## Step 0
- (a) `OSError: [Errno 30] Read-only file system: '/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-wi46'`, exit 1: it failed, as required.
- (b) HEAD is `f0259229e2b5eb386e8786588a1720ae7cd4b833`; `GOV_ROLE` is `independent-auditor`; `GOV_TICKET` is `DAEO-wi46`.
- `gov.__file__` is `/home/usain/gov-os-worktrees/W2-98/src/gov/__init__.py`.
- At the end, `git status --porcelain` is empty, and `--ignored` on the skill folder is empty.

## Validator and copies
- `diff -r template/governance/kernel/skills/spec-writing .rulesync/skills/spec-writing`: no output, exit 0.
- `diff -r template/governance/kernel/skills/spec-writing template/.rulesync/skills/spec-writing`: no output, exit 0.
- `python3 -m gov.check.skill_validator template/governance/kernel/skills/spec-writing/SKILL.md` printed `{"findings": []}`, exit 0.","ttft_ms":2887,"type":"result","duration_ms":62510,"uuid":"f4e25fdb-547d-47e6-9b43-2c18e6d28352","ttft_stream_ms":1370,"time_to_request_ms":23,"first_content_frame_ms":1370,"queued_turn_count":0,"result_index":1,"credential_expires_at":"2026-12-03T12:44:06.296Z"}
