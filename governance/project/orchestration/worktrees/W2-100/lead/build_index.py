"""Index the captured replies (W2-100, S4): for each skill's record entry, the session's reply and the judge's verdict
line, matched by the scenario's Situation (session prompt) and Pass line (judge prompt) and by time order."""
import json
import re
from pathlib import Path

import yaml

base = Path("/home/usain/gov-os-worktrees/W2-100")
skills_dir = base / "template/governance/kernel/skills"
tdir = base / ".gov-runtime/scratch/lead/skilleval/transcripts"
out = base / ".gov-runtime/scratch/lead/skilleval/transcripts-index.md"


def scenarios(skill):
    text = (skills_dir / skill / "scenarios.md").read_text()
    found = {}
    for block in re.split(r"(?m)^(?=## \d+\.)", text):
        m = re.match(r"## (\d+)\. (.*)", block)
        if not m:
            continue
        sit = re.search(r"\*\*Situation:\*\*\s*(.*?)(?=\n- \*\*Expected)", block, re.S).group(1)
        pas = re.search(r"\*\*Pass line:\*\*\s*(.*)", block, re.S).group(1)
        found[int(m.group(1))] = (m.group(2).strip(), " ".join(sit.split()), " ".join(pas.split()))
    return found


calls = []
for meta in sorted(tdir.glob("*.meta")):
    stem = meta.with_suffix("")
    prompt = " ".join(Path(str(stem) + ".prompt").read_text().split())
    try:
        reply = json.loads(Path(str(stem) + ".json").read_text())["result"]
    except Exception as exc:  # noqa: BLE001
        reply = f"<unreadable: {exc}>"
    calls.append({"stem": stem.name, "meta": meta.read_text(), "prompt": prompt, "reply": reply})

lines = ["# W2-100: the captured replies of the lead's real gov skilleval runs (S4)", "",
         "Run 1 (01:21-01:30 UTC) was made before the capture: its replies were not kept. Every later entry below",
         "pairs the record entry with the session's reply and the judge's last lines.", ""]
for skill in ("backend", "api", "data", "security"):
    sc = scenarios(skill)
    recs = yaml.safe_load((skills_dir / skill / "scenario-records.yaml").read_text())["records"]
    used = set()
    lines.append(f"## {skill}")
    for r in recs:
        n = r["scenario"]
        title, sit, pas = sc[n]
        run_at = str(r["run_at"]).replace(" ", "T")
        lines.append(f"### Scenario {n}: {r['title']} | verdict {r['verdict']} | run_at {r['run_at']} | skill_version {r['skill_version']}")
        sess = [c for c in calls if c["stem"] not in used and sit[:120] in c["prompt"] and f"skills={skill} " in c["meta"]]
        judge = [c for c in calls if c["stem"] not in used and pas[:120] in c["prompt"] and "judge" in c["meta"]]
        # a record's run_at is written after its judge; the matching calls are the earliest unused ones
        if not sess or not judge or str(r["run_at"]) < "2026-11-14T01:35":
            lines += ["(reply not kept: run 1, before the capture)", ""]
            continue
        s, j = sess[0], judge[0]
        used.update({s["stem"], j["stem"]})
        lines += [f"Session call {s['stem']}; judge call {j['stem']}.", "", "Session reply:", "", "~~~",
                  s["reply"].strip(), "~~~", "", "Judge's last lines:", "", "~~~",
                  "\n".join(j["reply"].strip().splitlines()[-4:]), "~~~", ""]
out.write_text("\n".join(lines) + "\n")
print(out, len(lines))
