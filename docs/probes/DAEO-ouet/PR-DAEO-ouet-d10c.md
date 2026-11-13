---
type: probe
task: DAEO-ouet
reviewer_session: e9c9fa7c-01f8-4b6c-869d-4240b15dab08
implementer_session: engineer 60f2b950-13d1-45cc-9e74-a5779e9d016c (dac10e5df, 1df7ccd60); test designers e4afe1cb-576c-4578-b75f-019234786a51 (5e36c7fc5) and e8cf0fc6-da59-4a3d-84c8-c6023ec331df (51f1f547a); round 1's 04b52305a, 3ac8e892f and 88c0772ff by the D-10 engineer and designer
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 8f6e66a17572ff2e192244df7aff19d7c8bd9af9
decisions_applied: DEC-1112 (3), DEC-1061 (2), PKG-D10a-scope (b), DEC-866
---

# Fresh probe of W2-96 (DAEO-ouet) at 8f6e66a17, after D-10's S-D10a/b merge (DEC-1112 (3), PKG-D10a-scope (b))

- **Why fresh:** everything since the last probe (PR-DAEO-ouet-d10b.md, pass at 8b31965edae8): the ticket's S-D10a/b lines (bbe222c59) and the merge 8f6e66a17 of w2/W2-96-d10b at bb71be1cf (review READY in two rounds, reviews/D10-W2-96-accept-review.md).
- **Brief:** .gov-runtime/scratch/orchestrator/briefs/D10-W2-96-probe-r3.md; a fresh, read-only independent reviewer, effort max; verdict.py READY; the orchestrator's judgement: pass.
- **Rows from this probe:** F1 (S-D10a's text predates scope (b); the CTO's ticket amendment or note), F2 (range `S1 -S3` drops lines; with round 2's F1, a Wave 3 row), F3 (W2-87, W1-22 item forms match no case; out of scope, a map fix row).
- **The reviewer's record follows, as returned.**

**Verdict: pass for W2-96 at `8f6e66a17`.** The declared `gov accept W2-96` now passes: exit 0, 190 passed and 0 failed, all 11 mapped lines measured, `"optin": ["breadth"]`. So the last probe's finding (four lines failing with every case passing) no longer holds. I found three findings and none blocks. I wrote nothing in any tree. The full record follows.

---

# Probe record: W2-96 (DAEO-ouet), full probe after D-10's S-D10a/b merge, at `8f6e66a17`

**Sandbox check (Step 0, `EMG-d4b-launched.md`): passed.**
- (a) The write to `/home/usain/gov-os-worktrees/.sandbox-trial-W2-96` failed, as required: `OSError: [Errno 30] Read-only file system`.
- (b) `echo sandbox-trial | git hash-object -w --stdin` returned `1ae28402a109c3397a44b19239a00adfa9472eb0`, and `git update-index --refresh` exited 0.

**ps check:** I ran `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` as given. It printed nothing.

- **task:** DAEO-ouet (W2-96). A fresh, read-only FULL probe of `gov accept` at integrate `8f6e66a17`, covering everything since `8b31965edae8`. KPI id: `w2-96-full-probe`.
- **decisions:** the findings rest on these:
  - DEC-1112 (3) (ACCEPTED, standing), and the CTO's delegated PKG-D10a-scope (b) under it (`DECISIONS-IN-FORCE.md:443-446`);
  - DEC-1061 (2) (ACCEPTED);
  - DEC-959 item 6, DEC-970's PKG-1 (a) (ACCEPTED), DEC-317 and DEC-820 (c);
  - DEC-801, DEC-808 and DEC-1010 (ACCEPTED), and DEC-1014.
  - F1 names both ids of a superseded text: S-D10a's wording (`bbe222c59`) against PKG-D10a-scope (b), which is the rule in force.
- **status:** DONE. The verdict is **pass**. There are three findings and none blocks.
- **work_completed:**
  - I checked identity and the history since the last probe.
  - I read the ticket, the last probe, both review rounds, JUDGEMENT, EMG-common, the runner, the command module, the root conftest's opt-in rules, W2-96's README map and the CLI's output path.
  - I ran the three runs the brief names, plus one refusal probe.
  - I swept every acceptance README with the old and new map readers, and checked opt-in overlaps and which groups each map needs.
  - I verified that nothing was written.
  - This took longer than the 20-minute estimate, mostly because of the sweeps over every map.
- **files_changed:** none.
  - `git status --porcelain` is empty at the start and at the end, and HEAD is `8f6e66a17` both times.
  - `git status --porcelain --ignored` is identical before and after.
  - `find src tests .tickets docs -newer <a marker made before the first run>` finds nothing.
  - Outside the trees: Step 0's blob and index refresh, as the brief requires, and my scratch folder, now removed.
  - **Refusal taken:** the Write tool was refused for a probe script in my scratch folder. I ran the same read-only probes as inline `python3 -I -c` commands, which write no file.
- **evidence:**
  - Probed commit `8f6e66a17572ff2e192244df7aff19d7c8bd9af9`, checked at the start and at the end. Session `e9c9fa7c-01f8-4b6c-869d-4240b15dab08`. `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-ouet`.
  - **The log** `git log 8b31965edae8..8f6e66a17` over the judged paths shows exactly the brief's list:
    - the ticket commit `bbe222c59`;
    - the tests `88c0772ff`, `5e36c7fc5` and `51f1f547a`;
    - the code `04b52305a`, `3ac8e892f`, `dac10e5df` and `1df7ccd60`;
    - the scratch merge `08c31e7ff` and the merges `443ce88f5` and `bb71be1cf`.
  - **Full history** adds three merges. `90c1fea6c` changes no judged file against its first parent. `5465e8137` and `4e63a8adc` carry only `bbe222c59`'s four ticket lines.
  - **The merges are faithful:**
    - From `bb71be1cf` to `8f6e66a17`, the judged files, `tests/conftest.py` and all four opt-in lists are byte-identical.
    - The designer's tests survive both merges unchanged.
    - `08c31e7ff` is a clean union of its two parents: each side adds only the other's files.
  - **Scratch:** it peaked at 20K and 7 inodes (`du -sh`, `du -s --inodes`). I removed it with `rm -r`, and the user site is intact.
- **tests:** every run went through `heavy_slot.sh` with the pinned interpreter. Each used `PYTHONPATH=<tree>/src`, a scratch HOME whose `.local/lib` linked to the user site, a scratch TMPDIR and `PYTHONDONTWRITEBYTECODE=1`. The pytest runs used `-p no:cacheprovider -o tmp_path_retention_policy=failed`.
  1. **W2-96's acceptance folder** (`--optin=lifted --optin=breadth -n 4`, plus the D-4b exclusion flags): **190 passed** in 43.4 s.
  2. **`tests/unit/accept`** (same flags): **206 passed** in 25.4 s.
     - Across both folders the exclusion left out exactly one case: `test_w2_96_d10.py::test_w2_96_d10b_every_listed_line_is_read[… in a real session: after-names9]`. It is a string-parse case whose id holds "real". Run alone, it passed, so the unit folder is **207/207**.
     - `-m local_only` selects nothing.
  3. **`gov accept W2-96`, the declared way:** **exit 0, `outcome: pass`**, `error_kind` null. 190 passed, 0 failed, 0 skipped, with `"optin": ["breadth"]` and no `report_only` key.

     | Line | S1 | S2 | S3 | S4 | S5 | S7 | S8 | F1 | F2 | F3 | F4 | unmapped |
     |---|---|---|---|---|---|---|---|---|---|---|---|---|
     | passed / failed | 14/0 | 22/0 | 23/0 | 11/0 | 36/0 | 24/0 | 38/0 | 18/0 | 23/0 | 11/0 | 31/0 | 42/0 |

  4. **Refusal probe, `gov accept W2-92 --json`:** exit 1, `ok: false`, `ACCEPT_MAP_UNREADABLE`.
     - The error names README line 128 and the cell. No test ran. This is round 2's F4.
- **discoveries:**
  1. **The last probe's F1 is resolved.** S2, S5, F1 and F4 now pass, measured: breadth is enabled for the R15 and R16 cases the map names. The run's 190 cases equal the folder's count with both opt-ins, so no W2-96 case is lifted.
  2. **The ticket's S-D10a was not amended to scope (b).** See F1.
  3. **One more silent-drop range form.** See F2.
  4. **W1-22 and W2-87 name cases in forms that match nothing.** See F3. W2-61h also holds a breadth entry while enabling no group; I did not examine why.
  5. **Eight readable maps would show report-only `lifted` lines:** W1-05 and W1-46 with breadth enabled; W1-30, W1-33, W2-107, W2-53, W2-71 and W2-72 with no group. Sixteen more maps get breadth alone.
  6. **Without `--json`, the CLI prints the result as indented JSON** (`main.py:186-190`). So `"optin"` and a report-only line's note appear in the text form too. Refusals go to stderr (`:184-185`).
- **risks:**
  - At the lift's closes (P1-13), these formal accepts fail or are refused for map-form reasons, all failing closed:
    - W2-87 and W1-22 (F3), and W1-27's S8 (round 1's F5);
    - W2-92 and W1-49, which are refused (round 2's F4).
  - The map-fix rows are needed before those closes, or the results must be read knowingly.
  - Until F1 is fixed, judging W2-96 from its ticket alone contradicts the code.
- **lessons:**
  - `python3 -I` does not imply `-B`. An inline probe that imports the tree's code needs `-I -B`. My first few probes lacked `-B`; they wrote nothing only because the existing bytecode was valid (the marker check confirms it).
  - Judge writes by entries newer than a marker, not by folder mtimes. The root's and `.gov-runtime`'s own mtimes move with every sandboxed command, because of the sandbox's mount points. They moved at 13:53:55 and again at 13:54:33, the moment of a plain `ls`, with no entry newer than the marker. The declared run had ended at 13:48:38.
- **proposed_decisions:** none.
- **unresolved:**
  - F3 rests on the runner's own matcher applied to the maps' items. I did not run `gov accept` on W1-22 or W2-87: they are whole suites, outside the brief.
  - Why W2-61h enables no group is unexamined.
  - S6 (the brief change) is outside gov accept's map by design. The ticket's D9-FATES note records it as met in half; it is outside this probe.
- **recommended_next_action:**
  - Take the probe as pass; READY is computed from the block below.
  - Before W2-96's close, amend S-D10a's text in the ticket, or add a note recording PKG-D10a-scope (b) (F1).
  - File F2 with round 2's F1 as one Wave 3 row.
  - Add map-fix rows for W1-22 and W2-87 beside W1-27's (F3).
  - No round.

## Answers to the checks

**1. Counts.** The acceptance folder passed 190/190. The unit folder passed 207/207 (206 with the exclusion, plus the 1 excluded case run alone). The declared `gov accept W2-96` passed: exit 0, 190/0, all 11 lines `pass`, breadth only. **The last probe's finding no longer holds:** no line fails without a failed case.

**2. No fail-open in the KPIs' terms.**
- **No test content leaks.**
  - The declared result holds only line ids, counts, totals and `"optin": ["breadth"]`.
  - The four cells refused in maps in use are named masked: W2-07 line 57, W2-68 line 91, W2-77 line 51 and W2-92 line 128. None holds a test, file or fixture name, an assertion text or a value.
  - The record of left-out cases lives in the private folder and is removed with it.
  - The suite's leak-marker probe passed in all 190 cases.
- **Unmapped cases counted.**
  - Every case that ran unmapped is counted (42/0/0). With breadth on, the whole folder ran.
  - Cases a list leaves out, in a group no mapped case needs, are neither run nor counted. S-D10a's "only" requires that (F3 names two maps where it matters).
- **Exit codes as declared.**
  - 0 on the pass, and 1 on the W2-92 refusal.
  - Codes 3 and 4 are covered by the suite's exit-code and error cases, which passed.
  - A report-only line never sets the code by itself: a run that measures no line fails with 3 (`runner.py:681-683`).
- **Nothing written:** see files_changed. The runner left no `gov-accept-*` folder in the TMPDIR it was given.
- **The reader never drops a listed line.**
  - I compared the old reader (`8b31965edae8`) and the new one over all 116 READMEs. Only W2-92 is newly refused (round 2's F4). Five maps read more items or lines, and none lost any.
  - All 2,597 mapped cells of the 56 readable maps were read in full. My scan's one flag was a false positive: W2-55 row 118, "W2-61's 20-question", is prose.
  - No map in use writes a spaced or worded range.
  - One unused form does drop lines (F2).
- **Lifted never runs or passes in a formal accept.**
  - `optin` never holds `lifted` (`runner.py:726`).
  - The caller's `GOV_TESTS_OPTIN` and `PYTEST_*` never reach the child (`:539-543`).
  - No lifted case shares an entry with breadth (535 lifted entries, 3,012 breadth). There are 28 nested overlaps, but all are breadth folder entries over lifted files in `tests/unit/close/` and `tests/unit/secrets_check/`, and no formal accept runs those. So the conftest's "collected whole" rule cannot pull a lifted case back into an accept.
  - A report-only line is never `pass`, and it cannot pass a run alone.
- **Round 2's rows:** none became reachable in ordinary work.
  - F2 is still not live. Only W2-54's conftest deselects, and W2-54 has 8 breadth entries and no lifted entry.
  - F1's forms appear in no map.
  - F3 and F4 are unchanged; I reproduced F4 live.

**3. Judgement: pass** for W2-96 at `8f6e66a17`.
- Every KPI line that gov accept measures is green, the declared way.
- The S-D10a/b behaviour matches the CTO's ruling in force.
- No finding is in scope, reachable in ordinary work, and failing open or losing work.

## Findings

Classification: 0 blocking. F1 is in scope, ordinary work yes, consequence other (a record row). F2 is in scope, ordinary work no, fails open (a Wave 3 row, with round 2's F1). F3 is out of scope, ordinary work yes, consequence other (map-fix rows). No round is proposed.

**F1 (S-D10a, record). The ticket's S-D10a still reads as it did before the CTO's scope (b).**
- **What was done:** I read W2-96's ticket at `8f6e66a17` beside the command's behaviour and PKG-D10a-scope (b).
- **What happened:**
  - The ticket says gov accept "runs the opt-in groups (tests/optin-lifted*.txt suites) that its own map's cases need", and that "a line whose mapped cases still run zero stays a fail".
  - Following (b), the command never runs `lifted`. It reports a line resting only on lifted cases as `report-only (lifted)`, and such a line does not fail the run.
  - Judged by the ticket's words alone, both behaviours are S-D10a failures. Eight maps in use will show such lines.
- **What should have happened:** the CTO's own delegated line should state the rule in force, or carry a note recording (b).
- **Both ids:** S-D10a as written (`bbe222c59`, DEC-1112 (3)), against PKG-D10a-scope (b) (CTO, 2026-11-10, DEC-1112 (3), `DECISIONS-IN-FORCE.md:443-446`), which is in force. The code follows (b).
- **What would reverse it:** the ticket amended, or annotated with (b), at the commit judged. Or a ruling that a delegated decision listed in DECISIONS-IN-FORCE amends a ticket's KPI text without an edit.
- Ordinary work: yes, because W2-96's close at the lift and any later audit read the ticket's KPI lines, with no construction needed.
- Consequence: other (the behaviour follows the decision in force; only the record disagrees).
- Scope: in.

**F2 (S-D10b, a row with round 2's F1). A range written with a space before the dash and none after it drops the lines it spans.**
- **What was done:** I gave the map reader the cells `S1 -S3` and `Success 1 -Success 3`.
- **What happened:**
  - Each was read as success-1 alone, with no refusal; success-2 and success-3 vanished.
  - For comparison, `S1-S3` reads all three lines, and `S1 - S3` and `S1 –S3` are refused, correctly.
  - This is round 2's F1 family, with a named second end instead of a bare number.
- **What should have happened:** the reader should read all three lines, or refuse the map naming the cell.
- **What would reverse it:** a map in use, or a designer's ordinary draft, writing a range this way. Or the reader reading or refusing these cells at this head.
- Ordinary work: no, because none of the 2,597 mapped cells in the readable maps writes it, and my scan found no listed line the reader drops.
- Consequence: fails open (a listed line is silently absent from the report).
- Scope: in.

**F3 (out of scope; round 1's F5 shape). Two maps in use name cases in forms that match no case, so their lines fail with no failed case.**
- **What was done:** I looked at the readable maps that hold breadth entries yet enable no group, and checked their rows' items against the runner's matcher.
- **What happened:**
  - W2-87's rows for S3/F3 and S4/F2 name several rows in one bracket: `test_4_…[not-a-mapping, unknown-default, …]` and `test_5_…[no-reranker, stub-alike]`.
  - W1-22's S1 names `TestValidatorAccepts::*` and `TestValidatorRejects::*`.
  - Each matches no case but counts as naming a test. So the line fails with no failed case, as W1-27's S8 does.
  - Breadth is never needed for those functions, so their extra rows are neither run nor counted.
  - The D-4 tables that name these cases by full node id have no Test column (W2-87 README:92, and W1-22's table holding line 172), so the reader ignores them by design.
- **What should have happened:** the maps should use the `file::name` form, or the matcher should accept these forms.
- **What would reverse it:** a `gov accept W2-87` (or W1-22) run at this head in which those lines pass, measured.
- Ordinary work: yes, because these are maps in use whose formal accepts run at the lift's closes.
- Consequence: other (it fails closed: a false failure, and nothing passes that should not).
- Scope: out (the item forms are older than this revision).

## Probed and found sound

- **History and roles:**
  - Only the listed commits touched the judged files, and every merge is faithful.
  - Every commit carries its trailers and stays within its allowed paths.
  - The implementer never changed the acceptance tests, and no work was lost.
- **The declared run:** it measures all 11 mapped lines with breadth only, and passes.
- **Lifted cases:**
  - `lifted` is never enabled, and the caller cannot enable it.
  - In acceptance folders, no breadth entry pulls a lifted case back in.
  - A line resting on any case that was not left out still fails when it runs zero.
- **The map reader:** it reads more and never less in every map in use. Its refusals name the cell with no test content.
- **Writes:** nothing was written in the repository, and the runner's private folder is removed.

```verdict
{"kpis": [{"kpi": "w2-96-full-probe", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```
