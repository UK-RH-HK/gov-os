---
milestone: "Owner's retrospective 2026-10-16 to 2026-11-16, part 1: where the work and the usage went"
commit: a2a07592e9001c9ef7411a26a5deebc874a3a7d0
pack_sha256: "none: no context pack; brief from the CTO, sources read directly"
---

# P1: where the work and the usage went (2026-10-16 to 2026-11-16)

Independent auditor, read-only. I measured and judged; I changed nothing. Yardstick: DEC-1047's aim (stop drift; memory; spec and KPIs; separated roles; "governing the traffic, not governing a city"; "everything else must justify itself") and DEC-1204, the golden rule.

**Where this file is.** The brief named `.gov-runtime/scratch/orchestrator/drafts/retro-2026-11/P1-usage.md`. The guard refused my `mkdir` of that folder ("a reviewer or auditor writes only its own review or audit record …", DEC-953 item 2). I did not try another way in. The report is in my scratch folder, and the CTO can move it.

## 1. Method

**Sources read.** I read every Claude Code transcript under `~/.claude/projects/`: 4,922 session files with usage in the window, about 159,000 distinct assistant messages, de-duplicated by message id (only 232 duplicates across files). That covers the main tree's sessions (the CTO's own sessions plus headless runs started in the main tree), their 596 subagent transcripts (typed by `*.meta.json`), 1,673 worktree sessions, the W2-27/EXAMIN and W2-81 run folders, and the live-test sessions that pytest spawns under `/tmp`. Other sources: 578 lead and adopter logs with `total_cost_usd`; `log/usage.txt` (plan percentages); git history of w2/integrate (5,167 commits); the register; the ticket files.

**Skipped by the walls.** `gov-os-operator` and the operator copies (26 MB), and the WALLS and SETS rehearsal folders (0 bytes in the window). I opened no hidden, held-out, evaluation or secret path.

**Measures.**
- **Tokens:** input + cache creation + cache read + output. Cache reads are 97 % of all tokens.
- **USD at the CLI's rates:** I priced tokens at list-type rates. On the 547 headless sessions whose logs record `total_cost_usd`, those rates give twice the recorded figure (log $3,173 against $6,103 estimated). So every USD figure here is the estimate × 0.52. The owner pays a subscription, so USD here is notional and only a weight.
- **Active hours:** the sum of gaps of 5 minutes or less between consecutive records in one session.
- **Elapsed hours:** first-to-last time per session, capped at 24 h. For the main-tree sessions, gaps of 30 minutes or less.
- **Owner messages:** user records with `origin.kind == "human"`, de-duplicated by time and text. Tool results, task notifications, `isMeta` records (hook feedback, scheduled prompts), cross-session messages, compaction summaries and automated `/usage` probes are excluded.
- **Time zone:** UTC. Weeks start on Friday 10-16. W5 has 4 days.

**Classification rule.** Every token goes to one category, by this order:
1. **(e) product work:** a session or main-tree message whose subject is EXAMIN or W2-81. That means the W2-26/27/28/29/30/81/93/94 trees and the `gov-os-runs/W2-27*` and `W2-81*` folders, whatever the session's role.
2. **(d) security:** guard, hooks, sandbox, box, walls, secrets or gitleaks, `ACT-GUARD-FIX-*`, `P-JOBS-USER-*`, `P-PERMISSIONS`. For a ticket tree, that means tags guard/sandbox/secrets/containment/indep-walls/installs/fail-open, or a title naming guard, sandbox, hook or secret. For example W2-05, 42a, 56, 58, 84, 106, 110, 111, 127, 141, 149 and 186.
3. **(c) ceremony candidates:** register entries, packages, DND rows, ACT bundles and jobs (including W2-148, the operator agent), review and probe rounds (every worktree reviewer session, every auditor subagent), the October assessment lenses and investigations, checkpoints, restarts (the first turn of a fresh CTO session) and compaction recoveries (the first 3 messages after a continuation).
4. **(a) Gov OS product development:** engineer, test designer, product-spec and research sessions in ticket trees; builder subagents; main-tree Edit/Write to `src/`, `tests/` or `template/`.
5. **(b) coordination:** everything else. That covers lead sessions of (a) tickets, dispatch, briefs, waits and reading background output, status blocks, pings, ticket edits, landings, and building the coordination tools (dispatcher, job runner).

Main-tree sessions are classified **per message**, from that message's tool calls (command, file path, description; for Agent and SendMessage, the prompt's opening). A message without tool calls takes its turn's category.

**Check of the rule.** I read a token-weighted sample of 40 main-tree messages by hand. About 85 % agree with my reading; most disagreements fall between (b) and (c).

**Sensitivity of the rule:**
- Putting ceremony before security moves (c) from 24 % to 28 % and (d) from 19 % to 15 %.
- Counting lead sessions of (a) tickets as (a) moves about 10 points from (b) to (a), giving (a) 32 % and (b) 22 %.

Scripts and their intermediate results are in this folder: `scan.py`, `roles.py`, `subs.py`, `classify.py`, `rules.py`, `owner.py`, `final.py` and `alt/`.

## 2. The table (whole window)

| category | tokens (B) | share | output tokens (M) | share | USD at CLI rates | share | active h | share | elapsed h | share | owner messages | share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| (a) Gov OS product development | 6.62 | 20% | 43 | 28% | 2,764 | 22% | 215 | 27% | 469 | 21% | counted in (b) | – |
| (b) coordination | 11.04 | 33% | 39 | 25% | 4,046 | 32% | 228 | 29% | 861 | 38% | 153 | 28% |
| (c) ceremony candidates | 7.80 | 24% | 36 | 23% | 3,011 | 24% | 154 | 19% | 326 | 14% | 262 | 48% |
| (d) security work | 6.11 | 19% | 31 | 20% | 2,388 | 19% | 167 | 21% | 509 | 22% | 105 | 19% |
| (e) product work (EXAMIN, W2-81) | 1.40 | 4% | 7 | 4% | 544 | 4% | 31 | 4% | 113 | 5% | 24 | 4% |
| **total** | **32.97** | | **156** | | **12,753** | | **795** | | **2,277** | | **544** | |

Owner messages are classified by subject with the same keyword order. No owner message is counted as (a); messages about Gov OS tickets fall in (b). Besides the 544, the owner sent 15 messages straight to other sessions: 6 to the EXAMIN CTO and 8 to W2-81's adopter runs.

**By who spent it** (USD at CLI rates, share of the total):

| session kind | share | active h |
|---|---|---|
| CTO main tree | 31% | 144 |
| CTO subagents | 23% | 226 |
| ticket leads | 15% | 131 |
| test designers | 13% | 118 |
| engineers | 7% | 76 |
| reviewers | 6% | 58 |
| unclassified workers in trees | 2% | – |
| product runs (EXAMIN, W2-81) | 2% | – |
| other | 1% | – |

**What ceremony is made of** (USD at CLI rates):

| ceremony subtype | USD | share of all spend |
|---|---|---|
| review rounds and audits | $1,066 | 8% |
| assessment lenses and investigations | $660 | 5%; almost all in W1, the October lenses, DEC-813 to 830 |
| ACT bundles and jobs | $512 | 4% |
| packages, register, DND | $447 | 4% |
| checkpoints | $80 | – |
| restarts and compaction recoveries | $69 | – |
| other | $176 | – |

**What the owner's 544 messages were for:**

| purpose | messages |
|---|---|
| direction or questions | 175 |
| answering a package or decision | 140 |
| running a job, ACT, commit or push and relaying its result | 134 |
| starting or resuming a session | 50 |
| yes lines for ACTs | 33 |
| corrections | 9 |
| IDE file shown | 3 |

104 of the 544 came between 23:00 and 06:00 UTC. The agents also pushed 206 notifications to the owner's phone.

## 3. Per-week trend (USD shares at CLI rates)

| week | dates | tokens (B) | USD | active h | owner msgs | (a) | (b) | (c) | (d) | (e) |
|---|---|---|---|---|---|---|---|---|---|---|
| W1 | 10-16..10-22 | 5.42* | 2,054 | 100 | 66 | 7% | 25% | 47% | 21% | 0% |
| W2 | 10-23..10-29 | 2.81 | 1,168 | 70 | 48 | 23% | 36% | 14% | 27% | 0% |
| W3 | 10-30..11-05 | 8.06 | 3,160 | 193 | 162 | 29% | 35% | 17% | 16% | 4% |
| W4 | 11-06..11-12 | 8.99 | 3,510 | 238 | 147 | 33% | 28% | 23% | 15% | 1% |
| W5 | 11-13..11-16 (4 days) | 7.68 | 2,861 | 194 | 121 | 10% | 36% | 20% | 21% | 13% |

\* W1 is under-counted: 10-16 and 10-17 lost transcripts (see §5).

**Ceremony output per week, from git and the register:**

| week | register entries | DEC-record commits | ACTs applied | probe or review record commits | merges | close commits |
|---|---|---|---|---|---|---|
| W1 | 106 | 0 | 0 | 18 | 12 | 13 |
| W2 | 29 | 9 | 1 | 15 | 22 | 19 |
| W3 | 128 | 40 | 4 | 20 | 274 | 47 |
| W4 | 183 | 65 | 22 | 64 | 242 | 82 |
| W5 | 51 | 46 | 13 | 86 | 177 | 95 |
| **total** | **497** (about 200,000 words) | **160** | **40** | **203** | **727** | **256** |

The register now holds about 328,000 words. 90 commits in the window carry `Role: owner`.

**Plan limit** (`usage.txt`): the weekly limit reached 100 % in the week that reset on Nov 8 and 97 % in the week that reset on Nov 15. By 11-16 17:04 the current week stood at 56 %, with 13,801 requests and 241 sessions in the last 24 hours.

**Reading of the trend:**
- **W1** was the owner's assessment week: lenses A to I, an independent assessment of Gov OS, filed as ceremony.
- **W2** was quiet.
- **W3** held the emergency (DEC-1047, 11-02). Volume tripled, coordination stood at 35 %, and owner messages peaked at 162.
- **W4** had the most product development (33 %), but also the ACT surge (22 applied), 183 register entries, and the plan limit hit.
- **W5** is the only week where product work is visible (13 %: EXAMIN's Wave 0 and W2-81's re-run). Gov OS development fell to 10 %. Owner messages ran at 30 a day, 54 of them relays of jobs the owner ran.

## 4. Examples (USD at CLI rates)

**(a) Gov OS product development**
- W2-32 retrieval: engineer and test designer, about $170.
- W2-88 (memory for any repository): engineer and test designer, about $118.
- W2-96 (gov accept): test designer, $61.
- W2-67 (test hygiene): test designer, $60.
- CTO subagents "D-10 red-fix list" ($102) and "D-5: the templates" ($82).

**(b) coordination**
- W2-88's lead ($90), W2-67's lead ($55), W2-60a's lead ($54).
- CTO subagents "Build operator job runner" ($91) and "Build the dispatcher with tests" ($47).
- The main tree's waits: 1,994 task notifications read, 380 SendMessage relays, 206 pushes.

**(c) ceremony candidates**
- Review rounds on W2-96 ($44), W2-67 ($31) and W2-88 ($30).
- W2-148, the operator agent (engineer, $30).
- The subagent "Build ACT-DEADMAN-INBOX-1 bundle" ($29).
- The October assessment lenses I1 to I4 (the logs record $274, $91, $84 and $33).
- 497 register entries in 31 days.

**(d) security work**
- W2-111 (hook latency): lead, $115.
- W2-05 (the git environment of the hooks): lead, test designer and reviewer, about $176.
- Subagent "Build P-JOBS-USER-1 (B) session sandbox", $66.
- Subagent "Build ACT-GUARD-FIX-7 bundle", $44.
- W2-149 (walls, set-up A), about $95.

**(e) product work**
- The EXAMIN run folder (W2-27), $66.
- W2-81's reviewer ($52) and test designer ($46).
- W2-81's adopter runs: python-app ($32 on 0.1.0), secret-history and typescript-monorepo ($18 each).
- W2-94's lead, $24.

## 5. What could not be measured, and how big the unknown is

1. **Lost transcripts at the start of the window.** Claude Code's 30-day cleanup has already removed the transcripts last written on 10-16 and 10-17. Those two days show 0.16 B tokens against 181 commits, and 31 lead logs from those days ($92 recorded) have no transcript left. At the window's average of about 6.4 M tokens per commit, roughly 1 B tokens are missing, about 3 % of the total and mostly W1. Every day of waiting loses one more day.
2. **The operator agent's sessions** were skipped by the walls: 24 MB of about 4 GB of transcripts, under 1 %. They would add to (c) and (d).
3. **The owner's own time** cannot be measured: reading packages, running jobs in a terminal, phone pushes. Only message counts and times are visible. 134 messages report jobs the owner ran outside Claude Code, and their duration is unknown.
4. **USD is notional:** calibrated on headless sessions only. Interactive sessions write 1-hour caches, and their true rate may differ by tens of percent. Shares move far less than absolute figures.
5. **Classification error** is about 15 % per message, mostly between (b) and (c). Ordering (§1) moves up to 4 points between (c) and (d), and up to 10 points between (a) and (b).
6. **Wall time** has two biased readings. Active hours (gaps of 5 minutes or less) under-count leads that wait on long test runs; the lead logs' `duration_ms` totals 933 h against 795 active hours across all sessions. Elapsed hours over-count overlapping waits.
7. **Owner messages by subject** come from a keyword reading of each message's opening. Long messages spanning several subjects are counted once, under the first matching category.

## 6. Findings

### F1. Product work got 4 % of the month; coordination and ceremony together got 56 %
Coordination (32 %) and ceremony candidates (24 %) took 56 % of the spend and 76 % of the owner's messages. Gov OS product development took 22 % (up to 32 % if leads count as building), and EXAMIN and W2-81 took 4 %.
- The CTO's main tree and its subagents spent 54 % of all usage.
- Engineers in ticket trees spent 7 %, and test designers 13 %, nearly twice the engineers.
- DEC-1047 asks that "everything else must justify itself" beyond tests and code that match the KPIs. On this measure most of the month's usage is the "everything else".

Ordinary work: yes, because this is the measured shape of normal operations over 31 days, not a constructed case.
Consequence: other (spend and throughput; the weekly plan limit was hit twice, so overhead directly displaced building).

This is not blocking (no fail-open, no lost work). It is a row for the owner.

What would reverse it: a re-classification showing that more than half of (b) is work by ticket leads on code and tests, rather than waiting, relaying and re-briefing. Or evidence that the plan limit was not binding.

### F2. The owner is a relay inside the loop
- 544 owner messages in 31 days: about 18 a day, peak 46 on 11-12, 104 at night.
- 134 report a job, ACT, commit or push the owner ran by hand and relay its output.
- 33 are yes lines for ACTs, 140 answer packages, and 50 start or resume sessions.
- Against that, 206 phone pushes and 497 register entries (about 200,000 words) were produced for the owner to read or approve.
- 48 % of the owner's messages concern ceremony subjects.

The aim's "governing the traffic, not governing a city" is contradicted by the owner acting as both traffic controller and operator.

Ordinary work: yes, because it happens every day in the normal flow (W5: 30 owner messages a day, 54 of them job relays).
Consequence: other (owner time and latency; nothing fails open).

A row for the owner, not a round.

What would reverse it: evidence that most of the 134 relays were one-off set-up jobs that will not recur once ACT-OPERATOR and P-JOBS-USER are live. The W5 rate argues against that so far.

### F3. Security work cost about as much as Gov OS's own building, and 4.4 times the product work
Security took 19 % of the spend (15 to 19 % depending on ordering) and 105 owner messages.
- Examples: W2-111, W2-05, W2-149, W2-141 and W2-186; ACT-GUARD-FIX-1 to 7; P-JOBS-USER-1; the box and the walls.
- Its share rose again in W5 (21 %) after falling to 15 to 16 % in W3 and W4.
- DEC-1047 says "not a security battle". The threat model in DEC-1204 covers honest mistakes and drift, not a same-privilege adversary. I have not judged each security item against that bar here; part 2 or the combining auditor should.

Ordinary work: yes, because these are normal tickets and ACTs, not crafted cases.
Consequence: other (spend; this measure says nothing on whether any item fails open).

A row.

What would reverse it: a per-item audit showing that most of this spend closed holes an honest agent hits in ordinary work, which fail open or lose work (the golden rule's bar). That would make the spend justified, not ceremony.

### F4. The evidence for this retrospective is being deleted
Transcripts older than 30 days are removed automatically. 10-16 and 10-17 are already mostly gone (about 1 B tokens, $92 of lead runs without a transcript). The next audit of W1 or W2 will find less each day.

Ordinary work: yes, because the default cleanup runs without any action by anyone.
Consequence: loses work (records and evidence; not code).

It is in scope for this retrospective but not a ticket's KPI. Under DEC-1204 it is a row for the owner to decide. Nothing is lifted or changed by me.

What would reverse it: a finding that the transcripts are archived elsewhere (I did not search for a copy), or a `cleanupPeriodDays` setting I did not see. The user, local and project settings files name none, so the 30-day default applies.

### F5. Restarts are cheap in tokens but costly in owner turns
- Restart and compaction recovery tokens are small ($69, plus $80 for checkpoints): 78 compaction continuations and 25 main-tree sessions with owner messages.
- But 50 owner messages are restarts or resumes, the second-largest owner cost after packages and relays.

Ordinary work: yes, because sessions fill their window daily.
Consequence: other.

A row.

What would reverse it: owner messages at restarts that turn out to carry decisions rather than boilerplate. Several do (for example the pre-restart decisions on 11-03), which would move some of the 50 into "answering a package".

**Classification of the findings:** F1 to F3 and F5 are other; F4 loses work (evidence only). None is in a ticket's scope, so no round is proposed. All are rows for the owner.

**Decisions these findings rest on:** DEC-1047, DEC-1204 (and through it DEC-801, DEC-1010), DEC-953 item 2 (the refusal noted above).
