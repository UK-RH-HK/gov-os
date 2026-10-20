# Brief: engineer — W2-59 (DAEO-kh9l), run 2: the CIT-P brought up to date

You are a fresh engineer. Ticket: `DAEO-kh9l` (`W2-59`, "The pinned judge: the declared checks and the hook lines run from the pin; the packaging gaps"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-59` on branch `w2/W2-59`. The ticket's code is done and its own acceptance tests pass. **Your one task: bring its change-impact proposal, `docs/changes/W2-59-CIT-P.md`, up to date with what has happened since it was written,** so the owner approves an accurate record (CAP-33). You change no code and no test.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kh9l','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-kh9l`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-59` and `w2/W2-59`). If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m gov.cli.main retrieve "<question>" --json`. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return which questions you asked and whether the answers helped. (The index may be stale; if it answers `FACET_UNAVAILABLE`, say so and read the named files.)
- **Reads are open, writes are closed (DEC-820, Policy 2).** You read freely: the repository, git history, other worktrees. Four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); (c) **the counterpart's work on this ticket: you never read `tests/acceptance/W2-59/`** — no file there, by any tool (its README included); you may run those tests and read their names, results and failure messages. The revised earlier cases in `tests/acceptance/W1-22/` and `tests/acceptance/W1-26/` (commit `45c6bfae`) are also a test designer's work on this ticket: describe them from that commit's message and the decision (`git log -1 --format=%B 45c6bfae`, `git show --stat 45c6bfae`), never from their source; (d) the hidden half of any evaluation set, by whoever is measured by it. Never read or name the qualification oracle.
- **DEC-849, read refusals until W2-58 lands:** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. **Count every read refusal you meet and give the count in your return.** Never read `.claude/settings.json`.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you need, do not work around it: return it as a package.
- Run everything in the foreground, one command after another. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag. Install nothing; never `sudo`.
- **No copy of the repository:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it.
- Nothing goes under a `.gov-runtime/` folder (DEC-673), in `~/.local` (never touch the owner's pin), or in `~/gov-os-workbench`.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Write files with the Write and Edit tools, with literal absolute paths. No subagents that write. Never write `.gov-runtime/**`. Never touch `tests/acceptance/**`. **Write only `docs/changes/W2-59-CIT-P.md`.**
- Never ask the owner anything and never notify anyone (DEC-850, DEC-855): a question is a package in your return.
- You use your model's full window; nobody asks you to stop or compact early (DEC-838).

## What you read

- `docs/changes/W2-59-CIT-P.md` as it stands, and the ticket file `.tickets/DAEO-kh9l.md` (read-only).
- In `docs/DECISION_REGISTER.md`: DEC-864 (W2-59's packages decided: items 1 to 4), DEC-865, DEC-822, DEC-835, DEC-853 item 4, DEC-750, DEC-754, CAP-33.
- The rows DEC-864 names, in `docs/plan/WAVE_2_LIST.md`: W2-M388, W2-M389, W2-M390, W2-L371.
- The history: `git log --oneline c5100159..HEAD` and the messages of `3eadca4c` (this branch's merge of `w2/integrate` at `74d22909`; it brought W2-62's session-start hook change, merged `6e4b2750`, and W2-50's secrets-scan fix, merged `98effadc`), `6d4925ab` (that merge's record corrected) and `45c6bfae`.
- The code at the head, where you need it to state facts (for example how `template/governance/kernel/hooks/sessionstart.py` stands after the merge; whether W2-05's overlap in §6 still holds against `w2/W2-05` as it stands now: `git merge-tree --write-tree --name-only HEAD w2/W2-05`, read-only).

## What the record must say after your edit (facts only, each with its source)

1. **The base:** this branch now holds `w2/integrate` at `74d22909` by the merge `3eadca4c` (git's own merge, no conflict); the front matter and §1 say so, and the original base `c5100159` stays named as where the change started.
2. **§7, the packages, decided (DEC-864):** P1 (the two hook programs put the project's `src` on their import path) is row W2-M389 for W2-10; P2 (`gov --version` from an installed wheel) stays as built, row W2-L371 for W2-16 and W2-18; the residual that the hook programs still come from the tree while their package comes from the pin is row W2-M390; the secrets scan's vanishing file is W2-M388. The owner acts stay, **in this order: first re-pin at the merge commit of this ticket into `w2/integrate` (it must hold W2-50's fix, DEC-853 item 4), then regenerate the settings from `.rulesync/hooks.jsonc`.** If the record states the opposite order anywhere (today §7's table says A1 regenerate then A2 re-pin "after A1"), correct it and say why in one line (the live hook programs and the pin's package then match from the first regenerated session).
3. **The earlier tests revised (DEC-864 item 1):** a short section naming the three cases (`tests/acceptance/W1-26/test_w1_26_planted_defects.py::test_planted_authority_defect_decision_checker_exception_not_swallowed`; `tests/acceptance/W1-22/test_w1_22_canaries.py::TestCanaryRunner::test_lexical_canary_hits_after_reindex` and `::test_semantic_canary_hits_after_reindex`), why they assumed what DEC-822 item 3 and DEC-835 remove, that a fresh independent test designer revised their setup only (commit `45c6bfae`, `Rewrite-Reason: DEC-822 item 3, DEC-835 (DEC-864)`), and that no KPI of W1-22 or W1-26 changed and no expectation was lowered.
4. **§4 "What stays"** no longer says the hook programs' import path is "with the owner as a package": it names row W2-M389.
5. **§6 W2-05's overlap:** still true as stated, or corrected from your read-only `merge-tree`.
6. **§10 Verification:** keep run 1's figures, labelled as run 1's; add one line that the lead's verification of run 2 (after the merge and the revision) is recorded in the lead's return. Do not invent figures.

Keep the record's form, style and length; change only what is stale or missing. `status: PROPOSED` stays.

Check it: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m gov.cli.main check --json` and report the status of the documentation and citation checks (those whose names say decisions, citations, docs or provenance) before and after your edit; a check your edit turns red is fixed before you commit.

## Commit

    git commit -m "W2-59 (DAEO-kh9l): the CIT-P after the merge-back and DEC-864" --trailer "Task: DAEO-kh9l" --trailer "Role: engineer" --trailer "Implements: DEC-864, DEC-835, CAP-33" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- docs/changes/W2-59-CIT-P.md

Check `git log --oneline -2` and `git status --short` after it.

## Return

Your last message, complete in itself. In `evidence`: the sandbox check's result (first), your commit hash with its trailers, the `gov.__file__` line, and the before and after status of the checks above. In `work_completed`: each of the six items and what you changed for it. Also give: the number of guard read refusals you met, and the `gov retrieve` questions you asked.

**The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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
