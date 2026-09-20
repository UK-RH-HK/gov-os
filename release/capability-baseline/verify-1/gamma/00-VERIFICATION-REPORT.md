# P2-AR-0048 — Governance OS Phase 2, verification iteration 1: family `gamma`

| Field | Value |
|---|---|
| Run | **P2-AR-0048** (fresh, independent capability-family verifier) |
| Family | `gamma` — E1–E4, F1–F5, G1–G2, H1–H4, I1–I4 (19 capabilities, 167 checklist bullets) |
| Candidate | `cap2-candidate-1`, commit `0bad524d836f179964ffbac31972856ea6434682` |
| Worktree HEAD | `8588813ec1ef9c832879e258ca5acfb573ae996f` (same product code and governed state as the tag) |
| Verdict | **FAMILY_VERIFICATION_COMPLETE** |
| Blocking findings | 3 (V1-F4-01 MATERIALLY_NEW, V1-F3-01 RESIDUAL BC-P2-41, V1-F4-02 RESIDUAL BC-P2-45) |
| Acceptance criteria left unmet by gamma's scope | **AC-4**, **AC-3** |

I authored none of the Governance OS implementation, none of its tests, none of the iteration-0 audits, none of the
repairs and no Phase-1 role. I did not read another iteration-1 verifier's evidence or branch, any agent transcript,
any task-output store or user auto-memory. I modified no product source. I do not issue the Phase-2 verdict.

---

## 1. Pinned inputs — all verified

| Input | Expected | Observed | Result |
|---|---|---|---|
| `product_identity.py HEAD` → `product_code_digest` | `e6332fc7…2220` | `e6332fc7d5af5c73adbe0f200003db30fe5a6fd0b7f24d047d3e340e6f972220` | match |
| `product_identity.py HEAD` → `governed_state_digest` | `3d2aeba2…20c0` | `3d2aeba2fc3b52a95c369c49a854bb9d443b0b03da1180db5339f01d892620c0` | match |
| `git rev-list -n1 cap2-candidate-1` | `0bad524…` | `0bad524d836f179964ffbac31972856ea6434682` | match |
| Contract v3 SHA-256 | `4c2df291…5ed3` | `4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3` | match |
| Frozen Phase-2 gate contract SHA-256 | `d2f33e89…f25e` | `d2f33e89d5459dd809e17271e46854cc886ed958ca63f89765e16d6a26a9f25e` | match |

No STOP condition. The audit universe was established from the owner source itself (Contract v3 lines 360–456 and
458–590), not from the compiled YAML or the evidence map.

## 2. Method

**Everything below is a fresh judgement on this candidate.** No iteration-0 status was carried forward.

* **Held-out tests I wrote** (`heldout/`, 11 probes + `RUN-ALL`): written from Contract v3 and the product's
  observable behaviour, never copied from builder tests or builder probes, and never added to the product tree.
  Each drives `target/release/gov` against a disposable project on an **isolated simulated machine**
  (`XDG_STATE_HOME` per project), so no probe touches the real machine's governance state.
* **A provisioned machine.** Most of gamma's load-bearing behaviour (gate answers, elevated installs, plugin
  registration) only exists on a machine with an authenticated human channel, which P2-ADJ-0001 ties to a
  provisioned Signed Release Root. I therefore wrote my own owner-side signer (`heldout/ownersign.py`, Ed25519 over
  the `signed` member's exact bytes) and release publisher (`heldout/publish_release.py`, which reproduces the
  product's own payload measurement — it recomputed the pinned `payload_hash` `348e1922…67bb5` exactly). Every
  probe provisions a throw-away root, re-verifies the installed kernel against a signed release of that same
  payload, and answers gates with an owner signature the `gov` binary cannot produce.
* **Builder claims are claims — and I did not rest on any.** I did not read the repair or integration reports under
  `release/capability-baseline/repair-1/**` at all. I read the owner source, the frozen gate contract, the owner
  decisions and adjudications, the iteration-0 blocker-class inventory and the gamma audit of record (both required
  for the disposition), and then the product's own source and policies. Every status below rests on something I ran.
* **Regression (O3).** `cargo test --lib` in this worktree: **276 passed, 0 failed**
  (`evidence/regression-cargo-test-lib.out`). I started `cargo test --test certification` and stopped it — see §12.

**Suite result:** `heldout/RUN-ALL` on a clean lab. Every FAIL is a recorded observation of the candidate's
behaviour that falsifies a contract bullet or an OD-P2-03 requirement, **not a harness error**; each maps to a
finding below. The per-probe results, which the final full run reproduces, are:

| Probe | Result |
|---|---|
| `E1-E2-authority.sh` | 14 passed, 0 failed |
| `E3-E4-handoff-claims.sh` | 16 passed, 0 failed |
| `F1-F2-F5-skills-tools-layers.sh` | 18 passed, 6 failed |
| `F3-F4-tool-install-gate.sh` | 16 passed, 5 failed |
| `F4-plugin-boundary.sh` | 12 passed, 0 failed |
| `G1-G2-I1-I4-command-work.sh` | 43 passed, 1 failed |
| `H1-H4-spec-readiness.sh` | 23 passed, 0 failed |
| `FRESHNESS-invalidation.sh` | 15 passed, 0 failed |
| `OD-P2-01-human-approval.sh` | 17 passed, 0 failed |
| `PRIOR-FINDINGS-recheck.sh` | 9 passed, 3 failed |
| `V1-F4-01-executed-proof.sh` | 1 passed, 2 failed |

**Total: 184 passed, 17 failed.** Each probe was run individually and captured in `evidence/<probe>.out`; those are
the authoritative records. I also started an aggregate run through `heldout/RUN-ALL` and **stopped it part-way**:
the machine was running several other verifiers' certification suites at load ~126 and each `gov` invocation was
taking minutes. `evidence/RUN-ALL.out` therefore holds the first five probes — whose lines reproduce the table above
exactly — plus a note recording why it stops there and the totals from the individual runs. `heldout/RUN-ALL`
re-runs all eleven on an unloaded machine.

## 3. Per-capability status

| Cap | Title | Status | Bullets met | Findings |
|---|---|---|---|---|
| E1 | Authority levels | **PRESENT_AND_SUBSTANTIAL** | 4/4 | — |
| E2 | Representative roles | PARTIAL | 6/7 | V1-E2-01 |
| E3 | Typed A2A handoffs | **PRESENT_AND_SUBSTANTIAL** | 8/8 | V1-E3-01, V1-F5-02 (non-bullet) |
| E4 | Concurrency/task claims | **PRESENT_AND_SUBSTANTIAL** | 5/5 | — |
| F1 | Skill lifecycle | PARTIAL | 3/4 | V1-F1-01, V1-F1-02 |
| F2 | Tool Capability Registry | PARTIAL | 6/8 | V1-F2-01, V1-F2-02 |
| F3 | Missing-tool acquisition | PARTIAL | 8/9 | **V1-F3-01**, **V1-F4-01** |
| F4 | Plugin trust boundary `[POST-VERIFICATION HARDENING]` | PARTIAL | 4/6 | **V1-F4-01**, **V1-F4-02**, **V1-F3-01** |
| F5 | MCP/A2A/tool separation | PARTIAL | 3/4 | V1-F5-01, V1-F5-02 |
| G1 | Natural-language intent | PARTIAL | 2/3 | V1-G1-01 |
| G2 | Small explicit human control set | **PRESENT_AND_SUBSTANTIAL** | 5/5 | — |
| H1 | SPEC lineage | **PRESENT_AND_SUBSTANTIAL** | 17/17 | — |
| H2 | 26-dimension Readiness Contract | **PRESENT_AND_SUBSTANTIAL** | 32/32 | — |
| H3 | Readiness generates work | **PRESENT_AND_SUBSTANTIAL** | 5/5 | — |
| H4 | Scenarios drive data/tests | **PRESENT_AND_SUBSTANTIAL** | 3/3 | V1-H4-01 (residual risk) |
| I1 | Unified task DAG | **PRESENT_AND_SUBSTANTIAL** | 22/22 | — |
| I2 | Task contract | **PRESENT_AND_SUBSTANTIAL** | 9/9 | — |
| I3 | Dynamic generation | **PRESENT_AND_SUBSTANTIAL** | 11/11 | — |
| I4 | Parallel execution | **PRESENT_AND_SUBSTANTIAL** | 5/5 | — |

**12 PRESENT_AND_SUBSTANTIAL, 7 PARTIAL, 0 ABSENT, 0 UNCLEAR, 0 N/A** at capability level. At bullet level:
**158 of 167 PRESENT_AND_SUBSTANTIAL, 7 PARTIAL, 2 ABSENT** (E2 "project-specific roles through governed
extension" and F1 "Lessons can propose skill updates through governed promotion" — both absent as bullets, but
neither makes its CAPABILITY absent, since the rest of each capability's bullets are met). No *capability* is
`ABSENT` or `UNCLEAR`, so **AC-2 holds for gamma**. Every `PARTIAL` carries an argued
AC-3 statement in `capability-audit.yaml`; two of them (F3, F4) are argued `COULD_UNDERMINE`, so **AC-3 fails for
gamma**, and F4 is the `POST_VERIFICATION_HARDENING` capability AC-4 names, so **AC-4 fails**.

## 4. Blocking findings

### V1-F4-01 — an interpreter-wrapped install command evades every authority-expansion trigger (**MATERIALLY_NEW**)

`tools::installation_authority` derives what an installation would hold by scanning each *argv element* of
`install_command` / `uninstall_command` / `health_check.command` literally. Wrapping the same effects in one string
argument hides them. With tool id, version, licence, pin, reversibility and the governed security review all
unchanged, each of

```
["sh","-c","sudo apt-get install -y x"]      ["bash","-lc","cp /etc/shadow ./x"]
["python3","-c","import os;os.system('sudo id')"]        ["make","install"]
```

is recorded `expands_authority: false`, `triggers_fired: []`, `undetermined: []`, branch `not_gated`, and installs
with **no Human Gate**.

This is not theoretical, and **`--execute` is not the boundary**:

* with `--execute`, a descriptor whose install command was `["sh","-c","printf … > <absolute path outside the
  project root>"]` installed on the non-gated branch and **its command ran**, writing that file;
* **without `--execute`**, the same wrapping in `health_check.command` — which runs on *every* installation — wrote
  outside the project root just the same.

Both are "broader filesystem or project access", an OD-P2-03 trigger, ungated. The absolute path is invisible to the
scan because `leaves_project` asks whether the *token* starts with `/`, and the token here is the whole shell
string.

The function's own documentation states the opposite rule — *"Anything that cannot be evaluated … a command the OS
cannot read — is an expansion and gates"* — but the implementation records `undetermined` only when the descriptor
carries no command at all (`runtime/src/tools.rs:974-977`). OD-P2-03 requirement 3 says the same thing normatively.

I label this **materially new** and say why plainly: the capability (F4/F3) is inventoried, but the mechanism is not.
BC-P2-39's mechanism was *"elevation decided by the descriptor's own declarations"*; this candidate deliberately no
longer does that. `installation_authority`, `change_decision`, OD-P2-03 and `CHANGE_POLICY.change_classes.tool_installation`
did not exist at iteration 0, so no inventoried class describes a defeated OS-side derivation. It is **adjacent** to
BC-P2-39 and I record that adjacency rather than claiming distance from it.

### V1-F3-01 — the governed security review is not bound to the installation it authorises (**RESIDUAL, BC-P2-41**)

`review_verdict` requires a T2-verified ACTIVE report closing a `security`-class task, written by neither the
installing session nor the installing role, naming this tool id and version with verdict `passed`. It never compares
the review with the installation subject (the SHA-256 over the descriptor as given) that is actually written. One
review of `TL-JQ 1.7.1` satisfied `licence_and_security_satisfied` for **six different descriptors with six different
install commands**; the last, whose command was replaced *after* the review, installed on the non-gated branch and
executed.

This is BC-P2-41 incompletely fixed: *"a tool's security review is satisfied by naming any existing record"* became
"by naming a governed review of this id and version", which is a real repair, but not the binding OD-P2-03
requirement 3 itself names (*"not bound to this exact installation (BC-P2-41)"*). It matters more under OD-P2-03 than
before, because the independent review is now what carries everything the OS cannot observe about a non-gated
installation — so V1-F3-01 and V1-F4-01 compound: the OS's own derivation can be evaded, and the human evidence that
was supposed to catch what it misses is about a different artefact.

### V1-F4-02 — the authorised side of the envelope is an unprotected project overlay file (**RESIDUAL, BC-P2-45**)

OD-P2-03 requirement 2 says the authorised envelope is *"computed from trusted OS state"*. `tools::role_permissions`
reads `governance/project/TOOL_PERMISSIONS.yaml` straight from `p.overlay()`. That file is an ordinary repository
file: not OS-written, no T2 seal, and — unlike `PROJECT_POLICY.yaml` and `MODEL_ROUTING_OVERRIDES.yaml` — not
evaluated through `policy_precedence::evaluate_overlay`; POLICY_PRECEDENCE declares no rule for it. Appending one
permission class to the acting role, **with no `gov` command, no change transaction and no gate**, turned the same
installation from `expands_authority: true, triggers_fired: [privilege_escalation]` into `expands_authority: false`.
`gov audit` afterwards reported nothing about it. The same exposure covers the other overlay documents OD-P2-03
names as envelope sources: `REPOSITORY_CONTRACT.yaml` decides "broader filesystem access" and `DATA_SENSITIVITY.yaml`
decides "new secret access".

This is BC-P2-45's mechanism — *project overlay files read directly, bypassing POLICY_PRECEDENCE, neither refused nor
reported* — still open for the overlay documents the round-3 repair did not cover, and now load-bearing for a
security decision. The capability set differs from BC-P2-45's (F4/F3/E1 rather than A1/M1/M2/M3/H3) but the mechanism
is the inventoried one, so I label it **residual**, not materially new.

## 5. My assessment of the OD-P2-03 implementation

**I do not re-open the owner's decision.** I attacked its implementation, on all three axes the dispatch named.

**What holds, and holds well.** The decision is implemented as an explicit, governed rule — `CHANGE_POLICY.change_classes.tool_installation`
names the owner decision (OD-P2-03), the governed record (D-0011), the manifest operation, the subject paths, each
non-gated condition mapped to the `TOOL_POLICY.auto_install_conditions` entry that decides it, the six
authority-expansion triggers and the envelope sources — visible to policy inspection, not implicit in code
(requirement 1). The descriptor is written **only** by its change transaction's execution — I saw that: a schema
failure inside CIT-E rolled the whole installation back, restoring the generated registry. The branch is also
re-derived at the instant of the write, from trusted state as it stands *then*, so a transaction pre-authorised when
simulated cannot slip through if the envelope has since narrowed (`apply_installation`, `runtime/src/tools.rs:1517-1530`);
that one I established by reading the code, not by narrowing an envelope between simulate and execute. Every installation is recorded either way,
and the installed descriptor carries the decision, the rule, the branch, why, the bound review and the change
transaction, so an auditor can trace any installed tool to what allowed it (requirements 4 and 5). Round-3 behaviour
is restored: a non-elevated, reviewed, pinned, reversible installation inside the envelope proceeds **with no gate**
(requirement 6). Both branches are exercised: I saw a non-gated install complete, and eleven distinct
authority-expansion cases each raise a Human Decision Gate — a permission class the role does not hold, a
host-authority class, a credential class, `sudo`, `apt-get`, `--global`, a path outside the project, a declared
policy mutation, an unallowlisted endpoint, a declared credential scope, and a credential name in an argument
(requirement 7). Ordinary use of an approved registry, by a role holding a network class, does **not** gate, exactly
as the owner said. And the gated branch really closes: after the owner answered both gates through the authenticated
human channel, the same install completed without raising a new gate — the BC-P2-41 dead end is gone.

**Where it does not hold.** On the dispatch's three questions:

1. *Is the envelope truly computed from trusted state rather than the descriptor's own claims?* **Partly.** The
   demanded side is genuinely OS-derived and a descriptor can only ever add to it — that is a real advance over
   BC-P2-39. But the **authorised** side is read from unprotected project overlay files, so the comparison can be won
   by editing one of them (V1-F4-02). The descriptor no longer authorises itself; the repository still can.
2. *Is every expansion route detected?* **No.** The derivation is a literal per-argv-element token scan, so any
   command that interposes a shell or an interpreter over a string hides privilege escalation, host authority and
   filesystem escape (V1-F4-01). The network trigger survives only incidentally, because `://` is found as a
   substring.
3. *Does anything that cannot be evaluated fail closed and gate?* **No.** Only an entirely absent command is recorded
   `undetermined`. A command the OS demonstrably cannot read is treated as fully evaluated and clean — contradicting
   OD-P2-03 requirement 3 and this function's own stated rule.

The policy comment is explicit that the token lists are *"a KERNEL FLOOR, not a safety proof … the governed,
independent security review carries what the OS cannot observe"*. That is a defensible architecture — and it is
exactly why V1-F3-01 is blocking rather than cosmetic: the review that is supposed to carry the unobservable is bound
to a tool id and a version string, not to the installation. The floor leaks and the backstop is about a different
artefact.

**Net.** The OD-P2-03 implementation is substantial, well-documented and right in its shape. It is not yet sound
against an install-authority role that wants to get an arbitrary command onto the trusted surface without the owner
seeing it.

## 6. My assessment of F4

F4 is two boundaries wearing one name, and they are in very different states.

**The plugin boundary is in good order** — 12 of 12 held-out assertions, every bullet demonstrated. A hand-declared
descriptor authorises nothing and the OS records each of its claims as ignored. Registration and provenance live in
T2-sealed OS state and a hand-written registry entry is refused. Descriptor and implementation bytes are bound,
including the module-form case (`python3 -m …`) that was BC-P2-40/S0-F4-01 — that is genuinely closed. One changed
byte fails closed; an edited descriptor no longer matches its registration. An executable plugin runs only while a
presented, owner-answered gate bound to exactly its registration subject authorises it, and elevation is never
decided by what the descriptor declares (`declared_elevation_decides_nothing: true`). Registration inside a claimed
task works and raises two gates that each name the other (round-4 INT3-O1). D-0010 holds: a hand-declared descriptor
may run only where the implementation *is* this `gov` binary serving an OS capability endpoint.

**The tool-installation boundary, which OD-P2-03 brought inside F4, is not.** All three blocking findings live here.
Because AC-4 asks whether the `POST_VERIFICATION_HARDENING` capabilities are *incorporated*, and F4 is one of the two
it names, **F4's state is decisive for AC-4 and AC-4 is not met.**

## 7. OD-P2-01 (agent roles stay adapter-declared)

In force, and the property it leaves load-bearing holds. I attacked it nine ways: `--role human`, `--by human`,
`--by product-owner`, `--by "the owner said yes in chat"`, `GOV_ROLE=human`, `GOV_HUMAN_GATE_APPROVED=1`,
`GOV_HUMAN=1`, a hand-written "signed" answer document, and agent resolution of an R2 irreversible low-confidence
gate — against a gate that had been rendered, so nothing was refused merely for being unpresented. Every one is
refused with a typed error (`AUTHORITY_DENIED` or `HUMAN_ANSWER_UNAUTHENTICATED`). A hand-edited gate record reads
T2 BROKEN / UNVERIFIED and authorises nothing; a hand-written `human_approved: true` decision authorises no change.
The owner's signature works, is recorded `answered_by_kind: human`, and re-verifies against the machine's anchor at
use time. **No agent-supplied input manufactured a human approval.**

## 8. H2–H4 and the scenario chain (P2-ADJ-0003)

H2 is exact: 26 dimensions, exactly the five statuses, all 26 cells evaluated per feature, a silent `N/A` reported
invalid and an `N/A_WITH_REASON` honoured as its own state. H3 generates the right class of work per dimension and
carries the designated role — and the designation is *enforced*: a backend-engineer claiming the independent-test
gap task is refused `ROLE_NOT_DESIGNATED`. An implementation task stays blocked while pre-implementation cells are
unsatisfied, and the project overlay can no longer switch that off. H4's chain is complete and traced, test-data
authorship is OS-recorded with a verified T2 binding, independence is *enforced* at registration
(`DATA_AUTHOR_NOT_INDEPENDENT`), and provenance is required and bound to content that exists.

P2-ADJ-0003 holds as ruled: an incomplete scenario chain made the suite `UNHEALTHY`, generated its remedy work, and
**refused nothing** — the readiness block's own 26 remedy tasks all stayed runnable. I built green baselines with
contract-valid fixtures, as the adjudication directs; no probe passed vacuously.

## 9. I1–I4 and generated work (BC-P2-24)

All 22 task classes exist **and were each created as a task in one DAG**. All nine task-contract fields have an
enforcing consumer. All eleven generation sources are declared in the verified kernel taxonomy and implemented; I
exercised generation end to end — real audit findings and a missing tool generated real linked tasks, and a lesson
from a worker return generated work linked to the causing record. Every generated task records its source, subject,
dedup key and the evidence that caused it, and a second immediate run generated nothing (idempotent). The DAG reports
runnable/blocked/waiting-human sets, a dependency-ordered critical path and a dependency-ordered per-feature path,
and an independent branch kept running while another waited on the owner. **BC-P2-24 is closed for gamma.**

## 10. Iteration-0 disposition (40 findings in scope)

`prior-findings-disposition.yaml` disposes of all 36 gamma audit-of-record findings and the 4 synthesis findings that
name a gamma capability: **29 CLOSED, 10 RESIDUAL, 1 NOT_APPLICABLE**.

Closed, with my own evidence, include the heaviest iteration-0 defects in this family: A0-E1-01 to A0-E1-04 and
S0-E1-01 (acting-role resolution, forged gate answers, the L4 default), A0-E4-01/02/03 and A0-E4-04 (claim atomicity,
DAG-derived claimability, worktree and scope, `continue`), A0-F1-01 (skill regression now executes), A0-F2-02,
A0-F3-01 (the answered install gate now installs), A0-F4-01/02/03/04 and S0-F4-01 (the whole plugin boundary),
A0-G1-02 (material change inside an ordinary task), A0-H3-01, A0-H4-01/02/03, A0-I2-01, A0-I2-02, A0-I3-01,
A0-I4-01, S0-I4-01 and S0-W5-01.

Still residual: A0-E1-05 (tester-independence half), A0-E2-01, A0-E3-01, A0-F1-02 (inputs/outputs half), A0-F1-03,
A0-F2-01 (task-class and filesystem-scope halves), A0-F3-02 (maintenance review and candidate surfacing),
**A0-F4-05 (the blocking one, → V1-F3-01)**, A0-F5-01 and A0-G1-01 (negation half). A0-I2-03 is
`NOT_APPLICABLE`: its precondition no longer arises in the form described, and I did not construct the original
reproduction, so I record that honestly rather than claiming it verified closed.

## 11. Freshness (AC-10 for gamma's capabilities)

Demonstrated, not assumed. The evidence currency key now carries 31 input classes including `tools_plugins`,
`project_skills`, `spec_tasks`, `spec_requirements`, `source`, `index_manifest` and `machine_trust`. Adding a project
skill changed the `project_skills` digest and the whole key; a new tool descriptor changed `tools_plugins`; a new
task changed `spec_tasks`. A green governance record stopped being current after a relevant input changed, the OS
named the changed class, and governance-affecting work was refused on it. **BC-P2-03's currency defect is closed for
gamma's capabilities.** One caveat: the refusal I observed carried code `INDEX_STALE` rather than an
obsolete-green code, so the *refusal* is demonstrated and the *precise reason* is one step upstream.

## 12. What I could not establish

* **`cargo test --test certification`** — I started it in this worktree and then **stopped it deliberately**. Three
  verifiers were running their certification suites on this machine at once and mine was starving my own held-out
  suite, which is the evidence only I can produce; the certification suite is regression evidence (O3) that AC-15
  makes the synthesis verifier's, and the orchestrator has already reproduced it at 207/0 on this candidate. So I
  have no certification number of my own. `cargo test --lib` did complete in this worktree: **276 passed, 0 failed**
  (`evidence/regression-cargo-test-lib.out`).
* **F3 "candidate discovery"** — I established that a capability gap becomes governed, role-designated work naming
  the tasks it blocks. Whether an agent working that task can actually *discover* candidates is agent behaviour a
  G6 qualification harness measures, not something Phase 2 can settle.
* **`production_merge_allowed` enforcement (I2 b9)** was observed only indirectly: the probe task was blocked earlier
  in the chain by its absent required tool, so the merge decision was never reached. The field is recorded and
  carried into the close decision; I did not see it refuse a merge.
* **`gov adopt` / `gov migrate` stages** (A0-E1-01's second half) are alpha's scope; I established the shared
  acting-role resolution those stages use, not the stages themselves.
* **The whole contract-binding chain (AC-13)** and the product-wide evidence-owner question (AC-10) are the synthesis
  verifier's. What I checked, and what held: gamma's 19 capabilities carry checklist bullets in the compiled view and
  an evidence class plus at least one automated check in the evidence map (0 of 19 unmapped), and `gov contract
  verify` in this worktree returns `CONTRACT_SOURCE_BOUND` over a compiled form it describes as semantically
  identical to the owner source including Gate U, the checklist items and the Contract v3:53-73 fields
  (`evidence/contract-verify.out`). Whether that self-description is itself trustworthy — BC-P2-01's original
  mechanism was a verifier comparing the compiled file with a fresh run of the same lossy compiler — is the
  synthesis verifier's to settle, not mine.
* **A0-I2-03's original reproduction** (the one-character path truncation) — see §10.
* **Gamma's probes ran on one machine kind.** The cross-machine attack (P2-ADJ-0002) is alpha's lead; my probes
  isolate `XDG_STATE_HOME` per project, which simulates separate machines but does not exercise two provisioned
  machines of one owner exchanging OS-written facts.

## 13. A note on side effects

While first exploring, I provisioned a trust anchor in the **real machine's** shared state
(`~/.local/state/governance-os/machine/trust/`) before I had isolated `XDG_STATE_HOME`. I noticed immediately, and
since `rm` is denied in this environment I **moved both files aside** to
`scratchpad/gamma-lab/quarantined-machine-trust/`, returning that directory to empty (its posture was `UNPROVISIONED`
beforehand and is again). Every probe in `heldout/` sets a per-project `XDG_STATE_HOME`, so nothing in the committed
suite touches shared machine state. No product source, and nothing outside this evidence directory and my run
report, was modified at any point.

## 14. Files

| Path | What it is |
|---|---|
| `capability-audit.yaml` | 19 capabilities, 167 bullets, each with implementation, automated and independent evidence |
| `findings.yaml` | 13 findings, each labelled `RESIDUAL` (with its class) or `MATERIALLY_NEW`, with reasons |
| `prior-findings-disposition.yaml` | all 40 iteration-0 findings in scope: 29 CLOSED, 10 RESIDUAL, 1 NOT_APPLICABLE |
| `heldout/RUN-ALL` | re-runs the whole suite; one PASS/FAIL line per assertion |
| `heldout/*.sh` | the eleven probes |
| `heldout/ownersign.py`, `heldout/publish_release.py` | my own owner-side signer and release publisher (published test seeds only) |
| `evidence/*.out` | captured output of every probe run |
