# Independent review of ACT-REPIN-W5, the lift's re-pin (DEC-1125 (3) (i)), C3 under RUBRIC-2

- task: ACT-REPIN-W5
- decisions: DEC-1125, DEC-1037, DEC-1057, DEC-1028, DEC-1087, DEC-1123, DEC-801, DEC-808, DEC-1010, DEC-1014
- Where this record is: the brief named `governance/project/orchestration/reviews/ACT-REPIN-W5-review.md`. The guard
  refused that path for a reviewer (DEC-953 item 2) and named this folder as the place for review records. The CTO moves
  the record if it wants it there.
- Reviewer: independent-auditor (Opus, effort high), a fresh session. Main tree on `w2/integrate` at `06734e529e6f` when
  the review started (`178f9bc05` by its end, record commits only). I wrote nothing but this record. I ran one command:
  the dry run in `/tmp/gov-os-emg-review5`, which has since been removed.
- Read: the package `packages/ACT-REPIN-W5.md`; `pin/REPIN-COMMANDS-W5.sh`, `repin7_checks.sh`, `repin7_registry.py`,
  `rehearse_repin7.sh`, `dryrun_w5.sh`, `smoke_repin5.sh`; the logs `log/repin-w5-rehearsal-r1..r4` and `-neg-*`;
  `drafts/repin-w5/NOTES.md`. For comparison, window 4's script (a diff) and its live log `~/repin-w4.log`. Also
  `tools/refresh_integration_store.sh`, `seed_store.py` (the rebuild path), `proc.sh`, `tree_busy.sh`, the live
  `.git/hooks/reference-transaction`, `.claude/settings.json`'s hook lines, the candidate's `rerank.py` (how the service
  is started), and `git diff bcea09060ebc 797495bdfc70 -- src/`.

## Verdict: READY

No finding blocks. Every finding is in scope and reachable in ordinary work, but none fails open or loses work: each
either stops the act with nothing switched or leaves the live state working.

**Classification:** 0 blocking; 8 rows, all `other` (F1 to F8). F1, F2 and F3 should be fixed in the package text
before 08:00. Each fix is one line, and none needs a new rehearsal.

## Reproduced and verified
- **The wheel:** `dryrun_w5.sh 797495bdfc70` gave epoch `1794359304` and sha256 `04b094fbd587…bc077d7c3` twice. Both
  match the script's `EPOCH` and `SHA`.
- **The script hashes:** the four handed-over scripts and the nine CTO tools match the package's sha256 now (the first
  and last 12 digits; the 12-digit prefixes for the tools).
- **The candidate against the branch:** `797495bdfc70` is an ancestor of `w2/integrate`. There is no diff between the
  two in `src`, `pyproject.toml`, `setup.py`, `setup.cfg` or `MANIFEST.in`. The 59 files, +7,219/−1,525, match.
- **The log timeline:** the script's mtime is 01:33:48. The three negative runs (01:33:54 to 01:33:59), r3 (01:36:15)
  and r4 (01:40:47) all ran after it. r1 and r2 ran on earlier text, as the package says.
- **The log figures:** r4 exit 0 in 282 s; r3 exit 0 in 270 s; S 39 s at a 2,530 MiB peak; 24,977 vectors with
  embed_headers true. The guard checks gave 453 / 467 / 267 / 151+1s; the staged pair failed exactly the four cases by
  name; fix-3 failed the same 49 cases under both pins; the hook took 0.17 to 0.23 s. In every run, the fixed live
  paths (gov link, script, pins, wheels, hook, registry, reranker pid) were UNCHANGED. In r2 and r4 the store moved with
  `w2/integrate` (the hook's lines are shown). neg-src and neg-uncommitted STOP at part 0. neg-check STOPs at B with
  "the store link is back on W2-00-store-b".

## Probed and found sound
- **The before-the-switch paths (0, A, S, B, C):**
  - Every failure goes to `stop`, which puts the store link back under `<link>.lock` when S had flipped it. This is the
    same lock that `refresh_integration_store.sh` and `gov rebuild --integration` (`gov/rebuild/integration.py`) take,
    so the put-back cannot interleave with a hook refresh.
  - The gate on B is the last line `ALL CHECKS PASS`, which the checks script prints only at its end, so B cannot pass
    without running.
  - The GPU stop kills the rebuild's own session group (setsid without a fork in a non-interactive script).
- **The after-the-switch paths (D, H):**
  - `PHASE=switched` is set before the rename. Every failure after it, whether from ERR or an explicit check, calls
    `rollback`.
  - `rollback` relinks the old pin, puts the store back and restarts the reranker only if D restarted it.
  - Once `PHASE=live`, a failed registry step says the pin is live and does not roll back. That is right: the pin has
    passed every check.
- **The reranker restart branch** (not rehearsed, the preparer's open point):
  - It is window 4's code; only the reason text differs (diff checked). It ran live in window 4:
    `restarts.jsonl` line 8, and `~/repin-w4.log` lines 38 to 42, "pid 1657369 from the new pin".
  - The candidate's start path (`rerank._start`: a lock, then `Popen(..., str(_SERVICE), ..., start_new_session=True)`)
    names the file by its path inside the pin. The `$N/*` check in D therefore matches, and the service survives the
    terminal closing.
- **The candidate guard:**
  - It checks three times (at the start, before the rebuild, at the quiet point). Each time, the candidate must be an
    ancestor of the branch, the wheel's inputs must have no diff, and the main tree must have no tracked change in
    `src`/`pyproject.toml`.
  - It also checks that the registry tree is on `w2/integrate` and that the registry file is clean.
  - Untracked files are rightly ignored: the wheel comes from `git archive`, and the store from the half's own checkout.
- **The store rebuild:**
  - `seed_store.py` runs `gov rebuild` with `PYTHONPATH=<half>/src`, so the store is built by the candidate's code
    whenever the inputs match. That makes `--force` correct.
  - An incremental rebuild is safe: semantic.py, chunking and the store's tables are unchanged, there is no
    schema/version constant in the diff, and `ollama.py`'s change concerns only the server start.
- **The hook is only read:** `core.hooksPath` is unset, so `.git/hooks/reference-transaction` is the hook git runs. It
  refreshes through `/home/usain/.local/bin/gov`, so after the switch it follows the new pin.
- **The guard checks run the new pin:**
  - guard4_check, test_guard_fix_4, test_g14, test_guard_fix_3 and hook_timing all take `GOV_PIN_PY`; test_live_hook
    takes `GOV_LIVE_HOOK_PY`. The live hook line reads the interpreter from `~/.local/bin/gov`'s shebang.
  - Check 6b proves that every `gov` name the live hooks and the staged hooks import resolves in the pin.
  - `suite()` needs "passed" and refuses "failed" or "error". g14 compares the failure set exactly. fix-3 compares
    against the old pin.
  - The registry script refuses unless the wheel sha256 and the link are right and window 4's entry appears exactly once.
- **Not gates (named reds):** the warm latency (DEC-1125 (1)) and the trailers family (DEC-1123 (3)). `gov context` at
  `--budget 100000` is acceptable as a non-gate.

## Findings, ranked

### F1 (medium): a landing on w2/integrate during the run makes the script STOP or roll back with nothing wrong
- **What happens:**
  - The package says that record commits "go on, and the script does not mind them". That holds only for commits made
    before the run.
  - Suppose a commit lands on `w2/integrate` between part S and part D (about 4 minutes). The live hook refreshes the
    same `W2-00-store` link: through the old pin before the switch, the new pin after. It rebuilds the spare half (the
    old half) at the new head and flips the link to it.
  - Part B's store check (`the store is at …, not …`) or part D's search check (`store.commit == STOREREF`) then fails.
    The result is a STOP or a ROLLED BACK, with a message that does not name the landing.
- **The rehearsal shows it is reachable:** landings happened during r2 (two) and r4 (one, at 01:42 during B). The
  rehearsal could not show the effect, because its mirror is not hooked. On the live tree, r4's timing would have
  ended in ROLLED BACK at D.
- **The rollback itself stays clean:** the link is already on the old half, and the old pin reads the store (no schema
  change).
- **Recommendation:**
  - In the package, replace "record commits go on" with "no landing on `w2/integrate` from the hand-over until the owner
    says done" (the CTO's hold, DEC-1028 item 6, already forbids its own commits).
  - Optionally, have the script compare the branch head with `STOREREF` at C and before D's search, and name "a landing
    during the run" in its message.
- Ordinary work: yes, because the CTO committed during two of the four rehearsal runs, and a commit is ordinary work.
- Consequence: other (it fails closed; it costs the 08:00 window and a CTO `rm -rf` of the new pin before a re-run).
- Reversed by: a rehearsal whose mirror has the hook installed and gets a commit during B, ending exit 0. Or a showing
  that the hook's refresh cannot flip the link the script checks.

### F2 (low-medium): nothing at 08:00 checks that the files the script runs are the reviewed ones
- **What is missing:** the package lists sha256 for the script, its three helpers and nine CTO tools (all match now).
  But neither the script nor the owner's command verifies them. The script calls `repin7_checks.sh`, `guard4_check.py`,
  `tree_busy.sh`, `proc.sh` and the rest from the scratch tree, where the CTO edits tools routinely (`repin7_checks.sh`
  at 01:27, `guard4_check.py` on Nov 8). An edit between this review and the run would go unnoticed.
- **Recommendation:** put one `sha256sum -c` line, over a checked-in list, ahead of the script in the owner's command
  (or as part 0's first step). Stop on a mismatch.
- Ordinary work: yes, because the CTO's tools change during ordinary night work.
- Consequence: other (a drifted helper usually makes the act stop; a weakened gate would need an edit to a gate file in
  the hours before, and the CTO re-hashes at the hand-over).
- Reversed by: the hand-over carrying a hash check by command, or the script checking the list itself.

### F3 (low): the owner's rollback is exact for the gov link only, and "push first" is not a command
- **The rollback:**
  - The rollback block's first line is exact and complete for what sessions use.
  - The reranker step is prose: a relative path `.gov-runtime/…/proc.sh` that works only from the repository root, and
    "<its pid>" with no command to find it.
  - "Revert the registry commit" gives no command and no trailers.
  - The store link is not restored. That is acceptable, because no store table changed and the old pin reads a store
    built by the candidate.
  - The reranker step is optional in practice: the live old pin has used a service with the candidate's bytes all night
    (pid 1544290).
- **"Push first"** is worded as a CTO precondition, not an owner command, and the script does not check it. Window 4 had
  the same wording.
- **Recommendation:** in the rollback block, mark the second and third steps as "for the CTO, not needed for sessions
  to work"; or write them out by absolute path, with `tree_busy.sh --cmd rerank_service.py` to find the pid and
  `git -C <repo> revert --no-edit <sha>` with the trailers. Say in one line who pushes.
- Ordinary work: yes, because the owner runs it alone at 08:00.
- Consequence: other.
- Reversed by: the owner confirming that a rollback of the link alone is all they would run, with the rest left to the
  CTO.

### F4 (low): the shared reranker is found by a substring of its command line
- **What happens:** `svc_pid` takes the first `/proc` entry whose command line contains `rerank_service.py`.
  Other processes match too: a session's `grep`/`rg` for that name, a pytest of `test_rerank_service.py`, or a test
  run's own service on a scratch socket. Part C can then decide wrongly, and part D's restart stops that process by
  pid. In most cases D's own checks (the service's file under `$N/`, `rerank.by == service`) then roll back.
- Ordinary work: yes, because naming that file in a command is ordinary, though rare under the freeze at 08:00.
- Consequence: other (it fails closed, or kills an unrelated short process; window 4 ran the same code without trouble).
- Reversed by: none at 08:00 if `tree_busy.sh --cmd rerank_service.py` shows exactly one line before the run. That is a
  one-line check the owner could add.

### F5 (low): no trap for Ctrl-C, a closed terminal or SIGTERM
- **What happens:**
  - An interrupt during the GPU wait or the rebuild leaves nothing switched. The detached rebuild may still flip the
    store link after the script has died, and that store works under the old pin.
  - An interrupt between the rename and the end of D leaves the new pin live with part D's checks unrun and no
    rollback. Part B had already passed.
  - Window 4's script is the same.
- Ordinary work: yes, because an operator may press Ctrl-C during a long "waiting: … runs" loop.
- Consequence: other.
- Reversed by: none needed if the package says "do not interrupt it; if you did, run the rollback line and tell the
  CTO".

### F6 (low): the g14 check ignores ERROR results
- **What happens:** `g14()` needs " passed" and an exact FAILED set, but it does not look for errors. If its session
  fixture `trees` errors (it uses git only), about 140 cases error, the rest pass, and the check prints ok.
- Ordinary work: yes, because an environmental fault in the fixture's git setup is plausible.
- Consequence: other (the fixture never runs the pin, so no pin fault can hide behind it; guard4, fix-4 and
  test_live_hook gate the same hook with ERROR counted).
- Reversed by: a g14 case whose setup runs the pin's interpreter.

### F7 (low): the record says "restarted" when nothing was restarted, and only one service file is compared
- **What happens:**
  - The registry note, the commit message and the DONE line say "the shared reranker restarted from the new pin (class
    3)" and "the reranker from the new pin". Tonight's state makes that false: the service runs from
    `/tmp/gov-os-emg-checks/clone/…` with the candidate's bytes, so part C restarts nothing and no `restarts.jsonl` line
    is written.
  - Part C compares only `rerank_service.py`, though `rerank_worker.py` also changed. A service from a clone whose
    service file matches but whose worker does not would not be restarted.
- Ordinary work: yes (tonight's state).
- Consequence: other (the record is inaccurate; behaviour is unchanged, because the bytes are the candidate's).
- Reversed by: a part C that also compares `rerank_worker.py`, and record text that follows `NEED_RESTART`.

### F8 (low): `gov launch` is exercised only to refuse an unknown ticket (the preparer's open point)
- **What is left untested:** the real start path (W2-20's gate, W2-56's sandbox, W2-153's role template) first runs at
  the CTO's first launch after the switch.
- Ordinary work: yes.
- Consequence: other (a fault refuses launches, so it fails closed; the rollback is one command).
- Reversed by: the CTO's first step after "done" being one real launch of a trivial ticket, which the package's "After
  it" could name.

## The preparer's open points, judged
- **The reranker restart is not rehearsed:** sound. The same code ran live in window 4, and the candidate's start path
  has run (the service the candidate started tonight).
- **The CTO tools are not hashed inside the script:** F2.
- **The store is rebuilt with `--force` at the run-time head:** sound (see above), apart from F1's race.
- **The hook is only read:** sound.
- **`--budget 100000`:** sound as a non-gate.
- **Row 88's four g14 cases:** sound (the set must be equal, by name).

```verdict
{"kpis": [
 {"kpi": "J1-rollback-or-old-state", "verdict": "pass", "findings": [
   {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "J2-candidate-guard-and-checks", "verdict": "pass", "findings": [
   {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F7", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F8", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "J3-rehearsal-logs-match-claims", "verdict": "pass", "findings": []},
 {"kpi": "J4-owner-commands-exact", "verdict": "pass", "findings": [
   {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}
]}
```
