"""Build briefs/td-2.md (review 1's test design batch) from td-1.md and design-r1.md."""

base = "/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/"
td1 = open(base + "briefs/td-1.md", encoding="utf-8").read()
addendum = open(base + "design-r1.md", encoding="utf-8").read()

head = td1[:td1.index("## What you read")]
head = head.replace("# Brief: independent test designer, W2-96 (DAEO-ouet), run 1",
                    "# Brief: independent test designer, W2-96 (DAEO-ouet), run 1, review 1's batch")
head = head.replace(
    "You write the ticket's acceptance tests from its KPI lines and its sources, in parallel with the engineer (DEC-959 item 7, DEC-963), and you show them red.",
    "You add review 1's cases to the ticket's acceptance tests, from the reviewer's findings given below as described "
    "behaviours (DEC-136), and you show them red.\n\n**Where things stand.** A first test designer wrote the suite "
    "(`73e50896445c` on this branch: 54 cases, marker `qzv96leak`, README map in the design note's form). The engineer's "
    "implementation exists on `w2/W2-96`; you still never read it (Policy 2 (c) below). An independent reviewer probed it "
    "and found behaviour the suite misses; the lead turned the findings into the addendum below.")
head = head.replace(
    "use `gov retrieve` for what you need to know before reading files at random, **from the integration branch's store only**: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve \"<question>\" --json` (a read; it holds `w2/integrate` as of its last refresh).",
    "use `gov retrieve` for what you need to know before reading files at random, **from the integration branch's store only**: `cd /home/usain/gov-os-worktrees/W2-00-store && timeout 90 gov retrieve \"<question>\" --json` (a read; it holds `w2/integrate` as of its last refresh). Known: inside the sandbox that call can hang on its embedder's network call; try it once, and if it times out, say so and read named files instead.")
head = head.replace(
    "put anything longer in a script file under `/home/usain/gov-os-worktrees/W2-96-tests/.gov-runtime/scratch/td/` and run it.",
    "put anything longer in a script file in your session's own temporary folder (the one the launcher set; `.gov-runtime/scratch/td/` is refused to this role) and run it by its literal path; a command with `$TMPDIR` in it is refused, so write the path out. Never `cd` into a subfolder of the repository (the sandbox leaves a `.claude/` folder there): use paths from the worktree's top.")

middle = """## What you read

- Your suite as it stands: `tests/acceptance/W2-96/` on this branch (its README, support module and cases).
- The ticket file `.tickets/DAEO-ouet.md` (read-only) and the sources named in it; the first brief's design note is repeated below.
- For R1, how this repository's `tests/conftest.py` refuses a per-run base folder (read it, `git show w2/integrate:tests/conftest.py`).

## The behaviour to test

The design note (unchanged, the interface both you and the engineer build to):

""" + td1[td1.index("> **What it is.**"):td1.index("## What you write")].rstrip() + """

""" + addendum + """

## What you write

- Only inside `tests/acceptance/W2-96/`: a new case file for review 1 (say `test_w2_96_at_review_1.py`, a name no unit file can share) and its rows in the README's map (in the map form, so `gov accept` can still run the folder), plus support code where needed. A case of the first batch that the addendum changes is revised with its reason; say which in your return. Do not touch any other ticket's tests.
- One case or a small group per point R1 to R7, each with the marker leak checks the suite already makes (stdout, stderr, the JSON, the given `TMPDIR`, the project tree) where they apply:
  - R1: a planted project whose `conftest.py` refuses a run given a per-run base folder; `gov accept` reports per line (a passing line passes, a failing line fails), the given `TMPDIR` ends empty.
  - R2: SIGTERM, and separately SIGHUP, to the `gov` process alone while a planted test is running (wait until the planted test has recorded that it started); `gov` ends with exit code 128 plus the signal's number; the planted child is gone afterwards (it records nothing after the signal, or its process no longer exists); the given `TMPDIR` holds nothing; no marker in the output.
  - R3: a failing planted test that leaves a folder without permissions in its temporary folder; and a timeout while a planted test holds such a folder; in both the given `TMPDIR` ends empty.
  - R4: a row-form row naming a failing test with an unreadable KPI cell (`Failure: …` with no number; `Success 3a`); a heading-form table under `### Failure: …` with no number: each refused with `ACCEPT_MAP_UNREADABLE`, exit 1, `ok: false`, no test run (a planted test records whether it ran), no marker anywhere.
  - R5: `::test_x` and `stem::test_x` items map their tests (a failing one fails its line); a `test_` item and a `file::test_x` item that match no collected test make their line fail; a line whose items all match and pass still passes.
  - R6: a planted project whose pytest configuration names a `log_file` inside the project: no file is written, the marker logged by a test appears nowhere.
  - R7: a planted test that ends the session early by pytest's own exit call with the "tests failed" code while every case so far passed: `error` with kind `crash`, exit 4.
- Keep the new cases fast (the whole suite well under five minutes), deterministic, no network.
- **Red first:** run the whole folder to the end with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96-tests/src python3 -m pytest tests/acceptance/W2-96 -q -p no:cacheprovider -o tmp_path_retention_policy=failed` (on this branch `gov accept` does not exist, so the new cases are red for that reason; the lead red-checks them against the implementation after the merge). The README states each new case's expected red reason against an implementation without the addendum.
- An ambiguous point or a dispute with the addendum is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Commit only your test paths, in one commit, with the trailers in the final block (the git hooks are uninstalled; never `--no-verify`, never `core.hooksPath`):

    git commit -m "W2-96 (DAEO-ouet): review 1's acceptance cases for gov accept" --trailer "Task: DAEO-ouet" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-959" --trailer "Rewrite-Reason: review 1's findings F1, F2, F3, F5, F6, F7 (DEC-136)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

`Implements:` holds only ids the register holds (DEC-927). Then `git log --oneline -2` and `git status --short`.

"""
tail = td1[td1.index("## Return"):]
open(base + "briefs/td-2.md", "w", encoding="utf-8").write(head + middle + tail)
print(len(head + middle + tail))
