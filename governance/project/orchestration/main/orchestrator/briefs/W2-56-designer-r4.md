# W2-56 — the independent test designer's brief, a small revision: S13's real case (DAEO-wnnz)

You are the independent test designer for **W2-56** (`.tickets/DAEO-wnnz.md`: read **S13** as changed today, marked
`[changed, DEC-1112 (3): the engineer's P-1 (b)]`, and "The engineer's round-1 points settled"). S13 now reads:
launched sessions can run gov check and their own suite inside the sandbox; **gov rebuild inside the sandbox is a
Wave 3 row** (it writes `.gov-runtime/rebuild/` and a rebuild lock, which today's sandbox keeps read-only; DEC-180).

## What the CTO saw (outside the sandbox, `GOV_W2_56_REAL=1`, short TMPDIR, on the engineer's head; results only)
`gov accept W2-56`: 259 passed, 1 failed: `test_s13_real_sandbox_gov_check_gov_rebuild_and_a_code_graph_suite_run_inside_the_sandbox`
(mapped S1 and S13). Its message:
- `"rebuild": {"code": 1, "tail": "gov rebuild: REBUILD_FAILED: the rebuild lock /tmp/gov-os-rebuild-2ecfbcb573d4.lock cannot be opened or created: Read-only file system: nothing is rebuilt"}` — now out of S13.
- `"suite": {"code": 1, ...}`: `FileNotFoundError: [Errno 2] No such file or directory: '<tmp>/pytest-of-usain/pytest-0/test_s13_real_sandbox_gov_chec0/wt/W2-77/.w56-real/probe.jsonl'` (from `pathlib.open(mode='a')`).
The other three real cases (S2, S7, S9) pass.

## Your job
1. Revise the S13 real case to the changed line: drop the gov rebuild step (rename the case to match), keep gov check
   and the code-graph suite inside the sandbox.
2. Find whether the suite step's `FileNotFoundError` is the case's own harness (for example the `.w56-real` folder not
   there, or not visible, where and when the probe writes inside the sandbox) or the product. If it is the harness,
   fix it so the case tests S13 and S1's sandboxed part; if it is the product, keep the case and say exactly what it
   shows, for the engineer. You can read the case and support files; you cannot run the real case in your sandbox.
3. README: the map and the real cases' section to match; a line for P-1 (b).
4. Do not change any other case.

## Where you work and rules
- `/home/usain/gov-os-worktrees/W2-56-tests`, branch `w2/W2-56-tests` (at `34adb8071`); write only
  `tests/acceptance/W2-56/`. First merge nothing; your branch is the tests' branch.
- Your record is your session's **final message**, in full (the launcher keeps it).
- Never read this ticket's implementation: never open, grep or list the engineer's worktree (base name `W2-56`,
  `/home/usain/gov-os-worktrees/W2-56`) or the branch `w2/W2-56`; keep every search inside your own worktree.
- Run the file once to show it collects and skips cleanly (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-56-tests/src`,
  through the heavy slot `EMG-common.md` names), then `python3 -m gov.cli.main accept W2-56 --root /home/usain/gov-os-worktrees/W2-56-tests` once.
- No GPU, model, network or installs. The hidden-half rule: never open anything under `~/gov-os-eval/` or
  `~/gov-os-runs/`, nor any `hidden`, `memory-verdict` or `memory-verdict-2` folder. DEC-1080: Read and Grep tools,
  one simple command per Bash call. Search again once (DEC-1092 (1)).
- **Commit** on `w2/W2-56-tests` with
  `--trailer "Task: DAEO-wnnz" --trailer "Implements: DEC-1112" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished. Waits and stops by pid only.

## Return
The twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first), the change, harness or product for the
suite step (with the evidence), the commit, `gov accept`'s counts, and `TESTS-READY <head>`.
