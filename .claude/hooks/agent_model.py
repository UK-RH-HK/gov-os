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
    for e in exceptions(root):
        if e.get("model") == model and e.get("subagent_type") in (kind, "*"):
            return 0
    print(f"model rule (the owner's decision, 2026-11-18): a helper runs Sonnet; '{model}' for '{kind}' is refused. "
          f"Spawn it without a model (the default is Sonnet), or bring the owner one line asking for an exception "
          f"(governance/project/model-exceptions.yaml).", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
