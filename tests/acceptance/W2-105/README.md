# W2-105 (DAEO-zpdj): the template's install block removed

Acceptance tests from the ticket's KPI lines and its sources (DEC-966 item 1, DEC-172, DEC-957, DEC-965), written by
the independent test designer in parallel with the implementer (MR-3, DEC-959 item 7, DEC-963). Profile STANDARD.

`template/.rulesync/permissions.jsonc` gave two deny rules, `npm install*` and `pip install*`. rulesync turns them
into `Bash(npm install*)` and `Bash(pip install*)` in every generated project's `.claude/settings.json`, and Claude
Code refuses a call a deny rule matches before any hook is asked. So in a product, the CTO's session never reaches the
guard's install rule and can never ask the owner (P-W2-90-1 P1-A). DEC-966 item 1 takes them out, as DEC-172 did for
this repository's settings.

## How the tests reach the template and the code (DEC-732)

- **Everything is read relative to the repository the tests sit in**: `REPO_ROOT = Path(__file__).resolve().parents[3]`
  (`w2_105_support.py`), as W2-90's helper does. Merged into the ticket's worktree and run there, they judge that
  worktree's `template/` and `src/gov`.
- **A generated project**, made as W2-90's helper makes it (`w2_90_kernel_wiring.generate_project`): `copier.yml` and
  `template/` assembled file by file into a temporary template source (W1-39's `assemble_source`), `copier copy`
  (W1-39's `create_project_and_run`), then `rulesync generate` in the project (W1-38's `run_rulesync_generate`). It
  gets a ticket in progress for each role (the orchestrator's coordination ticket `DAEO-zz91`, the engineer's
  `DAEO-zz90`, which the test designer works on, product-spec's, the auditor's and research's with its experiment
  folder `experiments/spikes/exp-901/`), and is committed. Built once per session in pytest's temporary folder; the
  cases that run the hook work on a copy of it.
- **A call is decided as the harness decides it** (W1-05's and W1-38's harness): a `permissions.deny` rule of the
  generated settings refuses before any hook is asked; otherwise the PreToolUse commands the settings register for
  Bash are run through `sh -c`, the event's JSON on standard input, `CLAUDE_PROJECT_DIR` set to the project, with
  `GOV_ROLE` and `GOV_TICKET` of the session (W1-05's `run_commands`). The hook's environment has no `PYTHONPATH`:
  this worktree's `src` is made importable for the stand-in home by a path file in its user site folder, as an
  editable install leaves one (W2-90's `install_gov_for`). So the guard that answers is this worktree's
  `src/gov/guard/` behind the template's `governance/kernel/hooks/pretooluse.py`.
- **"Asked by the guard"**: no settings rule (deny, ask or allow) binds the install, every registered command ended
  with 0, none refused, and the guard's program wrote `ask`. **"Refused by the guard"**: no settings deny rule
  refused first, and the guard's program itself ended with 0 and wrote `deny` (W1-38's `refused_by_the_program`: an
  exit 2 is also what an interpreter gives that did not find the program). The registered commands are run even when
  a settings rule denies, so that a red message says what the guard would have answered.
- **The base ("before")** is `template/.rulesync/permissions.jsonc` at `74d83913a86b`, the commit of DEC-664's round:
  the last change to the file on `w2/integrate` before this ticket. It is read with `git show` from the repository's
  history; its generated settings are what rulesync writes in a copy of the same generated project given that source.
- **Run**:

  ```
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-105 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs
  ```

  In the tests worktree, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-105-tests/src python3 -c "import gov;
  print(gov.__file__)"` printed `/home/usain/gov-os-worktrees/W2-105-tests/src/gov/__init__.py`. Run in the ticket's
  worktree, `<worktree>` is that worktree. Copier and rulesync are the registered tools at `~/.local/bin/` (nothing is
  installed by a test; a missing Copier fails the session fixture, never skips). No network.

## KPI lines and their cases

28 cases in `test_w2_105_install_block.py`. "Base" is this tests worktree's template, before the implementer's change.

### Success 1, failure 1: no deny rule for `npm install*` or `pip install*` in the generated settings

| Test | Measures | On the base |
|---|---|---|
| `test_no_rule_of_the_templates_source_binds_the_install[npm install -g ccusage]`, `[pip install requests]` | no `bash` rule of the template's source, whatever its value, binds the install (as `Bash(<pattern>)`) | **red**: `npm install*` / `pip install*` |
| `test_no_rule_of_the_generated_settings_binds_the_install[<install>-deny]` × 2 | no deny rule of the generated settings binds the install (W1-05's reading of a rule) | **red**: `Bash(npm install*)` / `Bash(pip install*)` |
| `test_no_rule_of_the_generated_settings_binds_the_install[<install>-ask]`, `[<install>-allow]` × 4 | removed, not moved: no ask or allow rule binds it either (W1-47's reading of DEC-172) | green; must stay green |

### Success 2, failures 1 and 2: the CTO's session is asked by the guard, every other session refused by it

| Test | Measures | On the base |
|---|---|---|
| `test_an_install_by_the_orchestrator_on_its_coordination_ticket_is_asked_by_the_guard[<install>]` × 2 | the orchestrator on `DAEO-zz91`, in the `default`, `auto` and `acceptEdits` modes: no settings rule decides, the hook is reached, the guard asks | **red**: a settings deny rule refuses first (the guard's own answer is `ask`) |
| `test_an_install_by_another_role_is_refused_by_the_guard[<role>-<install>]` × 8 (engineer, independent-test-designer, independent-auditor, product-spec) | refused, and by the guard's own program, not by a settings rule; no `ask` | **red**: a settings deny rule refuses first (the guard's own answer is `deny`) |
| `test_an_install_in_a_session_without_a_role_is_refused_by_the_guard[<install>]` × 2 | a session with no `GOV_ROLE`: the same | **red**: the same |
| `test_a_research_install_outside_its_experiment_folder_is_refused_by_the_guard[<install>]` × 2 | research on its ticket, started in the project's root: refused by the guard | **red**: the same |

### Success 3, failure 3: every other rule unchanged, by name and count

| Test | Measures | On the base |
|---|---|---|
| `test_the_comparison_base_gives_the_two_install_rules` | the base source gives the two rules and rulesync generates each once from it: the comparison is with the right base | green; green after too |
| `test_the_templates_source_is_its_base_less_the_two_install_rules` | the source's rules, as `(category, pattern, value)`, are the base's less the two, and their count is the base's less 2 | **red**: 4 rules, the base's 4 |
| `test_no_other_rule_of_the_templates_source_is_added_removed_or_changed` | the two install rules aside, the source's rules are the base's | green; must stay green |
| `test_the_generated_rules_are_the_base_rules_less_the_two_install_rules` | the generated rules, as `(list, rule)` with their counts over every list of `permissions`, are the base's less the two deny rules; total = base − 2 | **red**: 4 deny rules, the base's 4 |
| `test_no_other_generated_rule_is_added_removed_or_changed` | the two aside, every list's rules by name and count are the base's, and every non-list entry of `permissions` is the base's | green; must stay green |
| `test_sudo_is_still_denied_by_the_generated_settings` | a deny rule of the generated settings still binds `sudo apt-get install -y jq` | green; must stay green |

### Success 4, failure 4: W1-38 and W1-39 pass on the change

No case here: the line is shown by running `tests/acceptance/W1-38` and `tests/acceptance/W1-39` on the change. W1-38's
`test_w1_38_test_folder_rule.py` pinned the two install rules (`OTHER_SOURCE_RULES`, `OTHER_GENERATED_RULES`, two
messages); it is revised in this ticket's second test commit (`Rewrite-Reason: DEC-966 item 1`, DEC-866) to pin the
ticket-folder and sudo rules and nothing else. Its two revised cases are red on the base for the same reason and green
after. W1-39 names neither rule.

## The red on the base

20 red, 8 green (about 6 s). Every red is the one reason: the template's source still gives `npm install*` and
`pip install*`, rulesync generates them as deny rules, and the harness refuses the installs before the guard is asked.
The red messages of the KPI 2 cases show the guard's own answer is already what KPI 2 asks (`ask` for the
orchestrator, `deny` for every other session): the ticket's change, not the guard, is what is missing. The 8 green
cases guard what already holds (nothing moved to ask or allow; every other rule as it was; sudo still denied).

**The decided state is reachable** (a probe in a temporary project whose own copy of the source had the two lines
removed; nothing of the template was changed): the generated deny list is `Bash(sudo *)` and `Edit(.tickets/**)`, the
generated rules are the base's less the two, the orchestrator is asked by the guard in all three modes, and the six
other sessions are refused by the guard, for both installs.

## What of KPI 2 is left out, and why

The lead's reading (the ticket's only path is the template's permission source):

- **"Leads included"**: a lead is an orchestrator session on a ticket that is not the coordination ticket. The guard
  as it stands on `w2/integrate` knows no coordination ticket, so it asks a lead as it asks the CTO. A case that a
  lead is refused could pass only after a change to the guard, outside this ticket's path. Not written; the lead
  packages it.
- **Research's install inside its experiment folder** (DEC-163, W1-46 success 6): its own case is W1-46's
  `test_a_research_install_inside_the_experiment_folder_is_let_through[npm-install]`, moved by W2-90's next round
  (DEC-965). Only research outside its folder is tested here.
