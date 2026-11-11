# ACT-RERANK-TRIAL-1: the reranker trial, mxbai-rerank-large-v2 first, Qwen3-Reranker-4B in 8-bit second (DEC-1068 (a))

For the owner's operator (steps 0 to 3: the downloads and the installs; installs are never the CTO's, DEC-1058) and
for the CTO (the trial, section 4, under this ACT's approval). Prepared by a research worker for the CTO, 2026-11-04
~09:50, read-only. Every step that downloads nothing and installs nothing was rehearsed in a scratch folder:
`.gov-runtime/scratch/orchestrator/drafts/rerank-trial/rehearsal.log` (R0 to R11, R7b; appendices A to D hold the
probe, the stand-in, the trial worker and the script, whole). Estimates are marked (est.).

**What it changes:** three new folders, nothing else. `~/.cache/gov-os-trial/` (the downloads, as their own
`HF_HOME`, and the freeze), `~/.local/share/gov-os/reranker-trial-venv/` (a clone of the reranker venv plus
bitsandbytes, accelerate and psutil), `~/.local/share/gov-os/rerank-trial/` (the trial service's two files and its
socket). **What it never touches:** the live reranker venv, the pins, `~/.cache/huggingface` (read only, for today's
0.6B), the live socket and log in `~/.cache/gov-os/`, the embedders. **Nothing switches the live service:** a
candidate is only ever served by the trial copy on its own socket, to the trial's harness and probe.

## 1. The candidates

| | mxbai-rerank-large-v2 (first) | Qwen3-Reranker-4B, 8-bit (second) |
|---|---|---|
| licence | Apache-2.0: [card](https://huggingface.co/mixedbread-ai/mxbai-rerank-large-v2) and `LICENSE` in the repo at the pinned revision | Apache-2.0: [card](https://huggingface.co/Qwen/Qwen3-Reranker-4B) metadata (`license: apache-2.0`); no `LICENSE` file in the repo; base model Qwen3-4B-Base, Apache-2.0 |
| pinned revision | `ca7e1ee484c37c0ddd8d178a9a5c33cec575c5e6` (2026-04-08) | `22e683669bc0f0bd69640a1354a6d0aebcfeede5` (2026-04-16) |
| architecture | Qwen2ForCausalLM, 1.54 B; 28 layers, hidden 1,536, 12 heads (2 KV), MLP 8,960 | Qwen3ForCausalLM, 4.02 B; 36 layers, hidden 2,560, 32 heads (8 KV), MLP 9,728 |
| download (hub's dry run from this machine, R3) | 17 files, **3.1 GB** (`model.safetensors` 3,087,466,808 B, F16) | 17 files, **8.1 GB** (two shards: 4,058,781,760 + 3,984,833,200 B, bf16), quantised on load |
| weights on the GPU | **2,944 MiB** (bf16: transformers 5 loads in the config's dtype) | **4,212 MiB** (est.): 3.63 B linear weights in int8 (3,465 MiB) + the tied 151,669 x 2,560 embedding kept in bf16 (742 MiB) + row scales |
| published (the survey's table) | CoIR 70.87; BEIR 57.49 | CoIR 73.91; MTEB-Code 81.20; MTEB-R 69.76 |
| how it loads | **as today's model, a model-name change:** the repo ships sentence-transformers' files (`modules.json`: Transformer + `LogitScore`, `true_token_id` 16 = "1", `false_token_id` 15 = "0"), the same form as the 0.6B snapshot; the service's `CrossEncoder(model, revision=...)` serves it. No `mxbai-rerank` package needed | the same `LogitScore` form (yes 9693 / no 2152, as the 0.6B), **plus a quantised load** the service does not pass today: `model_kwargs={"quantization_config": BitsAndBytesConfig(load_in_8bit=True), "device_map": {"": 0}}` |
| what it needs | the download only | the download; **bitsandbytes 0.50.2** (2026-08-27; its Linux x86-64 wheel carries CUDA 13.0-13.2 builds for sm75 to sm120, [docs](https://huggingface.co/docs/bitsandbytes/main/installation)), **accelerate 1.15.0** (transformers 5.18's 8-bit path refuses without it: rehearsal R6b) and psutil (accelerate's dependency); a trial loader (section 4.1) |

**This machine:** RTX 5070 Ti (sm_120), 16,303 MiB, driver 610.88 (CUDA UMD 13.3). The reranker venv (uv-built, no
pip; listed read-only, R2): torch 2.14.1 on CUDA 13.0 wheels, transformers 5.18.0, sentence-transformers 6.1.0,
huggingface-hub 1.33.0, 60 packages. bitsandbytes, accelerate, psutil, mxbai-rerank, torchao and kernels are all
absent. transformers 5.18 asks bitsandbytes >= 0.46.1 and accelerate >= 1.1.0, and it moves an 8-bit model with
`.to()` only from bitsandbytes 0.48. sentence-transformers 6.1 already pads on the left and keeps only the last
position's logits (`logits_to_keep=1`), so the vocabulary logits do not grow with the text. **Other 8-bit routes, not
recommended:**
- FP8 (`FineGrainedFP8Config`) needs the `kernels` package, which fetches its kernels from the hub at run time.
- torchao must match torch 2.14 exactly.
- llama.cpp's reranking mode needs a new service, and its community GGUFs are reported broken.

**Risk:** bitsandbytes on sm_120 is documented but unproven here. [Issue #1937](https://github.com/bitsandbytes-foundation/bitsandbytes/issues/1937)
(an RTX 5070 Ti laptop on Windows, "no kernel image") was closed without a cause; the maintainer says sm_120 has been
in the wheels since about 0.45.3. If T4's load fails, candidate 2 stops there (section 6). bf16 does not fit (section 2).

## 2. The GPU fit (MiB)

**The budget:** the card is 16,303; the dispatcher's budget is 14,255 (total less the 2,048 headroom); the backstop
is 15,872. **Today:** 10,250 to 10,275 used (R0 to R10), with both embedders and the live 0.6B since 05:39.

**The base** (desktop + both embedders, no reranker): about **5,750**. Ollama's `size_vram` is 2,370,652,077 B
(2,261) for each embedder; the desktop is about 1,230 (the GPU agent's 1.2 GiB). So the live 0.6B holds about
**4,510** now: its 1,136 of weights, about 500 of CUDA context (est.), and about 2,870 that PyTorch keeps after its
largest requests ("near 4.6 GB", DEC-1068 (e)). The night's lower readings (212 at 04:00, 2.6 GB at 05:39) were
Windows paging the embedders out, so the base is read after warming both embedders (T1).

**The transient at the bound:** at most 16 texts, and count x longest pair <= 24,000 characters. One request is then
at most about 9,000 tokens (24,000 characters of code at about 3 characters a token, plus the template).
- **First principles** (memory-efficient attention: with a padding mask, transformers 5.18 repeats K/V rather than
  fall to the math kernel): tokens x (3 x MLP + about 8 x hidden) x 2 bytes, x 1.5 for the allocator.
  This gives 0.6B about 450, mxbai about 1,000, and the 4B about 2,000 (with bitsandbytes' int8/int32 buffers).
- **Kept without a release:** the measured 0.6B keeps about 6x its first-principles figure, as the allocator caches
  blocks across shapes. Scaled the same way, mxbai keeps up to about 6,400 and the 4B up to about 12,800 (est.).

| peak, the bound's worst shape | 0.6B (today) | mxbai bf16 | Qwen3-4B 8-bit |
|---|---:|---:|---:|
| weights + context + transient, **with the release after each request** (window 4's form; the trial copy) | 2,090 | **4,444** | **6,712** |
| total with the base (5,750), alone | 7,840 | **10,194** (4,061 under the budget) | **12,462** (1,793 under) |
| without the release (today's live form), total with the base, alone, up to (est.) | 10,260 (measured) | 15,594: past the budget, at the backstop | 23,262: past the card |
| beside the live 0.6B at its kept 4,510 | – | 14,704: past the budget | 16,972: past the card |
| beside a freshly restarted live 0.6B (about 1,640, then climbing) | – | 11,834, rising to 14,704 | 14,102, then over |

**So:**
1. **One reranker on the GPU at a time.**
2. **The trial copy releases its cache after each request.** This is DEC-1068 (e)'s window-4 change, and D4B-NIGHT
   made it the second condition before a stronger model loads. Without it, neither candidate fits at the bound.
3. **An adoption presupposes window 4's release in the live service.**

T2 to T4 measure every figure above: the peak per request (`peak_reserved_mib`, logged by the trial copy) and the
card's total per shape (the probe). The estimates only set the stop lines.

## 3. The operator's steps (one terminal; no repository commit)

**Step 0, the conditions** (each line prints `ok`, or stop):
```bash
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
L=~/.local/share/gov-os/reranker-venv; V=~/.local/share/gov-os/reranker-trial-venv; C=~/.cache/gov-os-trial; TR=~/.local/share/gov-os/rerank-trial
for d in $C $V $TR; do [ -e $d ] && echo "STOP: $d exists" || echo "ok: $d absent"; done
[ -e $O/log/act-in-progress.txt ] && echo "STOP: $(cat $O/log/act-in-progress.txt)" || echo "ACT-RERANK-TRIAL-1 steps 0-3 by the operator, $(date '+%F %T')" > $O/log/act-in-progress.txt
df -h --output=avail ~ | tail -1        # >= 25G (3.1 + 8.1 GB downloads, the venv's copy of the wheels)
mkdir -p -m 700 $C && uv pip freeze --python $L/bin/python > $C/live-freeze.txt && wc -l < $C/live-freeze.txt   # 60
LP=$(dirname "$(readlink -f ~/.local/bin/gov)")/../lib/python3.12/site-packages/gov/retrieval
sha256sum "$LP"/rerank.py "$LP"/rerank_service.py "$LP"/rerank_worker.py > $C/pin-sums.txt && cat $C/pin-sums.txt   # for the rollback's check
```

**Step 1, the trial venv: a clone of the live venv, from uv's cache, offline** (R2: all 60 packages are in uv's cache
at their exact versions). A new venv rather than the live one, so that the live service never imports a new package
and step 3's three packages can be removed with one `rm`:
```bash
uv venv --python /usr/bin/python3 $V
uv pip install --offline --python $V/bin/python -r $C/live-freeze.txt
uv pip freeze --python $V/bin/python | diff - $C/live-freeze.txt && echo "ok: the trial venv equals the live venv"
```

**Step 2, the downloads, each into its own model folder under `$C/hf/hub/`** (the trial's `HF_HOME`: no token is
read, and the live HF cache is not written):
```bash
export HF_HOME=$C/hf HF_HUB_DISABLE_TELEMETRY=1
$V/bin/hf download mixedbread-ai/mxbai-rerank-large-v2 --revision ca7e1ee484c37c0ddd8d178a9a5c33cec575c5e6
$V/bin/hf download Qwen/Qwen3-Reranker-4B --revision 22e683669bc0f0bd69640a1354a6d0aebcfeede5
unset HF_HOME HF_HUB_DISABLE_TELEMETRY
M=$C/hf/hub/models--mixedbread-ai--mxbai-rerank-large-v2/snapshots/ca7e1ee484c37c0ddd8d178a9a5c33cec575c5e6
Q=$C/hf/hub/models--Qwen--Qwen3-Reranker-4B/snapshots/22e683669bc0f0bd69640a1354a6d0aebcfeede5
stat -L -c '%s %n' $M/model.safetensors $Q/model-0000[12]-of-00002.safetensors   # 3087466808, 4058781760, 3984833200
ls $M $Q | grep -c -E '^(modules.json|config_sentence_transformers.json|1_LogitScore)$'                       # 6
```
mxbai's trial (T3) can start once its download is checked. It needs nothing from step 3.

**Step 3, the 8-bit packages, into the trial venv only, with every existing package held at its version:**
```bash
uv pip install --python $V/bin/python -c $C/live-freeze.txt bitsandbytes==0.50.2 accelerate==1.15.0
uv pip freeze --python $V/bin/python | diff $C/live-freeze.txt -    # only: > accelerate==1.15.0, > bitsandbytes==0.50.2, > psutil==<v>
ls $V/lib/python3.12/site-packages/bitsandbytes/ | grep -E 'libbitsandbytes_cuda13[0-9]'   # at least one CUDA 13 build
CUDA_VISIBLE_DEVICES=-1 $V/bin/python -I -B -c "import accelerate, bitsandbytes; print('ok', accelerate.__version__, bitsandbytes.__version__)"
uv pip freeze --python $L/bin/python | diff - $C/live-freeze.txt && echo "ok: the live venv unchanged"
rm $O/log/act-in-progress.txt
```
The import check hides the GPU and touches nothing on it; the first GPU proof is T4's load. Licences: bitsandbytes
MIT, accelerate Apache-2.0, psutil BSD-3-Clause.

**Not rehearsed:** steps 1 (the install half), 2 and 3 install or download. Rehearsed: step 0 (R1, R2), the venv's
creation and removal (R4), and step 2's file lists and sizes (R3, `--dry-run`).

## 4. The trial (the CTO, in a quiet window, under this ACT)

### 4.1 Before it: three small things (the CTO's tools lane, reviewed; no `src/` change)
- **The trial service's two files**, into `$TR/svc/`, and a `run/` folder (mode 700) beside them:
  - `rerank_service.py`: the live pin's, unchanged (`cmp` with `src/gov/retrieval/rerank_service.py`, R5).
  - `rerank_worker.py`: the pin's, with two trial-only changes (rehearsal log R5, the diff; appendix C, whole):
    1. `GOV_RERANK_TRIAL_8BIT=1` loads in 8-bit.
    2. After each request, one log line (`texts`, `padded_chars`, `seconds`, `peak_reserved_mib`,
       `reserved_after_mib`), and `torch.cuda.empty_cache()` unless `GOV_RERANK_TRIAL_RELEASE=0`.
  
  The live pin path is found as ACT-QUERY-GPU-2 found it, so it holds after re-pin window 3:
  `LP=$(dirname "$(readlink -f ~/.local/bin/gov)")/../lib/python3.12/site-packages/gov/retrieval`.
- **The harness's switch** (the research agent, in `night/harness/rx.py` and `run.sh`):
  - `GOV_RX_RERANK_DIR=$TR/run` sets `rr._cache` to the trial folder before `rr.default_reranker()`.
  - `GOV_RX_GPU_LIMIT_MIB=14255` stops the run at the budget instead of waiting for a reset.
  - Rules: only `rx.py` variants (the `PRODUCT` variant runs the product's client, which would start the *live*
    service beside the candidate); a fresh `GOV_RX_CACHE` for every model (its score key has no model name, so a
    shared cache would serve the 0.6B's scores as the candidate's); the per-question ranks kept (DEC-1068's audit).
- **The probe** (appendix A, rehearsed R8): the bound's five worst shapes one at a time (1 x 23,926 characters up to
  16 x 1,426), and N clients at once, with the product's 30 s answer timeout. It speaks only to the trial socket.

### 4.2 Which way: a second service on its own socket, with the live service stopped for the window
- **Recommended:** the trial copy on `$TR/run/rerank.sock`, its own lock and log, with the live service stopped for
  the window. The GPU then holds the base and one reranker (section 2: mxbai 10,194, the 4B 12,462, both under the
  budget). The slot watcher sees the trial copy as a service (it matches `rerank_service.py`), lets it take a slot,
  and holds the other one, so no private reranker joins it.
- **Not beside the live service:** both GPU slots are taken (the service and the watcher), so the trial would end
  with exit 75, unless it used its own lock folder, which goes round DEC-1043 (2). And section 2 puts the total past
  the budget.
- **Not the live service restarted on the candidate:** the model is a constant of the pinned client
  (`rerank.py` `MODEL`, `REVISION`), so this is a re-pin, not class 3. It would switch every session's searches,
  which this ACT forbids, and the live service has no release yet (section 2's "without" row).
- **Cost of the window:** a search by any other session meanwhile finds no live service. It tries to start one,
  finds no free slot (about 20 s), falls back to a private reranker, finds no slot again (about 20 s), and answers
  unranked, named in `rerank.log`. Hence a quiet window. Stopping the live service for a trial is not one of
  class 3's reasons, so this ACT's approval covers it, and covers starting the trial copy (a new service: an ACT
  item in RESTART-CLASSES).

### 4.3 The GPU rules for the window (2026-11-04 00:20, DEC-1067, DEC-1068 (4))
- **Before:** the dispatcher reads `heavy slots held: none`, `Jobs by phase: none`, and `leads running ... none`. No
  measure, rebuild, `gov accept` with real models, or experiment runs beside it. `rerank_reset_watch.sh` is not
  running (its reset stops every `rerank_service.py`, the trial's too).
- **The backstop:** `tools/gpu_backstop.sh <pgid> ...`, armed with the process groups of the harness's run, the trial
  service and the probe (each started in its own group with `setsid`; `proc.sh pgid <pid>`). Since 2026-11-05 it
  pauses only the groups it is given, never processes matched by their command text (the owner, L-0075); it ends by
  itself when they have all ended, so it is re-armed for each model's run.
  
  It pauses past 15,872, on a spill, or when an embedder loses layers. Then the CTO force-stops the trial service
  and goes to T6.
- **The trial's own stop line is the budget, 14,255:** the probe stops itself at `--limit 14255`, and the harness at
  `GOV_RX_GPU_LIMIT_MIB`. A candidate that reaches it at any shape **does not fit at the bound**, and it is recorded
  so.
- **Between models:** the GPU returns to the base (within 300) before the next one starts.

### 4.4 The steps
```bash
T=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/tree_busy.sh
V=~/.local/share/gov-os/reranker-trial-venv; TR=~/.local/share/gov-os/rerank-trial; C=~/.cache/gov-os-trial
LP=$(dirname "$(readlink -f ~/.local/bin/gov)")/../lib/python3.12/site-packages/gov/retrieval
stop_by_path() {   # DEC-1068 (f): SIGTERM, 30 s, then SIGKILL; by the file's full path, so live and trial never match each other (R9)
  local M=$1 P i
  for P in $(bash $T --cmd "$M" 2>/dev/null | awk '/^BUSY/{print $2}'); do kill -TERM $P; done
  for i in $(seq 1 30); do bash $T --cmd "$M" > /dev/null 2>&1 || { echo "stopped ($i s)"; return 0; }; sleep 1; done
  for P in $(bash $T --cmd "$M" 2>/dev/null | awk '/^BUSY/{print $2}'); do echo "SIGKILL $P"; kill -KILL $P; done
  sleep 1; ! bash $T --cmd "$M" > /dev/null 2>&1
}
start_trial() {    # $1 model, $2 revision, $3 8-bit 0|1, $4 HF_HOME; the detached form of R7b
  local n; n=$(cat "$TR/run/rerank.log" 2>/dev/null | wc -l)
  ( exec 9>"$TR/run/rerank.lock"; flock -n 9 || { echo "STOP: a trial service holds the lock"; exit 1; }
    HF_HOME="$4" HF_HUB_OFFLINE=1 GOV_RERANK_IDLE_S=3600 GOV_RERANK_TRIAL_8BIT="$3" GOV_RERANK_TRIAL_RELEASE=1 \
      setsid -f "$V/bin/python" -I "$TR/svc/rerank_service.py" "$1" "$2" "$TR/run/rerank.sock" 9 \
      >> "$TR/run/service.log" 2>&1 < /dev/null )
  for i in $(seq 1 180); do tail -n +$((n+1)) "$TR/run/rerank.log" 2>/dev/null | grep -q -E 'READY|REFUSED' && break; sleep 1; done
  tail -n +$((n+1)) "$TR/run/rerank.log"     # must read READY pid <n> device cuda:0
}
```
- **T0, the window:** check section 4.3's conditions; arm both backstops; write `log/act-in-progress.txt`.
- **T1, the base:**
  1. Stop the live service: `stop_by_path "$LP/rerank_service.py"`.
  2. Warm both embedders: class 1's and class 2's `curl ... "input":"warm"` lines (page them in).
  3. Read the GPU (expect about 5,750) and record it as the base.
- **T2, today's 0.6B on the trial copy (the path's own check):**
  1. `start_trial Qwen/Qwen3-Reranker-0.6B e61197ed45024b0ed8a2d74b80b4d909f1255473 0 ~/.cache/huggingface` (the
     live HF cache, read only).
  2. The GPU after the load, then `rerank_trial_probe.py $TR/run/rerank.sock peak --limit 14255`.
  3. The visible half: the harness's x5 + headers (m5's configuration), three runs. **It must give m5's visible
     21 / 19 with the same ranks per question**, or the trial path is not faithful: stop.
  4. Speed alone (median search over the three runs), then `load 10` and `load 20` with the probe, and 10 and 20 of
     the harness's searches at once (the first N visible questions, each with its own fresh cache).
  5. `stop_by_path "$TR/svc/rerank_service.py"`, and the GPU back to the base.
- **T3, mxbai:** `start_trial mixedbread-ai/mxbai-rerank-large-v2 ca7e1ee484c37c0ddd8d178a9a5c33cec575c5e6 0 $C/hf`,
  then T2's steps 2 to 5. Expected, after the load: the base + about 3,450.
- **T4, Qwen3-4B 8-bit** (after step 3):
  `start_trial Qwen/Qwen3-Reranker-4B 22e683669bc0f0bd69640a1354a6d0aebcfeede5 1 $C/hf`, then T2's steps 2 to 5.
  Expected, after the load: the base + about 4,700. A load error (no kernel image, or the bitsandbytes backend) ends
  candidate 2's trial: record it and go to T6.
- **T5, the hidden half:** every run scores all 48; the hidden figure is reported beside the visible one and never
  used to choose (DEC-1067 (b)).
- **T6, the restore:** section 5.

**Speed and concurrency (est., to be measured).** The service answers one request at a time, so N searches at once
make each request wait about N x its own time (R8: 0.30 s a request gave 3.0 s at 10 and 6.0 s at 20). Per page:
- **0.6B:** 0.24 s measured. At 20 at once, about 5 s.
- **mxbai:** about 3x the 0.6B's non-embedding compute, so about 0.7 s a page; about 14 s at 20 at once.
- **Qwen3-4B 8-bit:** about 8x, and LLM.int8 is no faster than bf16, so about 2 to 4 s a page; 20 to 40 s at 10,
  40 to 80 s at 20. **The product's 30 s answer timeout** then leaves searches unranked: R8's 1.6 s stand-in at
  20 at once timed out 42 of 60 requests.

**The choice rule, to be written into the trial's record before T3 runs** (DEC-1067 (b): the visible half chooses):
1. **Eligible only if:**
   - T2 reproduced m5's visible half;
   - no shape reached the budget;
   - at 10 searches at once, no request timed out;
   - its median search alone is at most 3.0 s (about 2x m5's 1.45 s). This bound is proposed; the owner may set
     another.
2. **Adopted only if** its visible hit@5 beats the 0.6B's 21 of 24; on a tie, its visible full evidence beats 19.
3. **Both win:** the higher visible hit@5, then full evidence, then mxbai (no install in the product, smaller,
   faster).
4. **Caveat:** the visible half has only 3 misses left (Q14, Q19, q23), so a candidate can gain at most 3 there. A
   gain seen only on the hidden half cannot be adopted.

**Time (est.):** about 25 minutes a model (the load, the probe, three visible runs, concurrency), so about 1.5 h for
all three.

## 5. The rollback (the live service keeps today's model throughout)
- **During the trial, or any stop:**
  1. `stop_by_path "$TR/svc/rerank_service.py"` (SIGKILL after 30 s).
  2. Check no trial process remains.
  3. Restart the live service with class 3's start line, unchanged:
     `cd /home/usain/gov-os-worktrees/W2-00-store && GOV_RERANK_IDLE_S=43200 ~/.local/bin/gov retrieve "what decides a close" --json > /dev/null`.
  4. Class 3's check: `READY pid <n> device cuda:0` in `~/.cache/gov-os/rerank.log`; a second search gives
     `rerank.by` = `service`; the GPU stays under 14,255.
  5. Disarm the backstops; remove `log/act-in-progress.txt`; one line in `log/restarts.jsonl`.
- **After the owner's decision, the files:** they are inert (nothing but the trial reads them). First the checks,
  each silent or `OK` (before the removal: they read step 0's records in `$C`):
  - `uv pip freeze --python ~/.local/share/gov-os/reranker-venv/bin/python | diff - $C/live-freeze.txt`;
  - `sha256sum -c $C/pin-sums.txt`. If a re-pin came between, it checks the old pin's files, still in place;
  - `ls ~/.cache/huggingface/hub | grep -E 'mxbai|Reranker-4B'`, which must print nothing.
  
  Then remove the candidate that is not adopted, or all of them:
  `rm -rf ~/.local/share/gov-os/rerank-trial ~/.local/share/gov-os/reranker-trial-venv ~/.cache/gov-os-trial`.
  R10 rehearsed these checks after removing the stand-in folders: the live venv's freeze, the pin's three files, the
  live service's pid 1185831 and the HF cache were all unchanged.
- **A step 1-3 failure:** `rm -rf` the folder that step made. Nothing else was changed.

## 6. What the rehearsal showed, and what it could not
- **Rehearsed** (log R0 to R11, R7b), all clean:
  - the conditions;
  - the live venv's versions and absent packages;
  - the 60 of 60 cached wheels;
  - the hub's file lists and sizes (`--dry-run`);
  - the venv's creation and removal (no package);
  - the trial copy's two files (the service byte-identical, the worker's diff parses).
- **The load with a stand-in name fails cleanly**, offline with the GPU hidden: `OSError` naming the hub, for the
  pin's worker and for the trial copy. With a stand-in folder (the 0.6B's configs, no weights):
  - plain: `OSError: no file named model.safetensors`;
  - 8-bit: `ValueError: ... requires accelerate`, the exact gap step 3 fills (R6, R6b). The GPU read the same before
    and after.
- **The trial service's start in the ACT's forms**, foreground and detached: `REFUSED`, exit 76, no socket, the lock
  freed (R7, R7b).
- **The probe** against a stand-in server (R8), with the queueing and timeout arithmetic above. Its first run found
  two faults, both fixed: the stand-in ended on a timed-out caller's broken pipe (the real service already catches
  that), and the probe did not catch the resets after it.
- **The force-stop:** a process ignoring SIGTERM was killed after 30 s, matched by its full path; the live service
  was not matched (R9).
- **The rollback's checks:** all unchanged, the live service never stopped (R10).
- **Not rehearsed, and why:**
  - the downloads (3.1 GB, 8.1 GB): a download;
  - step 1's install and step 3: installs;
  - any real model's load, READY on `cuda:0`, the probe and measure on a model, the live service's stop and class 3
    restart: they stop or start a reranker (DEC-1065 (1)). R6, R7 and R7b run the same code up to the first GPU or
    model step.
- **Unix socket paths are limited to 107 bytes.** The trial's is 60 (R8). A folder under the repository's scratch
  would be too long (172).

## 7. The recommendation, and what the owner decides
- **Run mxbai first, as the owner set.**
  - It is the only pure model swap: the download only, the service's own code path.
  - In the product it would be a re-pin of `MODEL` and `REVISION`, with window 4's release.
  - Its estimated peak leaves about 4 GiB under the budget.
  - It should stay under the 30 s timeout at 20 searches at once (est. 14 s).
- **Qwen3-4B in 8-bit** has the stronger published code scores (CoIR 73.9 against 70.9). Against it:
  - an 8.1 GB download and three new packages;
  - a quantised loader in the product: W2-112's `load()` changed, and bitsandbytes in the live venv, a later ACT;
  - unproven bitsandbytes on sm_120;
  - about 1.8 GiB to spare;
  - est. 2 to 4 s a page, which the one-at-a-time service turns into timeouts at 10 to 20 searches at once.
  
  It matters only if it wins on the visible half by more than mxbai and passes the concurrency rule.
- **The owner decides:**
  - (a) this ACT: steps 0 to 3 by the operator;
  - (b) the trial under it: stopping the live service for a quiet window of about 1.5 h, and starting the trial copy
    as a second service;
  - (c) the choice rule of 4.4, the 3.0 s speed bound in particular.
