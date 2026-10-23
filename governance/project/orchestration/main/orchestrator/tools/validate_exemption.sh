#!/usr/bin/env bash
# DEC-906 item 2: prepare the owner's acceptance_exemptions entry and validate it, before the ACT ping, with the
# pinned judge's readers and with a full run in the close's form (DEC-906 item 1). Writes only under
# /tmp/gov-os-exempt/ and the patch into the orchestrator's drafts. Prints verdicts and counts only.
T=/tmp/gov-os-exempt
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
PATCH=$ORCH/drafts/OWNER-C-acceptance-exemption.patch
OUT=$T/out
mkdir -p "$OUT"
log() { echo "$(date '+%F %T') $*" >> "$OUT/run.txt"; }
bash "$ORCH/tools/disk_gate.sh" 2>> "$OUT/run.txt" || { log "NOT STARTED: the disk gate is shut"; exit 2; }
rm -rf "$T/clone"
git clone -q --no-hardlinks --branch w2/integrate /home/usain/Dynamic-Agentic-Engineering-OS "$T/clone" || { log "clone failed"; exit 2; }
cd "$T/clone" || exit 2
log "clone at $(git log -1 --format=%h)"
python3 "$ORCH/tools/add_exemption.py" governance/project/path-map.yaml >> "$OUT/run.txt" 2>&1 || { log "the entry could not be added"; exit 2; }
git diff > "$PATCH"
log "patch written: $(git diff --stat | tail -1)"
/home/usain/.local/share/gov-os/pin-fecb870c/bin/python -E "$ORCH/tools/check_exemption_pin.py" "$T/clone" >> "$OUT/run.txt" 2>&1 \
  || { log "PIN CHECK FAILED"; exit 1; }
python3 "$ORCH/tools/placeholder_scan.py" "$PATCH" >> "$OUT/run.txt" 2>&1
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$T/clone/src" python3 -m gov.check.pathmap >> "$OUT/run.txt" 2>&1; log "core-pathmap exit $?"
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$T/clone/src" python3 -m gov.check.schema > /dev/null 2>&1; log "core-schema exit $?"
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$T/clone/src" python3 -m gov.cli.main rebuild --json > "$OUT/rebuild.json" 2>&1 \
  || { log "clone rebuild failed"; exit 2; }
log "clone rebuilt; waiting for the verification lock"
start=$(date +%s)
flock /tmp/gov-os-verify.lock env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$T/clone/src:$T/clone/src/gov/close/pytest_plugin" \
  GOV_CLOSE_SERIAL_ONLY_OF="$T/clone" \
  python3 -m pytest tests -n auto -q -p no:cacheprovider --no-header -p gov_close_serial_only \
  -o tmp_path_retention_policy=failed --junitxml="$OUT/parallel.xml" > "$OUT/parallel.txt" 2>&1
log "parallel exit $? in $(( $(date +%s) - start )) s (lock wait included): $(tail -1 "$OUT/parallel.txt")"
grep -E "^(FAILED|ERROR) " "$OUT/parallel.txt" | cut -c1-200 >> "$OUT/run.txt"
log "validation done"
