"""Write the final skilleval run's replies, paired with the records' last three entries per skill, to a markdown file."""
import json

import yaml

ROOT = "/home/usain/gov-os-worktrees/W2-101"
CAP = ROOT + "/.gov-runtime/scratch/lead/capture/replies.jsonl"
OUT = ROOT + "/.gov-runtime/scratch/lead/briefs/ps-3-final-replies.md"
lines = [json.loads(x) for x in open(CAP)][12:30]  # lines 13-30: the final run, session then judgement per scenario
out = ["# The final gov skilleval run (lead capture; each session reply and its judgement)\n"]
i = 0
for skill in ("frontend", "ui-ux", "devops"):
    recs = yaml.safe_load(open(f"{ROOT}/template/governance/kernel/skills/{skill}/scenario-records.yaml"))["records"][-3:]
    for rec in recs:
        session, judge = lines[i], lines[i + 1]
        i += 2
        assert not session["prompt"].startswith("You judge") and judge["prompt"].startswith("You judge")
        reply = json.loads(session["stdout"])["result"]
        verdict = json.loads(judge["stdout"])["result"]
        out.append(f"## {skill} scenario {rec['scenario']}: {rec['title']}\n")
        out.append(f"- record: verdict `{rec['verdict']}`, run_at `{rec['run_at']}`, skill_version "
                   f"`{rec['skill_version']}`, model `{rec['model']}`, cost_usd {rec['cost_usd']}\n")
        out.append("### Session reply\n\n" + reply.strip() + "\n")
        out.append("### Judgement\n\n" + verdict.strip() + "\n")
open(OUT, "w").write("\n".join(out))
print("wrote", OUT, i // 2, "scenarios")
