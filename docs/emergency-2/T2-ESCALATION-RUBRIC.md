# T2: the escalation rubric against Emergency 2, the CTO's proposal

`docs/emergency-2/T2-ESCALATION-RUBRIC.md` · the CTO, 2026-11-19 · for the owner's answer by code

**What you asked (DEC-1214 T2):** a phone push also when the CTO needs your decision (features, specs, KPIs, data and
measurement, P1 decisions touching the core or kernel); the CTO reviews the escalation rubric against the changes and
proposes whether to change it.

**The answer: yes, change it.** The rubric in force is DEC-957's (30 October). Of its nine P1 lines, three name
machinery Emergency 2 retired or moved, and three things you decided since are missing from it.

## 1. What no longer fits

| DEC-957 says the owner decides | What you decided since | So it becomes |
|---|---|---|
| "weakens any of the five guard rules" | the guard is retired (EMERGENCY-2 2.2) | gone |
| "any ACT" | the ACT pipeline is retired (2.10); kernel and instruction text is the CTO's call (3.5) | the CTO's |
| "installs" | the CTO approves and records every install; sudo stays yours (DEC-1214 G7) | the CTO's |
| "cost" | no daily budget, no rationing; the 99 % push (DEC-1215) | only a paid service stays yours |
| "a milestone slipping more than a day" | no deadlines; the release is judged by its acceptance (§8) | a line in the brief, not a decision |
| Emergency: "the guard failing open" | retired | gone |
| (missing) | adding or removing a ticket in a planned wave asks the owner (DEC-1214 K2) | yours |
| (missing) | a model exception comes to you as one line; a role whose quality drops goes back on your word (DEC-1212) | yours |
| (missing) | a review that has not converged after two rounds goes to you once, with options (3.3) | yours |

## 2. The rubric, rewritten

- **P3, the lead decides and records it in the ticket.** Reversible; inside the ticket's scope and paths; no change to
  the spec, the KPIs or a standing decision. A fix for a known bug, with the failing test first when no test caught it.
- **P2, the CTO decides** (a senior engineer for its own stream, the CTO approving what crosses streams). Shared code
  or another stream; the order of work inside a planned wave; a red landing or a failed merge, and whether a review is
  called; review findings, in two rounds at most; kernel and instruction text; an install inside the work's scope and
  the machine's capacity, recorded; chores.
- **P1, the owner decides; the CTO brings options and one recommendation.**
  1. A feature, a spec or a KPI line added, removed or changed.
  2. A ticket added to or removed from a planned wave.
  3. The Contract, the Charter or a standing decision.
  4. Data and measurement: memory's standard, how a measure is taken, a measure that came out void or under its bar.
  5. A P1 that touches the core or the kernel: a change to how every agent works that the CTO is not sure is its own
     to make.
  6. Anything irreversible outside a worktree: deleting history, data or a branch others read.
  7. A secret or a security exposure; a paid service.
  8. A model exception; a role going back from Sonnet.
  9. A review not converged after two rounds.
  10. What is your own hand: a release, a re-pin, a push, sudo, the machine's settings, going public.
- **Emergency: stop the affected work at once, then push.** A secret exposed outside the machine; a risk of losing
  data or work; the disk below its floor; the machine over its gate and not coming back.

## 3. When your phone is pushed

| Case | Push |
|---|---|
| An Emergency; the plan at 99 %; the CTO stalled (60 min by day, 2 h at night, from the dispatcher's pass) | at once, any hour |
| A P1 that stops work: nothing else on the list can go on without it | at once by day; at night it waits for the morning brief (T2-2) |
| A P1 that stops nothing | no push: the morning brief, one message, answered by code (T2-3) |

## 4. Your answers

| Code | Question | Options | Recommendation |
|---|---|---|---|
| **T2-1** | The rubric of §2 replaces DEC-957's | yes / no / yes with changes | **yes** |
| **T2-2** | A P1 that stops work, at night (23:00 to 08:00) | (a) it waits for the morning brief; only an Emergency, the 99 % and a CTO stall push at night; (b) it pushes at any hour | **(a)**: it is what you set for tonight, and the build list is long enough that work moves to the next item |
| **T2-3** | A P1 that stops nothing | (a) the morning brief only; (b) a push as well | **(a)** |

Answer form: "T2-1 yes, T2-2 a, T2-3 a".

**On your yes** the CTO changes the text that carries the rubric (the orchestration skill's briefs-and-returns page, the
role files and the domain skills' escalation sections: 23 kernel files and their generated copies), as one change under
3.5, with the tests that pin that text revised by a test designer; DEC-957's rubric is marked superseded in the
register.
