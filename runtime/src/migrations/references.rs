//! References between repository artefacts: code imports, document citations (markdown/reference-style/HTML links
//! and plain path mentions) and path references from code and configuration.
//!
//! Two consumers:
//! * the adoption path map — B2 "Imports/references/citations/consumers are represented" (Contract v3:194,
//!   BC-P2-52): every catalogue entry lists what it imports, cites and references and who consumes it;
//! * the **dependency proof** that must precede any retirement — R1 "verify no active dependency remains", R2
//!   "dependency proof before retirement" (Contract v3:879, :884; framework §69 "validate no active dependency
//!   remains", §70 "prove no active functionality depends on it"; BC-P2-33). The proof is computed from a fresh scan
//!   of the working tree at the moment it is relied on, over code, configuration and docs, and is deliberately
//!   conservative: a bare file-name mention counts, because a proof of absence that misses a reference is worse
//!   than a gate that asks one question too many.
use super::ownership::OsState;
use crate::util::{is_text_file, read_text, sha256_text};
use regex::Regex;
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::path::Path;
use std::sync::OnceLock;

/// Files larger than this are not scanned for references (recorded in the proof as `skipped_large`).
pub const MAX_SCAN_BYTES: u64 = 1_048_576;

/// Files whose mention of a path is an exclusion or ownership rule, not a dependency on the file.
pub const NON_DEPENDENCY_FILES: &[&str] = &[
    ".gitignore",
    ".gitattributes",
    ".dockerignore",
    ".npmignore",
    ".eslintignore",
    ".prettierignore",
    ".helmignore",
    ".slugignore",
    "CODEOWNERS",
];

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash, serde::Serialize)]
pub struct RefEdge {
    pub from: String,
    pub to: String,
    /// `import` | `citation` | `path_reference`
    pub kind: String,
    /// how `to` was resolved: `import` | `link` | `exact` | `relative` | `basename`
    pub resolution: String,
    /// 1-based line in `from` (0 when the analyser reports none)
    pub line: usize,
    /// role of `from` in a dependency proof: `code` | `config` | `docs`
    pub role: String,
}

impl RefEdge {
    pub fn to_value(&self) -> Value {
        json!({"from": self.from, "to": self.to, "kind": self.kind, "resolution": self.resolution, "line": self.line, "role": self.role})
    }
}

/// A file as the scanner sees it: repository path and inventory kinds.
#[derive(Debug, Clone)]
pub struct ScanFile {
    pub rel: String,
    pub kinds: Vec<String>,
}

#[derive(Debug, Clone, Default)]
pub struct ReferenceIndex {
    pub edges: Vec<RefEdge>,
    /// basename -> (from, line, role) for tokens naming a file by its bare file name only
    pub basename_mentions: HashMap<String, Vec<(String, usize, String)>>,
    pub paths: BTreeSet<String>,
    pub scanned: usize,
    pub skipped_large: Vec<String>,
}

/// Role of a file in a dependency proof.
pub fn role_of(rel: &str, kinds: &[String]) -> &'static str {
    let has = |k: &str| kinds.iter().any(|x| x == k);
    if has("source") || has("test") || has("entrypoint") {
        "code"
    } else if rel.starts_with("spec/")
        || has("doc")
        || has("spec_doc")
        || has("report")
        || has("research")
    {
        "docs"
    } else {
        "config"
    }
}

fn doc_like(rel: &str, kinds: &[String]) -> bool {
    let ext = Path::new(rel)
        .extension()
        .map(|e| e.to_string_lossy().to_lowercase())
        .unwrap_or_default();
    matches!(
        ext.as_str(),
        "md" | "markdown" | "rst" | "adoc" | "txt" | "html" | "htm"
    ) || kinds.iter().any(|k| k == "doc")
}

fn link_rx() -> &'static [Regex] {
    static R: OnceLock<Vec<Regex>> = OnceLock::new();
    R.get_or_init(|| {
        vec![
            // [text](target "title")
            Regex::new(r#"\]\(\s*<?([^)\s>]+)>?(?:\s+["'][^)]*["'])?\s*\)"#).unwrap(),
            // [ref]: target
            Regex::new(r"^\s{0,3}\[[^\]]+\]:\s*<?([^\s>]+)>?").unwrap(),
            // href="target" / src="target"
            Regex::new(r#"(?i)(?:href|src)\s*=\s*["']([^"']+)["']"#).unwrap(),
            // rst `text <target>`_
            Regex::new(r"`[^`<]*<([^>`]+)>`_").unwrap(),
        ]
    })
}

/// A line that *declares provenance* ("this record was extracted from X") rather than depending on X.
fn provenance_rx() -> &'static Regex {
    static R: OnceLock<Regex> = OnceLock::new();
    R.get_or_init(|| {
        Regex::new(r#"^\s*-?\s*["']?(legacy_source|extracted_from|provenance_source|migrated_from_path)["']?\s*:"#)
            .unwrap()
    })
}

/// Governed records that record events or evidence (checkpoints, audits, reports, change transactions, handoffs,
/// gates, legacy registrations): the paths they mention are history, not dependencies.
pub const EVENT_RECORD_TYPES: &[&str] = &[
    "checkpoint",
    "audit",
    "report",
    "cit",
    "handoff",
    "human-gate",
    "legacy",
];

fn event_record(rel: &str, text: &str) -> bool {
    if !(rel.ends_with(".yaml") || rel.ends_with(".yml")) {
        return false;
    }
    static R: OnceLock<Regex> = OnceLock::new();
    let rx = R.get_or_init(|| Regex::new(r#"(?m)^type:\s*["']?([A-Za-z-]+)["']?\s*$"#).unwrap());
    static G: OnceLock<Regex> = OnceLock::new();
    // the decision `gov decide` mints from a gate answer records that answer (it quotes the gate's question)
    let gate_answer = G.get_or_init(|| {
        Regex::new(r#"(?m)^derived_from:\s*(?:\[\s*["']?HDG-|\n\s*-\s*["']?HDG-)"#).unwrap()
    });
    rx.captures(text)
        .map(|c| EVENT_RECORD_TYPES.contains(&&c[1]))
        .unwrap_or(false)
        || gate_answer.is_match(text)
}

fn token_rx() -> &'static Regex {
    static R: OnceLock<Regex> = OnceLock::new();
    R.get_or_init(|| Regex::new(r"[A-Za-z0-9_./\-]+").unwrap())
}

pub fn normalize_rel(p: &str) -> String {
    let mut out: Vec<&str> = vec![];
    for seg in p.split('/') {
        match seg {
            "" | "." => {}
            ".." => {
                if out.pop().is_none() {
                    return String::new();
                }
            }
            s => out.push(s),
        }
    }
    out.join("/")
}

fn dir_of(rel: &str) -> String {
    Path::new(rel)
        .parent()
        .map(|d| d.to_string_lossy().replace('\\', "/"))
        .unwrap_or_default()
}

fn percent_decode(s: &str) -> String {
    let b = s.as_bytes();
    let mut out = Vec::with_capacity(b.len());
    let mut i = 0;
    while i < b.len() {
        if b[i] == b'%' && i + 2 < b.len() {
            if let Ok(v) = u8::from_str_radix(&s[i + 1..i + 3], 16) {
                out.push(v);
                i += 3;
                continue;
            }
        }
        out.push(b[i]);
        i += 1;
    }
    String::from_utf8_lossy(&out).to_string()
}

/// Resolve a link target written in `from` to a repository path, if it is a local path.
fn resolve_link(from: &str, target: &str) -> Option<String> {
    let t = target.trim();
    if t.is_empty()
        || t.starts_with('#')
        || t.contains("://")
        || t.starts_with("mailto:")
        || t.starts_with("data:")
    {
        return None;
    }
    let t = t.split(['#', '?']).next().unwrap_or("");
    let t = percent_decode(t);
    let p = if let Some(abs) = t.strip_prefix('/') {
        normalize_rel(abs)
    } else {
        let d = dir_of(from);
        normalize_rel(&if d.is_empty() { t } else { format!("{d}/{t}") })
    };
    if p.is_empty() {
        None
    } else {
        Some(p)
    }
}

/// A bare file name that is specific enough to count as naming a file (has an extension or a leading dot).
fn is_specific_basename(t: &str) -> bool {
    !t.contains('/') && t.len() >= 5 && t.contains('.') && !t.ends_with('.') && {
        let stem_ok = t.trim_start_matches('.').chars().any(|c| c.is_alphabetic());
        stem_ok
    }
}

/// Build the reference index over `files`. `with_imports` adds code-import edges from the code analyser.
pub fn build(root: &Path, files: &[ScanFile], with_imports: bool) -> ReferenceIndex {
    build_with_ghosts(root, files, with_imports, &[])
}

/// As [`build`], also resolving references to `ghosts`: paths that no longer exist (retired material) but that a
/// reference may still name, so a dangling reference is found by its full path, not only by its file name.
pub fn build_with_ghosts(
    root: &Path,
    files: &[ScanFile],
    with_imports: bool,
    ghosts: &[String],
) -> ReferenceIndex {
    let mut paths: BTreeSet<String> = files.iter().map(|f| f.rel.clone()).collect();
    paths.extend(ghosts.iter().filter(|g| !g.is_empty()).cloned());
    let mut by_basename: HashMap<String, Vec<String>> = HashMap::new();
    for p in &paths {
        let b = p.rsplit('/').next().unwrap_or(p).to_string();
        by_basename.entry(b).or_default().push(p.clone());
    }
    let mut idx = ReferenceIndex {
        paths: paths.clone(),
        ..Default::default()
    };
    let mut seen: BTreeMap<(String, String, String), RefEdge> = BTreeMap::new();
    let mut push = |e: RefEdge| {
        let k = (e.from.clone(), e.to.clone(), e.kind.clone());
        match seen.get(&k) {
            Some(old) if old.line != 0 && (old.line <= e.line || e.line == 0) => {}
            _ => {
                seen.insert(k, e);
            }
        }
    };
    for f in files {
        let abs = root.join(&f.rel);
        let Ok(meta) = abs.metadata() else { continue };
        if !meta.is_file() {
            continue;
        }
        if meta.len() > MAX_SCAN_BYTES {
            idx.skipped_large.push(f.rel.clone());
            continue;
        }
        if f.kinds.iter().any(|k| k == "binary") || !is_text_file(&abs) {
            continue;
        }
        let Ok(text) = read_text(&abs) else { continue };
        idx.scanned += 1;
        let evidence = event_record(&f.rel, &text);
        let role = role_of(&f.rel, &f.kinds).to_string();
        let docs = doc_like(&f.rel, &f.kinds);
        let dir = dir_of(&f.rel);
        for (i, line) in text.lines().enumerate() {
            let ln = i + 1;
            // provenance declarations are relations (kept in the path map) but never dependencies
            let line_role = if evidence || provenance_rx().is_match(line) {
                "provenance".to_string()
            } else {
                role.clone()
            };
            if docs {
                for rx in link_rx() {
                    for c in rx.captures_iter(line) {
                        if let Some(to) = resolve_link(&f.rel, &c[1]) {
                            if paths.contains(&to) && to != f.rel {
                                push(RefEdge {
                                    from: f.rel.clone(),
                                    to,
                                    kind: "citation".into(),
                                    resolution: "link".into(),
                                    line: ln,
                                    role: role.clone(),
                                });
                            }
                        }
                    }
                }
            }
            for m in token_rx().find_iter(line) {
                let t = m.as_str().trim_end_matches(['.', ',', ':', ';', '-']);
                if t.len() < 3 || !(t.contains('.') || t.contains('/')) {
                    continue;
                }
                let kind = if line_role == "provenance" {
                    "provenance"
                } else if role == "docs" {
                    "citation"
                } else {
                    "path_reference"
                };
                let mut cands: Vec<(String, &str)> = vec![];
                if let Some(abs_t) = t.strip_prefix('/') {
                    cands.push((normalize_rel(abs_t), "exact"));
                } else {
                    cands.push((normalize_rel(t), "exact"));
                    if !dir.is_empty() {
                        cands.push((normalize_rel(&format!("{dir}/{t}")), "relative"));
                    }
                }
                let mut hit = false;
                for (c, res) in cands {
                    if !c.is_empty() && paths.contains(&c) && c != f.rel {
                        push(RefEdge {
                            from: f.rel.clone(),
                            to: c,
                            kind: kind.into(),
                            resolution: res.into(),
                            line: ln,
                            role: line_role.clone(),
                        });
                        hit = true;
                        break;
                    }
                }
                if !hit && is_specific_basename(t) {
                    if let Some(targets) = by_basename.get(t) {
                        idx.basename_mentions
                            .entry(t.to_string())
                            .or_default()
                            .push((f.rel.clone(), ln, line_role.clone()));
                        // a bare name never resolves into the archive: archived material is not addressed
                        // by file name from the active tree, and a dangling name must not look re-pointed
                        if targets.len() == 1
                            && targets[0] != f.rel
                            && !targets[0].starts_with("archive/")
                        {
                            push(RefEdge {
                                from: f.rel.clone(),
                                to: targets[0].clone(),
                                kind: kind.into(),
                                resolution: "basename".into(),
                                line: ln,
                                role: line_role.clone(),
                            });
                        }
                    }
                }
            }
        }
    }
    if with_imports {
        let items: Vec<Value> = files
            .iter()
            .map(|f| json!({"path": f.rel, "kinds": f.kinds}))
            .collect();
        for (from, to) in super::classify::import_edges(root, &items) {
            let role = files
                .iter()
                .find(|f| f.rel == from)
                .map(|f| role_of(&f.rel, &f.kinds))
                .unwrap_or("code");
            push(RefEdge {
                from,
                to,
                kind: "import".into(),
                resolution: "import".into(),
                line: 0,
                role: role.into(),
            });
        }
    }
    idx.edges = seen.into_values().collect();
    idx
}

/// Scan the current working tree (fresh; nothing cached), as a dependency proof requires.
pub fn build_fresh(root: &Path) -> ReferenceIndex {
    build_fresh_with_ghosts(root, &[])
}

/// [`build_fresh`] that also resolves references to retired paths (`ghosts`).
pub fn build_fresh_with_ghosts(root: &Path, ghosts: &[String]) -> ReferenceIndex {
    let files: Vec<ScanFile> = crate::paths::iter_repo_files(root, false)
        .into_iter()
        .filter(|(_, rel)| !rel.starts_with(".git/"))
        .map(|(abs, rel)| ScanFile {
            kinds: super::inventory::detect_kinds(&rel, &abs)
                .into_iter()
                .map(|k| k.to_string())
                .collect(),
            rel,
        })
        .collect();
    build_with_ghosts(root, &files, true, ghosts)
}

/// Which files count as *active* for a dependency proof: the working tree minus the archive, the Governance OS's own
/// state (kernel, overlay, generated outputs, adoption evidence), files that are themselves leaving the active tree
/// in the same plan, and ignore/ownership files whose mention of a path is not a dependency on it.
pub struct ActiveSet<'a> {
    pub root: &'a Path,
    pub os: &'a OsState,
    pub archive_root: String,
    pub leaving: BTreeSet<String>,
}

impl ActiveSet<'_> {
    pub fn is_active(&self, rel: &str) -> bool {
        let name = rel.rsplit('/').next().unwrap_or(rel);
        !(rel.starts_with(&format!("{}/", self.archive_root.trim_end_matches('/')))
            || rel.starts_with(".git/")
            || self.leaving.contains(rel)
            || NON_DEPENDENCY_FILES.contains(&name)
            || self.os.owns(self.root, rel))
    }
}

impl ReferenceIndex {
    /// Every reference to one of `subjects` made from an active file (resolved edges plus bare file-name mentions).
    pub fn active_references_to(&self, subjects: &[String], active: &ActiveSet) -> Vec<RefEdge> {
        self.active_references(subjects, &[], active)
    }

    /// References from active files to `named` (resolved edges and bare file-name mentions) and to `explicit`
    /// (resolved edges only — used for archive locations, which share the retired file's bare name).
    pub fn active_references(
        &self,
        named: &[String],
        explicit: &[String],
        active: &ActiveSet,
    ) -> Vec<RefEdge> {
        let mut out: BTreeMap<(String, usize, String), RefEdge> = BTreeMap::new();
        let all: Vec<String> = named.iter().chain(explicit.iter()).cloned().collect();
        for e in &self.edges {
            let explicit_ok = e.resolution != "basename" || named.contains(&e.to);
            if e.kind == "provenance" {
                continue;
            }
            if all.contains(&e.to)
                && explicit_ok
                && !all.contains(&e.from)
                && active.is_active(&e.from)
            {
                out.insert((e.from.clone(), e.line, e.to.clone()), e.clone());
            }
        }
        let subjects = named;
        for s in subjects {
            let b = s.rsplit('/').next().unwrap_or(s);
            if !is_specific_basename(b) {
                continue;
            }
            for (from, line, role) in self.basename_mentions.get(b).cloned().unwrap_or_default() {
                if all.contains(&from) || !active.is_active(&from) || role == "provenance" {
                    continue;
                }
                if out.keys().any(|(f, l, _)| f == &from && *l == line) {
                    continue;
                }
                out.entry((from.clone(), line, s.clone()))
                    .or_insert_with(|| RefEdge {
                        from: from.clone(),
                        to: s.clone(),
                        kind: if role == "docs" {
                            "citation".into()
                        } else {
                            "path_reference".into()
                        },
                        resolution: "basename".into(),
                        line,
                        role,
                    });
            }
        }
        out.into_values().collect()
    }

    /// Edges whose endpoints involve `path`, for the path-map representation of one artefact.
    pub fn path_map_fields(&self, path: &str) -> Value {
        let mut imports = BTreeSet::new();
        let mut citations = BTreeSet::new();
        let mut path_references = BTreeSet::new();
        let mut consumers = BTreeSet::new();
        let mut cited_by = BTreeSet::new();
        let mut detail = vec![];
        for e in &self.edges {
            if e.from == path {
                match e.kind.as_str() {
                    "import" => imports.insert(e.to.clone()),
                    "citation" | "provenance" => citations.insert(e.to.clone()),
                    _ => path_references.insert(e.to.clone()),
                };
                detail.push(json!({"path": e.to, "direction": "out", "kind": e.kind, "resolution": e.resolution, "line": e.line}));
            } else if e.to == path {
                consumers.insert(e.from.clone());
                if e.kind == "citation" {
                    cited_by.insert(e.from.clone());
                }
                detail.push(json!({"path": e.from, "direction": "in", "kind": e.kind, "resolution": e.resolution, "line": e.line}));
            }
        }
        let mut references: BTreeSet<String> = BTreeSet::new();
        for s in [&imports, &citations, &path_references, &consumers] {
            references.extend(s.iter().cloned());
        }
        json!({"imports": imports, "citations": citations, "path_references": path_references, "consumers": consumers,
            "cited_by": cited_by, "references": references, "reference_edges": detail})
    }
}

/// The dependency proof for retiring `subject` (and, when given, its archive `target`, so that nothing active was
/// re-pointed at the archived copy). Computed from `index`, which must be a fresh scan at the time of reliance.
pub fn dependency_proof(
    index: &ReferenceIndex,
    subject: &str,
    target: Option<&str>,
    active: &ActiveSet,
) -> Value {
    let named = vec![subject.to_string()];
    let explicit: Vec<String> = target
        .filter(|t| !t.is_empty())
        .map(|t| vec![t.to_string()])
        .unwrap_or_default();
    let refs = index.active_references(&named, &explicit, active);
    let mut by_role: BTreeMap<String, usize> = BTreeMap::new();
    for r in &refs {
        *by_role.entry(r.role.clone()).or_insert(0) += 1;
    }
    let dependants: BTreeSet<(String, String)> = refs
        .iter()
        .map(|r| (r.from.clone(), r.kind.clone()))
        .collect();
    let digest = sha256_text(
        &dependants
            .iter()
            .map(|(f, k)| format!("{f}\t{k}"))
            .collect::<Vec<_>>()
            .join("\n"),
    );
    json!({"subject": subject, "archive_target": target, "scope": ["code", "config", "docs"], "scanned_files": index.scanned,
        "skipped_large_files": index.skipped_large, "active_references": refs.iter().map(|r| r.to_value()).collect::<Vec<_>>(),
        "by_role": by_role, "result": if refs.is_empty() { "NO_ACTIVE_REFERENCES" } else { "ACTIVE_REFERENCES" },
        "dependants_digest": &digest[..16], "computed_at": crate::util::now_iso()})
}

pub fn proof_is_clean(proof: &Value) -> bool {
    proof["result"] == "NO_ACTIVE_REFERENCES"
}

#[cfg(test)]
mod tests {
    use super::*;

    fn files(root: &Path, spec: &[(&str, &str, &[&str])]) -> Vec<ScanFile> {
        spec.iter()
            .map(|(rel, text, kinds)| {
                let p = root.join(rel);
                std::fs::create_dir_all(p.parent().unwrap()).unwrap();
                std::fs::write(&p, text).unwrap();
                ScanFile {
                    rel: rel.to_string(),
                    kinds: kinds.iter().map(|k| k.to_string()).collect(),
                }
            })
            .collect()
    }

    fn tmp(name: &str) -> std::path::PathBuf {
        let d =
            std::env::temp_dir().join(format!("gov-refs-{name}-{}", uuid::Uuid::new_v4().simple()));
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    #[test]
    fn citations_links_and_path_references_are_found() {
        let root = tmp("cit");
        let fs = files(
            &root,
            &[
                (
                    "README.md",
                    "# x\nSee the [login spec](docs/spec-login.md) and AGENT_RULES.md.\n",
                    &["doc"],
                ),
                (
                    "docs/spec-login.md",
                    "# Login\n[back](../README.md)\n",
                    &["doc"],
                ),
                ("AGENT_RULES.md", "rules\n", &["doc"]),
                (
                    "src/loader.py",
                    "RULES = \".cursorrules\"\nDB = 'memory/chat.sqlite'\n",
                    &["source"],
                ),
                (".cursorrules", "x\n", &["provider_rules"]),
                ("memory/chat.sqlite", "not really sqlite\n", &["chat_store"]),
            ],
        );
        let idx = build(&root, &fs, false);
        let has = |f: &str, t: &str, k: &str| {
            idx.edges
                .iter()
                .any(|e| e.from == f && e.to == t && e.kind == k)
        };
        assert!(has("README.md", "docs/spec-login.md", "citation"));
        assert!(has("docs/spec-login.md", "README.md", "citation"));
        assert!(has("README.md", "AGENT_RULES.md", "citation"));
        assert!(has("src/loader.py", ".cursorrules", "path_reference"));
        assert!(has("src/loader.py", "memory/chat.sqlite", "path_reference"));
        let pm = idx.path_map_fields("docs/spec-login.md");
        assert!(pm["references"].to_string().contains("README.md"));
        assert!(pm["cited_by"].to_string().contains("README.md"));
        let pm = idx.path_map_fields("README.md");
        assert!(pm["citations"].to_string().contains("docs/spec-login.md"));
        assert!(pm["references"].to_string().contains("docs/spec-login.md"));
        let _ = std::fs::remove_dir_all(root);
    }

    #[test]
    fn a_dependency_proof_sees_live_code_and_ignores_archive_and_leaving_files() {
        let root = tmp("proof");
        let fs = files(
            &root,
            &[
                ("src/loader.py", "open('.cursorrules')\n", &["source"]),
                (
                    "OLD_RULES.md",
                    "follow .cursorrules\n",
                    &["doc", "provider_rules"],
                ),
                ("archive/x.md", ".cursorrules is archived\n", &["doc"]),
                (".gitignore", ".cursorrules\n", &["config"]),
                (".cursorrules", "x\n", &["provider_rules"]),
                (
                    "lib/util.js",
                    "require('./' + 'chat.sqlite')\n",
                    &["source"],
                ),
                ("memory/chat.sqlite", "x\n", &["chat_store"]),
            ],
        );
        let idx = build(&root, &fs, false);
        let os = OsState::default();
        let mut leaving = BTreeSet::new();
        leaving.insert("OLD_RULES.md".to_string());
        let act = ActiveSet {
            root: &root,
            os: &os,
            archive_root: "archive".into(),
            leaving,
        };
        let p = dependency_proof(
            &idx,
            ".cursorrules",
            Some("archive/governance/legacy-rules/.cursorrules"),
            &act,
        );
        assert_eq!(p["result"], "ACTIVE_REFERENCES");
        let froms: Vec<&str> = p["active_references"]
            .as_array()
            .unwrap()
            .iter()
            .map(|r| r["from"].as_str().unwrap())
            .collect();
        assert_eq!(froms, vec!["src/loader.py"], "{p}");
        // a bare file name counts (conservative)
        let p2 = dependency_proof(&idx, "memory/chat.sqlite", None, &act);
        assert_eq!(p2["result"], "ACTIVE_REFERENCES", "{p2}");
        let _ = std::fs::remove_dir_all(root);
    }
}
