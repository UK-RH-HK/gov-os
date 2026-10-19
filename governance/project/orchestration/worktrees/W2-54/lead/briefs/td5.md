You are a fresh independent test designer (MR-3). Ticket: DAEO-0rfi (W2-54), profile FULL, **round 4c**. You work only in the worktree `/home/usain/gov-os-worktrees/W2-54` on branch `w2/W2-54`, launched through `gov launch` under its OS sandbox. Round 4's code is committed and measured green; three of its acceptance cases in `tests/acceptance/W2-54/test_w2_54_cpu_embedder.py` are red for reasons in the tests, not the code, and the orchestrator's DEC-811 (delegated, 2026-10-19) decides how they change. You make those changes, and nothing else.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0rfi','w').write('x')"` must **fail**. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must **work**. If (a) wrote the file or (b) failed, stop there and return, naming what happened (never delete a file (a) made).

## Standing rules (read first)

- Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-0rfi`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-54` and `w2/W2-54`) and `git log --oneline -1` (expect `4662871a`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. A foreground command is killed at 10 minutes: give long commands the Bash tool's `timeout: 600000`, and run a long suite file by file or case by case.
- **The code under test (DEC-732):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- The test command: `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/acceptance/W2-54/<file> -q -p no:cacheprovider -rs`, run to its end, never with `-x`.
- **Inside your sandbox `gov` reaches no shared Ollama** and the GPU is hidden: nothing you run is evidence about the GPU. The `shared_gpu` and `local_only` cases, `test_w2_54_green_here.py`, W1-21's real-models case, `gov rebuild` on this worktree and `gov check` are the lead's: leave them out and say so.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no stash in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Tests never write the main tree's store, another worktree's, or this worktree's.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. The sandbox may show placeholder files in the worktree (`.bashrc`, `.mcp.json`, `docs/source`, …): never commit them.
- Never run `gov rebuild --no-embeddings`. Never run `gov close`, `gov adopt` or `gov pause`.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**`.
- Never edit `docs/audit/wave-1/W1-43-wave-1-exit-audit.md`.
- **What you may change:** `tests/acceptance/W2-54/**` only (in practice `test_w2_54_cpu_embedder.py` and the README; `w2_54_support.py` only if a change below needs it). No other folder. The lead compares the tree before and after your session.
- The git hooks are uninstalled: before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-0rfi.md` (read-only): its KPI lines and sources.
- `tests/acceptance/W2-54/README.md` ("Round 4") and `tests/acceptance/W2-54/test_w2_54_cpu_embedder.py`, `w2_54_support.py`.
- `docs/changes/W2-54-CIT-E.md` §5.6 (round 4's change and the lead's measurement in §5.6.4; read only).

## The red cases at `fd66ed9c` (the lead's run, outside the sandbox; 7 failed, 87 passed)

```
test_every_read_sends_its_question_to_the_cpu_embedder_and_nothing_to_the_shared_runner
  AssertionError: `search who fires the glazed bowls` sent the CPU embedder nothing to embed   (step 5)
test_an_embedder_at_the_cpu_address_that_does_not_report_the_model_on_the_cpu_gives_no_query_vector[gpu|partial|nothing|other-model]
  AssertionError: the lexical route did not answer: {'available': True, 'reason': None}  (evidence: [])
test_an_address_held_by_something_that_is_not_an_embedder_gives_no_semantic_answer_and_no_fallback
test_with_no_executable_and_nothing_at_the_cpu_address_the_semantic_facet_is_unavailable_and_the_rest_answers
  AssertionError: the other routes did not answer: {'lexical': {'available': True, ...}, 'semantic': {'available': False, 'reason': ...}}  (evidence: [])
```

The semantic facet behaves as the cases require (unavailable with a reason, no fallback). The lexical route is available but returns no evidence, because the question asked holds no phrase a fixture note holds lexically. Step 5 fails because its text was already embedded and cached earlier in the same case (step 1 asked the same question), so the CPU embedder is rightly asked nothing.

## The orchestrator's DEC-811 (delegated, 2026-10-19; staged, not in this worktree's register — apply it as written here)

1. **PKG-W2-54-4-1 (a):** the `gov retrieve` calls in `test_w2_54_cpu_embedder.py` that expect lexical evidence once the semantic facet is unavailable ask a phrase a fixture note holds (such as "fires the glazed bowls"). **The lexical route is not changed.** Keep every other assertion of those cases as it is: the semantic facet unavailable with a reason, exit code 0, no traceback, the question never sent to the shared runner (check that the text you now ask is the one the no-fallback assertions look for), nothing cached, and the lexical route's evidence non-empty.
2. **PKG-W2-54-4-2 (a):** steps 5 and 6 of `test_every_read_sends_its_question_to_the_cpu_embedder_and_nothing_to_the_shared_runner` ask new texts, ones no earlier step asked, so each step has a text the CPU embedder has not embedded yet. **The step-5 text is still aimed at the kiln** (the search's answer is still asserted to be the CPU embedder's vector, the kiln, where the shared runner's would be the forge): give the stand-ins the target they need for it, as the existing QUESTION has. The assertion that every step sends the CPU embedder at least one text and the shared runner none stays.
3. **Ride-along (DEC-802):** `test_the_change_record_states_w1_21_s_hit_at_5_with_cpu_query_vectors_at_or_above_80` reads **W1-21's headline hit@5** (the overall figure), not a per-class figure. Today the case accepts any figure from 80 to 100 on the line, so a per-class figure (the line in §5.6.4 also lists, for example, `failed-approaches 100.0`) satisfies it even if the headline were below 80. Make the case find the headline figure (for instance the figure stated as W1-21's hit@5 before the per-class list, or one marked as the headline; choose a reading the record's present line meets and a line whose headline is below 80 fails, whatever its per-class figures) and require it at or above 80. The pass line stays 80.

No pass line, no threshold and no expectation is lowered. Each change carries `Rewrite-Reason: DEC-811 …` naming its package. The README's "Round 4" section gets a short note per change (what the case asked before and after, and why).

## Runs (each to its end, never `-x`)

1. Step 0 and the start checks; the `gov.__file__` line.
2. After your changes: the three changed cases (all parametrisations), then `tests/acceptance/W2-54` in full with `-m "not local_only and not shared_gpu" --ignore=tests/acceptance/W2-54/test_w2_54_green_here.py` (or the suite's own marker names, as the README states), file by file if one run would pass 10 minutes. Expected: every case green with today's code, the 7 included. Also show the ride-along case red against a line whose headline is below 80 (a temporary copy of the record in your temporary folder, read by a throwaway check, or a parametrised fixture inside the test — your choice; leave no throwaway in the tree).
3. Name every case that is not green, with its output.

## Commit

Commit only your test paths, one commit, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "W2-54 (DAEO-0rfi): <what>" --trailer "Task: DAEO-0rfi" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-773" --trailer "Rewrite-Reason: DEC-811 (orchestrator, delegated, 2026-10-19): PKG-W2-54-4-1 (a) <...>; PKG-W2-54-4-2 (a) <...>; ride-along (DEC-802) <...>" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After it, check `git log --oneline -2` and `git status --short`: a commit you did not make, stop and say so.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Nothing comes before the twelve fields. Refused twice for the same call, stop and say so.

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

In the fields: the sandbox check's result first; your commit's hash; each changed case with what it asked or asserted before and after (no expectation lowered); the runs with their counts; the ride-along's red demonstration; the `gov.__file__` line; any package.
