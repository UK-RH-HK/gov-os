# D-10's red-fix list: the review of W2-92's planted path map (W2-92, DAEO-n0wb)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-W2-92-review.md`; branch `w2/W2-92-d10-tests at cc128cf3b`; reviewer log `/home/usain/gov-os-worktrees/W2-92-d10-tests/.gov-runtime/scratch/lead/log/D10-W2-92-review.json`.
- verdict.py: READY (no blocking finding).

I found nothing wrong with the revision. The KPI `w2-92-planted-map` passes with no findings, so it is READY.

**Sandbox check (Step 0):** passed.
- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-n0wb','w').write('x')"` was refused with `OSError: [Errno 30] Read-only file system`, as required.
- (b) `echo sandbox-trial | git hash-object -w --stdin` returned `1ae28402a109c3397a44b19239a00adfa9472eb0`, and `git update-index --refresh` exited 0.

**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` printed nothing, of mine or anyone's.

---

**task:** DAEO-n0wb (W2-92), D-10's red-fix list. An independent, read-only review (role independent-auditor) of `cc128cf3b`: `adec4718a..cc128cf3b -- tests/`, KPI `w2-92-planted-map`.

**status:** DONE

**work_completed:**
- Read the diff and the whole of `w2_92_support.py`, plus `conftest.py` and the tests for unchanged, code route, fail-closed, hop, stated links, speed, drift and the S11 `gov links` case.
- Traced every read of the path map on the paths these cases call.
- Checked the new planted map against `gov`'s own loader and the kernel JSON schema.
- Ran the W2-92 folder read-only.
- Built the planted project twice, once with the old map and once with the new one, and compared the `test_u1` bundles with their pins.

**files_changed:** none, in any tree. Step 0's `hash-object -w` left one unreferenced loose blob (`1ae28402a109…`) in the shared object store, as the brief requires.

**evidence:**
- Reads of the map, by `file:line`:
  - The role filter `role_paths.caller` returns no filter at `src/gov/util/role_paths.py:503-504` when no role is named. No case passes `role=`, and `Api.env` sets no `GOV_ROLE` or `GOV_TICKET`.
  - `evaluation_sets` is read only by the guard (`src/gov/guard/reads.py:226,238`) and the measure (`src/gov/retrieval/measure.py:476`).
  - The other dropped blocks are read only by `close/`, `check/citations.py` and `retrieval/measure.py`.
  - A system's `where`/`reason` is only validated (`src/gov/config/loader.py:220-242`).
  - `gov links` reads only the map's comments (`src/gov/links/check.py:638-639`). Both the old and the new planted map are `yaml.safe_dump` output, which has no comments.
  - Lexical search reads only `namespaces` (`src/gov/retrieval/lexical.py:159-170`). The register is read at `src/gov/retrieval/retrieve.py:107-113`, `lexical.py:281-286` and `src/gov/store/loader.py:150-163`.
- Validity: `gov.config.loader.validate` passes. The kernel JSON schema (`path-map.schema.json` with `common.schema.json`, Draft 2020-12, jsonschema 4.10.3) gives 0 errors.
- Workaround: the Write tool was not granted for a scratch script in the sandbox TMPDIR. I ran the analysis as inline `python3 -B -c` commands instead, which write no file.
- Retry: the sandbox's bwrap setup failed once, because another worktree's `commondir` (W2-149-f11-tests) had vanished. The retry ran.
- Scratch folder `/tmp/gov-launch-erpyqfr1/claude-1000/rev-n0wb`: 6.4M and 561 inodes at its peak, removed at the end.
- `git status --porcelain --untracked-files=all` was empty after the runs.

**tests:**
- **The folder, read-only:**
  - How it ran: through `heavy_slot.sh`, with `-p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`, an empty HOME, `PYTHONUSERBASE=/home/usain/.local`, the branch's `src`, my own TMPDIR and `PYTHONDONTWRITEBYTECODE=1`.
  - Result: **114 passed, 30 skipped in 59.44 s.** The exclusion deselected nothing (144 collected).
  - The 30 skips are every case that uses the planted project with code (code route 7, fail-closed 6, record route 8, unchanged 9). The root conftest keeps `codebase-memory-mcp` off `PATH` by default, so those cases skip.
- **Old map against new map:** the planted project with its store, no code index, the tool absent, this branch's code.
  - Old map: `test_u1`'s plain, batched (and the continued page), unknown id and ticket cases equal their pins. **Unknown symbol does not.** Its evidence is `governance/project/path-map.yaml`, and it differs in batches, budget, evidence, expansions, merge and rerank.
  - New map: **all five cases and the continued page equal their pins.** Unknown symbol gives `[]`.
  - Lexical order: the old map adds `path-map.yaml` only for "who calls w92_leaf" and "who calls w92_leaf under DEC-301". The order is identical for `w92_leaf`, the four "what does … say" questions and the title question.
- **Not run by me:** the 30 skipped cases with the real tool. The CTO's run outside the sandbox (144 passed at `3e983d544`) is the evidence for them.

**discoveries:**
- The red reproduces with no code-graph tool at all: lexical search alone put the old map into the bundle for "who calls w92_nowhere". So the cause is the planted map, not W2-92's code route.
- The old map was also noise in the bundles of the "who calls …" questions (`test_c1` to `test_c4`, `test_u3[new routes]`, `test_u4`, `test_f3`). None of their assertions looks at it, and the new map removes it.

**risks:**
- The planted map now carries only the required top-level keys. If the kernel later makes another top-level key required, `Api.build` stops with CONFIG_INVALID. That failure is loud and closed, and the fix is one line. It is not a finding.
- The values still copied from the live map are closed words: `code_intelligence` enabled with `languages: [python]`, the policy strengths, and the statuses `minimal`/`absent`. None of them is a word any question uses.

**lessons:** A planted project that copies a live governance file brings that file's free text into the planted index. Copy closed values only, as this revision does.

**proposed_decisions:** none

**unresolved:** none

**recommended_next_action:** READY by the verdict below. The CTO takes `cc128cf3b` with D-10's red-fix list. No further round is needed.

---

## Answers to the checks

**1. No expectation lowered: yes, none is lowered.**
- **Dropped:** `decision_citations_base`, `acceptance_exemptions`, `close_timeout`, `accepted_reds`, `load_sensitive`, `evaluation_sets`, `evaluation_families`, `role_paths`, `sets_root_hidden`, `session_hidden` and `write_refused`. Each system's `where`/`reason` is replaced. `retrieval_authority` was already removed before this revision.
- **Not read by these cases:** none of the dropped blocks is read on any path these cases call (see the evidence).
- **Unchanged reads:** what the cases do read is the same as before: the `everything` namespace, `decision_register`, and `capabilities` copied whole.
- **The only channel left:** the map's own text in the planted index. The new map's content is a subset of the old map's, so it can only remove matches, and it removes them only from the "who calls …" answers.
- **By case family:**
  - The marina (`links_corpus()`), the hop, stated links and status compare the integrated code with head on one marina, judged by record text. Stated links read only the new store tables, built from front matter and the register.
  - Speed has no timing assertion, and `s6c` compares the base code with head on one project.
  - Verbless labels read the register text, and `gov links` reads only comments.
  - Drift reads a document in this repository, not a planted project.
  - The code-route, fail-closed and record-route cases make positive assertions about planted spans and texts, and negative ones about the request log. `f1`'s `LEXICAL_PATHS` comes from `corpus()` and is intersected with the bundle.
- **Not weaker than designed:** no case passes for the wrong reason, and none tests less than it was designed to. The pins were recorded when the live map had no "calls", and the new map restores that condition.

**2. The premise kept: yes.** The pins (`TODAY`) and `CASES` are untouched by the revision. My rebuild matches every case item for item with the new map. `test_u2` still checks the bundle against the live fused order on the same project.

**3. Validity: yes.**
- **Schema and loader:** the planted map passes both checks above.
- **Systems:** the `minimal` ones get `where: ["**"]` and the `absent` ones get `reason: absent`, which is exactly what the schema requires.
- **Namespace and register:** the `everything` namespace and the register path are unchanged.
- **Build:** `Api.build` succeeded for the planted project with code (my rebuild) and for the marina, verbless-labels and speed projects (the 114 passed).

**4. Trailers: yes.**
- Present: `Task: DAEO-n0wb`, `Implements: DEC-1109` (its item (2) restarts the work "before D-10"), `Role: independent-test-designer`, `Rewrite-Reason: DEC-1106 (3), DEC-1108 (5): …` and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Scope: one commit, changing only `tests/acceptance/W2-92/README.md` (+5) and `tests/acceptance/W2-92/w2_92_support.py` (+17 −4). The merge `3e983d544` does not touch that folder.

## Findings

None.

```verdict
{"kpis": [{"kpi": "w2-92-planted-map", "verdict": "pass", "findings": []}]}
```
