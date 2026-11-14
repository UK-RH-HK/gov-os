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

Plan and logs live in the folder named by ``W171_STATE``. ``gov_x_calls.jsonl`` holds one line for every call except
``--version``: ``{"t": <epoch seconds>, "argv", "cwd"}``.
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


def log(argv):
    os.makedirs(STATE, exist_ok=True)
    fd = os.open(os.path.join(STATE, "gov_x_calls.jsonl"), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        os.write(fd, (json.dumps({"t": time.time(), "argv": argv, "cwd": os.getcwd()}) + "\n").encode())
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
    for line in text.splitlines():
        try:
            doc = json.loads(line)
        except ValueError:
            sys.stdout.write(line + "\n")
            continue
        result = doc.get("result") if isinstance(doc, dict) else None
        if isinstance(result, dict) and p.get("store_commit"):
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
