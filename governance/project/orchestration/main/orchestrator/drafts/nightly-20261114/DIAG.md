# Nightly 20261114-0404: diagnosis of the six reds

Read-only diagnosis for the CTO (DAEO-sdxk). Nightly head f3d3438fcb45; current integrate 77220f814.
Reproduced from the main tree through heavy_slot.sh, TMPDIR=/tmp/gov-os-cto-f388, PYTHONUSERBASE=/home/usain/.local.
Nothing committed; no test, source or record edited.

None of the six is in `.gov-runtime/scratch/orchestrator/tools/skip_known.json`, `load_sensitive.txt`,
`nightly_only.txt`, or `governance/project/path-map.yaml` `accepted_reds` (which holds only W1-19's and W2-13's
latency cases, the run's two `accepted-red` lines). W2-54's two cases are listed in `tests/acceptance/serial-only.txt`
(lines 110-111, `nightly: real-model`), which places them; it does not accept them red.

## 1-2. W2-175 S7: `test_s7_record_sha256_of_each_template_is_its_sha256_at_the_head[role-cto]` and `[role-lead]`

(a) `tests/acceptance/W2-175/test_w2_175_record.py:53`:
`assert any(head in t.HEX64.findall(row.lower()) for row in rows)`:
- `docs/changes/W2-175-CIT-P.md: no row naming role-cto.md holds its sha256 at the head (dbcc9d8c...d789)`; the
  record's row holds base `1b1745571c...` and new `013d4d85bc...`.
- `... role-lead.md ... (c731503e...e799)`; the record's row holds `8279168522...` and `4e8e46b097...`.

(b) The test hashes `template/governance/kernel/templates/<stem>.md` as the working tree holds it (`t.path_of(stem)`),
which is integrate's head and not W2-175's. Commit **b88a76172** (2026-11-13 11:13, CTO, owner-approved in chat:
"W2-56 UNTIL deletion approved: role-lead c731503e, role-cto dbcc9d8c") deleted the "until W2-56" line from both
templates, after W2-175 closed (82c018e75, record ACCEPTED under DEC-1139; landed at 61cae50dc). The new bytes are
exactly the shas the assertion asks for.

(c) Red on 77220f814: **yes** (both).

(d) Class: **a test that pins a moving value**. The ticket's own Verify (DAEO-wahn line 64) says "the sha256 column
equals `sha256sum` of each file **at the ticket's head**"; the test reads integrate's HEAD instead, so every approved
template change after the close turns it red. The record is not wrong: it is a closed ticket's ACCEPTED CIT-P record
of the 1.0.1 bytes. (The other way, refreshing the record, means editing `docs/changes/W2-175-CIT-P.md`, a path of
closed W2-175 (DAEO-wahn allowed_paths line 21), and it breaks again at the next template change.)

(e) Route: a decided-behaviour revision by an independent test designer (DEC-1156 (7)). The test reads each template at
W2-175's landing commit (61cae50dc, or the merge that landed it) through git, the way `test_s7_record_names_each_template_s_base_sha256`
already pins its base commits. Then a narrow check. Cost: one small worker pass (one function and a pinned constant in
`w2_175_support.py`), about 20 minutes, no product change.

## 3-4. W2-130 S8: `test_s8_gov_links_at_head_gives_the_after_counts` and `test_s8_left_holds_d_5_d_6_and_d_9_by_path_and_role_as_gov_links_finds_them_at_head`

(a) `tests/acceptance/W2-130/test_w2_130_record.py:78`: `assert {k: v for k, v in after["by_code"].items() if v} == mine["by_code"]`.
At the nightly head: `{'CLOSED_TICKET_EDITED': 122} != {... 123}`, `{'UNKNOWN_ID': 56} != {... 55}`.
Line 101: `left.D-9 differs from the findings at HEAD`: `.tickets/DAEO-drhj.md {'orchestrator': 3} != {... 4}`, and the
record has one more item, `.tickets/DAEO-qyt2.md {'orchestrator': 1}`.

(b) The test runs `gov links --all --json` on a clone at integrate's HEAD and compares the result with the record
`docs/research/W2-130-link-cleanup.md` (refreshed at 6b62de94e by a2671a340; W2-130 merged at 127eaf409, 01:41).
`gov links` was run on clones at each revision (scratch script, counts below):

| revision | CLOSED_TICKET_EDITED | UNKNOWN_ID | change |
|---|---|---|---|
| 127eaf409 (W2-130 merge) | 122 | 56 | matches the record |
| e8236b19f W2-185 (DAEO-qyt2) merged and closed, 02:57 | 122 | 55 | qyt2's UNKNOWN_ID finding gone |
| c82335a40 W2-104 (DAEO-drhj) reopened under DEC-1164 (18), 02:58 | 123 | 55 | +1 CLOSED_TICKET_EDITED on drhj |
| f3d3438fcb45 (nightly) | 123 | 55 | |
| 77220f814 (W2-42a / DAEO-03ub closed again after its DEC-1164 (18) reopen 2b034037a) | 124 | 55 | +1 CLOSED_TICKET_EDITED on DAEO-03ub |

So each ordinary ticket event after the land (a close; a reopen of a closed ticket under DEC-1164 (18)) moves the
counts. No product change in `gov links` is involved.

(c) Red on 77220f814: **yes**, and it has moved further (`CLOSED_TICKET_EDITED` 124; D-9 adds `.tickets/DAEO-03ub.md` 1 -> 2).

(d) Class: **a test that pins a moving value**. The record's `counts-after.head` is the last clean-up commit
(`test_s8_counts_before_...` asserts exactly that), but these two cases compare the record with HEAD, which moves with
every ticket edit. Refreshing the record (`docs/research/W2-130-link-cleanup.md`, a path of closed W2-130, DAEO-q8cl
line 25) would only hold until the next close or reopen; it has already gone stale twice in five hours.

(e) Route: a decided-behaviour revision by an independent test designer (DEC-1156 (7)). Both cases run `gov links` at
`counts-after.head` (`record.commit_list("cleanup")[-1]`, through the existing `clone_at` fixture) instead of HEAD; the
HEAD-wide "no UNMARKED_CHANGE but the 8 pairs" Verify stays as it is, since it does not move with ticket closes. Then a
narrow check. Cost: one small worker pass (one fixture, two cases), about 20-30 minutes, plus one more `gov links` run
(about 6 s) per session.

## 5-6. W2-54: `test_w2_54_time_limit.py::test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit` and `test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here`

(a) Case 5, `test_w2_54_time_limit.py:84`: `assert done.returncode == 0`: "the check is not green on this repository /
`sh -c python3 -m gov.context.context_check` / exit code: 1 (190.7 s)", stdout ending
`context-reproducibility: 0 ticket(s) failed, 3 error(s)`. The time assertion (line 83) passed.
Case 6, `test_w2_54_green_here.py`: `assert entry.get("status") == S.GREEN`: "context-reproducibility is RED here:
[{"code": "CHECK_FAILED", ...}]" (`'RED' == 'GREEN'`).

(b) The REFUSED lines over the 6000 ceiling are not the failure: `context_check.main()` counts them as reproduced
refusals. The failure is the **3 errors**. I re-ran `python3 -m gov.context.context_check` in the kept clone
(f3d3438fc, its own store; the clone stays clean), which lists all three where the log's truncated stdout shows one:

```
ERROR: DAEO-6f0s: mandatory input 'W2-60a' not found in the store
ERROR: DAEO-6w5n: mandatory input 'W2-H046' not found in the store
ERROR: DAEO-sq3a: mandatory input 'W2-56' not found in the store
context-reproducibility: 0 ticket(s) failed, 3 error(s)
```

`gov context` takes every `sources:` entry as a mandatory input and looks it up as a store record
(`src/gov/context/__init__.py:164` `_ticket_mandatory_ids`, `:313` BLOCKED). A WBS id is no record. All three ids were
added by **57cbacfbf** (2026-11-14 00:02, "W2-130 follow-up (1): open and in-progress tickets' sources: from gov links
--propose-sources at 11c4d7a5a ... (P-W2-130-4 (a))"):
- DAEO-6f0s (W2-184, in_progress): `W2-60a` (the record is DAEO-cv58);
- DAEO-6w5n: `W2-H046` (a WBS hypothesis id in docs/plan/WAVE_2_*.md, no store record);
- DAEO-sq3a (W2-186, open): `W2-56` (the record is DAEO-wnnz).

Both cases were green in the 11-12 and 11-13 nightlies (cb208f9434d7 is before 57cbacfbf). No change to
`src/gov/context/` since 11-13 (last e0c076514, W2-183). The three tickets are also blocked for `gov context` / `gov brief`
right now, not only in the check.

(c) Red on 77220f814: **yes by cause, not reproduced cleanly here.** In the main tree both cases fail earlier, with a
stale store: "unmeasured: stale store: the store was built from 8f00bb90810b, not from HEAD 77220f8149af" (2 failed in
152 s). That is the main tree's environment (its store is not rebuilt by a read-only session). f3d3438..77220f814
changes no `sources:`/`deps:` line under `.tickets/` (only DAEO-03ub's two status lines) and nothing in `src/gov/context/`,
so the three errors stand at 77220f814.

(d) Class: **a record that must be refreshed**: three ticket files' `sources:` lines (`.tickets/DAEO-6f0s.md`,
`.tickets/DAEO-6w5n.md`, `.tickets/DAEO-sq3a.md`), CTO-owned ticket records written by the W2-130 follow-up, not in
closed W2-130's (DAEO-q8cl) product paths. Neither the test nor `gov context` is at fault: the check works as decided
(an unresolvable mandatory input is an error). Side note (discovery, not a route): `gov links --propose-sources`
proposed WBS ids as sources. Whether that is a defect of the closed `gov links` ticket's scope (DEC-1164 (18)), or the
CTO's application of P-W2-130-4 (a) taking them unfiltered, is open. Worth a look so that the next propose-sources pass
does not do it again.

(e) Route: a CTO ticket-record commit (Task: DAEO-sdxk; trailers in one block). It replaces `W2-60a` with `DAEO-cv58`
and `W2-56` with `DAEO-wnnz`, and drops `W2-H046` (or names it in the external-references list, if the owner wants it
kept as an input). Check by running `python3 -m gov.context.context_check` on a store rebuilt at the new head: it must
end green. Cost: about 10 minutes of edits plus one store rebuild and a 3-minute check; no worker and no test change.
DAEO-6f0s is in_progress (W2-184), so tell its lead about the sources line or make the edit on integrate before its
next merge-from-integrate. Also, for re-running these two cases in the main tree: rebuild the main tree's store at
HEAD first.

## Other notes

- Unrelated to the six, but in the same run: W2-45 S1's merges budget (CHECK_TIMED_OUT 60.07 s at 60 s) and W2-124 S1's
  `[hung]`/`[part-way-500]` (84 s at 60 s) were red under parallel load and passed alone: load (the gate's
  `load=12.2/6.6`, lock wait 1893 s).
- Scratch scripts used: `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/f3886235-4854-4c91-9cf3-1a1dd009cb50/scratchpad/links_at.py`
  and `cte_diff.py` (shared clones under /tmp/gov-os-cto-f388).
