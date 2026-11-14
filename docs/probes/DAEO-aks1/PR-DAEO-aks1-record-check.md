---
id: PR-DAEO-aks1-record-check
type: probe
status: ACTIVE
state_class: EVIDENCE
task: DAEO-aks1
decisions: [DEC-1176, DEC-1150, DEC-728, DEC-801, DEC-808, DEC-1010, DEC-1014, DEC-1073, DEC-820]
record: experiments/W2-88/smoke-run.md
record_commit: 9aa5957befb4f3b49f60889c5a63c20b07b8e616
auditor_session: 30c7b3dc-fd25-4f92-8889-53c75cea0877
verdict: pass
---
# PR-DAEO-aks1-record-check: the narrow independent check of the smoke run's record

A fresh independent-auditor session (`30c7b3dc-fd25-4f92-8889-53c75cea0877`) checked `experiments/W2-88/smoke-run.md` at
`9aa5957befb4f3b49f60889c5a63c20b07b8e616` (branch `w2/W2-88b`, `git rev-parse HEAD` printed that commit) against the
ticket DAEO-aks1's lines S1 to S5 and F1 to F3 (the `failure:` list in order), each by its own `Verify:` clause, and
against the logs it cites. This session ran no stage, wrote no part of the record and is not one of the A5 auditors.
This is the narrow check of a research record. It is not a review of gov adopt's code and not a validation of memory.
Everything was read only: the copies with read-only git commands, the logs and outputs with `cat`, `grep` and `python3 -I`
reading JSON.

Sandbox check (launch_worker.sh, EMG-d4b-launched.md step 0): (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-aks1`
failed with `OSError: [Errno 30] Read-only file system`; (b) `git hash-object -w --stdin` printed
`1ae28402a109c3397a44b19239a00adfa9472eb0` and `git update-index --refresh` exited 0. `ps -eo pid,args | grep -iE
"[o]llama|[l]lama-server"` printed nothing.

**Diff scope.** The ticket's commits on the branch are `f2b1d38af..HEAD` (c0cfe3099, bbbfc379a, cbe94d9e1, 9aa5957be).
I judged S3's and F2's diff checks on every path in that range except `.tickets/DAEO-aks1.md` (the CTO's ticket edit,
commit c0cfe3099) and this record under `docs/probes/DAEO-aks1/` (the CTO's instruction places it here), as the brief
says.

## S1: the copies

- The record has one section per repository. Each names its clone path under `~/gov-os-runs/W2-88b/`
  (`/home/usain/gov-os-runs/W2-88b/redis/`, `/home/usain/gov-os-runs/W2-88b/grafana/`), a 40-hex pinned commit, its
  tracked-file count and its licence.
- `git -C <copy> rev-parse HEAD`: redis `e4d21da2cd7522ffcf2de4a2b9ccadd5c970fc47`, grafana
  `140042f023c543f2a2fb3c139b5f6dbb063198a2`. Both equal the record's "Copy's HEAD at the end of the run". `git status --short`
  in each copy printed nothing (clean).
- The pins are in each copy's history: redis `ee8e7f70…` and grafana `a00ff430…` are the parents of the path-map commits
  (`db81b792…`, `da759782…`). Each `setup.log` names the same pin and path-map commit.
- `git -C <copy> ls-tree -r --name-only <pin> | wc -l`: redis 1961, grafana 24619. Both equal the record. MA's
  `tracked_files` is 1962 and 24620, as the record says.
- Licence: `git show <pin>:LICENSE.txt | sha256sum` (redis) gives `4a0e416b…ddc4e40`, and `git show <pin>:LICENSE |
  sha256sum` (grafana) gives `0d96a4ff…079abcb0`. Both equal the record. The first lines match the record's summaries:
  redis's tri-licence (RSALv2, SSPLv1, AGPLv3; BSD 3-clause for 7.2 and earlier) and grafana's AGPL v3. Origin URLs:
  `https://github.com/redis/redis.git` and `https://github.com/grafana/grafana.git`.
- `git log --all -S'gov-os-runs/W2-88b/redis' --oneline` finds `cbe94d9e1`. The same command for grafana finds `9aa5957be`
  and `cbe94d9e1`. `git log --name-status f2b1d38af..HEAD` shows that both commits touch only
  `experiments/W2-88/smoke-run.md` (and cbe94d9e1 deletes `experiments/W2-88/proof_bc.py` and `any-repository.md`). So
  these hits are the record's own text, which is expected, and not clone content.
- `git ls-files | grep -E '^(redis|grafana)/'` prints nothing. No clone file is tracked.

Verdict S1: pass. No finding.

## S2: one row per stage, exit codes equal the logs

- Each section's table has the rows MA, A0, A1, A2, A3, A4, A5, A6, A8 and A9, plus a separate MA-at-A3 row that is
  marked as an input and not one of the ten. Every row gives the command, exit code, start, end and outcome.
- Every row's command, start, end and exit code equals the matching row of `<name>-logs/stages.tsv`. Every exit code
  equals the `exit_code:` line in `<name>-logs/<label>.log` (`grep -H '^exit_code:' *.log`): 0 everywhere except A9, which
  is 1 on both copies.
- The elapsed and peak figures equal each `<label>.log.time` file. I recomputed the wall-clock spans from start and end:
  redis MA 22, MA-at-A3 21, A6 64, A8 36, A9 48; grafana MA 157, MA-at-A3 163, A3 10, A4 11, A5 12, A6 26749, A8 242,
  A9 13; the rest 5. All equal the record.
- gov's own `peak_rss_bytes` values (redis 36339712 and 35770368; grafana 52256768 and 51621888) equal the MA logs.
- `--questions` appears nowhere in either table's commands or in `stages.tsv`.
- grafana's first A6 run was stopped and has no exit code. The record keeps it out of the table, names its log
  `A6-stopped-1.log`, and explains why. Its log, `post-driver.log`, `post2-driver.log`, `post2.exit` (1) and `post2.pid`
  (501155) agree with the note under the table.

Verdict S2: pass. One row, R1, about the logs' header line rather than the record.

## S3: failures recorded; the diff check

- The non-zero rows are redis A9 (exit 1) and grafana A9 (exit 1).
  - **F-1** names the stage, the command, exit 1, `FABRIC_INCOMPLETE`, and gov's two output lines. Its text is
    byte-for-byte what `redis-logs/A9.log` holds between `--- output ---` and `--- end ---`.
  - **F-3** names the stage, the command, exit 1, `ADOPT_GIT_FAILED`, and the one output line. Its text is
    byte-for-byte what `grafana-logs/A9.log` holds.
- Both findings give their times and peaks, which equal the logs.
- A9 is the last stage, so no stage follows it to be marked not reached. The record says so for each copy, and each
  driver log ends "chain stops at A9 (rc=1): the stages after it are not reached".
- Both sections have an MA row (exit 0).
- What the findings say about the copies holds:
  - redis `.gov-runtime/rebuild/record.json`: `timing` record_s 1.4, lexical_s 0.5, secrets_s 3.3, semantic_s 0.3,
    codeintel_s 22.3, compaction_s 1.3, total_s 27.2; `stage_running` null; `watchdog_faults` empty; mtime
    2026-11-14 01:46:58Z.
  - `redis-out/a9/` and `grafana-out/a9/` are empty.
  - grafana `git check-ignore -v` prints `.gitignore:84:.claude/skills/*` for both SKILL.md paths, and line 84 of
    `HEAD:.gitignore` is `.claude/skills/*`. None of the five files A9 tried to add exists.
    `git status --short --ignored -- .claude governance` prints nothing.
  - The cited code lines say what the record says: `src/gov/adopt/fabric.py:705-708` raises `FABRIC_INCOMPLETE`, and
    `src/gov/adopt/stages.py:432-461` holds `_verdict` and `a5`.
- F-2 (not a stage failure) is borne out by the lead's A5 session logs. `.gov-runtime/scratch/lead/log/a5-redis.json`
  and `a5-grafana.json` hold session ids `4e66e97f-…` and `e9403ce5-…`, the target `governance/reviews/A5-path-map-verdict.md`,
  and the hook's rule-5 text. The rule-5 refusal is at `.claude/hooks/pretooluse.py:1090-1102`.
- The diff check: `git diff --name-only f2b1d38af..HEAD` lists `.tickets/DAEO-aks1.md` (excluded, see "Diff scope") and
  `experiments/W2-88/smoke-run.md`. The branch history in that range also adds and deletes `experiments/W2-88/proof_bc.py`
  and `experiments/W2-88/any-repository.md`, both inside `experiments/W2-88/`. No path is outside `experiments/W2-88/`.

Verdict S3: pass. No finding.

## S4: A5 on each copy

- redis: `git log -1 --format='%H %(trailers:key=Role,valueonly)' -- docs/audit/A5-path-map-verdict.md` prints
  `934b70218e6b43aac99c0da90ce131331d017700 independent-auditor`.
- grafana: the same command prints `c5edaf78c2806279ed504f9b7de581793735d54b independent-auditor`.
- In both commits the message's only trailer is `Role: independent-auditor`.
- The verdict files' `auditor_session` values, `4156cef7-6882-4672-89fe-5875c13ed3e1` (redis) and
  `fddde1db-ec8c-42b4-ad7a-481c33b8e9b9` (grafana), equal the record's A5 rows. Each copy's A5 adoption record repeats the
  same value.
- `git grep -n 'session: ' HEAD -- governance/adoption/` shows that the A0 to A8 records in both copies carry
  `session: lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1`, the session of every stage. Both auditor sessions differ from it.
- `verdict: pass` and the `path_map_hash` values (`6f9a287a…`, `ee5bcc47…`) equal F-2's text. The path-map sha256
  `5f72c863…` equals the record's.

Verdict S4: pass. No finding.

## S5 and F3: no questions, no measure, no validation; secrets

- `grep -c 'No questions, no measure, no validation\.'` counts 1 (line 15).
- `grep -inE 'hit@5|hit_at_5|right_e2e|right end to end|wrong claim|wrong_claims|mrr|recall|accuracy|query_ms|vector_scan_ms'
  experiments/W2-88/smoke-run.md` finds nothing (rc 1).
- I read the whole record. It holds no question set and no quality figure, and it claims nothing about memory's quality.
  MA's `estimate` block is quoted as gov's own estimate, with "no conclusion is drawn from it". A9's `measure` and
  `scale` blocks are not copied.
- The secrets appear by path and rule id only. I parsed the record's tables and compared them with MA's `secrets` field
  in `<name>-out/ma/memory-assessment.json`: redis 1 = 1 and grafana 148 = 148, identical as (path, rule) sets. The two
  MA runs on each copy are identical (O-5 holds). No value is quoted.
- `gitleaks detect --no-git --source experiments/W2-88/smoke-run.md --redact` (gitleaks 8.30.1) reports "no leaks found",
  rc 0.

Verdict S5: pass. Verdict F3: pass. No finding.

## F1: no clone in this repository; no workbench, ~/workspace or EXAMIN path

- `git ls-files` holds no clone path, and the branch's history holds none (see S1). Both clones are under
  `/home/usain/gov-os-runs/W2-88b/`.
- `grep -rIlE 'gov-os-workbench|/home/usain/workspace|~/workspace|EXAMIN APP|EXAMIN'` over `redis-logs`, `grafana-logs`,
  `aborted-1`, `aborted-2`, `redis-out`, `grafana-out` and `tmp` finds nothing (rc 1).
- A second search in different words (`grep -rIliE 'workbench|/workspace\b|examin'`) finds only
  `grafana-out/ma*/memory-assessment.json`. The hits are four of grafana's own files
  (`public/app/features/alerting/unified/triage/Workbench*.tsx`), not the workbench folder.
- In the record, the only hit is line 21, "No workbench, no `~/workspace`, no EXAMIN repository was read or cloned for
  this record". It names the folder in order to say it was not used. It is not a recorded command and not a path read
  (R2). No recorded command names any of those paths.
- I never listed or opened those folders.

Verdict F1: pass. One row, R2.

## F2: nothing written outside the copies and the record

- Before this record was written, `git status --short` (and `--porcelain`) in this worktree printed nothing.
- The branch's diff paths are all under `experiments/W2-88/` (see S3's diff check).
- The stage logs and outputs are all under `/home/usain/gov-os-runs/W2-88b/`.

Verdict F2: pass. No finding.

## Item 8: anything the logs contradict

I found no time, figure, outcome or finding text that the logs contradict. Beyond the checks above, these also hold:

- The `/usr/bin/time` peaks of grafana's A6 and A8 (6617236 and 6679012 kB).
- grafana A6's log: one `rebuild: slow: past 1800 s` line, no slot-wait line, `lexical`, `semantic` and `codeintel` all
  `recreated`, and `semantic.cut` count 47 with 47 paths.
- A8 on grafana has the same three `recreated` statuses and the same 47 cut files.
- The only `heavy_slot:` wait line in any stage log is in `A6-stopped-1.log` (01:47:41).
- No log has a `watchdog:` line (`grep -rln 'watchdog:'` rc 1).
- A6's commit `a0c8e7e0…` was committed at 2026-11-14T11:26:07+00:00.
- MA's estimate figures and the envelope (80000 nodes, 270000 edges, 2200000000 bytes, `within` false) are as quoted for
  both copies.
- redis's `minified` lists `deps/jemalloc/doc_internal/jemalloc.svg` with `by: header`.
- redis has 1972 tracked files at the end.
- `aborted-2/redis-logs/A3.log` ends with exit 1 and the quoted `ADOPT_STAGE_MISSING` text.
- The adopt skill's line 24 names the Independent Auditor role for A5, and line 41 names `--verdict <path>` for A7 and A10.

## Findings (rows; none blocks)

Classification: 2 findings, both rows (R1 out of scope, other; R2 in scope, other). None is in scope, ordinary work and
fails open or loses work, so this check proposes no round.

### R1: the logs' `wrapper:` line gives the two wrappers in the other order from the driver and the record

What happened: every `<label>.log` begins with `wrapper: env … bash …/heavy_slot.sh /usr/bin/time -f maxrss_kb=%M ...`,
which puts heavy_slot outside `/usr/bin/time`. The driver's line 28 (`.gov-runtime/scratch/lead/stages.sh`) runs
`setsid /usr/bin/time -o "$log.time" -f "maxrss_kb=%M elapsed_s=%e" bash "$SLOT" gov adopt …`, which puts `/usr/bin/time`
outside heavy_slot. Line 26 writes the header from a fixed string. The record follows line 28. What should have
happened: the header should give the order the driver ran. A reader who checks the record against the logs sees two
orders, and the order decides whether a slot wait falls inside `/usr/bin/time`'s elapsed figure. Of the stages in the
record, only the stopped first A6 run waited for a slot, and it has no row.
- Ordinary work: yes, because anyone who reads the record next to the logs meets the two orders.
- Consequence: other. The record is right and no figure in any row changes. It is out of scope: the driver is the
  lead's scratch tool, not the record.
- What would reverse it: evidence that line 28 of `stages.sh` at run time differed from the file now (the driver is in
  scratch and not versioned).

### R2: the record names `~/workspace` once, to say it was not read

What happened: line 21 says "No workbench, no `~/workspace`, no EXAMIN repository was read or cloned for this record".
The brief's F1 search for `~/workspace` as a path matches this sentence. F1's `Verify:` clause covers recorded commands
and logs, and neither names the path. This is a statement that the folder was not used, not a path read or written.
- Ordinary work: yes, because a scope statement naming the excluded folder is ordinary writing.
- Consequence: other. Nothing was read or written there.
- What would reverse it: a recorded command or log line that names a path under `~/workspace`, which this check did not
  find.

## What I probed and found sound

S1 to S5 and F1 to F3 as above. The record's description of the driver (setsid, the polling interval of 5 s, the
watchdog at 1572864 kB MemAvailable) matches `stages.sh` lines 15, 28, 31-37. The accounts of grafana's stopped first A6
run and its re-run agree with every driver log. F-2's claims are borne out by the lead's A5 session logs.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "R1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": [{"id": "R2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F2", "verdict": "pass", "findings": []}, {"kpi": "F3", "verdict": "pass", "findings": []}]}
```
