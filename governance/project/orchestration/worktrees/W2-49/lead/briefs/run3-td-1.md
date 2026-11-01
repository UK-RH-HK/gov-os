You are a fresh independent test designer (MR-3). Ticket: DAEO-ha8z (W2-49, "Contract v4.2, lite: CAP-44.h with A7 and A10, CAP-43.b (CIT-P)"), profile STANDARD. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-49-tests` on branch `w2/W2-49-tests` (DEC-963). You never read or write the ticket's own worktree, `/home/usain/gov-os-worktrees/W2-49`. The ticket's acceptance suite exists (`tests/acceptance/W2-49/`, 129 tests from earlier rounds, written before their implementation). You **add** tests for four behaviours the owner has decided and the suite does not yet test, and you show them red where the behaviour is not yet built.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ha8z','w').write('x')"` must fail; (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.

## Standing rules (read first)

- Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-ha8z`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-49-tests` and `w2/W2-49-tests`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **Reads are open, writes closed (DEC-820, Policy 2).** You read freely, with these refusals: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy it, never type its path; never read or name the qualification oracle); **(c) the counterpart's work on this ticket: you never read this ticket's in-progress implementation.** This round's implementation is made by a product-spec worker, in parallel with you, in `/home/usain/gov-os-worktrees/W2-49`: never read anything in that worktree, by any tool, and never read branch `w2/W2-49` beyond the commit your worktree started from (`b667fdc03ece`). The owner-approved specification of this ticket (Contract v4.2 in `docs/contract/contract.yaml` and `docs/contract/CONTRACT_v4.md`, and the approved change-impact proposal `docs/changes/W2-49-CIT-P.md`; DEC-741) was finished and approved in earlier rounds: read it in your own worktree as the specification. Do not read `docs/changes/W2-49-CIT-E.md` (this round's worker adds to it). **(d)** the hidden half of any evaluation set: never read it.
- **DEC-849, read refusals until W2-58 lands:** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you meet and give the count in your return. Never read `.claude/settings.json` or `.claude/settings.local.json`, and nothing under `~/.claude/`.
- **Retrieval (DEC-963, DEC-836):** use `gov retrieve` for what you need to know before reading files at random, and only from the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read; that store holds `w2/integrate` as of its last refresh, at most about half a day old; for what changed since, read `git show w2/integrate:<path>`). Never this ticket's worktree's store. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (`docs/contract/contract.yaml`, `docs/contract/CONTRACT_v4.md`, `docs/changes/W2-49-CIT-P.md`, `docs/changes/W2-49-CIT-E.md`, `docs/contract/capabilities/**`, `docs/contract/SOURCE_MAP.csv`), and name in your return each such result you were served. Say in your return whether you used `gov retrieve`, and for what.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-49-tests/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-49-tests/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. (Your tests are later merged into `/home/usain/gov-os-worktrees/W2-49` and run there with that worktree's `src/`: they must find every path from the test file's own location, never from a fixed worktree path.)
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. This ticket's tests need no dev tier. **`docs/source/`:** never read it, list it, or `git show` anything under it.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in copies single named files only, into your own temporary folder outside the tree, never `governance/project/`. A test that needs a tree builds a temporary one from single named files. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Write files with the Write and Edit tools and literal absolute paths. Keep shell commands readable whole: no here-documents, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; put anything longer in a script file in your own temporary folder and run that. No subagents that write. **Install nothing:** a tool you need is a P1 you return. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov close`, `gov adopt`, `gov pause` or `gov rebuild --no-embeddings`. Never run `docs/plan/tools/validate_s1.py` (DEC-738).
- **Row W2-L423's rule (DEC-911):** anything you write under `.gov-runtime/` writes commit hashes as 12 digits, never the full 40, and never writes the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Your scratch budget (DEC-898):** your share is 5 GB and 250,000 files and folders, outside the tracked tree. Keep the sandbox's own temporary folder; keep pytest's own retention (never a per-run `--basetemp`); remove every temporary tree you made as soon as you no longer need it; give `du -sh` and `du -s --inodes` of your temporary folder in your `evidence`.
- **The git hooks are uninstalled until W2-08.** Before your commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-ha8z.md` (read-only): its KPI lines (success line 3 and the failure line especially), its `allowed_paths`, its sources and its notes.
- Your own suite and its README, `tests/acceptance/W2-49/` (all of it): its support module, its readers and its form.
- The approved proposal `docs/changes/W2-49-CIT-P.md`: §3, §4, §6 (the v4.2 text), §7 D, §8 (its row on `docs/contract/SOURCE_MAP.csv` names the eight rows), §13.
- Contract v4.2 as approved, in your worktree: `docs/contract/contract.yaml` and `docs/contract/CONTRACT_v4.md` (CAP-43, CAP-44 with CAP-44.f, CAP-44.h, CAP-44.k, CAP-44.l, CAP-45.a, and the `status` field).
- The capability records `docs/contract/capabilities/*.md` as they stand in your worktree (276, DERIVED from `contract.yaml` under DEC-614): their form, e.g. `CAP-45.md`, `CAP-45.b.md`, `CAP-45.a.md`.
- `docs/contract/SOURCE_MAP.csv` as it stands in your worktree (it is unchanged since before this ticket; columns `source_document,source_item,class,carried_by_or_disposition`).
- W2-51's Wave 2 plan validator, an existing public tool: `docs/plan/tools/validate_w2.py` (run it as `python3 docs/plan/tools/validate_w2.py --root <tree root>`; read its help, its output form and which files it reads), and W2-51's suite README `tests/acceptance/W2-51/README.md` (its checks `cit-p-moved-items` and `cit-p-lines-applied`).
- In `docs/DECISION_REGISTER.md`: DEC-722, DEC-741, DEC-744, DEC-745 (item 2), DEC-750 (item 5), DEC-614, DEC-841 (only to know what you must **not** test), DEC-221, DEC-462, DEC-491, DEC-732, DEC-906.

## The behaviour to test (in proportion: STANDARD, each line's success and its failure and the key edge cases; no combinatorial expansion)

1. **KPI success line 3, "the plan validator's two-way check covers the moved parts" (DEC-744).** On this ticket's tree, W2-51's validator passes its two CIT-P checks, `cit-p-moved-items` and `cit-p-lines-applied`, and their lines account for the three items moved to Wave 2, lite (CAP-43.b, CAP-44.f, CAP-44.h) and the six CIT-P lines (those three and the split's CAP-43.d, CAP-44.k, CAP-44.l). Assert on the validator's own output for those two checks, not on its overall exit (its other checks judge the whole plan and are not this ticket's).
2. **The failure line, "a Contract item moved without a CIT-P line, or a CIT-P line with no change, fails the validator".** On a temporary tree the test builds from single named files (the files the validator reads), (i) a Contract item moved to Wave 2 with no CIT-P line makes `cit-p-moved-items` fail and name that item; (ii) a CIT-P line with no change in the Contract makes `cit-p-lines-applied` fail and name that line's id. Each changes one thing against the passing tree, so the passing case and each failing case differ only by it.
3. **DEC-745 item 2, the eight source-map rows.** In `docs/contract/SOURCE_MAP.csv`, the eight rows the CIT-P's §8 names (by `source_document` and `source_item`: Adoption Protocol v3.0 "Role D", "Role F", "12. D", "15. F", "20. Final adoption verdict"; Distribution Protocol v1.2 "Stage A7", "Stage A10", "18. Adoption acceptance") follow Contract v4.2: each states that its part is Wave 2, lite, under its v4.2 item (A7 and A10: CAP-44.f; the verdict: CAP-44.h), and that the rest stays Wave 3 under its v4.2 item (A7 and A10 beyond the lite form: CAP-44.k; the verdict with the ten ADOPTED_HEALTHY conditions: CAP-44.l). Failure: any of the eight still states the moved part as W3 only. The rows for "16. G" (A11) and "Stage A9" still say W3 and do not change. **No other row differs** from the file as it was before this ticket (compare with a fixed, existing commit, for example `git show ffc60703e373:docs/contract/SOURCE_MAP.csv`, never with a branch name: the tests must stay green after this ticket merges into `w2/integrate` and at its close). Every row still has the four columns, and the eight keep their `source_document`, `source_item` and `class`. Locate rows by their content, never by line number.
4. **DEC-750 item 5, the capability records.** (i) `docs/contract/capabilities/CAP-45.a.md` is regenerated from the approved v4.2: its title, its heading and its `Item:` line are `contract.yaml`'s CAP-45.a item text (the Wave 2 wording of D (ii)), in the same form as its sibling records (compare with an unchanged sibling of the same parent, as the suite's existing record test does). Failure: the record still carries a different item text from `contract.yaml` (today it carries v4.1's, "authenticated source (signed tag)"). (ii) Every record under `docs/contract/capabilities/` has `status: ACCEPTED` in its frontmatter, as both Contract files state; failure: any record with another status (today all say PROPOSED). Read the expected status from the Contract files, so the test states the rule ("the records' status is the Contract's") and its value.

**What you must not test:** DEC-841's open question. The tests must not need the nine items of DEC-841 (CAP-04.a, CAP-04.d, CAP-22.b, CAP-22.c, CAP-30.c, CAP-30.g, CAP-32.d, CAP-37.e, CAP-53.b) to move, and must not fix their wave either way.

**Adding is not rewriting.** New tests only, in new test files or added functions; extending the support module is adding. An existing test changes only where DEC-750 item 5 contradicts it: then it is a rewrite, in the same commit, with the trailer `Rewrite-Reason: DEC-750 item 5 <what and why>` and no expectation lowered (DEC-906, DEC-491); name each in the README and in your return (expected: none). The README update (the two lines no longer pending W2-51, the new tests and their expected red reasons) is not a rewrite.

## Red first

Run the whole suite to the end, never with `-x`:
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-49-tests/src TMPDIR=<your sandbox temporary folder> python3 -m pytest tests/acceptance/W2-49 -q -p no:cacheprovider -rs`
Expected: the 129 existing tests green; behaviours 3 and 4 red for the reasons your README states (nothing of this round is built in your tree); behaviours 1 and 2 may already be green (the validator and v4.2 are both in your tree): say for each such test why it is green now and that it is green by the behaviour, not by accident. Check every new test against throwaway stand-ins outside the tree (single named files, in your own temporary folder): one that follows the decided behaviour (it must pass) and one that breaks each line (it must fail with the stated message). Quote the `gov.__file__` line above.

An ambiguous line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## What you write

Only inside `tests/acceptance/W2-49/`. No throwaway left in the tree.

## Commit

Commit only your test paths, in one commit, trailers in the final block (DEC-182, DEC-476):

    git commit -m "W2-49 (DAEO-ha8z): acceptance tests for the validator lines (DEC-744), the eight source-map rows (DEC-745) and the records (DEC-750)" --trailer "Task: DAEO-ha8z" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-744, DEC-745, DEC-750, DEC-722" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

(with a `Rewrite-Reason:` trailer only if you rewrote an existing test). After it, run `git log --oneline -2` and `git status --short` and quote them.

## Return

Your commit's hash (12 digits); the new test count and the suite's total; each behaviour above with its tests and the red or green reason as you saw it; every existing test you rewrote, with its reason (expected: none); the retrieval results you dropped under P-R1; the read refusals you met; any package.

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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

Refused twice for the same call: stop and say so; no third try.
