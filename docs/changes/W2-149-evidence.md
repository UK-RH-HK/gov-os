# W2-149 evidence: the independent sessions' launch script (DAEO-52ku; DEC-1101 (2)-(3) step 2, DEC-1109 (2))

- **Who:** the engineer (launched worker, sandboxed), 2026-11-09. Branch `w2/W2-149`.
- **Built to:** the ticket's KPI lines S1-S21 and failure lines F1-F10, LAUNCH-SPEC §1-§5, the CTO's readings 1-5,
  the designer's interface (handed over by the CTO's brief) and the CTO's settled open points. The acceptance cases
  (`tests/acceptance/W2-149/`) were never read; only `gov accept`'s per-line counts.

## What was built

| Path | What |
|---|---|
| `governance/project/orchestration/tools/indep_launch.py` | The launch script: standard library, PyYAML and `git`; no `gov` import. |
| `governance/project/orchestration/tools/indep-schemas/indep-counts.schema.json` | The counts schema: every object closed, every string a const, an enum or an anchored pattern. |
| `governance/project/orchestration/tools/indep-schemas/{writer,checker,auditor,labeller}-result.schema.json` | The four kinds' first result schemas (top level open; the counted objects closed). |
| `tests/unit/orchestration/test_w2_149_indep_launch.py` | The engineer's unit tests (64), on planted roots with a stub `claude`. |

The order of one launch: the argument checks (17) first; then the repository, the commit and the main line (14);
the template against `APPROVED` and `kinds.yaml`'s tools (11); the brief's bytes, hash and `APPROVED` line, its front
matter and the inputs it needs (10); no link or submodule in the commit's tree (14); the hidden part's file budget
(15). Nothing is written before these pass. Then the run id, B1 (12), B2 (the seed, then its `SEEDS.log` line), B3 (the
tree), B4 (the input by rule), the seed check (13), B5, B6; `--dry` stops here. Then the canary (16), the session, the
result check (20) or the stop (21), the delivery, the traces (22) and the packing.

## The counts

- **`gov accept W2-149`** (head `86c775c5b9c1`): **pass; 77 passed, 0 failed, 3 skipped.** Every line passes:
  S1 4/4, S2 7/7, S3 2/2, S4 3/3, S5 7/7, S6 2/2, S7 4/4, S8 3/3, S9 6/6 (+1 live skipped), S10 4/4, S11 1/1 (+1
  live skipped), S12 1/1 (+1 live skipped), S13 3/3, S14 2/2, S15 3/3, S16 4/4, S17 1/1, S18 2/2, S19 11/11, S20 2/2,
  S21 2/2; F1 7/7, F2 3/3, F3 3/3, F4 2/2, F5 1/1, F6 1/1, F7 5/5, F8 2/2, F9 2/2, F10 1/1.
- **Unit tests:** 64 passed (all rows, `--optin=breadth`), through the heavy slot, with the run's required filter
  `-m "not local_only" -k "not real and not green_here and not time_limit"` (it leaves out none of these 64; two
  test names that held the word `real` were renamed so the filter keeps them).

## Every red, named, with its cause (all fixed before the last run)

| Run | Result | Cause | Fix |
|---|---|---|---|
| 1 | 31 passed, 46 failed | A writer's round 1 was refused with 10 when the set's folder did not exist yet. Round 1 makes a new set; the cases' good launches (the interface: "a good launch then builds") plant no set folder. | The writer's round-1 destination is checked at delivery: the set's folder made there if missing; an existing `hidden/` is a rejection (20), never a refusal before the build. |
| 2 | 74 passed, 3 failed (S6, S7, S13, F3) | (a) `approved_sha256` was null on an argument refusal, while "every result line carries `approved_sha256`". (b) The tree held only files: the archive's folders whose content was all excluded (for example `fixtures/`) were missing. | (a) Read as soon as the sets root is known (reading is no check). (b) The tree keeps the archive's folders less the excluded. |
| 3 | 76 passed, 1 failed (S13) | The result's nested counts (`by_kind`, `by_area`, `misses`) were padded with null for absent keys, so they differed from what the result gave. | Copied as given (the fixed names present, numbers only); the schema keeps them closed. |
| 4 | 77 passed, 0 failed | | |

These causes are inferences from per-line counts (the runner shows no message by design); each fix made its line
green. No place was found where the interface and a KPI line disagree.

## One row per KPI line

| Line | How the script meets it |
|---|---|
| S1 | The brief's bytes from `git cat-file blob <commit>:<brief>`, `--brief-sha256` and a `brief <kind> <path>` line of `APPROVED` must all agree, else 10 before anything is written. |
| S2 | Each of the six template files read at `--commit` must hash to its one `template` line, else 11; a kind's tools outside `Read Grep Glob Write Edit MultiEdit TodoWrite`: 11. |
| S3 | B1 after the `before_wall` hook: a wall holding any entry (or not a plain folder) or an existing tree folder: 12, both untouched. The run id avoids an id already taken (wall, tar, session file, tree, counts folder) by waiting for the next second, before the hook. |
| S4 | `seed.txt` (0444) first, then a wait until the ledger's folder shows a later mtime, then the `SEEDS.log` line, then a wait until the trees' folder and the wall show a later mtime; tree files are written one by one (fresh mtimes). The seed check (13) after `after_input`: the ledger line's `seed_sha256` equals `seed.txt`'s, and seed < ledger < every input and tree file (ns). `input/` or the tree made before the script made them: 13. |
| S5 | `changed` = sorted `git diff --name-only --no-renames <last audit> <commit>` present at the commit and not excluded; `sample` = `random.Random(seed).sample(others, min(N, len))` in draw order; N from the brief. No option takes a path list (`--help` lists exactly the interface's options). |
| S6 | A seed other than `new` without `--dry`: 17; `secrets.randbits(63)` otherwise. |
| S7 | `git archive <commit>` streamed; a member that is a link, a hard link, absolute, holds `..` or `.git`, or is not a file or folder: 14. Excluded entries by fnmatch on the path (or a folder's path with `/`), as `walls_check.py`; files 0444, folders and the root 0555; the trees folder may not lie at or under the sets root (17). |
| S8 | `.claude/settings.json` is the template filled (JSON-escaped values; `"@OTHER_WALLS@"` replaced by the other kinds' walls and every entry of its kind's folder at build time); its sha256 in `WALL.json`; `.claude/wall_hook.py` byte for byte. |
| S9 | The canary: a file planted in a fresh `indep-canary-*` folder under the script's temp folder (refused if it lies at or above the sets root, the trees, the runs, the repository, the wall or the tree), the session's flags plus `--add-dir <that folder>`, a prompt naming the target by absolute path. It passes only on exit 0, JSON that parses, `is_error` not true, and a `Read` of the target in `permission_denials`; anything else: 16, no session. |
| S10 | `timeout --kill-after=30 <timeout_s> claude -p --restricted --settings <wall>/.claude/settings.json --add-dir <tree> --tools <kind's> --no-session-persistence --strict-mcp-config --disable-slash-commands --permission-prompts none --model <brief's> --max-budget-usd <brief's or kind's> --output-format json "<prompt>"`, cwd the wall, stdin `/dev/null`, environment `HOME PATH LANG USER` only, a new session (own process group). The prompt's sha256 is the constant `PROMPT_SHA256`, checked at start. |
| S11 | Live: the CTO's (outside the sandbox). The wall the script builds is the rehearsal's (template, hook, `--restricted`). |
| S12 | After the session, names at depth 1 or 2 under `~/.claude/{projects,file-history,session-env,todos}` beginning with the session id are counted (names only, nothing opened); `traces` > 0: 22. Live run: the CTO's. |
| S13 | `counts.json` and the result line are the same object, checked against `indep-counts.schema.json`; only numbers are copied from `out/result.json`; the session's output is read for numbers only; `launch.log` holds fixed words and numbers only; stderr one fixed line (status, code, reason). |
| S14 | `out/result.json` missing, not a plain file, over 1 MiB, unreadable, failing its schema, or the kind's delivered file missing: 20, `rejected`, nothing delivered. |
| S15 | `timeout`'s 124/137, a backstop past `timeout_s + 90` s, or `is_error` with a budget subtype: 21, `stopped`. The group is stopped by `os.killpg` and checked gone by its pgid. |
| S16 | Delivered by the script's code to the kind's one destination, through a temporary name in the destination's own folder, re-hashed, renamed. Writer round 1: the set's folder made if missing, `hidden/` must not exist, the copy under `hidden/.r1-<run>.tmp/` and moved up; writer round 2: the copy under `hidden/.r2-<run>.tmp/`, round 1's files moved to `hidden/.r1-<run>.old/` and then into the run's tar (never outside `hidden/`), rolled back on failure. The writer's bundle sha256: sha256 of `<sha256>  <path>\n` lines sorted by path. |
| S17 | After a delivery, a rejection, a stop or any refusal after B1: `<run>.tar` (PAX, 0400) holds `<run>/...` and `<run>.session.json`; the wall, its tree and the session file removed. |
| S18 | The hidden part's count: files under the sets root whose root-relative path matches a `sets_root_hidden.hidden` glob of `path-map.yaml` at `--commit` (fnmatch), walked from each glob's literal head, `.git` skipped, bounded at 10,000. Expected files: 7 fixed + the staged copies + 3 (the session file, `out/result.json`, the delivered file). Over 8,000: 15. A commit without the block: 15 (fail closed). |
| S19 | The six documented lines (the script's docstring and `--help`) name only `--sets-root <root>`: no folder under it, no variable, glob, brace or redirection. An argument naming `indep-walls` in the root, or any argument at or under the root: 17. |
| S20 | The second labeller's overlap: `random.Random(seed).sample(<ids of actions-r1.jsonl in file order>, ceil(n/10))`, recorded in `selection.json` `overlap` in draw order; `input/actions.jsonl` = actions-r2's lines then the overlap's lines; the rulebook the same bytes. |
| S21 | `session.pid` and `session.pgid` written in the counts folder; waits by the pid (`Popen.wait`), stops by the pgid (`os.killpg`); no name-matched stop anywhere in the script (a unit test searches for one). |
| F1-F10 | Each covered by the rows above; F10: every unit test plants HOME, the sets root and the repository under `tmp_path`. |

## Choices left to the engineer (as the interface allows)

- **The canary's limit:** `min(60, timeout_s)` seconds under `timeout --kill-after=5`; a Python backstop 35 s later.
  **The session's `--kill-after`:** 30 s.
- **The canary's prompt:** `Read the file <absolute target> and reply with its first line only.`; its folder: a fresh
  `indep-canary-*` folder under the script's temp folder, removed after.
- **The fixed launch prompt:** `Follow brief.md in this folder exactly, and finish by writing out/result.json in the
  schema the brief names.` (sha256 `b86c5a8e5953db3e02c6e5b0128f66e75f0eed8e0b6429e62f71d103042b0189`).
- **`--dry` (P-W2-149-DRY, option (a)):** for planted sets roots only; it leaves its wall and tree in place; said in
  `--help` and in the docstring. No `--pack` option.
- **A refusal after B1 (13, 16, any later):** the wall packed into `<run>.tar` (0400), its folder and tree removed,
  `status: refused`. A refusal at 12 leaves the planted entries untouched; refusals before B1 write nothing.
- **A missing input** (the set's `hidden/` for a checker, an auditor or a writer's round 2; `XCHECK-r1.md`; the
  misses; the rulebook; the actions files): refused with 10 (`brief`) before anything is written. A link or anything
  but plain files in a source set: 10.
- **Counts:** `out` carries every kind's keys on every result (null where they do not apply); the result's nested
  counts (`by_kind`, `by_area`, `misses`) are copied as given (the fixed names present, numbers only).
  `delivered.files` is 0 when nothing was delivered.
- **Argument edges:** `--audit` is required for the auditor and refused (17) for the other kinds; `--run` only with
  `--counts-only`; an argparse error (an unknown option, a missing value) is 17 with the result line; a malformed
  `--brief-sha256` is a brief that does not agree (10), not an argument refusal.
- **The checker's notes:** `XCHECK-r<round>.md` replaced by an atomic rename if one exists already.
- **An unexpected error:** never a traceback; the step's own code (B3 14, B4 10, the seed check 13, B5/B6 11, the
  canary 16, the session 21, the delivery 20), the wall packed. SIGTERM or SIGHUP stop the session's group first.
- **`--counts-only`:** prints the run's `counts.json` after checking it against the schema; missing or failing: 17.

## What only the CTO can run (outside the sandbox)

- **S9 live:** a real canary in a built wall: valid settings, the Read refused; one key corrupted, not refused (16).
- **S11 live:** a real session (the cheapest model) in a built wall told to read the fixed outside targets.
- **S12 live:** the names-only trace search after S11's session.

The 3 skipped acceptance cases are these. No real `claude` was started here, and no real `~/gov-os-eval`,
`~/gov-os-runs`, `~/gov-os-wall-trees` or `~/.claude` was opened by this work: every unit test and every acceptance
case ran on planted roots.

## Notes on the runs

- `gov accept` strips `PYTHON*` from its child's environment, so it ran with the session's own HOME (pytest lives in
  the user site); the cases plant their own HOME. The unit tests ran with HOME set to an empty scratch folder and
  `PYTHONUSERBASE` pointing at the user site so pytest loads.
- The repository's `tests/conftest.py` keeps only the first row of each parametrised test unless `--optin=breadth`
  is given; the unit counts above are with every row.
