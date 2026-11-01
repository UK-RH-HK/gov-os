# Brief: independent test designer, DAEO-jsg1 (W2-86), batch 1

You are a fresh independent test designer (MR-3). Ticket: `DAEO-jsg1` (`W2-86`), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-86-tests` on branch `w2/W2-86-tests`. You write the ticket's acceptance tests from its KPI lines and its sources, before and in parallel with the implementation (DEC-963), and you show them red. You never read or write the ticket's own worktree `/home/usain/gov-os-worktrees/W2-86`.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-jsg1','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (the twelve fields), naming what happened. Never delete anything outside this worktree.

## Standing rules (read first)

- Run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-jsg1`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-86-tests` and `w2/W2-86-tests`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- **The code under test (DEC-732), word for word:** **In this worktree, every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. — For you, in the tests worktree, "this worktree" is `/home/usain/gov-os-worktrees/W2-86-tests`: use `PYTHONPATH=/home/usain/gov-os-worktrees/W2-86-tests/src` per command, and quote that `gov.__file__` line. Your tests, once merged into `/home/usain/gov-os-worktrees/W2-86` and run from there, must read that worktree's own path map and import its own `src/`: locate the repository from the test file's own place (never a hard-coded worktree path), and say in the README how.
- **Retrieval (DEC-836, DEC-963):** use `gov retrieve` for what you need to know before reading files at random, and only from the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read). Never this ticket's worktree's store. For what changed on `w2/integrate` since that store's refresh, read `git show w2/integrate:<path>`. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths, which are `governance/project/path-map.yaml`'s working copy on the ticket branch `w2/W2-86`, `tests/unit/retrieval/test_w2_86*` and `docs/research/W2-86-memory-measure.md`; name in your return any such result you were served. (The path map as it stands at the base `9dc5288161c4` and on `w2/integrate` is the existing state and is yours to read.)
- **Reads open, writes closed (DEC-820).** You read freely: the whole repository, git history, other worktrees. Refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy it, never type its path); **(c) the counterpart's work on this ticket: you never read this ticket's implementation — no file that branch `w2/W2-86` changes against its base `9dc5288161c4` (`git diff --name-only 9dc5288161c4...w2/W2-86` names them), other than your own tests; do not read `/home/usain/gov-os-worktrees/W2-86` at all;** **(d) the hidden half of any evaluation set (`fixtures/evaluation/**/hidden/**`), in any tree, never read or run.** Never read or name the qualification oracle. Never write in `~/gov-os-workbench`; never list, glob or search it.
- **DEC-849, read refusals:** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return. Run no glob, search or listing over `governance/project/`: name files there one by one. Never read `.claude/settings.json`.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target (literal paths only); no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; anything longer goes in a script file you write with the Write tool under `/home/usain/gov-os-worktrees/W2-86-tests/.gov-runtime/scratch/td/`, and you run that file. A refused form is not retried in another disguise (DEC-409).
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you need, do not work around it: return it as a package.
- No copy of the repository: no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of it or of a folder of it. A test that needs a repository or a root builds a temporary one; a stand-in copies single named files (a path map obtained with `git show` written into a temporary folder is fine), never `governance/project/` whole. No clone or copy of a programme under `.gov-runtime/` (DEC-673). Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Install nothing (an install is a P1 package in your return). No subagents that write.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Disk budget (DEC-898):** your share is 2 GB and 100,000 files and folders outside the tracked tree. Keep pytest's own retention (no `--basetemp`); do not set or change `TMPDIR` (the sandbox sets its own temp folder). Clean up what you make as you go; measure your scratch (`du -sh`, `du -s --inodes` of `.gov-runtime/scratch/td/`) at the end and give it in `evidence`.
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return `AUTH_REQUIRED`.

## What you read

- The ticket file `.tickets/DAEO-jsg1.md` (read-only): its KPI lines (success and failure), its `allowed_paths` and its sources.
- Its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-86"), and §0 (rules for every ticket).
- The decisions in `docs/DECISION_REGISTER.md`: DEC-952 item 1, DEC-388 (DP-8 above all), DEC-381, DEC-694, DEC-951 item 5 (tests minimal and in proportion), DEC-963 (the parallel work order).
- Lens B's F6: `docs/assessment/2026-10/B-memory-retrieval.md` (the finding near line 520, the policy value near line 633).
- The existing state the tests work against (read as it stands at the base, `git show 9dc5288161c4:<path>`, or on `w2/integrate`):
  - the path map `governance/project/path-map.yaml`: its header (lines 1 to 3: every tracked path matches a pattern of exactly one namespace; `**` crosses folders, `*` stays inside one folder) and its `namespaces:` block;
  - the semantic route's existing selection of which chunks are embedded, in `src/gov/retrieval/semantic.py` (the value constant and the selection function that reads the path map and the store's chunk table), and the path-map pattern matcher it uses;
  - the vendored parts: the `superpowers` entry of `governance/project/tool-registry.yaml`, and `template/governance/kernel/skills/superpowers/vendored.yaml`.
  This is existing code that the ticket must not change; reading it to learn its interface is allowed. The ticket's own implementation is data (the path map's namespace block), which you never read on the ticket branch.

## The behaviour to test (the KPIs, in proportion: three cases and a short README, about 100 lines in all)

The ticket makes the kernel template embedded as the path map means it (`embedded, except vendored code`), by data only: the path map's `namespaces:` block. After the change:

- **Embedded:** every tracked file under `template/` except the sets below. Among them: the role files `template/governance/kernel/roles/*.md`, the hooks `template/governance/kernel/hooks/*.py`, the kernel skills `template/governance/kernel/skills/<name>/SKILL.md`, and `template/governance/kernel/skills/superpowers/vendored.yaml` (the kernel's own record).
- **Not embedded, vendored code:** `template/governance/kernel/vendor/**`; the kernel's copies of the vendored skills, `template/governance/kernel/skills/superpowers/<skill>/**` (every file in a folder below `superpowers/`, not `vendored.yaml` itself); the vendored tk, `template/governance/kernel/bin/**`.
- **Not embedded, generated adapter copies:** `template/.rulesync/**`.
- Every namespace's `embedding_policy` is exactly `embedded` or `not embedded` (DEC-388, DEC-694's two values); no other value anywhere.
- Every tracked path under `template/` matches exactly one namespace (the header's rule, `**` and `*` as the header defines them).
- No change to the indexer's code; a file outside `template/` keeps its embedding verdict.

Write exactly these three cases (no more), under `tests/acceptance/W2-86/`:

1. **Every tracked file under `template/` (by `git ls-files`, run in the repository the test file sits in) is in exactly one namespace of that repository's path map; and the indexer's selection takes the role files, the hooks, the kernel skills, `vendored.yaml` and every other such file but the vendored set and `template/.rulesync/**`, and takes none of those.** Drive the selection as the semantic route applies it: plant a table of chunk paths (the store's chunk table, one chunk per tracked path) in a temporary folder and ask the existing selection which chunks it embeds, reading the repository's own path map. No embedder, no rebuild, no network. Also assert that each of the vendored and generated sets is non-empty among the tracked files (so the case cannot pass vacuously), and that the role files, hooks and kernel skills are non-empty too.
2. **Every namespace's `embedding_policy` is exactly `embedded` or `not embedded`.**
3. **A guard: for every tracked path outside `template/`, the selection's verdict is the same under the repository's path map as under the path map at the base `9dc5288161c4`** (read with `git show 9dc5288161c4:governance/project/path-map.yaml` into a temporary root). Green before and after the change; the README says so and names that base.

Cases 1 and 2 must be red on today's map (the base), each for the reason the README states; case 3 green at the base.

## What you write

- Only inside `tests/acceptance/W2-86/` in your worktree: the test file(s) and a short `README.md` that maps each KPI line (success and failure) to its case, gives each case's expected red reason at the base, says case 3 is a guard green before and after with base `9dc5288161c4`, and says how the tests locate and exercise the worktree's own path map and `src/`.
- Behaviour through public interfaces wherever one exists; the existing selection is driven as the route applies it. Deterministic, no network, no embedder, no store rebuild, nothing written in the repository.
- Red first: run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-86-tests/src python3 -m pytest tests/acceptance/W2-86 -q -p no:cacheprovider` to the end (never `-x`); cases 1 and 2 fail for the stated reasons, case 3 passes. Quote the summary line.
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`. Commit only your test paths, in one commit, with the trailers in the final block:

    git commit -m "W2-86 (DAEO-jsg1): acceptance tests, the kernel template embedded as the path map means it" --trailer "Task: DAEO-jsg1" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-952, DEC-388" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then `git log --oneline -2` and `git status --short`, quoted.

## Return

Your commit's hash (12 digits); the test count; the KPI lines with their tests; the red reason as you saw it; whether you used `gov retrieve` and for what; any result served under the implementation paths (P-R1); the read refusals you met (DEC-849); any package.

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

Your return gives the twelve fields first, each as a labelled line, with any payload after them. Refused twice for the same call: stop and say so.
