"""Read Claude Code transcripts as data, build one day's rows and totals, write or print them (W2-207)."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

PRICES = Path("governance/project/usage-prices.yaml")
LOG = Path(".gov-runtime/scratch/orchestrator/log")
FIELDS = ("input", "output", "cache_read", "cache_creation")
USAGE_KEYS = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")


class UsageError(Exception):
    pass


def now() -> datetime:
    text = os.environ.get("GOV_USAGE_NOW")
    if text:
        try:
            stamp = datetime.fromisoformat(text.replace("Z", "+00:00"))
            return stamp if stamp.tzinfo else stamp.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def parse_day(text) -> str:
    if not text:
        return now().astimezone(timezone.utc).strftime("%Y-%m-%d")
    try:
        return datetime.strptime(text, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        raise UsageError(f"--date is a day as YYYY-MM-DD, not {text!r}") from None


def home() -> Path:
    return Path(os.environ.get("HOME") or Path.home())


def record_path(day: str) -> Path:
    return home() / ".gov-os" / "usage" / f"{day}.json"


def load_prices(root: Path) -> dict:
    path = root / PRICES
    if not path.is_file():
        raise UsageError(f"the price table {PRICES} is missing under {root}")
    try:
        import yaml
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        models = data["models"] if isinstance(data, dict) and isinstance(data.get("models"), dict) else data
        table = {str(k): {f: float(v[f]) for f in FIELDS} for k, v in models.items() if isinstance(v, dict) and all(f in v for f in FIELDS)}
    except Exception as exc:  # a table that cannot be read is named, never guessed
        raise UsageError(f"the price table {PRICES} cannot be read: {exc}") from None
    return {"date": str(data.get("date", "")) if isinstance(data, dict) else "", "models": table}


def _repository(cwd: str, cache: dict) -> str:
    if cwd in cache:
        return cache[cwd]
    result = cwd
    if cwd and Path(cwd).is_dir():
        try:
            out = subprocess.run(["git", "-C", cwd, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                 capture_output=True, text=True, timeout=10)
            common = Path(out.stdout.strip())
            if out.returncode == 0 and common.name == ".git":
                result = str(common.parent)
        except Exception:
            pass
    cache[cwd] = result
    return result


def _meta(path: Path) -> dict:
    try:
        data = json.loads(path.with_name(path.name[:-len(".jsonl")] + ".meta.json").read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _launch_role(cwd: str, repo: str, sid: str):
    for base in dict.fromkeys((cwd, repo)):
        if not base:
            continue
        try:
            data = json.loads((Path(base) / ".gov-runtime" / "launches" / f"{sid}.json").read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("role"), str) and data["role"]:
                return data["role"]
        except Exception:
            continue
    return None


def _cto_ids(root: Path) -> set:
    try:
        return set((root / LOG / "cto-session.txt").read_text(encoding="utf-8", errors="replace").split())
    except Exception:
        return set()


def _day_of(stamp) -> str:
    try:
        return datetime.fromisoformat(str(stamp).replace("Z", "+00:00")).astimezone(timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return ""


def _files(day: str):
    base = home() / ".claude" / "projects"
    start = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()
    found = []
    for pattern in ("*/*.jsonl", "*/*/subagents/agent-*.jsonl"):
        for path in base.glob(pattern):
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            if mtime >= start or start > datetime.now(timezone.utc).timestamp():  # last written before the day starts: it cannot hold that day's messages
                found.append((mtime, str(path), path))
    return [p for _, _, p in sorted(found)]


def _int(value) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else 0


def collect(root: Path, day: str):
    """(rows without cost, skipped line count)."""
    cache: dict = {}
    seen: dict = {}      # (repo, session, message id) -> (model, tokens, helper meta role)
    skipped = 0
    nousage: set = set()  # a usage-less assistant line repeated in a resumed file counts once
    for path in _files(day):
        helper = path.parent.name == "subagents"
        meta = _meta(path) if helper else {}
        try:
            handle = open(path, encoding="utf-8", errors="replace")
        except OSError:
            continue
        with handle:
            for n, line in enumerate(handle):
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except ValueError:
                    skipped += 1
                    continue
                if not isinstance(obj, dict):
                    skipped += 1
                    continue
                if obj.get("type") != "assistant":
                    continue
                message = obj.get("message") if isinstance(obj.get("message"), dict) else {}
                usage = message.get("usage")
                stamp = _day_of(obj.get("timestamp"))
                if not isinstance(usage, dict):
                    if stamp in ("", day):
                        key = (obj.get("cwd"), obj.get("sessionId") or path.stem, message.get("id") or obj.get("uuid") or (str(path), n))
                        if key not in nousage:
                            nousage.add(key)
                            skipped += 1
                    continue
                if stamp != day:
                    continue
                cwd = obj.get("cwd") if isinstance(obj.get("cwd"), str) else ""
                repo = _repository(cwd, cache)
                if helper:
                    session = f"{path.parent.parent.name}/{path.stem}"
                else:
                    session = str(obj.get("sessionId") or path.stem)
                mid = message.get("id") or obj.get("uuid") or f"{path}:{n}"
                tokens = [_int(usage.get(k)) for k in USAGE_KEYS]
                seen[(repo, session, mid)] = (str(message.get("model") or "unknown"), tokens, cwd,
                                              meta.get("agentType") if helper else None, helper)
    cto = _cto_ids(root)
    groups: dict = {}
    for (repo, session, _), (model, tokens, cwd, agent, helper) in seen.items():
        row = groups.get((repo, session, model))
        if row is None:
            role = None if helper else _launch_role(cwd, repo, session)
            source = "launch record"
            if role is None and isinstance(agent, str) and agent:
                role, source = agent, "helper meta"
            if role is None and session in cto:
                role, source = "cto", "cto-session.txt"
            if role is None:
                role, source = "unknown", "unknown (no launch record, helper meta or cto-session.txt names a role)"
            row = groups[(repo, session, model)] = {
                "repository": repo, "session": session, "role": role, "role_source": source, "model": model,
                "input": 0, "output": 0, "cache_read": 0, "cache_creation": 0,
                "context_peak": 0}
        row["input"] += tokens[0]
        row["output"] += tokens[1]
        row["cache_read"] += tokens[2]
        row["cache_creation"] += tokens[3]
        row["context_peak"] = max(row["context_peak"], tokens[0] + tokens[2] + tokens[3])
    return sorted(groups.values(), key=lambda r: (r["repository"], r["session"], r["model"])), skipped


def _cost(row: dict, prices: dict):
    price = prices["models"].get(row["model"])
    if price is None:
        return None
    counts = (row["input"], row["output"], row["cache_read"], row["cache_creation"])
    return sum(c * price[f] for c, f in zip(counts, FIELDS)) / 1_000_000


def _sum_by(rows, key) -> dict:
    out: dict = {}
    for row in rows:
        name = key(row)
        t = out.setdefault(name, {"input": 0, "output": 0, "cache_read": 0,
                                  "cache_creation": 0, "cost_usd": 0.0, "sessions": 0})
        for k in ("input", "output", "cache_read", "cache_creation"):
            t[k] += row[k]
        t["cost_usd"] += row["cost_usd"] or 0.0
        t["sessions"] += 1
    for t in out.values():
        t["cost_usd"] = round(t["cost_usd"], 6)
    return out


def plan_reading(root: Path, day: str) -> str:
    last = None
    try:
        with open(root / LOG / "usage.txt", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if line.startswith(day):
                    last = line.rstrip("\n")
    except OSError:
        pass
    if last is None:
        return "unread"
    parts = last.split(" ", 2)
    return parts[2].strip() if len(parts) == 3 and parts[2].strip() else "unread"


def build(root: Path, day: str) -> dict:
    prices = load_prices(root)
    rows, skipped = collect(root, day)
    unpriced = sorted({r["model"] for r in rows if r["model"] not in prices["models"]})
    for row in rows:
        cost = _cost(row, prices)
        row["cost_usd"] = None if cost is None else round(cost, 6)
    return {
        "date": day, "timezone": "UTC", "price_table": {"path": str(PRICES), "date": prices["date"],
                                     "note": "dollars are a list-price estimate"},
        "rows": rows, "unpriced_models": unpriced, "skipped_lines": skipped,
        "totals": {
            "by_repository": _sum_by(rows, lambda r: r["repository"]),
            "by_role": _sum_by(rows, lambda r: r["role"]),
            "by_model": _sum_by(rows, lambda r: r["model"]),
            "by_repository_role": _sum_by(rows, lambda r: f"{r['repository']}|{r['role']}"),
            "all": _sum_by(rows, lambda r: "all").get("all", {}),
        },
        "plan_reading": plan_reading(root, day),
    }


def write_daily(root: Path, day: str):
    rec = build(root, day)
    path = record_path(day)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return path, rec


def _day_record(root: Path, day: str) -> dict:
    return build(root, day)


def show_lines(root: Path, day: str, days: int) -> list:
    last = datetime.strptime(day, "%Y-%m-%d")
    lines = []
    if days > 1:
        for back in range(days - 1, -1, -1):
            d = (last - timedelta(days=back)).strftime("%Y-%m-%d")
            rec = _day_record(root, d)
            repos = rec["totals"]["by_repository"]
            if not repos:
                lines.append(f"{d} no usage; plan: {rec['plan_reading']}")
            all_cost = rec["totals"]["all"].get("cost_usd", 0.0)
            for repo, t in sorted(repos.items(), key=lambda kv: -kv[1]["cost_usd"]):
                share = (100.0 * t["cost_usd"] / all_cost) if all_cost else 0.0
                lines.append(f"{d} {repo} ${t['cost_usd']:.2f} {share:.0f}% list-price estimate; plan: {rec['plan_reading']}")
        return lines
    rec = _day_record(root, day)
    total = rec["totals"]["all"].get("cost_usd", 0.0) if rec["rows"] else 0.0
    lines.append(f"usage {day}: ${total:.2f} list-price estimate in all; plan: {rec['plan_reading']}")
    for repo, t in sorted(rec["totals"]["by_repository"].items(), key=lambda kv: -kv[1]["cost_usd"]):
        share = (100.0 * t["cost_usd"] / total) if total else 0.0
        roles: dict = {}
        mine = [r for r in rec["rows"] if r["repository"] == repo]
        for r in mine:
            roles[r["role"]] = roles.get(r["role"], 0.0) + (r["cost_usd"] or 0.0)
        top = ", ".join(f"{k} ${v:.2f}" for k, v in sorted(roles.items(), key=lambda kv: -kv[1])[:3])
        sess: dict = {}
        for r in mine:
            sess[r["session"]] = sess.get(r["session"], 0.0) + (r["cost_usd"] or 0.0)
        big = max(sess.items(), key=lambda kv: kv[1])
        lines.append(f"{repo}: ${t['cost_usd']:.2f} ({share:.0f}% of the day); top roles: {top}; "
                     f"largest session: {big[0]} ${big[1]:.2f}; plan: {rec['plan_reading']}")
    if rec["unpriced_models"]:
        lines.append("unpriced models: " + ", ".join(rec["unpriced_models"]))
    return lines
