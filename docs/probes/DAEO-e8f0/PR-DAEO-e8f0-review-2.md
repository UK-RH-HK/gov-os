---
type: probe
task: DAEO-e8f0
reviewer_session: ba8863bb-7555-4e86-bcef-33b3b05a72e5
implementer_session: 96a38443-e7ae-4982-afdf-2fabaadc3e57
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 9c840ff50ae66463d68d0b8b7dc80647f9d81a64
---

# Probe of W2-71 (DAEO-e8f0) at 9c840ff50ae6: review 2, the last

**Probed:** head 9c840ff50ae6 on `w2/W2-71`, and run 2's diff `1598a1c0996c..9c840ff50ae6`:
- `src/gov/secrets/__init__.py`: the configuration read before the commit lookup, and `GIT_NO_LAZY_FETCH` on the lookup;
- the builder tests in `tests/unit/secrets_check/test_commit_exemption.py`;
- three new acceptance files, the support module and the README in `tests/acceptance/W2-71/`.

The code under test is this worktree's `src/` (DEC-732): `gov.__file__` is `/home/usain/gov-os-worktrees/W2-71/src/gov/__init__.py`. Tools: git 2.43.0 (Ubuntu `1:2.43.0-1ubuntu7.4`) and gitleaks 8.30.1.

**Method:** every scene was built from scratch in my temp folder.
- A bare source serves filters and any object id. A wrapper counts every upload-pack request it gets.
- Clones are made over `file://`, full or `--filter=blob:none`. After each clone, a fresh commit is pushed to the source, so only the remote holds it.
- Each scene ran three things:
  1. the code's own configuration read and commit lookup;
  2. the second guard alone (the configuration read bypassed in-process);
  3. a control: git called exactly as the code calls it, but without the variable.
- Tokens were built at run time. Only booleans and counts were printed.

**Step 0:**
- (a) The write outside the worktree failed ("Read-only file system").
- (b) `git hash-object -w` and `git update-index --refresh` worked.
- Role, ticket, worktree, branch and head were as expected.

**Tests:** acceptance W2-71: 304 of 304 passed (140.7 s). `tests/unit/secrets_check`: 42 of 42 passed (76.1 s).

**Verdict: pass.** Classification (DEC-809): F1 no/other, F2 yes/other, F3 no/other. No finding is "yes" with "fails open" or "loses work".

**Does any route still let git fetch, or let a real token pass?** No.
- **Fetching:** git fetched in 29 of the 39 configuration scenes when called without the variable. In each of those 29, the configuration read alone kept the code from asking git about any object. On this machine the variable alone also stopped every fetch. The code made 0 requests in all 39 scenes, and 0 in every end-to-end run.
- **Tokens:** every real-token form stayed a finding of the check, the filter and the path-name judgement, in a partial clone, a full clone and a promisor-by-include clone.

## Findings

### F1: a clean result recorded in a full clone is reused after the clone becomes a promisor (low)
- **What was done:** a full clone with an ordinary remote held three files under `.gov-runtime/`: two logs in `scratch/` and one SQLite store in `stores/`. Each quoted the clone's own head commit after a keyword. I then:
  1. ran the check by its declared command;
  2. set the remote as a promisor, as a filtered fetch does;
  3. ran the check again;
  4. removed the clean record and ran the check a third time.
- **What happened:**
  - The first run passed (exit 0) and recorded the three files as clean.
  - The second run, in what is now a promisor repository, passed on the reused results: exit 0, three reuse labels, 0 requests.
  - The third run, on the same bytes, named all three (exit 1).
  - The filter keeps no record, so on the same bytes it leaves such a page out. The check and the filter disagree.
- **What should have happened:** run 2's decision says that in a partial clone such a match stays a finding. A verdict that rested on the repository not being a partial clone should not outlive that change. Either a text exempted on that basis is not recorded, or the record keeps what the verdict rested on. This is the same class as review 1's F2.
- Ordinary work: no, because a clone becomes a promisor after the fact only through a deliberate change to the repository (a filtered fetch or a promisor set by hand); a clone made partial by `git clone --filter` starts with no record.
- Consequence: other (no fetch and nothing leaves the machine; no token passes, because the bytes were recorded clean only when every match had been verified as a local commit object).

### F2: full commit hashes in tool-written files under `.gov-runtime/scratch/` (info; review 1's F7 again)
- **What was done:** without printing anything, I counted 40-digit hex runs and both keywords in the 2,392 regular files of this worktree's `.gov-runtime/`. I then looked up the type of each hash in the lead's run-2 logs.
- **What happened:**
  - Only two files hold a keyword, and both are index stores: `store.db` and the code-graph copy of a tracked research page. DEC-923 leaves index stores out of the early warning, and this run wrote neither.
  - Run 2 added files with full hashes:
    - `scratch/lead/log/check2.json`: 133 distinct hashes, all commits here (`gov check`'s provenance);
    - `parallel2.out`: 1 commit;
    - `parallel2.xml`: 1 commit and 1 string that names no object;
    - `collect2.out`: 1 string that names no object;
    - more tripwire snapshots and the checkpoint tool's copies in `scratch/`, as review 1 found.
- **What should have happened:** DEC-911 item 1 and KPI 5 ask for 12-digit hashes in records and logs under `.gov-runtime/`. The tools do not shorten them: `gov check`, the tripwire, the checkpoint tool, and test output kept as a log.
- Ordinary work: yes, because the tools write these fields on every run.
- Consequence: other (no keyword stands in any of those files, so the rule cannot fire on them; and at the head, a full commit beside a keyword is exempt in a full clone).

### F3: three settings that git does not treat as a promisor turn the exemption off (info)
- **What was done:** full clones with an ordinary remote, each with one setting:
  - a promisor key with an empty value (bare, and as a quoted empty string);
  - a promisor key in a remote section without a name;
  - the partial-clone extension in the user's global file only.
  Each scene had git's own lookup, without the variable, as its control.
- **What happened:** git made no request in any of them. To git, an empty value is false; a remote section without a name has no URL; and the extension counts only in the repository's own file. The code counts each as a partial clone, so the project's own commit beside a keyword stays a finding.
- **What should have happened:** nothing is due. The decision is stricter only, and the code states that any promisor value other than git's spellings of false counts as true. This is noted because it differs from the decision's words ("promisor true, in git's spellings of a boolean") in the strict direction.
- Ordinary work: no, because neither git nor an ordinary setup writes any of these.
- Consequence: other (fails closed: the false red that DEC-911 item 4 removes comes back in such a repository).

## Found sound
- **No route that fetches.** 39 configuration scenes; in each, the code made 0 requests and the second guard alone made 0. In all 29 scenes where the control fetched, the configuration read said "partial clone". The scenes:
  - a real partial clone;
  - includes: a chain of relative includes, an include by `~`, the user's XDG file;
  - conditional includes by `gitdir:`, `gitdir/i:`, `onbranch:` and `hasconfig:remote.*.url:`, each in the repository's own file and in the user's global file;
  - worktrees: `extensions.worktreeConfig` with the promisor in the main worktree's own file, and in a linked worktree's; a linked worktree of a partial clone; a partial clone with a separate git dir;
  - remote names with dots, a space, a slash, a non-ASCII letter and an escaped quote;
  - spellings: the section and key in upper case; a key with no value; `on`, `2`, `0x1`, `1k`; false then true, and true then false; a filter that is empty or in camel case; the extension in upper case.
- **Consistent where git does not fetch.** The configuration read also says "not partial" exactly where git does not fetch:
  - a full clone;
  - a promisor set to false;
  - a worktree file without the extension (git ignores it too);
  - a full clone whose objects are also reached through an alternate, a partial clone's store (its own commit stays exempt; git does not fetch);
  - a project root in a subfolder of a partial clone (git answers nothing, so nothing is exempt and nothing is fetched).
  A partial clone with an alternate to a full store counts as partial.
- **One repository, one environment.** Both git calls get the same resolved root (also when the root is given through a link) and an identical environment. `GIT_NO_LAZY_FETCH` is `1` even when the caller set it to `0`, and the caller's `GIT_DIR` and `GIT_CONFIG_PARAMETERS` are removed.
- **A read that fails or hangs.** A configuration read that hangs (an include of a pipe nothing writes to) ends at the 10.0 s bound as "partial clone": no exemption, no request. A read that errs counts as a partial clone too (builder test and acceptance cases).
- **The second guard.** On this machine's git, the variable alone stopped the lookup's fetch in every scene where the control fetched.
- **No other git process.** The module and its two imports start only `git config --list -z`, `git cat-file --batch-check` and gitleaks.
- **What was not run.** The system file was not planted: this machine has none, and it cannot be written here. The configuration read lists the system scope, in the same environment as the lookup. No stock git before 2.43.4 was available; the controls stand in for it.
- **Real tokens still fail.** Four forms, built at run time: a bare token after each keyword, an upper-case bare token, and the prefixed form. Each is a finding of the check (in a log) and is left out by the filter (in a page), in a partial clone, a full clone and a full clone made a promisor by a global `onbranch:` include. A random hash as a folder name under the vendor keyword is a finding of the path-name judgement. The suite's six forms (K2) pass.
- **The full clone is unchanged.** The clone's own commit beside each keyword is exempt in a log, a store, a page and a folder name, with 0 requests. This repository, a linked worktree, is not taken for a partial clone (0.006 s). All 3,466 of its commits are exempt in 0.04 s; 20,000 random names take 1.0 s and none is exempt.
- **Nothing printed or written.** No output of the check, the filter or the path-name judgement holds any 40-digit hash or any token. The only new file is the record, and it holds no finding's digest. In a partial clone, no finding is recorded.
- **Time.** On 400 texts quoting a commit (20 processors, two runs each), run 1's code took 48.0 to 61.7 s and the head's 52.7 to 56.0 s: no measurable change, against a declared limit of 900 s. Only when git hangs does a text's bound grow from one 10 s git call to two, and then the text fails closed.
- **Keywords in parts.** The rule's id and both keywords appear whole in none of the 9 files run 2 changed and in none of its 4 commit messages. None of those holds a 40-digit hash.
- **Roles and tests.** c99395875f80 (the test designer) touches only `tests/acceptance/W2-71/`. 59af7377d528 (the engineer) touches only `src/gov/secrets/` and `tests/unit/secrets_check/`. The two orchestrator commits touch checkpoints only. No run-1 acceptance case was changed: the six run-1 files are untouched, the support module only gained lines, and the README lost only rows of its table.
- **Nothing left behind.** The worktree's untracked and ignored state was identical before and after the probe.

## The lead's judgement

- **Who probed.** A fresh read-only reviewer (role `independent-auditor`, session `ba8863bb-7555-4e86-bcef-33b3b05a72e5`, 2026-10-29), started through `gov launch` under its OS sandbox with the reading tools alone, at effort max; commissioned and judged by the ticket lead (an orchestrator-role session, DEC-137). This is review 2 of the ticket, the last (DEC-413), after run 2 fixed review 1's F1 (a partial clone's lazy fetch; the orchestrator's delegated decision, P1-MORNING-2026-10-29 item 4). The implementer of run 2 is the engineer session `96a38443-e7ae-4982-afdf-2fabaadc3e57`. The reviewer wrote nothing in the repository: the lead's tripwire before and after its session shows no change in this worktree.
- **Judged by `governance/project/briefs/JUDGEMENT.md` (DEC-801 to DEC-809).** The lead agrees with the reviewer's classification: no finding is "yes" with "fails open" or "loses work", so the probe passes and no round starts. F1 (a clean record kept across a clone turned promisor) joins review 1's F2 as one row (the clean record outliving what its verdict rested on). F2 (full commit hashes in tool-written files under `.gov-runtime/scratch/`, no keyword) repeats review 1's F7: a note on the tools. F3 (three settings git does not treat as a promisor turn the exemption off) fails closed and is stricter only: a note.
- **Supersedes for the close:** review 1's record `PR-DAEO-e8f0.md` probed 700102de5f4d, an ancestor of this record's probed commit, so it is of an earlier round (W2-M209); this record decides.
