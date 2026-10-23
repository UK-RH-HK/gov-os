You are the ticket lead for ticket `DAEO-9nys` (`W2-67`, "Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-67` on branch `w2/W2-67`.

**This is run 1, its round 1.** `git log --oneline -1` must show `6da043aa`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

## Why you start now

On 2026-10-22 and 2026-10-23 the suites' whole-tree copies filled the machine. One auditor's folder held 7 million files. pytest kept two garbage folders of 9.7 million. Two leads' full verification runs left 1 million and 5.3 million files each, five times a lead's budget.

The owner brought this ticket forward to the next free slot (DEC-904 item 5). It removes the tree-copying tests behind these explosions, and much of the close time. Read the ticket file (`.tickets/DAEO-9nys.md`), the card (`docs/plan/WAVE_2_WBS.md` §2, W2-67), and lens I's synthesis (`docs/assessment/2026-10/I-SYNTHESIS.md`): §4's W2-67 block, P-IS-3 and P-IS-7.

## The owner's decisions for this run

- **Round 1 only (the overlap rule):** work only in the folders no ticket in flight holds:
  - the copying fixtures: `tests/acceptance/W1-07/w1_07_support.py`, `tests/acceptance/W1-25/**`, W1-27's old-path case;
  - `tests/acceptance/W1-26/**`, `tests/acceptance/W1-27/**`, `tests/acceptance/W2-02/**`;
  - the guard unit test's fixed `/tmp` folder (`tests/unit/guard/**`, that case only);
  - the root `tests/conftest.py`'s temp-folder rule.

  Not now:
  - W1-30 and `tests/unit/close` (round 2, after W2-07 and W2-66 merge);
  - W2-50's cases (round 3, after W2-69 merges).
- **The KPIs this round takes:**
  - **every per-test copy** commits with `gc.auto=0`, or copies the working files without `.git`;
  - **W1-27's old-path case** gets a project of its own;
  - a planted 7,000-object tree runs every copying case green in parallel;
  - **the suites keep pytest's own retention** of three base folders, and nothing passes a per-run `--basetemp`;
  - **the weak cases in these folders** are revised, each first shown red against a planted fault, then green on the head, each with a `Rewrite-Reason:`:
    - `gov doctor`'s 40 W1-27 cases first, before W2-22, W2-18 or W2-09 changes doctor;
    - W1-26's 45 planted-defect cases, their fixture shown green before any defect;
    - W2-02's unmeasured case.
- **Measure what the copies cost,** before and after your change: the inodes and the time of the W1-07, W1-25, W1-26 and W1-27 suites in the close's form. A copy that no longer copies the tree should show it.
- **The verification run (DEC-904 item 3):**
  - under `flock /tmp/gov-os-verify.lock`, within 6,000,000 files and folders and 60 GB in your temp folder (`/tmp/gov-os-lead-W2-67`);
  - the disk gate just before;
  - name the temp folder and its size in your return; the orchestrator removes it.
- **MR-3:** your test designer revises acceptance tests; your engineer changes the fixtures' builder code and `tests/unit`. Neither writes the other's files.
- **The FULL review is limited to round 1's changes.** The orchestrator merges round 1 early, so every close gains from it. Rounds 2 and 3 come later, each with its own review.

## This run's order

1. **Tests first:** a fresh independent test designer, launched sandboxed, `--effort xhigh`, on round 1's KPIs and its weak-case revisions, FULL proportion.
2. **Check red yourself**, for the reasons the README gives.
3. **Implement:** a fresh engineer, launched sandboxed, `--effort high`, on the copying fixtures and the conftest rule.
4. **Verify** in the close's form, under the lock, with `gov check` after a rebuild. Measure the copies' cost.
5. **FULL review:** a fresh read-only reviewer (brief A3 with `JUDGEMENT.md` word for word, `--effort max`) on round 1's changes. Commit the probe record under `docs/probes/DAEO-9nys/`.
6. **Return** DONE for round 1 (the branch merges early; the ticket closes later), or PACKAGES.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
