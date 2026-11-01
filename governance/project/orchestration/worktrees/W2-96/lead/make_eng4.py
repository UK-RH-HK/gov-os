"""Build briefs/eng-4.md (run review 1's merged cases once, fix to the spec) from eng-2.md and design-r1.md."""

base = "/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/"
text = open(base + "briefs/eng-2.md", encoding="utf-8").read()
addendum = open(base + "design-r1.md", encoding="utf-8").read()

text = text.replace("# Brief: engineer, W2-96 (DAEO-ouet), run 1, second engineer",
                    "# Brief: engineer, W2-96 (DAEO-ouet), run 1, review 1's test run")
start = text.index("**Where things stand.**")
end = text.index("## Step 0")
text = text[:start] + (
    "**Where things stand.** `gov accept` is built (`9859695c8fcc`) and review 1's addendum below is built on it "
    "(`d8ac34ff71de`: `src/gov/accept/runner.py`, `tests/unit/accept/test_w2_96_accept.py`; 41 unit tests pass). "
    "The independent test designer's cases, review 1's included, are merged on this branch (`382ef3b6`: 79 cases). "
    "The R4 rule is read literally: in a map table with a KPI column, any body row with a backticked item in its "
    "Test/File cell whose KPI cell begins with no line name the reader takes refuses the run "
    "(`ACCEPT_MAP_UNREADABLE`), and that refusal wins over `ACCEPT_NO_MAP`. Your job: run the acceptance tests "
    "once and fix the code to the specification where they fail. You may read and change the earlier engineers' "
    "code: it is this ticket's own.\n\n") + text[end:]
marker = "Points that make this fail closed, never open:"
text = text.replace(marker, addendum + "\n" + marker)
text = text.replace(
    "3. Then run your unit tests again (`tests/unit/accept`) and return.",
    "3. Then run `gov accept` on this ticket once and quote its JSON: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src "
    "python3 -m gov.cli.main accept DAEO-ouet --json` (it must run in this repository and report per line).\n"
    "4. Run your unit tests again (`tests/unit/accept`) and return.")
text = text.replace("The suite takes about a minute.", "The suite takes about two minutes.")
open(base + "briefs/eng-4.md", "w", encoding="utf-8").write(text)
print(len(text), "4. Run your unit" in text, "Review 1's addendum" in text)
