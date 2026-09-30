---
id: CHARTER-v5
status: PROPOSED
supersedes_in_part: [Framework v4.1.2, Adoption Protocol v3.0, Distribution Protocol v1.2]
decisions: [DEC-039, DEC-044, DEC-058, DEC-064, DEC-065, DEC-066, DEC-075, DEC-083, DEC-085]
---

# Governance OS — Charter v5

The Charter says what the Governance OS is for, the rules it never breaks, and how it is run. Contract v4 turns it
into capabilities with one observable acceptance check each. ADR-0001 and ADR-0002 hold the threat model and the
architecture. Charter v5 and Contract v4 replace Framework v4.1.2, the two protocols and Contract v3 as the working
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
- The Gov OS is built in three waves: Wave 1 Integrate, Wave 2 Strengthen, Wave 3 Complete. Each wave ends in an exit
  check and an independent audit.
- It is qualified on two synthetic programmes (DEC-067) and released **once** as Release 1, a signed `v1.0.0` tag.
- Adoption into product repositories starts only after Release 1 (DEC-064).

## 2. Threat model

The Gov OS guards against **mistakes and drift**, not against an adversary running with the owner's privileges. A
process with the owner's OS privileges can defeat any in-process check, so the Gov OS does not try to be a security
boundary against it. Hooks and guards are guardrails that catch mistakes early.

The hard boundary has three parts:
- git history;
- the lefthook pre-push gate (G3) on the owner's machine, with GitHub Actions CI (G4–G5) as a visible advisory result
  on every push;
- the rule that only the owner merges, and only on green.

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
   compile into hooks, `gov check`, lefthook and CI. Agents see a short AGENTS.md (≤ ~1.5k tokens), a compiled
   context packet and terse `gov` output (DEC-003).
4. **Deterministic where it can be, judgement where it must be.**
   - Code resolves authority, closure, hashes and checks.
   - Models do discovery, relevance and planning by following skills.
   - Code checks the models' output (architecture v0.3 §3).
5. **Governance costs little.** Governance tokens are at most 10–15 % of a task's tokens (DEC-004, measured as in
   DEC-086). The context packet is at most ~6k tokens. Packets are delivered as a file path plus a short summary.
6. **Retrieval is complete, not top-k.** A batch size is never an evidence limit. Every answer carries a stopping
   reason from a fixed list, and NOT_FOUND is never proof of absence (DEC-030, DEC-080).
7. **Paths are allowed, not forbidden.** Write guards are default-deny allow-lists. Checks derive their scope from the
   repository, never from a hand-kept list (DEC-041).
8. **Assemble, then glue.** Mature tools do the heavy lifting. The `gov` CLI is thin glue behind the API-0002
   envelope. The owner approves every tool install (DEC-001, DEC-083).
9. **Delete before you wrap.** A surface that keeps producing blocking findings is deleted, narrowed or deferred, not
   defended with more machinery (DEC-044).

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
- **MR-3 Every task carries KPIs, and the builder never writes its own acceptance tests.** Each task states
  measurable success and failure criteria.
  - A **separate, freshly spawned Independent Test Designer** writes the acceptance tests from those KPIs, before
    implementation starts.
  - The implementer cannot edit them: the acceptance-test paths are outside the implementer's allowed paths.
  - Where practical, the test-data author is independent of both.
  - Builder tests are regression evidence only.
- **MR-4 Audit, discovery and impact are distinct functions.** Discovery closes specifications. Impact assessment
  (CIT-P) simulates a change before it happens. Execution (CIT-E) applies it and records the result. Audit
  independently compares the project's actual state with its specification and contract. `gov doctor` checks only
  the installation's own health. None of these substitutes for another.
  - Audit is performed by a fresh, read-only Independent Auditor who did not author what it audits.
  - It runs at every specification milestone and at every wave or release exit, including on the Gov OS's own
    Charter and Contract.
  - The auditor's yardstick is the governing sources **plus** the owner's accepted decisions: a deliberate, recorded
    drop is not a defect.
  - Its findings go to the owner as decision packages, within the loop budget.
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

## 5. Proportionality and the loop budget

**Profiles** (DEC-005, DEC-085). Ceremony scales with impact radius.

| Profile | Radius | Readiness rows required | Independent verification | Retrieval | Human gate |
|---|---|---|---|---|---|
| LITE | R0–R1 | the 10 mandatory rows (§37 rows 1, 2, 4, 5, 6, 9, 16, 23, 24, 25) | independent acceptance tests (MR-3) | code + tests, 1 follow-up round | none beyond MR-6 |
| STANDARD | R2 | mandatory rows + the rows the capability-type table in `readiness-dimensions.yaml` marks | MR-3 | + decisions, graph; ~3 rounds; single-pass synthesis | on contradictions |
| FULL | R3+ | all 26 rows | MR-3 + a fresh independent verifier with a bounded whole-system pack (DEC-042 as amended) | all facets; ~8 rounds, then escalate; hierarchical synthesis | customer gate before CIT-E |

- A row a profile does not require may stay MISSING without blocking.
- There is no defaulted N/A. Every N/A is N/A_WITH_REASON, written by an agent with a non-empty reason.
- **A spine specification always closes at FULL**, whatever the profile of the change that opens it (DEC-085).
- The round counts are placeholders, tuned from telemetry (DEC-035).

**Loop budget** (DEC-044). Any one surface gets at most **two review→repair rounds**. If the second round still finds
a blocking defect, the default disposition is **DELETE, NARROW or DEFER**. Continuing needs an explicit owner
decision, recorded as an ADR. `gov close` counts the rounds. The same limit applies to audits (DEC-070).

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
| 1 | orchestrator · product/specification · independent test designer · engineer · independent auditor |
| 2 | architecture · frontend · backend · database/data · integration/API · DevOps/SRE · security · performance · UX; typed handoffs |
| 3 | research · AI/ML · data author · change controller · memory/knowledge · tooling · release · claims/concurrency |

**Authority.** The owner is L5: the customer and the final authority (MR-6). Agents hold no approval authority.
- A decision becomes ACTIVE only with an approval fact from the owner's git account: an owner commit, a signed tag or
  a PR approval (DEC-046, CAP-21).
- Only the orchestrator may *propose* a tool install. It installs only after the owner approves in chat, and the
  install is recorded in the tool registry. `sudo` stays with the owner (DEC-083).

**The human as customer** (MR-6).
- The questions that matter arrive as decision packages in the active chat: question, why now, options, impact,
  reversibility, cost, recommendation, confidence.
- They are ranked P1–P3 by critical path and irreversibility, and asked at most five at a time.
- A branch that waits on the owner never stops independent branches.
- Every answer is recorded as a decision in git.

**Five distinct functions** (MR-4, DEC-066). None of these substitutes for another:
- `gov doctor`: installation health;
- discovery: the discovery skill plus `gov readiness`;
- impact (CIT-P): an OpenSpec proposal, plus `gov impact` from Wave 2;
- execution (CIT-E): OpenSpec apply/archive plus `gov close`;
- audit: a fresh, read-only Independent Auditor.

**Until Release 1** (DEC-073). An operator console session acts for the owner at the terminal. Each repository has its
own session. The Gov OS's own Wave 1 bootstraps MR-3 with settings deny rules and an operator diff check, then runs
under its own guard (DEC-084).

## 7. Non-goals

| Non-goal | Why | Decision |
|---|---|---|
| Plugin trust boundary: hash-binding, descriptor security, self-attestation prevention (CAP-26) | Defends against a same-privilege adversary | DEC-039, DEC-075 (ADR-0001) |
| Below-floor recovery, break-glass, DEGRADED mode (CAP-60) | Rests on the signed-release-root trust chain, which is not built | DEC-039 (ADR-0001) |
| Full root of trust: TUF metadata, key rotation and revocation, offline envelopes, bootstrap-mode separation (CAP-02 beyond its LITE form) | Same-privilege adversary; the LITE form is SSH-signed tags plus a hash manifest | DEC-027, DEC-074 Q11 |
| In-process authority levels L0–L5, acting-role resolution, sealed human channel (CAP-21 beyond its LITE form) | Same-privilege adversary; approvals come only from the owner's git account | DEC-039, DEC-074 Q11 |
| Automated tool-install gate, argv classification, install-authority envelopes (CAP-25 beyond its LITE form) | Reading argv cannot determine what executes; the owner approves each install | DEC-040 as amended by DEC-083 |
| Separate A2A communication layer and three-layer knowledge fabric (CAP-27 beyond its LITE form) | One owner, one harness at a time; kept as "read commands never mutate" | DEC-074 Q11 |
| Upstream lesson export gate, FCP loop, inbox (Contract v3 Q4) | No upstream loop; lessons stay in `docs/lessons/` | DEC-053 Q7 |
| LLM-extracted knowledge graphs for authority (Graphiti, LightRAG, GraphRAG, Cognee) and BMAD | Non-deterministic and token-heavy | DEC-021 |
| RAGFlow, until its adoption trigger fires | Heavy, and a second truth store; the default is Docling → markdown in git | DEC-020 (CONDITIONAL) |
| beads / beads_rust as the task tracker | Licence rider; superseded by `ticket` | DEC-072, DEC-074 |
| Superpowers subagent-driven-development, plugin install, foreign SessionStart hook | Conflicts with MR-3 and OpenSpec | DEC-074 Q5, DEC-076 |
| Rust kernel replacing the `gov` internals, within Release 1 | Assemble first; the kernel may replace the internals later | DEC-001, DEC-083 |
| The old control panels (V8.x) and 61-prompt plan; CP-1; D-0010/D-0011 plugin and tool-install machinery | Left behind; stage state lives in a committed file | DEC-046, DEC-058 |

## 8. Precedence

1. **Charter v5** (this document);
2. **Contract v4** (`docs/contract/CONTRACT_v4.md`; `contract.yaml` is the same content, machine-readable);
3. **ADRs** (`docs/adr/`);
4. everything else: specifications, tickets, skills, lessons.

- The decision register (`docs/DECISION_REGISTER.md`) records the owner's decisions that these documents carry. Where
  a document conflicts with an ACCEPTED or DONE decision, the decision wins, and the document is corrected by a new
  version.
- Where any of the above conflicts with the originals (Framework v4.1.2, the two protocols, Contract v3), **the ADRs
  supersede the originals** (DEC-053 Q5, DEC-058).
- The originals remain provenance only. They leave the working tree after S1-A closes (DEC-082).
