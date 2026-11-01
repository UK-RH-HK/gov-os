"""Build briefs/eng-2.md from eng-1.md: the build exists and the tests are merged; run them and fix to the spec."""
import re

base = "/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/briefs/"
text = open(base + "eng-1.md", encoding="utf-8").read()
text = text.replace("# Brief: engineer, W2-96 (DAEO-ouet), run 1", "# Brief: engineer, W2-96 (DAEO-ouet), run 1, second engineer")
text = text.replace(
    "You build the code to the specification and its KPIs, never to the tests (DEC-957); your test-driven development is your own unit tests.",
    "You build the code to the specification and its KPIs, never to the tests (DEC-957); your test-driven development is your own unit tests.\n\n"
    "**Where things stand.** A first engineer built `gov accept` and committed it (`9859695c8fcc`: `src/gov/accept/__init__.py`, "
    "`command.py`, `runner.py`, `tests/unit/accept/test_w2_96_accept.py`; 25 unit tests pass). The lead has merged the independent "
    "acceptance tests into this branch (`986fa7cf`). Your job: run the acceptance tests once, and fix the code to the specification "
    "where they fail (section \"The acceptance tests\" below). You may read and change the first engineer's code: it is this ticket's own.")
start = text.index("## The acceptance tests, once ready")
end = text.index("## Return")
new = (
    "## The acceptance tests (already merged)\n\n"
    "The independent test designer's tests are in `tests/acceptance/W2-96/` on this branch (merged by the lead in `986fa7cf`). "
    "You never open them (DEC-820 (c)).\n\n"
    "1. Run them **through pytest this once** (gov accept is what is being built, so it cannot be the judge of its own first run), "
    "reading results only: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m pytest tests/acceptance/W2-96 -q "
    "-p no:cacheprovider -o tmp_path_retention_policy=failed --tb=line`. You see names, pass or fail and the one-line failure "
    "messages; you never open the test files. The suite takes about a minute.\n"
    "2. If some fail: fix the code to the specification and the design note (never to a test's text), add a unit test for the "
    "behaviour, commit, and run them again; at most three runs in all. A failure you believe the specification does not ask for "
    "is a package, with the test's name and its one-line message, and you leave that behaviour as the specification says.\n"
    "3. Then run your unit tests again (`tests/unit/accept`) and return. Commit each fix with the trailers above "
    "(`--trailer \"Implements: DEC-959, DEC-317\"`).\n\n"
)
text = text[:start] + new + text[end:]
text = text.replace("- **Commit your work before any longer run.**", "- **Commit each fix before the next run.**")
open(base + "eng-2.md", "w", encoding="utf-8").write(text)
print(len(text))
