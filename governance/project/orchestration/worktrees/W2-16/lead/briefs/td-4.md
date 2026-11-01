# Brief: independent test designer (W2-16 round 3, DEC-772 item 1)

You are a fresh independent test designer (MR-3). Ticket: `DAEO-49o5` (`W2-16`, "Immutable, hash-pinned releases (CAP-43.b lite)"), profile FULL. **You work and commit only in the tests worktree `/home/usain/gov-os-worktrees/W2-16-tests`, on branch `w2/W2-16-tests`** (DEC-963). An engineer builds the same behaviour at the same time in another worktree, from the same specification; neither of you reads the other's work. The ticket's acceptance suite exists (`tests/acceptance/W2-16/`, 114 cases) and an earlier implementation is in your tree. The owner's decision DEC-772 changes who may build a release. You write the cases that hold it, show them red against the code in your tree, and make three recorded rewrites.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-49o5','w').write('x')"` must fail. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` (in your worktree) must work. If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-49o5`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-16-tests` and `w2/W2-16-tests`) and `git log --oneline -1` (expect `2c8cfc7a`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. **For you, "this worktree" is the tests worktree: use `/home/usain/gov-os-worktrees/W2-16-tests/src` in place of `/home/usain/gov-os-worktrees/W2-16/src` in that rule**, so your red runs judge the code as it stood before this round, never the engineer's work in progress.
- **Reads (DEC-820, Policy 2).** You read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never the qualification oracle; **(c) this ticket's implementation: never read `src/gov/release/**`, `src/gov/lock/**`, `copier.yml`, `docs/releases/README.md`, `tests/unit/release/**` or `tests/unit/lock/**`, in your worktree, in `/home/usain/gov-os-worktrees/W2-16` or in git history** (you may run them through the suite and read results); (d) the hidden half of any evaluation set. You may read other suites' tests (for example W1-50's freeze-lift driver) and the rest of `src/gov/` (for example `src/gov/pause/command.py`, which is not this ticket's code).
- **Retrieval (DEC-963, DEC-836, DEC-860, DEC-859):** what you need to know you ask first of the integration branch's store, never this worktree's or the engineer's: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read; it holds `w2/integrate` as of its last refresh; for what changed since, `git show w2/integrate:<path>`). Never one giant query: a large question in batches (`--batch-size`, then `--continue <token>`). A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; if that tool is not available to you, search named folders with Grep. **P-R1:** drop unread any retrieval result under the paths in (c), and name in your return each such result you were served.
- **Read refusals (DEC-849):** the guard may still refuse a search that starts at the repository root, `governance/project/` or `.claude/`. Take the refusal, never look for another form; search named folders instead; count the refusals in your return.
- **Scratch budget (DEC-898):** your share is 6 GB and 300,000 files and folders, outside the tracked tree. Keep pytest's own temp retention (no `--basetemp`); clean what you make as soon as it is not needed; give `du -sh` and `du -s --inodes` of anything you leave in your return.
- **Commit hashes (row W2-L423's rule, DEC-911):** anything you write under `.gov-runtime/` holds commit hashes as 12 digits, never 40, and never the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- Run everything in the foreground, one command after another: your session ends with your last message. A single tool call is cut off at 10 minutes: run a long suite file by file. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase (inside your own temporary repositories you may do what a case needs).
- Never read `.claude/settings.json` or `.claude/settings.local.json`, anywhere, nor anything under `~/.claude/`.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Never copy the repository or a folder of it** (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of it). A case that needs a repository builds a temporary one from scratch, copying single named files, as the suite's support module does. Nothing under `.gov-runtime/` holds a clone or copy of a programme (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Write files with the Write and Edit tools and literal absolute paths. No subagents that write. **Install nothing** (the guard refuses it; a tool you need is a package). No push, merge, rebase or tag of this repository.
- **Nobody tags this repository and nobody signs.** Releases are built only in temporary repositories; a tag there is unsigned, standing for the owner.
- Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause`.
- If the guard or the sandbox refuses something you needed, return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6). Record each refusal by the guard (time, the command's form in one line, the reason it gave).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return status `AUTH_REQUIRED`.

## What you read

- The ticket file `.tickets/DAEO-49o5.md` (read-only): its KPI lines (success 2: "The owner tags the release commit (agents never tag)").
- DEC-772, DEC-761, DEC-767, DEC-409, DEC-365, DEC-491, DEC-866 in `docs/DECISION_REGISTER.md` (search the register by id).
- The suite as it stands: `tests/acceptance/W2-16/README.md`, `w2_16_support.py`, `conftest.py`, and `test_w2_16_last_round.py` (the role cases and the case below).
- How W1-50 drives the freeze lift's seam with planted ancestry, a pseudo-terminal and the code typed back: `tests/acceptance/W1-50/w1_50_freeze_lift.py`, `test_w1_50_freeze_lift_ancestry.py`, `test_w1_50_freeze_lift_terminal.py`, `w1_50_freeze_README.md` ("The fifth batch"). Reuse its approach; do not import W1-50's modules into W2-16 (copy what you need into this suite's own support).

## The behaviour this round builds (DEC-772 item 1), as the lead specifies it for both workers

The owner's decision (DEC-772, 2026-10-18), item 1, word for word: "`gov release` is owner-only, from a plain terminal, like `gov approve` and the freeze lift: it refuses with a Claude Code process among its ancestors, with `GOV_ROLE` or `GOV_TICKET` set, or without a terminal, and asks for a typed one-time code. This replaces DEC-761 item 1's line '`gov release` refuses unless the role is orchestrator, or the owner in a plain terminal'. It is W2-16's next round, and that round does only this (tests first, one review of that change); W2-16's allowed paths do not change."

The lead's reading (fixed for this round; a worker who judges it wrong returns a package, never guesses):

1. **Which form.** Item 1 governs the build form: `gov release <version>`, and every `gov release` call that is not `--lock-from`. `gov release --lock-from <template>` (the template's Copier task, run inside `copier copy` and `copier update`) keeps its caller check exactly as it stands (refused for a `GOV_ROLE` set to anything but `orchestrator`; runs with it unset or `orchestrator`). Reason: a terminal-and-code check on the Copier task would refuse every install and update that is not typed by hand, against KPI 4 ("at copy as well as at update") and against W1-39's closed suite, which DEC-771 item 1 says W2-16 does not reopen.
2. **The build form refuses, before it reads or writes anything** (no file, no ref, no tag, no index change; non-zero exit; no traceback; the error code `RELEASE_REFUSED`; its details carry `reason`, one of the words below; its message says the reason in words), in each of these cases:
   - `session`: a Claude Code session is among its ancestor processes. The signs and the reading are the freeze lift's (DEC-409, `gov pause --off`): the same chain from `/proc`, the same signs of a session;
   - `ancestry`: the chain of ancestor processes cannot be read whole up to the system's first process (process 1, `init` or `systemd`);
   - `role`: `GOV_ROLE` is set in its environment, to any value (`orchestrator`, `owner` and the empty value included);
   - `ticket`: `GOV_TICKET` is set, to any value (the empty value included);
   - `terminal`: its standard input and its standard output are not both a terminal;
   - `code`: the code typed back is not the code shown. Only after every check above has passed, the command writes to the terminal a prompt holding a one-time code, the word `RELEASE-` followed by four decimal digits from the system's random source, and reads one line; the line, stripped of surrounding white space, must equal the code. A wrong line, an empty line or end of input refuses. Nothing is shown on a call refused earlier.
   - Where several hold, which reason is given is not fixed; every refusal writes nothing.
   - On success the build is what it is today: the record under `docs/releases/<version>/`, no commit, no tag; the result `{"version": <version>, "record": <the record's folder>}`.
3. **The test seam, in the freeze lift's form** (W1-50 drives `gov.pause.command._lift_test` the same way): the module `gov.release.command` has a function `_release_test(root, version, ancestry=None, terminal=None)`. `root` is the repository to release from (as the command's root); `version` the version string; `ancestry` a planted chain in the form `gov.pause.command.read_ancestry()` returns (a list of maps `pid`, `ppid`, `comm`, `exe`, `cmdline`; this process first, the system's first process last); `terminal` a pair `(input descriptor, output descriptor)`, each asked `os.isatty` whatever is passed. `GOV_ROLE` and `GOV_TICKET` are read from the process environment, never planted. It returns the command's result on success and raises `gov.cli.errors.GovError` with code `RELEASE_REFUSED` and details `reason` on refusal. The command itself always reads the real chain from `/proc` and uses descriptors `(0, 1)`; no option, argument or environment variable plants either.
4. **Nothing else changes:** what a release record holds, immutability, `verify`, `--lock-from`'s rules, doctor, Copier. The command lists (`src/gov/check/commands.py`, W1-07's list) are not touched in this round: W2-20's change is not in this tree (DEC-753 items 2 and 3).

## What you write

All inside `tests/acceptance/W2-16/` only, in one commit:

1. **New cases for item 2 and 3 of the specification** (a new file, for example `test_w2_16_owner_terminal.py`), one case per bullet, parameterised where natural, no combinatorial expansion:
   - through the seam, driven in a child process with a pseudo-terminal, the code read from it and typed back, `GOV_ROLE` and `GOV_TICKET` absent from the child's environment, and a planted chain that reaches process 1 with no Claude Code session in it: the build succeeds and writes the record (positive control);
   - the same, refused with its `reason`, nothing written (the suite's whole snapshot), no traceback: a planted chain holding a Claude Code session (a few of the freeze lift's signs, W1-50's chains); a chain that does not reach process 1; `GOV_ROLE` set (`orchestrator`, `owner`, `engineer`, the empty value); `GOV_TICKET` set (`DAEO-49o5`, the empty value); no terminal (a pipe, or `/dev/null`); a wrong code and an empty line typed back; end of input;
   - the real command, `gov release <version>` as the suite already runs it (a child process, `GOV_ROLE` and `GOV_TICKET` absent, once with standard input from `/dev/null` and once under a pseudo-terminal with the code typed back): refused, nothing written, no traceback. Do not assert which reason: a run from an agent's session has a Claude Code ancestor, the nightly's may not, and both must refuse (the pseudo-terminal run refuses for its ancestry or, where there is none, the case says so and ends as skipped with that reason, never as passed);
   - `gov release --lock-from` is unchanged: no new case (the existing role cases hold it).
2. **Three recorded rewrites (DEC-491, DEC-866), each keeping its purpose and lowering no other expectation:**
   - **The suite's release builds (DEC-772).** `w2_16_support.build_release` runs `gov release <version>` as a child process; under DEC-772 that call refuses from any test run, so every case that builds a release would fail for a reason that is not its own. Rewrite the helper so it builds through the seam as the owner (planted clean chain, pseudo-terminal, code typed back, `GOV_ROLE` and `GOV_TICKET` absent), keeping every assertion the helper makes today (a release from a clean `w2/integrate` commit, nothing changed outside `docs/releases/`, a record written, the owner's commit and tag). `Rewrite-Reason: DEC-772`.
   - **The two role cases' build halves (DEC-772 replaces DEC-761 item 1's line).** In `test_w2_16_last_round.py`, `test_gov_release_refuses_every_role_but_the_orchestrator_and_the_owner` and `test_gov_release_runs_for_the_orchestrator_and_the_owner`: for the form `gov release <version>`, every `GOV_ROLE` value now refuses, `orchestrator` included, and `GOV_ROLE` unset refuses without a terminal; move those expectations so the build form is held refused for every value (the old positive build controls become refusals; the seam's positive control above replaces them). The `--lock-from` form's cases stay exactly as they are. `Rewrite-Reason: DEC-772`.
   - **R3-F5 (DEC-767, P-R3-2 (a)).** `test_a_source_whose_release_records_were_removed_is_refused[copier copy]` copies into `tmp_path / "product"`, which the `own_release_project` fixture has already filled, so Copier stops before its task runs and the case fails whatever the code does. Change that one line so the copy goes into a fresh folder (a new name under `tmp_path`), nothing else. `Rewrite-Reason: DEC-767`.
3. **The README:** each new case with its KPI line (success 2), its source (DEC-772 item 1) and its expected red reason; a section for the three rewrites with their reasons; a line that the seam's name and form are the lead's specification for this round, in the freeze lift's form; and a line that W1-07's list entry for `release` is not made in this round (W2-20's change is not in the tree, DEC-753 item 3).

Change nothing outside `tests/acceptance/W2-16/`. If you judge a KPI requires revising another ticket's test, name it; do not change it.

## Red first

From your worktree, each to its end, never with `-x`:

    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-16-tests/src python3 -m pytest tests/acceptance/W2-16/<your new file> -q -p no:cacheprovider -rs
    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-16-tests/src python3 -m pytest tests/acceptance/W2-16 -q -p no:cacheprovider -rs -o tmp_path_retention_policy=failed

(file by file if the whole suite passes 10 minutes). Against the code in your tree the seam does not exist yet, so the seam cases and the rewritten helper's cases fail for that reason: say so, with counts, in your README and return. The R3-F5 case should pass once it copies into a fresh folder (the earlier code already refuses there): say how it ends. Report which cases pass today and why.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit: stop and say so. Never `--no-verify`, never `core.hooksPath`. One commit, your test paths only, trailers in the final block:

    git commit -m "W2-16 (DAEO-49o5): round 3 acceptance cases (DEC-772 item 1): gov release from a plain terminal with a typed code; the builds through the seam; the role cases' build halves; R3-F5 into a fresh folder" --trailer "Task: DAEO-49o5" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-772, DEC-767, CAP-43.b" --trailer "Rewrite-Reason: DEC-772" --trailer "Rewrite-Reason: DEC-767" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`.

## Return

Your last message, complete in itself: the sandbox check's result; your commit's 12-digit hash; the new cases with their red reason as you saw it; the three rewrites and how each ends today; each run's counts; the `gov.__file__` line; whether you used `gov retrieve` and for what; any retrieval result you dropped under P-R1; the guard's refusals and read refusals you met; any package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.
