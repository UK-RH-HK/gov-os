//! # Signed Release Root v1 (`SRR-1`) — implementation of the R0-accepted `ARCH-0003`
//!
//! ```text
//! trusted platform/admin bootstrap
//!   -> bootstrap verifier + public root metadata      (state::MachineState, provision)
//!   -> signed root/delegation metadata                (metadata::Root, accept_root_succession)
//!   -> signed release/targets + snapshot + timestamp  (metadata::{Release,Snapshot,Timestamp})
//!   -> ONE verifier for init/adopt/update/reinstall/rollback/recovery  (verifier::admit)
//!   -> private verified-byte staging                  (staging::stage)
//!   -> atomic commit + protected monotonic high-water (staging::commit_tree, verifier::record_installed)
//!   -> separate installed-kernel integrity            (crate::kernel_trust — D-0007, NOT this module)
//! ```
//!
//! ## Three predicates, three sources — kept apart on purpose
//!
//! The R0 rejection turned on conflating these, so they are separate types with separate sources here:
//!
//! | predicate | means | established by | lives in |
//! |---|---|---|---|
//! | **intact** | the local copy is unmodified | payload ↔ `KERNEL_MANIFEST.json` ↔ `framework.lock.kernel_manifest_hash`, and — where this machine recorded what it committed into the project — payload ↔ that protected record, by digest (`BC-P2-35`) | [`crate::kernel_trust`] (D-0007, ACTIVE, text unchanged) |
//! | **authentic** | the bytes are an authorised release | signed metadata chaining to the machine's root anchor, or this machine's own protected record of what it previously verified | [`verifier::Authenticity`] |
//! | **admissible** | it may be installed now | at or above both protected floors | [`verifier::AuthenticatedRelease::below_floor`] |
//!
//! D-0007's records establish only that a copy is *intact*. They never establish that it is *authentic*, and they
//! never establish that it is *admissible*. Nothing in this module reads them, and nothing in `kernel_trust` reads
//! signed metadata.
//!
//! ## Deployment envelope
//!
//! Private, locally hosted, owner-operated, private repositories. No public SaaS, multi-tenant or cloud assumption
//! is made anywhere in this module. R2 ceremonies (production signing, key custody) and R3 high-assurance controls
//! are deliberately absent: `gov` verifies signatures and never creates them.
pub mod binding;
pub mod breakglass;
pub mod crypto;
pub mod installation;
pub mod metadata;
pub mod plugins;
pub mod present;
pub mod provision;
pub mod staging;
pub mod state;
pub mod verifier;

pub use verifier::{
    admit, record_installed, AdmissionRequest, AuthenticatedRelease, Authenticity, Currency,
    Ingress, Posture,
};

use crate::{Result, FRAMEWORK_NAME};
use serde_json::{json, Value};

/// Machine-level trust status: posture, floors, currency, degraded marking.
///
/// Reports unknown things as unknown (frozen R0 item 10). It never claims current global revocation knowledge and
/// never claims knowledge of revocations that do not yet exist.
pub fn status() -> Result<Value> {
    let ms = state::MachineState::open()?;
    let now = metadata::local_clock_now();
    let product = FRAMEWORK_NAME;
    let floors = state::Floors::load(&ms, product);
    let installed = state::InstalledRecord::load(&ms, product);
    let degraded = breakglass::Degraded::load(&ms, product);
    let root = verifier::trusted_root(&ms, &now).ok().flatten();
    let root_v = match root.as_ref() {
        Some(r) => json!({
            "version": r.version, "expires": r.expires, "product": r.product,
            "expired_against_local_clock": r.envelope.is_expired(&now),
            "roles": r.roles.iter().map(|(k, v)| (k.clone(), json!({"threshold": v.threshold, "keys": v.keyids.len()}))).collect::<serde_json::Map<_, _>>(),
        }),
        None => Value::Null,
    };
    Ok(json!({
        "machine_id": ms.machine_id,
        "state_root": ms.root.display().to_string(),
        "posture": if ms.is_provisioned() { "PROVISIONED" } else { "UNPROVISIONED" },
        "admission_policy": admission_policy(ms.is_provisioned()),
        "trust_anchor": root_v,
        "provisioned": ms.provisioned_record(),
        "floors": floors.to_value(),
        "installed_release": installed.map(|i| json!({
            "release_version": i.release_version, "sequence": i.sequence, "channel": i.channel,
            "payload_hash": i.payload_hash, "kernel_manifest_hash": i.kernel_manifest_hash,
            "authenticity": i.authenticity, "verified_at": i.verified_at,
        })),
        "currency": {
            "state": "UNKNOWN",
            "basis": "currency is determined per ingress from timestamp/snapshot metadata against the declared local clock; between ingresses this client makes no standing claim",
            "revocation_knowledge": "this client reports only revocations it has received. It claims no knowledge of unseen revocations, and no knowledge of revocations that do not yet exist.",
            "local_clock": now,
            "clock_assumption": "ARCH-0003 §1: the local time source is inside the trusted local boundary. No signed, attested or monotonic time is assumed, required or provided. If the clock is materially wrong, expiry/staleness/currency are wrong in the corresponding direction; no floor is lowered, no unauthorised release is admitted and the verified-byte binding is unaffected.",
        },
        "installations": installations_recorded(&ms, product),
        // P2-ADJ-0002: whether T2 facts this machine writes are sealed under the owner's binding authority (and so
        // honoured on the owner's other provisioned machines) or with a machine-local key
        "t2_binding": binding::status(),
        "degraded": degraded.map(|d| json!({"marking": d.marking, "entered_at": d.entered_at, "record": d.record})),
        "break_glass": {
            "marking": breakglass::DEGRADED_TOKEN,
            "exit_policy": breakglass::EXIT_POLICY,
            "exit_condition": breakglass::exit_condition_description(),
            "authority": "owner-signed `recovery`-role authorisation placed out of band in the protected inbox below; never repository content, environment variables, caller fields, plugins or model output",
            "inbox": ms.break_glass_inbox().display().to_string(),
            "network_required": false,
        },
        "separation": {
            "authentic": "signed release metadata (this module)",
            "intact": "D-0007 installed-kernel integrity (gov kernel trust) — a separate control that establishes only that a local copy is unmodified",
            "admissible": "the floor check in the one verification policy",
        },
    }))
}

/// What this machine admits at a privileged lifecycle ingress, in its posture (OWNER-DECISION-P2-0002).
fn admission_policy(provisioned: bool) -> Value {
    if provisioned {
        json!({
            "policy": "signed_release_metadata_at_every_ingress",
            "admits": "releases authorised by signed release metadata chaining to this machine's trust anchor (or, offline, a release this machine itself verified earlier), at or above its floors",
            "refuses": "unsigned, tampered and below-floor material at every ingress",
        })
    } else {
        json!({
            "policy": verifier::UNPROVISIONED_ADMISSION_POLICY,
            "decision": "OWNER-DECISION-P2-0002",
            "admits": format!("only the payload embedded in this gov binary ({}), as a marked {} installation whose authenticity is UNKNOWN and which is never presented as current, verified or certified", crate::kernel::embedded_payload_hash(), verifier::BOOTSTRAP_MODE),
            "refuses": "kernel material from any external source (init --source, update, adopt, kernel reinstall, rollback, recovery): SRR_UNPROVISIONED_EXTERNAL_SOURCE_REFUSED",
            "remediation": "gov trust provision --anchor <root metadata from the administrator domain>, then install a signed release",
        })
    }
}

/// `BC-P2-36`: every project this machine has installed a kernel into, with what the single verifier decided — so a
/// machine with no trust anchor reports its installations as authenticity `UNKNOWN` instead of reporting nothing,
/// and `installed_release` above stays what it says it is: a release this machine *verified*.
fn installations_recorded(ms: &state::MachineState, product: &str) -> Value {
    let dir = ms.installed_dir(product).join("projects");
    let mut out: Vec<Value> = vec![];
    if let Ok(rd) = std::fs::read_dir(&dir) {
        let mut paths: Vec<std::path::PathBuf> =
            rd.filter_map(|e| e.ok()).map(|e| e.path()).collect();
        paths.sort();
        for p in paths {
            if let Ok(v) = crate::util::read_json(&p) {
                let cur = v.get("current").cloned().unwrap_or(Value::Null);
                out.push(json!({
                    "project_root": v.get("project_root").cloned().unwrap_or(Value::Null),
                    "release_version": cur.get("release_version").cloned().unwrap_or(Value::Null),
                    "payload_hash": cur.get("payload_hash").cloned().unwrap_or(Value::Null),
                    "authenticity": cur.get("authenticity").cloned().unwrap_or(Value::Null),
                    "ingress": cur.get("ingress").cloned().unwrap_or(Value::Null),
                    "admission": cur.get("admission").cloned().unwrap_or(Value::Null),
                    "at": cur.get("at").cloned().unwrap_or(Value::Null),
                    "pending": v.get("pending").map(|x| !x.is_null()).unwrap_or(false),
                }));
            }
        }
    }
    Value::Array(out)
}
