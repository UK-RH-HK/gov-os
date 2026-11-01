## Standing rules for every worker of DAEO-s9qc (W2-87) — read first

- **Step 0, before any work: the sandbox check, reported first in your return.** (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-s9qc','w').write('x')"` must fail; (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.
- Then run `printenv GOV_ROLE GOV_TICKET` and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect your role, `DAEO-s9qc`, `/home/usain/gov-os-worktrees/W2-87` and `w2/W2-87`). If anything differs, stop and say so.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-87/src` set **per command** (never in a session's `--settings` env). Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Memory (DEC-836, DEC-860, DEC-859):** before reading files at random, ask `gov retrieve`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-87/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: take a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used it.
- **Reads open, writes closed (DEC-820):** you read freely, except (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read or name the qualification oracle); (c) the counterpart's work on this ticket: the engineer never reads `tests/acceptance/W2-87/` (it may run those tests and see their names, results and failure messages), and the test designer never reads this ticket's implementation (the files `git diff --name-only w2/integrate...HEAD` names, other than its own tests); (d) the hidden half of any evaluation set (`fixtures/evaluation/**/hidden/**`), by anyone, in any tree. Writes stay inside the paths your brief gives.
- **Read refusals (DEC-849):** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form; search named folders instead. Count the refusals you met and give the count in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target (use literal paths); no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file in your own session scratchpad (the folder your session names; the guard refuses `.gov-runtime/scratch/lead/`), written with the Write tool, and run that file. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- **Protected material:** never read the held-out material's contents; never print a secret; never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **No copy of the tree:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. A test that needs a repository builds a temporary one from scratch. No clone or copy of a programme under `.gov-runtime/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` (and in your return), write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Git:** no amend, no rebase, no reset, no `git checkout` of another commit, no `git clean`, no `--no-verify`, no push, merge or tag. Trailers in the final block with `git commit --trailer`. Never edit `.tickets/`, the decision register or `docs/plan/`. Never run `gov close`, `gov adopt`, `gov pause`, or `gov rebuild` (of any kind; never `--no-embeddings`). Install nothing.
- **Disk (DEC-898):** your share of the ticket's budget is 3 GB and 200,000 files and folders outside the tracked tree. Keep pytest's own temp retention (never `--basetemp`); clean up what you make as soon as you no longer need it; measure your scratch (`du -sh`, `du -s --inodes`) at the end and give the figures.
- **Run everything in the foreground,** one command after another; return only after your commit exists. Never run a suite with `-x`. While `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists, run at most a single test file.
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return `AUTH_REQUIRED`.

# Brief: engineer, DAEO-s9qc (W2-87) — the record batch: `docs/research/W2-87-memory-measure.md`

You are a fresh engineer. Ticket: DAEO-s9qc (W2-87), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-87` on branch `w2/W2-87`. The code is done (head `cffef92c8534`). The lead ran W2-61's measure in its own session; you write its record **from the lead's outputs below**, in the form of `docs/research/W2-61-baseline.md` (read it first: its sections, its tone, its rule that the record holds scores only). You run no measure, no rebuild and no retrieval of your own for the figures.

## Rules for the record

- **Scores only:** ids, counts, ranks, digests, pass or fail. Quote no question's text, no gold answer and no retrieved text (W2-61's rule). Never read `fixtures/evaluation/**/hidden/**`; you need nothing under `fixtures/` at all.
- **Both figures together, always** (DEC-833 item 3): wherever hit@5 appears, full evidence appears beside it, and the in-the-bundle count.
- Commit hashes as 12 digits. Sources: DEC-952 item 1, DEC-941 item 1, DEC-833 item 3, DEC-877, CAP-10; the ticket's KPI line 6.
- Write only `docs/research/W2-87-memory-measure.md`, in a commit of its own (DEC-924 item 2).

## The sections (W2-61's form)

1. **What was measured, and where:** the three code states and the tree; the launchers; the measure; the set (visible half only); the budgets (the measure's defaults: `--batch-size 10 --bundle-budget 6000 --stack-budget 24000`).
2. **The stores' fingerprint**, with the deviation below.
3. **The runs** (table).
4. **The totals: both figures together**, beside W2-61's baseline.
5. **Per question**, baseline, control, batch 1 and head side by side; Q17 and Q20 named; every question whose first gold rank changed, before and after.
6. **What each part moved** (the owner asked to see it per step): the register fix, then the authority order.
7. **Deviations and what they mean.**
8. **How to repeat it.**

## The lead's outputs

**Clones** (each `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS <path>`, detached):
- `/home/usain/gov-os-runs/W2-87/head` at `cffef92c8534` (the branch head's code: both parts and the one-line fix; the tree measured and its stores);
- `/home/usain/gov-os-runs/W2-87/base` at `df0782fa4c4e` (the ticket's base; only its `src/` is used: the control);
- `/home/usain/gov-os-runs/W2-87/register` at `006ad0bb36ce` (batch 1, the register fix alone; only its `src/` is used);
- `/home/usain/gov-os-runs/W2-87/measure` at `e814289d58c4` (`w2/integrate`'s head when measured; the measure's code, `src/gov/retrieval/measure.py` last changed at `289b9314`, and the visible set, both unchanged since `df0782fa4c4e`).

**Launchers** (the pinned launcher's body: import `main` from `gov.cli.main` and exit with it), first lines:
- control `gov-base`: `#!/usr/bin/env -S PYTHONPATH=/home/usain/gov-os-runs/W2-87/base/src /home/usain/.local/share/gov-os/pin-5c401220/bin/python`
- batch 1 `gov-reg`: `#!/usr/bin/env -S PYTHONPATH=/home/usain/gov-os-runs/W2-87/register/src /home/usain/.local/share/gov-os/pin-5c401220/bin/python`
- head `gov-head`: `#!/usr/bin/env -S PYTHONPATH=/home/usain/gov-os-runs/W2-87/head/src /home/usain/.local/share/gov-os/pin-5c401220/bin/python`
- They lived in the lead's session scratchpad (`/tmp/claude-1000/…/scratchpad/bin/`), because the guard refused the orchestrator role's writes under `~/gov-os-runs/W2-87/bin/`.

**Each run's `retriever`** (from its record): control `gov_file` `/home/usain/gov-os-runs/W2-87/base/src/gov/__init__.py`, version `gov 0.1.0 (commit df0782fa4c4e)`; batch 1 `/home/usain/gov-os-runs/W2-87/register/src/gov/__init__.py`, `(commit 006ad0bb36ce)`; head `/home/usain/gov-os-runs/W2-87/head/src/gov/__init__.py`, `(commit cffef92c8534)`. Each record's `commit` (the tree): `cffef92c8534`.

**The measure command** (each run, from the head clone): `env -u GOV_TICKET PYTHONPATH=/home/usain/gov-os-runs/W2-87/measure/src python3 -m gov.retrieval.measure memory-retrieval --root /home/usain/gov-os-runs/W2-87/head --sets-root /home/usain/gov-os-runs/W2-87/measure --part visible --gov <launcher> --out /home/usain/gov-os-runs/W2-87/records --json [--compare <control's record>]`.

**The stores:** built once in the head clone at `cffef92c8534`, for all three runs, as `env -u PYTHONPATH -u GOV_TICKET flock /tmp/gov-os-rebuild.lock <gov-base> rebuild --json`, with embeddings (never `--no-embeddings`), after the disk gate (875 GiB and 65,160,169 inodes free). Exit 0; ended 21:20:11 UTC on 2026-10-30. `result.digest` and `result.store.digest`: `0b7e7d00c83f52f5cd6772c95eb1ac7637b83c081f192699a68bd13bd63a35c5`, no invalid entries; stores `lexical`, `semantic`, `codeintel` each `recreated`. sha256 after it: `.gov-runtime/store.db` `bdb4572966a45eccbbfa7119b406b9ddc8b43cee509a71c44cc13c4d2e5d9070`; `.gov-runtime/codeintel/home/code.db` `45073c6280bd8a7e32b3a054cbb0eeea3b91e5b8589cbcb11ee3ab7885a38c17`; `.gov-runtime/codeintel/home/_config.db` `6881a590e961b4c4faff0180c79e87d6af9c34a9367e12cf28bbe2dbc4028cf8`. This worktree's own rebuild at the same commit (its own code) gave the same digest.

**Deviation 1, the store builder:** the brief named the pinned gov (`5c40122014da`). Its rebuild (exit 0, digest `522296ef1709a39100d8a8ce9ed9819bf1c548373c3f877d7fa1cc41361c6c2d`, at `060e03ef57ea`) writes a `register_entries` table with no `span` column. W2-03's queries, in the base's code as in batch 1's and the head's, select that column, so every retrieval refused with STORE_MISSING ("no such column: span"). The store code (`src/gov/store/**`, `src/gov/records/**`) is the same at the base, batch 1 and the head, so the lead built the stores with the base's code: one store, by code no run is testing, for all three runs. W2-61's baseline was the pinned gov retrieving from the pinned gov's stores; the control here is the base's code on the head tree's stores, which is why the control and the baseline differ.

**Deviation 2, the tree:** the first measured tree was `060e03ef57ea` (control there: 7, 11 and 13 of 20, record `measure-memory-retrieval-visible-20261030T204744666636Z.json`). The lead's verification then found that the visible set's Q11 names the line `    fused = rrf(routes)` of `retrieve.py`, which batch 2 had rewritten; the fix `cffef92c8534` keeps the line and lifts on the next one (no change of behaviour). The runs were stopped and redone on `cffef92c8534`, the tree reported here. The control's figures were the same on both trees.

**Deviation 3, the order of steps:** the owner asked for a re-measure after the register fix and again after the authority order. The lead ran both after the code was done, on one tree and one set of stores, with batch 1's code as its own launcher: the same figures the step-by-step order would give for the code, with no difference of tree or store between the steps.

**The runs** (each exit 0, stderr empty; times UTC, 2026-10-30):

| Run | Code (`--gov`) | Ended | Length | Record (`--out`) | `--compare` |
|---|---|---|---|---|---|
| control | `gov-base` (`df0782fa4c4e`) | 21:38:41 | 1,088 s | `measure-memory-retrieval-visible-20261030T213841067037Z.json` | — |
| batch 1 | `gov-reg` (`006ad0bb36ce`) | 21:52:56 | 846 s | `measure-memory-retrieval-visible-20261030T215256578023Z.json` | the control |
| head | `gov-head` (`cffef92c8534`) | 22:11:54 | 1,129 s | `measure-memory-retrieval-visible-20261030T221154739899Z.json` | the control |

**Totals:**

| | hit@5 (floor 85) | full evidence (target 99 %) | in the bundle |
|---|---|---|---|
| W2-61 baseline (`23079f92a6fa`, pinned gov) | 8 of 20 (40 %) | 12 of 20 (60 %) | 14 of 20 |
| control (base code) | 7 of 20 (35 %) | 11 of 20 (55 %) | 13 of 20 |
| batch 1 (register fix) | 7 of 20 (35 %) | 11 of 20 (55 %) | 13 of 20 |
| head (register fix and authority order) | 11 of 20 (55 %) | 11 of 20 (55 %) | 15 of 20 |

**Per question.** Each cell: hit@5, first gold rank, in the bundle, full evidence (pieces found of needed). Baseline from W2-61's §5. Batch 1 equals the control in all five compared fields for 20 of 20 questions. The head differs from the control in the stacked digest for 20 of 20, and in the fields named.

| Q | baseline | control | batch 1 | head | head differs from the control in |
|---|---|---|---|---|---|
| Q01 | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | same as control | yes, 1, yes, yes (1/1) | stacked digest |
| Q02 | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | same | yes, 1, yes, yes (1/1) | stacked digest |
| Q03 | yes, 4, yes, yes (1/1) | no, 6, yes, yes (1/1) | same | yes, 2, yes, yes (1/1) | hit@5, first gold rank, stacked digest |
| Q04 | yes, 3, yes, yes (1/1) | yes, 3, yes, yes (1/1) | same | yes, 1, yes, yes (1/1) | first gold rank, stacked digest |
| Q05 | yes, 2, yes, yes (1/1) | yes, 2, yes, yes (1/1) | same | yes, 1, yes, yes (1/1) | first gold rank, stacked digest |
| Q06 | no, 9, yes, yes (2/2) | no, 9, yes, yes (2/2) | same | no, 7, yes, yes (2/2) | first gold rank, stacked digest |
| Q07 | no, 12, yes, yes (1/1) | no, 12, yes, yes (1/1) | same | no, 12, yes, yes (1/1) | stacked digest |
| Q08 | no, 9, yes, yes (1/1) | no, 9, yes, yes (1/1) | same | no, 11, yes, yes (1/1) | first gold rank, stacked digest |
| Q09 | no, 60, no, yes (1/1) | no, 60, no, yes (1/1) | same | no, 46, no, yes (1/1) | first gold rank, stacked digest |
| Q10 | no, 25, no, no (1/2) | no, 25, no, no (1/2) | same | no, none, no, no (0/2) | first gold rank, stacked digest |
| Q11 | yes, 4, yes, no (1/2) | yes, 4, yes, no (1/2) | same | yes, 4, yes, no (1/2) | stacked digest |
| Q12 | yes, 2, yes, yes (1/1) | yes, 2, yes, yes (1/1) | same | yes, 1, yes, yes (1/1) | first gold rank, stacked digest |
| Q13 | no, 6, yes, no (1/2) | no, 6, yes, no (1/2) | same | yes, 1, yes, no (1/2) | hit@5, first gold rank, stacked digest |
| Q14 | no, 16, yes, no (7/9) | no, 16, yes, no (6/9) | same | no, 17, yes, no (6/9) | first gold rank, stacked digest |
| Q15 | yes, 4, yes, yes (1/1) | yes, 4, yes, yes (1/1) | same | yes, 1, yes, yes (1/1) | first gold rank, stacked digest |
| Q16 | no, 7, yes, yes (1/1) | no, none, no, no (0/1) | same | no, none, no, no (0/1) | stacked digest |
| Q17 | no, 21, no, no (1/2) | no, 21, no, no (1/2) | same | yes, 2, yes, no (1/2) | hit@5, in the bundle, first gold rank, stacked digest |
| Q18 | no, none, no, no (0/2) | no, none, no, no (0/2) | same | no, none, no, no (0/2) | stacked digest |
| Q19 | no, none, no, no (0/1) | no, none, no, no (0/1) | same | no, none, no, no (0/1) | stacked digest |
| Q20 | no, 21, no, no (1/2) | no, 21, no, no (1/2) | same | yes, 2, yes, no (1/2) | hit@5, in the bundle, first gold rank, stacked digest |

**First gold ranks that changed, control → head:** better: Q03 6→2, Q04 3→1, Q05 2→1, Q06 9→7, Q09 60→46, Q12 2→1, Q13 6→1, Q15 4→1, Q17 21→2, Q20 21→2; worse: Q08 9→11, Q14 16→17, Q10 25→none (its one found piece lost: 1 of 2 → 0 of 2; Q10 was not full in either). Into the first five: Q03, Q13, Q17, Q20. Out of the first five: none. Into the bundle: Q17, Q20. Out: none.

**What each part moved:**
- **The register fix (batch 1):** nothing on this set. The register's last entry (DEC-953) is current, so no register chunk was being dropped, and the six questions with a ticket gained no register chunk in their stacked context. Its effect is on a store whose last entry is superseded (every register chunk was dropped) and on a closure that reaches an older entry; the acceptance tests show both.
- **The authority order (batch 2):** hit@5 7 → 11 of 20; in the bundle 13 → 15; full evidence 11 → 11. Q17 and Q20, whose first five were tests and assessment reports in W2-61's baseline, now have a governing source at rank 2. Full evidence did not move: Q17 and Q20 still find 1 of 2 needed pieces, and Q10 lost its one piece.
- **Against W2-61's baseline:** hit@5 8 → 11 (40 % → 55 %, floor 85: short by 30 points); full evidence 12 → 11 (60 % → 55 %, target 99 %: short by 44 points); in the bundle 14 → 15. The control (the base's code on today's tree) is already 1 below the baseline on each figure (Q03 and Q16 changed with the tree and the store builder, not with this ticket).

**How to repeat it:** W2-61's §8, with: three clones by exact path as above; the stores built in the head clone by the base's code (not the pinned gov, deviation 1); three launchers; the measure run three times on the same stores, the second and third with `--compare` the control's record; never `--part hidden`.

## Done when

- The file exists, every figure above is in it as given (none recomputed, none dropped), and every place that gives hit@5 also gives full evidence and the in-the-bundle count.
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-87/src python3 -m pytest tests/acceptance/W2-61 -q -p no:cacheprovider` still passes, and `python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/keyword_warn.py /home/usain/gov-os-worktrees/W2-87` lists nothing.
- One commit, the file alone:

      git commit -m "<subject>" --trailer "Task: DAEO-s9qc" --trailer "Implements: DEC-952, DEC-941, DEC-833" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

## Return

Your commit (12 digits) and its trailers; the file's line count; the test run's counts; your sandbox check; your `gov retrieve` use; read refusals met; your scratch figures.
Your final message is your return. It starts with these twelve labelled lines, then any payload:

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

The twelve fields come first, each as a labelled line, with any payload after them. Refused twice for the same call: stop and say so.
