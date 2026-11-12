# D-10's red-fix list: the review of W1-19's scratch environment and W2-54's shared_gpu case (W2-126, DAEO-jpr0)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-W1-19-W2-54-review.md`; branch `w2/W2-126-d10-tests at 8bb8182f1`; reviewer log `/home/usain/gov-os-worktrees/W2-126-d10-tests/.gov-runtime/scratch/lead/log/D10-W1-19-W2-54-review.json`.
- verdict.py: READY (no blocking finding).

sandbox_check: PASS. (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-jpr0','w').write('x')"` was refused with `OSError: [Errno 30] Read-only file system`. (b) `echo sandbox-trial | git hash-object -w --stdin` returned `1ae28402a109…`, and `git update-index --refresh` exited 0.
ps_check: PASS. `ps -eo pid,args` at the start and before return showed only my own shell and `ps`, since the sandbox has its own process namespace. No ollama or llama-server of mine ran. I used no GPU, no real model, and no `gov retrieve` or `gov context`.
task: W2-126 (DAEO-jpr0), D-10's red-fix list, DEC-1109 (2). A read-only independent review of `adec4718a..8bb8182f1`: A is W1-19's scratch environment and the vector cache; B is W2-54's `shared_gpu` query-device case.
status: DONE. Both KPIs pass with no blocking finding: none is in scope, reachable in ordinary work, and fails open or loses work. There are six rows (F1–F6), all with consequence "other".
work_completed: Read:
  - the diff and the three commits' trailers, and the ticket;
  - `tests/conftest.py`;
  - W1-19's conftest, support file, embedding-policy cases and semantic-index cases;
  - `vector_cache.py` and `semantic.py`'s device rule;
  - W2-54's shared-GPU file, conftest, support file and KPI line;
  - DEC-1033, DEC-1042, DEC-1065 and DEC-1067 in the register.
  Then reproduced A's red and green on the branch head, confirmed the fixture order, and collected B.
files_changed: none. I wrote nothing in any tree, and removed my scratch folder under the sandbox's TMPDIR.
evidence: All runs were at `8bb8182f1`, through `heavy_slot.sh`, with an empty HOME:
  - (1) `test_w1_19_embedding_policy.py` serially, both cases in one process: 2 passed.
  - (2) The same run with `Api.scratch_env` patched in memory to drop `GOV_VECTOR_CACHE_DIR`, as `adec4718a` did. This used a one-line `python3 -c` wrapper around `pytest.main` and wrote no file. Result: 1 failed, 1 passed, with `assert 'February' in ''` at line 73, exactly the reported red.
  - (3) One `indexed` case with `scratch_env` wrapped to print the cache folder it sees: `None` for `api.exists` (session fixture), `None` for `indexed`'s refresh (module fixture), then `…/pytest-1/vector-cache/4354afadc76a1173` in the test body. 1 passed.
  - (4) `-m shared_gpu --collect-only` on `test_w2_54_shared_gpu.py`: 2 tests, including the new node id.
  - Scratch use: 4.7 MB and 418 inodes at peak; removed.
tests: The four runs above: 5 cases run, 4 passed, and 1 red under the old behaviour as intended, plus one collect-only. Every run used `-p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only"`; runs (1) and (2) also used `-k "not real and not green_here and not time_limit"`, which left nothing out of that file. Not run: the whole W1-19 folder, which the designer's and the CTO's runs cover, and B on the GPU, which the sandbox blocks; the CTO's run outside it is the evidence.
discoveries:
  - (a) `indexed` is module-scoped (`tests/acceptance/W1-19/conftest.py:92`), not session-scoped as the brief says.
  - (b) The code counts a partly offloaded model as "gpu" (`semantic.py:378-379`, `size_vram > 0`). The revised case requires `size_vram == size`, so it is deliberately stricter than the code.
  - (c) In a run of both shared-GPU cases, the second case's read is served by the session's machine-wide cache (F5).
  - (d) The Write tool was refused for a throwaway plugin file under my own TMPDIR. I wrote no file and patched in memory instead; I'm naming it as the common rules ask.
risks: Nothing blocking. Under F3, a fixture would write stand-in vectors into whatever folder an exported `GOV_VECTOR_CACHE_DIR` names; nothing exports it today.
lessons: When a scratch environment drops a per-test variable, tests can share a cache without anyone noticing. Patching the helper in memory and re-running both cases in one process shows the cause and the fix without touching a tree.
proposed_decisions: none.
unresolved: Nothing for this revision. F1–F6 are rows for the CTO; F5 and F6 belong to W2-54, outside this revision.
recommended_next_action: READY on both KPIs; land as is.
  - F1 and F2 (the trailer and the ticket line) can ride along with the next edit of this ticket.
  - F3 is a Wave 3 row.
  - F4–F6 go to W2-54's next revision.

## Answers to the checks

**1. A: no expectation was lowered.**
- **Lowered?** No. `test_w1_19_embedding_policy.py` is not in the diff. The check `support.ORCHARD_WORD in ollama.embedded_text()` (line 73) is unchanged. It still requires the embedded namespace's text to reach this test's own stand-in. With the old environment it fails exactly as reported (run 2); with the revision it passes (run 1).
  - The first case's negative check (line 60, no word of a not-embedded namespace is sent) is now stronger: no vector cached by another test can stand in for a send.
- **With the variable unset:** `cache` is `None` or empty, so the key is left out and the dict is the old one, apart from key order. `**extra` is still last, so a caller can set or override the variable. `vector_cache.location()` also treats an empty value as unset (lines 44–46). The behaviour is the same as before.
- **Other environments W1-19 builds from scratch:**
  - `env_without_sqlite_vec` and `env_with_the_reranker_environment_and_no_snapshot` are built on `scratch_env`, so they now carry the variable too.
  - `real_env` copies `os.environ`, so it always carried it.
  - `git()` runs only git.
  - `scratch_env` still drops `GOV_GUARD_CALLS_DIR` (set per test, `tests/conftest.py:109-113`) and `GOV_REBUILD_LOCK` (set per process). Only the guard hook and `operator_run.py` read the first; only `gov/rebuild/watch.py` reads the second. W1-19's driver loads only `gov.retrieval`'s semantic, lexical and fusion modules, and none of them imports `gov.rebuild`. Dropping these two changes nothing.
- **The `indexed` fixture's shared cache:**
  - It is module-scoped, not session-scoped, and six cases use it, all in `test_w1_19_semantic_index.py`.
  - pytest sets it up before the per-test autouse fixture, so its refresh sees no variable and uses the scratch HOME's default cache (run 3).
  - After this revision no test body writes that cache, so `indexed` builds cold, once per process.
  - None of its six cases checks what its stand-in received or any cache count; they read `report["available"]`, the store's files, freshness, the manifest and the hits.
  - So it matters to no case. The one edge, an exported variable, is F3.

**2. B: the choice of "on the GPU".**
- **DEC-1033 (2)(b)** reads "a question's vector accepted from any device **and** the query server on the GPU". The first half is about what the code accepts; the stand-in cases of `test_w2_54_cpu_embedder.py` hold that (their Rewrite-Reason, lines 20–28). The second half is about where the machine runs the query server, which is what this case reads.
- **DEC-1065 (1)**, standing, allows no CPU embedder anywhere. The code already refuses a vector computed on the CPU (`DEVICES = ("gpu",)` and `EMBEDDER_ON_CPU`, `semantic.py:80-81`).
- **Verdict:** asserting the query server on the GPU is what the decisions say. The case is stricter in two places:
  - **Stricter than the code:** it requires the whole model on the GPU, while the code accepts a partly offloaded one. I read this as allowed. The same file has always read "on the GPU" as `size_vram == size` for the shared runner, and DEC-1067's GPU-safety rule treats "an embedder losing layers" as a fault. A split query server gives a red, never a false pass.
  - **Stricter than W2-54's KPI 5 wording**, which still says "on whatever device it reports the model on" and predates DEC-1065 (F6).
- **Nothing the case checked is lost:**
  - The shared runner is still checked before the read ("after the index build") and again after it.
  - One revision is still required: the two `/api/tags` digests must be equal and non-empty.
  - The printed line is kept, reworded to "the query server", and the CTO's printout matches the new format.
  - The new check still requires a non-empty listing with `size > 0`, so an unloaded, unreachable, CPU or split query server fails it.
  - The new full node id collects (run 4). `gov accept`'s map reader (`src/gov/accept/runner.py:68-108`) reads table rows only, so the old name left in a prose bullet at README line 1058 is not read as a map item.

**3. Trailers and files.**
- **`769f01577` (CTO):** `Task: DAEO-sdxk`, `Role: orchestrator`, `Implements: DEC-1109`, `Co-Authored-By` ✓. It has no Rewrite-Reason and needs none, since no test changed (DEC-491's trailer is for a designer's rewrite). Its `Task` names a different ticket (F1). It changes only `.tickets/DAEO-jpr0.md`, adding 3 lines.
- **`498204460`:** `Task: DAEO-jpr0`, `Role: independent-test-designer`, `Implements: DEC-1109, DEC-1042, DEC-1033`, `Rewrite-Reason: DEC-1042: …`, `Co-Authored-By` ✓. Files: `W1-19/w1_19_support.py` and `W1-19/README.md`.
- **`8bb8182f1`:** the same Task, Role and Implements, `Rewrite-Reason: DEC-1033 (2)(b) replaced DEC-798: …`, `Co-Authored-By` ✓. Files: `W2-54/test_w2_54_shared_gpu.py` and `W2-54/README.md`.
- **Files overall:** exactly the four named files plus the CTO's ticket line. The ticket's new lines name three of the four (F2).

## Findings

**F1** (scope: in; filed under `w1-19-vector-cache`, though it concerns both KPIs): The CTO's ticket commit `769f01577` changes `.tickets/DAEO-jpr0.md` but carries `Task: DAEO-sdxk`. The orchestration skill (`SKILL.md:71`, MR-6, DEC-537) says a commit touching a ticket's file names that ticket in `Task:`. The two earlier widenings of this ticket's paths (`818017894` and `d72e8dbe4`) did name DAEO-jpr0.
Ordinary work: yes, because the CTO wrote it in ordinary work under its D-series task id.
Consequence: other. A search by `Task: DAEO-jpr0` misses this widening of W2-126's paths; nothing fails open and no work is lost.

**F2** (scope: in; `w1-19-vector-cache`): The ticket's new lines name `tests/acceptance/W2-54/README.md` but not `tests/acceptance/W1-19/README.md`, which `498204460` changed. The guard allowed the write, because the test designer may write `tests/acceptance/**` while its ticket is in progress (`independent-test-designer.md:8`). So nothing escaped, but the ticket's record of D-10's paths is one file short.
Ordinary work: yes, because a hand-written path list easily misses a README.
Consequence: other. It is a gap in the record only.

**F3** (scope: in; `w1-19-vector-cache`): Calls made while fixtures are set up now take the process's own `GOV_VECTOR_CACHE_DIR`. `api.exists` (session) and `indexed`'s refresh (module) run `scratch_env` before the per-test fixture sets the folder (run 3).
- When the variable is unset, as in every run seen, they fall back to the scratch HOME, as before.
- If a shell exported it, `indexed` would now write the stand-in's vectors into that folder. That could be the owner's real cache, which DEC-1042 (1) keeps test runs out of. The entries would sit under the stand-in's own digest (`w1_19_support.py:810`), a key space no real lookup reads.
- Before this revision the scratch environment never carried the variable.
- A possible fix for the row: give fixture-time calls a folder of their own.
Ordinary work: no, because it needs the variable exported in the shell that starts pytest. Nothing in the repository or the orchestrator's tools sets it, and the cache's default location needs none.
Consequence: other. A few stand-in entries in a separate key space; nothing wrong is served.

**F4** (scope: in; `w2-54-query-device`): The note added to the "Round 4" bullet of W2-54's README (lines 1056–1063) says the case was "revised 2026-11-09". The same sentence still ends "Both would be red if run now; … so neither was revised". In the CTO's run at `8bb8182f1` both cases passed.
Ordinary work: yes, because readers meet the two statements side by side.
Consequence: other. Documentation only.

**F5** (scope: out; `w2-54-query-device`): In a run of both shared-GPU cases, `gpu_project` is module-scoped. When the module is set up, it captures the session's cache folder (W2-54 `conftest.py:83-96` gives per-case folders only to function-scoped users).
- So once the first case has asked `QUESTION`, the second case's read is served by the machine-wide cache. The query server's `/api/ps` then shows what earlier reads left, not this case's read.
- The case still fails closed: an unloaded model gives an empty list and a red, and a CPU or split placement is red.
- This is probably also why the first case passed in the CTO's run although the README expected red: its "cold" reads clear only the tree's cache.
- This was there before this revision.
Ordinary work: yes, because a normal `-m shared_gpu` run runs both cases in order.
Consequence: other. The case proves where the model sits, not that this read reached the query server; a wrong placement never passes.

**F6** (scope: out; `w2-54-query-device`): W2-54's KPI 5 line (`.tickets/DAEO-0rfi.md:36`) still says "on whatever device it reports the model on". It was written under DEC-1033, before DEC-1065 (1). The code refuses a CPU vector and this case asserts the GPU, so the case is stricter than the KPI's words but matches the decisions. The line could cite DEC-1065 (1) at W2-54's next ticket edit.
Ordinary work: yes, because someone reading only the ticket would expect a CPU query server to pass.
Consequence: other. At worst a red that the decisions call correct.

```verdict
{"kpis": [{"kpi": "w1-19-vector-cache", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "w2-54-query-device", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F6", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```
