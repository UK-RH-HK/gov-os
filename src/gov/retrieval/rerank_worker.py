"""The reranker's own process (W1-19; ADR-0002 §2, DEC-397). Started by ``gov.retrieval.rerank``, never imported.

It runs in the reranker environment, loads the pinned model once, and then answers one line with one line until
its caller closes the pipe: ``[query, [text, …]]`` in, ``[score, …]`` out, as JSON. The first line it writes says
the model is loaded; a process that ends without it has no model, and its reason is on standard error.
"""

import json
import sys


def main(model: str, revision: str) -> None:
    answers, sys.stdout = sys.stdout, sys.stderr  # whatever the libraries print stays out of the answers
    from sentence_transformers import CrossEncoder

    # The snapshot's own configuration carries the instruction and the yes/no scoring; the device is the library's
    # choice (the GPU when there is one).
    encoder = CrossEncoder(model, revision=revision)
    print(json.dumps(True), file=answers, flush=True)
    for line in sys.stdin:
        query, texts = json.loads(line)
        scores = encoder.predict([(query, text) for text in texts])
        print(json.dumps([float(score) for score in scores]), file=answers, flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:3])
