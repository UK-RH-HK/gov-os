# Release 0.1.3: the owner's steps

What 0.1.3 gives EXAMIN (EMERGENCY-2 §6.1, §7.6): `gov update` and the pinned install (W2-17, W2-18), the product close
without repair tickets or a review gate (W2-193, W2-194), `gov queue` with DONE as the green landing (W2-115b), memory
by construction and the memory-use log (W2-197), `gov discover` (W2-36), `gov backup` / `gov memaudit scan` /
`gov decisions basis` (W2-198), the run-time tool's first slice (`gov msg`, `gov dispatch watch`), and the launcher's
no-prompt default. No store rebuild (no store or rebuild code changed since 0.1.2).

In a **plain terminal** (not a Claude session or a terminal started from one). About 10 minutes.
While you do this, the CTO commits nothing to `w2/integrate`: the release record's parent must be C.

## 1. Check
```
env | grep -E '^(GOV_|CLAUDECODE)'            # must print nothing; else: unset GOV_ROLE GOV_TICKET CLAUDECODE
cd /home/usain/Dynamic-Agentic-Engineering-OS
git branch --show-current                     # w2/integrate
git log -1 --format='%h %s'                   # C: "Version 0.1.3 for release 0.1.3 ..."
git status --porcelain --untracked-files=no   # must print nothing
grep -n '^version' pyproject.toml             # version = "0.1.3"
```

## 2. Build the release record
```
~/.local/bin/gov release 0.1.3
```
Type the `RELEASE-<4 digits>` code it shows and press Enter. It answers with `"version": "0.1.3"`. A `RELEASE_REFUSED`
names its reason: tell the CTO and stop.

## 3. Commit the record and tag it
```
(cd docs/releases/0.1.3 && sha256sum -c manifest.sha256)     # manifest.json: OK
git add docs/releases/0.1.3
git commit -F - <<EOF
Release 0.1.3: gov update, the product close and gov queue, memory by construction (EMERGENCY-2 6.1, 7.6)

Built by gov release 0.1.3 from $(git rev-parse --short=12 HEAD) on w2/integrate.

Role: owner
Task: emergency-2
Implements: DEC-1211
EOF
git tag -a v0.1.3 -m "Release 0.1.3"
```

## 4. Re-pin
```
bash docs/emergency-2/release-0.1.3/repin.sh 2>&1 | tee -a ~/repin-rel-0.1.3.log
```
As for 0.1.2: it checks the tag and the record, builds the wheel twice against the record's sha256, installs
`pin-<C>` beside the live pin, switches `~/.local/bin/gov` atomically, checks it, rolls back by itself on a failed
check, and commits the registry entry as yours. It ends with `RE-PIN DONE` and prints the one-line rollback.

## 5. Optional, yours
`git push origin w2/integrate v0.1.3`

## 6. Tell the CTO "released"
The CTO then has the EXAMIN CTO run `gov update` in EXAMIN's copy (no re-adoption, §7.6) and reports what it changed.
