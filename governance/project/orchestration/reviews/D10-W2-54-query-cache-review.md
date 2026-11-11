# D-10's red-fix list: the review of W2-54's one-answer case under W2-138's store.root (W2-138, DAEO-rmhj)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-W2-54-query-cache-review.md`; branch `w2/W2-138-d10-tests at d6472c9a4`; reviewer log `/home/usain/gov-os-worktrees/W2-138-d10-tests/.gov-runtime/scratch/lead/log/D10-W2-54-query-cache-review.json`.
- verdict.py: READY (no blocking finding).

# Review record: W2-138 (DAEO-rmhj), D-10's red-fix list, revision `d6472c9a4`

The revision is sound and the verdict is **pass**. The helper hides nothing that W2-54's measure depends on. The equal-commit claim holds, the sweep holds, and the trailers are right. I re-ran the revised case and it passes. There are two non-blocking findings.

**Sandbox check (Step 0):** passed.
- (a) The write to `/home/usain/gov-os-worktrees/.sandbox-trial-W2-138` failed as required: `OSError: [Errno 30] Read-only file system`, exit 1.
- (b) `git hash-object -w --stdin` wrote `1ae28402a109…`, and `git update-index --refresh` exited 0.

**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` printed nothing, so no model process of mine is running.

**task:** a fresh, read-only review of `d6472c9a4` on `w2/W2-138-d10-tests`: W2-54's one-answer case compared without `result.store.root`. KPI id `w2-54-store-root`.

**status:** DONE

**work_completed:**
- Read the revision, the whole case file and the fixture helpers in `w2_54_support.py`.
- Traced where S1's `store` comes from in the source.
- Read W2-138's own S1 case, the ticket and DEC-1109.
- Spot-checked seven whole-result comparisons (four in W2-54, three in other suites) and the `gov context` path.
- Ran the one revised case read-only.

**files_changed:** none in any tree. Two things were written outside it:
- Step 0 (b) wrote its blob and refreshed the index, as the launch brief requires.
- I used a scratch folder under the sandbox's TMPDIR and have removed it.

**evidence:**
- The run: `tests/acceptance/W2-54/test_w2_54_query_cache.py::test_one_ticket_gets_one_packet_hash_whatever_the_cache_s_state` gave `PASSED`, `1 passed in 10.09s`. It was collected and run, not skipped.
- How it ran: through `heavy_slot.sh`, which waited for a slot from 00:40:38. Settings were `PYTHONPATH=<worktree>/src`, scratch `HOME` and TMPDIR, `PYTHONUSERBASE=/home/usain/.local`, `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider -o tmp_path_retention_policy=failed -rA`.
- No writes: after the run, `git status --porcelain` was empty, and `find -newer <marker>` listed no file in the tree.
- Scratch folder: `du -sh` 24K and `du -s --inodes` 7 before I removed it.

**tests:** one node id, using the stand-in embedder. It is not a `local_only`, `real`, `green_here` or `time_limit` case, so the exclusion left nothing out. I did not re-run the designer's whole-folder numbers (82 passed / 3 failed → 83 passed / 2 failed).

**discoveries:**
- **Folder mtimes:** the sandbox wrapper changes the mtime of the worktree root and of `.gov-runtime/` on every sandboxed command. They moved from 00:42:29 to 00:42:45 with only a `stat` in between; the `/dev/null` mount points in `ls` (`.bashrc`, `.gitconfig`, `.gov-runtime/s`…`scratc`) are the sandbox's. A `find -newer` therefore always lists those two folders even when no file changed.
- **Precedent for F1's fix:** `test_w2_54_dropped_order.py:143-146` already masks a folder as `<project>` instead of deleting it.

**risks:** F1 and F2 below. Neither blocks.

**lessons:** when a field names the folder, mask it with a fixed marker rather than deleting it. Masking keeps the field's presence in the comparison at no cost.

**proposed_decisions:** none.

**unresolved:**
- I could not run a probe script on made-up answer pairs: the Write tool's write into my TMPDIR was not granted, and I did not route round it. The helper's behaviour below comes from reading its four lines; it has no branches beyond them.
- The red before the revision is the CTO's measurement at `b0bbd373f`; I did not reproduce it.
- I opened only seven of the other suites' whole-result comparisons.

**recommended_next_action:**
- Compute READY from the block below.
- F1's masking can ride along the next time this file is touched (DEC-802).
- F2 becomes a row.

## Answers to the checks

**1. No fail-open: yes, no fail-open.**
- **What the helper does:** it drops only `store.root`, and only when `store` is a dict that holds it. It builds a copy, so `answer` and `answer_reference` themselves are untouched.
- **Differences that still fail:**
  - a different `store.commit`, or `None` from an unreadable store;
  - `store` missing, `None` or not a dict in one answer, since the other keeps `{"commit": …}`;
  - any other key under `store`, or a new top-level key;
  - the evidence, the facets, and everything else.
- **What it hides:**
  - **The value of `root`, by design.** It is the `--root` folder, link-resolved before any cache is read (`retrieve.py:156-160`, `retrieve/command.py:110-111`), so no cache state can change it. Its correctness is W2-138's KPI, held by `test_w2_138_store.py:18-27`, which checks that it is a string whose realpath is the store folder.
  - **Its presence on one side only**, when the other side's `store` is a dict without `root`. This is F1, and today's code cannot produce it.
- **Passing a result without `root` through is right here.** When both answers lack it, which happens before S1 or if S1 breaks everywhere, they are compared whole as before. Failing on absence would turn this cache case into a second S1 test and make it red for a reason outside its KPI.

**2. Commit equal by construction: yes.**
- **What the commit is:** `store.commit` is the store's fingerprints `head` (`retrieve.py:163-176`). `loader._load` writes it at build from `git rev-parse --verify HEAD^{commit}` (`loader.py:676, 693-695`). It depends on neither the folder nor when the read happens.
- **Same content:** each project gets exactly one commit with no parent, made by `commit_all` with the message "the fixture". The bytes are identical in both:
  - `.gitignore`;
  - the path map and `.gitleaks.toml` (`copy2` keeps the file mode);
  - one `files` dict, passed to both builds (`test_w2_54_query_cache.py`, lines 404 and 418).
- **Same metadata:** `S.git` (support lines 266-273) pins:
  - author and committer name, e-mail and date (`BASE_DATE`, `+00:00`);
  - `LC_ALL`;
  - `HOME` set to the project, with no system config, so there is no signing and no hooks.
- **Nothing commits later:** after the build, writes go only to the ignored `.gov-runtime/`.
- My run confirms it: the case passes with `commit` still compared. If a later fixture change broke the equality, the case would go red, which is the safe direction. The failure message would not say why, though (F2).

**3. The sweep: holds.** None of these compares whole `gov retrieve` results across folders:

| Comparison | What it compares |
|---|---|
| W2-54 `shared_gpu:111-119` | both bundles from one project |
| W2-54 `query_vector:78-92` | one project, through library `retrieve()`, which has no `store` (only `gov/retrieve/command.py::run` adds it) |
| W2-54 `query_vector:131-148` | one project |
| W2-54 `sandboxed_worker:235-257` | one read root; the inside/outside check at :261 compares evidence only |
| W2-32 `s7_file_index:129-135` | one project, before and after |
| W2-87 `support:395-397` | chunk ids and drops only |
| W2-92 `unchanged` | library `retrieve` (`w2_92_support.py:463`), no `store` |

`gov context` packets carry no `store`. This case's own cross-folder packet comparison (line 452) passed in my run.

**4. Trailers: all correct.**
- `Task: DAEO-rmhj` is W2-138's ticket, whose `allowed_paths` names this exact file "[DEC-1090 (3), DEC-1109 (2)]".
- `Role: independent-test-designer`.
- `Implements: DEC-1109, DEC-1090`.
- `Rewrite-Reason: DEC-1090 (3): …` is in the form the test-designer role file asks for (DEC-491), and the case's docstring carries the same text.
- `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Exactly one file changed, `tests/acceptance/W2-54/test_w2_54_query_cache.py`, +19 −2. The packet assertions are unchanged.

## Findings

**F1 (scope: in):** `_beside_its_folder` deletes `store.root` instead of masking it. So if one answer's `store` has `root` and the other's is a dict without it, the two compare equal.
- Ordinary work: no, because today's code cannot produce that pair. `store_of` (`retrieve.py:163-176`) builds `commit` and `root` in one dict literal, and `run` (`retrieve/command.py:127, 136, 148`) puts that dict in every result. W2-138's own case checks that `root` is present and correct.
- Consequence: other. At most it could hide an S1 regression, which is W2-138's KPI. It could never hide a difference in the evidence, facets or packet across cache states, which is W2-54's KPI. The fix is to replace `root` with a fixed marker when present, as `dropped_order:143-146` does. That makes it a row, not a round.

**F2 (scope: out):** the failure message in `same()` prints only the two evidence path lists. Any difference outside the evidence therefore shows up as "one question, two answers" over two identical lists.
- Ordinary work: yes, because that is exactly how the `root` difference appeared at `b0bbd373f`.
- Consequence: other. The test still fails, so it fails closed; only the diagnosis is slower. The message predates this revision and was not changed by it.

```verdict
{"kpis": [{"kpi": "w2-54-store-root", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```
