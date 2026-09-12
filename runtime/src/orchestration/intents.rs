//! Natural-language intent routing (framework §33): deterministic T0 patterns from the kernel command contract.
use crate::records::RecordStore;
use crate::util::read_yaml;
use crate::{Project, Result};
use serde_json::{json, Value};

pub fn route(p: &Project, text: &str) -> Result<Value> {
    let contract = read_yaml(
        &p.kernel_dir()
            .join("commands")
            .join("COMMAND_CONTRACT.yaml"),
    )?;
    let low = text.to_lowercase();
    let mut best: Option<(usize, Value)> = None;
    for ip in contract["intent_patterns"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        let score = ip["patterns"]
            .as_array()
            .map(|a| {
                a.iter()
                    .filter(|pat| low.contains(pat.as_str().unwrap_or("\u{0}")))
                    .map(|pat| pat.as_str().unwrap_or("").len())
                    .max()
                    .unwrap_or(0)
            })
            .unwrap_or(0);
        if score > 0 && best.as_ref().map(|b| score > b.0).unwrap_or(true) {
            best = Some((score, ip));
        }
    }
    let Some((_, ip)) = best else {
        return Ok(
            json!({"intent": "UNKNOWN", "text": text, "plan": [], "suggestion": "Try: status, continue, discover <topic>, approve, reject, pause, audit"}),
        );
    };
    let intent = ip["intent"].as_str().unwrap_or("UNKNOWN").to_string();
    let mut commands: Vec<String> = vec![];
    let store = RecordStore::load(&p.root);
    let pending_cit = store
        .of_type("cit")
        .into_iter()
        .filter(|c| c.get("cit_status") == "SIMULATED")
        .map(|c| c.id())
        .next_back();
    let pending_gate = store
        .of_type("human-gate")
        .into_iter()
        .filter(|g| matches!(g.get("gate_status").as_str(), "PENDING" | "PRESENTED"))
        .map(|g| g.id())
        .next();
    match intent.as_str() {
        "DISCOVER" => {
            commands.push(format!(
                "gov task create --class discovery --objective \"{}\"",
                text.replace('"', "'")
            ));
            commands.push("gov cit propose ... && gov cit simulate <CIT>".into());
        }
        "APPROVE" => {
            if let Some(g) = &pending_gate {
                commands.push(format!("gov decide {g} --option <id>"));
            }
            if let Some(c) = &pending_cit {
                commands.push(format!("gov cit approve {c} --by human"));
                commands.push(format!("gov cit execute {c}"));
            }
            commands.push("gov continue".into());
        }
        "REJECT" => {
            if let Some(c) = &pending_cit {
                commands.push(format!("gov cit reject {c} --by human"));
            }
        }
        "STATUS" => commands.push("gov status".into()),
        "CONTINUE" => commands.push("gov continue".into()),
        "PAUSE" => commands.push("gov pause".into()),
        "FREEZE" => commands.push("gov freeze-writes".into()),
        "ROLLBACK" => commands.push("gov cit rollback <CIT>".into()),
        "AUDIT" => commands.push("gov audit".into()),
        "DECIDE" => {
            if let Some(g) = &pending_gate {
                commands.push(format!("gov decide {g} --option <id>"));
            }
        }
        _ => {}
    }
    Ok(
        json!({"intent": intent, "text": text, "plan": ip["plan"], "commands": commands, "pending_cit": pending_cit, "pending_gate": pending_gate}),
    )
}
