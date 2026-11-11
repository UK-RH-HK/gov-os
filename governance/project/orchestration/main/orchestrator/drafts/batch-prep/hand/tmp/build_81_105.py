import sys
sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/batch-prep/hand/tmp")
from parts import *

NAMES = ("identity", "where", "hooks_check", "rebuild", "disk_gate", "accept", "lead_verify", "launch_worker", "wait_for", "links",
         "keyword_warn", "context_ceiling", "merge_integrate", "tests_worktree", "merge_tests", "tests_worktree_remove")


def finish(body):
    for name in NAMES:
        body = body.replace("{" + name + "}", f"(command `{name}`)")
    return body


def build(w2, tid, kind, out, impl, profile, title, summary, usd, paths, mid_extra, run, rubric_rows, jud, est, sources_txt, dod_note, nongoals):
    head = sub(ASSIGNMENT_HEAD, ID=tid, W2=w2, PROFILE=profile, TITLE=title, SUMMARY=summary, USD=usd, PATHS=paths)
    dod = DOD.replace("@@DOD_NOTE@@", dod_note)
    mid = f"""
## What must be true (KPI lines and how each is checked)
{kpi_table(tid, w2, width=150)}
{nongoals}
{dod}

## Inputs
{mid_extra}
"""
    rubric = sub(RUBRIC, RUBRIC_ROWS=rubric_rows)
    body = (HAND_NOTICE.replace("@@REFUSAL@@", refusal(w2, kind)) + head + mid + "\n## Commands (copy them as they are)\n" + commands(w2, tid)
            + "\n" + FORMS + "\n" + rubric + run + jud)
    body = sub(body, ID=tid, W2=w2, KIND=kind, IMPL=impl, PROFILE=profile.split()[0])
    body = finish(body)
    rows = ", ".join(ticket(tid)["list_rows"]) or "none"
    tail = ("\n\n---\n\n# The common lead brief (committed, `governance/project/briefs/LEAD-w2-common.md`), appended whole\n\n"
            + common(w2, tid, profile.split()[0], paths, rows, sources_txt, impl, est))
    out.write_text(body + tail)
    print(out, len(body + tail))


JUD_SHORT = """
## Judgement rules (if you start a reviewer anyway)
No reviewer is planned in this run. If one is ever needed, its brief carries `governance/project/briefs/JUDGEMENT.md` word for word (read it in your tree after the merge), every finding with its `Ordinary work: yes|no, because ...` and `Consequence: fails open|loses work|other` lines and the fenced `verdict` block, and READY is computed by `verdict.ready` (`""" + TOOLS + """/verdict.py`), never declared by you. The two review rounds this ticket's plan declared are used up or not yours to start: return PACKAGES instead.
"""

# ---------------------------------------------------------------- W2-81, land
W2, TID = "W2-81", "DAEO-l78m"
mid81 = """- Sources: DEC-941, DEC-936, DEC-930, DEC-833, DEC-820, DEC-845, DEC-873, DEC-911, DEC-728, DEC-953, DEC-954, DEC-957, DEC-898, DEC-906 (ACCEPTED); DEC-899 is DONE, not a rule; CAP-03.a, CAP-03.d, CAP-44.b, CAP-44.e, CAP-44.g, CAP-44.h, CAP-44.j. Read each by id in /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md, or ask memory (below). Also DEC-997, DEC-1005, DEC-1010 (the rounds), DEC-895 (a re-probe only if a merge changes files the probe judged), DEC-1120 (RUBRIC-2), DEC-1130 (1) (why this brief is hand-built).
- **What the lead knows of the ground** (state as of 2026-11-11 ~18:00 UTC; the CTO's helper read the ticket, the checkpoint and the last returns, not the tests):
  - **State.** `w2/W2-81` is 19 commits ahead of `w2/integrate` and 1,880 behind, head `e78e6af7530d`, clean, worktree `/home/usain/gov-os-worktrees/W2-81` exists. The deliverable is test code only (37 files, 7,077 added lines, all under `tests/acceptance/W2-81/**` and `docs/`): five synthetic repositories with planted problems, a judge, a scorer, the visible question half, a README. **No file of the branch changed on integrate since the merge base `c38a5b49bc86` (0 overlap, measured), so the merge should be clean.** It gates W2-93 (which needs W2-81 *closed*) and, later, W2-88. Its first real run is the CTO's, in W2-27.
  - **Last lead return** (`log/W2-81-A5-r4-records.json`, 11-02): DONE at `e78e6af7530d`, a records-only commit that made the two probe records valid against the probe schema (`docs/probes/DAEO-l78m/PR-DAEO-l78m-moderated.md`, probed head `165d3057146a`, READY computed from review 5's verdict block: F1, F2 out of scope, F3 not ordinary work; and `PR-DAEO-l78m.md`, an earlier round's record the probe gate skips). Its scoped run 5 was green at that head: 4,233 passed, 1 skipped (`tests/unit/retrieval/test_lexical.py:54`, govbridge, existing), 0 failures; W2-81's own 276 cases passed alone in 33 s (round 3's batch 7). Three rounds are used (DEC-997, DEC-1005); no further review is owed.
  - **Open points.** (1) Integrate moved 1,880 commits since that run, so the verification is repeated once on the merged tree: the two probe records must still read valid to the three record checks the way they did (`tests/acceptance/W1-08/test_w1_08_probe.py`, `tests/acceptance/W1-26/test_w1_26_probe_records.py`, `tests/acceptance/W2-02/test_w2_02_green_here.py`), and W2-81's 276 cases must still pass under the pinned `gov accept`. (2) DEC-895: the probe judged only files under `tests/acceptance/W2-81/**` and the ticket; with 0 overlap the merge changes none of them, so **no re-probe**. A conflict, or a merge that touches one, is PACKAGES. (3) Empty untracked harness folders sit in the tree (`tests/acceptance/W2-81/.claude/`, `tests/acceptance/W2-81/questions/.claude/`: `.cc-writes` markers; git shows them as nothing): name them in your return, never remove them (the guard refuses). (4) The branch's `trailer_gate` named three `Implements:` ids (DEC-1010, DEC-997) that resolve only on integrate's register: they resolve after this merge; the step is off in the facts file, so just note it. (5) EST_LOC_OVER (est 1,200; 7,077 added) is a warning, not a refusal: report the lines against the estimate."""

run81 = f"""
## Your run: land (only this section is in your brief)
**land**: the branch is verified and its review is done; the queue merges and closes, you never merge into `w2/integrate`. Because integrate moved, the land round is: confirm, merge integrate in, verify once, return the new head.
1. First calls: (command `identity`) (expect `orchestrator` and `{TID}`), (command `where`) (expect `/home/usain/gov-os-worktrees/W2-81` and `w2/W2-81`); read `/home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/CHECKPOINT.md` (it exists: its last line is DONE at `e78e6af7530d`); `git -C /home/usain/gov-os-worktrees/W2-81 rev-parse --short=12 HEAD` must be `e78e6af7530d` and `git status --short` empty. Anything else: stop and return PACKAGES.
2. Merge `w2/integrate` into the branch (command `merge_integrate`; message file ending `Task: {TID}`, `Role: orchestrator`), after (command `hooks_check`). Expect no conflict. A conflict: PACKAGES at once, with the file list (a conflict in `tests/acceptance/` is a test designer's, DEC-1052; you start none here without the CTO).
3. Check the merge changed no file the probe judged (DEC-895): `git diff --name-only` of the merge's first parent against the merge, none under `tests/acceptance/W2-81/` and not the ticket file. If one is, PACKAGES.
4. (command `disk_gate`); (command `accept`) once (276 cases expected; read it as pass or fail per line, never a case's source); the three record checks alone (the three files named above, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, the empty `HOME`); then (command `lead_verify`) once in the background and (command `wait_for`) on it (the scoped verification, DOD-2; the selection is expected to hold W2-81's folder and the record cases; the scoped run waits for a heavy slot). A red: name it only from the known-reds list `{TOOLS}/skip_known.json`, re-run a load-sensitive case alone once; a red your merge caused, or any other red you cannot name: PACKAGES with the output. Start no worker; the branch has no open round and you write no file under `tests/`.
5. Before you return: (command `links`) (`gov links --since e78e6af7530d`, first line quoted in `evidence`), (command `keyword_warn`), (command `context_ceiling`) once (a ceiling refusal: figures and a package naming what to trim, DEC-1027; W2-81 is one of the 8 that refused on 11-02), the scratch measures, CHECKPOINT.md rewritten with the new head, `git status --short` empty. Return DONE with the exact head you verified (12 digits), the `gov accept` counts, the scoped run's counts, a line saying no review ran, the `gov.__file__` line, and the lines against the estimate.
Estimated at 1.5 lead-hours and about $4 (E: its resumes were 1.7 to 1.9 h and $3.3 to 4.3, M).
"""

build(W2, TID, "land", PREP / "hand" / "W2-81-A5-r5-land.md", "DEC-941, DEC-936, DEC-930, DEC-820, DEC-953, DEC-954, DEC-957, DEC-1010",
      "FULL (C2)", "The adoption proving ground (W2-81): the land round, integrate merged in and the verification repeated once",
      "The ticket: five synthetic repositories built at test time with planted problems whose handling is known, controls against over-flagging, a judge, "
      "a scorer, mutation tests of the judge, per-repository question sets (the visible half here, the hidden half is W2-93's), one command for the real run "
      "(the CTO's, in W2-27), and a hermetic, bounded suite. Test code only, under `tests/acceptance/W2-81/**`.",
      "4", "tests/acceptance/W2-81/** (you write none: this run writes only under your scratch and, if the CTO asks, a checkpoint record)",
      mid81, run81,
      """| worker | role | class | model | effort | when |
|---|---|---|---|---|---|
| none planned | | C2 | | | a red or a conflict is PACKAGES; a repair is the CTO's to order (Opus at high for a designer on this C2 ticket) |""",
      JUD_SHORT, "1200 lines of code (7,077 added: EST_LOC_OVER)",
      "DEC-941, DEC-936, DEC-930, DEC-833, DEC-820, DEC-845, DEC-873, DEC-911, DEC-728, DEC-953, DEC-954, DEC-957, DEC-898, DEC-906, CAP-03.a, CAP-03.d, CAP-44.b, CAP-44.e, CAP-44.g, CAP-44.h, CAP-44.j",
      "DOD-4 holds from the earlier rounds: the probe record `PR-DAEO-l78m-moderated.md` is READY (computed); you add no review",
      "Non-goals (the ticket states none; `gov brief`'s NON_GOALS_MISSING): the hidden question half (W2-93's, an independent auditor's), the real run and its report (the CTO's, W2-27), any new case or fix in this run, and any merge into `w2/integrate`.")

# ---------------------------------------------------------------- W2-105, tests
W2, TID = "W2-105", "DAEO-zpdj"
mid105 = """- Sources: DEC-966, DEC-172, DEC-957, DEC-965, DEC-971 (all ACCEPTED). Read each by id in /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md, or ask memory (below). Also DEC-959 item 6 (the README map in the form `gov accept` reads), DEC-866, DEC-1031 item 3, DEC-1052, DEC-1120 (RUBRIC-2), DEC-1130 (1) (why this brief is hand-built).
- **What the lead knows of the ground** (state as of 2026-11-11 ~18:00 UTC; the CTO's helper read the ticket, the checkpoint, the last return and the diff, not the suites' results):
  - **State.** `w2/W2-105` is 7 commits ahead of `w2/integrate` and 1,856 behind, head `fa653609cc93`, clean, worktree `/home/usain/gov-os-worktrees/W2-105` exists. The one real change is done: two deny lines (`npm install*`, `pip install*`) out of `template/.rulesync/permissions.jsonc`, so a generated product's CTO session reaches the guard's install rule (DEC-966 item 1; the product's CTO-only rule is W2-110's, DEC-971 item 4). Tests: `tests/acceptance/W2-105/` (28 cases; README, conftest, support, one test file) and W1-38's two files, revised by this ticket for the two removed rules (`Rewrite-Reason: DEC-966 item 1`). Verified DONE on 11-01 (run 2): W1-38 201 passed, W1-39 71 passed, the scoped run 4,196 passed. It gates W2-90c (the cases of W2-90b that need W2-105).
  - **Last lead return** (`log/W2-105-A5-resume-ten.json`, 11-01 17:58): DONE with residual R-W2-105-1: `gov accept DAEO-zpdj` exit 3, 28 cases passed, 0 failed, but three KPI lines (success-1, success-2, failure-1) read **fail with 0 of 0 cases**, because the README's map items with placeholders (`test_x[<install>-deny]`, `[<role>-<install>]`) did not match any case in the then-reader's `matches()`; 22 cases unmapped; no case asserts the CTO-only rule (not this ticket's).
  - **What changed since.** The map reader was reworked on 11-10 (W2-96 D-10 round 2: it reads every further line a cell names, reads a list joined by ", and" whole, refuses a bracketed citation as a line name, enables only the `breadth` opt-in). So the three lines **may read now**; this run's first question is whether they do.
  - **The merge.** Three files changed on both sides since the merge base `f46b96537d74`: `template/.rulesync/permissions.jsonc` (integrate added the `gov launch:*` allow line, W2-56, near the two install denies this ticket removed: keep the allow line, keep the two denies removed), `tests/acceptance/W1-38/test_w1_38_test_folder_rule.py` and `tests/acceptance/W1-38/README.md` (this branch revised the two cases that pinned the install rules; integrate cut W1-38's full run from 201 to 35 cases and regenerated its README map, D-4 cut B: keep both sides' intent). **A conflict in an acceptance file is a test designer's to resolve, and that merge carries `Role: independent-test-designer`** (DEC-1052, DEC-1031 item 3); the permissions source is product-spec's file, so a conflict there you resolve only as a merge (never `-s ours`, never dropping the ticket's side); if the guard refuses you that write, or a conflict cannot keep the ticket's side, PACKAGES at once, naming the files.
  - **Open points.** (1) The CTO-only install rule and "leads included" are not this ticket's (W2-110, DEC-971 item 4): the README says so. (2) `gov accept` runs `copier` and `rulesync` (registered tools at `~/.local/bin`; node on `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH`); nothing is installed by a test. (3) Success 4 and failure 4 (W1-38 and W1-39 pass) have no case of their own in the README (shown by running those two folders); if the reader marks them unmeasured, the designer's map revision names how they are shown. (4) STANDARD profile: no probe, no reviewer. Previous lead's gap: the order "rebuild first" held it an hour behind the machine's rebuild queue though no selected case reads the store: skip the rebuild unless a case answers `STORE_MISSING`."""

run105 = f"""
## Your run: tests (only this section is in your brief)
**tests**: the tests only, here a README-map round if one is still needed, then the land. The code change is done and verified; do not touch `template/` except as the merge's own resolution.
1. First calls: (command `identity`) (expect `orchestrator` and `{TID}`), (command `where`) (expect `/home/usain/gov-os-worktrees/W2-105` and `w2/W2-105`); read `/home/usain/gov-os-worktrees/W2-105/.gov-runtime/scratch/lead/CHECKPOINT.md` (it exists: run 2, DONE at `fa653609cc93`); `git rev-parse --short=12 HEAD` must be `fa653609cc93` and `git status --short` empty. Anything else: stop and return PACKAGES.
2. Merge `w2/integrate` into the branch (command `merge_integrate`; message file ending `Task: {TID}` and the role the conflict rule above gives), after (command `hooks_check`). Resolve as described above. After the merge, check `template/.rulesync/permissions.jsonc` holds neither install deny line and still holds `gov launch:*`.
3. (command `disk_gate`); then (command `accept`) once with `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH` set for the run. Write the per-line result (S1 to S4, F1 to F4; the README names them success-n and failure-n) into CHECKPOINT.md.
   - **All eight lines read pass and none is unmeasured:** no designer round; skip to step 6.
   - **A line still reads fail or unmeasured with every case passing** (the 11-01 pattern): step 4.
   - **A case fails:** it is a real red from the merge (most likely W1-38's merged cases): PACKAGES with the output, unless it is a conflict-resolution slip in an acceptance file, which a designer fixes in step 4.
4. **Test-design round, README map only** (a fresh independent-test-designer in the tests worktree: (command `tests_worktree`), launched with (command `launch_worker`)): the map's items revised so the current reader reads them (the three failing items named by line and the reader's refusal text; name the real case ids or a form the reader matches, no placeholder in a code span; S4 and F4 by the cases that show them if the reader needs a case); **no case body, assertion or expectation changed, no line lowered** (`Rewrite-Reason: DEC-959 item 6`, DEC-866); it never reads this ticket's implementation (the permissions source, DEC-820 (c)) and drops unread any `gov retrieve` result under it (P-R1); its brief carries DEC-820 (c) and (d) and the hidden-half rule. Merge it ((command `merge_tests`)), run (command `accept`) once more; a line still red after this one batch: PACKAGES (the reader's rule, not a loop). Remove the tests worktree and branch ((command `tests_worktree_remove`)).
5. If the designer also resolved the W1-38 conflicts, that merge carries `Role: independent-test-designer`; the check that its commits carry `Task: {TID}`, `Role`, `Implements:` ids from the ticket's sources is yours, the moment each exists.
6. The scoped verification once: (command `lead_verify`) in the background, (command `wait_for`); W1-38 (35 cases in its full run after D-4 cut B, plus its breadth opt-in under `gov accept`) and W1-39 (success 4) are the ticket's own suites and must be named green; a red named only from the known-reds list `{TOOLS}/skip_known.json`; a load-sensitive case alone once.
7. Before you return: (command `links`) (`gov links --since fa653609cc93`, first line in `evidence`), (command `keyword_warn`), (command `context_ceiling`) once, scratch measures, CHECKPOINT.md rewritten, `git status --short` empty, TESTS-READY written naming the head if a designer round ran. Return DONE with the exact verified head (12 digits), `gov accept` counts per line before and after, the scoped run's counts and JUnit paths, the `gov.__file__` line, and the lines against the estimate of 10; the CTO lands it and W2-90c follows.
Estimated at 1.5 to 3 lead-hours and $4 to 9 (E: W2-105's own runs were 2.2 h and 2.3 h, $3 and $6, M); the machine's rebuild and slot queues are the uncertain part; no rebuild is planned.
"""

build(W2, TID, "tests", PREP / "hand" / "W2-105-A5-r3-tests.md", "DEC-966, DEC-172, DEC-957, DEC-965, DEC-971",
      "STANDARD (C3, permissions)", "The template's install block removed (W2-105): the README map round, if still needed, and the land",
      "The ticket: a project generated from the template holds no deny rule for `npm install*` or `pip install*`, so an install reaches the guard's install rule "
      "and the CTO's session is asked as this repository's is; every other permission rule is unchanged; the template's own suites (W1-38, W1-39) pass.",
      "4", "template/.rulesync/permissions.jsonc (the ticket's only path; the tests are `tests/acceptance/W2-105/**` and W1-38's two files)",
      mid105, run105,
      """| worker | role | class | model | effort | when |
|---|---|---|---|---|---|
| test designer | independent-test-designer | C3 (permissions) | Opus (`claude-opus-5-5`) | high | step 4 only, and only if a line still reads fail or unmeasured after the merge; also the W1-38 conflict resolution |
| product-spec | product-spec | C3 | Sonnet (`claude-sonnet-5-5`) | high | none planned: the merge's one resolution is the lead's; a launch needs the CTO's word |""",
      JUD_SHORT, "10 lines of code",
      "DEC-966, DEC-172, DEC-957, DEC-965, DEC-971",
      "DOD-4 does not apply: STANDARD, no review; DOD-1 is the point, the eight lines read pass through `gov accept`",
      "Non-goals (the ticket states none; `gov brief`'s NON_GOALS_MISSING): a product's CTO-only install rule and \"leads included\" (W2-110, DEC-971 item 4), W2-90c's cases, any change to a permission other than the two denies, and any merge into `w2/integrate`.")
