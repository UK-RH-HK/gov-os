//! `SRR-R0-L6` — built-in/local capabilities versus remotely acquired privileged plugins, tools and profiles.
//!
//! The R0 reviewer recorded (AR-0023, A-08) that `tools`/`plugins`/`skills` are "a deliberately separate trust
//! domain under frozen-boundary R0 item 11 and Contract v3 F2/F3/F4", and the owner deferred the distinction to
//! R1 via `OWNER-DECISION-0005` §2. This module makes it concrete.
//!
//! ## The distinction
//!
//! | class | where the bytes come from | what authorises them | delegated signed target |
//! |---|---|---|---|
//! | [`Acquisition::BuiltIn`] | inside the verified release payload | the release/targets digests already cover every byte | not needed, and not consulted |
//! | [`Acquisition::LocalProject`] | authored in the governed project | kernel-owned registration, pins and `TOOL_POLICY`; a descriptor never self-authorises | not applicable |
//! | [`Acquisition::RemotelyAcquired`] | fetched from outside this machine | kernel registration **and**, when privileged, a delegation in the verified release metadata | **required** |
//!
//! The rule the classes exist to enforce: **a privileged capability whose bytes came from outside the verified
//! release payload and outside the governed project must be authorised by a delegated signed target in the release
//! metadata.** Nothing in a descriptor — including `provenance`, `security_review: passed` or a `source` field —
//! can move a capability into a weaker class, because the class is derived from where the bytes actually are, not
//! from what the descriptor says about itself.
//!
//! This is layered *on top of* the existing plugin controls (registration, pin digests, permission classes, Human
//! Gates); it replaces none of them. ARCH-0003 §9: "Descriptors cannot self-authorise."
use crate::srr::metadata::Delegation;
use crate::util::glob_match;
use crate::{GovError, Result};
use serde_json::{json, Value};
use std::path::Path;

/// Permission classes that make a capability *privileged* for the purposes of this rule.
pub const PRIVILEGED_PERMISSION_CLASSES: &[&str] = &[
    "SYSTEM_INSTALL",
    "SECRET_READ",
    "DEPLOY_PRODUCTION",
    "NETWORK_EGRESS",
    "REPO_WRITE",
    "CREDENTIAL_USE",
];

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Acquisition {
    /// Shipped inside the verified kernel payload. Its bytes are covered by the release payload digests.
    BuiltIn,
    /// Authored inside the governed project and governed by kernel-owned registration and policy.
    LocalProject,
    /// Obtained from outside this machine.
    RemotelyAcquired,
}

impl Acquisition {
    pub fn as_str(&self) -> &'static str {
        match self {
            Acquisition::BuiltIn => "BUILT_IN",
            Acquisition::LocalProject => "LOCAL_PROJECT",
            Acquisition::RemotelyAcquired => "REMOTELY_ACQUIRED",
        }
    }
}

/// Classify by **where the bytes are**, never by what the descriptor claims about itself.
pub fn classify(
    project_root: &Path,
    kernel_dir: &Path,
    implementation: Option<&Path>,
) -> Acquisition {
    let Some(impl_path) = implementation else {
        // No local implementation path resolved: the bytes are not on this machine under our control.
        return Acquisition::RemotelyAcquired;
    };
    let abs = impl_path
        .canonicalize()
        .unwrap_or_else(|_| impl_path.to_path_buf());
    let kernel = kernel_dir
        .canonicalize()
        .unwrap_or_else(|_| kernel_dir.to_path_buf());
    if abs.starts_with(&kernel) {
        return Acquisition::BuiltIn;
    }
    let proj = project_root
        .canonicalize()
        .unwrap_or_else(|_| project_root.to_path_buf());
    if abs.starts_with(&proj) {
        return Acquisition::LocalProject;
    }
    Acquisition::RemotelyAcquired
}

pub fn is_privileged(descriptor: &Value) -> bool {
    descriptor
        .get("required_permission_classes")
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter().any(|x| {
                x.as_str()
                    .map(|s| PRIVILEGED_PERMISSION_CLASSES.contains(&s))
                    .unwrap_or(false)
            })
        })
        .unwrap_or(false)
}

/// Does a delegated signed target in the verified release metadata authorise this capability?
///
/// A delegation matches when its `paths` glob the capability id and, when the delegation binds a channel, that
/// channel equals the channel of the release that carried it (`SRR-R0-L2`).
pub fn delegation_for<'a>(
    delegations: &'a [Delegation],
    capability_id: &str,
    release_channel: &str,
) -> Option<&'a Delegation> {
    delegations.iter().find(|d| {
        if let Some(c) = d.channel.as_deref() {
            if c != release_channel {
                return false;
            }
        }
        d.threshold > 0
            && !d.keyids.is_empty()
            && d.paths
                .iter()
                .any(|p| glob_match(p, capability_id) || p == capability_id)
    })
}

/// Fail closed when a **privileged, remotely acquired** capability has no delegated signed target.
///
/// Built-in capabilities are covered by the release payload digests; local-project capabilities keep the existing
/// kernel-owned controls. Only the third class needs a delegation, and it is refused without one.
///
/// **The `OWNER-DECISION-0006` §6 bullet 5 sink.** Every capability acquisition decision in the product resolves
/// here, so the below-floor refusal sits here too rather than beside the two operations (`plugins register`,
/// `tools install`) that happen to reach it today.
pub fn guard_acquisition(
    capability_id: &str,
    descriptor: &Value,
    acquisition: Acquisition,
    delegations: &[Delegation],
    release_channel: &str,
) -> Result<Value> {
    let privileged = is_privileged(descriptor);
    if privileged {
        crate::srr::breakglass::guard_effect(
            crate::srr::breakglass::Effect::PrivilegedPluginAcquisition,
            "plugin acquisition",
        )?;
    }
    let verdict = json!({
        "capability": capability_id,
        "acquisition_class": acquisition.as_str(),
        "privileged": privileged,
        "release_channel": release_channel,
    });
    if acquisition != Acquisition::RemotelyAcquired || !privileged {
        return Ok(verdict);
    }
    match delegation_for(delegations, capability_id, release_channel) {
        Some(d) => {
            let mut v = verdict;
            v["delegated_target"] = json!({"name": d.name, "threshold": d.threshold, "keys": d.keyids.len(), "paths": d.paths, "channel": d.channel});
            Ok(v)
        }
        None => Err(GovError::new(
            "SRR_PLUGIN_NOT_DELEGATED",
            format!("'{capability_id}' is a privileged capability acquired from outside this machine and outside the verified release payload. Such a capability must be authorised by a delegated signed target in the verified release metadata (SRR-R0-L6); none matches it. A descriptor cannot authorise itself."),
        )
        .with_details(json!({
            "capability": capability_id, "acquisition_class": acquisition.as_str(),
            "required_permission_classes": descriptor.get("required_permission_classes").cloned().unwrap_or(Value::Null),
            "available_delegations": delegations.iter().map(|d| json!({"name": d.name, "paths": d.paths, "channel": d.channel})).collect::<Vec<_>>(),
            "remedy": "ship the capability inside the release payload, author it in the governed project, or publish a delegated signed target for it",
        }))),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_privileged_remote_capability_without_a_delegation_is_refused() {
        let d = json!({"required_permission_classes": ["SYSTEM_INSTALL"]});
        let e = guard_acquisition(
            "acme/scanner",
            &d,
            Acquisition::RemotelyAcquired,
            &[],
            "stable",
        )
        .unwrap_err();
        assert_eq!(e.code, "SRR_PLUGIN_NOT_DELEGATED");
    }

    #[test]
    fn built_in_and_local_capabilities_need_no_delegation() {
        let d = json!({"required_permission_classes": ["SYSTEM_INSTALL"]});
        assert!(guard_acquisition("k/x", &d, Acquisition::BuiltIn, &[], "stable").is_ok());
        assert!(guard_acquisition("p/x", &d, Acquisition::LocalProject, &[], "stable").is_ok());
        // an unprivileged remote capability is also allowed by this rule (other controls still apply)
        let u = json!({"required_permission_classes": ["READ_ONLY"]});
        assert!(guard_acquisition("r/x", &u, Acquisition::RemotelyAcquired, &[], "stable").is_ok());
    }

    #[test]
    fn a_matching_delegation_admits_a_privileged_remote_capability_on_its_own_channel() {
        let d = json!({"required_permission_classes": ["SYSTEM_INSTALL"]});
        let del = vec![Delegation {
            name: "partners".into(),
            keyids: vec!["k1".into()],
            threshold: 1,
            paths: vec!["acme/*".into()],
            channel: Some("stable".into()),
        }];
        assert!(guard_acquisition(
            "acme/scanner",
            &d,
            Acquisition::RemotelyAcquired,
            &del,
            "stable"
        )
        .is_ok());
        // wrong channel: the delegation does not apply (SRR-R0-L2)
        assert!(guard_acquisition(
            "acme/scanner",
            &d,
            Acquisition::RemotelyAcquired,
            &del,
            "beta"
        )
        .is_err());
    }
}
