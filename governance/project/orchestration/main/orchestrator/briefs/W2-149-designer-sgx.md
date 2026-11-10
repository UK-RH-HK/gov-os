# W2-149 — the independent test designer's brief, set-up A's wiring (DAEO-52ku)

You are the independent test designer for **W2-149** (`.tickets/DAEO-52ku.md`). Read the ticket first: the changed lines
**S16** and **S20**, the new lines **S22 to S28**, the new failure line (each marked `[changed, DEC-1112 (3)]`) and its
last note ("Set-up A's wiring placed here"). Your earlier cases are in `tests/acceptance/W2-149/`: read your README,
`w2_149_support.py` (the stub `claude`, `World`, the planted template and `APPROVED`) and `test_w2_149_seed_content.py`
and `test_w2_149_results.py` before you write.

## The point
The launch script (merged) refuses the five owner-approved set-up A briefs at stage 10 (they name no `model` or
`result_schema`; the labellers and the auditor no `sample`), and it has none of the flows set-up A needs. The briefs'
bytes are fixed (approved once by the owner, hashed): **nothing may require a change in them.** The template supplies
what they lack, and the script gains set-up A's flows. The CTO's rulings (delegated, DEC-1112 (3)): the seeds stay the
script's own draw (S6; the declaration's amendment A5); the labeller kind runs set-up A's flows only; the overlap
auditor never appends to `AUDITS.log`; a rule script that cannot run confined refuses with the new code 18.

## Your references (in your worktree, untracked; read them, never copy their bodies into the tests)
- `.gov-runtime/scratch/ref/INTERFACE-DRAFT.md`: the lead's proposed interface (places, flows, file names, the
  template's `briefs:` map). **You fix the interface:** adopt it, or change what a case needs, and state the result in
  your README's interface section; the engineer builds to that section only.
- `.gov-runtime/scratch/ref/sgx1-briefs/*.md`: the five approved briefs in full (their inputs, outputs and result
  forms are the spec for S24 to S28). `.gov-runtime/scratch/ref/sgx1-front-matter/*.fm`: their front matter alone.
- `.gov-runtime/scratch/ref/LAUNCH-SPEC.md`: the original specification.

## What the cases must show (red today, each for the reason your README states)
- **S22:** five planted briefs whose front matter is **byte for byte** the `.fm` files (a short planted body of your own
  after the front matter, never the real body: the bodies must not enter the repository's tests), their lines in a
  planted `APPROVED`, the planted `kinds.yaml` carrying a `model` per kind and the `briefs:` entries: each `--dry` build
  exits 0, with `WALL.json`'s model and result schema the entry's. A front-matter value beats the entry; an entry of
  another kind, and a value found nowhere, refuse 10; a labeller brief with no entry refuses 10.
- **S23:** the tree exclusions (`governance/project/indep-briefs/**` for every wall; the entry's `tree_exclude` for a
  set-up A brief only).
- **S24, S20:** each flow's staged inputs, compared with planted sources (planted halves: a tuning half under the
  planted runs folder's `SANDBOX-GUARD-EXP-1/tuning/`, a held-out half in the planted sets root's sealed folder; a
  planted `.tickets/` in the planted repository); writer 2's `seal.json` both ways; round 2's `input/round1/` and its
  hash check; `--set` against the flow's half; S20's set recomputed independently from the seed.
- **S25:** the confined rule script. Planted `label_rules.py` files: a good one; one that reads a planted marker file
  outside it; one that opens a socket; one that starts a process; one that loops past the cap; one that leaves out an
  id. Expect 18, nothing staged, no marker anywhere (staged files, output, log). Missing `bwrap`: 18. **First probe
  your own sandbox once** (`bwrap --unshare-all --die-with-parent --ro-bind /usr /usr true`): if a nested `bwrap`
  cannot run there, mark the cases that need it with a marker of their own, registered in `conftest.py` and kept out
  of the default run like `live`, say so in the README, and the lead runs them outside the sandbox. Do not skip
  silently.
- **S26:** labeller 1's completeness check and the hand-over-script merge (`how`).
- **S27:** the overlap auditor: disputes, the 40 split (45 planted disputes give runs of 40 and 5), the x/y map
  recomputed from the seed and absent from the wall, `tickets.jsonl` limited to the four fields, the delivery's
  validation, x/y mapped back, `audit` and `owner`, the old `labels.jsonl` kept, no `AUDITS.log` line, a memory
  writer's selection unchanged afterwards.
- **S16:** set-up A's destinations: a hash of the planted sets root and the planted experiment folder before and after,
  per flow; all or nothing; an existing destination refuses 20.
- **S28:** each flow's result forms accepted, an extra free-text field refused 20 without a trace (S13's grep).
- **Existing cases** that use the old labeller flow (the sealed folder's `rulebook.md`, `corpus/actions-r1.jsonl` and
  `-r2.jsonl`, `labels/<run>.jsonl`, the `random.Random` overlap) or the generic labeller brief: revise them to set-up
  A's labeller flows as far as S16, S20 and S22 require and no further; every other case's behaviour stays.
  Commits that change an existing case carry `--trailer "Rewrite-Reason: DEC-1112 (3) (set-up A's wiring: S16, S20
  changed, the labeller kind's flows replaced)"`. List each revised case in the README with its reason.

Map every case to its KPI line in the README's table, with its red reason, and write the interface section (the
template's `briefs:` keys, the environment overrides you choose for the rule python and `bwrap`, every place and file
name, the new exit code).

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-149-sgx-tests`, branch `w2/W2-149-sgx-tests`, made from
  `w2/integrate` at `ce1e9d0df` (the ticket changed). Write only `tests/acceptance/W2-149/`.
- **Your record:** your whole return is your session's final message, in full.

## Rules
- You never read the implementation: not `governance/project/orchestration/tools/indep_launch.py`, not
  `tests/unit/orchestration/test_w2_149*`, not `docs/changes/W2-149-evidence.md`, and never the engineer's worktree
  (`W2-149-sgx`). Run the script only as your cases do. The template (`governance/project/indep-walls/`) and the
  schemas folder you may read.
- No GPU, model, network or installs; no real `claude` session.
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them. Every case on planted roots (failure line 10); never the real `~/gov-os-eval`,
  `~/gov-os-runs`, `~/gov-os-wall-trees` or `~/.claude`.
- Run your cases through the heavy slot that `EMG-common.md` names, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-149-sgx-tests/src`, `TMPDIR=/tmp/gov-os-emg-w2-149-sgx-designer`, a
  scratch HOME with `.local` linked in, and `PYTHONUSERBASE=/home/usain/.local`; `-n auto` is allowed. Then run
  `python3 -m gov.cli.main accept W2-149 --root /home/usain/gov-os-worktrees/W2-149-sgx-tests`.
- Scratch budget: 20 GB and 1,000,000 files and folders outside the tracked tree; remove your temp trees as you go.
- **DEC-1080:** one simple command per Bash call. **Search again once (DEC-1092 (1)).** Use `gov retrieve` for what you
  need to know of the decisions.
- **Commit** on `w2/W2-149-sgx-tests`, only `tests/acceptance/W2-149/`, with
  `--trailer "Task: DAEO-52ku" --trailer "Implements: DEC-1112, DEC-1113" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished. Waits and stops by pid only, never a name match. Report your
  scratch size (`du -s --inodes`, `du -sh`).

## Return
In your final message:
- the twelve labelled fields of `EMG-common.md` (task, status, work_completed, files_changed, evidence, tests,
  discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), first, as labelled lines;
- the new and revised cases: node ids, expectation, red today and why;
- whether a nested `bwrap` ran in your sandbox, and which cases carry the outside-the-sandbox marker;
- the commits;
- `gov accept`'s counts (expected: the new and revised cases red, every other case green);
- `TESTS-READY`.
Refused twice for the same call: stop and say so; no third try.
