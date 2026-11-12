# Brief eng-1: engineer for DAEO-qz4p (W2-173), profile FULL, class C3

You implement ticket DAEO-qz4p (W2-173): the launch script's follow-ups for the memory audit. An independent test
designer writes the acceptance tests (tests/acceptance/W2-173/) in parallel; you never read them (the guard refuses
the counterpart's work). Write your own unit tests as you go (test first).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-173 |
| branch | w2/W2-173 |
| allowed paths | governance/project/orchestration/tools/indep_launch.py, governance/project/orchestration/tools/indep-schemas/**, tests/unit/orchestration/test_w2_173*, docs/changes/W2-173-evidence.md |
| ticket (read it first; KPI lines S1-S5 and F1-F4 are the spec) | /home/usain/gov-os-worktrees/W2-173/.tickets/DAEO-qz4p.md |
| base of the script (S5: nothing else changes) | `git diff 2f98aecbc -- governance/project/orchestration/tools/indep_launch.py` must show only the four changes |
| the fixed forms (read-only) | governance/project/indep-briefs/memory-audit/checker.md §6-§7, auditor.md §6-§7 (never write under indep-briefs/ or indep-walls/) |
| W2-149's unit and acceptance tests (they must still pass unchanged) | tests/unit/orchestration/test_w2_149_*.py, tests/acceptance/W2-149/ |
| the sources (read by id in docs/DECISION_REGISTER.md) | DEC-1101, DEC-1120, DEC-1112, DEC-1113, DEC-1050, DEC-1073 |

Search with Read, Grep and Glob; search once more in other words if the first does not answer (DEC-1065).

## The interface (as the ticket states it; the lead's reading where marked)
- **S1 effort.** Front matter `effort:` one of `low`, `medium`, `high`, `xhigh`, `max` (constant beside the others).
  Validate at stage 10 (`front_matter`/`resolve_brief` path) before anything is built: any other value (or a
  non-string) refuses 10 (`brief`) and the walls folder is untouched. Pass `--effort <value>` to the session (in
  `session_flags` or where the argv is built; the canary too only if that is the natural place — keep the canary's
  behaviour otherwise as at 2f98aecbc); no `effort` line: no `--effort` flag at all. Record it in `WALL.json` and as
  one top-level `effort` field (string or null) in every counts object (refusals before the brief is read: null);
  add `effort` to `indep-counts.schema.json` (`"type": ["string","null"], "enum": [the five, null]`) and to its
  `required` only if every counts path the script writes carries it (it should: the counts object is built in one place).
  The five set-up A briefs (no `effort`) must still pass stage 10 and build dry walls unchanged.
- **S2 stopped, memory writer and checker only.** `writer-result.schema.json` and `checker-result.schema.json` gain an
  optional `stopped` property, `enum` of the seven `STOPPED` words. In `check_result` (non-set-up-A path, kinds writer
  and checker): when result.json reads as a JSON object whose `stopped` is one of the six words other than `none`,
  copy the word to `counts["out"]["stopped"]` and end 21 (`stopped`, status `stopped`) with nothing delivered — before
  the schema check, the numbers and the out/ files' checks, so a stopped result never ends 20. `none` or absent: as
  today. A `stopped` outside the seven: schema refusal 20. Set-up A flows keep their own handling exactly (a stopped
  set-up A result still ends 20, line ~1806): do not touch it. The auditor kind is not in S2.
- **S3 the checker's notes.** Before delivering `XCHECK-r<n>.md`, check `out/notes.md` (UTF-8): line 1
  `# Cross-check notes`; then `## Questions`; then exactly one line per file of the staged `input/set/` (the ids = the
  set's file stems, e.g. `q01` for `q01.yaml`) in id order, each `<id> | accept|revise|reject | <codes or -> | also:
  <...> | <sentence>`: five fields split on ` | `, field 2 one of the three words, field 3 `-` or non-empty, field 4
  starts `also:`, field 5 non-empty; then `## The set`; then its five lines, starting in order `domains:`,
  `categories:`, `keyword:`, `supersession `, `set codes:` (the lead's reading of checker.md §6); nothing else but a
  trailing newline (tolerate blank lines between sections only if you judge the brief's form allows it; say which in
  the evidence). `result.json`'s `accepted`, `revise`, `rejected` must equal the three words' counts (and `checked` the
  line count). Anything else: Refuse(20, ...) with nothing written to the set's folder.
- **S4 the auditor's classes (memory auditor; NOT set-up A's overlap auditor, whose delivery is unchanged).** Before
  delivering `miss-classes.json`, check `out/classes.json`: a JSON object with exactly one key per line of the staged
  `input/misses.jsonl` (the ids those lines carry: read the auditor brief §2 for the line's form), no other key; each
  value an object with `class` in `MISS_CLASSES` and `reason` a string of one line (no `\n` or `\r`), at most 200
  characters; the five `misses` counts in result.json equal the classes' counts. Anything else: Refuse(20, ...), no
  `miss-classes.json`, no `AUDITS.log` line, the audit's folder byte-identical.
- **S5.** No other change to the script: every exit code keeps its meaning; the existing 21 code and `stopped` reason are
  reused, not redefined. Update the module docstring's lines for these four changes only. Do not touch the walls'
  template, the path map, the guard, the approved list, any brief.

## Rules
- Unit tests in tests/unit/orchestration/test_w2_173_*.py, planted folders under tmp_path, a stub `claude` on PATH;
  never the real ~/gov-os-eval, ~/gov-os-runs, ~/.claude, any hidden folder, or a real walled session.
- Before you return, run W2-149's suites and yours, whole-folder form:
  `env HOME=/home/usain/gov-os-worktrees/W2-173/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-173/src python3 -m pytest <folder or files> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  for tests/acceptance/W2-149, tests/unit/orchestration/test_w2_149_*.py and your test_w2_173_*.py. W2-149's
  acceptance count at the merge was 206 passed, 0 failed, 3 skipped; report yours.
- Write docs/changes/W2-173-evidence.md: each KPI line, what implements it (function names), the test that shows it,
  and the S5 diff summary (`git diff --stat 2f98aecbc -- governance/project/orchestration/tools/`).
- Commit in small batches (the lead merges the tests between them; never edit while a merge is announced), your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-qz4p" --trailer "Role: engineer" --trailer "Implements: DEC-1101, DEC-1120, DEC-1112, DEC-1113" -- <your paths>`
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-173/.gov-runtime/scratch/;
  literal paths as write targets. Never touch .gov-runtime/scratch/lead/.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (pytest summary lines per suite) / tests / discoveries / risks / lessons /
proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
