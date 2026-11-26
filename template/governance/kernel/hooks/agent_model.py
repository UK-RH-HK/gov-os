#!/usr/bin/env python3
"""The owner's model rule for helpers (audit 09 decision 2, 2026-11-18; DEC-1212 (2) and (4), DEC-1214 K1; W2-201):
every helper spawned with the Agent tool runs the model the rubric gives helpers, Sonnet. Judged in this order:

1. A fork (`subagent_type: fork`) is refused: helper work goes to a fresh helper from a written brief (DEC-1212 (4)).
   Only an entry for `subagent_type: fork` in the exceptions file lifts it.
2. A spawn that names no model gets "sonnet" written into it (PreToolUse `updatedInput`, every other key kept) and
   passes; a spawn that names Sonnet passes unchanged. The alias is written, never a full model id: the Agent tool's
   `model` accepts only `sonnet`, `opus`, `haiku` and `fable`, so a full id fails the spawn (AM-1). Only Sonnet is
   ever written, whatever the subagent type.
3. Fable (any model whose name has `fable`) is refused for every type: no session runs it (DEC-1225 (3)), and no entry
   covers it.
4. Any other model is refused unless governance/project/model-exceptions.yaml lists an exception for it
   (`exceptions: [{subagent_type: <name or "*">, model: <alias or id>, decided: <DEC or date>, class?, task?,
   decision?}]`). An entry that names Opus covers every Opus model. Three keys limit an entry, and every one it carries
   must be met (DEC-1225 (2)): `class: C3` (the spawn's ticket is C3: the prompt names it in a line `Task: <ticket id>`,
   and the class is computed from governance/project/criticality.yaml by the rule of
   gov.launch.criticality.ticket_criticality, the highest matching rule over `allowed_paths` and `profile`; the
   ticket's `class` key is never read), `task: <id or list>` (that `Task:` line names one of them) and
   `decision: <DEC-id or list>` (a line `Decision: <DEC-id>` names one of them). An entry that names Opus and carries
   none of the three lifts nothing.

The CTO's own session is not a helper and is not judged here. Exit 2 refuses, with the reason on stderr. Whatever
cannot be read (the exceptions file, the rubric, the ticket) refuses a spawn that names another model: unreadable
means Sonnet. An event that is not JSON, or for another tool, exits 0. Standalone: the standard library and yaml."""
import fnmatch
import json
import os
import re
import sys

try:  # the pin's gov package, when the kit's line starts the pin's interpreter; this file runs without it too
    import gov  # noqa: F401
except ImportError:
    pass

EXCEPTIONS_REL = "governance/project/model-exceptions.yaml"
CRITICALITY_REL = "governance/project/criticality.yaml"
CLASSES = ("C0", "C1", "C2", "C3")  # lowest first
TASK_LINE = re.compile(r"^Task: (DAEO-[a-z0-9]+)\s*$", re.MULTILINE)
DECISION_LINE = re.compile(r"^Decision: (DEC-[0-9]+)\s*$", re.MULTILINE)
LIMITERS = ("class", "task", "decision")


class Unreadable(Exception):
    """Something the judgement needs cannot be read; its text is the reason."""


def allowed(model: str) -> bool:
    return model == "sonnet" or model.startswith("claude-sonnet-")


def names_opus(model) -> bool:
    return isinstance(model, str) and (model == "opus" or model.startswith("claude-opus-"))


def names_fable(model) -> bool:
    return isinstance(model, str) and "fable" in model.lower()


def model_matches(entry_model, model: str) -> bool:
    """The rule of gov.launch.model_exceptions.model_matches: the same text, or Opus for Opus (alias or id); never
    Fable."""
    if names_fable(model):
        return False
    return entry_model == model or (names_opus(entry_model) and names_opus(model))


def as_list(value) -> list:
    """A `task` or `decision` given as one string is a list of one."""
    return list(value) if isinstance(value, (list, tuple)) else [value]


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


def _worktrees(root: str) -> list:
    """The repository's other worktrees (a lead writes its feature as a ticket on its own branch, so the ticket is in
    its worktree before it is in the project's own ``.tickets/``); none when git cannot say."""
    try:
        import subprocess
        out = subprocess.run(["git", "-C", root, "worktree", "list", "--porcelain"], capture_output=True, text=True,
                             timeout=10)
        if out.returncode != 0:
            return []
        here = os.path.realpath(root)
        paths = [line[len("worktree "):] for line in out.stdout.splitlines() if line.startswith("worktree ")]
        return [path for path in paths if os.path.realpath(path) != here]
    except Exception:
        return []


def ticket_front(root: str, ticket: str) -> dict:
    rel = f".tickets/{ticket}.md"
    try:
        import yaml
        path = os.path.join(root, rel)
        if not os.path.isfile(path):  # the project's own ticket wins; else the first worktree that holds it
            path = next((p for p in (os.path.join(tree, rel) for tree in _worktrees(root)) if os.path.isfile(p)), path)
        with open(path, encoding="utf-8") as f:
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


def write_model(args: dict) -> int:
    """A spawn that names no model gets the alias "sonnet" written into it (PreToolUse `updatedInput`, every other key
    kept), so its model no longer depends on an environment variable the harness may not read."""
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "updatedInput": {**args, "model": "sonnet"},
    }}))
    return 0


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
    if not model:
        return write_model(args)
    if allowed(model):
        return 0
    said = (f"model rule (the owner's decision, DEC-1225): a helper runs Sonnet; '{model}' for '{kind}' is refused")
    if names_fable(model):
        return refuse(f"{said}: no session runs Fable (DEC-1225 (3)), and no exception covers it. Spawn it without a "
                      f"model (the default is Sonnet).")
    try:
        entries = [e for e in exceptions(root) if e.get("subagent_type") in (kind, "*")
                   and model_matches(e.get("model"), model)]
        if not entries:
            return refuse(f"{said}. Spawn it without a model (the default is Sonnet), or bring the owner one line "
                          f"asking for an exception ({EXCEPTIONS_REL}).")
        prompt = args.get("prompt")
        prompt_text = prompt if isinstance(prompt, str) else ""
        ids = sorted(set(TASK_LINE.findall(prompt_text)))
        decisions = set(DECISION_LINE.findall(prompt_text))
        reasons = []
        who = "Opus" if names_opus(model) else repr(model)
        for entry in entries:
            missing = []
            if "class" in entry:
                if len(ids) != 1:
                    found = "none" if not ids else "more than one ticket: " + ", ".join(ids)
                    missing.append(f"class: {who} is for {entry['class']} work only, and the spawn's prompt "
                                   f"must name its ticket in one line 'Task: <ticket id>' (found {found}), so its class "
                                   f"cannot be read (unreadable means Sonnet)")
                else:
                    found = ticket_class(root, ticket_front(root, ids[0]))
                    if found != entry["class"]:
                        missing.append(f"class: {who} is for {entry['class']} work only, and the ticket "
                                       f"{ids[0]} is {found}")
            if "task" in entry:
                listed = [str(i) for i in as_list(entry["task"])]
                if len(ids) != 1 or ids[0] not in listed:
                    missing.append(f"task: the entry holds for {', '.join(listed)}, and the spawn's prompt must carry "
                                   f"one line 'Task: <ticket id>' naming one of them (found "
                                   f"{', '.join(ids) if ids else 'none'})")
            if "decision" in entry:
                listed = [str(i) for i in as_list(entry["decision"])]
                if not decisions & set(listed):
                    missing.append(f"decision: the entry holds for {', '.join(listed)}, and the spawn's prompt must "
                                   f"carry one line 'Decision: <DEC-id>' naming one of them (found "
                                   f"{', '.join(sorted(decisions)) if decisions else 'none'})")
            if not missing and names_opus(entry.get("model")) and not any(key in entry for key in LIMITERS):
                missing.append("limiter: an entry that names Opus carries a class, task or decision limiter, and "
                               "this one carries none, so it lifts nothing")
            if not missing:
                return 0
            reasons += missing
        return refuse(f"{said}: no exception in {EXCEPTIONS_REL} is met (DEC-1225 (2)); limiter not met: "
                      f"{'; '.join(reasons)}. Spawn it without a model (the default is Sonnet).")
    except Unreadable as error:
        return refuse(f"{said}: {error} (unreadable means Sonnet).")


def main() -> int:
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict) or event.get("tool_name") not in ("Agent", "Task"):
            return 0
        args = event.get("tool_input")
        if not isinstance(args, dict):
            return 0  # nothing to judge or to write into
        root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    except Exception:
        return 0
    try:
        return judge(args, root)
    except Exception as error:  # never a crash: what cannot be judged is refused, with the reason
        return refuse(f"model rule: the spawn cannot be judged ({type(error).__name__}: {error}); unreadable means "
                      f"Sonnet.")


if __name__ == "__main__":
    sys.exit(main())
