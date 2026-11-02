---
type: probe
task: DAEO-u4oz
reviewer_session: 5042a938-fb97-4767-a2a2-9b5cc0765e94
implementer_session: f5463fda-38ba-4f6d-babf-5f8ddfe97366
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: b37b5c8f1741 (12 digits in this draft, DEC-911; the full id in a committed record)
---

# DRAFT, not committed: review 1 of W2-04 (DAEO-u4oz) at b37b5c8f1741, judgement fail (F1 blocks)

READY by verdict.py: False (success-5: F1 blocks, in scope, ordinary work, fails open).
The lead's triage (moderator rule, DEC-1010 item 1): F1 blocks (it is row W2-H034's own symptom, KPI 5);
F2, F3, F6 in scope, other: rows (may ride with the repair, DEC-802); F4, F5 out of scope: rows / packages.
Probed head (in full, once): b37b5c8f1741

## Verdict: fail

Classification (DEC-809): F1 in scope / ordinary yes / fails open (blocks). F2, F3 and F6 in scope / ordinary yes / other. F4 out / ordinary yes / other. F5 out / ordinary yes / fails open (a row).

### F1 — An emptied mandatory file is shown as read, with the empty-content hash and 0 tokens (KPI 5; S5; W2-H034)
- **What was done:** I built a project with a charter and a capability file CAP-P1, and a ticket citing both, and built its store from HEAD. I then emptied CAP-P1's file in the working tree, as a truncating write leaves it, and ran `gov context` and the check. I repeated this with a dependency ticket emptied, and with `--brief`.
- **What happened:** exit 0, `ok: true`. CAP-P1 is listed as a mandatory input, ACTIVE, `tokens` 0, with `sha256` and `constraint` equal to the empty-content hash (e3b0c442…). It is not marked not read, and the packet's tokens fell from 249 to 115. The check is green. The emptied dependency gives the same, and the brief summary (what the session-start hook injects) lists it as present. A file reduced to one newline is shown as read at 1 token.
- **What should have happened:** BLOCKED with a non-zero exit, naming CAP-P1 and its file (the file no longer holds the record the store lists), or CAP-P1 listed as not read. It should never be `ok` with the empty-content hash or 0 tokens. Register entries already behave this way, because their span is read from the store. The suite covers "emptied" only for the register; for a file of its own it covers deleted and no permission.
- **Where:** `src/gov/context/__init__.py:48-50` hashes whatever the working-tree file holds.
- **Window:** the working tree only. The close refuses a tree that differs from HEAD, and a committed empty file drops the record at the next load (then BLOCKED, not found). The packet a worker works from is what is affected.
- **Severity:** medium.
- Ordinary work: yes, because a truncating write on the file being edited (a redirect onto the file being read, a script that opens it for writing before reading) is a textbook accident, and the session-start hook builds the context at every start, resume and compaction without the agent asking.
- Consequence: fails open

### F2 — `further_batch` is empty when the room ends exactly on a batch's last item, or when the mandatory part fills the ceiling exactly (KPI 7; S7, S7a)
- **What was done:** on the ledger fixture I set `--budget` so the room equalled exactly the first batch, then exactly two batches, then zero.
- **What happened:** with exact room, 10 (or 20) items are stacked, `further_batch` is [] and `dropped` is [], while 39 (or 29) ranked items were left for lack of room. With zero room, `supplementary_batches`, `further_batch` and `dropped` are all empty: 49 items are left, and the packet looks the same as a lookup that found nothing. With one more token, the packet names the next item.
- **What should have happened:** `further_batch` begins with the first ranked item not stacked. S7 says "an empty list when nothing was left".
- **Where:** `src/gov/retrieval/supplementary.py:125-144`.
- **Severity:** low. It needs an exact token match, and a full last batch hints that more remains.
- Ordinary work: yes, because any build whose room ends exactly on a batch boundary gives it, by chance.
- Consequence: other

### F3 — The check is green when every ticket refuses
- **What was done:** a project of two tickets, each at 8,706 mandatory tokens; then the check.
- **What happened:** exit 0, two `REFUSED:` lines, "context-reproducibility: green (0 packet(s) built twice alike, 2 refused over the ceiling twice alike)".
- **What should have happened:** with no packet built, the check should say unmeasured, as it already does for "every ticket's context computation failed". The lead's P3 call covers named refusals but leaves this extreme open.
- **Where:** `src/gov/context/context_check.py:109-139`.
- **Severity:** low.
- Ordinary work: yes, because a project whose tickets all cite large files gives it; here 57 of 182 tickets refuse.
- Consequence: other

### F4 — 31 open or in-progress tickets refuse at the default ceiling; their closes fail late and count, and their sessions lose the context silently (out of scope)
- **What was done:** I ran `gov.context.context` over all 182 tickets of this worktree on the lead's store.
- **What happened:** 8 in-progress and 23 open tickets refuse with `CONTEXT_OVER_CEILING` (26 closed ones refuse as well; 1 open ticket is BLOCKED, DAEO-i89t, already known).
  - **In progress:** W2-11 (DAEO-k7hz, 16,405 mandatory tokens), W2-20 (DAEO-r30l, 11,194), W2-56 (DAEO-wnnz, 7,788), W2-61h (DAEO-h2k3, 9,985), W2-81 (DAEO-l78m, 18,161), W2-90b (DAEO-nqa2, 6,515), W2-91 (DAEO-a3u2, 10,106), W2-92 (DAEO-n0wb, 7,645).
  - **Open:** W2-12, W2-15a, W2-15b, W2-19, W2-24, W2-27, W2-32, W2-33, W2-46, W2-60b, W2-78, W2-82, W2-83a, W2-83b, W2-88, W2-93, W2-94, W2-98, W2-99, W2-112, W2-115, W2-117, and DAEO-2d6f.
  - **The close** builds the context only after its acceptance and regression runs (`src/gov/close/command.py:239-243`), and the `CONTEXT_FAILED` refusal there is counted (247, 335).
  - **The session-start hook** builds the brief context and drops every error (`template/governance/kernel/hooks/sessionstart.py:150-158`).
- **What should have happened:** the refusal itself is the specification working (S2). The merge cost should be decided before the merge (P-B). Statuses are as this worktree's `.tickets/` states them.
- **Severity:** medium (integration).
- Ordinary work: yes, because every close and session start of those tickets meets it after the merge.
- Consequence: other

### F5 — On a store older than HEAD, a source that HEAD retired satisfies the ticket (out of scope; a row)
- **What was done:** I built the store, committed a change retiring the ticket's capability source, did not reload, and ran `gov context`.
- **What happened:** exit 0, `ok`, the source shown ACTIVE, and nothing in the packet says the store is older than HEAD. The check correctly reports the store as unmeasured, and after a reload the context is BLOCKED ("is RETIRED").
- **What should have happened:** the specification puts stale-store handling only in the check and the close, and both do it. Whether `gov context` itself should name such a store needs a decision (P-D).
- **Severity:** low to medium.
- Ordinary work: yes, because worker stores lag their commits until the lead rebuilds.
- Consequence: fails open

### F6 — `supplementary_query` shows the whole text, but only its 12 longest words are searched (KPI 6; S6)
- **What happened:** for this ticket, only one of the title's three words ("reproducible") is among the 12 searched; "bounded" and "context" are crowded out by longer words of the KPI lines. The packet does not show which words were searched.
- **What should have happened:** S6 holds as written. Whether the title should always contribute, and whether the packet should show the searched words, is a row.
- **Severity:** low.
- Ordinary work: yes, because most tickets' KPI lines hold more than twelve words longer than their title's.
- Consequence: other

### Probed and found sound
- **Ceiling:** every `ok` packet I built held `tokens` = `budget.used` ≤ limit, with the ticket text whole.
- **Refusals:** named, with ticket, limit and mandatory size; DAEO-03pw fits at 5,996.
- **Decision hash:** DEC-860 is named by its span's own hash, not the register file's; file inputs keep their file's hash.
- **Reproducibility:** the same hash across processes and hash seeds; no network call at all, and the semantic module is loaded but never called.
- **RETIRED after a reload:** blocks, naming the record and its status.
- **Stacking:** strict rank order; `further_batch` begins at the first item that did not fit and is at most one batch long; no batch limit exceeds the room.
- **Stale store in the check:** reported as unmeasured.
- **Roles and paths:** engineer and test-designer commits are separate, and all within allowed paths.
- **Revised tests:** no W1-41, W2-54 or unit expectation was lowered.
  - W1-41's padded twin still catches an external reference counted as read content.
  - W2-54's relaxed premise ("same id or same path") is still met by `docs/adr/split.md`, one record cut into 12 chunks that share its id.
  - The unit case dropped its hash equality only because the rank is now the context's own; its dropped-list guarantee is still asserted.

judgement: fail

```verdict
{"kpis": [{"kpi": "success-1", "verdict": "pass", "findings": []}, {"kpi": "success-2", "verdict": "pass", "findings": [{"id": "F4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-3", "verdict": "pass", "findings": []}, {"kpi": "success-4", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-5", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]}, {"kpi": "success-6", "verdict": "pass", "findings": [{"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-7", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "failure-1", "verdict": "pass", "findings": [{"id": "F5", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}]}]}
```

guard_refusals:
- end of session | a recursive delete of my own probe folder in the session's temporary folder | the permission was not granted (a harness permission, no hook reason shown; not worked around) | true | 1
- read refusals met (DEC-849): 0

brief_gaps:
- The session-start hook is a second caller of `gov.context.context`, and it drops every error | "What you read", beside the close's `_build_context` | 3
- The close builds the context only after its acceptance and regression runs, and counts that refusal | the same place | 4
- A run with PYTHONPATH=<worktree>/src writes `__pycache__` beside src/ unless bytecode writing is off, and the sandbox lets the worktree be written | the DEC-732 standing rule | 2
- The suite's w2_04_support.py builds fixture projects and can be imported read-only | "What you read" | 2
