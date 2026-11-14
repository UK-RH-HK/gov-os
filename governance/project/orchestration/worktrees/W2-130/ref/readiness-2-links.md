# Readiness review before the fresh 80, aspect 2: the stated links and status marks (W2-92 S7-S10, W2-129 `gov links`)

Reviewer 2 of 7 (DEC-1097 (3); FRESH-80-READINESS §5). I worked read-only. I opened nothing under `~/gov-os-eval/` and
no hidden or spent question file. I made no commit, rebuild, GPU run or install. I followed JUDGEMENT.md and
AUDITOR-common.md.

**Verdict: READY for the 80.** There are no FIX-BEFORE-THE-80 findings and six rows.

## What I checked and how

- **Code read:** `src/gov/retrieval/retrieve.py` (`_graph`, `force`, `entry_mark`, `item`, the hop), `graph_route.py`
  (`changers`, `follow`), `store/loader.py` (`register_entries`, `register_statements`, `_stated_links`, `_load`),
  `retrieve/command.py` with `decisions/register.py` (`leave_out`), and `links/command.py` and `links/check.py`.
- **Tickets and records read:** W2-92 (`DAEO-n0wb`) and W2-129 (`DAEO-q7lk`), their reviews `w2-92-w4.md` and
  `w2-129.md`, and `docs/research/W2-129-links.md`.
- **The pin and the code:** the pin `pin-bcea09060ebc` differs from `src/` only by W2-138 (store fields). The status
  and link code is the same.
- **The measured store:** E0's clone (`~/gov-os-runs/D4B/w4-e0/repo`, HEAD `c00d525fd420`) has a store built at
  `c00d525f` (kind rebuild). Its `stated_links` table is filled: AMENDS 396, CITES 1,739, OF_TASK 381, SUPERSEDES 7,
  UNDER 2,534. So the configuration DEC-1097 (1)(a)(b) judges carries S7 to S9.
- **Searches:** 9 `gov retrieve` searches with the pinned binary (`--root ~/gov-os-worktrees/W2-00-store`), one at a
  time. The guard refused nothing (0 refusals).
- **`gov links` without the mark:** I ran `--propose-marks`, which writes nothing. I also ran `check.findings` in
  memory through the pin's Python, so `.gov-runtime/links/mark` was not written.

### What the searches answered (the marks work as specified)

| # | Question (plain words unless an id is named) | What the bundle said | Judged |
|---|---|---|---|
| 1 | DEC-140 (withdrawn whole by DEC-842 through a `Changed by:` label; its status word is still ACCEPTED) | `in_force: false, not_in_force: SUPERSEDED, changed_by: [DEC-842]`. The hop added DEC-842, ranked 2nd. | right |
| 2 | The window and auto-compact threshold for a worker (DEC-208, 248 and 451, each changed in part by DEC-838) | DEC-838 ranked 1st, in force. DEC-208, 248 and 451 are in force with `changed_by` naming DEC-838. | right |
| 3 | W2-48's cache conditions (DEC-876 SUPERSEDED by DEC-880) | DEC-876 is not served as current: W2-55's `leave_out` removes SUPERSEDED-status entries. DEC-880 is in the bundle, and DEC-843 is marked changed by DEC-880. | right; F2 seen here |
| 4 | Installs (DEC-040 PROPOSED) | DEC-040 `in_force: false, not_in_force: PROPOSED`, changed by DEC-083. DEC-083 is in the bundle. | right |
| 5 | Architecture and stack (ADR-0002, a file record that is PROPOSED) | Every ADR-0002 item `in_force: false, PROPOSED`. | right |
| 6 | The D4B gaps (DEC-1066, changed by free text in DEC-1067, with no mark on DEC-1066's own entry) | DEC-1066 `changed_by: [DEC-1067]`, taken from the changer's side. DEC-1067 itself is not in the bundle (F4). | right |
| 7 | DEC-899 (7 changers) | The hop added all 7 changers first, newest first, within its bound of 12. The facet says `left: 22`. | right |
| 8 | K9's bar on the fresh 80 | DEC-1083 in force, `changed_by: [DEC-1087, DEC-1084]`, with DEC-1097 ranked 2nd. DEC-1097 is not named as a changer (F3). | data gap |
| 9 | MR-3 | The MR-3 items `in_force: false, not_in_force: PROPOSED`, ranked 1st (F1). | data defect |

### Other checks

- **Every register chunk that touches an entry carries its status.** The register has 1,093 live entries and refuses
  none. Chunks with no mark lie in the preface or change log, which is W2-92 review F1, a known row.
- **The text form prints the whole result as JSON** (`cli/main.py`), so the marks reach an agent with or without
  `--json`.
- **Whole supersessions whose own status word is still ACCEPTED** number two: DEC-140 (a stated link) and DEC-960 (an
  edge from DEC-961). The bundle marks both not in force, and W2-55's `leave_out` removes DEC-960. No whole
  supersession reads as current.
- **The 186 UNMARKED_CHANGE decisions** still show their changers in a bundle: `changers()` reads the changer's own
  label or text (search 6).
- **`gov links` is never a gate.** Nothing in `src/gov`, `.claude/hooks` or the kernel hooks calls it.
- **The standing count matches the notice.** Recounted read-only at the store's head: **3,130 findings** in 2.75 s.
  By code: UNLINKED_ID 1,877; UNKNOWN_ID 556; UNMARKED_CHANGE 186; NOT_IN_FORCE_AS_RULE 141; CLOSED_TICKET_EDITED 117;
  STATUS_CONFLICT 116; TICKET_CHANGE_UNMARKED 93; ENFORCES_SUPERSEDED 44.
- **The 80 cannot take a fix in this aspect.** DEC-1097 (1)(a)(b) and FRESH-80-1 item 12 fix the commit
  (`c00d525f`), the pin and E0's store, with no rebuild. A data or code fix made now cannot enter the judged
  configuration without re-opening DEC-1097. So the question for each finding is whether it makes the verdict
  *wrong*, not whether it lowers the score. A defect the configuration really has, measured as it is, keeps the
  verdict honest.

## Findings

**F1: The Master Rules read as not in force.**
- **What happens:** the generated `docs/contract/master-rules/MR-1.md` to `MR-6.md` say `status: PROPOSED`, while
  `contract.yaml` says ACCEPTED. S9 therefore marks every MR item `in_force: false, not_in_force: PROPOSED` (search 9:
  MR-3 ranked 1st). A binding rule reads as not in force.
- **Known already:** `gov links` reports it as STATUS_CONFLICT ×6, "expected" at W2-129 point (10).
- **Effect on the 80:** E0's store at `c00d525f` holds the same six PROPOSED rows, so the 80 measures it as it is.
- **Scope:** in scope.
- `Ordinary work: yes, because any question naming a master rule gets the mark, at the top of the bundle.`
- `Consequence: other (the guard still enforces MR-3 by paths; the answer may hedge or make a wrong claim about an MR's
  standing).`
- **Makes the verdict wrong:** no.
- **Class:** **ROW**.
- **Recommendation:**
  - regenerate the six MR records from `contract.yaml` in W2-130's clean-up, before the release;
  - when the 80 is read, attribute any wrong claim that traces to an MR mark to this known data defect, not to the
    run.

**F2: Spurious changers.**
- **No-verb labels:** a `**Changed by:**` value with no verb takes every DEC id in its text as a changer.
  - DEC-880 ← DEC-843 (the label's text names DEC-843 as the object of DEC-882's correction);
  - DEC-281 ← DEC-208, DEC-237, DEC-838 (DEC-281's former basis, not its changers).
- **Free text with no subject:** a clause such as "the cache withdrawn by DEC-880" with no id before it is taken as a
  change of the entry itself (DEC-1053 ← DEC-880).
- **Size:** 11 change links have a changer older than its target, so they are certainly wrong. 144 no-verb statements
  fall on 87 targets, and 39 of those targets have more than one.
- **Shared:** `gov links` reads the same function, so the same noise appears in UNMARKED_CHANGE.
- **Scope:** in scope.
- `Ordinary work: yes, because these entries come up in ordinary questions (search 3).`
- `Consequence: other (extra ids in changed_by; nothing current is hidden and nothing superseded shown as current; it
  may invite a wrong claim, which the 80 then measures as it is).`
- **Class:** **ROW** (the loader's next pass: take one changer per clause of a no-verb value, by its leading id).

**F3: DEC-1097 changes K9's bar without a mark.**
- **What changed:** DEC-1097 (1)(d) moves K9's bar from 85 % hit@5 (DEC-1083 (2)) to 85 % right end to end with wrong
  claims at most 5 %, hit@5 reported beside it.
- **Why nothing sees it:** neither entry states the change. DEC-1097 lists DEC-1083 (2) under `**Under:**`, so the
  bundle shows DEC-1083 in force, changed by DEC-1087 and DEC-1084 only (search 8), and `gov links` cannot find it.
  DEC-866 item 1 asks that the old entry be marked at once.
- **Scope:** in scope for the marks' correctness; the cause is the register's text, not the code.
- `Ordinary work: yes, because whoever builds FRESH-80-1's scripts (items 14-19) will ask exactly this.`
- `Consequence: other (DEC-1097 ranked 2nd in the same bundle; the 80's commit predates both decisions; the verdict is
  computed from DEC-1097 itself).`
- **Class:** **ROW**.
- **Recommendation:** one line now under DEC-866, no round. Add to DEC-1083's status line
  `**Changed by:** DEC-1097 (1)(d) (the bar is end to end, wrong claims at most 5 %; hit@5 beside it)`, or add
  `**Changes:** DEC-1083 (2)` on DEC-1097. Before the scripts are built.

**F4: Changers are named but not fetched for decisions found only by text.**
- **What happens:** for a decision that only the lexical or meaning route reached, `changed_by` names its changers,
  but the hop does not fetch them. The hop starts only from the record route and the closure. Example (search 6):
  DEC-1066's changer DEC-1067 is named and absent.
- **Covered by:** this is S8 as specified, and the search-again practice (DEC-1092 (1)) covers it.
- **Scope:** in scope.
- `Ordinary work: yes, because most questions name no id.`
- `Consequence: other (the changer is named, so nothing reads as current).`
- **Class:** **ROW**.

**F5: Two status words read as in force.**
- **What happens:** CONDITIONAL (1 entry, "adopt only when its trigger fires") and DONE (5) read as `in_force: true`.
  S9 names only PROPOSED, REJECTED, WITHDRAWN and SUPERSEDED.
- **Known already:** this repeats W2-92 review S9's note.
- **Scope:** out of scope (the KPI's list).
- `Ordinary work: yes, because an honest agent can reach one of these 6 entries in a search.`
- `Consequence: other.`
- **Class:** **ROW**.

**F6: The standing link findings stay open.**
- **What they include:** 141 NOT_IN_FORCE_AS_RULE. Among them, the kernel retrieval skill cites PROPOSED DEC-032,
  DEC-034 and DEC-035 in 5 lines, and `w2-orchestrator.md` cites SUPERSEDED DEC-869. Also 110 STATUS_CONFLICT (spent in
  ARCHIVE §B, current in the register) and 186 UNMARKED_CHANGE.
- **Status:** all known; this is W2-130's work. `gov links` is a notice by design (DEC-1052).
- **Scope:** out of scope (data, not the tools).
- `Ordinary work: yes, because agents read these kernel skill lines and prompt lines in ordinary work.`
- `Consequence: other.`
- **Class:** **ROW**.

**Out of my aspect, for the CTO (no class given):**
- **A shared scratchpad:** the seven reviewers share the session scratchpad. Another reviewer overwrote my first output
  file (`q1.json`). I moved to `scratchpad/r2-links/`, now copied to `scratchpad/readiness-2/`, and re-checked, so no conclusion here
  rests on a foreign file.
  Same-named outputs in the shared folder could mislead a reviewer.
- **The store moved:** the store link switched during my run, from `e66f2a696` to `0732a0a74a31` (aspect 1's
  refresh). That does not change any finding here.

## Evidence

- **Outputs:** `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/ad44f5fe-276d-46b7-85cd-df9f8d97a3ec/scratchpad/readiness-2/`
  holds `s6.json` to `s9.json`, copied from my private `r2-links/` per the coordinator's note. Each was checked against
  the figures printed as it ran (first items and hop records match), so all four are my own searches.
- **Searches 1 to 5:** their shared-folder files (`scratchpad/q1.json` to `q5.json`) were later overwritten by other
  reviewers. This record cites only the figures I printed as each search ran, never those files.
- **Scratch:** 380 KB and 10 inodes; nothing heavy was run.
- **Which questions `gov retrieve` answered:** searches 1 to 9 above. Searches 6 and 8 left a changer outside the
  bundle, so I checked the store and the register directly; I did not run a second search for them.

```verdict
{"kpis": [
 {"kpi": "S7 stated links", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S8 one bounded hop", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S9 status in the bundle", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "W2-129 gov links (notice, standing findings)", "verdict": "pass", "findings": [{"id": "F6", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}
]}
```

READY for the 80: no finding is in scope, reachable in ordinary work and failing open (or making the verdict wrong).
