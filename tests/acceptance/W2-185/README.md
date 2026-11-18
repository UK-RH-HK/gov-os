# W2-185 (DAEO-qyt2): adopted projects get the context watch; portability's lift is per hook; W1-38's fixture holds seven hooks

**Retired with the guard and the sandbox (EMERGENCY-2 6.1, DAEO-gr7t).** The template's `posttooluse.py` entry is no longer asked for, and the kernel's hook scripts are five.

Profile STANDARD, class C2. Decisions: DEC-1167 (4), DEC-1163 (6) E (a), DEC-971 item 3, DEC-805, DEC-1156 (7).
Written from the ticket's KPI lines and the code as it stands on the base `31eab2103` (never from the engineer's branch).

## How the map is run

`gov accept` runs pytest on this folder. `conftest.py` points a run of this folder alone at the node ids the tables
below name, each once: the existing cases that the ticket's Verify clauses name, in their own files with their own
folders' conftests and fixtures (the form of `tests/acceptance/W2-182/`), then this folder's own cases. A node id that no
file holds is a collection error, which `gov accept` reports for the whole run. A run that names a node of this folder,
or this folder with another path, keeps its arguments. `w2_185_support.py` reads the README for `conftest.py` and holds
the cases' helpers (a reader of the hooks sources, stand-in hook entries, stand-in roots in `tmp_path`).
`test_the_readme_maps_every_case_of_this_folder` fails when this folder holds a case the tables do not name, or a name
the file does not hold.

## The map

| KPI id | tests | expected red reason (on the base `31eab2103`) |
|---|---|---|
| S1 | `tests/acceptance/W2-185/test_w2_185_hooks.py::test_s1_the_template_wires_context_watch_in_post_tool_use_beside_posttooluse` | red: `template postToolUse has 0 entries for context_watch.py; one is expected` |
| S1 | `tests/acceptance/W2-185/test_w2_185_hooks.py::test_s1_every_kernel_hook_script_is_named_by_a_command_of_the_template_hooks_source` | red: `no command of template/.rulesync/hooks.jsonc runs: ['context_watch.py']` |
| S1 | `tests/acceptance/W2-23/test_w2_23_space.py::test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir` | red (known, `test_w2_23_space.py:94`): `the settings' hook command lines do not reach the seven kernel hooks: ['context_watch.py']` |
| S2 | `tests/acceptance/W2-185/test_w2_185_hooks.py::test_s2_the_repository_s_two_sources_as_s1_makes_them_give_no_finding` | red: one `HOOKS_MATCHER_DIFFERS` for postToolUse, `matchers ['Bash'] here, ['Bash', 'Bash'] in template/.rulesync/hooks.jsonc` (the lift skips postToolUse only while the root lacks the event) |
| S2 | `tests/acceptance/W2-185/test_w2_185_hooks.py::test_s2_the_posttooluse_entry_beside_the_root_s_one_entry_is_no_finding` | red: the same `HOOKS_MATCHER_DIFFERS` over a stand-in pair |
| S2 | `tests/acceptance/W2-185/test_w2_185_hooks.py::test_s2_post_tool_use_failure_carrying_only_posttooluse_is_no_finding` | green on the base (today's event lift); it keeps the lift for the `posttooluse.py` entry alone when the change lands |
| S2 | `tests/acceptance/W2-185/test_w2_185_hooks.py::test_s2_a_template_with_only_the_posttooluse_entries_and_no_root_event_is_no_finding` | green on the base (today's event lift); it keeps DEC-971 item 3's lift for the `posttooluse.py` entries when the change lands |
| S2 | `tests/acceptance/W2-05/test_w2_05_hooks_source.py::test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources` | green on the base; red with S1's line alone (`HOOKS_MATCHER_DIFFERS`, postToolUse), green with S1 and S2 |
| S2 | `tests/unit/gitenv/test_program_env.py::test_this_repository_s_two_hooks_sources_agree` | green on the base; red with S1's line alone (the same finding), green with S1 and S2 |
| S3 | `tests/acceptance/W2-185/test_w2_185_hooks.py::test_s3_the_w1_38_fixture_copies_exactly_the_kernel_hooks` | red with the fixture as it stood on the base: `HOOK_SCRIPTS [...six...] is not the kernel's [...seven, context_watch.py first...]`; this branch's fixture revision turns it green |
| S3 | `tests/acceptance/W1-38/test_w1_38_rulesync.py::TestHookStubs::test_hook_stubs_exist` | green on the base; red with S1's line and a six-hook fixture: `hook scripts in .claude/settings.json do not exist: ['governance/kernel/hooks/context_watch.py']` |
| S3 | `tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py::TestABashCallAfterAChangeOfDirectory::test_an_ordinary_allowed_call_is_not_blocked` | green on the base; red with S1's line and a six-hook fixture: the PostToolUse command ends with `[Errno 2] No such file ... governance/kernel/hooks/context_watch.py` |
| F1 | `tests/acceptance/W2-185/test_w2_185_hooks.py::test_f1_an_extra_matcher_on_the_root_s_post_tool_use_is_a_finding` | green on the base (the base already finds a drift there); stays a finding when S2 lands |
| F1 | `tests/acceptance/W2-185/test_w2_185_hooks.py::test_f1_a_second_template_stop_entry_with_a_matcher_is_a_finding` | green on the base (a `stop` event is compared today); stays a finding |
| F1 | `tests/acceptance/W2-185/test_w2_185_hooks.py::test_f1_an_event_only_the_template_has_is_a_finding` | green on the base; stays a finding |
| F1 | `tests/acceptance/W2-185/test_w2_185_hooks.py::test_f1_a_template_post_tool_use_entry_other_than_posttooluse_with_no_root_event_is_a_finding` | red: `no hooks finding names postToolUse` (today the whole event is exempt while the root lacks it; the only finding is the root's `stop`) |
| F1 | `tests/acceptance/W2-185/test_w2_185_hooks.py::test_f1_a_template_post_tool_use_failure_entry_other_than_posttooluse_with_no_root_event_is_a_finding` | red: `no hooks finding names postToolUseFailure` (the whole event is exempt) |
| F1 | `tests/acceptance/W2-185/test_w2_185_hooks.py::test_the_readme_maps_every_case_of_this_folder` | green; fails when a case of this folder is not in the tables (the self-check sits under F1 because a case that drops out of the map unseen would let a drift stay a finding no one runs, and `gov accept` reads a KPI cell only as a ticket line) |

## What each case judges

- S1: the template's `postToolUse` holds one `context_watch.py` entry with matcher `Bash`, timeout 10, whose command is the
  root's `context_watch.py` command with `template/governance/kernel/hooks/` written `governance/kernel/hooks/`, and still
  holds a `posttooluse.py` entry; every `*.py` of `template/governance/kernel/hooks/` is run by some command of the
  template's hooks source (`stop.py` is told from `subagentstop.py` by the path separator). W2-23 S6 is the Verify clause's
  settings-reach case: a planted eighth hook script no settings line runs fails it (`...reach the seven kernel hooks:
  ['eighth_hook.py']`).
- S2: `_hooks_findings` over stand-in roots gives no finding where the template's `postToolUse` is the root's entries plus
  the `posttooluse.py` entry (the repository's two sources as S1 makes them, a minimal pair), none for a template
  `postToolUseFailure` carrying only `posttooluse.py`, and none for a template with only `posttooluse.py` entries where the
  root has no such event. The two existing cases of the Verify clause judge the live sources.
- S3: `w1_38_support.HOOK_SCRIPTS`, and the files `build_project_from_template` copies to `governance/kernel/hooks/`, are
  exactly the `*.py` of `template/governance/kernel/hooks/`; the two W1-38 cases judge that the generated settings name
  only copied scripts.
- F1: each planted drift is a finding that names its event (`postToolUse` is told from `postToolUseFailure`): an extra
  matcher on the root's `postToolUse`; a second template `stop` entry with a matcher; an event only the template has; a
  template `postToolUse` or `postToolUseFailure` entry other than `posttooluse.py` where the root has no such event.

## Planted breaks the Verify clauses name (shown in a scratch copy of the base, removed after)

| Break | Result |
|---|---|
| an eighth hook script (`eighth_hook.py`) with no wiring, S1's line planted | W2-23 S6 red: `do not reach the seven kernel hooks: ['eighth_hook.py']` |
| S1's line planted, W1-38's fixture with six hooks | both W1-38 cases red (messages above) and the S3 case red; with the seven-hook fixture they pass |
| S1's line planted, today's `portability.py` | the W2-05 and program_env cases red (`HOOKS_MATCHER_DIFFERS`, postToolUse); with a per-hook exemption (a reference one, scratch only) they pass, and so do this folder's 13 cases |
| an extra matcher on the root's `postToolUse`; a template hook in another event | the F1 cases above: each gives a hooks finding |

## Known reds

W2-23 S6 is red until S1 lands; the cases marked red above turn green with S1 and S2. Nothing in this folder starts a
model, an embedder or the network; the cases run through the repository's own `src` (`PYTHONPATH=<tree>/src`).
