# W2-152 — the independent test designer's brief (DAEO-o5x1)

You are the independent test designer for **W2-152** (`.tickets/DAEO-o5x1.md`): `gov brief`, a filled brief from the
ticket and the facts file, refused when the ticket is not READY by code (W2-128's code half, part 1; DEC-1050,
DEC-1052, DEC-1083, DEC-1088 (3)). Profile STANDARD. Read first, in full: the ticket (its ten KPI lines, three failure
lines **and its body's "Interface" section**: the command form, inputs, placeholders, the role → template map, what
counts as a verify, the output and refusal forms; build on it, do not guess past it); W2-128's ticket
`.tickets/DAEO-t8mp.md` body "Interface and rounds" (the placeholder syntax, `keys.yaml`, the facts file's shape);
`governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md` §B ("Filling"), §D TPL-3 and TPL-5; and the
templates and facts as merged on integrate: `template/governance/kernel/templates/` (`brief.md`, `role-lead.md`'s
"## Your run" section, `keys.yaml`) and `governance/project/facts.yaml`.

## What the cases must show
- One case group per KPI line S1-S10 and per failure line F1-F3 (the README's KPI cell: `S1`…`S10`, `F1`…`F3`).
- **Fixture repositories, not this one:** build a small temporary repository per case (a `.tickets/` with planted
  tickets, a `governance/project/facts.yaml`, and the kernel templates, either copied from integrate at test time or a
  minimal planted set where a case needs control), and run `python3 -m gov.cli.main brief … --root <tmp>` as a
  subprocess (the public interface), with `PYTHONPATH=<worktree>/src`. Golden files where the KPI says so (S1 per
  worker role, S6 per run kind): build the expected text from the fixture's own inputs by a rule the case states, or
  commit the golden output with the fixture, never by reading an implementation.
- **The ready check (S8, S9):** one planted ticket per required field missing (allowed_paths empty; a KPI line with no
  verify in either form; a `depends_on` not closed) and per advisory item (no `non_goals`; `est_loc` 401); the
  dependency fields either side of `ready.new_since`; `WAITS_ON_UNKNOWN`; an empty list as a declared none. Assert the
  codes the ticket names, in `details.findings` (with `--json`) and on stderr.
- **S2's verify rule:** a string KPI line holding `Verify:` with text counts as having a verify; a `{line, verify}`
  object with an empty verify does not.
- **S10:** `facts.yaml` carries `ready.new_since` (an ISO date) and validates against `facts.schema.json`; W2-128's
  acceptance cases still pass (run `gov accept W2-128` on your tree in the case, or mark it the CTO's run in the README).
- **F3:** a filesystem spy (for example a temporary repository whose other files are unreadable, or an `strace`-free
  check that the tree is byte-unchanged after the run and that no file outside the four inputs was opened, via
  Python's audit hooks in a subprocess wrapper): gov brief writes nothing.
- Say for each case whether it is red on integrate (no `gov brief` command: the CLI exits with an unknown-command
  error) for the right reason, or a green guard.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-152-tests`, branch `w2/W2-152-tests`, made from `w2/integrate` at
  `97f39dc4` today. You write only `tests/acceptance/W2-152/`: the cases, a `conftest.py` and support module, fixtures,
  and a `README.md` with the map `| KPI line | Test (node id) | On integrate | Why |` (one id such as `S1` per KPI cell,
  each test in backticks with its full node id, as `tests/acceptance/W2-128/README.md`).
- You may read anything on `w2/integrate` (DEC-963), including `src/gov/cli/main.py` (how a command module is found
  and how `GovError` and `--json` are emitted) and other commands' acceptance cases for the form.

## Rules
- **Never read this ticket's implementation (G-14; DEC-820 (c)):** never open `/home/usain/gov-os-worktrees/W2-152` or
  the branch `w2/W2-152`, nor `src/gov/brief/` if it appears in any tree.
- **The exclusion line (DEC-1093 (2)):** keep every Grep, Glob and recursive Bash search inside your own worktree; if a
  search shows you a line of the implementation anyway, stop reading it and say so.
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own, different words; then
  answer from both, with path and lines, or say "not found". Two searches in all. No `gov retrieve` in the sandbox.
- No GPU, model, network or installs. Never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run only your cases: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-152-tests/src python3 -m pytest tests/acceptance/W2-152 -q -p no:cacheprovider -m "not local_only" -k "not real and not green_here and not time_limit"`
  with an empty `HOME` (set `PYTHONUSERBASE=/home/usain/.local` if pytest is not found); then
  `python3 -m gov.cli.main accept W2-152 --root /home/usain/gov-os-worktrees/W2-152-tests` (if it crashes in the sandbox,
  say so: the CTO runs it outside).
- **DEC-1080:** Read and Grep tools; one simple command per Bash call; no `cd … &&` chains. No merge inside the sandbox.
  Before you end, every test run you started has finished.
- **Commit** on `w2/W2-152-tests`, only `tests/acceptance/W2-152/`, with
  `--trailer "Task: DAEO-o5x1" --trailer "Implements: DEC-1050, DEC-1052, DEC-1083, DEC-1088" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Size: about 35 to 50 cases.

## Return
Your final message, in full: the twelve labelled fields of `EMG-common.md` (sandbox check and `ps` check first), the
case list (node id, KPI line, red or green on integrate, and why), the commit, `gov accept`'s counts,
`TESTS-READY <hash12>`, and anything untestable or ambiguous in the interface as `discoveries`.
