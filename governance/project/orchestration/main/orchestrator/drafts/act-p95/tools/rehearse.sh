#!/bin/bash
# ACT-P95-1's rehearsal, end to end, as the operator will run the ACT: a planted HOME that holds only the one file the ACT
# touches (a copy of the live gate file), a copy of the repository's src/ (git archive of the head: the checks import the
# product's own reader from it), the operator's clean environment (env -i, PATH, LANG, TMPDIR, HOME planted), every manifest
# check run EXACTLY as written with `bash -c` from that copy, and the plain apply. The planted day (tools/plant_samples.py):
# maximum 9.5 GB, p95 under 2.5 GB. No real session, no live file written; the live gate file and samples file are only
# read, and hashed before and after to show they did not change. The log holds fixed text only (no head, pid, date or count).
#   bash rehearse.sh      the log is ../rehearsal.log (it ends "failures: <n>"); the planted bundle is ../acts/REHEARSAL-ONLY-ACT-P95-1 (never submitted: the live bundle is built on the sample day into acts/ACT-P95-1)
set -u
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/act-p95
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
T=$D/tools
LOG=$D/rehearsal.log
BUNDLE=$D/acts/REHEARSAL-ONLY-ACT-P95-1
LIVE=$HOME/.gov-os/machine
W=$(mktemp -d "$D/tmp/rehearsal.XXXXXX") || exit 5
trap 'rm -rf "$W"' EXIT
: > "$LOG"
exec > >(tee -a "$LOG") 2>&1
FAILS=0
ok() { echo "ok   $1"; }
bad() { echo "FAIL $1"; FAILS=$((FAILS + 1)); }
sha() { sha256sum "$1" | cut -c1-64; }
USER_HOME=$HOME
PH=$W/home                       # the planted HOME: only the touched file
CL=$W/clone                      # src/ of the head
cenv() { env -i PATH=/usr/local/bin:/usr/bin:/bin LANG=C.UTF-8 TMPDIR="$W" HOME="$PH" PYTHONDONTWRITEBYTECODE=1 "$@"; }
penv() { env -i PATH=/usr/local/bin:/usr/bin:/bin LANG=C.UTF-8 TMPDIR="$W" HOME="$USER_HOME" PYTHONDONTWRITEBYTECODE=1 "$@"; }
tree() { (cd "$PH" && find . -type f | LC_ALL=C sort | while read -r f; do echo "$f $(sha "$f")"; done); }
expect() { # expect <label> <want exit> <cmd...>   (clean env, planted HOME, cwd = the src copy)
  local label="$1" want="$2"; shift 2
  (cd "$CL" && cenv "$@") > "$W/out" 2>&1; local rc=$?
  [ "$rc" = "$want" ] && ok "$label" || { bad "$label (wanted exit $want, got $rc)"; tail -n 6 "$W/out" | cut -c1-200 | sed 's/^/     /'; }
}
echo "ACT-P95-1 rehearsal: the p95 of the sampled working sizes in place of the maximum"

echo "--- A. set-up: the live files are read, never written"
live_before="$(sha "$LIVE/gate.json")"
samples_before="$([ -f "$LIVE/samples.jsonl" ] && sha "$LIVE/samples.jsonl" || echo none)"
mkdir -p "$PH/.gov-os/machine" "$CL"
(git -C "$MAIN" archive HEAD src | tar -x -C "$CL") && ok "A1 src/ of the head copied (git archive)" || bad "A1 git archive"
cp -p "$LIVE/gate.json" "$PH/.gov-os/machine/gate.json" && ok "A2 the planted HOME holds a copy of the gate file, and nothing else" || bad "A2"
python3 -I "$T/plant_samples.py" "$W/samples.jsonl" && ok "A3 the planted day written (192 session samples outside verification, 5 outliers)" || bad "A3"
python3 -I "$T/p95_remeasure.py" figures --samples "$W/samples.jsonl" | tail -n 1 | sed "s/^/     /"

echo "--- B. the tests: green on the p95, red on the maximum"
(cd "$D" && penv env P95_SRC="$CL/src" P95_GATE="$LIVE/gate.json" python3 -m pytest -q -p no:cacheprovider --basetemp="$W/pt" tests) > "$W/out" 2>&1 \
  && ok "B1 tests/test_p95_remeasure.py green on the tool (the p95)" || { bad "B1 tests red on the tool"; tail -n 15 "$W/out" | cut -c1-200 | sed 's/^/     /'; }
cp -r "$T" "$W/mutant"
sed -i 's/    return ordered\[k - 1\]/    return ordered[-1]/' "$W/mutant/p95_remeasure.py"
if cmp -s "$T/p95_remeasure.py" "$W/mutant/p95_remeasure.py"; then bad "B2 the mutant is the tool: the sed did not change it"; else ok "B2 a mutant of the tool that returns the maximum was made"; fi
(cd "$D" && penv env P95_TOOLS="$W/mutant" P95_SRC="$CL/src" P95_GATE="$LIVE/gate.json" python3 -m pytest -q -p no:cacheprovider --basetemp="$W/ptm" tests) > "$W/out" 2>&1 \
  && bad "B3 the tests are GREEN on the maximum" || ok "B3 the same tests are RED on a tool that writes the maximum"

echo "--- C. the product's own --remeasure writes the maximum on this day; the bundle writes the p95"
mkdir -p "$W/twin/.gov-os"
cp -rp "$PH/.gov-os/machine" "$W/twin/.gov-os/machine"
cp "$W/samples.jsonl" "$W/twin/.gov-os/machine/samples.jsonl"
(cd "$CL" && env -i PATH=/usr/local/bin:/usr/bin:/bin LANG=C.UTF-8 TMPDIR="$W" HOME="$W/twin" PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
   python3 -m gov.cli.main resources --remeasure --json) > "$W/out" 2>&1
product="$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["working_size_bytes"]["value"])' "$W/twin/.gov-os/machine/gate.json")"
[ "$product" = 9500000000 ] && ok "C1 gov resources --remeasure wrote the maximum: working_size_bytes 9500000000" || bad "C1 the product wrote $product"
rm -rf "$BUNDLE"
python3 -I "$T/p95_remeasure.py" build --out "$BUNDLE" --samples "$W/samples.jsonl" --gate "$PH/.gov-os/machine/gate.json" > "$W/out" 2>&1 \
  && ok "C2 the bundle is built from the same samples" || { bad "C2 build"; cat "$W/out"; }
after_v="$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["working_size_bytes"]["value"])' "$BUNDLE/after/home/.gov-os/machine/gate.json")"
[ "$after_v" = 2475000000 ] && ok "C3 the bundle's after file has working_size_bytes 2475000000 (the p95), not 9500000000" || bad "C3 the bundle holds $after_v"
python3 -I "$T/p95_remeasure.py" verify "$BUNDLE" > "$W/out" 2>&1 && ok "C4 verify: the after file is reproduced from the evidence" || bad "C4 verify"
python3 - "$BUNDLE" "$PH/.gov-os/machine/gate.json" <<'EOF' && ok "C5 only working_size_bytes differs between the before and the after file" || bad "C5 more than one key differs"
import json, sys
b = json.load(open(sys.argv[2])); a = json.load(open(sys.argv[1] + "/after/home/.gov-os/machine/gate.json"))
raise SystemExit(0 if list(a) == list(b) and [k for k in b if a[k] != b[k]] == ["working_size_bytes"] else 1)
EOF

echo "--- D. the manifest's checks, as written with bash -c, on the planted HOME"
cp -r "$BUNDLE" "$W/provisional" && printf 'failures: 0\n' > "$W/prov.log"
python3 -I "$T/p95_remeasure.py" manifest "$W/provisional" --rehearsal "$W/prov.log" > /dev/null && ok "D0 a manifest was drawn up for the checks" || bad "D0 manifest"
python3 -I "$T/p95_remeasure.py" verify "$W/provisional" > /dev/null && ok "D0b verify with the manifest: the checks are the tool's, every file hashes as listed" || bad "D0b"
check() { python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["checks"][int(sys.argv[2])]["cmd"])' "$W/provisional/manifest.json" "$1"; }
state0="$(tree)"
expect "D1 apply.sh check: the file is the frozen before" 0 bash "$BUNDLE/apply.sh" check
expect "D2 apply.sh verify before the apply: refused (3)" 3 bash "$BUNDLE/apply.sh" verify
expect "D3 check 0 (the file is JSON) is green on the before" 0 bash -c "$(check 0)"
expect "D4 check 1 (the figure and the rest of the file) is RED on the before" 1 bash -c "$(check 1)"
expect "D5 check 2 (the product's own reader: no fault, the figure, not due) is RED on the before" 1 bash -c "$(check 2)"
expect "D6 apply.sh undo before the apply: nothing to undo (0)" 0 bash "$BUNDLE/apply.sh" undo
[ "$(tree)" = "$state0" ] && ok "D7 nothing changed yet" || bad "D7 a file changed before the apply"
expect "D8 apply.sh apply (the plain apply, no option)" 0 bash "$BUNDLE/apply.sh" apply
state1="$(tree)"
[ "$(diff <(echo "$state0") <(echo "$state1") | grep -c '^>')" = 1 ] && [ "$(echo "$state0" | wc -l)" = "$(echo "$state1" | wc -l)" ] \
  && ok "D9 exactly one file changed, none added: the gate file (no temp file left)" || bad "D9 the planted HOME changed in more than the gate file"
[ "$(sha "$PH/.gov-os/machine/gate.json")" = "$(cut -d'|' -f4 "$BUNDLE/list.txt")" ] && ok "D10 the file is the frozen after, byte for byte" || bad "D10"
[ "$(stat -c %a "$PH/.gov-os/machine/gate.json")" = 600 ] && ok "D11 the mode 600 is kept" || bad "D11 mode"
for n in 0 1 2; do expect "D12.$n check $n as written, on the applied file" 0 bash -c "$(check $n)"; done
expect "D13 apply.sh verify after the apply" 0 bash "$BUNDLE/apply.sh" verify
expect "D14 apply.sh apply again: nothing to do (0)" 0 bash "$BUNDLE/apply.sh" apply
[ "$(tree)" = "$state1" ] && ok "D15 the second apply changed nothing" || bad "D15"

echo "--- E. the maximum written in its place is caught; a moved or tampered state is refused"
cp -p "$PH/.gov-os/machine/gate.json" "$W/applied.json"
python3 -I -c 'import json,sys; p=sys.argv[1]; d=json.load(open(p)); d["working_size_bytes"]["value"]=9500000000; open(p,"w").write(json.dumps(d,indent=2)+"\n")' "$PH/.gov-os/machine/gate.json"
expect "E1 check 1 is RED when the maximum is written instead of the p95" 1 bash -c "$(check 1)"
expect "E2 check 2 is RED when the maximum is written instead of the p95" 1 bash -c "$(check 2)"
moved="$(sha "$PH/.gov-os/machine/gate.json")"
expect "E3 undo over a file that is neither the after nor the before: refused (3)" 3 bash "$BUNDLE/apply.sh" undo
expect "E4 apply over a file that is neither: refused (3)" 3 bash "$BUNDLE/apply.sh" apply
expect "E5 apply.sh check on it: state other (3)" 3 bash "$BUNDLE/apply.sh" check
[ "$(sha "$PH/.gov-os/machine/gate.json")" = "$moved" ] && ok "E6 the refused steps touched nothing" || bad "E6"
cp -p "$W/applied.json" "$PH/.gov-os/machine/gate.json"
expect "E7 undo" 0 bash "$BUNDLE/apply.sh" undo
[ "$(tree)" = "$state0" ] && ok "E8 the undo restored the planted HOME byte for byte" || bad "E8 the undo left a difference"
cp "$BUNDLE/after/home/.gov-os/machine/gate.json" "$W/after.keep"
printf ' ' >> "$BUNDLE/after/home/.gov-os/machine/gate.json"
expect "E9 a frozen after copy that does not hash as listed: apply exits 4" 4 bash "$BUNDLE/apply.sh" apply
cp "$W/after.keep" "$BUNDLE/after/home/.gov-os/machine/gate.json"
[ "$(tree)" = "$state0" ] && ok "E10 nothing touched by the refused apply" || bad "E10"
mv "$PH/.gov-os/machine/gate.json" "$PH/.gov-os/machine/real.json"; ln -s real.json "$PH/.gov-os/machine/gate.json"
expect "E11 a link in place of the file: refused (3)" 3 bash "$BUNDLE/apply.sh" apply
rm -f "$PH/.gov-os/machine/gate.json"; mv "$PH/.gov-os/machine/real.json" "$PH/.gov-os/machine/gate.json"
rm -f "$PH/.gov-os/machine/gate.json.tmp"
expect "E12 apply.sh check after the repair" 0 bash "$BUNDLE/apply.sh" check

echo "--- F. the operator's own classifier on the bundle (read only)"
python3 -I "$T/p95_remeasure.py" manifest "$W/provisional" --rehearsal "$W/prov.log" > /dev/null
cls="$(python3 -I -B /home/usain/gov-os-operator/install/act_class.py "$W/provisional" 2>&1 | tail -n 1)"
python3 -I -c 'import json,sys; d=json.loads(sys.argv[1]); sys.exit(0 if d.get("class")=="b" and not d.get("hits") else 1)' "$cls" \
  && ok "F1 act_class.py: class b (row machine-gate), no script hit" || { bad "F1 act_class: $cls"; }

echo "--- G. the live files were only read"
[ "$(sha "$LIVE/gate.json")" = "$live_before" ] && ok "G1 the live gate file is unchanged" || bad "G1 the live gate file changed"
now_samples="$([ -f "$LIVE/samples.jsonl" ] && sha "$LIVE/samples.jsonl" || echo none)"
[ "$now_samples" = "$samples_before" ] && ok "G2 the live samples file is unchanged" || bad "G2 the live samples file changed"
echo "failures: $FAILS"
