# The owner's decisions on the Emergency 2 audits

Owner: Usain. Built with his advisor, one audit at a time, from `docs/emergency-2/audits/`. For the CTO to execute as
the refactoring and building plan that finishes Gov OS. Each line is the owner's decision unless marked otherwise.

## Audit 09: usage, the last two days (decided 2026-11-18)

**What the audit found.** $1,616 and 65 % of the weekly plan in 62 hours. The CTO's apparatus spent 64 % (its forks
30 %); 39 % went into machinery Emergency 2 retires; 8.5 % into machine wake-ups of the CTO; 95 % ran on Opus. The cost
is context: 52 % of the money went on messages carrying over 300k tokens, which only the CTO, its forks and the EXAMIN
CTO reached.

**Decisions.**
1. **The CTO's context:** no cap; the full window, up to a million tokens, always. A fresh CTO session each morning,
   without stopping any lead or worker, with a smooth handover through its checkpoint and EMERGENCY-2.md.
2. **Models and effort:** every session (helpers and leads included) runs the model and effort the rubric gives its
   role; no session chooses its own. Enforced by code: the launcher picks them for launched roles; the CTO's helpers
   come from fixed roles with their model set, a Sonnet default in `~/.claude/settings.json`, and any other model
   refused. An exception comes to the owner as one line; he decides.
3. **The rubric moves from Opus to Sonnet** for: the owner's operator session; every lead, all profiles; every helper
   the CTO spawns; the proving runs, acceptance included; and C2 engineers, test designers and auditors. C3 roles
   stay on Opus, and so does the CTO. Running it is the trial: if quality drops for a role, the CTO tells the owner, and the owner
   changes that role back in code. Until audit 04's full table is decided, the rubric is DEC-1120's table with these
   changes.
4. **The CTO's own items, applied now as the audit recommends:** stay off the retired machinery and close W2-111,
   W2-186 and W2-56 on their records; no inbox waiter and no idle-check wake-ups (files and one daily digest); no fork
   for helper work, a fresh helper from a written brief; review only red work, two rounds at most; check the 5-minute
   cache before applying it to workers; no register entry for what the landing records; one plan reading an hour, a
   daily budget, and points reserved first for the two fresh-80 measures and the proving run.
5. **The EXAMIN CTO** is retired and started fresh by the CTO (its guards off and no-prompt mode set first, its old
   Claude memory moved aside, Remote Control on, a short brief from its approved Wave 0 brief 2ec48c78, its reports
   and the latest reply).

## Audits 01 to 08: the decisions page (decided 2026-11-18)

Already decided before the page: U1 to U4 and L4 (audit 09, above); Q-CAP44 approved (W2-192's Contract line for the
spec-audit adoption stage, Contract 4.4).

### Planning and tickets
- **K1, the rubric (audit 4, Table 3): (a) approved.** Its model and effort table follows the decisions of audit 09
  (Sonnet for leads, helpers and C2 roles; C3 roles and the CTO on Opus). The landing and the close are code and
  deterministic; a quality auditor is launched only when a landing goes red or a merge fails, to find and fix the cause.
- **K2, approval per ticket: (c).** The owner's note: DEC-974 (no new tickets without the owner) is superseded by the
  planning-first way of working. Wave 0 (EXAMIN's refactor, its memory) is a planning stage and needs no approval per
  ticket. Each later wave is planned with a set list of tickets; adding or removing a ticket in a planned wave asks the
  owner.

### Records and rules
- **G4, the register: (a)** all 33 groups as listed; the CTO settles the doubtful rows. DEC-027 (signed tags as the
  root of trust) moves to superseded, following L3.
- **G5, the re-baseline: (a)** Charter v6 and Contract v5 in one change, approved by group.
- **G6, fresh audits: (a)** at the release acceptance and at adoption stages A5, AS, A7, A10; otherwise only for a red,
  a failed landing or a feature not working. The Contract changes to match.
- **G7, installs: (c)** the CTO approves and records every install, so nothing out of the work's scope or beyond the
  machine's capacity is installed; sudo stays the owner's.
- **L3, release authenticity: (a)** pinned and hash-checked, no signing until friction asks for it; DEC-027 superseded.

### Landing, close and memory
- **L1, gov queue: confirmed** (the thin queue).
- **L2, DONE: confirmed** (DONE is the green landing). The owner's note: the landing and the close are one deterministic
  action. The landing writes the close record itself; no separate close step carries weight of its own. The CTO
  proposes which `gov` commands stay and which retire on that basis: practical, fast, cheap, high quality, records kept,
  nothing duplicated.
- **M1, gov context: (c)** retire the module too; the close (inside the landing) records decisions from the ticket's
  sources. Everything that depended on `gov context` is replaced by something tested and proven; no ceiling anywhere.
- **Q-CLOSE:** folded into the landing-and-close merge of L2: the landing records such a red as a known base red; no
  separate rule, no Wave 3 row.

### Repository
- **G1, retired history: (b) and (c)** `git rm` the retired code, tests, ACT bundles and prompts, and also keep them on
  an archive branch, besides the tag `pre-emergency-2`. Before anything is removed: bundle the six worktrees' unique
  commits and tar the live scratch tools. Memory's index is cleaned before the first fresh-80 measure.
- **G2, origin/record/w2: (a)** keep it, stop syncing, remove its worktree.
- **G3, the 43 GB beside the repository: (b)** a later audit, once the refactoring is safely finished: the size of Gov
  OS's documents, worktrees and folders, what is duplicated, what can be deleted and what stays.

### The run-time tool
- **T1, the stall check from the dispatcher's cron pass: confirmed.** (It runs in a shell script, at no model cost; the
  inbox waiter and idle hook were retired by audit 09's decisions.)
- **T2, phone pushes: confirmed, extended:** also when the CTO needs a decision from the owner (features, specs, KPIs,
  data and measurement, P1 decisions touching the core or kernel). The CTO reviews the escalation rubric against these
  changes and proposes whether to change it.
- **T3, no GPU: confirmed.**
- **Q-UPD, gov update and the owner's edits: confirmed** (the three-way merge).

### EXAMIN
- **E1, the dispositions: (b)** all at once, after the owner has read everything (his answers on the EXAMIN page).
- **E2, tests kept green: (a)** no new red by test id, plus green characterization tests; Tesseract and Poppler installed
  by the owner before the merge back.
- **E3, the amended brief: (a)** EMERGENCY-2 §7 plus a one-page addendum. The memory standard is the end-to-end figure,
  95 % or better on a fresh 80; hit@5 is not a target. The EXAMIN CTO launches an independent question writer (a fresh
  session that never sees the store's build) and runs EXAMIN's measure itself; the transcript scan voids a measure if
  the hidden half is read; the question sets live outside the clone and are never indexed.

### The nightly
- **NIGHT: (c)** both stay off for now. Fixes go ahead and land; done tickets land as a batch, and a full suite runs
  when a landing needs it, with every red fixed to green. When everything is green again in the morning, the nightly
  and the morning brief come back.

## EXAMIN's Wave 0 decisions page (decided 2026-11-18, all at once, as E1 (b))

All eighteen as the EXAMIN CTO recommends, with these additions:
- **G2:** the 242 task cards are converted into records too (id, type, status, as the reports), not archived out of
  memory: they record why EXAMIN's code exists.
- **N1:** CLAUDE.md and AGENTS.md rewritten on Gov OS's template for adopted repositories, keeping the owner's binding
  rules (every id with a description, the five rules, fast only where a check can prove you wrong).
- **From the memory assessment:** the 1,568 answered packages stay records (their id stripped only if the fresh 80 shows
  them crowding); the archived legacy sources stay out of memory's index once their records exist; a `gov rebuild`
  after each batch of step 5 commits, through the resource gate.
- **The measure:** as E3 above.
- **Order:** `gov update` to 0.1.3 first, from the Gov OS CTO's note; then step 5, group by group, each group one
  reversible commit, no new red by test id.
