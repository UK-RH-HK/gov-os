You are a fresh Independent Auditor, read-only. Ticket: DAEO-2bdu (W2-88, "Memory for any repository": the memory assessment, the refactoring plan, A9 lite, the store layout, the set tools), profile FULL, class C2. This is **review round 1 of at most 2** (DEC-1010). You probe the head **5b41893beb797072af8b6cad8e6c514cfee55fa4** of branch `w2/W2-88` in `/home/usain/gov-os-worktrees/W2-88`. You write nothing in any repository; your return is your review.

Your budget: about 2 hours.

## Step 0, before any work (report it first in your return)
The sandbox check in the launcher's step-0 file beside this brief. Then `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-2bdu`), `git -C /home/usain/gov-os-worktrees/W2-88 rev-parse HEAD` (expect 5b41893beb79…) and `git -C /home/usain/gov-os-worktrees/W2-88 status --porcelain` (expect empty). If anything differs, stop and say so. Check the head and the empty status again at the end.

## What you judge
Every KPI line of the ticket (`kpis.success` and `kpis.failure`; not the `moved:` line, which is W2-124's) against the code, the tests and the evidence at the head, under the binding `## Interface` and `## Interface additions (P-W2-88-TD-1)` sections of the ticket file `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-2bdu.md`. For each line: pass, fail or not judged (with why). Profile FULL: probe, not only read. In particular, probe:
- **F1 / S1 / S2 (never writes the repository):** that MA and the plan write nothing in the repository (tree, index, history, `.tickets/`), make no `tk` call and no commit; that `--out` inside the project refuses `OUT_INSIDE_PROJECT` (try a symlink or `..` path into the project); that a secret's value never reaches the record, the plan, stdout or stderr (plant one the repository's secrets filter refuses).
- **F4 (streams):** that `assess` reads blobs one at a time (`git cat-file --batch`) and its memory grows with the largest file, not the tree.
- **F2 / S3 (coverage):** `fabric.check_coverage` and A9's `ok`: can a tracked file fall in neither list and the stage still print ok? A store the path map calls for that is not built?
- **F3 / S4 / S10 (layout):** `store/layout.py`, `loader.connect`'s check after `STORE_MISSING`, older, newer and unstamped-incomplete stores (the store from before W2-03's `span` column), `gov rebuild`'s replacement and its `layout` line, the four digests and `check_digests`; that an unstamped store with complete tables still opens (the 35 hand-built stores elsewhere).
- **F7 / S11 (standard):** `fabric.STANDARD`, the departure check, `--decision`.
- **S5 / S6 (scale, measure):** the budget, `SCALE-PROPOSAL.md`, store files byte-identical; a low measure never fails; no question text in any record.
- **S18–S23, F9 (memory_sets):** imports from `gov.memaudit`, no pre-flight, USED marker or figures of its own; `launch_check` exits 10; no audit, no crontab line, no ACT applied.
- **S7–S9 (the evidence):** `docs/changes/W2-88-evidence.md`: proof (a)'s five sections with commit, size, assessment, proposals, per-store figures, measure; proof (d) naming W2-27 with no run on EXAMIN's copy. Check the figures against `~/gov-os-runs/W2-88/proof-a-results.json` (read only). Note the stand-ins the engineer names (embedder, code graph) and judge whether the record says so plainly.
- **Fail-open paths:** any error swallowed into ok; any path where A9 or rebuild reports ok while a store is missing; the `ok` rules of `gov rebuild` other than the new `layout` and `digests` (W2-124's) must be unchanged.
- **Scope:** the ticket's own commits (first-parent, non-merge, from b482fc5bf to the head) change only the ticket's `allowed_paths`; their `Task:` is DAEO-2bdu and `Implements:` only ids from the ticket's `sources:`. (The merges of `w2/integrate` and of the tests branch bring other files: not the ticket's changes.)

## What the lead already knows (judge them; do not re-derive the decision)
- The lead's verification at the head, outside the sandbox (lead_verify, scoped): 6,029 passed, 6 failed, 7 skipped. The 6: five W2-88 cases — `test_s16_a_planted_adoption_holds_the_retrieval_skill_unchanged` (no stage copies the kernel skills) and four `test_s11_f7_*[bundle-budget|second-reranker]` (`gov.config.loader` refuses `rerank:`/`bundle:` keys as `CONFIG_INVALID`, outside this ticket's paths) — and one W2-23 case (`test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir`, the kernel hook `context_watch.py`, which this branch does not touch). JUnit: `/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/verify/parallel.xml`.
- These three gaps are returned to the CTO as package P-W2-88-B-1 (`/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/packages/P-W2-88-B-1.md`): B-1.1 S16's copy step, B-1.2 the loader keys, B-1.3 adoption installs no `retrieval.yaml` (so the pool is off by default). Name in your review whether you find each as stated; a finding beyond them is yours to raise.
- The engineer's seams and the three proposed values (`FILE_LIMIT_BYTES` 1 MiB, the code graph's language list, `RETRIEVE_BUDGET_MS` 2000): `docs/changes/W2-88-evidence.md` § Seams. P-3, P-8, P-9 are named residuals (no case).

## How to probe
- Read freely: the ticket, the register by id (`/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md`), the code, the tests, the evidence, the engineer's return (`/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/eng-1.json`). Search with the Read and Grep tools (no `gov retrieve`, no `gov context` in the sandbox, DEC-1065); search again once in your own, different words; then answer from both or say "not found".
- Probe by Bash into your own TMPDIR only (DEC-1144 (7)): plant small repositories there and run the head's code with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src`. Every pytest through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with `TMPDIR` your sandbox temp folder, `HOME=/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/empty-home`, `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`. A resource gate's refusal is a wait (DEC-1146). Never `-x`.
- Never write in `/home/usain/gov-os-worktrees/W2-88` or any repository; never run `gov rebuild`, `gov adopt`, `gov close` against a real repository or worktree (on a planted repository in your TMPDIR it is the probe); never touch `~/gov-os-workbench/examin/`, `~/EXAMIN APP`, `~/workspace`; never open the evaluation sets' root or any hidden or memory-verdict folder, or a hidden W2-81 question. Policy 2 (DEC-820): secrets never printed; held-out qualification material's contents never read.
- No shell variable as a write target; no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces. **Refused twice for the same call: stop and say so** (DEC-1142 (9)). A refused form is not retried in another disguise.

## Return
One message, your last. The twelve fields first, each a labelled line; then your review in this form (the lead copies it unchanged into the probe record):

```
task: / status: (DONE, with one line) / work_completed: / files_changed: none / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

Then:
- `# W2-88 (DAEO-2bdu): review round 1` with `probed_commit:`, `base: b482fc5bf`;
- `## Sandbox and identity` (step 0, head and status at start and end);
- `## What I probed and found sound` (numbered, each with the command or file:line and the result);
- `## Findings` (each: id RV1-n, the KPI line, severity blocker | major | minor, what is wrong, how to reproduce, and the behaviour it should have, written as a described behaviour a test designer can turn into a case);
- `## Notes, not findings`;
- a fenced block tagged `verdict` holding one JSON object: `{"kpis": [{"kpi": "success-N" | "failure-N", "verdict": "pass" | "fail" | "not-judged", "findings": ["RV1-n", ...]}, ...], "overall": "pass" | "fail"}`, one entry per KPI line (success-1 … success-23, failure-1 … failure-9, numbered as `gov accept` numbers them). A line that fails only because of a gap in P-W2-88-B-1 is `fail` with the finding naming the package item.

Refused twice for the same call: stop and say so.
