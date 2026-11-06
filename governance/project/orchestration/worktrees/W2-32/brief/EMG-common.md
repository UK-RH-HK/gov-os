# The emergency's common rules for the CTO's agents (DEC-1033, DEC-1038, DEC-1039), session debdb3f7, 2026-11-02 evening

You are one of the CTO's emergency agents. The owner's emergency and freeze are in force: everything on this machine is
stopped except the infrastructure fixes. Your task brief (the file that named this one) says what you do; these rules
hold for every one of them.

- **Where you write:** only the worktree (and, if your brief names one, the scratch file) your brief names. Commit only
  there, on its own branch, with `git commit -m "<subject>" --trailer "Task: <id>" --trailer "Implements: <ids>"
  --trailer "Role: <your role>" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"` and `-- <paths>`.
  Never commit on `w2/integrate`, never merge into it, never push, never amend or rebase. The CTO merges.
- **Every heavy job through the gate (DEC-1038 (4)):** every test run (pytest beyond a single small unit file, a
  measurement, a collect-only over the whole tree) runs as
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh <command>`;
  a store rebuild through `.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh`. Nothing heavy past it. Long
  commands in the background, never blocking for more than a few minutes at a time.
- **Tests use your tree's own code:** `PYTHONPATH=<your worktree>/src` on each command (never in settings);
  `TMPDIR=/tmp/gov-os-emg-<your short name>`; pytest with `-o tmp_path_retention_policy=failed -p no:cacheprovider`.
  Never the full suite (DEC-968): your own tests, plus, when you change `src/`, the scoped set from
  `PYTHONPATH=<tree>/src python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/select_tests.py <tree> <W2> <ticket id>`
  (its `pytest_options` added to `pytest tests`). A red you did not cause: re-run it alone, then name it; do not fix
  what is outside your brief.
- **The machine is the owner's (DEC-1038 (1)):** never touch the shared Ollama servers (127.0.0.1:11434 and :11435) or
  their processes, `~/.local/bin`, `~/.config`, `~/.ollama`, the crontab, `.wslconfig` or any service. Anything that
  needs such a change: write the exact commands as a proposed owner ACT in your return. No installs (a P1 in your
  return). No `sudo`. `rm` only inside your own `TMPDIR`. Processes are judged with
  `.gov-runtime/scratch/orchestrator/tools/tree_busy.sh <W2 or --cmd path>`, never `pgrep -f` on a path.
- **The guard's five rules hold:** an implementer never writes acceptance tests (`tests/acceptance/**`); reviewers
  write only their review record; no reads of secrets or of the held-out material's contents or of an evaluation
  set's hidden half; no installs. A refusal is taken, never routed round (DEC-849). **A false refusal is worked round
  at once and you keep going (the owner, DEC-1040 item 3):** an equivalent form (the Edit or Write tool for a file
  change, or a script file run by its path), never a form chosen to pass a true refusal; name it in your return.
  The guard misreads heredocs and `$(…)` loops today (W2-42a fixes it): prefer the Edit/Write tools for file edits.
- **Under `.gov-runtime/`:** commit hashes written as 12 digits; row W2-L423's rule (write none of the keywords
  `tools/keyword_warn.py` looks for).
- **Knowledge:** use `gov retrieve "<question>"` (run in your worktree) for what you need to know about the codebase
  and the decisions (DEC-836); code questions by small, targeted searches, never one giant query (DEC-859, DEC-860).
- **Judgement (reviewers):** `governance/project/briefs/JUDGEMENT.md` word for word; each finding with
  `Ordinary work: yes|no, because ...` and `Consequence: fails open|loses work|other`, and the fenced `verdict` block.
- **Scratch budget:** 20 GB and 1,000,000 files and folders outside the tracked tree; report `du -sh` and
  `du -s --inodes` of your `TMPDIR` in your `evidence` line; clean it as you go.
- **Speed matters:** this is the owner's emergency; keep to your brief's scope and estimate.
- **Return:** the twelve fields first, as labelled lines: task, status, work_completed, files_changed, evidence,
  tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action; then any payload.
  Status DONE, PARTIAL or PACKAGES (a decision only the CTO or the owner can take, with your recommendation and
  confidence). Refused twice for the same call: stop and say so; no third try.
