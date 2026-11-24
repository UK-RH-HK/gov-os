# G-6 with G-8: the records and forms map, and the path map (DEC-1241 G-6, G-8)

`docs/emergency-2/integration/RECORDS-MAP.md` · independent audit (Opus), read-only · 2026-11-24 · Gov OS `w2/integrate`
at `98893679c`; EXAMIN `/home/usain/gov-os-runs/W2-27/examin` at `e2c25b8` (branch `wave0/schema-contract-and-disclosure-fix`),
read only.

**How it was made.** Memory first: `gov retrieve` ran twice (once on the path map, once in my own words on record forms).
The store is at `49e7fa070d78`, **584 paths behind HEAD**; it answered with the path-map checker
(`src/gov/check/pathmap.py:75-112`), the W2-95 ticket and the schema map (`src/gov/check/schema.py:23-66`), which I
then read at HEAD. Everything else is from files. Four Sonnet helpers each took one area (spec and ticket; brief and
maps; decisions, close records and returns; memory measure, usage, adoption, release and update) and returned rows
with path:line evidence. I spot-checked their key lines (`ticket.schema.json:6`, `check/authority.py:44`,
`launch/command.py:52-81`, `close/command.py:77-86`, `retrieval/retrieve.py:48`, `subagentstop.py:14-19`,
`queue/fix.py:40-66`, `queue/command.py:405-430`). The path map I measured myself, read-only, with the product's own
matchers (§3.3). I did not run the test suite (full suite outside the slot).

**Builds on, not repeated:** the tool map (`TOOL-MAP.md`: tools, its hand-offs 1 to 9 and rule 5), audit 4 §1.5 (the
22 templates, the seven missing forms) and §3 (List B, B1 to B16), `DECISIONS-HELD.md`, `FINDINGS.md` (I-1 to I-10).
Where those already say it, a row points to them.

**Marks used.**
- *Check, when:* **before** (before work starts or before launch) · **land** (at the landing) · **after** (a notice
  after the landing, or a scheduled check) · **typed** (only when someone types the command) · **never**.
- *Held:* **H** held by code on Gov OS's path today · **H\*** held by code inside a tool Gov OS bypasses today
  (`gov queue`, `gov brief`; DEC-1239 (3) keeps Gov OS on the plain path, so these hold in the scratch repository and
  EXAMIN only) · **C** checked after (a notice, or typed) · **A** an agent only.
- *Place:* every fix below is **integration** (DEC-1238 (7)) unless it says otherwise.

---

## 0. The answer in ten lines

1. **The path map is the best-held record in Gov OS, and it is still cracked.** Gov OS: 5,551 tracked files, 0 in two
   namespaces, **6 in none** (the whole `docs/emergency-2/integration/` folder, made on 22 November; this file makes it
   7). EXAMIN: 3,910 tracked files, 0 in none, 0 in two. Nothing caught Gov OS's six because the coverage check runs
   only in `gov queue`'s after-step as a notice (`queue/after.py:8`, `check/structural.py:44`) and Gov OS lands by hand.
2. **Two grammars read the same map.** The schema says `*` stays inside one folder (`path-map.schema.json:145`). The
   check, the landing's selection, memory and the impact trace follow it. **`gov doctor` and adoption's A2 use
   `fnmatch`, where `*` crosses folders** (`doctor/command.py:604-615`; `adopt/project.py:205-216` imports doctor's).
   On Gov OS's map the root namespace `root-files: ["*"]` (`path-map.yaml:8-9`) then matches every file: doctor
   reports **pass with 6 files unmapped**, sees **5,543 files in two namespaces** and cannot report it, and A2 classes
   **every file as `root-files`**. Gov OS's own A2 record shows it: 1,712 of 1,712 artefacts `namespace: root-files`
   (`governance/adoption/A2-classification.md`, 2026-10-11).
3. **A4 (a path in two namespaces) is still not built** in A3 or doctor (DEC-1238 (1c)); only `core-pathmap` reports it.
4. **No ticket path is checked against the map.** No code in brief, plan, launch, readiness, dispatch or discover loads
   `path-map.yaml` (helper 1); `gov brief` checks only that `allowed_paths` is not empty (`brief/build.py:161`).
5. **The brief chain is broken in the middle**, as G-3 says: `gov launch` takes no brief (`launch/command.py:52-81`),
   its launch record holds the role template's hash, not the brief's (`launcher.py:857`); all 50 briefs in
   `docs/emergency-2/briefs/` are hand-written; the agent files carry literal slots (`.claude/agents/engineer.md:21`).
6. **Spec to ticket to test has no code link after creation.** `gov discover` copies K-lines into the ticket once
   (`discover/tickets.py:107-117`); nothing compares them later; 66 of 188 acceptance folders fail `parse_map` today
   (the tool map counted 72 of 189).
7. **The ticket schema requires three fields** (`ticket.schema.json:6`: `role`, `allowed_paths`, `kpis`). `kind`
   (DEC-1242 R-3) is in 0 of 271 tickets; `specification` is read by code (`readiness/checker.py:101`,
   `tasks/queue.py:80`) but is not in the schema and is in 0 tickets.
8. **Returns:** the lead's return has two forms that disagree and no check; the helper's is checked by label only.
9. **The memory measure's figure reaches no gate:** `FIGURES.json` has no release or commit stamp (`memaudit/figures.py:118-136`)
   and no reader in `src/gov/release/`; usage and context figures live only in scratch scripts.
10. **Many records have a form only in code** (no schema): the declaration, `FIGURES.json`, the landing's runtime files,
    the adoption stage records, the release, re-pin and update records; 4 schemas exist that no code loads at run time
    (`register-entry`, `memory-audit`, `facts` checked only by tests) or writes (`adoption-verdict`).

---

## 1. The records map (G-6)

One row per record the tools pass along. Columns: **record · form · writes it · checks it, when · reads it next, and
what it relies on · step(s) · missing, and the fix (owner)**. Ticket ids: W1-08 `DAEO-uudf`, W2-02 `DAEO-zflj`, W2-36
`DAEO-w19l` (discover), W2-129 `DAEO-q7lk` (links), W2-152 `DAEO-o5x1` (brief), W2-128 `DAEO-t8mp` (templates), W2-136
`DAEO-p3ln` (plan), W2-21 `DAEO-1ahb` (launch lead, launch records), W2-153 `DAEO-8s85` (role template at launch), W2-96
`DAEO-ouet` (accept), W2-115b `DAEO-j9z6` and W2-206 `DAEO-l2b2` (queue), W2-201 `DAEO-k1us`, W2-11 `DAEO-k7hz`
(twelve fields), W1-25 `DAEO-rrxp` (checkpoint), W2-204 `DAEO-ma4q` (memaudit), W2-198 `DAEO-o5wi` (scan), W2-209
`DAEO-a2h5` (release, in progress), W2-17 `DAEO-sdhj` (update), W1-41 `DAEO-cdoi` (adopt lite), W1-27 `DAEO-xw3k`
(doctor), W2-95 `DAEO-57hm` (core-pathmap), W2-207 `DAEO-rt4s` (run-time tool, open), W2-210 (verdict, on `e2/d1-verdict`).

### 1.1 Spec, KPIs and the ticket (W7)

| Record | Form | Writes it | Checks it, when | Reads it next (relies on) | Step | Missing → fix (owner) |
|---|---|---|---|---|---|---|
| **Spec** | body: `skills/spec-writing/spec-form.md:15,23`; front matter `schemas/specification.schema.json:1-10` (shared fields only) | `gov discover` drafts (`discover/command.py:101`, `draft.py:82-113`); product-spec fills by hand | **typed**: `check_spec.py` through `gov discover --check` (`discover/check.py:80-101`); the schema scan never sees it (`check/schema.py:27`: `.tickets` and `docs` only); **land**: a specification-class ticket passes readiness (`close/gates.py:103`) | `gov discover --ticket` (`discover/command.py:186-200`) relies on `check.kpis`, `check.verifies` | W7 | no body schema; `openspec/changes/**` outside the schema scan; no link back once the ticket exists → add `openspec/**` to `RECORD_PATHS` (fix, W1-26 schema check, ~5 lines) |
| **K-lines** | `- K<n>: …` + `Fails if:` (`spec-form.md:23-43`); one `- K<n>: <verify>` under `## Verify` (`discover/check.py:58-68`) | product-spec, by hand | **typed**: every K has a verify (`discover/check.py:96-100`) | `discover/tickets.py:107-117` copies each into `kpis` as `… [Kn]`, once | W7→W8 | **nothing compares a ticket's `[Kn]` lines with its spec later**: `links/check.py:86-87` has no `K` id form → `KPI_DRIFT` in `gov links` (tool map fix 3; A-23b) (fix, W2-129 + W2-152, ~40 lines) |
| **Ticket** | `schemas/ticket.schema.json` (requires only `role`, `allowed_paths`, `kpis`, `:6`; extra keys allowed); `templates/ticket.md:15-50` | `tk` and an agent by hand (271 files); `gov discover` (`discover/tickets.py:27-117`) | **typed**: `gov check schema`; **land**: only when the commits touch a governance prefix (`close/command.py:77-86`), and `.tickets/` is not one; **before** (H\*): `gov brief`'s ready check (`brief/build.py:157-186`), which `gov launch` does not run | `gov plan` (`plan/tickets.py:103-116`); `gov brief`; `gov queue`; `gov accept` | W7, W8, W11 | a ticket-only change skips the schema check; launch skips the ready check → ready check in `gov launch` (with G-3, A-6) |
| `kpis` | schema `:8-22,56-62` (line or `{line, verify}`) | by hand (271/271); discover `tickets.py:71,99,111` | **before** H\*: `KPI_NO_VERIFY` (`build.py:163-166`); **land**: notice (`queue/checks.py:116-121`) | brief table (`build.py:402-404`); `links/check.py:159,556-569` (bracket ids); `gov accept` via README | W8, W9 | link to the spec's K-lines (row above) |
| `allowed_paths` | schema `:55`, required, ≥1 | by hand; discover `--paths` | **before** H\*: non-empty only (`build.py:161`); while building: the guard (`containment/scope.py:34-57`); **land** H\*: scope gate (`close/command.py:202,413-435`), queue path notice (`queue/command.py:289`) | plan's write overlap (`plan/derive.py:7`); criticality (`launch/criticality.py:87`); selection (`close/select.py:238`) | W7-W11 | **never checked against the path map** → §3.5 item 3 |
| `reads` (the read paths) | schema `:65`, optional; no `read_paths` field exists | by hand (39/271); discover `tickets.py:76` | **before** H\*: `READS_MISSING` for tickets created after `facts.ready.new_since` (`build.py:170-174`) | plan warns `READS_WIDE` only (`plan/derive.py:9`) | W7 | not checked against the map → §3.5 item 3 |
| `needs` | schema `:66` | by hand (53/271) | **before** H\*: `NEEDS_MISSING`, new tickets (`build.py:172`) | plan's read-after-write order (`plan/derive.py:157-161`) | W7 | — |
| `waits_on` | schema `:24-38,67` | by hand (69/271) | **before** H\*: `WAITS_ON_MISSING`, `WAITS_ON_UNKNOWN` (`build.py:172-179`) | `plan/derive.py:153,168` | W7, W8 | — |
| `depends_on` | schema `:46-54` (accepts WBS ids; the template says tickets only, `ticket.md:61`) | by hand (254/271) | **before** H\*: `DEPENDS_NOT_CLOSED` (`build.py:167-169`) | `plan/derive.py:149` (`DEPS_DISAGREE`) | W7 | schema and template disagree → chore (product-spec) |
| `class` | schema `:44`, any string; values only in a comment (`ticket.md:20-22`) | by hand (264/271) | **land** H\*: `gates.ticket_class` (`close/gates.py:25-52`, `queue/command.py:258-262`) | model exceptions (`launcher.py:844`); readiness (`checker.py:222`) | W8, W11 | no enum → enum in schema (fix, W2-02, ~5 lines) |
| `kind` | **absent** (DEC-1242 R-3 (a): required) | nobody (0/271) | never | the queue guesses "feature" from KPIs plus a body (`queue/checks.py:105-121`) | W7, W11 | the field, `required`, migration of **271** tickets (R-3 said 219) → schema fix (W2-02) + migration chore |
| `acceptance_tests` | schema `:71`, an object with no `path` property | by hand (262/271); discover `{path, author}` (`discover/command.py:200`) | **land** H\*: test authors (`queue/command.py:266,286-295`); `links/check.py:571-578` (path exists) | `gov accept` (`accept/runner.py:631-640`) | W9, W11 | `path` in the schema (fix, W2-02) |
| `sources` | schema `:69` | by hand (264/271); discover writes none | **after**: `UNLINKED_ID` (`links/check.py:554-569`) | brief header (`build.py:400`) | W8, W11 | discover's feature ticket has none → fix (W2-36) |
| `specification` | **not in the schema** (passes as an extra key) | discover only (`tickets.py:114`); 0/271 | never | `readiness/checker.py:101`; `tasks/queue.py:80` (`SPEC_NOT_CLOSED`) | W7, W11 | code reads a field no spec states → schema property + name check (SQ-R2) |

### 1.2 Brief, templates and the maps it is built from (W8, W9)

| Record | Form | Writes it | Checks it, when | Reads it next (relies on) | Step | Missing → fix (owner) |
|---|---|---|---|---|---|---|
| **Brief** | `templates/brief.md:6-62` (24 slots; `{MEMORY_BLOCK}` `:30`, `{COMMANDS_TABLE}` `:33`); no schema | `gov brief` to stdout, saves nothing (`brief/command.py:77`); in practice an agent by hand: **50 of 50** files in `docs/emergency-2/briefs/` | **before** H\*: ready check; `PLACEHOLDER_LEFT` (`build.py:382`); unknown `{CMD:}` (`:208-213`); all only when `gov brief` runs; the 4,000-character budget printed, never enforced (`command.py:65`) | the session; the scratch `launch_worker.sh:25-27` pipes it to `gov launch`, which takes no brief argument (`launch/command.py:52-81`) | W8 | launch neither builds nor checks it; no brief hash in the launch record (`launcher.py:857,911-928`) → G-3: `gov launch` builds the brief (or takes `--brief` and re-runs the ready check), records brief and `brief.md` sha256 (fix, W2-21 + W2-152, ~60 lines) |
| Memory section of the brief | `gov retrieve` bundle via `brief/memory.py:75` | code | cut at `BUNDLE_BUDGET = 6000` tokens (`retrieval/retrieve.py:48`); `MEMORY_UNAVAILABLE` is a warning only (`build.py:375-376`) | the session (rule 5: uncut) | W8 | the cut and the warning → tool map hand-off 1 (A-11) |
| `keys.yaml` | `templates/keys.yaml`; no schema | by hand | **never** | `build.py:342-344`: a listed key with no value is left as written, not refused (`:218`), e.g. `{SUBJECT}`, `{COMMIT_PATHS}`, `{HEAD}` | W8 | keys.yaml lets a slot escape → refuse a listed key left unfilled in a launch brief (fix, W2-152, ~10 lines) |
| **Role templates** (`role-cto`, `-engineer`, `-lead`, `-product-spec`, `-research`, `-reviewer`, `-test-designer`) | `templates/role-*.md` | by hand; byte copies to `.claude/templates/`; `.claude/agents/*.md` composed unfilled (`adapters/portability.py:196-208,250`) | **typed**: copy equal byte for byte (`portability.py:231-247`; doctor `:929`); slots never | the session's appended system prompt, raw (`launcher.py:31-36,856`); `gov brief` fills only `{CMD:}` rows and one lead run block (`build.py:248-268,347`); `role-cto` is in no `ROLE_TEMPLATES` (`brief/__init__.py:7-14`) | W8-W11 | literal slots reach sessions (`.claude/agents/engineer.md:21`, 31 in `orchestrator.md`) → audit 4 A-24 / 015a F11 (fix, W2-153) |
| **Commands map** | `schemas/facts.schema.json`; `governance/project/facts.yaml` (`commands :31`, `steps :127`, `budgets :166`, `ready :188`) | `gov adopt --facts` once (`adopt/facts.py:46-72,142-151`), then by hand | **typed** only in unit tests; `gov brief` refuses a missing or unreadable file (`build.py:333-336`) but never loads the schema | `build.py:196-213` (`{CMD:}`, `{STEP:}`), `:422-424` (paths), `:352`; `memory.py:37` | W7, W8 | runtime schema check; `launch_worker`/`lead_brief` entries point at untracked scratch (`facts.yaml:75-83`) → validate in `gov brief` (fix, W2-128, ~10 lines); retire the scratch entries with G-5 |
| **Test map** | `schemas/test-map.schema.json`; `governance/project/test-map.yaml` (192 lines); kit seed (43 lines) | by hand | **land** H\*: `select.load_map` validates (`close/select.py:66-91`); scoped selection refuses (`:769-771`, `SELECTION_REFUSED`) | `select.py:374-453` (`record_only`, couplings, `every_close`); `close/batch.py`, `queue/full.py:98`, `close/nightly.py`; the store's fingerprint (`store/loader.py` `_record_only`) | W11, W6 | nothing before the landing checks that a new path is placed → covered once the path map is exact (§3.5) |
| **Acceptance README map** | prose and example in `skills/test-design/test-kinds.md:27-52`; no template | test designer, by hand | **typed** (`gov accept`, `accept/runner.py:139-191,716-736`); **land** H\*: `ACCEPT_MAP_UNREADABLE`, `ACCEPT_NO_MAP`, `NO_ACCEPTANCE_TESTS` (`queue/checks.py:171-191`) | `gov accept`'s per-line report; `queue/acceptance.py:20-48` | W9→W10, W11 | **66 of 188 folders fail today**: 23 no README, 31 unreadable, 8 empty, 4 a line it cannot read (W2-07 `:57`, W2-68 `:91`, W2-77 `:51`, W2-115 `:97`); no check at write time → G-2 (chores/fixes under each folder's ticket); `parse_map` in the designer's commit check (A-12) |
| TESTS-READY marker and "red on the base" | none; instruction only (`role-lead.md:43`, `role-engineer.md:15`, path `facts.yaml:21`) | the lead, by hand | **never**: `red_at_base` only excuses regression reds (`close/attribution.py:314-317`) | the engineer | W9 | A-3 (fix, W2-115b + W2-96) |
| **Launch record** | code only (`launcher.py:911-928`), folder `.gov-runtime/launches/` (`launch/record.py:44-56`) | `gov launch` | never (written, not judged) | `spend/brake.py` (projection); session records | W8 | brief sha256 and path (row "Brief"); none since 16 November (audit 4 §1.1) |

### 1.3 Decisions, landing, fixes, returns, handover (W5, W10-W12, W15)

| Record | Form | Writes it | Checks it, when | Reads it next (relies on) | Step | Missing → fix (owner) |
|---|---|---|---|---|---|---|
| **Decision record** | `templates/decision-record.md` (register line `:15-20`); `schemas/madr.schema.json` (nothing required) | the CTO, by hand | **typed**: `gov decisions basis` (`decisions/command.py:43-49`, `basis.py:100-125`); **after**: the schema family in the queue's after-step (`queue/after.py:51-60`); owner approval skipped (`check/authority.py:44`, `ACTIVE_UNAPPROVED`) | — | W5 | no level fields (touches, reversible, inside); no `answer` → T-1's first slice (feature approved, DEC-1236, DEC-1242 T-1, R-6) |
| **Register entry** | `schemas/register-entry.schema.json` (requires `id/type/status/owner/date/span`), **loaded by no code** (`check/schema.py:49-50`) | the CTO, by hand (`docs/DECISION_REGISTER.md`, 187 entries) | as above | `store/loader.py:203-247` (heading form, capital status line, one heading per id); `:410-470` turns Under/Changes/Supersedes into links; `gov decisions in-force` (`command.py:78`) | W5, W2, W6 | a parse of the heading and status by the loader is the only shape check → validate each entry against the schema in `gov decisions basis` and in T-1's `answer` (fix, W2-02, ~20 lines) |
| **Decision package** | `templates/decision-package.md` (10 headings; skill says 6); schema requires nothing | the CTO, by hand (189 in `governance/project/orchestration/packages/`) | **after**: schema family (`check/schema.py:35-36`) | a PROPOSED package holds tickets (`tasks/queue.py:61-62`; `status/command.py:79-90`) | W5 | one heading list; the page form (DEC-1236) → with T-1 |
| **Checkpoint** | `templates/checkpoint.md`; `schemas/checkpoint.schema.json` (requires `task, trigger, next_action, created, inputs`); a second copy at `schemas/records/checkpoint.schema.json` | `checkpoint/record.py:78-113`: deliberate → `docs/checkpoints/`, automatic → `.gov-runtime/scratch/checkpoints/`; Stop and PreCompact hooks (`hooks/stop.py:68-73`, only with `GOV_TICKET`); close at transition (`close/command.py:1436`) | **before write**: arguments (`record.py:88-95`); **after**: schema family | SessionStart hook (`sessionstart.py:150-179`) via `_latest()` (`record.py:116`); `gov checkpoint --resume`; `close/select.py:738`; **no launcher** reads one | W10, W15 | committed checkpoints stopped on 2026-11-14 (393 files; scratch 3,177, latest 2026-11-24); `decisions_applied` asked (`role-lead.md:75`) but not a `record.write` field; two schema copies → chore (one schema) + T-13 below |
| **Handover** (lead `CHECKPOINT.md`, CTO morning handover) | prose (`role-lead.md:72-75`); none for the CTO | by hand | **never** | the next session, by reading | W15 | DEC-1242 T-13: the handover in the checkpoint form, read by the launcher (fix, W1-25 + W2-207, ~40 lines) |
| **Close record** | `schemas/close.schema.json` (requires only `task`); no template | `close/command.py:1441-1470`; the queue through `close._record_and_close` (`queue/command.py:422`), commit `--no-verify`, trailers `Task`, `Role` only (`:426-427`) | **after**: schema family | `close/select.py:136-139` (`evidence.scope == "full"`, `evidence.head`: the green record the next selection starts from); `close/nightly.py:150-154`; status and release do **not** read it (release reads trailers, `release/patch.py:236-248`) | W11, W6 | what a close must hold (evidence, selection, impact list of T-11, fixes) is in no schema; 19 records, 6 with no evidence, silently ignored by the selection → `close.schema.json` requires `evidence` when written by the queue (fix, W2-206, ~15 lines); T-11's impact list into it |
| **The landing's own records** | code only: `queue.json` (`.gov-runtime/queue/<stamp>/`, `queue/command.py:76,474`); `select.json`, JUnit, `summary.txt`, `verify.exit` (`.gov-runtime/close/verify/<t>/`, `close/command.py:1724-1746`); nightly `docs/close/nightly/NR-*.json` (`close/nightly.py:483-485`) | `gov queue`, `gov close`, the nightly | never | the CTO; the next landing reads only the committed close record | W11 | `queue.json` is ignored runtime: a landing's notices (path, ticket, impact) are lost after the run → copy the notices into the close record (fix, W2-206, ~10 lines) |
| **Fix section** | none (prose, `.tickets/DAEO-xm6l.md:84-96`; `ticket.md:65` says the opposite) | an agent, by hand (14 of 271 tickets) | `queue/checks.py:14-16` needs `Task:` + `Fix:` trailers (H\*); `release/patch.py:150-173` reads `Fix:` | release notes, via the trailer only | W12 | the queue writes `fixes:` into the **close record** (`queue/fix.py:40-66`), not the ticket; its own commit has no `Fix:` trailer (`queue/command.py:412-413`) → A-15: the queue writes `## Fix:` from the trailer (fix, W2-115b, ~30 lines); `ticket.md:65` brought in line (chore) |
| **Chore trailer** | none (`Task: chore` vs `Task: emergency-2` in briefs) | by hand | never (`--direct` is built per DEC-1242 T-2 but nothing reads the form) | digest, patch notes (`release/patch.py:236-254`) | W12 | one trailer form (B5, A-16, A-32) (chore + fix, W2-115b) |
| **Lead's return** | **two forms that disagree**: `role-lead.md:77-82` (status word, `gov links` quote, reviewer verdict path) vs `LEAD-COMMON.md:30` (branch, head, KPI evidence, reds not yours; `:25` says no review) | the lead, by hand | **never**: a lead is a top-level session, so SubagentStop does not run; `session_watch/transcript.py:48-53` reads only `IDLE-REASON:` | the CTO, by reading | W10, W11 | one form in `role-lead.md` (kernel text, CTO's, §3.5), held in code: `return.schema.json` + a check when the lead's session ends (A-7; I-10 "no open question") (fix, W2-21, ~50 lines) |
| **Helper's return** | `TWELVE_FIELDS` (`hooks/subagentstop.py:14-19`; product copy identical) | the helper | **before accept** H: label present with text on the same line (`:33-36`), every subagent type, no matcher; an error inside the hook also blocks (`:64-67`) | the lead, by reading | W10 | a label followed by a list on the next line is refused (it blocked two of this audit's helpers); no matcher → 015a F12 (fix, W2-11, ~15 lines) |

### 1.4 Memory measure, usage, adoption, release, update (W1, W4, W13-W15)

| Record | Form | Writes it | Checks it, when | Reads it next (relies on) | Step | Missing → fix (owner) |
|---|---|---|---|---|---|---|
| **Questions** `qNN.yaml` | code only (`memaudit/preflight.py:29-30`) | writer agent (B10, `memaudit/briefs/writer.py:5`) | **before** H: `gov memaudit preflight` (`preflight.py:83-93`); `deliver` DL-* | declare and measure via the set digest (`memaudit/common.py:120-123`) | W4 | no schema file (fine while code holds it); the `forbidden` count (A-9, e2/d5) |
| **Declaration** `DECLARATION.json`, `USED` | code only (`memaudit/declare.py:280-285`: commits, store sha, `gov_pin`, set digest, settings) | `declare.py:291,295`; `USED` `:172` | **before** H: a second declare refused (`USED`) | `measure.py:145,194-195`; `judge.py:195-196`; `standing.py:182` | W4 | models and release version absent (only `gov_pin`) |
| **`FIGURES.json`** | code only (`memaudit/figures.py:118-136`; models added at `judge.py:272`) | `judge.py:273`; `classes.py:25` | re-run guard only (`judge.py:200`); shape never | `measure.py:66`; `digest.py:45-48`; `standing.py:182`; `fresh.py:313`; **no reader in `src/gov/release/` or `gov status`** | W4→W13 | **no stamp** (release, gov commit, audit commit, store commit, rule version) and **no gate** → A-9 stamp (copy the declaration's commits in) + A-13 release gate reads the latest verdict (fix, W2-204 + W2-209, ~40 lines) |
| **Transcript scan** | a returned dict (`memaudit/scan.py:204`) | under `fresh`: `COUNTS.json` `st["scan"]` (`fresh.py:291-311`); standalone `gov memaudit scan` prints only (`command.py:103-125`) | **at close of the run** H: a finding voids the run (`fresh.py:297-311`) | none outside `fresh` | W4 | the standalone scan leaves no record → write `SCAN.json` with window and commit (fix, W2-198, ~15 lines) |
| Memory-audit config | `governance/project/memory-audit.yaml`; `schemas/memory-audit.schema.json` **loaded by no code** | by hand | **typed**: `gov memaudit check` (`memaudit/__main__.py:123`); `config.load` closed keys (`config.py:26,402`) | judge, brief, deliver, preflight | W4 | the schema is dead text → load it in `config.load` or delete it (chore, W2-204) |
| **Usage figures** | none (one free-text line) | scratch `usage_log.sh:19` → `log/usage.txt` | never | scratch `cto_watch.sh`, `measure_week.py` | W15 | outside the product (tool map row 83, A-36, no code) → W2-207 |
| **Context figures** | none (stdout) | scratch `context_measure.py:1-15` | never | none | W15 | no kept record; absorb (tool map row 85) → W2-207 |
| Capacity samples | none | scratch `capacity_sampler.py:31` → `log/capacity-samples.jsonl` | never | its own `--summary` | W15 | absorb into `gov resources --sample` → W2-207 |
| Session records | code only (`launch/session_record.py:1-14,56,182-187`) | `session_record.py:274` via `launcher.py:1212-1225` | never | `spend/brake.py:5,27` | W15 | no daily usage or context total from them → W2-207 (the daily figures P-1 schedules) |
| Memory-use log | code only (`memory_use/__init__.py:5-9`) | `memory_use/__init__.py:72-94` (from `retrieve/command.py:144`, `brief/command.py:61`) | never | `gov memory-use` | W15 | — |
| **Adoption stage records** A0-A4, A6, A8, A9 | code only (`adopt/project.py:193-196`: `stands_on` = previous record's sha256) | `Run.finish`, one commit each (`adopt/stages.py:50-57`), `governance/adoption/<stage>-<title>.md` | **before next stage** H: `project.chain` (`project.py:175-190`: `STAGE_MISSING`, `CHAIN_BROKEN`) | A3 needs A1 (`stages.py:479`); A6 needs A0 and A4 (`:684-706`) | W1 | A2 classifies with doctor's grammar → §3.4 |
| **A3 target path map** | the proposal's `artefacts` (`stages.py:214-230`) | the caller's proposal, recorded by A3 | **before** H: proposal refusals (`stages.py:474-505`); A5/A6/A7 hold the hash (`lite_gates.py:157-171`) | A4 plan (`stages.py` `_plan`), A5 review | W1 | does not refuse a path in two namespaces (A4, DEC-1238 (1c)) → §3.5 item 2 |
| **Auditor's verdict files** (A5, A7, A10) | free front matter; `adoption-verdict.schema.json` registered (`check/schema.py:53`) but **no code writes that type** | an auditor, by hand (`--verdict <path>`, `adopt/command.py:34`) | **before** H: `stages.py:541-565`, `lite_gates.py:62-105` (`NO_VERDICT`, `VERDICT_NOT_PASS`, `VERDICT_OTHER_RECORD`, `VERDICT_NOT_INDEPENDENT`) | A5, A7, A10 | W1 | A5 uses another key set than A7/A10 (B16) → one schema, gates validate against it (fix, W1-41, ~20 lines) |
| AS spec audit record | as stage records | `adopt/spec_audit.py:276` | **before A3** H: `spec_audit.gate` (`:310-314`) | A3 | W1 | — |
| **Adoption verdict** (CAP-44.h) | on `e2/d1-verdict` only (`3acad31a9`, `3f2050653`), not merged | — | — | — | W1 | the merge (W2-210, 0.1.6 per DEC-1231) |
| **Release record** `docs/releases/<v>/manifest.json`, `.sha256` | code only (`release/__init__.py:216-217`) | `release.build` (`:218-222`); the owner commits and tags | **typed**: `release.verify` | `update/core.py` (verifies at tag), `update/pending.py:64`, `release/patch.py:78` | W13→W14 | no memory or adoption input to the release (A-13) |
| Patch cut records `kind.json`, `gates.json`, `suite.json`, `NOTE.md` | code only (`release/__init__.py:451-453`) | `release/cut.py:4-14` | **before cut** H\* (switched off, DEC-1223): G0-G4 (`release/gates.py:63-182`) | `release/repin.py:402-403` | W13 | no gate reads `FIGURES.json` |
| Release authority | `governance/project/release-authority.yaml`; code only (`gates.py:63-93`) | by hand, decision commit | **before** H\*: G0 | G0 | W13 | — |
| Re-pin record `repin.json`, `rollback.sh` | code only (`repin.py:408-410`) | `repin.py:408-460` | never | none traced | W13 | — |
| **Update record** `governance/updates/<B>.json` | code only (`update/core.py:595-598`) | `core.py:599`, one commit | **at the update** H: overlay, drift and pin checks, rollback on failure (`core.py:593`) | `gov update --rollback` (`core.py:730`) | W14 | no doctor or coverage check after the update (§3.5 item 6) |
| Rollback record `<B>.rolled-back.json` | code only (`core.py:702`) | `core.py:700-704` | never | none | W14 | — |

**Where the rows stand:** only the questions, the declaration, the adoption chain and its gates, the helper's return
(by label) and the update record have a fixed form and a code check on Gov OS's path today. Everything else is checked
off the path (inside `gov queue` or `gov brief`), only when typed, after the landing, or never.

---

## 2. The chain of hand-offs, W1 to W16

Each line: record → next tool or job · **H / H\* / C / A** · the break, if any.

| # | Hand-off | Held | Break |
|---|---|---|---|
| 1 | kit `path-map.yaml` → `gov adopt` A2 classification (W1) | H (refuses `NO_PATH_MAP`, `project.py:211`) | **A2 uses doctor's `fnmatch`**: a root `*` classes everything as one namespace (§3.4) |
| 2 | A2 → A3 target path map → A4 plan → A5 verdict → A6 (W1) | H (`stands_on` chain; A5 hash) | a path in two namespaces passes A3 (A4 not built) |
| 3 | A7/A10/AS → verdict (W1) | H for the gates; verdict stage not merged | CAP-44.h (W2-210) |
| 4 | path map → `gov rebuild` (namespaces, `lexical_policy`, `embedding_policy`) (W2) | H (`config/loader.py` validates; `retrieval/lexical.py:154-186`) | an unmapped path is indexed by default: a hidden-set file in no evaluation namespace would be indexed (fails open) |
| 5 | commit → store refresh (W3) | H (hook, after-step) | no retry, the store 584 paths behind (I-9, G-1) |
| 6 | memaudit config + questions → declaration → reader/grader → `FIGURES.json` (W4) | H inside `fresh` | |
| 7 | `FIGURES.json` → digest, release (W4→W13) | **A** (nobody reads it but the CTO) | no stamp, no gate (A-9, A-13) |
| 8 | decision record → register → store links, `in-force` (W5→W2) | C (basis typed; schema after) | no level; owner approval skipped (`authority.py:44`) |
| 9 | register / spec / ticket change → affected tickets and tests (W6) | **A** (`gov impact` called by nothing; I-5) | T-11: `gov impact --changed` in the after-step, into the close record |
| 10 | spec K-lines → ticket `kpis` (W7) | H at creation by `gov discover`; then **A** | **no drift check** (`KPI_DRIFT`) |
| 11 | ticket paths (`allowed_paths`, `reads`, `needs`) → plan, brief (W7) | H\* (non-empty, ready) | **never checked against the path map** |
| 12 | ticket + template + facts + memory + path map → brief (W8) | H\* (`gov brief`) | **50 of 50 briefs by hand**; launch takes none (G-3) |
| 13 | brief → `gov launch` → launch record (W8) | **A** | no brief hash; no launch since 16 Nov (audit 4) |
| 14 | role template → agent file → session (W8) | C (byte copy typed) | literal slots reach the session (A-24) |
| 15 | ticket `kpis` → designer's tests + README map (W9) | C (`gov accept` typed); H\* at the queue | 66 of 188 maps fail; red on the base unchecked (A-3) |
| 16 | tests → engineer (TESTS-READY) (W9→W10) | **A** | marker read by no code |
| 17 | helper → lead (twelve fields) (W10) | H (label check) | multi-line values refused (015a F12) |
| 18 | lead → CTO (return) (W10→W11) | **A** | two forms, no check (A-7) |
| 19 | branch → `gov queue` → close record (W11) | H\* (refusals, selection, acceptance, authorship, dirty worktree) | Gov OS lands by hand (DEC-1239 (3)); notices die in `queue.json` |
| 20 | merged tree → path-map coverage (W11) | **C** (`core-pathmap` in the after-step, notice) | the 6 unmapped files of 22 November went unseen |
| 21 | close record → next selection's base (W11→W11) | H\* (`evidence.scope == "full"`) | 6 of 19 records with no evidence are skipped silently |
| 22 | fix commit (`Fix:`) → close record `fixes:` → release notes (W12→W13) | H\* (trailer check) | ticket's `## Fix:` section by hand; queue's commit has no `Fix:` |
| 23 | chore → digest (W12) | **A** | no trailer form (A-16, A-32) |
| 24 | release manifest → `gov update` (W13→W14) | H (verify at tag) | release gates off (DEC-1223) |
| 25 | `gov update` → adopted path map (W14) | H (adds `governance/updates/**`, `update/pathmap.py:1-8`) | no coverage check after the update |
| 26 | handover → next CTO / lead (W15) | **A** | T-13 (checkpoint form, read by the launcher) |
| 27 | usage / context → daily figures (W15) | **A** (scratch) | W2-207 |
| 28 | the schedule → W16 checks (doctor, measure, regression) | **A** (nothing scheduled) | P-1, T-5 |

**Totals:** of 28 hand-offs, **H 9**, **H\* 6** (held in a tool Gov OS bypasses; row 15 counted here), **C 3**, **A 10**
(row 10 counted as A: held only at creation). The breaks that
matter most for the integration test (DEC-1240's planted cases): 12-13 (brief and launch), 18 (lead return), 15-16
(red on the base), 20 (coverage at the landing), 7 (memory figure).

---

## 3. The path map (G-8)

### 3.1 Where it lives

| Copy | Path | Size | Notes |
|---|---|---|---|
| Gov OS | `governance/project/path-map.yaml` | 736 lines | first namespace `root-files: ["*"]` (`:8-9`); `docs/emergency-2/*` and four subfolders in `docs` (`:58-62`); archive `:143` |
| The kit | `template/governance/project/path-map.yaml` | 26 lines | six namespaces; "`copier update` never overwrites it" (`:1-2`); no root `*` |
| EXAMIN | `/home/usain/gov-os-runs/W2-27/examin/governance/project/path-map.yaml` | 319 lines | 18 namespaces (`:20-259`), no root `*` |
| Adoption A3 | `governance/adoption/A3-target-path-map.md` (the proposal recorded), hashed into A4-A7 | — | A3 records a proposal; the caller writes the map itself |
| Schema | `template/governance/kernel/schemas/path-map.schema.json` | — | "Every tracked path matches a pattern of exactly one namespace" (`:10`); grammar: "`*` stays inside one folder, `**` crosses folders" (`:145`) |

### 3.2 Every tool that reads or writes it

**Writers:** an agent, by hand (Gov OS, EXAMIN); adoption A3 records the target (`adopt/stages.py:214-230`, `:474`);
`gov update` adds one line `governance/updates/**` as a text merge (`update/pathmap.py:1-8,90-91`; `update/core.py:182-191`).
Nothing else writes it.

**Readers** (49 product files name it; the ones that act on it):

| Reader | Path:line | What it uses | Matcher |
|---|---|---|---|
| `core-pathmap` (G1, hard-block declared) | `check/pathmap.py:75-112`; `kernel/checks/core-pathmap.yaml:1-5` | every tracked path in exactly one namespace | the map's (`:43-46`) |
| the queue's after-step | `queue/after.py:8`; `check/structural.py:44` | runs `core-pathmap` as a **notice** | the map's |
| `gov doctor` `path_map` part | `doctor/command.py:604-633` | unmapped paths only, no doubles | **`fnmatch`** |
| `gov doctor` `path_compliance` part | `doctor/command.py:636-668` | moved-file references (not the map) | — |
| adoption A2 | `adopt/project.py:200-216` ("the same one, not a second"), `stages.py:186-192` | first namespace that matches | **doctor's `fnmatch`** |
| adoption refactor plan | `adopt/refactor_plan.py:85-94` | proposes fixes for none / two | the map's (`util/patterns`) |
| adoption A3, policies | `adopt/stages.py:433-441`; `fabric.py:502,521,793`; `safety.py:167-205` | `embedding_policy`, code intelligence, hash | — |
| A7 gate | `adopt/lite_gates.py:157-188` | the A3 hash | — |
| config load | `config/loader.py:306-327`; `config/path_map_schema.py` | schema validation | — |
| memory build | `rebuild/command.py:43-57,402`; `retrieval/lexical.py:149-186` | `lexical_policy`, `embedding_policy`; `id_forms` | the map's |
| memory store | `store/loader.py:53,150-175` | the register's path (`REGISTER_KEY`) | — |
| retrieval authority | `retrieval/authority.py:26,100` | authority keys | — |
| role read-denies (guard parts) | `util/role_paths.py:41,74,355-365`; `util/parts.py:20,394` | `<role>.reads_denied` | `fnmatch` for shared names (`role_paths.py:301`) |
| the landing's records and history | `close/history.py:25,44`; `close/ratchet.py:41-44`; `close/gates.py:153,261`; `close/traceability.py:119-135` | register key, trailers base, base keys | — |
| test-run workers | `queue/full.py:39-45` | worker count | — |
| memory measure | `memaudit/preflight.py:32,205-235`; `declare.py:77-118` (writes the set's entry in the **sets** tree's map) | evaluation namespaces and sets | **`fnmatchcase`** (wider: fails safe) |
| secrets filter | `secrets/__init__.py:490,508` | namespaces | its own |
| impact trace | `impact/readings.py:78` | namespace of a path | the map's |
| links | `links/check.py:197,641` | the map as a record | — |
| landing selection | `close/select.py:40-44` | **not the map**: `allowed_paths`, the test map's `record_only` | the map's grammar (`util/patterns`) |
| `gov brief`, `gov plan`, `gov launch`, readiness, dispatch, discover | — | **do not read it** (helper 1) | — |

So: memory, the guard's read-denies, the memory measure, adoption and doctor rely on the map; the landing relies on it
only through the after-step notice. **Which documents are records is decided by the test map's `record_only`
(`test-map.yaml:46-49`, `select.py:791-855`), not by the path map** (the owner's card G-8 says the path map).

### 3.3 Does it cover every tracked file exactly once? (measured 2026-11-24, read-only)

Method: `git ls-files`, then each product matcher over each namespace's patterns (scripts in `/tmp`, nothing written to
either repository).

| Repository | Tracked | `core-pathmap` (the map's grammar): none / two | `util/patterns` (selection, store): none / two | `memaudit/config`: none / two | doctor (`fnmatch`): none / two |
|---|---|---|---|---|---|
| Gov OS | 5,551 | **6 / 0** | 6 / 0 | 6 / 0 | **0 / 5,543** |
| EXAMIN | 3,910 | **0 / 0** | 0 / 0 | 0 / 0 | 0 / 0 |

- **Gov OS's six unmapped files:** `docs/emergency-2/integration/DECISIONS-HELD.md`, `DECISIONS-PAGE-2026-11-22.html`,
  `FINDINGS.md`, `GOLDEN-WORKFLOW-CORRECTIONS.md`, `TOOL-MAP.md`, `golden-workflow-decisions.html`. The folder was made
  on 22 November (`51236b741`, `87dcf68a2`, `cf4265828`); `path-map.yaml:58` holds `docs/emergency-2/*` (one level)
  and four named subfolders, not `integration/`. **This file is the seventh** once committed.
- **Doctor sees no gap** because `fnmatch`'s `*` crosses `/`, so `root-files: ["*"]` holds every file; the same makes
  5,543 files "doubly classified" (for example 2,296 `tests` files also `root-files`), which doctor never checks.
- **EXAMIN agrees under every matcher.** Its "doctor path check" failure is the other part, `path_compliance` (moved
  references: 3,626 in audit 6, `docs/emergency-2/audits/06-examin.md:48`, finding F-009), not coverage. I re-ran it
  read-only; on EXAMIN it did not finish in 280 s (exit 143), so I have no new count.

### 3.4 Its cracks so far

| Crack | What happened | Cause in code | State |
|---|---|---|---|
| **I-2** (22 Nov) | a record-only document a fix branch wrote refused the landing | the test map's selection, not the path map (`select.py:849`) | fixed in 0.1.5 (`8555186af`): placed with a notice `RECORD_PLACED` (`select.py:884`) |
| **W2-81's A4** | the rust adopter's map put `governance/project/audits/**` in two namespaces; A9 stopped `FABRIC_INCOMPLETE` naming no file (`W2-81-PROVING-RUN-0.1.4-ANALYSIS.md:87,190`) | A3 and doctor do not check doubles; A2 takes the first match (`project.py:214-215`) | **open**: a fix under W1-41 (DEC-1238 (1c)); `refactor_plan.py:126` claims "`gov doctor` lists no path held by two namespaces", which doctor cannot do |
| **Release folders, 18 Nov** | `docs/emergency-2/release-0.1.3/` in no namespace turned tests red | no coverage check at commit; hand commit | fixed by hand (`4c7bdc77d`, `release-*/**`) |
| **Integration folder, 22 Nov** (new) | six files in no namespace for two days | the same: the check runs only in the queue's after-step | **open** (§4 fix 1) |
| **Two grammars** (new) | doctor and A2 read `*` as crossing folders; Gov OS's own A2 record classes 1,712 of 1,712 files `root-files` | `doctor/command.py:604-615`; `adopt/project.py:207` | **open**; contradicts the schema (`path-map.schema.json:145`), so a fix, not a question |
| **EXAMIN's doctor** | `path_compliance` fails | substring matches of moved paths (audit 6 row 12) | open, F-009; outside the path map |

### 3.5 What makes it the one source (the owner's G-8 (a)), each with its smallest code

| # | Piece | Today | Smallest code | Size | Owner |
|---|---|---|---|---|---|
| 1 | **One matcher** | 3 grammars (§3.2) | doctor's `_check_path_map` returns `check.pathmap.check(root)` (unmapped and doubled, named); `adopt/project.classify` uses `check.pathmap._matches` (made public as `pathmap.matches`) and reports a double instead of the first match. Failing tests first: a planted map with `"*"` and an unmapped `sub/x` → doctor fails; a double → doctor names both. `memaudit/preflight` may stay wider (it fails safe), said in a comment | ~25 lines + 2 tests | fix under W1-27 (doctor) and W1-41 (A2) |
| 2 | **Exact coverage proved in doctor and at adoption** | doctor unmapped only; A3 no doubles | item 1 gives doctor; A3 refuses a proposal whose resulting map leaves a tracked path in none or two (`stages.py:474-505`, one call to `pathmap.check` on the proposal) | ~15 lines | fix under W1-41 (the A4 fix, DEC-1238 (1c)) |
| 3 | **Ticket paths checked when planned** | not at all | in `gov brief`'s ready check (and `gov plan`): each `allowed_paths`, `reads`, `needs` glob's fixed prefix (the part before the first `*`) must fall under a namespace of the map; a write path in an evaluation, hidden-set or archive namespace is refused. Codes `PATH_UNMAPPED`, `PATH_FORBIDDEN_NAMESPACE` | ~40 lines | fix under W2-152 (brief), W2-136 (plan) |
| 4 | **`gov brief` takes each job's paths from the ticket and the map** | `{PATHS}` from `allowed_paths` only (`build.py:398`) | the brief prints, for each ticket path, its namespace, and the role's `reads_denied` from `util/role_paths.expand` (already computes them, `:355-365`); generated at launch per G-3 | ~30 lines | fix under W2-152, with G-3's launch change (W2-21) |
| 5 | **The landing checks the same** | after-step notice (`queue/after.py`) | before the merge, `pathmap.check` on the merged tree, restricted to paths the change adds or renames; refuse those in none or two, naming the line to add (SQ-R1 for refuse vs notice); doubles of existing paths stay a notice | ~25 lines | fix under W2-206 (after-step) / W2-115b |
| 6 | **Kept current by adoption and `gov update`** | update adds `governance/updates/**` and nothing more | after `gov update` merges, run `pathmap.check` and write its count into the update record (`update/core.py:595-598`); a new kit folder the adopted map does not hold becomes a notice with the line to add | ~15 lines | fix under W2-17 |
| 7 | **Scheduled** | nothing | doctor in W16's weekly run (P-1, T-5) carries item 1 | 0 (schedule line) | W2-207 |
| 8 | **This repository's map exact** | 6 unmapped | add `docs/emergency-2/integration/**` to `docs` (`path-map.yaml:58-62`) | 1 line | chore |

With 1, 2, 5 and 8, code proves exact coverage at every landing (in the scratch repository and EXAMIN; in Gov OS once
it moves onto its own tools, DEC-1239 (4)) and in doctor; 3 and 4 make briefs carry it; 6 keeps adopted maps current.

---

## 4. Fixes, in order

Order: what the integration test (DEC-1240) needs first, smallest first within a group. **Kind:** fix under the
owning ticket (failing test first), chore, or new feature (owner's yes).

| # | What | Where | Kind (owner) | Size |
|---|---|---|---|---|
| 1 | `docs/emergency-2/integration/**` into `docs` | `governance/project/path-map.yaml:58-62` | chore | 1 line |
| 2 | One matcher: doctor and A2 use the map's grammar; doctor reports doubles | `doctor/command.py:604-633`, `adopt/project.py:205-216`, `check/pathmap.py:43` | fix, W1-27 + W1-41 | ~25 + tests |
| 3 | A3 refuses a map with a path in none or two (A4) | `adopt/stages.py:474-505` | fix, W1-41 | ~15 |
| 4 | Coverage at the landing on added paths (after SQ-R1) | `queue/command.py` pre-merge, `queue/after.py` | fix, W2-206 | ~25 |
| 5 | Ticket paths checked against the map in the ready check and `gov plan` | `brief/build.py:157-186`, `plan/derive.py` | fix, W2-152 + W2-136 | ~40 |
| 6 | `gov launch` builds or takes the brief, re-runs the ready check, records brief and template sha256; brief prints each path's namespace and the read-denies | `launch/command.py:52-81`, `launcher.py:857,911-928`, `brief/build.py:398` | fix, W2-21 + W2-152 (G-3, A-6) | ~90 |
| 7 | `keys.yaml` no longer lets a slot escape; `facts.yaml` schema checked in `gov brief` | `brief/build.py:218,333-337` | fix, W2-152 + W2-128 | ~20 |
| 8 | Literal slots out of the agent files | `adapters/portability.py:196-208` | fix, W2-153 (A-24, 015a F11) | in flight |
| 9 | One lead return form, `return.schema.json`, checked at session end; "no open question" | `templates/role-lead.md:77-82` (CTO, §3.5), `LEAD-COMMON.md:30`, new check | fix, W2-21 (A-7, I-10) | ~50 |
| 10 | Helper return: values on the next line accepted; a matcher | `hooks/subagentstop.py:33-36` | fix, W2-11 (015a F12) | ~15 |
| 11 | `KPI_DRIFT`: ticket `[Kn]` vs spec K-lines; `specification` in the schema | `links/check.py:86-87,556`, `ticket.schema.json` | fix, W2-129 + W2-02 (A-23b; SQ-R2) | ~45 |
| 12 | Ticket schema: `kind` required, `class` enum, `acceptance_tests.path`, `specification`; then the 271-ticket migration | `ticket.schema.json:6,44,71` | fix, W2-02 (R-3) + chore | ~15 + migration |
| 13 | Ticket and `openspec/**` changes reach the schema check at the landing | `close/command.py:77-86`, `check/schema.py:27` | fix, W1-26 / W2-206 | ~5 |
| 14 | The 66 failing README maps fixed or retired | `tests/acceptance/*/README.md` | chores and fixes per folder (G-2) | 66 folders |
| 15 | Red on the base checked at TESTS-READY | `queue`, `accept` | fix, W2-115b + W2-96 (A-3) | per audit 4 |
| 16 | Close record requires `evidence` when the queue writes it; landing notices and T-11's impact list copied in | `close.schema.json`, `queue/command.py:422,474` | fix, W2-206 | ~25 |
| 17 | The queue writes `## Fix:` in the ticket from the trailer; its commit carries `Fix:` | `queue/fix.py:40-66`, `queue/command.py:412-413` | fix, W2-115b (A-15) | ~30 |
| 18 | `FIGURES.json` stamped from the declaration; a release gate reads the latest verdict | `memaudit/figures.py:118-136`, `release/gates.py` | fix, W2-204 + W2-209 (A-9, A-13) | ~40 |
| 19 | Standalone scan writes `SCAN.json` | `memaudit/command.py:103-125` | fix, W2-198 | ~15 |
| 20 | Handover in the checkpoint form, read by the launcher; one checkpoint schema | `checkpoint/record.py`, `launch/`, `schemas/records/checkpoint.schema.json` | fix, W1-25 + W2-207 (T-13); chore | ~40 |
| 21 | Decision record level fields, `gov decisions answer`, the register entry validated | `decisions/`, `register-entry.schema.json` | **new feature, approved** (DEC-1236, DEC-1242 T-1, R-6) | per its spec |
| 22 | One verdict schema for A5/A7/A10; merge W2-210 | `adopt/stages.py:541-565`, `lite_gates.py:62-105` | fix, W1-41; W2-210 merge (0.1.6) | ~20 |
| 23 | `gov update` runs the coverage check into its record | `update/core.py:595-598` | fix, W2-17 | ~15 |
| 24 | Usage, context and capacity figures into the product | scratch → `src/gov` | W2-207 (A-36) | per W2-207 |
| 25 | Dead schemas: load `memory-audit.schema.json` or delete it; one chore trailer form | `memaudit/config.py`; briefs | chores | small |

**Summary for the owner.** The records Gov OS passes along mostly exist and most have a writer, but the hand-offs
between them are held by code in only 9 of 28 places on today's path; 6 more are held inside `gov queue` and `gov
brief`, which Gov OS bypasses, and 10 rest on an agent alone, chiefly the brief, the launch, the lead's return, red on
the base and the memory figure. The path map is the best-kept record: EXAMIN's covers all 3,910 files exactly once, and
Gov OS's misses only six files in the integration folder made on 22 November. But two cracks matter more than the
count. First, nothing checks coverage where work lands (only a notice after a `gov queue` landing), so a new folder
goes unmapped until a test happens to fail. Second, `gov doctor` and adoption read the map with a different glob rule
from the schema, the landing and memory: on Gov OS's own map doctor reports "pass" with six files missing, and
adoption files every one of Gov OS's files under one namespace, as its own A2 record from October shows. The fix is
small and mostly one matcher: doctor and adoption use the map's own rule and report doubles (about 25 lines), A3
refuses a double (the A4 fix you already ruled a fix), the landing checks the paths a change adds, and briefs and
plans check each ticket's paths against the map; then the map can be the one source briefs, the landing and memory
rely on. One question needs you (SQ-R1: refuse or notice at the landing); the rest are fixes under closed tickets or
chores.

---

## 5. Spec questions (DEC-1238 (10))

### SQ-R1. At the landing, is a path the change adds that the path map does not hold exactly once a refusal or a notice?

- **Found:** G-8 (a) says "code proves it covers every tracked file exactly once, at every landing". DEC-1239 (2) says
  "a record-only document a branch writes is placed as a record with a notice at the landing, never refused". The two
  meet on a new document in a folder no namespace holds (the integration folder, the release folders of 18 November).
  An unmapped path fails open where it matters: memory indexes it by default (`retrieval/lexical.py:154-186` keeps out
  only what a not-indexed namespace matches), so a hidden-set file put outside the evaluation namespace would be
  indexed, and the guard's read-denies do not cover it.
- **Options:**
  - (a) **Refuse** a path the change adds or renames that falls in no namespace or in two, naming the line to add; the
    branch adds one line and re-lands. Cost: one bounce per new folder (two such folders in the last week: 18 and 22 November).
    DEC-1239 (2) stands, because it is about test selection, not classification.
  - (b) **Notice** at the landing and fail doctor; the CTO adds the line as a chore. Cost: the drift seen on 22
    November (two days unmapped) stays possible; a hidden-set leak is caught only by the memory measure's scan.
  - (c) Refuse only a path in an evaluation or hidden-set folder, or in two namespaces; notice for the rest. Cost: a
    second rule to keep; most new folders still drift until someone reads the notice.
- **Recommendation:** (a). It is what G-8 (a) asks, the cost is one line in the same branch, and it is the only option
  that closes the fail-open case in ordinary work.
- **Sources:** DEC-1241 G-8; DEC-1239 (2); `queue/after.py:8`; `path-map.yaml:58-62`; §3.3, §3.4.
- **Stops work:** no. Fixes 1 to 3 and 5 to 25 go on; only fix 4's refuse/notice line waits.

### SQ-R2. The ticket's `specification` field: code reads it, no schema or decision states it

- **Found:** `readiness/checker.py:101` and `tasks/queue.py:80` (`SPEC_NOT_CLOSED`) read `specification`;
  `discover/tickets.py:114` writes it; `ticket.schema.json` does not name it; 0 of 271 tickets carry it. `KPI_DRIFT`
  (fix 11) needs one field that links a ticket to its spec; tickets link specs today only through `sources` ids.
- **Options:** (a) add `specification: <path to the spec>` to the schema, required when `kind: feature` (R-3), and use it
  for `KPI_DRIFT`; cost: the R-3 migration fills it for the feature tickets that have a spec. (b) Use `sources` (an id
  of a spec in the list) and retire `specification` from the readers; cost: an id must resolve to a spec file, which
  `gov links` does today for DEC and CAP ids only. (c) Leave it; cost: the drift check has nothing to read.
- **Recommendation:** (a): one explicit path is what a code check can rely on, and discover already writes it.
- **Sources:** helper 1 rows; DEC-1242 R-3; tool map §4 fix 3.
- **Stops work:** no; fix 11 waits on it, nothing else.

**Not raised as questions (decided by text already, so fixes):** the glob grammar (the schema states it,
`path-map.schema.json:145`); the lead's return form (kernel text, the CTO's under EMERGENCY-2 §3.5, and green work needs
no review, so `LEAD-COMMON.md:25` is right and `role-lead.md:77-82`'s reviewer path goes); R-3's count (271 tickets, not
219, a fact for the migration chore).

---

## 6. What I could not verify

- EXAMIN's `path_compliance` today (the read-only run did not finish in 280 s).
- The memaudit run-folder and `COUNTS.json` path patterns (`layout.paths`, not traced); who calls `gov memaudit digest`.
- Whether `gov check`'s schema scan reaches `governance/adoption/` verdict files.
- The reader of `role-cto.md` beyond `start_cto.sh` (audit 4 says it reaches no session); `build_lead_brief.py` (scratch).
- Which test turned red on 18 November for the release folder (the commit message says "follow-up reds"; I did not run
  the suite).
