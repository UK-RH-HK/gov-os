You are the ticket lead for ticket `DAEO-u4oz` (`W2-04`, "gov context bounded and reproducible"), profile FULL, keystone 4, working only in the worktree `/home/usain/gov-os-worktrees/W2-04` on branch `w2/W2-04`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-u4oz.md`) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-04"); W2-03's card ("#### W2-03"), whose per-entry hashes you use;
- DEC-860, DEC-836, DEC-829 (item 2, keystone 4: "bounded context packets carrying real text"), DEC-833 (item 3), DEC-941 (item 1), DEC-942 (item 1), DEC-943 (item 2), DEC-946 (item 3) and DEC-951 (item 5); CAP-15 (items d and f) in `docs/contract/`;
- lens B's report `docs/assessment/2026-10/B-memory-retrieval.md`, finding F1 (packets 42 to 168 times their ceiling, with no text of their inputs, reported as a success; DAEO-03pw at 814,821 tokens in the Wave 1 exit audit's F-M5);
- `src/gov/context/__init__.py` whole (358 lines), `src/gov/context/context_check.py` (the `context-reproducibility` check, run at every close) and `src/gov/context/command.py`;
- read-only, through their public interfaces:
  - `src/gov/store/loader.py`: `register_entries`, each entry's span and `content_hash` (W2-03);
  - `src/gov/retrieval/retrieve.py`: `retrieve` with `batch_size`, `bundle_budget` and `continuation`;
  - `src/gov/retrieval/synthesis.py`: `validate_notes` (row W2-M134).

## Why you start now

- **`gov context` is unbounded and empty.** Each mandatory decision is read as the whole register file (`_read_record` reads the record's path, which for every decision is the register). So a packet that cites one decision counts about 250,000 tokens, reports `ok: true`, and still carries no text of its inputs (lens B F1).
- **Briefs wait on it.** The orchestrator builds every brief with `gov context` only once you have merged (DEC-836). Its drift measure starts with your close and W2-55's (DEC-943 item 2).
- **Memory is the critical path to EXAMIN's copy** (DEC-941 item 1, DEC-946 item 3). W2-61's baseline of the visible half, on 2026-10-29: hit@5 8 of 20 (40 %, against CAP-10's floor of 85), full evidence 12 of 20 (60 %, against the owner's target of 99 %), in the bundle 14 of 20.
- **Stacked on W2-03 (DEC-786).** W2-03 is merged into `w2/integrate` (`a8eaf26e`), so it is in your base, and it closes in the first close batch.
  - **Read-only to you:** its paths, `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**` and `src/gov/check/citations.py`.
  - **Your merge waits** until W2-03 has closed.
  - **Check W2-03's state** before the engineer starts and before you return: `grep -m1 '^status:' /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-ym8a.md`. If it says `closed` or `in_progress`, go on.
  - **If W2-03's close is refused,** the orchestrator writes `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/REFUSED-DAEO-ym8a`. Check for it at the same two points. If it is there, start nothing more, write your checkpoint, and return PACKAGES naming it.
- **Launched beside W2-55** (DEC-942 item 1). The two tickets share `src/gov/context/**`, and that overlap is split by file: every file there is yours (below).

## The decisions for this run

- **First, a measure, before the design is fixed.** After the first rebuild, count with a small script of yours in scratch that reads this worktree's store:
  - how many open and in-progress tickets have mandatory inputs (the ticket's own text, plus each source as its own entry or record) above 6,000 tokens;
  - DAEO-03pw's figure.

  Put the figures in the design note. **If more than a tenth of the open and in-progress tickets would be refused, or any ticket of the memory chain would be** (W2-55, W2-64, W2-05, W2-06, W2-13, W2-15a), return PACKAGES with the figures before the engineer starts. The ceiling is CAP-15's, and changing it, or what counts as mandatory, is the owner's call. The package blocks the engineer only.
- **Design first, short.** The ticket's paths hold no note, so you write it in your scratch: `.gov-runtime/scratch/lead/design.md`, at most a page, in behaviour. It is a plan, not code. It says:
  - **the packet's parts, in order, each carrying the text it counts** (DEC-829 item 2; lens B F1):
    - the ticket's own text, always, first, never dropped;
    - the mandatory inputs, by precedence. Each decision is its own entry's text (its span in the store), named by its own hash (W2-03's `content_hash`), never the register file;
    - the supplementary block, in the room left;
  - **the ceiling:** 6,000 tokens by default, counted as now (characters / 4), with `--budget` as it is. The packet never holds more;
  - **over the ceiling:** when the ticket's text and the mandatory inputs alone exceed the ceiling, `gov context` gives a named error and a non-zero exit, and never `ok: true`. The error gives the size and the ceiling. Nothing mandatory is cut to fit;
  - **`context-reproducibility` under the ceiling:**
    - a ticket refused for its size is refused the same way twice. Say whether the check counts that as reproducible or as an error, and why;
    - the check stays green on this repository, because it runs at every close and a red there blocks every close;
    - its time, before and after;
    - row W2-M294 (green on a stale store, red after a rebuild);
  - **one hash per commit:** two builds of one ticket's context, on stores rebuilt from one commit, give one hash, both with a live semantic index and without one.
    - The note states its reading of "with or without". The KPI's words mean one hash in both states. A weaker reading is a package, not a choice.
    - Ties in the supplementary block are broken by a stated total order (path, then first line, then id), the same across processes (W2-M330);
  - **the supplementary block** (DEC-860, W2-M126):
    - the query is built from the ticket's title and KPI lines, not from the first long word;
    - the evidence comes from `retrieve` in batches (`batch_size`, `continuation`), ranked and stacked while there is room;
    - the packet names what it left for a further batch: the continuation and how many items;
    - each item keeps its path and line span, so that W2-55's later filter can act on it;
    - a failed lookup is named by its kind (W2-L180), never "index unavailable" for every failure;
  - **mandatory records that do not stand or cannot be read:**
    - SUPERSEDED, RETIRED and REJECTED never satisfy a source (W2-M215). The code already has `NO_LONGER_STANDS`: re-check it;
    - an unreadable mandatory record blocks the context or is marked not read. It is never shown as read with an empty hash (W2-H034, W2-L088);
  - **what does not change:**
    - the external-references rule (W1-41, DEC-520);
    - the conflict and supersession rules at one level;
    - `--brief` and `--dry-run`.

  The note goes into the test designer's and the reviewer's briefs as text.
- **The rows (DEC-718):** re-check each against the code.
  - **W2-M133's place is `src/gov/check/runner.py`,** outside your paths: it is a residual, or a package if it bears on a KPI.
  - **W2-M134:** say whether `gov context` calling `validate_notes` is in your reach and in the ticket's scope.
  - **A row found already fixed** is reported with the commit that fixed it.
- **Tests first,** by a fresh independent test designer (launched sandboxed, `--effort xhigh`, a measured trial for FULL test designers, DEC-839; its brief must not set `TMPDIR`), in `tests/acceptance/W2-04/`:
  - one case per KPI line and per failure line, in temporary repositories built from scratch, each with a small register and a store rebuilt by this worktree's code;
  - **the ceiling held:** a ticket with many supplementary candidates stays within the ceiling, with its own text whole;
  - **over the ceiling:** mandatory inputs alone above the ceiling give the named error, a non-zero exit of `gov context` and no `ok: true`;
  - **each decision is its own entry:** its hash is its own entry's, and its text is its entry's span, never the register;
  - **reproducible:**
    - two stores rebuilt from one commit give one hash, with a live semantic index and without one. Use a planted index stand-in where an embedder cannot run, and say which in the README;
    - ties give one order across two processes;
  - **the rest of the KPIs:**
    - an unreadable mandatory record, and a RETIRED or REJECTED source;
    - the query built from the title and the KPIs;
    - the batches stacked, and what was left named;
  - **live cases on this worktree's store:**
    - DAEO-03pw refuses with the named error, or fits;
    - `context-reproducibility` is green on this repository;
  - **the rows:** a case for each row still open after the re-check;
  - **earlier acceptance tests that pin the old packet** (W1-24's and W1-41's among them; the designer checks): named in the README, never edited. A revision is a package (DEC-866 where a superseded decision is the cause);
  - **in proportion (owner, DEC-951 item 5):** the owner found 2,980 lines of tests for 713 lines of code out of proportion. Aim at about 450 lines, fixtures included. The README gives the count, and says why for anything past it.
- **The engineer** (fresh, launched sandboxed where its suites allow, `--effort high`) works only in the allowed paths:
  - `src/gov/context/**`;
  - `src/gov/retrieval/supplementary*` (a new file);
  - `tests/unit/context/**`.

  It reads the store and the retrieval through their interfaces. If the tie order inside `retrieve`, a missing field of a store entry, or anything else outside the paths must change, return PACKAGES.
- **Fail closed:**
  - never `ok: true` over the budget;
  - never the ticket's text dropped, or a mandatory input cut to fit;
  - never an input shown as read that was not read;
  - never a lookup failure hidden in the supplementary block;
  - never an order that depends on the process, the dictionary or the clock.
- **Running beside you** (paths checked against yours, file by file):
  - **W2-55** (`DAEO-arrl`, launched beside you) holds `src/gov/decisions/**`, `src/gov/retrieve/**` (its filter), `template/governance/kernel/schemas/register-entry.schema.json`, `tests/unit/decisions/**` and `docs/research/W2-55-backfill.md`.
    - `src/gov/context/**` is yours alone in this run. W2-55 writes there only after your merge (its round 2).
    - Do not filter supplementary items by a decision's status beyond what the code does now: that is W2-55's.
  - **W2-64** (`DAEO-0uhh`) holds `src/gov/check/schema.py`, `template/governance/kernel/schemas/close.schema.json` and `tests/unit/check/test_schema*`.
  - **W2-61** (`DAEO-iw1f`) holds `src/gov/retrieval/measure.py` and `tests/unit/retrieval/test_measure*`. Your builder tests go in `tests/unit/context/`, never `tests/unit/retrieval/`.
  - **W2-05** (`DAEO-0z8c`, resuming) holds `src/gov/**/*.py` for the git environment of git calls. Your files start no git process; if you add one, build its environment as `gov.store.loader` does and name it.
  - **W2-84** holds `src/gov/guard/reads.py`. **W2-51** holds `docs/plan/tools/validate_w2.py`. **W2-67** holds `tests/unit/close/**`, `tests/unit/guard/**` and `tests/conftest.py`. **W2-60a** holds `src/gov/launch/**`.
  - **W2-39 and W2-13** (not started) take `src/gov/context/**` and `src/gov/retrieve/**` after you.

  Do not touch their files. If your design needs a change there, return PACKAGES.
- **Verification:** in the close's form, under the lock, with the retention option and the disk gate first. The nightly, the close's quiet window, the 01:00 cut-off and the rebuild lock apply as the common brief states them.
  - `context-reproducibility` is **GREEN** in `gov check --json` on this worktree's code, with its time before and after your change.
  - **Known:** W2-54's green-here cases may time out under load in a plain full run (row W2-L429): re-run them alone. W1-46's and W1-19's cases run in your serial phase.
  - Any other red is named with its cause.
- **W2-61's measure is the orchestrator's,** after W2-61 and this ticket merge. It measures `gov retrieve`, which this ticket does not change. Your return shows it with `git diff --name-only w2/integrate...HEAD -- src/gov/retrieval src/gov/retrieve`, which should name only your new `supplementary` file, one that `gov retrieve` does not import. If your branch changes anything `gov retrieve` runs, say so: the orchestrator then measures before the merge.
- **Reviews:** one, for the ticket. A fresh FULL reviewer (brief A3 with `JUDGEMENT.md` word for word, `--effort max`) reviews the final head and is given the design note.
  - **The probe looks above all for:**
    - a packet above its ceiling, or `ok: true` over the budget;
    - the ticket's own text dropped, or a mandatory input cut;
    - a decision read as the whole register, or named by a hash not its own;
    - two hashes from one commit (the semantic index on or off, the process order, dictionary order, the time, a stale store);
    - a record that was not read shown as read;
    - a superseded, retired or rejected record that satisfies a source;
    - a lookup failure hidden;
    - `context-reproducibility` red on this repository, or hiding an error as reproducible.
  - **A finding that shows one of the ticket's failure lines fails the review.**
  - Commit the probe record only when it passes. If it fails on such a finding: one test-design batch, one engineer, a full run, and a second, last review (DEC-413).

## This run's order

1. A full rebuild of this worktree, then the size measure, then the design note (yours, in scratch). Return PACKAGES here if the measure calls for it.
2. Tests first (the test designer), then **check red yourself.**
3. The W2-03 check, then the engineer.
4. Rebuild and verify in full.
5. The review.
6. **Return** DONE or PACKAGES. DONE means the probe passed and the branch is ready to merge once W2-03 has closed (say "held, stacked on W2-03" in the status line if it has not).

**Estimate:** about 220 lines; about 8 hours with the full run and one review.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
