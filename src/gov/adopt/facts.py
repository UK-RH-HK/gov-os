"""The adoption's facts file (W2-174 S5; DEC-1148 (2)): ``governance/project/facts.yaml``, which ``gov brief`` needs.

``write_default`` writes it when the repository has none, from product defaults: gov command forms, and a named
placeholder (``{UNSET_<NAME>}``, which ``gov brief`` refuses by name) for a command with no gov form. The project's
CTO fills those afterwards. ``ready.new_since`` is the adoption's UTC date, a quoted ISO string. A facts file that
exists is never touched.

``write_queue_settings`` (W2-202 A5; L2 section 2) writes ``governance/project/queue.yaml`` where the repository has
none: the settings ``gov queue`` lands by (the integration branch, the form of a ticket's work branch). The landing
is the close, so no ``close.yaml`` is written.
"""

from __future__ import annotations

import datetime
from pathlib import Path

HEADER = """\
# The project facts the kernel templates are filled from (schema: template/governance/kernel/schemas/facts.schema.json).
# Written by `gov adopt --facts` from product defaults. A command written as {UNSET_<NAME>} has no gov form: `gov brief`
# refuses a brief that names it, until the project's CTO writes the command it uses (a `run` form and a `check` form
# that exits 0 in a temporary repository with no model, network or GPU).
"""

PATHS = """\
paths:
  main: '.'
  tree: '.'
  tests_tree: '../{W2}-tests'
  ticket_file: '{MAIN}/.tickets/{ID}.md'
  scratch: '{TREE}/.gov-runtime/scratch'
  lead_records: '{TREE}/.gov-runtime/scratch/lead'
  briefs: '{TREE}/.gov-runtime/scratch/lead/briefs'
  logs: '{TREE}/.gov-runtime/scratch/lead/log'
  checkpoint_file: '{TREE}/.gov-runtime/scratch/lead/CHECKPOINT.md'
  tests_ready: '{TREE}/.gov-runtime/scratch/lead/TESTS-READY'
  empty_home: '{WRITE_TREE}/.gov-runtime/scratch/empty-home'
  acceptance_root: 'tests/acceptance/'
  acceptance: 'tests/acceptance/{W2}'
  acceptance_readme: 'tests/acceptance/{W2}/README.md'
  probes: '{TREE}/docs/probes/{ID}'
"""

# name -> (run, check); None: no gov form, written as {UNSET_<NAME>} for both
COMMANDS = {
    "identity": None,
    "where": None,
    "retrieve": ('gov retrieve "<question>"', "gov retrieve --help"),
    "context": ("gov context {ID} --role {WORKER_ROLE}", "gov context --help"),
    "links": ("gov links --since {BASE}", "gov links --help"),
    "accept": ("gov accept {ID} --root {WRITE_TREE}", "gov accept --help"),
    "pytest_folder": None,
    "unit_tests": None,
    "schema_check": None,
    "rebuild": ("gov rebuild", "gov rebuild --help"),
    "lead_verify": None,
    "launch_worker": None,
    "wait_for": ("gov wait {EXIT_FILE}", "gov wait --help"),
    "lead_brief": ("gov brief lead {ID} --run {RUN_KIND} --part {PART}", "gov brief --help"),
    "tests_worktree": None,
    "merge_tests": None,
    "tests_worktree_remove": None,
    "checkpoint": ('gov checkpoint --ticket {ID} --trigger ticket-transition --next "{NEXT}"', "gov checkpoint --help"),
    "context_ceiling": ("gov context {ID} --json", "gov context --help"),
}

TAIL = """\
dod:
- id: DOD-1
  line: 'Acceptance green: every KPI line''s verify holds through {CMD:accept}, read as pass or fail per line.'
- id: DOD-2
  line: 'The landing''s checks are green: `gov queue {ID}` lands the work (its impact-selected run on the merged result green, every acceptance-test commit by the test designer or the owner; a path outside allowed_paths is a notice).'
- id: DOD-3
  line: 'The close is written at the land: the ticket''s close record names the landed merge and the ticket is closed.'

steps:
  keyword_warn:
    "on": false
    line: 'Before verification, run the project''s keyword check.'
    match: 'keyword_warn'
  trailer_gate:
    "on": false
    line: 'Before you return, run the project''s trailer check.'
    match: 'trailer_gate'
  collect_only:
    "on": false
    line: 'Before DONE, collect the tests only; it ends with no collection error.'
    match: '--collect-only'
  hooks_check:
    "on": false
    line: 'Before each commit, check that no pre-commit hook stops you.'
    match: 'pre-commit'
  scratch_measure:
    "on": false
    line: 'Before every heavy run and at the end, give the scratch size and inode count in `evidence`.'
    match: 'du -s'
  context_ceiling:
    "on": true
    line: 'Before DONE, run {CMD:context_ceiling} once; on CONTEXT_OVER_CEILING return the figures and a package naming what to trim.'
    match: 'gov(\\.cli\\.main)? context \\S+ --json'
  checkpoint_record:
    "on": true
    line: 'At the end, before the final probe, record {CMD:checkpoint} with the next step.'
    match: 'gov(\\.cli\\.main)? checkpoint'
  guard_refusal_lines:
    "on": true
    line: '- <time> | <the command''s form, one line> | <the rule''s reason as the hook gave it> | true or false-positive'
    match: 'guard_refusals:'

budgets:
  brief: 4000
  ticket: 4000
  role-research: 3500
  role-product-spec: 3500
  role-test-designer: 3500
  role-engineer: 3500
  role-reviewer: 3500
  role-lead: 8000
  role-cto: 6000

harness_allowed:
- Bash
- Read
- Edit
- Write
- Grep
- Glob

ready:
  new_since: '{today}'
"""


def _commands() -> str:
    lines = ["commands:"]
    for name, forms in COMMANDS.items():
        run, check = forms or ("{UNSET_%s}" % name.upper(),) * 2
        lines += [f"  {name}:", f"    run: '{run}'", f"    check: '{check}'"]
    return "\n".join(lines) + "\n"


def write_default(root: Path, today: datetime.date) -> dict:
    """Write ``<root>/governance/project/facts.yaml`` unless it exists: ``{"path": ..., "written": true|false}``."""
    path = Path(root) / "governance/project/facts.yaml"
    if path.exists():
        return {"path": str(path), "written": False}
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join([HEADER, PATHS, _commands(), TAIL.replace("{today}", today.isoformat())])
    try:
        with open(path, "x", encoding="utf-8") as handle:  # "x": a facts file that appeared meanwhile stays
            handle.write(text)
    except FileExistsError:
        return {"path": str(path), "written": False}
    return {"path": str(path), "written": True}


QUEUE_SETTINGS_REL = "governance/project/queue.yaml"
QUEUE_SETTINGS = """\
# The settings gov queue lands by. Written by `gov adopt --facts` from product defaults; the project's CTO changes them.
# integration: the branch tickets land on. work_branch: the form of a ticket's work branch ({ticket}: the ticket's
# id, {wbs}: its wbs_id); `gov queue <ticket>=<branch>` names another branch for one landing.
integration: main
work_branch: "{ticket}"
"""


def write_queue_settings(root: Path) -> dict:
    """Write ``<root>/governance/project/queue.yaml`` unless it exists: ``{"path": ..., "written": true|false}``."""
    path = Path(root) / QUEUE_SETTINGS_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "x", encoding="utf-8") as handle:  # "x": a settings file that is there stays as it is
            handle.write(QUEUE_SETTINGS)
    except FileExistsError:
        return {"path": str(path), "written": False}
    return {"path": str(path), "written": True}
