# Lead brief: the memory measure runs on any adopted repository, by product commands (W2-204, a new feature; W2-187 and W2-188 reopened by EMERGENCY-2 §6.1)

Read `/home/usain/Dynamic-Agentic-Engineering-OS/docs/emergency-2/briefs/NIGHT-COMMON.md` first and follow it (and
`LEAD-COMMON.md`: add `-n auto` to slot runs of more than one file). Branch `e2/memaudit-adopted` from `w2/integrate`,
worktree `/home/usain/gov-os-worktrees/E2-memaudit-adopted`. **C3** (`src/gov/memaudit/**`): the test designer and the
engineer run Claude Fable 5.2 (`model: "fable"`). `Task: DAEO-<your new ticket id>`, `Class: F`.

**Why (release-blocking, EMERGENCY-2 §8.2 item 3 and §7.4):** EXAMIN's copy must reach 95 % or better end to end on a
fresh 80, measured "as Gov OS's is". The EXAMIN CTO found tonight (its F-032) that `python3 -m gov.memaudit` holds Gov
OS's own repository as constants, so no adopted repository can go from a question set to a judged figure. Gov OS's own
first fresh 80 also stopped on this module (JOB-20261116-15: the driver stops at a preflight refusal the design repairs).

**Read:**
- EXAMIN's finding and its proposal: `/home/usain/gov-os-runs/W2-27/examin/.gov-runtime/scratch/govos/REQUESTS.md`,
  the sections dated 2026-11-19 01:45 (F-032, each claim with path:line) and 01:55 (EXAMIN's side of a per-repository
  configuration), and its `evidence/MEASURE-RUNBOOK.md` beside it. Read only those; change nothing in EXAMIN.
- The module: `src/gov/memaudit/` (`tables.py` DOMAINS, SUBSYSTEMS, QUOTAS; `measure.py` the control set and its fixed
  figure; `preflight.py`, `drops.py`, `declare.py`, `driver.py`, `judge.py`, `prompts.py`, `command.py`, `__main__.py`).
- The rule: DEC-1210 (a fresh 80 per measure: 40 visible, 40 hidden, written and measured at once on a pinned
  snapshot, judged end to end at 95 %, hit@k a diagnostic), `docs/audit/emergency-2026-11/context/dec-1210-fresh-80.md`;
  the owner's E3 in DEC-1214 (an adopted repository's CTO launches an independent question writer, a fresh session that
  never sees the store's build, and runs the measure itself; the transcript scan voids a measure if the hidden half is
  read; the sets live outside the clone and are never indexed); EMERGENCY-2 §2.7, §5.3.
- The first run's findings F-1 and F-2: `.gov-runtime/scratch/orchestrator/drafts/fresh-80/P-FRESH-80-1.md` §6 and
  `JOB-20261116-17.md` beside it (the cycle the design means: writer round 1, preflight 1 recorded not stopping, checker,
  writer round 2 and checker round 2 when asked, `void`, the final preflight, `measure`, `judge`).
- W2-187's and W2-188's tickets (`.tickets/DAEO-0cd2.md`, `.tickets/DAEO-zlog.md`).

**The CTO's decisions (do not reopen them):**
1. **Per-repository configuration.** The domain table, the subsystem table, the question categories with their quotas,
   and the control set with its baseline move out of the code into `governance/project/memory-audit.yaml` (a schema
   under `template/governance/kernel/schemas/`). Gov OS's own file holds today's constants unchanged, so Gov OS's
   measure and every existing test behave as before. No silent default: in a repository without the file, every step
   refuses by name and says which file to write. A subsystem may be declared by path or by a record key (EXAMIN's
   `feature`), as EXAMIN's proposal asks; shape the rest of its proposal as you judge, and say in your return what
   EXAMIN's file would be.
2. **Product commands.** The steps an adopter runs are on the CLI under `gov memaudit` (beside `scan`): at least the
   steps the driver runs and the driver itself, one command for a whole fresh 80 (both halves, on a pinned snapshot it
   builds: a clone at the commit and its own store; the live store untouched). `python3 -m gov.memaudit` keeps working.
3. **The writer and the checker.** Per the owner's E3 they are independent fresh sessions; the walls launcher
   (`indep_launch.py`) stays Gov OS's own tool and is not the product's. The product gives the adopter the writer's and
   the checker's briefs filled from the repository's configuration (`gov memaudit brief --kind writer|checker`), and the
   driver takes the delivered halves from the sets root. Gov OS's own approved briefs
   (`governance/project/indep-briefs/memory-audit/*.md`, pinned by sha) are not changed tonight: show in your return
   how the generated brief for Gov OS's configuration differs from the approved one (F-2's `by_area` list is expected).
4. **F-1 and F-2 are fixed here** (fixes in W2-187's record): the driver follows the cycle above; the writer's result
   counts areas in the configuration's own domain list.
5. **Comparability.** The reader's and the graders' prompts, schemas and models are not touched (DEC-1098; pinned by
   hash in `prompts.py`): a figure from this change compares with FRESH-80-RESULT. No model substitution reaches them.
6. **The hidden halves.** You and your helpers never read anything under `~/gov-os-eval` or any real question set.
   Every test uses planted sets in its own temp folders. No real writer, checker, reader or grader session is started;
   no measure is run; no rebuild of a shared store. The CTO runs the first real fresh 80 after you land.

**Your feature (a ticket first, wbs_id W2-204, status in_progress, KPI lines each observable with its verify).** At
least: Gov OS's constants reproduced from its configuration file with every existing memaudit test green unchanged; a
planted second repository with other domains, categories and a control set goes from two delivered halves to a judged
figure with fake reader and graders; a repository without the file is refused by name at every step; the driver's
cycle with a first preflight refused then repaired, and with the final preflight refused (stop, exit code as the
design says); the filled briefs; the CLI commands; the failure lines (a category quota that does not sum to the half's
size, a domain with no file, an unknown key in the file).

**Flow:** test designer (Fable) writes `tests/acceptance/W2-204/`, red on the base; engineer (Fable) builds until `gov
accept W2-204` is green; then `tests/unit/memaudit`, `tests/acceptance/W2-187`, `W2-188`, `W2-171` and every memaudit
acceptance folder (`grep -rl "gov.memaudit\|memaudit" tests/acceptance --include=*.py -l | cut -d/ -f3 | sort -u`),
with node on the PATH (`PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH`). `src/gov/cli/main.py` is also being
changed by the M1 lead tonight (it removes `gov context`): keep your change there to the `memaudit` subcommands.

**Return** as NIGHT-COMMON says, plus: the exact commands the EXAMIN CTO runs for its fresh 80 after `gov update`
(from the briefs to the judged figure), and EXAMIN's `memory-audit.yaml` as you would write it from its proposal.
