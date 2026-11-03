#!/usr/bin/env python3
"""While a shared reranker service (rerank_service.py) runs, hold every reranker GPU slot it does not hold itself, so
no private reranker joins it on the GPU (the owner, 2026-11-02 ~20:35: the service, two private rerankers and both
embedders can exceed the GPU's budget; DEC-1036 lets one private beside the service, which reaches the budget, and the
service rises to about 6.4 GB under load). Private rerankers then wait or go unranked, named (ACT-RERANK-WAIT-1),
never onto the CPU. Stricter only; ends by itself (its locks with it) once no service has run for GRACE seconds.

    python3 rerank_service_slot_hold.py [--once]      (detached by the CTO: setsid -f ... >> log/rerank-slot-hold.log)

Env for tests: GOV_RERANK_GPU_LOCK_DIR (default /tmp), GOV_RERANK_GPU_SLOTS (default 2), HOLD_POLL_S (2), HOLD_GRACE_S (60),
HOLD_SERVICE_MATCH (default rerank_service.py)."""
import fcntl, os, sys, time

FOLDER = os.environ.get("GOV_RERANK_GPU_LOCK_DIR", "/tmp")
SLOTS = int(os.environ.get("GOV_RERANK_GPU_SLOTS", "2"))
POLL = float(os.environ.get("HOLD_POLL_S", "2"))
GRACE = float(os.environ.get("HOLD_GRACE_S", "60"))
MATCH = os.environ.get("HOLD_SERVICE_MATCH", "rerank_service.py")


def log(msg):
    print(time.strftime("%F %T"), msg, flush=True)


def services():
    found = []
    for p in os.listdir("/proc"):
        if p.isdigit() and int(p) != os.getpid():
            try:
                argv = open(f"/proc/{p}/cmdline", "rb").read().split(b"\0")
            except OSError:
                continue
            if any(os.path.basename(a.decode(errors="replace")) == MATCH for a in argv[:3]):
                found.append(int(p))
    return found


def service_holds_slot(pids):
    """Whether one of the running services already holds a GPU reranker slot lock of its own (its open files)."""
    names = {os.path.realpath(os.path.join(FOLDER, f"gov-os-rerank-gpu-{i}.lock")) for i in range(SLOTS)}
    for pid in pids:
        try:
            for fd in os.listdir(f"/proc/{pid}/fd"):
                try:
                    if os.path.realpath(os.readlink(f"/proc/{pid}/fd/{fd}")) in names:
                        return True
                except OSError:
                    continue
        except OSError:
            continue
    return False


def main():
    held = {}
    watch = "--watch" in sys.argv  # 23:05: a standing watcher; it never exits, so a later service is covered too
    last_seen = time.time() if services() else 0.0
    if not last_seen and not watch:
        log("no shared reranker service running; nothing to hold")
        return 0
    if watch:
        log("watching for shared reranker services (standing; DEC-1043 item 2)")
    while True:
        running = services()
        if running and not service_holds_slot(running):
            last_seen = time.time()  # a service is starting: let it take its own slot first (never race it)
        elif running:
            last_seen = time.time()
            for i in range(SLOTS):
                if i in held:
                    continue
                fd = os.open(os.path.join(FOLDER, f"gov-os-rerank-gpu-{i}.lock"), os.O_CREAT | os.O_RDWR, 0o600)
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    held[i] = fd
                    log(f"holding GPU reranker slot {i} (service pids {running})")
                except OSError:
                    os.close(fd)  # held by the service itself, or by a private reranker that got there first
        elif held and time.time() - last_seen > GRACE:
            for i, fd in held.items():
                os.close(fd)
                log(f"released GPU reranker slot {i}: no service for {GRACE:.0f} s")
            held = {}
            if not watch:
                return 0
        elif not held and not watch and time.time() - last_seen > GRACE:
            return 0
        if "--once" in sys.argv:
            return 0
        time.sleep(POLL)


if __name__ == "__main__":
    sys.exit(main())
