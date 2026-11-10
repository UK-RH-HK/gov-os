"""W2-149 acceptance tests' support: the planted world and the independent oracles.

Nothing here imports the script under test: it is run as a program, from a planted repository, with a planted HOME and
a planted sets root, and a stub ``claude`` first on ``PATH``. The oracles (the selection rule, the filled settings, the
built-wall checks of the rehearsal's ``walls_check.py`` (its F class), the counts' shape) are written from the ticket's
KPI lines and LAUNCH-SPEC alone. The interface they hold the script to is stated in this folder's README.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import pwd
import random
import re
import stat
import subprocess
import sys
import tarfile
import time
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SCRIPT = TREE / "governance" / "project" / "orchestration" / "tools" / "indep_launch.py"
if os.environ.get("W2_149_SCRIPT"):  # the test designer's own check of the cases against a scratch sketch only
    SCRIPT = Path(os.environ["W2_149_SCRIPT"])
SCHEMAS = SCRIPT.parent / "indep-schemas"
COUNTS_SCHEMA = SCHEMAS / "indep-counts.schema.json"
TEMPLATE_REL = "governance/project/indep-walls"
TEMPLATE_SRC = TREE / TEMPLATE_REL
TEMPLATE_FILES = ("settings.json.tmpl", "wall_hook.py", "CLAUDE.md.tmpl", "kinds.yaml", "tree-exclude.txt", "README.md")
BRIEFS_REL = "governance/project/indep-briefs"
KINDS = ("writer", "checker", "auditor", "labeller")
STUB_MODEL = "claude-stub-model"
KIND_TOOLS = {"writer": {"Read", "Grep", "Glob", "Write", "Edit", "TodoWrite"},
              "checker": {"Read", "Grep", "Glob", "Write", "TodoWrite"},
              "auditor": {"Read", "Grep", "Glob", "Write", "TodoWrite"},
              "labeller": {"Read", "Grep", "Glob", "Write", "TodoWrite"}}
KIND_BUDGET = {"writer": 25, "checker": 15, "auditor": 15, "labeller": 30}
KIND_TIMEOUT = {"writer": 7200, "checker": 5400, "auditor": 5400, "labeller": 10800}
FORBIDDEN_TOOLS = {"Bash", "WebFetch", "WebSearch", "Task", "Agent", "NotebookEdit", "Skill"}
DEFAULT_SET = {"writer": "memory-verdict-4", "checker": "memory-verdict-3", "auditor": "memory-verdict-3",
               "labeller": "sandbox-guard-exp-1"}
DELIVER_TO = {"writer": "set", "checker": "notes", "auditor": "classes", "labeller": "labels"}
SEALED = "fixtures/evaluation/sandbox-guard-exp-1/hidden"

# The fixed words of the interface (README "The counts").
ACT = "ACT-INDEP-WALLS-1"
STATUSES = ("delivered", "rejected", "refused", "stopped", "dry")
REASONS = {10: "brief", 11: "template", 12: "wall_exists", 13: "seed_order", 14: "commit", 15: "file_budget",
           16: "canary", 17: "argument", 18: "rules", 20: "result", 21: "stopped", 22: "trace"}
WRITER_KINDS = ("fact", "procedure", "decision", "location", "negative")
WRITER_AREAS = ("contract", "decisions", "kernel", "code", "tests", "operations", "docs")
AUDIT_CLASSES = ("gold_wrong", "question_ambiguous", "retrieval_miss", "answer_wrong", "out_of_scope")
TOOLS_COUNTED = ("Read", "Grep", "Glob", "Write", "Edit", "MultiEdit", "TodoWrite", "Bash", "WebFetch", "WebSearch",
                 "Task", "Agent", "NotebookEdit", "Skill", "other")
COUNTS_KEYS = {"act", "kind", "run", "set", "round", "commit", "brief_sha256", "approved_sha256", "template_ok",
               "seed_sha256", "override", "selection", "session", "out", "delivered", "traces", "status", "code",
               "reason"}
NESTED_KEYS = {"selection": {"changed", "sample", "overlap"},
               "session": {"exit", "is_error", "turns", "cost_usd", "duration_s", "refusals"},
               "refusals": set(TOOLS_COUNTED),
               "out": {"schema_ok", "files", "questions", "by_kind", "by_area", "checked", "accepted", "revise",
                       "rejected", "misses", "labelled", "allow", "refuse", "agree", "disagree"},
               "by_kind": set(WRITER_KINDS), "by_area": set(WRITER_AREAS), "misses": set(AUDIT_CLASSES),
               "delivered": {"files", "sha256", "to"}}
WALL_KEYS = {"kind", "run", "set", "round", "commit", "repo", "tree", "runs", "home", "sets_root", "brief_sha256",
             "seed_sha256", "settings_sha256", "hook_sha256", "template_sha256", "approved_sha256", "selection",
             "seeded_before_content", "runs_override", "trees_override"}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
RUN_ID = re.compile(r"^\d{8}T\d{6}Z-[a-z0-9][a-z0-9-]*-r[12]$")
SET_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
HIDDEN_GLOBS = ("fixtures/evaluation/memory-retrieval/hidden/**", "fixtures/evaluation/memory-verdict/**",
                "fixtures/evaluation/memory-verdict-2/**", "transcripts/**", "runs/fresh-80/**",
                "fixtures/evaluation/sandbox-guard-exp-1/hidden/**", "indep-walls/**")
SGX_SET_BLOCK = """evaluation_sets:
  sandbox-guard-exp-1:
    visible: []
    hidden: ["fixtures/evaluation/sandbox-guard-exp-1/hidden/**"]
    measures:
      roles: [engineer, research, product-spec, independent-test-designer, independent-auditor]
"""
SGX_HIDDEN_GLOB = '"fixtures/evaluation/sandbox-guard-exp-1/hidden/**", '
PATH_MAP = """# Planted path map (W2-149 acceptance tests): the block the launch script counts the hidden part by, and the
# evaluation set writer 2's seal is read from (S24).
""" + SGX_SET_BLOCK + """sets_root_hidden:
  root: "~/gov-os-eval"
  hidden: ["fixtures/evaluation/memory-retrieval/hidden/**", "fixtures/evaluation/memory-verdict/**",
           "fixtures/evaluation/memory-verdict-2/**", "transcripts/**", "runs/fresh-80/**",
           "fixtures/evaluation/sandbox-guard-exp-1/hidden/**", "indep-walls/**"]
  refused_roles: [orchestrator, engineer, research, product-spec, independent-test-designer, independent-auditor]
"""

# -- set-up A's wiring (DEC-1112 (3), DEC-1113): the planted template's kinds.yaml and the five approved briefs' front
# matter, byte for byte (their bodies are never planted: each planted brief carries a short body of the tests' own).
SGX1_TREE_EXCLUDE = (".claude/**", "src/gov/guard/**", "src/gov/launch/**", "governance/project/indep-walls/**")
# S23 (F38; DEC-1113 (2): the overlap auditor decides from the decisions alone): its entry also leaves out every file
# that states which dispute side is which labeller's. The other four set-up A entries keep SGX1_TREE_EXCLUDE.
AUDITOR_TREE_EXCLUDE = (".tickets/**", "governance/project/orchestration/packages/**",
                        "governance/project/orchestration/tools/indep_launch.py", "tests/acceptance/W2-149/**",
                        "tests/unit/orchestration/test_w2_149*", "docs/changes/W2-149-evidence.md")
SGX1_IDS = ("sgx1-writer-tuning", "sgx1-writer-heldout", "sgx1-labeller", "sgx1-labeller-2", "sgx1-overlap-auditor")


def _flow_list(globs) -> str:
    return "[" + ", ".join(json.dumps(g) for g in globs) + "]"


def template_entry_excludes() -> dict:
    """Set-up A's five entries' ``tree_exclude`` as this tree's own template (``kinds.yaml``) states them (S23, F38):
    the planted ``kinds.yaml`` carries them, so a dry build exercises the template's entries as the engineer leaves
    them. An entry missing or malformed falls back to the four globs (S22's and S23's template cases catch it)."""
    try:
        import yaml
        briefs = (yaml.safe_load((TEMPLATE_SRC / "kinds.yaml").read_text()) or {}).get("briefs") or {}
    except Exception:  # noqa: BLE001 - a template that does not parse is the template cases' finding
        briefs = {}
    out = {}
    for bid in SGX1_IDS:
        tx = (briefs.get(bid) or {}).get("tree_exclude") if isinstance(briefs, dict) else None
        ok = isinstance(tx, list) and tx and all(isinstance(g, str) for g in tx)
        out[bid] = tuple(tx) if ok else SGX1_TREE_EXCLUDE
    return out


_TX = _flow_list(SGX1_TREE_EXCLUDE)
_TXE = {bid: _flow_list(g) for bid, g in template_entry_excludes().items()}
KINDS_YAML = f"""# Planted kinds.yaml (W2-149 acceptance tests, set-up A's wiring): the template's four kinds as they stand, each
# with a model, and the briefs: map a brief's missing model, result_schema and sample are taken from (DEC-1112 (3)).
kinds:
  writer:
    tools: [Read, Grep, Glob, Write, Edit, TodoWrite]
    input: [selection]
    input_round2: [set, notes]
    delivers: set
    budget_usd: 25
    timeout_s: 7200
    model: claude-kind-writer
  checker:
    tools: [Read, Grep, Glob, Write, TodoWrite]
    input: [set]
    delivers: notes
    budget_usd: 15
    timeout_s: 5400
    model: claude-kind-checker
  auditor:
    tools: [Read, Grep, Glob, Write, TodoWrite]
    input: [set, misses]
    delivers: classes
    budget_usd: 15
    timeout_s: 5400
    model: claude-kind-auditor
  labeller:
    tools: [Read, Grep, Glob, Write, TodoWrite]
    input: [rulebook, actions]
    delivers: labels
    budget_usd: 30
    timeout_s: 10800
    model: claude-kind-labeller
briefs:
  sgx1-writer-tuning:
    kind: writer
    flow: sgx1-writer-1
    model: claude-entry-writer-tuning
    result_schema: sgx1-writer-tuning-result.schema.json
    tree_exclude: {_TXE['sgx1-writer-tuning']}
  sgx1-writer-heldout:
    kind: writer
    flow: sgx1-writer-2
    result_schema: sgx1-writer-heldout-result.schema.json
    tree_exclude: {_TXE['sgx1-writer-heldout']}
  sgx1-labeller:
    kind: labeller
    flow: sgx1-labeller-1
    model: claude-entry-labeller
    result_schema: sgx1-labeller-result.schema.json
    sample: 0
    tree_exclude: {_TXE['sgx1-labeller']}
  sgx1-labeller-2:
    kind: labeller
    flow: sgx1-labeller-2
    model: claude-entry-labeller-2
    result_schema: sgx1-labeller-2-result.schema.json
    sample: 0
    tree_exclude: {_TXE['sgx1-labeller-2']}
  sgx1-overlap-auditor:
    kind: auditor
    flow: sgx1-overlap-auditor
    model: claude-entry-overlap-auditor
    result_schema: sgx1-overlap-auditor-result.schema.json
    sample: 0
    tree_exclude: {_TXE['sgx1-overlap-auditor']}
  w2-149-no-schema:
    kind: writer
    flow: sgx1-writer-1
    sample: 5
    tree_exclude: {_TX}
  w2-149-no-sample:
    kind: auditor
    flow: sgx1-overlap-auditor
    result_schema: sgx1-overlap-auditor-result.schema.json
    tree_exclude: {_TX}
"""
_TOOLS5 = "tools: [Read, Grep, Glob, Write, TodoWrite]\n"
_TOOLS6 = "tools: [Read, Grep, Glob, Write, Edit, TodoWrite]\n"
_EXP = "experiment: SANDBOX-GUARD-EXP-1\n"
SGX1_FRONT = {
    "labeller": ("---\nbrief: sgx1-labeller\nkind: labeller\nversion: 3\n" + _EXP + "rounds: 2\n" + _TOOLS5
                 + "budget_usd: 30\ntimeout_s: 10800\n---\n"),
    "labeller-2": ("---\nbrief: sgx1-labeller-2\nkind: labeller\nversion: 3\n" + _EXP + "rounds: 2\n" + _TOOLS5
                   + "budget_usd: 30\ntimeout_s: 10800\n---\n"),
    "writer-tuning": ("---\nbrief: sgx1-writer-tuning\nkind: writer\nversion: 3\n" + _EXP + "rounds: 1\n" + _TOOLS6
                      + "sample: 400\nbudget_usd: 25\ntimeout_s: 7200\n---\n"),
    "writer-heldout": ("---\nbrief: sgx1-writer-heldout\nkind: writer\nversion: 3\n" + _EXP + "rounds: 1\n" + _TOOLS6
                       + "sample: 400\nbudget_usd: 25\ntimeout_s: 7200\n---\n"),
    "overlap-auditor": ("---\nbrief: sgx1-overlap-auditor\nkind: auditor\nversion: 1\n" + _EXP + "rounds: 1\n"
                        + _TOOLS5 + "budget_usd: 10\ntimeout_s: 3600\n"
                        + 'budget_basis: "the labellers\' figures (30 USD, 10800 s per half: a rulebook, then several '
                        "hundred actions by hand) scaled to the overlap's disputes, about 40 cases (10 % of 400), one "
                        "round, no rulebook or script; the declaration's brake at twice the projection applies\"\n"
                        + "---\n"),
}
# The sha256 of each approved brief's front matter alone (the .fm files beside the approved briefs, 2026-11-10).
SGX1_FRONT_SHA256 = {
    "labeller": "8d8ec2c78dc7190d252f1a7094e3ec497de4d4e6161d0287e3be77fc44c74723",
    "labeller-2": "ea75f95d0562a71b8976dfc0dc67e7266c8497cf52bdf7e4ae7883d3f4a7541e",
    "writer-tuning": "75558111cac1e00e96c971dd80f176739a12d058b3bc084ec5de975d749f7f65",
    "writer-heldout": "d91987a40a4cb239d205f6815f6eac2ec4ee04e2e994c83f7c4def4dea33c4c9",
    "overlap-auditor": "058e22f90fc205569df7824de4574d06ea58a4af7cb81ebea350308d243b0362",
}
SGX1_BODY = ("# The planted body of a set-up A brief (W2-149 acceptance tests)\n\nNot the approved text: only the front "
             "matter above is the approved brief's, byte for byte.\n")
_FM_EXTRA = "model: claude-front-model\nresult_schema: labeller-result.schema.json\n"
SGX1_VARIANTS = {
    # S22: a front-matter value beats the entry's
    "sgx1x/labeller-front": SGX1_FRONT["labeller"][:-4] + _FM_EXTRA + "---\n",
    # S22: an entry of another kind (every value present in the front matter, so only the entry's kind refuses)
    "sgx1x/writer-as-labeller": ("---\nbrief: sgx1-writer-tuning\nkind: labeller\n" + _FM_EXTRA + "sample: 3\n---\n"),
    "sgx1x/labeller-as-auditor": ("---\nbrief: sgx1-labeller\nkind: auditor\nmodel: claude-front-model\n"
                                  "result_schema: auditor-result.schema.json\nsample: 3\n---\n"),
    # S22: a labeller brief naming no entry, or an id the map does not hold (every value present otherwise)
    "sgx1x/labeller-unknown": ("---\nbrief: sgx1-labeller-9\nkind: labeller\n" + _FM_EXTRA + "sample: 3\n---\n"),
    # S22: a value found nowhere (the entry lacks it and so does the front matter)
    "sgx1x/no-schema": "---\nbrief: w2-149-no-schema\nkind: writer\n---\n",
    "sgx1x/no-sample": "---\nbrief: w2-149-no-sample\nkind: auditor\n---\n",
}
PLANTED_TICKETS = {
    "DAEO-aaa1": ("engineer", "W2-901", ["src/pkg/**", "docs/d01.md"]),
    "DAEO-aaa2": ("independent-test-designer", "W2-902", ["tests/acceptance/W2-902/**"]),
    "DAEO-aaa3": ("orchestrator", "W2-903", ["governance/**", ".tickets/**"]),
}
TICKET_MARK = "MARK-W2149-TICKET-BODY"


def ticket_text(tid, role, wbs, paths):
    lines = ["---", f"id: {tid}", "status: open", "deps: []", f"title: 'Planted ticket {tid} (W2-149 acceptance tests)'",
             f"role: {role}", f"wbs_id: {wbs}", "allowed_paths:"] + [f"- {p}" for p in paths]
    lines += ["kpis:", "  success:", f"  - 'S1 planted KPI line ({TICKET_MARK})'", "profile: LIGHT", "---",
              f"# Planted ticket {tid}", "", f"Its body ({TICKET_MARK}) never reaches a wall.", ""]
    return "\n".join(lines)


SETUP_A_FILES = {
    # S23: one file under each of the set-up A entries' tree_exclude globs (the template's and the briefs' are there)
    ".claude/settings.json": '{"permissions": {"deny": []}}\n',
    ".claude/hooks/pretooluse.py": "# planted guard hook (W2-149 S23)\n",
    "src/gov/guard/core.py": "# planted guard code (W2-149 S23)\n",
    "src/gov/launch/run.py": "# planted launcher code (W2-149 S23)\n",
}
SETUP_A_FILES.update({f".tickets/{t}.md": ticket_text(t, *v) for t, v in PLANTED_TICKETS.items()})
# S23 (F38): one file under each of the overlap auditor's further globs but .tickets/** (the tickets above), each
# holding TELL_MARK; tree-exclude.txt leaves none of them out, so every tree but the overlap auditor's holds them.
TELL_MARK = "TELL-W2149-WHICH-SIDE"
TELL_FILES = {
    "governance/project/orchestration/packages/ACT-W2-149-PLANTED.md": f"# planted package (W2-149 S23, {TELL_MARK})\n",
    "governance/project/orchestration/tools/indep_launch.py": f"# planted launcher (W2-149 S23, {TELL_MARK})\n",
    "tests/acceptance/W2-149/planted.md": f"# planted acceptance notes (W2-149 S23, {TELL_MARK})\n",
    "tests/unit/orchestration/test_w2_149_planted.py": f"# planted unit test (W2-149 S23, {TELL_MARK})\n",
    "docs/changes/W2-149-evidence.md": f"# planted evidence (W2-149 S23, {TELL_MARK})\n",
}
SETUP_A_FILES.update(TELL_FILES)
GIT_ENV = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_AUTHOR_NAME": "W2-149 tests",
           "GIT_AUTHOR_EMAIL": "w2-149@example.invalid", "GIT_COMMITTER_NAME": "W2-149 tests",
           "GIT_COMMITTER_EMAIL": "w2-149@example.invalid", "PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path) -> str:
    return sha256(Path(path).read_bytes())


def real_home() -> str:
    return pwd.getpwuid(os.getuid()).pw_dir


def git(repo, *args, raw=False):
    env = dict(GIT_ENV, HOME=str(repo))
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, env=env, timeout=60)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.decode(errors='replace')}")
    return p.stdout if raw else p.stdout.decode()


def next_second():
    """Wait until the UTC second changes, so the next launch of the same kind, set and round gets a new run id."""
    now = int(time.time())
    while int(time.time()) == now:
        time.sleep(0.02)


def make_writable(root):
    """Teardown: the walls' and trees' read-only modes would stop the temporary folder's removal."""
    for dp, dn, fn in os.walk(root):
        for name in dn + fn:
            p = os.path.join(dp, name)
            try:
                if not os.path.islink(p):
                    os.chmod(p, 0o700 if os.path.isdir(p) else 0o600)
            except OSError:
                pass
    try:
        os.chmod(root, 0o700)
    except OSError:
        pass


def excluded(rel: str, globs) -> bool:
    """The exclusion rule as the rehearsal's walls_check.py applies it (fnmatch on the repository-relative path)."""
    return any(fnmatch.fnmatch(rel, g) for g in globs)


# -- the planted repository ---------------------------------------------------------------------------------------

def brief_text(kind, sample, model=STUB_MODEL, budget=None, timeout=None, body=None):
    lines = ["---", f"kind: {kind}", f"sample: {sample}", f"model: {model}",
             f"result_schema: {kind}-result.schema.json"]
    if budget is not None:
        lines.append(f"budget_usd: {budget}")
    if timeout is not None:
        lines.append(f"timeout_s: {timeout}")
    lines += ["---", "", body or f"# The planted {kind} brief (W2-149 acceptance tests)\n\nFollow this folder's rules "
              "and write out/result.json in the schema named above.", ""]
    return "\n".join(lines)


BRIEFS = {"writer": brief_text("writer", 5, budget=0.5, timeout=30),
          "checker": brief_text("checker", 3),
          "auditor": brief_text("auditor", 3, budget=0.5, timeout=30),
          "labeller": brief_text("labeller", 3, budget=0.5, timeout=30),
          "writer-short": brief_text("writer", 5, budget=0.5, timeout=2),
          "writer-overbudget": brief_text("writer", 5, budget=99, timeout=30)}
# Set-up A (DEC-1112 (3)): the five approved briefs' front matter byte for byte, each with a planted body, at the
# approved briefs' own paths (governance/project/indep-briefs/sgx1/<name>.md); and S22's variants.
BRIEFS.update({f"sgx1/{name}": fm + SGX1_BODY for name, fm in SGX1_FRONT.items()})
BRIEFS.update({name: fm + SGX1_BODY for name, fm in SGX1_VARIANTS.items()})


def flip_last_letter(data: bytes) -> bytes:
    """One changed byte: the last ASCII letter's case swapped."""
    for i in range(len(data) - 1, -1, -1):
        c = data[i]
        if 65 <= c <= 90 or 97 <= c <= 122:
            return data[:i] + bytes([c ^ 0x20]) + data[i + 1:]
    raise ValueError("no letter to change")


def bash_in_kinds(data: bytes) -> bytes:
    text = data.decode()
    old = "tools: [Read, Grep, Glob, Write, Edit, TodoWrite]"
    assert old in text, "the template's writer tools line moved"
    return text.replace(old, "tools: [Read, Grep, Glob, Write, Edit, TodoWrite, Bash]", 1).encode()


def corrupt_settings(data: bytes) -> bytes:
    """One key corrupted: hooks.PreToolUse a string, not a list (Claude Code's -p ignores such a file)."""
    doc = json.loads(data)
    doc["hooks"]["PreToolUse"] = "python3 -I @WALL@/.claude/wall_hook.py @WALL@ @TREE@"
    return (json.dumps(doc, indent=2) + "\n").encode()


def path_map_without_the_set(data: bytes) -> bytes:
    """PU (S24): the path map holds no sandbox-guard-exp-1 evaluation set (sets_root_hidden still names its glob)."""
    text = data.decode()
    assert SGX_SET_BLOCK in text
    return text.replace(SGX_SET_BLOCK, "evaluation_sets: {}\n", 1).encode()


def path_map_without_the_cover(data: bytes) -> bytes:
    """PC (S24): the set's entry stays; sets_root_hidden no longer covers its hidden glob."""
    text = data.decode()
    head, sep, tail = text.partition("sets_root_hidden:")
    assert sep and SGX_HIDDEN_GLOB in tail
    return (head + sep + tail.replace(SGX_HIDDEN_GLOB, "", 1)).encode()


def base_files(extra_briefs=None):
    files = {"README.md": "# The planted repository (W2-149 acceptance tests)\n",
             "CLAUDE.md": "Planted CLAUDE.md of the planted repository.\n",
             "tools/run.sh": "#!/bin/sh\necho planted\n",
             "governance/project/path-map.yaml": PATH_MAP,
             # excluded from every tree (tree-exclude.txt)
             "fixtures/evaluation/memory-verdict-3/visible.md": "excluded: the evaluation sets\n",
             ".gov-runtime/notes.md": "excluded: the runtime scratch (DUMMY MARK-OUTSIDE-09 the CTO scratch)\n",
             "docs/audit/memory-measure-a.md": "excluded: a measure audit\n",
             "tests/acceptance/W2-61/test_x.py": "# excluded: W2-61's tests\n",
             "docs/research/EXP-003/r.md": "excluded: EXP-003\n"}
    for n in range(1, 21):
        files[f"docs/d{n:02d}.md"] = f"# Planted doc {n}\nplanted line {n}\n"
    for n in range(1, 11):
        files[f"src/pkg/m{n:02d}.py"] = f"VALUE = {n}\n"
    for name in TEMPLATE_FILES:
        files[f"{TEMPLATE_REL}/{name}"] = (TEMPLATE_SRC / name).read_bytes()
    # set-up A's wiring: the planted kinds.yaml (a model per kind, the briefs: map); tree-exclude.txt stays the tree's
    files[f"{TEMPLATE_REL}/kinds.yaml"] = KINDS_YAML
    files.update(SETUP_A_FILES)
    for name, text in dict(BRIEFS, **(extra_briefs or {})).items():
        files[f"{BRIEFS_REL}/{name}.md"] = text
    return files


def _write(root: Path, rel: str, data):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.is_symlink():
        p.unlink()
    p.write_bytes(data if isinstance(data, bytes) else data.encode())


def _commit(root, message):
    git(root, "add", "-A")
    git(root, "commit", "-q", "--no-gpg-sign", "-m", message)
    return git(root, "rev-parse", "HEAD").strip()


def build_repo(root: Path, extra_briefs=None) -> dict:
    """The planted repository. On ``w2/integrate``: A (the last audit's commit), L (adds a symlink), B (the commit
    most cases launch at: the link gone, a few paths changed), then one commit per single change from B's tree
    (TB: one byte of writer.md; T-<file>: one byte of each template file; TK: Bash in the writer's tools; TS: one
    settings key corrupted), then Z (B's tree again, the head). ``side`` holds S, a child of B not reachable from
    ``w2/integrate``."""
    root.mkdir(parents=True)
    git(root, "init", "-q")
    git(root, "checkout", "-q", "-b", "w2/integrate")
    files = base_files(extra_briefs)
    for rel, data in files.items():
        _write(root, rel, data)
    os.chmod(root / "tools/run.sh", 0o755)
    shas = {"A": _commit(root, "A: the planted base (the last audit)")}
    os.symlink("../README.md", root / "docs/link.md")
    shas["L"] = _commit(root, "L: a symlink in the tree")
    (root / "docs/link.md").unlink()
    _write(root, "docs/d03.md", "# Planted doc 3\nchanged after the audit\n")
    _write(root, "src/pkg/m02.py", "VALUE = 222\n")
    _write(root, "docs/new.md", "# A doc added after the audit\n")
    _write(root, "fixtures/evaluation/memory-verdict-3/visible.md", "excluded, and changed\n")
    _write(root, ".gov-runtime/notes.md", "excluded, and changed (DUMMY MARK-OUTSIDE-09 the CTO scratch)\n")
    _write(root, "docs/audit/memory-measure-b.md", "excluded, and added\n")
    shas["B"] = _commit(root, "B: the commit the cases launch at")
    b_bytes = {}
    variants = [("TB", f"{BRIEFS_REL}/writer.md", flip_last_letter)]
    variants += [(f"T-{name}", f"{TEMPLATE_REL}/{name}", flip_last_letter) for name in TEMPLATE_FILES]
    variants += [("TK", f"{TEMPLATE_REL}/kinds.yaml", bash_in_kinds),
                 ("TS", f"{TEMPLATE_REL}/settings.json.tmpl", corrupt_settings),
                 ("PU", "governance/project/path-map.yaml", path_map_without_the_set),
                 ("PC", "governance/project/path-map.yaml", path_map_without_the_cover)]
    previous = None
    for key, rel, change in variants:
        if previous:
            _write(root, previous, b_bytes[previous])
        b_bytes.setdefault(rel, (root / rel).read_bytes())
        _write(root, rel, change(b_bytes[rel]))
        shas[key] = _commit(root, f"{key}: one change from B ({rel})")
        previous = rel
    _write(root, previous, b_bytes[previous])
    shas["Z"] = _commit(root, "Z: B's tree again (the head)")
    git(root, "checkout", "-q", "-b", "side", shas["B"])
    _write(root, "docs/side.md", "# On a side branch only\n")
    shas["S"] = _commit(root, "S: not reachable from w2/integrate")
    git(root, "checkout", "-q", "w2/integrate")
    briefs = dict(BRIEFS, **(extra_briefs or {}))
    return {"path": str(root.resolve()), "shas": shas, "briefs": sorted(briefs),
            "brief_kind": {n: re.search(r"^kind: (\w+)$", t, re.M).group(1) for n, t in briefs.items()}}


# -- the stub claude and the test hook ----------------------------------------------------------------------------

STUB = r'''#!__PY__ -I
"""The W2-149 stub `claude` (acceptance tests only). It records each call (argv, cwd, environment, process ids,
stdin, its parent's command line) and plays Claude Code:
  - the canary is the call whose prompt names an existing file by its absolute path (the launch prompt names none);
  - --restricted refuses a Read outside the session's folder and every --add-dir folder;
  - a --settings file it cannot read, parse or validate is ignored without a word;
  - with the settings loaded, the Read is refused only when a PreToolUse hook in them refuses it (run as Claude Code
    runs a command hook: sh -c, the event on stdin, exit 2 or a "deny" decision refuses);
  - the real session plays the case's script (out/ files, a sleep, a child, the budget's end, a trace file);
  - the user's settings source (S10, DEC-1112 (3)): with no --setting-sources, or a list naming "user", it loads
    $HOME/.claude/settings.json when that file is valid: its SessionStart hooks run at every call's start and its
    PreToolUse hooks run beside the --settings file's on the canary's Read (allow lines never lift a refusal: Claude
    Code's deny-over-allow); a list that leaves "user" out loads nothing from it. Each call records which."""
import hashlib, json, os, re, subprocess, sys, time, uuid

CFG = __CFG__
REC = __REC__
VALUE = {"--settings", "--tools", "--model", "--max-budget-usd", "--output-format", "--permission-prompts",
         "--max-turns", "--setting-sources", "--allowedTools", "--allowed-tools", "--disallowedTools",
         "--disallowed-tools", "--system-prompt", "--append-system-prompt", "--mcp-config", "--permission-mode",
         "--session-id", "--fallback-model", "--input-format"}
MODES = {"default", "acceptEdits", "plan", "bypassPermissions", "dontAsk"}


def parse(argv):
    flags, adds, rest, i = {}, [], [], 0
    while i < len(argv):
        a = argv[i]
        name, eq, val = a.partition("=")
        if name == "--add-dir":
            if eq:
                adds.append(val)
                i += 1
                continue
            i += 1
            if i < len(argv):
                adds.append(argv[i])
                i += 1
            while i < len(argv) and not argv[i].startswith("-") and os.path.isdir(argv[i]):
                adds.append(argv[i])
                i += 1
            continue
        if a.startswith("--") and name in VALUE:
            if eq:
                flags[name] = val
                i += 1
            else:
                flags[name] = argv[i + 1] if i + 1 < len(argv) else None
                i += 2
            continue
        if a.startswith("-"):
            flags[a] = True
            i += 1
            continue
        rest.append(a)
        i += 1
    return flags, adds, (rest[-1] if rest else None)


def target_of(prompt):
    for m in re.finditer(r"(?:^|(?<=[\s'\"`(]))(/[^\s'\"`]+)", prompt or ""):
        t = m.group(1).rstrip(".,;:)!?")
        if os.path.isfile(t):
            return t
    return None


def inside(p, d):
    return p == d or p.startswith(d.rstrip("/") + "/")


def settings_ok(path):
    try:
        with open(path) as f:
            d = json.load(f)
    except Exception:
        return None
    if not isinstance(d, dict):
        return None
    p = d.get("permissions", {})
    if not isinstance(p, dict):
        return None
    for k in ("allow", "deny", "ask"):
        if k in p and not (isinstance(p[k], list) and all(isinstance(x, str) for x in p[k])):
            return None
    if "defaultMode" in p and p["defaultMode"] not in MODES:
        return None
    if "disableBypassPermissionsMode" in p and p["disableBypassPermissionsMode"] != "disable":
        return None
    if "model" in d and not isinstance(d["model"], str):
        return None
    h = d.get("hooks", {})
    if not isinstance(h, dict):
        return None
    for entries in h.values():
        if not isinstance(entries, list):
            return None
        for e in entries:
            if not isinstance(e, dict) or not isinstance(e.get("hooks"), list):
                return None
            if "matcher" in e and not isinstance(e["matcher"], str):
                return None
            for x in e["hooks"]:
                if not isinstance(x, dict) or x.get("type") != "command" or not isinstance(x.get("command"), str):
                    return None
                if "timeout" in x and (isinstance(x["timeout"], bool) or not isinstance(x["timeout"], (int, float))):
                    return None
    for k, t in (("enableAllProjectMcpServers", bool), ("cleanupPeriodDays", int)):
        if k in d and not isinstance(d[k], t):
            return None
    return d


def hook_denies(settings, tool, tin, cwd, sid):
    for e in settings.get("hooks", {}).get("PreToolUse", []):
        m = e.get("matcher", "")
        if m not in ("", "*"):
            try:
                if not re.fullmatch(m, tool):
                    continue
            except re.error:
                continue
        for x in e["hooks"]:
            event = {"session_id": sid, "transcript_path": "", "cwd": cwd, "hook_event_name": "PreToolUse",
                     "tool_name": tool, "tool_input": tin}
            try:
                p = subprocess.run(["/bin/sh", "-c", x["command"]], input=json.dumps(event), capture_output=True,
                                   text=True, cwd=cwd, timeout=x.get("timeout", 60))
            except Exception:
                continue  # a hook that cannot run is a non-blocking error in Claude Code
            if p.returncode == 2:
                return True
            if p.returncode == 0 and p.stdout.strip():
                try:
                    out = json.loads(p.stdout)
                except Exception:
                    continue
                if (out.get("hookSpecificOutput") or {}).get("permissionDecision") == "deny":
                    return True
    return False


def user_source(flags):
    """The user's settings source: on with no --setting-sources or a list naming "user"; its file loaded when valid."""
    src = flags.get("--setting-sources")
    on = src is None or "user" in [x.strip() for x in str(src).split(",")]
    path = os.path.join(os.environ.get("HOME", "/nonexistent"), ".claude", "settings.json")
    present = os.path.isfile(path)
    loaded = settings_ok(path) if (on and present) else None
    return {"sources": src, "user_on": on, "path": path, "present": present, "loaded": loaded is not None}, loaded


def run_hooks(settings, event_name, cwd, sid, **extra):
    for e in settings.get("hooks", {}).get(event_name, []):
        for x in e["hooks"]:
            event = dict({"session_id": sid, "transcript_path": "", "cwd": cwd, "hook_event_name": event_name}, **extra)
            try:
                subprocess.run(["/bin/sh", "-c", x["command"]], input=json.dumps(event), capture_output=True,
                               text=True, cwd=cwd, timeout=x.get("timeout", 60))
            except Exception:
                pass


def record(name, data):
    with open(os.path.join(REC, name), "a") as f:
        f.write(json.dumps(data) + "\n")


# Set-up A's sessions (DEC-1112 (3)): a program reads the wall's own input/ and writes what the brief asks, so a real
# run (whose seed the script draws) still answers its own staged ids. Each returns {out/ file: text}.
LABELS = ("allow", "refuse", "ask")


def _jsonl(path):
    with open(path) as f:
        return [json.loads(x) for x in f if x.strip()]


def _by_class(lines):
    return {str(k): sum(1 for x in lines if str(x["rule_class"]) == str(k)) for k in range(1, 15)}


def _class_forms(lines, a):
    """S31: ``class_form`` "str" writes every rule_class as its decimal string; ``bad_class`` (JSON text) replaces the
    first line's rule_class with that value."""
    if a.get("class_form") == "str":
        for x in lines:
            x["rule_class"] = str(x["rule_class"])
    if a.get("bad_class") is not None and lines:
        lines[0]["rule_class"] = json.loads(a["bad_class"])
    return lines


def prog_hand_labels(cwd, a):
    """Labeller 1, round 2: a hand label for every id the script marked uncertain, put in classes 1-13, or drew in
    the sample (``drop``: leave out the required id at that index; ``extra``: also label that many other ids;
    ``class_form``/``bad_class``: S31's forms)."""
    script = _jsonl(os.path.join(cwd, "input", "script-labels.jsonl"))
    with open(os.path.join(cwd, "input", "sample.json")) as f:
        sample = set(json.load(f)["ids"])
    need = [x["id"] for x in script if x["uncertain"] or 1 <= int(x["rule_class"]) <= 13 or x["id"] in sample]
    more = [x["id"] for x in script if x["id"] not in need][:a.get("extra", 0)]
    if a.get("drop") is not None:
        need = need[:a["drop"]] + need[a["drop"] + 1:]
    by = {x["id"]: x for x in script}
    lines = [{"id": i, "label": "refuse" if by[i]["label"] == "allow" else "allow", "rule_class": 11,
              "clauses": ["DEC-820 (4)"], "reason": "names docs/ and DEC-820 (4) only"} for i in need + more]
    lines = _class_forms(lines, a)
    result = {"round": 2, "hand_labelled": len(lines), "allow": sum(x["label"] == "allow" for x in lines),
              "refuse": sum(x["label"] == "refuse" for x in lines), "ask": 0, "by_class": _by_class(lines),
              "uncertain_seen": sum(1 for x in script if x["uncertain"]), "sample": len(sample),
              "instructions_ignored": 0, "stopped": "none"}
    return {"hand-labels.jsonl": "".join(json.dumps(x) + "\n" for x in lines), "result.json": json.dumps(result)}


def prog_labels2(cwd, a):
    """Labeller 2, round 2: one hand label per line of input/sample.jsonl (``bad``: S30's broken files;
    ``class_form``/``bad_class``: S31's forms)."""
    sample = _jsonl(os.path.join(cwd, "input", "sample.jsonl"))
    lines = [{"id": x["id"], "label": LABELS[k % 3], "rule_class": 11 if k % 3 else 14, "clauses": ["DEC-820 (4)"],
              "how": "hand", "reason": "names docs/ and DEC-820 (4) only"} for k, x in enumerate(sample)]
    lines = _class_forms(lines, a)
    bad = a.get("bad")
    if bad == "missing":
        lines = lines[:-1]
    elif bad == "extra":
        lines = lines + [dict(lines[0], id="x-a998-not-in-the-sample")]
    elif bad == "repeat":
        lines = lines + [dict(lines[0])]
    elif bad == "label":
        lines[0]["label"] = "maybe"
    elif bad == "how":
        lines[0]["how"] = "script"
    elif bad == "clauses":
        lines[0]["clauses"] = "DEC-820 (4)"
    result = {"round": 2, "sample": len(sample), "labelled": len(lines),
              "allow": sum(x["label"] == "allow" for x in lines), "refuse": sum(x["label"] == "refuse" for x in lines),
              "ask": sum(x["label"] == "ask" for x in lines), "by_class": _by_class(lines), "instructions_ignored": 0,
              "stopped": "none"}
    return {"labels-2.jsonl": "".join(json.dumps(x) + "\n" for x in lines), "result.json": json.dumps(result)}


def prog_decide(cwd, a):
    """The overlap auditor: one decision per case of input/disputes.jsonl, in order; by index mod 5: agrees x, agrees
    y, neither (the third label), x flagged cannot-settle, y flagged may-change-verdict. ``bad`` breaks the file."""
    cases = _jsonl(os.path.join(cwd, "input", "disputes.jsonl"))
    out = []
    for i, c in enumerate(cases):
        m = i % 5
        pick, agree = {0: (c["x"], "x"), 1: (c["y"], "y"), 3: (c["x"], "x"), 4: (c["y"], "y")}.get(m, (None, "neither"))
        label = pick["label"] if pick else [x for x in LABELS if x not in (c["x"]["label"], c["y"]["label"])][0]
        flag = {3: "cannot-settle", 4: "may-change-verdict"}.get(m, "none")
        out.append({"id": c["id"], "label": label, "rule_class": int(pick["rule_class"]) if pick else 9,
                    "basis": ["DEC-1113 (2)", "DEC-820 (4)"], "agrees_with": agree, "flag": flag,
                    "reason": "" if flag == "none" else "DEC-820 (4) against DEC-1093 (2) on docs/ only"})
    out = _class_forms(out, a)
    bad = a.get("bad")
    if bad == "drop_last":
        out = out[:-1]
    elif bad == "swap":
        out[0], out[1] = out[1], out[0]
    elif bad == "reason_on_none":
        next(x for x in out if x["flag"] == "none")["reason"] = "a reason on a case flagged none"
    elif bad == "flag_word":
        out[0]["flag"] = "unsure"
    result = {"cases": len(cases), "decided": len(out), "allow": sum(x["label"] == "allow" for x in out),
              "refuse": sum(x["label"] == "refuse" for x in out), "ask": sum(x["label"] == "ask" for x in out),
              "agrees_x": sum(x["agrees_with"] == "x" for x in out), "agrees_y": sum(x["agrees_with"] == "y" for x in out),
              "neither": sum(x["agrees_with"] == "neither" for x in out),
              "cannot_settle": sum(x["flag"] == "cannot-settle" for x in out),
              "may_change_verdict": sum(x["flag"] == "may-change-verdict" for x in out), "by_class": _by_class(out),
              "instructions_ignored": 0, "stopped": "none"}
    return {"decisions.jsonl": "".join(json.dumps(x) + "\n" for x in out), "result.json": json.dumps(result)}


PROGRAMS = {"hand_labels": prog_hand_labels, "labels2": prog_labels2, "decide": prog_decide}


def main():
    argv = sys.argv[1:]
    with open(CFG) as f:
        cfg = json.load(f)
    flags, adds, prompt = parse(argv)
    cwd = os.getcwd()
    target = target_of(prompt)
    canary = target is not None
    try:
        with open("/proc/%d/cmdline" % os.getppid(), "rb") as f:
            parent = [x.decode(errors="replace") for x in f.read().split(b"\0") if x]
    except OSError:
        parent = []
    try:
        devnull = os.path.samestat(os.fstat(0), os.stat(os.devnull))
    except OSError:
        devnull = False
    listing = {}
    for dp, _dn, fn in os.walk(os.path.join(cwd, "input")):
        for n in fn:
            fp = os.path.join(dp, n)
            with open(fp, "rb") as f:
                listing[os.path.relpath(fp, os.path.join(cwd, "input"))] = hashlib.sha256(f.read()).hexdigest()
    sid = (cfg.get("canary_session_id") if canary else (cfg.get("session") or {}).get("session_id")) \
        or str(uuid.uuid4())
    user_rec, user = user_source(flags)
    record("calls.jsonl", {"argv": argv, "flags": flags, "adds": adds, "prompt": prompt, "cwd": cwd,
                           "env": dict(os.environ), "pid": os.getpid(), "pgid": os.getpgrp(), "ppid": os.getppid(),
                           "parent": parent, "stdin_devnull": devnull, "canary": canary, "target": target,
                           "input": listing, "session_id": sid, "user_settings": user_rec, "t": time.time_ns()})
    if user is not None:
        run_hooks(user, "SessionStart", cwd, sid, source="startup")
    if canary:
        mode = cfg.get("canary", "model")
        if mode == "sleep":
            time.sleep(cfg.get("canary_sleep", 30))
        if mode == "garbage":
            sys.stdout.write("this is not the JSON of a result\n")
            return 0
        settings = flags.get("--settings")
        loaded = settings_ok(os.path.join(cwd, settings)) if isinstance(settings, str) else None
        rt = os.path.realpath(target)
        dirs = [os.path.realpath(cwd)] + [os.path.realpath(os.path.join(cwd, d)) for d in adds]
        why = None
        if flags.get("--restricted") and not any(inside(rt, d) for d in dirs):
            why = "restricted"
        elif any(s is not None and hook_denies(s, "Read", {"file_path": target}, cwd, sid) for s in (user, loaded)):
            why = "hook"
        denials = [{"tool_name": "Read", "tool_use_id": "toolu_stub_canary", "tool_input": {"file_path": target}}] \
            if why else []
        if mode == "wrong_denial":
            denials = [{"tool_name": "Read", "tool_use_id": "toolu_stub_other",
                        "tool_input": {"file_path": "/etc/hostname"}}]
        record("outcomes.jsonl", {"pid": os.getpid(), "canary": True, "settings_loaded": loaded is not None,
                                  "user_settings_loaded": user is not None, "why": why, "mode": mode})
        print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "session_id": sid,
                          "num_turns": 2, "total_cost_usd": 0.0005, "duration_ms": 40,
                          "permission_denials": denials, "result": "done"}))
        return 0
    s = cfg.get("session")
    if s is None:
        record("outcomes.jsonl", {"pid": os.getpid(), "canary": False, "tripwire": True})
        sys.stderr.write("W2-149 stub: no session was expected in this case\n")
        return 97
    if s.get("trace"):
        d = os.path.join(os.environ.get("HOME", "/nonexistent"), ".claude", "projects", "-w2-149-stub")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, sid + ".jsonl"), "w") as f:
            f.write("{}\n")
    if s.get("child"):
        c = subprocess.Popen(["sleep", "300"])
        with open(os.path.join(REC, "child.pid"), "w") as f:
            f.write(str(c.pid))
    if s.get("sleep"):
        time.sleep(s["sleep"])
    files = dict(s.get("out") or {})
    if s.get("program"):
        files.update(PROGRAMS[s["program"]](cwd, s.get("program_args") or {}))
        extra = (s.get("program_args") or {}).get("extra_result")
        if extra:
            files["result.json"] = json.dumps(dict(json.loads(files["result.json"]), **extra))
    for rel, text in files.items():
        p = os.path.join(cwd, "out", rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(text)
    budget = bool(s.get("budget"))
    print(json.dumps({"type": "result", "subtype": "error_max_budget_usd" if budget else "success",
                      "is_error": budget, "session_id": sid, "num_turns": 3, "total_cost_usd": 0.0123,
                      "duration_ms": 2345, "permission_denials": s.get("denials") or [],
                      "result": s.get("result", "done")}))
    sys.stdout.flush()
    record("outcomes.jsonl", {"pid": os.getpid(), "canary": False, "budget": budget})
    return 1 if budget else 0


if __name__ == "__main__":
    sys.exit(main())
'''

HOOK = r'''#!__PY__ -I
"""The W2-149 test hook (GOV_INDEP_TEST_HOOK): run by the launch script as <hook> <point> <wall> <tree>."""
import json, os, sys, time

CFG = __CFG__


def main():
    with open(CFG) as f:
        cfg = json.load(f)
    point, wall, tree = (sys.argv[1:4] + ["", "", ""])[:3]
    with open(cfg["record"], "a") as f:
        f.write(json.dumps({"point": point, "wall": wall, "tree": tree, "t": time.time_ns()}) + "\n")
    for act in cfg.get("actions", {}).get(point, []):
        op = act["op"]
        if op == "write":
            p = os.path.join(wall if act["where"] == "wall" else tree, act["rel"])
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                f.write(act["text"])
        elif op == "future_mtime":
            t = time.time_ns() + 5_000_000_000
            os.utime(os.path.join(wall, act["rel"]), ns=(t, t))
        elif op == "drop_ledger_line":
            path, run = cfg["ledger"], os.path.basename(wall)
            mode = os.stat(path).st_mode
            os.chmod(path, 0o600)
            with open(path) as f:
                keep = [line for line in f if run not in line]
            with open(path, "w") as f:
                f.writelines(keep)
            os.chmod(path, mode & 0o7777)
        elif op == "mark":
            with open(act["file"], "w") as f:
                f.write(str(time.time_ns()))
        elif op == "newer":
            with open(act["mark"]) as f:
                mark = int(f.read())
            kind, run = os.path.basename(os.path.dirname(wall)), os.path.basename(wall)
            skip = [os.path.join(wall, "out") + "/", wall + ".session.json",
                    os.path.join(cfg["runs"], kind, run) + "/"] + [s.rstrip("/") + "/" for s in act.get("skip", [])]
            found = []
            for root in act["roots"]:
                for dp, dn, fn in os.walk(root):
                    for n in fn:
                        fp = os.path.join(dp, n)
                        if any((fp + "/").startswith(s) or fp == s.rstrip("/") for s in skip):
                            continue
                        try:
                            if os.lstat(fp).st_mtime_ns > mark:
                                found.append(fp)
                        except OSError:
                            pass
            with open(act["out"], "w") as f:
                json.dump(found, f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def _program(path: Path, template: str, **values):
    text = template.replace("__PY__", sys.executable)
    for k, v in values.items():
        text = text.replace(f"__{k}__", repr(str(v)))
    path.write_text(text)
    os.chmod(path, 0o755)


# -- outputs a session may leave in out/ --------------------------------------------------------------------------

GOOD_RESULT = {"writer": {"questions": 3, "by_kind": {"fact": 2, "procedure": 1}, "by_area": {"code": 2, "docs": 1}},
               "checker": {"checked": 3, "accepted": 2, "revise": 1, "rejected": 0},
               "auditor": {"misses": {"retrieval_miss": 2, "gold_wrong": 1}},
               "labeller": {"labelled": 23, "allow": 20, "refuse": 3}}
GOOD_DELIVERY = {"writer": {"set/q01.yaml": "id: q01\nquestion: planted one\n",
                            "set/q02.yaml": "id: q02\nquestion: planted two\n",
                            "set/sub/q03.yaml": "id: q03\nquestion: planted three\n"},
                 "checker": {"notes.md": "# Cross-check notes (planted)\n- q01 accepted\n"},
                 "auditor": {"classes.json": json.dumps({"m1": "retrieval_miss", "m2": "retrieval_miss",
                                                         "m3": "gold_wrong"})},
                 "labeller": {"labels.jsonl": "".join(json.dumps({"id": f"a{n:02d}", "label": "allow"}) + "\n"
                                                      for n in range(1, 24))}}


def good_out(kind, **extra_result):
    out = {"result.json": json.dumps(dict(GOOD_RESULT[kind], **extra_result))}
    out.update(GOOD_DELIVERY[kind])
    return out


def bundle_sha(kind, files: dict) -> str:
    """The delivered bundle's sha256 (README): one file's own sha256; the writer's set the sha256 of its manifest,
    the lines "<file sha256>  <path relative to out/set/>\\n" sorted by path."""
    if kind != "writer":
        (data,) = files.values()
        return sha256(data)
    lines = "".join(f"{sha256(files[rel])}  {rel}\n" for rel in sorted(files))
    return sha256(lines.encode())


# -- the run of the script ----------------------------------------------------------------------------------------

class Run:
    def __init__(self, code, out, err):
        self.code, self.out, self.err = code, out, err
        self.line = None
        lines = [x for x in out.strip().splitlines() if x.strip()]
        if lines:
            try:
                parsed = json.loads(lines[-1])
                self.line = parsed if isinstance(parsed, dict) else None
            except ValueError:
                pass

    def why(self):
        return f"exit {self.code}; last stdout: {self.out[-600:]!r}; stderr: {self.err[-1500:]!r}"


class World:
    """One case's planted world: HOME (its runs and trees folders), the sets root, the stub's folder and records.
    ``live``: the real HOME (the session's login), the runs and trees folders by the two overrides, the sets root under
    the case's temporary folder."""

    def __init__(self, tmp: Path, repo: dict | None, base: Path, live=False):
        self.tmp = Path(os.path.realpath(tmp))
        self.base = Path(os.path.realpath(base))
        self.live = live
        if live:
            self.home = Path(os.path.realpath(real_home()))
            self.sr = self.tmp / "eval"
            self.runs_root = self.tmp / "runs"
            self.trees = self.tmp / "trees"
        else:
            self.home = self.tmp / "home"
            self.sr = self.home / "gov-os-eval"
            self.runs_root = self.home / "gov-os-runs"
            self.trees = self.home / "gov-os-wall-trees"
        self.runs = self.runs_root / "indep"
        self.walls = self.sr / "indep-walls"
        self.bin, self.rec, self.scratch = self.tmp / "bin", self.tmp / "rec", self.tmp / "t"
        self.hooks = 0
        self.repo = None
        if repo is not None:
            self.attach(repo)

    def attach(self, repo):
        self.repo = repo
        self.repo_path = Path(repo["path"])
        self._blobs = {}

    # git at the planted repository
    def sha(self, key):
        return self.repo["shas"].get(key, key)

    def blob(self, key, rel) -> bytes:
        k = (key, rel)
        if k not in self._blobs:
            self._blobs[k] = git(self.repo_path, "show", f"{self.sha(key)}:{rel}", raw=True)
        return self._blobs[k]

    def brief_sha(self, name, key="B"):
        return sha256(self.blob(key, f"{BRIEFS_REL}/{name}.md"))

    def tracked(self, key="B"):
        return [p for p in git(self.repo_path, "ls-tree", "-r", "--name-only", "-z", self.sha(key)).split("\0") if p]

    def exclusions(self, key="B"):
        text = self.blob(key, f"{TEMPLATE_REL}/tree-exclude.txt").decode()
        return [x.strip() for x in text.splitlines() if x.strip() and not x.strip().startswith("#")]

    # planting
    def plant(self):
        for d in (self.home, self.sr, self.runs, self.trees, self.bin, self.rec, self.scratch):
            d.mkdir(parents=True, exist_ok=True)
        actions1 = "".join(json.dumps({"id": f"a{n:02d}", "tool": "Bash", "input": f"ls docs/a{n:02d}"},
                                      sort_keys=True) + "\n" for n in range(1, 24))
        actions2 = "".join(json.dumps({"id": f"b{n:02d}", "tool": "Read", "input": f"docs/b{n:02d}.md"},
                                      sort_keys=True) + "\n" for n in range(1, 13))
        files = {"fixtures/evaluation/memory-verdict-2/hidden/p01.yaml": "DUMMY MARK-OUTSIDE-04 a hidden set file\n",
                 "fixtures/evaluation/memory-verdict-3/hidden/q01.yaml": "id: q01\nquestion: planted set one\n",
                 "fixtures/evaluation/memory-verdict-3/hidden/q02.yaml": "id: q02\nquestion: planted set two\n",
                 "fixtures/evaluation/memory-verdict-3/hidden/sub/q03.yaml": "id: q03\nquestion: planted three\n",
                 f"{SEALED}/rulebook.md": "# The planted rulebook (SANDBOX-GUARD-EXP-1 stand-in)\n",
                 f"{SEALED}/corpus/actions-r1.jsonl": actions1,
                 f"{SEALED}/corpus/actions-r2.jsonl": actions2,
                 f"{SEALED}/corpus/zz-marker.jsonl": "DUMMY MARK-OUTSIDE-05 the sealed folder\n",
                 f"{SEALED}/labels/planted.jsonl": "{}\n",
                 "runs/audit-1/misses.jsonl": "".join(json.dumps({"id": f"m{n}", "question": "planted",
                                                                  "gold": "x", "answer": "y"}) + "\n"
                                                      for n in (1, 2, 3)),
                 "runs/e0/counts.txt": "DUMMY MARK-OUTSIDE-06 a run folder\n",
                 "transcripts/t01.md": "DUMMY MARK-OUTSIDE-07 a transcript\n"}
        for rel, text in files.items():
            _write(self.sr, rel, text)
        self.walls.mkdir(exist_ok=True)
        os.chmod(self.walls, 0o700)
        if self.repo is not None:
            self.approve()
            (self.runs / "AUDITS.log").write_text(json.dumps(
                {"time": "2026-11-01T00:00:00Z", "commit": self.sha("A"), "run": "planted", "audit": "planted"}) + "\n")
        if not self.live:
            _write(self.home, ".claude/projects/-planted/other-session-id.jsonl", "{}\n")
        self.write_stub()

    def approve(self, template=None, briefs=None, drop_kind=None, extra=()):
        """``<sets root>/indep-walls/APPROVED`` in the owner's list's form; every template file as at B unless
        ``template`` names another commit for it; a ``brief`` line for each planted brief."""
        template = template or {}
        lines = ["# APPROVED, planted by the W2-149 acceptance tests (the owner's list's form)"]
        for name in TEMPLATE_FILES:
            data = self.blob(template.get(name, "B"), f"{TEMPLATE_REL}/{name}")
            lines.append(f"{sha256(data)}  template {TEMPLATE_REL}/{name}")
        for b in (self.repo["briefs"] if briefs is None else briefs):
            kind = self.repo["brief_kind"][b]
            if kind != drop_kind:
                lines.append(f"{self.brief_sha(b)}  brief {kind} {BRIEFS_REL}/{b}.md")
        lines += list(extra)
        p = self.walls / "APPROVED"
        if p.exists():
            os.chmod(p, 0o600)
        p.write_text("\n".join(lines) + "\n")
        os.chmod(p, 0o400)

    def approved_sha(self):
        return sha_file(self.walls / "APPROVED")

    def write_stub(self, canary="model", session=None, **more):
        cfg = dict(more, canary=canary, session=session)
        (self.rec / "stub.json").write_text(json.dumps(cfg))
        stub = self.bin / "claude"
        if not stub.exists():
            _program(stub, STUB, CFG=self.rec / "stub.json", REC=self.rec)

    def write_hook(self, actions) -> dict:
        self.hooks += 1
        cfg = self.rec / f"hook-{self.hooks}.json"
        record = self.rec / f"hook-{self.hooks}.jsonl"
        cfg.write_text(json.dumps({"record": str(record), "actions": actions, "ledger": str(self.ledger),
                                   "runs": str(self.runs)}))
        path = self.bin.parent / f"test-hook-{self.hooks}"
        _program(path, HOOK, CFG=cfg)
        self.last_hook_record = record
        return {"GOV_INDEP_TEST_HOOK": str(path)}

    def hook_points(self):
        p = getattr(self, "last_hook_record", None)
        if p is None or not p.exists():
            return []
        return [json.loads(x)["point"] for x in p.read_text().splitlines() if x.strip()]

    def calls(self):
        p = self.rec / "calls.jsonl"
        return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []

    def session_calls(self):
        return [c for c in self.calls() if not c["canary"]]

    def canary_calls(self):
        return [c for c in self.calls() if c["canary"]]

    @property
    def ledger(self):
        return self.runs / "SEEDS.log"

    @property
    def exp(self):
        """Set-up A's experiment folder, ``<runs>/SANDBOX-GUARD-EXP-1`` (the tuning half's home, S16)."""
        return self.runs_root / "SANDBOX-GUARD-EXP-1"

    def half(self, name) -> Path:
        """The half's folder H: ``tuning`` is ``<runs>/SANDBOX-GUARD-EXP-1/tuning``, ``held-out`` the sealed folder."""
        return {"tuning": self.exp / "tuning", "held-out": self.sr / SEALED}[name]

    def ledger_lines(self):
        if not self.ledger.exists():
            return []
        return [json.loads(x) for x in self.ledger.read_text().splitlines() if x.strip()]

    # the launch
    def check_planted(self):
        """Every launch fails closed unless each location is planted (failure line 10): the sets root, the runs and
        trees folders and the repository under this session's temporary folder, never the real ones."""
        home = os.path.realpath(real_home())
        real = [os.path.join(home, n) for n in ("gov-os-eval", "gov-os-runs", "gov-os-wall-trees", ".claude")]
        for p in (self.sr, self.runs_root, self.trees, self.repo_path):
            rp = os.path.realpath(p)
            assert rp.startswith(str(self.base) + "/"), f"{p} is not under this session's temporary folder"
            assert not any(rp == r or rp.startswith(r + "/") for r in real), f"{p} is a real location"
        if self.live:
            assert str(self.home) == home, "a live case runs with the real HOME (the session's login)"
        else:
            assert str(self.home).startswith(str(self.tmp) + "/"), "HOME is not planted"
            assert str(self.home) != home

    def base_env(self):
        env = {"HOME": str(self.home), "LANG": "C.UTF-8", "USER": os.environ.get("USER") or "w2-149",
               "TMPDIR": str(self.scratch),
               # noise the session must never see (S10)
               "GOV_ROLE": "orchestrator", "GOV_TICKET": "W2-00", "CLAUDE_PROJECT_DIR": str(TREE),
               "GOV_W2_149_NOISE": "noise"}
        if self.live:
            env["PATH"] = os.environ.get("PATH", "/usr/bin:/bin")
            env["GOV_INDEP_RUNS_DIR"] = str(self.runs_root)
            env["GOV_INDEP_TREES_DIR"] = str(self.trees)
        else:
            env["PATH"] = f"{self.bin}:/usr/bin:/bin"
        return env

    def launch(self, *args, env=None, timeout=180) -> Run:
        if not SCRIPT.is_file():
            pytest.fail("governance/project/orchestration/tools/indep_launch.py does not exist yet (W2-149 builds it)")
        self.check_planted()
        e = self.base_env()
        e.update(env or {})
        p = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], cwd=str(self.repo_path), env=e,
                           capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        return Run(p.returncode, p.stdout, p.stderr)

    def args(self, kind="writer", brief=None, commit="B", set_=None, round_=None, seed=None, dry=False,
             audit=None, sha=None):
        brief = brief or kind
        a = ["--sets-root", self.sr, "--kind", kind, "--brief", f"{BRIEFS_REL}/{brief}.md",
             "--brief-sha256", sha or self.brief_sha(brief), "--commit", self.sha(commit),
             "--set", set_ or DEFAULT_SET[kind]]
        if round_ is not None:
            a += ["--round", str(round_)]
        if kind == "auditor":
            a += ["--audit", audit or "audit-1"]
        if seed is not None:
            a += ["--seed", str(seed)]
        if dry:
            a.append("--dry")
        return a

    def deliver(self, kind, session_extra=None, out=None, **kw) -> Run:
        """A real run with the stub playing a session that leaves ``out`` (a good result by default)."""
        session = dict(out=out if out is not None else good_out(kind), **(session_extra or {}))
        self.write_stub(session=session)
        return self.launch(*self.args(kind, **kw))

    # where a run's things are
    def wall(self, line) -> Path:
        return self.walls / line["kind"] / line["run"]

    def tree(self, line) -> Path:
        return self.trees / f"{line['kind']}-{line['run']}"

    def counts_dir(self, line) -> Path:
        return self.runs / line["kind"] / line["run"]

    def tar(self, line) -> Path:
        return self.walls / line["kind"] / f"{line['run']}.tar"

    def tar_names(self, line):
        with tarfile.open(self.tar(line)) as t:
            return t.getnames()

    def tar_member(self, line, suffix):
        with tarfile.open(self.tar(line)) as t:
            for m in t.getmembers():
                if m.name.endswith(suffix) and m.isfile():
                    return t.extractfile(m).read()
        return None

    # snapshots
    def built_state(self, kind):
        kd = self.walls / kind
        listing = lambda d: sorted(os.listdir(d)) if d.is_dir() else None  # noqa: E731
        return listing(kd), listing(self.trees), self.ledger.read_bytes() if self.ledger.exists() else None

    def hashes(self, root: Path) -> dict:
        out = {}
        if not root.exists():
            return out
        for dp, _dn, fn in os.walk(root):
            for n in fn:
                fp = os.path.join(dp, n)
                out[os.path.relpath(fp, root)] = sha_file(fp) if not os.path.islink(fp) else "link"
        return out

    def hidden_count(self):
        """The hidden part's file count: the files under the sets root whose path matches a hidden glob."""
        n = 0
        for dp, _dn, fn in os.walk(self.sr):
            for name in fn:
                rel = os.path.relpath(os.path.join(dp, name), self.sr)
                n += any(fnmatch.fnmatch(rel, g) for g in HIDDEN_GLOBS)
        return n

    def fill_hidden(self, total):
        """Top the hidden part up to ``total`` files with planted files under a hidden glob."""
        bulk = self.sr / "fixtures/evaluation/memory-verdict/hidden/bulk"
        bulk.mkdir(parents=True, exist_ok=True)
        need = total - self.hidden_count()
        assert need >= 0
        for i in range(need):
            (bulk / f"f{i:05d}.txt").write_text("bulk\n")
        assert self.hidden_count() == total

    # the independent oracles
    def expected_selection(self, seed, n, commit="B", last="A"):
        ex = self.exclusions(commit)
        tracked = self.tracked(commit)
        present = set(tracked)
        diff = [p for p in git(self.repo_path, "diff", "--name-only", "-z", self.sha(last), self.sha(commit)).split("\0")
                if p]
        changed = sorted(p for p in diff if p in present and not excluded(p, ex))
        others = [p for p in tracked if not excluded(p, ex) and p not in changed]
        return changed, random.Random(seed).sample(others, min(n, len(others)))

    def tree_problems(self, tree: Path, commit="B"):
        probs = []
        ex = self.exclusions(commit)
        expected = [p for p in self.tracked(commit) if not excluded(p, ex)]
        found = {}
        if stat.S_IMODE(os.lstat(tree).st_mode) != 0o555:
            probs.append(f"the tree's root is mode {oct(stat.S_IMODE(os.lstat(tree).st_mode))}")
        for dp, dn, fn in os.walk(tree):
            for name in dn + fn:
                fp = os.path.join(dp, name)
                rel = os.path.relpath(fp, tree)
                st = os.lstat(fp)
                if stat.S_ISLNK(st.st_mode):
                    probs.append(f"a link: {rel}")
                    continue
                if name == ".git":
                    probs.append(f"a .git: {rel}")
                if excluded(rel, ex) or (stat.S_ISDIR(st.st_mode) and excluded(rel + "/", ex)):
                    probs.append(f"an excluded path: {rel}")
                mode = stat.S_IMODE(st.st_mode)
                if stat.S_ISDIR(st.st_mode) and mode != 0o555:
                    probs.append(f"folder {rel} mode {oct(mode)}")
                if stat.S_ISREG(st.st_mode):
                    if mode != 0o444:
                        probs.append(f"file {rel} mode {oct(mode)}")
                    found[rel] = sha_file(fp)
        missing = sorted(set(expected) - set(found))
        extra = sorted(set(found) - set(expected))
        if missing or extra:
            probs.append(f"files: {len(found)} found, {len(expected)} expected; missing {missing[:5]}, extra {extra[:5]}")
        for rel in set(expected) & set(found):
            if found[rel] != sha256(self.blob(commit, rel)):
                probs.append(f"{rel}: not the commit's bytes")
        return probs

    def expected_settings(self, wall: Path, tree: Path, model=STUB_MODEL, commit="B"):
        """The template filled for this wall, as a JSON value; the ``@OTHER_WALLS@`` entry left out (the caller checks
        those entries apart)."""
        subs = {"@WALL@": str(wall), "@TREE@": str(tree), "@REPO@": os.path.realpath(self.repo_path),
                "@WORKTREES@": str(self.home / "gov-os-worktrees"), "@RUNS@": str(self.runs_root),
                "@HOME@": str(self.home), "@SETS_ROOT@": str(self.sr), "@WALLS@": str(self.walls), "@MODEL@": model}

        def fill(x):
            if isinstance(x, str):
                for k, v in subs.items():
                    x = x.replace(k, v)
                return x
            if isinstance(x, list):
                return [fill(i) for i in x if i != "@OTHER_WALLS@"]
            if isinstance(x, dict):
                return {k: fill(v) for k, v in x.items()}
            return x

        return fill(json.loads(self.blob(commit, f"{TEMPLATE_REL}/settings.json.tmpl")))

    def expected_claude_md(self, line, brief="writer", commit="B"):
        text = self.blob(commit, f"{TEMPLATE_REL}/CLAUDE.md.tmpl").decode()
        for k, v in {"@KIND@": line["kind"], "@RUN@": line["run"], "@BRIEF_SHA@": self.brief_sha(brief),
                     "@TREE@": str(self.tree(line)), "@COMMIT@": self.sha(commit)}.items():
            text = text.replace(k, v)
        return text

    def f_checks(self, wall: Path, kind: str, commit="B"):
        """The rehearsal's built-wall checks (walls_check.py, its F class) on one wall; the failures by name."""
        fails = []

        def check(name, cond):
            if not cond:
                fails.append(name)

        w, W, sr = str(wall), str(self.walls), str(self.sr)
        s = json.loads((wall / ".claude/settings.json").read_text())
        m = json.loads((wall / "WALL.json").read_text())
        deny, allow = s["permissions"]["deny"], s["permissions"].get("allow", [])
        check("the settings' sha256 is the manifest's", sha_file(wall / ".claude/settings.json") == m["settings_sha256"])
        check("the hook is the template's, byte for byte",
              (wall / ".claude/wall_hook.py").read_bytes() == self.blob(commit, f"{TEMPLATE_REL}/wall_hook.py"))
        check("the brief's sha256 is the manifest's", sha_file(wall / "brief.md") == m["brief_sha256"])
        check("no allow rule opens a shell, the web or a path outside the wall and its tree; writes out/ only",
              all(not a.startswith(("Bash", "WebFetch", "WebSearch")) and (f"/{w}/" in a or f"/{m['tree']}/" in a)
                  for a in allow) and all(f"/{w}/out/" in a for a in allow if a.startswith(("Edit", "Write"))))
        need = ["Bash", "WebFetch", "WebSearch", "Task", "Bash(gov retrieve *)", "Bash(gov context *)", "Bash(git *)",
                f"Read(/{m['runs']}/**)", f"Read(/{m['home']}/.claude/**)", f"Read(/{m['repo']}/**)",
                f"Read(/{sr}/runs/**)", f"Read(/{sr}/transcripts/**)", f"Read(/{sr}/fixtures/**)",
                f"Read(/{W}/APPROVED)", f"Edit(/{w}/.claude/**)", f"Edit(/{m['tree']}/**)"]
        need += [f"Read(/{W}/{k}/**)" for k in KINDS if k != kind]
        kd = os.path.join(W, kind)
        need += [f"Read(/{W}/{kind}/{r}/**)" for r in sorted(os.listdir(kd))
                 if r != wall.name and os.path.isdir(os.path.join(kd, r))
                 and os.stat(os.path.join(kd, r)).st_mtime <= os.stat(wall / "WALL.json").st_mtime]
        missing = [x for x in need if x not in deny]
        check(f"the deny list holds every required class (missing {missing})", not missing)
        hooks = s["hooks"]["PreToolUse"]
        check("the one hook is the wall's own, on every tool",
              len(hooks) == 1 and hooks[0]["matcher"] == "*" and len(hooks[0]["hooks"]) == 1 and
              hooks[0]["hooks"][0]["command"] == f"python3 -I {w}/.claude/wall_hook.py {w} {m['tree']}")
        probs = self.tree_problems(Path(m["tree"]), commit)
        check(f"the tree is plain, complete and read-only ({probs[:3]})", not probs)
        check("the seed was written before the content", m["seeded_before_content"] is True and
              os.stat(wall / "seed.txt").st_mtime_ns < os.stat(wall / "input/selection.json").st_mtime_ns)
        check("the seed's sha256 is the manifest's", sha_file(wall / "seed.txt") == m["seed_sha256"])
        check("the tree lies outside the sets root and outside the wall",
              not m["tree"].startswith(sr + "/") and not m["tree"].startswith(w + "/"))
        n = sum(len(f) for _a, _b, f in os.walk(wall))
        check(f"the wall itself holds few files ({n})", n <= 50)
        check("the wall's root, .claude and input are read-only",
              not any(stat.S_IMODE(os.stat(p).st_mode) & 0o222 for p in (wall, wall / ".claude", wall / "input")))
        check("out/ is the wall's one writable folder, 0700",
              stat.S_IMODE(os.stat(wall / "out").st_mode) == 0o700)
        return fails

    # the counts' shape
    def free_text(self, obj):
        """Every value of a counts object that is not a number, a boolean, null, a sha256, a commit, a fixed word, the
        run's id or the set's name; and every key outside the fixed sets."""
        words = set(KINDS) | set(STATUSES) | set(REASONS.values()) | set(DELIVER_TO.values()) | {ACT}
        bad = []
        if set(obj) != COUNTS_KEYS:
            bad.append(f"top-level keys {sorted(set(obj) ^ COUNTS_KEYS)}")

        def walk(x, key, parent):
            if isinstance(x, dict):
                allowed = NESTED_KEYS.get(key)
                for k, v in x.items():
                    if key and (allowed is None or k not in allowed):
                        bad.append(f"key {k!r} under {key!r}")
                    walk(v, k, key)
            elif isinstance(x, list):
                bad.append(f"a list under {key!r}")
            elif isinstance(x, str):
                ok = (HEX64.match(x) or HEX40.match(x) or RUN_ID.match(x) or x in words
                      or (key == "set" and SET_NAME.match(x)))
                if not ok:
                    bad.append(f"text under {key!r}: {x[:40]!r}")
        for k, v in obj.items():
            walk(v, k, None)
        return bad


def schema_holes(schema):
    """The places where the counts schema would let free text or an unnamed key through: an object without
    ``additionalProperties: false``, a string without an enum, a const or an anchored pattern."""
    holes = []

    def types(node):
        t = node.get("type")
        return set(t) if isinstance(t, list) else {t} if isinstance(t, str) else set()

    def walk(node, where):
        if isinstance(node, dict):
            t = types(node)
            if "properties" in node or "object" in t or "patternProperties" in node:
                if node.get("additionalProperties") is not False:
                    holes.append(f"{where}: an object without additionalProperties: false")
                if "patternProperties" in node:
                    holes.append(f"{where}: patternProperties (keys not fixed)")
            if "string" in t and not ("enum" in node or "const" in node or
                                      (isinstance(node.get("pattern"), str) and node["pattern"].startswith("^")
                                       and node["pattern"].endswith("$"))):
                holes.append(f"{where}: a string without an enum, a const or an anchored pattern")
            for k, v in node.items():
                if k not in ("enum", "const", "required", "examples", "default"):
                    walk(v, f"{where}/{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{where}/{i}")

    walk(schema, "#")
    return holes


def validate(schema, obj):
    import jsonschema
    cls = jsonschema.validators.validator_for(schema)
    return [e.message for e in cls(schema).iter_errors(obj)]


def proc_group(pgid):
    """The live (not zombie) processes of a process group, from /proc, by pgid (never a name match)."""
    alive = []
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            with open(f"/proc/{d}/stat") as f:
                fields = f.read().rsplit(")", 1)[1].split()
        except (OSError, IndexError):
            continue
        if int(fields[2]) == pgid and fields[0] != "Z":
            alive.append(int(d))
    return alive


def pid_alive(pid):
    try:
        with open(f"/proc/{pid}/stat") as f:
            return f.read().rsplit(")", 1)[1].split()[0] != "Z"
    except (OSError, IndexError):
        return False


def wait_gone(check, seconds=3.0):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if not check():
            return True
        time.sleep(0.05)
    return not check()


def assert_refused(world, run: Run, code: int):
    """The exit code, and the result line: status refused, the code, its fixed reason word, the approved list's sha256."""
    assert run.code == code, run.why()
    line = run.line
    assert line is not None, f"no result line on stdout: {run.why()}"
    assert line.get("status") == "refused", line
    assert line.get("code") == code and line.get("reason") == REASONS[code], line
    if (world.walls / "APPROVED").exists():
        assert line.get("approved_sha256") == world.approved_sha(), "approved_sha256 is printed in every result"


def assert_nothing_built(world, kind, before):
    """Nothing built: the kind's wall listing, the trees folder and the seed ledger as they were; no session."""
    walls, trees, ledger = world.built_state(kind)
    assert walls == before[0], f"indep-walls/{kind}/ changed: {before[0]} -> {walls}"
    assert trees == before[1], f"the trees folder changed: {before[1]} -> {trees}"
    assert ledger == before[2], "a SEEDS.log line was written"
    assert world.calls() == [], "claude was started"


def assert_good_launch(world, kind="writer", **kw):
    """Failure line 2: after the refusal a good launch for the same kind and set still builds (a --dry build: the
    wall, its seed, input and tree), on the default approved list."""
    world.approve()
    next_second()
    run = world.launch(*world.args(kind, dry=True, **kw))
    assert run.code == 0, run.why()
    line = run.line
    assert line and line["status"] == "dry" and RUN_ID.match(line["run"] or ""), line
    wall = world.wall(line)
    assert (wall / "WALL.json").is_file() and (wall / "seed.txt").is_file(), "the good launch built no wall"
    assert (wall / "input/selection.json").is_file() and world.tree(line).is_dir()
    return line


def clone_repo(repo: dict, dst: Path) -> dict:
    """A clone of the planted repository (the same commits; its own working tree)."""
    git(Path(repo["path"]).parent, "clone", "-q", "--no-hardlinks", repo["path"], str(dst))
    return dict(repo, path=str(dst.resolve()))


def write_file(root: Path, rel: str, data):
    _write(root, rel, data)
