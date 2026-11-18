---
id: CAP-58.h
type: capability
status: PROPOSED
state_class: DERIVED
title: 'Containment judged at the landing by commit trailers: a forward HEAD move, including an integration merge, is judged commit by commit, each commit''s paths against the allowed paths of its own `Role` and `Task` trailers; a path outside them is a notice, never a refusal; only a test-authorship breach (MR-3) is refused; a merge commit is not a finding when every commit it brings passes; a commit with no `Role` or `Task` trailer is judged against the caller'
depends_on:
- CAP-58
---

# CAP-58.h: Containment judged at the landing by commit trailers: a forward HEAD move, including an integration merge, is judged commit by commit, each commit's paths against the allowed paths of its own `Role` and `Task` trailers; a path outside them is a notice, never a refusal; only a test-authorship breach (MR-3) is refused; a merge commit is not a finding when every commit it brings passes; a commit with no `Role` or `Task` trailer is judged against the caller

A covers item of CAP-58 (Containment judged at the landing). Generated from `docs/contract/contract.yaml` (Contract v5, version 5.0), which is the authority (DEC-614).

- **Item:** Containment judged at the landing by commit trailers: a forward HEAD move, including an integration merge, is judged commit by commit, each commit's paths against the allowed paths of its own `Role` and `Task` trailers; a path outside them is a notice, never a refusal; only a test-authorship breach (MR-3) is refused; a merge commit is not a finding when every commit it brings passes; a commit with no `Role` or `Task` trailer is judged against the caller
- **Wave:** W1
