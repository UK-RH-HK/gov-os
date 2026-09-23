# Trust-architecture prior-art study — common brief for all research agents

**Read this first. Your own dispatch prompt gives you a scope within it.** This file exists so six researchers share one
accurate problem statement instead of six paraphrases of it.

| Field | Value |
|---|---|
| Authorised by | the product owner, 2026-09-23 |
| Nature | **READ-ONLY architecture research and decision support.** Nothing here is implemented. |
| Phase 2 | **STOPPED** throughout. It does not resume on anything you find. |
| Output | one evidence-backed report per agent, feeding a single owner-facing document |

## Absolute constraints — these bind every agent

**Do NOT**: modify product, runtime or kernel code; start a repair round; mint a candidate; change Contract v3 or the
frozen Phase-2 acceptance criteria; activate V8.3; or **implement any architecture you discover**. You are researching,
not building. Write only your own report file.

**Do not make the owner's decision.** Your job is to establish what exists, what it actually guarantees, and what it
costs — so the owner can choose.

## 1. The problem, stated precisely

Governance OS is a governance runtime (Rust) for AI-assisted software engineering. Across R0, R1 and Phase 2 it has
failed **five consecutive times** on the same underlying shape:

```
lower-trust input
      ↓
representation / declaration / configuration
      ↓
Governance OS interprets it
      ↓
higher-trust authority or execution effect
```

> **The recurring defect: the check reasons about a representation, but the actual authority or effect is determined
> somewhere the representation does not cover.**

Each repair correctly fixed the enumeration it was handed — programs, then command shapes, then list-entry premises,
then class values, then *consumers* of a class field, then *obligations* of that field — and left the enumerating
pattern intact. **The pattern, not any particular list, is the defect.**

## 2. The concrete defects — map your findings against these, not against abstractions

These are real, proven, reproduced with filesystem-level effect. Cite them by id.

### Execution binding

| id | What happens |
|---|---|
| **P79-F11** | `env --chdir=decoy sh install.sh`, with `install.sh` correctly hash-pinned. The OS hashed and verified `<root>/install.sh`, declared it readable, installed **ungated** — and the kernel executed `<root>/decoy/install.sh`. **Verified bytes ≠ executed bytes**, on the *conforming* path. |
| **P79-F1** | `env PATH=. true` installs ungated; the kernel executes `<root>/true`, a project file pinned by nothing. The exec inherits the environment, so `PATH` rebinds the program **after** classification. 26 of 26 loader-variable shapes (`LD_PRELOAD`, `LD_AUDIT`, `PYTHONPATH`, `BASH_ENV`, `GIT_SSH_COMMAND`, …) classify as readable. |
| **AR77-F1** | A `file://` URL with an *empty authority* is not recognised as a network endpoint and resolves as an in-project relative path; writes outside the project root, ungated. |
| **AR77-F2** | An absolute path embedded inside a larger token (`curl --write-out '%output{/abs/path}'`) is invisible to path scanning. |
| **AR77-F4** | A **hard link** defeats path-boundary resolution entirely — nothing to canonicalise. |
| **AR68/AR73 family** | ~40 further command shapes: wrapper chains, flag bundles, attached-value inline code, flagless interpreters, stdin interpreters, backslash/forward-slash spelling divergence. |

**The generalisation for execution**: the OS binds *lexical `argv`* while the kernel executes what `argv` **resolves
to**, through an environment and working directory that the same `argv` controls.

### Authority-bearing state

| id | What happens |
|---|---|
| **P79-F8** | A hand edit appending `{pattern: "product/*.py", class: test}` to a project-editable `REPOSITORY_CONTRACT.yaml` **gains no exemption** and is equal on every compared dimension — so it is accepted, applied, **refused by nothing and reported nowhere**. Its effect: it *removes an obligation* (`MATERIAL_CHANGE_REQUIRES_CIT`), letting a task close a change that is otherwise refused. The integrity check models authority **granted**, not obligations **lost**. |
| **AR77-F3** | The same file's `class` field silently conferred exemptions via a *second* consumer the integrity check did not know about. |
| **P79-F10** | **The product has no mechanism anywhere to distinguish a governed contract change from a hand edit.** A targeted search found none. This blocks the obvious fix ("require change control for authority-bearing edits") because nothing can tell the two apart. |
| **R0/R1 era** | An unauthenticated source attempting to establish trusted identity; update/init ingress making currency claims about an unauthenticated source. |

## 3. The research frame — three trust levels

- **Level 1 — trusting Governance OS itself.** Is the runtime being installed and executed the authentic authorised
  version? (Existing direction: a compact TUF-style release root, accepted at R0/R1.)
- **Level 2 — trusting its decisions, state and execution.** **This is the current Phase-2 problem.** 2A governed
  state/authority provenance; 2B execution binding; 2C policy/configuration integrity.
- **Level 3 — higher-assurance / hostile execution.** Isolation architectures, *if and when* stronger guarantees than a
  private owner-controlled machine are needed.

**Do not let Level 3 contaminate Levels 1–2.** Solving an R3 problem inside Phase 2 because the technology exists is a
failure mode, not a win.

## 4. Deployment profile — judge everything against this, not against enterprise defaults

One owner. Owner-controlled machine, **Linux under WSL2** (12 physical cores; no hardware-security assumptions
established). Private repositories. **No public SaaS, no cloud dependency, must work offline.** Not multi-tenant, not
hostile-neighbour.

**Trusted**: the OS, the hardware, the owner, admin privileges where stated.
**Lower-trust**: AI agents and models, project repositories, project-editable configuration, downloaded tools and
plugins, external code.

For every option, classify: **REQUIRED NOW** (private/local integrity) · **USEFUL LATER** (R2 release) ·
**HIGH-ASSURANCE ONLY** (R3/hostile/enterprise).

## 5. Source quality — every important technical claim carries a citation

Prefer, in order: official specifications and standards → official project documentation → source repositories →
peer-reviewed or serious security papers → respected engineering documentation. Blogs only for interpretation.

**State what a technology actually guarantees *and what it explicitly does not*.** A mechanism's advertised property is
frequently not the property we need; say so when that is the case. Popularity is not evidence.

For each candidate record: security property provided · property **not** provided · trust assumptions · maturity ·
maintenance status · licence · platform support · **works locally/offline?** · requires cloud? · requires root? ·
**works in WSL2?** · operational complexity · integration complexity · performance impact · fit for a single-owner
private environment.

## 6. Classify every candidate

- **USE DIRECTLY** — a mature component or protocol becomes part of Governance OS with minimal custom security logic.
- **WRAP / INTEGRATE** — delegate the hard security property to the mature component; Governance OS provides governance
  and orchestration around it.
- **ADAPT THE PATTERN** — the implementation is not reusable but the architecture is established; follow it.
- **BUILD CUSTOM** — genuinely Governance-OS-specific; no existing primitive suffices.

**Be conservative about `BUILD CUSTOM`.** The burden of proof is: *why are we implementing this ourselves instead of
relying on an established primitive?* Five rounds of custom mechanism have just failed; that is the context for this
study.

## 7. What a good result looks like

**Simplification, not accumulation.** The goal is not to assemble every security technology you can find. Actively look
for places where an established primitive lets Governance OS **delete custom code** — for example: a hermetic execution
model that makes the custom command classifier unnecessary; a sealed/authenticated state model that makes "detect a
hand edit" the wrong question entirely; one derived authority source replacing several synchronised enumerations.

Report reductions in: trusted computing base · custom security code · number of authority sources · number of
enumerations · test and proof surface · maintenance burden.

**A smaller architecture is preferable where assurance is equivalent or stronger.**

## 8. Your report

Write to `release/orchestration/phase-2/RESEARCH/<your-agent-file>.md` (your prompt names it). Structure it as you
judge best, but it must contain: the technologies you assessed with the per-candidate record from §5; your
`USE DIRECTLY / WRAP / ADAPT / BUILD CUSTOM` classification with reasoning; explicit mapping to the defect ids in §2;
the `REQUIRED NOW / USEFUL LATER / HIGH-ASSURANCE ONLY` split; simplification opportunities; what you could **not**
determine; and your sources.

Say plainly where evidence is thin. "I could not establish this" is a useful result; a confident claim you cannot cite
is worse than nothing — this project has been burned specifically by confident unsourced reasoning, twice.
