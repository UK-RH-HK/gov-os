# Brief td-1: independent test designer for DAEO-qz4p (W2-173), profile FULL, class C3

You are the independent test designer (MR-3) for ticket DAEO-qz4p (W2-173): the launch script's follow-ups for the
memory audit. You write the acceptance tests from the ticket's KPI lines, before the engineer's code exists. You never
read the engineer's work on this ticket (its branch w2/W2-173 after this brief, its unit tests `tests/unit/orchestration/test_w2_173*`).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-173-tests |
| branch | w2/W2-173-tests |
| your allowed paths | tests/acceptance/W2-173/** |
| ticket (read it first; the KPI lines S1-S5 and F1-F4 are the spec) | /home/usain/gov-os-worktrees/W2-173-tests/.tickets/DAEO-qz4p.md |
| the script under test (read its CLI, docstring, exit codes and constants; do not test its internals) | governance/project/orchestration/tools/indep_launch.py |
| W2-149's acceptance tests: reuse their planting helpers (import them, never copy-edit them) | tests/acceptance/W2-149/w2_149_support.py, w2_149_setup_a.py and the test_w2_149_*.py files |
| the fixed forms (read-only; never write under indep-briefs/ or indep-walls/) | governance/project/indep-briefs/memory-audit/checker.md §6 and §7; governance/project/indep-briefs/memory-audit/auditor.md §6 and §7 |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1101, DEC-1120, DEC-1112, DEC-1113, DEC-1050, DEC-1073 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words, then
answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## The interface (as the ticket states it; the lead's reading where marked)
- **S1 effort.** A brief's front matter may carry `effort:` one of `low`, `medium`, `high`, `xhigh`, `max`. The stub
  `claude` on PATH then receives `--effort <value>` (two argv items); with no `effort` line it receives no `--effort`.
  `WALL.json` (in the wall) and `counts.json` record it: counts gain one top-level field `effort`, a string or null
  (null when the brief names none). Any other value: exit 10 (reason `brief`) before anything is built: the walls
  folder under the planted sets root is unchanged (compare a listing/hash of it before and after). The five set-up A
  briefs (no `effort`) still pass stage 10 and build dry walls. The counts schema `indep-counts.schema.json` gains
  `effort`; every counts.json the script writes still validates against it.
- **S2 stopped (memory writer and checker only).** A writer's or checker's `out/result.json` may carry `stopped`, one of
  `none`, `input-missing`, `input-malformed`, `decisions-conflict`, `forbidden-read-needed`, `form-not-writable`,
  `not-sealed`. Any word but `none`: nothing delivered, exit 21, `counts.json` has `status: stopped`, `reason: stopped`
  and the word at `out.stopped` (the counts schema already has `out.stopped` with these words). This holds even when the
  rest of that result or the out/ files would otherwise refuse 20 (missing set, missing notes). `none` with a good set
  or notes delivers as before. `writer-result.schema.json` and `checker-result.schema.json` gain `stopped` as an
  optional property; a result without `stopped` still validates and delivers. A `stopped` value outside the seven is a
  schema refusal (20). Set-up A's flows are NOT changed: a set-up A result with a stopped word still ends 20 as at
  W2-149 (S5) — do not write a test that expects 21 there.
- **S3 notes form (memory checker).** `out/notes.md` must be, in this order: the line `# Cross-check notes`; the line
  `## Questions`; one line per file of the set staged in `input/set/` in id order, each
  `<id> | accept|revise|reject | <codes or -> | also: <...> | <sentence>` (five `|`-separated fields); the line
  `## The set`; then its five lines (lead's reading of checker.md §6: lines starting `domains:`, `categories:`,
  `keyword:`, `supersession `, `set codes:`). The result's `accepted`, `revise`, `rejected` equal the counts of the
  three words in the lines. Anything else: exit 20, nothing written to the set's folder (no `XCHECK-r<n>.md`; the
  set's folder byte-identical before and after). Test only what S3's Verify names (well formed delivered; a missing
  line; a fourth verdict word; an id not in the set; counts that disagree) — do not test codes' or sentences' inner syntax.
- **S4 classes form (memory auditor, not the set-up A overlap auditor).** `out/classes.json` is an object
  `{"<id>": {"class": ..., "reason": ...}}` with exactly one key per line of `input/misses.jsonl` (its ids), each
  `class` one of `gold_wrong`, `question_ambiguous`, `retrieval_miss`, `answer_wrong`, `out_of_scope`, each `reason` a
  single line (no newline) of at most 200 characters, and `result.json`'s five `misses` counts equal the classes'
  counts. Anything else: exit 20, nothing delivered (no `miss-classes.json`, no new `AUDITS.log` line; the audit's
  folder byte-identical before and after).
- **S5 and F3/F4.** W2-149's acceptance cases pass unchanged; the script's diff against `2f98aecbc` outside the four
  changes is the reviewer's (do not write a diff-shape test of the script's text). You may write the F3/F4 name check:
  `git diff --name-only <base>...HEAD` lists none of the walls' template files, `governance/project/path-map.yaml`,
  the guard, the approved list or the set-up A briefs, and only paths matched by the ticket's allowed_paths plus
  `tests/acceptance/W2-173/**` (base: the merge-base with `w2/integrate`, or `dac438772` if that is unavailable).

## Rules
- Planted sets root, HOME and repository under pytest's tmp_path, and a stub `claude` on PATH that records its argv;
  never the real ~/gov-os-eval, ~/gov-os-runs, ~/.claude, ~/gov-os-eval hidden folders, or a real walled session.
- Tests must be red now where the KPI is new (S1-S4) and green where it holds today (no-effort and set-up A cases,
  result without `stopped`). Run them and say which are red and why.
- Whole-folder pytest form: `env HOME=/home/usain/gov-os-worktrees/W2-173-tests/.gov-runtime/scratch/empty-home
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-173-tests/src python3 -m pytest tests/acceptance/W2-173 -q -p no:cacheprovider
  -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
  Also run W2-149's acceptance folder the same way once to confirm your imports of its helpers break nothing.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-173-tests/.gov-runtime/scratch/.
  Literal paths only as write targets.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-qz4p" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1101, DEC-1120, DEC-1112, DEC-1113" -- tests/acceptance/W2-173`
- Keep the suite fast (the script's dry/stubbed paths; seconds per case).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines, red and green counts per KPI) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
A question the ticket does not settle: write your reading into the test's docstring and name it in `unresolved`.
