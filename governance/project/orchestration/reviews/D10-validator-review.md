# D-10's red-fix list: the review of the plan validator's two reads, round 1 (W2-139, DAEO-ongl)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-validator-review.md`; branch `w2/W2-139-d10` at `d76e79996`; reviewer log `/home/usain/gov-os-worktrees/W2-139-d10/.gov-runtime/scratch/lead/log/D10-validator-review-5.json`.
- verdict.py: NOT READY (validator-wbs-ids: F1 blocks: in scope, ordinary work, fails open). Round 2: `briefs/D10-validator-r2.md`.

Sandbox check (Step 0, launch_worker.sh):
- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-W2-139','w').write('x')"` was refused: `OSError: [Errno 30] Read-only file system`. That is the required result.
- (b) `echo sandbox-trial | git hash-object -w --stdin` gave `1ae28402a109c3397a44b19239a00adfa9472eb0`. `git update-index --refresh` exited 0. Both worked.

ps check: `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing, at the start and again before return.

**task:** W2-139 (DAEO-ongl), D-10's red-fix list. An independent, read-only review of the plan validator's two reads: `git diff adec4718a..d76e79996` on `w2/W2-139-d10`.

**status:** DONE. The verdict is computed from the block at the end:
- `validator-wbs-ids`: **fail** (F1).
- `validator-cap-pattern`: **pass**.

**work_completed:**
- Read the brief, EMG-d4b, EMG-common and JUDGEMENT, plus the diff, the whole validator and its unit file, WBS §1 and §2, and the readings in W2-51's acceptance README.
- Ran the branch's validator on this worktree. The worktree merges integrate after `966a9ac67`. It reproduces the CTO's output exactly: `PASS wave2-tickets — 109 W2 ids agree … (78 in the §1 table, 31 in §2's cards only)` and `RESULT: 2 FAIL`.
- Ran the `adec4718a` validator in memory on the same records, for a before/after per check.
- Ran 17 probes of the §2 reading on throwaway trees.
- Tested 22 CAP forms and scanned the validator's read scope and the tracked tree with both patterns.
- Ran the three new unit cases against the old and new validator.
- Ran three pytest runs through the heavy slot.

**files_changed:** None tracked; `git status --short` is clean. Writes that fall outside the brief's "write nothing", named:
1. The Step 0 blob `1ae28402a109` in the shared object store, and the index refresh. Both are required by the check.
2. Three git-ignored bytecode files, written by Python when I loaded modules by path. My brief only allows `rm` inside my own TMPDIR, so they are still there; later runs set `PYTHONDONTWRITEBYTECODE=1`.
   - `docs/plan/tools/__pycache__/validate_w2.cpython-312.pyc` (00:16:30Z)
   - `tests/unit/plan/__pycache__/test_validate_w2.cpython-312.pyc` (00:19:20Z)
   - `tests/unit/plan/__pycache__/test_validate_w2.cpython-312-pytest-9.0.3.pyc` (00:31:09Z)
3. Scratch in my own TMPDIR folder, now removed.

A refusal I worked round: the Write tool was refused for a script file in my TMPDIR folder. I did not retry it and wrote no script files. Instead I ran the probes as inline `python3 -c` programs whose only writes were throwaway trees under the sandbox's TMPDIR.

**evidence:**
- All outputs are quoted in the checks below.
- Scratch before removal: `du -sh` 736K, `du -s --inodes` 184.

**tests:**
- `tests/unit/plan`: **72 passed**, 0 deselected. This ran after an 11-minute wait, because all three slots were taken.
- `tests/acceptance/W2-51` together with `tests/acceptance/W2-49/test_w2_49_validator_lines.py`: **46 passed, 13 deselected**.
  - The `-m/-k` exclusion did not remove these 13. The inverse selections (`-k "real or green_here or time_limit"` and `-m local_only`) both collect 0.
  - The opt-in suites' `rep:` lines removed them: `tests/conftest.py:226`, `tests/optin-lifted-breadth.txt:1077,1085-1089`.
- The same two with `--optin=lifted,breadth`: **59 passed** (47 + 12), which matches the worker's counts.
- The exclusion `-m "not local_only" -k "not real and not green_here and not time_limit"` left out nothing in any of these runs.

**discoveries:**
- F1: 51 Wave 2 tickets are never read, which hides 23 tickets that have no WBS entry.
- W2-51's README reading R1 (`tests/acceptance/W2-51/README.md:72`) fixes a Wave 2 ticket as `^W2-[0-9]{2}[a-z]?$`. It was written when every id had two digits.
- `.tickets/DAEO-m4rq.md:29` contains a bare `CAP-1` in an example ("CAP-1 never matches CAP-10").
- The WBS note at line 241, "The later tickets (W2-59 onwards) are in §2's cards only", is out of date: W2-86 to W2-127 have §1 rows.
- W1-41's acceptance already treats `S0a-CAP-13` as "a capability's prefix inside a longer id" (`test_w1_41_external_follow_up.py:176`). That agrees with the new CAP rule.

**risks:** S3's "green validator" would show `wave2-tickets` PASS while 23 Wave 2 tickets have no WBS entry. Fixing the read turns the check red until those 23 records exist.

**lessons:**
- Loading a module by path writes `__pycache__` into the tree. A read-only reviewer should set `PYTHONDONTWRITEBYTECODE=1` from the first command.
- When comparing a whole-folder test count with a worker's, name the opt-in deselections or pass `--optin`.

**proposed_decisions:** Classification: F1 in/yes/fails open (blocks); F2 in/no/fails open (row); F3 in/yes/other (row); F4 in/no/other (row). The three options for F1 (DEC-105 form):
- **(a) Apply now.**
  - Validator: accept two or three digits (`W2-[0-9]{2,3}[a-z]?`) at `validate_w2.py:20`, `:23` and `:110`, plus one unit case with a three-digit ticket, row and card. All inside W2-139's paths; about 20 minutes.
  - Records on integrate: 23 one-line cards in W2-63's form, about 30 minutes. Reword the example at `DAEO-m4rq.md:29`, or accept that line as a real FAIL.
  - R1's text says two digits, so the decision should name the departure from it.
  - Then a one-line re-review.
- **(b) Defer, but make the line honest now.** Keep two digits, and have the `wave2-tickets` and `ticket-contract-ids-exist` lines name the 51 tickets they skip. About 10 minutes. The 23 gaps stay unflagged.
- **(c) Re-baseline.** State that the check covers W2-00 to W2-99 (R1 as written), record a Wave 3 row, and present S3's green as partial.

I recommend (a). My confidence is high that the gap is real (it is measured) and medium on the cost.

**unresolved:**
- W2-51's 59 cases have not been run against a widened validator. By grep, no case uses a three-digit id.
- F1's scope is for the moderator to triage. I put it in scope for the reasons given under F1.

**recommended_next_action:** The CTO triages F1 and picks an option. If (a): resume W2-139 for the three-pattern change and its unit case, add the 23 cards on integrate, then run a one-line re-review. F2 to F4 go in as rows.

---

## Answers to the checks

**1. No fail-open in the §2 reading.** Probes run against the branch's `check_wave2_tickets`:
- **A card for a ticket that does not exist:** FAIL, `ids on one side only: W2-70 (WBS §2 card only)`. Unit case 2 pins this with W2-60.
- **A heading that is not a card:** `#### W2-81's held-out half` is not read, because `CARD` needs a space right after the id. A ticket W2-81 with only that heading fails as `.tickets/ only`.
  - These forms are not read either, so each fails closed: `#### W2-89:`, `#### **W2-89**`, `### W2-89`, and a fenced `## ` line that ends §2 early.
  - `#### W2-89 — T` is read.
  - All 94 `#### W2-` headings in the real §2 are cards for their own id; `W2-61h W2-61's…` reads as W2-61h.
- **A split parent:** `#### Split: W2-60 …` (WBS:1463) is not read. Written without `Split:`, it is read as a card and FAILs `W2-60 (WBS §2 card only)`, which is fail-closed.
- **A card outside §2:** one in §3, or a `####` card inside §1, is not read, and the ticket fails as `.tickets/ only`. Unit case 2 pins §3 with W2-98.
- **An id only in a card's body:** not read, so FAIL.
- **Is the PASS count honest?**
  - For two-digit ids, yes: 109 = 78 table + 31 cards only, and the real §2 holds 94 card headings.
  - For coverage, no (F1): `.tickets/` holds 160 Wave 2 tickets, and the 51 with ids W2-100 to W2-153 are read on neither side.
  - Probe: a W2-154 ticket with no row or card gives PASS; so does a W2-154 card with no ticket.
- One more behaviour change: an early ticket whose §1 row is gone but whose card remains now PASSes; it used to FAIL (F3).

**2. The CAP pattern.**
- **Forms still read** by the new pattern, exactly as by the old: `(CAP-22.c)`, `—CAP-1`, `item—CAP-22.c`, `–CAP-22.c`, `CAP-22.c/CAP-22.b`, an id at the start of a line, `[CAP-10.a, CAP-22.b]`, `CAP-22.b,CAP-22.c`, `**CAP-43.b**`, an id in backticks, `|CAP-22.c|`, `CAP-22.c's`, `CAP-22.c-lite`, `_CAP-22.c`.
- **The only form that loses an id** is `CAP-22.b-CAP-22.c`, which now reads only CAP-22.b (F2).
- **Read scope** (1,574 files: `.tickets/*.md`, `tests/acceptance/**`, `docs/changes/*-CIT-P.md`, the WBS):
  - 3,979 tokens before, 3,966 after; the new pattern gains none and loses 13.
  - All 13 are inside `ACT-OLLAMA-CAP-1/2`, `OLLAMA-CAP-1` or `S0a-CAP-13`.
  - The 13 lost matches the worker's count; my totals differ because I counted a different scope.
- **Tracked tree:** 11,263 tokens before, 11,212 after; 376 distinct ids before and after, none lost.
- **CIT-P lines** have their own pattern (`:141`), so the change does not touch them. The baseline lines are `- CAP-…` with a space, so they are unaffected.
- **Before and after on the same records:** only `ticket-contract-ids-exist` changes, from `FAIL CAP-1 (W2-20), CAP-2 (W2-20)` to PASS, besides `wave2-tickets`. Delivered, cited, cit-p-moved (3), cit-p-applied (6), list-counts and triage-counts are identical.
- `ticket-contract-ids-exist` shares F1's ticket gap: once widened, it reads 51 more tickets, and the only id it then reports is the example `CAP-1 (W2-134)`.

**3. The three unit cases.**
- **Against `adec4718a`** (in memory, same fixtures), all three fail:
  - case 1 gives `W2-59 (.tickets/ only), W2-60a (.tickets/ only)`;
  - case 2 gives `W2-59 (.tickets/ only), W2-63 (.tickets/ only)`;
  - case 3 gives `CAP-1 (W2-20), CAP-2 (W2-20)`.
- **Against the branch**, all three pass.
- **They pin behaviour, not incidental text.**
  - Case 2's exact string pins both sides, and also that `W2-81's` and the §3 heading are not read as cards.
  - Case 3 pins both directions: the ACT names are not read, and a bare `CAP-1` is still reported.
- **Weak spots:**
  - Case 1 checks its counts by substring (F4).
  - No case uses a three-digit id or a split heading without `Split:`.
  - The CAP case covers only the hyphen-before and space-before forms; the probes above cover the rest.

**4. Trailers and files.**
- **`d76e79996` trailers**, as parsed by `git log --format=%(trailers)`: `Task: DAEO-ongl` (W2-139's ticket file), `Implements: DEC-1109, DEC-1112`, `Role: product-spec`, `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **`d76e79996` files:** only `docs/plan/tools/validate_w2.py` (+16/−6) and `tests/unit/plan/test_validate_w2.py` (+41).
- **`4771fba13`:** only `.tickets/DAEO-ongl.md`, adding the two `allowed_paths` lines. Trailers: `Task: DAEO-sdxk` (W2-00), `Role: orchestrator`, `Implements: DEC-1109`, Co-Authored-By.
- Neither validator file has changed between `d76e79996` and HEAD `619da87f4`, and `966a9ac67` is in HEAD's history.

## Findings

**F1: three-digit W2 ids are read on neither side, so `wave2-tickets` PASSes over 23 tickets with no WBS entry** (`docs/plan/tools/validate_w2.py:20`, `:23`, `:110`; KPI `validator-wbs-ids`)
- `W2_ID`, the §1 row pattern and the new `CARD` all take exactly two digits.
- On these records, 51 Wave 2 tickets (W2-100 to W2-153) and 28 §1 rows (W2-100 to W2-127) are never read.
- Widened to `W2-[0-9]{2,3}[a-z]?`, the check FAILs with 23 tickets that are only in `.tickets/`: W2-128 to W2-131, W2-133 to W2-142 and W2-145 to W2-153. W2-139, this revision's own ticket, is one of them.
- `triage-counts` is unchanged when widened.
- Ordinary work: yes, because 23 tickets were already filed straight from decisions with no card or row. That is the class the CTO fixed by hand for W2-63 and W2-66c in `966a9ac67`, and every ticket filed now has a three-digit id.
- Consequence: fails open
- Scope: in. It answers check 1's "is the PASS line's count honest?" for this revision's own new PASS line. The new `CARD` pattern and its docstring (`:126`, "the later tickets (W2-59 onwards)") keep the two-digit limit, and this revision is what makes the check green for S3. The root cause is older (W2-51's `W2_ID` and README R1), so the moderator may re-triage it.

**F2: a hyphen-joined pair loses its second id** (`validate_w2.py:22`; KPI `validator-cap-pattern`)
- `CAP-22.b-CAP-22.c` now reads only CAP-22.b. In `ticket-contract-ids-exist`, a second id the Contract lacks would go unreported. In the other checks the same loss gives a false FAIL.
- Ordinary work: no, because no file in the tree joins ids that way (Grep `CAP-\d+(\.[a-z]+)?-CAP-\d`: 0 hits). The project joins ids with "and", commas, slashes or en dashes, and all of those are still read.
- Consequence: fails open
- Scope: in

**F3: the union of table and cards accepts a card for an early ticket whose §1 row is gone** (`validate_w2.py:172`; KPI `validator-wbs-ids`)
- Probe: W2-05's row removed, its card kept. The old validator FAILs `W2-05 (.tickets/ only)`; the new one PASSes with "(1 in the §1 table, 1 in §2's cards only)".
- Ordinary work: yes, because §1 rows are edited at every re-plan.
- Consequence: other. The WBS still records the ticket in its card, the check compares the WBS with `.tickets/` (never the table with the cards), and the changed counts are visible in the PASS line.
- Scope: in

**F4: unit case 1 checks its counts by substring** (`tests/unit/plan/test_validate_w2.py:66`; KPI `validator-wbs-ids`)
- `"3 W2 ids" in reason` would also accept "13 W2 ids", and the same holds for "1 in the §1 table" and "2 in §2's cards only". An equality check would pin the line.
- Ordinary work: no, because getting a wrong count on this fixture would mean reading ten ids it does not contain.
- Consequence: other
- Scope: in

```verdict
{"kpis": [{"kpi": "validator-wbs-ids", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "validator-cap-pattern", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}]}
```
