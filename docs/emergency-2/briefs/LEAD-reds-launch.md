# Lead brief: reds-launch (the launcher, role files, hooks, templates)

Read `/home/usain/Dynamic-Agentic-Engineering-OS/docs/emergency-2/briefs/REDS-COMMON.md` first and follow it.
Branch `e2/reds-launch` from `w2/integrate`, worktree `/home/usain/gov-os-worktrees/E2-reds-launch`. Task trailer:
`Task: emergency-2`, `Class: Q`. Kernel and instruction text named below may change in your branch: the CTO approves it
by naming it here (§3.5).

**Your reds**
1. **W2-33 (36 cases: `test_w2_33_lines`, `test_w2_33_files` S8, all of `test_w2_33_planted`).** The CTO already fixed
   the line form (76073838d). What remains: W2-33's S7 table and S8 expect Opus for `orchestrator.md`,
   `senior-engineer.md` and `ticket-lead.md`; DEC-1212 (3) put every lead on Sonnet, and the role files say so since
   24a384ae8. The CTO's decision: (T) the S7 table and the S8 line follow DEC-1212 (3); the role files stay.
2. **W2-153 `test_w2_153_launch` (5 cases): "the launch changed beyond the one flag".** The launch's arguments changed
   with gov launch's no-prompt default (b33eecd9e) and the launcher without the guard and the sandbox (85710e6e6),
   both right by EMERGENCY-2 §2.2-2.3. (T) if the difference is only theirs; (C) if anything else changed.
3. **W2-50 `test_w2_50_last_review` (3 cases): "the sandbox may not write the session's temp folder".** The sandbox is
   retired (§6.1). (T): retire what asserts the sandbox; keep whatever else the cases check.
4. **W2-185 `test_s1_the_template_wires_context_watch_in_post_tool_use_beside_posttooluse`:** the root's
   `context_watch.py` hook command (the `$HOME/.local/bin/gov` form) and the template's (the newer form that looks in the
   git common dir first and exits 0 when no gov is found) differ. The template is the canonical source. (R): bring the
   root's copy to the template's (by the generator that writes it, if there is one); (T) only if the test pins the old
   form.
5. **W1-29 `test_hook_copies_identical[stop.py]`:** `src/gov/hooks/stop.py` and
   `template/governance/kernel/hooks/stop.py` differ; the template is canonical. Check which change is the intended one
   (`git log` both); (R) bring the other copy to it.
6. **W1-35 `test_the_brief_has_a_placeholder_for_each_thing_it_is_filled_in_with[engineer]`:** `brief.md` and
   `role-engineer.md` have no placeholder for `decisions`, which the brief is filled with. Find which side moved
   (probably W2-197's memory-by-construction change to the templates or `gov brief`). (C or R): a template that lost its
   placeholder gets it back; a filler that no longer fills it, the test follows (T).
7. **W2-188 `test_w2_188_copies` (2 cases): the adopt skill is at `version: "1.2.0"` with 5 hunks against W2-188's base;
   the test pins 1.1.0 and 4 hunks.** The skill changed after W2-188 (find the change; probably the memory-first line).
   (T): the pins follow the skill as it stands; W2-188 reopens at the lift (DEC-1210 (8)).
8. **`tests/unit/orchestration/test_cto_safety_nets.py` (2-3 cases): the test reads the live CTO inbox** ("inbox: 4
   item(s) unread"). (C, unit test): isolate it from the live inbox (its own temp inbox or address).
9. **W1-30 r15 `test_another_object_with_exit_code_0_is_still_a_finding[unmeasured, exit code 0]`:** `gov check`
   answers RED on graph integrity in the case's fixture where the case expects the unmeasured verdict. Find why; T or C.
