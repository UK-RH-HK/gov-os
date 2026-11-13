You are a fresh Independent Test Designer (MR-3). Ticket: DAEO-g29a (W2-113, "An adopted product's CTO is named at adoption"), profile STANDARD, run 2 of the ticket (run 1 stopped at the interface check; the owner decided the interface, DEC-1156 (4)). You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-113-tests` (branch `w2/W2-113-tests`, made from the ticket branch's head 4d2773584a8f, DEC-963); you never write the ticket's own worktree `/home/usain/gov-os-worktrees/W2-113`.

Your budget: about 75 minutes. One new suite, `tests/acceptance/W2-113/`.

## Step 0, before any work: the sandbox check (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-g29a','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return.

Then check identity: `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-g29a`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-113-tests`, `w2/W2-113-tests`). If anything differs, stop and say so.

## What you read
- The ticket file `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g29a.md`: its KPI lines **success-1, success-2, failure-1, failure-2** and its `## Interface` section I1-I3 (binding; cite I1-I3 in your README). The `moved:` line (role files, now W2-33's) and the `lifted:` line (the quiet-hours hook, DEC-1083) are NOT tested.
- The decisions, by id in `docs/DECISION_REGISTER.md` (grep by id only): DEC-971 (item 4), DEC-957, DEC-982, DEC-974, DEC-1083, DEC-1156 (its item (4)), DEC-1052, DEC-1155, DEC-820.
- The surroundings you test against (not the counterpart's work, which does not exist at your head):
  - `src/gov/guard/install.py` — read only the public names `coordination_ticket(project_root)`, `cto_install(project_root, session_role, subagent_type, ticket_id)`, `ROSTER`, `COORDINATION_KEY`; the guard's install decision is made by the kernel hook `template/governance/kernel/hooks/pretooluse.py` (rule 4). Judge through the hook as the W2-110 suite does, not by calling `cto_install` alone.
  - **W2-110's suite** `tests/acceptance/W2-110/` (README, `w2_110_support.py`, `conftest.py`): how a product is generated (copier, then `rulesync generate`, via W2-90's `w2_90_kernel_wiring`), how a session's install is put through the hook (`call(...)`, `Session`, `cto(...)`), and its predicates `tells_to_escalate`, `says_how_to_set_the_key`. Reuse it by import where you can; do not copy large parts.
  - How `gov adopt --lite --stage A0` is run on a planted repository: `tests/acceptance/W1-41/w1_41_support.py` and `tests/acceptance/W2-23/w2_23_support.py` (config, clean tree, the A0 record and commit), and `src/gov/adopt/project.py` / `src/gov/adopt/safety.py` for where A0's record and commit live (read for names and paths only).
  - `src/gov/tasks/tickets.py` `create(root, title)` (the vendored `tk` at `governance/kernel/bin/tk`, tickets in `.tickets/`).
- **Search with the Read and Grep tools only** (no `gov retrieve`, no `gov context` inside the sandbox, DEC-1065); search again once in different words if the first does not answer. Search named folders, never the repository root.

## Policy 2 (DEC-820): reads open, four refusals
You read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (file names may be seen); (c) **the counterpart's work on this ticket: you never read this ticket's implementation**: the engineer's changes to `src/gov/adopt/stages.py`, `src/gov/guard/install.py`, `template/governance/kernel/hooks/permission_request.py`, `tests/unit/adopt/test_w2_113*`, on any branch other than your own head (do not look at `w2/W2-113` past 4d2773584a8f or any other branch); you may run tests against them and see results; (d) the hidden half of any evaluation set. Never open the evaluation sets' root or any hidden or memory-verdict folder.

## What to write: `tests/acceptance/W2-113/` (one README with the KPI map, test modules, a support module)
Every KPI line (success-1, success-2, failure-1, failure-2) maps to at least one case. The cases find the repository from their own location (its `src/` and `template/`), so merged into the ticket's worktree they judge that worktree's code.

- **"A planted repository adopted" (I3):** a git repository in `tmp_path` with the template copied in (copier, then `rulesync generate`, as in W2-110's suite), committed clean, then `gov adopt --lite --stage A0` run as a subprocess with that worktree's `src` on `PYTHONPATH` and the repository as its root. No hand edit of the roster or any ticket between adoption and the guard calls. Generate the product once per session (it is slow) and copy it per case.
- **success-1 / failure-1 (I1):** after A0: `governance/project/roster.yaml` holds a top-level `coordination_ticket` whose value is the id of a ticket file that A0 created in `.tickets/` (absent before A0), whose title is `<project> coordination` (`<project>` as the product is named; state in the README how you read the name and how strictly you judge the title) and whose frontmatter carries `class: coordination`; A0's record names both the ticket and the roster; both files are in A0's commit (the commit A0 made, with its set-up files) and the tree is clean after. Then, through the hook: an orchestrator session whose `GOV_TICKET` is that new ticket's id asks the owner for an install (ask, not refuse, not allow) — failure-1's case is exactly this with no edit; a refusal there is the failure.
- **failure-2 (I3):** in the same adopted repository, an engineer, an independent-test-designer, an independent-auditor, and an orchestrator on another ticket (a second ticket that exists in `.tickets/`) each attempt an install: each refused; none asked or let through.
- **I2, the three defaults (part of success-1):** (i) a roster that already names an existing ticket: A0 keeps the key's value and creates no ticket (the `.tickets/` file set unchanged); (ii) a roster with other content but no key: A0 adds the key and changes nothing else in the roster (compare parsed content less the key, and say whether you also check comments/ordering); (iii) `tk` missing (remove `governance/kernel/bin/tk` from the planted repo before A0): A0 refuses (non-zero exit) and writes nothing — no new ticket, no roster change, no new commit, no A0 record. Do not fix the refusal's wording beyond what I2 states.
- **success-2 (F5):** planted products (W2-110's generator is enough; adoption not needed) with (a) no roster key, (b) no roster file, (c) a key naming no ticket in `.tickets/`: the orchestrator's install and another role's install are both refused; the refusal text names `GOV_TICKET` and says how to set the key (W2-110's `says_how_to_set_the_key` or your own stated predicate); and the text does not claim a key was set when none was (e.g. no "set at adoption" phrased as a fact, no "the key names ..." in case (a)/(b)); state your exact predicate for "claims a key was set" in the README and keep it narrow enough that a true text passes.
- **No break of W2-110 (brief's ask):** do not re-test W2-110's KPIs; but note in `discoveries` any W2-110 case (file:line) whose assertion would conflict with success-2's new words (e.g. one that pins the old text exactly).
- **Path case (DEC-1155):** if you write a case "the branch changes only the ticket's allowed_paths", it judges only branch `w2/W2-113` (skip elsewhere, naming the branch found), and compares paths with `Path.is_relative_to`, never a text search of a temporary path.
- **README:** how to run; kinds; reading rules; the KPI map table in `gov accept`'s form (one row per KPI line, `success-N`/`failure-N`, the cases as code spans, and the red reason on the base 4d2773584a8f). For form, read `tests/acceptance/W2-110/README.md` and another recent suite's README with a KPI map (e.g. `tests/acceptance/W2-52/README.md`). Every case is red on the base for a stated reason (A0 creates no ticket and writes no roster today; the refusal does not name `GOV_TICKET`); a case green on the base is a mistake unless the README names it and why (e.g. failure-2's refusals may already hold on the base — say so; such a case is still required).

## How to run (every pytest through the heavy slot)
- `mkdir -p /tmp/gov-os-lead-W2-113` first; then `env TMPDIR=/tmp/gov-os-lead-W2-113 PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-113-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-113 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --tb=line`. Never `-x`. Report counts and time; show that each red is red for the stated reason (not a collection, import or fixture error — a fixture that cannot generate the product or run A0 is your bug, fix it).
- A resource gate's refusal from `heavy_slot.sh` is a wait (DEC-1146): wait and run again; it does not count as a refusal.
- **Show each check bites:** for success-1's roster/ticket checks and success-2's predicate, show once that the case passes against a minimal stand-in that behaves as I1/I2 and success-2 state (e.g. a script in your scratch that, after the real A0, does what I1 says by hand; a refusal string written as success-2 asks), and fails against one that does not. Stand-ins live in `tmp_path` or your scratch, never in the ticket's paths. Say how in your return.
- Check that `gov accept` reads your README's map: `cd /home/usain/gov-os-worktrees/W2-113-tests && env TMPDIR=/tmp/gov-os-lead-W2-113 PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-113-tests/src python3 -m gov.cli.main accept W2-113 --json` (one run; it reports per KPI line). If it refuses the map, fix the map's form (no test change), or return a package.

## Machine and budget (DEC-898)
3 GB and 150,000 files outside the tracked tree. Clean up every temp tree you make. Measure your scratch before you return (`du -s --inodes`, `du -sh`) and give the figures in `evidence`. No clone or copy of the repository itself (no `cp -r` of the repo, `rsync`, `git archive`, `git worktree`, `git clone` of it); generating a product from the template into `tmp_path`, as W2-110 does, is fine. Under `.gov-runtime/`, write commit hashes as 12 digits, never 40.

## Commands the guard can read (DEC-941 item 4a)
No shell variable as a write target; no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; anything longer goes in a script file under `/home/usain/gov-os-worktrees/W2-113-tests/.gov-runtime/scratch/td/` written with the Write tool, then run. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try** (DEC-1142 (9)). On an authentication error (401, 403), stop and return `AUTH_REQUIRED`.

## Commits
- Write only under `tests/acceptance/W2-113/`.
- Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. No amend, rebase, reset or push.
- `git commit -m "<subject>" --trailer "Task: DAEO-g29a" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-971, DEC-957, DEC-982, DEC-974, DEC-1083" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-113`
- `Implements:` holds only ids from the ticket's `sources:` (DEC-971, DEC-957, DEC-982, DEC-974, DEC-1083, DEC-991, DEC-994). An id you rely on that is not there (DEC-1156, DEC-1052, DEC-1155) goes in `discoveries`, never in `Implements:`.

## Never
Never run `gov close`, `gov pause`, or `gov adopt` against any real repository or worktree (running it as a subprocess on a planted repository in `tmp_path` is the test, and is fine); never `docs/plan/tools/validate_s1.py`; never ask or notify the owner; install nothing; no sudo; never write `.gov-runtime/**` outside `.gov-runtime/scratch/**`; never write a ticket file, the register or a plan file. If a KPI cannot be tested as written without guessing an interface I1-I3 does not state, do not invent it: test what is stated and return a package (question, options with cost, recommendation, confidence).

## Return
One message, your last. The twelve fields first, each a labelled line; then the payload (the case list per KPI line, the bite checks, the run's counts, the `gov accept` result, the sandbox check, read refusals met, scratch figures).

```
task: / status: (DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, with one line why) / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
The twelve fields first, any payload after. Refused twice for the same call: stop and say so.

## Context packet (gov context DAEO-g29a --role independent-test-designer --budget 9000; the default 6000 ceiling refused it, CONTEXT_OVER_CEILING, 8440 tokens)
Read `/home/usain/gov-os-worktrees/W2-113-tests/.gov-runtime/scratch/brief/td-1.ctx.md` (the ticket's text and its seven source decisions, JSON).
