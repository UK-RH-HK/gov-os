//! Skill registry: kernel skills (framework/skills) + project skills (governance/project/skills).
use crate::util::read_yaml;
use crate::{Project, Result};
use serde_json::{json, Value};

pub fn list_skills(p: &Project) -> Vec<Value> {
    let mut out = vec![];
    for (dir, source) in [
        (p.kernel_dir().join("skills"), "kernel"),
        (p.overlay_dir().join("skills"), "project"),
    ] {
        let Ok(rd) = std::fs::read_dir(&dir) else {
            continue;
        };
        let mut paths: Vec<_> = rd
            .filter_map(|e| e.ok())
            .map(|e| e.path())
            .filter(|x| x.extension().map(|e| e == "yaml").unwrap_or(false))
            .collect();
        paths.sort();
        for path in paths {
            if let Ok(mut v) = read_yaml(&path) {
                v["_source"] = json!(source);
                v["_path"] = json!(path
                    .strip_prefix(&p.root)
                    .unwrap_or(&path)
                    .to_string_lossy());
                out.push(v);
            }
        }
    }
    out
}

pub fn find_skill(p: &Project, id: &str) -> Option<Value> {
    list_skills(p)
        .into_iter()
        .find(|s| s["id"].as_str() == Some(id))
}

/// Resolve skills for a task: by required_skills, else by task class + role.
pub fn resolve(p: &Project, task: &Value) -> Result<Value> {
    let skills = list_skills(p);
    let required: Vec<String> = task
        .get("required_skills")
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    let class = task
        .get("class")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    let role = task
        .get("role")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    let mut resolved = vec![];
    let mut missing = vec![];
    for r in &required {
        match skills
            .iter()
            .find(|s| s["id"].as_str() == Some(r) && s["status"].as_str() == Some("ACTIVE"))
        {
            Some(s) => resolved
                .push(json!({"id": s["id"], "version": s["version"], "source": s["_source"]})),
            None => missing.push(r.clone()),
        }
    }
    let candidates: Vec<Value> = skills
        .iter()
        .filter(|s| {
            s["status"].as_str() == Some("ACTIVE")
                && s["task_classes"]
                    .as_array()
                    .map(|a| a.iter().any(|c| c.as_str() == Some(&class)))
                    .unwrap_or(false)
                && (role.is_empty()
                    || s["roles"]
                        .as_array()
                        .map(|a| {
                            a.iter()
                                .any(|c| c.as_str() == Some(&role) || c.as_str() == Some("all"))
                        })
                        .unwrap_or(false))
        })
        .map(|s| json!({"id": s["id"], "version": s["version"], "source": s["_source"]}))
        .collect();
    Ok(
        json!({"task": task["id"], "resolved": resolved, "missing": missing, "candidates_by_class_role": candidates, "capability_gap": !missing.is_empty()}),
    )
}

pub fn validate_all(p: &Project) -> Vec<String> {
    let mut problems = vec![];
    for s in list_skills(p) {
        let id = s["id"].as_str().unwrap_or("?").to_string();
        if let Ok(errs) = p.schemas().errors("skill", &s) {
            for e in errs.iter().take(3) {
                problems.push(format!("{id}: {e}"));
            }
        }
        if s["validation_scenarios"]
            .as_array()
            .map(|a| a.is_empty())
            .unwrap_or(true)
        {
            problems.push(format!("{id}: no validation scenarios"));
        }
    }
    problems
}
