# Test design: kinds, cost and the README map

A reference file of the test-design skill, one level below `SKILL.md` (DEC-889 item 11 c, DEC-951 item 5, DEC-959
item 6). A project's own values stand as `<placeholders>` (DEC-539); the limits below are defaults it may set
otherwise in <the project's test settings>.

## The kinds

| Kind | What it is | How it is declared | Default limit per test |
|---|---|---|---|
| unit | one function or module, in process; the implementer's own tests, never the designer's | its folder, `<the project's unit-test path>` | under 1 s |
| acceptance | a KPI line's behaviour through the public interface, in process or one child process, on a minimal temporary fixture | its folder, the ticket's acceptance path | under 5 s |
| live or harness | a real model session, a real daemon, the network or the agent harness | `<the project's marker for live tests>`; outside the default run where the project allows | stated in the test, at most `<limit>` |
| dev-tier | runs on the project's dev-tier repositories, named only and cloned into a temporary folder | `<the project's dev-tier marker>` | under 60 s |
| load-sensitive | asserts a time or a latency | `<the project's marker>`; times the code's own work, never the machine's load (DEC-979 item 1) | under 5 s |
| repository-state | reads the live repository's own records, not the code | `<the project's marker>`; listed in the record-reading set | under 5 s |

## Cost, and how it is measured

- Each test's run time is measured from the test runner's own per-test durations (a durations report or the JUnit
  XML times) on the designer's red run, and again on the lead's run. The README gives each file's total.
- A test past its kind's limit is made smaller (a smaller fixture, fewer cases), or declared as the slower kind
  with its reason. A per-test time limit stops a hung test (DEC-889 item 11 b).
- A fixture is a temporary repository built from scratch with only what the case needs; never a copy of the whole
  working tree, and never a nested run of a whole suite inside a test.

## The README map

For each KPI line: the line, the tests under it, and the expected red reason of each. The project's opaque
acceptance runner reads the map and reports pass or fail per line, with counts, and nothing of the tests' content;
a test the map does not name is counted as unmapped, never named, and a README with no map is refused (DEC-959
item 6). The exact syntax follows that runner. In the form its in-progress code reads, a table with a `KPI` column
naming the line (`success-1`, `failure-2`) and a `Test` column naming files or cases in backticks:

| KPI | Test | Red reason |
|---|---|---|
| success-1 | `test_example.py::test_the_command_reports_each_line` | the command does not exist yet |
| failure-1 | `test_example.py::test_a_run_error_names_only_its_kind` | the error carries its message |
