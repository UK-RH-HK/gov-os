"""The planted ``claude`` (a script the world copies to ``bin/claude``; Interface 6).

Called as the fresh 80 calls it: ``-p --safe-mode --tools "" --no-session-persistence --output-format json --model
<m> --effort high --max-budget-usd <b> --system-prompt <s> --json-schema <j>`` with the prompt on standard input. It
answers one JSON with ``structured_output``, ``usage`` and ``total_cost_usd`` from ``claude_plan.json``, found in the
folder named by ``W171_STATE`` (else ``state/`` beside this file), and logs every call to ``claude_calls.jsonl``
there (the test's own log: the prompt, the argv, the model, the cost, the time).

Plan: ``{"q": {<question text>: {"id", "reader": [<response>...], "grader": [..], "check": [..],
"cost": {"reader", "grader", "check"}}}, "cost": {...}, "sleep": <seconds>}``. A response is the structured output
(a reader's object, or a grade word for a grader) or ``"empty"``: the call returns nothing (exit 1, no standard
output, or the text in ``garbage``). Responses are taken by the number of this question's calls of that kind so far
(a call run once more is the next one). Reader or grader kind: by the schema (``verdict`` or ``grade``) and the model
(``opus`` grades, ``sonnet`` checks).
"""
import fcntl
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.realpath(__file__))
STATE = os.environ.get("W171_STATE") or os.path.join(HERE, "state")


def locked(name, text=None, number=None):
    fd = os.open(os.path.join(STATE, name), os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        if text is not None:
            os.write(fd, text.encode("utf-8"))
    finally:
        os.close(fd)


def counter(key):
    os.makedirs(os.path.join(STATE, "claude_state"), exist_ok=True)
    safe = key.replace("/", "_").replace(" ", "_")[:150]
    path = os.path.join(STATE, "claude_state", safe)
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        n = int(os.read(fd, 32).decode() or "0")
        os.lseek(fd, 0, os.SEEK_SET)
        os.ftruncate(fd, 0)
        os.write(fd, str(n + 1).encode())
        return n
    finally:
        os.close(fd)


def main():
    argv = sys.argv[1:]
    flags = {}
    for i, a in enumerate(argv):
        if a.startswith("--") and i + 1 < len(argv):
            flags[a] = argv[i + 1]
    prompt = sys.stdin.read()
    schema = json.loads(flags.get("--json-schema", "{}"))
    model = flags.get("--model", "")
    props = schema.get("properties", {})
    kind = "reader" if "verdict" in props else ("grader" if "opus" in model else "check")
    first = prompt.split("\n\nGold answer: ", 1)[0] if kind != "reader" else prompt.split("\n", 1)[0]
    text = first[len("Question: "):] if first.startswith("Question: ") else first
    os.makedirs(STATE, exist_ok=True)
    with open(os.path.join(STATE, "claude_plan.json"), encoding="utf-8") as f:
        plan = json.load(f)
    spec = plan.get("q", {}).get(text, {})
    n = counter(f"{spec.get('id', 'unknown')}|{kind}")
    script = spec.get(kind) or []
    response = script[n] if n < len(script) else (script[-1] if script else None)
    started = time.time()
    if plan.get("sleep"):
        time.sleep(plan["sleep"])
    empty = response in (None, "empty")
    cost = 0.0 if empty else float((spec.get("cost") or plan.get("cost") or {}).get(kind, 0.01))
    locked("claude_calls.jsonl", json.dumps({
        "qid": spec.get("id"), "kind": kind, "inv": n, "model": model, "usd": cost, "empty": empty,
        "argv": argv, "prompt": prompt, "t0": started, "t1": time.time()}) + "\n")
    if os.environ.get("W171_STDERR_WORDS"):
        sys.stderr.write(os.environ["W171_STDERR_WORDS"] + "\n")
    if empty:
        sys.stdout.write(plan.get("garbage", ""))
        return 1
    structured = response if kind == "reader" else {"grade": response, "reason": "planted"}
    sys.stdout.write(json.dumps({"type": "result", "is_error": False, "result": "", "structured_output": structured,
                                 "usage": {"input_tokens": 10, "output_tokens": 5, "cache_read_input_tokens": 0,
                                           "cache_creation_input_tokens": 0},
                                 "total_cost_usd": cost}) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
