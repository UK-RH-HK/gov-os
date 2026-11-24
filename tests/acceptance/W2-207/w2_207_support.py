"""Support for the W2-207 acceptance tests: planted transcripts, a planted price table, `gov usage` as a child process.

Nothing real is read: HOME, the Gov OS root and the repositories all live under the test's tmp_path.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[3] / "src"

# Rates in USD per million tokens, chosen so the hand-computed costs are exact to 6 decimals.
PRICES = """\
date: 2026-11-01
models:
  m-a:
    input: 10
    output: 20
    cache_read: 1
    cache_creation: 5
  m-b:
    input: 2
    output: 4
    cache_read: 0.5
    cache_creation: 1
"""
RATES = {"m-a": (10, 20, 1, 5), "m-b": (2, 4, 0.5, 1)}
KINDS = ("input", "output", "cache_read", "cache_creation")


def cost(model, i, o, cr, cc):
    r = RATES[model]
    return round((i * r[0] + o * r[1] + cr * r[2] + cc * r[3]) / 1e6, 6)


def ts(day, hms="10:00:00"):
    return f"{day}T{hms}.000Z"


class Env:
    def __init__(self, base: Path):
        self.base = base
        self.home = base / "home"
        self.root = base / "root"
        self.repos = base / "repos"
        for p in (self.home, self.root, self.repos):
            p.mkdir(parents=True)
        self.usage_dir = self.home / ".gov-os" / "usage"

    # -- planting -------------------------------------------------------------------------------
    def prices(self, text=PRICES):
        p = self.root / "governance" / "project" / "usage-prices.yaml"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def _log(self, name):
        p = self.root / ".gov-runtime" / "scratch" / "orchestrator" / "log" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def usage_txt(self, lines):
        self._log("usage.txt").write_text("\n".join(lines) + "\n")

    def cto(self, *sessions):
        self._log("cto-session.txt").write_text("\n".join(sessions) + "\n")

    def repo(self, name) -> Path:
        p = self.repos / name
        p.mkdir(parents=True, exist_ok=True)
        return p

    def launch(self, repo: Path, session, role):
        p = repo / ".gov-runtime" / "launches" / f"{session}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"record": "gov-launch", "session_id": session, "role": role}))

    def folder(self, repo: Path) -> Path:
        d = self.home / ".claude" / "projects" / str(repo).replace("/", "-")
        d.mkdir(parents=True, exist_ok=True)
        return d

    def transcript(self, repo: Path, session, lines, file=None, helper=None, agent_type=None):
        """Write a transcript (list of dicts or raw strings). helper=<id> puts it under subagents/."""
        d = self.folder(repo)
        if helper:
            d = d / session / "subagents"
            d.mkdir(parents=True, exist_ok=True)
            path = d / f"agent-{helper}.jsonl"
            if agent_type:
                (d / f"agent-{helper}.meta.json").write_text(json.dumps({"agentType": agent_type}))
        else:
            path = d / f"{file or session}.jsonl"
        path.write_text("\n".join(x if isinstance(x, str) else json.dumps(x) for x in lines) + "\n")
        return path

    @staticmethod
    def msg(repo: Path, session, mid, when, model, i, o, cr, cc, sidechain=False):
        return {
            "type": "assistant",
            "isSidechain": sidechain,
            "sessionId": session,
            "cwd": str(repo),
            "timestamp": when,
            "message": {
                "id": mid,
                "role": "assistant",
                "model": model,
                "usage": {
                    "input_tokens": i,
                    "cache_creation_input_tokens": cc,
                    "cache_read_input_tokens": cr,
                    "output_tokens": o,
                },
            },
        }

    # -- running --------------------------------------------------------------------------------
    def run(self, *args, root=True):
        env = dict(os.environ)
        env.update(HOME=str(self.home), PYTHONPATH=str(SRC), GOV_USAGE_NOW="2026-11-25T12:00:00Z")
        cmd = [sys.executable, "-m", "gov.cli.main", "usage", *args]
        if root:
            cmd += ["--root", str(self.root)]
        return subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120, cwd=str(self.base))

    def daily(self, date, *extra):
        return self.run("daily", "--date", date, *extra)

    def record(self, date) -> dict:
        return json.loads((self.usage_dir / f"{date}.json").read_text())

    def tree(self, *roots):
        out = set()
        for r in roots:
            for dp, _dn, fn in os.walk(r):
                for f in fn:
                    p = Path(dp) / f
                    out.add((str(p), p.stat().st_size))
        return out


def recompute(record):
    """Every total of the record, summed again from its rows."""
    def blank():
        return {"input": 0, "output": 0, "cache_read": 0, "cache_creation": 0, "cost_usd": 0.0}

    totals = {"by_repository": {}, "by_role": {}, "by_model": {}, "by_repository_role": {}}
    for row in record["rows"]:
        keys = {
            "by_repository": row["repository"],
            "by_role": row["role"],
            "by_model": row["model"],
            "by_repository_role": f"{row['repository']}|{row['role']}",
        }
        for kind, key in keys.items():
            t = totals[kind].setdefault(key, blank())
            for k in KINDS:
                t[k] += row[k]
            t["cost_usd"] += row["cost_usd"] or 0.0
    return totals


def assert_totals_match(record):
    want = recompute(record)
    got = record["totals"]
    for kind in want:
        assert set(got[kind]) == set(want[kind]), (kind, sorted(got[kind]), sorted(want[kind]))
        for key, w in want[kind].items():
            g = got[kind][key]
            for k in KINDS:
                assert g[k] == w[k], (kind, key, k, g[k], w[k])
            assert abs((g["cost_usd"] or 0.0) - w["cost_usd"]) < 1e-6, (kind, key, g["cost_usd"], w["cost_usd"])
