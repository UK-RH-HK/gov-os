---
type: probe
task: DAEO-2bdu
round: runs 8 and 8b narrow check (DEC-1154, the CTO's --owner-named DEC-1154; DEC-1183, DEC-1185, DEC-893)
reviewer_session: 8321277d-e53f-4275-9d8b-7fbbff7c76cb
implementer_session: eng-9-3 96ca8eef-9d28-42b9-a5ab-cc8e71799087 (S27 revert, package 1, package 2 by type); eng-10-2 0318813c-322d-4381-837a-f60ec461ee37 (S28, step 6, GITLEAKS_MISSING); test designer td-13 98bb918c-c346-455a-869d-a3a99d88761e, td-14-2 53a8ccfe-b111-4079-92b8-97292583aa61, td-15 e2652b8f-cdf8-4557-a6b3-2bf2de424dd9
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: pass
probed_commit: f4e882ddbb22b87ab83309cc686999fc8f7e8c1d
decisions_applied: [DEC-1154, DEC-1183, DEC-1185, DEC-893, DEC-1156, DEC-1010, DEC-136, DEC-820, DEC-1052, DEC-1178]
---

# Probe record: W2-88 (DAEO-2bdu), the narrow independent check of runs 8 and 8b: PASS

## The lead's judgement and triage

- **Who probed.** A fresh, read-only Independent Auditor session (`8321277d-e53f-4275-9d8b-7fbbff7c76cb`, claude-opus-5-5, effort high, class C2, promoted by W2-184), started through `launch_worker.sh` / `gov launch` under the OS sandbox on 2026-11-15. The first launch (nc-r8, 00:56) was refused once: `review round 3 of DAEO-2bdu is refused: at most two review rounds (DEC-1010) ... needs --owner-named <DEC-id>`; the CTO decided the relaunch under DEC-1154 (a narrow independent check of changes the owner decided after the ticket's review), and it ran as nc-r8-2 with `--owner-named DEC-1154`. Step 0 held; the head was f4e882ddb and `git status --porcelain` was empty at start and end. Its tripwire changes were in W2-111's trees only (another ticket's lead).
- **The brief's base** was written `0821e85146b0` (a typing slip of the lead's); the reviewer used `0821e8514` (0821e85145a5), as stated in its check.
- **The redis copy's A9 at f4e882ddb** (S25's re-run and S28's figures; `~/gov-os-runs/W2-88/redis`, its record `governance/adoption/A9-memory-fabric.md` lines 4042-4046 and 5568-5572; log `.gov-runtime/scratch/lead/log/redis-a9-8b.*`): exit 0, `"ok": true`, 14:44.68 wall, peak RSS 838,032 KiB; the code graph 41,086 nodes and 143,008 links (the tool's totals: the stage refuses any gap), 1,977 pieces read, 0 from the record (a first read), `read_seconds: 493.893`.
- **The verdict stands as PASS** (no finding blocks: none is in scope, ordinary work and fails open or loses work). The triage:

| finding | severity | triage |
|---|---|---|
| R8-1 W2-187's unit test `tests/unit/adopt/test_w2_187_walls_act.py::test_with_no_scanner_on_path_step_6_holds_the_placeholder_for_the_operator` still asserts the gitleaks placeholder item 24 removed | major, non-blocking (it reddens the land's suite) | the CTO's path route, decided ~01:50 (8fed04d1f: allowed_paths gain the file): a fresh engineer revises only that case to `GITLEAKS_MISSING` with no slot (Rewrite-Reason: DEC-893, DEC-1156 (7)); one narrow re-check of R8-1 and R8-2 only, with `--owner-named DEC-1154` |
| R8-2 a refresh keeps an unchanged file's links whose target moved to a changed file (counts and ids still equal) | major, consequence other, non-blocking | to the CTO and the owner with the reviewer's options (a) the record stale when a link's source or target is missing from the fresh node read, (b) re-read unchanged files whose targets lie in changed files (S28's failure line forbids it today), (c) a named residual; the CTO decided (a) within S28 (~01:50): the record is stale, and every link re-read, when any link it holds has a source or target missing from the fresh node read; a unit case and a stand-in case reproduce the moved-target refresh; the same narrow re-check |
| R8-3 an unreadable grouped-count shape falls back to an unchecked whole read | minor, fails open, ordinary work no | a Wave 3 row (the CTO, ~01:50; reachable only by test_codeintel's stand-ins; the real tool answers counts as digits) |

The reviewer's check follows, unchanged.

# W2-88 (DAEO-2bdu): narrow check of runs 8 and 8b (DEC-1183, DEC-1185, DEC-893)
probed_commit: f4e882ddbb22b87ab83309cc686999fc8f7e8c1d
base: 0821e85146b0 (as briefed; it does not resolve. The commit is 0821e85145a543ffadf2f8b5339212784d00faa8, which was used.)

## Sandbox and identity
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-2bdu` failed with `OSError: [Errno 30] Read-only file system`; no file was left.
- (b) `echo sandbox-trial | git hash-object -w --stdin` worked (1ae28402a1…); `git update-index --refresh` exited 0.
- `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-2bdu`.
- HEAD was f4e882ddbb22b87ab83309cc686999fc8f7e8c1d at the start and at the end; `status --porcelain` was empty both times.
- `ps` showed no ollama or llama-server process.
- Limit: the sandbox refuses AF_UNIX sockets (`socket_creation failed with EPERM`), so the real tool cannot run in this session.

## The L8-1 rewrite
`git diff 0821e8514 2c2621dfc -- docs/probes/DAEO-2bdu/` changes only lines inside the two `verdict` fences. The KPIs, verdicts, finding ids (in order) and `overall: fail` are the same in both records. The values for RV1-1 to RV1-8 (round 1) and RV2-1 and RV2-2 (round 2) come from the records' own lines; I checked lines 88, 94, 105, 112, 117-140 of round 1 and 77, 90, 96 of round 2. The `no`/`other` values for RV1-9 to RV1-11 (round 1) and for every RV1 id in round 2 are not in the records. They are the lead's non-blocking fill-ins, and the commit body says so openly.

## What I probed and found sound
1. **S27 (b) revert.** `git diff a23678e27 HEAD -- src/gov/secrets/` shows only `_FORM = 4` → `6` and its comment (`src/gov/secrets/__init__.py:61`). `cache.engine(rules, _FORM)` (:192) and the reuse record (:543, :561, :575) use form 6, so nothing that forms 4 or 5 judged is reused. `_scan` (:268) receives only one file's chunks: `_forms(content)` of one text (:191, :198) or `_store(path)` of one store (:628-632). No path judges two files in one gitleaks process. The three batched-only cases carry `BATCHED_ONLY` with DEC-1183's reason (`test_w2_88_scan_speed.py:41`, :232, :249, :300); the others stay live. `tests/unit/secrets/test_w2_88_scan.py` passed.
2. **Package 1 (a).** All 11 files under `src/gov/_shipped/` are byte-equal to their sources (`cmp`). `indep-walls/` has the same six files in both places. Git modes match: `wall_hook.py` and `memaudit_cron.sh` are 100755. `pyproject.toml:18-32` declares each file as package data. `fabric.shipped` (`fabric.py:78-100`) looks in order at the source tree, then `<package>/_shipped/<rel>`, then the copier copy (for `template/` paths). Otherwise it refuses `SHIPPED_FILE_MISSING` with `looked`, which is never empty. `test_w2_88_p1_installed.py` builds the wheel the release way (`git archive` export, `pip wheel --no-build-isolation --no-index`, fresh venv) and passed, including S24 from the installed wheel and the executable check at :448. `p1_shipped_bytes` passed.
3. **S28 reader** (`codeintel/__init__.py:456-754`):
   - The totals come from the grouped counts.
   - Each label's path list is counted first (:491) and checked against that count (:497). A cut File list is read per holder by equality, with each piece counted (:508-552). A holder whose own list is cut, or that mixes string and other paths, is refused by name.
   - There is one equality-filtered piece per path, with its count first (:555-566). A piece that is cut or has duplicate ids is read by type within the file, each type counted and checked for distinct ids (:569-581). A (file, type) piece over 100,000 raises `GraphTooLarge` with the file (:476-477); A9's message names the file, type and count, with `details.file` (`fabric.py:507-522`).
   - Labels with no string path get label pieces (:585-592).
   - Across all pieces, the sum and the distinct ids must equal the total, else `GraphShort` names the duplicated pieces and the label gaps (:613-629). That maps to `FABRIC_INCOMPLETE` through `built: False` (`fabric.py:600-614`, :445-464).
   - Nodes are read per label, checked, and fall back to reads by path (:633-658).
   - The record is saved only after a pass (:742-743) and survives the re-index (:347-370). A stale record that fails the check makes everything be read again (:734-740).
   - Grep finds no `ORDER BY`, `SKIP`, `LIMIT`, `IN [`, `STARTS WITH`, string `>`, or `type`/`id` inside `WHERE` (see R8-3 for the whole-graph fallback).
   - `read_seconds` and the piece counts go into the record (`fabric.py:597`, :612).
   - The redis A9 at f4e882ddb exited 0 with `"ok": true` in 14:44 wall (`redis-a9-8b.*`).
4. **Step 6 (DEC-893).** `_cron` returns only `fabric.shipped(CRON, root)` and lets `SHIPPED_FILE_MISSING` through (`memory_sets.py:163-169`); the `<path to Gov OS>` fallback is gone. With no gitleaks, `_step_6` writes prose that names `GITLEAKS_MISSING`, gives no cron line, and has no `<…>` slot (:172-182). A9's record names it (`fabric.py:840`). A9 does refuse earlier (`REBUILD_FAILED`) when the scan is on and gitleaks is missing. With the scan off by configuration (DEC-1045), A9 reaches step 6 and writes GITLEAKS_MISSING, never a slot. No code path writes `<path to gitleaks>`. The revision in 81a85ce4b changes only the `none-on-path` branch, and the `planted` branch is unchanged. `test_w2_187_s11_cron.py` and `test_w2_88_cron.py` passed; the latter checks the executable bit at :32.
5. **a5144a3ec resolution.** `walls_act` keeps `repo`/`_toplevel`, `_gitleaks`, `PUSH_ORDER` and step 6 together with `root`/`fabric.shipped(WALLS, root)`. No `parents[3]` remains in `src/gov/adopt/`; the only `parents[1]` is the package folder, `fabric.py:75`.
6. **Tests (item 7).**
   - e504e50c6: the S27 skips; the shipped bytes; the installed wheel; `test_safety` still asserts `WOULD_OVERWRITE` and the file unchanged (:105), with the plant now not ignored.
   - 84541cc87: the S28 cases (a)-(g) plus a guard holding the stand-in to items 13-14 (`test_w2_88_f1_codegraph.py:424-448`). The stand-in refuses over 100,000 rows, `IN`, `STARTS WITH` and functions in `WHERE`; answers a string cursor with 0 rows; answers `SKIP`/`LIMIT` short; and has the size cut. That matches the probes (f1-probe5b to 11).
   - Every `Rewrite-Reason` names a decision. I found no assertion weakened without need.
7. **Scope (item 8).** Each of the 8 engineer and orchestrator commits and the 3 test-designer commits carries `Task: DAEO-2bdu`. Every `Implements:` id is in `sources:` (DEC-954, CAP-44.b, CAP-44.f, CAP-17, CAP-20, DEC-1010, DEC-1112; the merge's DEC-1178, DEC-1101, DEC-1125). Every file is in `allowed_paths`, or is the test designer's `tests/acceptance/W2-88/**`.

## Findings
**R8-1 (success-22; major; non-blocking by the rules, but it reddens the land's suite).** W2-187's unit test `tests/unit/adopt/test_w2_187_walls_act.py::test_with_no_scanner_on_path_step_6_holds_the_placeholder_for_the_operator` (:52-55) still asserts ` GOV_MEMAUDIT_GITLEAKS=<path to gitleaks> `. Item 24's decided change made it red at f4e882ddb: `assert ' GOV_MEMAUDIT_GITLEAKS=<path to gitleaks> ' in 'GITLEAKS_MISSING'`. The acceptance twin was revised through the CTO's path route; this unit file was not, and it is outside this ticket's `allowed_paths`. Reproduce: run pytest on that node at HEAD. It should assert GITLEAKS_MISSING and no slot, revised through the same path route. Evidence that would reverse this: the file revised on integrate before the land.
- Ordinary work: yes, because any full or scoped suite run at the head runs it.
- Consequence: other (a red test that blocks the land's green run; no behaviour fails open).

**R8-2 (success-28 and failure-1; major; owner-level, because the fix touches S28's own refresh rule).** The refresh takes an unchanged file's links from the record. A link's target, however, can live in a changed file. When a function moves or is renamed across files and the number of links stays the same, the refreshed read passes every S28 check (counts equal the tool's, ids distinct) while holding a link the tool no longer has and missing the one it does have.
- Reproduce: `$TMPDIR/aud/probe_refresh.py` uses a fake tool answering the reader's exact queries, with the same ids after the re-index. `a.py` calls `foo`, which moves from `b.py` to `c.py`. The fresh read gives `callers: {'code.b.foo': [a.main]}`. The refresh gives `pieces_from_record: 1`, `counted (6, 4)` and `callers: {}`. A read of the same graph with no record gives `{'code.c.foo': [a.main]}`. The stale answer reaches `closure`, `impact` and `dead_code` (c.foo reported as unused).
- Not covered by tests: the stand-in never moves a target between files (`standin_f1/tool.py:140-145`).
- Behaviour it should have: the record should not stand when links it holds no longer exist. Options for the owner:
  - (a) Cheap and within S28: treat the record as stale when any link it holds has a source or target missing from the fresh node read. This catches moves, renames and deletions.
  - (b) Also re-read the links of unchanged files whose targets lie in changed files. S28's failure line currently forbids this.
  - (c) Accept the staleness until the next read with no record.
- Evidence that would reverse this: the real tool renumbering `id(r)` on every re-index so that record ids always clash with fresh ones (then the read fails closed and re-reads), or the real tool resolving targets so a move always changes the count.
- Ordinary work: yes, because moving or renaming a function between files while its callers stay unchanged is ordinary refactoring.
- Consequence: other (stale code-graph answers. A9's recorded counts are the tool's own and stay right; no guard fails open and no work is lost).

**R8-3 (success-28; minor; Wave 3 row).** When the grouped type count comes back in a shape `_pairs` does not read (`codeintel/__init__.py:721-724`, kept for test_codeintel's stand-ins in ad8ba50b1), the reader reads the whole graph unchecked (`_NODES`/`_EDGES`). Under 100,000 rows that answer can be cut by size silently (item 14), giving a partial read that reports ok. It should refuse by name whenever the tool is the real one. Evidence that would reverse this: the path being reachable only by the stand-ins.
- Ordinary work: no, because the real tool answers counts as digits (probes 5b-11); only a changed tool output reaches this path.
- Consequence: fails open.

## Notes, not findings
- P2: `GOV_MEMAUDIT_PUSH="<remote> <branch>"` sits in step 6's prose as the optional declaration's form, outside the cron line's backticks. The cron line itself has no slot. If the form is pasted unfilled, `git push` to `<remote>` fails, which is closed. Lead's (a) agreed.
- P1: the record's half of GITLEAKS_MISSING can be reached through A9 when the scan is off by configuration (DEC-1045), and no route writes a slot. Lead's (a) agreed.
- Step 6 does not quote the cron path or `--repo`, as W2-187 wrote it; a path with a space would break the line.
- The stand-in's docstring names `test_w2_88_s28_pieces.py`, which does not exist; the S28 cases are in `test_w2_88_f1_codegraph.py`.
- `memory_sets.gitleaks_missing()` is evaluated separately in `walls_act` and in the record (`fabric.py:840`). They could disagree only if gitleaks were installed mid-run.
- `accept-10.txt` and `verify-8b/` had no results when I looked.

```verdict
{"kpis": [{"kpi": "success-24", "verdict": "pass", "findings": []}, {"kpi": "success-25", "verdict": "pass", "findings": []}, {"kpi": "success-27", "verdict": "pass", "findings": []}, {"kpi": "success-28", "verdict": "pass", "findings": [{"id": "R8-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "R8-3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "success-22", "verdict": "pass", "findings": [{"id": "R8-1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "failure-1", "verdict": "pass", "findings": [{"id": "R8-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}], "overall": "pass"}
```
