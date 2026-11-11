"""Builds the three FULL-review briefs from review_template.md, the tickets' own KPI lines and JUDGEMENT.md (word for word).

Usage: python3 -I build_briefs.py <W2-112|W2-149|W2-148>   (reads the main tree read-only; writes the brief under briefs/)
"""
import re
import subprocess
import sys
from pathlib import Path

import yaml

MAIN = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
ORCH = MAIN / ".gov-runtime/scratch/orchestrator"
TMPL = ORCH / "drafts/probes-batch/tmp/review_template.md"
HEAD = "7b5c3cb94fd9"


def short(h):
    out = subprocess.run(["git", "-C", str(MAIN), "rev-parse", "--short=12", h], capture_output=True, text=True)
    if out.returncode:
        raise SystemExit(f"cannot expand {h}: {out.stderr}")
    return out.stdout.strip()


def expand(text):
    return re.sub(r"@@([0-9a-f]{7,40})@@", lambda m: short(m.group(1)), text)


def ticket(tid):
    text = (MAIN / ".tickets" / f"{tid}.md").read_text(encoding="utf-8")
    front = text.split("---\n", 2)[1]
    return yaml.safe_load(front)


def kpi_lines(front):
    out = []
    for i, line in enumerate(front["kpis"]["success"], 1):
        m = re.match(r"(S\d+)\s", line)
        out.append((m.group(1) if m else f"S{i}", line))
    for i, line in enumerate(front["kpis"]["failure"], 1):
        out.append((f"F{i}", line))
    return out


SPEC = {}

SPEC["W2-112"] = dict(
    ticket="DAEO-clon", wbs="W2-112", cls="C2", estimate="45 to 60 minutes, about $5",
    title="W2-112 (DAEO-clon): FULL review of the shared reranker service's merged code (independent auditor)",
    worktree="/home/usain/gov-os-worktrees/W2-20",
    why_wt="W2-112 has no worktree of its own; W2-20's ticket `DAEO-r30l` carries the CTO's reviews, so the launch names `LAUNCH_TICKET=DAEO-clon` from that tree",
    why_needed="LIFT-CLOSES-1: `gov accept W2-112` gave 59 of 59, but a FULL ticket's close is refused with `PROBE_MISSING` without one, and the ticket was accepted as built in D-1 with no review of its final code",
    diffpaths="src/gov/retrieval src/gov/status tests/unit/retrieval tests/acceptance/W2-112 docs/research/W2-112-shared-reranker.md",
    hotspots="two services started at once (the start lock) or a socket another user can open (the socket's mode and folder, no network port: failure line 2); a search that fails or hangs because of the service (the time limits, a service that dies mid-request, a request over the cap, the service's one thread and its backlog); one session's scores reaching another (S2, failure line 1); the idle end; the memory release (after each answer, never breaking it: judged through F1, S2 and S4); the answers' match to a private reranker's reference (S3, failure line 3); that every fallback is named and `gov status` counts it (S4).",
    tests="`tests/acceptance/W2-112/` (59 cases), `tests/unit/retrieval/test_w2_112_shared_reranker.py` (with `GOV_TESTS_OPTIN=lifted,breadth`: without it four parametrised rows are deselected), `tests/unit/semantic/test_rerank_process.py`, `tests/unit/orchestration/test_gov_reranker_gpu_slot.py` and `tests/unit/status/test_status.py`. The service's real process and its Unix socket run with stand-ins for torch and the model (an earlier review ran them in this sandbox); a case that needs a real model or GPU is left out by the exclusion: name it",
    cto="`gov accept W2-112` at the lift's closes (LIFT-CLOSES-1): 59 passed, 0 failed, 0 skipped, pass, 84 s; cases per line: S1 7, S2 5, S3 3, S4 14, S5 2, S6 13, S7 15, F1 13, F2 7, F3 3",
    specific="""## What has changed, and what has been reviewed before (facts; judge the code, not this history)

- **No earlier review judged the whole ticket's final code.** Two partial reviews existed as scratch, neither committed:
  a round 1 of the original build (2026-11-02; a commit message names its F1, repaired in `@@ed0891667@@`), and a narrow review of the
  DEC-1068 memory release (2026-11-06, at `@@5bf20b532@@`): the service empties the GPU cache after each request and logs the
  allocated and reserved MiB, `@@7448ce364@@`. You judge all ten lines on the head as it is now.
- **Other tickets changed the judged files after those reviews, and are in the head:** W2-137 (`@@8586d60f7@@`, merge `@@213abadc1@@`):
  the request cap raised from 16 to 64 and the service names a request over its bound; W2-145 (`@@86f1af6e5@@`, `@@e6f9bbaff@@`,
  `@@1be3e47de@@`): see the next point; W2-138 (`@@dcda27011@@`: the store's commit and folder in every search result), W2-150
  (`@@28c586930@@`: static import closure, names moved into `gov.util` and `gov.store`), W2-135, W2-32 S7 and S11 in `retrieve.py`
  and `rerank.py`. The acceptance cases were revised after them: `@@aadce89d6@@` (the cases that assumed a private fallback, now
  W2-145's S1 to S4), D-4's cut (55 to 48 cases in the full run), D-10 `@@73e33d7b3@@`.
- **W2-145 amends what S4, S6 and S7 say about a private fallback.** Ticket `DAEO-2tfd` (merged; owner's DEC-1048 (5), DEC-1046 (1),
  DEC-1097 (8)): the shared service is the only reranker; a search it cannot answer stays **unranked and named**
  (`merge.reranked` false with its reason, the fused order kept), never a private reranker on the GPU or the CPU; the service
  holds every reranker GPU slot. The ticket's own words for S4, S6 and S7 were not edited. **The CTO's reading, which you apply:** what
  those lines still demand is that a search never fails or hangs because of the service, that the outcome is named and counted, that
  nothing runs on the CPU, and that the stopgap stays in place (S7's `.pth` and research document section 5). A missing private
  fallback is not by itself a failure of S4, S6 or S7. If you think that reading is wrong, say so in one row; do not fail a line
  on it. W2-145 has its own ticket and review: do not re-review it, use it as context.
- **A known open point, not a finding:** S5's 48-question half (after W2-61h) is not yet measured (D9-FATES: met in part; the
  research document says so under "After W2-61h"). Judge that the document says this plainly and that its other half (memory with
  10 concurrent searches before and after, and the searches' times) is present and consistent with the code; if the document
  misstates either, that is a finding.
- **Rows already carried from the memory-release review** (name one by its description if you meet it independently; it is a row, not
  a new round, unless you show a worse consequence): `rerank.log` is never trimmed and `gov status` reads it whole; a CUDA error
  message spans several log lines; a service that has hit a sticky CUDA error lives on answering only errors.
""",
)

SPEC["W2-149"] = dict(
    ticket="DAEO-52ku", wbs="W2-149", cls="C3", estimate="75 to 100 minutes, about $9",
    title="W2-149 (DAEO-52ku): FULL review of the independent sessions' launch script, merged (independent auditor)",
    worktree="/home/usain/gov-os-worktrees/W2-149",
    why_wt="the ticket's own worktree, on branch `w2/W2-149`",
    why_needed="BATCH-PREP section 2: the ticket is merged but has no `docs/probes/DAEO-52ku/`; it stays `in_progress` by design for rows F37 and F40 and others, and its close, and W2-173 behind it, need the probe of the final code",
    diffpaths="governance/project/orchestration/tools/indep_launch.py governance/project/orchestration/tools/indep-schemas governance/project/indep-walls tests/unit/orchestration tests/acceptance/W2-149 docs/changes/W2-149-evidence.md",
    hotspots="the refusals that must build nothing (S1 to S3 and S18, and the failure lines on a half-built wall a later run could build into after any refusal code); the seed first and drawn by the script (S4 to S6); the tree plain and read-only, and what it leaves out (S7, S23); the canary guarding the settings and the launched command and its environment (S9, S10); no free text from a session reaching `counts.json`, the output or the log (S13, S28); delivery only where the kind and its flow lands, nothing partial, nothing after a stop or a bad result (S14, S16, S24 to S30); the finished wall packed and the hidden file budget (S17, S18); waits and stops by pid (S15, S21); the confined rule script (S25); the overlap auditor's blind (S23, S27)",
    tests="`tests/unit/orchestration/test_w2_149_indep_launch.py` and `tests/unit/orchestration/test_w2_149_setup_a.py`, and `tests/acceptance/W2-149/` (with `GOV_TESTS_OPTIN=lifted,breadth`). The cases that need `bwrap` skip or fail in the sandbox if it is missing or blocked: name which. The three live cases (S9 live canary both ways, S11, S12) need a real `claude` and are the CTO's: never run them, and never run a real `claude`. **Every probe uses planted roots (HOME, sets root, repository) under your `TMPDIR` and a stub `claude`; never `~/gov-os-eval`, `~/gov-os-runs/indep`, `~/gov-os-wall-trees` or the real `~/.claude`** (a failure line of this ticket)",
    cto="`gov accept W2-149` at the last merge, in the declared form with the `bwrap` opt-in, outside the sandbox: pass, 206 passed, 0 failed, 3 skipped (live); with every opt-in 362 passed; unit 153 passed; the 3 live cases passed (haiku, planted roots). The script's sha256 starts `90b943aef8be`, `kinds.yaml` `ddd84ae25910`, `tree-exclude.txt` `e8395088167e` (check them)",
    why_diff="",
    specific="""## What has changed, and what has been reviewed before (facts; judge the code, not this history)

- **No single review judged the final code against all of S1 to S31.** The ticket was reviewed in pieces, each READY by `verdict.py`
  (scratch records, none committed): round 1 (head `@@8d4569bfef3c@@`, S1 to S21; one blocking finding, repaired) and round 2
  (`@@a929356ea@@`, S1 to S21 pass); the F11 follow-up (`--setting-sources project`, merge `@@ff1865184@@`), narrow; set-up A's
  wiring (merge `@@7f0e71519@@`, review at `@@7df7c35e3@@`, S16 and S20 changed, S22 to S28 added), then the wiring review's F18 to F23
  (merge `@@90c1fea6c@@`, narrow), then F36 and F38 (merge `@@2f98aecbc@@`, narrow), then the ticket's merge `@@b4de529b4@@`. The script
  is now 2,456 lines. S1 to S21 were last judged at `@@a929356ea@@`; most of the script's current behaviour (set-up A, the confined
  rule script, the blinded disputes, the delivery checks) has only been judged narrowly. **Judge every line afresh.**
- **Since the last narrow review nothing under the ticket's paths has changed:**
  `git -C $TMPDIR/clone diff --stat @@2f98aecbc@@ HEAD -- governance/project/orchestration/tools/indep_launch.py governance/project/indep-walls governance/project/orchestration/tools/indep-schemas tests/acceptance/W2-149 tests/unit/orchestration/test_w2_149_indep_launch.py tests/unit/orchestration/test_w2_149_setup_a.py docs/changes/W2-149-evidence.md`
  should print nothing (the CTO checked; check it yourself and say so). The template files under `governance/project/indep-walls/`
  other than `kinds.yaml` and `tree-exclude.txt` are ACT-INDEP-WALLS-1's, outside the ticket's paths: reachable context.
- **Known rows, carried (name one by its id if you meet it independently; a row, not a new round, unless you show a worse
  consequence than its record says):** F37 (a round-1 rejection by the rule check logs `rejected rules` without the check's own word,
  so a missing `bwrap` looks like a broken script); F40 (the overlap auditor's blind rests on the excluded places: a later record
  restating the dispute sides elsewhere would bring the tell back; the CTO dry-builds that wall and searches its tree before the
  auditor's first real run); F16 and F17 (Claude Code's `--restricted` already ignores the settings files, so `--setting-sources project`
  is a second guard, and the stub does not model that rule); F2 and F11 of round 2, which went to the owner (the path map's
  `sets_root_hidden` does not cover a new set's `hidden/`, the XCHECK notes or `runs/<audit>/miss-classes.json`: an ACT, an entry
  criterion before the first real writer run). The ticket's notes at its end give each in the ticket's own words.
- **Reading settled by the CTO (ticket, "Readings settled"):** the canary's target is planted in its own temporary folder and added by
  `--add-dir` for the canary only, so only the wall's settings and hook can refuse it; every location other than `--sets-root`
  derives from `HOME`; the brief and template bytes are read with `git show` at `--commit`, never from a working tree.
""",
)

SPEC["W2-148"] = dict(
    ticket="DAEO-xafn", wbs="W2-148", cls="C3", estimate="75 to 100 minutes, about $9",
    title="W2-148 (DAEO-xafn): FULL review of the operator agent's merged code (independent auditor)",
    worktree="/home/usain/gov-os-worktrees/W2-148",
    why_wt="the ticket's own worktree, on branch `w2/W2-148`",
    why_needed="BATCH-PREP section 2: the ticket is merged but has no `docs/probes/DAEO-xafn/`; the CTO found that the scratch reviews are not a valid probe of the final code (below), so this is the fresh FULL review its close needs",
    diffpaths="governance/project/operator tests/unit/operator tests/acceptance/W2-148 docs/changes/W2-148-evidence.md",
    hotspots="every gate failing closed (G1 to G9: S1 to S5, S8, S11 to S13); the classifier on every table row and the class that only rises (S6, S7, S9); the owner's yes read from the transcript and nothing else (S10); the apply, the touched-file check, the control-file after-check and the undo, under DEC-1106's rule (only the ACT's own change is restored; another's live change is left as written, the lock held, a P1 naming the file; S12, S14, S15, S22); the commit freeze and the reference-transaction check in `freeze_gate.py` (S14); the DEC-1131 round count and the failed-line rule (S4); waits and stops by pid, the canary and the wall (S17 to S19); the trial's honesty (S23); the planted roots and the owner's operator untouched (S24)",
    tests="`tests/acceptance/W2-148/` and `tests/unit/operator/` (the ticket's `test_w2_148*` files, plus `test_act_operator_1.py` and `test_dec1131_rounds.py`, which landed after the earlier reviews), with `GOV_TESTS_OPTIN=lifted,breadth`. The unit trial file `tests/unit/operator/test_w2_148_unit_trial.py` may be run: it works on planted folders; check that it does before you run it. **Every probe uses planted operator roots, HOME, repositories and transcripts under your `TMPDIR` and stubs for `claude`, `crontab` and the push channels; never `~/gov-os-operator`, `~/.claude` or the live control files** (a failure line of this ticket)",
    cto="BATCH-PREP: `gov accept W2-148` 166 of 166, then 169 of 169 after the replay check; the trial's counts are in `docs/changes/W2-148-evidence.md`",
    specific="""## What has changed, and what has been reviewed before (facts; judge the code, not this history)

- **No earlier review is a basis for the probe record** (the CTO's check, 2026-11-11). Five reviews exist as scratch, none committed
  and none of the final code: round 1 (head `@@45dd9e2dc@@`, not READY: S6 and S12), round 2 (`@@85a5cf655@@`, not READY: one finding in
  round 2's own fix), a narrow round 3 (`@@1af33c535@@`, DEC-1106 (1) and (3): S12 to S15, S22, F15), a narrow review of DEC-1107
  (`@@0fe71aa8b@@`: S22, F15) and a narrow review of the replay check (`@@24abf75a1@@`, DEC-1108 (2): S15). DEC-1010's two rounds were
  used and the owner gave two exception rounds (DEC-1106, DEC-1107). So **a blocking finding in this review goes to the owner once,
  with options**; say plainly whether anything blocks.
- **The judged files have changed since the last of those reviews.**
  `git -C $TMPDIR/clone diff --stat @@24abf75a1@@ HEAD -- governance/project/operator tests/unit/operator tests/acceptance/W2-148 docs/changes/W2-148-evidence.md`
  shows eight files: ACT-OPERATOR-1 (`@@2a6462653@@`, 2026-11-09: the new `freeze_gate.py`, the reference-transaction check of the commit
  freeze, 174 lines; 8 lines in `operator_run.py`; a new unit test file); a D-10 rename of the unit trial file (`@@a38809a33@@`); and
  ACT-OPERATOR-ROUNDS-1 (`@@6fbe73b1a@@`, 2026-11-11, by the owner's operator, DEC-1131 (3): `verdict.py` and `operator_run.py`: a KPI
  line marked fail blocks READY, and the two-round cap counts per ACT id across its builds; plus a new unit test file). Read
  those changes with the rest. The reference-transaction hook that calls `freeze_gate.py` is installed in the main repository's
  git hooks by that ACT, and the guard's rule closing the install folder is in `.claude/hooks/pretooluse.py` and the path map: control
  paths outside the ticket's paths, reachable context, `scope: out` if one of them is the only place a defect lives.
- **Readings settled by the CTO (ticket, "Readings settled" and the notes):** the yes's marks (S10) are `type: user` with
  `origin.kind: human`, and if a format drops the mark no line counts (fail closed); the landing check's scope (S16) is the commits outside
  a ticket as the landing selection reads them; the agent's session runs from its own wall folder inside `~/gov-os-operator/`, never
  the root; DEC-1106 (1) and (3) override S15's "undoes the ACT" for files that are not the ACT's own, and the commit freeze is
  `install/act-in-progress.txt`; DEC-1108 (2) makes S15's replay check the CTO's call set against the guard's call log by sha256 both ways.
- **Known rows, carried (name one by its id if you meet it independently; a row, not a new round, unless you show a worse
  consequence than its record says):** F3 (the replay's call source: its own ACT), F5, F7 (kept as the package says), F16, F21 to F28 (the owner-undo and recovery paths when files are left; the pushed line's 190-character cut; a freeze
  left by a crash between the claim and the journal; Claude Code's own writes under `.claude/**` during the dry run; the ignored exit
  of `git reset` in `undo_live`), and F30 to F33 (the replay check: a set line with a non-object `event` and a `dropped` mark; a log
  line without `sha256` raising `KeyError`; session ids matched in lower case only; the replay judging each call without its `agent_type`).
""",
)

name = sys.argv[1]
spec = SPEC[name]
front = ticket(spec["ticket"])
lines = kpi_lines(front)
ids = [k for k, _ in lines]
kpi_text = "\n".join(f"- **{k}**: {text}" for k, text in lines)
kpi_text += (
    f"\n\n**The verdict block carries one entry for each of these {len(ids)} ids, in this order:** {', '.join(ids)}. "
    "(`F1` and on are the ticket's failure lines, in the order above.)"
)
allowed = "\n".join(f"- `{p}`" for p in front["allowed_paths"])
judgement = (MAIN / "governance/project/briefs/JUDGEMENT.md").read_text(encoding="utf-8").rstrip("\n")
body = TMPL.read_text(encoding="utf-8")
repl = {
    "TITLE": spec["title"], "CLASS": spec["cls"], "TICKET": spec["ticket"], "WBS": spec["wbs"],
    "WORKTREE": spec["worktree"], "WORKTREE_WHY": spec["why_wt"], "WHY_NEEDED": spec["why_needed"],
    "HEAD": HEAD, "DIFFPATHS": spec["diffpaths"], "KPI_LINES": kpi_text, "ALLOWED": allowed,
    "SPECIFIC": spec["specific"], "JUDGEMENT": judgement, "HOTSPOTS": spec["hotspots"], "TESTS": spec["tests"],
    "CTO_RESULTS": spec["cto"], "ESTIMATE": spec["estimate"],
}
for key, value in repl.items():
    body = body.replace("{{" + key + "}}", expand(value))
left = re.findall(r"\{\{[A-Z_]+\}\}", body)
if left:
    raise SystemExit(f"unfilled: {left}")
out = ORCH / "briefs" / f"{spec['wbs']}-A3-probe.md"
out.write_text(expand(body) if "@@" in body else body, encoding="utf-8")
print(out, len(body), "bytes;", len(ids), "kpi ids")
