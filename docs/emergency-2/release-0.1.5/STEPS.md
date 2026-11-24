# Release 0.1.5: the owner's steps (his last manual cut, DEC-1226)

What 0.1.5 gives: **the model rubric in code** (DEC-1225: the CTO and senior engineer on Opus, every other role on
Sonnet, enforced by `gov launch`, the role files and the helper hook, which writes Sonnet into every helper spawn; leads at
medium effort, DEC-1236 (2)); **releases on your behalf, slice (a)** (W2-209: the patch rule, the gates G0 to G4 with the
update rehearsal judged by regression, `gov release --patch`, the general re-pin with its self-rollback, the push; the
authority file stays **off** until you say so after this cut); **the strict memory grading** (DEC-1227 D5: citing a stale
source makes an answer wrong; the figure stamped with release, commit, models and rule), so EXAMIN's fresh 80 on 0.1.5
is the new baseline; **no claude.ai connectors in any session** and MCP tools by role (DEC-1232 (6)); **pause stops every
starter** (N-07); **no hit@5 floor** left (N-14); `gov doctor` with a patch-only CLI/extension gap at exit 0 (D6) and
finding tools in their own folders; `gov update` leaving doctor green and adding each hook once; `gov queue`
refusing a dirty worktree; real adopted repositories land (D7, pinned by tests); W2-81's fixes; Contract 5.1 and the
Charter's release lines (DEC-1233, DEC-1235). The green base: the full suite on `0bd2945b0` with the weekly tier, 19,074 passed, 0 failed, 0 errors (`docs/close/nightly/NR-20261124T135851Z-0bd2945b04fe.json`); after it only the register gained DEC-1245 (`ff8951d85`, a record); C adds only that record, this folder and the
version line. The re-pin refreshes the stores through the new link and runs the hooks through the new pin.

In a **plain terminal** (not a Claude session or a terminal started from one). About 15 minutes (the store refreshes take a few).
While you do this, the CTO commits nothing to `w2/integrate`: the release record's parent must be C.

## 1. Check
```
env | grep -E '^(GOV_|CLAUDECODE)'            # must print nothing; else: unset GOV_ROLE GOV_TICKET CLAUDECODE
cd /home/usain/Dynamic-Agentic-Engineering-OS
git branch --show-current                     # w2/integrate
git log -1 --format='%h %s'                   # C: "Version 0.1.5 for release 0.1.5 ..."
git status --porcelain --untracked-files=no   # must print nothing
grep -n '^version' pyproject.toml             # version = "0.1.5"
```

## 2. Build the release record
```
~/.local/bin/gov release 0.1.5
```
Type the `RELEASE-<4 digits>` code it shows and press Enter. It answers with `"version": "0.1.5"`. A `RELEASE_REFUSED`
names its reason: tell the CTO and stop.

## 3. Commit the record and tag it
```
(cd docs/releases/0.1.5 && sha256sum -c manifest.sha256)     # manifest.json: OK
git add docs/releases/0.1.5
git commit -F - <<EOF
Release 0.1.5: the model rubric in code, releases on the owner's behalf (slice a), the strict memory grading, no connectors, Contract 5.1 (DEC-1225, DEC-1226, DEC-1227)

Built by gov release 0.1.5 from $(git rev-parse --short=12 HEAD) on w2/integrate.

Role: owner
Task: emergency-2
Implements: DEC-1226
EOF
git tag -a v0.1.5 -m "Release 0.1.5"
```

## 4. Re-pin
```
bash docs/emergency-2/release-0.1.5/repin.sh 2>&1 | tee -a ~/repin-rel-0.1.5.log
```
As for 0.1.3: it checks the tag and the record, builds the wheel twice against the record's sha256, installs
`pin-<C>` beside the live pin, switches `~/.local/bin/gov` atomically, checks it (now also the five hooks through the
new pin), rolls back by itself on a failed check, commits the registry entry as yours, then rebuilds the two stores
through the new link (a failed rebuild keeps the pin and says so). It ends with `RE-PIN DONE` and prints the one-line
rollback.

## 5. Optional, yours
`git push origin w2/integrate v0.1.5`

## 6. Tell the CTO "released"
The CTO then: turns the authority file on (a decision-record commit carrying your standing approval, DEC-1223, DEC-1226,
DEC-1235) and tells you; writes its handover, so you can set `autoMemoryReclaim=dropCache` in `.wslconfig` and restart WSL
(DEC-1233 (8)); the EXAMIN CTO runs `gov update` to 0.1.5 in EXAMIN's copy and its fresh 80 on the strict grading; Gov
OS enters the integration emergency (DEC-1238 (3)).
