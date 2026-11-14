"""Builds briefs/nc-4.md: the narrow re-check of P1-1's fix only (S27), with JUDGEMENT.md word for word."""
from pathlib import Path

D = Path("/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/briefs")
judgement = Path("/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/briefs/JUDGEMENT.md").read_text()
H = "d766514fd651b6b463d628625feee431e9faffd4"
B = "ef9c773c30365081e634d05a9b68c6eb7c4dd446"
G = "git -C /home/usain/gov-os-worktrees/W2-88"
L = "/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log"

text = f"""You are a fresh Independent Auditor, read-only. Ticket: DAEO-2bdu (W2-88, "Memory for any repository"), profile FULL, class C2, run 7 (the reopen under DEC-1164 (18) on DEC-1178 (3)(b) and (4)). The narrow independent check of run 7 at {B[:9]} (`{L}/nc-3.review.md`) passed S24, S25 and S26 and failed S27 on one blocker, **P1-1** (a batch let a secret through that the one-per-file form leaves out). This is **the narrow re-check of P1-1's fix only** (DEC-1154). You probe the head **{H}** of branch `w2/W2-88` in `/home/usain/gov-os-worktrees/W2-88`. You write nothing in any repository; your return is your check.

Budget: about 1 hour.

## Step 0, before any work (report it first in your return)
The sandbox check in the launcher's step-0 file beside this brief. Then `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-2bdu`), `{G} rev-parse HEAD` (expect {H}) and `{G} status --porcelain` (expect empty). If anything differs, stop and say so. Check both again at the end.

## What you judge (only this)
**The change since {B[:9]}**: `{G} diff {B} {H}`: the test designer's revision a4eff2312 (whole-tree copies limited to named paths, DEC-385; merged at e747d1f4e), its P1-1 cases e66a9cb58 (merged at 8e3c3def6), and the engineer's fix d766514fd (`src/gov/secrets/__init__.py`, `tests/unit/secrets/test_w2_88_scan.py`, the evidence file's "Fix 3" and re-measure).
1. **P1-1, fixed or not, probed:** the checker's own reproduction (`{L}/nc-3.review.md`, P1-1: a file ending in a bare generic key, `password:` / `token =` / `secret:`, followed in the batch by a file whose first line holds a key only `generic-api-key` catches; the pair in both orders; in a long batch with the pair in the middle; end to end on 12 planted files as the checker did) against a23678e27's one-per-file form, with real gitleaks: the verdict per file equal. Probe the fence (`_FENCE`): can any rule of the project's `.gitleaks.toml` still run from one text into the next across it (a value class that takes `#`, a multi-line rule, a file ending without a newline, a file whose last line is itself `#`, CRLF)? Is a match that a rule's own filter drops (stopwords, entropy) still able to hide the next file's secret?
2. **The reuse record:** `_FORM` changed so form-4 records (written by the batched scan before the fix) are not reused; a second run in the same HOME gives the same verdict.
3. **Fail-open brought in by the fix:** a file judged clean that the one-per-file form leaves out; a finding put on the wrong file and its real owner kept; the fence changing what a text's own rules see (a secret the fence turns into a non-match, or a false positive the one-per-file form does not give: the second is "other", the first fails open).
4. **S27's figures:** the evidence file's re-measure (at least 10 times) holds as written.
5. **The tests:** do e66a9cb58's cases and the new unit tests assert the stated behaviour? Does a4eff2312 keep every assertion of the cases it touched (weakens nothing) and export no `governance/project/held-out.yaml`?
6. **Scope:** each non-merge commit since {B[:9]} changes only the ticket's `allowed_paths` (the test designer: `tests/acceptance/W2-88/`), carries `Task: DAEO-2bdu`, and its `Implements:` lists only ids from the ticket's `sources:` (`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-2bdu.md`).

## What the lead already knows (judge them; do not re-derive the decisions)
- The lead's `gov accept` and scoped lead_verify on {H[:9]} run beside you (`{L}/accept-8.txt`, `{L}/verify-8.txt`, `{L}/verify/`); their results go into the record beside your check.
- Not re-judged here (nc-3 passed them; their open items are the lead's packages): S24's full-line case red for the unshipped pool, walls and briefs; S25's cause in `gov.codeintel`; W2-23's `test_safety.py` case meeting S26's refusal first.
- The engineer's return reached the lead without its twelve fields (its last message was an idle note); its commit message and the evidence file's "Fix 3" state what it built.

## The rules you judge by (governance/project/briefs/JUDGEMENT.md, word for word)

{judgement}

## How to probe
- Read freely: the ticket, the register by id (`/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md`), the code, the tests, the logs under `{L}/`. Search with the Read and Grep tools (no `gov retrieve`, no `gov context`, DEC-1065); search again once in your own, different words; then answer from both or say "not found".
- Probe by Bash into your own TMPDIR only (DEC-1144 (7)): plant small repositories there and run the head's code with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src`, and a23678e27's from a `git -C /home/usain/gov-os-worktrees/W2-88/src archive --prefix=src/ a23678e27` export in your TMPDIR, each with its own empty HOME. Every pytest through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with `TMPDIR` your sandbox temp folder, `HOME` a folder under it, `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`. A resource gate's refusal is a wait (DEC-1146). Never `-x`.
- Never write in `/home/usain/gov-os-worktrees/W2-88` or any repository; never run `gov rebuild`, `gov adopt`, `gov close` against a real repository or worktree; never touch `~/gov-os-workbench/examin/` or the copies under `~/gov-os-runs/`; never open the evaluation sets' root or any hidden or memory-verdict folder. Secrets never printed; held-out qualification material's contents never read (DEC-820).
- No shell variable as a write target; no here-document, no backticks, no `bash -c '...'`; no long inline `python3 -c` with braces. Your tool list holds no Write tool: write probe scripts into your TMPDIR with `printf` from Bash (DEC-1144 (7)). **Refused twice for the same call: stop and say so** (DEC-1142 (9)). A refused form is not retried in another disguise.

## Return
One message, your last. The twelve fields first, each a labelled line; then your check in this form (the lead copies it unchanged into the probe record):

```
task: / status: (DONE, with one line) / work_completed: / files_changed: none / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

Then:
- `# W2-88 (DAEO-2bdu): narrow re-check of P1-1's fix (S27)` with `probed_commit:`, `base: {B[:9]}`;
- `## Sandbox and identity`;
- `## P1-1` (a table: item of the stated behaviour, fixed | not fixed | partly, file:line, how you probed it);
- `## What I probed and found sound` (numbered, each with the command or file:line and the result);
- `## Findings` (new ones: id P1R-n, the KPI line, severity blocker | major | minor, what is wrong, how to reproduce, the behaviour it should have, and the two lines the rules above require);
- `## Notes, not findings`;
- a fenced block tagged `verdict` holding one JSON object: `{{"kpis": [{{"kpi": "success-27", "verdict": "pass" | "fail", "findings": [{{"id": "P1-1" | "P1R-n", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}}]}}], "overall": "pass" | "fail"}}` (P1-1 listed with its classification only if it is not fixed).

Refused twice for the same call: stop and say so.
"""
(D / "nc-4.md").write_text(text)
print(len(text))
