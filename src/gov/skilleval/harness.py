"""The skill evaluation harness behind ``gov skilleval`` (W2-104, DEC-959 item 5, DEC-820 (a)).

A skill's folder holds ``SKILL.md`` (front matter with ``name`` and ``version``) and ``scenarios.md``: three
scenarios, each ``## <n>. <title>`` with the bullets ``Situation``, ``Expected`` and ``Pass line`` (W2-11's form).
Each scenario runs as two new ``claude -p`` processes, each in its own temporary folder outside the project:

- the session, whose folder's ``.claude/skills/`` holds only the evaluated skill (no ``scenarios.md``, no record),
  is given the Situation;
- the judgement, in an empty folder, is given the Pass line, the Expected text and the session's reply, and ends
  with ``VERDICT: PASS`` or ``VERDICT: FAIL``.

A verdict is ``pass`` only when both ran and the judgement's last verdict line says PASS; ``fail`` when it says
FAIL or has none; ``not-run`` with a one-line cause when a process could not be run or did not answer. The harness
passes its environment through to ``claude`` and reads no secret itself: no key file is opened, and neither the
environment nor a child's standard error or output text reaches the records or the envelope.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

from gov.cli.errors import GovError

DEFAULT_MODEL, DEFAULT_EFFORT = "claude-opus-5-5", "high"  # DEC-839's worker defaults, until roles state their own
SCENARIOS, RECORD = "scenarios.md", "scenario-records.yaml"
SUMMARIES = "scenario-summaries.md"  # hand-written beside them (W2-100's and W2-101's interface); never shown to the session
IMPORTS = "governance/project/skill-imports.yaml"
# Keeps the session to its folder's own settings and skills: no user settings or skills, no MCP servers, no saved
# session (claude --help). --bare is not used: it would refuse the program's own sign-in.
ISOLATION = ("--setting-sources", "project", "--strict-mcp-config", "--no-session-persistence")
FIELDS = {"Situation": "situation", "Expected": "expected", "Pass line": "pass_line"}
HEADING = re.compile(r"^## (\d+)\.\s+(\S.*?)\s*$")
BULLET = re.compile(r"^- \*\*(Situation|Expected|Pass line):\*\*\s*(.*)$")
VERDICT = re.compile(r"^VERDICT: (PASS|FAIL)$")
ADOPT_FIELDS = ("source", "version", "licence")

SESSION_PROMPT = """You have one skill, "{name}", installed in this folder's .claude/skills/. Use it as it directs.

Situation:
{situation}

Act on this situation as the skill directs, and report what you did and what you produced."""

JUDGE_PROMPT = """You judge whether a session's reply meets a scenario's pass line. Judge only from the reply below.

Pass line:
{pass_line}

Expected behaviour:
{expected}

The session's reply:
<<<
{reply}
>>>

Give your reasons briefly, then end with one last line, exactly "VERDICT: PASS" if the pass line holds, or
"VERDICT: FAIL" if it does not or cannot be told from the reply."""


class NotRun(Exception):
    """A model process that could not be run or did not answer; its message is the cause, never its output."""


def _unevaluable(skill_dir: Path, message: str) -> GovError:
    return GovError("SKILL_NOT_EVALUABLE", f"{message}; nothing was run or recorded", {"skill": str(skill_dir)},
                    exit_code=5)


def _front_matter(text: str) -> dict:
    end = text.find("\n---", 3)
    if not text.startswith("---") or end < 0:
        return {}
    try:
        front = yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        return {}
    return front if isinstance(front, dict) else {}


def parse_scenarios(text: str) -> list[dict]:
    """The scenarios of a ``scenarios.md``, in order; each with ``n``, ``title`` and the three bullets' text."""
    scenarios, field = [], None
    for line in text.splitlines():
        heading, bullet = HEADING.match(line), BULLET.match(line)
        if heading:
            scenarios.append({"n": int(heading.group(1)), "title": heading.group(2)})
            field = None
        elif line.startswith("#"):
            field = None
        elif bullet and scenarios:
            field = FIELDS[bullet.group(1)]
            scenarios[-1][field] = bullet.group(2).strip()
        elif field and line[:1].isspace() and line.strip():
            scenarios[-1][field] = f"{scenarios[-1][field]} {line.strip()}".strip()
        else:
            field = None
    return scenarios


def load_skill(skill_dir: Path) -> tuple[str, str, list[dict]]:
    """The skill's name, version and three complete scenarios; exit code 5 when it cannot be evaluated."""
    if not (skill_dir / "SKILL.md").is_file():
        raise _unevaluable(skill_dir, "the skill has no SKILL.md")
    front = _front_matter((skill_dir / "SKILL.md").read_text(encoding="utf-8"))
    name, version = front.get("name"), front.get("version")
    if not name or version is None or not str(version).strip():
        raise _unevaluable(skill_dir, "SKILL.md's front matter has no name or no version")
    if not (skill_dir / SCENARIOS).is_file():
        raise _unevaluable(skill_dir, f"the skill has no {SCENARIOS}")
    scenarios = parse_scenarios((skill_dir / SCENARIOS).read_text(encoding="utf-8"))
    complete = [s["n"] for s in scenarios if all(s.get(key) for key in FIELDS.values())]
    if [s["n"] for s in scenarios] != [1, 2, 3] or complete != [1, 2, 3]:
        raise _unevaluable(skill_dir, f"{SCENARIOS} does not hold exactly three complete scenarios, 1 to 3")
    return str(name), str(version), scenarios


def ask(step: str, prompt: str, cwd: str, model: str, effort: str, timeout: float) -> tuple[str, float]:
    """One new ``claude -p`` process: its reply and cost, or ``NotRun`` with a one-line cause."""
    program = shutil.which("claude")
    if program is None:
        raise NotRun(f"{step}: no claude on the PATH")
    command = [program, "-p", "--model", model, "--effort", effort, "--output-format", "json", *ISOLATION]
    try:
        done = subprocess.run(command, input=prompt, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", cwd=cwd, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise NotRun(f"{step}: timed out after {timeout:g} seconds") from None
    except OSError:
        raise NotRun(f"{step}: claude could not be started") from None
    if done.returncode != 0:
        raise NotRun(f"{step}: claude exited with code {done.returncode}")
    try:
        answer = json.loads(done.stdout)
    except ValueError:
        answer = None
    answer = answer if isinstance(answer, dict) else {}
    cost = answer.get("total_cost_usd")
    if not (isinstance(answer.get("result"), str) and isinstance(answer.get("is_error"), bool)
            and isinstance(cost, (int, float)) and not isinstance(cost, bool)):
        raise NotRun(f"{step}: claude's output is not the expected JSON object")
    if answer["is_error"]:
        raise NotRun(f"{step}: claude reported an error (is_error)")
    return answer["result"], float(cost)


def judge_verdict(reply: str) -> tuple[str, str | None]:
    """The verdict read from the judgement's reply: its last line ``VERDICT: PASS`` or ``VERDICT: FAIL``."""
    found = [m.group(1) for m in (VERDICT.match(line.strip()) for line in reply.splitlines()) if m]
    if not found:
        return "fail", "the judgement gave no verdict line"
    return ("pass", None) if found[-1] == "PASS" else ("fail", "judged FAIL against the pass line")


def run_scenario(skill_dir: Path, name: str, scenario: dict, model: str, effort: str, timeout: float) -> dict:
    start = time.monotonic()
    try:
        with tempfile.TemporaryDirectory(prefix="gov-skilleval-session-") as folder:
            shutil.copytree(skill_dir, Path(folder, ".claude", "skills", skill_dir.name),
                            ignore=shutil.ignore_patterns(SCENARIOS, RECORD, SUMMARIES))
            prompt = SESSION_PROMPT.format(name=name, situation=scenario["situation"])
            reply, cost = ask("session", prompt, folder, model, effort, timeout)
        with tempfile.TemporaryDirectory(prefix="gov-skilleval-judge-") as folder:
            prompt = JUDGE_PROMPT.format(pass_line=scenario["pass_line"], expected=scenario["expected"], reply=reply)
            judged, judge_cost = ask("judgement", prompt, folder, model, effort, timeout)
        verdict, cause = judge_verdict(judged)
        cost_usd = round(cost + judge_cost, 6)
    except NotRun as why:
        verdict, cause, cost_usd = "not-run", str(why), None
    return {"scenario": scenario["n"], "title": scenario["title"], "verdict": verdict, "cause": cause,
            "cost_usd": cost_usd, "seconds": round(time.monotonic() - start, 3)}


def _yaml_map(path: Path, key: str) -> dict | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    return data if isinstance(data, dict) and isinstance(data.get(key), list) else None


def _header(text: str) -> str:
    """The leading comment lines of a YAML file, kept when the file is written again."""
    lines = []
    for line in text.splitlines(keepends=True):
        if line.strip() and not line.lstrip().startswith("#"):
            break
        lines.append(line)
    return "".join(lines)


def _refusal(entries: list[dict], all_passed: bool) -> str | None:
    if len(entries) != 1:
        return f"{IMPORTS} has {'no' if not entries else 'more than one'} entry for this skill"
    missing = [key for key in ADOPT_FIELDS if entries[0].get(key) is None or not str(entries[0][key]).strip()]
    if missing:
        return f"the import entry records no {', '.join(missing)}"
    if entries[0].get("licence_verdict") != "allowed":
        return "the import entry's licence_verdict is not 'allowed'"
    return None if all_passed else "not all three scenarios passed in this run"


def adopt(root: Path, name: str, version: str, all_passed: bool, run_at: str) -> str | None:
    """Marks the skill's import entry adopted; returns the reason when adoption is refused (the entry then false)."""
    path = root / IMPORTS
    data = _yaml_map(path, "imports") if path.is_file() else None
    if data is None:
        return f"{IMPORTS} is missing or is not a map with an imports list"
    entries = [entry for entry in data["imports"] if isinstance(entry, dict) and entry.get("name") == name]
    reason = _refusal(entries, all_passed)
    for entry in entries:
        entry.pop("adopted_version", None)
        entry.pop("adopted_at", None)
        entry["adopted"] = reason is None
        if reason is None:
            entry.update(adopted_version=version, adopted_at=run_at)
    if entries:
        text = path.read_text(encoding="utf-8")
        path.write_text(_header(text) + yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return reason


def evaluate(root: Path, skill: str, adopt_import: bool = False, model: str | None = None,
             effort: str | None = None, timeout: float = 900.0):
    skill_dir = Path(skill) if Path(skill).is_absolute() else Path(root) / skill
    skill_dir = skill_dir.resolve()
    name, version, scenarios = load_skill(skill_dir)
    record = skill_dir / RECORD
    records = {"records": []}
    if record.exists() and (records := _yaml_map(record, "records")) is None:
        raise GovError("RECORD_INVALID", f"{RECORD} is not a map with a records list; nothing was run",
                       {"record": str(record)})
    model, effort = model or DEFAULT_MODEL, effort or DEFAULT_EFFORT
    results = []
    for scenario in scenarios:
        run_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        results.append(run_scenario(skill_dir, name, scenario, model, effort, timeout))
        records["records"].append({"skill": name, "skill_version": version, **results[-1], "model": model,
                                   "effort": effort, "run_at": run_at})
    record.write_text(yaml.safe_dump(records, sort_keys=False, allow_unicode=True), encoding="utf-8")
    result = {"skill": name, "skill_version": version, "scenarios": results, "record": str(record), "adopted": None}
    verdicts = {r["verdict"] for r in results}
    if adopt_import:
        reason = adopt(Path(root), name, version, verdicts == {"pass"}, run_at)
        result["adopted"] = reason is None
        return (dict(result, reason=reason), 6) if reason else result
    code = 3 if "fail" in verdicts else 4 if "not-run" in verdicts else 0
    return (result, code) if code else result
