Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-149/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-149 — the engineer's brief: build the launch script to the stated interface (DAEO-52ku)

You are the engineer for **W2-149** (`.tickets/DAEO-52ku.md`: read it in full, with its body's "Readings settled by
the CTO"; reading 1 corrects LAUNCH-SPEC's canary): the independent sessions' launch script, which builds one walled
folder per job (writer, checker, auditor, labeller) from an owner-approved brief and template, chooses the content by
rule from a seed recorded first, guards the wall's settings with a canary, starts one closed headless `claude -p`
session in it, delivers its product by its own code, and returns only counts (the owner's DEC-1101 (2)-(3) step 2,
DEC-1109 (2)). Read `.gov-runtime/scratch/ref/LAUNCH-SPEC.md` in your worktree in full: its §1 to §5 are the
specification, its §6 the KPI lines. The ticket's KPI lines S1 to S21 and its ten failure lines are what you build to.
Profile FULL: every check fails closed; a refusal never leaves a half-built wall.

The independent test designer has written `tests/acceptance/W2-149/` (80 cases: 77 in the default run, 64 of them red today because nothing is built, 13 green guards and premises; 3 live, run by the CTO). Its README states the interface the
cases call; the CTO hands you that section below, **from the start** (the spec, not the tests), so you build to it
without reading the cases.

**Your job:**
1. **Build `governance/project/orchestration/tools/indep_launch.py`** to the interface below, with the counts schema
   and the four kinds' result schemas in `governance/project/orchestration/tools/indep-schemas/`. Standard library,
   PyYAML and `git` only; no `gov` import (the CTO runs it standalone). It reads the walls' template
   (`governance/project/indep-walls/`: `kinds.yaml`, `settings.json.tmpl`, `wall_hook.py`, `CLAUDE.md.tmpl`,
   `tree-exclude.txt`, `README.md`) from the repository at `--commit` and never changes it. The reference builder
   `.gov-runtime/scratch/ref/build_wall.py` in your worktree shows LAUNCH-SPEC's B1 to B6 as the rehearsal built them
   (a reference, not the script: its arguments are not the interface).
2. **The canary (ticket reading 1):** its target file lies in its own temporary folder, which the canary's command adds
   with `--add-dir` (otherwise the wall's flags), so Claude Code's `--restricted` alone would allow the Read and only the
   wall's settings and hook can refuse it. A Read not in `permission_denials`, a canary that errors, times out or whose
   output cannot be read: code 16, no real session.
3. **Your own unit tests** in `tests/unit/orchestration/test_w2_149*`, and the evidence record
   `docs/changes/W2-149-evidence.md`: what you built, the counts, every red named, and what only the CTO can run
   outside your sandbox (the live cases: a real canary and a real session).

**Nothing live:** you never open the real `~/gov-os-eval/`, `~/gov-os-runs/`, `~/gov-os-wall-trees/` or `~/.claude/`,
and never start a real `claude` session (a stub on PATH in your tests). The CTO runs the live cases outside the sandbox.

## Where you work
- `/home/usain/gov-os-worktrees/W2-149`, branch `w2/W2-149` (from `w2/integrate`, with `w2/W2-149-tests` merged in).
  Your paths are the ticket's `allowed_paths`: `governance/project/orchestration/tools/indep_launch.py`,
  `governance/project/orchestration/tools/indep-schemas/**`, `tests/unit/orchestration/test_w2_149*`,
  `docs/changes/W2-149-evidence.md`.
- **You never read `tests/acceptance/W2-149/`** (G-14; DEC-820 (c)): only `gov accept`'s results. **The exclusion line
  (DEC-1093 (2)), by base name:** every recursive grep carries `--exclude-dir=W2-149`; every Grep or Glob call that
  could reach the folder carries `!tests/acceptance/W2-149/**`; find carries `-path '*/W2-149' -prune`. Start your
  searches from relative paths inside your worktree (`.`, `governance/`, `src/`), never from its absolute path (grep's
  `--exclude-dir` would skip the worktree itself, which is also named `W2-149`). If a search shows you a line of the
  cases anyway, stop reading it and say so in your return.
- **The template folder's name and the guard:** `indep-walls` is under the sets root's hidden glob, and the guard's line
  rule refuses a Bash line that names it next to a path. Read its files with the Read tool; never name the folder in a
  Bash command line (your code builds the name itself).
- You may read any code and record in your worktree: the ticket, `ACT-INDEP-WALLS-1.md` under
  `governance/project/orchestration/packages/`, the template, `governance/project/path-map.yaml` (`sets_root`,
  `sets_root_hidden`: the hidden part's walk for S18), `.claude/hooks/pretooluse.py` (S19: your documented lines must
  pass it; read how its line rule and its walk work), and `.gov-runtime/scratch/ref/` (`LAUNCH-SPEC.md`,
  `REHEARSAL.md`, `build_wall.py`, `walls_check.py`).

## Verify
- Through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
  with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-149/src`: your unit tests; then
  `python3 -m gov.cli.main accept W2-149 --root /home/usain/gov-os-worktrees/W2-149` (counts per line, results only).
  Name every red with its cause; a case that cannot pass in your sandbox (say why) is run by the CTO outside it.
- **Commit as you go**, each part as it passes, so a session that ends early leaves its work committed.

## Rules
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder of a real tree. No GPU, no model, no network, no installs, no service.
- DEC-1080: Read and Grep tools; one simple command per Bash call; no `cd … &&` chains. Search again once
  (DEC-1092 (1)) if needed.
- Do not merge `w2/integrate`. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- Waits and stops by pid or pgid only, never a name match (L-0075), in your code and your session.
- **Commit** on `w2/W2-149` with
  `--trailer "Task: DAEO-52ku" --trailer "Implements: DEC-1101" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished.

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it in this worktree's
`.gov-runtime/scratch/lead/log/W2-149-engineer.json`; it is the record): the twelve labelled fields of `EMG-common.md`
(sandbox and `ps` checks first), what you built, `gov accept W2-149`'s counts per line, the unit counts, every red
named, and any place where the interface and a KPI line disagree (the KPI line wins: say so, with the case's failure
message).

---

# The interface the acceptance cases assume (the designer's README, as written)

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
  commit; 15 file budget; 16 canary; 17 argument; 20 result rejected; 21 stopped; 22 a trace. Fixed here:
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
  `input/misses.jsonl` ← `runs/<audit>/misses.jsonl`; labeller `input/rulebook.md` ←
  `fixtures/evaluation/sandbox-guard-exp-1/hidden/rulebook.md` and `input/actions.jsonl`: round 1 the bytes of
  `.../hidden/corpus/actions-r1.jsonl`; round 2 (the second labeller) the lines of `.../corpus/actions-r2.jsonl`
  and the overlap's lines, the overlap = `random.Random(seed).sample(<ids of actions-r1.jsonl in file order>,
  ceil(n / 10))` (each line a JSON object with `"id"`), recorded in `selection.json` `overlap` in draw order.
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
- **The session:** `timeout --kill-after=<s> <timeout_s> claude -p --restricted --settings
  <wall>/.claude/settings.json --add-dir <tree> --tools <the kind's, comma-joined> --no-session-persistence
  --strict-mcp-config --disable-slash-commands --permission-prompts none --model <brief's> --max-budget-usd
  <brief's or kind's> --output-format json "<prompt>"`, cwd the wall, stdin `/dev/null`, stdout to
  `<wall>.session.json`, environment exactly `HOME PATH LANG USER` (the script's own values), in its own process
  group. The prompt: one line, naming `brief.md` and `out/result.json`, no absolute path; its sha256 written in the
  script's source as a 64-hex literal.
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
  - labeller `{"labelled", "allow", "refuse": int}` (+ `agree`, `disagree`); delivers `out/labels.jsonl`.
  Missing, failing, or the delivered file missing: **20**, `status: rejected`, nothing delivered.
- **Destinations** (S16): writer `fixtures/evaluation/<set>/hidden/` (round 1: must not exist); checker
  `fixtures/evaluation/<set>/XCHECK-r<round>.md`; auditor `runs/<audit>/miss-classes.json` (and `AUDITS.log` gains
  `{"commit": <the run's>}` once delivered); labeller `fixtures/evaluation/sandbox-guard-exp-1/hidden/labels/<run>.jsonl`.
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
| `delivered` | `{files, sha256, to}`, `to` in `set notes classes labels` or null |
| `traces` | integer |
| `status` | `delivered`, `rejected`, `refused`, `stopped`, `dry` |
| `code`, `reason` | the exit code; null, or the code's fixed word: 10 `brief`, 11 `template`, 12 `wall_exists`, 13 `seed_order`, 14 `commit`, 15 `file_budget`, 16 `canary`, 17 `argument`, 20 `result`, 21 `stopped`, 22 `trace` |

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
decision). It writes `{"type": "result", "subtype", "is_error", "session_id", "num_turns", "total_cost_usd",
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

# The open points, settled by the CTO (2026-11-09) [DEC-1101 (2)-(3)]

- **P-W2-149-DRY, option (a):** `--dry` belongs on planted sets roots only (it leaves its wall for inspection); say so
  in the script's `--help` text and in the evidence record. No `--pack` option.
- **A refusal after B1 (13, 16, and any later refusal):** the wall is packed as in S17 (`<run>.tar`, 0400, holding the
  wall and any session file), its folder and its tree removed, `status: refused`; the hidden part grows by one file.
  A refusal at 12 leaves the planted entries untouched; refusals before B1 write nothing under the sets root.
- **Writer round 2's delivery:** all or nothing, and never a moment with the questions outside a hidden folder: the
  new set is copied under a temporary name **inside** `fixtures/evaluation/<set>/hidden/` (e.g. `.r2-<run>.tmp/`),
  hashed, then swapped in by renames within `hidden/`; round 1's files go into the run's tar, not beside `hidden/`.
- **A missing input** (the set, the misses, the rulebook, the actions): refused before anything is written, with code
  **10** and reason `brief` (the brief's job cannot be built from what is there); name it in the evidence record.
- **The canary's limit and `--kill-after`:** as you choose within the interface; state them in the evidence record.
