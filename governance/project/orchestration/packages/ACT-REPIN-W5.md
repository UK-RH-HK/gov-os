# ACT-REPIN-W5: re-pin window 5, the lift's (DEC-1125 (3) (i))

For the owner's operator, in a **plain terminal** (not inside a Claude session: it reinstalls gov, DEC-928 item 3).
The CTO writes `log/act-in-progress.txt` at the hand-over (DEC-1028 item 6: no CTO commit until the owner says done).
**Push first** (DEC-1087 (7)): the CTO's tree is committed and `record/w2` synced.

## What it does
0. **Stops, with nothing changed,** unless all of this holds:
   - `~/.local/bin/gov` is `pin-bcea09060ebc` (window 4's), and that pin runs;
   - the CTO's hold is written; the store link names a half; `nvidia-smi` is there;
   - the reference-transaction hook is there, parses and refreshes the store through `~/.local/bin/gov`;
   - **the wheel's inputs are the candidate's.** `src/`, `pyproject.toml` and anything else the wheel is built from are
     the same in `797495bdfc70` and in `w2/integrate` as it stands (checked at the start, before the rebuild and at the
     quiet point), and `src/` and `pyproject.toml` have no uncommitted change in the main tree. The CTO freezes `src/`
     for the night; record commits go on, and the script does not mind them;
   - the main tree is on `w2/integrate` and `tool-registry.yaml` has no uncommitted change (your commit takes only that file).
1. Builds gov's wheel from `797495bdfc70`, twice, each from a clean export, and checks that both builds have the dry
   run's sha256 (`04b094fb…d7c3`). `797495bdfc70` is `w2/integrate` on 2026-11-11 01:08 UTC. It carries every build
   since window 4's pin (`bcea09060ebc`): 59 files of `src/`, 7,219 lines added, 1,525 removed:
   - W2-20: the resource gate (`gov resources`, `~/.gov-os/machine/gate.json`, the heavy-job slots); every `gov launch`
     passes the gate;
   - W2-56: `gov launch` for every worker on the guard alone;
   - W2-136 and W2-147: `gov plan`; W2-152: `gov brief`; W2-153: the role template at launch;
   - W2-141: the guard refuses an engineer's search that can reach its own acceptance folder;
   - W2-145 and W2-137: no private reranker beside the shared service; the reranker's request cap 16 to 64;
   - W2-138: the store's commit and folder in every search result;
   - W2-150: the `gov.util` modules; W2-96: `gov accept` and the opt-in suites;
   - D-6 part 2: W2-92, W2-129, W2-55 (the links and the change labels).
2. Installs it as `pin-797495bdfc70` beside the live `pin-bcea09060ebc`.
3. Rebuilds the integration store **at `w2/integrate`'s head as it is when you run it** (records may have moved since
   the candidate; the code that builds the store is the candidate's own, because the script stops unless `src/` is the
   same), in the spare half, and flips the `W2-00-store` link to it. The rebuild is forced: the hook keeps the store at
   the head already, and an unforced refresh would leave it built by the old pin's code.
4. Runs every check through the new pin by its path (the list is under the rehearsal below).
5. Switches `~/.local/bin/gov` to the new pin in one atomic rename.
6. **Restarts the shared reranker from the new pin (class 3), if its file differs.** W2-145 and W2-137 changed the
   service, so a service running from the old pin is stopped by its pid, and one search starts it again from the new
   pin. The script compares the running service's bytes first; if they are the new pin's already, or no service runs,
   it restarts nothing.
7. Checks it live (the guard's three smoke calls, a search through the switched link), and switches back to
   `pin-bcea09060ebc` by itself if a check fails. That rollback also restarts the reranker from the old pin.
8. **Does not touch the git hooks.** `.git/hooks/reference-transaction` is window 4's hook with the lines
   ACT-OPERATOR-1 and ACT-SELECT-HOOK-1 added since. It refreshes the store through `~/.local/bin/gov`, so after the
   switch it runs the new pin by itself. (Window 4's script wrote that file whole: run again, it would have taken those
   lines out. This one only reads it.)
9. Records the pin in the tool registry: your commit, `Role: owner`, `Implements: DEC-1125`. That commit is a landing on
   `w2/integrate`, so the hook then refreshes the store once more, in the background, with the new pin.

`pin-bcea09060ebc` and the old store half stay, for the rollback. The servers, the crontab and the dispatcher stay as
they are.

## The commands (about 5 minutes)
```
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/pin/REPIN-COMMANDS-W5.sh 2>&1 | tee ~/repin-w5.log
```
- It stops at the first failure:
  - before the switch (parts 0, A, S, B, C), with `STOP: ...`: nothing is switched, the store link goes back;
  - after it (parts D, H), with `ROLLED BACK: ...`.
- Either way: tell the CTO.
- Success ends with `RE-PIN DONE: pin-797495bdfc70 is live ...`.
- **The GPU (part S):** it waits while a measure or a rebuild runs, takes the GPU lock, stops with `STOP` above 14,000
  MiB used before it starts, and stops the rebuild past 15,500 MiB.
- If it says `STOP: src/, pyproject.toml or another input of the wheel differs`, a code change reached `w2/integrate`
  after the candidate. That is not a fault of the script: the CTO decides a new candidate and a new dry run.

**Scripts handed over** (sha256, the first and last 12 digits):
- `pin/REPIN-COMMANDS-W5.sh`: `36493fa0eef1…dc67c1f02740`;
- `pin/repin7_checks.sh`: `d4d23ba4875b…d547c8e3f1e5`;
- `pin/repin7_registry.py`: `b05a99db6827…d0f13966419b`;
- `pin/smoke_repin5.sh` (window 3's, unchanged): `2f466f9df215…eab26d833dcc`.

The script also calls the CTO's tools. Their sha256 at the rehearsal (the first 12 digits): `guard4_check.py` `ff5321041613`,
`hook_timing.py` `823d876cf796`, `heavy_slot.sh` `3d5ffa51964c`, `refresh_integration_store.sh` `81302de55a2d`,
`seed_store.py` `71c970feba35`, `rebuild_slot.sh` `1f317984fe2b`, `test_guard_fix_3.py` `d638c1fb3acb`,
`tree_busy.sh` `867c37bd05ed`, `proc.sh` `5b189399f40b`. The CTO checks them again at the hand-over.

## The CTO's rehearsal on the same commit (DEC-1057)
The whole script ran as you will run it, against a scratch mirror under `/tmp/gov-os-emg-repin5/`:
- the gov link and the pins' folder (the old pin linked, never written);
- the two store halves (shared clones with copies of their stores);
- a registry clone;
- the hold;
- a scratch hooks folder with a copy of the live hook (the script only reads it).

The live shared reranker was not restarted in the rehearsal (`GOV_REPIN_SKIP_RERANK=1`). Part C still compared its
bytes with the new pin's, and every search still went through it. The script is `pin/rehearse_repin7.sh`; the logs are
`log/repin-w5-rehearsal-r1.txt` to `-r4.txt` and the three `-neg-*.txt`.

**Run 4, the script as handed over: exit 0, 282 s from start to end.** Run 3 (the same script): exit 0, 270 s.
- **0.** All preconditions held.
- **A.** Both builds gave sha256 `04b094fb…d7c3`, the dry run's.
- **S.** The rebuild took 39 s (run 3: 35 s), GPU peak 2,530 MiB (run 3: 5,049 MiB), incremental on the spare half's own
  store. The store holds 24,977 vectors, made with headers.
- **B. ALL CHECKS PASS:**
  - the pin's `gov` imports from the pin; its commands include `brief`, `links`, `plan` and `resources`;
  - window 4's builds still in the pin; the pin accepts the main tree's own `retrieval.yaml` (the pool is on);
  - window 5's builds in the pin, each by name:
    - the reranker's cap (64 texts, 24,000 characters), no private reranker, the service holds the free slots;
    - the guard's search rule; the `gov.util` modules and the old names that re-import them;
    - the launcher's sandbox, gate, environment and plan check; the role template flag; `portability.compose`;
    - `gov accept`'s opt-in suites; `gov brief --run`; `gov resources --slot`;
    - `gov resources` reads this machine's real `gate.json` without a fault; `gov launch` refuses an unknown ticket by
      name and starts nothing; `gov plan --json` answers; `gov links --since HEAD~1` answers;
  - the store at the head, a search with both facets and `rerank.by` = service, and the result names the store's commit
    and folder, in 2.3 s;
  - `gov context DAEO-sdxk` builds with a wide budget and answers at the default ceiling what the old pin answers
    (see "For the CTO", below); `gov context --in-force`;
  - the three hooks (SessionStart, PreCompact, Stop) exit 0;
  - every `gov` name the live guard hook imports (8) is in the new pin, and so is every one the staged W2-141 hooks
    import (8): a missing name would refuse every tool call;
  - `guard4_check.py` PASS (453 cases);
  - `test_guard_fix_4.py` 467 passed;
  - `test_live_hook.py` and W2-141's unit cases: 267 passed;
  - `test_g14.py` with the live hook: 151 passed, 1 skipped;
  - `test_g14.py` with W2-141's staged hook pair: **4 failed**, 147 passed, 1 skipped, the four by name (below);
  - ACT-GUARD-FIX-3's suite: the same 49 cases fail as on the old pin, by design since ACT-GUARD-FIX-4;
  - the hook takes 0.17 to 0.23 s.
- **C.** The running reranker (pid 1544290) was started tonight from a check clone of another helper, with the
  candidate's own bytes: no restart needed. The old pin's service file and the new pin's differ, so a service running
  from the old pin gets restarted after the switch. **That restart is not rehearsed** (the live service is never touched
  in a rehearsal); it is window 4's code with the reason text changed.
- **D.** The guard's three smoke calls: the Read passes; the acceptance-test write is refused; with no judge, the call is
  refused. A search through the switched link has both facets, the service and the store's commit.
- **H.** The hook is unchanged and refreshes through the gov link; the new pin's `gov rebuild` offers `--integration`.
- **E.** The registry edit and commit (`Role: owner`, `Task: decision-record`, `Implements: DEC-1125`) in the registry clone.
  The file parses, with one gov entry for the new pin.
- Afterwards the live gov link and its script, the live pins and wheels, the live hook, the registry file and the
  reranker's pid were **unchanged** (sha256 or `readlink`, before and after, in each log). The live store link and its
  halves moved in runs 2 and 4 because the CTO committed during the run and the live hook refreshed the live store: the
  log says so and shows the hook's lines. The rehearsal never wrote to them.

**The stops, rehearsed with a planted fault (logs `-neg-src`, `-neg-uncommitted`, `-neg-check`):**
- a branch whose `src/` differs from the candidate: `STOP` at part 0, nothing built or switched;
- an uncommitted change in `src/`: `STOP` at part 0;
- a check of part B failing after the store was rebuilt and its link flipped: `STOP`, and `the store link is back on`
  the old half; the gov link unchanged.

**Fixed in the rehearsal before this hand-over:**
- **Run 1 stopped at B:** the `gov links` check required exit 0, but `gov links` exits 1 when it finds something new (a
  notice). The check now reads the answer's `ok`. The STOP path worked: nothing switched.
- **Found while reading window 4's script:** its part H would have overwritten the hook (see item 8 above). The new
  script does not write the hook.
- **Found in run 1:** with window 4's hook live, the ready store half is already at the head, so an unforced refresh
  answers "fresh" in 2 s and leaves the store built by the old pin's code. Part S now forces the rebuild.

**Named reds, not gates (DEC-1125 (1), DEC-1123 (3)):** the warm real-model query latency (W1-19, W2-13: this script
measures no p95; it times one search and prints it) and the trailers family (this script runs no trailers check). Every
other check of window 4 is kept.

## W2-141's hook (`docs/changes/W2-141-hook/`): the order does not matter
That change (two files copied over the live hook, `.claude/hooks/pretooluse.py` and `role_reads.py`) is a separate ACT
of the operator. The script works the same whether it comes before or after this one:
- with the old hook live, `test_g14.py` must pass in full;
- with W2-141's hook live (`BEGIN W2-141 BLOCK` in `role_reads.py`), exactly four engineer cases must fail, by name, and
  none other: "a search of the whole acceptance folder (from above)", "Glob lists names", "Grep from above" and "grep -r
  from above". These are W2-141's intended refusals;
- the staged pair is run the same way, whichever is live.

**The pair rehearsed with the candidate pin (review F4).** The same steps as the W2-141 rebuild's rehearsal, with the pin
the re-pin script installed (`drafts/repin-w5/rehearse_w2141.sh`, log `drafts/repin-w5/w2141-rehearsal.log`, 02:12 GMT, 39 min):
- the live hook and the staged pair both give: `sets_globs_check.py` 573 run, 0 failed; `walls_check.py` 331, 0 failed;
- replay of 48 hours (21,919 unique calls), under the CTO's own ticket: **0 calls changed**;
- the same calls under W2-141's ticket (an engineer): 31 allow to deny, all "the search can reach
  tests/acceptance/W2-141/" (W2-141's S1 and S2), **0 deny to allow**;
- `test_g14.py`: the staged pair adds exactly the four cases above to what the live hook already fails;
- the hook's median per call: 133 ms with the pair.

The rehearsal's clone had to stand under `/tmp` (this night's rules close `~/gov-os-runs`), where the guard's catastrophic-rm
rule treats the clone as scratch. So nine cases that depend on where the clone is, or on its base, are red **both before and after** the pair
(`guard4_check.py`'s sets W8 case; six of `test_guard_fix_4.py`; `test_the_logged_refusals_replay_as_decided`; and
`test_w2_91_tests_today` in g14). The same suites pass in the main tree (the script's part B: 453, 467, 267 and 151).
The rehearsal's own count of "failures: 2" is those two guard4 lines, one before and one after.

## Rollback (if anything goes wrong after the switch)
```
ln -sfn ~/.local/share/gov-os/pin-bcea09060ebc/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov; hash -r
```
There is no hook to remove: this act wrote none. Then the reranker: `bash .gov-runtime/scratch/orchestrator/tools/proc.sh stop <its pid>`,
and one `gov retrieve` starts it from the old pin. Revert the registry commit.

## After it
Tell the CTO "done". It then:
- ends its hold (`mv`, never `rm`);
- checks that the registry commit's hook run refreshed the store with the new pin (`log/integration-store.log`);
- applies W2-141's hook ACT, if it has not been applied;
- runs the lift's formal closes (DECIDED-NOT-DONE row 97: `gov accept W2-92` and `gov accept W2-05` first, with the new
  pin's reader);
- takes the first memory audit's date from DEC-1125 (2): it measures this re-pin's retrieval change.

## For the CTO (not for the owner's commands)
- `gov context <id> --json` answers `CONTEXT_OVER_CEILING` at the default 6,000 tokens for every in-progress ticket tried
  (DAEO-sdxk 18,713, DAEO-r30l 28,537, DAEO-wnnz 28,480, DAEO-ouet 10,370, DAEO-xwro 9,288, DAEO-o5x1 7,040, DAEO-8s85
  6,902), under the live pin too. A record finding, not a pin fault: the packet builds with `--budget 100000`.
- D1 (a `git diff <rev>:<path> <rev>:<path>` falsely refused by the guard): a row; the new pin carries the live pin's
  behaviour. F1 and F3 for W2-141's README, as text: `drafts/repin-w5/W2-141-README-fold.md`.
- The notes: `drafts/repin-w5/NOTES.md`.

**Basis:** DEC-1125 (3) (i) (the re-pin ACT, rehearsed in a clone and independently reviewed, ready with the exact
commands), under DEC-1037's re-pin windows and DEC-1122 (3) (the lift's critical path under usage (A)); question 1 (memory:
agents get the current store, refreshed after every merge, and the product the experiments measure) and question 2 (GPU
work in turns under its bounds; nothing switched unless every check passes; a rollback in one command).
