# ACT-MSET-1: the new measurement set: 60 questions, written fresh and blind (DEC-1070 (4))

For a **new session the owner opens, outside the CTO's system**, used only for this: a plain terminal, not under the
guard, not launched by `gov launch`, with no access to the CTO's session or its agents. **Nothing about these
questions reaches the CTO's session**: the writer reports to the owner only "done" and the three count lines in
section 6.

## 1. What it is for
- **The verdict on memory.** The visible 40 tune and choose; the hidden 40 check the tuning. This set is measured
  only at decision points (before a re-pin), and never used to choose or tune anything.
- **Its value depends on staying unseen.** No method, label or setting may be fitted to it. So it is written without
  sight of the other questions or of any retrieval result.

## 2. The size: 60, as the owner decided (the owner's minimum was 40)
- **The target is unchanged: 95 % hit@5, with 85 % the floor, and it is to be achieved.** The set is written to measure
  memory honestly against that target. It is never made easier or harder to reach it: each question follows the
  rubric, whatever the product is expected to score.
- **The precision:** at a pass rate near 75 %, 60 questions give a standard error of about 5.6 points, against 6.8 at
  40. That's enough to tell the hidden half's 72 % from the visible half's 90 %. The 75 % is only the assumption
  behind this precision figure, not an expectation. Near the target the error is smaller: about 2.8 points at 95 %.
- It gives each governing domain at least 6 questions (10 %), so a per-domain figure means something.
- **The quotas** (R5 item 6, scaled to 60; exact counts, summing to 60):

  | `category` | Count | Notes |
  |---|---|---|
  | `decision` | 8 | at least 3 whose naive answer is superseded |
  | `contract` | 6 | the Contract and the Charter |
  | `plan` | 6 | |
  | `ticket` | 6 | tickets and the path map |
  | `exact-string` | 6 | exact strings and identifiers, with file and line |
  | `callers` | 6 | callers, callees and definitions |
  | `code-paraphrase` | 5 | a code fact asked in other words |
  | `kernel-template` | 5 | at least 3 on roles or skills |
  | `multi-file` | 5 | each needs two or more files |
  | `failure-memory` | 5 | each cites a lesson or failure record |
  | `history` | 1 | |
  | `nonexistent-id` | 1 | an id that exists nowhere |

- **R5 at 60:** each governing domain (code, decisions, tickets, the plan, the Contract and Charter) at least 6, and
  no subsystem above 15 (25 %).

## 3. What the writer reads, and what it never reads
**Reads:**
- the repository at `w2/integrate`'s head (`/home/usain/Dynamic-Agentic-Engineering-OS`), read-only;
- the rubric `docs/research/memory-measure-audit/RUBRIC.md` (version 2), sections 1 and 2 in full. It is the rule
  for every question.

**Never reads:**
- the visible questions (`fixtures/evaluation/memory-retrieval/`) or the hidden ones
  (`~/gov-os-eval/fixtures/evaluation/memory-retrieval/`);
- any measure, search or run output (`~/gov-os-runs/`, `~/gov-os-eval/runs/`);
- the audit and research records about the measure: `docs/research/memory-measure-audit/` other than `RUBRIC.md`,
  `docs/audit/memory-measure-*`, `docs/research/EXP-003/`, and the `drafts/d4b/` folder;
- the decision register's DEC-1066 to DEC-1070 for anything beyond the rubric's rules (they name misses).

**Never uses:**
- `gov retrieve`, `gov context` or any search of the product's index, to find a question or its answer. A set found
  through the product would favour what the product already finds. Gold is found by reading files, with `grep`,
  `git log` and `git show`.

## 4. How to write each question
1. **Write the question first, as an agent working here would ask it** (R4). Then find its governing source. Never
   start from a passage and phrase a question from its words (R4 forbids phrasing taken from the answer).
2. **Apply every rubric item, R1 to R11,** to each question as it is written, especially:
   - R1, correct today from the governing source, never a superseded decision;
   - R2, the gold source in what memory searches by meaning, or the question marked as a keyword question;
   - R3, unambiguous;
   - R8, never from the evaluation's own documents;
   - R11, no answer that changes with ordinary work.
3. **The form:** each question is one file in the visible half's form (R7, R10).
   - Ids are `m01` to `m60`, one file each: `m01.yaml`.
   - Fields: `id`, `category`, `commit` (the head you read, 12 characters), `question`, `gold_answer`, `sources`.
   - Each source has `path`, `heading` (one whole line of the file) and `lines: [first, last]`. An entry is one piece
     of evidence; a list inside an entry is alternatives.
   - A first comment line says only "DEC-1070 (4), the measurement set".
4. **No two questions ask the same fact** (R9).

## 5. Where it goes
- The folder is `~/gov-os-eval/fixtures/evaluation/memory-verdict/hidden/`. Create it with mode 700, and create no
  copy anywhere else. It sits outside every git tree.
- Nothing is committed, and nothing is written inside the repository.

## 6. The checks, then "done"
Run these three, and send the owner only their output lines:
```
D=~/gov-os-eval/fixtures/evaluation/memory-verdict/hidden
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/d4b
python3 $O/repin_gold.py $D /home/usain/Dynamic-Agentic-Engineering-OS        # must print unresolved: 0
python3 -I $O/mset_overlap.py $D /home/usain/Dynamic-Agentic-Engineering-OS/fixtures/evaluation/memory-retrieval/visible \
  ~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden                   # must print overlapping ...: 0
python3 -c "import yaml,glob,collections; print(collections.Counter(yaml.safe_load(open(f))['category'] for f in glob.glob('$D/*.yaml')))"
```
- **`mset_overlap.py`** prints only this set's ids whose gold source is also a tuning question's. Nothing about the
  other questions is printed. Each id it names is replaced by a question on a different source, and the check is
  run again until it prints 0.
- **Then an independent cross-check**, as for the hidden 16: a second fresh session the owner opens applies the rubric
  blind to the 60 and reports ids and reasons only; the fixes are made by the writer. Until then, the set is not
  measured.

## 7. What the CTO does, and does not do
- **Does:**
  - prepares the measure's side: one path-map line declaring the set `memory-verdict`, its hidden glob covering the
    folder, with the owner's approval;
  - runs `python3 -m gov.retrieval.measure memory-verdict --sets-root ~/gov-os-eval --part hidden` only at a decision
    point, with counts only shown, kept ranks stored as for the hidden half.
- **Does not:** read, list by content, or re-label any of the 60. A fault found by the measure (a source that no
  longer resolves) goes to the owner by id. It is fixed by the writer or the operator, never by the CTO.

## Rollback
Delete the folder. Nothing else was written.
