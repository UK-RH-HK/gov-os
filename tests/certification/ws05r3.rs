//! Repair iteration 1, round 3, WS-5 (P2-AR-0036): governed work generated from events (BC-P2-24), material changes
//! made inside tasks (BC-P2-13 close side), the close / claim / DAG wiring of WS-4's round-2 APIs (R2-1, R2-2,
//! R2-3), experiments closing through their lifecycle (IP-WS10-11), the availability rule at claim, and the claims
//! store at its BC-P2-31 location. Black-box through the `gov` JSON contract; human answers go through the owner-
//! signed channel (`crate::ws03`). Builder regression evidence (Contract v3 O3), not acceptance evidence.
use crate::common::*;
use crate::ws05::{receipt, receipt_with, traceable_inputs};
use serde_json::{json, Value};
use std::path::Path;

fn fresh(tag: &str) -> (std::path::PathBuf, Gov) {
    let (root, g) = setup_fixture("greenfield", tag, "S-ws5r3");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        tag,
        "--alias",
        &format!("a-{tag}"),
    ]);
    git_commit_all(&root, "after init");
    (root, g)
}

fn create(g: &Gov, class: &str, objective: &str, allowed: &str, fields: Value) -> String {
    let f = fields.to_string();
    let mut args = vec![
        "task",
        "create",
        "--class",
        class,
        "--objective",
        objective,
        "--status",
        "READY",
        "--fields",
        &f,
    ];
    if !allowed.is_empty() {
        args.extend(["--allowed", allowed]);
    }
    g.ok(&args)["id"].as_str().unwrap().to_string()
}

/// Every generated task of the project, with its generation block.
fn generated(root: &Path) -> Vec<Value> {
    let mut out = vec![];
    let dir = root.join("spec/tasks");
    let mut names: Vec<String> = std::fs::read_dir(&dir)
        .unwrap()
        .filter_map(|e| e.ok())
        .map(|e| e.file_name().to_string_lossy().to_string())
        .filter(|n| n.starts_with("TASK-") && n.ends_with(".yaml"))
        .collect();
    names.sort();
    for n in names {
        let t = yaml(root, &format!("spec/tasks/{n}"));
        if t["generation"].is_object() {
            out.push(t);
        }
    }
    out
}

fn of_source<'a>(g: &'a [Value], source: &str) -> Vec<&'a Value> {
    g.iter()
        .filter(|t| t["generation"]["source"] == source)
        .collect()
}

fn write_file(root: &Path, rel: &str, text: &str) {
    let p = root.join(rel);
    std::fs::create_dir_all(p.parent().unwrap()).unwrap();
    std::fs::write(p, text).unwrap();
}

/// BC-P2-24 (Contract v3:571-583; AC-5): research discoveries, proposed decisions, lessons, human decisions, missing
/// tools and skills, retrieval failures and performance regressions each generate governed work **when the event
/// is recorded** (the command that recorded it), in the same DAG, linked to the record the event left, with the
/// designated role of its source — once: reconciling again generates nothing, and more work needing the same
/// missing tool extends the existing task's `blocks` instead of duplicating it.
#[test]
fn every_event_source_generates_linked_governed_work_once() {
    let (root, g) = fresh("ws5r3-gen");
    crate::ws03::human_channel(&g);
    // --- research discoveries, proposed decisions and lessons: a worker's return
    let t = create(&g, "research", "benchmark totals", "docs/**", json!({}));
    let h = g.ok(&[
        "handoff",
        "create",
        "--to-role",
        "research-agent",
        "--task",
        &t,
    ]);
    let hid = h["id"].as_str().unwrap().to_string();
    let ret = root.join(".governance-runtime/ret.json");
    std::fs::write(&ret, json!({"task": t, "status": "success", "work_completed": "benchmark", "files_changed": [], "evidence": [],
        "tests": {"status": "passed"}, "discoveries": ["u32 overflows at 4.2M cents", "none"], "risks": ["data loss"],
        "lessons": ["check integer widths before choosing a money type"], "proposed_decisions": ["adopt u64 cents"],
        "unresolved": ["migration of stored totals"], "recommended_next_action": "create a migration task"}).to_string()).unwrap();
    g.with_role("research-agent").with_session("S-r").ok(&[
        "handoff",
        "return",
        &hid,
        "--file",
        ret.to_str().unwrap(),
    ]);
    let gen = generated(&root);
    let disc = of_source(&gen, "research-discovery");
    assert_eq!(
        disc.len(),
        2,
        "one per discovery / unresolved item, trivial items ignored: {gen:?}"
    );
    for d in &disc {
        assert_eq!(d["class"], "discovery");
        assert_eq!(d["role"], "product-spec-agent");
        assert!(
            d["derived_from"].as_array().unwrap().contains(&json!(hid)),
            "{d}"
        );
        assert_eq!(d["generation"]["detected_by"], "handoff return");
    }
    let prop = of_source(&gen, "proposed-decision");
    assert_eq!(prop.len(), 1, "{gen:?}");
    assert_eq!(prop[0]["class"], "decision-preparation");
    let les = of_source(&gen, "lesson");
    assert_eq!(les.len(), 1, "{gen:?}");
    let lesson_id = les[0]["generation"]["subject"]
        .as_str()
        .unwrap()
        .to_string();
    assert!(lesson_id.starts_with("L-"));
    assert!(les[0]["derived_from"]
        .as_array()
        .unwrap()
        .contains(&json!(lesson_id)));
    // --- a human decision on a gate an agent raised
    let gate = g.ok(&[
        "gate",
        "create",
        "--question",
        "Adopt u64 cents for totals?",
        "--fields",
        &crate::ws03::package(json!({})),
    ])["id"]
        .as_str()
        .unwrap()
        .to_string();
    let dec = crate::ws03::human_decide(&g, &gate, "A");
    let did = dec["decision"].as_str().unwrap().to_string();
    let gen = generated(&root);
    let hd = of_source(&gen, "human-decision");
    assert_eq!(hd.len(), 1, "{gen:?}");
    assert_eq!(hd[0]["generation"]["subject"], json!(did));
    assert!(hd[0]["derived_from"]
        .as_array()
        .unwrap()
        .contains(&json!(did)));
    assert_eq!(hd[0]["class"], "specification");
    // --- missing tools and skills: one capability task per missing id, blocking the work that needs it
    let needy = create(
        &g,
        "tooling",
        "needs a missing tool and skill",
        "tools/**",
        json!({"required_tools": ["TOOL-NOPE"], "required_skills": ["SKL-NOPE"]}),
    );
    let gen = generated(&root);
    let tools = of_source(&gen, "missing-tool");
    let skills = of_source(&gen, "missing-skill");
    assert_eq!((tools.len(), skills.len()), (1, 1), "{gen:?}");
    assert_eq!(tools[0]["blocks"], json!([needy]));
    assert_eq!(tools[0]["role"], "tooling-engineer");
    let tool_task = tools[0]["id"].as_str().unwrap().to_string();
    let reasons = g.ok(&["task", "dag"])["blocked"].to_string();
    assert!(
        reasons.contains(&tool_task),
        "the needing task waits for the capability work: {reasons}"
    );
    let needy2 = create(
        &g,
        "tooling",
        "also needs the tool",
        "tools/b/**",
        json!({"required_tools": ["TOOL-NOPE"]}),
    );
    let gen = generated(&root);
    assert_eq!(
        of_source(&gen, "missing-tool").len(),
        1,
        "no duplicate capability task"
    );
    let tt = yaml(&root, &format!("spec/tasks/{tool_task}.yaml"));
    assert_eq!(tt["blocks"], json!([needy, needy2]), "{tt}");
    // --- a retrieval failure: its follow-up task is linked from the failure record
    let m = g.with_role("backend-engineer").ok(&[
        "memory",
        "miss",
        "--query",
        "where is the rounding policy?",
        "--expected",
        "D-0009",
    ]);
    let fid = m["id"].as_str().unwrap().to_string();
    let rec = yaml(&root, m["path"].as_str().unwrap());
    assert_eq!(rec["follow_up"]["status"], "linked", "{rec}");
    let ft = rec["follow_up"]["task"].as_str().unwrap().to_string();
    let ftask = yaml(&root, &format!("spec/tasks/{ft}.yaml"));
    assert_eq!(ftask["generation"]["source"], "retrieval-failure");
    assert_eq!(ftask["generation"]["failure"], json!(fid));
    assert_eq!(ftask["class"], "memory");
    // no loops: a miss on a query made for the follow-up itself (its context compile queries its title and
    // objective) is recorded, and generates no follow-up of the follow-up
    let n_rf = of_source(&generated(&root), "retrieval-failure").len();
    let own = format!(
        "{} {}",
        ftask["title"].as_str().unwrap(),
        ftask["objective"].as_str().unwrap()
    );
    let m2 = g
        .with_role("backend-engineer")
        .ok(&["memory", "miss", "--query", &own]);
    assert!(m2["id"].is_string(), "{m2}");
    assert_eq!(
        of_source(&generated(&root), "retrieval-failure").len(),
        n_rf
    );
    // --- a performance regression reported by the product: a durable regression record, then linked work
    g.ok(&[
        "telemetry",
        "emit",
        "--name",
        "product.perf",
        "--attrs",
        r#"{"latency_ms": 900, "baseline_ms": 100}"#,
    ]);
    let gen = generated(&root);
    let perf = of_source(&gen, "performance-regression");
    assert_eq!(perf.len(), 1, "{gen:?}");
    assert_eq!(perf[0]["class"], "performance");
    let pf = perf[0]["generation"]["failure"]
        .as_str()
        .unwrap()
        .to_string();
    assert!(
        perf[0]["derived_from"]
            .as_array()
            .unwrap()
            .contains(&json!(pf)),
        "an indexed failure record is linked by an edge: {}",
        perf[0]
    );
    // a measurement within its baseline is not a regression
    g.ok(&[
        "telemetry",
        "emit",
        "--name",
        "product.perf2",
        "--attrs",
        r#"{"latency_ms": 101, "baseline_ms": 100}"#,
    ]);
    assert_eq!(
        of_source(&generated(&root), "performance-regression").len(),
        1
    );
    // --- idempotent: reconciling again generates nothing; the dry run proposes nothing new
    let before = generated(&root).len();
    let again = g.ok(&["task", "generate"]);
    assert_eq!(again["created"], json!([]), "{again}");
    let dry = g.ok(&["task", "generate", "--dry-run"]);
    assert_eq!(dry["pending"], json!([]), "{dry}");
    assert_eq!(generated(&root).len(), before);
    // generated work names its source everywhere work is picked
    let list = g.ok(&["task", "list"]);
    assert!(list
        .as_array()
        .unwrap()
        .iter()
        .any(|x| x["generated_from"]["source"] == "human-decision"));
    // --- linked in the graph: the generated work reaches its source through a DERIVED_FROM edge
    g.ok(&["rebuild-memory", "--incremental"]);
    let hdt = hd[0]["id"].as_str().unwrap().to_string();
    let nb = g.ok(&["memory", "graph", &hdt, "--depth", "1"]);
    assert!(
        nb.as_array()
            .unwrap()
            .iter()
            .any(|x| x["node"] == json!(did)),
        "{nb}"
    );
    // --- generation is a governed write: refused while writes are frozen (its dry run still reads)
    g.ok(&["freeze-writes", "--reason", "incident"]);
    assert_eq!(g.err(&["task", "generate"]).error_code(), "FROZEN");
    g.ok(&["task", "generate", "--dry-run"]);
    g.ok(&["resume"]);
}

/// BC-P2-24 + the availability rule: a critical security finding recorded by a persisted audit generates security
/// remediation work that names the check it remedies; the hard-block refuses unrelated claims (naming the block),
/// while the remediation stays claimable under the block it remedies.
#[test]
fn a_security_finding_generates_remediation_that_stays_available_under_its_block() {
    let (root, g) = fresh("ws5r3-sec");
    let other = create(&g, "documentation", "unrelated docs", "docs/**", json!({}));
    write_file(
        &root,
        "src/creds.rs",
        "pub const K: &str = \"AKIAIOSFODNN7EXAMPLE\";\npub const S: &str = \"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\";\n",
    );
    let a = g.run(&["audit"]);
    assert!(
        !a.ok(),
        "a secret in product source is unhealthy: {}",
        a.envelope
    );
    let gen = generated(&root);
    let sec = of_source(&gen, "security-finding");
    assert!(!sec.is_empty(), "{gen:?}");
    // the path the secret is in is the remediation's scope; every check reporting it is remedied by it
    let remedy = sec
        .iter()
        .find(|t| t["allowed_paths"].to_string().contains("src/creds.rs"))
        .unwrap_or_else(|| panic!("{sec:?}"));
    assert_eq!(remedy["class"], "security");
    assert_eq!(remedy["role"], "security-engineer");
    assert!(
        !remedy["remedies"].as_array().unwrap().is_empty(),
        "{remedy}"
    );
    let rid = remedy["id"].as_str().unwrap().to_string();
    let e = g.err(&["task", "claim", &other]);
    assert_eq!(e.error_code(), "HEALTH_HARD_BLOCK", "{}", e.envelope);
    let c = g
        .with_role("security-engineer")
        .with_session("S-sec")
        .ok(&["task", "claim", &rid]);
    let remedied = c["availability"]["remedied_blocks"].as_array().unwrap();
    assert!(!remedied.is_empty(), "{c}");
    for b in remedied {
        assert!(
            remedy["remedies"].as_array().unwrap().contains(&b["check"]),
            "{c}"
        );
    }
    // a second audit of the same failure generates nothing new
    let _ = g.run(&["audit"]);
    let n = of_source(&generated(&root), "security-finding").len();
    assert_eq!(n, sec.len());
}

/// BC-P2-24 / AC-5 "remediation from each health failure", on a RED result that the event's own records make stale
/// (epsilon-r O5 S8): the doctor records a secret in product source, the audit that follows writes its governance-
/// suite record, which changes the doctor check's inputs before generation reads the health state. Generation
/// re-evaluates the stale failure (as the guard re-evaluates a stale block) instead of dropping it: one security
/// remediation for the one condition, remedying the doctor check and the path-map family that both report it, plus
/// the unrelated audit finding; nothing is generated twice.
#[test]
fn a_red_result_made_stale_by_the_events_own_records_is_reevaluated_not_dropped() {
    let (root, g) = fresh("ws5r3-red");
    write_file(
        &root,
        "src/creds.rs",
        "pub const K: &str = \"AKIAIOSFODNN7EXAMPLE\";\n",
    );
    let adapter = root.join("governance/generated/adapters/api/system-instruction.txt");
    let mut text = std::fs::read_to_string(&adapter).unwrap();
    text.push_str("\n#tamper\n");
    std::fs::write(&adapter, text).unwrap();
    let d = g.run(&["doctor"]);
    assert!(!d.ok(), "{}", d.envelope);
    let a = g.run(&["audit"]);
    assert!(!a.ok(), "{}", a.envelope);
    let _ = g.run(&["continue"]);
    let _ = g.run(&["task", "replan"]);
    let gen = generated(&root);
    let remedies = |t: &Value| -> Vec<String> {
        t["remedies"]
            .as_array()
            .map(|a| {
                a.iter()
                    .filter_map(|x| x.as_str().map(|s| s.to_string()))
                    .collect()
            })
            .unwrap_or_default()
    };
    let secret: Vec<&Value> = of_source(&gen, "security-finding")
        .into_iter()
        .filter(|t| remedies(t).contains(&"D011".to_string()))
        .collect();
    assert_eq!(secret.len(), 1, "one remediation for the secret: {gen:?}");
    assert!(
        remedies(secret[0]).contains(&"path_map_compliance".to_string()),
        "the doctor check and the path-map family report one condition: {}",
        secret[0]
    );
    assert!(
        gen.iter()
            .any(|t| remedies(t).contains(&"adapter_portability".to_string())),
        "{gen:?}"
    );
    // reconciling again generates nothing
    let n = gen.len();
    let again = g.ok(&["task", "generate"]);
    assert!(again["created"].as_array().unwrap().is_empty(), "{again}");
    assert_eq!(generated(&root).len(), n);
}

/// BC-P2-24 CIT effects (Contract v3:578, :1134): a CIT that changes an input of completed work generates its
/// revalidation work when it executes — one `validation` task that `revalidates` the completed task, linked to it,
/// counted as the CIT-effect work of the engine (adopted, never duplicated: reconciling again creates nothing).
#[test]
fn a_cit_effect_on_completed_work_generates_one_linked_revalidation_task() {
    let (root, g) = fresh("ws5r3-cit");
    let inputs = traceable_inputs(&root, "0730");
    git_commit_all(&root, "inputs");
    g.ok(&["rebuild-memory", "--incremental"]);
    let done = create(&g, "refactor", "totals", "src/**", inputs);
    g.ok(&["context", "compile", &done]);
    g.ok(&["task", "claim", &done]);
    write_file(&root, "src/totals.rs", "pub fn t() -> i64 { 398 }\n");
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = receipt(
        &g,
        &root,
        &done,
        "done",
        "totals",
        &["src/totals.rs"],
        "not_applicable_with_reason",
    );
    g.ok(&["task", "close", &done, "--report", &rep]);
    git_commit_all(&root, "done");
    let mf = root.join(".governance-runtime/mf-cit.json");
    std::fs::write(
        &mf,
        json!([{"op": "set_field", "target": "REQ-0730", "field": "statement", "value": "totals are integer cents"}]).to_string(),
    )
    .unwrap();
    let cit = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "state the unit",
        "--trigger",
        "behaviour_change",
        "--targets",
        "REQ-0730",
        "--manifest",
        mf.to_str().unwrap(),
    ])["id"]
        .as_str()
        .unwrap()
        .to_string();
    let sim = g.ok(&["cit", "simulate", &cit]);
    crate::ws03::human_decide(&g, sim["human_gate"].as_str().unwrap(), "A");
    g.ok(&["cit", "approve", &cit, "--by", "owner", "--method", "human"]);
    g.ok(&["cit", "execute", &cit]);
    let list = g.ok(&["task", "list"]);
    let reval: Vec<&Value> = list
        .as_array()
        .unwrap()
        .iter()
        .filter(|t| t["generated_from"]["source"] == "cit-effect")
        .collect();
    assert_eq!(reval.len(), 1, "{list}");
    assert_eq!(reval[0]["generated_from"]["subject"], json!(done), "{list}");
    let rid = reval[0]["id"].as_str().unwrap().to_string();
    let rt = g.ok(&["task", "show", &rid]);
    assert_eq!(rt["revalidates"], json!(done), "{rt}");
    // the engine counts it as the CIT effect's work: reconciling again creates nothing, and lists it as adopted or
    // generated for this source
    let again = g.ok(&["task", "generate"]);
    assert_eq!(again["created"], json!([]), "{again}");
    let n = list
        .as_array()
        .unwrap()
        .iter()
        .filter(|t| t["generated_from"]["source"] == "cit-effect")
        .count();
    assert_eq!(
        g.ok(&["task", "list"])
            .as_array()
            .unwrap()
            .iter()
            .filter(|t| t["generated_from"]["source"] == "cit-effect")
            .count(),
        n
    );
}

/// BC-P2-24 failed tests: a recorded failing product-test family generates one repair task derived from the failing
/// run; a second failing run of the same streak generates nothing new.
#[test]
fn a_failing_product_test_family_generates_repair_work() {
    let (root, g) = fresh("ws5r3-ft");
    let pp_path = "governance/project/PROJECT_POLICY.yaml";
    let mut pp = yaml(&root, pp_path);
    pp["tests"] = json!({"families": {"unit": {"command": ["sh", "-c", "echo failing; exit 3"], "covers": ["src/**"]}}});
    write_yaml(&root, pp_path, &pp);
    git_commit_all(&root, "unit family");
    let r = g.run(&["verify", "product"]);
    assert_eq!(r.error_code(), "PRODUCT_TESTS_FAILED", "{}", r.envelope);
    let rec = r.details()["record"].as_str().unwrap().to_string();
    let gen = generated(&root);
    let ft = of_source(&gen, "failed-tests");
    assert_eq!(ft.len(), 1, "{gen:?}");
    assert_eq!(ft[0]["generation"]["subject"], "unit");
    assert_eq!(ft[0]["class"], "repair");
    assert!(ft[0]["derived_from"]
        .as_array()
        .unwrap()
        .contains(&json!(rec)));
    assert!(ft[0]["allowed_paths"].to_string().contains("src/**"));
    let _ = g.run(&["verify", "product"]);
    assert_eq!(of_source(&generated(&root), "failed-tests").len(), 1);
}

/// BC-P2-13 in-task half (Contract v3:446, :638-647): what a task changed is classified at its close, never by its
/// label. A material change completes only through change control (refused `MATERIAL_CHANGE_REQUIRES_CIT`, every
/// finding named); initial authoring of specification by specification work is not a change to existing
/// authority; product source may be changed by a class contracted to change it, not by a discovery task.
#[test]
fn material_changes_inside_a_task_complete_only_through_change_control() {
    let (root, g) = fresh("ws5r3-mat");
    write_yaml(
        &root,
        "spec/requirements/REQ-0700.yaml",
        &json!({"id": "REQ-0700", "type": "requirement", "title": "totals exact", "status": "ACTIVE", "kind": "functional", "acceptance_criteria": ["2 x 199 = 398"]}),
    );
    git_commit_all(&root, "spec");
    g.ok(&["rebuild-memory", "--incremental"]);
    // initial authoring by specification-producing work: a new acceptance obligation (for REQ-0700) written by
    // test-design work is not a change to existing authority
    let t2 = create(
        &g,
        "test-design",
        "design acceptance tests",
        "spec/**",
        json!({}),
    );
    let spec = g
        .with_role("independent-test-designer")
        .with_session("S-spec");
    spec.ok(&["task", "claim", &t2]);
    write_yaml(
        &root,
        "spec/tasks/TST-0701.yaml",
        &json!({"id": "TST-0701", "type": "test-obligation", "title": "totals acceptance", "status": "ACTIVE", "family": "acceptance", "tests": ["REQ-0700"], "test_path": "tests/totals.rs", "author_role": "independent-test-designer", "independent_of_implementer": true}),
    );
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = receipt(
        &spec,
        &root,
        &t2,
        "t2",
        "designed",
        &["spec/tasks/TST-0701.yaml"],
        "not_applicable_with_reason",
    );
    let c = spec.ok(&["task", "close", &t2, "--report", &rep]);
    assert!(
        c["material_changes_accepted"]
            .to_string()
            .contains("initial authoring"),
        "{c}"
    );
    // an existing acceptance criterion edited inside an ordinary task
    let t1 = create(
        &g,
        "documentation",
        "tidy spec",
        "spec/**,docs/**",
        json!({}),
    );
    g.ok(&["task", "claim", &t1]);
    let mut r = yaml(&root, "spec/requirements/REQ-0700.yaml");
    r["acceptance_criteria"] = json!(["totals may be approximate"]);
    write_yaml(&root, "spec/requirements/REQ-0700.yaml", &r);
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = receipt(
        &g,
        &root,
        &t1,
        "t1",
        "tidied",
        &["spec/requirements/REQ-0700.yaml"],
        "not_applicable_with_reason",
    );
    let e = g.err(&["task", "close", &t1, "--report", &rep]);
    assert_eq!(
        e.error_code(),
        "MATERIAL_CHANGE_REQUIRES_CIT",
        "{}",
        e.envelope
    );
    assert!(
        e.details()["refused"]
            .to_string()
            .contains("acceptance_criteria_change"),
        "{}",
        e.envelope
    );
    // the same edit of an existing test obligation, even by test-design work, is a change to existing authority
    let t5 = create(
        &g,
        "test-design",
        "revise acceptance tests",
        "spec/**",
        json!({}),
    );
    git(
        &root,
        &["checkout", "--", "spec/requirements/REQ-0700.yaml"],
    );
    g.ok(&["task", "release", &t1]);
    spec.ok(&["task", "claim", &t5]);
    let mut o = yaml(&root, "spec/tasks/TST-0701.yaml");
    o["test_path"] = json!("tests/other.rs");
    write_yaml(&root, "spec/tasks/TST-0701.yaml", &o);
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = receipt(
        &spec,
        &root,
        &t5,
        "t5",
        "revised",
        &["spec/tasks/TST-0701.yaml"],
        "not_applicable_with_reason",
    );
    let e = spec.err(&["task", "close", &t5, "--report", &rep]);
    assert_eq!(
        e.error_code(),
        "MATERIAL_CHANGE_REQUIRES_CIT",
        "{}",
        e.envelope
    );
    git(&root, &["checkout", "--", "spec/tasks/TST-0701.yaml"]);
    spec.ok(&["task", "release", &t5]);
    // product source written by a discovery task is outside its contract; by a refactor task it is not
    let t3 = create(&g, "discovery", "explore", "src/**", json!({}));
    g.ok(&["task", "claim", &t3]);
    write_file(&root, "src/extra.rs", "pub fn f() -> i64 { 1 }\n");
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = receipt(
        &g,
        &root,
        &t3,
        "t3",
        "explored",
        &["src/extra.rs"],
        "not_applicable_with_reason",
    );
    let e = g.err(&["task", "close", &t3, "--report", &rep]);
    assert_eq!(
        e.error_code(),
        "MATERIAL_CHANGE_REQUIRES_CIT",
        "{}",
        e.envelope
    );
    assert!(e.details()["refused"]
        .to_string()
        .contains("product source"));
    g.ok(&["task", "release", &t3]);
    let inputs = traceable_inputs(&root, "0710");
    git_commit_all(&root, "inputs");
    g.ok(&["rebuild-memory", "--incremental"]);
    let t4 = create(&g, "refactor", "refactor", "src/**", inputs);
    g.ok(&["task", "claim", &t4]);
    write_file(&root, "src/extra.rs", "pub fn f() -> i64 { 2 }\n");
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = receipt(
        &g,
        &root,
        &t4,
        "t4",
        "refactored",
        &["src/extra.rs"],
        "not_applicable_with_reason",
    );
    g.ok(&["task", "close", &t4, "--report", &rep]);
}

/// IP-R3-6 (WS-4 IP-3): a CIT executed inside a claim window covers an out-of-scope path only while the path's
/// content is exactly what the CIT wrote; a later edit of the same path is the worker's again.
#[test]
fn cit_coverage_is_bound_to_the_content_the_cit_wrote() {
    let (root, g) = fresh("ws5r3-cov");
    let t = create(&g, "documentation", "docs", "docs/**", json!({}));
    g.ok(&["task", "claim", &t]);
    let mf = root.join(".governance-runtime/mf.json");
    std::fs::write(&mf, json!([{"op": "write_file", "path": "notes/cit-written.md", "content": "written by the CIT\n"}]).to_string()).unwrap();
    let cit = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "add a note",
        "--trigger",
        "editorial",
        "--targets",
        "notes/cit-written.md",
        "--manifest",
        mf.to_str().unwrap(),
    ])["id"]
        .as_str()
        .unwrap()
        .to_string();
    g.ok(&["cit", "simulate", &cit]);
    g.with_role("change-controller")
        .ok(&["cit", "approve", &cit, "--method", "auto"]);
    g.with_role("change-controller")
        .ok(&["cit", "execute", &cit]);
    // edited after the CIT wrote it: no longer the CIT's governed change
    write_file(
        &root,
        "notes/cit-written.md",
        "written by the CIT, then edited by the worker\n",
    );
    write_file(&root, "docs/a.md", "a\n");
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = receipt(
        &g,
        &root,
        &t,
        "cov",
        "docs",
        &["docs/a.md"],
        "not_applicable_with_reason",
    );
    let e = g.err(&["task", "close", &t, "--report", &rep]);
    assert_eq!(e.error_code(), "MUTATION_SCOPE_VIOLATION", "{}", e.envelope);
    assert!(e.envelope.to_string().contains("notes/cit-written.md"));
    // as the CIT left it, it is covered
    write_file(&root, "notes/cit-written.md", "written by the CIT\n");
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = receipt(
        &g,
        &root,
        &t,
        "cov2",
        "docs",
        &["docs/a.md"],
        "not_applicable_with_reason",
    );
    g.ok(&["task", "close", &t, "--report", &rep]);
}

/// WS-4 R2-1/R2-2/R2-3 (BC-P2-04 close and pick side): an input changed outside change control shows as stale where
/// work is picked (DAG, list) before anyone propagates it; claiming propagates it (the work is marked for re-test,
/// which re-delivery acknowledges for work that has not started); for started work a re-test flag is cleared only by
/// re-test evidence against the changed inputs, and the close records the revalidated inputs.
#[test]
fn stale_inputs_are_seen_propagated_at_claim_and_cleared_only_by_retest_evidence() {
    let (root, g) = fresh("ws5r3-stale");
    let inputs = traceable_inputs(&root, "0720");
    git_commit_all(&root, "inputs");
    g.ok(&["rebuild-memory", "--incremental"]);
    let a = create(&g, "refactor", "work A", "src/a/**", inputs.clone());
    let b = create(&g, "refactor", "work B", "src/b/**", inputs.clone());
    g.ok(&["context", "compile", &a]);
    g.ok(&["context", "compile", &b]);
    // a direct change of the requirement both consumed, made outside change control while no work is claimed
    let rq = "spec/requirements/REQ-0720.yaml";
    let mut r = yaml(&root, rq);
    r["statement"] = json!("totals are integer cents, rounded half-even");
    write_yaml(&root, rq, &r);
    git_commit_all(&root, "direct change");
    // round 4 (P2-AR-0043, INT3-O2): a host-run index rebuild now propagates a direct change it observes (G1), so to
    // keep observing the claim-time propagation this test is about, the rebuild moves after the claim below (the DAG,
    // the list and the claim read the records, not the index)
    let reasons = g.ok(&["task", "dag"]).to_string();
    assert!(
        reasons.contains("changed since this task's work consumed them"),
        "{reasons}"
    );
    let list = g.ok(&["task", "list"]);
    assert!(list.to_string().contains("REQ-0720"), "{list}");
    // claiming propagates the change first: the work is marked for re-test and so not runnable as delivered
    let c = g.run(&["task", "claim", &b]);
    assert_eq!(c.error_code(), "TASK_NOT_RUNNABLE", "{}", c.envelope);
    assert!(c.envelope.to_string().contains("retest"), "{}", c.envelope);
    assert_eq!(g.ok(&["task", "show", &a])["retest_required"], true);
    // the index catches up after the claim propagated (nothing left for the rebuild to propagate)
    let rb = g.ok(&["rebuild-memory", "--incremental"]);
    assert_ne!(rb["upstream_changes"]["propagated"], true, "{rb}");
    // work that never started re-delivers its context at the current inputs, which acknowledges the change
    g.ok(&["context", "compile", &b]);
    g.ok(&["task", "claim", &b]);
    // an upstream change reaching started work (through change control, inside its claim window) is re-tested
    let mf = root.join(".governance-runtime/mf-stale.json");
    std::fs::write(
        &mf,
        json!([{"op": "set_field", "target": "REQ-0720", "field": "statement", "value": "totals are integer cents, rounded half-up"}]).to_string(),
    )
    .unwrap();
    let cit = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "change rounding",
        "--trigger",
        "behaviour_change",
        "--targets",
        "REQ-0720",
        "--manifest",
        mf.to_str().unwrap(),
    ])["id"]
        .as_str()
        .unwrap()
        .to_string();
    let sim = g.ok(&["cit", "simulate", &cit]);
    let gate = sim["human_gate"].as_str().unwrap().to_string();
    crate::ws03::human_decide(&g, &gate, "A");
    g.ok(&["cit", "approve", &cit, "--by", "owner", "--method", "human"]);
    g.ok(&["cit", "execute", &cit]);
    assert_eq!(g.ok(&["task", "show", &b])["retest_required"], true);
    write_file(&root, "src/b/x.rs", "pub fn x() {}\n");
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = receipt(
        &g,
        &root,
        &b,
        "b1",
        "work",
        &["src/b/x.rs"],
        "not_applicable_with_reason",
    );
    let e = g.err(&["task", "close", &b, "--report", &rep]);
    assert_eq!(e.error_code(), "RETEST_EVIDENCE_REQUIRED", "{}", e.envelope);
    let rep = receipt_with(
        &g,
        &root,
        &b,
        "b2",
        "work",
        &["src/b/x.rs"],
        "not_applicable_with_reason",
        json!({"retest": {"inputs": ["REQ-0720"], "status": "passed", "evidence": "re-ran the unit family against the changed requirement"}}),
    );
    let done = g.ok(&["task", "close", &b, "--report", &rep]);
    assert!(
        done["revalidated_inputs"].to_string().contains("REQ-0720"),
        "{done}"
    );
    let bt = g.ok(&["task", "show", &b]);
    assert_eq!(bt["retest_required"], false);
    assert_eq!(bt["staleness"]["stale"], false, "{bt}");
}

/// WS-10 IP-WS10-11 (Contract v3 J2): an experiment task closes only when it is linked to an OS-written experiment
/// record with a recorded run; an L3 `--force` close records the override.
#[test]
fn an_experiment_task_closes_only_through_its_lifecycle() {
    let (root, g) = fresh("ws5r3-exp");
    let t = create(
        &g,
        "experiment",
        "try a faster summation",
        "spec/experiments/**",
        json!({}),
    );
    g.ok(&["task", "claim", &t]);
    write_file(&root, "spec/experiments/notes.md", "tried it\n");
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = receipt(
        &g,
        &root,
        &t,
        "exp",
        "experimented",
        &["spec/experiments/notes.md"],
        "not_applicable_with_reason",
    );
    let e = g.err(&["task", "close", &t, "--report", &rep]);
    assert_eq!(
        e.error_code(),
        "EXPERIMENT_LIFECYCLE_REQUIRED",
        "{}",
        e.envelope
    );
    let f = g.ok(&["task", "close", &t, "--report", &rep, "--force"]);
    assert!(
        f["overrides"].to_string().contains("experiment_lifecycle"),
        "{f}"
    );
}

/// BC-P2-31: the claims store and claim baselines live at their state location (`.governance-state/`), outside every
/// directory the product classifies derived; deleting the derived runtime directory keeps the claim live and the
/// claimed work closable against its sealed baseline.
#[test]
fn claims_and_claim_baselines_survive_deleting_the_derived_runtime() {
    let (root, g) = fresh("ws5r3-state");
    let t = create(&g, "documentation", "docs", "docs/**", json!({}));
    g.ok(&["task", "claim", &t]);
    assert!(exists(&root, ".governance-state/claims.db"));
    assert!(exists(
        &root,
        &format!(".governance-state/tasks/{t}/claim-tree.json")
    ));
    assert!(!exists(&root, ".governance-runtime/claims.db"));
    assert_eq!(
        git(&root, &["status", "--porcelain", ".governance-state"]).1,
        "",
        "state is self-ignored"
    );
    std::fs::remove_dir_all(root.join(".governance-runtime")).unwrap();
    g.ok(&["rebuild-memory"]);
    let other = g.with_session("S-other").run(&["task", "claim", &t]);
    assert_eq!(other.error_code(), "TASK_CLAIMED", "{}", other.envelope);
    write_file(&root, "docs/b.md", "b\n");
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = receipt(
        &g,
        &root,
        &t,
        "st",
        "docs",
        &["docs/b.md"],
        "not_applicable_with_reason",
    );
    let c = g.ok(&["task", "close", &t, "--report", &rep]);
    assert_eq!(c["task_status"], "DONE");
}
