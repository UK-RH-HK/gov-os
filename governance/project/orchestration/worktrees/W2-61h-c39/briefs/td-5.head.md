# Independent test designer: W2-61h (DAEO-h2k3) — N2 (b): a rewritten heading-cited section is listed; an entry listed once (DEC-1180 (1), (4))

You are a fresh independent test designer. Headless: only your last message is read.

## Where you work
- Your tree (write here only): /home/usain/gov-os-worktrees/W2-61h-c39-tests, branch w2/W2-61h-c39-tests (at w2/integrate 494d5c933).
- Files you may change: `tests/acceptance/W2-61h/w2_61h_support.py` and `tests/acceptance/W2-61h/README.md`; and
  `tests/acceptance/W2-61h/test_w2_61h_visible_new.py` / `tests/acceptance/W2-61h/test_w2_61h_hidden_form.py` **only
  where the change needs them** (e.g. to add the planted proofs). Nothing else (not `test_w2_61h_families.py`, not
  `tests/optin-lifted*.txt`, not the question files).
- Scratch: the sandbox's own `$TMPDIR` for every planted repository and planted sets root.

## The decision you implement
DEC-1180 (1) and (4) (`docs/DECISION_REGISTER.md`, grep `### DEC-1180`, read items (1) and (4)); the ticket's S4 and
F3 lines (`.tickets/DAEO-h2k3.md` `kpis:`, the 4th success line and the 4th failure line) and its last two paragraphs
("Reopened 2026-11-14" and "N2 (b), 2026-11-14"). The previous revision (DEC-1178 (1)) is the current
`judge_sources()` in `tests/acceptance/W2-61h/w2_61h_support.py:219-279` and the README's S4 "changed rule" row.

**Why:** the last revision counted as "changed" only what the measure cannot find again. So a heading-cited section
whose text was rewritten, under a heading still found at HEAD, was not listed (`w2_61h_support.py:263-264`: a heading
found at HEAD returns early). The owner read "lines changed" as (b): such a section **is** listed. A narrow check also
found row N1: when two alternatives of one entry both changed, that entry was listed twice (`[1, 1]`).

## The revision (S4 and F3 as they stand, plus N2 (b))
1. **A heading-cited source:** compare the cited section's text at the source's own commit and at HEAD. The section
   runs from the heading line to the next heading of the same or a higher level, or to the end of the file (the
   measure's span rule, `span_of`, at each commit). If the text differs, the entry is **listed** by question id and
   entry number only, even though its heading is still found at HEAD. Never failed; never blocks a close. If the text
   is the same (wherever in the file the section now sits), it is not listed. State in the README your call for a
   heading that is not a `#` heading (where `span_of` spans the stated width), and what "text differs" means
   (exact line equality, or trailing whitespace stripped; say which and why).
2. **An entry is listed once** (row N1, DEC-1180 (4)): two or more changed alternatives of the same entry give one
   `"<file> entry <n>"` line.
3. **Everything else unchanged:** a block moved unchanged is no fault and not listed; a changed lines-cited span is
   listed; a heading gone at HEAD with no lines is listed; a path gone at HEAD is listed; a source that does not hold
   its answer at its own commit is red; messages name file names and entry numbers only (`_fail`, untraced). Keep
   every existing test function's name (the ticket's KPI lines and packages cite them; `tests/optin-lifted-breadth.txt`
   holds `rep: tests/acceptance/W2-61h/test_w2_61h_visible_new.py`, so in the full run **only the first row of a
   parametrised function runs**: make each proof a single non-parametrised case, or extend the existing planted case).
   Update the list's message and the docstrings only where they become false (it now names "block(s) or section(s)").

## Prove it on planted data only
- **In the visible module's always-run planted case** (`test_s4_f3_judges_each_source_at_its_own_commit_on_planted_data`,
  or a new non-parametrised case beside it, judged with the same `judge_all`/`judge_sources` the real cases use), add:
  - **(e)** a heading-cited section rewritten under an unchanged heading: passes and **is listed**;
  - **(f)** a heading-cited section that moved unchanged (e.g. lines inserted above it): passes and **is not listed**;
  - **(g)** an entry with two alternatives that both changed: **listed once**.
  - **(a)-(d) keep their outcomes**: (a) moved unchanged, passes, not listed; (b) lines changed, passes, listed;
    (c) never held its answer at its own commit, red with file name and entry number only (assert no planted question,
    answer, path or span text in any message); (d) control, passes, not listed.
  - Optional, if cheap: a planted red for q21-q24's anchor missing from its span at its own commit (row N3 of the last
    check). If you skip it, say why in one line of your return.
- **The hidden-form module against a throwaway sets root under `$TMPDIR`** (planted questions in the module's form,
  citing real commits and real non-evaluation files of this repository; never anything from `/home/usain/gov-os-eval`):
  show its S4 case gives (e) listed, (f) not listed, (g) one line, and (a)-(d) as before. Report the S4 case's outcomes
  only (other hidden cases may be red on a synthetic plant for their own reasons). Also show the module still skips
  without `GOV_EVAL_SETS_ROOT` and under `GOV_ROLE=engineer`.
- **The visible module at HEAD** (q21-q24 against the repository) must pass in an ordinary run. If the revision now
  lists real visible entries, report them (file and entry number) — they pass, listed.

## Check your change
Every pytest through heavy_slot.sh (a resource gate's refusal is a wait, not a refusal):
```
mkdir -p /home/usain/gov-os-worktrees/W2-61h-c39-tests/.gov-runtime/scratch/empty-home
cd /home/usain/gov-os-worktrees/W2-61h-c39-tests && bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-61h-c39-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-61h-c39-tests/src python3 -m pytest tests/acceptance/W2-61h -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
For the throwaway sets root run, prefix `env -u GOV_ROLE -u GOV_TICKET GOV_EVAL_SETS_ROOT=<your $TMPDIR root>`, add
`-rA`, and run only `tests/acceptance/W2-61h/test_w2_61h_hidden_form.py`. Report counts and outcomes only.

## README
Update the S4 "changed rule" row and the S4/F3 rows (the section rule, listed once), and add a dated section
"DEC-1180 (1), (4): N2 (b) and N1" recording the planted proofs (e), (f), (g) and (a)-(d) by outcome only. Keep the
walled command's form (`env -u GOV_ROLE -u GOV_TICKET GOV_EVAL_SETS_ROOT=<root> python3 -m pytest
tests/acceptance/W2-61h/test_w2_61h_hidden_form.py -p no:cacheprovider <flags>`); correct any older sentence the
revision makes false (e.g. "a heading still found at HEAD ... is not listed").

## Commit
Your paths only; trailers in one final paragraph (no blank line between them):
```
git -C /home/usain/gov-os-worktrees/W2-61h-c39-tests commit -m "<subject>" --trailer "Rewrite-Reason: DEC-1180 (1)" --trailer "Task: DAEO-h2k3" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-828, DEC-820, DEC-1084, DEC-1178" -- <the files you changed>
```
Check with `git -C /home/usain/gov-os-worktrees/W2-61h-c39-tests log -1 --format='%(trailers)'` that all four read as
trailers. (DEC-1180 is not in the ticket's `sources:`; it stays in `Rewrite-Reason:` only.)

## Rules
- **Never open `/home/usain/gov-os-eval` or any hidden, retired-hidden or memory-verdict folder; read no hidden content.**
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around a refusal.
- No hidden question, answer or gold path in any commit message, file, log or your return.
- Searching: Read and Grep only (no `gov retrieve`, no `gov context` in the sandbox); search again once, in other words.
- You may read `src/gov/retrieval/measure.py` and `tests/acceptance/W2-134/` for the span and re-anchor rules.
- If an API error ends you mid-way, your commits and files are your checkpoint: the lead relaunches you once.

## Return (your last message; nothing else is read)
Twelve labelled lines, "none" where nothing: task / status (DONE or PACKAGES) / work_completed / files_changed /
evidence / tests (the visible run's counts; the planted case's outcomes (a)-(g); the throwaway-root S4 outcomes; the
skip checks; any real visible entries now listed) / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then `commits: <hash12> <subject>` and `guard_refusals: none | - <form> | <reason>`.
PACKAGES: each as question, options with cost, recommendation, confidence, what it blocks.

## The ticket's context packet (gov context DAEO-h2k3 --role independent-test-designer --root W2-00-store --budget 36000)

```
