Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-88b/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Research worker brief: W2-88b (DAEO-aks1), run 4: the smoke run's record

You are the **research** worker for ticket **DAEO-aks1** (W2-88b, profile STANDARD). Your lead is the ticket lead (an orchestrator session in this worktree). The smoke run itself is done: the lead ran gov adopt's stages on the two copies outside the sandbox. **You write the record** from the run's logs. You run nothing of gov adopt, gov rebuild or any stage; you do not touch the copies.

You run in the sandbox: no network. Never run `gov retrieve` or `gov context`; search with the Read and Grep tools, and search again once in your own, different words before you say "not found" (two searches in all).

## Read first (authority)
- The ticket, in full: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-aks1.md`. Its KPI lines S1 to S5 and the three failure lines F1 to F3 (the `failure:` list, in order) are what the record must satisfy, each with its `Verify:` clause. Read the body's "Re-scoped by the owner (DEC-1176)" part.
- DEC-1176 in `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` (line 15068 onward; grep the register by id only). Also by id: DEC-1150, DEC-728.
- Note: `gov context`'s packet for this ticket still shows the ticket's text from before DEC-1176; the ticket file above is the authority. Do not use `.gov-runtime/scratch/lead/context-*.md`.

## Where things are
| what | path |
|---|---|
| your worktree / branch | /home/usain/gov-os-worktrees/W2-88b / w2/W2-88b |
| your write paths | `experiments/W2-88/**` only |
| the record you write | `experiments/W2-88/smoke-run.md` |
| the copies (read only; never write, never `git` anything that writes) | `/home/usain/gov-os-runs/W2-88b/redis/`, `/home/usain/gov-os-runs/W2-88b/grafana/` |
| each copy's stage logs (read only) | `/home/usain/gov-os-runs/W2-88b/<name>-logs/`: `stages.tsv` (one row per stage run: label, start, end, exit_code, maxrss_kb, command), `<label>.log` (header, gov's output, then `end:`, `exit_code:`, `maxrss_kb:`), `<label>.log.time`, `setup.log` (the pinned commit and the path map's commit), `pre-driver`/`post-driver.log` or `pre.out` (the driver's lines) |
| each copy's gov outputs (read only) | `/home/usain/gov-os-runs/W2-88b/<name>-out/` (`ma/`, `ma-at-a3/`, `proposal.yaml`, `a9/`) |
| the driver that ran the stages (read only) | `/home/usain/gov-os-worktrees/W2-88b/.gov-runtime/scratch/lead/stages.sh` |
| the clone set-up (read only) | `.gov-runtime/scratch/lead/clone.sh`, `setup3.sh`, `log/setup3.log` |
| the stage code (read only) | `src/gov/adopt/stages.py` (`STAGES` order, A5's gate lines 432-461), `src/gov/adopt/project.py` |
| two aborted earlier attempts (not the record's; mention only) | `/home/usain/gov-os-runs/W2-88b/aborted-1/`, `aborted-2/` |

## Facts the lead gives you (check each against the logs; the logs win)
- **redis/redis**: clone of https://github.com/redis/redis.git, pinned commit `ee8e7f70152404649ac947157fd662d11b4a00d5`, 1961 tracked files at the pin, licence file `LICENSE.txt` (read its first lines and name the licence(s) it states; record the file's path and sha256). C, with vendored `deps/`.
- **grafana/grafana**: clone of https://github.com/grafana/grafana.git, pinned commit `a00ff430d41e74022eb54361c9741e224e150021`, 24619 tracked files at the pin, licence `LICENSE` (AGPL-3.0; check and record path and sha256). Go and TypeScript.
- Before MA the lead committed the adopter's input in each copy (not a gov stage): `governance/project/path-map.yaml`, one namespace `all` holding `'**'`, `embedding_policy: embedded`, code intelligence on (setup.log names the commit). The adopter's proposal for A3 is `artefacts: []` (no action).
- `MA-at-A3`: MA run a second time at A2's head, because A3's `--assessment` must hold the assessment of HEAD's commit (stages.py:348-365). S2's MA row is the first MA run; give MA-at-A3 its own row, clearly labelled as the input to A3, not one of S2's ten rows.
- Every stage ran through `heavy_slot.sh` (a slot's wait, if any, is a wait: record its length if the log shows one) and under the driver's memory watchdog (MemAvailable under 1.5 GB kills the stage's process group; the log then has a `watchdog:` line).
- **A5 (S4).** The verdicts came from fresh independent-auditor sessions launched by the lead (run 4), each committed in its copy at `docs/audit/A5-path-map-verdict.md` with `Role: independent-auditor` alone:
  - redis: verdict commit `934b70218e6b43aac99c0da90ce131331d017700`, auditor session `4156cef7-6882-4672-89fe-5875c13ed3e1`, verdict pass, path map hash `6f9a287a72ac1062f1103651205e35d56ff74a810cdef715640a52e991f94d5a`.
  - grafana: verdict commit `c5edaf78c2806279ed504f9b7de581793735d54b`, auditor session `fddde1db-ec8c-42b4-ad7a-481c33b8e9b9`, verdict pass, path map hash `ee5bcc474a0929c4fc8c07ead1c5757c52e55e706409acb68998227b328c4e60`.
  - Every stage ran under `--session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` (the stages' records say so).
  - Check each with `git -C <copy> log -1 --format='%H %(trailers:key=Role,valueonly)' -- docs/audit/A5-path-map-verdict.md` and the verdict file's front matter (read-only git commands only).
- **Finding: A5's route (run 3).** A first pair of auditor sessions (redis `4e66e97f-fbd1-46f5-a78c-7ee5fd58cd4c`, grafana `e9403ce5-c537-4022-bc48-47f4b71f78da`) both judged the path map a pass but could not write the verdict: the briefs placed it at `governance/reviews/A5-path-map-verdict.md` in the copy, and this repository's PreToolUse hook (`.claude/hooks/pretooluse.py` rule 5, DEC-953 item 2, lines 1093-1102) refused the write: "a reviewer or auditor writes only its own review or audit record (docs/probes/, docs/audit/, docs/assessment/, .gov-runtime/scratch/orchestrator/reviews/), its own scratch, or /tmp". gov adopt fixes no verdict path (`--verdict <path>`, stages.py:432-461), so run 4 placed it under `docs/audit/`, which the hook allows. Record this as a finding for the owner: neither gov adopt nor the adopt skill names where the auditor's verdict goes, and the first place chosen was refused by the guard. It is not a stage failure (no A5 ran in run 3 with a refused verdict).
- **grafana's memory.** MA's estimate for grafana was a peak of about 38.4 GB against about 15 GB available (read the figure from `grafana-out/ma/` or MA.log and quote it with its source). If a grafana stage was stopped by the watchdog or failed for memory, it is that stage's failure (S3): the stage, command, exit code, the watchdog line or gov's refusal code, the error's first lines, time run, and the figures. If grafana's A9 completed, record that it completed and its time and `/usr/bin/time` peak, and that MA's estimate was above what the machine had.

## This is batch 1 of 2 (the run's state when you start)
- **redis is finished**: MA, A0 to A4, A5, A6, A8 exited 0; **A9 exited 1** with `gov adopt: FABRIC_INCOMPLETE: a store the path map calls for was not built: codegraph (codegraph: RuntimeError: codebase-memory-mcp query_graph failed (exit code 0))` (`redis-logs/A9.log`; `src/gov/adopt/fabric.py:705-708` raises it). A9 made no commit; the copy's HEAD at the end is A8's commit (check it). A9 is the last stage, so nothing after it is "not reached". Look in `redis-out/a9/` and the copy's `.gov-runtime/rebuild/record.json` (read only) for what the rebuild says about the code graph, and quote gov's own words only.
- **grafana is still running**: MA, A0 to A4 and A5 exited 0; **A6 is running** (started 2026-11-14T01:47:41Z; its rebuild has been in its `secrets` stage since about 01:48:43Z, one `gitleaks stdin` process per file at about 2 files a second over 24,621 files, seen in `grafana/.gov-runtime/rebuild/record.json`'s `stage_running`/`stage_running_s` and the process list; the heavy slot was taken within about 10 s, so no slot wait to speak of). Write grafana's rows A6, A8 and A9 as `pending: running` (start time for A6), and its end HEAD as `pending`. Record the secrets stage's duration so far as an observation (not a failure): what the record shows, with its time. The lead finishes grafana in batch 2.
- Commit batch 1 as below. Batch 2 (a fresh session or this one resumed) fills grafana's rows from its logs when its run ends.

## What you write: `experiments/W2-88/smoke-run.md`
Front matter (`id: W2-88b-smoke-run`, `type: evidence`, `status: ACTIVE`, `state_class: EVIDENCE`, `task: DAEO-aks1`, `decisions_applied: [DEC-1176, DEC-1150, DEC-728]`), then:
1. **What this is**: the smoke run tests only whether gov adopt works on repositories different from this one, small and large, and where it fails. Include the sentence **No questions, no measure, no validation.** word for word. State that A9's own `measure` block (no question set given) and its `scale` block stay in A9's record in the copy and are not copied here.
2. **Where**: the copies under `~/gov-os-runs/W2-88b/<name>/` (the folder the guard gives this ticket, P2 (a)); never committed here, never pushed; no workbench, no `~/workspace`, no EXAMIN repository read or cloned.
3. **One section per repository** (`## redis/redis`, `## grafana/grafana`), each with: clone path; origin URL; pinned commit (40 hex); the copy's HEAD at the end of the run (40 hex: `git -C <copy> rev-parse HEAD`; S1's check compares it); tracked-file count at the pin; licence (name, file, sha256); the path map commit; then **a stage table**, one row per stage MA, A0, A1, A2, A3, A4, A5, A6, A8, A9 in that order (plus the labelled MA-at-A3 row between A2 and A3), columns: stage, exact command (from stages.tsv, word for word; the `heavy_slot.sh`/`/usr/bin/time` wrapper named once above the table), exit code, start, end, wall-clock seconds, peak RSS (`/usr/bin/time` maxrss_kb, said as such; and gov's own peak if gov printed one), outcome (completed, failed or not reached; a not-reached row names the failing stage). A5's row names the verdict file, its commit in the copy and the auditor session id.
4. **Findings** (S3): one entry per failure (stage, command, exit code, the refusal code gov printed, the error's first lines with any secret value left out, time run, the file or path the error names), plus the A5-route finding above and any notable non-failing observation the logs show (warnings gov printed, e.g. a chunk over its size limit). Each says it is a finding for the owner, not fixed here. If a stage row's exit code is not 0, it has an entry.
5. **The assessment's secrets**, if MA names any: by path and rule id only, never a value, never a line of the file.
6. **Earlier attempts**: one paragraph: two aborted attempts of run 3 (their logs in `aborted-1/`, `aborted-2/`), stopped by the lead because they overlapped; not this record's rows.

Exit codes in the record must equal the logs' `exit_code:` lines. No recorded command carries `--questions`.

**Forbidden text** (S5, F3): the record must not contain, case-insensitively, any of `hit@5`, `hit_at_5`, `right_e2e`, `right end to end`, `wrong claim`, `wrong_claims`, `MRR`, `recall`, `accuracy`, `query_ms`, `vector_scan_ms`, as substrings anywhere (so no "recalled" either). No question set, no quality figure, no claim that memory works, is measured or is proven. No repository content beyond paths, counts, hashes and gov's own messages.

## Also in this batch
- Remove the superseded run-2 files with `git rm`: `experiments/W2-88/proof_bc.py` and `experiments/W2-88/any-repository.md` (superseded by DEC-1176 (2), (3); the stand-in verdict is option (c), not offered).
- Check, and say in your return with the command and its output:
  - `grep -inE 'hit@5|hit_at_5|right_e2e|right end to end|wrong claim|wrong_claims|mrr|recall|accuracy|query_ms|vector_scan_ms' experiments/W2-88/smoke-run.md` finds nothing;
  - `grep -n 'No questions, no measure, no validation.' experiments/W2-88/smoke-run.md` finds it;
  - for each copy, `git -C <copy> rev-parse HEAD` equals the recorded end HEAD;
  - each row's exit code equals its log's `exit_code:` (a small read-only script under your `$TMPDIR` is fine);
  - `gitleaks detect --no-git --source experiments/W2-88/smoke-run.md` (if gitleaks is not installed in the sandbox, say so; the lead runs it);
  - `git status --short` lists only `experiments/W2-88/` paths.
- Commit (your paths only), the trailers in one final paragraph:
```
git commit -m "W2-88b (DAEO-aks1): the smoke run's record experiments/W2-88/smoke-run.md (both copies, every stage, the findings; no questions, no measure, no validation); run 2's proof_bc.py and any-repository.md removed (DEC-1176 (2), (3))" --trailer "Task: DAEO-aks1" --trailer "Role: research" --trailer "Implements: DEC-1176, DEC-1150, DEC-728" -- experiments/W2-88/smoke-run.md experiments/W2-88/proof_bc.py experiments/W2-88/any-repository.md
```
  Then `git log -1 --format='%H%n%(trailers)'` must show Task, Role and Implements.

## Rules
- Reads are open except: secrets (never printed), the held-out qualification material's contents, the counterpart's work, the hidden half of an evaluation set. Never read, list or stat `~/gov-os-workbench/`, `~/workspace`, `~/EXAMIN APP`, the evaluation sets' root or any hidden folder.
- Any pytest goes through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh` with TMPDIR outside the repository (none is expected for this batch).
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so in your return; never work around a refusal.
- No new ticket; a gap is a finding in your return.

## Return (your last message; only it is read)
The twelve fields, each a labelled line ("none" where nothing):
`task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:`
In `evidence`: the commit hash and its trailers as `git log` prints them, each check above with its output, and the list of findings recorded (stage, copy, exit code, refusal code).
