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
//! | 6 | refused activities | [`guard`] / [`guard_light`] — a **default-refuse allow-list** ([`REFUSAL_POLICY`]): every operation outside [`PERMITTED_OPERATIONS`] is refused, so §6 bullet 1 is enforced as a class rather than as an enumeration. [`REFUSED_ACTIVITIES`] and [`REFUSAL_CLASSES`] only name which bullet a refusal is reported under |
//! | 7 | exit condition | [`exit_satisfied`] — the single `SRR2-R1-C1` policy point |
//! | 8 | the floor itself is never lowered | [`enter`] writes no floor; `Floors::raise_*` are monotonic-only |
//! | 9 | ingress consistency | the floor check lives in the one verifier every ingress calls |
//! | 10| works with no network | every check here reads local files only |
use crate::srr::metadata::BreakGlassToken;
use crate::srr::state::{write_durable, Floors, MachineState};
use crate::util::now_iso;
use crate::{GovError, Result};
use serde_json::{json, Value};
use std::path::PathBuf;

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
pub const REFUSAL_CLASSES: &[(&str, &str)] = &[
    ("gate create", "human_gate_create"),
    ("gate present", "human_gate_create"),
    ("gate answer", "human_gate_approve"),
    ("decide", "human_gate_approve"),
    ("release build", "release_certification"),
    ("release certify", "release_certification"),
    ("certify", "release_certification"),
    ("trust provision", "trust_policy_mutation"),
    ("trust root-update", "trust_policy_mutation"),
    ("trust revoke", "trust_policy_mutation"),
    ("policy set", "trust_policy_mutation"),
    ("plugin install", "privileged_plugin_acquisition"),
    ("plugin acquire", "privileged_plugin_acquisition"),
    ("plugins register", "privileged_plugin_acquisition"),
    ("tools install", "privileged_plugin_acquisition"),
    ("skills install", "privileged_plugin_acquisition"),
    ("floor", "floor_lower_or_reset"),
];

/// The §6 bullet a refusal of `operation` is reported under. Bullet 1 is the default for everything else.
pub fn refusal_class(operation: &str) -> &'static str {
    for (needle, class) in REFUSAL_CLASSES {
        if operation.contains(needle) {
            return class;
        }
    }
    "normal_privileged_operation"
}

/// The permitted set rendered for an operator-facing refusal message.
fn permitted_summary() -> String {
    PERMITTED_OPERATIONS
        .iter()
        .map(|(label, activity)| format!("`{label}` ({activity})"))
        .collect::<Vec<_>>()
        .join(", ")
}

/// The single refusal, shared by [`guard`] and [`guard_light`] so the two can never drift apart.
fn refuse(operation: &str, entered_at: &str, record: &Value) -> GovError {
    let class = refusal_class(operation);
    GovError::new(
        "SRR_BELOW_FLOOR_REFUSED",
        format!(
            "'{operation}' is refused: this machine is marked `{DEGRADED_TOKEN}`. Below-floor recovery permits only the OWNER-DECISION-0006 §5 recovery activities and refuses everything else (§6); '{operation}' is refused as {class}. Permitted while below floor: {}. To leave break-glass, {}.",
            permitted_summary(),
            exit_condition_description()
        ),
    )
    .with_details(json!({
        "marking": DEGRADED_TOKEN,
        "operation": operation,
        "refused_class": class,
        "refusal_policy": REFUSAL_POLICY,
        "entered_at": entered_at,
        "permitted": PERMITTED_ACTIVITIES,
        "permitted_operations": PERMITTED_OPERATIONS
            .iter()
            .map(|(l, a)| json!({"operation": l, "section_5_activity": a}))
            .collect::<Vec<_>>(),
        "exit_condition": exit_condition_description(),
        "break_glass_record": record,
    }))
}

/// A three-valued read of the marking record, so that "present but unreadable" is never silently "not marked".
enum Marking {
    /// No marking record at all, or one whose `active` is explicitly `false` (a cleared exit).
    NotMarked,
    /// The machine is marked `DEGRADED — RECOVERY ONLY`.
    Marked(Value),
    /// A marking record exists but cannot be read as one. Refusal is the structural default here too: a machine
    /// whose marking cannot be read is not thereby unmarked. Recovery is unaffected, because every
    /// [`PERMITTED_OPERATIONS`] entry is allowed before this is ever consulted, so the exit path stays open.
    Unreadable,
}

fn read_marking(path: &std::path::Path) -> Marking {
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

/// Cheap `DEGRADED — RECOVERY ONLY` check for the hot path: it resolves the protected state root and reads one
/// file, without creating the state layout. Used by [`crate::orchestration::control::guard_write`], which every
/// mutating governed operation already calls, so `OWNER-DECISION-0006` §6 is enforced at the same chokepoint as
/// `FREEZE_WRITES` rather than at a new one that a code path could forget.
///
/// Identical policy to [`guard`]: both consult [`permitted_activity`] and both refuse through the same private
/// `refuse`, so the hot-path guard and the state-carrying guard cannot diverge.
pub fn guard_light(product: &str, operation: &str) -> Result<()> {
    // The §5 allow-list is consulted first, so a recovery operation needs no state read at all and can never be
    // blocked by a failure to read state.
    if permitted_activity(operation).is_some() {
        return Ok(());
    }
    let Ok(root) = crate::srr::state::resolve_state_root() else {
        // No protected machine state resolves here, so there is no marking on this machine to enforce: the
        // ungoverned/unprovisioned case, not a degraded one. `resolve_state_root` is used exactly as it stands;
        // this repair does not change how machine-state paths are resolved (AR27-OD1 is out of scope).
        return Ok(());
    };
    let path = root
        .join("degraded")
        .join(format!("{}.json", product.replace(['/', '\\'], "_")));
    match read_marking(&path) {
        Marking::NotMarked => Ok(()),
        Marking::Marked(v) => Err(refuse(operation, &entered_at_of(&v), &v)),
        Marking::Unreadable => Err(refuse(
            operation,
            "",
            &json!({"unreadable_marking_record": path.display().to_string()}),
        )),
    }
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
    pub fn load(ms: &MachineState, product: &str) -> Option<Degraded> {
        let v = crate::util::read_json(&ms.degraded_path(product)).ok()?;
        if !v.get("active").and_then(|x| x.as_bool()).unwrap_or(false) {
            return None;
        }
        Some(Degraded {
            product: product.to_string(),
            marking: v
                .get("marking")
                .and_then(|x| x.as_str())
                .unwrap_or(DEGRADED_TOKEN)
                .to_string(),
            entered_at: v
                .get("entered_at")
                .and_then(|x| x.as_str())
                .unwrap_or("")
                .to_string(),
            record: v,
        })
    }
}

/// Is this machine currently below floor for `product`?
pub fn is_degraded(ms: &MachineState, product: &str) -> bool {
    Degraded::load(ms, product).is_some()
}

/// Refuse an operation while the machine is marked `DEGRADED — RECOVERY ONLY` (OWNER-DECISION-0006 §6).
///
/// **The default is refuse, structurally.** The decision procedure is [`permitted_activity`]: an operation
/// proceeds only when its label appears verbatim in [`PERMITTED_OPERATIONS`] alongside the §5 activity that
/// covers it. Everything else is refused, whether or not anyone anticipated it — which is what it means to refuse
/// "normal privileged Governance OS operation" (§6 bullet 1) as a class rather than as a list of strings.
/// [`REFUSAL_CLASSES`] chooses only which §6 bullet the refusal is *reported* under; it decides nothing.
pub fn guard(ms: &MachineState, product: &str, operation: &str) -> Result<()> {
    if permitted_activity(operation).is_some() {
        return Ok(());
    }
    let path = ms.degraded_path(product);
    match read_marking(&path) {
        Marking::NotMarked => Ok(()),
        Marking::Marked(v) => Err(refuse(operation, &entered_at_of(&v), &v)),
        Marking::Unreadable => Err(refuse(
            operation,
            "",
            &json!({"unreadable_marking_record": path.display().to_string()}),
        )),
    }
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
