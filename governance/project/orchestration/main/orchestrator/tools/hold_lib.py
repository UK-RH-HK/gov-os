"""Shared parts of mem_hold.py and night_hold.py (DEC-1138 (2), (3); CTO scratch tool, stdlib only).

Both tools hold the dispatcher's next lead start by commenting live lines of dispatch/ready.txt, and cooperate on that one
file under an flock on dispatch/ready.lock:

  * every change re-reads ready.txt UNDER the lock, applies its edit to what it just read (so a line the CTO added while
    lines were held is never lost), writes a temp file in the same folder and renames it over ready.txt; if ready.txt
    changed between the read and the rename (an editor that does not take the lock), the pass starts over;
  * a held line keeps its place: `#HELD-MEM <line>` or `#HELD-NIGHT <line>`; releasing removes only that exact prefix.

The inbox items written here carry NO `W2:` line on purpose: the dispatcher reads `W2: <id>` in an unread inbox item as
"an unread inbox item for it (waits for the CTO)" and would stop that ticket's lead starting.

Nothing here kills, signals or matches a process by name. A "running lead" is the dispatcher's own rule (dispatcher.py
lead_w2): a process whose arguments hold the launch form's identity marker and whose working folder is under
~/gov-os-worktrees/<W2>; it is only read from /proc.
"""
import contextlib
import fcntl
import json
import os
import shutil
import time

DEFAULT_ORCH = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator"
DEFAULT_WT = "/home/usain/gov-os-worktrees"
MARKER = 'GOV_ROLE":"orchestrator","GOV_TICKET'  # the launch form's identity, as dispatcher.py and gate_check.py count leads

MEM_PREFIX = "#HELD-MEM "
NIGHT_PREFIX = "#HELD-NIGHT "


class Cfg:
    """Every path in one place; tests pass a planted folder as `orch` and never touch the live ones."""

    def __init__(self, orch=DEFAULT_ORCH, wt=DEFAULT_WT):
        self.orch = orch
        self.wt = wt

    dispatch = property(lambda s: os.path.join(s.orch, "dispatch"))
    ready = property(lambda s: os.path.join(s.orch, "dispatch", "ready.txt"))
    lock = property(lambda s: os.path.join(s.orch, "dispatch", "ready.lock"))
    started = property(lambda s: os.path.join(s.orch, "dispatch", "started.txt"))
    inbox = property(lambda s: os.path.join(s.orch, "dispatch", "inbox"))
    brake = property(lambda s: os.path.join(s.orch, "log", "brake"))
    log = property(lambda s: os.path.join(s.orch, "log"))
    nightly = property(lambda s: os.path.join(s.orch, "log", "nightly"))


def stamp(t=None):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() if t is None else t))


def fstamp(t=None):
    return time.strftime("%Y%m%d-%H%M%S", time.localtime(time.time() if t is None else t))


# ---- reading the machine ------------------------------------------------------------------------------------------

def mem_available_kb(path="/proc/meminfo"):
    try:
        for line in open(path):
            if line.startswith("MemAvailable:"):
                return int(line.split()[1])
    except (OSError, ValueError):
        pass
    return None


def running_leads(cfg, proc_root="/proc"):
    """Sorted W2 ids of the running leads (the dispatcher's rule), read from /proc."""
    out = set()
    base = cfg.wt.rstrip("/") + "/"
    for pid in os.listdir(proc_root):
        if not pid.isdigit():
            continue
        try:
            with open(f"{proc_root}/{pid}/cmdline", "rb") as f:
                argv = [a.decode("utf-8", "replace") for a in f.read().split(b"\0") if a]
            cwd = os.readlink(f"{proc_root}/{pid}/cwd")
        except OSError:
            continue
        if not any(MARKER in a for a in argv) or not cwd.startswith(base):
            continue
        name = cwd[len(base):].split("/")[0]
        if name and not name.endswith("-tests") and not name.startswith("W2-00-"):
            out.add(name)
    return sorted(out)


def started_logs(cfg):
    """The lead logs the dispatcher already started (started.txt: <date> <time> <W2> <brief> <log>)."""
    out = set()
    try:
        for line in open(cfg.started):
            f = line.split()
            if len(f) >= 5 and not line.lstrip().startswith("#"):
                out.add(f[-1])
    except OSError:
        pass
    return out


# ---- ready.txt ----------------------------------------------------------------------------------------------------

def is_live(line):
    s = line.strip()
    return bool(s) and not s.startswith("#")


def ready_w2(line):
    f = line.split()
    return f[0] if f else None


def is_running_lead_line(line, leads, started):
    """The started line of a running lead: the dispatcher says 'running' or 'already started' for it, so it needs no hold."""
    f = line.split()
    return len(f) == 4 and f[0] in leads and f[3] in started


class LockTimeout(Exception):
    pass


@contextlib.contextmanager
def ready_lock(cfg, timeout=10.0):
    os.makedirs(cfg.dispatch, exist_ok=True)
    fd = os.open(cfg.lock, os.O_CREAT | os.O_RDWR, 0o644)
    deadline = time.time() + timeout
    try:
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.time() > deadline:
                    raise LockTimeout(f"ready.lock busy for {timeout} s")
                time.sleep(0.05)
        yield
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def _sig(p):
    st = os.stat(p)
    return (st.st_ino, st.st_size, st.st_mtime_ns)


def rewrite_ready(cfg, fn, backup=False, tries=6, lock_timeout=10.0, after_read=None):
    """Under the lock: read ready.txt, `fn(lines) -> (new_lines, info)`, write a temp file beside it, rename.
    Returns (info, changed). `backup`: keep `ready.txt.pre-hold-<stamp>` (the file as read) when it changes.
    `after_read` is a test hook run between the read and the rename (an unlocked editor's write)."""
    for _ in range(tries):
        with ready_lock(cfg, lock_timeout):
            try:
                sig = _sig(cfg.ready)
                with open(cfg.ready) as f:
                    lines = f.read().splitlines(True)
            except FileNotFoundError:
                return {}, False
            new, info = fn(list(lines))
            if new == lines:
                return info, False
            if after_read:
                after_read()
            tmp = os.path.join(cfg.dispatch, f".ready.txt.hold-tmp-{os.getpid()}")
            with open(tmp, "w") as f:
                f.writelines(new)
                f.flush()
                os.fsync(f.fileno())
            shutil.copymode(cfg.ready, tmp)
            if _sig(cfg.ready) != sig:  # changed since the read: do it again from what is there now
                os.remove(tmp)
                after_read = None
                continue
            if backup:
                bk = f"{cfg.ready}.pre-hold-{fstamp()}"
                n = 1
                while os.path.exists(bk):
                    n += 1
                    bk = f"{cfg.ready}.pre-hold-{fstamp()}-{n}"
                shutil.copy2(cfg.ready, bk)
                info["backup"] = os.path.basename(bk)
            os.replace(tmp, cfg.ready)
            return info, True
    raise LockTimeout("ready.txt kept changing under the rewrite")


def hold_live_lines(lines, prefix, skip=lambda line: False):
    """Comment every live line (except `skip`) as prefix + line. Returns (lines, info)."""
    out, held, w2s = [], [], []
    for l in lines:
        if is_live(l) and not skip(l):
            out.append(prefix + l)
            held.append(l.strip())
        else:
            out.append(l)
        if is_live(l):
            w2s.append(ready_w2(l))
    return out, {"held": held, "live_w2": sorted(set(w2s))}


def release_lines(lines, prefix, handover_prefix=None):
    """Remove exactly `prefix` from the lines that start with it (or re-label them `handover_prefix`)."""
    out, rel = [], []
    for l in lines:
        if l.startswith(prefix):
            rest = l[len(prefix):]
            if handover_prefix:
                out.append(handover_prefix + rest)
            else:
                out.append(rest)
            rel.append(rest.strip())
        else:
            out.append(l)
    return out, {"released": rel}


def count_held(cfg, prefix):
    try:
        return sum(1 for l in open(cfg.ready) if l.startswith(prefix))
    except OSError:
        return 0


# ---- records ------------------------------------------------------------------------------------------------------

def jsonl(path, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(row) + "\n")


def inbox_item(cfg, name, body, t=None):
    os.makedirs(cfg.inbox, exist_ok=True)
    base = os.path.join(cfg.inbox, f"{fstamp(t)}-{name}")
    p, n = base + ".txt", 1
    while os.path.exists(p):
        n += 1
        p = f"{base}-{n}.txt"
    with open(p, "w") as f:
        f.write(body)
    return p


def write_json_atomic(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp-{os.getpid()}"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, path)


def read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


# ---- the other tool's presence (so a release never opens a window the other still holds) ----------------------------

def pid_alive(pid):
    try:
        os.kill(int(pid), 0)  # signal 0 checks existence only; nothing is signalled
        return True
    except (OSError, ValueError, TypeError):
        return False


def active_path(cfg, name):
    return os.path.join(cfg.log, f"{name}.active")


def set_active(cfg, name, on, why=""):
    p = active_path(cfg, name)
    if on:
        write_json_atomic(p, {"pid": os.getpid(), "since": stamp(), "why": why})
    else:
        with contextlib.suppress(OSError):
            os.remove(p)


def is_active(cfg, name):
    d = read_json(active_path(cfg, name))
    return bool(d) and pid_alive(d.get("pid"))
