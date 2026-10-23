# The owner's Role: owner commit C of 2026-10-23 (DEC-906 item 2), prepared and validated

**The entry:** the path map's new `acceptance_exemptions` list, beside `accepted_history`, with one entry:
`c9a08678644485a7528bc875164e110881b63d93`, citing DEC-900.
- Patch: `drafts/OWNER-C-acceptance-exemption.patch` (sha256 starts `9d8915e771b236f0`), 6 lines added to `governance/project/path-map.yaml`.
- It applies to `w2/integrate` at `488972e4`.

**Validation (DEC-906 item 1, DEC-895),** on a fresh clone of `83a3867e` with the patch applied:
- **With the pinned judge's own code** (`pin-fecb870c`, its python `-E`):
  - its config loader reads the patched path map;
  - the ratchet counts all 30 `load_sensitive` entries, with 0 findings;
  - `accepted_reds` is empty, with 0 findings;
  - `accepted_history` is unchanged (5 entries);
  - the new block is exactly the one entry decided.
- **The placeholder scan:** nothing.
- **With the repository's own code:** `core-pathmap` and `core-schema` both green.
- **A full parallel run in the close's form,** under the lock, with `-o tmp_path_retention_policy=failed`: **15,466 passed, 30 skipped (the same 30 as before), 1 failed.**
  - The one red is W1-01's `test_only_the_test_designer_commits_to_acceptance_tests`, as expected.
  - The entry only takes effect when W2-70's revision of the case, which reads the list, merges. That is W2-70's KPI.
  - No other red: W2-58's launched sessions pass at this temp path.
- The record of the run: the orchestrator's `log/exemption-validation-2026-10-23.txt`.

**The commands:**

```
cd /home/usain/Dynamic-Agentic-Engineering-OS
git status --short
git apply --check .gov-runtime/scratch/orchestrator/drafts/OWNER-C-acceptance-exemption.patch
git apply .gov-runtime/scratch/orchestrator/drafts/OWNER-C-acceptance-exemption.patch
git diff --stat
git commit -m "Owner decision DEC-906: acceptance_exemptions lists c9a08678 (DEC-900) for W1-01's history case" --trailer "Task: decision-record" --trailer "Role: owner" -- governance/project/path-map.yaml
```

After it, W2-70's lead merges `w2/integrate` back, and its revised W1-01 cases read the entry.
