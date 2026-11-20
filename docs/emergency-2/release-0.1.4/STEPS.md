# Release 0.1.4: the owner's steps

What 0.1.4 gives (EMERGENCY-2 §8.2 items 2 and 3): the memory measure on any adopted repository, so EXAMIN can run its
fresh 80 (W2-204); `gov update` that keeps only the `git push` and `sudo` deny lines and takes the legacy lines out, and
the golden rules at the head of an adopted repository's CLAUDE.md and AGENTS.md (W2-17's fix, DEC-1217 (6), (7));
`gov launch --fix` / `--chore` and a fix under a closed ticket landing through `gov queue` (W2-201's fix, DEC-1219 (5));
the landing and close as one action's first parts (W2-202, W2-206); the run-time tool's slices 2 and 3 (W2-199, W2-205);
the rubric in code (W2-201); `gov context` retired (W2-200); the register's exit (W2-203); Charter v6 and Contract v5
(DEC-1219). The green base: the full suite on `e74765954` with the weekly tier, 18,086 passed, 0 failed
(`docs/close/nightly/NR-20261119T201400Z-e74765954452.json`); C adds only that record, this folder and the version line.
The re-pin rebuilds the stores through the new link (0.1.4 changes the store loader) and runs the five hooks through the
new pin.

In a **plain terminal** (not a Claude session or a terminal started from one). About 15 minutes (the store rebuilds take a few).
While you do this, the CTO commits nothing to `w2/integrate`: the release record's parent must be C.

## 1. Check
```
env | grep -E '^(GOV_|CLAUDECODE)'            # must print nothing; else: unset GOV_ROLE GOV_TICKET CLAUDECODE
cd /home/usain/Dynamic-Agentic-Engineering-OS
git branch --show-current                     # w2/integrate
git log -1 --format='%h %s'                   # C: "Version 0.1.4 for release 0.1.4 ..."
git status --porcelain --untracked-files=no   # must print nothing
grep -n '^version' pyproject.toml             # version = "0.1.4"
```

## 2. Build the release record
```
~/.local/bin/gov release 0.1.4
```
Type the `RELEASE-<4 digits>` code it shows and press Enter. It answers with `"version": "0.1.4"`. A `RELEASE_REFUSED`
names its reason: tell the CTO and stop.

## 3. Commit the record and tag it
```
(cd docs/releases/0.1.4 && sha256sum -c manifest.sha256)     # manifest.json: OK
git add docs/releases/0.1.4
git commit -F - <<EOF
Release 0.1.4: the memory measure for adopted repositories, the kit after Emergency 2, fixes under closed tickets, Contract v5 (EMERGENCY-2 8.2, 8.3)

Built by gov release 0.1.4 from $(git rev-parse --short=12 HEAD) on w2/integrate.

Role: owner
Task: emergency-2
Implements: DEC-1217
EOF
git tag -a v0.1.4 -m "Release 0.1.4"
```

## 4. Re-pin
```
bash docs/emergency-2/release-0.1.4/repin.sh 2>&1 | tee -a ~/repin-rel-0.1.4.log
```
As for 0.1.3: it checks the tag and the record, builds the wheel twice against the record's sha256, installs
`pin-<C>` beside the live pin, switches `~/.local/bin/gov` atomically, checks it (now also the five hooks through the
new pin), rolls back by itself on a failed check, commits the registry entry as yours, then rebuilds the two stores
through the new link (a failed rebuild keeps the pin and says so). It ends with `RE-PIN DONE` and prints the one-line
rollback.

## 5. Optional, yours
`git push origin w2/integrate v0.1.4`

## 6. Tell the CTO "released"
The CTO then restarts the EXAMIN CTO on Opus, which runs `gov update` to 0.1.4 in EXAMIN's copy (no re-adoption, §7.6),
then its fresh 80 (release acceptance item 3); and the CTO starts W2-81's proving run on Sonnet (item 2).
