"""Make td-4.md and eng-6.md from td-3.md and eng-5.md: the same step 0, standing rules and return, a new middle for review 3's fix."""
LEAD = "/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/"
addendum = open(LEAD + "design-r3.md", encoding="utf-8").read().split("\n", 2)[2].strip()


def parts(name):
    text = open(LEAD + "briefs/" + name, encoding="utf-8").read()
    start = text.index("## Step 0")
    rules_end = text.index("## What you read")
    ret = text.index("## Return")
    return text[start:rules_end], text[ret:]


td_rules, td_return = parts("td-3.md")
td_rules = td_rules.replace("Return only after your commits exist.", "Return only after your commit exists.")
td_middle = """## What you read

- Your suite as it stands: `tests/acceptance/W2-96/` on this branch (README, support module, cases; run 2's file `test_w2_96_at_run_2.py` included).
- The ticket file `.tickets/DAEO-ouet.md` (read-only) and DEC-970 in `docs/DECISION_REGISTER.md`.
- The lead's addenda (behaviour only): `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/design-r2.md` (R8 to R13) and review 3's, below.

## The behaviour to test: review 3's addendum

""" + addendum + """

How review 3 reproduced V1 (as a described behaviour): a planted test runs a nested `gov accept` on a nested planted project, started in a session of its own (as this suite's own harness starts nested runs); the nested test writes about 3,000 small files and sleeps about 1 s. SIGTERM was then sent to the outer `gov` once the nested `gov`'s removal had begun, or to the outer and the nested `gov` at the same moment (as a stop of a whole process tree does). In about one run in three the outer `gov` reported `ok: true`, `outcome: error`, `error_kind: crash`, exit 4 instead of 143, and test-named folders (and once 2,657 test-written files) stayed in the caller's `TMPDIR`. The removal stopped at the first entry another process had removed meanwhile.

## What you write

- Only inside `tests/acceptance/W2-96/`: a new case file (say `test_w2_96_at_review_3.py`), its rows in the README's map (in the map forms the suite uses; under R8 every case must also be mapped or it still counts), and support code where needed.
- R14: the nested form above, both ways (SIGTERM to the outer `gov` while the nested removal runs; SIGTERM to both at once): each must end with 143 and the given `TMPDIR` empty, no marker anywhere. It is a race: repeat each form enough times inside the case (or parametrize) that the run-2 code fails it reliably (review 3 saw about one in three; aim for a red in nearly every run of the case), while the whole W2-96 suite stays well under eight minutes. Also a case where a planted test's own-session process keeps creating and removing files in its temporary folder while the run ends normally (no signal): the outcome is the results' (pass, exit 0), never `crash`, and the given `TMPDIR` ends empty.
- R15: a planted passing test that leaves 8,000 empty sibling folders in its temporary folder: pass, exit 0, the given `TMPDIR` empty, and the whole `gov accept` run under a generous bound you state (review 3 measured 22.7 s for the removal alone on run 2's code against 0.6 s for a plain recursive removal; choose a bound that a linear removal meets under load and run 2's code misses, and say why).
- Revise no earlier case unless the addendum changes it; say so if you do.
- Keep the cases deterministic in outcome, no network.
- **Red first:** this branch (`w2/W2-96-tests`, made from the ticket's head `382e6d8fba8c`) carries run 2's implementation, which lacks review 3's addendum. Run the whole W2-96 folder to the end: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96-tests/src python3 -m pytest tests/acceptance/W2-96 -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=line`. Say which new cases are red and why (the README states each expected red reason), and run the new file a second time to show the race cases are red reliably.
- An ambiguous point or a dispute with the addendum is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

One commit, only your test paths, trailers in the final block (the git hooks are uninstalled; never `--no-verify`, never `core.hooksPath`; check first that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file):

    git commit -m "W2-96 (DAEO-ouet): review 3's acceptance cases for gov accept, a clean-up that tolerates concurrent changes (DEC-970)" --trailer "Task: DAEO-ouet" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-970, DEC-959" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

(Add `Rewrite-Reason: review 3's V1 (DEC-136)` only if you revise an earlier case.) `Implements:` holds only ids the register holds (DEC-927). Then `git log --oneline -2` and `git status --short`.

"""
td_head = """# Brief: independent test designer, W2-96 (DAEO-ouet), run 2, review 3's batch (DEC-970, DEC-916)

You are a fresh independent test designer (MR-3). Ticket: `DAEO-ouet` (W2-96, the opaque acceptance runner `gov accept`), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-96-tests` on branch `w2/W2-96-tests`. You add review 3's cases to the ticket's acceptance tests, from the reviewer's finding given below as a described behaviour (DEC-136), and you show them red.

**Where things stand.** The suite in `tests/acceptance/W2-96/` has 100 cases (run 1's and run 2's), marker `qzv96leak`. The engineer's run-2 implementation is in this worktree's tree (this branch was made from the ticket's head); you still never read it (Policy 2 (c) below), but your red run executes it. Review 3 probed it and found one behaviour that fails open; the lead turned it into the addendum below. A fresh engineer builds it in parallel in `/home/usain/gov-os-worktrees/W2-96`; the lead merges your branch after you return. A leftover empty folder in the ticket's worktree is not yours this time: do not try to remove it.

"""
open(LEAD + "briefs/td-4.md", "w", encoding="utf-8").write(td_head + td_rules + td_middle + td_return)

eng_rules, eng_return = parts("eng-5.md")
eng_rules = eng_rules.replace("(expect `549dd29b1c6f`)", "(expect `382e6d8fba8c`)")
eng_middle = """## What you read

- The ticket file `.tickets/DAEO-ouet.md` (read-only): its KPI lines, its `allowed_paths` and its body (DEC-970).
- The code as it stands: `src/gov/accept/` (the clean-up's removal in `runner.py` above all), `tests/unit/accept/`.
- The lead's addenda: `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/design.md`, `design-r1.md`, `design-r2.md` (R8 to R13), which still hold except where review 3's addendum below differs.

## Review 3's addendum (behaviour only; it overrides the earlier notes where they differ)

""" + addendum + """

How review 3 reproduced V1: a planted test runs a nested `gov accept` on a nested planted project in a session of its own (the acceptance harness starts nested runs this way; eight other suites here also start own-session processes); the nested test writes about 3,000 files and sleeps about 1 s; SIGTERM goes to the outer `gov` once the nested `gov`'s removal has begun, or to both `gov`s at once. In about one run in three the outer `gov` ended `crash`, exit 4, with test-named folders left in the caller's `TMPDIR`: the removal stopped at the first entry another process had removed ("file not found"). Run 1's removal, which passed over errors, gave 143 and nothing left in 12 of 12. Review 3 also measured the removal of 1,000 / 2,000 / 4,000 / 8,000 sibling folders at 0.39 / 2.48 / 8.99 / 22.66 s (quadratic).

Points that keep this failing closed: R8 to R13 unchanged; nothing printed from the child; a stopped run never exits 0.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/accept/**` and `tests/unit/accept/test_w2_96*.py` (every new file's basename starts `test_w2_96_`). Not `src/gov/check/commands.py` this time.
- Never `src/gov/cli/main.py`, never `tests/acceptance/**` (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Proportion (DEC-135): only R14 and R15. Review 3's row V3 (signal windows at the very start and very end of `gov`) is a Wave 3 row: do not build it.
- Unit tests first (TDD): R14 (an entry removed by another process during the removal is passed over; a folder refilled meanwhile is emptied again; a stopped run keeps 128+N; an unstopped run is not turned into `crash`), R15 (8,000 sibling folders), with R10's deep chain still passing. Run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m pytest tests/unit/accept -q -p no:cacheprovider -o tmp_path_retention_policy=failed` to the end, never `-x`.
- **Commit before any acceptance run.** Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Trailers in the final block:

      git commit -m "W2-96 (DAEO-ouet): review 3, the clean-up tolerates concurrent changes and is linear in its entries (DEC-970)" --trailer "Task: DAEO-ouet" --trailer "Role: engineer" --trailer "Implements: DEC-970, DEC-959, DEC-317" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

  `Implements:` holds only ids the register holds (DEC-927). After every commit: `git log --oneline -2` and `git status --short`.

## Steps

1. Build R14 and R15 with unit tests, run your unit tests to the end, commit.
2. Run the current acceptance tests once as a regression check, reading results only: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m gov.cli.main accept DAEO-ouet --json` (quote the JSON and the exit code). Review 3's new cases are not on this branch yet. If it does not pass, run the folder once through pytest for the failing names and one-line messages (`... -m pytest tests/acceptance/W2-96 -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=line`), fix the code to the specification, commit, and run again; at most three acceptance runs in all.
3. Return. The lead resumes this session after merging review 3's acceptance cases, for one acceptance run.

"""
eng_head = """# Brief: engineer, W2-96 (DAEO-ouet), run 2, review 3's fix (DEC-970, DEC-916)

You are a fresh engineer. Ticket: `DAEO-ouet` (W2-96, the opaque acceptance runner `gov accept`), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-96` on branch `w2/W2-96`. You build the code to the specification and its KPIs, never to the tests (DEC-957); your test-driven development is your own unit tests.

**Where things stand.** Run 2 is built (`41b9fdddf109`, `917aba42cd9c`: R8 to R13), its 100 acceptance cases pass through `gov accept`, and the unit tests pass (62). Review 3 probed it and found one behaviour that fails open (V1): run 2's new removal, which replaced run 1's tolerant one, stops at its first error. The lead turned it into the addendum below. A test designer writes review 3's cases in parallel; the lead merges them after you return, then resumes this session for one acceptance run.

"""
open(LEAD + "briefs/eng-6.md", "w", encoding="utf-8").write(eng_head + eng_rules + eng_middle + eng_return)
for name in ("td-4.md", "eng-6.md"):
    text = open(LEAD + "briefs/" + name, encoding="utf-8").read()
    print(name, len(text.splitlines()), "Step 0" in text, "## Return" in text, "recommended_next_action" in text)
