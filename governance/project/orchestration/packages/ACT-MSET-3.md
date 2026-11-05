# ACT-MSET-3: the new verdict set: 80 questions, written fresh and blind by a new writer (DEC-1074 (3))

- **For:** the owner (section 0), then the owner's operator (section 9), then **a new session the owner opens,
  outside the CTO's system**, used only for this: a plain terminal, not under the guard, not launched by `gov launch`,
  with no access to the CTO's session or its agents. It is not the writer of the 60 (`~/gov-os-writer`).
- **Nothing about these questions reaches the CTO's session.** The writer reports to the owner only "done" and the
  count lines of section 6.
- **By:** the CTO, session `812bc5ce`, 2026-11-05, from ACT-MSET-1 and ACT-MSET-2 (the 60's briefs, which worked:
  cross-check 52 as written, 4 minor, 4 major, 0 drops).
- **The cross-check** is ACT-MSET-4, in the same package, for a second new session.

## 0. For the owner: what you decide
1. **This brief** for the writer (sections 1 to 8), and ACT-MSET-4 for the checker.
2. **The one real choice, the failure-memory quota (section 2).** The repository holds 5 lesson records and no failure
   record, and the 140 earlier questions already draw on them. A new question may not share a gold source with an
   earlier set. So the 60's rate (5 of 60, which would be 6 of 80) is likely not writable.
   - **(A) Recommended:** 4 failure-memory questions, and if fewer can be written without sharing a gold source, the
     shortfall (at most 2) moves to `decision`. The quota check accepts only that shift.
   - (B) Keep 6, and let the writer stop and report if it cannot.
3. **The two session folders** (section 9): the writer's and the checker's settings, copies of the 60's with the
   additions listed there. Your operator creates them with the commands in section 9, rehearsed.
4. **The path-map line** declaring `memory-verdict-2` in both path maps (section 10), worded as the 60's line you
   approved. I add it once you approve, before the writer starts, and validate it.

- **What it blocks:** nothing now. The set is used only at the next decision point (the next testing and the trial),
  so it should be ready by then. The writer's work is about 2 to 3 hours, the cross-check about 1 hour (est., from the
  60's sessions scaled by 80/60).
- **Basis:** question 1 (memory: only a set nothing was tuned on gives a verdict, DEC-1074 (1)) and question 2 (a set
  that shares the tuning sets' gold or phrasing would misjudge memory).

## 1. What it is for
- **The verdict on memory at the next decision point.** The visible 40, the hidden 40 and the spent 60 are now tuning or
  diagnostic sets (DEC-1074 (1)). This set is measured once, at the next decision point, and never used to choose or
  tune anything.
- **Its value depends on staying unseen.** No method, label or setting may be fitted to it. So it is written without
  sight of any other question set, or of any retrieval result, or of the records about earlier sets' misses.

## 2. The size and the quotas: 80 questions
- **The target is unchanged: 95 % hit@5, with 85 % the floor, and it is to be achieved.** The set measures memory
  honestly against that target. It is never made easier or harder: each question follows the rubric, whatever the
  product is expected to score.
- **Why 80:** consistency is now judged within 5 points on sets of about 80 (DEC-1074 (4)). At 80 questions the
  standard error is about 5 points near 70 %, 4 near 85 % and 2.4 near 95 %, against 5.6 to 6 at 60.
- **R5 at 80:** each governing domain (code, decisions, tickets, the plan, the Contract and Charter) at least 8
  (10 %), and no subsystem above 20 (25 %).
- **The quotas** (R5 item 6, scaled from the 60's; exact counts, summing to 80):

  | `category` | Count | Notes |
  |---|---|---|
  | `decision` | 13 | at least 4 whose naive answer is superseded; takes failure-memory's shortfall, if any |
  | `contract` | 8 | the Contract and the Charter |
  | `plan` | 8 | |
  | `ticket` | 8 | tickets and the path map |
  | `exact-string` | 8 | exact strings and identifiers, with file and line |
  | `callers` | 8 | callers, callees and definitions |
  | `code-paraphrase` | 7 | a code fact asked in other words |
  | `kernel-template` | 7 | at least 4 on roles or skills |
  | `multi-file` | 6 | each needs two or more files |
  | `failure-memory` | 4 | each cites a lesson or failure record; at least 2 (option (A) of section 0) |
  | `history` | 2 | |
  | `nonexistent-id` | 1 | an id that exists nowhere; scored apart (DEC-1071 (5)) |

## 3. What the writer reads, and what it never reads
**Reads:**
- the repository at `w2/integrate`'s head (`/home/usain/Dynamic-Agentic-Engineering-OS`), read-only;
- the rubric `docs/research/memory-measure-audit/RUBRIC.md` (version 2), sections 1 and 2 in full. It is the rule
  for every question.

**Never reads** (the session's settings deny each, section 9):
- every other question set: the visible questions (`fixtures/evaluation/memory-retrieval/`), the hidden ones
  (`~/gov-os-eval/fixtures/evaluation/memory-retrieval/`), and the spent 60
  (`~/gov-os-eval/fixtures/evaluation/memory-verdict/`, its cross-check and retired copies included);
- the earlier writer's and checker's folders (`~/gov-os-writer`, `~/gov-os-checker`);
- any measure, search or run output (`~/gov-os-runs/`, `~/gov-os-eval/runs/`, `~/gov-os-eval/transcripts/`);
- the records about the measure and its misses: `docs/research/memory-measure-audit/` other than `RUBRIC.md`,
  `docs/audit/memory-measure-*`, `docs/audit/memory-verdict-*`, `docs/audit/memory-recall-diagnosis-*`,
  `docs/research/EXP-003/`, `docs/research/W2-61-baseline.md`, `docs/research/W2-88-memory-practice.md`,
  `governance/project/orchestration/packages/LIFT-1/D4B-*`, lens B's report
  (`docs/assessment/2026-10/B-memory-retrieval.md`), `tests/acceptance/W2-61*/`, all of `.gov-runtime/` and the
  worktrees under `~/gov-os-worktrees/`;
- the decision register's DEC-1066 to DEC-1074 for anything beyond the rubric's rules (they describe misses and the
  sets' profiles).

**Never uses:**
- `gov retrieve`, `gov context`, the measure, or any search of the product's index, to find a question or its answer.
  A set found through the product would favour what the product already finds. Gold is found by reading files, with
  `grep`, `git log` and `git show`.

## 4. How to write each question
1. **Write the question first, as an agent working here would ask it** (R4), in that agent's own words. Then find its
   governing source. Never start from a passage and phrase a question from its words.
2. **Apply every rubric item, R1 to R11,** to each question as it is written, especially:
   - R1, correct today from the governing source, never a superseded decision;
   - R2, the gold source in what memory searches by meaning, or the question marked as a keyword question;
   - R3, unambiguous;
   - R6, every source's span holds its answer, with a heading that is one whole line of the file, found once;
   - R8, never from the evaluation's own documents;
   - R11, no answer that changes with ordinary work.
3. **No question about the memory measure itself,** its sets or its results (they are the evaluation's own subject).
4. **The form:** each question is one file in the visible half's form (R7, R10).
   - Ids are `v01` to `v80`, one file each: `v01.yaml`.
   - Fields: `id`, `category`, `commit` (the head you read, 12 characters), `question`, `gold_answer`, `sources`.
   - Each source has `path`, `heading` (one whole line of the file) and `lines: [first, last]`. An entry is one piece
     of evidence; a list inside an entry is alternatives.
   - A first comment line says only "DEC-1074 (3), the verdict set of 80".
5. **No two questions ask the same fact** (R9), and none shares a gold source with an earlier set (the overlap check,
   section 6, enforces it).

## 5. Where it goes
- The folder is `~/gov-os-eval/fixtures/evaluation/memory-verdict-2/hidden/` (mode 700; your operator creates it).
  Create no copy anywhere else. It sits outside every git tree.
- Your session may write only there and in `memory-verdict-2/retired/` (the old copies the cross-check's fixes leave).
  Nothing is committed, and nothing is written inside the repository.

## 6. The checks, then "done"
Run these five, and send the owner only their output lines:
```
D=~/gov-os-eval/fixtures/evaluation/memory-verdict-2/hidden
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/d4b
R=/home/usain/Dynamic-Agentic-Engineering-OS
python3 -I $O/mset_anchors.py $D $R        # must print: path missing: 0; heading on no line: 0; heading on more than one line: 0
python3 $O/repin_gold.py $D $R             # must print: unresolved: 0
python3 -I $O/mset_overlap.py $D $R/fixtures/evaluation/memory-retrieval/visible \
  ~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden ~/gov-os-eval/fixtures/evaluation/memory-verdict/hidden
                                           # must print: overlapping a tuning question's gold source: 0
python3 -I $O/mset_quota.py $D             # must end: total: 80 of 80; PASS
```
- **`mset_anchors.py`** names, by this set's own ids, any source whose path is missing or whose heading is on no line
  or on more than one. `repin_gold.py` alone falls back to a source's lines when its heading is not found, so a
  mistyped heading passes it (found in this ACT's rehearsal).
- **`mset_overlap.py`** prints only this set's ids whose gold source is also a question's in one of the three earlier
  sets. Nothing about the other sets is printed. Each id it names is replaced by a question on a different source, and
  the check is run again until it prints 0.
- **`mset_quota.py`** prints the counts per category against section 2's table, and PASS (naming the failure-memory
  shift if one was used).
- **Then the independent cross-check (ACT-MSET-4).** Until it is done and its fixes are made, the set is not measured.

## 7. After the cross-check
- You make the fixes the checker's report and the owner's word call for, keeping each changed question's old copy as
  `retired/<id>-pre-xcheck.yaml`, never in `hidden/`.
- Then run section 6's five checks again, and send the owner their lines.

## 8. What the CTO does, and does not do
- **Does:**
  - adds the path-map line declaring the set `memory-verdict-2` in both path maps (section 10), with the owner's
    approval, and validates it on the empty folder;
  - runs `python3 -m gov.retrieval.measure memory-verdict-2 --sets-root ~/gov-os-eval --part hidden` only at the next
    decision point, with counts only shown, kept ranks stored as for the hidden half.
- **Does not:** read, list by content, or re-label any of the 80. A fault found by the measure (a source that no longer
  resolves) goes to the owner by id. It is fixed by the writer or the operator, never by the CTO.

## 9. The operator's steps: the two session folders (rehearsed)
**The settings are copies of the 60's sessions' (`~/gov-os-writer/.claude/settings.json`, `~/gov-os-checker/.claude/settings.json`), with these changes:**
- **Both:** the set's folder is now `memory-verdict-2`. New denials: the spent 60's folder; the earlier writer's and
  checker's folders; `.gov-runtime/`, the worktrees and the transcripts; the misses' records (`docs/audit/memory-verdict-*`,
  `docs/audit/memory-recall-diagnosis-*`, `packages/LIFT-1/D4B-*`, `docs/research/W2-88-memory-practice.md`,
  `docs/research/W2-61-baseline.md`, lens B's report, `tests/acceptance/W2-61*`); the measure and `ollama` commands.
- **The writer:** a write rule (its PreToolUse hook) lets it write only under `memory-verdict-2/hidden/` and
  `memory-verdict-2/retired/`. The 60's writer had no such rule; its brief alone kept it.
- **The checker:** as the 60's: it writes only `memory-verdict-2/XCHECK.md`, and git and repository edits are denied.

The files are in `governance/project/orchestration/packages/ACT-MSET-3/` (`writer-settings.json`, `writer-CLAUDE.md`,
`checker-settings.json`, `checker-CLAUDE.md`). **The commands** (one terminal, about 1 minute):
```
P=/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/packages/ACT-MSET-3
V2=~/gov-os-eval/fixtures/evaluation/memory-verdict-2
mkdir -p ~/gov-os-writer2/.claude ~/gov-os-checker2/.claude && mkdir -p -m 700 $V2/hidden $V2/retired && chmod 700 $V2
cp $P/writer-settings.json ~/gov-os-writer2/.claude/settings.json && cp $P/writer-CLAUDE.md ~/gov-os-writer2/CLAUDE.md
cp $P/checker-settings.json ~/gov-os-checker2/.claude/settings.json && cp $P/checker-CLAUDE.md ~/gov-os-checker2/CLAUDE.md
```
**Check:** `stat -c %a $V2 $V2/hidden` prints `700` twice; `cmp $P/writer-settings.json ~/gov-os-writer2/.claude/settings.json` is silent.

**Start the writer** from `~/gov-os-writer2` as the 60's was (`cd ~/gov-os-writer2 && claude`), after the CTO says
the path-map line is in. Then paste:

> Read `/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/packages/ACT-MSET-3.md` and follow
> it exactly. Write the questions only to `~/gov-os-eval/fixtures/evaluation/memory-verdict-2/hidden/`. Tell me only
> "done" and the output lines of section 6's checks.

**The rehearsal** (DEC-1057): the commands above with only the home folder substituted, then both write rules fed the
paths each session would write, then the checks on planted folders. Script and log:
`.gov-runtime/scratch/orchestrator/drafts/mset3/rehearse.sh` and `rehearsal-20261105-*.log`: **REHEARSAL PASS**, 23
checks. It found one fault, fixed before this hand-over: `repin_gold.py` passes a mistyped heading (it falls back to
the lines), so `mset_anchors.py` was added to section 6. **Not rehearsed:** the Claude sessions themselves (they are
yours to open).

## 10. The path-map line (both maps), worded as the 60's
In `~/gov-os-eval/governance/project/path-map.yaml` (the sets root, which the measure reads) and in
`governance/project/path-map.yaml` (the main tree), under `evaluation_sets:`, after `memory-verdict`:
```yaml
  # memory-verdict-2, the verdict set of 80 (DEC-1074 (3), ACT-MSET-3/4; the line approved by the owner, <date>):
  # written blind by a new writer outside the CTO's system; never used to choose or tune; measured by the CTO only
  # at the next decision point, counts only. Every role but the orchestrator is refused it.
  memory-verdict-2:
    visible: []
    hidden: ["fixtures/evaluation/memory-verdict-2/hidden/**"]
    measures:
      roles: [engineer, research, product-spec, independent-test-designer, independent-auditor]
```
- `memory-verdict`'s comment gains one line: "spent 2026-11-05 (one use, 40 of 59); a diagnostic set from DEC-1074 (2)".
  Its refused roles are unchanged.
- **Rehearsed:** the sets root's map with the line added parses, and `evaluation_sets` lists `memory-verdict-2` with
  its glob and roles.

## Rollback
Delete `~/gov-os-eval/fixtures/evaluation/memory-verdict-2/`, `~/gov-os-writer2` and `~/gov-os-checker2`, and
revert the path-map commit. Nothing else is written.
