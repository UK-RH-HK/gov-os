---
name: brief
version: 1.0.0
role: any
---
# Your assignment
You are a fresh {ROLE} session. Your role's rules are in your system prompt (template `{ROLE_TEMPLATE}`); this brief gives this assignment's facts.
Ticket {ID} ({W2}), profile {PROFILE}. Objective: {TITLE}. {TICKET_SUMMARY: one paragraph from the ticket's body}

## Where you work
| what | path |
|---|---|
| your tree (write here only) | {WRITE_TREE} |
| branch | {BRANCH} |
| allowed paths | {PATHS} |
| ticket file (read-only) | {TICKET_FILE} |
| your scratch | {WRITE_TREE}/.gov-runtime/scratch/ |

## What must be true (KPI lines and how each is checked)
{KPI_TABLE: | id | line | verify |}
Non-goals (do not build, do not test): {NON_GOALS}
Done when: the DoD lines {DOD_REFS} hold for your part.

## Inputs
- Sources: {SOURCES}. Read each by id in {REGISTER}, or ask memory (below).
- What the lead knows of the ground: {LEAD_NOTE}
{REPAIR: the failing output, verbatim, and nothing else of earlier rounds}

## Commands (copy them as they are)
{COMMANDS_TABLE: | name | command | for this role, from facts.yaml}
Ask memory first: {CMD:retrieve} "<which decision governs X | where is Y implemented>"; grep the register only by id.
Search again once: if the bundle does not answer, or your answer may be incomplete, ask once more in your own, different words; then answer from both bundles with path and lines, or say "not found". Two searches in all; never answer beyond what you read.
No `gov retrieve` in the sandbox, and no `gov context`: a launched worker searches with the Read and Grep tools, and searches again once the same way [DEC-1065].
Every whole-folder pytest run adds `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty `HOME`: run it as {CMD:pytest_folder} [DEC-1065].
Wait for anything long with {CMD:wait_for}, one call per 9.5 min; never a hand-written sleep loop.
No merge inside the sandbox: the CTO or your lead merges into your branch outside it; a restore or conflict resolution in `tests/acceptance/` is a test designer's [DEC-1052].

## Forms that work (the guard and the harness accept these)
- Write and edit files with the Write and Edit tools and absolute paths.
- Anything longer than one line goes in a script file under {WRITE_TREE}/.gov-runtime/scratch/, run with `bash <file>` or `python3 <file>`.
- Use literal paths, never a shell variable or `$(…)` as a write target; name the folder a listing or search starts at.
- The harness allows these headless without asking: {HARNESS_ALLOWED}. For anything else use a script file as above, or report it; never retry another form.

## Commit (your paths only)
```
git commit -m "{SUBJECT}" --trailer "Task: {ID}" --trailer "Role: {ROLE}" --trailer "Implements: {IMPL}" -- {COMMIT_PATHS}
```
- `Task:` is the ticket's id ({ID}, a `DAEO-…` id), never a W2 id [DEC-182].
- `Implements:` lists only ids from the ticket's `sources:`, each ACCEPTED [DEC-927].
- Put an id you need that is not in `sources:` in `discoveries`, never into `Implements:` alone [DEC-1073].
- Cite only ACCEPTED decisions as rules; name a PROPOSED one "proposed", never as the rule [DEC-1073].

## Return (your last message; nothing else is read)
The twelve fields first, each a labelled line ("none" where nothing), then each section below, always present:
```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
template: {ROLE_TEMPLATE}@{ROLE_VERSION}
commits: <hash12> <subject> | Task/Role/Implements as committed
brief_gaps: none | - <what was missing> | <where it belonged: template, facts, ticket, tool> | <minutes, est.>
guard_refusals: none | {STEP:guard_refusal_lines}
```
Refused twice for the same call: stop and say so. Never work around a refusal: report it.
