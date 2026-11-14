# ACT-REPIN-REL-0.1.0: the re-pin from release 0.1.0 (DEC-1178 (3), P-RELEASE-1 §6)

**DRAFT, NOT HANDED OVER.** The values C, the record's sha256 and the wheel's sha256 are filled by the CTO at
"released" (`fill_release.sh`); the rehearsal is then run again on the real C, and an independent review follows. Until
then this page is for the reviewer and the CTO; the commands below are the operator's once the slots in `{…}` are filled.

For the owner's operator, in a **plain terminal** (Windows Terminal, then WSL; not inside a Claude session, not a
terminal started from one, not the operator console: it reinstalls gov, DEC-928 item 3). It runs right after the owner
made release 0.1.0 (P-RELEASE-1 §4 steps 1 to 8: `gov release 0.1.0` at C, the record committed with `Role: owner`, the
annotated tag `v0.1.0` on the record commit) and before the operator's EXAMIN setup (DEC-1180 (3)).
The CTO's hold is on from "release ready at C" until you say "done": nothing lands on `w2/integrate` in between, so
`src/` and `pyproject.toml` stay C's (RL-3). The CTO writes `log/act-in-progress.txt` at the hand-over.

## What it does
0. **Stops, with nothing changed,** unless all of this holds:
   - `~/.local/bin/gov` is `pin-797495bdfc70` (window 5's), and that pin runs;
   - the CTO's hold is written; the store link names a half; `nvidia-smi` is there;
   - the reference-transaction hook is there, parses and refreshes the store through `~/.local/bin/gov`;
   - **the wheel's inputs are the release's:** `src/`, `pyproject.toml` and anything else the wheel is built from are
     the same at C and at `w2/integrate` as it stands (checked at the start, before the rebuild and at the quiet
     point), with no uncommitted change in `src/` or `pyproject.toml`;
   - the main tree is on `w2/integrate`, and `tool-registry.yaml` has no uncommitted change.
1. **R. Reads the release and checks it against the filled values (RL-1):**
   - `v0.1.0` is an annotated tag, on a commit with one parent, and that parent is C;
   - between C and the tag only `docs/releases/0.1.0/manifest.json` and `manifest.sha256` changed;
   - `manifest.sha256` holds for `manifest.json`, and `manifest.json`'s sha256 is the record sha256 filled in;
   - the manifest names version `0.1.0`, commit C in full, CLI version `0.1.0`, and the wheel
     `gov-0.1.0-py3-none-any.whl` with the wheel sha256 filled in;
   - the epoch filled in is C's commit time;
   - the record's own check (`gov.release.verify`, the old pin's release code, the code `gov release` ran) passes on
     the tag's `template/` tree;
   - the tag's commit is in `w2/integrate`'s history.
2. **A.** Builds gov's wheel from C, twice, each from a clean export, and checks both builds equal **the release
   record's wheel sha256**. Installs it as `pin-{C}` beside the live `pin-797495bdfc70`.
3. **S.** Rebuilds the integration store at `w2/integrate`'s head as it is when you run it, in the spare half, by the
   new code, and flips the `W2-00-store` link to it (forced, as window 5).
4. **B.** Runs every check through the new pin by its path (window 5's list, plus: `gov adapters`, `wait`, `dispatch`,
   `impact`, `session-watch`, `skilleval` and `release` answer; the release code imports).
5. **C, D.** At the quiet point, switches `~/.local/bin/gov` to the new pin in one atomic rename; restarts the shared
   reranker from the new pin only if the running service's file differs from the new pin's (class 3).
6. Checks it live: the guard's three smoke calls; a search through the switched link; **P-RELEASE-1 §5's two lines:**
   the installed wheel's sha256 equals the record's, and `readlink -f ~/.local/bin/gov` names `pin-{C}`; `gov --help`
   lists `adapters` and `wait` (P-2). It switches back to `pin-797495bdfc70` by itself if a check fails.
7. **H.** Does not touch the git hooks (only reads them).
8. **E.** Records the pin in the tool registry: your commit, `Role: owner`, `Task: decision-record`,
   `Implements: DEC-1178`.

`pin-797495bdfc70` and the old store half stay, for the rollback.

## The commands (about 5 minutes)
1. **The files the script runs are the reviewed ones, then the re-pin** (one line; `sha256sum -c` prints 18 `OK`
   lines, the filled script, its checks, its registry edit, the smoke test, the CTO's 9 tools and the 5 files the
   checks also run (two test suites, the heavy slots' sizes, the staged W2-141 hook pair), and stops the line
   if any file changed since the review; `fill_release.sh` writes the list at "released"):
```
cd /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator && sha256sum -c drafts/repin-rel-0.1.0/REPIN-REL-0.1.0.sha256 && bash drafts/repin-rel-0.1.0/REPIN-COMMANDS-REL-0.1.0.sh 2>&1 | tee -ai ~/repin-rel-0.1.0.log
```
- The log is appended to, never overwritten; an earlier run's working folder is kept beside the new one.
- Ctrl-C (or closing the terminal) is safe: before the switch it stops the store rebuild within seconds (60 s at most),
  puts the store link back and prints `STOP: interrupted`; after it, it switches back (`ROLLED BACK`). Tell the CTO
  either way.
- It stops at the first failure:
  - before the switch (parts 0, R, A, S, B, C), with `STOP: ...`: nothing is switched, the store link goes back;
  - after it (parts D, H), with `ROLLED BACK: ...`.
- Either way: tell the CTO, and do nothing else.
- Success ends with `RE-PIN DONE: pin-{C} (release 0.1.0) is live ...`.
- `STOP: v0.1.0 is not an annotated tag` or `... is not on the record commit whose parent is ...`: §4 step 6 was not
  done as written (`git tag -a v0.1.0` right after the record commit). Tell the CTO; do not move the tag yourself.
- `STOP: src/, pyproject.toml or another input of the wheel differs`: a code change reached `w2/integrate` after C.
  The CTO decides (RL-2: a new numbered release, 0.1.1).
- The GPU (part S): it waits while a measure or a rebuild runs, takes the GPU lock, stops above 14,000 MiB used before
  it starts, and stops the rebuild past 15,500 MiB.

## Rollback (if anything goes wrong after the switch)
```
ln -sfn ~/.local/share/gov-os/pin-797495bdfc70/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov; hash -r
```
That one line is yours, and it is the whole rollback of what sessions use. The rest is the CTO's, after you tell it:
the reranker, if the script restarted it, is stopped by its pid and one `gov retrieve` starts it from the old pin; the
registry commit is reverted (`git revert --no-edit <the commit>`).

## After it
Tell the CTO "done". It then ends its hold (`mv`, never `rm`), adds §5's two lines to
`docs/plan/wave-2/examin-copy/release-check.md` from your log, checks the registry commit's hook run refreshed the
store with the new pin, and hands over the EXAMIN setup (DEC-1180 (3)).

## Rehearsal and review
See `NOTES.md` (the rehearsal's outcomes on the stand-in C, and the steps left at "release ready").
