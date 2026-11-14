#!/usr/bin/env python3
"""W2-42a (DAEO-03ub) reopened for R4 (D1) and R5 (the error path), DEC-1157 (12). Run from the repo root."""
p = '.tickets/DAEO-03ub.md'
t = open(p, encoding='utf-8').read()


def one(o, n):
    global t
    assert t.count(o) == 1, o[:40]
    t = t.replace(o, n)


one('status: closed\n', 'status: in_progress\n')
R4 = ("  - 'R4 (D1, 2026-11-14): `git diff REV:PATH REV:PATH` (a revision-colon-path on one or both sides, each naming a "
      "blob that exists) and `git show REV:PATH` are judged as reads of those paths, under the read rules the path names; a "
      "revision word that names no commit, tree or blob is refused as today, not passed [DND row 122, W2-141''s review, "
      "DEC-1157 (12), DEC-1180 (4)] Verify: the `test_r4_*` cases in tests/acceptance/W2-42a/ pass on planted repositories "
      "(both sides blobs: judged as reads; a path the role may not read: still refused; a revision that does not resolve: "
      "refused, rule not `error`)'\n")
R5 = ("  - 'R5 (the error path, 2026-11-14): no Bash or tool input makes the guard''s judge raise inside itself: the `list index "
      "out of range` crash and the revision it cannot classify each get a ruled decision (allow, or a refusal naming its rule), "
      "never rule `error`; the error path stays and still fails closed for a genuine fault (a missing file, the 20-second "
      "deadline) [DND row 123, DEC-1128 (3), DEC-1133 (2), DEC-1157 (12)] Verify: the `test_r5_*` cases in "
      "tests/acceptance/W2-42a/ pass: the crashing forms the engineer finds in the code (empty words, a lone operator, a "
      "trailing pipe, `&&` or `;`, an option with no value, an unterminated `$(`), each ruled; a property case over generated "
      "token sequences that never sees rule `error` from an exception; a planted genuine fault still gives `error` and refuses'\n")
one("  failure:\n", R4 + R5 + "  failure:\n")
F = ("  - 'R4/R5: a call refused today that the fix lets through although it writes into a walled path or reads a refused one "
     "(a fail-open). Verify: the `test_r45_failure_*` cases in tests/acceptance/W2-42a/ pass (a blob read of a held-out or "
     "secrets path, a `git diff` whose output is redirected into tests/acceptance/, each still refused)'\n")
i = t.index('profile: FULL\n')
t = t[:i] + F + t[i:]
one('- DEC-1044\n', '- DEC-1044\n- DEC-1128\n- DEC-1133\n- DEC-1157\n- DEC-1180\n')
t = t.rstrip('\n') + '\n\n' + (
    "**Reopened 2026-11-14 by the CTO within the ticket's purpose (DEC-1157 (12), DEC-1180 (4); listed for the owner's "
    "reading): R4 (D1) and R5 (the error path).** The DND sweep of 11-14 found both still in the code (rows 122 and 123, "
    "triggers met: the lift DEC-1158; DEC-1128 (3) \"the guard's own error-path faults are fixed first after the lift\"): "
    "`reads.py:1721-1725` resolves every revision word as a commit, so a blob ref is refused; and nothing guards the judge "
    "against the three `list index out of range` crashes logged on 11-10. Both sit in `reads.py`/`decide.py`, already in "
    "this ticket's paths. Order: a fresh test designer writes R4, R5 and the failure line as described behaviour (DEC-136), "
    "from the code and planted repositories only (never the guard's call log `~/.gov-os/guard-calls`, the bar's held-out "
    "source, SETUP-A-BAR S2, DEC-1108 (4)); a fresh engineer fixes; gov accept; a narrow independent check (DEC-1156 (7)). "
    "The live hook takes the fix by ACT (DEC-1133 (2): \"each by ACT\"), with the parser copy already planned "
    "(DEC-1174 (1)). The CTO's own Bash line naming a revision-colon-path in text was refused on 11-14 by this very fault.") + '\n'
open(p, 'w', encoding='utf-8').write(t)
print('ok')
