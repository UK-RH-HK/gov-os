//! Derived runtime store (SQLite + FTS5). Never authoritative; always rebuildable from Git + records.
use crate::Result;
use rusqlite::{params, Connection, OptionalExtension};
use serde_json::{json, Map, Value};
use std::path::Path;

pub const SCHEMA: &str = r#"
CREATE TABLE IF NOT EXISTS artifacts (
  artifact_id TEXT PRIMARY KEY, path TEXT UNIQUE NOT NULL, record_type TEXT, title TEXT, status TEXT, state_class TEXT,
  namespace TEXT, sensitivity TEXT, path_class TEXT, content_hash TEXT, repo_commit TEXT, index_version TEXT,
  size INTEGER, indexed_at TEXT, data_json TEXT, semantic INTEGER, lexical INTEGER, graph INTEGER, code INTEGER,
  default_retrieval INTEGER DEFAULT 1, superseded_by TEXT);
CREATE TABLE IF NOT EXISTS chunks (
  chunk_id TEXT PRIMARY KEY, artifact_id TEXT NOT NULL, parent_chunk_id TEXT, level TEXT, section TEXT, ordinal INTEGER,
  content_hash TEXT, text TEXT, chars INTEGER, lexical INTEGER DEFAULT 1, semantic INTEGER DEFAULT 1);
CREATE INDEX IF NOT EXISTS idx_chunks_artifact ON chunks(artifact_id);
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(text, chunk_id UNINDEXED, artifact_id UNINDEXED, tokenize='__TOKENIZER__');
CREATE TABLE IF NOT EXISTS vectors (chunk_id TEXT PRIMARY KEY, artifact_id TEXT, embedder TEXT, dim INTEGER, vec TEXT);
CREATE INDEX IF NOT EXISTS idx_vectors_artifact ON vectors(artifact_id);
CREATE TABLE IF NOT EXISTS edges (src TEXT, type TEXT, dst TEXT, source_artifact TEXT, provenance TEXT, PRIMARY KEY (src, type, dst, source_artifact));
CREATE INDEX IF NOT EXISTS idx_edges_dst ON edges(dst);
CREATE TABLE IF NOT EXISTS symbols (symbol_id TEXT PRIMARY KEY, artifact_id TEXT, path TEXT, name TEXT, qualname TEXT, kind TEXT,
  lineno INTEGER, end_lineno INTEGER, parent TEXT, signature TEXT, language TEXT, provider TEXT);
CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(name);
CREATE TABLE IF NOT EXISTS symbol_refs (path TEXT, name TEXT, kind TEXT, lineno INTEGER, target TEXT);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS retrieval_log (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, query TEXT, routes TEXT, hits TEXT, latency_ms REAL);
CREATE TABLE IF NOT EXISTS excluded (path TEXT PRIMARY KEY, reason TEXT, detail TEXT);
CREATE TABLE IF NOT EXISTS capability (key TEXT PRIMARY KEY, value TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS derivation (path TEXT PRIMARY KEY, artifact_id TEXT, key TEXT);
"#;

pub struct RuntimeDb {
    pub conn: Connection,
}

pub fn row_to_json(row: &rusqlite::Row, cols: &[String]) -> Value {
    let mut m = Map::new();
    for (i, c) in cols.iter().enumerate() {
        let v: Value = match row.get_ref(i) {
            Ok(rusqlite::types::ValueRef::Null) => Value::Null,
            Ok(rusqlite::types::ValueRef::Integer(n)) => json!(n),
            Ok(rusqlite::types::ValueRef::Real(f)) => json!(f),
            Ok(rusqlite::types::ValueRef::Text(t)) => {
                Value::String(String::from_utf8_lossy(t).to_string())
            }
            Ok(rusqlite::types::ValueRef::Blob(b)) => {
                Value::String(format!("<blob {} bytes>", b.len()))
            }
            Err(_) => Value::Null,
        };
        m.insert(c.clone(), v);
    }
    Value::Object(m)
}

impl RuntimeDb {
    pub fn open(path: &Path) -> Result<Self> {
        if let Some(p) = path.parent() {
            std::fs::create_dir_all(p)?;
        }
        let conn = Connection::open(path)?;
        conn.execute_batch("PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;")?;
        Ok(RuntimeDb { conn })
    }
    pub fn open_memory() -> Result<Self> {
        let db = RuntimeDb {
            conn: Connection::open_in_memory()?,
        };
        db.init_schema()?;
        Ok(db)
    }
    pub fn init_schema(&self) -> Result<()> {
        self.init_schema_with("unicode61")
    }
    /// Create the schema; the FTS5 tokenizer is part of the lexical pin (MEMORY_POLICY.lexical.tokenizer).
    pub fn init_schema_with(&self, tokenizer: &str) -> Result<()> {
        let safe: String = tokenizer
            .chars()
            .filter(|c| c.is_ascii_alphanumeric() || *c == ' ' || *c == '_')
            .collect();
        self.conn.execute_batch(&SCHEMA.replace(
            "__TOKENIZER__",
            if safe.is_empty() { "unicode61" } else { &safe },
        ))?;
        Ok(())
    }
    pub fn integrity_ok(&self) -> bool {
        self.conn
            .query_row("PRAGMA integrity_check", [], |r| r.get::<_, String>(0))
            .map(|s| s == "ok")
            .unwrap_or(false)
    }
    pub fn has_schema(&self) -> bool {
        self.conn
            .query_row(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='artifacts'",
                [],
                |r| r.get::<_, i64>(0),
            )
            .map(|n| n > 0)
            .unwrap_or(false)
    }
    pub fn query(&self, sql: &str, params: &[&dyn rusqlite::ToSql]) -> Result<Vec<Value>> {
        let mut stmt = self.conn.prepare(sql)?;
        let cols: Vec<String> = stmt.column_names().iter().map(|s| s.to_string()).collect();
        let rows = stmt.query_map(params, |row| Ok(row_to_json(row, &cols)))?;
        let mut out = vec![];
        for r in rows {
            out.push(r?);
        }
        Ok(out)
    }
    pub fn query_one(&self, sql: &str, params: &[&dyn rusqlite::ToSql]) -> Result<Option<Value>> {
        Ok(self.query(sql, params)?.into_iter().next())
    }
    pub fn exec(&self, sql: &str, params: &[&dyn rusqlite::ToSql]) -> Result<usize> {
        Ok(self.conn.execute(sql, params)?)
    }
    pub fn count(&self, table: &str) -> i64 {
        self.conn
            .query_row(&format!("SELECT COUNT(*) FROM {table}"), [], |r| r.get(0))
            .unwrap_or(0)
    }
    pub fn counts(&self) -> Value {
        let mut m = Map::new();
        for t in [
            "artifacts",
            "chunks",
            "vectors",
            "edges",
            "symbols",
            "symbol_refs",
            "excluded",
        ] {
            m.insert(t.into(), json!(self.count(t)));
        }
        Value::Object(m)
    }
    pub fn get_meta(&self, key: &str) -> Option<Value> {
        self.conn
            .query_row("SELECT value FROM meta WHERE key=?1", params![key], |r| {
                r.get::<_, String>(0)
            })
            .optional()
            .ok()
            .flatten()
            .and_then(|s| serde_json::from_str(&s).ok())
    }
    pub fn set_meta(&self, key: &str, value: &Value) -> Result<()> {
        self.conn.execute(
            "INSERT OR REPLACE INTO meta(key,value) VALUES (?1,?2)",
            params![key, serde_json::to_string(value)?],
        )?;
        Ok(())
    }
    pub fn delete_artifact(&self, artifact_id: &str) -> Result<()> {
        let path: Option<String> = self
            .conn
            .query_row(
                "SELECT path FROM artifacts WHERE artifact_id=?1",
                params![artifact_id],
                |r| r.get(0),
            )
            .optional()?;
        self.conn.execute(
            "DELETE FROM chunks_fts WHERE artifact_id=?1",
            params![artifact_id],
        )?;
        self.conn.execute(
            "DELETE FROM vectors WHERE artifact_id=?1",
            params![artifact_id],
        )?;
        self.conn.execute(
            "DELETE FROM chunks WHERE artifact_id=?1",
            params![artifact_id],
        )?;
        self.conn.execute(
            "DELETE FROM edges WHERE source_artifact=?1",
            params![artifact_id],
        )?;
        if let Some(p) = path {
            self.conn
                .execute("DELETE FROM symbols WHERE path=?1", params![p])?;
            self.conn
                .execute("DELETE FROM symbol_refs WHERE path=?1", params![p])?;
            self.conn
                .execute("DELETE FROM derivation WHERE path=?1", params![p])?;
        }
        self.conn.execute(
            "DELETE FROM artifacts WHERE artifact_id=?1",
            params![artifact_id],
        )?;
        Ok(())
    }
    pub fn clear_index(&self) -> Result<()> {
        for t in [
            "chunks_fts",
            "vectors",
            "chunks",
            "edges",
            "symbols",
            "symbol_refs",
            "artifacts",
            "excluded",
            "derivation",
        ] {
            self.conn.execute(&format!("DELETE FROM {t}"), [])?;
        }
        Ok(())
    }
    pub fn artifact(&self, id: &str) -> Result<Option<Value>> {
        self.query_one("SELECT * FROM artifacts WHERE artifact_id=?1", &[&id])
    }
    pub fn artifact_by_path(&self, path: &str) -> Result<Option<Value>> {
        self.query_one("SELECT * FROM artifacts WHERE path=?1", &[&path])
    }
    pub fn artifact_ids(&self) -> Result<std::collections::HashSet<String>> {
        Ok(self
            .query("SELECT artifact_id FROM artifacts", &[])?
            .into_iter()
            .filter_map(|v| {
                v.get("artifact_id")
                    .and_then(|x| x.as_str())
                    .map(|s| s.to_string())
            })
            .collect())
    }
    pub fn begin(&self) -> Result<()> {
        self.conn.execute_batch("BEGIN")?;
        Ok(())
    }
    pub fn commit(&self) -> Result<()> {
        self.conn.execute_batch("COMMIT")?;
        Ok(())
    }
}
