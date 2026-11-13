---
type: probe
task: DAEO-8s85
reviewer_session: 328ba771-d265-41e1-9f2c-c41e9686e6ec
implementer_session: 769bcd53-a269-4a4c-900f-59fdcd84126f
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 0ffe7196e1e2cfc64f9e5da8fef0a438c2e6a80d
---

# Probe of DAEO-8s85 (W2-153), the routed line from W2-33 (success 6): narrow independent check, judgement pass

The check covers only the cases for the ticket's sixth success line, routed from W2-33 (DEC-1156 (3)). They are
`tests/acceptance/W2-153/test_w2_153_routed.py` and the README's "Routed line" section, mapped to `S6`. S1 to S5
and both failure lines were reviewed and merged earlier. The record is narrow: this is not a full re-review.

- **Head probed:** `0ffe7196e1e2` on `w2/W2-153`. Since the branch's integrate merge `9afc9e44d`, its only changes are
  the two test files.
- **Work under check:** the test designer's commit `8f7affc8a81d` (session `769bcd53-a269-4a4c-900f-59fdcd84126f`,
  the `implementer_session` above) and the README map commit `a1212200a`. The map edit was written by session
  `57a09ef0-fe19-44e3-a4b9-870767b7844d` and committed by session `866f2cf6-ba04-4a63-8131-78a39e9a7fe5`.
- **Reviewer:** a fresh independent-auditor, session `328ba771-d265-41e1-9f2c-c41e9686e6ec`, model claude-opus-5-5,
  class C2. It was launched read-only (`--allowedTools Bash Read Grep Glob`) and carried JUDGEMENT.md word for word.
  `git status --short` was empty before and after, and the tripwire shows no change in the W2-153 trees.
- **`gov accept W2-153` on this head (the lead, outside the sandbox):** pass. `success-6` had 71 passed, 0 failed and
  18 skipped; nothing was unmapped; 137 passed and 18 skipped in all.
- **The lead's triage (DEC-1010 item 1):** no finding is in scope, ordinary work and fails open or loses work, so
  READY holds.
  - F1 (`template/.rulesync/subagents/` not compared by the generation check) goes to the CTO as a recorded row.
  - F2 (a duplicate contradicting line would pass the unchanged case) is recorded and needs an unusual
    construction.
  - F3 (`.claude/skills/adopt/SKILL.md` GENERATED_DIFFERS on the tree) is out of scope and goes to the CTO.

## The reviewer's return (verbatim)

task: W2-153 (DAEO-8s85). This was a narrow independent check of success line 6, the line routed from W2-33 under DEC-1156 (3), done as a read-only independent auditor.

sandbox check: passed.
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-153` failed with `OSError: [Errno 30] Read-only file system`.
- (b) `git hash-object -w --stdin` worked (it gave `1ae28402a109…`), and `git update-index --refresh` worked.

ps check: `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing.

status: DONE

work_completed:
- **Identity:** HEAD is `0ffe7196e1e2cfc64f9e5da8fef0a438c2e6a80d`. `git status --short` was empty before and after.
- **Unchanged since integrate:** `portability.py`, the three copy folders and the kernel roles are byte-identical to `w2/integrate`.
- **Reading:** I read the routed test file, the support bed (`PortabilityBed`, `composed_source`, `naming`) and `portability.py`, plus `runner.py::parse_map` and `line_names`. I also read W2-33's ticket: S7, F1 and "Clauses judged elsewhere".
- **README map:** I ran `parse_map` on the README. `success-6` maps exactly the four routed node ids, and no other line maps a routed test.
- **Copy of the head:** I made it with `git archive | tar` under my `$TMPDIR`. The routed file ran 71 passed, 18 skipped.
- **Real check on the copy:** I ran `python3 -m gov.adapters.portability` on the copy with the installed rulesync 24.0.0, before and after planted hand edits.
- **Planted breaks:** I made my own breaks, different roles and folders from the designer's, and ran pytest once more.

files_changed: none. Nothing was written in any tree, and my scratch copy is deleted.

evidence:
- **Unedited copy, pytest:** 71 passed, 18 skipped in 2.19 s.
- **Unedited copy, real check:** no finding on any role copy. Its only finding is `GENERATED_DIFFERS .claude/skills/adopt/SKILL.md`; see F3.
- **Real check with hand edits:**
  - Adding " (edited by hand)" to the `Launch default` line of `.claude/agents/engineer.md` gave `GENERATED_DIFFERS` naming that file.
  - The same edit to the `Skills` line of `.rulesync/subagents/engineer.md` gave `SOURCE_DIFFERS` naming the source. It also named `.claude/agents/engineer.md`, because rulesync regenerates the agent.
  - The same edit to the `Launch by criticality` line of `template/.rulesync/subagents/engineer.md` gave no finding (F1).
- **Planted-break run** (10 failed, 61 passed, 18 skipped). I planted four copy breaks and two mutations, and exactly the 10 predicted cases failed:
  - `engineer::template/.rulesync/subagents::launch-by-criticality` (my template edit, still in place)
  - `qa-engineer::.claude/agents::launch-by-criticality` (hand edit)
  - `orchestrator::.rulesync/subagents::skills` (hand edit)
  - `research::template/.rulesync/subagents::{launch-default,skills}` (copy deleted)
  - All three `generated-agent` drift cases: the generated comparison was made blind to `.claude/agents/`.
  - `launch-default-composed-source` and `launch-by-criticality-composed-source`: the source comparison was made blind to `- **Launch` lines. `skills-composed-source` stayed green, as it should, since Skills was still compared.
- **Scratch:** 117M and 5,666 inodes at the peak. My files are now deleted, leaving 337 inodes, all the harness's own.

tests:
- **Command:** the routed file only, run as `env HOME=<scratch> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=<copy>/src PYTHONDONTWRITEBYTECODE=1 bash …/heavy_slot.sh python3 -m pytest <copy>/tests/acceptance/W2-153/test_w2_153_routed.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`.
- **Runs:** twice, once unedited and once with the breaks.
- **Exclusion:** no `-m`/`-k` was needed for a single file, which has no real-model cases. Nothing was left out.

discoveries:
- **D1, the stand-in's limit:** the drift cases' "the other file is not named" holds only because the stand-in rulesync copies fixed output. With the real rulesync, a source edit also names the regenerated agent. That is right for the check; the case simply doesn't model it.
- **D2:** `heavy_slot.sh` under this sandbox can't append to `log/heavy-slot-waits.jsonl` or remove `/tmp/gov-os-heavy-prio-*`, because both are read-only. It printed warnings but still ran the job.
- **D3:** at this head the real check is red on the repository's own tree because of `.claude/skills/adopt/SKILL.md` (F3).

risks: drift in `template/.rulesync/subagents/` is not caught by this repository's standing generation check (F1). The three S6 lines there are still guarded by S6's carried cases whenever W2-153's acceptance runs.

lessons:
- With the real rulesync on a `git archive` copy, you can check a generation-check clause end to end in under a minute, without touching the repository.
- The rm safety check refuses `$TMPDIR/home`; use literal paths.

proposed_decisions: none.

unresolved:
- Should `template/.rulesync/subagents/` be named by `gov.adapters.portability` itself, for example compared with `compose()` the way `.rulesync/subagents/` is? I recommend a Wave 3 row, not a round (F1).

recommended_next_action: land S6 on this verdict and record F1 to F3 as rows. No round is needed.

judgement: pass

**Classification (one line):** 3 findings. None is in scope, reachable in ordinary work and failing open or losing work. F1 is in scope, ordinary work yes, consequence other. F2 is in scope, ordinary work no, other. F3 is out of scope, ordinary work yes, other. All three are rows; none blocks.

**Answers to the brief's questions**
1. **Both clauses are covered, with no silent narrowing.**
   - **Unchanged:** the cases cover 9 roles × 3 folders × 3 labels = 81. The 18 skips are exactly the six role files with no `Launch by criticality` line, times three folders. I confirmed by grep that only engineer, independent-test-designer and qa-engineer carry that line, so no other spelling is skipped. The guard case requires `Launch default` and `Skills` in every role file. All three labels are single lines with no continuation lines, so checking whole lines loses nothing.
   - **The folders:** the three folders hold exactly the nine kernel roles, and they are the only committed role copies. The `.gov-runtime/codeintel` mirror is an index, not a copy.
   - **Drift named:** all three labels are tested in both the generated agent and the composed source. The control case shows the unedited stand-in is clean.
2. **Each case can fail.** My planted breaks above failed exactly the predicted cases. The real check also names a hand edit to the real `.claude/agents/engineer.md` and `.rulesync/subagents/engineer.md`, so the clause holds beyond the stand-in.
3. **The map is right.** The header's `KPI line` column is index 0 and `Test (node id)` is index 2. `S6` is read as `success-6`, and the four items are full node ids.

**Findings**

- **F1.**
  - **What I did:** on a copy of the head, I hand-edited the `Launch by criticality` line in `template/.rulesync/subagents/engineer.md`, then ran the real generation check.
  - **What happened:** no finding named the file. The check compares `.rulesync/subagents/` and `.claude/agents/` but only the hooks source under `template/.rulesync/`.
  - **What should have happened:** if the template's copies count as "generated role copies" (the routed test treats them so for the unchanged clause), the check should name the edit.
  - **Scope:** in, for the line's general clause. The verify wording, "a planted hand edit in one copy is named", is met by the other two folders.
  - **Ordinary work:** yes, because an honest agent with this path can edit the template copy. W2-33 itself has `template/.rulesync/subagents/orchestrator.md` in its paths.
  - **Consequence:** other. The drift goes unnoticed in this repository's check, but no guard opens and no work is lost. S6's carried cases still catch a change to the three lines (my planted break failed). By reading, not run: an adopted project's own check compares its `.rulesync/` (taken from the template) with `compose()` and would name the drift there.
  - **What would reverse it:** an adopted project built from a drifted template whose own portability check passes, which would make it fail open in adopted projects. Or a reading of S6 / W2-33 F1 that excludes the template copies, which would make it scope out.

- **F2.**
  - **What I did:** I read how the unchanged cases test a line: the kernel line must appear anywhere among the copy's lines.
  - **What happened:** a copy that keeps the kernel's line and also has a second, different line with the same label would pass. This is from reading the code; I did not run it.
  - **What should have happened:** the copy's lines with that label equal the kernel's.
  - **Scope:** in.
  - **Ordinary work:** no, because a hand edit that keeps the original line and adds a contradicting duplicate is an unusual construction. The generation check also names it in `.claude/agents/` and `.rulesync/subagents/`.
  - **Consequence:** other.
  - **What would reverse it:** a real copy in the history carrying such a duplicate.

- **F3.**
  - **What I did:** I ran the real generation check on the unedited copy of the head.
  - **What happened:** it exits 1 with `GENERATED_DIFFERS .claude/skills/adopt/SKILL.md`.
  - **What should have happened:** a clean exit 0 on the repository's own tree.
  - **Scope:** out. This is a skill, not a role copy.
  - **Ordinary work:** yes, because anyone running the check on this tree hits it.
  - **Consequence:** other. The check is red, which is the safe direction. But a later role-copy drift would show up next to an existing red rather than turning a clean check red.
  - **What would reverse it:** the same check exiting 0 on integrate's head with the same rulesync.

```verdict
{"kpis": [{"kpi": "success-6", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```

decisions: DEC-1156 (3), DEC-315, DEC-957, DEC-1112 (3), DEC-801, DEC-808, DEC-1010, DEC-1014. None of them is superseded or PROPOSED, as far as I could tell.
