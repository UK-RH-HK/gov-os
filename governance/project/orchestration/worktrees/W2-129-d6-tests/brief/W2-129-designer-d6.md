Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-129-d6-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-129 — the independent test designer's brief, D-6 part 2: S17, planted ids in test fixtures (DAEO-q7lk)

You are the independent test designer for **W2-129** (`.tickets/DAEO-q7lk.md`: read it, with its new line **S17**,
its new failure line and its "D-6 part 2 placed here" note). `gov links` is merged into `w2/integrate`; its
acceptance tests are in `tests/acceptance/W2-129/` (read the README first: the interface, the planted-repository
support module and the S1-S16 map). This round adds S17 only. DEC-1109 (2) restarted D-6 part 2. The row comes from
the W2-130 sitting (DEC-1098 (3); DECIDED-NOT-DONE row 24: "the check to skip test fixtures").

## What S17 says, briefly
In a **Python test file** (`tests/**/*.py`), an id inside a **string literal that is not a docstring** is a planted
fixture id. Examples: a planted register `REGISTER = """### DEC-<n> ..."""`, a path `"records/decisions/DEC-<n>.md"`,
or `f"{ACCEPTANCE}/W1-90/test_fixture.py"`.
- (1) A planted id gives **no UNKNOWN_ID**.
- (2) An **ENFORCES_SUPERSEDED** that W2-55's propagation gives for a test-file line is carried only when the old id
  also stands on that line outside such a literal: in a comment, a docstring or code.
- (3) Ids in comments and docstrings are judged as today. So is every non-Python test file (`README.md`, `*.json`,
  `*.yaml`, `*.txt`), and a Python test file that does not parse.
- (4) W2-55's `gov.decisions.propagation` itself is unchanged: `python3 -m gov.decisions.propagation` still reports
  the line.

On this repository, at the branch's base, `gov links --all` gives **73 ENFORCES_SUPERSEDED** for the test designer,
29 of them inside planted registers and records, and **557 UNKNOWN_ID** for the test designer, mostly made-up ids in
literals.

## What the cases must show (2 to 8 cases; add them first, the engineer then builds)
Use your planted repository.
- **Planted, now quiet:**
  - an unknown wave id (e.g. `W1-90`) inside an assigned string literal in a planted `tests/.../test_x.py` gives no
    UNKNOWN_ID;
  - a superseded decision's id inside a planted multi-line register string gives no ENFORCES_SUPERSEDED in
    `gov links`' output.
- **Still judged (guards):**
  - the same unknown id in a `#` comment gives UNKNOWN_ID;
  - the same id in a module or function docstring gives UNKNOWN_ID;
  - the superseded id in a comment gives ENFORCES_SUPERSEDED;
  - the superseded id in a test folder's `README.md` gives ENFORCES_SUPERSEDED;
  - a `.py` test file with a syntax error is judged as today;
  - a line holding the old id both in a literal and in a trailing comment is still carried.
- **W2-55 unchanged:** where cheap, `python3 -m gov.decisions.propagation` in the planted repository still names the
  literal's line.

Map the cases to **S17** and the new failure line. For each case, say what it expects and whether it is red today:
the "quiet" cases should be red for the stated reason, and the guards green. Update the README with S17's interface
line and a note for DEC-1109.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-129-d6-tests`, branch `w2/W2-129-d6-tests`, made from
  `w2/integrate` at `d48639954`. Write only `tests/acceptance/W2-129/`.
- **Your record:** your whole return is your session's **final message**, in full. The launcher keeps it in this
  worktree's `.gov-runtime/scratch/lead/log/`.

## Rules
- **Never read this ticket's implementation (G-14; DEC-820 (c)).** It is `src/gov/links/` and `tests/unit/links/` in
  your own worktree.
  - Never open, grep or list them, nor the engineer's worktree (base name `W2-129-d6`).
  - Never run `git show`, `git log -p` or `git diff` on them.
  - Run the code only through your cases.
  - You may read `src/gov/decisions/propagation.py` (W2-55's, not this ticket's).
- **The exclusion line (DEC-1093 (2)):**
  - every recursive grep carries `--exclude-dir=links`;
  - every Grep or Glob call that could reach the implementation carries `!src/gov/links/**` and
    `!tests/unit/links/**`;
  - find carries `-path '*/gov/links' -prune`.

  Keep searches inside your own worktree. If a search shows you a line of the implementation anyway, stop reading it
  and say so in your return.
- **Search again once (DEC-1092 (1)):** two searches in all.
- **Planted folders only.** No GPU, model, network or installs.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, nor any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Run your cases through the heavy slot that `EMG-common.md` names,** with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-129-d6-tests/src` and a scratch HOME (link `.local/lib` to the user site
  so pytest is found). Then run
  `python3 -m gov.cli.main accept W2-129 --root /home/usain/gov-os-worktrees/W2-129-d6-tests`. The earlier cases
  should pass, and the new "quiet" cases should be red for the right reason. Never the full suite.
- **DEC-1080:** use the Read and Grep tools, one simple command per Bash call, and no `cd … &&` chains.
- **Commit** on `w2/W2-129-d6-tests`, only `tests/acceptance/W2-129/`, with
  `--trailer "Task: DAEO-q7lk" --trailer "Implements: DEC-1109" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished. Waits and stops by pid only.

## Return
- The twelve labelled fields of `EMG-common.md` (the sandbox check and the `ps` check first).
- The new cases: node id, KPI line, what each expects, red or green today and why.
- The README's changed interface lines, quoted in full.
- The commit, `gov accept`'s counts and the `TESTS-READY` text.
- Anything ambiguous, as `discoveries`.
