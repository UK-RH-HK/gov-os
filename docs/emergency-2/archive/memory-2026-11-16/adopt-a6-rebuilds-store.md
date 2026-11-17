---
name: adopt-a6-rebuilds-store
description: "gov adopt's A6 recreates the lexical, semantic and code-intel indexes; a rebuild hold must cover A6 and later, not only gov rebuild and A9"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-16T16:03:45.091Z
---

On 11-16, the W2-81 re-run's REBUILD HOLD (written by my fork into w2-81/REPLIES.md) said "stop before gov rebuild and A9; A0 to A8 go on". But A6 ("controlled migration", even with an empty plan) recreates the store's indexes in about 37 s. Three adopters (python-app-clean, legacy-docs, typescript-monorepo) rebuilt between 15:57 and 16:00, beside JOB-20261116-02, against the owner's "no store rebuild beside it". I stopped the other four sessions by pid at 16:03.

**Why:** I worded the hold from the stage names, not from what each stage does. The product's help and the adopt skill do not say A6 rebuilds.

**How to apply:** a hold on rebuilds or index builds covers A6 and every later stage, and any `gov adopt` stage not checked. Before wording any hold, grep the stage functions for the rebuild or index calls. Sessions running headless read the replies file only at their stops, so a hold that must take effect now means stopping them by pid ([[waits-by-pid-only]]). Related: [[read-the-rule-before-routing]].

**Correction 11-16 17:1x:** A8 also rebuilds the store (python-app F-013), so my "exact from the code" hold missed it. A hold on rebuilds covers every stage from A6 on unless a run shows otherwise.
