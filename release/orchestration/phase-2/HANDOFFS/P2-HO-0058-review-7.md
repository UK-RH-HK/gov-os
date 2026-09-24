# P2-HO-0058 — seventh independent adversarial review (P2-AR-0094)

| Field | Value |
|---|---|
| Subject | `phase2/remediation-ar92` **`a376cc4`** (base `4686e8d`) |
| Your role | **independent adversarial reviewer.** You did not build this. No role may grade its own work. |
| Evidence class | **`INDEPENDENT_ADVERSARIAL`** — your findings are the only ones that close anything |
| Authority | OD-P2-08 §7 (independence), §8 (stop conditions), §10 (what minting requires) |
| Builder's report | `P2-AR-0093`'s hand-back, reproduced in the round record. Treat every claim in it as **unverified**. |

## 0. Where this stands, so you can aim

Six independent reviews have preceded you. **Property A has now held twice** — AR90 and AR92 both attacked it and
could construct no divergence. `runtime/src/exec_resolve.rs` is **untouched** by this round (I verified: the diff is
empty). Confirm no regression; do not re-litigate a settled surface.

**Property C is where every failure has landed**, and the pattern is exact and worth stating because it predicts what
you should attack: *each repair adds a mechanism, and that new mechanism is the next round's defect.* AR91 introduced
`other_live_claim`; AR92 broke precisely that and nothing else. **This round introduces `gov floor-reanchor` and an
OS-written sandbox marker. Those two are your primary targets.**

Seven rounds have failed by enumeration: programs → shapes → list premises → class values → consumers → obligations →
a liveness predicate. Ask of each new mechanism: *what does it reason about, and where is the authority actually
determined?*

## 1. What I verified myself before dispatching (do not re-derive; attack past it)

* `paths.rs:765` — the `&& Path::new(minted_for).exists()` conjunct **is deleted**. The guard now returns on
  `minted_for != current_canon` alone.
* `is_health_sandbox_root` now takes `state_root` and requires `shaped && sandbox_record_path(...).is_file()`.
* `COMMAND_GUARDS` line 288 registers `g("floor reanchor", "install_kernel", Write)` — the same tier as `init` and
  `kernel reinstall`. **No new authority tier was invented.**
* Dispatch (`cli/src/main.rs:1967`) calls `guard_write(&p, "floor reanchor")` **and** `authority::require(&p,
  "install_kernel")`, and `g0_label` maps the command to the matching `"floor reanchor"`. I chased a suspected guard
  bypass here — `command_name` spells it `"floor-reanchor"` (hyphen) at `main.rs:2397` — and it is **not** a bypass:
  `command_name` feeds display/telemetry only. **But two parallel hand-maintained label tables for one command, one
  authority-bearing and one not, already diverging in spelling, is the AR90-C6 / AR92-D2 defect class.** Judge it.
* Product diff is 5 files: `cli/src/main.rs`, `orchestration/control.rs`, `paths.rs`, `policy.rs`,
  `scheduler/sandbox.rs`. Anything outside that is not this round's.

## 2. Primary target — the sandbox marker is now a capability, and the builder says it leaks

I derived this from the code and it is the sharpest thing I can hand you. **Verify or refute it first.**

`Sandbox::create` writes its marker under the protected `state_root`, keyed by the sandbox path, and removes it in
`Drop`. The builder disclosed the leak but classified it as *"storage-hygiene, same class, same severity, not
fixed."* **That classification looks wrong to me**, because this round made the marker authority-bearing: it is now
the sole thing separating a real sandbox from an attacker's `mkdir -p`. A leaked marker is a leaked capability.

The chain to test:

1. `Sandbox::create` builds `base = p.runtime_dir().join("health").join("sandboxes")` — **inside the project**, so an
   attacker with ordinary project-scoped write access can *observe* the `{purpose}-{short_uuid}` directory name while
   the sandbox is alive. The uuid defends against guessing, **not against watching.**
2. Kill the process before `Drop` runs (`kill -9`, OOM, power loss). The marker persists; the sandbox directory does
   not.
3. The attacker recreates a directory at that exact observed path.
4. `is_health_sandbox_root` → shaped ✓ + record ✓ → **exemption granted**, `reconcile` skips `other_live_claim`
   entirely, and the planted donor floor is adopted.

If that holds, it is HIGH and it re-opens AR92-C2 by a different route. Also test: whether the marker is keyed to the
*canonicalised* path (AR90-C4's symlink route composed with this), and whether marker and shape can disagree.

## 3. Primary target — `gov floor-reanchor` is an identity transfer

The builder was straight about this rather than claiming AR92-C3 solved, which is to their credit: re-anchoring
**moves** an identity and **removes the old store entry**. So a successful re-anchor *frees* the identity's previous
claim. Attack that directly:

* Can an attacker induce or redirect a re-anchor so that the removal happens where they want it? What decides
  `p.root`?
* Run it from a still-live second checkout: the builder states this **steals the identity from the first**, which is
  then refused on its own next read. Is that reachable without `install_kernel`, or composable with an attacker-
  planted document so the owner's legitimate remedy does the theft?
* It **never reads `bound_cit`** — deliberately, the builder says, because it operates below that layer. Test a
  re-anchor against a document whose `bound_cit` names a transaction this store never had. The builder names this as
  an untested combination.
* **Concurrency**: scan-then-write-then-remove is not atomic. The builder names racing invocations as reasoned, not
  measured, with last-write-wins and a swallowed `remove_dir_all`. Construct the race.
* Idempotence and authority controls: `ar92_reanchor_requires_install_kernel_authority` and
  `..._refuses_when_this_machine_never_held_the_identity` — the second carries a documented harness limitation (the
  explicit `ADOPTION_FLOOR_REANCHOR_NO_PRIOR_CLAIM` code is unobservable through a full CLI round-trip because G0 and
  `kernel reinstall` resolve the situation first). **Decide whether the property it claims instead is actually
  proved.**

## 4. The builder changed two of your predecessor's held-out probes — adjudicate this

This needs an independent ruling and the builder cannot give it:

1. **`ar92_c3_a_second_live_checkout..._is_refused_its_floor`** — the AR92 reviewer's own probe asserted
   `o.finding.is_none()`. The builder changed it to `o.finding.is_some() && o.eff == "source"`, arguing the original
   was aspirational and contradicted the AR92 review's own prose ("is refused its own committed floor… Fail-closed
   and reported"). **Read AR92's text and rule on whether that is a legitimate correction or a builder relaxing an
   independent probe to fit the implementation.** If the latter, it is a finding in its own right.
2. **`ar92_c4_a_bare_relocation_re_anchors_silently`** — documented the pre-repair defect; now asserts refusal plus
   exactly one store entry. Name unchanged, docstring updated. Same question.

## 5. Secondary — verify, do not assume

* **AR92-C3 is NOT closed** and the builder says so. A second live checkout still permanently loses its floor, and
  the only remedy would steal the identity from the original. Judge whether this round made it *worse*.
* **§1.4 disclosure.** New durable `FloorIdentityState::bootstrap_adopted`, surfaced through
  `PolicySet::floor_disclosures` → `gov policy overrides`'s `"disclosures"` array, deliberately separate from
  `refused_overrides`/D027 so a legitimate clone stays healthy. Test that the separation cannot be used to route a
  *reportable* event into the non-failing channel. The builder found that a transient signal was consumed by G0's own
  internal policy load before the handler saw it — check the durable field has no equivalent consumption path.
* **Missing positive control (builder-disclosed).** No targeted test proves a *legitimate* sandbox still gets the
  exemption. The builder suggests an `Isolation::Sandbox` check after `rebuild-memory`. **Build it.** A guard that
  refuses everything passes every negative test.
* **Not taken, named only:** §2.2 rollback residual (advance-on-commit + `pending_sequence`), §2.4 `manifest_paths`
  hand-enumeration, unbounded `adoption-floors/` and `health-sandboxes/` growth. Confirm each is genuinely LOW and
  genuinely not attacker-reachable, rather than accepting the label.

## 6. Do not pass by gating everything, and re-run rather than carry forward

Independently re-run at minimum: `ar92_floor ar92_probe ar90_probe ar88_ ar90_floor ar83_governed_widening
multi_machine::clone_rebuilds_identical_derived_state brownfield::brownfield_adoption_end_to_end`. **All five
OC-P2-04 cases must stay reachable and reportable**; `floor_requires_product=false` must stay false; a conforming
pinned ELF must stay ungated **and running**; a genuine foreign clone must still bootstrap and stay healthy.

The builder reports **full suite 363/0** in 3,486 s at `a376cc4` (default threads; load fluctuated 15–48 from other
sessions on this box). **Verify the figure against the tree**; re-run the full suite only if you change a product
line or have reason to doubt it.

Never `--test-threads=1`. Never pipe without `set -o pipefail`. Never bare `cargo fmt`. Note: `. "$HOME/.cargo/env"`
is refused by the worktree sandbox guard — use `"$HOME/.cargo/bin/cargo"` directly.

## 7. Anti-stall

Never wait on me. Bounded iteration count and a deterministic timeout action on every wait; prefer waiting on file
content; if you match processes, prove the waiter cannot match itself. Do not ask permission to run tests.

## 8. Return

A verdict — `SURFACE_SOUND` or `RESIDUAL_DEFECTS` — then: each finding with severity, the reproduction you built, and
whether it is new or a re-opening; **each of the seven OD-P2-08 §8 stop conditions answered explicitly YES/NO with
reasoning**; your ruling on §4; your verdict on Property A and Property C separately; what you could not probe; and
your commit SHA.

**If this surface is now sound, saying so is the most valuable thing you can do.** A manufactured objection costs a
phase for nothing; an unfounded green ships a defect. Neither is acceptable — only the evidence is. Two consecutive
reviews have found Property A sound and said so plainly, and that is exactly how it should have gone.
