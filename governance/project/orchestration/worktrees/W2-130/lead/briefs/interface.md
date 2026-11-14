## The interface (the lead's decisions where the ticket is silent; the same text goes to the test designer and the implementer)

The ticket fixes the paths and what each holds. The lead fixes the layout here so cases can read it.

### Fixed facts (full hashes are resolved with `git rev-parse`; abbreviations below are unique in this repository)
- Clean-up starting head: `232efc47d` (e12f8a30c's parent). The merge that brought the re-baselined ticket: `09542040f`.
- Clean-up commits already in history: `e12f8a30c` (batches a0, a1, a2 and b1: the 87's marks, the rest's marks, the
  archive one-per-line change, the open tickets' sources) and `c4420040f` (after the owner's sitting, DEC-1098 (3):
  status words, the a3 marks, this ticket's KPI 4 line and its sources DEC-1098 and DEC-1088).
- Owner decisions: DEC-1097 (9) allowed the start; DEC-1098 (3) (committed in `9546edd61`) ruled the sitting list
  `governance/project/orchestration/packages/W2-130-SITTING.md` (committed in `2f9c80b1f`).
- W2-129's landing: merge `34eed411a`; W2-92's stated links adopted: merge `3679ca0ba`.
- The earlier independent audit: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/reviews/w2-130-marks.md`
  (at `2f9c80b1f`, for e12f8a30c) and its second part for c4420040f (at `ce7f10eb8a2a`). The record copies what it
  needs from it; cases read only the record and git, never that scratch file.
- This run's follow-up commits (made after the tests are merged): (1) a sources commit (only `sources:` lines of open
  or in-progress tickets, only `.tickets/*.md`, the ids `gov links --propose-sources` gives at its parent); (2) the
  R-12 rewording in `DECISIONS-IN-FORCE.md`; (3) the lessons' `sources:` keys; (4) a marks commit adding exactly
  `**Changed by:** DEC-1122 (4)` to DEC-1115's status line and `**Changed by:** DEC-086` to DEC-026's (status-line
  appends only), after a fresh independent auditor's check; (5) the record and LINK-RECONCILIATION.md, last.
  Each of (1)-(4) is its own commit and changes no other file.

### The record: `docs/research/W2-130-link-cleanup.md`
Prose for a reader, plus machine-readable fenced blocks. Each block opens with a line of exactly
```` ```<lang> w2-130:<name> ```` and closes with ```` ``` ````; `<lang>` is `yaml`, `diff` or `python`. Each name
appears once. Every commit is a full 40-hex hash in the blocks. Ids are `DEC-n` with the register's zero padding.
A pair is written `DEC-a<-DEC-b` (changed <- changer) in prose; in YAML it is `{changed: DEC-a, changer: DEC-b}`.

- `yaml w2-130:commits` — a mapping:
  `starting_head`, `first_commit` (e12f8a30c), `w2_129_landing`, `w2_92_adoption`, `start_decision: "DEC-1097 (9)"`,
  `status_decision: "DEC-1098 (3)"`, `status_decision_commit` (9546edd61), `sitting_commit` (2f9c80b1f);
  `cleanup:` the list of every clean-up commit in order (e12f8a30c, c4420040f, then follow-ups (1)-(4)); and the
  lists `marks:` (e12f8a30c, c4420040f, follow-up (4)), `sources:` (e12f8a30c, follow-up (1)), `status:`
  (c4420040f, follow-up (2)), and the single hashes `r12:` (2) and `lessons:` (3). The record's own commit(s) are not
  in these lists; they change only the record and LINK-RECONCILIATION.md.
- `yaml w2-130:ids-87` — a list of the 87 ids (the census's script at 3d1c459e on 24f06026).
- `yaml w2-130:census` — a mapping, one key per each of the census's 215 drifting ids, value the list of changers the
  census states for it (`DEC-1115: [DEC-1122]`).
- `yaml w2-130:archive-13` — a list of the 13 pairs stated only in ARCHIVE-SUPERSEDED §A.
- `yaml w2-130:judged-wrong` — a list of every pair left unmarked because the earlier independent auditor judged it
  wrong: `{changed, changer, verdict: "<the auditor's words, quoted>", finding: "<its finding id, e.g. F1>",
  in_gov_links: true|false}`. It holds exactly the 8 pairs gov links reports (DEC-853<-DEC-884, DEC-1050<-DEC-1057,
  DEC-120<-DEC-173, DEC-724<-DEC-860, DEC-056<-DEC-017, DEC-072<-DEC-064, DEC-162<-DEC-156, DEC-1053<-DEC-880, each
  `in_gov_links: true`) plus each census pair not on its status line that the auditor judged wrong
  (`in_gov_links: false`).
- `yaml w2-130:audits` — a list, one item per marks commit (each hash in `commits.marks`):
  `{commit, audit_head, audit_date: "<ISO 8601 with time and zone>", audit_source: "<where the check is recorded>",
  seed: <int or null>, free_text: [<mark>...], labelled: [<mark>...]}` where `<mark>` is
  `{changed, changer, mark: "<the mark text gov links proposed>", verdict: right|wrong, fate: committed|dropped|corrected,
  committed_mark: "<text committed, when fate is committed or corrected>"}`. `labelled` holds the 20 drawn by `seed`,
  or every labelled mark when the commit adds 20 or fewer (then `seed: null`).
- `yaml w2-130:comparison` — a mapping commit -> `{unchecked: <int>, wrong: <int>}`, from comparing each marks commit's
  diff with `audits`.
- `diff w2-130:patch-a0`, `diff w2-130:patch-a1`, `diff w2-130:patch-a2`, `diff w2-130:patch-b1` — the patches
  e12f8a30c applied, byte for byte as gov links (or the drafts' builder) printed them, before the auditor's drops and
  rewrites; `diff w2-130:patch-sources-2` — the open and in-progress tickets' file sections of `gov links --propose-sources` at follow-up (1)'s parent, byte for byte (as b1 was e12f8a30c's; the closed tickets' sections are not applied, their ids go to `closed-missing`);
  `diff w2-130:patch-marks-3` — `gov links --propose-marks` at follow-up (4)'s parent (all of it; the two applied
  marks are among its hunks; the 8 judged-wrong ones are not applied).
- `yaml w2-130:trailer-residuals` — `{head: <232efc47d full>, values: [{trailer: Task|Implements, value: "<the value as
  written>", commits: [<full>...], tickets: [<ticket id or W2 id or null>...], should_have_named: [<ids>] or "<text>"}]}`;
  each (trailer, value) once. `Task: decision-record` is not listed (valid under DEC-861).
- `python w2-130:recount` — a self-contained Python 3 script (standard library and git only) that, run as
  `python3 - <rev>` with stdin the script and cwd the repository, prints one JSON list of `{trailer, value}` for every
  trailer value in `git log <rev>`'s history that names no record. Run at 232efc47d it gives exactly the set in
  `trailer-residuals`.
- `python w2-130:drift` — a self-contained Python 3 script that applies docs/research/W2-92-proto-drift.py's
  definitions to `docs/DECISION_REGISTER.md` and `governance/project/orchestration/ARCHIVE-SUPERSEDED.md` as read
  from the working tree (the entries' own text, no store), run as `python3 -` with cwd the repository, and prints one
  JSON object `{"drift": [{changed, changer}...], "count": <int>}`. `yaml w2-130:drift-run` holds
  `{head, command, output: <that JSON object>, set_aside: [<pairs>], count_after_set_aside: 0}`.
- `yaml w2-130:counts-before` and `yaml w2-130:counts-after` — `{head, command: "gov links --all --json ...",
  by_code: {CODE: n}, by_code_role: {CODE: {role: n}}, unlinked_by_status: {open: n, in_progress: n, closed: n, ...}}`;
  before at 232efc47d, after at the last clean-up commit (follow-up (4)); a re-run at the record's commit gives the
  same `by_code`.
- `yaml w2-130:closed-missing` — mapping closed ticket id -> list of ids its KPI brackets or worker commits name that
  its `sources:` lacks (from gov links --all's UNLINKED_ID on closed tickets at the last clean-up commit).
- `yaml w2-130:dec-1123-linked` (added in run 3 for S4 re-baselined to DEC-1123 (2), P-W2-130-4 (a)) — mapping
  ticket id (`DAEO-…`) -> list of `{id: <the id gov links reports UNLINKED_ID>, form: list_rows|wbs|dec-798,
  via: "<what links it>"}`. It holds every UNLINKED_ID that `gov links --all --json` reports at HEAD on an open or
  in-progress ticket and that one of DEC-1123 (2)'s forms links, and nothing else:
  `form: list_rows` — the id is a backlog row (`W2-H…`, `W2-M…`, `W2-L…`) that is in the ticket's `list_rows`
  (`via`: the id as it stands there); `form: wbs` — the id is a WBS id (a ticket's `wbs_id`) whose ticket's id
  (`via`: that `DAEO-…` id) is in the ticket's `sources:`; `form: dec-798` — the id is DEC-798 and `via` is
  `DEC-1033`, which is in the ticket's `sources:`. Every other UNLINKED_ID on an open or in-progress ticket is
  added to its `sources:` by follow-up (1), from `gov links --propose-sources` (W2-H046 on DAEO-6w5n, the one backlog
  row not in its ticket's `list_rows`, among them: `list_rows` is a field other than `sources:`, so the ticket's
  F1 keeps it out; the record names it).
  The sources follow-up (1) is the last clean-up commit (after (2), (3) and (4), which are already in history:
  8d245901b, 8f8d707f0, bce798c3a); `cleanup:` is in ancestry order.
  `diff w2-130:patch-sources-2` stays `gov links --propose-sources --all` at (1)'s parent, the open and in-progress
  tickets' sections, byte for byte (the form ids included); the ids (1) adds equal that patch's ids less
  `dec-1123-linked`'s (ticket, id) pairs, and equal `gov links --propose-sources` at (1)'s parent less the same pairs
  (a ticket whose proposed ids are all form ids is not changed).
- `yaml w2-130:no-record` — mapping ticket id -> list of ids in its brackets or sources that name no record (for D-9).
- `yaml w2-130:lessons` — mapping lesson id (L-0074 ...) -> `{sources: [ids], came_from: "<the lesson's own words
  naming its decision or failure>", agree: true}`.
- `yaml w2-130:left` — `{D-5: {<path>: {<role>: n}}, D-6: {...}, D-9: {...}}`, the findings left at the last
  clean-up commit by path and role.

### LINK-RECONCILIATION.md (`governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md`)
Names `governance/project/orchestration/packages/W2-130-SITTING.md` as the list the owner ruled on and DEC-1098 (3).
Carries one markdown table row per sitting row: `| <DEC-id> | <group letter> | <proposal> | <reason> | <ruling> |`,
where `<proposal>` and `<reason>` are the sitting row's proposal column (without `**`) and reason column, verbatim.

### Lessons
Each `docs/lessons/*.md` gets one front-matter line `sources: [<ids>]` (ids that gov links resolves: `DEC-n`,
`L-nnnn`, a ticket id or a W2 id), added before the closing `---`; no other byte of the file changes.

### R-12
DECISIONS-IN-FORCE.md's R-12 line is reworded so it does not list DEC-896 as in force (for example "lifting item 2
of the done DEC-896" written so gov links reads no in-force claim); gov links --all then reports no STATUS_CONFLICT.
