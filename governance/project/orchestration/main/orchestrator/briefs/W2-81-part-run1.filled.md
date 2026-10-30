You are the ticket lead for ticket `DAEO-l78m` (`W2-81`, "The adoption proving ground: five synthetic repositories with planted problems, a judge, and question sets per repository"). It is profile FULL, a test-design ticket on track B, and you work only in the worktree `/home/usain/gov-os-worktrees/W2-81` on branch `w2/W2-81`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `135ae00947cb`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-l78m.md`), with its ten KPI lines and five failure lines;
- in `docs/plan/WAVE_2_WBS.md` §2, its card ("#### W2-81") and the companion's card ("#### W2-81's held-out half");
- the re-plan, `governance/project/orchestration/packages/REPLAN-W2.md` §7.6;
- DEC-941, DEC-936 (item 3.6), DEC-930, DEC-833, DEC-820 ((c) and (d)), DEC-845, DEC-873, DEC-911, DEC-728, DEC-899 (item 7), DEC-906 and DEC-946 (item 5);
- the Contract's CAP-44 (`docs/contract/CONTRACT_v4.md`, "### CAP-44"): CAP-44.b to CAP-44.h and CAP-44.j, with CAP-03.a and CAP-03.d, and CAP-10's floor;
- the adoption code as it stands, read only, for the records each stage writes: `src/gov/adopt/` (`stages.py`, `legacy.py`, `project.py`, `command.py`);
- W1-41's acceptance cases (`tests/acceptance/W1-41/`), for how a case builds a repository of its own at test time;
- the path map's `evaluation_sets` block (`governance/project/path-map.yaml`), for the form of an evaluation set's entry.

## Why you start now

- **The proving ground is an entry criterion for EXAMIN's copy** (DEC-941; DEC-936 item 3.6; K9 in the WBS), beside the memory measure. Nothing today measures three things:
  - whether adoption tells current material from historical;
  - whether it keeps a secret out of its records and indexes;
  - whether it proposes restructuring rather than doing it.
- **Priority 5 of the owner's standing priorities** (DEC-946): the rest of EXAMIN's minimum.
- **No overlap:** its one path, `tests/acceptance/W2-81/**`, is held by no other ticket.
- **What it finds missed scopes later tickets.** Its first real run is the orchestrator's, after memory and K3. The planted problems found missed then decide what W2-26, W2-52 and W2-27 to W2-30 must cover.

## The decisions for this run

- **The visible part only.**
  - **The companion's path-map entry is not yet made.** Its card names it: `adoption-proving-ground`, with `visible: tests/acceptance/W2-81/questions/**` and `hidden: fixtures/evaluation/adoption-proving-ground/hidden/**`.
  - **The guard's hidden-part refusal reaches only a session's own tree** (row W2-H063).
  - So this run writes no hidden half anywhere: no hidden question, no hidden variant, no sample of either, and nothing under `fixtures/`.
  - **What the README does instead:** it states the hidden half's form, for the companion's auditor to write later.
  - **The visible questions** go under `tests/acceptance/W2-81/questions/`, so that the orchestrator's entry matches.
  - **When the hidden half is absent,** the scorer says so by name. The judge's verdict is then never READY: a figure not measured is a figure short.
  - **The self-tests may build a stand-in hidden half in their temporary folder.** It must be generated at test time, labelled a stand-in, and never committed.
  - Nobody in this ticket reads `fixtures/evaluation/**/hidden/**`, in this worktree or the main tree (DEC-820 (d)).
- **Who writes what: two fresh independent test designers, one after the other.** The ticket's only path is the acceptance folder, which only test designers write (DEC-906, MR-3). Each is launched sandboxed with `--effort xhigh`, and its brief must not set `TMPDIR`.
  - **td-1, tests first: the contract and the self-tests.** It writes:
    - the README:
      - each KPI line mapped to its cases;
      - each planted kind's correct handling and the record that must show it, against the adoption stages as built (A0 to A6, and A8 lite; A7 and A10 lite only once W2-52 lands, NOT_BUILT until then);
      - the manifest's form;
      - the judge's, scorer's and runner's interfaces;
      - the visible and hidden question forms;
      - the list of killed mutants, one per planted problem;
    - every `test_*.py` file: the judge's self-tests, including the mutation stand-ins of KPI line 8 and the controls of KPI line 5.

    The cases import the support modules inside the cases or a fixture, never at module level. A missing module is then a red case, never a collection error.
  - **Check red yourself (step 2 of the loop):**
    - every case is red because the support modules the README names do not exist yet;
    - none passes;
    - none is skipped (`-rs`);
    - none errors at collection.

    A case green before any judge exists cannot fail, and is a finding.
  - **td-2, the support modules,** which turn td-1's cases green. It writes:
    - the builders and the manifest;
    - the judge, the scorer and the runner;
    - the visible questions, at least 10 per repository, each with its gold sources and its forbidden citations.

    Policy 2 (c) applies as it does to an engineer:
    - td-2 reads the README, runs the `test_*.py` cases and reads their results;
    - it does not read the bodies of the `test_*.py` files;
    - it changes no `test_*.py` file and no KPI mapping in the README.

    A case it thinks wrong goes back to you as a dispute, and you return it as a package.
  - **If td-2 cannot finish in its 90-minute budget,** it commits what is green and returns, and you resume the same session (`--resume`) once.
- **Fixed by the KPIs; put them in both briefs as behaviour, never as names of code (DEC-462):**
  - **The repositories.** Five shapes, each built at test time in a temporary folder of its own as a git repository of its own, file by file and commit by commit.
    - Nothing is cloned from this repository, its worktrees or the dev tiers.
    - `GOV_DEV_TIERS` is not used, and the workbench is never listed or read.
    - Large files are generated at test time, scaled small in the self-tests and full size only in the real run.
  - **The planted problems.**
    - Each kind is planted in at least two shapes.
    - Each instance's names, places and wording are drawn from a seed per run, and the seed is in the report.
    - The manifest is kept outside the built repository: an adoption that could read it would fool the judge.
    - Every gold source of every visible question exists in the built repository for any seed (a self-test).
  - **The secret.**
    - It is built from parts at test time, committed early and removed later, so it lives only in history.
    - It is never whole in a tracked file of this repository, in a record, a log, a report or an output.
    - The judge compares it in memory only. **No assertion has the value in its expression:** pytest prints an assertion's operands when it fails. Compare a digest, or assert on a flag.
    - Its form is one the secrets scanner's default rules detect; a self-test shows the scanner finds it in the built history. A missing scanner fails, naming it.
    - The scanner's rule id and keywords appear in tracked files only in parts (row W2-L423's rule).
  - **The judge fails closed.**
    - A missing, unreadable or malformed record is MISSED.
    - A stage not built is NOT_BUILT, and is named.
    - A judge error is an error.
    - None of them is ever READY.
  - **The runner, one command for the real run, not collected as a test.**
    - It takes its run folder by literal path and writes nothing in this repository.
    - It is exercised in the self-tests only with stand-in adoption outputs in a temporary folder.
    - **Nobody in this run runs a real adoption or the real run** (`gov adopt`, the stages, or `gov retrieve` over a built repository): that first run is the orchestrator's (the ticket).
  - **The self-tests are hermetic and fast.**
    - They need no network and no model.
    - They write only in their temporary folders and remove them.
    - They take under 120 s alone and under the close's parallel load: build each repository once per module.
    - None is skipped.
  - **No `conftest.py` in `tests/acceptance/W2-81/`.**
    - A conftest outside W2-66's folder turns DEC-919's known red on (row W2-L440).
    - Fixtures live in support modules the cases import.
    - Support modules are not named `test_*`.
    - Nothing is added to the serial-only list.
- **Your checks** (in a script file under `.gov-runtime/scratch/lead/`, never `python3 -c` with braces, DEC-409):
  - `tests/acceptance/W2-81/` alone, twice, with different seeds: all green, no skip, under 120 s, and the seed in each report;
  - **one killed mutant per planted problem:** the README's list matches the cases one for one, and each mutant's case fails on it;
  - `git ls-files tests/acceptance/W2-81` lists no built repository, no generated large file, and no file over 200 KB;
  - the built repositories' temporary folders are gone after the run;
  - `keyword_warn.py` on the worktree, and `gov check`'s secrets checks green on the head;
  - `pytest --collect-only -q` over `tests`: no collection error.
- **Verification:** in full, in the close's form, under the lock, with the retention option and the disk gate first.
  - **The nightly (owner, DEC-933, DEC-936):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists (from 02:00 most nights), you and your workers run no suite and no full run. Wait, and go on the moment it is gone.
  - **Closes:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, start no worker and no suite.
  - **The 01:00 cut-off (owner, DEC-939 item 6):** from about 01:00, start no full verification run that `nightly_estimate.py estimate` says cannot finish before 02:00.
  - **Locks:** every full run goes under `flock /tmp/gov-os-verify.lock`, and every rebuild under `flock /tmp/gov-os-rebuild.lock` (DEC-939 item 2).
  - **Known:**
    - W1-42's accepted reds;
    - the load-sensitive cases, re-run alone;
    - W2-54's green-here cases may time out under load (row W2-L429), so re-run them alone;
    - W1-46's and W1-19's cases run in your serial phase.
  - Any other red is named with its cause.
- **Reviews: one (the ticket).** A fresh FULL reviewer (brief A3 with `JUDGEMENT.md` word for word, `--effort max`) on the final head, given td-1's README. **The probe looks above all for a way the proving ground passes an adoption that is not ready:**
  - a planted problem judged FOUND_AND_HANDLED when the stand-in missed or mishandled it;
  - a missing, unreadable or malformed record read as handled;
  - READY with a control flagged, a stage unmeasured or NOT_BUILT, the hidden half absent, or a figure short or reported alone;
  - a mutant listed in the README that no case kills;
  - a kind planted in only one shape, or an instance a fixed answer passes whatever the seed;
  - the manifest reachable from inside the built repository;
  - the secret's value whole anywhere: a tracked file, a record, a report, a log, or pytest's failure output;
  - any write in this repository, a read of the workbench or of a hidden half, a network need, a skip;
  - any hidden question or variant written in this run.

  **A finding that shows one of the ticket's failure lines fails the review.** Commit the probe record only when it passes. If it fails on such a finding: one test-design batch, the red cases and a full run, then a second and last review (DEC-413). In that batch, a fresh test designer is given the finding as a described behaviour (DEC-136).

**Running beside you:**
- **No running ticket holds `tests/acceptance/W2-81/**`.**
- **W2-52** (`DAEO-siiz`, merge-back) holds `src/gov/adopt/lite_gates.py`, `stages.py`, `template/governance/kernel/skills/adopt/**` and `.claude/skills/adopt/SKILL.md`:
  - the README reads the stage records as they stand at your head;
  - it names A7 and A10 lite NOT_BUILT where they are absent.
- **W2-26** (`DAEO-2ds6`) holds `docs/research/EXP-003/examin/**`.
- **W2-71** holds `src/gov/secrets/**` and `tests/unit/secrets_check/**`.
- **W2-61** holds `src/gov/retrieval/measure.py` and `tests/acceptance/W2-61/`.
- **W2-03** holds `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**` and `src/gov/check/citations.py`.
- **W2-05** holds the git-environment lines across `src/gov/**/*.py`.
- **W2-60a** holds `src/gov/launch/launcher.py`, `role.py` and `record.py`.
- **W2-77** holds `src/gov/close/nightly.py`.
- **The path map:** `governance/project/path-map.yaml` is the orchestrator's. Nobody here writes it.

Read them, change nothing there. If the proving ground needs a change in one of them, return PACKAGES.

## This run's order

1. td-1: the README and the self-tests.
2. **Check red yourself.**
3. td-2: the support modules and the visible questions.
4. Your checks.
5. Rebuild and verify in full.
6. The review.
7. **Return** DONE or PACKAGES.
   - DONE means the probe passed and the branch is ready to merge.
   - After the merge, the orchestrator adds the path-map entry. Then comes the companion's auditor for the hidden half, then the first real run.
   - Name, for the companion's auditor, the README sections it needs: the hidden form, and the builders' variant hook.

**Estimate:** about 1,200 lines, about 9 hours:
- td-1, about 90 minutes;
- td-2, up to two 90-minute budgets;
- the full run, about 95 minutes;
- the review and the return.

If your session nears its end first, write your checkpoint and return PACKAGES naming what is left; a fresh lead resumes from the checkpoint.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
