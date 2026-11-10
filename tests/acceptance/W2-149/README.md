# W2-149 acceptance tests: the independent sessions' launch script

Ticket DAEO-52ku (W2-149), profile FULL (DEC-1101 (2)-(3) step 2, DEC-1109 (2)). Written by the independent test
designer (MR-3) from the ticket's KPI lines S1-S21, its ten failure lines, its "Readings settled by the CTO" and
LAUNCH-SPEC §1-§5, before any implementation, reading only `w2/integrate` (`bc72066fa`): the template
`governance/project/indep-walls/`, ACT-INDEP-WALLS-1, the path map, `.claude/hooks/pretooluse.py` and the CTO's
reference copies (`walls_check.py`, `rehearse.sh`, `REHEARSAL.md`).

**Set-up A's wiring** (DEC-1112 (3), DEC-1113; S16 and S20 changed, S22-S28 and failure line 11 added; written at
`ce1e9d0df` from those lines, the five approved briefs' input, output and result sections, their front matter, and the
lead's interface draft, which the section "Set-up A's wiring: the interface" below adopts with changes): the
five briefs' bytes never change; the template supplies what they lack and the script gains set-up A's flows. Where that
section and an older line of this README differ, that section governs.

## How they run

    PYTHONPATH=<worktree>/src TMPDIR=<scratch> python3 -m pytest tests/acceptance/W2-149 -q -p no:cacheprovider \
      -o tmp_path_retention_policy=failed
    python3 -m gov.cli.main accept W2-149 --root <worktree>

About 45 s, serial. **Live cases** (marker `live`, file `test_w2_149_live.py`) are skipped unless
`GOV_W2_149_LIVE=1`: the CTO runs them outside the sandbox, with `claude` on `PATH` and the real HOME (the session's
login); they cost a few cents (model `haiku`).

**`bwrap` cases** (marker `bwrap`, registered in `conftest.py`, skipped unless `GOV_W2_149_BWRAP=1`): the cases whose
launch runs the first labeller's rule script confined (S25's good and five bad scripts, S26's two, S28's labeller
round 2). The launch sandbox cannot start a nested `bwrap` (probed 2026-11-10: `bwrap --unshare-all --die-with-parent
--ro-bind /usr /usr true` says "No permissions to create new namespace"), so the CTO runs them outside it, planted
roots as every case, no model and no network beyond the case's own 127.0.0.1 listener:
`GOV_W2_149_BWRAP=1 python3 -m pytest tests/acceptance/W2-149 -m bwrap ...`. S25's missing-`bwrap` case needs no
`bwrap` and runs in the default run.

- **Planted folders only.** One planted git repository per session (`w2_149_support.build_repo`); per case a planted
  HOME (`<tmp>/home`, holding `gov-os-eval/` (the sets root), `gov-os-runs/indep/`, `gov-os-wall-trees/`,
  `.claude/projects/`), a stub `claude` first on `PATH`, and records. `World.check_planted` fails every launch closed
  unless the sets root, runs, trees and repository lie under the session's temporary folder and none is a real
  `~/gov-os-eval`, `~/gov-os-runs`, `~/gov-os-wall-trees` or `~/.claude` (failure line 10). No model, network or GPU.
- **The planted repository** (`w2/integrate`): A (the last audit's commit, in the planted `AUDITS.log`), L (adds the
  symlink `docs/link.md`), B (the link gone; `docs/d03.md`, `src/pkg/m02.py` changed, `docs/new.md` added, three
  excluded paths changed), then one commit per single change from B's tree: TB (one byte of `writer.md`), T-`<file>`
  (one byte of each template file), TK (`Bash` in the writer's tools), TS (`hooks.PreToolUse` a string), then Z (B's
  tree again, the head). `side` holds S, not reachable from `w2/integrate`. It carries the six template files copied
  from this tree, a path map holding only `sets_root_hidden`, and six briefs in `governance/project/indep-briefs/`.
  **Set-up A** (in A, so the A..B diff is unchanged): the template's `kinds.yaml` is the tests' own
  (`w2_149_support.KINDS_YAML`: the four kinds as they stand plus a `model` each, and the `briefs:` map; the other five
  template files stay this tree's); the path map also holds the `sandbox-guard-exp-1` evaluation set; the five set-up A
  briefs at `governance/project/indep-briefs/sgx1/<name>.md` (front matter byte for byte, checked against the approved
  sha256s; a planted body), six S22 variants under `sgx1x/`; one file under each of `.claude/**`, `src/gov/guard/**`,
  `src/gov/launch/**`; three tickets in `.tickets/`. Two more one-change commits from B: PU (the path map without the
  set's entry) and PC (`sets_root_hidden` no longer covering the set's hidden glob).
- **The stub `claude`** (`w2_149_support.STUB`) and **the test hook** (`HOOK`): their contracts are below.
- **The oracles** (the selection, the tree, the filled settings and standing note, the F checks, the counts' shape)
  are computed in `w2_149_support.World` from the planted repository and the KPI lines, never from the script.
- **A check of the tests themselves:** a throwaway sketch of the script, written by the designer in its scratchpad
  (never committed; `W2_149_SCRIPT=<path>` points the cases at it), passes all 77 non-live cases. Two mutations: the
  sketch with LAUNCH-SPEC's original canary (target outside every working folder, no own `--add-dir`) fails both
  S9 cases that guard reading 1; the case S6 found a bug of the cases themselves (now fixed).

## The interface (what the engineer builds to)

The script is `governance/project/orchestration/tools/indep_launch.py` (standard library, PyYAML, `git`; no `gov`
import); its schemas in `governance/project/orchestration/tools/indep-schemas/` beside it.

### Command line and exit codes (LAUNCH-SPEC §1, §5)

    python3 indep_launch.py --sets-root <root> --kind writer|checker|auditor|labeller \
        --brief governance/project/indep-briefs/<name>.md --brief-sha256 <64 hex> --commit <commit> \
        --set <set> [--round 1|2] [--audit <name>] [--seed new|<int>] [--dry]
    python3 indep_launch.py --sets-root <root> --kind <kind> --run <run id> --counts-only

- The options are exactly: `--sets-root --kind --brief --brief-sha256 --commit --set --round --audit --seed --dry
  --counts-only --run -h/--help`; nothing else (S5 reads `--help`). `--round` defaults to 1. `--audit` (the auditor
  only) names the audit's folder `runs/<audit>/` under the sets root. Set and audit names match
  `^[a-z0-9][a-z0-9-]{0,63}$`.
- **`--seed`:** `new` (the default) draws 63 random bits; an integer only with `--dry`, else **17** (S6).
- **`--dry`:** B0-B6 in full (the seed recorded, `SEEDS.log` line included), then stops: no canary, no session, the
  wall and its tree **left in place** for inspection, `status: "dry"`, exit 0, `counts.json` written.
- **`--counts-only`:** prints `<runs>/indep/<kind>/<run>/counts.json` as the result line, exit 0; builds nothing.
- **Exit codes** (§5): 0 delivered or dry; 10 brief; 11 template; 12 wall or tree exists; 13 seed not first; 14
  commit; 15 file budget; 16 canary; 17 argument; **18 rules** (set-up A's rule script cannot run confined or fails,
  DEC-1112 (3); its section below); 20 result rejected; 21 stopped; 22 a trace. Fixed here:
  - **10** also: the brief's front matter `kind` differs from `--kind`; `budget_usd` or `timeout_s` above the kind's.
  - **11** also: a kind's tools in `kinds.yaml` outside `Read, Grep, Glob, Write, Edit, MultiEdit, TodoWrite`.
  - **14** also: a commit whose tree holds a link (mode 120000) or a submodule (160000), checked before anything is
    written; and, at extraction, an archive member that is a link, absolute, or holds `..`.
  - **17**: a seed without `--dry`; a `--sets-root` with a path part `indep-walls`; any other argument whose value,
    `~` expanded and read against the folder the script runs in, lies at or under the sets root; an override (below)
    that is not absolute or lies at or under the sets root; a bad set or audit name. **The argument checks come
    first**, before every other check.
  - Order otherwise: 17, then 14 (resolve, reach), 11, 10, 14 (links), 15, then B1 (12) onward.

### Where everything is (reading 2)

- **The repository:** `git rev-parse --show-toplevel` of the folder the script runs in. **The main line:** local
  branch `w2/integrate` if it exists, else `main`; `--commit` must resolve (`<c>^{commit}`) and be its ancestor.
- **Bytes from git** (reading 3): the brief and the six template files are `git show <commit>:<path>`, never the
  working tree; the tree is `git archive <commit>`.
- **HOME:** the runs folder `~/gov-os-runs` (the script writes under `<it>/indep/`) and the trees folder
  `~/gov-os-wall-trees`. **Overrides** (tests and the CTO's trial only): `GOV_INDEP_RUNS_DIR` replaces
  `~/gov-os-runs`, `GOV_INDEP_TREES_DIR` replaces `~/gov-os-wall-trees`; a run with either says so in `WALL.json`
  (`runs_override`, `trees_override`) and in `counts.json` (`override: true`).
- **The sets root:** `--sets-root`, real path. `APPROVED` is `<root>/indep-walls/APPROVED`.
- **A run:** id `<UTC yyyymmddThhmmssZ>-<set>-r<round>` (`^\d{8}T\d{6}Z-[a-z0-9][a-z0-9-]*-r[12]$`); wall
  `<root>/indep-walls/<kind>/<run>/`; tree `<trees>/<kind>-<run>/`; session output `<wall>.session.json`; the
  finished wall `<root>/indep-walls/<kind>/<run>.tar`; the counts folder `<runs>/indep/<kind>/<run>/` holding
  `counts.json`, `launch.log` (the script's log), `session.pid`, `session.pgid`.
- **The hidden part's count** (S18): the files under the sets root whose root-relative path matches a
  `sets_root_hidden.hidden` glob of the repository's `governance/project/path-map.yaml` at `--commit` (the
  rehearsal's fnmatch rule). This run's expected files: at least the wall's fixed files plus its staged copies. Count
  plus expected above 8,000: **15** before anything is written.

### APPROVED's lines

    # comment lines and blank lines are ignored
    <sha256>  template governance/project/indep-walls/<file>      (two spaces; one line per template file)
    <sha256>  brief <kind> <repository path of the brief>        (the operator writes these at step 3)

A missing or different `template` line: 11. No `brief <kind> <--brief>` line with `--brief-sha256`, or the bytes at
`--commit` hashing otherwise: 10. Every result line carries `approved_sha256` (the sha256 of `APPROVED`'s bytes).

### The brief's front matter (reading 4)

    ---
    kind: writer                         # must equal --kind
    sample: 5                            # N, the sample's size
    model: <model id>
    result_schema: writer-result.schema.json    # a file in indep-schemas/
    budget_usd: 0.5                      # optional, at most kinds.yaml's
    timeout_s: 30                        # optional, at most kinds.yaml's
    ---

Absent `budget_usd`/`timeout_s`: the kind's from `kinds.yaml`.

### The build (LAUNCH-SPEC §2), the content rule, the inputs

- **B1:** the wall must not exist (an empty folder may be accepted), the tree folder must not exist: else **12**,
  both left untouched.
- **B2:** `seed.txt` holds the seed in decimal and a newline, mode 0444; then one JSON line appended to
  `<runs>/indep/SEEDS.log`: `{"time": "<UTC ISO Z>", "kind", "run", "commit": <40 hex>, "seed": <int>,
  "seed_sha256": <sha256 of seed.txt's bytes>}` (more keys allowed). **Every file under `input/` and the tree, and
  this ledger write, carry an mtime (ns) strictly later than `seed.txt`'s** (a filesystem's coarse clock may need a
  pause of one tick after B2); the ledger's mtime earlier than every input and tree file in a fresh HOME.
- **B3:** the tree: the archive's files less `tree-exclude.txt` (fnmatch on the repository path, as
  `walls_check.py`); no entry (file or folder) whose path, or a folder's path with `/`, matches an exclusion; every
  file 0444 (executables too), every folder and the root 0555; no `.git`, no link.
- **The rule:** `last` = the `commit` of `AUDITS.log`'s last line (`<runs>/indep/AUDITS.log`, JSON lines
  `{"time", "commit": <40 hex>, "run", "audit"}`; no line: no changed paths). `changed` = sorted
  `git diff --name-only <last> <commit>` that exist at the commit and are not excluded. `others` = `git ls-tree -r
  --name-only <commit>` (its order) less the excluded and the changed. `sample = random.Random(seed).sample(others,
  min(N, len(others)))`, a fresh `Random(seed)` for each draw.
- **B4:** `input/selection.json` = `{"commit", "last_audit" (40 hex or null), "seed_sha256", "changed", "sample"}`
  (+ `"overlap"` for the second labeller), then the kind's staged copies, all 0444 in a 0555 `input/`:
  writer round 1 nothing more; writer round 2 `input/set/**` ← `fixtures/evaluation/<set>/hidden/**` and
  `input/notes.md` ← `fixtures/evaluation/<set>/XCHECK-r1.md`; checker `input/set/**`; auditor `input/set/**` and
  `input/misses.jsonl` ← `runs/<audit>/misses.jsonl`; the labeller: **set-up A's flows only** (the section "Set-up
  A's wiring: the interface"; the old staging from the sealed folder's `rulebook.md` and `corpus/actions-r1.jsonl` /
  `-r2.jsonl` and the `random.Random` overlap are gone, DEC-1112 (3), S20 changed). A set-up A writer's walls follow
  B4 (selection.json; writer 2 also seal.json); a set-up A labeller's or the overlap auditor's walls stage exactly
  their briefs' inputs, no selection.json.
- **The seed check (13)** runs after the test hook's `after_input` and before `WALL.json`: this run's ledger line
  present with `seed_sha256` equal to `seed.txt`'s, and the mtime rule above.
- **B5:** `brief.md` (the approved bytes); `CLAUDE.md` = `CLAUDE.md.tmpl` with `@KIND@ @RUN@ @BRIEF_SHA@ @TREE@
  @COMMIT@` (the 40-hex commit) replaced; `.claude/settings.json` = `settings.json.tmpl` with `@WALL@ @TREE@ @REPO@
  @WORKTREES@ (<HOME>/gov-os-worktrees) @RUNS@ (the folder replacing ~/gov-os-runs) @HOME@ @SETS_ROOT@ @WALLS@
  (<root>/indep-walls) @MODEL@` replaced by real paths and the brief's model, and the `"@OTHER_WALLS@"` entry
  replaced by `Read(/<walls>/<k>/**)` for each other kind and `Read(/<walls>/<kind>/<r>/**)` for each wall folder of
  its kind present at build time (the filled file need not be valid: the canary is the check); `.claude/wall_hook.py`
  byte for byte; `out/` empty, 0700; the wall's root, `.claude/` and `input/` with no write bit.
- **B6:** `WALL.json` holds at least `kind run set round commit repo tree runs home sets_root brief_sha256
  seed_sha256 settings_sha256 hook_sha256 template_sha256 ({file: sha256} for the six) approved_sha256 selection
  ({changed, sample} counts) seeded_before_content runs_override trees_override`.

### The canary and the session (LAUNCH-SPEC §3, reading 1)

- **The canary:** the script plants one file in a temporary folder of its own (outside the wall, the tree and every
  root above), runs `claude` from the wall with the session's flags plus `--add-dir <that folder>`, under
  `timeout`, with the limit `min(60, timeout_s)`, and a prompt that names the target **by its absolute path**. It
  passes only when the JSON output parses and `permission_denials` holds a `Read` whose `tool_input.file_path` is the
  target. Anything else (output unreadable, the limit passed, an error, another denial): **16**, the session never
  started.
- **The session** (S10, `--setting-sources project` added by DEC-1112 (3), F11): `timeout --kill-after=<s> <timeout_s>
  claude -p --restricted --setting-sources project --settings <wall>/.claude/settings.json --add-dir <tree> --tools <the kind's, comma-joined> --no-session-persistence
  --strict-mcp-config --disable-slash-commands --permission-prompts none --model <brief's> --max-budget-usd
  <brief's or kind's> --output-format json "<prompt>"`, cwd the wall, stdin `/dev/null`, stdout to
  `<wall>.session.json`, environment exactly `HOME PATH LANG USER` (the script's own values), in its own process
  group. The prompt: one line, naming `brief.md` and `out/result.json`, no absolute path; its sha256 written in the
  script's source as a 64-hex literal.
- **`--setting-sources project`** (DEC-1112 (3), F11): the session and the canary each carry it once, the value
  `project` exactly (no `user`, no `local`), in either form (`--setting-sources project` or `=project`), so the
  user's `~/.claude/settings.json` (and any user hook) never loads into a wall; the wall's own settings still come by
  `--settings`.
- **The pid files:** `session.pid` (the process the script started) and `session.pgid` (its group, the session's)
  in the counts folder; waits and stops only by them (`os.killpg`), never by a name.
- **Stopped (21):** `timeout`'s exit (124/137), or `is_error` with a `subtype` naming the budget
  (`error_max_budget_usd`): nothing delivered, the group gone.

### The result, the delivery, the wall packed

- **`out/result.json`** must pass `indep-schemas/<brief's result_schema>` (top level may hold other fields; only
  numbers are copied). The four first versions:
  - writer `{"questions": int, "by_kind": {k: int}, "by_area": {a: int}}`, `k` in `fact procedure decision location
    negative`, `a` in `contract decisions kernel code tests operations docs` (closed objects); delivers `out/set/**`;
  - checker `{"checked", "accepted", "revise", "rejected": int}`; delivers `out/notes.md`;
  - auditor `{"misses": {class: int}}`, class in `gold_wrong question_ambiguous retrieval_miss answer_wrong
    out_of_scope`; delivers `out/classes.json`;
  - labeller `{"labelled", "allow", "refuse": int}` (+ `agree`, `disagree`) (no flow delivers by it once set-up A's
    wiring lands; a front matter may still name it, S22's variant does);
  - set-up A's five: the section below.
  Missing, failing, or the delivered file missing: **20**, `status: rejected`, nothing delivered.
- **Destinations** (S16): writer `fixtures/evaluation/<set>/hidden/` (round 1: must not exist); checker
  `fixtures/evaluation/<set>/XCHECK-r<round>.md`; auditor `runs/<audit>/miss-classes.json` (and `AUDITS.log` gains
  `{"commit": <the run's>}` once delivered); set-up A's flows (the labeller's only ones): the section below.
  Copied by a temporary name, hashed, renamed. **The bundle's sha256:** one file's own; the writer's set the sha256 of
  the lines `<file sha256>  <path relative to out/set/>\n` sorted by path.
- **Traces (22):** the files or folders at depth 1 or 2 under `~/.claude/{projects,file-history,session-env,todos}`
  whose name begins with the session id; `traces` is that count; 22 when it is not 0 (`status` as it would be).
- **Packed:** after a delivery, a rejection or a stop, `<run>.tar` (mode 0400) holds the wall (members `<run>/...`)
  and `<run>.session.json`; the wall, its tree and the session file removed: the hidden part grows by one file.

### The counts (LAUNCH-SPEC §4) and the result line

`indep-schemas/indep-counts.schema.json`: every object `additionalProperties: false`, every string an `enum`, a
`const` or an anchored `pattern`. Every key present on every result (unknown values `null`):

| Key | Value |
|---|---|
| `act` | `"ACT-INDEP-WALLS-1"` |
| `kind`, `run`, `set`, `round`, `commit` | the kind; the run id or null; the set name; 1 or 2; 40 hex or null |
| `brief_sha256`, `approved_sha256`, `seed_sha256` | 64 hex or null |
| `template_ok`, `override` | booleans |
| `selection` | `{changed, sample, overlap}` integers |
| `session` | `{exit, is_error, turns, cost_usd, duration_s, refusals}`; `refusals` a closed object of counts keyed `Read Grep Glob Write Edit MultiEdit TodoWrite Bash WebFetch WebSearch Task Agent NotebookEdit Skill other` (any other tool name counts under `other`) |
| `out` | `{schema_ok, files (every file under out/), <the kind's numbers>}` |
| `delivered` | `{files, sha256, to}`, `to` in `set notes classes labels cases round1 decisions` or null (set-up A's round 1 also each delivered file's sha256, the engineer's keys, 64-hex patterns) |
| `traces` | integer |
| `status` | `delivered`, `rejected`, `refused`, `stopped`, `dry` |
| `code`, `reason` | the exit code; null, or the code's fixed word: 10 `brief`, 11 `template`, 12 `wall_exists`, 13 `seed_order`, 14 `commit`, 15 `file_budget`, 16 `canary`, 17 `argument`, 18 `rules`, 20 `result`, 21 `stopped`, 22 `trace` |

**The result line:** stdout's last line is this object as one line of JSON (equal to `counts.json` when one is
written). No free text from `out/` or the session in it, in stderr or in `launch.log`; no path under the wall printed.

### The test hook

`GOV_INDEP_TEST_HOOK=<executable>`: when set, the script runs `<executable> <point> <wall> <tree>` (absolute paths)
at each point, with its own environment, waiting for it and ignoring its exit: `before_wall` (the run id chosen, B0
passed, nothing written), `after_seed`, `after_tree`, `after_input`, `before_canary`, `before_session`,
`after_session`. The session's environment never carries it. The cases use `before_wall` (S3), `after_input` (S4),
`before_session` and `after_session` (S11 live).

### The stub `claude` (the cases' model of Claude Code)

It records each call (argv, parsed flags and `--add-dir` folders, prompt, cwd, environment, pid, pgid, ppid, its
parent's command line from `/proc`, whether stdin is `/dev/null`, a listing of `input/`) to the case's records. A call
is **the canary** when its prompt names an existing file by absolute path. For the canary it models Claude Code:
`--restricted` refuses a Read outside cwd and every `--add-dir` folder; a `--settings` file it cannot read, parse or
validate (a known key of the wrong type) is ignored without a word; with the settings loaded the Read is refused only
when a `PreToolUse` hook in them refuses it, run as `sh -c <command>` with the event on stdin (exit 2 or a `deny`
decision). **The user's settings source** (S10, F11): with no `--setting-sources`, or a list naming `user`, every
call loads `$HOME/.claude/settings.json` when that file is valid: its `SessionStart` hooks run at the call's start and
its `PreToolUse` hooks run beside the `--settings` file's on the canary's Read (its allow lines never lift a refusal,
as Claude Code's deny-over-allow); a list that leaves `user` out loads nothing from it. Each call records
`user_settings` (`sources`, `present`, `loaded`) in `calls.jsonl`, the canary's outcome `user_settings_loaded`. No
earlier case plants that file, so their behaviour is unchanged. It writes `{"type": "result", "subtype", "is_error", "session_id", "num_turns", "total_cost_usd",
"duration_ms", "permission_denials": [{"tool_name", "tool_use_id", "tool_input"}], "result"}`. A case can make the
canary print garbage, sleep, or report another denial; and make the session write `out/` files, sleep, spawn a child
(`sleep 300`), end on its budget, or leave a trace file. With no session set, a session call fails (exit 97) and is
recorded: a `--dry` build that starts anything fails its case.

### Left to the engineer

The canary's exact prompt (it names its target by absolute path) and its temporary folder's place; the
`--kill-after` value; how the wall is filled (text or JSON), packed (tar format) and removed; the expected-file count
beyond its floor; `launch.log`'s content (no free text, no wall path); the `SEEDS.log` and `AUDITS.log` keys beyond
those named; what a refusal at 13 or 16 leaves (the cases ask only that no session starts and a good launch then
builds; packing it as in S17 is recommended); writer round 2's replacement of an existing `hidden/`; a missing input
(a set, the misses, the rulebook) before anything is written (no code is fixed for it).

## Set-up A's wiring: the interface (DEC-1112 (3), DEC-1113; what the engineer builds to)

The lead's draft (`INTERFACE-DRAFT.md`) adopted, with these changes: one result schema per brief (writer 1's has no
`not-sealed`); no `selection.json` in a labeller's or the auditor's wall (their briefs name none; labeller 2's
round 1 is "`input/half.json` only"); the x/y draw, the map's, the merge's and the mapped-back forms fixed; the map
written at delivery only; the rule script's two overrides and caps named; the selection of a set-up A writer stays S5's.

### The template (the engineer's two files)

- `tree-exclude.txt` gains the line `governance/project/indep-briefs/**` (every wall).
- `kinds.yaml`: every kind gains `model: <model id>`; a top-level `briefs:` map, keyed by the front matter's `brief:`
  id, each entry `{kind, flow, result_schema, sample, tree_exclude}` and optionally `model`. The five entries:

| Brief id | `kind` | `flow` | `result_schema` (in `indep-schemas/`) | `sample` |
|---|---|---|---|---|
| `sgx1-writer-tuning` | writer | `sgx1-writer-1` | `sgx1-writer-tuning-result.schema.json` | optional (the front matter has 400) |
| `sgx1-writer-heldout` | writer | `sgx1-writer-2` | `sgx1-writer-heldout-result.schema.json` | optional (the front matter has 400) |
| `sgx1-labeller` | labeller | `sgx1-labeller-1` | `sgx1-labeller-result.schema.json` | 0 |
| `sgx1-labeller-2` | labeller | `sgx1-labeller-2` | `sgx1-labeller-2-result.schema.json` | 0 |
| `sgx1-overlap-auditor` | auditor | `sgx1-overlap-auditor` | `sgx1-overlap-auditor-result.schema.json` | 0 |

  Each entry's `tree_exclude`: `.claude/**`, `src/gov/guard/**`, `src/gov/launch/**`,
  `governance/project/indep-walls/**`. The models are the CTO's to choose (the cases read the planted ones). The
  planted `kinds.yaml` adds two test-only entries (`w2-149-no-schema`, `w2-149-no-sample`) and an entry `model` on four
  of the five; the script must take any entry of this form.

### Stage 10 (S22)

- `model`, `result_schema` and `sample`, each: the front matter's value, else the value in the `briefs:` entry the
  front matter's `brief:` names, else (`model` only) the kind's `model`. A value found nowhere: **10**. An entry whose
  `kind` differs from the front matter's: **10**. A labeller brief with no `brief:` id, or one the map does not hold:
  **10** (the labeller kind runs set-up A's flows only). A brief of another kind with no `brief:` id: as before.
  Front-matter keys the script does not use (`brief version experiment rounds tools budget_basis`) are ignored;
  `budget_usd`/`timeout_s` as before (the five's are within their kinds').
- `WALL.json` gains `model` (the resolved one, also the settings' `@MODEL@`), `result_schema`, `brief_id` and `flow`
  (both null without an entry).

### The trees (S23)

Every tree: the archive less `tree-exclude.txt`. A brief with an entry: also less the entry's `tree_exclude` (fnmatch
on the repository path, as `tree-exclude.txt`). The selection (S5) stays "less `tree-exclude.txt`": the entry's globs
limit what a wall may read, not the writer's pool of places (a place is a name).

### Places (S16, S24)

`<runs>` is `GOV_INDEP_RUNS_DIR` or `~/gov-os-runs`; `EXP` = `<runs>/SANDBOX-GUARD-EXP-1`. **H**, the half's folder:
`tuning` → `EXP/tuning`; `held-out` → `<sets root>/fixtures/evaluation/sandbox-guard-exp-1/hidden` (the sealed
folder). Under H: `corpus/actions.jsonl` and `planted/cases.jsonl` (inputs; `planted/cases.jsonl` is also the writers'
destination); `labels/r1-sgx1-labeller/{rulebook.md,label_rules.py}`; `labels/r1-sgx1-labeller-2/rulebook-2.md`;
`labels/labels.jsonl`; `labels/labels-2.jsonl`; `labels/audit/<run>.map.json` and `labels/audit/<run>.decisions.jsonl`;
`labels/history/<any name>` (a replaced `labels.jsonl`); `labels/owner.jsonl`.

- `--set` names the half: writer 1 `tuning`, writer 2 `held-out`, the labellers and the auditor either; anything else
  **17**, nothing built (checked once the entry is known, after stage 10). `--round`: the writers and the auditor 1, the
  labellers 1 or 2. `--audit` stays required for the auditor kind, recorded only (no misses read).

### The staged inputs (S20, S24, S25, S27): `input/` holds exactly

| Flow | Round | `input/` |
|---|---|---|
| `sgx1-writer-1` | 1 | `selection.json` (S5) |
| `sgx1-writer-2` | 1 | `selection.json`, `seal.json` |
| `sgx1-labeller-1` | 1 | `half.json`, `actions.jsonl`, `cases.jsonl` |
| `sgx1-labeller-1` | 2 | the same, `round1/rulebook.md`, `round1/label_rules.py`, `script-labels.jsonl`, `sample.json` |
| `sgx1-labeller-2` | 1 | `half.json` |
| `sgx1-labeller-2` | 2 | `half.json`, `round1/rulebook-2.md`, `sample.jsonl` |
| `sgx1-overlap-auditor` | 1 | `half.json`, `disputes.jsonl`, `tickets.jsonl` |

- `half.json`: `{"half": <half>, "pin": <the 40-hex commit>}`; the auditor's also `"cases": <this run's disputes>`.
  Exactly these keys.
- `actions.jsonl` / `cases.jsonl`: H's `corpus/actions.jsonl` / `planted/cases.jsonl`, line by line in file order, each
  kept to `id role agent ticket wbs tool input cwd executable strata source` (and `rule_class` for a case); one JSON
  object per line (key order free). "The half's staged lines" below: the actions' then the cases'.
- `seal.json`: `{"sealed": true}` when the path map at `--commit` has `evaluation_sets.sandbox-guard-exp-1.hidden`
  holding `fixtures/evaluation/sandbox-guard-exp-1/hidden/**` and a `sets_root_hidden.hidden` glob covers it (the same
  glob, or one matching a path under that folder); else `{"sealed": false}` (commits B, PU, PC).
- `round1/`: H's `labels/r1-<brief id>/` files, byte for byte. Round 1's `counts.json` records each delivered file's
  sha256; round 2 takes the latest delivered round-1 run of the same brief sha256 and half from `<runs>/indep/labeller/`
  and refuses **10** when a file's sha256 differs, or when no round 1 was delivered.
- `sample.jsonl` (labeller 2, round 2): the half's staged lines whose `int(sha256((SEED + "overlap" +
  id).encode("utf-8")).hexdigest(), 16) % 10 == 0`, in order; SEED is the wall's `seed.txt` less its newline.
- `script-labels.jsonl`: the rule script's output lines, in order. `sample.json`: `{"ids": [...]}`, the half's staged
  ids whose `int(sha256((SEED + "labeller-sample" + id).encode("utf-8")).hexdigest(), 16) % 20 == 0`, in order.
- `disputes.jsonl`: the ids in both `labels.jsonl` and `labels-2.jsonl` whose `label` differs and that no
  `labels/audit/*.decisions.jsonl` names, sorted by id, the first 40; one line each, in that order: `{"id", "action":
  {role agent ticket wbs tool input cwd} (from the staged line), "x": {label rule_class clauses reason}, "y": {...}}`.
  **x/y:** `rng = random.Random(seed)`; for each case in that order, `rng.random() < 0.5` means x is labeller 1
  (`labels.jsonl`), else x is labeller 2. Nothing else of either labeller enters the wall.
- `tickets.jsonl`: one line per ticket a case's action names (its `ticket` matched to a ticket file's `id`, or its
  `wbs` to `wbs_id`), read from `.tickets/*.md` at `--commit`: `{"id", "role", "wbs_id", "allowed_paths"}` and nothing
  else; a name no ticket file holds gives no line; order free.
- **A missing input refuses 10 before anything is written:** H's `corpus/actions.jsonl` or `planted/cases.jsonl`
  (labeller 1), round 1's files or counts (round 2), `labels.jsonl` or `labels-2.jsonl` (the auditor).

### The rule script (S25; exit 18, reason `rules`)

- At labeller 1's round 2 the script runs round 1's delivered `label_rules.py` under `bwrap`: the program
  `GOV_INDEP_BWRAP` names (an absolute path; tests and the trial only), else `bwrap` on `PATH`; the interpreter
  `GOV_INDEP_RULES_PYTHON` names (absolute; tests and the trial only), else the one on the first line of
  `~/.local/bin/gov`; `-I`. Every namespace unshared (no network), `--die-with-parent`, nothing bound but the
  interpreter's own files (and the rule script) read-only, nothing writable; no new process (a fork or an exec inside
  fails); caps on CPU, memory and output, a wall-clock cap of at most 60 s. Stdin: the half's staged lines.
- The output must give every staged id exactly once: `{"id", "label": allow|refuse|ask, "rule_class": 1..14 (int),
  "clauses": [strings], "uncertain": bool}`. Anything else (a non-zero exit, a cap reached, an id missing, repeated or
  unknown, a bad value; `bwrap` or the interpreter missing or unable to start): **18**, nothing staged (no
  `script-labels.jsonl` or `sample.json` in the wall or its tar), no session; it may run before or after the wall is
  built (a refusal after B1 leaves what 13 leaves).

### The deliveries (S16, S26, S27): a temporary name, hashed, renamed; all or nothing

| Flow | Round | From `out/` | To | `delivered.to` |
|---|---|---|---|---|
| `sgx1-writer-1` | 1 | `cases.jsonl` | tuning H `planted/cases.jsonl` | `cases` |
| `sgx1-writer-2` | 1 | `cases.jsonl` | held-out H `planted/cases.jsonl` | `cases` |
| `sgx1-labeller-1` | 1 | `rulebook.md`, `label_rules.py` | H `labels/r1-sgx1-labeller/` | `round1` |
| `sgx1-labeller-1` | 2 | `hand-labels.jsonl`, merged | H `labels/labels.jsonl` | `labels` |
| `sgx1-labeller-2` | 1 | `rulebook-2.md` | H `labels/r1-sgx1-labeller-2/` | `round1` |
| `sgx1-labeller-2` | 2 | `labels-2.jsonl` (its bytes) | H `labels/labels-2.jsonl` | `labels` |
| `sgx1-overlap-auditor` | 1 | `decisions.jsonl`, mapped back | H `labels/audit/<run>.decisions.jsonl` (and below) | `decisions` |

- An existing destination file refuses **20** (the auditor's `labels.jsonl` and `owner.jsonl` excepted); nothing
  else changes under the sets root or `EXP` (the wall's tar aside). `out/aims.jsonl` stays in the tar only. A
  destination's missing folders are made (writer 1's case starts with no `EXP` at all; `labels/r1-<id>/` and
  `labels/history/` are made by their first delivery).
- `delivered.files`: the delivered `out/` files (round 1 of labeller 1: 2); `sha256`: one file's own (for labeller 1's
  round 2 the merged `labels.jsonl`'s, for the auditor the mapped-back decisions file's); several files: the sha256 of
  the lines `<file sha256>  <name>\n` sorted by name.
- **Labeller 1, round 2 (S26):** `out/hand-labels.jsonl`, lines `{"id", "label", "rule_class", "clauses", "reason"}`,
  must cover every id `script-labels.jsonl` marks uncertain, every id it puts in classes 1-13 and every `sample.json`
  id; else **20**, nothing written. The merge: one line per staged id, in the staged order, exactly `{"id", "label",
  "rule_class", "clauses", "reason", "how"}`: a hand line's values and `how: "hand"`, else the script's with
  `reason: ""` and `how: "script"`.
- **The overlap auditor (S27):** `out/decisions.jsonl` must hold one line per case, in the disputes' order, the same
  ids, exactly `id label rule_class basis agrees_with flag reason` (`label` allow|refuse|ask, `rule_class` 1-14, `basis`
  a list of strings, `agrees_with` x|y|neither, `flag` none|cannot-settle|may-change-verdict, `reason` empty exactly when
  the flag is `none`); else **20**, nothing under H changes. Delivered: each line as the auditor wrote it, `agrees_with`
  x or y replaced by `labeller-1` or `labeller-2` by the map; `labels/audit/<run>.map.json` = `{<id>: {"x": 1|2, "y":
  2|1}}` for the run's cases, written at delivery only (never by a dry build or a rejection, never in the wall);
  `labels.jsonl` rewritten, its old bytes first copied into `labels/history/` (one new file, its name free): flag `none`
  → the auditor's `label` and `how: "audit"`; flagged → `how: "owner"`; every other line unchanged; `owner.jsonl` gains
  one line per flagged case, in order, carrying its `id` (both labels and the decision; other keys free). **No
  `AUDITS.log` line, ever** (a memory writer's `last_audit` is untouched).

### The results (S28)

`indep-schemas/sgx1-<flow>-result.schema.json` for `writer-tuning`, `writer-heldout`, `labeller`, `labeller-2`,
`overlap-auditor`: each closed (`additionalProperties: false` at every level), numbers and fixed words only, the
brief's result forms (the labellers' round 1 and round 2 both); `by_class`, `cases`, `copies`, `near_miss` objects
keyed `"1"`..`"14"`; `stopped` the brief's words (writer 1's without `not-sealed`). `counts.json`'s `out` carries each
number of the result under its own key (an object of numbers as an object); `stopped` may be carried as its fixed
word; the counts schema stays closed. An extra field: **20**, its text nowhere (counts, output, log).

## KPI lines, tests, and the outcome on `w2/integrate` `bc72066fa`

Run in the launch sandbox through the heavy slot: **80 cases: 64 failed, 13 passed, 3 skipped** (the live ones).
Every red fails on "governance/project/orchestration/tools/indep_launch.py does not exist yet" (62) or
"indep-schemas/indep-counts.schema.json does not exist yet" (2).

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `test_w2_149_refusals.py::test_s1_a_brief_byte_altered_at_the_commit_refuses_10` | red | no script |
| S1 | `test_w2_149_refusals.py::test_s1_a_wrong_hash_argument_refuses_10` | red | no script |
| S1 | `test_w2_149_refusals.py::test_s1_the_approved_line_removed_refuses_10` | red | no script |
| S1 | `test_w2_149_refusals.py::test_s1_a_brief_whose_front_matter_names_another_kind_refuses_10` | red | no script |
| S2 | `test_w2_149_refusals.py::test_s2_one_changed_byte_in_a_template_file_refuses_11` | red (6) | no script; one case per template file |
| S2 | `test_w2_149_refusals.py::test_s2_the_bytes_come_from_the_commit_not_the_working_tree` | red | no script; reading 3 |
| S3 | `test_w2_149_refusals.py::test_s3_a_wall_holding_an_entry_refuses_12_and_leaves_it_untouched` | red | no script |
| S3 | `test_w2_149_refusals.py::test_s3_an_existing_tree_folder_refuses_12_and_leaves_it_untouched` | red | no script |
| S4 | `test_w2_149_seed_content.py::test_s4_the_seed_and_its_ledger_line_come_before_every_input_and_tree_file` | red | no script |
| S4 | `test_w2_149_seed_content.py::test_s4_a_seed_newer_than_the_input_refuses_13` | red | no script; the forced reordering |
| S4 | `test_w2_149_seed_content.py::test_s4_a_missing_ledger_line_refuses_13` | red | no script |
| S5 | `test_w2_149_seed_content.py::test_s5_two_dry_builds_with_one_seed_select_the_rule_s_paths` | red | no script |
| S5 | `test_w2_149_seed_content.py::test_s5_the_argument_parser_offers_no_path_or_path_list_option` | red | no script |
| S5 | `test_w2_149_seed_content.py::test_s5_the_kind_s_inputs_are_read_only_copies_from_the_sets_root` | red (4) | no script; writer r2, checker, auditor, labeller |
| S5 | `test_w2_149_premises.py::test_s5_premise_the_rule_s_inputs_are_planted` | green (premise) | the diff, the exclusions (fnmatch and segment globs agree on every planted path) |
| S6 | `test_w2_149_refusals.py::test_s6_a_given_seed_without_dry_refuses_17` | red | no script |
| S6 | `test_w2_149_seed_content.py::test_s6_two_real_builds_draw_different_63_bit_seeds` | red | no script |
| S7 | `test_w2_149_tree_settings.py::test_s7_the_tree_is_the_archive_at_the_commit_less_the_exclusions_plain_and_read_only` | red | no script |
| S7 | `test_w2_149_tree_settings.py::test_s7_a_commit_holding_a_symlink_refuses_14_before_anything_is_built` | red | no script |
| S7 | `test_w2_149_tree_settings.py::test_s7_a_trees_folder_under_the_sets_root_refuses_17` | red | no script |
| S7 | `test_w2_149_premises.py::test_s7_premise_the_planted_commits_are_one_change_each` | green (premise) | L holds a link; each T commit one change (one byte where it says so); S unreachable |
| S8 | `test_w2_149_tree_settings.py::test_s8_the_built_wall_passes_the_rehearsal_s_f_checks` | red | no script |
| S8 | `test_w2_149_tree_settings.py::test_s8_the_settings_are_the_template_filled_for_this_wall` | red | no script |
| S8 | `test_w2_149_tree_settings.py::test_s8_the_manifest_and_the_standing_note_name_this_wall` | red | no script |
| S9 | `test_w2_149_canary_session.py::test_s9_settings_made_invalid_refuse_16_before_the_session` | red | no script |
| S9 | `test_w2_149_canary_session.py::test_s9_the_canary_s_target_is_one_only_the_wall_s_settings_and_hook_refuse` | red | no script; reading 1 |
| S9 | `test_w2_149_canary_session.py::test_s9_a_canary_whose_output_cannot_be_read_refuses_16` | red | no script |
| S9 | `test_w2_149_canary_session.py::test_s9_a_canary_that_times_out_refuses_16` | red | no script |
| S9 | `test_w2_149_canary_session.py::test_s9_a_denial_of_some_other_read_is_not_the_canary_s_refusal` | red | no script |
| S9 | `test_w2_149_premises.py::test_s9_premise_the_stub_models_claude_code` | green (premise) | restricted alone refuses outside; valid hook refuses; invalid settings ignored |
| S9 | `test_w2_149_live.py::test_s9_live_the_canary_refused_with_valid_settings_not_with_one_key_corrupted` | skipped (live) | the CTO, outside the sandbox |
| S10 | `test_w2_149_canary_session.py::test_s10_the_session_s_line_cwd_environment_and_stdin_flag_by_flag` | red | no script |
| S10 | `test_w2_149_canary_session.py::test_s10_the_session_and_the_canary_carry_setting_sources_project_and_no_user_settings_load` | red at `d1e53016e` (F11) | the canary's (and the session's) line names no `--setting-sources`; the stub loads the planted user file |
| S10 | `test_w2_149_canary_session.py::test_s10_tools_budget_and_timeout_come_from_kinds_yaml_when_the_brief_names_none` | red | no script |
| S10 | `test_w2_149_canary_session.py::test_s10_a_brief_asking_more_than_the_kind_s_budget_refuses_10` | red | no script |
| S10 | `test_w2_149_canary_session.py::test_s10_a_kinds_yaml_naming_bash_refuses_11` | red | no script |
| S11 | `test_w2_149_tree_settings.py::test_s11_the_built_wall_s_hook_refuses_each_outside_target_and_allows_its_brief_and_tree` | red | no script |
| S11 | `test_w2_149_live.py::test_s11_live_every_outside_read_is_refused_and_nothing_leaks` | skipped (live) | the CTO |
| S12 | `test_w2_149_results.py::test_s12_a_trace_under_claude_is_counted_and_reported_22` | red | no script |
| S12 | `test_w2_149_live.py::test_s12_live_no_trace_is_left_under_claude` | skipped (live) | the CTO |
| S13 | `test_w2_149_results.py::test_s13_free_text_from_out_or_the_session_reaches_no_output` | red | no script |
| S13 | `test_w2_149_results.py::test_s13_the_counts_schema_is_closed_and_every_value_typed` | red | no schema |
| S13 | `test_w2_149_results.py::test_s13_a_refusal_line_carries_its_code_reason_word_and_approved_sha256` | red | no schema |
| S14 | `test_w2_149_results.py::test_s14_a_missing_result_is_rejected_20` | red | no script |
| S14 | `test_w2_149_results.py::test_s14_a_result_failing_its_kind_s_schema_is_rejected_20` | red | no script |
| S15 | `test_w2_149_canary_session.py::test_s15_a_session_past_its_timeout_is_stopped` | red | no script |
| S15 | `test_w2_149_canary_session.py::test_s15_a_session_s_child_is_stopped_with_its_process_group` | red | no script |
| S15 | `test_w2_149_canary_session.py::test_s15_a_session_ended_by_its_budget_is_stopped_and_nothing_delivered` | red | no script |
| S16 | `test_w2_149_results.py::test_s16_the_delivery_lands_only_where_the_kind_delivers` | red (4) | no script; one case per kind |
| S17 | `test_w2_149_results.py::test_s17_a_finished_wall_is_one_file` | red | no script |
| S18 | `test_w2_149_results.py::test_s18_a_launch_past_the_8000_file_budget_refuses_15` | red | no script |
| S18 | `test_w2_149_results.py::test_s18_a_launch_inside_the_budget_builds` | red | no script |
| S19 | `test_w2_149_guard_line.py::test_s19_each_documented_line_is_allowed_to_the_orchestrator` | green (guard, 6) | the hook allows each documented line today |
| S19 | `test_w2_149_guard_line.py::test_s19_the_same_line_naming_a_folder_under_the_sets_root_is_refused` | green (guard, 3) | the hook refuses `indep-walls/` after the root today |
| S19 | `test_w2_149_guard_line.py::test_s19_the_script_refuses_an_argument_naming_a_folder_under_the_sets_root_17` | red (2) | no script |
| S20 | `test_w2_149_seed_content.py::test_s20_the_overlap_is_the_declaration_s_rule_with_the_wall_s_seed` | revised (DEC-1112 (3)) | the set-up A table below |
| S20 | `test_w2_149_seed_content.py::test_s20_round_1_stages_half_json_and_nothing_of_the_actions` | revised (DEC-1112 (3)) | the set-up A table below |
| S21 | `test_w2_149_canary_session.py::test_s21_the_script_holds_no_name_matched_wait_or_stop` | red | no script |
| S21 | `test_w2_149_canary_session.py::test_s21_the_session_s_pid_and_pgid_are_recorded_in_the_run_s_counts_folder` | red | no script |
| F1 | `test_w2_149_refusals.py::test_s1_the_approved_line_removed_refuses_10` | red | no script |
| F1 | `test_w2_149_refusals.py::test_s2_one_changed_byte_in_a_template_file_refuses_11` | red | no script |
| F2 | `test_w2_149_refusals.py::test_s3_a_wall_holding_an_entry_refuses_12_and_leaves_it_untouched` | red | no script |
| F2 | `test_w2_149_refusals.py::test_f2_a_commit_that_does_not_resolve_refuses_14` | red | no script; code 14 alone |
| F2 | `test_w2_149_refusals.py::test_f2_a_commit_not_reachable_from_the_main_line_refuses_14` | red | no script |
| F3 | `test_w2_149_seed_content.py::test_s4_a_seed_newer_than_the_input_refuses_13` | red | no script |
| F3 | `test_w2_149_refusals.py::test_s6_a_given_seed_without_dry_refuses_17` | red | no script |
| F3 | `test_w2_149_seed_content.py::test_s5_the_argument_parser_offers_no_path_or_path_list_option` | red | no script |
| F4 | `test_w2_149_canary_session.py::test_s9_settings_made_invalid_refuse_16_before_the_session` | red | no script |
| F4 | `test_w2_149_canary_session.py::test_s9_the_canary_s_target_is_one_only_the_wall_s_settings_and_hook_refuse` | red | no script |
| F5 | `test_w2_149_canary_session.py::test_s10_the_session_s_line_cwd_environment_and_stdin_flag_by_flag` | red | no script |
| F6 | `test_w2_149_results.py::test_s13_free_text_from_out_or_the_session_reaches_no_output` | red | no script |
| F7 | `test_w2_149_results.py::test_s14_a_result_failing_its_kind_s_schema_is_rejected_20` | red | no script |
| F7 | `test_w2_149_results.py::test_s16_the_delivery_lands_only_where_the_kind_delivers` | red | no script |
| F8 | `test_w2_149_results.py::test_s17_a_finished_wall_is_one_file` | red | no script |
| F8 | `test_w2_149_results.py::test_s18_a_launch_past_the_8000_file_budget_refuses_15` | red | no script |
| F9 | `test_w2_149_canary_session.py::test_s15_a_session_s_child_is_stopped_with_its_process_group` | red | no script |
| F9 | `test_w2_149_canary_session.py::test_s21_the_script_holds_no_name_matched_wait_or_stop` | red | no script |
| F10 | `test_w2_149_premises.py::test_f10_every_launch_runs_on_planted_roots` | green (guard) | the planted-roots tripwire refuses a real HOME or sets root |

### The F11 follow-up (DEC-1112 (3)), on `w2/integrate` `d1e53016e` (W2-149 merged, S10 changed)

One case added for S10's change, plus the stub's user-source rule (above); no earlier case adjusted (none asserts the
exact flag list or its length); the live S11 case asserts nothing about the command line (a real `claude`, no argv
record), so nothing was added there, and no case writes into the real `~/.claude/`.

- `test_s10_the_session_and_the_canary_carry_setting_sources_project_and_no_user_settings_load`: a planted
  `<HOME>/.claude/settings.json` (allow `Bash(*)`, `Read(*)`, `Edit(*)`, `Write(*)`; `defaultMode: acceptEdits`; a
  `SessionStart` and a `PreToolUse` hook that append to a log). First the premise, the stub driven directly: no flag
  and `user,project` load it (the hook runs), `project` does not. Then a good writer launch: each of the two calls
  gives `--setting-sources` exactly once, `project`; neither loaded the user file; the user hooks never ran; exit 0,
  `delivered`; one canary, one session; the canary refused by the wall's own settings' hook.
- **Outcome** (the launch sandbox, the heavy slot): **81 cases: 1 failed (the new one), 77 passed, 3 skipped (live)**.
  The new case fails on "the canary's line gives --setting-sources []; want exactly ['project']".
- **A check of the case:** the merged script run as a program behind a throwaway `PATH` shim (scratch only, never
  committed) whose `claude` adds only `--setting-sources project` before the stub: the new case and the other S9 and
  S10 cases pass (the flag-by-flag case's prompt-constant check reads the wrapper's text, the shim's own artefact).

Every refusal case (codes 10-17) also asserts nothing built (the kind's wall listing, the trees folder and
`SEEDS.log` unchanged, no `claude` started; for 12 the planted entries' hashes) and then a second, good `--dry` launch
for the same kind and set (`assert_good_launch`).

### Set-up A's wiring (DEC-1112 (3), DEC-1113), on `w2/integrate` `ce1e9d0df`

New cases in `test_w2_149_setup_a_stage.py`, `test_w2_149_setup_a_rules.py`, `test_w2_149_setup_a_audit.py`,
`test_w2_149_setup_a_delivery.py` (support: `w2_149_setup_a.py`), and four revised. "Stage 10 today": the merged script
refuses every set-up A brief with 10 (no `model`, no `result_schema`, the labellers and the auditor no `sample`), so a
case that needs a set-up A launch to build or deliver fails on "exit 10" there.

| KPI line | Test (node id) | Today | Why red (or green) |
|---|---|---|---|
| S22 | `test_w2_149_setup_a_stage.py::test_s22_premise_the_planted_briefs_carry_the_approved_front_matter_byte_for_byte` | green (premise) | the five front matters' sha256s are the approved ones; no `model`/`result_schema`; `sample` only in the writers' |
| S22 | `test_w2_149_setup_a_stage.py::test_s22_the_template_s_kinds_yaml_gives_a_model_per_kind_and_the_five_briefs_entries` | red | the template's `kinds.yaml` has no `model` and no `briefs:` |
| S22 | `test_w2_149_setup_a_stage.py::test_s22_each_approved_set_up_a_brief_passes_stage_10_in_a_dry_build` | red (5) | stage 10 today |
| S22 | `test_w2_149_setup_a_stage.py::test_s22_a_front_matter_value_beats_the_entry` | red | stage 10 today (no `sample`) |
| S22 | `test_w2_149_setup_a_stage.py::test_s22_an_entry_of_another_kind_refuses_10` | red (2) | today it builds (exit 0): every value is in the front matter and no entry is read |
| S22 | `test_w2_149_setup_a_stage.py::test_s22_a_labeller_brief_with_no_entry_refuses_10` | red (2) | today the generic labeller brief and an unknown id build (exit 0) |
| S22 | `test_w2_149_setup_a_stage.py::test_s22_a_value_found_nowhere_refuses_10_and_the_approved_brief_of_its_flow_builds` | red (2) | the 10 holds today; the approved brief of the flow then fails at stage 10 |
| S23 | `test_w2_149_setup_a_stage.py::test_s23_the_template_s_tree_exclude_leaves_out_the_briefs` | red | `tree-exclude.txt` lacks `governance/project/indep-briefs/**` |
| S23 | `test_w2_149_setup_a_stage.py::test_s23_a_set_up_a_tree_leaves_out_its_entry_s_globs_and_a_memory_writer_s_keeps_them` | red | stage 10 today (and the memory writer's tree holds the briefs) |
| S24 | `test_w2_149_setup_a_stage.py::test_s24_premise_the_seal_commits_are_one_change_each` | green (premise) | PU, PC: one path-map change each, as stated |
| S24 | `test_w2_149_setup_a_stage.py::test_s24_writer_1_stages_its_selection_by_s5_s_rule` | red | stage 10 today |
| S24 | `test_w2_149_setup_a_stage.py::test_s24_writer_2_s_seal_json_says_whether_the_seal_is_in_the_path_map` | red (3) | stage 10 today; B true, PU and PC false |
| S24 | `test_w2_149_setup_a_stage.py::test_s24_labeller_1_round_1_stages_the_half_s_lines_kept_to_the_brief_s_fields` | red (2) | stage 10 today; one per half |
| S24 | `test_w2_149_setup_a_stage.py::test_s24_round_2_stages_round_1_s_delivered_files` | red | stage 10 today (round 1) |
| S24 | `test_w2_149_setup_a_stage.py::test_s24_a_round_1_file_changed_since_its_counts_refuses_10` | red | stage 10 today (round 1) |
| S24 | `test_w2_149_setup_a_stage.py::test_s24_a_missing_input_refuses_10_before_anything_is_written` | red (4) | the 10 holds today (stage 10); the same launch then fails to build with its input there |
| S24 | `test_w2_149_setup_a_stage.py::test_s24_a_set_that_is_not_the_flow_s_half_refuses_17` | red (5) | exit 10 (stage 10), not 17 |
| S20 | `test_w2_149_seed_content.py::test_s20_the_overlap_is_the_declaration_s_rule_with_the_wall_s_seed` | red (revised) | stage 10 today (labeller 2's round 1) |
| S20 | `test_w2_149_seed_content.py::test_s20_round_1_stages_half_json_and_nothing_of_the_actions` | red (revised) | stage 10 today |
| S25 | `test_w2_149_setup_a_rules.py::test_s25_no_bwrap_refuses_18` | red | stage 10 today (round 1); runs in the default run |
| S25 | `test_w2_149_setup_a_rules.py::test_s25_the_good_rule_script_s_labels_and_the_sample_are_staged` | skipped (`bwrap`); red outside | stage 10 today |
| S25 | `test_w2_149_setup_a_rules.py::test_s25_a_rule_script_that_breaks_its_confinement_refuses_18` | skipped (`bwrap`, 5); red outside | stage 10 today; a file, a socket, a process, the cap, a missing id |
| S26 | `test_w2_149_setup_a_rules.py::test_s26_a_hand_file_missing_a_required_id_is_rejected_20` | skipped (`bwrap`); red outside | stage 10 today |
| S26 | `test_w2_149_setup_a_rules.py::test_s26_a_complete_hand_file_merges_hand_over_script` | skipped (`bwrap`); red outside | stage 10 today; also S16's labeller 1 round 2 |
| S27 | `test_w2_149_setup_a_audit.py::test_s27_the_disputes_their_x_y_order_and_the_tickets_are_staged_by_rule` | red | stage 10 today |
| S27 | `test_w2_149_setup_a_audit.py::test_s27_a_delivered_audit_maps_x_y_back_and_writes_the_labels_by_rule` | red | stage 10 today; the 40/5 split, the map, AUDITS.log, a memory writer's selection |
| S27 | `test_w2_149_setup_a_audit.py::test_s27_a_decisions_file_out_of_rule_is_rejected_20` | red (4) | exit 10 (stage 10), not 20 |
| S16 | `test_w2_149_setup_a_delivery.py::test_s16_set_up_a_writers_deliver_their_cases_to_the_half_s_planted_folder` | red (2) | stage 10 today |
| S16 | `test_w2_149_setup_a_delivery.py::test_s16_each_labeller_s_round_1_keeps_its_files_in_the_half_s_round_1_folder` | red (2) | stage 10 today |
| S16 | `test_w2_149_setup_a_delivery.py::test_s16_labeller_2_s_round_2_delivers_its_labels_to_labels_2_jsonl` | red | stage 10 today |
| S16 | `test_w2_149_setup_a_delivery.py::test_s16_an_existing_set_up_a_destination_refuses_20` | red (2) | exit 10 (stage 10), not 20 |
| S16 | `test_w2_149_setup_a_delivery.py::test_s16_a_set_up_a_delivery_is_all_or_nothing` | red | exit 10 (stage 10), not 20 |
| S16 | `test_w2_149_setup_a_rules.py::test_s26_a_complete_hand_file_merges_hand_over_script` | skipped (`bwrap`); red outside | labeller 1 round 2's destination |
| S16 | `test_w2_149_setup_a_audit.py::test_s27_a_delivered_audit_maps_x_y_back_and_writes_the_labels_by_rule` | red | the auditor's destinations |
| S16 | `test_w2_149_results.py::test_s16_the_delivery_lands_only_where_the_kind_delivers` | green (revised, 3) | writer, checker, auditor unchanged; the labeller param removed |
| S28 | `test_w2_149_setup_a_delivery.py::test_s28_each_flow_s_result_schema_is_closed_and_takes_the_brief_s_forms` | red (5) | the five schemas do not exist yet |
| S28 | `test_w2_149_setup_a_delivery.py::test_s28_an_extra_free_text_field_is_refused_20_without_a_trace` | red (6), skipped (`bwrap`, 1) | exit 10 (stage 10), not 20 |
| S28 | `test_w2_149_setup_a_delivery.py::test_s16_set_up_a_writers_deliver_their_cases_to_the_half_s_planted_folder` | red | each delivery's result form accepted, its numbers in counts |
| S5 | `test_w2_149_seed_content.py::test_s5_the_kind_s_inputs_are_read_only_copies_from_the_sets_root` | red (revised, 1 of 4) | the labeller param is set-up A's labeller 1 now: stage 10 today; the other three green |
| F11 | `test_w2_149_setup_a_rules.py::test_s25_a_rule_script_that_breaks_its_confinement_refuses_18` | skipped (`bwrap`); red outside | a rule script run unconfined, or its failure treated as a pass |
| F11 | `test_w2_149_setup_a_rules.py::test_s25_no_bwrap_refuses_18` | red | stage 10 today |
| F11 | `test_w2_149_setup_a_audit.py::test_s27_the_disputes_their_x_y_order_and_the_tickets_are_staged_by_rule` | red | an x/y map or a labeller's other work inside the auditor's wall |
| F11 | `test_w2_149_setup_a_audit.py::test_s27_a_delivered_audit_maps_x_y_back_and_writes_the_labels_by_rule` | red | an AUDITS.log line from the overlap auditor |
| F11 | `test_w2_149_setup_a_delivery.py::test_s16_a_set_up_a_delivery_is_all_or_nothing` | red | a set-up A delivery anywhere but its flow's destination |

**Revised cases** (each commit carries `Rewrite-Reason: DEC-1112 (3) (set-up A's wiring: S16, S20 changed, the
labeller kind's flows replaced)`); every other earlier case's behaviour is unchanged:

1. `test_w2_149_seed_content.py::test_s5_the_kind_s_inputs_are_read_only_copies_from_the_sets_root[labeller-1]`: the
   generic labeller brief now refuses 10 (S22), so the param stages set-up A's first labeller on the held-out half
   (`half.json`, the projected `actions.jsonl` and `cases.jsonl`, no `selection.json`); writer, checker, auditor as were.
2. `test_w2_149_seed_content.py::test_s20_the_overlap_is_the_declaration_s_rule_with_the_wall_s_seed` (was
   `..._ten_percent_rounded_up_drawn_with_the_second_run_s_seed`): S20 changed, the declaration's rule, not
   `random.Random`; on the half's staged lines, after a delivered round 1.
3. `test_w2_149_seed_content.py::test_s20_round_1_stages_half_json_and_nothing_of_the_actions` (was
   `..._no_other_input_differs_between_the_two_labellers`): S20's round-1 clause; the two labellers' inputs differ by
   design now.
4. `test_w2_149_results.py::test_s16_the_delivery_lands_only_where_the_kind_delivers`: the `labeller` param (old
   destination `labels/<run>.jsonl`) removed; set-up A's deliveries are the new S16 cases.

**Support changes** (no earlier case's expectation moved): `REASONS` gains 18; the planted repository gains the set-up
A files above (in A) and the commits PU, PC; the planted `kinds.yaml` is the tests' own with the same four kinds,
tools, budgets and timeouts plus models and the `briefs:` map (every earlier brief names its model, so the kind's model
never applies to them); the stub gains three session programs (`hand_labels`, `labels2`, `decide`: a session that
reads its own `input/` and writes what its brief asks, so a run whose seed the script draws still answers its own ids);
`World.exp` and `World.half`.

**Outcome** (the launch sandbox, the heavy slot): `gov accept W2-149` **149 cases: 61 failed, 76 passed, 12 skipped**
(3 `live`, 9 `bwrap`), none unmapped; the lines failing are S5 (its labeller param), S16, S20, S22-S28 and F11, each
red for the reason in the rows above; every other line passes (no earlier case went red). The pytest run with
`-m "not local_only" -k "not real and not green_here and not time_limit"` gives 61 failed, 75 passed, 12 skipped (the
`-k` leaves out `test_s6_two_real_builds_draw_different_63_bit_seeds`, green in `gov accept`).

**A check of the cases themselves** (scratch, never committed): each planted rule script run unconfined with the
system python passes with its marker inside its labels (the file's, the listener's, the child's), the looping one never
ends and the dropping one gives one id fewer, so a confined 18 means the confinement held; no script's source holds its
marker; the stub's programs write a valid hand file and decisions file and each `bad` variant breaks the README's rule;
the planted YAML parses. No sketch of the script was written for this follow-up: the green side is unproven until the
engineer's script runs them.

## Notes and limits

- **N-1. `--dry` leaves its wall.** The cases inspect a built wall (S4, S5, S7, S8, S20) through `--dry`. On the real
  sets root a dry wall stays under `indep-walls/`, which no guarded session can remove; dry runs belong on a planted
  sets root (or a later `--pack <run>`), a decision for the CTO.
- **N-2. Absolute or `..` archive members** cannot be planted with git (it refuses such trees); only the link case
  is tested (S7). The extraction check is stated, not tested.
- **N-3. The live cases** were not run here (no real session in the sandbox). Their checks follow the rehearsal's
  `live_sessions` step; a model that declines with no tool call is retried up to three times.
- **N-4. Fixed lists** (the writer's `kind`/`area`, the auditor's classes) are first versions; a brief that revises
  them changes the result schemas with its own approval, and these cases' `GOOD_RESULT` with them.

## Files

- `w2_149_support.py`: the planted repository and world, the stub `claude`, the test hook, the oracles.
- `conftest.py`: the session's repository, each case's world, the `live` marker and its switch.
- `test_w2_149_refusals.py` (S1-S3, S6, code 14), `test_w2_149_seed_content.py` (S4-S6, S20),
  `test_w2_149_tree_settings.py` (S7, S8, S11), `test_w2_149_canary_session.py` (S9, S10, S15, S21),
  `test_w2_149_results.py` (S12-S14, S16-S18), `test_w2_149_guard_line.py` (S19), `test_w2_149_live.py` (live),
  `test_w2_149_premises.py` (premises, F10).
- Set-up A's wiring: `w2_149_setup_a.py` (the planted halves, the planted rule scripts, the flows' launches, the
  oracles), `test_w2_149_setup_a_stage.py` (S22-S24), `test_w2_149_setup_a_rules.py` (S25, S26),
  `test_w2_149_setup_a_audit.py` (S27), `test_w2_149_setup_a_delivery.py` (S16's set-up A flows, S28).
- **N-5. S19's documented labeller line** still names the generic `labeller.md` and `--set sandbox-guard-exp-1`: those
  cases drive only the guard hook (no launch), so S16, S20 and S22 do not reach them and they are unchanged; the CTO's
  real set-up A lines name `indep-briefs/sgx1/<name>.md` and `--set tuning|held-out`.
