---
name: guard-shell-reading-allowlist
description: "any guard code that reads shell text to decide (e.g. expanding a variable) must be a strict grammar that binds nothing on any unfollowed form, never a deny list of builtins"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-16T15:31:07.288Z
---

2026-11-16, ACT-GUARD-FIX-8 round 1 REFUSED (KPI 4, fails open): my pre-pass expanded `NAME=<literal>` for the revision rule and bailed on a deny list of first words. The reviewer set the variable past it in 16 ways: `builtin read`/`command eval`/`builtin printf -v`, `$'eval'`, `$E`, `trap 'C=…' DEBUG`, `IFS+=`/`for IFS in`, `for ((C=…))`, `a[C=…]=`, `$[C=…]`, `[[ 1 -eq C=… ]]`, `exec {C}>`, and `'$C'` in single quotes; plus the old fallback to the hook's own environment.

**Why:** bash has too many ways to set or reread a variable for a deny list to cover; a guard that reads shell text is a wall, so a missed form is a fail-open.

**How to apply:** write such a reading as a grammar: the whole command must consist only of forms it follows (plain literal command words, $NAME/${NAME} only, a short list of operators), and anything else binds nothing (today's refusal stands). Never fall back to the hook's environment for a name the command may set. Probe with the reviewer's style: a real-commit decoy vs a bad value, confirmed in bash. Related: [[act-check-source-strings-as-written]], [[no-rehearsal-against-live]].
