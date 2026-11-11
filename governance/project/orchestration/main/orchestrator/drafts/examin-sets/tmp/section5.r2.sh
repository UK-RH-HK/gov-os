cd /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/examin-sets/tmp/clone5
G=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/accepted-reds-1/acts-r2/ACT-ACCEPTED-REDS-1
sha256sum $G/manifest.json      # expect b8df21d891600ff4701ff264ff94f32257c4c9150ae4eb4a3254af2662248ea7
git status --short              # the map must not be listed (other lines are the CTO's and stay uncommitted)
bash $G/apply.sh check          # expect: state before (sha256 0ec1d20da86a)  (state other: stop, tell the CTO; it means EXAMIN-SETS-1 is not applied yet, or the map moved)
bash $G/apply.sh apply          # expect: state applied (sha256 5654eca4c139)
bash $G/apply.sh verify         # silent, exit 0
PYTHONPATH=src python3 -m gov.check.pathmap; echo $?   # expect: 0, with no output before it
git diff --numstat -- governance/project/path-map.yaml  # expect: 9  1  governance/project/path-map.yaml
git commit -m "ACT-ACCEPTED-REDS-1: accepted_reds lists the two warm real-model latency cases (W1-19, W2-13) until W2-155 closes (DEC-1134)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1134, DEC-1125" --trailer "Role: owner" -- governance/project/path-map.yaml
"$(head -1 ~/.local/bin/gov | cut -c3-)" -I -c 'from gov.close import ratchet; c,f=ratchet.counted_entries(".","accepted_reds"); print(len(c),len(f))'   # expect: 2 0
