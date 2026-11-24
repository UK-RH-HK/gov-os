`docs/emergency-2/proposals/DECISIONS-BY-PAGE-SPEC.md` · the product-spec session of the Gov OS CTO, 2026-11-22 · **proposed, for the owner's yes** (DB-1 to DB-5 below); nothing is built, no ticket file exists, the file is not committed

Decisions cited: DEC-1217, DEC-1219, DEC-1214, DEC-1224, DEC-1223, DEC-1222, DEC-1227, DEC-1231, DEC-861, DEC-862, DEC-818, DEC-308, DEC-328, DEC-220, DEC-093, DEC-850, DEC-855, DEC-1204. Sources: the owner's brief of 2026-11-22, EMERGENCY-2 2.1, 3.5, 4.1, 4.2, 4.6, 7.6, 10.1, T2-ESCALATION-RUBRIC 2 to 4, docs/DECISION_REGISTER.md (DEC-1214, DEC-1217, DEC-1224, DEC-1225 to DEC-1231), docs/emergency-2/audits/DECISIONS-FOR-THE-OWNER.md, docs/emergency-2/audits/OWNER-DECISIONS-2026-11-18.md, docs/emergency-2/L2-COMMANDS.md section 0, docs/emergency-2/G5-APPROVAL.md, docs/emergency-2/proposals/RELEASE-ON-BEHALF.md and IMPORTS-ADOPTION-SPEC.md (the form), template/governance/kernel/templates/decision-package.md and decision-record.md, template/governance/kernel/schemas/decision-package.schema.json, template/governance/kernel/skills/orchestration/SKILL.md and briefs-and-returns.md, src/gov/decisions, src/gov/adopt/stages.py (`_package`), src/gov/status/command.py, src/gov/close/history.py (`owner_decision`), src/gov/release/cut.py, memory's bundle for "owner decision page answer sheet".

# Decisions by page

`docs/emergency-2/proposals/DECISIONS-BY-PAGE-SPEC.md` · 2026-11-22 · written by the spec-writing method (problem, goals and non-goals, KPIs each with its verify and failure line, test data, open questions as owner options) · for the owner's decision; after release 0.1.5

**In five lines.** (1) Every question that needs you is one structured record, the existing decision package with its fields made machine-readable: question, what was found, options each with cost and consequence, recommendation with reason, sources, and what it blocks. (2) The CTO gathers the open ones into one batch, and code renders one self-contained, phone-first HTML page from it: a card per decision, tap an option, type a note, copy the answer sheet. (3) The sheet is a fixed text block that carries the batch id and a hash of the batch, so it answers exactly the page you saw. (4) `gov decisions answer <sheet>` checks the sheet and writes each answer into the register, by code, in the register's entry form, with `Decided-by: owner (page <batch id>)`; a second paste changes nothing. (5) The escalation rubric sends every decision that is yours through the page, and a decision that stops work still pushes at once. **This adds two actions to the existing `gov decisions` command (no new command), and changes kernel text (the package template, the rubric lines) that is the CTO's to change once you say yes.**

## Problem

**The incident.** Decisions come to you as long chat messages, and your answers are written into the register by hand.

- **One message, thirty questions.** `docs/emergency-2/audits/DECISIONS-FOR-THE-OWNER.md` put 27 coded questions (L1 to Q-CAP44) in one message, each with its options and a recommendation in bold. You answered with a code line. Your 2026-11-19 line "L2-1 yes, L2-2 yes, L2-3 a, ... K1-1 Opus" held 13 answers.
- **Hand transcription.** The CTO turned each such line into one register entry by hand: DEC-1214 holds more than twenty answers in one entry, DEC-1217 seven items, DEC-1227 nine. Each answer is the CTO's paraphrase of your code, so what is recorded is the CTO's reading, and the reading can be wrong. It was: DEC-1224 recorded "X12" as EXAMIN's "D-X12, the Socratic constraint"; the EXAMIN CTO found on 2026-11-20 that X12 was a different item (label each expanded search term patent or scientific), and the register was corrected by hand in `51edaa44d`.
- **Relay.** EMERGENCY-2 1.4 counts 544 owner messages in 31 days, of which 140 were package answers and 134 relays [P1 §2]. Most of a package answer is typing a code back, on a screen that is often a phone.
- **No way to answer one thing and leave the rest.** A long message is answered whole or later; a decision that stops work waits behind nine that do not.
- **Today's package form does not help the owner.** `decision-package.md` has six prose parts (DEC-818) and a cap of five open packages (DEC-220, DEC-093). `gov status` lists them by id only. Nothing renders them, and nothing reads your answer: the template's "Answer" section is filled by hand.

## Users and scenarios

- **The owner**, on a phone, between other things. He opens one page, reads a card, taps an option, adds a line, and at the end copies one block and pastes it into the chat. He never types a code. He can answer six of nine and leave three.
- **The CTO** raises a P1 and has the record filled in by whoever found it (a lead returns the record, not prose). It runs one command to make the page, publishes it, sends one push if something stops, and after the owner pastes the sheet it runs one command that records everything.
- **A lead or a Senior Engineer** returns a decision as a record in the package form; nobody retypes it (DEC-850, DEC-855: only the CTO talks to the owner, and now through the page).
- **An adopted repository's CTO** (EXAMIN's) does the same against its own register.

Stories:
1. Nine questions have gathered by morning. The CTO makes batch `B-20261123-1`; one stops work (a release acceptance waits). The CTO pushes at once (DEC-1217 (5)) with the page; the owner answers all nine on the phone in ten minutes; the CTO pastes the sheet; nine register entries and one commit exist; the CTO carries on.
2. The owner answers four and taps nothing on five. The sheet has `skip` for the five. Four entries are written; the five stay open and appear on the next page, or on the same page if he returns to it and pastes a longer sheet.
3. The owner pastes the same sheet twice (the chat sent it twice). The second run reports "already recorded as DEC-n" for each and changes nothing.
4. The CTO re-asks one question with better options after the page went out (a new package, `replaces:`). The owner then pastes the old page's sheet. The command refuses that line by name and says which newer package asks it.
5. The owner adds a note to an answer that changes it ("b, but only for the first week"). The register entry carries option b and the note in his words, side by side, and the command's output lists every note so the CTO acts on it.
6. A card is about an exposed secret. Its record says `file_only: true`; the batch is rendered as a file and never offered to the Artifact tool.

## Goals

- A decision for the owner is one record with the same fields every time, so it can be read in thirty seconds on a phone.
- The owner answers by tapping and typing a note, and pastes one block; he types no code and no register text.
- A sheet answers exactly the batch it was copied from; a sheet for another or a changed batch is refused by code.
- The register entry is written by code from the sheet, in the register's form, with the owner's note verbatim; the CTO's reading is not in it.
- A re-paste, a partial answer and a changed mind each have a defined result.
- Every decision that is the owner's by the rubric reaches him this way; a drift to chat is seen by a weekly count.
- The adopted repositories get it through `gov update`.

## Non-goals

- No change to who decides: the rubric's P1 list stays yours, the page only carries it (T2-ESCALATION-RUBRIC 2). The page decides nothing for a deadline: no default answer applies when a deadline passes; the CTO re-asks.
- No answer in the chat is refused: the owner can still speak to the CTO in chat, and the CTO records that as today (`Decided-by: owner (chat)`). The page is the route for the CTO's questions, not a gag on his words.
- No server, no web hosting, no account, no network from `gov`: `gov` writes files; the CTO's own tool publishes. Nothing is fetched by the page.
- No use of the Artifact runtime capabilities (state shared between viewers, a question back to Claude, saved files): the page works as a plain file, and the answer travels by paste. Reading answers straight from the page is a Wave 3 row if the paste proves a friction.
- No new `gov` command (the table is being cut from 37 to 34, DEC-1217): the two actions live under `gov decisions`.
- No change to which decisions need the owner, to the register's other entries, to the basis-line check, or to `Role: owner` (never used, DEC-861).
- No scan of the cards for secrets beyond what the CTO's own messages get (EMERGENCY-2 2.11); a card never carries a secret, only a path (`file_only` covers the case).
- Not a place for long documents: a card holds a short question and short options; the detail is a source the card names.

## The template I found (and did not)

- **Not found: your own pages.** No `*.html` in this repository, in `~/gov-os-runs`, in `~/gov-os-worktrees` or in the workbench holds "answer sheet", and no file named like a decision or answer page exists. A scan of the CTO sessions' transcripts under `~/.claude/projects` for this repository finds no Artifact call that published one. `OWNER-DECISIONS-2026-11-18.md` says it was "built with his advisor", so the pages you have used were most likely made in the advisor's own sessions and are not in the repository. **The template of the page is therefore not read; it is built from your description** (a card per decision, pick an option, add a note, copy the answer sheet). I need one thing from you or the CTO: the HTML (or a screenshot) of the last decision page you liked, to commit as the template's golden example before the ticket starts (see Placement).
- **The text twins, in the repository, have the same shape:** `docs/emergency-2/audits/DECISIONS-FOR-THE-OWNER.md` (a code, a question, the options lettered, the recommendation in bold, "answer with the codes, e.g. R1 a, R2 c"), `docs/emergency-2/L2-COMMANDS.md` section 0 ("The owner's page: answer with codes", a Code / Question / Options / Recommendation table), `docs/emergency-2/G5-APPROVAL.md` ("How to answer: one line, for example G5-1 yes ..."), `docs/emergency-2/T2-ESCALATION-RUBRIC.md` section 4 (the owner's answers by code), and the register's records of such answers, `docs/emergency-2/audits/OWNER-DECISIONS-2026-11-18.md`, DEC-1214, DEC-1217. The page makes these tappable and makes the answer a block of text instead of a hand-typed line.
- **The nearest page template on this machine** is the `project-artifact` plugin's `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/project-artifact/skills/project-artifact/template.html` (about 20 KB): one inline file, light and dark colours through `prefers-color-scheme`, a header, status pills, wide content scrolling inside its own box, and one small script. The Artifact tool blocks every external host, so everything is inlined. The decisions page takes that house style and none of its tab structure.

## The record: one decision, as a package

The record is the existing `decision-package` (`DP-<n>`), not a new kind. Reasons: `gov status` and the queue already count open ones (`status: PROPOSED`, DEC-308); `constrains:` already names the tickets that wait; adoption's A2 already writes one (`src/gov/adopt/stages.py`, `_package`); the state lives in `status` alone (DEC-328). A new kind would be a second place to say each of these. The six parts of DEC-818 become fields, so a lead returns the record and code reads it.

Frontmatter (the schema's new fields are **optional**, so no existing package breaks; `gov decisions page` requires them, the way a ticket's READY is computed by code):

| Field | Holds | Limit (so a card fits a phone) |
|---|---|---|
| `id`, `type`, `status`, `state_class`, `title`, `rank`, `constrains` | as today; `status` is PROPOSED while open, ACCEPTED once answered, DECLINED, REVOKED, STALE as today (DEC-328) | title 120 characters |
| `question` | the question, one or two sentences | 300 |
| `found` | what was found, in plain words (the old "Why now" and "Current state") | 900 |
| `options` | a list of 2 to 6 of `{key, label, cost, consequence, changes?}`: `key` is `a`, `b`, `c` in order; `cost` says what choosing it costs, including whether it can be undone and the rework (the old "Reversibility" and "Cost of rework"); `consequence` says what happens next (the old "Impact"); `changes:` optionally names the earlier decisions this option changes, as the register's `Changes:` field does | label 80, cost 240, consequence 240 |
| `recommendation` | `{option, reason, confidence}`: one key of `options`, why, and low, medium or high (a package without one is not sent, as today) | reason 400 |
| `sources` | the files, decision ids and commits the question rests on; each must exist (a path in the tree, a DEC id in the register, a commit) | 12 |
| `blocks` | `nothing`, or what stops until it is answered (the old "Exact permitted next actions"); `constrains:` keeps naming the tickets | 200 |
| `deadline` | optional date; a card past its deadline is marked late, nothing else happens | |
| `meanwhile` | optional: what goes on while it is open | 200 |
| `rubric` | the line of the escalation rubric that makes it the owner's: `P1.1` to `P1.10` (T2 section 2), or `P2.brought` for a P2 the CTO brings | |
| `under` | the decisions the question rests on (`DEC-n`), for the register's `Under:` field | |
| `raised` | `{by, ticket, date}` | |
| `replaces` | optional: the package this one re-asks; the older one is then withdrawn (below) | |
| `file_only` | true: never publish this card (an exposed secret, a security exposure, customer data); default false | |

The body keeps the template's headings for anything longer than a limit allows (a table, a calculation); the page shows the body only as "more", the sheet and the register never read it. The package template and `_package` in A2 are rewritten to carry the fields; the schema stays one file with the new properties added.

**Page-ready** is computed by code, like READY: `gov decisions page` lists, for each open package it cannot take, the field that is missing or over its limit, the recommendation that names no option, the source that does not exist, the `rubric` that is not a rubric line. It never fills a field itself.

## The page

`gov decisions page [--ids DP-a,DP-b] [--max 12] [--out <dir>]` takes the open, page-ready packages (all of them, unless `--ids`), orders them (stops-work first, then late, then the nearest deadline, then P1 before P2), cuts them at `--max` (default 12; the rest go on a second page of the same send), and writes:

- `<batches>/B-<YYYYMMDD>-<n>.json`, the manifest: the batch id, its creation time, each card's id, the card's content hash, and the batch's own hash (below). Tracked in git.
- `<batches>/B-<YYYYMMDD>-<n>.html`, the page, from `template/governance/kernel/templates/decisions-page.html`. Tracked in git, so the sheet can be checked against exactly what was shown.

`<batches>` is `docs/decisions/batches/` unless the project's path map names another place.

What the page is:

- **One file, no outside data.** All styles and the one script are inline; no `src`, `href`, `url(` or `import` to another host, no fetch; the cards are rendered by code into the HTML, so the page reads without script and the script only adds picking, notes and the sheet. Under 300 KB.
- **Mobile first.** A viewport meta; one column; no horizontal scroll of the page body at a width of 360 pixels (a wide source name wraps, a table scrolls in its own box); every tap target at least 44 pixels high; text and inputs at least 16 pixels (so the phone does not zoom); light and dark colours.
- **A card per decision.** Top: the id, the title, a badge (`stops work: <what>` or `stops nothing`, `late`). Then the question, then "what was found". Then the options, each a large tap target with its letter, label, cost and consequence; the recommended one marked, with the reason and the confidence under it. A note box ("add a note", 400 characters, with a count). The sources as plain text, never links (the page cannot open a repository file). "More" opens the body.
- **A header** with the batch id, the first 12 characters of its hash and the count; **a footer bar** that stays on screen: "7 of 9 answered", the button **Copy answer sheet**, and below it the sheet in a read-only box.
- **The copy.** The button uses the clipboard where the viewer lets it. Where it does not (an embedded page often blocks it), the same text sits in a read-only box that selects itself on a tap, with one line: "press and hold, Copy". Both are always present.
- **Choices survive a reload** in the browser's own storage when it has one (keyed by the batch hash, in a guard that ignores a refusal); nothing depends on it.
- A card with no pick is `skip` in the sheet. Picking the same option again unpicks it.

**Publishing (an owner option, DB-2).** `gov` writes the file and prints the path and the push text; it never publishes and never sends. The CTO publishes with its own Artifact tool (a private page at claude.ai, one URL a batch; the viewer keeps the versions) and appends the link to the push. The other route is the file itself, which the owner opens by his own means on the phone. A batch with a `file_only` card is never offered to the Artifact tool, and the push says "file".

## The answer sheet

A fixed text block, copied by the page. A worked example:

```
GOV-ANSWERS 1
batch: B-20261123-1
hash: sha256:9f2c...e41a
answered: 2026-11-23T06:41:00Z
count: 3
DP-0042: b | note: only for the first week, then ask me again
DP-0043: a
DP-0044: skip
END
```

- **Grammar.** The first line is `GOV-ANSWERS 1`. Then `batch:`, `hash:`, `answered:` (the page's clock, UTC) and `count:` in that order. Then exactly `count` lines, one for every card of the batch and in its order: the package id, a colon, the option's letter (`a` to `f`) or `skip`, and optionally ` | note: ` and the note to the end of the line. Then `END`. A note is one line (the page turns line breaks into spaces), 400 characters at most; it may hold `|`, quotes and any script, because it is the last field.
- **The batch hash** is the SHA-256, in hex, of the batch's canonical form: the batch id, then the cards in page order, each as `{id, question, found, options (key, label, cost, consequence), recommendation, sources, blocks, deadline, constrains, meanwhile, file_only}`, written as JSON with sorted keys, no spaces and UTF-8. The same function writes it into the page and the manifest and checks it on a sheet. A card changed after publication, or a different batch, has a different hash.
- **Tolerance.** The parser ignores whatever the chat adds around the block (text before `GOV-ANSWERS 1` and after `END`, a code fence, quote marks, CR and LF endings, trailing spaces) and reads the first complete block. It does not forgive a missing line, an extra line, a count that does not match, or a letter that is not an option of that card.
- **What a sheet is not.** It is not signed: the hash tells the sheet which batch it answers and catches a stale or mangled paste. It does not defend against someone with the owner's own privilege writing a sheet (EMERGENCY-2 3.1: honest mistakes and drift, not an adversary).

## `gov decisions answer <sheet>`

`gov decisions answer <file|-> [--register <path>] [--dry-run]` is run by the CTO (`GOV_ROLE=orchestrator`; any other role is refused, DEC-861) in the main worktree, after the owner pastes the sheet. It never asks anything.

**Checks, in this order; the first failure refuses the whole sheet and nothing is written (the tree is byte for byte as before):**

| Code | Refuses when |
|---|---|
| `ANSWER_ROLE` | the caller is not the orchestrator |
| `ANSWER_FORMAT` | no block, a wrong first line, a field missing or out of order, a count that is not the number of lines, a duplicate id, a note over 400 characters |
| `ANSWER_BATCH` | no manifest for `batch:`; a manifest whose recomputed hash is not the stored one (a hand-edited manifest) |
| `ANSWER_HASH` | `hash:` is not the batch's hash |
| `ANSWER_UNKNOWN_ID` | a line names a package the batch does not hold, or the lines are not the batch's cards in its order |
| `ANSWER_OPTION` | a letter that is not an option of that card |
| `ANSWER_WITHDRAWN` | the card was re-asked: a package with `replaces:` it exists; the message names the newer package and the batch that holds it |
| `ANSWER_STALE` | the package at HEAD is no longer PROPOSED, or its content hash is not the manifest's (changed after publication) |
| `ANSWER_CONFLICT` | the package is already ACCEPTED by this batch with another option (a changed mind is a new package that `Changes:` the entry) |
| `ANSWER_DATE` | `answered:` is before the batch was made or more than a day after now |
| `ANSWER_DIRTY` | the register, the packages or the batch folder have uncommitted changes |
| `REGISTER_UNREADABLE` | the register cannot be read as `### DEC-<n> — title` entries |

**What it writes**, for each line that picks an option (a `skip` writes nothing and leaves the package PROPOSED):

1. **A register entry**, appended at the end of the entries, with the next free id (the highest `DEC-n` in the register plus one, consecutive in the sheet's order), in the form DEC-1225 to DEC-1231 use:

   ```
   ### DEC-1234 — <the package's title>: <the option's label>
   - **Status:** ACCEPTED (owner, 2026-11-23, on the decisions page B-20261123-1, answer DP-0042; recorded by code with `Role: orchestrator`, `Decided-by: owner (page B-20261123-1)`; standing) · **Under:** <the package's `under`> · **Changes:** <the option's `changes`>
   - **Decision:** (b) <the option's label>: <its consequence>. The owner's note, read with the option and carried out as written: "<the note, verbatim>".
   - **Basis:** the owner's answer on the decisions page B-20261123-1 (sheet `docs/decisions/batches/B-20261123-1.sheet-9f2c41ab.txt`, answered 2026-11-23); what was found: <the package's `found`>; the page `docs/decisions/batches/B-20261123-1.html`.
   - **Governing sources:** <the package's `sources`>; DP-0042.
   ```

   `Under:` and `Changes:` are left out when empty; `The owner's note` is left out when there is none. The status line opens `ACCEPTED (owner,` so that `owner_decision` in `src/gov/close/history.py` reads it as the owner's decision. The basis holds the date and a path that exists, so `gov decisions basis` passes it. The recording phrase names the project's CTO as its register does ("recorded by the EXAMIN CTO" there).
2. **The package**: `status: ACCEPTED`, and its "Answer" section filled (option chosen, the DEC id, the batch, the date), as the template already asks.
3. **The sheet itself**, verbatim, as `<batches>/<batch>.sheet-<first 8 hash characters of the sheet>.txt`.
4. **One commit** of exactly these paths, subject `DEC-1234 to DEC-1236 (page B-20261123-1): <titles>`, trailers `Class: C`, `Task: decision-record`, `Role: orchestrator`, `Decided-by: owner (page B-20261123-1)`. Nothing is left staged (DEC-861). If the commit fails, the files are put back.

**Output.** One line per answer (`DP-0042 -> DEC-1234 (b)`), then `skipped: DP-0044`, then `notes for the CTO:` with each note and its card, then `still open in this batch: ...`. Exit 0; a refusal exits 1 with its code.

**Idempotent.** A card already ACCEPTED by this batch with the same option prints `DP-0042 already recorded as DEC-1234` and changes nothing; a sheet with only such lines exits 0 and makes no commit. A later, fuller sheet of the same batch (same hash) answers the cards still open and leaves the rest. `--dry-run` prints what would be written and writes nothing.

**Writes are all or nothing:** the register and the package files are written to temporary names and renamed, and the commit is last; any failure before it restores the files (`git checkout` of the listed paths, the tree having been clean).

## Routing: the rubric sends every owner decision through the page

**What counts as an owner decision here** is exactly the P1 list of the rubric of DEC-1219 (2), `T2-ESCALATION-RUBRIC.md` section 2, items 1 to 9, plus the P2 the CTO brings because nothing else on the list can go on without it (section 3). Each is a package with its `rubric` line. Item 10 (a release, a re-pin, a push, sudo, the machine's settings, going public) is your hand, not a question: it stays a plain line to you, except when the CTO asks whether it may do one (then a card). **Not** on the page: a P2 or P3 the CTO or a lead decides (it goes in the digest, DEC-220); an Emergency (stop the work and push at once; the page follows if a choice remains); a status report; your own chat words.

**When batches go out** (this is DEC-1217 (5) and the rubric's section 3, applied; DB-3 is the one open point):

| Case | What goes out |
|---|---|
| a package that stops work (`blocks` is not `nothing`, or `constrains` is not empty) | a page at once, at any hour, with a push; the page carries every open package, the stoppers first (DB-3 (a)) |
| packages that stop nothing | no push; they go on the morning page, the decision part of the morning brief, which carries one line and the link |
| a stopper's page and the morning page | the same kind of batch; the next batch holds only what is still open |

**The push** is the text `gov decisions page` prints, at most 150 characters, with the link or "file" appended by the CTO: `Decisions waiting: 5 (2 stop work). Page B-20261123-1: tap, answer, copy the sheet, paste it to the CTO.` It is sent through the CTO's own push tool, as the stall push is. A batch with no stopper prints no push text.

**How the routing is carried.**
- The kernel text says it: the rubric lines in the orchestration skill (`briefs-and-returns.md`, `incident-response.md`), the orchestrator, Senior Engineer and ticket-lead role files and the domain skills' "When to escalate" sections gain one sentence, "a decision that is the owner's is a package with its fields, raised to the CTO in the return; it reaches the owner on the decisions page, never as a message" [DEC-1217 (5)]. The package template and the "Answer" section follow. This is kernel and instruction text: the CTO's call (EMERGENCY-2 3.5); nothing reaches the owner but this proposal's yes.
- A lead's return carries the package file; `gov status` already lists the open ones and gains the age and whether each is on a batch.
- **Drift is caught, not prevented** (EMERGENCY-2 2.1): `gov decisions basis --week` lists each owner entry of the week with its channel, `page <batch>` or `chat`, and prints `open packages not on a page: N (oldest: <hours>)`. A week that shows an owner question answered in chat which was a P1 package is a finding for the CTO to fix, not a refusal.

**What this changes in what is decided:** the cap of five open packages in the template's "Batching" line and the orchestration skill (DEC-220, DEC-093) is replaced by the batch (12 a page); DEC-818's six parts are carried as fields; `Decided-by:` gets a second channel value, `page <batch>`, beside `chat`, and nothing reads the channel as approval (DEC-862 (c): the entry's own owner status line does).

## Where it lives in the kit

| Piece | Place | Adopted repositories get it by |
|---|---|---|
| the two actions | `src/gov/decisions/` (`package.py` fields, hash and page-ready; `page.py`; `answer.py`; `command.py` gains `page` and `answer` and the `--week` lines); `HELP` and usage updated | the release's `gov` (`gov update` pins it) |
| the page template | `template/governance/kernel/templates/decisions-page.html` | `gov update`, the kit's overlay rule (three-way merge keeps the project's edits) |
| the record's schema and template | `template/governance/kernel/schemas/decision-package.schema.json` (new optional properties), `templates/decision-package.md` (the structured form) | `gov update` |
| the rubric and routing text | the kernel skills, role files and templates named above, with their generated copies | `gov update` (the CTO's change) |
| adoption's question | `src/gov/adopt/stages.py` `_package` writes the new fields | the release |
| configuration | `governance/project/config` key `decisions: {batches: docs/decisions/batches, register: docs/DECISION_REGISTER.md, page_max: 12}`; the defaults hold when absent | `gov adopt` writes it; `gov update` leaves the project's value |

EXAMIN gets all of it by `gov update` to the release that carries it, without re-adopting (EMERGENCY-2 7.6). Its register (`docs/DECISION_REGISTER.md`, read in the clone at `~/gov-os-runs/fresh/20261120/repo`) has the same `### DEC-<n> — title` and `- **Status:** ACCEPTED (owner, <date>, ...; recorded by the EXAMIN CTO)` shape, so `answer` writes it unchanged except for the recording phrase, which is a configuration value.

## Placement and size

**Size: M.** About 1,100 lines with tests: the record's fields, limits and page-ready check (about 150), the canonical hash and the manifest (about 80), the page renderer and the template, HTML and script (about 400, the template being the bulk), the sheet parser and `answer` with its refusals and the all-or-nothing write (about 350), the `--week` and `gov status` lines (about 40), and the kernel text, which is the CTO's and not counted. It touches kernel and a command, so it is a FULL ticket.

**Release.** It is a new feature, so it cannot ride in a patch release (the patch rule's P3 and P5 in RELEASE-ON-BEHALF: a feature ticket closes, a kit file changes). It follows 0.1.5 (DEC-1226, the owner's last manual cut) and rides the release after it, the first bigger one, with D1 the lite verdict stage (DEC-1231): it is the owner's hand again, as a bigger release is.

**Ticketing.** One new feature ticket, two slices by one lead (DEC-1214 K2: adding a ticket to a planned wave asks you, and this proposal's yes is that ask). It extends the closed `gov decisions` command and the package template and replaces neither (EMERGENCY-2 4.6: a new KPI line on a closed feature is a new ticket).
- **Slice (a): the record and the answer.** Fields and limits, page-ready, the canonical hash, the manifest, the sheet parser and `gov decisions answer`; KPIs PG-1, PG-3 to PG-6. It is useful alone: the CTO can already give you the sheet as plain text.
- **Slice (b): the page.** The renderer and the template, the push text, the `--week` and `status` lines; KPIs PG-2, PG-7, PG-8, and PG-9 with slice (a).
- **First step, before either:** the owner or the CTO supplies the HTML of a decision page he liked (see "The template I found"), committed as the template's golden example; if there is none, the template is built to this document's description and your first real page is the acceptance.
- **The kernel text** (rubric lines, role files, skills, the package template's prose) is the CTO's change, made after your yes and landing with slice (b).

## KPIs

- PG-1: A package carries question, what was found, 2 to 6 options each with a cost and a consequence, a recommendation that names one of them with a reason and a confidence, sources that exist, and `blocks`; `gov decisions page` takes a package only when all of that holds and within the limits, and says for each other open package the field that is missing, too long or false.
  Fails if: a package with a missing field, an over-limit text, a recommendation naming no option or a source that does not exist is put on a page, or a refusal names no field.
- PG-2: The page for a batch is one file with no reference to another host, readable without script, with a card per package showing its question, what was found, every option with cost and consequence, the recommended option marked, what it blocks, its deadline and its sources, a note box, and the always-visible bar with the count, the Copy button and the sheet in a read-only box; at a width of 360 pixels the body does not scroll sideways and every tap target is at least 44 pixels high.
  Fails if: the page names an outside host or loads data, a card lacks one of those parts, the sheet exists only behind the Copy button, the body scrolls sideways at 360 pixels, or a tap target is under 44 pixels.
- PG-3: The sheet is the fixed block of the grammar above: the page and the Python writer produce byte-identical sheets for the same picks and notes (including `|`, quotes, accents, emoji and line breaks in a note), and the parser reads a sheet that the chat wrapped (a fence, quote marks, CRLF, text around it).
  Fails if: the two writers differ for any pick or note, a note is lost or altered beyond its line breaks, or a wrapped but intact sheet is refused.
- PG-4: `gov decisions answer` on a valid sheet writes one register entry per picked option, in the form of DEC-1225 to DEC-1231 (title, an `ACCEPTED (owner, <date>, on the decisions page <batch>, answer <id>` status line, the option and the owner's note verbatim, a basis naming the batch and the finding, the sources), with consecutive free ids in the sheet's order; sets each package to ACCEPTED with its answer filled; stores the sheet; and makes one commit with `Task: decision-record`, `Role: orchestrator` and `Decided-by: owner (page <batch id>)`.
  Fails if: an entry differs from that form, an id is reused or skipped, a note is changed, a package stays PROPOSED after its entry, the commit lacks a trailer, more than one commit is made, or `gov decisions basis` or `gov links` finds something new in the written entries.
- PG-5: A sheet with the wrong hash, an unknown or missing or duplicate id, an option the card does not have, a changed or already answered or withdrawn package, a bad date, a bad count or a note over 400 characters, or run by a role other than the orchestrator, or over uncommitted decision files, is refused with its code and changes nothing.
  Fails if: any file, the register or the history differs after a refusal, a refusal carries no code, or a sheet of another batch is accepted.
- PG-6: The same sheet pasted twice changes nothing the second time and exits 0, naming the entries it already made; a `skip` leaves its package open, and a fuller sheet of the same batch answers only what is open; a different option for an answered package is refused.
  Fails if: a second paste writes an entry or a commit, a `skip` writes anything, or a later answer duplicates an earlier one.
- PG-7: When a batch holds a package that stops work, `gov decisions page` prints one push text of at most 150 characters naming the count, the number that stop work and the batch id, and the batch carries all open packages, the stoppers first; with none that stops work it prints no push text; a batch holding a `file_only` card is marked file-only in its manifest and in the push text.
  Fails if: a push text is printed for a batch with no stopper, none for a batch with one, it is longer than 150 characters, a stopper is not first, or a file-only card is not marked.
- PG-8: Drift to chat is seen: `gov decisions basis --week` prints for each owner entry its channel (`page <batch>` or `chat`) and a line `open packages not on a page: N (oldest: <hours>)`, and `gov status` shows each open package's age and its batch.
  Fails if: an owner entry of the week shows no channel, a P1 package open for over 24 hours and on no batch is not counted, or a page-written entry is shown as chat.
- PG-9: In a scratch adopted repository at the previous release, `gov update` to the release that carries this brings the command, the template, the schema and the package template; one package goes through page, sheet and `answer`, writing that repository's own register with its own recording phrase, and the repository's own edits to the kit files are kept.
  Fails if: an adopted repository lacks any of the pieces after the update, `answer` writes Gov OS's phrase or path into it, or the update overwrites a project's edit.

## How each KPI is verified

All run in temporary repositories with a temporary `$HOME`; none touches the real register or publishes anything. The first real page, answered by the owner on his phone, is the one check no test can make (see Accepted by).

| Code | In short | Verify |
|---|---|---|
| PG-1 | page-ready | build packages with each defect planted (a field missing, an over-limit text, a recommendation on option `z`, a source path that is not there, a bad `rubric`) and one clean: `page` takes the clean one and names exactly each planted field for the others; the schema accepts a package with none of the new fields |
| PG-2 | the page | render a batch; parse the HTML: no `http`, `//host`, `url(`, `import`, `fetch` or `XMLHttpRequest` outside the card text; the viewport meta; the card parts present with the script removed; the CSS carries a `min-height` of at least 44 pixels on the option and button classes, no fixed width over 360 pixels and `overflow-x:auto` on tables; the sheet box is in the page; size under 300 KB. A headless-browser run, where one is on the machine, adds a width-360 overflow check; the test names it NOT RUN, never passed, when none is |
| PG-3 | sheet parity | run the page's script under `node` with a small stand-in for the document, for a fixed set of picks and notes; compare its text byte for byte with the Python writer's; feed the parser the sheet inside a fence, with quote marks, with CRLF and with text around it. A missing `node` fails the test as an environment fault; it is never skipped |
| PG-4 | the register by code | on a scratch register with the real entry form, answer a sheet of three picks and one `skip`; compare each new entry with the expected text; read the status line with `owner_decision`; run `gov decisions basis --range HEAD^..HEAD` and `gov links --since HEAD~1`; read the commit's trailers; read the three package files and the stored sheet |
| PG-5 | refusals | one sheet per refusal code (each from a good sheet with one change); compare a snapshot of the tree and `git rev-parse HEAD` before and after, and the code printed |
| PG-6 | idempotent, partial, changed mind | paste twice (second: no diff, exit 0); answer with a `skip`, then a fuller sheet of the same batch; then the same card with another letter |
| PG-7 | push | planted batches: one stopper, none, five stoppers, one `file_only`: the printed text, its length, the order of the cards and the manifest's mark |
| PG-8 | drift | a scratch register with one `page` and one `chat` owner entry and two open packages (one over 24 hours): the `--week` lines and `gov status` |
| PG-9 | adopted | a scratch repository adopted at the previous release's kit, with one kit file edited by the project: `gov update` to the candidate, then the round trip, then a byte comparison of the edited file |

## Test data

| source | kind | owner | recipe | privacy | secrets | hidden half | secured |
|---|---|---|---|---|---|---|---|
| packages: clean, and one per planted defect of PG-1; a batch of three, of nine and of thirteen (the cut at 12) | synthetic | independent test designer | written at test time from the schema's own fields, a fixed seed, one commit at a time | none | none | n/a | yes |
| sheets: good, wrapped, wrong hash, unknown id, missing line, duplicate, wrong letter, long note, notes with `|`, quotes, accents, emoji and line breaks, bad date, re-pasted, skip-then-fuller | synthetic | independent test designer | built from a batch's manifest by the Python writer, then edited one thing per case | none | none | n/a | yes |
| a scratch register with the entry form of DEC-1225 to DEC-1231 and of EXAMIN's `DEC-001` to `DEC-003` | synthetic | independent test designer | a copy of the shapes, with invented decisions | none | none | n/a | yes |
| a scratch adopted repository at the previous release's kit with one edited kit file | synthetic | independent test designer | the W2-81 builders' first repository, as RELEASE-ON-BEHALF uses it | none | none | n/a | yes |
| a golden decision page (the owner's), if supplied | the owner's | owner | his HTML, committed once as the template's example | none | none | n/a | yes |

## Out of scope

- Reading the owner's answer straight from the page, a shared state, a question back to Claude: Wave 3, if the paste proves a friction.
- Publishing: the CTO's Artifact tool and the owner's phone are outside `gov`; nothing in this feature calls the network.
- The kernel and instruction text (rubric lines, role files, skills, the package template's prose), CLAUDE.md and AGENTS.md: the CTO's change after the yes (EMERGENCY-2 3.5).
- The Contract's covers item for this feature and any wording in EMERGENCY-2 or the T2 rubric: as the owner decides, after his yes.
- The owner's chat answers, the digest of delegated decisions and the morning brief's other parts: unchanged.
- Machine incidents and the Emergency class of the rubric: unchanged; they push and are not batched.

## Open questions

Answer by code, for example "DB-1 yes, DB-2 c, DB-3 a, DB-4 a, DB-5 a". Until then this page is also the first use of the idea: the same questions, in the form the feature would send.

- Question DB-1: Build decisions by page as one feature ticket in two slices, after 0.1.5, riding the release after it?
  - Options: (a) yes (cost: one FULL ticket of about 1,100 lines, and the kernel text for the CTO to change); (b) slice (a) only, the record, the sheet and `answer`, with the sheet given as plain text for now (cost: no page on the phone, the main gain deferred); (c) no (cost: today's long messages and hand-recorded answers stay)
  - Recommendation: (a). The incident is repeated and recorded (DEC-1214, DEC-1217, the DEC-1224 correction); slice (a) is useful alone, so a stop after it loses nothing. Confidence: high.
- Question DB-2: How does the page reach your phone?
  - Options: (a) the CTO's Artifact tool only (cost: it needs that tool and your claude.ai login on the phone; the page leaves the machine for claude.ai, as your chat does; no route for a `file_only` card); (b) a file you open yourself (cost: you move a file to the phone, no tap-through from the push); (c) the Artifact tool, with the file always written beside it as the fallback and the only route for a `file_only` batch
  - Recommendation: (c). One tap from the push in the ordinary case, and the file when the tool is missing or the card is too sensitive to publish. Confidence: medium; I could not test your phone's browser with an Artifact page (the clipboard may be blocked there, which is why the read-only box is always present).
- Question DB-3: How often do batches go out, and what does a stopper's page carry?
  - Options: (a) one morning page for what stops nothing, and an immediate page with a push for a stopper, carrying every open package with the stoppers first (cost: an immediate page may hold decisions that could have waited, and you may answer them at once); (b) as (a), but a stopper's page carries only the stoppers and the morning page the rest (cost: two pages a day sometimes, and you see the others later); (c) a fixed second page each evening as well (cost: more pages to open on a quiet day)
  - Recommendation: (a), the least interruption: each time you are pulled in, you can clear everything. It keeps your rule unchanged (DEC-1217 (5)). Confidence: medium.
- Question DB-4: May an answer be free text, apart from the note?
  - Options: (a) no: an option or `skip`, and a note on any card, recorded in your words beside the option (cost: if no option fits, you pick `skip` and say why in the note, and the CTO re-asks with new options in the next batch); (b) yes: an extra "other" answer that is only your words (cost: the register gets an answer that code cannot map to an option, and the CTO must read it before acting)
  - Recommendation: (a). A note on a chosen option already carries "b, but only for a week" (the way you changed IM-3 and IM-4, DEC-1222), and each recorded answer then stays one of the options the CTO costed. Confidence: medium.
- Question DB-5: How does the register record a page's answers?
  - Options: (a) one entry per answered decision, each with its own id (cost: a long batch makes many entries; the register is longer); (b) one entry per batch, with an item per answer, as DEC-1214 and DEC-1227 are (cost: one answer cannot be superseded or looked up alone; `Changes:` must name an item, as DEC-1231 does for DEC-1227 D1)
  - Recommendation: (a). The register's grain is one decision an entry (DEC-1225 to DEC-1231), a later change names one id, and memory finds each by its own title. Confidence: medium.

## Accepted by

The owner, by his answers to DB-1 to DB-5, recorded by the orchestrator (DEC-861). Then, for each KPI, the independent test designer's acceptance tests written from PG-1 to PG-9, red on the base; the engineer's `gov accept` green; and the first real page: a batch of the CTO's genuine open questions, published by the route chosen in DB-2, answered by the owner on his phone, pasted, and recorded by `gov decisions answer`; the CTO reads the commit and the entries against what the owner tapped before the kernel text is switched to say "never as a message".

## For the owner

You asked that every decision that needs you reach you as a card on a page, and that your answers be written into the register by code. This is the design. Questions are the packages we already have, with the fields filled the same way each time: the question, what was found, the options with their costs, the recommendation, the sources, and what stops until you answer. The CTO gathers the open ones into one batch and code makes one phone-sized page from it: a card each, tap an option, add a note, copy the sheet. The sheet carries the batch's number and a fingerprint, so it can only answer the page you saw; you paste it to the CTO, who runs one command, and each answer becomes a register entry in the same form as DEC-1225 to DEC-1231, with your note in your own words and `Decided-by: owner (page <batch>)`. Pasting twice changes nothing; leaving a card alone leaves it open; the old page cannot answer a question that was re-asked. A decision that stops work still pushes you at once, with the page; everything else waits for the morning. I could not find a page you used in the repository, so I built this from your description: if you send the last one you liked, the page takes its look. The five questions are above; I recommend yes, the Artifact tool with the file as fallback, a stopper's page that carries everything open, notes but no free-text answer, and one register entry per decision. Nothing is built, no ticket is opened, and the file is not committed.
