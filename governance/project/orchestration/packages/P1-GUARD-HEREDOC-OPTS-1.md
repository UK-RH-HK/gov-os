# P1-GUARD-HEREDOC-OPTS-1: the live guard hook fails open on `bash -euo pipefail <<'EOF'` (MR-3 and rule 5)

**(1) Context.** This repository's live PreToolUse hook (`.claude/hooks/pretooluse.py` with `.claude/hooks/bash_writes.py`,
sha256 `74f8dbea…` and `bb246a21…`) keeps five rules since DEC-953 item 2. It refuses, among others, an engineer's write
to the acceptance tests (MR-3). W2-42a, the product's guard parser, is in its FULL review. Round 1 (auditor session
b4ed5672, head e9e4f7bac) found F1: in scope, ordinary work yes, fails open. The auditor noted that the live hook has
the same gap.

**(2) What happened, verified by the CTO** (14:58 UTC, a dry decision through the live hook with the pinned
interpreter, as an engineer on DAEO-03ub; nothing was written):
- `bash <<'EOT'` / `echo x > tests/acceptance/W2-01/zz_probe.py` / `EOT`: **deny**, "only the independent test designer
  writes the acceptance tests (MR-3) (DEC-953 item 2)".
- The same with `bash -euo pipefail <<'EOT'`: **allow** (an empty answer).
- **The cause:** `_kind` (`.claude/hooks/bash_writes.py:1081-1086`) counts every word not starting with `-` as a script
  operand. `pipefail`, the value of `-o`, makes the shell "read a script file", so the heredoc body is taken as data and
  never judged. The same holds for `-o <opt>`, `-O <opt>`, `--rcfile <f>`, `--init-file <f>` and for
  `cat <<'EOF' | bash -o pipefail`.

**(3) Why it matters.** `set -euo pipefail` is a common shell idiom. An honest worker writing a heredoc script with it
gets no MR-3 refusal for a write into `tests/acceptance/`, or for anything else rule 5 guards. Two things still stand:
- **The backstop:** every launched worker's tripwire (DEC-789) compares the tracked tree when its session ends, and names
  any change outside its paths. A write would be caught after the fact, not stopped.
- **No sign of use:** nothing shows the spelling has been used for such a write.

**(4) Options.**
- **(a) ACT-GUARD-FIX-5 now: the same fix in the live hook.**
  - The change: in `_kind`, skip the values of the shell options that take one (`-o`, `-O`, `--rcfile`, `--init-file`,
    and a combined flag ending in `o` or `O`). Treat `/dev/stdin` and `/dev/fd/0` as stdin. Read a shell with an
    unknown option as a shell, failing closed.
  - Tests: a replay of W2-42a's F1 spellings, plus the five-rule hook's own suites.
  - Route: built and rehearsed by a helper, one independent review, your yes; class (b) by `guard-hook`, applied by your
    operator.
  - Cost: about 2 to 3 hours to your yes. It changes only that function. It refuses more and never less, so it is
    stricter-only.
- **(b) Wait for W2-42a's reviewed fix and copy it into the live hook.** About a day: its fix round, review round 2,
  then the same ACT. The hole stays open meanwhile, covered only by the tripwire.
- **(c) A brief line only** ("never pass options to a shell that reads a heredoc"). Minutes, but it relies on every
  agent reading it, and fixes nothing.

**(5) Recommendation: (a)**, with W2-42a's F1 fix running in parallel in the product. Confidence high.
- Classification: in scope, ordinary work yes, fails open.
- Stopping running work is not needed: the tripwire catches a write at session end, and the leads carry on. If you want
  the stop the emergency rubric names, I would hold new worker launches until the ACT is applied.

**(6) What it blocks.** Nothing waits on it, but the guard stays open on this spelling until it is fixed. W2-42a's own
F1 round goes ahead either way.

Your line: `GUARD-HEREDOC (a)` (and `hold launches` if you want the stop), or `(b)`, `(c)`.
