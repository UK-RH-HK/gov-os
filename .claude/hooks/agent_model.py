#!/usr/bin/env python3
"""The owner's model rule for helpers (audit 09 decision 2, 2026-11-18): every helper spawned with the Agent tool runs
the model the rubric gives helpers, Sonnet; any other model is refused unless the owner listed an exception in
governance/project/model-exceptions.yaml (`exceptions: [{subagent_type: <name or "*">, model: <model>, decided: <DEC or date>}]`).
A spawn that names no model takes CLAUDE_CODE_SUBAGENT_MODEL (claude-sonnet-5-5 in the user settings) and passes.
The CTO's own session (Opus) is not a helper and is not judged here. Exit 2 refuses; anything unreadable lets the
call through (the default model is Sonnet anyway)."""
import json
import os
import sys

ALLOWED = ("sonnet", "claude-sonnet-")


def allowed(model: str) -> bool:
    return model == "sonnet" or model.startswith("claude-sonnet-")


def exceptions(root: str) -> list:
    try:
        import yaml
        with open(os.path.join(root, "governance/project/model-exceptions.yaml"), encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return [e for e in data.get("exceptions", []) if isinstance(e, dict)]
    except Exception:
        return []


OPUS = ("opus", "claude-opus-5-5")
FABLE = ("fable", "claude-fable-5-2")


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


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0
    if event.get("tool_name") not in ("Agent", "Task"):
        return 0
    args = event.get("tool_input") or {}
    model = str(args.get("model") or "").strip()
    if not model or allowed(model):
        return 0
    kind = str(args.get("subagent_type") or "general-purpose")
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    sub = substitution(root)
    for e in exceptions(root):
        if e.get("subagent_type") not in (kind, "*"):
            continue
        if sub and e.get("model") in OPUS:  # DEC-1215: while the substitution is active, an Opus exception is Fable's
            if model in FABLE:
                return 0
            if model in OPUS:
                print(f"model rule (DEC-1215, the owner's temporary substitution until {sub}): every Opus role runs "
                      f"Claude Fable 5.2 instead; spawn '{kind}' with model 'fable'.", file=sys.stderr)
                return 2
        elif e.get("model") == model:
            return 0
    print(f"model rule (the owner's decision, 2026-11-18): a helper runs Sonnet; '{model}' for '{kind}' is refused. "
          f"Spawn it without a model (the default is Sonnet), or bring the owner one line asking for an exception "
          f"(governance/project/model-exceptions.yaml).", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
