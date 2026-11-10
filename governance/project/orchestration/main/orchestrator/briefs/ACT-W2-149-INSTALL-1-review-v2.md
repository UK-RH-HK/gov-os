# ACT-W2-149-INSTALL-1, rebuilt — the independent review of an ACT package (one round; READY by verdict.py)

You are a fresh, read-only independent reviewer, and not the ACT's author. Review the **rebuilt ACT-W2-149-INSTALL-1**.
The launch script's approved list (`<sets root>/indep-walls/APPROVED`) gains the five set-up A briefs the owner approved
once (DEC-1113; SANDBOX-GUARD-EXP-DECLARATION §12) and the operator agent's two (DEC-1109 (1)). **Two of its six
template lines change** to the walls' template files as set-up A's wiring changed them (W2-149, merged `7f0e71519`):
`kinds.yaml` and `tree-exclude.txt`. The five briefs are committed byte for byte into the repository, where the launch
script reads them at `--commit`. The first build was reviewed READY (its records are beside the package). This build
replaces it, because the wiring changed the script and the template the first build pinned (its review's F4).

Everything you need is copied into your worktree, under `.gov-runtime/scratch/ref/ACT-W2-149-INSTALL-1/`:
- `ACT-W2-149-INSTALL-1.md`: the package. Read it in full. `@SHA8@` and `@REVIEW@` are filled after this review.
- `ACT-INDEP-WALLS-1.md` (the list as first written), `ACT-SETS-GLOBS-1.md`, `OPERATOR-AGENT-1.md` (§2 classes, §5 what
  stays the owner's) and `SANDBOX-GUARD-EXP-DECLARATION.md` (§12 the approved hashes; A5).
- The first build's reviews (`ACT-W2-149-INSTALL-1-review-r1.md`, `-r2.md`) and the wiring's review
  (`W2-149-sgx-review-r1.md`, its F18 to F30).
- `drafts/`: `apply.sh`, `freeze.py`, `install_check.py`, `rehearse.sh`, `rehearsal.log`, `APPROVED.before`,
  `APPROVED.after`, `briefs/` (the five).
- `sets-globs/`: ACT-SETS-GLOBS-1's drafts.

The launch script and the walls' template are in your worktree's tree, `w2/integrate` at `29907d750` with the wiring
merged (`governance/project/orchestration/tools/indep_launch.py`; `governance/project/indep-walls/`). Read the template
folder with the Read tool only, never naming it in a Bash line.

## Check (each a KPI line of your verdict block)
- **K1 the touched set is exact:**
  - `apply.sh apply` writes only these: the five brief files under `governance/project/indep-briefs/sgx1/` (compute
    their sha256s against §12), `<sets root>/indep-walls/APPROVED` (0400), and its own `backup/`;
  - it reads nothing else under the sets root;
  - the operator's commit holds exactly the five files.
- **K2 the list is right:**
  - `APPROVED.after` is ACT-INDEP-WALLS-1's list with exactly the two template lines changed, each to its file's sha256
    at `7f0e71519`. Then come the comments and seven `brief <kind> <path>` lines;
  - the launch script's own `parse_approved` reads 6 template lines and 7 brief lines, one hash per template file;
  - each brief line's kind is the brief's front-matter `kind` (or `operator`, which no launch accepts);
  - no line approves anything the owner did not approve. **The two template lines are an owner approval of the template
    change by this ACT's yes:** say whether the package states that plainly, and what each changed file now lets a wall
    do that it could not before.
- **K3 the undo is real:** `apply.sh undo` puts the list back byte for byte (`331e48fa…`) from a checked backup and
  removes only the five files. Say what state the tree and the launches are in after an undo.
- **K4 the rehearsal is real:**
  - the log is a run of this `apply.sh` in a clone with a planted HOME and sets root, and it ends `failures: 0`;
  - **set-up A's five briefs pass stage 10 and build their dry walls** (exit 0);
  - its counts are what the package states;
  - say where it differs from the live run.
- **K5 the order holds:**
  - `check` and `apply` refuse before ACT-SETS-GLOBS-1 is applied, and when the tree's launch script or either template
    file is not the wiring's (read `order_ok` and `drafts_ok`);
  - the package states the order;
  - nothing here breaks if W2-141's hook (rebuilt on ACT-SETS-GLOBS-1's) lands later.
- **K6 the class:** by OPERATOR-AGENT-1 §2 and §5, the class you find, whatever the package claims, with the reason.
- **K7 the package's account of what it does is true:**
  - set-up A launches through the merged script once the list is applied;
  - before the ACT, a launch is refused 11;
  - the wiring's F18 to F23 are stated as what would rebuild it;
  - the pin amendment follows.

  Read `build_and_run`'s stages 11 and 10 and the flows' staging.
- **K8 independence:**
  - with the briefs committed, does any wall's tree hold another brief? (`git archive` less `tree-exclude.txt` and the
    entry's `tree_exclude`.)
  - does the template change let one independent session see what its brief says it must not?
  - is the package's residual on it right?

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`. Mark it `scope: in` only if it concerns this ACT's change.

## Write and return
- **You write nothing in any tree.**
  - You may run `apply.sh`, `install_check.py` and the launch script only against copies you make in your own temporary
    folder, with a planted HOME and a planted sets root: never the real sets root, never the main tree.
  - You may run the tests read-only through
    `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
    `PYTHONPATH=<your worktree>/src` and an empty scratch HOME (`PYTHONUSERBASE=/home/usain/.local`).
  - No real `claude` session, no GPU, no network. Single simple Bash commands (DEC-1080).
  - The hidden-half rule holds: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/` or any `hidden` folder,
    and never name the sets root on a command line.
- **Search again once (DEC-1092 (1))** if a search does not answer.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md` (task, status, work_completed, files_changed, evidence, tests,
    discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), with the sandbox and `ps`
    checks first;
  - your answer to K1-K8;
  - every finding with its two lines and its scope (ids from F31);
  - at the end, one fenced block opened with three backticks and the word `verdict`:
    `{"act": "ACT-W2-149-INSTALL-1", "class": "a|b|O", "apply_sh_sha256": "<the sha256 of drafts/apply.sh you read>", "kpis": [{"kpi": "K1", "verdict": "pass|fail", "findings": [{"id": "F31", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ... "K8"]}`.

Refused twice for the same call: stop and say so; no third try.
