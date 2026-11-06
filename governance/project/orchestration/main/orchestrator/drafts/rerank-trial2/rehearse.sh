#!/usr/bin/env bash
# ACT-RERANK-TRIAL-2's rehearsal (DEC-1057): act.sh's own steps on stand-in folders (only O, C and their contents
# substituted); the real trial venv is used read-only (hf --dry-run, uv pip freeze); the downloads are dry runs; the
# real trial cache, the real live HF cache and the real in-progress mark are checked unchanged at the end.
#   bash rehearse.sh <scratch folder>
set -u
ACT=/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/packages/ACT-RERANK-TRIAL-2/act.sh
S=$1; rm -rf "$S"; mkdir -p "$S/O/log" "$S/C/hf/hub"
REAL_C=$HOME/.cache/gov-os-trial; REAL_O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
V=$HOME/.local/share/gov-os/reranker-trial-venv
real_c_before=$(ls -la "$REAL_C" "$REAL_C/hf/hub" | sha256sum); live_before=$(ls -la "$HOME/.cache/huggingface/hub" | sha256sum)
venv_before=$(uv pip freeze --python "$V/bin/python" | sha256sum)
export O=$S/O C=$S/C
fails=0
step() {  # name, expected exit, args...
  local name=$1 want=$2; shift 2
  out=$(bash "$ACT" "$@" 2>&1); rc=$?
  if [ $rc -eq "$want" ]; then echo "ok   $name (rc $rc)"; else echo "FAIL $name (rc $rc, want $want)"; fails=$((fails + 1)); fi
  echo "$out" | sed 's/^/       | /'
}
expect() { if eval "$2"; then echo "ok   $1"; else echo "FAIL $1"; fails=$((fails + 1)); fi; }

step "R1 check: the conditions met, marked in progress" 0 check
expect "R1b the mark written in the stand-in log" '[ -s "$S/O/log/act-in-progress.txt" ]'
step "R2 check again: STOP, an ACT in progress" 1 check
DRY=1 step "R3 download, dry run: lists the files, downloads nothing" 0 download
expect "R3b the dry run wrote no model folder" '[ ! -e "$S/C/hf/hub/models--Alibaba-NLP--gte-reranker-modernbert-base/snapshots" ] && [ ! -e "$S/C/hf/hub/models--zeroentropy--zerank-1-small-reranker/snapshots" ]'
gs=$S/C/hf/hub/models--Alibaba-NLP--gte-reranker-modernbert-base/snapshots/f7481e6055501a30fb19d090657df9ec1f79ab2c
zs=$S/C/hf/hub/models--zeroentropy--zerank-1-small-reranker/snapshots/a65fd51c450e9b47fdddab98e31166ecad21af8d
mkdir -p "$gs" "$zs"
for f in README.md config.json special_tokens_map.json tokenizer.json tokenizer_config.json; do echo x > "$gs/$f"; done
truncate -s 598436708 "$gs/model.safetensors"
for f in LICENSE README.md added_tokens.json config.json generation_config.json merges.txt special_tokens_map.json tokenizer.json tokenizer_config.json vocab.json; do echo x > "$zs/$f"; done
truncate -s 3441185608 "$zs/model.safetensors"
step "R4 verify on the stand-in download (sparse files of the real sizes): all ok, the mark removed" 0 verify
expect "R4b the mark removed" '[ ! -e "$S/O/log/act-in-progress.txt" ]'
echo x > "$zs/modeling_zeranker.py"
step "R5 verify with a code file planted: STOP" 1 verify
rm "$zs/modeling_zeranker.py"
truncate -s 100 "$gs/model.safetensors"
step "R6 verify with a short gte weights file: STOP" 1 verify
step "R7 undo: the two model folders removed" 0 undo
expect "R7b nothing left of either model" '[ -z "$(ls "$S/C/hf/hub")" ]'
expect "R8 the real trial cache unchanged" '[ "$(ls -la "$REAL_C" "$REAL_C/hf/hub" | sha256sum)" = "$real_c_before" ]'
expect "R9 the real live HF cache unchanged" '[ "$(ls -la "$HOME/.cache/huggingface/hub" | sha256sum)" = "$live_before" ]'
expect "R10 the real trial venv unchanged" '[ "$(uv pip freeze --python "$V/bin/python" | sha256sum)" = "$venv_before" ]'
expect "R11 no real in-progress mark" '[ ! -e "$REAL_O/log/act-in-progress.txt" ]'
[ $fails -eq 0 ] && echo "REHEARSAL PASS" || echo "REHEARSAL FAILED $fails"
exit $fails
