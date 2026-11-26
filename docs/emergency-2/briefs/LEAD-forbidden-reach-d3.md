# Lead brief: forbidden-reach-d3, `gov memaudit forbidden-reach` with D3's classifier present (FINDINGS I-49; a fix under W2-204, DAEO-ma4q)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-26. **Read `docs/emergency-2/briefs/LEAD-COMMON.md`
first: every rule there applies.** Decide, never ask (I-10). Use `systematic-debugging`. Every `gov retrieve` takes
`--root /home/usain/gov-os-worktrees/W2-00-store`. Never open a hidden question-set root. **Small and fast: release 0.1.8 waits on it.**

## Why
The 0.1.8 release suite (`docs/close/nightly/NR-20261126T130205Z-84e60c40e97a.json`) found four cases of
`tests/unit/memaudit/test_forbidden_reach.py` failing alone on the integration branch: `test_a_stale_class_without_either_policy_counts_as_outside`
and `test_of_two_excluding_namespaces_the_first_in_the_map_holds_the_file_once[first0-second0]`, `[first1-second1]`, `[first3-second3]`;
each run gives `(4, ['ERROR: GovError'])` instead of the count line (`:73`). `forbidden-reach` (`src/gov/memaudit/forbiddenreach.py`) was
built where D3's classifier `gov.retrieval.stale` did not exist and uses it once it does; batch A brought it. Read FINDINGS I-49, the
landing record `.gov-runtime/scratch/orchestrator/log/landings/forbidden-reach-20261126.md`, and `src/gov/retrieval/stale.py`.

## What (a `## Fix:` line in `.tickets/DAEO-ma4q.md`)
- **FD-1** Find which call raises `GovError` with D3's classifier present (file:line) and fix the cause in `forbiddenreach.py` (or, if the
  classifier's contract is what is wrong, say so and fix the smallest side, with the CTO named in your return): the four cases pass, and the
  rest of the file, W2-204's `forbidden-reach` acceptance file and D3's own tests stay green. The unit cases are the engineer's; acceptance
  files are the test designer's only if one must change (say why).

## Where
Worktree `/home/usain/gov-os-worktrees/E2-forbidden-reach-d3`, branch `e2/forbidden-reach-d3` from `w2/integrate`. Code area:
`src/gov/memaudit/forbiddenreach.py`, `tests/unit/memaudit/test_forbidden_reach.py`, and `src/gov/retrieval/stale.py` only if FD-1 shows it
must change. Never merge into `w2/integrate`.

## Green
The four cases green; `tests/unit/memaudit`, `tests/unit/retrieval`, `tests/acceptance/W2-204/test_w2_204_fr_forbidden_reach.py` and
`tests/acceptance/W2-212` green; then exactly the impact-selected suites (`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue
DAEO-ma4q=e2/forbidden-reach-d3 --onto w2/integrate --select`) through the heavy slot. Check the trailers (LEAD-COMMON).

## Return
Branch and head; the cause (file:line); the fix; the runs' summaries; your retrieves (count, queries, records used). Under 300 words.

## Your memory bundle (DEC-1249 (1); profile: code locations, conventions, earlier fixes and findings; uncut)
store: 84e60c40e97a (/home/usain/gov-os-worktrees/W2-00-store-a)
{
  "store": {
    "commit": "84e60c40e97affc464efe4a3bf60dce2716e5fd5",
    "head": "84e60c40e97affc464efe4a3bf60dce2716e5fd5",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-a"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "8dd60c7db510871157bc9944",
      "sha256": "8701b0a2114abf1cff4a080609669f06db2217aa24b1269780720cf27ab73cf2",
      "path": "src/gov/memaudit/forbiddenreach.py",
      "start_line": 45,
      "end_line": 53,
      "text": "def _stale_classifier():\n    \"\"\"D3's ``classifier`` (``gov.retrieval.stale``), or None on a tree that has no such module.\"\"\"\n    try:\n        from gov.retrieval.stale import classifier\n    except ModuleNotFoundError as exc:\n        if exc.name != \"gov.retrieval.stale\":\n            raise\n        return None\n    return classifier\n",
      "chunk_id": "8dd60c7db510871157bc9944",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "3a93c748afa53ce705ceae0b",
      "sha256": "2ce1e88dffe1ea8c3ddfb11ba4c97c2e25090b8ff2d0541962cf00e317f7420c",
      "path": "src/gov/doctor/command.py",
      "start_line": 995,
      "end_line": 1021,
      "text": "def _check_stale_class(root: Path) -> dict:\n    \"\"\"A notice (W2-212 SR-4, DEC-1227 D3): each namespace of the path map that states no ``stale_class`` and is stale\n    as a whole, with the three lines to add, or only in some of its paths, with those paths to move (``unclassed``).\n    Status ``report`` when there is one, else ``pass``; it never makes doctor unhealthy, and a path map that cannot be\n    read gives ``pass``.\"\"\"\n    import yaml\n\n    from gov.retrieval.stale import unclassed\n    try:\n        document = yaml.safe_load((root / \"governance\" / \"project\" / \"path-map.yaml\").read_text(encoding=\"utf-8\"))\n    except (OSError, UnicodeDecodeError, yaml.YAMLError):\n        document = None\n    found = [item if \"paths\" in item else\n             {**item, \"add\": [f\"stale_class: {item['stale_class']}\", \"lexical_policy: not indexed\",\n                              \"embedding_policy: not embedded\"]} for item in unclassed(document)]\n    if not found:\n        return {\"status\": \"pass\", \"namespaces\": []}\n    reasons = []\n    whole = \", \".join(str(item[\"namespace\"]) for item in found if \"add\" in item)\n    if whole:\n        reasons.append(f\"namespace(s) {whole} say superseded, historical, legacy or archive and state no stale_class, \"\n                       \"so their documents are in the default bundle: add the three lines under each (see `add`)\")\n    mixed = \", \".join(str(item[\"namespace\"]) for item in found if \"paths\" in item)\n    if mixed:\n        reasons.append(f\"namespace(s) {mixed} say it in some of their paths only: move those paths into a namespace of \"\n                       \"their own with the stale class (see `paths` and `move`)\")\n    return {\"status\": \"report\", \"namespaces\": found, \"reason\": \"; \".join(reasons)}\n",
      "chunk_id": "3a93c748afa53ce705ceae0b",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "3e577622af3144f8ae8ad56d",
      "sha256": "3be92cc8f49de1830f74d05683241e68e27e278366c408fbff0b991314cd6627",
      "path": "src/gov/retrieval/stale.py",
      "start_line": 30,
      "end_line": 53,
      "text": "def unclassed(document) -> list[dict]:\n    \"\"\"Each namespace of a parsed path map that states no ``stale_class`` and says superseded, historical, legacy or\n    archive in its name or paths. Stale as a whole (its name, or every one of its paths, says it):\n    ``{namespace, words, stale_class}``. Only some of its paths (a catch-all namespace keeps live documents):\n    ``{namespace, words, paths, move}``, ``paths`` those that say it. Reads no file; a map that is no map gives ``[]``.\"\"\"\n    spaces = document.get(\"namespaces\") if isinstance(document, dict) else None\n    found = []\n    for name, space in (spaces.items() if isinstance(spaces, dict) else ()):\n        if not isinstance(space, dict) or STALE_CLASS in space:\n            continue\n        paths = space.get(\"paths\") if isinstance(space.get(\"paths\"), list) else []\n        words = stale_words(name, *paths)\n        if not words:\n            continue\n        stale = [path for path in paths if stale_words(path)]\n        if stale_words(name) or len(stale) == len(paths):\n            found.append({\"namespace\": name, \"words\": words, \"stale_class\": STALE_WORDS[words[0]]})\n        else:\n            found.append({\"namespace\": name, \"words\": words, \"paths\": stale,\n                          \"move\": f\"if their documents are stale, move {', '.join(map(str, stale))} out of `{name}` \"\n                                  f\"into a namespace of their own that states stale_class {STALE_WORDS[words[0]]} with \"\n                                  \"lexical_policy `not indexed` and embedding_policy `not embedded`; the other paths \"\n                                  \"stay as they are\"})\n    return found\n",
      "chunk_id": "3e577622af3144f8ae8ad56d",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "c495b465687492217d585b54",
      "sha256": "8220e0941b5529ae2ca1c7d6e7c664905be84b6abf3a1803afb3a6ead1029873",
      "path": "template/governance/kernel/skills/adopt/SKILL.md",
      "start_line": 49,
      "end_line": 62,
      "text": "## Stale class (W2-212, DEC-1227 D3)\n\nA namespace whose documents are superseded, historical or legacy states `stale_class`, one of `superseded`, `historical` or `legacy`, never guessed from a name. With it the namespace states both policies that keep it out of default memory, or the path map is CONFIG_INVALID naming the namespace:\n\n```yaml\nstale_class: legacy\nlexical_policy: not indexed\nembedding_policy: not embedded\n```\n\n`gov retrieve` then leaves those documents out of its default bundle, on every route, even if they were indexed before the class existed; they are found on purpose with `gov retrieve --include-stale` or a question that names the file's path, listed under `stale`, each marked `stale: true` with its `stale_class`.\n\nStage A3 refuses (`ADOPT_STALE_CLASS`), naming it and recording nothing, a namespace without `stale_class` whose name, or every path, holds the word superseded, historical, legacy or archive (archive is `historical`; whole words). If only some paths or a description field do, A3 records, with a notice under `notices`; move such paths into a classed namespace of their own, never class a catch-all. `gov doctor`'s `stale_class` part reports both, never failing.\n\n",
      "chunk_id": "c495b465687492217d585b54",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "2cefbde65d0d80940856ba1b",
      "sha256": "6898e2695e957a85b0eb38e411b8cbce09b49b3cb6179715369612018a310a05",
      "path": "src/gov/adopt/stages.py",
      "start_line": 459,
      "end_line": 493,
      "text": "def _stale_classes(config: dict) -> list[dict]:\n    \"\"\"Refuse (ADOPT_STALE_CLASS) a namespace that is stale as a whole and states no ``stale_class`` (W2-212, DEC-1227\n    D3; ``unclassed``). Returns the notices: a namespace only some of whose paths say it, and one only a description\n    field says it of. The value of a class stated is the loader's (CONFIG_INVALID), not judged here.\"\"\"\n    path_map = config.get(\"path-map.yaml\")\n    spaces = path_map.get(\"namespaces\") if isinstance(path_map, dict) else None\n    if not isinstance(spaces, dict):\n        return []\n    found = {item[\"namespace\"]: item for item in unclassed(path_map)}\n    faults = {name: item for name, item in found.items() if \"paths\" not in item}\n    if faults:\n        lines = [f\"namespace `{name}` says {', '.join(item['words'])} in its name or paths and states no stale_class\"\n                 for name, item in faults.items()]\n        raise refuse(\"STALE_CLASS\", \"the path map is not recorded: \" + \"; \".join(lines) + \"; give each stale_class: \"\n                     \"superseded, historical or legacy (archive is historical) with lexical_policy: not indexed and \"\n                     \"embedding_policy: not embedded, so its documents stay out of the default bundle\",\n                     namespaces=list(faults), classes={name: item[\"stale_class\"] for name, item in faults.items()})\n    notices = []\n    for name, space in spaces.items():\n        if not isinstance(space, dict) or \"stale_class\" in space:\n            continue\n        if name in found:\n            item = found[name]\n            notices.append({\"namespace\": name, \"words\": item[\"words\"], \"paths\": item[\"paths\"],\n                            \"notice\": f\"namespace `{name}` says {', '.join(item['words'])} in some of its paths only \"\n                                      f\"and states no stale_class: {item['move']}\"})\n            continue\n        said = _stale_words(*(space.get(field, \"\") for field in STALE_DESCRIBED))\n        if said:\n            notices.append({\"namespace\": name, \"words\": said,\n                            \"notice\": f\"namespace `{name}` describes itself as {', '.join(said)} but states no \"\n                                      f\"stale_class: if its documents are stale, add stale_class: \"\n                                      f\"{STALE_WORDS[said[0]]}, lexical_policy: not indexed, embedding_policy: \"\n                                      \"not embedded\"})\n    return notices\n",
      "chunk_id": "2cefbde65d0d80940856ba1b",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "3b3a7ea25ef39f01246938c1",
      "sha256": "8220e0941b5529ae2ca1c7d6e7c664905be84b6abf3a1803afb3a6ead1029873",
      "path": ".claude/skills/adopt/SKILL.md",
      "start_line": 49,
      "end_line": 62,
      "text": "## Stale class (W2-212, DEC-1227 D3)\n\nA namespace whose documents are superseded, historical or legacy states `stale_class`, one of `superseded`, `historical` or `legacy`, never guessed from a name. With it the namespace states both policies that keep it out of default memory, or the path map is CONFIG_INVALID naming the namespace:\n\n```yaml\nstale_class: legacy\nlexical_policy: not indexed\nembedding_policy: not embedded\n```\n\n`gov retrieve` then leaves those documents out of its default bundle, on every route, even if they were indexed before the class existed; they are found on purpose with `gov retrieve --include-stale` or a question that names the file's path, listed under `stale`, each marked `stale: true` with its `stale_class`.\n\nStage A3 refuses (`ADOPT_STALE_CLASS`), naming it and recording nothing, a namespace without `stale_class` whose name, or every path, holds the word superseded, historical, legacy or archive (archive is `historical`; whole words). If only some paths or a description field do, A3 records, with a notice under `notices`; move such paths into a classed namespace of their own, never class a catch-all. `gov doctor`'s `stale_class` part reports both, never failing.\n\n",
      "chunk_id": "3b3a7ea25ef39f01246938c1",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "0fc2df4c2c0bfb7f1f4bb9a3",
      "sha256": "8220e0941b5529ae2ca1c7d6e7c664905be84b6abf3a1803afb3a6ead1029873",
      "path": ".rulesync/skills/adopt/SKILL.md",
      "start_line": 49,
      "end_line": 62,
      "text": "## Stale class (W2-212, DEC-1227 D3)\n\nA namespace whose documents are superseded, historical or legacy states `stale_class`, one of `superseded`, `historical` or `legacy`, never guessed from a name. With it the namespace states both policies that keep it out of default memory, or the path map is CONFIG_INVALID naming the namespace:\n\n```yaml\nstale_class: legacy\nlexical_policy: not indexed\nembedding_policy: not embedded\n```\n\n`gov retrieve` then leaves those documents out of its default bundle, on every route, even if they were indexed before the class existed; they are found on purpose with `gov retrieve --include-stale` or a question that names the file's path, listed under `stale`, each marked `stale: true` with its `stale_class`.\n\nStage A3 refuses (`ADOPT_STALE_CLASS`), naming it and recording nothing, a namespace without `stale_class` whose name, or every path, holds the word superseded, historical, legacy or archive (archive is `historical`; whole words). If only some paths or a description field do, A3 records, with a notice under `notices`; move such paths into a classed namespace of their own, never class a catch-all. `gov doctor`'s `stale_class` part reports both, never failing.\n\n",
      "chunk_id": "0fc2df4c2c0bfb7f1f4bb9a3",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "3f49ed9b081149ab7f1560f0",
      "sha256": "c1dfef6391154c6abc559ca306dc93be08f7ccad2bb05ee7f3e63f1640d0b059",
      "path": "src/gov/retrieval/stale.py",
      "start_line": 73,
      "end_line": 82,
      "text": "def classifier(root: Path):\n    \"\"\"``path -> (namespace, stale_class)`` or None, for the path map's stale-class namespaces; reads the path map only.\"\"\"\n    rules = _rules(root)\n\n    def of(rel: str):\n        for name, kind, pattern in rules:\n            if pattern.fullmatch(rel):\n                return name, kind\n        return None\n    return of if rules else None\n",
      "chunk_id": "3f49ed9b081149ab7f1560f0",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "13f3f606f71fabf5a9d94e8b",
      "sha256": "ffc04b7e57a40ab7a0e3562403197d5091174c4363238ff62d77aa0e7b2b8b8b",
      "path": "src/gov/retrieval/stale.py",
      "start_line": 60,
      "end_line": 70,
      "text": "def _rules(root: Path) -> list[tuple[str, str, re.Pattern]]:\n    map_rel = f\"{lexical.PROJECT_DIR}/path-map.yaml\"\n    place = Path(root) / map_rel\n    document = read_yaml(place, \"CONFIG_INVALID\", map_rel) if place.is_file() else None\n    namespaces = document.get(\"namespaces\") if isinstance(document, dict) else None\n    rules = []\n    for name, entry in (namespaces.items() if isinstance(namespaces, dict) else ()):\n        if isinstance(entry, dict) and entry.get(STALE_CLASS) and isinstance(entry.get(\"paths\"), list):\n            rules += [(name, entry[STALE_CLASS], lexical._pattern(pattern))\n                      for pattern in entry[\"paths\"] if isinstance(pattern, str)]\n    return rules\n",
      "chunk_id": "13f3f606f71fabf5a9d94e8b",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "8f9d555ac8df712624b07804",
      "sha256": "8220e0941b5529ae2ca1c7d6e7c664905be84b6abf3a1803afb3a6ead1029873",
      "path": "template/.rulesync/skills/adopt/SKILL.md",
      "start_line": 49,
      "end_line": 62,
      "text": "## Stale class (W2-212, DEC-1227 D3)\n\nA namespace whose documents are superseded, historical or legacy states `stale_class`, one of `superseded`, `historical` or `legacy`, never guessed from a name. With it the namespace states both policies that keep it out of default memory, or the path map is CONFIG_INVALID naming the namespace:\n\n```yaml\nstale_class: legacy\nlexical_policy: not indexed\nembedding_policy: not embedded\n```\n\n`gov retrieve` then leaves those documents out of its default bundle, on every route, even if they were indexed before the class existed; they are found on purpose with `gov retrieve --include-stale` or a question that names the file's path, listed under `stale`, each marked `stale: true` with its `stale_class`.\n\nStage A3 refuses (`ADOPT_STALE_CLASS`), naming it and recording nothing, a namespace without `stale_class` whose name, or every path, holds the word superseded, historical, legacy or archive (archive is `historical`; whole words). If only some paths or a description field do, A3 records, with a notice under `notices`; move such paths into a classed namespace of their own, never class a catch-all. `gov doctor`'s `stale_class` part reports both, never failing.\n\n",
      "chunk_id": "8f9d555ac8df712624b07804",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-d3sr",
      "sha256": "8b8bfec4e870cee13871e1cc13659a929be00541ae585c3f445761d37ba1daff",
      "path": ".tickets/DAEO-d3sr.md",
      "start_line": 59,
      "end_line": 63,
      "text": "## Design (the lead's choices)\n- Namespace field `stale_class: superseded | historical | legacy` (optional). It requires `lexical_policy: not indexed` and `embedding_policy: not embedded`.\n- Retrieval drops chunks of stale-class paths from every route unless `include_stale`; `--include-stale` and a path named in the question add a `stale` list to the bundle, read from the files, each entry `stale: true`.\n- A3 refuses, without the class, only a namespace stale as a whole (its name, or every one of its paths, says it). A namespace only some of whose paths say it is recorded with a notice naming those paths to move into a namespace of their own; a description-field match is a notice too. `gov doctor` notices the same for an adopted repository. One function (`gov.retrieval.stale.unclassed`) classifies for both.\n\n",
      "chunk_id": "a39720090e08fb406677c969",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "58dcc34173423da187957def",
      "sha256": "3c94e972baad1eddb1e90c799e331400fcefbeae66214d56dfce271930a9d65a",
      "path": "src/gov/retrieval/stale.py",
      "start_line": 1,
      "end_line": 18,
      "text": "\"\"\"The stale route (W2-212, DEC-1227 D3): the namespaces a path map marks ``stale_class`` (superseded, historical or\nlegacy) are kept out of every route of ``gov retrieve``'s default bundle, even a chunk indexed before the class existed,\nand are found on purpose: the bundle's ``stale`` list, read from the files (never the index), for ``--include-stale``\nor a question that names the file's path. Each entry is marked ``stale: true`` with its ``stale_class``.\"\"\"\n\nfrom __future__ import annotations\n\nimport os\nimport re\nfrom pathlib import Path\n\nfrom gov.config.loader import STALE_CLASS, read_yaml\nfrom gov.retrieval import lexical\n\nSTALE_WORDS = {\"superseded\": \"superseded\", \"historical\": \"historical\", \"legacy\": \"legacy\", \"archive\": \"historical\"}\nSTALE_DESCRIBED = (\"provenance\", \"retention\", \"sensitivity\", \"export_policy\", \"deletion_rebuild\")\n\n\n",
      "chunk_id": "58dcc34173423da187957def",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "d3bcff3fd9b66b7d00658907",
      "sha256": "3934a33b3620134315b0d68ada0e7af3842730d080754e588afe99930ff43aa1",
      "path": "src/gov/config/loader.py",
      "start_line": 145,
      "end_line": 162,
      "text": "def lexical_policy_fault(ns_value: dict) -> str | None:\n    \"\"\"Why the namespace's ``lexical_policy`` is refused, or None: a value other than ``LEXICAL_POLICIES`` (absent is\n    ``indexed``), or ``not indexed`` with ``embedding_policy: embedded``; a ``stale_class`` outside\n    ``STALE_CLASSES``, or one without ``not indexed`` and ``not embedded`` (W2-212).\"\"\"\n    if STALE_CLASS in ns_value:\n        if ns_value[STALE_CLASS] not in STALE_CLASSES:\n            return f\"{STALE_CLASS} must be one of {STALE_CLASSES}, not {ns_value[STALE_CLASS]!r}\"\n        if ns_value.get(LEXICAL_POLICY) != NOT_INDEXED or ns_value.get(\"embedding_policy\") != NOT_EMBEDDED:\n            return (f\"a namespace with {STALE_CLASS} must state {LEXICAL_POLICY}: {NOT_INDEXED} and \"\n                    f\"embedding_policy: {NOT_EMBEDDED}, or its files stay in the default bundle\")\n    if LEXICAL_POLICY not in ns_value:\n        return None\n    if ns_value[LEXICAL_POLICY] not in LEXICAL_POLICIES:\n        return f\"must be one of {LEXICAL_POLICIES} (absent: {INDEXED})\"\n    if ns_value[LEXICAL_POLICY] == NOT_INDEXED and ns_value.get(\"embedding_policy\") == EMBEDDED:\n        return (f\"{NOT_INDEXED} cannot be embedded: the vectors are built from the keyword index's chunks \"\n                f\"(embedding_policy is {EMBEDDED})\")\n    return None\n",
      "chunk_id": "d3bcff3fd9b66b7d00658907",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "3956d8266c1faeb36be82246",
      "sha256": "c835f411c8bedf1edb23d317d295d688412102b02d0a8f41d6a1109c9849a80a",
      "path": "src/gov/config/loader.py",
      "start_line": 46,
      "end_line": 60,
      "text": "POOL_FLAGS = (\"meaning_uncut\", \"drop_nested\")\nKNOWN_FILES = {\"path-map.yaml\": PATH_MAP_SCHEMA, SECRETS_FILE: SECRETS_SCHEMA, RETRIEVAL_FILE: RETRIEVAL_SCHEMA}\n# A namespace's keyword-index policy (DEC-1066 (3)): optional, one of two values; absent is indexed. Any other value is\n# CONFIG_INVALID in either form of the path map, so a misspelt exclusion never leaves its files in the index.\nLEXICAL_POLICY = \"lexical_policy\"\nINDEXED, NOT_INDEXED = \"indexed\", \"not indexed\"\nLEXICAL_POLICIES = (INDEXED, NOT_INDEXED)\n# ``not indexed`` with ``embedding_policy: embedded`` is refused (the CTO, P2): the vectors are built from the keyword\n# index's chunks, so such a namespace would get no vectors while claiming them. The value semantic retrieval embeds.\nEMBEDDED = \"embedded\"\n# A namespace's stale class (W2-212, DEC-1227 D3): optional; it needs both policies that keep the files out of the keyword\n# index and the vectors, so a class that still leaves them in the default bundle is CONFIG_INVALID, never fails open.\nSTALE_CLASS = \"stale_class\"\nSTALE_CLASSES = (\"superseded\", \"historical\", \"legacy\")\nNOT_EMBEDDED = \"not embedded\"\n",
      "chunk_id": "3956d8266c1faeb36be82246",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "9b4e4df532082e2acffa3420",
      "sha256": "91bc766bdb00ffd00f70b1be6ea43e3ecbad7e71056bc6690647e4f54ce46525",
      "path": "tests/unit/retrieval/test_w2_212_stale.py",
      "start_line": 1,
      "end_line": 50,
      "text": "\"\"\"W2-212 (D3): the stale class's loader rule and the word matching that A3 and doctor share.\"\"\"\n\nfrom gov.config.loader import lexical_policy_fault\nfrom gov.retrieval.stale import classifier, stale_words, unclassed\n\nGOOD = {\"stale_class\": \"legacy\", \"lexical_policy\": \"not indexed\", \"embedding_policy\": \"not embedded\"}\n\n\ndef test_a_class_with_both_policies_is_no_fault():\n    assert lexical_policy_fault(GOOD) is None\n\n\ndef test_a_class_without_a_policy_is_a_fault():\n    assert \"stale_class\" in lexical_policy_fault({**GOOD, \"lexical_policy\": \"indexed\"})\n    assert \"stale_class\" in lexical_policy_fault({**GOOD, \"embedding_policy\": \"embedded\"})\n    assert \"stale_class\" in lexical_policy_fault({\"stale_class\": \"legacy\"})\n\n\ndef test_a_class_outside_the_three_is_a_fault():\n    assert \"stale_class\" in lexical_policy_fault({**GOOD, \"stale_class\": \"old\"})\n\n\ndef test_words_are_whole_word_parts_and_archive_is_historical():\n    assert stale_words(\"Legacy-Docs\", \"docs/old_archive/**\") == [\"legacy\", \"archive\"]\n    assert stale_words(\"legacyish\") == []\n    assert unclassed({\"namespaces\": {\"a\": {\"paths\": [\"docs/archive/**\"]},\n                                     \"b\": {\"paths\": [\"x/**\"], **GOOD}}}) == [\n        {\"namespace\": \"a\", \"words\": [\"archive\"], \"stale_class\": \"historical\"}]\n\n\ndef test_a_namespace_is_stale_as_a_whole_by_its_name_or_by_every_path():\n    found = unclassed({\"namespaces\": {\"legacy-docs\": {\"paths\": [\"docs/live/**\"]},\n                                      \"b\": {\"paths\": [\"docs/legacy/**\", \"old/archive/**\"]},\n                                      \"none\": {\"paths\": []}}})\n    assert [(item[\"namespace\"], \"paths\" in item) for item in found] == [(\"legacy-docs\", False), (\"b\", False)]\n\n\ndef test_a_namespace_only_some_of_whose_paths_say_it_gives_those_paths_to_move():\n    [item] = unclassed({\"namespaces\": {\"harbour\": {\"paths\": [\"docs/**\", \"docs/legacy/**\", \"a/archive/**\"]}}})\n    assert item[\"paths\"] == [\"docs/legacy/**\", \"a/archive/**\"] and item[\"words\"] == [\"legacy\", \"archive\"]\n    assert \"namespace of their own\" in item[\"move\"] and \"stale_class\" in item[\"move\"]\n\n\ndef test_the_classifier_matches_only_classed_namespaces(tmp_path):\n    (tmp_path / \"governance/project\").mkdir(parents=True)\n    (tmp_path / \"governance/project/path-map.yaml\").write_text(\n        \"namespaces:\\n  old:\\n    paths: [docs/old/**]\\n    stale_class: legacy\\n    lexical_policy: not indexed\\n\"\n        \"    embedding_policy: not embedded\\n  cur:\\n    paths: [docs/**]\\n\", encoding=\"utf-8\")\n    of = classifier(tmp_path)\n    assert of(\"docs/old/a.md\") == (\"old\", \"legacy\") and of(\"docs/b.md\") is None\n",
      "chunk_id": "9b4e4df532082e2acffa3420",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "465ac935f15a02b902ccb96e",
      "sha256": "ae99f6826e27b7b96baa2d68a20720cadc1c4e068d0f30534db18a19150fe0cb",
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "start_line": 15,
      "end_line": 26,
      "text": "## 0. What was found (the evidence the rubric rests on)\n\n1. **Guessing staleness from words fails both ways.** D3's stage A3 refused any namespace whose name or paths held\n   `legacy`, `archive`, `superseded` or `historical` (`e2/bundle-a:src/gov/retrieval/stale.py`, `STALE_WORDS`,\n   `unclassed`). It turned about 300 of batch A's 318 reds red (I-40, `DIAGNOSIS-bundle-a-1.md`) and would have dropped\n   the live documents of any catch-all namespace once classed as told (DEC-1254 E-02). The other way, EXAMIN's likely\n   stale sources carry no stale word at all: its pre-adoption register `docs/decisions/**` is \"kept as history\" and\n   `docs/reports/**`, `docs/audits/**` are \"dated history\", yet all three are embedded namespaces (EXAMIN\n   `governance/project/path-map.yaml`, namespaces `plans` and `reports`). Its fresh 80 lost 3 of 5 hidden misses to a cited\n   stale or superseded source (I-36; `docs/audits/wave0/memory/FRESH80-2026-11-25.md`). A word list could never find them;\n   a place can.\n2. **Each repository invents its own map.** Gov OS keeps its archive in `docs/archive/**` and `docs/emergency-2/archive/**`;\n",
      "chunk_id": "465ac935f15a02b902ccb96e",
      "routes": [
        "semantic"
      ],
      "batch": 2
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
    "duplicates": 20,
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
      "chunk_id": "3a93c748afa53ce705ceae0b",
      "parent_id": "a872fb8838507bc8f978082a",
      "path": "src/gov/doctor/command.py",
      "start_line": 995,
      "end_line": 1021
    },
    {
      "chunk_id": "3e577622af3144f8ae8ad56d",
      "parent_id": "832204d10825c0abeb5fe111",
      "path": "src/gov/retrieval/stale.py",
      "start_line": 30,
      "end_line": 53
    },
    {
      "chunk_id": "c495b465687492217d585b54",
      "parent_id": "4c9c653f4494c9e8e4381de2",
      "path": "template/governance/kernel/skills/adopt/SKILL.md",
      "start_line": 49,
      "end_line": 62
    },
    {
      "chunk_id": "2cefbde65d0d80940856ba1b",
      "parent_id": "8fd3323e583dd82e03c3293d",
      "path": "src/gov/adopt/stages.py",
      "start_line": 459,
      "end_line": 493
    },
    {
      "chunk_id": "3b3a7ea25ef39f01246938c1",
      "parent_id": "8a4f00a3511d2261cc3d2eeb",
      "path": ".claude/skills/adopt/SKILL.md",
      "start_line": 49,
      "end_line": 62
    },
    {
      "chunk_id": "0fc2df4c2c0bfb7f1f4bb9a3",
      "parent_id": "c626dfdd4401551184dc36e2",
      "path": ".rulesync/skills/adopt/SKILL.md",
      "start_line": 49,
      "end_line": 62
    },
    {
      "chunk_id": "8f9d555ac8df712624b07804",
      "parent_id": "81fb8965619b9c0c88844a7c",
      "path": "template/.rulesync/skills/adopt/SKILL.md",
      "start_line": 49,
      "end_line": 62
    },
    {
      "chunk_id": "d3bcff3fd9b66b7d00658907",
      "parent_id": "5f9a667f4168d0f9a2343375",
      "path": "src/gov/config/loader.py",
      "start_line": 145,
      "end_line": 162
    },
    {
      "chunk_id": "9b4e4df532082e2acffa3420",
      "parent_id": "b2ba18be47504b02bbab9276",
      "path": "tests/unit/retrieval/test_w2_212_stale.py",
      "start_line": 1,
      "end_line": 50
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "path": "docs/emergency-2/briefs/LEAD-forbidden-reach.md",
      "chunk_id": "186af32357bb85eac238692a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-d3sr.md",
      "chunk_id": "36ed88606c16ee2b7a405cb8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-classification-rubric.md",
      "chunk_id": "ff0514b4b08c340e193dcbc4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-forbidden-reach.md",
      "chunk_id": "6620b7bef27f62696fd1edb6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-classification-rubric.md",
      "chunk_id": "41feca868a62c43c3bbe8c01",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-forbidden-reach.md",
      "chunk_id": "2d71ebe741572cce1cf4e79f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-classification-rubric.md",
      "chunk_id": "2109315af5fba6f6b76fde8f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-d3-stale-route.md",
      "chunk_id": "37b00652826484fd45bf23a7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "de65d6f3164fa6abbad8e421",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-d3sr.md",
      "chunk_id": "448ca60379a697c79eb3952c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "a275bfe54bff524563a0733a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-classification-rubric.md",
      "chunk_id": "2ed0c6b57f328a88d532dbb0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "3cb7c4fa415f3c44a6160e54",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "f6d3bd6f928af653f7994b1e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-bundle-a-reds.md",
      "chunk_id": "c97642dee2be75c6198d9604",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/doctor/command.py",
      "chunk_id": "892818581b17e03503d0e7f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-d3sr.md",
      "chunk_id": "179ad55bdfb1a56f0385dd6c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-classification-rubric.md",
      "chunk_id": "7777e162ec462e29fc5edabc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/cli/errors.py",
      "chunk_id": "2ee0ef097deb52488e914a86",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/cli/errors.py",
      "chunk_id": "2fab0638d1a25bdfddbe8b36",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/forbiddenreach.py",
      "chunk_id": "a246f206f89e0b1b0cc9549b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-classification-rubric.md",
      "chunk_id": "269f2e537b700026d3749a68",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "c8fff461ae1527597aeea76e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-d3sr.md",
      "chunk_id": "a927d7654e7f10493a8c7c0e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-bundle-a-reds.md",
      "chunk_id": "bede30dacba43ffb04353cf8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/stale.py",
      "chunk_id": "2c9292f4a46418ee759f7c9c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "b7763a3232a979a4d54eacfc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/stale.py",
      "chunk_id": "4e53adc8eab9d2393cd7747a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/stale.py",
      "chunk_id": "8591831523b29681eb6629f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-bundle-a-reds.md",
      "chunk_id": "bfb6c50387e3a793a5fbe481",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-212/README.md",
      "chunk_id": "78e93ba396b292bd24e4f22e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/stale.py",
      "chunk_id": "f51df80621d02ca03391f93f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RUBRIC-DECISIONS-2026-11-26.html",
      "chunk_id": "1151003d5dc286ae19252a90",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-26.html",
      "chunk_id": "03e8c53af0059f893eec8656",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "6e7f96af45e10f7bd0c877b3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-212/w2_212_support.py",
      "chunk_id": "c0a122e987035514b657cdc5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/stale.py",
      "chunk_id": "c779b7455b534d77fbaf91b3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/lexical.py",
      "chunk_id": "5f891d3f1009f38f4a65734b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".claude/skills/adopt/SKILL.md",
      "chunk_id": "33f14b081f78f4260e11d1e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "59ba9be3b049184fb82d054c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".rulesync/skills/adopt/SKILL.md",
      "chunk_id": "a9de5b9c07f970e467704b20",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "85de2139ec51ead681f3f596",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/.rulesync/skills/adopt/SKILL.md",
      "chunk_id": "7c9fe114d1a72a244f68d784",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "493899489a894da356a23d79",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "88d30862fcf2e7223b409ff2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "1cc94a0d2f222e4b847d7619",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "73b7802e869a1c1d37c09702",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "d4bfc04b20cfe19c3b5e483b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "b3dbaab81edb854e3d71938a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "2b751e0f5253dea898b427a3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "ecde9005925a223340261323",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "7ae24a260a1b43a3afd0c9fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "3495a37ef888fc803b30e097",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/retrieval/test_w2_212_stale.py",
      "chunk_id": "e269ebf73d884c49ad326306",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "e85a257b7359d4d2c32c14f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "c5e9e1ef3324bbea70c0d38a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "e3ad5bcfe45a7f1e8a305156",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-classification-rubric.md",
      "chunk_id": "f4ed4eab9d8523c9907963d8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "3d4ea60a227b9907d3efa0e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "caffefdeabb7f070193358de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "e92d60b2a85d75863295d7d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-13-evidence.md",
      "chunk_id": "eeef122d66bf43f29dfc6f71",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "bb0f8c740c9c2052eb9882ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/check/pathmap.py",
      "chunk_id": "5f5822be36ebfafe24aa1e5b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "81279b225463dfc1ded09e6f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A2-classification.md",
      "chunk_id": "688ecf6a4c395cef9de1d417",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "b3da8a06e0eab3acdad3e74b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-13-evidence.md",
      "chunk_id": "c585ccaaf11e814ef38dedac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/adopt/test_adopt.py",
      "chunk_id": "a64e916ff573c786213e5f64",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "1e73f43529c8327655efe101",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "49c763885b6f7ba17f61a173",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "e0be8122fde74d8e1220454b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "b19a6694d6e3c331778ccb28",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "f94776d900f7ef21d656701e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "283ba10ee40f9a5f8aabcba3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "a8fd74e50934bd1e330fd646",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "7c7331cd6a8d4dfa1e4747ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "6c4eaf66b4e3096fe25e5507",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "chunk_id": "929a5bc0e21f73676220f03b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md",
      "chunk_id": "905cb141dd6b151a24670696",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-212/test_w2_212_doctor.py",
      "chunk_id": "eddd516492afaeeff0569663",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-d3sr.md",
      "chunk_id": "e5f34c2a2a6a4838e3c5caf8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/memaudit/test_forbidden_reach.py",
      "chunk_id": "7f49f88fd143bb6a7e9961c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-212/README.md",
      "chunk_id": "51965ab631b3904dea4c3660",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/README.md",
      "chunk_id": "8f3ea4c8d99a2124304b6670",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/retrieval/test_w2_212_stale.py",
      "chunk_id": "4e6082a614932c4881d05e3c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/retrieval/test_w2_212_stale.py",
      "chunk_id": "6c4efb060240a2d469506eba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-212/test_w2_212_config.py",
      "chunk_id": "73a24e440f82b805776758e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-212/test_w2_212_adopt.py",
      "chunk_id": "9916c8f91a9d8377fc00f691",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/retrieval/test_w2_13_lexical_policy.py",
      "chunk_id": "53d1476b98cfd480e7dfeaee",
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
    },
    "code": {
      "available": true,
      "reason": null
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5771
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLWQzc3IubWQiLDU5LDYzLCJhMzk3MjAwOTBlMDhmYjQwNjY3N2M5NjkiXSxbImRvY3MvZW1lcmdlbmN5LTIvcHJvcG9zYWxzL0NMQVNTSUZJQ0FUSU9OLVJVQlJJQy5tZCIsMTUsMjYsIjQ2NWFjOTM1ZjE1YTAyYjkwMmNjYjk2ZSJdLFsic3JjL2dvdi9hZG9wdC9zdGFnZXMucHkiLDQ3Miw0ODgsImIyNjEzNzEwYmJiMmU5MmFlYzU5YWFmMiJdLFsic3JjL2dvdi9hZG9wdC9zdGFnZXMucHkiLDQ4Niw0OTMsImNkNjBmZjMwNmIyNzYyY2FkOWQ5YWZhNSJdLFsic3JjL2dvdi9jb25maWcvbG9hZGVyLnB5Iiw0Niw2MCwiMzk1NmQ4MjY2YzFmYWViMzZiZTgyMjQ2Il0sWyJzcmMvZ292L21lbWF1ZGl0L2ZvcmJpZGRlbnJlYWNoLnB5Iiw0NSw1MywiOGRkNjBjN2RiNTEwODcxMTU3YmM5OTQ0Il0sWyJzcmMvZ292L3JldHJpZXZhbC9zdGFsZS5weSIsMSwxOCwiNThkY2MzNDE3MzQyM2RhMTg3OTU3ZGVmIl0sWyJzcmMvZ292L3JldHJpZXZhbC9zdGFsZS5weSIsNDUsNTMsIjI0M2VhYjQxOWNjN2U5ZjVjY2UyMTJhZCJdLFsic3JjL2dvdi9yZXRyaWV2YWwvc3RhbGUucHkiLDYwLDcwLCIxM2YzZjYwNmY3MWZhYmY1YTlkOTRlOGIiXSxbInNyYy9nb3YvcmV0cmlldmFsL3N0YWxlLnB5Iiw3Myw4MiwiM2Y0OWVkOWIwODExNDlhYjdmMTU2MGYwIl0sWyJ0ZW1wbGF0ZS9nb3Zlcm5hbmNlL2tlcm5lbC9za2lsbHMvYWRvcHQvU0tJTEwubWQiLDU5LDYyLCJkMmU0ZTc5ZGUwNGIwNjZmZTViOWZhZTUiXV0sImYiOiIvaG9tZS91c2Fpbi9nb3Ytb3Mtd29ya3RyZWVzL1cyLTAwLXN0b3JlLWEiLCJpIjpbXSwibyI6MjAsInAiOnsiYiI6InNlcnZpY2UiLCJkIjoiY3VkYTowIiwiaCI6IjU2NTViNzBiZWFkYzJhMjgiLCJvIjpbMjUsMSwzLDAsNyw0LDYsMTMsMjYsMjcsMiwxMCwyOSw1LDksMTQsMzQsMzksMTcsMzEsMzIsOCwxNSwyMiwzMCwxNiwyOCwzNiwyMywxMSwxMiwzNSwyMCwxOCwzOCwzMywyNCwzNywxOSwyMV19LCJxIjoiZm9yYmlkZGVuLXJlYWNoIGNsYXNzaWZpZXIgZ292LnJldHJpZXZhbC5zdGFsZSBjbGFzc2lmaWVyIHVuY2xhc3NlZCBHb3ZFcnJvciwgdGhlIHBhdGggbWFwIG5hbWVzcGFjZXMgc3RhbGVfY2xhc3MgbGV4aWNhbF9wb2xpY3kiLCJyIjowLCJzIjoiODRlNjBjNDBlOTdhZmZjNDY0ZWZlNGEzYmY2MGRjZTI3MTZlNWZkNSIsInQiOm51bGwsIngiOlsiNGM5YzY1M2Y0NDk0YzllOGU0MzgxZGUyIiwiNWY5YTY2N2Y0MTY4ZDBmOWEyMzQzMzc1IiwiODFmYjg5NjU2MTliOWMwYzg4ODQ0YTdjIiwiODMyMjA0ZDEwODI1YzBhYmViNWZlMTExIiwiOGE0ZjAwYTM1MTFkMjI2MWNjM2QyZWViIiwiOGZkMzMyM2U1ODNkZDgyZTAzYzMyOTNkIiwiYTg3MmZiODgzODUwN2JjOGY5NzgwODJhIiwiYjJiYTE4YmU0NzUwNGIwMmJiYWI5Mjc2IiwiYzYyNmRmZGQ0NDAxNTUxMTg0ZGMzNmUyIl19",
  "routing": {
    "code": [],
    "named": [],
    "phrasings": [
      "forbidden-reach classifier gov.retrieval.stale classifier unclassed GovError, the path map namespaces stale_class lexical_policy",
      "forbidden-reach classifier gov.retrieval.stale classifier unclassed GovError path map namespaces stale_class lexical_policy"
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
        "chunk_id": "243eab419cc7e9f5cce212ad",
        "path": "src/gov/retrieval/stale.py",
        "start_line": 45,
        "end_line": 53
      },
      {
        "chunk_id": "d2e4e79de04b066fe5b9fae5",
        "path": "template/governance/kernel/skills/adopt/SKILL.md",
        "start_line": 59,
        "end_line": 62
      },
      {
        "chunk_id": "b2613710bbb2e92aec59aaf2",
        "path": "src/gov/adopt/stages.py",
        "start_line": 472,
        "end_line": 488
      },
      {
        "chunk_id": "cd60ff306b2762cad9d9afa5",
        "path": "src/gov/adopt/stages.py",
        "start_line": 486,
        "end_line": 493
      }
    ]
  }
}
