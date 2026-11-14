---
type: probe
task: DAEO-0cd2
reviewer_session: 923b7aa4-a20b-45df-b182-c70ce248abaa
implementer_session: "engineer cc5956a9-edfa-4d91-a4cc-76ce0f2786d5 (597a82f93, d3d70b584); test designer d6048ab0-75a0-4f8a-9cd8-b65dbe59f28c (fc634374b)"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 89d291eac5680a6900f6e5b755b47da84f0f0229
decisions_applied: [DEC-1154, DEC-1157, DEC-1180, DEC-1156, DEC-1010, DEC-801, DEC-803, DEC-808]
---

# Probe record: W2-187 (DAEO-0cd2), the narrow check of the fix batch after review round 1

- **What was probed.** Head `89d291eac568` of `w2/W2-187`: only the change since review round 1's head `5b82d1d53868`
  (its record is now `PR-DAEO-0cd2-round-1.md`, pass). That change is the CTO's decided fix (a), in this ticket
  (DEC-1157 (12), DEC-1180 (4), DEC-1156 (7)):
  - F-A: the store searched is the declared store. On the standing and the fresh path, the `preflight`, `measure` and
    `judge` children work in the store link's work tree, as I6 states.
  - F-B, riding along: push only the scanned commit.
  - R1, riding along: step 6's cron line names gitleaks.

  The commits: the engineer's `597a82f93` and `d3d70b584`; the test designer's `fc634374b`, merged at `89d291eac`; and
  the lead's `46d131ab9`. This is a narrow check (DEC-1154), not a review round.
- **Who probed.** A fresh read-only reviewer: role `independent-auditor`, Opus, effort high, class C2, session
  `923b7aa4-a20b-45df-b182-c70ce248abaa`, 2026-11-14, started through `gov launch` under its OS sandbox. The ticket lead
  (an orchestrator-role session) commissioned and judged it. It wrote nothing: tripwire clean, `git status` empty at
  the end.
- **The lead's results at the probed head.** `gov accept W2-187`: pass, 210 passed, 0 failed, every line `success-1` to
  `success-12` and `failure-1` to `failure-7` pass. `tests/acceptance/W2-187` 210 passed, `W2-172` 162 passed, `W2-171`
  140 passed. The engineer also ran `W2-170` 184, `W2-173` 91, `W2-88` 215 and `tests/unit/memaudit` 363 passed.
- **The lead's judgement.** Pass, as the verdict block computes. Rows X1-X4 are recorded, none blocking:
  - X1: resolve the link once per run, so a refresh between `measure` and `judge` cannot split a run across halves. It
    fails closed and can ride along in a later resume.
  - X2: the fresh path's `pool` child still searches the repository's store. It is out of scope and goes with round 1's
    R6 to W2-172's owner.

**What I probed and found sound**
- **F-A, standing path:** `standing` hands `preflight`, `measure` and `judge` the link as `--repo` (`driver.py:180-190`).
  - `measure` resolves `--root` and runs every `gov retrieve` (the probe, the control and the measure) with that folder as cwd (`retrieval/measure.py:322,474`; `runner.py:51,72`). `judge`'s later searches use cwd `self.repo`, which is now the link (`judge.py:51`).
  - The real `gov` reports the fingerprints head of the cwd's store (`retrieve.py:163-176`), so the searched store and the declared store `f"{link}/.gov-runtime/store.db"` are the same.
- **Anchors at the audit commit:** the audit commit is `head_of(link)`, the link's own `HEAD` (`schedule.py:97-101`; `driver.py:370,385`). So the link's work tree is at that commit. `preflight`, `matcher` and `_lines_at` read it there, and `declare`'s DC-STORE still requires the link's store head to equal it.
- **F-A, fresh path:** `run` does the same (`driver.py:197-216`). S7's F is `right / n` from the fresh figures' verdict (`standing.py:286-292`), which comes from `judge`, so S7 compares the same store.
- **State does not move:** the children find the key folder through `GOV_MEMAUDIT_STATE`, which the driver sets (`schedule.py:63-67`), so handing them the link changes no state path.
- **The engineer's pool note:** `pool` (`driver.py:221`) feeds only `figures["pool"]`, that is the pool-regression cadence input, not S7's F or any verdict. It does not touch S7's comparison (row X2).
- **F-B:**
  - `scanned` reads `refs/heads/<branch>` before `scan` starts. A clean scan pushes `<sha>:refs/heads/<branch>`, and the line uses `commit[:12]`.
  - A missing branch gives a non-zero code (`returncode or 128`, or 127) and `PUSH failed`, so it fails closed and `commit[:12]` is never reached with no commit.
  - Findings and scan failures still block before any push.
  - The no-declaration path returns before `scanned`, so it writes nothing.
- **R1:** step 6's line carries `GOV_MEMAUDIT_GITLEAKS=<abspath(which) or "<path to gitleaks>">` before the wrapper, and `PUSH_ORDER` is unchanged. The wrapper passes its environment through to `push` (no `env -i`).
- **Nothing else moved:**
  - In `src`, only `driver.py`, `push.py` and `memory_sets.py` changed; `prompts.py`, the reader, the grader, `matcher` and `figures` are untouched.
  - No new output carries an id, question, gold, answer, citation, path or secret.
  - The week rule, `maintain` and the fail-closed push are unchanged.
- **Scope and separation:**
  - Every file the fix commits change is in `allowed_paths` (or is the ticket's acceptance path).
  - The engineer's commits touch no file under `tests/acceptance/`.
  - The merge `89d291eac` brings exactly the test designer's 8 files, and its tree equals `fc634374b` on `tests/acceptance` (empty diff).

**Findings (rows, none blocking)**
- **X1: a refresh during a run puts `judge` on the other half.**
  - What happens: the children get the link path unresolved, and the driver checks `<link>.lock` only at start (`driver.py:180,396`). If `gov rebuild --integration` swaps the link between `measure` and `judge`, `judge`'s later searches answer from the other half's store. They are then counted as `store` search failures with an empty bundle (`judge.py:55-56`), and anchors load from the newer tree.
  - What should happen: the driver resolves the link once, so every child of one run works in the same half.
  - This is still better than round 1, where the searches went to the repository's store.
  - Ordinary work: yes, because the operator's refresh after an integration merge can fall in the Monday run window.
  - Consequence: other. It fails closed: counted failures and at worst a spurious miss, never a false pass.
  - Scope: in (S3), not blocking.
  - Reversed by: evidence that the refresh never runs while an audit holds its lock, or that the children resolve the link once.
- **X2: the fresh path's `pool` child still searches the repository's store** (`driver.py:221`). This is the engineer's note.
  - It does not touch S7's F or any verdict. It can skew only W2-172's pool-regression cadence trigger, or stop a fresh run before `figures` when the repository has no store of its own (`pool.py:175-178`). Both are W2-172 behaviour, unchanged here (round 1's R6).
  - Ordinary work: yes, because the cron layout is the default.
  - Consequence: other.
  - Scope: out (the decided fix names `preflight`, `measure` and `judge`).
  - Reversed by: a KPI line that makes the pool figure a verdict input.
- **X3: an unusual branch spelling now fails the push** (`push.py:128-134`). A declaration that writes the branch as `refs/heads/main`, or a SHA-256 object-format repository (64-hex ids against the length check of 40), now gives `PUSH failed: git push exit 128`, where round 1 pushed.
  - Ordinary work: no, because the ACT text asks for `<branch>` and Gov OS repositories use SHA-1.
  - Consequence: other (fails closed, named).
  - Scope: in (S12), not blocking.
  - Reversed by: a declared form that the ACT text documents as a full ref.
- **X4: the R1 acceptance case could not be shown red by running it on round 1's code** (an environment artefact of the extracted `src`). Its assertion `GOV_MEMAUDIT_GITLEAKS=… ` cannot hold on round 1's line.
  - Ordinary work: no, because it concerns the probe, not the product.
  - Consequence: other.
  - Scope: in (S11), not blocking.

**Verdict: pass**

```verdict
{"kpis": [{"kpi": "success-3", "verdict": "pass", "findings": [{"id": "X1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-6", "verdict": "pass", "findings": []}, {"kpi": "success-7", "verdict": "pass", "findings": [{"id": "X2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-11", "verdict": "pass", "findings": [{"id": "X4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "success-12", "verdict": "pass", "findings": [{"id": "X3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "failure-7", "verdict": "pass", "findings": []}]}
```

guard_refusals: 1. A `git show --cc --format='%P' 89d291eac` call, which would have shown whole commit diffs, was refused by the guard (DEC-953: "git cannot say whether a revision holds the hidden part"). I did not repeat it. The merge check used `git diff --name-only` and `--stat` limited to `src tests docs governance`, which show file names only. The git status of the tree is empty at the end.
