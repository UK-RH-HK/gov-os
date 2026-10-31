# P-SPEED-1: the fastest safe fix for slow rebuilds: gitleaks results remembered by content hash (P1, for approval)

For the owner (DEC-966 item 4).

## 1. Context
- A store rebuild runs the secrets filter (`src/gov/secrets/__init__.py`, `indexable()` and `path_holds_secret()`) on every file it indexes, every time.
- For each file and each of the 2 rule sets in force, it starts one `gitleaks stdin` process. With about 2,600 tracked files, that is over 5,000 gitleaks starts per rebuild, plus one per path name.
- Nothing is remembered between rebuilds, worktrees or clones. A close's clean clone and the nightly's clone each re-scan files the main tree scanned an hour earlier.

## 2. What happened (W2-76's measurements)
- **Run 1:** the secrets stage took 274.8 s of a 307.4 s rebuild (89 %).
- **Run 2:** 547.9 s of 735.4 s, at load about 50 (75 %).
- **This session's rebuilds:** 2,253 s for the W2-54 pre-check clone, and 3,459 s for the designers' first store, both at load 35 to 50.
- Rebuilds also wait for one another, under the one-rebuild-at-a-time rule you kept for now. So their length holds up closes, leads, the nightly and the designers' store.

## 3. Why it matters
- Every close, lead and nightly pays this in full, and the rebuild lock queues them behind each other.
- Cutting the secrets stage to the files that are new or changed is the largest single speed gain available. It does not weaken the scan.

## 4. The fix (W2-107, filed with this package)
- **One machine-wide cache** at `~/.cache/gov-os/secrets-scan.sqlite`, outside every repository. Worktrees, close clones, the nightly and the designers' store share it. It holds only hashes and verdicts, never content.
- **Its key:**
  - the sha256 of the exact bytes scanned (a file's content, or a path's names);
  - the kind;
  - the engine's fingerprint: gitleaks' version string (8.30.1 today), the sha256 of every rule set in force, and the cache format's version.
- **Only "clean" is remembered,** meaning no finding of any kind by any rule set. Any finding is always scanned again and never remembered. That includes a match exempted as one of this repository's commit hashes (row W2-L423's rule), since that exemption depends on the repository.
- **Any update to gitleaks or its rules clears every remembered result.** A fingerprint that differs from the cache's empties it.
- **It fails closed:**
  - a cache that cannot be read, is corrupt or is locked counts as a miss, so the file is scanned;
  - a failed write is ignored;
  - a scan that cannot decide still raises, as today.
- **The nightly scans every file in full:** with `GOV_SECRETS_FULL_SCAN=1` it ignores what is remembered and writes fresh results. The nightly sets it, a one-line change to `nightly.sh` that I make at merge time, with `test_nightly.sh` and a review.
- **The rebuild's record** says how many files were scanned and how many were remembered, beside W2-76's stage times.
- **Expected effect:** a rebuild after a merge scans only the merge's new or changed files (tens to a few hundred, not 2,600), and a close clone's rebuild after the main tree's scans almost nothing. On run 1's figures that is about 30 s instead of 307 s. The ticket measures it: a second rebuild of an unchanged tree, and a close clone after the main tree, before and after.

## 5. Where it belongs, and the options
- **(a) A ticket of its own, W2-107: FULL, priority 0 (recommended).**
  - Its files, `src/gov/secrets/`, belong to no running ticket, so it can start now.
  - It is FULL because the filter guards the index: a wrong remembered "clean" would let a secret in, which fails open. So it gets the independent review.
  - About 150 to 250 lines, roughly 6 to 8 hours.
- **(b) Fold it into W2-76.** W2-76 holds `src/gov/rebuild/**` and is in its run 3 (the lock pass-through, then its figures for rule 3). The cache lives in `src/gov/secrets/`, a different module, so folding it in would delay W2-76's close and mix a security change into a timing ticket.
- **(c) Batch the files into fewer gitleaks calls** instead of remembering results. This would be faster for a first scan, but harder to attribute a finding to its file. It is kept as a later option, not instead of (a).

## 6. Recommendation
**(a), confidence high.** Classification: ordinary work, yes (every rebuild); consequence: other (slow), with the fail-open risk handled by remembering only clean results, the fingerprint, failing closed, and the nightly's full scan.

**What waiting costs:** every rebuild stays at 5 to 60 minutes.

**What it blocks:** nothing.

I start it as soon as you say yes, ahead of the queued resumes.
