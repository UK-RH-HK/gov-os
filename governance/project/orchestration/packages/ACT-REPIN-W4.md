# ACT-REPIN-W4: re-pin window 4 (DEC-1087 (8))

For the owner's operator, in a **plain terminal** (not inside a Claude session: it reinstalls gov, DEC-928 item 3).
The CTO writes `log/act-in-progress.txt` at the hand-over (DEC-1028 item 6: no CTO commit until the owner says done).
**Push first** (DEC-1087 (7)): the CTO's tree is committed and `record/w2` synced.

## What it does
1. Builds gov's wheel from `bcea09060ebc`, twice, each from a clean export, and checks that both builds have the dry
   run's sha256 (`11a16d0f…d406`). `bcea09060ebc` is `w2/integrate` on 2026-11-06, with every build DEC-1087 placed
   before the re-pin:
   - W2-92: the stated links;
   - W2-32 S11: the candidate pool;
   - W2-131 and W2-133: register ids;
   - W2-112: the shared reranker releases its GPU memory after each request;
   - W2-134 and W2-61h S7: the measure re-anchors in memory; source families;
   - W2-135: a line over 4,000 characters cut;
   - W2-116: the integration store refreshed after every merge; `GOV_STORE` for every worker;
   - W2-129: `gov links`;
   - D-6 part 1 and D-9's records.
2. Installs it as `pin-bcea09060ebc` beside the live `pin-8284fb408bd4`.
3. Rebuilds the integration store at the same commit in the spare half, and flips the `W2-00-store` link to it.
4. Runs every check through the new pin by its path:
   - the store;
   - the hooks;
   - the guard's four suites;
   - and, new for this window, each build above, found in the pin.
5. Switches `~/.local/bin/gov` to the new pin in one atomic rename.
6. **Restarts the shared reranker from the new pin (class 3).** W2-112 changed its service, so the running one (from
   window 3) is stopped by its pid, and one search starts it again from the new pin. The script checks the new
   service runs from the new pin.
7. Checks it live, and switches back to `pin-8284fb408bd4` by itself if a check fails. That rollback restarts the
   reranker from the old pin and removes the hook.
8. **Installs W2-116's `reference-transaction` hook** in `.git/hooks`, with the review's three fixes:
   - no inherited Python settings;
   - its own refresh lock before a heavy slot;
   - `flock -o`.

   From then on, every update of `w2/integrate` refreshes the store in the background.
9. Records the pin in the tool registry: your commit, `Role: owner`.

`pin-8284fb408bd4` and the old store half stay, for the rollback. The servers, the crontab and the dispatcher stay as
they are.

**After it, the CTO's first commit switches the pool on** (W2-32 S11) in `retrieval.yaml`:
- pin-8284fb408bd4 refuses that key (CONFIG_INVALID), so it cannot be in any tree the old pin reads before the switch;
- the script refuses to run if it already is;
- the new hook then refreshes the store at that head with the new pin.

## The commands (about 3 minutes)
```
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/pin/REPIN-COMMANDS-W4.sh 2>&1 | tee ~/repin-w4.log
```
- It stops at the first failure:
  - before the switch (parts 0, A, S, B, C), with `STOP: ...`;
  - after it (parts D, H), with `ROLLED BACK: ...`.
- Either way: tell the CTO.
- Success ends with `RE-PIN DONE: pin-bcea09060ebc is live ...`.
- **The GPU (part S):** it waits while a measure or a rebuild runs, takes the GPU lock, stops with `STOP` above 14,000
  MiB used before it starts, and stops the rebuild past 15,500 MiB.

**Scripts handed over** (sha256):
- `pin/REPIN-COMMANDS-W4.sh`: `3b838d9e…4715`;
- `pin/repin6_checks.sh`: `80206f36…2b54`;
- `pin/repin6_registry.py`: `01cc5f69…f8f2`.

## The CTO's rehearsal on the same commit (DEC-1057)
The whole script ran as you will run it, against a scratch mirror:
- the gov link and the pins' folder (the old pin linked, never written);
- the two store halves (shared clones with copies of their stores);
- a registry clone;
- the hold;
- **a scratch hooks folder** (the live `.git/hooks` was never touched).

The live shared reranker was not restarted in the rehearsal (`GOV_REPIN_SKIP_RERANK=1`). Part C still compared its
bytes with the new pin's, and every search still went through it.

The script is `pin/rehearse_repin6.sh`. The logs are `log/repin-w4-rehearsal-r1.txt` to `-r4.txt`.

**Run 3: exit 0, 124 s from start to end:**
- **A.** Both builds gave sha256 `11a16d0f…d406`, the dry run's.
- **S.** The rebuild took 27 s, with a GPU peak of 9,482 MiB. The store holds 20,399 vectors, made with headers.
- **B. ALL CHECKS PASS:**
  - the window 4 builds in the pin: W2-112's release, `gov links`, `gov rebuild --integration`, the launcher's
    `GOV_STORE`, the line cap, the pool module, and a planted `retrieval.yaml` with the five pool settings, which the
    new pin accepts;
  - the measure's families;
  - a search on the store with both facets and `rerank.by` = service, in 1.8 s;
  - `gov context`; the three hooks exit 0;
  - `guard4_check.py` PASS (70 cases);
  - `test_guard_fix_4.py` 467 passed;
  - `test_g14.py` 151 passed, 1 skipped;
  - `test_live_hook.py` 63 passed;
  - ACT-GUARD-FIX-3's suite: the same 49 cases fail as on the old pin, by design since ACT-GUARD-FIX-4;
  - the hook takes 0.1 s.
- **C.** The running reranker (pid 3997564, from `pin-8284fb408bd4`) differs from the new pin's: it is restarted after
  the switch.
- **D.**
  - The guard's three smoke calls: the Read passes; the acceptance-test write is refused; with no judge, the call is
    refused.
  - A search through the switched link has both facets and the service, in 1.6 s.
- **H.** The hook was written and parses, and the new pin's `gov rebuild` offers `--integration`.
- **E.** The registry edit and commit.
- Afterwards the live gov link, the live store link, the live pins and the live hooks were unchanged.

**Run 4, the script as handed over** (after the CTO removed today's merged worktrees, with the registry note's final
text): **exit 0, 123 s.**
- Every check of part B passed: `guard4_check.py` PASS (70 cases); `test_guard_fix_4.py` 467 passed; `test_g14.py`
  151 passed, 1 skipped; `test_live_hook.py` 63 passed; FIX-3 the same 49 cases as the old pin; `ALL CHECKS PASS`.
- `RE-PIN DONE`.
- The live gov link, store link, pins and hooks were unchanged.

**Fixed in the rehearsal before this hand-over:**
- **Run 1 stopped at B:** W2-112's memory release had been built on its branch on 11-04 but never merged. Only its
  ticket line was on integrate. Its review (READY) and merge followed, then a new commit and a new dry run. The STOP
  path worked: the store link went back on its old half, and nothing was switched.
- **Run 2 stopped at B** on one case of `test_guard_fix_4.py`. A planted write into the `EMG-queue` worktree, which
  the CTO had removed as merged and clean that evening, was refused. The old pin fails it the same way. The worktree
  is recreated from its kept branch and kept as the suite's fixture.

## Rollback (if anything goes wrong after the switch)
```
ln -sfn ~/.local/share/gov-os/pin-8284fb408bd4/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov; hash -r
rm -f /home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks/reference-transaction
```
Then the reranker: `bash .gov-runtime/scratch/orchestrator/tools/proc.sh stop <its pid>`, and one `gov retrieve`
starts it from the old pin. Revert the registry commit.

## After it
Tell the CTO "done". It then:
- ends its hold (`mv`, never `rm`);
- switches the pool on (one commit; the new hook refreshes the store);
- runs the parallel-agents and memory test (DEC-1087 (10)), including W2-112's live measure: 10 and 20 searches at
  once, the reranker's memory lines against `nvidia-smi`, and errors and fallbacks;
- then E0 and E0b.

**Basis:** question 1 (memory: agents get the current store, refreshed after every merge, and the product the
experiments measure) and question 2 (GPU work in turns under its bounds; nothing switched unless every check passes; a
rollback in one command).
