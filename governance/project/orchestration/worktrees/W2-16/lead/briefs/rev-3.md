# Brief: reviewer of the last round (FULL ticket, read-only, DEC-761)

You are a fresh reviewer. Ticket `DAEO-49o5` (`W2-16`, "Immutable, hash-pinned releases (CAP-43.b lite)"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-16` on branch `w2/W2-16`, at the head `d9035982bbe7023d8c2c007deb023b8e353b39fc`. The owner ordered one last round (DEC-761) and one review **of that round's change only**. You probe that head for behaviour the tests miss in this round's change. You write nothing.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-49o5`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-16` and `w2/W2-16`), and `git rev-parse HEAD` (expect `d9035982bbe7023d8c2c007deb023b8e353b39fc`). If anything differs, stop and say so.
- **The code under test (DEC-732):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. A single tool call is cut off at 10 minutes.
- You write nothing in this worktree, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash` in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier probes use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Never copy the repository or a folder of it** (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A probe that needs a repository builds a temporary one in a temporary folder (under `/tmp`, from `mktemp -d`), copying single named files only, never `governance/project/`. The acceptance tests' support modules (`tests/acceptance/W2-16/w2_16_support.py`, its `conftest.py`, and W1-39's `w1_39_support.py`) show how to assemble a stand-in Gov OS repository and a template source from single files, build releases there, and run `gov` and Copier with an environment the probe builds; you may import those helpers from a probe script kept in your temporary folder. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Write no file of the repository and make no commit. No subagents. Install nothing, no network. No push, merge, rebase or tag of this repository (tags only inside your own temporary repositories, unsigned). Never run `gov release` in this worktree; only in your temporary folders.
- Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause`.
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return status `AUTH_REQUIRED`.

## What you read

- The ticket file `.tickets/DAEO-49o5.md`: its KPI lines and its `allowed_paths`.
- The owner's decision for this round (DEC-761, 2026-10-17; staged, not yet in this worktree's register), as written: "One more round, tests first: `gov release --lock-from` refuses once the project's lock records a release, and when the source holds no release record (R2-F1); a lock whose release block was deleted fails (R2-F2); a version tag from a source with no release records is refused (R2-F3); `gov release` refuses unless the role is orchestrator, or the owner in a plain terminal (no governed session): engineers and auditors never cut or rewrite a release; W1-39's no-files case and W1-32's command list are revised by the test designer, each as a recorded rewrite with its reason, keeping its purpose." And: "A known limit to probe, not to build around: the guard skips leading `NAME=value` assignments in a Bash command, so a session could run `GOV_ROLE=orchestrator gov release …`. The role check this round builds is the command's; the guard side is W2-H058's. The reviewer probes this form and reports it by name with its result."
- The lead's reading, stated in the new README section of `tests/acceptance/W2-16/README.md`: the refusal of a source with no release record is built for a source **whose history holds records** (they were removed); a source that **never** held one (W1-39's) still installs, pending the owner's answer to the lead's package; "refuses once the lock records a release" is read as "never rewrites or drops the release the lock records; writes another release's lock only where it verifies and the answers file names it (an update)"; the owner is `GOV_ROLE` unset (DEC-365, as `gov pause` reads it).
- The round's change: `git diff ee557d02..d9035982bbe7023d8c2c007deb023b8e353b39fc -- src copier.yml docs/releases tests` (the cases `adbeea77`, the repair `fe8612d9` and `861a634d`). Earlier rounds' work is not under review except where this round's change touches it.
- DEC-365, DEC-488, DEC-491, DEC-499, DEC-542, DEC-753, DEC-136, DEC-413 in `docs/DECISION_REGISTER.md`; CAP-43 and CAP-02 in `docs/contract/contract.yaml`.

## What you probe (this round's change only)

Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such. For each, say what you did and what happened.

1. **`gov release --lock-from` in every state of the lock and the source.** Lock states: no lock; a lock stating `release: null` (a plain install); a lock recording a release; a lock whose release entries were deleted; a lock whose release entries were replaced by `release: null`; a lock that is not a readable map. Source states: a plain folder with no release record; a git repository that never held one, with a version tag; a git repository whose records were removed in a later commit (tagged); the genuine source of the release the lock records; the genuine source of a later release, with and without the answers file naming it; a source whose records are present but whose kernel was edited after release. Is the lock ever rewritten without the release it recorded, or an edited kernel made to pass doctor? Is any refusal partial (a lock half-written, a file left changed)?
2. **The deleted or edited release block.** Deleted entries alone; deleted with a kernel file and its lock hash edited together; replaced by `release: null`; the version or the manifest hash edited; the held release manifest edited. Which does doctor fail, and which is the unsigned limit (CAP-02.c, Wave 3)?
3. **A version tag from a source with no release records.** Records removed (history holds them): refused by `copier copy`, `copier update` and `--lock-from`? A source that never held one: installs (the lead's package); say what this leaves open.
4. **The role check, both forms (`gov release <version>` and `--lock-from`).** Each role (`engineer`, `independent-auditor`, `independent-test-designer`, `product-spec`, `research`, `ticket-lead`, an unknown name, set and empty), no role (`GOV_ROLE` unset: the owner), `orchestrator`. A Copier task run with each role in its environment. **A role set in the command's own environment:** from your own session (`GOV_ROLE=independent-auditor`), run in a temporary folder `GOV_ROLE=orchestrator <gov> release …` and `env -u GOV_ROLE <gov> release …` (with `<gov>` = `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -m gov.cli.main`), and say what the guard and the command did. **Report this as its own named finding, "the role set in the command's own environment (DEC-761 item 4)", with its result, apart from the round's other findings**; the guard side is W2-H058's, outside this ticket. The owner in a plain terminal cannot be reproduced from a session: say how the command reads it.
   For your other probes you need `gov` to run as the orchestrator or the owner: run it from a probe script with an environment the script builds without `GOV_ROLE` (as the acceptance suite does), in your temporary folders only.
5. **The two rewritten cases keep their purpose:** `tests/acceptance/W1-39/test_w1_39_drift.py::test_a_project_with_neither_lock_nor_answers_file_stays_unmeasured` (a never-installed project unmeasured, no failure, no match without hashing; DEC-499, DEC-488) and `tests/acceptance/W1-32/test_w1_32_command_set.py::test_the_command_set_is_the_twelve_and_the_three_recorded_ones` (every offered command recorded, `release` alone excused until the lists record it, DEC-753). Would each still catch what it caught before?
6. **The disputed case.** The engineer reports that `tests/acceptance/W2-16/test_w2_16_last_round.py::test_a_source_whose_release_records_were_removed_is_refused[copier copy]` cannot pass because its `copier copy` destination is the folder its own fixture (`own_release_project`, `tmp_path / "product"`) already fills, so Copier stops at its overwrite prompt before the task runs. Check that claim, and whether the refusal holds when the same copy goes to a fresh folder. You change nothing.
7. Whether this round's change breaks an earlier behaviour: `copier update` from one release to the next; a plain W1-39 install and update; doctor on this repository itself (its `framework_lock` part must not turn red); a project whose lock was written before this round.

## Return

The head you probed, and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity (BLOCKER, HIGH, MEDIUM, LOW), and whether it loses work, lets a role write outside its scope, lets an implementer change acceptance tests, or makes the guard or a gate fail open. Say also what you probed and found sound. Then your judgement on this round's change: `pass` (no finding that loses work, writes outside scope, changes acceptance tests or fails open in ordinary work, beyond the limits the owner named: the role set in the command's own environment, and what the lead's package leaves open for a source that never held a record) or `fail`. You repair nothing (MR-4). The lead writes the probe record from your return.

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

The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them: there, the probe record's content, as a YAML block with `probed_commit` (full id), `judgement` (`pass` or `fail`) and `findings` (each with `id`, `severity`, `behaviour`, `fail_open` true/false), the named finding on the role set in the command's own environment among them, then the narrative. Refused twice for the same call: stop and say so.
