
## W1-38 round: the adapter check applies the held-out step after its generation (2026-10-11; DEC-635, DEC-641, DEC-644)

Probed head `8ad901d5`, merged directly. Built: when the project has a held-out file, the adapter-portability check has the existing generator write the Read deny rules into the settings it generated in its temporary folder, then compares; a step that fails is the finding `HELD_OUT_STEP_FAILED` with the error's type only, and nothing is compared. The generator is unchanged. 18 acceptance cases and 13 unit cases added, none rewritten. Residuals, all on the Wave 2 list:

- **A project with a held-out file and no permissions and hooks sources can never be green:** rulesync writes no settings there and the step has nothing to write into (fail-closed; the template ships both sources).
- **The finding on the settings does not mention the step:** an owner who generated and forgot the step reads "is not what rulesync generates from its sources".
- **`HELD_OUT_STEP_FAILED` covers two causes** (a broken held-out file; generated settings missing or malformed), told apart only by the error's type; while it stands, drift in other generated files is not reported.
- **Two project roots:** the check judges the folder it runs in; the generator run by hand takes `CLAUDE_PROJECT_DIR` first. In a worktree session where that variable names the main tree, the step run by hand would write the other tree's settings. No case sets the two apart.
- **Not covered by a case:** an empty list under the key and a file unreadable for lack of rights (the reviewer ran both: red).
- **rulesync generating over an existing settings file keeps what it has no source for** (an env block, unknown keys, Read deny rules) and reorders: the apply procedure here generates into an empty folder and copies (DEC-645). An adopted project needs the same procedure as a command of the product.
- **`RULESYNC_FAILED` echoes up to 500 characters of rulesync's own error text** (older code): it could carry a held-out path only if a source named one.
- **Of the 18 cases, 6 answer the same on the code before the round** (pins, named in the suite's README).
- **The suite's README of round 4** still says every settings key reaches the file through a rulesync source; the new section corrects it for the held-out rules.
