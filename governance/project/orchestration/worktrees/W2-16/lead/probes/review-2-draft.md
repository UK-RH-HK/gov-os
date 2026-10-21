---
type: probe
task: DAEO-49o5
reviewer_session: d4a25f19-6229-43e3-9a4a-2b05c895d601
implementer_session: af1b2b85-e84c-4484-b19a-14e15f3a2076
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: eda494aeb5438c4f4f05de093b7564a68b8ccbed
---

# Probe of DAEO-49o5 (W2-16) at eda494ae: second and last review (DEC-413), DRAFT, judgement fail

This draft is not committed (DEC-733): the review failed. It is the second and last reviewer pass, so there is no third review in this run.

The reviewer was rev-2 (independent-auditor), session d4a25f19-6229-43e3-9a4a-2b05c895d601. It was read-only, and its `git status --porcelain` was empty. It ran its probes in `/tmp/w216probe.zM5L`.

## Findings

```yaml
probed_commit: eda494aeb5438c4f4f05de093b7564a68b8ccbed
judgement: fail
findings:
  - id: R2-F1
    severity: HIGH
    fail_open: true
    writes_outside_scope: true
    behaviour: "In an installed project, `gov release --lock-from <any folder with no docs/releases records>` rewrites governance/framework.lock from the kernel as installed, edits included, with no release block. Doctor's framework_lock goes from DRIFT (fail, exit 3) to MATCH (pass). The guard allows the command for engineer and independent-auditor, while it denies the same role a Write or a redirect to the lock. Neither the guard nor the CLI enforces ACT_PATHS. Reproduced as GOV_ROLE=engineer; the guard verdict came from calling decide() directly."
  - id: R2-F2
    severity: MEDIUM
    fail_open: true
    behaviour: "Deleting the lock's release block leaves doctor at MATCH. The deletion plus one file-hash edit hides a kernel edit. This is the first review's F2, still open. A full forgery is the unsigned limit (CAP-02.c, Wave 3); the block deletion alone could be caught without signatures."
  - id: R2-F3
    severity: MEDIUM
    fail_open: true
    behaviour: "A source with no docs/releases records installs any ref unverified, even a v<semver> tag. (a) The owner tags the commit the manifest names rather than the record-holding commit: the first release installs unhashed and doctor passes. (b) A source whose records were removed and whose kernel was edited, tagged v1.1.0, installs and passes. This is the first review's F3 and P-A, still open."
  - id: R2-F4
    severity: MEDIUM
    fail_open: false
    behaviour: "On a project installed before this change, doctor gives ERROR (fails closed). The remedy `copier update --trust` exits 0 but leaves framework.lock with conflict markers (UU), and doctor then gives ERROR 'not a readable map'. A manual step is needed."
  - id: R2-F5
    severity: LOW
    fail_open: false
    behaviour: "A refused `copier update` (tampered release) exits 1 but leaves the tampered kernel file and the changed answers file in the tree. Doctor gives DRIFT; it can be recovered with git."
  - id: R2-F6
    severity: LOW
    fail_open: false
    behaviour: "copier.yml is not in the manifest, and no file modes are recorded. A changed copier.yml at a release tag installs (later caught by doctor). Emptying the executables list needs a lock edit."
  - id: R2-F7
    severity: LOW
    fail_open: false
    behaviour: "A version counts as known only through records in history or a tag named v<V> or <V>. A tag such as release-1.0.0, with no record in history, lets 1.0.0 be built again."
```

## Found sound (run, not read)

- **Refused builds:**
  - dirty, staged or untracked trees;
  - a HEAD that is not on w2/integrate, and a repository with no w2/integrate;
  - a version already known: in the tree, removed later, an older HEAD, build metadata, a bare tag;
  - an uncommitted record;
  - invalid versions.
- **Every git step that fails refuses the build.**
- **Commit bytes are hashed under assume-unchanged and skip-worktree.**
- **No tag, no signature, no write outside `docs/releases/<version>/`, and no partial record.**
- **copy and update refuse:**
  - a changed, added or removed file;
  - a wrong manifest.sha256;
  - a non-release ref of a source that has records.
- **Doctor fails** with `--skip-tasks`, after a direct copy of template/, or when the lock, the answers file or both are deleted.
- **Doctor on this repository:** framework_lock is unmeasured, not red.
- **Suites:** W2-16 85 passed; unit lock and release 50 passed.

## Packages from this review

- **R2-P1:** may `gov release --lock-from` run outside a Copier task, and may it drop the release block? The reviewer recommends refusing it when the project's lock already records a release or when the source has no record (medium-high).
- **R2-P2:** the owner tags the record-holding commit, not the commit the manifest names (high).
