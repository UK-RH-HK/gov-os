You are the ticket lead for ticket `DAEO-rmbe` (`W2-69`, "The secrets check reads what the stores hold: no chance red from where a scan begins"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-69` on branch `w2/W2-69`.

**This is run 1.** `git log --oneline -1` must show `c2d539c6`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

## Why you start now

The secrets-indexing check, a hard-block check, flags a fragment of a longer identifier when one of gitleaks' reads of its standard input begins inside a word. Where the reads begin moves with every rebuild, so any rebuild can turn `gov check` and a close RED by chance. This stopped W2-62's close on 2026-10-22 (package `governance/project/orchestration/packages/P-W2-62-G1.md`, row W2-M404).

The owner ordered this ticket (DEC-897) and set its order (DEC-899): W2-66 and W2-07 first, this ticket next. It rides in the first re-pin. Until then, DEC-897 (b) allows one proven re-run of a close's queue per close. Read the ticket file (`.tickets/DAEO-rmbe.md`) and the card (`docs/plan/WAVE_2_WBS.md` §2, W2-69) first.

## The owner's decisions for this run

- **DEC-897 item 1, the design question:** should the check scan the indexed text (each SQLite store's rows, as text) instead of the raw database bytes?
  - That option comes with each store compacted (`VACUUM`) after each rebuild, so no deleted text survives in free pages, and a boundary-aware raw scan kept only as a backstop.
  - **The tests decide.**
  - **Answer it in `docs/research/W2-69-secrets-scan.md` before the code,** with evidence: measure on a copy of the code-graph store, `.gov-runtime/codeintel/home/code.db` of your worktree after its rebuild. The package's §2 gives the cut test (gitleaks clean on a whole line, red on the line cut at the match's first byte).
  - **Print positions, lengths, rule ids and exit codes only, never the matched bytes.**
- **The KPIs' three tests:**
  - a real token is found at every offset and in every form the stores hold it;
  - an embedded fragment of a longer identifier is not flagged, at every offset relative to any read edge;
  - deleted text does not survive a rebuild.
- **The check must not be weakened:**
  - every file under `.gov-runtime/` it scans today is still scanned, with every rule set;
  - a scan that cannot finish fails closed;
  - DEC-853's reuse of a clean result keyed on the store's hash stays;
  - a finding is never reused.
- **P-IS-5 (a), in DEC-899:**
  - **The rename (W2-L373):** `tests/unit/secrets/` is renamed `tests/unit/secrets_check/`, because it shadows the standard library's `secrets` under some plugins. That is your engineer's builder-test work.
  - **The W2-50 cases:** your test designer revises, only where scanning rows as text or compacting changes what they expect, each with a `Rewrite-Reason: DEC-897`:
    - W2-50's secrets-scan scale cases (`tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py`, `w2_50_scan_support.py`);
    - the secrets cases of `test_w2_50_never_indexed.py` and `test_w2_50_last_review.py`.
  - **MR-3:** these acceptance files are named in your ticket file's body, never in the engineer's `allowed_paths`.
- **Compaction lives in `src/gov/rebuild/command.py`, the compaction step after each store's build only.** W2-06 holds the rest of that folder and starts after you.
- **DEC-898, the scratch budget:** as in the common brief below. Report the scratch size in every return.

## This run's order

1. **The design question,** answered with evidence in the research note, by a fresh research worker (launched sandboxed, `--effort high`) or by you. Commit the note.
2. **Tests first:** a fresh independent test designer, launched sandboxed, `--effort xhigh` (a FULL ticket's designer), on every KPI line, FULL proportion, and the named W2-50 revisions.
3. **Check red yourself.**
4. **Implement:** a fresh engineer, launched sandboxed, `--effort high`, inside the allowed paths only, the rename included.
5. **Verify** in the close's form, with `gov check` after a rebuild, the secrets-indexing family GREEN.
6. **FULL review:** a fresh read-only reviewer (brief A3 with `JUDGEMENT.md` word for word, `--effort max`) on the final code. Commit the probe record under `docs/probes/DAEO-rmbe/`.
7. **Return** DONE, or PACKAGES.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit); split larger work into rounds.

---
