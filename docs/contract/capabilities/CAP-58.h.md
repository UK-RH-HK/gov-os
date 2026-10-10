---
id: CAP-58.h
type: capability
status: PROPOSED
state_class: DERIVED
title: 'Containment attribution by commit trailers: a forward HEAD move, including an integration merge by the orchestrator, is judged commit by commit, each commit''s paths against the allowed paths of its own `Role` and `Task` trailers and not against the caller; a merge commit is not a finding when every commit it brings passes; a commit with no `Role` or `Task` trailer is judged against the caller'
depends_on:
- CAP-58
---

# CAP-58.h: Containment attribution by commit trailers: a forward HEAD move, including an integration merge by the orchestrator, is judged commit by commit, each commit's paths against the allowed paths of its own `Role` and `Task` trailers and not against the caller; a merge commit is not a finding when every commit it brings passes; a commit with no `Role` or `Task` trailer is judged against the caller

A covers item of CAP-58 (Path guards as default-deny allow-lists). Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority (DEC-614).

- **Item:** Containment attribution by commit trailers: a forward HEAD move, including an integration merge by the orchestrator, is judged commit by commit, each commit's paths against the allowed paths of its own `Role` and `Task` trailers and not against the caller; a merge commit is not a finding when every commit it brings passes; a commit with no `Role` or `Task` trailer is judged against the caller
- **Wave:** W1
