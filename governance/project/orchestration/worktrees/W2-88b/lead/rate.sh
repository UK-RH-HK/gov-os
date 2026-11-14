# samples the gitleaks children of grafana's A6 gov process for 20 s; prints distinct pids seen
seen=""
for i in $(seq 1 40); do
  for p in $(pgrep -P 501192 gitleaks); do case " $seen " in *" $p "*) ;; *) seen="$seen $p";; esac; done
  sleep 0.5
done
echo "distinct gitleaks in 20s: $(echo $seen | wc -w)"
