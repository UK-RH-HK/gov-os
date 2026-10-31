# W2-110 acceptance tests: a product's CTO-only install rule

Ticket: `DAEO-3r1j` (W2-110) · Profile: FULL · Sources: DEC-971 item 4, DEC-957, DEC-966 item 1, DEC-163, DEC-083
(DEC-040 amended), DEC-221, DEC-462, DEC-866; `P1-MORNING-2026-10-31` item 4 · Model: rule 4 of this repository's own
hook, `.claude/hooks/pretooluse.py` · Author: independent test designer (MR-3). Written from the ticket's KPI lines and
its sources, in parallel with the engineer, without reading the implementation (DEC-959 item 7, DEC-963). The base is
`695eea48139f`.

Run it from the root of the worktree the tests sit in:

    PYTHONPATH=<that worktree>/src python3 -m pytest tests/acceptance/W2-110 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs

`copier` comes from `~/.local/bin/copier` or `PATH` (W1-39's `require_copier`). `rulesync` comes from `RULESYNC_BIN` or
`~/.local/bin/rulesync` (W1-38). PyYAML is the product's own dependency. **No command in these tests is run.** Each is
only text in the hook's input, so nothing is installed and nothing reaches the network.

**179 cases in 4 files.**

**Red run on the base (`695eea48139f`): 121 failed, 58 passed, 0 skipped, 46 s.** That includes one product generated
per session (about 11 s) and one copy per configuration.

The 121 red cases fail for three reasons, all of them the ticket's:

- **R1, asked (76 cases).** The base asks the owner about every acting orchestrator's install. That covers a session
  with the orchestrator role on any ticket or on none, and an orchestrator subagent in any session with a known role.
  So the lead is asked, and so is every orchestrator in a product whose key cannot be read.
- **R2, refused without the escalation (31 cases).** Another role, or no role, is refused, but with the old words:
  "install by role '…' denied: only the orchestrator may propose installs, …". The refusal does not tell the session
  to raise a P1 escalation to the CTO.
- **R3, refused without saying how to set the key (14 cases).** In a product without a usable key, a non-orchestrator
  is refused with the same old words. The refusal does not name `governance/project/roster.yaml` and
  `coordination_ticket`.

The 58 green cases guard what already holds; each is named under [Green on the base](#green-on-the-base-58-cases).

## How the cases run the code of the worktree they sit in (DEC-732)

Every path is taken relative to the test files: `REPO_ROOT = Path(__file__).resolve().parents[3]`
(`w2_110_support.py`). Merged into the ticket's worktree, the cases judge that worktree's `template/` and `src/`. Two
checks fail the session with a named reason if that is not so:

- **The product** (fixture `generated`, once per session; W2-90's `generate_project`). `copier.yml` and `template/`
  are assembled file by file into a temporary template source (W1-39's `assemble_source`). Then `copier copy` runs,
  and `rulesync generate` writes `.claude/settings.json` (W1-38). No folder of the repository is copied.
  - The fixture checks that the product's `governance/kernel/hooks/pretooluse.py` is byte for byte this worktree's
    `template/governance/kernel/hooks/pretooluse.py`.
- **The stand-in home** (fixture `sandbox`; W1-38's `make_session_sandbox`, nothing installed). The home's
  `.local/bin/gov` names this interpreter in its first line, and its user site holds a path file naming this
  worktree's `src`.
  - The template's pinned PreToolUse line (W2-106) starts the hook with that interpreter and `-E`.
  - The fixture checks that this interpreter, with `-E` and that home, imports `gov` from `<REPO_ROOT>/src/gov`. The
    session's `PYTHONPATH` plays no part, because `-E` drops it.
- **A call runs as Claude Code runs it** (`w2_110_support.call`; W1-05's `hook_commands`, `hook_input` and
  `run_commands`). Every PreToolUse line the generated settings register for Bash runs through `sh -c` in the
  product's root, with:
  - the call's JSON on standard input, carrying `agent_type` for a subagent and `cwd` when the case sets one;
  - `CLAUDE_PROJECT_DIR`, the stand-in `HOME`, and `GOV_ROLE` and `GOV_TICKET` as the session declares them (unset
    when `None`).
- **The decision** is W1-05's and W1-04's form:
  - `deny`: exit 2, or exit 0 with `permissionDecision: deny`;
  - `ask`: exit 0 with `permissionDecision: ask`;
  - `allow`: exit 0 with neither (no decision);
  - `error`: any other exit code.

  The reason is the `permissionDecisionReason`, or standard error on exit 2. Every case judges the hook lines'
  decision. The settings' own `permissions.deny` rule is recorded beside it (`Answer.settings_rule`), and the CTO
  cases assert that no such rule refuses the call first.

## The fixtures

### Tickets

Every configuration holds these tickets, all `in_progress`, in W1-04's ticket form:

| Ticket | WBS id | Role | Paths | Used as |
|---|---|---|---|---|
| `DAEO-c0rd` | `P-00` | orchestrator | `governance/project/**` | the coordination ticket |
| `DAEO-1ead` | `P-01` | orchestrator | `governance/project/**` | another orchestration ticket (the coordination ticket in `key-names-another-ticket`) |
| `DAEO-eng1` | `P-02` | engineer | `src/app/**` | a lead's ticket (the orchestrator on it), the engineer's, the test designer's, the ticket-lead's |
| `DAEO-spc1` | `P-03` | product-spec | `docs/spec/**` | product-spec's |
| `DAEO-aud1` | `P-04` | independent-auditor | `docs/audit/**` | the auditor's |
| `DAEO-rsc1` | `P-05` | research | `experiments/exp-1/**` (the folder exists) | research's (DEC-163, DEC-242) |
| `DAEO-w200` | `W2-00` | orchestrator | `governance/project/**` | this repository's coordination WBS id in a product where it is not the coordination ticket: nothing of this repository's rule may be in the product's code |

`DAEO-gone` and `P-99` are ids that no ticket of the product has.

### Configurations

Each configuration is a copy of the generated product with those tickets and its own roster
(`w2_110_support.configure`). Each is made once per session and shared by the cases that use it. Any roster the
template ships is removed first, except in `as-generated`.

| Configuration | `governance/project/roster.yaml` |
|---|---|
| `key-by-id` | `coordination_ticket: DAEO-c0rd` at the top level, before a `roles:` block |
| `key-by-wbs` | `coordination_ticket: P-00` |
| `key-only` | the key alone |
| `key-quoted-after-roles` | `roles:` first, then `coordination_ticket: "DAEO-c0rd"` |
| `key-names-another-ticket` | `coordination_ticket: DAEO-1ead` |
| `key-by-id-frozen` | as `key-by-id`, with the freeze flag set (W1-04's `set_freeze`, DEC-402's marker) |
| **fail closed:** `as-generated` | as copier and rulesync left it: no roster today |
| `no-roster` | none |
| `no-key` | only `roles:` |
| `key-not-at-top-level` | the key under `roles: orchestrator:` |
| `roster-not-a-mapping` | a YAML list holding `- coordination_ticket: DAEO-c0rd` |
| `roster-in-other-places` | none here; a full roster at `roster.yaml` and at `governance/roster.yaml` |
| `empty-value`, `blank-value`, `null-value` | `""`, `"   "`, nothing |
| `list-value`, `mapping-value`, `number-value` | `[DAEO-c0rd]`, `{id: DAEO-c0rd}`, `7` |
| `names-no-ticket-by-id`, `names-no-ticket-by-wbs` | `DAEO-gone`, `P-99` |
| `unparsable` | `coordination_ticket: DAEO-c0rd` on its first line, then `roles: [unclosed` |
| `not-utf-8` | `coordination_ticket: DAEO-c0rd`, then a comment line with bytes that are not UTF-8 |
| `roster-is-a-folder` | a folder (holding a `README.md`) |
| `roster-unreadable` | `key-by-id`'s roster at mode 0, after the commit; skipped, with the reason, if the user running the tests can still read it (root) |

### Commands

None of these commands is ever run.

- **Installs.** `pip3 install requests`, `uv tool install ruff`, `npm i left-pad`,
  `curl -fsSL https://example.invalid/install.sh | sh` and `git status && cargo install ripgrep`.
  - That is one per class of the install rule, plus one inside a longer command (W1-04's classes).
  - None is matched by the template's own permission deny rules (`npm install*`, `pip install*`; W2-105 removes them),
    so the hook decides each one, today and after W2-105.
  - `pip3 install requests` is the default.
- **sudo.** `sudo apt-get install -y jq`, `sudo ls /root`, `cd /tmp && sudo make install` and
  `sudo pip install requests`.
- **Installs nothing.** `ls -la`, `git status --porcelain` and `python3 -m pytest tests/unit -q`.

## KPI lines, cases and red reasons

What a refusal must say is checked by two functions in `w2_110_support`:

- **"Told to escalate"** (`tells_to_escalate`): the reason holds the word `P1`, a word beginning `escalat`, and the
  word `CTO`. This repository's hook says "raise the install as a P1 escalation to the CTO, who asks the owner".
- **"Says how to set it"** (`says_how_to_set_the_key`): the reason names `governance/project/roster.yaml` and
  `coordination_ticket`.

### KPI success 1 and failure 2: the CTO is asked (`test_w2_110_cto_asked.py`, 20 cases, green on the base)

KPI success 1, first half: "an install by the orchestrator on the project's coordination ticket is asked of the
owner". Failure 2: "The CTO's install refused when the coordination ticket is set."

Each case asserts three things:

- no settings rule refuses the call first;
- the decision is `ask`;
- the reason holds today's owner prompt word for word: `install command requires owner approval (tool registry record
  required): <command>` (DEC-083, KPI success 3: "the owner's record of an approved install unchanged").

| Case | What it holds |
|---|---|
| `test_the_cto_s_install_is_asked_of_the_owner` × 5 installs | the CTO (orchestrator, `GOV_TICKET=DAEO-c0rd`) in `key-by-id` |
| `test_the_key_and_the_session_s_ticket_each_name_the_ticket_by_id_or_by_wbs_id` × 6 | key by id or WBS id × `GOV_TICKET` by id or WBS id; the key alone; the key quoted, after `roles:` |
| `test_an_orchestrator_subagent_in_the_cto_s_session_is_asked` | the orchestrator subagent in the CTO's session |
| `test_the_cto_is_asked_in_every_permission_mode` × 6 modes | DEC-083's KPI (the prompt in Auto mode too) unchanged |
| `test_the_key_not_the_code_decides_which_orchestrator_is_the_cto` × 2 | with the key naming `DAEO-1ead`, the orchestrator on `DAEO-1ead` (by id and by WBS id) is asked |

On the base all 20 are green, because every orchestrator is asked. They guard failure 2: an implementation that
refused the CTO, or that read the session's ticket or the key in only one of their two forms, turns them red.

### KPI success 1 and failure 1: every other session is refused and told to escalate (`test_w2_110_others_refused.py`, 59 cases, all red)

KPI success 1, second half: "by any other session, a lead (the orchestrator on another ticket) included, it is
refused, and the refusal tells the session to raise it as a P1 escalation". Failure 1: "A lead's or a worker's
install in a generated project asked or allowed."

Each case asserts that the decision is `deny` and that the reason is "told to escalate". All cases use `key-by-id`
unless the table says otherwise.

| Case | Sessions | Red on the base |
|---|---|---|
| `test_every_session_but_the_cto_s_is_refused_and_told_to_escalate` × 38 | see the four rows below | R1 for the 13 orchestrator cases, R2 for the 25 others |
| (8 of the 38) leads and other orchestrators | the lead on `DAEO-eng1` (by id and by WBS id); on `DAEO-1ead`; on `DAEO-w200` (by id and as `W2-00`); with no `GOV_TICKET`; with an empty one; on `DAEO-gone` | R1 |
| (12 + 4 of the 38) other roles; no role | engineer, independent-test-designer, product-spec, independent-auditor, research (from the project's root, outside its folder) and ticket-lead, each on its own ticket and on the coordination ticket; no role, an empty role and the unknown role `owner` on the coordination ticket, and no role with no ticket | R2 |
| (8 + 6 of the 38) subagents | in the CTO's session: a subagent of each of those six roles, `general-purpose` and `Explore`. An orchestrator subagent in a lead's session, in an orchestrator session with no ticket, in an engineer's session (on its own ticket and on the coordination ticket), in a test designer's session on the coordination ticket, and in a session with no role on the coordination ticket | R2 for the CTO-session subagents and the session with no role; R1 for the other 5 orchestrator subagents (DEC-117 asks them today) |
| `test_every_install_of_a_lead_and_of_a_worker_is_refused` × 2 × 5 | the lead and the engineer, each install | R1 for the lead, R2 for the engineer |
| `test_a_lead_is_refused_in_the_modes_that_skip_prompts` × 3 | `auto`, `dontAsk`, `bypassPermissions` | R1 |
| `test_with_the_key_by_wbs_id_the_others_are_refused_too` × 4 | `key-by-wbs`: the lead, the orchestrator on `DAEO-w200`, the orchestrator with no ticket, an orchestrator subagent in an engineer's session | R1 |
| `test_when_the_key_names_another_ticket_the_others_are_refused` × 3 | `key-names-another-ticket`: the orchestrator on `DAEO-c0rd` (by id and by WBS id) and on `DAEO-w200` | R1 |
| `test_a_research_session_outside_its_experiment_folder_is_refused_and_told_to_escalate` | research on its own ticket with `cwd` in `src/app` | R2 |

"Never written in the code" (KPI success 2) is held here and in the CTO file: the key, not a fixed id, decides. An
implementation that fixed `W2-00`, or `DAEO-c0rd`, fails the `DAEO-w200` cases or the `key-names-another-ticket` cases.

### KPI success 2 and failure 3: fail closed (`test_w2_110_fail_closed.py`, 63 cases, 62 red)

KPI success 2: "with no such key, or a key naming no ticket, every session's install is refused and the refusal says
how to set it (fail closed)". Failure 3: "A missing or unreadable coordination-ticket key read as 'ask everyone'."

Each case asserts that the decision is `deny`, so never `ask` and never a pass-through, and that the reason "says how
to set it".

| Case | What it holds | Red on the base |
|---|---|---|
| `test_the_cto_s_install_is_refused_when_the_key_cannot_be_read` × 18 | every fail-closed configuration; the orchestrator on `DAEO-c0rd` | R1 |
| `test_an_orchestrator_whose_ticket_is_what_the_key_holds_is_refused` × 9 | `GOV_TICKET` holds the key's words exactly: `DAEO-gone`, `P-99`, `""`, `"   "` and `"7"`, or is unset while the key is null, missing, or in a roster that is not there (`no-roster`, `as-generated`) | R1 |
| `test_every_session_s_install_is_refused_and_told_how_to_set_the_key` × 12 sessions × 2 (`no-roster`, `unparsable`) | the CTO by WBS id; its orchestrator subagent; a lead; an orchestrator with no ticket; the six other roles on their own tickets; no role; an orchestrator subagent in an engineer's session | R1 for the 5 orchestrator sessions, R3 for the 7 others, in each of the 2 configurations |
| `test_without_a_roster_every_install_of_the_cto_is_refused` × 5 | each install | R1 |
| `test_without_a_roster_the_cto_is_refused_in_every_permission_mode` × 6 | never an `ask`, in any mode | R1 |
| `test_the_product_as_generated_names_no_coordination_ticket` | the generated product's roster, if the template ships one, sets no ticket: the key is the project's, set at adoption (an empty key is allowed) | **green**: the template ships no roster |

### KPI success 3 and failure 4: nothing else changes (`test_w2_110_unchanged.py`, 37 cases, all green on the base)

KPI success 3: "Nothing else in the install rule changes: sudo still refused to every role, the research role's one
exception inside its experiment folder kept, a frozen project still refusing installs, the owner's record of an
approved install unchanged". Failure 4: "sudo, the research exception or the freeze changed."

The owner's prompt part of KPI success 3 is held in the CTO cases above.

| Case | What it holds |
|---|---|
| `test_sudo_is_refused_to_the_cto` × 3 | the hook itself refuses each sudo command for the CTO, whatever the settings' own `sudo *` rule does |
| `test_sudo_is_refused_to_every_other_session` × 7 | `sudo pip install requests`: the lead, the engineer, research in its folder, no role, the CTO's orchestrator subagent, and the would-be CTO in `no-roster` and `unparsable` |
| `test_the_research_exception_holds_with_or_without_the_key` × 4 configurations × 2 forms | research on `DAEO-rsc1`, with `cwd` in `experiments/exp-1` or as `cd experiments/exp-1 && pip3 install requests` from the root, gets no decision (let through, DEC-163) in `key-by-id`, `no-roster`, `no-key` and `unparsable` |
| `test_a_frozen_product_refuses_every_install_the_cto_s_included` × 6 | `key-by-id-frozen`: the CTO (by id and by WBS id), its orchestrator subagent, the lead, the engineer and research in its folder are all refused |
| `test_a_bash_call_that_installs_nothing_is_decided_as_before` × 4 sessions × 3 commands | no decision for the CTO and the lead in `key-by-id`, the CTO in `no-roster` and the engineer in `unparsable`: a broken key changes installs only |
| `test_the_cto_s_install_that_writes_where_the_guard_refuses_stays_refused` | `pip3 install requests > .gov-runtime/records.jsonl` by the CTO is refused, not asked: the rule only escalates |

### KPI success 4: the template's and the guard's own suites pass

KPI success 4: "The template's own suites (W1-38, W1-39) and the guard's own suites pass on the change." These are run
as their own suites, in the lead's verification, not from here. The guard's suites that still assert the old rule are
listed below. They cannot pass on the change until they are revised, and the decision to revise them is not the
designer's.

## Green on the base (58 cases)

- **The 20 CTO cases** (`test_w2_110_cto_asked.py`). The base asks every orchestrator, the CTO among them. They guard
  failure 2.
- **`test_the_product_as_generated_names_no_coordination_ticket`.** The template ships no roster.
- **The 37 "nothing else changes" cases** (`test_w2_110_unchanged.py`):
  - sudo, 3 + 7;
  - the research exception, 8;
  - the freeze, 6;
  - calls that install nothing, 12;
  - the guard's write refusal kept, 1.

## Checked against the rule asked for (a scratch simulation, not committed)

A pytest plugin in the session's scratch folder replaced each configured product's `governance/kernel/hooks/pretooluse.py`
after `configure`. The replacement was the template's hook with a CTO-only install branch:

1. the freeze refuses;
2. the research exception in its folder is let through;
3. the roster is read as YAML, as UTF-8 text; a non-text or empty value, or a value that names no ticket of `.tickets/`
   by id or WBS id, refuses with the file and the key named;
4. the CTO is the orchestrator role, acting as the orchestrator, whose `GOV_TICKET` resolves to the same ticket file
   as the key; the CTO is asked with today's prompt;
5. every other session is refused with this repository's words.

Nothing tracked was touched. Results:

- **That rule: 179 passed** (66 s).
- **Every orchestrator asked** (the base's choice, with the fail-closed part kept): 24 failed. These are the leads,
  the orchestrators on other tickets or none, and the orchestrator subagents in their sessions, across the five
  refused-session tests.
- **A key that cannot be read asks everyone:** 62 failed. That is every fail-closed case but the template-roster one.

## Readings stated, not asked

1. **"Cannot be read or parsed" covers the whole roster.** A roster that is not valid YAML, or not UTF-8 text, is
   refused even when its first line, `coordination_ticket: DAEO-c0rd`, reads fine alone (`unparsable`, `not-utf-8`).
   A broken file is not half-read, so this is the fail-closed reading.
2. **"Non-text" is the YAML value's type.** `7`, `[DAEO-c0rd]` and `{id: DAEO-c0rd}` are refused. None of them names
   a ticket either, so any reading refuses them. `7` is checked also against an orchestrator whose `GOV_TICKET` is
   `7`, which no ticket is.
3. **The two kinds of refusal say different things.** A configured product's refusal tells the session to escalate.
   A fail-closed refusal says how to set the key. Neither is asked to carry the other's words, though it may.
4. **`ticket-lead` is "every other session".** It is a known role of the guard (DEC-434), so it is refused like the
   other roles: on its own and on the coordination ticket, and as a subagent in the CTO's session.
5. **The coordination ticket's status and role are not judged.** Rule 4 of this repository's hook does not judge
   them, and no KPI line does.

## Earlier tests that enforce the old rule (DEC-866): named, not edited

These cases assert "any orchestrator is asked". DEC-083 and DEC-117 still hold them (orchestrator-only `ask`; an
orchestrator subagent asked in any session with a declared role). DEC-957 item 3 and DEC-971 item 4 change that rule.
None of their fixture projects has a roster with `coordination_ticket` (W1-46's copies this repository's roster,
which has only `roles:`). Under the change each of these cases is refused, through fail closed or as a non-CTO
session.

| Suite: case | What it asserts | Cases |
|---|---|---|
| `tests/acceptance/W1-04/conftest.py::install_rule` (fixture) | `pip install requests` by the orchestrator on `DAEO-zz91` is `ask`; every W1-04 case but the registry schema's depends on it | gates about 340 |
| `W1-04/test_w1_04_install_rule.py::test_an_install_by_the_orchestrator_is_asked_about` | the orchestrator is asked, 25 installs | 25 |
| `W1-04/test_w1_04_install_rule.py::test_the_ask_is_one_the_harness_shows_to_the_owner` | the ask's form | 1 |
| `W1-04/test_w1_04_install_rule.py::test_inside_a_subagent_the_acting_role_decides` | `orchestrator-subagent-in-orchestrator-session`, `orchestrator-subagent-in-engineer-session` and `orchestrator-subagent-in-designer-session` → `ask` | 3 of 11 |
| `W1-04/test_w1_04_auto_mode.py::test_an_install_by_the_orchestrator_is_asked_about_in_every_permission_mode` | 6 modes × 5 installs → `ask` | 30 |
| `W1-04/test_w1_04_auto_mode.py::test_an_orchestrator_subagent_is_asked_about_in_auto_mode_too` | an orchestrator subagent in an engineer's session → `ask` | 2 |
| `W1-04/test_w1_04_only_escalates.py::test_a_frozen_repository_stays_closed_to_an_install_that_writes` | asks the orchestrator before the freeze | 1 |
| `W1-04/test_w1_04_probe_findings.py`: the cases through `_assert_an_install`, and `test_while_frozen_an_install_is_denied_to_every_role_the_orchestrator_included` | the orchestrator is asked (before the freeze, in the latter) | about 89 |
| `tests/unit/install/test_install.py`: `test_orchestrator_install_gets_ask`, `test_ask_leaves_snapshot`, `test_ask_output_has_three_keys`, `test_unfrozen_repo_asks_install_for_orchestrator`, `test_curl_combined_option_ask_for_orchestrator` | the kernel hook asks the orchestrator | 5 |
| `W1-47/test_w1_47_uv_installs.py`: `test_the_orchestrator_is_asked`, `…_in_every_permission_mode`, `…_for_the_forms_of_dec_216_in_every_permission_mode`, `test_the_uv_installs_of_w1_04_are_still_asked` | the orchestrator is asked for uv installs | about 80 |
| `W1-47/test_w1_47_kernel_template.py::test_the_template_s_guard_asks_before_an_install` | the kernel template's guard asks | 1 |
| `W1-50/test_w1_50_freeze_guard_reading.py::test_the_install_rule_reads_the_flag_as_the_guard_does` | the orchestrator is asked when the flag is not a freeze | 5 |
| `W1-03/test_w1_03_calls_known_to_be_over.py`, case `install-ask-the-owner-declined-then-an-engineer-subagent` | starts from the orchestrator's ask | 2 |
| `W1-05/test_w1_05_live_hooks.py::test_an_install_by_the_orchestrator_asks_the_owner_through_the_kernel_s_wiring` | asked through the generated product's wiring | 1 |
| `W1-46/test_w1_46_install_spellings.py::test_the_orchestrator_is_asked_about_uv_run_w_with_its_value_joined` | asked through the kernel guard | 1 |

No case asserts the old refusal's words. The sweep was made with `gov retrieve` and a read-only search of `tests/`.
The cases that run this repository's own five-rule hook (W1-33's guard-and-launcher case, and W1-05's and W1-46's
non-kernel cases) already follow DEC-957 and are not affected.

## Not tested

- **"Set at adoption."** No path of this ticket writes the key: the adopt skill and the template's overlay are outside
  it. See the return's package.
- **The template's own permission deny rules** (`npm install*`, `pip install*`) are W2-105's.
- **The live headless attempt** (DEC-120): it needs a running harness.
- **Evasive spellings of an install** (CAP-25.c), and commands near the install classes (W1-04's list).
- **The case of ticket ids** (`p-00` against `P-00`), two tickets with one WBS id, and a `GOV_TICKET` with spaces
  around it: no source decides them.
