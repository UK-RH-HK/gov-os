Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief eng-3: engineer for DAEO-0cd2 (W2-187), fix batch 2, profile FULL, class C2

You are a fresh engineer for ticket DAEO-0cd2 (W2-187: the memory audit's standing hidden set and its weekly maintenance
pass). The code is built and its acceptance suite passes but for items outside your part. Since then the ticket was
amended twice: under the owner's N2 (b) (DEC-1180 (1)), S10 (6) and the Interface's I10 item 6; and under DEC-1182 (2),
S12 and F7 with their interface I13 (the CTO's, at the ticket's end). You build those two and nothing else. The Interface is binding; a case you cannot meet within it or your allowed paths comes back as a package
(question, options with cost, recommendation, confidence, what it blocks).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-187 |
| branch | w2/W2-187 (head f4fdc7fa1; `w2/integrate` merged, so the ticket below is the amended one) |
| your allowed paths | src/gov/memaudit/**, src/gov/adopt/memory_sets.py, governance/project/orchestration/tools/memaudit_cron.sh, tests/unit/memaudit/**, tests/unit/adopt/test_w2_187*, docs/changes/W2-187-evidence.md |
| the ticket (read S10, S11, S12, F7, the Interface's I10 item 6, I11, the "Amended 2026-11-14" paragraphs and I13 at the end) | /home/usain/gov-os-worktrees/W2-187/.tickets/DAEO-0cd2.md |
| the maintenance pass | src/gov/memaudit/maintain.py (item 6), tests/unit/memaudit/test_maintain.py |
| the measure's heading span and the block at a commit (reuse; `src/gov/retrieval/measure.py` is not in your paths, never edit it) | src/gov/retrieval/measure.py (`_span`, `_HEADING`, `_lines_at`, the module docstring's "How a source is matched") |
| how W2-61h's tests planted the same rule (read for the rule only) | tests/acceptance/W2-61h/w2_61h_support.py |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox. Never open the
real sets root (`~/gov-os-eval`), the real runs folder (`~/gov-os-runs`), any hidden half or memory-verdict folder;
never print a question id, question, answer, path or span of any hidden set (DEC-820).

## What to build (I10 item 6 as amended)
Item 6 lists, per set the sets root's path map declares (standing sets left out, U2), the entries `matcher.questions`
reports `unresolved`. With N2 (b) it also lists a **heading-cited source whose section text differs between the source's
own commit (its `commit`, else the question's) and the head**, though its heading is still found. The section is from
its heading line to the line before the next heading of the same or a higher level, or the end of the file, as measure's
docstring and `_span` define it. Compare the section's lines at the commit (`git show <commit>:<path>` through
measure's `_lines_at`) with the section's lines at the head. A source with no commit is never listed by this rule. An
entry is listed once, even when both rules list it. The request `REANCHOR-<week>.json` keeps its form
(`{"week", "audit_commit", "set", "changed": [{"id", "entry"}], "count"}`), and no question, answer or path text goes
anywhere. A block moved unchanged is still not listed. `maintain` stays exit 0 always; a fault reading one source
skips that source, never the pass.

The test designer is adding the acceptance case for this in parallel. Write your own unit cases in
`tests/unit/memaudit/test_maintain.py`: a rewritten section listed; an unchanged section not listed; a section at the
end of the file; a `###` section ending at the next `##`; listed once when both rules hit; no commit, not listed.

## What to build (S12, F7: I13 word for word is the contract)
- `src/gov/memaudit/push.py` and the subcommand `python3 -m gov.memaudit push --sets-root R [--repo D] [--gitleaks EXE]`:
  the declaration from `GOV_MEMAUDIT_PUSH="<remote> <branch>"` (absent or empty: no push); the scan exactly as I13 gives
  it (`gitleaks detect --source <repo> --no-banner --redact --report-format json --report-path <a 0600 temporary file
  outside the repository>`, counted then deleted; exit 0 clean; exit 1 with entries `findings <k>`; any other exit, the
  timeout `GOV_MEMAUDIT_SCAN_TIMEOUT_S` (default 600) or no binary `scan failed <reason word>`; the binary `--gitleaks`,
  else `$GOV_MEMAUDIT_GITLEAKS`, else `gitleaks` on PATH); `git push <remote> <branch>` only on a clean scan; the five
  output lines and exits of I13; git's own output in a 0600 file in the key folder, never printed. The same PUSH line
  appended as the last line of the cycle's latest `DIGEST.txt` in the key folder. `say` the only printer; no finding's
  text (a secret, a match, a line) anywhere. This module's scan call is the only gitleaks call in `gov.memaudit` and the
  wrapper.
- `memaudit_cron.sh`: `push` as the last step, after the audit steps that ran, only when a standing or fresh step started
  that cycle; one more `cron.log` line with the six keys unchanged and the step `push`; the wrapper's exit stays the last
  started step's. Never in `maintain`.
- `memory_sets.walls_act`: ACT.md step 6 adds I13's sentence word for word.
- Unit tests under `tests/unit/memaudit/` (a fake gitleaks script, a bare remote under `tmp_path`) and
  `tests/unit/adopt/test_w2_187*` for step 6. The test designer writes the acceptance cases in parallel
  (`test_w2_187_s12_push.py`), merged by your lead later.

## Rules
- Never copy the reader path; keep `maintain` a pass, never a gate. Reuse measure's helpers rather than a second span
  rule.
- **Every pytest through the heavy-slot gate**, the sandbox's own `$TMPDIR`, a Bash timeout of 3600000 ms for each:
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187/src python3 -m pytest tests/unit/memaudit -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  and the same for `tests/acceptance/W2-187`. The only W2-187 reds you may leave are the test designer's open items:
  any S10 case naming a rewritten heading section and any S12/F7 case not yet merged. A heavy-slot refusal is a wait.
- Update `docs/changes/W2-187-evidence.md` (S10 (6) with N2 (b), S12 and F7: the cases and results, and the source size by `git diff --stat 5336a6fca -- src governance`).
- Literal paths only as write targets. If a Write into `.gov-runtime/scratch/` is refused, write no script; use the
  Edit tool on your own files and one-line commands.
- **Commit** your paths only, the trailers in ONE final paragraph:
  `git commit -m "W2-187: <subject>" --trailer "Task: DAEO-0cd2" --trailer "Role: engineer" --trailer "Implements: DEC-1182, DEC-1179, DEC-1101, DEC-1072" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <your paths>`
  Never `Role: owner` or `Decided-by:`. No merge, no push, no edit of `.tickets/`, the register or `tests/acceptance/`.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)). A permission denial of a Write or a Bash form is a refusal too: do not
  redo the same edit by another form; report it.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines) / tests / discoveries / risks / lessons /
proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
