---
id: DAEO-52ku
status: in_progress
deps: []
links: []
created: 2026-11-09T18:55:59Z
type: task
priority: 1
assignee: engineer
external-ref: W2-149
tags: [wave-2, implementation, indep-walls, memory, full]
wbs_id: W2-149
title: 'The independent sessions'' launch script: a walled headless session per job from an approved brief (DEC-1101 (2)-(3) step 2)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- governance/project/orchestration/tools/indep_launch.py
- governance/project/orchestration/tools/indep-schemas/**
- tests/unit/orchestration/test_w2_149*
- docs/changes/W2-149-evidence.md
kpis:
  success:
  - 'S1 The brief is the approved one: a launch whose brief''s bytes at `--commit`, `--brief-sha256` and the `brief <kind>` line of `<sets root>/indep-walls/APPROVED` do not all agree refuses with code 10 and builds nothing. Verify: three launches in a planted sets root (one byte of the brief altered, a wrong hash argument, the line removed): exit 10 each; `indep-walls/<kind>/` unchanged; no tree folder; no `SEEDS.log` line [DEC-1101 (2)-(3)]'
  - 'S2 The template is the approved one: one changed byte in any of the six template files (`settings.json.tmpl`, `wall_hook.py`, `CLAUDE.md.tmpl`, `kinds.yaml`, `tree-exclude.txt`, `README.md`) against its `template` line in `APPROVED` refuses with code 11. Verify: six launches, one per file: exit 11 each; nothing built [DEC-1101 (2)-(3)]'
  - 'S3 A wall is built only into nothing: a wall folder holding any entry, or an existing tree folder, refuses with code 12 and leaves both untouched. Verify: one file planted in the wall; the tree folder planted; exit 12 each; the planted entries'' hashes unchanged [DEC-1101 (2)-(3)]'
  - 'S4 The seed comes first: `seed.txt` (0444) and its `SEEDS.log` line exist before any tree or input file: `seed.txt`''s mtime (ns) is earlier than every file under `input/` and the tree, and the ledger line''s sha256 equals `seed.txt`''s. Verify: build one wall; compare mtimes (ns) and hashes; a forced reordering (a test hook writing `input/` first) refuses with code 13 [DEC-1101 (2)-(3)]'
  - 'S5 The content is chosen by rule: `selection.json` equals the rule''s result: `git diff --name-only <last audit> <commit>` less `tree-exclude.txt`, plus `random.Random(seed).sample` of the other tracked paths, sized by the brief''s front matter (`sample:`); the same seed and commit give the same selection; no argument accepts a path or a path list. Verify: two `--dry` builds with one seed: identical selections; the selection recomputed independently in the test; the argument parser offers no path-list option [DEC-1101 (2)-(3)]'
  - 'S6 The caller cannot choose the seed: a real run with `--seed <n>` refuses with code 17 (a given seed only with `--dry`); a real run''s seed is drawn by the script (63 random bits). Verify: exit 17, nothing built; two real builds draw different seeds [DEC-1101 (2)-(3)]'
  - 'S7 The tree is plain and read-only: the tree is `git archive <commit>` less `tree-exclude.txt`: no `.git`, no link, no excluded path, every file 0444, every folder 0555, outside the sets root; an archive member that is a link, an absolute path or holds `..` refuses. Verify: walk the tree; compare with `git ls-tree -r <commit>` less the exclusions (count and per-file hash); a planted commit holding a symlink refuses [DEC-1101 (2)-(3)]'
  - 'S8 The wall''s settings are the template''s: `.claude/settings.json` equals the template filled for this wall, its sha256 is in `WALL.json`, its deny list holds every required class (the shell, the web, subagents, memory''s search, git, the repository, the worktrees, the run outputs, `~/.claude`, the rest of the sets root, `APPROVED`, the other kinds'' walls and the walls present at build time), and its one hook is the wall''s own (`.claude/wall_hook.py`, byte for byte the template''s). Verify: the built-wall (F) checks of the rehearsal (`walls_check.py wall`''s F class) re-expressed as cases on a built wall [DEC-1101 (2)-(3)]'
  - 'S9 The canary guards the settings: before the real session a one-turn session in the wall, with the same flags, must come back with its Read of a file the script planted outside the wall in `permission_denials`; with a settings file made invalid on purpose the Read is not refused, and the launch refuses with code 16 before the real session. The canary''s target must be one Claude Code''s `--restricted` mode alone would allow (see the CTO''s reading 1), so only the wall''s settings and hook can refuse it. Verify: a stub `claude` modelling Claude Code (a `--settings` file it cannot parse is ignored); exit 16; no `<wall>.session.json`; live (outside the sandbox, the CTO): the real canary with valid settings refused, with one key corrupted not refused [DEC-1101 (2)-(3)]'
  - 'S10 The session is headless and closed: the launched command carries `-p --restricted --setting-sources project --settings <wall''s> --add-dir <tree> --tools <the kind''s> --no-session-persistence --strict-mcp-config --disable-slash-commands --permission-prompts none --model <model> --max-budget-usd <kind''s> --output-format json` and the fixed launch prompt (its sha256 a constant in the script), under `timeout --kill-after`, from the wall, stdin `/dev/null`, with an environment of `HOME`, `PATH`, `LANG`, `USER` only (no `GOV_*`, no `CLAUDE_PROJECT_DIR`); tools, budget, timeout and model come from `kinds.yaml` and the brief''s front matter, never from the caller; never Bash, WebFetch, WebSearch, Task, Agent or an MCP tool; the canary carries `--setting-sources project` too, so the user''s and the local settings files never load into a wall. Verify: a stub `claude` on `PATH` that records its argv, cwd and environment, and that loads a planted user settings file unless `--setting-sources` leaves the user source out [DEC-1101 (2)-(3)] [changed, DEC-1112 (3): F11]'
  - 'S11 The walls hold in a live session: a live session in a built wall (the cheapest model) told to read each of a fixed list of outside targets (another wall, another wall''s tree, `APPROVED`, a hidden set file, the sealed folder, a run folder, the transcripts folder, the seed ledger, the CTO''s scratch, the repository) makes every attempt and each is refused; it reads its own brief and tree; no outside marker appears in `out/` or its output; nothing is written outside `out/`. Verify: the rehearsal''s `live_sessions` step as a test marked live, in planted roots, run by the CTO outside the sandbox [DEC-1101 (2)-(3)]'
  - 'S12 No trace is left: after a session, no file under `~/.claude/{projects,file-history,session-env,todos}` names its session id; `counts.json`''s `traces` is that count. Verify: a names-only search by session id after S11''s run: 0 [DEC-1101 (2)-(3)]'
  - 'S13 Only counts return: `counts.json` validates against `indep-counts.schema.json` (`additionalProperties: false` at every level; every value a number, a boolean, a sha256, a fixed word or the run''s id: no free text); a planted `out/result.json` carrying a marker text in an extra field leaves no trace of it in `counts.json`, the printed output or the script''s log. Verify: plant the marker; grep the three: 0 [DEC-1101 (2)-(3)]'
  - 'S14 A bad result is not delivered: an `out/result.json` that is missing or fails its kind''s schema gives `status: rejected`, exit 20, nothing written under the set''s folder or the sealed folder. Verify: hashes of the destination folders before and after [DEC-1101 (2)-(3)]'
  - 'S15 Budget and timeout stop it: a session past its timeout is stopped by its process group, gives `status: stopped`, exit 21, nothing delivered; the budget flag is always present; a session ended by its budget (`is_error` with the budget''s subtype) also gives `stopped`. Verify: a stub `claude` that sleeps (and one that spawns a child); the process group gone afterwards, checked by pgid, never a name match [DEC-1101 (2)-(3), DEC-1073]'
  - 'S16 The delivery lands only where the kind delivers: a writer''s `out/set/**` in `fixtures/evaluation/<set>/hidden/`, a checker''s `out/notes.md` in `fixtures/evaluation/<set>/XCHECK-r<round>.md`, an auditor''s `out/classes.json` in `runs/<audit>/miss-classes.json`, a labeller''s `out/labels.jsonl` in `fixtures/evaluation/sandbox-guard-exp-1/hidden/labels/<run>.jsonl`; nothing else changes under the sets root; `delivered.sha256` equals the bundle''s hash; the delivery is all or nothing (a temporary name, hashed, renamed). Verify: hash the planted sets root''s tree before and after, per kind [DEC-1101 (2)-(3)]'
  - 'S17 A finished wall is one file: after delivery (or a rejection or a stop) the wall is packed into `indep-walls/<kind>/<run>.tar` (0400), its folder and its tree are gone, and the hidden part''s file count has grown by exactly one. Verify: count before and after [DEC-1101 (2)-(3)]'
  - 'S18 The hidden part''s file budget holds: the hidden part''s file count (the guard''s walk of the sets root''s hidden globs) plus this run''s expected files is at most 8,000, else code 15 before anything is written. Verify: the planted hidden part at 7,990 files: a launch that would add more than 10 refuses with code 15 [DEC-1101 (2)-(3)]'
  - 'S19 The CTO''s line passes the guard: every documented command line of the script (one per kind, `--dry`, `--counts-only`) is allowed for the orchestrator by the tree''s guard hook (`.claude/hooks/pretooluse.py`), and the same line naming a folder under the sets root (`indep-walls/...`) is refused, code 17 from the script too. Verify: the hook driven with each line as an orchestrator Bash event, with a planted HOME and sets root (the rehearsal''s `walls_check.py repo` W5/W6 classes, extended with the script''s real lines) [DEC-1101 (2)-(3), DEC-1097 (2)]'
  - 'S20 The second labeller''s overlap is by the seed: the overlap set is 10 % of the first labeller''s actions (rounded up), drawn with the second run''s seed, identical on a re-draw with that seed, and no other input differs between the two labellers. Verify: two `--dry` builds; compare [DEC-1101 (2)-(3), DEC-1099 (1) Q5]'
  - 'S21 Waits and stops by pid: the script records the session''s pid and pgid in the run''s counts folder and waits and stops only by them. Verify: a code search for name-matched kills (`pkill`, `killall`, `pgrep -f`): none; the stop path tested with S15 [DEC-1101 (2)-(3), DEC-1073]'
  failure:
  - 'A launch that builds or starts anything when the brief''s bytes, its hash argument or its APPROVED line disagree, or when a template file does not match APPROVED (fails open: an unapproved brief or wall).'
  - 'A wall built into a folder that is not empty, or over an existing tree folder; a refusal (any code) that leaves a half-built wall a later run could build into (S3 must hold after every refusal code).'
  - 'Content chosen, or a tree or input file written, before the seed is written and its SEEDS.log line appended; a caller-given seed accepted in a real run; a path or path list accepted from the caller.'
  - 'A real session started when the canary''s Read was not refused, or a canary whose target Claude Code''s restricted mode alone would refuse (so ignored settings still pass it); a canary that errors, times out or cannot be read treated as a pass.'
  - 'A session started with any tool beyond the kind''s, without --restricted, the wall''s --settings, --no-session-persistence, --strict-mcp-config or the budget, from another folder, or with any GOV_* or CLAUDE_PROJECT_DIR in its environment.'
  - 'Free text from the session or out/ reaching counts.json, the printed output or the script''s log; a path under the wall printed other than its run id.'
  - 'A delivery from a missing or schema-failing result, from a stopped session, or partial (some files landed, some not); anything written under the sets root outside the kind''s destination.'
  - 'A wall or tree left in place after the run (the hidden part growing by more than one file per run), or a launch past the 8,000-file budget.'
  - 'A wait or a stop by a name match; a timed-out session whose process group survives.'
  - 'A test or the trial opening the real ~/gov-os-eval, ~/gov-os-runs/indep or ~/gov-os-wall-trees (every test on planted roots).'
profile: FULL
sources:
- DEC-1101
- DEC-1109
- DEC-1099
- DEC-1097
- DEC-1073
- DEC-1057
- DEC-1010
- DEC-820
est_loc: 700
acceptance_tests:
  path: tests/acceptance/W2-149/
  author: 'independent-test-designer (MR-3), from these KPI lines and LAUNCH-SPEC, before the engineer: a planted sets root (APPROVED, set folders, the sealed folder, a hidden part of planted size), a planted HOME, planted repositories with commits, a stub claude on PATH; live cases (S9 live, S11, S12) marked live and kept out of the default run; never the real ~/gov-os-eval, ~/gov-os-runs or ~/.claude'
track: B
list_rows: []
needs: []
waits_on: []
---
# W2-149 The independent sessions' launch script: a walled headless session per job from an approved brief

The owner's DEC-1101 (3) step 2, restarted by DEC-1109 (2): the launch script for the independent writers, checkers,
auditors and labellers (DEC-1101 (2)), tests first, one review. Built on ACT-INDEP-WALLS-1 (applied, `147706ae`): its
template `governance/project/indep-walls/`, the path-map entries and its rehearsal
(`governance/project/orchestration/packages/ACT-INDEP-WALLS-1.md`). The specification is LAUNCH-SPEC (its §1 to §5;
its §6 is these KPI lines), copied into the worktrees as `.gov-runtime/scratch/ref/LAUNCH-SPEC.md`.

- **What is built here:** `governance/project/orchestration/tools/indep_launch.py` (the CTO's committed tool; standard
  library, PyYAML and `git`, no `gov` import), the counts schema and the four kinds' result schemas in
  `governance/project/orchestration/tools/indep-schemas/`, the engineer's unit tests, and the evidence record.
- **What is not built here:** the four fixed briefs (DEC-1101 (3) step 3, to the owner) and their `brief <kind>`
  lines in `APPROVED` (the operator's); the default (step 4). Nothing live changes under this ticket: the script never
  runs against the real sets root until the briefs are approved.
- **Readings settled by the CTO (2026-11-09) [DEC-1101 (2)-(3)]:**
  1. **The canary's target (a correction to LAUNCH-SPEC §3):** Claude Code's `--restricted` confines the file tools to
     the working folders (`--add-dir` included) by itself (Claude Code 2.1.318's help; REHEARSAL.md's probes). A Read
     of a file outside every working folder is refused even when the wall's settings were ignored, so LAUNCH-SPEC's
     canary as written would pass with the settings unloaded: it fails open. The canary therefore plants its file in
     its own temporary folder and adds that folder with `--add-dir` for the canary only (otherwise the same flags):
     restricted mode allows that Read, and only the wall's settings and hook (which know only the wall and its tree)
     refuse it. A Read in `permission_denials` means the settings loaded; an allowed Read refuses with code 16. The CTO
     proves it live (S9): valid settings refused, one corrupted key not refused.
  2. **Planted roots:** every location other than `--sets-root` derives from `HOME` (`~/gov-os-wall-trees/`,
     `~/gov-os-runs/indep/`) and the repository is the git top level of the folder the script runs in; tests plant
     HOME, the sets root and the repository. For the CTO's live trial, which needs the real HOME for the session's
     login, the interface names one environment override each for the runs folder and the trees folder (tests and the
     trial only); a run with an override says so in `WALL.json` and in a boolean of `counts.json`.
  3. **Where the bytes come from:** the brief and the template files are read from the repository at `--commit`
     (`git show`), never from a working tree, and checked against `APPROVED` before anything is written.
  4. **The briefs' front matter** (planted in tests; the real briefs are step 3's): `kind`, `sample` (N), `model`,
     `result_schema` (a file name in `indep-schemas/`), and optionally `budget_usd` and `timeout_s` at most the kind's
     in `kinds.yaml` (a larger value refuses). The result schemas here are first versions; the briefs may revise them
     with their own approval.
  5. **The labellers' input** (rulebook, actions) and the auditor's misses are read from the sets root's own folders by
     the script's code; their places are the designer's to fix in the interface, inside the planted sets root.
- **Tests first:** an independent test designer writes `tests/acceptance/W2-149/` from these lines and LAUNCH-SPEC,
  before the engineer starts, on planted folders only; live cases are marked live and run by the CTO outside the
  sandbox (a planted brief and tree; never the sets root's real content).
- **Profile FULL:** the script decides what an independent session sees and what reaches the CTO; a check that fails
  open breaks the sets' independence (question 2). Hence every refusal tested on its own, one independent review
  (READY by `verdict.py`, at most two rounds), and a live canary and session before the briefs go to the owner.
- **Est.:** about 700 lines with the engineer's tests; about two working days with its review.

[DEC-1101 (2)-(3); DEC-1109 (2)]

## Notes

**2026-11-09T20:54:38Z**

READY (verdict.py) at w2/W2-149 a929356ea after review round 2 of 2 (records: orchestrator reviews/W2-149-review-r1.md, -r2.md). gov accept W2-149 77 passed, 0 failed, 3 live skipped; the 3 live cases (S9 live canary both ways, S11, S12) passed outside the sandbox at a929356ea. Rows carried: F3, F4, F7, F8, F9, F10, F12, F13, F14, F15 (in, none ordinary-work fails-open). To the owner: F2 (the path map's sets_root_hidden does not cover a new set's hidden/, XCHECK notes or runs/<audit>/miss-classes.json: an ACT, an entry criterion before the first real writer run) and F11. Not merged.

**2026-11-09T23:13:43Z**

The F11 follow-up placed here (the CTO's delegated decision, DEC-1112 (3); ACT-SETS-GLOBS-1 §3; DECIDED-NOT-DONE row 77): S10's flag list gains `--setting-sources project`, for the session and the canary alike, so the real HOME's `~/.claude/settings.json` (allow-all lines, `acceptEdits`) and any later user hook or `CLAUDE.md` never load into a wall; the wall's own `.claude/settings.json` is the project source and is also passed by `--settings`, so nothing the wall needs is lost (ACT-INDEP-WALLS-1's live session B held with that flag). Tests first: one independent test designer case (the flag present, the user settings file not loaded), then the engineer, one review (READY by verdict.py), the live S11 case re-run by the CTO. Branches `w2/W2-149-f11-tests`, `w2/W2-149-f11` from `w2/integrate`.
