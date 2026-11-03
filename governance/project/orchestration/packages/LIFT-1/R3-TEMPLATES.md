# R3 — Templates, as good software companies use them (DEC-1050 TEMPLATES)

By the R3 researcher, read-only, 2026-11-02. Helpers and outputs: `/tmp/gov-os-inv-R3/` (`briefsizes.py`, `gaps.py`).
**Revised after R2** (`drafts/LIFT-1/R2-BRIEFS.md`, which arrived after my first draft). §B′ says what R2 changed; the lead
template (T-7), the measures (§B), TPL-3 and TPL-7 now build on R2's evidence. Where we both counted the same thing,
the figures agree: 511 gap lines and 7,424 minutes in 83 returns; worker briefs with a median of about 12.6k to 12.9k characters.

**Headline.**
1. There is no single template. Each session's instructions are put together from four layers of text that disagree: the kernel `brief-*.md` (9 Oct), Appendix A of the 116 KB CTO prompt, the 54 KB common lead brief, and the worker briefs that leads write by hand (440 of them, median 12.9k characters, 35 % of it standing rules copied over). The common brief says outright that its rules "override the templates where they differ".
2. The role files never reach a launched session. `gov launch` passes no `--agent` and no `--append-system-prompt-file`, and none of the 440 briefs uses either flag. A worker learns its role only from what its lead copied into the brief. Several kernel texts still state rules that are now superseded (for example, the engineer "reads the acceptance tests and runs them until they pass", against DEC-957/959).
3. Leads reported 511 brief-gap lines in 83 returns, 7,424 stated minutes in all. By keyword the gaps are about guard or sandbox refusals (119), paths (114), rebuild/store (101), command forms (88) and decision readings (82). 197 of them were placed in the common brief and 119 in the ticket's part. What is missing is facts (paths, commands, which text holds), not rules.
4. Good companies keep one short template per artifact. The stable "how" lives in a shared file that loads every time, the per-task facts are filled in, done is defined once, rules with no exceptions are enforced by tools rather than prose, and every return has a fixed form (sources §A).
R2 corrects the premise. The "3 %" was 3 % of the mandated *decision reading list*, not of the brief. Leads follow the brief's commands (83 to 100 % for 11 of 14 commands). Their time goes into *doing*: 25 % of tool calls are wait loops, 12 % ceremony steps, 343 verification wrappers written by hand, 218 harness denials. Once the brief gave a command form that works, the share of sessions with a guard refusal fell from 68 % to 17 %. So the templates must give working steps and shipped scripts, not more text to read, and their KPI is the per-line follow rate.
5. The design: one kernel template per role plus a ticket template and a brief envelope. The lead's template comes as one short form per kind of run (tests only, implement and verify, review round, resume, land), and its commands ship as scripts (`lead_verify.sh`, `launch_worker.sh`, `wait_for.sh`). They are filled by a generator from the ticket file and one tested project facts file (`paths`, `commands`, step switches). They reach every session the same way: the launcher appends the role template to the system prompt, rulesync puts it in the `.claude/agents/` bodies, and the brief comes on stdin. Reading and following are measured from returns and transcripts, never gated. The work is eight packages, TPL-1 to TPL-8 (§D), each with testable KPI lines. The templates are in the Appendix.

---

## Table

| id | what | where (paths, tickets, decisions) | cost (machine / tokens / owner; source) | what it protects | DEC-1010 test: in aim? ordinary work? fails open or loses work? | recommendation | what lifting takes (code, tests, tickets, config) | depends on |
|---|---|---|---|---|---|---|---|---|
| R3-1 | **Four layers of brief text that contradict one another**: kernel `brief-*.md`, the CTO prompt's Appendix A (A1–A5), `LEAD-w2-common.md` ("they override the templates where they differ", l.90), and each lead's own worker briefs | `template/governance/kernel/templates/brief-*.md`; `governance/project/prompts/w2-orchestrator.md` l.372–430; `governance/project/briefs/LEAD-w2-common.md`; DEC-537, DEC-824 | T: a lead reads ~56k characters on stdin plus the files it is told to read. 82 gap lines on decision readings or contradictions (keyword count, `gaps.py`). Claude Code's own docs: when two instructions contradict, "Claude may pick one arbitrarily" (§A9) | Every session gets the rules | In aim (aim 2, 3) / yes / loses work: a wrong reading costs a round | **Replace** with one template per role (Appendix). Appendix A and the common brief become pointers. History stays in the register | TPL-1, TPL-6 | owner's row decisions (P1) for the conditional lines |
| R3-2 | **Leads write every worker brief by hand** and copy the standing rules into each one | `~/gov-os-worktrees/*/.gov-runtime/scratch/lead/briefs/*.md`: n = 440, median 12,891 characters, p90 20,022, max 47,889; 324 have a "Standing rules" section, median 4,910 characters, a median 35 % of the brief (`briefsizes.py`) | T: brief writing is lead output tokens; the copies drift. The combined list (R-1 note) puts the median worker brief at 12.9k | Workers get the rules | In aim / yes / a dropped rule loses work | **Generate** briefs from template + ticket + facts. The lead writes only the "what the lead knows" paragraph and any repair input | TPL-3 | TPL-1, TPL-2 |
| R3-3 | **Role files do not reach launched sessions.** `gov launch` starts `claude --settings … <cli_args>` with no agent or system-prompt file. The `.claude/agents/*.md` bodies load only for an in-session subagent of that type | `src/gov/launch/launcher.py` `launch()` l.284–330; 0 of 440 briefs pass `--agent` or `--append-system-prompt*` (grep; the 3 hits are W2-60a's subject matter, not launches) | None directly. It is why rules get copied by hand (R3-2) | — | A coupling gap: the role "states" but is never shown | **Deliver**: the launcher appends the role template with `--append-system-prompt-file` (CLI 2.1.316 here supports it, §A10). The lead's dispatcher launch line does the same | TPL-4: ~10 lines in `launcher.py` plus unit tests; the dispatcher's launch line | TPL-1 |
| R3-4 | **Kernel texts state superseded rules.** `roles/engineer.md`: "implement … until its acceptance tests pass". `brief-engineer.md`: "What you read: the ticket's acceptance tests" and "run the acceptance tests … until they pass" (against DEC-957/959: the engineer never reads them and runs them only through `gov accept`). `skills/test-design`: "does not read … src/" (against A1/DEC-963: it reads the existing code on `w2/integrate`). `roles/orchestrator.md`: `gov checkpoint` at every round (R-6). Kernel briefs: "The guard refuses here-documents …" (goes with G-1/G-2) | the files named | T and rounds: a worker that follows the kernel text breaks the procedure (not measured) | — | Drift between text and practice | **Rewrite** within TPL-1, one CIT-P for the kernel (CAP-33). K-4's two orchestration-skill lines go in the same CIT-P | TPL-1, TPL-6 | G-1/G-2 landing (E3) for the guard lines |
| R3-5 | **The ticket format has no non-goals, no per-KPI way to verify, and no definition of ready.** KPI lines mix the rule, its citation and its history | `.tickets/*.md`; `template/governance/kernel/templates/ticket.md`; `schemas/ticket.schema.json`. 136 W2 tickets: median 3,824 characters, median 5 success lines, median line 224 characters; **2 of 136 name non-goals or out-of-scope items** | Rounds and findings go to scope questions (DEC-1010's moderator does this triage by hand) | Clear scope (aim 2, 4) | In aim / yes / an unclear scope loses rounds | **Add** to the ticket template: `non_goals`, `verify` per KPI line (the observable check), `done_when` pointing to the one DoD. A ready check prints its gaps as warnings (not a gate) | TPL-5: schema plus template plus `gov brief` warnings; existing tickets are not re-written (only new and re-profiled ones) | TPL-2 |
| R3-6 | **No single Definition of Done.** "Done" is spread across the lead brief's steps 4–7, the close, the queue, DEC-1010 and DEC-968 | brief l.145–166; `gov close`; `land.py` | T: leads re-derive it each run (gap lines "return / record form": 62) | One finish line (aim 4) | In aim / yes / a missed step loses a landing | **One DoD** of six lines in the facts file, quoted by the ticket and lead templates | TPL-2 | — |
| R3-7 | **Commands live in prose, untested.** Forms like the serial-phase one-liner, the `gov launch` line and `rebuild_slot.sh` appear only in brief text. A tool change breaks them silently | brief l.92–97, l.106, l.155–156 | 88 gap lines on command forms. 119 on guard/sandbox refusals, many of them caused by command forms (79 of 86 logged refusals were false: G-1). The combined list notes 4 owner commits in 3 days for guard fixes | Agents run the right thing | In aim / yes / a wrong form loses a run or trips the guard | **One commands table** in `governance/project/facts.yaml`. Every entry is smoke-tested (`--help` or a dry run) in a unit test, and templates refer to commands by name. Long chains become one tool (`lead_verify.sh`) | TPL-2, TPL-3b | E3 (G-2) for the guard side |
| R3-8 | **The return form is good: keep it.** The twelve fields (DEC-793) are enforced for subagents by `subagentstop.py`. `brief_gaps:` (DEC-943) is the best existing measure of whether a brief serves its reader | brief l.172–199; `template/governance/kernel/hooks/subagentstop.py` | 83 returns carry `brief_gaps:`, a median of ~6 lines each (511/83) | Readable returns; a feedback loop | In aim / yes / an unreadable return loses work | **Keep**, plus a `template: <name>@<version>` receipt line. The other sections become fixed short forms (Appendix T-0) | TPL-1, TPL-7 | G-11 (the `guard_refusals` form) |
| R3-9 | **No template version or receipt.** Nobody can tell which text a session followed | — | O: cannot be audited | Drift (aim) | In aim / yes / not fail-open | **Add** a version in each template's front matter. The return quotes it, and a script checks it against what was injected | TPL-7 | TPL-4 |
| R3-10 | **The reviewer brief predates DEC-1010.** `brief-reviewer.md` has no verdict block. `JUDGEMENT.md` is copied "word for word" into each review brief | `templates/brief-reviewer.md`; `briefs/JUDGEMENT.md`; brief l.88, l.126 | T: rev briefs have a median of 13,751 characters (n = 56) | DEC-1010 (stays) | In aim / yes / an unparseable verdict blocks READY | **Rewrite** the QA/reviewer template around the `verdict` block that `verdict.py` reads, with JUDGEMENT's tests as three lines plus a pointer | TPL-1 | DEC-1010 (unchanged) |
| R3-11 | **The hand-over has no fixed form.** The lead's prose `CHECKPOINT.md` is freeform, while the kernel `checkpoint.md` has fields | `templates/checkpoint.md`; brief l.170 | Resumes re-read (R2 owns the count) | Resume (aim 1) | In aim / yes / loses work | **Fix the form**: the state at the top, then next step, open items and where things are, like the live incident document of SRE practice (§A6) | TPL-1 (in T-7, T-8) | R-6/R-7 decisions |
| R3-12 | **The research record template is 236 bytes** and does not name the decision it feeds or its stopping rule | `templates/research.md`; `roles/research.md` | — | Discovery (aim 2) | In aim / yes / an unanchored study loses work | **Extend** (T-2): the question, the decision it feeds, the method, the stop rule, the sources cited, the verdict and a draft KPI line | TPL-1 | — |
| R3-13 | **The CTO's per-ticket parts are freeform.** 850 files in `.gov-runtime/scratch/orchestrator/briefs/` follow no form. `build_lead_brief.py` checks only placeholders and `IMPL` | `.gov-runtime/scratch/orchestrator/tools/build_lead_brief.py` (47 lines) | T: the part is where 119 gap lines were placed | Leads get the ticket's facts | In aim / yes / loses rounds | **A form for the part** inside T-8 (why now, staged decisions, order, probe focus). The generator fills everything else from the ticket | TPL-3 | TPL-2 |
| R3-14 | **Skills grant nothing and are loaded on demand. Keep them for procedures** (how to design a test, run a change, audit), not for paths and commands | `template/governance/kernel/skills/*` (9, 2.0–9.1 KB) | — | Methods (CAP-24.b) | — | **Keep.** Templates name the one or two skills a role loads. A role's subagent definition may preload them (`skills:` field, §A10) | TPL-4 | — |

Outside my part (one line each, for the combiner):
- O1: the readiness checker (`src/gov/readiness/`, 26 rows) is for specifications. It must not become a ticket gate: the ticket's ready check in TPL-5 prints warnings only.
- O2: the scratch tools directory still holds 4 `heavy_slot.sh` backups and 2 `select_tests` copies (O-8).

---

## Evidence for the larger items

**R3-1/R3-2: brief sizes.** `python3 -I /tmp/gov-os-inv-R3/briefsizes.py` over `~/gov-os-worktrees/*/.gov-runtime/scratch/lead/briefs/*.md`:
`n 440 median 12891 p90 20022 max 47889; with standing-rules section 324, median SR chars 4910.5; median SR share 0.35`.
By kind: td 156 (median 13,925), eng 153 (11,404), rev 56 (13,751), ps 13 (7,298). One example: W2-112's 15 briefs total 143,097 characters (`eng-1.md` 20,706; `rev-2.md` 21,614).

**R3-3: delivery.** `launcher.py` l.322: `subprocess.Popen([str(cli), "--settings", json.dumps(settings), *cli_args], …)`. The role reaches the session only as `GOV_ROLE` in the environment, for the guard. A grep for `--agent ` or `--append-system-prompt` in the 440 briefs, the common brief and the CTO prompt finds only W2-60a's three briefs, where these flags are the subject of the work. The CLI reference (§A10) says `--append-system-prompt-file` "load[s] additional system prompt text from a file and append[s] to the default prompt" and that all system-prompt flags "work in both interactive and non-interactive modes". `_check_cli_args` does not refuse it. The repository's CLI is 2.1.316.

**R3-3/R3-14: one source, already checked.** `src/gov/adapters/portability.py` already checks, byte for byte, that the kernel role and skill files, their `.rulesync/` sources and the generated `.claude/` files agree. Templates added as kernel files go through the same path, and that check covers them for free.

**R3-5: tickets.** A script over the 136 `.tickets/*.md` with `wbs_id: W2-*`: median 3,824 characters (max 15,861); success KPI lines median 5 (max 18); median KPI line 224 characters. A regex for `non.goal|out of scope|no-go` finds 2 tickets. Example: W2-61 (`DAEO-iw1f`) has 7 success lines, and each carries its citations inline; none says how to check it.

**Brief gaps.** `python3 -I /tmp/gov-os-inv-R3/gaps.py` reads the last JSON object's `result` in each `.gov-runtime/scratch/orchestrator/log/W2-*.json` and takes the `- … | … | …` lines after `brief_gaps:`:
`returns with brief_gaps 83, gap lines 511, stated minutes (lower bound) 7424`.
By keyword (one line can fall in several categories; a rough classification, not a reading of each line): guard/sandbox 119, path 114, other 110, rebuild/store 101, command form 88, decision reading/contradiction 82, test selection 62, return/record form 62.
Where the leads placed them: common brief 197 (+5 "the common brief", +14 "common brief / tool"), this ticket's part 119, a tool 42, the ticket file 25.

**Guard refusals.** `.gov-runtime/scratch/orchestrator/log/guard-refusals.jsonl` has 87 rows: 79 false-positive, 4 true, 4 unjudged. By reason: 57 "a command that may write the acceptance tests", 10 reviewer write-reads, 10 "names given at run time". A template cannot fix false refusals (E3 does). What it can do is give the command forms that do not trip the guard: write files with the Write tool and absolute paths, and name the folder a listing starts at.

**Contradictions, quoted.** `roles/engineer.md` l.5: "implement one ticket until its acceptance tests pass". DEC-957 in the common brief l.11: the engineer builds "to fulfil the spec and its KPIs, never to make the tests pass: it may run the acceptance tests and see only pass or fail, never read them". `skills/test-design/SKILL.md`: "does not read implementation files, source code, or any path under src/". Appendix A1: "the existing code it must work with, as it stands on the ticket's base (`git show w2/integrate:<path>`)".

---

## A. What good software companies and projects do (sources)

1. **Change descriptions: a short first line, then what and why.** Google's guide asks for a "short, specific summary" first line in the imperative, then a body with the problem, the reason for the approach and its shortcomings, written so it stays understandable after links die. Small changes are "one self-contained change", "100 lines is usually a reasonable size", "1000 lines is usually too large". Sources: https://google.github.io/eng-practices/review/developer/cl-descriptions.html, https://google.github.io/eng-practices/review/developer/small-cls.html
2. **Reviews: a checklist, and severities kept apart.** Reviewers look at design, functionality, complexity ("solve the problem they know needs to be solved now"), tests ("would they fail if the code broke"), naming, comments and docs. A minor point is labelled "Nit:" and "isn't mandatory". Source: https://google.github.io/eng-practices/review/reviewer/looking-for.html. *Mapping:* DEC-1010's in-scope / ordinary-work / consequence triage is the same separation; out-of-scope findings are the nits.
3. **Design notes: goals and non-goals, alternatives, short when the problem is small.** Google design docs: context and scope, goals and non-goals ("explicitly chosen not to be goals"), the design, alternatives considered, cross-cutting concerns. 1–3 pages for a small change, and none when the solution is not ambiguous (https://www.industrialempathy.com/posts/design-docs-at-google/). Rust's RFC template: summary, motivation, guide- and reference-level explanation, drawbacks, rationale and alternatives, prior art, unresolved questions (https://raw.githubusercontent.com/rust-lang/rfcs/master/0000-template.md). Kubernetes KEPs: goals and non-goals, a test plan, graduation criteria, a production-readiness questionnaire (https://github.com/kubernetes/enhancements/blob/master/keps/NNNN-kep-template/README.md). Oxide's RFDs: depth "should match urgency and importance", and the ideation state must be "clear and narrowly defined" (https://rfd.shared.oxide.computer/rfd/0001). Shape Up's pitch: problem, appetite (the time box), solution, rabbit holes, no-gos (https://basecamp.com/shapeup/1.5-chapter-06).
4. **Ready and done, each defined once.** Scrum: the Definition of Done "creates transparency by providing everyone a shared understanding", and items are "ready" when they can be finished within a sprint (https://scrumguides.org/scrum-guide.html). INVEST (Independent, Negotiable, Valuable, Estimable, Small, Testable; Bill Wake, 2003) is the usual readiness test (https://www.agilealliance.org/glossary/invest/). GitLab's definition of done includes tests that pass in CI, and its MR description must list the "steps or setup required to ensure reviewers can view the changes" (https://docs.gitlab.com/development/contributing/merge_request_workflow/). Atlassian: a DoD that crosses a hand-off must cover what the next team needs (https://www.atlassian.com/agile/project-management/definition-of-done).
5. **Acceptance criteria as examples.** Gherkin: Given (a known state), When (an event), Then (an observable outcome, "rather than internal state"); "we recommend 3-5 steps per example" (https://cucumber.io/docs/gherkin/reference/).
6. **Hand-overs and runbooks.** Google SRE: playbooks give "roughly a 3x improvement in MTTR as compared to the strategy of 'winging it'" (https://sre.google/sre-book/introduction/). Incident command is handed over explicitly ("You're now the incident commander, okay?", with "firm acknowledgment"), and the commander keeps "a living incident document" with the key facts at the top (https://sre.google/sre-book/managing-incidents/). Postmortems use fixed fields: summary, impact, root causes, trigger, resolution, detection, action items, lessons, timeline (https://sre.google/sre-book/example-postmortem/; PagerDuty's has a similar form: https://response.pagerduty.com/after/post_mortem_template/).
7. **Templates live in the repository and are applied by the tool.** GitHub applies `.github/pull_request_template.md` automatically, and several templates live under `PULL_REQUEST_TEMPLATE/` (https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository). Issue forms are YAML with `validations: required: true` per field, so required fields are checked by the tool, not by goodwill (https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms). Kubernetes' PR template asks for what the change does and why, related issues, notes for the reviewer, the release note and AI use (https://raw.githubusercontent.com/kubernetes/kubernetes/master/.github/PULL_REQUEST_TEMPLATE.md).
8. **Briefing agents.** Anthropic's multi-agent system: "Each subagent needs an objective, an output format, guidance on the tools and sources to use, and clear task boundaries"; "Without detailed task descriptions, agents duplicate work, leave gaps, or fail to find necessary information" (https://www.anthropic.com/engineering/multi-agent-research-system). Context engineering: "the smallest possible set of high-signal tokens"; the system prompt at "the right altitude"; keep lightweight identifiers (paths) and load just in time; structured notes outside the window; sub-agents return condensed summaries of about 1,000–2,000 tokens (https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
9. **Instruction files: short, consistent, with enforcement in tools.** Claude Code: "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence". "If two instructions contradict each other, Claude may pick one arbitrarily". `/doctor prompt-audit` finds conflicting or outdated instructions (https://code.claude.com/docs/en/memory). Best practices: the most useful line is "the command that runs" the check; "If something has to happen every time, make it a hook, a deny rule, or a managed setting"; "If Claude keeps ignoring a line … adding IMPORTANT probably won't fix it"; and keep the enforced set small (https://code.claude.com/docs/en/best-practices).
10. **Delivery mechanisms in the CLI.** `--append-system-prompt-file` appends a file to the default system prompt and works in `-p` mode. `--agent <name>` makes an agent's body the session's system prompt, replacing the default. An agent file's `skills:` field preloads full skill content (https://code.claude.com/docs/en/cli-reference, https://code.claude.com/docs/en/sub-agents).
11. **Why length and position matter.** Accuracy follows a U-shape: best when the relevant text is at the start or end of the context, worse in the middle (Liu et al., TACL 2024, https://aclanthology.org/2024.tacl-1.9/). With many instructions, even the best frontier models reach only about 68 % at 500 instructions, with a bias towards the earliest ones (IFScale, https://arxiv.org/abs/2507.11538). *Reading for us:* a 56k-character brief with ~40 bullet rules, read once at the start and then pushed into the middle of a 140k–890k context, is the case these papers describe. That is an inference; the 3 % reading figure itself is R2's.

**What carries over (the principles TPL-1 to TPL-8 apply):**
- **P1.** One template per artifact, kept in the repository and applied by the tool (A7).
- **P2.** Stable "how" and per-task "what" are separated. The stable part loads every time; the per-task part is filled in, never hand-copied (A8, A9, A10).
- **P3.** Every brief has an objective, inputs as exact paths, boundaries (non-goals and what not to touch), commands as exact strings that are tested, done (one DoD), and the output form (A3, A4, A8).
- **P4.** Rules with no exceptions are enforced by the guard, the launcher and tools. The template states the command, not the prohibition (A9). This is also DEC-1050 (12)'s root fix: "agents briefed so well … that they do not trip the guard".
- **P5.** Acceptance criteria are examples with an observable check (A5).
- **P6.** Reviews separate blocking from non-blocking findings (A2), which is DEC-1010.
- **P7.** Hand-overs are explicit and keep the state at the top (A6).
- **P8.** Size follows from P2: the prose rules are short (a budget), while the paths and commands tables are complete. The owner's point stands (DEC-1050 (7)): better guidance, not less.

---

## B. The design

**Files.** Each template has a version in its front matter and lives in the kernel. Project facts are separate, so EXAMIN's copy gets the same templates with its own facts.
- `template/governance/kernel/templates/` holds T-0 `brief.md` (the envelope and return form), T-1 `ticket.md`, and T-2 to T-8 (`role-research.md`, `role-product-spec.md`, `role-test-designer.md`, `role-engineer.md`, `role-reviewer.md`, `role-lead.md`, `role-cto.md`). They replace `brief-*.md`, and `checkpoint.md` and `research.md` are folded in.
- `governance/project/facts.yaml` (new, project-owned) holds:
  - `paths:` (main tree, worktree pattern, store tree, scratch, logs, probe folder),
  - `commands:` (named, exact, with `{placeholders}`),
  - `dod:` (six lines),
  - `steps:` (switches for conditional steps, so a lift such as `keyword_warn`, `trailer_gate`, `context_ceiling` or `checkpoint_record` is one config line; the owner's row decisions set them),
  - `budgets:` (sizes).

**Filling.** One generator, `gov brief <role> <ticket> [--part <file>] [--repair <file>]`. It starts in the CTO's tools as an extension of `build_lead_brief.py`, then moves into the product. It reads the ticket's front matter and the facts, fills T-0 with the role's section, and refuses only two things: a placeholder left over, or a KPI line with no `verify`. It prints the ready-check warnings (TPL-5) and the brief's size.

**Delivery, the same for every session:**
- **A launched worker or lead** gets its role template as an appended system prompt (`--append-system-prompt-file <tree>/.claude/templates/<role>.md`, added by `gov launch` and by the dispatcher's lead line) and the generated brief on stdin. CLAUDE.md loads as now.
- **An in-session subagent** gets its role template as the body of `.claude/agents/<role>.md`, generated from the same kernel file by rulesync, with the role's one or two skills in `skills:`.
- **The CTO** gets T-8 as its prompt's operating section. Its prompt is otherwise unchanged (DEC-1050 (10): no cut without evidence).
- **Skills** stay procedures, loaded on demand.
- One source is checked by the existing portability check, byte for byte.

**Ownership (R2-3).** product-spec writes the templates and the facts file; the CTO approves; kernel parts go through CIT-P (CAP-33). A line enters a template only where it changes what a session *does*. It is written as an imperative with the decision id in brackets, and carries no history. A line that holds only "until X" names X's ticket, and the generator refuses it once that ticket is closed. A change is judged by the next lead run's follow-rate counts (M3), not by adding a paragraph. This scopes DEC-851 item 1 and DEC-943 item 1 for templates (an owner amendment).

**Knowing that they are read and followed (measures, never gates; one weekly line in the daily document).** Baselines are R2's unless marked R3.
- **M1 receipt.** The return's `template:` line equals the injected version. This checks delivery.
- **M2 form.** The return parses: the twelve fields plus the T-0 sections (`check_return.py`, shared with `subagentstop.py`'s rule).
- **M3 follow rate per line (the templates' main KPI, R2).** For each step a template names, the share of sessions given that template whose transcript shows the step's command. R2 measured 83 to 100 % for 11 of 14 commands. Read both ways: a low rate means the line fails, and a high rate on a line that guards nothing means it costs work (R2-5). Add the share that succeeded on the first try.
- **M4 gaps by kind.** `brief_gaps` lines per return, counted weekly by kind: 6.7 → 5.1 per return from 30 Oct to 2 Nov. 52 % of the stated minutes (3,824 of 7,424) are machine contention. Those go to the dispatcher's list, not to the template, and are excluded from M4's target. Every other line is closed within a week by a tool, a facts entry or a template line that M3 then measures, or recorded "won't fix" (the gap log).
- **M5 refusals.** The share of sessions with a guard refusal: 68 % → 17 % after the command forms went in. After G-1 the 17 Rule-1 read refusals go too. The target is refusals only where the template gave no working form.
- **M6 doing cost.** Per session, from transcripts:
  - wait-loop calls (24.5 % of calls, median 25 a lead);
  - ceremony calls (11.6 %, median 14);
  - hand-written wrapper scripts (343 in 117 of 159 sessions);
  - harness permission denials (218 in 110 logs);
  - tool calls before the first worker launch (median 24).
  Each should fall once the scripts and the run-kind templates are in.
- **Dropped:** a re-reading measure. R2 found a median of 0 re-reads, so that is not where leads get lost.

Falling M4 (excluding contention), M5 and M6, with M1 to M3 high on lines that pass DEC-1010's test, is the evidence that the templates are read and followed. The minutes of M4 and M6 are the productivity measure the owner asked for (DEC-1050 (10)).

---

## B′. What R2 changed in this design (each traced to R2's row)

| R2 row | R2's evidence | change here |
|---|---|---|
| R2-1, R2-2, R2-16 | The 3 % was the decision list; leads open a median of 2 DECs. `gov retrieve` was run in 19 % of the sessions whose brief named it; the register was reached by `grep` 188 times | No reading list in any template. T-7 step 0 says to ask `gov retrieve` first ("which decision governs X", "where is Y") and to grep the register only by id |
| R2-4, R2-14 | The run's facts sit in the 2.6k part; 95 % of the text is common to every kind of run; the stdin mechanism works | T-7 is a short common head plus **one section per run kind**: `tests`, `build` (implement and verify), `review`, `resume`, `land`. `gov brief lead {ID} --run <kind>` includes only that section. Delivery stays one stdin prompt, with the role head as an appended system prompt |
| R2-5 | Ceremonies are obeyed 83 to 100 %: 2,135 calls, 11.6 % | A step stays only if it passes DEC-1010's test. Tripwire and disk gate go *inside* `launch_worker.sh` and `lead_verify.sh`, not as steps. `keyword_warn`, collect-only, `trailer_gate`, the hooks check and the `du` measures are `steps:` switches the owner's rows set (default per P1). R-4/R-5 stay with the owner: R2's new evidence is that these lines cost work |
| R2-6 | Waits are 24.5 % of calls; 75 `sleep` chains blocked | `wait_for.sh <exit-file> [<max-s>]` (blocks up to 9.5 min, prints the tail and exit code) is the only wait form in every template. The alternative, letting the guard accept `Monitor`, is a CIT-P for the G-rows |
| R2-7 | Working forms cut refusals 68 % → 17 % | T-0 carries a **"forms that work"** block in positive form: the Write tool with absolute paths; a script file under scratch for anything longer than one line; literal paths, never a shell variable as a write target; name the folder a listing starts at |
| R2-8 | 218 harness denials (`rm` 55, `python3` 39) | T-0 lists the commands the harness allows headless, generated from the settings' allow list into `facts.yaml: harness_allowed`, and says what to do with anything else (a script file run by `bash`, or report it). With O-7 (`rm` free except catastrophic deletes) |
| R2-9 | 343 hand-written verification wrappers | `lead_verify.sh`, `launch_worker.sh` and `wait_for.sh` ship in TPL-3b, and the templates name them in one line each |
| R2-10, R2-11 | Leads read Appendix A and the kernel templates, then write 399 briefs; the two lead templates disagree | Worker briefs come from `gov brief <role>` (TPL-3). Appendix A leaves the CTO prompt (TPL-6). The kernel's T-7 is the one lead template, and the project only fills its facts |
| R2-12 | Stale "until X" lines are still obeyed | The generator refuses a line whose "until" names a closed ticket (TPL-3 S6) |
| R2-13 | The gap loop collects but does not close (18 register rows, 2 fixed) | M4 by kind, weekly. Closure is a tool, facts entry or line that M3 then measures. Contention goes to the dispatcher |
| R2-15 | 24 tool calls and 107k characters before the first launch | T-7 gives the lead its first calls: identity, resume check, the ticket file, the 3 to 5 paths or one `gov retrieve` question the part names, then the first launch |

---

## C. Budgets (prose only; the paths and commands tables are not limited)

| template | prose budget | rationale |
|---|---|---|
| T-0 envelope (filled, excluding the KPI lines and the sources list) | ≤ 4,000 characters | one screen of facts; A8, A9 |
| T-2 to T-6 role templates | ≤ 3,500 characters each | under the 200-line CLAUDE.md guidance with room left (A9) |
| T-7 lead | ≤ 8,000 characters | the lead's loop has 8 steps; the 54k of today is mostly history (combined R-1) |
| T-8 CTO operating section | ≤ 6,000 characters | for its session start, briefs and hand-over only |
| T-1 ticket | ≤ 4,000 characters of body | median today 3,824 |

---

## D. Work packages for the refactoring (spec and KPI lines; each line is testable)

**TPL-1 — The kernel template set** (product-spec writes; the CTO approves (R2-3); one CIT-P, CAP-33; one review)
- S1 `template/governance/kernel/templates/` holds T-0 to T-8 as in the Appendix, each with `name`, `version` and `role` front matter. *Verify:* a unit test lists the nine files and parses their front matter.
- S2 The prose of each template (excluding fenced tables of paths and commands) is within §C's budget. *Verify:* the test measures the characters.
- S3 No template restates a rule that DEC-957, DEC-959, DEC-963, DEC-1010 or DEC-1050 superseded. Named checks: the engineer template contains no instruction to read `tests/acceptance/`; the test designer's permits reading code on `w2/integrate`; the reviewer's carries the `verdict` block in DEC-1010's form. *Verify:* string tests on those three facts.
- S4 `brief-engineer.md`, `brief-test-designer.md`, `brief-reviewer.md`, `brief-product-spec.md` and `brief-lead.md` are removed or reduced to a one-line pointer, and `roles/engineer.md` l.5 says "to fulfil the spec and its KPIs". *Verify:* a test.
- S5 Every placeholder in a template is a key the generator knows. *Verify:* a test against TPL-3's key list.
- F1 A template names a path or command that is not in `facts.yaml`. *Verify:* a test fails.

**TPL-2 — The project facts file** (orchestrator, CTO lane; then product-spec for the schema)
- S1 `governance/project/facts.yaml` holds `paths`, `commands`, `dod`, `steps` and `budgets`. It validates against `template/governance/kernel/schemas/facts.schema.json`. *Verify:* a schema test.
- S2 Each `commands` entry has a `check:` form (`--help`, a dry run or a no-op), and a unit test runs every check in a temporary repository and passes. *Verify:* the test (none needs a heavy slot).
- S3 `steps` switches decide which conditional lines appear in a filled brief. Switching one off removes its line and changes nothing else. *Verify:* a generator test with one switch flipped.
- S4 `dod` has at most six lines, and the ticket and lead templates quote it by reference. *Verify:* a test.
- F1 A command form appears in a template text and not in `facts.yaml`. *Verify:* TPL-1 F1.

**TPL-3 — The generator** (engineer; CTO's tools first, product second)
- S1 `gov brief <role> <ticket>` prints a filled T-0 with the role section, given only the ticket file and `facts.yaml`. The output is byte-identical for identical inputs. *Verify:* a golden-file test.
- S2 It exits non-zero naming each leftover placeholder, and each KPI line without `verify`. *Verify:* tests.
- S3 It prints the ready-check warnings (TPL-5 S3) and the filled size against §C. A warning never stops it. *Verify:* tests.
- S4 The lead's hand-written part is limited to "what the lead knows" and "repair input" (`--part`, `--repair`); the standing rules are never in the stdin brief. *Verify:* the generated brief contains no text from the role template.
- S5 (TPL-3b, the scripts, CTO's tools lane; R2-6, R2-9):
  - `lead_verify.sh <tree> <W2> <ID>` runs the selection, the parallel run and the serial phase (only what `gov.close.serial.phase` selects, DEC-1050 T-5) under its heavy slot. It writes the two JUnit files, one summary line and an exit-code file.
  - `launch_worker.sh <role> <effort> <brief>` builds the `gov launch` line, runs the tripwire snapshot and compare, the disk gate and the sandbox step-0 check, and writes the log and an exit file.
  - `wait_for.sh <exit-file> [<max-s>]` blocks for at most 570 s and prints the tail and the exit code.
  - *Verify:* a shell test per script in a temporary repository with a stub suite or a stub CLI.
- S6 The generator refuses a template or part line holding "until <ticket>" when that ticket's status is `closed` (R2-12). *Verify:* a test with a closed fixture ticket.
- S7 `gov brief lead {ID} --run tests|build|review|resume|land` includes only that run kind's section of T-7 (R2-4). *Verify:* one golden file per kind.
- F1 Two runs on the same inputs differ. *Verify:* S1.

**TPL-4 — Delivery** (engineer; the launcher is product code; the dispatcher is the CTO's)
- S1 `gov launch <role> <ticket>` passes `--append-system-prompt-file <root>/.claude/templates/<role>.md` and refuses to start if the file is missing. *Verify:* a launcher unit test on the built argv.
- S2 The dispatcher's lead launch passes the same flag with `role-lead.md`. *Verify:* a test on the dispatcher's built command.
- S3 `.claude/agents/<role>.md` bodies are generated from the kernel role templates by rulesync, with a `skills:` list. `gov.adapters.portability` reports them consistent. *Verify:* the existing portability tests extended by one case.
- S4 `.claude/templates/*.md` are generated copies, checked byte for byte by the same portability check. *Verify:* a test.
- F1 A launched session starts without its role template. *Verify:* S1's refusal case.

**TPL-5 — The ticket template and the ready check** (product-spec; schema change; one review)
- S1 `ticket.schema.json` allows `non_goals: [str]` and a KPI line of the form `{line, verify}` beside the plain-string form, so the old 136 tickets stay valid. *Verify:* schema tests on both forms.
- S2 T-1 (Appendix) is the kernel ticket template; `verify` says the observable check (a command and its expected outcome, or the file and what it shows). *Verify:* the template test.
- S3 The ready check (inside `gov brief`) warns when: there is no `non_goals`; a KPI line has no `verify`; `allowed_paths` is empty; `est_loc` > 400 (Google's small-change guidance, A1: warn and suggest a split); a `depends_on` is not closed. *Verify:* one test per warning.
- F1 The ready check refuses a brief for a warning. *Verify:* a test that it exits 0 with warnings.

**TPL-6 — Retire the contradicting layers** (orchestrator for the project prompt and briefs; product-spec for the kernel skills; one review)
- S1 Appendix A of `governance/project/prompts/w2-orchestrator.md` is a pointer to the templates, under 600 characters. *Verify:* a size test.
- S2 `governance/project/briefs/LEAD-w2-common.md` is replaced by T-7 plus facts; `build_lead_brief.py` is replaced by `gov brief lead`. *Verify:* the file is removed or a pointer, and the CTO's next lead brief comes from `gov brief`.
- S3 `skills/test-design/SKILL.md`'s read restriction matches DEC-963 (reads code on `w2/integrate`, never this ticket's implementation), and `skills/orchestration/SKILL.md` "Briefs" points to the templates. K-4's two lines are fixed in the same CIT-P. *Verify:* string tests.
- S4 `JUDGEMENT.md` becomes a section of T-6. No brief copies it. *Verify:* a test.
- F1 Two template-bearing files state different rules for the same step. *Verify:* `/doctor prompt-audit` (A9), run once by the reviewer, reports no conflict in `.claude/` (a review step, not a gate).

**TPL-7 — Measures** (engineer, the CTO's tools)
- S1 `check_return.py <log.json>` reports per return: the twelve fields present, the `template:` receipt equal to the injected version, and the T-0 sections present. *Verify:* fixture tests on 3 good and 3 bad returns.
- S2 `template_report.py` prints M1 to M6 for a date range from the logs, the transcripts and `guard-refusals.jsonl`. It reads only, needs no heavy slot, and finishes in under 60 s on the current logs. It reuses R2's counters and `/tmp/gov-os-inv-R3/gaps.py`. *Verify:* a fixture test plus one timed run.
- S2a M3 is computed per template line: each named step carries a `match:` pattern in `facts.yaml`, and the report prints one row per line (sessions given it, sessions that ran it, first-try successes). *Verify:* a fixture with one followed step and one skipped.
- S3 The gap log (the existing `governance/project/orchestration/brief-gaps.md`, re-formed) lists every `brief_gaps` line with its kind and its fix (a facts, template or tool commit) or "won't fix" and why. Contention lines are routed to the dispatcher's list. *Verify:* `template_report.py` counts unrouted lines by kind.
- F1 A measure blocks a launch, a close or a landing. *Verify:* none is called from `gov launch`, `gov close` or `land.py` (grep test).

**TPL-8 — The pilot and the comparison** (orchestrator)
- S1 Three tickets of different roles and run kinds run with the new templates (one engineer `build`, one product-spec, one with a FULL `review`), and `template_report.py` reports M1 to M6 against R2's baselines: 5.1 to 6.7 gap lines per return; 68 % → 17 % of sessions with a refusal; 24.5 % wait calls; 11.6 % ceremony calls; 343 wrappers in 117 of 159 sessions; 218 denials; 24 calls before the first launch. *Verify:* the report in the pilot record.
- S2 Pilot target:
  - M1 = 100 % and M2 = 100 %;
  - M3 ≥ 90 % per kept line;
  - M4 ≤ 2 non-contention gap lines per return;
  - M5: refusals only where no working form was given;
  - M6: wait calls ≤ 5 % of calls; wrappers written = 0; harness denials ≤ 1 per session; ≤ 12 calls before the first launch.
  A target missed goes to the gap log and a template, facts or tool fix, never to a new paragraph.
- S3 After the pilot, every new lead and worker brief comes from `gov brief`. *Verify:* M1 over a week.

**Order and dependencies.**
0. Earliest and largest relief (R2-6, R2-9): TPL-3b's three scripts, in the CTO's tools lane. They help today's leads at once, before any template exists.
1. Then TPL-2 (facts) and TPL-1 (templates, in parallel), then TPL-3, then TPL-4.
2. TPL-5 can go beside TPL-3.
3. TPL-6 comes after TPL-4 and the owner's row decisions (they set the `steps` switches).
4. TPL-7 goes beside TPL-3, and TPL-8 comes last.
5. E1 (G-1's landing check) and E3 (G-2) come before the templates drop the "the guard refuses here-documents…" lines.

Estimate (est., from comparable kernel-text and tool tickets in the combined list): TPL-1 ~0.5 day; TPL-2 ~0.5 day; TPL-3 ~1 day; TPL-4 ~0.5 day; TPL-5 ~0.5 day; TPL-6 ~0.5 day; TPL-7 ~0.5 day; TPL-8 ~1 day of pilots. About 4 to 5 working days in all, with parts in parallel.

---

## Appendix — the templates

Placeholders are filled by `gov brief` from the ticket file and `governance/project/facts.yaml`:
- `{ID}` is the tk id, `{W2}` the WBS id, `{PROFILE}` the profile, `{IMPL}` the `Implements:` ids, `{EST}` the estimate.
- `{TREE}` is `/home/usain/gov-os-worktrees/{W2}`, `{TESTS_TREE}` is `{TREE}-tests`, `{MAIN}` is `/home/usain/Dynamic-Agentic-Engineering-OS`, `{TOOLS}` is `{MAIN}/.gov-runtime/scratch/orchestrator/tools`, `{STORE_TREE}` is `/home/usain/gov-os-worktrees/W2-00-store`.
- `{CMD:name}` is a named command from `facts.yaml`, and `{STEP:name}` a line included only when that switch is on.

The command forms below are today's (from the common brief and the tools as they are). `lead_verify.sh`, `launch_worker.sh` and `wait_for.sh` are proposed (TPL-3b). Until they exist, `facts.yaml` maps `{CMD:lead_verify}`, `{CMD:launch_worker}` and `{CMD:wait_for}` to today's three verification commands, the `gov launch` line with the tripwire around it, and the `until [ -s f ]` loop, so the templates do not change when the scripts land.

### T-0 `brief.md` — the envelope every session receives on stdin (generated)

```markdown
---
template: brief@1.0
role: {ROLE}
ticket: {ID} ({W2}), profile {PROFILE}
---
# Your assignment
You are a fresh {ROLE} session. Your role's rules are in your system prompt (template `{ROLE_TEMPLATE}`); this brief gives this assignment's facts.
Objective: {TITLE}. {ONE_PARAGRAPH_FROM_TICKET_BODY}

## Where you work
| what | path |
|---|---|
| your tree (write here only) | {WRITE_TREE} |
| branch | {BRANCH} |
| allowed paths | {PATHS} |
| ticket file (read-only) | {MAIN}/.tickets/{ID}.md |
| your scratch | {WRITE_TREE}/.gov-runtime/scratch/ |

## What must be true (KPI lines and how each is checked)
{KPI_TABLE: | id | line | verify |}
Non-goals (do not build, do not test): {NON_GOALS}
Done when: the DoD lines {DOD_REFS} hold for your part.

## Inputs
- Sources: {SOURCES} (read each in `{MAIN}/docs/DECISION_REGISTER.md`, by id, or ask `gov retrieve`).
- What the lead knows of the ground: {LEAD_NOTE}
{REPAIR: the failing output, verbatim, and nothing else of earlier rounds}

## Commands (copy them as they are)
{COMMANDS_TABLE_FOR_ROLE}
Ask memory first: {CMD:retrieve} "<which decision governs X | where is Y implemented>"; grep the register only by id.
Wait for anything long: {CMD:wait_for} <exit-file> (one call per 9.5 min; never a hand-written sleep loop).

## Forms that work (the guard and the harness accept these)
- Write and edit files with the Write/Edit tools and absolute paths.
- Anything longer than one line goes in a script file under {WRITE_TREE}/.gov-runtime/scratch/ and is run with `bash <file>` or `python3 <file>`.
- Use literal paths, never a shell variable or `$(…)` as a write target. When you list or search, name the folder the listing starts at.
- The harness allows these headless without asking: {HARNESS_ALLOWED}. For anything else, use a script file as above, or report it; never retry another form.

## Return (your last message; nothing else is read)
The twelve fields first, each a labelled line ("none" where nothing):
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then, each section always present:
template: {ROLE_TEMPLATE}@{VERSION}
commits: <hash12> <subject> | Task/Role/Implements as committed
brief_gaps: none | - <what was missing> | <where it belonged: template, facts, ticket, tool> | <minutes, est.>
guard_refusals: none | {STEP:guard_refusal_lines}
Refused twice for the same call: stop and say so. Never work around a refusal: report it.
```

### T-1 `ticket.md` — the ticket (front matter plus a short body)

```markdown
---
id: DAEO-xxxx
wbs_id: W2-nn
title: <the outcome, in one line, imperative>
role: engineer | product-spec | research | independent-auditor
profile: LITE | STANDARD | FULL     # FULL only for memory, the five guard rules, launch/close, the queue, data loss
status: open
depends_on: []                     # tickets that must be closed first
allowed_paths: [src/gov/<area>/**, tests/unit/<area>/**]
est_loc: 120                       # > 400: split (warning)
kpis:
  success:
  - line: <one observable outcome, present tense>     [DEC-n]
    verify: <command and expected result | file and what it shows>
  failure:
  - line: <what must never happen>
    verify: <the case that shows it refused>
non_goals:
- <what this ticket deliberately does not do>
sources: [DEC-n, CAP-n]
acceptance_tests: {path: tests/acceptance/W2-nn/}
---
# W2-nn <title>
**Problem.** Two or three sentences: who is hurt, how, the evidence (a path, a count).
**Approach (if known).** One paragraph; alternatives in one line each, or "none worth a note".
**Rabbit holes.** What to avoid, one line each.
**Card:** docs/plan/WAVE_2_WBS.md §2 (W2-nn). History lives in the register and the close record, not here.
```

### T-2 `role-research.md` — research and discovery

```markdown
---
template: role-research@1.0
role: research
skills: [discovery, retrieval]
---
# You are a research session
You answer one question with evidence so that a decision or a KPI line can be written. You change no product file.
1. Check identity: {CMD:identity} (expect `research`, {ID}). Different: stop and say so.
2. State the question, the decision it feeds and your stop rule (time or evidence) in your record's first lines before any work.
3. Find what the repository already knows first: {CMD:retrieve} "<question>"; then external sources (WebSearch/WebFetch), each cited by URL.
4. Measure from logs and records that exist; if one run is indispensable, run it through {CMD:heavy_slot} once; never a suite.
5. Write only in your experiment folder {PATHS} and scratch. Installs only into a venv inside that folder.
6. Your record ({RECORD_PATH}): question | decision it feeds | method | commands run | measurements (estimates marked "est." with how) | sources | verdict | draft KPI lines (each with `verify`) | residuals.
7. Commit the record: {CMD:commit role=research}.
Never: read secrets, held-out material, or `~/gov-os-workbench`; write outside your folder.
Return: T-0's form; `work_completed` holds the verdict in two lines.
```

### T-3 `role-product-spec.md`

```markdown
---
template: role-product-spec@1.0
role: product-spec
skills: [discovery, change]
---
# You are a product-spec session
You write what the ticket specifies rather than codes: schemas, templates, skills, role files, specifications, KPI lines, docs.
1. Identity: {CMD:identity} (expect `product-spec`, {ID}).
2. Read the ticket, its sources and the files you change; ask {CMD:retrieve} for anything else. Where two sources disagree, the later owner decision holds; name both in `discoveries`.
3. A KPI line you write is one observable outcome with its `verify`; a spec section has goals, non-goals, and alternatives in one line each.
4. A kernel file (template/governance/kernel/**) changes only under the ticket's CIT-P (CAP-33): say which in your commit body.
5. Write only {PATHS}. Run the unit tests your paths have: {CMD:unit_tests}.
6. Commit: {CMD:commit role=product-spec}. A report or assessment is committed alone (DEC-924).
For a specification gap (no ticket paths): write nothing; return a draft answer with sources, options, recommendation and confidence.
Never: write tests/acceptance/**, code under src/, or the ticket files.
```

### T-4 `role-test-designer.md`

```markdown
---
template: role-test-designer@1.0
role: independent-test-designer
skills: [test-design]
---
# You are the independent test designer
You write the ticket's acceptance tests from its KPI lines and sources, before and beside the implementation, and show them red.
1. Identity: {CMD:identity} (expect `independent-test-designer`, {ID}); you work in {TESTS_TREE} only.
2. Read: the ticket, its sources, and the existing code as it stands on the base: `git show w2/integrate:<path>`. Retrieval only from the integration store: {CMD:retrieve_store} "<question>". Never read what this ticket's branch changes (`git diff --name-only w2/integrate...w2/{W2}` names them) other than your own tests.
3. One test per KPI line at least; per profile: LITE one, STANDARD success+failure+key edges, FULL thorough. Each test checks the line's `verify` through a public interface (CLI, file, exit code), never internals. Deterministic, no network; a repository is built in tmp_path.
4. tests/acceptance/{W2}/README.md maps: | KPI id | tests | expected red reason |.
5. Red: {CMD:acceptance_red} — every test fails for the README's reason.
6. Commit only your test paths: {CMD:commit role=independent-test-designer}; a rewrite after an implementer's commit adds `--trailer "Rewrite-Reason: <reason>"`.
An ambiguous KPI line is never guessed: return it in `proposed_decisions` with options, recommendation, confidence.
Never: write outside tests/acceptance/{W2}/ (and earlier tests the KPI lines name); write code the tests judge.
```

### T-5 `role-engineer.md`

```markdown
---
template: role-engineer@1.0
role: engineer
skills: [test-driven-development, systematic-debugging]
---
# You are the engineer
You build the code to fulfil the spec and its KPI lines (DEC-957), never to make the tests pass.
1. Identity: {CMD:identity} (expect `engineer`, {ID}); you work in {TREE} only.
2. Read: the ticket, its sources, the code you touch; ask {CMD:retrieve} "<question>" for the rest. Never read tests/acceptance/{W2}/ by any tool.
3. Test-first on your own unit tests in {UNIT_TEST_PATH}: {CMD:unit_tests}. No code for cases beyond the KPI lines (DEC-135). A refusal KPI must still refuse: never make a guard or gate fail open.
4. Commit your work before any long run: {CMD:commit role=engineer}.
5. When `{TREE}/.gov-runtime/scratch/lead/TESTS-READY` exists, read the acceptance results once: {CMD:accept} — pass/fail per KPI line only.
6. Write files with the Write/Edit tools and absolute paths; run long commands in the background with an exit-code file and wait for it.
A test you think is wrong: report it in `proposed_decisions`; never edit or work around it.
Never: write outside {PATHS} or .gov-runtime/scratch/; install; push, merge, rebase, amend.
```

### T-6 `role-reviewer.md` — QA and review (read-only)

```markdown
---
template: role-reviewer@1.0
role: independent-auditor
skills: [audit]
---
# You are the reviewer (QA): you read everything, you change nothing
You probe the head {HEAD} of {TREE} for behaviour the acceptance tests miss, against the ticket's KPI lines and non-goals.
1. Identity: {CMD:identity}; `git -C {TREE} rev-parse HEAD` equals {HEAD}.
2. Read the ticket, the tests, the code and the lead's results (you re-run nothing the lead ran; run code only to reproduce a finding, in tmp_path).
3. For every finding answer: in scope (the ticket's KPI lines, not its non-goals)? reachable by an honest agent in ordinary work? consequence: fails open | loses work | other? A finding needing a deliberate construction is ordinary_work: no.
4. Look first for: lost work; a role writing outside its scope; an implementer able to change acceptance tests; a guard or gate failing open.
5. Write nothing in any tree. `git -C {TREE} status --porcelain` is empty when you finish.
Return: T-0's form, then the probe record body with this fenced block, one entry per KPI line:
    ```verdict
    {"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
    ```
and each finding as a described behaviour (what was done, what happened, what should have), never as code. Say what you probed and found sound.
```

### T-7 `role-lead.md` — the ticket lead (orchestrator session in one worktree)

```markdown
---
template: role-lead@1.0
role: orchestrator (ticket lead)
skills: [orchestration, checkpoint]
---
# You are the ticket lead for {ID} ({W2})
You run this one ticket's loop to the DoD and return one summary. Headless: only your last message is read. You never merge into w2/integrate, edit .tickets/ or the register, push, or write the acceptance tests.

## Where things are
| what | path |
|---|---|
| your worktree / branch | {TREE} / w2/{W2} |
| tests worktree / branch | {TESTS_TREE} / w2/{W2}-tests |
| your records | {TREE}/.gov-runtime/scratch/lead/ (briefs/, log/, CHECKPOINT.md) |
| integration store (designer's retrieval) | {STORE_TREE} |
| probe records (FULL) | {TREE}/docs/probes/{ID}/ |
| CTO tools | {TOOLS} |

## Your first calls (every run)
0. {CMD:identity} (expect orchestrator, {ID}, {TREE}, w2/{W2}); `test -f {TREE}/.gov-runtime/scratch/lead/CHECKPOINT.md && echo resume`; read `.tickets/{ID}.md`; read the 3 to 5 paths, or ask the one `gov retrieve` question, that the part names. Then start your run's first step. Ask memory, not the register: {CMD:retrieve} "<question>".

## Your run: {RUN_KIND} (only this section is in your brief; the generator picks it with `--run`)
**tests** — the tests only:
1. {CMD:tests_worktree_add}
2. `{CMD:brief} independent-test-designer {ID} > {TREE}/.gov-runtime/scratch/lead/briefs/td-<n>.md`
3. {CMD:launch_worker role=independent-test-designer}, then {CMD:wait_for}
4. Check the return (below); merge the tests ({CMD:merge_tests}); check red ({CMD:red_check}); write TESTS-READY.

**build** — implement and verify:
1. Run *tests* steps 1 to 3 and, in parallel, `{CMD:brief} {IMPL_ROLE} {ID}` with {CMD:launch_worker role={IMPL_ROLE}}. One writer per worktree; never edit while a worker runs.
2. Merge the tests when the implementer is between batches; write TESTS-READY.
3. Verify: {CMD:rebuild}, then {CMD:lead_verify}, then {CMD:wait_for}. No full `gov check` (DEC-1050 T-1). Known reds by name from {FACT:accepted_reds}; a load-sensitive case is re-run alone once.
4. Red: a fresh implementer with the failing output only (`{CMD:brief} {IMPL_ROLE} {ID} --repair <junit>`). Three iterations that don't converge: ESCALATION.

**review** — one review round (FULL; at most two rounds, DEC-1010):
1. `{CMD:brief} independent-auditor {ID} --head <hash>`, launched read-only, then {CMD:wait_for}.
2. Pass: write and commit the probe record under docs/probes/{ID}/.
3. Fail: the triage of every finding goes in your return; a fix starts with a test-design batch given the finding as a described behaviour. Never decide a FAIL away; never a third round.

**resume** — read CHECKPOINT.md; do its NEXT line; then continue in the run kind it names.

**land** — the branch is verified: confirm the head equals the verified head and the tree is clean (`git status --short`), then return DONE with that head. The queue merges and closes; you never merge.

{STEP:keyword_warn} {STEP:trailer_gate} {STEP:context_ceiling} {STEP:checkpoint_record}

## Each worker return
Check the twelve fields (if any are missing, resume the worker once with the missing list), its commits' trailers, and `launch_worker.sh`'s tripwire and sandbox line.
At the end of every run: remove the tests worktree and its branch, if made.

## Hand-over (CHECKPOINT.md, rewritten at every worker return, merge, package, compaction)
STATE: <one line> | HEAD: <hash12> | NEXT: <the next command> | WAITING ON: <none|what>
Workers: <name, session id, status> · Rounds: converged|in progress (no count) · Decisions taken: <line each> · Open packages: <line each> · Paths: <logs, briefs>

## Return
T-0's form, status one of DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED. DONE adds: the verified head; each suite's counts and JUnit paths; the `gov.__file__` line; the reviewer's verdict path; residuals; lines against {EST}. PACKAGES: each as question, options with cost, recommendation, confidence, what it blocks.
Never: run gov close, adopt or pause; amend, rebase, reset; write src/, template/, tests/ or docs/ (except the probe record).
```

### T-8 `role-cto.md` — the CTO's operating section (in its prompt; the rest of its prompt unchanged)

```markdown
---
template: role-cto@1.0
role: orchestrator (main)
skills: [orchestration, planning, change]
---
# Operating card
Start: read RESUME HERE and the decisions-in-force list; the rest on demand ({CMD:retrieve}).
Launch a lead: the ticket is ready (no `gov brief` error; warnings named in the part); write the part (form below); `{CMD:brief} lead {ID} --part <part.md>`; launch with the role-lead template appended.
Part form (≤ 2,000 characters): Why now | Decisions staged for this run (ids, one line each) | Order of this run | Probe focus (FULL) | Known traps (paths, reds).
A return: check_return; route its brief_gaps lines into the gap log (fix facts/template/tool, or won't fix) the same week.
A decision: owner decisions to the register; delegated choices as a line in the ticket's record (pending R-8).
Hand-over (RESUME HERE, at the top): STATE | RUNNING (leads, sessions) | WAITING ON OWNER | NEXT | where things are.
Measure weekly: template_report (M1–M6) one line in the daily document; never a gate.
```

---
*Sources cited inline in §A. Measurements: `/tmp/gov-os-inv-R3/briefsizes.py`, `/tmp/gov-os-inv-R3/gaps.py`, and the shell commands quoted under "Evidence".*
