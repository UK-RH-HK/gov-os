//! # Content hashes of bound files, reused only under a key that no changed byte can keep (BC-P2-40)
//!
//! Plugin authorisation ([`super::governance::authorize`]) recomputes the implementation a plugin would execute at
//! every execution and every `plugin_set` classification ([`super::binding::resolve`]), and compares it with the
//! registered and declared pins (Contract v3 F4:428-429: drift fails closed). Hashing every bound file every time is
//! what makes a plugin whose program is a large binary slow (the debug `gov` binary serving embeddings is ~170 MB:
//! ~2.3 s per classification). This module lets a digest be reused — within a process and across processes — only
//! when reuse cannot return the digest of bytes other than the file's current bytes.
//!
//! ## The key, and why a changed byte cannot keep it
//!
//! A digest is stored with the file's [`StatKey`]: device, inode, size, modification time, **status-change time
//! (`ctime`)**, mode and owner. It is reused only when a fresh `stat` returns exactly the same key. Every way of
//! changing a file's bytes changes that key:
//!
//! * `write(2)`, `truncate`, and the first store through a (new) shared writable mapping (the kernel's
//!   `page_mkwrite`) set `mtime` and `ctime` to the current time; `ctime` cannot be set by an unprivileged process
//!   (resetting `mtime` with `utimensat`/`touch -d` sets `ctime` to *now*); `chmod`/`chown` set `ctime`;
//! * replacing the file (write-then-rename, delete-and-recreate) gives a different inode, and a reused inode number
//!   is a new file whose `ctime` is its creation time.
//!
//! That holds where the kernel maintains the timestamps itself. A digest is therefore stored only for a file on a
//! **local filesystem** whose inode times the running kernel keeps ([`local_fs`]: ext2/3/4, XFS, Btrfs, F2FS, ZFS,
//! tmpfs, ramfs, overlayfs). On network and user-space filesystems (NFS, SMB, FUSE such as sshfs, 9p/drvfs) the
//! times come from elsewhere — a remote `touch -d` can leave `ctime` untouched — so nothing there is ever cached.
//!
//! Two gaps would remain with that key alone, and both are closed before a digest is stored:
//!
//! 1. **Same-tick rewrites** (the defect found in round 2: a same-size rewrite inside one filesystem timestamp tick
//!    kept `(size, mtime, inode)`). A digest is stored only when the file's `ctime` and `mtime` lie at least
//!    [`QUIESCENCE`] before the moment its bytes are read ([`quiescent`]) — longer than the coarsest timestamp
//!    granularity of a local filesystem (FAT/exFAT: 2 s; the Linux coarse clock: ≤ 10 ms). Any later change is
//!    stamped at or after that moment, so it cannot reproduce the stored `ctime`.
//! 2. **A writer that already holds the file open for writing** (a shared writable mapping whose pages are already
//!    dirty can change bytes without a new timestamp until write-back). A digest is stored only when the OS proves no
//!    process holds the file open for writing at the moment it is read ([`no_writer`]): on Linux a *read lease*
//!    cannot be granted on a file that is open for writing anywhere (`fcntl(F_SETLEASE, F_RDLCK)` fails `EAGAIN`);
//!    the lease is released at once (a lease break is routed to `SIGURG`, whose default disposition is to ignore it).
//!    A file the caller does not own cannot be leased; it is proven writer-free only when it is owned by root and
//!    writable by nobody else (only root could have it open for writing — outside this threat model). Otherwise
//!    nothing is stored and the file is hashed every time.
//!
//! Finally the `stat` is repeated after the bytes are read; a file that changed while being read is never stored.
//!
//! ## Where digests are kept
//!
//! In process memory, and in the machine's protected state (`<state root>/plugin-pin-cache/cache.json`, the same
//! root as the T2 binding key and the trust floors), which no repository writer can reach: a forged entry there would
//! need the machine's own state, and the entry is still used only for a file whose `stat` key matches. The store is a
//! cache: losing it, or a machine without a resolvable state root, only costs a re-hash. New digests are written to
//! it in one batch per implementation resolved ([`flush`]).
//!
//! **What this does not change.** Authorisation still reads the current `stat` of every bound file at every
//! execution, still enumerates every bound directory afresh (an added or removed file is a change), and still
//! compares the result with the pins. As before, bytes changed *after* authorisation and before the plugin process
//! loads them (a race against the spawn) are outside what any hash-then-execute design can see.
use crate::util::now_iso;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::sync::{Mutex, OnceLock};
use std::time::{Duration, SystemTime, UNIX_EPOCH};

/// How long before its bytes are read a file must have last changed for its digest to be stored.
pub const QUIESCENCE: Duration = Duration::from_secs(3);
/// Upper bound on persisted entries (the oldest are dropped first).
const MAX_PERSISTED: usize = 16_384;
/// Pending digests beyond this are written without waiting for [`flush`].
const MAX_PENDING: usize = 1_024;
const CACHE_DIR: &str = "plugin-pin-cache";
const CACHE_FILE: &str = "cache.json";

/// What a stored digest is valid for: the file's identity and every timestamp a change of its bytes updates.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct StatKey {
    pub dev: u64,
    pub ino: u64,
    pub size: u64,
    pub mtime_ns: i64,
    pub ctime_ns: i64,
    pub mode: u32,
    pub uid: u32,
}

impl StatKey {
    fn to_value(&self) -> Value {
        json!({"dev": self.dev.to_string(), "ino": self.ino.to_string(), "size": self.size.to_string(),
               "mtime_ns": self.mtime_ns.to_string(), "ctime_ns": self.ctime_ns.to_string(), "mode": self.mode, "uid": self.uid})
    }
    fn from_value(v: &Value) -> Option<StatKey> {
        let n = |k: &str| {
            v.get(k)
                .and_then(|x| x.as_str())
                .and_then(|s| s.parse::<i128>().ok())
        };
        Some(StatKey {
            dev: u64::try_from(n("dev")?).ok()?,
            ino: u64::try_from(n("ino")?).ok()?,
            size: u64::try_from(n("size")?).ok()?,
            mtime_ns: i64::try_from(n("mtime_ns")?).ok()?,
            ctime_ns: i64::try_from(n("ctime_ns")?).ok()?,
            mode: u32::try_from(v.get("mode")?.as_u64()?).ok()?,
            uid: u32::try_from(v.get("uid")?.as_u64()?).ok()?,
        })
    }
    fn slot(&self) -> String {
        format!("{}:{}", self.dev, self.ino)
    }
}

/// The [`StatKey`] of the regular file at `p` (symlinks followed); `None` for anything else.
#[cfg(unix)]
pub fn stat_key(p: &Path) -> Option<StatKey> {
    use std::os::unix::fs::MetadataExt;
    let m = std::fs::metadata(p).ok()?;
    if !m.is_file() {
        return None;
    }
    Some(StatKey {
        dev: m.dev(),
        ino: m.ino(),
        size: m.size(),
        mtime_ns: m
            .mtime()
            .saturating_mul(1_000_000_000)
            .saturating_add(m.mtime_nsec()),
        ctime_ns: m
            .ctime()
            .saturating_mul(1_000_000_000)
            .saturating_add(m.ctime_nsec()),
        mode: m.mode(),
        uid: m.uid(),
    })
}

#[cfg(not(unix))]
pub fn stat_key(_p: &Path) -> Option<StatKey> {
    // no status-change time to key on: never cached
    None
}

/// Rule 1: the file last changed at least [`QUIESCENCE`] before `read_start` (both `ctime` and `mtime`).
pub fn quiescent(k: &StatKey, read_start: SystemTime) -> bool {
    let Ok(d) = read_start.duration_since(UNIX_EPOCH) else {
        return false;
    };
    let limit = d.as_nanos() as i128 - QUIESCENCE.as_nanos() as i128;
    (k.ctime_ns as i128) < limit && (k.mtime_ns as i128) < limit
}

/// The filesystems whose inode times the running kernel maintains itself (`statfs` magic numbers): ext2/3/4, XFS,
/// Btrfs, tmpfs, F2FS, overlayfs, ZFS, ramfs.
#[cfg(target_os = "linux")]
const LOCAL_FS_MAGIC: &[u64] = &[
    0xEF53,
    0x5846_5342,
    0x9123_683E,
    0x0102_1994,
    0xF2F5_2010,
    0x794C_7630,
    0x2FC1_2FC1,
    0x8584_58F6,
];

/// Whether `p` lives on a filesystem whose timestamps the running kernel maintains ([`LOCAL_FS_MAGIC`]).
#[cfg(target_os = "linux")]
pub fn local_fs(p: &Path) -> bool {
    use std::os::unix::ffi::OsStrExt;
    let Ok(c) = std::ffi::CString::new(p.as_os_str().as_bytes()) else {
        return false;
    };
    // SAFETY: `c` is a valid NUL-terminated path and `buf` is a properly sized, zero-initialised `statfs`.
    let mut buf: libc::statfs = unsafe { std::mem::zeroed() };
    if unsafe { libc::statfs(c.as_ptr(), &mut buf) } != 0 {
        return false;
    }
    LOCAL_FS_MAGIC.contains(&((buf.f_type as u64) & 0xFFFF_FFFF))
}

#[cfg(not(target_os = "linux"))]
pub fn local_fs(_p: &Path) -> bool {
    false
}

/// Rule 2: no process holds `p` open for writing at this moment (see the module documentation).
pub fn no_writer(p: &Path, k: &StatKey) -> bool {
    if k.uid == 0 && k.mode & 0o022 == 0 {
        return true;
    }
    lease_probe(p)
}

/// `F_SETSIG` (`fcntl(2)`; 10 on every Linux architecture, not exported by the `libc` crate for every target).
#[cfg(target_os = "linux")]
const F_SETSIG: libc::c_int = 10;

#[cfg(target_os = "linux")]
fn lease_probe(p: &Path) -> bool {
    use std::os::unix::io::AsRawFd;
    let Ok(f) = std::fs::File::open(p) else {
        return false;
    };
    let fd = f.as_raw_fd();
    // SAFETY: plain fcntl calls on a file descriptor this function owns for its whole duration.
    unsafe {
        if libc::fcntl(fd, F_SETSIG, libc::SIGURG) != 0 {
            return false;
        }
        if libc::fcntl(fd, libc::F_SETLEASE, libc::F_RDLCK) != 0 {
            return false;
        }
        libc::fcntl(fd, libc::F_SETLEASE, libc::F_UNLCK);
    }
    true
}

#[cfg(not(target_os = "linux"))]
fn lease_probe(_p: &Path) -> bool {
    false
}

/// Streaming SHA-256 of a file's bytes.
fn stream_sha256(p: &Path) -> Option<String> {
    use std::io::Read;
    let mut f = std::fs::File::open(p).ok()?;
    let mut h = Sha256::new();
    let mut buf = vec![0u8; 1 << 20];
    loop {
        let n = f.read(&mut buf).ok()?;
        if n == 0 {
            break;
        }
        h.update(&buf[..n]);
    }
    Some(hex::encode(h.finalize()))
}

#[derive(Debug, Clone)]
struct Entry {
    key: StatKey,
    sha256: String,
    path: String,
    at: String,
}

#[derive(Default)]
struct Cache {
    /// slot (`dev:ino`) -> entry
    entries: BTreeMap<String, Entry>,
    persistent_loaded: bool,
    /// Stored in memory, not yet written to the machine's store.
    pending: Vec<Entry>,
}

fn cache() -> &'static Mutex<Cache> {
    static C: OnceLock<Mutex<Cache>> = OnceLock::new();
    C.get_or_init(|| Mutex::new(Cache::default()))
}

fn store_file() -> Option<PathBuf> {
    // unit tests of this crate never read or write the real machine's state
    if cfg!(test) {
        return None;
    }
    crate::srr::state::resolve_state_root()
        .ok()
        .map(|r| r.join(CACHE_DIR).join(CACHE_FILE))
}

fn read_store(file: &Path) -> BTreeMap<String, Entry> {
    let mut out = BTreeMap::new();
    let Ok(v) = crate::util::read_json(file) else {
        return out;
    };
    for (slot, e) in v
        .get("entries")
        .and_then(|m| m.as_object())
        .cloned()
        .unwrap_or_default()
    {
        let (Some(key), Some(sha)) = (
            e.get("key").and_then(StatKey::from_value),
            e.get("sha256").and_then(|s| s.as_str()),
        ) else {
            continue;
        };
        if sha.len() != 64 || key.slot() != slot {
            continue;
        }
        out.insert(
            slot,
            Entry {
                key,
                sha256: sha.to_string(),
                path: e["path"].as_str().unwrap_or("").to_string(),
                at: e["at"].as_str().unwrap_or("").to_string(),
            },
        );
    }
    out
}

fn persist(new: &[Entry]) {
    let Some(file) = store_file() else {
        return;
    };
    let mut all = read_store(&file);
    for e in new {
        all.insert(e.key.slot(), e.clone());
    }
    if all.len() > MAX_PERSISTED {
        let mut by_age: Vec<(String, String)> =
            all.iter().map(|(s, e)| (e.at.clone(), s.clone())).collect();
        by_age.sort();
        for (_, s) in by_age.into_iter().take(all.len() - MAX_PERSISTED) {
            all.remove(&s);
        }
    }
    let doc = json!({
        "purpose": "cache of content hashes of plugin-bound files (capabilities::pincache, BC-P2-40); an entry is used only for a file whose stat key (device, inode, size, mtime, ctime, mode, owner) is unchanged. Deleting this file only costs a re-hash.",
        "entries": all.iter().map(|(s, e)| (s.clone(), json!({"key": e.key.to_value(), "sha256": e.sha256, "path": e.path, "at": e.at}))).collect::<serde_json::Map<String, Value>>(),
    });
    let Some(dir) = file.parent() else {
        return;
    };
    if std::fs::create_dir_all(dir).is_err() {
        return;
    }
    let tmp = dir.join(format!(
        ".{CACHE_FILE}.{}.{}.tmp",
        std::process::id(),
        crate::util::short_uuid()
    ));
    let body = serde_json::to_string(&doc).unwrap_or_default();
    if std::fs::write(&tmp, body).is_ok() {
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            let _ = std::fs::set_permissions(&tmp, std::fs::Permissions::from_mode(0o600));
        }
        if std::fs::rename(&tmp, &file).is_err() {
            let _ = std::fs::remove_file(&tmp);
        }
    }
}

fn lookup(k: &StatKey) -> Option<String> {
    let mut c = cache().lock().ok()?;
    if !c.persistent_loaded {
        c.persistent_loaded = true;
        if let Some(f) = store_file() {
            for (s, e) in read_store(&f) {
                c.entries.entry(s).or_insert(e);
            }
        }
    }
    c.entries
        .get(&k.slot())
        .filter(|e| &e.key == k)
        .map(|e| e.sha256.clone())
}

/// **The SHA-256 of the bytes of the regular file at `p` (symlinks followed)**, reusing a stored digest only under
/// the rules in the module documentation. `None` when `p` is not a readable regular file.
pub fn sha256_of(p: &Path) -> Option<String> {
    let Some(before) = stat_key(p) else {
        // not a regular file we can key (or no unix metadata): hash it, never store
        return stream_sha256(p);
    };
    if let Some(sha) = lookup(&before) {
        return Some(sha);
    }
    let read_start = SystemTime::now();
    let writer_free = no_writer(p, &before);
    let sha = stream_sha256(p)?;
    let stable = stat_key(p).as_ref() == Some(&before);
    if writer_free && stable && quiescent(&before, read_start) && local_fs(p) {
        let e = Entry {
            key: before.clone(),
            sha256: sha.clone(),
            path: p.to_string_lossy().to_string(),
            at: now_iso(),
        };
        let overflow = match cache().lock() {
            Ok(mut c) => {
                c.entries.insert(before.slot(), e.clone());
                c.pending.push(e);
                c.pending.len() > MAX_PENDING
            }
            Err(_) => false,
        };
        if overflow {
            flush();
        }
    }
    Some(sha)
}

/// Write the digests stored since the last flush to the machine's store (one read-merge-write). Called once per
/// implementation resolved; a consumer hashing a batch of files through [`sha256_of`] calls it after the batch.
pub fn flush() {
    let pending: Vec<Entry> = match cache().lock() {
        Ok(mut c) => std::mem::take(&mut c.pending),
        Err(_) => return,
    };
    if !pending.is_empty() {
        persist(&pending);
    }
}

/// Whether a digest for the file at `p` is currently stored under its present key (diagnostics and tests).
pub fn is_cached(p: &Path) -> bool {
    stat_key(p).and_then(|k| lookup(&k)).is_some()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn tmpdir() -> PathBuf {
        let d = std::env::temp_dir().join(format!("gov-pincache-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    fn key(ctime_s: i64, mtime_s: i64) -> StatKey {
        StatKey {
            dev: 1,
            ino: 2,
            size: 3,
            mtime_ns: mtime_s * 1_000_000_000,
            ctime_ns: ctime_s * 1_000_000_000,
            mode: 0o100644,
            uid: 1000,
        }
    }

    #[test]
    fn a_file_is_quiescent_only_when_it_last_changed_well_before_the_read() {
        let t = UNIX_EPOCH + Duration::from_secs(1_000);
        assert!(quiescent(&key(990, 990), t));
        // changed within the quiescence window (same tick as the read, or a coarse-granularity filesystem)
        assert!(!quiescent(&key(999, 990), t));
        assert!(!quiescent(&key(990, 999), t));
        assert!(!quiescent(&key(1_000, 990), t));
        // a timestamp in the future is never quiescent
        assert!(!quiescent(&key(990, 5_000), t));
    }

    /// Only filesystems whose inode times the running kernel maintains are ever cached (procfs is not one of them).
    #[cfg(target_os = "linux")]
    #[test]
    fn only_kernel_maintained_local_filesystems_are_cached() {
        assert!(!local_fs(Path::new("/proc/self/status")));
        assert!(!local_fs(Path::new("/nonexistent/for/sure")));
    }

    #[test]
    fn the_stat_key_round_trips_through_the_store_format() {
        let k = key(990, 991);
        assert_eq!(StatKey::from_value(&k.to_value()), Some(k));
    }

    #[cfg(unix)]
    #[test]
    fn a_file_written_just_now_is_hashed_again_on_every_call_so_a_same_tick_rewrite_is_seen() {
        let d = tmpdir();
        let f = d.join("s.sh");
        std::fs::write(&f, "echo one\n").unwrap();
        let a = sha256_of(&f).unwrap();
        assert!(
            !is_cached(&f),
            "a file changed within the quiescence window must never be stored"
        );
        // same size, same (coarse) timestamp tick as the first write
        std::fs::write(&f, "echo two\n").unwrap();
        let b = sha256_of(&f).unwrap();
        assert_ne!(a, b);
        assert_eq!(b, stream_sha256(&f).unwrap());
    }

    /// The rules that decide storage, exercised on real files: a quiescent, writer-free file is stored and reused;
    /// any later change of its bytes — even with the modification time put back — changes its key, so the stored
    /// digest is never returned for the new bytes. A file someone holds open for writing is never stored.
    #[cfg(target_os = "linux")]
    #[test]
    fn a_stored_digest_is_never_returned_for_changed_bytes() {
        let d = tmpdir();
        let f = d.join("impl.py");
        std::fs::write(&f, "print('approved')\n").unwrap();
        let old = SystemTime::now() - Duration::from_secs(3600);
        std::fs::File::options()
            .write(true)
            .open(&f)
            .unwrap()
            .set_modified(old)
            .unwrap();
        let g = d.join("held.py");
        std::fs::write(&g, "x = 1\n").unwrap();
        let _writer = std::fs::File::options().append(true).open(&g).unwrap();
        // ctime is "now": wait out the quiescence window rather than faking it
        std::thread::sleep(QUIESCENCE + Duration::from_millis(200));
        let k0 = stat_key(&f).unwrap();
        if !no_writer(&f, &k0) || !local_fs(&f) {
            eprintln!("the temporary directory is not a local, lease-granting filesystem; the cache stays disabled here (nothing to test)");
            return;
        }
        let a = sha256_of(&f).unwrap();
        assert!(is_cached(&f), "a quiescent, writer-free file is stored");
        assert_eq!(sha256_of(&f).unwrap(), a);
        // rewrite with the same size, then put the modification time back: ctime still moves
        std::fs::write(&f, "print('swapped!')\n").unwrap();
        std::fs::File::options()
            .write(true)
            .open(&f)
            .unwrap()
            .set_modified(old)
            .unwrap();
        let k1 = stat_key(&f).unwrap();
        assert_eq!(
            (k1.size, k1.mtime_ns, k1.ino),
            (k0.size, k0.mtime_ns, k0.ino)
        );
        assert_ne!(k1.ctime_ns, k0.ctime_ns);
        let b = sha256_of(&f).unwrap();
        assert_ne!(a, b, "a stored digest was returned for changed bytes");
        assert_eq!(b, stream_sha256(&f).unwrap());
        // a file held open for writing is never stored, even once quiescent
        let kg = stat_key(&g).unwrap();
        assert!(
            !no_writer(&g, &kg),
            "the lease probe must see the open writer"
        );
        sha256_of(&g).unwrap();
        assert!(!is_cached(&g));
        let _ = std::fs::remove_dir_all(&d);
    }
}
