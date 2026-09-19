use serde_json::Value;
use std::fmt;

/// Governance error with a stable machine-readable code (surfaced through the CLI JSON envelope, API-0002).
#[derive(Debug, Clone)]
pub struct GovError {
    pub code: String,
    pub message: String,
    pub details: Value,
}

impl GovError {
    pub fn new(code: &str, message: impl Into<String>) -> Self {
        GovError {
            code: code.to_string(),
            message: message.into(),
            details: Value::Null,
        }
    }
    pub fn with_details(mut self, details: Value) -> Self {
        self.details = details;
        self
    }
    pub fn io(context: &str, e: std::io::Error) -> Self {
        GovError::new("IO_ERROR", format!("{context}: {e}"))
    }
    /// Exit code class per API-0002.
    pub fn exit_code(&self) -> i32 {
        match self.code.as_str() {
            "USAGE" => 2,
            "VERIFICATION_FAILED" | "UNHEALTHY" | "SCHEMA_INVALID" => 3,
            "BLOCKED_BY_CONTROL"
            | "HUMAN_GATE_REQUIRED"
            | "VERDICT_REQUIRED"
            | "FROZEN"
            | "PAUSED"
            // a governed operation refused by an active health hard-block (scheduler G0 guard), or a remedy that
            // did not clear the block it was admitted under, is the same "blocked" class as emergency controls and
            // unanswered gates (API-0002; IP-WS02-10)
            | "HEALTH_HARD_BLOCK"
            | "HEALTH_REMEDY_INCOMPLETE"
            // blocked by a Human Decision Gate (API-0002 exit 4 "blocked by ... human gate"; WS-5 IP-R3-7): the
            // work's governing gate does not authorise it, is not answered yet, or was declined
            | "GATE_NOT_AUTHORISED"
            | "GATE_NOT_ANSWERED"
            | "GATE_DECLINED" => 4,
            _ => 1,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn blocked_class_codes_exit_4() {
        for c in [
            "FROZEN",
            "PAUSED",
            "HUMAN_GATE_REQUIRED",
            "HEALTH_HARD_BLOCK",
            "HEALTH_REMEDY_INCOMPLETE",
            "GATE_NOT_AUTHORISED",
            "GATE_NOT_ANSWERED",
            "GATE_DECLINED",
        ] {
            assert_eq!(GovError::new(c, "x").exit_code(), 4, "{c}");
        }
        // governance errors that are not a control-state or human-gate block stay in class 1
        for c in [
            "TASK_NOT_READY",
            "CLAIM_BASELINE_UNBOUND",
            "RECEIPT_INVALID",
        ] {
            assert_eq!(GovError::new(c, "x").exit_code(), 1, "{c}");
        }
    }
}

impl fmt::Display for GovError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[{}] {}", self.code, self.message)
    }
}

impl std::error::Error for GovError {}

impl From<std::io::Error> for GovError {
    fn from(e: std::io::Error) -> Self {
        GovError::new("IO_ERROR", e.to_string())
    }
}
impl From<serde_json::Error> for GovError {
    fn from(e: serde_json::Error) -> Self {
        GovError::new("JSON_ERROR", e.to_string())
    }
}
impl From<serde_yaml::Error> for GovError {
    fn from(e: serde_yaml::Error) -> Self {
        GovError::new("YAML_ERROR", e.to_string())
    }
}
impl From<rusqlite::Error> for GovError {
    fn from(e: rusqlite::Error) -> Self {
        GovError::new("DB_ERROR", e.to_string())
    }
}

pub type Result<T> = std::result::Result<T, GovError>;

#[macro_export]
macro_rules! bail {
    ($code:expr, $($arg:tt)*) => { return Err($crate::GovError::new($code, format!($($arg)*))) };
}
