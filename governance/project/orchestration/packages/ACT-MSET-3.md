# ACT-MSET-3: the new verdict set: 80 questions, written fresh and blind by the 60's writer (DEC-1074 (3), DEC-1076)

- **For:** the owner's operator (section 9), then **the writer session of the 60** (`~/gov-os-writer`), outside the
  CTO's system, resumed by the owner with `claude --continue` so its new settings load: a plain terminal, not under the
  guard, not launched by `gov launch`, with no access to the CTO's session or its agents.
- **Nothing about these questions reaches the CTO's session.** The writer reports to the owner only "done" and the
  count lines of section 6.
- **By:** the CTO, session `812bc5ce`, 2026-11-05, from ACT-MSET-1 and ACT-MSET-2 (the 60's briefs).
- **The cross-check** is ACT-MSET-4, in the same package, for the checker session of the 60 (`~/gov-os-checker`).

## 0. Decided (DEC-1075, DEC-1076)
- This brief, ACT-MSET-4, the folders' settings and the path-map line approved (DEC-1075). The line is in both path
  maps (`efcd91a2`).
- The failure-memory quota is option (A): 4 questions, a shortfall of at most 2 moved to `decision` (DEC-1075 (2)).
- The 80 are written and cross-checked by the same writer and checker sessions as the 60 (DEC-1076, amending
  DEC-1074 (3)); their folders keep their names and gain the settings of section 9.
- Basis: question 1 (memory: only a set nothing was tuned on gives a verdict) and question 2 (a set that shares the
  tuning sets' gold misjudges memory).

## 1. What it is for
- **The verdict on memory at the next decision point.** The visible 40, the hidden 40 and the spent 60 are now tuning or
  diagnostic sets (DEC-1074 (1)). This set is measured once, at the next decision point, and never used to choose or
  tune anything.
- **Its value depends on staying unseen.** No method, label or setting may be fitted to it. So it is written without
  reading any other question set, any retrieval result, or the records about earlier sets' misses.

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
  (`~/gov-os-eval/fixtures/evaluation/memory-retrieval/`), and the 60 (`~/gov-os-eval/fixtures/evaluation/memory-verdict/`,
  its cross-check and retired copies included);
- the checker's folder (`~/gov-os-checker`);
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
   - **Vary the phrasing from your earlier work.** Ask each question as a different working role would ask it: an
     engineer, a test designer, a lead, an auditor, the owner. Use plain working words, and never echo a source's
     wording.
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
- **The checker also lists, per question, every other place that states the same answer** (ACT-MSET-4 section 3,
  item 6). Add each as an alternative of its entry by the rubric: only where it holds that whole piece on its own
  (R7 item 1) and is the governing source or a faithful restatement of it (R1 item 3); a place that holds only part
  of it, or is a report, is left out. Note in your done line how many you added and how many you left out.
- Then run section 6's five checks again, and send the owner their lines.

## 8. What the CTO does, and does not do
- **Does:**
  - adds the path-map line declaring the set `memory-verdict-2` in both path maps (section 10), with the owner's
    approval, and validates it on the empty folder;
  - runs `python3 -m gov.retrieval.measure memory-verdict-2 --sets-root ~/gov-os-eval --part hidden` only at the next
    decision point, with counts only shown, kept ranks stored as for the hidden half.
- **Does not:** read, list by content, or re-label any of the 80. A fault found by the measure (a source that no longer
  resolves) goes to the owner by id. It is fixed by the writer or the operator, never by the CTO.

## 9. The operator's steps: the same two sessions' folders (rehearsed)
**Each session keeps its folder (`~/gov-os-writer`, `~/gov-os-checker`) and its conversation; its settings and its
`CLAUDE.md` are replaced, the old ones kept beside them.** The changes against the 60's settings:
- **Both:** the set's folder is now `memory-verdict-2` (its added directory). New denials: the 60's folder; the other
  session's folder (never its own); `.gov-runtime/`, the worktrees and the transcripts; the misses' records
  (`docs/audit/memory-verdict-*`, `docs/audit/memory-recall-diagnosis-*`, `packages/LIFT-1/D4B-*`,
  `docs/research/W2-88-memory-practice.md`, `docs/research/W2-61-baseline.md`, lens B's report,
  `tests/acceptance/W2-61*`); the measure and `ollama` commands.
- **The writer:** a write rule (its PreToolUse hook) lets it write only under `memory-verdict-2/hidden/` and
  `memory-verdict-2/retired/`.
- **The checker:** its write rule now names `memory-verdict-2/XCHECK.md` only; its git and repository-edit denials stay.

The files are in `governance/project/orchestration/packages/ACT-MSET-3/` (`writer-settings.json`, `writer-CLAUDE.md`,
`checker-settings.json`, `checker-CLAUDE.md`). **The commands** (one terminal, about 1 minute, with neither session
running):
```
P=/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/packages/ACT-MSET-3
V2=~/gov-os-eval/fixtures/evaluation/memory-verdict-2
for s in writer checker; do
  cp -p ~/gov-os-$s/.claude/settings.json ~/gov-os-$s/.claude/settings.json.pre-act-mset-3
  cp -p ~/gov-os-$s/CLAUDE.md ~/gov-os-$s/CLAUDE.md.pre-act-mset-3
  cp $P/$s-settings.json ~/gov-os-$s/.claude/settings.json && cp $P/$s-CLAUDE.md ~/gov-os-$s/CLAUDE.md
done
mkdir -p -m 700 $V2/hidden $V2/retired && chmod 700 $V2
```
**Check:** `stat -c %a $V2 $V2/hidden` prints `700` twice; `cmp $P/writer-settings.json ~/gov-os-writer/.claude/settings.json`
and `cmp $P/checker-settings.json ~/gov-os-checker/.claude/settings.json` are silent.

**Resume the writer** with `cd ~/gov-os-writer && claude --continue`, so the new settings load. Then paste:

> Read `/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/packages/ACT-MSET-3.md` and follow
> it exactly. It is a new task: the 60 are finished. Write the questions only to
> `~/gov-os-eval/fixtures/evaluation/memory-verdict-2/hidden/`. Tell me only "done" and the output lines of section 6's
> checks.

**The rehearsal** (DEC-1057): the two sessions' current files copied into a scratch home, the commands above run there
with only the home folder substituted, then both write rules fed the paths each session would write, the denials
checked (neither session denied its own folder), and the checks on planted folders. Script and log:
`.gov-runtime/scratch/orchestrator/drafts/mset3/rehearse.sh` and `rehearsal-20261105-*.log`: **REHEARSAL PASS**, 24
checks. An earlier run found one fault, fixed: `repin_gold.py` passes a mistyped heading (it falls back to the lines),
so `mset_anchors.py` was added to section 6. **Not rehearsed:** the Claude sessions themselves (yours to resume).

## 10. The path-map line (both maps): in (`efcd91a2`)
In `~/gov-os-eval/governance/project/path-map.yaml` (the sets root, which the measure reads; the old file kept as
`path-map.yaml.pre-dec1075`) and in `governance/project/path-map.yaml` (the main tree), under `evaluation_sets:`, after
`memory-verdict`, which gained "Spent 2026-11-05 (one use, 40 of 59); a diagnostic set from DEC-1074 (2)":
```yaml
  memory-verdict-2:
    visible: []
    hidden: ["fixtures/evaluation/memory-verdict-2/hidden/**"]
    measures:
      roles: [engineer, research, product-spec, independent-test-designer, independent-auditor]
```
Both maps validated (`check_sets`), and the guard check passes.

## Rollback
For each of `writer` and `checker`: `mv ~/gov-os-$s/.claude/settings.json.pre-act-mset-3 ~/gov-os-$s/.claude/settings.json`
and `mv ~/gov-os-$s/CLAUDE.md.pre-act-mset-3 ~/gov-os-$s/CLAUDE.md`. Delete
`~/gov-os-eval/fixtures/evaluation/memory-verdict-2/`. Revert the path-map commit. Nothing else is written.
