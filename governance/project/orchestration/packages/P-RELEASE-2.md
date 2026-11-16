# P-RELEASE-2: release 0.1.1 and its re-pin (your sitting)

**DRAFT 2026-11-16 05:4x. The owner's steps (section 4) and the re-pin line (section 5) are filled from the rehearsed,
reviewed bundle `drafts/repin-rel-0.1.1/` before this goes to you.**

## 1. What 0.1.1 is for
0.1.0 (C `076cded14882`, re-pinned ~17:00 on 11-15) is what EXAMIN's copy and W2-81's six adoptions ran on overnight.
They met four product defects, now fixed and landed on `w2/integrate`:

| Ticket | What 0.1.1 fixes | Met by |
|---|---|---|
| W2-88 S29 (DAEO-2bdu) | the wheel ships `template/.gitleaks.toml` and A9's kernel sources, so A0 and A9 work from an installed release | W2-81: A0 exit 1 in all six (DEC-1189 (1)) |
| W2-174 (DAEO-zmo4) | the Verify pass also writes the launch fields `tk` cannot (role, allowed_paths, kpis, …), and the wheel ships the ticket and common schemas | EXAMIN F-011, F-018 (your operator wrote them by hand: DEC-1188) |
| W2-153 (DAEO-8s85) | `gov adapters generate` writes `.claude/templates/` in an adopted repository; doctor names a missing copy | W2-81 and EXAMIN: A5 `LAUNCH_NO_TEMPLATE` (DEC-1192) |
| W2-111 (DAEO-qvff) | the guard hook's import cut (S9), the live-hook diff for ACT-GUARD-FIX-7 (S10), malformed YAML fails closed | DEC-1187, P-W2-111-YAML-REST |

Also in since 0.1.0: W2-178 (the auditor's copy of a set without its dropped questions), W2-60a (role, skills, model and
effort loaded at launch; the launch record), W2-94's re-anchor flow, W2-88 S27 (folder mode). In all: 9 merges, 22 files
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

## 4. Your steps (filled from the bundle's rehearsed README)
{TO FILL: the bump, `gov release 0.1.1`, the record check, the record commit, the tag v0.1.1 on the record commit, "released"}

## 5. The re-pin (your operator, plain terminal, about 5 minutes)
{TO FILL: the one line, with the targets named (DEC-1196 (5)), the reviewed bundle's sha256 check first}

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
