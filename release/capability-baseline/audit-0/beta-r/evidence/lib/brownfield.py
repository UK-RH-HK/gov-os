"""P2-AR-0009 brownfield adoption driver (independent evidence harness).

Copies fixtures/brownfield/project, materialises its chat store as SQLite (as a real legacy repo would carry it) and
drives `gov adopt` stage by stage with the role/session separation the product requires.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from govprobe import Gov, commit_all, log, new_project, write

STAGES = ["A0", "A1", "A2", "A3", "A4", "A5", "A5R", "A6", "A6G", "A7", "A8", "A9", "A10", "A11"]


def prepare(name: str, extra_files: dict | None = None):
    root = new_project(name, fixture="brownfield", files=extra_files)
    sql = (root / "memory/chat_history.sql").read_text()
    con = sqlite3.connect(str(root / "memory/chat_history.sqlite"))
    con.executescript("PRAGMA journal_mode=DELETE;" + sql)
    con.close()
    (root / "memory/chat_history.sql").unlink()
    commit_all(root, "with chat db")
    return root


def roles(root: Path):
    planner = Gov(root, "S-planner")
    return {
        "planner": planner,
        "reviewer": Gov(root, "S-reviewer", "migration-reviewer"),
        "executor": Gov(root, "S-executor", "migration-executor"),
        "verifier": Gov(root, "S-verifier", "migration-verifier"),
        "memverifier": Gov(root, "S-memverifier", "memory-verifier"),
    }


def run_stages(root: Path, upto: str, show: bool = True, name: str = "shipping-quotes", alias: str = "fx-brown") -> dict:
    r = roles(root)
    out = {}
    for st in STAGES:
        if st == "A0":
            out[st] = r["planner"].ok("adopt", "baseline", show=show)
        elif st == "A1":
            out[st] = r["planner"].ok("adopt", "inventory", show=show)
        elif st == "A2":
            out[st] = r["planner"].ok("adopt", "classify", show=show)
        elif st == "A3":
            out[st] = r["planner"].ok("adopt", "map", show=show)
        elif st == "A4":
            out[st] = r["planner"].ok("adopt", "plan", show=show)
        elif st == "A5":
            out[st] = r["planner"].ok("adopt", "test-design", show=show)
        elif st == "A5R":
            out[st] = r["reviewer"].ok("adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED", show=show)
        elif st == "A6":
            out[st] = r["executor"].ok("adopt", "migrate", "--name", name, "--alias", alias, show=show)
        elif st == "A6G":
            cat = [json.loads(l) for l in (root / "spec/audits/GOVERNANCE-ADOPTION/04-TARGET-PATH-MAP.jsonl").read_text().splitlines()]
            gates = [e["human_gate"] for e in cat if e.get("requires_human_gate") and e.get("human_gate")]
            for gid in gates:
                r["executor"].ok("gate", "present", gid, show=show)
                r["executor"].ok("decide", gid, "--option", "A", "--by", "owner", show=show)
            out[st] = r["executor"].ok("adopt", "migrate", "--batch", "7", show=show) if gates else {}
        elif st == "A7":
            out[st] = r["verifier"].ok("adopt", "verify-migration", show=show)
        elif st == "A8":
            out[st] = r["executor"].ok("adopt", "extract-legacy", show=show)
        elif st == "A9":
            out[st] = r["executor"].ok("adopt", "build-memory", show=show)
        elif st == "A10":
            out[st] = r["memverifier"].ok("adopt", "verify-memory", show=show)
        elif st == "A11":
            out[st] = r["executor"].ok("adopt", "audit", show=show)
        if st == upto:
            break
    return out
