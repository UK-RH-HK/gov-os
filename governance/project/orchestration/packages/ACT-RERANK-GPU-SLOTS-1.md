# ACT-RERANK-GPU-SLOTS-1: at most two rerankers on the GPU; the embedder is never pushed off (DEC-1031 item 2)

For the owner's operator. **It replaces ACT-RERANK-CPU-1, which must not be applied:** the GPU agent measured a
reranker on the CPU at more than 100 s per query on a loaded machine (against 0.18 s p50 on the GPU), so moving every
reranker to the CPU would cripple retrieval. It writes two files in your reranker environment under `~/.local/share`
(yours, not the repository's).

## 1. What the GPU agent measured (`drafts/LB-PLAN-gpu.md`)
- Each reranker on the GPU takes about **3.5 GiB** (bf16 weights 2.8 GiB allocated, 3.2 GiB reserved, plus its CUDA
  context). Nine were resident at 11:58; **at 12:16 the card held 15.1 of 16.3 GB with 11 reranker processes**, the
  state that preceded last night's crashes. WSL's kernel log holds 1,440 GPU allocation failures (`dxg`, ENOMEM).
- The embedder needs about 2.5 to 3.5 GiB (pinned since 12:05). Embedder plus two rerankers: about 10.5 GiB of 16.3,
  with room to spare.

## 2. The change
A small module in the reranker environment, loaded at every start through a `.pth` line (which Python runs at
start-up, also under the worker's `-I`): each reranker process tries to hold one of two lock files
(`/tmp/gov-os-rerank-gpu-0.lock`, `-1.lock`) for its whole life. With one, it keeps the GPU; without one, it hides the
GPU (`CUDA_VISIBLE_DEVICES=-1`) and runs on the CPU. A lock is released when its process ends, however it ends. Any
error inside it hides the GPU (fails safe for the embedder). `GOV_RERANK_GPU_SLOTS` changes the number (default 2).
**Tested** in a throwaway environment: four processes started together: two kept the GPU (slots 0 and 1), two got
`CUDA_VISIBLE_DEVICES=-1`; after they ended, a new one took slot 0.
**What it does not do:** the rerankers already running keep their GPU memory until their sessions end (they are
leads' and workers' processes; stopping them would break their searches). New ones obey the limit at once. The
overflow rerankers run on the CPU, slowly; W2-112's shared reranker (one process on the GPU for every session)
removes the overflow, and moves up in the plan (P1-LOAD-BALANCE-1, step 6).

## 3. The commands
```
V=$HOME/.local/share/gov-os/reranker-venv
SP=$($V/bin/python -I -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")
cp /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/gov_reranker_gpu_slot.py "$SP/"
echo 'import gov_reranker_gpu_slot' > "$SP/gov-reranker-gpu-slot.pth"
$V/bin/python -I -c "import os; print('slot', os.environ.get('GOV_RERANK_GPU_SLOT'), 'CUDA_VISIBLE_DEVICES', os.environ.get('CUDA_VISIBLE_DEVICES'))"
```
The last line prints `slot 0` or `slot 1` (a free slot) or `CUDA_VISIBLE_DEVICES -1` (both taken); either shows it is
in force. (The module is staged in the CTO's scratch while its commits are on hold; it is committed to
`governance/project/orchestration/tools/gov_reranker_gpu_slot.py` once you say the ACTs are done.)

## 4. The check
The dispatcher's `GPU:` line counts the reranker holders; once today's resident ones have ended it shows at most
`reranker (2)`, and the GPU's memory stays under about 11 GB.

## 5. Undo
`rm "$SP/gov-reranker-gpu-slot.pth" "$SP/gov_reranker_gpu_slot.py"`. W2-112's shared reranker replaces it (its ticket
then removes these files).
