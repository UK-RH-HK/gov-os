cd /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/act-w1-01-exempt-3/tmp/clone5
G=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/act-w1-01-exempt-3/acts/ACT-W1-01-EXEMPT-3
sha256sum $G/manifest.json      # expect 6af6bdeb15b018d37f8b11b451b783dbb959ea33e762c89cefaa1033f01cba5e
git status --short              # the map must not be listed (other lines are the CTO's and stay uncommitted)
bash $G/apply.sh check          # expect: state before (sha256 fb52ab2dc756)  (state other: stop, tell the CTO)
bash $G/apply.sh apply          # expect: state applied (sha256 f4029cfb4942)
bash $G/apply.sh verify         # silent, exit 0
PYTHONPATH=src python3 -m gov.check.pathmap; echo $?   # expect: 0, with no output before it
git diff --numstat -- governance/project/path-map.yaml  # expect: 2  0  governance/project/path-map.yaml
git commit -m "ACT-W1-01-EXEMPT-3: acceptance_exemptions lists the owner's ACT-OPERATOR-ROUNDS-1 commit 6fbe73b1adde (DEC-1136 (1))" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1136, DEC-906, DEC-253" --trailer "Role: owner" -- governance/project/path-map.yaml
"$(head -1 ~/.local/bin/gov | cut -c3-)" -I -c 'import yaml; from pathlib import Path; from gov.close import gates; s=yaml.safe_load(open("governance/project/path-map.yaml")); print("6fbe73b1adde40571f00d490b4b478cf86b70a52" in gates.owner_listed(Path("."), s))'   # expect: True
PYTHONPATH=src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W1-01/test_w1_01_history.py::test_only_the_test_designer_commits_to_acceptance_tests tests/acceptance/W1-01/test_w1_01_integration_merges.py::test_the_integration_merges_of_this_repository_pass -q -p no:cacheprovider
