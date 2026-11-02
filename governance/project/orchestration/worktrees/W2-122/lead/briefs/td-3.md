# Brief: independent test designer, DAEO-blwa (W2-122), STANDARD — run 2: retire KPI 5's cases (DEC-1027 C)

You are a fresh independent test designer (MR-3). Ticket: DAEO-blwa (W2-122), profile STANDARD. You work only in the
worktree `/home/usain/gov-os-worktrees/W2-122-tests` on branch `w2/W2-122-tests` (DEC-963). You never read or write
the ticket's own worktree, `/home/usain/gov-os-worktrees/W2-122`.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-blwa','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (do not delete anything).

## Standing rules

Read `/home/usain/gov-os-worktrees/W2-122-tests/.gov-runtime/scratch/lead/briefs/td-1.md` if it exists there; if not,
the rules are these, word for word where quoted:

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-blwa`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-122-tests` and
  `w2/W2-122-tests`). If anything differs, stop and say so.
- Run everything in the foreground. No `git checkout` of another commit, no reset, no clean, no amend, no rebase.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for
  verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122-tests/src` set
  **per command** (never in a session's `--settings` env). Your verification shows it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122-tests/src python3 -c "import gov; print(gov.__file__)"`, quoted in
  your return; it must point into this worktree.
- **Retrieval (DEC-963, DEC-836):** use `gov retrieve` for what you need to know before reading files at random, only
  from the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`.
  **Never one giant query (DEC-860):** batches (`--batch-size`, then `--continue <token>`). **A code question
  (DEC-859)** uses the code graph's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted.
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (`src/gov/rebuild/seed.py`,
  `src/gov/rebuild/command.py`, `tests/unit/rebuild/test_w2_122*`, `docs/changes/W2-122-evidence.md`) and name in your
  return each such result you were served.
- **Policy 2 (DEC-820):** reads are open, with four refusals: (a) secrets and keys, never printed; (b) the contents of
  the held-out qualification material (its file names may be seen); never read or name the qualification oracle;
  (c) the counterpart's work on this ticket: you never read this ticket's implementation (the files above, as they
  stand on the ticket's branches) and never anything in `/home/usain/gov-os-worktrees/W2-122`; (d) the hidden half of
  any evaluation set, by whoever is measured by it. Writes stay inside `tests/acceptance/W2-122/`.
- **Read refusals (DEC-849):** the guard still refuses some reads (searches from the repository root,
  `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead,
  and count the refusals in your return.
- **Command forms (DEC-941 item 4a):** no shell variable as a write target, no here-document, no backticks, no
  `bash -c '…'`, no long inline `python3 -c` with braces; anything longer goes in a script file under
  `/home/usain/gov-os-worktrees/W2-122-tests/.gov-runtime/scratch/td/` written with the Write tool, then run.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Never copy the repository or a folder of it; no clone or programme file under `.gov-runtime/`. Never write in
  `~/gov-os-workbench`. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, commit hashes as 12 digits, never 40, and never the
  keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Budget (DEC-898):** 1 GB and 50,000 files and folders outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-122`
  on every run; pytest's own retention, never `--basetemp`; measure (`du -sh`, `du -s --inodes` of your scratch) at the
  end and give the figures in `evidence`.
- One test file is not heavy. Never run a rebuild of a real worktree. Install nothing, no push/merge/rebase/tag, no
  writing subagents; never ask or notify the owner. On an authentication error return `AUTH_REQUIRED`; on
  ESCALATION_BLOCKED, stop and return it.

## The decision you apply

DEC-1027 C (owner, 2026-11-02): the ticket's KPI 5 ("`gov rebuild` exits non-zero, named, when the semantic store was
asked for and not recreated ...") moved to its own ticket, W2-124 (`DAEO-mb2t`), with the owner's rule that adoption
never fails for a missing embedder. The ticket file `.tickets/DAEO-blwa.md` no longer holds it (read it: its `success`
lines are now four, then one `failure` line). The seeding itself is unchanged.

## Do only this

1. Retire the four KPI 5 cases in `tests/acceptance/W2-122/test_w2_122_semantic_required.py`:
   `test_a_rebuild_with_the_endpoint_down_fails_named`, `test_a_rebuild_whose_endpoint_fails_part_way_fails_named`,
   `test_a_seeded_rebuild_with_the_endpoint_down_fails_named`,
   `test_without_embeddings_the_semantic_store_is_skipped_and_the_answer_is_ok` (remove the file if nothing else is
   in it; leave any helper in `w2_122_support.py` or `conftest.py` that other tests still use, and remove only what
   these four alone used).
2. In `tests/acceptance/W2-122/README.md`: remove the K5 map row, the K5 lines of the expected-red table and the K5
   behaviour paragraph; renumber the map's KPI cells so they match the ticket file's numbering now (`gov accept`
   reads them: `success-1` .. `success-4` / `K1` .. `K4` and `failure-1` / `F1`, numbered as the ticket file's
   `kpis` block numbers them; check the old numbering against the new lines one by one). Change no other test and
   lower no other expectation.
3. Check: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122-tests/src TMPDIR=/tmp/gov-os-lead-W2-122 python3 -m gov.cli.main accept DAEO-blwa --json`
   in your worktree. On this base code the tests run red, as they did; what matters is that the map is read and that
   every KPI line of the ticket file (four success, one failure) appears in its `lines`, and no K5 case is listed. If
   it would outlive ten minutes, check the map with a small script file under `.gov-runtime/scratch/td/` that calls
   `gov.accept.runner.parse_map` on the README, and say which check you ran. Also
   `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122-tests/src python3 -m pytest tests/acceptance/W2-122 --collect-only -q -p no:cacheprovider`
   must collect with no error (quote the last line).
4. Commit only those files, trailers in the final block:

       git commit -m "W2-122 acceptance: KPI 5's cases retired, moved to W2-124 (DEC-1027 C)" --trailer "Task: DAEO-blwa" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1027, DEC-1014" --trailer "Rewrite-Reason: DEC-1027 C" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

   Then quote `git log --oneline -2` and `git status --short`.

## Return

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

Also say: the sandbox check's result; whether you used `gov retrieve` and any P-R1 result served; the read refusals
met. Refused twice for the same call: stop and say so.
