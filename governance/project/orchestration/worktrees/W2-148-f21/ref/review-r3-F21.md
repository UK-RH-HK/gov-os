**F21 (S22, F15), scope: in.** With files left, the owner's undo step returns `result: "undone"` and exit 0 (`operator_run.py:1528`). The journal recovery returns 1 in the same case (`:1593`). This breaks the letter of "never reports success".
- Ordinary work: yes, because the owner's undo within 7 days can meet a control file the CTO commits, or one Claude Code writes, during the undo.
- Consequence: other. The lock stops every later run and launch, the P1 names each file, and the result carries `left` and `lock: true`. Only a caller that keys on exit 0 or on the word "undone" misreads it. Ride-along: exit 1 and a distinct result word.

