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


def recording_loader(path, word):
    """A reranker that keeps every text it is given (appended to ``path`` as JSON lines) and scores each by how often
    it holds ``word`` (S7: what the reranker reads)."""
    def load():
        def score(query, texts):
            with open(path, "a", encoding="utf-8") as out:
                for text in texts:
                    out.write(json.dumps(text) + "\n")
            return [float(text.lower().count(word)) for text in texts]
        return score
    return load


def hashed_score(text):
    """A score of its own for every text (DEC-1067 (f)'s order check): no two texts tie."""
    import hashlib
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:12], 16) / float(16 ** 12)


def calls_loader(path):
    """A reranker that keeps each request it is given (one JSON line per call: its texts) and scores each text by
    ``hashed_score``."""
    def load():
        def score(query, texts):
            with open(path, "a", encoding="utf-8") as out:
                out.write(json.dumps(list(texts)) + "\n")
            return [hashed_score(text) for text in texts]
        return score
    return load


def rank_score(text):
    """The S8 stand-in's score of a text: its ``rankNN`` (0 without one), plus half a hash fraction of the text, so
    no two texts tie and the ranks still decide (each fraction is under 1). Rewrite-Reason: the padded bound groups
    requests by length (ties in the pool's order): with no ties, the unbatched order is the scores' alone."""
    import re
    found = [int(n) for n in re.findall(r"\brank(\d{2})\b", text)]
    return float(max(found) if found else 0) + 0.5 * hashed_score(text)


def ranks_loader(path):
    """A reranker that keeps each request (one JSON line per call) and scores each text by ``rank_score`` (S8)."""
    def load():
        def score(query, texts):
            with open(path, "a", encoding="utf-8") as out:
                out.write(json.dumps(list(texts)) + "\n")
            return [rank_score(text) for text in texts]
        return score
    return load


def code_route_stand_in(spec):
    """Replace the code route (the real code-graph tool cannot run in the launch sandbox): a question naming
    ``spec["symbol"]`` gets the chunks of ``spec["paths"]``, in that order, as the route's hits; any other none."""
    from gov.retrieval import code_route

    def route(root, query, chunks, *args, **kwargs):
        if spec["symbol"] not in query:
            return None
        hits = [chunk for path in spec["paths"] for chunk in sorted(
            (c for c in chunks.values() if c["path"] == path), key=lambda c: c["start_line"])]
        return hits, {"available": True, "reason": None}

    code_route.route = route


def reranker(spec):
    if spec is None:
        return None  # the default reranker
    if spec.startswith("ranks:"):
        return ranks_loader(spec.split(":", 1)[1])
    if spec.startswith("calls:"):
        return calls_loader(spec.split(":", 1)[1])
    if spec.startswith("record:"):
        _, path, word = spec.split(":", 2)
        return recording_loader(path, word)
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
    if op == "lexical_search":  # DEC-1068's index-time methods: the keyword route's answer, refreshed or not
        from gov.retrieval import lexical
        return lexical.search(call["root"], call["query"], refresh=call.get("refresh", False))
    if call.get("code_route"):
        code_route_stand_in(call["code_route"])
    if op == "retrieve":
        from gov.retrieval.retrieve import retrieve
        options = {key: call[key] for key in ("batch_size", "bundle_budget", "continuation", "radius") if key in call}
        return retrieve(call["root"], call["query"], reranker=reranker(call.get("reranker")), **options)
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
                         "message": str(error), "code": getattr(error, "code", None),
                         "traceback": traceback.format_exc()}
    print(json.dumps(out, default=str))


if __name__ == "__main__":
    main()
