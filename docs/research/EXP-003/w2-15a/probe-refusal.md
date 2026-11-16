# EXP-003 W2-15a: the refused probe read of the sets root's hidden folder

- **Ticket:** DAEO-rd0g (W2-15a). **Under:** DEC-1171 (3), DEC-1186 (3); S1's "a recorded refused probe read of the
  sets root's hidden folder from a worktree", made before the owner's operator's walled run.
- **Session:** the ticket lead (`GOV_ROLE=orchestrator`, `GOV_TICKET=DAEO-rd0g`), headless, in the worktree
  `/home/usain/gov-os-worktrees/W2-15a` on `w2/W2-15a` at `28fef4a99c44`.
- **When:** 2026-11-15 16:13:58 UTC (from `date -u` run just before the call).
- **The call (one, the only one):** the Read tool on
  `/home/usain/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/zz-probe-w2-15a.yaml`, a name chosen not to
  exist. No listing, search or other call touched the evaluation sets root before or after it.
- **The result: refused.** The refusal text, as returned, whole:

  ```
  File is in a directory that is denied by your permission settings.
  ```

- **No content was read.** The refusal came before any file access; nothing of the folder (no name, count or text)
  was returned or is recorded here.
- **Which layer refused:** the harness's permission settings (a `Read` deny on the folder, the rule ACT-PERMISSIONS-2
  set; the same rule stands in the main tree's `.claude/settings.local.json`). That layer decides before the live
  hook (`.claude/hooks/pretooluse.py`) runs, so this probe shows the wall holds for this session but did not exercise
  the hook's own sets-root rule. The probe was not repeated (one probe, as briefed).
