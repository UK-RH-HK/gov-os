//! **Materiality of a change, determined from what it changes** (BC-P2-13, CIT-P side; Contract v3:446 "Consequential
//! changes automatically invoke required impact/gate logic", :638-647 "Auto-trigger for material: architecture,
//! behaviour, interfaces, security, governance/policy, infrastructure cost, acceptance criteria, data migration";
//! framework §47 "Every accepted material state change is handled atomically", §48 "The human should not need to type
//! /impact").
//!
//! The proposer's trigger label is a *claim*; this module derives, from the records, paths and content a change
//! touches, which of the eight material classes it belongs to. `cit::propose`/`simulate` take the union of the
//! declared label and the derived classes ([`Materiality::effective_triggers`]), so a material change labelled
//! `editorial` is still simulated automatically, estimated at its class's radius and gated by
//! `CHANGE_POLICY.human_gate_triggers`. The same classifier answers "is this *performed* change material?" for work
//! done outside a CIT ([`classify_paths`]); the task-close host (`orchestration::tasks::close`, WS-5, round 3) calls it
//! so that material edits made inside ordinary tasks cannot close outside CIT-P/CIT-E (integration point, see the
//! WS-4 round-2 report).
//!
//! ## Rules (kernel floor; a project cannot remove a class from a change)
//!
//! | what changes | class |
//! |---|---|
//! | an `architecture` record; `docs/architecture/**`, ADRs, `spec/architecture/**` | architecture_change |
//! | an `interface` record; API contracts (`*.proto`, `*.graphql`, OpenAPI/Swagger, `*.avsc`, `*.wsdl`) | interface_change |
//! | acceptance/success/failure criteria of requirements and scenarios; test obligations; a feature's requirement/scenario/acceptance-test lists | acceptance_criteria_change |
//! | any other content of a requirement, scenario, feature or decision (not its planning attributes `priority`, `owner_role`, `legacy_source`); product source (repository-contract class `source`) | behaviour_change |
//! | a `security` record; security-named paths (auth, crypto, permission, secrets, TLS, …); a removed or weakened line carrying a security check (verify/signature/authenticate/authorise/permission/…) | security_change |
//! | `governance/**` (except `governance/generated/**`), `framework/**`, any policy/overlay configuration file | governance_change |
//! | infrastructure definitions (`infra/**`, Terraform, Kubernetes/Helm, Docker/Compose, CloudFormation, Bicep, serverless) | infrastructure_cost |
//! | migrations (`migrations/**`, `db/migrate/**`, Alembic/Flyway), SQL carrying DDL/DML, dataset schema fields | data_migration |
//!
//! Decisions carry the class of what they decide (`tags`), defaulting to behaviour. Bookkeeping fields the OS writes
//! (`updated`, `staleness`, `retest_required`, `journal`, `os_state`, …) never make a change material. Each finding
//! records its evidence and rule, and whether the change must pass a CIT even when made inside a task
//! (`requires_cit_in_task`): every class does, except behaviour changes to product source, which an implementation
//! task is contracted to make (its task contract and declared requirements govern them).
use crate::records::{parse_record_text, RecordStore};
use crate::util::glob_match;
use crate::Project;
use serde_json::{json, Value};
use std::collections::BTreeSet;

/// The eight material classes of Contract v3:640-647, as `CHANGE_POLICY` trigger names, most severe first.
pub const MATERIAL_CLASSES: [&str; 8] = [
    "governance_change",
    "architecture_change",
    "security_change",
    "data_migration",
    "interface_change",
    "infrastructure_cost",
    "acceptance_criteria_change",
    "behaviour_change",
];

/// Record fields the OS itself writes as bookkeeping: a change confined to them is not a material change.
pub const BOOKKEEPING_FIELDS: &[&str] = &[
    "updated",
    "created",
    "staleness",
    "retest_required",
    "retest_reason",
    "revalidation",
    "provenance",
    "journal",
    "os_state",
    "os_binding",
    "closed_at",
    "closed_by_report",
    "status_note",
    "human_gate",
];

/// Planning attributes of a specification record (requirement, scenario, feature): in which order it is worked, who
/// owns it and where it came from. They do not specify what the product does, so a change confined to them is not a
/// behaviour change (framework §49 "R1 local semantic change" at most); every other field of such a record is.
pub const PLANNING_FIELDS: &[&str] = &["priority", "owner_role", "legacy_source"];

const CRITERIA_FIELDS: &[&str] = &[
    "acceptance_criteria",
    "success_criteria",
    "failure_criteria",
    "then",
    "given",
    "when",
    "acceptance",
    "acceptance_tests",
];

const ARCHITECTURE_PATHS: &[&str] = &[
    "spec/architecture/**",
    "docs/architecture/**",
    "**/architecture/**",
    "**/adr/**",
    "**/ADR-*",
    "**/adr-*",
    "**/ARCHITECTURE.md",
    "ARCHITECTURE.md",
];
const INTERFACE_PATHS: &[&str] = &[
    "**/*.proto",
    "**/*.graphql",
    "**/*.gql",
    "**/openapi*.yaml",
    "**/openapi*.yml",
    "**/openapi*.json",
    "**/swagger*.yaml",
    "**/swagger*.yml",
    "**/swagger*.json",
    "**/*.avsc",
    "**/*.wsdl",
    "spec/interfaces/**",
];
const INFRA_PATHS: &[&str] = &[
    "infra/**",
    "infrastructure/**",
    "terraform/**",
    "**/*.tf",
    "**/*.tfvars",
    "k8s/**",
    "kubernetes/**",
    "helm/**",
    "charts/**",
    "deploy/**",
    "**/Dockerfile",
    "**/docker-compose*.yml",
    "**/docker-compose*.yaml",
    "**/*.bicep",
    "**/cloudformation*",
    "**/serverless.yml",
    "**/serverless.yaml",
];
const MIGRATION_PATHS: &[&str] = &[
    "migrations/**",
    "**/migrations/**",
    "**/migration/**",
    "db/migrate/**",
    "**/alembic/**",
    "**/flyway/**",
];
const GOVERNANCE_FILES: &[&str] = &[
    "**/*_POLICY.yaml",
    "**/PROJECT_POLICY.yaml",
    "**/PROJECT_EXCEPTIONS.yaml",
    "**/REPOSITORY_CONTRACT.yaml",
    "**/TOOL_PERMISSIONS.yaml",
    "**/DATA_SENSITIVITY.yaml",
    "**/MODEL_ROUTING_OVERRIDES.yaml",
    "**/CAPABILITY_PROFILE.yaml",
];
/// Path segments that name security machinery.
const SECURITY_SEGMENTS: &[&str] = &[
    "auth",
    "authn",
    "authz",
    "authentication",
    "authorization",
    "authorisation",
    "security",
    "crypto",
    "cryptography",
    "permission",
    "permissions",
    "acl",
    "rbac",
    "oauth",
    "jwt",
    "secrets",
    "secret",
    "tls",
    "ssl",
    "certs",
    "certificates",
    "csrf",
    "sanitize",
    "sanitise",
];
/// Tokens of a line that implements a security check; removing or changing such a line is a security change.
const SECURITY_TOKENS: &[&str] = &[
    "verify",
    "signature",
    "authenticat",
    "authoriz",
    "authoris",
    "permission",
    "csrf",
    "sanitiz",
    "sanitis",
    "encrypt",
    "decrypt",
    "hash_password",
    "bcrypt",
    "argon",
    "check_access",
    "require_role",
    "is_admin",
    "acl",
    "rbac",
    "certificate",
    "tls",
];
/// SQL that changes a schema or rewrites data.
const SQL_CHANGE: &[&str] = &[
    "create table",
    "alter table",
    "drop table",
    "drop column",
    "truncate",
    "delete from",
    "update ",
    "insert into",
    "rename column",
    "create index",
    "drop index",
];
const SQL_DESTRUCTIVE: &[&str] = &["drop table", "drop column", "truncate", "delete from"];
/// Infrastructure attributes whose change moves cost.
const SIZING_TOKENS: &[&str] = &[
    "instance_class",
    "instance_type",
    "machine_type",
    "vm_size",
    "node_count",
    "replicas",
    "min_size",
    "max_size",
    "desired_capacity",
    "allocated_storage",
    "sku",
    "cpu",
    "memory",
    "storage",
    "size",
];

/// One reason a change is material.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Finding {
    pub class: &'static str,
    /// The record id or repository path the finding is about.
    pub subject: String,
    pub rule: &'static str,
    pub evidence: String,
    /// Whether this change must pass CIT-P/CIT-E even when made inside an ordinary task.
    pub requires_cit_in_task: bool,
}

impl Finding {
    pub fn to_value(&self) -> Value {
        json!({"class": self.class, "subject": self.subject, "rule": self.rule, "evidence": self.evidence, "requires_cit_in_task": self.requires_cit_in_task})
    }
}

/// The materiality of a change set.
#[derive(Debug, Clone, Default)]
pub struct Materiality {
    pub findings: Vec<Finding>,
}

fn class_rank(c: &str) -> usize {
    MATERIAL_CLASSES
        .iter()
        .position(|x| *x == c)
        .unwrap_or(MATERIAL_CLASSES.len())
}

impl Materiality {
    /// The derived classes, most severe first.
    pub fn classes(&self) -> Vec<&'static str> {
        let set: BTreeSet<&'static str> = self.findings.iter().map(|f| f.class).collect();
        let mut v: Vec<&'static str> = set.into_iter().collect();
        v.sort_by_key(|c| class_rank(c));
        v
    }
    pub fn material(&self) -> bool {
        !self.findings.is_empty()
    }
    /// Findings that must go through change control even inside a task.
    pub fn requiring_cit(&self) -> Vec<&Finding> {
        self.findings
            .iter()
            .filter(|f| f.requires_cit_in_task)
            .collect()
    }
    /// The declared label (when it names a material class) united with every derived class, most severe first.
    pub fn effective_triggers(&self, declared: &str) -> Vec<String> {
        let mut v: Vec<String> = self.classes().into_iter().map(String::from).collect();
        if MATERIAL_CLASSES.contains(&declared) && !v.iter().any(|c| c == declared) {
            v.push(declared.to_string());
        }
        v.sort_by_key(|c| class_rank(c));
        v
    }
    /// The single most severe effective trigger (the declared label when nothing material was derived).
    pub fn effective_trigger(&self, declared: &str) -> String {
        self.effective_triggers(declared)
            .into_iter()
            .next()
            .unwrap_or_else(|| declared.to_string())
    }
    pub fn to_value(&self, declared: &str) -> Value {
        let derived = self.classes();
        json!({
            "declared_trigger": declared,
            "derived_classes": derived,
            "effective_triggers": self.effective_triggers(declared),
            "effective_trigger": self.effective_trigger(declared),
            "material": self.material() || MATERIAL_CLASSES.contains(&declared),
            "label_understates": !derived.is_empty() && !MATERIAL_CLASSES.contains(&declared),
            "requires_cit_in_task": self.requiring_cit().iter().map(|f| f.to_value()).collect::<Vec<_>>(),
            "findings": self.findings.iter().map(|f| f.to_value()).collect::<Vec<_>>(),
            "rule_source": "cit::materiality (kernel floor; Contract v3:638-647)",
        })
    }
    fn push(
        &mut self,
        class: &'static str,
        subject: &str,
        rule: &'static str,
        evidence: String,
        in_task: bool,
    ) {
        let f = Finding {
            class,
            subject: subject.to_string(),
            rule,
            evidence,
            requires_cit_in_task: in_task,
        };
        if !self.findings.contains(&f) {
            self.findings.push(f);
        }
    }
}

/// One change to classify.
#[derive(Debug, Clone)]
pub enum Change {
    /// A governed record: `before`/`after` are its data (`None` = did not exist / removed). `fields` lists the
    /// top-level fields the change touches; empty means "derive from before/after".
    Record {
        id: String,
        rtype: String,
        path: String,
        fields: Vec<String>,
        before: Option<Value>,
        after: Option<Value>,
    },
    /// Any other repository path: `before`/`after` are its text (`None` = absent).
    File {
        path: String,
        before: Option<String>,
        after: Option<String>,
    },
}

fn tokens(path: &str) -> Vec<String> {
    path.to_lowercase()
        .split(|c: char| !c.is_ascii_alphanumeric())
        .filter(|s| !s.is_empty())
        .map(String::from)
        .collect()
}

fn any_glob(globs: &'static [&'static str], path: &str) -> Option<&'static str> {
    globs.iter().copied().find(|g| glob_match(g, path))
}

fn changed_fields(before: Option<&Value>, after: Option<&Value>) -> Vec<String> {
    let empty = serde_json::Map::new();
    let b = before.and_then(|v| v.as_object()).unwrap_or(&empty);
    let a = after.and_then(|v| v.as_object()).unwrap_or(&empty);
    let mut keys: BTreeSet<String> = b.keys().cloned().collect();
    keys.extend(a.keys().cloned());
    keys.into_iter().filter(|k| b.get(k) != a.get(k)).collect()
}

fn tag_classes(data: &Value) -> Vec<&'static str> {
    let mut out = vec![];
    let tags: Vec<String> = data["tags"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|t| t.as_str().map(|s| s.to_lowercase()))
                .collect()
        })
        .unwrap_or_default();
    for t in &tags {
        let c = if t.contains("architect") {
            "architecture_change"
        } else if t.contains("secur") || t.contains("privacy") || t.contains("auth") {
            "security_change"
        } else if t.contains("interface") || t == "api" {
            "interface_change"
        } else if t.contains("infra") || t.contains("cost") {
            "infrastructure_cost"
        } else if t.contains("migration") || t.contains("schema") || t == "data" {
            "data_migration"
        } else if t.contains("governance") || t.contains("policy") {
            "governance_change"
        } else {
            continue;
        };
        if !out.contains(&c) {
            out.push(c);
        }
    }
    out
}

fn classify_record(
    m: &mut Materiality,
    id: &str,
    rtype: &str,
    fields: &[String],
    before: Option<&Value>,
    after: Option<&Value>,
) {
    let fields: Vec<String> = if fields.is_empty() {
        changed_fields(before, after)
    } else {
        fields.to_vec()
    };
    let content: Vec<&String> = fields
        .iter()
        .filter(|f| !BOOKKEEPING_FIELDS.contains(&f.as_str()))
        .collect();
    if content.is_empty() && before.is_some() && after.is_some() {
        return;
    }
    let what = match (before.is_some(), after.is_some()) {
        (false, true) => "created".to_string(),
        (true, false) => "removed".to_string(),
        _ => format!(
            "fields changed: {}",
            content
                .iter()
                .map(|s| s.as_str())
                .collect::<Vec<_>>()
                .join(", ")
        ),
    };
    let crit: Vec<&String> = content
        .iter()
        .copied()
        .filter(|f| CRITERIA_FIELDS.contains(&f.as_str()))
        .collect();
    let non_crit = content
        .iter()
        .any(|f| !CRITERIA_FIELDS.contains(&f.as_str()) && !PLANNING_FIELDS.contains(&f.as_str()))
        || before.is_none()
        || after.is_none();
    match rtype {
        "architecture" => m.push(
            "architecture_change",
            id,
            "record type architecture",
            format!("architecture record {id} {what}"),
            true,
        ),
        "interface" => m.push(
            "interface_change",
            id,
            "record type interface",
            format!("interface record {id} {what}"),
            true,
        ),
        "security" => m.push(
            "security_change",
            id,
            "record type security",
            format!("security record {id} {what}"),
            true,
        ),
        "test-obligation" => m.push(
            "acceptance_criteria_change",
            id,
            "record type test-obligation",
            format!("test obligation {id} {what}"),
            true,
        ),
        "requirement" | "scenario" | "feature" => {
            if !crit.is_empty() {
                m.push(
                    "acceptance_criteria_change",
                    id,
                    "acceptance criteria field",
                    format!(
                        "{rtype} {id}: {} changed",
                        crit.iter()
                            .map(|s| s.as_str())
                            .collect::<Vec<_>>()
                            .join(", ")
                    ),
                    true,
                );
            }
            if rtype == "feature" && content.iter().any(|f| f.as_str() == "interfaces") {
                m.push(
                    "interface_change",
                    id,
                    "feature interfaces",
                    format!("feature {id}: interfaces changed"),
                    true,
                );
            }
            if rtype == "feature"
                && content
                    .iter()
                    .any(|f| matches!(f.as_str(), "requirements" | "scenarios"))
            {
                m.push(
                    "acceptance_criteria_change",
                    id,
                    "feature scope",
                    format!("feature {id}: requirement/scenario set changed"),
                    true,
                );
            }
            if non_crit {
                m.push(
                    "behaviour_change",
                    id,
                    "specified behaviour",
                    format!("{rtype} {id} {what}"),
                    true,
                );
            }
        }
        "decision" => {
            let data = after.or(before).cloned().unwrap_or(Value::Null);
            let tagged = tag_classes(&data);
            if tagged.is_empty() {
                m.push(
                    "behaviour_change",
                    id,
                    "decision (product direction)",
                    format!("decision {id} {what}"),
                    true,
                );
            }
            for c in tagged {
                m.push(
                    c,
                    id,
                    "decision tag",
                    format!("decision {id} (tagged) {what}"),
                    true,
                );
            }
        }
        "data" => {
            if content.iter().any(|f| {
                matches!(
                    f.as_str(),
                    "schema"
                        | "columns"
                        | "fields"
                        | "format"
                        | "location"
                        | "source"
                        | "migration"
                )
            }) || before.is_none()
                || after.is_none()
            {
                m.push(
                    "data_migration",
                    id,
                    "dataset schema/location",
                    format!("dataset {id} {what}"),
                    true,
                );
            }
        }
        _ => {}
    }
    if !matches!(rtype, "decision") {
        let data = after.or(before).cloned().unwrap_or(Value::Null);
        for c in tag_classes(&data) {
            m.push(
                c,
                id,
                "record tag",
                format!("{rtype} {id} (tagged) {what}"),
                true,
            );
        }
    }
}

fn lines_with<'a>(text: &'a str, toks: &[&str]) -> BTreeSet<&'a str> {
    text.lines()
        .map(|l| l.trim())
        .filter(|l| {
            let lo = l.to_lowercase();
            toks.iter().any(|t| lo.contains(t))
        })
        .collect()
}

fn classify_file(
    p: Option<&Project>,
    m: &mut Materiality,
    path: &str,
    before: Option<&str>,
    after: Option<&str>,
) {
    // a governed record written as a file is classified as the record it is
    let rec_after = after.and_then(|t| parse_record_text(t, path));
    let rec_before = before.and_then(|t| parse_record_text(t, path));
    if let Some(r) = rec_after.as_ref().or(rec_before.as_ref()) {
        if !r.id().is_empty() && !r.rtype().is_empty() {
            classify_record(
                m,
                &r.id(),
                &r.rtype(),
                &[],
                rec_before.as_ref().map(|x| &x.data),
                rec_after.as_ref().map(|x| &x.data),
            );
        }
    }
    let what = match (before.is_some(), after.is_some()) {
        (false, true) => "created",
        (true, false) => "removed",
        _ => "modified",
    };
    let lower = path.to_lowercase();
    if (glob_match("governance/**", path) && !glob_match("governance/generated/**", path))
        || glob_match("framework/**", path)
        || any_glob(GOVERNANCE_FILES, path).is_some()
    {
        m.push(
            "governance_change",
            path,
            "governance path",
            format!("{path} {what}"),
            true,
        );
    }
    if let Some(g) = any_glob(ARCHITECTURE_PATHS, path) {
        m.push(
            "architecture_change",
            path,
            "architecture path",
            format!("{path} {what} (matches {g})"),
            true,
        );
    }
    if let Some(g) = any_glob(INTERFACE_PATHS, path) {
        m.push(
            "interface_change",
            path,
            "interface contract path",
            format!("{path} {what} (matches {g})"),
            true,
        );
    }
    // executable acceptance criteria (Gherkin feature files)
    if lower.ends_with(".feature") {
        m.push(
            "acceptance_criteria_change",
            path,
            "executable acceptance criteria",
            format!("{path} {what} (Gherkin feature file)"),
            true,
        );
    }
    // infrastructure recognised by content wherever it lives (Terraform resources, Kubernetes/Helm manifests)
    let infra_by_content = after
        .or(before)
        .map(|t| {
            t.lines().any(|l| {
                let l = l.trim_start();
                l.starts_with("resource \"") || l.starts_with("module \"")
            }) || (t.contains("apiVersion:") && t.contains("kind:"))
        })
        .unwrap_or(false);
    let infra_glob = any_glob(INFRA_PATHS, path).or(if infra_by_content {
        Some(
            "infrastructure definition by content (Terraform resource/module, Kubernetes manifest)",
        )
    } else {
        None
    });
    if let Some(g) = infra_glob {
        let sizing = match (before, after) {
            (Some(b), Some(a)) => {
                let lb = lines_with(b, SIZING_TOKENS);
                let la = lines_with(a, SIZING_TOKENS);
                lb.symmetric_difference(&la)
                    .map(|s| s.to_string())
                    .collect::<Vec<_>>()
            }
            _ => vec![],
        };
        m.push(
            "infrastructure_cost",
            path,
            "infrastructure definition",
            if sizing.is_empty() {
                format!("{path} {what} (matches {g})")
            } else {
                format!("{path}: sizing changed: {}", sizing.join(" | "))
            },
            true,
        );
    }
    let sql_text = after.or(before).unwrap_or("").to_lowercase();
    let is_sql = lower.ends_with(".sql");
    let sql_ops: Vec<&str> = SQL_CHANGE
        .iter()
        .copied()
        .filter(|k| sql_text.contains(k))
        .collect();
    if any_glob(MIGRATION_PATHS, path).is_some() || (is_sql && !sql_ops.is_empty()) {
        let destructive: Vec<&str> = SQL_DESTRUCTIVE
            .iter()
            .copied()
            .filter(|k| sql_text.contains(k))
            .collect();
        m.push(
            "data_migration",
            path,
            "data migration",
            if destructive.is_empty() {
                format!("{path} {what}; SQL operations: {sql_ops:?}")
            } else {
                format!("{path} {what}; DESTRUCTIVE SQL: {destructive:?}")
            },
            true,
        );
    }
    let segs = tokens(path);
    if let Some(s) = segs
        .iter()
        .find(|s| SECURITY_SEGMENTS.contains(&s.as_str()))
    {
        m.push(
            "security_change",
            path,
            "security path",
            format!("{path} {what} (path names '{s}')"),
            true,
        );
    }
    if let Some(b) = before {
        let lb = lines_with(b, SECURITY_TOKENS);
        let la = after
            .map(|a| lines_with(a, SECURITY_TOKENS))
            .unwrap_or_default();
        let removed: Vec<&&str> = lb.difference(&la).collect();
        if !removed.is_empty() {
            m.push(
                "security_change",
                path,
                "security check removed or changed",
                format!(
                    "{path}: security-relevant line(s) removed or changed: {}",
                    removed
                        .iter()
                        .map(|s| s.to_string())
                        .collect::<Vec<_>>()
                        .join(" | ")
                ),
                true,
            );
        }
    }
    if let Some(p) = p {
        let class = p.contract().decide(path).class();
        if class == "source" {
            m.push(
                "behaviour_change",
                path,
                "product source",
                format!("{path} {what} (repository contract class source)"),
                false,
            );
        }
    }
}

/// Classify a change set.
pub fn classify(p: Option<&Project>, changes: &[Change]) -> Materiality {
    let mut m = Materiality::default();
    for c in changes {
        match c {
            Change::Record {
                id,
                rtype,
                path,
                fields,
                before,
                after,
            } => {
                classify_record(&mut m, id, rtype, fields, before.as_ref(), after.as_ref());
                // the record's location also classifies it (governance overlay records, architecture docs, …)
                classify_path_only(p, &mut m, path, before.is_some(), after.is_some());
            }
            Change::File {
                path,
                before,
                after,
            } => classify_file(p, &mut m, path, before.as_deref(), after.as_deref()),
        }
    }
    m
}

fn classify_path_only(
    p: Option<&Project>,
    m: &mut Materiality,
    path: &str,
    existed: bool,
    exists: bool,
) {
    if path.is_empty() {
        return;
    }
    let what = match (existed, exists) {
        (false, true) => "created",
        (true, false) => "removed",
        _ => "modified",
    };
    if (glob_match("governance/**", path) && !glob_match("governance/generated/**", path))
        || any_glob(GOVERNANCE_FILES, path).is_some()
    {
        m.push(
            "governance_change",
            path,
            "governance path",
            format!("{path} {what}"),
            true,
        );
    }
    let _ = p;
}

fn read_opt(p: &Project, rel: &str) -> Option<String> {
    std::fs::read_to_string(p.root.join(rel)).ok()
}

/// The changes a CIT's mutation manifest would make, as they stand in the repository now.
pub fn changes_of_manifest(p: &Project, store: &RecordStore, cit: &Value) -> Vec<Change> {
    let mut out = vec![];
    for op in cit["mutation_manifest"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        let kind = op["op"].as_str().unwrap_or("");
        match kind {
            "set_field" | "set_status" => {
                let target = op["target"].as_str().unwrap_or("");
                let Some(r) = store.get(target) else {
                    continue;
                };
                let field = if kind == "set_status" {
                    "status".to_string()
                } else {
                    op["field"]
                        .as_str()
                        .unwrap_or("")
                        .split('.')
                        .next()
                        .unwrap_or("")
                        .to_string()
                };
                let mut after = r.data.clone();
                if kind == "set_status" {
                    after["status"] = op["value"].clone();
                } else if let Some(f) = op["field"].as_str() {
                    if f.contains('.') {
                        crate::util::deep_set(&mut after, f, op["value"].clone());
                    } else {
                        after[f] = op["value"].clone();
                    }
                }
                out.push(Change::Record {
                    id: r.id(),
                    rtype: r.rtype(),
                    path: r.path.clone(),
                    fields: vec![field],
                    before: Some(r.data.clone()),
                    after: Some(after),
                });
            }
            "write_file" => {
                let path = op["path"].as_str().unwrap_or("").to_string();
                out.push(Change::File {
                    before: read_opt(p, &path),
                    after: op["content"].as_str().map(String::from),
                    path,
                });
            }
            "delete_file" => {
                let path = op["path"].as_str().unwrap_or("").to_string();
                out.push(Change::File {
                    before: read_opt(p, &path),
                    after: None,
                    path,
                });
            }
            "move_file" => {
                // a move keeps the content: the locations it leaves and enters are what may be material, and a
                // non-record file moved is removed at one path and created at the other
                let from = op["path"].as_str().unwrap_or("").to_string();
                let to = op["to"].as_str().unwrap_or("").to_string();
                let text = read_opt(p, &from);
                let is_record = text
                    .as_deref()
                    .and_then(|t| parse_record_text(t, &from))
                    .is_some();
                if is_record {
                    for path in [from, to] {
                        out.push(Change::Record {
                            id: String::new(),
                            rtype: String::new(),
                            path,
                            fields: vec![],
                            before: None,
                            after: None,
                        });
                    }
                } else {
                    out.push(Change::File {
                        path: from,
                        before: text.clone(),
                        after: None,
                    });
                    out.push(Change::File {
                        path: to,
                        before: None,
                        after: text,
                    });
                }
            }
            "append_record" => {
                let rec = op["record"].clone();
                let id = rec["id"].as_str().unwrap_or("").to_string();
                let rtype = rec["type"].as_str().unwrap_or("").to_string();
                let path = op["path"].as_str().map(String::from).unwrap_or_else(|| {
                    crate::records::TYPE_DIR
                        .iter()
                        .find(|(t, _)| *t == rtype)
                        .map(|(_, d)| format!("{d}/{id}.yaml"))
                        .unwrap_or_default()
                });
                let before = store.get(&id).map(|r| r.data.clone());
                out.push(Change::Record {
                    id,
                    rtype,
                    path,
                    fields: vec![],
                    before,
                    after: Some(rec),
                });
            }
            "set_lock_field" => out.push(Change::File {
                path: "governance/framework.lock".into(),
                before: read_opt(p, "governance/framework.lock"),
                after: Some(String::new()),
            }),
            _ => {}
        }
    }
    // Declared targets that are repository paths (not record ids) and that no manifest op already covers: what the
    // CIT says it touches is classified by location even when it carries no manifest (content not stated, so only
    // the path-based rules can fire). A path escaping the root is classified by name only and never read.
    let covered: std::collections::BTreeSet<String> = out
        .iter()
        .map(|c| match c {
            Change::Record { path, .. } | Change::File { path, .. } => path.clone(),
        })
        .collect();
    for t in cit["targets"].as_array().cloned().unwrap_or_default() {
        let Some(t) = t.as_str().map(|s| s.trim().to_string()) else {
            continue;
        };
        if t.is_empty() || store.get(&t).is_some() || covered.contains(&t) {
            continue;
        }
        if !(t.contains('/') || t.contains('.')) {
            continue;
        }
        let escapes = t.starts_with('/') || t.split('/').any(|seg| seg == "..");
        let now = if escapes { None } else { read_opt(p, &t) };
        out.push(Change::File {
            path: t,
            before: now.clone(),
            after: now,
        });
    }
    out
}

/// The materiality of a CIT's manifest.
pub fn classify_manifest(p: &Project, store: &RecordStore, cit: &Value) -> Materiality {
    classify(Some(p), &changes_of_manifest(p, store, cit))
}

/// `git <args>` in `root` with its stdout **untrimmed** (`Project::git` trims, which corrupts porcelain status lines
/// and file contents). `None` when git fails.
pub fn git_output(root: &std::path::Path, args: &[&str]) -> Option<String> {
    let o = std::process::Command::new("git")
        .args(args)
        .current_dir(root)
        .output()
        .ok()?;
    if !o.status.success() {
        return None;
    }
    Some(String::from_utf8_lossy(&o.stdout).to_string())
}

/// **The materiality of changes already performed in the working tree** (the in-task detection API; integration
/// point for `orchestration::tasks::close`, WS-5): each path's content at `base` (a commit; `None` = `HEAD`)
/// against its content now. Returns the findings; `requiring_cit()` lists those that must not close outside a CIT.
pub fn classify_paths(p: &Project, paths: &[String], base: Option<&str>) -> Materiality {
    let base = base.unwrap_or("HEAD");
    let mut changes = vec![];
    for rel in paths {
        let before = git_output(&p.root, &["show", &format!("{base}:{rel}")]);
        let after = read_opt(p, rel);
        if before == after {
            continue;
        }
        changes.push(Change::File {
            path: rel.clone(),
            before,
            after,
        });
    }
    classify(Some(p), &changes)
}

/// Kernel radius floor of a material class under `CHANGE_POLICY.radius_rules` (framework §49).
pub fn radius_floor(p: &Project, class: &str) -> String {
    let pol = p.policies();
    match class {
        "governance_change" => pol.get_str(
            "CHANGE_POLICY",
            "radius_rules.governance_paths_radius",
            "R5",
        ),
        "architecture_change" => {
            let r = pol.get_str(
                "CHANGE_POLICY",
                "radius_rules.interface_or_behaviour_radius",
                "R2",
            );
            // an architecture change is at least subsystem-wide (framework §49 R3)
            if r.trim_start_matches('R').parse::<u8>().unwrap_or(2) < 3 {
                "R3".into()
            } else {
                r
            }
        }
        "interface_change" | "behaviour_change" | "security_change" => pol.get_str(
            "CHANGE_POLICY",
            "radius_rules.interface_or_behaviour_radius",
            "R2",
        ),
        "editorial" => pol.get_str("CHANGE_POLICY", "radius_rules.editorial_radius", "R0"),
        _ => pol.get_str("CHANGE_POLICY", "radius_rules.single_artifact_radius", "R1"),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn rec(id: &str, rtype: &str, fields: &[&str], before: Value, after: Value) -> Change {
        Change::Record {
            id: id.into(),
            rtype: rtype.into(),
            path: format!("spec/x/{id}.yaml"),
            fields: fields.iter().map(|s| s.to_string()).collect(),
            before: Some(before),
            after: Some(after),
        }
    }
    fn file(path: &str, before: Option<&str>, after: Option<&str>) -> Change {
        Change::File {
            path: path.into(),
            before: before.map(String::from),
            after: after.map(String::from),
        }
    }

    #[test]
    fn each_material_class_is_derived_from_what_changes_not_from_a_label() {
        let cases: Vec<(Change, &str)> = vec![
            (
                rec(
                    "ARCH-0001",
                    "architecture",
                    &["summary"],
                    json!({"summary": "REST"}),
                    json!({"summary": "event bus"}),
                ),
                "architecture_change",
            ),
            (
                rec(
                    "API-0001",
                    "interface",
                    &["summary"],
                    json!({}),
                    json!({"summary": "v2"}),
                ),
                "interface_change",
            ),
            (
                rec(
                    "SCN-0001",
                    "scenario",
                    &["success_criteria"],
                    json!({}),
                    json!({"success_criteria": ["p95 < 20 s"]}),
                ),
                "acceptance_criteria_change",
            ),
            (
                rec(
                    "REQ-0001",
                    "requirement",
                    &["statement"],
                    json!({}),
                    json!({"statement": "x"}),
                ),
                "behaviour_change",
            ),
            (
                file(
                    "product/auth.py",
                    Some("def authorise(t):\n    return verify_signature(t)\n"),
                    Some("def authorise(t):\n    return True\n"),
                ),
                "security_change",
            ),
            (
                file(
                    "infra/main.tf",
                    Some("resource \"db\" { instance_class = \"small\" }\n"),
                    Some("resource \"db\" { instance_class = \"8xlarge\" }\n"),
                ),
                "infrastructure_cost",
            ),
            (
                file(
                    "product/migrations/002.sql",
                    None,
                    Some("ALTER TABLE customer DROP COLUMN legacy;\n"),
                ),
                "data_migration",
            ),
            (
                file("governance/project/NOTES.md", None, Some("x\n")),
                "governance_change",
            ),
            (
                file(
                    "tests/features/checkout.feature",
                    Some("Then total is 398\n"),
                    Some("Then total is 400\n"),
                ),
                "acceptance_criteria_change",
            ),
            (
                file(
                    "ops/cluster.yaml",
                    None,
                    Some("apiVersion: apps/v1\nkind: Deployment\nspec:\n  replicas: 40\n"),
                ),
                "infrastructure_cost",
            ),
            (
                file(
                    "platform/db.hcl",
                    Some("resource \"aws_db_instance\" \"x\" { instance_class = \"small\" }\n"),
                    Some("resource \"aws_db_instance\" \"x\" { instance_class = \"8xlarge\" }\n"),
                ),
                "infrastructure_cost",
            ),
        ];
        for (c, want) in cases {
            let m = classify(None, &[c.clone()]);
            assert!(m.classes().contains(&want), "{c:?} -> {:?}", m.classes());
            assert_eq!(m.effective_trigger("editorial"), m.classes()[0]);
            assert!(m.to_value("editorial")["label_understates"]
                .as_bool()
                .unwrap());
        }
    }

    #[test]
    fn bookkeeping_and_editorial_changes_are_not_material() {
        let m = classify(
            None,
            &[rec(
                "REQ-0001",
                "requirement",
                &["staleness", "updated"],
                json!({}),
                json!({"staleness": {"stale": true}}),
            )],
        );
        assert!(!m.material(), "{:?}", m.findings);
        // planning attributes of a requirement (order, owner, provenance) do not specify behaviour ...
        let m = classify(
            None,
            &[rec(
                "REQ-0001",
                "requirement",
                &["priority"],
                json!({"priority": "low"}),
                json!({"priority": "high"}),
            )],
        );
        assert!(!m.material(), "{:?}", m.findings);
        // ... but the same change together with the statement does
        let m = classify(
            None,
            &[rec(
                "REQ-0001",
                "requirement",
                &["priority", "statement"],
                json!({"priority": "low", "statement": "a"}),
                json!({"priority": "high", "statement": "b"}),
            )],
        );
        assert_eq!(m.classes(), vec!["behaviour_change"]);
        let m = classify(None, &[file("docs/guide.md", Some("a"), Some("b"))]);
        assert!(!m.material(), "{:?}", m.findings);
        let m = classify(None, &[file("infra/main.tf", Some("x"), Some("y"))]);
        assert_eq!(m.classes(), vec!["infrastructure_cost"]);
        assert!(m.requiring_cit().len() == 1);
    }

    #[test]
    fn the_declared_label_is_kept_but_never_lowers_the_derived_classes() {
        let m = classify(None, &[file("governance/project/X.md", None, Some("x"))]);
        assert_eq!(m.effective_trigger("behaviour_change"), "governance_change");
        let none = Materiality::default();
        assert_eq!(none.effective_trigger("security_change"), "security_change");
        assert_eq!(none.effective_triggers("editorial"), Vec::<String>::new());
    }

    #[test]
    fn declared_path_targets_are_classified_without_a_manifest() {
        let root =
            std::env::temp_dir().join(format!("gov-ws04r2-tgt-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(root.join("governance/project")).unwrap();
        std::fs::write(
            root.join("governance/project/PROJECT_POLICY.yaml"),
            "x: 1\n",
        )
        .unwrap();
        let p = Project::open(&root);
        let store = RecordStore::load(&root);
        let cit = json!({"targets": ["governance/project/PROJECT_POLICY.yaml", "REQ-9999", "../outside/secrets/x.pem"],
                         "mutation_manifest": []});
        let m = classify_manifest(&p, &store, &cit);
        let classes = m.classes();
        assert!(classes.contains(&"governance_change"), "{classes:?}");
        // a path escaping the root is classified by name only (never read) and a bare id is not a path
        assert!(classes.contains(&"security_change"), "{classes:?}");
        assert!(m.findings.iter().all(|f| f.subject != "REQ-9999"));
        // a target a manifest op already covers is not classified twice
        let cit2 = json!({"targets": ["governance/project/PROJECT_POLICY.yaml"],
                          "mutation_manifest": [{"op": "write_file", "path": "governance/project/PROJECT_POLICY.yaml", "content": "x: 2\n"}]});
        let n = classify_manifest(&p, &store, &cit2)
            .findings
            .iter()
            .filter(|f| f.class == "governance_change")
            .count();
        assert_eq!(n, 1);
        let _ = std::fs::remove_dir_all(&root);
    }
}
