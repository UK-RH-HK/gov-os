# W2-176 (DAEO-ktiw): remove the 200k cap from context_watch.py (the owner's order, 2026-11-12 ~02:30), tests first

You are an engineer (Opus 5.5, high; class C3, kernel hooks), in W2-176's worktree `/home/usain/gov-os-worktrees/W2-176`, branch `w2/W2-176`, head `ad13a5b36` (R8 already fixed at `4dec7ec3c`). First calls: `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-ktiw`); `git -C /home/usain/gov-os-worktrees/W2-176 status --short` must be empty.

## The owner's decision (2026-11-12, chat; the CTO records it as DEC-1141, replacing DEC-1118 (A) entirely)
There is no token cap for any session: the CTO, leads, workers and helpers each use their model's full window and compact; the checkpoint and handover are written by the hook before compaction and the summary opens with the read-first line. The owner withdrew the approval of `3a580a4b4d42` because those bytes carry the cap.

## The change
In `template/governance/kernel/hooks/context_watch.py`: remove `HANDOVER_CAP` and the CTO-only branch (the coordination-ticket test) entirely, so every session is reminded once per context window at 85 % of its own model's window (the model table: Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable 5.2 at 1,000,000; unknown models 200,000 as the fallback window size of an unknown model, which is a model size, not a cap); keep R8's order (the text built before the marker), the re-arm below 50 %, the subagent skip, the 256 KiB tail, fail-safe exit 0. The reminder's wording must not mention 200k or a handover limit: it says write the checkpoint, update the files that need it, and open the compaction summary with the read-first line; a handover aid, not a stop.

## Tests first
Update `tests/unit/hooks/test_w2_176_context_watch.py`: the cap cases become "a lead or worker on a 1M model is reminded at 850k, not at 170k" and "no session is reminded below 85 % of its own window"; remove the CTO-only expectations; show the new cases red on the current hook, green after. Run through the gate, TMPDIR outside the repository: `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env TMPDIR=/tmp/gov-os-w2-176-nocap PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-176/src python3 -m pytest tests/unit/hooks -q -p no:cacheprovider -o tmp_path_retention_policy=failed`, then `tests/acceptance/W1-29`, `W1-49`, `W2-62` one folder per run. Parse each from pytest's own summary line.

## Commit and record
The red test, then the fix (`--trailer "Task: DAEO-ktiw" --trailer "Role: engineer"`, each with `-- <paths>`); then update `docs/changes/W2-176-CIT-P.md`: §2's new sha256 for `context_watch.py`, a §3.8 "the cap removed (the owner, 2026-11-12)", and the front matter/status saying the approval of 3a580a4b4d42 was withdrawn and the new bytes await review and approval. Report the new sha256 in full.

## Rules
Write only the hook, its unit test file and the CIT-P record. Refused twice for the same call: stop and say so. Never put `Role: owner` or `Decided-by:` on a commit of yours. Under `.gov-runtime/`, commit hashes as 12 digits. Waits by pid only. There is no token cap on your own session either.

## Return
First twelve labelled lines in order: task, status, work_completed, files_changed, evidence (commits, red-then-green counts, the new sha256), tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action.
