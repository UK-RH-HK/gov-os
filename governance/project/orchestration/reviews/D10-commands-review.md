# D-10's red-fix list: the review of brief, links and plan recorded in the command lists (W2-20, DAEO-r30l)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-commands-review.md`; branch `w2/W2-20-d10c at 1732686b3 and w2/W2-20-d10c-tests at f1bb1819f`; reviewer log `/home/usain/gov-os-worktrees/W2-20-d10c-tests/.gov-runtime/scratch/lead/log/D10-commands-review.json`.
- verdict.py: READY (no blocking finding).

sandbox_check: Passed. (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-W2-20','w').write('x')"` was refused with `OSError: [Errno 30] Read-only file system`. (b) `echo sandbox-trial | git hash-object -w --stdin` printed `1ae28402a109…` and `git update-index --refresh` exited 0.

ps_check: `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` printed nothing.

task: DAEO-r30l (W2-20, D-10's red-fix list: `brief`, `links` and `plan` recorded in the command lists)

status: DONE

work_completed:
- Identity holds: `printenv GOV_ROLE GOV_TICKET` printed `independent-auditor` and `DAEO-r30l`.
- Both heads are an integrate merge (7b422979c617) on top of the commit under review:
  - designer: `bc772b14a2d1` on top of `f1bb1819f7ea`;
  - engineer: `97efe2a1dfd5` on top of `1732686b30b9`.
- Each head differs from integrate only by its own commit: 7 test files for the designer, `src/gov/check/commands.py` (+2) for the engineer.
- I read both diffs, the full revised cases, the support lists, the code check, the skill validator, the CLI's command discovery, both workers' briefs, the ticket's `allowed_paths`, and DEC-542, 747, 753, 1050, 1052, 1074, 1087, 1088, 1109 and 1112, plus D10-REDS §6.2 and DECIDED-NOT-DONE row 115.
- I also searched for every other list of command names.

files_changed: none. Both trees' `git status --porcelain` is empty.

evidence:
- Commands run: `git log`, `git show`, `git diff --stat` (common parent to head, integrate to head), `git status --porcelain`, `printenv`, `ls` of the two brief folders, and the step-0 and `ps` checks. Everything else was read with Read and Grep.
- No TMPDIR folder was created, so there is nothing to `du`.
- Step 0's `hash-object -w` wrote one loose blob (`1ae28402a109`, the text `sandbox-trial`) into the shared object store, as the check prescribes. It is not in any tree.

tests: none run. My role runs code only to reproduce a finding, and neither finding needs a run. So no exclusion applied and nothing was left out.

discoveries:
- **How the red arose.** DEC-747 item 1 says a later ticket that adds a `gov` command needs `src/gov/check/commands.py` in its paths, and the orchestrator checks this before each start (register line 8100). That check missed W2-129, W2-136 and W2-152. The known next commands are W2-37's `impact` (DEC-812 item 6) and W2-12's `approve`. `release` waits for W2-20's close (DEC-753).
- **Stale case counts.** The `Cases:` header lines in W1-07's and W1-26's READMEs date from D-4's cut. They are now short by 3 and 6. Nothing parses them, and the appended paragraphs give the right counts (10 and 20).

risks: A merged-pair run without `--optin=breadth` collects none of the nine new W1-07 and W1-26 rows, and would still come out green (F2).

lessons: A citation given in a brief is worth checking against the register before it is copied into code, tests and trailers (F1).

proposed_decisions: none

unresolved: I cannot see whether the CTO's helper's merged run used `--optin=breadth`.

recommended_next_action:
- Merge both branches. They touch separate files, so the merge is clean.
- Run W1-07 and W1-26 with `--optin=lifted,breadth`, and W1-32 as it is. Confirm that `[brief]`, `[links]` and `[plan]` are collected and green in all three revised parametrized functions.
- F1's citation can ride along the next time these lines are touched (DEC-802), or stay a row.
- F2 goes to the test-suite owner as a Wave 3 row.

decisions: DEC-753, DEC-747, DEC-542, DEC-1052, DEC-1050, DEC-1112, DEC-1088, DEC-1074, DEC-1087, DEC-1061, DEC-1109, DEC-801, DEC-1010

---

## Answers to the checks

**1. The exact sets are still exact. Yes.**
- **An unrecorded command still fails.** W1-32's `extra` assertion (`test_w1_32_command_set.py:92-93`) is unchanged.
- **A recorded command gone from `gov --help` still fails.** The `gone` assertion (`:90-91`) is unchanged.
- **The pins are exact.**
  - W1-32's pin (`:84-85`) holds W1-07's list, minus `release`, to exactly the eight names.
  - W1-07's count case (`test_w1_07_recorded_commands.py:50-51`) holds exactly the nine.
  - Adding or dropping a name fails both.
- **`lock` stays a module command.**
  - `RECORDED_MODULE_COMMANDS = ("lock",)` is unchanged in both lists.
  - W1-32 `:86` and `:94` still pass.
  - W1-07's `lock` case and W1-26's two `lock` skill cases are untouched.
- **`release` alone stays excused.** `EXCUSED_UNTIL_RECORDED = ("release",)` is unchanged, and `release` is in neither list.
- **No assertion was weakened.** W1-26's file changed only in docstrings and one comment.

**2. The three are real commands. Yes. The cited decisions are right for `links` and `plan`, but not for `brief` (F1).**
- **Modules.** `src/gov/brief/command.py`, `src/gov/links/command.py` and `src/gov/plan/command.py` exist.
- **`gov --help`.**
  - The CLI offers every `src/gov/*/command.py` it finds (`src/gov/cli/main.py:109-114`).
  - There are 21 command modules: exactly the twelve, the eight recorded and `release`.
  - I did not run `gov --help` myself. This rests on reading the code and on the designer's green W1-07 cases for the three, which assert both that each is offered and that `gov <name> --help` exits 0.
- **`plan`.** DEC-1088 (1)-(2) approves `gov plan` and W2-136's KPI lines. Correct.
- **`links`.** DEC-1074 (7) adopts LINK-INTEGRITY with W2-129 as a new ticket. Correct. DEC-1087 changed only item (7)'s O1 (A), and its item (4) orders W2-129 built.
- **`brief`.** It is cited as DEC-1088 (3), which is not the decision that approved the command (F1).
- **The procedure.** DEC-753's basis names exactly the two lists changed here, citing DEC-747. D10-REDS §6.2 and DECIDED-NOT-DONE row 115 assign this item to the CTO, under DEC-1109 (2)'s red-fix list.

**3. No other list needs the three.**
- **The skill validator** uses `GOV_COMMANDS` from `commands.py` (`skill_validator.py:23`, `:124`), so the engineer's line covers it.
- **Unit tests that read the list** are unaffected by appending:
  - `test_kernel_followup.py:100-109` reads the list as it finds it;
  - `test_w2_96_run2.py:383-386` only checks that `accept` is in it.
- **`facts.yaml` `commands:`** is the template-fill map. It already has `links` (`:46-48`), and no template uses `{CMD:brief}` or `{CMD:plan}`.
- **`harness_allowed`** lists tool names, not commands.
- **The kernel template's `settings.json`** allows only `Bash(gov launch:*)`, which is not a command list.
- **API-0002** has no list of command names.
- **CLAUDE.md** names no `gov` commands.
- **The role files** name only `gov launch`.
- **No skill** names any of the three.
- **`test-map.yaml`** maps paths to suites.
- **The template** holds no copy of `commands.py`.

**4. Trailers and files. Yes.**
- Both commits carry exactly the trailers their briefs prescribed:
  - `Task: DAEO-r30l`;
  - `Implements: DEC-1109, DEC-753`;
  - `Role: engineer` or `Role: independent-test-designer`;
  - `Co-Authored-By`.
- The designer's `Rewrite-Reason` is word for word the brief's.
- The engineer changed only `src/gov/check/commands.py`, which is in the ticket's `allowed_paths` (line 21).
- The designer changed only W1-07, W1-26 and W1-32 files. In W1-32 that is only `test_w1_32_command_set.py`, and all three README lines were appended, not edited.

## Findings

Classification: F1 is in scope, ordinary work yes, consequence other (a row). F2 is out of scope, ordinary work yes, consequence other (a row). No finding blocks, and no round is proposed.

**F1. The decision cited for `brief` is not the one that approved the command.**
- **What was done.**
  - Both commits cite `brief` as "(W2-152, DEC-1088 (3))".
  - That covers the engineer's comment (`commands.py:15`), the support comment, three docstrings, three README paragraphs and the Rewrite-Reason.
  - The citation was copied from both briefs and D10-REDS.md:137.
- **What happened.**
  - DEC-1088 (3) (register lines 13679-13683) decides the `reads:`, `needs:` and `waits_on:` fields. It names neither `gov brief` nor W2-152. Neither name appears anywhere in the register.
  - `gov brief` is W2-128's TPL-3. It was approved in DEC-1052's "TPL-1 to TPL-8 as one package" (line 13028), and split into W2-152 as a CTO-delegated P2 under DEC-1112 (3).
  - W2-152's own S1 cites `[DEC-1050, DEC-1052]`. DEC-1088 (3) backs only W2-152's S9, the dependency check inside the command.
- **What it should be.** "W2-152 (W2-128 TPL-3; DEC-1052, DEC-1112 (3))", with DEC-1088 (3) added for its dependency check if wanted.
- Ordinary work: yes, because a worker copies the citation its brief gives, as both did here.
- Consequence: other. A reader tracing the approval lands on a decision about ticket fields. Nothing fails open and no work is lost.
- Scope: in.
- **What would reverse it:** a register line I missed that approves the `gov brief` command or W2-152 under DEC-1088.

**F2. The default run does not check the code's list against the tests' list.**
- **What was done.** D-4's cut (DEC-1061) put every W1-07 and W1-26 recorded-commands case in `tests/optin-lifted-breadth.txt` (lines 42-44 and 466-470). Only W1-32's case runs by default, and it reads W1-07's list, not the code's.
- **What happens.** Suppose only one sibling branch is merged, or a later edit drops a name from `commands.py`. Then:
  - the default run stays green;
  - the skill validator would refuse a skill that names the dropped command;
  - `core-commands` would stop checking that command's module, though W1-32 still catches a missing module through `gov --help`.
- **Effect on this revision.** The six W1-26 rows that prove the engineer's line are collected only with `--optin=breadth`.
- **What should happen.** The merged pair is verified with breadth. Whether one default case should hold the two lists equal is for the test-suite owner to decide.
- Ordinary work: yes, because running the default selection, or merging one branch without the other, needs no unusual construction.
- Consequence: other. The short list fails closed in the skill validator, and the module check is still covered by W1-32.
- Scope: out. The placement comes from D-4's cut, and this revision's lines are correct as read.
- **What would reverse it:** a default-run case I missed that compares `src/gov/check/commands.py::RECORDED_GOV_COMMANDS` with W1-07's list.

## Probed and found sound
- **The code check.** The engineer's three names match the module folders and W1-07's list exactly. `GOV_COMMANDS` is computed after the append, so `core-commands` gets stricter (all three modules are present) and the skill validator accepts only real commands.
- **W1-26's fixture.** `reserved_command_module_files` (`w1_26_support.py:289-295`) finds a module for any name. Nothing on `gov check`'s path imports the three commands' modules, so the merged rows can plant their defect and run.
- **The integrate merges** lost nothing.
- **The appended README counts** match the parametrization.

```verdict
{"kpis": [{"kpi": "command-lists-three", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```
