# ACT-PATHMAP-NS-1: two folders placed in a path-map namespace (DEC-1101 (1): an unindexed-path notice resolved within a day)

- **Why:** the structural pass's pathmap family names `governance/project/indep-walls/` (added by ACT-INDEP-WALLS-1,
  `147706ae`) as in no namespace; W2-148 (`DAEO-xafn`) will add `governance/project/operator/` the same way.
- **The change:** two lines in `governance/project/path-map.yaml`, in `project-overlay` beside the briefs and prompts
  (embedded, restricted, every role may read; nothing hidden). The guard's rules, the hook and every hidden glob are
  unchanged. Class (a) by effect (DEC-1104 (2)): it governs no agent.
- **The patch:** `.gov-runtime/scratch/orchestrator/drafts/pathmap-ns/path-map.patch` (3 lines added).
- **Rehearsed in a clone** (`~/gov-os-runs/act-pathmap-ns/clone`, at `5f015c99`): the structural pass all 9 families
  ok (pathmap ok); `guard4_check` 453 run, 0 failed, PASS. Map before `622b0c5b1a77…`, after `3f7ae7f83d99…`.
- **A note for the CTO:** the template folder's name matches the sets root's hidden glob (`indep-walls/**`) when a shell
  command names it relatively, so the guard refuses commands that spell it; write such records with the Write tool.
- **Undo:** `git revert` of the operator's commit.
