# Lead brief: fix-w2-56, W2-56's environment and refused-argument cases after DEC-1225 and DEC-1232 (6) (fixes under W2-201 `DAEO-k1us`)

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it (node on PATH; `GOV_TESTS_OPTIN=weekly` for W2-56).
Name: `fix-w2-56`; worktree `/home/usain/gov-os-worktrees/E2-fix-w2-56`, branch `e2/fix-w2-56` from `w2/integrate`.
**Do not merge.** Every helper Sonnet; this lead runs medium. It blocks release 0.1.5: green **within about 45 minutes**.
Decide, never ask (you run as `claude -p`).

**The reds** (the third run of the 0.1.5 full suite, on `9beb1d159`; 7 of W2-56's 154 cases):
1. `tests/acceptance/W2-56/test_w2_56_environment.py`: `test_s5_no_parent_claude_gov_or_pythonpath_value_reaches_the_session[engineer|independent-test-designer|independent-auditor|product-spec|research]` and `test_s5_each_parent_variable_set_alone_is_kept_from_the_session[CLAUDE_CODE_SUBAGENT_MODEL]`: "the parent's CLAUDE_CODE_SUBAGENT_MODEL reached the session: 'claude-sonnet-5-5' (not the session's 'claude-opus-5-5')". `src/gov/launch/launcher.py:911` sets `settings["env"]["CLAUDE_CODE_SUBAGENT_MODEL"] = model` (the session's model). Since `models-rubric` and `fixes-015a` F19 (DEC-1225), every one of these roles launches Sonnet whatever its role file says, so the session's own value is Sonnet, which equals the parent value the fixture plants: the case can no longer tell a leak from the launcher's own setting, and its expectation (the session's model is Opus) is pre-DEC-1225.
2. `tests/acceptance/W2-56/test_w2_56_refused_arguments.py::test_s6_a_new_refused_argument_refuses_the_launch[--mcp-config {"mcpServers": {}}]`: the case expects any `--mcp-config` refused; `fixes-015a` F1 (DEC-1232 (6)) made `gov launch` accept only what the role's MCP list allows (read F1's code and its W2-201 cases for the exact rule).

## The flow
1. **Test designer first** (only it edits `tests/acceptance/`): revise S5 so the leak stays detectable after DEC-1225: plant a parent `CLAUDE_CODE_SUBAGENT_MODEL` that differs from what the launcher sets (for example `claude-haiku-5-5`), and expect the session to carry Sonnet, the DEC-1225 helper model (not the parent's value). Revise S6's `--mcp-config` case to F1's rule (a config naming a server outside the role's list is refused; say in the commit what F1 does with an empty one and pin exactly that). `Rewrite-Reason` naming DEC-1225 and DEC-1232 (6) inside the final trailer paragraph of each commit. Run them on the base: if a revised case is red on the base because the launcher really lets the parent's value through, that is a product bug: then the engineer makes the launcher set the helper model explicitly (Sonnet, from the rubric) and never pass the parent's through.
2. **Engineer** only if step 1 shows a product bug.
3. **Green:** `tests/acceptance/W2-56` (weekly), `tests/acceptance/W2-201`, `tests/unit/launch`, `tests/unit/optin`; `gov accept W2-201` exit 0. Record the fix in `.tickets/DAEO-k1us.md` as a `## Fix:` section.
Return: branch and head; whether a product bug was found; the pytest summary lines; the accept summary.
