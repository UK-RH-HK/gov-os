---
id: DAEO-r3gx
wbs_id: W2-203
external-ref: W2-203
status: closed
deps: []
links: []
created: 2026-11-19T00:10:00Z
type: task
priority: 1
assignee: engineer
tags: [wave-2, register, emergency-2, c3]
class: implementation
role: engineer
profile: FULL
state_class: AUTHORITATIVE
allowed_paths:
- docs/DECISION_REGISTER.md
- docs/archive/**
- docs/emergency-2/audits/08-new-register.py
- governance/project/path-map.yaml
- template/governance/kernel/schemas/path-map.schema.json
- src/gov/util/archive.py
- src/gov/store/loader.py
- src/gov/store/layout.py
- src/gov/check/citations.py
- src/gov/links/check.py
- src/gov/records/queries.py
- src/gov/closure/__init__.py
- src/gov/doctor/command.py
- src/gov/close/history.py          # the owner-decision lookups read the archive's entries too (the smallest change; named in the return)
- src/gov/close/traceability.py     # a decision a closed ticket's trailer names resolves through the archive
- tests/unit/store/**
- tests/unit/check/**
- tests/unit/links/**
- tests/unit/doctor/**
- tests/unit/close/test_w2_203*
- tests/unit/records/**
- tests/unit/closure/**
- tests/acceptance/W2-203/**
reads:
- docs/emergency-2/EMERGENCY-2.md
- docs/emergency-2/audits/08-register.md
- docs/emergency-2/audits/08-doubtful-settled.md
- src/gov/store/loader.py
- src/gov/retrieval/lexical.py
- src/gov/retrieval/semantic.py
- src/gov/config/loader.py
- src/gov/check/pathmap.py
needs:
- src/gov/store/loader.py
waits_on: []
est_loc: 420
kpis:
  success:
  - line: "S1 Archived: the old register is at docs/archive/DECISION_REGISTER-2026-11-19.md, its first line saying the file is archived and read-only (naming EMERGENCY-2 section 11.3, DEC-1214 G4 and audit 8) and the rest of it every entry of the base register, text for text; the path map names it under decision_register_archive (the path map, not the code, holds the path); a namespace archive (paths docs/archive/**, embedding_policy not embedded, lexical_policy not indexed, as evaluation-sources has them) puts the archive out of both indexes; every tracked path matches exactly one namespace; the kernel's path-map schema accepts the new key [EMERGENCY-2 11.3, DEC-1214 G4 (a)]"
    verify: "tests/acceptance/W2-203/test_w2_203_archive.py: the archive file's first line; every entry of git show 05ed38219:docs/DECISION_REGISTER.md is in the archive with identical text; the path map's key and namespace; core-pathmap green on this tree (exactly one namespace per tracked path); the schema validates the path map"
  - line: "S2 The kept register: docs/DECISION_REGISTER.md opens with a short head saying what the file is, that the earlier decisions are in the archive by id and naming audit 8, then holds every entry of the archive whose status line carries Class: kept, and every entry from DEC-1211 on, each verbatim (id, heading, status line and class, text) and in the archive's order, and no other entry; the store loader reads it with no refusal; gov doctor lists the archive among its historical paths and reports no more problems than on the base [EMERGENCY-2 11.3, DEC-1214 G4 (a)]"
    verify: "tests/acceptance/W2-203/test_w2_203_register.py: the new file's entry ids equal the archive's kept ids plus every id from DEC-1211 on, in order; each entry's text equals the archive's; register_entries(text) refuses nothing; the head names the archive and audit 8; gov.doctor.command's historical list holds the archive path; doctor's outcome per check on this tree is the base's (offline, deterministic invocation)"
  - line: "S3 Out of memory: after a rebuild of a fixture repository whose path map names a register, an archive and the archive namespace, a search for a decision found only in the archive returns no chunk of docs/archive/, a decision of the kept register still resolves by id and by its words, and the store holds no record and no register entry for an archive-only id (the archive's ids and headings are kept in a table of their own, outside the digest); the shared store is not rebuilt [EMERGENCY-2 11.3, DEC-1214 G4 (a)]"
    verify: "tests/acceptance/W2-203/test_w2_203_memory.py: a fixture git repository; the lexical index and gov retrieve (or the retrieval entry the W2-13 and W2-69 acceptance tests use) for a token only the archive holds return no docs/archive/ chunk; a kept entry's token returns its chunk; records and register_entries have no archive-only id; the archived-ids table holds it with its heading"
  - line: "S4 Archived ids resolve as history: an id that only the archive holds, cited from a kept entry (a Supersedes or Changed by label), a ticket's sources, a test file, a document's decisions: key or a commit message, is no finding of the decision-citations check (DECISION_UNRECORDED), of gov links (UNKNOWN_ID) or of gov closure (a gap), and no dangling reference of the store; gov closure of the archived id, or from a kept entry that names it, lists it with kind history; the archive is read for ids and headings only; the 366 archived ids the kept entries cite on this repository raise no finding that the base did not have in the citations check, gov links or gov closure [EMERGENCY-2 11.3, DEC-1214 G4 (a), the CTO's reading of audit 8 step 6]"
    verify: "tests/acceptance/W2-203/test_w2_203_resolve.py: fixture repositories (kept register, archive, tickets, tests, a commit citing an archived id) run through citations.check, gov links --json, gov closure and records.dangling: no finding for the archived id, kind history in the closure; on this repository, gov links --all and citations.check report no finding of those codes that git show 05ed38219's tree does not, and every archived id a kept entry cites resolves"
  - line: "S5 Owner decisions in the archive still count: a decision an owner-decision lookup of gov close reads (the path map's acceptance_exemptions, accepted_history and load_sensitive entries, a probe's accepted_by, the trailer ids of closed tickets) and that lives only in the archive is found with its status line and text, so the entry still counts; on this repository no entry of the path map's lists is refused that the base counted, and no closed ticket's trailer id is unresolved that the base resolved [EMERGENCY-2 11.3, DEC-1214 G4 (a); the brief's smallest change in gov close's lookup of a decision id]"
    verify: "tests/acceptance/W2-203/test_w2_203_close_lookup.py: a fixture project whose path map lists an acceptance_exemptions entry for an owner decision held only by the archive: gov.close.gates.owner_listed counts it (acceptance_exemptions is read there; ratchet.counted_entries reads accepted_reds and load_sensitive, which the same cases cover); on this repository the listed and refused entries of the three lists equal the base's"
  - line: "S6 Rebuildable: docs/emergency-2/audits/08-new-register.py reads the archive (its path from the path map's decision_register_archive, or --archive) and writes the kept register with --out, taking every entry from DEC-1211 on whatever the last id is; on this repository rebuilding from the archive gives the committed docs/DECISION_REGISTER.md byte for byte, and an entry appended to the archive after DEC-1216 is in the output [EMERGENCY-2 11.3; the CTO's re-run after a late entry]"
    verify: "tests/acceptance/W2-203/test_w2_203_builder.py: run the script on this tree into a temporary file and compare bytes with the committed register; on a copy of the archive with a DEC-1217 entry appended, the output holds the entry verbatim and the existing entries are unchanged"
  failure:
  - line: "F1 A kept entry missing from the new register is not noticed: the script's --check on a register that lacks an archive entry of Class: kept (or of DEC-1211 and later) names it, one line REGISTER_KEPT_MISSING <id> each, and exits 1 [EMERGENCY-2 11.3, DEC-1214 G4 (a)]"
    verify: "tests/acceptance/W2-203/test_w2_203_builder.py: fixture archive and a register with one kept entry removed: the output names REGISTER_KEPT_MISSING and the id, exit 1; the committed register and archive of this repository: exit 0, no line"
  - line: "F2 An entry held by both files with different text is not noticed: --check names it, one line REGISTER_ENTRY_DIFFERS <id> each, and exits 1 [EMERGENCY-2 11.3, DEC-1214 G4 (a)]"
    verify: "tests/acceptance/W2-203/test_w2_203_builder.py: fixture register whose copy of an entry differs by one character: REGISTER_ENTRY_DIFFERS and the id, exit 1"
  - line: "F3 An id in neither file resolves as history: a decision id that is in neither the register nor the archive (cited from a kept entry, a ticket, a test, a document or a commit) is still a finding of the citations check, of gov links and of the closure (an unresolved gap), and a dangling reference of the store [EMERGENCY-2 11.3, DEC-1214 G4 (a)]"
    verify: "tests/acceptance/W2-203/test_w2_203_resolve.py: the same fixtures with DEC-9999 cited in each place: DECISION_UNRECORDED, UNKNOWN_ID, a closure gap UNRESOLVED and a dangling row for it"
  - line: "F4 An archive entry is returned by memory: an archive-only decision is a store record, a register_entries row, a keyword or vector chunk, or a gov retrieve result [EMERGENCY-2 11.3, DEC-1214 G4 (a)]"
    verify: "tests/acceptance/W2-203/test_w2_203_memory.py: as S3, for each of records, register_entries, the lexical chunk table and the retrieve answer"
non_goals:
- "no refusal rule that stops a commit changing docs/archive/** (the CTO's decision on audit 8 step 5 (b): the header line only; EMERGENCY-2 10.1, no rule without an incident)"
- "no rebuild of the shared store and no fresh-80 measure (the CTO runs them)"
- "no change to src/gov/memaudit/tables.py's live path: the question writers' decisions domain reads the kept register"
- "src/gov/close/** is touched only where a decision-id lookup lives (history.py, traceability.py), by the smallest change; M1 and L2 work in the rest of it tonight"
- "the archive is not parsed for edges, statements or statuses: ids and headings only"
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1211, DEC-1214, DEC-1215, DEC-479, DEC-473, DEC-521]
acceptance_tests: {path: tests/acceptance/W2-203/}
---
# The old register archived and out of memory's index; the kept register in force

# W2-203 The old register archived and out of memory's index; the kept register in force

Filed 2026-11-19 by the orchestrator (lead brief `register-exit`) on EMERGENCY-2 section 11.3 ("After audit 8, the old
register is archived read-only and excluded from memory's index") and DEC-1214 G4 (a): audit 8's classes are on every
entry from DEC-001 to DEC-1210 (merge be38bcaee).

**Problem.** The register holds 1,216 entries, 153 of them kept. Memory indexes the whole file, so a question about a
rule in force meets chunks of superseded and retired history. Memory's index must be clean before the first fresh-80
measure (DEC-1214 G1).

**Approach.** The old file moves whole to `docs/archive/DECISION_REGISTER-2026-11-19.md` under a first line that says
archived and read-only (the header line only). A new `docs/DECISION_REGISTER.md` holds the kept entries and every entry
from DEC-1211 on, verbatim, built from the archive by `docs/emergency-2/audits/08-new-register.py`. The path map names
the archive under a new key `decision_register_archive` and gives `docs/archive/**` a namespace not embedded and not
indexed. The code that resolves a decision id reads the archive for ids and headings only: the store keeps them in a
table `archived_decisions (id, heading)` outside the digest (the pattern of `record_titles` and `stated_links`), so
`gov closure` and the dangling query resolve them as history; the citations check reads the archive of each commit's own
tree; `gov links` counts them among the ids that exist. Where a lookup needs an owner decision's status line and text
(gov close's ratchet lists and accepted history), its register reader falls back to the archive's entries.

**Decided by the CTO** (not reopened): audit 8 step 5 (b); step 6 teaches the code to read the archive; the archive's
name and the key beside `decision_register`.

**Closed at the land, 2026-11-19 04:25 (the CTO; EMERGENCY-2 4.3 step 5):** merged as 0a7d1301a (branch `e2/register-exit` at 60faf4271). On the merged tree, through the slot with workers: the acceptance folders W2-203, W2-130, W1-48, W2-129, W2-51, W2-49, W1-06, W2-188, W2-03, W1-10, W2-128 and the unit folders store, check, links, doctor, decisions, records, closure: 1,144 passed and 2 collection errors; the unit folders retrieval, plan, memaudit, close, optin: 1,332 passed; `gov accept W2-203`: 61 passed, 0 failed. The 2 errors were this ticket's (a fix here, the CTO's): `tests/unit/closure/test_w2_203_history.py` and `tests/unit/records/test_w2_203_dangling.py` imported the store folder's builder file by its bare name, which the acceptance folder's file of the same name takes in one collection (the full suite's); they load it by path now, and W2-203's acceptance folder with the store, closure and records unit folders in one run: 119 passed. The builder's check on the merged tree: ok, 161 entries. The main tree's store rebuilt at 0a7d1301a; a search for an archived decision returned 0 of 19 evidence items from `docs/archive/`. Owed: the 271 lines of old version tables that 43 kept entries carry; DEC-085, DEC-086 and DEC-894 (no class, archive only) for the CTO to settle; W2-203's repository-reading cases in the test map's `record_reading` list.

**A fix in gov doctor found by this ticket's S2 case, 2026-11-19 05:21 (the CTO; EMERGENCY-2 4.2):** doctor's path compliance reported a reference to any path that git's history ever shows renamed away, even when HEAD holds the path again (`tests/optin-lifted-breadth.txt` was renamed away and back; W2-200's ticket names it, so the S2 case went red on the landing branch of W2-200). A path HEAD holds is no moved path now. The failing test first: `tests/unit/doctor/test_path_compliance_renamed_back.py` (1 of 2 red before, 2 green after); `tests/unit/doctor` and this ticket's register cases: 49 passed.

**Amended at 13:24 on 2026-11-19 (the CTO; a fix in this ticket's record, EMERGENCY-2 4.2):** S2, S6 and F1 held the register in force to the archive word for word for every entry, the ones from DEC-1211 on included. That was the CTO's mistake in the lead's brief: the register is live from DEC-1211 on (the revert of DEC-1215 was recorded in its entry at 13:21, as DEC-1215 (2) orders, and four cases went red). The lines now read: every entry the archive classes kept (DEC-001 to DEC-1210) is in the register verbatim, and rebuilding that part from the archive gives it byte for byte; the entries from DEC-1211 on are the register's own, may be amended, and may be followed by entries the archive lacks; `REGISTER_KEPT_MISSING` and `REGISTER_ENTRY_DIFFERS` fail by name for the kept part only. The builder's `--check` compares only the kept part (`_live`); the test designer revises the four cases.

**S5's count case revised (merged 13:51 on 2026-11-19, `0a7467f72`; designer commit `339d7b2f1`):** the head may count more than the base, never less: nothing the base counted is refused, anything still listed stays counted, and a new entry needs a decision from DEC-1211 on (the head's one new entry is G1's exemption, DEC-1217 (2)). `gov accept W2-203` on the merged tree: 63 of 63.

**S2's doctor case revised (2026-11-19, the test designer; branch `e2/w203-s2`):** it compared every moved reference since the base and went red on `e63a7c9bd` with 66, all to `CONTRACT_v4.md` and `CHARTER_v5.md` renamed by DEC-1219 and cited by history records; it now judges only W2-203's own moves (old or new path the register or the archive); the per-part statuses still equal the base's and stay compared. A cited file renamed into the archive's path still fails it.
