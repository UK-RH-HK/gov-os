# P-RELEASE-2: release 0.1.1 and its re-pin (your sitting)

**Ready 2026-11-16 08:1x: the bundle is reviewed (READY, narrow re-check READY); section 4 is its rehearsed steps.**

## 1. What 0.1.1 is for
0.1.0 (C `076cded14882`, re-pinned ~17:00 on 11-15) is what EXAMIN's copy and W2-81's six adoptions ran on overnight.
They met four product defects, now fixed and landed on `w2/integrate`:

| Ticket | What 0.1.1 fixes | Met by |
|---|---|---|
| W2-88 S29 (DAEO-2bdu) | the wheel ships `template/.gitleaks.toml` and A9's kernel sources, so A0 and A9 work from an installed release | W2-81: A0 exit 1 in all six (DEC-1189 (1)) |
| W2-174 (DAEO-zmo4) | the Verify pass also writes the launch fields `tk` cannot (role, allowed_paths, kpis, …), and the wheel ships the ticket and common schemas | EXAMIN F-011, F-018 (your operator wrote them by hand: DEC-1188) |
| W2-153 (DAEO-8s85) | `gov adapters generate` writes `.claude/templates/` in an adopted repository; doctor names a missing copy | W2-81 and EXAMIN: A5 `LAUNCH_NO_TEMPLATE` (DEC-1192) |
| W2-111 (DAEO-qvff) | the guard hook's import cut (S9), the live-hook diff for ACT-GUARD-FIX-7 (S10), malformed YAML fails closed | DEC-1187, P-W2-111-YAML-REST |
| W2-190 (DAEO-6oj6, landed ef4d79693 this morning) | A3 refuses deleting a file another tracked file names (`DELETE_REFERENCED`) or one classed superseded (`DELETE_SUPERSEDED`) | W2-81: secret-history's two MISHANDLED deletes (DEC-1197 (2)(ii)) |
| W2-189 (DAEO-kfn1, landed 933e5020b this morning) | `gov retrieve` (and `gov context`, which calls it) answers from the last good store when HEAD has moved, naming its commit, the head and the stale paths (walled ones counted, not named) | W2-81: five stale stores served nothing (DEC-1197 (2)(i)) |

Also in since 0.1.0: W2-178 (the auditor's copy of a set without its dropped questions), W2-60a (role, skills, model and
effort loaded at launch; the launch record), W2-94's re-anchor flow, W2-88 S27 (folder mode). In all: 11 merges (with W2-190 and W2-189), 28 files
under `src/` and `pyproject.toml` (adopt 4, guard 3, adapters 3, the shipped template 7, util 2, doctor 1, secrets 1),
no kernel file. Every one landed through the merge queue with its review.

**Not in 0.1.1:** anything that lands after I say "release ready at C" (the hold). W2-60b (started 05:34) and W2-15a's
records land after the re-pin.

## 2. The version: (a) raise it to 0.1.1, or (b) keep the CLI at 0.1.0
`gov release` takes the manifest's `cli_version` from `pyproject.toml` (`src/gov/release/__init__.py:183`); it does not
compare it with the release's own number. `pyproject.toml` says 0.1.0.
- **(a) Recommended.** Your first step is one commit of yours that changes `pyproject.toml`'s `version` to `0.1.1`;
  C is that commit. The wheel is `gov-0.1.1-…whl`, `gov --version` says 0.1.1, and W2-81's re-run and EXAMIN can tell the
  two releases apart by the number. The two unit suites that read the version read `pyproject.toml` at run time
  (`tests/unit/cli/test_w2_59_version.py:17`, `tests/unit/release/test_release.py`); no test fixes it at 0.1.0.
  Cost: one more command in your sitting.
- **(b)** Release 0.1.1 with `cli_version` 0.1.0 and the wheel `gov-0.1.0-…whl`. Only the manifest's wheel sha256 tells
  the two apart. Cost: none now; confusion at every later read.

## 3. The hold
From my message "release ready at C" until you say "done" after the re-pin, nothing lands or is committed on
`w2/integrate` but your bump, your record commit and your registry commit (memory rule; RL-3). Leads keep running;
their lands wait. I write `log/act-in-progress.txt` at the hand-over.

## 4. Your steps (copied word for word from the reviewed bundle README part 1, BUNDLE.sha256 54e1a619 (review READY; narrow re-checks READY at dd201943 and at 54e1a619 for D18-D20); review READY, narrow re-check READY)

1. Open a plain terminal.
   ```
   env | grep '^GOV_'          # must print nothing; if it prints, run: unset GOV_ROLE GOV_TICKET
   ```
2. Check the checkout:
   ```
   cd /home/usain/Dynamic-Agentic-Engineering-OS
   git branch --show-current                     # w2/integrate
   git rev-parse HEAD                            # the H the CTO named
   git status --porcelain --untracked-files=all  # must print nothing
   grep -n '^version' pyproject.toml             # 7:version = "0.1.0"
   ```
3. Raise the version to 0.1.1 in one commit of yours (this commit is C):
   ```
   sed -i 's/^version = "0.1.0"$/version = "0.1.1"/' pyproject.toml && git add pyproject.toml && git commit -q -F - <<'EOF'
   Version 0.1.1 for release 0.1.1 (P-RELEASE-2)

   Role: owner
   Task: DAEO-sdxk
   Implements: DEC-772, DEC-1089
   EOF
   git show --stat HEAD | tail -2                # 1 file changed, 1 insertion(+), 1 deletion(-): pyproject.toml
   git log -1 --format='%(trailers)'             # the three lines
   ```
   - It passes the landing check (`Role: owner`; checked in the rehearsal: `landing_check.py` prints `[]`).
   - The tests that read the version read `pyproject.toml` at run time (`tests/unit/cli/test_w2_59_version.py`; the
     release tests use their own fixtures), so no test changes with it.
4. Build:
   ```
   ~/.local/bin/gov release 0.1.1
   ```
   - It shows `type RELEASE-<4 digits> to build release 0.1.1:`. Type that code and press Enter.
   - It answers with `"version": "0.1.1"` and the record's path.
   - A `RELEASE_REFUSED` names its reason. Tell the CTO, and do nothing else.
5. Check the record:
   ```
   (cd docs/releases/0.1.1 && sha256sum -c manifest.sha256)   # manifest.json: OK
   git status --porcelain                                       # only: ?? docs/releases/0.1.1/
   ```
6. Commit it, with the trailers in ONE final paragraph. The message fills C itself (HEAD is C at this step); the
   decision number `DEC-1198` is filled here (DEC-1198: the decision I record from your P-RELEASE-2 line; if another decision takes that number first, I correct it in this page when I say "release ready"), the same number the re-pin is
   filled with, and the re-pin stops (part R) unless the record commit names that C and that decision:
   ```
   git add docs/releases/0.1.1
   git commit -F - <<EOF
   Release 0.1.1: the record of the second numbered, frozen release (W2-16, DEC-772)

   Built by gov release 0.1.1 from $(git rev-parse --short=12 HEAD) on w2/integrate.

   Role: owner
   Task: DAEO-sdxk
   Implements: DEC-772, DEC-1089, DEC-1198
   EOF
   git log -1 --format='%B' | grep '^Built by'   # Built by gov release 0.1.1 from <C, 12 digits> on w2/integrate.
   git log -1 --format='%(trailers)'             # shows the three lines, the decision filled
   ```
7. Tag **the record commit**, the one you just made:
   ```
   git tag -a v0.1.1 -m "Release 0.1.1 (W2-16)"
   git rev-parse 'v0.1.1^{commit}' HEAD          # the same id twice
   git rev-parse HEAD^                           # C, your version bump commit
   ```
8. Optional, yours, as usual (DEC-1087 (7)): `git push origin w2/integrate v0.1.1`.
9. Tell the CTO "released". It fills part 2 from the tag and gives you its line.

**Option (b), no version bump (rehearsed as mode `opt-b`):** skip step 3. C is then the head H the CTO named, the
record's `cli_version` and wheel name stay 0.1.0 (`gov-0.1.0-py3-none-any.whl`), and the CTO fills part 2 with
`--cli 0.1.0`. Steps 1, 2 and 4 to 9 are the same commands (step 2's `grep` still shows 0.1.0; step 7's `HEAD^` is H).

## 5. The re-pin (your operator, plain terminal, about 5 minutes)
At "released" I run `fill_release.sh --c <C> --repo /home/usain/Dynamic-Agentic-Engineering-OS --dec DEC-1198` (it
refuses unless the tag, the record and the record commit's message all agree), rehearse the filled script at the real C
on a mirror, have the filled bytes reviewed, then give your operator one line: the bundle's sha256 check first, then the
script with both targets named (`--home /home/usain --repo /home/usain/Dynamic-Agentic-Engineering-OS`; DEC-1196 (5)).
It installs `pin-<C>` beside pin-076cded14882, rebuilds the store, runs the checks, switches `~/.local/bin/gov`
atomically and rolls back by itself on a failed check. Rollback line (yours, if anything goes wrong after the switch):
`ln -sfn ~/.local/share/gov-os/pin-076cded14882/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov; hash -r`

## 6. After it
- I end the hold, add the two release-check lines to `docs/plan/wave-2/examin-copy/release-check.md`, and check the
  registry commit refreshed the store with the new pin.
- W2-81's full re-run on 0.1.1 (DEC-1197 (3)) with the corrected adopter brief, a LITE ticket cycle per repository,
  and the judge's stage-list fix if it has landed.
- EXAMIN's copy: **(i) recommended:** it stays on 0.1.0 until its adoption run ends (its 0.1.0 workarounds are already
  committed by your operator; no mid-run swap); **(ii)** re-install 0.1.1 into it now (a setup job; its A0 to A10 records
  were made on 0.1.0).

## 7. Your lines
`P-RELEASE-2 (a)` or `(b)`; `EXAMIN (i)` or `(ii)`; then, at the sitting, the steps of section 4 and "released".
