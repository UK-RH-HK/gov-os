
## DAEO-6mk8 (W1-31) closed after the round of DEC-655, with the ticket tool, by the owner's decision (2026-10-14; for the exit auditor; DEC-672, DEC-689)

Two `gov close` runs, neither exit 4 (outputs kept by the orchestrator):

- **First, at `e5ef7475` (2026-10-13):** exit 3 on the three cases that were red on the integration branch since the owner's apply of the generated adapter output (DEC-665), and on a stale checkpoint. The three cases were rewritten in the W1-38 round and merged at `99fbb546`.
- **The one further close, at `44f5bded` (DEC-672):** exit 3, `CHECK_FAILED` on one case of 12,305: `tests/acceptance/W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist`, for one host of the list, in the serial run. It is a live network connection. Run alone straight afterwards the case gave 17 passed, that host included, and it passed in the full regression at the same head an hour earlier. The ticket's own suite gave 161 passed; no other finding.
- **Closed with `tk close` by the owner's decision (DEC-689).** The round's probe passed (`docs/probes/DAEO-6mk8/PR-DAEO-6mk8-round-DEC-655.md`).
- **Learning metrics of the round:** KPI disputes 0; 1 case rewritten (reason DEC-655); 30 cases added; source lines +31 −20 against 150.

## DAEO-emkd (W1-02) closed after the round of DEC-685, with the ticket tool, by the owner's decision (2026-10-14; for the exit auditor; DEC-690)

`gov close DAEO-emkd` at `2588fd12` returned exit 3, `CHECK_FAILED`, on 13 findings (output kept by the orchestrator):

- **All 13 are on commits of 2026-10-01 to 2026-10-11, from before this round:** three commits without a trailer (`15a0dbc4`, `56f1476d`, `d6bb6d5a`), six commits that name no task (`478a8ed0`, `3d58265d`, `d33cb33c`, `0645ec3d`, `e91924da`, `a4e66919`), two containment findings on early commits that hold the ticket file beside a worker's work (`7d9ab30e`, `cd233578`), and one commit in the ticket's range that carries the reviewer's role (`b87ac775`).
- **Every test run of the close was green:** the ticket's suite 3,648 and 5 passed, the regression 9,472 and 258 passed; the validator ALL PASS. By DEC-536 this is the post-merge regression of the round.
- **The round's own commits carry all three trailers; its probe passed** (`docs/probes/DAEO-emkd/PR-DAEO-emkd-round-DEC-685.md`).
- **Closed with `tk close` by the owner's decision (DEC-690).**
