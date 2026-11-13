t = open("rev-2.md").read()
t = t.replace("Anything in `src/` is out of scope: it did\nnot change since eb6d0cc07643.",
              "Anything in `src/` is out of scope: this ticket\nchanged none of it since eb6d0cc07643 (what the w2/integrate merge brought is other tickets').")
t += open("rev-2.ctx.md").read()
t += '''

## Return (your last message; nothing else is read)
First a fenced verdict block, exactly:
```verdict
ticket: DAEO-fd0p
head: 14c9e7a36
round: narrow check (DEC-1154) of DEC-1156 (1), (6)
verdict: PASS | FAIL
blocking: <n>
```
PASS only when no finding is blocking (an assertion that is false or weaker than the code; a change to anything but
the ACT_PATHS assertion in test_route.py; an F4 that can pass on `w2/W2-159` with a path W2-159 does not allow, or is
red or silently passed elsewhere; a planted case that passes vacuously or writes outside `tmp_path`; a missing
Rewrite-Reason). Then each finding: id (N-<n>), severity (blocking / non-blocking), file:line, what you did to show it
(the probe's command and its output, short), and the behaviour that would be right (described, not a patch). Then the
probes you ran with their results. Then the twelve fields, each a labelled line ("none" where nothing): task / status /
work_completed / files_changed / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action, and `guard_refusals:` (none, or each: time | form | the hook's reason | true or
false-positive).
'''
open("rev-2.md", "w").write(t)
