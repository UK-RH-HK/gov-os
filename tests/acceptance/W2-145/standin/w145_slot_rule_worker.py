"""A private reranker of an older tree that keeps the GPU slot rule (the W2-145 tests' stand-in for W2-112's worker,
or any worker under the interim ``gov-reranker-gpu-slot.pth``). Run with the planted reranker environment's
interpreter: ``python -I w145_slot_rule_worker.py``.

The rule as ACT-RERANK-WAIT-1 states it, written here from the rule and not taken from the code under test: hold one
of ``GOV_RERANK_GPU_SLOTS`` lock files ``gov-os-rerank-gpu-<i>.lock`` in ``GOV_RERANK_GPU_LOCK_DIR`` (an exclusive,
non-blocking ``flock``) for the process's life, waiting up to ``GOV_RERANK_GPU_WAIT_S`` seconds for one; without one,
end named with exit 75 before anything loads. Holding one, load the (stand-in) model on the GPU, print
``{"device": ...}`` and end 0.
"""

import fcntl
import json
import os
import sys
import time

NO_SLOT = 75


def main() -> int:
    slots = int(os.environ.get("GOV_RERANK_GPU_SLOTS", "2"))
    wait = float(os.environ.get("GOV_RERANK_GPU_WAIT_S", "20"))
    folder = os.environ["GOV_RERANK_GPU_LOCK_DIR"]
    deadline, held = time.monotonic() + wait, None
    while held is None:
        for number in range(slots):
            descriptor = os.open(os.path.join(folder, f"gov-os-rerank-gpu-{number}.lock"), os.O_CREAT | os.O_RDWR,
                                 0o600)
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                os.close(descriptor)
                continue
            held = descriptor
            break
        if held is None:
            if time.monotonic() >= deadline:
                print("w145 slot-rule worker: no GPU slot free within its wait", file=sys.stderr, flush=True)
                return NO_SLOT
            time.sleep(0.2)
    from sentence_transformers import CrossEncoder

    encoder = CrossEncoder("Qwen/Qwen3-Reranker-0.6B", revision="e61197ed45024b0ed8a2d74b80b4d909f1255473",
                           device="cuda")
    print(json.dumps({"device": str(encoder.device)}), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
