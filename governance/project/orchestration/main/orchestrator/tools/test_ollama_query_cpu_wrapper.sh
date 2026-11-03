#!/bin/bash
# The wrapper with a fake real binary: 11435 serve gets the GPU hidden and CPUs 8-11; everything else passes through.
set -u
here=$(cd "$(dirname "$0")" && pwd)
t=$(mktemp -d)
cat > "$t/fake" <<'EOF'
#!/bin/bash
echo "args=$* cuda=${CUDA_VISIBLE_DEVICES-unset} cpus=$(taskset -cp $$ | sed 's/.*: //')${GOMAXPROCS:+ gomax=$GOMAXPROCS}${OMP_NUM_THREADS:+ omp=$OMP_NUM_THREADS}"
EOF
chmod +x "$t/fake"
run() { GOV_OLLAMA_WRAP_REAL="$t/fake" GOV_OLLAMA_WRAP_LOGDIR="$t" bash "$here/ollama_query_cpu_wrapper.sh" "$@"; }
fail=0
check() { if [ "$1" = "$2" ]; then echo "ok   $3"; else echo "FAIL $3: got [$1] want [$2]"; fail=1; fi; }
: > "$t/serve-11435.log"
OLLAMA_HOST=127.0.0.1:11435 run serve; check "$(tail -1 "$t/serve-11435.log")" "args=serve cuda=-1 cpus=8-11" "11435 serve: GPU hidden, CPUs 8-11, to its log"
OLLAMA_HOST=http://127.0.0.1:11435 run serve; check "$(tail -1 "$t/serve-11435.log")" "args=serve cuda=-1 cpus=8-11" "11435 as a URL"
check "$(grep -c 'started (cpu) by the wrapper; caller pid' "$t/query-autostart.log")" "2" "each start recorded with its caller"
echo gpu > "$t/query-server-device"
OLLAMA_HOST=127.0.0.1:11435 CUDA_VISIBLE_DEVICES=-1 run serve; check "$(tail -1 "$t/serve-11435.log")" "args=serve cuda=unset cpus=8-11" "device file gpu: the GPU visible (even if the caller hid it), same CPUs and log"
check "$(grep -c 'started (gpu) by the wrapper' "$t/query-autostart.log")" "1" "a gpu start recorded as such"
echo cpu > "$t/query-server-device"
OLLAMA_HOST=127.0.0.1:11435 run serve; check "$(tail -1 "$t/serve-11435.log")" "args=serve cuda=-1 cpus=8-11" "device file cpu: the GPU hidden again"
echo junk > "$t/query-server-device"
OLLAMA_HOST=127.0.0.1:11435 run serve; check "$(tail -1 "$t/serve-11435.log")" "args=serve cuda=-1 cpus=8-11" "an unreadable device file: the CPU (the safe side)"
rm "$t/query-server-device"
cpus=$(taskset -cp $$ | sed 's/.*: //')
check "$(OLLAMA_HOST=127.0.0.1:11434 CUDA_VISIBLE_DEVICES= run serve)" "args=serve cuda= cpus=$cpus" "11434 serve passes through unchanged"
check "$(unset OLLAMA_HOST; run serve)" "args=serve cuda=unset cpus=$cpus" "no OLLAMA_HOST passes through"
check "$(OLLAMA_HOST=127.0.0.1:11435 run ps)" "args=ps cuda=unset cpus=$cpus" "11435 non-serve passes through"
check "$(OLLAMA_HOST=127.0.0.1:114350 run serve)" "args=serve cuda=unset cpus=$cpus" "another port is not caught"
check "$(OLLAMA_HOST=127.0.0.1:11434 GOMAXPROCS=1 OMP_NUM_THREADS=1 run serve)" "args=serve cuda=unset cpus=$cpus" "a serve drops a heavy slot's thread budget (11434)"
OLLAMA_HOST=127.0.0.1:11435 GOMAXPROCS=1 OMP_NUM_THREADS=1 run serve; check "$(tail -1 "$t/serve-11435.log")" "args=serve cuda=-1 cpus=8-11" "a serve drops a heavy slot's thread budget (11435)"
check "$(OLLAMA_HOST=127.0.0.1:11435 GOMAXPROCS=1 run ps)" "args=ps cuda=unset cpus=$cpus gomax=1" "a non-serve keeps its environment"
rm -r "$t"
exit $fail
