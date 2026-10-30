You are the ticket lead for ticket `DAEO-arrl` (`W2-55`, "Decisions tagged by domain, status and scope; superseded and done entries left out of what agents see"), profile STANDARD, keystone 4, working only in the worktree `/home/usain/gov-os-worktrees/W2-55` on branch `w2/W2-55`.

**This is run 1, round 1 of two declared rounds (below).** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-arrl.md`) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-55"); W2-03's card ("#### W2-03"), whose decision records you build on;
- DEC-791 (item 1), DEC-825 (items 2 and 4), DEC-866, DEC-851, DEC-786, DEC-833 (item 3), DEC-941 (item 1), DEC-942 (item 1), DEC-946 (item 3) and DEC-951 (item 5);
- the sweep `governance/project/orchestration/packages/SWEEP-2026-10-20.md`: W1-49's two window cases and W2-59's three earlier cases, your check's first fixture;
- lens B's report `docs/assessment/2026-10/B-memory-retrieval.md`: finding F4 and question Q05 (a superseded decision served unmarked);
- W2-61's baseline record, on its branch: `git -C /home/usain/gov-os-worktrees/W2-61 show a9a25960:docs/research/W2-61-baseline.md`, sections 4 to 6 and 8;
- what W2-03 left in your base (merged in `a8eaf26e`):
  - `src/gov/store/loader.py`: `register_entries` and `_read_register`. Each `### DEC-n` entry is a record with its own span and hash, and its status is the word after `**Status:**`;
  - `src/gov/decisions/checker.py`, and where it runs: `src/gov/check/authority.py`, which calls it inside `core-authority`, a hard-block check;
- `src/gov/retrieve/command.py` (the `gov retrieve` command, 28 lines) and the not-current filter in `src/gov/retrieval/retrieve.py` (lines 40 to 60 and 180 to 200). That filter maps a path to one id, so it cannot act on one entry of the register (lens B F4);
- `src/gov/context/__init__.py`, read-only in this round;
- `template/governance/kernel/schemas/register-entry.schema.json`.

## Why you start now

- **Memory is the critical path to EXAMIN's copy** (DEC-941 item 1, DEC-946 item 3). W2-61's baseline of the visible half on 2026-10-29, repeatable, is:
  - hit@5: 8 of 20 (40 %), against CAP-10's floor of 85 (lens B had 65 %);
  - full evidence: 12 of 20 (60 %), against the owner's target of 99 %;
  - in the bundle: 14 of 20.
- **Agents are served decisions that no longer stand.** The register holds 947 entries. Twelve whole entries are SUPERSEDED or DONE, and many more are changed in part. `gov retrieve` serves them as if in force (lens B F4, Q05). Nothing says which rules are kernel-wide, or where a rule lands (DEC-825 item 2).
- **Stacked on W2-03 (DEC-786).** W2-03 is merged into `w2/integrate` (`a8eaf26e`), so it is in your base, and it closes in the first close batch.
  - **Read-only to you:** its paths `src/gov/store/**`, `src/gov/records/**` and `src/gov/check/citations.py`.
  - **Yours from now on:** `src/gov/decisions/**` and `tests/unit/decisions/**`, on top of its work.
  - **Your merge waits** until W2-03 has closed.
  - **Check W2-03's state** before the engineer starts and before you return: `grep -m1 '^status:' /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-ym8a.md`. If it says `closed` or `in_progress`, go on.
  - **If W2-03's close is refused,** the orchestrator writes `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/REFUSED-DAEO-ym8a`. Check for it at the same two points. If it is there, start nothing more, write your checkpoint, and return PACKAGES naming it.
- **Launched beside W2-04** (DEC-942 item 1). The two tickets share `src/gov/context/**`, and that overlap is split by file (below).
- **The orchestrator's drift measure starts with your close and W2-04's** (DEC-943 item 2).

## Two declared rounds (DEC-916)

- **Round 1, this run:**
  - the design, the tests, the red check;
  - the engineer, for everything except the `gov context` half of KPI line 3;
  - the backfill proposal;
  - W2-61's measure on your head;
  - then a return of PACKAGES with the backfill for the owner.

  **No full verification in this round.** The validator is meant to fail on the register until the owner's accepted backfill is applied, and it runs inside `core-authority`, so a full run now would only show that red.
- **Round 2, a later run with its own brief:** it starts once the owner has accepted the backfill, the orchestrator has applied it on `w2/integrate`, and W2-04 has merged.
  - Merge `w2/integrate` into this branch.
  - Add the `gov context` half: one test-design batch, then one engineer, built on W2-04's packet.
  - Rebuild, verify in full, run the measure again, and return DONE.
  - If W2-04 has not merged by then, round 2 returns PACKAGES naming the `gov context` half as the only open KPI.

## The decisions for this run

- **Design first, short.** The ticket's paths hold no note, so you write it in your scratch: `.gov-runtime/scratch/lead/design.md`, at most a page, in behaviour. It is a plan, not code. It says:
  - **the tags' form in the register:**
    - where each entry carries its domain (one of the closed list of eleven), its scope (this repository, or kernel-wide) and its "lands in" (the kernel file, the prompt or the project brief that states it);
    - the form "lands in" takes for an entry that is no standing rule;
    - how the status names what superseded or amended the entry: `SUPERSEDED by DEC-n`, or a "Changed by" note for a part (DEC-825 item 4, DEC-866 item 1).

    The form is part of your package: the owner accepts the form and the tags together.
  - **one rule for "not in force":** a whole entry whose status word is SUPERSEDED or DONE is left out. An entry changed only in part ("Changed by") stays in. Nothing else is left out. The rule is read from the register at `HEAD`, as the store reads it, never from the working tree;
  - **`gov retrieve`:** the filter applies where the command gives its bundle (`src/gov/retrieve/command.py`), to every item whose path and lines fall in a not-in-force entry's span.
    - The bundle says how many items it left out, and names each left-out id with the entry that replaced it, never its text.
    - Batches and `--continue` still work;
  - **the validator:** it lives in the decisions checker, which `core-authority` already runs.
    - Every entry carries domain, status, scope and "lands in"; the domain is from the closed list; a SUPERSEDED entry's status names its successor.
    - Each failure names its entry.
    - No new check declaration and no new `gov` command: both are outside your paths. If the design needs either, return PACKAGES;
  - **the propagation check (DEC-866 item 4):**
    - what it reads: tests, code, skills, briefs, ticket KPIs, the prompt and the path map;
    - how it finds a place that still enforces a superseded or changed decision: by id, and by value only where the fixture shows this can be done without guessing;
    - where a recorded reason lives: the register (DEC-866 item 3);
    - the finding's form: both decisions and the place;
    - its time on this repository, because `core-authority` runs at every close;
  - **the schema:**
    - The tags are fields of a register entry, so they go into `register-entry.schema.json`. The orchestrator adds that file to your paths before launch: your `decision*` glob matches only the decision-package schema, which you do not touch.
    - `core-schema` does not read the register, and `src/gov/check/schema.py` is W2-64's. Your validator does the checking.

  The note goes into the test designer's and the engineers' briefs as text.
- **Tests first,** by a fresh independent test designer (launched sandboxed, `--effort high`; its brief must not set `TMPDIR`), in `tests/acceptance/W2-55/`:
  - one case per KPI line and per failure line, in temporary repositories built from scratch, with a small register;
  - **the validator:** an entry missing each tag in turn fails, and the failure names it. So does a domain outside the list, and a SUPERSEDED entry whose status names no successor;
  - **`gov retrieve`** on a fixture that holds a superseded entry, a done entry and an entry changed in part:
    - the first two are never served, and the bundle gives the count and the ids;
    - the third is served;
    - lens B's Q05 shape (a superseded decision ranked first for its question) is one case;
  - **the propagation check:** the sweep's five cases are rebuilt as fixtures:
    - W1-49's two window cases: tests that enforce DEC-636's window after DEC-838;
    - W2-59's three cases: DEC-605's premise after DEC-822 and DEC-835.

    Each is found, and the finding names both decisions and the place. The same fixture with a recorded reason passes;
  - **the backfill:**
    - the branch's commits never change `docs/DECISION_REGISTER.md`;
    - the proposal names every entry of the register at the head, with its tags and a reason for each;
    - it holds the 120 amends and refines that DEC-825 left;
    - it draws its sample by a stated, repeatable method;
  - **the live case:** every entry of this worktree's register passes the validator. It is red until the accepted backfill is applied in round 2, and the README says so;
  - **left for later:** the `gov context` half of KPI line 3 is round 2's. KPI line 6 (the measure) is no test of this ticket. The README names both;
  - **in proportion (owner, DEC-951 item 5):** the owner found 2,980 lines of tests for 713 lines of code out of proportion. Aim at about 300 lines for this round, fixtures included. The README gives the count, and says why for anything past it.
- **The engineers** (each fresh, launched sandboxed where its suites allow, `--effort high`), one after the other:
  1. **The code engineer** works only in:
     - `src/gov/decisions/**`;
     - `src/gov/retrieve/**` (the filter only);
     - `template/governance/kernel/schemas/register-entry.schema.json`;
     - `tests/unit/decisions/**`, for its builder tests, the retrieve filter's included.

     Nothing in `src/gov/context/**` this round.
  2. **The backfill engineer** writes `docs/research/W2-55-backfill.md`, in a commit of its own (DEC-924 item 2). It holds:
     - one row per entry: the proposed domain, scope, "lands in" and status note, with the reason for each;
     - for a rule that drafts tags, the rule as stated and, on each row, which rule gave it. An entry no rule decides is read and marked so;
     - DEC-825's 120 amends and refines, as proposed "Changed by" notes on the earlier entries;
     - the propagation check's findings on this repository, each with a proposed update or a reason to record;
     - the sample for the owner: about 40 entries, drawn with a named seed, every domain represented, and every entry proposed as kernel-wide listed in full.

     Nothing is written to the register.
- **Fail closed:**
  - an entry the validator cannot read is a finding, never a pass;
  - the bundle never drops an item without counting it;
  - the propagation check missing an input is RED, never green;
  - no tag is applied to the register, by anyone in this ticket.
- **Running beside you** (paths checked against yours, file by file):
  - **W2-04** (`DAEO-u4oz`, launched beside you) holds every file of `src/gov/context/**` (`__init__.py`, `command.py`, `context_check.py`), `src/gov/retrieval/supplementary*` and `tests/unit/context/**`. You write nothing in `src/gov/context/**` until round 2, after its merge.
  - **W2-64** (`DAEO-0uhh`) holds `src/gov/check/schema.py`, `template/governance/kernel/schemas/close.schema.json` and `tests/unit/check/test_schema*`. No overlap.
  - **W2-78** (`DAEO-v4is`) adds new files only under `template/governance/kernel/schemas/`. `register-entry.schema.json` is yours.
  - **W2-05** (`DAEO-0z8c`, resuming) holds `src/gov/**/*.py` for the git environment of git calls. In your paths, that is the git helper of `src/gov/decisions/checker.py` (`_GIT`, its environment and `_git`). Leave it as it stands; the later merge takes the conflict.
  - **W2-61** (`DAEO-iw1f`) holds `src/gov/retrieval/measure.py`, `tests/unit/retrieval/test_measure*` and `fixtures/evaluation/memory-retrieval/visible/**`.
  - **W2-84** holds `src/gov/guard/reads.py`. **W2-51** holds `docs/plan/tools/validate_w2.py`. **W2-67** holds `tests/unit/close/**`, `tests/unit/guard/**` and `tests/conftest.py`. **W2-60a** holds `src/gov/launch/**`.
  - **W2-13** (`DAEO-zqvn`, not started) takes `src/gov/retrieve/**` after you.

  Do not touch their files. If your design needs a change there, return PACKAGES.
- **The register, the tickets and the plan** are never written by you or your workers. The orchestrator applies the accepted backfill.
- **Checks this round,** with the gates, the locks and the night rules as the common brief states them:
  - the W2-55 suite, `tests/unit/decisions` and `tests/unit/check`;
  - `gov check --json` after a full rebuild of this worktree. Name every check that is not green, with its cause. `core-authority` red on the untagged register is expected: it is the package's subject;
  - the collection check (DEC-868);
  - **the backfill tried on a copy:** put the proposed tags into a copy of the register file alone, in a temporary repository built from scratch. The validator must be green there, and you give the propagation check's findings with it.
- **W2-61's measure, on your head, after the engineers** (your filter changes what `gov retrieve` serves). It is your figure for this branch. The ticket's KPI line 6 is the orchestrator's re-run after the merge.
  - **The tool is on W2-61's branch, not yet merged.** Read `src/gov/retrieval/measure.py`'s docstring, `tests/acceptance/W2-61/README.md` and section 8 of the baseline record, all in `/home/usain/gov-os-worktrees/W2-61`, read-only. Use `PYTHONPATH=/home/usain/gov-os-worktrees/W2-61/src` for the measure, and `--sets-root /home/usain/gov-os-worktrees/W2-61`.
  - **If W2-61 has merged by then** (`git -C /home/usain/Dynamic-Agentic-Engineering-OS log -1 --format=%h w2/integrate -- src/gov/retrieval/measure.py` prints a commit), use `/home/usain/Dynamic-Agentic-Engineering-OS` for both instead.
  - **The clone:** `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS /home/usain/gov-os-runs/W2-55/repo`, detached at your head. You make it yourself, never a worker.
  - **The stores:** built in the clone by this branch's code, after the load and disk gates. Use `env -u GOV_TICKET PYTHONPATH=/home/usain/gov-os-worktrees/W2-55/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json`, run from the clone, in the background with an exit-code file.
  - **The retriever:** the measure removes `PYTHONPATH` from the process that retrieves, and runs `--gov`'s executable. So write, with the Write tool, `/home/usain/gov-os-runs/W2-55/gov-under-test`, holding two lines:
    - `#!/usr/bin/env -S PYTHONPATH=/home/usain/gov-os-worktrees/W2-55/src python3`
    - `import sys; from gov.cli.main import main; sys.exit(main())`

    Then `chmod +x` it.
  - **The run:** one run, visible half only, from the clone. Use `--root` (the clone), `--part visible`, `--gov` (that file), `--out /home/usain/gov-os-worktrees/W2-55/.gov-runtime/scratch/lead/measure` and `--json`. Add `--compare /home/usain/gov-os-worktrees/W2-61/.gov-runtime/scratch/lead/runs/records/measure-memory-retrieval-visible-20261029T212614400969Z.json`, the baseline's run 1. If that file is gone, leave `--compare` out and compare against the record's section 5.
  - **The check before trusting it:** the record's `retriever.gov_file` must point into `/home/usain/gov-os-worktrees/W2-55/src/`. If it does not, or the guard refuses a write under `/home/usain/gov-os-runs/W2-55/`, take the refusal and stop the measure. Name it in your return; the orchestrator measures after the merge.
  - **What you report, beside the baseline (8, 12 and 14 of 20):**
    - both figures together: hit@5 against 85 and full evidence against 99 %, and in the bundle;
    - each question that moved, Q05 by name;
    - what differs from the baseline: the tree, the retriever (this branch's code, not the pin) and the stores.

    Scores only, never a question's text or a retrieved item's text.
  - **After it:** remove the clone and keep the records. Run `keyword_warn.py` again.
- **No review (STANDARD).**
- **The package that ends this round,** in DEC-818's six parts:
  - the tag form;
  - the backfill's path and its sample;
  - the propagation check's findings here, each with its proposed update or reason;
  - the validator's findings on the register now, and on the backfilled copy;
  - the measure beside the baseline.

  It blocks round 2 only.

## This run's order

1. The design note (yours, in scratch).
2. Tests first (the test designer), then **check red yourself.**
3. The W2-03 check, then the code engineer.
4. The backfill engineer.
5. A full rebuild of this worktree, then the checks of this round and the backfilled copy.
6. W2-61's measure on your head.
7. A `gov checkpoint` record, then **return PACKAGES** (round 1 of 2: the backfill for the owner) with the branch head. Return earlier if another package blocks the engineers.

**Estimate:** about 150 lines of code, plus the backfill; about 6 hours for round 1, the measure included.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
