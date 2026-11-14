**Verdict: pass.** F-A, F-B and R1 are each met as described at `89d291eac5680a6900f6e5b755b47da84f0f0229`, and nothing else in behaviour moved. The new acceptance cases can't pass for the wrong reason: the F-A and F-B cases fail on round 1's code for the right reason, and the R1 case can't pass there by reading. I found nothing that blocks; four recorded rows follow.

**Step 0, sandbox check (launch_worker.sh):**
- (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-187` was refused (read-only file system), and no file exists.
- (b) `git hash-object -w --stdin` gave `1ae28402a109…` and `git update-index --refresh` exited 0. Both worked.
- `ps` check: no ollama or llama-server process is running.

task: chk-1, the narrow independent check of DAEO-0cd2 (W2-187) after review round 1 (FULL, class C2, DEC-1154)
status: done, verdict pass
work_completed: Read the fix diff from `5b82d1d53` to `89d291eac` (`597a82f93`, `d3d70b584`, `fc634374b`, `46d131ab9`). Traced F-A through the driver and its children (`--repo` and cwd of `preflight`, `measure` with its probe and control, `judge`, `declare`), and `gov.retrieval.measure` and `retrieve.store_of`. Traced F-B through `push.run`, `scanned` and `push`, and R1 through `memory_sets.walls_act` and the wrapper's environment. Ran the new F-A, F-B and R1 acceptance cases against round 1's code (an extracted copy of `src` at `5b82d1d53`, through `W172_SRC`). Checked scope, test-writer separation and the merge commit.
files_changed: none
evidence: `src/gov/memaudit/driver.py:180-190,197-216,221`; `src/gov/memaudit/push.py:124-135,201-230`; `src/gov/adopt/memory_sets.py:150-154,189-191`; `src/gov/memaudit/judge.py:45-57`; `src/gov/retrieval/measure.py:322,474`; `src/gov/memaudit/runner.py:45-55,67-73`; `src/gov/memaudit/declare.py:259-261`; `src/gov/memaudit/schedule.py:63-67,97-101`; `src/gov/memaudit/standing.py:286-292`; `src/gov/memaudit/pool.py:166-189`; `tests/acceptance/W2-187/fake_gov_x.py:46-69,149-160`
tests: 4 single cases, all through heavy_slot with an empty HOME, against round 1's `src`:
- S3 F-A case: fails with `FAULT attempt-1: store_commit`.
- S7 F-A case: fails because `measure` and `judge` searches ran in `.../repo`.
- S12 F-B case: fails because round 1 pushed the commit that landed during the scan.
- S11 R1 case: inconclusive there (round 1's `memory_sets` cannot find the briefs outside the extracted `src`); by reading, it cannot pass on round 1's line, which has no `GOV_MEMAUDIT_GITLEAKS=`.

Nothing at HEAD was re-run; the lead's results stand (`gov accept` 210 passed).
discoveries: The store link `/home/usain/gov-os-worktrees/W2-00-store` is a symlink to `-a`, with a `-b` half beside it. The driver hands the children the link path unresolved and checks `<link>.lock` only when the run starts (row X1).
risks: X1 (a refresh during a run); X2 (`pool` still searches the repository's own store; out of scope).
lessons: A planted `gov` that answers a fixed store commit wherever it runs cannot show which store was searched. Answering from the cwd's store, as the test designer's `store_from: root` does, is the form that tells them apart.
proposed_decisions: none
unresolved: none
recommended_next_action: The lead writes the narrow-check record with this verdict block. X1 to X4 are rows: X1 could ride along in a later resume (resolve the link once in the driver), and X2 goes with R6 to W2-172's owner.

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