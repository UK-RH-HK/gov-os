# Releases (W2-16, CAP-43.b lite, DEC-722)

Each folder `docs/releases/<version>/` is the record of one release, written by `gov release <version>` from a
clean commit that `w2/integrate` contains, and never written again (a version that has a record is refused):

- `manifest.json`: the semantic version and the full commit; every file under `template/` (by its path as a
  project sees it) with its sha256; the gov wheel's name and sha256; the CLI version (`pyproject.toml`); the
  schema versions (each kernel schema's sha256, as schemas carry no version of their own); the vendored skills'
  version and upstream licence; release notes.
- `manifest.sha256`: the manifest's own hash, in `sha256sum` form.

`gov release` neither commits, tags nor signs. The owner commits the record and tags the release commit
`v<version>`, unsigned (CAP-02.c stays in Wave 3). The template's Copier task (`gov release --lock-from`)
verifies the tagged release against these hashes, refuses one that does not match, and records the release's
version and manifest hash in the project's `governance/framework.lock`, which `gov doctor` compares.

`gov release <version>` is the owner's alone (DEC-772). The owner's procedure:

1. Open a plain terminal, outside any Claude Code session (not a terminal started from one, nor the operator
   console), with neither `GOV_ROLE` nor `GOV_TICKET` set, to any value (`env | grep '^GOV_'` shows nothing).
2. In a clean checkout of a commit that `w2/integrate` contains, run `gov release <version>`.
3. It shows `type RELEASE-<4 digits> to build release <version>:`; type that code back and press Enter.
4. Commit the record under `docs/releases/<version>/` and tag the release commit `v<version>`, unsigned.

Before anything is read or written, it refuses (`RELEASE_REFUSED`, with `reason`) a Claude Code session among its
ancestor processes (`session`), a chain of ancestors it cannot read whole up to the system's first process
(`ancestry`), `GOV_ROLE` set (`role`) or `GOV_TICKET` set (`ticket`), and an input or output that is not a terminal
(`terminal`); the code is shown only after those checks, and a wrong code, an empty line or the end of input refuses
(`code`). The lock task, `gov release --lock-from`, runs inside `copier copy` and `copier update`, and runs only for
the orchestrator (`GOV_ROLE=orchestrator`) or the owner (`GOV_ROLE` unset); every other role, an empty one among
them, is refused (DEC-761, DEC-365). The lock
always states its release: the release's version, manifest hash and manifest, or `release: null` for a template
source that never held a record; a lock that does not state it fails `gov doctor`. `gov release --lock-from`
never rewrites a lock that records a release from a source with no record, refuses a source whose git history
holds release records its tree no longer has, and refuses a lock it cannot read or that does not state its release.
