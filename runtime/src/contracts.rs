//! Governance Capability Acceptance Contract v3 — hash-bound source, compiled form, evidence map and generated view.
//!
//! The contract itself says how this must work (repo-root contract, "Contract authority model"):
//!
//! * `framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md` is the **human-approved
//!   normative source**, and the agent "must **not** invent or rewrite its semantics from memory";
//! * `framework/contracts/governance-capability-acceptance.yaml` is the **machine-executable compiled form**;
//! * the runtime consumes the YAML, "but it is valid only when `contract-source.lock` proves that it was
//!   compiled/validated from the exact approved source hash";
//! * "Any semantic difference between source and compiled representation is a hard failure."
//!
//! ## Provenance of the canonical import (logged precedence conflict)
//!
//! `GATE-OWNER-CAC-UPLOAD` was written expecting the owner to copy the approved file into
//! `framework/contracts/source/` once builder scaffolding existed. The owner instead supplied the normative source
//! at the repository root (`Governance_OS_Capability_Acceptance_Contract_v3.md`) and directed that that exact file
//! be used and hash-bound. An active owner directive outranks a frozen gate convention, so:
//!
//! * the **repository-root file is the authoritative owner source**;
//! * `framework/contracts/source/…` is a **builder-produced canonical import**, required to be byte-identical to it;
//! * divergence between the two is a hard failure, not a warning — see [`verify`].
//!
//! ## What is compiled (BC-P2-01)
//!
//! The compiler is a *line-accounting* reader of the approved bytes. It paraphrases nothing: every line of the owner
//! source other than a blank line or a `---` thematic break is carried **verbatim, with its line number, exactly once**
//! in the compiled form, and each carried line is placed in the structure the source gives it:
//!
//! * every gate (`# GATE X — …`) and every capability section (`## X<n>. …`). A gate that states its checklist without
//!   numbered capability headings — Gate U — is itself a capability section whose id is the gate letter (frozen gate
//!   contract §9.4: "It is still a capability section of the owner source");
//! * every checklist item (`- [ ] …`, `N. [ ] …`) with a stable id `<capability>.<n>` and the lead-in it belongs to;
//! * every other line of a section — lead-ins, the qualifiers that complete a list ("persist beyond conversation
//!   lifetime.", "and silent N/A is invalid."), the W10 hard invariant, gate-level prose — with a mechanical kind;
//! * every advanced-qualification challenge, with an id minted from its position (`AQC-<section>`);
//! * the requirement-class label **exactly as the source states it**, and the Contract v3:60 class it denotes. A label
//!   that denotes none of the three classes the source enumerates (Gate V's "NEW TESTING REFINEMENT") is carried
//!   verbatim, not mapped;
//! * every per-capability field of Contract v3:53-73. Where the source states a value (id, title, source reference,
//!   requirement class, challenge ids) the compiled form carries it; where it states none, the compiled form carries the
//!   field as `null` — it may not invent one — and the governed value lives in the evidence map;
//! * the preamble (contract-level definitions and vocabularies) and the closing sections.
//!
//! ## What `verify` proves, and why it is not self-referential
//!
//! Comparing the compiled file with a fresh run of the same compiler proves only that the compiler is deterministic.
//! [`verify`] therefore also checks each derived view against the **source text itself**, with rules that do not use
//! the compiler's parse ([`source_accounting`]): every non-blank line carried verbatim; every checklist line carried as a
//! checklist item inside the section that contains it; every capability heading, every gate and every heading-less
//! gate carried as a capability; every label carried as written. It then compares the compiled form, the source-derived
//! part of the evidence map and the generated view with the owner-source model, field by field, and fails with a typed
//! error naming each difference. The source lock binds every view's digest.
use crate::util::{read_text, sha256_text};
use crate::{GovError, Result};
use regex::Regex;
use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};
use std::sync::OnceLock;

/// The owner-approved normative source at the repository root.
pub const OWNER_SOURCE: &str = "Governance_OS_Capability_Acceptance_Contract_v3.md";
/// The canonical import inside the kernel payload; must be byte-identical to [`OWNER_SOURCE`].
pub const CANONICAL_IMPORT: &str =
    "framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md";
pub const COMPILED: &str = "framework/contracts/governance-capability-acceptance.yaml";
pub const SOURCE_LOCK: &str = "framework/contracts/contract-source.lock";
pub const SCHEMA: &str = "framework/schemas/governance-capability-acceptance.schema.json";
pub const EVIDENCE_MAP: &str = "tests/governance/capability-evidence-map.yaml";
pub const GENERATED_VIEW: &str = "docs/generated/GOVERNANCE_CAPABILITY_ACCEPTANCE.md";

/// The digest the product owner supplied for the approved source, recorded in `GATE-OWNER-CAC-UPLOAD` and in the
/// AR-0026 handoff. Pinning it here means a substituted "approved source" is refused even if every file in the
/// repository were replaced consistently.
pub const OWNER_SOURCE_SHA256: &str =
    "4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3";

/// The approved source as compiled into this binary, for consumers that need the contract universe without a source
/// checkout (the Qualification Oracle validator). [`embedded_model`] refuses it unless it hashes to
/// [`OWNER_SOURCE_SHA256`].
pub const EMBEDDED_SOURCE: &str = include_str!(
    "../../framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md"
);

const CONTRACT_VERSION: &str = "v3";
const COMPILED_SCHEMA_ID: &str = "governance-os.capability-acceptance-contract";
const MAP_SCHEMA_ID: &str = "governance-os.capability-evidence-map";
const LOCK_SCHEMA_ID: &str = "governance-os.contract-source-lock";
/// Version 2 of every derived view: the line-accounting compiled form (version 1 carried headings only).
const DERIVED_VIEW_VERSION: u64 = 2;
/// The value of a governed evidence-map field nobody has mapped yet.
pub const NOT_YET_MAPPED: &str = "NOT_YET_MAPPED";
/// How the owner source introduces an advanced-qualification challenge.
pub const CHALLENGE_PREFIX: &str = "**Advanced qualification challenge:**";
/// A differences list is truncated to this many entries in an error's details (the count is always exact).
const MAX_REPORTED_DIFFERENCES: usize = 200;

/// Where the value of a per-capability field is stated.
pub const STATED_IN_OWNER_SOURCE: &str = "owner_source";
/// A per-capability field the owner source states no capability-specific value for: the governed value lives in the
/// evidence map (populated by governed evidence mapping, never by the compiler).
pub const STATED_IN_EVIDENCE_MAP: &str = "evidence_map";

/// Contract v3:57-73 "Required contract fields per capability", in source order: (the source text without its list
/// marker and trailing punctuation, the key every derived view uses, where the value is stated). The compiler refuses a
/// source whose field list differs from this table, so the table can never silently fall out of step with the source.
pub const CONTRACT_FIELDS: &[(&str, &str, &str)] = &[
    ("stable capability ID", "id", STATED_IN_OWNER_SOURCE),
    ("title/description", "title", STATED_IN_OWNER_SOURCE),
    (
        "source governing-document reference",
        "source_reference",
        STATED_IN_OWNER_SOURCE,
    ),
    (
        "requirement class: `ORIGINAL`, `POST_VERIFICATION_HARDENING`, or `EXECUTION_REFINEMENT`",
        "requirement_class",
        STATED_IN_OWNER_SOURCE,
    ),
    ("severity if violated", "severity", STATED_IN_EVIDENCE_MAP),
    (
        "applicability rule",
        "applicability",
        STATED_IN_EVIDENCE_MAP,
    ),
    (
        "evidence class(es)",
        "evidence_class",
        STATED_IN_EVIDENCE_MAP,
    ),
    (
        "automated check/test IDs",
        "automated_checks",
        STATED_IN_EVIDENCE_MAP,
    ),
    (
        "independent-verification obligation",
        "independent_verification",
        STATED_IN_EVIDENCE_MAP,
    ),
    (
        "evidence-freshness triggers",
        "freshness_triggers",
        STATED_IN_EVIDENCE_MAP,
    ),
    (
        "health-scheduler tier(s) G0–G6",
        "health_scheduler_tiers",
        STATED_IN_EVIDENCE_MAP,
    ),
    (
        "advanced-qualification challenge IDs",
        "qualification_challenge_ids",
        STATED_IN_OWNER_SOURCE,
    ),
    (
        "adoption verification obligation",
        "adoption_obligation",
        STATED_IN_EVIDENCE_MAP,
    ),
    (
        "periodic operational-audit obligation",
        "operational_audit_obligation",
        STATED_IN_EVIDENCE_MAP,
    ),
    (
        "allowed status values",
        "allowed_status",
        STATED_IN_EVIDENCE_MAP,
    ),
    (
        "N/A requirements",
        "na_requirements",
        STATED_IN_EVIDENCE_MAP,
    ),
    (
        "remediation/task-generation rule",
        "remediation_rule",
        STATED_IN_EVIDENCE_MAP,
    ),
];

/// Preamble sections the compiler reads contract-level vocabularies from (headings verbatim).
const FIELDS_SECTION: &str = "## Required contract fields per capability";
const EVIDENCE_CLASSES_SECTION: &str =
    "## Relationship between the contract and the governance suite";
const FRESHNESS_SECTION: &str = "## Evidence freshness";
const LIFECYCLE_SECTION: &str = "## Lifecycle";
/// The capability and lead-in under which the source defines the health-scheduler tiers.
const TIERS_CAPABILITY: &str = "O5";
const TIERS_LEAD_IN: &str = "Tiered checks:";

/// The governed per-capability fields (value stated in the evidence map, not by the owner source).
pub fn governed_fields() -> Vec<&'static str> {
    CONTRACT_FIELDS
        .iter()
        .filter(|f| f.2 == STATED_IN_EVIDENCE_MAP)
        .map(|f| f.1)
        .collect()
}

// ------------------------------------------------------------------------------------------ the owner-source model

/// One carried source line.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct Line {
    pub line: usize,
    pub text: String,
}

/// One checklist item (`- [ ] text` or `N. [ ] text`).
#[derive(Debug, Clone, PartialEq)]
pub struct Item {
    pub id: String,
    pub line: usize,
    pub number: Option<u64>,
    pub text: String,
    /// Line of the lead-in ("Tiered checks:", "Rules:") the item belongs to, when the section has one.
    pub group: Option<usize>,
}

impl Item {
    /// The source line this item was read from, reconstructed exactly.
    pub fn source_text(&self) -> String {
        match self.number {
            Some(n) => format!("{n}. [ ] {}", self.text),
            None => format!("- [ ] {}", self.text),
        }
    }
}

/// A non-checklist line of a gate or capability section, verbatim.
#[derive(Debug, Clone, PartialEq)]
pub struct Statement {
    pub line: usize,
    /// `lead_in` (ends with ':' and opens a group), `qualifier` (follows checklist items and completes them),
    /// `hard_invariant` (a quotation under a "Hard invariant:" lead-in), `quote`, or `prose`.
    pub kind: &'static str,
    pub text: String,
    pub group: Option<usize>,
}

/// An advanced-qualification challenge paragraph, verbatim.
#[derive(Debug, Clone, PartialEq)]
pub struct Challenge {
    pub id: String,
    pub line: usize,
    pub gate: String,
    /// The capability (or gate) section the paragraph appears in. Attribution is positional, never interpreted.
    pub section: String,
    pub text: String,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Capability {
    pub id: String,
    pub title: String,
    /// `None` for a gate capability (a gate with no numbered capability headings): its heading is the gate's.
    pub heading: Option<Line>,
    pub gate: String,
    pub gate_capability: bool,
    pub start_line: usize,
    pub end_line: usize,
    /// The requirement-class label exactly as the source states it (on the capability heading or, failing that, on
    /// its gate heading).
    pub label: Option<String>,
    pub label_line: Option<usize>,
    pub requirement_class: String,
    /// False when the label denotes none of the classes Contract v3:60 enumerates (the label is then carried verbatim).
    pub requirement_class_enumerated: bool,
    pub items: Vec<Item>,
    pub statements: Vec<Statement>,
    pub challenge_ids: Vec<String>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Gate {
    pub id: String,
    pub title: String,
    pub heading: Line,
    pub label: Option<String>,
    pub start_line: usize,
    pub end_line: usize,
    pub gate_capability: bool,
    pub capability_ids: Vec<String>,
    /// Gate-level lines that precede the first capability heading (e.g. Gate V's oracle custody sentence).
    pub statements: Vec<Statement>,
    pub challenge_ids: Vec<String>,
}

/// A preamble or closing section, carried verbatim.
#[derive(Debug, Clone, PartialEq)]
pub struct Section {
    pub id: String,
    pub heading: Option<Line>,
    pub lines: Vec<Line>,
    pub items: Vec<Item>,
}

/// One entry of Contract v3:57-73.
#[derive(Debug, Clone, PartialEq)]
pub struct FieldDef {
    pub line: usize,
    pub field: String,
    pub key: &'static str,
    pub stated_in: &'static str,
}

/// Contract-level vocabularies the owner source defines.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct Vocabularies {
    /// Contract v3:60.
    pub requirement_classes: Vec<String>,
    /// Contract v3:81-91.
    pub evidence_classes: Vec<Line>,
    /// Contract v3:97-109.
    pub freshness_inputs: Vec<Line>,
    /// Contract v3:115-127.
    pub lifecycle_points: Vec<Line>,
    /// O5 "Tiered checks:" — (tier token, the item line).
    pub tiers: Vec<(String, Line)>,
}

/// The owner source, fully accounted for.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct ContractModel {
    pub source_sha256: String,
    pub source_line_count: usize,
    pub excluded_line_count: usize,
    pub title: Line,
    pub preamble: Vec<Section>,
    pub gates: Vec<Gate>,
    pub capabilities: Vec<Capability>,
    pub challenges: Vec<Challenge>,
    pub closing: Vec<Section>,
    pub fields: Vec<FieldDef>,
    pub vocab: Vocabularies,
}

impl ContractModel {
    pub fn capability(&self, id: &str) -> Option<&Capability> {
        self.capabilities.iter().find(|c| c.id == id)
    }
    pub fn capability_ids(&self) -> Vec<String> {
        self.capabilities.iter().map(|c| c.id.clone()).collect()
    }
    pub fn tier_ids(&self) -> Vec<String> {
        self.vocab.tiers.iter().map(|t| t.0.clone()).collect()
    }
    pub fn challenge_ids(&self) -> Vec<String> {
        self.challenges.iter().map(|c| c.id.clone()).collect()
    }
    /// Checklist items of the capability universe.
    pub fn item_count(&self) -> usize {
        self.capabilities.iter().map(|c| c.items.len()).sum()
    }
    pub fn statement_count(&self) -> usize {
        self.capabilities
            .iter()
            .map(|c| c.statements.len())
            .sum::<usize>()
            + self.gates.iter().map(|g| g.statements.len()).sum::<usize>()
    }
    /// Every item of the document (capability universe plus preamble/closing sections), by id.
    pub fn any_item(&self, id: &str) -> Option<&Item> {
        self.capabilities
            .iter()
            .flat_map(|c| c.items.iter())
            .chain(
                self.preamble
                    .iter()
                    .chain(self.closing.iter())
                    .flat_map(|s| s.items.iter()),
            )
            .find(|i| i.id == id)
    }
    pub fn carried_line_count(&self) -> usize {
        self.source_line_count - self.excluded_line_count
    }
}

/// The model of the approved source compiled into this binary, refused unless it is the owner's exact bytes.
pub fn embedded_model() -> Result<ContractModel> {
    let sha = sha256_text(EMBEDDED_SOURCE);
    if sha != OWNER_SOURCE_SHA256 {
        return Err(GovError::new(
            "CONTRACT_SOURCE_DIVERGED",
            format!("the Capability Acceptance Contract compiled into this binary has digest {sha}, the owner-approved digest is {OWNER_SOURCE_SHA256}. Rebuild from the approved source."),
        ));
    }
    parse(EMBEDDED_SOURCE)
}

/// A line that carries no content: blank, or a `---` thematic break.
pub fn is_structural_blank(text: &str) -> bool {
    let t = text.trim();
    t.is_empty() || t == "---"
}

/// `- [ ] text` → (None, text); `26. [ ] text` → (Some(26), text).
pub fn checklist_parts(line: &str) -> Option<(Option<u64>, &str)> {
    if let Some(rest) = line.strip_prefix("- [ ] ") {
        return Some((None, rest));
    }
    let digits = line.bytes().take_while(|b| b.is_ascii_digit()).count();
    if digits > 0 {
        if let Some(rest) = line[digits..].strip_prefix(". [ ] ") {
            return Some((line[..digits].parse().ok(), rest));
        }
    }
    None
}

/// `Title **[LABEL]**` → ("Title", Some("LABEL")).
fn split_label(s: &str) -> (String, Option<String>) {
    let t = s.trim_end();
    if t.ends_with("]**") {
        if let Some(i) = t.rfind("**[") {
            let label = &t[i + 3..t.len() - 3];
            return (t[..i].trim_end().to_string(), Some(label.to_string()));
        }
    }
    (t.to_string(), None)
}

fn is_gate_id(s: &str) -> bool {
    !s.is_empty() && s.chars().all(|c| c.is_ascii_uppercase())
}

fn is_capability_id(s: &str) -> bool {
    let letters = s.chars().take_while(|c| c.is_ascii_uppercase()).count();
    letters > 0 && letters < s.len() && s[letters..].chars().all(|c| c.is_ascii_digit())
}

fn slug(heading: &str) -> String {
    let t = heading.trim_start_matches('#').trim();
    let mut out = String::new();
    let mut dash = false;
    for ch in t.chars() {
        if ch.is_ascii_alphanumeric() {
            out.push(ch.to_ascii_uppercase());
            dash = false;
        } else if !dash && !out.is_empty() {
            out.push('-');
            dash = true;
        }
    }
    while out.ends_with('-') {
        out.pop();
    }
    out
}

fn unrecognised(n: usize, why: &str, text: &str) -> GovError {
    GovError::new(
        "CONTRACT_SOURCE_UNRECOGNISED",
        format!("line {n} of the approved source is {why}: {text:?}. The compiler accounts for every line of the owner source and refuses to guess at a construct it does not know; the source must not be edited — extend the compiler instead."),
    )
    .with_details(json!({"line": n, "text": text}))
}

/// `- item;` → `item` (one trailing ';' or '.' removed).
fn list_text(line: &str) -> String {
    let t = line.strip_prefix("- ").unwrap_or(line).trim_end();
    t.strip_suffix(';')
        .or_else(|| t.strip_suffix('.'))
        .unwrap_or(t)
        .to_string()
}

#[derive(Default)]
struct Body {
    items: Vec<Item>,
    statements: Vec<Statement>,
    challenges: Vec<Line>,
    group: Option<(usize, String)>,
    last_was_item: bool,
    last_line: usize,
}

impl Body {
    fn absorb(&mut self, n: usize, raw: &str) {
        self.last_line = n;
        if let Some((number, text)) = checklist_parts(raw) {
            self.items.push(Item {
                id: String::new(),
                line: n,
                number,
                text: text.to_string(),
                group: self.group.as_ref().map(|g| g.0),
            });
            self.last_was_item = true;
            return;
        }
        if raw.starts_with(CHALLENGE_PREFIX) {
            self.challenges.push(Line {
                line: n,
                text: raw.to_string(),
            });
            self.last_was_item = false;
            return;
        }
        let under_hard_invariant = self
            .group
            .as_ref()
            .map(|g| g.1.to_ascii_lowercase().starts_with("hard invariant"))
            .unwrap_or(false);
        let kind = if raw.starts_with('>') {
            if under_hard_invariant {
                "hard_invariant"
            } else {
                "quote"
            }
        } else if raw.trim_end().ends_with(':') {
            "lead_in"
        } else if self.last_was_item {
            "qualifier"
        } else {
            "prose"
        };
        let group = if kind == "lead_in" {
            None
        } else {
            self.group.as_ref().map(|g| g.0)
        };
        self.statements.push(Statement {
            line: n,
            kind,
            text: raw.to_string(),
            group,
        });
        if kind == "lead_in" {
            self.group = Some((n, raw.trim_end().to_string()));
        }
        self.last_was_item = false;
    }
}

struct RawSection {
    heading: Option<Line>,
    lines: Vec<Line>,
    items: Vec<Item>,
}

impl RawSection {
    fn new(heading: Option<Line>) -> Self {
        RawSection {
            heading,
            lines: vec![],
            items: vec![],
        }
    }
    fn absorb(&mut self, n: usize, raw: &str, verbatim_only: bool) {
        if !verbatim_only {
            if let Some((number, text)) = checklist_parts(raw) {
                self.items.push(Item {
                    id: String::new(),
                    line: n,
                    number,
                    text: text.to_string(),
                    group: None,
                });
                return;
            }
        }
        self.lines.push(Line {
            line: n,
            text: raw.to_string(),
        });
    }
}

struct RawCap {
    id: String,
    title: String,
    label: Option<String>,
    heading: Option<Line>,
    body: Body,
}

struct RawGate {
    id: String,
    title: String,
    label: Option<String>,
    heading: Line,
    body: Body,
    caps: Vec<RawCap>,
}

fn finish_sections(raw: Vec<RawSection>, used: &mut BTreeSet<String>) -> Vec<Section> {
    raw.into_iter()
        .map(|s| {
            let base = match &s.heading {
                Some(h) => slug(&h.text),
                None => "FRONT-MATTER".to_string(),
            };
            let mut id = base.clone();
            let mut k = 2;
            while !used.insert(id.clone()) {
                id = format!("{base}-{k}");
                k += 1;
            }
            let items = s
                .items
                .into_iter()
                .enumerate()
                .map(|(i, mut it)| {
                    it.id = format!("{id}.{}", i + 1);
                    it
                })
                .collect();
            Section {
                id,
                heading: s.heading,
                lines: s.lines,
                items,
            }
        })
        .collect()
}

fn section_list<'a>(sections: &'a [Section], heading: &str) -> Result<&'a Section> {
    sections
        .iter()
        .find(|s| s.heading.as_ref().map(|h| h.text == heading).unwrap_or(false))
        .ok_or_else(|| {
            GovError::new(
                "CONTRACT_SOURCE_UNRECOGNISED",
                format!("the approved source has no preamble section {heading:?}; the compiler reads the contract's vocabularies from it"),
            )
        })
}

/// Resolve a requirement-class label against the classes Contract v3:60 enumerates. An unlabelled capability is an
/// original requirement (the source's preamble: later hardening "remain[s] explicitly labelled as such rather than
/// silently rewriting the original requirements"). A label denotes an enumerated class when, ignoring case, hyphens and
/// underscores and a leading "NEW", it names that class; otherwise the label itself is carried, verbatim.
fn resolve_class(label: Option<&str>, classes: &[String]) -> (String, bool) {
    let Some(label) = label else {
        return ("ORIGINAL".to_string(), true);
    };
    let norm = |s: &str| {
        s.to_ascii_uppercase()
            .replace(['-', '_'], " ")
            .split_whitespace()
            .collect::<Vec<_>>()
            .join(" ")
    };
    let l = norm(label);
    let l = l.strip_prefix("NEW ").unwrap_or(&l).to_string();
    for c in classes {
        if norm(c) == l {
            return (c.clone(), true);
        }
    }
    (label.to_string(), false)
}

/// Parse the approved source into its complete model. Fails closed (`CONTRACT_SOURCE_UNRECOGNISED`) on any construct
/// it cannot place, rather than dropping it.
pub fn parse(source: &str) -> Result<ContractModel> {
    let mut title: Option<Line> = None;
    let mut preamble: Vec<RawSection> = vec![];
    let mut gates: Vec<RawGate> = vec![];
    let mut closing: Vec<RawSection> = vec![];
    let mut in_fence = false;
    // 0 before the title, 1 preamble, 2 gates, 3 closing sections
    let mut region = 0u8;
    let mut count = 0usize;
    let mut excluded = 0usize;
    for (i, raw) in source.lines().enumerate() {
        let n = i + 1;
        count = n;
        if is_structural_blank(raw) {
            excluded += 1;
            continue;
        }
        let fence = raw.starts_with("```");
        if !in_fence && !fence {
            let level = raw.bytes().take_while(|b| *b == b'#').count();
            if level > 0 && raw[level..].starts_with(' ') {
                let line = Line {
                    line: n,
                    text: raw.to_string(),
                };
                if level == 1 {
                    let rest = &raw[2..];
                    if region == 0 {
                        title = Some(line);
                        region = 1;
                        preamble.push(RawSection::new(None));
                        continue;
                    }
                    if let Some(g) = rest.strip_prefix("GATE ") {
                        if region == 3 {
                            return Err(unrecognised(n, "a gate after the closing sections", raw));
                        }
                        let (id, rest2) = g.split_once(" — ").ok_or_else(|| {
                            unrecognised(n, "a gate heading without the ' — ' separator", raw)
                        })?;
                        if !is_gate_id(id) {
                            return Err(unrecognised(
                                n,
                                "a gate heading with an unrecognised id",
                                raw,
                            ));
                        }
                        let (gtitle, label) = split_label(rest2);
                        gates.push(RawGate {
                            id: id.to_string(),
                            title: gtitle,
                            label,
                            heading: line,
                            body: Body::default(),
                            caps: vec![],
                        });
                        region = 2;
                        continue;
                    }
                    let sec = RawSection::new(Some(line));
                    if region >= 2 {
                        closing.push(sec);
                        region = 3;
                    } else {
                        preamble.push(sec);
                    }
                    continue;
                }
                match region {
                    2 => {
                        let rest = raw.strip_prefix("## ").ok_or_else(|| {
                            unrecognised(
                                n,
                                "a sub-heading inside a gate that is not a capability heading",
                                raw,
                            )
                        })?;
                        let (id, t) = rest.split_once(". ").ok_or_else(|| {
                            unrecognised(n, "a capability heading without '<ID>. '", raw)
                        })?;
                        if !is_capability_id(id) {
                            return Err(unrecognised(
                                n,
                                "a capability heading with an unrecognised id",
                                raw,
                            ));
                        }
                        let (ctitle, label) = split_label(t);
                        let g = gates.last_mut().expect("region 2 has a gate");
                        g.caps.push(RawCap {
                            id: id.to_string(),
                            title: ctitle,
                            label,
                            heading: Some(line),
                            body: Body::default(),
                        });
                        continue;
                    }
                    1 => {
                        preamble.push(RawSection::new(Some(line)));
                        continue;
                    }
                    3 => {
                        closing.push(RawSection::new(Some(line)));
                        continue;
                    }
                    _ => return Err(unrecognised(n, "a heading before the document title", raw)),
                }
            }
        }
        if fence {
            in_fence = !in_fence;
        }
        let verbatim_only = in_fence || fence;
        match region {
            0 => return Err(unrecognised(n, "content before the document title", raw)),
            1 => preamble
                .last_mut()
                .expect("preamble section")
                .absorb(n, raw, verbatim_only),
            2 => {
                let g = gates.last_mut().expect("gate");
                match g.caps.last_mut() {
                    Some(c) => c.body.absorb(n, raw),
                    None => g.body.absorb(n, raw),
                }
            }
            _ => closing
                .last_mut()
                .expect("closing section")
                .absorb(n, raw, verbatim_only),
        }
    }
    if in_fence {
        return Err(GovError::new(
            "CONTRACT_SOURCE_UNRECOGNISED",
            "the approved source ends inside a code fence",
        ));
    }
    let title = title.ok_or_else(|| {
        GovError::new(
            "CONTRACT_SOURCE_UNRECOGNISED",
            "the approved source has no document title",
        )
    })?;
    if gates.is_empty() {
        return Err(GovError::new(
            "CONTRACT_SOURCE_UNRECOGNISED",
            "the approved source has no gate",
        ));
    }
    let mut used = BTreeSet::new();
    let preamble = finish_sections(preamble, &mut used);
    let closing = finish_sections(closing, &mut used);

    // ---- contract-level definitions (Contract v3:53-127)
    let fsec = section_list(&preamble, FIELDS_SECTION)?;
    let flines: Vec<&Line> = fsec
        .lines
        .iter()
        .filter(|l| l.text.starts_with("- "))
        .collect();
    if flines.len() != CONTRACT_FIELDS.len() {
        return Err(GovError::new(
            "CONTRACT_SOURCE_UNRECOGNISED",
            format!(
                "Contract v3 lists {} per-capability fields; the compiler knows {}",
                flines.len(),
                CONTRACT_FIELDS.len()
            ),
        ));
    }
    let mut fields = vec![];
    let mut requirement_classes = vec![];
    for (l, (text, key, stated)) in flines.iter().zip(CONTRACT_FIELDS.iter()) {
        let t = list_text(&l.text);
        if t != *text {
            return Err(unrecognised(
                l.line,
                &format!("a per-capability field that is not {text:?}"),
                &l.text,
            ));
        }
        if *key == "requirement_class" {
            requirement_classes = t
                .split('`')
                .enumerate()
                .filter(|(i, _)| i % 2 == 1)
                .map(|(_, s)| s.to_string())
                .collect();
        }
        fields.push(FieldDef {
            line: l.line,
            field: t,
            key,
            stated_in: stated,
        });
    }
    if !requirement_classes.iter().any(|c| c == "ORIGINAL") {
        return Err(GovError::new(
            "CONTRACT_SOURCE_UNRECOGNISED",
            "Contract v3's requirement-class field does not enumerate ORIGINAL",
        ));
    }
    let dash_list = |heading: &str| -> Result<Vec<Line>> {
        Ok(section_list(&preamble, heading)?
            .lines
            .iter()
            .filter(|l| l.text.starts_with("- "))
            .map(|l| Line {
                line: l.line,
                text: list_text(&l.text),
            })
            .collect())
    };
    let evidence_classes = dash_list(EVIDENCE_CLASSES_SECTION)?;
    let freshness_inputs = dash_list(FRESHNESS_SECTION)?;
    let lifecycle_points: Vec<Line> = section_list(&preamble, LIFECYCLE_SECTION)?
        .lines
        .iter()
        .filter_map(|l| {
            let digits = l.text.bytes().take_while(|b| b.is_ascii_digit()).count();
            if digits == 0 {
                return None;
            }
            l.text[digits..].strip_prefix(". ").map(|rest| Line {
                line: l.line,
                text: list_text(rest),
            })
        })
        .collect();
    if evidence_classes.is_empty() || freshness_inputs.is_empty() || lifecycle_points.is_empty() {
        return Err(GovError::new(
            "CONTRACT_SOURCE_UNRECOGNISED",
            "a contract-level vocabulary (evidence classes, freshness inputs, lifecycle) is empty",
        ));
    }

    // ---- gates and capability sections
    let mut out_gates = vec![];
    let mut out_caps: Vec<Capability> = vec![];
    let mut challenges = vec![];
    for g in gates {
        let gate_capability = g.caps.is_empty();
        let mut caps_raw = g.caps;
        let mut gate_body = g.body;
        if gate_capability {
            caps_raw.push(RawCap {
                id: g.id.clone(),
                title: g.title.clone(),
                label: None,
                heading: None,
                body: std::mem::take(&mut gate_body),
            });
        } else if let Some(it) = gate_body.items.first() {
            return Err(unrecognised(
                it.line,
                "a checklist item outside every capability section of a gate that has capability sections",
                &it.source_text(),
            ));
        }
        let mut gate_challenges = vec![];
        for (k, ch) in gate_body.challenges.iter().enumerate() {
            let id = if k == 0 {
                format!("AQC-{}", g.id)
            } else {
                format!("AQC-{}-{}", g.id, k + 1)
            };
            challenges.push(Challenge {
                id: id.clone(),
                line: ch.line,
                gate: g.id.clone(),
                section: g.id.clone(),
                text: ch.text.clone(),
            });
            gate_challenges.push(id);
        }
        let mut cap_ids = vec![];
        let mut end = g.heading.line.max(gate_body.last_line);
        for rc in caps_raw {
            let (label, label_line) = match (&rc.label, &rc.heading) {
                (Some(l), Some(h)) => (Some(l.clone()), Some(h.line)),
                _ => match &g.label {
                    Some(l) => (Some(l.clone()), Some(g.heading.line)),
                    None => (None, None),
                },
            };
            let (requirement_class, enumerated) =
                resolve_class(label.as_deref(), &requirement_classes);
            let start = rc
                .heading
                .as_ref()
                .map(|h| h.line)
                .unwrap_or(g.heading.line);
            let items: Vec<Item> = rc
                .body
                .items
                .into_iter()
                .enumerate()
                .map(|(i, mut it)| {
                    it.id = format!("{}.{}", rc.id, i + 1);
                    it
                })
                .collect();
            let mut ids = vec![];
            for (k, ch) in rc.body.challenges.iter().enumerate() {
                let id = if k == 0 {
                    format!("AQC-{}", rc.id)
                } else {
                    format!("AQC-{}-{}", rc.id, k + 1)
                };
                challenges.push(Challenge {
                    id: id.clone(),
                    line: ch.line,
                    gate: g.id.clone(),
                    section: rc.id.clone(),
                    text: ch.text.clone(),
                });
                gate_challenges.push(id.clone());
                ids.push(id);
            }
            let cend = start.max(rc.body.last_line);
            end = end.max(cend);
            cap_ids.push(rc.id.clone());
            out_caps.push(Capability {
                id: rc.id,
                title: rc.title,
                heading: rc.heading,
                gate: g.id.clone(),
                gate_capability,
                start_line: start,
                end_line: cend,
                label,
                label_line,
                requirement_class,
                requirement_class_enumerated: enumerated,
                items,
                statements: rc.body.statements,
                challenge_ids: ids,
            });
        }
        gate_challenges.sort_by_key(|id| {
            challenges
                .iter()
                .find(|c| &c.id == id)
                .map(|c| c.line)
                .unwrap_or(0)
        });
        out_gates.push(Gate {
            id: g.id,
            title: g.title,
            heading: g.heading.clone(),
            label: g.label,
            start_line: g.heading.line,
            end_line: end,
            gate_capability,
            capability_ids: cap_ids,
            statements: gate_body.statements,
            challenge_ids: gate_challenges,
        });
    }
    challenges.sort_by_key(|c| c.line);
    let mut seen = BTreeSet::new();
    for c in &out_caps {
        if !seen.insert(c.id.clone()) {
            return Err(GovError::new(
                "CONTRACT_SOURCE_UNRECOGNISED",
                format!(
                    "capability id {} appears twice in the approved source",
                    c.id
                ),
            ));
        }
    }

    // ---- health-scheduler tiers (O5 "Tiered checks:"), cross-checked with Contract v3:67 "G0–G6"
    let o5 = out_caps
        .iter()
        .find(|c| c.id == TIERS_CAPABILITY)
        .ok_or_else(|| {
            GovError::new(
                "CONTRACT_SOURCE_UNRECOGNISED",
                "the approved source has no O5 section to read the health-scheduler tiers from",
            )
        })?;
    let lead = o5
        .statements
        .iter()
        .find(|s| s.kind == "lead_in" && s.text == TIERS_LEAD_IN)
        .map(|s| s.line);
    let tiers: Vec<(String, Line)> = o5
        .items
        .iter()
        .filter(|it| lead.is_some() && it.group == lead)
        .map(|it| {
            (
                it.text.split_whitespace().next().unwrap_or("").to_string(),
                Line {
                    line: it.line,
                    text: it.text.clone(),
                },
            )
        })
        .collect();
    let consecutive = tiers
        .iter()
        .enumerate()
        .all(|(i, (t, _))| *t == format!("G{i}"));
    let range_ok = fields
        .iter()
        .find(|f| f.key == "health_scheduler_tiers")
        .map(|f| {
            f.field
                .ends_with(&format!("G0–G{}", tiers.len().saturating_sub(1)))
        })
        .unwrap_or(false);
    if tiers.is_empty() || !consecutive || !range_ok {
        return Err(GovError::new(
            "CONTRACT_SOURCE_UNRECOGNISED",
            "the O5 'Tiered checks:' items do not define the G0–G6 tiers Contract v3:67 names",
        ));
    }

    Ok(ContractModel {
        source_sha256: sha256_text(source),
        source_line_count: count,
        excluded_line_count: excluded,
        title,
        preamble,
        gates: out_gates,
        capabilities: out_caps,
        challenges,
        closing,
        fields,
        vocab: Vocabularies {
            requirement_classes,
            evidence_classes,
            freshness_inputs,
            lifecycle_points,
            tiers,
        },
    })
}

// ------------------------------------------------------------------------------------------ the compiled form

fn line_json(l: &Line) -> Value {
    json!({"line": l.line, "text": l.text})
}

fn item_json(it: &Item) -> Value {
    let mut o = Map::new();
    o.insert("id".into(), json!(it.id));
    o.insert("line".into(), json!(it.line));
    if let Some(n) = it.number {
        o.insert("number".into(), json!(n));
    }
    o.insert("text".into(), json!(it.text));
    if let Some(g) = it.group {
        o.insert("group".into(), json!(g));
    }
    Value::Object(o)
}

fn statement_json(s: &Statement) -> Value {
    let mut o = Map::new();
    o.insert("line".into(), json!(s.line));
    o.insert("kind".into(), json!(s.kind));
    o.insert("text".into(), json!(s.text));
    if let Some(g) = s.group {
        o.insert("group".into(), json!(g));
    }
    Value::Object(o)
}

fn challenge_json(c: &Challenge) -> Value {
    json!({"id": c.id, "gate": c.gate, "section": c.section, "line": c.line, "text": c.text})
}

fn section_json(s: &Section) -> Value {
    json!({
        "id": s.id,
        "heading": s.heading.as_ref().map(line_json).unwrap_or(Value::Null),
        "lines": s.lines.iter().map(line_json).collect::<Vec<_>>(),
        "checklist": s.items.iter().map(item_json).collect::<Vec<_>>(),
    })
}

fn source_reference(line: usize) -> String {
    format!("{CANONICAL_IMPORT}:{line}")
}

fn capability_json(c: &Capability) -> Value {
    let mut o = Map::new();
    o.insert("id".into(), json!(c.id));
    o.insert("title".into(), json!(c.title));
    o.insert(
        "heading".into(),
        c.heading.as_ref().map(line_json).unwrap_or(Value::Null),
    );
    o.insert("gate".into(), json!(c.gate));
    o.insert("gate_capability".into(), json!(c.gate_capability));
    o.insert(
        "family".into(),
        json!(c
            .id
            .chars()
            .take_while(|x| x.is_ascii_alphabetic())
            .collect::<String>()),
    );
    o.insert(
        "source_reference".into(),
        json!(source_reference(c.start_line)),
    );
    o.insert(
        "source_lines".into(),
        json!({"start": c.start_line, "end": c.end_line}),
    );
    o.insert("requirement_class".into(), json!(c.requirement_class));
    o.insert("requirement_class_label".into(), json!(c.label));
    o.insert("requirement_class_label_line".into(), json!(c.label_line));
    o.insert(
        "requirement_class_enumerated".into(),
        json!(c.requirement_class_enumerated),
    );
    o.insert("status".into(), json!("DECLARED"));
    o.insert(
        "checklist".into(),
        Value::Array(c.items.iter().map(item_json).collect()),
    );
    o.insert(
        "statements".into(),
        Value::Array(c.statements.iter().map(statement_json).collect()),
    );
    o.insert("qualification_challenge_ids".into(), json!(c.challenge_ids));
    for k in governed_fields() {
        // The owner source states no capability-specific value: the compiled form may not invent one.
        o.insert(k.into(), Value::Null);
    }
    Value::Object(o)
}

fn gate_json(g: &Gate) -> Value {
    json!({
        "id": g.id,
        "title": g.title,
        "heading": line_json(&g.heading),
        "requirement_class_label": g.label,
        "source_lines": {"start": g.start_line, "end": g.end_line},
        "gate_capability": g.gate_capability,
        "capabilities": g.capability_ids,
        "statements": g.statements.iter().map(statement_json).collect::<Vec<_>>(),
        "qualification_challenge_ids": g.challenge_ids,
    })
}

const COVERAGE_RULE: &str = "every line of the owner source except blank lines and '---' thematic breaks is carried verbatim, with its line number, exactly once (checklist items as '- [ ] <text>' or '<number>. [ ] <text>')";

/// Compile the executable representation. Deterministic and byte-stable for a given source.
pub fn compile_model(m: &ContractModel) -> Value {
    json!({
        "schema": COMPILED_SCHEMA_ID,
        "schema_version": DERIVED_VIEW_VERSION,
        "contract_version": CONTRACT_VERSION,
        "compiled_from": {
            "owner_source": OWNER_SOURCE,
            "canonical_import": CANONICAL_IMPORT,
            "source_sha256": m.source_sha256,
        },
        "compiler": {
            "note": "Mechanically derived from the approved source by a line-accounting compiler. No contract semantics are authored here: every carried line is the owner's text, verbatim; ids are minted from position; a per-capability field the owner source states no value for is null. This file is valid only while contract-source.lock proves it was compiled from that exact source hash, and `gov contract verify` fails on any semantic difference.",
        },
        "document": {"title": line_json(&m.title)},
        "coverage": {
            "rule": COVERAGE_RULE,
            "source_lines": m.source_line_count,
            "carried_lines": m.carried_line_count(),
            "excluded_lines": m.excluded_line_count,
        },
        "field_definitions": m.fields.iter().map(|f| json!({"line": f.line, "field": f.field, "key": f.key, "value_stated_in": f.stated_in})).collect::<Vec<_>>(),
        "vocabularies": {
            "requirement_classes": m.vocab.requirement_classes,
            "evidence_classes": m.vocab.evidence_classes.iter().map(|l| json!({"line": l.line, "value": l.text})).collect::<Vec<_>>(),
            "freshness_inputs": m.vocab.freshness_inputs.iter().map(|l| json!({"line": l.line, "value": l.text})).collect::<Vec<_>>(),
            "lifecycle_points": m.vocab.lifecycle_points.iter().map(|l| json!({"line": l.line, "value": l.text})).collect::<Vec<_>>(),
            "health_scheduler_tiers": m.vocab.tiers.iter().map(|(t, l)| json!({"tier": t, "line": l.line, "value": l.text})).collect::<Vec<_>>(),
        },
        "preamble": m.preamble.iter().map(section_json).collect::<Vec<_>>(),
        "gate_count": m.gates.len(),
        "gates": m.gates.iter().map(gate_json).collect::<Vec<_>>(),
        "capability_count": m.capabilities.len(),
        "checklist_item_count": m.item_count(),
        "capabilities": m.capabilities.iter().map(capability_json).collect::<Vec<_>>(),
        "advanced_qualification_challenges": m.challenges.iter().map(challenge_json).collect::<Vec<_>>(),
        "closing": m.closing.iter().map(section_json).collect::<Vec<_>>(),
    })
}

/// Parse and compile in one step.
pub fn compile(source: &str) -> Result<Value> {
    Ok(compile_model(&parse(source)?))
}

// ------------------------------------------------------------------------------------------ the evidence map

/// The default value of a governed field nobody has mapped.
fn governed_default(key: &str) -> Value {
    match key {
        "evidence_class" => json!(NOT_YET_MAPPED),
        "automated_checks" => json!([]),
        _ => Value::Null,
    }
}

/// Build the evidence map from the owner-source model. Governed values (Contract v3:53-73 fields the source states no
/// value for, and per-item automated checks) are carried over from `existing` by capability / item id — populating
/// them is governed work, and regenerating the map never discards it.
pub fn evidence_map(m: &ContractModel, existing: Option<&Value>) -> Value {
    let mut old_rows: BTreeMap<String, &Value> = BTreeMap::new();
    if let Some(rows) = existing
        .and_then(|e| e.get("capabilities"))
        .and_then(|v| v.as_array())
    {
        for r in rows {
            if let Some(id) = r.get("capability").and_then(|v| v.as_str()) {
                old_rows.insert(id.to_string(), r);
            }
        }
    }
    let rows: Vec<Value> = m
        .capabilities
        .iter()
        .map(|c| {
            let old = old_rows.get(&c.id).copied();
            let mut old_items: BTreeMap<String, &Value> = BTreeMap::new();
            if let Some(items) = old
                .and_then(|o| o.get("checklist"))
                .and_then(|v| v.as_array())
            {
                for it in items {
                    if let Some(id) = it.get("id").and_then(|v| v.as_str()) {
                        old_items.insert(id.to_string(), it);
                    }
                }
            }
            let mut o = Map::new();
            o.insert("capability".into(), json!(c.id));
            o.insert("title".into(), json!(c.title));
            o.insert("gate".into(), json!(c.gate));
            o.insert(
                "source_reference".into(),
                json!(source_reference(c.start_line)),
            );
            o.insert("requirement_class".into(), json!(c.requirement_class));
            o.insert("requirement_class_label".into(), json!(c.label));
            let items: Vec<Value> = c
                .items
                .iter()
                .map(|it| {
                    let mut v = item_json(it);
                    let checks = old_items
                        .get(&it.id)
                        .and_then(|o| o.get("automated_checks"))
                        .cloned()
                        .unwrap_or_else(|| json!([]));
                    v.as_object_mut()
                        .expect("item object")
                        .insert("automated_checks".into(), checks);
                    v
                })
                .collect();
            o.insert("checklist".into(), Value::Array(items));
            o.insert(
                "statements".into(),
                Value::Array(c.statements.iter().map(statement_json).collect()),
            );
            o.insert("qualification_challenge_ids".into(), json!(c.challenge_ids));
            for k in governed_fields() {
                let v = old
                    .and_then(|o| o.get(k))
                    .cloned()
                    .unwrap_or_else(|| governed_default(k));
                o.insert(k.into(), v);
            }
            Value::Object(o)
        })
        .collect();
    let mut out = json!({
        "schema": MAP_SCHEMA_ID,
        "schema_version": DERIVED_VIEW_VERSION,
        "contract_version": CONTRACT_VERSION,
        "source_sha256": m.source_sha256,
        "note": MAP_NOTE,
        "governed_fields": governed_fields(),
        "gates": m.gates.iter().map(|g| json!({
            "id": g.id,
            "title": g.title,
            "line": g.heading.line,
            "requirement_class_label": g.label,
            "statements": g.statements.iter().map(statement_json).collect::<Vec<_>>(),
        })).collect::<Vec<_>>(),
        "advanced_qualification_challenges": m.challenges.iter().map(challenge_json).collect::<Vec<_>>(),
        "capabilities": rows,
    });
    if let Some(f) = existing.and_then(|e| e.get("freshness_invalidation")) {
        if !f.is_null() {
            out["freshness_invalidation"] = f.clone();
        }
    }
    out
}

/// The evidence map's own note: what is source-derived, what is governed, and what the owners determine.
const MAP_NOTE: &str = "capability → test/check/evidence mapping. Every field except the governed ones is derived from the owner source and checked against it by `gov contract verify`. The governed fields — the Contract v3:53-73 fields the owner source states no per-capability value for, each checklist item's automated_checks and the freshness_invalidation owners — are populated by governed evidence mapping, never asserted by the compiler, and are preserved by `gov contract compile`. Evidence owners (BC-P2-02, frozen AC-10) are objects {id: <kind>:<reference>, class, tiers?, record?, tests?, exercises?} in automated_checks (product and builder owners) and independent_verification (independent owners); `gov contract verify` resolves every owner against the product and fails, typed, on a capability with no running owner. evidence_class (Contract v3:81-91), health_scheduler_tiers (O5), freshness_triggers (Contract v3:97-109), adoption_obligation, operational_audit_obligation and remediation_rule are what the owners determine, derived by `gov contract compile`; the source lock binds the digest of every governed value, so none changes without a recompile.";

/// The source-derived part of an evidence map: every governed value removed.
pub fn evidence_map_projection(map: &Value) -> Value {
    let mut v = map.clone();
    if let Some(o) = v.as_object_mut() {
        o.remove("freshness_invalidation");
    }
    let governed = governed_fields();
    if let Some(rows) = v.get_mut("capabilities").and_then(|r| r.as_array_mut()) {
        for row in rows {
            if let Some(o) = row.as_object_mut() {
                for k in &governed {
                    o.remove(*k);
                }
                if let Some(items) = o.get_mut("checklist").and_then(|x| x.as_array_mut()) {
                    for it in items {
                        if let Some(io) = it.as_object_mut() {
                            io.remove("automated_checks");
                        }
                    }
                }
            }
        }
    }
    v
}

// ------------------------------------------------------------------------------------------ the generated view

fn cell(s: &str) -> String {
    s.replace('|', "\\|")
}

fn render_value(v: Option<&Value>) -> String {
    match v {
        None | Some(Value::Null) => "—".to_string(),
        Some(Value::String(s)) => format!("`{s}`"),
        Some(Value::Array(a)) if a.is_empty() => "none".to_string(),
        Some(Value::Array(a)) => a
            .iter()
            .map(|x| match x {
                Value::String(s) => format!("`{s}`"),
                o => format!("`{}`", crate::util::canonical_json(o)),
            })
            .collect::<Vec<_>>()
            .join(", "),
        Some(o) => format!("`{}`", crate::util::canonical_json(o)),
    }
}

fn class_sentence(c: &Capability) -> String {
    let src = format!(
        "Source: `{}` (lines {}–{})",
        source_reference(c.start_line),
        c.start_line,
        c.end_line
    );
    match (&c.label, c.label_line) {
        (None, _) => format!(
            "{src} · requirement class `{}` (no label in the source)",
            c.requirement_class
        ),
        (Some(l), line) if c.requirement_class_enumerated => format!(
            "{src} · requirement class `{}` · source label `{l}` (line {})",
            c.requirement_class,
            line.unwrap_or(0)
        ),
        (Some(l), line) => format!(
            "{src} · requirement class `{}` — not one of the classes enumerated at Contract v3 line 60, carried verbatim · source label `{l}` (line {})",
            c.requirement_class,
            line.unwrap_or(0)
        ),
    }
}

/// One rendered element of a section, in source order.
enum Element<'a> {
    Item(&'a Item),
    Statement(&'a Statement),
    Challenge(&'a Challenge),
}

fn element_line(e: &Element) -> usize {
    match e {
        Element::Item(i) => i.line,
        Element::Statement(s) => s.line,
        Element::Challenge(c) => c.line,
    }
}

fn render_element(e: &Element) -> String {
    match e {
        Element::Item(i) => format!("{} <sub>{} · L{}</sub>", i.source_text(), i.id, i.line),
        Element::Statement(s) => format!("{} <sub>L{} · {}</sub>", s.text, s.line, s.kind),
        Element::Challenge(c) => format!("{} <sub>{} · L{}</sub>", c.text, c.id, c.line),
    }
}

fn render_elements(
    out: &mut String,
    exp: &mut Vec<(String, String)>,
    owner: &str,
    mut elements: Vec<Element>,
) {
    elements.sort_by_key(element_line);
    let mut prev_item = None;
    for e in &elements {
        let is_item = matches!(e, Element::Item(_));
        if prev_item.is_some() && (prev_item != Some(true) || !is_item) {
            out.push('\n');
        }
        let line = render_element(e);
        let what = match e {
            Element::Item(i) => format!("{owner} checklist item {}", i.id),
            Element::Statement(s) => format!("{owner} {} at line {}", s.kind, s.line),
            Element::Challenge(c) => format!("{owner} advanced-qualification challenge {}", c.id),
        };
        out.push_str(&line);
        out.push('\n');
        exp.push((what, line));
        prev_item = Some(is_item);
    }
    if !elements.is_empty() {
        out.push('\n');
    }
}

fn emit(out: &mut String, exp: &mut Vec<(String, String)>, what: String, line: String) {
    out.push_str(&line);
    out.push('\n');
    exp.push((what, line));
}

/// The evidence owners and governed fields of one capability, as the generated view shows them.
fn render_owners(
    out: &mut String,
    exp: &mut Vec<(String, String)>,
    cap: &str,
    row: Option<&Value>,
) {
    for (field, title) in [
        (
            "automated_checks",
            "Evidence owners (automated_checks, Contract v3:64):",
        ),
        (
            "independent_verification",
            "Independent verification (Contract v3:65):",
        ),
    ] {
        let owners = row
            .and_then(|r| r.get(field))
            .and_then(|v| v.as_array())
            .cloned()
            .unwrap_or_default();
        emit(
            out,
            exp,
            format!("{cap} {field} heading"),
            title.to_string(),
        );
        if owners.is_empty() {
            emit(
                out,
                exp,
                format!("{cap} {field} none"),
                "- none".to_string(),
            );
        }
        for o in owners {
            let id = o.get("id").and_then(|v| v.as_str()).unwrap_or("?");
            let mut line = format!(
                "- `{id}` — {}",
                o.get("class").and_then(|v| v.as_str()).unwrap_or("?")
            );
            let tiers = str_array(o.get("tiers"));
            if !tiers.is_empty() {
                line.push_str(&format!(" · {}", tiers.join(", ")));
            }
            if let Some(r) = o.get("record").and_then(|v| v.as_str()) {
                line.push_str(&format!(" · record `{r}`"));
            }
            let tests = str_array(o.get("tests"));
            if !tests.is_empty() {
                line.push_str(&format!(" · tests {}", tests.join(", ")));
            }
            if let Some(e) = o.get("exercises").and_then(|v| v.as_str()) {
                line.push_str(&format!(" — {e}"));
            }
            emit(out, exp, format!("{cap} owner {id}"), line);
        }
        out.push('\n');
    }
    let items: Vec<Value> = row.map(|r| lines_of(r, "checklist")).unwrap_or_default();
    let named: Vec<&Value> = items
        .iter()
        .filter(|i| {
            i.get("automated_checks")
                .and_then(|v| v.as_array())
                .map(|a| !a.is_empty())
                .unwrap_or(false)
        })
        .collect();
    if !named.is_empty() {
        emit(
            out,
            exp,
            format!("{cap} item owners heading"),
            "Checklist items → owners:".to_string(),
        );
        for it in named {
            let iid = it.get("id").and_then(|v| v.as_str()).unwrap_or("?");
            emit(
                out,
                exp,
                format!("{cap} item {iid} owners"),
                format!("- `{iid}`: {}", render_value(it.get("automated_checks"))),
            );
        }
        out.push('\n');
    }
    emit(
        out,
        exp,
        format!("{cap} governed heading"),
        "Governed fields (evidence map; Contract v3:61-73):".to_string(),
    );
    for k in governed_fields() {
        if k == "automated_checks" || k == "independent_verification" {
            continue;
        }
        emit(
            out,
            exp,
            format!("{cap} governed {k}"),
            format!("- {k}: {}", render_value(row.and_then(|r| r.get(k)))),
        );
    }
    out.push('\n');
}

/// Render the generated readable view. Returns the text and the lines that must appear in it, each named by the
/// element it carries (so a verifier reports "checklist item A1.3 missing", not only "the file differs").
pub fn render_view(m: &ContractModel, map: &Value) -> (String, Vec<(String, String)>) {
    let rows: BTreeMap<String, &Value> = map
        .get("capabilities")
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|r| {
                    r.get("capability")
                        .and_then(|v| v.as_str())
                        .map(|id| (id.to_string(), r))
                })
                .collect()
        })
        .unwrap_or_default();
    let mut out = String::new();
    let mut exp: Vec<(String, String)> = vec![];
    out.push_str("# Governance Capability Acceptance — generated runtime view\n\n");
    out.push_str("**Derived and non-authoritative.** The normative source is the owner-approved\n");
    out.push_str(&format!("`{OWNER_SOURCE}` (SHA-256 `{OWNER_SOURCE_SHA256}`), imported byte-identically to\n`{CANONICAL_IMPORT}`.\n\n"));
    out.push_str("This file is generated by `gov contract compile` and checked by `gov contract verify`, which fails on any difference\nfrom a fresh rendering of the owner source and the evidence map. Do not edit it; edit nothing but the owner source and\nthe governed fields of `tests/governance/capability-evidence-map.yaml`. Every checklist item, statement and challenge\nbelow is the owner's text, verbatim, followed by its id and source line.\n\n");
    let universe = format!(
        "Universe: {} capabilities in {} gates; {} checklist items; {} advanced-qualification challenges.",
        m.capabilities.len(),
        m.gates.len(),
        m.item_count(),
        m.challenges.len()
    );
    out.push_str(&universe);
    out.push_str("\n\n");
    exp.push(("universe summary".into(), universe));

    out.push_str("## Capability index\n\n");
    out.push_str("| Capability | Title | Gate | Requirement class | Source label | Source line | Checklist items | Challenge IDs | Evidence class | Owners (product / independent) | Tiers |\n|---|---|---|---|---|---|---|---|---|---|---|\n");
    for c in &m.capabilities {
        let row_v = rows.get(&c.id).copied();
        let count = |k: &str| {
            row_v
                .and_then(|r| r.get(k))
                .and_then(|v| v.as_array())
                .map(|a| a.len())
                .unwrap_or(0)
        };
        let checks = format!(
            "{} / {}",
            count("automated_checks"),
            count("independent_verification")
        );
        let row = format!(
            "| `{}` | {} | {} | `{}` | {} | {} | {} | {} | {} | {} | {} |",
            c.id,
            cell(&c.title),
            c.gate,
            c.requirement_class,
            c.label
                .as_ref()
                .map(|l| format!("`{l}`"))
                .unwrap_or_else(|| "—".into()),
            c.start_line,
            c.items.len(),
            if c.challenge_ids.is_empty() {
                "—".to_string()
            } else {
                c.challenge_ids
                    .iter()
                    .map(|i| format!("`{i}`"))
                    .collect::<Vec<_>>()
                    .join(", ")
            },
            cell(&render_value(row_v.and_then(|r| r.get("evidence_class")))),
            checks,
            cell(&render_value(
                row_v.and_then(|r| r.get("health_scheduler_tiers"))
            ))
        );
        out.push_str(&row);
        out.push('\n');
        exp.push((format!("{} index row", c.id), row));
    }
    out.push('\n');

    out.push_str("## Contract-level definitions (owner-source preamble)\n\n");
    out.push_str("### Required contract fields per capability (Contract v3:53-73)\n\n");
    out.push_str("| Source line | Field | Key in every derived view | Value stated in |\n|---|---|---|---|\n");
    for f in &m.fields {
        let row = format!(
            "| {} | {} | `{}` | {} |",
            f.line,
            cell(&f.field),
            f.key,
            if f.stated_in == STATED_IN_OWNER_SOURCE {
                "owner source"
            } else {
                "evidence map (governed)"
            }
        );
        out.push_str(&row);
        out.push('\n');
        exp.push((format!("contract field {}", f.key), row));
    }
    out.push('\n');
    let vocab_list =
        |out: &mut String, exp: &mut Vec<(String, String)>, title: &str, v: &[Line]| {
            out.push_str(&format!("### {title}\n\n"));
            for l in v {
                let line = format!("- {} <sub>L{}</sub>", l.text, l.line);
                out.push_str(&line);
                out.push('\n');
                exp.push((format!("{title} entry at line {}", l.line), line));
            }
            out.push('\n');
        };
    vocab_list(
        &mut out,
        &mut exp,
        "Evidence classes (Contract v3:81-91)",
        &m.vocab.evidence_classes,
    );
    vocab_list(
        &mut out,
        &mut exp,
        "Evidence-freshness inputs (Contract v3:97-109)",
        &m.vocab.freshness_inputs,
    );
    vocab_list(
        &mut out,
        &mut exp,
        "Lifecycle points (Contract v3:115-127)",
        &m.vocab.lifecycle_points,
    );
    out.push_str("### Health-scheduler tiers (O5 “Tiered checks:”)\n\n");
    for (t, l) in &m.vocab.tiers {
        let line = format!("- `{t}` — {} <sub>L{}</sub>", l.text, l.line);
        out.push_str(&line);
        out.push('\n');
        exp.push((format!("tier {t}"), line));
    }
    out.push('\n');

    for g in &m.gates {
        let heading = format!("## Gate {} — {}", g.id, g.title);
        out.push_str(&heading);
        out.push_str("\n\n");
        exp.push((format!("gate {} heading", g.id), heading));
        let meta = format!(
            "Source line {} · capabilities: {} · source label: {} · advanced-qualification challenge IDs: {}",
            g.heading.line,
            g.capability_ids
                .iter()
                .map(|c| format!("`{c}`"))
                .collect::<Vec<_>>()
                .join(", "),
            g.label
                .as_ref()
                .map(|l| format!("`{l}`"))
                .unwrap_or_else(|| "—".into()),
            if g.challenge_ids.is_empty() {
                "—".to_string()
            } else {
                g.challenge_ids
                    .iter()
                    .map(|i| format!("`{i}`"))
                    .collect::<Vec<_>>()
                    .join(", ")
            }
        );
        out.push_str(&meta);
        out.push_str("\n\n");
        exp.push((format!("gate {} summary", g.id), meta));
        let mut gate_elements: Vec<Element> = g.statements.iter().map(Element::Statement).collect();
        gate_elements.extend(
            m.challenges
                .iter()
                .filter(|c| c.section == g.id && !g.gate_capability)
                .map(Element::Challenge),
        );
        render_elements(&mut out, &mut exp, &format!("gate {}", g.id), gate_elements);
        for cid in &g.capability_ids {
            let Some(c) = m.capability(cid) else { continue };
            let h = format!("### {}. {}", c.id, c.title);
            out.push_str(&h);
            out.push_str("\n\n");
            exp.push((format!("{} heading", c.id), h));
            let cls = class_sentence(c);
            out.push_str(&cls);
            out.push_str("\n\n");
            exp.push((format!("{} requirement class", c.id), cls));
            let mut elements: Vec<Element> = c.items.iter().map(Element::Item).collect();
            elements.extend(c.statements.iter().map(Element::Statement));
            elements.extend(
                m.challenges
                    .iter()
                    .filter(|x| x.section == c.id)
                    .map(Element::Challenge),
            );
            render_elements(&mut out, &mut exp, &c.id, elements);
            let row_v = rows.get(&c.id).copied();
            let fields_line = format!(
                "Contract v3:57-73 fields — stated by the owner source: id `{}`, title, source_reference, requirement_class, qualification_challenge_ids {}; governed (evidence map): the owners and fields below.",
                c.id,
                render_value(Some(&json!(c.challenge_ids)))
            );
            out.push_str(&fields_line);
            out.push_str("\n\n");
            exp.push((format!("{} contract fields", c.id), fields_line));
            render_owners(&mut out, &mut exp, &c.id, row_v);
        }
    }

    for s in &m.closing {
        if s.items.is_empty() {
            continue;
        }
        let heading = format!(
            "## {} (line {})",
            s.heading
                .as_ref()
                .map(|h| h.text.trim_start_matches('#').trim().to_string())
                .unwrap_or_default(),
            s.heading.as_ref().map(|h| h.line).unwrap_or(0)
        );
        out.push_str(&heading);
        out.push_str("\n\n");
        exp.push((format!("closing section {} heading", s.id), heading));
        for it in &s.items {
            let line = format!("{} <sub>{} · L{}</sub>", it.source_text(), it.id, it.line);
            out.push_str(&line);
            out.push('\n');
            exp.push((format!("closing checklist item {}", it.id), line));
        }
        out.push('\n');
    }
    let footer = format!(
        "{} capabilities · {} checklist items · generated from source SHA-256 `{}`.",
        m.capabilities.len(),
        m.item_count(),
        m.source_sha256
    );
    out.push_str(&footer);
    out.push('\n');
    exp.push(("footer".into(), footer));
    (out, exp)
}

// ------------------------------------------------------------------------------------------ the source lock

/// The source-lock: binds every derived view to the exact approved source hash.
pub fn source_lock(
    m: &ContractModel,
    compiled: &Value,
    evidence_map_source_sha256: &str,
    evidence_map_governed_sha256: &str,
    generated_view_sha256: &str,
    schema_sha256: &str,
) -> Value {
    json!({
        "schema": LOCK_SCHEMA_ID,
        "schema_version": DERIVED_VIEW_VERSION,
        "contract_version": CONTRACT_VERSION,
        "owner_source": OWNER_SOURCE,
        "owner_source_sha256": OWNER_SOURCE_SHA256,
        "canonical_import": CANONICAL_IMPORT,
        "canonical_import_sha256": m.source_sha256,
        "compiled": COMPILED,
        "compiled_sha256": crate::util::hash_value(compiled),
        "compiled_schema": SCHEMA,
        "compiled_schema_sha256": schema_sha256,
        "evidence_map": EVIDENCE_MAP,
        "evidence_map_source_sha256": evidence_map_source_sha256,
        "evidence_map_governed_sha256": evidence_map_governed_sha256,
        "generated_view": GENERATED_VIEW,
        "generated_view_sha256": generated_view_sha256,
        "universe": {
            "capabilities": m.capabilities.len(),
            "gates": m.gates.len(),
            "checklist_items": m.item_count(),
            "qualification_challenges": m.challenges.len(),
            "carried_source_lines": m.carried_line_count(),
        },
        "binding": "The compiled representation, the source-derived fields of the evidence map and the generated view are valid only while canonical_import_sha256 equals owner_source_sha256 and each equals a fresh derivation from that source (compiled_sha256: canonical-JSON digest of the compiled value; evidence_map_source_sha256: canonical-JSON digest of the evidence map with its governed fields removed; evidence_map_governed_sha256: canonical-JSON digest of its governed values — evidence owners and every field they determine — as `gov contract compile` last wrote them; generated_view_sha256: SHA-256 of the view's bytes). `gov contract verify` fails on any semantic difference (Contract v3, 'Contract authority model') and on a governed value changed without a recompile.",
        "gate": "GATE-OWNER-CAC-UPLOAD",
        "logged_precedence_conflict": "The owner supplied the normative source at the repository root rather than at the destination path; an active owner directive outranks the frozen gate convention, so the root file is authoritative and the destination copy is a hash-bound canonical import.",
    })
}

// ------------------------------------------------------------------------------------------ differences

fn short(v: &Value) -> Value {
    let s = match v {
        Value::String(s) => s.clone(),
        o => crate::util::canonical_json(o),
    };
    if s.chars().count() > 240 {
        json!(format!("{}…", s.chars().take(240).collect::<String>()))
    } else if v.is_string() {
        v.clone()
    } else {
        json!(s)
    }
}

fn difference(
    view: &str,
    at: &str,
    problem: &str,
    expected: Option<&Value>,
    found: Option<&Value>,
) -> Value {
    let mut o = Map::new();
    o.insert("view".into(), json!(view));
    o.insert("at".into(), json!(at));
    o.insert("problem".into(), json!(problem));
    if let Some(e) = expected {
        o.insert("expected".into(), short(e));
    }
    if let Some(f) = found {
        o.insert("found".into(), short(f));
    }
    Value::Object(o)
}

fn key_of(v: &Value) -> Option<String> {
    for k in ["id", "capability", "key", "tier"] {
        if let Some(s) = v.get(k).and_then(|x| x.as_str()) {
            return Some(s.to_string());
        }
    }
    v.get("line")
        .and_then(|x| x.as_u64())
        .map(|n| format!("L{n}"))
}

/// Compare `found` with `expected`, keying arrays of records by their id (or line) so that a deleted capability is
/// reported as `capabilities[U]: missing`, not as a hundred shifted positions.
pub fn keyed_diff(view: &str, expected: &Value, found: &Value, at: &str, out: &mut Vec<Value>) {
    match (expected, found) {
        (Value::Object(e), Value::Object(f)) => {
            for (k, ev) in e {
                let p = if at.is_empty() {
                    k.clone()
                } else {
                    format!("{at}.{k}")
                };
                match f.get(k) {
                    None => out.push(difference(view, &p, "missing", Some(ev), None)),
                    Some(fv) => keyed_diff(view, ev, fv, &p, out),
                }
            }
            for (k, fv) in f {
                if !e.contains_key(k) {
                    let p = if at.is_empty() {
                        k.clone()
                    } else {
                        format!("{at}.{k}")
                    };
                    out.push(difference(
                        view,
                        &p,
                        "unexpected (not in the owner source)",
                        None,
                        Some(fv),
                    ));
                }
            }
        }
        (Value::Array(e), Value::Array(f)) => {
            let ek: Option<Vec<String>> = e.iter().map(key_of).collect();
            let fk: Option<Vec<String>> = f.iter().map(key_of).collect();
            match (ek, fk) {
                (Some(ek), Some(fk)) if !e.is_empty() => {
                    let before = out.len();
                    let mut fmap: BTreeMap<&str, Vec<&Value>> = BTreeMap::new();
                    for (k, v) in fk.iter().zip(f.iter()) {
                        fmap.entry(k.as_str()).or_default().push(v);
                    }
                    for (k, ev) in ek.iter().zip(e.iter()) {
                        let p = format!("{at}[{k}]");
                        match fmap.get(k.as_str()) {
                            None => out.push(difference(view, &p, "missing", Some(ev), None)),
                            Some(vs) if vs.len() > 1 => {
                                out.push(difference(view, &p, "duplicated", Some(ev), None))
                            }
                            Some(vs) => keyed_diff(view, ev, vs[0], &p, out),
                        }
                    }
                    let eset: BTreeSet<&str> = ek.iter().map(|s| s.as_str()).collect();
                    for (k, fv) in fk.iter().zip(f.iter()) {
                        if !eset.contains(k.as_str()) {
                            out.push(difference(
                                view,
                                &format!("{at}[{k}]"),
                                "unexpected (not in the owner source)",
                                None,
                                Some(fv),
                            ));
                        }
                    }
                    if out.len() == before && ek != fk {
                        out.push(difference(
                            view,
                            at,
                            "order differs from the owner source",
                            None,
                            None,
                        ));
                    }
                }
                _ => {
                    if e.len() != f.len() {
                        out.push(difference(
                            view,
                            at,
                            &format!(
                                "has {} entries, the owner source gives {}",
                                f.len(),
                                e.len()
                            ),
                            Some(expected),
                            Some(found),
                        ));
                    } else {
                        for (i, (ev, fv)) in e.iter().zip(f.iter()).enumerate() {
                            keyed_diff(view, ev, fv, &format!("{at}[{i}]"), out);
                        }
                    }
                }
            }
        }
        _ => {
            if expected != found {
                out.push(difference(view, at, "differs", Some(expected), Some(found)));
            }
        }
    }
}

fn label_regex() -> &'static Regex {
    static RX: OnceLock<Regex> = OnceLock::new();
    RX.get_or_init(|| Regex::new(r"\*\*\[([^\]]+)\]\*\*\s*$").expect("label regex"))
}

fn checklist_regex() -> &'static Regex {
    static RX: OnceLock<Regex> = OnceLock::new();
    RX.get_or_init(|| Regex::new(r"^\s*(?:-|[0-9]+\.)\s+\[ \]\s").expect("checklist regex"))
}

fn capability_heading_regex() -> &'static Regex {
    static RX: OnceLock<Regex> = OnceLock::new();
    RX.get_or_init(|| Regex::new(r"^##\s+([A-Z]+[0-9]+)\.\s").expect("capability heading regex"))
}

fn gate_heading_regex() -> &'static Regex {
    static RX: OnceLock<Regex> = OnceLock::new();
    RX.get_or_init(|| Regex::new(r"^#\s+GATE\s+([A-Z]+)\s").expect("gate heading regex"))
}

fn lines_of(v: &Value, key: &str) -> Vec<Value> {
    v.get(key)
        .and_then(|x| x.as_array())
        .cloned()
        .unwrap_or_default()
}

/// Collects the `{line, text}` pairs a derived view carries.
struct Accounting<'a> {
    view: &'a str,
    carried: Vec<(usize, String, String)>,
    d: &'a mut Vec<Value>,
}

impl Accounting<'_> {
    fn malformed(&mut self, at: String) {
        self.d.push(difference(
            self.view,
            &at,
            "malformed carried line (needs an integer line and a string text)",
            None,
            None,
        ));
    }
    fn take(&mut self, v: &Value, at: String, item: bool) {
        let line = v.get("line").and_then(|x| x.as_u64());
        let text = v.get("text").and_then(|x| x.as_str());
        match (line, text) {
            (Some(l), Some(t)) => {
                let t = if item {
                    match v.get("number").and_then(|x| x.as_u64()) {
                        Some(n) => format!("{n}. [ ] {t}"),
                        None => format!("- [ ] {t}"),
                    }
                } else {
                    t.to_string()
                };
                self.carried.push((l as usize, t, at));
            }
            _ => self.malformed(at),
        }
    }
}

/// **Independent line accounting of a compiled form against the source text.** It uses none of the compiler's
/// parsing: it collects every `{line, text}` the compiled value carries, reconstructs checklist lines, and requires that
/// every non-blank line of the source is carried verbatim exactly once; that every checklist-shaped source line is
/// carried *as a checklist item* inside the capability section that textually contains it; that every capability
/// heading, every gate and every gate without capability headings (Gate U) is carried as a capability; that every
/// requirement-class label is carried exactly as written; and that every advanced-qualification challenge is carried.
pub fn source_accounting(view: &str, compiled: &Value, source: &str) -> Vec<Value> {
    let mut d = vec![];
    let src: Vec<&str> = source.lines().collect();
    let mut acc = Accounting {
        view,
        carried: vec![],
        d: &mut d,
    };
    if let Some(t) = compiled.get("document").and_then(|x| x.get("title")) {
        acc.take(t, "document.title".into(), false);
    }
    let mut item_lines: BTreeMap<usize, String> = BTreeMap::new();
    for key in ["preamble", "closing"] {
        for s in lines_of(compiled, key) {
            let sid = s
                .get("id")
                .and_then(|x| x.as_str())
                .unwrap_or("?")
                .to_string();
            if let Some(h) = s.get("heading").filter(|h| !h.is_null()) {
                acc.take(h, format!("{key}[{sid}].heading"), false);
            }
            for l in lines_of(&s, "lines") {
                acc.take(&l, format!("{key}[{sid}].lines"), false);
            }
            for it in lines_of(&s, "checklist") {
                acc.take(&it, format!("{key}[{sid}].checklist"), true);
                if let Some(l) = it.get("line").and_then(|x| x.as_u64()) {
                    item_lines.insert(l as usize, sid.clone());
                }
            }
        }
    }
    for g in lines_of(compiled, "gates") {
        let gid = g
            .get("id")
            .and_then(|x| x.as_str())
            .unwrap_or("?")
            .to_string();
        match g.get("heading") {
            Some(h) => acc.take(h, format!("gates[{gid}].heading"), false),
            None => acc.malformed(format!("gates[{gid}].heading")),
        }
        for s in lines_of(&g, "statements") {
            acc.take(&s, format!("gates[{gid}].statements"), false);
        }
    }
    let caps = lines_of(compiled, "capabilities");
    for c in &caps {
        let cid = c
            .get("id")
            .and_then(|x| x.as_str())
            .unwrap_or("?")
            .to_string();
        if let Some(h) = c.get("heading").filter(|h| !h.is_null()) {
            acc.take(h, format!("capabilities[{cid}].heading"), false);
        }
        for it in lines_of(c, "checklist") {
            acc.take(&it, format!("capabilities[{cid}].checklist"), true);
            if let Some(l) = it.get("line").and_then(|x| x.as_u64()) {
                item_lines.insert(l as usize, cid.clone());
            }
        }
        for s in lines_of(c, "statements") {
            acc.take(&s, format!("capabilities[{cid}].statements"), false);
        }
    }
    let mut challenge_lines = BTreeSet::new();
    for ch in lines_of(compiled, "advanced_qualification_challenges") {
        let id = ch
            .get("id")
            .and_then(|x| x.as_str())
            .unwrap_or("?")
            .to_string();
        acc.take(
            &ch,
            format!("advanced_qualification_challenges[{id}]"),
            false,
        );
        if let Some(l) = ch.get("line").and_then(|x| x.as_u64()) {
            challenge_lines.insert(l as usize);
        }
    }
    let carried = std::mem::take(&mut acc.carried);
    drop(acc);

    // 1. every non-blank source line carried verbatim exactly once
    let mut by_line: BTreeMap<usize, Vec<(String, String)>> = BTreeMap::new();
    for (l, t, at) in carried {
        by_line.entry(l).or_default().push((t, at));
    }
    for (i, text) in src.iter().enumerate() {
        let n = i + 1;
        let got = by_line.remove(&n);
        if is_structural_blank(text) {
            if let Some(g) = got {
                d.push(difference(
                    view,
                    &g[0].1,
                    &format!("carries line {n}, which is blank or a thematic break in the source"),
                    None,
                    None,
                ));
            }
            continue;
        }
        match got {
            None => d.push(difference(
                view,
                &format!("source line {n}"),
                "not carried (content of the owner source is missing from this view)",
                Some(&json!(text)),
                None,
            )),
            Some(g) if g.len() > 1 => d.push(difference(
                view,
                &format!("source line {n}"),
                &format!(
                    "carried {} times ({})",
                    g.len(),
                    g.iter().map(|x| x.1.clone()).collect::<Vec<_>>().join(", ")
                ),
                Some(&json!(text)),
                None,
            )),
            Some(g) if g[0].0 != *text => d.push(difference(
                view,
                &format!("{} (source line {n})", g[0].1),
                "text differs from the owner source",
                Some(&json!(text)),
                Some(&json!(g[0].0)),
            )),
            _ => {}
        }
    }
    for (n, g) in by_line {
        d.push(difference(
            view,
            &g[0].1,
            &format!("carries line {n}, which the owner source does not have"),
            None,
            None,
        ));
    }

    // 2. structural placement, from the raw source text
    let mut cap_by_id: BTreeMap<String, &Value> = BTreeMap::new();
    for c in &caps {
        if let Some(id) = c.get("id").and_then(|x| x.as_str()) {
            cap_by_id.insert(id.to_string(), c);
        }
    }
    let top_or_cap = |t: &str| t.starts_with("# ") || t.starts_with("## ");
    let mut expected_ids: BTreeSet<String> = BTreeSet::new();
    let mut gate_label: Option<String> = None;
    let mut current_gate: Option<String> = None;
    for (i, text) in src.iter().enumerate() {
        let n = i + 1;
        if checklist_regex().is_match(text) && !item_lines.contains_key(&n) {
            d.push(difference(
                view,
                &format!("source line {n}"),
                "checklist line not carried as a checklist item",
                Some(&json!(text)),
                None,
            ));
        }
        if text.starts_with(CHALLENGE_PREFIX) && !challenge_lines.contains(&n) {
            d.push(difference(
                view,
                &format!("source line {n}"),
                "advanced-qualification challenge not carried as a challenge",
                Some(&json!(text)),
                None,
            ));
        }
        if text.starts_with("# ") {
            current_gate = None;
            gate_label = None;
        }
        if let Some(gm) = gate_heading_regex().captures(text) {
            let gid = gm[1].to_string();
            current_gate = Some(gid.clone());
            gate_label = label_regex().captures(text).map(|m| m[1].to_string());
            let gate_ok = lines_of(compiled, "gates").iter().any(|g| {
                g.get("id").and_then(|x| x.as_str()) == Some(gid.as_str())
                    && g.get("heading")
                        .and_then(|h| h.get("line"))
                        .and_then(|x| x.as_u64())
                        == Some(n as u64)
            });
            if !gate_ok {
                d.push(difference(
                    view,
                    &format!("gates[{gid}]"),
                    &format!("gate heading at line {n} not carried as a gate"),
                    Some(&json!(text)),
                    None,
                ));
            }
            let stop = src
                .iter()
                .enumerate()
                .skip(n)
                .find(|(_, t)| t.starts_with("# "))
                .map(|(j, _)| j + 1)
                .unwrap_or(src.len() + 1);
            let has_caps = src[n..stop - 1]
                .iter()
                .any(|t| capability_heading_regex().is_match(t));
            if !has_caps {
                // a gate that states its checklist without capability headings is a capability section (§9.4)
                expected_ids.insert(gid.clone());
                let c = cap_by_id.get(&gid);
                let ok = c
                    .map(|c| c.get("gate_capability").and_then(|x| x.as_bool()) == Some(true))
                    .unwrap_or(false);
                if !ok {
                    d.push(difference(view, &format!("capabilities[{gid}]"), &format!("gate {gid} (line {n}) states its checklist without capability headings; it is a capability section of the owner universe and is not carried as one"), None, None));
                }
                if let Some(c) = c {
                    let got = c
                        .get("requirement_class_label")
                        .cloned()
                        .unwrap_or(Value::Null);
                    let want = gate_label.clone().map(Value::String).unwrap_or(Value::Null);
                    if got != want {
                        d.push(difference(
                            view,
                            &format!("capabilities[{gid}].requirement_class_label"),
                            "label differs from the owner source",
                            Some(&want),
                            Some(&got),
                        ));
                    }
                    check_attribution(view, c, &gid, n, stop, &src, &mut d);
                }
            }
            continue;
        }
        if let Some(cm) = capability_heading_regex().captures(text) {
            let cid = cm[1].to_string();
            expected_ids.insert(cid.clone());
            match cap_by_id.get(&cid) {
                None => d.push(difference(
                    view,
                    &format!("capabilities[{cid}]"),
                    &format!("capability heading at line {n} not carried"),
                    Some(&json!(text)),
                    None,
                )),
                Some(c) => {
                    if c.get("heading")
                        .and_then(|h| h.get("line"))
                        .and_then(|x| x.as_u64())
                        != Some(n as u64)
                    {
                        d.push(difference(
                            view,
                            &format!("capabilities[{cid}].heading"),
                            &format!("does not carry the heading at line {n}"),
                            Some(&json!(text)),
                            None,
                        ));
                    }
                    if c.get("gate").and_then(|x| x.as_str()) != current_gate.as_deref() {
                        d.push(difference(
                            view,
                            &format!("capabilities[{cid}].gate"),
                            "gate differs from the owner source",
                            current_gate.as_ref().map(|g| json!(g)).as_ref(),
                            c.get("gate"),
                        ));
                    }
                    let own = label_regex().captures(text).map(|m| m[1].to_string());
                    let want = own
                        .or_else(|| gate_label.clone())
                        .map(Value::String)
                        .unwrap_or(Value::Null);
                    let got = c
                        .get("requirement_class_label")
                        .cloned()
                        .unwrap_or(Value::Null);
                    if got != want {
                        d.push(difference(
                            view,
                            &format!("capabilities[{cid}].requirement_class_label"),
                            "label differs from the owner source",
                            Some(&want),
                            Some(&got),
                        ));
                    }
                    let stop = src
                        .iter()
                        .enumerate()
                        .skip(n)
                        .find(|(_, t)| top_or_cap(t))
                        .map(|(j, _)| j + 1)
                        .unwrap_or(src.len() + 1);
                    check_attribution(view, c, &cid, n, stop, &src, &mut d);
                }
            }
        }
    }
    for id in cap_by_id.keys() {
        if !expected_ids.contains(id) {
            d.push(difference(
                view,
                &format!("capabilities[{id}]"),
                "unexpected (no such capability section in the owner source)",
                None,
                None,
            ));
        }
    }
    if compiled.get("capability_count").and_then(|x| x.as_u64()) != Some(expected_ids.len() as u64)
    {
        d.push(difference(
            view,
            "capability_count",
            "differs from the owner universe",
            Some(&json!(expected_ids.len())),
            compiled.get("capability_count"),
        ));
    }
    d
}

/// Every checklist item a capability carries must lie inside the section that textually contains it.
fn check_attribution(
    view: &str,
    c: &Value,
    cid: &str,
    start: usize,
    stop: usize,
    src: &[&str],
    d: &mut Vec<Value>,
) {
    let mut own = BTreeSet::new();
    for it in lines_of(c, "checklist") {
        if let Some(l) = it.get("line").and_then(|x| x.as_u64()) {
            let l = l as usize;
            own.insert(l);
            if l <= start || l >= stop {
                d.push(difference(
                    view,
                    &format!("capabilities[{cid}].checklist"),
                    &format!(
                        "carries line {l}, which lies outside the {cid} section (lines {start}–{})",
                        stop - 1
                    ),
                    None,
                    None,
                ));
            }
        }
    }
    for (j, t) in src
        .iter()
        .enumerate()
        .take(stop.saturating_sub(1))
        .skip(start)
    {
        if checklist_regex().is_match(t) && !own.contains(&(j + 1)) {
            d.push(difference(
                view,
                &format!("capabilities[{cid}].checklist"),
                &format!("does not carry the {cid} checklist line {}", j + 1),
                Some(&json!(t)),
                None,
            ));
        }
    }
}

fn schema_errors(
    view: &str,
    schema: &Value,
    def: Option<&str>,
    data: &Value,
) -> Result<Vec<Value>> {
    let root = match def {
        None => schema.clone(),
        Some(d) => json!({
            "$schema": schema.get("$schema").cloned().unwrap_or(Value::Null),
            "$id": schema.get("$id").cloned().unwrap_or(Value::Null),
            "$defs": schema.get("$defs").cloned().unwrap_or_else(|| json!({})),
            "$ref": format!("#/$defs/{d}"),
        }),
    };
    let compiled = jsonschema::JSONSchema::options()
        .with_draft(jsonschema::Draft::Draft202012)
        .compile(&root)
        .map_err(|e| {
            GovError::new(
                "CONTRACT_SCHEMA_INVALID",
                format!("{SCHEMA} does not compile as JSON Schema 2020-12: {e}"),
            )
        })?;
    let mut out = vec![];
    if let Err(errs) = compiled.validate(data) {
        for e in errs.take(50) {
            out.push(difference(
                view,
                &format!("{view}{}", e.instance_path),
                &format!("violates {SCHEMA}: {e}"),
                None,
                None,
            ));
        }
    }
    Ok(out)
}

/// Governed evidence-map values must be drawn from the vocabularies the owner source defines.
fn governed_vocabulary_differences(m: &ContractModel, map: &Value, d: &mut Vec<Value>) {
    let classes: BTreeSet<&str> = m
        .vocab
        .evidence_classes
        .iter()
        .map(|l| l.text.as_str())
        .collect();
    let fresh: BTreeSet<&str> = m
        .vocab
        .freshness_inputs
        .iter()
        .map(|l| l.text.as_str())
        .collect();
    let tiers: BTreeSet<String> = m.tier_ids().into_iter().collect();
    for row in lines_of(map, "capabilities") {
        let id = row
            .get("capability")
            .and_then(|x| x.as_str())
            .unwrap_or("?")
            .to_string();
        for k in governed_fields() {
            if row.get(k).is_none() {
                d.push(difference(
                    "evidence_map",
                    &format!("capabilities[{id}].{k}"),
                    "per-capability contract field (Contract v3:53-73) missing",
                    None,
                    None,
                ));
            }
        }
        for it in lines_of(&row, "checklist") {
            if it.get("automated_checks").is_none() {
                let iid = it.get("id").and_then(|x| x.as_str()).unwrap_or("?");
                d.push(difference(
                    "evidence_map",
                    &format!("capabilities[{id}].checklist[{iid}].automated_checks"),
                    "missing",
                    None,
                    None,
                ));
            }
        }
        let ec: Vec<String> = match row.get("evidence_class") {
            Some(Value::String(s)) => vec![s.clone()],
            Some(Value::Array(a)) => a
                .iter()
                .map(|x| x.as_str().unwrap_or("").to_string())
                .collect(),
            _ => vec![],
        };
        for c in &ec {
            if c != NOT_YET_MAPPED && !classes.contains(c.as_str()) {
                d.push(difference(
                    "evidence_map",
                    &format!("capabilities[{id}].evidence_class"),
                    "not an evidence class of Contract v3:81-91",
                    Some(&json!(classes.iter().collect::<Vec<_>>())),
                    Some(&json!(c)),
                ));
            }
        }
        if ec.len() > 1 && ec.iter().any(|c| c == NOT_YET_MAPPED) {
            d.push(difference(
                "evidence_map",
                &format!("capabilities[{id}].evidence_class"),
                "NOT_YET_MAPPED cannot be combined with an evidence class",
                None,
                row.get("evidence_class"),
            ));
        }
        if let Some(Value::Array(a)) = row.get("health_scheduler_tiers") {
            for t in a {
                if !t.as_str().map(|s| tiers.contains(s)).unwrap_or(false) {
                    d.push(difference(
                        "evidence_map",
                        &format!("capabilities[{id}].health_scheduler_tiers"),
                        "not a health-scheduler tier of O5",
                        Some(&json!(tiers)),
                        Some(t),
                    ));
                }
            }
        }
        if let Some(Value::Array(a)) = row.get("freshness_triggers") {
            for t in a {
                if !t.as_str().map(|s| fresh.contains(s)).unwrap_or(false) {
                    d.push(difference(
                        "evidence_map",
                        &format!("capabilities[{id}].freshness_triggers"),
                        "not an evidence-freshness input of Contract v3:97-109",
                        Some(&json!(fresh.iter().collect::<Vec<_>>())),
                        Some(t),
                    ));
                }
            }
        }
    }
}

/// Differences between an evidence map and the owner source (source-derived fields), its schema and the contract's
/// vocabularies (governed fields).
pub fn evidence_map_differences(
    m: &ContractModel,
    map: &Value,
    schema: &Value,
) -> Result<Vec<Value>> {
    let mut d = vec![];
    let expected = evidence_map_projection(&evidence_map(m, None));
    keyed_diff(
        "evidence_map",
        &expected,
        &evidence_map_projection(map),
        "",
        &mut d,
    );
    governed_vocabulary_differences(m, map, &mut d);
    d.extend(schema_errors(
        "evidence_map",
        schema,
        Some("evidence_map"),
        map,
    )?);
    Ok(d)
}

/// What regenerating the evidence map would silently drop from an existing (current-version) map: keys outside the
/// map's schema, and rows for capabilities the owner source does not have. `generate` refuses rather than discard.
fn uncarried_evidence_data(m: &ContractModel, existing: &Value) -> Vec<Value> {
    if existing
        .get("schema_version")
        .and_then(|v| v.as_u64())
        .unwrap_or(0)
        < DERIVED_VIEW_VERSION
    {
        // a version-1 map carried only the (empty) evidence_class / automated_checks placeholders, which are kept
        return vec![];
    }
    let mut row_keys: BTreeSet<&str> = [
        "capability",
        "title",
        "gate",
        "source_reference",
        "requirement_class",
        "requirement_class_label",
        "checklist",
        "statements",
        "qualification_challenge_ids",
    ]
    .into_iter()
    .collect();
    row_keys.extend(governed_fields());
    let item_keys: BTreeSet<&str> = ["id", "line", "number", "text", "group", "automated_checks"]
        .into_iter()
        .collect();
    let ids: BTreeSet<String> = m.capability_ids().into_iter().collect();
    let mut d = vec![];
    let top: BTreeSet<&str> = [
        "schema",
        "schema_version",
        "contract_version",
        "source_sha256",
        "note",
        "governed_fields",
        "gates",
        "advanced_qualification_challenges",
        "capabilities",
        "freshness_invalidation",
    ]
    .into_iter()
    .collect();
    if let Some(o) = existing.as_object() {
        for (k, v) in o {
            if !top.contains(k.as_str()) {
                d.push(difference(
                    "evidence_map",
                    k,
                    "would be discarded by regeneration",
                    None,
                    Some(v),
                ));
            }
        }
    }
    for row in lines_of(existing, "capabilities") {
        let id = row
            .get("capability")
            .and_then(|x| x.as_str())
            .unwrap_or("?")
            .to_string();
        if !ids.contains(&id) {
            d.push(difference(
                "evidence_map",
                &format!("capabilities[{id}]"),
                "row for a capability the owner source does not have",
                None,
                None,
            ));
        }
        if let Some(o) = row.as_object() {
            for (k, v) in o {
                if !row_keys.contains(k.as_str()) {
                    d.push(difference(
                        "evidence_map",
                        &format!("capabilities[{id}].{k}"),
                        "would be discarded by regeneration",
                        None,
                        Some(v),
                    ));
                }
            }
        }
        for it in lines_of(&row, "checklist") {
            let iid = it
                .get("id")
                .and_then(|x| x.as_str())
                .unwrap_or("?")
                .to_string();
            if let Some(o) = it.as_object() {
                for (k, v) in o {
                    if !item_keys.contains(k.as_str()) {
                        d.push(difference(
                            "evidence_map",
                            &format!("capabilities[{id}].checklist[{iid}].{k}"),
                            "would be discarded by regeneration",
                            None,
                            Some(v),
                        ));
                    }
                }
            }
        }
    }
    d
}

fn diverged(code: &str, what: &str, diffs: Vec<Value>, remedy: &str) -> GovError {
    let n = diffs.len();
    let head: Vec<String> = diffs
        .iter()
        .take(4)
        .map(|x| {
            format!(
                "{} {}{}",
                x["at"].as_str().unwrap_or(""),
                x["problem"].as_str().unwrap_or(""),
                match (&x.get("expected"), &x.get("found")) {
                    (Some(e), Some(f)) => format!(" (expected {e}, found {f})"),
                    (Some(e), None) => format!(" (expected {e})"),
                    (None, Some(f)) => format!(" (found {f})"),
                    _ => String::new(),
                }
            )
        })
        .collect();
    GovError::new(
        code,
        format!(
            "{what}: {n} difference(s) from the owner source {OWNER_SOURCE} — {}{}. Any semantic difference between the source and a derived representation is a hard failure (Contract v3, 'Contract authority model'). Remedy: {remedy}",
            head.join("; "),
            if n > 4 { "; …" } else { "" }
        ),
    )
    .with_details(json!({
        "difference_count": n,
        "differences": diffs.into_iter().take(MAX_REPORTED_DIFFERENCES).collect::<Vec<_>>(),
        "owner_source_sha256": OWNER_SOURCE_SHA256,
        "remedy": remedy,
    }))
}

const REGENERATE: &str = "regenerate every derived view from the approved source with `gov contract compile` (it preserves the governed evidence-map fields); never hand-edit a derived view and never edit the owner source";

fn read_import(repo_root: &Path, verb: &str) -> Result<String> {
    let import = read_text(&repo_root.join(CANONICAL_IMPORT)).map_err(|e| {
        GovError::new(
            "CONTRACT_SOURCE_MISSING",
            format!("the canonical Capability Acceptance Contract import is missing at {CANONICAL_IMPORT}: {}", e.message),
        )
    })?;
    let import_sha = sha256_text(&import);
    if import_sha != OWNER_SOURCE_SHA256 {
        return Err(GovError::new(
            "CONTRACT_SOURCE_DIVERGED",
            format!("{verb}{CANONICAL_IMPORT} has digest {import_sha}, the owner-approved source digest is {OWNER_SOURCE_SHA256}. The contract text may not be paraphrased, summarised or edited; restore the owner's exact bytes."),
        )
        .with_details(json!({"path": CANONICAL_IMPORT, "found_sha256": import_sha, "expected_sha256": OWNER_SOURCE_SHA256})));
    }
    Ok(import)
}

fn read_schema(repo_root: &Path) -> Result<(Value, String)> {
    let text = read_text(&repo_root.join(SCHEMA)).map_err(|e| {
        GovError::new(
            "CONTRACT_SCHEMA_MISSING",
            format!("{SCHEMA} is missing or unreadable: {}", e.message),
        )
    })?;
    let v: Value = serde_json::from_str(&text).map_err(|e| {
        GovError::new(
            "CONTRACT_SCHEMA_INVALID",
            format!("{SCHEMA} is not JSON: {e}"),
        )
    })?;
    Ok((v, sha256_text(&text)))
}

/// Everything derived from the approved source, computed once.
struct Derived {
    import: String,
    model: ContractModel,
    compiled: Value,
    schema: Value,
    schema_sha256: String,
}

fn derive(repo_root: &Path, verb: &str) -> Result<Derived> {
    let import = read_import(repo_root, verb)?;
    let model = parse(&import)?;
    let compiled = compile_model(&model);
    // The compiler must itself be lossless over the approved bytes; a lossy compiler is a product defect.
    let lossy = source_accounting("compiled (fresh)", &compiled, &import);
    if !lossy.is_empty() {
        return Err(diverged(
            "CONTRACT_COMPILER_LOSSY",
            "the contract compiler does not account for the approved source",
            lossy,
            "the compiler is defective; fix runtime/src/contracts.rs — the source must not be edited",
        ));
    }
    let (schema, schema_sha256) = read_schema(repo_root)?;
    let rejected = schema_errors("compiled (fresh)", &schema, None, &compiled)?;
    if !rejected.is_empty() {
        return Err(diverged(
            "CONTRACT_SCHEMA_DIVERGED",
            &format!("{SCHEMA} rejects the compiled form of the owner source (it must admit every owner-source capability, including Gate U)"),
            rejected,
            "correct the compiled-form schema so that it admits the owner universe, then regenerate",
        ));
    }
    Ok(Derived {
        import,
        model,
        compiled,
        schema,
        schema_sha256,
    })
}

/// Verify the whole chain, failing closed on any divergence.
///
/// Checks, in order:
/// 1. the canonical import exists and matches the owner-supplied digest pinned in [`OWNER_SOURCE_SHA256`], and, when
///    the owner source is present in this tree, is **byte-identical** to it; the source lock records that digest;
/// 2. the compiler accounts for every line of the approved source, and the compiled-form schema admits the result;
/// 3. the compiled YAML: independent line accounting against the source text, field-by-field comparison with the
///    owner-source model, schema validation, then equality with a fresh compilation (`CONTRACT_COMPILED_DIVERGED`);
/// 4. the evidence map: every source-derived field compared with the owner-source model, every governed Contract
///    v3:53-73 field present and drawn from the contract's vocabularies, schema validation
///    (`CONTRACT_EVIDENCE_MAP_DIVERGED`);
/// 5. the generated view: every element present as rendered, then equality with a fresh rendering
///    (`CONTRACT_GENERATED_VIEW_DIVERGED`);
/// 6. every field of the source lock (`CONTRACT_LOCK_DIVERGED`).
pub fn verify(repo_root: &Path) -> Result<Value> {
    let import = read_import(repo_root, "")?;
    let owner_path = repo_root.join(OWNER_SOURCE);
    let owner_present = owner_path.exists();
    if owner_present {
        let owner = read_text(&owner_path)?;
        if owner.as_bytes() != import.as_bytes() {
            return Err(GovError::new(
                "CONTRACT_SOURCE_DIVERGED",
                format!(
                    "{CANONICAL_IMPORT} is not byte-identical to the owner source {OWNER_SOURCE}"
                ),
            ));
        }
    }
    let lock: Value = crate::util::read_yaml(&repo_root.join(SOURCE_LOCK)).map_err(|e| {
        GovError::new(
            "CONTRACT_LOCK_MISSING",
            format!("{SOURCE_LOCK} is missing or unreadable: {}", e.message),
        )
    })?;
    let import_sha = sha256_text(&import);
    if lock["canonical_import_sha256"].as_str() != Some(import_sha.as_str())
        || lock["owner_source_sha256"].as_str() != Some(OWNER_SOURCE_SHA256)
    {
        return Err(GovError::new(
            "CONTRACT_LOCK_DIVERGED",
            format!("{SOURCE_LOCK} does not bind the approved source digest {OWNER_SOURCE_SHA256}"),
        )
        .with_details(lock.clone()));
    }
    let dv = derive(repo_root, "")?;

    // 3. the compiled form
    let on_disk: Value = crate::util::read_yaml(&repo_root.join(COMPILED)).map_err(|e| {
        GovError::new(
            "CONTRACT_COMPILED_MISSING",
            format!("{COMPILED} is missing or unreadable: {}", e.message),
        )
    })?;
    let mut d = source_accounting("compiled", &on_disk, &dv.import);
    keyed_diff("compiled", &dv.compiled, &on_disk, "", &mut d);
    d.extend(schema_errors("compiled", &dv.schema, None, &on_disk)?);
    if d.is_empty() && crate::util::hash_value(&on_disk) != crate::util::hash_value(&dv.compiled) {
        d.push(difference(
            "compiled",
            "",
            "differs from a fresh compilation of the approved source",
            Some(&json!(crate::util::hash_value(&dv.compiled))),
            Some(&json!(crate::util::hash_value(&on_disk))),
        ));
    }
    if !d.is_empty() {
        return Err(diverged(
            "CONTRACT_COMPILED_DIVERGED",
            &format!("{COMPILED} does not faithfully represent the approved source"),
            d,
            REGENERATE,
        ));
    }

    // 4. the evidence map
    let map: Value = crate::util::read_yaml(&repo_root.join(EVIDENCE_MAP)).map_err(|e| {
        GovError::new(
            "CONTRACT_EVIDENCE_MAP_MISSING",
            format!("{EVIDENCE_MAP} is missing or unreadable: {}", e.message),
        )
    })?;
    let d = evidence_map_differences(&dv.model, &map, &dv.schema)?;
    if !d.is_empty() {
        return Err(diverged(
            "CONTRACT_EVIDENCE_MAP_DIVERGED",
            &format!("{EVIDENCE_MAP} does not faithfully carry the approved source"),
            d,
            "restore the source-derived fields with `gov contract compile` (governed fields are preserved); governed values must come from the contract's vocabularies",
        ));
    }

    // 4b. the evidence owners (BC-P2-02, frozen AC-10): every capability has an owner that runs, every owner resolves,
    // and every field the owners determine is what they determine
    let registry = OwnerRegistry::load(repo_root);
    let owners = owner_differences(&dv.model, &map, &registry, false);
    if let Some(e) = owner_error(&owners) {
        return Err(e);
    }
    // 4c. no governed value changed since `gov contract compile` wrote it
    let governed_sha = crate::util::hash_value(&evidence_map_governed(&map));
    if lock
        .get("evidence_map_governed_sha256")
        .and_then(|v| v.as_str())
        != Some(governed_sha.as_str())
    {
        return Err(GovError::new(
            "CONTRACT_EVIDENCE_MAP_NOT_RECOMPILED",
            format!("{EVIDENCE_MAP}: its governed values (evidence owners and what they determine) are not the ones `gov contract compile` last resolved, derived and bound in {SOURCE_LOCK}. A governed value may change only through a recompile, which re-resolves every owner and re-derives every field the owners determine."),
        )
        .with_details(json!({"expected_sha256": lock.get("evidence_map_governed_sha256"), "found_sha256": governed_sha, "remedy": "gov contract compile"})));
    }

    // 5. the generated view
    let view = read_text(&repo_root.join(GENERATED_VIEW)).map_err(|e| {
        GovError::new(
            "CONTRACT_GENERATED_VIEW_MISSING",
            format!("{GENERATED_VIEW} is missing or unreadable: {}", e.message),
        )
    })?;
    let (expected_view, expectations) = render_view(&dv.model, &map);
    let present: BTreeSet<&str> = view.lines().collect();
    let mut d = vec![];
    for (what, line) in &expectations {
        if !present.contains(line.as_str()) {
            d.push(difference(
                "generated_view",
                what,
                "missing or altered",
                Some(&json!(line)),
                None,
            ));
        }
    }
    if view != expected_view {
        let el: Vec<&str> = expected_view.lines().collect();
        let fl: Vec<&str> = view.lines().collect();
        let k = el
            .iter()
            .zip(fl.iter())
            .position(|(a, b)| a != b)
            .unwrap_or(el.len().min(fl.len()));
        d.push(difference(
            "generated_view",
            &format!("line {}", k + 1),
            "differs from a fresh rendering of the owner source and evidence map",
            el.get(k).map(|s| json!(s)).as_ref(),
            fl.get(k).map(|s| json!(s)).as_ref(),
        ));
    }
    if !d.is_empty() {
        return Err(diverged(
            "CONTRACT_GENERATED_VIEW_DIVERGED",
            &format!("{GENERATED_VIEW} does not faithfully render the approved source"),
            d,
            REGENERATE,
        ));
    }

    // 6. the source lock, every field
    let expected_lock = source_lock(
        &dv.model,
        &dv.compiled,
        &crate::util::hash_value(&evidence_map_projection(&evidence_map(&dv.model, None))),
        &governed_sha,
        &sha256_text(&expected_view),
        &dv.schema_sha256,
    );
    let mut d = vec![];
    keyed_diff("source_lock", &expected_lock, &lock, "", &mut d);
    if !d.is_empty() {
        return Err(diverged(
            "CONTRACT_LOCK_DIVERGED",
            &format!("{SOURCE_LOCK} does not bind the current derived views"),
            d,
            REGENERATE,
        ));
    }

    let m = &dv.model;
    Ok(json!({
        "contract_version": CONTRACT_VERSION,
        "owner_source": OWNER_SOURCE,
        "owner_source_present_in_tree": owner_present,
        "owner_source_sha256": OWNER_SOURCE_SHA256,
        "canonical_import": CANONICAL_IMPORT,
        "canonical_import_byte_identical": true,
        "compiled": COMPILED,
        "capability_count": m.capabilities.len(),
        "gate_count": m.gates.len(),
        "checklist_item_count": m.item_count(),
        "statement_count": m.statement_count(),
        "qualification_challenge_count": m.challenges.len(),
        "source_lines": {"total": m.source_line_count, "carried_verbatim": m.carried_line_count(), "blank_or_thematic_break": m.excluded_line_count},
        "labelled_capabilities": m.capabilities.iter().filter(|c| c.label.is_some()).map(|c| json!({"capability": c.id, "requirement_class_label": c.label, "requirement_class": c.requirement_class})).collect::<Vec<_>>(),
        "source_lock": SOURCE_LOCK,
        "schema": SCHEMA,
        "evidence_map": EVIDENCE_MAP,
        "generated_view": GENERATED_VIEW,
        "evidence_owners": owners.summary,
        "evidence_map_governed_sha256": governed_sha,
        "checks": [
            "canonical import byte-identical to the owner source and equal to the pinned owner digest",
            "compiler line accounting: every non-blank line of the approved source carried verbatim exactly once",
            "compiled form: independent line accounting against the source text, and semantically identical to the owner source (universe incl. Gate U, checklist items, statements, challenges, labels, Contract v3:53-73 fields)",
            "compiled-form schema admits the owner universe and the compiled form",
            "evidence map: every capability, checklist item, statement, challenge and label of the owner source; every governed Contract v3:53-73 field present and drawn from the contract's vocabularies",
            "evidence owners (BC-P2-02, frozen AC-10): every capability names at least one owner that runs; every owner resolves against the product (scheduler catalogue tiers, G0 command classification, the test harnesses' module trees, held-out suites, frozen gate contract) or, where this tree does not carry those sources, is disclosed as deferred; evidence classes, tiers, freshness triggers, adoption/operational-audit owners and the remediation rule are what the owners determine; every freshness trigger in use names an owner proving invalidation",
            "governed values: bound by the source lock, so none changed without `gov contract compile`",
            "generated view: every element present and identical to a fresh rendering",
            "source lock: binds the source, the compiled form, the schema, the evidence map and the generated view",
        ],
        "verdict": "CONTRACT_SOURCE_BOUND",
    }))
}

/// Regenerate every derived artifact from the approved source. Used by the builder and by `gov contract compile`;
/// it never rewrites the source itself, and it preserves the governed evidence-map fields. It finishes by running
/// [`verify`], so it never reports success over a chain that does not verify.
pub fn generate(repo_root: &Path) -> Result<Value> {
    let dv = derive(repo_root, "refusing to compile: ")?;
    let map_path = repo_root.join(EVIDENCE_MAP);
    let existing = if map_path.exists() {
        Some(crate::util::read_yaml(&map_path).map_err(|e| {
            GovError::new(
                "CONTRACT_EVIDENCE_MAP_UNREADABLE",
                format!("{EVIDENCE_MAP} exists but cannot be read, so its governed evidence values cannot be preserved; refusing to overwrite it: {}", e.message),
            )
        })?)
    } else {
        None
    };
    if let Some(e) = &existing {
        let lost = uncarried_evidence_data(&dv.model, e);
        if !lost.is_empty() {
            return Err(diverged(
                "CONTRACT_EVIDENCE_MAP_DIVERGED",
                &format!("{EVIDENCE_MAP} holds data that regeneration would discard; refusing to overwrite it"),
                lost,
                "move the data into a governed field (the Contract v3:53-73 fields the owner source states no value for, or a checklist item's automated_checks), or extend the evidence-map schema and generator together",
            ));
        }
    }
    let mut map = evidence_map(&dv.model, existing.as_ref());
    complete_governed(&dv.model, &mut map);
    let d = evidence_map_differences(&dv.model, &map, &dv.schema)?;
    if !d.is_empty() {
        return Err(diverged(
            "CONTRACT_EVIDENCE_MAP_DIVERGED",
            &format!("the governed values carried over from {EVIDENCE_MAP} are invalid; refusing to write"),
            d,
            "correct the governed evidence-map values (vocabularies: Contract v3:81-91, :97-109, O5 tiers)",
        ));
    }
    // every owner is resolved here, where the owners' sources are: compile never defers and never binds an owner it
    // could not resolve (BC-P2-02)
    let owners = owner_differences(&dv.model, &map, &OwnerRegistry::load(repo_root), true);
    if let Some(mut e) = owner_error(&owners) {
        e.message = format!("refusing to compile: {}", e.message);
        return Err(e);
    }
    let (view, _) = render_view(&dv.model, &map);
    let lock = source_lock(
        &dv.model,
        &dv.compiled,
        &crate::util::hash_value(&evidence_map_projection(&evidence_map(&dv.model, None))),
        &crate::util::hash_value(&evidence_map_governed(&map)),
        &sha256_text(&view),
        &dv.schema_sha256,
    );
    crate::util::write_yaml(&repo_root.join(COMPILED), &dv.compiled)?;
    crate::util::write_yaml(&map_path, &map)?;
    crate::util::write_text(&repo_root.join(GENERATED_VIEW), &view)?;
    crate::util::write_yaml(&repo_root.join(SOURCE_LOCK), &lock)?;
    let verified = verify(repo_root)?;
    Ok(json!({
        "compiled": COMPILED,
        "source_lock": SOURCE_LOCK,
        "evidence_map": EVIDENCE_MAP,
        "generated_view": GENERATED_VIEW,
        "capability_count": dv.model.capabilities.len(),
        "checklist_item_count": dv.model.item_count(),
        "source_sha256": dv.model.source_sha256,
        "governed_values_preserved_from_existing_map": existing.is_some(),
        "verify": verified,
    }))
}

// ------------------------------------------------------------------------------------------ evidence owners (BC-P2-02)
//
// Frozen gate contract AC-10: "every required capability has at least one evidence owner (G0 guard, G1 mutation, G2
// task-close, G3 checkpoint/handoff, G4 milestone, G5 full suite, G6 qualification, independent held-out
// verification, Human Decision Gate evidence, release/clean-clone evidence). No required capability has zero evidence
// owners." Contract v3:64-65 name the fields that carry them: "automated check/test IDs" and "independent-verification
// obligation".
//
// An owner is an object in a capability's `automated_checks` or, for an independent owner, in its
// `independent_verification`: `{id: "<kind>:<reference>", class: <Contract v3:83-91 evidence class>, ...}`. `gov
// contract verify` resolves every reference against the product itself — the scheduler catalogue, the G0 command
// classification and the kernel payload compiled into this binary, and, from the tree, the test harnesses' module
// trees, the independent held-out suites and the frozen gate contract — and derives what the owners determine
// (evidence classes, health-scheduler tiers, evidence-freshness triggers, the adoption/operational-audit owners and the
// remediation rule), so none of those can be asserted without an owner that carries it.

/// One kind of evidence owner.
#[derive(Debug, Clone, Copy)]
pub struct OwnerKind {
    /// The id prefix: an owner id is `<prefix>:<reference>`.
    pub prefix: &'static str,
    /// An independent owner (Contract v3:65; O3): named only in `independent_verification`, never as builder evidence.
    pub independent: bool,
    /// Runs at health-scheduler tiers: the owner states `tiers`, which must equal what the product declares.
    pub tiered: bool,
    /// Counts toward the minimum of one running owner per capability. An obligation the frozen gate contract assigns
    /// to a future independent verifier is recorded, but it is not a running owner of its own.
    pub runs: bool,
    /// The Contract v3:83-91 evidence classes an owner of this kind may carry.
    pub classes: &'static [&'static str],
    /// What the reference names and how it is resolved.
    pub resolves: &'static str,
}

/// Every kind of evidence owner the map may name.
pub const OWNER_KINDS: &[OwnerKind] = &[
    OwnerKind {
        prefix: "check",
        independent: false,
        tiered: true,
        runs: true,
        classes: &["governance health check"],
        resolves: "a governance-suite family the scheduler catalogue declares (`scheduler::catalogue`) and the kernel TEST_POLICY runs; `tiers` equals the catalogue's",
    },
    OwnerKind {
        prefix: "doctor",
        independent: false,
        tiered: true,
        runs: true,
        classes: &["governance health check"],
        resolves: "a `gov doctor` check the scheduler catalogue declares; `tiers` equals the catalogue's",
    },
    OwnerKind {
        prefix: "g0",
        independent: false,
        tiered: true,
        runs: true,
        classes: &["automated invariant/guard"],
        resolves: "a command label `orchestration::control::COMMAND_GUARDS` classifies for a governed project: the G0 guard decides every invocation of it before anything runs (`tiers: [G0]`)",
    },
    OwnerKind {
        prefix: "test",
        independent: false,
        tiered: false,
        runs: true,
        classes: &[
            "unit/integration/system test",
            "migration/rollback evidence",
            "clean-clone/release evidence",
        ],
        resolves: "`test:<harness>:<path>`: a test the harness runs (`lib` = `cargo test --lib`, `certification` = `cargo test --test certification`), resolved through the crate's module tree from its root file, and not `#[ignore]`d",
    },
    OwnerKind {
        prefix: "human-gate",
        independent: false,
        tiered: false,
        runs: true,
        classes: &["human-gate evidence"],
        resolves: "a command label `orchestration::control::COMMAND_GUARDS` classifies that produces Human Decision Gate evidence, with the `record` type it writes (a kernel record type or kernel schema)",
    },
    OwnerKind {
        prefix: "release",
        independent: false,
        tiered: false,
        runs: true,
        classes: &["clean-clone/release evidence"],
        resolves: "a command label `orchestration::control::COMMAND_GUARDS` classifies that produces release or clean-clone evidence, with the `record` type it writes (a kernel record type or kernel schema)",
    },
    OwnerKind {
        prefix: "heldout",
        independent: true,
        tiered: false,
        runs: true,
        classes: &["independent held-out test"],
        resolves: "an independent held-out suite directory `release/verification/<run>/evidence/heldout-tests` carrying its crate manifest (`Cargo.toml.txt`); each `tests` entry `<binary>::<fn>` is a `#[test]` of that suite",
    },
    OwnerKind {
        prefix: "obligation",
        independent: true,
        tiered: false,
        runs: false,
        classes: &["independent held-out test", "independent audit evidence"],
        resolves: "an acceptance criterion (`AC-<n>`) of the frozen Phase-2 gate contract whose text assigns the work to an independent verifier or reviewer",
    },
];

/// The kind an owner id names.
pub fn owner_kind(id: &str) -> Option<&'static OwnerKind> {
    let (prefix, rest) = id.split_once(':')?;
    if rest.trim().is_empty() {
        return None;
    }
    OWNER_KINDS.iter().find(|k| k.prefix == prefix)
}

/// The test harnesses a `test:` owner may name: (harness, crate root file, command that runs it).
pub const TEST_HARNESSES: &[(&str, &str, &str)] = &[
    ("lib", "runtime/src/lib.rs", "cargo test --lib"),
    (
        "certification",
        "tests/certification/main.rs",
        "cargo test --test certification",
    ),
];
/// Where the independent held-out suites live.
pub const HELDOUT_ROOT: &str = "release/verification";
/// The frozen Phase-2 gate contract whose acceptance criteria an `obligation:` owner names.
pub const FROZEN_GATE_CONTRACT: &str =
    "release/orchestration/phase-2/GATES/PHASE-2-FROZEN-GATE-CONTRACT.md";

/// Allowed capability statuses: the frozen gate contract §4 vocabulary, which compiles Contract v3:93
/// (`PRESENT_AND_SUBSTANTIAL`), :1202-1203 (`ABSENT`, `UNCLEAR`, `PARTIAL`) and V8.2 CAP-1's `N/A_WITH_REASON`
/// (Contract v3:514-515: "silent N/A is invalid").
pub const STATUS_VOCABULARY: &[&str] = &[
    "PRESENT_AND_SUBSTANTIAL",
    "PARTIAL",
    "ABSENT",
    "UNCLEAR",
    "N/A_WITH_REASON",
];
/// Contract v3:62 applicability rule, as the Phase-2 sources state it for every capability.
pub const APPLICABILITY_RULE: &str = "required: every capability of the owner source is required unless it is recorded N/A_WITH_REASON (frozen gate contract AC-2, §4); the same contract applies at every lifecycle point of Contract v3:115-127";
/// Contract v3:72 N/A requirements, as the sources state them for every capability.
pub const NA_REQUIREMENTS: &str = "N/A only as N/A_WITH_REASON citing the exact normative text that places the obligation outside the lifecycle being judged; silent N/A is invalid (Contract v3:514-515; frozen gate contract AC-2, §4)";
/// The Contract v3:115-127 lifecycle points the adoption obligation refers to.
const ADOPTION_POINTS: &[&str] = &["`gov adopt`", "post-adoption acceptance"];
/// The Contract v3:115-127 lifecycle point the periodic operational-audit obligation refers to.
const OPERATIONAL_POINTS: &[&str] = &["periodic operational governance-health audits"];
const ADOPTION_WITH: &str = "re-established in the adopted project by the owners listed, which run at G5: `gov adopt` runs the full suite at A11 and post-adoption acceptance re-runs it (Contract v3:122-123; O5 G5)";
const ADOPTION_WITHOUT: &str = "no owner of this capability runs inside an adopted project: the adopted release carries the capability on that release's own evidence (its test and independent owners), which is re-established for every release (Contract v3:122-123)";
const OPERATIONAL_WITH: &str = "re-evaluated by the owners listed at every periodic operational audit (`gov audit` runs the G5 full suite) (Contract v3:126; O5 G5)";
const OPERATIONAL_WITHOUT: &str = "no owner runs at a project's periodic operational audit: the capability is re-established with each release's evidence (Contract v3:126)";
const REMEDIATION_TIERED: &str = "a failing finding of a tier owner is an audit finding that generates linked, governed remediation work (`orchestration::generation`; Contract v3 I3:573-575; frozen AC-5); a hard-block owner refuses what relies on the failing state and admits that work as the block's remedy (availability rule, P2-HO-0031)";
const REMEDIATION_UNTIERED: &str = "a failing owner test or held-out result is a failed test (Contract v3 I3:574): the candidate's regression is not green (frozen AC-15) and the failure is repaired as governed work before the capability is relied on";

// --------------------------------------------------------------------------- the test harnesses' module trees

/// One `#[test]` function found in a harness's module tree.
#[derive(Debug, Clone, PartialEq)]
pub struct TestSite {
    /// Repository-relative file.
    pub file: String,
    pub line: usize,
    pub ignored: bool,
}

/// Replace the contents of comments, string, byte-string, raw-string and character literals with spaces, keeping
/// every newline and every byte offset, so braces, attributes and items can be read without being fooled by text.
fn blank_non_code(src: &str) -> String {
    let b = src.as_bytes();
    let n = b.len();
    let mut out: Vec<u8> = Vec::with_capacity(n);
    let blank = |c: u8| if c == b'\n' { b'\n' } else { b' ' };
    let ident = |c: u8| c.is_ascii_alphanumeric() || c == b'_';
    let mut i = 0;
    while i < n {
        let c = b[i];
        let prev_ident = i > 0 && ident(b[i - 1]);
        if c == b'/' && i + 1 < n && b[i + 1] == b'/' {
            while i < n && b[i] != b'\n' {
                out.push(b' ');
                i += 1;
            }
            continue;
        }
        if c == b'/' && i + 1 < n && b[i + 1] == b'*' {
            let mut depth = 0usize;
            while i < n {
                if i + 1 < n && b[i] == b'/' && b[i + 1] == b'*' {
                    depth += 1;
                    out.extend_from_slice(b"  ");
                    i += 2;
                } else if i + 1 < n && b[i] == b'*' && b[i + 1] == b'/' {
                    depth = depth.saturating_sub(1);
                    out.extend_from_slice(b"  ");
                    i += 2;
                    if depth == 0 {
                        break;
                    }
                } else {
                    out.push(blank(b[i]));
                    i += 1;
                }
            }
            continue;
        }
        // raw strings: r"…", r#"…"#, br"…", br#"…"#
        if !prev_ident && (c == b'r' || (c == b'b' && i + 1 < n && b[i + 1] == b'r')) {
            let mut j = if c == b'b' { i + 2 } else { i + 1 };
            let mut hashes = 0usize;
            while j < n && b[j] == b'#' {
                hashes += 1;
                j += 1;
            }
            if j < n && b[j] == b'"' {
                out.extend_from_slice(&b[i..=j]);
                j += 1;
                loop {
                    if j >= n {
                        break;
                    }
                    if b[j] == b'"'
                        && n >= j + 1 + hashes
                        && b[j + 1..j + 1 + hashes].iter().all(|x| *x == b'#')
                    {
                        out.push(b'"');
                        out.extend(std::iter::repeat(b'#').take(hashes));
                        j += 1 + hashes;
                        break;
                    }
                    out.push(blank(b[j]));
                    j += 1;
                }
                i = j;
                continue;
            }
        }
        // strings and byte strings
        if c == b'"' || (!prev_ident && c == b'b' && i + 1 < n && b[i + 1] == b'"') {
            let start = if c == b'b' { i + 1 } else { i };
            out.extend_from_slice(&b[i..=start]);
            let mut j = start + 1;
            while j < n {
                if b[j] == b'\\' && j + 1 < n {
                    out.push(b' ');
                    out.push(blank(b[j + 1]));
                    j += 2;
                    continue;
                }
                if b[j] == b'"' {
                    out.push(b'"');
                    j += 1;
                    break;
                }
                out.push(blank(b[j]));
                j += 1;
            }
            i = j;
            continue;
        }
        // character literals (a lifetime has no closing quote)
        if c == b'\'' {
            if i + 3 < n && b[i + 1] == b'\\' {
                if let Some(end) = b[i + 3..].iter().take(12).position(|x| *x == b'\'') {
                    let stop = i + 3 + end;
                    out.push(b'\'');
                    out.extend(std::iter::repeat(b' ').take(stop - i - 1));
                    out.push(b'\'');
                    i = stop + 1;
                    continue;
                }
            } else if i + 1 < n {
                let width = match b[i + 1] {
                    x if x < 0x80 => 1,
                    x if x >= 0xF0 => 4,
                    x if x >= 0xE0 => 3,
                    _ => 2,
                };
                if i + 1 + width < n && b[i + 1 + width] == b'\'' {
                    out.push(b'\'');
                    out.extend(std::iter::repeat(b' ').take(width));
                    out.push(b'\'');
                    i += width + 2;
                    continue;
                }
            }
        }
        out.push(c);
        i += 1;
    }
    String::from_utf8(out).unwrap_or_default()
}

#[derive(Debug, Clone, PartialEq)]
enum Tok {
    Ident(String),
    Punct(char),
}

fn tokens(code: &str) -> Vec<(Tok, usize)> {
    let mut v = vec![];
    let mut line = 1usize;
    let chars: Vec<char> = code.chars().collect();
    let mut i = 0;
    while i < chars.len() {
        let c = chars[i];
        if c == '\n' {
            line += 1;
            i += 1;
        } else if c.is_alphabetic() || c == '_' {
            let s = i;
            while i < chars.len() && (chars[i].is_alphanumeric() || chars[i] == '_') {
                i += 1;
            }
            v.push((Tok::Ident(chars[s..i].iter().collect()), line));
        } else if c.is_whitespace() || c.is_ascii_digit() {
            i += 1;
        } else {
            v.push((Tok::Punct(c), line));
            i += 1;
        }
    }
    v
}

/// The directory a file module's child `mod x;` files live in.
fn child_dir(file: &Path) -> PathBuf {
    let dir = file.parent().map(Path::to_path_buf).unwrap_or_default();
    match file.file_name().and_then(|f| f.to_str()) {
        Some("lib.rs") | Some("main.rs") | Some("mod.rs") => dir,
        _ => dir.join(
            file.file_stem()
                .and_then(|s| s.to_str())
                .unwrap_or_default(),
        ),
    }
}

fn scan_module_file(
    repo_root: &Path,
    file: &Path,
    module: &[String],
    out: &mut BTreeMap<String, TestSite>,
    seen: &mut BTreeSet<PathBuf>,
) {
    if !seen.insert(file.to_path_buf()) {
        return;
    }
    let Ok(src) = std::fs::read_to_string(file) else {
        return;
    };
    let rel = crate::util::rel_posix(file, repo_root);
    let toks = tokens(&blank_non_code(&src));
    // the brace stack: Some(name) for an inline module, None for any other block
    let mut stack: Vec<Option<String>> = vec![];
    let (mut test_attr, mut ignore_attr) = (false, false);
    let mut i = 0;
    let at = |i: usize| toks.get(i).map(|t| &t.0);
    while i < toks.len() {
        match &toks[i].0 {
            Tok::Punct('#') => {
                let mut j = i + 1;
                if at(j) == Some(&Tok::Punct('!')) {
                    j += 1;
                }
                if at(j) == Some(&Tok::Punct('[')) {
                    let mut depth = 0i32;
                    let mut k = j;
                    let mut inner: Vec<&Tok> = vec![];
                    while k < toks.len() {
                        match &toks[k].0 {
                            Tok::Punct('[') => depth += 1,
                            Tok::Punct(']') => {
                                depth -= 1;
                                if depth == 0 {
                                    break;
                                }
                            }
                            t => inner.push(t),
                        }
                        k += 1;
                    }
                    match inner.first() {
                        Some(Tok::Ident(a)) if a == "test" && inner.len() == 1 => test_attr = true,
                        Some(Tok::Ident(a)) if a == "ignore" => ignore_attr = true,
                        _ => {}
                    }
                    i = k + 1;
                    continue;
                }
                i += 1;
            }
            Tok::Ident(w) if w == "mod" => {
                if let (Some(Tok::Ident(name)), next) = (at(i + 1), at(i + 2)) {
                    let name = name.clone();
                    if next == Some(&Tok::Punct('{')) {
                        stack.push(Some(name));
                        test_attr = false;
                        ignore_attr = false;
                        i += 3;
                        continue;
                    }
                    if next == Some(&Tok::Punct(';')) {
                        let inline: Vec<String> = stack.iter().flatten().cloned().collect();
                        if stack.iter().all(|f| f.is_some()) {
                            let mut dir = child_dir(file);
                            for m in &inline {
                                dir = dir.join(m);
                            }
                            let cand = [
                                dir.join(format!("{name}.rs")),
                                dir.join(&name).join("mod.rs"),
                            ];
                            if let Some(f) = cand.iter().find(|p| p.is_file()) {
                                let mut child: Vec<String> = module.to_vec();
                                child.extend(inline);
                                child.push(name);
                                scan_module_file(repo_root, f, &child, out, seen);
                            }
                        }
                        test_attr = false;
                        ignore_attr = false;
                        i += 3;
                        continue;
                    }
                }
                i += 1;
            }
            Tok::Ident(w) if w == "fn" => {
                if let Some(Tok::Ident(name)) = at(i + 1) {
                    if test_attr && stack.iter().all(|f| f.is_some()) {
                        let mut path: Vec<String> = module.to_vec();
                        path.extend(stack.iter().flatten().cloned());
                        path.push(name.clone());
                        out.insert(
                            path.join("::"),
                            TestSite {
                                file: rel.clone(),
                                line: toks[i].1,
                                ignored: ignore_attr,
                            },
                        );
                    }
                }
                test_attr = false;
                ignore_attr = false;
                i += 2;
            }
            Tok::Punct('{') => {
                stack.push(None);
                test_attr = false;
                ignore_attr = false;
                i += 1;
            }
            Tok::Punct('}') => {
                stack.pop();
                i += 1;
            }
            Tok::Punct(';') => {
                test_attr = false;
                ignore_attr = false;
                i += 1;
            }
            _ => i += 1,
        }
    }
}

/// Every `#[test]` function a harness runs, by the path the harness lists it under (`module::…::fn`), read by
/// following the crate's module tree from its root file exactly as the compiler does (`mod x;` → `x.rs` or
/// `x/mod.rs`; inline `mod x { … }`), with comments and literals blanked. `None` when the tree does not carry the
/// harness's root file. The certification suite checks this index against the harness's own `--list`.
pub fn test_index(repo_root: &Path, harness: &str) -> Option<BTreeMap<String, TestSite>> {
    let (_, entry, _) = TEST_HARNESSES.iter().find(|h| h.0 == harness)?;
    let root_file = repo_root.join(entry);
    if !root_file.is_file() {
        return None;
    }
    let mut out = BTreeMap::new();
    scan_module_file(repo_root, &root_file, &[], &mut out, &mut BTreeSet::new());
    Some(out)
}

/// The `#[test]` functions of one held-out suite file (`<suite>/<binary>.rs`), by `<binary>::<fn>`.
fn heldout_tests(file: &Path, repo_root: &Path, binary: &str) -> BTreeMap<String, TestSite> {
    let mut out = BTreeMap::new();
    scan_module_file(
        repo_root,
        file,
        &[binary.to_string()],
        &mut out,
        &mut BTreeSet::new(),
    );
    out
}

// --------------------------------------------------------------------------- resolution

/// The outcome of resolving one owner reference.
#[derive(Debug, Clone, PartialEq)]
pub enum Resolution {
    /// It exists and runs; the value locates it (file and line, catalogue declaration, guard class …).
    Resolved(Value),
    /// This tree does not carry what the reference is resolved in (a release-tooling tree with no test sources); the
    /// reason is disclosed. `gov contract compile` never defers: it resolves every owner where the sources are.
    Deferred(String),
    /// It does not exist, or does not run as named.
    Unresolved(String),
}

/// Everything owner references are resolved against.
pub struct OwnerRegistry {
    root: PathBuf,
    tests: BTreeMap<&'static str, Option<BTreeMap<String, TestSite>>>,
    suite_families: BTreeSet<String>,
    gate_contract: Option<String>,
    heldout_present: bool,
}

fn embedded_suite_families() -> BTreeSet<String> {
    crate::kernel::embedded::files()
        .iter()
        .find(|(p, _)| *p == "policies/TEST_POLICY.yaml")
        .and_then(|(_, b)| serde_yaml::from_slice::<Value>(b).ok())
        .and_then(|v| {
            v.get("governance_families").and_then(|l| {
                l.as_array().map(|a| {
                    a.iter()
                        .filter_map(|x| x.as_str().map(String::from))
                        .collect()
                })
            })
        })
        .unwrap_or_default()
}

fn record_type_known(t: &str) -> bool {
    crate::records::TYPE_DIR.iter().any(|(ty, _)| *ty == t)
        || crate::kernel::embedded::files()
            .iter()
            .any(|(p, _)| *p == format!("schemas/{t}.schema.json"))
}

impl OwnerRegistry {
    /// Read everything the tree carries. Nothing is required: what is absent defers the owners resolved in it.
    pub fn load(repo_root: &Path) -> Self {
        let mut tests = BTreeMap::new();
        for (h, _, _) in TEST_HARNESSES {
            tests.insert(*h, test_index(repo_root, h));
        }
        OwnerRegistry {
            root: repo_root.to_path_buf(),
            tests,
            suite_families: embedded_suite_families(),
            gate_contract: std::fs::read_to_string(repo_root.join(FROZEN_GATE_CONTRACT)).ok(),
            heldout_present: repo_root.join(HELDOUT_ROOT).is_dir(),
        }
    }

    /// The test index of a harness, when the tree carries it.
    pub fn tests(&self, harness: &str) -> Option<&BTreeMap<String, TestSite>> {
        self.tests.get(harness).and_then(|t| t.as_ref())
    }

    /// What the tree does not carry, by owner kind (for disclosure).
    pub fn absent_sources(&self) -> Vec<String> {
        let mut v = vec![];
        for (h, entry, _) in TEST_HARNESSES {
            if self.tests(h).is_none() {
                v.push(format!("test harness `{h}` ({entry})"));
            }
        }
        if !self.heldout_present {
            v.push(format!("independent held-out suites ({HELDOUT_ROOT})"));
        }
        if self.gate_contract.is_none() {
            v.push(format!("frozen gate contract ({FROZEN_GATE_CONTRACT})"));
        }
        v
    }

    /// Resolve an owner reference by its id alone (tiers, class and record are checked by [`owner_differences`]).
    pub fn resolve_id(&self, id: &str, record: Option<&str>, tests: &[String]) -> Resolution {
        use crate::orchestration::control::{Scope, COMMAND_GUARDS};
        use crate::scheduler::catalogue::{self, Surface};
        let Some(kind) = owner_kind(id) else {
            return Resolution::Unresolved(format!(
                "not an owner id: `<kind>:<reference>` with kind one of {}",
                OWNER_KINDS
                    .iter()
                    .map(|k| k.prefix)
                    .collect::<Vec<_>>()
                    .join(", ")
            ));
        };
        let reference = &id[kind.prefix.len() + 1..];
        match kind.prefix {
            "check" | "doctor" => {
                let want = if kind.prefix == "check" {
                    Surface::Family
                } else {
                    Surface::Doctor
                };
                match catalogue::get(reference) {
                    Some(def) if def.surface == want => {
                        if want == Surface::Family && !self.suite_families.contains(reference) {
                            return Resolution::Unresolved(format!("`{reference}` is declared in the scheduler catalogue but the kernel TEST_POLICY governance_families does not run it"));
                        }
                        Resolution::Resolved(json!({
                            "declared_in": "runtime/src/scheduler/catalogue.rs",
                            "surface": if want == Surface::Family { "governance-family" } else { "doctor" },
                            "tiers": def.tiers.iter().map(|t| t.as_str()).collect::<Vec<_>>(),
                            "duty": def.duty,
                            "enforcement": catalogue::enforcement(def)["mode"],
                        }))
                    }
                    Some(_) => Resolution::Unresolved(format!(
                        "`{reference}` is a scheduler check of the other surface (use `{}:`)",
                        if kind.prefix == "check" {
                            "doctor"
                        } else {
                            "check"
                        }
                    )),
                    None => Resolution::Unresolved(format!(
                        "no check `{reference}` in the scheduler catalogue"
                    )),
                }
            }
            "g0" | "human-gate" | "release" => {
                let Some(g) = COMMAND_GUARDS.iter().find(|c| c.label == reference) else {
                    return Resolution::Unresolved(format!(
                        "no command `{reference}` in orchestration::control::COMMAND_GUARDS"
                    ));
                };
                let scope = match g.scope {
                    Scope::Project => "project".to_string(),
                    Scope::Outside(why) => format!("outside a governed project: {why}"),
                };
                if kind.prefix == "g0" {
                    if !matches!(g.scope, Scope::Project) {
                        return Resolution::Unresolved(format!(
                            "`{reference}` is not guarded by G0 ({scope})"
                        ));
                    }
                    return Resolution::Resolved(
                        json!({"declared_in": "runtime/src/orchestration/control.rs", "authority": g.authority, "effect": format!("{:?}", g.effect), "scope": scope, "tiers": ["G0"]}),
                    );
                }
                match record {
                    None => Resolution::Unresolved(format!(
                        "a `{}:` owner names the `record` type its command writes",
                        kind.prefix
                    )),
                    Some(r) if !record_type_known(r) => Resolution::Unresolved(format!(
                        "`{r}` is neither a kernel record type nor a kernel schema"
                    )),
                    Some(r) => Resolution::Resolved(
                        json!({"declared_in": "runtime/src/orchestration/control.rs", "authority": g.authority, "scope": scope, "record": r}),
                    ),
                }
            }
            "test" => {
                let Some((harness, path)) = reference.split_once(':') else {
                    return Resolution::Unresolved(
                        "a test owner is `test:<harness>:<path>`".into(),
                    );
                };
                let Some((_, entry, cmd)) = TEST_HARNESSES.iter().find(|h| h.0 == harness) else {
                    return Resolution::Unresolved(format!(
                        "unknown test harness `{harness}` (lib, certification)"
                    ));
                };
                match self.tests.get(harness).and_then(|t| t.as_ref()) {
                    None => Resolution::Deferred(format!(
                        "this tree does not carry {entry}, the root of `{cmd}`"
                    )),
                    Some(idx) => match idx.get(path) {
                        None => Resolution::Unresolved(format!(
                            "`{cmd}` has no test `{path}` (resolved from {entry})"
                        )),
                        Some(s) if s.ignored => Resolution::Unresolved(format!(
                            "`{path}` is #[ignore]d: `{cmd}` does not run it"
                        )),
                        Some(s) => Resolution::Resolved(
                            json!({"harness": harness, "command": cmd, "file": s.file, "line": s.line}),
                        ),
                    },
                }
            }
            "heldout" => {
                let rel = reference.trim_end_matches('/');
                let shaped = rel.starts_with(&format!("{HELDOUT_ROOT}/"))
                    && rel.ends_with("/heldout-tests")
                    && !rel.split('/').any(|s| s == ".." || s.is_empty());
                if !shaped {
                    return Resolution::Unresolved(format!(
                        "a held-out owner names a directory {HELDOUT_ROOT}/<run>/evidence/heldout-tests"
                    ));
                }
                if !self.heldout_present {
                    return Resolution::Deferred(format!(
                        "this tree does not carry {HELDOUT_ROOT}"
                    ));
                }
                let dir = self.root.join(rel);
                if !dir.join("Cargo.toml.txt").is_file() {
                    return Resolution::Unresolved(format!(
                        "{rel} does not carry a held-out suite (no Cargo.toml.txt)"
                    ));
                }
                let mut located = vec![];
                for t in tests {
                    let Some((bin, _)) = t.split_once("::") else {
                        return Resolution::Unresolved(format!(
                            "held-out test `{t}` is not `<binary>::<fn>`"
                        ));
                    };
                    let file = dir.join(format!("{bin}.rs"));
                    let found = heldout_tests(&file, &self.root, bin);
                    match found.get(t.as_str()) {
                        Some(s) => located.push(json!({"test": t, "file": s.file, "line": s.line})),
                        None => {
                            return Resolution::Unresolved(format!(
                                "the held-out suite {rel} has no test `{t}`"
                            ))
                        }
                    }
                }
                Resolution::Resolved(json!({"suite": rel, "tests": located}))
            }
            "obligation" => {
                let ok_id = reference.starts_with("AC-")
                    && reference[3..].chars().all(|c| c.is_ascii_digit())
                    && reference.len() > 3;
                if !ok_id {
                    return Resolution::Unresolved(
                        "an obligation names an acceptance criterion `AC-<n>` of the frozen gate contract".into(),
                    );
                }
                let Some(text) = &self.gate_contract else {
                    return Resolution::Deferred(format!(
                        "this tree does not carry {FROZEN_GATE_CONTRACT}"
                    ));
                };
                let row = text
                    .lines()
                    .enumerate()
                    .find(|(_, l)| l.starts_with(&format!("| {reference} |")));
                match row {
                    None => Resolution::Unresolved(format!(
                        "the frozen gate contract has no criterion {reference}"
                    )),
                    Some((_, l))
                        if !["independent verifier", "independent reviewer", "independent wherever"]
                            .iter()
                            .any(|w| l.to_lowercase().contains(w)) =>
                    {
                        Resolution::Unresolved(format!(
                            "{reference} does not assign its work to an independent verifier or reviewer"
                        ))
                    }
                    Some((n, _)) => Resolution::Resolved(
                        json!({"declared_in": FROZEN_GATE_CONTRACT, "line": n + 1}),
                    ),
                }
            }
            _ => Resolution::Unresolved("unknown owner kind".into()),
        }
    }
}

// --------------------------------------------------------------------------- what owners determine

/// A Contract v3:97-109 freshness input a currency-class label denotes (`"governing contract/policy (governance test
/// inputs)"` denotes `"governing contract/policy"`), or `None` for a class the contract's list does not name.
fn freshness_input_of(label: &str, vocab: &[String]) -> Option<String> {
    if vocab.iter().any(|v| v == label) {
        return Some(label.to_string());
    }
    let head = label.split(" (").next().unwrap_or(label);
    vocab.iter().find(|v| v.as_str() == head).cloned()
}

/// The Contract v3:97-109 inputs whose change makes an owner's evidence stale. For a tier owner these are exactly the
/// input classes the scheduler keys its result by (`catalogue::expand_deps` plus its extras), so they are what
/// actually invalidates it; a G0 guard reads the classes every check reads; a test, held-out suite or obligation is
/// evidence about the product build; a release is evidence about the release payload; a human-gate answer is bound
/// to the specification and decision it governs, under the gate policy.
pub fn owner_freshness(m: &ContractModel, id: &str) -> Vec<String> {
    use crate::scheduler::catalogue::{self, Extra};
    let vocab: Vec<String> = m
        .vocab
        .freshness_inputs
        .iter()
        .map(|l| l.text.clone())
        .collect();
    let mut labels: Vec<&str> = vec![];
    match owner_kind(id).map(|k| k.prefix) {
        Some("check") | Some("doctor") => {
            if let Some(def) = catalogue::get(&id[id.find(':').map(|i| i + 1).unwrap_or(0)..]) {
                for c in catalogue::expand_deps(def) {
                    labels.push(crate::verification::currency::contract_class_of(c));
                }
                for e in def.extras {
                    match e {
                        Extra::LiveIndex => labels.push("relevant index manifest"),
                        Extra::ContractSource => labels.push("governing contract/policy"),
                        _ => {}
                    }
                }
            }
        }
        Some("g0") => {
            for c in catalogue::IMPLICIT_DEPS {
                labels.push(crate::verification::currency::contract_class_of(c));
            }
        }
        Some("human-gate") => {
            labels.extend(["authoritative spec/decision", "governing contract/policy"])
        }
        Some("release") => labels.extend([
            "runtime/kernel implementation",
            "governing contract/policy",
            "schema",
            "migration",
            "tool/plugin",
        ]),
        Some(_) => labels.push("runtime/kernel implementation"),
        None => {}
    }
    let set: BTreeSet<String> = labels
        .iter()
        .filter_map(|l| freshness_input_of(l, &vocab))
        .collect();
    vocab.into_iter().filter(|v| set.contains(v)).collect()
}

fn owners_of(row: &Value, key: &str) -> Vec<Value> {
    row.get(key)
        .and_then(|v| v.as_array())
        .cloned()
        .unwrap_or_default()
}

fn owner_id(o: &Value) -> Option<&str> {
    o.get("id").and_then(|v| v.as_str())
}

fn str_array(v: Option<&Value>) -> Vec<String> {
    v.and_then(|x| x.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|s| s.as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default()
}

/// The fields a row's owners determine, as `gov contract compile` writes them: evidence classes (Contract v3:63),
/// health-scheduler tiers (:67), evidence-freshness triggers (:66), the adoption (:69) and periodic operational-audit
/// (:70) obligations and the remediation rule (:73).
pub fn derived_fields(m: &ContractModel, row: &Value) -> Map<String, Value> {
    let mut all = owners_of(row, "automated_checks");
    all.extend(owners_of(row, "independent_verification"));
    let classes: BTreeSet<String> = all
        .iter()
        .filter_map(|o| o.get("class").and_then(|c| c.as_str()).map(String::from))
        .collect();
    let mut tiers: BTreeSet<String> = BTreeSet::new();
    let mut fresh: BTreeSet<String> = BTreeSet::new();
    let mut g5: Vec<String> = vec![];
    let mut tiered_owner = false;
    for o in &all {
        let Some(id) = owner_id(o) else { continue };
        let t = str_array(o.get("tiers"));
        if owner_kind(id).map(|k| k.tiered).unwrap_or(false) {
            tiered_owner = true;
            if t.iter().any(|x| x == "G5") && !g5.contains(&id.to_string()) {
                g5.push(id.to_string());
            }
        }
        tiers.extend(t);
        fresh.extend(owner_freshness(m, id));
    }
    let vocab_order = |v: &[Line], set: &BTreeSet<String>| -> Vec<String> {
        v.iter()
            .filter(|l| set.contains(&l.text))
            .map(|l| l.text.clone())
            .collect()
    };
    let mut d = Map::new();
    d.insert(
        "evidence_class".into(),
        if all.is_empty() {
            json!(NOT_YET_MAPPED)
        } else {
            json!(vocab_order(&m.vocab.evidence_classes, &classes))
        },
    );
    d.insert(
        "health_scheduler_tiers".into(),
        json!(m
            .tier_ids()
            .into_iter()
            .filter(|t| tiers.contains(t))
            .collect::<Vec<_>>()),
    );
    d.insert(
        "freshness_triggers".into(),
        json!(vocab_order(&m.vocab.freshness_inputs, &fresh)),
    );
    d.insert(
        "adoption_obligation".into(),
        json!({"lifecycle_points": ADOPTION_POINTS, "owners": g5, "rule": if g5.is_empty() { ADOPTION_WITHOUT } else { ADOPTION_WITH }}),
    );
    d.insert(
        "operational_audit_obligation".into(),
        json!({"lifecycle_points": OPERATIONAL_POINTS, "owners": g5, "rule": if g5.is_empty() { OPERATIONAL_WITHOUT } else { OPERATIONAL_WITH }}),
    );
    d.insert(
        "remediation_rule".into(),
        json!(if tiered_owner {
            REMEDIATION_TIERED
        } else {
            REMEDIATION_UNTIERED
        }),
    );
    d
}

/// Fill what the owners determine, and the values the Phase-2 sources state for every capability where the map
/// states none (applicability, allowed status, N/A requirements). `severity` is left as the map states it: no
/// normative source states a per-capability severity, and the compiler may not invent one.
pub fn complete_governed(m: &ContractModel, map: &mut Value) {
    if let Some(rows) = map.get_mut("capabilities").and_then(|r| r.as_array_mut()) {
        for row in rows.iter_mut() {
            let derived = derived_fields(m, row);
            let Some(o) = row.as_object_mut() else {
                continue;
            };
            for (k, v) in derived {
                o.insert(k, v);
            }
            if o.get("independent_verification")
                .map(|v| v.is_null())
                .unwrap_or(true)
            {
                o.insert("independent_verification".into(), json!([]));
            }
            if o.get("applicability").map(|v| v.is_null()).unwrap_or(true) {
                o.insert("applicability".into(), json!(APPLICABILITY_RULE));
            }
            if o.get("allowed_status").map(|v| v.is_null()).unwrap_or(true) {
                o.insert("allowed_status".into(), json!(STATUS_VOCABULARY));
            }
            if o.get("na_requirements")
                .map(|v| v.is_null())
                .unwrap_or(true)
            {
                o.insert("na_requirements".into(), json!(NA_REQUIREMENTS));
            }
        }
    }
}

/// The governed part of an evidence map — every governed field of every row, each checklist item's owners and the
/// freshness-invalidation owners — whose digest the source lock binds, so a governed value changed without `gov
/// contract compile` is refused.
pub fn evidence_map_governed(map: &Value) -> Value {
    let governed = governed_fields();
    let rows: Vec<Value> = lines_of(map, "capabilities")
        .iter()
        .map(|r| {
            let mut o = Map::new();
            o.insert("capability".into(), r.get("capability").cloned().unwrap_or(Value::Null));
            for k in &governed {
                o.insert((*k).into(), r.get(*k).cloned().unwrap_or(Value::Null));
            }
            o.insert(
                "checklist".into(),
                Value::Array(
                    lines_of(r, "checklist")
                        .iter()
                        .map(|it| json!({"id": it.get("id"), "automated_checks": it.get("automated_checks")}))
                        .collect(),
                ),
            );
            Value::Object(o)
        })
        .collect();
    json!({"capabilities": rows, "freshness_invalidation": map.get("freshness_invalidation").cloned().unwrap_or(Value::Null)})
}

/// The result of checking a map's owners.
#[derive(Debug, Default)]
pub struct OwnerCheck {
    /// Owners that do not resolve (or, when compiling, could not be resolved in this tree).
    pub unresolved: Vec<Value>,
    /// Capabilities with no running owner.
    pub missing: Vec<Value>,
    /// Malformed or misplaced owners, and owner-determined fields that are not what the owners determine.
    pub invalid: Vec<Value>,
    pub summary: Value,
}

/// Check every capability's owners: each is well formed, resolves, and is placed where its independence says; every
/// capability has at least one running owner; the fields the owners determine are exactly what they determine; each
/// checklist item names only its capability's owners; every freshness trigger in use names an owner that proves the
/// invalidation. `strict` (compile) refuses what this tree cannot resolve instead of deferring it.
pub fn owner_differences(
    m: &ContractModel,
    map: &Value,
    reg: &OwnerRegistry,
    strict: bool,
) -> OwnerCheck {
    use crate::scheduler::catalogue;
    let mut r = OwnerCheck::default();
    let classes_vocab: BTreeSet<&str> = m
        .vocab
        .evidence_classes
        .iter()
        .map(|l| l.text.as_str())
        .collect();
    let mut by_kind: BTreeMap<String, usize> = BTreeMap::new();
    let mut by_class: BTreeMap<String, usize> = BTreeMap::new();
    let mut caps_by_tier: BTreeMap<String, usize> = BTreeMap::new();
    let mut caps_by_class: BTreeMap<String, usize> = BTreeMap::new();
    let mut deferred: Vec<Value> = vec![];
    let (mut owners_total, mut items_total, mut items_owned) = (0usize, 0usize, 0usize);
    let (mut tiered_caps, mut test_only, mut rows_n) = (0usize, vec![], 0usize);
    let mut triggers_in_use: BTreeSet<String> = BTreeSet::new();
    let mut resolved_ids: BTreeMap<String, Resolution> = BTreeMap::new();
    let mut resolve = |id: &str, record: Option<&str>, tests: &[String]| -> Resolution {
        let key = format!("{id}|{}|{}", record.unwrap_or(""), tests.join(","));
        resolved_ids
            .entry(key)
            .or_insert_with(|| reg.resolve_id(id, record, tests))
            .clone()
    };
    for row in lines_of(map, "capabilities") {
        rows_n += 1;
        let cap = row
            .get("capability")
            .and_then(|x| x.as_str())
            .unwrap_or("?")
            .to_string();
        let mut running = 0usize;
        let mut kinds_here: BTreeSet<&str> = BTreeSet::new();
        let mut ids_here: BTreeSet<String> = BTreeSet::new();
        for (field, independent) in [
            ("automated_checks", false),
            ("independent_verification", true),
        ] {
            let v = row.get(field);
            let list = match v {
                None | Some(Value::Null) if independent => vec![],
                Some(Value::Array(a)) => a.clone(),
                _ => {
                    r.invalid.push(difference(
                        "evidence_map",
                        &format!("capabilities[{cap}].{field}"),
                        "must be a list of owners",
                        None,
                        v,
                    ));
                    continue;
                }
            };
            for (i, o) in list.iter().enumerate() {
                let at = format!("capabilities[{cap}].{field}[{i}]");
                let Some(id) = owner_id(o) else {
                    r.invalid.push(difference(
                        "evidence_map",
                        &at,
                        "an owner is an object {id, class, …}",
                        None,
                        Some(o),
                    ));
                    continue;
                };
                let at = format!("capabilities[{cap}].{field}[{id}]");
                let Some(kind) = owner_kind(id) else {
                    r.unresolved.push(difference(
                        "evidence_map",
                        &at,
                        &format!(
                            "unknown owner kind (one of {})",
                            OWNER_KINDS
                                .iter()
                                .map(|k| k.prefix)
                                .collect::<Vec<_>>()
                                .join(", ")
                        ),
                        None,
                        Some(o),
                    ));
                    continue;
                };
                if !ids_here.insert(id.to_string()) {
                    r.invalid.push(difference(
                        "evidence_map",
                        &at,
                        "named twice for this capability",
                        None,
                        None,
                    ));
                }
                if kind.independent != independent {
                    r.invalid.push(difference("evidence_map", &at, if kind.independent { "an independent owner belongs in independent_verification, never among builder or product evidence (Contract v3 O3; frozen AC-12)" } else { "a product or builder owner belongs in automated_checks, never in independent_verification" }, None, None));
                }
                let allowed: BTreeSet<&str> =
                    ["id", "class", "tiers", "record", "tests", "exercises"]
                        .into_iter()
                        .collect();
                if let Some(obj) = o.as_object() {
                    for k in obj.keys() {
                        if !allowed.contains(k.as_str()) {
                            r.invalid.push(difference(
                                "evidence_map",
                                &format!("{at}.{k}"),
                                "not an owner field (id, class, tiers, record, tests, exercises)",
                                None,
                                None,
                            ));
                        }
                    }
                }
                let class = o.get("class").and_then(|c| c.as_str()).unwrap_or("");
                if !classes_vocab.contains(class) {
                    r.invalid.push(difference(
                        "evidence_map",
                        &format!("{at}.class"),
                        "not an evidence class of Contract v3:81-91",
                        Some(&json!(classes_vocab.iter().collect::<Vec<_>>())),
                        o.get("class"),
                    ));
                } else if !kind.classes.contains(&class) {
                    r.invalid.push(difference(
                        "evidence_map",
                        &format!("{at}.class"),
                        &format!(
                            "a `{}:` owner produces {}",
                            kind.prefix,
                            kind.classes.join(" or ")
                        ),
                        None,
                        o.get("class"),
                    ));
                }
                let record = o.get("record").and_then(|x| x.as_str());
                if record.is_some() != matches!(kind.prefix, "human-gate" | "release") {
                    r.invalid.push(difference(
                        "evidence_map",
                        &format!("{at}.record"),
                        "`record` is stated by exactly the human-gate and release owners",
                        None,
                        o.get("record"),
                    ));
                }
                let tests = str_array(o.get("tests"));
                if o.get("tests").is_some() && kind.prefix != "heldout" {
                    r.invalid.push(difference(
                        "evidence_map",
                        &format!("{at}.tests"),
                        "`tests` is stated only by a held-out owner",
                        None,
                        None,
                    ));
                }
                if let Some(e) = o.get("exercises") {
                    if !e.is_string() {
                        r.invalid.push(difference(
                            "evidence_map",
                            &format!("{at}.exercises"),
                            "a short statement of what the owner exercises",
                            None,
                            Some(e),
                        ));
                    }
                }
                let stated_tiers = str_array(o.get("tiers"));
                if o.get("tiers").is_some() != kind.tiered {
                    r.invalid.push(difference(
                        "evidence_map",
                        &format!("{at}.tiers"),
                        if kind.tiered {
                            "a tier owner states the tiers it runs at"
                        } else {
                            "only a tier owner (check, doctor, g0) states tiers"
                        },
                        None,
                        o.get("tiers"),
                    ));
                }
                owners_total += 1;
                *by_kind.entry(kind.prefix.to_string()).or_default() += 1;
                *by_class.entry(class.to_string()).or_default() += 1;
                match resolve(id, record, &tests) {
                    Resolution::Resolved(site) => {
                        if kind.tiered {
                            let declared = str_array(site.get("tiers"));
                            if declared != stated_tiers {
                                r.unresolved.push(difference("evidence_map", &format!("{at}.tiers"), "differs from the tiers the product declares for it (scheduler catalogue / G0)", Some(&json!(declared)), Some(&json!(stated_tiers))));
                            }
                        }
                        if kind.runs {
                            running += 1;
                        }
                        kinds_here.insert(kind.prefix);
                    }
                    Resolution::Deferred(why) if !strict => {
                        deferred.push(json!({"capability": cap, "owner": id, "reason": why}));
                        if kind.runs {
                            running += 1;
                        }
                        kinds_here.insert(kind.prefix);
                    }
                    Resolution::Deferred(why) => {
                        r.unresolved.push(difference("evidence_map", &at, &format!("cannot be resolved in this tree ({why}); compile the map where the owners' sources are"), None, None));
                    }
                    Resolution::Unresolved(why) => {
                        r.unresolved
                            .push(difference("evidence_map", &at, &why, None, None));
                    }
                }
            }
        }
        if running == 0 {
            r.missing.push(difference("evidence_map", &format!("capabilities[{cap}]"), "has no evidence owner that runs (a G0-G6 tier check, a test the harness runs, Human Decision Gate or release evidence, or an independent held-out suite); an obligation of a future verifier alone does not own it (frozen AC-10)", None, None));
        }
        // what the owners determine
        let derived = derived_fields(m, &row);
        for (k, v) in &derived {
            if row.get(k) != Some(v) {
                r.invalid.push(difference("evidence_map", &format!("capabilities[{cap}].{k}"), "is not what the capability's owners determine; `gov contract compile` derives it", Some(v), row.get(k)));
            }
        }
        let tiers_here = str_array(derived.get("health_scheduler_tiers"));
        for t in &tiers_here {
            *caps_by_tier.entry(t.clone()).or_default() += 1;
        }
        for c in str_array(derived.get("evidence_class")) {
            *caps_by_class.entry(c).or_default() += 1;
        }
        triggers_in_use.extend(str_array(derived.get("freshness_triggers")));
        if !tiers_here.is_empty() {
            tiered_caps += 1;
        } else if !kinds_here.is_empty()
            && kinds_here
                .iter()
                .all(|k| *k == "test" || *k == "obligation")
        {
            test_only.push(json!(cap));
        }
        // the values the sources state for every capability
        match row.get("allowed_status") {
            Some(Value::Array(a))
                if !a.is_empty()
                    && a.iter().all(|s| {
                        s.as_str()
                            .map(|x| STATUS_VOCABULARY.contains(&x))
                            .unwrap_or(false)
                    }) => {}
            other => r.invalid.push(difference(
                "evidence_map",
                &format!("capabilities[{cap}].allowed_status"),
                "one or more statuses of the frozen gate contract §4 vocabulary",
                Some(&json!(STATUS_VOCABULARY)),
                other,
            )),
        }
        for k in ["applicability", "na_requirements"] {
            if !row.get(k).map(|v| v.is_string()).unwrap_or(false) {
                r.invalid.push(difference(
                    "evidence_map",
                    &format!("capabilities[{cap}].{k}"),
                    "the rule the sources state (a string)",
                    None,
                    row.get(k),
                ));
            }
        }
        if !matches!(
            row.get("severity"),
            Some(Value::Null) | Some(Value::String(_))
        ) {
            r.invalid.push(difference(
                "evidence_map",
                &format!("capabilities[{cap}].severity"),
                "a stated severity, or null where no source states one",
                None,
                row.get("severity"),
            ));
        }
        // checklist items name only this capability's owners
        for it in lines_of(&row, "checklist") {
            items_total += 1;
            let iid = it.get("id").and_then(|x| x.as_str()).unwrap_or("?");
            let named = it
                .get("automated_checks")
                .and_then(|v| v.as_array())
                .cloned()
                .unwrap_or_default();
            if !named.is_empty() {
                items_owned += 1;
            }
            for n in named {
                if !n.as_str().map(|s| ids_here.contains(s)).unwrap_or(false) {
                    r.invalid.push(difference(
                        "evidence_map",
                        &format!("capabilities[{cap}].checklist[{iid}].automated_checks"),
                        "a checklist item names owners of its capability, by id",
                        Some(&json!(ids_here.iter().collect::<Vec<_>>())),
                        Some(&n),
                    ));
                }
            }
        }
    }
    // every freshness trigger in use names an owner that proves changing it invalidates prior green evidence (AC-10)
    let proofs = map.get("freshness_invalidation");
    let mut proven: BTreeSet<String> = BTreeSet::new();
    match proofs {
        None | Some(Value::Null) => {}
        Some(Value::Array(entries)) => {
            for (i, e) in entries.iter().enumerate() {
                let trig = e.get("trigger").and_then(|x| x.as_str()).unwrap_or("");
                let at = format!("freshness_invalidation[{trig}]");
                if !m.vocab.freshness_inputs.iter().any(|l| l.text == trig) {
                    r.invalid.push(difference(
                        "evidence_map",
                        &format!("freshness_invalidation[{i}].trigger"),
                        "not an evidence-freshness input of Contract v3:97-109",
                        None,
                        e.get("trigger"),
                    ));
                    continue;
                }
                let owners = str_array(e.get("owners"));
                if owners.is_empty() {
                    r.invalid.push(difference(
                        "evidence_map",
                        &at,
                        "names no owner that proves the invalidation",
                        None,
                        None,
                    ));
                }
                let mut ok = !owners.is_empty();
                for id in owners {
                    match resolve(&id, None, &[]) {
                        Resolution::Resolved(_) => {}
                        Resolution::Deferred(why) if !strict => deferred
                            .push(json!({"freshness_trigger": trig, "owner": id, "reason": why})),
                        Resolution::Deferred(why) | Resolution::Unresolved(why) => {
                            ok = false;
                            r.unresolved.push(difference(
                                "evidence_map",
                                &format!("{at}.owners[{id}]"),
                                &why,
                                None,
                                None,
                            ));
                        }
                    }
                }
                for k in e
                    .as_object()
                    .map(|o| o.keys().cloned().collect::<Vec<_>>())
                    .unwrap_or_default()
                {
                    if !["trigger", "owners", "proves"].contains(&k.as_str()) {
                        r.invalid.push(difference("evidence_map", &format!("{at}.{k}"), "not a field of a freshness-invalidation entry (trigger, owners, proves)", None, None));
                    }
                }
                if ok {
                    proven.insert(trig.to_string());
                }
            }
        }
        Some(other) => r.invalid.push(difference(
            "evidence_map",
            "freshness_invalidation",
            "a list of {trigger, owners, proves}",
            None,
            Some(other),
        )),
    }
    for t in &triggers_in_use {
        if !proven.contains(t) {
            r.invalid.push(difference("evidence_map", &format!("freshness_invalidation[{t}]"), "a freshness trigger in use names no owner proving that changing it invalidates prior green evidence (frozen AC-10, second sentence)", None, None));
        }
    }
    let tiers_total = m.tier_ids();
    r.summary = json!({
        "capabilities": rows_n,
        "owners": owners_total,
        "owners_by_kind": by_kind,
        "owners_by_class": by_class,
        "capabilities_by_evidence_class": caps_by_class,
        "capabilities_by_tier": tiers_total.iter().map(|t| (t.clone(), json!(caps_by_tier.get(t).copied().unwrap_or(0)))).collect::<Map<String, Value>>(),
        "capabilities_with_a_tier_owner": tiered_caps,
        "capabilities_owned_only_by_tests": test_only,
        "checklist_items": items_total,
        "checklist_items_naming_an_owner": items_owned,
        "freshness_triggers_in_use": triggers_in_use,
        "deferred": deferred,
        "not_in_this_tree": reg.absent_sources(),
        "catalogue_checks": catalogue::CHECKS.len(),
    });
    r
}

fn owner_error(chk: &OwnerCheck) -> Option<GovError> {
    let (code, what, diffs) = if !chk.unresolved.is_empty() {
        ("CONTRACT_EVIDENCE_OWNER_UNRESOLVED", "an evidence owner does not resolve to a check, test, suite, command or criterion that exists and runs", chk.unresolved.clone())
    } else if !chk.missing.is_empty() {
        ("CONTRACT_EVIDENCE_OWNER_MISSING", "a capability has no evidence owner that runs (frozen AC-10: no required capability has zero evidence owners)", chk.missing.clone())
    } else if !chk.invalid.is_empty() {
        ("CONTRACT_EVIDENCE_OWNER_INVALID", "an evidence owner is malformed or misplaced, or a field its owners determine is not what they determine", chk.invalid.clone())
    } else {
        return None;
    };
    let mut all = diffs;
    for (k, v) in [
        ("unresolved", &chk.unresolved),
        ("missing", &chk.missing),
        ("invalid", &chk.invalid),
    ] {
        if !v.is_empty() && !all.iter().any(|d| v.contains(d)) {
            all.push(json!({"view": "evidence_map", "at": k, "problem": format!("{} further {k} difference(s)", v.len())}));
        }
    }
    let mut e = diverged(
        code,
        &format!("{EVIDENCE_MAP}: {what}"),
        all,
        "name, for every capability, owners that exist and run and exercise it (never an invented one); a capability nothing exercises stays unmapped and fails here; then `gov contract compile`",
    );
    if let Some(o) = e.details.as_object_mut() {
        o.insert("unresolved".into(), json!(chk.unresolved.len()));
        o.insert("missing".into(), json!(chk.missing.len()));
        o.insert("invalid".into(), json!(chk.invalid.len()));
    }
    Some(e)
}

// ------------------------------------------------------------------------------------------ suite-to-contract matrix

/// Outputs of runs of the owners, supplied to the matrix as their last-run evidence. The matrix runs no owner and
/// infers no result: an owner no supplied output covers is reported as not run in the supplied evidence.
#[derive(Debug, Clone, Default)]
pub struct RunEvidence {
    /// `cargo test --lib` outputs.
    pub lib: Vec<PathBuf>,
    /// `cargo test --test certification` outputs.
    pub certification: Vec<PathBuf>,
    /// Held-out re-run outputs: per test binary a block headed `===== <suite label> :: <binary> =====`.
    pub heldout: Vec<PathBuf>,
    /// `gov --json health run …` and `gov --json doctor` outputs.
    pub health: Vec<PathBuf>,
}

fn cargo_result_regex() -> &'static Regex {
    static RX: OnceLock<Regex> = OnceLock::new();
    RX.get_or_init(|| {
        Regex::new(r"(?m)^test (\S+) \.\.\. (ok|FAILED|ignored)").expect("cargo result regex")
    })
}

fn heldout_block_regex() -> &'static Regex {
    static RX: OnceLock<Regex> = OnceLock::new();
    RX.get_or_init(|| Regex::new(r"(?m)^===== (.+?) :: (.+?) =====$").expect("heldout block regex"))
}

/// The suite label a held-out suite's crate manifest gives (`srr-heldout-ar0027` → `AR-0027`).
fn heldout_label(dir: &Path) -> Option<String> {
    let t = std::fs::read_to_string(dir.join("Cargo.toml.txt")).ok()?;
    let name = t
        .lines()
        .find(|l| l.trim_start().starts_with("name"))?
        .split('"')
        .nth(1)?
        .to_string();
    let tail = name.rsplit('-').next()?;
    let digits: String = tail.chars().filter(|c| c.is_ascii_digit()).collect();
    let letters: String = tail
        .chars()
        .take_while(|c| c.is_ascii_alphabetic())
        .collect();
    if digits.is_empty() || letters.is_empty() {
        return None;
    }
    Some(format!("{}-{digits}", letters.to_uppercase()))
}

struct Supplied {
    files: Vec<Value>,
    tests: BTreeMap<(String, String), (String, String)>,
    heldout: BTreeMap<String, Value>,
    heldout_tests: BTreeMap<(String, String), (String, String)>,
    checks: BTreeMap<String, (String, String)>,
}

fn supplied_file(repo_root: &Path, kind: &str, p: &Path) -> Result<(String, String)> {
    let text = read_text(p).map_err(|e| {
        GovError::new(
            "CONTRACT_MATRIX_EVIDENCE_UNREADABLE",
            format!("run evidence {} cannot be read: {}", p.display(), e.message),
        )
    })?;
    let shown = p
        .canonicalize()
        .ok()
        .and_then(|c| {
            repo_root.canonicalize().ok().and_then(|r| {
                c.strip_prefix(r)
                    .ok()
                    .map(|x| x.to_string_lossy().to_string())
            })
        })
        .unwrap_or_else(|| p.display().to_string());
    let _ = kind;
    Ok((shown, text))
}

fn read_supplied(repo_root: &Path, ev: &RunEvidence) -> Result<Supplied> {
    let mut s = Supplied {
        files: vec![],
        tests: BTreeMap::new(),
        heldout: BTreeMap::new(),
        heldout_tests: BTreeMap::new(),
        checks: BTreeMap::new(),
    };
    for (harness, list) in [("lib", &ev.lib), ("certification", &ev.certification)] {
        for p in list {
            let (shown, text) = supplied_file(repo_root, harness, p)?;
            let mut n = 0;
            for c in cargo_result_regex().captures_iter(&text) {
                n += 1;
                let status = match &c[2] {
                    "ok" => "PASSED",
                    "FAILED" => "FAILED",
                    _ => "IGNORED",
                };
                s.tests.insert(
                    (harness.to_string(), c[1].to_string()),
                    (status.to_string(), shown.clone()),
                );
            }
            s.files.push(json!({"kind": format!("cargo test ({harness})"), "path": shown, "sha256": sha256_text(&text), "results": n}));
        }
    }
    // held-out suites: map each run block's suite label to the suite directory whose manifest names it
    let mut labels: BTreeMap<String, String> = BTreeMap::new();
    if let Ok(rd) = std::fs::read_dir(repo_root.join(HELDOUT_ROOT)) {
        for e in rd.flatten() {
            let dir = e.path().join("evidence").join("heldout-tests");
            if let Some(l) = heldout_label(&dir) {
                labels.insert(l, crate::util::rel_posix(&dir, repo_root));
            }
        }
    }
    for p in &ev.heldout {
        let (shown, text) = supplied_file(repo_root, "heldout", p)?;
        let heads: Vec<(usize, usize, String, String)> = heldout_block_regex()
            .captures_iter(&text)
            .map(|c| {
                let m = c.get(0).expect("match");
                (m.start(), m.end(), c[1].to_string(), c[2].to_string())
            })
            .collect();
        for (i, (_, end, label, binary)) in heads.iter().enumerate() {
            let stop = heads.get(i + 1).map(|h| h.0).unwrap_or(text.len());
            let body = &text[*end..stop];
            let Some(dir) = labels.get(label) else {
                continue;
            };
            let entry = s.heldout.entry(dir.clone()).or_insert_with(|| {
                json!({"label": label, "passed": 0, "failed": 0, "failing": [], "not_compiling": [], "evidence": shown})
            });
            let mut ran = 0;
            for c in cargo_result_regex().captures_iter(body) {
                ran += 1;
                let status = if &c[2] == "ok" {
                    "PASSED"
                } else if &c[2] == "FAILED" {
                    "FAILED"
                } else {
                    "IGNORED"
                };
                let key = if status == "PASSED" {
                    "passed"
                } else {
                    "failed"
                };
                if status != "IGNORED" {
                    entry[key] = json!(entry[key].as_u64().unwrap_or(0) + 1);
                }
                let name = format!("{binary}::{}", &c[1]);
                if status == "FAILED" {
                    entry["failing"]
                        .as_array_mut()
                        .expect("array")
                        .push(json!(name));
                }
                s.heldout_tests
                    .insert((dir.clone(), name), (status.to_string(), shown.clone()));
            }
            if ran == 0 && (body.contains("error[E") || body.contains("could not compile")) {
                entry["not_compiling"]
                    .as_array_mut()
                    .expect("array")
                    .push(json!(binary));
            }
        }
        s.files.push(json!({"kind": "held-out re-run", "path": shown, "sha256": sha256_text(&text), "blocks": heads.len()}));
    }
    for p in &ev.health {
        let (shown, text) = supplied_file(repo_root, "health", p)?;
        let v: Value = serde_json::from_str(&text).map_err(|e| {
            GovError::new(
                "CONTRACT_MATRIX_EVIDENCE_UNREADABLE",
                format!("health evidence {} is not JSON: {e}", p.display()),
            )
        })?;
        let r = v.get("result").unwrap_or(&v);
        let tier = r
            .get("tier")
            .and_then(|t| t.as_str())
            .unwrap_or("")
            .to_string();
        let mut n = 0;
        if let Some(f) = r.get("families").and_then(|x| x.as_object()) {
            for (id, res) in f {
                n += 1;
                let ok = res.get("ok").and_then(|x| x.as_bool()).unwrap_or(false);
                let how = res.get("status").and_then(|x| x.as_str()).unwrap_or("ran");
                s.checks.insert(
                    format!("check:{id}"),
                    (
                        format!(
                            "RAN{}: {} ({how})",
                            if tier.is_empty() {
                                String::new()
                            } else {
                                format!(" at {tier}")
                            },
                            if ok { "ok" } else { "findings" }
                        ),
                        shown.clone(),
                    ),
                );
            }
        }
        if let Some(c) = r.get("checks").and_then(|x| x.as_array()) {
            for chk in c {
                let Some(id) = chk.get("id").and_then(|x| x.as_str()) else {
                    continue;
                };
                n += 1;
                let ok = chk.get("ok").and_then(|x| x.as_bool()).unwrap_or(false);
                s.checks.insert(
                    format!("doctor:{id}"),
                    (
                        format!("RAN (gov doctor): {}", if ok { "ok" } else { "findings" }),
                        shown.clone(),
                    ),
                );
            }
        }
        s.files.push(json!({"kind": "gov health/doctor run", "path": shown, "sha256": sha256_text(&text), "results": n, "tier": tier}));
    }
    Ok(s)
}

fn last_run(s: &Supplied, o: &Value) -> Value {
    let id = owner_id(o).unwrap_or("");
    let not_run = json!({"status": "NOT_IN_SUPPLIED_EVIDENCE"});
    match owner_kind(id).map(|k| k.prefix) {
        Some("test") => {
            let rest = &id[5..];
            let Some((h, path)) = rest.split_once(':') else {
                return not_run;
            };
            match s.tests.get(&(h.to_string(), path.to_string())) {
                Some((st, file)) => json!({"status": st, "evidence": file}),
                None => not_run,
            }
        }
        Some("check") | Some("doctor") => match s.checks.get(id) {
            Some((st, file)) => json!({"status": st, "evidence": file}),
            None => not_run,
        },
        Some("heldout") => {
            let dir = id[8..].trim_end_matches('/');
            match s.heldout.get(dir) {
                None => not_run,
                Some(agg) => {
                    let named: Vec<Value> = str_array(o.get("tests"))
                        .iter()
                        .map(|t| {
                            let st = s
                                .heldout_tests
                                .get(&(dir.to_string(), t.clone()))
                                .map(|x| x.0.clone())
                                .unwrap_or_else(|| "NOT_IN_SUPPLIED_EVIDENCE".into());
                            json!({"test": t, "status": st})
                        })
                        .collect();
                    json!({"status": format!("RAN: {} passed, {} failed", agg["passed"], agg["failed"]), "failing": agg["failing"], "not_compiling": agg["not_compiling"], "named_tests": named, "evidence": agg["evidence"]})
                }
            }
        }
        Some("obligation") => {
            json!({"status": "OBLIGATION: discharged by the independent verification of the candidate, not by builder evidence"})
        }
        _ => not_run,
    }
}

/// The suite-to-contract matrix (frozen AC-10): every capability → its owners → their tiers → their last-run
/// evidence, generated from the evidence map after it verifies. Returns the machine-readable matrix and its Markdown
/// rendering.
pub fn suite_to_contract(repo_root: &Path, ev: &RunEvidence) -> Result<(Value, String)> {
    let verified = verify(repo_root)?;
    let dv = derive(repo_root, "")?;
    let map: Value = crate::util::read_yaml(&repo_root.join(EVIDENCE_MAP))?;
    let reg = OwnerRegistry::load(repo_root);
    let chk = owner_differences(&dv.model, &map, &reg, false);
    let supplied = read_supplied(repo_root, ev)?;
    let mut rows = vec![];
    let mut status_counts: BTreeMap<String, usize> = BTreeMap::new();
    for row in lines_of(&map, "capabilities") {
        let cap = row["capability"].as_str().unwrap_or("?").to_string();
        let mut owners = vec![];
        for (field, independent) in [
            ("automated_checks", false),
            ("independent_verification", true),
        ] {
            for o in owners_of(&row, field) {
                let id = owner_id(&o).unwrap_or("").to_string();
                let lr = last_run(&supplied, &o);
                let head = lr["status"]
                    .as_str()
                    .unwrap_or("")
                    .split([':', ' '])
                    .next()
                    .unwrap_or("")
                    .to_string();
                *status_counts.entry(head).or_default() += 1;
                let resolved = match reg.resolve_id(
                    &id,
                    o.get("record").and_then(|x| x.as_str()),
                    &str_array(o.get("tests")),
                ) {
                    Resolution::Resolved(v) => v,
                    Resolution::Deferred(w) => json!({"deferred": w}),
                    Resolution::Unresolved(w) => json!({"unresolved": w}),
                };
                owners.push(json!({
                    "id": id,
                    "kind": owner_kind(&id).map(|k| k.prefix),
                    "independent": independent,
                    "class": o.get("class"),
                    "tiers": o.get("tiers").cloned().unwrap_or(json!([])),
                    "exercises": o.get("exercises"),
                    "resolved": resolved,
                    "last_run": lr,
                }));
            }
        }
        let items = lines_of(&row, "checklist");
        rows.push(json!({
            "capability": cap,
            "title": row["title"],
            "gate": row["gate"],
            "evidence_class": row["evidence_class"],
            "health_scheduler_tiers": row["health_scheduler_tiers"],
            "freshness_triggers": row["freshness_triggers"],
            "checklist_items": items.len(),
            "checklist_items_naming_an_owner": items.iter().filter(|i| i["automated_checks"].as_array().map(|a| !a.is_empty()).unwrap_or(false)).count(),
            "owners": owners,
        }));
    }
    let fresh: Vec<Value> = lines_of(&map, "freshness_invalidation")
        .iter()
        .map(|e| {
            let owners: Vec<Value> = str_array(e.get("owners"))
                .iter()
                .map(|id| json!({"id": id, "last_run": last_run(&supplied, &json!({"id": id}))}))
                .collect();
            json!({"trigger": e["trigger"], "proves": e.get("proves"), "owners": owners})
        })
        .collect();
    let matrix = json!({
        "schema": "governance-os.suite-to-contract-matrix",
        "schema_version": 1,
        "generated_by": "gov contract matrix (runtime/src/contracts.rs::suite_to_contract), from the evidence map after `gov contract verify`",
        "contract": {
            "owner_source_sha256": OWNER_SOURCE_SHA256,
            "evidence_map": EVIDENCE_MAP,
            "evidence_map_governed_sha256": crate::util::hash_value(&evidence_map_governed(&map)),
            "verify_verdict": verified["verdict"],
        },
        "run_evidence_supplied": supplied.files,
        "summary": {
            "owners": chk.summary,
            "owner_last_run_status_counts": status_counts,
        },
        "freshness_invalidation": fresh,
        "capabilities": rows,
    });
    let md = render_matrix(&matrix);
    Ok((matrix, md))
}

fn md_cell(v: &Value) -> String {
    let s = match v {
        Value::Null => "—".to_string(),
        Value::String(s) => s.clone(),
        Value::Array(a) if a.is_empty() => "—".to_string(),
        Value::Array(a) => a
            .iter()
            .map(|x| {
                x.as_str()
                    .map(String::from)
                    .unwrap_or_else(|| x.to_string())
            })
            .collect::<Vec<_>>()
            .join(", "),
        o => o.to_string(),
    };
    s.replace('|', "\\|").replace('\n', " ")
}

fn render_matrix(mx: &Value) -> String {
    let mut out = String::new();
    let s = &mx["summary"]["owners"];
    out.push_str("# Suite-to-contract matrix (frozen gate contract AC-10)\n\n");
    out.push_str("Generated by `gov contract matrix` from `tests/governance/capability-evidence-map.yaml` after `gov contract verify`\n");
    out.push_str("returned `CONTRACT_SOURCE_BOUND`. Every owner below was resolved by the product (scheduler catalogue, G0 command\n");
    out.push_str("classification, the test harnesses' module trees, the held-out suites, the frozen gate contract). Last-run evidence\n");
    out.push_str("is read from the run outputs supplied to the command, never inferred: an owner no supplied output covers is\n");
    out.push_str("`NOT_IN_SUPPLIED_EVIDENCE`. Builder evidence is regression evidence (Contract v3 O3); independent owners are\n");
    out.push_str("listed separately and are never builder evidence.\n\n");
    out.push_str(&format!(
        "Contract source SHA-256 `{}` · evidence map governed digest `{}`.\n\n",
        md_cell(&mx["contract"]["owner_source_sha256"]),
        md_cell(&mx["contract"]["evidence_map_governed_sha256"])
    ));
    out.push_str("## Run evidence supplied\n\n| Kind | File | SHA-256 |\n|---|---|---|\n");
    for f in mx["run_evidence_supplied"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        out.push_str(&format!(
            "| {} | `{}` | `{}` |\n",
            md_cell(&f["kind"]),
            md_cell(&f["path"]),
            md_cell(&f["sha256"])
        ));
    }
    out.push_str("\n## Summary\n\n");
    out.push_str(&format!(
        "- capabilities: {} · owners: {} · capabilities with a G-tier owner: {} · capabilities owned only by tests (no G-tier, held-out, human-gate or release owner): {}\n",
        s["capabilities"], s["owners"], s["capabilities_with_a_tier_owner"],
        s["capabilities_owned_only_by_tests"].as_array().map(|a| if a.is_empty() { "none".to_string() } else { a.iter().filter_map(|x| x.as_str()).collect::<Vec<_>>().join(", ") }).unwrap_or_default()
    ));
    out.push_str(&format!(
        "- checklist items naming an owner: {} of {}\n",
        s["checklist_items_naming_an_owner"], s["checklist_items"]
    ));
    out.push_str(&format!(
        "- deferred owners (sources not in this tree): {}\n\n",
        s["deferred"].as_array().map(|a| a.len()).unwrap_or(0)
    ));
    out.push_str("| Owners by kind | Count |\n|---|---|\n");
    for (k, v) in s["owners_by_kind"].as_object().cloned().unwrap_or_default() {
        out.push_str(&format!("| `{k}` | {v} |\n"));
    }
    out.push_str(
        "\n| Evidence class (Contract v3:83-91) | Owners | Capabilities |\n|---|---|---|\n",
    );
    for (k, v) in s["owners_by_class"]
        .as_object()
        .cloned()
        .unwrap_or_default()
    {
        out.push_str(&format!(
            "| {k} | {v} | {} |\n",
            s["capabilities_by_evidence_class"][&k]
        ));
    }
    out.push_str("\n| Tier (O5) | Capabilities with an owner at the tier |\n|---|---|\n");
    for (k, v) in s["capabilities_by_tier"]
        .as_object()
        .cloned()
        .unwrap_or_default()
    {
        out.push_str(&format!("| {k} | {v} |\n"));
    }
    out.push_str("\n| Owner last-run status | Owners |\n|---|---|\n");
    for (k, v) in mx["summary"]["owner_last_run_status_counts"]
        .as_object()
        .cloned()
        .unwrap_or_default()
    {
        out.push_str(&format!(
            "| {} | {v} |\n",
            if k.is_empty() { "—".into() } else { k }
        ));
    }
    out.push_str("\n## Freshness triggers → owners proving invalidation (AC-10, second sentence)\n\n| Trigger (Contract v3:97-109) | Owner | Last run | What it proves |\n|---|---|---|---|\n");
    for e in mx["freshness_invalidation"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        for o in e["owners"].as_array().cloned().unwrap_or_default() {
            out.push_str(&format!(
                "| {} | `{}` | {} | {} |\n",
                md_cell(&e["trigger"]),
                md_cell(&o["id"]),
                md_cell(&o["last_run"]["status"]),
                md_cell(&e["proves"])
            ));
        }
    }
    out.push_str("\n## Capabilities\n\n");
    let mut gate = String::new();
    for c in mx["capabilities"].as_array().cloned().unwrap_or_default() {
        let g = c["gate"].as_str().unwrap_or("").to_string();
        if g != gate {
            out.push_str(&format!("### Gate {g}\n\n"));
            gate = g;
        }
        out.push_str(&format!(
            "#### {} — {}\n\nEvidence class: {} · tiers: {} · freshness triggers: {} · checklist items naming an owner: {}/{}\n\n",
            md_cell(&c["capability"]),
            md_cell(&c["title"]),
            md_cell(&c["evidence_class"]),
            md_cell(&c["health_scheduler_tiers"]),
            md_cell(&c["freshness_triggers"]),
            c["checklist_items_naming_an_owner"],
            c["checklist_items"]
        ));
        out.push_str("| Owner | Class | Tier(s) | Independent | Last-run evidence | Exercises |\n|---|---|---|---|---|---|\n");
        for o in c["owners"].as_array().cloned().unwrap_or_default() {
            let lr = &o["last_run"];
            let ev = match lr.get("evidence") {
                Some(Value::String(e)) => format!("{} (`{}`)", md_cell(&lr["status"]), e),
                _ => md_cell(&lr["status"]),
            };
            out.push_str(&format!(
                "| `{}` | {} | {} | {} | {} | {} |\n",
                md_cell(&o["id"]),
                md_cell(&o["class"]),
                md_cell(&o["tiers"]),
                if o["independent"].as_bool().unwrap_or(false) {
                    "yes"
                } else {
                    "no"
                },
                ev,
                md_cell(&o["exercises"])
            ));
        }
        out.push('\n');
    }
    out
}

/// Write the matrix to `out` as `suite-to-contract.json` and `suite-to-contract.md`.
pub fn write_suite_to_contract(repo_root: &Path, ev: &RunEvidence, out: &Path) -> Result<Value> {
    let (mx, md) = suite_to_contract(repo_root, ev)?;
    std::fs::create_dir_all(out).map_err(|e| GovError::io("creating the matrix directory", e))?;
    crate::util::write_json(&out.join("suite-to-contract.json"), &mx)?;
    crate::util::write_text(&out.join("suite-to-contract.md"), &md)?;
    Ok(json!({
        "written": [out.join("suite-to-contract.json").display().to_string(), out.join("suite-to-contract.md").display().to_string()],
        "capabilities": mx["capabilities"].as_array().map(|a| a.len()),
        "summary": mx["summary"],
        "run_evidence_supplied": mx["run_evidence_supplied"],
    }))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    fn repo() -> PathBuf {
        Path::new(env!("CARGO_MANIFEST_DIR"))
            .parent()
            .expect("workspace root")
            .to_path_buf()
    }

    fn model() -> ContractModel {
        embedded_model().expect("the embedded approved source parses")
    }

    /// A disposable copy of every file of the binding chain, with the owners' sources (the test harnesses' crates,
    /// the held-out suites and the frozen gate contract) linked in read-only from this checkout, so `gov contract
    /// compile` can resolve every owner in it.
    fn fixture(tag: &str) -> PathBuf {
        let dir = bare_fixture(tag);
        std::fs::create_dir_all(dir.join("tests")).unwrap();
        for rel in ["runtime", "tests/certification", "release"] {
            std::os::unix::fs::symlink(repo().join(rel), dir.join(rel)).unwrap();
        }
        dir
    }

    /// A disposable copy of the binding chain only: the shape of a release-tooling tree, which carries no test
    /// sources, no held-out suites and no gate contract.
    fn bare_fixture(tag: &str) -> PathBuf {
        let dir =
            std::env::temp_dir().join(format!("gov-contract-{tag}-{}", crate::util::short_uuid()));
        for rel in [
            OWNER_SOURCE,
            CANONICAL_IMPORT,
            COMPILED,
            SOURCE_LOCK,
            SCHEMA,
            EVIDENCE_MAP,
            GENERATED_VIEW,
        ] {
            let dst = dir.join(rel);
            std::fs::create_dir_all(dst.parent().unwrap()).unwrap();
            std::fs::copy(repo().join(rel), &dst).unwrap();
        }
        dir
    }

    fn edit_yaml(dir: &Path, rel: &str, f: impl FnOnce(&mut Value)) {
        let p = dir.join(rel);
        let mut v = crate::util::read_yaml(&p).unwrap();
        f(&mut v);
        crate::util::write_yaml(&p, &v).unwrap();
    }

    fn cap_index(v: &Value, id: &str, key: &str) -> usize {
        v["capabilities"]
            .as_array()
            .unwrap()
            .iter()
            .position(|c| c[key] == id)
            .unwrap()
    }

    fn err_code(dir: &Path) -> (String, String) {
        let e = verify(dir).expect_err("verify must fail");
        (e.code.clone(), crate::util::canonical_json(&e.details))
    }

    #[test]
    fn the_owner_universe_is_read_in_full() {
        let m = model();
        assert_eq!(
            m.capabilities.len(),
            101,
            "100 numbered capabilities plus Gate U"
        );
        assert_eq!(m.gates.len(), 23);
        assert_eq!(
            m.item_count(),
            713,
            "every checklist item of the capability sections"
        );
        assert_eq!(m.challenges.len(), 8);
        let u = m.capability("U").expect("Gate U is a capability section");
        assert!(u.gate_capability && u.heading.is_none());
        assert_eq!(u.items.len(), 28);
        assert_eq!(u.title, "Framework Health SLOs");
        assert_eq!(u.requirement_class, "ORIGINAL");
        let closing_items: usize = m.closing.iter().map(|s| s.items.len()).sum();
        assert_eq!(
            closing_items, 9,
            "the pre-advanced-qualification acceptance items"
        );
        assert_eq!(m.fields.len(), 17);
        assert_eq!(m.vocab.evidence_classes.len(), 9);
        assert_eq!(m.vocab.freshness_inputs.len(), 11);
        assert_eq!(m.vocab.lifecycle_points.len(), 11);
        assert_eq!(m.tier_ids(), vec!["G0", "G1", "G2", "G3", "G4", "G5", "G6"]);
    }

    #[test]
    fn labels_are_carried_exactly_as_the_source_states_them() {
        let m = model();
        let c = |id: &str| m.capability(id).unwrap().clone();
        assert_eq!(
            c("A2").label.as_deref(),
            Some("POST-VERIFICATION HARDENING")
        );
        assert_eq!(c("A2").requirement_class, "POST_VERIFICATION_HARDENING");
        assert_eq!(c("F4").requirement_class, "POST_VERIFICATION_HARDENING");
        assert_eq!(c("O5").label.as_deref(), Some("NEW EXECUTION REFINEMENT"));
        assert_eq!(c("O5").requirement_class, "EXECUTION_REFINEMENT");
        assert_eq!(
            c("O5").title,
            "Governance Health Scheduler",
            "no source markup in the title"
        );
        for v in ["V1", "V2", "V3", "V4"] {
            assert_eq!(c(v).label.as_deref(), Some("NEW TESTING REFINEMENT"));
            assert_eq!(c(v).label_line, Some(1012));
            assert_eq!(
                c(v).requirement_class,
                "NEW TESTING REFINEMENT",
                "carried verbatim, not mapped"
            );
            assert!(!c(v).requirement_class_enumerated);
        }
        let labelled: Vec<String> = m
            .capabilities
            .iter()
            .filter(|c| c.label.is_some())
            .map(|c| c.id.clone())
            .collect();
        assert_eq!(labelled, vec!["A2", "F4", "O5", "V1", "V2", "V3", "V4"]);
    }

    #[test]
    fn qualifiers_invariant_and_challenges_are_carried_verbatim() {
        let m = model();
        let e3 = m.capability("E3").unwrap();
        let q = e3.statements.iter().find(|s| s.line == 385).unwrap();
        assert_eq!(
            (q.kind, q.text.as_str()),
            ("qualifier", "persist beyond conversation lifetime.")
        );
        let h2 = m.capability("H2").unwrap();
        let q = h2.statements.iter().find(|s| s.line == 515).unwrap();
        assert_eq!(
            (q.kind, q.text.as_str()),
            ("qualifier", "and silent N/A is invalid.")
        );
        assert_eq!(h2.items.len(), 31);
        assert_eq!(h2.items[25].number, Some(26));
        let w10 = m.capability("W10").unwrap();
        let hi = w10
            .statements
            .iter()
            .find(|s| s.kind == "hard_invariant")
            .unwrap();
        assert!(hi.text.starts_with("> Mandatory task inputs are resolved through authoritative structured dependency/state mechanisms before supplementary retrieval."));
        let ids: Vec<String> = m.challenge_ids();
        assert_eq!(
            ids,
            vec!["AQC-A1", "AQC-A2", "AQC-A3", "AQC-B2", "AQC-D6", "AQC-H4", "AQC-J2", "AQC-W12"]
        );
        let g = m.gates.iter().find(|g| g.id == "V").unwrap();
        assert_eq!(g.statements.len(), 1);
        assert!(g.statements[0]
            .text
            .contains("verifier-owned hidden oracle"));
    }

    #[test]
    fn the_compiler_accounts_for_every_line_of_the_approved_source() {
        let m = model();
        let compiled = compile_model(&m);
        let d = source_accounting("compiled", &compiled, EMBEDDED_SOURCE);
        assert!(d.is_empty(), "{d:#?}");
        let nonblank = EMBEDDED_SOURCE
            .lines()
            .filter(|l| !is_structural_blank(l))
            .count();
        assert_eq!(m.carried_line_count(), nonblank);
    }

    #[test]
    fn the_line_accounting_is_independent_of_the_compiler() {
        // A compiled form that silently drops a checklist item, a qualifier or Gate U is caught by the accounting,
        // not by comparing the compiler with itself.
        let m = model();
        let mut c = compile_model(&m);
        let a1 = cap_index(&c, "A1", "id");
        c["capabilities"][a1]["checklist"]
            .as_array_mut()
            .unwrap()
            .remove(2);
        let d = source_accounting("compiled", &c, EMBEDDED_SOURCE);
        assert!(d.iter().any(|x| x["at"] == "source line 135"), "{d:#?}");
        let mut c = compile_model(&m);
        let u = cap_index(&c, "U", "id");
        c["capabilities"].as_array_mut().unwrap().remove(u);
        let d = source_accounting("compiled", &c, EMBEDDED_SOURCE);
        assert!(d.iter().any(|x| x["at"] == "capabilities[U]"), "{d:#?}");
        let mut c = compile_model(&m);
        let o5 = cap_index(&c, "O5", "id");
        c["capabilities"][o5]["requirement_class_label"] = json!("EXECUTION REFINEMENT");
        let d = source_accounting("compiled", &c, EMBEDDED_SOURCE);
        assert!(
            d.iter()
                .any(|x| x["at"] == "capabilities[O5].requirement_class_label"),
            "{d:#?}"
        );
        // an item moved to another capability is misattributed even though every line is still carried once
        let mut c = compile_model(&m);
        let a1 = cap_index(&c, "A1", "id");
        let it = c["capabilities"][a1]["checklist"]
            .as_array_mut()
            .unwrap()
            .remove(0);
        let a2 = cap_index(&c, "A2", "id");
        c["capabilities"][a2]["checklist"]
            .as_array_mut()
            .unwrap()
            .push(it);
        let d = source_accounting("compiled", &c, EMBEDDED_SOURCE);
        assert!(
            d.iter().any(|x| x["at"] == "capabilities[A2].checklist"),
            "{d:#?}"
        );
    }

    #[test]
    fn a_single_changed_byte_in_the_source_changes_the_binding() {
        let a = compile(EMBEDDED_SOURCE).unwrap();
        let b =
            compile(&EMBEDDED_SOURCE.replacen("Canonical authority", "Canonical  authority", 1))
                .unwrap();
        assert_ne!(
            a["compiled_from"]["source_sha256"],
            b["compiled_from"]["source_sha256"]
        );
        assert_eq!(
            crate::util::hash_value(&a),
            crate::util::hash_value(&compile(EMBEDDED_SOURCE).unwrap()),
            "compilation is deterministic"
        );
    }

    #[test]
    fn the_committed_binding_chain_verifies() {
        let r = verify(&repo()).expect("the committed derived views verify");
        assert_eq!(r["verdict"], "CONTRACT_SOURCE_BOUND");
        assert_eq!(r["capability_count"], 101);
        assert_eq!(r["checklist_item_count"], 713);
    }

    #[test]
    fn regeneration_is_idempotent_over_the_committed_views() {
        let dir = fixture("regen");
        generate(&dir).expect("generate");
        for rel in [COMPILED, SOURCE_LOCK, EVIDENCE_MAP, GENERATED_VIEW] {
            assert_eq!(
                std::fs::read(dir.join(rel)).unwrap(),
                std::fs::read(repo().join(rel)).unwrap(),
                "{rel} is not the output of `gov contract compile`"
            );
        }
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn a_semantic_difference_in_the_compiled_form_is_a_typed_failure() {
        for (name, mutate) in [
            (
                "delete one checklist item",
                Box::new(|v: &mut Value| {
                    let a1 = cap_index(v, "A1", "id");
                    v["capabilities"][a1]["checklist"]
                        .as_array_mut()
                        .unwrap()
                        .remove(0);
                }) as Box<dyn Fn(&mut Value)>,
            ),
            (
                "delete Gate U",
                Box::new(|v: &mut Value| {
                    let u = cap_index(v, "U", "id");
                    v["capabilities"].as_array_mut().unwrap().remove(u);
                }),
            ),
            (
                "change a label",
                Box::new(|v: &mut Value| {
                    let o5 = cap_index(v, "O5", "id");
                    v["capabilities"][o5]["requirement_class_label"] =
                        json!("EXECUTION REFINEMENT");
                }),
            ),
            (
                "map the Gate V label",
                Box::new(|v: &mut Value| {
                    let v1 = cap_index(v, "V1", "id");
                    v["capabilities"][v1]["requirement_class"] = json!("ORIGINAL");
                }),
            ),
            (
                "invent a per-capability value",
                Box::new(|v: &mut Value| {
                    let a1 = cap_index(v, "A1", "id");
                    v["capabilities"][a1]["severity"] = json!("HIGH");
                }),
            ),
            (
                "drop the W10 hard invariant",
                Box::new(|v: &mut Value| {
                    let w = cap_index(v, "W10", "id");
                    v["capabilities"][w]["statements"]
                        .as_array_mut()
                        .unwrap()
                        .retain(|s| s["kind"] != "hard_invariant");
                }),
            ),
            (
                "paraphrase an item",
                Box::new(|v: &mut Value| {
                    let a1 = cap_index(v, "A1", "id");
                    v["capabilities"][a1]["checklist"][0]["text"] = json!("Hard invariants exist.");
                }),
            ),
        ] {
            let dir = fixture("compiled");
            edit_yaml(&dir, COMPILED, |v| mutate(v));
            let (code, details) = err_code(&dir);
            assert_eq!(code, "CONTRACT_COMPILED_DIVERGED", "{name}: {details}");
            let _ = std::fs::remove_dir_all(&dir);
        }
    }

    #[test]
    fn a_semantic_difference_in_the_evidence_map_is_a_typed_failure() {
        for (name, mutate) in [
            (
                "delete one checklist item",
                Box::new(|v: &mut Value| {
                    let a1 = cap_index(v, "A1", "capability");
                    v["capabilities"][a1]["checklist"]
                        .as_array_mut()
                        .unwrap()
                        .remove(0);
                }) as Box<dyn Fn(&mut Value)>,
            ),
            (
                "delete Gate U",
                Box::new(|v: &mut Value| {
                    let u = cap_index(v, "U", "capability");
                    v["capabilities"].as_array_mut().unwrap().remove(u);
                }),
            ),
            (
                "change a label",
                Box::new(|v: &mut Value| {
                    let v4 = cap_index(v, "V4", "capability");
                    v["capabilities"][v4]["requirement_class_label"] =
                        json!("NEW EXECUTION REFINEMENT");
                }),
            ),
            (
                "drop a per-capability contract field",
                Box::new(|v: &mut Value| {
                    let a1 = cap_index(v, "A1", "capability");
                    v["capabilities"][a1]
                        .as_object_mut()
                        .unwrap()
                        .remove("freshness_triggers");
                }),
            ),
            (
                "an evidence class the contract does not define",
                Box::new(|v: &mut Value| {
                    let a1 = cap_index(v, "A1", "capability");
                    v["capabilities"][a1]["evidence_class"] = json!("vibes");
                }),
            ),
            (
                "a tier O5 does not define",
                Box::new(|v: &mut Value| {
                    let a1 = cap_index(v, "A1", "capability");
                    v["capabilities"][a1]["health_scheduler_tiers"] = json!(["G9"]);
                }),
            ),
            (
                "drop a challenge",
                Box::new(|v: &mut Value| {
                    v["advanced_qualification_challenges"]
                        .as_array_mut()
                        .unwrap()
                        .pop();
                }),
            ),
        ] {
            let dir = fixture("map");
            edit_yaml(&dir, EVIDENCE_MAP, |v| mutate(v));
            let (code, details) = err_code(&dir);
            assert_eq!(code, "CONTRACT_EVIDENCE_MAP_DIVERGED", "{name}: {details}");
            let _ = std::fs::remove_dir_all(&dir);
        }
    }

    #[test]
    fn a_semantic_difference_in_the_generated_view_is_a_typed_failure() {
        let view = std::fs::read_to_string(repo().join(GENERATED_VIEW)).unwrap();
        let first_item = view
            .lines()
            .find(|l| l.starts_with("- [ ] Constitution/hard invariants"))
            .unwrap()
            .to_string();
        let u_row = view
            .lines()
            .find(|l| l.starts_with("| `U` |"))
            .unwrap()
            .to_string();
        for (name, edited) in [
            (
                "delete one checklist item",
                view.replacen(&format!("{first_item}\n"), "", 1),
            ),
            ("delete Gate U", view.replacen(&format!("{u_row}\n"), "", 1)),
            (
                "change a label",
                view.replacen("`NEW TESTING REFINEMENT`", "`TESTING_REFINEMENT`", 1),
            ),
            (
                "edit prose",
                view.replacen("Derived and non-authoritative", "Authoritative", 1),
            ),
        ] {
            let dir = fixture("view");
            std::fs::write(dir.join(GENERATED_VIEW), edited).unwrap();
            let (code, details) = err_code(&dir);
            assert_eq!(
                code, "CONTRACT_GENERATED_VIEW_DIVERGED",
                "{name}: {details}"
            );
            let _ = std::fs::remove_dir_all(&dir);
        }
    }

    #[test]
    fn the_lock_and_the_schema_are_part_of_the_binding() {
        let dir = fixture("lock");
        edit_yaml(&dir, SOURCE_LOCK, |v| {
            v["evidence_map_source_sha256"] = json!("0".repeat(64))
        });
        assert_eq!(err_code(&dir).0, "CONTRACT_LOCK_DIVERGED");
        let _ = std::fs::remove_dir_all(&dir);
        // a schema that cannot express Gate U is refused
        let dir = fixture("schema");
        let p = dir.join(SCHEMA);
        let s = std::fs::read_to_string(&p)
            .unwrap()
            .replace("^[A-Z]+[0-9]*$", "^[A-Z]+[0-9]+$");
        std::fs::write(&p, s).unwrap();
        assert_eq!(err_code(&dir).0, "CONTRACT_SCHEMA_DIVERGED");
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn governed_evidence_values_survive_regeneration() {
        // BC-P2-02 changed the governed shape (owners are objects; evidence class, tiers and freshness triggers are
        // what the owners determine). The property is unchanged: governed values survive regeneration, a governed
        // value changed without a recompile is detected, and data regeneration would discard is refused.
        let dir = fixture("governed");
        edit_yaml(&dir, EVIDENCE_MAP, |v| {
            let a1 = cap_index(v, "A1", "capability");
            let owner = v["capabilities"][a1]["automated_checks"][0]["id"].clone();
            v["capabilities"][a1]["automated_checks"][0]["exercises"] =
                json!("a governed statement of what this owner exercises");
            v["capabilities"][a1]["checklist"][1]["automated_checks"] = json!([owner]);
        });
        // the lock (and the view) now lag the map: verify says so, and regeneration brings them up to date
        assert_eq!(err_code(&dir).0, "CONTRACT_EVIDENCE_MAP_NOT_RECOMPILED");
        generate(&dir).expect("regenerate");
        let map = crate::util::read_yaml(&dir.join(EVIDENCE_MAP)).unwrap();
        let a1 = cap_index(&map, "A1", "capability");
        assert_eq!(
            map["capabilities"][a1]["automated_checks"][0]["exercises"],
            "a governed statement of what this owner exercises"
        );
        assert_eq!(
            map["capabilities"][a1]["checklist"][1]["automated_checks"][0],
            map["capabilities"][a1]["automated_checks"][0]["id"]
        );
        verify(&dir).expect("verifies after regeneration");
        // data regeneration would discard is refused, not dropped
        edit_yaml(&dir, EVIDENCE_MAP, |v| {
            let a1 = cap_index(v, "A1", "capability");
            v["capabilities"][a1]["evidence_owners"] = json!(["somebody's mapping"]);
        });
        let before = std::fs::read(dir.join(EVIDENCE_MAP)).unwrap();
        assert_eq!(
            generate(&dir).unwrap_err().code,
            "CONTRACT_EVIDENCE_MAP_DIVERGED"
        );
        assert_eq!(std::fs::read(dir.join(EVIDENCE_MAP)).unwrap(), before);
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn an_edited_import_is_refused_before_anything_else() {
        let dir = fixture("import");
        let p = dir.join(CANONICAL_IMPORT);
        let mut t = std::fs::read_to_string(&p).unwrap();
        t.push_str("\nan unauthorised addition\n");
        std::fs::write(&p, t).unwrap();
        assert_eq!(err_code(&dir).0, "CONTRACT_SOURCE_DIVERGED");
        assert_eq!(generate(&dir).unwrap_err().code, "CONTRACT_SOURCE_DIVERGED");
        let _ = std::fs::remove_dir_all(&dir);
    }

    // ------------------------------------------------------------------ BC-P2-02: evidence owners (P2-AR-0042)

    fn listed(args: &[&str]) -> BTreeSet<String> {
        let exe = std::env::current_exe().expect("the running test binary");
        let o = std::process::Command::new(exe)
            .args(args)
            .output()
            .expect("list the harness's tests");
        String::from_utf8_lossy(&o.stdout)
            .lines()
            .filter_map(|l| l.strip_suffix(": test").map(String::from))
            .collect()
    }

    #[test]
    fn the_owner_resolver_lists_exactly_the_tests_the_lib_harness_runs() {
        // the harness's own list is the authority: the resolver must agree with it exactly, both ways
        let all = listed(&["--list", "--format", "terse"]);
        let ignored = listed(&["--list", "--format", "terse", "--ignored"]);
        let idx = test_index(&repo(), "lib").expect("the lib crate root");
        let found: BTreeSet<String> = idx.keys().cloned().collect();
        assert!(all.len() > 200, "{}", all.len());
        assert_eq!(found, all, "resolver vs `cargo test --lib -- --list`");
        let found_ignored: BTreeSet<String> = idx
            .iter()
            .filter(|(_, s)| s.ignored)
            .map(|(k, _)| k.clone())
            .collect();
        assert_eq!(found_ignored, ignored);
        let me = &idx
            ["contracts::tests::the_owner_resolver_lists_exactly_the_tests_the_lib_harness_runs"];
        assert_eq!(me.file, "runtime/src/contracts.rs");
    }

    #[test]
    fn the_resolver_reads_items_not_text() {
        let dir = std::env::temp_dir().join(format!("gov-owner-lex-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(dir.join("src/a")).unwrap();
        std::fs::write(
            dir.join("src/lib.rs"),
            "//! #[test] fn doc_comment() {}\nmod a;\n#[cfg(test)]\nmod tests {\n    /* #[test] fn in_block_comment() { } */\n    #[test]\n    fn real() { let _ = \"#[test] fn in_string() {\"; let _ = '{'; let _ = r#\"}\"}\"#; }\n    #[test]\n    #[ignore = \"slow\"]\n    fn skipped() {}\n    fn helper<'a>(x: &'a str) -> &'a str { x }\n    mod inner {\n        #[test]\n        fn nested() {}\n    }\n}\n",
        )
        .unwrap();
        std::fs::write(
            dir.join("src/a.rs"),
            "mod b;\n#[test]\nfn at_a() { let c = '\\''; let _ = c; }\n",
        )
        .unwrap();
        std::fs::write(dir.join("src/a/b.rs"), "#[test] fn at_b() {}\n").unwrap();
        let mut out = BTreeMap::new();
        scan_module_file(
            &dir,
            &dir.join("src/lib.rs"),
            &[],
            &mut out,
            &mut BTreeSet::new(),
        );
        let names: Vec<&str> = out.keys().map(|s| s.as_str()).collect();
        assert_eq!(
            names,
            vec![
                "a::at_a",
                "a::b::at_b",
                "tests::inner::nested",
                "tests::real",
                "tests::skipped"
            ]
        );
        assert!(out["tests::skipped"].ignored && !out["tests::real"].ignored);
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn owner_references_resolve_against_the_product() {
        let reg = OwnerRegistry::load(&repo());
        let ok = |id: &str, record: Option<&str>, tests: &[&str]| {
            let t: Vec<String> = tests.iter().map(|s| s.to_string()).collect();
            matches!(reg.resolve_id(id, record, &t), Resolution::Resolved(_))
        };
        assert!(ok("check:schema_invariants", None, &[]));
        assert!(ok("doctor:D011", None, &[]));
        assert!(ok("g0:task close", None, &[]));
        assert!(ok(
            "test:lib:contracts::tests::the_committed_binding_chain_verifies",
            None,
            &[]
        ));
        assert!(ok(
            "test:certification:ws03::every_cli_command_label_is_classified_by_g0",
            None,
            &[]
        ));
        assert!(ok("human-gate:gate answer", Some("human-gate"), &[]));
        assert!(ok("release:release build", Some("release-manifest"), &[]));
        assert!(ok(
            "heldout:release/verification/4.1.6-r1/evidence/heldout-tests",
            None,
            &["heldout_srr::a1_signature_lifted_from_a_different_document_is_refused"]
        ));
        assert!(ok("obligation:AC-14", None, &[]));
        assert!(ok("obligation:AC-6", None, &[]));
        // negatives: each is a typed non-resolution, never a pass
        for (id, record) in [
            ("check:no_such_family", None),
            ("check:D011", None),
            ("doctor:schema_invariants", None),
            ("g0:release build", None),
            ("g0:no such command", None),
            ("test:lib:contracts::tests::no_such_test", None),
            ("test:lib:contracts::tests", None),
            ("test:bench:x", None),
            ("human-gate:gate answer", None),
            ("human-gate:gate answer", Some("no-such-record")),
            (
                "heldout:release/verification/nowhere/evidence/heldout-tests",
                None,
            ),
            ("heldout:tests/certification", None),
            ("obligation:AC-10", None),
            ("obligation:AC-99", None),
            ("vibes:anything", None),
        ] {
            assert!(
                matches!(reg.resolve_id(id, record, &[]), Resolution::Unresolved(_)),
                "{id} must not resolve"
            );
        }
        assert!(matches!(
            reg.resolve_id(
                "heldout:release/verification/4.1.6-r1/evidence/heldout-tests",
                None,
                &["heldout_srr::no_such_test".to_string()]
            ),
            Resolution::Unresolved(_)
        ));
    }

    #[test]
    fn what_the_owners_determine_is_derived_from_the_product() {
        let m = model();
        let row = json!({"automated_checks": [
            {"id": "check:graph_integrity", "class": "governance health check", "tiers": ["G1", "G2", "G4", "G5", "G6"]},
            {"id": "g0:task close", "class": "automated invariant/guard", "tiers": ["G0"]},
            {"id": "test:lib:graph::lineage::tests::stale_links_and_unconsumed_outputs_are_named", "class": "unit/integration/system test"}],
            "independent_verification": [{"id": "obligation:AC-12", "class": "independent audit evidence"}]});
        let d = derived_fields(&m, &row);
        assert_eq!(
            d["evidence_class"],
            json!([
                "automated invariant/guard",
                "unit/integration/system test",
                "governance health check",
                "independent audit evidence"
            ])
        );
        assert_eq!(
            d["health_scheduler_tiers"],
            json!(["G0", "G1", "G2", "G4", "G5", "G6"])
        );
        // graph_integrity keys its result by the records, the index manifest and the path map (plus the implicit
        // classes): those are exactly the inputs that make its evidence stale
        let fresh: Vec<String> = str_array(d.get("freshness_triggers"));
        for t in [
            "governing contract/policy",
            "runtime/kernel implementation",
            "schema",
            "project path map",
            "authoritative spec/decision",
            "relevant index manifest",
        ] {
            assert!(fresh.contains(&t.to_string()), "{t}: {fresh:?}");
        }
        assert!(!fresh.contains(&"model/retrieval profile".to_string()));
        assert_eq!(
            d["adoption_obligation"]["owners"],
            json!(["check:graph_integrity"])
        );
        assert_eq!(d["remediation_rule"], REMEDIATION_TIERED);
        let bare = derived_fields(&m, &json!({"automated_checks": []}));
        assert_eq!(bare["evidence_class"], NOT_YET_MAPPED);
    }

    #[test]
    fn every_capability_names_a_running_owner_and_every_owner_resolves() {
        let m = model();
        let map = crate::util::read_yaml(&repo().join(EVIDENCE_MAP)).unwrap();
        let chk = owner_differences(&m, &map, &OwnerRegistry::load(&repo()), true);
        assert!(chk.unresolved.is_empty(), "{:#?}", chk.unresolved);
        assert!(chk.missing.is_empty(), "{:#?}", chk.missing);
        assert!(chk.invalid.is_empty(), "{:#?}", chk.invalid);
        assert_eq!(chk.summary["capabilities"], 101);
        assert_eq!(chk.summary["deferred"], json!([]));
        for row in lines_of(&map, "capabilities") {
            let running = owners_of(&row, "automated_checks")
                .iter()
                .chain(owners_of(&row, "independent_verification").iter())
                .filter(|o| owner_kind(owner_id(o).unwrap()).unwrap().runs)
                .count();
            assert!(running > 0, "{}", row["capability"]);
        }
    }

    /// Mutation controls for BC-P2-02: each makes `gov contract verify` fail with its own typed error.
    #[test]
    fn an_owner_mutation_is_a_typed_failure() {
        type M = Box<dyn Fn(&mut Value)>;
        let first_test_owner = |v: &Value, cap: &str| -> usize {
            let i = cap_index(v, cap, "capability");
            v["capabilities"][i]["automated_checks"]
                .as_array()
                .unwrap()
                .iter()
                .position(|o| o["id"].as_str().unwrap().starts_with("test:"))
                .expect("a test owner")
        };
        let first_tier_owner = |v: &Value, cap: &str| -> usize {
            let i = cap_index(v, cap, "capability");
            v["capabilities"][i]["automated_checks"]
                .as_array()
                .unwrap()
                .iter()
                .position(|o| o["id"].as_str().unwrap().starts_with("check:"))
                .expect("a check owner")
        };
        let cases: Vec<(&str, M, &str)> = vec![
            (
                "zero owners (Gate U)",
                Box::new(|v: &mut Value| {
                    let u = cap_index(v, "U", "capability");
                    v["capabilities"][u]["automated_checks"] = json!([]);
                    v["capabilities"][u]["independent_verification"] = json!([]);
                    for it in v["capabilities"][u]["checklist"].as_array_mut().unwrap() {
                        it["automated_checks"] = json!([]);
                    }
                }),
                "CONTRACT_EVIDENCE_OWNER_MISSING",
            ),
            (
                "only an obligation of a future verifier",
                Box::new(|v: &mut Value| {
                    let c = cap_index(v, "A1", "capability");
                    v["capabilities"][c]["automated_checks"] = json!([]);
                    v["capabilities"][c]["independent_verification"] =
                        json!([{"id": "obligation:AC-12", "class": "independent audit evidence"}]);
                    for it in v["capabilities"][c]["checklist"].as_array_mut().unwrap() {
                        it["automated_checks"] = json!([]);
                    }
                }),
                "CONTRACT_EVIDENCE_OWNER_MISSING",
            ),
            (
                "a test owner that does not exist",
                Box::new(move |v: &mut Value| {
                    let c = cap_index(v, "W3", "capability");
                    let t = first_test_owner(v, "W3");
                    v["capabilities"][c]["automated_checks"][t]["id"] =
                        json!("test:lib:context::manifest::tests::no_such_test");
                }),
                "CONTRACT_EVIDENCE_OWNER_UNRESOLVED",
            ),
            (
                "a check the catalogue does not declare",
                Box::new(move |v: &mut Value| {
                    let c = cap_index(v, "B2", "capability");
                    let t = first_tier_owner(v, "B2");
                    v["capabilities"][c]["automated_checks"][t]["id"] =
                        json!("check:path_map_vibes");
                }),
                "CONTRACT_EVIDENCE_OWNER_UNRESOLVED",
            ),
            (
                "a tier the catalogue does not declare for the check",
                Box::new(move |v: &mut Value| {
                    let c = cap_index(v, "B2", "capability");
                    let t = first_tier_owner(v, "B2");
                    v["capabilities"][c]["automated_checks"][t]["tiers"] = json!(["G0"]);
                }),
                "CONTRACT_EVIDENCE_OWNER_UNRESOLVED",
            ),
            (
                "an independent owner filed as builder evidence",
                Box::new(|v: &mut Value| {
                    let c = cap_index(v, "A2", "capability");
                    let ind = v["capabilities"][c]["independent_verification"][0].clone();
                    v["capabilities"][c]["automated_checks"]
                        .as_array_mut()
                        .unwrap()
                        .push(ind);
                }),
                "CONTRACT_EVIDENCE_OWNER_INVALID",
            ),
            (
                "an evidence class claimed without an owner that carries it",
                Box::new(|v: &mut Value| {
                    let c = cap_index(v, "C4", "capability");
                    v["capabilities"][c]["evidence_class"]
                        .as_array_mut()
                        .unwrap()
                        .push(json!("synthetic-repository evidence"));
                }),
                "CONTRACT_EVIDENCE_OWNER_INVALID",
            ),
            (
                "a tier claimed without an owner that runs there",
                Box::new(|v: &mut Value| {
                    let c = cap_index(v, "Q2", "capability");
                    v["capabilities"][c]["health_scheduler_tiers"] = json!(["G6"]);
                }),
                "CONTRACT_EVIDENCE_OWNER_INVALID",
            ),
            (
                "an owner class outside Contract v3:81-91",
                Box::new(move |v: &mut Value| {
                    let c = cap_index(v, "E4", "capability");
                    let t = first_test_owner(v, "E4");
                    v["capabilities"][c]["automated_checks"][t]["class"] = json!("vibes");
                }),
                "CONTRACT_EVIDENCE_OWNER_INVALID",
            ),
            (
                "a freshness trigger outside Contract v3:97-109",
                Box::new(|v: &mut Value| {
                    let c = cap_index(v, "D1", "capability");
                    v["capabilities"][c]["freshness_triggers"] = json!(["the weather"]);
                }),
                "CONTRACT_EVIDENCE_MAP_DIVERGED",
            ),
            (
                "an evidence class outside Contract v3:81-91",
                Box::new(|v: &mut Value| {
                    let c = cap_index(v, "D1", "capability");
                    v["capabilities"][c]["evidence_class"] = json!(["vibes"]);
                }),
                "CONTRACT_EVIDENCE_MAP_DIVERGED",
            ),
            (
                "a status outside the frozen gate contract §4",
                Box::new(|v: &mut Value| {
                    let c = cap_index(v, "D2", "capability");
                    v["capabilities"][c]["allowed_status"] = json!(["GREEN_ENOUGH"]);
                }),
                "CONTRACT_EVIDENCE_MAP_DIVERGED",
            ),
            (
                "a freshness trigger in use with no owner proving its invalidation",
                Box::new(|v: &mut Value| {
                    v["freshness_invalidation"]
                        .as_array_mut()
                        .unwrap()
                        .retain(|e| e["trigger"] != "project path map");
                }),
                "CONTRACT_EVIDENCE_OWNER_INVALID",
            ),
            (
                "a checklist item naming an owner its capability does not have",
                Box::new(|v: &mut Value| {
                    let c = cap_index(v, "A1", "capability");
                    v["capabilities"][c]["checklist"][0]["automated_checks"] =
                        json!(["check:graph_integrity"]);
                }),
                "CONTRACT_EVIDENCE_OWNER_INVALID",
            ),
            (
                "a valid owner swapped in without a recompile",
                Box::new(move |v: &mut Value| {
                    let c = cap_index(v, "W8", "capability");
                    let t = first_test_owner(v, "W8");
                    v["capabilities"][c]["automated_checks"][t]["exercises"] =
                        json!("edited by hand after the last compile");
                }),
                "CONTRACT_EVIDENCE_MAP_NOT_RECOMPILED",
            ),
        ];
        for (name, mutate, want) in cases {
            let dir = fixture("owners");
            edit_yaml(&dir, EVIDENCE_MAP, |v| mutate(v));
            let (code, details) = err_code(&dir);
            assert_eq!(code, want, "{name}: {details}");
            let _ = std::fs::remove_dir_all(&dir);
        }
    }

    #[test]
    fn a_tree_without_the_owners_sources_defers_and_discloses_and_never_compiles() {
        // a release-tooling tree (the chain only): verify binds the chain and discloses what it could not resolve
        let dir = bare_fixture("bare");
        let r = verify(&dir).expect("the chain verifies where the sources are absent");
        assert_eq!(r["verdict"], "CONTRACT_SOURCE_BOUND");
        let deferred = r["evidence_owners"]["deferred"].as_array().unwrap();
        assert!(!deferred.is_empty());
        assert!(deferred.iter().all(|d| d["reason"]
            .as_str()
            .unwrap()
            .contains("this tree does not carry")));
        assert_eq!(
            r["evidence_owners"]["not_in_this_tree"]
                .as_array()
                .unwrap()
                .len(),
            4
        );
        // an owner that no tree could resolve is still refused (a catalogue check is resolved in the binary)
        edit_yaml(&dir, EVIDENCE_MAP, |v| {
            let c = cap_index(v, "B2", "capability");
            let t = v["capabilities"][c]["automated_checks"]
                .as_array()
                .unwrap()
                .iter()
                .position(|o| o["id"].as_str().unwrap().starts_with("check:"))
                .unwrap();
            v["capabilities"][c]["automated_checks"][t]["id"] = json!("check:path_map_vibes");
        });
        assert_eq!(err_code(&dir).0, "CONTRACT_EVIDENCE_OWNER_UNRESOLVED");
        let _ = std::fs::remove_dir_all(&dir);
        // compile never defers: it binds only owners it resolved
        let dir = bare_fixture("bare-compile");
        let e = generate(&dir).unwrap_err();
        assert_eq!(e.code, "CONTRACT_EVIDENCE_OWNER_UNRESOLVED");
        assert!(e.message.starts_with("refusing to compile"));
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn the_matrix_is_generated_from_the_map_with_the_supplied_run_evidence() {
        let dir = std::env::temp_dir().join(format!("gov-matrix-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(&dir).unwrap();
        let lib = dir.join("lib.out");
        std::fs::write(
            &lib,
            "test contracts::tests::the_committed_binding_chain_verifies ... ok\ntest scheduler::tests::tiers_parse_and_default_selection ... FAILED\n",
        )
        .unwrap();
        let ev = RunEvidence {
            lib: vec![lib],
            ..Default::default()
        };
        let (mx, md) = suite_to_contract(&repo(), &ev).expect("matrix");
        assert_eq!(mx["capabilities"].as_array().unwrap().len(), 101);
        assert_eq!(mx["contract"]["verify_verdict"], "CONTRACT_SOURCE_BOUND");
        let owners: Vec<&Value> = mx["capabilities"]
            .as_array()
            .unwrap()
            .iter()
            .flat_map(|c| c["owners"].as_array().unwrap().iter())
            .collect();
        let status_of = |id: &str| {
            owners
                .iter()
                .find(|o| o["id"] == id)
                .map(|o| o["last_run"]["status"].clone())
        };
        if let Some(s) = status_of("test:lib:scheduler::tests::tiers_parse_and_default_selection") {
            assert_eq!(s, "FAILED");
        }
        // nothing is inferred: an owner the supplied evidence does not cover is reported as such
        assert!(owners
            .iter()
            .any(|o| o["last_run"]["status"] == "NOT_IN_SUPPLIED_EVIDENCE"));
        for c in m_ids() {
            assert!(md.contains(&format!("#### {c} — ")), "{c}");
        }
        let _ = std::fs::remove_dir_all(&dir);
    }

    fn m_ids() -> Vec<String> {
        model().capability_ids()
    }
}
