**Under the five-rule guard (ACT 1, `6c36c7b5`; DEC-953 item 2, DEC-954, DEC-957):** the Gov OS's features are lifted as gates on this repository's development; your ticket closes on the audit's 10 practices. Where the common brief names a lifted rule, its DEC-953 block holds. Installs: you are refused by the guard; raise any install as a P1 in your return.

You are the ticket lead for ticket `DAEO-8lmb` (`W2-90`, "The 235 live-wiring tests judge the kernel's wiring"), profile LITE, a test-revision ticket under the owner's named decision (DEC-906, given in DEC-957: ACT 1 option (a)). You work only in the worktree `/home/usain/gov-os-worktrees/W2-90` on branch `w2/W2-90`. It is the first lead after ACT 1 and gates the closes' move off the pre-ACT head, so keep it tight.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `92153da18a69`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-8lmb.md`);
- DEC-957 (the ACT 1 part), DEC-953 item 2, DEC-954, DEC-906 in `docs/DECISION_REGISTER.md`;
- `governance/project/orchestration/packages/ACT-1-GUARD.md`, whole: what ACT 1 changed (the pre-tool hook now runs `.claude/hooks/pretooluse.py`, the five-rule hook; PostToolUse and PostToolUseFailure removed; permissions and deny rules unchanged) and how the 235 were measured;
- the 235 case ids, one per line: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/W2-90-cases.txt` (the measurement: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/act1-confirmed.json`; the scripts `tools/act1_tests.py`, `tools/act1_confirm.py` beside it);
- `git show 6c36c7b5 --stat` and its diff of `.claude/settings.json` and `.rulesync/hooks.jsonc`;
- the kernel's wiring as the product ships it: `template/` (its rulesync sources and the settings it generates), `template/governance/kernel/hooks/`, `src/gov/guard/`, and how existing suites already generate a repository from the template (search `tests/acceptance/` for `copier copy`).

## Why you start now

- ACT 1 switched this repository's own guard to the five-rule hook. The kernel's full guard and its containment hooks stay in the product, built and tested; only this repository stopped running them.
- 235 cases in 19 files asserted the old live wiring of *this repository*. They are red after ACT 1 and green on the base. Until they are revised, every close tests on the pre-ACT head (`aafd45c1`) and the nightly carries 235 known reds.

## The decisions for this run

- **One worker: a fresh independent test designer** (brief A1, `--effort high`, its brief must not set `TMPDIR`). This ticket has no engineer and no code change. You do not edit the tests yourself.
- **What the test designer does, case by case:** each of the 235 asserts the same behaviour, with the same expected verdict, of the kernel's wiring instead of this repository's live settings:
  - where a case read `.claude/settings.json` or `.rulesync/hooks.jsonc` of this repository, it reads the settings the kernel's template generates, or those of a repository generated from the template in a temporary folder (as other suites already do);
  - where a case ran the live pre-tool hook line, it runs the hook line those generated settings register;
  - shared fixtures may move into the two conftests the ticket names; a helper needed in any other file is a package.
- **Lowering nothing (MR-3, DEC-906):** no case deleted, skipped, xfailed or weakened; a case that truly cannot be moved is named in the README with its reason and returned as a package, not dropped.
- **The README** `tests/acceptance/W2-90/README.md` maps each of the 235 ids to its revised case (one table), and says what each file now reads.
- **Commits:** the test designer commits under `Role: independent-test-designer`, `Task: DAEO-8lmb`, with the trailer `Rewrite-Reason: DEC-953 item 2` on every commit that changes an earlier ticket's test.
- **Verification (scoped, DEC-954 / P-W2-64-1 (a)):** you run the 19 revised files, and nothing wider:
  1. in this worktree (the head after ACT 1): all 19 files green;
  2. on a clean clone of `aafd45c1` (before ACT 1) with the 19 revised files copied in, under `/tmp/gov-os-lead-W2-90/`: all 19 green, so the revision judges the product, not the switch;
  3. each run under the verify lock (`tools/verify_lock.sh`, the common brief), `PYTHONPATH` set to that tree's `src/`.
  The case count before and after is the same (235 collected among the 19 files' cases, by id or by the README's map).
- **Paths:** the 19 files, `tests/acceptance/W1-05/conftest.py`, `tests/acceptance/W1-46/conftest.py`, `tests/acceptance/W2-90/**`. Nothing else.
- **Budget:** about 2 to 3 hours. Scratch budget: 20 GB and 1,000,000 files and folders for you and your worker, outside the tracked tree.

Return DONE with the commits, both scoped runs' counts, and the README's path; or PACKAGES for any case that cannot be moved.
