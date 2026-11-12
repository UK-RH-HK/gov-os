# W2-112 (DAEO-clon): FULL review of the shared reranker service's merged code (independent auditor)

You are a fresh **independent auditor** (Opus 5.5, effort high, class C2; RUBRIC-2, DEC-1120: reviewers run on Opus at
high, the old max is replaced), launched by the CTO (orchestrator DAEO-sdxk, session b40cba91, 2026-11-11) under ticket
`DAEO-clon` (W2-112) from the worktree `/home/usain/gov-os-worktrees/W2-20` (W2-112 has no worktree of its own; W2-20's ticket `DAEO-r30l` carries the CTO's reviews, so the launch names `LAUNCH_TICKET=DAEO-clon` from that tree). Your job is one **FULL, read-only review of the
ticket's merged code at the head of `w2/integrate`**, judged on the ticket's KPI lines alone (DEC-1131), producing a probe
record text that the CTO commits as `docs/probes/DAEO-clon/PR-DAEO-clon.md`. You cannot write it: you return it as text.
The record is the evidence the ticket's formal close needs (LIFT-CLOSES-1: `gov accept W2-112` gave 59 of 59, but a FULL ticket's close is refused with `PROBE_MISSING` without one, and the ticket was accepted as built in D-1 with no review of its final code). Nothing here is a round of changes: you find, you
do not fix.

## Step 0 and the common rules

- **Step 0, the sandbox check, reported first in your return** (the launcher's `EMG-d4b-launched.md`, copied beside this
  brief): (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-clon','w').write('x')"` must fail; (b)
  `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b)
  failed, stop and return. Then `ps -eo pid,args` on its own (no pipe): report that no ollama or llama-server process is
  yours.
- Read first, whole: `EMG-common.md` and `EMG-d4b-launched.md` beside this brief. The CTO's lift files (`LIFT-common.md`,
  `NIGHT-common.md`) are not copied for you; their rules that apply are restated in this brief, with these changes to the old
  text: the lift's closes are done; the main tree (`/home/usain/Dynamic-Agentic-Engineering-OS`) must stay clean (you never
  write there); the next free decision id is DEC-1137 (yours to propose, never to write); your temporary folder is the
  sandbox's own `TMPDIR` (never a new `/tmp/gov-os-emg-*` folder).
- **You are read-only.** Your tools are Bash, Read, Grep and Glob; you have no Write or Edit. Write only under your own
  `TMPDIR` (a probe script goes there as an inline `python3 -I -c '...'`, or a file made one simple command at a time). Never
  `git add`, `commit`, `stash`, `checkout`, `reset`, `merge`, `push` in any repository you did not clone yourself, and never
  commit anything at all: the record is returned as text and the CTO commits it. A reviewer commit anywhere in the ticket's range
  would make the probe record invalid (DEC-137). If the Write tool is refused when you try it, do not make the file another
  way; say so in your return.
- **The guard's rules hold.** No installs. No reads of secrets or of held-out material; never open `~/gov-os-eval`,
  `~/gov-os-runs`, `~/gov-os-wall-trees`, `~/gov-os-operator`, any folder named `hidden`, `memory-verdict` or
  `memory-verdict-2`, or the real `~/.claude`. A refusal is taken, never routed round (a false refusal is worked round by an
  equivalent form, named in your return). **Refused twice for the same call: stop and say so; no third try.**
- **No real model, embedder, reranker or GPU job, and no network (DEC-1064, DEC-1065).** Never run `gov retrieve` or
  `gov context`; read code with Grep and Read. Every test of yours uses stand-ins.
- **Waits and stops by pid only** (`tools/proc.sh`: `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh`),
  never the Monitor tool, never a process-name match (`pgrep -f`, `pkill`, `killall`). Run a long command in the background and
  wait on its pid.
- **Under `.gov-runtime/` and in everything you return, write commit hashes as 12 digits** (row W2-L423's rule), and write none
  of the keywords `tools/keyword_warn.py` looks for (they are written in parts in that file; never copy them out).
- **Scratch budget: 30 GB and 2,000,000 files and folders** outside the tracked tree. Report `du -sh` and `du -s --inodes` of
  your `TMPDIR` in `evidence`, and remove your clone and probe folders when done.
- **Context:** there is no token cap: use your model's full window; before compaction the hook writes your checkpoint and the summary opens with the read-first line (the owner, 2026-11-12, replacing DEC-1118 (A)).

## The head you review: a clone of `w2/integrate`

Your own worktree is **hundreds of commits behind** `w2/integrate` and is not what is merged. Do not judge its files. Make a
clone at the start and read and run everything from it:

```
git clone -q --no-hardlinks --single-branch -b w2/integrate file:///home/usain/Dynamic-Agentic-Engineering-OS $TMPDIR/clone
git -C $TMPDIR/clone rev-parse --short=12 HEAD
```

The head was `7b5c3cb94fd9` when this brief was written. **Review the clone's head at your start** and name its 12 digits as
the record's `probed_commit`; if it is not `7b5c3cb94fd9`, run `git -C $TMPDIR/clone diff --stat 7b5c3cb94fd9 HEAD -- src/gov/retrieval src/gov/status tests/unit/retrieval tests/acceptance/W2-112 docs/research/W2-112-shared-reranker.md`
and say what moved. Run code with `PYTHONPATH=$TMPDIR/clone/src`, and with `HOME` set to an empty folder under `TMPDIR` (add
`PYTHONUSERBASE=/home/usain/.local` if the empty HOME hides pytest or another module).

## The frame: the ticket's KPI lines (judge only these, DEC-1131)

Ticket `DAEO-clon` (`.tickets/DAEO-clon.md` in the clone: read it whole, including its notes). Its KPI lines are below, in the
ticket's own words, with the id each takes in your verdict block. **Judge each line by what it says and by its `Verify:`
text where it has one. A thing the ticket does not state is not a finding; a thing a line does state that is not met is.**
A failed line is `"verdict": "fail"` (a failed line blocks READY, DEC-1131 (3)).

- **S1**: One reranker process serves every session on the machine: the same pinned model, revision and environment as today (ADR-0002 §2, DEC-397), listening on a local socket in the user's own folder (mode 0600, no network port), started on demand by the first search that needs it under a lock (two searches starting together start one service), ending itself after a set idle time [DEC-979 item 4, P-RERANKER-1]
- **S2**: Many sessions at once: 20 concurrent searches are answered by that one process, each with its own scores for its own texts, in arrival order, with a cap on a request's texts and a time limit per request [DEC-979 item 4]
- **S3**: The same answers: for the same inputs on the same device, the order and the scores match a private reranker's (within float rounding; ties keep the given order), measured on the 20 visible memory questions and, after W2-61h, the 48 [DEC-979 item 4, DEC-374]
- **S4**: If the service is down (it cannot start, does not answer within about 2 s, or answers with an error), the search falls back to a private reranker as today; where that cannot start either (a sandboxed worker, the memory floor reached), the fused order is kept and the bundle is marked `rerank: unavailable` (DEC-374); a search never fails or hangs because of the service; each fallback is logged and `gov status` counts them [DEC-979 item 4, DEC-374]
- **S5**: Measured, in docs/research/W2-112-shared-reranker.md: memory with 10 concurrent searches before and after (today up to 9 rerankers, 9.4 GiB at peak), and the searches' times [DEC-979 item 4, CAPACITY-1]
- **S6**: The service runs its one model on the GPU, within the GPU budget (DEC-1032: the embedder first, about 3.5 GB; the shared reranker second, about 2.5 to 3.5 GB; at least 2 GB headroom); it holds one of the two GPU reranker slots (it waits for one like any reranker, or fails named), so at most one private reranker runs beside it; below its share it does not start (never on the CPU) and searches fall back through the slot rule or go unranked, named; measured: the GPU's memory with the embedder and the service under 20 concurrent searches [DEC-1032, DEC-1033, DEC-1036]
- **S7**: When it lands, the stopgap that caps private rerankers on the GPU (the `gov-reranker-gpu-slot.pth` in the reranker environment, ACT-RERANK-GPU-SLOTS-1) stays in place as the machine-wide guard (it caps every reranker, whatever its tree's commit): §5 of the research document records that it is not to be retired by an ACT now, and is retired only when old code fails closed by construction (a later ticket) [DEC-1048, P-W2-112-F9 (c)]; and when the service is down the search falls back to a private reranker through the GPU slot rule (it waits for one of the slots, else the search goes on unranked, named: `merge.reranked` false with its reason); it never runs a reranker on the CPU (DEC-1033: on the CPU a query takes over 100 s) [DEC-1032, DEC-1033]
- **F1**: A search that fails, hangs, or returns another session's scores because of the service.
- **F2**: Two services started at once, or a socket another user can open.
- **F3**: Answers that differ from a private reranker's on the same inputs and device.

**The verdict block carries one entry for each of these 10 ids, in this order:** S1, S2, S3, S4, S5, S6, S7, F1, F2, F3. (`F1` and on are the ticket's failure lines, in the order above.)

**Scope (the ticket's `allowed_paths`; "in scope" means a finding about these files or about how the KPI lines hold through them):**

- `src/gov/retrieval/rerank.py`
- `src/gov/retrieval/rerank_worker.py`
- `src/gov/retrieval/rerank_service.py`
- `src/gov/retrieval/retrieve.py`
- `src/gov/status/command.py`
- `tests/unit/semantic/test_rerank_process.py`
- `tests/unit/orchestration/test_gov_reranker_gpu_slot.py`
- `tests/unit/status/test_status.py`
- `tests/unit/retrieval/test_w2_112*`
- `docs/research/W2-112-shared-reranker.md`

Code outside these paths is reachable context (read it to judge a line), but a defect that lives only there is `scope: out`.

## What has changed, and what has been reviewed before (facts; judge the code, not this history)

- **No earlier review judged the whole ticket's final code.** Two partial reviews existed as scratch, neither committed:
  a round 1 of the original build (2026-11-02; a commit message names its F1, repaired in `ed0891667f46`), and a narrow review of the
  DEC-1068 memory release (2026-11-06, at `5bf20b53224d`): the service empties the GPU cache after each request and logs the
  allocated and reserved MiB, `7448ce364c6e`. You judge all ten lines on the head as it is now.
- **Other tickets changed the judged files after those reviews, and are in the head:** W2-137 (`8586d60f7af3`, merge `213abadc1446`):
  the request cap raised from 16 to 64 and the service names a request over its bound; W2-145 (`86f1af6e586f`, `e6f9bbaff929`,
  `1be3e47debb4`): see the next point; W2-138 (`dcda270113f0`: the store's commit and folder in every search result), W2-150
  (`28c586930555`: static import closure, names moved into `gov.util` and `gov.store`), W2-135, W2-32 S7 and S11 in `retrieve.py`
  and `rerank.py`. The acceptance cases were revised after them: `aadce89d67c5` (the cases that assumed a private fallback, now
  W2-145's S1 to S4), D-4's cut (55 to 48 cases in the full run), D-10 `73e33d7b32bc`.
- **W2-145 amends what S4, S6 and S7 say about a private fallback.** Ticket `DAEO-2tfd` (merged; owner's DEC-1048 (5), DEC-1046 (1),
  DEC-1097 (8)): the shared service is the only reranker; a search it cannot answer stays **unranked and named**
  (`merge.reranked` false with its reason, the fused order kept), never a private reranker on the GPU or the CPU; the service
  holds every reranker GPU slot. The ticket's own words for S4, S6 and S7 were not edited. **The CTO's reading, which you apply:** what
  those lines still demand is that a search never fails or hangs because of the service, that the outcome is named and counted, that
  nothing runs on the CPU, and that the stopgap stays in place (S7's `.pth` and research document section 5). A missing private
  fallback is not by itself a failure of S4, S6 or S7. If you think that reading is wrong, say so in one row; do not fail a line
  on it. W2-145 has its own ticket and review: do not re-review it, use it as context.
- **A known open point, not a finding:** S5's 48-question half (after W2-61h) is not yet measured (D9-FATES: met in part; the
  research document says so under "After W2-61h"). Judge that the document says this plainly and that its other half (memory with
  10 concurrent searches before and after, and the searches' times) is present and consistent with the code; if the document
  misstates either, that is a finding.
- **Rows already carried from the memory-release review** (name one by its description if you meet it independently; it is a row, not
  a new round, unless you show a worse consequence): `rerank.log` is never trimmed and `gov status` reads it whole; a CUDA error
  message spans several log lines; a service that has hit a sticky CUDA error lives on answering only errors.


## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.
- **How reviews converge (owner, standing, DEC-1010 item 1; in force for the CTO, every lead, reviewer and QA engineer):**
  - **A moderator, not a circle of reviewers:** the QA engineer (or the Senior Engineer; until the three layers start, the CTO) triages every finding against the ticket's own scope and KPIs. A finding outside the scope, or one that needs an unusual construction, becomes a Wave 3 row, never a round.
  - **A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work.** Everything else lands as a recorded row.
  - **At most two review rounds.** If something still blocks after that, it goes to the owner once, with options; no more routine exceptions.
  - **READY is computed by code, not declared by an agent:** each reviewer returns a structured verdict per KPI line, a fenced `verdict` block in the probe record: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`; the close (and the merge queue's pre-check) computes READY from it: no finding that is in scope, ordinary work yes and fails open or loses work. A lead never writes a verdict over a reviewer's.

## What to do

1. Read the ticket, then the code in scope at the clone's head, then the tests that map to each KPI line (the acceptance
   folder's README maps lines to cases; do not take the map as proof: read what the case asserts).
2. Judge **every KPI line** pass or fail from the code and your own probes (planted folders and stand-ins under `TMPDIR`; never
   a live root). Look hardest where a failure would fail open or lose work: two services started at once (the start lock) or a socket another user can open (the socket's mode and folder, no network port: failure line 2); a search that fails or hangs because of the service (the time limits, a service that dies mid-request, a request over the cap, the service's one thread and its backlog); one session's scores reaching another (S2, failure line 1); the idle end; the memory release (after each answer, never breaking it: judged through F1, S2 and S4); the answers' match to a private reranker's reference (S3, failure line 3); that every fallback is named and `gov status` counts it (S4).
3. Run the **scoped** tests only, through the heavy-job gate, with this exclusion on every run of a whole folder
   (`-m "not local_only" -k "not real and not green_here and not time_limit"`) and say what it left out:
   `tests/acceptance/W2-112/` (59 cases), `tests/unit/retrieval/test_w2_112_shared_reranker.py` (with `GOV_TESTS_OPTIN=lifted,breadth`: without it four parametrised rows are deselected), `tests/unit/semantic/test_rerank_process.py`, `tests/unit/orchestration/test_gov_reranker_gpu_slot.py` and `tests/unit/status/test_status.py`. The service's real process and its Unix socket run with stand-ins for torch and the model (an earlier review ran them in this sandbox); a case that needs a real model or GPU is left out by the exclusion: name it
   Command form: `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env PYTHONPATH=$TMPDIR/clone/src HOME=<empty folder> PYTHONUSERBASE=/home/usain/.local TMPDIR=$TMPDIR python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`
   (add `GOV_TESTS_OPTIN=lifted,breadth` for the opt-in cases). Never the full suite (DEC-968). The CTO's own results, which you
   do not re-run: `gov accept W2-112` at the lift's closes (LIFT-CLOSES-1): 59 passed, 0 failed, 0 skipped, pass, 84 s; cases per line: S1 7, S2 5, S3 3, S4 14, S5 2, S6 13, S7 15, F1 13, F2 7, F3 3. If the gate or the sandbox will not run a case, say which and why; never run it outside the gate.
4. Classify each finding: id `FR-1`, `FR-2`, ... (a FULL review's own ids, so none collides with an earlier round's), its KPI line,
   `scope: in|out`, the two lines below, `Reversed by:` (what evidence would make it not a finding), and how you showed it
   (the call, the file and lines).
5. Compose the record (below) and return.

## The verdict block and the probe record form

The verdict is one fenced `verdict` block in the record, one entry for **every** KPI line above (`pass` or `fail`, with its
findings, possibly none), in exactly this form (the close computes READY from it by code; you never declare READY):

```verdict
{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "FR-1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```

The record's form is the existing probe record `docs/probes/DAEO-u4oz/PR-DAEO-u4oz.md` (read it in your clone: it is the model,
written 2026-11-11). The CTO writes its "The lead's judgement" section; **you write the rest**, between `PROBE_MD_BEGIN` and
`PROBE_MD_END`, in this order:

1. The YAML front matter, exactly these keys: `type: probe`, `task: DAEO-clon`, `reviewer_session: not known` (the CTO fills it
   from the launch log), `implementer_session: not recorded` (the CTO fills it), `reviewer_wrote_nothing: true`,
   `commissioned_by: orchestrator`, `judged_by: orchestrator`, `judgement: pass` (only if no finding is in scope, ordinary work
   yes and fails open or loses work, and no line is marked fail; else `fail`), `probed_commit: <12 digits>` (the CTO expands it
   to the full id: the close gate needs the full id, and `.gov-runtime/` takes 12 digits).
2. `# Probe record: W2-112 (DAEO-clon) <title>, FULL review of the merged code (DEC-1010, DEC-1131)`.
3. `## The reviewer's record (as returned)`: a short plain-language summary (does every line pass; what blocks, if anything; what
   lands as rows), then the twelve fields in a fenced block, as in the model.
4. A line `task: DAEO-clon`, a line `decisions:` (the decisions you relied on, each as DEC-n), a line `probed_commit: <12 digits>`.
5. `**Scope.**`, `**Method.**` (the probes, with counts), `**Probed and found sound.**` (numbered, by KPI line, with file and
   lines), and `**Findings**`: each with its KPI line, `scope`, `Ordinary work: yes|no, because ...`,
   `Consequence: fails open|loses work|other`, `Reversed by:`.
6. `**Classification:**` on one line (how many yes/fails open or loses work, yes/other, and rows marked no), then the `verdict` block.

## Return

As your final message: **the twelve labelled lines first**, each label at the start of its own line (`task`, `status`,
`work_completed`, `files_changed`, `evidence`, `tests`, `discoveries`, `risks`, `lessons`, `proposed_decisions`, `unresolved`,
`recommended_next_action`), with step 0 and the `ps` check first in `evidence`, the clone's head in `evidence`, the tests and
what the exclusion left out in `tests`, `files_changed: none`; status DONE, PARTIAL or PACKAGES. Then a line `PROBE_MD_BEGIN`,
the record text of the form above, and a line `PROBE_MD_END`. Estimate: 45 to 60 minutes, about $5.
