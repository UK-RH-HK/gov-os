# The investigation (DEC-1047): common rules for every part

You are one of several read-only investigators the CTO launched on the owner's order. Read DEC-1047 in
`/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` first (its last entry): it holds the owner's
words. Be harsh and concrete. Your part brief (the file that named this one) says what you investigate.

## The aim (the yardstick)
The Gov OS stops drift and makes the owner's agents work, and record their work, the way a good software company
does. It is not a security battle and not a rule battle. It needs: (1) a good tool that extends the agents' memory
(RAG and combined memory); (2) help developing the spec and the KPIs through research and discovery agents, then their
execution by other agents; (3) roles whose permissions keep apart work whose interests conflict (the builder never
writes or reads its own acceptance tests; the reviewer never fixes what it reviews); (4) governance of the WBS and of
tickets' launching and closing with well-structured dependencies: "governing the traffic, not governing a city".
What matters is tests and code that match the KPIs and the spec and pass green. Everything else must justify itself.

## The benchmark (DEC-1010's test)
A rule, check, gate, test, record or ceremony earns its place only where what it guards against is (i) within the aim
above, (ii) reachable in ordinary work (an honest agent's mistake, not a deliberate adversary: ADR-0001), and (iii)
would otherwise fail open or lose work. Anything that blocks or slows work for any other reason is bureaucracy: the
recommendation is to lift it. Options per item: **lift** (switch off here, by configuration where it is product; the
feature may stay built), **scope to the change** (run only what the change can reach), **move to the nightly**,
**keep**. DEC-1010 itself (moderated reviews, at most two rounds, READY by `verdict.py`) stays whatever you find.

## Rules
- **Read-only.** Write only your own report file (named in your part brief) and helper scripts or outputs under
  `/tmp/gov-os-inv-<part>/`. No commit, no edit in any tree, no test runs (measure from logs and records that exist);
  if one small measurement is indispensable, one light command through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, never a suite.
  No gitleaks (DEC-1045). Never read secrets, the held-out material's contents or `~/gov-os-workbench`.
- **Costs measured, not guessed, wherever a source exists:** machine time (JUnit XML durations: `/tmp/gov-os-nightly-junit/`,
  `~/gov-os-runs/W2-00/`, close and landing logs `.gov-runtime/scratch/orchestrator/log/`), tokens (each lead's JSON log
  in `.gov-runtime/scratch/orchestrator/log/*.json` carries `usage` and `total_cost_usd`; brief sizes in bytes), the
  owner's time (packages in `governance/project/orchestration/packages/`, pings in `~/.config/gov-os-notify/pings.log`,
  decisions in the register). Mark every estimate as an estimate, with how you reached it.
- Work in batches with small, targeted searches (never one giant query; `gov retrieve "<question>"` from the main tree
  is available). Use your model's full window; keep to your part; note anything outside it in one line for the combiner.
- Report every other problem of the same kind you find in your part, named or not.

## Your report (the file your part names), in this form
A short headline (5 lines), then one table row per item:
`| id | what | where (paths, tickets, decisions) | cost (machine / tokens / owner; source) | what it protects | DEC-1010 test: in aim? ordinary work? fails open or loses work? | recommendation | what lifting takes (code, tests, tickets, config) | depends on |`
then, under the table, the evidence for the larger items (commands, counts, paths). Ids: `<part>-<n>` (for example `A1-3`).
Return the twelve fields first as labelled lines (task, status, work_completed, files_changed, evidence, tests,
discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), with your headline in
`work_completed` and the report's path in `files_changed`. Refused twice for the same call: stop and say so.
