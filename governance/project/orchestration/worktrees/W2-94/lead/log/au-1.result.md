task: W2-94 (DAEO-g87r): the narrow independent check of `check_gold.py` and `tests/acceptance/W2-94/` at head `69b1233aff3d`

sandbox check (Step 0, `EMG-d4b-launched.md`): (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-94` was refused (`OSError: [Errno 30] Read-only file system`), as it should be. (b) `git hash-object -w --stdin` worked (`1ae28402a109…`) and `git update-index --refresh` worked. Head confirmed: `git rev-parse HEAD` = `69b1233aff3dc13adfbdb4e6b3f8251ba6e170b9`.

ps check: `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing.

status: DONE. Overall judgement: **pass**. No finding blocks; six findings land as rows.

work_completed: I read the diff `b3106ac57..69b1233af` (check_gold.py and the eight files in the test folder), the writer brief (whole), the header of `release_visible.sh`, the CTO's `launch_rehearsal.sh`, and the guard's evaluation-set rule (`src/gov/guard/reads.py:232-243`). I ran the folder once through the heavy slot. I ran 8 probes on planted stand-ins and 2 mutants of the script, all in `$TMPDIR`.

files_changed: none. `git status --porcelain` is empty.

evidence: `pytest tests/acceptance/W2-94` gives 391 passed in 36.8 s through `heavy_slot.sh`. The slot tool waited for a slot and could not write its wait log (read-only file system); the run itself completed. Probe outputs are quoted in the findings below. Scratch use was 9.9 MB plus 68 KB, now removed.

tests: 391/0. The `-m/-k` exclusion left nothing out: no case in this folder starts a model.

discoveries: In the CTO's own launch rehearsal, the brief's draw line is written with a literal `k` (`launch_rehearsal.sh:62`: `1 code-location SEED+k=18 even …`). The script refuses that form (finding A).

risks: When the CTO runs the script on the real delivery, it may report `draw FAIL` falsely (finding A) or refuse the whole set (finding B). Either way it fails closed, never open.

lessons: A check of a delivery written blind should accept every form the brief's own example and wording allow, including a placeholder the brief leaves outside angle brackets.

proposed_decisions: none.

unresolved: none.

recommended_next_action: Fix A, and B as option (ii), when the ticket resumes (DEC-802), not as a round of their own: the test designer widens the draw-line pattern and adds one planted case for each. If the CTO runs the script before that fix, read `FAIL draw DRAW_LINE_BAD` together with `DRAW_LINES_MISMATCH` as a likely false failure, and check the draw by hand against `seed.txt`.

---

# Probe record: W2-94 (DAEO-g87r), the counts-only gold check and its acceptance cases

task: DAEO-g87r
decisions: [DEC-801, DEC-802, DEC-808, DEC-809, DEC-1010, DEC-1014, DEC-828, DEC-957, DEC-820, DEC-845]

**What I probed:** head `69b1233aff3d` of `w2/W2-94`, worktree `/home/usain/gov-os-worktrees/W2-94`; the change is commits `83beeb8f6311` and `ad1fd021f83a`.

**How:**
- I read the script against sections 5 to 7 of the writer brief, the header of `release_visible.sh` and the ticket's KPI lines.
- I ran the folder once.
- I ran 8 probes through the folder's own `w2_94_support.build` and `run_check` on stand-ins in `$TMPDIR`.
- I ran 2 mutants with `W2_94_CHECK_GOLD`.
- Nothing under `~/gov-os-eval`, `~/gov-os-runs`, a real `hidden` folder, the workbench or EXAMIN was opened.

**Classification:** 6 findings, none of them blocking. Five are in scope with ordinary work yes and consequence other (A, B, C, D, F). One is in scope with ordinary work no and consequence fails open (E). No round is proposed.

## Findings

**A (S1, S5): the script refuses a draw line written as the brief words it.**
- **What:** the brief gives the line as `<k> <category> SEED+k=<value> <parity> visible=<id> hidden=<id>` (`EXAMIN-writer.md:155-156`). Every placeholder there is in angle brackets except the `k` of `SEED+k=`. The brief's author wrote it literally in the launch rehearsal (`launch_rehearsal.sh:62`: `SEED+k=18`). The script accepts only digits after `SEED+` (`check_gold.py:122`).
- **What happened:** probe P1 is a good 20-question set with `SEED+k=` in every line. It printed `draw FAIL`, then `FAIL draw DRAW_LINE_BAD` and `FAIL draw DRAW_LINES_MISMATCH`, and exited 1.
- **What should happen:** the line is accepted, with k taken from the line's first field.
- Ordinary work: yes, because a writer following the brief's wording literally writes `SEED+k=`, as the brief's own author did.
- Consequence: other. It is a false failure that fails closed, and it stops the CTO getting a clean S1 pass and S5's second half.
- Scope: in.
- **What would reverse it:** the real `DRAW.txt` using digits after `SEED+`, which only the CTO can see; or the owner ruling that the literal form breaks the brief.

**B (S1, S4): an alternative written like the brief's example refuses the whole set.**
- **What:** in the brief's section 7 example, "alternative b" has `path` and `heading` but no `lines` (`EXAMIN-writer.md:170-173`). R6 (`:128-130`) asks for `lines` on every source. The script refuses a source without lines for the whole set (`check_gold.py:322-323`, refusal raised at `:616-617`).
- **What happened:** probe P2 printed only `REFUSED SOURCE_NO_LINES q07` and exited 2, with no counts for the other 19 questions.
- **What should happen:** either (i) keep the refusal as R6 asks, or (ii) treat an alternative without lines as one that does not hold, so its entry holds when another alternative does, and an entry left with none is reported by id as a `FAIL`.
- Ordinary work: yes, because a writer may copy the example's shape.
- Consequence: other (fails closed).
- Scope: in.
- **What would reverse it:** the owner reading R6 as overriding the example, so that a refusal is the intended result.

**C (S4): a heading copied without its indentation is reported as not found.**
- **What:** the script compares a heading with the file's lines after trimming only trailing spaces (`check_gold.py:398`).
- **What happened:** in probe P3 the heading was an indented code line (`    def …`) written without its indentation. The script printed `FAIL q07 HEADING_NOT_FOUND`. The control, P3b, kept the indentation and held.
- **What should happen:** this is arguable. R6 says "one whole line … the first line equal to it", which the script follows literally. Trimming leading spaces as well would make the check tolerant.
- Ordinary work: yes, because YAML authors routinely drop leading spaces.
- Consequence: other. It is a false failure reported by id, and the CTO can check it by hand.
- Scope: in.
- **What would reverse it:** the owner keeping R6's exact-line reading.

**D (S1): the draw's seed is never compared with the seed the launch recorded.**
- **What:** the script checks only that every line gives the same seed and follows the brief's rule (`check_gold.py:469-470`). It never sees `seed.txt` or the run record's seed.
- **What happened:** in probe P4, a draw made consistently from seed+1, with the files moved to match, printed `draw ok` and exited 0.
- **What should happen:** an optional `--seed <n>` argument, compared with the seed the lines give and printed as a code only.
- Ordinary work: yes, because a writer can misread or mis-add the seed. The split would still be stratified and balanced.
- Consequence: other. Only the seed's origin goes unchecked, and the KPI asks only that "the record holds the seed".
- Scope: in.
- **What would reverse it:** the CTO's launch record comparing `seed.txt` with `DRAW.txt` already.

**E (S4, F3): a short answer with no identifier and no long word holds on any span.**
- **What:** the rule's own limits (`check_gold.py:55-58`, `:254-256`, `:253`).
- **What happened:** in probe P6, the answer `Yes, it does.` cited against an unrelated span gave 20 of 20 hold. In probe P7, back-quoted words found only inside longer words also held.
- **What should happen:** these limits are stated in the docstring (`:65-74`). An answer with no token and no content word could at least be counted as "not judged" instead of "holds".
- Ordinary work: no, because it needs two mistakes together: an answer with no identifier and no content word of five letters or more (R5 asks for facts), and a wrong span.
- Consequence: fails open.
- Scope: in. It is a Wave 3 row.
- **What would reverse it:** a real answer of that shape, which only the CTO can see.

**F (S4, test coverage): one case does not test what its docstring says.**
- **What:** `test_s4_the_nonexistent_questions_hold_when_their_names_are_nowhere_at_the_commit` says the asked names are planted "in the scaffold commit and in the working tree". It plants them only in the untracked working tree (`extra_worktree`).
- **What happened:** a mutant that runs `git grep` at `HEAD` instead of the recorded commit passed all 38 S4 cases. A second mutant, reading the source files at `HEAD`, was caught by 3 cases.
- **What should happen:** plant one name in the scaffold commit as well.
- Ordinary work: yes, because a later edit to the script could make that change.
- Consequence: other. The scaffold commit only adds files, so a search at `HEAD` finds more names, and that fails closed.
- Scope: in.
- **What would reverse it:** a case that already plants a name in the scaffold commit.

## What I probed and found sound

- **Q1, failing open:**
  - Sources are read only through `git cat-file blob <COPY-HEAD commit>:<path>`. The commit comes from the committed `COPY-HEAD.txt` at the clone's `HEAD`, and an edited working-tree copy of that file is ignored (there is a test for it).
  - A path that is in the scaffold, a folder or a binary is reported. So is a span outside the file or a heading not in it.
  - A question's `commit` equal to the scaffold commit is refused.
  - Every output either prints "n of n hold" with an id per failure, or refuses. An internal exception exits 3, never 0.
  - Exit is 1 whenever any `FAIL` line is printed.
  - The count bounds (10 to 20), the 7 required fields, duplicate ids, the halves differing by at most one, each category in both halves, `visible/` byte-equal to `hidden/visible/`, and the record's sha256 values are all checked. The layout matches `release_visible.sh`.
- **Q2, output:** every `print` writes a fixed code or a `qNN` id taken from a checked file name. Usage errors, YAML errors and exceptions print codes only. stderr stayed empty and no planted word appeared in any probe run or in the 97 counts-only cases.
- **Q3, stand-ins only:** every set and clone is built under `tmp_path`, with HOME planted. The only real files read are the tree's path map and W2-61's close record. The folder passes 391/0.
- **Q4, F1:** the live hook is asked about each call as each of the 5 roles in `examin`'s `measures`: 20 routes in the tree (Read, Grep, Glob, `cat`, `grep -r`, `git log -p`/`--all -p`, `git grep`, `git show`, `git cat-file`) and 9 under the planted sets root. A Bash call that is allowed is then run for real and must find the planted word 0 times. One test proves the stand-in is in the repository's history; controls show that `visible/` and an ordinary `git log --oneline` stay open. `GOV_TICKET=W2-00` makes no difference, because `examin` measures by role (`reads.py:239-243`).
- **Q5, the README:** it maps S1, S4, F3, F1 and S5, plus the counts-only and fail-closed rows. It names S2, S3, F2 and the refusal of a second release as the CTO's and operator's records. Its count of 97 counts-only cases is correct.

```verdict
{"kpis": [
 {"kpi": "S1", "verdict": "pass", "findings": [
   {"id": "A", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "B", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "D", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S2", "verdict": "pass", "findings": []},
 {"kpi": "S3", "verdict": "pass", "findings": []},
 {"kpi": "S4", "verdict": "pass", "findings": [
   {"id": "B", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "C", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "E", "scope": "in", "ordinary_work": "no", "consequence": "fails open"},
   {"id": "F", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S5", "verdict": "pass", "findings": [
   {"id": "A", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "F1", "verdict": "pass", "findings": []},
 {"kpi": "F3", "verdict": "pass", "findings": [
   {"id": "E", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}
]}
```

Overall: **pass**.