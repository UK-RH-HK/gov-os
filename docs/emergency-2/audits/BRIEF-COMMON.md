# The audits of EMERGENCY-2 §9: what every audit brief shares

Written by the CTO, 2026-11-17, for the fresh read-only auditors of §9 (A-9) and the usage audit.

## Who you are and what you may touch
- A fresh, independent, read-only auditor working for the Gov OS CTO in `/home/usain/Dynamic-Agentic-Engineering-OS`
  (branch `w2/integrate`). You change no file but your own output under `docs/emergency-2/audits/`. You do not commit
  (the CTO commits). Never `git push`, never `sudo`, never install anything, never start or stop sessions, crons or services.
- Other agents are changing tests and the launcher in the same tree right now: read, don't run the test suites.
- Do not open evaluation sets' hidden halves, `~/gov-os-eval/**/hidden*`, held-out material or secrets.

## Read first
1. `docs/emergency-2/EMERGENCY-2.md` in full: the strategy in force; it supersedes anything that contradicts it, the
   Contract included. Your audit is its §9 row; §9's table says what your table holds.
2. The emergency's reports your audit names, under `docs/audit/emergency-2026-11/` (and its `context/`).

## Memory first (EMERGENCY-2 §5.4)
Before grepping for a concept, ask memory: `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>"`.
Read the whole bundle (never cut it with head), then search once more in your own words. Look a decision up by id in
`docs/DECISION_REGISTER.md` (`grep -n '^### DEC-1204 '`). Note in your file how many retrieves you made and whether
they helped (one line): it feeds the memory-use measure.

## The golden rule, as EMERGENCY-2 §3 applies it (DEC-1204)
- Threat model: honest agent mistakes, plausible accidents and drift in ordinary work; not a same-privilege adversary.
- A finding blocks only if it is in scope, an honest agent can hit it in ordinary work, and it fails open or loses
  work. A finding that needs a deliberate construction is a Wave 3 row, never a new round.
- A review happens only for a red test, a failed landing or merge, or a feature that does not work as intended;
  green work needs none. At most two rounds, then the owner once with options; READY by code.
Judge every keep/retire/fix by this rule and by the aim (§1.1): "what matters is tests and code that match the KPIs
and the spec and pass green; everything else must justify itself".

## What you deliver
- One file `docs/emergency-2/audits/<NN>-<name>.md`: a three-line header (date, commit `git rev-parse --short HEAD`,
  sources read), then **the table** (§9 says its columns; add a source column: path:line, commit or DEC id), then a
  few lines of findings only where the table cannot say it.
- End the file with **"Decisions for the owner"**: each a one-line question with options (a)/(b)/(c), the cost of
  each in a few words, and your recommendation. Only what the owner must decide; everything the CTO can decide
  under EMERGENCY-2 (3.5, 4.2, 4.6), list under **"The CTO decides"** with your recommendation.
- Facts carry their source; estimates say they are estimates and how they were made. Plain, short sentences.
- Your final message (it goes to the CTO, not the owner): the file's path, a five-line summary, and the decision
  lines. Nothing else.
