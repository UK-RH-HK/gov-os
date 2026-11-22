# W2-209 rehearsal (slice (a)): a patch release on a scratch clone and a scratch `$HOME`

Run on 2026-11-20 by the ticket lead, with `rehearse.py` in this folder, on the branch `e2/release-patch`. Result: **26 of 26
checks ok** (`results.json`). The real `~/.local/bin/gov` link was read before and after: unchanged (check Z). Nothing was
pushed or fetched: the scratch clone has no `origin`; the "push" is a stand-in script that appends its arguments to a file.

## How it is set up

- The scratch clone is of this branch's head (current code), `origin` removed. A scratch release **0.9.0** is built on it
  by `gov.release.build` and tagged, so there is a release N with a record. The planted range sits on N; the release cut
  is **0.9.1**. (Scratch numbers: the real next release's number is not the rehearsal's to name.)
- The scratch `$HOME` holds one live pin, the wheel of N, linked from `~/.local/bin/gov`. Every `gov` call is a child
  process with that `HOME`, working in the clone, `GOV_ROLE=orchestrator` where the case says so.
- The authority file is switched **on in the scratch clone only**, by a scratch commit carrying
  `Decided-by: owner (standing, DEC-1223)`. The committed file in this repository stays `patch_releases: off`.
- G2's record is planted (green, full, `optin: ["weekly"]`, head and tree of C). G3 is stood in by the seam
  (`_patch_test(rehearse=...)`, report `{"verdict": "READY", "standin": true}`); see "What remains for the real G3".

## What it shows

| Case | What | Result |
|---|---|---|
| A | A planted patch (a `Fix:` commit under a ticket closed at N, a `Class: Q` chore, the version commit) | `gov release 0.9.1 --patch --check`: `patch`, P1 to P5 all pass; the tree is clean after (nothing written) |
| B | Six planted bigger changes, each on the patch plus one change | each refused as `bigger`, naming the rule and what failed it: a `docs/contract` path (P2: `docs/contract/PLANTED.md`), `EMERGENCY-2.md` (P2), a ticket closed since N (P3: `DAEO-zzzz`), a new command (P4: `added: planted`), a kit schema added (P5: `planted.schema.json`), a feature commit with neither `Fix:` nor `Class: Q`/`C` (P3, the commit named) |
| C | The cut with the planted green record, G3 stood in, `--push` a stand-in | the record folder holds `manifest.json`, `manifest.sha256`, `kind.json`, `gates.json`, `suite.json`, `NOTE.md`; tag `v0.9.1` annotated, its parent C; the record commit's trailers are `Role: orchestrator`, `Decided-by: owner (standing, DEC-1223)`, `Task: release`; the re-pin switched the scratch link to `pin-<C12>`; the registry entry committed; `repin.json` `ok`; `rollback.sh` written; one push of at most 190 characters (`push-text.0.9.1.scratch.txt`); the authority file unchanged; `bash rollback.sh` in a plain shell (no `gov` on its path) put the previous link back and wrote `0.9.1` into `burned` |
| D | A second clone whose candidate carries a hook (`stop.py`) that exits 3 | the post-pin check `hooks` failed; the scratch link named the old pin again (the whole cut, wheel builds included, took 29.9 s); `repin.json` `rolled_back`; `0.9.1` in `burned`; tag and record stay; one push `Gov OS 0.9.1 NOT pinned: post-pin check failed (hooks). ...` (`push-text.0.9.1.failed.scratch.txt`); the registry file unchanged; a second re-pin of the burned release stops at `burned` |
| Z | The machine's real link | unchanged |

Files here: `REHEARSAL.md`, `rehearse.py`, `results.json` (every check with its evidence), `kind.0.9.1.scratch.json`,
`gates.0.9.1.scratch.json`, `NOTE.0.9.1.scratch.md` (the scratch cut's record files), the two push texts.

## What the rehearsal taught (each is in the code or the setup, none changes a KPI line)

1. **A scratch `$HOME` hides two things the real one has**, and each first showed as a rolled-back re-pin: the user's site
   packages (`sqlite_vec`, so the post-pin search lost its semantic facet: the script sets `PYTHONUSERBASE` to the real user
   base, as the acceptance driver does) and a git identity (the registry commit failed with "Author identity unknown": the
   script sets `GIT_AUTHOR_*` and `GIT_COMMITTER_*`). The re-pin did what it should: rolled back and burned. On the real
   machine neither is missing.
2. **A pin of the base release (0.1.4) reads a store built by today's code as stale** (its semantic facet says `stale`), so the
   post-pin search through an old-code pin fails. The rehearsal therefore runs on current code (scratch release N built on
   this branch's head). For the first real patch release the store must be at a state the new pin reads: the pin is the
   new release's code, so a store built by the CTO's current pin is read by it; the CTO rebuilds after a release whose
   store loader changed (as 0.1.4's script did).
3. The search needs a store in the clone: the script copies `store.db` and `query-vector-cache.db` from the existing
   store (a file copy, no rebuild; `.gov-runtime/` is ignored by git).
4. If the registry commit itself fails after the switch, the re-pin rolls back with the check named `registry` (a sixth
   reason beside the five of the spec). It is the safe reading; named here so the CTO knows the word.

## What remains for the real G3 (the proving run on real kept outputs)

`proving.rehearse` is built to the W2-81 run's form and tested with stand-ins for the runner and the judge (the acceptance
cases of S5: NOT_READY naming the repository and step, the kept folder and `root` unchanged). It has **not** been run for
real. What it reads of a kept run: `<kept>/run.json` (its `manifests` path, which must still exist), `<kept>/repos/<name>`
and `<kept>/outputs/<name>` for the six repositories, `<kept>/report.json` for the end-to-end figure per repository
(`repositories.<name>.figures.end_to_end`) and the close step's ticket (`repositories.<name>.queue.ticket`). Still needed
from the W2-81 run now going (`~/gov-os-runs/W2-81/run-0.1.4/` once its lead finishes):

- the kept run folder itself, with all six repositories adopted at that run's release, their outputs and manifests;
- **to check against the real `report.json`**: whether it holds `repositories.<name>.queue.ticket` (W2-81's `--queue-ticket`
  form); where it does not, the close step is skipped and said so, which is a weaker G3 than the spec's "`gov close` of one
  ticket in each clone exits 0". If the real report keeps the landing under another key, `_queue_ticket` in
  `src/gov/release/proving.py` reads the wrong one: a one-line fix once the form is seen;
- one real pass of `rehearse` on a real candidate (the real `gov update`, `gov doctor` and `gov close` through six clones
  and the default judge, `tests/acceptance/W2-81/w2_81_judge.judge`, called per repository over the kept repository and
  over the clone). The judge is asked for the outputs-and-repository judgement with the kept run's own end-to-end figure
  (no session runs), so this G3 proves that the update left the adoption's outputs judged as before, not new memory
  quality;
- the candidate's release record is built in G3's scratch source, so the six kept repositories must have been adopted from
  a release whose `template/` the update can move to the candidate (they were adopted at N: `gov update <X>` is the real N
  to X update).

Until that is run, G3 is a built and unit-tested gate and a stand-in in the rehearsal; the first real patch release should
not be cut before one real G3 pass.
