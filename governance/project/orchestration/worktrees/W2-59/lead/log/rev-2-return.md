task: Second and last independent review (CAP-33, DEC-413) of W2-59's CIT-P and final code at `fef0fcd5`, read-only, probing for behaviour the tests miss under ADR-0001's threat model.

status: DONE. The probe is complete and the judgement is **pass**: no finding against the change is "Ordinary work: yes" with "fails open" or "loses work". One fail-open that predates the change (R2-D1) is reported separately so it can go into a package.

work_completed: I ran Step 0 and built a stand-in pin from this worktree's wheel in my temporary folder, writing nothing into the worktree. I ran the seven hook lines through `sh -c` under that pin, covering:
- a worker's inherited environment;
- pins broken in ordinary ways;
- two rollback forms;
- W2-62's resume injection;
- `PYTHONUSERBASE`;
- `bash` instead of `sh`;
- a guard program with a half-finished edit.

I checked the remade history and run 3's merge with git and with the close's own gate functions, read-only. I checked the judge's checks, the project-root lookups, the wheel's contents and `gov --version`. I checked the CIT-P statement by statement and ran six suites.

files_changed: none. Nothing was written in the repository; the worktree's status was identical before and after. My scripts and builds are only in my temporary folder.

evidence:
- **Sandbox check:** (a) refused with "Read-only file system". (b) `git hash-object -w --stdin` gave `1ae28402…`, and `git update-index --refresh` exited 0.
- **Identity:** `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-kh9l`, top `/home/usain/gov-os-worktrees/W2-59`, branch `w2/W2-59`, HEAD `fef0fcd59401d96c4fbe00bc0d44465e59ed1f53`.
- **Code under test:** with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src`, `gov.__file__` is `/home/usain/gov-os-worktrees/W2-59/src/gov/__init__.py`.
- **Remade merge:** `git merge-tree --write-tree c76cddf5 74d22909` gives `6b2943c8`, which is `e48a601d`'s tree. Its trailers are `Task: DAEO-kh9l`, `Implements: DEC-750, DEC-877`, `Role: orchestrator`.
- **Re-applied commits:** all ten old/new pairs match in patch-id, raw diff, message and author. `d3e594bf`'s tree equals `w2/W2-59-old`'s (`08b3e60b`), and `3eadca4c` is not in HEAD's history.
- **Run 3's merge:** `git merge-tree --write-tree d3e594bf 97fc656a` gives `d26c7e76`, which is `3dbd766d`'s tree. Its trailers are `Task: DAEO-kh9l`, `Implements: DEC-750`, `Role: orchestrator`.
- **Close gate (`_check_unmeasured`, read-only):** W2-59 is clean. None of the 21 commits this branch adds to `97fc656a` names no task.
- **Probe outputs:** the findings below quote them.
- **Read refusals:** 1. A command naming a `.claude/settings.json` path in my temporary folder was refused, and I dropped that route.
- **Other guard refusals:** 2. One write target and one shell variable the guard could not resolve; I rewrote each with literal paths inside my temporary folder.
- **Permission prompt:** 1 not granted (removing my own temporary folder); I used a fresh folder instead.
- **`gov retrieve`:** I asked "DEC-877 W2-59 merge-back remade under DEC-412" and "hook lines pin interpreter -E PYTHONPATH". Both came back `FACET_UNAVAILABLE` (lexical and semantic indexes stale) with no evidence, so they did not help; I read named files instead.
- **Code graph:** not used, because each start writes a setting under the worktree's runtime folder.

tests: every run used `PYTHONPATH=<worktree>/src`, `-p no:cacheprovider` and `PYTHONDONTWRITEBYTECODE=1`.

| Suite | Passed | Skipped | Failed |
|---|---|---|---|
| W2-59 acceptance | 55 | 0 | 0 |
| W1-38 acceptance | 201 | 0 | 0 |
| Builder tests (three W2-59 files and `tests/unit/validate/test_canary.py`) | 16 | 0 | 0 |
| `tests/unit/{check,cli,retrieval,validate}` | 179 | 1 | 0 |
| Acceptance W1-07, W1-22, W1-26, W2-62 | 717 | 1 | 1 |

The one failure is W2-62's live-resume case. Its `claude -p` session could not reach `api.anthropic.com` from this sandbox, so it is environmental, not this ticket's code.

discoveries:
- **R2-D1 (predates the change):** a guard program in the tree with a syntax error exits 1, so the call goes through. W2-10 and W2-18 may edit that program. Row W2-M390 records only the fail-closed side of this.
- **`-E` and `PYTHONUSERBASE`:** `-E` does not keep `PYTHONUSERBASE` out (R2-F1).
- **Template hooks:** the template's own hooks source, used by adopted projects, still starts the first `python3` on `PATH`. That is out of this ticket's scope.
- **Stale index:** this worktree's retrieval index is stale.
- **Integration branch:** `w2/integrate` has moved to `4c25bdfb`.

risks:
- My "nothing written" check compares file names before and after, not the contents of ignored files that already existed.
- One environment listing printed the sandbox proxy's credential (in `GIT_SSH_COMMAND`) to my own tool output. It was not stored and is not repeated here.
- I listed the `~/.local/bin/gov` link once (it points to `pin-fecb870c`) and ran `rulesync` from `~/.local/bin` into my temporary folder. I read nothing else under `~/.local`.
- R2-F1 was shown on a stand-in made with system site packages, which the acceptance support says is how the owner's pin is made. I did not read the owner's pin.

lessons:
- The guard refuses any command that names a `.claude/settings.json` path, even one in a temporary folder.
- The guard also refuses write targets and shell variables it cannot resolve, so probe paths need to be written out literally.
- A read-only reviewer cannot use the code graph.

proposed_decisions:
1. **R2-D1:** make it an entry criterion of W2-10 and W2-18 and add it to row W2-M390. The criterion: the guard line ends with exit 2 whenever its program ends with any code other than 0 or 2, or the program moves with the pin. Recommended, confidence medium. Alternatively, it comes to the owner as a package, as DEC-413 provides for a fail-open left after the second round.
2. **R2-F2:** nothing is committed after the probed head (DEC-413). The CIT-P goes to the owner together with this probe record, which lists what is stale. Confidence high.
3. **R2-F1 and R2-F3:** rows for the Wave 3 hardening pass. Confidence high.

unresolved:
- CIT-P §7 A2's `GENERATED_DIFFERS` is not verified, because verifying it means reading the generated settings file, which every role is refused.
- Where R2-D1 goes is not decided.

recommended_next_action: Commit this probe record under `docs/probes/DAEO-kh9l/` (judgement pass), and carry R2-D1 and R2-F2 in the package that brings the CIT-P to the owner.

````markdown
---
type: probe
task: DAEO-kh9l
reviewer_session: 91d56ad8-529b-4734-bb3d-4f44514872bf
implementer_session: 5b7defda-73f6-4543-a7a2-b374758dcce5
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: fef0fcd59401d96c4fbe00bc0d44465e59ed1f53
---

# Probe record: W2-59 (DAEO-kh9l), the CIT-P's second review

(`CLAUDE_SESSION_ID` is unset; the reviewer session id is this session's own, from its scratchpad path.)

- **What was probed:** head `fef0fcd5` of `w2/W2-59`, run, not only read. The judge was a stand-in pin: this worktree's wheel, built with its build folders in the reviewer's temporary folder (nothing written into the worktree) and installed non-editable in a `--system-site-packages` venv there. It was instrumented after the install and reached through a link at a temporary `HOME/.local/bin/gov`. Projects were built from scratch with single named files. Probed:
  - each of the seven hook lines through `sh -c`:
    - in a worker's environment (`PYTHONPATH`, also `PYTHONHOME` and `PYTHONSTARTUP`);
    - with `PYTHONUSERBASE` set;
    - with a dangling link after a re-pin, an interpreter that is gone, and a pin whose guard module is missing;
    - after the rollback, in pip's user form and in a venv-editable form;
    - with W2-62's session-start hook as the orchestrator on resume;
    - under `bash`;
    - with a guard program left half-edited;
    - `gov launch`'s guard recognition, for every matcher form.
  - the remade history and run 3's merge, with git and with `gov close`'s own gate functions, read-only;
  - the judge's declared checks, the project-root lookups, the wheel's contents, and `gov --version` from the wheel and from the source tree;
  - the CIT-P, statement by statement.

  Suites (worktree `src`):

  | Suite | Result |
  |---|---|
  | W2-59 acceptance | 55 passed |
  | W1-38 acceptance | 201 passed |
  | Builder tests | 16 passed |
  | `tests/unit/{check,cli,retrieval,validate}` | 179 passed, 1 skipped |
  | Acceptance W1-07, W1-22, W1-26, W2-62 | 717 passed, 1 skipped, 1 failed |

  The failure is W2-62's live-resume case: its `claude -p` session could not reach the API from the reviewer's sandbox, so it is environmental.

- **What it found:**

  **R2-F1 (low): `-E` does not keep `PYTHONUSERBASE` out, though CIT-P §3.2 and §9 say it does.**
  - **What was done:**
    - The guard line was run with the stand-in pin for an engineer's Write outside the ticket's paths.
    - `PYTHONUSERBASE` named a folder whose site-packages held a `usercustomize` module and a `gov` package whose guard allows everything.
    - The pin's interpreter was also asked directly under `-E`.
  - **What happened:**
    - Under `-E` the interpreter reports that it ignores the environment. Even so, its user site is the folder `PYTHONUSERBASE` names, that folder is on its import path, and the `usercustomize` module there ran inside the guard's process.
    - The `gov` package there was not imported (the pin's own site-packages comes first), and the pin's guard denied the write.
    - `PYTHONPATH` and `PYTHONHOME` were ignored, as stated.
  - **What should have happened:** either what §3.2 says ("no folder the session names is put on the import path and no sitecustomize there runs", `PYTHONUSERBASE` named among the variables ignored), or the CIT-P says that `PYTHONUSERBASE` still reaches the program. §9's last row ("a user install under a non-default PYTHONUSERBASE does not reach the hook program") is untrue in the same way.
  - Ordinary work: no, because nothing in this repository, the launcher or the sessions sets `PYTHONUSERBASE`. `gov launch` adds only `GOV_ROLE`, `GOV_TICKET`, `TMPDIR` and `CLAUDE_CODE_TMPDIR` to the caller's environment, and it needs a variable set by hand.
  - Consequence: other. A CIT-P statement is untrue; the pin's guard still decided; using the gap is a deliberate construction (DEC-801). This holds for a pin made with system site packages, as the acceptance support says the owner's is.

  **R2-F2 (low): the CIT-P at the head shows decided packages as open, credits a correction to the wrong merge, and leaves two consequences unstated.**
  - **§1 ¶1:** "by the merge `e48a601d` (… its record corrected in `70cfbcf9`)". In fact `70cfbcf9`, re-applied unchanged, corrects the record of `3eadca4c`, as its own message says. `e48a601d` carries its own `Task:`, `Role:` and `Implements:` trailers and needs no correction. The id swap in `a3aefd89` made the sentence untrue of the new merge.
  - **P-W2-59-5:** §1 ¶2 calls it "open with the orchestrator", and §7's row says "Open" and still describes `3eadca4c` reaching `w2/integrate`. DEC-877 items 1 and 2 decided it ((a), with row W2-M394), and §1 ¶3 itself says the branch was remade.
  - **P-W2-59-6 and P-W2-59-7:** §4 says "Two questions stay open" and §7's rows say "Open". DEC-877 items 3 and 4 decided both: P-W2-59-6 (a), as built, and P-W2-59-7, row W2-M393 for W2-56. DEC-877 item 3 also says "The CIT-P's §4 states it", and §4 at the head does not.
  - **§9's four residuals:** they are "proposed" as rows, but DEC-877 item 5 already made them W2-L375 to W2-L378.
  - **Front matter:** `base` names only `74d22909`, and `decisions_carried` lacks DEC-877 and DEC-412, both of which §1 cites.
  - **Unstated consequence 1 (§5):** once the settings hold the new lines, sessions run the pin's guard. A guard change merged later, such as W2-58's read rules or W2-05's containment, then governs those sessions only after a re-pin, as §5 says of a check fix. Before this change, the main tree's sessions ran a merged guard at once.
  - **Unstated consequence 2 (§7 R1, §9):** hook programs being read from the tree is stated only as a fail-closed risk. Its fail-open side (R2-D1) is not stated.
  - **§10** (judged by reading, not reproduced; what remains of the first review's F6): it does not say that reverting this ticket's merge after W2-05 has merged would conflict in `_run_command`.
  - Ordinary work: yes, because the CIT-P is the record the owner reads to approve the change.
  - Consequence: other. No behaviour changes.

  **R2-F3 (info): from a source tree with no git on `PATH`, `gov --version` fails with a traceback.**
  - **What happened:** with the worktree's `src` on `PYTHONPATH` and no git on `PATH`, it ended with `FileNotFoundError`, exit 1. The wheel printed `gov 0.1.0 (commit unknown)`.
  - **What should have happened:** `(commit unknown)`.
  - Ordinary work: no, because a source tree is a git checkout and git is on `PATH` wherever one is used.
  - Consequence: other.

  **Predates the change, so not counted against it: R2-D1, a guard program in the tree that cannot run lets the call through.**
  - **What was done:** the project's `template/governance/kernel/hooks/pretooluse.py` was given a half-finished edit, with one bracket left open. The guard line was then run with the stand-in pin for an engineer's Write outside the ticket's paths.
  - **What happened:**
    - The pin's interpreter stopped on the syntax error with exit 1, and the line passes that code on.
    - Claude Code blocks a PreToolUse call only on exit 2 or a deny decision, so the call would proceed.
    - The line's form at `c5100159` also gives exit 1.
    - By reading, not run: a broken containment program leaves a Bash call unchecked in the same way.
  - **What should have happened:** a guard program that cannot run blocks the call, as the line already does when the pin cannot be found or run.
  - Ordinary work: yes, because W2-10's and W2-18's allowed paths hold `template/governance/kernel/hooks/**`, and an edit left half-finished between two tool calls is an honest slip.
  - Consequence: fails open. That worker's session is unguarded until the file is fixed.
  - **Why it is not counted against this change:**
    - The behaviour is the same before the change.
    - This ticket's hook scope is "the hook command lines' interpreter only" (DEC-835).
    - The program stays read from the tree by design (CIT-P §3.2; R1, row W2-M390, which records only the fail-closed side).
  - **Proposed:** an entry criterion of W2-10 and W2-18. The guard line ends with exit 2 when its program ends with any code other than 0 or 2, or the program moves with the pin. Alternatively, a package to the owner (DEC-413).

  **What was sound:**
  - **Hook lines:**
    - In a worker's environment every line started the pin's interpreter and imported the pin's package. subagentStop imports none; its exit 2 there is its own twelve-field rule.
    - The decoy `gov` and its `sitecustomize` never ran.
    - The guard line denied an out-of-scope Write with and without the inherited `PYTHONPATH`.
    - With a dangling link, a gone interpreter or a missing guard module, the guard line blocked (exit 2) and the after-call lines exited 2 with a message. Nothing fell back to the tree or to the `python3` on `PATH`.
    - Both rollback forms were followed: the editable install's own interpreter decided.
    - `gov launch` recognises the guard for every matcher that covers Write, Edit and Bash, and refuses Bash alone.
    - W2-62's session-start hook, as the orchestrator on resume, injects the whole RESUME HERE section and names the roster's prompt; its sibling import still works under `-E`.
    - `-E` drops nothing that is used: no hook-reached code reads a `PYTHON*` variable, its child processes are git only (the reranker starts with `-I`), and no git hooks are installed.
    - `sh` (dash) and `bash` behave the same.
    - preCompact and sessionStart import a project's own `src/gov` when one exists (row W2-M389, unchanged); stop imports the pin's.
  - **History:**
    - `e48a601d` is git's own merge of its parents (`6b2943c8`), with its trailers.
    - The ten re-applied commits match the old ones in patch, message, author and trailers.
    - The new head's tree equals the old head's (`08b3e60b`), and `3eadca4c` is not in the history.
    - `3dbd766d` is git's own merge (`d26c7e76`) with its trailers. Both sides are reproduced exactly, and none of the ticket's files is touched.
  - **Close gate:**
    - Run with the close's own functions, the work-without-a-task gate passes W2-59.
    - None of the 21 commits this branch adds to `97fc656a` names no task.
    - The 34 refusals among 81 other tickets all cite older commits already on `w2/integrate`.
  - **Judge:**
    - Every declared command starts `python3 -m` or `gov`, no check module starts `python3` or `gov` itself, and `-m gov.cli.main` runs `main`.
    - No module of the package changes its own environment, so the close's in-process checks get the judge's.
    - No module at the head finds repository files from its install path.
    - The wheel holds every tracked file under `src/gov`; `retrieve_baseline.yaml` is the only non-Python one, and a builder test guards it.
    - Copier ships the canaries to adopted projects. `requires-python` is at least 3.11, so `-P` is always known.
    - `gov --version` prints `gov 0.1.0 (commit unknown)` from the wheel, and from the tree `gov 0.1.0 (commit fef0fcd5…)`, run from any folder.
  - **CIT-P statements that are true:**
    - +71/−21 in six files;
    - the lines it cites at `c5100159`;
    - the 543 paths;
    - `98effadc` held by `w2/integrate`, `e48a601d` and HEAD;
    - W2-05 still at `f19f156e`, with the same two conflicts in the same lines at this head;
    - `912ddc63`'s role, Rewrite-Reason and six files;
    - §3.1 and §3.3 to §3.5;
    - §8;
    - §10's three/four line forms;
    - §11's 55, 201 and 16, reproduced at the head.
  - **Roles:**
    - Every engineer commit stays inside the allowed paths, and none touches `tests/acceptance/`.
    - The test designer's commits touch only acceptance tests.
    - The tests (`922dd542`) came before the implementation (`771e9a0c`).

  **Not verified:** §7 A2's `GENERATED_DIFFERS`, because reading the generated settings file is refused to every role. The owner's pin itself was not read.
````