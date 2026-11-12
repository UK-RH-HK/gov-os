# W2-149 (DAEO-52ku): FULL review of the independent sessions' launch script, merged (independent auditor)

You are a fresh **independent auditor** (Opus 5.5, effort high, class C3; RUBRIC-2, DEC-1120: reviewers run on Opus at
high, the old max is replaced), launched by the CTO (orchestrator DAEO-sdxk, session b40cba91, 2026-11-11) under ticket
`DAEO-52ku` (W2-149) from the worktree `/home/usain/gov-os-worktrees/W2-149` (the ticket's own worktree, on branch `w2/W2-149`). Your job is one **FULL, read-only review of the
ticket's merged code at the head of `w2/integrate`**, judged on the ticket's KPI lines alone (DEC-1131), producing a probe
record text that the CTO commits as `docs/probes/DAEO-52ku/PR-DAEO-52ku.md`. You cannot write it: you return it as text.
The record is the evidence the ticket's formal close needs (BATCH-PREP section 2: the ticket is merged but has no `docs/probes/DAEO-52ku/`; it stays `in_progress` by design for rows F37 and F40 and others, and its close, and W2-173 behind it, need the probe of the final code). Nothing here is a round of changes: you find, you
do not fix.

## Step 0 and the common rules

- **Step 0, the sandbox check, reported first in your return** (the launcher's `EMG-d4b-launched.md`, copied beside this
  brief): (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-52ku','w').write('x')"` must fail; (b)
  `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b)
  failed, stop and return. Then `ps -eo pid,args` on its own (no pipe): report that no ollama or llama-server process is
  yours.
- Read first, whole: `EMG-common.md` and `EMG-d4b-launched.md` beside this brief. The CTO's lift files (`LIFT-common.md`,
  `NIGHT-common.md`) are not copied for you; their rules that apply are restated in this brief, with these changes to the old
  text: the lift's closes are done; the main tree (`/home/usain/Dynamic-Agentic-Engineering-OS`) must stay clean (you never
  write there); the next free decision id is DEC-1137 (yours to propose, never to write); your temporary folder is the
  sandbox's own `TMPDIR` (never a new `/tmp/gov-os-emg-*` folder).
- **You are read-only.** Your tools are Bash, Read, Grep and Glob; you have no Write or Edit. Write only under your own
  `TMPDIR` (a probe script goes there as an inline `python3 -I -c '...'`, or a file made one simple command at a time). Never
  `git add`, `commit`, `stash`, `checkout`, `reset`, `merge`, `push` in any repository you did not clone yourself, and never
  commit anything at all: the record is returned as text and the CTO commits it. A reviewer commit anywhere in the ticket's range
  would make the probe record invalid (DEC-137). If the Write tool is refused when you try it, do not make the file another
  way; say so in your return.
- **The guard's rules hold.** No installs. No reads of secrets or of held-out material; never open `~/gov-os-eval`,
  `~/gov-os-runs`, `~/gov-os-wall-trees`, `~/gov-os-operator`, any folder named `hidden`, `memory-verdict` or
  `memory-verdict-2`, or the real `~/.claude`. A refusal is taken, never routed round (a false refusal is worked round by an
  equivalent form, named in your return). **Refused twice for the same call: stop and say so; no third try.**
- **No real model, embedder, reranker or GPU job, and no network (DEC-1064, DEC-1065).** Never run `gov retrieve` or
  `gov context`; read code with Grep and Read. Every test of yours uses stand-ins.
- **Waits and stops by pid only** (`tools/proc.sh`: `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh`),
  never the Monitor tool, never a process-name match (`pgrep -f`, `pkill`, `killall`). Run a long command in the background and
  wait on its pid.
- **Under `.gov-runtime/` and in everything you return, write commit hashes as 12 digits** (row W2-L423's rule), and write none
  of the keywords `tools/keyword_warn.py` looks for (they are written in parts in that file; never copy them out).
- **Scratch budget: 30 GB and 2,000,000 files and folders** outside the tracked tree. Report `du -sh` and `du -s --inodes` of
  your `TMPDIR` in `evidence`, and remove your clone and probe folders when done.
- **Context:** there is no token cap: use your model's full window; before compaction the hook writes your checkpoint and the summary opens with the read-first line (the owner, 2026-11-12, replacing DEC-1118 (A)).

## The head you review: a clone of `w2/integrate`

Your own worktree is **hundreds of commits behind** `w2/integrate` and is not what is merged. Do not judge its files. Make a
clone at the start and read and run everything from it:

```
git clone -q --no-hardlinks --single-branch -b w2/integrate file:///home/usain/Dynamic-Agentic-Engineering-OS $TMPDIR/clone
git -C $TMPDIR/clone rev-parse --short=12 HEAD
```

The head was `7b5c3cb94fd9` when this brief was written. **Review the clone's head at your start** and name its 12 digits as
the record's `probed_commit`; if it is not `7b5c3cb94fd9`, run `git -C $TMPDIR/clone diff --stat 7b5c3cb94fd9 HEAD -- governance/project/orchestration/tools/indep_launch.py governance/project/orchestration/tools/indep-schemas governance/project/indep-walls tests/unit/orchestration tests/acceptance/W2-149 docs/changes/W2-149-evidence.md`
and say what moved. Run code with `PYTHONPATH=$TMPDIR/clone/src`, and with `HOME` set to an empty folder under `TMPDIR` (add
`PYTHONUSERBASE=/home/usain/.local` if the empty HOME hides pytest or another module).

## The frame: the ticket's KPI lines (judge only these, DEC-1131)

Ticket `DAEO-52ku` (`.tickets/DAEO-52ku.md` in the clone: read it whole, including its notes). Its KPI lines are below, in the
ticket's own words, with the id each takes in your verdict block. **Judge each line by what it says and by its `Verify:`
text where it has one. A thing the ticket does not state is not a finding; a thing a line does state that is not met is.**
A failed line is `"verdict": "fail"` (a failed line blocks READY, DEC-1131 (3)).

- **S1**: S1 The brief is the approved one: a launch whose brief's bytes at `--commit`, `--brief-sha256` and the `brief <kind>` line of `<sets root>/indep-walls/APPROVED` do not all agree refuses with code 10 and builds nothing. Verify: three launches in a planted sets root (one byte of the brief altered, a wrong hash argument, the line removed): exit 10 each; `indep-walls/<kind>/` unchanged; no tree folder; no `SEEDS.log` line [DEC-1101 (2)-(3)]
- **S2**: S2 The template is the approved one: one changed byte in any of the six template files (`settings.json.tmpl`, `wall_hook.py`, `CLAUDE.md.tmpl`, `kinds.yaml`, `tree-exclude.txt`, `README.md`) against its `template` line in `APPROVED` refuses with code 11. Verify: six launches, one per file: exit 11 each; nothing built [DEC-1101 (2)-(3)]
- **S3**: S3 A wall is built only into nothing: a wall folder holding any entry, or an existing tree folder, refuses with code 12 and leaves both untouched. Verify: one file planted in the wall; the tree folder planted; exit 12 each; the planted entries' hashes unchanged [DEC-1101 (2)-(3)]
- **S4**: S4 The seed comes first: `seed.txt` (0444) and its `SEEDS.log` line exist before any tree or input file: `seed.txt`'s mtime (ns) is earlier than every file under `input/` and the tree, and the ledger line's sha256 equals `seed.txt`'s. Verify: build one wall; compare mtimes (ns) and hashes; a forced reordering (a test hook writing `input/` first) refuses with code 13 [DEC-1101 (2)-(3)]
- **S5**: S5 The content is chosen by rule: `selection.json` equals the rule's result: `git diff --name-only <last audit> <commit>` less `tree-exclude.txt`, plus `random.Random(seed).sample` of the other tracked paths, sized by the brief's front matter (`sample:`); the same seed and commit give the same selection; no argument accepts a path or a path list. Verify: two `--dry` builds with one seed: identical selections; the selection recomputed independently in the test; the argument parser offers no path-list option [DEC-1101 (2)-(3)]
- **S6**: S6 The caller cannot choose the seed: a real run with `--seed <n>` refuses with code 17 (a given seed only with `--dry`); a real run's seed is drawn by the script (63 random bits). Verify: exit 17, nothing built; two real builds draw different seeds [DEC-1101 (2)-(3)]
- **S7**: S7 The tree is plain and read-only: the tree is `git archive <commit>` less `tree-exclude.txt`: no `.git`, no link, no excluded path, every file 0444, every folder 0555, outside the sets root; an archive member that is a link, an absolute path or holds `..` refuses. Verify: walk the tree; compare with `git ls-tree -r <commit>` less the exclusions (count and per-file hash); a planted commit holding a symlink refuses [DEC-1101 (2)-(3)]
- **S8**: S8 The wall's settings are the template's: `.claude/settings.json` equals the template filled for this wall, its sha256 is in `WALL.json`, its deny list holds every required class (the shell, the web, subagents, memory's search, git, the repository, the worktrees, the run outputs, `~/.claude`, the rest of the sets root, `APPROVED`, the other kinds' walls and the walls present at build time), and its one hook is the wall's own (`.claude/wall_hook.py`, byte for byte the template's). Verify: the built-wall (F) checks of the rehearsal (`walls_check.py wall`'s F class) re-expressed as cases on a built wall [DEC-1101 (2)-(3)]
- **S9**: S9 The canary guards the settings: before the real session a one-turn session in the wall, with the same flags, must come back with its Read of a file the script planted outside the wall in `permission_denials`; with a settings file made invalid on purpose the Read is not refused, and the launch refuses with code 16 before the real session. The canary's target must be one Claude Code's `--restricted` mode alone would allow (see the CTO's reading 1), so only the wall's settings and hook can refuse it. Verify: a stub `claude` modelling Claude Code (a `--settings` file it cannot parse is ignored); exit 16; no `<wall>.session.json`; live (outside the sandbox, the CTO): the real canary with valid settings refused, with one key corrupted not refused [DEC-1101 (2)-(3)]
- **S10**: S10 The session is headless and closed: the launched command carries `-p --restricted --setting-sources project --settings <wall's> --add-dir <tree> --tools <the kind's> --no-session-persistence --strict-mcp-config --disable-slash-commands --permission-prompts none --model <model> --max-budget-usd <kind's> --output-format json` and the fixed launch prompt (its sha256 a constant in the script), under `timeout --kill-after`, from the wall, stdin `/dev/null`, with an environment of `HOME`, `PATH`, `LANG`, `USER` only (no `GOV_*`, no `CLAUDE_PROJECT_DIR`); tools, budget, timeout and model come from `kinds.yaml` and the brief's front matter, never from the caller; never Bash, WebFetch, WebSearch, Task, Agent or an MCP tool; the canary carries `--setting-sources project` too, so the user's and the local settings files never load into a wall. Verify: a stub `claude` on `PATH` that records its argv, cwd and environment, and that loads a planted user settings file unless `--setting-sources` leaves the user source out [DEC-1101 (2)-(3)] [changed, DEC-1112 (3): F11]
- **S11**: S11 The walls hold in a live session: a live session in a built wall (the cheapest model) told to read each of a fixed list of outside targets (another wall, another wall's tree, `APPROVED`, a hidden set file, the sealed folder, a run folder, the transcripts folder, the seed ledger, the CTO's scratch, the repository) makes every attempt and each is refused; it reads its own brief and tree; no outside marker appears in `out/` or its output; nothing is written outside `out/`. Verify: the rehearsal's `live_sessions` step as a test marked live, in planted roots, run by the CTO outside the sandbox [DEC-1101 (2)-(3)]
- **S12**: S12 No trace is left: after a session, no file under `~/.claude/{projects,file-history,session-env,todos}` names its session id; `counts.json`'s `traces` is that count. Verify: a names-only search by session id after S11's run: 0 [DEC-1101 (2)-(3)]
- **S13**: S13 Only counts return: `counts.json` validates against `indep-counts.schema.json` (`additionalProperties: false` at every level; every value a number, a boolean, a sha256, a fixed word or the run's id: no free text); a planted `out/result.json` carrying a marker text in an extra field leaves no trace of it in `counts.json`, the printed output or the script's log. Verify: plant the marker; grep the three: 0 [DEC-1101 (2)-(3)]
- **S14**: S14 A bad result is not delivered: an `out/result.json` that is missing or fails its kind's schema gives `status: rejected`, exit 20, nothing written under the set's folder or the sealed folder. Verify: hashes of the destination folders before and after [DEC-1101 (2)-(3)]
- **S15**: S15 Budget and timeout stop it: a session past its timeout is stopped by its process group, gives `status: stopped`, exit 21, nothing delivered; the budget flag is always present; a session ended by its budget (`is_error` with the budget's subtype) also gives `stopped`. Verify: a stub `claude` that sleeps (and one that spawns a child); the process group gone afterwards, checked by pgid, never a name match [DEC-1101 (2)-(3), DEC-1073]
- **S16**: S16 The delivery lands only where the kind and its flow deliver: with no set-up A flow, a writer's `out/set/**` in `fixtures/evaluation/<set>/hidden/`, a checker's `out/notes.md` in `fixtures/evaluation/<set>/XCHECK-r<round>.md`, an auditor's `out/classes.json` in `runs/<audit>/miss-classes.json`; set-up A's flows (H the half's folder: `tuning` is `<runs>/SANDBOX-GUARD-EXP-1/tuning`, `held-out` the sealed folder `fixtures/evaluation/sandbox-guard-exp-1/hidden`): writer 1's `out/cases.jsonl` in the tuning H's `planted/cases.jsonl`, writer 2's in the held-out H's, `out/aims.jsonl` in the wall's tar only; labeller 1 round 1's `rulebook.md` and `label_rules.py` in `H/labels/r1-sgx1-labeller/`, its round 2's merged labels in `H/labels/labels.jsonl`; labeller 2 round 1's `rulebook-2.md` in `H/labels/r1-sgx1-labeller-2/`, its round 2's `labels-2.jsonl` in `H/labels/labels-2.jsonl`; the overlap auditor's decisions in `H/labels/audit/<run>.decisions.jsonl` with `labels.jsonl` rewritten (the old copy in `H/labels/history/`) and flagged cases appended to `H/labels/owner.jsonl`; an existing destination file (other than the auditor's `labels.jsonl` and `owner.jsonl`) refuses 20; nothing else changes under the sets root or `<runs>/SANDBOX-GUARD-EXP-1`; `delivered.sha256` equals the bundle's hash; the delivery is all or nothing (a temporary name, hashed, renamed). Verify: hash the planted sets root's tree and the planted experiment folder before and after, per kind and flow [DEC-1101 (2)-(3)] [changed, DEC-1112 (3): set-up A's deliveries to the scorer's names, the tuning half's to the experiment folder (the declaration §4, §5; the sandbox README's item 4)]
- **S17**: S17 A finished wall is one file: after delivery (or a rejection or a stop) the wall is packed into `indep-walls/<kind>/<run>.tar` (0400), its folder and its tree are gone, and the hidden part's file count has grown by exactly one. Verify: count before and after [DEC-1101 (2)-(3)]
- **S18**: S18 The hidden part's file budget holds: the hidden part's file count (the guard's walk of the sets root's hidden globs) plus this run's expected files is at most 8,000, else code 15 before anything is written. Verify: the planted hidden part at 7,990 files: a launch that would add more than 10 refuses with code 15 [DEC-1101 (2)-(3)]
- **S19**: S19 The CTO's line passes the guard: every documented command line of the script (one per kind, `--dry`, `--counts-only`) is allowed for the orchestrator by the tree's guard hook (`.claude/hooks/pretooluse.py`), and the same line naming a folder under the sets root (`indep-walls/...`) is refused, code 17 from the script too. Verify: the hook driven with each line as an orchestrator Bash event, with a planted HOME and sets root (the rehearsal's `walls_check.py repo` W5/W6 classes, extended with the script's real lines) [DEC-1101 (2)-(3), DEC-1097 (2)]
- **S20**: S20 The second labeller's overlap is the declaration's rule: labeller 2's round-2 `input/sample.jsonl` holds exactly the half's staged action and case lines whose `int(sha256((SEED + "overlap" + id).encode("utf-8")).hexdigest(), 16) % 10 == 0`, SEED being the wall's `seed.txt` less its newline (the declaration §5 and its amendment A5: that half's labeller-2 round-2 wall's seed); no `random.Random`; its round 1 stages `input/half.json` and nothing of the actions. Verify: two `--dry` builds with one seed: identical; the set recomputed independently in the test; round 1's `input/` listing [DEC-1101 (2)-(3), DEC-1099 (1) Q5] [changed, DEC-1112 (3): the declaration's overlap rule, not 10 % drawn with random.Random]
- **S22**: S22 Stage 10 takes the template's defaults: a brief's `model`, `result_schema` and `sample` come from its front matter, else from the `briefs:` entry of the template's `kinds.yaml` named by its front matter's `brief:` id (whose `kind` must equal the brief's), else (`model` only) from the kind's `model` in `kinds.yaml`; a value found nowhere, or an entry of another kind, refuses 10; a labeller brief with no `briefs:` entry refuses 10 (the labeller kind runs set-up A's flows only). Briefs carrying the five approved set-up A briefs' front matter byte for byte (no `model`, no `result_schema`; the labellers and the auditor no `sample`), with their lines in a planted `APPROVED` and the entries in a planted `kinds.yaml`, each pass stage 10 in a `--dry` build. Verify: the five dry builds exit 0 with `WALL.json`'s model and schema the entry's; a front-matter value beats the entry; an entry of another kind, and a missing value: 10 each [DEC-1112 (3), DEC-1113] [changed, DEC-1112 (3): added for set-up A's wiring, the briefs' bytes unchanged]
- **S23**: S23 The trees leave out what the template says: every wall's tree leaves out `governance/project/indep-briefs/**` (`tree-exclude.txt`); a set-up A brief's tree also leaves out its `briefs:` entry's `tree_exclude` globs (the guard's and the launcher's code: `.claude/**`, `src/gov/guard/**`, `src/gov/launch/**`, `governance/project/indep-walls/**`); the overlap auditor's entry also leaves out every file that states which dispute side is which labeller's: `.tickets/**`, `governance/project/orchestration/packages/**`, `governance/project/orchestration/tools/indep_launch.py`, `tests/acceptance/W2-149/**`, `tests/unit/orchestration/test_w2_149*` and `docs/changes/W2-149-evidence.md` (its tickets arrive in `input/`; its brief reads only the register, the Contract, the path map and the held-out list); a brief with no entry keeps them. Verify: walk a set-up A and a memory writer's dry-built trees against a planted commit holding files under each glob [DEC-1112 (3), DEC-803; ACT-W2-149-INSTALL-1 review F7] [changed, DEC-1112 (3): added for set-up A's wiring, the briefs' bytes unchanged] [changed, DEC-1112 (3): F38, the auditor decides from the decisions alone (DEC-1113 (2))]
- **S24**: S24 Set-up A's inputs are staged by rule, from the half's folder: `input/half.json` (`half`, `pin` = the commit; the auditor also `cases`); labeller 1's `input/actions.jsonl` and `input/cases.jsonl` from `H/corpus/actions.jsonl` and `H/planted/cases.jsonl`, each line kept to the brief's fields (`id role agent ticket wbs tool input cwd executable strata source`, and `rule_class` for a planted case); writer 2's `input/seal.json` `{"sealed": true}` only when the path map at `--commit` holds the `sandbox-guard-exp-1` set's hidden glob and `sets_root_hidden` covers it, else `{"sealed": false}`; round 2's `input/round1/` equal to round 1's delivered files, refused 10 when a file's sha256 differs from round 1's `counts.json`; a missing input refuses 10 before anything is written; `--set` names the flow's half (writer 1 `tuning`, writer 2 `held-out`, labellers and the auditor either), else 17. Verify: dry builds per flow; staged bytes compared with the planted sources [DEC-1112 (3), DEC-1113; the declaration §5, §6] [changed, DEC-1112 (3): added for set-up A's wiring, the briefs' bytes unchanged]
- **S25**: S25 The first labeller's rule script runs confined: at round 1's delivery and again at round 2 the script runs `label_rules.py` (round 1's `out/` file, then its delivered copy) under `bwrap` (no network, every namespace unshared, nothing bound but the interpreter's own files read-only, no writable file, a CPU, memory and wall-clock cap, an output cap) on the pinned python with `-I`, stdin the half's staged lines; its output must give every staged id exactly once with `label` allow|refuse|ask, `rule_class` 1-14, `clauses` a list and `uncertain` a boolean; `input/script-labels.jsonl` is that output and `input/sample.json` the ids whose `int(sha256((SEED + "labeller-sample" + id).encode("utf-8")).hexdigest(), 16) % 20 == 0`. At round 2, a planted rule script that reads a planted marker file outside it, opens a socket, starts a process, runs past the cap, or leaves out an id refuses with the new code 18 (`rules`), nothing staged; no `bwrap` refuses 18. At round 1's delivery, the same script refuses the delivery: `rejected`, 20, nothing lands in `H/labels/r1-sgx1-labeller/`, so a broken script never becomes round 1's frozen file. Verify: each planted script; the marker never appears in any staged file, output or log [DEC-1112 (3); the sandbox README item 1] [changed, DEC-1112 (3): added for set-up A's wiring, the briefs' bytes unchanged] [changed, DEC-1112 (3): F18 of the wiring's review, the check also at round 1's delivery]
- **S26**: S26 The first labeller's labels are complete before they land: round 2 delivers only when `out/hand-labels.jsonl` holds a valid line (`id label rule_class clauses reason`) for every id the script marked uncertain, every id the script put in classes 1-13, and every sample id; `labels.jsonl` is then one line per staged id, the hand label over the script's, `how` `hand` or `script`; otherwise `rejected`, 20, nothing written. Verify: a hand file missing one required id: 20 and the destinations unchanged; a complete one: the merge recomputed in the test [DEC-1112 (3); the declaration §5] [changed, DEC-1112 (3): added for set-up A's wiring, the briefs' bytes unchanged]
- **S27**: S27 The overlap auditor gets the disputes and returns decisions by rule: the disputes are the ids in both `labels.jsonl` and `labels-2.jsonl` whose `label` differs and that no earlier audit run decided, the first 40 by id per run; each case's `x`/`y` order drawn with `random.Random(seed)`, the map written to `H/labels/audit/<run>.map.json` and never into the wall; `input/disputes.jsonl` per the brief (the action without source, strata or aim; each label with `label rule_class clauses reason`; every side's `reason` is empty, so no side is told apart by it); `input/tickets.jsonl` one line per ticket a case names, its `id role wbs_id allowed_paths` from `.tickets/` at `--commit` and nothing else; `out/decisions.jsonl` validated (one line per case, in order, the same ids, the brief's fields and values, `reason` empty exactly when the flag is `none`), else 20; `x`/`y` mapped back; settled cases take the auditor's decision in `labels.jsonl` (its `label`, its `rule_class`, `clauses` = its `basis`, `reason` = its `reason`; `how` `audit`), flagged ones `how` `owner` and a line in `owner.jsonl`; no `AUDITS.log` line, ever. Verify: 45 planted disputes give runs of 40 and 5; the map recomputed from the seed; `AUDITS.log` and every memory writer's selection unchanged [DEC-1113 (2); the CTO's delegated split at 40] [changed, DEC-1112 (3): added for set-up A's wiring, the briefs' bytes unchanged] [changed, DEC-1112 (3): F21 and F22 of the wiring's review, the auditor's brief: the two labels arrive blind, and its decision replaces both] [changed, DEC-1112 (3): F36, every reason blanked]
- **S28**: S28 Set-up A's results are counts in their own schemas: each flow's `out/result.json` is checked against its own schema in `indep-schemas/` (`additionalProperties: false`; numbers and fixed words only; each round's form as the brief's result section states it) and `counts.json` carries its numbers only; an extra field refuses 20 with no trace of its text. Verify: each brief's result forms accepted; a planted extra free-text field: 20, grep of counts, output and log: 0 [DEC-1101 (2)-(3), DEC-1113] [changed, DEC-1112 (3): added for set-up A's wiring, the briefs' bytes unchanged]
- **S29**: S29 A set-up A result that says it stopped delivers nothing: when a set-up A flow's `out/result.json` (valid against its schema) has `stopped` other than `none`, nothing is delivered: `status` `rejected`, 20, `out.stopped` the word, every destination unchanged, the products in the wall's tar only. Verify: per flow, a planted `stopped` word with its out/ files present; the destinations hashed before and after [DEC-1112 (3): F19 of the wiring's review] [changed, DEC-1112 (3): added]
- **S30**: S30 The second labeller's labels are checked before they land: round 2 delivers `labels-2.jsonl` only when it holds exactly one valid line per staged sample id (`id label rule_class clauses how reason`, `label` allow|refuse|ask, `rule_class` per S31, `clauses` a list of strings, `how` `hand`, `reason` a string) and no other id; delivered with `rule_class` as an integer; otherwise `rejected`, 20, nothing written. Verify: a missing id, an extra id, a repeated id, a bad label: 20 each and the destination unchanged; a good file: its lines as delivered [DEC-1112 (3): F20 of the wiring's review] [changed, DEC-1112 (3): added]
- **S31**: S31 A rule class is a number from 1 to 14 in either form: wherever a session's line carries `rule_class` (the rule script's output, the hand labels, the second labeller's labels, the auditor's decisions), a JSON integer 1-14 or a decimal string `"1"`-`"14"` (no sign, no leading zero, no space) is accepted, and every file the script writes carries it as an integer; a boolean, a float, 0, 15 or any other string refuses as that file's check does (18 for the rule script, 20 for the others). Verify: each file with the string form accepted and stored as an integer; each bad form refused [DEC-1112 (3): F23 of the wiring's review] [changed, DEC-1112 (3): added]
- **S21**: S21 Waits and stops by pid: the script records the session's pid and pgid in the run's counts folder and waits and stops only by them. Verify: a code search for name-matched kills (`pkill`, `killall`, `pgrep -f`): none; the stop path tested with S15 [DEC-1101 (2)-(3), DEC-1073]
- **F1**: A launch that builds or starts anything when the brief's bytes, its hash argument or its APPROVED line disagree, or when a template file does not match APPROVED (fails open: an unapproved brief or wall).
- **F2**: A wall built into a folder that is not empty, or over an existing tree folder; a refusal (any code) that leaves a half-built wall a later run could build into (S3 must hold after every refusal code).
- **F3**: Content chosen, or a tree or input file written, before the seed is written and its SEEDS.log line appended; a caller-given seed accepted in a real run; a path or path list accepted from the caller.
- **F4**: A real session started when the canary's Read was not refused, or a canary whose target Claude Code's restricted mode alone would refuse (so ignored settings still pass it); a canary that errors, times out or cannot be read treated as a pass.
- **F5**: A session started with any tool beyond the kind's, without --restricted, the wall's --settings, --no-session-persistence, --strict-mcp-config or the budget, from another folder, or with any GOV_* or CLAUDE_PROJECT_DIR in its environment.
- **F6**: Free text from the session or out/ reaching counts.json, the printed output or the script's log; a path under the wall printed other than its run id.
- **F7**: A delivery from a missing or schema-failing result, from a stopped session, or partial (some files landed, some not); anything written under the sets root outside the kind's destination.
- **F8**: A wall or tree left in place after the run (the hidden part growing by more than one file per run), or a launch past the 8,000-file budget.
- **F9**: A wait or a stop by a name match; a timed-out session whose process group survives.
- **F10**: A test or the trial opening the real ~/gov-os-eval, ~/gov-os-runs/indep or ~/gov-os-wall-trees (every test on planted roots).
- **F11**: A rule script run unconfined, or its failure, timeout or partial output treated as a pass; an x/y map or a labeller's other work inside the auditor's wall; an AUDITS.log line from the overlap auditor; a set-up A delivery anywhere but its flow's destination [changed, DEC-1112 (3): set-up A's wiring]

**The verdict block carries one entry for each of these 42 ids, in this order:** S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13, S14, S15, S16, S17, S18, S19, S20, S22, S23, S24, S25, S26, S27, S28, S29, S30, S31, S21, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11. (`F1` and on are the ticket's failure lines, in the order above.)

**Scope (the ticket's `allowed_paths`; "in scope" means a finding about these files or about how the KPI lines hold through them):**

- `governance/project/orchestration/tools/indep_launch.py`
- `governance/project/orchestration/tools/indep-schemas/**`
- `governance/project/indep-walls/kinds.yaml`
- `governance/project/indep-walls/tree-exclude.txt`
- `tests/unit/orchestration/test_w2_149*`
- `docs/changes/W2-149-evidence.md`

Code outside these paths is reachable context (read it to judge a line), but a defect that lives only there is `scope: out`.

## What has changed, and what has been reviewed before (facts; judge the code, not this history)

- **No single review judged the final code against all of S1 to S31.** The ticket was reviewed in pieces, each READY by `verdict.py`
  (scratch records, none committed): round 1 (head `8d4569bfef3c`, S1 to S21; one blocking finding, repaired) and round 2
  (`a929356ea544`, S1 to S21 pass); the F11 follow-up (`--setting-sources project`, merge `ff1865184930`), narrow; set-up A's
  wiring (merge `7f0e71519f83`, review at `7df7c35e3bb7`, S16 and S20 changed, S22 to S28 added), then the wiring review's F18 to F23
  (merge `90c1fea6c7e5`, narrow), then F36 and F38 (merge `2f98aecbc525`, narrow), then the ticket's merge `b4de529b451c`. The script
  is now 2,456 lines. S1 to S21 were last judged at `a929356ea544`; most of the script's current behaviour (set-up A, the confined
  rule script, the blinded disputes, the delivery checks) has only been judged narrowly. **Judge every line afresh.**
- **Since the last narrow review nothing under the ticket's paths has changed:**
  `git -C $TMPDIR/clone diff --stat 2f98aecbc525 HEAD -- governance/project/orchestration/tools/indep_launch.py governance/project/indep-walls governance/project/orchestration/tools/indep-schemas tests/acceptance/W2-149 tests/unit/orchestration/test_w2_149_indep_launch.py tests/unit/orchestration/test_w2_149_setup_a.py docs/changes/W2-149-evidence.md`
  should print nothing (the CTO checked; check it yourself and say so). The template files under `governance/project/indep-walls/`
  other than `kinds.yaml` and `tree-exclude.txt` are ACT-INDEP-WALLS-1's, outside the ticket's paths: reachable context.
- **Known rows, carried (name one by its id if you meet it independently; a row, not a new round, unless you show a worse
  consequence than its record says):** F37 (a round-1 rejection by the rule check logs `rejected rules` without the check's own word,
  so a missing `bwrap` looks like a broken script); F40 (the overlap auditor's blind rests on the excluded places: a later record
  restating the dispute sides elsewhere would bring the tell back; the CTO dry-builds that wall and searches its tree before the
  auditor's first real run); F16 and F17 (Claude Code's `--restricted` already ignores the settings files, so `--setting-sources project`
  is a second guard, and the stub does not model that rule); F2 and F11 of round 2, which went to the owner (the path map's
  `sets_root_hidden` does not cover a new set's `hidden/`, the XCHECK notes or `runs/<audit>/miss-classes.json`: an ACT, an entry
  criterion before the first real writer run). The ticket's notes at its end give each in the ticket's own words.
- **Reading settled by the CTO (ticket, "Readings settled"):** the canary's target is planted in its own temporary folder and added by
  `--add-dir` for the canary only, so only the wall's settings and hook can refuse it; every location other than `--sets-root`
  derives from `HOME`; the brief and template bytes are read with `git show` at `--commit`, never from a working tree.


## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.
- **How reviews converge (owner, standing, DEC-1010 item 1; in force for the CTO, every lead, reviewer and QA engineer):**
  - **A moderator, not a circle of reviewers:** the QA engineer (or the Senior Engineer; until the three layers start, the CTO) triages every finding against the ticket's own scope and KPIs. A finding outside the scope, or one that needs an unusual construction, becomes a Wave 3 row, never a round.
  - **A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work.** Everything else lands as a recorded row.
  - **At most two review rounds.** If something still blocks after that, it goes to the owner once, with options; no more routine exceptions.
  - **READY is computed by code, not declared by an agent:** each reviewer returns a structured verdict per KPI line, a fenced `verdict` block in the probe record: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`; the close (and the merge queue's pre-check) computes READY from it: no finding that is in scope, ordinary work yes and fails open or loses work. A lead never writes a verdict over a reviewer's.

## What to do

1. Read the ticket, then the code in scope at the clone's head, then the tests that map to each KPI line (the acceptance
   folder's README maps lines to cases; do not take the map as proof: read what the case asserts).
2. Judge **every KPI line** pass or fail from the code and your own probes (planted folders and stand-ins under `TMPDIR`; never
   a live root). Look hardest where a failure would fail open or lose work: the refusals that must build nothing (S1 to S3 and S18, and the failure lines on a half-built wall a later run could build into after any refusal code); the seed first and drawn by the script (S4 to S6); the tree plain and read-only, and what it leaves out (S7, S23); the canary guarding the settings and the launched command and its environment (S9, S10); no free text from a session reaching `counts.json`, the output or the log (S13, S28); delivery only where the kind and its flow lands, nothing partial, nothing after a stop or a bad result (S14, S16, S24 to S30); the finished wall packed and the hidden file budget (S17, S18); waits and stops by pid (S15, S21); the confined rule script (S25); the overlap auditor's blind (S23, S27)
3. Run the **scoped** tests only, through the heavy-job gate, with this exclusion on every run of a whole folder
   (`-m "not local_only" -k "not real and not green_here and not time_limit"`) and say what it left out:
   `tests/unit/orchestration/test_w2_149_indep_launch.py` and `tests/unit/orchestration/test_w2_149_setup_a.py`, and `tests/acceptance/W2-149/` (with `GOV_TESTS_OPTIN=lifted,breadth`). The cases that need `bwrap` skip or fail in the sandbox if it is missing or blocked: name which. The three live cases (S9 live canary both ways, S11, S12) need a real `claude` and are the CTO's: never run them, and never run a real `claude`. **Every probe uses planted roots (HOME, sets root, repository) under your `TMPDIR` and a stub `claude`; never `~/gov-os-eval`, `~/gov-os-runs/indep`, `~/gov-os-wall-trees` or the real `~/.claude`** (a failure line of this ticket)
   Command form: `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env PYTHONPATH=$TMPDIR/clone/src HOME=<empty folder> PYTHONUSERBASE=/home/usain/.local TMPDIR=$TMPDIR python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`
   (add `GOV_TESTS_OPTIN=lifted,breadth` for the opt-in cases). Never the full suite (DEC-968). The CTO's own results, which you
   do not re-run: `gov accept W2-149` at the last merge, in the declared form with the `bwrap` opt-in, outside the sandbox: pass, 206 passed, 0 failed, 3 skipped (live); with every opt-in 362 passed; unit 153 passed; the 3 live cases passed (haiku, planted roots). The script's sha256 starts `90b943aef8be`, `kinds.yaml` `ddd84ae25910`, `tree-exclude.txt` `e8395088167e` (check them). If the gate or the sandbox will not run a case, say which and why; never run it outside the gate.
4. Classify each finding: id `FR-1`, `FR-2`, ... (a FULL review's own ids, so none collides with an earlier round's), its KPI line,
   `scope: in|out`, the two lines below, `Reversed by:` (what evidence would make it not a finding), and how you showed it
   (the call, the file and lines).
5. Compose the record (below) and return.

## The verdict block and the probe record form

The verdict is one fenced `verdict` block in the record, one entry for **every** KPI line above (`pass` or `fail`, with its
findings, possibly none), in exactly this form (the close computes READY from it by code; you never declare READY):

```verdict
{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "FR-1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```

The record's form is the existing probe record `docs/probes/DAEO-u4oz/PR-DAEO-u4oz.md` (read it in your clone: it is the model,
written 2026-11-11). The CTO writes its "The lead's judgement" section; **you write the rest**, between `PROBE_MD_BEGIN` and
`PROBE_MD_END`, in this order:

1. The YAML front matter, exactly these keys: `type: probe`, `task: DAEO-52ku`, `reviewer_session: not known` (the CTO fills it
   from the launch log), `implementer_session: not recorded` (the CTO fills it), `reviewer_wrote_nothing: true`,
   `commissioned_by: orchestrator`, `judged_by: orchestrator`, `judgement: pass` (only if no finding is in scope, ordinary work
   yes and fails open or loses work, and no line is marked fail; else `fail`), `probed_commit: <12 digits>` (the CTO expands it
   to the full id: the close gate needs the full id, and `.gov-runtime/` takes 12 digits).
2. `# Probe record: W2-149 (DAEO-52ku) <title>, FULL review of the merged code (DEC-1010, DEC-1131)`.
3. `## The reviewer's record (as returned)`: a short plain-language summary (does every line pass; what blocks, if anything; what
   lands as rows), then the twelve fields in a fenced block, as in the model.
4. A line `task: DAEO-52ku`, a line `decisions:` (the decisions you relied on, each as DEC-n), a line `probed_commit: <12 digits>`.
5. `**Scope.**`, `**Method.**` (the probes, with counts), `**Probed and found sound.**` (numbered, by KPI line, with file and
   lines), and `**Findings**`: each with its KPI line, `scope`, `Ordinary work: yes|no, because ...`,
   `Consequence: fails open|loses work|other`, `Reversed by:`.
6. `**Classification:**` on one line (how many yes/fails open or loses work, yes/other, and rows marked no), then the `verdict` block.

## Return

As your final message: **the twelve labelled lines first**, each label at the start of its own line (`task`, `status`,
`work_completed`, `files_changed`, `evidence`, `tests`, `discoveries`, `risks`, `lessons`, `proposed_decisions`, `unresolved`,
`recommended_next_action`), with step 0 and the `ps` check first in `evidence`, the clone's head in `evidence`, the tests and
what the exclusion left out in `tests`, `files_changed: none`; status DONE, PARTIAL or PACKAGES. Then a line `PROBE_MD_BEGIN`,
the record text of the form above, and a line `PROBE_MD_END`. Estimate: 75 to 100 minutes, about $9.
