You are the ticket lead for ticket `DAEO-e8f0` (`W2-71`, "The secrets check passes a real commit hash of this repository for row W2-L423's rule only"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-71` on branch `w2/W2-71`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `51a443a47ae8`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it. Read the ticket file (`.tickets/DAEO-e8f0.md`), its card in `docs/plan/WAVE_2_WBS.md` §2, row W2-L423 in `docs/plan/WAVE_2_LIST.md`, and DEC-911 (item 4), DEC-298, DEC-347 and DEC-853 first.

## Why you start now

- **One gitleaks default rule** takes a bare 40-hex string for a token when it stands beside its keyword. A full commit hash in a log or record under `.gov-runtime/` can then turn `gov check`'s hard-block secrets-indexing check red by chance (row W2-L423).
- **Today the workaround is human:** commit hashes are written as 12 digits under `.gov-runtime/`, and the rule's keywords are never written there (DEC-911, "row W2-L423's rule"). An early-warning script and gate (b) catch slips.
- **The check strips allowlists** (DEC-298, DEC-347), so the exemption is written in the check itself, for that one rule and that one shape of match.
- **The owner's cadence (DEC-933 item 1, DEC-936 item 2):** each judge improvement is re-pinned as soon as it merges and passes its checks. You are the first of the third re-pin's two tickets; W2-68's ticket is being written now.

## The decisions for this run

- **The rule, exactly (DEC-911 item 4, the ticket's KPIs):**
  - a match of that one rule that is exactly 40 hex digits naming a commit object of the repository being scanned (`git cat-file -e <sha>^{commit}` in that project) is no finding, for both the secrets-indexing check and the pre-index filter, in a file and in a stored value;
  - everything else stays a finding: any other rule; 39 or 41 digits; a short hash; another repository's commit; a tree or blob id; a match whose verification cannot run (no git, not a repository, an error, a timeout). It fails closed;
  - a real token of that vendor in each of the rule's forms (its prefixed form, and 40 hex naming no commit here), built at test time, still fails.
- **Nothing printed or written:** matches are held in memory only. No report file, no match in any log, output or record. The clean-result record (DEC-853) never records a finding. Every file scanned today is still scanned with every rule set; no allowlist is added.
- **Row W2-L423's rule applies to this ticket's own files:** in every tracked file you or your workers write (code, tests, README, records), the rule's id and its keywords are written only in parts (for example joined at run time), never whole. Under `.gov-runtime/`, hashes are 12 digits. The test designer and the engineer get this in their briefs.
- **Tests first,** by a fresh independent test designer (launched sandboxed, `--effort high`; its brief must not set `TMPDIR`), in `tests/acceptance/W2-71/`:
  - one case per KPI line, in temporary repositories built from scratch (a real commit, a tree id, a blob id, another repository's commit);
  - tokens built at test time, never stored whole;
  - the check and the pre-index filter both judged, for a file and for a stored value;
  - red first: each case fails on the current code for the right reason.
- **The engineer** (fresh, launched sandboxed, `--effort high`) works only in `src/gov/secrets/**` and new unit tests under `tests/unit/secrets_check/`. Keep the verification within the check's existing git-process budgets, and cache per scan, not across scans.
- **Running beside you:** W2-75 (`tests/acceptance/W2-54/` only). No overlap.
- **Verification:** in the close's form, under the lock, with the retention option and the disk gate first.
  - **The nightly (owner, DEC-933, DEC-936):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists (from 02:00 most nights), you and your workers run no suite and no full run. Wait, and go on the moment it is gone. Every full run also waits for the verification lock.
  - **Known:** W2-54's green-here cases may time out under load in a plain full run (row W2-L429; W2-75 fixes the close's route); re-run them alone. W1-46's and W1-19's cases run in your serial phase (a plain run has no nightly route).
  - Any other red is named with its cause.
- **Reviews:** two (DEC-413). A fresh FULL reviewer (brief A3 with `JUDGEMENT.md` word for word, `--effort max`) on the final head; the probe asks above all whether any real token can pass. Commit the probe record only when it passes.

## This run's order

1. Tests first (the test designer), then **check red yourself.**
2. The engineer.
3. Rebuild and verify in full.
4. Review 1. If it fails on a fail-open finding an honest agent can hit: one test-design batch, one engineer, a full run, review 2 (the last).
5. **Return** DONE (probe passed; ready to merge, then re-pinned), or PACKAGES.

**Estimate:** about 50 lines in `src/gov/secrets/`, about 5 hours with the full run and one review.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
