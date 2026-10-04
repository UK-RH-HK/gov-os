# W1-47 acceptance tests — guard hardening: escape hatch, failed commands, oracle path

Ticket `DAEO-o4fg` (`W1-47`). Written by the Independent Test Designer before implementation (MR-3, DEC-069), from the
ticket's KPIs, Contract v4 (`CAP-62.a`, `CAP-58.f`, `CAP-49.c`, `CAP-25.f`, `CAP-25.g`) and DEC-083, DEC-152, DEC-153,
DEC-162, DEC-163, DEC-172, DEC-174, DEC-178, DEC-179. The second batch brings the suite in line with the owner's
answers to the first batch's six decision packages: DEC-213 and DEC-215 to DEC-219.

Run: `python3 -m pytest tests/acceptance/W1-47 -q -p no:cacheprovider` (970 cases, about 2.5 minutes before
implementation).

## How the tests work

- **Public interfaces only.** The hooks are run as the harness runs them: one JSON object on standard input, the
  decision on standard output. The settings files and `governance/project/held-out.yaml` are read as files. Nothing
  imports `src/gov/guard/`.
- **Nothing is run for real.** A command under test is text in the hook's input. The only commands executed are the
  small fixture commands of the failed-command and kernel-template tests (`echo changed >> README.md; exit 3`), in a
  temporary project. No network, no install, no Claude Code session. No test needs this machine, so none is
  `local_only`.
- **Temporary projects only.** The fixture project of W1-03 (both kernel hooks at `governance/kernel/hooks/`), and a
  *wired copy*: `src/gov`, the kernel hooks and `.claude/settings.json` of this repository copied into a new
  repository, so the commands the committed settings register run with no `PYTHONPATH` from the test. The wired copy
  copies those three places only; it does not copy the working tree, and it leaves the `Read(//…)` deny rules out of
  its copy of the settings file.
- **Helpers** come from `w1_03_support` (fixture project, a whole Bash call, findings) and `w1_05_support` (registered
  commands of a settings file), as W1-45's suite does. `w1_47_support.py` adds the held-out configuration, the
  settings rules, the guard call with a free `tool_input`, and a runner for the commands of the kernel template.

## The held-out path

No file here carries a held-out path, and no test opens, lists or stats anything under one.

- **The configuration (DEC-218).** `governance/project/held-out.yaml` was written by the owner. Its key is
  `held_out_paths`, a list of absolute paths.
- **The committed rule is checked statically.** `test_w1_47_oracle_rule.py` reads the list at run time and compares
  each path, as text, with the `Read` rules in `permissions.deny` of `.claude/settings.json`. The same file checks
  that no file of the ticket repeats a path (reading 20).
- **A value is never shown.** Every failure about it is a fixed text raised with `pytest.fail(..., pytrace=False)`,
  with no value and no count taken from the list; the object that holds the values hides them in its `repr`; no test
  id is built from one.
- **The guard is tested against a stand-in, built without the committed file.** `configure_stand_in` writes a
  `held-out.yaml` of its own into the temporary project, with `held_out_paths` holding the path of a directory made
  in the temporary area. `test_the_stand_in_configuration_is_built_without_the_committed_file` checks that only the
  static checks use the committed file.
- **The owner's commit of the file is the confirmation of the value** (DEC-218). No test can tell whether a
  configured path is the oracle's.

## KPI lines, tests and red reasons

"Red reason" is what the test says before implementation. "Green already" means the case passes today; the reason is
in the section below.

| KPI line | Tests | Red reason |
|---|---|---|
| Success 1, failure 1 — escape hatch `[CAP-62.a]` | `test_w1_47_escape_hatch.py`: denied for the five roles, a session with no role and two subagents (3 commands each); in all six permission modes; on a write inside the ticket paths; on an install (deny, not ask); through the committed settings. `test_the_template_s_guard_denies_the_escape_hatch` | `… with dangerouslyDisableSandbox: true by <who> was not denied by a rule: decision=allow` (`decision=ask` for the install). Template case: `template/governance/kernel/settings.json does not exist` |
| Success 2 — failed commands `[CAP-58.f]`, DEC-217 | `test_w1_47_failed_commands.py`: both events registered for Bash, and the same check on both, in this repository's settings and in the kernel template; a change, a new file and an acceptance test left by a failed command are caught, by the hook and through the committed settings. `test_w1_47_kernel_template.py` (30 cases): PreToolUse for every tool; every command through `$CLAUDE_PROJECT_DIR`; the template's commands, run in a project that has the kernel installed, give the guard's decisions (deny out of scope, allow in scope, ask on an install, escape hatch, held-out path) and the containment check's (a change out of scope reported after both events, an acceptance test restored after a failed command, a change in scope left alone) | Template cases: `template/governance/kernel/settings.json does not exist: the kernel template has no settings file`. This repository's cases are green already |
| Success 3, failure 3 — committed `Read` deny rule `[CAP-49.c]`, DEC-218 | `test_w1_47_oracle_rule.py`: `held_out_paths` is a non-empty list of absolute paths; a deny rule built from every path of the list is present; no path is in an `ask` or `allow` rule | `permissions.deny of .claude/settings.json carries no Read rule built from a path of held_out_paths …`. The other cases are green already |
| Success 4, failure 2 — guard rule `[CAP-49.c]`, DEC-215, DEC-218 | `test_w1_47_oracle_guard.py`: 31 plain calls (Read, Grep, Glob, 16 Bash forms, Write, Edit, NotebookEdit, four MCP shapes, an unknown tool) by the five roles and a session with no role; a second place for the stand-in; subagents; every permission mode; while frozen; the path follows the configuration; every path of the list; through the committed settings; other paths stay open. `test_w1_47_oracle_naming.py`: 17 calls that hold the path in free text or code, 25 that reach it through a relative path, `..`, `~`, `$HOME` or a symbolic link, each by the orchestrator, the engineer and a session with no role; the same forms on a directory that is not held out stay open; the exception for the two files that hold the path. `test_w1_47_oracle_config.py`: a missing file means no rule; a file with no key or not of the stated shape stops every call | `… on the stand-in oracle path by <who> was not denied by a rule: decision=allow`; `…, with the stand-in held-out path in its input, by <who> was not denied by a rule: decision=allow`; `…, which reaches the stand-in held-out path, by <who> was not denied by a rule: decision=allow`; `… with a governance/project/held-out.yaml that is broken (<kind>) was let through: decision=allow` |
| Failure 4 — a test names the oracle | `test_no_acceptance_test_of_this_ticket_names_a_configured_path`, `test_the_stand_in_configuration_is_built_without_the_committed_file` | None: green already |
| Failure 7 — an implementation file names the oracle | `test_no_implementation_file_names_a_configured_path`, `test_the_settings_file_names_a_configured_path_in_its_read_deny_rule_only` | None: green already; they keep the implementation from repeating a path |
| Success 5, failure 5 — no ask rule `[CAP-25.f]` | `test_w1_47_settings_rules.py`: one case for each of the eleven rules; no rule on a longer command that begins with one; not moved to `deny` or `allow`; `Bash(sudo:*)` and the six other deny rules in place; the kernel template carries none | `permissions.ask of .claude/settings.json still carries ['Bash(pip:*)']` and ten more; kernel template: `template/governance/kernel/settings.json does not exist` |
| Success 6, failure 6 — four `uv` forms `[CAP-25.g]`, DEC-216 | `test_w1_47_uv_installs.py`: 41 commands ask for the orchestrator (23 of the first batch, 18 with a value option or `-w`); the four plain forms and the two forms DEC-216 words ask in all six permission modes; the 41 are denied for engineer, test designer and auditor; sixteen other `uv` commands stay unclassified, five of them with a value option in front; W1-04's three `uv` installs still ask | `` `uv --directory sub add requests` by the orchestrator did not ask: decision=allow `` and `` `…` by engineer was not denied by a rule: decision=allow `` |
| Success 6, the research role's exception | None here: carried by W1-46's test design (DEC-219) | — |
| Success 7 — no session role, no wide scope | `test_w1_47_session_role.py`: an orchestrator subagent has no wide scope when `GOV_ROLE` is unset, empty or blank, or names another role; the orchestrator's own session keeps it; `tests/unit/guard` passes | None: green already (reading 19) |
| "The acceptance tests of W1-04 still pass" (success 5 and 6) | `tests/acceptance/W1-04`, run as it stands | Green today: 336 passed |

## Green before implementation (247 of 970)

- **Escape hatch, 16.** The controls: the same call with the field absent or `false` is let through.
- **Failed commands, 10.** `PostToolUseFailure` for Bash is registered in this repository's settings since W1-05
  (3 cases), and the hook has handled the event since W1-03 (6 cases, and 1 through the committed settings). The
  ticket's body says so: this ticket makes the registration a tested requirement.
- **Held-out configuration, 8.** With no `held-out.yaml` in the project there is no held-out rule (reading 7).
- **Guard rule, plain forms, 57.** Calls on other paths are allowed (42). A write under the stand-in is denied by the
  allow-list already for a session with no role, for the engineer inside the repository, and `cp` out of it for every
  role (15). They are kept, because the KPI is "whatever the tool and whatever the call does".
- **Guard rule, DEC-215, 55.** The same forms on a directory that is not held out are allowed (37); the
  orchestrator's edits to the two files that hold the path are allowed (6) and the other roles' are denied by the
  allow-list (8); four writes by a session with no role are denied by the allow-list already.
- **Committed rule, 6.** The owner wrote `held-out.yaml`, so the list is there, and nothing names a path yet: not an
  `ask` or `allow` rule, not the settings file, not an implementation file, not this suite. Only the deny rule itself
  is missing.
- **Settings rules, 10.** The seven deny rules are there today (8 cases), and the install rules sit in `ask`, not in
  `deny` or `allow` (2 cases).
- **`uv`, 67.** The commands this change must not classify are allowed today (64), and W1-04's three `uv` installs
  ask today.
- **Session role, 18.** DEC-179 says of the defect: "Its only caller passes the argument, so no session gains a write
  today." What the hook shows is therefore right already; these cases keep it right.

The 36 kernel-template cases are reported by pytest as errors, not failures: the fixture that loads
`template/governance/kernel/settings.json` fails with the fixed text above.

**The kernel-template tests against a candidate file.** They cannot go past their fixture before the file exists. To
see that they test what they say, they were run once against a throw-away settings object (PreToolUse with no
matcher, both post-command events for Bash, each command
`python3 "$CLAUDE_PROJECT_DIR/governance/kernel/hooks/<hook>.py"`), outside the repository and with no change to the
guard: 34 passed, 2 failed, the escape hatch and the held-out path, both with `decision=allow`.

## Readings

Where the sources do not spell a point out, this is what the tests take it to mean. Readings 5, 8, 10, 13, 14 and 16
were rewritten for the owner's answers; 22 to 27 are new.

1. **"Denies" is a rule's decision.** Exit code 0 with `permissionDecision: deny`. Exit code 2 stops a call too, but
   it is the hook reporting its own failure (DEC-110). `assert_denied_by_rule` asks for the first.
2. **"Whatever the role" / "every role"** is the five known roles, a session that declares no role, and a subagent
   (an engineer subagent and one of no known type). The research role does not exist yet (W1-46).
3. **`dangerouslyDisableSandbox: true`** is the JSON value `true` in the Bash call's `tool_input`. Other truthy
   values (`"true"`, `1`) are not tested.
4. **The escape hatch on an install is denied, not asked.** A prompt would let an approval send the command out of
   the sandbox.
5. **`held-out.yaml` holds `held_out_paths`, a non-empty list of absolute paths** (DEC-218). The static checks fail
   on anything else, with a fixed text. A trailing `/` on an entry is ignored.
6. **The committed rule's form.** `//<path>` is the absolute form of a path in a permission rule, so the rule is
   `Read(/` + a configured value + `)`. A trailing `/` or `/**` after the value is accepted; nothing else is. There
   is one such rule, at least, for every path of the list.
7. **A missing `held-out.yaml` means no held-out rule.** This is a reading, not an answer of the owner: DEC-218
   speaks of a missing key and a broken file. The fixture projects of W1-02…W1-45 have no such file and expect their
   calls to be allowed; those suites hold the guard to it, and eight cases here state it.
8. **"Names the held-out path" (DEC-215).** Literally anywhere: the configured path as a substring of any string
   value of the input, at any depth, whatever the tool; the Bash `description` field counts, and so do free text and
   code inside a command. Reached without being written out: a path relative to the session's working directory, a
   path through `..`, `~` at the start of a path (in a Bash command and in a file tool's path field), `$HOME` in a
   Bash command, and a symbolic link to the directory or to one file of it. Keys of the input are not tested, nor
   `${HOME}`, nor other variables, nor a configured path that is itself a link.
9. **"Any other tool"** is shown for Write, Edit, NotebookEdit, Agent, WebFetch, TodoWrite, MCP tools with the path
   in a field, in a list, in a nested object and in free text, and a tool name no list written today can hold.
10. **The stand-in.** A directory with two files and a notebook, in the temporary area, in the temporary project, or
    in the temporary home directory, named by a `held-out.yaml` the test writes itself. The first batch built that
    file from the committed one; it no longer does (DEC-218).
11. **"Decides install commands alone"** means the rules were removed, not moved: none of them in `deny` (which would
    stop the orchestrator's prompt, DEC-083) or in `allow`. A rule counts when its command prefix is one of the
    eleven, with `:*`, ` *` or `*` as its wildcard, or is a longer command that begins with one.
12. **"The other deny rules"** are the six that sit beside `Bash(sudo:*)` today.
13. **The kernel template's settings file** is `template/governance/kernel/settings.json` (DEC-217), a JSON object in
    the shape of a Claude Code settings file. "PreToolUse for every tool": a command that names `pretooluse` is
    registered for each write tool, each read-only tool, the other tools of W1-05's list and a tool name not known
    today. "The containment check" is a command that names `posttooluse`, for Bash. "Through `$CLAUDE_PROJECT_DIR`":
    every registered command holds that variable and none holds this repository's own directory. The template
    carries no install rule (ticket body).
14. **"A project that has the kernel installed"** is W1-03's fixture project: both hooks at `governance/kernel/hooks/`
    (where Copier puts them) and the `gov` package importable, as package DP-4's option 1 has it. No test installs
    anything, so the package is put on Python's path. The project's own `src/gov` is a stub and its `template/`
    holds no working hook, so a command written for this repository's layout fails the behavioural cases.
15. **`CAP-58.f`, "a call refused by a deny rule reaches no hook"** is the harness's behaviour. It needs a session
    and is not tested.
16. **`uv`'s value options (DEC-216).** `--directory`, `--project`, `--cache-dir` and `--config-file` take the next
    word as their value; the value is skipped even when it is the name of a subcommand
    (`uv --directory run add requests` is an install; `uv --directory add run python script.py` is not). `-w` is
    tested as an option of `uv run` in front of the command to run. Not tested: `-w` joined to its value, a value
    option in front of W1-04's `uv pip install`, and `uvx` with a value option.
17. **`uv run --with-requirements` is not classified.** The KPI says a `uv run` without `--with` is not classified;
    `governance/project/bootstrap.md` lists `uv run --with-requirements` under "What stays without a prompt". So do
    `uv lock`, `uv remove`, `uv venv`, `uv pip sync`, `uv pip list`, `uv tool run` and `uv --version` (ticket body:
    "The other commands on the list stay without a prompt").
18. **Product-spec** is not named by the `uv` KPI and is not asserted there.
19. **Success 7.** The function is internal and its one caller always passes the argument, so no public interface
    can leave it out. The tests show the hook's behaviour around a missing session role, and that `tests/unit/guard`
    passes. Whether a builder test calls the function without the argument is for the reviewer to read.
20. **Failure 4 and failure 7 are checked by comparing text.** The committed list is read once more than for the
    deny rule itself: to check that the settings file names a path in that rule only, and that no implementation
    file and no file of this suite repeats one. Nothing is opened under a path and only file names are shown. See
    DP-7. "Reads the qualification oracle" cannot be shown by an automatic check.
21. **Failure 1, "reaches execution"** is tested as the hook's decision, in every permission mode. Whether the
    harness honours a deny is W1-05's ground.
22. **"Fails closed" (DEC-218)** is tested as: the call does not go through. A deny decision and exit code 2 both
    count; a finding is not required. It holds for every call, a Read of an unrelated file included, for the
    orchestrator, the engineer and a session with no role.
23. **"No such key, or a broken file"** is: an empty file, a file of comments, another key, a misspelt key, text
    that is not YAML, a document that is not a mapping, the key with no value, the key holding one string, the key
    holding a mapping, a list holding a number, and a list holding a relative path. An empty list is not tested
    (DP-8). A file that cannot be opened is not tested.
24. **The exception of DEC-215** is tested for the Write and Edit tools on `governance/project/held-out.yaml` and
    `.claude/settings.json` of the project, with the path in `content`, `new_string` or `old_string`. "Their usual
    role rules still apply": the orchestrator's edit is allowed, as it is today; the engineer's, the test designer's,
    the auditor's and a session with no role's is denied, as it is today. The same edit to any other file is denied,
    `governance/project/bootstrap.md` and `.claude/settings.local.json` included. A Bash command that names the path
    is denied whatever file it writes.
25. **The accepted residual of DEC-215** has no test in either direction: a parent directory given to a recursive
    tool, a glob that matches without naming, and a look-alike sibling. No control of this suite uses such a call.
26. **Every path of the list is hidden** (DEC-218 says "a list"): shown with two stand-ins in different directories.
27. **The wired copy carries no held-out path.** The committed settings file will hold the path in its `Read` rule;
    the copy leaves the `Read(//…)` rules out. The registered commands are taken from the committed file itself.

## Decision packages

### Answered

| Package | Answer | What the suite does |
|---|---|---|
| DP-1 — what "names the oracle path" covers | **DEC-215**, option 3: literal anywhere, relative path, `..`, `~`, `$HOME`, symbolic link; exception for the two files that hold the path; parents, globs and look-alike siblings are an accepted residual | `test_w1_47_oracle_naming.py` (181 cases); readings 8, 24, 25 |
| DP-2 — the research role's exception | **DEC-219**, option 1: tested in W1-46's test design | Marked as carried; no test here |
| DP-3 — `uv` options that take a value | **DEC-216**, option 2: `--directory`, `--project`, `--cache-dir`, `--config-file`, and `uv run -w` | 104 more cases in `test_w1_47_uv_installs.py`; reading 16 |
| DP-4 — the kernel template's settings file | **DEC-217**, option 1: `template/governance/kernel/settings.json`, PreToolUse for every tool, both post-command events, commands through `$CLAUDE_PROJECT_DIR`, a behavioural test | `test_w1_47_kernel_template.py` (30 cases); the six earlier template cases ask for that file by name; readings 13, 14 |
| DP-5 — the shape of `held-out.yaml` | **DEC-218**: the owner wrote the file, key `held_out_paths`; a missing key or a broken file fails closed; the deny rule is generated by a script | `test_w1_47_oracle_config.py` (99 cases); the static checks cover every path of the list; the stand-in no longer uses the committed file; readings 5, 7, 10, 22, 23, 26 |
| DP-6 — W1-05's fixture copies the working tree | **DEC-213**, option 1: the oracle is outside the repository | Nothing changes |

### Open

#### DP-7 — May the committed list be read for the two "names the path" checks?

- **Question.** The second batch's brief allows a test to load `held-out.yaml` "for one purpose only: to check that
  the committed `Read` deny rule is built from it". Failure 4 and failure 7 of the ticket are tested by two more
  comparisons of the same loaded values: against the text of the ticket's implementation files and against the text
  of this suite. Do those two stay?
- **Why now.** Without them failure 4 and failure 7 have no test that knows the value; with them the list is read
  for more than the one purpose. Both instructions cannot be met to the letter.
- **Options.** (1) They stay: three static comparisons of text, fixed failure texts, file names only, nothing opened
  under a path. (2) They go: `test_no_implementation_file_names_a_configured_path` and
  `test_no_acceptance_test_of_this_ticket_names_a_configured_path` are removed; failure 7 keeps the settings-file
  check and failure 4 keeps the check that the stand-in is built without the committed file; whether a file repeats
  a path is then for the reviewer, who may not name it either.
- **Impact.** Under option 2 nothing automatic notices an implementation file or a test that repeats a path.
- **Reversibility.** High: two cases.
- **Cost.** None either way.
- **Recommendation.** Option 1, which is what the suite does now.
- **Confidence.** Medium.

#### DP-8 — `held_out_paths: []`

- **Question.** Is a file whose list is empty "broken" (fail closed), or a valid file that hides nothing?
- **Why now.** DEC-218 gives the shape as "a list of absolute paths" and names a missing key and a broken file. An
  empty list is neither clearly. The suite does not test it.
- **Options.** (1) Fail closed: an empty list is not the stated shape. (2) No held-out rule, as with a missing file.
- **Impact.** Option 2 lets an emptied list switch the rule off silently, which DEC-179 calls a defect. Option 1
  means a product repository with nothing held out carries no `held-out.yaml` at all.
- **Reversibility.** High.
- **Cost.** One line in the guard and four cases here.
- **Recommendation.** Option 1.
- **Confidence.** Medium.

## Earlier tests

No earlier acceptance test is changed, and none is made wrong by this ticket's KPIs as far as their text shows:

- No earlier test requires an install or download ask rule in the committed settings. W1-01 and W1-05 read
  `permissions.deny` and the hooks only; W1-04 and W1-05 assert the hook's `ask`, which stays.
- The fixture projects of the earlier suites have no `held-out.yaml`; reading 7 keeps their calls allowed.
- No rewrite after implementation is expected.
