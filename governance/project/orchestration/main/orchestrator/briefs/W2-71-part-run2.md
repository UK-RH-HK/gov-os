You are the ticket lead for ticket `DAEO-e8f0` (`W2-71`, "The secrets check passes a real commit hash of this repository for row W2-L423's rule only"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-71` on branch `w2/W2-71`.

**This is run 2, the last round (DEC-413: review 2 is the last).** `git rev-parse --short=12 HEAD` must show `1598a1c0996c` (run 1's DONE head), and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it. Read your run 1 checkpoint (`.gov-runtime/scratch/lead/CHECKPOINT.md`), the probe record `docs/probes/DAEO-e8f0/PR-DAEO-e8f0.md` (its F1), and package `governance/project/orchestration/packages/P1-MORNING-2026-10-29.md` item 4.

## Why you start now

- **Review 1 passed,** with one finding the orchestrator decided to fix before the merge (a delegated decision, stricter only; P1-MORNING-2026-10-29 item 4).
- **F1:** in a partial clone, the check's `git cat-file --batch-check` on a 40-hex candidate makes git lazily fetch the object from the promisor remote. A candidate that may be a real token is then sent to that remote, although the verdict still fails closed. This repository is a full clone, so nothing is sent here today. But the third re-pin ships the check to every adopted repository, some of them partial clones.

## The decisions for this run

- **The rule:** when the scanned repository is a partial clone, the exemption does not ask git at all, and the finding stays a finding (fail closed). Read the repository's configuration without touching the object store: `extensions.partialClone` set, or any remote with `promisor = true`, or a `partialclonefilter`. A configuration that cannot be read counts as a partial clone (fail closed).
  - Also keep git from fetching even in a full clone: run `cat-file` with `GIT_NO_LAZY_FETCH=1` where your git supports it (state the version you measured), as a second guard, never as the only one.
- **Tests first,** by a fresh independent test designer (launched sandboxed, `--effort xhigh`; its brief must not set `TMPDIR`), in `tests/acceptance/W2-71/`, with `Rewrite-Reason:` only if an existing case changes:
  - a partial clone built at test time (`git clone --filter=blob:none` from a local bare repository, with `uploadpack.allowFilter` set in the source). A real commit's hash beside the rule's keyword stays a finding there, and no fetch is made: count the source's upload-pack requests, or point the promisor at a path that would fail;
  - the same in a repository with only a promisor remote configured, and in one whose configuration cannot be read;
  - red first, against run 1's code.
- **The engineer** (fresh, launched sandboxed, `--effort high`) works only in `src/gov/secrets/**` and `tests/unit/secrets_check/**`.
- **Row W2-L423's rule** applies to every tracked file you or your workers write: the rule's id and keywords only in parts; hashes as 12 digits under `.gov-runtime/`.
- **Verification:** in the close's form, under the lock, with the retention option and the disk gate first.
  - **The nightly:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists, run no suite. Every full run waits for the verification lock.
  - **A close queue may be running in the main tree** (W2-75, W2-63, W2-07, W2-68). Your full run takes the lock as usual. Run heavy suites only when the 1-minute load is under 20, waiting inside each background command.
  - **Known:** the DEC-919 case (W2-66's lead-verification case, listing your conftest; row W2-L440). W2-54's green-here cases in a plain run may time out under load; re-run them alone.
- **Review 2 (the last):** a fresh FULL reviewer (brief A3 with `JUDGEMENT.md` word for word, `--effort max`) on the final head. Its scope is the run-2 change and anything it touches, and above all whether any route still lets git fetch, or lets a real token pass. Commit the probe record only when it passes.

## This run's order

1. Tests first (the test designer), then **check red yourself.**
2. The engineer.
3. Rebuild and verify in full.
4. Review 2.
5. **Return** DONE (ready to merge and re-pin), or PACKAGES.

**Estimate:** about 15 lines in `src/gov/secrets/`, about 3 hours with the full run and the review.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
