You are a fresh engineer. Ticket: DAEO-juee (W2-62, "Resume in full: the session-start hook delivers the whole RESUME HERE block and names the prompt in force"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-62` on branch `w2/W2-62` (its acceptance tests are committed at `87cad875`). You implement the ticket until its acceptance tests pass.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-juee','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, naming what happened.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-juee`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-62` and `w2/W2-62`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=/home/usain/gov-os-worktrees/W2-62/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return.
- **Memory (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-62/src python3 -m gov.cli.main retrieve "<question>" --json`.
- **Reads (DEC-820, Policy 2):** you read freely: the whole repository, the committed context, git history, other worktrees. Only four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); (c) the counterpart's work on this ticket: **you never read `tests/acceptance/W2-62/`, by any tool** (no cat, Read, grep, git show or diff of it); you may run those tests and read their names, results and failure messages; (d) the hidden half of any evaluation set, by whoever is measured by it. Never read or name the qualification oracle. (The two earlier suites `tests/acceptance/W1-49/` and `tests/acceptance/W1-29/` are not this ticket's tests; you may read them, and you never write them.)
- **Read refusals (DEC-849):** until W2-58 lands, the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you met and give the count in your return. Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.rulesync/hooks.jsonc`.
- Refused twice for the same call: stop and say so; no third try (AR-6).
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. Commit your work before you run any long suite.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it); copy single named files only, never `governance/project/`. Nothing goes under a `.gov-runtime/` folder except your own scratch notes under `.gov-runtime/scratch/`.
- Never write in `~/gov-os-workbench`; never list, glob or search it.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Nobody runs `gov close`, `gov adopt`, `gov pause`, `gov rebuild --no-embeddings` or `docs/plan/tools/validate_s1.py`. On ESCALATION_BLOCKED from any command, stop and return it.
- Never ask the owner a question and never use a question box (DEC-850): a question comes back in your return as a package, and you keep working on whatever it does not block.
- Use your model's full window; you are never asked to stop or compact early (DEC-838).
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-juee.md` (read-only): its KPI lines and its `allowed_paths`.
- The list rows it takes in: W2-M372 and W2-M373 in `docs/plan/WAVE_2_LIST.md`.
- The decisions: DEC-792 in `docs/DECISION_REGISTER.md`. DEC-837 and DEC-838, as they apply to you: **DEC-837:** (1) the session-start hook loads the RESUME HERE block in full, never a first-9,000-characters cut (row W2-M372), and names the prompt in force, not Wave 1's (row W2-M373); (2) once it does, DEC-792's 8,000-character limit on RESUME HERE is lifted; the resume holds the full session state (what is happening, what was decided, what is next, where things are), and repository knowledge comes from retrieval and the context packets, not from the resume; (3) a checkpoint is written at every handover (a worker's return, a merge, a package, a compaction); (4) the ticket is a kernel hook change through CIT-P (CAP-33); the owner approved its scope. **DEC-838:** every session uses its model's full window; no launch sets a compaction threshold.
- The code the ticket touches: `template/governance/kernel/hooks/sessionstart.py` (with `precompact.py` beside it, which it imports), `template/governance/kernel/skills/checkpoint/SKILL.md`, the builder tests under `tests/unit/hooks/`, the change skill (`template/governance/kernel/skills/change/`) and an existing record such as `docs/changes/S2-CIT-P.md` for the CIT-P's form. This hook runs live in every session of the main tree once merged.

## The behaviour to build

The research the second KPI line asks for is done (measured by the orchestrator, 2026-10-19): Claude Code 2.1.292 (`~/.local/bin/claude`), a headless Haiku 4.5 session started in a folder with no project settings, `--settings` carrying one SessionStart hook that printed `{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext": <N characters ending in a random 17-character token>}}`; the session was asked, without tools, to quote the last 30 characters it saw. N = 9,500: the whole context arrived; the session quoted the token exactly. N = 12,000 and N = 60,000: the harness did not inject it; it said "Output too large (11.7KB). Full output saved to: `~/.claude/projects/<project>/<session>/tool-results/hook-<id>-1-additionalContext.txt`" and showed a preview; the token never reached the session (it quoted filler). So a SessionStart hook's context arrives whole only up to about 10,000 characters (the hook's own 10,000-character cap). **"In full" therefore means:** the hook's injection stays within that bound and carries the instruction to read the checkpoint's RESUME HERE section in full before anything else, naming the file, the section's exact line range and its size; when the section fits within the bound with the rest of the critical parts, it is injected whole as well.

For a session whose role is exactly `orchestrator`:

1. **The bound.** The injected text is never longer than 10,000 characters, whatever the checkpoint, the context packet or the ready list holds.
2. **The instruction, always.** When the checkpoint has a RESUME HERE section, the injection carries an instruction to read that section in full before anything else, naming the checkpoint's path (relative to the project, as today), the section's exact line range in that file, and its size. **The form, a public interface:** the range is written `lines <first>-<last>` (1-based, inclusive, line numbers of the checkpoint file), and the size is written `<n> characters` (n may carry thousands separators, as in `50,213 characters`). The range is exact: lines first to last of the file are the section, from its heading line to its last line that is not empty (trailing empty lines excluded), and the stated size is the number of characters of those lines joined by newlines. A reader that takes exactly those lines gets the whole section, with no character lost. The section is found as today: the heading that begins with "RESUME HERE" and everything up to the next heading of the same or a higher level (a line inside a fenced code block is not a heading), in the written part of the checkpoint (before the generated state block, if there is one).
3. **Whole when it fits.** When the whole section fits within the bound together with the other critical parts (the instruction and the staleness warning, if there is one), the section is also injected whole, character for character; a total of exactly 10,000 characters fits.
4. **Never a cut.** When it does not fit (for example a section of 50,000 characters), the injection is still within the bound and still carries the instruction of item 2 whole; it never carries a cut of the section's first 9,000 characters, and the word "truncated" appears nowhere in it. Whether a short opening part of the section is shown as well is your choice; if you show one, never let it pass for the whole section.
5. **The critical parts are never trimmed.** The instruction, the staleness warning (as today) and the whole section when it fits are never cut. When the optional parts (the `gov context --brief` summary, the `tk ready` output, the checkpoint resume brief) would take the injection past the bound, the optional parts are the ones trimmed.
6. **No section.** A checkpoint with no RESUME HERE section, or no checkpoint at all, still names the checkpoint's path and says it is missing, can't be read or has no RESUME HERE section; exit 0.
7. **The prompt in force (W2-M373), a public interface:** the project's configuration names the orchestrator's prompt in `governance/project/roster.yaml` (of the project the hook runs for, `CLAUDE_PROJECT_DIR`), under `roles:` → `orchestrator:`, as the key `prompt:` with a path relative to the project (for example `prompt: governance/project/prompts/w2-orchestrator.md`). When that key is set, the injection names that path, in the main tree (as today: read the prompt and the checkpoint now) and in a linked worktree (as today: the ticket-lead sentence, appendix A5 of that prompt, and the lead checkpoint). When it is absent (no roster file, no `prompt` key, a roster that is not valid YAML), the injection names no prompt at all: not `governance/project/prompts/w1-orchestrator.md` and no other path under `governance/project/prompts/`; it still names the checkpoint and the instruction to read it. No constant prompt path remains. **That key is not yet in this repository's own roster, and `governance/project/roster.yaml` is outside the ticket's paths: do not write it.** Name the exact line to add in your return as a package; until it is added, this repository's sessions are told no prompt.

For every session:

8. **Exit 0, never blocks.** Unreadable input (stdin that is empty, not JSON, a JSON array or a JSON string; a checkpoint or roster that cannot be read or decoded) still exits 0, prints either nothing or one valid JSON object of the form `{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext": <text>}}`, and returns well within the hook's timeout.
9. **Other roles.** A role other than `orchestrator` gets no RESUME HERE injection: none of the section's text, no instruction to read the checkpoint's section and no line range.

The checkpoint skill (`template/governance/kernel/skills/checkpoint/SKILL.md`, the resume rule only):

10. It states the resume rule: RESUME HERE holds the full session state (what is happening, what was decided, what is next, where things are); repository knowledge comes from retrieval and the context packets, not from the resume; a checkpoint is written at every handover (a worker's return, a merge, a package, a compaction) [DEC-837 items 2 and 3]; and the session-start hook delivers the section in full, as above. It sets no 8,000-character limit on RESUME HERE. Change nothing else in the skill; if the skill's version field needs a bump by the project's rules, bump it.

The change record (`docs/changes/W2-62-CIT-P.md`):

11. A CIT-P (the change skill's form; `docs/changes/S2-CIT-P.md` is an example) for this kernel hook and skill change: the trigger (DEC-837, rows W2-M372 and W2-M373), **the research record as given above** (Claude Code 2.1.292, headless, the three sizes and what happened at each, the conclusion: the bound of about 10,000 characters and the route by instruction, file, line range and size; the live resumed-session check is run by the lead), the three options (apply now, defer, re-baseline) with the owner's choice (apply now, scope approved in DEC-837, CAP-33), the impact (the hook, the skill, the unit tests, the earlier acceptance suites W1-49 and W1-29 that the test designer revised, DEC-792's limit lifted, and the roster line still to be added by the owner or the orchestrator), and the independent review that follows (a read-only reviewer after green).

## What you write

- Only inside the ticket's `allowed_paths`: `template/governance/kernel/hooks/sessionstart.py`, `template/governance/kernel/skills/checkpoint/**` (the resume rule only), `tests/unit/hooks/**`, `docs/changes/W2-62-CIT-P.md`.
- Never the acceptance tests (MR-3), nothing under `tests/acceptance/**`. A test you think is wrong is returned as a package, never edited and never worked around.
- Builder tests go in `tests/unit/hooks/`, as regression evidence only. Existing builder tests there that assert the old behaviour (the Wave 1 prompt constant, the cut) are updated to the new behaviour; say which.
- Proportion (DEC-135): no code for edge cases beyond the KPI lines; the estimate is about 60 lines. Never make a guard decision fail open; the hook still exits 0 on any input and never blocks a session.
- Run, in the foreground, each suite to its end, never with `-x`, until they pass:
  - `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-62/src python3 -m pytest tests/acceptance/W2-62 -q -p no:cacheprovider -rs -m "not local_only"` (the one `local_only` live case needs the network, which your sandbox has not; the lead runs it);
  - the same for `tests/acceptance/W1-49` (with `-m "not local_only"`) and `tests/acceptance/W1-29`, each in its own process;
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-62/src python3 -m pytest tests/unit/hooks -q -p no:cacheprovider`.

## Commit

Commit only your paths (`git commit -- <paths>`), with the trailers in the final block (DEC-182, DEC-476). There is no pre-commit hook; never `--no-verify`, never `core.hooksPath`:

    git commit -m "W2-62 (DAEO-juee): the session-start hook names the section's lines and size, and the prompt from the roster; the checkpoint skill's resume rule; the CIT-P" --trailer "Task: DAEO-juee" --trailer "Role: engineer" --trailer "Implements: DEC-837" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2` and `git status --short`.

## Return

Your last message, complete in itself. The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Put in them: the sandbox check's result; your commit's hash; the files changed; the tests you ran with their counts; the lines added and removed (against the estimate of 60); the builder tests you changed; the guard read refusals you met (a count, with what was refused); whether you used `gov retrieve`; the `gov.__file__` line; the roster line as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence); anything else you were refused or could not settle, as a package.

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

Refused twice for the same call: stop and say so.
