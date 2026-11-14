
## Check
- Each of F-A, F-B and R1 is met as described.
  - F-A: the store every standing and fresh search reaches equals the link's, the anchors are read at the audit commit,
    and S7 compares the same store.
  - F-B: the remote gets only the scanned commit.
  - R1: step 6's line names the scanner.
- Nothing else in behaviour moved:
  - the one judged path (`prompts.py`, the reader, grader and matcher unchanged);
  - counts only (no id, question, gold, answer, citation, path or secret in any line, log or digest);
  - the week rule;
  - `maintain` not a gate;
  - the push fails closed;
  - the no-declaration push writes nothing.
- The acceptance cases cannot pass for the wrong reason: the planted `gov` now answers the store of the folder it runs
  in.
- The engineer's note: the fresh path's `pool` child still gets the repository as `--repo` (a retrieval-only
  diagnostic re-measure). Judge whether that touches S7's comparison or any KPI line.
- Scope: every file the fix commits change is inside `allowed_paths`; only the test designer touched
  `tests/acceptance/`.
- Do not re-run whole suites (the lead's results are at the end); small probes are yours.

**Held-out rules (DEC-820):**
- Never open the evaluation sets' root, the real runs folder or any folder under its `indep/`, any hidden half or
  memory-verdict folder, or the real crontab.
- Never a real model call, a real search, a real push to a real remote, or a real gitleaks over a real repository.
- Plant everything in your sandbox's temporary folder. Any pytest goes through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=<an empty folder in your temporary folder> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187/src python3 -m pytest <one file or case> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  with a Bash timeout of 3600000 ms; a heavy-slot refusal is a wait.
- Search with Read, Grep and Glob (DEC-1065); no `gov retrieve`, no `gov context`.

## Judgement rules (governance/project/briefs/JUDGEMENT.md, carried word for word)

