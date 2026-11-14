# W2-130 (e): readiness reviewer 2's F2, the spurious changers (draft, 2026-11-08)

HEAD `7b73a02d0db3`. From `.gov-runtime/scratch/orchestrator/reviews/readiness-2-links.md` F2. The register's text is not edited for these (W2-130's failure line: an entry's text changes only by its status marks); the fix is the loader's reading (a D-6 row, `register_statements`), and W2-130 commits no mark built on them.

## A. Certainly wrong: the changer is older than the entry (11)

| Entry | Read as changed by | Where read | Form | In which entry's text | Was a proposed mark? | Fix |
|---|---|---|---|---|---|---|
| DEC-056 | DEC-017 | text | text: replaced by | DEC-056 | yes: dropped from the patch | the loader's next pass: a free-text verb takes a changer only when the clause's subject is this entry; a version-table row or a quoted case is not the entry's text |
| DEC-072 | DEC-064 | text | text: superseded by | DEC-072 | yes: dropped from the patch | the loader's next pass: a free-text verb takes a changer only when the clause's subject is this entry; a version-table row or a quoted case is not the entry's text |
| DEC-162 | DEC-156 | text | text: amended by | DEC-162 | yes: dropped from the patch | the loader's next pass: a free-text verb takes a changer only when the clause's subject is this entry; a version-table row or a quoted case is not the entry's text |
| DEC-281 | DEC-208 | label | **Changed by:** | DEC-281 | no (its status line names it) | the loader's next pass: a `Changed by:`/`Lifted by:` value with no verb gives one changer per clause, its leading id; the other ids in it are its object or basis |
| DEC-281 | DEC-237 | label | **Changed by:** | DEC-281 | no (its status line names it) | the loader's next pass: a `Changed by:`/`Lifted by:` value with no verb gives one changer per clause, its leading id; the other ids in it are its object or basis |
| DEC-594 | DEC-593 | text | text: lifted by | DEC-600 | no (its status line names it) | the loader's next pass: a free-text verb takes a changer only when the clause's subject is this entry; a version-table row or a quoted case is not the entry's text |
| DEC-728 | DEC-723 | label | **Changed by:** | DEC-728 | no (its status line names it) | the loader's next pass: a `Changed by:`/`Lifted by:` value with no verb gives one changer per clause, its leading id; the other ids in it are its object or basis |
| DEC-780 | DEC-775 | label | **Lifted by:** | DEC-780 | yes: dropped from the patch | the loader's next pass: a `Changed by:`/`Lifted by:` value with no verb gives one changer per clause, its leading id; the other ids in it are its object or basis |
| DEC-880 | DEC-843 | label | **Changed by:** | DEC-880 | no (its status line names it) | the loader's next pass: a `Changed by:`/`Lifted by:` value with no verb gives one changer per clause, its leading id; the other ids in it are its object or basis |
| DEC-896 | DEC-891 | label | **Changed by:** | DEC-896 | no (its status line names it) | the loader's next pass: a `Changed by:`/`Lifted by:` value with no verb gives one changer per clause, its leading id; the other ids in it are its object or basis |
| DEC-1053 | DEC-880 | text | text: withdrawn by | DEC-1053 | yes: dropped from the patch | the loader's next pass: a free-text verb takes a changer only when the clause's subject is this entry; a version-table row or a quoted case is not the entry's text |

## B. `Changed by:` values with no verb before their second id (32 values)

Each id after the first is read as a changer too. Some are real second changers (a list), others the object or basis of the first (as DEC-880's `DEC-882: DEC-843 is superseded …`). Fix: the loader's next pass takes the leading id of each clause; a real list is written `DEC-a; DEC-b`. Until then a bundle shows the extra ids in `changed_by` (nothing current hidden, nothing superseded shown current).

| Entry | Ids read as changers | The value (excerpt) |
|---|---|---|
| DEC-156 | DEC-165, DEC-176, DEC-434 | DEC-165 (one path outside the repository), DEC-176, DEC-434 (as far as a ticket lead is concerned) |
| DEC-176 | DEC-365, DEC-402 | DEC-365, DEC-402 |
| DEC-183 | DEC-205, DEC-235 | DEC-205 (the command's first word), DEC-235 |
| DEC-208 | DEC-237, DEC-250 | DEC-237, DEC-250 (the main orchestrator's `CONTEXT_CHECKPOINT` stop) |
| DEC-220 | DEC-416, DEC-974 | DEC-416, DEC-974 |
| DEC-365 | DEC-402, DEC-407, DEC-409 | DEC-402, DEC-407 ("unset `GOV_ROLE` is the owner"), DEC-409 |
| DEC-391 | DEC-393, DEC-396 | DEC-393, DEC-396 |
| DEC-394 | DEC-398, DEC-403 | DEC-398, DEC-403 |
| DEC-454 | DEC-868, DEC-899 | DEC-868 (items 1 (b) and 3), DEC-899 (P-IS-4 (a)) |
| DEC-455 | DEC-868, DEC-908 | DEC-868 item 3 and DEC-908 (for one part): a broken context is refused at once by the pre-close `gov check`, uncounted, not a counted iteration. |
| DEC-480 | DEC-868, DEC-908 | DEC-868 item 1 (b) and DEC-908 (for one part): `gov check` runs on every close (W2-07's KPI 5), not only when governance files change. |
| DEC-492 | DEC-868, DEC-899, DEC-866 | DEC-868 item 3 and DEC-899 (P-IS-4 (a)): the commit gates and the pre-close gate refuse at once, before any test, spending no attempt; "every gate asked; one co |
| DEC-493 | DEC-896, DEC-903 | DEC-896 item 2 and DEC-903 (for one part): the overlay holds the path map and the test map. |
| DEC-513 | DEC-518, DEC-536 | DEC-518, DEC-536 |
| DEC-608 | DEC-917, DEC-880, DEC-913 | DEC-917: the three guard lines (PreToolUse, PostToolUse, PostToolUseFailure) take the exit-mapping form of DEC-880 item 3 and DEC-913; the four lifecycle lines  |
| DEC-726 | DEC-843, DEC-852 | item 1's key restated as behaviour by DEC-843, with DEC-852's conditions (2026-10-19) |
| DEC-757 | DEC-900, DEC-899 | DEC-900: its two `accepted_reds` entries (W1-42's RETR-X-02 and governance share) are retired; DEC-899 item 3: the W1-02 and W1-05 p95 `load_sensitive` entries  |
| DEC-851 | DEC-1052, DEC-1057 | DEC-1052 (item 1), DEC-1057 |
| DEC-879 | DEC-883, DEC-884 | DEC-883 item 1 (c) makes "no code merges while a batch runs" the batch rule of W2-66; DEC-884: W2-59 merges together with W2-65 just before the combined re-pin, |
| DEC-880 | DEC-882, DEC-843, DEC-884, DEC-889 | DEC-882: DEC-843 is superseded in its items 1 and 2 only; its item 3, the install approval, stands while the tools are installed; DEC-884: the settings regenera |
| DEC-880 | DEC-904, DEC-952 | DEC-904 (item 2), DEC-952 (item 2) |
| DEC-883 | DEC-889, DEC-890 | DEC-889 refines items 2 b (failing tests re-run alone before any bisect), 3 (a declared record-reading set runs on every head), 4 (two fingerprints) and 5 (daem |
| DEC-896 | DEC-923, DEC-891 | DEC-923: item 1's records are DEC-891's (ticket files included) and its "ACCEPTED decision" is the owner's or a delegated one, also when later superseded; a `Ro |
| DEC-916 | DEC-1010, DEC-987 | DEC-1010, DEC-987 |
| DEC-949 | DEC-1057, DEC-973 | DEC-1057, DEC-973 |
| DEC-954 | DEC-1037, DEC-957 | DEC-1037 (Q8), DEC-957 (Q9) |
| DEC-991 | DEC-1050, DEC-1057 | DEC-1050, DEC-1057 |
| DEC-1003 | DEC-1052, DEC-1057 | DEC-1052, DEC-1057 (scoped, O-11) |
| DEC-1039 | DEC-1047, DEC-1049, DEC-1052 | DEC-1047, DEC-1049 (item 3), DEC-1052 |
| DEC-1047 | DEC-1049, DEC-1051 | DEC-1049, DEC-1051 (item 1) |
| DEC-1080 | DEC-1081, DEC-1082 | DEC-1081 (1), DEC-1082 (0) |
| DEC-1083 | DEC-1084, DEC-1098, DEC-1097, DEC-1087 | DEC-1084 (W2-66b, W2-90c); DEC-1098 (1) (K9's memory line met); DEC-1097 (1)(d) (K9's bar: right end to end ≥ 85 % with wrong claims ≤ 5 %, target 95 %, hit@5 b |
