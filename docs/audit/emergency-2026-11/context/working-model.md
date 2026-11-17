# Summary: the working model (how the owner works with the Gov OS CTO, the EXAMIN CTO and the operator)

A one-page summary, 2026-11-16. Sources: DEC-1199 (roles), DEC-1173, DEC-1191, DEC-1193, DEC-1196 (5), DEC-1203,
DEC-1205, DEC-1209; `governance/project/operator/class-rules.yaml`, `operator_run.py` (gates G1-G9);
`~/gov-os-operator/queue/jobs/README.md` (the job protocol); `governance/project/prompts/w2-orchestrator.md`.

**Who does what.** The **owner** decides. The **Gov OS CTO** (this repository's orchestrator session, tmux `cto`)
works on Gov OS only: it sees what is broken or missing, fixes Gov OS, or asks the EXAMIN CTO to act. The **EXAMIN
CTO** (an interactive session, Remote Control "EXAMIN CTO") leads EXAMIN's Wave 0. The **operator** applies what needs
the owner's permissions: ACTs (a program with gates, outside the CTOs' sessions) and jobs (the operator's console).

**Channels.**
- The owner talks to each CTO directly: this CTO in its chat; the EXAMIN CTO in the app. Nothing reaches a CTO
  through another CTO as the owner's word unless the owner wrote it; relays say so.
- The CTOs talk to each other by cross-session messages (SendMessage) and the EXAMIN CTO's `REQUESTS.md` / the Gov OS
  CTO's `examin/REPLIES.md`.
- The CTOs talk to the operator only through the queue: ACT requests (`~/gov-os-operator/queue/<ACT>.req`, one line
  `<ACT-id> <manifest sha256>`) and jobs (`~/gov-os-operator/queue/jobs/JOB-<yyyymmdd>-<nn>.md`). The Gov OS CTO reads
  every product CTO's job in full before copying it into the queue unchanged.

**The owner's line forms.**
- `yes ACT-<id> <sha8>`, alone on a line, in the Gov OS CTO's chat: approves one class (b) ACT bundle at that manifest;
  the operator's gate G6 reads it from the CTO's transcript. (Once boxed, the owner gives yes lines to the operator
  directly until it reads `~/.gov-os-owner/yes.log`.)
- Package lines: `P-<NAME>-1 (a)` (or the option named), `yes <artefact> <sha8>` for an approved text, `<ticket> keeps
  …`, and the like; each is recorded as a register entry by the CTO (DEC-861), with "Decided-by: owner".
- `run JOB-<id>`, in the operator's console chat: the operator runs that job file and writes
  `queue/jobs/results/JOB-<id>.result.md`; the CTO's watcher turns it into an inbox item. The jobs README is the
  operator's rulebook: every change to it is quoted to the owner before the operator follows it.

**ACT classes** (`class-rules.yaml`, DEC-1173): **(a)** the CTO commits it (ordinary repository work); **(b)** control
paths (the guard and hooks, settings, CLAUDE.md and AGENTS.md, the dispatcher's tools, the operator's files): a bundle
built and rehearsed on copies, one independent review under the golden rule (at most two rounds), the owner's yes
line, then the operator applies it with its gates G1-G9 (frozen, under a decision, rehearsed with 0 failures, READY by
code, sha match, class, live state, a dry run, holds); **(O)** by the owner's own hand.

**The owner's plain terminal** (never a Claude session): releases with the typed release code; re-pins; the session
box's pin steps (`pin_owner.sh`, the held-out history count); the operator's full-permission steps
(OWNER-OPERATOR-FULL-1); installs; one-line settings changes the owner chooses to make by hand. Every handed command is
rehearsed on a copy first and refuses without its explicit target (DEC-1196 (5)).

**Rhythm.** A 09:00 morning package and an 18:00 evening digest (decisions since the owner's last push, the owner's
items in short form, the CTO's delegated decisions, restarts, usage, guard refusals, memory use, disk, leads). Every
report ends with `status_block.py`'s block (counts, leads, closes, reopened and new tickets with their approving
lines, what waits on the owner).

**How work is judged and routed.** The golden rule (DEC-1204, the `judging-work` skill): a finding blocks only if it
is in scope, an honest agent hits it in ordinary work, and it fails open or loses work; crafted constructions are Wave
3 rows; at most two rounds, then the owner once. The provisional rubric (DEC-1208) routes work as Q (quick), L, S or F,
with protected areas never quick.

**In force now: the emergency (DEC-1209, 17:26).** No new tickets; running work stops at its current step; no new
review round, lead or worker; the audits and the rubric research go on; EXAMIN works directly; the emergency's own
fixes (GF-8, GF-9, the box and its start lines, the operator's full permission) first; lifted only by the owner after
deciding from the reports in `docs/audit/emergency-2026-11/`.
