# Brief rev-1: independent auditor (STANDARD review, round 1) for DAEO-8a3f (W2-158), class C2

Budget: projection 4 USD.

You are the independent auditor for ticket DAEO-8a3f (W2-158): `gov check --structural`, one cheap, bounded pass over
the tree's declared check families and the new links on a head, a notice and never a refusal. Read-only: you write
nothing in the repository; your verdict is your return. Probe head `4916311219bd` of branch `w2/W2-158`
(`git -C /home/usain/gov-os-worktrees/W2-158 rev-parse HEAD` must show it; if not, stop and say so). This is round 1
of at most 2 (DEC-1010).

## Step 0, before any work (report it first in your return)

`printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-8a3f`). Do step 0 of
`/home/usain/gov-os-worktrees/W2-158/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id `DAEO-8a3f`:
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-8a3f','w').write('x')"` must FAIL. If it
wrote the file, stop and return.

## What to read
| what | path |
|---|---|
| ticket: KPI lines S1-S5 and F1-F4 with their Verify are the spec; then its sections "Interface", "Non-goals", "Rabbit holes" | /home/usain/gov-os-worktrees/W2-158/.tickets/DAEO-8a3f.md |
| the lead's readings L1-L10 of what the Interface leaves open (claims to check against the ticket, not to trust) | /home/usain/gov-os-worktrees/W2-158/.gov-runtime/scratch/lead/briefs/interface.md |
| the code | src/gov/check/structural.py (new), src/gov/check/command.py (the `--structural` option and dispatch) |
| the whole change | `git -C /home/usain/gov-os-worktrees/W2-158 diff c8e9c236c 4916311219bd -- src tests docs/changes` (the merges of w2/integrate bring only tickets, register and orchestration records; the listed folders are this ticket's work alone) |
| the evidence (S5's measured time) | docs/changes/W2-158-evidence.md |
| tests | tests/acceptance/W2-158/ (the independent test designer's), tests/unit/check/test_w2_158_structural.py (the engineer's) |
| how declarations are read today, and `gov links` (what the links line calls) | src/gov/cli/checks.py; src/gov/links/command.py, src/gov/links/check.py; the command-module convention in src/gov/cli/main.py's docstring (CHILD_EXIT_CODE) |
| the CTO's reference tool (context only; F3 forbids its built-in commands) | /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/structural_pass.py |
| sources (grep docs/DECISION_REGISTER.md only by id, e.g. `### DEC-1052`) | DEC-1052, DEC-1073, DEC-1119, DEC-1109; tickets DAEO-q7lk (W2-129, gov links), DAEO-neam (W2-45) in .tickets/ |

Search with Read, Grep and Glob; if a first search does not answer, search once more in different words, then answer
from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context`.

## What to probe (at least these; find more)
1. Each of S1-S5 and F1-F4: does the code do what the line says, including each Verify's planted cases? In particular:
   - S1/F3: only the tree's own declared `command` strings run (template/governance/kernel/checks first, else
     governance/kernel/checks); no built-in command list anywhere; a family with no declaration reads skipped and
     runs nothing; all started at once, one process each; at the bound the whole process group is killed (a
     grandchild too) and the pass never waits past the bound for one command.
   - S2/F2: the line forms exactly as stated; a timed-out family reads `NOTICE ... not measured`, never ok; the last
     line `structural pass at <head12> ...`. Look for any path where a timeout, a crash in reading a result, an
     unreadable YAML or a command that cannot start reads ok or makes the pass raise.
   - S3/F1: exit 0 whatever the checks find (including an exception inside one family's handling?); exit 2 only for
     no folder, not a work tree, no HEAD, bad arguments; plain `gov check` and `gov check --list` unchanged. Search
     src/gov/close, src/gov/launch, src/gov/queue for any call of it whose result decides a refusal.
   - S4: portability runs only on a change under template/governance/kernel/{roles,skills,hooks}/** or .rulesync/**,
     or an unresolvable base; links runs after the others, within the bound, its line forms as stated; without a base
     both are named as left out; without src/gov/links/ the links line is skipped with its reason.
   - S5: it writes nothing but the declared commands' outputs and links' mark (no __pycache__, no index rewrite from
     its own git reads: check `--no-optional-locks` or GIT_OPTIONAL_LOCKS); the evidence's measured time is within
     the bound plus 10 s. You may re-measure on a clone of the head under your TMPDIR (never on
     /home/usain/Dynamic-Agentic-Engineering-OS itself).
2. Scope (F4): `git diff --name-only c8e9c236c 4916311219bd -- src tests docs/changes template governance/kernel` lists only the ticket's
   `allowed_paths:` plus `tests/acceptance/W2-158/**`; the acceptance tests changed only in the test designer's
   commits (`git log --format='%h %(trailers:key=Role,valueonly)' c8e9c236c..4916311219bd -- tests/acceptance`).
3. The tests: would they catch a wrong implementation? Plant a few mutations of the fail-open paths (a timeout read
   as ok, a non-zero exit, a built-in command, portability run with no kernel change) on a mirror copy under your
   TMPDIR, never in the tree (point PYTHONPATH at the mirror's src).
4. Smell for this repository's own names baked into product code (`w2/`, `integrate`, `DAEO-`, CTO tool paths) in
   src/gov/check/structural.py.

Runs: planted folders only (pytest's tmp_path or your TMPDIR). **Every pytest run goes through the heavy-slot gate**,
with a TMPDIR outside the repository and outside `~/gov-os-runs`, `PYTHONUSERBASE=/home/usain/.local`, an empty
`HOME`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`:

    env HOME=/home/usain/gov-os-worktrees/W2-158/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local TMPDIR=/tmp PYTHONPATH=/home/usain/gov-os-worktrees/W2-158/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <folder or file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"

(if TMPDIR=/tmp is refused in your sandbox, use your sandbox's TMPDIR; the cases deselected by `-k` include S5's
real-repository timing case: run it alone once if you can). The base-red rule: a red that is not this ticket's and
also fails on w2/integrate's head is a shared base red, not blocking. The lead's verify of this head: RED only in six W2-96 signal cases (tests/unit/accept/test_w2_96_{run2,review3,review4}.py), parallel 4220 tests, 6 failed; every W2-158 case green; the lead is checking them on w2/integrate's head (base-red rule): do not judge them as this ticket's.

Refused twice for the same call: stop and say so; never reach the same effect by another command, form or file
(DEC-1142 (9)).

Judge against ADR-0001's threat model (DEC-801): a finding is blocking only if an honest agent or operator hits it in
ordinary work and it fails open (a NOTICE turned into a refusal or a non-zero exit, a timeout read as ok, a command
run that is not the tree's declaration, a write outside the declared outputs and links' mark) or loses work. For each
blocking finding, say the smallest fix and the planted input that shows it.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE or ESCALATION) / work_completed /
files_changed (none) / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then a fenced verdict block:
```
verdict: PASS | FAIL
head: <hash12>
findings: <n>
- <id> | <severity: blocking, major, minor> | <KPI line> | <file:line> | <what is wrong, the planted input and the wrong output>
```
Then the per-KPI block (a fenced block with the info string `verdict`, JSON:
`{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F-1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}`,
one entry for each of S1-S5 and F1-F4). Then `guard_refusals:` (none, or each: time | form | the hook's reason | true
or false-positive).
