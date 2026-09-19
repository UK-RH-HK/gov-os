//! Upstream learning pipeline and Export Gate (framework §75E-G, protocol §13-14, INV-012 fail closed).
use crate::records::{save_record, RecordStore};
use crate::util::{glob_match, hash_value, now_iso, read_json, write_json, write_yaml};
use crate::{GovError, Project, Result};
use regex::Regex;
use serde_json::{json, Value};
use std::path::Path;

fn redact_identifiers(text: &str, identifiers: &[String]) -> (String, usize) {
    let mut out = text.to_string();
    let mut n = 0;
    for id in identifiers {
        if id.len() < 3 {
            continue;
        }
        // an identifier written with spaces also appears hyphenated/underscored/joined (slugs, tags, categories)
        let tokens: Vec<String> = id
            .split([' ', '-', '_'])
            .filter(|t| !t.is_empty())
            .map(regex::escape)
            .collect();
        let pattern = if tokens.len() > 1 {
            format!("(?i){}", tokens.join("[\\s_-]*"))
        } else {
            format!("(?i){}", regex::escape(id))
        };
        let rx = Regex::new(&pattern).unwrap();
        let c = rx.find_iter(&out).count();
        if c > 0 {
            n += c;
            out = rx.replace_all(&out, "[REDACTED]").to_string();
        }
    }
    (out, n)
}

fn strip_paths(text: &str, forbidden: &[String]) -> (String, Vec<String>) {
    let rx = Regex::new(r"(?:/[\w.\-]+){2,}|(?:[\w.\-]+/){1,}[\w.\-]+\.[A-Za-z0-9]{1,6}").unwrap();
    let mut removed = vec![];
    let mut out = text.to_string();
    for m in rx.find_iter(text) {
        let s = m.as_str();
        if forbidden
            .iter()
            .any(|f| glob_match(f, s.trim_start_matches('/')))
            || s.starts_with('/')
        {
            removed.push(s.to_string());
        }
    }
    for r in &removed {
        out = out.replace(r, "[PATH-REMOVED]");
    }
    (out, removed)
}

fn code_lines(text: &str) -> usize {
    let mut n = 0;
    let mut in_fence = false;
    for l in text.lines() {
        if l.trim_start().starts_with("```") {
            in_fence = !in_fence;
            continue;
        }
        if in_fence {
            n += 1;
        }
    }
    n
}

pub fn outbound_dir(p: &Project) -> std::path::PathBuf {
    p.runtime_dir().join("outbound")
}

// ------------------------------------------------------------------------------------------ content controls
//
// BC-P2-50: the export gate fails closed on raw project content and index data **whatever their names or synthetic
// declaration** (Contract v3:861-866; release protocol §17 "any upstream operation that attempts to include a forbidden
// path/content class must fail closed"; framework §75E "raw code, product specs, customer data, project vector stores
// ... are prohibited by default", §75G "everything else is denied"). Path and file-name controls stay; these controls
// look at the bytes that would leave:
//
// * reproduction of repository content — fixture lines (and fenced code in lesson text) are compared with every line
//   of the project's tracked and untracked text files (the framework's own kernel, derived adapter output and the
//   lesson records being exported excluded); a whole-file copy, more than a policy-bounded number of reproduced
//   lines, one long reproduced line, or any line from a secret/never-export file blocks the export;
// * index data — chunk identifiers of the project's derived index, runs of the stored embedding vectors, long
//   numeric arrays (embedding-shaped data) and long opaque hex/base64 runs block the export.
//
// A `synthetic: true` declaration is still required and still not trusted.

/// Bounds of the content controls. Fixed in the product rather than read from policy so that no overlay, policy
/// override or kernel-policy edit can switch the gate off; `LEARNING_POLICY.upstream.forbidden_content` names the
/// content classes they enforce.
#[derive(Debug, Clone)]
pub struct ContentControls {
    /// a line with at least this many non-whitespace characters that reproduces a project line counts
    pub reproduced_line_min_chars: usize,
    /// reproduced lines tolerated per fixture file (any line of a secret/never-export file blocks)
    pub reproduced_lines_max: usize,
    /// a single reproduced line this long blocks on its own
    pub long_line_chars: usize,
    /// lesson prose: a verbatim excerpt of this many consecutive project lines blocks
    pub prose_consecutive_lines: usize,
    /// longer runs of numbers are embedding/vector-shaped data
    pub max_numeric_array: usize,
    /// longer hex/base64 runs are opaque (encoded or binary) content
    pub max_opaque_blob_chars: usize,
}

impl Default for ContentControls {
    fn default() -> Self {
        ContentControls {
            reproduced_line_min_chars: 16,
            reproduced_lines_max: 1,
            long_line_chars: 48,
            prose_consecutive_lines: 3,
            max_numeric_array: 64,
            max_opaque_blob_chars: 200,
        }
    }
}

fn norm_line(l: &str) -> String {
    l.split_whitespace()
        .collect::<Vec<_>>()
        .join(" ")
        .to_lowercase()
}

fn sig_chars(n: &str) -> usize {
    n.chars().filter(|c| !c.is_whitespace()).count()
}

fn h64(s: &str) -> u64 {
    use std::hash::{Hash, Hasher};
    let mut h = std::collections::hash_map::DefaultHasher::new();
    s.hash(&mut h);
    h.finish()
}

/// Every significant line of the project's text files, for reproduction checks.
struct Corpus {
    files: Vec<(String, bool)>,
    lines: std::collections::HashMap<u64, (usize, usize)>,
    whole: std::collections::HashMap<u64, usize>,
}

/// Paths whose content is not project content for export purposes: the framework's own kernel (upstream already
/// owns it), output derived from it, and the lesson records being exported.
const CORPUS_EXCLUDED: &[&str] = &[
    "governance/kernel/",
    "governance/generated/",
    "spec/lessons/",
];

fn build_corpus(p: &Project, min_chars: usize) -> Corpus {
    let never_export = p
        .policies()
        .get_list("SECURITY_POLICY", "never_export_classes");
    let classifications: Vec<(String, String)> = p
        .overlay()
        .get("DATA_SENSITIVITY.yaml")
        .get("classifications")
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|c| {
                    Some((
                        c.get("pattern")?.as_str()?.to_string(),
                        c.get("class")?.as_str()?.to_string(),
                    ))
                })
                .collect()
        })
        .unwrap_or_default();
    let contract = p.contract();
    let mut c = Corpus {
        files: vec![],
        lines: Default::default(),
        whole: Default::default(),
    };
    for (abs, rel) in crate::paths::iter_repo_files(&p.root, false) {
        if CORPUS_EXCLUDED.iter().any(|x| rel.starts_with(x)) || rel.starts_with(".git/") {
            continue;
        }
        if abs.metadata().map(|m| m.len() > 4_194_304).unwrap_or(true)
            || !crate::util::is_text_file(&abs)
        {
            continue;
        }
        let Ok(text) = crate::util::read_text(&abs) else {
            continue;
        };
        // every project file is export-denied by default; "sensitive" singles out secret and never-export
        // (restricted/confidential) material, one reproduced line of which blocks on its own
        let d = contract.decide(&rel);
        let sensitive = d.is_secret()
            || classifications
                .iter()
                .any(|(pat, cls)| glob_match(pat, &rel) && never_export.contains(cls));
        let idx = c.files.len();
        c.files.push((rel.clone(), sensitive));
        let mut normed = vec![];
        for (i, l) in text.lines().enumerate() {
            let n = norm_line(l);
            if n.is_empty() {
                continue;
            }
            if sig_chars(&n) >= min_chars && n.chars().any(|ch| ch.is_alphanumeric()) {
                c.lines.entry(h64(&n)).or_insert((idx, i + 1));
            }
            normed.push(n);
        }
        if !normed.is_empty() {
            c.whole.entry(h64(&normed.join("\n"))).or_insert(idx);
        }
    }
    c
}

/// Fingerprints of the project's derived index (chunk ids and stored embedding vectors), when an index exists.
struct IndexPrints {
    chunk_ids: std::collections::HashSet<String>,
    db: Option<std::path::PathBuf>,
}

fn index_prints(p: &Project) -> IndexPrints {
    let path = p.db_path();
    let mut chunk_ids = std::collections::HashSet::new();
    if path.exists() {
        if let Ok(conn) =
            rusqlite::Connection::open_with_flags(&path, rusqlite::OpenFlags::SQLITE_OPEN_READ_ONLY)
        {
            if let Ok(mut st) = conn.prepare("SELECT chunk_id FROM chunks LIMIT 500000") {
                if let Ok(rows) = st.query_map([], |r| r.get::<_, String>(0)) {
                    for id in rows.flatten() {
                        if id.len() >= 6 {
                            chunk_ids.insert(id);
                        }
                    }
                }
            }
        }
    }
    IndexPrints {
        chunk_ids,
        db: if path.exists() { Some(path) } else { None },
    }
}

fn float_rx() -> &'static Regex {
    static R: std::sync::OnceLock<Regex> = std::sync::OnceLock::new();
    // integers included: a dump that writes zero components as `0` must not break the run or the alignment
    R.get_or_init(|| Regex::new(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?").unwrap())
}

/// Consecutive float runs of `text`: (longest run length, the sequence of every float in order).
fn float_runs(text: &str) -> (usize, Vec<f64>) {
    let mut longest = 0;
    let mut run = 0;
    let mut last_end: Option<usize> = None;
    let mut all = vec![];
    for m in float_rx().find_iter(text) {
        let adjacent = last_end
            .map(|e| {
                text[e..m.start()]
                    .chars()
                    .all(|c| c.is_whitespace() || matches!(c, ',' | ';' | '[' | ']' | '"' | '\''))
            })
            .unwrap_or(false);
        run = if adjacent { run + 1 } else { 1 };
        longest = longest.max(run);
        last_end = Some(m.end());
        if let Ok(v) = m.as_str().parse::<f64>() {
            all.push(v);
        }
    }
    (longest, all)
}

fn quantise(v: f64) -> i64 {
    (v * 10_000.0).round() as i64
}

/// 4-grams of quantised floats with at least two non-zero members (sparse embeddings share zero runs with anything).
fn grams(v: &[f64]) -> std::collections::HashSet<[i64; 4]> {
    let q: Vec<i64> = v.iter().map(|x| quantise(*x)).collect();
    q.windows(4)
        .filter(|w| w.iter().filter(|x| **x != 0).count() >= 2)
        .map(|w| [w[0], w[1], w[2], w[3]])
        .collect()
}

/// The chunk of the derived index whose stored vector shares a run with `fixture_grams`, if any.
fn vector_hit(db: &Path, fixture_grams: &std::collections::HashSet<[i64; 4]>) -> Option<String> {
    if fixture_grams.is_empty() {
        return None;
    }
    let conn =
        rusqlite::Connection::open_with_flags(db, rusqlite::OpenFlags::SQLITE_OPEN_READ_ONLY)
            .ok()?;
    let mut st = conn
        .prepare("SELECT chunk_id, vec FROM vectors LIMIT 200000")
        .ok()?;
    let rows = st
        .query_map([], |r| Ok((r.get::<_, String>(0)?, r.get::<_, String>(1)?)))
        .ok()?;
    for (id, vec) in rows.flatten() {
        let Ok(v) = serde_json::from_str::<Vec<f64>>(&vec) else {
            continue;
        };
        let q: Vec<i64> = v.iter().map(|x| quantise(*x)).collect();
        for w in q.windows(4) {
            if w.iter().filter(|x| **x != 0).count() >= 2
                && fixture_grams.contains(&[w[0], w[1], w[2], w[3]])
            {
                return Some(id);
            }
        }
    }
    None
}

fn fenced_blocks(text: &str) -> String {
    let mut out = vec![];
    let mut inside = false;
    for l in text.lines() {
        if l.trim_start().starts_with("```") {
            inside = !inside;
            continue;
        }
        if inside {
            out.push(l);
        }
    }
    out.join("\n")
}

/// Run the content controls over outbound items `(label, text, strict)`: strict for fixture files (and fenced code),
/// prose rules for lesson text. Returns the reasons to fail closed and a report of what was examined.
pub fn content_gate(p: &Project, items: &[(String, String, bool)]) -> (Vec<String>, Value) {
    let ctl = ContentControls::default();
    let corpus = build_corpus(p, ctl.reproduced_line_min_chars);
    let prints = index_prints(p);
    let blob_rx = Regex::new(&format!(
        r"[A-Fa-f0-9]{{{n},}}|[A-Za-z0-9+/]{{{n},}}={{0,2}}",
        n = ctl.max_opaque_blob_chars
    ))
    .unwrap();
    let chunk_tok = Regex::new(r"[A-Za-z0-9_:./@\-]+#\d+").unwrap();
    let mut reasons = vec![];
    let mut report = vec![];
    for (label, text, strict) in items {
        if text.trim().is_empty() {
            continue;
        }
        let mut item_reasons: Vec<String> = vec![];
        // 1. whole-file copy
        let normed: Vec<String> = text
            .lines()
            .map(norm_line)
            .filter(|n| !n.is_empty())
            .collect();
        if let Some(fi) = corpus.whole.get(&h64(&normed.join("\n"))) {
            item_reasons.push(format!(
                "{label} is a copy of project file {}",
                corpus.files[*fi].0
            ));
        }
        // 2. reproduced lines
        let check = |t: &str| -> Vec<(usize, String, usize, bool, usize)> {
            t.lines()
                .enumerate()
                .filter_map(|(i, l)| {
                    let n = norm_line(l);
                    if sig_chars(&n) < ctl.reproduced_line_min_chars
                        || !n.chars().any(|c| c.is_alphanumeric())
                    {
                        return None;
                    }
                    corpus.lines.get(&h64(&n)).map(|(fi, ln)| {
                        (
                            i + 1,
                            corpus.files[*fi].0.clone(),
                            *ln,
                            corpus.files[*fi].1,
                            sig_chars(&n),
                        )
                    })
                })
                .collect()
        };
        let strict_text = if *strict {
            text.clone()
        } else {
            fenced_blocks(text)
        };
        let hits = check(&strict_text);
        if !hits.is_empty() {
            let sensitive: Vec<&(usize, String, usize, bool, usize)> =
                hits.iter().filter(|h| h.3).collect();
            let long: Vec<&(usize, String, usize, bool, usize)> =
                hits.iter().filter(|h| h.4 >= ctl.long_line_chars).collect();
            if !sensitive.is_empty() {
                item_reasons.push(format!(
                    "{label} reproduces content of a secret/never-export project file ({}:{})",
                    sensitive[0].1, sensitive[0].2
                ));
            } else if hits.len() > ctl.reproduced_lines_max {
                item_reasons.push(format!("{label} reproduces {} line(s) of raw project content (e.g. {}:{}); a synthetic fixture must not copy repository content, whatever it is named or declared", hits.len(), hits[0].1, hits[0].2));
            } else if !long.is_empty() {
                item_reasons.push(format!(
                    "{label} reproduces a long line of raw project content ({}:{})",
                    long[0].1, long[0].2
                ));
            }
        }
        if !*strict {
            // prose: a multi-line verbatim excerpt of a project file
            let all = check(text);
            let mut run = 1;
            let mut best = if all.is_empty() { 0 } else { 1 };
            for w in all.windows(2) {
                run = if w[1].0 == w[0].0 + 1 && w[1].1 == w[0].1 {
                    run + 1
                } else {
                    1
                };
                best = best.max(run);
            }
            if best >= ctl.prose_consecutive_lines {
                item_reasons.push(format!(
                    "{label} contains a verbatim {best}-line excerpt of project file {}",
                    all[0].1
                ));
            }
            if all.iter().any(|h| h.3) {
                item_reasons.push(format!("{label} quotes a secret/never-export project file"));
            }
        }
        // 3. index data: chunk ids, stored vectors, embedding-shaped numbers, opaque blobs
        if let Some(m) = chunk_tok
            .find_iter(text)
            .find(|m| prints.chunk_ids.contains(m.as_str()))
        {
            item_reasons.push(format!(
                "{label} contains derived-index data (chunk id {})",
                m.as_str()
            ));
        }
        let (longest, floats) = float_runs(text);
        if longest > ctl.max_numeric_array {
            item_reasons.push(format!("{label} contains a run of {longest} numbers (embedding/vector-shaped data; limit {})", ctl.max_numeric_array));
        }
        if let Some(db) = &prints.db {
            if let Some(id) = vector_hit(db, &grams(&floats)) {
                item_reasons.push(format!(
                    "{label} reproduces the stored embedding vector of index chunk {id}"
                ));
            }
        }
        if let Some(m) = blob_rx.find(text) {
            item_reasons.push(format!("{label} contains an opaque {}-character hex/base64 run (encoded or binary content cannot be reviewed)", m.as_str().len()));
        }
        report.push(json!({"item": label, "strict": strict, "reproduced_lines": hits.len(), "longest_numeric_run": longest, "blocked": item_reasons}));
        reasons.extend(item_reasons);
    }
    (
        reasons,
        json!({"controls": {"reproduced_line_min_chars": ctl.reproduced_line_min_chars, "reproduced_lines_max": ctl.reproduced_lines_max, "long_line_chars": ctl.long_line_chars,
            "prose_consecutive_lines": ctl.prose_consecutive_lines, "max_numeric_array": ctl.max_numeric_array, "max_opaque_blob_chars": ctl.max_opaque_blob_chars},
            "corpus_files": corpus.files.len(), "index_chunks_known": prints.chunk_ids.len(), "items": report}),
    )
}

/// The export-approval request a submission must satisfy: the exact packet (id + payload hash) and destination.
pub struct ExportApprovalRequest<'a> {
    pub packet_id: &'a str,
    pub lesson_id: &'a str,
    pub payload_hash: &'a str,
    pub destination: &'a str,
}

/// **The export-approval hook.** Every upstream submission obtains its approval here and nowhere else.
///
/// Today the only approval input is the caller-supplied `--approved-by` string, which is *not* an authenticated
/// human channel: it is recorded as such (`channel: "cli-argument"`, `authenticated: false`) and bound to the exact
/// packet and payload hash it approved, so it cannot be replayed onto another packet.
///
/// **Integration point (BC-P2-10, WS-3):** when the authenticated human channel lands, this function obtains the
/// approval from it — e.g. a Human Decision Gate raised for `(packet_id, payload_hash, destination)` and answered
/// through the channel the acting agent cannot operate — and returns its evidence here (`authenticated: true`);
/// `submit` needs no other change. `LEARNING_POLICY.upstream.approval = human` must then refuse a CLI-string approval.
pub fn resolve_export_approval(
    p: &Project,
    req: &ExportApprovalRequest,
    approved_by: Option<&str>,
) -> Result<Value> {
    let policy = p
        .policies()
        .get_str("LEARNING_POLICY", "upstream.approval", "human");
    if policy == "human" && approved_by.map(|s| s.trim().is_empty()).unwrap_or(true) {
        return Err(GovError::new(
            "HUMAN_GATE_REQUIRED",
            "LEARNING_POLICY.upstream.approval=human: --approved-by <human> is required",
        ));
    }
    Ok(
        json!({"required": policy, "approved_by": approved_by, "approved_at": now_iso(), "channel": "cli-argument", "authenticated": false,
            "binds": {"packet_id": req.packet_id, "lesson_id": req.lesson_id, "payload_hash": req.payload_hash, "destination": req.destination},
            "note": "unauthenticated approval string; the authenticated human channel (BC-P2-10) replaces it at this hook"}),
    )
}

fn payload_hash_of(packet: &Value) -> String {
    hash_value(
        &json!({"p": packet["problem_statement"], "f": packet["generic_failure_mode"], "i": packet["impact"], "c": packet["suggested_framework_change"], "x": packet["synthetic_fixture"], "m": packet["metrics"]}),
    )
}

/// `gov upstream prepare <lesson-id>`: build a sanitised packet or fail closed with reasons.
pub fn prepare(p: &Project, lesson_id: &str) -> Result<Value> {
    p.require_installed()?;
    crate::authority::require(p, "upstream_prepare")?;
    let pol = p.policies();
    let store = RecordStore::load(&p.root);
    let lesson = store
        .get(lesson_id)
        .ok_or_else(|| GovError::new("LESSON_NOT_FOUND", format!("{lesson_id} not found")))?;
    if lesson.rtype() != "lesson" {
        return Err(GovError::new(
            "USAGE",
            format!("{lesson_id} is not a lesson"),
        ));
    }
    let eligible = pol.get_list("LEARNING_POLICY", "upstream_eligible_scopes");
    let scope = lesson.get("scope");
    if !eligible.contains(&scope) {
        return Err(GovError::new("UPSTREAM_SCOPE", format!("lesson {lesson_id} has scope {scope}; only {eligible:?} lessons may be exported (framework §75E)")));
    }
    // LEARNING_POLICY.corroboration_min_sources / lesson_lifecycle: reported together with the content scans below
    let min_sources = pol
        .get_i64("LEARNING_POLICY", "corroboration_min_sources", 1)
        .max(0) as usize;
    let sources = lesson.list("sources").len() + lesson.list("corroboration").len();
    let lifecycle_ok = pol.get_list("LEARNING_POLICY", "lesson_lifecycle");
    let mut policy_blocks: Vec<String> = vec![];
    if sources < min_sources {
        policy_blocks.push(format!("lesson {lesson_id} cites {sources} source(s); LEARNING_POLICY.corroboration_min_sources = {min_sources}"));
    }
    if !lifecycle_ok.is_empty()
        && !lesson.get("lifecycle").is_empty()
        && !lifecycle_ok.contains(&lesson.get("lifecycle"))
    {
        policy_blocks.push(format!(
            "lesson lifecycle '{}' is not a LEARNING_POLICY.lesson_lifecycle value",
            lesson.get("lifecycle")
        ));
    }
    let never_export = pol.get_list("SECURITY_POLICY", "never_export_classes");
    let classifications: Vec<(String, String)> = p
        .overlay()
        .get("DATA_SENSITIVITY.yaml")
        .get("classifications")
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|c| {
                    Some((
                        c.get("pattern")?.as_str()?.to_string(),
                        c.get("class")?.as_str()?.to_string(),
                    ))
                })
                .collect()
        })
        .unwrap_or_default();
    let forbidden_paths = pol.get_list("LEARNING_POLICY", "upstream.forbidden_paths");
    let max_code = pol.get_i64(
        "LEARNING_POLICY",
        "upstream.max_code_lines_unless_synthetic",
        0,
    ) as usize;
    let metrics_enabled = pol.get_bool(
        "LEARNING_POLICY",
        "upstream.aggregate_metrics_enabled",
        false,
    );
    let mut identifiers: Vec<String> = p.secret_scanner().identifiers.clone();
    identifiers.push(p.project_name());
    identifiers.push(
        p.root
            .file_name()
            .map(|f| f.to_string_lossy().to_string())
            .unwrap_or_default(),
    );
    let mut scans = json!({"identifiers_redacted": 0, "paths_removed": [], "secret_hits": [], "code_lines": 0, "blocked_reasons": []});
    let mut blocked: Vec<String> = policy_blocks;
    let mut sanitize = |field: &str| -> String {
        let raw = lesson.get(field);
        let (t1, n) = redact_identifiers(&raw, &identifiers);
        scans["identifiers_redacted"] =
            json!(scans["identifiers_redacted"].as_u64().unwrap_or(0) + n as u64);
        let (t2, removed) = strip_paths(&t1, &forbidden_paths);
        for r in removed {
            scans["paths_removed"]
                .as_array_mut()
                .unwrap()
                .push(json!(r));
        }
        let hits = p.secret_scanner().scan_text(&t2, field);
        for h in hits {
            scans["secret_hits"]
                .as_array_mut()
                .unwrap()
                .push(json!({"field": field, "pattern": h.pattern_id}));
            blocked.push(format!("secret pattern {} in field {field}", h.pattern_id));
        }
        let cl = code_lines(&t2);
        scans["code_lines"] = json!(scans["code_lines"].as_u64().unwrap_or(0) + cl as u64);
        t2
    };
    let problem = sanitize("problem_statement");
    let failure = sanitize("generic_failure_mode");
    let impact = sanitize("impact");
    let change = sanitize("suggested_change");
    let body = sanitize("body");
    let category = {
        let c = sanitize("category");
        if c.is_empty() {
            "uncategorised".to_string()
        } else {
            c
        }
    };
    let _title = sanitize("title");
    let _tags = sanitize("tags");
    let synthetic = lesson.data.get("synthetic_reproducer").cloned();
    let mut fixture: Option<Value> = None;
    let mut outbound_items: Vec<(String, String, bool)> = [
        "problem_statement",
        "generic_failure_mode",
        "impact",
        "suggested_change",
        "body",
        "category",
        "title",
    ]
    .iter()
    .map(|f| (format!("lesson field {f}"), lesson.get(f), false))
    .collect();
    if let Some(sf) = &synthetic {
        if sf.get("synthetic").and_then(|v| v.as_bool()) != Some(true) {
            blocked.push("synthetic_reproducer must declare synthetic: true".into());
        }
        let mut files = serde_json::Map::new();
        for (name, content) in sf
            .get("files")
            .and_then(|f| f.as_object())
            .cloned()
            .unwrap_or_default()
        {
            let text = content.as_str().unwrap_or("").to_string();
            outbound_items.push((format!("fixture file {name}"), text.clone(), true));
            if forbidden_paths.iter().any(|f| glob_match(f, &name)) {
                blocked.push(format!(
                    "fixture file {name} matches a forbidden outbound path"
                ));
            }
            if let Some((pat, cls)) = classifications
                .iter()
                .find(|(pat, cls)| glob_match(pat, &name) && never_export.contains(cls))
            {
                blocked.push(format!("fixture file {name} matches DATA_SENSITIVITY classification {pat} ({cls}) in SECURITY_POLICY.never_export_classes"));
            }
            let (t1, _) = redact_identifiers(&text, &identifiers);
            if !p.secret_scanner().scan_text(&t1, &name).is_empty() {
                blocked.push(format!("secret pattern in fixture file {name}"));
            }
            files.insert(name, json!(t1));
        }
        fixture = Some(
            json!({"synthetic": true, "description": sf.get("description").cloned().unwrap_or(json!("")), "files": files}),
        );
    }
    // content controls: what would leave, not what it is called (BC-P2-50)
    let (content_reasons, content_report) = content_gate(p, &outbound_items);
    blocked.extend(content_reasons);
    scans["content"] = content_report;
    let total_code = scans["code_lines"].as_u64().unwrap_or(0) as usize;
    if total_code > max_code && fixture.is_none() {
        blocked.push(format!("{total_code} raw code line(s) in lesson text exceed policy max {max_code}; provide a synthetic reproducer instead"));
    }
    if body.len() > 4000 {
        blocked
            .push("lesson body too long for an abstraction packet (>4000 chars): summarise".into());
    }
    let metrics = if metrics_enabled {
        lesson.data.get("aggregate_metrics").cloned()
    } else {
        None
    };
    let existing = std::fs::read_dir(outbound_dir(p))
        .map(|rd| rd.count())
        .unwrap_or(0);
    let packet_id = format!("PKT-{:04}", existing + 1);
    let mut packet = json!({"packet_id": packet_id, "lesson_id": lesson_id, "scope": "FRAMEWORK", "category": category, "problem_statement": problem, "generic_failure_mode": failure, "impact": impact,
        "evidence_strength": if lesson.get("evidence_strength").is_empty() { "low".to_string() } else { lesson.get("evidence_strength") }, "suggested_framework_change": change, "source_project_alias": p.project_alias(), "local_reference": lesson_id,
        "sensitive_content_removed": true, "raw_product_code_included": false, "raw_customer_data_included": false, "raw_spec_included": false, "synthetic_fixture": fixture, "metrics": metrics, "prepared_at": now_iso(), "framework_version": p.framework_version(), "approval": {"required": pol.get_str("LEARNING_POLICY", "upstream.approval", "human"), "approved_by": null}});
    if let Some(a) = packet["source_project_alias"].as_str() {
        if identifiers.iter().any(|i| i.eq_ignore_ascii_case(a)) {
            blocked.push("project alias equals a project identifier; set a non-identifying alias in PROJECT_POLICY".into());
        }
    }
    scans["blocked_reasons"] = json!(blocked);
    packet["scans"] = scans.clone();
    let errs = p.schemas().errors("upstream-packet", &packet)?;
    let mut blocked_all = blocked.clone();
    blocked_all.extend(errs.iter().map(|e| format!("schema: {e}")));
    let dir = outbound_dir(p).join(packet["packet_id"].as_str().unwrap_or("PKT"));
    std::fs::create_dir_all(&dir)?;
    if !blocked_all.is_empty() {
        write_json(
            &dir.join("blocked.json"),
            &json!({"lesson": lesson_id, "reasons": blocked_all, "scans": scans, "at": now_iso()}),
        )?;
        return Err(GovError::new(
            "UPSTREAM_BLOCKED",
            format!(
                "export gate failed closed for {lesson_id}: {}",
                blocked_all.join("; ")
            ),
        )
        .with_details(json!({"reasons": blocked_all, "scans": scans})));
    }
    let payload_hash = payload_hash_of(&packet);
    packet["payload_hash"] = json!(payload_hash);
    write_yaml(&dir.join("packet.yaml"), &packet)?;
    write_json(&dir.join("scans.json"), &scans)?;
    Ok(
        json!({"packet_id": packet["packet_id"], "path": dir.join("packet.yaml").display().to_string(), "payload_hash": payload_hash, "scans": scans, "export_allowed": true, "approval_required": packet["approval"]["required"]}),
    )
}

/// `gov upstream submit <packet-id> --destination <canonical lessons/inbox dir> --approved-by <human>`.
pub fn submit(
    p: &Project,
    packet_id: &str,
    destination: &str,
    approved_by: Option<&str>,
) -> Result<Value> {
    p.require_installed()?;
    crate::orchestration::control::guard_write(p, "upstream submit")?;
    crate::authority::require(p, "upstream_submit")?;
    let pol = p.policies();
    let dir = outbound_dir(p).join(packet_id);
    let packet_path = dir.join("packet.yaml");
    if !packet_path.exists() {
        return Err(GovError::new(
            "PACKET_NOT_FOUND",
            format!("{packet_id} not prepared (run gov upstream prepare)"),
        ));
    }
    let mut packet = crate::util::read_yaml(&packet_path)?;
    p.schemas()
        .validate("upstream-packet", &packet, "(packet)")?;
    let scans = read_json(&dir.join("scans.json")).unwrap_or(json!({}));
    if !scans["blocked_reasons"]
        .as_array()
        .map(|a| a.is_empty())
        .unwrap_or(false)
    {
        return Err(GovError::new(
            "UPSTREAM_BLOCKED",
            "packet has blocked reasons",
        ));
    }
    // the packet must be the one prepared: any edit after prepare changes its payload hash
    if packet["payload_hash"].as_str() != Some(payload_hash_of(&packet).as_str()) {
        return Err(GovError::new(
            "UPSTREAM_BLOCKED",
            "packet content differs from its recorded payload hash (edited after prepare); prepare it again",
        ));
    }
    // content controls again over exactly what would leave (fixture files and packet text), whatever their names
    let mut outbound_items: Vec<(String, String, bool)> = [
        "problem_statement",
        "generic_failure_mode",
        "impact",
        "suggested_framework_change",
        "category",
    ]
    .iter()
    .map(|f| {
        (
            format!("packet field {f}"),
            packet[*f].as_str().unwrap_or("").to_string(),
            false,
        )
    })
    .collect();
    if let Some(files) = packet["synthetic_fixture"]["files"].as_object() {
        for (name, content) in files {
            outbound_items.push((
                format!("fixture file {name}"),
                content.as_str().unwrap_or("").to_string(),
                true,
            ));
        }
    }
    let (content_reasons, content_report) = content_gate(p, &outbound_items);
    if !content_reasons.is_empty() {
        return Err(GovError::new(
            "UPSTREAM_BLOCKED",
            format!(
                "export gate failed closed at submission: {}",
                content_reasons.join("; ")
            ),
        )
        .with_details(json!({"reasons": content_reasons, "content": content_report})));
    }
    // re-scan at submission (content could have been edited)
    let fail_closed = pol.get_str(
        "SECURITY_POLICY",
        "on_secret_in_export_payload",
        "fail_closed",
    ) == "fail_closed";
    for f in [
        "problem_statement",
        "generic_failure_mode",
        "impact",
        "suggested_framework_change",
        "category",
        "source_project_alias",
    ] {
        if (!p
            .secret_scanner()
            .scan_text(packet[f].as_str().unwrap_or(""), f)
            .is_empty()
            || !p
                .secret_scanner()
                .identifier_hits(packet[f].as_str().unwrap_or(""))
                .is_empty())
            && fail_closed
        {
            return Err(GovError::new("UPSTREAM_BLOCKED", format!("secret or identifier in {f} at submission (SECURITY_POLICY.on_secret_in_export_payload=fail_closed)")));
        }
    }
    for flag in [
        "raw_product_code_included",
        "raw_customer_data_included",
        "raw_spec_included",
    ] {
        if packet[flag].as_bool() != Some(false) {
            return Err(GovError::new(
                "UPSTREAM_BLOCKED",
                format!("{flag} must be false"),
            ));
        }
    }
    let approval_evidence = resolve_export_approval(
        p,
        &ExportApprovalRequest {
            packet_id,
            lesson_id: packet["lesson_id"].as_str().unwrap_or(""),
            payload_hash: packet["payload_hash"].as_str().unwrap_or(""),
            destination,
        },
        approved_by,
    )?;
    if destination.starts_with("http://")
        || destination.starts_with("https://")
        || destination.starts_with("git@")
    {
        return Err(GovError::new("REMOTE_TRANSPORT_NOT_CONFIGURED", "remote destinations are not supported by this release; submit to a local clone of the canonical repository (lessons/inbox/)"));
    }
    let dest = Path::new(destination);
    if !dest.is_dir() || !dest.ends_with("inbox") {
        return Err(GovError::new(
            "UPSTREAM_DESTINATION",
            format!("destination must be an existing lessons/inbox directory (got {destination})"),
        ));
    }
    // outbound allowlist: exactly packet.yaml (+ fixture files embedded in the packet). Nothing else leaves.
    let allowed = pol.get_list("LEARNING_POLICY", "upstream.allowed_payload");
    if !allowed.iter().any(|a| a == "packet") {
        return Err(GovError::new(
            "UPSTREAM_BLOCKED",
            "policy does not allow packet export",
        ));
    }
    packet["approval"] = approval_evidence.clone();
    let target_dir = dest.join(packet_id.to_string() + "-" + p.project_alias().as_str());
    std::fs::create_dir_all(&target_dir)?;
    write_yaml(&target_dir.join("packet.yaml"), &packet)?;
    let mut sent = vec!["packet.yaml".to_string()];
    if let Some(fx) = packet["synthetic_fixture"].as_object() {
        if allowed.iter().any(|a| a == "synthetic_fixture") {
            for (name, content) in fx
                .get("files")
                .and_then(|f| f.as_object())
                .cloned()
                .unwrap_or_default()
            {
                let safe = name.replace("..", "_").trim_start_matches('/').to_string();
                let path = target_dir.join("fixture").join(&safe);
                if let Some(d) = path.parent() {
                    std::fs::create_dir_all(d)?;
                }
                crate::util::write_text(&path, content.as_str().unwrap_or(""))?;
                sent.push(format!("fixture/{safe}"));
            }
        }
    }
    let entry = json!({"at": now_iso(), "packet_id": packet_id, "lesson_id": packet["lesson_id"], "payload_hash": packet["payload_hash"], "destination": target_dir.display().to_string(), "approved_by": approved_by, "approval": approval_evidence, "session": p.session_id, "files": sent});
    let ledger = p.root.join(pol.get_str(
        "LEARNING_POLICY",
        "upstream.ledger",
        "spec/reports/upstream-ledger.jsonl",
    ));
    let mut text = crate::util::read_text(&ledger).unwrap_or_default();
    text.push_str(&serde_json::to_string(&entry)?);
    text.push('\n');
    crate::util::write_text(&ledger, &text)?;
    let mut store = RecordStore::load(&p.root);
    if let Some(l) = store.get_mut(packet["lesson_id"].as_str().unwrap_or("")) {
        l.set("lifecycle", json!("promoted"));
        l.set("upstream", json!({"packet_id": packet_id, "payload_hash": packet["payload_hash"], "at": now_iso()}));
        save_record(&p.root, l)?;
    }
    Ok(entry)
}
