---
name: yaml-parse-front-matter-before-sha-yes
description: "before asking the owner to approve a skill/role text by sha, YAML-parse its front matter (unquoted \": \" breaks it)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-16T16:40:23.707Z
---

Before a skill or role text goes to the owner for a `yes <name> <sha8>`, its front matter must pass `yaml.safe_load`. On 11-16 the owner had already approved judging-work's text (0fc1c502). `gov rebuild` then flagged its front matter as invalid YAML: the `description:` held an unquoted ": ". The fix (quoting that one value) changes the bytes, so the owner has to approve again on the committed bytes, through W2-195's CIT-P.

**Why:** rulesync, the store and the launcher all read the front matter with YAML, and an approval is tied to exact bytes.

**How to apply:** run the YAML parse, and quote any value that holds ": ", before handing over the sha. Related: [[ticket-fields-no-inline-comments]].

**Again 11-16 19:05 (W2-195 lead, the CIT-P draft):** my `docs/changes/W2-195-CIT-P.md` front matter had `owner_approval: pending (DEC-1204 (7): the owner ...)`; uncommitted in the tree, it reddened W2-02 `test_core_schema_is_green_on_this_repository` in lead_verify (SCHEMA_UNREADABLE_RECORD). Every docs/ record I write: quote free-text values in single quotes and `yaml.safe_load` the front matter before any verify run.
