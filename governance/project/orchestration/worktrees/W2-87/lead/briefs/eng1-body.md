
# Brief: engineer, DAEO-s9qc (W2-87), batch 1 of 2 — the register as its entries

You are a fresh engineer. Ticket: DAEO-s9qc (W2-87), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-87` on branch `w2/W2-87`. This batch is the owner's register defect only (DEC-952 item 1); the authority order is a later batch — do not start it.

## What you read

- `.tickets/DAEO-s9qc.md` (read-only) and the decisions DEC-952 (item 1), DEC-423, DEC-424, DEC-791 (item 1), DEC-866 in `docs/DECISION_REGISTER.md`.
- `src/gov/retrieval/retrieve.py` whole (262 lines): `_graph` and `record_of` (line 52), the closure route (line 130), the drops (lines 181 to 200).
- `src/gov/records/queries.py` (`records`, `edges`: a register entry's record carries `heading`, `title`, `span`, `content_hash`) and the register's records in `src/gov/store/loader.py` (lines 103 to 215, `register_entries`, `_read_register`, W2-03): read only.
- Anything else you need (DEC-820), except `tests/acceptance/W2-87/`.

## The defect

`record_of = {record["path"]: record["id"] for record in known}` maps each path to one id. Every decision of the register is its own record, but all share the register's path, so every chunk of the register takes the id and status of whichever entry comes last (`records()` sorts by id: the newest). If that entry were superseded, every register chunk would be dropped. The closure route has the same fault: a register chunk joins it only when the newest entry is reached.

## What to build (batch 1)

- **New `src/gov/retrieval/authority.py`** holding **one function that maps a register chunk to its entry** (W2-55 will reuse it, so make it a clear public function with a docstring): given the store's records (and edges) and the root, a chunk's `path` and `start_line` → the entry whose span holds that line (its id, type, status, and whether it is current), or none (a chunk before the first entry, or a file that is not the register). The register is the file the path map's `decision_register` key names, as the store's register records give it (they all carry its path and a `span`); do not hard-code the register's path. An entry's lines are where its stored span stands in the register file read from `root` (its heading line and as many lines as its span has). An entry is **not current** when its status is SUPERSEDED, it is the target of a SUPERSEDES edge, or its status is DEPRECATED, REJECTED or WITHDRAWN (DEC-423; reuse `retrieve.py`'s constants rather than copy them, without an import cycle). Deterministic.
- **`src/gov/retrieval/retrieve.py`, two places only:**
  - **the closure route (line 130):** a register chunk joins it when *its own* entry is in the closure, not the register's last entry; every other file as today;
  - **the drops (lines 181 to 200):** a register chunk is never dropped for another entry's status; its own entry's status drops nothing new in this ticket (leaving superseded and done entries out, with their count, is W2-55's, DEC-791 item 1). Every other file's drops, the frontmatter fallback and `merge.dropped` stay exactly as today.
  - Leave `_graph`'s return and everything else in the file unchanged (the evidence `id` field too; W2-55 owns the tags). For a store whose register's last entry is current, the bundle without a ticket or ids must be today's, item for item.
- **Builder tests** in new `tests/unit/retrieval/test_w2_87_register.py` (a planted temporary repository, no embeddings, as the existing unit tests under `tests/unit/retrieval/` build theirs), regression evidence only. Proportion (DEC-135): no code for edge cases beyond the KPIs.

## Your paths

Write only: `src/gov/retrieval/authority.py`, `src/gov/retrieval/retrieve.py`, new `tests/unit/retrieval/test_w2_87*`. Nothing else (`governance/project/path-map.yaml` is batch 2's). Never `tests/acceptance/**`.

## Done when

- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-87/src python3 -m pytest tests/acceptance/W2-87/test_w2_87_register.py -q -p no:cacheprovider` passes (run it; read its results and failure messages, never its source); the authority cases (`test_w2_87_authority.py`) stay red — that is batch 2.
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-87/src python3 -m pytest tests/unit/retrieval tests/acceptance/W1-21 tests/acceptance/W1-19 -q -p no:cacheprovider -n 4` passes; a red there you believe is not yours is named with its failure message (never check out another commit to prove it).
- One commit:

      git commit -m "<subject>" --trailer "Task: DAEO-s9qc" --trailer "Implements: DEC-952, DEC-423" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

## Return

Your commit (12 digits) and its trailers; the function's name, signature and behaviour (for W2-55); the lines changed in `retrieve.py`; the suites you ran with counts; your sandbox check; your `gov retrieve` use; read refusals met; your scratch figures.

Your final message is your return. It starts with these twelve labelled lines, then any payload:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

The twelve fields come first, each as a labelled line, with any payload after them. Refused twice for the same call: stop and say so.
