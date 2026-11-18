# Lead brief: the rubric in code (K1, RT-8) and audit 09's usage rules enforced by code (W2-201, a new feature)

Read `/home/usain/Dynamic-Agentic-Engineering-OS/docs/emergency-2/briefs/NIGHT-COMMON.md` first and follow it.
Branch `e2/k1-usage` from `w2/integrate`, worktree `/home/usain/gov-os-worktrees/E2-k1-usage`. The role files are kernel
text (`template/governance/kernel/roles/**`, C3): the CTO approves their change by naming it here (§3.5); their test
designer and engineer run Opus. `Task: DAEO-<your new ticket id>`, `Class: F`.

**Read:** DEC-1212 and DEC-1214 (K1) in `docs/DECISION_REGISTER.md`; audit 4 Table 3 and its model table
(`docs/emergency-2/audits/04-tickets-and-rubric.md` lines 170-195) with the owner's changes (DEC-1212 (3), DEC-1214
K1: Sonnet for every lead, all profiles; every helper; C2 test designers, engineers and auditors; the proving runs; C3
roles and the CTO on Opus); audit 9 `docs/emergency-2/audits/09-usage-last-two-days.md` (its recommendations and the
CTO's items, DEC-1212 (4)); `src/gov/launch/role.py` (the `Launch default` and `Launch by criticality` lines), the
launcher, `governance/project/criticality.yaml` (or wherever the criticality list lives), `.claude/hooks/agent_model.py`
and `governance/project/model-exceptions.yaml`.

**Your feature (a ticket first, wbs_id W2-201, KPI lines each with its verify):**
1. **K1 / RT-8:** the role files' `Launch default` and `Launch by criticality` lines carry the table above; the
   criticality list is Table 3's C3 list; `gov launch` picks model and effort from the role, the ticket's class and the
   table, states them in its launch log, and refuses a caller's other model (an exception only from the exceptions file).
2. **The helper rule by class:** `agent_model.py` lets Opus through for a test designer or engineer only for C3 work and
   names the reason in its refusal otherwise (design how the hook knows the class: the session's ticket, an env the
   launcher sets, or the lead naming the ticket; keep it simple and safe: unreadable means Sonnet).
3. **Audit 09's usage rules in code** (each one only where code can hold it; list the rest in your return): no `fork`
   subagent for helper work (refused by the hook, naming "a fresh helper from a written brief"); the 5-minute prompt
   cache for launched workers kept and checked; no inbox waiter and no idle-check wake-up hooks in the settings the
   product writes; one plan reading an hour at most (`usage_log.sh` EVERY floor). Do not add any usage brake or budget:
   the owner removed rationing tonight.
**Flow:** test designer (Opus for the role-file and launcher C3 parts) writes `tests/acceptance/W2-201/`, red on the
base, and revises W2-33/W2-184 cases the table changes (with a Rewrite-Reason naming DEC-1214 K1); engineer builds until
`gov accept W2-201` is green; then W2-33, W2-184, W2-153, `tests/unit/launch`, `tests/unit/hooks`.
