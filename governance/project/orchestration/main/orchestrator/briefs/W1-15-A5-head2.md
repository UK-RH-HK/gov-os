You are the ticket lead for ticket `DAEO-7nne` (`W1-15`, "Secret rules and pre-index filter"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-15` on branch `w1/W1-15`. You run the ticket loop for this one ticket. Its implementer is an engineer (brief A2). FULL: after green, a reviewer (brief A3).

## State of this ticket

- An earlier lead ran the test design: head `7ed25507`, 59 cases (17 `local_only`), red for the stated reasons. Its checkpoint is `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree; read it. It returned six packages. **All six are decided as the designer and the lead recommended, so the suite stands and the engineer starts directly.** They are DEC-285 to DEC-290 on `w1/integrate`.

## What you do, in order

1. **Take `w1/integrate` into this branch first**: `git merge w1/integrate`, with a message whose last paragraph has `Task: DAEO-7nne` and `Role: orchestrator`. Resolve nothing by hand; if it conflicts, abort the merge and return PACKAGES saying so. The containment hook will flag the merge; that is a record, not a defect (DEC-254); mention it in your summary. Then read DEC-285 to DEC-290 in `docs/DECISION_REGISTER.md`:
   - DEC-285: the filter is `gov.secrets.indexable(root, paths)`; if it cannot decide it raises or drops the path, never lets it through; a family check's `command` runs by `sh -c` in the project root, exit 0 is green.
   - DEC-286: the seven dev canaries as the designer found them; the token canary in both spellings.
   - DEC-287: the filter runs the gitleaks binary (`~/.local/bin/gitleaks`, 8.30.1, in the tool registry) with the rules of `.gitleaks.toml`; nothing is installed.
   - DEC-288: `template/.gitleaks.toml` has the rules and no path allowlist; the root `.gitleaks.toml` has the same rules plus this repository's allowlist.
   - DEC-289: the filter reads only a namespace's `paths` and `memory_class`.
   - DEC-290: the root file allowlists, by path, the tracked documents that only name the canary identifier, after the engineer runs gitleaks over the tree and reports which they are; the filter ignores path allowlists; the secrets-indexing check scans store content, SQLite rows included.
2. **Engineer** (brief A2, fresh), to the suite as it stands. Estimate 70 LOC, with the extra for the store scan accepted (DEC-290); proportion rule DEC-135. The engineer reports the list of tracked paths gitleaks flags before it writes the root allowlist, and allowlists only documents that name the canary identifier, never a file with a real-looking secret outside the fixtures already allowlisted. If gitleaks flags anything that looks like a real secret, stop and return it as a package without printing the value.
3. **Verify** every suite and the validator. Suites of tickets still in flight elsewhere (W1-46, W1-49, W1-50, W1-25) may be red or absent on this branch from their own tickets; W1-50 is red by design (26 failed, 17 passed). Confirm that and report them apart.
4. **Reviewer** (brief A3): ways a planted secret or a product-data file still reaches a derived store: a path that matches no namespace; a project with no path map; encodings (UTF-16, base64, a secret split across lines); a symbolic link from a governance namespace to a product file; a file renamed after it was classed; a very large file; gitleaks missing or failing (the filter must not fail open); an allowlisted path. A finding that lets a secret or product data through is fixed (a test batch first, as described behaviours, then a fresh engineer); the rest are residuals.
5. Return DONE with the whole ticket's summary. Learning metrics so far: KPI disputes 0, ambiguity packages 6.

