"""W2-155 run 2, DEC-1159 (2)/(3): ONE request at the new padded bound (48,000) to the live shared reranker, in a GPU
window (GPU use near 0 %, no other reranker request in flight), with nvidia-smi sampled every 20 ms before, during and
after. Shape: the bound's worst case per request, 2 pairs of 24,000 characters (each text 24,000 - len(Q)), i.e. the
longest sequences the bound allows (memory per character is highest for the longest sequences). Never a stream."""
import json
import socket
import subprocess
import sys
import time
from pathlib import Path

SMI = "/usr/lib/wsl/lib/nvidia-smi"
SOCK = str(Path.home() / ".cache/gov-os/rerank.sock")
LOG = Path.home() / ".cache/gov-os/rerank.log"
Q = "Which files implement the leapfrog integrator?"
OUT = Path(sys.argv[1])
SHAPE = sys.argv[2] if len(sys.argv) > 2 else "2x24000"


def smi():
    line = subprocess.run([SMI, "--query-gpu=utilization.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"],
                          capture_output=True, text=True, check=True).stdout.strip()
    return [int(x) for x in line.split(",")]


def text(n, i):
    base = f"[path: docs/part-{i}.md]\n" + ("The integrator advances position and velocity by half steps. " * 800)
    return base[:n]


if SHAPE == "2x24000":
    texts = [text(24_000 - len(Q), i) for i in range(2)]
else:
    count, chars = (int(x) for x in SHAPE.split("x"))
    texts = [text(chars - len(Q), i) for i in range(count)]
padded = len(texts) * max(len(Q) + len(t) for t in texts)
assert padded <= 48_000, padded

before = [smi() for _ in range(5)]
log_before = LOG.stat().st_size
if max(u for u, _, _ in before) > 5:
    print(json.dumps({"refused": "GPU busy", "before": before}))
    sys.exit(3)
sampler = subprocess.Popen([SMI, "--query-gpu=timestamp,utilization.gpu,memory.used", "--format=csv,noheader,nounits",
                            "-lms", "20"], stdout=open(OUT.with_suffix(".smi.csv"), "w"))
time.sleep(1.0)
start = time.perf_counter()
with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as c:
    c.settimeout(60)
    c.connect(SOCK)
    c.sendall((json.dumps([Q, texts]) + "\n").encode())
    answer = json.loads(c.makefile("rb").readline())
round_trip = time.perf_counter() - start
time.sleep(1.5)
sampler.terminate()
sampler.wait()
after = [smi() for _ in range(3)]
with open(LOG, "rb") as f:
    f.seek(log_before)
    log_lines = f.read().decode("utf-8", "replace").splitlines()
rows = []
for line in OUT.with_suffix(".smi.csv").read_text().splitlines():
    parts = [p.strip() for p in line.split(",")]
    if len(parts) == 3 and parts[2].isdigit():
        rows.append((parts[0], int(parts[1]), int(parts[2])))
peak = max(m for _, _, m in rows) if rows else None
base = min(m for _, _, m in before)
total = before[0][2]
result = {"shape": SHAPE, "texts": len(texts), "padded_chars": padded, "round_trip_s": round(round_trip, 3),
          "ok": "scores" in answer, "answer_keys": sorted(answer), "error": answer.get("error"),
          "before": before, "after": after, "samples": len(rows), "peak_used_mib": peak, "baseline_used_mib": base,
          "request_delta_mib": (peak - base) if peak is not None else None, "total_mib": total,
          "budget_mib": total - 2048, "within_budget": peak is not None and peak <= total - 2048,
          "max_util_during": max(u for _, u, _ in rows) if rows else None, "rerank_log_lines": log_lines}
OUT.write_text(json.dumps(result, indent=1))
print(json.dumps({k: v for k, v in result.items() if k not in ("before", "after")}, indent=1))
