---
type: probe
task: DAEO-e8f0
reviewer_session: d2169346-fb39-4c59-b65f-a27a6a40a83f
implementer_session: f54e59a0-cdd8-4a17-9214-476fe84da7d7
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 700102de5f4d1498f5452f50e7f4b306124f3d62
---

# Probe of W2-71 (DAEO-e8f0) at 700102de5f4d

**Probed:** head 700102de5f4d on `w2/W2-71`, and the diff against merge base 51a443a47ae8 with `w2/integrate`, in `src/gov/secrets` and `tests/unit/secrets_check`. The code under test is this worktree's `src/` (DEC-732): `gov.__file__` is `/home/usain/gov-os-worktrees/W2-71/src/gov/__init__.py`. Tools: git 2.43.0, gitleaks 8.30.1.

**Method:** every probe built its project from scratch in my temp folder. Tokens were built at run time and only booleans were reported. Changes made by this ticket were told from older gaps by running the merge base's module, loaded under another name, on the same scene.

**Step 0:**
- (a) The write outside the worktree failed ("Read-only file system").
- (b) `git hash-object -w` and `git update-index --refresh` worked.
- Role, ticket, worktree, branch and head were as expected.

**Tests (one file at a time; a nightly run held the machine):**
- Acceptance W2-71: 213 of 213 passed.
- Unit: `test_commit_exemption.py` 5 passed, `test_secrets.py` 12, `test_scan_scale.py` 12.

**Verdict: pass.** Classification (DEC-809): F1 yes/other, F2 yes/other, F3 yes/other, F4 yes/other, F5 no/fails open, F6 no/other, F7 yes/other. No finding is "yes" with "fails open" or "loses work".

**Can any real token pass?** No finding of any rule is dropped at the head. The only match the code lets go is a finding of row W2-L423's rule whose secret is exactly 40 hex digits that git names as a commit object of the project, and no real token is one. What does change: a text whose only detected match was a quoted commit is no longer refused. So a token the rule itself never matches loses that accidental block (F4, F5).

## Findings

### F1: in a partial clone, the verification sends each unknown candidate to the promisor remote (medium)
- **What was done:** I built a project as a partial clone (blob filter) of a local remote whose upload-pack logs what it is asked for. A log under `.gov-runtime/scratch/` and a page under `docs/` each quoted, after a keyword, a random 40-hex string standing in for the vendor's bare-form token. I ran the check by its declared command, then the filter.
- **What happened:**
  - Both failed closed: the check exited 1 naming the log, and the filter left the page out.
  - But git's lazy fetch sent each candidate that is not in the local object store to the remote, as an object asked for.
  - A commit present only on the remote was fetched into the project's store during the check, and was then exempt.
  - This is new: the code before this ticket never ran git.
  - git 2.43 has no switch to stop lazy fetches (one comes in 2.44). The code also removes every git variable of the caller, so a caller's own setting to stop them would be removed too.
  - The KPI's own test, a `git cat-file -e` call, fetches the same way.
- **What should have happened:** the matches stay in memory only (KPI 4) and no candidate leaves the machine. Either git reads only the local store, or the code fails closed without asking git when the repository has a promisor remote.
- Ordinary work: yes, because a partial clone is a common setup for a large repository the Gov OS is adopted into, and nothing has to be constructed. This programme's repository is a full clone, so it does not occur here today.
- Consequence: other (a match, which can be a real token of the vendor's bare form, is disclosed to the promisor remote; the verdict stays a finding).

### F2: a clean result is reused after the commit it rested on is pruned (low)
- **What was done:** a project quoted a commit of a side branch after each keyword, in three places: a log under `.gov-runtime/scratch/`, one value of a SQLite store under `.gov-runtime/stores/`, and a page under `docs/`.
  1. I ran the check (the store files were judged clean and recorded).
  2. I deleted the side branch, expired the reflog and ran garbage collection, so the commit was no longer an object.
  3. I ran the check again.
  4. I removed the clean record and ran the check once more.
- **What happened:** run 2 passed the log and the store on the reused results (exit 0, two reuse labels). Run 4, on the same bytes, named both (exit 1). The filter keeps no record and left the page out after the prune, so the check and the filter disagree on the same bytes.
- **What should have happened:** a match that names no commit object of the repository is a finding (KPI 1, failure KPI 2). A verdict that rests on the repository's commits should not be reused once they may have changed. It should either not be kept, or be kept together with what it rests on.
- Ordinary work: yes, because ticket branches are deleted after they merge, and git's automatic garbage collection prunes their unreachable commits once the default expiry passes (30 days for reflog entries, 2 weeks for unreachable objects).
- Consequence: other (no credential can pass this way: only bytes whose every match was then a commit of the project are ever recorded clean).

### F3: the record's form is unchanged, so older code, the pinned judge included, trusts this code's clean results (low)
- **What was done:** I ran the merge base's module beside the head's on one project that quoted its own commits after each keyword, in a log and in a store. I also read the pinned judge (`pin-5c401220`) for its record form, record path and scanner digest, without running it.
- **What happened:**
  - The older code flags both stores.
  - Once the head's code had recorded them clean, the older code passed both on the reused results.
  - The record form is 4 in both, and the scanner digest is the same in both.
  - The pinned judge has form 4, the same record path and no exemption. Its scanner digest equals the head's on this worktree's rules.
- **What should have happened:** a record written under the exemption is not trusted by a judge that does not apply it, and the reverse; a new record form would do it. The cost: each judge rescans in full whenever the other wrote last (time only).
- Ordinary work: yes, because until the second re-pin the pinned judge is older than this ticket, and verification runs of a tree's own code (DEC-732) write the record into the same `.gov-runtime/` that the pinned gate reads.
- Consequence: other (the pinned gate (b) passes those stores instead of failing closed as DEC-911 item 3 describes, but they hold only commit hashes of the project; no credential passes).

### F4: a token the rule itself never matches loses the block a quoted commit gave it (low)
- **What was done:** the older and the head code judged texts under the vendor keyword. Each held a random 40-hex token placed in one of three ways: at a sentence's end, in brackets, or joined to a commit by a hyphen. Each text also quoted a commit of the project. I then judged the same tokens without the commit.
- **What happened:**
  - With the commit, each text was refused before the ticket and passes at the head.
  - Without it, each passes both before and after. Row W2-L423's rule never matches a bare-form token followed by a full stop, a closing bracket or a hyphen (tested), nor, by the rule's definition, a comma. That is gitleaks' own trailing condition.
  - A token followed by a space, a quote, a semicolon or a line's end stays a finding at the head.
- **What should have happened:** nothing is due in this ticket. No finding of any rule is dropped, and any implementation of DEC-911 item 4 has this effect. The gap is the rule's (a Wave 3 row).
- Ordinary work: yes, because a token written at a sentence's end, in a log that also quotes a commit beside a keyword, is ordinary prose.
- Consequence: other (the text was refused before only because the quoted commit was itself flagged, which is the false red DEC-911 item 4 removes; the rule's coverage of the token is the same as before this ticket).

### F5: the filter reads a SQLite file by its bytes and misses a bare-form token in a value of its own (low; mostly pre-existing)
- **What was done:** the filter judged SQLite files under `docs/` with the older and the head code, and the check judged the same stores under `.gov-runtime/stores/`. Three stores:
  1. One value quoting a commit after the vendor keyword, and another value holding a random token alone.
  2. One value holding the keyword alone, and another holding the token alone.
  3. A contentless FTS5 table indexing a line with the keyword and a token.
- **What happened:**
  - In the raw bytes, the byte before a value (its record header) can be a word character, so the rule's word boundary fails.
  - Stores 2 and 3 pass the filter both before and after the ticket.
  - Store 1 was refused before only because of the quoted commit, and passes at the head.
  - The check, which reads values and FTS5 terms, finds all three. The lexical indexer indexes tracked files the filter passes.
- **What should have happened:** the filter judges a SQLite file in an indexable path by its values, as the check does.
- Ordinary work: no, because it needs a tracked SQLite file in a governance namespace holding a real token in a value of its own.
- Consequence: fails open (in the filter, before this ticket for stores 2 and 3; this ticket removes the accidental block on store 1).

### F6: a colon in the folder above the root breaks the ceiling (low)
- **What was done:** a project root that is not itself a repository, inside a repository whose folder path holds a colon; then the same without the colon.
- **What happened:** with the colon, the parent repository's commit was answered as the project's and exempt; without it, it was not. The ceiling variable given to git is a colon-separated list, so the parent's path is split at the colon and stops nothing.
- **What should have happened:** a root that is not itself a repository is never answered by one above it, as the code itself states.
- Ordinary work: no, because it needs a colon in a folder name above a project root that is itself no repository.
- Consequence: other (the exempt string is a real commit of the repository that holds the project; no credential passes).

### F7: tool-written records under `.gov-runtime/scratch/` hold full commit hashes (info)
- **What was done:** I counted, without printing, 40-digit hex strings and both keywords in the 30 files under this worktree's `.gov-runtime/scratch/`.
- **What happened:** no file holds a keyword. 7 tool-written files hold full commit hashes: the tripwire snapshots' head fields, gov check's provenance fields, and the checkpoint tool's head-commit field in CP-DAEO-e8f0-0001 and -0002. The tracked checkpoints this ticket changed (CP-0003, CP-0004) hold none.
- **What should have happened:** DEC-911 item 1 and KPI 5 ask for 12-digit hashes in records under `.gov-runtime/`. The suite reads that as binding sessions, not tools.
- Ordinary work: yes, because the tools write these fields on every run.
- Consequence: other (no keyword stands in those files, so the rule cannot fire on them; at the head a full commit hash beside a keyword is exempt anyway).

## Found sound
- **Real tokens of the vendor:**
  - A random bare-form token after the vendor keyword is a finding of both the check and the filter in a plain file, a UTF-16 file, a SQLite value, an FTS5 table with content, and a store's freed space.
  - The check also finds it in a contentless FTS5 index.
  - This agrees with K2's 6 forms, each in a file and a store, for the check and the filter.
- **Path names** (`path_holds_secret`, which the acceptance suite does not cover):
  - A commit of the project as a folder name under the vendor keyword is exempt, in lower or upper case.
  - A token, a tree id, a blob id, the prefix keyword joined to a commit, and a commit beside a token are all findings.
- **Sharing:** these all stay findings: a token on the same line as an exempt commit, a token on the next line, a token in another value of the same store (check), and another rule's finding on the same line.
- **Another repository:** with `GIT_DIR`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES` or `GIT_COMMON_DIR` naming another repository, that repository's commit stays a finding, and the project's own commit is still exempt.
- **Linked worktree:**
  - Inside this launched session, the verification answers for this worktree's shared repository.
  - The session's own git configuration variables are removed first. The repository belongs to the session's user, so git still answers; were it another user's, git would refuse and the match would stay a finding.
- **The verification:** only an answer naming the exact 40 digits as type commit counts. No git, an error, a short answer, a timeout or a non-zero exit all give no commit (code reading, plus the suite's no-git, not-a-repository, git-fails and git-hangs cases).
- **Time:**
  - All 3,377 commits of this repository were verified in 0.01 s, and 20,000 unknown names in 0.64 s.
  - git is asked once per text, after every rule set has run, within a 10 s bound per call; the existing limits are unchanged.
- **No rule set skipped:** both rule sets still run on exempt texts (K4); a text stops early only on a finding that is not exempt.
- **Nothing written or printed:**
  - No new file appeared in the project root after the check ran, and no hash appeared on the check's or the filter's standard output or error.
  - The record holds digests only, and the gitleaks report stays in memory.
  - The error the check raises carries the exit code only (code reading).
- **No allowlist added:** neither gitleaks file is changed, and every file is still scanned (K4).
- **Keywords in parts:** the rule's id and both keywords appear whole in none of the 15 files this ticket changed, in its commit messages, or in their compiled caches, and none of those files holds a 40-digit hash.

## The lead's judgement

- **Who probed.** A fresh read-only reviewer (role `independent-auditor`, session `d2169346-fb39-4c59-b65f-a27a6a40a83f`, 2026-10-29), started through `gov launch` under its OS sandbox with the reading tools alone, at effort max; commissioned and judged by the ticket lead (an orchestrator-role session, DEC-137). It wrote nothing in the repository: the lead's tripwire before and after its session shows no change in this worktree or in any other tree.
- **Judged by `governance/project/briefs/JUDGEMENT.md` (DEC-801 to DEC-809).** The lead agrees with the reviewer's classification: no finding is "yes" with "fails open" or "loses work", so the probe passes and no round starts (DEC-413). F1 to F7 go back to the orchestrator as residuals. F1 (a partial clone's lazy fetch) comes with a recommendation to weigh it before the second re-pin: the verdict fails closed, but a candidate match leaves the machine. F2 and F3 (the clean record across a prune and across code versions) are rows. F4 and F5 (gaps in the rule and the filter, mostly from before this ticket) and F6 (a colon above the root) are Wave 3 rows. F7 is a note on tool-written fields.
