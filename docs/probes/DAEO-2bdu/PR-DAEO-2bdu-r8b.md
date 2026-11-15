---
type: probe
task: DAEO-2bdu
round: runs 8 and 8b narrow re-check of R8-1, R8-2 (a) and item 27 (DEC-1154, the CTO's --owner-named DEC-1154)
reviewer_session: 941f5bd8-2a82-4e0b-bfe2-2b83100dab3d
implementer_session: eng-11 7ddd054c-410c-4a03-a27e-c82aed34cf3e (R8-1, R8-2 (a)); eng-12-2 cc6965b7-a7d1-408f-a1cc-658c7659352a (item 27); test designer td-16 d611ba26-40df-4ef0-bc3a-51ed916c48fd, td-17-2 49102ce1-8f00-484f-af5c-e7051e922826
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: pass
probed_commit: 72bfcaa5ba87b975071449784cea5e984a30752e
decisions_applied: [DEC-1154, DEC-1185, DEC-893, DEC-1156, DEC-1010, DEC-136, DEC-820, DEC-1052]
---

# Probe record: W2-88 (DAEO-2bdu), the narrow re-check of R8-1, R8-2 (a) and item 27: PASS

## The lead's judgement and triage

- **Who probed.** A fresh, read-only Independent Auditor session (`941f5bd8-2a82-4e0b-bfe2-2b83100dab3d`, claude-opus-5-5, effort high, class C2, promoted by W2-184), launched with `--owner-named DEC-1154` (the CTO's decision for the narrow checks of changes the owner decided after the ticket's review), under the OS sandbox on 2026-11-15. Step 0 held; head 72bfcaa5b and an empty `git status --porcelain` at start and end. Its tripwire changes were in other tickets' trees only.
- **What it judged:** the CTO's decisions on the narrow check of runs 8 and 8b (`PR-DAEO-2bdu-r8.md`): R8-1 (W2-187's no-scanner unit case revised to `GITLEAKS_MISSING`, ea6e4c35c), R8-2 (a) (the refresh's record stale when a held link loses an end, 19c9cbdc1; the stand-in case c150ccd57), and the lead's last fixes from the code-graph module's run at d5f7f4282: item 27 (a node label over the cap read by path, 3a6409f34) and item 28 (td-17-2's fix of a plant defect in the S28 (e) case, 8ac6f2ef0).
- **The verdict stands as PASS**, no new finding. Its note N1 (a re-export change keeps both ends of a stale link: the reviewer's option (b) of R8-2, which the CTO did not choose) is a named residual and a Wave 3 row, with R8-3 of the first check.

The reviewer's check follows, unchanged.

# W2-88 (DAEO-2bdu): narrow re-check of R8-1, R8-2 (a) and item 27
probed_commit: 72bfcaa5ba87b975071449784cea5e984a30752e
base: f21439de5

## Sandbox and identity
- (a) The write to `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-2bdu` failed with `OSError: [Errno 30] Read-only file system`. No file was left.
- (b) `echo sandbox-trial | git hash-object -w --stdin` worked (1ae28402a1…). `git update-index --refresh` exited 0.
- `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-2bdu`. HEAD was 72bfcaa5ba87b975071449784cea5e984a30752e at the start and the end. `git status --porcelain` was empty at the start and the end.
- `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing.

## R8-1 and R8-2
| item of the stated behaviour | status | file:line | how probed |
|---|---|---|---|
| R8-2 (a): a held link with a missing source or target makes the record stale; every piece is read again | fixed | `src/gov/codeintel/__init__.py:606-614`, `:756-760` | My fake tool, move case. HEAD: `pieces_read 4, pieces_from_record 0, record_stale True, stale_links 1`; the a.py piece is asked again. Base f21439de5: `pieces_from_record 1`, a.py not asked. |
| Move case (foo from b.py to c.py, a.py unchanged, counts and `id(r)` unchanged) gives `c.foo`'s caller | fixed | same | HEAD: `callers("foo")` = a.main and `definitions("foo")` = c.py, counted (6, 6). Base: `callers("foo")` = []. The record is rewritten: the next refresh takes 3 pieces from it and gives the same answers. |
| Rename case (foo to bar) | fixed | same | HEAD: `callers("bar")` = a.main, `record_stale True`. Base: `callers("bar")` = []. |
| A refresh whose held links all keep their ends reads only the changed files (item 18 kept) | fixed (kept) | `:615-622` | Only c.py changes. `pieces_from_record 2`, `record_stale False`. The only link reads asked are c.py's piece and the Project label piece; a.py is never asked. |
| A failed read keeps the last good record | fixed (kept) | `:761-770`, `_save_record` `:714` | Move plus a cut c.py piece: `GraphShort` (FABRIC_INCOMPLETE), `gov-links.json` bytes unchanged, no stats. The next good read is stale and gives the right caller. A cut node read (Function, b.py) also refuses with the record unchanged. |
| `record_stale` / `stale_links` reach A9's record | fixed | `:772-773`; `fabric.py:597` | Code read, and `test_s28_h_…[move,rename]` passes, finding `record_stale` true and `pieces_from_record` 0 in the A9 record. |
| Item 27: a label over the cap (or cut) is read by path, each path counted first, the sum checked, refused by name where no sound piece exists, never a partial read | fixed | `:655-682` | My fake. (A) Method, 100,002 nodes over 3 of 5 files: ok, counted 100,008; 5 path counts, 3 path reads, 0 whole reads. (B) 2 nodes at `<python-builtins>`: refused by name, 100,002 counted against 100,000. (C) one (Method, m0.c) piece of 100,001: GraphTooLarge naming the label, file and count. (D) a label ≤ cap whose node read is cut: read through its own path list, `<python-builtins>` included, ok. (E) a cut label whose own list holds a `{}` path: refused, 12 against 11. (G) a cut path piece: refused. The fake refuses any answer over 100,000 rows, as the real tool does; no query hit that. |
| Item 28: `assert_last_good_kept` asserts no less than decided | fixed | `tests/acceptance/W2-88/test_w2_88_f1_codegraph.py:184-201`, `:382-385` | Read. It checks: no ok, HEAD unmoved, A9 record list unchanged, no new commit under governance/adoption, record and copy bytes unchanged, no new copies, clean tree. The third A9 still checks the refresh of only what changed. The case passes. |
| R8-1: only the no-scanner case changed; it asserts `GITLEAKS_MISSING`, no `<path to gitleaks>`, no `<...>` slot, no cron line; it carries `Rewrite-Reason: DEC-893, DEC-1156 (7)` | fixed | `tests/unit/adopt/test_w2_187_walls_act.py:52-61` (ea6e4c35c) | Diff: only that case and `import re` changed; the other six cases are untouched. The file passes (7 cases in the run above). |

## What I probed and found sound
- The stale check fails closed. A malformed held row (not a list of 4) counts as a missing end and forces a full re-read. The retry path (`GraphShort` while pieces were taken from the record) still re-reads everything and sets `record_stale` true.
- The nodes are now read before the links. A node-read refusal comes first and writes nothing.
- The new unit cases (3 for item 25, 3 for item 27) assert the stated behaviour: `stale_links` 1, every piece asked again, record rewritten without `code.b.foo`, the path-0 file not read, the label never asked whole, both refusals with their figures. The unit stand-in change gives generated links ends that are real nodes. That is needed, because otherwise every held link would look stale. It removes no assertion from the existing cases; only the `FOLDERS` line was reformatted.
- The test designer's stand-in keys `named` and `calls` do nothing in plans that leave them out. Case (h) checks that the unchanged caller file is read again, that every `id(r)` is served once (distinct count equal to the total), and `record_stale` and `pieces_from_record` 0.
- Scope:
  - All six commits carry `Task: DAEO-2bdu`.
  - The `Implements:` ids (DEC-954, CAP-44.b, CAP-44.f, CAP-17, CAP-20) are all in `sources:`.
  - The engineer's and lead's files (`src/gov/codeintel/__init__.py`, `tests/unit/codeintel/test_w2_88*`, `tests/unit/adopt/test_w2_187_walls_act.py`, `docs/changes/W2-88-evidence.md`) are all in `allowed_paths`.
  - The test designer's two commits touch only `tests/acceptance/W2-88/**`, which is that role's area (MR-3), merged by the lead.

## Findings
None new.

## Notes, not findings
- **N1 (success-28, outside item 25's decided rule).** Item 25 makes the record stale only when a held link loses an end. Some resolution changes leave both ends in place. Example: an unchanged `a.py` calls `foo` re-exported through `pkg/__init__.py`, and the re-export changes from `.b` to `.c` while `b.foo` still exists. The refresh then keeps `a.main -> b.foo` while the tool now links `a.main -> c.foo`, and the counts are equal. This is the reviewer's option (b), which the CTO did not choose. I list it for Wave 3 or the CTO only, not as a round.
  - Ordinary work: yes, because changing a re-export is an ordinary refactor.
  - Consequence: other (a stale code-graph answer; the A9 counts stay the tool's own; nothing fails open, nothing is lost).
  - Evidence that would reverse it: the real tool resolving calls only to the definition named in the caller's own file.
- The redis measure (143,008 links) ran before item 25 and item 27. The new code has not met the real tool. The only new step that could fail on real data is the name set, and the real tool's names are strings (probe 3), so I expect none.
- The README says `test_s28_h` was red on f21439de5. I did not re-run it on the base. My own fake shows the base giving the wrong caller in both the move and rename cases.

```verdict
{"kpis": [{"kpi": "success-28", "verdict": "pass", "findings": []}, {"kpi": "failure-1", "verdict": "pass", "findings": []}, {"kpi": "success-22", "verdict": "pass", "findings": []}], "overall": "pass"}
```
