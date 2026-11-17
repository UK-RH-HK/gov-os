# P-GOLDEN-RULE-1: one golden rule for judging work (ADR-0001 + DEC-801 + DEC-1010), a kernel skill, shipped

Drafted 2026-11-16 for the owner (the owner's message of ~16:4x). It asks your approval of (1) a register entry, (2) a
kernel skill's text (by its sha256; the kernel change goes by CIT-P), (3) a product ticket on your P1, and (4) the
interim practice.

## 1. The register entry (next free id at commit: DEC-1204)
> ### DEC-1204 — How work is judged: one golden rule (merges ADR-0001 / DEC-039, DEC-801 and DEC-1010 item 1) (standing)
> - **Status:** ACCEPTED (owner, 2026-11-16) · **Under:** DEC-039, DEC-801, DEC-802, DEC-803, DEC-1010 · **Changes:**
>   DEC-039, DEC-801, DEC-1010 (1): each keeps its id and now points here.
> - **Decision:** (1) **The threat model:** Gov OS guards against honest agent mistakes, plausible accidents and drift
>   in ordinary work, not a same-privilege adversary; the hard boundary is git history, protected-branch CI and the
>   owner's signed approvals. (2) **What may block:** only a finding, within the change's scope, that an honest agent
>   can hit in ordinary work and that fails open or loses work; a finding that needs a deliberate construction
>   (decoys, booby-traps, planted links, hand-set git environment or replace refs, chained escapes) is a Wave 3 row,
>   never a new round. (3) **How reviews converge:** a moderator triages every finding against the change's scope; at
>   most two rounds, then the owner once with options; no extra round on its own; READY computed by code from each
>   reviewer's structured verdict. (4) It applies to every review, the ACTs, the job runner and the box included
>   (the owner, 2026-11-16 ~16:3x). (5) It lives in one kernel skill, `judging-work`, preloaded by every role that
>   judges work and put into every such brief by `gov brief`; it ships through the kit and every release.
> - Marks on the three: DEC-039 "· **Changed by DEC-1204:** merged into the golden rule"; DEC-801 the same;
>   DEC-1010 "· **Changed by DEC-1204:** item 1 merged into the golden rule".

## 2. The skill: `template/governance/kernel/skills/judging-work/SKILL.md`
sha256 `0fc1c502f553eb780bb0af4652b04f676853b10e097270c2d6ad2bea89a5f5c7`, 58 lines, in the kernel skills' form
(front matter name/description/version 1.0.0). Its five sections: the threat model; what may block (the two questions
word for word, the two record lines); how reviews converge (moderator, two rounds then the owner, no extra round,
feature-gated risks, READY from the fenced verdict block); doing it (reviewer/auditor/probe/QA; moderator/CTO;
packages); what it is not (it never lowers a wall). The file is `drafts/golden-rule/SKILL.md`, word for word what
the CIT-P installs.

## 3. The product change (a ticket, for your P1; no ticket is filed without it)
**Title:** "The golden rule ships: the judging-work skill preloaded, briefed and checked". Profile FULL (it touches
the kernel and the launcher's refusals). Allowed paths: the skill folder; the role files' Skills lines;
`template/governance/kernel/templates/role-reviewer.md` (its `skills:` list); `src/gov/brief/build.py`;
`src/gov/launch/role.py` / `launcher.py` (the refusal); `src/gov/adopt/fabric.py` (`KERNEL_FOLDERS`) and the shipped
lists (`fabric.PACKAGED`, `test_w2_88_shipped` THE_SHIPPED, W2-88's acceptance ITEMS); their unit tests.
KPI lines (each with its verify):
- S1 **Preloaded:** the Skills line of `independent-auditor.md` and `qa-engineer.md`, and `role-reviewer.md`'s
  `skills:` list, name `judging-work`; a launch of each role carries the skill (the launch record's `skills`).
- S2 **Briefed automatically:** `gov brief <role>` for the independent-auditor, reviewer and QA roles (and a lead
  brief's reviewer/probe step) includes the skill's sections 1-3 from the installed skill file, never a hand copy;
  the brief names the skill's version.
- S3 **Checked:** `gov brief` refuses `BRIEF_JUDGING_RULE_MISSING` and `gov launch` refuses `LAUNCH_JUDGING_RULE_MISSING`
  for a judging role (independent-auditor, reviewer, probe, QA engineer) whose brief or role lacks the skill or names
  a different version; a unit case per role and one acceptance case.
- S4 **Shipped:** `gov init` (the kit) and a wheel of HEAD both deliver the skill (`.claude/skills/judging-work/`
  after `gov adapters generate`); the shipped-folder lists include it exactly.
- F1 the skill's text is never edited by the brief builder (its sha256 in the brief equals the installed file's).
The kernel files (the skill, the role files, the template) need the CIT-P below before any merge.

## 4. The CIT-P
`docs/changes/<ticket>-CIT-P.md`, written by the ticket's lead with the bytes: the new `SKILL.md` (sha256 above), the
Skills-line diffs of `independent-auditor.md` (`audit, retrieval` → `audit, judging-work, retrieval`) and
`qa-engineer.md` (`qa-review` → `qa-review, judging-work`), and `role-reviewer.md`'s `skills: [audit]` →
`skills: [audit, judging-work]`. The orchestrator's and ticket-lead's role files gain it too
(`orchestration, …, judging-work, …`), since they moderate and triage. Your approval is by the bytes' sha256.

## 5. EXAMIN first
EXAMIN's copy runs 0.1.0 until its run's end (DEC-1198 (1)); its Wave 0 starts now. Two routes:
(a) **recommended:** the EXAMIN CTO receives the skill's text now, by a REPLIES.md section and a copy at
`<clone>/.gov-runtime/scratch/govos/judging-work.md`, and applies it by hand (as the CTO does, section 6) until the
release carrying the ticket is installed in its copy (0.1.2); (b) a kit update into the copy now (an owner job),
before the product check exists. Every later product CTO receives it through `gov init` and `gov adopt`.

## 6. The interim (from today until the ticket lands): the CTO's standing paragraph
Pasted, word for word, into every reviewer, auditor, probe and QA brief the CTO or a lead writes:
> **Judging work (the golden rule, DEC-1204; ADR-0001, DEC-801, DEC-1010):** you judge against ADR-0001's threat
> model: honest agent mistakes, plausible accidents and drift in ordinary work, not a same-privilege adversary. Ask of
> every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
> A finding blocks only if both answers are yes and it is within this change's scope; a finding that needs a
> deliberate construction (a decoy, a booby-trap, a planted link, hand-set git environment or replace refs, a chained
> escape) is a Wave 3 row, never a new round; one outside the scope is a row for the ticket that owns it. Every finding
> carries `Ordinary work: yes|no, because ...` and `Consequence: fails open|loses work|other`. End with ONE fenced
> `verdict` block, unquoted. A moderator triages your findings; at most two rounds, then the owner once.

## 7. Costs, options, recommendation, your lines
- (a) **Recommended:** DEC-1204 now; the skill by CIT-P; the ticket now (about a day: TD, engineer, the kernel step,
  review); EXAMIN by route 5 (a); the interim paragraph from today. Cost: a day of a lead plus your approval of the
  bytes. Every adopted repository inherits a checked rule.
- (b) The register entry and the skill only, no brief injection or check: half a day; the rule is loaded but can
  still be left out of a hand-written brief.
- (c) The register entry and the interim paragraph only: no product change; the risk that it is forgotten again.

**Your lines:** `P-GOLDEN-RULE-1 (a)` (this also approves the ticket on your P1 and DEC-1204's text), `(b)` or `(c)`;
and `yes judging-work 0fc1c502` for the skill's text (the CIT-P approval follows on its bytes).
