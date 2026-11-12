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

For each KPI line: the line, the tests under it, and the expected red reason of each. The opaque acceptance
runner, `gov accept`, reads the map and reports pass or fail per line, with counts, and nothing of the tests'
content; a test the map does not name is counted as unmapped, never named, and a README with no map is refused
(DEC-959 item 6). The form it reads:

- **A table with a KPI column and a test column.** Its header row has a column whose title starts with `KPI` and
  one whose title starts with `Test` or `File`. Each row names its line at the start of the KPI cell, and its tests
  in the test cell, each item a code span: a test file, a file and one case (`<file>::<case>`, as the project's
  test runner names a case), or a case's bare name. Text outside the code spans (the red reason, a note) is not
  read as a test.
- **Or a table under a heading that names its line** (`## success-1`): a table with a test or file column and no
  KPI column takes its line from the nearest heading above it.
- **The line names** are `success-N` and `failure-N`, N the line's number among the ticket's success or failure
  KPI lines, from 1. Accepted spellings: `success 1`, `S1`, `s-1`, `failure 2`, `F2`; `KPI 3` and `K3` name
  `success-3`. A cell or heading may name several lines, joined by `/`, `,`, `;` or `and`; bold marks are ignored.
  A table inside a fenced block is not read.
- **Refused, never answered with raw output:** a README with no map (`ACCEPT_NO_MAP`); a row with tests whose KPI
  cell names no line, or a table of tests under a heading that starts with `success`, `failure` or `KPI` but names
  no line (`ACCEPT_MAP_UNREADABLE`).
- **Counted:** a test the map does not name is counted under unmapped (passed and failed), never named; any failed
  test, mapped or not, fails the run. A line passes when at least one of its tests passed, none failed, and every
  test it names was found.

| KPI | Test | Red reason |
|---|---|---|
| success-1 | `<test file>::<case that reports each line>` | the command does not exist yet |
| failure-1 | `<test file>::<case that names only an error's kind>` | the error carries its message |
