# Brief: independent test designer — DAEO-kl5e (W2-50), FULL

You are a fresh independent test designer (MR-3). Ticket: DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`. You write the ticket's acceptance tests from its KPI lines and its sources, before the implementation, and you show them red.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nothing under `~/.claude/` is read.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **The real scratch roots are never touched.** Neither your tests nor you create, write, list or remove anything in the real `~/gov-os-runs/` (it does not exist, and nobody creates it in this run), the real `~/gov-os-worktrees/` or the real `~/gov-os-workbench/`. Tests run the code under test with a temporary home folder (the `HOME` environment variable of the process under test) or another public means. If there is no public means to point the code under test at a temporary home, return a package; do not test against the real home. Before you return, run `test -e ~/gov-os-runs && echo PRESENT || echo ABSENT` and quote the output: it must print ABSENT.
- A hazard you must design round: the guard already allows writes in the temp folder (`tempfile.gettempdir()`, which follows `TMPDIR`). A temporary home that lies inside the temp folder the code under test sees would make every path under it allowed for that reason alone, so a refusal test would pass or fail for the wrong reason. Make the temporary home and the temp folder of the code under test disjoint (for example, give the process under test a `TMPDIR` that is a sibling of the temporary home), and say in the README how you did it.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in imports the package under test or copies single named files, never `governance/project/`; a test that needs a repository builds a temporary one from scratch or from the dev tiers. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree (a temporary repository you built is not either of them). Tests launch no real `claude` session and use no network.
- Refused twice for the same call: stop and say so; no third try (AR-6).
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-kl5e.md` (read-only): its KPI lines, its `allowed_paths` and its sources.
- The card of W2-50 in `docs/plan/WAVE_2_WBS.md` §2 (search for "#### W2-50"), and §0 (rules for every ticket).
- The list row it takes in: W2-M355 ("Live clones under /tmp lost on reboot"), in `docs/plan/WAVE_2_LIST.md` and `docs/plan/WAVE_2_TRIAGE.md`.
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-728 (the owner decision behind this ticket), DEC-723 (the workbench, writing work under `~/gov-os-runs/<W2 id>/`), DEC-159 (the per-session temp folder of a launched worker), DEC-160 and DEC-161 (the sandbox), CAP-33 in `docs/contract/contract.yaml` (change control), DEC-136, DEC-221, DEC-462, DEC-491, DEC-732.
- The public interfaces the ticket must work with, as earlier acceptance suites drive them: the guard's decision as the PreToolUse hook and the earlier guard suites call it (see `tests/acceptance/W1-03/` and `tests/acceptance/W1-05/` for how they drive it, with the role, the ticket and the project root); `gov launch` and the settings it gives the session it starts, including the sandbox's filesystem write list and the session's temp folder (see `tests/acceptance/W1-32/` and `tests/acceptance/W1-48/` for how they drive it without a real session); the role files under `governance/kernel/roles/` or `template/governance/kernel/roles/`; `gov rebuild` and the stores it builds; the secrets-indexing check (`template/governance/kernel/checks/secrets-indexing.yaml`, run as `python3 -m gov.secrets`). You read no private part of an implementation to learn what a test should expect.

## The behaviour to test (from the KPI lines and DEC-728)

Success:
1. **One durable root.** `~/gov-os-runs/` is the one durable scratch root outside the repository, known to the guard and to the launcher's sandbox [DEC-728, W2-M355].
2. **Its own folder only.** A session of any role writes only under `~/gov-os-runs/<its own ticket>/`. That folder is named by the ticket's W2 id (its `external-ref`, as for worktrees), or by its `tk` id when it has none, and resolved from the session's `GOV_TICKET`.
   - The guard allows Write, Edit and judged Bash targets there.
   - The launcher adds exactly that folder (not the root) to the sandbox write list.
   - The folder is created on first use.
3. **Survival.** A clone made there survives the session's end and a restart (W2-M355: clones under `/tmp` are lost on a reboot; the launcher removes its session's temp folder at the session's end).
4. **Never indexed.** Nothing under `~/gov-os-runs` is indexed by this repository's stores, and this repository's secrets-indexing check never scans it.
   - A product clone that is adopted there has its own store, inside the clone; that store is the clone's, not this repository's.
   - A planted secret in a clone there reaches no index of this repository.

Failure — each refused, with the guard's reason (the refusal's text says why):
5. another ticket's folder under `~/gov-os-runs`;
6. the root itself (a file directly in it, or removing it);
7. a path outside it reached by `..`, a symbolic link or a hard link;
8. a session with no ticket;
9. any path outside the repository other than the temp folder and the session's own folder;
10. `~/gov-os-workbench` and `~/gov-os-worktrees` (other than the session's own worktree) stay refused as before.

Also from DEC-728 item 2: the refusals hold for Write, Edit and judged Bash targets alike, and "a session of any role" means the rule is the same for each role that may write; where a role file makes a role read-only or gives it no paths, say in the README how you read "any role" against it.

Where a KPI line admits more than one reading (for example, which component creates the folder on first use, whether a session whose ticket is forged or unknown is treated as one with no ticket, or how a W2 id with a letter suffix is named), do not stop: choose the reading the sources best support, write the tests on it, state it in the README as your reading with its source, and list it in `proposed_decisions` with your recommendation and confidence. The lead puts these readings before the owner with the change proposal, before any implementation starts. A reading that no source supports at all is a package and gets no test.

## What you write

- Only inside `tests/acceptance/W2-50/`. No earlier ticket's test is revised unless a KPI line names it; if you find that an earlier ticket's acceptance test contradicts these KPI lines (for example one that requires every path outside the repository but the temp folder to be refused), name it, do not edit it, and return it as a package. No throwaway implementation is left in the tree.
- FULL: thorough — every KPI line's success and failure, the escapes the failure lines name (`..`, a symbolic link, a hard link) and the obvious variants a reviewer would try (a rename or move into or out of the folder, a case change of the ticket folder's name, the root reached through a trailing slash or `.`), with no combinatorial expansion beyond what a KPI demands (DEC-221).
- Behaviour through public interfaces, never internals. Deterministic, no network. Tests that need a repository build a temporary one (with a `.tickets/` folder holding the ticket files the test needs). Tests that run code in a child process pass `PYTHONPATH` on to it, so that a run from this worktree exercises this worktree's code (DEC-732); the README says how.
- A README at `tests/acceptance/W2-50/README.md` that maps each KPI line to its tests and gives the expected red reason of each, states how the temporary home and temp folder are set up, and states how the suite runs this worktree's code.
- Red first: run the tests to the end, never with `-x`:
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/acceptance/W2-50 -q -p no:cacheprovider -rs`
  They fail for the reason the README states. Tests that hold refusals that already hold today (for example the workbench staying refused) may pass now; say which, and why that is expected. If the suite needs this repository's store, say so and do not build one yourself in this worktree; return it.
- An ambiguous KPI line or a dispute that no source settles is returned as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your test paths, in one commit, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "W2-50 (DAEO-kl5e): acceptance tests for the durable scratch root" --trailer "Task: DAEO-kl5e" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | LEAD_CHECKPOINT | AUTH_REQUIRED, and one line of why>
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

In those fields give: your commit's hash and trailers; the `gov.__file__` line; the test count; each KPI line with its tests; the red reason as you saw it, per test or group; which tests pass now and why; every earlier test you found in conflict; the `~/gov-os-runs` ABSENT line; every reading you chose, with its source, recommendation and confidence. Refused twice for the same call: stop and say so.
