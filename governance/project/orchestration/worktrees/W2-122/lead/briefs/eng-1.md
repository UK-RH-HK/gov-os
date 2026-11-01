# Brief: engineer, DAEO-blwa (W2-122), STANDARD — batch 1

You are a fresh engineer. Ticket: DAEO-blwa (W2-122), profile STANDARD. You work only in the worktree
`/home/usain/gov-os-worktrees/W2-122` on branch `w2/W2-122`. You build the ticket's code to fulfil its specification
and KPI lines, never to make tests pass (DEC-957).

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-blwa`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-122` and `w2/W2-122`).
  If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing
  started in the background is ever read. A command that could outlive the Bash tool's ten minutes is not run. Return
  only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for
  verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122/src` set **per
  command** (never in a session's `--settings` env). Your verification shows it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122/src python3 -c "import gov; print(gov.__file__)"`, quoted in your
  return; it must point into this worktree.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random. This
  worktree has no store yet (its rebuild waits for a heavy-job slot; the lead runs it after your batch), and its code
  is the integration branch's, so ask the integration store:
  `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read; never write there). Its
  answers under `tests/acceptance/W2-122/` (none expected) are dropped unread (DEC-820 (c)). **Never
  one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then
  `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph
  tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole
  graph.
- **Policy 2 (DEC-820):** reads are open, with four refusals: (a) secrets and keys, never printed; (b) the contents of
  the held-out qualification material (its file names may be seen); never read or name the qualification oracle;
  (c) the counterpart's work on this ticket: you never read `tests/acceptance/W2-122/` by any tool, in this worktree,
  in `/home/usain/gov-os-worktrees/W2-122-tests` or in git history (you may run those tests and see their names,
  results and failure messages, through `gov accept` only); (d) the hidden half of any evaluation set, by whoever is
  measured by it. Writes stay inside your paths.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the
  repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named
  folders instead, and count the refusals in your return. Never read `.claude/settings.json`.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target, no here-document, no
  backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; anything longer goes in a script file under
  `/home/usain/gov-os-worktrees/W2-122/.gov-runtime/scratch/eng/` written with the Write tool, then run. A refused
  form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of
  this repository); copy single named files only, never `governance/project/`. Tests that need a repository build a
  temporary one from scratch under pytest's `tmp_path`. No clone, copy or programme file under any `.gov-runtime/`
  folder (DEC-673). Never write in `~/gov-os-workbench`. Inside a session `.gov-runtime/freeze` may show as a
  placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, write commit hashes as 12 digits, never the full 40, and
  never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Your budget (DEC-898):** 10 GB and 500,000 files and folders outside the tracked tree. Set
  `TMPDIR=/tmp/gov-os-lead-W2-122` on every test run. Keep pytest's own temp retention; never `--basetemp`. Clean what
  you make as soon as it is no longer needed. Measure (`du -sh` and `du -s --inodes` of `.gov-runtime/scratch/eng/`
  and your temp use) at the start and the end; give the figures in `evidence`.
- **Heavy steps (DEC-979 D1, DEC-1008):** one test or one test file is not heavy. More than one test file runs as
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh <the pytest command>`.
  **You run no rebuild of this worktree or of any real tree:** the lead runs those, and the lead measures KPI 3 in its
  own session on the shared embedding server. Never run `gov rebuild --no-embeddings` on a real tree (DEC-719); on a
  temporary planted repository in a test it is allowed. Never send requests to the shared embedding server
  (127.0.0.1:11434) from your tests: a test stands up its own stand-in endpoint on another port (existing tests show
  how).
- Install nothing: an install is a P1 package in your return. No push, merge, rebase or tag. Never write
  `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never touch `tests/acceptance/**`. No subagents that write. Never
  ask or notify the owner; never `owner-ping`.
- On an authentication or access error, stop and return `AUTH_REQUIRED`. On ESCALATION_BLOCKED from any command, stop
  and return it.

## What you read

- The ticket file `.tickets/DAEO-blwa.md` (read-only): its KPI lines and its `allowed_paths`.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-1014 (items 4 and 6), DEC-1015 (item 4), DEC-1011, DEC-1001,
  DEC-982, DEC-996 item 3, DEC-719, DEC-530, DEC-374, DEC-694, DEC-966, DEC-897, DEC-135.
- W2-116's ticket `.tickets/DAEO-f58b.md` (its fourth KPI line: the warm base `gov rebuild --seed` reads).
- The code the ticket touches: `src/gov/rebuild/command.py`, `src/gov/rebuild/watch.py` (the rebuild lock, the
  stage watch, the settings file `governance/project/rebuild.yaml`), the stores' layout under `.gov-runtime/`
  (`store.db*`, `codeintel/`, `query-vector-cache.db*`), the secrets record (`src/gov/secrets/cache.py`, W2-107), how
  the semantic stage decides what to embed and how it records its embedder (`src/gov/retrieval/semantic.py`, its
  manifest), the lexical refresh, the code-graph index (`src/gov/codeintel/`), the record store's fingerprints row
  (`src/gov/store/loader.py`, `src/gov/close/fingerprint.py`), and how `gov` commands register their arguments and
  exit codes (`src/gov/cli/`).

## What to build

The ticket's KPI lines, as they stand in its file. The lead fixes this outside so that you and the independent test
designer, who works in parallel and never sees your code, build to the same interface (a lead's reading, logged for
the CTO; if any of it cannot be built as stated, return a package rather than build something else):

- **K1 (seeded equals cold).** `gov rebuild --seed <folder>`: `<folder>` is the root of a warm base tree (the folder
  that holds its `.gov-runtime/`, as the integration store `~/gov-os-worktrees/W2-00-store` does; a link is followed,
  resolved once). The rebuild copies the base's stores (the lexical, semantic and code-graph stores, and the secrets
  record's entries) into the tree, under the tree's rebuild lock, before the stages run, then rebuilds
  incrementally: only the files whose content differs from the base's are re-embedded. The result is the same store,
  entry for entry, as a cold rebuild of the same tree: the rebuild digests equal and every chunk's vector equal.
  Copy SQLite stores consistently (a base may be read while it is used: copy through SQLite's own backup, not a file
  copy that can miss a write-ahead log), and copy what the code-graph tool keeps for the tree in the form it reads it
  (where its home path is per tree, the copy is re-homed, never shared with the base). The base is only read, never
  written.
- **The answer.** A rebuild given `--seed` answers, in its `--json` result, a `seed` object with `status` one of
  `seeded`, `refused` or `none`, the `base` it read (or none), and a `reason` that names why where it is not
  `seeded`. Without `--seed`, `gov rebuild` does not seed (today's behaviour, unchanged).
- **The base's record.** Every full rebuild writes `.gov-runtime/rebuild/stores.json` in its tree: a JSON object with
  at least `code` (the fingerprint of the Gov OS code that built the stores), `embedder` (an object with `model` and
  `revision`, as the semantic stage records them) and `schema` (the stores' schema version), written only after the
  stores are complete. The seed compares the base's record with the tree's own build: the running code's
  fingerprint, the embedder the endpoint reports now, the running code's schema version. **"Code fingerprint" means
  the Gov OS program that turns files into store entries, not the repository's content** (the content differing is
  exactly what seeding is for). The simplest fail-closed choice is a digest of the running `gov` package's own
  source files; a narrower one is allowed only where you show that every module that shapes a store entry is in it.
  Say which you chose, and why, in your return.
- **K2 (fail closed).** A base whose `code`, `embedder` (model or revision) or `schema` differs from the tree's, or a
  base with no readable record, is refused: `seed.status` `refused`, its `reason` names what differed (the words
  `code fingerprint`, `embedder model` or `schema`, or that the base has no record), nothing of the base is left in
  the tree, and the rebuild runs cold. Never a store that mixes two embedders. The rebuild itself succeeds.
- **K4 (configured base, any adopted repository).** `gov rebuild --seed` with no folder reads the warm base from the
  project's configuration: the key `integration_store` in `governance/project/rebuild.yaml` (the settings file
  `watch.py` already reads), an absolute path. A project with no such key, or one whose path holds no base, rebuilds
  cold with `seed.status` `none` (or `refused` for a base that is there but does not match) and a `reason` that
  names it. Nothing of this repository or this machine is in the code (DEC-1014 item 6, DEC-982).
- **K5 (DEC-1015 item 4, stricter-only).** `gov rebuild` (seeded or not) exits non-zero when the semantic store was
  asked for and not recreated (the endpoint unavailable, hung, or failing part way): a `GovError` with the code
  `REBUILD_FAILED`, its details naming the semantic store (`"store": "semantic"`) and the reason; never an ok answer
  over a partial store. Only `--no-embeddings` skips the semantic store and still answers ok. Check whether any
  existing test or caller relies on today's ok answer with `stores.semantic` `not_recreated` (for example a
  project whose path map embeds nothing, DEC-694): name each one in your return, and do not bend it silently
  (DEC-866).
- **K3** is measured by the lead. You do not write `docs/changes/W2-122-evidence.md` in this batch; a later batch
  writes it from the lead's figures.
- **Failure line:** a seeded store that differs from a cold rebuild's, or a seed from another embedder or schema
  used, never happens.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/rebuild/seed.py`, `src/gov/rebuild/command.py`,
  `tests/unit/rebuild/test_w2_122*`. If the work needs another path (the command list, another module), return a
  package naming it; never write outside.
- Your own unit tests (test-driven) in `tests/unit/rebuild/test_w2_122*.py`, as regression evidence only, on small
  temporary repositories with a stand-in endpoint.
- Proportion (DEC-135): no code for edge cases beyond the KPI lines. Never make a gate decision fail open: every
  failure KPI must still refuse. About 150 lines are estimated.
- Run your unit tests and the existing rebuild unit tests (`tests/unit/rebuild/`) to their end, never with `-x`:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122/src TMPDIR=/tmp/gov-os-lead-W2-122 bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh python3 -m pytest tests/unit/rebuild -q -p no:cacheprovider -o tmp_path_retention_policy=failed`.

## Commit, then the acceptance tests

1. Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file;
   if one is there, stop and return. Never `--no-verify`. Commit only your paths, with the trailers in the final
   block:

       git commit -m "<subject>" --trailer "Task: DAEO-blwa" --trailer "Role: engineer" --trailer "Implements: DEC-1014, DEC-1015" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

   Then run `git log --oneline -2` and `git status --short` and quote them.
2. **The acceptance tests arrive while you work (DEC-963):** the lead merges them into this worktree between your
   batches. Only if `/home/usain/gov-os-worktrees/W2-122/.gov-runtime/scratch/lead/TESTS-READY` exists when your
   commit is made, run them once, reading results only, through
   `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122/src TMPDIR=/tmp/gov-os-lead-W2-122 python3 -m gov.cli.main accept DAEO-blwa --json`
   only (never `pytest` on `tests/acceptance/`), and report pass or fail per KPI line and the counts. If it does not
   exist, say so and return; the lead starts the next batch.

## Return

Your commit's hash (12 digits); the files changed; the lines added and removed; the code fingerprint you chose and
why; the tests you ran with their results; the `gov accept` result if run; each existing test or caller that relied
on an ok answer without the semantic store; the `gov retrieve` queries you ran; the read refusals you met; anything
you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost,
recommendation, confidence).

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
