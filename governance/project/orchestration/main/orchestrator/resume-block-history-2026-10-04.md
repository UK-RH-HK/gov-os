## RESUME HERE (2026-10-04, parallel run, prompt v4)

- **Prompt v4** (`e4dc57ce`): parallel tickets with ticket leads. **Next free register id: DEC-244.** Register
  v0.46 (`c0a4c3b0`): DEC-235 parallel tickets, DEC-236 ticket leads, DEC-237 context limits, DEC-238 W1-08 kernel
  minimums + capabilities, DEC-239 W1-08 DP-3, DEC-240…DEC-242 W1-46 DP-4, DP-5, DP-7, DEC-243 digest accepted.
  No owner package is open. No digest is owed.
- **Commits after the register:** `8c267690` Contract CAP-23.c (W1, provider W1-42; **the provider is my choice,
  told to the owner**), `4e761153` W1-42 KPI line + sources, `17eac6a3` WBS rules, `ac7f4958` W1-08 KPI reworded,
  `97793f08` W1-46 allowed_paths + `research-allowlist.yaml`, `c7aba533` `state_class` on the 48 tickets (DEC-229,
  done), `5203ab3c` W1-37 and W1-18 claimed. Validator ALL PASS at `5203ab3c`.
- **Regression at `5203ab3c`** (after the ticket edits): ALL GREEN (W1-01 31 + 28 skipped, W1-02 529, W1-03 364,
  W1-04 336, W1-05 99, W1-06 96, W1-07 228, W1-45 105, W1-47 970, W1-48 172, `tests/unit` 430); validator ALL PASS.
- **In flight (4 tickets, 5 slots; W1-18 counts double). Worktrees under `~/gov-os-worktrees/`, branches
  `w1/<W1-id>`, all cut from `5203ab3c`. Leads are headless background sessions; each one's summary lands in
  `log/<W1-id>-lead-run1.json` (`result` field); briefs `briefs/<W1-id>-A5.md` (= `-A5-head.md` + `LEAD-common.md`).**
  - W1-46 (`DAEO-jdqr`, FULL): batch 2 tests → red → engineer → verify → reviewer.
  - W1-08 (`DAEO-uudf`, STANDARD): batch 2 tests → red → product-spec worker → verify.
  - W1-37 (`DAEO-yvzh`, LITE): tests → engineer. Likely a package (vendor folder vs. skills path, DEC-194/DEC-199).
  - W1-18 (`DAEO-1ve2`, STANDARD, heavy): tests → engineer. Ollama is not installed; an install package may come.
- **W1-37 update:** lead run 1 returned PACKAGES (4, no tests written). Delegated: DEC-244…DEC-247 (register
  v0.47, `b7e6da3b`; **next free id DEC-248**). Branch fast-forwarded to `b7e6da3b`; **lead run 2 running**
  (`briefs/W1-37-A5-run2.md`, `log/W1-37-lead-run2.json`). KPI disputes so far: 4.
  **Open with the owner (told, 1 package):** does the version recorded beside the vendored skills satisfy CAP-24's
  "version in frontmatter" (rec. yes for vendored skills; else the copies get a frontmatter version and the hash
  rule changes). **Digest owed:** DEC-244…DEC-247 (given in the message of this turn).
- **W1-18 update:** lead run 1 returned PACKAGES (3); branch head `71651e81` (1 test, red as stated); the lead's
  checkpoint is in the worktree's `.gov-runtime/scratch/lead/CHECKPOINT.md`. No lead running; worktree kept.
  **Put to the owner (told):** DP-1 interface (rec. (a) one function `ensure_available`, total deadline 20 s,
  add `src/gov/retrieval/__init__.py` to `allowed_paths`; names low confidence), DP-2 does `gov` stop the daemon
  (rec. (a) start only, with a note against ADR-0002's "stopped by gov" → owner's), DP-3 facet state (rec. (a)
  in the result + standard error). Full text in `log/W1-18-lead-run1.json`. On answers: record from DEC-248,
  ticket path change in its own commit (`Task: DAEO-1ve2`), fast-forward/merge `w1/integrate` into the branch, fresh
  lead. Also noted: G-22's text is not in the archive; the embedding-model registry row (DEC-195) is not needed by
  this ticket on stand-ins. KPI disputes so far: 3.
- **Owner decisions DEC-248…DEC-250** (register v0.48, `1432b82c`; **next free id DEC-251**): W1-49 new ticket
  (`DAEO-32n6`, FULL, engineer, light auto-resume hooks; commits `386fc5ab` ticket + WBS + validator 49 tickets,
  `2dd9aaef` CAP-37.g, `5dfa4bb8` ADR-0002 figure 5,580, `cf17d90a` claim); DEC-249 **mid-wave audit when W1-21 is
  merged** (fresh read-only independent auditor, own worktree, checks every closed ticket against Contract v4.1 and
  covers; findings follow DEC-220); DEC-250 **after W1-49 closes: stop only for owner-level packages, escalations,
  WAVE_1_EXIT_READY; TELL THE OWNER when W1-49 closes (operator updates prompt section 7), and say whether KPI 3
  ended in the residual.** Until then the CONTEXT_CHECKPOINT stop stays.
- **W1-49 lead run 1 running** (`briefs/W1-49-A5.md`, `log/W1-49-lead-run1.json`), worktree cut from `cf17d90a`.
- **W1-37: lead run 2 DONE** (branch head `68827e60`); merged `00e3d539`; post-merge suites running
  (`log/reg/at-00e3d539.txt`). On green: residuals to `bootstrap.md` (zero headroom on sizes, chars not bytes; file
  modes not asserted; no LICENSE in the copy; CAP-24 version with the owner), `tk close DAEO-yvzh`, closed row,
  metrics (KPI disputes 4; rewrites 0; LOC 12 authored + 1,895 upstream copies against 20; tests 393 lines;
  converged; no conflict), save the worktree's `.gov-runtime/findings.jsonl` to `log/W1-37-findings.jsonl`, then
  `git worktree remove`, `git branch -d w1/W1-37`.
- **Containment and merges (tell the owner, package):** `src/gov/guard/containment.py` flags every HEAD move that
  contains a merge commit ("HEAD moved (not a forward move on the same branch)"), so each section 3 merge writes
  one finding (`findings.jsonl` now 2 lines: W1-06 misattribution + the W1-37 merge). Also: in a worktree, a
  worker's commit of `tests/acceptance/**` is attributed to the lead's polling call and flagged in that worktree's
  findings (seen in W1-37 and W1-18). Both are records of real, permitted actions. Rec.: accept as records until a
  containment ticket teaches it section 3 merges and worker attribution; owner's call (touches containment).
- **P1 ANSWERED (register v0.50 `adcd0c95`: DEC-253…DEC-256; v0.51 `775948a3`: DEC-257 delegated; next free id
  DEC-258).** DEC-253: a test designer revises the W1-01 history test to accept an integration merge of
  test-designer commits (rewrite after implementation, "owner decision: integration merges"). DEC-254: merge
  findings and worker-commit misattributions are records (noted in `bootstrap.md` `3aaf21cf`; **note them in each
  close row**). DEC-255: new ticket **W1-50** (`DAEO-xnbx`, FULL, engineer, depends W1-03; commits `74aa6cf5`,
  CAP-58.h `b9a6c1b5`, ADR figure 5,680 `08acaa86`, claim `8be8a660`; validator counts 50 tickets).
  **DEC-256 ORDER — follow exactly:**
  1. W1-50 **test design batch only**: lead run 1 running (`briefs/W1-50-A5.md`, `log/W1-50-lead-run1.json`),
     worktree cut from `8be8a660` (contains the W1-37 merge).
  2. When it returns: merge `w1/W1-50` (tests only; `--no-ff`), run W1-01 → must be green; then the full run.
  3. Then resume merges and closes: close W1-37 first (steps in the W1-37 bullet), then W1-08 etc.
  4. W1-50's implementation (a fresh lead in the same worktree, engineer + reviewer) starts only **after W1-46 is
     merged**. Keep the W1-50 worktree and branch; after step 2 fast-forward the branch to `w1/integrate`.
  W1-50 holds a slot (6 of 6 with W1-46, W1-08, W1-49, W1-18×2, W1-37 awaiting close): start nothing new.
- **W1-49 update:** lead run 1 returned PACKAGES with tests committed (`829f8a37`, 62 tests, 9 `local_only`, red).
  Delegated: DEC-258 (DP-1: current = at most 30 min old; manual compaction blocked, automatic lets through +
  `CHECKPOINT NOT CURRENT` after), DEC-259 (DP-2: hooks act only for `GOV_ROLE=orchestrator`) — register v0.52
  `fb0de6d0`; **next free id DEC-260**. **DP-3 to the owner at the next stop** (prompt path for a lead: designer
  (a) lead checkpoint path + RESUME HERE only; lead (b) the orchestrator prompt path in both trees — I rec. (b);
  suite stands at (a) meanwhile). **Lead run 2 running** (`briefs/W1-49-A5-run2.md`, `log/W1-49-lead-run2.json`):
  engineer → verify → reviewer. Facts: `CLAUDE_CODE_AUTO_COMPACT_WINDOW=300000` in settings `env` works (KPI 3, no
  residual; not proved that a compaction starts near 300k); SessionStart cap 10,000 chars. **Tell the owner at
  close (DEC-250), with the DEC-258 gap: an automatic compaction over a stale checkpoint proceeds — so I must
  rewrite this checkpoint after every merge, close and stop.** KPI disputes: 3. Digest owed: DEC-257, DEC-258,
  DEC-259.
- **OWNER ANSWERS (register v0.53 `ba724fde`: DEC-260…DEC-264; next free id DEC-265). No owner package is open;
  no digest is owed.**
  - DEC-260/261 W1-18 (interface `ensure_available`; start only). Path commit `df204909`; `bootstrap.md` note
    `9c67919b`. **W1-18 lead run 2 running** (`briefs/W1-18-A5-run2.md`, `log/W1-18-lead-run2.json`): test batch 2,
    then it merges `w1/integrate` into its branch (to get the ticket's new path) **only if `tests/acceptance/W1-50`
    is on `w1/integrate`**, else it returns LEAD_CHECKPOINT "waiting for merges to resume" → then restart a fresh
    lead with the same brief once the W1-50 batch is merged.
  - DEC-262 CAP-24: `vendored.yaml`'s version is enough for vendored skills. **Put in W1-30's brief: `gov close`
    reads a vendored skill's version from the record beside it.** W1-37 closes as soon as merges resume.
  - DEC-263 (W1-49 DP-3: role-specific injection) and DEC-264 (PreCompact never blocks; appends a generated state
    block: git head, tickets in progress from `tk`, worktree list, pending owner decisions; SessionStart warns when
    the written part is older than the block; **amends DEC-258**). W1-49 KPI lines added `69b766bc`.
    **W1-49 lead run 2 is still building to the old suite (block on manual). When it returns: do NOT merge; start
    a fresh lead (run 3) for a test batch on DEC-263 + DEC-264 (rewrites after implementation, "owner decision,
    DEC-264"), then a fresh engineer, verify, reviewer.** The branch needs the ticket's new KPI lines only for
    reading; give them in the brief.
- **W1-08: lead run 2 DONE** (branch head `54c7748a`; 209 cases; all suites green on the branch, W1-46 red from
  its own ticket). **Ready to merge after the W1-50 test batch (DEC-256), after W1-37's close.** Delegated DEC-265
  (DP-10: `languages` required only when enabled; test case → W1-27's test design) — register v0.54 `3357de7c`;
  **next free id DEC-266**; digest owed: DEC-265 (given). At close: residuals 1–15 from
  `log/W1-08-lead-run2.json` to `bootstrap.md`; metrics: KPI disputes 10 (7 + DP-8 + DP-9 by the lead + DP-10),
  rewrites after implementation 0, tests added after implementation 9 cases + 1 strengthened ("delegated
  decision"), LOC 690 added / 7 removed against 200, converged. Leftover untracked
  `.gov-runtime/scratch/w1-08-batch3/` in the worktree goes with `git worktree remove --force` (untracked scratch
  only; check `git status` is otherwise clean first). After the merge, "every tracked path in exactly one
  namespace" may fail for paths other tickets added (W1-37's skills, W1-50's tests): if so, a product-spec repair
  of `path-map.yaml` under W1-08 before closing. Tell W1-46's close: update the `systems` snapshot (research).
- **W1-50 test batch MERGED `30185589`** (branch head `d2ab1147`: W1-01 revision `2da766ab`, W1-50 suite 43
  cases, 26 red by design). **W1-01 green on `w1/integrate`: 46 passed, 28 skipped.** Full run in
  `log/reg/at-30185589.txt` (running). `findings.jsonl` 3 lines (2 merges = records, DEC-254). **Merges resume
  when that run is green: close W1-37, then merge W1-08 (full run), close it.**
  W1-50: 7 packages. Delegated DEC-266…DEC-270 (DP-1, 2, 3, 6, 7) — register v0.55 `cb004822`; **next free id
  DEC-271**; digest given. **With the owner (told): DP-4** (trailers naming a closed / not-started ticket: lead
  rec. (b) ignore status for closed, (a) finding for not started; low-medium) **and DP-5** (a worker's call
  committing with another role's trailers: rec. (b) own-trailer judging only in the orchestrator's own call, plus
  the residual that the orchestrator can commit with designer trailers silently). On answers: record; W1-50 test
  batch 2 (DP-5 (b) and DEC-269 need a few more tests; may run before W1-46 merges — tests only; the W1-03 merge
  test stays under DEC-266); implementation only after W1-46 is merged. W1-50 worktree kept; fast-forward its
  branch to `w1/integrate` before the next lead. Rewrites after implementation: 1 (W1-01 history test, "owner
  decision: integration merges"); 15 W1-01 cases added. Told the owner: the revised W1-01 rule also fails a merge
  whose acceptance-test content matches no parent (two branches editing the same acceptance file).
- **W1-46: lead run 1 returned PACKAGES** (branch head `d00a4a97`; 326 cases, 4 failing each on an open package;
  all earlier suites green on the branch; reviewed; LOC 413/12 against 220; lead checkpoint in the worktree; full
  text `log/W1-46-lead-run1.json`). Delegated DEC-271 (DP-8), DEC-272 (DP-9), DEC-273 (DP-13) — register v0.56
  `4cd3ed6a`; **next free id DEC-274**; digest given. **WITH THE OWNER (stop block sent): W1-46 DP-14 (P1, `ln`
  to a new name under `.gov-runtime/`; rec. (b)), DP-16 (P1, who writes `.claude/agents/research.md`; rec. the
  owner copies the draft from the worktree's `.gov-runtime/scratch/W1-46/research.md`), DP-10 (P1, bypass flags and
  `--add-dir`; rec. refuse all), DP-11 (P1, unwired guard; rec. refuse, built), DP-12 (P1, Edit deny rules for
  acceptance tests, tickets, `.claude`; rec. all three + a KPI line), DP-15 (P2, `cdn-lfs.huggingface.co` does not
  resolve; rec. drop it); W1-50 DP-4, DP-5.** On answers: record from DEC-274; KPI line for DP-12 in its own
  commit (`Task: DAEO-jdqr`); fresh W1-46 lead from its checkpoint: test batch 4 (decided packages + DEC-271…273),
  fresh engineer, full verification with live sessions. Also told: launched sessions in a worktree probably can't
  commit (`.git` outside the sandbox root; inferred) — matters once leads use `gov launch`; the guard now denies
  `.gov-runtime/` outside `scratch/` to every role; residual list for `bootstrap.md` in the log. W1-33 and W1-50's
  implementation wait on W1-46.
- **(history) For the next stop (owner asked) — answered above:** present W1-18 DP-1 (interface; rec. (a) `ensure_available`, 20 s total
  deadline, add `src/gov/retrieval/__init__.py` to allowed_paths; low confidence on names → owner) and DP-2 (stop
  the daemon; rec. (a) start only; sets aside ADR-0002's "stopped by gov" → owner), and the W1-37 CAP-24 version
  question (rec. (a) the record beside the files is enough; reads the Contract → owner). DP-3 is delegated
  (DEC-257). Digest owed: DEC-251, DEC-252 (given), DEC-257.
- **(history) P1 as it was put:** The W1-37 merge commit `00e3d539` (trailer
  `Role: orchestrator`) makes `tests/acceptance/W1-01/test_w1_01_history.py::
  test_only_the_test_designer_commits_to_acceptance_tests` fail: it lists commits with `git rev-list
  --full-history HEAD -- tests/acceptance` and wants `Role: independent-test-designer` on each; a merge of a branch
  that carries tests is listed. `w1/integrate` is red on that one case (W1-01: 1 failed, 30 passed). W1-37 is NOT
  closed, worktree kept. Options put: (a) the owner/operator removes the unpushed merge and integration becomes
  something else; (b) a test designer revises the W1-01 test (and containment gets a ticket) to accept
  integration merges whose test changes all come from designer commits; (c) other. Rec. (b). Worktrees cut before
  `00e3d539` (W1-46, W1-08, W1-18, W1-49) are unaffected until they take `w1/integrate` in: **leads are told not
  to merge `w1/integrate` into their branch.** Rest of the run at `00e3d539`: see `log/reg/at-00e3d539.txt`.
- **W1-08 update:** lead run 1 returned PACKAGES with the ticket implemented and green at `4b209505` (200 cases;
  LOC 664/200; 11 residuals listed in `log/W1-08-lead-run1.json` for `bootstrap.md` at close). Delegated: DEC-251
  (capabilities entry shape), DEC-252 (`lesson_id` `^L-[0-9]{4,}$`) — register v0.49 `05155c41`; **next free id
  DEC-253**. **Lead run 2 running** (`briefs/W1-08-A5-run2.md`, `log/W1-08-lead-run2.json`): short test round +
  small repair. Its note: the product-spec worker's output showed the held-out path string twice (from ticket
  `allowed_paths` and ADR-0002 §6) — accepted residual per DEC-223. **Digest owed:** DEC-251, DEC-252 (given).
- **Waiting: W1-33** (`DAEO-xog0`, not claimed). Its `allowed_paths` (`template/governance/kernel/roles/**`,
  `governance/project/roster.yaml`, `.claude/agents/**`) overlap W1-46's (research role file, `roster.yaml`,
  `.claude/agents/research.md`), so section 3 makes it wait; its KPI also says it leaves W1-46's research role in
  place. Start it when W1-46 is merged and closed. Told to the owner.
- **When a lead returns:** read only `result`. DONE → in the main tree `git merge --no-ff w1/<W1-id>`, run every
  acceptance suite + `tests/unit` + validator, then `tk close`, closed-tickets row, learning metrics, residuals to
  `bootstrap.md`, `git worktree remove`, `git branch -d`. PACKAGES → decide under DEC-220 or put to the owner,
  record, then a fresh lead in the same worktree with the answers. LEAD_CHECKPOINT → a fresh lead in the same
  worktree (same brief; it reads `.gov-runtime/scratch/lead/CHECKPOINT.md` there). After each merge the other
  leads' branches are behind: a conflict at their merge is resolved in their worktree.
- **If I was restarted:** the background lead processes may be gone. Check `pgrep -af "claude -p"` and each log;
  a lead with an empty log and no process is restarted fresh in its worktree (it resumes from its own checkpoint
  or from `git log`).
- **Guard note:** the guard refuses `mkdir` outside the repository for me, but `git worktree add
  ~/gov-os-worktrees/<id> …` (the prompt's command) works and creates the folder. Here-documents are refused: write
  with Write, then `cat file >> target`.
- **Next after these:** W1-33 (after W1-46), W1-10 (needs W1-08; critical path), W1-12, W1-34, W1-25, W1-15
  (need W1-08), W1-09 (needs W1-10). Gate before each start: `free -g` ≥ 4 GiB available, load < 20 (nproc 20).

- **LATEST STATE (read this last, it overrides the bullets above where they differ):** W1-37 CLOSED
  (`84b1b874`). **W1-08 MERGED `00af199c`** (W1-08 209 + W1-01 46 green, validator ALL PASS right after the
  merge); full run in `log/reg/at-00af199c.txt`. On green: `cat bootstrap-w1-08.md >> bootstrap.md` (file is in
  this folder), commit (`Task: DAEO-uudf`), `tk close DAEO-uudf`, commit, closed row + metrics, copy the
  worktree findings to `log/W1-08-findings.jsonl`, `git worktree remove --force` (untracked scratch only), delete
  the branch. **W1-08's close makes ready: W1-10 (critical path; also needs W1-07 ✓), W1-12, W1-34, W1-25, W1-15
  (check their deps and path overlaps, then claim + worktree + lead for each, within the gate; slots: W1-46 1,
  W1-49 1, W1-18 2, W1-50 1 → 1 free now, more when leads return).** Running leads: W1-49 run 2, W1-18 run 2.
  Waiting on the owner: W1-46 (6 packages), W1-50 DP-4/DP-5.

- **W1-49: lead run 2 DONE on the OLD decisions** (head `171c9188`, 65 green, reviewed; not merged). **Lead run 3
  running** (`briefs/W1-49-A5-run3.md`, `log/W1-49-lead-run3.json`): merges `w1/integrate` into its branch, test
  batch 3 for DEC-263 + DEC-264 (rewrites after implementation, "owner decision, DEC-264"), engineer, verify,
  reviewer → DONE → merge, full run, close, **then tell the owner (DEC-250)**. Run 2's twelve residuals are in
  `log/W1-49-lead-run2.json`; run 3 says which still stand. Its merge will also bring `.claude/settings.json`
  changes (two hook registrations + `env.CLAUDE_CODE_AUTO_COMPACT_WINDOW=300000`): never print or diff that file.

- **LATEST (overrides the above):** W1-08 CLOSED `632c5c2a`, worktree removed. **W1-18 lead run 2 DONE** (head
  `884e84b0`), **MERGED `b81c4d43`** (W1-18 15 + W1-01 + W1-08 green, validator ALL PASS); full run in
  `log/reg/at-b81c4d43.txt`. On green: bootstrap residuals (from `log/W1-18-lead-run2.json`: a serve that never
  becomes healthy is left running; untested engineer choices; no registry row for the embedding model (DEC-195);
  G-22 text only in the archive; designer readings; no real-daemon test), `tk close DAEO-1ve2`, row + metrics (KPI
  disputes 3; rewrites 0; LOC 71 against 40; converged; 1 lead-side merge record), findings already copied
  (`log/W1-18-findings.jsonl`), remove worktree + branch.
  **W1-10 (`DAEO-4yyl`, STANDARD, critical path) claimed `2b88df5b`, lead run 1 running**
  (`briefs/W1-10-A5.md`, `log/W1-10-lead-run1.json`).
  **Ready, not started (start when W1-18 closes and frees 2 slots; gate first):** W1-12 (`DAEO-lc4q`, STANDARD,
  product-spec), W1-25 (`DAEO-rrxp`, STANDARD, engineer), W1-15 (`DAEO-7nne`, FULL, engineer), W1-34
  (`DAEO-egm9`, LITE, product-spec). No path overlaps among them or with tickets in flight. Slots now: W1-46 1,
  W1-49 1, W1-50 1, W1-18 2, W1-10 1 = 6.

- **LATEST 2 (overrides the above):** full run at `b81c4d43` ALL GREEN (W1-18 15, W1-08 209, W1-01 46 + 28
  skipped, W1-37 4, W1-02 529, W1-03 364, W1-04 336, W1-05 99, W1-06 96, W1-07 228, W1-45 105, W1-47 970, W1-48
  172, unit 433; W1-50 26 failed / 17 passed by design; validator ALL PASS). **W1-18 CLOSED `d9e5c386`**, worktree
  removed. **Claimed `092cd013` and leads running: W1-15** (`DAEO-7nne`, FULL; `log/W1-15-lead-run1.json`) **and
  W1-25** (`DAEO-rrxp`, STANDARD; `log/W1-25-lead-run1.json`). **In flight = 6: W1-46 (owner), W1-50 (owner),
  W1-49 run 3, W1-10 run 1, W1-15 run 1, W1-25 run 1.** Ready, waiting for a slot: W1-12 (`DAEO-lc4q`), W1-34
  (`DAEO-egm9`). Closed today in the parallel run: W1-37, W1-08, W1-18. `findings.jsonl` in the main tree: 1 old
  + one record per merge.

- **LATEST 3:** **W1-10 lead run 1 returned PACKAGES with the ticket built and green** (head `5661f99c`, 76
  cases; LOC 238 against 260). Delegated DEC-274…DEC-278 (DP-1, 2, 4, 5, 6) — register v0.57; **next free id
  DEC-279**; digest given. **DP-3 with the owner (told, not blocking): who writes `.gov-runtime/store.db` in a live
  session** (rec. (a) only the orchestrator / `gov` run by it, decided for good at W1-27; low-medium). **MERGED
  `46449b17`** (W1-10 76 + W1-01 green, validator ALL PASS); full run in `log/reg/at-46449b17.txt`. On green:
  `cat bootstrap-w1-10.md >> governance/project/bootstrap.md` (file in this folder), commit (`Task: DAEO-4yyl`),
  `tk close DAEO-4yyl`, row (base `2b88df5b`, head `5661f99c`) + metrics (KPI disputes 0; ambiguity packages 5 +
  DP-3; rewrites 0; LOC 238/260; converged), worktree + branch removed (findings copied:
  `log/W1-10-findings.jsonl`). **To do later (DEC-277): a product-spec gap worker checks the four edge keys against
  the archived Framework §11.2.** After W1-10 closes: W1-09 (`DAEO-topz`, FULL; needs W1-07, W1-08, W1-10 — all
  closed then; check its paths for overlap) takes the free slot before W1-12 / W1-34.

- **LATEST 4: W1-25 lead run 1 returned PACKAGES** (head `58869523`: 52 tests red, 1 planned W1-07 revision;
  no engineer; lead checkpoint in the worktree; full text `log/W1-25-lead-run1.json`). Delegated DEC-279…DEC-282
  (DP-2, 4, 5 shape, 6) — register v0.58; paths commit (`Task: DAEO-rrxp`); **next free id DEC-283**; digest given.
  **With the owner: DP-1 (presented): how `gov checkpoint` is wired when `src/gov/cli/**` is outside the paths —
  designer (a) add `src/gov/cli/main.py` to the ticket; lead (b) one generic change in `main.py` by the
  orchestrator so each command's handler, arguments, act paths and exit code come from its own module (I rec. (b),
  but W1-46 holds `src/gov/cli/**` and is in flight → do it after W1-46 merges or let W1-46's engineer do it).
  HELD for the cap of five, present next: DP-3 (checkpoint directory `docs/checkpoints/<ticket>/` + guard and
  containment exception; rec. (c); owner-level) and the DP-5 default age / commit count.** On answers: fresh lead
  from its checkpoint (the branch must take `w1/integrate` in for the ticket's new paths).
  Owner queue now: W1-46 DP-14, 16, 10, 11, 12 (P1) + DP-15; W1-50 DP-4, DP-5; W1-10 DP-3; W1-25 DP-1.

- **LATEST 5: W1-49 lead run 3 DONE** (head `b33e6890`; 105 cases green with the real session; all other
  suites green on the branch; hooks 228 LOC against 120; full text `log/W1-49-lead-run3.json`). Delegated DEC-283
  (DP-4), DEC-284 (DP-5) — register v0.59; **next free id DEC-285**; digest given. **NOT MERGED: with the owner
  (P1-level, told): second review finding 1 could lose written content** (a save of the checkpoint in place
  between the hook's read and its write is cut or overwritten; reachable only by wrapping the file object; the
  hook runs while the session is idle). The prompt says such a finding is fixed; the lead and I recommend accepting
  it as a residual until W1-29. On "accept": record, merge `w1/W1-49`, full run, residuals to `bootstrap.md`
  (lists in the run 2 and run 3 logs), close, **tell the owner W1-49 is closed (DEC-250) with: threshold
  configurable, no residual on KPI 3; the warning shows after every compaction until I rewrite the checkpoint; the
  block cannot list pending owner decisions.** On "fix": a fresh lead (test batch as described behaviour, then
  engineer). Metrics: KPI disputes 5; rewrites after implementation 15 + 2 removed ("owner decision, DEC-264");
  tests added after implementation 45; LOC hooks 228 / settings 24 / builder tests 123; converged; 3 lead runs.
  After the merge the PreCompact hook appends a state block to THIS checkpoint at each compaction: leave the
  block alone and rewrite the written part.

- **LATEST 6: W1-15 lead run 1 returned PACKAGES** (head `7ed25507`, 59 cases red; no engineer). All six
  delegated as recommended: DEC-285…DEC-290 — register v0.60 `7538546f`; **next free id DEC-291**; digest given;
  **asked the owner to confirm the count of seven canaries (DEC-286)**. **Lead run 2 running**
  (`briefs/W1-15-A5-run2.md`, `log/W1-15-lead-run2.json`): merges `w1/integrate`, engineer, verify, reviewer. At
  close: correct the W1-08 residual lines in `bootstrap.md` that name W1-15 (DEC-289 → W1-17 or W1-24); raise
  gitleaks on CI with W1-40 (DEC-287).

- **LATEST 7 (current state):** full run at `46449b17` ALL GREEN (W1-10 76, W1-18 15, W1-08 209, W1-01 46 + 28
  skipped, W1-37 4, W1-02 529, W1-03 364, W1-04 336, W1-05 99, W1-06 96, W1-07 228, W1-45 105, W1-47 970, W1-48
  172, unit 437; W1-50 red by design; validator ALL PASS). **W1-10 CLOSED `d79bc38f`.** **W1-09 (`DAEO-topz`,
  FULL) claimed `ee7f0ffb`, lead run 1 running** (`briefs/W1-09-A5.md`, `log/W1-09-lead-run1.json`).
  **In flight = 6:** W1-46 (owner: 6 packages), W1-50 (owner: DP-4, DP-5; impl after W1-46), W1-25 (owner: DP-1;
  held DP-3 + defaults), W1-49 (owner: accept/fix the lost-content finding; else ready to merge), W1-15 (lead run
  2 running), W1-09 (lead run 1 running). **Closed in the parallel run: W1-37, W1-08, W1-18, W1-10.**
  **Ready, waiting for a slot:** W1-12 (`DAEO-lc4q`), W1-34 (`DAEO-egm9`). Blocked: W1-33 (W1-46), W1-17
  (W1-15 + owner's W1-10 DP-3 answer), W1-16 (W1-15). Context: this session is long — at the next merge or close,
  consider the CONTEXT_CHECKPOINT stop (DEC-237; still in force until W1-49 closes).

## RESUME HERE (2026-10-04, parallel run, prompt v4 — consolidated after W1-10's close)

- **Prompt v4** (`e4dc57ce`). **Next free register id: DEC-306.** Register v0.65. Branch
  `w1/integrate`, tree clean, nothing pushed. Validator ALL PASS (it counts 50 tickets: W1-49 and W1-50 are new).
- **Last full run:** at `797ea347`, ALL GREEN (W1-15 92, unit 444; the rest as at `46449b17`: W1-10 76, W1-18 15, W1-08 209, W1-01 46 + 28 skipped, W1-37 4,
  W1-02 529, W1-03 364, W1-04 336, W1-05 99, W1-06 96, W1-07 228, W1-45 105, W1-47 970, W1-48 172, `tests/unit`
  437; W1-50 26 failed / 17 passed **by design** until its engineer runs). Since then only tickets, the register,
  `bootstrap.md` and `.gitignore` changed. Regression command and results: `log/reg/`.
- **Closed in the parallel run:** W1-37, W1-08, W1-18, W1-10, W1-15 (rows and metrics below).
- **Standing rules added today (all in the register and the WBS rules):**
  - DEC-235/236/237: up to 6 tickets, one worktree each (`~/gov-os-worktrees/<W1-id>`, branch `w1/<W1-id>`), a lead
    per ticket; gate before each start (`free -g` ≥ 4 GiB available, load < 20); heavy tickets count double; I
    merge (`git merge --no-ff`, trailers `Task: <id>` / `Role: orchestrator` in the last paragraph), re-run every
    suite, then close, remove the worktree, delete the branch.
  - DEC-253/254: each merge writes a containment finding ("HEAD moved, not a forward move") and each worktree
    holds worker-commit misattributions: **records, not defects**; note them in the close row; copy the worktree's
    `.gov-runtime/findings.jsonl` to `log/<W1-id>-findings.jsonl` before removing it.
  - DEC-256: W1-50's implementation only after W1-46 is merged.
  - DEC-249: **mid-wave audit when W1-21 is merged** (fresh read-only independent auditor, own worktree).
  - DEC-250: **when W1-49 closes, tell the owner** (operator updates prompt section 7); until then the
    CONTEXT_CHECKPOINT stop stays.
  - Leads are told to `git merge w1/integrate` into their branch at the start of a run (allowed since the W1-01
    history test was revised, `30185589`).
- **How a lead is started** (always background, one Bash call each):
  `cd ~/gov-os-worktrees/<W1-id> && /home/usain/.local/bin/claude -p --output-format json --permission-mode
  acceptEdits --allowedTools "Bash" "Read" "Edit" "Write" "Grep" "Glob" "Agent" "Monitor" "TaskStop" --settings
  '{"env":{"GOV_ROLE":"orchestrator","GOV_TICKET":"<ticket id>"}}' < <main tree>/.gov-runtime/scratch/orchestrator/
  briefs/<W1-id>-A5-runN.md > …/log/<W1-id>-lead-runN.json 2> …/log/<W1-id>-lead-runN.err` (absolute literal
  paths). A brief = `briefs/<W1-id>-A5-headN.md` + `briefs/LEAD-common.md` (cat with literal paths). Read only the
  JSON's `result`. Guard notes: here-documents and shell variables in write targets are refused; `mkdir` outside
  the repository is refused but `git worktree add ~/gov-os-worktrees/<id> -b w1/<id> w1/integrate` works.
- **A lead that returns a one-line "waiting for the worker" result has ended its turn and killed its worker.**
  Check `git status` in the worktree, then restart a fresh lead whose brief says: after starting a worker in the
  background, wait in the foreground with `until [ -s <log> ]; do sleep 20; done`, repeated, before saying
  anything (see `briefs/W1-09-A5-run3.md`). Put that paragraph in every new lead brief.
- **If I was restarted:** background leads may be gone. `pgrep -af "local/bin/claude -p"`; a lead with an empty
  log and no process is restarted fresh with the same brief (it resumes from the worktree's
  `.gov-runtime/scratch/lead/CHECKPOINT.md` and `git log`).

### In flight (6 of 6)

| W1 | ticket | worktree head | state | next |
|---|---|---|---|---|
| W1-46 | `DAEO-jdqr` FULL | `d00a4a97` | implemented, reviewed, 322/326; lead checkpoint in the worktree | **owner: DP-14, DP-16, DP-10, DP-11, DP-12 (P1), DP-15.** Then: KPI line for DP-12 (own commit), fresh lead (merge integrate; test batch 4 for the answers + DEC-271…273; engineer; live sessions), merge, close; update W1-08's `systems` snapshot note; then start W1-33 and W1-50's implementation |
| W1-50 | `DAEO-xnbx` FULL | `d2ab1147` (tests merged `30185589`) | test batch 1 merged; DEC-266…270 delegated | **owner: DP-4, DP-5.** Then test batch 2 (DP-5, DEC-269 need a few tests); engineer only after W1-46 merges. Fast-forward the branch to `w1/integrate` before the next lead |
| W1-25 | `DAEO-rrxp` STANDARD | `58869523` | 52 tests red; DEC-279…282 delegated; paths commit `8bb69324` | **owner: DP-1 (wiring in `src/gov/cli/main.py`; I rec. (b) one generic change, done in W1-46's round).** HELD for the cap: DP-3 (checkpoint directory + guard/containment exception) and the DP-5 default age / commit count |
| W1-49 | `DAEO-32n6` FULL | `b33e6890` | built, 105 green, reviewed twice; DEC-258/259/263/264/283/284 | **owner: accept as a residual, or fix, the second review's finding 1 (an in-place save during the hook's read–write window can be lost).** On accept: merge, full run, residuals (run 2 and run 3 logs), close, tell the owner (DEC-250). Never print or diff `.claude/settings.json` (it gains two hook registrations and `env.CLAUDE_CODE_AUTO_COMPACT_WINDOW`). After the merge the hook appends a state block to THIS file at each compaction: leave the block, rewrite the written part |
| W1-12 | `DAEO-lc4q` STANDARD | `9ace3f8b` | **lead run 2 DONE**: 21 tests green, config file delivered (DEC-303), all other suites green on the branch; 429 lines (about 112 authored) against 110; residuals 1–8 in `log/W1-12-lead-run2.json`. DEC-302…DEC-305 delegated (register v0.65; paths commit `c303bd84`) | **NOT MERGED: owner DP-5 (presented)** — the CIT-E half of KPI 3 [CAP-30.e]: (a) stated in the schema + residual on W1-26 (built), (b) a stamp with a hash test, (c) move that half to W1-26. Also asked: may G-07/G-09 in the workbench be read (DEC-304). On "(a)": merge, full run, residuals, close (base `6a053c1a`; metrics: 5 packages, rewrites 0, tests added after implementation 2 "delegated decision", 2 lead runs, converged) |
| W1-09 | `DAEO-topz` FULL | `ac6cbe3b` | **lead run 3 DONE**: 77 cases green, reviewed, 3 findings fixed (H1 release under a flock; H2 folder rule → DEC-300; M3 unreadable claim → DEC-301), all other suites green on the branch; source 211 lines against 100; 15 residuals in `log/W1-09-lead-run3.json`. Register v0.64 | **NOT MERGED: owner-level DP-4 (specification status) and DP-6 (open decision package), built on option (a), HELD for the cap — present them next.** On "as built": merge, full run, residuals, close (base `ee7f0ffb`; metrics: 10 packages, rewrites 0, tests added after implementation 15, LOC 211/100, 3 lead runs, one lead run lost its engineer). On a different answer: a short test round + small change first |

### Owner queue (what the owner has been told, in order of blocking)

1. W1-49: accept or fix the lost-content finding (blocks its merge and DEC-250).
2. W1-46: DP-14, DP-16, DP-10, DP-11, DP-12 (P1) and DP-15 (blocks W1-33 and W1-50's implementation).
3. W1-25: DP-1 (blocks its engineer).
4. W1-50: DP-4, DP-5.
5. W1-10: DP-3, who writes `.gov-runtime/store.db` in a live session (needed before W1-17).
6. Asked, not packages: confirm the seven canaries (DEC-286); DEC-283 means a warning after every compaction;
   DEC-290's root allowlist.
7. **Held for the cap of five, present next:** W1-25 DP-3 and the watchdog defaults; W1-09 DP-4 and DP-6.
   Full texts: `log/W1-25-lead-run1.json`, `log/W1-09-lead-run1.json`.
- **No digest is owed** (every delegated decision up to DEC-297 has been given; DEC-291…297 are in the message of
  the stop that follows this checkpoint).

### Ready, waiting for a slot

- W1-12 (`DAEO-lc4q`, STANDARD, product-spec; `template/openspec/schemas/**`,
  `template/governance/kernel/templates/openspec/**`) and W1-34 (`DAEO-egm9`, LITE, product-spec; two template files
  under `template/governance/kernel/templates/`). No overlap with tickets in flight (W1-25 has
  `templates/checkpoint.md` only).
- W1-16 (`DAEO-lkeb`, FULL, codebase-memory wrapper) is ready since W1-15 closed, but counts double (indexing): start it when two slots are free. Blocked: W1-33 (W1-46); W1-17 (the owner's answer on W1-10 DP-3); W1-11 (W1-34);
  W1-13, W1-14 (W1-09, W1-12).

### Notes to carry

- W1-30's brief: `gov close` reads a vendored skill's version from `vendored.yaml` (DEC-262).
- W1-27's test design: the disabled `code_intelligence` form (DEC-265); the doctor check of the vendored `tk`
  (DEC-296); `gov rebuild` wired to `gov.store.load` with its registry case revised (DEC-275).
- DEC-277: before any real record uses `evidence_for`, `tests`, `generates`, `validates`, a product-spec gap worker
  checks them against the archived Framework §11.2.
- W1-46's lead inferred that a launched session in a worktree cannot commit (`.git` outside the sandbox root):
  test it before leads switch to `gov launch`.
- The owner chose the provider of CAP-23.c (W1-42) implicitly by not objecting; W1-49 and W1-50 carry my
  estimates (120, 100) and my mirror failure lines.


(The step-by-step bullets this block replaces are kept in `resume-block-history-2026-10-04.md` in this folder.)

## Earlier resume block (2026-10-04, superseded by the one above)
