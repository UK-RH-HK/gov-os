# Brief: independent test designer (the last round, DEC-761)

You are a fresh independent test designer (MR-3). Ticket: `DAEO-49o5` (`W2-16`, "Immutable, hash-pinned releases (CAP-43.b lite)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-16` on branch `w2/W2-16`. The ticket's acceptance tests exist (`tests/acceptance/W2-16/`, 85 cases) and an implementation is committed. A second review found behaviour the tests miss, and the owner ordered one more round, tests first (DEC-761, below). You add the cases that hold it, from the KPI lines and the behaviour described below, show them red, and make two recorded rewrites of earlier tickets' cases.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-49o5`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-16` and `w2/W2-16`), and `git log --oneline -1` (expect `ee557d02`). If anything differs, stop and say so.
- **The code under test (DEC-732):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. A single tool call is cut off at 10 minutes: run a long suite file by file.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase in this worktree (inside your own temporary repositories you may do what a case needs).
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Never copy the repository or a folder of it** (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A test that needs a repository builds a temporary one from scratch, copying single named files, as the suite's support module already does. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing. No push, merge, rebase or tag of this repository. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- **Nobody tags this repository and nobody signs.** A case that needs a tag makes it in its own temporary repository, unsigned, standing for the owner. Releases are built only in temporary repositories.
- Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return status `AUTH_REQUIRED`.

## What you read

- The ticket file `.tickets/DAEO-49o5.md` (read-only): its KPI lines and sources (CAP-43.b, CAP-43, DEC-722, CAP-02.c).
- The suite as it stands: `tests/acceptance/W2-16/README.md`, its support module and its cases. You extend it; you change no existing W2-16 case's expectation (if you judge one must change, return it as a package).
- CAP-43 and CAP-02 with their covers in `docs/contract/contract.yaml`; DEC-136, DEC-221, DEC-365, DEC-462, DEC-491, DEC-499, DEC-542 in `docs/DECISION_REGISTER.md`.
- Public interfaces only: `gov release <version>`, `gov release --lock-from <template source>` (the template's Copier task, in `copier.yml`), `gov doctor --json`, `copier copy` / `copier update` as the suite already runs them, their exit codes and output, the files of a release record and of a created project, `git` in temporary repositories. You read no private part of the implementation to learn what a case should expect.

## The owner's decision (DEC-761, 2026-10-17; staged, not yet in this worktree's register; apply it as written here)

"One more round, tests first: `gov release --lock-from` refuses once the project's lock records a release, and when the source holds no release record (R2-F1); a lock whose release block was deleted fails (R2-F2); a version tag from a source with no release records is refused (R2-F3); `gov release` refuses unless the role is orchestrator, or the owner in a plain terminal (no governed session): engineers and auditors never cut or rewrite a release; W1-39's no-files case and W1-32's command list are revised by the test designer, each as a recorded rewrite with its reason (`Rewrite-Reason:`, DEC-491), keeping its purpose."

## The behaviour to add (as described behaviour, DEC-136), with the lead's reading

The lead reads the decision against the ticket's own KPI and the closed suites, as follows. Write the cases to this reading; where you judge it wrong, return a package rather than guess.

**A. `--lock-from` in an installed project (R2-F1). KPI success 4 and the failure line.** Seen today: in a project installed from release `1.4.0` (lock records the release; doctor MATCH), a kernel file edited (doctor DRIFT naming it), then `gov release --lock-from <a folder holding no release record>` run by hand at the project root rewrites the lock from the edited kernel, with no release, exit 0; doctor then gives MATCH. What must hold:
1. **Once the project's lock records a release, `--lock-from` never rewrites it into a lock without a release, and never makes an edited kernel pass.** Run by hand at such a project's root, with the kernel edited (doctor failing first), each of these is refused (non-zero exit, no traceback, the lock byte for byte as it was) and doctor still fails naming the file afterwards:
   - a source folder holding no release record (a plain folder of `copier.yml` and `template/`, and the same as a git repository with a version tag and no record ever);
   - the genuine stand-in source of the same release the lock records (`v1.4.0` checked out): rewriting the lock of the installed release from the edited kernel is refused, or, if the command writes, doctor still fails naming the edited file (never MATCH).
   The positive control the suite already holds stays green: `copier update` from `1.4.0` to `1.5.0` writes the lock of `1.5.0` (KPI success 4, "at update"). So the lead reads "refuses once the lock records a release" as: it refuses to rewrite or drop the release the lock records; it writes the lock of another release only where that release verifies against its hashes and is the one the answers file names (an update).
2. **A source whose release records were removed** (the stand-in Gov OS repository: its `w2/integrate` holds release records in its history; a later commit removes `docs/releases/` and edits a kernel file; tagged `v1.6.0` by the case, standing for the owner) **is refused**: by `copier copy --vcs-ref v1.6.0` (non-zero, no lock written that passes doctor), by `copier update` from `1.4.0` to `v1.6.0` (non-zero; the lock does not change to a lock without a release), and by `gov release --lock-from` run by hand with that source. Seen today: it installs unverified and doctor passes (R2-F3 (b)).

**B. A lock whose release block was deleted (R2-F2). KPI success 4 ("a project cannot silence the lock comparison"), the failure line.** In a project installed from a release, delete from `governance/framework.lock` every entry that records the release (the entries whose value is or holds the release version, its manifest hash, or the release manifest the lock holds; find them by value, no key name is fixed), changing nothing else: doctor's `framework_lock` part fails (status `fail`, doctor exits non-zero). Seen today: MATCH (the first review's F2). Also the same deletion together with one kernel file edit and that file's hash in the lock's file manifest edited to match: doctor fails. Edits beyond these, that rewrite every record a project holds consistently, are the unsigned limit (CAP-02.c, Wave 3): no case.

**C. A version tag from a source with no release records (R2-F3).** The lead's reading, pending a package to the owner: the refusal is built in this round for a source **whose history holds release records** (A.2 above). A source that **never** held a record (W1-39's template source, `copier.yml` and `template/` alone, tagged `v0.1.0`) installs as W1-39 holds it: W1-39's suite (about 55 cases) and this suite's plain-source cases (W2-M174, W2-L227, W2-H029's and W2-M175's first forms) all install from such a source, and the owner named none of them for a rewrite. Do not write a case that refuses a never-recorded source, and change none of those cases; say in the README that this part waits for the owner's answer (the lead's package). Item 3 of DEC-761 leaves to the owner which commit is tagged (W2-L351, R2-P2): no case depends on it beyond what the suite already does (the tag is on the commit that holds the record).

**D. The role check. KPI success 2 ("agents never tag"), DEC-761, DEC-365.** `gov release` (both forms: building `<version>`, and `--lock-from`) runs only for the orchestrator or the owner. The caller is the environment variable `GOV_ROLE`, as `gov pause` reads it (DEC-365): unset is the owner in a plain terminal (no governed session, since every governed session is launched with `GOV_ROLE` set); `orchestrator` is the orchestrator. Every other value is refused: `engineer`, `independent-auditor`, `independent-test-designer`, `product-spec`, `research`, `ticket-lead`, an unknown name, and a set but empty value. A refusal exits non-zero, with no traceback, names the role or says only the orchestrator or the owner may release, and writes nothing (the whole snapshot the suite already takes: files, refs, HEAD, index; for `--lock-from`, the project's lock byte for byte). The positive controls: the same build with `GOV_ROLE=orchestrator`, and with `GOV_ROLE` unset (the suite's existing cases already run `gov` with `GOV_ROLE` unset: say so in the README, and keep it so; set `GOV_ROLE` only in the new role cases). The command does not read the process ancestry: the suites run Copier tasks with `GOV_ROLE` unset from agent sessions, and DEC-761 names no rewrite for them. A command that sets `GOV_ROLE=orchestrator` in its own environment from a session whose role is another is a known limit the owner ordered probed, not built around (the guard side is W2-H058's): no case. One case per refused value, parameterised; one positive case each for orchestrator and unset; both forms. No combinatorial expansion beyond that.

**E. The two recorded rewrites (DEC-491), each keeping its purpose.**
1. `tests/acceptance/W1-39/test_w1_39_drift.py::test_a_project_with_neither_lock_nor_answers_file_stays_unmeasured`: today it deletes both files from a project made by `copier copy` (an installed kernel) and holds "unmeasured, exit 0", which W2-H029 (this ticket's KPI 4) and W2-16's `test_deleting_both_the_lock_and_the_answers_file_does_not_silence_the_comparison` say must fail. Its purpose (DEC-499): a project **never installed** from the template has its lock part unmeasured and is no failure, and nothing is a match without hashing (DEC-488). Rewrite it to a never-installed project (no installed kernel, no lock, no answers file; W1-27's shape), keeping both assertions. Its docstring states the rewrite and its reason.
2. `tests/acceptance/W1-32/test_w1_32_command_set.py::test_the_command_set_is_the_twelve_and_the_three_recorded_ones`: today it fails because `gov --help` offers `release`, which the recorded command lists do not hold yet (DEC-753: `release` is recorded in W1-07's list and in `RECORDED_GOV_COMMANDS` only after W2-20 closes, not in this round; those lists are not touched). Its purpose: every command `gov` offers is recorded, every recorded command is offered, the module command is none of `gov`'s. Rewrite it so that `release`, and only `release`, is excused while the recorded lists lack it (naming DEC-753), and so it still passes, unchanged, once the lists record `release`; any other unrecorded command still fails it. Its docstring states the rewrite and its reason.
Change nothing else in W1-39's or W1-32's folders.

## What you write

- New W2-16 cases only inside `tests/acceptance/W2-16/` (a new file is best, for example one for this round), and the README's mapping: each new case, its KPI line, its source ("second review of W2-16, R2-F1/F2/F3", "DEC-761"), its expected red reason; plus a section for the two rewrites and for item C's open part.
- The two rewrites above, in place.
- No combinatorial expansion: one case per bullet, parameterised where natural. Reuse the suite's fixtures (releases built once per session; a case that changes a project works on a copy).
- Red first: run the new file, then the whole W2-16 suite to its end, never with `-x`, then the two rewritten cases:
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -m pytest tests/acceptance/W2-16 -q -p no:cacheprovider -rs`
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -m pytest "tests/acceptance/W1-39/test_w1_39_drift.py::test_a_project_with_neither_lock_nor_answers_file_stays_unmeasured" "tests/acceptance/W1-32/test_w1_32_command_set.py::test_the_command_set_is_the_twelve_and_the_three_recorded_ones" -q -p no:cacheprovider -rs`
  The new cases fail for the reason your README states (a positive control that passes today is fine, and named as such); the 85 earlier W2-16 cases still pass; say how the two rewritten cases end today. Then run W1-39's whole suite and W1-32's whole suite once each, to their end, and report their counts.
- An ambiguous point is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit: stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your test paths, in one commit, with the trailers in the final block (DEC-182, DEC-476, DEC-491):

    git commit -m "W2-16 (DAEO-49o5): last-round acceptance cases (DEC-761): --lock-from, release block, removed records, the role check; W1-39 and W1-32 rewrites" --trailer "Task: DAEO-49o5" --trailer "Role: independent-test-designer" --trailer "Implements: CAP-43.b" --trailer "Rewrite-Reason: cases added after implementation from the second review (R2-F1, R2-F2, R2-F3) and the role check, by DEC-761; W1-39's neither-file case moved to a never-installed project (W2-H029 makes an installed kernel with neither file fail; DEC-499's purpose kept); W1-32's command-set case excuses release alone until the lists record it (DEC-753), its purpose kept" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`.

## Return

Your last message, complete in itself: your commit's hash; the new cases with their KPI line and red reason as you saw it; the rewritten cases and how they end; each suite's counts; the `gov.__file__` line; any package.

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

The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.
