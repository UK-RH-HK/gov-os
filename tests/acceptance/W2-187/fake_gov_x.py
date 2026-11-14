"""The planted ``gov`` of W2-187 (a script the world copies into each ``pin-<12 hex>`` folder).

* ``gov --version`` and ``gov retrieve [options] <question> --json``: W2-171's planted ``gov`` (its plan, its faults, its
  logs), loaded by path (``@FAKE@``), with W2-138's field ``result.store.commit`` added to each answer: the plan's
  ``store_commit``, or the plan's ``other_commit[<question text>]`` for a question whose answer comes from another store.
* ``gov rebuild --integration <branch>`` and ``gov rebuild`` (the maintenance pass, S10): from ``x_plan.json``
  ``{"rebuild": {"exit": 0, "link": <folder>, "advance_to": <commit>, "fix_layout": bool, "sleep": <s>}}``. A successful
  rebuild moves the link's work tree to ``advance_to`` and its store's fingerprint head with it, and drops the layout stamp
  when ``fix_layout``.
* ``gov links --since <rev> --json`` (S10 item 3): ``{"links": {"new": <k>, "refuse": bool}}``; exit 1 with new findings,
  0 with none, 2 when it ``refuse``s (the real command's codes).

* ``{"store_from": "root"}`` in ``x_plan.json`` (review round 1's F-A, the CTO's fix of 2026-11-14): the answer's
  ``result.store.commit`` is then, as the real ``gov`` reports it (``gov.retrieval.retrieve.store_of``), the ``head`` of
  the ``fingerprints`` row of ``<root>/.gov-runtime/store.db``, ``<root>`` the folder the search runs in (``--root`` when
  given, else the working directory, its links followed), or null when that folder holds no store; the plan's
  ``other_commit[<question text>]`` still wins for a question it names. Without the key the answer is as above (the plan's
  ``store_commit`` wherever the search runs).

Plan and logs live in the folder named by ``W171_STATE``. ``gov_x_calls.jsonl`` holds one line for every call except
``--version``: ``{"t": <epoch seconds>, "argv", "cwd", "root", "step"}``: ``root`` the real path of the folder the search
runs in; ``step`` the subcommand of the nearest ancestor process run as ``-m gov.memaudit <step>`` (null when none).
"""
import fcntl
import importlib.util
import io
import json
import os
import sqlite3
import subprocess
import sys
import time

FAKE = "@FAKE@"
STATE = os.environ.get("W171_STATE") or os.path.join(os.path.dirname(os.path.realpath(__file__)), "state")


def plan():
    try:
        with open(os.path.join(STATE, "x_plan.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def root_of(argv):
    """The folder a search runs in, as the real ``gov`` takes it: ``--root <dir>`` when given, else the working
    directory; its links followed."""
    root = os.getcwd()
    if "--root" in argv and argv.index("--root") + 1 < len(argv):
        root = argv[argv.index("--root") + 1]
    return os.path.realpath(root)


def store_commit_at(root):
    """The ``head`` of the ``fingerprints`` row of ``<root>/.gov-runtime/store.db`` (opened read-only), else None."""
    path = os.path.join(root, ".gov-runtime", "store.db")
    if not os.path.isfile(path):
        return None
    try:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            row = con.execute("SELECT head FROM fingerprints LIMIT 1").fetchone()
        finally:
            con.close()
    except sqlite3.Error:
        return None
    return row[0] if row else None


def step_of():
    """The subcommand of the nearest ancestor process run as ``... -m gov.memaudit <step> ...`` (Linux ``/proc``)."""
    pid = os.getppid()
    for _ in range(16):
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                args = [a.decode("utf-8", "replace") for a in f.read().split(b"\0") if a]
            with open(f"/proc/{pid}/stat", encoding="utf-8") as f:
                parent = int(f.read().rsplit(")", 1)[1].split()[1])
        except (OSError, ValueError, IndexError):
            return None
        for i in range(len(args) - 2):
            if args[i] == "-m" and args[i + 1] == "gov.memaudit":
                return args[i + 2]
        if parent <= 1:
            return None
        pid = parent
    return None


def log(argv):
    os.makedirs(STATE, exist_ok=True)
    fd = os.open(os.path.join(STATE, "gov_x_calls.jsonl"), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        os.write(fd, (json.dumps({"t": time.time(), "argv": argv, "cwd": os.getcwd(), "root": root_of(argv),
                                  "step": step_of()}) + "\n").encode())
    finally:
        os.close(fd)


def rebuild():
    spec = plan().get("rebuild") or {}
    if spec.get("sleep"):
        time.sleep(float(spec["sleep"]))
    code = int(spec.get("exit", 0))
    if code != 0:
        sys.stderr.write("planted rebuild failed\n")
        return code
    link, head = spec.get("link"), spec.get("advance_to")
    if link:
        if head:
            subprocess.run(["git", "-C", link, "checkout", "-q", "--detach", head], check=True, capture_output=True)
        con = sqlite3.connect(os.path.join(link, ".gov-runtime", "store.db"))
        if head:
            con.execute("UPDATE fingerprints SET head = ?", (head,))
        if spec.get("fix_layout"):
            con.execute("DROP TABLE IF EXISTS store_layout")
        con.commit()
        con.close()
    print("planted rebuild done")
    return 0


def links():
    spec = plan().get("links") or {}
    if spec.get("refuse"):
        print(json.dumps({"ok": False, "command": "links", "result": {}, "session": None}))
        return 2
    new = int(spec.get("new", 0))
    result = {"summary": f"gov links: {new} new", "new": new, "standing": 0, "findings": []}
    print(json.dumps({"ok": True, "command": "links", "result": result, "session": None}))
    return 1 if new else 0


def retrieve(argv):
    spec = importlib.util.spec_from_file_location("w171_fake_gov", FAKE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    kept, buffer = sys.stdout, io.StringIO()
    sys.stdout = buffer
    try:
        code = module.main()
    finally:
        sys.stdout = kept
    text = buffer.getvalue()
    question, _, _ = module.parse(argv[1:])
    p = plan()
    root = root_of(argv)
    for line in text.splitlines():
        try:
            doc = json.loads(line)
        except ValueError:
            sys.stdout.write(line + "\n")
            continue
        result = doc.get("result") if isinstance(doc, dict) else None
        if isinstance(result, dict) and p.get("store_from") == "root":
            result["store"] = {"commit": (p.get("other_commit") or {}).get(question) or store_commit_at(root),
                               "root": root}
        elif isinstance(result, dict) and p.get("store_commit"):
            result["store"] = {"commit": (p.get("other_commit") or {}).get(question) or p["store_commit"]}
        sys.stdout.write(json.dumps(doc) + "\n")
    return code


def main():
    argv = sys.argv[1:]
    if argv[:1] == ["--version"]:
        print("gov planted 0")
        return 0
    log(argv)
    if argv[:1] == ["rebuild"]:
        return rebuild()
    if argv[:1] == ["links"]:
        return links()
    if argv[:1] == ["retrieve"]:
        return retrieve(argv)
    return 2


if __name__ == "__main__":
    sys.exit(main())
