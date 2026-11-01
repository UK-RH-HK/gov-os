# Brief: independent test designer, DAEO-blwa (W2-122), STANDARD

You are a fresh independent test designer (MR-3). Ticket: DAEO-blwa (W2-122), profile STANDARD. You work only in the
worktree `/home/usain/gov-os-worktrees/W2-122-tests` on branch `w2/W2-122-tests` (DEC-963). You never read or write
the ticket's own worktree, `/home/usain/gov-os-worktrees/W2-122`. You write the ticket's acceptance tests from its KPI
lines and its sources, in parallel with the engineer, and you show them red.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-blwa`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-122-tests` and
  `w2/W2-122-tests`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing
  started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for
  verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122-tests/src` set
  **per command** (never in a session's `--settings` env). Your verification shows it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122-tests/src python3 -c "import gov; print(gov.__file__)"`, quoted in
  your return; it must point into this worktree. Your tests must exercise whatever `gov` the pytest process imports:
  every `gov` they start runs as `sys.executable -m gov.cli.main` with the pytest process's own `PYTHONPATH`
  inherited, so that, once merged into the ticket's worktree and run there with that worktree's `PYTHONPATH`, they
  exercise the ticket's code. Your README says so.
- **Retrieval (DEC-963, DEC-836):** use `gov retrieve` for what you need to know before reading files at random, and
  only from the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`
  (a read). Never the ticket worktree's store. **Never one giant query (DEC-860):** a large question is taken in
  batches (`--batch-size`, then `--continue <token>`). **A code question (DEC-859)** uses the code-graph tool's own
  traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. What
  changed on `w2/integrate` since that store's refresh, read with `git show w2/integrate:<path>`.
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths
  (`src/gov/rebuild/seed.py`, `src/gov/rebuild/command.py`, `tests/unit/rebuild/test_w2_122*`,
  `docs/changes/W2-122-evidence.md`), and name in your return each such result you were served (DEC-820 (c)). You
  may read `src/gov/rebuild/command.py` as it stands on `w2/integrate` (`git show w2/integrate:src/gov/rebuild/command.py`)
  to learn today's public behaviour, never the ticket branch's.
- **Policy 2 (DEC-820):** reads are open, with four refusals: (a) secrets and keys, never printed; (b) the contents of
  the held-out qualification material (its file names may be seen); never read or name the qualification oracle;
  (c) the counterpart's work on this ticket: you never read this ticket's implementation, the files
  `git -C /home/usain/gov-os-worktrees/W2-122 diff --name-only w2/integrate...HEAD` names (other than your own
  tests), and never anything in `/home/usain/gov-os-worktrees/W2-122`; (d) the hidden half of any evaluation set, by
  whoever is measured by it. Writes stay inside your paths.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the
  repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named
  folders instead, and count the refusals in your return. Never read `.claude/settings.json`.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target, no here-document, no
  backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; anything longer goes in a script file under
  `/home/usain/gov-os-worktrees/W2-122-tests/.gov-runtime/scratch/td/` written with the Write tool, then run. A refused
  form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of
  this repository). A test that needs a repository builds a temporary one from scratch, under pytest's `tmp_path`. No
  clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Never write in `~/gov-os-workbench`; never
  list, glob or search it. Inside a session `.gov-runtime/freeze` may show as a placeholder device file: conclude
  nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, write commit hashes as 12 digits, never the full 40, and
  never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Your budget (DEC-898):** 5 GB and 250,000 files and folders outside the tracked tree. Set
  `TMPDIR=/tmp/gov-os-lead-W2-122` on every test run. Keep pytest's own temp retention; never `--basetemp`. Clean what
  you make as soon as it is no longer needed. Measure (`du -sh` and `du -s --inodes`) before your red run and at the
  end; give the figures in `evidence`.
- **Heavy steps (DEC-979 D1, DEC-1008):** one test file is not heavy. If your red run covers more than one file, run it
  as `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh <the pytest command>`.
  A rebuild of this repository itself is heavy and you do not need one: your tests build small temporary
  repositories. Never run `gov rebuild --no-embeddings` on any real worktree.
- Install nothing (a tool you need is a package, P1). No push, merge, rebase or tag. Never write `.gov-runtime/**`
  outside `.gov-runtime/scratch/`. No subagents that write. Never ask or notify the owner; never `owner-ping`.
- On an authentication or access error, stop and return `AUTH_REQUIRED`. On ESCALATION_BLOCKED from any command,
  stop and return it.

## What you read

- The ticket file `.tickets/DAEO-blwa.md` (read-only): its KPI lines, its `allowed_paths` and its sources.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-1014 (items 4 and 6), DEC-1015 (item 4), DEC-1011, DEC-1001,
  DEC-982, DEC-996 item 3, DEC-719, DEC-530, DEC-374, DEC-694, DEC-966, DEC-963.
- W2-116's ticket `.tickets/DAEO-f58b.md` (its fourth KPI line: the warm base `gov rebuild --seed` reads).
- The WBS rules, `docs/plan/WAVE_2_WBS.md` section 0, and the W2-122 card in section 2.
- The public interfaces, as they stand on `w2/integrate`: `gov rebuild` and its `--json` answer and exit codes; the
  stores it writes under `.gov-runtime/` (the record store `store.db`, the lexical and semantic stores, the code-graph
  index under `codeintel/`, `query-vector-cache.db`); the semantic store's manifest of the embedder model and revision
  (DEC-374); the embedding endpoint the semantic stage asks (`OLLAMA_HOST`, its model list, its embed requests); the
  machine-wide secrets record (W2-107, `GOV_SECRETS_CACHE`); the rebuild settings file
  `governance/project/rebuild.yaml` (W2-76). Existing tests on `w2/integrate` that stand up a local stand-in embedding
  endpoint, or plant a repository and rebuild it, show how to do so: find them yourself and reuse their way.

## The behaviour to test

The ticket's KPI lines, as they stand in its file, and this interface, which the lead fixes so that you and the
engineer build to the same outside (a lead's reading, logged for the CTO):

- **K1 (seeded equals cold).** `gov rebuild --seed <folder>` takes `<folder>`, the root of a warm base tree (the folder
  that holds that base's `.gov-runtime/`, as the integration store `~/gov-os-worktrees/W2-00-store` does; a link is
  followed). It copies the base's stores (the lexical, semantic and code-graph stores, and the secrets record's
  entries) into the tree, then rebuilds incrementally: only the files whose content differs from the base's are
  re-embedded (seen at the embedding endpoint: no embed request for a chunk of a file the base already held with the
  same content). The result is the same store, entry for entry, as a cold rebuild of the same tree: the rebuild
  digests equal, and every chunk's vector equal. Check it on a planted repository: a base built cold at one commit,
  a tree at a later commit that adds, changes and removes files, seeded from the base, against a cold rebuild of that
  same tree.
- **The answer.** A rebuild given `--seed` answers, in its `--json` result, a `seed` object with `status` one of
  `seeded`, `refused` or `none`, the `base` it read (or none), and a `reason` that names why where it is not
  `seeded`. Without `--seed`, `gov rebuild` does not seed (today's behaviour).
- **The base's record.** Every full rebuild writes `.gov-runtime/rebuild/stores.json` in its tree: a JSON object with
  at least `code` (the fingerprint of the Gov OS code that built the stores), `embedder` (an object with `model` and
  `revision`, as the semantic stage records them) and `schema` (the stores' schema version). The seed compares the
  base's record with the tree's own build (the running code's fingerprint, the embedder the endpoint reports now, the
  running code's schema version).
- **K2 (fail closed).** A base whose `code`, `embedder` (model or revision) or `schema` differs from the tree's, or a
  base with no readable record, is refused: `seed.status` is `refused`, its `reason` names what differed (the words
  `code fingerprint`, `embedder model` or `schema`, or that the base has no record), and the rebuild runs cold: the
  store is entry for entry a cold rebuild's, never one that mixes two embedders. The rebuild itself succeeds.
  Construct the mismatch by building a base, then changing one value in its record; for the embedder, also by
  building the base against a stand-in endpoint that reports another revision.
- **K4 (configured base, any adopted repository).** `gov rebuild --seed` with no folder reads the warm base from the
  project's configuration: the key `integration_store` in `governance/project/rebuild.yaml`, an absolute path. A
  project with no such key, or one whose path holds no base, rebuilds cold with `seed.status` `none` (or `refused`
  for a base that is there but does not match) and a `reason` that names it. Nothing of this repository or machine is
  in the code: a planted repository with its own `rebuild.yaml` naming its own base works the same.
- **K5 (a rebuild without its semantic store fails).** `gov rebuild` (seeded or not) exits non-zero when the
  semantic store was asked for and not recreated (the endpoint unavailable, hung, or failing part way): the error
  code `REBUILD_FAILED`, its answer naming the semantic store and the reason; never an ok answer over a partial
  store. Only `--no-embeddings` (on a planted repository only) skips the semantic store and still answers ok. Use a
  stand-in endpoint that is down, and one that fails part way through a rebuild's embed requests.
- **K3** is a measurement on this repository for the engineer's evidence file; at most one test that the file
  `docs/changes/W2-122-evidence.md` exists and names the semantic stage's seconds and the embedding requests sent,
  seeded against cold, alone and with two others. No test runs the measurement.
- **Failure line:** a seeded store that differs from a cold rebuild's, or a seed from another embedder or schema
  used, is red in your tests.

## What you write

- Only inside `tests/acceptance/W2-122/` in your worktree. No throwaway implementation is left in the tree.
- STANDARD (DEC-221): every KPI line's success and failure plus the key edge cases (a link as the base; files added,
  changed and removed between base and tree). No combinatorial expansion. Behaviour through public interfaces, never
  internals. Deterministic, no network beyond a stand-in endpoint on 127.0.0.1 that your test starts and stops.
  Never the shared embedding server.
- A `README.md` there that maps each KPI line (K1 to K5 and the failure line) to its tests, gives the expected red
  reason of each, and says how the tests exercise the code under test (above).
- Red first: run your tests to the end, never with `-x`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122-tests/src TMPDIR=/tmp/gov-os-lead-W2-122 python3 -m pytest tests/acceptance/W2-122 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`;
  they fail for the reason the README states (the base code has no `--seed`, and answers ok without its semantic
  store). Collection must succeed. Report the counts.
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact,
  reversibility, cost, recommendation, confidence).

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file; if
one is there, stop and return. Never `--no-verify`. Commit only your test paths, in one commit, with the trailers in
the final block:

    git commit -m "<subject>" --trailer "Task: DAEO-blwa" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1014, DEC-1015" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then run `git log --oneline -2` and `git status --short` and quote them.

## Return

Your commit's hash (12 digits); the test count; the KPI lines with their tests; the red reason as you saw it; the
`gov.__file__` line; every earlier test you rewrote, with its reason (none expected); the `gov retrieve` queries you
ran and any result under the implementation paths you were served; the read refusals you met; any package.

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the
start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after
them:

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
