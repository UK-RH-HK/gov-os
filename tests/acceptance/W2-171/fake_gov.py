"""The planted ``gov`` (a script the world copies into a ``pin-<12 hex>`` folder; Interface 6).

It answers ``gov --version`` and ``gov retrieve [options] <question> --json`` from a plan, and nothing else (any other
subcommand is logged and refused: a rebuild, a restart or a model call by the runner would show in the call log).

Where it finds its plan and logs: the folder named by ``W171_STATE`` (the test's world passes it to every child, so a
world copied whole still reads its own plan), else ``state/`` beside this file.

* ``gov_plan.json``: ``{"questions": {<question text>: <spec>}, "default": <spec>}``. A spec:
    ``calls``  the ranked calls, each a list of items: ``"d"`` a distractor, ``"g"`` / ``"g<i>"`` gold ``<i>``
               (or a dict ``{"k": "g", "routes": [...]}``); a call that is not the last carries ``continuation``;
    ``gold``   ``[[path, first, last], ...]``;
    ``fault``  ``null`` or ``rerank`` (``rerank.by`` private), ``lexical`` / ``semantic`` (route unavailable),
               ``semantic_missing`` (route absent), ``pool`` (the pool's rerank fallen back), ``nolist`` (evidence not
               a list), ``unresolved`` (the empty UNRESOLVED_IDS bundle, no rerank: not degraded), ``exit`` (exit 1);
    ``mutate_store``  ``{"path": <file>, "data": <text>}`` appended to the file when the question is asked;
    ``by_occ`` ``{"<n>": {<keys to override>}}`` for the n-th time this question (and token) is asked.
* ``gov_calls.jsonl``: one line per call: argv, the three variables the runner must set or unset, the question
  (the test's own log, never under the run folder).
When ``OLLAMA_HOST`` / ``GOV_QUERY_OLLAMA_HOST`` are set, one ``POST /api/embed`` goes to each; when the file
``$HOME/.cache/gov-os/rerank.sock`` exists, one line goes to it: only what the real ``gov`` does at a search.
"""
import fcntl
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
STATE = os.environ.get("W171_STATE") or os.path.join(HERE, "state")
VALUE_FLAGS = {"--ticket", "--id", "--radius", "--batch-size", "--bundle-budget", "--continue", "--root"}


def locked_append(name, text):
    fd = os.open(os.path.join(STATE, name), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        os.write(fd, text.encode("utf-8"))
    finally:
        os.close(fd)


def occurrence(key):
    os.makedirs(os.path.join(STATE, "gov_state"), exist_ok=True)
    path = os.path.join(STATE, "gov_state", hashlib.sha1(key.encode("utf-8")).hexdigest())
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        raw = os.read(fd, 32).decode() or "0"
        n = int(raw) + 1
        os.lseek(fd, 0, os.SEEK_SET)
        os.ftruncate(fd, 0)
        os.write(fd, str(n).encode())
        return n
    finally:
        os.close(fd)


def parse(args):
    options, question, token, i = {}, None, None, 0
    while i < len(args):
        a = args[i]
        if a == "--json":
            options["json"] = True
        elif a in VALUE_FLAGS:
            options[a] = args[i + 1]
            i += 1
        elif a.startswith("--"):
            options[a] = True
        else:
            question = a
        i += 1
    return question, options.get("--continue"), options


def touch_servers():
    import http.client
    for var in ("OLLAMA_HOST", "GOV_QUERY_OLLAMA_HOST"):
        host = os.environ.get(var)
        if host:
            conn = http.client.HTTPConnection(host, timeout=10)
            conn.request("POST", "/api/embed", json.dumps({"model": "stub", "input": "x"}),
                         {"Content-Type": "application/json"})
            conn.getresponse().read()
            conn.close()
    sock = os.path.join(os.environ.get("HOME", ""), ".cache", "gov-os", "rerank.sock")
    if os.path.exists(sock):
        import socket
        s = socket.socket(socket.AF_UNIX)
        s.settimeout(10)
        s.connect(sock)
        s.sendall(b'{"op": "rerank", "n": 1}\n')
        s.recv(100)
        s.close()


def item(kind, spec, call, j, text):
    routes = ["lexical", "semantic"]
    if isinstance(kind, dict):
        routes = kind.get("routes", routes)
        kind = kind["k"]
    if kind.startswith("g"):
        path, first, last = spec["gold"][int(kind[1:] or 0)]
    else:
        digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
        path, first, last = f"docs/other/d-{digest}-{call}-{j}.md", 1, 3
    return {"path": path, "start_line": first, "end_line": last, "text": f"text of {path} lines {first}-{last}",
            "routes": routes}


def main():
    argv = sys.argv[1:]
    if argv[:1] == ["--version"]:
        print("gov planted 0")
        return 0
    os.makedirs(STATE, exist_ok=True)
    env = {k: os.environ.get(k) for k in ("GOV_ROLE", "GOV_STORE", "GOV_TICKET")}
    question, token, options = parse(argv[1:]) if argv[:1] == ["retrieve"] else (None, None, {})
    locked_append("gov_calls.jsonl", json.dumps({"argv": argv, "env": env, "q": question, "token": token,
                                                            "cwd": os.getcwd()}) + "\n")
    if argv[:1] != ["retrieve"] or question is None:
        return 2
    with open(os.path.join(STATE, "gov_plan.json"), encoding="utf-8") as f:
        plan = json.load(f)
    spec = dict(plan["questions"].get(question) or plan.get("default") or {"calls": [["d"] * 10]})
    spec.update((spec.get("by_occ") or {}).get(str(occurrence(f"{question}|{token or ''}")), {}))
    if spec.get("mutate_store"):
        with open(spec["mutate_store"]["path"], "ab") as f:
            f.write(spec["mutate_store"]["data"].encode("utf-8"))
    touch_servers()
    fault = spec.get("fault")
    if fault == "exit":
        return 1
    calls = spec.get("calls") or [["d"] * 10]
    index = int(token[1:]) if token else 0
    evidence = [item(k, spec, index, j, question) for j, k in enumerate(calls[index])]
    result = {"evidence": evidence, "continuation": f"c{index + 1}" if index + 1 < len(calls) else None,
              "facets": {"lexical": {"available": True}, "semantic": {"available": True}},
              "rerank": {"by": "service"}, "pool": {"fallback": False}, "stopping_reason": "BUDGET"}
    if fault == "rerank":
        result["rerank"] = {"by": "private"}
    elif fault in ("lexical", "semantic"):
        result["facets"][fault] = {"available": False}
    elif fault == "semantic_missing":
        del result["facets"]["semantic"]
    elif fault == "pool":
        result["pool"] = {"fallback": True}
    elif fault == "nolist":
        result["evidence"] = "none"
    elif fault == "unresolved":
        result = {"evidence": [], "continuation": None, "stopping_reason": "UNRESOLVED_IDS",
                  "gaps": [{"id": "DEC-9999"}]}
    if os.environ.get("W171_STDERR_WORDS"):
        sys.stderr.write(os.environ["W171_STDERR_WORDS"] + "\n")
    sys.stdout.write(json.dumps({"ok": True, "result": result}) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
