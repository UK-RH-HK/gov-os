# W2-149 — the independent test designer's brief (DAEO-52ku)

You are the independent test designer for **W2-149** (`.tickets/DAEO-52ku.md`): the independent sessions' launch
script, which builds one walled folder per job (writer, checker, auditor, labeller) from an owner-approved brief and
template, chooses the content by rule from a seed recorded first, guards the wall's settings with a canary, starts one
closed headless `claude -p` session in it, and returns only counts (the owner's DEC-1101 (2)-(3) step 2, DEC-1109 (2)).
Read the ticket in full first, including its body's "Readings settled by the CTO" (reading 1 corrects LAUNCH-SPEC's
canary: read it closely), then `.gov-runtime/scratch/ref/LAUNCH-SPEC.md` in your worktree in full: its §1 to §5 are the
specification, its §6 the KPI lines. The ticket's KPI lines S1 to S21 and its ten failure lines are what you test.
Profile FULL: thorough, every success and failure line with its edge cases, every refusal code refusing on its own.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-149-tests`, branch `w2/W2-149-tests`, made from `w2/integrate` today.
- You write only `tests/acceptance/W2-149/`: the cases, a `conftest.py` and support module(s) (the planted builders and
  the stub `claude`), and a `README.md` whose map the runner reads (header `| KPI line | Test (node id) | On integrate |
  Why |`, one id such as `S1` in each KPI cell, the test in backticks with its full node id, as
  `tests/acceptance/W2-133/README.md`).
- **State the interface in the README,** so the engineer builds to it. The script is
  `governance/project/orchestration/tools/indep_launch.py` (nothing there yet), with its schemas in
  `governance/project/orchestration/tools/indep-schemas/`. The command line and the exit codes are LAUNCH-SPEC's §1
  and §5; fix what they leave open, as small as the KPI lines need:
  - how the cases plant every location (the ticket's reading 2): the repository (the git top level of the folder the
    script runs in), HOME (`~/gov-os-wall-trees/`, `~/gov-os-runs/indep/`), the sets root; the one environment
    override each for the runs folder and the trees folder, and where a run says it used one;
  - `APPROVED`'s line forms: the template lines as the live file has them, `<sha256>  template
    governance/project/indep-walls/<name>` (two spaces; `#` lines are comments; ACT-INDEP-WALLS-1's `apply.sh`), and
    the brief line you fix (e.g. `<sha256>  brief <kind> <repository path>`), which the operator will write at step 3;
  - the brief's front matter (the ticket's reading 4), the run id's form (LAUNCH-SPEC B1), `SEEDS.log`'s and
    `AUDITS.log`'s line forms, `selection.json`'s and `WALL.json`'s keys;
  - where the auditor's misses, the labellers' rulebook and actions and the writer's round-2 inputs are read from in
    the sets root (reading 5), and each kind's destination (S16);
  - the counts schema's file name and every field (LAUNCH-SPEC §4), and each kind's `out/result.json` schema (its
    numeric fields, the fixed lists for the writer's `kind` and `area`, the auditor's classes);
  - the stub `claude`'s contract: what it reads (argv, `--settings`, the prompt), how it tells the canary from the real
    session, what JSON it writes (`session_id`, `is_error`, `subtype`, `num_turns`, `total_cost_usd`, `duration_ms`,
    `permission_denials` with `tool_name` and `tool_input`), and how it models Claude Code: a `--settings` file it
    cannot parse or validate is ignored without a word; with the settings loaded, the canary's Read is refused only
    when the wall's hook (the command in the loaded settings, run as Claude Code would) refuses it; a case can make it
    write `out/` files, sleep, spawn a child, or end on its budget;
  - the test hook (an environment variable, e.g. `GOV_INDEP_TEST_HOOK=<executable>` run at named points) that S4's
    forced reordering uses; the clean session environment never carries it;
  - the result line printed on stdout (the counts, `status`, and on a refusal the code and a fixed reason word).
  Name what you leave to the engineer.
- **Your record:** your whole return (the twelve fields below) is your session's **final message**, in full: the
  launcher keeps it in this worktree's `.gov-runtime/scratch/lead/log/W2-149-designer.json`, which is the record (your
  session cannot write that folder itself, and its own scratchpad is deleted when it ends).
- **You may read:** any code and record on `w2/integrate` in your worktree: the ticket, `ACT-INDEP-WALLS-1.md` under
  `governance/project/orchestration/packages/`, the walls' template (`governance/project/indep-walls/`: `kinds.yaml`,
  `settings.json.tmpl`, `wall_hook.py`, `CLAUDE.md.tmpl`, `tree-exclude.txt`, `README.md`), `governance/project/path-map.yaml`
  (its `sets_root` and `sets_root_hidden`), `.claude/hooks/pretooluse.py` (S19), and `tests/unit/orchestration/` for how
  the CTO's committed tools are tested. Reference copies from the CTO's scratch are in
  `.gov-runtime/scratch/ref/`: `LAUNCH-SPEC.md`, `REHEARSAL.md`, `walls_check.py` (its `wall` F checks for S8 and its
  `repo` W5/W6 classes for S19: reuse their logic in your own cases), `rehearse.sh` (its `live_sessions` step for S11)
  and `verdict.py`.
- **The template folder's name and the guard:** `indep-walls` is under the sets root's hidden glob, and the guard's line
  rule refuses a Bash line that names it next to a path. Read its files with the Read tool; never name the folder in a
  Bash command line. Your cases reach it from Python code (they copy the template into the planted repository).

## What the cases must show (from the ticket)
- **S1 to S3, S6, S14 to S15, S18 (the refusals):** each code refusing on its own with every other check passing in the
  same planted set-up; nothing built (the planted `indep-walls/<kind>/` listing, the trees folder and `SEEDS.log`
  unchanged); and the first failure line: after every refusal code, a second, good launch for the same kind and set
  still builds (no half-built wall left to build into).
- **S2:** six cases, one per template file. **S1:** three. **S3:** a planted entry in the wall, the tree folder planted.
- **S4, S5, S20 (the seed and the content):** mtimes in ns and hashes; the forced reordering through the test hook
  (code 13); the selection recomputed in your own code from the planted repository (`git diff --name-only`, the
  exclusions, `random.Random(seed).sample`); two `--dry` builds with one seed identical; the overlap 10 % rounded up.
- **S7, S8 (the tree and the settings):** the walk against `git ls-tree` less the exclusions; a planted commit with a
  symlink refusing; the F checks.
- **S9 (the canary):** with the stub, settings made invalid: exit 16, no `<wall>.session.json`; also a canary whose
  output cannot be read, or that times out, refusing (the fourth failure line); and that the canary's planted target is
  inside a folder the canary's command adds with `--add-dir` and outside the wall and its tree (reading 1: a target
  `--restricted` alone would refuse proves nothing). Add one case marked live: the real canary with valid settings
  refused, with one key corrupted not refused.
- **S10:** the stub's recorded argv, cwd and environment against the line, flag by flag; the tools, budget, timeout and
  model from `kinds.yaml` and the planted brief; a brief asking more than the kind's budget refusing.
- **S11, S12 (live):** the rehearsal's live step as a case marked live (the cheapest model), in planted roots with the
  runs and trees overrides and the real HOME (the session needs its login): ten outside targets, each with a marker,
  all refused; no marker out; nothing written outside `out/`; 0 traces by session id (names only).
- **S13, S16, S17:** a marker in an extra field of `out/result.json`, grepped in `counts.json`, stdout, stderr and the
  script's log; the planted sets root hashed before and after, per kind; the tar's mode, the wall and tree gone, the
  hidden part's count up by one.
- **S19:** the tree's own `.claude/hooks/pretooluse.py`, driven with each documented line as an orchestrator Bash event
  (`GOV_ROLE=orchestrator`), with a planted HOME whose sets root holds a planted `indep-walls/`: allowed; the same line
  naming `indep-walls/...` after the root: refused (and the script's own code 17 for it).
- **S21:** a source scan of the script for `pkill`, `killall`, `pgrep -f` (none); the pid and pgid files.
- Every case is red on integrate for the right reason (the script does not exist yet) unless it is a green guard; say
  which. Live cases are kept out of the default run (a marker and an environment switch you name), and run by the CTO
  outside the sandbox.

## Rules
- **Never read this ticket's implementation (G-14; DEC-820 (c)):** there is none yet; never open the engineer's
  worktree (base name `W2-149`, under the worktrees folder) or the branch `w2/W2-149` if either appears, and never read
  the engineer's files on this ticket. You work from the ticket's KPI lines, LAUNCH-SPEC and today's integrate code.
- **The exclusion line (DEC-1093 (2)), for you:** keep every Grep, Glob and recursive Bash search inside your own
  worktree. If a search must start above it, it carries the exclusion by base name: `--exclude-dir=W2-149` for grep,
  `!**/W2-149/**` for Grep and Glob, `-path '*/W2-149' -prune` for find. If a search shows you a line of the
  implementation anyway, stop reading it and say so in your return.
- **Search again once (DEC-1092 (1)):** if what you searched (Grep and Read; no `gov retrieve` in the sandbox,
  `EMG-d4b-launched.md`) does not answer, or you can tell your answer may be incomplete, search once more in your own,
  different words; then answer from both searches and the files you read, with path and lines, or say "not found".
  Two searches in all.
- **Planted folders only:** every case under a temporary folder (sets root, HOME, repositories, runs, trees). Never
  touch or read the real `~/gov-os-eval/`, `~/gov-os-runs/`, `~/gov-os-wall-trees/` or `~/.claude/` (beyond the live
  cases' names-only trace count); a case that would reach them fails closed. No real `claude` session outside a case
  marked live; no GPU, no model, no network, no installs.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder of a real tree (your planted `hidden/` folders under your temporary
  folder are yours).
- Run your cases through the heavy slot that `EMG-common.md` names (where the sandbox allows it), with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-149-tests/src`, and run
  `python3 -m gov.cli.main accept W2-149 --root /home/usain/gov-os-worktrees/W2-149-tests` to show the runner reads
  your map.
- **DEC-1080:** read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains; one line
  before any command that will ask for permission.
- **Commit** on `w2/W2-149-tests`, only `tests/acceptance/W2-149/`, with
  `--trailer "Task: DAEO-52ku" --trailer "Implements: DEC-1101" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- **Before you end your session,** make sure every test run you started has finished: do not end with a background
  run still going; any wait or stop by pid, never a name match.
- Keep to the estimate: tests about half a day; FULL, so every line covered, but one case per edge, no combinatorial
  expansion (about 50 to 80 cases).

## Return
The twelve labelled fields of `EMG-common.md` (sandbox check and `ps` check first), with the case list (node id, KPI
line, red or green on integrate, and why), the interface the README states, the commit, `gov accept`'s counts,
`TESTS-READY` text, and anything untestable or ambiguous as `discoveries` or a decision package with your
recommendation and confidence.
