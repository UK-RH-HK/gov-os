//! Signed Release Root v1 — below-floor break-glass recovery (`OWNER-DECISION-0006`, ARCH-0003 §7.1).
//!
//! Requirement map (all ten binding requirements of OWNER-DECISION-0006):
//!
//! | # | requirement | where |
//! |---|---|---|
//! | 1 | recovery release must still be authentic | the floor check is relaxed in [`super::verifier`]; the authenticity check is not reached by any break-glass path |
//! | 2 | owner-controlled, non-manufacturable authority | [`authorise`] + [`super::metadata::BreakGlassToken`] |
//! | 3 | durable entry record | [`enter`] → `degraded/<product>.json` in protected machine state |
//! | 4 | explicit `DEGRADED — RECOVERY ONLY` marking | [`DEGRADED_TOKEN`] |
//! | 5 | permitted activities | [`PERMITTED_ACTIVITIES`] (the §5 text) and [`PERMITTED_OPERATIONS`] (the operation labels that realise it) |
//! | 6 | refused activities | **two enforcement points, one decision.** [`guard`] / [`guard_light`] decide §6 bullet 1 at the *operation* level through a default-refuse allow-list ([`REFUSAL_POLICY`]). [`guard_effect`] / [`guard_effect_on`] decide §6 bullets 2–7 at the *effect* level, and are called **from inside the primitive that performs the effect** ([`SECTION_6_SINKS`]), so a path that reaches the effect cannot miss them. [`REFUSED_ACTIVITIES`] names the classes; [`REFUSAL_CLASSES`] only chooses which bullet a bullet-1 refusal is reported under |
//! | 7 | exit condition | [`exit_satisfied`] — the single `SRR2-R1-C1` policy point |
//! | 8 | the floor itself is never lowered | [`enter`] writes no floor; `Floors::raise_*` are monotonic-only |
//! | 9 | ingress consistency | the floor check lives in the one verifier every ingress calls |
//! | 10| works with no network | every check here reads local files only |
//!
//! ## Why there are two enforcement points and not one, and why that is still one decision
//!
//! `OWNER-DECISION-0006` §6 bullet 1 names a **class of operations** ("normal privileged Governance OS
//! operation"), so it is decided where operations are named: at [`crate::orchestration::control::guard_write`],
//! which every mutating governed operation already calls. Bullets 2–7 name **effects** — creating or approving a
//! Human Gate, certifying a release, mutating trust policy, acquiring a privileged plugin, lowering a floor,
//! presenting a below-floor release as current. An effect is not an operation: `update --apply` is an allow-listed
//! §5 restoration operation that *contains* a §6 bullet 2 effect, and `gov trust root-update` is an operation that
//! never passes an operation-level chokepoint at all because it takes no `Project`.
//!
//! `AR29-B1` and `AR29-B2` were both instances of one class: **the guard was not on the path**. Adding a guard
//! call beside each offending operation would close those two instances and leave the class open, because the next
//! operation someone writes would need someone to remember. So the effect-level check lives **inside the single
//! primitive that realises each effect** ([`SECTION_6_SINKS`]). A caller that has not been written yet still
//! reaches the effect only through its sink, and the sink refuses. The enforcement is a property of the effect,
//! not of the caller.
//!
//! ## Why the census is derived and not declared
//!
//! That argument is only as good as the census behind it, and three R1 iterations failed the same way: a
//! *declared enumeration* standing in for a universal negative, complete when written and silently short as soon
//! as the product grew an unenumerated path — and, each time, a test derived from the same enumeration as the
//! code, so it could not see that the enumeration was short. [`SECTION_6_SINKS`] was the third such enumeration.
//!
//! [`SECTION_6_SIGNATURES`] replaces the claim. It names, per bullet, the product's own primitives an
//! implementation of that effect must use, and `section_6_coverage_is_derived_from_the_product` walks **every
//! function in `runtime/src` and `cli/src`** to find them. A new primitive appears in the derived set without
//! anyone remembering to add it. A bullet that claims no primitive exists must first prove its detector can see
//! one, against a positive control. What the derivation cannot see is written down beside it.
//!
//! Both points call one private decision (`decide`) over one reading of one record ([`read_marking`]), so the
//! operation-level guard, the effect-level guard, [`Degraded::load`] and [`is_degraded`] can never disagree about
//! whether this machine is marked (`AR29-C1`).
use crate::srr::metadata::BreakGlassToken;
use crate::srr::state::{degraded_path_at, write_durable, Floors, MachineState};
use crate::util::now_iso;
use crate::{GovError, Result};
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

/// The machine marking required by `OWNER-DECISION-0006` §4, byte-exact.
///
/// The separator is U+2014 EM DASH, not a hyphen and not an en dash. The assertion below pins the exact bytes so a
/// well-meaning edit cannot silently change the token.
pub const DEGRADED_TOKEN: &str = "DEGRADED — RECOVERY ONLY";

/// Bytes of [`DEGRADED_TOKEN`]: `DEGRADED`, space, U+2014 (E2 80 94), space, `RECOVERY ONLY`.
pub const DEGRADED_TOKEN_BYTES: &[u8] = b"DEGRADED \xe2\x80\x94 RECOVERY ONLY";

/// OWNER-DECISION-0006 §5 — permitted while below floor.
pub const PERMITTED_ACTIVITIES: &[&str] = &[
    "inspection",
    "backup_export",
    "diagnosis",
    "repair",
    "uninstall_reinstall",
    "restore_authenticated_release",
];

/// OWNER-DECISION-0006 §6 — refused while below floor.
pub const REFUSED_ACTIVITIES: &[&str] = &[
    "normal_privileged_operation",
    "human_gate_create",
    "human_gate_approve",
    "release_certification",
    "trust_policy_mutation",
    "privileged_plugin_acquisition",
    "floor_lower_or_reset",
    "present_below_floor_release_as_current",
];

/// **The allow-list.** The operation labels permitted while the machine is marked `DEGRADED — RECOVERY ONLY`,
/// each mapped to the `OWNER-DECISION-0006` §5 activity that covers it.
///
/// Matching is **exact**, never substring: an operation proceeds only when its label appears here verbatim.
/// Everything else is refused — including an operation added to the product tomorrow, and one nobody anticipated.
/// This table is the *only* exception to a structural default of refusal, which is what §6 bullet 1 requires:
/// "normal privileged Governance OS operation" is a **class**, and a class cannot be enforced by enumerating its
/// members.
///
/// Why each entry is a §5 activity and not §6 bullet 1:
///
/// | operation | §5 activity | why it is recovery, not normal governed operation |
/// |---|---|---|
/// | `checkpoint` | backup/export | captures resumable state; advances no governed record's lifecycle, decides nothing and grants no authority |
/// | `kernel reinstall` | uninstall/reinstall | the ingress break-glass exists to serve; the release it installs is still authenticity- and floor-checked inside `admit` |
/// | `update --apply` | restoration of an authenticated release | same, and independently floor-checked inside `admit` |
/// | `update --rollback` | restoration of an authenticated release | restores a previously installed release, whose target is admitted through `admit` like every other ingress (§9) |
///
/// **An entry permits the operation; it does not suspend §6 inside it** (`AR29-N4`). §5 is permissive and §6 is a
/// MUST NOT, so an allow-listed operation that internally needs a §6 bullet 2–7 effect is refused at that effect
/// by [`guard_effect`]. [`BELOW_FLOOR_LIMITS`] states, per entry, exactly where that bites, so the allow-list and
/// the reachable behaviour agree rather than merely coexisting.
///
/// The admission criterion applied to this table: an operation belongs here only when it realises a §5 activity
/// **and** it neither advances the lifecycle of a governed record nor changes trust, authority or policy state.
/// That criterion deliberately excludes two labels a reader might expect to find here, because both mutate
/// governed state despite read-sounding names: `task status` is [`crate::orchestration::tasks::set_status`], a
/// lifecycle mutation behind `mutate_task_status`, and `cit simulate` writes `cit_status = SIMULATED` back to the
/// transaction. Both are §6 bullet 1.
///
/// §5's "inspection" and "diagnosis" need no entry here: read-only commands (`gov trust status`, `gov doctor`,
/// `gov recover --dry-run`, the `list`/`show` surfaces) never call
/// [`crate::orchestration::control::guard_write`], so they never reach this guard. §5's "repair" is realised by
/// the three installation entries above.
///
/// §5 is permissive — "Permitted activities **may** include" — so a narrower allow-list satisfies it, while §6 is
/// a MUST NOT. When a mapping is arguable the entry is left out: erring narrow can only cost availability, erring
/// wide breaks the decision.
pub const PERMITTED_OPERATIONS: &[(&str, &str)] = &[
    ("checkpoint", "backup_export"),
    ("kernel reinstall", "uninstall_reinstall"),
    ("update --apply", "restore_authenticated_release"),
    ("update --rollback", "restore_authenticated_release"),
];

/// The shape of the §6 control, named in one checkable place: an allow-list whose default is refusal.
pub const REFUSAL_POLICY: &str = "allow_list_default_refuse";

/// **What an allow-listed operation still cannot do below floor** (`AR29-N4`).
///
/// `OWNER-DECISION-0006` §5 permits an *activity*; §6 forbids a set of *effects*. The two meet inside
/// `update --apply`, which is permitted as restoration of an authenticated release and which, for a target the
/// installed policy says needs human approval, would have to create a new Human Gate — a §6 bullet 2 MUST NOT.
/// The decision is not ours to soften: the operation is refused at that point, and the restoration routes that
/// need no gate stay open.
///
/// This table exists so the promise and the behaviour are written down in the same place. It decides nothing:
/// [`guard_effect`] is the decision, and it is reached from inside the effect whether or not an operation appears
/// here. It is surfaced in every refusal's `details` and in the durable entry record so an operator reads the
/// limit at the moment it bites.
pub const BELOW_FLOOR_LIMITS: &[(&str, &str)] = &[(
    "update --apply",
    "completes below floor only when the target needs no new Human Gate: creating one is OWNER-DECISION-0006 §6 bullet 2, which binds inside an allow-listed operation exactly as it binds outside one. `kernel reinstall` and `update --rollback` need no gate and remain available.",
)];

/// The gate-free restoration routes, named in refusals so a refused operator is never left without one.
pub const GATE_FREE_RESTORATION_ROUTES: &[&str] = &["kernel reinstall", "update --rollback"];

/// The `OWNER-DECISION-0006` §5 activity that permits `operation` below floor, or `None` when nothing does.
///
/// This is the whole of the §6 decision procedure. `None` means refuse.
pub fn permitted_activity(operation: &str) -> Option<&'static str> {
    PERMITTED_OPERATIONS
        .iter()
        .find(|(label, _)| *label == operation)
        .map(|(_, activity)| *activity)
}

/// Which `OWNER-DECISION-0006` §6 bullet a refusal is *reported* under.
///
/// **This table is not the policy and refusal never depends on it.** An operation absent from it is refused
/// exactly as one present in it is, and is reported under §6 bullet 1, `normal_privileged_operation` — the class
/// the decision names for privileged governed work in general. The table exists only so that an operation the
/// decision names specifically is refused with that specific bullet quoted back to the operator.
///
/// **Every label here names a real operation** (`AR29-N5`): each one is a string this product actually passes to
/// an enforcement point — `control::guard_write`, [`guard`], [`guard_light`] or [`guard_effect`]. AR-0027's
/// false negative on `trust root-update` came from the opposite arrangement: the table named eight operations the
/// product did not have, a label sweep refused the *labels*, and nobody noticed that no *operation* was reached.
/// Names that no operation carries now live in [`RESERVED_REFUSAL_CLASSES`] where they cannot be mistaken for
/// coverage, and the certification test
/// `section_6_refusal_class_tables_are_partitioned_by_what_the_product_actually_enforces` checks the partition
/// against the product's own call sites.
pub const REFUSAL_CLASSES: &[(&str, &str)] = &[
    ("gate create (system)", "human_gate_create"),
    ("gate create (update --apply)", "human_gate_create"),
    ("gate create", "human_gate_create"),
    ("gate answer", "human_gate_approve"),
    ("release build", "release_certification"),
    ("trust provision", "trust_policy_mutation"),
    ("trust root-update", "trust_policy_mutation"),
    ("trust anchor write", "trust_policy_mutation"),
    ("plugin acquisition", "privileged_plugin_acquisition"),
    ("plugins register", "privileged_plugin_acquisition"),
    ("tools install", "privileged_plugin_acquisition"),
];

/// Names that `OWNER-DECISION-0006` §6 makes plausible but that **no operation in this product carries**.
///
/// They are kept, separately and explicitly, for one narrow reason: if such an operation is ever added, its
/// refusal should quote the right bullet on day one rather than default to bullet 1. They are exactly as inert as
/// [`REFUSAL_CLASSES`] — nothing is refused or permitted because of either table — and being listed here is a
/// statement that the operation **does not exist**, which is the opposite of a coverage claim.
pub const RESERVED_REFUSAL_CLASSES: &[(&str, &str)] = &[
    ("gate present", "human_gate_create"),
    ("decide", "human_gate_approve"),
    ("release certify", "release_certification"),
    ("certify", "release_certification"),
    ("trust revoke", "trust_policy_mutation"),
    ("policy set", "trust_policy_mutation"),
    ("plugin install", "privileged_plugin_acquisition"),
    ("plugin acquire", "privileged_plugin_acquisition"),
    ("skills install", "privileged_plugin_acquisition"),
    ("floor", "floor_lower_or_reset"),
];

/// The §6 bullet a refusal of `operation` is reported under. Bullet 1 is the default for everything else.
pub fn refusal_class(operation: &str) -> &'static str {
    for (needle, class) in REFUSAL_CLASSES.iter().chain(RESERVED_REFUSAL_CLASSES) {
        if operation.contains(needle) {
            return class;
        }
    }
    "normal_privileged_operation"
}

/// The `OWNER-DECISION-0006` §6 bullet number a refusal class belongs to, for the operator-facing refusal.
///
/// Bullet 2 covers two classes ("creation **or approval** of new Human Gates"), so this is an explicit mapping and
/// not a position in [`REFUSED_ACTIVITIES`].
pub fn refusal_bullet(class: &str) -> u8 {
    match class {
        "normal_privileged_operation" => 1,
        "human_gate_create" | "human_gate_approve" => 2,
        "release_certification" => 3,
        "trust_policy_mutation" => 4,
        "privileged_plugin_acquisition" => 5,
        "floor_lower_or_reset" => 6,
        "present_below_floor_release_as_current" => 7,
        _ => 1,
    }
}

/// The permitted set rendered for an operator-facing refusal message.
fn permitted_summary() -> String {
    PERMITTED_OPERATIONS
        .iter()
        .map(|(label, activity)| format!("`{label}` ({activity})"))
        .collect::<Vec<_>>()
        .join(", ")
}

/// The single refusal, shared by [`guard`], [`guard_light`] and [`guard_effect`] so they can never drift apart.
///
/// `class` is supplied by the caller rather than derived here, because the two enforcement points know it for
/// different reasons: the operation-level guards read it off [`refusal_class`] (reporting only), while
/// [`guard_effect`] already holds the [`Effect`] it was asked to clear, which *is* the class.
fn refuse(class: &'static str, operation: &str, entered_at: &str, record: &Value) -> GovError {
    let bullet = refusal_bullet(class);
    GovError::new(
        "SRR_BELOW_FLOOR_REFUSED",
        format!(
            "'{operation}' is refused: this machine is marked `{DEGRADED_TOKEN}`. Below-floor recovery permits only the OWNER-DECISION-0006 §5 recovery activities and refuses everything else (§6); '{operation}' is refused as {class} (§6 bullet {bullet}). Permitted while below floor: {}. To leave break-glass, {}.",
            permitted_summary(),
            exit_condition_description()
        ),
    )
    .with_details(json!({
        "marking": DEGRADED_TOKEN,
        "operation": operation,
        "refused_class": class,
        "section_6_bullet": bullet,
        "refusal_policy": REFUSAL_POLICY,
        "entered_at": entered_at,
        "permitted": PERMITTED_ACTIVITIES,
        "permitted_operations": PERMITTED_OPERATIONS
            .iter()
            .map(|(l, a)| json!({"operation": l, "section_5_activity": a}))
            .collect::<Vec<_>>(),
        "below_floor_limits": BELOW_FLOOR_LIMITS
            .iter()
            .map(|(l, note)| json!({"operation": l, "limit": note}))
            .collect::<Vec<_>>(),
        "gate_free_restoration_routes": GATE_FREE_RESTORATION_ROUTES,
        "exit_condition": exit_condition_description(),
        "break_glass_record": record,
    }))
}

/// **Refuse when the subject of the §6 decision cannot be determined** (`AR31-B2`).
///
/// [`guard_light`] and [`guard_effect`] are reached from sinks that hold no [`MachineState`], so they resolve the
/// protected state root themselves. Both used to convert a resolution error into a clearance. The comment that
/// justified it named "the ungoverned/unprovisioned case" — and AR-0031 enumerated every input to
/// [`crate::srr::state::resolve_state_root`] and showed that case returns `Ok` and never reaches the branch. The
/// only input that reaches it is `GOV_MACHINE_STATE_DIR` pointing elsewhere on an already-provisioned machine,
/// which is the one input the product has already classified as hostile and refuses. Both enforcement points
/// therefore failed open on precisely that input, together, for all of bullets 1-7.
///
/// `OWNER-DECISION-0006` §6 is a MUST NOT. A check that cannot identify its subject has not established that the
/// subject is unmarked, so it refuses. No legitimate input reaches this path, so failing closed costs nothing.
///
/// The fix is here and nowhere else: machine-state root resolution is owner-closed by `OWNER-DECISION-0007` §1
/// (`AR27-OD1` is out of scope) and [`crate::srr::state::resolve_state_root`] and `default_state_root` are
/// byte-identical across this repair. Only the handling of their error changed.
///
/// [`guard_effect_on`] and [`guard`] cannot reach this: they are handed the [`MachineState`] and resolve nothing,
/// which is why §6 bullet 4 held under the input that opened the others.
fn undetermined_subject(class: &'static str, operation: &str, cause: &GovError) -> GovError {
    GovError::new(
        "SRR_BELOW_FLOOR_SUBJECT_UNDETERMINED",
        format!(
            "'{operation}' is refused: this machine's protected state root could not be resolved, so whether it is marked `{DEGRADED_TOKEN}` cannot be determined ({}: {}). OWNER-DECISION-0006 §6 is a MUST NOT, and a check that cannot identify its subject has not established that the machine is unmarked, so it refuses rather than clears. Unset {} and retry.",
            cause.code,
            cause.message,
            crate::srr::state::ENV_STATE_DIR
        ),
    )
    .with_details(json!({
        "marking": DEGRADED_TOKEN,
        "operation": operation,
        "refused_class": class,
        "section_6_bullet": refusal_bullet(class),
        "subject": "UNDETERMINED",
        "fail": "closed",
        "cause": {"code": cause.code, "message": cause.message},
        "state_root_env": crate::srr::state::ENV_STATE_DIR,
        "exit_condition": exit_condition_description(),
    }))
}

/// A three-valued read of the marking record, so that "present but unreadable" is never silently "not marked".
///
/// **This is the only reader of the marking record in the implementation** (`AR29-C1`). The guards, the effect
/// enforcement point, [`Degraded::load`], [`is_degraded`], `gov trust status`, `gov trust break-glass`,
/// `gov recover` and [`try_exit`] all resolve through it, so no two consumers can hold opposite opinions about
/// whether this machine is marked.
enum Marking {
    /// No marking record at all, or one whose `active` is explicitly `false` (a cleared exit).
    NotMarked,
    /// The machine is marked `DEGRADED — RECOVERY ONLY`.
    Marked(Value),
    /// A marking record exists but cannot be read as one. Refusal is the structural default here too: a machine
    /// whose marking cannot be read is not thereby unmarked.
    ///
    /// Neither half of recovery is blocked by it. **Restoration** stays open because every
    /// [`PERMITTED_OPERATIONS`] entry is allowed before this is ever consulted. **Exit** stays open because
    /// [`Degraded::load`] reads through this same function, so an unreadable record is a `Degraded` value that a
    /// satisfied `OWNER-DECISION-0006` §7 exit rewrites in place — which is what `AR29-C1` found was not true of
    /// the previous arrangement, where `Degraded::load` read the record with the opposite disposition.
    Unreadable,
}

fn read_marking(path: &Path) -> Marking {
    if !path.exists() {
        return Marking::NotMarked;
    }
    let Ok(v) = crate::util::read_json(path) else {
        return Marking::Unreadable;
    };
    match v.get("active").and_then(|x| x.as_bool()) {
        Some(true) => Marking::Marked(v),
        Some(false) => Marking::NotMarked,
        None => Marking::Unreadable,
    }
}

fn entered_at_of(record: &Value) -> String {
    record
        .get("entered_at")
        .and_then(|x| x.as_str())
        .unwrap_or("")
        .to_string()
}

/// **The whole §6 decision**, in one place: is this machine marked, and if so, refuse under `class`.
///
/// Every enforcement point in the implementation ends here — the operation-level [`guard`] and [`guard_light`],
/// and the effect-level [`guard_effect`] / [`guard_effect_on`]. There is exactly one reading of the record
/// ([`read_marking`]) and exactly one refusal ([`refuse`]).
fn decide(path: &Path, class: &'static str, operation: &str) -> Result<()> {
    match read_marking(path) {
        Marking::NotMarked => Ok(()),
        Marking::Marked(v) => Err(refuse(class, operation, &entered_at_of(&v), &v)),
        Marking::Unreadable => Err(refuse(
            class,
            operation,
            "",
            &json!({"unreadable_marking_record": path.display().to_string()}),
        )),
    }
}

/// Cheap `DEGRADED — RECOVERY ONLY` check for the hot path: it resolves the protected state root and reads one
/// file, without creating the state layout. Used by [`crate::orchestration::control::guard_write`], which every
/// mutating governed operation already calls, so `OWNER-DECISION-0006` §6 bullet 1 is enforced at the same
/// chokepoint as `FREEZE_WRITES` rather than at a new one that a code path could forget.
///
/// Identical policy to [`guard`]: both consult [`permitted_activity`] and both refuse through the same private
/// `decide`, so the hot-path guard and the state-carrying guard cannot diverge.
///
/// `AR29-N3`: the marking path is built by [`crate::srr::state::degraded_path_at`], the same function
/// `MachineState::degraded_path` uses. The two used to sanitise the product string differently — identical for
/// the current `FRAMEWORK_NAME`, and a silent total bypass of §6 for any product string containing a character
/// only one of them rewrote.
pub fn guard_light(product: &str, operation: &str) -> Result<()> {
    // The §5 allow-list is consulted first, so a recovery operation needs no state read at all and can never be
    // blocked by a failure to read state.
    if permitted_activity(operation).is_some() {
        return Ok(());
    }
    let root = match crate::srr::state::resolve_state_root() {
        Ok(r) => r,
        // `AR31-B2` — **fail closed on an undetermined subject.** See [`undetermined_subject`].
        Err(e) => return Err(undetermined_subject(refusal_class(operation), operation, &e)),
    };
    decide(
        &degraded_path_at(&root, product),
        refusal_class(operation),
        operation,
    )
}

/// The durable break-glass entry record and current marking for one product.
#[derive(Debug, Clone)]
pub struct Degraded {
    pub product: String,
    pub marking: String,
    pub entered_at: String,
    pub record: Value,
}

impl Degraded {
    /// Load the marking **through the same reader the guards use** (`AR29-C1`).
    ///
    /// A record that exists but cannot be read as one is `Some`, not `None`: the guards refuse on it, so every
    /// other consumer must agree that the machine is marked, and — the part that was actually broken —
    /// [`try_exit`] must be able to *clear* it when the `OWNER-DECISION-0006` §7 exit condition is met. Returning
    /// `None` here meant the exit rewrote nothing and the guard went on refusing for ever, while
    /// `gov trust status` reported `degraded: null`.
    ///
    /// This changes only who reads the record, never the exit **policy**: [`exit_satisfied`] and [`EXIT_POLICY`]
    /// are untouched and remain the single owner-decided exit-floor comparison.
    pub fn load(ms: &MachineState, product: &str) -> Option<Degraded> {
        let path = ms.degraded_path(product);
        match read_marking(&path) {
            Marking::NotMarked => None,
            Marking::Marked(v) => Some(Degraded {
                product: product.to_string(),
                marking: v
                    .get("marking")
                    .and_then(|x| x.as_str())
                    .unwrap_or(DEGRADED_TOKEN)
                    .to_string(),
                entered_at: entered_at_of(&v),
                record: v,
            }),
            Marking::Unreadable => Some(Degraded {
                product: product.to_string(),
                marking: DEGRADED_TOKEN.to_string(),
                entered_at: String::new(),
                record: json!({
                    "active": true,
                    "marking": DEGRADED_TOKEN,
                    "unreadable_marking_record": path.display().to_string(),
                    "note": "This machine's break-glass marking record is present but cannot be read as a record. It is treated as marked by every reader, and a satisfied OWNER-DECISION-0006 §7 exit rewrites it in place.",
                }),
            }),
        }
    }
}

/// Is this machine currently below floor for `product`?
pub fn is_degraded(ms: &MachineState, product: &str) -> bool {
    Degraded::load(ms, product).is_some()
}

/// Refuse an operation while the machine is marked `DEGRADED — RECOVERY ONLY` (OWNER-DECISION-0006 §6 bullet 1).
///
/// **The default is refuse, structurally.** The decision procedure is [`permitted_activity`]: an operation
/// proceeds only when its label appears verbatim in [`PERMITTED_OPERATIONS`] alongside the §5 activity that
/// covers it. Everything else is refused, whether or not anyone anticipated it — which is what it means to refuse
/// "normal privileged Governance OS operation" (§6 bullet 1) as a class rather than as a list of strings.
/// [`REFUSAL_CLASSES`] chooses only which §6 bullet the refusal is *reported* under; it decides nothing.
///
/// This is the *operation*-level point. Bullets 2–7 name effects rather than operations and are enforced by
/// [`guard_effect`] from inside the effect itself; see the module header.
pub fn guard(ms: &MachineState, product: &str, operation: &str) -> Result<()> {
    if permitted_activity(operation).is_some() {
        return Ok(());
    }
    decide(
        &ms.degraded_path(product),
        refusal_class(operation),
        operation,
    )
}

// ------------------------------------------- OWNER-DECISION-0006 §6 bullets 2-7 : the effect enforcement point

/// The effects `OWNER-DECISION-0006` §6 forbids below floor, one variant per named effect.
///
/// An effect is not an operation. `gov trust root-update` is an operation that performs
/// [`Effect::TrustPolicyMutation`]; `update --apply` is an *allow-listed* operation that would perform
/// [`Effect::HumanGateCreate`] on its way to a §5 restoration. §6 binds the effect in both cases.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Effect {
    /// Bullet 1 — normal privileged Governance OS operation. Decided by [`guard`] / [`guard_light`].
    NormalPrivilegedOperation,
    /// Bullet 2 — creation of a new Human Gate.
    HumanGateCreate,
    /// Bullet 2 — approval of a new Human Gate.
    HumanGateApprove,
    /// Bullet 3 — release certification.
    ReleaseCertification,
    /// Bullet 4 — trust-policy mutation.
    TrustPolicyMutation,
    /// Bullet 5 — privileged plugin/profile acquisition.
    PrivilegedPluginAcquisition,
    /// Bullet 6 — lowering or resetting the signed security floor / high-water.
    FloorLowerOrReset,
    /// Bullet 7 — treating the below-floor release as current or fully trusted.
    PresentBelowFloorReleaseAsCurrent,
}

impl Effect {
    /// The `OWNER-DECISION-0006` §6 activity name this effect is refused as. Always in [`REFUSED_ACTIVITIES`].
    pub fn activity(&self) -> &'static str {
        match self {
            Effect::NormalPrivilegedOperation => "normal_privileged_operation",
            Effect::HumanGateCreate => "human_gate_create",
            Effect::HumanGateApprove => "human_gate_approve",
            Effect::ReleaseCertification => "release_certification",
            Effect::TrustPolicyMutation => "trust_policy_mutation",
            Effect::PrivilegedPluginAcquisition => "privileged_plugin_acquisition",
            Effect::FloorLowerOrReset => "floor_lower_or_reset",
            Effect::PresentBelowFloorReleaseAsCurrent => "present_below_floor_release_as_current",
        }
    }
    /// The §6 bullet number.
    pub fn bullet(&self) -> u8 {
        refusal_bullet(self.activity())
    }
}

/// **The §6 sink census.** For each §6 bullet, the primitive in this product that realises the effect, and
/// therefore the place the enforcement point has to sit.
///
/// **This table is a summary, not the coverage claim.** Three R1 iterations failed because a *declared*
/// enumeration stood in for a universal negative and went silently short as soon as the product grew a path its
/// author had not enumerated: first the list of forbidden operations, then the set of guarded call sites, then
/// this census. The coverage claim now lives in [`SECTION_6_SIGNATURES`], which is **derived from the product's
/// own source** by `section_6_coverage_is_derived_from_the_product`: every function in `runtime/src` and
/// `cli/src` is examined, and any function that performs a durable write and matches an effect's signature must
/// carry that effect's enforcement. This table exists so a reader can see the answer; the derivation is what
/// checks it.
///
/// No entry claims "no primitive exists" any more. Bullets 6 and 7 used to, and both claims were unfalsifiable by
/// the product's own suite (`AR31-N5`) — which is exactly how `AR31-B1` survived repair 2. Both now have real
/// sinks. The mechanism that makes an absence claim refutable is kept anyway, for the next bullet that needs one:
/// see [`SECTION_6_SIGNATURES`].
pub const SECTION_6_SINKS: &[(&str, &str)] = &[
    (
        "normal_privileged_operation",
        "crate::orchestration::control::guard_write",
    ),
    (
        "human_gate_create",
        "crate::records::save_record (every write of a `human-gate` record, however the Record was minted) + crate::orchestration::gates::build (compiler-enforced &Clearance, inside gates.rs)",
    ),
    ("human_gate_approve", "crate::orchestration::gates::answer"),
    ("release_certification", "crate::release::build"),
    (
        "trust_policy_mutation",
        "crate::srr::state::MachineState::set_root_metadata",
    ),
    (
        "privileged_plugin_acquisition",
        "crate::srr::plugins::guard_acquisition + crate::tools::install — both capability-registry writers ask, unconditionally",
    ),
    (
        "floor_lower_or_reset",
        "crate::srr::state::Floors::save — the only writer of floors/<product>.json, monotonic against the persisted value",
    ),
    (
        "present_below_floor_release_as_current",
        "crate::srr::present::presentation — reached by every command result the CLI emits, and by doctor, update --check and the agent context packet directly",
    ),
];

/// **The §6 effect signatures — the coverage claim, in a form the product can be measured against.**
///
/// Each entry is `(activity, signature markers, acceptance markers)`.
///
/// * **signature markers** name the product's own primitives that an implementation of the effect must use: the
///   record-type table, the protected path builders, the capability registries, the command-result envelope. A
///   function that performs a durable write and mentions one of these is *derived* to be a place the effect can
///   happen — whether or not anyone remembered to put it in [`SECTION_6_SINKS`].
/// * **acceptance markers** are what makes such a function acceptable: it carries the effect's enforcement call,
///   or it reaches the sink that does.
///
/// `section_6_coverage_is_derived_from_the_product` walks **every** function in `runtime/src` and `cli/src`,
/// computes the derived set, and fails naming any function in it that carries no acceptance marker. Nothing is on
/// a list of "places to look": the function set comes from the tree.
///
/// **How a "no primitive exists" claim can now fail.** An entry may legitimately derive to the empty set — that
/// is what "no primitive realises this effect" means. Such a claim is only worth anything if the detector behind
/// it can detect a primitive, so the test first runs each signature against a **positive control**: a synthetic
/// implementation of that effect, written the way a future author plausibly would. A signature that fails to
/// match its positive control fails the test, whatever it then finds (or does not find) in the product. An
/// absence claim is therefore the *most* tested case rather than a loop the test silently skips (`AR31-N5`).
///
/// **What this cannot see**, stated plainly because three roles in this lineage overstated a universal property
/// and every overstatement was later falsified:
///
/// * an implementation that reaches the effect without using any of the product's own primitives — writing
///   `trust/root.json` with a hand-built path and `std::fs::write`, say. The path-literal markers below catch the
///   obvious spellings and nothing catches a computed one.
/// * anything outside `runtime/src` and `cli/src`.
/// * a caller that is *given* a value rather than deriving it: a `&Clearance` handed across a function boundary
///   is accepted at the boundary, not re-derived.
/// * dynamic dispatch, macro-generated code, and any string assembled at run time.
///
/// **A cost of this mechanism, stated so it is not mistaken for a defect.** The markers below are string literals,
/// and they name the product's own primitives. A *file-level* grep census — "which files mention
/// `root_metadata_path`, `guard_acquisition`, `floors_path`?" — will therefore now also count this file. Such a
/// census must exclude [`SECTION_6_SIGNATURES`]; the derived census in the certification suite is unaffected,
/// because it examines function bodies and these are module-level constants inside none.
/// * the marking on a non-CLI consumer: the command-result envelope covers every `gov` command including ones not
///   yet written, but an in-process embedder of `gov_runtime` that calls a reporting function directly gets the
///   marking only from the surfaces that carry it themselves.
pub const SECTION_6_SIGNATURES: &[(&str, &[&str], &[&str])] = &[
    (
        "normal_privileged_operation",
        &["control::guard_write(", "guard_write(p,", "guard_write(&p"],
        &["guard_write(", "breakglass::guard_light"],
    ),
    (
        "human_gate_create",
        &["save_record(", "record_path_for(", "record_dir_for("],
        &[
            "Effect::HumanGateCreate",
            "guarded_record_effect(",
            "save_record(",
            "_clearance: &crate::srr::breakglass::Clearance",
        ],
    ),
    (
        "human_gate_approve",
        &["json!(\"ANSWERED\")", "\"gate_status\", json!(\"ANSWERED\")"],
        &["Effect::HumanGateApprove"],
    ),
    (
        "release_certification",
        &["certification_status", "\"certification\": {\"status\""],
        &["Effect::ReleaseCertification"],
    ),
    (
        "trust_policy_mutation",
        &[
            "root_metadata_path(",
            "provisioned_path(",
            "join(\"root.json\")",
            "join(\"provisioned.json\")",
        ],
        &["Effect::TrustPolicyMutation", "set_root_metadata("],
    ),
    (
        "privileged_plugin_acquisition",
        &["join(\"plugins\")", "join(\"tools\")", "guard_acquisition"],
        &["Effect::PrivilegedPluginAcquisition", "guard_acquisition"],
    ),
    (
        "floor_lower_or_reset",
        &["floors_path(", "join(\"floors\")"],
        &["floor_lower_or_reset", "raise_metadata(", "raise_release(", "raise_minimum_secure("],
    ),
    (
        "present_below_floor_release_as_current",
        &["\"command\": name", "\"ok\": true, \"command\""],
        &[
            "Effect::PresentBelowFloorReleaseAsCurrent",
            "present::attach(",
            "present::presentation(",
        ],
    ),
];

/// **What counts as performing a durable write**, derived rather than assumed.
///
/// The derived census asks two questions of every function: does it match an effect's signature, and does it
/// write anything durable. This is the second question. A function that matches a signature but writes nothing
/// cannot realise the effect — it is a reader, a path builder or a report — so it is not a violation.
///
/// These are the product's own persistence primitives. The certification suite proves the list non-vacuous by
/// running it against a positive control, the same way it proves each signature.
pub const SECTION_6_WRITE_PRIMITIVES: &[&str] = &[
    "write_durable(",
    "std::fs::write(",
    "fs::write(",
    "std::fs::rename(",
    "File::create(",
    "write_yaml(",
    "write_text(",
    "write_json(",
    "save_record(",
    ".save(",
    "write_all(",
    "println!",
    "print!",
];

/// **Functions the derivation finds and that are not violations, each with the reason.**
///
/// This is not a list of places to look — the derivation is complete over `runtime/src` and `cli/src` and this
/// list is what it *found*. The signatures deliberately over-approximate, because a universal negative is better
/// served by a detector that is too eager than by one that is too narrow, and an over-eager detector needs
/// somewhere for the justified cases to be written down.
///
/// The difference from the enumerations that failed three times is the direction of the obligation. Those listed
/// where the effect could happen, and went short when the product grew a path nobody listed. This lists
/// exceptions *after* derivation: a new match cannot appear silently, because the census fails until someone
/// writes the reason here. `section_6_coverage_is_derived_from_the_product` additionally fails when an entry here
/// no longer matches its signature, so an exemption cannot rot into a blanket after the code it excused has
/// moved.
pub const SECTION_6_DERIVATION_EXEMPTIONS: &[(&str, &str, &str)] = &[(
    "human_gate_create",
    "runtime/src/cit/mod.rs::take_snapshot",
    "computes a record's own canonical path (`record_path_for`) in order to COPY that record into a CIT rollback snapshot. It mints no record, and every byte it writes goes to the snapshot directory, never to a record path. The two CIT ops that do reach a record path — `append_record` and `write_file` — pass `save_record` and the §6 record-type check respectively.",
)];

/// The reason `path::function` is exempt from `activity`'s derived census, or `None` if it is not exempt.
pub fn derivation_exemption(activity: &str, site: &str) -> Option<&'static str> {
    SECTION_6_DERIVATION_EXEMPTIONS
        .iter()
        .find(|(a, s, _)| *a == activity && *s == site)
        .map(|(_, _, why)| *why)
}

/// The signature and acceptance markers declared for `activity`, or `None` when the census does not name it.
pub fn section_6_signature(activity: &str) -> Option<(&'static [&'static str], &'static [&'static str])> {
    SECTION_6_SIGNATURES
        .iter()
        .find(|(a, _, _)| *a == activity)
        .map(|(_, sig, acc)| (*sig, *acc))
}

/// **Record types whose persistence is itself an `OWNER-DECISION-0006` §6 effect.**
///
/// `AR31-N3`: the bullet-2 creation guarantee was a property of `gates.rs`, not of the product.
/// [`crate::orchestration::gates::build`] is private and takes a sealed [`Clearance`], so no new gate-raising
/// function *inside that module* compiles without asking §6 — but `records::new_record`, `records::save_record`
/// and every field of `Record` are `pub`, and AR-0031 minted a `human-gate` record three ways with no
/// `Clearance` in existence. One of those three (a non-literal type argument) is invisible to **any** source
/// scan, so a source-literal census cannot close it.
///
/// The effect is therefore enforced where the effect happens. However a `Record` is minted, it becomes durable
/// only through [`crate::records::save_record`], and that function asks §6 for every type named here. The
/// compiler-enforced `&Clearance` on `gates::build` is kept as well: the two are complementary, one binding new
/// code inside `gates.rs` at compile time and one binding every writer in the product at the instant of the write.
pub const GUARDED_RECORD_TYPES: &[(&str, Effect)] = &[("human-gate", Effect::HumanGateCreate)];

/// The §6 effect that persisting a record of type `rtype` realises, or `None` when persistence is not a §6 effect.
pub fn guarded_record_effect(rtype: &str) -> Option<Effect> {
    GUARDED_RECORD_TYPES
        .iter()
        .find(|(t, _)| *t == rtype)
        .map(|(_, e)| *e)
}

/// **A sealed witness that [`guard_effect`] was consulted for one effect and did not refuse it.**
///
/// The fields are private and there is no public constructor, no `Clone`, no `Copy` and no `Default`, so a value
/// of this type cannot come into existence anywhere except inside this module — not by a struct literal, not by
/// functional-update syntax, not from another crate. A function that takes a `&Clearance` therefore cannot be
/// called at all without the §6 decision having run: the *compiler* puts the enforcement point on the path, not a
/// convention and not a reviewer's memory.
///
/// It is deliberately **not** how the trust-policy and release-certification sinks are gated. Those call
/// [`guard_effect`] themselves, at the instant of the effect, because a token passed in from a caller is a
/// decision taken at some earlier moment; the check inside the sink is the decision taken *now*. The witness is
/// used where a sink has a small, fixed set of in-module wrappers ([`crate::orchestration::gates::build`]) and the
/// type system can carry the proof the last few lines without opening a time-of-use gap.
#[derive(Debug)]
pub struct Clearance {
    effect: Effect,
    operation: String,
}

impl Clearance {
    /// The only constructor, private to this module and reachable only from [`guard_effect_on`].
    fn issue(effect: Effect, operation: &str) -> Clearance {
        Clearance {
            effect,
            operation: operation.to_string(),
        }
    }
    pub fn effect(&self) -> Effect {
        self.effect
    }
    pub fn operation(&self) -> &str {
        &self.operation
    }
}

/// **THE `OWNER-DECISION-0006` §6 bullets 2–7 enforcement point**, state-carrying form.
///
/// Called from inside the primitive that performs `effect` (see [`SECTION_6_SINKS`]), so every path that reaches
/// the effect passes it — including paths written after this code, which is what makes §6 a property of the
/// effect rather than of a list of callers somebody has to maintain.
///
/// **There is no allow-list exception here.** [`PERMITTED_OPERATIONS`] is the §5 exception to bullet 1 and to
/// bullet 1 only. Bullets 2–7 are MUST NOTs that bind *inside* a permitted operation exactly as they bind outside
/// one — the live case being `update --apply`, which is permitted as restoration and still may not create a Human
/// Gate to get there (`AR29-N4`, [`BELOW_FLOOR_LIMITS`]). [`Effect::NormalPrivilegedOperation`] is accepted for
/// completeness and is the one variant that does consult the allow-list, so that the two enforcement points state
/// one policy between them.
pub fn guard_effect_on(
    ms: &MachineState,
    product: &str,
    effect: Effect,
    operation: &str,
) -> Result<Clearance> {
    if effect == Effect::NormalPrivilegedOperation && permitted_activity(operation).is_some() {
        return Ok(Clearance::issue(effect, operation));
    }
    decide(&ms.degraded_path(product), effect.activity(), operation)?;
    Ok(Clearance::issue(effect, operation))
}

/// [`guard_effect_on`] for a sink that holds no [`MachineState`], resolving the protected state root the same way
/// [`guard_light`] does and, since `AR31-B2`, failing **closed** on the same undetermined subject for the same
/// reason ([`undetermined_subject`]).
///
/// The marking is always written and read under [`crate::FRAMEWORK_NAME`] — `enter` writes
/// `degraded/<product>.json` for the product the break-glass token binds, and `authorise` refuses a token whose
/// product is not this one — so that is the product this resolves.
pub fn guard_effect(effect: Effect, operation: &str) -> Result<Clearance> {
    if effect == Effect::NormalPrivilegedOperation && permitted_activity(operation).is_some() {
        return Ok(Clearance::issue(effect, operation));
    }
    let root = match crate::srr::state::resolve_state_root() {
        Ok(r) => r,
        // `AR31-B2` — **fail closed on an undetermined subject.** See [`undetermined_subject`].
        Err(e) => return Err(undetermined_subject(effect.activity(), operation, &e)),
    };
    decide(
        &degraded_path_at(&root, crate::FRAMEWORK_NAME),
        effect.activity(),
        operation,
    )?;
    Ok(Clearance::issue(effect, operation))
}

// ------------------------------------------------------------------- SRR2-R1-C1 : the single exit policy point

/// **`SRR2-R1-C1` / `GATE-OWNER-R1-BREAK-GLASS-EXIT` — THE break-glass exit policy point.**
///
/// This function is the *only* place in the implementation that decides whether the `DEGRADED — RECOVERY ONLY`
/// marking may be cleared. Nothing else in the codebase compares a release against an exit floor; every caller
/// routes here. The owner's open question is which floor the exit must clear:
///
/// * **(b) stricter, fail-safe — implemented here:** the release must be at or above **both** the signed minimum
///   secure release **and** the protected local high-water.
/// * (a) looser: at or above the signed minimum secure release only, as `OWNER-DECISION-0006` §7 reads literally.
///
/// The orchestrator's interim assumption selects (b) — a machine that has verified release *N* should not be
/// treated as recovered while sitting on *N-1*, because everything between the two floors is exactly the window an
/// attacker wants. It is implemented as **one comparison** so the owner can adopt (a) with a single change:
/// replace `floors.effective_floor_sequence()` with `floors.minimum_secure_sequence` on the line marked below, and
/// change `EXIT_POLICY` to `"a"`. No other code changes, and no other site encodes the choice.
pub const EXIT_POLICY: &str = "b_stricter_both_floors";

pub fn exit_satisfied(release_version: &str, release_sequence: u64, floors: &Floors) -> bool {
    // SRR2-R1-C1 / GATE-OWNER-R1-BREAK-GLASS-EXIT — the two lines below are the whole policy. To adopt reading
    // (a), replace them with `floors.minimum_secure_sequence` and `floors.minimum_secure_release.clone()` and set
    // EXIT_POLICY to "a_signed_minimum_only". Nothing else in the codebase encodes this choice.
    let required_sequence = floors.effective_floor_sequence();
    let required_version = floors.effective_floor_version();
    release_sequence >= required_sequence
        && (required_version.is_empty()
            || crate::lock::compare_versions(release_version, &required_version)
                != std::cmp::Ordering::Less)
}

pub fn exit_condition_description() -> String {
    format!(
        "install and verify an authenticated release at or above BOTH the signed minimum secure release AND the protected local high-water (SRR2-R1-C1 policy `{EXIT_POLICY}`, GATE-OWNER-R1-BREAK-GLASS-EXIT); the marking is then cleared automatically"
    )
}

// ---------------------------------------------------------------------------------------------- authorisation

/// Locate and verify an owner-signed break-glass authorisation for this machine (OWNER-DECISION-0006 §2, §10).
///
/// Every input is local: the inbox directory inside protected machine state, the trusted root metadata, and the
/// local clock. **No network or code-hosting access is consulted**, so recovery works on an isolated machine.
///
/// What cannot produce a valid authorisation:
/// * repository content — the inbox is outside every repository and the signature is over owner-held key material;
/// * environment variables — [`super::state::refuse_authority_env`] refuses them outright, and no env var is read here;
/// * caller fields / CLI flags — `--break-glass` only *requests* below-floor admission; this function supplies the
///   authority, and refuses if no valid token exists;
/// * plugins or model output — neither can mint a `recovery`-role signature;
/// * the running binary itself — it holds no signing key, so a below-floor or revoked binary cannot self-authorise.
pub struct Authorisation {
    pub token: BreakGlassToken,
    pub path: PathBuf,
}

pub fn authorise(
    ms: &MachineState,
    root: &crate::srr::metadata::Root,
    product: &str,
    now: &str,
) -> Result<Authorisation> {
    if !root.has_role(crate::srr::metadata::ROLE_RECOVERY) {
        return Err(GovError::new(
            "SRR_BREAK_GLASS_NO_AUTHORITY",
            "the trusted root delegates no `recovery` role, so no below-floor break-glass authorisation can exist on this machine (OWNER-DECISION-0006 §2)",
        ));
    }
    let inbox = ms.break_glass_inbox();
    let mut entries: Vec<PathBuf> = std::fs::read_dir(&inbox)
        .map(|rd| {
            rd.filter_map(|e| e.ok())
                .map(|e| e.path())
                .filter(|p| p.is_file() && p.extension().map(|x| x == "json").unwrap_or(false))
                .collect()
        })
        .unwrap_or_default();
    entries.sort();
    if entries.is_empty() {
        return Err(GovError::new(
            "SRR_BREAK_GLASS_NOT_AUTHORISED",
            format!("below-floor recovery requires an owner-signed break-glass authorisation. None was found in {} (OWNER-DECISION-0006 §2: the authority is owner-controlled and out of band; it cannot come from repository content, environment variables, caller fields, plugins or model output).", inbox.display()),
        )
        .with_details(json!({"inbox": inbox.display().to_string(), "machine_id": ms.machine_id})));
    }
    let mut rejected: Vec<Value> = vec![];
    for path in entries {
        let env = match crate::srr::metadata::Envelope::read(&path) {
            Ok(e) => e,
            Err(e) => {
                rejected.push(json!({"path": path.display().to_string(), "reason": e.message}));
                continue;
            }
        };
        // Signed by the owner's offline `recovery` role, at threshold.
        if let Err(e) = root.verify_role(crate::srr::metadata::ROLE_RECOVERY, &env) {
            rejected.push(json!({"path": path.display().to_string(), "reason": e.message}));
            continue;
        }
        let token = match BreakGlassToken::parse(env) {
            Ok(t) => t,
            Err(e) => {
                rejected.push(json!({"path": path.display().to_string(), "reason": e.message}));
                continue;
            }
        };
        if token.product != product {
            rejected.push(json!({"path": path.display().to_string(), "reason": format!("binds product '{}', not '{product}'", token.product)}));
            continue;
        }
        // Bound to this exact machine: a token issued for one machine cannot be copied to another.
        if token.machine_id != ms.machine_id {
            rejected.push(json!({"path": path.display().to_string(), "reason": "binds a different machine_id"}));
            continue;
        }
        if let Some(fault) = token.envelope.expiry_fault(now) {
            rejected.push(json!({"path": path.display().to_string(), "reason": fault}));
            continue;
        }
        // Single use: a spent nonce cannot be replayed into a second entry.
        if ms
            .break_glass_consumed()
            .join(format!("{}.json", nonce_file(&token.nonce)))
            .exists()
        {
            rejected.push(
                json!({"path": path.display().to_string(), "reason": "nonce already consumed"}),
            );
            continue;
        }
        return Ok(Authorisation { token, path });
    }
    Err(GovError::new(
        "SRR_BREAK_GLASS_NOT_AUTHORISED",
        format!("no valid owner-signed break-glass authorisation for this machine was found in {} ({} candidate(s) rejected)", inbox.display(), rejected.len()),
    )
    .with_details(json!({"machine_id": ms.machine_id, "rejected": rejected})))
}

fn nonce_file(nonce: &str) -> String {
    crate::util::sha256_text(nonce)[..32].to_string()
}

/// Enter break-glass: consume the authorisation, write the durable entry record and mark the machine.
///
/// The record carries everything `OWNER-DECISION-0006` §3 asks for where available: machine identity, the current
/// signed security floor and protected high-water, the recovery release identity, the reason and a
/// timestamp/evidence reference.
///
/// **§8 — no floor is written here.** This function never touches `floors/<product>.json`. It records that the
/// machine is knowingly operating beneath its floors; it does not move them.
#[allow(clippy::too_many_arguments)]
pub fn enter(
    ms: &MachineState,
    auth: &Authorisation,
    floors: &Floors,
    recovery_release_version: &str,
    recovery_sequence: u64,
    payload_hash: &str,
    kernel_manifest_hash: &str,
    ingress: &str,
) -> Result<Value> {
    // SRR2-R1-C2: the authorisation must name the digests actually being installed, not just a version.
    let hash_ok = (!auth.token.recovery_payload_hash.is_empty()
        && auth.token.recovery_payload_hash == payload_hash)
        || (!auth.token.recovery_kernel_manifest_hash.is_empty()
            && auth.token.recovery_kernel_manifest_hash == kernel_manifest_hash);
    if !hash_ok {
        return Err(GovError::new(
            "SRR_BREAK_GLASS_WRONG_PAYLOAD",
            format!(
                "the break-glass authorisation binds a different recovery payload (SRR2-R1-C2). Authorised payload_hash={} kernel_manifest_hash={}; measured payload_hash={payload_hash} kernel_manifest_hash={kernel_manifest_hash}.",
                auth.token.recovery_payload_hash, auth.token.recovery_kernel_manifest_hash
            ),
        )
        .with_details(json!({
            "authorised": {"payload_hash": auth.token.recovery_payload_hash, "kernel_manifest_hash": auth.token.recovery_kernel_manifest_hash, "release_version": auth.token.recovery_release_version},
            "measured": {"payload_hash": payload_hash, "kernel_manifest_hash": kernel_manifest_hash, "release_version": recovery_release_version},
        })));
    }
    let record = json!({
        "active": true,
        "marking": DEGRADED_TOKEN,
        "entered_at": now_iso(),
        "product": auth.token.product,
        "machine_id": ms.machine_id,
        "ingress": ingress,
        "reason": auth.token.reason,
        "authorisation": {
            "nonce": auth.token.nonce,
            "issued": auth.token.issued,
            "expires": auth.token.expires,
            "source": auth.path.display().to_string(),
            "token_sha256": auth.token.envelope.file_sha256,
        },
        "floors_at_entry": {
            "signed_minimum_secure_release": floors.minimum_secure_release,
            "signed_minimum_secure_sequence": floors.minimum_secure_sequence,
            "protected_release_high_water": floors.release_high_water_version,
            "protected_release_high_water_sequence": floors.release_high_water_sequence,
            "metadata_high_water": floors.metadata_high_water,
        },
        "recovery_release": {
            "release_version": recovery_release_version,
            "sequence": recovery_sequence,
            "payload_hash": payload_hash,
            "kernel_manifest_hash": kernel_manifest_hash,
        },
        "permitted_activities": PERMITTED_ACTIVITIES,
        "permitted_operations": PERMITTED_OPERATIONS
            .iter()
            .map(|(l, a)| json!({"operation": l, "section_5_activity": a}))
            .collect::<Vec<_>>(),
        "refusal_policy": REFUSAL_POLICY,
        "refused_activities": REFUSED_ACTIVITIES,
        "below_floor_limits": BELOW_FLOOR_LIMITS
            .iter()
            .map(|(l, note)| json!({"operation": l, "limit": note}))
            .collect::<Vec<_>>(),
        "section_6_enforcement": {
            "bullet_1": "operation level: crate::orchestration::control::guard_write -> breakglass::guard_light, a default-refuse allow-list",
            "bullets_2_to_7": "effect level: breakglass::guard_effect, called from inside the primitive that performs the effect",
            "sinks": SECTION_6_SINKS.iter().map(|(a, s)| json!({"activity": a, "sink": s})).collect::<Vec<_>>(),
        },
        "exit_condition": exit_condition_description(),
        "exit_policy": EXIT_POLICY,
        "floors_unchanged": "OWNER-DECISION-0006 §8: break-glass records that the machine is operating beneath its floors; it does not lower, reset or forget them.",
    });
    write_durable(&ms.degraded_path(&auth.token.product), &record)?;
    // Consume the nonce only after the entry record is durable, so a crash can never spend an authorisation
    // without leaving the record that OWNER-DECISION-0006 §3 requires.
    write_durable(
        &ms.break_glass_consumed()
            .join(format!("{}.json", nonce_file(&auth.token.nonce))),
        &json!({"nonce": auth.token.nonce, "consumed_at": now_iso(), "machine_id": ms.machine_id, "product": auth.token.product}),
    )?;
    let _ = std::fs::remove_file(&auth.path);
    Ok(record)
}

/// Clear the marking when, and only when, [`exit_satisfied`] holds for the release just installed and verified.
///
/// Returns the cleared record, or `None` if the machine was not marked. Refuses (leaving the marking in place) if
/// the exit policy is not satisfied.
pub fn try_exit(
    ms: &MachineState,
    product: &str,
    release_sequence: u64,
    release_version: &str,
    authenticated: bool,
    floors: &Floors,
) -> Result<Option<Value>> {
    let Some(d) = Degraded::load(ms, product) else {
        return Ok(None);
    };
    // OWNER-DECISION-0006 §7 and §1: the exit release must be authenticated, never merely present.
    if !authenticated {
        return Ok(Some(
            json!({"cleared": false, "reason": "the installed release is not authenticated; break-glass exit requires an authenticated release", "marking": DEGRADED_TOKEN}),
        ));
    }
    if !exit_satisfied(release_version, release_sequence, floors) {
        return Ok(Some(json!({
            "cleared": false,
            "reason": exit_condition_description(),
            "marking": DEGRADED_TOKEN,
            "release": {"version": release_version, "sequence": release_sequence},
            "required_sequence": floors.effective_floor_sequence(),
            "signed_minimum_secure_sequence": floors.minimum_secure_sequence,
            "protected_release_high_water_sequence": floors.release_high_water_sequence,
            "exit_policy": EXIT_POLICY,
        })));
    }
    let mut rec = d.record.clone();
    rec["active"] = json!(false);
    rec["cleared_at"] = json!(now_iso());
    rec["cleared_by_release"] = json!({"version": release_version, "sequence": release_sequence});
    rec["exit_policy"] = json!(EXIT_POLICY);
    write_durable(&ms.degraded_path(product), &rec)?;
    Ok(Some(json!({"cleared": true, "record": rec})))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn degraded_marking_is_byte_exact_with_an_em_dash() {
        // OWNER-DECISION-0006 §4 requires this exact string.
        assert_eq!(DEGRADED_TOKEN.as_bytes(), DEGRADED_TOKEN_BYTES);
        assert!(
            DEGRADED_TOKEN.contains('\u{2014}'),
            "separator must be U+2014 EM DASH"
        );
        assert!(!DEGRADED_TOKEN.contains('-'), "must not be a hyphen-minus");
        assert!(
            !DEGRADED_TOKEN.contains('\u{2013}'),
            "must not be an en dash"
        );
        assert_eq!(DEGRADED_TOKEN.len(), 26); // 24 chars, em dash is 3 bytes
    }

    /// `AR27-B1` — §6 bullet 1 names a CLASS, so refusal must be the structural default. Anything not on the
    /// §5 allow-list is refused, including labels nobody enumerated when this was written.
    #[test]
    fn below_floor_refusal_is_structural_not_an_enumeration() {
        assert_eq!(REFUSAL_POLICY, "allow_list_default_refuse");
        for label in [
            // the seven AR-0027 measured as permitted with no §5 cover
            "cit approve",
            "cit reject",
            "gate revoke",
            "handoff return",
            "plugins unregister",
            "adopt extract-legacy",
            "adopt build-memory",
            // two more that mutate governed state despite read-sounding names
            "task status",
            "cit simulate",
            // labels that did not exist when this table was written
            "an operation invented after this repair",
            "",
            "quorum override",
            // near-misses on allow-listed labels: exact match, never substring or case folding
            "kernel reinstall --force",
            "KERNEL REINSTALL",
            "checkpoint delete",
            "update --apply-unverified",
        ] {
            assert!(
                permitted_activity(label).is_none(),
                "'{label}' must not be permitted while the machine is marked `{DEGRADED_TOKEN}`"
            );
        }
    }

    #[test]
    fn every_permitted_operation_names_a_real_section_5_activity() {
        for (label, activity) in PERMITTED_OPERATIONS {
            assert!(
                PERMITTED_ACTIVITIES.contains(activity),
                "'{label}' claims §5 activity '{activity}', which OWNER-DECISION-0006 §5 does not name"
            );
            assert_eq!(permitted_activity(label), Some(*activity));
        }
        // §7 and §10: the way out of break-glass must stay open, offline, on a marked machine.
        for must in ["kernel reinstall", "update --apply", "update --rollback"] {
            assert!(
                permitted_activity(must).is_some(),
                "'{must}' is how a machine restores an authenticated release and leaves break-glass"
            );
        }
    }

    #[test]
    fn refusal_classes_report_a_section_6_bullet_but_decide_nothing() {
        // A specifically named operation is reported under its own bullet ...
        assert_eq!(refusal_class("gate create"), "human_gate_create");
        assert_eq!(refusal_class("release certify"), "release_certification");
        assert_eq!(refusal_class("trust root-update"), "trust_policy_mutation");
        // ... and everything else under §6 bullet 1, which is why membership cannot be load-bearing.
        assert_eq!(
            refusal_class("an operation invented after this repair"),
            "normal_privileged_operation"
        );
        assert_eq!(refusal_class("cit approve"), "normal_privileged_operation");
        for (_, class) in REFUSAL_CLASSES {
            assert!(
                REFUSED_ACTIVITIES.contains(class),
                "'{class}' is not an OWNER-DECISION-0006 §6 activity"
            );
        }
    }

    /// `AR29-B1` / `AR29-B2` — the §6 bullets 2–7 effect enforcement point has **no allow-list exception**.
    ///
    /// The allow-list is the §5 exception to bullet 1. An operation that is permitted below floor is still
    /// forbidden the named effects, which is the whole of the `update --apply` case: permitted as restoration,
    /// refused at the Human Gate it would have to create.
    #[test]
    fn a_named_section_6_effect_has_no_allow_list_exception() {
        let dir = std::env::temp_dir().join(format!("bg-effect-{}", crate::util::short_uuid()));
        let ms = MachineState::at(&dir).unwrap();
        let product = "p";
        write_durable(
            &ms.degraded_path(product),
            &json!({"active": true, "marking": DEGRADED_TOKEN, "entered_at": "2026-01-01T00:00:00Z"}),
        )
        .unwrap();

        // bullet 1 keeps its §5 exception, at both the operation guard and the effect point
        assert!(guard(&ms, product, "update --apply").is_ok());
        assert!(guard_effect_on(
            &ms,
            product,
            Effect::NormalPrivilegedOperation,
            "update --apply"
        )
        .is_ok());

        // bullets 2-7 do not, whatever operation label is presented — including an allow-listed one
        for effect in [
            Effect::HumanGateCreate,
            Effect::HumanGateApprove,
            Effect::ReleaseCertification,
            Effect::TrustPolicyMutation,
            Effect::PrivilegedPluginAcquisition,
            Effect::FloorLowerOrReset,
            Effect::PresentBelowFloorReleaseAsCurrent,
        ] {
            for label in ["update --apply", "kernel reinstall", "checkpoint", "anything"] {
                let e = guard_effect_on(&ms, product, effect, label).unwrap_err();
                assert_eq!(e.code, "SRR_BELOW_FLOOR_REFUSED");
                assert_eq!(e.details["refused_class"], effect.activity());
                assert_eq!(e.details["section_6_bullet"], effect.bullet());
            }
        }

        // and on an unmarked machine every effect clears
        std::fs::remove_file(ms.degraded_path(product)).unwrap();
        for effect in [Effect::TrustPolicyMutation, Effect::HumanGateCreate] {
            let c = guard_effect_on(&ms, product, effect, "x").unwrap();
            assert_eq!(c.effect(), effect);
            assert_eq!(c.operation(), "x");
        }
        let _ = std::fs::remove_dir_all(&dir);
    }

    /// Every §6 activity has a declared sink and every sink names a §6 activity, so the census cannot silently
    /// lose a bullet.
    #[test]
    fn every_section_6_activity_has_exactly_one_declared_sink() {
        assert_eq!(SECTION_6_SINKS.len(), REFUSED_ACTIVITIES.len());
        for a in REFUSED_ACTIVITIES {
            assert_eq!(
                SECTION_6_SINKS.iter().filter(|(x, _)| x == a).count(),
                1,
                "§6 activity '{a}' must have exactly one declared sink"
            );
        }
        for (activity, sink) in SECTION_6_SINKS {
            assert!(REFUSED_ACTIVITIES.contains(activity));
            assert!(!sink.is_empty());
        }
        // the enum and the activity names are one vocabulary
        for effect in [
            Effect::NormalPrivilegedOperation,
            Effect::HumanGateCreate,
            Effect::HumanGateApprove,
            Effect::ReleaseCertification,
            Effect::TrustPolicyMutation,
            Effect::PrivilegedPluginAcquisition,
            Effect::FloorLowerOrReset,
            Effect::PresentBelowFloorReleaseAsCurrent,
        ] {
            assert!(REFUSED_ACTIVITIES.contains(&effect.activity()));
            assert!((1..=7).contains(&effect.bullet()));
        }
    }

    /// `AR29-N5` — the reserved names are inert, report a real §6 bullet, and are disjoint from the live table.
    #[test]
    fn reserved_refusal_classes_are_inert_and_disjoint() {
        for (label, class) in RESERVED_REFUSAL_CLASSES {
            assert!(
                REFUSED_ACTIVITIES.contains(class),
                "'{class}' is not an OWNER-DECISION-0006 §6 activity"
            );
            assert!(
                permitted_activity(label).is_none(),
                "'{label}' is both refusal-classified and permitted"
            );
            assert!(
                !REFUSAL_CLASSES.iter().any(|(l, _)| l == label),
                "'{label}' is in both tables"
            );
        }
        // reporting only: a reserved name is refused exactly as an unnamed one is
        assert_eq!(refusal_class("release certify"), "release_certification");
        assert_eq!(refusal_class("trust root-update"), "trust_policy_mutation");
        assert_eq!(refusal_class("gate create"), "human_gate_create");
        assert_eq!(refusal_class("nothing at all"), "normal_privileged_operation");
    }

    /// `AR29-N4` — every limit named applies to an operation the allow-list actually permits, so the table cannot
    /// drift into describing something that is not on offer.
    #[test]
    fn below_floor_limits_describe_allow_listed_operations() {
        for (label, note) in BELOW_FLOOR_LIMITS {
            assert!(
                permitted_activity(label).is_some(),
                "'{label}' carries a below-floor limit but is not on the allow-list"
            );
            assert!(note.len() > 40, "'{label}' needs a usable explanation");
        }
        for route in GATE_FREE_RESTORATION_ROUTES {
            assert!(
                permitted_activity(route).is_some(),
                "'{route}' is offered as a way out of break-glass but is not permitted below floor"
            );
        }
    }

    /// `AR29-C1` — one reader. An unreadable record is marked for the guard *and* for `Degraded::load`, and a
    /// satisfied §7 exit rewrites it instead of silently doing nothing.
    #[test]
    fn the_marking_record_has_exactly_one_reader() {
        let dir = std::env::temp_dir().join(format!("bg-reader-{}", crate::util::short_uuid()));
        let ms = MachineState::at(&dir).unwrap();
        let product = "p";
        let mut floors = Floors {
            product: product.into(),
            ..Default::default()
        };
        floors.raise_release("4.1.5", 15, true);

        std::fs::write(ms.degraded_path(product), b"{\"active\": tr").unwrap();
        assert!(guard(&ms, product, "cit approve").is_err());
        assert!(
            is_degraded(&ms, product),
            "the guard refuses as marked, so every other reader must agree"
        );
        // the exit is open, not merely the restore path
        let exit = try_exit(&ms, product, 16, "4.1.6", true, &floors)
            .unwrap()
            .expect("an unreadable marking is a marking");
        assert_eq!(exit["cleared"], true);
        assert!(!is_degraded(&ms, product));
        assert!(guard(&ms, product, "cit approve").is_ok());
        let _ = std::fs::remove_dir_all(&dir);
    }

    /// `AR31-B2` — the guards fail **closed** when they cannot determine their subject, and the refusal says so
    /// rather than borrowing the vocabulary of a machine known to be marked.
    #[test]
    fn an_undetermined_subject_refuses_and_says_which_it_is() {
        let cause = GovError::new("SRR_PROTECTED_STATE_OVERRIDE_REFUSED", "relocated");
        let e = undetermined_subject("human_gate_create", "gate create", &cause);
        assert_eq!(e.code, "SRR_BELOW_FLOOR_SUBJECT_UNDETERMINED");
        assert_eq!(e.details["subject"], "UNDETERMINED");
        assert_eq!(e.details["fail"], "closed");
        assert_eq!(e.details["refused_class"], "human_gate_create");
        assert_eq!(e.details["section_6_bullet"], 2);
        assert_eq!(e.details["cause"]["code"], "SRR_PROTECTED_STATE_OVERRIDE_REFUSED");
        // the operator is told what to do about it, not merely that it happened
        assert!(e.message.contains(crate::srr::state::ENV_STATE_DIR));
        assert!(!e.details["exit_condition"].as_str().unwrap_or("").is_empty());
    }

    /// The allow-list is consulted before any state is resolved, so a §5 recovery operation can never be blocked
    /// by the fail-closed path: restoration stays available on a machine whose state root will not resolve.
    #[test]
    fn failing_closed_never_blocks_a_section_5_restoration_route() {
        for route in ["kernel reinstall", "update --apply", "update --rollback", "checkpoint"] {
            assert!(
                permitted_activity(route).is_some(),
                "'{route}' must be decided by the allow-list before any state read"
            );
        }
    }

    /// `AR31-N3` — the record-write sink dispatches on the record TYPE, which is what all three of AR-0031's
    /// constructions produce, rather than on a source literal that two of them do not spell.
    #[test]
    fn a_guarded_record_type_is_recognised_however_the_record_was_minted() {
        assert_eq!(guarded_record_effect("human-gate"), Some(Effect::HumanGateCreate));
        assert_eq!(guarded_record_effect("task"), None);
        assert_eq!(guarded_record_effect(""), None);
        for (rtype, effect) in GUARDED_RECORD_TYPES {
            assert!(REFUSED_ACTIVITIES.contains(&effect.activity()));
            assert!(
                crate::records::record_dir_for(rtype).is_ok(),
                "'{rtype}' is guarded but is not a record type this product has"
            );
        }
        let computed: &str = "human-gate";
        let r = crate::records::new_record(computed, "HDG-0001", "t", json!({}));
        assert_eq!(guarded_record_effect(&r.rtype()), Some(Effect::HumanGateCreate));
        let mut retyped = crate::records::new_record("task", "TASK-0001", "t", json!({}));
        retyped.set("type", json!("human-gate"));
        assert_eq!(
            guarded_record_effect(&retyped.rtype()),
            Some(Effect::HumanGateCreate)
        );
    }

    /// `AR31-N5` / `OWNER-DECISION-0008` mandate parts 3 and 4 — the census is derived and no bullet is excused.
    ///
    /// The behaviour is measured by `section_6_coverage_is_derived_from_the_product` in the certification suite,
    /// which needs the source tree. This asserts the shape the derivation depends on, where it is cheapest to
    /// notice that it has gone.
    #[test]
    fn every_section_6_bullet_has_a_derivation_signature_and_none_claims_an_absence() {
        assert_eq!(SECTION_6_SIGNATURES.len(), REFUSED_ACTIVITIES.len());
        for a in REFUSED_ACTIVITIES {
            let (sig, acc) = section_6_signature(a)
                .unwrap_or_else(|| panic!("§6 activity '{a}' has no derivation signature"));
            assert!(!sig.is_empty(), "'{a}' has an empty signature: it would derive nothing");
            assert!(!acc.is_empty(), "'{a}' has no acceptance marker: everything would be a violation");
            for m in sig.iter().chain(acc.iter()) {
                assert!(!m.trim().is_empty(), "'{a}' has a blank marker, which matches everything");
            }
        }
        for (activity, sink) in SECTION_6_SINKS {
            assert!(
                !sink.starts_with("no primitive"),
                "§6 '{activity}' claims no primitive exists; that claim must be carried by a signature that                  derives nothing while still flagging its positive control, not by a sink string"
            );
        }
        assert!(!SECTION_6_WRITE_PRIMITIVES.is_empty());
        for (activity, site, why) in SECTION_6_DERIVATION_EXEMPTIONS {
            assert!(REFUSED_ACTIVITIES.contains(activity));
            assert!(site.contains("::"), "an exemption names a path::function");
            assert!(why.len() > 60, "'{site}' needs a usable reason");
            assert_eq!(derivation_exemption(activity, site), Some(*why));
        }
        assert_eq!(derivation_exemption("human_gate_create", "nowhere::nothing"), None);
    }

    #[test]
    fn exit_requires_both_floors_under_the_stricter_policy() {
        let mut f = Floors {
            product: "p".into(),
            ..Default::default()
        };
        f.raise_minimum_secure("4.1.2", 12, "x");
        f.raise_release("4.1.5", 15, true);
        assert_eq!(EXIT_POLICY, "b_stricter_both_floors");
        // above the signed minimum but below the protected high-water: refused under (b)
        assert!(!exit_satisfied("4.1.3", 13, &f));
        // at the high-water: accepted
        assert!(exit_satisfied("4.1.5", 15, &f));
        assert!(exit_satisfied("4.1.6", 16, &f));
        // below both: refused
        assert!(!exit_satisfied("4.1.1", 11, &f));
    }
}
