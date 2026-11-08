"""Test helpers: a counting attempt on the planted set (the fake gov's first calls, the measure's line form), and a
fake claude that answers by the planted rules and counts its calls."""
import json
import subprocess
import threading
from pathlib import Path

import yaml

import f80lib as L
import fresh80_reader as RD


def make_attempt(planted, name="attempt-1"):
    runs = planted["root"] / "runs/fresh-80"
    att = runs / name
    (att / "kept").mkdir(parents=True)
    lines, n = ["families: contract (4 members), kernel (3 members), agents (2 members)"], 0
    for f in sorted(planted["hidden"].glob("*.yaml")):
        d = yaml.safe_load(f.read_text())
        n += 1
        out = subprocess.run([str(planted["gov"]), "retrieve", d["question"], "--json"], capture_output=True,
                             text=True).stdout
        (att / "kept" / f"{n:05d}.json").write_text(out)
        hit = "[hit]" in d["question"]
        lines.append(f"{d['id']} (hidden): hit@5 {'yes' if hit else 'no'} (first gold rank {3 if hit else '-'}), in the "
                     f"bundle {'yes' if hit else 'no'}; full evidence {'yes' if hit else 'no'} ({int(hit)} of 1 "
                     f"pieces); 1 calls")
    lines.append("total: hit@5 70 of 80 (87.5 %, floor 85); full evidence 70 of 80 (87.5 %, target 99 %)")
    (att / "measure.txt").write_text("\n".join(lines) + "\n")
    (att / "DONE").write_text("x")
    (runs / "COUNTS").write_text(name + "\n")
    (runs / "USED").write_text("x")
    return att


class FakeClaude:
    """Reader: answers citing the gold when a bundle holds docs/q/<id>.md lines 1-3; not_found for DEC-99999;
    search_again ("again <id>") otherwise. Grader: correct; check: correct unless the id is in ``check_wrong``.
    ``garbage_once``: ids whose first reader call returns nothing. ``cite_outside``: ids that also cite an unseen
    range. Cost per call ``cost``."""

    def __init__(self, cost=0.01, check_wrong=(), garbage_once=(), cite_outside=(), wrong=()):
        self.cost, self.check_wrong, self.garbage = cost, set(check_wrong), set(garbage_once)
        self.outside, self.wrong = set(cite_outside), set(wrong)
        self.calls, self.prompts, self.lock = 0, [], threading.Lock()

    def __call__(self, argv, prompt, cwd):
        system = argv[argv.index("--system-prompt") + 1]
        model = argv[argv.index("--model") + 1]
        with self.lock:
            self.calls += 1
            self.prompts.append((system, prompt))
        import re
        qid = (re.search(r"\b(v\d\d)\b", prompt) or [None, "v00"])[1]
        if "grade one answer" in system:
            g = "correct"
            if model == "claude-sonnet-5-5" and qid in self.check_wrong:
                g = "wrong"
            if qid in self.wrong:
                g = "wrong"
            return json.dumps({"structured_output": {"grade": g, "reason": "r"}, "total_cost_usd": self.cost})
        if "choosing search words" in system:
            return json.dumps({"structured_output": {"search": f"again {qid}"}, "total_cost_usd": self.cost})
        with self.lock:
            if qid in self.garbage:
                self.garbage.discard(qid)
                return "not json"
        if "DEC-99999" in prompt:
            out = {"verdict": "not_found", "answer": "", "citations": [], "search": ""}
        elif f"--- docs/q/{qid}.md lines 1-3" in prompt:
            cites = [{"path": f"docs/q/{qid}.md", "start_line": 1, "end_line": 3}]
            if qid in self.outside:
                cites.append({"path": "docs/elsewhere.md", "start_line": 5, "end_line": 9})
            out = {"verdict": "answer", "answer": f"fact {qid}", "citations": cites, "search": ""}
        else:
            out = {"verdict": "search_again", "answer": "", "citations": [], "search": f"again {qid}"}
        return json.dumps({"structured_output": out, "total_cost_usd": self.cost, "usage": {"input_tokens": 1}})


def setup(planted, monkeypatch, fake):
    monkeypatch.setattr(L, "_run_claude", fake)
    monkeypatch.setattr(L, "GOV", str(planted["gov"]))
    monkeypatch.setattr(L, "hold_on", lambda: True)
    monkeypatch.setattr(L, "pinned", lambda: True)
    monkeypatch.setattr(L, "R", planted["main"])
    monkeypatch.delenv("GOV_ROLE", raising=False)


def preflight_json(planted):
    runs = planted["root"] / "runs/fresh-80"
    runs.mkdir(parents=True, exist_ok=True)
    f = runs / "preflight.json"
    d = json.loads(f.read_text()) if f.is_file() else {}
    d.update(all_ok=True, at="test", item1={"sha256": L.set_digest(planted["root"])})
    d.setdefault("item6", {"nowhere": True})
    f.write_text(json.dumps(d))


def reader(planted, *extra):
    """The reader as the CTO runs it: through L.run_tool (ACT checked, standard error to the run folder)."""
    preflight_json(planted)
    return L.run_tool("reader", RD.main, ["--sets-root", str(planted["root"]), "--clone", str(planted["clone"]), *extra])


def rows(planted, folder="reader"):
    d = planted["root"] / "runs/fresh-80" / folder
    return {f.stem: json.loads(f.read_text()) for f in d.glob("v*.json")}


def clean(out, planted):
    for line in out.splitlines():
        assert str(planted["root"]) + "/" not in line, line
        assert "memory-verdict-2/" not in line and "fresh-80/" not in line, line
        assert "planted question" not in line and "fact v" not in line and "gold v" not in line, line
        assert not ("nonexistent-id" in line and "v80" in line), line
