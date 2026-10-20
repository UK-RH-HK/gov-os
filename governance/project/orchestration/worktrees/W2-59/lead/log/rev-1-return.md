Probe of head `9b9faac3` is complete. The judgement is **fail**, on one finding (F1): in every worker session the new hook lines still run the worktree's guard instead of the pin's. This isn't a regression: the old lines did the same, and this change was meant to end it. A second finding (F2) fails closed, so it doesn't fail the probe, but it needs a decision before the merge.

task: Independent CIT-P review (CAP-33) of W2-59 (DAEO-kh9l) at head 9b9faac3, read-only, probing for behaviour the acceptance tests miss
status: DONE — probe complete; judgement fail on F1 (ordinary work: yes, fails open); F2 (ordinary work: yes, fails closed) needs a decision before W2-59 merges
work_completed: Built a stand-in pin from this worktree's wheel in my temporary folder (nothing written to the worktree) and ran it. Ran the declared checks, all seven hook lines through `sh -c` in about 20 setups, `gov launch`'s guard recognition, canaries and the retrieval check from the wheel in both layouts, and `gov --version`. Judged the merge-back 3eadca4c (its tree, both sides, the close's gates, using the close's own functions on the real history and on a repository built from scratch). Rebuilt the revised W1-26 case from single files, with a control. Checked the CIT-P statement by statement. Ran the W2-59, W1-38 and builder suites.
files_changed: none
evidence: Sandbox check first: (a) the write outside the worktree was refused (OSError: [Errno 30] Read-only file system); (b) `git hash-object -w` gave 1ae28402…, and `git update-index --refresh` exited 0. Identity as expected: GOV_ROLE=independent-auditor, GOV_TICKET=DAEO-kh9l, top /home/usain/gov-os-worktrees/W2-59, branch w2/W2-59, HEAD 9b9faac3ee45ba9160a110025d6a79cd305501e9. `gov.__file__` = /home/usain/gov-os-worktrees/W2-59/src/gov/__init__.py. Guard read refusals: 0. There was one write refusal ("Bash write to '/<guard-unresolvable>' denied"), for a write target held in a shell variable; I redid it once with literal paths. `gov retrieve`: one question ("DEC-822 the pinned judge: what item 3 and step 2 require of the declared checks and the hook lines") returned FACET_UNAVAILABLE because both facets are stale; it did not help. Rebuilding the index would write under `.gov-runtime/`, so I read the register directly. The code-graph tools are not in this session; I used targeted searches of named folders. This session's own environment carries PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src. 3eadca4c's tree 6b2943c8 equals `git merge-tree --write-tree` of its parents; that command and step 0 wrote only loose objects (no ref, index or worktree file changed). Git status at the end is clean apart from the sandbox's placeholder dotfiles.
tests: tests/acceptance/W2-59: 41 passed, 3 deselected (the gitleaks cases, which use a binary under ~/.local; not run). tests/acceptance/W1-38: 201 passed (204 s). Builder tests (the three test_w2_59 files plus tests/unit/validate/test_canary.py): 16 passed. W1-26 and W1-22 suites not run: their fixtures copy the working tree or need gitleaks and an embedder; W1-26's mechanism was rebuilt instead.
discoveries: F1: the committed launch form (`PYTHONPATH=<worktree>/src python3 -m gov.cli.main launch …`, governance/project/briefs/LEAD-w2-common.md line 42) plus the launcher passing its whole environment to the session (src/gov/launch/launcher.py:319) put the worktree's `src` on the import path of every worker's hooks and of any bare `gov` in those sessions. Existing row W2-L173 covers only a relative PYTHONPATH. F2: the merge-back's missing `Task:` trailer makes the close's "work without a task" gate refuse other tickets' closes once W2-59 lands.
risks: After the merge, F2 can't be repaired without rewriting w2/integrate's history or changing the close: correction commit 6d4925ab is not read by any gate, and the accepted history (DEC-734) applies only to the trailer gate. Unless F1 is fixed, regenerating the settings file (A2) gives workers no pinned guard. If W2-05's resume resolves its runner conflict by literally keeping both sides, the four PYTHONPATH lines come back; W2-59's acceptance tests would catch that at W2-05's close.
lessons: Test hook lines and a bare `gov` under the environment a launched worker actually has, not a clean one. Every merge needs `Task:`, or the close attributes everything it brings as work with no task.
proposed_decisions: Classification first (DEC-809): F1 ordinary + fails open; F2 ordinary + other; F6 (CIT-P text) ordinary + other; F3–F5 not ordinary, Wave 3 rows. P-F1: (a) in W2-59's resume, the hook lines' programs import the pin's package whatever PYTHONPATH the session inherited, with an acceptance case run under a worker's environment (test designer first, W1-38 re-checked); (b) as well, the launch form or the launcher stops carrying PYTHONPATH into sessions (outside W2-59's paths), which also covers a bare `gov` there; (c) defer as a raised row. I recommend (a) now and (b) as a package; confidence medium-high. P-F2: (a) before the merge, the merge-back is remade with its trailers (rewrites only the unmerged ticket branch); (b) merge as is and give the close a reading for it later (a judge change); (c) merge as is, which leaves the affected closes refused. I recommend (a); confidence medium, as it sits against DEC-750's no-rewrite practice.
unresolved: CIT-P §7 A2's "adapter-portability RED with one finding, GENERATED_DIFFERS" is not verified: running that check means reading .claude/settings.json. That Claude Code passes its process environment to hook commands is documented behaviour, not observed inside the harness; the lines' behaviour under that environment is reproduced. The 3 gitleaks cases, the W1-22 suite and the W1-26 suite were not run by me.
recommended_next_action: Take P-F1 and P-F2 to the orchestrator before the owner approves the CIT-P; F1's fix and the CIT-P corrections ride in W2-59's resume (DEC-802).

---
type: probe
task: DAEO-kh9l
reviewer_session: b3eef354-6cf1-408e-9d9c-c01f77de26ca
implementer_session: 5b7defda-73f6-4543-a7a2-b374758dcce5
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: 9b9faac3ee45ba9160a110025d6a79cd305501e9
---

# Probe record: W2-59 (DAEO-kh9l), the CIT-P review

(`CLAUDE_SESSION_ID` is unset; the reviewer session id is this session's own, from its scratchpad path.)

- **What was probed:** head `9b9faac3` of `w2/W2-59`, run, not only read. The judge was a stand-in pin built from this worktree's wheel, in a venv in the reviewer's temporary folder, reached through a link at a temporary `HOME/.local/bin/gov`. Projects were built from scratch with single named files. Probed:
  - the declared checks under that judge: a decoy `src/gov`, a `gov/` at the project root, decoy `python3`/`python`/`gov` first on `PATH`, seven forms of a declared command, a check module new in the tree, and an inherited `PYTHONPATH`;
  - each of the seven hook lines through `sh -c`: the pin by link and by `PATH`, `HOME` unset, no pin, a dangling link, an interpreter that is gone, pip's long-form script, an `env` first line, an environment without the package, odd first lines, an inherited `PYTHONPATH`, and W2-62's session-start hook run as the orchestrator;
  - `gov launch`'s guard recognition with the new line;
  - canaries and the retrieval-regression check from the wheel, in both layouts, with decoys at the install path; the baseline in the wheel; `gov --version` from the wheel and from the source tree;
  - the merge-back `3eadca4c`: its tree, both sides, and the close's gates;
  - commit `45c6bfae`'s three revised cases, with W1-26's mechanism rebuilt from single files and a control;
  - the CIT-P, statement by statement.

  Suites: W2-59 acceptance 41 passed (3 gitleaks cases not run), W1-38 201 passed, builder tests and `tests/unit/validate/test_canary.py` 16 passed.

- **What it found:**

  **F1 (high): in every worker session the hook lines still run the worktree's guard, not the pin's.**
  - **What was done:** the new preToolUse line was run with the environment a worker started by the committed launch form has. That form (`governance/project/briefs/LEAD-w2-common.md` line 42) puts `PYTHONPATH=<worktree>/src` on the `gov launch` command, and the launcher hands its whole environment to the session (`src/gov/launch/launcher.py:319`). This review's own session carries `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src`.
  - **What happened:**
    - The line starts the pin's interpreter, which honours the inherited `PYTHONPATH`. The same line's program imported the pin's `gov/guard/decide.py` in a lead's environment, and `/home/usain/gov-os-worktrees/W2-59/src/gov/guard/decide.py` in a worker's.
    - With an edited guard in the project's `src/gov/guard/` that allows everything, the line refused a Write outside scope without `PYTHONPATH` (the pin's guard). With `PYTHONPATH=<project>/src` it ended with exit 0 and no decision, so the call was allowed, and the edited guard decided.
    - A bare `gov check` with that environment ran the project's own `gov` package: the pin's console script imported it.
  - **What should have happened:** a hook program imports the pin's package in every session, whatever `PYTHONPATH` the session inherited, or no session inherits it. The acceptance tests run each line with no `PYTHONPATH`, so they cannot see this.
  - **Context:** not a regression; the old lines put the project's `src` on the path explicitly. But DEC-822 step 2's purpose holds only in sessions without `PYTHONPATH` (leads, the orchestrator). CIT-P §3.2 ("the program imports the pin's installed package") and §4 ("a bare `gov` is the pinned judge") are untrue in worker sessions, and §9 does not list the risk. The nearest existing row is W2-L173, which covers only a relative path.
  - Ordinary work: yes, because every sandboxed worker is started by the committed form and the launcher passes the caller's environment on; this very session carries it.
  - Consequence: fails open. Any ticket that edits a module the guard imports has its engineers and test designers guarded by its own in-progress code. W2-58, W2-05, W2-09, W2-10 and W2-42 have `src/gov/guard/**` in their allowed paths, and W2-58 is editing the read rules now. This is the state the ticket's own "Why" classes as ordinary work: yes, fails open. Reproduced: an edited guard allowed a write the pin's guard refused.

  **F2 (high for the wave's closes): the merge-back 3eadca4c names no task, so other tickets' closes will refuse once W2-59 lands.**
  - **What was done:**
    - `gov close`'s "work without a task" gate was run with the close's own functions on the real history at this head, which is what `w2/integrate` will hold after W2-59 lands.
    - The same history shape was built from scratch, with and without the trailer.
  - **What happened:**
    - The merge has no `Task:` or `Role:`. Every other merge in the history has both.
    - Against its first parent it brings 543 paths, including other tickets' own files.
    - The gate refuses W2-63 (LITE), W2-58 and W2-62 (STANDARD), and W2-05 and W2-12 (FULL, probed after the merge). Each refusal names only `3eadca4c`.
    - W2-50's FULL probe gate measures the merge (it holds both probed commits) and exempts it.
    - W2-59's own close: no finding.
    - From scratch: without the trailer, WORK_WITHOUT_TASK (exit 3); with it, no finding.
    - The correction in `6d4925ab` is read by no gate, and the accepted history (DEC-734) does not apply to this gate.
  - **What should have happened:** the merge-back carries `Task: DAEO-kh9l` and `Role: orchestrator` (DEC-750 item 3), so its paths are read as this ticket's merge.
  - **Otherwise sound:** the merge is git's own merge of its parents (tree `6b2943c8` equals `git merge-tree --write-tree`). Each side's changes are reproduced exactly, and it touches none of W2-59's paths. CIT-P §1 says the merge is "corrected in 6d4925ab" but does not state this consequence.
  - Ordinary work: yes, because leaving out trailers on a routine merge-back is an honest slip; it happened here.
  - Consequence: other. It fails closed: false refusals counted toward those tickets' escalations, permanent once in `w2/integrate` unless history is rewritten or the close changes. Nothing fails open and no work is lost.

  **F3 (low, Wave 3 row): the preToolUse line only checks that the named interpreter is an executable file.**
  - **What happened:** a `gov` found by the line whose first line names `/bin/true`, `/bin/false` or a folder made the line end with exit 0, 1 or 126. That is allowed or non-blocking.
  - **What should have happened:** a blocking answer whenever the program could not decide.
  - Ordinary work: no, because the pin's and the rollback's console scripts always name a working Python; this needs a hand-made `gov`.
  - Consequence: fails open.

  **F4 (low, Wave 3 row): `gov --version` from a source tree follows an inherited `GIT_DIR`.**
  - **What happened:** with `GIT_DIR` set by hand to the main checkout, the worktree's code printed commit `0cbe240a` instead of `9b9faac3`. It also names `HEAD` without saying the tree has uncommitted changes.
  - **What should have happened:** it names the commit of the code that runs.
  - Ordinary work: no, because it needs a git variable set by hand (DEC-801), or a source install run inside another repository's git hook.
  - Consequence: other (a wrong provenance line).

  **F5 (low, Wave 3 row): only a command whose first word is exactly `python3` or `gov` is rewritten.**
  - **What happened:** declarations written as `python …`, `/usr/bin/python3 …`, `env python3 …`, `python3` followed by a tab, or after another command (`true && python3 …`) ran the first interpreter on `PATH` (the decoy ran), without the judge's package.
  - **What should have happened:** either every declared Python check runs with the judge, or a declaration in another form is refused.
  - Ordinary work: no, because no declaration uses another form today.
  - Consequence: other (on this machine such a check fails closed with no `gov` module).

  **F6 (low): CIT-P text.**
  - **What happened:**
    - §3.2 and §4 are untrue in worker sessions (F1).
    - §1 omits F2's consequence; §9 lacks F1's risk.
    - §10 says the hook lines return to `PYTHONPATH="$CLAUDE_PROJECT_DIR/src" python3 …`, but only three of the seven had that form; four were a bare `python3 …`. A revert after W2-05's merge would not be clean.
    - §7 A2's GENERATED_DIFFERS claim is not verified by this review, because running that check means reading `.claude/settings.json`.
  - **What should have happened:** each statement true of the head.
  - Ordinary work: yes, because it is the record the owner approves.
  - Consequence: other.

  **F7 (info, Wave 3 row): canaries with both kernel layouts.**
  - **What happened:** a project holding both layouts with different canary declarations uses the template's silently.
  - **What should have happened:** as with the check declarations (DEC-579), a difference is refused.
  - Ordinary work: no, because no project holds both with different canaries; this repository holds only the template layout.
  - Consequence: other.

- **What was sound:**
  - **The judge (no `PYTHONPATH` in the environment):**
    - Every declared check ran as `<pin>/bin/python -P …` with the installed package, including leading spaces.
    - A decoy `src/gov` and a root `gov/` were never imported; decoy `python3` and `gov` on `PATH` never ran.
    - The `gov` declaration ran through `-m gov.cli.main` and gave the pin's answer.
    - A check module new in the tree was RED with "No module named …", as CIT-P §5 says.
    - `gov ci` (the git pre-commit and pre-push gates) uses the same path.
    - DEC-732's per-command `PYTHONPATH` still chooses the code under test: the overlay was used by `/usr/bin/python3 -P -m gov.check.authority`.
  - **The hook lines:**
    - The pin was found through the link, and through `PATH` with `HOME` unset or elsewhere.
    - With no pin anywhere: preToolUse, postToolUse and postToolUseFailure exit 2; preCompact, sessionStart, stop and subagentStop exit 1.
    - A dangling link, an interpreter that is gone, an `env` first line, and an environment without the package each gave exit 2.
    - Pip's long-form script made `sh` stop on a syntax error, exit 2.
    - The rollback to an editable install is followed.
    - The after-call hook fails soft (exit 2, no restore) when its package cannot run.
    - `gov launch` recognises the guard in the new line for every matcher form.
    - W2-62's session-start hook runs under the new line: exit 0, injecting the checkpoint lines.
  - **Packaging, from the wheel:**
    - `retrieve_baseline.yaml` ships; it is the only non-Python file under `src/gov`.
    - Canaries are read from the project in both layouts; with none, FACET_UNAVAILABLE. No install-path decoy was read.
    - The retrieval check adopts each tier with the project's path map and gitleaks configuration, and runs without a traceback.
    - No other module finds repository files from its install path; every declared check reads the working folder.
  - **`gov --version`:** the wheel prints `gov 0.1.0 (commit unknown)`; the source tree prints `gov 0.1.0 (commit 9b9faac3…)` from any folder. Other forms (`--version --json`, `-V`) are usage errors, and the KPI asks no more.
  - **Commit `45c6bfae`:**
    - Role independent-test-designer; only the six named files changed.
    - W1-26: the raising plant gives RED with `DECISION_CHECKER_ERROR`, and the control plant gives GREEN. The plant is called from the declared check's own process, so the case cannot pass vacuously. Expectation unchanged (RED or YELLOW).
    - W1-22: assertions unchanged. The fixture gains the kernel's two declarations in the installed layout; `passed` needs every kernel query to hit.
  - **Roles:** every engineer commit is inside the allowed paths; none touches `tests/acceptance/`.
  - **CIT-P accurate on:**
    - +71/−21 in six files, and the lines it cites at `c5100159`;
    - W2-05 still at `f19f156e` with the same two conflicts and the stated resolution;
    - rows W2-M388, W2-M389, W2-M390 and W2-L371 as decided in DEC-864;
    - the exit code per event and the long-form risk;
    - A1's precondition (`98effadc` is in this branch) and the A1-then-A2 order.