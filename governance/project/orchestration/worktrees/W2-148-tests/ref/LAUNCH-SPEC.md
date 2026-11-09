# LAUNCH-SPEC: the independent sessions' launch script (DEC-1101 (3) step 2)

- **For:** the independent test designer who writes its tests first, the engineer who builds it, and its one review.
- **By:** a research agent for the CTO, 2026-11-09, with ACT-INDEP-WALLS-1 (step 1). It builds on that ACT's template
  (`governance/project/indep-walls/`), its path-map entries and its rehearsal. `drafts/indep-walls/build_wall.py` is a
  reference for steps B1 to B6 below, not the script.
- **Name and home (proposed):** `governance/project/orchestration/tools/indep_launch.py` (the CTO's committed tools),
  tests under that ticket's `tests/acceptance/<WBS>/`. The CTO runs it; nobody else needs to.

## 1. Inputs (the command line: nothing else is chosen by the caller)
```
python3 indep_launch.py --sets-root ~/gov-os-eval --kind writer|checker|auditor|labeller \
    --brief governance/project/indep-briefs/<kind>.md --brief-sha256 <64 hex> \
    --commit <commit> --set <set name> [--round 1|2] [--seed new] [--dry] [--counts-only]
```
- **`--sets-root`** only: the line names no folder under it (the guard's line rule, DEC-1097 (2)). The script derives
  `indep-walls/`, the set's folder and the run folders in its own code.
- **`--kind`:** one of the four in `kinds.yaml`.
- **`--brief` and `--brief-sha256`:** the approved brief's path in the repository at `--commit`, and its sha256. Both
  must match: the file's bytes at the commit, and a `brief <kind>` line of `<sets root>/indep-walls/APPROVED` (the owner's
  list, written by the operator only).
- **`--commit`:** resolves to a commit reachable from `w2/integrate` (or the adopted repository's main branch). The
  tree is built at it.
- **The seed:** always drawn by the script (`--seed new`, 63 random bits). A given seed is accepted only with `--dry`
  (a test of reproducibility); a real run never takes a seed from the caller.
- **The content rule** (not an input): the paths changed between the last audit's commit (the last line of
  `~/gov-os-runs/indep/AUDITS.log`, written by the script, never by hand) and `--commit`, plus a sample of N older
  tracked paths drawn with the seed. N comes from the brief's front matter (`sample:`); none from the caller.

## 2. What it builds (in this order; each step refuses on failure and leaves what it made for the record)
- **B0, checks before anything is written:** every template file's sha256 equals its `template` line in `APPROVED`;
  the brief's sha256 as in §1; `APPROVED` itself hashes to the value printed in the owner's approval record (the
  script prints `approved_sha256` in every result, so any change shows); the hidden part's file count under the sets
  root (the guard's walk counts it, cap 10,000) plus this run's expected files is at most **8,000**.
- **B1, an empty wall:** `<sets root>/indep-walls/<kind>/<run>/` where `<run>` is `<UTC yyyymmddThhmmssZ>-<set>-r<round>`.
  It must not exist (or be an empty folder); `~/gov-os-wall-trees/<kind>-<run>/` must not exist.
- **B2, the seed first:** `seed.txt` (mode 0444) written and hashed, and one line appended to
  `~/gov-os-runs/indep/SEEDS.log` (time, kind, run, commit, the seed, its sha256), **before** any content is chosen
  or any tree is built.
- **B3, the plain tree:** `git archive <commit>` less `tree-exclude.txt`, unpacked into
  `~/gov-os-wall-trees/<kind>-<run>/`; a link, an absolute path or a `..` in the archive refuses; every file 0444,
  every folder 0555; no `.git`.
- **B4, the input by rule:** `input/selection.json` (the commit, the last audit's commit, the seed's sha256, the changed
  paths, the sample), then the kind's staged copies (read-only): writer round 2 its own round-1 set and the checker's
  notes; checker the set; auditor the set and the measured misses; labeller the rulebook and its actions (the second
  labeller's 10 % overlap drawn with the seed). Copies only; the session never reaches the sets root.
- **B5, the session's files:** `brief.md` (the approved bytes), `CLAUDE.md` and `.claude/settings.json` from the
  template (the other walls present at build time named in its deny list), `.claude/wall_hook.py`; `out/` empty (0700);
  the wall's root, `.claude/` and `input/` read-only.
- **B6, the manifest:** `WALL.json`: kind, run, set, round, commit, repo, tree, the sha256s of brief, seed, settings,
  hook, every template file and `APPROVED`, the selection's counts, and `seeded_before_content`.

## 3. How it launches
- **The canary (before the real session):** a one-turn session in the wall with the same flags and the cheapest model,
  told to Read one file the script plants outside the wall (in its own temporary folder). It must come back with that
  Read in `permission_denials`. Otherwise the wall's settings did not load (`-p` ignores a settings file that fails
  validation, without a word) and the script refuses. Cost about $0.005 (the rehearsal's sessions: $0.004–0.005).
- **The session:** from the wall, with a clean environment (`env -i` with `HOME`, `PATH`, `LANG`, `USER` only: no
  `GOV_*`, no `CLAUDE_PROJECT_DIR`), in its own process group, its pid recorded, waited on by pid (L-0075):
  ```
  timeout --kill-after=30 <timeout_s> claude -p --restricted --settings <wall>/.claude/settings.json \
      --add-dir <tree> --tools <the kind's tools> --no-session-persistence --strict-mcp-config \
      --disable-slash-commands --permission-prompts none --model <model> --max-budget-usd <budget_usd> \
      --output-format json "<the fixed launch prompt>" < /dev/null > <wall>.session.json
  ```
  The fixed launch prompt is one line: follow `brief.md` exactly and finish by writing `out/result.json`. It holds no
  content of its own, and its sha256 is a constant in the script. `--tools`, the budget, the timeout and the model come
  from `kinds.yaml` and the brief's front matter, never from the caller.
- **No tools beyond the brief's:** the kind's list (`Read, Grep, Glob, Write, Edit, TodoWrite` at most). Never Bash,
  WebFetch, WebSearch, Task or MCP. The wall hook refuses everything else anyway.
- **The session's own output** (`<wall>.session.json`, beside the wall, inside the hidden part) is read by the script
  for numbers only (exit, `is_error`, turns, cost, duration, `permission_denials` by tool name). Its text never leaves.

## 4. What returns to the CTO: counts and digests only, in a fixed schema
`~/gov-os-runs/indep/<kind>/<run>/counts.json`, also printed, validated against `indep-counts.schema.json`
(`additionalProperties: false`, every value a number, a boolean, a sha256 or one of a fixed set of words: no free
text):
- `act`, `kind`, `run`, `set`, `round`, `commit`;
- `brief_sha256`, `approved_sha256`, `template_ok`, `seed_sha256`;
- `selection`: `changed`, `sample`;
- `session`: `exit`, `is_error`, `turns`, `cost_usd`, `duration_s`, `refusals` (per tool name: a count);
- `out`: `schema_ok`, `files`, and the kind's counts: writer `questions` (by `kind` and by `area` from fixed lists);
  checker `checked`, `accepted`, `revise`, `rejected`; auditor `misses` by class (the brief's fixed classes); labeller
  `labelled`, `allow`, `refuse`, and, for the overlap, `agree`, `disagree`;
- `delivered`: `files`, `sha256` (of the delivered bundle), `to` (a fixed word: `set`, `notes`, `classes`, `labels`);
- `traces`: the count of files under `~/.claude` for the session id (must be 0);
- `status`: `delivered` | `rejected` | `refused` | `stopped`.

`out/result.json` must pass the kind's schema. Only its numeric fields are copied into `counts.json`; every other
field stays in the wall. The delivery (writer's set, checker's notes, auditor's classes, labeller's labels) is copied
by the script's code from `out/` to its place under the sets root (for the labellers the sealed folder,
`fixtures/evaluation/sandbox-guard-exp-1/hidden/labels/<run>.jsonl`). The session never writes there itself
(ACT-SANDBOX-SEAL-1 §3 (2) met through the script).

**After the run:** the wall (less nothing) is packed into `indep-walls/<kind>/<run>.tar` (0400, one file) and its folder and
tree removed, so the hidden part grows by one file per run; `AUDITS.log` gains the commit once an audit's last job is
delivered.

## 5. How it refuses (exit codes; nothing launched; the reason printed with the counts schema's `status: refused`)
| Code | Refusal |
|---|---|
| 10 | the brief's sha256 differs from `--brief-sha256`, or has no `brief <kind>` line in `APPROVED` |
| 11 | a template file's sha256 differs from its `APPROVED` line |
| 12 | the wall exists and is not an empty folder, or its tree folder exists |
| 13 | the seed was not recorded first: no `SEEDS.log` line for the run, or `seed.txt` is newer than `input/selection.json` |
| 14 | the commit does not resolve, or is not reachable from the main line |
| 15 | the hidden part's file budget (8,000) would be passed |
| 16 | the canary's Read was not refused (the settings did not load) |
| 17 | a caller-given seed without `--dry`, or an argument naming a folder under the sets root |
| 20 | `out/result.json` missing or failing its schema: `status: rejected`, nothing delivered |
| 21 | the budget or the timeout stopped the session: `status: stopped`, nothing delivered |
| 22 | a trace of the session under `~/.claude`: reported and counted |

## 6. KPIs (for the independent test designer; each with its Verify line)
- **S1. The brief is the approved one.** A launch whose brief's bytes, `--brief-sha256` and the `APPROVED` line do
  not all agree refuses with code 10 and builds nothing. *Verify:* three launches (altered byte, wrong hash argument,
  line removed) in a planted sets root; exit 10; `indep-walls/<kind>/` unchanged; no tree folder; no `SEEDS.log` line.
- **S2. The template is the approved one.** One changed byte in any of the six template files refuses with code 11.
  *Verify:* six launches, one per file; exit 11 each; nothing built.
- **S3. A wall is built only into nothing.** A wall folder holding any entry, or an existing tree folder, refuses with
  code 12 and leaves both untouched. *Verify:* plant one file in the wall; plant the tree folder; exit 12; the planted
  entries' hashes unchanged.
- **S4. The seed comes first.** `seed.txt` and its `SEEDS.log` line exist before any tree or input file: `seed.txt`'s
  mtime is earlier than every file under `input/` and the tree, and the ledger line's sha256 equals `seed.txt`'s.
  *Verify:* build one wall; compare mtimes (ns) and hashes; a forced reordering (a test hook writing `input/` first)
  refuses with code 13.
- **S5. The content is chosen by rule.** `selection.json` equals the rule's result: `git diff --name-only <last audit>
  <commit>` less the exclusions, plus `random.Random(seed).sample` of the rest, sized by the brief. The same seed and
  commit give the same selection; the caller cannot pass paths. *Verify:* two `--dry` builds with one seed: identical
  selections; recompute independently; no argument accepts a path list.
- **S6. The caller cannot choose the seed.** A real run with `--seed <n>` refuses with code 17. *Verify:* exit 17,
  nothing built.
- **S7. The tree is plain and read-only.** The tree is the archive at the commit less `tree-exclude.txt`: no `.git`, no
  link, no excluded path, every file 0444, every folder 0555, outside the sets root. *Verify:* walk it; compare with
  `git ls-tree` less the exclusions (count and per-file hash).
- **S8. The wall's settings are the template's.** `.claude/settings.json` equals the template filled for this wall,
  its sha256 is in `WALL.json`, its deny list holds every required class (the shell, the web, subagents, memory's search,
  git, the repository, the worktrees, the run outputs, `~/.claude`, the rest of the sets root, `APPROVED`, the other
  kinds and the walls present at build time), and its one hook is the wall's own. *Verify:* `walls_check.py wall`'s F
  checks on a built wall.
- **S9. The canary guards the settings.** With a settings file made invalid on purpose, the canary's Read is not
  refused and the launch refuses with code 16 before the real session. *Verify:* corrupt one key in a test wall; exit
  16; the session never started (no `<wall>.session.json`).
- **S10. The session is headless and closed.** The launched command carries `-p --restricted --settings <wall's>
  --add-dir <tree> --tools <the kind's> --no-session-persistence --strict-mcp-config --disable-slash-commands
  --permission-prompts none --max-budget-usd <kind's>`, under `timeout`, from the wall, with no `GOV_*` and no
  `CLAUDE_PROJECT_DIR` in its environment. *Verify:* run with a stub `claude` on `PATH` that records its argv, cwd
  and environment.
- **S11. The walls hold in a live session.** A live session in a built wall (the cheapest model) told to read each of
  a fixed list of outside targets (another wall, another wall's tree, `APPROVED`, a hidden set file, the sealed folder,
  a run folder, the transcripts folder, the seed ledger, the CTO's scratch, the repository) makes every attempt and
  each is refused; it reads its own brief and tree; no outside marker appears in `out/` or its output; nothing is
  written outside `out/`. *Verify:* the rehearsal's `live_sessions` step, as a test (marked live).
- **S12. No trace is left.** After a session, no file under `~/.claude/{projects,file-history,session-env,todos}`
  names its session id. *Verify:* names-only search by session id after S11's run: 0.
- **S13. Only counts return.** `counts.json` validates against `indep-counts.schema.json` (no free text: every string
  a sha256, a fixed word or the run's id); a planted `out/result.json` carrying a question's text in an extra field
  leaves no trace of that text in `counts.json`, the printed output or the script's log. *Verify:* plant the marker
  text; grep the three: 0.
- **S14. A bad result is not delivered.** An `out/result.json` that is missing or fails its schema gives `status:
  rejected`, exit 20, nothing written under the set's folder or the sealed folder. *Verify:* hashes of the destination
  folders before and after.
- **S15. Budget and timeout stop it.** A session past its timeout is stopped by process group, gives `status:
  stopped`, exit 21, nothing delivered; the budget flag is always present. *Verify:* a stub `claude` that sleeps; the
  pid group gone afterwards (by pid, never a name match).
- **S16. The delivery lands only where the kind delivers.** A writer's `out/set/**` lands in
  `fixtures/evaluation/<set>/hidden/`, a labeller's `out/labels.jsonl` in the sealed folder's `labels/<run>.jsonl`, and
  nothing else changes under the sets root; `delivered.sha256` equals the bundle's hash. *Verify:* hash the sets root's
  tree (planted) before and after.
- **S17. A finished wall is one file.** After delivery the wall is packed into `indep-walls/<kind>/<run>.tar` (0400), its
  folder and its tree are gone, and the hidden part's file count has grown by exactly one. *Verify:* count before and
  after.
- **S18. The hidden part's file budget holds.** With the planted hidden part at 7,990 files, a launch that would add
  more than 10 refuses with code 15. *Verify:* plant the files; exit 15.
- **S19. The CTO's line passes the guard.** Every documented command line of the script (one per kind, `--dry`,
  `--counts-only`) is allowed for the orchestrator by the live hook, and the same line naming `indep-walls/...` after the root
  is refused. *Verify:* `walls_check.py repo`'s W5/W6 classes, extended with the script's real lines.
- **S20. The second labeller's overlap is by the seed.** The overlap set is 10 % of the first labeller's actions
  (rounded up), drawn with the second run's seed, identical on a re-draw with that seed, and no other input differs
  between the two labellers. *Verify:* two `--dry` builds; compare.
- **S21. Waits and stops by pid.** The script records the session's pid and pgid in the run's counts folder and waits
  and stops only by them. *Verify:* a code search for name-matched kills (`pkill`, `killall`, `pgrep -f`): none; the
  stop path tested with S15.

**Failure lines (the script's own):** a refusal never leaves a half-built wall that a later run could build into (S3
holds after every refusal code); a delivery is all or nothing (copy to a temporary name, hash, rename); the script never
prints a path under the wall other than its run id.
