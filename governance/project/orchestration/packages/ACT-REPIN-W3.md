# ACT-REPIN-W3: re-pin window 3 (DEC-1068 (e))

For the owner's operator, in a **plain terminal** (not inside a Claude session: it reinstalls gov, DEC-928 item 3).
The CTO writes `log/act-in-progress.txt` at the hand-over (DEC-1028 item 6: no CTO commit until the owner says done).

## What it does
1. Builds gov's wheel from `8284fb408bd4`, twice, each from a clean export, and checks that both builds have the dry
   run's sha256. `8284fb408bd4` is `w2/integrate` at 09:18 on 2026-11-04, with DEC-1068 recorded. It holds the night
   of DEC-1067: W2-32's G1, S8 routing by question type with the phrasings, reranker requests bounded at 16 texts and
   24,000 padded characters, and contextual headers when embedded. `rebuild.yaml` (`embed_headers: true`) and
   `retrieval.yaml` (routing, phrasings) switch these on.
2. Installs it as `pin-8284fb408bd4` beside the live `pin-9894b0cf`.
3. Re-embeds the integration store with headers at the same commit, in the spare half (`W2-00-store-b`), and flips the
   `W2-00-store` link to that half, the way the refresh tool does. This is the refresh tool itself, pinned to the commit.
4. Runs every check through the new pin by its path.
5. Switches `~/.local/bin/gov` to the new pin in one atomic rename.
6. Checks it live, and switches back to `pin-9894b0cf` by itself if a check fails.
7. Records the pin in the tool registry: your commit, `Role: owner`.

`pin-9894b0cf` and the old store half stay, for the rollback. Nothing else on the machine changes: the servers, the
crontab, the dispatcher and the shared reranker stay as they are. Window 4 is for the reranker's memory release.

## The commands (about 3 minutes)
```
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/pin/REPIN-COMMANDS-8284fb408bd4.sh 2>&1 | tee ~/repin-8284fb408bd4.log
```
- It stops at the first failure.
  - **Before the switch** (sections 0, A, S, B and C), a failure prints `STOP: ...`. It puts the store link back on
    its old half and changes nothing that sessions use.
  - **After the switch** (section D), a failed check switches straight back to `pin-9894b0cf` and the old store half
    by itself, and prints `ROLLED BACK: ...`.
  - Either way: tell the CTO.
- Success ends with `RE-PIN DONE: pin-8284fb408bd4 is live`.
- **The GPU (section S):** the store re-embed is a GPU job, and GPU jobs take turns (DEC-1068 (4)).
  - It waits, up to 2 hours, while `measure.sh`, `measure_rx.sh` or `rebuild_slot.sh` runs, and takes
    `/tmp/gov-os-d4b-rebuild.lock`.
  - It uses only the shared embedder that is already running. A rebuild never starts one: only a restart's `start=True`
    does.
  - It stops with `STOP` if more than 14,000 MiB of GPU memory is in use before it starts. It stops the re-embed (by
    its own process group) if the GPU goes past 15,500 MiB.

## The CTO's rehearsal on the same commit (DEC-1057)
The whole script ran as you will run it, against a scratch mirror of what it touches. The script takes these paths
from `GOV_REPIN_*` variables with the live defaults, and your run sets none of them:
- `.local/bin/gov` and the pins' folder: the old pin linked, never written;
- the two store halves: shared clones at the live halves' commits, with copies of their stores;
- a clone of the repository for the registry commit;
- the hold file.

The real HOME stayed, because it names the shared reranker's socket and the machine-wide vector cache, which your
run uses. `~/.local/bin/gov`, the live pins and the live store were checked unchanged after every run. The script
used is `.gov-runtime/scratch/orchestrator/pin/rehearse_repin5.sh`. The log of the final run is
`.gov-runtime/scratch/orchestrator/log/repin-w3-rehearsal-20261104.txt` (run 4, the script as handed over: exit 0,
147 s from start to end). Runs 1 to 3 are kept beside it (`-r1-stopped`, `-r2`, `-r3`).
- **A.** Both builds gave sha256 `82fbe15b2fccfe2c06872b6389a2ca8dc67c601d08efbf53e63801c41860c02e` (also in the
  CTO's separate dry run).
- **S.**
  - The GPU had 10,250 MiB in use before the refresh, and 10,271 MiB at its peak.
  - The refresh took 37 s: the semantic stage 4.0 s, the code index 17.6 s, the lexical index 7.0 s. It ended
    `rc=0`, and the link moved to `W2-00-store-b` at `8284fb408bd4`.
  - The store holds 18,896 vectors, all made with headers (`embed_headers true` recorded), and 10 chunks were cut at
    10,000 characters.
  - It is fast because the machine-wide vector cache already holds the headers' vectors, from the night's m4/m5
    clones and from this rehearsal. The first rehearsal run's semantic stage took 8.2 s. A cold re-embed with headers
    took 550 s (m4).
- **B. ALL CHECKS PASS:**
  - gov imports from the pin; the commands are listed; there is no CPU-only gate;
  - the padded bound is in the pin's `rerank.py`; the dependencies import;
  - the store is at the commit with headers;
  - a search on it has both facets and `rerank.by` = `service`, in 1.7 s;
  - `gov context` works; the SessionStart, PreCompact and Stop hooks exit 0;
  - `guard4_check.py` PASS (70 cases);
  - `test_guard_fix_4.py` 467 passed; `test_g14.py` 151 passed, 1 skipped; `tests/unit/hooks/test_live_hook.py` 63
    passed. These are the live hook's suites as ACT-G14b checked them.
  - ACT-GUARD-FIX-3's suite: 49 failed, 236 passed, 1 skipped. These are **the same 49 cases as the live
    `pin-9894b0cf`**. Since ACT-GUARD-FIX-4 (`3bc25241`, after window 2) the live hook lets unresolvable targets
    through by design (its `LET_THROUGH`), so that suite now fails those cases under either pin. The check is "the new
    pin fails exactly the old pin's".
  - The hook takes 0.1 s.
- **C.**
  - The shared reranker (pid 1185831) runs from `pin-9894b0cf`'s `rerank_service.py`, which is byte for byte the new
    pin's.
  - `pin-9894b0cf` searches the new store with both facets.
  - The mirror's old-pin folder is a link, so the rehearsal listed no old-pin processes ("IDLE"). Your run lists the
    reranker service there as `BUSY 1185831 ...` (or its pid then), which is expected.
- **D.**
  - The guard's three smoke calls: the Read passes, the acceptance-test write is refused, and with no judge reachable
    the call is refused (exit 2).
  - A search through the switched link has both facets and `rerank.by` = `service`, in 1.6 s.
- **E.** The registry edit and the commit: one file; the trailers `Task: decision-record`, `Implements: DEC-1068`,
  `Role: owner`. `approved_by` stays `DEC-1037`, as window 2's entry was set after W1-06's red.
- **The rollback by hand**, tried on run 3's mirror: under 0.01 s. The old pin then searches the new store
  with both facets and the service.

Fixed in the rehearsal before this hand-over:
- **Run 1 stopped at B**, on ACT-GUARD-FIX-3's suite (above). The STOP path worked: the store link went back on its
  old half, and nothing was switched. The guard checks now follow ACT-G14b.
- **Run 2 passed**, but section C reported the reranker "not running" while it served. The cause was a pipe's SIGPIPE
  under `pipefail`, now fixed (run 3).
- **Run 4:** the commit's full id is now worked out from its 12 digits when the script runs, so no 40-hex id sits under
  `.gov-runtime/` (row W2-L423's rule). The wheel's sha256 still pins the exact content.
- **Window 2's script printed no `STOP` line when its checks failed** (`checks | tee` under `pipefail` exited first).
  This script catches every failure with an ERR trap.

## The shared reranker (class 3): no restart
This switch needs no restart under class 3:
- The new pin's `rerank_service.py` is identical to the running service's (`git diff 9894b0cf 8284fb40` is empty for
  it; `cmp` in section C checks it, and stops if not).
- The padded bound is on the client side (`rerank.py`, in every search the new pin runs).
- The client has no version handshake with the service.

The service keeps serving from `pin-9894b0cf`'s folder, which stays. Its next start, by class 3 or after its idle end,
comes from the new pin. Its memory release after each request (W2-112, `dc72280b`) is window 4's.

## Rollback (if anything goes wrong after the switch)
```
ln -sfn ~/.local/share/gov-os/pin-9894b0cf/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov; hash -r
```
Then revert the registry commit. The store can stay: `pin-9894b0cf` searches it with both facets (the rehearsal).

## What to know
- **The 49 failures of ACT-GUARD-FIX-3's suite are expected.** The script passes them only when they equal the old
  pin's.
- **Keyword-only until the next rebuild** (the headers review's F3; this fails closed): after the switch, a tree whose
  `rebuild.yaml` has headers on but whose store was made without them searches by keywords until its next rebuild.
  Today these are the main tree (its store is already stale under the old pin) and `W2-112`. W2-32's trees have no
  store yet. The integration store is re-embedded here.
- `w2/integrate` moved on during the rehearsal (to `bd87a8b21941` at the hand-over) with no change to `src/`. The pin
  is `8284fb408bd4` whatever the head is. The store goes on following integrate's head by the merge queue's promotion
  and the refresh, as before.

## After it
Tell the CTO "done". It ends its hold (`mv`, never `rm`), confirms the pin from its own session, and goes on with
D-5 to D-9 on the product that scored 38 of 48.

**Basis:** question 1 (memory: the sessions run the product measured at 38 of 48, with the store it was measured on,
not the pin's 25) and question 2 (GPU work in turns under its bounds; nothing switched unless every check passes; a
rollback in one command).
