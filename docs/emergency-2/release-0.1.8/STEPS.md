# Release 0.1.8: the owner's steps (a bigger release, built by his hand: DEC-1254 E-03)

What 0.1.8 gives: **D3** (W2-212: stale and superseded documents kept out of default memory; adoption's A3 refuses only a namespace
stale as a whole, a mixed one gets a notice, DEC-1254 E-02) and **`gov memaudit forbidden-reach`** (the measure's own count of whether
an audit's cited forbidden sources are now outside default memory), which EXAMIN's next measure needs; **the lite adoption verdict**
(W2-210); **the escalation rubric's first slice** (W2-211); **usage per repository** (W2-207 UR); **models and effort by role in every
repository through the kit** (the model hook, `defaultMode`); **the fresh 80's launch lines for every kind and the writer check's record in
the session folder** (I-33, I-37, I-38); **the trustworthy selection** (1-0, 1-8 `gov impact` bounded, 1-9 the impact trace at the landing,
1-11 (c) the path map's exact coverage at the landing, 1-13 node on the test run's PATH); **the timing tests judged by the work under test**
(I-32); **the release rule for approved releases** (I-34: from 0.1.9 the CTO cuts an approved release by code); **W2-213's first slice** (DEC-1256 (1): the standard frozen in the kit, `standard.yaml`, and `gov layout check`, which EXAMIN and ASMO OS run on their restructure plans before anything moves); **the model hook writes the alias `sonnet`** (I-50: a role-typed helper spawn no longer fails); the CTO's card 2.0.1.

**The green base:** the full suite on `147b6ee1c` with the weekly tier, **20,350 passed, 0 failed, 0 errors** (record
`docs/close/nightly/NR-20261126T162755Z-147b6ee1c7c7.json`, committed in C). C adds only that record and this file to the tested commit.
The re-pin refreshes the stores through the new link and runs the six hooks (the model hook is new) through the new pin.

In a **plain terminal** (not a Claude session or a terminal started from one). About 15 minutes (the store refreshes take a few).
While you do this, the CTO commits nothing to `w2/integrate`: the release record's parent must be C.

## 1. Check
```
env | grep -E '^(GOV_|CLAUDECODE)'            # must print nothing; else: unset GOV_ROLE GOV_TICKET CLAUDECODE
cd /home/usain/Dynamic-Agentic-Engineering-OS
git branch --show-current                     # w2/integrate
git log -1 --format='%h %s'                   # C: "Version 0.1.8 for release 0.1.8 ..."
git status --porcelain --untracked-files=no   # must print nothing
grep -n '^version' pyproject.toml             # version = "0.1.8"
```

## 2. Build the release record
```
~/.local/bin/gov release 0.1.8
```
Type the `RELEASE-<4 digits>` code it shows and press Enter. It answers with `"version": "0.1.8"`. A `RELEASE_REFUSED` names its
reason: tell the CTO and stop.

## 3. Commit the record and tag it
```
(cd docs/releases/0.1.8 && sha256sum -c manifest.sha256)     # manifest.json: OK
git add docs/releases/0.1.8
git commit -F - <<EOF
Release 0.1.8: D3 and forbidden-reach for EXAMIN's measure, the lite verdict, the escalation slice, usage per repository, models by role through the kit, the trustworthy selection, releases by code from 0.1.9 (DEC-1254 E-03)

Built by gov release 0.1.8 from $(git rev-parse --short=12 HEAD) on w2/integrate.

Role: owner
Task: emergency-2
Implements: DEC-1254
EOF
git tag -a v0.1.8 -m "Release 0.1.8"
```

## 4. Re-pin
```
bash docs/emergency-2/release-0.1.8/repin.sh 2>&1 | tee -a ~/repin-rel-0.1.8.log
```
As for 0.1.7: it checks the tag and the record, uses the kept cut wheel of C (its sha256 equal to the record's), installs `pin-<C>`
beside the live pin, switches `~/.local/bin/gov` atomically, checks it (help, launch, a search on both facets, the six hooks through the
new pin), rolls back by itself on a failed check, commits the registry entry as yours, then rebuilds the two stores through the new link
(a failed rebuild keeps the pin and says so). It ends with `RE-PIN DONE` and prints the one-line rollback.

## 5. Optional, yours
`git push origin w2/integrate v0.1.8`

## 6. Tell the CTO "released"
The CTO then tells the EXAMIN and ASMO OS CTOs that 0.1.8 is pinned (EXAMIN: `gov update 0.1.8`; its restructure waits for W2-213's
slice 1, then `forbidden-reach` before its fresh pair, DEC-1256), installs the commit-time role hook in Gov OS only when batch B lands
(0.1.9), and goes on with batch B.
