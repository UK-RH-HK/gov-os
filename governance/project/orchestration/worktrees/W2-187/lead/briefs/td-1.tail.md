
----

## Rules
- One test (or more) per KPI line S1-S11 and F1-F6, each doing what its Verify says, read with the Interface items the
  line names (I1-I12; "How the code-bound clauses read" settles the wording). Name each after its id (`test_s1_...`,
  `test_f3_...`). Cover the printed codes a KPI line reaches: `STANDING DECLARED ...`, `STANDING_SPENT <k>`,
  `STANDING_LIVE <set>`, `STANDING_BRIEFS`, `STANDING_FORM`, `STANDING_NONE`, `STANDING_RETIRED`, `STANDING_DIGEST`,
  `MS-STANDING`, `MS-IMPORTED`, `USED` with exit 3, `PRE-FLIGHT standing: n <n> of <n_set>; dropped <k>`,
  `STANDING_THIN <live>`, `STANDING <week> right <r> of <n>: passes|misses`, `KEY <key>` / `LIVE <set>|none`,
  `drift: not yet (k of 4)` / `DRIFT ...`, `STANDING_FITTED`, `STANDING_STALE`, `MEMORY_REPAIR open|closed|residual`,
  `REPAIR open since <week>|none|residual DEC-<n>`, `MODE fresh` / `DUE ...` / `REASON first|28d|miss|wait`, the
  `MAINTAIN 1 store ... 6 reanchor <k>` line, the I12 digest lines, and the exit map (0, 1, 2, 3, 4).
- Reach the code as its callers do: `python3 -m gov.memaudit <subcommand> --sets-root <root> ...` and
  `bash governance/project/orchestration/tools/memaudit_cron.sh --repo <dir>` in a child process, judged by exit code,
  printed lines, and the files under `<runs>/indep/memaudit/<key>/` (I2), `<sets root>/runs/<set>/<week>/` and the
  key folder's `indep/`. Every child gets this tree's `src/` first on `PYTHONPATH` (fail the run if it would import
  `gov` from elsewhere, as the earlier suites do). A9's `walls_act` and `declare.bar` may be called in-process (they are
  library functions the Interface names), but import the ticket's new modules (`gov.memaudit.standing`,
  `gov.memaudit.maintain`) only inside test bodies, never at collection, so the suite runs red by failing, not by
  erroring at import.
- **The seams the Interface names, and only those:** `--sets-root`, `--repo`, `--runs-dir`, `--store-link`, `--gov`,
  `--claude`, `--gate-cmd`, `--week`, `--replaces`, `--residual`, `--sets`; the environment `GOV_INDEP_RUNS_DIR`,
  `GOV_MEMAUDIT_NOW`, `GOV_MEMAUDIT_MAINTAIN_TIMEOUT_S`, `GOV_MEMAUDIT_GATE_POLL_S`, `GOV_MEMAUDIT_GATE_MAX_S`,
  `GOV_MEMAUDIT_PYTHON`, `GOV_MEMAUDIT_SETS_ROOT`, `GOV_MEMAUDIT_GATE`. W2-170's and W2-171's steps run for real, fed by
  the fake `gov` and fake `claude` as W2-171's world feeds them (a fake `gov` answering `retrieve`/`measure`, `rebuild
  --integration`, `links --json`; a fake `claude` answering the reader and graders).
- **S3's spy (one shared code path):** run a planted fresh judged step and a planted standing judged step under a spy on
  the reader, grader and matcher functions (e.g. a `sitecustomize.py` on a planted `PYTHONPATH` entry that wraps
  `gov.memaudit.judge._Judge.one`, the grading call and `gov.memaudit.matcher`'s functions and logs each call with its
  qualified name), and assert the same qualified functions are called in both. Also assert no module of `src/gov/memaudit/`
  but the existing reader path defines the reader prompt or calls `claude` for the reader (the "no second copy" rule),
  by a source scan that names only function and module names.
- **S4 and F1 (the substring grep must mean something):** five planted misses whose ids, questions, gold paths, answers
  and citations are unique strings; grep stdout, stderr, `FIGURES.json`, `HISTORY.jsonl`, `<key>/indep/AUDITS.log`, the
  digest block (stdout and `DIGEST.txt`), every file under the key folder and every file under the sets root outside
  `runs/<set>/`: 0 hits each; no `misses.jsonl` anywhere; no auditor launch in the launch stub's log or the ledger.
  Every path that can appear on a printed line (sets root, repository, store link, stubs, interpreter) must contain none
  of the planted strings; assert that precondition before the grep. F1's "every launched session's brief": a standing run
  starts no launch at all; assert the launch stub's log is empty.
- **S2:** use `GOV_MEMAUDIT_NOW` for the ISO week. DECLARATION.json before USED before the first search: by the ledger's
  line order and the fake `gov`'s first search log time against the two files' mtimes (nanoseconds). A second run the same
  week: exit 3 and the trees (the sets root and the key folder) byte-identical by a hash of every file and mode. A
  planted `STOPPED` with no `reader/`: one restart (the folder renamed `<week>.stopped/`), a second refused with exit 3.
  A planted `STOPPED` with `reader/` present: refused.
- **S5 and the revisions (DEC-1156 (7), the ticket's "Test revisions"):** unit cases `bar(40)`, `bar(79)`, `bar(80)`
  give need_right 38, 76, 76 and max_wrong 2, 3, 4, and the `ROUNDING` text names "standing and fresh runs alike". Revise
  only the bar values and helpers in the W2-170, W2-171 and W2-172 files of your allowed paths (about 16 lines): the
  revised W2-170 helper `bar` returns I5's dict key for key, so W2-88's S15 case (tests/acceptance/W2-88/
  test_w2_88_practice.py) passes unedited. Make each revision the smallest that pins the new bar; change nothing else.
- **G1 (the CTO's routing):** in `tests/acceptance/W2-172/w2_172_world.py` (lines ~281-282) and `w2_172_git.py` (lines
  ~43-44) point `mem` and `audits_log` at `<runs>/indep/memaudit/<key>/` and `<key>/indep/AUDITS.log` with I2's key
  (about four lines). Every W2-172 test file other than `test_w2_172_s7_digest.py` stays byte-unchanged;
  `test_w2_172_s7_digest.py` changes only for the bar figure and for I12's DRIFT/MAINTAIN lines when a set is live.
- **Commits for the revisions:** one commit for the bar values with the trailer `Rewrite-Reason: DEC-1179 (2)`, and one
  for W2-172's two helpers with `Rewrite-Reason: DEC-1179 (5)`, each in the same final trailer paragraph as Task and
  Role (see Commit below). Your W2-187 suite goes in its own commit(s).
- **S8:** `tests/acceptance/W2-172/test_w2_172_s5_due.py` passes unchanged (no live set); add the fresh-cadence cases
  (27 days not due, 28 days due on the Monday; a miss makes it due the next Monday), the P1 line, the two repair
  openings, and `status --repair` exit 1, then 0 after a planted pass or `--residual DEC-1`, and exit 4 for a malformed id.
- **S9:** two planted repositories on one runs folder: two keys (assert the key's form `<basename>-<8 hex>` from the
  realpath), neither reads the other's `HISTORY.jsonl`; a pin change on an adopted repository is a retrieval change
  (`due` gives weekly with that reason); a change under `src/gov/retrieval/` of a Gov OS-shaped repository is not a
  trigger for an adopted one; `pool-import --sets a b` imports exactly a and b; a standing set name is `MS-STANDING`.
- **S10:** planted store 3 commits behind (one `rebuild --integration` call in the fake gov's log, the head printed);
  a failing rebuild (the old store kept and the failure named, exit 0); planted link findings and two unindexed paths
  counted; the audit (the standing run) runs whatever the pass finds; `retrieval.yaml` and path map digests unchanged; a
  set with one changed cited block and one block moved unchanged lists only the changed one, by question id and entry
  number, in `REANCHOR-<week>.json`, with no question, answer or path text in it or in the digest. Note G6 (a same-head
  refresh of a stale-layout store) is the engineer's evidence, not a test of yours.
- **S11:** the wrapper with `GOV_MEMAUDIT_PYTHON` pointing at an interpreter shim (as W2-172's py_shim.py) that answers
  `standing live`, `due`, `due --fresh`, `maintain`, `standing run`, `run` with planted output and logs each call: a due
  standing run and a due fresh set run maintain, standing run, then run, in that order; a standing run ending `misses`
  adds a second `maintain` before `run`; nothing runs when neither is due; `LIVE none` gives today's path. A planted A9
  call to `walls_act(..., repo=<dir>)` writes ACT.md whose step 6 holds the cron line with `--repo <dir>` and Mondays
  21:00; no crontab is called (W2-172's fake_crontab.py on PATH records no call).
- **F2:** `measure --kept` on a standing set exits 3 and writes nothing; a planted edit to a hidden file after the
  declaration is `STANDING_DIGEST` before any search, with the week not spent. **F3:** `standing run --decision x`,
  `--force` and a data flag each exit 4; `--help` of every subcommand shows no command comparing two configurations or
  commits on a standing set. **F4:** `tests/unit/memaudit/test_prompts.py` unchanged since the base (git) and passing,
  plus S3's spy. **F5:** W2-170's S3 and F2 cases on fresh sets pass with only bar values revised; W2-171's S5 case
  unchanged (git diff against the base shows it). **F6:** S10's runs; `maintain.py`'s source imports no crontab writer
  (scan for `crontab`), and the digests are unchanged after a pass.
- **A scope case:** `git diff --name-only <merge-base with w2/integrate>...HEAD` lists only the ticket's allowed_paths
  plus `tests/acceptance/W2-187/`; it judges only branch `w2/W2-187` and skips elsewhere; say so in its docstring.
- **The split (pre-approved, DEC-1179 O8 (a)):** put S10 and S11 in their own files (`test_w2_187_s10_*.py`,
  `test_w2_187_s11_*.py`) and their helpers apart, so they can move to W2-187b whole. In `discoveries`, give your
  estimate of the implementation lines your suite demands, split as S1-S9 and S10-S11, and say whether the whole is
  above about 900 lines.
- Tests are red now (no `standing`, `maintain`, `due --fresh`, `status --repair`, keyed state, new bar). Run them and
  say which are red and why; anything green now is a fault in the test unless it guards "nothing else happens" or an
  unchanged behaviour (S8's W2-172 S5 case, F4, F5).
- Keep the suite fast (seconds per case, the whole folder in a few minutes): fake commands only; worlds built once per
  module where cases do not write to them. No test named with `real`, `green_here` or `time_limit`. Bounded polls,
  never a bare sleep.
- **Every pytest through the heavy-slot gate**, one folder per run, TMPDIR the sandbox's own `$TMPDIR` (outside the
  repository and outside ~/gov-os-runs):
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-187-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187-tests/src python3 -m pytest tests/acceptance/W2-187 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (make the empty HOME first with `mkdir -p`); run the same for `tests/acceptance/W2-170`, `W2-171`, `W2-172` and
  `W2-88` after your revisions and report each summary line. A heavy-slot or resource refusal is a wait: run again when
  it opens; it never counts as a refusal.
- Add `tests/acceptance/W2-187/README.md`: how the tests reach the code, what is planted, each KPI's cases.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-187-tests/.gov-runtime/scratch/.
  Literal paths only as write targets.
- **Commit** your paths only, the trailers in ONE final paragraph (a blank line between them hides `Task:` from git):
  `git commit -m "<subject>" --trailer "Task: DAEO-0cd2" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1092, DEC-1074, DEC-1072, DEC-1156" [--trailer "Rewrite-Reason: DEC-1179 (2)"] --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <your paths>`
  Never `Role: owner` or `Decided-by:`. No merge, no push, no edit of `.tickets/` or the register.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines, red and green counts per KPI) / tests /
discoveries (with the size estimate) / risks / lessons / proposed_decisions / unresolved / recommended_next_action.
Then `commits:` (hash12, subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true
or false-positive).
