# W2-153 — the fixtures revision (R1), the independent test designer's brief (DAEO-8s85)

You are a fresh independent test designer working under **W2-153** (`.tickets/DAEO-8s85.md`: read it, especially
"The review's R1"). W2-153 makes `gov launch`, for workers and leads alike, refuse to start unless
`<root>/.claude/templates/<stem>.md` exists for the role. The ticket's Interface gives the role → stem map:
engineer `role-engineer`, independent-test-designer `role-test-designer`, independent-auditor `role-reviewer`,
product-spec `role-product-spec`, research `role-research`, lead and orchestrator `role-lead`. Earlier tickets'
acceptance cases build fixture repositories and launch sessions in them. Without the copy, those launches will be
refused once W2-153 lands.

## The change (DEC-866: a revision of other tickets' cases carries `Rewrite-Reason:`; `Task:` is W2-153's)
- In the acceptance support files of **W2-56, W2-20, W2-136, W1-46, W1-28, W1-32, W2-58, W1-50 and W2-54**
  (`tests/acceptance/<id>/`, their conftest and support modules, and the cases if a case builds its own repository):
  every fixture that builds a repository a launch runs in plants `.claude/templates/<stem>.md` for the role launched.
  Planting all eight files is the simplest, and any byte content will do; a fixture that copies the real ones from the
  tree is fine too.
- The cases newly red on W2-153 (the CTO's scan):
  - W2-56: 136 of its 256 cases (its launch fixtures);
  - W2-20: `test_w2_20_launch.py` (13), `test_w2_20_plan_source.py` (2), `test_w2_20_stale_samples.py` (1);
  - W2-136: `test_w2_136_launch_check.py` (3);
  - W1-46: `test_w1_46_held_out.py` (2), `test_w1_46_experiment_folder.py` (1).
- W1-28, W1-32, W2-58, W1-50 and W2-54 are red today for another reason: their fixture HOMEs lack the machine gate
  file (W2-20's gate). Plant the template copies there too, so W2-153 does not turn them red again once that is
  fixed. Do **not** fix the gate-file reds; they are another item. Name them in `discoveries`.
- A case that tests that a launch **is refused** for another reason (a broken held-out file, a gate, a plan) must
  still reach that refusal: plant the copy, so the template check is not what refuses.
- **W2-153's own launch cases** (`tests/acceptance/W2-153/`, your predecessor's): the stub CLI's record path is read
  from an environment variable (`W2_153_RECORD`). W2-56's launcher now passes the session a cleaned environment
  (W2-56 S5, in integrate's `src/gov/launch/launcher.py`, which you may read). So the stub records nothing and the
  launch cases fail. Move the record path to something the cleaned launch keeps: a file next to the stub, or the stub
  writing beside its own path, for example. Read W2-56's S5 on integrate to see what is kept. Assert the same things
  as before.
- Change nothing else: no assertion, no expected value. Only the fixture setup and that harness.

## Where you work, rules, return
- Your worktree `/home/usain/gov-os-worktrees/W2-153-tests`, branch `w2/W2-153-tests`. Write only the support files
  and cases of the nine folders above, and W2-153's own harness (`tests/acceptance/<id>/`). Never `tests/acceptance/W2-153/`'s assertions.
- **Never read W2-153's implementation:** never open `/home/usain/gov-os-worktrees/W2-153`, the branch `w2/W2-153`,
  or `src/gov/launch/launcher.py` there. The behaviour you plant for is stated above. Keep every search inside your
  worktree.
- Run each folder on your tree, which has integrate's launcher, so the folders must stay exactly as green or red as
  before. Run one folder per pytest call (their conftest modules collide):
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-153-tests/src python3 -m pytest tests/acceptance/<id> -q -p no:cacheprovider -m "not local_only" -k "not real and not green_here and not time_limit" --tb=no`.
  Report each folder's counts before and after your change; they must be equal. The CTO runs them on W2-153's branch.
- No GPU, model, network or installs. No real session: the fixtures' stub CLIs only. Never open `~/gov-os-eval/`,
  `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder. DEC-1080: one simple command per
  Bash call. No merge inside the sandbox. Search again once (DEC-1092 (1)) if a search does not answer.
- **Commit** on `w2/W2-153-tests`, only those folders, with
  `--trailer "Task: DAEO-8s85" --trailer "Implements: DEC-1050, DEC-1112" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: W2-153 refuses a launch without the role's template copy (S1, DEC-1050); the fixtures plant it (DEC-866)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- **Return** (your final message, in full): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks
  first), the files changed, each folder's counts before and after, the commit and `TESTS-READY <hash12>`.
