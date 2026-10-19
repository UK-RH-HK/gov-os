"""W2-54 round 2, item 1: does a per-request embedder setting remove the variation? (never committed)

For each setting: RUNS runs; run i embeds a preceding text P (cycling over PRECEDING), then the target T once
(the first embedding of T after another text), then T REPEATS more times. Each text is sent as semantic.py sends a
question: one /api/embed request, model qwen3-embedding:0.6b, input [INSTRUCTION + text], plus the setting's
``options``. Reported per setting: the largest component difference between the first embedding after another text
and its repeats, the largest between repeats, and how many runs differed at all.
"""

import json
import sys
import urllib.request

HOST = "http://127.0.0.1:11434"
MODEL = "qwen3-embedding:0.6b"
INSTRUCTION = "Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery: "
TARGETS = ("context", "The context packet's dropped list in a stable order")
PRECEDING = ("who reads the harbour tide tables", "when are the pear trees pruned",
             "the audit-report type exactly as W2-02 defines it")
RUNS, REPEATS = 6, 3
SETTINGS = {
    "default": None,
    "num_thread=1": {"num_thread": 1},
    "num_thread=20": {"num_thread": 20},
    "seed=42": {"seed": 42},
    "num_thread=1,seed=42": {"num_thread": 1, "seed": 42},
}
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def embed(text, options):
    body = {"model": MODEL, "input": [INSTRUCTION + text]}
    if options is not None:
        body["options"] = options
    request = urllib.request.Request(HOST + "/api/embed", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
    with OPENER.open(request, timeout=300) as reply:
        return json.load(reply)["embeddings"][0]


def largest(a, b):
    return max(abs(x - y) for x, y in zip(a, b))


def main():
    names = sys.argv[1:] or list(SETTINGS)
    for name in names:
        options = SETTINGS[name]
        embed("warm-up " + name, options)  # the first request with new options may reload the runner
        for target in TARGETS:
            first_vs_repeat, repeat_vs_repeat, differed, rows = 0.0, 0.0, 0, []
            for run in range(RUNS):
                preceding = PRECEDING[run % len(PRECEDING)]
                embed(preceding, options)
                first = embed(target, options)
                repeats = [embed(target, options) for _ in range(REPEATS)]
                f = max(largest(first, r) for r in repeats)
                r = max(largest(repeats[0], x) for x in repeats[1:])
                first_vs_repeat, repeat_vs_repeat = max(first_vs_repeat, f), max(repeat_vs_repeat, r)
                differed += (f > 0 or r > 0)
                rows.append(f"run {run} after {preceding[:24]!r}: first-vs-repeats {f:.6f}, repeats {r:.6f}")
            print(f"[{name}] target {target!r}: {RUNS} runs, {differed} differed; "
                  f"largest first-vs-repeats {first_vs_repeat:.6f}, largest repeats-vs-repeats {repeat_vs_repeat:.6f}")
            for row in rows:
                print("   ", row)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
