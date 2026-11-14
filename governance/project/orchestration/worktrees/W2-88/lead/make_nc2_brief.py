"""Builds briefs/nc-2.md from briefs/nc-1.md (the JUDGEMENT block, word for word) and briefs/run6-interface.md."""
from pathlib import Path

D = Path("/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/briefs")
old = (D / "nc-1.md").read_text().splitlines(keepends=True)
judgement_block = "".join(old[37:63])
assert judgement_block.startswith("## The rules you judge by"), judgement_block[:60]
iface = (D / "run6-interface.md").read_text()
H = "ed568a699e4fa82908fc3f8830e16733a8e7a5c4"
B = "01ec6d2a7"
G = "git -C /home/usain/gov-os-worktrees/W2-88"

text = f"""You are a fresh Independent Auditor, read-only. Ticket: DAEO-2bdu (W2-88, "Memory for any repository"), profile FULL, class C2. Review rounds are spent (round 2, the last, failed; DEC-1010). The first narrow check (`docs/probes/DAEO-2bdu/PR-DAEO-2bdu.md` at 01ec6d2a7) failed on NC-1 (a blocker: a refused A9 record commit still ran `git reset --hard` through W2-23's `project.commit`) and NC-2 (minor). The owner decided P1-W2-88-NC-1 (a): complete the fix in `fabric.py` only, W2-23's `project.commit` and `project.restore` unchanged, then **a narrow independent check of that change only** (DEC-1154's practice; there is no further review round). You are that check. You probe the head **{H}** of branch `w2/W2-88` in `/home/usain/gov-os-worktrees/W2-88`. You write nothing in any repository; your return is your check.

Your budget: about 1 hour.

## Step 0, before any work (report it first in your return)
The sandbox check in the launcher's step-0 file beside this brief. Then `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-2bdu`), `{G} rev-parse HEAD` (expect {H}) and `{G} status --porcelain` (expect empty). If anything differs, stop and say so. Check the head and the empty status again at the end.

## What you judge (only this)
**The change since {B}**: `{G} diff {B} {H}`, which holds the engineer's commit aa476d394d30 (`src/gov/adopt/fabric.py`, `tests/unit/adopt/test_w2_88_nc1.py`), the lead's 5aaff3dd8 (the evidence file's copy-step text), and the test designer's cases 9990563fc8d9 merged at ed568a699e4f (`tests/acceptance/W2-88/test_w2_88_nc1_commit.py`, `standin_nc1/`, `standin_nc2/`, the README's "Run 6 revisions"). Judge it against NC-1's and NC-2's stated behaviour: the first narrow check's record `/home/usain/gov-os-worktrees/W2-88/docs/probes/DAEO-2bdu/PR-DAEO-2bdu.md` (NC-1 and NC-2, each "Behaviour it should have", and the triage table's described behaviours) and the binding interface the pair built to, below. Nothing else of the ticket is re-judged (RV2-1 and RV2-2 were found fixed for every case they named; round 2 passed every other line).

1. **NC-1, fixed or not, probed:** on planted repositories in your TMPDIR, reproduce the first check's case (a `pre-commit` hook that exits 1; an edit to a tracked file and a new file staged during the run; A9's record commit refused) and the interface's other items: no `reset` in the reflog, HEAD and branch unmoved, the edit kept, the staged file kept staged, A9's copies and its record out of the tree and the index (only while still A9's bytes/blob), the folders A9 made removed only when empty, `ADOPT_GIT_FAILED` with `details.exit_code` and git's text naming the hook's refusal; with HEAD moved during the run `HEAD_MOVED` with `cause: "ADOPT_GIT_FAILED"`; an interrupt during the commit; an untracked file at the record's path (`ADOPT_WOULD_OVERWRITE`, the untracked file kept byte for byte, the undo run); a successful commit unchanged (one commit, copies and record). Read the code path from `a9` through `_stage` to the new `commit` step.
2. **NC-2, fixed or not:** an interrupt the moment `install`'s `git add` returns (and where a copy replaced a tracked file) leaves no copy in the index or the tree, status clean.
3. **Fail-open or lost work brought in by the change:** any path where the new step or the changed undo deletes or unstages something A9 did not write or stage (e.g. the blob now compared without the mode; the blob hashed before the add with the repository's filters), leaves A9's copies or record behind on a refusal with HEAD unmoved, swallows a refusal into ok, or turns an interrupt into a silent exit. W2-23's `project.commit` and `project.restore` must be unchanged (`{G} diff {B} {H} -- src/gov/adopt/project.py` empty), and A1 to A8 must still commit through them (`stages.py` unchanged or only A9's call site).
4. **The tests:** do the acceptance cases and the unit tests assert the stated behaviour (not the code's accidents)? Do the README map rows name existing cases?
5. **Scope of the change:** each non-merge commit since {B} changes only the ticket's `allowed_paths` (or, for the test designer, `tests/acceptance/W2-88/`), carries `Task: DAEO-2bdu`, and its `Implements:` lists only ids from the ticket's `sources:` (`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-2bdu.md`).

## What the lead already knows (judge them; do not re-derive the decision)
- The lead's `gov accept W2-88` on {H}: see `/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/accept-6.txt`. The lead's scoped lead_verify runs beside you; its result goes into the record beside your check.
- The interface's process exit for the refusal reads 1 (corrected by the lead after the test designer's reading: `gov.cli.main` gives a refusal exit 1; 2 is argparse's usage error).
- The engineer names three risks: (1) the index mode is no longer compared, only the blob; (2) a copy edited between `hash-object` and `git add` (milliseconds) stays in the index; (3) a successful record commit takes whatever someone staged during the run (the first check's note; the interface keeps it as a named residual). Classify each under the rules below.
- Decided, not to re-open: the copy step at A9 and its files (B-1.1, B-1.3); RV2-1's undo and `HEAD_MOVED` (run 5); the review rounds are spent; the reset that A1 to A8 keep through `project.commit` is the CTO's separate P2 (the owner, 2026-11-13), out of this check.

{iface}
{judgement_block}
## How to probe
- Read freely: the ticket, the register by id (`/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md`), the code, the tests, the workers' logs under `/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/` (eng-5, td-8). Search with the Read and Grep tools (no `gov retrieve`, no `gov context` in the sandbox, DEC-1065); search again once in your own, different words; then answer from both or say "not found".
- Probe by Bash into your own TMPDIR only (DEC-1144 (7)): plant small repositories there and run the head's code with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src`. Every pytest through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with `TMPDIR` your sandbox temp folder, `HOME=/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/empty-home`, `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`. A resource gate's refusal is a wait (DEC-1146). Never `-x`.
- Never write in `/home/usain/gov-os-worktrees/W2-88` or any repository; never run `gov rebuild`, `gov adopt`, `gov close` against a real repository or worktree (on a planted repository in your TMPDIR it is the probe); never touch `~/gov-os-workbench/examin/`; never open the evaluation sets' root or any hidden or memory-verdict folder. Policy 2 (DEC-820): secrets never printed; held-out qualification material's contents never read.
- No shell variable as a write target; no here-document, no backticks, no `bash -c '...'`; no long inline `python3 -c` with braces (keep commands short). Your tool list holds no Write tool: write probe scripts into your TMPDIR with `printf` from Bash (DEC-1144 (7)). **Refused twice for the same call: stop and say so** (DEC-1142 (9)). A refused form is not retried in another disguise.

## Return
One message, your last. The twelve fields first, each a labelled line; then your check in this form (the lead copies it unchanged into the probe record):

```
task: / status: (DONE, with one line) / work_completed: / files_changed: none / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

Then:
- `# W2-88 (DAEO-2bdu): narrow independent check of the NC-1/NC-2 fix` with `probed_commit:`, `base: {B}`;
- `## Sandbox and identity` (step 0, head and status at start and end);
- `## NC-1 and NC-2` (a table: item of the stated behaviour, fixed | not fixed | partly, file:line, how you probed it);
- `## What I probed and found sound` (numbered, each with the command or file:line and the result);
- `## Findings` (new ones: id NC2-n, the KPI line, severity blocker | major | minor, what is wrong, how to reproduce, the behaviour it should have, and the two lines the rules above require);
- `## Notes, not findings`;
- a fenced block tagged `verdict` holding one JSON object, in the rules' form: `{{"kpis": [{{"kpi": "success-3" | "success-16", "verdict": "pass" | "fail", "findings": [{{"id": "NC-n" | "NC2-n", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}}]}}], "overall": "pass" | "fail"}}`, one entry for each of success-3 and success-16 (the lines the change touches).

Refused twice for the same call: stop and say so.
"""
(D / "nc-2.md").write_text(text)
jt = Path("/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/briefs/JUDGEMENT.md").read_text().strip()
print("lines", text.count("\n"), "judgement word for word:", jt in text)
