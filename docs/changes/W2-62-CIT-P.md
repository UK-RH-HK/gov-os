---
id: W2-62-CIT-P
type: change-impact-proposal
status: PROPOSED
date: 2026-10-19
branch: w2/W2-62
base: 87cad875
ticket: DAEO-juee (W2-62)
author: engineer (W2-62)
review: a read-only independent reviewer, after the acceptance tests are green
decisions_carried: [DEC-792, DEC-837, DEC-838]
list_rows: [W2-M372, W2-M373]
state_class: EVIDENCE
---

# W2-62: change-impact proposal (CIT-P) on the session-start hook and the checkpoint skill

This change makes the kernel's session-start hook deliver the orchestrator's RESUME HERE section in full and name the
prompt in force, and writes the resume rule into the checkpoint skill. It is a kernel hook and skill change, so it
goes through CIT-P (CAP-33); the owner approved its scope in DEC-837.

## 1. What triggers the change

| # | Trigger | Source | State before this change |
|---|---|---|---|
| T1 | The hook injects only the first 9,000 characters of the RESUME HERE section (`SECTION_MAX_CHARS`) and says so only in a closing `[truncated …]` line; a long section's later state never reaches the resumed session | Row W2-M372; DEC-792 item 2; DEC-837 item 1 | Open |
| T2 | The hook names the Wave 1 prompt (`PROMPT_REL = governance/project/prompts/w1-orchestrator.md`) in Wave 2 | Row W2-M373; DEC-792 item 2; DEC-837 item 1 | Open |
| T3 | RESUME HERE holds the full session state; repository knowledge comes from retrieval and the context packets; a checkpoint at every handover | DEC-837 items 2 and 3 | Not in the checkpoint skill; DEC-792 item 1 limits RESUME HERE to 8,000 characters |

## 2. Research record: does Claude Code cap or move a SessionStart hook's `additionalContext`?

Measured by the orchestrator on 2026-10-19, before implementation (the ticket's second KPI line).

- **Harness:** Claude Code 2.1.292 (`~/.local/bin/claude`), a headless session on Haiku 4.5, started in a folder with
  no project settings. `--settings` carried one SessionStart hook that printed
  `{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext": <N characters ending in a random 17-character token>}}`.
  The session was asked, without tools, to quote the last 30 characters it saw.
- **N = 9,500 characters:** the whole context arrived; the session quoted the token exactly.
- **N = 12,000 characters:** the harness did not inject the context. It said "Output too large (11.7KB). Full output
  saved to: `~/.claude/projects/<project>/<session>/tool-results/hook-<id>-1-additionalContext.txt`" and showed a
  preview; the token never reached the session (it quoted filler).
- **N = 60,000 characters:** the same as at 12,000: moved to a file, a preview shown, the token never reached the
  session.

**Conclusion.** Claude Code 2.1.292 moves a SessionStart hook's `additionalContext` to a file above a size: it arrives
whole only up to about 10,000 characters (the hook's own 10,000-character cap). So the bound stays 10,000 characters,
and a section that does not fit is delivered by instruction rather than by injection: the hook names the checkpoint
file, the section's exact line range (`lines <first>-<last>`) and its size (`<n> characters`), and tells the session to
read those lines in full before anything else. A section that fits within the bound with the other critical parts is
injected whole as well. The live resumed-session check (a resumed session shows the whole section read) is run by the
lead, as the `local_only` case of the acceptance suite; this engineer's sandbox has no network.

## 3. What changes

| File | Change |
|---|---|
| `template/governance/kernel/hooks/sessionstart.py` | `SECTION_MAX_CHARS` and the `[truncated …]` line removed. New `resume_lines`: the section and its 1-based line range in the checkpoint (heading to last line that is not empty; a fenced line is not a heading; the written part only). The orchestrator's injection carries the instruction with path, range and size; the whole section when it fits the 10,000-character bound with the instruction and the staleness warning; otherwise none of it, and a sentence that says so. Critical parts are never cut; the optional parts (`gov context --brief`, `tk ready`, the checkpoint resume brief) are trimmed. `PROMPT_REL` removed: new `roster_prompt` reads `roles: orchestrator: prompt:` from `governance/project/roster.yaml`; with none (no file, no key, not valid YAML) no prompt is named. Input that is a JSON array or string is read as no input |
| `template/governance/kernel/skills/checkpoint/SKILL.md` | New section "The resume rule" (DEC-837 items 1 to 3); version 1.0.0 → 1.1.0 (CAP-24.c). Nothing else changed |
| `tests/unit/hooks/` | Builder tests updated from the Wave 1 prompt constant and the cut to the roster prompt and the line range; new builder tests for the range, the bound and the roster |

## 4. The three options (DEC-105)

| Option | What it means here | Cost |
|---|---|---|
| **Apply now** (chosen by the owner, DEC-837; scope approved under CAP-33) | The hook and the skill change as in §3; DEC-792's 8,000-character limit is lifted once it lands | This ticket (about 60 lines of hook code), the revised acceptance suites, one independent review |
| Defer | Keep the 9,000-character cut and the Wave 1 prompt until W2-10 | The orchestrator keeps resuming from a cut section under the wrong prompt, and RESUME HERE stays held to 8,000 characters by DEC-792 |
| Re-baseline | Drop RESUME HERE injection and rely on the checkpoint brief alone | Loses the staleness warning's context and the orchestrator's state on resume; contradicts DEC-837 |

## 5. Impact

| Area | Impact |
|---|---|
| The hook | As in §3. Runs live in every session of the main tree once merged |
| The checkpoint skill | The resume rule; version 1.1.0 |
| Unit tests | `tests/unit/hooks/test_w29_hooks.py` and `test_resume_hooks.py` updated (the prompt constant and the cut); new builder tests |
| Acceptance suites | `tests/acceptance/W2-62/` (new); `tests/acceptance/W1-49/` and `tests/acceptance/W1-29/` revised by the Independent Test Designer for the new behaviour (the line range in place of the cut and the word `truncated`; the prompt from the roster) |
| Decisions | DEC-792's 8,000-character limit on RESUME HERE is lifted (DEC-837 item 2) |
| Configuration | `governance/project/roster.yaml` needs `prompt: governance/project/prompts/w2-orchestrator.md` under `roles:` → `orchestrator:`, added by the owner or the orchestrator (outside this ticket's paths). Until it is added, this repository's sessions are told no prompt (never a wrong one) |
| Other kernel hooks, the guard, the launcher | None |

## 6. Independent review

After the acceptance suites are green, a read-only independent reviewer (a fresh session that did not author this
change) reviews the hook, the skill and this record against DEC-837 and the ticket's KPIs (CAP-33.d). A CIT-E then
records what was applied.
