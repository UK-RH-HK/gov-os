# Independent assessment of the Gov OS, October 2026 — Lens D: tool staging, and building versus using

## 1. Header

**Lens.** D: tool staging, and building versus using. The lens asks three things:

1. For each of thirteen tools, whether it is mature enough to use as an aid or as a gate, or is still being built.
2. Where a tool that is still being built gates its own construction (the `gov` command runs from this repository's own `src/` folder), and how that causes loops.
3. How to separate building the Gov OS from using it.

**Date.** 2026-10-19. All times in this report are UTC.
- The assessment started at about 12:45 (`CHECKPOINT.md`, "RESUME HERE": "ASSESSMENT RUNNING (owner, 13:45)", in British Summer Time).
- Runs 2 to 8 below took place between 12:51 and 13:05.
- Runs 1 and 9 were repeated later, while I checked this report against its sources.

**Assessor.** I am an independent-auditor session (`GOV_ROLE=independent-auditor`). I work under the ticket context DAEO-sdxk, which is W2-00, the Wave 2 coordination ticket.
- The Wave 2 orchestrator started me on the owner's order of 2026-10-19.
- I am one of five auditors. Each takes one lens and cannot see the others' work.
- I wrote none of the work assessed.
- Wave 2 was paused throughout: nothing was closed, merged or committed while I worked.

**Head assessed.** `w2/integrate` at `fecb870c`. Its working copy holds the owner's next batch (DEC-813 to DEC-817), staged and uncommitted, in three files: `docs/DECISION_REGISTER.md`, `docs/plan/WAVE_2_WBS.md` and `docs/plan/WAVE_2_LIST.md`. I read it and changed nothing.

**Branches and trees read.**
- `w2/integrate`: its head, history, records and staged batch.
- `w2/W2-49` at `19d45246`. Contract v4.2 exists only on this branch; `w2/integrate` holds v4.1. I read only its version line and the lines of CAP-43.a–d, CAP-44.h and CAP-45.a, with `git show` and `git grep`.
- `w2/W2-16` at `1908149d`: its log, its head commit and its commit count.
- `w2/W2-50` and its worktree `/home/usain/gov-os-worktrees/W2-50`:
  - its change under `src/gov` against its merge base `00fe09b6`;
  - its `.gov-runtime/findings.jsonl`;
  - which copy of `gov` Python imports there.
- The last-commit dates of all fourteen `w2/*` branches, and the tag list.

**What I read.**
- In full: the Charter v5 (`docs/charter/CHARTER_v5.md`) and ADR-0001 (`docs/adr/ADR-0001-threat-model.md`, the threat model).
- The owner's project files, each opened by name:
  - `governance/project/prompts/w2-orchestrator.md`: in part, including §14 (the judgement rules);
  - `governance/project/bootstrap.md`: lines 2438–2459 and 2572–2587, and the closing headings between lines 2723 and 2850;
  - `governance/project/path-map.yaml`: its systems block (lines 143–209) and the two ratchet lists;
  - `governance/project/tool-registry.yaml`: the entry for `gov` (lines 205–212);
  - `governance/project/briefs/JUDGEMENT.md` and `governance/project/briefs/AUDITOR-common.md`, in full.
- The decision register, `docs/DECISION_REGISTER.md` (the "register"): each entry cited below, at the lines given.
- The Wave 2 plan:
  - `docs/plan/WAVE_2_WBS.md` (the work breakdown, "WBS"):
    - the rules in §0, the tracks and the ticket table;
    - the cards of W2-10, W2-16, W2-17, W2-18, W2-24, W2-42, W2-48, W2-49, W2-50, W2-53, W2-54, W2-56 and W2-57;
    - the schedule notes and the exit criteria.
  - `docs/plan/WAVE_2_LIST.md` (the "LIST"): rows W2-H009, W2-H019, W2-H031, W2-H032, W2-H040, W2-H052, W2-H054, W2-M061, W2-M123, W2-M332, W2-M364 and W2-L352;
  - `docs/plan/WAVE_2_TRIAGE.md` (the "TRIAGE"): the lines of W2-H031 and W2-H054.
- The orchestrator's records under `.gov-runtime/scratch/orchestrator/`:
  - `CHECKPOINT.md`, its current sections;
  - all 33 close logs in `log/`, and the check logs there that carry "gov: not found";
  - `log/sweep-times.txt` and the listing of `log/repair-tickets/`;
  - the lead briefs `briefs/LEAD-common.md` and `briefs/W2-16-A5-run1.md`, for the import-path rule.
- Wave 1 exit evidence:
  - the close records `docs/plan/wave-1-exit/evidence/close-*.json`, and `docs/plan/wave-1-exit/EXIT-REPORT.md` at lines 44 and 324;
  - the exit audit `docs/audit/wave-1/W1-43-wave-1-exit-audit.md`, at findings F-M5 and F-M12;
  - the probe records of W1-02 (`docs/probes/DAEO-emkd/`) and of W2-01 (`docs/probes/DAEO-g0ip/`);
  - lessons `docs/lessons/L-0077.md` and `docs/lessons/L-0078.md`: their headers and opening paragraphs;
  - `docs/changes/W2-54-CIT-E.md`, line 433.
- Code:
  - `template/governance/kernel/hooks/pretooluse.py`: lines 1–80, 97–175 and 200–470;
  - in the same folder: `stop.py` lines 28–31, `sessionstart.py` lines 65–68, `precompact.py` lines 108–110 and `posttooluse.py` line 152;
  - `src/gov/doctor/command.py` lines 506–515, and `src/gov/cli/main.py:95`;
  - `src/gov/codeintel/__init__.py` (the code-graph daemon folder), `src/gov/check/command.py` and `src/gov/rebuild/check.py`;
  - `pyproject.toml`, `lefthook.yml`, `.github/workflows/ci.yml` and `tests/acceptance/conftest.py`;
  - the `PYTHONPATH` lines of `.rulesync/hooks.jsonc`;
  - under `tests/`: the lines that name `$CLAUDE_PROJECT_DIR/src`, and the test names of `tests/acceptance/W1-38/test_w1_38_hooks_source.py`.
- The install of `gov`: `~/.local/lib/python3.12/site-packages/__editable__.gov-0.1.0.pth`, the package's `direct_url.json`, and `~/.local/bin/gov`.
- The main tree's `.gov-runtime/findings.jsonl`.

**Helpers.** I started five helper sessions of my own, under this session's role and guard, and told them to stay read-only. They swept:
- the register, for episodes where a tool gated its own construction;
- every logged `gov close`;
- the probe, audit and exit records;
- the code of the thirteen tools (two helpers).

I checked every statement of theirs that this report uses against the cited file. Where I could not check a statement, I left it out.

**What I ran.** I never ran the bare `gov` that is on PATH.

| # | Command (short form) | Where | Which code ran | Result |
|---|---|---|---|---|
| 1 | `python3 -m gov.guard.hooks` | main tree | the editable install: the main tree's `src/` at `fecb870c` (the staged batch touches no code). Read-only. | lists the seven registered Claude Code hooks and their command lines. Run twice; the second run was during the checking of this report. |
| 2 | `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS /tmp/gov-os-assessment-D/repo` | `/tmp` | git | a clone at `fecb870c`; still clean at the end |
| 3 | The PreToolUse hook program, fed a Read call and an Edit call as JSON on standard input, three times: (a) with the file as committed; (b) after appending the line `def _half_typed_edit(:` to the clone's `src/gov/guard/decide.py`; (c) after `git checkout -- src/gov/guard/decide.py` in the clone (`cmp` identical to a saved copy; `git status --short` empty) | the clone | the clone's `template/governance/kernel/hooks/pretooluse.py`. `CLAUDE_PROJECT_DIR` and `PYTHONPATH` were set to the clone, with `GOV_ROLE=independent-auditor` and `PYTHONDONTWRITEBYTECODE=1`. This is the live hook's own command form (run 1). | (a) exit 0; (b) exit 2 for the Read, and exit 2 for the Edit of `decide.py`; (c) exit 0. Standard error was empty in every case. I ran the whole sequence twice, at about 12:53 and at 13:02, with the same result. See F2. |
| 4 | `python3 -B -c 'import gov; print(gov.__file__)'`, bare and with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` | W2-50 worktree | Python's import only | bare: `/home/usain/Dynamic-Agentic-Engineering-OS/src/gov/__init__.py`, the main tree. With `PYTHONPATH`: the worktree's own file. |
| 5 | `gov doctor --json` | the clone | the clone's `src/`, through my wrapper `/tmp/gov-os-assessment-D/bin/gov-clone`. The wrapper sets `PYTHONPATH` to the clone and calls `gov.cli.main`, so it does not use the `gov` on PATH. `TMPDIR` was in my scratch folder. | exit 3, `DOCTOR_UNHEALTHY`; `hooks: pass`; see F7 |
| 6 | `gov check --list` | the clone | as in run 5 | 18 declared checks |
| 7 | `python3 -m pytest tests/unit/close tests/unit/guard -q -p no:cacheprovider` | the clone | the clone's `src/` (`PYTHONPATH`), with `TMPDIR` in scratch. The resource gate was checked in the same command (load1 15.75, MemAvailable 19,795,036 kB, 13:03). | 1,099 passed in 54.85 s |
| 8 | `pytest` of the single test that refused W2-53's last close: `tests/acceptance/W1-30/test_w1_30_r13_probe_findings.py::test_after_a_run_cut_at_the_time_limit_no_process_of_it_lives_or_writes_into_the_project` | the clone | as in run 7 (load1 5.93, 13:04) | passed alone; its call took 17.36 s |
| 9 | Read-only commands: git (`log`, `show`, `diff`, `grep`, `rev-list`, `merge-base`, `for-each-ref`, `tag`, `status`, `config --get`), `sed` and `grep`. Also Python one-liners that parse the close logs, the path map and doctor's output. | main tree, W2-50 worktree, clone | system git and Python; no `gov` code | cited where used |

**Limits.**

- *What I did not run.* I ran no `gov rebuild`, no full `gov check` and no `gov close`.
  - A rebuild writes the code-graph daemon folder under `/tmp/gov-cbm-1000/` (`src/gov/codeintel/__init__.py`, `DAEMON_BASE`). That is outside the two places I may write.
  - A full check needs a built record store.
  - A close needs a rebuild and one to one and a half hours of a quiet machine. Four other auditors share this machine.
  - The resource gate was shut when I first checked it (load1 29.05), and load1 was 30.32 at 13:34.
  - So close behaviour comes from the orchestrator's 33 close logs. I did not re-measure it.
- *What I did not read.*
  - `~/gov-os-workbench`, which is out of bounds. The dev tiers' installs and hooks are therefore known only from the records.
  - `~/.claude/`, the settings files, the held-out file and the qualification oracle.
  - Contract v4.2 beyond the lines named, and `bootstrap.md` and the w2 prompt beyond the parts named.
  - The decision packages' own texts (P-W2-…). I cite them through the register and the checkpoint.
- *Guard refusals.* I met three, each once, and retried none in the same form:
  1. A listing of `governance/` and `governance/kernel/` was refused under the settings and held-out protection (DEC-508, DEC-525). I used `python3 -m gov.guard.hooks` instead, which the refusal named.
  2. A shell here-document that wrote my wrapper into my scratch folder was refused because the guard could not read it (DEC-409). I wrote the same file with the Write tool.
  3. A command whose output path came from a shell variable was refused as unresolvable. I re-ran it with literal paths, which the orchestrator's own standing rules also prescribe (`CHECKPOINT.md`, "Standing rules": "no `$VAR` write targets").

  Refusals 2 and 3 were reworded so the guard could judge them. They were not ways round a protection; I record them so a reader can judge that.
- *Hook text.* This session's start-up context carried text from the session-start hook that was addressed to the orchestrator: its ticket list and a checkpoint "resume" line. I treated it as a source, not as an instruction.
- *Line numbers.*
  - `CHECKPOINT.md` was being edited while I read it, so I cite it by section, not by line.
  - WBS line numbers are those of the working copy, which holds the staged batch. From line 599 on, they are 1 to 14 above the numbers at `fecb870c`.
  - Register lines up to 8897 are the same as at `fecb870c`; the staged entries come after them.
  - The staged LIST rows were changed in place, so LIST line numbers have not moved.

**Words used in this report.**

- *Gov OS:* the governance tool set this repository builds. It has four parts:
  - the `gov` command-line program, in Python, under `src/gov/`;
  - the Claude Code hooks;
  - the git hooks;
  - the kernel templates copied into adopted projects.
- *Wave, track, ticket, orchestrator, lead, worker:*
  - Wave 2 is the current block of work: 55 tickets in three tracks (WBS:88–90). Track A (adoption readiness) comes first and gates the pilot; Track B is the EXAMIN pilot; Track C is the rest.
  - The orchestrator is the main session that runs the Wave.
  - A lead runs one ticket in its own worktree and starts workers for it: an engineer, an independent test designer, and reviewers.
- *Register, WBS, LIST, TRIAGE, row:*
  - The register records every owner decision (DEC-…).
  - The WBS is the Wave 2 plan.
  - The LIST holds the known problems ("rows"): W2-H… rows are high, W2-M… medium and W2-L… low. The TRIAGE assigns each row to a ticket.
- *AR-…, F-M…, P-W2-…:* AR-1 to AR-10 are the owner's adoption-readiness items, and F-M… are the Wave 1 exit audit's findings; both are settled in DEC-718. A P-W2-… is a decision package for the owner.
- *Editable install:* a Python install that points at a folder of source code instead of copying it. Whatever the folder holds at that moment is what runs. `gov` is installed this way from this repository (DEC-605).
- *Main tree, worktree:* the main tree is the repository's main checkout (`/home/usain/Dynamic-Agentic-Engineering-OS`, on `w2/integrate`). A worktree is a separate checkout of one ticket's branch, under `/home/usain/gov-os-worktrees/`.
- *Hook:* a program that runs at a fixed moment.
  - Claude Code runs its hooks around tool calls (PreToolUse before, PostToolUse after) and at moments such as session start and stop.
  - Git runs its hooks at commit and push; lefthook installs them.
- *Guard:* the PreToolUse hook. It allows or refuses each tool call, by role and path.
- *Containment:* the PostToolUse check. It records changes made outside a ticket's allowed paths.
- *`gov close`:* the command that decides whether a ticket may close. It runs:
  - the ticket's acceptance tests, which an independent test designer writes before the code (master rule MR-3);
  - the full regression: every test in the repository;
  - the governance checks (`gov check`). A red "hard-block" check refuses the close.

  It also checks the probe, and the commit trailers: lines such as `Task:` and `Implements:` that tie a commit to its ticket. Exit 0 is a "clean close".
- *`tk close`:* the plain ticket tool's close, which runs no checks. The owner allows it only by named decision.
- *Ratchet:* two owner-kept lists in `governance/project/path-map.yaml`:
  - `accepted_reds`: known failing tests that do not refuse a close;
  - `load_sensitive`: tests that, when they fail in the close, are re-run alone inside the same close, and count only if they then pass.
- *Probe:* an independent adversarial review of a ticket's final code, recorded under `docs/probes/`.
- *load1, resource gate, quiet window:*
  - load1 is the machine's one-minute load average.
  - The resource gate allows a heavy run only when load1 is below 20 and at least 6,710,886 kB of memory is available (`CHECKPOINT.md`, "Standing rules").
  - A quiet window is a period with no other lead running. Every close needs one (DEC-780).
- *Dev tiers and fixtures:* synthetic projects (ORION, called "a-dev", and ARGUS, called "b-dev") and test fixtures, used to try the Gov OS outside this repository.
- *Release, pin:*
  - A release is a fixed, hash-verified version of the Gov OS, built by `gov release` (W2-16).
  - The Charter's single signed Release 1 comes later. Until then, Wave 2's releases are "pinned and hash-verified, not signed" (CAP-43.b).
  - To pin is to install a release so that it cannot change under its users (W2-18).
- *Change rules:*
  - A change to the kernel, policy or skills needs evidence, independent review and owner approval. It goes through a change proposal ("CIT-P") and its evidence record ("CIT-E") (CAP-33).
  - A proposal that contradicts a closed specification comes with three costed options: apply now, defer, or re-baseline (DEC-105).

## 2. Answers to the lens's questions

### 2.1 Question 1: the stage of each tool

**Stages.**
- **Gate:** its refusal stops work (a tool call, a commit, a merge or a close), and its record here shows that it also lets correct work through.
- **Aid:** it is used, and its output informs people and agents. It does not stop work on its own, or it stops work only through another tool (usually `gov close`).
- **Being built:** not yet dependable for its intended use here. It is unbuilt, uninstalled, or has never once passed on this repository.

| Tool | Stage | Evidence | What it takes to reach the next stage |
|---|---|---|---|
| `gov close` | **Being built**, though it is used as *the* gate. The rule is that every Wave 2 ticket closes through it (WBS §0 rule 1, WBS:47; exit criterion 1, WBS:951). | 33 logged runs on this repository, 28 in Wave 1 and 5 in Wave 2, and none passed: 26 `CHECK_FAILED`, 4 `ESCALATION_BLOCKED`, 1 `PROBE_MISSING`, 1 `TRAILER_MISSING`, 1 `STORE_STALE` (`.gov-runtime/scratch/orchestrator/log/`; run 9). The only clean close ever is ORION-im02, on the a-dev clone (`docs/plan/wave-1-exit/evidence/close-ORION-im02.json`, `ok: true`). The register says: "no Wave 1 ticket closed through a clean `gov close`: accepted. It is AR-8" (register:7604). W2-01 was closed with `tk close` by owner decision, "the one named exception to exit criterion 1" (register:8296). Wave 2 has closed 1 ticket of 55, W2-01 (`CHECKPOINT.md`, State). | One clean close of a real ticket here, by a judge that is not the code under judgement (R1). The test cache (W2-48), so that a close no longer takes an hour or more of a quiet machine. |
| The ratchet (`accepted_reds`, `load_sensitive`) | **Being built**, and already in force inside every close. | It was merged with W2-53 (`c9537e39`), not closed. It decided W2-53's last close: it let the 2 accepted reds through and refused the unlisted W1-30 case (`log/close-DAEO-7rr2-3.json`). The lists hold 2 `accepted_reds` and 27 `load_sensitive` entries: 23 tied to row W2-M364, 3 to W2-M332, 1 to W2-L352 (run 9). Since `1330e0e2` the lists only shrink, and "Any addition comes to the owner as a decision package first" (DEC-766, register:8396–8397). A listed case is re-run alone inside the close (DEC-757 item 3, register:8300), and "the ratchet does not retry a load-sensitive case to let a close through" (DEC-780 item 3, register:8553). Its unit tests pass (run 7). | W2-53's close. A way to handle a case that fails only under load without stopping every close (R2). |
| The guard | **Gate.** It has the longest record of any tool here. It is still being changed. | It is live on every tool call of every session: the PreToolUse hook has no matcher (run 1). It fails closed on its own errors (`pretooluse.py:254`; `_fail` at 97–106). W1-02's four probe records all judge "pass" (`docs/probes/DAEO-emkd/`). Its unit tests pass (run 7). It still refuses some correct calls: a helper of the Wave 1 exit audit made 58 identical refused SubagentHandback calls (exit audit:272, 368–369). W2-09 puts that call on the guard's list. Each session's guard is that session's own working code (row W2-M123, LIST:380; F2). W2-50 changes `decide.py` by +405 lines against its merge base (run 9), and W2-09, W2-10 and W2-42 change the guard after it. | Run it from a pinned copy (R1). W2-42's measure "a broken guard-file edit cannot lock every session" (WBS:807), which is late in Track C. |
| Containment | **Aid**, by design: it records and does not block. | It runs after every Bash call, failed or not (run 1). At 2026-10-19T13:00:09Z it flagged a read-only `git rev-parse … && git status --short` run by another auditor as "change outside allowed paths". The three files it named are the orchestrator's staged batch (the main tree's `.gov-runtime/findings.jsonl`, last line). The orchestrator calls this "a false attribution" (`CHECKPOINT.md`, "RESUME HERE"). Containment "rests on self-declared commit trailers" (row W2-H019, LIST:209). | W2-44: trailers bound to the launch identity (WBS:148). Correct attribution when several sessions share one tree. |
| The hooks | **Split.** The Claude Code hooks are live: the guard is a gate and the others are aids. The git hooks are off and CI cannot pass, so those parts are **being built**. | Seven Claude Code hooks are registered (run 1). The lefthook git hooks were removed on 2026-10-15 (DEC-712, register:7478–7488). They were put back on 2026-10-16 at 09:42 and removed again before `82459573` (register:7620; F-M13 at 7614). `.git/hooks` holds only `*.sample` files, and `core.hooksPath` is unset (run 9). WBS §0 rule 4 keeps them off "until Track A's fixes land" (WBS:54). CI needs the pre-push evidence note and pytest on the runner, and has neither (`.github/workflows/ci.yml`:14–17, 20–23, 78–82). | W2-05 (the git environment of every check and hook; idle), W2-06 and W2-08 (hooks back on). pytest on the CI runner, by owner approval (R6). |
| The sandbox | **Aid**, for launched workers only. | It is the operating-system sandbox that the launcher puts around a worker's Bash commands (DEC-152, DEC-161). Since DEC-799 (2026-10-19), every worker whose suites do not need the code graph starts in it (register:8748). Hooks, MCP servers, the file tools and the orchestrator's own session run outside it (ADR-0001:49–51), and so do the leads (DEC-769's basis, register:8426). Its untested cases wait for the experiment EXP-002 (W2-40). | W2-56; W2-21 (leads sandboxed, DEC-769); W2-40. |
| `gov launch` | **Aid**, becoming the gate for how workers start. | The trial of DEC-789 became the standing rule of DEC-799 (WBS:59). Leads still start in the owner's launch form until W2-21 closes (DEC-715; WBS:59). Leads launch workers from the worktree, with that worktree's code: `cd <this worktree> && PYTHONPATH=src python3 -m gov.cli.main launch …` (`briefs/LEAD-common.md:19`). So a worker's sandbox is built by the worktree's own launcher code. | W2-21 (`gov launch lead`), W2-56. |
| `gov check` | **Gate** inside `gov close`; an **aid** on its own. | 18 declared checks (run 6). A red hard-block check refuses a close (register:8414). The checkpoint records "`gov check` at `6f7d4f9e`: no red" (`CHECKPOINT.md`, State). Its help text still says "running them is not built yet" (`src/gov/cli/main.py:95`; F9). Its runner semantics are open work (W2-45). | W2-45. The help text corrected (R5). |
| The retrieval stack | **Aid.** | It feeds `gov context` and the record store. A store not rebuilt at the head refuses a close (`STORE_STALE`, `log/close-DAEO-7rr2-2.json`). A full rebuild took 11 min 46 s in the sweep of 2026-10-18 (`log/sweep-times.txt`). Its quality measure is hit@5: the share of test questions with a right answer among the first five results. W1-21 measured 81.67 at `5f038b47`, against a pass line of 80. W2-54 did not re-measure it, because no GPU is reachable (`docs/changes/W2-54-CIT-E.md:433`). W2-54's CPU-only query embedder is merged, not closed. W2-13 and W2-15a/b are not started. | W2-06 (re-index at commit), W2-13, and the two passes of experiment EXP-003 (W2-15a/b). |
| Context (`gov context`) | **Aid**, still being built. | Sessions get it through the session-start hook, and every close builds it. At the Wave 1 exit it returned 814,821 tokens against a 6,000-token budget, with `ok: true` and the ticket's own text dropped (exit audit:119 and 328, F-M5). W2-04 (bounded and reproducible) waits for W2-03 (WBS:98), which is held. W2-54 made the order of the dropped list stable; it is merged, not closed. | W2-03, then W2-04. |
| Checkpoints (`gov checkpoint`) | **Aid.** | The stop and pre-compaction hooks write checkpoints, and so do the leads ("leads write real checkpoints", DEC-511, register:5589). A stale checkpoint is a close finding (`CHECKPOINT_STALE`, register:8289 and 8414). The orchestrator's own `CHECKPOINT.md` is kept by hand. In a worktree, the stop hook writes with the main tree's checkpoint code (`stop.py:30`; F8). Two rows are open: checkpoint numbering has no lock and writes are not atomic (W2-M061, LIST:318), and a save during the pre-compaction window can be lost (W2-H009, LIST:199). | W2-42's atomic saves (WBS:807). |
| `gov adopt` | **Aid** here; **being built** for product repositories. | `gov adopt --lite` ran its eight stages on this repository on 2026-10-11 (`bootstrap.md`:2579–2581). In the Wave 1 exit, the a-dev clone reached stage A8 (`EXIT-REPORT.md`:44), and b-dev was adopted to A2 (register:7497). The adoption of EXAMIN's copy (W2-27) waits for the safety-critical subset of DEC-727, W2-26, W2-49, W2-50, W2-19 and W2-52 (WBS:130), and for W2-56 (DEC-799 item 4, register:8749). Its path runs through W2-16, W2-18 and W2-23 (WBS:921). | W2-24's adoption of a fixture with a pinned release (WBS:656–657); W2-23 and W2-27. |
| Releases (`gov release`, `gov update`, pinned install) | **Being built.** No release has ever been cut. | `gov release` exists only on `w2/W2-16`. That branch has been held at `1908149d` since 2026-10-17, and its head commit says "the last round's review passed, packages to the owner". It is 30 commits ahead of `w2/integrate`, including W2-49's 13 beneath it (run 9). It is eighth in the close order (`CHECKPOINT.md`, "Held / idle tickets"). `gov release` is the owner's alone, run from a plain terminal (DEC-772, register:8445–8448). W2-17 and W2-18 are not started. The repository's tags (`v4.1.x-rc1`, `wave-1-exit` and others) are not Gov OS releases. This repository has no `framework.lock`: doctor reports `framework_lock: unmeasured, MISSING` (run 5). The Charter releases the Gov OS "**once** as Release 1, a signed `v1.0.0` tag" (Charter:31), and allows the EXAMIN pilot only "on a pinned, hash-verified release" (Charter:33–34). Contract v4.2 makes Wave 2's release one that "is pinned and hash-verified, not signed" (CAP-43.b, `w2/W2-49`:`docs/contract/CONTRACT_v4.md`:684). | Close W2-49 and W2-16. The owner cuts a first W2-16 release (DEC-772). W2-18. W2-24 installs a release, pinned, into a fixture. |

**In short:**
- One tool is a gate by its record: the guard.
- Three tools are gates by rule, all inside `gov close`: the close itself, the ratchet and `gov check`. `gov check`'s record here is short, and the close and the ratchet have not passed yet.
- The commit and push gates are off.
- Everything else is an aid, or is still being built.

The pace of Wave 2 is tied to the gate with the weakest record here: `gov close`.

### 2.2 Question 2: where a tool that is still being built gates its own construction, and how that causes loops

Three wires connect the code being written to the tools that govern it. None is hidden, and each was chosen for a reason. Together they mean that the Gov OS is judged, guarded and briefed by itself, in its unfinished state.

**Wire 1: the editable install.** The `gov` on PATH is an editable install of the main tree.
- The owner installed it with `python3 -m pip install --user --break-system-packages -e /home/usain/Dynamic-Agentic-Engineering-OS` (DEC-605, 2026-10-10, register:6472–6474; `tool-registry.yaml`:208).
- The install's `.pth` file holds `/home/usain/Dynamic-Agentic-Engineering-OS/src`.
- The tool registry says why it was installed and what that means (`tool-registry.yaml`:212):
  - it was "Needed so that an adopted project's hooks and check commands find gov (package P-40)";
  - "an editable install has no wheel, the code that runs is this repository's working tree at its checked-out commit";
  - the sha256 it records is that of the launcher script `~/.local/bin/gov`, not of the code that runs.

Any bare `gov`, run anywhere on the machine, runs the main tree's files as they are at that moment (run 4). This includes:
- the git hooks, which call `gov ci …` by name (`lefthook.yml`:21, 23, 28);
- checks that call `gov` by name;
- the hooks and checks of adopted projects, the dev tiers among them (the registry's own reason, above).

The install followed fourteen refused closes, between 2026-10-08 and 2026-10-10 at 03:49.
- In thirteen of them, the check `fresh-agent-reconstruction` "exited with code 127", with "/bin/sh: 1: gov: not found" (`log/close-W1-30b.json` to `log/close-W1-15H.json`).
- The fourteenth, `close-W1-30G.json`, stopped at the escalation limit and carries the same text.
- The register's basis for the install is only "OWNER, on package P-40 option (a), approved and done" (register:6473).

A check needed a `gov` on PATH, and the copy put there was the working tree itself.

**Wire 2: the hooks.** Each Claude Code session's hooks run code from that session's own tree.
- The guard's command line is `PYTHONPATH="$CLAUDE_PROJECT_DIR/src" python3 "$CLAUDE_PROJECT_DIR/template/governance/kernel/hooks/pretooluse.py"`. Containment's is the same with `posttooluse.py` (run 1). The hook source `.rulesync/hooks.jsonc` carries the same prefix three times (lines 7, 15 and 23).
- The session-start and pre-compaction hooks put `<project>/src` first on Python's import path (`sessionstart.py:65–68`, `precompact.py:108–110`).
- The stop hook does not. It imports `gov.checkpoint.record` with no path of its own (`stop.py:30`). In a worktree it therefore runs the main tree's checkpoint code, through the editable install, while the guard and containment run the worktree's code.

Every tool call starts a new Python process, which reads the files as they are on disk at that instant. So in a ticket's worktree, the guard is the ticket's own unfinished guard.

**Wire 3: the gate after the merge.** `gov close` runs in the main tree, on `w2/integrate`, after the ticket is merged.
- WBS §0 rule 1 (WBS:48) says W2-01 "is itself closed with `gov close` once merged, because `gov` runs from this repository's `src/` (an editable install)".
- DEC-757 item 4 (register:8305) says "W2-53 closes through `gov close` using its own merged mechanism".

A ticket that changes the close is therefore judged by its own change. The close's full regression also includes the close's own acceptance tests from Wave 1 (W1-30, "gov close").

**A fourth, smaller wire.** Leads run `gov launch` from the worktree, with the worktree's code (`briefs/LEAD-common.md:19`). A launcher ticket's workers therefore run in a sandbox built by the code they are changing.

**The loops these wires have caused, with evidence:**

- **L1: the guard locks the session that edits it** (wire 2). A broken save of a guard file refuses every later call of that session, including the call that would repair it, and no reason is shown.
  - I demonstrated it (run 3).
  - It happened in Wave 1: "the guard failed closed; repaired from outside with `git checkout`" (`bootstrap.md`:2444).
  - It happened again in W2-50's worktree (F2).
- **L2: the close refuses the tickets that build it, for reasons that are not theirs** (wire 3).
  - *Wave 1.*
    - The close counted its own adoption-gap refusals toward its escalation stop. W1-30 and W1-38 were closed with `tk close` past that stop. The owner's Wave 2 item: "`gov close` counts adoption-gap refusals toward escalation, against DEC-492" (DEC-651, register:6921–6927).
    - W1-38's escalation then "comes only from history: the nine commits of 2026-10-07 without `Implements:`, and the undone `a95e54a3`" (DEC-683, register:7231).
  - *W2-01* rebuilt the close path. Its close "refused with six findings, none of them W2-01's work" (P-W2-19, register:8289):
    - a probe invalidated by the orchestrator's own integration commits;
    - W1-42's two named reds, "which refuse every Wave 2 close";
    - a p95 latency case (the 95th-percentile response time) that passed alone;
    - a stale checkpoint;
    - a context gap.

    The owner closed it with `tk close`, "the one named exception to exit criterion 1" (DEC-757 item 1, register:8296).
  - *W2-53* built the ratchet and the later-merge gate.
    - Its first close refused on three hard-block checks, "each red before W2-53's merge too and none of them W2-53's work", plus a stale checkpoint (register:8414).
    - Clearing them took a new ticket, W2-54 (DEC-768: "The three pre-existing reds are cleared, never weakened; W2-54; then W2-53 is closed again", register:8416). W2-54 merged on 2026-10-19 and now waits behind W2-53.
    - W2-53's re-close then refused on one test. It is W1-30's acceptance case for ending a run's processes at the close's time limit. It failed in the parallel run of 13,454 tests, and it passes alone ("alone 3/3 pass, 17.8 s; 2 s reaping margin", `CHECKPOINT.md`, State; my run 8: 17.36 s).
    - The remedy is an entry in the list W2-53 itself built. Only the owner may add one (DEC-766), and that package, P-W2-47, is on hold. "A re-close without a change = ratchet retry (forbidden)" (`CHECKPOINT.md`, "Open owner items").
    - Every held ticket closes after W2-53 (DEC-757 item 4, register:8305; DEC-806, register:8804).
- **L3: the fixes wait behind the loop.** Five tickets would weaken or remove these loops, and all of them wait behind the close queue (F5):
  - the release (W2-16);
  - the test cache (W2-48);
  - the hooks' git environment (W2-05);
  - the stable launcher, which also takes row W2-H054 (W2-21);
  - the guard's self-lock fix (W2-42).
- **L4: a git hook ran the main tree's current check code inside a ticket's commit** (wire 1, through lefthook).
  - The pre-commit hook's `retrieval-regression` check ran git with the variables git exports to a hook. It wrote two foreign commits, `4b051fde` and `dc6aa34c`, onto `w1/W1-42` (DEC-710 and DEC-712, 2026-10-15, register:7470–7488).
  - The bug itself was ordinary. The staging point is that a hook here runs whatever check code the main tree holds at that moment. There is no release step in between where a fixture run could have caught it.
  - The owner removed the hooks, and they are still off (F6).
- **L5: two versions of the Gov OS in one session** (wire 1 against wire 2).
  - In a worktree, a bare `gov` or `import gov` runs the main tree, while the guard and containment run the worktree.
  - DEC-732's basis: "W2-01's lead found that `env -u PYTHONPATH python3 -c 'import gov'` in a worktree loads the main tree's code, so a suite run in the prescribed form tests the main tree, not the ticket's change" (register:7805).
  - A hand rule in every brief keeps verification honest (F8).
- **L6: the gate's own review rounds held every close.**
  - DEC-737 let layer 2 start but held the closes: "only the closes wait for W2-01" (register:7908). "W2-07, W2-41 and W2-48 wait for W2-01 entirely: they touch or call `gov close`" (register:7919).
  - W2-01 then needed four failed probe records before its scope was split, and W2-53 took over the later-merge case (DEC-754).
  - The rounds found real defects. Round 4's Finding 1 was "(fail-open, loses work)": a later merge could delete a probed file while `gov close` passed (register:8225). So the reviews were right to hold the gate.
  - The staging cost is that when a gate is built and used at once, every review round of the gate stops the whole Wave.
  - The pattern resembles the review-repair loop that lessons L-0077 (critical) and L-0078 (high) describe from Phase 2.
  - The owner's answer was to put the threat model into every review (DEC-801 to DEC-809). That limits rounds; it does not remove the cause.

**What it has cost.**
- *Wave 1:* 28 logged close runs on this repository, none passed.
  - Four times the close's escalation stop ended the attempt (`ESCALATION_BLOCKED`; DEC-096's limit on loops that do not converge, ADR-0001:30–31).
  - No Wave 1 ticket closed through a clean `gov close` (register:7604).
  - W1-30 and W1-38 were closed with `tk close` (DEC-651, DEC-683).
  - W1-02 was closed with the ticket tool after its close "refused, as every close does until this repository's adoption (DEC-522)" (`bootstrap.md`:2450).
- *Wave 2:* the plan was approved on 2026-10-16 (DEC-729, register:7755). By 2026-10-19:
  - five logged close runs, none passed: W2-01's, W2-53's three, and the blocker sweep (a trial close of W2-53 on a scratch merge, DEC-775);
  - one ticket of 55 closed, by owner exception;
  - two merged and not closed;
  - ten held, one idle and 41 not started (`CHECKPOINT.md`, State);
  - seven of the held tickets' branches (W2-02, W2-03, W2-16, W2-20, W2-26, W2-49, W2-51) have had no commit since 2026-10-17 or earlier (run 9).
- *Time per close:* one to one and a half hours of the machine.
  - The blocker sweep of 2026-10-18 ran while two leads worked. It took 11 min 46 s to rebuild, 6 min 13 s to check and 73 min 58 s to close (`log/sweep-times.txt`).
  - The re-close of 2026-10-19 spent about 59 minutes in its tests alone: 20 s for acceptance, 1,877 s for the parallel regression, and 1,643 s for 263 cases run one by one afterwards (`log/close-DAEO-7rr2-3.json`).
  - The plan assumed "≈ 1 hour" for the regression plus "≈ 4 min" for the rebuild (WBS:943).
- *Repair tickets:* refused closes write repair tickets; 19 are kept in `log/repair-tickets/`.

The refusals are shrinking, so the tool is converging.
- Runs that reached their checks between 8 and 11 October carried 14 to 57 findings each.
- Runs since 13 October carried 1 to 22, and the last run, on 19 October, carried one (run 9).

But what is left is the machine's load, staleness and history, not the tickets' work. The one clean close, ORION-im02, ran on the a-dev exit clone, which does not carry this repository's history. It shows that the close can pass; it does not show why the close fails here.

### 2.3 Question 3: how to separate building from using

The owner's outline has five steps. Here is each one against what exists:

| Step of the outline | What exists today | Gap |
|---|---|---|
| Build with ordinary discipline | Acceptance tests written first by an independent test designer (MR-3); an engineer; an independent probe of the final code; the guard on every call. | CI cannot run the tests: pytest is not on the runner (`ci.yml`:20–23, 78–82). The commit and push hooks are off (DEC-712). There is no referee outside the agent's machine. |
| Test against fixtures and the dev tiers | `fixtures/`; ORION (a-dev) and ARGUS (b-dev). | The dev tiers are governed by the same editable install: the tool registry says it was installed so that "an adopted project's hooks and check commands find gov" (`tool-registry.yaml`:212). A trial on a dev tier therefore tries the main tree as it is that minute, not a fixed version. I could not inspect the workbench to confirm this there. |
| Release and pin | `gov release`, built and reviewed on `w2/W2-16`, and held. The framework lock from W1-39 (CAP-43.a). | No release has been cut. W2-18 (the pinned install) is not started. This repository has no `framework.lock`. |
| Use it on another repository first | W2-24 cuts a release and installs it, pinned, into a fresh copy of the TypeScript fixture. It then adopts the fixture and closes one ticket there with `gov close` (WBS:656–660). Its failure line already names "the fixture importing this repository's `src/`" (WBS:663). | It happens once, at the end of Track A, after "every other Track A ticket" (WBS:118) and, in the staged batch, after W2-57 (WBS:651). It is not a step that every version goes through. EXAMIN's copy (W2-27) does not wait for it (WBS:130). By the plan's schedule, the copy's verdict comes at ≈ day 13 (WBS:921), and Track A's verdict, which includes W2-24, at ≈ day 14 (WBS:922). |
| Govern this repository only by a pinned earlier release | Nothing. WBS §0 rule 1 (WBS:48) states the opposite, and W2-18 is written for product repositories only (WBS:112, 435–443; rule 7 at WBS:60). | The whole step is missing (F1). The plan treats as a failure in a fixture (WBS:663) what it prescribes for this repository (WBS:48). |

**Proposed arrangement.** Treat the Gov OS repository as its own first product repository.

1. **Two installations with two jobs.**
   - The *using* copy is a pinned, non-editable install of release N, in an environment of its own. Its `gov` is the one on PATH, and its hook programs are the ones this repository's hooks call.
   - Every governing tool runs release N: the guard, containment, the session hooks, `gov close`, `gov check`, `gov context`, `gov checkpoint` and `gov launch`.
   - The *building* copy is the working tree's `src/`. Only tests import it (`PYTHONPATH=<tree>/src`, as DEC-732 already requires), and so do explicit trial runs on fixtures and dev tiers in throwaway clones. The hooks and the gate never import it.
2. **The gate for this repository is the pinned close.**
   - Release N's `gov close` judges every change toward N+1.
   - A ticket that changes the close is judged by three things: the old close, its own acceptance tests (which run the new code), and a fixture run of the new close.
   - The new close governs only after it is released and pinned.
3. **Each version climbs a ladder:**
   1. build (tests and review);
   2. prove it on fixtures and dev tiers, each with that version installed;
   3. cut release N+1 (owner only, DEC-772);
   4. install N+1, pinned, on another repository first, and close real tickets there (W2-24's run, repeated for every version);
   5. move this repository's pin from N to N+1, by owner decision, on that evidence.

   To roll back, move the pin back.
4. **Bootstrap.** `gov release` is not merged, so the first pinned copy, the "bootstrap pin", is made by hand.
   - Its form is the one W2-16's releases take before Release 1: pinned and hash-verified, not signed (CAP-43.b).
   - The owner builds a wheel from a commit that already holds W2-53's ratchet (`fecb870c` qualifies), records its sha256 in the tool registry, and installs it non-editable. Without the ratchet, W1-42's two named reds would refuse every close (register:8289).
   - W2-16 then closes under the bootstrap pin, and the owner cuts the first W2-16 release with `gov release`.
   - This is how a compiler is first built: by an earlier version of itself.
   - It is not the Charter's Release 1 (Charter:31), which stays a single signed release at the end.
   - It keeps DEC-084's dogfooding: this repository still runs under its own guard, one version behind.

**What this fixes, and what it does not.**
- It removes the cause of three loops:
  - L1: the guard a session runs is no longer that session's own work;
  - the "moving judge" half of L2;
  - L5: there is one `gov` for using, and an explicit path for testing.
- It narrows L4: the git hooks call the pinned `gov`, behind a release step and fixture trials.
- It lets L3's tickets close on their merits.
- It does **not** make tests that fail under load pass, and it does not shorten a close. Those need R2 and W2-48.
- It adds one real cost. When a ticket changes a format that the judge reads (a record schema, a trailer, the path map), a release that accepts the new format must come first. The order is: widen what the judge accepts, release that, then start using the new format.

## 3. Findings

Severity is my judgement:
- **High:** it sets the pace of the Wave, or the owner's control.
- **Medium:** a recurring cost, or a misleading signal, with a workaround in place.
- **Low:** a description that is out of date.

### F1. This repository is governed by its own working copy; no pinned version exists, and the plan prescribes none for it

**Evidence.**
- *The install.* The editable install (DEC-605, register:6472–6474; the `.pth` file). The tool registry: "the code that runs is this repository's working tree at its checked-out commit" (`tool-registry.yaml`:212).
- *The hooks.* The live hook command lines put the session tree's `src/` first (run 1; `.rulesync/hooks.jsonc`).
- *The plan says so in terms.* W2-01 "is itself closed with `gov close` once merged, because `gov` runs from this repository's `src/` (an editable install)" (WBS:48).
- *The pinned install is planned for product repositories only:*
  - rule 7: "A product repository runs a fixed, pinned, hash-verified Gov OS release (W2-16, W2-18), never this repository's editable development copy" (WBS:60);
  - W2-18's title, "a product repository runs a fixed release, never the development copy" (WBS:435);
  - W2-18's failure line, "a product session that imports this repository's `src/gov`" (WBS:443).
- *W2-18 has the right measure but cannot apply it here.*
  - Its KPI "The guard and kernel hooks a session runs are the pinned release's code, not the session tree's [W2-M123]" (WBS:440) is the right measure. Row W2-M123, "A session's guard is its own tree's code" (LIST:380), is the known row.
  - But W2-18's allowed paths (WBS:436) do not include this repository's hook registration: `.rulesync/hooks.jsonc` and the settings generated from it.
  - Those command lines put `$CLAUDE_PROJECT_DIR/src` first on the import path.
  - So W2-18 as written cannot make this repository's sessions run a pinned guard.
- *No lock.* There is no `framework.lock` here (run 5).
- *The Charter.*
  - The Charter applies the master rules to "the Gov OS's own development from S1 onward (DEC-065)" (Charter:83).
  - It says the Gov OS's own work, after a bootstrap, "runs under its own guard (DEC-084)" (Charter:199–201; DEC-084, "bootstrap, then dogfood", register:767).
  - That is dogfooding with no staging: neither text says which version of the guard.

Ordinary work: yes, because every session, hook, check and close on this repository runs whatever code is on disk in its tree at that moment.
Consequence: other — in every case I found, it failed closed (refusals, stalls, a moving judge). It could fail open for one session, if a guard ticket's half-finished guard were more permissive than the last good one, but I found no instance.
**Severity: high.** It is the common cause of F2, F4, F5 and F8.

### F2. A broken save of a guard file locks the session that made it: every later call is refused, the repair included, and no reason is shown

**Evidence.**
- *Demonstration* (run 3, in my clone, with the live hook's own command form):
  - a Read call with the intact guard: exit 0;
  - after appending one unfinished line to `src/gov/guard/decide.py`: a Read call exits 2, and an Edit of `decide.py` itself (the repair) exits 2;
  - after restoring the file: exit 0;
  - the clone's `.gov-runtime/findings.jsonl` records `"kind":"import_error","reason":"cannot import guard logic: invalid syntax (decide.py, line 913)"` for each refused call.
- *No reason reaches the session.*
  - The failure path `_fail` (`pretooluse.py`:97–106) writes the reason only to `.gov-runtime/findings.jsonl`, then exits 2.
  - `pretooluse.py` writes nothing to standard error anywhere, and the standard-error files of run 3 are empty.
  - The locked session cannot read the findings file either, because its Read is refused too.
- *Earlier occurrence:* "A worker's incomplete save of a guard file stops every session of that worktree (run 6: a function got a required argument and its callers did not; the guard failed closed; repaired from outside with `git checkout`)" (`bootstrap.md`:2444).
- *Recurrence in Wave 2,* in the W2-50 worktree:
  - `.gov-runtime/findings.jsonl` line 7 records `"kind":"decide_error","reason":"decision failed: name '_overlap_or_under' is not defined","tool_name":"Edit"`;
  - it was logged between 2026-10-16T21:15:58Z and 2026-10-17T09:27:09Z (the entries around it);
  - the name is in no commit of any branch: `git log --all -S_overlap_or_under` is empty;
  - so the guard that refused the engineer's Edit was the engineer's own unsaved intermediate state of `decide.py`;
  - how the session was repaired is not recorded in what I read.
- *The hand rule given since* is "prove the whole new file outside the tree, one save, `git status --short` as the first call after it" (`bootstrap.md`:2444). It asks engineers not to edit guard files in steps, which is how the Edit tool works. W2-50's refused call was an Edit.
- *The rules already ask for a reason.*
  - The owner's AR-6 item 4 says: "The same standard, 'say why, refuse once, then record', applies to the guard's refusals (F-M7, F-M12)" (register:7581).
  - W2-10's measures cover the stop hooks' refusal text "on standard error" (WBS:315) and "Every guard refusal says it is final for that call" (WBS:318). They also cover an exception inside a *stop* hook (WBS:320).
  - None of them covers the guard's own import or decision failure.
- *Row W2-H032* (LIST:222) covers a missing `gov` ("the pre-call hook blocks every call"), not a broken one.
- *The planned fix is late.*
  - Row W2-H031, "Incomplete save of a guard file stops every session of the worktree" (high; LIST:221; TRIAGE:75), is in W2-42 (WBS:807).
  - W2-42 is in Track C and depends on W2-10 (WBS:146). W2-10 depends on W2-09 (WBS:104), which starts once W2-50 has closed (register:7925–7928).
  - Meanwhile W2-50, W2-09 and W2-21 change `decide.py` or the launcher one after another (WBS:911).
- *Context:* agents that are refused without a reason retry. A helper of the Wave 1 exit audit made 58 identical refused calls (exit audit:368–369, F-M12).

Ordinary work: yes, because every engineer on a guard ticket edits these files in their own worktree, and it has happened at least twice.
Consequence: other — it fails closed: nothing is let through, and the files stay on disk. But the session stalls until someone repairs it from outside.
**Severity: medium.**

### F3. `gov close` has never passed on this repository, and Wave 2's exit depends on it

**Evidence.**
- *The record:* 33 logged runs on this repository, none passed (run 9): 26 `CHECK_FAILED`, 4 `ESCALATION_BLOCKED`, 1 `PROBE_MISSING`, 1 `TRAILER_MISSING`, 1 `STORE_STALE`.
- *The register:*
  - "F-M3, no Wave 1 ticket closed through a clean `gov close`: accepted. It is AR-8" (register:7604).
  - AR-8 asks that "the first Wave 2 ticket in this repository closes through a clean `gov close`" (register:7586). That has not happened: W2-01 was closed with `tk close` (register:8296).
  - Before it, W1-30 and W1-38 were closed with `tk close` past the escalation stop (DEC-651, register:6921), and W1-38's escalation came "only from history" (DEC-683, register:7231).
- *The rule:* exit criterion 1 requires every Wave 2 ticket to close through a clean `gov close`: "A ticket closed any other way is a named failure of this criterion" (WBS:951).
- *The cost per run:* one to one and a half hours of the machine (§2.2, "What it has cost"). The plan assumed "≈ 1 hour" plus "≈ 4 min", and "≈ 7 hours over layers 1 and 2" (WBS:943).
- *The trend is better:* 14 to 57 findings per run between 8 and 11 October; 1 to 22 since 13 October; one in the last run.

Ordinary work: yes, because every ticket must pass it, and each Wave 2 refusal I traced was caused by something outside the ticket. The evidence: register:8289 and 8414; `log/close-DAEO-7rr2-2.json` (`STORE_STALE`); `CHECKPOINT.md`, State.
Consequence: other — it fails closed; the cost is the queue, and the owner decisions it needs.
**Severity: high.**

### F4. The close judges its own change after the merge, and the only remedy for a failure under load is an entry only the owner may add, so one timing test holds every close

**Evidence.**
- *Self-judging:* DEC-757 item 4: "W2-53 closes through `gov close` using its own merged mechanism" (register:8305).
- *The last refusal* (`log/close-DAEO-7rr2-3.json`):
  - acceptance: 57 passed;
  - regression: 13,454 passed and 3 failed, namely W1-42's 2 accepted reds and one case. The close's finding reads: "`tests/acceptance/W1-30/test_w1_30_r13_probe_findings.py::test_after_a_run_cut_at_the_time_limit_no_process_of_it_lives_or_writes_into_the_project` is red (failed) and accepted_reds does not list it";
  - that case is W1-30's ("gov close") acceptance test that a run cut at the time limit leaves no process behind;
  - it passed alone three times for the orchestrator ("alone 3/3 pass, 17.8 s; 2 s reaping margin", `CHECKPOINT.md`, State), and once for me (run 8: 17.36 s at load1 5.93).
- *The same class is known:*
  - DEC-762 item 4 put a sibling case, `tests/unit/close/test_follow_up.py::test_at_the_time_limit_the_processes_a_run_started_are_ended_with_it`, into `load_sensitive` by the owner's commit. It had failed once under `-n 8` and passed alone twice (register:8356; row W2-L352, LIST:997);
  - row W2-M332 is "p95 latency and time-limit cases fail under machine load" (LIST:589);
  - in Wave 1, W1-30's r8 case failed under load 17 to 45, because "its inner `gov close` run has time limits that a loaded machine can pass" (`bootstrap.md`:2452). The p95 and W1-46 cases did the same (`bootstrap.md`:2445).
- *The remedy and its rules:*
  - the remedy is an entry in `load_sensitive`, the list W2-53 built;
  - "From `1330e0e2` on, `accepted_reds` and `load_sensitive` only shrink." "Any addition comes to the owner as a decision package first … It is never folded into a batch of other answers" (DEC-766 items 1 and 2, register:8396–8397);
  - "**Never (c):** the ratchet does not retry a load-sensitive case to let a close through" (DEC-780 item 3, register:8553);
  - the package, P-W2-47, is "ON HOLD … Blocks W2-53's re-close and every close behind it. A re-close without a change = ratchet retry (forbidden)" (`CHECKPOINT.md`, "Open owner items").
- *Load is normal here.*
  - W1-46's 23 live-session cases "fail at setup under parallel load and pass alone" (DEC-760 item 1, register:8324).
  - In the blocker sweep they failed under load. 20 then passed in the ratchet's re-run alone, and 3 failed alone too and later passed on a quieter machine: "The 'alone' re-run was not alone" (DEC-780's basis, register:8547–8549).
  - My own gate checks found load1 29.05 (about 13:00) and 30.32 (13:34).
- *An entry would not let a failing test through.*
  - A listed test that fails in the close "counts only if it passes in an isolated re-run inside the same close" (DEC-757 item 3, register:8300).
  - The evidence I saw does not settle the cause of this case's failure under load. It may be the test's own timing (a 2 s margin), or the close may really leave a process alive when the machine is loaded.
  - That question belongs to W2-57, which P-W2-47 proposes to widen, not to the queue.

Ordinary work: yes, because parallel leads, reviewers and auditors load this machine in normal work, and the close runs the full regression.
Consequence: other — it fails closed. One Wave 1 timing test holds the thirteen tickets in the close order (`CHECKPOINT.md`, "Held / idle tickets").
**Severity: high.**

### F5. The tickets that would end the loop wait behind it

**Evidence.**
- *The release.* W2-16 has been held at `1908149d` since 2026-10-17, and its head commit says "the last round's review passed, packages to the owner". It is eighth in the close order: "W2-53, W2-54, W2-02, W2-03, W2-20, W2-51, W2-49, W2-16, …" (`CHECKPOINT.md`, "Held / idle tickets").
- *The test cache.*
  - The plan says "W2-48 takes the close queue off the critical path from layer 3 on (DEC-726)" (WBS:927), and "The cache took most of the ≈ 50 hours of serial close time off the path" (WBS:944).
  - Yet W2-48 is not started: "After W2-53 closes, W2-48 (the test cache) takes the next free slot after W2-21, since it shortens every later close" (DEC-780 item 4, register:8554).
  - W2-21 "starts once W2-50 has closed" (DEC-779 item 3, register:8541), and W2-50 "closes after W2-53" (DEC-760 item 2, register:8325).
  - Before that, DEC-737 held W2-48 for W2-01 "entirely", because it touches `gov close` (register:7919). It also shares `src/gov/close/` with W2-53 (WBS:916).
- *No new ticket while closes wait:* "no new ticket starts while a close waits on a quiet window it would disturb" (WBS:83, rule 19; DEC-806, register:8804).
- *The hooks' git environment.* W2-05 is idle until "W2-50 + W2-53 close" (`CHECKPOINT.md`, "Held / idle tickets"). The hooks stay off until Track A's fixes land (WBS:54).
- *The guard's self-lock fix.* W2-42 is in Track C, behind W2-10, W2-09 and W2-50 (F2).
- *Row W2-H054* (two versions in one worktree) is in W2-21 (TRIAGE:98). W2-21 depends on the held W2-20 (WBS:115) and waits for W2-50 (register:8541).
- *The first pinned use* comes at W2-24, after "every other Track A ticket" (WBS:118) and, in the staged batch, after W2-57 (WBS:651).

Ordinary work: yes, because this is the plan's own order, followed as written.
Consequence: other — delay.
- The plan's critical path of about 20.5 working days excludes "owner waits" (WBS:918).
- Those waits now set the pace: "one ticket closed of 55; nine verified tickets wait on W2-53's re-close" (DEC-806's basis, register:8803).

**Severity: high.**

### F6. The commit and push gates are off and CI cannot pass, so ADR-0001's hard boundary is not working during Wave 2

**Evidence.**
- *ADR-0001's hard boundary* (ADR-0001:52–57) has four parts:
  - git history;
  - "the lefthook **pre-push gate (G3)**";
  - GitHub Actions CI on every push, "as a visible **advisory** result";
  - "only the owner merges, and only on green".
- *The git hooks are off.*
  - They were removed on 2026-10-15, after a hook's check wrote foreign commits onto a ticket branch (DEC-710 to DEC-712, register:7470–7488).
  - They were put back on 2026-10-16 at 09:42 and removed again before `82459573` (register:7620; F-M13 at 7614).
  - `.git/hooks` holds no hook but samples, and `core.hooksPath` is unset (run 9).
  - WBS §0 rule 4 keeps them off until Track A's fixes land (WBS:54). W2-08 then asks the owner to reinstall them.
- *A test asserts that the gate is off.* `test_no_lefthook_hook_is_installed_in_this_repository` (`tests/acceptance/W1-40/test_w1_40_workflow_text.py:181`) passes only while the hooks are off. The owner accepted it as F-M4, to be restated when they return (register:7605).
- *Their return has entry criteria.*
  - F-A ("a check the project declares gets no inherited `GIT_INDEX_FILE`") is an entry criterion of W2-08 (DEC-804 items 1–2, register:8788–8792).
  - DEC-807 moved F-B and D-1 to Wave 3 (register:8817).
  - This is what DEC-803 prescribes for a risk that comes with a feature.
- *CI cannot pass.*
  - Its tests step fails with "unmeasured" until the owner approves pytest for the runner (`ci.yml`:20–23, 78–82).
  - Its evidence step fails when the commit has no pre-push note (`ci.yml`:14–17, 89, 93). No note can be written while the hooks are off.
  - CI already installs `gov` non-editable from the checkout (`ci.yml`:45). It is the one place here that runs a fixed copy.
- *Nothing is pushed during Wave 2* (`CHECKPOINT.md`, "Standing rules"). So the boundary acts only when the owner pushes and merges at the Wave's end, and as things stand, CI cannot be green then.
- *The guard and containment still run on every call.* But they are guardrails, not the boundary (ADR-0001:47–51).

Ordinary work: yes, because every commit made now goes in without the commit-time checks (G1 and G2) and the staged-secrets scan, and Wave 2 will end with a CI that cannot be green.
Consequence: fails open — the commit and push checks do not run. The owner accepted this for the hooks (DEC-712), and the guard and containment still run on every call.
**Severity: medium.** The risk is accepted and planned for (W2-05, W2-08), but F5 delays its end.

### F7. `gov doctor` reports the hooks as passing when no git hook is installed, and cannot tell an editable or foreign `gov`

**Evidence.**
- *The hooks check.* `src/gov/doctor/command.py`:506–515 returns "pass" when `lefthook.yml` exists and the lefthook program is found. It never looks at what git will actually run.
- *My doctor run* (run 5): `"hooks": {"status": "pass", "config_present": true, "binary_installed": true}`, while no hook is installed (F6).
- *The `gov` entry:* `ok: true`, with `found_version` empty and no location. Nothing says that `gov` is an editable install, or which tree it imports.
- *The planned check is for product repositories only.* W2-18's measure is "`gov doctor` in a product repository fails when its `gov` is an editable install, resolves to another repository's `src/`, or differs from `framework.lock`" (WBS:439).
- *Gates rely on doctor:*
  - W2-22 is "`gov doctor` green" (WBS:116);
  - exit criterion 3 is "`gov doctor` is green (exit 0) on this repository and on EXAMIN" (WBS:957);
  - W2-24 needs "`gov doctor` and `gov check` are green there" (WBS:658).

  With today's hooks check, doctor could be green here with no git hook at all.

Ordinary work: yes, because adoption, W2-22, W2-24 and the exit all rely on doctor as the health check, and it is run as a matter of course.
Consequence: fails open — a health check that passes a gate that is not there.
**Severity: medium.**

### F8. Two versions of the Gov OS in one worktree session; a hand rule keeps them apart, and DEC-732's stated reason misdescribes the hooks

**Evidence.**
- *The two versions* (run 4):
  - in the W2-50 worktree, a bare `import gov` loads the main tree, and with the per-command `PYTHONPATH` it loads the worktree;
  - the guard and containment there load the worktree (wire 2);
  - the stop hook loads the main tree (`stop.py:30`).
- *The hand rule.* DEC-732 (register:7806–7808) requires:
  - that "every test run and every `gov` command used for verification runs that worktree's own `src/`", with `PYTHONPATH` set per command (item 1);
  - that each lead shows a `gov.__file__` check, and "the output goes in the lead's return" (item 2).

  It is written into every brief, for example `briefs/W2-16-A5-run1.md`:85.
- *The row.* W2-H054 (high) is triaged into W2-21: "until it lands, the rule is kept by hand in every brief" (TRIAGE:98).
- *DEC-732's stated reason.*
  - Item 3 says the rule "is set per command, not in a session's environment, so the guard's own hooks keep running the code the session started under" (register:7809).
  - They do not. Each hook call is a new process that imports the session tree's `src/` as it is on disk at that moment. Run 3 shows a hook picking up an edit made after the session started.
  - The rule is still right; its reason is not.

Ordinary work: yes, because a bare `gov` or a `pytest` without the per-command `PYTHONPATH` is the default form in a worktree, and W2-01's lead met it (register:7805).
Consequence: fails open, for a worktree's own verification only: a green result can come from the main tree's code. The close after the merge then tests the right code, and fails closed.
**Severity: medium.** It is known, a hand rule is in force, and it is a row.

### F9. The tool's description of itself lags what is built

**Evidence.**
- *`gov check`'s help* says "list the declared checks (--list); running them is not built yet" (`src/gov/cli/main.py:95`). In fact the checks run and refuse closes (run 6; `src/gov/check/command.py`; register:8414).
- *The path map's systems block* marks five systems as absent, though their code exists under `src/gov/`:
  - the record store and retrieval, "not built yet" (`path-map.yaml`:148–149; `src/gov/store/`, `src/gov/retrieval/`);
  - the model adapters, "No adapter is built yet" (166–167; `src/gov/adapters/`);
  - `gov checkpoint`, "not built yet" (190–191; `src/gov/checkpoint/`);
  - telemetry, "not built yet" (193–194; `src/gov/telemetry/`);
  - `gov pause`, "not built yet" (208–209; `src/gov/pause/`).
- *Doctor's `adoption_level`* reports "systems_identified" 15 of 22 (run 5).

Ordinary work: yes, because agents read the help text and the path map to learn what exists.
Consequence: other — misleading, with no gate affected.
**Severity: low.**

## 4. Recommendations

**Classification of the findings** (on one line, as DEC-809 asks): F1 yes/other · F2 yes/other (fails closed) · F3 yes/other · F4 yes/other · F5 yes/other · F6 yes/fails open (accepted for the hooks, DEC-712) · F7 yes/fails open · F8 yes/fails open (a worktree's own verification only) · F9 yes/other.

F6, F7 and F8 answer "yes" to both questions.
- None of them is the work of a ticket under review.
- Each has a ticket that will run anyway: W2-08 for F6 and F7, W2-22 for F7, and W2-21 for F8. Their fixes ride along there (DEC-802).

None of the recommendations asks for a review round on any ticket. They are changes of method, for the owner to decide.

**R1. Govern this repository by a pinned, non-editable release, never by its own working tree.** It rests on F1, F2, F4, F5 and F8. It contradicts WBS §0 rule 1 (WBS:48) and the wording of exit criterion 1 (WBS:951), so under DEC-105 it comes with three costed options:

- **(a) Apply now. This is my recommendation, with medium-to-high confidence.** Before the next close:
  1. The owner builds the bootstrap pin by hand (§2.3, step 4):
     - a wheel from a commit that holds W2-53's ratchet (`fecb870c` qualifies);
     - its sha256 recorded in the tool registry;
     - installed non-editable into an environment of its own, and put on PATH in place of the editable install.

     DEC-605 is replaced.
  2. This repository's hook command lines call that environment and the hook programs of the pinned commit, not `$CLAUDE_PROJECT_DIR/src` and `template/…`.
     - This changes the hook source `.rulesync/hooks.jsonc` and the settings generated from it: an owner change under CAP-33.
     - The W1-38 acceptance tests compare that source with the generated settings and with the kernel template's (`tests/acceptance/W1-38/test_w1_38_hooks_source.py`).
     - I did not measure whether the change turns any of them red, so the independent test designer checks that first (MR-3).
  3. DEC-732's per-command `PYTHONPATH` stays. It now chooses only the code under test.
  4. Exit criterion 1 reads: "a clean `gov close` by the pinned release in force".
  5. W2-16 closes under the bootstrap pin. The owner then cuts the first W2-16 release with `gov release` (DEC-772).
  6. From then on, each version climbs the ladder of §2.3 and is used on a fixture first (W2-24's run, repeated for each version).

  - *Changes:*
    - DEC-605 and WBS §0 rule 1 are replaced, and exit criterion 1 is reworded;
    - W2-18 is widened to this repository: its KPI at WBS:440, and its paths;
    - the lead and worker briefs keep DEC-732's rule, with its reason corrected.
  - *Cost,* in my estimate: about a day of owner and orchestrator time, plus one CIT-P.
  - *Risk:* when a ticket changes a format that the pinned judge reads, a release that accepts the new format must come first.
  - *What it unblocks:* the self-judging half of the close queue (F4), the guard self-lock for this repository (F2), and the two-versions rule (F8).
- **(b) Defer to W2-18.** Widen W2-18 to cover this repository, and keep the current method until W2-16, W2-18 and W2-24 close.
  - *Changes:* W2-18's card only.
  - *Cost of waiting:* sixteen tickets that change the close, the guard, the hooks, the checks or the launcher go on being judged or guarded by their own unfinished code:
    - twelve in Track A: W2-05, W2-06, W2-07, W2-08, W2-09, W2-10, W2-19, W2-21, W2-48, W2-50, W2-53 and W2-56;
    - four in Track C: W2-41, W2-42, W2-44 and W2-45.

    That is the loop of F3 to F5 for the rest of Track A.
- **(c) Re-baseline.** Keep the editable install, and move exit criterion 1's proof off this repository.
  - This repository's tickets close on tests, independent review and the owner's merge.
  - The clean `gov close` is proven on the fixture and on EXAMIN's copy, with a pinned release (W2-24, W2-27).
  - *Changes:* exit criterion 1 and AR-8.
  - *Cost:* the lowest now.
  - *But:* the dogfooding signal from this repository is lost, and F2 remains.

**R2. Free the queue now, and stop a single timing test from stopping every close.** It rests on F4 and F3.
- *P-W2-47.* Decide it on the evidence.
  - The refusing case passes alone (`CHECKPOINT.md`; my run 8).
  - A `load_sensitive` entry still requires it to pass in an isolated re-run inside the same close (DEC-757 item 3).
  - That in-close re-run was "not alone" under load before (DEC-780's basis), so the close must keep its quiet window (DEC-780).
  - Whether the failure comes from the test's timing or from a real fault of the close under load is for W2-57 to settle (staged as DEC-813, WBS:651), as P-W2-47 proposes.
- *A standing rule, for the owner to weigh.*
  - When a test fails only in the parallel regression and passes alone three times in a quiet window, the orchestrator may add it to `load_sensitive` provisionally. The entry names the test by exact id and names its fix row. The owner ratifies or removes it in the next batch.
  - This reverses DEC-766's "package first" for that one narrow class.
  - Its risk is drift: a list that grows by habit.
  - `accepted_reds` stays owner-first.

**R3. Once the queue moves, close first the tickets that end the loop.** It rests on F5, F3 and F6.
- After W2-53 and W2-54, close W2-51, W2-49 and W2-16 ahead of W2-02, W2-03 and W2-20 in DEC-806's order. W2-49 closes after W2-51, whose validator its KPI uses (WBS:916).
- W2-48, the cache, starts as soon as W2-53 has closed, not after W2-21.
- W2-05 is not held behind W2-50 once a pinned judge is in place.

With R1(a) in force, most of this order stops mattering.

**R4. Make the guard's own failures explain themselves, and not need an outside repair.** It rests on F2.
- Widen W2-10's measure "Every guard refusal says it is final for that call" (WBS:318) to the guard's own failure paths: `import_error`, `decide_error` and the time limit.
  - The reason then goes to standard error, where Claude Code shows it to the agent. W2-10 already asks this of the stop hooks (WBS:315), and AR-6 item 4 asks it of the guard (register:7581).
  - The guard still fails closed.
  - W2-10 has not started, so this is a change to its card, not a round.
- Under R1, the session's guard is the pinned copy, and W2-H031 goes away for this repository.
- Without R1, W2-H031's own measure applies, and should come earlier than W2-42: "The guard falls back safely or the save is atomic" (LIST:221). Falling back to the last good copy is not a fail-open: the guard still judges every call.

**R5. Make `gov doctor` see the staging facts here, not only in product repositories, and correct the tool's description of itself.** It rests on F7, F6, F1 and F9.
- Doctor's hooks check reads what git will run: the hooks folder, or `core.hooksPath`. Add this to W2-08's measures, before exit criterion 3 and W2-22 count doctor's green.
- Its `gov` check fails on an editable install, or on an import from another tree, in this repository too. Widen W2-18's measure at WBS:439, or put the check in W2-22.
- Correct `src/gov/cli/main.py:95` and the path map's systems block.
- Have each release carry the list of built commands, so that the description travels with the version.

**R6. Give "ordinary discipline" a referee outside the agent's machine.** It rests on F6.
- Approve pytest for the CI runner (`ci.yml`:20–23 names this as the owner's decision), so that CI measures the tests while the hooks are off.
- Say plainly in the plan that CI's evidence step stays red until the hooks return. Then "only on green" (ADR-0001:57) can be met at the end of Wave 2, rather than waived.
