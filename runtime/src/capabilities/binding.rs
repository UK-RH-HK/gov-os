//! # What a plugin execution is, and which bytes it runs (BC-P2-39, BC-P2-40)
//!
//! ## Execution class — elevation is never decided by the descriptor (BC-P2-39; Contract v3 F4:426, :430; ARCH-0003 §9)
//!
//! The host spawns a plugin as an ordinary child process of the invoking account ([`super::host::invoke`]). The OS has
//! no run-time mechanism that confines what such a process does: `permissions: {network: false,
//! filesystem_write: false}` and `required_permission_classes` are *declarations*, and nothing enforces them. A
//! mechanism that could (an OS sandbox: namespaces, seccomp, Landlock, a container runtime) would be a new external
//! dependency class and needs owner adoption (synthesis `owner-decisions-required.md` row 2); it is not chosen here.
//!
//! Therefore the OS classifies every plugin by **what it actually executes**, never by what it declares:
//!
//! | [`ExecutionClass`] | what runs | can it exceed the non-elevated floor? | what execution requires |
//! |---|---|---|---|
//! | `OsProvided` | this very `gov` binary (same file, or byte-identical) serving one of [`OS_CAPABILITY_SERVERS`] — code the verified release wrote, which reads one request on stdin and writes one response on stdout | no: its effects are the release's own, known and bounded | the authority floor and the role checks (D-0005 consequence 3's hand-declared allowance survives here) |
//! | `Executable` | anything else: a script, an interpreter with a module or inline code, a binary | **yes, whatever the descriptor says** | an OS-written (T2-verified) registration **and** a presented, owner-answered gate raised for exactly that plugin identity, version, implementation and permission set, re-verified at every execution |
//!
//! Declared permissions still matter, but only in the direction that cannot widen anything: the acting role must hold
//! every declared permission class, and the declarations are shown to the human who decides the registration gate.
//!
//! ## Implementation binding (BC-P2-40; Contract v3 F4:428-429)
//!
//! [`resolve`] derives, from the command vector alone, every file the execution loads by name and hashes each one:
//!
//! * the **program** (`command[0]`, resolved through `PATH` exactly as `exec` resolves it, symlinks followed): the
//!   interpreter or binary that runs;
//! * every **argument** that names an existing file (a script, a config the program is handed);
//! * for the Python **module form** (`python3 [opts] -m pkg.mod`), the whole top-level package the interpreter would
//!   import, found by asking the interpreter for its search path from the plugin's working directory and applying
//!   Python's own finder order (regular package, then module file, then namespace portions) — including
//!   `__pycache__`, because a planted byte-code file with a matching source stamp is loaded instead of the source;
//! * every path the descriptor lists under `implementation:` (helper modules the entry point loads from elsewhere),
//!   and under `model.artefacts` / `runtime.artefacts` (the model an embed/rerank plugin loads and the inference
//!   runtime it runs on, IP-R2-13: [`declared_paths`]) — so the component identity of the retrieval profile
//!   (BC-P2-30) is identity of bytes the registration approved;
//! * inline code (`sh -c '<code>'`, `python3 -c '<code>'`) lives in the descriptor, whose bytes the registration binds.
//!
//! A symlink inside a bound tree binds where it points *and* the bytes it resolves to; a symlinked directory is
//! followed. Digests are recomputed at every authorisation unless the pin cache proves the bytes cannot have changed
//! since they were hashed ([`super::pincache`]; [`content_sha256`]).
//!
//! A command whose implementation cannot be located (a module the interpreter cannot find, a declared path that does
//! not exist, an unresolvable program) is refused, typed: nothing unbound ever runs.
//!
//! The environment a plugin inherits could otherwise substitute code without touching a bound byte (`PYTHONPATH`
//! shadowing, a `sitecustomize` injected through it, `NODE_OPTIONS=--require`, `LD_PRELOAD`, `BASH_ENV`): the host
//! removes [`LOADER_ENV_VARS`] from the plugin's environment ([`apply_plugin_env`]), and module resolution runs under
//! the same environment. `PYTHONDONTWRITEBYTECODE=1` keeps an execution from changing the bytes it is bound to.
//!
//! **Stated limit.** Code an implementation reads and evaluates from a location it does not name (a script that
//! `eval`s an arbitrary file, a module that imports a sibling it is not packaged with) is outside what a static
//! reading of the command can find. The registration gate shows the approver the exact bound file set, and the
//! descriptor's `implementation:` list is the way to bring such code inside the binding.
use super::protocol::PluginDescriptor;
use crate::util::{canonical_json, sha256_hex};
use crate::{GovError, Result};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::sync::{Mutex, OnceLock};

/// OS capability servers: `gov` subcommands whose whole behaviour is "read one gov-capability/1 request from stdin,
/// write one response to stdout, exit" (they open no project and write nothing). `(subcommand words, flags without a
/// value, flags taking a value)`. A command vector that runs this binary with anything else is `Executable`.
pub const OS_CAPABILITY_SERVERS: &[(&[&str], &[&str], &[&str])] =
    &[(&["capabilities", "serve-embed"], &["--reverse"], &["--id"])];

/// Environment variables through which a caller could make an interpreter or the dynamic loader run code that is not
/// the plugin's bound implementation. Removed from every plugin execution and from module resolution.
pub const LOADER_ENV_VARS: &[&str] = &[
    "PYTHONPATH",
    "PYTHONHOME",
    "PYTHONSTARTUP",
    "PYTHONUSERBASE",
    "PYTHONINSPECT",
    "PYTHONPYCACHEPREFIX",
    "PYTHONSAFEPATH",
    "PYTHONPLATLIBDIR",
    "PYTHONEXECUTABLE",
    "PYTHONWARNINGS",
    "PYTHONBREAKPOINT",
    "NODE_OPTIONS",
    "NODE_PATH",
    "PERL5LIB",
    "PERLLIB",
    "PERL5OPT",
    "RUBYLIB",
    "RUBYOPT",
    "LD_PRELOAD",
    "LD_LIBRARY_PATH",
    "LD_AUDIT",
    "DYLD_INSERT_LIBRARIES",
    "DYLD_LIBRARY_PATH",
    "DYLD_FRAMEWORK_PATH",
    "BASH_ENV",
    "ENV",
    "JAVA_TOOL_OPTIONS",
    "_JAVA_OPTIONS",
    "JDK_JAVA_OPTIONS",
    "CLASSPATH",
];

/// Bound on the files one implementation may comprise (a module tree larger than this is refused, not truncated).
const MAX_BOUND_FILES: usize = 20_000;

/// Descriptor fields that are requests or OS-written copies, never part of what a registration approves.
const NON_SUBJECT_FIELDS: &[&str] = &["provenance", "registration_gate", "pin", "status"];

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ExecutionClass {
    /// This `gov` binary serving one of [`OS_CAPABILITY_SERVERS`]: non-elevated by construction.
    OsProvided,
    /// Anything else: an unsandboxed process that can exceed the non-elevated floor whatever it declares.
    Executable,
}

impl ExecutionClass {
    pub fn as_str(&self) -> &'static str {
        match self {
            ExecutionClass::OsProvided => "OS_PROVIDED",
            ExecutionClass::Executable => "EXECUTABLE",
        }
    }
}

/// One bound file: why it is bound, where it is (project-relative when inside the project), and its content hash.
#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize)]
pub struct BoundFile {
    pub role: String,
    pub path: String,
    pub sha256: String,
}

/// The implementation a plugin's command executes, as the OS derived it.
#[derive(Debug, Clone, serde::Serialize)]
pub struct Implementation {
    #[serde(serialize_with = "ser_class")]
    pub class: ExecutionClass,
    /// The resolved program (absolute, symlinks followed).
    pub program: String,
    pub files: Vec<BoundFile>,
    /// sha256 over the sorted `(path, sha256)` list: the implementation identity a registration binds.
    pub sha256: String,
    /// Where the plugin's own code lives (module package, script, or the program): the location `SRR-R0-L6` classifies.
    #[serde(skip)]
    pub primary: Option<PathBuf>,
}

fn ser_class<S: serde::Serializer>(
    c: &ExecutionClass,
    s: S,
) -> std::result::Result<S::Ok, S::Error> {
    s.serialize_str(c.as_str())
}

impl Implementation {
    pub fn to_value(&self) -> Value {
        json!({"execution_class": self.class.as_str(), "program": self.program, "sha256": self.sha256, "files": self.files})
    }
    pub fn paths(&self) -> Vec<String> {
        self.files.iter().map(|f| f.path.clone()).collect()
    }
}

fn unresolved(desc: &PluginDescriptor, why: String) -> GovError {
    GovError::new(
        "PLUGIN_IMPLEMENTATION_UNRESOLVED",
        format!(
            "plugin '{}': {why}. The OS binds every byte a plugin executes (Contract v3 F4:428); an implementation it \
             cannot locate is never run. Fix the command, or list the implementation's files under `implementation:`.",
            desc.plugin_id
        ),
    )
    .with_details(json!({"plugin_id": desc.plugin_id, "command": desc.command}))
}

/// Remove the loader-controlling variables from a plugin's environment ([`LOADER_ENV_VARS`]) and keep an execution
/// from writing byte-code into its own bound tree.
pub fn apply_plugin_env(cmd: &mut std::process::Command) {
    for v in LOADER_ENV_VARS {
        cmd.env_remove(v);
    }
    cmd.env("PYTHONDONTWRITEBYTECODE", "1");
}

/// The command vector with `{project_root}` / `{plugin_dir}` substituted (exactly what the host executes).
pub fn substituted_command(desc: &PluginDescriptor, root: &Path) -> Vec<String> {
    let plugin_dir = Path::new(&desc.source)
        .parent()
        .map(|p| p.to_string_lossy().to_string())
        .unwrap_or_default();
    desc.command
        .iter()
        .map(|c| {
            c.replace("{project_root}", &root.to_string_lossy())
                .replace("{plugin_dir}", &plugin_dir)
        })
        .collect()
}

/// The working directory the host runs the plugin in.
pub fn working_dir(desc: &PluginDescriptor, root: &Path) -> PathBuf {
    desc.cwd
        .as_ref()
        .map(|c| root.join(c))
        .unwrap_or_else(|| root.to_path_buf())
}

fn under(p: &Path, dir: &Path) -> Option<PathBuf> {
    let d = dir.canonicalize().unwrap_or_else(|_| dir.to_path_buf());
    p.strip_prefix(&d).ok().map(|r| r.to_path_buf())
}

fn display(p: &Path, root: &Path) -> String {
    match under(p, root) {
        Some(r) => r.to_string_lossy().replace('\\', "/"),
        None => p.to_string_lossy().to_string(),
    }
}

fn is_executable_file(p: &Path) -> bool {
    let Ok(m) = std::fs::metadata(p) else {
        return false;
    };
    if !m.is_file() {
        return false;
    }
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        m.permissions().mode() & 0o111 != 0
    }
    #[cfg(not(unix))]
    {
        true
    }
}

/// Resolve `command[0]` the way `exec` does: a name containing `/` is a path (relative to the working directory);
/// a bare name is searched on `PATH`.
pub fn resolve_program(program: &str, cwd: &Path) -> Option<PathBuf> {
    let found = if program.contains('/') {
        let p = if Path::new(program).is_absolute() {
            PathBuf::from(program)
        } else {
            cwd.join(program)
        };
        p.is_file().then_some(p)
    } else {
        let path = std::env::var_os("PATH")?;
        std::env::split_paths(&path)
            .map(|d| d.join(program))
            .find(|c| is_executable_file(c))
    }?;
    Some(found.canonicalize().unwrap_or(found))
}

/// The file of the RUNNING `gov` binary: `/proc/self/exe` on Linux names the running inode even if the path was
/// replaced or deleted since start; elsewhere `current_exe`.
fn running_exe() -> PathBuf {
    #[cfg(target_os = "linux")]
    {
        PathBuf::from("/proc/self/exe")
    }
    #[cfg(not(target_os = "linux"))]
    {
        std::env::current_exe().unwrap_or_default()
    }
}

fn file_identity(p: &Path) -> Option<(u64, u64, u64)> {
    let m = std::fs::metadata(p).ok()?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::MetadataExt;
        Some((m.dev(), m.ino(), m.len()))
    }
    #[cfg(not(unix))]
    {
        Some((0, 0, m.len()))
    }
}

/// The content hash of the running binary, read from the running file itself — at most once per process, and not at
/// all when the machine's pin cache holds a digest stored under the running file's present stat key
/// ([`super::pincache`]: a running executable cannot be open for writing, and any later change of its bytes changes
/// its key).
fn running_exe_sha() -> Option<&'static str> {
    static SHA: OnceLock<Option<String>> = OnceLock::new();
    SHA.get_or_init(|| super::pincache::sha256_of(&running_exe()))
        .as_deref()
}

/// `Some(sha)` when `program` is the running `gov` binary — the very same file (device and inode), or a byte-identical
/// copy — with its content hash; `None` otherwise. The same-file case needs no re-hash: an executable cannot be
/// rewritten in place while it runs (ETXTBSY), and a replaced path is a different inode.
fn this_binary(program: &Path) -> Option<String> {
    let run = file_identity(&running_exe())?;
    let prog = file_identity(program)?;
    if cfg!(unix) && run.0 == prog.0 && run.1 == prog.1 {
        return running_exe_sha().map(String::from);
    }
    if run.2 != prog.2 {
        return None;
    }
    let h = hash_file(program)?;
    (Some(h.as_str()) == running_exe_sha()).then_some(h)
}

/// Whether `args` (after the program) invoke exactly one OS capability server with only its own flags.
fn os_capability_server(args: &[String]) -> bool {
    OS_CAPABILITY_SERVERS.iter().any(|(words, bare, valued)| {
        if args.len() < words.len()
            || args[..words.len()]
                .iter()
                .zip(words.iter())
                .any(|(a, w)| a != w)
        {
            return false;
        }
        let mut i = words.len();
        while i < args.len() {
            let a = &args[i];
            if bare.contains(&a.as_str()) {
                i += 1;
            } else if valued.contains(&a.as_str()) && i + 1 < args.len() {
                i += 2;
            } else if valued.iter().any(|v| a.starts_with(&format!("{v}="))) {
                i += 1;
            } else {
                return false;
            }
        }
        true
    })
}

/// **The content hash of the file at `p`, as the implementation binding computes it** (symlinks followed): the
/// digest every pin compares, reused only under the pin cache's rules ([`super::pincache`]). Other components that
/// identify the same files — the retrieval profile's runtime and model identity (BC-P2-30) — use this instead of
/// re-hashing, so a large program or model is read once, not once per consumer (call [`super::pincache::flush`]
/// after a batch so new digests reach the machine's store). `None` when `p` is not a readable regular file.
pub fn content_sha256(p: &Path) -> Option<String> {
    if let (Some(run), Some(file)) = (file_identity(&running_exe()), file_identity(p)) {
        if cfg!(unix) && run.0 == file.0 && run.1 == file.1 {
            return running_exe_sha().map(String::from);
        }
    }
    super::pincache::sha256_of(p)
}

/// Content hash of one bound file. A symlink binds both where it points and the bytes it resolves to, so re-pointing
/// it and changing the file it points at are both changes (a symlink identified by its target text alone would let
/// the target's bytes change unseen). The bytes are read afresh unless the pin cache proves they cannot have changed.
fn hash_file(p: &Path) -> Option<String> {
    let meta = std::fs::symlink_metadata(p).ok()?;
    if meta.file_type().is_symlink() {
        let t = std::fs::read_link(p).ok()?;
        let content = if std::fs::metadata(p).map(|m| m.is_file()).unwrap_or(false) {
            content_sha256(p)?
        } else {
            "unresolved".to_string()
        };
        return Some(sha256_hex(
            format!("symlink:{}\ncontent:{content}", t.to_string_lossy()).as_bytes(),
        ));
    }
    content_sha256(p)
}

/// Every file under `dir`, sorted, recursively. A symlinked directory inside the tree is followed (an interpreter
/// imports through it) and its link is bound as well; each directory is entered once (cycles end there).
fn tree_files(dir: &Path, out: &mut Vec<PathBuf>) -> std::result::Result<(), String> {
    let mut stack = vec![dir.to_path_buf()];
    let mut entered: std::collections::BTreeSet<PathBuf> = std::collections::BTreeSet::new();
    while let Some(d) = stack.pop() {
        if !entered.insert(d.canonicalize().unwrap_or_else(|_| d.clone())) {
            continue;
        }
        let rd = std::fs::read_dir(&d).map_err(|e| format!("cannot read {}: {e}", d.display()))?;
        let mut entries: Vec<PathBuf> = rd.filter_map(|e| e.ok()).map(|e| e.path()).collect();
        entries.sort();
        for e in entries {
            let ft = std::fs::symlink_metadata(&e)
                .map(|m| m.file_type())
                .map_err(|x| format!("cannot stat {}: {x}", e.display()))?;
            if ft.is_dir() {
                stack.push(e);
                continue;
            }
            if ft.is_symlink() && std::fs::metadata(&e).map(|m| m.is_dir()).unwrap_or(false) {
                stack.push(e.clone());
            }
            out.push(e);
            if out.len() > MAX_BOUND_FILES {
                return Err(format!(
                    "{} holds more than {MAX_BOUND_FILES} files; an implementation that large is not bound",
                    dir.display()
                ));
            }
        }
    }
    out.sort();
    Ok(())
}

fn is_python(name: &str) -> bool {
    let base = Path::new(name)
        .file_name()
        .map(|b| b.to_string_lossy().to_string())
        .unwrap_or_default();
    base == "python"
        || base
            .strip_prefix("python")
            .map(|rest| !rest.is_empty() && rest.chars().all(|c| c.is_ascii_digit() || c == '.'))
            .unwrap_or(false)
}

type SearchKey = (PathBuf, Vec<String>, PathBuf);

/// The interpreter's module search path from `cwd` (the list Python's `-m` resolves against), under the plugin
/// environment. Cached per (interpreter, options, working directory) for the life of the process.
fn python_search_path(
    program: &Path,
    opts: &[String],
    cwd: &Path,
) -> std::result::Result<Vec<PathBuf>, String> {
    static CACHE: OnceLock<Mutex<BTreeMap<SearchKey, Vec<PathBuf>>>> = OnceLock::new();
    let key = (program.to_path_buf(), opts.to_vec(), cwd.to_path_buf());
    let cache = CACHE.get_or_init(|| Mutex::new(BTreeMap::new()));
    if let Some(v) = cache.lock().ok().and_then(|c| c.get(&key).cloned()) {
        return Ok(v);
    }
    let mut cmd = std::process::Command::new(program);
    cmd.args(opts)
        .arg("-c")
        .arg("import sys, json; print(json.dumps(sys.path))")
        .current_dir(cwd)
        .stdin(std::process::Stdio::null());
    apply_plugin_env(&mut cmd);
    let out = cmd.output().map_err(|e| {
        format!(
            "cannot ask {} for its module search path: {e}",
            program.display()
        )
    })?;
    if !out.status.success() {
        return Err(format!(
            "{} could not report its module search path (exit {:?})",
            program.display(),
            out.status.code()
        ));
    }
    let v: Vec<String> = serde_json::from_slice(&out.stdout).map_err(|e| {
        format!(
            "unreadable module search path from {}: {e}",
            program.display()
        )
    })?;
    let dirs: Vec<PathBuf> = v
        .into_iter()
        .map(|s| {
            if s.is_empty() {
                cwd.to_path_buf()
            } else if Path::new(&s).is_absolute() {
                PathBuf::from(s)
            } else {
                cwd.join(s)
            }
        })
        .collect();
    if let Ok(mut c) = cache.lock() {
        c.insert(key, dirs.clone());
    }
    Ok(dirs)
}

/// Locate what `import <top>` loads, in Python's finder order over `search`: a regular package (a directory with an
/// `__init__`), else a module file (source, byte-code or extension), else every namespace portion. Returns the
/// paths to bind (a directory is bound as a whole tree).
fn python_top_level(top: &str, search: &[PathBuf]) -> Vec<PathBuf> {
    let mut portions = vec![];
    for entry in search.iter().filter(|e| e.is_dir()) {
        let pkg = entry.join(top);
        if pkg.is_dir() {
            let regular = std::fs::read_dir(&pkg)
                .map(|rd| {
                    rd.filter_map(|e| e.ok()).any(|e| {
                        let n = e.file_name().to_string_lossy().to_string();
                        n == "__init__.py" || n.starts_with("__init__.")
                    })
                })
                .unwrap_or(false);
            if regular {
                return vec![pkg];
            }
        }
        if let Ok(rd) = std::fs::read_dir(entry) {
            let mut files: Vec<PathBuf> = rd
                .filter_map(|e| e.ok())
                .map(|e| e.path())
                .filter(|p| {
                    let n = p
                        .file_name()
                        .map(|n| n.to_string_lossy().to_string())
                        .unwrap_or_default();
                    p.is_file()
                        && (n == format!("{top}.py")
                            || n == format!("{top}.pyc")
                            || n == format!("{top}.pyw")
                            || (n.starts_with(&format!("{top}."))
                                && (n.ends_with(".so") || n.ends_with(".pyd"))))
                })
                .collect();
            if !files.is_empty() {
                files.sort();
                return files;
            }
        }
        if pkg.is_dir() {
            portions.push(pkg);
        }
    }
    portions
}

/// Descriptor fields that declare files beyond the command vector, and the role their bound files carry:
/// `implementation:` (helpers the entry point loads), and — for the retrieval components' identity (BC-P2-30,
/// IP-R2-13) — `model.artefacts` (weights, tokenizer, configuration the plugin loads) and `runtime.artefacts` (the
/// inference runtime it loads: libraries, a model server, an environment's packages).
pub const DECLARED_FIELDS: &[(&str, &str)] = &[
    ("implementation", "declared"),
    ("model", "model"),
    ("runtime", "runtime"),
];

/// One path a descriptor declares ([`DECLARED_FIELDS`]).
#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize)]
pub struct DeclaredPath {
    /// `declared` (from `implementation:`), `model` or `runtime`: the role its bound files carry.
    pub role: String,
    /// The path as the descriptor writes it.
    pub declared: String,
    /// Where it resolves: `{project_root}` / `{plugin_dir}` substituted, a relative path taken from the project root.
    pub abs: PathBuf,
    /// Inside the repository (content every clone carries) rather than machine-local.
    pub in_repository: bool,
}

/// **Every path `desc` declares beyond its command** — `implementation:`, `model.artefacts`, `runtime.artefacts` —
/// resolved as [`resolve`] binds them, whether or not they exist. For an executable plugin every one of them is bound
/// by the registration (its bytes are part of the implementation identity; a missing one is refused), so the
/// retrieval profile (BC-P2-30) can identify the model and runtime from the files the registration binds.
pub fn declared_paths(desc: &PluginDescriptor, root: &Path) -> Vec<DeclaredPath> {
    let plugin_dir = Path::new(&desc.source)
        .parent()
        .map(|p| p.to_string_lossy().to_string())
        .unwrap_or_default();
    let root_c = root.canonicalize().unwrap_or_else(|_| root.to_path_buf());
    let mut out = vec![];
    for (field, role) in DECLARED_FIELDS {
        for s in desc.declared_paths(field) {
            let sub = s
                .replace("{project_root}", &root.to_string_lossy())
                .replace("{plugin_dir}", &plugin_dir);
            let abs = if Path::new(&sub).is_absolute() {
                PathBuf::from(&sub)
            } else {
                root.join(&sub)
            };
            let canon = abs.canonicalize().unwrap_or_else(|_| abs.clone());
            out.push(DeclaredPath {
                role: role.to_string(),
                declared: s.clone(),
                in_repository: canon.starts_with(&root_c),
                abs,
            });
        }
    }
    out
}

/// **Derive the implementation of `desc` as the host would execute it from `root`** (see the module documentation).
pub fn resolve(desc: &PluginDescriptor, root: &Path) -> Result<Implementation> {
    let root_c = root.canonicalize().unwrap_or_else(|_| root.to_path_buf());
    let cmd = substituted_command(desc, root);
    let cwd = working_dir(desc, root);
    let Some(first) = cmd.first() else {
        return Err(unresolved(desc, "the command is empty".into()));
    };
    let program = resolve_program(first, &cwd).ok_or_else(|| {
        unresolved(
            desc,
            format!("its program '{first}' does not resolve to a file (relative to its working directory, or on PATH)"),
        )
    })?;
    let os_binary = this_binary(&program);
    let program_sha = match &os_binary {
        Some(h) => h.clone(),
        None => hash_file(&program).ok_or_else(|| {
            unresolved(
                desc,
                format!("its program {} is unreadable", program.display()),
            )
        })?,
    };
    let args: Vec<String> = cmd[1..].to_vec();
    let mut bound: BTreeMap<String, BoundFile> = BTreeMap::new();
    let mut add = |role: &str, p: &Path, sha: String| {
        let path = display(p, &root_c);
        bound.entry(path.clone()).or_insert(BoundFile {
            role: role.to_string(),
            path,
            sha256: sha,
        });
    };
    add("program", &program, program_sha.clone());
    let class = if os_binary.is_some() && os_capability_server(&args) {
        ExecutionClass::OsProvided
    } else {
        ExecutionClass::Executable
    };
    let mut primary: Option<PathBuf> = None;
    let mut trees: Vec<(String, PathBuf)> = vec![];
    if class == ExecutionClass::Executable {
        let python = is_python(first) || is_python(&program.to_string_lossy());
        let mut i = 0;
        let mut interpreter_opts = true;
        while i < args.len() {
            let a = &args[i];
            if python && interpreter_opts && a == "-m" {
                let Some(module) = args.get(i + 1) else {
                    return Err(unresolved(desc, "`-m` names no module".into()));
                };
                let top = module.split('.').next().unwrap_or("").to_string();
                if top.is_empty() {
                    return Err(unresolved(desc, format!("module name '{module}' is empty")));
                }
                let search = python_search_path(&program, &args[..i], &cwd)
                    .map_err(|e| unresolved(desc, e))?;
                let found = python_top_level(&top, &search);
                if found.is_empty() {
                    return Err(unresolved(
                        desc,
                        format!(
                            "module '{module}' is not on {}'s search path from {}",
                            program.display(),
                            cwd.display()
                        ),
                    ));
                }
                for f in found {
                    let f = f.canonicalize().unwrap_or(f);
                    if primary.is_none() {
                        primary = Some(f.clone());
                    }
                    trees.push(("module".into(), f));
                }
                interpreter_opts = false;
                i += 2;
                continue;
            }
            if python && interpreter_opts && a == "-c" {
                // inline code: it lives in the descriptor, whose bytes the registration binds
                interpreter_opts = false;
                i += 2;
                continue;
            }
            if a.starts_with('-') {
                i += 1;
                continue;
            }
            interpreter_opts = false;
            let p = if Path::new(a).is_absolute() {
                PathBuf::from(a)
            } else {
                cwd.join(a)
            };
            if p.is_file() {
                let p = p.canonicalize().unwrap_or(p);
                if let Some(h) = hash_file(&p) {
                    if primary.is_none() {
                        primary = Some(p.clone());
                    }
                    add("argument", &p, h);
                }
            }
            i += 1;
        }
        for d in declared_paths(desc, root) {
            if !d.abs.exists() {
                let what = match d.role.as_str() {
                    "model" => "model artefact",
                    "runtime" => "runtime artefact",
                    _ => "implementation path",
                };
                return Err(unresolved(
                    desc,
                    format!("its declared {what} '{}' does not exist", d.declared),
                ));
            }
            trees.push((d.role.clone(), d.abs.canonicalize().unwrap_or(d.abs)));
        }
    }
    for (role, t) in trees {
        if t.is_dir() {
            let mut files = vec![];
            tree_files(&t, &mut files).map_err(|e| unresolved(desc, e))?;
            for f in files {
                let h = hash_file(&f)
                    .ok_or_else(|| unresolved(desc, format!("{} is unreadable", f.display())))?;
                add(&role, &f, h);
            }
        } else {
            let h = hash_file(&t)
                .ok_or_else(|| unresolved(desc, format!("{} is unreadable", t.display())))?;
            add(&role, &t, h);
        }
    }
    super::pincache::flush();
    let files: Vec<BoundFile> = bound.into_values().collect();
    let mut acc = String::new();
    for f in &files {
        acc.push_str(&format!("{}\t{}\n", f.path, f.sha256));
    }
    Ok(Implementation {
        class,
        program: program.to_string_lossy().to_string(),
        sha256: sha256_hex(acc.as_bytes()),
        files,
        primary: primary.or(Some(program)),
    })
}

/// The descriptor content a registration approves: the descriptor minus the fields that are requests or OS-written
/// copies ([`NON_SUBJECT_FIELDS`]), with the registration defaults applied so the first and the confirming
/// `gov plugins register` compute the same subject.
pub fn normalized_descriptor(v: &Value) -> Value {
    let mut d = v.clone();
    if let Some(o) = d.as_object_mut() {
        for k in NON_SUBJECT_FIELDS {
            o.remove(*k);
        }
        o.remove(crate::t2::SEAL_FIELD);
        o.entry("approved_roles").or_insert(json!(["all"]));
        o.entry("health_check")
            .or_insert(json!({"kind": "command_exists"}));
    }
    d
}

/// **The registration subject**: exactly what a registration gate approves — plugin identity and version, the
/// normalized descriptor (command, working directory, declared permissions and classes, approved roles) and the
/// implementation the OS derived (class, program, every bound file and its hash). Returns `(subject, sha256)`; the
/// gate carries `subject.sha256` and `gates::human_approval_for` honours only an answer bound to it.
pub fn registration_subject(descriptor: &Value, imp: &Implementation) -> (Value, String) {
    let norm = normalized_descriptor(descriptor);
    let doc = json!({
        "kind": "plugin-registration",
        "plugin_id": norm.get("plugin_id").cloned().unwrap_or(Value::Null),
        "capability": norm.get("capability").cloned().unwrap_or(Value::Null),
        "version": norm.get("version").map(|v| match v { Value::String(s) => s.clone(), other => other.to_string() }),
        "descriptor": norm,
        "implementation": imp.to_value(),
    });
    let sha = sha256_hex(canonical_json(&doc).as_bytes());
    (doc, sha)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn desc(dir: &Path, command: Vec<&str>, extra: Value) -> PluginDescriptor {
        let mut v =
            json!({"plugin_id": "p", "capability": "embed", "version": "1", "command": command});
        for (k, x) in extra.as_object().cloned().unwrap_or_default() {
            v[k] = x;
        }
        PluginDescriptor::from_value(
            &v,
            &dir.join("governance/project/plugins/p.yaml")
                .to_string_lossy(),
        )
        .unwrap()
    }

    fn tmp() -> PathBuf {
        let d = std::env::temp_dir().join(format!("gov-bind-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(d.join("governance/project/plugins")).unwrap();
        d
    }

    #[test]
    fn a_script_binds_the_program_and_the_script_and_any_edit_changes_the_identity() {
        let d = tmp();
        std::fs::write(d.join("s.sh"), "echo one\n").unwrap();
        let a = resolve(&desc(&d, vec!["sh", "s.sh"], json!({})), &d).unwrap();
        assert_eq!(a.class, ExecutionClass::Executable);
        assert!(
            a.files
                .iter()
                .any(|f| f.path == "s.sh" && f.role == "argument"),
            "{:?}",
            a.files
        );
        assert!(a.files.iter().any(|f| f.role == "program"));
        std::fs::write(d.join("s.sh"), "echo two\n").unwrap();
        let b = resolve(&desc(&d, vec!["sh", "s.sh"], json!({})), &d).unwrap();
        assert_ne!(a.sha256, b.sha256);
    }

    #[test]
    fn inline_code_is_executable_and_bound_through_the_descriptor() {
        let d = tmp();
        let a = resolve(&desc(&d, vec!["sh", "-c", "echo hi"], json!({})), &d).unwrap();
        assert_eq!(a.class, ExecutionClass::Executable);
        let (_, s1) = registration_subject(
            &json!({"plugin_id": "p", "command": ["sh", "-c", "echo hi"]}),
            &a,
        );
        let (_, s2) = registration_subject(
            &json!({"plugin_id": "p", "command": ["sh", "-c", "echo bye"]}),
            &a,
        );
        assert_ne!(s1, s2, "the inline code is part of the approved subject");
    }

    #[test]
    fn a_missing_program_or_declared_path_is_refused() {
        let d = tmp();
        assert_eq!(
            resolve(&desc(&d, vec!["./nope.sh"], json!({})), &d)
                .unwrap_err()
                .code,
            "PLUGIN_IMPLEMENTATION_UNRESOLVED"
        );
        assert_eq!(
            resolve(
                &desc(
                    &d,
                    vec!["sh", "-c", "true"],
                    json!({"implementation": ["lib/missing.sh"]})
                ),
                &d
            )
            .unwrap_err()
            .code,
            "PLUGIN_IMPLEMENTATION_UNRESOLVED"
        );
    }

    /// IP-R2-13: the model and runtime artefacts a descriptor declares (typically outside the plugin's directory)
    /// are bound with their roles, any change to them changes the implementation identity, and a missing one is
    /// refused before anything runs.
    #[test]
    fn declared_model_and_runtime_artefacts_are_bound_with_their_roles() {
        let d = tmp();
        let ext = tmp(); // outside the project: a model cache, a runtime installation
        std::fs::write(d.join("s.sh"), "echo embed\n").unwrap();
        std::fs::create_dir_all(ext.join("model")).unwrap();
        std::fs::write(ext.join("model/weights.bin"), [1u8, 2, 3]).unwrap();
        std::fs::write(ext.join("model/tokenizer.json"), "{}").unwrap();
        std::fs::write(ext.join("libinfer.so"), "elf").unwrap();
        let extra = json!({"model": {"id": "m", "artefacts": [ext.join("model").to_string_lossy()]},
                           "runtime": {"artefacts": [ext.join("libinfer.so").to_string_lossy()]}});
        let dp = desc(&d, vec!["sh", "s.sh"], extra);
        let paths = declared_paths(&dp, &d);
        assert_eq!(
            paths.iter().map(|p| p.role.as_str()).collect::<Vec<_>>(),
            vec!["model", "runtime"]
        );
        assert!(paths.iter().all(|p| !p.in_repository));
        let a = resolve(&dp, &d).unwrap();
        let role_of = |imp: &Implementation, name: &str| {
            imp.files
                .iter()
                .find(|f| f.path.ends_with(name))
                .map(|f| f.role.clone())
        };
        assert_eq!(role_of(&a, "weights.bin").as_deref(), Some("model"));
        assert_eq!(role_of(&a, "tokenizer.json").as_deref(), Some("model"));
        assert_eq!(role_of(&a, "libinfer.so").as_deref(), Some("runtime"));
        std::fs::write(ext.join("model/weights.bin"), [1u8, 2, 4]).unwrap();
        let b = resolve(&dp, &d).unwrap();
        assert_ne!(
            a.sha256, b.sha256,
            "a changed model byte must change the identity"
        );
        std::fs::write(ext.join("libinfer.so"), "elg").unwrap();
        let c = resolve(&dp, &d).unwrap();
        assert_ne!(
            b.sha256, c.sha256,
            "a changed runtime byte must change the identity"
        );
        let missing = desc(
            &d,
            vec!["sh", "s.sh"],
            json!({"model": {"artefacts": ["models/absent.bin"]}}),
        );
        let e = resolve(&missing, &d).unwrap_err();
        assert_eq!(e.code, "PLUGIN_IMPLEMENTATION_UNRESOLVED");
        assert!(e.message.contains("model artefact"), "{}", e.message);
        let _ = std::fs::remove_dir_all(&ext);
    }

    /// A symlink inside a bound tree binds the bytes it resolves to (changing the target file is a change), and a
    /// symlinked directory is followed (a file added under it is a change).
    #[cfg(unix)]
    #[test]
    fn symlinked_files_and_directories_inside_a_bound_tree_are_bound_by_content() {
        let d = tmp();
        let outside = tmp();
        std::fs::write(outside.join("helper.py"), "X = 1\n").unwrap();
        std::fs::create_dir_all(outside.join("sub")).unwrap();
        std::fs::write(outside.join("sub/mod.py"), "Y = 1\n").unwrap();
        std::fs::create_dir_all(d.join("lib")).unwrap();
        std::os::unix::fs::symlink(outside.join("helper.py"), d.join("lib/helper.py")).unwrap();
        std::os::unix::fs::symlink(outside.join("sub"), d.join("lib/sub")).unwrap();
        std::fs::write(d.join("s.sh"), "echo x\n").unwrap();
        let dp = desc(&d, vec!["sh", "s.sh"], json!({"implementation": ["lib"]}));
        let a = resolve(&dp, &d).unwrap();
        assert!(
            a.files.iter().any(|f| f.path.ends_with("lib/sub/mod.py")),
            "{:?}",
            a.files
        );
        std::fs::write(outside.join("helper.py"), "X = 2\n").unwrap();
        let b = resolve(&dp, &d).unwrap();
        assert_ne!(
            a.sha256, b.sha256,
            "the symlink target's bytes changed unseen"
        );
        std::fs::write(outside.join("sub/extra.py"), "Z = 1\n").unwrap();
        let c = resolve(&dp, &d).unwrap();
        assert_ne!(
            b.sha256, c.sha256,
            "a file added under a symlinked directory changed nothing"
        );
        let _ = std::fs::remove_dir_all(&outside);
    }

    #[test]
    fn the_os_capability_server_is_recognised_only_with_its_own_flags() {
        assert!(os_capability_server(&[
            "capabilities".into(),
            "serve-embed".into()
        ]));
        assert!(os_capability_server(&[
            "capabilities".into(),
            "serve-embed".into(),
            "--id".into(),
            "x".into(),
            "--reverse".into()
        ]));
        assert!(!os_capability_server(&[
            "capabilities".into(),
            "serve-embed".into(),
            "--root".into(),
            "/".into()
        ]));
        assert!(!os_capability_server(&[
            "plugins".into(),
            "register".into()
        ]));
        assert!(!os_capability_server(&["capabilities".into()]));
    }

    #[test]
    fn python_names_are_recognised() {
        for n in ["python", "python3", "/usr/bin/python3.12", "python3.11"] {
            assert!(is_python(n), "{n}");
        }
        for n in ["pythonista", "sh", "python3-config"] {
            assert!(!is_python(n), "{n}");
        }
    }

    #[test]
    fn python_finder_order_prefers_a_regular_package_then_a_module_then_namespace_portions() {
        let d = tmp();
        let a = d.join("a");
        let b = d.join("b");
        std::fs::create_dir_all(a.join("pkg")).unwrap(); // namespace portion (no __init__)
        std::fs::create_dir_all(b.join("pkg")).unwrap();
        std::fs::write(b.join("pkg/__init__.py"), "").unwrap(); // regular package later on the path
        assert_eq!(
            python_top_level("pkg", &[a.clone(), b.clone()]),
            vec![b.join("pkg")]
        );
        std::fs::write(a.join("mod.py"), "").unwrap();
        assert_eq!(
            python_top_level("mod", &[a.clone(), b.clone()]),
            vec![a.join("mod.py")]
        );
        std::fs::remove_file(b.join("pkg/__init__.py")).unwrap();
        assert_eq!(
            python_top_level("pkg", &[a.clone(), b.clone()]),
            vec![a.join("pkg"), b.join("pkg")]
        );
    }
}
