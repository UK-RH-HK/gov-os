---
name: git-archive-base-export-form
description: "To re-run reds on a base commit, export named paths with a literal git archive line in a Write-tool script; `--format=tar` with the whole tree in a Bash heredoc was refused by the guard"
metadata:
  node_type: memory
  type: feedback
  originSessionId: e0e854ea-5dbb-4da8-bdcb-635cad00acdc
  modified: 2026-11-16T09:08:10.417Z
---

To check whether a scoped-run red is also red on the base, export only the named paths: `git -C <tree> archive <sha> src tests governance template pyproject.toml | tar -x -C <tree>/.gov-runtime/scratch/base-<sha>`. Write that line in a script file with the Write tool, using literal paths, and run it with `bash`. W2-189 build2 (2026-11-16 09:08): a heredoc script holding `git -C $T archive --format=tar 452354001` (the whole tree) was refused by the PreToolUse hook as "a revision the guard cannot resolve" (DEC-820, DEC-953 item 2). The named-path literal form ran.

**Why:** the guard has to resolve every revision and path it is shown. A variable or option in that position makes the call impossible to judge, and a whole-tree export could copy walled material.

**How to apply:** use literal sha and paths, never the whole tree, and put it in a script written with the Write tool. Record the refusal in guard_refusals. Related: [[lesson-to-memory-at-once]]
