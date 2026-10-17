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

Both forms of `gov release` run only for the orchestrator (`GOV_ROLE=orchestrator`) or the owner (`GOV_ROLE`
unset, a plain terminal); every other role, an empty one among them, is refused (DEC-761, DEC-365). The lock
always states its release: the release's version, manifest hash and manifest, or `release: null` for a template
source that never held a record; a lock that does not state it fails `gov doctor`. `gov release --lock-from`
never rewrites a lock that records a release from a source with no record, refuses a source whose git history
holds release records its tree no longer has, and refuses a lock it cannot read or that does not state its release.
