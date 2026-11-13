task: DAEO-fd0p
# PKG-W2-160-ROUTE-1: W2-159's unit test pins the old `ACT_PATHS`, which the decided Interface changes

## Question
DEC-1153 (2) and PKG-W2-160-IFACE-1 (a) say that `.gov-runtime/dispatch/inbox/**` is added to
`src/gov/session_watch/command.py`'s `ACT_PATHS`. The helper watch writes its items there. The engineer added it
(eb6d0cc07). W2-159's unit test `tests/unit/session_watch/test_route.py:19`
(`test_the_command_is_declared_by_its_module`) asserts `command.act_paths == (".gov-runtime/session-watch/**",)`.
It is green on the base and red on this branch. The file is not in W2-160's allowed_paths (only
`tests/unit/session_watch/test_w2_160*` is), so neither the lead nor the engineer may change it. Which option does
the CTO choose?

## Options
(a) **Widen by one test file (recommended).** Add `tests/unit/session_watch/test_route.py` to allowed_paths, limited
    to that one assertion. The engineer (or a fresh one, about 0.5 USD) changes line 19 to the two-path tuple
    `(".gov-runtime/session-watch/**", ".gov-runtime/dispatch/inbox/**")`. Cost: one ticket edit, a one-line change,
    and a re-run of lead_verify (about 10 minutes). The decided Interface stays as written.
(b) **Keep `ACT_PATHS` as W2-159 had it.** Revert the inbox entry; the helper watch would write the inbox without
    declaring it. Cost: this contradicts DEC-1153 (2)'s accepted text and the act-class declaration
    (`src/gov/cli/main.py:27`), so the owner's decision would need re-opening. Not recommended.
(c) **The CTO changes the line at merge** (an ACT on a W2-159 test, outside this ticket). Cost: the branch stays red
    on one W2-159 unit test until then, and the change lands without a ticket path. Not recommended.

## Recommendation
(a), confidence high. The assertion records W2-159's paths, and DEC-1153 (2) changed them. Updating the test is the
consequence the package missed: IFACE-1 named the command file but not its unit test.

## What it blocks
Landing. The build is otherwise green (66/66 W2-160 acceptance; see the lead's return). The review can run on the
current head, because the change is a one-line test edit. The narrow check after it is the lead's re-run.

## Accept in one line
"PKG-W2-160-ROUTE-1 (a): allowed_paths add tests/unit/session_watch/test_route.py (the ACT_PATHS assertion only)."
