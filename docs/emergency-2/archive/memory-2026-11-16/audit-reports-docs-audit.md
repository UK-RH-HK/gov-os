---
name: audit-reports-docs-audit
description: "every auditor/reviewer brief names its report path under docs/audit/<topic>/ (path map docs/audit/**; guard REVIEW_PATHS); never drafts/ or a scratch folder; the emergency's home is docs/audit/emergency-2026-11/"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-16T17:38:05.073Z
---

On 11-16 I briefed five auditors to write under `.gov-runtime/scratch/orchestrator/drafts/…`. The guard refused every one: auditors write only to REVIEW_PATHS (`pretooluse.py:81`: docs/probes/, docs/audit/, docs/assessment/, .gov-runtime/scratch/review/, .gov-runtime/scratch/orchestrator/reviews/). Their reports landed in scratch folders or came back as text. The owner: "The audits are not landing … Nothing stays only in a scratch folder."

**Why:** I named a path without checking the guard's write rule for the auditor role.

**How to apply:** every audit, review and research report brief names `docs/audit/<topic>/<name>.md` (tracked; in the path map as `docs/audit/**`). The emergency's single location is `docs/audit/emergency-2026-11/`. Commit each report there as it lands. A research-role session may be refused there too: tell it to return its text if refused, and copy it in myself. Related: [[auditor-scratch-via-bash]].

**Also (11-16):** files under docs/audit/ are records held to audit-report.schema.json: front matter needs milestone, commit (a bare hash), pack_sha256, and values containing ": " must be quoted. Run `gov.check.schema.run` before committing a report. Three reports turned the core-schema check red from fb066dd6e until 1d2f13708.
