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
mkdir -p "$BED/tmp"; export TMPDIR="$BED/tmp"
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
is "$(grep -c '^-[^-]' "$BED/after-minus-before.diff")" 5 "A6 five lines removed (_kind's shell branch), the rest added"
echo "     $(grep -c '^+[^+]' "$BED/after-minus-before.diff") lines added"
python3 -I - "$ACT/before/repo/$P" "$ACT/after/repo/$P" <<'EOF'
import sys
b, a = (open(p).read() for p in sys.argv[1:3])
cut = lambda t: (t[:t.index("\ndef _kind(words):")], t[t.index("\n_PARAM = "):])
sys.exit(0 if cut(b) == cut(a) else 1)
EOF
r $? "A7 the text before _kind and from _PARAM on is identical: only _kind's own region changes"
git -C "$REPO" show refs/heads/w2/W2-42a:tests/acceptance/W2-42a/fixtures/f1_shell_options.json > "$BED/f1.json"; r $? "A9 W2-42a's F1 fixture read from refs/heads/w2/W2-42a"
is "$(git -C "$REPO" ls-files -s -- $P | cut -d' ' -f2)" "$(git -C "$REPO" hash-object "$ACT/before/repo/$P")" "A8 the before copy is the committed blob (HEAD)"

echo "--- B. a fresh clone of w2/integrate"
git clone -q --no-hardlinks --branch w2/integrate "$REPO" "$BED/clone" || { echo "clone failed"; exit 3; }
cd "$BED/clone" || exit 3
out=$(bash "$ACT/apply.sh" check); rc=$?; echo "     $out"
is "$rc|${out%% (*}" "0|state before" "B1 check: state before (exit 0)"
python3 -I - "$HERE/checks.json" > "$BED/checks-before.txt" <<'EOF'
import json, subprocess, sys
for c in json.load(open(sys.argv[1])):
    print(subprocess.run(["bash", "-c", c], capture_output=True, text=True).returncode)
EOF
is "$(paste -sd, "$BED/checks-before.txt")" "0,1,1" "B2 the checks before the apply: 1 passes (it parses), 2 and 3 refuse (exits 0,1,1)"
mode0=$(stat -c %a "$P")
out=$(bash "$ACT/apply.sh" apply); rc=$?; echo "     $out"
is "$rc" 0 "B3 apply (exit 0)"
cmp -s "$P" "$ACT/after/repo/$P"; r $? "B4 the file is the after, byte for byte"
is "$(stat -c %a "$P")" "$mode0" "B5 its mode kept ($mode0)"
bash "$ACT/apply.sh" verify; r $? "B6 verify (exit 0)"
out=$(bash "$ACT/apply.sh" apply); rc=$?; echo "     $out"
is "$rc|${out##*; }" "0|nothing to do" "B7 apply again: nothing to do"
is "$(git status --porcelain | sed 's/^...//' | paste -sd,)" "$P" "B8 only bash_writes.py changed in the clone"
python3 -I - "$HERE/checks.json" > "$BED/checks-after.txt" 2> "$BED/checks-after.err" <<'EOF'
import json, subprocess, sys
for c in json.load(open(sys.argv[1])):
    p = subprocess.run(["bash", "-c", c], capture_output=True, text=True)
    print(p.returncode)
    sys.stderr.write(p.stdout[-300:])
EOF
sed 's/^/     /' "$BED/checks-after.err"
is "$(paste -sd, "$BED/checks-after.txt")" "0,0,0" "B9 the manifest's three checks after the apply (exits 0,0,0)"

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
python3 -I "$BED/probe.py" "$BED/hooks-before" "$BED/clone" > "$BED/probe-before.txt" 2>&1
python3 -I "$BED/probe.py" "$BED/hooks-after" "$BED/clone" > "$BED/probe-after.txt" 2>&1
want_before="F1 bash -euo pipefail|allow F1 bash -o pipefail|allow F1 bash -O extglob|allow F1 bash --rcfile|allow F1 bash --init-file|allow F1 cat | bash -o pipefail|allow F1 bash /dev/stdin|allow plain bash|deny bash -c|allow bash script.sh|allow bash -o pipefail script.sh|allow cat data|allow designer, bash -euo pipefail|allow"
want_after="F1 bash -euo pipefail|deny F1 bash -o pipefail|deny F1 bash -O extglob|deny F1 bash --rcfile|deny F1 bash --init-file|deny F1 cat | bash -o pipefail|deny F1 bash /dev/stdin|deny plain bash|deny bash -c|allow bash script.sh|allow bash -o pipefail script.sh|allow cat data|allow designer, bash -euo pipefail|allow"
sed 's/^/     before: /' "$BED/probe-before.txt"
is "$(paste -sd' ' "$BED/probe-before.txt")" "$want_before" "C2 before: each F1 spelling is allowed (the defect reproduced); plain bash refused; the others as expected"
sed 's/^/     after:  /' "$BED/probe-after.txt"
is "$(paste -sd' ' "$BED/probe-after.txt")" "$want_after" "C3 after: each F1 spelling is refused; plain bash, bash -c, bash script.sh, cat and the test designer as before"
is "$(diff <(grep -v '^F1' "$BED/probe-before.txt") <(grep -v '^F1' "$BED/probe-after.txt") | wc -l)" 0 "C4 every case that is not an F1 spelling answers the same before and after"

echo "--- D. the follow-up tests (through heavy_slot.sh, TMPDIR in the bed)"
git apply "$ACT/followup-tests.diff"; r $? "D1 the follow-up tests apply to the clone"
cmp -s tests/unit/hooks/fixtures/f1_shell_options.json "$BED/f1.json"; r $? "D1b the follow-up's fixture copy is W2-42a's file, byte for byte"
is "$(git status --porcelain | sed 's/^...//' | sort | paste -sd,)" "$P,tests/unit/hooks/fixtures/,$T" "D2 the clone's changes are the hook, the one test file and its fixture copy"
bash "$ACT/apply.sh" undo > /dev/null
export GOV_LIVE_HOOK_CORPUS="$CORPUS"
bash "$HEAVY" python3 -m pytest -q -p no:cacheprovider "$T" -k "heredoc or option_values or w2_42a" > "$BED/d-before.txt" 2>&1
echo "     before: $(tail -1 "$BED/d-before.txt" | mask)"
nred=$(grep -cE '^E +(AssertionError: )?[^ ].*: want deny, got allow \(\)$' "$BED/d-before.txt")
is "$(grep -c '^FAILED' "$BED/d-before.txt")|$(grep -o '[0-9]* passed' "$BED/d-before.txt" | tail -1)" "13|9 passed" "D3 before: red are the F1 case group, the _kind table and 11 of W2-42a's 19 cases (the 12 allowed shell spellings less the unquoted one); green the data-as-before group, 4 controls, 4 spellings"
echo "     F1 spellings red before: $nred"
is "$nred" 10 "D4 before: ten F1 spellings allowed (ten cases named 'want deny, got allow')"
bash "$ACT/apply.sh" apply > /dev/null
bash "$HEAVY" python3 -m pytest -q -p no:cacheprovider "$T" -k "heredoc or option_values or w2_42a" > "$BED/d-after.txt" 2>&1
echo "     after: $(tail -1 "$BED/d-after.txt" | mask)"
grep -q '^22 passed' <(tail -1 "$BED/d-after.txt" | sed 's/^=* *//'); r $? "D5 after: the 22 new tests green (3, and W2-42a's 19)"
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
python3 -I "$HERE/fx_probe.py" "$BED/hooks-before" "$BED/hooks-after" "$BED/fxclone" "$BED/f1.json" > "$BED/fx.txt" 2>&1; frc=$?
sed 's/^/     /' "$BED/fx.txt"
is "$frc" 0 "H1 the 15 shell spellings: 12 allowed before, 14 refused after (the unquoted-delimiter case is let through, G-1, as plain bash <<EOF is today); the 4 data controls keep their verdict (allowed); nothing refused before is allowed after"
echo "--- F. the main tree"
is "$(sha256sum "$REPO/$P" | cut -c1-64)" "$main_before" "F1 the main tree's bash_writes.py is unchanged"
is "$(sha256sum "$REPO/.claude/hooks/pretooluse.py" | cut -c1-64)" "$main_pre" "F2 the main tree's pretooluse.py is unchanged"
is "$(git -C "$REPO" status --porcelain -- .claude governance tests src | sha256sum | cut -c1-64)" "$main_status" "F3 the main tree's tracked .claude/governance/tests/src status unchanged"

echo "--- G. the guard replay (every refused call is still refused)"
cd "$BED" || exit 3
if [ -n "$CALLS" ]; then
  python3 -I "$HERE/replay5.py" "$BED/hooks-before" "$BED/hooks-after" "$CORPUS" "$CALLS" > "$BED/replay.txt" 2>&1; rrc=$?
else
  python3 -I "$HERE/replay5.py" "$BED/hooks-before" "$BED/hooks-after" "$CORPUS" > "$BED/replay.txt" 2>&1; rrc=$?
fi
sed 's/^/     /' "$BED/replay.txt"
is "$rrc" 0 "G1 no call refused before is allowed after, no hook error"
is "$(grep -c 'allowed before, refused after (replay_refused): 0' "$BED/replay.txt")" 1 "G2 no call is newly refused (the replay_refused list of the review is empty)"
echo "=== $ok ok, $bad failed"
echo "failures: $bad"
