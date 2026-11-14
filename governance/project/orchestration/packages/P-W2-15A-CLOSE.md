# P-W2-15A-CLOSE: what W2-15a's close needs, and the owner's operator's walled run for the hidden half

For the owner. Draft of 2026-11-14 23:51 UTC, by a helper of the CTO, from the committed records only. Nothing in it
ran on the hidden half; no hidden folder, question, answer or count was read. Head when drafted: `ebedddd60c09`
(`w2/integrate`). Ticket `.tickets/DAEO-rd0g.md` (W2-15a, open); DECIDED-NOT-DONE row 35.

## 0. In short
- The visible half is the CTO's run (section 4); the hidden half is yours (section 2): one script, counts only.
- Two things come first: a revised metric section committed before any new run, and one recorded refused probe of the
  sets root's hidden folder from a worktree (section 1, lines 1 and 4). Neither exists in the repository today.
- A miss on 34 of 39 is a live possibility (section 3). Three questions for you are in section 6.

## 1. What the close needs, line by line (DEC-1171 (3), the ticket's four lines as D9-FATES numbered them)

| Line | What it needs | What exists | Still open |
|---|---|---|---|
| 1 Metric | A metric section committed before the pass's first run, with every raw output dated after it. W2-61's measure, both figures, on the current set (40 visible, 39 hidden until 40): hit@5 against 95 % (floor 85) and the all-evidence share against 99 %; memory proven at hidden hit@5 of at least 34 of 39 (35 of 40). Hidden figures copied from your operator's walled record, after a recorded refused probe read from a worktree. | Section 2 of `docs/research/EXP-003/w2-15a-baseline.md`, in `fd637510d7ad`, is the metric of the 48-question set (24 visible, 24 hidden, 21 of 24). It was committed together with its raw outputs, not before them. Its figures (28 of 48 hit@5, 16 of 24 hidden) are on the old set and the old code. Reference points on today's sets: E0 of 2026-11-07 (`b741707e1eee`, `packages/LIFT-1/E0-RESULT.md`): visible 34 of 40 hit@5 (85.0 %), full evidence 35 of 40; hidden 32 of 39 (82.1 %, h24 apart, old labels). Fresh 80 (DEC-1129 (1)): 84.8 % hit@5, 78 of 79 right end to end. | (a) a revised section 2 for the current set, committed before the run; (b) the visible run; (c) the hidden run; (d) the probe. No committed record of a refused probe of the real sets root was found in `docs/probes/`, `closes/` or `packages/`. |
| 2 Five modes | One row per mode (lexical, semantic, fused, fused plus reranker, lighter reranker): both figures on the visible half, hidden counts from your operator's record, command, versions, raw under `docs/research/EXP-003/w2-15a/raw/`. A mode with no row leaves the line unmet. | Pass 1's four rows on the old 24/24 set (`raw/table.md`, `raw/measure-*.txt`). The lighter reranker is not installed (D9-FATES: met in part). | Four rows on the current set: visible by the CTO, hidden by your operator (sections 2 and 4 take the four modes). The lighter reranker row stays unmet: question Q1. |
| 3 Stacking test | One run of a 24k-unit question retrieved in batches of at most 8k, with its raw output and each check's result (a failing check is recorded as failing). | Met: section 6 of the baseline and `raw/stack-q14.json`, `raw/stack-q14-duplicates.txt` in `fd637510d7ad` (complete: yes; no duplicates: fails, 3 hashes). Q14 was re-worded on 2026-11-09, so the test is not re-run. | Nothing. |
| 4 Closes | Every measure of lines 1 to 3 per mode, with command, gov, model and reranker versions, clone commit, store digest and raw kept; each figure re-derived from raw by the record's table script; at most three gaps, each with the misses it is meant to reach; DEC-1171 (3) sends them to W2-15b. | Section 8 of the baseline names three gaps (chunking view, ranked-lexical tuning, the fusion's route hits), written for W2-32 on the old set. W2-32 is closed (`8ba025e8fa26`). | The record rewritten from the new run: versions, digest, table, the misses classified (visible with `diag/` and `goldpos.py`; hidden by ids and ranks only), at most three gaps. More than three is a P1 for you. |

**Order (the ticket's own rule):** (1) the research session commits the revised section 2 and it lands on
`w2/integrate`; (2) the probe; (3) the CTO's visible run and your walled run, both at one named head that holds (1);
never at the same time as each other or as a store rebuild (one GPU job at a time); (4) the record from both.

**The probe (line 1):** one launched `research` session in W2-15a's worktree makes one Read of a file that does not exist
under the sets root's hidden folder (a name such as `zz-probe-w2-15a.yaml`) and records the guard's refusal, with no
content. This helper did not run it: it is itself a read attempt on that folder.

## 2. The owner's operator's walled command (the hidden half, counts only)
A plain terminal, not under the guard, no `GOV_ROLE`, no `GOV_TICKET`. Script:
`.gov-runtime/scratch/orchestrator/drafts/w2-15a-close/walled_hidden_counts.sh` (parses; refuses at once if a role is
set). It checks the tree, clones afresh, builds the store seeded from the integration store, then runs the measure on
`--part hidden` alone, one mode after another, each through `heavy_slot.sh`, with the GPU backstop armed.

```
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-15a-close
C=ebedddd60c09            # the head that holds the revised section 2; the same commit the CTO's visible run names
git -C /home/usain/Dynamic-Agentic-Engineering-OS merge-base --is-ancestor $C w2/integrate && echo tree-ok
env -u GOV_ROLE -u GOV_TICKET setsid --wait bash $D/walled_hidden_counts.sh $C rerank lexical semantic fused
```
What the script does in the clone at `~/gov-os-runs/W2-00/w2-15a-close-walled/repo`, as its first lines: `git merge-base
--is-ancestor <commit> w2/integrate`, a fresh `git clone --no-hardlinks`, `checkout --detach <commit>`, `git merge-base
--is-ancestor <commit> HEAD`, and a clean `git status --porcelain`; it stops on any failure. The measure itself is
`python3 -m gov.retrieval.measure memory-retrieval --root <clone> --sets-root ~/gov-os-eval --part hidden --out
~/gov-os-eval/runs/w2-15a-close/<mode> --gov <wrapper of W2-15a's committed modes.py>`. The measure's text (it names
each hidden question's id and rank) and its record go to files under the sets root's `runs/` folder (mode 700), never
to the terminal. Mode `rerank` is the shipped path; the other three are pass 1's modes on the same code.

**Hidden count today: 39, as far as committed records show.** The hidden-form count case reads 39
(`HIDDEN_COUNT = 39`, revised in `94aa1debcbba`); your operator's walled run at `5f9a9dedf7c0` (2026-11-14) passed it,
and `96321d437ad7` closed W2-61h on it; h10 left on 2026-11-13 (DEC-1171 (2), `dff6e46615b5`). DEC-1171 (2) made 40
conditional on a walled writer's round 2 whose brief variant was to come to you for approval; no approval and no
later commit records a replacement. The count the script prints settles it: 39 gives the line 34, 40 gives 35.

## 3. Output, pass line, and a miss
Per mode the terminal shows five lines and the pass line, for example (planted figures, not a result):
```
-- mode rerank: exit 0, 1004 s
   questions judged: 39
   right, hit@5: 35 of 39 (89.7 %); floor 85, target 95
   all evidence in the stacked context: 37 of 39 (94.9 %); target 99 %
   gold blocks unresolved: 0
   commit: ebedddd60c09; part: hidden
   PASS LINE: PASS: hit@5 35 against 34 of 39
   record sha256: <16 hex>...; stderr lines: 0
```
- **Pass:** `rerank` at 34 of 39 (35 of 40) or more is the memory proof; the all-evidence share and hit@5 are judged
  against 99 % and 95 % (floor 85) and recorded either way. The other three modes have no pass line; their counts
  fill the mode table.
- **A miss** (below 34 of 39 on `rerank`, or either figure below its floor): the figures are recorded as measured; the
  research session classifies the misses (visible by `diag/`, hidden by ids and ranks) and names at most three gaps for
  W2-15b, each with its misses. More than three is a P1 for you. How near a pass to expect: E0 gave 82.1 % hidden and the
  fresh 80 gave 84.8 %, against 87.2 % (34 of 39); a miss is the likelier outcome. Whether a miss still closes the
  ticket is question Q2.
- `stderr lines` counts the measure's unresolved-block lines (ids are in the file, never on the terminal). Five hidden
  questions (h03, h20, h24, h35, h36; six entries) await the walled writer's re-anchoring on Monday 2026-11-16
  (`packages/REANCHOR-LIST-20261116.md`); if the measure scores them against changed text, the counts can read low.
- h24 is the nonexistent-id question; the measure counts it like every other file (the older figure scripts set it
  apart), so 39 and 34 above include it, as DEC-1171 words them.
- Time: pass 1 ran 1,171 s for 48 questions in `rerank` (about 7 s a call). Expect 15 to 20 minutes a mode on a quiet
  machine, so 60 to 80 minutes for four. Today (load near 40) a call took about 40 s.

## 4. The visible half, the CTO's run
`bash .gov-runtime/scratch/orchestrator/drafts/w2-15a-close/visible_run.sh <commit> rerank lexical semantic fused`
(absolute path as above; the script is itself the heavy-slot form: the rebuild and each measure go through
`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
`TMPDIR=/tmp/gov-os-w215a`, `PYTHONUSERBASE=/home/usain/.local`). It makes a fresh clone under
`~/gov-os-runs/W2-00/w2-15a-close/`, does the same tree check, builds the store, and measures `--part visible` with the
clone as sets root (so the sets root is not touched and no hidden name appears). Its output ends with the same
counts block per mode and the line "VISIBLE HALF (no pass line of its own...)". Run it before or after yours, never
beside it. The records land in `.../w2-15a-close/out/records-<mode>/` for `table.py`.

**Rehearsal (2026-11-14 23:39 to 23:50 UTC, at `ebedddd60c09`):** the tree checks passed; the clone was 392 MB (988 MB
with its store); the seeded rebuild took 169 s; the measure started through `heavy_slot.sh` after a wait for a slot,
`modes.py rerank` ran the head's code and the shared reranker service scored (log lines `service`). I stopped it
after 10 reranks in about 7 minutes (load 38 to 41 from other leads' test runs), past the 20-minute bound, so no
figure exists. The clone and its store were removed (the log is `rehearsal-visible.log` in this folder).
The hidden script was not run; its `bash -n`, its refusal under a set `GOV_ROLE` and `counts_only.py` on planted data
were checked.

## 5. The owner's line to the operator
`Run in a plain terminal: env -u GOV_ROLE -u GOV_TICKET setsid --wait bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-15a-close/walled_hidden_counts.sh <commit> rerank lexical semantic fused, after the probe is recorded; give the CTO only the printed counts and the pass line.`

## 6. For you
- **Q1, the lighter reranker (line 2):** (a) accept the row as "not installed" and the line met in part, as D9-FATES
  fated it (recommended: no install is decided or costed); (b) install one first (a new decision and a cost).
- **Q2, a miss:** (a) W2-15a closes on the measured record with at most three gaps to W2-15b, S1's memory clause
  re-worded to "recorded against 34 of 39" (your exception to DEC-757 (6) for the ticket file; recommended: the ticket
  is a baseline, DEC-1171 (3) sends gaps to W2-15b, K9's bar is the end-to-end one of DEC-1097 (1)(d)); (b) the ticket
  stays open until a later run meets 34 of 39.
- **Q3, the hidden record:** (a) counts only in the record (the table script re-derives the visible half; hidden cells
  are copied from your operator's printed counts; recommended); (b) also ids, first gold rank and hit or miss per
  hidden question (`counts_only.py --ranks`, no text; DEC-1171 (3) allows it), so the table script re-derives hidden
  cells and the gaps can be classed per question.
