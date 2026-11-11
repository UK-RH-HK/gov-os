"""Builds the hand-built lead brief for W2-66c (DAEO-btcs), run tests (DEC-1130 (1)). Reuses parts.py; writes one file."""
import sys
sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/batch-prep/hand/tmp")
import re
import parts
from parts import *

OUT = ORCH / "briefs" / "W2-66c-A5-r2-tests.md"
W2, TID, KIND = "W2-66c", "DAEO-btcs", "tests"

NAMES = ("identity", "where", "hooks_check", "rebuild", "disk_gate", "accept", "lead_verify", "launch_worker", "wait_for", "links",
         "keyword_warn", "context_ceiling", "merge_integrate", "tests_worktree", "merge_tests", "tests_worktree_remove", "stop_a_job")


def finish(body):
    for name in NAMES:
        body = body.replace("{" + name + "}", f"(command `{name}`)")
    return body


def kpi_table_66c():
    d = ticket(TID)
    rows = []
    for i, line in enumerate(d["kpis"]["success"], 1):
        t = " ".join(str(line).split())
        m = re.search(r"Verify: (.*?) \[DEC", t)
        v = m.group(1) if m else t
        head = t.split(" Verify:")[0]
        head = head[:150].rstrip() + ("..." if len(head) > 150 else "")
        v = v[:230].rstrip() + ("..." if len(v) > 230 else "")
        rows.append(f"| S{i} | {head.replace('|', '/')} | the ticket's own `Verify:` (cut): {v.replace('|', '/')} |")
    fverify = [
        "S6's red run on the parent map of ACT-SELECT-FIXES-1 (`795d97c7cd44`): every S1-S4 case red there, so none passes before the ACT; you repeat that run yourself (step 6)",
        "`git diff --name-only <BASE>..HEAD` of the tests branch names only `tests/acceptance/W2-66/test_w2_66_select_fixes.py`; `git diff <BASE>..HEAD -- tests/acceptance/W2-66/` shows no other file of the folder touched, and no `skip`, `xfail` or `skipif` in the new file",
        "read the new file (it is yours to read: you are the lead, not the designer): no `subprocess`, no `pytest.main`, no `os.system`, no `gov` command started, no path read outside the repository's tracked files and `tmp_path`; the file's imports named in your return",
    ]
    for i, (line, v) in enumerate(zip(d["kpis"]["failure"], fverify), 1):
        t = " ".join(str(line).split()).replace("|", "/")
        rows.append(f"| F{i} | {t[:150]} | {v} |")
    return "| id | line (cut; the ticket file holds the whole line) | verify |\n|---|---|---|\n" + "\n".join(rows)



def fill(text):
    """LEAD-w2-common.md's slots are written {ID} etc.; parts.common() substitutes @@ID@@ forms only, so they stay open. Fill them here."""
    vals = {"ID": TID, "W2": W2, "PROFILE": "LITE", "PATHS": paths, "ROWS": rows, "SOURCES": sources_txt, "IMPL": impl, "EST": "160 lines of code"}
    for k, v in vals.items():
        text = text.replace("{" + k + "}", v)
    return text


HAND = HAND_NOTICE.replace(
    "refuses this ticket today: a reviewed ticket in progress has KPI lines with no `Verify:` text.",
    "refuses this ticket today: its three failure lines carry no `Verify:` text (the success lines do), and the ticket states no non-goals (the size and non-goals lines are warnings, not refusals).",
).replace(
    "DEC-1130 (1) (the owner's exception to DEC-1083, for tickets in progress only) lets it launch",
    "DEC-1130 (1) (the owner's exception to DEC-1083, for reviewed tickets in progress; the CTO applies it to this ticket, which is `open`: its D-10 designer revision of 11-10 was reviewed READY and returned it to open, `2979f3607`; the CTO claims it before the launch) lets it launch",
).replace(
    "The KPI table below carries each line's `Verify:` as the one command that measures it (`gov accept`, read from the README map): the ticket file itself is not edited by this brief.",
    "The KPI table below carries each success line's own `Verify:` text from the ticket (cut) and, for the three failure lines, the check the lead makes; the ticket file itself is not edited by this brief.",
)

MID = """- Sources: DEC-1109, DEC-1112, DEC-1100, DEC-1098, DEC-889, DEC-253, DEC-968, DEC-1061, DEC-912, DEC-1045, DEC-906 (ACCEPTED); DEC-891 and DEC-896 are DONE, not rules (read them for what they decided). Read each by id in /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md, or ask memory (below). Also DEC-1120 (RUBRIC-2), DEC-1130 (1) (why this brief is hand-built), DEC-892 (a test-revision ticket is judged on its declared `acceptance_tests.path`, here `tests/acceptance/W2-66/`).
- **What the lead knows of the ground** (state as of 2026-11-11 ~19:00 UTC; the CTO's helper read the ticket, the ACT's package and the live map, not the tests of this ticket, which do not exist yet):
  - **State.** `DAEO-btcs` is `open`; the worktree `/home/usain/gov-os-worktrees/W2-66c` exists on a fresh branch `w2/W2-66c` made from `w2/integrate` at `256b4e12d7ca` (so the role templates `.claude/templates/role-test-designer.md` and `role-lead.md` are present), clean. The file to write, `tests/acceptance/W2-66/test_w2_66_select_fixes.py`, does not exist. This is a **tests-only run**: no product code, no `src/`, no `governance/`, no `tests/optin-lifted-breadth.txt` change; the ticket's one allowed path is that file.
  - **ACT-SELECT-FIXES-1 is applied** (the operator committed it as `8038e0ee648c`; its parent is `795d97c7cd44`; DECIDED-NOT-DONE row 37). It changed `governance/project/test-map.yaml` (19 couplings, was 16; 31 `record_reading` entries, was 30; 17 `record_only` entries, was 13; 16 today, after ACT-WIN-TOAST-1) and dropped the `rep:` line for W2-66's record-only case from `tests/optin-lifted-breadth.txt` (F1 (a), so a selection runs all seven rows). The ACT's package is `governance/project/orchestration/packages/ACT-SELECT-FIXES-1.md` (§1 lists the exact lines; it is a plain record, you may read it; the designer works from the KPI lines, not from it, MR-3).
  - **What changed on those two files since the ACT** (so S6's \"green on `w2/integrate`\" is measured on the live files, and S6's \"red on the parent\" on the parent's): `3849c1ca2223` (ACT-WIN-TOAST-1: `tools/win_toast.ps1` out of `record_only`), `a46d4517a1a0` (ACT-D4-RESTORE-1: six lines of the breadth list), `3fea21bb5322` (W2-140: four renamed W2-49 cases renamed in the breadth list). None touches the four couplings or the `record_reading` line; the designer's cases are written from the KPI lines and must hold on the live head.
  - **The designer round was revised in D-10** (`2979f3607`): on `w2/W2-66c-d10-tests` (`dc5c0fd87278`, merged to integrate) a designer changed W2-66's DEC-891 record case (`test_w2_66_live_test_map.py::test_every_record_of_each_of_dec_891_s_places_is_record_only`, line 300) so a file under a `tools/` folder that a `.py` there names is not a record (option (a), DEC-1112 (3)); the review rows F1, F2, F4 stay recorded in the ticket. **That change is not this run's work** and its files (`test_w2_66_live_test_map.py`, the README) are W2-66b's (`DAEO-zuiy`): leave them. S4's case here pins that the same case is in `record_reading` and runs whole; it must not re-derive the D-10 change.
  - **The W2-66 suite already reads the live map the way these cases must**: `test_w2_66_live_test_map.py` (`RECORD_READERS`, `COUPLINGS` fixtures, the product's loader `gov.close.select.load_map(root)` returning `(map, error)`, matcher `gov.close.select.match(path, pattern)`, `plan(root, wbs, ...)`) and `tests/conftest.py`'s `optin_entries(folder)`. The designer reads those tests and the README's Interface section for the calls' forms, and **does not read the bodies of `src/gov/close/select.py`** (it writes from the KPI lines; the signatures are in the README).
  - **Open points.** (1) **The README is outside the ticket's paths.** `allowed_paths` is the one `.py` file, so the designer cannot add the six lines' map to `tests/acceptance/W2-66/README.md`; `gov accept` reads that map. Run (command `accept`) once at the end and report the result per line as information; an unmapped or unreadable reading for S1-S6 is expected and is a discovery for the CTO (who may add the README to the ticket's paths), never a PACKAGES on its own. (2) **S6's red run** needs the parent's two files copied over a scratch clone (step 6): this is the proof that F1 holds (no case passes before the ACT); the designer records its own run in the commit body, and you repeat it. (3) S4's planted-repository case runs the product's `gov.close.select.plan` on a copy of the test map and tickets folder inside a planted git repository: the case starts no gov command and no pytest (F3), it calls the function. (4) The tests branch and worktree are the lead's to create and remove; the designer never reads the held-out or evaluation material (none is involved). (5) Estimate: ticket says about 160 lines and two hours with the S6 record."""

RUN = f"""
## Your run: tests (only this section is in your brief)
**tests**: one independent test designer writes `tests/acceptance/W2-66/test_w2_66_select_fixes.py` from the six success lines and three failure lines; you create its worktree, brief it, check its work and merge it into your branch. You write no test and no code yourself. The CTO runs the scoped run and the formal close.
1. First calls: (command `identity`) (expect `orchestrator` and `{TID}`), (command `where`) (expect `/home/usain/gov-os-worktrees/W2-66c` and `w2/W2-66c`); `git -C /home/usain/gov-os-worktrees/W2-66c status --short` empty; `git -C /home/usain/gov-os-worktrees/W2-66c rev-parse --short=12 HEAD` is the BASE (record it; it is `256b4e12d7ca` or a later integrate head with the ticket's claim) and `git merge-base --is-ancestor HEAD w2/integrate` holds; `.claude/templates/role-test-designer.md` exists in your tree and `tests/acceptance/W2-66/test_w2_66_select_fixes.py` does not. Anything else: stop and return PACKAGES. Write `/home/usain/gov-os-worktrees/W2-66c/.gov-runtime/scratch/lead/CHECKPOINT.md` (no earlier one exists: this is the ticket's first lead run) with BASE and the step you are at, and keep it current.
2. If the CTO's claim commit (`tk start DAEO-btcs`) is on `w2/integrate` but not in your branch, merge `w2/integrate` first (command `merge_integrate`; message file ending `Task: {TID}` and `Role: orchestrator`), after (command `hooks_check`); expect no conflict (a conflict: PACKAGES at once). Then BASE is the merge's head.
3. (command `disk_gate`). Create the tests worktree (command `tests_worktree`): `/home/usain/gov-os-worktrees/W2-66c-tests` on `w2/W2-66c-tests`. Note its path in CHECKPOINT.md.
4. **Write the designer's brief** (Write tool) at `/home/usain/gov-os-worktrees/W2-66c/.gov-runtime/scratch/lead/briefs/designer-1.md` from the role template `.claude/templates/role-test-designer.md` (read it in your tree) and this ticket: the designer's own facts only. It carries:
   - the identity (role `independent-test-designer`, ticket `{TID}`, worktree `/home/usain/gov-os-worktrees/W2-66c-tests`, branch `w2/W2-66c-tests`); the one path it may write, `tests/acceptance/W2-66/test_w2_66_select_fixes.py`; the nine KPI lines **word for word** from the ticket file (S1 to S6, F1 to F3; the ticket's `Verify:` text on S1 to S6 is the design's measure);
   - the method: tests first, from the lines and the interfaces, never from the patch (MR-3, DEC-906); it reads the existing W2-66 tests and README Interface section and `tests/conftest.py` for the calls' forms; it **never reads the bodies of `src/gov/close/select.py` or any implementation** and drops unread any `gov retrieve` result under `src/` (DEC-820 (c), P-R1); it never reads `governance/project/orchestration/packages/ACT-SELECT-FIXES-1.md` or the ACT's patch files (the lines say what to pin); it reads `governance/project/test-map.yaml` and `tests/optin-lifted-breadth.txt` because the cases read them as data (they are tracked inputs, not the implementation);
   - the cases' form: pytest, one parametrised case per path where the line says "a case per path" (S1 one per path of the three, S2 one per tracked file under `template/governance/kernel/checks/` listed by `git ls-files`, S3 planted paths: an acceptance `.py`, an acceptance `.md`, a conftest); a helper that reads the live map with `gov.close.select.load_map` and matches with `gov.close.select.match`; S4's three cases (`record_reading` holds the node id; no opt-in list holds a `rep:` line for the function, read with `optin_entries`; a planted git repository in `tmp_path` with a copy of the map and tickets folder and one records-only commit, asserting `plan` selects the case); S5 over every coupling target (node ids checked by reading the file's `def` and `class` lines, no collection, no run) and a planted map with a misspelt node id that reds the same helper; **no case runs a pytest selection, starts a gov command or reads outside the repository's tracked files and its own temporary folders** (F3); no `skip`, `xfail` or `skipif`;
   - **S6 as a procedure the designer carries out and records in the commit body:** (a) run the new file in a scratch clone of its tests branch under `/tmp/gov-os-lead-W2-66c/` (the brief names the folder; one clone, removed after) with the parent's `governance/project/test-map.yaml` and `tests/optin-lifted-breadth.txt` copied over from `795d97c7cd44` (`git show 795d97c7cd44:<path>`): every S1 to S4 case must be red there (S5's cases are exempt from the red rule: say what they do on the parent); a case that is green on the parent pins nothing (F1): it is rewritten until it reds, or dropped and named in the return; (b) the same file green on `8038e0ee648c`'s two files and on the live head (the worktree as it stands); the three counts in the commit body (red on parent, green on the ACT, green on integrate) with the exact pytest line; empty `HOME` and `PYTHONPATH` of the clone's `src`, as the common forms say;
   - the commit line: `git commit -m "W2-66c: ..." --trailer "Task: {TID}" --trailer "Implements: DEC-1100, DEC-1098, DEC-1109, DEC-1112" --trailer "Role: independent-test-designer" -- tests/acceptance/W2-66/test_w2_66_select_fixes.py` (a new file, so no `Rewrite-Reason`); never amend; the hidden-half rule and no installs; its twelve return fields as labelled lines first; `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>"` for what it needs about decisions (twice at most, DEC-1092 (1)), and a statement in its return of whether it used it.
   - Add to its return a line `readme_map_gap:` naming whether the six lines map to cases it can name (so the CTO can have the README line written), and the file's case count per S line.
5. Launch it (command `launch_worker`) with `--class C2 --model claude-opus-5-5 --projection-usd 5` and `independent-test-designer high designer-1.md` (the CTO's choice: Opus at high for this designer on this C2 ticket; BATCH-PREP's table says Sonnet high; the CTO's choice holds), `LAUNCH_TREE=/home/usain/gov-os-worktrees/W2-66c-tests`, `LAUNCH_TICKET={TID}`; it prints the log, exit file and pid; (command `wait_for`) on the exit file, one call per 9.5 minutes; stop only with (command `stop_a_job`) by pid. The launcher runs the tripwire; name its result. Check the twelve fields (the resume rule of the common brief applies).
6. **Check the designer's work yourself** (it is your gate, no reviewer runs):
   - the commit: `git -C /home/usain/gov-os-worktrees/W2-66c-tests log --format='%h %an%n%B' BASE..HEAD` shows one or more commits with `Task: {TID}`, `Role: independent-test-designer` and `Implements:` ids from the ticket's sources (ACCEPTED ones); `git diff --name-only BASE..HEAD` is exactly the one allowed path (F2); no other case of the folder touched or skipped;
   - the nine lines, one by one, against the file (name the case ids that show each; the verify column above is the check);
   - **repeat S6 yourself, once:** in a throwaway clone under `/tmp/gov-os-lead-W2-66c/clone` (script file with the Write tool, run with `bash`): clone the tests branch, copy over the parent's two files (`git show 795d97c7cd44:governance/project/test-map.yaml` and `:tests/optin-lifted-breadth.txt`), run the file (empty `HOME`, `PYTHONPATH=<clone>/src`, `-m "not local_only"`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, one file only, through the heavy slot if it exceeds a minute): every S1 to S4 case red; then without the copy-over: green. Any S1-S4 case green on the parent: send the designer back once in the same session (`--resume`, naming the cases); a second failure: PACKAGES (a promotion is the CTO's, DEC-1120 (3)). Remove the clone afterwards (`rm` only inside `/tmp/gov-os-lead-W2-66c`);
   - run the new file once on your own tree after the merge (step 7) and the folder `tests/acceptance/W2-66/` alone (the empty-HOME form of the common forms, every whole-folder run with the filters): the new cases green, the others as before (a red you did not cause: name it only from `{TOOLS}/skip_known.json`, a load-sensitive one alone once).
7. Merge the designer's branch into yours (command `merge_tests`; message file ending `Task: {TID}`, `Role: orchestrator`; expect no conflict, a new file). Remove the tests worktree and branch (command `tests_worktree_remove`; then the branch by `git -C /home/usain/gov-os-worktrees/W2-66c branch -d w2/W2-66c-tests`).
8. (command `accept`) once (the README map is not the ticket's path: report the per-line reading as information, open point 1); then the scoped verification: (command `lead_verify`) in the background, (command `wait_for`) on it (the selection is expected to hold `tests/acceptance/W2-66/`; the run waits for a heavy slot).
9. Before you return: (command `links`) (`gov links --since BASE`, first line in `evidence`), (command `keyword_warn`), (command `context_ceiling`) once, the scratch measures, CHECKPOINT.md rewritten, `git status --short` empty, a `TESTS-READY` file in your scratch naming the head. Return DONE with the exact head (12 digits), the designer's commit hashes (12 digits) and counts (red on the parent, green on the ACT, green on the head), the case ids per S line, `readme_map_gap`, the scoped run's counts and JUnit paths, the `gov.__file__` line, the tripwire result, and the lines against the estimate of 160; the CTO runs its scoped run, lands the branch and closes the ticket.
Estimated at 1.5 lead-hours and about $4.5 (E: the ticket says about 2 h; a designer worker is about $1 to 3, M).
"""

RUBRIC_ROWS = """| worker | role | class | model | effort | when |
|---|---|---|---|---|---|
| test designer | independent-test-designer | C2 | Opus (`claude-opus-5-5`) | high | step 5: one round on S1-S6 and the three failure lines; a resume for S6's red cases at most once |
| reviewer | none | C2 | | | LITE: no reviewer, no probe; the CTO's scoped run and close |"""

JUD = """
## Judgement rules (if you start a reviewer anyway)
No reviewer is planned: the profile is LITE (an independent test designer, then the CTO's scoped run). If one is ever needed, its brief carries `governance/project/briefs/JUDGEMENT.md` word for word, every finding with its `Ordinary work: yes|no, because ...` and `Consequence: fails open|loses work|other` lines and the fenced `verdict` block, and READY is computed by `verdict.ready` (`""" + TOOLS + """/verdict.py`), never declared by you; but you start none without the CTO: return PACKAGES.
"""

NONGOALS = "Non-goals (the ticket states none; `gov brief`'s NON_GOALS_MISSING): any change to `governance/project/test-map.yaml` or `tests/optin-lifted-breadth.txt` or `src/` (ACT-SELECT-FIXES-1 applied them; a red case that wants one is a discovery, never a fix), W2-66b's file `test_w2_66_live_test_map.py` and the README, the D-10 `tools/` change to the record case (done, `dc5c0fd87278`), `win_toast.ps1`'s placement, a pytest selection run from inside a case, and any merge into `w2/integrate`."

paths = "tests/acceptance/W2-66/test_w2_66_select_fixes.py (one new file; the designer writes it in the tests worktree)"
sources_txt = "DEC-1109, DEC-1112, DEC-1100, DEC-1098, DEC-889, DEC-891, DEC-253, DEC-968, DEC-1061, DEC-896, DEC-912, DEC-1045, DEC-906"
impl = "DEC-1100, DEC-1098, DEC-1109, DEC-1112"
profile = "LITE (C2, test-revision)"
title = "W2-66c: W2-66's live-map suite pins ACT-SELECT-FIXES-1's lines; the tests run, one independent test designer, S1 to S6 and the failure lines"
summary = ("The ticket: a new file of W2-66's suite pins the test map's four couplings (settings and hook wiring, the declared checks, the history rule, W1-50's fixture scan), "
           "W2-66's record-only case in the always-run set (run whole, no opt-in list leaving a row out) and the existence of every coupling target; "
           "tests first: every pinning case red on the map of ACT-SELECT-FIXES-1's parent, green after it.")

head = sub(ASSIGNMENT_HEAD, ID=TID, W2=W2, PROFILE=profile, TITLE=title, SUMMARY=summary, USD="4.5", PATHS=paths)
dod = DOD.replace("@@DOD_NOTE@@", "DOD-4 does not apply: LITE, no review and no probe; DOD-1 is the point: the six success lines hold, shown red on the ACT's parent and green after it; the CTO's scoped run and close follow")
mid = f"""
## What must be true (KPI lines and how each is checked)
{kpi_table_66c()}
{NONGOALS}
{dod}

## Inputs
{MID}
"""
rubric = sub(RUBRIC, RUBRIC_ROWS=RUBRIC_ROWS)
body = (HAND.replace("@@REFUSAL@@", refusal(W2, KIND)) + head + mid + "\n## Commands (copy them as they are)\n" + commands(W2, TID)
        + "\n" + FORMS + "\n" + rubric + RUN + JUD)
body = sub(body, ID=TID, W2=W2, KIND=KIND, IMPL=impl, PROFILE="LITE")
body = finish(body)
rows = ", ".join(ticket(TID)["list_rows"]) or "none"
tail = ("\n\n---\n\n# The common lead brief (committed, `governance/project/briefs/LEAD-w2-common.md`), appended whole\n\n"
        + fill(common(W2, TID, "LITE", paths, rows, sources_txt, impl, "160 lines of code")))
OUT.write_text(body + tail)
print(OUT, len(body + tail))
