task: DAEO-mb2t (W2-124), independent audit (STANDARD), one round, read-only
status: DONE
work_completed: Ran the sandbox check. Traced S1–S5, F1 and F2 to the code and its own tests, and probed each with planted projects and stand-in embedders. Ran 31 rows of the 20 revised earlier cases against 21 deliberate breaks, one behaviour at a time, on a copy of the tree in my TMPDIR (case 9 is stated only). Checked the four commits of the ticket. Verdict: PASS.
files_changed: none. `git -C /home/usain/gov-os-worktrees/W2-124 status --porcelain` is empty; every probe file was in TMPDIR and has been removed.
evidence:
- **Sandbox check:** (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-mb2t` failed with `OSError: [Errno 30] Read-only file system`, and no file exists. (b) `git hash-object -w --stdin` gave `1ae28402a109…` (exit 0); `git update-index --refresh` exited 0.
- **Identity:** `printenv` gave `independent-auditor`, `DAEO-mb2t`. HEAD is `7a3aecb38fb56260569b3acafbf0e089fd043499`, as expected.
- **No model processes:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing.
- **TMPDIR:** 115M and 9,639 inodes at the peak; 192K after clean-up.
- **The diff:** the two-dot `diff w2/integrate 7a3aecb38fb5` shows 74 files, because integrate has moved on since. I used the three-dot form (merge base `95c957ae9`), which gives the ticket's 28 files.
- **Baseline:** all 30 revised rows pass on the unbroken copy: 27 in 57.8 s, plus 12 in 0.86 s re-run with `--optin=lifted --optin=breadth`, because the conftest had deselected 3 rows.
- **Break runs:** each break was applied by `brk.py` and checked to match exactly once; `drive.sh` then ran the cases through `heavy_slot.sh`. The red/green results are in the tests table.
- **probe_a (S1, S2, S5, F1), CLI on planted projects:**
  - Embedded namespace, embedder unavailable: exit 1, `REBUILD_FAILED` and `store: semantic` printed, no warm-base record.
  - Same project with `--no-embeddings`: exit 0, ok.
  - Namespace not embedded, embedder unavailable: exit 0, `requested: false`.
  - No path map: exit 0, `complete: false`, `not_built` names lexical and codeintel.
  - Healthy embedder: exit 0, 3 vectors, record written.
  - Embedder that hangs: exit 1, `REBUILD_FAILED`, `store: semantic`, after 221 s.
  - No `.gitleaks.toml` with `--no-embeddings`: exit 0, `complete: false`, `not_built` names lexical with the reason.
- **probe_b:**
  - Fresh part-way embedder: exit 1, `REBUILD_FAILED`/`semantic`, 32 of at least 36 vectors left, no record.
  - `rebuild_gate.semantic_failure` on 11 planted results: fails for absent, `null`, not a dict, error envelope, `not_recreated`, and a string `"false"`; passes only `recreated` and `requested: false`. This is the same rule as `rebuild_semantic_check.py`.
  - `close.batch._rebuild` on a planted partial result: `GovError REBUILD_FAILED semantic planted`; on a complete result: ok.
- **rebuild_slot.sh** with `GOV_REBUILD_PYTHON` pointing at a stand-in that prints the envelope: semantic `not_recreated` gives exit 75; `null` gives 75; `recreated` gives 0; `requested: false` gives 0.
- **probe_c (S3, F2), `stages._RefreshFirst`:**
  - A semantic refusal puts the finding `SEMANTIC_NOT_RECREATED` (reason, `gov rebuild`) in the committed record and in the report, and nothing is raised.
  - A lexical refusal, or a semantic refusal with no lexical store: the record is committed, then `ADOPT_INDEX_REFRESH_FAILED` is raised.
  - A failed batch: committed with no rebuild.
tests:

| case | break applied | red under the break |
|---|---|---|
| 1 mismatch | pin check skipped (`if False`) | yes: ok:true where REBUILD_FAILED was expected |
| 1 mismatch | refusal reason without a code | yes |
| 2 unpinned ×3 | `refused = None` after `_pin` | yes ×3: no `…_UNPINNED` |
| 2 unpinned ×3 | no code | yes ×3 |
| 3 not listed | refusal without a code or model name | yes |
| 3 not listed | no code | yes |
| 4 unreachable | no code | yes |
| 4 unreachable | lexical flipped to not_recreated | yes: "keyword index is still built" |
| 5 CPU | device check skipped | yes: ok:true over CPU vectors |
| 5 CPU | no code | yes |
| 6 secrets | cache `remembered()` always True | yes: canary in `lexical_fts_content` |
| 7 stale | search raises on a stale index | yes |
| 8 stale | search raises on a stale index | yes: traceback |
| 9 latency | stated (local_only; diff reviewed, budget lines untouched) | stated |
| 10 timings[full] | `semantic_s` key dropped | yes |
| 10 timings[full] | semantic stage untimed | no (see L-2; not a revision defect) |
| 11 digest | nondeterministic field in semantic | yes: "built different stores" |
| 12 W2-116 reindex | vectors deleted when model-less | yes: "3 vectors before, 0 after" |
| 13 W1-41[full] | note and words removed (`note2`) | yes |
| 13 W1-41[full] | note only (words remain in the reason) | no (expected) |
| 13 W1-41[full] | code index differs for a non-embedded project (`codeintel2`) | no (L-1); the sibling row `[…-no-embeddings]` turns red |
| 14 ×2 | link switched on a failed build | yes ×2 |
| 14 ×2 | warm-base record written on refusal | yes ×2 |
| 15 | vectors deleted when model-less | yes |
| 16 ×6 | words dropped | yes ×6 |
| 16 Embedded ×2 | `embedding_policy` matched case-insensitively | yes ×2 (the other 4 rows are not about case; green as expected) |
| 17 ×6 | warm-base record written on refusal | yes ×6 |
| 17 seeded ×3 | seed not performed | yes ×3 (unseeded rows green as expected) |
| 18 | cut kept only when available | yes |

discoveries:
- With no embedder, adoption's A6 refresh now stops at the semantic check, so the code index is not refreshed and the compaction does not run. The finding names only the semantic store (L-3).
- A project whose path map embeds, that has no `.gitleaks.toml`, fails a full rebuild with `REBUILD_FAILED`/`semantic` and the reason ".gitleaks.toml cannot be read". It is not ok with `not_built`, because S1 takes precedence over P2 (b); this fails closed. S5's own case uses `--no-embeddings`.
- The conftest deselects some rows that are named by node id unless the run opts in.
risks: none blocking. The hang case takes about 221 s per run (three tries of 60 s).
lessons: A break has to reach every place a guarded value appears. Removing the note alone left case 13 green because the words also appear in the reason; only `note2` showed the assertion still bites.
proposed_decisions: none
unresolved: none
recommended_next_action: READY on the verdict. Record L-1 to L-3 as rows; none needs a round.

**Refusals met:** the Write tool was refused once for a file in TMPDIR (as EMG-common.md expects). After that I wrote probe files by Bash `printf` into TMPDIR, the route EMG-common.md prescribes, with no here-documents as the brief requires. Nothing was retried in the same form. No guard, sandbox or hook refusals otherwise.

**Classification:** 3 findings, all low and non-blocking (0 in scope + ordinary work + fails open/loses work); no round proposed.

**Findings**

- **L-1 (low), case 13.**
  - *What was done:* the full-mode row of `test_the_rebuild_says_no_namespace_is_embedded` now compares the stores only over those the refused reference built. That is lexical and semantic, because the code index runs after the semantic check.
  - *What happened:* with a break where the code index comes out differently only for a project with no embedded namespace, the revised row stays green; the original assertion compared all stores. The unrevised sibling row `[…-no-embeddings]` does turn red, so a code-index regression that hits both modes is still caught. Only one confined to full mode is not.
  - *What should have happened:* to keep the full comparison, the reference could be given a healthy stand-in embedder and every store except semantic compared.
  - *Judgement:* the case keeps its point (ok, exit 0, lexical recreated, the words); one comparison is narrower.
  - Ordinary work: no, because a code-index regression that depends on both the embeddings flag and the absence of an embedded namespace needs a contrived coupling. Consequence: other.
  - *Would reverse it:* a code path in which the code-index outcome depends on the embeddings mode for projects with no embedded namespace.
- **L-2 (low), case 10; not a revision defect.**
  - *What happened:* when the semantic stage is not timed, the case stays green, because `Watch.timing()` fills an untimed stage with 0. This was true before the revision as well; the case asserts the keys, the numbers and the record. The revision makes it stronger: the full row must now actually recreate the semantic store.
  - Ordinary work: yes, because removing a stage timer is an ordinary edit. Consequence: other.
  - *Would reverse it:* the original case asserting that the semantic stage took more than 0 s.
- **L-3 (low), S3; out of scope.**
  - *What happened:* adoption with no embedder finishes A6 with the semantic finding, but the refresh stopped before the code index and the compaction (commit `461d03775`). The report's stores have no codeintel entry, and the finding does not say this. Later stages do not depend on it: `_importers` builds the code graph itself. The command in the finding, `gov rebuild`, repairs all of it.
  - Ordinary work: yes, because this is exactly S3's scenario. Consequence: other.
  - *Would reverse it:* a stage or tool after A6 that reads the code index and expects it refreshed.

**What I probed and found sound:**
- F1 across unavailable, hung and part-way embedders, the seed path and the integration path. There is no ok answer, no warm-base record and no link move over a partial store.
- The gate rule is identical to `rebuild_semantic_check.py` and fails closed on malformed input.
- The close's own rebuild refuses a partial result.
- In adoption, any refusal other than the semantic one still fails as `INDEX_REFRESH_FAILED`, after the record's commit.
- In the revision commit, only the 13 listed files changed, each change carries `Rewrite-Reason: DEC-1027 C`, and no assertion was dropped. The latency helper `_tiers` is used only by case 9.
- Commits: `Task: DAEO-mb2t` on all four. Roles match their paths (engineer for `src/` and its unit tests, test designer for the tests). `Implements:` is within `sources:`. Every path is in `allowed_paths`, plus the designer's own `tests/acceptance/W2-124/`.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": [{"id": "L-3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": [{"id": "L-1", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "L-2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F2", "verdict": "pass", "findings": []}]}
```

```verdict
ticket: DAEO-mb2t
head: 7a3aecb38fb56260569b3acafbf0e089fd043499
verdict: PASS
blocking: none
findings: L-1 (low), L-2 (low), L-3 (low)
revised_cases_checked: 31 of 32 rows run against a break (cases 1-8, 10-18) / 1 stated (case 9, local_only)
```