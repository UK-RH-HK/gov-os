# P2-HO-0054 — A + C structural remediation (OD-P2-07)

| Field | Value |
|---|---|
| Authorised by | **OD-P2-07**, the owner's architecture decision of 2026-09-22 |
| Base | `phase2/repair-3-boundary` `e25ca70` (P2-AR-0076, full suite 252/0) |
| Execution | native Claude subagent, `claude-sonnet-5`, worktree-isolated |
| Follows | P2-HO-0051 in full, except where this file amends it |
| Evidence class of everything you write | **`BUILDER_DEVELOPMENT_EVIDENCE`** — see §6 |

## 1. What this round is, and what it is not

**This is not another enumeration round.** Four rounds have failed by enumerating: programs, then command shapes, then
the premises of list entries, then `class` values, then the *consumers* of `class`. The owner's instruction is explicit:

> Do NOT treat this as another local enumeration/patch round. The purpose is to remove the architectural pattern
> responsible for the repeated failures.

If you find yourself adding a name to a list to fix a finding, **stop and reconsider** — that is the failure mode, not
the fix. The two properties below are what you are building; the tests you write are not the definition of done.

## 2. Option A — no raw or unbound command may acquire ungated installation authority

> **Property A: an installation reaches the ungated path only if every file it executes is pinned in the descriptor and
> byte-verified immediately before execution. Anything that cannot be reduced to an exact bound artefact is
> `undetermined` and gates.**

**The good news: most of this machinery already exists and works.** `classify_file_candidate`
(`runtime/src/tools.rs:1099`) already verifies that an executed file is named in `descriptor.pinned_files` with a
matching `sha256`, is inside the project, and is re-read at execution. `pinned_files_of` (`:1297`) reads the pins.
P2-AR-0077 confirmed the byte-binding and lifetime re-verification hold (AR68-F4, AR73-F4, AR73-F6 all closed).

**So A is mostly subtractive, and that is the point.** The defect is that `unreadable_command_shape` has an *escape
hatch* — `plain_argument_programs` — that returns "readable" for a command that executes no pinned artefact at all, on
the premise that the OS can read the program's whole argv. That premise has now been falsified three times for `curl`
alone (`-K`, `file://` with an empty authority, `--write-out %output{…}`) and once structurally for `cp` (symlink, then
hard link).

**Remove the escape hatch.** A command that does not reduce to a verified pinned artefact gates. Expect
`plain_argument_programs` to disappear, and check whether `argument_indirection_flags` becomes dead with it — a flag that
redirects argument reading cannot matter when there is no unbound path left to protect. **Deleting a mechanism is a
better outcome than extending one.** If either list survives, your report must say exactly why.

**Where the argv itself is bound.** You may reasonably ask: a pinned script given different arguments does different
things, so what binds argv? The answer is already in the architecture — the governed security review binds the
**descriptor**, and the descriptor carries the commands. So argv is bound by the review, and the artefact bytes by the
pin. OD-P2-07 states this: the review must bind the specific descriptor/version, the artefact identity, its digest(s),
and any executable artefact the installation requires. **Verify this is actually true of `review_subject` rather than
assuming it** — if argv is not covered by the review subject, that is a finding to report, and an important one.

**Explicitly forbidden**: adding another curl flag, command shape, program, path syntax or parser exception to fix
AR77-F1, F2 or F4.

**Preserved**: a raw command may still run **through a gate**. And ordinary acquisition survives by wrapping
installation logic in a pinned reviewed artefact — an `install.sh` whose bytes are bound and re-verified.

### 2a. Authorisation you will need — existing tests assert the old architecture

Certification tests currently assert that raw-command installs proceed **ungated** — at minimum `r2_wsa.rs:433`,
`r4_residual.rs:1212`, `:1299`, `:1319` (the `["curl","-sS","<https url>"]` shapes), plus `cp`-based negative controls.
Under Property A those shapes must now **gate**.

**You are authorised to change what those tests assert**, on the same reasoning that governed P2-ADJ-0004: the behaviour
they assert *is* the defect, and the change makes them **stricter**, never weaker. The conditions are absolute:

- **No test may be renamed, removed or `#[ignore]`d.** The evidence map names tests by exact path.
- Each changed assertion must be listed in your report with its file, its old claim and its new one.
- **A test must never be weakened to make something pass.** If a test cannot be satisfied by a *correct* implementation
  of Property A, stop and report it — that is a finding about the architecture, not a file to adjust.
- Ordinary acquisition must still be demonstrably possible: show at least one **conforming, pinned-artefact** install
  proceeding ungated with **zero** gate records. If Property A leaves no ungated path at all, you have over-applied it.

## 3. Option C — one authoritative source for `class` authority semantics

> **Property C: project-editable classification state cannot silently increase effective authority or obtain a
> governance exemption.**

Establish **one** authoritative predicate answering *"does this class confer any exemption from any governed control?"*,
and make every relevant consumer derive from it. **Do not add the four missing values to another list** — that is the
enumeration failure one more time.

**You must survey all consumers, not only the two AR77-F3 named.** A non-exhaustive starting set, found by the
orchestrator with `grep -rn "\.class()" runtime/src/`:

- `orchestration/tasks.rs:1856` `is_production_path` — exempts **six** values, gates `EXPERIMENT_OUTPUT_IN_PRODUCTION`,
  `PRODUCTION_MERGE_NOT_ALLOWED` and the after-the-fact governance sweep;
- `orchestration/tasks.rs:947` `contract_generated` — exempts **two**, drops paths from the observed-mutation set;
- `policy_precedence.rs:586` `confers_generated_exemption` — the current comparison, **two** values;
- `paths.rs:364` `SECRET_CLASS`, `paths.rs:830` a `"derived" | "generated"` match, `paths.rs:338`;
- `verification/lineage.rs:295`, `:596`, `:981` (`CODE_CLASSES`), `:1077`, `:1082`.

Work out which of these are **authority-bearing** (a class value changes whether a control applies) versus merely
descriptive (indexing, reporting, lineage labelling). Only the authority-bearing ones must derive from the single
predicate — but **say in your report which you judged descriptive and why**, because a wrong call there is exactly how
this class of defect recurs.

**The capability is preserved.** An authorised governed change may classify paths as evidence/generated/derived. The
owner is explicit: *"The defect is not the capability. The defect is obtaining that capability through an unauthorised
hand edit."* So a governed transaction must still be able to do this; a hand edit to
`governance/project/REPOSITORY_CONTRACT.yaml` must be refused **and reported** — OC-P2-04 clause 4: *"Silence is
failure."*

## 4. AR77-F4 and AR77-F5

- **AR77-F4 (hard link).** The owner: *"do not simply mark it closed because raw-command trust was removed."*
  Independently retest it against the new architecture and demonstrate its disposition with **effect-level** evidence —
  create a hard link, run the install, compare file **content** outside the root before and after. If Property A closes
  it, prove that; if a residue remains, say so.
- **AR77-F5.** Correct the runtime message that tells an auditor `curl -k` "reads further arguments from a file". If the
  mechanism disappears with `argument_indirection_flags`, note that the finding is resolved by deletion. Do not broaden
  this into unrelated work.

## 5. Scope

`allow_write`: `runtime/src/tools.rs`, `runtime/src/policy_precedence.rs`, `runtime/src/orchestration/tasks.rs`,
`runtime/src/paths.rs`, `framework/policies/TOOL_POLICY.yaml`, the certification tests named in §2a, and new test files
you declare in `tests/certification/main.rs`.

Beyond that list, **stop the item and report it** rather than reaching for the file. `tests/governance/capability-evidence-map.yaml`
is **out of scope** and must not be hand-edited, and `gov contract compile` must not be run — both adjudicated
previously; new tests are discovered automatically via `contracts::test_index`.

## 6. Your tests are development evidence, and cannot close these findings

OD-P2-07 is explicit, and it follows from P2-AR-0077 finding that the previous property test quantified over
`["generated", "derived"]` — exactly the two values its own author implemented — inside a test named *"for any class
value"*:

> Builder-authored property tests are NOT automatically independent evidence. … That only proved "the implementation
> behaves correctly over the cases the implementation author imagined."

So: write thorough regression tests, property tests and negative controls — you should, and your implementation needs
them. But label them `BUILDER_DEVELOPMENT_EVIDENCE` in your report and understand that **a fresh independent Opus 5
reviewer will derive its own attack domain and will not treat your generator as the definition of completeness.** It
will specifically attack what your generator *cannot produce*.

The most useful thing you can do about that: **in your report, name the cases your own generators cannot reach.** The
previous builder did this unprompted and it was the most valuable part of its handover.

## 7. Testing protocol

Targeted tests while iterating; affected dependency tests next; **one** full certification suite at the end.

- **The full suite costs ~50 minutes** (measured: 252 tests, 2,966 s, machine-exclusive at default threads). Not 20–25 —
  that estimate is retracted.
- **Never pass `--test-threads=1`** (≈3× penalty, no isolation benefit here). Use default threads.
- **Never pipe a test command without `set -o pipefail`.**
- Record thread count, machine load, command line and duration with every suite figure you report.
- Start commands with `. "$HOME/.cargo/env"`.
- **Do not run bare `cargo fmt`** — it walks the whole module tree and reformats files outside your scope; a previous
  worker hit this and had to revert ~17 files. Use `rustfmt --edition 2021 --check <single non-root file>`.

## 8. Stall protection — you must never wait on me indefinitely

`worker_stall_protection` is **ACTIVE** (owner instruction; `ORCHESTRATOR_STATE.yaml`). A previous worker sat idle for
~420 minutes waiting for a coordinator confirmation that never came. That must not recur, so:

- **Do not wait for my permission to start your full suite.** Evaluate the precondition yourself: proceed when no
  competing `cargo`/`gov` certification process is running and load average is below ~4. If it is not satisfied, wait,
  re-check periodically, and **proceed automatically** once it is.
- If you ever genuinely need a decision from me, report state `BLOCKED_ON_COORDINATOR` with: why you are blocked, what
  you are waiting for, a **timeout**, and the **default action** you will take when it expires. Then take that action.
- Never report yourself as running when you are waiting.

Write your checkpoint to `release/orchestration/phase-2/telemetry/checkpoints/P2-AR-0078.checkpoint.md` before the full
suite and after each property lands.

## 9. What to return

Verdict (`REPAIRED_CLAIMED` / `PARTIAL` / `OWNER_DECISION_REQUIRED` / `INCOMPLETE`), then:

- **Property A**: what mechanism now enforces it, **what you deleted**, whether `plain_argument_programs` and
  `argument_indirection_flags` still exist and why, and whether `review_subject` genuinely binds argv.
- **Property C**: the single predicate, every consumer you surveyed, which you judged authority-bearing versus
  descriptive **and why**, and how a future consumer is prevented from silently diverging.
- **AR77-F4** with effect-level evidence; **AR77-F5** disposition.
- **Changed test assertions** per §2a: file, old claim, new claim.
- **Tests added**, each labelled property / regression / negative control — all `BUILDER_DEVELOPMENT_EVIDENCE`.
- **The cases your generators cannot reach.**
- **Checks run**: command, result, duration, thread count, load.
- **Anything left undone**, with the reason.
- **Your commit SHA** on the branch.

An accurate `PARTIAL` naming a real weakness is worth far more than a confident `REPAIRED_CLAIMED`. The next reviewer is
adversarial, independent, and has broken this surface four times.
