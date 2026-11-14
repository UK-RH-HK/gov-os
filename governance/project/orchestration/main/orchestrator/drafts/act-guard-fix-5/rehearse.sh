#!/bin/bash
# ACT-GUARD-FIX-5's rehearsal: bash rehearse.sh <bed folder (new, under /tmp/claude-1000/agf5-*)> <repository> [<call set from build_replay_calls.py>]
# A. the bundle; B. a fresh clone of w2/integrate: check, the checks before, apply, verify, the checks after;
# C. the live hook, run as Claude Code runs it, on the bundle's before and after copies: the F1 spellings as an
# engineer writing under tests/acceptance (allowed before, refused after) and the cases that must not change; D. the
# follow-up tests (the F1 cases red before, all green after; the hook's own suites green after); E. undo and
# refusals; F. the main tree untouched; G. the guard replay (every logged refusal, and the shell heredoc calls of the
# last 48 hours, through the hook before and after: every call refused before is refused after). Ends "failures: N".
set -u
BED=${1:?bed}; REPO=${2:?repository}; CALLS=${3:-}
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACT=$REPO/.gov-runtime/scratch/orchestrator/acts/ACT-GUARD-FIX-5
HEAVY=$REPO/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
CORPUS=$REPO/.gov-runtime/scratch/orchestrator/drafts/act-guard-fix-4/work/corpus4.json
P=.claude/hooks/bash_writes.py
T=tests/unit/hooks/test_live_hook.py
case "$BED" in /tmp/claude-1000/agf5-?*) ;; *) echo "the bed must be under /tmp/claude-1000/agf5-" >&2; exit 2 ;; esac
[ ! -e "$BED" ] || { echo "the bed exists: $BED" >&2; exit 2; }
mkdir -p "$BED/tmp"; export TMPDIR="$BED/tmp" PYTHONDONTWRITEBYTECODE=1
ok=0; bad=0
mask() { sed -e "s#$BED#<bed>#g" -e "s#$REPO#<repo>#g"; }
r() { if [ "$1" = 0 ]; then echo "ok   $2"; ok=$((ok + 1)); else echo "FAIL $2"; bad=$((bad + 1)); fi; }
is() { [ "$1" = "$2" ]; r $? "$3"; }
IFS='|' read -r root path before after < "$ACT/list.txt"
main_before=$(sha256sum "$REPO/$P" | cut -c1-64)
main_pre=$(sha256sum "$REPO/.claude/hooks/pretooluse.py" | cut -c1-64)
main_status=$(git -C "$REPO" status --porcelain -- .claude governance tests src | sha256sum | cut -c1-64)

echo "--- A. the bundle"
is "$root|$path" "repo|$P" "A1 list.txt names the one file, root repo"
is "$(sha256sum "$ACT/before/repo/$P" | cut -c1-64)" "$before" "A2 the before copy hashes as listed"
is "$(sha256sum "$ACT/after/repo/$P" | cut -c1-64)" "$after" "A3 the after copy hashes as listed"
is "$before" "$main_before" "A4 the main tree's bash_writes.py is the frozen before"
bash -n "$ACT/apply.sh"; r $? "A5 apply.sh parses"
diff -u "$ACT/before/repo/$P" "$ACT/after/repo/$P" > "$BED/after-minus-before.diff"
is "$(grep -c '^-[^-]' "$BED/after-minus-before.diff")" 7 "A6 seven lines removed (_kind's five-line shell branch, body()'s one elif, the held-body loop's one if), the rest added"
echo "     $(grep -c '^+[^+]' "$BED/after-minus-before.diff") lines added"
python3 -B -I - "$ACT/before/repo/$P" "$ACT/after/repo/$P" <<'EOF'
import difflib, sys
b, a = (open(p).read().split("\n") for p in sys.argv[1:3])
def at(sig, nth=1):
    return [k for k, ln in enumerate(b) if ln.strip() == sig][nth - 1]
windows = [(at('return "shell" if not operands or "-s" in opts else "data"') - 6, at('return "shell" if not operands or "-s" in opts else "data"') + 3),
           (at('elif kind == "shell" and body["quoted"]:') - 1, at('elif kind == "shell" and body["quoted"]:') + 3),
           (at("targets = _written(staged[at:], raw=True)") - 3, at("targets = _written(staged[at:], raw=True)") + 1)]
ops = [o for o in difflib.SequenceMatcher(None, b, a, autojunk=False).get_opcodes() if o[0] != "equal"]
hit = [[k for k, (lo, hi) in enumerate(windows) if lo <= o[1] and o[2] <= hi] for o in ops]
ok = all(hit) and {h[0] for h in hit} == {0, 1, 2}
print("changed blocks (old line ranges):", [(o[1] + 1, o[2]) for o in ops])
sys.exit(0 if ok else 1)
EOF
r $? "A7 every changed block lies in one of three places (_kind's shell branch, body()'s shell elif, the held-body loop's registration line), all three are touched; every other line is identical"
git -C "$REPO" show refs/heads/w2/W2-42a:tests/acceptance/W2-42a/fixtures/f1_shell_options.json > "$BED/f1.json"; r $? "A9 W2-42a's F1 fixture read from refs/heads/w2/W2-42a"
is "$(git -C "$REPO" ls-files -s -- $P | cut -d' ' -f2)" "$(git -C "$REPO" hash-object "$ACT/before/repo/$P")" "A8 the before copy is the committed blob (HEAD)"

is "$(find "$ACT/before" "$ACT/after" -type f | wc -l)|$(find "$ACT" -name __pycache__ -o -name '*.pyc' | wc -l)" "2|0" "A10 the frozen copies are the two listed files, no __pycache__ or bytecode in the bundle (review F2)"
is "$(find "$ACT" -type f ! -path "$ACT/before/*" ! -path "$ACT/after/*" -printf '%f\n' | sort | paste -sd' ')" "apply.sh followup-tests.diff list.txt manifest.json rehearsal.log" "A11 the bundle holds no other file (apply.sh, the follow-up diff, list.txt, manifest.json, the rehearsal log; review.md is the operator's, added later)"
echo "--- B. a fresh clone of w2/integrate"
git clone -q --no-hardlinks --branch w2/integrate "$REPO" "$BED/clone" || { echo "clone failed"; exit 3; }
cd "$BED/clone" || exit 3
out=$(bash "$ACT/apply.sh" check); rc=$?; echo "     $out"
is "$rc|${out%% (*}" "0|state before" "B1 check: state before (exit 0)"
python3 -B -I - "$HERE/checks.json" > "$BED/checks-before.txt" <<'EOF'
import json, subprocess, sys
for c in json.load(open(sys.argv[1])):
    print(subprocess.run(["bash", "-c", c], capture_output=True, text=True).returncode)
EOF
is "$(paste -sd, "$BED/checks-before.txt")" "0,1,1,1" "B2 the checks before the apply: 1 passes (it parses), 2, 3 and 4 refuse (exits 0,1,1,1)"
mode0=$(stat -c %a "$P")
out=$(bash "$ACT/apply.sh" apply); rc=$?; echo "     $out"
is "$rc" 0 "B3 apply (exit 0)"
cmp -s "$P" "$ACT/after/repo/$P"; r $? "B4 the file is the after, byte for byte"
is "$(stat -c %a "$P")" "$mode0" "B5 its mode kept ($mode0)"
bash "$ACT/apply.sh" verify; r $? "B6 verify (exit 0)"
out=$(bash "$ACT/apply.sh" apply); rc=$?; echo "     $out"
is "$rc|${out##*; }" "0|nothing to do" "B7 apply again: nothing to do"
is "$(git status --porcelain | sed 's/^...//' | paste -sd,)" "$P" "B8 only bash_writes.py changed in the clone"
python3 -B -I - "$HERE/checks.json" > "$BED/checks-after.txt" 2> "$BED/checks-after.err" <<'EOF'
import json, subprocess, sys
for c in json.load(open(sys.argv[1])):
    p = subprocess.run(["bash", "-c", c], capture_output=True, text=True)
    print(p.returncode)
    sys.stderr.write(p.stdout[-300:])
EOF
sed 's/^/     /' "$BED/checks-after.err"
is "$(paste -sd, "$BED/checks-after.txt")" "0,0,0,0" "B9 the manifest's four checks after the apply (exits 0,0,0,0)"

echo "--- C. the live hook, as Claude Code runs it, on the bundle's before and after copies"
for s in before after; do
  mkdir -p "$BED/hooks-$s"; cp -a "$REPO/.claude/hooks/." "$BED/hooks-$s/"; cp "$ACT/$s/repo/$P" "$BED/hooks-$s/bash_writes.py"
done
cmp -s "$BED/hooks-before/pretooluse.py" "$BED/clone/.claude/hooks/pretooluse.py"; r $? "C1 both hook copies hold the clone's own pretooluse.py (the hook is not part of the change)"
cat > "$BED/probe.py" <<'EOF'
import json, os, subprocess, sys
hooks, project = sys.argv[1:3]
PY = open(os.path.expanduser("~/.local/bin/gov")).readline()[2:].strip()
T = "tests/acceptance/W2-01/zz_probe.py"
CASES = {
    "F1 bash -euo pipefail": ("engineer", f"bash -euo pipefail <<'EOT'\necho x > {T}\nEOT"),
    "F1 bash -o pipefail": ("engineer", f"bash -o pipefail <<'EOT'\necho x > {T}\nEOT"),
    "F1 bash -O extglob": ("engineer", f"bash -O extglob <<'EOT'\necho x > {T}\nEOT"),
    "F1 bash --rcfile": ("engineer", f"bash --rcfile /dev/null <<'EOT'\necho x > {T}\nEOT"),
    "F1 bash --init-file": ("engineer", f"bash --init-file /dev/null <<'EOT'\necho x > {T}\nEOT"),
    "F1 cat | bash -o pipefail": ("engineer", f"cat <<'EOF' | bash -o pipefail\necho x > {T}\nEOF"),
    "F1 bash /dev/stdin": ("engineer", f"bash /dev/stdin <<'EOT'\necho x > {T}\nEOT"),
    "plain bash": ("engineer", f"bash <<'EOT'\necho x > {T}\nEOT"),
    "bash -c": ("engineer", f"bash -c 'echo hi' <<'EOT'\necho x > {T}\nEOT"),
    "bash script.sh": ("engineer", f"bash script.sh <<'EOT'\necho x > {T}\nEOT"),
    "bash -o pipefail script.sh": ("engineer", f"bash -o pipefail script.sh <<'EOT'\necho x > {T}\nEOT"),
    "cat data": ("engineer", f"cat <<'EOF'\necho x > {T}\nEOF"),
    "designer, bash -euo pipefail": ("independent-test-designer", f"bash -euo pipefail <<'EOT'\necho x > {T}\nEOT"),
}
for name, (role, command) in CASES.items():
    event = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": project, "session_id": "agf5"}
    env = dict(os.environ, GOV_ROLE=role, GOV_TICKET="DAEO-03ub", CLAUDE_PROJECT_DIR=project)
    env.pop("PYTHONPATH", None)
    p = subprocess.run([PY, "-E", os.path.join(hooks, "pretooluse.py")], input=json.dumps(event), capture_output=True,
                       text=True, env=env, timeout=90)
    if p.returncode == 2:
        d = "deny"
    elif p.returncode != 0:
        d = "error"
    else:
        d = json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"] if p.stdout.strip() else "allow"
    print(f"{name}|{d}")
EOF
python3 -B -I "$BED/probe.py" "$BED/hooks-before" "$BED/clone" > "$BED/probe-before.txt" 2>&1
python3 -B -I "$BED/probe.py" "$BED/hooks-after" "$BED/clone" > "$BED/probe-after.txt" 2>&1
want_before="F1 bash -euo pipefail|allow F1 bash -o pipefail|allow F1 bash -O extglob|allow F1 bash --rcfile|allow F1 bash --init-file|allow F1 cat | bash -o pipefail|allow F1 bash /dev/stdin|allow plain bash|deny bash -c|allow bash script.sh|allow bash -o pipefail script.sh|allow cat data|allow designer, bash -euo pipefail|allow"
want_after="F1 bash -euo pipefail|deny F1 bash -o pipefail|deny F1 bash -O extglob|deny F1 bash --rcfile|deny F1 bash --init-file|deny F1 cat | bash -o pipefail|deny F1 bash /dev/stdin|deny plain bash|deny bash -c|allow bash script.sh|allow bash -o pipefail script.sh|allow cat data|allow designer, bash -euo pipefail|allow"
sed 's/^/     before: /' "$BED/probe-before.txt"
is "$(paste -sd' ' "$BED/probe-before.txt")" "$want_before" "C2 before: each F1 spelling is allowed (the defect reproduced); plain bash refused; the others as expected"
sed 's/^/     after:  /' "$BED/probe-after.txt"
is "$(paste -sd' ' "$BED/probe-after.txt")" "$want_after" "C3 after: each F1 spelling is refused; plain bash, bash -c, bash script.sh, cat and the test designer as before"
is "$(diff <(grep -v '^F1' "$BED/probe-before.txt") <(grep -v '^F1' "$BED/probe-after.txt") | wc -l)" 0 "C4 every case that is not an F1 spelling answers the same before and after"

cp "$HERE/f1_round2_cases.json" "$BED/f1_round2_cases.json"
mkdir -p "$BED/hooks-round1"; cp -a "$BED/hooks-before/." "$BED/hooks-round1/"; cp "$HERE/bash_writes.py.round1" "$BED/hooks-round1/bash_writes.py"
rm -rf "$BED/proj"; git clone -q --no-hardlinks --branch w2/integrate "$REPO" "$BED/proj" || { echo "clone failed"; exit 3; }
mkdir -p "$BED/proj/tests/acceptance/X"; echo "echo hi" > "$BED/proj/script.sh"; echo "x=1" > "$BED/proj/tests/acceptance/X/t.py"
python3 -B -I "$HERE/cases_probe.py" "$BED/f1_round2_cases.json" "$BED/proj" "$BED/hooks-before" "$BED/hooks-round1" "$BED/hooks-after" > "$BED/round2.txt" 2>&1
awk -F'|' 'BEGIN{printf "     %-36s %-7s %-8s %-8s %s\n", "id", "expect", "before", "round 1", "after"} {printf "     %-36s %-7s %-8s %-8s %s\n", $1, $2, $3, $4, $5}' "$BED/round2.txt"
is "$(awk -F'|' '$2 == "deny" && $5 != "deny"' "$BED/round2.txt" | wc -l)" 0 "C5 round 2's 38 cases (19 unquoted-and-file cases and their quoted twins): every one is refused after"
is "$(awk -F'|' '$2 == "allow" && ($3 != "allow" || $5 != "allow")' "$BED/round2.txt" | wc -l)" 0 "C6 the 7 controls are allowed before and after"
is "$(awk -F'|' '$3 == "deny" && $5 != "deny"' "$BED/round2.txt" | wc -l)" 0 "C7 no case refused before is allowed after (stricter only)"
echo "     refused before and allowed by the round 1 file (review F1): $(awk -F'|' '$3 == "deny" && $4 != "deny"' "$BED/round2.txt" | wc -l); newly refused after: $(awk -F'|' '$3 == "allow" && $5 == "deny"' "$BED/round2.txt" | wc -l)"
is "$(awk -F'|' '$3 == "deny" && $4 != "deny"' "$BED/round2.txt" | wc -l | awk '{print ($1 >= 10) ? "ok" : "few"}')" ok "C8 the round 1 file is looser than before on at least ten of these cases (review F1 reproduced), the after file on none"
python3 -B -I "$HERE/matrix_cases.py" "$BED/matrix_cases.json" > /dev/null
python3 -B -I "$HERE/cases_probe.py" "$BED/matrix_cases.json" "$BED/proj" "$BED/hooks-before" "$BED/hooks-round1" "$BED/hooks-after" > "$BED/matrix.txt" 2>&1
python3 -B -I - "$BED/matrix.txt" <<'EOF'
import collections, sys
rows = [l.rstrip("\n").split("|") for l in open(sys.argv[1])]
c = collections.Counter((r[-3], r[-1]) for r in rows)
lost = [r for r in rows if r[-3] == "deny" and r[-1] != "deny"]
lost1 = [r for r in rows if r[-3] == "deny" and r[-2] != "deny"]
new = collections.Counter(r[2] for r in rows if r[-3] == "allow" and r[-1] == "deny")
harmless = [r for r in rows if r[-3] == "allow" and r[-1] == "deny" and r[2] in ("echo hi", "echo $(date)")]
print(f"     {len(rows)} calls (20 heads x 8 bodies x quoted or not x 2 tails x engineer and auditor): refused before {sum(v for k, v in c.items() if k[0] == 'deny')}, after {sum(v for k, v in c.items() if k[1] == 'deny')}; refused before and allowed after: {len(lost)} (the round 1 file: {len(lost1)}); newly refused: {c[('allow', 'deny')]}, by body: {dict(new)}")
sys.exit(0 if not lost and not harmless else 1)
EOF
r $? "C9 the differential matrix through the whole hook: 1,280 calls, none refused before is allowed after, and no harmless body (echo hi, echo \$(date)) is newly refused"
echo "--- D. the follow-up tests (through heavy_slot.sh, TMPDIR in the bed)"
git apply "$ACT/followup-tests.diff"; r $? "D1 the follow-up tests apply to the clone"
cmp -s tests/unit/hooks/fixtures/f1_shell_options.json "$BED/f1.json"; r $? "D1b the follow-up's fixture copy is W2-42a's file, byte for byte"
cmp -s tests/unit/hooks/fixtures/f1_round2_cases.json "$HERE/f1_round2_cases.json"; r $? "D1c the follow-up's round 2 case file is the one the rehearsal ran in C"
is "$(git status --porcelain | sed 's/^...//' | sort | paste -sd,)" "$P,tests/unit/hooks/fixtures/,$T" "D2 the clone's changes are the hook, the one test file and its fixture copy"
bash "$ACT/apply.sh" undo > /dev/null
export GOV_LIVE_HOOK_CORPUS="$CORPUS"
bash "$HEAVY" python3 -m pytest -q -p no:cacheprovider "$T" -k "heredoc or option_values or w2_42a or round_2" > "$BED/d-before.txt" 2>&1
echo "     before: $(tail -1 "$BED/d-before.txt" | mask)"
nred=$(grep -cE '^E +(AssertionError: )?[^ ].*: want deny, got allow \(\)$' "$BED/d-before.txt")
n2=$(awk -F'|' '$2 == "deny" && $3 != "deny"' "$BED/round2.txt" | wc -l); exp_failed=$((2 + 12 + n2)); exp_pass=$((67 - exp_failed))
is "$(grep -c '^FAILED' "$BED/d-before.txt")|$(grep -o '[0-9]* passed' "$BED/d-before.txt" | tail -1)" "$exp_failed|$exp_pass passed" "D3 before: of the 67 new tests, $exp_failed are red: the F1 case group, the _kind table, 12 of W2-42a's 19 cases (the 12 spellings allowed before) and $n2 of round 2's 45 (the cases refused after and allowed before); the other $exp_pass green"
echo "     F1 spellings red before: $nred"
is "$nred" 12 "D4 before: the F1 case group has 12 red cases (the ten spellings, and the two unquoted bodies with nothing to expand: 'want deny, got allow')"
bash "$ACT/apply.sh" apply > /dev/null
bash "$HEAVY" python3 -m pytest -q -p no:cacheprovider "$T" -k "heredoc or option_values or w2_42a or round_2" > "$BED/d-after.txt" 2>&1
echo "     after: $(tail -1 "$BED/d-after.txt" | mask)"
grep -q '^67 passed' <(tail -1 "$BED/d-after.txt" | sed 's/^=* *//'); r $? "D5 after: the 67 new tests green (3, W2-42a's 19 and round 2's 45)"
bash "$HEAVY" python3 -m pytest -q -p no:cacheprovider tests/unit/hooks tests/unit/guard/test_w2_141_search.py tests/acceptance/W2-141/test_w2_141_hook.py > "$BED/d-all.txt" 2>&1
rc=$?; echo "     the hook's own suites after: $(tail -1 "$BED/d-all.txt" | mask)"
is "$rc" 0 "D6 after: tests/unit/hooks (the live hook's cases and the logged-refusals replay), test_w2_141_search.py and test_w2_141_hook.py green"
bash "$HEAVY" python3 -m pytest -q -p no:cacheprovider "$T" -k logged_refusals > "$BED/d-replay.txt" 2>&1
is "$(tail -1 "$BED/d-replay.txt" | grep -o '[0-9]* passed')" "1 passed" "D7 after: test_the_logged_refusals_replay_as_decided ran (the corpus is here) and passed"
unset GOV_LIVE_HOOK_CORPUS
git checkout -q -- "$T"; rm -rf tests/unit/hooks/fixtures

echo "--- E. undo and refusals"
out=$(bash "$ACT/apply.sh" undo); rc=$?; echo "     $out"
is "$rc" 0 "E1 undo (exit 0)"
cmp -s "$P" "$ACT/before/repo/$P"; r $? "E2 undone byte for byte"
out=$(bash "$ACT/apply.sh" check); rc=$?; is "$rc|${out%% (*}" "0|state before" "E3 check: state before (exit 0)"
echo "# a later change" >> "$P"
bash "$ACT/apply.sh" apply 2>&1 | mask | sed 's/^/     /'; is "${PIPESTATUS[0]}" 3 "E4 apply refuses a bash_writes.py changed since the freeze (exit 3)"
cp "$ACT/after/repo/$P" "$P"; echo "# a later change" >> "$P"
bash "$ACT/apply.sh" undo 2>&1 | mask | sed 's/^/     /'; is "${PIPESTATUS[0]}" 3 "E5 undo refuses it too (exit 3)"
bash "$ACT/apply.sh" verify 2>/dev/null; is "$?" 3 "E6 verify refuses it (exit 3)"
git checkout -q -- "$P"
ln -sf "$ACT/after/repo/$P" "$BED/link.py"; mv "$P" "$BED/real.py"; ln -s "$BED/link.py" "$P"
bash "$ACT/apply.sh" check 2>/dev/null; is "$?" 3 "E7 a link in the file's place is refused"
rm "$P"; mv "$BED/real.py" "$P"

echo "--- H. W2-42a's F1 fixture, every id through the hook before and after (an engineer writing under tests/acceptance/)"
git clone -q --no-hardlinks --branch w2/integrate "$REPO" "$BED/fxclone" || { echo "clone failed"; exit 3; }
mkdir -p "$BED/fxclone/tests/acceptance/X"; echo "echo hi" > "$BED/fxclone/script.sh"; echo "x = 1" > "$BED/fxclone/x.py"
echo "x = 1" > "$BED/fxclone/tests/acceptance/X/t.py"
python3 -B -I "$HERE/fx_probe.py" "$BED/hooks-before" "$BED/hooks-after" "$BED/fxclone" "$BED/f1.json" > "$BED/fx.txt" 2>&1; frc=$?
sed 's/^/     /' "$BED/fx.txt"
is "$frc" 0 "H1 the 15 shell spellings: 12 allowed before, all 15 refused after (the unquoted-delimiter case too, round 2); the 4 data controls keep their verdict (allowed); nothing refused before is allowed after"
echo "--- F. the main tree"
is "$(sha256sum "$REPO/$P" | cut -c1-64)" "$main_before" "F1 the main tree's bash_writes.py is unchanged"
is "$(sha256sum "$REPO/.claude/hooks/pretooluse.py" | cut -c1-64)" "$main_pre" "F2 the main tree's pretooluse.py is unchanged"
is "$(git -C "$REPO" status --porcelain -- .claude governance tests src | sha256sum | cut -c1-64)" "$main_status" "F3 the main tree's tracked .claude/governance/tests/src status unchanged"

echo "--- G. the guard replay (every refused call is still refused)"
cd "$BED" || exit 3
if [ -n "$CALLS" ]; then
  python3 -B -I "$HERE/replay5.py" "$BED/hooks-before" "$BED/hooks-after" "$CORPUS" "$CALLS" > "$BED/replay.txt" 2>&1; rrc=$?
else
  python3 -B -I "$HERE/replay5.py" "$BED/hooks-before" "$BED/hooks-after" "$CORPUS" > "$BED/replay.txt" 2>&1; rrc=$?
fi
sed 's/^/     /' "$BED/replay.txt"
is "$rrc" 0 "G1 no call refused before is allowed after, no hook error"
nnew=$(sed -n 's/^allowed before, refused after (replay_refused): \([0-9]*\).*/\1/p' "$BED/replay.txt")
r 0 "G2 newly refused calls (the review's replay_refused list), each with its hook reason above: ${nnew:-?}"
is "$(find "$ACT" -name __pycache__ -o -name '*.pyc' | wc -l)" 0 "G3 after the whole rehearsal the bundle still holds no __pycache__ or bytecode (nothing imported the frozen copies in place)"
echo "=== $ok ok, $bad failed"
echo "failures: $bad"
