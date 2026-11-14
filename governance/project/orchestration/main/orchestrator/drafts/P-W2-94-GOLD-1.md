# P-W2-94-GOLD-1: W2-94's gold check fails 3 questions and the draw's form; nothing in the set changes without your word

**(1) Context.** W2-94 (EXAMIN's question set) returned DONE at cfbcd75ab386. Your operator ran its `check_gold.py` on the
real delivery and got 17 of 20, draw FAIL, release ok, exit 1. I diagnosed from the check's code, the brief (§5, §6) and
the two **visible** failures. I read no hidden file.

**(2) What ANSWER_NOT_IN_SPANS tests** (`check_gold.py:48-58`, `answer_in` at :246).
- **Rule 2a:** it takes the gold answer's *tokens*: back-quoted pieces and any "identifier-shaped" word. That means a
  word with `_`, `/` or `::`, camelCase, letters mixed with digits, **a hyphenated word with a digit**, or a dotted file
  name. Every token must occur **literally and case-sensitively** in the cited spans, or be the name of a cited source.
- **Rule 2b:** an answer with no token passes when a third of its long words occur by stem.
- So the check is literal only for identifier-like words. Plain prose words are free, but any word the regex takes for
  an identifier must be copied exactly from the span.

**(3) The two visible failures: both gold answers are right; the check is too literal.**
- **q01** (code-location): the answer names `spec/2-PLAN/VIEWS.md`. Its span (`gen_views.py` 179-196) writes that file
  as `os.path.join("spec/2-PLAN", "VIEWS.md")` (line 196). The literal string first appears at line 197, one line past
  the span, and in the docstring (lines 10 and 13). The token's parts occur in order inside the span.
- **q12** (governance-rule): the answer says each heading is "a level-2 heading". The span (SKILL.md 78-81) shows them
  as `## What was done` and so on. "level-2" is the writer's own word for `##`, as §5 item 5 requires. The check reads
  it as an id like `DEC-051` and finds no `level-2` in the span.
- **q02** (hidden, the same category as q01): not diagnosed. The command below gives its token class without content.

**(4) The draw.**
- **The form matches.** The check's line form (`check_gold.py:122`) is the brief's §6 form, with one strictness: `k` in
  `SEED+k=` must be the digit, which is the natural reading.
- **The split itself is right.** The released visible ids (q01, q04, q05, q08, q09, q12, q13, q16, q17, q20) alternate
  exactly as §6's parity rule gives for one seed.
- **One line fails the form (DRAW_LINE_BAD).** DRAW_LINES_MISMATCH follows from that same line: its category then has
  no parsed line. If the writer had read `SEED+k` literally, all ten lines would fail, so this one line has another
  defect (a spacing, a tab, a field). The command below shows its shape.

**(5) Your operator's two commands** (counts, classes, ids, categories and parity only; never a question, an answer, a
token's text, a value or the seed; safe to paste here):
```
cd /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-94-gold && env -u GOV_ROLE -u GOV_TICKET python3 -I gold_diag.py draw --sets-root /home/usain/gov-os-eval; echo "exit=$?"
cd /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-94-gold && env -u GOV_ROLE -u GOV_TICKET python3 -I gold_diag.py tokens --sets-root /home/usain/gov-os-eval --copy /home/usain/gov-os-runs/W2-94/examin --check /home/usain/gov-os-worktrees/W2-94/fixtures/evaluation/examin/check_gold.py --id q02; echo "exit=$?"
```
- **The draw command** prints one line per DRAW.txt line. A good line shows `k`, category, parity and the two ids, never
  the value. A bad line shows its first mismatching field and its shape, with letters as `a` and digits as `9`.
- **The tokens command** gives each missing token's class (path, hyphen-digit, …), its length, and whether it is found
  case-insensitively, as path parts in order, or with "-" read as a space.
- Tried on visible q01 and q12, it gives `class=path … parts-in-order=True` and `class=hyphen-digit`.

**(6) Options.**
- **For ANSWER_NOT_IN_SPANS:**
  - **(a) Fix the check, set unchanged.** In W2-94's own `check_gold.py`, by a W2-94 run: a test designer's cases, then
    the engineer.
    - A hyphen-digit word counts as an identifier only when it is id-shaped (an upper-case prefix: `DEC-051`, `W2-94`),
      not `level-2` or `top-3`.
    - A path token is held when its parts occur in order in the spans (code that joins a path).
    - Then your operator re-runs the check. About 1.5 h with a narrow check.
    - Risk: a wrong span that happens to hold a path's parts in order would pass. Small.
  - **(b) Change the set.** Extend q01's two spans to line 197 and re-word q12's answer to back-quote `##`. These are
    visible files already released and confirmed (DEC-1152), so this means a re-release and a new release record. q02,
    if it needs a change, goes through the walled writer. About 1 to 2 h, plus your operator's steps.
  - **(c) Hand-confirmed exceptions:** the check reads a list of ids you confirmed. Fast, but it weakens the check for
    future sets.
- **For the draw:**
  - **(d)** If the shape shows a pure form defect (a spacing, a tab, a stray character) and the values agree with the
    visible ids, your operator corrects that one line of DRAW.txt. DRAW.txt is the draw's record, not a question. Add a
    note line to the release record, then re-run.
  - **(e)** If it shows a real disagreement (an id or a parity), the draw goes back to the walled writer.

**(7) Recommendation: (a) and (d)**, subject to the two outputs. Confidence: medium until q02's class and the draw's
shape are in; high for q01 and q12.
- The brief requires the writer's own words, so the check must accept them. The set's content is right.
- If q02's class is not path or hyphen-digit, it is a real defect in a hidden question: a separate package to you.
- A row, not a change now: §6 should read `SEED+<k>=` to remove the literal reading.

**(8) What it blocks.** W2-94's land and close, which feed W2-27's EXAMIN work. Not W2-27's start.

Your line: `W2-94 GOLD (a)+(d)` after the two outputs (or name others).
