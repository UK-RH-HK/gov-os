# Lead brief: agent-model-alias, the model hook writes an alias the Agent tool accepts (a stopper for release 0.1.8; a fix under W2-201, DAEO-k1us)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-26. **Read `docs/emergency-2/briefs/LEAD-COMMON.md`
first: every rule there applies, with one exception for this lead only:** spawn every helper with `model: "sonnet"` given explicitly
(the hook you fix is live in Gov OS's settings and breaks a spawn that names no model). Decide, never ask (I-10). Use
`systematic-debugging`. Every `gov retrieve` takes `--root /home/usain/gov-os-worktrees/W2-00-store`. **Small and fast: 0.1.8 is held for it.**

## Why (proven by the CTO in the real path)
`.claude/hooks/agent_model.py` (byte-equal to the kit's `template/governance/kernel/hooks/agent_model.py`, both from batch A at
`84e60c40e`) writes the role table's model into a spawn that names none (`write_model`, `:187-193`, through `table_model` `:168-176` and
`_own_table_model` `:159-164`). For a role-typed spawn (`subagent_type: engineer`) it writes the full id `claude-sonnet-5-5`; for
`general-purpose` the alias `sonnet`. Claude Code's Agent tool accepts only `sonnet`, `opus`, `haiku`, `fable`: the CTO's real spawn of
`subagent_type: engineer` with no model failed with "PreToolUse hook for Agent returned updatedInput that failed schema validation ...
expected one of sonnet|opus|haiku|fable". Every lead spawns its test designer and engineer with no model (LEAD-COMMON), so every lead's
flow breaks, in Gov OS now and in every repository that takes 0.1.8.

## What (a `## Fix:` line in `.tickets/DAEO-k1us.md`)
- **AM-1** The hook's `updatedInput.model` is always one of the Agent tool's aliases: a role table entry given as a full id is written
  as its family's alias (`claude-sonnet-*` -> `sonnet`; and so for opus, haiku, fable if the table ever names them), for every role and
  for `general-purpose`; the refusal rules (`allowed`, `names_opus`, `names_fable`, `model_matches`) keep reading both forms. Failing test
  first: a unit case per role-table entry asserting the written model is in the alias set, red today for `engineer`. The two copies stay
  byte-equal (find the test that pins that and keep it green).
- **Prove it in the real path:** in a scratch clone with the fixed hook in its `.claude/hooks/` and its settings, one real Agent spawn of
  `subagent_type: engineer` with no model, from a `claude -p` session started in that clone (Sonnet, a one-line prompt that asks for
  `PROBE OK`), succeeds; record the command and the output.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-agent-model-alias`, branch `e2/agent-model-alias` from `w2/integrate`. Code area: the two hook
copies, `tests/unit/hooks/` (or wherever the hook's unit tests live), `tests/acceptance/W2-201/` or `W2-208/` only through the independent
test designer if an acceptance case pins the full id, `.tickets/DAEO-k1us.md`. Never merge into `w2/integrate`.

## Green
AM-1 red then green; the hook's unit tests and W2-201's and W2-208's model cases green; the real-path proof; then exactly the
impact-selected suites (`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-k1us=e2/agent-model-alias --onto w2/integrate
--select`) through the heavy slot. Check the trailers (LEAD-COMMON).

## Return
Branch and head; the fix (file:line); the tests; the real-path proof; the selected run's summary; your retrieves. Under 300 words.

## Your memory bundle (DEC-1249 (1); profile: code locations, conventions, earlier fixes and findings; uncut)
store: a2214ad4b865 (/home/usain/gov-os-worktrees/W2-00-store-a)
{
  "store": {
    "commit": "a2214ad4b86595567fcd1e4b9c7cb8a64bbf26e8",
    "head": "a2214ad4b86595567fcd1e4b9c7cb8a64bbf26e8",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-a"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "e31f703efed76e049c8f3823",
      "sha256": "7aa9cd4f73f9cef0d7166858009ae68c9e9f1526dcfbcf9fedc634973af82870",
      "path": "template/governance/kernel/hooks/agent_model.py",
      "start_line": 187,
      "end_line": 195,
      "text": "def write_model(args: dict, root: str = \"\") -> int:\n    \"\"\"A spawn that names no model gets a Sonnet model written into it (PreToolUse `updatedInput`, every other key\n    kept), so its model no longer depends on an environment variable the harness may not read.\"\"\"\n    print(json.dumps({\"hookSpecificOutput\": {\n        \"hookEventName\": \"PreToolUse\",\n        \"permissionDecision\": \"allow\",\n        \"updatedInput\": {**args, \"model\": table_model(root, str(args.get(\"subagent_type\") or \"general-purpose\"))},\n    }}))\n    return 0\n",
      "chunk_id": "e31f703efed76e049c8f3823",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "e4ba6764e0979fd665612170",
      "sha256": "7aa9cd4f73f9cef0d7166858009ae68c9e9f1526dcfbcf9fedc634973af82870",
      "path": ".claude/hooks/agent_model.py",
      "start_line": 187,
      "end_line": 195,
      "text": "def write_model(args: dict, root: str = \"\") -> int:\n    \"\"\"A spawn that names no model gets a Sonnet model written into it (PreToolUse `updatedInput`, every other key\n    kept), so its model no longer depends on an environment variable the harness may not read.\"\"\"\n    print(json.dumps({\"hookSpecificOutput\": {\n        \"hookEventName\": \"PreToolUse\",\n        \"permissionDecision\": \"allow\",\n        \"updatedInput\": {**args, \"model\": table_model(root, str(args.get(\"subagent_type\") or \"general-purpose\"))},\n    }}))\n    return 0\n",
      "chunk_id": "e4ba6764e0979fd665612170",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "9859af771995221cbea8bf9a",
      "sha256": "af0df07dda60b3574f4495fc2958fee02bcb81f886421cefbad66af3016f960a",
      "path": "template/governance/kernel/hooks/agent_model.py",
      "start_line": 1,
      "end_line": 286,
      "text": "#!/usr/bin/env python3\n\"\"\"The owner's model rule for helpers (audit 09 decision 2, 2026-11-18; DEC-1212 (2) and (4), DEC-1214 K1; W2-201):\nevery helper spawned with the Agent tool runs the model the rubric gives helpers, Sonnet. Judged in this order:\n\n1. A fork (`subagent_type: fork`) is refused: helper work goes to a fresh helper from a written brief (DEC-1212 (4)).\n   Only an entry for `subagent_type: fork` in the exceptions file lifts it.\n2. A spawn that names no model gets a model written into it (PreToolUse `updatedInput`, every other key kept) and\n   passes: the model of the row for its subagent type in governance/project/role-table.yaml when the row exists and\n   is a Sonnet model, else \"sonnet\" (an unreadable table, no row or another model mean \"sonnet\"); a spawn that names\n   Sonnet passes unchanged.\n3. Fable (any model whose name has `fable`) is refused for every type: no session runs it (DEC-1225 (3)), and no entry\n   covers it.\n4. Any other model is refused unless governance/project/model-exceptions.yaml lists an exception for it\n   (`exceptions: [{subagent_type: <name or \"*\">, model: <alias or id>, decided: <DEC or date>, class?, task?,\n   decision?}]`). An entry that names Opus covers every Opus model. Three keys limit an entry, and every one it carries\n   must be met (DEC-1225 (2)): `class: C3` (the spawn's ticket is C3: the prompt names it in a line `Task: <ticket id>`,\n   and the class is computed from governance/project/criticality.yaml by the rule of\n   gov.launch.criticality.ticket_criticality, the highest matching rule over `allowed_paths` and `profile`; the\n   ticket's `class` key is never read), `task: <id or list>` (that `Task:` line names one of them) and\n   `decision: <DEC-id or list>` (a line `Decision: <DEC-id>` names one of them). An entry that names Opus and carries\n   none of the three lifts nothing.\n\nThe CTO's own session is not a helper and is not judged here. Exit 2 refuses, with the reason on stderr. Whatever\ncannot be read (the exceptions file, the rubric, the ticket) refuses a spawn that names another model: unreadable\nmeans Sonnet. An event that is not JSON, or for another tool, exits 0. Standalone: the standard library and yaml.\"\"\"\nimport fnmatch\nimport json\nimport os\nimport re\nimport sys\n\ntry:  # the pin's gov package, when the kit's line starts the pin's interpreter; this file runs without it too\n    import gov  # noqa: F401\nexcept ImportError:\n    pass\n\nEXCEPTIONS_REL = \"governance/project/model-exceptions.yaml\"\nCRITICALITY_REL = \"governance/project/criticality.yaml\"\nTABLE_REL = \"governance/project/role-table.yaml\"\nCLASSES = (\"C0\", \"C1\", \"C2\", \"C3\")  # lowest first\nTASK_LINE = re.compile(r\"^Task: (DAEO-[a-z0-9]+)\\s*$\", re.MULTILINE)\nDECISION_LINE = re.compile(r\"^Decision: (DEC-[0-9]+)\\s*$\", re.MULTILINE)\nLIMITERS = (\"class\", \"task\", \"decision\")\n\n\nclass Unreadable(Exception):\n    \"\"\"Something the judgement needs cannot be read; its text is the reason.\"\"\"\n\n\ndef allowed(model: str) -> bool:\n    return model == \"sonnet\" or model.startswith(\"claude-sonnet-\")\n\n\ndef names_opus(model) -> bool:\n    return isinstance(model, str) and (model == \"opus\" or model.startswith(\"claude-opus-\"))\n\n\ndef names_fable(model) -> bool:\n    return isinstance(model, str) and \"fable\" in model.lower()\n\n\ndef model_matches(entry_model, model: str) -> bool:\n    \"\"\"The rule of gov.launch.model_exceptions.model_matches: the same text, or Opus for Opus (alias or id); never\n    Fable.\"\"\"\n    if names_fable(model):\n        return False\n    return entry_model == model or (names_opus(entry_model) and names_opus(model))\n\n\ndef as_list(value) -> list:\n    \"\"\"A `task` or `decision` given as one string is a list of one.\"\"\"\n    return list(value) if isinstance(value, (list, tuple)) else [value]\n\n\ndef _yaml(path: str, what: str):\n    try:\n        import yaml\n        with open(path, encoding=\"utf-8\") as f:\n            return yaml.safe_load(f)\n    except Exception:\n        raise Unreadable(f\"{what} cannot be read or is not YAML\") from None\n\n\ndef exceptions(root: str) -> list:\n    data = _yaml(os.path.join(root, EXCEPTIONS_REL), EXCEPTIONS_REL)\n    if not isinstance(data, dict) or not isinstance(data.get(\"exceptions\"), list):\n        raise Unreadable(f\"{EXCEPTIONS_REL} is not a map with an 'exceptions' list\")\n    return [e for e in data[\"exceptions\"] if isinstance(e, dict)]\n\n\ndef _matches(glob: str, path: str) -> bool:\n    return fnmatch.fnmatchcase(path, glob) or fnmatch.fnmatchcase(glob, path)\n\n\ndef ticket_class(root: str, front: dict) -> str:\n    \"\"\"The highest class among the rubric's rules that match the ticket's `allowed_paths` (a trailing `# comment`\n    stripped) and `profile`; the rubric's `default` when none does.\"\"\"\n    data = _yaml(os.path.join(root, CRITICALITY_REL), CRITICALITY_REL)\n    if not isinstance(data, dict) or data.get(\"default\") not in CLASSES or not isinstance(data.get(\"rules\"), list):\n        raise Unreadable(f\"{CRITICALITY_REL} is not a map with a default class and a list of rules\")\n    listed = front.get(\"allowed_paths\")\n    paths = [re.sub(r\"\\s+#.*$\", \"\", p) for p in listed if isinstance(p, str)] if isinstance(listed, list) else []\n    found = []\n    for rule in data[\"rules\"]:\n        globs = rule.get(\"paths\") if isinstance(rule, dict) else None\n        if not isinstance(rule, dict) or rule.get(\"class\") not in CLASSES or (\"profile\" in rule) == (\"paths\" in rule) \\\n                or (\"paths\" in rule and not (isinstance(globs, list) and all(isinstance(g, str) for g in globs))):\n            raise Unreadable(f\"{CRITICALITY_REL} holds a rule that is not of its form\")\n        if \"profile\" in rule:\n            hit = front.get(\"profile\") == rule[\"profile\"]\n        else:\n            hit = any(_matches(glob, path) for glob in globs for path in paths)\n        if hit:\n            found.append(rule[\"class\"])\n    return max(found, key=CLASSES.index, default=data[\"default\"])\n\n\ndef _worktrees(root: str) -> list:\n    \"\"\"The repository's other worktrees (a lead writes its feature as a ticket on its own branch, so the ticket is in\n    its worktree before it is in the project's own ``.tickets/``); none when git cannot say.\"\"\"\n    try:\n        import subprocess\n        out = subprocess.run([\"git\", \"-C\", root, \"worktree\", \"list\", \"--porcelain\"], capture_output=True, text=True,\n                             timeout=10)\n        if out.returncode != 0:\n            return []\n        here = os.path.realpath(root)\n        paths = [line[len(\"worktree \"):] for line in out.stdout.splitlines() if line.startswith(\"worktree \")]\n        return [path for path in paths if os.path.realpath(path) != here]\n    except Exception:\n        return []\n\n\ndef ticket_front(root: str, ticket: str) -> dict:\n    rel = f\".tickets/{ticket}.md\"\n    try:\n        import yaml\n        path = os.path.join(root, rel)\n        if not os.path.isfile(path):  # the project's own ticket wins; else the first worktree that holds it\n            path = next((p for p in (os.path.join(tree, rel) for tree in _worktrees(root)) if os.path.isfile(p)), path)\n        with open(path, encoding=\"utf-8\") as f:\n            lines = f.read().splitlines()\n        if not lines or lines[0].strip() != \"---\":\n            raise ValueError\n        end = next(i for i in range(1, len(lines)) if lines[i].strip() == \"---\")\n        front = yaml.safe_load(\"\\n\".join(lines[1:end]))\n        if not isinstance(front, dict):\n            raise ValueError\n        return front\n    except Exception:\n        raise Unreadable(f\"the ticket {ticket} cannot be read ({rel}, its front matter)\") from None\n\n\ndef refuse(text: str) -> int:\n    print(text, file=sys.stderr)\n    return 2\n\n\ndef _own_table_model(root: str, kind: str) -> str:\n    data = _yaml(os.path.join(root, TABLE_REL), TABLE_REL)\n    for row in data[\"rows\"]:\n        if row[\"role\"] == kind:\n            model = row[\"model\"]\n            return model if isinstance(model, str) and model.startswith(\"claude-sonnet-\") else \"sonnet\"\n    return \"sonnet\"\n\n\ndef table_model(root: str, kind: str) -> str:\n    \"\"\"The model of the role table's row for ``kind`` when the row exists and is Sonnet; else \"sonnet\" (the table\n    unreadable, no row, or a row of another model). Read through the pinned gov package's reader when the interpreter\n    has it (the kit's hook line starts the pin's interpreter), else by the same rule here, so the hook runs alone.\"\"\"\n    try:\n        from gov.launch import role_table\n        row = role_table.row_for(root, kind)\n        model = row[\"model\"] if row else None\n        return model if isinstance(model, str) and model.startswith(\"claude-sonnet-\") else \"sonnet\"\n    except ImportError:\n        pass\n    except Exception:\n        return \"sonnet\"\n    try:\n        return _own_table_model(root, kind)\n    except Exception:\n        return \"sonnet\"\n\n\ndef write_model(args: dict, root: str = \"\") -> int:\n    \"\"\"A spawn that names no model gets a Sonnet model written into it (PreToolUse `updatedInput`, every other key\n    kept), so its model no longer depends on an environment variable the harness may not read.\"\"\"\n    print(json.dumps({\"hookSpecificOutput\": {\n        \"hookEventName\": \"PreToolUse\",\n        \"permissionDecision\": \"allow\",\n        \"updatedInput\": {**args, \"model\": table_model(root, str(args.get(\"subagent_type\") or \"general-purpose\"))},\n    }}))\n    return 0\n\n\ndef judge(args: dict, root: str) -> int:\n    kind = str(args.get(\"subagent_type\") or \"general-purpose\")\n    model = str(args.get(\"model\") or \"\").strip()\n    if kind == \"fork\":\n        try:\n            lifted = any(e.get(\"subagent_type\") == \"fork\" for e in exceptions(root))\n        except Unreadable:\n            lifted = False\n        if not lifted:\n            return refuse(\"helper rule (the owner's decision, DEC-1212 (4)): no fork for helper work; spawn a fresh \"\n                          \"helper from a written brief (a named subagent type and a brief that stands alone). Only \"\n                          f\"an entry for 'fork' in {EXCEPTIONS_REL} lifts this.\")\n    if not model:\n        return write_model(args, root)\n    if allowed(model):\n        return 0\n    said = (f\"model rule (the owner's decision, DEC-1225): a helper runs Sonnet; '{model}' for '{kind}' is refused\")\n    if names_fable(model):\n        return refuse(f\"{said}: no session runs Fable (DEC-1225 (3)), and no exception covers it. Spawn it without a \"\n                      f\"model (the default is Sonnet).\")\n    try:\n        entries = [e for e in exceptions(root) if e.get(\"subagent_type\") in (kind, \"*\")\n                   and model_matches(e.get(\"model\"), model)]\n        if not entries:\n            return refuse(f\"{said}. Spawn it without a model (the default is Sonnet), or bring the owner one line \"\n                          f\"asking for an exception ({EXCEPTIONS_REL}).\")\n        prompt = args.get(\"prompt\")\n        prompt_text = prompt if isinstance(prompt, str) else \"\"\n        ids = sorted(set(TASK_LINE.findall(prompt_text)))\n        decisions = set(DECISION_LINE.findall(prompt_text))\n        reasons = []\n        who = \"Opus\" if names_opus(model) else repr(model)\n        for entry in entries:\n            missing = []\n            if \"class\" in entry:\n                if len(ids) != 1:\n                    found = \"none\" if not ids else \"more than one ticket: \" + \", \".join(ids)\n                    missing.append(f\"class: {who} is for {entry['class']} work only, and the spawn's prompt \"\n                                   f\"must name its ticket in one line 'Task: <ticket id>' (found {found}), so its class \"\n                                   f\"cannot be read (unreadable means Sonnet)\")\n                else:\n                    found = ticket_class(root, ticket_front(root, ids[0]))\n                    if found != entry[\"class\"]:\n                        missing.append(f\"class: {who} is for {entry['class']} work only, and the ticket \"\n                                       f\"{ids[0]} is {found}\")\n            if \"task\" in entry:\n                listed = [str(i) for i in as_list(entry[\"task\"])]\n                if len(ids) != 1 or ids[0] not in listed:\n                    missing.append(f\"task: the entry holds for {', '.join(listed)}, and the spawn's prompt must carry \"\n                                   f\"one line 'Task: <ticket id>' naming one of them (found \"\n                                   f\"{', '.join(ids) if ids else 'none'})\")\n            if \"decision\" in entry:\n                listed = [str(i) for i in as_list(entry[\"decision\"])]\n                if not decisions & set(listed):\n                    missing.append(f\"decision: the entry holds for {', '.join(listed)}, and the spawn's prompt must \"\n                                   f\"carry one line 'Decision: <DEC-id>' naming one of them (found \"\n                                   f\"{', '.join(sorted(decisions)) if decisions else 'none'})\")\n            if not missing and names_opus(entry.get(\"model\")) and not any(key in entry for key in LIMITERS):\n                missing.append(\"limiter: an entry that names Opus carries a class, task or decision limiter, and \"\n                               \"this one carries none, so it lifts nothing\")\n            if not missing:\n                return 0\n            reasons += missing\n        return refuse(f\"{said}: no exception in {EXCEPTIONS_REL} is met (DEC-1225 (2)); limiter not met: \"\n                      f\"{'; '.join(reasons)}. Spawn it without a model (the default is Sonnet).\")\n    except Unreadable as error:\n        return refuse(f\"{said}: {error} (unreadable means Sonnet).\")\n\n\ndef main() -> int:\n    try:\n        event = json.load(sys.stdin)\n        if not isinstance(event, dict) or event.get(\"tool_name\") not in (\"Agent\", \"Task\"):\n            return 0\n        args = event.get(\"tool_input\")\n        if not isinstance(args, dict):\n            return 0  # nothing to judge or to write into\n        root = os.environ.get(\"CLAUDE_PROJECT_DIR\") or os.getcwd()\n    except Exception:\n        return 0\n    try:\n        return judge(args, root)\n    except Exception as error:  # never a crash: what cannot be judged is refused, with the reason\n        return refuse(f\"model rule: the spawn cannot be judged ({type(error).__name__}: {error}); unreadable means \"\n                      f\"Sonnet.\")\n\n\nif __name__ == \"__main__\":\n    sys.exit(main())\n",
      "chunk_id": "9859af771995221cbea8bf9a",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "19ee7bea26f819ec7f905bf1",
      "sha256": "116758387bb86bf8eabae1975f8a7dbb1582e9b94294112c9692b7fa0713e65f",
      "path": ".claude/hooks/agent_model.py",
      "start_line": 1,
      "end_line": 14,
      "text": "#!/usr/bin/env python3\n\"\"\"The owner's model rule for helpers (audit 09 decision 2, 2026-11-18; DEC-1212 (2) and (4), DEC-1214 K1; W2-201):\nevery helper spawned with the Agent tool runs the model the rubric gives helpers, Sonnet. Judged in this order:\n\n1. A fork (`subagent_type: fork`) is refused: helper work goes to a fresh helper from a written brief (DEC-1212 (4)).\n   Only an entry for `subagent_type: fork` in the exceptions file lifts it.\n2. A spawn that names no model gets a model written into it (PreToolUse `updatedInput`, every other key kept) and\n   passes: the model of the row for its subagent type in governance/project/role-table.yaml when the row exists and\n   is a Sonnet model, else \"sonnet\" (an unreadable table, no row or another model mean \"sonnet\"); a spawn that names\n   Sonnet passes unchanged.\n3. Fable (any model whose name has `fable`) is refused for every type: no session runs it (DEC-1225 (3)), and no entry\n   covers it.\n4. Any other model is refused unless governance/project/model-exceptions.yaml lists an exception for it\n   (`exceptions: [{subagent_type: <name or \"*\">, model: <alias or id>, decided: <DEC or date>, class?, task?,\n",
      "chunk_id": "19ee7bea26f819ec7f905bf1",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "6f117f87dd7562abceb052bc",
      "sha256": "82b92bcdb8123e16b7c1d2e5097600d804fcb7c8e2c0a63149b3cf05e8d00145",
      "path": "docs/emergency-2/briefs/LEAD-fixes-015a.md",
      "start_line": 34,
      "end_line": 44,
      "text": "  `stop_hook_active` (exit 0 when set). Verify: a planted return with the value on the next line passes once; with\n  `stop_hook_active` true the hook exits 0. Owner: W1-29.\n\n- **F13 Every helper runs Sonnet, whatever its agent type** (DEC-1225, the owner's priority 1): on 2026-11-22 audit 1's\n  four `Explore` helpers (the built-in type, no `model` named) ran **Opus** although `CLAUDE_CODE_SUBAGENT_MODEL` named\n  Sonnet (`.gov-runtime/scratch/orchestrator/log/usage-breakdown-2026-11-22.md`, audit 1's helpers); general-purpose and\n  role helpers ran Sonnet. `.claude/hooks/agent_model.py` passes a spawn that names no model on the assumption the\n  default applies. Make the hook write the model into the spawn: a PreToolUse hook may return `updatedInput`; every\n  Agent spawn that names no model gets `model: \"sonnet\"` (and an Opus spawn the exceptions file lets through keeps its\n  model), so no built-in or plugin agent type can run its own or its parent's model. The kit's copy of the hook does the\n  same (EXAMIN gets it by `gov update`). Verify: planted spawns of `Explore`, `Plan`, `general-purpose` and a role type\n",
      "chunk_id": "6f117f87dd7562abceb052bc",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-k1us",
      "sha256": "2b607412e23cb27d2578d03561bde83332307bce2fa5ba8c6330f9a867e742eb",
      "path": ".tickets/DAEO-k1us.md",
      "start_line": 334,
      "end_line": 334,
      "text": "Found 2026-11-22: a spawn that named no model relied on CLAUDE_CODE_SUBAGENT_MODEL, which the harness does not always read, so such a helper could run the session's model. No test caught it. Required: `.claude/hooks/agent_model.py` writes model `sonnet` into every Agent spawn that names no model, through PreToolUse `updatedInput` with the full input kept; an Opus spawn the exceptions file allows keeps its model; Fable stays refused; no kit copy of the hook exists and none is added. Kind: a fix, no new ticket; the ticket stays closed. Failing test first: `tests/acceptance/W2-201/test_w2_201_fix_f13_model_written.py` (15 cases); code `.claude/hooks/agent_model.py` (`write_model`; a non-object `tool_input` is left alone); units `tests/unit/hooks/test_w2_201_agent_model.py` (`written`, the no-model cases for Agent and Task). Result: the 15 cases and the units are green. Four older acceptance files of this ticket still assert that a no-model spawn prints nothing (`test_w2_201_f1_hook_unreadable.py`, `test_w2_201_s5_hook_class.py` cases `*-no-model`, `test_w2_201_s6_hook_fork.py::..[no-model]`: 11 cases) and are red against the line this fix states: they need the test designer's revision (the builder never edits them).\n",
      "chunk_id": "960eec3d60ecfbb7a168fb59",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-k1us",
      "sha256": "9fc27028b87ff07cbd7dd361dcf3735627daf5da42d70bae75e1c4f330c57a32",
      "path": ".tickets/DAEO-k1us.md",
      "start_line": 88,
      "end_line": 100,
      "text": "## Interface\n\n- **Role files.** The values of S1. The generated copies (`.rulesync/subagents`, `template/.rulesync/subagents`,\n  `.claude/agents`) change with the kernel file wherever a copy check holds them equal (W1-28, W1-33, W2-153 S3).\n- **`governance/project/criticality.yaml`.** The rules of S2 in the file form `gov.launch.criticality` already reads\n  (`version`, `default`, `opus`, `rules`); no new key.\n- **`governance/project/model-exceptions.yaml`.** `exceptions: [{subagent_type, model, decided, class?}]`; `class` is\n  optional and, when `C3`, limits the entry to C3 tickets. `model` is an alias (`opus`) or a model id; `opus` matches\n  every `claude-opus-*`. One reader rule for the launcher and the hook (the hook stays standalone: `python3 -I`,\n  stdlib and yaml only; a test holds the two equal).\n- **The hook** (`.claude/hooks/agent_model.py`): the order is fork, then model. Ticket found from the spawn prompt line\n  `^Task: (DAEO-[a-z0-9]+)\\s*$` (every such line; all the same id, else unreadable). Class by the same rule as\n  `ticket_criticality`. Exit 2 with the reason on stderr; any other outcome exit 0.\n",
      "chunk_id": "1d2651892431f0512406812d",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "76fca833c069cbe72ce34b9a",
      "sha256": "f0661cc2fd08c27e6ba3372dcd9e5028b4b3a1a3a2d2745bd16b0c86c0c71f5e",
      "path": "docs/emergency-2/briefs/LEAD-models-by-role.md",
      "start_line": 15,
      "end_line": 20,
      "text": "- **4-2** the kit complete: `agent_model.py` and its hook line in the kit (`template/.rulesync/hooks.jsonc`), reading the same table; `defaultMode: bypassPermissions` in the kit's settings; the root `permissions.jsonc` aligned with the two live deny lines (git push, sudo). EXAMIN runs an older 2,124-byte hook copy that `gov update` must replace. Owner: W2-208 (`.tickets/DAEO-kt8e.md`, closed: a fix). Beware I-16 (`docs/emergency-2/integration/FINDINGS.md`): `gov adapters generate` duplicated the governance head in hand-written CLAUDE.md and AGENTS.md; do not run it on Gov OS's own tree; check `.claude/settings.json` after any generation in a scratch repository.\n\nKernel text you may change for these items (the CTO approves it by naming it here): the role files' model and effort lines under `template/governance/kernel/roles/` (they read the table instead of restating it, values unchanged), the kit's hooks and settings files.\n\nCode area (stream B): `src/gov/launch/`, `.claude/hooks/agent_model.py`, `template/`, `governance/project/` configuration for the table. Stay out of `src/gov/dispatch/`, `src/gov/resources/`, `src/gov/rebuild*`, `src/gov/decisions/` (other leads).\n\n",
      "chunk_id": "76fca833c069cbe72ce34b9a",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "6f77c5acae014d21ad478c30",
      "sha256": "86ed7dd8f5a062aab8a6c17a0b87cf6d5449bcb1c85eba082234898f65903a97",
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "start_line": 261,
      "end_line": 262,
      "text": "| Helper hook | `.claude/hooks/agent_model.py` (218 lines); `governance/project/model-exceptions.yaml` | every Agent spawn naming a model other than Sonnet is refused (Opus by an entry only; Fable and `fork` refused) | a spawn that names **no model** passes, so built-in types such as `Explore` ran Opus (F13); the one auditor Opus entry has no limiter |\n| Criticality | `governance/project/criticality.yaml` (rules C3 to C1, default C2, `opus:`); `launch/criticality.py` | computes a ticket's class from `allowed_paths` and `profile`; read by the hook (`class: C3` entries, none left) and by `gov launch` (table lookup, promotion and probe use `opus:`) | with the table gone from the role files (R1) the class no longer changes any model or effort except promotion and probe |\n",
      "chunk_id": "6f77c5acae014d21ad478c30",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-kt8e",
      "sha256": "bf69821c3792acb67f389fc96afc0157620891e05564d973e1123d2137e20f20",
      "path": ".tickets/DAEO-kt8e.md",
      "start_line": 110,
      "end_line": 118,
      "text": "## Fix: the kit holds the model hook, the table and `defaultMode`; the root permission source matches the live deny lines (MR-4; INTEGRATION-PLAN row 4-2; A-27; lead `models-by-role`, 2026-11-24)\n\nFound by the integration plan: EXAMIN runs an older copy of the helper hook and the kit ships none, `defaultMode` is not in the kit's settings, and the root\n`.rulesync/permissions.jsonc` spells the deny lines differently from the two live ones. Required; the ticket stays closed. I-16\n(`gov adapters generate` duplicates the head in hand-written CLAUDE.md and AGENTS.md) is not touched: generation is only run in a scratch repository.\n\n**MR-4 The kit complete (4-2).** The kit holds `.claude/hooks/agent_model.py` (`template/.claude/hooks/agent_model.py`, byte-equal to Gov OS's own, which reads\n`governance/project/role-table.yaml` by the same rule as the launcher: a spawn of a helper naming a model other than Sonnet is refused, a spawn with no model has Sonnet written\nin, unreadable means Sonnet), its hook line `PreToolUse`, matcher `Agent|Task`, in `template/.rulesync/hooks.jsonc` (`python3 -I \"$CLAUDE_PROJECT_DIR/.claude/hooks/agent_model.py\"`), the\n",
      "chunk_id": "cf4a79f7b9d410a806b59311",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    }
  ],
  "batches": [
    {
      "size": 10
    },
    {
      "size": 10
    }
  ],
  "merge": {
    "candidates": 20,
    "duplicates": 18,
    "dropped": [],
    "reranked": true
  },
  "rerank": {
    "by": "service",
    "device": "cuda:0",
    "reason": null
  },
  "expansions": [
    {
      "chunk_id": "9859af771995221cbea8bf9a",
      "parent_id": "e96d7b075133646738f38548",
      "path": "template/governance/kernel/hooks/agent_model.py",
      "start_line": 1,
      "end_line": 286
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "path": "template/governance/kernel/hooks/agent_model.py",
      "chunk_id": "715f6bb15517b274514acc0e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/agent_model.py",
      "chunk_id": "8d28938f7363fffe0d247ce4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/agent_model.py",
      "chunk_id": "1c5015813d7073a6df76e03d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/agent_model.py",
      "chunk_id": "99de8fce4c0b14cb0b6d9f55",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/agent_model.py",
      "chunk_id": "9b1049108fef37c949ebd4ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/agent_model.py",
      "chunk_id": "3a5e7d089af58da90e538d42",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "a0336fa412a8efc51912bd41",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".claude/hooks/agent_model.py",
      "chunk_id": "46e5f01b0d2cdcb2f360e9b4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/agent_model.py",
      "chunk_id": "492b0e44ed3b0d35d0916404",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adapters/merge.py",
      "chunk_id": "ba362ecf896b6b15659a1377",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-models-by-role.md",
      "chunk_id": "6e48d9709caa00cba11b0799",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "be3a00bfac74afd5d24ecd54",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/agent_model.py",
      "chunk_id": "e22d7ea78717c15f95c29304",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "2d0834518a58c49388bc387d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "fc3695df132559428d51d6af",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/agent_model.py",
      "chunk_id": "fd74f60c8f56f3a5385f63bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".claude/hooks/agent_model.py",
      "chunk_id": "cf41e21dbeb3700fdd9c09b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/agent_model.py",
      "chunk_id": "b740a73aaa87e7e77d6279c6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "ab1c2bb56768d84db3a7c785",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/agent_model.py",
      "chunk_id": "27231d19d845616c7820953b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "a9411e5d9f44eb8c6ea18591",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/agent_model.py",
      "chunk_id": "a976d331fd5a08bf075ca8b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/agent_model.py",
      "chunk_id": "d5c8862090e1b46a85de5cfe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "66e9d709731040d21356c0b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/agent_model.py",
      "chunk_id": "faf3b2f7f8a7054c63eed3a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".claude/hooks/agent_model.py",
      "chunk_id": "9d74f90c1f9d0d3042f72c55",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MODEL-TIERS-1.md",
      "chunk_id": "b3315b74f65190057b83f281",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".claude/hooks/agent_model.py",
      "chunk_id": "7f76911e3c6248c476e4bbd8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "f5c44f4f1dd2c2be22eb79d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-153-evidence.md",
      "chunk_id": "a8b466eea2056931e493c44d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "39a843ca4bfe1c55b6a68f1a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/agent_model.py",
      "chunk_id": "6aecf20dbe81e4ef5921f82d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "8accb601bdaf2bd096d623a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".claude/hooks/agent_model.py",
      "chunk_id": "03589531f398135889aa1fe3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-60a-CIT-E.md",
      "chunk_id": "ba1e2e06b023697206170075",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_fix_f13_model_written.py",
      "chunk_id": "eb80c9a9d41725de91eda852",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "0b4c13cff7d5baf1def34a60",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".claude/hooks/agent_model.py",
      "chunk_id": "642d72763dd1e5e12f9fa533",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MODEL-TIERS-1.md",
      "chunk_id": "c0470b0eeb417debbda875a7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "451ec92885b7a1e1fa816602",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/hooks/test_mr4_agent_model_table.py",
      "chunk_id": "5311f2acc51bce4f148016fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-153-evidence.md",
      "chunk_id": "1134b3b786da78395fa242e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/agent_model.py",
      "chunk_id": "df4b1cc35760f8d582c3b047",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/w2_201_support.py",
      "chunk_id": "7254d1561e066921de8b62ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/MODELS-BY-ROLE-DISAGREEMENTS.md",
      "chunk_id": "036bd936c5eb09868a182561",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MODEL-TIERS-1.md",
      "chunk_id": "d88f879d7f48e42f48604ebf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".claude/hooks/agent_model.py",
      "chunk_id": "5aab2e494755752b6a3f3b84",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "16737f5af51525c00b585bcc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MODEL-TIERS-1.md",
      "chunk_id": "da19134768c849b862a5e466",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".claude/hooks/agent_model.py",
      "chunk_id": "220c5bede9d45df363280adf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md",
      "chunk_id": "5ed68689dfd8041ecc94d82d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "b7da75d422fa0cd258206c8d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/role_table.py",
      "chunk_id": "87110f0913cc294a20ecb2a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".claude/hooks/agent_model.py",
      "chunk_id": "f3db2dc76f91be30399b129c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-153-evidence.md",
      "chunk_id": "13fd51092aaac48f7f80905a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/hooks/test_w2_201_agent_model.py",
      "chunk_id": "e8d014da31ebd0557741acaf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/E-roles-context.md",
      "chunk_id": "8024c93309a50d53d0acdc98",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MODEL-TIERS-1.md",
      "chunk_id": "1c6fa93940c0d371f845c7e5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "73d89519458258100d3b0bc0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "bafc0a0c0909e4ddb4435417",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-208/test_w2_208_mr4_kit.py",
      "chunk_id": "5d23e24afa7c8d909dd7e7c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-3ef2.md",
      "chunk_id": "412cbbfa98ba2cb00edce855",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.8/TOOL-STATUS-DRAFT.md",
      "chunk_id": "70c0425edd206e8eb7faaee0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/agent_model.py",
      "chunk_id": "091f3a9cf19b411bf31324e1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-lrre.md",
      "chunk_id": "825a342b6f63654a7650f9fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ecac.md",
      "chunk_id": "9941a60603e7d9b65e8ab0dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "4630835b459f7cb0b76dd1a7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-models-rubric.md",
      "chunk_id": "20b90ac07cdd6dd0178a0f78",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md",
      "chunk_id": "3ad2076fce811fdfa94fd6e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MODEL-TIERS-1.md",
      "chunk_id": "f486de23f64fc4ee85142392",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "4630286e8cfdb1b9d139cae5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/role-table.yaml",
      "chunk_id": "867e206985d2df6d9952a261",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "06a6739c1d58e412ec741660",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/agent_model.py",
      "chunk_id": "97db74baa9df8e8c81d4575f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-lrre.md",
      "chunk_id": "48574190edac75c95dbdfa39",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-models-rubric.md",
      "chunk_id": "fc424c02846a7c2251723923",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-lrre.md",
      "chunk_id": "fd95bc44c09e00458fd60c98",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "4ff89cef2f02eccb83ab83ff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cv58.md",
      "chunk_id": "a34d222c0792b404b0d738c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cv58.md",
      "chunk_id": "faafc4c32d6089b19fc0565d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adapters/portability.py",
      "chunk_id": "e159256105aae68a57ceb839",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-60a-CIT-E.md",
      "chunk_id": "ebb27c73dd8106c3e57171bc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/w2_201_support.py",
      "chunk_id": "df6978783e67c49c453f3a25",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/w2_201_support.py",
      "chunk_id": "6861a44c5ed49f597476e5de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_s6_hook_fork.py",
      "chunk_id": "d966296b22309106c060d8df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "ea0966ad609befd50104f5ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_s1_role_files.py",
      "chunk_id": "02f65afac3bd4d656535d5a4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_s5_hook_class.py",
      "chunk_id": "56aa481b4e854a581e3ae37a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/F-models-context.md",
      "chunk_id": "977b6f42af57042c30639827",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/E-roles-context.md",
      "chunk_id": "a679629669b5808b1a11f4fb",
      "reason": "NOT_GATHERED"
    }
  ],
  "facets": {
    "lexical": {
      "available": true,
      "reason": null
    },
    "semantic": {
      "available": true,
      "reason": null
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5996
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIuY2xhdWRlL2hvb2tzL2FnZW50X21vZGVsLnB5IiwxLDE0LCIxOWVlN2JlYTI2ZjgxOWVjN2Y5MDViZjEiXSxbIi5jbGF1ZGUvaG9va3MvYWdlbnRfbW9kZWwucHkiLDE4NywxOTUsImU0YmE2NzY0ZTA5NzlmZDY2NTYxMjE3MCJdLFsiLnRpY2tldHMvREFFTy1rMXVzLm1kIiw4OCwxMDAsIjFkMjY1MTg5MjQzMWYwNTEyNDA2ODEyZCJdLFsiLnRpY2tldHMvREFFTy1rMXVzLm1kIiwzMzQsMzM0LCI5NjBlZWMzZDYwZWNmYmI3YTE2OGZiNTkiXSxbIi50aWNrZXRzL0RBRU8ta3Q4ZS5tZCIsMTEwLDExOCwiY2Y0YTc5ZjdiOWQ0MTBhODA2YjU5MzExIl0sWyJkb2NzL2VtZXJnZW5jeS0yL2JyaWVmcy9MRUFELWZpeGVzLTAxNWEubWQiLDM0LDQ0LCI2ZjExN2Y4N2RkNzU2MmFiY2ViMDUyYmMiXSxbImRvY3MvZW1lcmdlbmN5LTIvYnJpZWZzL0xFQUQtbW9kZWxzLWJ5LXJvbGUubWQiLDE1LDIwLCI3NmZjYTgzM2MwNjljYmU3MmNlMzRiOWEiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vREVDSVNJT05TLUhFTEQubWQiLDI2MSwyNjIsIjZmNzdjNWFjYWUwMTRkMjFhZDQ3OGMzMCJdLFsidGVtcGxhdGUvZ292ZXJuYW5jZS9rZXJuZWwvaG9va3MvYWdlbnRfbW9kZWwucHkiLDY4LDY5LCIxZThkM2ZiNjg5MjY1OTNhMjU4OGZjYWUiXSxbInRlbXBsYXRlL2dvdmVybmFuY2Uva2VybmVsL2hvb2tzL2FnZW50X21vZGVsLnB5Iiw3Myw3NCwiMmFlOGVkNjY0YTg5MGZjZWVkMjAyZDcwIl0sWyJ0ZW1wbGF0ZS9nb3Zlcm5hbmNlL2tlcm5lbC9ob29rcy9hZ2VudF9tb2RlbC5weSIsODIsODMsIjFhNzExYmE2ZDFhMTk4M2E3YjJiYWYwYSJdLFsidGVtcGxhdGUvZ292ZXJuYW5jZS9rZXJuZWwvaG9va3MvYWdlbnRfbW9kZWwucHkiLDg5LDkwLCIzNTE4Y2I4Y2IwMWQ2ZGJiNTU1MGUwZjIiXSxbInRlbXBsYXRlL2dvdmVybmFuY2Uva2VybmVsL2hvb2tzL2FnZW50X21vZGVsLnB5IiwxMzIsMTMzLCI2NzZlNDczMDFhYzg5ZGI0NTQyNzVkYjYiXSxbInRlbXBsYXRlL2dvdmVybmFuY2Uva2VybmVsL2hvb2tzL2FnZW50X21vZGVsLnB5IiwxNTIsMTUzLCIzOTAwYmI4OWRmOTVkNWFkYjUzMzU0NDYiXSxbInRlbXBsYXRlL2dvdmVybmFuY2Uva2VybmVsL2hvb2tzL2FnZW50X21vZGVsLnB5IiwxNTcsMTU4LCI0YzY0ZTQyOWQ0MmExZTc0NWJmNWNhYWIiXSxbInRlbXBsYXRlL2dvdmVybmFuY2Uva2VybmVsL2hvb2tzL2FnZW50X21vZGVsLnB5IiwxNjgsMTg0LCI1MDJmNTc2NGJlYjMxZjI1NGM4M2YwMzYiXSxbInRlbXBsYXRlL2dvdmVybmFuY2Uva2VybmVsL2hvb2tzL2FnZW50X21vZGVsLnB5IiwxODcsMTk1LCJlMzFmNzAzZWZlZDc2ZTA0OWM4ZjM4MjMiXSxbInRlbXBsYXRlL2dvdmVybmFuY2Uva2VybmVsL2hvb2tzL2FnZW50X21vZGVsLnB5IiwxOTYsMTk3LCIxOTY5NzJjNDM5NzIwNGYxYjZiMzVkZmMiXSxbInRlbXBsYXRlL2dvdmVybmFuY2Uva2VybmVsL2hvb2tzL2FnZW50X21vZGVsLnB5IiwyNjUsMjY2LCI0ZjM3ZThhYjA2MGE5YTUwMWFiNDFkZjMiXV0sImYiOiIvaG9tZS91c2Fpbi9nb3Ytb3Mtd29ya3RyZWVzL1cyLTAwLXN0b3JlLWEiLCJpIjpbXSwibyI6MjAsInAiOnsiYiI6InNlcnZpY2UiLCJkIjoiY3VkYTowIiwiaCI6IjJhMTM5YjJkNDIzYzQ4NGYiLCJvIjpbMSwyMCwyLDE4LDQsMCwzMCw5LDUsNiw4LDE5LDIxLDIyLDI0LDI1LDI3LDI4LDMxLDMyLDM1LDM3LDcsMzgsMzksMywxMywzNCwxMCwyOSwzMywxNSwxMSwyMywyNiwxNCwzNiwxMiwxNywxNl19LCJxIjoiYWdlbnRfbW9kZWwucHkgaG9vayB3cml0ZXMgdGhlIHJvbGUgdGFibGUgbW9kZWwgaW50byBhbiBBZ2VudCBzcGF3biwgdXBkYXRlZElucHV0LCByb2xlIHRhYmxlIGZ1bGwgbW9kZWwgaWRzLCBBZ2VudCB0b29sIG1vZGVsIGFsaWFzZXMsIG1vZGVsIGhvb2sgdGVzdHMgYnl0ZS1lcXVhbCBjb3BpZXMiLCJyIjowLCJzIjoiYTIyMTRhZDRiODY1OTU1NjdmY2QxZTRiOWM3Y2I4YTY0YmJmMjZlOCIsInQiOm51bGwsIngiOlsiZTk2ZDdiMDc1MTMzNjQ2NzM4ZjM4NTQ4Il19",
  "routing": {
    "code": [],
    "named": [],
    "phrasings": [
      "agent_model.py hook writes the role table model into an Agent spawn, updatedInput, role table full model ids, Agent tool model aliases, model hook tests byte-equal copies",
      "agent_model.py hook writes role table model Agent spawn updatedInput role table full model ids Agent tool model aliases model hook tests byte-equal copies"
    ]
  },
  "pool": {
    "settings": {
      "meaning_uncut": true,
      "route_depth": 60,
      "rerank_depth": 40,
      "per_file_first10": 2,
      "drop_nested": true
    },
    "reranked": 40,
    "order": "first",
    "nested": [
      {
        "chunk_id": "502f5764beb31f254c83f036",
        "path": "template/governance/kernel/hooks/agent_model.py",
        "start_line": 168,
        "end_line": 184
      },
      {
        "chunk_id": "196972c4397204f1b6b35dfc",
        "path": "template/governance/kernel/hooks/agent_model.py",
        "start_line": 196,
        "end_line": 197
      },
      {
        "chunk_id": "1a711ba6d1a1983a7b2baf0a",
        "path": "template/governance/kernel/hooks/agent_model.py",
        "start_line": 82,
        "end_line": 83
      },
      {
        "chunk_id": "1e8d3fb68926593a2588fcae",
        "path": "template/governance/kernel/hooks/agent_model.py",
        "start_line": 68,
        "end_line": 69
      },
      {
        "chunk_id": "2ae8ed664a890fceed202d70",
        "path": "template/governance/kernel/hooks/agent_model.py",
        "start_line": 73,
        "end_line": 74
      },
      {
        "chunk_id": "3518cb8cb01d6dbb5550e0f2",
        "path": "template/governance/kernel/hooks/agent_model.py",
        "start_line": 89,
        "end_line": 90
      },
      {
        "chunk_id": "3900bb89df95d5adb5335446",
        "path": "template/governance/kernel/hooks/agent_model.py",
        "start_line": 152,
        "end_line": 153
      },
      {
        "chunk_id": "4c64e429d42a1e745bf5caab",
        "path": "template/governance/kernel/hooks/agent_model.py",
        "start_line": 157,
        "end_line": 158
      },
      {
        "chunk_id": "4f37e8ab060a9a501ab41df3",
        "path": "template/governance/kernel/hooks/agent_model.py",
        "start_line": 265,
        "end_line": 266
      },
      {
        "chunk_id": "676e47301ac89db454275db6",
        "path": "template/governance/kernel/hooks/agent_model.py",
        "start_line": 132,
        "end_line": 133
      }
    ]
  }
}
