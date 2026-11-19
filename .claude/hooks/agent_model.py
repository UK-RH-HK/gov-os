#!/usr/bin/env python3
"""The owner's model rule for helpers (audit 09 decision 2, 2026-11-18; DEC-1212 (2) and (4), DEC-1214 K1; W2-201):
every helper spawned with the Agent tool runs the model the rubric gives helpers, Sonnet. Judged in this order:

1. A fork (`subagent_type: fork`) is refused: helper work goes to a fresh helper from a written brief (DEC-1212 (4)).
   Only an entry for `subagent_type: fork` in the exceptions file lifts it.
2. A spawn that names no model takes CLAUDE_CODE_SUBAGENT_MODEL (claude-sonnet-5-5 in the user settings) and passes;
   so does one that names Sonnet.
3. Any other model is refused unless governance/project/model-exceptions.yaml lists an exception for it
   (`exceptions: [{subagent_type: <name or "*">, model: <alias or id>, decided: <DEC or date>, class: C3?}]`). An entry
   that names Opus covers every Opus model. An entry with `class: C3` holds only for C3 work: the spawn's prompt names
   its ticket in a line `Task: <ticket id>`, and the ticket's class is computed from
   governance/project/criticality.yaml by the rule of gov.launch.criticality.ticket_criticality (the highest matching
   rule over `allowed_paths` and `profile`; the ticket's `class` key is never read).
4. While the owner's temporary substitution (governance/project/model-substitution.yaml, DEC-1215) is active, Fable
   is judged as Opus, and a spawn that names Opus is refused with the hint to name Fable.

The CTO's own session is not a helper and is not judged here. Exit 2 refuses, with the reason on stderr. Whatever
cannot be read (the exceptions file, the rubric, the ticket) refuses a spawn that names another model: unreadable
means Sonnet. An event that is not JSON, or for another tool, exits 0. Standalone: the standard library and yaml."""
import fnmatch
import json
import os
import re
import sys

EXCEPTIONS_REL = "governance/project/model-exceptions.yaml"
CRITICALITY_REL = "governance/project/criticality.yaml"
CLASSES = ("C0", "C1", "C2", "C3")  # lowest first
TASK_LINE = re.compile(r"^Task: (DAEO-[a-z0-9]+)\s*$", re.MULTILINE)
FABLE = ("fable", "claude-fable-5-2")


class Unreadable(Exception):
    """Something the judgement needs cannot be read; its text is the reason."""


def allowed(model: str) -> bool:
    return model == "sonnet" or model.startswith("claude-sonnet-")


def names_opus(model) -> bool:
    return isinstance(model, str) and (model == "opus" or model.startswith("claude-opus-"))


def model_matches(entry_model, model: str, substituted: bool) -> bool:
    """The rule of gov.launch.model_exceptions.model_matches: the same text, Opus for Opus (alias or id), and, while
    the substitution is active, Opus for Fable."""
    if entry_model == model:
        return True
    return names_opus(entry_model) and (names_opus(model) or (substituted and model in FABLE))


def _yaml(path: str, what: str):
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        raise Unreadable(f"{what} cannot be read or is not YAML") from None


def exceptions(root: str) -> list:
    data = _yaml(os.path.join(root, EXCEPTIONS_REL), EXCEPTIONS_REL)
    if not isinstance(data, dict) or not isinstance(data.get("exceptions"), list):
        raise Unreadable(f"{EXCEPTIONS_REL} is not a map with an 'exceptions' list")
    return [e for e in data["exceptions"] if isinstance(e, dict)]


def substitution(root: str) -> str:
    """The `until` of the owner's active temporary substitution (governance/project/model-substitution.yaml, DEC-1215)
    of Opus by Fable, or '' when there is none, it is inactive, unreadable or past its `until`."""
    try:
        import yaml
        from datetime import datetime, timezone
        with open(os.path.join(root, "governance/project/model-substitution.yaml"), encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not data.get("active") or data.get("to") != "claude-fable-5-2":
            return ""
        until = str(data.get("until") or "")
        if until and datetime.now(timezone.utc) >= datetime.fromisoformat(until):
            return ""
        return until or "revoked"
    except Exception:
        return ""


def _matches(glob: str, path: str) -> bool:
    return fnmatch.fnmatchcase(path, glob) or fnmatch.fnmatchcase(glob, path)


def ticket_class(root: str, front: dict) -> str:
    """The highest class among the rubric's rules that match the ticket's `allowed_paths` (a trailing `# comment`
    stripped) and `profile`; the rubric's `default` when none does."""
    data = _yaml(os.path.join(root, CRITICALITY_REL), CRITICALITY_REL)
    if not isinstance(data, dict) or data.get("default") not in CLASSES or not isinstance(data.get("rules"), list):
        raise Unreadable(f"{CRITICALITY_REL} is not a map with a default class and a list of rules")
    listed = front.get("allowed_paths")
    paths = [re.sub(r"\s+#.*$", "", p) for p in listed if isinstance(p, str)] if isinstance(listed, list) else []
    found = []
    for rule in data["rules"]:
        globs = rule.get("paths") if isinstance(rule, dict) else None
        if not isinstance(rule, dict) or rule.get("class") not in CLASSES or ("profile" in rule) == ("paths" in rule) \
                or ("paths" in rule and not (isinstance(globs, list) and all(isinstance(g, str) for g in globs))):
            raise Unreadable(f"{CRITICALITY_REL} holds a rule that is not of its form")
        if "profile" in rule:
            hit = front.get("profile") == rule["profile"]
        else:
            hit = any(_matches(glob, path) for glob in globs for path in paths)
        if hit:
            found.append(rule["class"])
    return max(found, key=CLASSES.index, default=data["default"])


def ticket_front(root: str, ticket: str) -> dict:
    rel = f".tickets/{ticket}.md"
    try:
        import yaml
        with open(os.path.join(root, rel), encoding="utf-8") as f:
            lines = f.read().splitlines()
        if not lines or lines[0].strip() != "---":
            raise ValueError
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
        front = yaml.safe_load("\n".join(lines[1:end]))
        if not isinstance(front, dict):
            raise ValueError
        return front
    except Exception:
        raise Unreadable(f"the ticket {ticket} cannot be read ({rel}, its front matter)") from None


def refuse(text: str) -> int:
    print(text, file=sys.stderr)
    return 2


def judge(args: dict, root: str) -> int:
    kind = str(args.get("subagent_type") or "general-purpose")
    model = str(args.get("model") or "").strip()
    if kind == "fork":
        try:
            lifted = any(e.get("subagent_type") == "fork" for e in exceptions(root))
        except Unreadable:
            lifted = False
        if not lifted:
            return refuse("helper rule (the owner's decision, DEC-1212 (4)): no fork for helper work; spawn a fresh "
                          "helper from a written brief (a named subagent type and a brief that stands alone). Only "
                          f"an entry for 'fork' in {EXCEPTIONS_REL} lifts this.")
    if not model or allowed(model):
        return 0
    sonnet = (f"model rule (the owner's decision, 2026-11-18): a helper runs Sonnet; '{model}' for '{kind}' is "
              f"refused")
    try:
        sub = substitution(root)
        entries = [e for e in exceptions(root) if e.get("subagent_type") in (kind, "*")
                   and model_matches(e.get("model"), model, bool(sub))]
        if not entries:
            return refuse(f"{sonnet}. Spawn it without a model (the default is Sonnet), or bring the owner one line "
                          f"asking for an exception ({EXCEPTIONS_REL}).")
        if sub and names_opus(model):  # DEC-1215: while the substitution is active, an Opus exception is Fable's
            return refuse(f"model rule (DEC-1215, the owner's temporary substitution until {sub}): every Opus role "
                          f"runs Claude Fable 5.2 instead; spawn '{kind}' with model 'fable'.")
        if any("class" not in e for e in entries):
            return 0
        needed = sorted({str(e["class"]) for e in entries})
        prompt = args.get("prompt")
        ids = sorted(set(TASK_LINE.findall(prompt if isinstance(prompt, str) else "")))
        if len(ids) != 1:
            found = "none" if not ids else "more than one ticket: " + ", ".join(ids)
            return refuse(f"{sonnet}: Opus is for {', '.join(needed)} work only, and the spawn's prompt must name "
                          f"its ticket in one line 'Task: <ticket id>' (found {found}), so its class cannot be read "
                          f"(unreadable means Sonnet).")
        found = ticket_class(root, ticket_front(root, ids[0]))
        if found in needed:
            return 0
        return refuse(f"{sonnet}: the ticket {ids[0]} is {found}, and Opus is for {', '.join(needed)} work only "
                      f"(DEC-1214 K1). Spawn it without a model (the default is Sonnet).")
    except Unreadable as error:
        return refuse(f"{sonnet}: {error} (unreadable means Sonnet).")


def main() -> int:
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict) or event.get("tool_name") not in ("Agent", "Task"):
            return 0
        args = event.get("tool_input")
        root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    except Exception:
        return 0
    try:
        return judge(args if isinstance(args, dict) else {}, root)
    except Exception as error:  # never a crash: what cannot be judged is refused, with the reason
        return refuse(f"model rule: the spawn cannot be judged ({type(error).__name__}: {error}); unreadable means "
                      f"Sonnet.")


if __name__ == "__main__":
    sys.exit(main())
