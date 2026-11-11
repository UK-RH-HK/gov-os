# D-10's red-fix list: the review of the plan validator, round 2 (W2-139, DAEO-ongl)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-validator-review-r2.md`; branch `w2/W2-139-d10` at `c57955a96`; reviewer log `/home/usain/gov-os-worktrees/W2-139-d10/.gov-runtime/scratch/lead/log/D10-validator-review-r2.json`.
- verdict.py: READY (no blocking finding; F1 a row: not ordinary work).

# D-10's red-fix list: review of the plan validator, round 2 (W2-139, DAEO-ongl)

**Sandbox check (Step 0, launch_worker.sh):**
- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-W2-139','w').write('x')"` was refused with `OSError: [Errno 30] Read-only file system`. That is the required result.
- (b) `echo sandbox-trial | git hash-object -w --stdin` gave `1ae28402a109c3397a44b19239a00adfa9472eb0`, the same object as in round 1. `git update-index --refresh` exited 0. Both worked.

**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing, at the start and again before return. The sandbox's process list held only my own shell.

**task:** W2-139 (DAEO-ongl), D-10's red-fix list. An independent, read-only round-2 review of `c57955a96` on `w2/W2-139-d10`.

**status:** DONE. Per KPI:
- `validator-wbs-ids`: **pass**, with one row (F1: ordinary work no).
- `validator-cap-pattern`: **pass**.
- My block holds no blocking finding; `verdict.py` computes READY from it.

**work_completed:**
- Read the brief, EMG-d4b, EMG-common, JUDGEMENT and round 1's record, plus the commit, the whole validator, its unit file, DEC-730 and `common.schema.json`.
- Loaded round 1's validator (`c57955a96^`) and this one from source, in memory, and ran every check of both on the same records.
- Analysed every ticket's id, §1's table, §2's headings and the triage column.
- Probed the four reads with 12 id forms.
- Checked that each of the 23 new cards points at the right ticket file.
- Reproduced the worker's validator run and ran two pytest runs through the heavy slot.

**files_changed:** None tracked; `git status --short` is clean. Writes, named:
1. The Step 0 blob, which already existed, and the index refresh.
2. A scratch folder in my own TMPDIR (24K, 6 inodes), now removed.
- No bytecode: every run set `PYTHONDONTWRITEBYTECODE=1`. The newest `.pyc` in either folder is from 00:47:25Z, the worker's run a minute after its commit.
- A refusal I worked round: the Write tool was refused for a script file in my TMPDIR folder. I did not retry it. Instead I ran inline `python3 -c` programs that write nothing.

**evidence:**
- All outputs are quoted in the checks below.
- Scratch before removal: `du -sh` 24K, `du -s --inodes` 6.

**tests:**
- `tests/unit/plan`: **75 passed**, 0 deselected.
- `tests/acceptance/W2-51` together with `tests/acceptance/W2-49/test_w2_49_validator_lines.py`, with `--optin=lifted,breadth`: **59 passed**, 0 deselected. That equals the worker's 47 + 12; I ran the two together, not apart.
- Both runs used `-m "not local_only" -k "not real and not green_here and not time_limit"`, which left out nothing.

**discoveries:**
- DEC-730's `wbs_id` grammar takes two or more digits (`^W[0-9]+-[0-9]{2,}[a-z]?$`, `common.schema.json:14`). The validator now takes two or three (F1).
- The project's other W2 reader, `src/gov/retrieval/graph_route.py:31`, takes any number of digits (`W2-[0-9]+[a-z]?`).
- The numbers W2-89, W2-132, W2-143 and W2-144 are unused: no ticket mentions them, and no row or card exists for them.
- Four repair tickets name W2 test paths in their titles but carry no `wbs_id` (DAEO-cv6c, pr0y, s1wp, sg6x). They are not Wave 2 tickets, and that is unchanged.
- The new `CAP-1 (W2-134)` FAIL comes from KPI prose at `.tickets/DAEO-m4rq.md:29` ("CAP-1 never matches CAP-10").

**risks:**
- The validator is still red, with 3 FAIL: the two old record FAILs, plus `CAP-1 (W2-134)` from the wider coverage.
- The `wave2-tickets` PASS is honest. F1's gap opens only past W2-999, or if the same typo is copied into both a ticket and the WBS.

**lessons:**
- Check a reader's id width against the governing grammar (DEC-730, the schema), not only against today's records. The records showed no four-digit id; the schema shows the cap.
- Loading the module source with `exec` instead of importing it compares two versions without writing bytecode.

**proposed_decisions:**
- Classification: F1 in/no/fails open (row).
- Recommendation: ride along in W2-139's next resume (DEC-802), or the Wave 3 pass, about 10 minutes:
  - widen `W2_ID_RE` to `W2-[0-9]{2,}[a-z]?`, so all four reads follow DEC-730;
  - change case 4's four-digit assertion so the id is read;
  - name in one decision line the departure from W2-51's R1.
- Confidence: high.

**unresolved:**
- No decision yet names the departure from R1 (`tests/acceptance/W2-51/README.md:72`, `^W2-[0-9]{2}[a-z]?$`). A grep of both registers for "three-digit", "three digits" and `{2,3}` finds nothing.
- `CAP-1 (W2-134)` is the CTO's to settle: reword the example at `DAEO-m4rq.md:29`, or accept the FAIL.

**recommended_next_action:** The CTO runs `verdict.py` on the block below, records F1 as a row, and settles `CAP-1 (W2-134)`.

---

## Answers to the checks

**1. F1 is closed, and the PASS line is honest.**
- **Tickets:**
  - 217 ticket files: 160 W2, 51 W1 and 6 with no id.
  - 51 W2 tickets are newly read: W2-100 to W2-153, less the unused 132, 143 and 144.
  - No `wbs_id` or `external-ref` value containing "W2" escapes the pattern.
  - There are no duplicate ids, and `wbs_id` and `external-ref` never disagree.
- **§1:**
  - One table, with 106 rows read: 95 plain and 11 bold. 28 of them are new (W2-100 to W2-127).
  - No table line whose first cell names a W2 id goes unread, and no rows are struck through, indented or duplicated.
- **§2:**
  - 120 headings name a W2 id, and 117 are read as cards: 94 with two digits and 23 with three.
  - None is duplicated, none sits in a fence (§2 has no fences), none is at another heading level, and no three-digit heading lies outside §2.
  - The three headings not read are the same non-cards as in round 1: `#### Split: W2-60`, `#### W2-81's held-out half` and `### DEC-951: W2-54's…`.
  - All 23 three-digit cards point (**Ticket file:**) at the ticket file that carries their own id.
- **Triage column:** 798 open rows, and none changes column. All 541 W2 dispositions have two digits, and `triage-counts` is unchanged.
- **Probe of the four reads (tickets, plain row, bold row, card):**
  - Read on every side: `W2-07`, `W2-15a`, `W2-139`, `W2-128a`, `W2-999` and `W2-015`.
  - Read on no side: `W2-128ab`, `W2-128A` and `W2-1`. DEC-730's grammar refuses them too.
  - Also read on no side: `W2-1000`, `W2-1270` and `W2-1390`. DEC-730's grammar accepts these → F1.
  - There is no prefix read: `W2-1390` never reads as `W2-139`. The sides therefore always agree, and never mismatch.
  - `#### W2-139: x` and `#### **W2-139** x` are not read as cards, so they fail closed.
- **The PASS line:**
  - The CLI output is exactly the worker's line: `PASS wave2-tickets — 160 W2 ids agree between the WBS (106 in the §1 table, 54 in §2's cards only) and .tickets/`, then `RESULT: 3 FAIL, 5 NOT RUN`, exit 1.
  - The WBS id set equals the ticket id set; 63 ids are in both the table and a card.
  - Round 1's validator, on the same records, gives 109 (78 + 31).

**2. F4 is closed.**
- `test_validate_w2.py:68` now asserts `reason == "3 W2 ids agree between the WBS (1 in the §1 table, 2 in §2's cards only) and .tickets/"`.
- The three new cases compare `(ok, reason)` by equality.

**3. No regression.**
- The `CAP` and `ROW` patterns are byte-identical to round 1's.
- On the same records only two lines change:
  - `wave2-tickets`: 109 → 160.
  - `ticket-contract-ids-exist`: PASS → `FAIL CAP-1 (W2-134)`.
  - The other six lines are identical: CAP-22.c, the ten uncited items, 3/6 CIT-P, 950 list rows and 798 triage rows.
- The new FAIL comes from coverage, not from the pattern. It is a bare `CAP-1`, which round 1's case 3 pins as reported.
- Round 1's three unit cases pass. Its rows F2 and F3 are untouched: `CAP` and the table-plus-cards union are unchanged.

**4. Trailers and files.**
- **Trailers on `c57955a96`:** `Task: DAEO-ongl`, `Implements: DEC-1109, DEC-1112`, `Role: product-spec`, `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. These are exactly the four that `D10-validator-engineer.md:57-58` requires.
- **Files:** only the two allowed paths (`DAEO-ongl.md:19-20`), +38/−8.
- **The merge `4b4ca0c12`:** it left both files as round 1 reviewed them (the diff `d76e79996..c57955a96^` is empty).

## Findings

Round 2's ids start at F1, as the brief asks. Round 1's F2 and F3 remain recorded rows.

**F1: the W2 id stops at three digits, narrower than DEC-730's grammar, and unit case 4 pins it** (`docs/plan/tools/validate_w2.py:21`; `tests/unit/plan/test_validate_w2.py:89-94`; KPI `validator-wbs-ids`)
- `W2_ID_RE` is `W2-[0-9]{2,3}[a-z]?`. DEC-730 (`DECISION_REGISTER.md:7775-7779`) and `common.schema.json:14` allow two or more digits.
- A schema-valid `W2-1000` is read on no side.
- Case 4 asserts PASS for a `W2-1270` ticket that has no WBS entry ("a four-digit id is not a W2 id").
- Ordinary work: no, because the highest id is W2-153 (160 tickets), so a four-digit id needs about 850 more tickets in this wave; and a ticket with an extra digit typed by mistake is still caught on the WBS side, unless the same typo is copied into its card or row.
- Consequence: fails open
- Scope: in. This revision chose the three-digit limit and pinned it in a test.
- Fix: `{2,}` at line 21, which all four reads share, and case 4 changed to read the id; it rides along with the next resume.

```verdict
{"kpis": [{"kpi": "validator-wbs-ids", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "validator-cap-pattern", "verdict": "pass", "findings": []}]}
```
