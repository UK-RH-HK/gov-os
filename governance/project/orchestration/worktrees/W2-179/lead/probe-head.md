---
type: probe
task: DAEO-c9n8
reviewer_session: 79f85759-ea74-4c94-a5ee-5103960ddc1b
implementer_session: 6117e372-d954-4339-a8ed-97ff4fc383cf
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 4a9d5d0748343351b60d6de38cdb6e5ddd07dbd4
decisions_applied: [DEC-820, DEC-866, DEC-966, DEC-1101]
---

# Probe record: W2-179 (DAEO-c9n8), the LITE review of W2-170's F3 file-access case revision

- **What was probed.** Head `4a9d5d074834` of `w2/W2-179`: the independent test designer's one commit `3c1981b03b90` (session `6117e372-d954-4339-a8ed-97ff4fc383cf`, Sonnet at effort high, class C1), merged by the ticket lead. It changes `tests/acceptance/W2-170/test_w2_170_s4_map.py` (the helper `_true_root_opens`, which leaves out the repository's own root taken from `W.HERE`, compared in realpath form, plus a guard that the root is narrower than every true root) and `tests/acceptance/W2-170/README.md`. Base `3eeb5cb2e98e`.
- **Who probed.** A fresh read-only reviewer (role `independent-auditor`, session `79f85759-ea74-4c94-a5ee-5103960ddc1b`, Opus at effort high, class C1, 2026-11-12), started through `gov launch` under its OS sandbox with the reading tools alone. Commissioned and judged by the ticket lead (an orchestrator-role session). It wrote nothing in the repository: the lead's tripwire before and after its session shows no change in this worktree, and `git status --porcelain` stayed empty.
- **Step 0.** The write outside the worktree was refused (read-only file system). `git hash-object -w` and `git update-index --refresh` worked. `gov.__file__` = `/home/usain/gov-os-worktrees/W2-179/src/gov/__init__.py`. Read refusals: 0. One Write refusal: the probe script under TMPDIR, refused for quiet hours (DEC-991). It was not retried, and the verdict does not rest on it.
- **The lead's runs beside it.** These were all on `4a9d5d074834`, in fresh `--no-hardlinks` clones under `~/gov-os-runs/W2-179/clone` and `/tmp/w2-179-else/clone`, both since removed:
  - The case as merged passed in both clones.
  - A synthetic log entry at `~/gov-os-runs/W2-179/planted-outside/x.txt` failed the case in both, with only that path in `reached`.
  - A synthetic entry naming the clone's own `src/gov/memaudit/__init__.py` passed in both.
  - The pre-revision case failed in the runs-folder clone with the repository's own files, which reproduces the nightly's red.
  - `gov accept W2-179` passed: 179 passed, 0 failed.
  - `lead_verify`: 3,935 tests, 6 failed. All six are W2-96's shared base reds:
    - four fail on `w2/integrate`'s head `f3d612de7147`;
    - the other two pass when run alone on this head (load-sensitive);
    - all six are red in the nightly of 11-12 on `9bbef27f1d05`.
- **Threat model (DEC-801, DEC-808).** The review judges against ADR-0001's threat model: honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries.
- **Verdict: pass.** Classification (DEC-809): yes and fails open or loses work 0; yes and other 0; rows 2 (RV1, RV2). The lead's judgement agrees:
  - RV1 (the helper's docstring overstates its symlink handling; selection by spelling is unchanged from the base) is a row.
  - RV2 (a false red if the nightly ever keeps its interpreter or temp folder under `~/gov-os-runs` outside the clone; it fails closed) is a row.
  - Both are returned to the orchestrator as residuals.

## The reviewer's record (verbatim)

