# ACT-RERANK-CPU-1: no reranker can push the embedder off the GPU (DEC-1031 item 2)

For the owner's operator (a plain command; it writes one file in your reranker environment under `~/.local/share`,
which is yours, not the repository's).

## 1. Context
Last night 8 to 10 rerankers ran at once (one per searching session), each putting its own copy of
`Qwen/Qwen3-Reranker-0.6B` on the GPU: sentence-transformers uses the GPU whenever torch finds one. At 04:30 the GPU
crashed (`CUDA error: unknown error`) and at 04:34 the shared embedder reloaded with 1.9 GiB free: 0/29 layers on the
GPU, 30 to 100 times slower, for seven hours (DEC-1029).

## 2. What is done already, and what this ACT adds
- **Done (the CTO, 2026-11-02 12:05, under DEC-1031 item 2):** the shared embedder is pinned in GPU memory
  (`keep_alive: -1`; `/api/ps` shows `expires_at` 2319 and 2.37 GB in VRAM; an ordinary request does not undo it). Its
  share is held first while its runner lives. If the runner crashes and reloads, the dispatcher's GPU watch (v4.5)
  alerts at once and the CTO re-pins it.
- **This ACT:** the reranker environment hides the GPU from every reranker it starts, until the shared reranker
  (W2-112) runs on the GPU with its own budget. One `.pth` file in the environment's site-packages, which Python runs
  at start-up, also in the isolated mode (`-I`) the worker uses. Tested in a throwaway environment: the line applies
  under `-I`; and with the GPU hidden, the reranker environment's torch reports no CUDA (`torch.cuda.is_available()`
  False; today True).
- **The cost:** rerankers run on the CPU, as their design assumed (ADR-0002; W1-19's case "the rerank process stays
  within 2.5 GB"). In the live hour they used 0.07 cores on average (p95 0.3). Their system memory stays as today
  (up to 8.4 GB for all of them); the shared reranker (W2-112) is what brings that down.

## 3. The commands
```
V=$HOME/.local/share/gov-os/reranker-venv
SP=$($V/bin/python -I -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")
echo 'import os; os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Gov OS: rerankers on the CPU until W2-112 (DEC-1031 item 2)' > "$SP/gov-reranker-cpu.pth"
$V/bin/python -I -c "import torch; print('reranker sees CUDA:', torch.cuda.is_available())"
```
The last line must print `reranker sees CUDA: False`. Rerankers already running keep their GPU memory until their
session ends; new ones start on the CPU.

## 4. The check
The dispatcher's `GPU:` status line shows `reranker (0)` among the holders once the running ones have ended, and the
GPU's memory falls to the embedder's share (about 2.4 to 3.5 GB).

## 5. Undo
`rm "$SP/gov-reranker-cpu.pth"`. When W2-112's shared reranker lands, it takes the GPU with its budget and this file
goes (its ticket says so).
