"""Shared pieces of the hand-built lead briefs (DEC-1130 (1)). Read-only on the repository; the builder writes the four files."""
import re
from pathlib import Path

import yaml

MAIN = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
ORCH = MAIN / ".gov-runtime/scratch/orchestrator"
PREP = ORCH / "drafts/batch-prep"
TOOLS = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools"
WT = "/home/usain/gov-os-worktrees"


def sub(text, **kv):
    for k, v in kv.items():
        text = text.replace("@@" + k + "@@", v)
    return text


def ticket(tid):
    raw = (MAIN / ".tickets" / f"{tid}.md").read_text()
    fm = raw.split("---")[1]
    return yaml.safe_load(fm)


def kpi_table(tid, w2, width=165):
    d = ticket(tid)
    rows = []
    for kind, tag in (("success", "S"), ("failure", "F")):
        for i, line in enumerate(d["kpis"][kind], 1):
            t = " ".join(str(line).split()).replace("|", "/")
            if len(t) > width:
                t = t[: width - 3].rstrip() + "..."
            rows.append(f"| {tag}{i} | {t} | `gov accept {w2}`: the cases its README map names for {tag}{i} |")
    return "| id | line (cut; the ticket file holds the whole line) | verify |\n|---|---|---|\n" + "\n".join(rows)


def refusal(w2, kind):
    t = (PREP / "briefs" / f"{w2}-{kind}.md").read_text()
    t = t.replace("# REFUSED, not a brief:", "### Recorded refusal (not a brief):", 1)
    return t.strip()


def judgement():
    return (MAIN / "governance/project/briefs/JUDGEMENT.md").read_text().strip()


def common(w2, tid, profile, paths, rows, sources, impl, est):
    t = (MAIN / "governance/project/briefs/LEAD-w2-common.md").read_text()
    return sub(t, ID=tid, W2=w2, PROFILE=profile, PATHS=paths, ROWS=rows, SOURCES=sources, IMPL=impl, EST=est)


def commands(w2, tid, tree_note=""):
    T = f"{WT}/{w2}"
    rows = [
        ("identity", "`printenv GOV_ROLE GOV_TICKET`"),
        ("where", f"`git -C {T} rev-parse --show-toplevel --abbrev-ref HEAD`"),
        ("retrieve", '`gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "{QUESTION}"`'),
        ("context", f"`gov context {tid} --role {{WORKER_ROLE}}` (a ceiling refusal: write the worker's brief by hand from its role template and this brief, and say so)"),
        ("launch_worker", f"`env LAUNCH_TREE={{WORKER_TREE}} LAUNCH_TICKET={tid} bash {TOOLS}/launch_worker.sh --class {{CLASS}} --model {{MODEL}} --projection-usd {{USD}} {{WORKER_ROLE}} {{EFFORT}} {{BRIEF_FILE}}` (class, model and effort: the table in 'Your run'; it prints the log, exit file and pid)"),
        ("wait_for", f"`bash {TOOLS}/wait_for.sh {{EXIT_FILE}}` (one call per 9.5 min; it waits on the exit file and asks `proc.sh` by the pid file)"),
        ("stop_a_job", f"`bash {TOOLS}/proc.sh stop <pid>` (or `-<pgid>`); the pid is in the job's `.pid` file"),
        ("merge_integrate", f"`git -C {T} merge --no-ff w2/integrate -F {{MESSAGE_FILE}}` (the message file ends with `Task: {tid}` and `Role: orchestrator`)"),
        ("tests_worktree", f"`git -C {T} worktree add {T}-tests -b w2/{w2}-tests HEAD`"),
        ("merge_tests", f"`git -C {T} merge --no-ff w2/{w2}-tests -F {{MESSAGE_FILE}}`"),
        ("accept", f"`gov accept {w2} --root {T}`"),
        ("rebuild", f"`env PYTHONPATH={T}/src bash {TOOLS}/rebuild_slot.sh {T}`"),
        ("lead_verify", f"`bash {TOOLS}/lead_verify.sh {T} {w2} {tid}`"),
        ("disk_gate", f"`bash {TOOLS}/disk_gate.sh`"),
        ("keyword_warn", f"`python3 {TOOLS}/keyword_warn.py {T}`"),
        ("hooks_check", "`test ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks/pre-commit`"),
        ("tests_worktree_remove", f"`git -C {T} worktree remove {T}-tests`"),
        ("context_ceiling", f"`gov context {tid} --json`"),
        ("links", "`gov links --since {BASE}`"),
        ("scratch", f"`du -sh {T}/.gov-runtime/scratch` and `du -s --inodes {T}/.gov-runtime/scratch`, and the same two for `/tmp/gov-os-lead-{w2}`"),
    ]
    return "| name | command |\n|---|---|\n" + "\n".join(f"| {a} | {b} |" for a, b in rows)


ASSIGNMENT_HEAD = """# Your assignment
You are a fresh orchestrator session. Your role's rules are in your system prompt (template `role-lead`); this brief gives this assignment's facts.
Ticket @@ID@@ (@@W2@@), profile @@PROFILE@@. Objective: @@TITLE@@. @@SUMMARY@@
projection_usd: @@USD@@

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/@@W2@@ |
| branch | w2/@@W2@@ |
| allowed paths | @@PATHS@@ |
| ticket file (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/@@ID@@.md |
| your scratch | /home/usain/gov-os-worktrees/@@W2@@/.gov-runtime/scratch/ |
| the CTO's tools | /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools |
"""

DOD = "Done when: the DoD lines DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6 hold for your part (@@DOD_NOTE@@)."

FORMS = """Ask memory first: `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<which decision governs X | where is Y implemented>"` (the integration store; a worktree has no store of its own, DEC-1092 (1)); read a decision's text in `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` by its id. Search again once: if the bundle does not answer, or your answer may be incomplete, ask once more in your own, different words; then answer from both bundles with path and lines, or say "not found". Two searches in all. The store holds integrate's head, so its line numbers are integrate's: read the file in your own worktree before relying on a line.
Every whole-folder pytest run adds `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty `HOME`: `env HOME=/home/usain/gov-os-worktrees/@@W2@@/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/@@W2@@/src python3 -m pytest {FOLDER} -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"` [DEC-1065]. Never the full suite (DEC-968).
No merge inside a sandbox: you merge outside it; a restore or conflict resolution in `tests/acceptance/` is a test designer's, and that merge carries `Role: independent-test-designer` (DEC-1052, DEC-1031 item 3).

## Forms that work (the guard and the harness accept these)
- Write and edit files with the Write and Edit tools and absolute paths. One simple command per Bash call; no `cd ... &&` chains (use `git -C <dir>` or full paths); no here-documents, backticks or `$(...)` as a write target; anything longer than one line goes in a script file under `/home/usain/gov-os-worktrees/@@W2@@/.gov-runtime/scratch/` (Write tool), run with `bash <file>` or `python3 <file>`.
- The harness allows these headless without asking: Bash, Read, Edit, Write, Grep, Glob. For anything else use a script file as above, or report it; never retry another form.
- **Waits and stops by pid only (L-0075, DEC-1073 (4)):** wait for a job with `wait_for.sh <exit file>`; stop one only with `proc.sh stop <pid>` or `-<pgid>` from its `.pid` file. Never `pgrep`, `pkill`, `killall`, a `ps | grep` name match, and never the Monitor tool (the guard refuses it).

## Commit (your paths only)
```
git commit -m "{SUBJECT}" --trailer "Task: @@ID@@" --trailer "Role: orchestrator" --trailer "Implements: @@IMPL@@" -- {COMMIT_PATHS}
```
- Commit **only on your own branch `w2/@@W2@@` in your own worktree**. No commit on `w2/integrate` or in the main tree, no push, no merge into `w2/integrate` (the CTO merges and closes).
- A worker's commit carries its own `Role:`; `Task:` is the ticket's id (@@ID@@, a `DAEO-...` id), never a W2 id [DEC-182]. `Implements:` lists only ids from the ticket's `sources:`, each ACCEPTED [DEC-927]. An id you need that is not in `sources:` goes in `discoveries`, never into `Implements:` alone [DEC-1073]. Cite only ACCEPTED decisions as rules; name a PROPOSED one "proposed" [DEC-1073].
- **Merges of `w2/integrate` into your branch** carry `Task: @@ID@@` and `Role: orchestrator` (a message file, since `git merge` takes no `--trailer`), are never `-s ours`, never resolve a conflict by dropping the ticket's side, and never remove what git's own merge keeps [DEC-750, DEC-754].
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` (your briefs, logs, records, every worker's return) write commit hashes as 12 digits, never the full 40, and never write the keywords of the secrets rule that takes a bare 40-hex string; run `keyword_warn.py` before your verification. (A committed probe record's `probed_commit` is the one place the full id belongs: it lives under `docs/`, not `.gov-runtime/`.)
- **Scratch budget (DEC-898):** you and all your workers together 20 GB and 1,000,000 files and folders outside the tracked tree; `TMPDIR` for every run at most `/tmp/gov-os-lead-@@W2@@`; give `du -sh` and `du -s --inodes` of it and of your scratch in `evidence`; clean as you go; name what you cannot remove.

## Return (your last message; nothing else is read)
The twelve fields first, each a labelled line ("none" where nothing), then each section below, always present:
```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
template: role-lead@1.0.0
commits: <hash12> <subject> | Task/Role/Implements as committed
brief_gaps: none | - <what was missing> | <where it belonged: template, facts, ticket, tool> | <minutes, est.>
guard_refusals: none | - <time> | <the command's form, one line> | <the rule's reason as the hook gave it> | true or false-positive [DEC-958]
```
Refused twice for the same call: stop and say so. Never work around a refusal: report it.
Status is one of DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED, AUTH_REQUIRED. Say, per worker, its model, effort and class as launched, whether its brief told it to use `gov retrieve` and whether its log shows it did, and its tripwire result.
"""

HAND_NOTICE = """# HAND-BUILT lead brief: @@W2@@ (@@ID@@), run @@KIND@@ (DEC-1130 (1))

`gov brief lead @@W2@@ --run @@KIND@@` refuses this ticket today: a reviewed ticket in progress has KPI lines with no `Verify:` text. DEC-1130 (1) (the owner's exception to DEC-1083, for tickets in progress only) lets it launch on a hand-built brief with the refusal recorded in the brief. This brief takes the form `gov brief` produces (template `brief.md`, role template `role-lead`, the facts file `governance/project/facts.yaml`), then the ticket's own run section, then the committed common lead brief, appended whole (prompt section 15). Where the common text and the facts file's steps differ, this part holds: the steps `trailer_gate`, `collect_only` and `checkpoint_record` are off (facts.yaml `steps`: DEC-1057, DEC-953 item 1); `keyword_warn`, `hooks_check`, `scratch_measure`, `context_ceiling` and the guard-refusal lines are on. A hand-built brief is not checked by `gov brief`: the CTO reads it before launch.

## What `gov brief` said (recorded, DEC-1130 (1))

@@REFUSAL@@

The KPI table below carries each line's `Verify:` as the one command that measures it (`gov accept`, read from the README map): the ticket file itself is not edited by this brief.

---

"""

RUBRIC = """## Model, effort and class by RUBRIC-2 (DEC-1120 (3)) for each worker you start
Every `launch_worker.sh` call names its class, model and effort; there is no default. A spawn after two failed rounds or a fail-open finding is a promotion, named with `--promoted "<reason>"` (DEC-1120 (3)); you do not promote on your own: return PACKAGES.
@@RUBRIC_ROWS@@
You yourself run as lead on Opus at high. The tools: `--model claude-opus-5-5` for Opus, `--model claude-sonnet-5-5` for Sonnet.
"""
