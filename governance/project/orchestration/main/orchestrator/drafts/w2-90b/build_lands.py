"""Builds the two hand-built land briefs of 2026-11-11 ~20:30 (DEC-1130 (1)): W2-81-A5-r6-land.md and W2-90b-A5-r2-land.md,
in .gov-runtime/scratch/orchestrator/briefs/. It reuses the shared pieces of drafts/batch-prep/hand/tmp/parts.py and fills
every slot that builder left open ({ID}, {W2}, ... of LEAD-w2-common.md, and the command table's {QUESTION}, {EXIT_FILE}, ...).
Read-only on the repository; it writes only the two briefs. Run: python3 -I build_lands.py"""
import re
import sys
from pathlib import Path

sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/batch-prep/hand/tmp")
import parts  # noqa: E402
from parts import ASSIGNMENT_HEAD, DOD, FORMS, HAND_NOTICE, MAIN, RUBRIC, TOOLS, WT, kpi_table, sub  # noqa: E402

HERE = Path(__file__).resolve().parent
BRIEFS = parts.ORCH / "briefs"
NAMES = ("identity", "where", "hooks_check", "rebuild", "disk_gate", "accept", "lead_verify", "launch_worker", "wait_for", "links",
         "keyword_warn", "context_ceiling", "merge_integrate", "tests_worktree", "merge_tests", "tests_worktree_remove", "context")
SLOT = re.compile(r"\{[A-Z][A-Z_]*\}")


def refusal(w2, tid):
    err = (HERE / f"gov-brief-{w2}.err").read_text().strip()
    return (f"### Recorded refusal (not a brief): gov brief lead {w2}-land (live pin pin-797495bdfc70), 2026-11-11 ~20:20 UTC\n\n"
            "Command: `gov brief lead <ticket> --run <kind>` from the main tree (the file name is `<W2>-<kind>`). Exit 1, nothing on stdout. "
            f"Its stderr, copied:\n\n```\n{err}\n```")


def commands(w2, tid, fills, unused):
    """parts.commands() with every slot filled: `fills` maps a slot to its value; `unused` names the rows that this run does not use."""
    table = parts.commands(w2, tid)
    out = []
    for row in table.splitlines():
        m = re.match(r"\| (\w+) \| (.*) \|$", row)
        if m and m.group(1) in unused:
            row = f"| {m.group(1)} | {unused[m.group(1)]} |"
        elif m and m.group(1) in fills:
            row = f"| {m.group(1)} | {fills[m.group(1)](m.group(2))} |"
        out.append(row)
    return "\n".join(out)


def common(w2, tid, profile, paths, rows, sources, impl, est):
    t = (MAIN / "governance/project/briefs/LEAD-w2-common.md").read_text()
    old = ("The orchestrator writes the ticket's own part (why it starts now, the decisions staged for it, this run's order, its probe's focus) before it, "
           "fills `{ID}` (the tk id), `{W2}` (the WBS id), `{PROFILE}`, `{PATHS}`, `{ROWS}`, `{SOURCES}`, `{IMPL}` and `{EST}`, and gives the lead the result.")
    assert old in t, "the common brief's opening sentence changed"
    new = (f"The orchestrator wrote the ticket's own part (why it starts now, the decisions staged for it, this run's order) before it, and filled this text's "
           f"slots for this ticket: the tk id {tid}, the WBS id {w2}, the profile {profile}, the allowed paths, the list rows, the sources, the `Implements:` ids and the estimate.")
    t = t.replace(old, new)
    t = sub_braces(t, {"ID": tid, "W2": w2, "PROFILE": profile, "PATHS": paths, "ROWS": rows, "SOURCES": sources, "IMPL": impl, "EST": est})
    return t


def sub_braces(text, kv):
    for k, v in kv.items():
        text = text.replace("{" + k + "}", v)
    return text


def finish(body):
    for name in NAMES:
        body = body.replace("{" + name + "}", f"(command `{name}`)")
    return body


def commit_section(forms, new):
    start = forms.index("## Commit (your paths only)")
    end = forms.index("- Commit **only on your own branch")
    return forms[:start] + new + forms[end:]


def pytest_line(forms, folder, note):
    old = "`env HOME=/home/usain/gov-os-worktrees/@@W2@@/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/@@W2@@/src python3 -m pytest {FOLDER} "
    assert old in forms, "the pytest line changed"
    new = ("`env HOME=/home/usain/gov-os-worktrees/@@W2@@/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/@@W2@@/src python3 -m pytest "
           + folder + " ")
    forms = forms.replace(old, new)
    marker = "Never the full suite (DEC-968)."
    assert marker in forms
    return forms.replace(marker, marker + " " + note, 1)


def assemble(w2, tid, kind, impl, profile, title, summary, usd, paths, mid_extra, run, rubric_rows, jud, est, sources_txt, dod_note, nongoals,
             fills, unused, forms_new_commit, folder, pytest_note):
    head = sub(ASSIGNMENT_HEAD, ID=tid, W2=w2, PROFILE=profile, TITLE=title, SUMMARY=summary, USD=usd, PATHS=paths)
    dod = DOD.replace("@@DOD_NOTE@@", dod_note)
    mid = f"""
## What must be true (KPI lines and how each is checked)
{kpi_table(tid, w2, width=150).replace(f"`gov accept {w2}`: the cases its README map names for", "the scoped `lead_verify` and the README's per-case rows for") if w2 == "W2-90b" else kpi_table(tid, w2, width=150)}
{nongoals}
{dod}

## Inputs
{mid_extra}
"""
    forms = commit_section(FORMS, forms_new_commit)
    forms = pytest_line(forms, folder, pytest_note)
    rubric = sub(RUBRIC, RUBRIC_ROWS=rubric_rows)
    notice = HAND_NOTICE.replace("@@REFUSAL@@", refusal(w2, tid))
    body = (notice + head + mid + "\n## Commands (copy them as they are)\n" + commands(w2, tid, fills, unused) + "\n" + forms + "\n" + rubric + run + jud)
    body = sub(body, ID=tid, W2=w2, KIND=kind, IMPL=impl, PROFILE=profile.split()[0])
    body = finish(body)
    rows = "none (the ticket's `list_rows` is empty)"
    tail = ("\n\n---\n\n# The common lead brief (committed, `governance/project/briefs/LEAD-w2-common.md`), appended whole\n\n"
            + common(w2, tid, profile.split()[0], paths, rows, sources_txt, impl, est))
    return body + tail


JUD = """
## Judgement rules (if you start a reviewer anyway)
No reviewer is planned in this run. If one is ever needed, its brief carries `governance/project/briefs/JUDGEMENT.md` word for word (read it in your tree after the merge), every finding with its `Ordinary work: yes|no, because ...` and `Consequence: fails open|loses work|other` lines and the fenced `verdict` block, and READY is computed by `verdict.ready` (`""" + TOOLS + """/verdict.py`), never declared by you. The review rounds this ticket's plan declared are used up or not yours to start: return PACKAGES instead.
"""

# =====================================================================================================  W2-81, round 6
W2, TID = "W2-81", "DAEO-l78m"
T81 = f"{WT}/W2-81"
MSG81 = f"{T81}/.gov-runtime/scratch/land/merge-message.txt"
VEXIT81 = f"{T81}/.gov-runtime/scratch/lead/log/verify/verify.exit"
HEAD81 = "4009d597a173"
SRC81 = ("DEC-941, DEC-936, DEC-930, DEC-833, DEC-820, DEC-845, DEC-873, DEC-911, DEC-728, DEC-953, DEC-954, DEC-957, DEC-898, DEC-906, "
         "CAP-03.a, CAP-03.d, CAP-44.b, CAP-44.e, CAP-44.g, CAP-44.h, CAP-44.j")
IMPL81 = "DEC-941, DEC-936, DEC-930, DEC-820, DEC-953, DEC-954, DEC-957"

mid81 = f"""- Sources: DEC-941, DEC-936, DEC-930, DEC-833, DEC-820, DEC-845, DEC-873, DEC-911, DEC-728, DEC-953, DEC-954, DEC-957, DEC-898, DEC-906 (ACCEPTED); DEC-899 is DONE, not a rule; CAP-03.a, CAP-03.d, CAP-44.b, CAP-44.e, CAP-44.g, CAP-44.h, CAP-44.j. Read each by id in /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md, or ask memory (below). Also DEC-997, DEC-1005, DEC-1010 (the rounds), DEC-895 (a re-probe only if a merge changes files the probe judged), DEC-1120 (RUBRIC-2), DEC-1130 (1) (why this brief is hand-built), DEC-1136 (1) and (2) (W1-01's exemption, applied).
- **What the lead knows of the ground** (state as of 2026-11-11 ~20:20 UTC; the CTO's helper read the ticket, the checkpoint, the last return and the git history, not the tests):
  - **State.** `w2/W2-81` is 22 commits ahead of `w2/integrate` and 17 behind (integrate's head `9d288f1b1c49`), head `{HEAD81}`, clean, worktree `{T81}` exists. The deliverable is test code only (37 files, 7,077 added lines, all under `tests/acceptance/W2-81/**` and `docs/`): five synthetic repositories with planted problems, a judge, a scorer, the visible question half, a README. It gates W2-93 (which needs W2-81 *closed*) and, later, W2-88. Its first real run is the CTO's, in W2-27.
  - **Your last return** (round 5, `log/W2-81-A5-r5b-land.json`, PACKAGES at `76c9b5cd1071`): four packages, all answered. **P-W2-81-LAND-1: the CTO accepted `76c9b5cd1071` as the land merge.** It is the merge of `w2/integrate` the CTO made at 18:11 (first parent `e78e6af7530d`, `Task: DAEO-l78m`, `Role: orchestrator`); it is in your branch's history; **do not undo it, redo it or look for it again**: your merge in this run is a second merge of `w2/integrate` on top of it. **LAND-2** (the README map): two test-designer commits did it, `294f3e84bbe7` (four rows' KPI cells now start with the lines they serve) and `{HEAD81}` (four items of S5, S11 and F2 named by full node id), both `Role: independent-test-designer`, `Rewrite-Reason: W2-96 S-D10b ...`, both changing only `tests/acceptance/W2-81/README.md` (measured: 4 + 3 lines). Read-only, the pin's `parse_map` reads all 17 lines (S1 to S12, F1 to F5) from the README now; whether each item meets a collected case is `gov accept`'s to say, and is this run's first measure. **LAND-3** (W1-01): the owner's operator applied ACT-W1-01-EXEMPT-3 (`7b5c3cb94fd9`, `Role: owner`): `6fbe73b1adde` is listed in `acceptance_exemptions`, so W1-01's integration-merge case should now pass for the merges that bring it in. **LAND-4** (the context ceiling): decided: **report the figures, trim nothing** (below).
  - **What integrate did since `76c9b5cd1071`:** 17 commits, 17 files, none under `tests/acceptance/W2-81/` or `docs/probes/DAEO-l78m/` and not `.tickets/DAEO-l78m.md` (measured: `git diff --name-only HEAD...w2/integrate`); they are other tickets' files, the register, `DECISIONS-IN-FORCE.md`, the path map (EXEMPT-3's two lines), two orchestration tools, and DECIDED-NOT-DONE. A read-only `git merge-tree` of the branch with integrate shows **no conflict**; no `src/` file changes.
  - **Open points.** (1) DEC-895: the probe judged only files under `tests/acceptance/W2-81/**` and the ticket; the two designer commits changed the README only, and the merge changes none of the probed files, so **no re-probe** (the probe record `PR-DAEO-l78m-moderated.md` is READY, computed, and unchanged). A conflict, or a merge that touches `tests/acceptance/W2-81/**` or `docs/probes/DAEO-l78m/**`, is PACKAGES. (2) The three record checks (`tests/acceptance/W1-08/test_w1_08_probe.py`, `tests/acceptance/W1-26/test_w1_26_probe_records.py`, `tests/acceptance/W2-02/test_w2_02_green_here.py`) need `GOV_TESTS_OPTIN=lifted,breadth` to give 55 passed (33.7 s on 11-11; by default 8 passed and 47 are deselected, DEC-1061), and an empty `HOME` hides pytest (it lives in the user site): add `PYTHONUSERBASE=/home/usain/.local`. `gov accept` itself takes the normal `HOME` (its child run crashes, exit 4, under an empty one). (3) Six W2-96 cases (`tests/unit/accept/test_w2_96_review3.py`, `test_w2_96_review4.py`, `test_w2_96_run2.py`: the r14, r16 and r9_r12 cases) failed in the last scoped run's parallel phase (worker gw3) and passed alone, 6 in 11.2 s: if they are the only reds, re-run them alone once; if they pass, name them as flaky candidates (DEC-757, DEC-762, DEC-766 are lifted: a red that passes alone is a candidate you name) and the run is not a package. (4) Empty untracked harness folders sit in the tree (`tests/acceptance/W2-81/.claude/`, `tests/acceptance/W2-81/questions/.claude/`: `.cc-writes` markers; git shows them as nothing): name them in your return, never remove them (the guard refuses). (5) EST_LOC_OVER (est 1,200; 7,077 added) is a warning, not a refusal: report the lines against the estimate. (6) `trailer_gate` is off in the facts file; the old note about DEC-1010 and DEC-997 resolving only on integrate's register no longer applies (the register came in with `76c9b5cd1071`). (7) A change to `.tickets/DAEO-l78m.md` that touches only `sources:` lines (W2-130's 9 lines came in with `76c9b5cd1071`) is named in your return, not a stop; any other change to the ticket file is PACKAGES."""

run81 = f"""
## Your run: land, round 6 (only this section is in your brief)
**land**: the branch is verified and its review is done; the queue merges and closes, you never merge into `w2/integrate`. The README map is repaired (two designer commits), W1-01's red is gone, and the CTO accepted the first merge. The land round is: check `gov accept` first, merge integrate in again, verify once, return the new head.
1. First calls: (command `identity`) (expect `orchestrator` and `{TID}`), (command `where`) (expect `{T81}` and `w2/W2-81`); read `{T81}/.gov-runtime/scratch/lead/CHECKPOINT.md` (it exists: its last run section is 'Run 6', PACKAGES at `76c9b5cd1071`; add a 'Run 7 - land round 6' section as you go); `git -C {T81} rev-parse --short=12 HEAD` must be `{HEAD81}` and `git status --short` empty. Anything else: stop and return PACKAGES (a head other than `{HEAD81}` means the CTO or a designer moved the branch after this brief was written; say what `git log --oneline -3` shows).
2. **Before any merge: (command `disk_gate`), then (command `accept`) once on the branch as it is** (not under an empty `HOME`; read the result as pass or fail per line, never a case's source). **It must exit 0.** If it does not (a refusal such as `ACCEPT_MAP_UNREADABLE`, or a line that reads fail or unmeasured): **return PACKAGES at once**, with its output, the README line numbers it names and the line names; no merge, no worker (the fix is a designer's, the CTO orders it). Write its per-line counts into CHECKPOINT.md.
3. Merge `w2/integrate` into the branch: after (command `hooks_check`), write the message file `{MSG81}` with the Write tool, exactly this: the first line `W2-81: merge w2/integrate (land round 6; the second merge, on top of the CTO's accepted 76c9b5cd1071)`, a blank line, then the two trailer lines one under the other, `Task: {TID}` and `Role: orchestrator`; then (command `merge_integrate`). Expect no conflict. A conflict: `git -C {T81} merge --abort` once (if the guard refuses it, leave the tree as it is and say so), then PACKAGES at once with the file list (a conflict in `tests/acceptance/` is a test designer's, DEC-1052; you start none here without the CTO).
4. Check what the merge changed (DEC-895): `git -C {T81} diff --name-only HEAD^1 HEAD`: **none** under `tests/acceptance/W2-81/` or `docs/probes/DAEO-l78m/`; `.tickets/DAEO-l78m.md` only as open point (7) allows. If one is, PACKAGES. Also name the two designer commits' files (`git -C {T81} diff --stat 76c9b5cd1071 {HEAD81}`): expect `tests/acceptance/W2-81/README.md` alone, 8 lines changed.
5. On the merged tree: (command `disk_gate`); (command `accept`) once more (276 cases expected, exit 0); the three record checks alone with `env HOME={T81}/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local GOV_TESTS_OPTIN=lifted,breadth PYTHONPATH={T81}/src python3 -m pytest tests/acceptance/W1-08/test_w1_08_probe.py tests/acceptance/W1-26/test_w1_26_probe_records.py tests/acceptance/W2-02/test_w2_02_green_here.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed` (55 passed expected); then (command `lead_verify`) once in the background and (command `wait_for`) on it (one call per 9.5 minutes; the scoped verification, DOD-2; the selection is expected to hold W2-81's folder and the record cases; the scoped run waits for a heavy slot). A red: name it only from the known-reds list `{TOOLS}/skip_known.json` or open point (3); re-run a load-sensitive case alone once; W1-01's integration-merge case is expected green now: if it is red, name the commit it names and return PACKAGES; a red your merge caused, or any other red you cannot name: PACKAGES with the output. Start no worker; the branch has no open round and you write no file under `tests/`.
6. Before you return: (command `links`) (`gov links --since {HEAD81}`, first line quoted in `evidence`), (command `keyword_warn`), (command `context_ceiling`) once: **P-W2-81-LAND-4 is decided: a ceiling refusal (CONTEXT_OVER_CEILING; 23,037 of 6,000 tokens on 11-11) is reported as figures only, in `evidence`; you trim nothing, edit no ticket file and write no package for it** (DEC-1027), the scratch measures, CHECKPOINT.md rewritten with the new head, `git status --short` empty. Return DONE with the exact head you verified (12 digits), both `gov accept` runs' counts, the record checks' and the scoped run's counts, a line saying no review ran, the `gov.__file__` line, the lines against the estimate, and the empty harness folders named.
Estimated at 1.5 lead-hours and about $4 (E: its resumes were 1.7 to 1.9 h and $3.3 to 4.3; the r5 land round was about 0.8 h and $2.2, M).
"""

commit81 = """## Commit (this run's one commit is the merge)
This run makes **one commit: the merge of step 3**, with the message file given there (trailers `Task: DAEO-l78m` and `Role: orchestrator`; `git merge` takes no `--trailer`). You write no other commit and no file under `tests/`; CHECKPOINT.md and the other scratch files are untracked and are not committed.
"""

b81 = assemble(W2, TID, "land", IMPL81, "FULL (C2)", "The adoption proving ground (W2-81): the land round 6, `gov accept` first, integrate merged in again, the verification repeated once",
               "The ticket: five synthetic repositories built at test time with planted problems whose handling is known, controls against over-flagging, a judge, "
               "a scorer, mutation tests of the judge, per-repository question sets (the visible half here, the hidden half is W2-93's), one command for the real run "
               "(the CTO's, in W2-27), and a hermetic, bounded suite. Test code only, under `tests/acceptance/W2-81/**`.",
               "4", "tests/acceptance/W2-81/** (you write none: this run writes only under your scratch and the merge commit)",
               mid81, run81,
               """| worker | role | class | model | effort | when |
|---|---|---|---|---|---|
| none planned | | C2 | | | a red or a conflict is PACKAGES; a repair is the CTO's to order (Opus at high for a designer on this C2 ticket) |""",
               JUD, "1200 lines of code (7,077 added: EST_LOC_OVER)", SRC81,
               "DOD-4 holds from the earlier rounds: the probe record `PR-DAEO-l78m-moderated.md` is READY (computed); you add no review",
               "Non-goals (the ticket states none; `gov brief`'s NON_GOALS_MISSING): the hidden question half (W2-93's, an independent auditor's), the real run and its report (the CTO's, W2-27), any new case or fix in this run, and any merge into `w2/integrate`.",
               fills={
                   "retrieve": lambda c: c.replace("{QUESTION}", "<your question, in words>"),
                   "wait_for": lambda c: c.replace("{EXIT_FILE}", VEXIT81),
                   "merge_integrate": lambda c: c.replace("{MESSAGE_FILE}", MSG81),
                   "links": lambda c: c.replace("{BASE}", HEAD81),
               },
               unused={n: "not used: this run starts no worker (a repair is the CTO's to order)" for n in
                       ("context", "launch_worker", "tests_worktree", "merge_tests", "tests_worktree_remove")},
               forms_new_commit=commit81, folder="tests/acceptance/W2-81",
               pytest_note="(W2-81's own folder is judged by `gov accept`, not by this form; the record checks in 'Your run' step 5 use their own opt-in form.)")
(BRIEFS / "W2-81-A5-r6-land.md").write_text(b81)
print("W2-81-A5-r6-land.md", len(b81))

# =====================================================================================================  W2-90b, round 2 (land)
W2, TID = "W2-90b", "DAEO-nqa2"
T90 = f"{WT}/W2-90b"
MSG90 = f"{T90}/.gov-runtime/scratch/land/merge-message.txt"
DBRIEF = f"{T90}/.gov-runtime/scratch/lead/briefs/designer-merge.md"
DEXIT = f"{T90}/.gov-runtime/scratch/lead/log/designer-merge.exit"
VEXIT90 = f"{T90}/.gov-runtime/scratch/lead/log/verify/verify.exit"
HEAD90 = "73c18fea1e1f"
SRC90 = "DEC-965, DEC-970, DEC-966, DEC-953, DEC-906, DEC-1016, DEC-999, MR-3, DAEO-0mtg"
IMPL90 = "DEC-953, DEC-965, DEC-970, DEC-906, DEC-999"
RES = (HERE / "RESOLUTION.md").read_text()
res_body = RES[RES.index("## The resolution, file by file"):RES.index("## Found while reading")].strip()

mid90 = f"""- Sources: DEC-965, DEC-970, DEC-966, DEC-953, DEC-906, DEC-1016, DEC-999 (ACCEPTED), MR-3 and DAEO-0mtg (a ticket id the ticket lists as a source and as its dependency). Read each by id in /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md, or ask memory (below). Also DEC-1022 item 2 (P-W2-90b-1 answered), DEC-1052 and DEC-1031 item 3 (a conflict in `tests/acceptance/` is a test designer's; the merge carries `Role: independent-test-designer`), DEC-1088 (5) (every `gov launch` passes the gate), DEC-866, DEC-1120 (RUBRIC-2), DEC-1130 (1) (why this brief is hand-built).
- **What the lead knows of the ground** (state as of 2026-11-11 ~20:20 UTC; the CTO's helper read the ticket, the checkpoint, the last return and the git history, and ran a read-only merge test; it did not run the suites):
  - **State.** `w2/W2-90b` is 6 commits ahead of `w2/integrate` and 1,860 behind (merge base `8723754f3fec`; integrate's head `9d288f1b1c49`), head `{HEAD90}` (a records commit, `CP-DAEO-nqa2-0004`, on the verified head `d2408361d185`), clean, worktree `{T90}` exists. The work is done and verified (your last return, `log/W2-90b-A5-run1-ten.json`, PACKAGES with one package): the cases tied to this repository's live wiring now judge the kernel's wiring (W1-33's four, W1-05's two setup errors, W2-54's sandboxed worker, W2-59's and W2-65's guard and post-tool ids with the 14 restored ids), the stand-in homes hold the editable install's `gov`, and `tests/acceptance/W2-90b/README.md` maps every case. Nothing is lowered. Four cases went to W2-90c because they need W2-105.
  - **P-W2-90b-1 is answered** (DEC-1022 item 2, commit `3a4203e56` on integrate): option (b), S4 for W1-46's live sessions and W1-50's freeze launcher is re-baselined under DEC-822 item 3 and sits in W2-90c; nothing waits on it.
  - **The merge is not clean.** A read-only `git merge-tree --write-tree --name-only w2/W2-90b w2/integrate` exits 1: **three conflicts, all in acceptance files:** `tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py`, `tests/acceptance/W1-47/w1_47_support.py`, `tests/acceptance/W2-90/w2_90_kernel_wiring.py`; three more files changed on both sides and merge cleanly (`tests/acceptance/W2-54/test_w2_54_sandboxed_worker.py`, `tests/acceptance/W2-59/test_w2_59_hook_lines_worker_env.py`, `tests/acceptance/W2-90/README.md`). Integrate fixed the same two problems this branch fixed (the pinned `gov` in a stand-in home: W2-20 D-10's `plant_pinned_gov`; and W1-33's launcher needing an open resource gate, DEC-1088 (5)) in its own way. **Only a test designer resolves them**, and the merge carries `Role: independent-test-designer` (DEC-1052, DEC-1031 item 3). The resolution is written out below ('The designer's job'); the CTO's helper prepared it from the three hunks and both sides' commits (`3a1be7726`, `5b6873b3a`, `e66c69c45` on integrate; `591199ea1`, `7ce46d8b3` on this branch).
  - **Open points.** (1) The four W2-90c cases (W1-05 `test_an_install_by_the_orchestrator_asks_the_owner[pip install requests]` and `[npm install -g ccusage]`; W1-46 `test_a_research_install_inside_the_experiment_folder_is_let_through[npm-install]`; W1-33 `test_an_install_asks_for_the_orchestrator_and_is_denied_to_every_other_role[orchestrator]`) need W2-105 (the template's two install denies removed); W2-105 may not be merged yet: if they are red, they are the four named in the README, not a package. (2) Four `tests/unit/launch/test_runs.py` cases fail whenever the temp path contains `W2-90` (measured on the last run; `/tmp/gov-os-lead-W2-90b` does): re-run those four alone once with `env TMPDIR=/tmp`; if they pass, name them as this known residual and the run is not a package. (3) The serial phase of the last run waited 80 minutes for a heavy slot and hit the Bash tool's two-hour limit: `lead_verify` now runs only the selected serial entries, in the background; wait on it with `wait_for` in 9.5-minute calls and never in the foreground. (4) No rebuild is planned: the last one took 63 minutes and no selected case reads the store; run it only if a selected case answers `STORE_MISSING`. (5) `gov accept W2-90b` is **not** a measure for this ticket: its folder holds only the README (no case; the ticket is judged on the suites it revises, DEC-892) and the pin's map reader reads 0 lines from that README (`ACCEPT_NO_MAP`); do not run it, and say so in `discoveries`. (6) W1-19's warm p95 case fails alone under load (DEC-1134 names it; the owner's ACT-ACCEPTED-REDS-1 is pending): name it from `skip_known.json` or DEC-1134 if it appears. (7) LITE: no probe and no reviewer. (8) The guard may refuse the designer's launch with a merge in progress, or its tripwire may flag the merge's own files: then PACKAGES (the CTO makes the merge by hand and starts the designer)."""

DESIGNER_JOB = f"""
## The designer's job (copy it into the designer's brief, from the role template `template/governance/kernel/templates/role-test-designer.md` of your tree, and add the standing lines below)
You are the independent test designer for ticket {TID} (W2-90b), resolving the merge of `w2/integrate` into this branch in {T90}: the merge is **in progress** (`git merge --no-ff --no-commit w2/integrate` stopped on three conflicts). Edit **only** the three conflicted files below and the two README paragraphs named at the end; run **no git command that writes** (no `git add`, `commit`, `merge`, `checkout`, `reset`, `stash`): the lead stages and commits. Nothing is lowered: no case deleted, skipped, xfailed or weakened (ticket S5 and F2); both sides' intent is kept; never `-s ours`, never drop this branch's side.

{res_body}

Standing lines for the designer's brief (word for word from the common lead brief): DEC-732 (this worktree's own `src/`, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-90b/src` per command, `gov.__file__` shown); DEC-836, DEC-1092 (1), DEC-860, DEC-859 (use `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>"` for what you need, search again once, small targeted questions); P-R1 (drop unread any `gov retrieve` result under the ticket's implementation paths: there are none here, the ticket is tests only; name any you were served); DEC-849 (take a read refusal, never look for another form; count them); DEC-820 (c) and (d) and the hidden-half rule (never open `~/gov-os-eval`, `~/gov-os-runs`, any folder named `hidden` or `memory-verdict`); the guard's five rules; the Write and Edit tools for file changes; no `cd ... &&` chains. It checks its own result with `grep -c '<<<<<<<'` on each file (must be 0), `python3 -I -m py_compile` on each file, and a collect-only of the three files with the tree's `src` (`env PYTHONPATH={T90}/src python3 -m pytest <the three files> --collect-only -q -p no:cacheprovider`: no collection error). It runs no suite. It returns the twelve fields, naming per file what it kept from which side.
"""

run90 = f"""
## Your run: land, round 2 (only this section is in your brief)
**land**: the branch is verified, there is no review (LITE), the queue merges and closes: you never merge into `w2/integrate`. Because integrate moved 1,860 commits and three acceptance files conflict, the land round is: confirm, start the merge, have a test designer resolve the three files, commit the merge as the designer's, verify once, return the new head.
1. First calls: (command `identity`) (expect `orchestrator` and `{TID}`), (command `where`) (expect `{T90}` and `w2/W2-90b`); read `{T90}/.gov-runtime/scratch/lead/CHECKPOINT.md` (it exists: its 'What a resume must do' says nothing more in this ticket and to land the verified head with the records commit; add a 'Run 2 - land' section as you go); `git -C {T90} rev-parse --short=12 HEAD` must be `{HEAD90}` and `git status --short` empty. Anything else: stop and return PACKAGES.
2. (command `disk_gate`); (command `hooks_check`); then start the merge **without committing it**: `git -C {T90} merge --no-ff --no-commit w2/integrate` (the commit is step 5's; it is `{T90}`'s own tree, never the main tree). Expect exactly the three conflicted files above and no other. A different set, or a conflict in a file outside this ticket's `allowed_paths`: `git -C {T90} merge --abort` once (if the guard refuses it, leave the tree and say so), then PACKAGES with the list.
3. Write the designer's brief by hand with the Write tool to `{DBRIEF}` (the section 'The designer's job' below, with the role template and the standing lines), then start the designer (command `launch_worker`; class C2, Opus, high; the table in 'Your run' below) and wait on it (command `wait_for`, designer's exit file; one call per 9.5 minutes). A refusal of the launch because a merge is in progress, or a sandbox or tripwire refusal that names the merge's own files: `git -C {T90} merge --abort` once, then PACKAGES (open point 8).
4. When it is done, check what it left (you write nothing in `tests/`): `git -C {T90} status --short` shows the merge's staged files and, unstaged, the designer's edits to **only** the three files, `tests/acceptance/W2-90b/README.md` and `tests/acceptance/W2-90/README.md`; `grep -c '<<<<<<<'` on the three files is 0; in each of the three files the number of `def test_` lines and of `@pytest.mark.parametrize` lines is at least that of each side (`git -C {T90} show {HEAD90}:<file>` and `git -C {T90} show w2/integrate:<file>`); `kernel_launch` in W1-33 now plants the open gate and the not-a-worker case takes `ready`; `install_editable_gov` and `EDITABLE_PYTHON` are gone or marked superseded and nothing calls them. Anything off: send it back once (a second worker only on the CTO's word); still off: PACKAGES with the diff.
5. Commit the merge: `git -C {T90} add` the files the designer changed (the three files and the two READMEs, by path), write the message file `{MSG90}` with the Write tool (first line `W2-90b: merge w2/integrate (the pinned gov and the open gate come from integrate; the kernel wiring stays)`, then a blank line, then the trailers `Task: {TID}`, `Role: independent-test-designer`, `Rewrite-Reason: DEC-953 item 2 (the merge keeps integrate's plant_pinned_gov and open gate, W2-106 and DEC-1088 (5))`, `Implements: {IMPL90}`), and `git -C {T90} commit -F {MSG90}`. `git status --short` must then be empty. Check the designer's own commit (if it made any) and this one carry `Task`, `Role` and `Implements:` ids from the ticket's sources.
6. Verify once: (command `disk_gate`); (command `lead_verify`) in the background, then (command `wait_for`) on its exit file (one call per 9.5 minutes; the scoped verification, DOD-2; the selection is expected to hold the revised suites of W1-05, W1-33, W1-46, W1-47, W2-54, W2-59, W2-65 and W2-90; the scoped run waits for a heavy slot). The four W2-90c cases (open point 1), the four `test_runs.py` cases (open point 2, after the alone re-run) and the cases of open point 6 are named, not packages; a red your merge caused (most likely in the six overlapping files or the suites that read support files integrate also changed: `w1_05_support.py`, `w1_46_support.py`, `w2_59_support.py`, `w2_65_support.py`, `w2_54_support.py`) or any other red you cannot name: PACKAGES with the output. Also (the 'Not lowered' check the ticket asks for): `--collect-only -q` of the revised files gives at least the ids of the starting head's.
7. Before you return: (command `links`) (`gov links --since {HEAD90}`, first line quoted in `evidence`), (command `keyword_warn`), (command `context_ceiling`) once (a ceiling refusal: **report the figures only, trim nothing, write no package for it**, as the CTO decided for W2-81, DEC-1027), the scratch measures, CHECKPOINT.md rewritten with the new head, `git status --short` empty, the designer's untracked scratch named. Return DONE with the exact head you verified (12 digits), the scoped run's counts and JUnit paths, the named reds with the proof for each, a line saying no review ran and no `gov accept` was run (open point 5), the `gov.__file__` line, and the lines against the estimate of 300.
Estimated at 1.5 to 2 lead-hours and $4, plus the designer, one round, 20 to 40 minutes and $3 to 5 (E: this ticket's first designer round was one round, four commits; its lead run was 6.1 h of which the rebuild and the slot waits were most, M).
"""

commit90 = f"""## Commit (this run's one commit is the merge)
This run makes **one commit: the merge of step 5**, in the worktree `{T90}`, from the message file given there. Its role is `Role: independent-test-designer` and not `Role: orchestrator`, because a test designer resolved its conflicts in acceptance files (DEC-1052, DEC-1031 item 3; W1-01's DEC-253 rule judges a merge's own changes by its role). You write no other commit and no file under `tests/`; CHECKPOINT.md and the other scratch files are untracked.
"""

b90 = assemble(W2, TID, "land", IMPL90, "LITE (C2)", "W2-90b: the cases tied to this repository's live wiring move to the kernel's wiring; the land round 2, integrate merged in with a designer resolving three acceptance conflicts",
               "The ticket: a test revision (no implementation) moving W1-33's, W1-05's, W1-46's, W2-54's, W2-59's and W2-65's wiring-bound cases onto the kernel's wiring "
               "(the template with its install block removed and its hook lines pinned), the 14 dropped ids restored, the stand-in homes holding the editable install's gov, nothing lowered, "
               "and a README that maps every case; the four cases needing W2-105 go to W2-90c.",
               "5", "the ticket's `allowed_paths` (tests only: W1-05, W1-33, W1-46, W1-47, W1-50, W2-54, W2-59, W2-65, W2-90 and W2-90b files named in the ticket file); this run writes only the merge commit, and a test designer writes the three conflicted files",
               mid90 + "\n" + DESIGNER_JOB, run90,
               f"""| worker | role | class | model | effort | when |
|---|---|---|---|---|---|
| test designer | independent-test-designer | C2 | Opus (`claude-opus-5-5`) | high | step 3 only: the three conflicted acceptance files, in this tree, one round; a second round only on the CTO's word |
| product-spec, engineer, reviewer | | | | | none |""",
               JUD, "300 lines of code", SRC90,
               "LITE: no probe and no review (DOD-4 does not apply); DOD-2 is the scoped verification; `gov accept` is not a measure here (open point 5)",
               "Non-goals (the ticket states none; `gov brief`'s NON_GOALS_MISSING): the four W2-90c cases and everything that needs W2-105 or W2-110, W1-46's live sessions and W1-50's launcher case (DEC-1022 item 2), any case body changed beyond the three files' conflict resolution, and any merge into `w2/integrate`.",
               fills={
                   "retrieve": lambda c: c.replace("{QUESTION}", "<your question, in words>"),
                   "context": lambda c: c.replace("{WORKER_ROLE}", "independent-test-designer"),
                   "launch_worker": lambda c: (c.replace("{WORKER_TREE}", T90).replace("{CLASS}", "C2").replace("{MODEL}", "claude-opus-5-5")
                                               .replace("{USD}", "5").replace("{WORKER_ROLE}", "independent-test-designer").replace("{EFFORT}", "high")
                                               .replace("{BRIEF_FILE}", DBRIEF)),
                   "wait_for": lambda c: c.replace("{EXIT_FILE}", DEXIT + "` for the designer, `" + VEXIT90 + "` for `lead_verify`"),
                   "merge_integrate": lambda c: f"`git -C {T90} merge --no-ff --no-commit w2/integrate` (conflicts in three acceptance files expected; the commit is `git -C {T90} commit -F {MSG90}` in step 5)",
                   "links": lambda c: c.replace("{BASE}", HEAD90),
               },
               unused={n: "not used: no tests worktree in this run (the designer works in the merge's own tree)" for n in
                       ("tests_worktree", "merge_tests", "tests_worktree_remove")},
               forms_new_commit=commit90, folder="tests/acceptance/W2-90b",
               pytest_note="(This ticket's own folder holds only the README; its measure is the scoped `lead_verify`, and a revised suite alone is run only with this form's flags.)")
(BRIEFS / "W2-90b-A5-r2-land.md").write_text(b90)
print("W2-90b-A5-r2-land.md", len(b90))

for name in ("W2-81-A5-r6-land.md", "W2-90b-A5-r2-land.md"):
    t = (BRIEFS / name).read_text()
    left = sorted(set(SLOT.findall(t)) | set(re.findall(r"\{W2\}|\{[A-Z][A-Z0-9_]*\}", t)))
    print(name, "non-empty:", bool(t.strip()), "| slots left:", left)
