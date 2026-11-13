# Brief eng-1: engineer for DAEO-p8tv (W2-172), profile FULL, class C2

You are the engineer for ticket DAEO-p8tv (W2-172: the memory audit's driver and schedule). You implement the four new
subcommands of `python3 -m gov.memaudit` (`run`, `due`, `baseline`, `status`, plus the `figures` reader of Interface
item 6) and the cron wrapper `governance/project/orchestration/tools/memaudit_cron.sh`, until the independent acceptance
suite `tests/acceptance/W2-172/` passes. The ticket's `## Interface` section (items 1-12, the CTO's answers O1-O4 above
it) is the contract: you conform to it and never change it. A gap or a clash in it comes back as a package (status
PACKAGES: question, options with cost, recommendation, confidence, what it blocks), not as your own invention.

## The CTO's decision PKG-W2-172-TESTS-1 (DEC-1112 (3), 2026-11-12): binding, word for word; it is in the main tree's
## copy of the ticket and not yet in yours, so it is here
- **GATE-1 (a):** the driver splits `--gate-cmd`'s value with `shlex.split` and runs the words as given, so the default
  `gov resources --check` works; the Interface's "called with no arguments" reads "run as its words".
- **TD-1 (b):** the 12-line digest does not record `--force`; item 1's "and the digest" is corrected to the counts only.
- **TD-2 (b):** RN-NAME is judged by `STARTS.log` (an audit started), not by a refusal's `COUNTS.json`, so a refused run
  can be retried the same day.

Two acceptance cases still plant only the audit folder (no `STARTS.log` line) and expect `RN-NAME`
(`test_s4_a_second_start_on_the_same_date_is_refused_rn_name_and_writes_nothing_there` and the `RN-NAME` pairs of
`test_s2_the_first_check_that_fails_refuses`). The test designer is revising them in parallel to plant a `STARTS.log`
line naming `<A>`; implement TD-2 (b), and report those cases as "awaiting the test designer's revision" if they are
the only reds left. Never edit `tests/acceptance/` (it is not yours, and a restore there is the test designer's).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-172 |
| branch | w2/W2-172 |
| your allowed paths | src/gov/memaudit/**, tests/unit/memaudit/**, governance/project/orchestration/tools/memaudit_cron.sh, docs/changes/W2-172-evidence.md |
| the ticket (read it first, whole: KPI lines and the Interface at its end) | /home/usain/gov-os-worktrees/W2-172/.tickets/DAEO-p8tv.md |
| the acceptance suite (read it: README.md maps each KPI line to its cases; conftest.py, w2_172_world.py, launch_stub.py, gate_stub.py, py_shim.py, w2_172_digest.py are how it reaches you) | tests/acceptance/W2-172/ |
| W2-170's and W2-171's code you call as children and never change in behaviour (their subcommands, exit codes, layout, `say`) | src/gov/memaudit/ (`__main__.py`, preflight.py, drops.py, declare.py, measure.py, judge.py, classes.py, pool.py, figures.py, say.py, layout.py, common.py); their Interfaces .tickets/DAEO-61vm.md and .tickets/DAEO-k1e2.md |
| the launch script (called, never changed): argv, exit codes 0/10-22 (16 the canary), the counts object as stdout's last line, the `AUDITS.log` line form | governance/project/orchestration/tools/indep_launch.py (docstring), governance/project/orchestration/indep-schemas/indep-counts.schema.json |
| the gate's own check (O2) | src/gov/resources/command.py (`gov resources --check`: exit 0 open) |
| the store link's build and lock | src/gov/rebuild/integration.py, governance/project/rebuild.yaml |
| the package | governance/project/orchestration/packages/MEMORY-AUDIT-1.md |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1101, DEC-1125, DEC-1097, DEC-1038, DEC-1050, DEC-1073 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## Held-out rules (DEC-820)
Never open the real sets root (`~/gov-os-eval`), the real runs folder (`~/gov-os-runs`), any hidden half or
memory-verdict folder, the real crontab. Never run the real launch script against real sets, a real model call or a
real search. The driver's own process opens no path under `--sets-root` (F1; the suite spies on it with an audit hook).

The ticket's context packet (`gov context DAEO-p8tv --role engineer --budget 20000`, built by your lead) follows; its
`ticket_text` is the same ticket file as above.

----

