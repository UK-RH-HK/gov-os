# W2-142 — the independent test designer's brief (DAEO-qskx)

You are the independent test designer for **W2-142** (`.tickets/DAEO-qskx.md`): search again once in the kernel
skills, the retrieval skill's new step 7 and one sentence in the discovery skill (DEC-1094 (2); the patches are
`governance/project/orchestration/packages/LIFT-1/SEARCH-AGAIN-PRACTICE.md` §2, §3.1 and §3.2). Read the ticket and
the package's §2 and §3 in full first. Profile LITE: one test per KPI line, string tests on the two skills, plus the
failure line.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-142-tests`, branch `w2/W2-142-tests`, made from `w2/integrate` today.
- You write only `tests/acceptance/W2-142/`: the cases, a `conftest.py` if needed, and a `README.md` whose map the
  runner reads. Its header is `| KPI line | Test (node id) | On integrate | Why |`, with one id such as `S1` in each KPI
  cell and the test in backticks with its full node id (as `tests/acceptance/W2-133/README.md`).
- **Your record:** write your return (the twelve fields below) also to
  `/home/usain/gov-os-worktrees/W2-142-tests/.gov-runtime/scratch/lead/W2-142-designer-return.md` (you cannot write the
  main tree's scratch).
- You may read anything on `w2/integrate`: `template/governance/kernel/skills/retrieval/SKILL.md` (its steps, W2-138's
  step-5 line, its version), `template/governance/kernel/skills/discovery/SKILL.md` (line 55's neighbourhood), the
  skills validator (`python3 -m gov.check.skill_validator --both-layouts <skill folder>`, its size budget), and
  `tests/acceptance/W2-138/` for how a string test on a skill is written there.

## What the cases must show (from the ticket)
- **S1:** the retrieval skill has a step 7 after step 6 with the practice: "search again once", "own, different words",
  "not found", "two searches"; W2-138's step-5 line kept; version 1.1.0; the skills validator passes (size budget).
  Red on integrate (no step 7, version 1.0.0); the step-5 line a green guard.
- **S2:** the discovery skill gains one sentence: search again once before routing a question to the owner as
  unanswered; the validator passes. Red on integrate.
- **S3:** the landing at the lift's re-pin ACT and the adoption count are the CTO's evidence, not a string test: say
  so in the README (one test only if something in the tree can be checked, e.g. the evidence file names the adoption
  count's first reading; otherwise mark it untestable here).
- **The failure line:** nothing beyond the two named lines changes. Test it against today's text: everything in each
  skill outside the added step and sentence (and the version field) is unchanged from integrate's
  (`git show w2/integrate:<path>` read at test time, or a stored copy with its commit named).
- Say for each case whether it is red on integrate for the right reason, or a green guard.

## Rules
- **Never read this ticket's implementation (G-14; DEC-820 (c)):** there is none yet; never open
  `/home/usain/gov-os-worktrees/W2-142` or the branch `w2/W2-142` if either appears, and never read the product-spec
  worker's files on this ticket. You work from the ticket, the package and today's integrate text only.
- **The exclusion line (DEC-1093 (2)), for you:** keep every Grep, Glob and recursive Bash search inside your own
  worktree, never from `/home/usain/gov-os-worktrees/` or `/home/usain/`, so no search can reach this ticket's worker
  worktree; if a search shows you a line of the implementation anyway, stop reading it and say so in your return.
- **Search again once (DEC-1092 (1)):** if what you searched (Grep and Read; no `gov retrieve` in the sandbox,
  `EMG-d4b-launched.md`) does not answer, or you can tell your answer may be incomplete, search once more in your own,
  different words; then answer from both searches and the files you read, with path and lines, or say "not found".
  Two searches in all.
- No GPU, no model, no network.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run your cases with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-142-tests/src`, and run
  `python3 -m gov.cli.main accept W2-142 --root /home/usain/gov-os-worktrees/W2-142-tests` to show the runner reads
  your map.
- **DEC-1080:** read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains; one line
  before any command that will ask for permission.
- **Commit** on `w2/W2-142-tests`, only `tests/acceptance/W2-142/`, with
  `--trailer "Task: DAEO-qskx" --trailer "Implements: DEC-1094, DEC-1097" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- **Before you end your session,** make sure every test run you started has finished.
- Keep to the estimate: this is a small round (about 4 to 6 cases).

## Return
The twelve labelled fields of `EMG-common.md` (sandbox check and `ps` check first), with the case list (node id, KPI
line, red or green on integrate, and why), the commit, `gov accept`'s counts, `TESTS-READY` text, and anything
untestable or ambiguous as `discoveries`.
