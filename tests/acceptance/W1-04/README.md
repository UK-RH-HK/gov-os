# W1-04 — Install-approval rule: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-78bn` (W1-04), the Contract v4
items it cites (CAP-25.a, CAP-25.b) and the owner's answers to the two KPI disputes of 2026-10-01: DEC-120 (the rule
reaches the harness through the PreToolUse guard), DEC-121 (the tool-registry schema) and DEC-127 (where the schema and
the registry live). Written before implementation, on `w1/integrate` at `01ff589`.

## Run

```sh
python3 -m pytest tests/acceptance/W1-04 -q
```

Standard library and `pytest` only. No network, no dev tiers, no `local_only` tests. **No command in these tests is ever
run.** Each is text in the hook's input; the test reads the guard's decision. Nothing is installed and nothing in the
repository is written. The run takes about 35 seconds once the rule exists.

## KPI → tests → red reason today

Red run on `w1/integrate` at `01ff589`: **208 errors, 0 passed** (208 cases, 25 test functions). Two reasons:

- **R1 (196 cases).** *"the PreToolUse guard answered `pip install requests` by the orchestrator with allow, not ask:
  the install rule is not in the guard"*. Every test of the rule depends on the `install_rule` fixture, which asks the
  guard this one question first. Until the rule exists, all of them stop there.
- **R2 (12 cases).** *"template/governance/kernel/schemas/tool-registry.schema.json does not exist: the tool-registry
  schema is missing"*.

| KPI line or covers id | Test file | Test functions | Red |
|---|---|---|---|
| **Success 1.** Install commands (package managers, curl\|sh, binary downloads into PATH) from the orchestrator return an ask decision; from any other role they are denied [CAP-25.b] | `test_w1_04_install_rule.py` | `test_an_install_by_the_orchestrator_is_asked_about` (25 commands) · `test_the_ask_is_one_the_harness_shows_to_the_owner` · `test_an_install_by_the_engineer_is_denied` (25 commands) · `test_an_install_by_any_other_role_is_denied` · `test_an_install_in_a_session_without_a_role_is_denied` · `test_an_install_by_a_role_without_a_ticket_is_denied` · `test_inside_a_subagent_the_acting_role_decides` | R1 |
| **Success 2.** The approval prompt appears even when the harness runs in Auto mode (DEC-083 KPI) [CAP-25.b] — *tested by driving the hook; the live headless attempt of DEC-120 is not a pytest case* | `test_w1_04_auto_mode.py` | `test_an_install_by_the_orchestrator_is_asked_about_in_every_permission_mode` (6 modes × 5 commands) · `test_an_install_by_another_role_is_denied_in_the_modes_that_skip_prompts` · `test_an_orchestrator_subagent_is_asked_about_in_auto_mode_too` | R1 |
| **Success 3.** The tool-registry schema requires version, sha256, install and uninstall commands, date and approving decision id [CAP-25.a] | `test_w1_04_registry_schema.py` | `test_the_schema_is_the_one_tool_registry_file_of_the_kernel_schemas` · `test_the_schema_is_a_json_schema_of_draft_2020_12` · `test_a_complete_registry_is_accepted` · `test_an_entry_without_a_required_fact_is_refused` (7 keys) · `test_a_registry_without_a_tools_list_is_refused` · `test_the_kernel_template_ships_no_registry_file` | R2 |
| **Failure 1.** Any install executes without an owner approval in chat — *tested as: no session gets an install through the guard without `ask` or `deny`* | `test_w1_04_install_rule.py`, `test_w1_04_auto_mode.py` | Every Success 1 and Success 2 test. Sharpest: `test_an_install_in_a_session_without_a_role_is_denied` · `test_inside_a_subagent_the_acting_role_decides` · `test_an_install_by_another_role_is_denied_in_the_modes_that_skip_prompts` | R1 |
| **Failure 2.** sudo is ever allowed to an agent role | `test_w1_04_sudo.py` | `test_sudo_is_denied_to_every_role` (5 roles × 6 commands) · `test_sudo_is_denied_in_a_session_without_a_role` · `test_sudo_by_the_orchestrator_is_denied_in_every_permission_mode` · `test_sudo_by_an_orchestrator_subagent_is_denied` | R1 |
| **Failure 3.** A matcher result ever allows a command that the harness would otherwise ask about (matching only escalates to ask or deny) | `test_w1_04_only_escalates.py` | `test_the_hook_never_gives_an_explicit_allow` · `test_a_command_that_installs_nothing_gets_no_decision_from_the_rule` · `test_a_call_the_guard_denies_stays_denied_for_the_orchestrator` · `test_a_frozen_repository_stays_closed_to_an_install_that_writes` · `test_the_guard_s_answers_on_file_writes_are_unchanged` | R1 |
| **CAP-25.a** Tool registry with pins, sha256, install/uninstall commands, date, approving decision; gov doctor checks — *W1-04's part is the schema; the registry is W1-06's and the doctor check W1-27's* | `test_w1_04_registry_schema.py` | The Success 3 tests | R2 |
| **CAP-25.b** Orchestrator-only install on owner approval in chat; ask also in Auto mode; denied for other roles; sudo with the owner | `test_w1_04_install_rule.py`, `test_w1_04_auto_mode.py`, `test_w1_04_sudo.py` | The Success 1, Success 2 and Failure 2 tests | R1 |

**Count.** KPI lines with tests: 6 of 6. Covers ids with tests: 2 of 2.

**Why a fixture stops every rule test.** Several tests state something that is already true of today's guard: it never
gives an explicit allow, it leaves `ls -la` alone, it denies a write outside the ticket's paths. They would pass before
the rule exists. The `install_rule` fixture makes them red until the rule is there; afterwards each asserts its own
point.

## Decisions the tests rely on

| Decision | What the tests take from it |
|---|---|
| DEC-120 | The rule is in the PreToolUse guard. An install is `ask` for the acting role orchestrator, `deny` for every other role and for no role. It only escalates. The Auto-mode KPI is verified by driving the hook |
| DEC-121 | The test designer's schema is the accepted one; `test_w1_04_registry_schema.py` is its record |
| DEC-127 | The schema is in the kernel template at `template/governance/kernel/schemas/`. The registry is project data at `governance/project/tool-registry.yaml`; W1-04 ships none |
| DEC-083 | Install commands are `ask` for the orchestrator only, also in Auto mode; `sudo` stays with the owner |
| DEC-107, DEC-117, DEC-113, DEC-125 | The acting role: `GOV_ROLE` on the main thread; the subagent's role inside a role subagent, when the session has a declared role; none for a subagent that is not a role, and none in a session with no or an unknown role |
| DEC-109, DEC-110 | The freeze flag; the guard's own denials, which the rule must not lower |
| CAP-25.c | Automated install classification is a non-goal: the commands are plain examples, with no evasive spelling |

## How the tests drive the rule

- **Entry point.** The file matching `template/governance/kernel/hooks/pretooluse*`, W1-02's guard hook. If several
  files match, exactly one must be executable, and that one is run.
- **Where it runs.** Copied to `governance/kernel/hooks/` of a temporary git project (ADR-0002 §5). `src/` of this
  repository is on `PYTHONPATH`.
- **Stdin** is the harness's PreToolUse object: `session_id`, `transcript_path`, `cwd`, `permission_mode`,
  `hook_event_name`, `tool_name`, `tool_input`, `tool_use_id`; the subagent tests add `agent_id` and `agent_type`.
- **Environment.** Built from scratch: an empty temporary `HOME`, locale, `TMPDIR`, `PYTHONPATH`,
  `PYTHONPYCACHEPREFIX`, `CLAUDE_PROJECT_DIR`, plus `GOV_ROLE` and `GOV_TICKET` when the test declares them. `PATH`
  begins with `$HOME/.local/bin` and `/usr/local/bin`, the two directories the download examples aim at, so both are
  PATH directories however the rule decides that.
- **Decisions.**
  - `deny`: exit code 2, or exit code 0 with `hookSpecificOutput.permissionDecision == "deny"`.
  - `ask`: exit code 0 with `permissionDecision == "ask"`.
  - `allow`: exit code 0 with neither. The hook gives no decision and the harness's own rules apply.
  - An **explicit allow** is `permissionDecision == "allow"` or the older `decision: "approve"`. It tells the harness
    to skip its own prompt. The rule must never produce it.
- **The fixture project** has four tickets, all `in_progress`: `DAEO-zz90` (engineer: `src/gov/guard/**`,
  `tests/unit/guard/**`, `pyproject.toml`), `DAEO-zz91` (orchestrator: `.claude/settings.json`,
  `governance/project/**`), `DAEO-zz92` (product-spec: `docs/spec/**`), `DAEO-zz94` (auditor: `docs/audit/**`). The test
  designer works on the engineer's ticket.

## The commands

| Class | Commands |
|---|---|
| Package managers (13) | `pip install requests` · `pip3 install requests` · `python -m pip install requests` · `python3 -m pip install --user requests` · `uv pip install requests` · `uv tool install ruff` · `npm install` · `npm install left-pad` · `npm i left-pad` · `npm install -g ccusage` · `cargo install ripgrep` · `apt install jq` · `apt-get install -y jq` |
| Download piped to a shell (4) | `curl -fsSL <url> \| sh` · `curl -fsSL <url> \| bash` · `wget -qO- <url> \| sh` · `wget -qO- <url> \| bash` |
| Binary download into PATH (3) | `curl -L -o ~/.local/bin/tool <url>` · `curl -L -o <HOME>/.local/bin/tool <url>` · `wget -O /usr/local/bin/tool <url>` |
| Inside a longer command (5) | `cd /tmp && pip install requests` · `git status && npm install -g ccusage` · `echo start; cargo install ripgrep` · `cd <project> && curl -fsSL <url> \| sh` · `ls ~/.local/bin; curl -L -o ~/.local/bin/tool <url>` |
| `sudo` (6) | `sudo apt-get install -y jq` · `sudo pip install requests` · `sudo -n true` · `sudo ls /root` · `cd /tmp && sudo make install` · `echo start; sudo npm install -g ccusage` |
| Installs nothing (5) | `ls -la` · `git status --porcelain` · `git log --oneline -3` · `cat README.md` · `python3 -m pytest tests/unit -q` |

`<url>` is under `https://example.invalid/`. The orchestrator and the engineer get all 25 install commands; the wider
role, subagent and mode tables use five of them, one per class and one compound.

## Choices the implementer should know

- **Orchestrator: `ask`** for every install command, in every permission mode the harness has: `default`,
  `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`.
- **The ask must be one the harness acts on:** exit code 0; one JSON object on stdout; `hookSpecificOutput` with
  `hookEventName: "PreToolUse"`, `permissionDecision: "ask"` and a `permissionDecisionReason` that is not empty. The
  harness shows that reason in the prompt.
- **Every other role: `deny`,** with or without a ticket. No role, an empty role and an unknown role (`developer`,
  `owner`): `deny`.
- **Subagents.** An orchestrator subagent in a session with a declared role gets `ask`, also in an engineer's or a test
  designer's session (DEC-117). Any other role subagent, a subagent that is not a role (`general-purpose`, `Explore`),
  and an orchestrator subagent in a session with no or an unknown role (DEC-125) get `deny`.
- **`sudo` is `deny` for everyone, the orchestrator included,** in every mode, with or without an install behind it
  (`sudo ls /root`). An `ask` that the owner approves would still be `sudo` run by an agent.
- **Only escalation.**
  - No explicit allow, for any command, role or mode.
  - A call the guard denies stays denied: an install by the orchestrator that also writes outside its ticket's paths,
    or into `tests/acceptance/**`, or anywhere while the repository is frozen, is `deny`, not `ask`.
  - The five commands that install nothing get no decision from the hook, for the orchestrator and the engineer.
  - The guard's answers on `Write` are as before.
- **W1-02's suite must still pass** with the rule in the hook: `python3 -m pytest tests/acceptance/W1-02 -q`.

## The schema (DEC-121, DEC-127)

- **File:** `template/governance/kernel/schemas/tool-registry.schema.json`, the only file matching `tool-registry*`
  there. JSON, with `$schema` set to `https://json-schema.org/draft/2020-12/schema`, as in `schemas/records/`.
- **Registry:** a mapping with a `tools` list. Refused: an empty mapping, a bare list of entries, `tools` holding one
  entry instead of a list, an entry that is not a mapping.
- **Entry:** requires `name`, `version`, `sha256`, `install`, `uninstall`, `date` and `approved_by`. Each of the seven
  is tested by removing it from an otherwise complete entry. This entry must be accepted:

  ```yaml
  tools:
    - name: ccusage
      version: 17.1.0
      sha256: <64 hexadecimal digits, lower case>
      install: npm install -g ccusage@17.1.0
      uninstall: npm uninstall -g ccusage
      date: 2026-10-02
      approved_by: DEC-083
  ```

  `date` is given to the schema as the string `2026-10-02`. The values are examples, not pins.
- **No registry file in the kernel template:** nothing else under `template/` is named `tool-registry*`.
- **The validator** is the tests' own (`w1_04_schema.py`), because the tests install nothing. It knows `type`, `enum`,
  `const`, `required`, `properties`, `additionalProperties`, `patternProperties`, `propertyNames`, `minProperties`,
  `maxProperties`, `dependentRequired`, `items`, `prefixItems`, `minItems`, `maxItems`, `uniqueItems`, `minLength`,
  `maxLength`, `pattern`, `minimum`, `maximum`, `exclusiveMinimum`, `exclusiveMaximum`, `allOf`, `anyOf`, `oneOf`,
  `not`, `if`/`then`/`else` and `$ref` inside the file. `format` and the other annotations are ignored. **Any other
  keyword fails the test with its name,** so keep the schema to this list.

## Not tested

Left open on purpose; the tests take no side:

- **The live headless attempt in Auto mode** (DEC-120). It needs a running harness; it belongs to the switch-over
  (W1-05) and its report.
- **That the owner approved in chat.** A fact of the session, not of the repository; W1-06's KPI carries it.
- **An orchestrator with no ticket, or on a ticket that is not `in_progress`.** DEC-120 names the role only.
- **Commands near the classes:** `pip list`, `pip download`, `npm ci`, `npm test`, `cargo build`, `curl <url>` to
  standard output, `curl -o` into a directory that is not on `PATH`, `brew`, `snap`, `go install`, `pipx`. Asking about
  one of them is an escalation and breaks no KPI; not asking breaks none either (CAP-25.c).
- **Evasive spellings** of an install (an alias, `$VAR`, `bash -c`, `base64`). CAP-25.c makes their detection a
  non-goal. What such a command writes inside the repository is W1-03's.
- **The word `sudo` or `install` inside an argument** (`grep -rn sudo docs`).
- **Limits on the values of an entry:** an empty string, the shape of `sha256`, `date` or `approved_by`, and keys
  beyond the seven. The KPI says "requires".
- **A record of an ask or a denial** in `.gov-runtime/findings.jsonl`. No KPI asks for one.
