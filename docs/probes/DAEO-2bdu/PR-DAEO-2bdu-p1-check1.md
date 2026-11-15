---
type: probe
task: DAEO-2bdu
round: run 7 narrow check 1 (DEC-1154; DEC-1178 (3)(b))
reviewer_session: f56d15cb-70c4-42df-bc78-47d3dbb04d52
implementer_session: eng-6-3 2cc8047c-1aca-4a3e-bb43-5cb15cb0ed85 (S24-S27); eng-7 307b58af-d219-430b-9c99-c15e649b5771 (S24 looked); eng-8 1f439f53-4151-4444-923f-b87e262b001c (P1-1 fix); test designer td-9 ffe82e2b-f6f6-4b38-a9ab-426e56c14804, td-10 a3f752df-a540-4c4e-b895-5ad1784cfd8b, td-11 2e82e9d3-fdc8-448c-a3bd-ab62a7838a90, td-12 cdc0bc46-6b5b-45e1-a491-7c5bb3ae2d54
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: fail
probed_commit: ef9c773c30365081e634d05a9b68c6eb7c4dd446
decisions_applied: [DEC-1154, DEC-1178, DEC-1164, DEC-1010, DEC-136, DEC-820, DEC-1052, DEC-801, DEC-808, DEC-096]
---

# Probe record: W2-88 (DAEO-2bdu), run 7's narrow independent check (S24 to S27): FAIL on S27 (P1-1)

The ticket was reopened on 2026-11-14 under DEC-1164 (18) on the owner's DEC-1178 (3)(b) and (4) for S24 to S27. This record is the narrow independent check DEC-1154 and DEC-1178 (3)(b) call for, of the change a23678e27..ef9c773c3. Its re-check, of P1-1's fix, is `PR-DAEO-2bdu-p1.md`.

## The lead's judgement and triage
- **Who checked.** A fresh, read-only Independent Auditor (`f56d15cb-70c4-42df-bc78-47d3dbb04d52`, claude-opus-5-5, effort high, class C2), started through `launch_worker.sh` / `gov launch` under the OS sandbox on 2026-11-14, its brief carrying `governance/project/briefs/JUDGEMENT.md` word for word (`.gov-runtime/scratch/lead/briefs/nc-3.md`).
- **The verdict stands as FAIL** (never decided away). S24, S25 and S26 pass. S27 fails on P1-1 (in scope, ordinary work yes, fails open): a blocker. Triage: fixed in the same run as fix iteration 3 (eng-8, d766514fd), after the test designer's case for it (td-12, e66a9cb58, DEC-136); re-checked in `PR-DAEO-2bdu-p1.md`.
- **The lead's packages, confirmed by the checker as outside the ticket's paths:** (1) the pool, walls template and MEMORY-AUDIT-1 briefs are not shipped in the wheel or under `template/` (S24's full-line case stays red); (2) S25's cause is in `src/gov/codeintel/__init__.py` (the tool's 100,000-row cap); (3) W2-23's `tests/unit/adopt/test_safety.py::test_s1_a_stage_writes_nothing_over_an_untracked_file` meets S26's refusal first.
- **The lead's verification at ef9c773c3:** `gov accept W2-88`: 256 passed, 2 failed (success-24's full-line case, package (1); the `real` redis case, over its 240 s limit under load), `.gov-runtime/scratch/lead/log/accept-7.txt`; scoped lead_verify RED 6 of 6,835 (package (3); package (1); W1-28 and W1-50 on two whole-tree copies, revised by td-11 a4eff2312; the W2-112 reranker case and the redis `real` case, load-sensitive), `.gov-runtime/scratch/lead/log/verify-7.txt`. The lead's redis re-run: `CODEGRAPH_TOO_LARGE`, exit 1, 41,086 nodes and 142,983 edges, HEAD unmoved, 75 s, peak 826,532 kB.

## The checker's return (unchanged)

task: DAEO-2bdu (W2-88, "Memory for any repository"), the narrow independent check of run 7 (S24 to S27) at ef9c773c3
status: DONE. S24, S25 and S26 pass. S27 fails on one blocker (P1-1): batching lets a secret through that the one-per-file form leaves out.
work_completed: Step 0; read the diff a23678e27..ef9c773c3 and the seven commits' scope and trailers; built a release-form wheel and a copier kit from a planted tag, and ran A9's shipped reads from the wheel; probed S26 edge cases on planted repositories; compared S27's batch against the one-per-file form on 324 ordered file pairs with real gitleaks, then end to end against a23678e27's code; read the lead's redis logs; ran the four run-7 unit-test files.
files_changed: none (`git status --porcelain` empty at the end)
evidence: all of it under my TMPDIR `/tmp/gov-launch-w2bzta_e/claude-1000/`: the scripts `p/s27_pairs.py`, `p/s27_e2e.py`, `p/s27_lines.py`, `p/s26_edges.py`, `p/s24_build.sh`, `p/s24_probe.py`; the S24 build in `s24/`; the unit-test output `unit.txt`
tests: the four run-7 unit-test files, through heavy_slot with `-m "not local_only" -k "not real and not green_here and not time_limit"`: 39 passed, exit 0 (the filter deselected none). I re-ran no acceptance cases; the lead's run is `run7-acc.txt`, and `accept-7.txt` was still empty when I finished.
discoveries: P1-1. When a file ends in a bare key (`password:` or `token =`), gitleaks' generic-api-key match runs across the blank-line separator into the next file in the batch and swallows that file's own secret. The finding is put back only on its StartLine (the first file), so the second file is judged clean and recorded clean in the reuse record.
risks: The wrong "clean" verdicts go into the reuse record that every scan shares (the record under HOME). I saw the base code (a23678e27) read the head's wrong result back from a shared HOME. A fix needs to stop those records being reused (for example by changing `_FORM`).
lessons: The batch's premise that "no match runs from one text into the next but across blank lines" is false for rules that use `\s`. The tests' "split secret" case checks only the false-positive direction.
proposed_decisions: none
unresolved: My own direct S25 call with the stand-in failed in `codeintel`'s set-up (my harness, not the code). I relied on the unit cases with the stand-in tool (they pass, undo checked) and the lead's real redis run.
recommended_next_action: The engineer fixes P1-1 in `src/gov/secrets/__init__.py`, in the ticket's paths: put each finding back on every file its StartLine to EndLine covers, and change `_FORM` so run 7's records are not reused. The test designer adds the shadowing pair as a case. The S27 narrow check is then re-run; S24 to S26 need no new round.

# W2-88 (DAEO-2bdu): narrow independent check of run 7 (S24 to S27)
probed_commit: ef9c773c30365081e634d05a9b68c6eb7c4dd446
base: a23678e27

## Sandbox and identity
- Step 0 (EMG-d4b-launched.md):
  - (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-2bdu` failed with `OSError: [Errno 30] Read-only file system`, as it should.
  - (b) `git hash-object -w --stdin` and `git update-index --refresh` both worked (exit 0).
- `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-2bdu`.
- HEAD was ef9c773c3 and the status empty, at the start and at the end.
- `ps` showed no ollama or llama-server process, at the start and at the end.
- Refusals during the check:
  - The guard refused once a `for c in …; do git show $c` loop ("cannot say whether a revision holds the hidden part"). I used one `git log a23678e27..HEAD` instead.
  - A Monitor call needed approval and was refused. I waited with a background Bash command instead.
  - Neither call was repeated in the same form.
- My own breach of the brief: several early commands wrote to `$TMPDIR/...` (a shell variable as a write target). From the S24 build on I used literal paths. Every write stayed inside my TMPDIR.

## S24 to S27
| item | met | file:line | how probed |
|---|---|---|---|
| S24: one resolver, three places in order, never `parents[3]` as the root | met | src/gov/adopt/fabric.py:55-87 | wheel built from `git archive` with `pip wheel --no-deps --no-build-isolation --no-index`, installed into a `--system-site-packages` venv, run with no PYTHONPATH from outside the tree. `gov.__file__` is in the venv and `_source_tree()` is None. |
| S24: `SHIPPED_FILE_MISSING` with `details.file` and `details.looked`, never empty, never a place not looked at | met | fabric.py:76-87 | From the wheel: the pool, the walls and the briefs are refused, with `file` = rel and `looked` = the search description only. No `<root>/<rel>` appears for a rel outside `template/`. |
| S24: every shipped read goes through the resolver, at run time, never at import | met | fabric.py:93,186,214-224,275; memory_sets.py:136; safety.py:62; assess.py:144 | Grep finds no `parents[3]` or `GOV_OS` in src/gov/adopt. Importing fabric, memory_sets and safety from the wheel succeeds. The walls and briefs are checked before `install` (fabric.py:785-786). |
| S24: kit from copier (planted tag, `--skip-tasks`) | partly (the lead's package) | — | Found in the kit: both skill folders, brief.md, role-cto.md and `.gitleaks.toml`. `read_standard` refuses `SHIPPED_FILE_MISSING` for `governance/project/retrieval.yaml`. The wheel holds none of the pool, walls or briefs. |
| S25: over the cap gives `CODEGRAPH_TOO_LARGE` with nodes, edges, cap and tool; at or under the cap, as today; another failure gives `FABRIC_INCOMPLETE` | met | fabric.py:494-527, 600-603 | Unit cases with the stand-in pass, undo checked (`test_w2_88_f1.py:98-117`). The lead's redis re-run gives exit 1, `CODEGRAPH_TOO_LARGE` (41,086 nodes, 142,983 edges), and `.before` and `.after` are identical. |
| S26: MA and A0 refuse first, with path, source, line and pattern; tracked paths not refused; no `add -f`; no ignore file edited | met | safety.py:80-127; stages.py:62,154 | Planted repositories: a whole-folder rule `.claude/`, a nested `governance/.gitignore` with `*.md` (line 2 named), a `!` re-include (goes on), `.gitleaks.toml` ignored, and a clean repository. The acceptance cases cover `.gitignore`, `info/exclude`, `core.excludesFile` and a tracked path. |
| S26: the list covers what A0 to A9 commit | met | safety.py:80-97 | Checked against `stages.a0` to `a2` (the A0 files, the coordination ticket and roster, A2's packages), `project.record_path`, `lite_gates`, `legacy.CIT_E` and `fabric.kernel_targets`. A6's targets and A8's imports come from proposals and are documented as not known at the start. |
| S27: the same verdict per file as the one-per-file form | **not met** | src/gov/secrets/__init__.py:301-334 | 324 ordered pairs with real gitleaks 8.30.1 give 4 mismatches, all of them P1-1. End to end: a23678e27 leaves out `config/11-prod.env`; the head keeps it. |
| S27: parallel batches, at most `_workers()` at once; public names kept; 10× | met | secrets/__init__.py:473-478; evidence.md:499-506 | One batch at a time per worker. Run 7's figures are 60× at budget 1 and 14.3× at budget 7. |

## What I probed and found sound
1. Scope of the change:
   - The five engineer commits touch only the ticket's `allowed_paths`.
   - The test designer's 0841cfb3c and 7646ebe89 touch only `tests/acceptance/W2-88/`.
   - Every non-merge commit carries `Task: DAEO-2bdu`.
   - Every `Implements:` id (DEC-954, CAP-44.b, CAP-44.f, CAP-44.g, CAP-17, CAP-20) is in the ticket's `sources:`.
2. S24 from the installed wheel (`p/s24_probe.py`): the imports succeed, the template files resolve to `<project>/X`, and `fabric.STANDARD` and `safety.TEMPLATE_GITLEAKS` raise `AttributeError` that names `SHIPPED_FILE_MISSING` (not a crash at import).
3. Older readers still work: `fabric.STANDARD` (through module `__getattr__`) and `departures(doc)` with one argument, as used by `test_w2_88_run4.py` and `standin_b1`.
4. S25: the refusal is raised inside `_stage`, after `install`, so `a9`'s `except BaseException` runs A9's undo (fabric.py:789-793). The unit case asserts nothing is left written.
5. S26: `check-ignore -v -z --stdin` is parsed four fields per record and `!` patterns are dropped. MA calls the check right after `require_commit`; A0 calls it first in `a0`. No `add -f` appears anywhere.
6. S27 directions that hold: a file a finding names is re-judged alone, so the commit-hash exemption stands; an unreadable report or a finding on a line no file owns sends the whole batch to the one-per-file form. In the 324 pairs, CRLF, `\r` only, form feeds, blank lines, a missing final newline and an empty file all gave the same verdicts.
7. README map rows success-24 to success-27: all 22 named node ids exist as `def test_…` in their files.
8. Unit tests: 39 passed (`unit.txt`).

## Findings
**P1-1** (success-27, severity **blocker**): a secret is let through when a neighbouring file in the batch ends in a bare key.
- **What is wrong:** File A ends with a bare generic key, such as `password:` on its last line or `token =` with no value. The next file in the batch, B, starts with a secret that only gitleaks' `generic-api-key` rule catches (for example `API_KEY=<value>` on its first line). gitleaks then reports one match from A's line 4 to B's line 7: its `\s` classes cross the blank-line separator, and the match swallows B's own match. `_scan_batch` puts the finding back only on its StartLine (A). A is re-judged alone and is clean. B is in no owner set, so it is judged clean, kept as indexable, and written to the reuse record as `scanned` clean.
- **Reproduce:**
  - Pair probe: `python3 -I p/s27_pairs.py s27root` gives `MISMATCH ['tail_key', 'generic_env'] batch [False, False] alone [False, True] owners [0]`, plus 3 more variants.
  - End to end: `p/s27_e2e.py` on 12 planted files, each run with its own HOME. a23678e27 keeps 11 of 12 and leaves out `config/11-prod.env`; the head keeps 12 of 12.
  - Line span: `p/s27_lines.py` shows `('generic-api-key', 4, 7)`, with A on lines 2 to 6 and B starting at line 7.
- **Behaviour it should have:** The one-per-file form's verdict. A finding should be put back on every file its StartLine to EndLine covers, or the file after an owner whose alone scan comes back clean should be judged alone. Records written as clean by run 7's batching should stop being reused (a new `_FORM`). A test-designer case should plant this pair. A file a finding names is already re-judged alone, so the fix costs no speed.
- Ordinary work: yes, because it needs no construction: a config file ending in an empty `password:` key, followed in path order by a `.env` whose first line holds a key, is ordinary content in a repository being adopted (rare, but an accident, not a planted construction).
- Consequence: fails open (a file holding a secret is judged indexable, and the wrong clean verdict persists in the machine-wide reuse record).

## The lead's packages and known reds
- **(1) S24 full-line case:** correctly classified as outside the paths. From the wheel with the copier kit, I saw A9's first read (`read_standard`, then `shipped`) refuse `SHIPPED_FILE_MISSING` for `governance/project/retrieval.yaml`, and `shipped` refuse the walls and the briefs too. The wheel holds none of them. Shipping them needs `pyproject.toml` package data or new data files, and neither is in `allowed_paths`. The engineer's argument against putting the pool under `template/` (evidence.md:443-446) is sound.
- **(2) S25 cause in `gov.codeintel`:** correctly outside the paths (`src/gov/codeintel/__init__.py` is not in `allowed_paths`). Inside the paths, A9 names the cause, as the redis run shows.
- **(3) `tests/unit/adopt/test_safety.py::test_s1_a_stage_writes_nothing_over_an_untracked_file`:** correctly outside the paths (only `tests/unit/adopt/test_w2_88*` is allowed). The new `ADOPT_PATH_IGNORED` that the test now meets first is the behaviour S26 asks for.
- **The engineer's named risks:**
  - The first `looked` entry being a description, not a path: Ordinary work: yes, because every installed release takes this branch. Consequence: other (the message is clear).
  - A repository that ignores `.claude/` now refuses at MA and A0: Ordinary work: yes, because ignoring `.claude/` is common. Consequence: other (it fails closed, as the CTO's choice (b) intends).
  - The 36,000-file estimate assuming small files: Ordinary work: yes, because repository sizes vary. Consequence: other (only the time estimate is affected).

## Notes, not findings
- A tracked symlinked `.claude` makes the S26 check fail as `ADOPT_GIT_FAILED` ("pathspec … is beyond a symbolic link"), not `ADOPT_PATH_IGNORED`. It still refuses at once with nothing written. Ordinary work: no, because a tracked symlink at `.claude` is unusual. Consequence: other.
- `shipped` also tries the project's copy when a source tree exists but lacks the file; the interface says "else". This is harmless. Ordinary work: no, because a source tree is always complete. Consequence: other.
- From an installed release, A9 reads brief.md and role-cto.md from the project's own copy and writes them back to the same paths. Any edits the project made stand as "shipped bytes". This is by design ((2) of the interface). Ordinary work: yes, because every installed release does this. Consequence: other.
- `_source_tree` would also accept a Gov OS checkout that merely contains the venv, which could be a different version from the installed wheel. Ordinary work: no, because a venv inside a checkout on another branch is rare. Consequence: other.

```verdict
{"kpis": [{"kpi": "success-24", "verdict": "pass", "findings": []}, {"kpi": "success-25", "verdict": "pass", "findings": []}, {"kpi": "success-26", "verdict": "pass", "findings": []}, {"kpi": "success-27", "verdict": "fail", "findings": [{"id": "P1-1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]}], "overall": "fail"}
```
