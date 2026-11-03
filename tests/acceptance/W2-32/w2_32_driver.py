"""The W2-32 tests' driver: one call of the code under test in a child process, answered as one JSON line.

``python3 w2_32_driver.py '{"op": ..., ...}'`` prints ``{"gov": <the gov imported>, "result": ...}`` or, when the call
raised, ``{"gov": ..., "raised": {"type", "types", "message", "traceback"}}``. Only public interfaces are called; the
README names them. The stand-in rerankers are here: none loads a model.
"""

from __future__ import annotations

import json
import subprocess
import sys
import traceback


def dying_process_loader():
    """A reranker that loads and then dies: its process prints the "loaded" line and exits, so the first score
    writes to a closed pipe or reads an empty answer (W2-M104)."""
    def load():
        process = subprocess.Popen([sys.executable, "-c", "print('{\"device\": \"cpu\"}', flush=True)"],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        json.loads(process.stdout.readline())  # loaded
        process.wait()

        def score(query, texts):
            process.stdin.write(json.dumps([query, texts]) + "\n")
            process.stdin.flush()
            return json.loads(process.stdout.readline())

        return score
    return load


def raising_loader(name):
    errors = {"BrokenPipeError": BrokenPipeError, "ConnectionResetError": ConnectionResetError,
              "EOFError": EOFError, "RuntimeError": RuntimeError, "JSONDecodeError": None}

    def load():
        def score(query, texts):
            if name == "JSONDecodeError":
                return json.loads("")
            raise errors[name](f"the stand-in reranker died after loading ({name})")
        return score
    return load


def constant_loader():
    def load():
        return lambda query, texts: [0.0 for _ in texts]
    return load


def reranker(spec):
    if spec is None:
        return None  # the default reranker
    if spec == "dies-process":
        return dying_process_loader()
    if spec.startswith("dies:"):
        return raising_loader(spec.split(":", 1)[1])
    if spec == "constant":
        return constant_loader()
    raise ValueError(f"no stand-in reranker {spec!r}")


def run(call):
    op = call["op"]
    if op == "semantic_search":
        from gov.retrieval import semantic
        return semantic.search(call["root"], call["query"], refresh=call.get("refresh", False))
    if op == "semantic_refresh":
        from gov.retrieval import semantic
        return semantic.refresh(call["root"])
    if op == "manifest":
        from gov.retrieval import semantic
        return semantic.manifest(call["root"])
    if op == "retrieve":
        from gov.retrieval.retrieve import retrieve
        return retrieve(call["root"], call["query"], reranker=reranker(call.get("reranker")))
    if op == "fusion_search":
        from gov.retrieval import fusion
        from gov.retrieval.rerank import last_outcome
        answer = fusion.search(call["root"], call["query"], call.get("limit"), refresh=call.get("refresh", False),
                               reranker=reranker(call.get("reranker")))
        return {**answer, "outcome": last_outcome()}
    if op == "rerank":
        from gov.retrieval.rerank import last_outcome, rerank
        answers = []
        for _ in range(call.get("times", 1)):
            ranked = rerank(call["query"], call["candidates"], reranker(call.get("reranker")))
            answers.append({"ranked": ranked, "outcome": last_outcome()})
        return answers
    if op == "ensure":
        from gov.retrieval import ollama
        return {"shared": ollama.ensure_available(timeout_s=call.get("timeout_s", 3.0)),
                "query": ollama.ensure_query_available(timeout_s=call.get("timeout_s", 3.0))}
    if op == "learning_record":
        from gov.retrieval import learning
        return learning.record(call["root"], call["miss"])
    if op == "learning_events":
        from gov.retrieval import learning
        return learning.events(call["root"])
    raise ValueError(f"no op {op!r}")


def main():
    import gov
    call = json.loads(sys.argv[1])
    out = {"gov": gov.__file__}
    try:
        out["result"] = run(call)
    except BaseException as error:  # reported, so a case can say what was raised
        out["raised"] = {"type": type(error).__name__, "types": [kind.__name__ for kind in type(error).__mro__],
                         "message": str(error), "traceback": traceback.format_exc()}
    print(json.dumps(out, default=str))


if __name__ == "__main__":
    main()
