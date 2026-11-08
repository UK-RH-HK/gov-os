# Readiness reviewer 7 of 7: the fresh 80's own readiness (DEC-1097 (3); FRESH-80-READINESS §5 item 7)

2026-11-08, read-only, for the Wave 2 CTO. Judged against DEC-1097 (1)-(3) and FRESH-80-1 (§2's twenty items, §3.2's
order, §3.4's rule, §3.5's fault rule, §4.3's rounding). Read: JUDGEMENT.md, AUDITOR-common.md, DEC-1097, FRESH-80-1,
FRESH-80-READINESS, the draft FRESH-80-DECLARATION, `drafts/fresh80/` (README and every script, read whole except the
E4 bash copies, which I read only for the hold and the write targets), `drafts/sets-root-guard/` (DESIGN §A-E,
REHEARSAL, path-map.patch, apply.sh's header, the F cases), RESTART-CLASSES §rules, DEC-1028 (6) and the w2 prompt's
commit-freeze line, the pin's `gov/retrieval/measure.py` (how a failed retrieval ends a run).
Nothing under `~/gov-os-eval/` or any run-folder row under `~/gov-os-runs/D4B/` was opened or listed. No `gov
retrieve` (the brief forbids live searches): no retrieval question asked; guard refusals: 0. I ran
`pytest drafts/fresh80/tests` (planted set, fake gov, fake model): **52 passed**. Scratch: 100 MB / 25,112 inodes at
the peak (pytest's temp folders), cleaned to 4 KB.

## 1. The twenty items against something concrete
| # | item | met by | state |
|---|---|---|---|
| 1 | the set unchanged; digest | `preflight.py` item1 (80 files, mode 700, no other entries, mtime after DEC-1078's close, combined digest in the `sha256sum *.yaml \| sha256sum` form; test `test_digest_is_sha256sum_form`); declaration §1 blank | met; the result "repeats" the digest only as a copy (F6) |
| 2 | anchors at the measured commit | `preflight.py` item2, the measure's own `_load`, `_anchored`, `_lines_at`; five classes plus no-heading classes; named by id and entry | met |
| 3 | stale gold answers | the checker's brief (READINESS §2); `--expect-sha256`, `--expect-changed` | met, with gaps in the brief (F3, F4) |
| 4 | the q12 sync not applied | nothing applies it; the 80's labels untouched by the tools | met |
| 5 | families line | `preflight.py` item5; `f80_check.py families` again just before the 80; the control and each attempt's first line | met |
| 6 | nonexistent-id question | `preflight.py` item6 (`lexical.ids_in`, whole-token `git grep`), by category; figures' drop branch; `gap_names_ids` for DEC-1071 (5) | detection met; **the drop path is unreachable** (F2) |
| 7 | readers read the 80; run folder under the sets root | `f80lib.paths` (`runs/fresh-80`); the ACT's `runs/fresh-80/**` glob (path-map.patch, F1-F23 cases) | met in design; **no gate that the ACT is applied** (F1) |
| 8 | grader agreement; stricter grade as data; no re-grade | reader keeps both grades; figures `stricter`, `agree`, `no_grade` | met |
| 9 | "answer correct, citation aside" | figures `correct` | met |
| 10 | commit `c00d525f` before the re-pin | `COMMIT`, `item12`, `f80_check clone` (HEAD, clean, pool, gov link at the pin) | met |
| 11 | exact command; control 34 ± 2 first | `run_measure.sh` `measure()` (e0_run's form, defaults, `GOV_ROLE=orchestrator`, GOV_KEEP wrapper); `f80_check control` | met |
| 12 | clone and store unchanged | `item12`; store sha before/after each attempt; no rebuild (test `test_no_rebuild_in_the_script`) | met |
| 13 | nothing beside the live parts | the hold line; integrate head and store-log lines recorded over the window (recorded, not enforced) | met as a CTO rule (F5 on the hold file) |
| 14 | one shot | `USED` written with noclobber after the control and before the 80; refused once it exists; one `--restart` | met |
| 15 | fault mid-run | `run_measure.sh` §8 (automatic restart into attempt-2, `--restart` after a kill, STOPPED on a second fault); a failed retrieval ends the measure with exit 1 (`measure.py` `_ask` raises), so it is caught | met |
| 16 | reader resumes | `one()` skips a question with a row; rows written whole (`os.replace`) | met |
| 17 | silent search failure | `L.search` returns ok False; counted and named by id | met |
| 18 | citations outside received items | `outside_citations`, `citation_right_only_outside` | met |
| 19 | fresh-80 copies, dry mode, review, pinned | every tool has `--dry`/`DRY=1`; `FRESH80-REVIEWED.sha256` checked by every runner (absent today, as it should be before READY) | met |
| 20 | hidden-half rule for the CTO | `say` refuses hidden paths; ids and counts only; category never beside id; the guard design allows only root-only command lines | met (F10 on tracebacks) |

The rounding (§4.3) is right in code: `L.bar` gives 68 / 3 / 76 on 79, and 67 and 4 miss (tests at the edges).

## 2. The declaration draft against §3.4 and DEC-1097
- **Judged condition in full:** pin, clone, commit, store (as written by E0, not rebuilt), flags (pool on), bundle
  6,000, reader and prompt (E2's, pinned by sha256), three attempts and the A2 cut, both graders, the matcher with
  families. The labelling **rubric** that §3.4 lists is not named (F7).
- **Denominator, bar, rounding:** 79, at least 68 right **and** at most 3 wrong claims, target 76; observed figure;
  hit@5 beside it, never in it. Consistent with DEC-1097 (1)(d).
- **Data conditions:** every experiment of the 138 (e3, e3sa, e5, e4 with M3 and M1, e2g, plus A1, A3, retrieval),
  each labelled "data only, not judged", with projection and brake. Consistent with (1)(c) and (5). Only (1)(a)
  judged.
- **Fault rule:** §3.5 as written, plus "a store changed during an attempt stops everything", which follows from
  "the same store" and is stricter, not looser.
- **Blanks to fill before commit:** the interval's name (F7) and the pre-flight's counts. No line records that
  ACT-GUARD-SETS-1 is applied (F1).

## 3. The checker's brief (READINESS §2)
Sufficient in substance: an outside checker in a clean clone at `c00d525f`, outside the guard, never the CTO's tools,
counts only back (unchanged, changed, ambiguous, re-labelled) and a new combined sha256. **It does not give the
digest's form**, so the `--expect-sha256` comparison can fail on form alone (F3), and it leaves four cases without a
rule (F4). All of them fail closed: the pre-flight stops, nothing is measured.

## 4. The order
FRESH-80-1 §3.2, the README's steps and the declaration agree: checker → (ACT applied) → pre-flight → declaration
committed → hold → control → `USED` → measure → judged reader → hold ends → data conditions → figures. The code
enforces most of it: the measure and the reader refuse without the hold, the pin and a clean pre-flight; `USED` is
written only after the control passes; data conditions and E4/E5 refuse while the hold stands and before the reader's
summary exists. **Two steps are text only:** the ACT applied (F1) and the declaration committed (F12). Before the
ACT, the only thing that opens the 80 on the CTO's side is the pre-flight, which writes counts only
(`preflight.json`): no leak. The first files holding question text (kept `gov retrieve` outputs, reader rows) are
written by `run_measure.sh` and the reader, and neither checks the ACT.

**The hold convention** (`FRESH-80 HOLD` in `log/act-in-progress.txt`): the same file as DEC-1028 (6)'s ACT freeze,
with precedent (`e4_window.sh` used it as "the CTO's own hold"). Mostly helpful: the ACT scripts stop while it
stands (ACT-RERANK-TRIAL-1/2), the commit-freeze reading ("no commit that touches the paths named") covers it, since
the line names every commit on `w2/integrate`, and checkpoints are held. One collision: README step 3 writes it with
`>` (F5).

## 5. Findings

### F1 — FIX BEFORE THE 80: nothing checks that ACT-GUARD-SETS-1 is applied before the 80 is touched
- Where: `run_measure.sh` step 1, `fresh80_reader.py` `main`, `preflight.py`; the declaration has no line for it.
  README step 1 says "after … ACT-GUARD-SETS-1 applied" in prose only. The live map has no `sets_root_hidden` today.
- Why it matters: DEC-1097 (2) says "applied before the 80's single use". Without it, the kept outputs and reader rows
  under `runs/fresh-80/`, and the 80 itself, are open to every measured role, including the W2-141 / P-SELECT-GRAPH
  / W2-130 sessions DEC-1097 (8)-(9) run beside it. The same ACT was missed once already (READINESS §3: "Applied: no
  … the CTO did not catch it").
- Fix (minutes): one check in `run_measure.sh` (and the reader), before anything is written. The main tree's
  `governance/project/path-map.yaml` has a `sets_root_hidden` block whose hidden list holds `runs/fresh-80/**` and
  `fixtures/evaluation/memory-verdict-2/**`, and the live `.claude/hooks/pretooluse.py` holds `sets_root_rule`. Check
  the content, not hashes, which later commits move. Add a declaration line: "ACT-GUARD-SETS-1 applied (commit,
  guard check), live worktrees merged: ____".
- Scope: in. Ordinary work: yes, because a step held only in prose was already missed for this very ACT.
- Consequence: fails open (the hidden-set protection is absent at the single use). Note: E0's clone store is frozen
  and the reader has no tools, so the figure itself cannot be tuned by a reader of the 80; the open part is the
  protection the owner required.

### F2 — ROW: the declared drop for the nonexistent id is unreachable in code
- Where: `preflight.py` `item6` returns not ok when a token now exists, so `all_ok` is false. `run_measure.sh` refuses
  "the pre-flight has not run clean" (`test_nonexistent_id_now_exists` asserts rc 1). Yet FRESH-80-1 item 6, DEC-1097
  (1)(g) and the declaration say "dropped from every figure", and `fresh80_figures.py` has the drop branch.
- Fix: count item 6's "no" as the declared drop (ok, with `dropped` true) instead of a stop; the question is outside
  the 79 anyway.
- Ordinary work: yes, because DEC-1079 to DEC-1088 and W2-128 to W2-136 exist at `c00d525f` and were created after the
  set. Consequence: other (fails closed: the run is blocked and goes to the owner; the verdict is not touched).

### F3 — ROW (ride along before the brief is sent): the checker's brief does not state the digest's form
- Where: READINESS §2 says "the new combined sha256". The pre-flight compares the form `sha256sum *.yaml | sha256sum`
  in the set's folder, in name order (README open item 2). The shell's glob order follows the locale, Python's
  `sorted` follows code points, so add `LC_ALL=C`.
- Fix: put the line in the brief word for word: `cd <set folder> && LC_ALL=C sha256sum *.yaml | sha256sum`.
- Ordinary work: yes, because "a combined sha256" is often taken as `cat *.yaml | sha256sum`. Consequence: other (a
  mismatch stops the pre-flight; one more operator round).

### F4 — ROW: four cases without a rule in the checker's brief
- (a) *ambiguous*: nothing says what the writer does, and a reader right by one statement is graded wrong (fails
  closed). Suggest: the writer adds the second place as an alternative and the gold accepts either, or the CTO
  decides from the count before the declaration.
- (b) the nonexistent id found to exist: say "flag only, never change the question" (FRESH-80-1 item 6 decides).
- (c) "keeping … commit field" against "re-labelled to `c00d525f`" reads both ways. Say "the commit field set to
  `c00d525fd420`".
- (d) the pre-flight's own checks, which the writer must respect:
  - old labels go to `memory-verdict-2/retired/`, never inside `hidden/`;
  - no stray files (`*.yaml~`, swap files);
  - folder mode 700;
  - unchanged files keep their mtimes (no copy-back of the folder);
  - `--expect-changed` = re-labelled entries plus any later item-2 fixes.
- Ordinary work: yes. Consequence: other (each fails closed at the pre-flight or lowers the figure).

### F5 — ROW: the hold is written with `>` over any existing `act-in-progress.txt`
- Where: README step 3, and `mv` at step 6. If the ACT's own mark still stands (its hand-over mark is ended only on
  the owner's word, DEC-1028 (6)), or an "E4-WINDOW NOT RESTORED" mark does, the hold overwrites it and step 6 ends
  it without the owner's word.
- Fix: `[ -e …/act-in-progress.txt ] && echo "STOP: $(cat …)" || echo "FRESH-80 HOLD …" > …`, as ACT-RERANK-TRIAL-1
  line 87 does.
- Ordinary work: yes, because the ACT is applied just before the pre-flight. Consequence: other (a freeze mark lost;
  nothing in the measure).

### F6 — ROW: the 80's digest is not recomputed at the run
- `f80_check preflight` trusts `preflight.json`'s `all_ok` with no age or digest check. A late writer fix after a
  clean pre-flight would be measured with the declaration's digest no longer true. Item 1's "the result record
  repeats the digest" is met only as a copy.
- Fix: `run_measure.sh` recomputes the combined digest before `USED` and compares it with `preflight.json`, and the
  figures print it.
- Ordinary work: yes (a late fix round). Consequence: other.

### F7 — ROW: the declaration's open choices
- Name the interval beside the verdict (Clopper-Pearson or Wilson; FRESH-80-1 §4.3's example is Wilson's) before the
  commit.
- Name the labelling rubric version that §3.4 lists.
- Add F1's ACT line.
- Ordinary work: yes. Consequence: other (beside the bar, not in it).

### F8 — ROW: data spend above the option the owner chose
- Data conditions project 108 USD (brake 216), plus 15 for the judged run. FRESH-80-1 §5 3(c), which the owner chose,
  said "about $60 to $70 more".
- Tell the owner the corrected figure with the launch notice (DEC-1097's order: "The CTO tells the owner when it is
  ready").
- Ordinary work: yes. Consequence: other.

### F9 — ROW: e2g runs on the 80 while GLOSSARY-1 is OPEN (DEC-1097 (6))
- The result record should say that the 80's e2g figure cannot decide GLOSSARY-1 (§3.4 item 4: no figure on the 80
  chooses anything).
- Ordinary work: yes. Consequence: other.

### F10 — ROW: Python tracebacks reach `~/gov-os-runs/fresh-80/*.out`
- README steps 5 and 8 send the Python tools' stderr there with `2>&1`, outside the protected folder; the bash
  scripts already route stderr into the run folder. A traceback's message rarely holds question text.
- Fix: the Python tools redirect their own stderr into the run folder, since the CTO's line may not name it.
- Ordinary work: yes. Consequence: other.

### F11 — ROW: the declaration's commit (step 2) starts the integration store's refresh minutes before the control
- This is a different store (E3-SA's slip, about 30 s, no effect seen). Wait for its log line before step 4.
- Ordinary work: yes. Consequence: other.

### F12 — ROW: nothing checks that the declaration is committed, with no blanks, before `USED`
- DEC-1097 (1) itself already fixes the judged condition and the bar in the register, so a late commit cannot move
  them. A check in `run_measure.sh` (`git log` holds the file, and it has no `____`) costs one line.
- Ordinary work: yes. Consequence: other.

**Classification (DEC-809):** 1 finding in scope, ordinary work yes, fails open (F1); 11 rows (F2-F12), all fail
closed or other. Recommendation: fix F1, with F2, F3 and F4 riding along in the same pass and F3/F4 before the
checker's brief is sent; then READY. None needs a second round.

```verdict
{"kpis": [
 {"kpi": "FRESH-80-1 §2 items 1-20 met by concrete steps", "verdict": "fail", "findings": [
   {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"},
   {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F10", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "declaration complete per §3.4 and consistent with DEC-1097", "verdict": "pass", "findings": [
   {"id": "F7", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F8", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F9", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "checker's brief sufficient; what comes back", "verdict": "pass", "findings": [
   {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "order safe; nothing touches the 80 before the ACT; hold convention", "verdict": "fail", "findings": [
   {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"},
   {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F11", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F12", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "§4.3 rounding and §3.5 fault rule in code", "verdict": "pass", "findings": []}
]}
```

**Verdict: NOT READY for the 80**: one fix (F1), minutes of work; READY once F1 is in and the files are pinned.

## Round 2 (the last; 2026-11-08)
Checked against the files: `drafts/fresh80/` (f80lib, f80_check, preflight, run_measure.sh, the reader, figures,
data, hold.sh, README), the declaration draft and FRESH-80-READINESS §2 at `a06dfa804bbb`. Nothing under
`~/gov-os-eval/` opened. `pytest drafts/fresh80/tests`: **74 passed** (52 before), including
`test_refused_without_the_act` (measure), `test_reader_refused_without_the_act`,
`test_refused_without_the_act_nothing_written` (pre-flight), `test_refused_declaration_blank_uncommitted_or_digest_moved`
and `test_hold_never_overwrites_and_ends_only_its_own`. Scratch peaked at 151 MB and was removed.

| finding | round 2 | state |
|---|---|---|
| **F1** (FIX) | `L.act_applied` checks content, never hashes: the main tree's `sets_root_hidden` names this sets root, its globs hold `runs/fresh-80/**` and `memory-verdict-2/**`, the orchestrator is refused, and the live hook has `def sets_root_rule(`. It runs before anything is written: `run_measure.sh` (its first refusals, before `mkdir`), each Python tool through `L.run_tool`, `f80_e5_live.sh` and `f80_e4_prep.sh`. The declaration has an "ACT-GUARD-SETS-1 applied at ____; guard check ____; live worktrees merged ____" line, which `declared` forces filled | **closed** |
| F2 | `item6` returns ok with `dropped` when the id now exists; figures print the drop | closed |
| F3 | brief: `cd <set folder> && LC_ALL=C sha256sum *.yaml \| sha256sum`; `L.set_digest` sorts by bytes | closed |
| F4 | brief: rules for *ambiguous*, the nonexistent id flagged only, the commit field set to `c00d525fd420`, `retired/` outside `hidden/`, file hygiene and mtimes | closed (row R2-1 below) |
| F5 | `hold.sh begin` refuses to overwrite any mark; `end` moves only its own | closed |
| F6, F12 | `f80_check declared`: tracked, clean at HEAD, no `____`, digest = the set's now = the pre-flight's; before the first attempt and before each attempt; figures repeat the digest | closed |
| F7 | rubric line and interval blank in the declaration; `declared` refuses while a blank stands | closed |
| F8 | README: tell the owner 108 USD with the launch notice | carried to the owner (row) |
| F9 | README: the 80's e2g figure cannot decide GLOSSARY-1. Not yet in the declaration's §4 | row (add one line to §4) |
| F10 | `run_tool` sends stderr and tracebacks to `<run folder>/<name>.err`; the CTO sees the class only | closed |
| F11 | README step 2: wait for the integration store's refresh line | closed |

New in round 2, rows only:
- **R2-1:** the brief's *ambiguous* entries get a new source, so they change files. The counts back list
  "re-labelled" but do not say whether ambiguous entries are in it, and `--expect-changed` must count them.
  - Ordinary work: yes, because the checker may report re-labelled = changed only.
  - Consequence: other (a mismatch stops the pre-flight; one more operator round).
- **R2-2:** `f80_e4_window.sh`, `f80_e4_replays.sh` and `f80_so_measure.sh` do not call the ACT check themselves.
  They run only after `f80_e4_prep.sh`, which does, and they write only under `data/e4/` after the judged run.
  - Ordinary work: no, because only an undo of the applied ACT between steps reaches it.
  - Consequence: other.
- Readiness 5's F2 (the writer and checker transcripts open) is with the owner's operator before the pre-flight. That
  is outside this aspect; it is noted only so it is not lost.

```verdict
{"kpis": [
 {"kpi": "FRESH-80-1 §2 items 1-20 met by concrete steps", "verdict": "pass", "findings": [
   {"id": "R2-2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "declaration complete per §3.4 and consistent with DEC-1097", "verdict": "pass", "findings": [
   {"id": "F8", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F9", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "checker's brief sufficient; what comes back", "verdict": "pass", "findings": [
   {"id": "R2-1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "order safe; nothing touches the 80 before the ACT; hold convention", "verdict": "pass", "findings": []},
 {"kpi": "§4.3 rounding and §3.5 fault rule in code", "verdict": "pass", "findings": []}
]}
```

**Round 2 verdict: READY for the 80** on my aspect, once the files are pinned and ACT-GUARD-SETS-1 is applied. The
tools now refuse to run without the ACT. Rows: F8, F9, R2-1, R2-2.
