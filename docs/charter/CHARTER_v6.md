---
id: CHARTER-v6
status: ACCEPTED
supersedes_in_part: [Framework v4.1.2, Adoption Protocol v3.0, Distribution Protocol v1.2]
decisions: [DEC-039, DEC-044, DEC-058, DEC-064, DEC-065, DEC-066, DEC-075, DEC-083, DEC-085, DEC-088, DEC-089, DEC-093, DEC-094, DEC-096, DEC-163, DEC-165, DEC-173]
type: specification
state_class: AUTHORITATIVE
---

# Governance OS — Charter v6

The Charter says what the Governance OS is for, the rules it never breaks, and how it is run. Contract v5 turns it
into capabilities with one observable acceptance check each. ADR-0001 and ADR-0002 hold the threat model and the
architecture. Charter v6 and Contract v5 replace Framework v4.1.2, the two protocols and Contract v3 as the working
texts. The originals are kept unchanged as provenance (DEC-058).

## 1. Purpose and scope

**Purpose.** The Gov OS keeps AI agents accurate, bounded and traceable while they build software for one human
owner (DEC-039). It extends the agents' context and memory. The authoritative memory is the repository: git-tracked
records plus derived indexes that can be rebuilt from git on any machine. It never lives in an agent session or a
vendor account (DEC-057).

**Scope.**
- One Gov OS serves every project type, language and agent harness. Projects differ only in their committed overlay
  configuration (DEC-060).
- Every Contract v3 capability that survives ADR-0001 is in scope. That includes the full 26-dimension readiness
  contract (DEC-064).
- The Gov OS is built in two waves, Wave 1 Integrate and Wave 2 Strengthen, and then released lean (EMERGENCY-2 §8).
  The release is accepted by §8.2 of EMERGENCY-2: the Contract's checks pass, the proving run on the synthetic
  repositories passes, EXAMIN's copy is adopted with memory at 95 % or more end to end on a fresh 80, and one EXAMIN
  feature ticket goes through the flow. After it, the Gov OS changes only from friction with adopted repositories;
  Wave 3 is the list of items built only then.
- The release is pinned and hash-verified, cut and re-pinned by the owner (DEC-1214 L3). No tag is signed until
  friction asks for it.
- EXAMIN runs Wave 0 as direct work: memory built through `gov adopt` and the refactor, no tickets and no later waves
  before the release (EMERGENCY-2 §7). Every other product repository adopts on the release, through `gov adopt`, and
  moves between releases with `gov update`.

## 2. Threat model

The Gov OS guards against **mistakes and drift**, not against an adversary running with the owner's privileges. A
process with the owner's OS privileges can defeat any in-process check, so the Gov OS does not try to be a security
boundary against it. There is no guard, no sandbox, no box and no permission prompt: mistakes are caught and corrected
by the deterministic landing and the transcript scan, not prevented (EMERGENCY-2 §2, DEC-1211).

The hard boundary has four parts:
- git history;
- the owner's own `git push` and release, from his own terminal, with two settings deny lines (`git push` and `sudo`)
  that hold in every permission mode;
- an hourly `git bundle` of each repository, kept outside the tree;
- the lefthook pre-push gate (G3) on the owner's machine, with GitHub Actions CI (G4–G5) as a visible advisory result
  on every push.

The landing merges into integration; only the owner pushes. Agents have full permission in the repository, worktree and
run folder they work in; sessions stay apart by where they start, the folders they are given and their brief.

`main` is not branch-protected (no GitHub Pro); enabling protection later changes no other decision (DEC-075).
Approvals are facts only when they come from the owner's git account. No in-process trust classes, root-of-trust
machinery or install-authority envelopes are built.

Full statement: [ADR-0001](../adr/ADR-0001-threat-model.md) (DEC-039 as amended by DEC-075).

## 3. Principles

1. **Memory and context live in the repository.** Git-tracked files are the only truth. Everything under
   `.gov-runtime/` is derived and rebuildable (`gov rebuild`).
2. **Agnostic.** One release line, with an overlay per project. Adapters are generated for Claude Code and AGENTS.md
   from one source (DEC-060, DEC-074 Q6).
3. **Governance is code, not prose.** Agents never read the originals or this Charter during normal work. Rules
   compile into the landing, the templates, the briefs, the skills, `gov check`, lefthook and CI. Agents see a short
   AGENTS.md (≤ ~1.5k tokens), a brief that carries their retrieval, and terse `gov` output (DEC-003; EMERGENCY-2 §1.2,
   §5.4).
4. **Deterministic where it can be, judgement where it must be.**
   - Code resolves authority, closure, hashes and checks.
   - Models do discovery, relevance and planning by following skills.
   - Code checks the models' output (architecture v0.3 §3).
5. **Governance costs little.** Governance tokens are at most 10–15 % of a task's tokens (DEC-004, measured as in
   DEC-086), reported weekly. There is no context packet and no packet ceiling: `gov context` is retired and the brief
   carries the ticket's retrieval uncut (EMERGENCY-2 §5.4, §10.2; DEC-1214 M1).
6. **Retrieval is complete, not top-k.** A batch size is never an evidence limit. Every answer carries a stopping
   reason from a fixed list, and NOT_FOUND is never proof of absence (DEC-030, DEC-080).
7. **Paths are allowed, not forbidden.** Paths are declared on the ticket and checked at the landing; nothing is refused
   at write time. Checks derive their scope from the repository, never from a hand-kept list (DEC-041).
8. **Assemble, then glue.** Mature tools do the heavy lifting. The `gov` CLI is thin glue behind the API-0002
   envelope. The owner approves every tool install (DEC-001, DEC-083).
9. **Delete before you wrap.** A loop that does not converge in two rounds goes to the owner once, with options: fixed
   differently, narrowed, split, deferred, deleted or continued. It is never defended with more machinery (DEC-044 as
   amended by DEC-096 and DEC-1204).

## 4. Master rules (verbatim from architecture v0.3 §1A)

These rules apply to every session in every Gov OS, including the Gov OS's own development from S1 onward (DEC-065).

- **MR-1 Specification comes first.** Work starts from discovery. Agent sessions and the human (the customer)
  exchange questions and answers until a spine specification, or a feature specification, is **closed**.
  - A specification is closed when its readiness contract (26 dimensions) has every required cell PRESENT, or
    N/A_WITH_REASON, for its profile.
  - A silent N/A is invalid.
- **MR-2 Closed specifications generate the work.** A closed specification produces the WBS: tasks, dependencies,
  order and roles. Readiness gaps generate tasks of their own (discovery, data, research, test design). No
  production code task becomes READY until its specification's required cells are satisfied.
- **MR-3 Every feature carries KPIs, and the builder never writes its own acceptance tests.** Each feature ticket states
  measurable success and failure criteria.
  - A **separate, freshly spawned Independent Test Designer** writes the acceptance tests from those KPIs, before
    implementation starts.
  - The landing refuses an acceptance-test change that the test designer did not author (EMERGENCY-2 §4.3).
  - Where practical, the test-data author is independent of both.
  - Builder tests are regression evidence only.
- **MR-4 Audit, discovery and impact are distinct functions.** Discovery closes specifications. Impact assessment
  (CIT-P) simulates a change before it happens. Execution (CIT-E) applies it and records the result. Audit
  independently compares the project's actual state with its specification and contract. `gov doctor` checks only
  the installation's own health. None of these substitutes for another.
  - Audit is performed by a fresh, read-only Independent Auditor who did not author what it audits.
  - A fresh auditor runs at the release acceptance and at adoption stages A5, AS, A7 and A10. Otherwise a review
    happens only for a red test, a failed landing or merge, or a feature that does not work as intended, batched when
    several come together (EMERGENCY-2 §3.4, §3.6; DEC-1214 G6).
  - The auditor's yardstick is the governing sources **plus** the owner's accepted decisions: a deliberate, recorded
    drop is not a defect.
  - Its contested and owner-level findings go to the owner as decision packages, within the loop budget.
- **MR-5 The Gov OS works as a software company.** Work is done by role agents: orchestrator, product/specification,
  research, architecture, UX, frontend, backend, database/data, integration/API, AI/ML, DevOps/SRE, security,
  performance, data author, independent test designer, test execution, integration, change controller,
  memory/knowledge, tooling, independent auditor, release. Each role is a capability contract with a scope, tools, a
  model tier and an authority level. Models are replaceable workers, never holders of project memory.
- **MR-6 The human is the customer and final authority (L5).** The questions that matter reach the human:
  specification, features, security, privacy, hosting, cost, irreversible choices.
  - Each arrives as a decision package in the active chat: question, why now, options, impact, reversibility,
    cost, recommendation, confidence.
  - Questions are ranked by critical path and irreversibility, and low-priority ones are batched.
  - A branch waiting on the human does not stop independent branches.
  - Answers are recorded as decisions in git.

## 5. Proportionality and the loop policy

**Work classes and profiles** (DEC-005, DEC-085; EMERGENCY-2 §4). Work is a feature, a fix or a chore. A feature is a
ticket with a spec and KPIs. A known bug is a fix, recorded in its owning ticket, with the failing test first when no
test caught it. A chore (records, docs, configuration, a tidy-up with the tests unchanged) is a direct commit, listed
in the digest. The measured rubric sets model, effort and checks; the profiles below stay until it replaces them, and
ceremony scales with impact radius.

| Profile | Radius | Readiness rows required | Independent verification | Retrieval | Human gate |
|---|---|---|---|---|---|
| LITE | R0–R1 | the 10 mandatory rows (§37 rows 1, 2, 4, 5, 6, 9, 16, 23, 24, 25) | independent acceptance tests (MR-3) | code + tests, 1 follow-up round | none beyond MR-6 |
| STANDARD | R2 | mandatory rows + the rows the capability-type table in `readiness-dimensions.yaml` marks | MR-3 | + decisions, graph; ~3 rounds; single-pass synthesis | on contradictions |
| FULL | R3+ | all 26 rows | MR-3; no verifier for green work (EMERGENCY-2 §3.4) | all facets; ~8 rounds, then escalate; hierarchical synthesis | customer gate before CIT-E |

- A row a profile does not require may stay MISSING without blocking.
- There is no defaulted N/A. Every N/A is N/A_WITH_REASON, written by an agent with a non-empty reason.
- **A spine specification always closes at FULL**, whatever the profile of the change that opens it (DEC-085).
- The round counts are placeholders, tuned from telemetry (DEC-035).

**Loop policy** (DEC-1204, amending DEC-096, DEC-044, DEC-070 and DEC-082). This applies to every loop that runs until
convergence: review→repair, audit→repair, test→fix and verification.
- The loop runs **at most two rounds**.
- A second round that does not converge produces one **escalation package** for the owner, with options. It gives:
  - each round's outcome;
  - why the loop is not converging;
  - the options: fix differently, narrow, split, defer, delete, or continue.
- The owner decides once. READY is computed by code.
- The orchestrator or `gov` holds the round count and the budget. **They are never disclosed to the sessions inside
  the loop.**
- Retrieval stopping rules are a separate thing and are unchanged (DEC-034, DEC-080).

## 6. Operating model

**The company** (MR-5, DEC-066). Work is done by role agents. Each role is a subagent definition generated by rulesync
from kernel role files plus the project roster. It carries:
- a purpose;
- an allowed-path pattern;
- its tools;
- a model tier;
- an authority level;
- a handoff format.

| Wave | Roles |
|---|---|
| 1 | orchestrator · product/specification · independent test designer · engineer · independent auditor · research, in a minimal form (DEC-163) |
| 2 | architecture · frontend · backend · database/data · integration/API · test execution · integration · DevOps/SRE · security · performance · UX; typed handoffs (DEC-094) |
| 3 | research, with the full research lifecycle · AI/ML · data author · change controller · memory/knowledge · tooling · release · claims/concurrency |

**Authority.** The owner is L5: the customer and the final authority (MR-6). Agents hold no approval authority.
- A decision becomes ACTIVE only with an approval fact from the owner's git account: an owner commit, a signed tag or
  a PR approval (DEC-046, CAP-21).
- Only the orchestrator installs tools, and only after the owner approves a decision package in chat. The install is
  recorded in the tool registry. Install commands are `ask` for the orchestrator, also in Auto mode, and denied for
  every other role, except the research role, inside its experiment folder (DEC-163). `sudo` stays with the owner (DEC-083, DEC-095).

**The human as customer** (MR-6).
- The questions that matter arrive as decision packages in the active chat: question, why now, options, impact,
  reversibility, cost, recommendation, confidence. The template also carries current state and exact permitted next
  actions (Framework §52).
- They are ranked P1–P3 by critical path and irreversibility, and asked at most five at a time. A P1 package may
  bypass the cap (DEC-093).
- A branch that waits on the owner never stops independent branches.
- Every answer is recorded as a decision in git.

**Five distinct functions** (MR-4, DEC-066). None of these substitutes for another:
- `gov doctor`: installation health;
- discovery: the discovery skill plus `gov readiness`;
- impact (CIT-P): an OpenSpec proposal, plus `gov impact` from Wave 2;
- execution (CIT-E): OpenSpec apply/archive plus `gov close`;
- audit: a fresh, read-only Independent Auditor. It runs (DEC-1214 G6):
  - at the release acceptance;
  - at adoption stages A5, AS, A7 and A10.

  Otherwise a review happens only for a red test, a failed landing or merge, or a feature that does not work as
  intended. Contested and owner-level findings come to the owner as decision packages; a fix is recorded in the
  owning ticket, never a ticket of its own.

Readiness gaps generate linked tickets from Wave 1 (DEC-089).

**The owner's operator.** The owner's operator is his own interactive session, with full permission across WSL. The
operator agent, its cron launcher and its lock are retired with the ACT pipeline; there is no guard (EMERGENCY-2 §2.6,
§2.10).

## 7. Non-goals

| Non-goal | Why | Decision |
|---|---|---|
| A write guard, an OS sandbox, a box, permission prompts and permission editing (CAP-58, CAP-61, CAP-62) | Prevention by permission failed the owner's aim: it cost more than the mistakes it stopped; the landing catches and corrects | DEC-1211 (EMERGENCY-2 §2.2) |
| The ACT pipeline, the class rules, the approved lists and the operator agent | A two-line change went through a full decision loop | DEC-1211 (EMERGENCY-2 §2.10) |
| Plugin trust boundary: hash-binding, descriptor security, self-attestation prevention (CAP-26) | Defends against a same-privilege adversary | DEC-039, DEC-075 (ADR-0001) |
| Below-floor recovery, break-glass, DEGRADED mode (CAP-60) | Rests on the signed-release-root trust chain, which is not built | DEC-039 (ADR-0001) |
| Full root of trust: TUF metadata, key rotation and revocation, offline envelopes, bootstrap-mode separation (CAP-02 beyond its LITE form) | Same-privilege adversary; the LITE form is a pinned, hash-verified release with its manifest, and no signing until friction asks | DEC-1214 L3 (DEC-027 superseded), DEC-074 Q11 |
| In-process authority levels L0–L5, acting-role resolution, sealed human channel (CAP-21 beyond its LITE form) | Same-privilege adversary; approvals come only from the owner's git account | DEC-039, DEC-074 Q11 |
| Automated tool-install gate, argv classification, install-authority envelopes (CAP-25 beyond its LITE form) | Reading argv cannot determine what executes; the owner approves each install | DEC-040 as amended by DEC-083 |
| Separate A2A communication layer and three-layer knowledge fabric (CAP-27 beyond its LITE form) | One owner, one harness at a time; kept as "read commands never mutate". Minimal per-session inbox files inside the run-time tool are in scope (RT-6) | DEC-074 Q11; EMERGENCY-2 §6.3 |
| The full upstream lesson export gate and FCP loop (Contract v3 Q4) | Lessons stay in `docs/lessons/`. Only a lite loop for framework lessons is built, in Wave 3: a lesson packet with no product code, data or secrets goes to a shared inbox (CAP-41) | DEC-053 Q7, reversed for framework lessons only by DEC-165 |
| LLM-extracted knowledge graphs for authority (Graphiti, LightRAG, GraphRAG, Cognee) and BMAD | Non-deterministic and token-heavy | DEC-021 |
| RAGFlow, until its adoption trigger fires | Heavy, and a second truth store; the default is Docling → markdown in git | DEC-020 (CONDITIONAL) |
| beads / beads_rust as the task tracker | Licence rider; superseded by `ticket` | DEC-072, DEC-074 |
| Superpowers subagent-driven-development, plugin install, foreign SessionStart hook | Conflicts with MR-3 and OpenSpec | DEC-074 Q5, DEC-076 |
| Rust kernel replacing the `gov` internals, within Release 1 | Assemble first; the kernel may replace the internals later | DEC-001, DEC-083 |
| The old control panels (V8.x) and 61-prompt plan; CP-1; D-0010/D-0011 plugin and tool-install machinery | Left behind; stage state lives in a committed file | DEC-046, DEC-058 |

## 8. Precedence

1. **Charter v6** (this document);
2. **Contract v5** (`docs/contract/CONTRACT_v5.md`; `contract.yaml` is the same content, machine-readable);
3. **ADRs** (`docs/adr/`);
4. everything else: specifications, tickets, skills, lessons.

- The decision register (`docs/DECISION_REGISTER.md`) records the owner's decisions that these documents carry. Where
  a document conflicts with an ACCEPTED or DONE decision, the decision wins, and the document is corrected by a new
  version.
- Where any of the above conflicts with the originals (Framework v4.1.2, the two protocols, Contract v3), **the ADRs
  supersede the originals** (DEC-053 Q5, DEC-058).
- The originals remain provenance only. They leave the working tree after S1-A closes (DEC-082).
