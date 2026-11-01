You are a fresh reviewer (the QA engineer, role `independent-auditor`). Ticket DAEO-0z8c (W2-05, "The git environment of every check, hook and helper; the settings re-sort"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-05` on branch `w2/W2-05`, at the head `e122beca7ef7`. The ticket's earlier rounds passed their reviews (probe records `docs/probes/DAEO-0z8c/PR-DAEO-0z8c.md` and `docs/probes/DAEO-0z8c/PR-DAEO-0z8c-dec970.md`, the latter at `f8e85f531cbf`). This is the **second and last review of one new round only** (DEC-971, DEC-980; DEC-413, DEC-916): a merge of the integration branch that resolved a conflict in a file the last review judged (DEC-895), the owner's decision on package H, and a test revision of another ticket's cases. You judge this round's commits, not the earlier work. You read the code, the tests and the results below; you re-run no suite (DEC-959 item 1), and run the code only to probe behaviour the tests miss. You write nothing in the repository.

## Step 0, before any work: the sandbox check (owner, DEC-789)

You were started through `gov launch`, sandboxed. Before anything else, run these and report their exact output first in your return (in `evidence`, and say in `status` whether the check passed):

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0z8c','w').write('x')"`: a write outside your worktree. It **must fail**. If it wrote the file, do not delete it: stop there and return, naming the file.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and then `git update-index --refresh`: git's own writes. They **must work**. If either fails, stop there and return with the exact error.

These two writes of step (b) are the only writes you make in the repository; they change no file and no branch.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-0z8c`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-05` and `w2/W2-05`) and `git rev-parse HEAD` (expect a full commit id beginning `e122beca7ef7`; give it in full in your return: it is the probe record's `probed_commit`). If anything differs, stop and say so. Inside the sandbox `git status` shows placeholder device files at the worktree root (`.bashrc`, `.gitconfig`, `.mcp.json` and the like, character devices `1, 3`): they are not real; conclude nothing from them.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. **This rule goes into every worker brief you write, word for word.** Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **What you may read.** Everything: the code, the tests, the history (DEC-820: reviewers read everything), except (a) secrets and keys, never printed; (b) the contents of the held-out material (never read, print, search, diff or copy it, never type its path, DEC-525); (d) the hidden half of any evaluation set. Never read or name the qualification oracle. Never read `.claude/settings.json` or `.claude/settings.local.json`, anywhere, and nothing under `~/.claude/`. Run no glob, search or listing over `governance/project/`: name the files you need there one by one (DEC-508).
- **Memory first (DEC-836, DEC-859, DEC-860).** Use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src timeout 300 python3 -m gov.cli.main retrieve "<question>" --json`. A large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget, never one giant query or context. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. This worktree's store is being rebuilt beside you (it dates from before this round's merges), so an answer may be stale or unavailable: then read the named files. Say in your return which questions you asked.
- **Read refusals (DEC-849).** Until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal; never look for another form; search named folders instead. Count the refusals you met.
- **The guard has five rules now (ACT 1, DEC-953 item 2, DEC-954):** the implementer never writes acceptance tests; reviewers and auditors write only their own records; no reads of the hidden half of an evaluation set or of the held-out material; no reads of secrets; no installs without the owner. The tool's own command checker refuses here-documents, `$TMPDIR` in compound commands and `rm`: put a long probe in a script file under your temporary folder and run it. Report every refusal you meet (time, the command's form in one line, the reason it gave).
- Run everything in the foreground, one command after another. A foreground command is killed after 10 minutes: keep each probe within that. You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no commit, no amend, no rebase, no merge, no push, no tag in this worktree.
- Write no file of the repository. Your probes run in your temporary folder (the one `gov launch`'s sandbox set; do not set `TMPDIR`), and every temporary repository you need is built there from scratch with `git init`.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in imports the package (with the `PYTHONPATH` above) or copies single named files, never `governance/project/`. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- **The git hooks stay uninstalled until W2-08.** Never run `lefthook install` or `lefthook uninstall` in this repository or any of its worktrees.
- Never run `gov close`, `gov adopt`, `gov pause`, `gov rebuild` or `gov checkpoint` against this worktree or the main tree. Install nothing (an install you need is a P1 escalation in your return). No subagents.
- **Disk (DEC-898).** Your share of the ticket's budget is 3 GB and 150,000 files and folders outside the tracked tree. Measure `du -sh` and `du -s --inodes` of your temporary folder at the end and give the figures in `evidence`.
- **Row W2-L423's rule (DEC-911).** In anything you write, give commit hashes as 12 digits (the probed head in full only where asked), and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.
- Nobody asks or notifies the owner. On an authentication or access error (401, 403, "Failed to authenticate"), stop and return with status `AUTH_REQUIRED`.
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. **Refused twice for the same call: stop and say so; no third try** (AR-6).


## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.


## What you read

- The ticket file `.tickets/DAEO-0z8c.md` (read-only): its KPI lines and its `allowed_paths`.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-971 (item 3), DEC-980 (items 2 and 3), DEC-805, DEC-953 (item 2, ACT 1), DEC-802 (P-B1-2), DEC-895, DEC-491, DEC-866, DEC-710; ADR-0001.
- The last review's record, `docs/probes/DAEO-0z8c/PR-DAEO-0z8c-dec970.md`.
- **This round's change** (`git log --first-parent b28866ba3b22..e122beca7ef7`):
  - **`d1533bf30a10`, the lead's merge of `w2/integrate`** (`f7f4fb5e`; W2-95's rewrite of the path-map check, W2-107's secrets cache, W2-108's freshness work in the lexical index). One conflict, in `src/gov/check/pathmap.py`: the lead kept W2-95's code (its version 1.1.0, its utf-8/surrogateescape listing, its findings for a missing or unreadable path map and an unlistable repository) and put back this ticket's git environment on its one git call (`env=git_env(root, pinned=True)`). `src/gov/retrieval/lexical.py` merged without a conflict: W2-108's new git calls (`rev-parse HEAD --git-path index`, `ls-files -z`, in its freshness key) go through `_git`, which carries this ticket's `git_env(root)`. See `git diff b28866ba3b22 d1533bf30a10 -- src/gov/check/pathmap.py src/gov/retrieval/lexical.py` and `git show d1533bf30a10 -- src/gov/check/pathmap.py` (the combined diff).
  - **Test designer `aedc72140fcb`** (merged as `4e225e7c63da`): fourteen new cases in `tests/acceptance/W2-05/test_w2_05_hooks_source.py` for DEC-971 item 3; and W2-72's four fail-closed cases in `tests/acceptance/W2-72/test_w2_72_merge_tree_that_cannot_run.py` and `w2_72_support.py` moved off a `git` first on `PATH` (which containment no longer runs, P-B1-2) onto a missing blob for exit 128 and the helper's in-process git folder list (`gov.util.gitenv.GIT_DIRS`) for exit 129, `Rewrite-Reason: DEC-802 (P-B1-2)`; READMEs.
  - **Engineer `1d9c0dca01b2`:** `LIFTED_HOOK_EVENTS` in `src/gov/adapters/portability.py` and a one-line skip in `_hooks_findings`; builder tests `tests/unit/gitenv/test_hooks_lifted.py`.
  - The lead's checkpoint record `110125ddda0b` (the first review's head).
  - **The fix after the first review:** engineer `a5b728d2f8a7`: the lexical index's `_git` now runs `git_env(root, pinned=True)` (all four of its calls: `ls-files -z` and `hash-object --stdin-paths` in `_tracked`, W2-108's `rev-parse HEAD --git-path index` and `ls-files -z` in `_tree`); builder tests `tests/unit/gitenv/test_lexical_pinned.py`; sweep row 24.
  - The lead's checkpoint record `e122beca7ef7`.

## The first review of this round (review 1 of 2; this is the second and last, DEC-413, DEC-916)

The first review (at `110125ddda0b`) judged **pass**, with two rows: R6-1 (a lifted hook event given a value that is not a list in the repository's source is no finding; Ordinary work: no; Consequence: fails open, the drift report only, while the exception lasts) and R6-2 (the lexical index's git calls were unpinned, so a person's global `trace2.eventTarget` got events; Ordinary work: yes; Consequence: other). Everything else it probed it found sound: the merge resolution kept both sides; the path-map check and the lexical index ignore every inherited `GIT_*` variable and the person's configuration for what they list and judge; DEC-971 item 3 holds exactly; W2-72's four cases keep every expectation and reach the failing merge-tree. Do not re-probe what it found sound unless the fix touches it.

**Why there was a fix after a pass:** the lead's scoped run then found this ticket's own acceptance case `tests/acceptance/W2-05/test_w2_05_planted.py::test_gov_close_runs_its_subprocesses_and_the_ticket_tests_with_a_sanitised_environment` red, in the run and alone: a person's `[trace2] eventTarget` in `~/.gitconfig` was written during `gov close` by three git processes, all the lexical index's (`rev-parse HEAD --git-path index` twice, `ls-files -z` once), which came with W2-108's freshness key in the merge. That is R6-2 breaking the KPI of row W2-M161; the case was green in the last round, before the merge.

## Results so far (judge from these; do not re-run the suites)

- Test designer, sandboxed, at `d1533bf30a10` (before the engineer's change): W2-72 whole 73 passed (the four revised green; before the revision they were red on this branch and green on the integration branch); the hooks-source file 24 cases, red only the over-this-repository case and the three point-1 cases (each a `HOOKS_EVENT_DIFFERS` finding for a lifted event), as its README states. Mutation checks: with the exception made to do nothing, points 2 to 4 went red; with the case's own git withheld, W2-72's four went red on an empty log.
- Engineer, sandboxed, at `1d9c0dca01b2`: `tests/unit/gitenv` and `tests/unit/adapters` 147 passed; the hooks-source acceptance file 24 passed; `python3 -m gov.adapters.portability` over this worktree: exit 0, no finding.
- The lead's first scoped run at `110125ddda0b` (outside the sandbox, the close's environment): unit 3083 passed, 1 skipped; W2 acceptance part 3942 passed, 8 failed (the W2-05 planted `gov close` case above, ours; W2-59 ×4 and W1-46 `npm-install`, known and W2-90b's; W2-66's DEC-919 case naming `tests/acceptance/W2-05/conftest.py`; W2-05's code-index case waiting out its 300 s behind other sessions' rebuild lock; W2-50's gov-check scale case, red on the integration branch's code too); W1 part 10624 passed. `gov check`: 21 green (adapter-portability among them), yellow core-decision-citations and openspec-validate.
- The fix, engineer, sandboxed, at `a5b728d2f8a7`: the new unit tests red before (both the `~/.gitconfig` event target and the XDG perf target written) and green after; `tests/unit/gitenv` and `tests/unit/retrieval` 153 passed, 1 skipped; the planted `gov close` case green; `test_w2_05_planted.py` 20 passed, 2 red only in the sandbox (the retrieval check's two cases, red there with or without the fix: no embedder); `tests/acceptance/W2-108/` 26 passed, 1 skipped. Its judgement on `hash-object`: pinned too; for an ordinary project the blob ids are unchanged; only a person with a global `core.autocrlf = true` and a CRLF file sees that file's id follow the file as it stands, so it shows stale once and is re-indexed; the ids are used only inside the index.
- The lead's second scoped run, on the final code, is running beside you; you will not see it.
- **Known, not new:** P-W2-05-R3-1 (an entry criterion of W2-08, DEC-971 item 3); `gov release` (sweep row 66, waits for W2-16's close, DEC-777); the Wave 3 rows R4-2 to R5-4 and N-1.

## What you probe

**Above all, the fix (`a5b728d2f8a7`):** under `gov close`, `gov check`, `gov retrieve` and `gov rebuild` on a throwaway project, a person's trace settings (`trace2.eventTarget`, `trace2.perfTarget`, `trace2.normalTarget` in `~/.gitconfig`, the XDG file, and the system file) are never written by the lexical index's calls; the freshness key, the listing, the blob ids and the store's digest are those of an unpinned run for an ordinary project; an inherited `GIT_INDEX_FILE` of the root's own git directory is still used; the repository's own `.gitattributes`, `.git/info/attributes` and `.git/config` (filters, `core.autocrlf`, `eol`) still shape `hash-object`'s ids; the engineer's `core.autocrlf` case loses no work (a store built before the fix, then refreshed after it: the file re-indexed, nothing dropped, no answer lost); and whether any other git call that W2-108's or W2-107's merged code makes (the secrets cache, the semantic index) still reads the person's configuration where a trace setting there could write during these commands.

Then, only where the fix could touch it, the points below (the first review found them sound):

- **The merge resolution (DEC-895):** `pathmap.py`'s git call gets this ticket's pinned environment and W2-95's behaviour is intact: an inherited `GIT_DIR`, `GIT_INDEX_FILE` (one not in the root's git directory) or `GIT_WORK_TREE`, or a person's global or system configuration (for example `core.quotePath`, an alias, a trace setting), changes neither what the check lists nor its verdict; a non-UTF-8 or quoted path is still listed as W2-95 meant; a repository git cannot list is still a finding, never green. `lexical.py`: W2-108's freshness key and listing still work under `git_env(root)` in the main tree and in a linked worktree (the `--git-path index` answer with and without an inherited `GIT_INDEX_FILE`), and an inherited `GIT_DIR` reaches none of its git calls. Nothing else of either side of the merge was dropped (compare with `git diff f7f4fb5e d1533bf30a10 -- src/` and `git diff b28866ba3b22 d1533bf30a10 -- src/`).
- **H's exception (DEC-971 item 3):** exactly the two events, named in the comparison, only where the template alone has them; every other one-sided event still a finding in either direction, also beside the lifted ones; a lifted event only in the repository's source still a finding; once back in both sources compared as any other (it ends by itself); output form unchanged; an adopted project (whose kernel is not the template's) unaffected. Whether anything else that reads the two hooks sources (another check, `gov doctor`, a generator) needs the same exception or now disagrees with this check.
- **W2-72's revised cases (DEC-980 item 2):** nothing lowered and no case removed (compare with `git show 4e225e7c63da^1:tests/acceptance/W2-72/…`); each case still reaches the failing merge-tree it claims (not a different failure); the `sitecustomize` seam in the hook process cannot leak into another test or the person's environment; the seam would show red, not green, if containment went back to a `PATH` git or stopped failing closed.

And, as before, behaviour the tests miss that could lose work or make the guard or a gate fail open in this round's change. Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

Before you return, run `git status --short` and `git log --oneline -1` and quote them: the status must show nothing but the sandbox's placeholder files, and the head `e122beca7ef7`.

## Return

The head you probed (in full); your judgement, `pass` or `fail` by the rules above (fail only for a finding with "Ordinary work: yes" and "Consequence: fails open" or "loses work"); and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and its two lines. Say also what you probed and found sound, and give the probe record's content (front matter fields `judgement` and `probed_commit`, the method, the findings) in your return: the lead writes the record from it. You repair nothing (MR-4).

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

Put the sandbox check's result (a) and (b) first in `evidence`, and your judgement (`judgement: pass` or `judgement: fail`) and your findings in `work_completed` and `discoveries`. After the twelve fields, a section `guard_refusals:` (one line per refusal, or `none`) and the count of read refusals.

Refused twice for the same call: stop and say so.
