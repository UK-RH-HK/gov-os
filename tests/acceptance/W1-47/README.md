# W1-47 acceptance tests — guard hardening: escape hatch, failed commands, oracle path

Ticket `DAEO-o4fg` (`W1-47`). Written by the Independent Test Designer before implementation (MR-3, DEC-069), from the
ticket's KPIs, Contract v4 (`CAP-62.a`, `CAP-58.f`, `CAP-49.c`, `CAP-25.f`, `CAP-25.g`) and DEC-083, DEC-152, DEC-153,
DEC-162, DEC-163, DEC-172, DEC-174, DEC-178, DEC-179.

Run: `python3 -m pytest tests/acceptance/W1-47 -q -p no:cacheprovider` (553 cases, about 50 s before implementation).

## How the tests work

- **Public interfaces only.** The hooks are run as the harness runs them: one JSON object on standard input, the
  decision on standard output. The settings files and `governance/project/held-out.yaml` are read as files. Nothing
  imports `src/gov/guard/`.
- **Nothing is run for real.** A command under test is text in the hook's input. The only commands executed are the
  small fixture commands of the failed-command tests (`echo changed >> README.md; exit 3`), in a temporary project.
  No network, no install, no Claude Code session. No test needs this machine, so none is `local_only`.
- **Temporary projects only.** The fixture project of W1-03 (both kernel hooks at `governance/kernel/hooks/`), and a
  *wired copy*: `src/gov`, the kernel hooks and `.claude/settings.json` of this repository copied into a new
  repository, so the commands the committed settings register run with no `PYTHONPATH` from the test. The wired copy
  copies those three places only; it does not copy the working tree.
- **Helpers** come from `w1_03_support` (fixture project, a whole Bash call, findings) and `w1_05_support` (registered
  commands of a settings file), as W1-45's suite does. `w1_47_support.py` adds the oracle configuration, the settings
  rules and the guard call with a free `tool_input`.

## The qualification oracle

No file here carries the oracle's path, and no test opens, lists or stats anything under it.

- **The committed rule is checked statically.** The test reads the value from `held-out.yaml` at run time and compares
  it, as text, with the `Read` rules in `permissions.deny` of `.claude/settings.json`.
- **The value is never shown.** Every failure about it is a fixed text raised with `pytest.fail(..., pytrace=False)`;
  the object that holds it hides it in its `repr`; no test id is built from it.
- **The guard is tested against a stand-in.** `configure_stand_in` takes the committed `held-out.yaml`, replaces its
  one path value with the path of a directory made in the temporary area, and writes the result into the temporary
  project. The test knows nothing of the file's keys, and the temporary project never names the oracle.
- **The owner confirms the value at close** (DEC-162). No test can tell whether the configured path is the oracle's.

## KPI lines, tests and red reasons

"Red reason" is what the test says before implementation. "Green already" means the case passes today; the reason is
in the section below.

| KPI line | Tests | Red reason |
|---|---|---|
| Success 1, failure 1 — escape hatch `[CAP-62.a]` | `test_w1_47_escape_hatch.py`: denied for the five roles, a session with no role and two subagents (3 commands each); in all six permission modes; on a write inside the ticket paths; on an install (deny, not ask); through the committed settings | `… with dangerouslyDisableSandbox: true by <who> was not denied by a rule: decision=allow` (`decision=ask` for the install) |
| Success 2 — failed commands `[CAP-58.f]` | `test_w1_47_failed_commands.py`: both events registered for Bash, and the same check on both, in this repository's settings and in the kernel template; a change, a new file and an acceptance test left by a failed command are caught, by the hook and through the committed settings | Kernel template: `no file matches template/governance/kernel/settings*`. Everything else is green already |
| Success 3, failure 3 — committed `Read` deny rule `[CAP-49.c]` | `test_w1_47_oracle_rule.py`: the configuration holds one absolute path; the deny rule built from it is present; the path is in no `ask` or `allow` rule | `governance/project/held-out.yaml does not exist` |
| Success 4, failure 2 — guard rule `[CAP-49.c]` | `test_w1_47_oracle_guard.py`: 31 calls (Read, Grep, Glob, 16 Bash forms, Write, Edit, NotebookEdit, four MCP shapes, an unknown tool) by the five roles and a session with no role; a second place for the stand-in; subagents; every permission mode; while frozen; the path follows the configuration; through the committed settings; other paths stay open | `governance/project/held-out.yaml does not exist`. With the file in place and no rule: `… on the stand-in oracle path by <who> was not denied by a rule: decision=allow` (shown in a simulated root, see below) |
| Failure 4 — a test names the oracle | `test_no_acceptance_test_of_this_ticket_names_the_configured_path` | `governance/project/held-out.yaml does not exist` |
| Failure 7 — an implementation file names the oracle | `test_no_implementation_file_names_the_configured_path`, `test_the_settings_file_names_the_path_in_the_read_deny_rule_only` | `governance/project/held-out.yaml does not exist` |
| Success 5, failure 5 — no ask rule `[CAP-25.f]` | `test_w1_47_settings_rules.py`: one case for each of the eleven rules; no rule on a longer command that begins with one; not moved to `deny` or `allow`; `Bash(sudo:*)` and the six other deny rules in place; the kernel template carries none | `permissions.ask of .claude/settings.json still carries ['Bash(pip:*)']` and ten more; kernel template: `no file matches …settings*` |
| Success 6, failure 6 — four `uv` forms `[CAP-25.g]` | `test_w1_47_uv_installs.py`: 23 commands ask for the orchestrator; the four plain forms ask in all six permission modes; the 23 are denied for engineer, test designer and auditor; eleven other `uv` commands stay unclassified; W1-04's three `uv` installs still ask | `` `uv add requests` by the orchestrator did not ask: decision=allow `` and `` `…` by engineer was not denied by a rule: decision=allow `` |
| Success 7 — no session role, no wide scope | `test_w1_47_session_role.py`: an orchestrator subagent has no wide scope when `GOV_ROLE` is unset, empty or blank, or names another role; the orchestrator's own session keeps it; `tests/unit/guard` passes | None: green already (see the reading below) |
| "The acceptance tests of W1-04 still pass" (success 5 and 6) | `tests/acceptance/W1-04`, run as it stands | Green today: 336 passed |

## Green before implementation (101 of 553)

- **Escape hatch, 16.** The controls: the same call with the field absent or `false` is let through.
- **Failed commands, 10.** `PostToolUseFailure` for Bash is registered in this repository's settings since W1-05
  (3 cases), and the hook has handled the event since W1-03 (6 cases, and 1 through the committed settings). The
  ticket's body says so: this ticket makes the registration a tested requirement.
- **Settings rules, 10.** The seven deny rules are there today (8 cases), and the install rules sit in `ask`, not in
  `deny` or `allow` (2 cases).
- **`uv`, 47.** The commands this change must not classify are allowed today (44), and W1-04's three `uv` installs
  ask today.
- **Session role, 18.** DEC-179 says of the defect: "Its only caller passes the argument, so no session gains a write
  today." What the hook shows is therefore right already; these cases keep it right.

After implementation, some oracle cases would also pass without the new rule: a write under the stand-in by a
session with no role is denied by the allow-list already. They are kept, because the KPI is "whatever the tool and
whatever the call does".

## A simulated root

The oracle tests cannot fail on the guard before `held-out.yaml` exists. To see their real red reason, the suite was
run once in a throw-away root built in the session's scratch area: this repository's guard files, a `held-out.yaml`
with a made-up path, the matching `Read` rule, no ask rules and a template settings file, and no change to the guard.
Result: 371 failed, 182 passed. Every failure was `was not denied by a rule: decision=allow`,
`did not ask: decision=allow`, or the escape-hatch install's `decision=ask`. The static checks, the controls and the
writes the allow-list already denies passed. The made-up path appeared in no output of the static tests.

## Readings

Where the sources do not spell a point out, this is what the tests take it to mean.

1. **"Denies" is a rule's decision.** Exit code 0 with `permissionDecision: deny`. Exit code 2 stops a call too, but
   it is the hook reporting its own failure (DEC-110). `assert_denied_by_rule` asks for the first.
2. **"Whatever the role" / "every role"** is the five known roles, a session that declares no role, and a subagent
   (an engineer subagent and one of no known type). The research role does not exist yet (W1-46).
3. **`dangerouslyDisableSandbox: true`** is the JSON value `true` in the Bash call's `tool_input`. Other truthy
   values (`"true"`, `1`) are not tested.
4. **The escape hatch on an install is denied, not asked.** A prompt would let an approval send the command out of
   the sandbox.
5. **`held-out.yaml` holds exactly one absolute path.** The file's keys are not specified anywhere, so the tests look
   for the one string value that starts with `/`. Two such values, or none, fail the test. See DP-5.
6. **The committed rule's form.** `//<path>` is the absolute form of a path in a permission rule, so the rule is
   `Read(/` + the configured value + `)`. A trailing `/` or `/**` after the value is accepted; nothing else is.
7. **A missing `held-out.yaml` means no oracle rule.** The fixture projects of W1-02…W1-45 have no such file and
   expect their reads to be allowed; those suites hold the guard to it. A malformed file is not tested (DP-5).
8. **"Names the oracle path"**, as far as tested: the configured absolute path, word for word, as a path of its own
   or as the start of a path under it. In Bash, a word of the command, bare or quoted, in any position. In another
   tool, the whole value of an input field at any depth. Everything else is DP-1.
9. **"Any other tool"** is shown for Write, Edit, NotebookEdit, MCP tools with the path in a field, in a list and in
   a nested object, and a tool name no list written today can hold.
10. **The eleven ask rules.** A rule counts when its command prefix is one of the eleven, with `:*`, ` *` or `*` as
    its wildcard, or is a longer command that begins with one (`Bash(pip install:*)`).
11. **"Decides install commands alone"** means the rules were removed, not moved: none of them in `deny` (which would
    stop the orchestrator's prompt, DEC-083) or in `allow`.
12. **"The other deny rules"** are the six that sit beside `Bash(sudo:*)` today.
13. **The kernel template's settings file** is the one file matching `template/governance/kernel/settings*` (the
    ticket's `allowed_paths`), a JSON object in the shape of a Claude Code settings file. "The containment check" in a
    settings file is a command that names `posttooluse`. The template carries no install rule (ticket body). See DP-4.
14. **"A command that writes a file and then fails is caught"** is tested on the hook and through this repository's
    settings. It is not run through the template's commands (DP-4).
15. **`CAP-58.f`, "a call refused by a deny rule reaches no hook"** is the harness's behaviour. It needs a session
    and is not tested.
16. **"With or without options before the subcommand"** is tested with options that are one word: a flag (`-q`,
    `--quiet`, `--no-cache`, `--offline`) or `--name=value`. See DP-3.
17. **`uv run --with-requirements` is not classified.** The KPI says a `uv run` without `--with` is not classified;
    `governance/project/bootstrap.md` lists `uv run --with-requirements` under "What stays without a prompt". So do
    `uv lock`, `uv remove`, `uv venv`, `uv pip sync`, `uv pip list`, `uv tool run` and `uv --version` (ticket body:
    "The other commands on the list stay without a prompt").
18. **Product-spec** is not named by the `uv` KPI and is not asserted there.
19. **Success 7.** The function is internal and its one caller always passes the argument, so no public interface
    can leave it out. The tests show the hook's behaviour around a missing session role, and that `tests/unit/guard`
    passes. Whether a builder test calls the function without the argument is for the reviewer to read.
20. **Failure 7, "reads the qualification oracle".** No automatic check can show this. The test checks naming only,
    over the files of the ticket's `allowed_paths`.
21. **Failure 1, "reaches execution"** is tested as the hook's decision, in every permission mode. Whether the
    harness honours a deny is W1-05's ground.

## Decision packages

### DP-1 — What "names the oracle path" covers beyond the literal absolute path

- **Question.** Which of these must the guard deny? (a) a relative path or one with `..` that resolves under the
  oracle; (b) `~`, `$HOME` or another variable in front; (c) a symbolic link to it; (d) a parent directory used by a
  recursive tool (`grep -r x <parent>`, Grep or Glob with `path` = the repository root); (e) a glob that matches it
  without naming it; (f) the path inside free text of another tool (an Agent prompt, a WebFetch URL, a Grep
  `pattern`, the `content` of a Write, the `old_string` of an Edit); (g) the path inside code in a Bash command
  (`python3 -c "open('<path>/x')"`); (h) a sibling whose name begins with the same characters (`<path>-old`).
- **Why now.** The KPI and its failure line say "names" and "whatever the tool"; the tests need a rule to pin.
  Point (f) also decides whether the orchestrator can still edit `held-out.yaml` and the deny rule in
  `.claude/settings.json` with the file tools, since those edits carry the path in their input.
- **Options.** (1) Literal only: the path as a word or a field value, as tested now. (2) Literal anywhere: the path
  as a substring of any string in the input, which adds (f) and (g), with an exception for the content fields of a
  Write or Edit to the two files that hold the path. (3) Option 2 plus resolution of path fields and Bash words:
  relative paths, `..`, `~`, variables and links, which adds (a), (b), (c). (4) Option 3 plus ancestors and globs,
  (d) and (e).
- **Impact.** Option 1 leaves `cat ../x/…` and `python3 -c` open in the orchestrator's session. Option 4 would deny
  a Grep on the repository root if the oracle sits inside the repository. For the file tools the committed `Read`
  rule already covers (a) to (c), since the harness resolves the path; the gap is Bash in the unsandboxed
  orchestrator session, where DEC-162 already accepts "a Bash command that reaches the oracle without naming its
  path" as a residual.
- **Reversibility.** High: a rule and its tests.
- **Cost.** Option 2: about 10 lines and 15 cases. Option 3: about 25 lines (the guard already expands `~` and
  variables for write targets) and 20 cases. Option 4: larger, with false denials.
- **Recommendation.** Option 3, with (d), (e) and (h) stated as part of the accepted residual in `bootstrap.md`.
- **Confidence.** Medium.

### DP-2 — The research role's exception cannot be tested in this ticket

- **Question.** Success 6 says "the research role's exception (DEC-163, W1-46) still lets them through inside its
  experiment folder". The role comes with W1-46, which depends on W1-47. Today `GOV_ROLE=research` is an unknown
  role. Who tests the clause?
- **Why now.** It is a KPI clause of this ticket with no test.
- **Options.** (1) W1-46's test design covers it, with the four `uv` forms in its install cases; W1-47 closes with
  the clause recorded as carried. (2) W1-47 adds the research role to the guard now. (3) The clause is taken out of
  W1-47's KPI.
- **Impact.** Option 2 pulls W1-46's role file and experiment-folder rule forward, outside this ticket's
  `allowed_paths`. Option 1 needs a line in W1-46's ticket.
- **Reversibility.** High.
- **Cost.** Option 1: one KPI sentence in W1-46 and four cases there.
- **Recommendation.** Option 1.
- **Confidence.** High.

### DP-3 — `uv` options that take their value as a separate word, and near forms

- **Question.** Is `uv --directory sub add requests` an install under this KPI? The same for `--project <path>`,
  `--cache-dir <path>`, `--config-file <path>`. And: `uv run -w requests` (the short form of `--with`),
  `uv run --with-editable .`, and `uv tool run`, which is what `uvx` stands for.
- **Why now.** "With or without options before the subcommand" does not say which options. `bootstrap.md` records
  that W1-04's rule misses `pip install` after an option with a value; a rule that skips words starting with `-`
  misses these too. The tests cover one-word options only.
- **Options.** (1) One-word options only, as tested; the rest is added to the list of misses in `bootstrap.md`.
  (2) The rule knows `uv`'s global options that take a value and skips the value. (3) The rule looks for the
  subcommand among all words that are not options, which also asks for `uv run add.py`.
- **Impact.** A miss fails open for the orchestrator (no prompt) and for the other roles (no denial); in a launched
  worker session the sandbox backs it.
- **Reversibility.** High.
- **Cost.** Option 2: about 8 lines and 8 cases, and a list to keep current with `uv`.
- **Recommendation.** Option 2 for the four value options above and `-w`; `uv tool run` and `--with-editable` stay
  as `bootstrap.md` has them unless the owner says otherwise.
- **Confidence.** Medium.

### DP-4 — The kernel template's settings file: name, content and how it is tested

- **Question.** What is the file called, what does it hold besides the two post-command registrations, and how do
  its commands find the `gov` package in a product repository?
- **Why now.** The KPI says "in the kernel template"; the template has no settings file and no source describes
  one. The tests ask for one JSON file matching `template/governance/kernel/settings*` with the containment hook on
  `PostToolUse` and `PostToolUseFailure` for Bash, and nothing more. They do not run its commands, because a
  command written for this repository (`PYTHONPATH="$CLAUDE_PROJECT_DIR/src"`, hooks under `template/`) would not
  work in a product repository, and the product layout is not settled in this ticket.
- **Options.** (1) `template/governance/kernel/settings.json`: plain JSON with `PreToolUse` for every tool and both
  post-command events for Bash, each command `python3 "$CLAUDE_PROJECT_DIR/governance/kernel/hooks/<hook>.py"`,
  relying on an installed `gov`; a behavioural test through those commands joins this suite. (2) The minimum the
  tests ask for now. (3) The template's settings move to the ticket that builds the Copier template, and the
  "kernel template" clause leaves this KPI.
- **Impact.** Under option 2 the template could carry a registration that does not work where it is used.
- **Reversibility.** High.
- **Cost.** Option 1: one file of about 30 lines and about 4 more cases.
- **Recommendation.** Option 1.
- **Confidence.** Medium.

### DP-5 — The shape of `held-out.yaml`, and what the guard does when the file is wrong

- **Question.** Which key holds the path, and what does the guard do when the file exists and cannot be read, is not
  YAML, or holds no path?
- **Why now.** The guard and W1-46's launcher both read the file; no source names a key. The tests are indifferent to
  the key (reading 5). A missing file means no rule (reading 7). A broken file is not tested.
- **Options.** (1) The engineer picks the key and states it in the file's header; a broken file makes the guard fail
  closed (exit 2 and a finding, DEC-110, DEC-179); two cases join this suite. (2) The owner fixes the key now. (3) A
  broken file is treated like a missing one.
- **Impact.** Option 3 lets a damaged file switch the rule off silently, which DEC-179 calls a defect. Option 1
  stops every tool call until the file is repaired; the orchestrator would repair it by hand outside the session.
- **Reversibility.** High.
- **Cost.** Option 1: about 6 lines and 2 cases.
- **Recommendation.** Option 1.
- **Confidence.** Medium.

### DP-6 — W1-05's fixture copies the whole working tree

- **Question.** `copy_working_tree` in `tests/acceptance/W1-05/w1_05_support.py` copies every tracked file and every
  untracked file git does not ignore. If the oracle sits inside this repository and is not ignored, that suite reads
  it on every run. Is that the case?
- **Why now.** This ticket hides the oracle from every session started in the repository root; a test run from such
  a session would still copy it. The test designer may not look, so only the owner can answer. This suite avoids
  the helper for that reason.
- **Options.** (1) The owner confirms the oracle is outside the repository or ignored by git; nothing changes.
  (2) The Independent Test Designer revises `copy_working_tree` to leave out the configured path, as a rewrite
  after implementation.
- **Impact.** None under option 1. Under option 2, one helper of a closed ticket changes.
- **Reversibility.** High.
- **Cost.** Option 2: about 5 lines.
- **Recommendation.** Option 1 if it holds, otherwise option 2.
- **Confidence.** High that the question matters; no knowledge of the answer.

## Earlier tests

No earlier acceptance test is changed, and none is made wrong by this ticket's KPIs as far as their text shows:

- No earlier test requires an install or download ask rule in the committed settings. W1-01 and W1-05 read
  `permissions.deny` and the hooks only; W1-04 and W1-05 assert the hook's `ask`, which stays.
- No rewrite after implementation is expected.
