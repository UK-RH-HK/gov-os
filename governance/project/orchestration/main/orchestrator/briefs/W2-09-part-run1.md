You are the ticket lead for ticket `DAEO-a3m2` (`W2-09`, "SubagentHandback on the guard's list; the list checked against the CLI"), profile FULL, keystone 3, working only in the worktree `/home/usain/gov-os-worktrees/W2-09` on branch `w2/W2-09`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**This run ends at the engineer gate.** It covers the design, the tests, the red check and the CIT-P. No code is written in it.

**Read first:**
- the ticket file (`.tickets/DAEO-a3m2.md`) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-09"), with its route: "the guard change goes through CIT-P with owner approval (CAP-33). The lead returns the proposal as a package before the engineer starts";
- DEC-685, DEC-743 (item 4, and the CIT-P's §6.2 it cites), DEC-849, DEC-941 (item 1.3) and DEC-942 (items 1 and 4); CAP-33 in the Contract;
- the six list rows in `docs/plan/WAVE_2_LIST.md` and `docs/plan/WAVE_2_TRIAGE.md`: W2-H055, W2-I015, W2-L203, W2-M016, W2-M235 and W2-M236. Re-check each against the code (DEC-718);
- `src/gov/guard/decide.py`: `WRITE_TOOLS`, `READ_TOOLS` and `LISTED_TOOLS` with their reasons (lines 20 to 45), and the decision that refuses an unknown tool (around line 1128); `src/gov/guard/reads.py`'s `policy_refusal`, which today judges only the read tools and Bash;
- `src/gov/doctor/command.py`, read-only: `_check_tools` and `_check_claude_code`, and `tests/unit/doctor/test_doctor.py`;
- a CIT-P's form: `docs/changes/W2-50-CIT-P.md` (its basis names its tests' commit and red count) and `docs/changes/W2-59-CIT-P.md` (a judge change, with its owner acts and rollback), and the kernel's change skill (`.claude/skills/change/SKILL.md`).

## Why you start now

- **K3, block C** (DEC-941 item 1.3; REPLAN-W2 §2, row C: W2-60, W2-11, W2-09, W2-33). You also head the chain W2-09 → W2-10 → W2-11 and W2-42. W2-10 depends on you, and K3's W2-11 and K6's W2-42 both depend on W2-10.
- **Guarded sessions refuse harmless tools** (W2-M016). Monitor and every `mcp__` tool are refused today, so leads wait with sleep loops. A new or renamed harness tool stays refused until someone lists it by hand, and nothing notices when the CLI changes (W2-M236).
- **A fail-open hole, high** (W2-H055, DEC-743 item 4): the guard does not judge a `git clone` destination. A session without a sandbox (the orchestrator, a lead) can clone into another ticket's folder, the `~/gov-os-runs` root or the workbench.
- **Your first phase writes no file another ticket holds** (DEC-942 item 1). The CIT-P comes first and needs the owner's approval, and the engineer's `decide.py` is shared with W2-58 and W2-05 (below). So the proposal and the tests start now, and the engineer starts once both have landed.

## The decisions for this run

- **Design first, short.** The ticket's paths hold no note, so you write it in your scratch: `.gov-runtime/scratch/lead/design.md`, at most a page, in behaviour; it is a plan, not code. It says:
  - **`SubagentHandback`:** on the known list, with its reason. A helper's return is handed back under the guard, and the guard judges it rather than refusing it as unknown;
  - **the owner's list of read-only tools** (W2-M016, W2-I015). It names each tool proposed, Monitor and the read-only `mcp__` tools you find in use, with its effect: what it reads, whether it writes a file of the project, and whether it runs a command. The list is the owner's to approve in the CIT-P; the note proposes it;
  - **a listed tool with a write effect is judged like Bash** (the failure KPI). A tool that runs a command, as Monitor does, has that command judged as Bash's is: its write targets, and the read refusals of DEC-820 (a), (c) and (d) that `policy_refusal` applies to Bash;
  - **an unknown tool is still refused** (DEC-685). Names are compared as sent: a case variant or a near-name of a listed tool is unknown;
  - **the CLI check** (W2-M236): where `gov doctor` reads the installed CLI's version and its tool list, and how it knows the version changed since the last comparison. It names each difference both ways: a tool in the CLI that the guard does not know, and a listed tool the CLI no longer has. A CLI it cannot read is never a pass. If the source of the tool list needs a model call, a login or the network, the note says so;
  - **`git clone`'s destination** (W2-H055) is judged as a write target like any other, for every role. A clone into another ticket's folder, the `~/gov-os-runs` root or the workbench is refused with the guard's reason;
  - **W2-L203 and W2-M235:** whether the side effects of `Agent`'s worktree isolation and of `SendMessage` are judged or accepted by decision, and where W2-M235's wiring check lives. If it is `src/gov/launch/launcher.py`, it is outside your paths;
  - **the files the engineer will need**, named one by one. `gov doctor`'s wiring very likely needs `src/gov/doctor/command.py`, which is outside your paths. W2-57 holds it, and W2-05 has changed it. Give the exact lines.

  It goes into the test designer's brief as text, and into the CIT-P engineer's.
- **Tests first,** by a fresh independent test designer (launched sandboxed, `--effort xhigh`, a measured trial for FULL test designers, DEC-839; its brief must not set `TMPDIR`), in `tests/acceptance/W2-09/`:
  - one case per KPI line, success and failure, plus the key edge cases;
  - the guard's hook program from this worktree (DEC-732), fed the hook input as Claude Code sends it:
    - `SubagentHandback` passes, with its reason;
    - an unknown name, a case variant and a near-name are refused;
    - each tool on the proposed list is judged, not refused as unknown;
  - **a listed tool that runs a command:**
    - a command that writes outside the session's paths is refused, as with Bash;
    - a command that reads a secret, the counterpart's work or a hidden half is refused, as with Bash;
    - a read-only command passes;
  - **`git clone`'s destination,** for an unsandboxed role and a launched role: into another ticket's folder, the `~/gov-os-runs` root and the workbench, each refused with the reason. A clone into the session's own permitted path passes. Use temporary folders and fake home paths; never clone this repository;
  - **`gov doctor`'s comparison,** against a planted stand-in for the CLI (a script on a temporary `PATH` that reports a version and a tool list). Never the real `claude`, and no session is launched:
    - a version change triggers the comparison;
    - each difference is named both ways;
    - an unreadable CLI is not a pass;
  - **earlier acceptance tests that pin the known list** (W1-02's and W1-38's among them; the designer checks): named in the README, never edited. A revision is a package.
  - **The tests follow the design note's proposed list.** If the owner changes the list in approving the CIT-P, the designer revises those cases with `Rewrite-Reason:` naming the owner's decision (DEC-491) and lowers no other expectation.
- **The CIT-P,** after the red check, by a fresh engineer (launched sandboxed, `--effort high`).
  - **Its one file:** `docs/changes/W2-09-CIT-P.md`. It writes no code and no test, and never reads `tests/acceptance/W2-09/`.
  - **Its form and content:** the form of W2-50's and W2-59's, carrying the design note and stating:
    - what changes and what stays;
    - the owner's list for approval, tool by tool with its effect;
    - every file the change touches, those outside the paths with their exact lines;
    - the owner's acts: the re-pin and the settings regeneration, since the guard judges every session;
    - the risks and the rollback;
    - the tests' commit with their case count and red count, from your red check, which you give it.
  - **The routes:** your workers have no `product-spec` route, since the ticket's role is engineer, so the engineer writes the CIT-P (as W2-59's did).
- **The engineer gate.** The implementing engineer starts in a later run, and only when all three of these hold. Check each with Bash, and quote the output in your return:
  1. **the owner has approved the CIT-P:** a decision on `w2/integrate`'s register names W2-09's CIT-P (`git -C /home/usain/Dynamic-Agentic-Engineering-OS grep -n 'W2-09' w2/integrate -- docs/DECISION_REGISTER.md`, read for an approval);
  2. **W2-58 is closed:** `grep -m1 '^status:' /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-5j8b.md` says `status: closed`;
  3. **W2-05 is merged:** `git -C /home/usain/Dynamic-Agentic-Engineering-OS merge-base --is-ancestor w2/W2-05 w2/integrate` exits 0. Give its exit code and `git -C /home/usain/Dynamic-Agentic-Engineering-OS log -1 --format=%h w2/W2-05`. That merge carries its row 42, the freeze look-up's 15 seconds in `decide.py` (DEC-783 item 2).

  In this run the first cannot hold yet, so you return PACKAGES at the gate. Say which of the three hold, and what the engineer waits for.
- **Fail closed** (for the CIT-P and the tests):
  - nothing new is let through without its reason;
  - no fallback widens the list;
  - no listed tool that runs a command escapes Bash's judgement;
  - an unreadable CLI is never green.
- **Running beside you** (paths checked against yours, file by file):
  - **W2-58** (`DAEO-5j8b`, closing) holds `src/gov/guard/{decide,reads,protected,heldout}.py`, `src/gov/launch/**`, `tests/unit/guard/**`, `tests/unit/launch/**` and `template/governance/kernel/schemas/path-map.schema.json`. `LISTED_TOOLS` lives in its `decide.py`, and a refused close repairs into the same files.
  - **W2-05** (`DAEO-0z8c`, merge-back) has changed `src/gov/guard/containment.py` and `src/gov/doctor/command.py`. Its run 3 plans `src/gov/guard/decide.py` (row 42), `src/gov/guard/reads.py`, `src/gov/cli/main.py` and `src/gov/close/{repo,history,traceability,command,tool}.py`. It also holds `src/gov/**/*.py` for the git environment of git calls, and `src/gov/util/gitenv.py`.
  - **W2-57** (`DAEO-cy5o`, run 4b queued) holds `src/gov/doctor/command.py`, `src/gov/close/serial.py` and `src/gov/close/command.py`.
  - **W2-67** (`DAEO-9nys`) holds `tests/unit/guard/**`, `tests/unit/close/**` and `tests/conftest.py`. When the engineer comes, it writes only new `tests/unit/guard/test_w2_09*` files there.
  - **W2-61h** is held until the guard's refusal of a hidden half covers every tree (row W2-H063). That fix lands in `src/gov/guard/reads.py`, which your design does not touch.
  - **W2-60a** (`DAEO-cv58`) holds `src/gov/launch/{launcher,role,record}.py`. W2-56 holds `launcher.py`, `sandbox.py`, `environ.py` and `src/gov/codeintel/__init__.py`.
  - **W2-03** holds `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**` and `src/gov/check/citations.py`. **W2-61** holds `src/gov/retrieval/measure.py`. **W2-71** holds `src/gov/secrets/**`. **W2-77** holds `src/gov/close/nightly.py`. **W2-68** (closing) holds `src/gov/close/{batch,fingerprint,command,repo}.py` and `src/gov/store/**`.

  In this run, write nothing there. Any change the design needs outside your paths goes into the CIT-P with its exact lines, and into your return as a package.
- **The red check:** the acceptance suite `tests/acceptance/W2-09/` only, in the background with an exit-code file. A rebuild is needed only if the tests need the store.
  - **The nightly (owner, DEC-933, DEC-936):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists (from 02:00 most nights), you and your workers run no suite and no rebuild. Wait, and go on the moment it is gone.
  - **A close's quiet window:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, start no worker and no suite.
  - **Every rebuild** runs as `flock /tmp/gov-os-rebuild.lock …` (DEC-939 item 2).
  - **The full verification and the 01:00 cut-off (DEC-939 item 6)** belong to the engineer's run, not this one.
- **Review:** one (FULL), in the engineer's run. A fresh FULL reviewer (brief A3 with `JUDGEMENT.md` word for word, `--effort max`) on the final head, given the design note and the approved CIT-P. None in this run.

## This run's order

1. The design note (yours, in scratch).
2. Tests first (the test designer), then **check red yourself.**
3. The CIT-P (a fresh engineer, its one file), given your red-check figures.
4. A checkpoint (`gov checkpoint`, committed with your trailers).
5. The engineer gate's three checks.
6. **Return** PACKAGES:
   - **P-W2-09-1:** the CIT-P for the owner, in DEC-818's six parts, with the CIT-P's path and commit, the tests' commit and red count, the proposed list, and your recommendation and confidence;
   - any package for a file outside your paths, with its exact lines;
   - **the gate's state:** each of the three conditions with its output, and what the engineer waits for.

   These block only the engineer phase.

**Estimate:** about 90 lines in the engineer's run. This run: the design, the tests and the CIT-P, about 4 hours, with no full run.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
