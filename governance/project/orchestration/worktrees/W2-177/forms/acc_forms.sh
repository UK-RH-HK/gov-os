#!/bin/bash
# W2-177 (DAEO-1k7y) P-W2-177-1: run the W2-96 and W2-56 signal acceptance files in each start form, N times each.
# usage: bash acc_forms.sh <tree> <tag> <N> [form ...]    forms: fg setsid-bg bg-job (default: fg setsid-bg)
#   fg         the verify's environment in the foreground: HOME an empty folder, SIGINT at default
#   setsid-bg  lead_verify.sh's form and the cron nightly's: `setsid ... &` from a non-interactive bash (SIGINT ignored)
#   bg-job     a plain background job `... &` from a non-interactive bash (SIGINT ignored)
# Output: <tree>/.gov-runtime/scratch/acc-forms/<tag>/<form>-<i>.txt and counts.txt. Every pytest through heavy_slot.sh,
# TMPDIR outside the repository, PYTHONUSERBASE=/home/usain/.local.
set -u
TREE=${1:?tree}; TAG=${2:?tag}; N=${3:?N}; shift 3
FORMS=("$@"); [ ${#FORMS[@]} -eq 0 ] && FORMS=(fg setsid-bg)
OUT=$TREE/.gov-runtime/scratch/acc-forms/$TAG
EMPTY=$TREE/.gov-runtime/scratch/empty-home
mkdir -p "$OUT" "$EMPTY"
INNER=$OUT/inner.sh
cat > "$INNER" <<EOF
#!/bin/bash
cd "$TREE" || exit 2
export PYTHONPATH=$TREE/src PYTHONUSERBASE=/home/usain/.local
export TMPDIR=\$(mktemp -d /tmp/w2-177-acc.XXXXXX) || { echo "no TMPDIR outside the repository"; exit 3; }
[ -n "\$TMPDIR" ] || exit 3
python3 -c 'import signal; print("SIGINT-ignored-at-start:", int(signal.getsignal(signal.SIGINT) == signal.SIG_IGN))'
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \\
  python3 -m pytest \\
  tests/acceptance/W2-96/test_w2_96_at_run_2.py \\
  tests/acceptance/W2-96/test_w2_96_at_no_leak.py \\
  tests/acceptance/W2-56/test_w2_56_endings.py \\
  -q -rfEs -p no:cacheprovider -o tmp_path_retention_policy=failed
code=\$?
rm -rf -- "\$TMPDIR"
exit \$code
EOF
cd "$TREE" || exit 2
for form in "${FORMS[@]}"; do
  pass=0; fail=0
  for i in $(seq 1 "$N"); do
    log=$OUT/$form-$i.txt
    case $form in
      fg)        env HOME="$EMPTY" bash "$INNER" > "$log" 2>&1 < /dev/null ;;
      setsid-bg) env HOME="$EMPTY" setsid bash "$INNER" > "$log" 2>&1 < /dev/null & wait $! ;;
      bg-job)    env HOME="$EMPTY" bash "$INNER" > "$log" 2>&1 < /dev/null & wait $! ;;
      *) echo "unknown form $form"; exit 2 ;;
    esac
    summary=$(grep -E "^[0-9]+ (passed|failed|error)|^=+ .*(passed|failed|error)" "$log" | tail -1)
    ign=$(grep -o "SIGINT-ignored-at-start: [01]" "$log" | head -1)
    echo "$form run $i: $ign | $summary" | tee -a "$OUT/counts.txt"
    if grep -qE "failed|error|skipped" <<< "$summary" || [ -z "$summary" ]; then fail=$((fail+1)); else pass=$((pass+1)); fi
  done
  echo "FORM $form: $pass of $N runs all passed, $fail with a red (or skip)" | tee -a "$OUT/counts.txt"
done
echo done > "$OUT/exit"
