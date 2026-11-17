---
name: probe-brief-fill-reviewer-effort
description: "in a reviewer brief, fill reviewer_effort with the launched effort; \"<the effort you ran at>\" made au-3 write \"low\" though its session ran at high (W2-60b, 11-16)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 932d783b-5364-4f91-8247-79fa01c22dbf
  modified: 2026-11-16T12:04:39.706Z
---

W2-60b au-3 (2026-11-16 12:0x, narrow check, launched `independent-auditor high --owner-named DEC-1154`): the brief left `reviewer_effort: <the effort you ran at>`. The reviewer wrote `reviewer_effort: low`. The spend log ("launched, high") and the session record (`.gov-runtime/sessions/<id>.json` in the main checkout, effort from the log's perTurnEffort) both say high. The record was committed word for word (as the brief promised), and the mismatch was reported in the return.

**Why:** a launched session cannot see its own effort setting reliably, so it guesses.
**How to apply:** write the literal launched effort into the brief's front-matter form (e.g. `reviewer_effort: high`). Before committing a record, check it against the session record's `effort.value`. Related: [[probe-record-one-verdict-block]], [[review-record-verdict-block]].
