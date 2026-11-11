# ACT-RERANK-WAIT-1: no reranker on the CPU; without a GPU slot it waits, or the search goes unranked (DEC-1033)

For the owner's operator, in a plain terminal (it copies one file into your reranker environment under
`~/.local/share`; no repository commit). It updates the module ACT-RERANK-GPU-SLOTS-1 installed; the `.pth` stays.

## What changes (the owner's emergency rule, until W2-112's shared reranker is live)
- A reranker worker with one of the two GPU slots keeps the GPU, as today.
- Without one, it waits for one for up to 20 s (`GOV_RERANK_GPU_WAIT_S`), checking once a second; if none frees, it
  ends at once, before torch or the model loads, with `gov reranker: no GPU slot free within 20 s; this search goes
  without reranking` on stderr (exit 75). The search goes on unranked: the bundle's `merge.reranked` is false
  (`src/gov/retrieval/retrieve.py`, `rerank.py` treat an ended worker as "no model", DEC-374).
- **It never falls back to the CPU** (where a query took over 100 s) unless `GOV_RERANK_ALLOW_CPU=1` is set (a test
  or a measurement only). A worker started with the GPU already hidden ends named (exit 76). Any error, a bad setting
  or an interrupt ends it named (exit 70), never with a traceback.
- Only the reranker worker is affected: any other Python run from that environment is untouched (today's module took
  a slot for every Python there, your checks included).
- **Reviewed:** an independent review passed with no blocking finding (`.gov-runtime/scratch/orchestrator/reviews/
  emg-rerank-slot.md`); its finding F2 (a non-finite wait) is fixed; 17 tests pass
  (`tests/unit/orchestration/test_gov_reranker_gpu_slot.py`, `tests/unit/semantic/test_rerank_process.py`), one of them
  end to end through the real `rerank.py` and `rerank_worker.py`.
- **The cost:** W1-19's real-model cases require reranking, so on a busy machine they now fail after the 20 s wait
  instead of grinding for minutes; run them with `GOV_RERANK_ALLOW_CPU=1` when a slot cannot be had.

## The commands
```
V=$HOME/.local/share/gov-os/reranker-venv
SP=$($V/bin/python -I -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")
cp "$SP/gov_reranker_gpu_slot.py" "$SP/gov_reranker_gpu_slot.py.dec1031"
cp /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/gov_reranker_gpu_slot.py "$SP/"
cmp /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/gov_reranker_gpu_slot.py "$SP/gov_reranker_gpu_slot.py" && cat "$SP/gov-reranker-gpu-slot.pth"
```
`cmp` prints nothing; the `.pth` reads `import gov_reranker_gpu_slot`.

## The check
```
# 1. a non-worker Python is untouched: "slot None CUDA_VISIBLE_DEVICES None"
$V/bin/python -I -c "import os; print('slot', os.environ.get('GOV_RERANK_GPU_SLOT'), 'CUDA_VISIBLE_DEVICES', os.environ.get('CUDA_VISIBLE_DEVICES'))"
# 2. a stand-in worker: "slot 0" or "slot 1" and exit 0, or (both taken) after 3 s the named line and exit 75; never "CUDA_VISIBLE_DEVICES -1"
D=$(mktemp -d); echo "import os; print('slot', os.environ.get('GOV_RERANK_GPU_SLOT'), 'CUDA_VISIBLE_DEVICES', os.environ.get('CUDA_VISIBLE_DEVICES'))" > "$D/rerank_worker.py"
GOV_RERANK_GPU_WAIT_S=3 $V/bin/python -I "$D/rerank_worker.py"; echo "exit $?"; rm -r "$D"
```
Rerankers already running keep what they have until their sessions end; new ones obey at once.

## Undo
`cp "$SP/gov_reranker_gpu_slot.py.dec1031" "$SP/gov_reranker_gpu_slot.py"`
