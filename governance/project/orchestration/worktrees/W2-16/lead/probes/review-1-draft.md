# Draft (failing) probe record, review 1, reviewer session 4e9603df-f0aa-44bb-a85d-2fc0285b99cb

My judgement is **fail**. The main reason is that a release version can be built a second time from a different commit, which the immutability KPI says must be refused. I changed nothing: the worktree is clean and the head is still `38c8f1bbcdcd805c37b3eaccf8567f2b1b9ed481`.

task: Probe W2-16 (DAEO-49o5) at head 38c8f1bb for behaviour its acceptance tests miss, without writing anything.
status: DONE, probes complete; one HIGH finding where a gate fails open, so the judgement is fail.
work_completed: Checked role, ticket, worktree, branch and head; all matched. Read the ticket, the diff from 846d75e1, the test README and the origin lines 1965–1980. Built a stand-in Gov OS repository and projects in `/tmp/tmp.C7FmV1TjFd`, using `w2_16_support` helpers, single named files only. Ran `gov release`, `copier copy` and `copier update` (9.18.2) and `gov doctor` against this worktree's `src/`. Ran the unit, W2-16 and W1-39 suites, and `gov doctor` on this repository.
files_changed: none
evidence: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -c "import gov; print(gov.__file__)"` printed `/home/usain/gov-os-worktrees/W2-16/src/gov/__init__.py`. Results of each probe are below. `git status --porcelain` was empty at the end, and HEAD was still 38c8f1bbcdcd805c37b3eaccf8567f2b1b9ed481.
tests: unit tests in `tests/unit/lock` and `tests/unit/release`: 45 passed. `tests/acceptance/W2-16`: 75 passed. `tests/acceptance/W1-39`: 70 passed, 1 failed. The failure is `test_a_project_with_neither_lock_nor_answers_file_stays_unmeasured`, the red already recorded as package P-1 in the test README.
discoveries: (1) The immutability check only looks at the checked-out tree, so a version can be rebuilt from another commit. (2) Deleting the lock's `release` key brings back the W2-H029 silencing. (3) A source with no release record installs without verification, and doctor still passes. (4) A file marked `--assume-unchanged` gets past the clean-tree check. Details are in the narrative.
risks: Two backstops outside the code still stand against finding 1: git refuses to recreate an existing `v<version>` tag without `-f`, and a merge of a second record for the same version would conflict. Neither is enforced by `gov release`.
lessons: In this setup, many worktrees sit on commits that `w2/integrate` already contains but that predate later records. The immutability check therefore has to read `w2/integrate` and the tags, not the working tree.
proposed_decisions: P-A: should the "tag the release commit" wording mean the commit that holds the record, or the commit the manifest names? Today they differ, and nothing checks the manifest's `commit` against the commit being installed. I recommend the record-holding commit, with a check that the manifest's commit is its parent and has the same `template/` tree; confidence medium. P-B: should the lock comparison require a `release` entry when the answers file names a `v<semver>` tag? I recommend yes, as a cheap close of finding 2 within the lite design; confidence medium.
unresolved: Finding 1 (HIGH) needs a repair round by the engineer. Findings 2 and 3 need the owner or the lead to decide whether they belong to this ticket or are residuals until CAP-02.c in Wave 3. The W1-39 P-1 case is still pending, as already known.
recommended_next_action: Send finding 1, with findings 2 to 4, to the engineer for a repair round, then re-probe.

```yaml
probed_commit: 38c8f1bbcdcd805c37b3eaccf8567f2b1b9ed481
judgement: fail
findings:
  - severity: HIGH
    fail_open: true
    behaviour: >
      gov release <version> refuses a version only if docs/releases/<version>/ exists in the checked-out tree.
      Release 1.4.0 was built at commit c0b, recorded at c1 on w2/integrate and tagged v1.4.0. Then
      `gov release 1.4.0` was run on a detached checkout of the older ancestor c0. It exited 0 and wrote a new
      record naming commit c0. In a second repository, deleting the record in a later commit and rebuilding
      1.4.0 from a new commit also exited 0, while tag v1.4.0 already existed. It should have been refused
      ("building the same version from another commit is refused", CAP-43): the record on w2/integrate, the
      record in history and the existing tag v<version> are all unchecked. No work is lost and nothing is
      written outside scope, but the immutability gate fails open.
  - severity: MEDIUM
    fail_open: true
    behaviour: >
      Project installed by copier copy from v1.4.0; doctor passed. A kernel file and its hash in the lock's
      manifest were edited together: DRIFT, as the W2-H029 case expects. When the lock's `release` key was
      also deleted, doctor reported MATCH and pass, although .copier-answers.yml still says _commit: v1.4.0.
      The comparison treats the release entry as optional and never ties it to the answers file. This
      variant could be caught without a signature. Rewriting the lock's manifest, the embedded release
      manifest and its sha256 together also gives MATCH; that cannot be caught until CAP-02.c (Wave 3), as
      the README says.
  - severity: MEDIUM
    fail_open: true
    behaviour: >
      A commit with no docs/releases/ was tagged v9.9.9 and installed with copier copy. It exited 0, wrote a
      lock without a release entry, and doctor passed. Any install from a source or ref without a release
      record skips verification without a word, and a product repository cannot tell it from a verified
      install. If the owner tags the commit the manifest names (one reading of "the release commit"), the
      first release installs unverified and later releases are refused. verify() never checks the manifest's
      `commit`.
  - severity: LOW
    fail_open: true
    behaviour: >
      A template file was marked `git update-index --assume-unchanged` and edited. `git status` was clean and
      `gov release 1.5.0` exited 0. The manifest hashed the edited working-tree bytes, not the committed blob
      (they differ). An install from the tag would then be refused, but a release was recorded from a tree
      that was not clean, and its version is used up.
  - severity: LOW
    fail_open: false
    behaviour: >
      `gov release 1.4.0+build.2` was accepted beside an existing 1.4.0: two records with equal semver
      precedence.
  - severity: LOW
    fail_open: false
    behaviour: >
      A project whose lock lacks `executables` and `folders` (the W1-39 format, simulated by removing those
      keys) now gets framework_lock fail with ERROR "lacks executables or folders". It fails closed, but the
      reason does not name the fix (copier update).
  - severity: LOW
    fail_open: false
    behaviour: >
      docs/releases/README.md says shipped files are listed "by path as a project sees it", but the manifest
      keys them by template path, including .jinja suffixes (lefthook.yml.jinja, .copier-answers.yml.jinja,
      .github/workflows/ci.yml.jinja). The lock comparison is unaffected because these files are outside the
      shipped paths.
```

### What I probed and found sound
- **Dirty tree and branch:** a release from a dirty tree (tracked, staged or untracked changes) or from a commit not on `w2/integrate` is refused; the acceptance tests cover this. The only gap is finding 4.
- **Partial records:** a refused build (vendored licence removed) left nothing behind; `git status --porcelain --ignored` was empty.
- **No tag, no signature:** `gov release` creates no tag. The code has no tag or sign call, and the tests cover it.
- **Writes outside the record:** by reading, the build writes only `docs/releases/<v>/`; the wheel is built in a temporary folder.
- **Install from a non-release ref when records exist:** `copier copy --vcs-ref w2/integrate` and `--vcs-ref HEAD` (both describe as `v1.4.0-N-g…`) were refused. Copier removed the new destination.
- **Refused copy into an existing folder:** the user's file was kept, and the kernel was left without a lock. Doctor reported UNLOCKED, fail, so a missing lock does not pass on this path.
- **Refused `copier update` to an unreleased ref:** exit 1, the old lock stays, and doctor reports DRIFT naming the file and the tag mismatch. The changes are in the committed project's working tree and can be reverted with git, so no work is lost.
- **`copier update` with a local kernel edit:** the lock records 1.5.0, and doctor reports DRIFT naming the edited file.
- **Tampering caught:** kernel file plus lock manifest edited with the release entry kept gives DRIFT. A wrong embedded manifest hash gives ERROR. File changed, added or removed after release, and a wrong manifest hash, are all refused by copy, update and doctor (acceptance tests).
- **Doctor on this repository:** framework_lock is unmeasured (MISSING, "no framework.lock"); there is no root kernel, lock or answers file. Doctor's overall failure comes from other parts: tools, path_compliance, index_freshness and claude_code.
- **Cannot be caught by design:** a record rewritten consistently with a changed file in a later commit, with the tag moved, was accepted by copy and passed doctor. This is the unsigned lite limit (CAP-02.c, Wave 3).

### Narrative
The most serious hole is finding 1. In this project, many worktrees sit on commits that `w2/integrate` already contains but that predate a later release record, so a rebuild from a stale checkout is ordinary rather than exotic. That is why I judge **fail**. The only things standing in the way today are the owner's tag (git refuses an existing tag without `-f`) and a merge conflict between two records for the same version; `gov release` itself checks neither. Findings 2 and 3 reopen the silencing and verification gaps in cheap ways that the unsigned design could still catch. The owner or lead should decide whether they belong to this ticket or stay as residuals until CAP-02.c. The rest of the probed behaviour holds.