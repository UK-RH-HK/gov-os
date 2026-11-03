task: Independent probe (brief A3, read-only) of DAEO-clon (W2-112), profile FULL, at head 0b9deb2dd442: behaviour the acceptance tests miss.
status: DONE. The probe is complete; judgement **fail** on one blocking finding (F1). The research document's ACT for retiring the GPU-slot stopgap would remove the slot cap for every tree that lacks W2-112's worker. It is a document fix in the ticket's own paths.
work_completed: Read the ticket, its sources (DEC-979 item 4, DEC-374, DEC-397, DEC-1031 to DEC-1036, ADR-0001, ADR-0002 §2, P-RERANKER-1, ACT-RERANK-GPU-SLOTS-1, ACT-RERANK-WAIT-1, the interim module), the change from be02bb012537 and the acceptance suite. Ran 15 probes (p1 to p15) with the suite's stand-in model in temporary HOMEs with private slot folders. Looked read-only at the real reranker log, the live service and the slot holders. Ran one `gov retrieve`. Checked commit scope and role trailers. Answered the brief's question on serial failure (d).
files_changed: none in the repository. Scratch only, under /tmp/gov-os-lead-W2-112/rev/: a helper, probe scripts p1 to p15, and a five-file copy of the reranker modules with another pin.
evidence:
- **p1:** with both slots held and no interim module, searches through the installed `gov`'s code and the main checkout's code loaded a model at once (0.02 s). With the module they waited 5.01 s and went unranked. W2-112's tree never loaded.
- **Machine:** 64 of 65 checkouts and the installed `gov` pin lack the worker's own slot rule.
- **p12:** with the lock files removed under two holders, a third reranker loaded.
- **p6:** a search was answered by a service running another pin, in both directions, with no fallback and no log line.
- **p5:** a sandbox-like fallback was scored, the log stayed empty and the status read 0/0.
- **p9 and p13:** a cached fallback reranker kept its slot after the service returned. A cached "no slot" answered "unavailable" in 0.0 s with both slots free.
- **p2:** a search arriving at the idle end fell back.
- **p4:** a hung service stayed alive past its idle time, holding its slot.
- **p3:** with the socket removed, a search took 67.2 s. With the lock also removed, two services ran.
- **p15:** with an idle setting of 0, the service crashed after READY and left a stale socket.
- **Sound:** p7, p8, p10, p11, p14.
- **Real log:** READY at 14:11 and 14:26 only.
tests: no suite re-run (the lead's results read from `.gov-runtime/scratch/lead/log/`); 15 probe scripts run, results in the record.
discoveries:
- (1) Only W2-112's `rerank_worker.py` carries its own slot rule. The installed `gov` (pin-5c401220) and 64 other checkouts rely on the interim module alone.
- (2) Requests carry no pin, so the service answers with whatever pin its starter's tree carries.
- (3) Sandboxed sessions' fallbacks are never logged, and `gov status` shows 0.
- (4) Serial failure (d) is the embedder's, not the reranker's.
- (5) A fallback private reranker stays loaded for its process's life.
risks:
- F1: if §5 is applied as written after the merge, rerankers from the installed `gov` and unmerged worktrees load on the GPU without a slot (DEC-1031's crash state).
- F2: once a ticket changes the reranker pin or the service code, searches can be answered silently by another tree's model.
lessons:
- Run probes with `python3 -B`. Importing the worktree's test modules otherwise writes `__pycache__` into the repository.
- The suite's `Box` makes hermetic service probes cheap, given a short TMPDIR in the scratch folder.
- A machine-wide service shared by every tree needs a pin handshake.
proposed_decisions: none. Suggested routing is in the record.
unresolved:
- The embedder's own state during the 15:29 to 15:44 window; not reproducible from here.
- F2's protocol choice, for W2-32.
- Whether F3 belongs to W2-127 (the sandbox's write rule) or to the wording of `gov status`.
recommended_next_action: Moderator triage. F1's fix rides along in the ticket's resume (DEC-802): rewrite §5 to keep the module until the installed `gov` and every tree carry the worker's own rule, and drop step 3. Then re-check §5 alone.

---

```yaml
type: probe
task: DAEO-clon
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: 0b9deb2dd442
```

## Probe record: DAEO-clon (W2-112) at 0b9deb2dd442

**What was probed.**
- **Head:** 0b9deb2dd442, the lead's checkpoint over the engineer's 352d8d161503.
- **Change:** be02bb012537 to HEAD over the allowed paths: `rerank.py`, `rerank_service.py` (new), `rerank_worker.py`, `retrieve.py`, `status/command.py`, four unit test files and the research document.
- **Code under test:** `/home/usain/gov-os-worktrees/W2-112/src/gov/__init__.py`, set per command. Every probe session and the `gov retrieve` ran this worktree's `src/`.

**How it was probed.**
- **Probes:** 15 (p1 to p15). Each ran in a temporary HOME under `/tmp/gov-os-lead-W2-112/rev/`, built by the acceptance suite's own `Box`: a real venv holding the stand-in model and a stand-in torch, a private GPU-slot folder, a slot wait of 5 s and no network. Each box ended its own processes.
- **Real machine, read-only:** `~/.cache/gov-os/`, the live service, slot holders via `/proc`, the installed interim module, and every checkout's reranker worker.
- **One real `gov retrieve`.**
- **Scope:** git log, diff and trailers.

### Found sound (run)
1. **Cold start racing 40 searches** (model load 3 s): all 40 were scored with their own scores, in a private reranker's order. One model load, one service, no fallback; the slowest took 6.7 s (p7).
2. **Interim module beside the product's rule:** a private fallback holds exactly one slot, and the service takes its own slot without the module acting on it (p8). The older module (`.dec1031`) marks its slot the same way. With either version, W2-112's service and worker never run on the CPU (read).
3. **SIGTERM at HEAD:** the socket is removed, END is logged, and the next search starts one fresh service (p14). The real 14:11 service left a stale socket on 775c58eda031, before the handler existed; the research note documents this.
4. **An ordinary `gov retrieve` through the CLI** (p11):
   - Service up: `rerank.by` is the service, on cuda, and the bundle is reranked.
   - Service down: a private reranker, with its reason, reranked.
   - Down with both slots held: "unavailable" with both reasons, `merge.reranked` false, 5.7 s.
5. **`gov status`'s reranker part** (p10):
   - A 243 MB log of one million lines is counted in 0.63 s (574 MB peak).
   - One bad byte makes the part "not read", named; `gov status` does not crash.
   - An absent log reads 0/0 (see F3).
6. **Socket permissions:** the real socket is `srw-------` in a `drwx------` folder, with no network port (the acceptance tests cover the port).
7. **Scope and the acceptance tests:**
   - The engineer's product commits (d26e5a2cd3bd, 775c58eda031, 352d8d161503; Role: engineer) touch only the allowed paths.
   - Every commit touching `tests/acceptance/W2-112/` carries Role: independent-test-designer.
   - HEAD's acceptance folder is identical to the designer's 9af602dc8545.
   - No implementer changed the acceptance tests, and nothing was written outside the ticket's paths.
8. **Serial failure (d) is not the reranker's doing** (asked by the brief):
   - The assertion that failed is the semantic route's availability for DQ-A-08, i.e. the embedder. It is checked before `merge.reranked`, and every query checked before DQ-A-08 passed both assertions.
   - The real `rerank.log` holds no FALLBACK or REFUSED line at all, only READY at 14:11 and 14:26. Every fallback appends a line, cached ones included.
   - The one service (pid 1806803) started at 14:26:23 from HEAD's product code, after 352d8d161503 at 14:18:52. Its environment carries no idle or slot override. It ran without a break through the serial run and holds slot 1.
   - The serial run was not sandboxed, so any fallback would have been logged.
   - The 6.4 to 6.8 s per query of (c) fit a wait on the query embedder; a warm rerank takes a fraction of a second.

### Findings

**F1: The research document's ACT for retiring the stopgap (§5) removes the GPU slot cap for every tree that lacks W2-112's worker.** Severity: high. KPI: success-7.
- **Done:**
  - Read §5. It says to apply the ACT "only after W2-112 has merged", claims removing the module "changes nothing in behaviour", and has a step 3 that removes the slot lock files once `fuser` shows no holder.
  - Counted which reranker workers carry their own slot rule.
  - p1: both slots held, one search through the installed `gov`'s code and one through the main checkout's code, each without the module (the state after the ACT) and with it (today).
  - p12: both lock files removed while two rerankers held them, then one search.
- **Happened:**
  - Only W2-112's worker carries the rule. The installed `gov` (re-pinned 2026-10-28 under DEC-935; next re-pin at ACT 2) and 64 other checkouts (the main checkout, the merge-queue clone, 62 worktrees) rely on the module alone.
  - At about 16:20, real slot 0 was held through the module by a private reranker that the merge-queue clone started from its old worker.
  - p1: without the module, both old trees loaded the model at once beside the two held slots, making a third reranker. With the module, they waited and went unranked. W2-112's tree never loaded.
  - p12: a new service took a fresh lock file and loaded, giving three rerankers on two slots.
- **Should have happened:**
  - Retiring the module must not lift the cap for any process that can start a reranker from this environment.
  - The precondition should be: after the installed `gov` and every tree carry the worker's own rule (ACT 2's re-pin, the open worktrees merged). Until then the module stays; p8 shows it is harmless beside W2-112's worker.
  - The lock files should never be removed. They are empty, and removing them only opens p12's race.
- Scope: in. KPI 7 makes this ACT the lead's deliverable, and §5 is in the ticket's research document.
- Ordinary work: yes, because the operator applies the ACT as written once the ticket merges, while the installed `gov` and every worktree not yet merged keep starting private rerankers with their old worker in ordinary searches.
- Consequence: fails open. The GPU slot rule is bypassed and more rerankers than the budget reach the GPU, the state of the crashes DEC-1031 records.

**F2: The service answers with whatever pin its starter's tree carries; requests carry no pin.** Severity: medium (latent today). KPI: success-1, success-3, failure-3.
- **Done (p6):** a copy of the five reranker files, with only `REVISION` changed to `w2-32-new-pin`, run against the same HOME in both orders.
- **Happened:** that tree's search was scored by a service that loaded e61197ed…, with no fallback and no log line. In the other order, this worktree's search was scored by a service that loaded `w2-32-new-pin`.
- **Should have happened:** a search is answered only by a service with the caller's model and revision (for example, the request names its pin and a mismatch falls back, named).
- Scope: in.
- Ordinary work: no, because at this head all 65 checkouts pin the same revision and only this tree has the service. The risk arises with the first change to the pin or the service, W2-32 first. DEC-732 would then route that tree's real-HOME measures to another tree's service. Under DEC-803 this is an entry criterion of that ticket.
- Consequence: fails open when it arises: a new pin's measure or test can be answered by the old model.

**F3: A sandboxed session's fallback is neither logged nor counted, and `gov status` reports 0 as if measured.** Severity: low to medium. KPI: success-4.
- **Done (p5):** a session that cannot make a Unix socket (the suite's shim) and cannot write `~/.cache` ran one search. The read-only `~/.cache` was set up with bubblewrap, matching the launcher's sandbox, which lets a session write only to its temporary folder and its runs folder. Not run inside the real launch sandbox.
- **Happened:** the search fell back to a private reranker and was scored. Nothing was logged, and the reranker part read `fallbacks 0, service_refusals 0`.
- **Should have happened:** every fallback is counted (KPI 4), or the count is labelled as covering only sessions that can write the log (DEC-449, DEC-454).
- Scope: in.
- Ordinary work: yes, because until W2-127 every sandboxed search falls back (DEC-1035 (c)).
- Consequence: other. A status figure under-reports.

**F4: The fallback private reranker is kept for its process's life.** Severity: medium. KPI: success-4, success-7.
- **Done:** p9 and p13, in one long-lived process, as in a test run or a measure.
- **Happened:**
  - p9: after a fallback, the service came back and answered, but the private stayed loaded, holding the second slot. Another session's fallback then went unranked after 8.6 s ("no GPU slot freed").
  - p13: a private that had found no slot was never retried. With both slots free, the next search returned "unavailable" in 0.0 s with the stale reason.
- **Should have happened:** a fallback private ends or is retried once its need has passed, and a transient "no slot" is not cached.
- Scope: in. The caching existed before ("as today"), but this ticket made the private a fallback, and the slot rule makes its failures transient.
- Ordinary work: yes, because long runs rerank in one process, and a single service blip while both slots are busy is enough.
- Consequence: other. Searches go unranked, named.

**F5: A search arriving at the service's idle end falls back instead of starting a new service.** Severity: low. KPI: success-1, success-4.
- **Done (p2):** idle time 2 s; a search sent the moment the socket vanished, with and without 1.5 s of simulated CUDA teardown.
- **Happened:** both times the search fell back to a private reranker, logged as "the service this search waited for ended before it listened".
- **Should have happened:** an idle end refuses nothing, so the search should start a new service.
- Scope: in.
- Ordinary work: yes, but rarely (a search within about a second of the 15-minute idle end).
- Consequence: other. An extra model load and a logged fallback.

**F6: A service that hangs, or whose model fails on every request, never recovers while searches keep arriving.** Severity: medium. KPI: success-2, success-4, failure-1.
- **Done (p4):** request time limit 3 s, idle 4 s.
- **Happened:**
  - Hung: each search waited the full time limit, then fell back. With the other slot taken, a search went unranked after 8 s. The service was still alive 6 s past its idle time, holding its slot.
  - Failing: every request got an error and every search fell back. The service ended only after a quiet idle period.
- **Should have happened:** a service that cannot answer ends or is replaced.
- Scope: in.
- Ordinary work: yes, because a GPU fault, as DEC-1031 records, can stick or fail the model call.
- Consequence: other. Each search is bounded but slower (30 s by default), then ranked by a private reranker or left unranked.

**F7: Removing the socket, or the start lock, under a live service.** Severity: low. KPI: failure-2.
- **Done:** p3.
- **Happened:** with the socket removed, the next search waited 67 s before falling back, and others would too until the idle end. With the lock removed as well, a second service started beside the first.
- **Should have happened:** a search detects an unreachable live service sooner, and the lock cannot be replaced while it is held.
- Scope: in.
- Ordinary work: no, because it needs files in `~/.cache/gov-os/` deleted by hand; nothing in `gov` removes them.
- Consequence: other. The two-slot cap still held.

**F8: An idle setting of zero, inherited from the starting search, crashes the service after it binds.** KPI: success-1.
- **Done (p15):** a search run with an idle setting of 0.
- **Happened:** the service logged READY, crashed at its first accept and left a stale socket. Each search then paid two model loads (a service that crashed, then a private). The logged reason, "ended before it listened", is wrong: it had listened.
- **Should have happened:** the setting is checked, or the service ends cleanly and removes its socket.
- Scope: in. Ordinary work: no. Consequence: other.

### Observations (no finding)
- **O1 (read, not run):** a W1-19 case links the real reranker environment into a temporary HOME. It will now start a short-lived service from the real environment. That service takes a real `/tmp` slot (or waits up to 20 s for one) and opens a CUDA context before failing for lack of the snapshot. Relevant to W1-19's revision under DEC-1033 item 3.
- **O2:** below the service's share, the private fallback loads with no free-memory check. This follows DEC-1036's wording, and the acceptance README notes it is unstated. It is a question for the GPU budget (DEC-1032 (iii)).
- **O3:** the service still scores a request after its caller has timed out.
- **O4:** success-5's "before" figure for 10 searches is CAPACITY-1's figure plus one private reranker's measurements, not a fresh run.

**Classification:** 1 blocking (F1: in scope, ordinary work yes, fails open); 7 rows (F2 to F8: ordinary work no, or consequence other).

**Recommendation:**
- F1's fix rides along in the resume (DEC-802).
- F2 becomes an entry criterion of W2-32 and of any ticket that changes the pin or the service (DEC-803).
- F3 goes to W2-127 or to the wording of `gov status`.
- F4 to F8 become Wave 3 rows.

```verdict
{"kpis": [
 {"kpi": "success-1", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F7", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F8", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "success-2", "verdict": "pass", "findings": [{"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "success-3", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "success-4", "verdict": "fail", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "success-5", "verdict": "pass", "findings": []},
 {"kpi": "success-6", "verdict": "pass", "findings": []},
 {"kpi": "success-7", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "failure-1", "verdict": "pass", "findings": [{"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "failure-2", "verdict": "pass", "findings": [{"id": "F7", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "failure-3", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}
]}
```

Success-4 is marked fail only because the "each fallback is logged and counted" clause does not hold for sandboxed sessions (F3). Its findings are "other", so it does not block.

---

- **`gov.__file__`:** `/home/usain/gov-os-worktrees/W2-112/src/gov/__init__.py`
- **Read refusals met:** 0.
- **`gov retrieve` used:** yes, once, on ACT 2's re-pin of the installed `gov`. The lead's running service answered on `cuda:0`; no new service was started (the real log is unchanged).
- **Processes:** every probe box ended its own processes. Checked afterwards: no process carries my scratch folder in its arguments or as its HOME. I did not start or stop the real service; the lead's pid 1806803, running since 14:26, was left as it was.
- **Scratch:** 30 files and folders, 164 KB, under `/tmp/gov-os-lead-W2-112/rev/`. The worktree is clean at 0b9deb2dd442.