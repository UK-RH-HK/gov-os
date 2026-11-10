# ACT-W2-149-INSTALL-1 — the narrow review, round 2 (the last; READY by verdict.py)

You are a fresh, read-only independent reviewer, not the ACT's author. Round 1 of the review of **ACT-W2-149-INSTALL-1**
(its full record: `.gov-runtime/scratch/ref/ACT-W2-149-INSTALL-1/ACT-W2-149-INSTALL-1-review-r1.md` in your worktree)
was READY by `verdict.py`, with K1 and K6 marked fail and seven in-scope findings F1-F7. The CTO's helper changed the
drafts and the package in answer. **Narrow scope:** check those answers, and that nothing else changed.

Everything is in `.gov-runtime/scratch/ref/ACT-W2-149-INSTALL-1/` (the package, `drafts/` as now built, ACT-SETS-GLOBS-1,
ACT-INDEP-WALLS-1, OPERATOR-AGENT-1, LAUNCH-SPEC, the declaration, the sandbox experiment's README), and the launch
script and template in your worktree's tree (`w2/integrate`, ACT-SETS-GLOBS-1 live: hook `74f8dbea4761`, map
`44f99ea563cb`). Round 1 reviewed `drafts/apply.sh` `e52f548e979ae0c0…`; now `871d2c9db3dc…`.

## Check (each a KPI line of your verdict block)
- **K1 F1 and F2:** `apply.sh`'s two inline Python runs carry `-B` and the apply writes no `__pycache__` into the tree;
  the package's §5 commit and undo commit are limited by `-- governance/project/indep-briefs/sgx1`, and the touched set
  is now exactly what §1 states.
- **K2 F3:** the four globs reach the Python check unexpanded from any working folder.
- **K3 nothing else changed in `apply.sh`:** diff it against round 1's (`git diff --no-index` between your own copy of
  round 1's text, rebuilt from the record if needed, is not required: read the whole script and say whether anything but
  F1/F3 differs from what round 1 described); `APPROVED.after` (`9e9d6f212a1e`), the briefs, `freeze.py` and
  `install_check.py` hash as round 1 read them.
- **K4 the rehearsal:** `rehearsal.log` (round 2's re-run) ends `failures: 0` and shows the F1, F2 and F3 cases.
- **K5 F5:** §0 states class (O) with the `walled-sessions` row, and the routing (your yes, your operator by hand).
- **K6 F4, F6, F7:** §3 and §8 now state that the ACT stands only if applied before the follow-up changes the script,
  that the declaration's pin must move, and that the briefs' exclusion from the walls' trees is an entry criterion.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this ACT's change.

## Write and return
- **You write nothing** in any tree. You may run `apply.sh` and the launch script only against copies in your own
  temporary folder with a planted HOME and sets root (never the real one, never the main tree). No real `claude`
  session, no GPU, no network. Single simple Bash commands (DEC-1080). The hidden-half rule holds: never open anything
  under `~/gov-os-eval/`, `~/gov-os-runs/` or any `hidden` folder, and never name the sets root on a command line.
- **Your record is your session's final message**, in full: the twelve labelled fields of `EMG-common.md` (task,
  status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved,
  recommended_next_action; sandbox and `ps` checks first), your answer to K1-K6, every finding with its two lines and
  scope (new ids from F8), and at the end one fenced block opened with three backticks and the word `verdict`:
  `{"act": "ACT-W2-149-INSTALL-1", "round": 2, "class": "a|b|O", "apply_sh_sha256": "<the sha256 of drafts/apply.sh you read>", "kpis": [{"kpi": "K1", "verdict": "pass|fail", "findings": [...]}, ... "K6"]}`.
Refused twice for the same call: stop and say so; no third try.
