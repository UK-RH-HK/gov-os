# BR-AR-0028 hermeticity probe: logs every open()/sqlite3.connect()/os.* mutation whose path is under the
# machine-wide gov-bridge store roots ($HOME/.cache/gov-bridge/store/** or store-*/**) or the shared telemetry dir,
# with the pytest test id active at the time. Installed via PYTHONPATH so subprocesses of the suite inherit it.
import os, sys, json
_LOG = os.environ.get("BRAR28_AUDIT_LOG")
_HOME = os.path.join(os.path.expanduser("~"), ".cache", "gov-bridge")
_STORE_PREFIX = os.path.join(_HOME, "store")      # matches store/... AND store-<RUN>/...
_TELE_PREFIX = os.path.join(_HOME, "telemetry")
_busy = [False]
_EVENTS = {"open", "sqlite3.connect", "os.remove", "os.rename", "os.mkdir", "os.rmdir", "shutil.move",
           "shutil.rmtree", "os.truncate", "os.chmod"}

def _norm(p):
    try:
        if isinstance(p, (bytes, os.PathLike)):
            p = os.fsdecode(p)
    except Exception:
        return None
    if not isinstance(p, str):
        return None
    if p.startswith("file:"):
        p = p[5:]
    p = p.split("?", 1)[0]
    try:
        return os.path.abspath(p)
    except Exception:
        return None

def _hook(event, args):
    if _busy[0] or not _LOG or event not in _EVENTS or not args:
        return
    p = _norm(args[0])
    if p is None:
        return
    kind = "store" if p.startswith(_STORE_PREFIX) else ("telemetry" if p.startswith(_TELE_PREFIX) else None)
    if kind is None:
        return
    _busy[0] = True
    try:
        mode = args[1] if len(args) > 1 and event == "open" else None
        rec = {"kind": kind, "event": event, "path": p, "mode": str(mode), "pid": os.getpid(),
               "test": os.environ.get("PYTEST_CURRENT_TEST"), "GOVBRIDGE_STORE": os.environ.get("GOVBRIDGE_STORE")}
        with open(_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
    finally:
        _busy[0] = False

sys.addaudithook(_hook)
