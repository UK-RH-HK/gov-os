# Release 0.1.2: the owner's steps

`gov launch` without the guard and the sandbox, accepting the no-prompt mode (EMERGENCY-2.md 6.1, first row). In a
**plain terminal** (not a Claude session or a terminal started from one). About 10 minutes.

While you do this, the CTO commits nothing to `w2/integrate`: the release record's parent must be C.

## 1. Check
```
env | grep -E '^(GOV_|CLAUDECODE)'            # must print nothing; else: unset GOV_ROLE GOV_TICKET CLAUDECODE
cd /home/usain/Dynamic-Agentic-Engineering-OS
git branch --show-current                     # w2/integrate
git log -1 --format='%h %s'                   # C: "Version 0.1.2 for release 0.1.2 ..."
git status --porcelain --untracked-files=no   # must print nothing
grep -n '^version' pyproject.toml             # version = "0.1.2"
```

## 2. Build the release record
```
~/.local/bin/gov release 0.1.2
```
Type the `RELEASE-<4 digits>` code it shows and press Enter. It answers with `"version": "0.1.2"`. A `RELEASE_REFUSED`
names its reason: tell the CTO and stop.

## 3. Commit the record and tag it
```
(cd docs/releases/0.1.2 && sha256sum -c manifest.sha256)     # manifest.json: OK
git add docs/releases/0.1.2
git commit -F - <<EOF
Release 0.1.2: gov launch without the guard and the sandbox (W2-16, DEC-772; EMERGENCY-2 6.1)

Built by gov release 0.1.2 from $(git rev-parse --short=12 HEAD) on w2/integrate.

Role: owner
Task: emergency-2
Implements: DEC-772, DEC-1209
EOF
git tag -a v0.1.2 -m "Release 0.1.2"
```

## 4. Re-pin
```
bash docs/emergency-2/release-0.1.2/repin.sh 2>&1 | tee -a ~/repin-rel-0.1.2.log
```
It checks the tag and the record, builds the wheel twice and compares it with the record's sha256, installs
`pin-<C>` beside the live pin, switches `~/.local/bin/gov` atomically, checks `gov --help`, `gov launch --help` and a
search through the new link, rolls back by itself on a failed check, and commits the registry entry as yours. It ends
with `RE-PIN DONE` and prints the one-line rollback.

## 5. Optional, yours
`git push origin w2/integrate v0.1.2`

## 6. Tell the CTO "released"
The CTO then switches EXAMIN's guard off and sets its no-prompt mode (EMERGENCY-2 6.1, the EXAMIN row).
