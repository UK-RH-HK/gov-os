#!/usr/bin/env bash
# ACT-RERANK-TRIAL-2 (DEC-1081 (3)): two more rerankers' downloads into the trial's own HF_HOME. No install, no
# package, no change to any venv, the live HF cache, the pins or the live service.
#
#   bash act.sh check     step 0: the conditions (each line ok, or STOP); marks the ACT in progress
#   bash act.sh download  step 1: the two pinned downloads (DRY=1 lists the files and sizes only)
#   bash act.sh verify    step 2: sizes, file counts, no code file, the live cache and the trial venv unchanged
#   bash act.sh undo      removes the two model folders this ACT made, nothing else
#
# Only the paths below may be overridden (the rehearsal does); the operator runs it with none set.
set -u
O=${O:-/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator}
V=${V:-$HOME/.local/share/gov-os/reranker-trial-venv}
C=${C:-$HOME/.cache/gov-os-trial}
LIVE_HF=${LIVE_HF:-$HOME/.cache/huggingface/hub}
GTE=Alibaba-NLP/gte-reranker-modernbert-base;  GTE_REV=f7481e6055501a30fb19d090657df9ec1f79ab2c
ZER=zeroentropy/zerank-1-small-reranker;      ZER_REV=a65fd51c450e9b47fdddab98e31166ecad21af8d
G=$C/hf/hub/models--Alibaba-NLP--gte-reranker-modernbert-base
Z=$C/hf/hub/models--zeroentropy--zerank-1-small-reranker
fails=0
say() { if [ "$1" = ok ]; then echo "ok: $2"; else echo "STOP: $2"; fails=$((fails + 1)); fi; }

case "${1:-}" in
check)
  [ -x "$V/bin/hf" ] && [ -x "$V/bin/python" ] && say ok "the trial venv ($V)" || say stop "no trial venv at $V"
  [ -d "$C/hf/hub" ] && say ok "the trial HF_HOME ($C/hf)" || say stop "no $C/hf/hub"
  for d in "$G" "$Z"; do [ -e "$d" ] && say stop "$d exists" || say ok "$(basename "$d") absent"; done
  avail=$(df -k --output=avail "$C" | tail -1)
  [ "$avail" -ge 6000000 ] && say ok "$((avail / 1048576)) GiB free (6 needed: 0.6 + 3.5 GB, with room)" || say stop "under 6 GiB free"
  [ -e "$O/log/act-in-progress.txt" ] && say stop "an ACT is in progress: $(cat "$O/log/act-in-progress.txt")"
  if [ $fails -eq 0 ]; then
    ls "$LIVE_HF" > "$C/act2-live-hf-before.txt"
    uv pip freeze --python "$V/bin/python" > "$C/act2-trial-freeze-before.txt"
    echo "ACT-RERANK-TRIAL-2 by the operator, $(date '+%F %T')" > "$O/log/act-in-progress.txt"
    echo "ok: marked in progress; $(wc -l < "$C/act2-trial-freeze-before.txt") packages in the trial venv recorded"
  fi
  ;;
download)
  dry=(); [ "${DRY:-0}" = 1 ] && dry=(--dry-run)
  export HF_HOME=$C/hf HF_HUB_DISABLE_TELEMETRY=1
  "$V/bin/hf" download "$GTE" --revision "$GTE_REV" --include "*.json" --include model.safetensors --include README.md "${dry[@]}" || fails=$((fails + 1))
  "$V/bin/hf" download "$ZER" --revision "$ZER_REV" --exclude "*.py" --exclude .gitattributes "${dry[@]}" || fails=$((fails + 1))
  ;;
verify)
  gs=$G/snapshots/$GTE_REV; zs=$Z/snapshots/$ZER_REV
  [ "$(stat -L -c %s "$gs/model.safetensors" 2>/dev/null)" = 598436708 ] && say ok "gte's weights, 598,436,708 B" || say stop "gte's weights missing or the wrong size"
  [ "$(stat -L -c %s "$zs/model.safetensors" 2>/dev/null)" = 3441185608 ] && say ok "zerank's weights, 3,441,185,608 B" || say stop "zerank's weights missing or the wrong size"
  [ "$(ls "$gs" 2>/dev/null | wc -l)" = 6 ] && say ok "gte: 6 files" || say stop "gte: not 6 files"
  [ "$(ls "$zs" 2>/dev/null | wc -l)" = 11 ] && say ok "zerank: 11 files" || say stop "zerank: not 11 files"
  [ "$(find "$G" "$Z" -name '*.py' 2>/dev/null | wc -l)" = 0 ] && say ok "no code file downloaded (zerank's modeling_zeranker.py left out)" || say stop "a .py file was downloaded"
  [ "$(find "$G" -name '*.onnx' 2>/dev/null | wc -l)" = 0 ] && say ok "no ONNX copies downloaded" || say stop "ONNX files were downloaded"
  ls "$LIVE_HF" | diff -q - "$C/act2-live-hf-before.txt" > /dev/null && say ok "the live HF cache unchanged" || say stop "the live HF cache changed"
  uv pip freeze --python "$V/bin/python" | diff -q - "$C/act2-trial-freeze-before.txt" > /dev/null && say ok "the trial venv unchanged (no package)" || say stop "the trial venv changed"
  if [ $fails -eq 0 ]; then rm -f "$O/log/act-in-progress.txt"; echo "ok: ACT-RERANK-TRIAL-2 done; the in-progress mark removed"; fi
  ;;
undo)
  rm -rf "$G" "$Z" "$C/hf/hub/.locks/models--Alibaba-NLP--gte-reranker-modernbert-base" "$C/hf/hub/.locks/models--zeroentropy--zerank-1-small-reranker"
  rm -f "$O/log/act-in-progress.txt"
  echo "undo: the two model folders removed; nothing else touched"
  ;;
*) sed -n '2,10p' "$0"; exit 2 ;;
esac
[ $fails -eq 0 ] && exit 0 || { echo "FAILED: $fails"; exit 1; }
