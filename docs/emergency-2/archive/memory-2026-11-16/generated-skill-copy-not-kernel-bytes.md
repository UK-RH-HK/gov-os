---
name: generated-skill-copy-not-kernel-bytes
description: "gov adapters generate (rulesync) rewrites a skill's front matter; never brief \".claude/skills copy = kernel bytes\""
metadata:
  node_type: memory
  type: feedback
  originSessionId: 1598bb29-57cd-422c-a892-c13f34c9be31
  modified: 2026-11-16T16:55:40.827Z
---

A `.claude/skills/<x>/SKILL.md` made by `gov adapters generate` is NOT the kernel file's bytes: rulesync folds the description, drops the top-level `version` (keeps only `metadata.version`) and drops the blank line after the front matter. The kernel file and its `template/.rulesync/skills/` mirror are byte-identical; the generated copy matches only in name, version (via metadata.version) and body.

**Why:** W2-195 td-1 (2026-11-16): my interface item 7 said the generated copy equals the kernel bytes; the test designer found it impossible and asserted name/version/body instead (a brief gap, ~10 min).

**How to apply:** in any brief or check on shipped/preloaded skills, assert bytes only for the kernel file and its rulesync mirror; for the generated copy, assert name, version read as `gov.launch.role._version` does (top-level, else metadata.version), and body. Related: [[shipped-folder-exactness-tests]].
