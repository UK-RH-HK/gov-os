# Release check: Gov OS 0.1.0 (P-RELEASE-1 §5, DEC-1178 (3); W2-27's install lines)

- Release record: `docs/releases/0.1.0/manifest.json` (sha256 `120fdb868668ace2488529bb321169db2d21a8ad2ce9ff28c65d0520a5f38eec`), committed by the owner at `fc7367b29dc68e963c1578d4a48869bdf1860033` (`Role: owner`), built by `gov release 0.1.0` from C = `076cded14882b58af148f4493ccc3ed4c4f29750` on w2/integrate; the annotated tag `v0.1.0` is on the record commit, its parent C. Pushed by the owner 2026-11-15.
- The wheel reproduces: the record's wheel sha256 `f6402ee58a398fa3bda216653ff2a3ea097724cfe0ba82d0af5e2a4ccfc8eb03` was built twice from C in the re-pin's rehearsal (05:34) and again by the post-fill review's own build; all equal.
- The re-pin from the release (ACT-REPIN-REL-0.1.0, filled script sha256 `f5f8f65bdb3c…`, post-fill review READY), run by the owner in a plain terminal on 2026-11-15, ended `RE-PIN DONE: pin-076cded14882 (release 0.1.0) is live; pin-797495bdfc70 kept for the rollback; the store at 883e1ba6b152`; ALL CHECKS PASS; the registry commit `301708296`. The landing check after it: GREEN (6,551 tests, 0 failed).

## §5's two lines (measured 2026-11-15 18:31)
- The installed wheel's sha256 equals the record's: `sha256sum ~/.local/share/gov-os/wheels/076cded14882/gov-0.1.0-py3-none-any.whl` = `f6402ee58a398fa3bda216653ff2a3ea097724cfe0ba82d0af5e2a4ccfc8eb03` = `manifest.json`'s `wheel.sha256`.
- `readlink -f ~/.local/bin/gov` = `/home/usain/.local/share/gov-os/pin-076cded14882/bin/gov`.

The EXAMIN copy's kit was installed from the tag (`copier copy --vcs-ref v0.1.0`; its `governance/framework.lock` names release 0.1.0, template commit `fc7367b29dc6`; `gov doctor`'s framework_lock part MATCH, the EXAMIN CTO's report 02).
