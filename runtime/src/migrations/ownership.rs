//! What the Governance OS itself owns in a repository.
//!
//! Adoption must never classify, plan or retire the OS's own installed or generated state as legacy governance
//! (BC-P2-33; Contract v3:874 "mark old governance LEGACY" — current governance is not old governance; :191 every
//! material artefact classified by current path, class, authority and intended target; adoption protocol A0 "detect
//! interrupted prior governance work"). Re-running adoption stages on a repository that already carries the OS
//! (after an interrupted or remediated adoption) is an anticipated path, not an edge case.
//!
//! Ownership is established from the installation's own records, not from file names: the lock and kernel manifest
//! establish an install; the adapter manifest lists the generated outputs (wherever an adapter writes them) with the
//! hash they were generated with. A file merely *named* like an OS output is not exempt unless an install or an
//! adapter manifest vouches for it.
use crate::util::{read_json, sha256_file};
use std::collections::BTreeMap;
use std::path::Path;

/// The adoption evidence tree (protocol §5). Written by `gov adopt`; never legacy.
pub const ADOPTION_EVIDENCE_PREFIX: &str = "spec/audits/GOVERNANCE-ADOPTION/";
/// The installed OS layout under the governance root.
pub const OS_LAYOUT_PREFIXES: &[&str] = &[
    "governance/kernel/",
    "governance/project/",
    "governance/generated/",
    "governance/tests/",
];
pub const OS_LOCK: &str = "governance/framework.lock";
/// Derived path-map projection `adapters::generate` writes at the repository root.
pub const OS_ROOT_PROJECTION: &str = "framework.json";

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Ownership {
    /// kernel, overlay, lock or OS test state of a verified install
    Installed,
    /// an adapter output (or the root projection) listed by the adapter manifest; `intact` = hash still matches
    Generated { intact: bool },
    /// the adoption evidence tree
    Evidence,
    /// OS layout present without a lock/kernel manifest: an interrupted install (A0 PARTIAL_SHOULD_ROLL_BACK)
    UnverifiedLayout,
}

impl Ownership {
    pub fn label(&self) -> &'static str {
        match self {
            Ownership::Installed => "installed",
            Ownership::Generated { .. } => "generated",
            Ownership::Evidence => "adoption_evidence",
            Ownership::UnverifiedLayout => "unverified_layout",
        }
    }
    pub fn reason(&self) -> &'static str {
        match self {
            Ownership::Installed => "installed Governance OS state (kernel, project overlay, lock or OS tests): current governance, never legacy",
            Ownership::Generated { intact: true } => "Governance OS generated output listed in governance/generated/adapter-manifest.json (hash matches): current governance, never legacy",
            Ownership::Generated { intact: false } => "Governance OS generated output listed in governance/generated/adapter-manifest.json, modified since generation (regenerate with `gov adapters generate`): never legacy",
            Ownership::Evidence => "Governance OS adoption evidence tree (written by gov adopt): never legacy",
            Ownership::UnverifiedLayout => "Governance OS layout without framework.lock/kernel manifest (interrupted install, A0 PARTIAL_SHOULD_ROLL_BACK): recovered or rewritten by batch 0, never archived as legacy",
        }
    }
}

#[derive(Debug, Clone, Default)]
pub struct OsState {
    pub installed: bool,
    /// output path -> sha256 recorded at generation ("" when the manifest records none)
    pub generated_outputs: BTreeMap<String, String>,
}

impl OsState {
    pub fn load(root: &Path) -> OsState {
        let installed = root.join(OS_LOCK).is_file()
            && root
                .join("governance/kernel")
                .join(crate::kernel::KERNEL_MANIFEST)
                .is_file();
        let mut generated_outputs = BTreeMap::new();
        // An output is the OS's only when the *installed kernel* declares an adapter writing it and the adapter
        // manifest records it: a planted manifest alone cannot exempt a legacy file from classification.
        if installed {
            let mut declared: std::collections::BTreeSet<String> = Default::default();
            if let Ok(rd) = std::fs::read_dir(root.join("governance/kernel/adapters")) {
                for e in rd.filter_map(|e| e.ok()) {
                    if let Ok(meta) = crate::util::read_yaml(&e.path().join("adapter.yaml")) {
                        if let Some(o) = meta["output"].as_str() {
                            declared.insert(o.trim_start_matches("./").to_string());
                        }
                    }
                }
            }
            if let Ok(m) = read_json(&root.join("governance/generated/adapter-manifest.json")) {
                if let Some(a) = m["adapters"].as_object() {
                    for v in a.values() {
                        if let Some(o) = v["output"].as_str() {
                            let o = o.trim_start_matches("./").to_string();
                            if declared.contains(&o) {
                                generated_outputs
                                    .insert(o, v["hash"].as_str().unwrap_or("").to_string());
                            }
                        }
                    }
                }
                generated_outputs.insert(OS_ROOT_PROJECTION.to_string(), String::new());
            }
        }
        OsState {
            installed,
            generated_outputs,
        }
    }

    /// The OS's claim on `rel`, if any.
    pub fn owner_of(&self, root: &Path, rel: &str) -> Option<Ownership> {
        let rel = rel.trim_start_matches("./");
        if rel.starts_with(ADOPTION_EVIDENCE_PREFIX) {
            return Some(Ownership::Evidence);
        }
        if let Some(h) = self.generated_outputs.get(rel) {
            let intact = h.is_empty()
                || sha256_file(&root.join(rel))
                    .map(|x| &x == h)
                    .unwrap_or(false);
            return Some(Ownership::Generated { intact });
        }
        let layout = rel == OS_LOCK || OS_LAYOUT_PREFIXES.iter().any(|p| rel.starts_with(p));
        if layout {
            return Some(if self.installed {
                if rel.starts_with("governance/generated/") {
                    Ownership::Generated { intact: true }
                } else {
                    Ownership::Installed
                }
            } else {
                Ownership::UnverifiedLayout
            });
        }
        None
    }

    pub fn owns(&self, root: &Path, rel: &str) -> bool {
        self.owner_of(root, rel).is_some()
    }
}
