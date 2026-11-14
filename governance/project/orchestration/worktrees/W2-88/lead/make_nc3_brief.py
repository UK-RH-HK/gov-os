"""Builds briefs/nc-3.md: the narrow independent check of run 7 (S24-S27), with JUDGEMENT.md word for word and the
run-7 interface as the pair built to it."""
from pathlib import Path

D = Path("/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/briefs")
judgement = Path("/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/briefs/JUDGEMENT.md").read_text()
iface = (D / "run7-interface.md").read_text()
H = "ef9c773c30365081e634d05a9b68c6eb7c4dd446"
B = "a23678e27"
G = "git -C /home/usain/gov-os-worktrees/W2-88"
L = "/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log"

text = f"""You are a fresh Independent Auditor, read-only. Ticket: DAEO-2bdu (W2-88, "Memory for any repository"), profile FULL, class C2. The ticket was reopened on 2026-11-14 under DEC-1164 (18) on the owner's DEC-1178 (3)(b) and (4) for four items, its S24 to S27 (P-1: A9 from an installed release; F-1: redis's code graph; F-3: ignore rules found at the start, the CTO's choice (b); the secret scan's speed). Review rounds are spent; DEC-1154 and DEC-1178 (3)(b) call for **a narrow independent check of this change only**. You are that check. You probe the head **{H}** of branch `w2/W2-88` in `/home/usain/gov-os-worktrees/W2-88`. You write nothing in any repository; your return is your check.

This run is the critical path to the first release (0.1.0). Your budget: about 1.5 hours.

## Step 0, before any work (report it first in your return)
The sandbox check in the launcher's step-0 file beside this brief. Then `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-2bdu`), `{G} rev-parse HEAD` (expect {H}) and `{G} status --porcelain` (expect empty). If anything differs, stop and say so. Check the head and the empty status again at the end.

## What you judge (only this)
**The change since {B}**: `{G} diff {B} {H}`: the engineer's commits fcfbd87f9 (S26), bdbaa37a5 (S24), 4d49108fb (S25), 2da02b28e (S27, with the run-7 evidence), ff290696e (S24's `details.looked`); the test designer's cases 0841cfb3c (merged at 57c20ac47) and its revision 7646ebe89 (merged at {H[:9]}). Judge it against S24 to S27 as the ticket states them (`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-2bdu.md`, S24 to S27 and its last paragraph "Reopened 2026-11-14") and the binding interface below. Nothing else of the ticket is re-judged.

1. **S24, probed:** the resolver's three places and its refusal (`SHIPPED_FILE_MISSING`, `details.file` and `details.looked`, never empty, never a place not looked at); no `parents[3]` in `src/gov/adopt/`; no shipped-file read at import; every one of the five reads through it. Build a wheel in the release form in your TMPDIR (`python3 -m pip wheel -q --no-deps --no-build-isolation --no-index`, a fresh `--system-site-packages` venv, `pip install --no-deps --no-index`, all inside a script in your TMPDIR, installing nothing on the machine) and run A9's shipped reads from it on a project whose kit `copier copy` installed from a planted tag (`--skip-tasks`). What it finds and what it refuses by name.
2. **S25, probed:** with a stand-in for the tool's answers (a stand-in `codebase-memory-mcp` first on `PATH`, or the test designer's `standin_f1/`), a graph over the 100,000-row cap gives `CODEGRAPH_TOO_LARGE` with the counts and the cap; under the cap, as today; another failure, `FABRIC_INCOMPLETE` with its text; never a pass with 0 nodes and edges. The lead's re-run on the redis copy: `{L}/redis-a9.err`, `.exit`, `.before`, `.after`, `.status`, `.time`.
3. **S26, probed:** MA and A0 refuse `ADOPT_PATH_IGNORED` at once, naming each path with the rule's file, line and pattern, for `.gitignore`, `.git/info/exclude` and `core.excludesFile`; nothing written, staged or committed; never `git add -f`, never an ignore file edited; a tracked path the rules match is not refused; the list of written paths covers what A0 to A9 commit (look for a path a stage commits that the list misses).
4. **S27, probed:** the same verdict per file as a23678e27's one-per-file form on a planted set with planted test secrets (built from parts in your TMPDIR; never print a value): a finding put back on its own file only, never on a neighbour in the batch; files with blank lines, form feeds, CRLF, no final newline, a secret spanning a batch's boundary between two files, a large file, a link, `scan: off`, the reuse record of clean results; batches at most `_workers()` at once. The measured figures in `docs/changes/W2-88-evidence.md` ("Run 7") and whether they hold the 10-times line.
5. **Fail-open or lost work brought in by the change:** a secret missed by the batching (a file judged clean that the one-per-file form leaves out: this fails open), a refusal swallowed into ok, a long stage reached before the ignore check, a shipped file replaced by a default, A9's undo skipped on the new refusals.
6. **The tests:** do the acceptance cases and the unit tests assert the stated behaviour (not the code's accidents)? Do the README map rows (success-24 to success-27) name existing cases?
7. **Scope of the change:** each non-merge commit since {B} changes only the ticket's `allowed_paths` (or, for the test designer, `tests/acceptance/W2-88/`), carries `Task: DAEO-2bdu`, and its `Implements:` lists only ids from the ticket's `sources:`.

## What the lead already knows (judge them; do not re-derive the decisions)
- The lead's run of the four run-7 modules at 2da02b28e: `{L}/run7-acc.txt` (10 red: 7 on a stderr check under `--json`, the lead's interface wording, revised by td-10; 2 on `details.looked` empty, fixed by ff290696e; 1 the package below). The lead's `gov accept` and scoped lead_verify on {H[:9]} run beside you (`{L}/accept-7.txt`, `{L}/verify-7.txt` when they end); their results go into the record beside your check.
- **Expected red, the lead's package (1):** S24's full-line case (`test_s24_a9_from_an_installed_release_copies_reads_and_writes_from_shipped_bytes`): from an installed release A9 refuses `SHIPPED_FILE_MISSING` for `governance/project/retrieval.yaml` (the pool), and would for `governance/project/indep-walls` and the MEMORY-AUDIT-1 briefs: none is under `template/` or in the wheel; shipping them is outside the ticket's paths.
- **The lead's package (2):** S25's real cause is in `src/gov/codeintel/__init__.py` (the tool refuses a query over 100,000 rows; `_graph` reads all edges in one query; `_Session.tool` drops the tool's text), outside the ticket's paths; in the paths A9 names it.
- **Known red outside the paths (3):** `tests/unit/adopt/test_safety.py::test_s1_a_stage_writes_nothing_over_an_untracked_file` (W2-23's) plants an ignored `governance/` and expects `ADOPT_WOULD_OVERWRITE`; S26 now refuses `ADOPT_PATH_IGNORED` first.
- The refusal's process exit is 1 (`gov.cli.main`; 2 is argparse's usage error); under `--json` the refusal is in the envelope and stderr is empty (the lead's interface correction, DEC-1052).
- The engineer's named risks: the first `looked` entry in the no-tree case is a description, not a path; a repository that ignores generated `.claude/` content now refuses at MA and A0; the 36,000-file estimate assumes small files (the scan's time follows the bytes, about 0.37 MB/s with this rule file). Classify each under the rules below.
- Decided, not to re-open: run 5's and 6's undo; the review rounds are spent; the reopen's four items and the CTO's choice (b) for F-3.

{iface}
## The rules you judge by (governance/project/briefs/JUDGEMENT.md, word for word)

{judgement}

## How to probe
- Read freely: the ticket, the register by id (`/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md`), the code, the tests, the workers' logs under `{L}/` (eng-6-3, eng-7) and `/home/usain/gov-os-worktrees/W2-88-tests/.gov-runtime/scratch/lead/log/` (td-9, td-10). Search with the Read and Grep tools (no `gov retrieve`, no `gov context` in the sandbox, DEC-1065); search again once in your own, different words; then answer from both or say "not found".
- Probe by Bash into your own TMPDIR only (DEC-1144 (7)): plant small repositories there and run the head's code with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src`. Every pytest through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with `TMPDIR` your sandbox temp folder, `HOME` a folder under it, `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`. A resource gate's refusal is a wait (DEC-1146). Never `-x`.
- Never write in `/home/usain/gov-os-worktrees/W2-88` or any repository; never run `gov rebuild`, `gov adopt`, `gov close` against a real repository or worktree (on a planted repository in your TMPDIR it is the probe); never touch `~/gov-os-workbench/examin/` or the copies under `~/gov-os-runs/`; never open the evaluation sets' root or any hidden or memory-verdict folder. Policy 2 (DEC-820): secrets never printed; held-out qualification material's contents never read.
- No shell variable as a write target; no here-document, no backticks, no `bash -c '...'`; no long inline `python3 -c` with braces (keep commands short). Your tool list holds no Write tool: write probe scripts into your TMPDIR with `printf` from Bash (DEC-1144 (7)). **Refused twice for the same call: stop and say so** (DEC-1142 (9)). A refused form is not retried in another disguise.

## Return
One message, your last. The twelve fields first, each a labelled line; then your check in this form (the lead copies it unchanged into the probe record):

```
task: / status: (DONE, with one line) / work_completed: / files_changed: none / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

Then:
- `# W2-88 (DAEO-2bdu): narrow independent check of run 7 (S24 to S27)` with `probed_commit:`, `base: {B}`;
- `## Sandbox and identity` (step 0, head and status at start and end);
- `## S24 to S27` (a table: item of the stated behaviour, met | not met | partly, file:line, how you probed it);
- `## What I probed and found sound` (numbered, each with the command or file:line and the result);
- `## Findings` (new ones: id P1-n, the KPI line, severity blocker | major | minor, what is wrong, how to reproduce, the behaviour it should have, and the two lines the rules above require);
- `## The lead's packages and known reds` (for each of (1), (2), (3): correctly classified as outside the ticket's paths or not, and what you saw);
- `## Notes, not findings`;
- a fenced block tagged `verdict` holding one JSON object, in the rules' form: `{{"kpis": [{{"kpi": "success-24" | "success-25" | "success-26" | "success-27", "verdict": "pass" | "fail", "findings": [{{"id": "P1-n", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}}]}}], "overall": "pass" | "fail"}}`, one entry for each of success-24 to success-27. Judge S24 on what the ticket's paths can do (the package's red is the lead's to carry, not a finding against the change, unless the change itself is wrong).

Refused twice for the same call: stop and say so.
"""
(D / "nc-3.md").write_text(text)
print(len(text))
