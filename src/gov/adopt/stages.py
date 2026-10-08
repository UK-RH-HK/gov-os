"""The stages of ``gov adopt --lite`` (W1-41; CAP-06, CAP-44; DEC-090, DEC-517). One stage per call.

Each stage needs a clean tree and the committed record of every stage before it, each standing on the one before
(by content hash), and commits its own record. A refusal writes nothing. The tool proposes and scores nothing: A3
takes its actions from the caller's proposal, and what the proposal does not name is kept. It moves nothing without
an A5 verdict that holds for the path map as it stands, changes no file content, and rewrites nothing: importers,
references and consumers are flagged in the plan.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import yaml

from gov.adopt import project
from gov.adopt.project import FOLDER, MOVING, git, refuse, resolve
from gov.cli.errors import GovError

ACTIONS = ("KEEP", *MOVING, "RETIRE", "DELETE_FROM_ACTIVE_TREE")  # CAP-06.b
EXECUTED = ("MOVE", "RENAME", "DELETE_FROM_ACTIVE_TREE")  # what an A6 batch does; none changes a file's content
KINDS = ("rule-file", "memory-store", "chat-database")
AUDITOR = "independent-auditor"
# A native package layout: a package manifest, and what lies under the ``src/`` folder beside it (CAP-44.j).
MANIFESTS = ("pyproject.toml", "setup.py", "setup.cfg", "package.json", "Cargo.toml", "pom.xml", "build.gradle")
REFS = "refs/gov/adoption"


@dataclass
class Run:
    root: Path
    args: object
    config: dict
    stage: str
    tracked: dict   # path -> blob id at HEAD
    records: dict   # stage -> the frontmatter of its record
    hashes: dict    # stage -> the sha256 of its record

    def finish(self, data: dict, extra: dict | None = None, **result) -> dict:
        """Commit the stage's evidence record (and ``extra`` files) on what is staged; the envelope's result."""
        rel = project.record_path(self.stage)
        previous = self.hashes.get(project.STAGES[project.STAGES.index(self.stage) - 1]) if self.hashes else None
        text = project.record_text(self.stage, {"session": self.args.session, "stands_on": previous, **data})
        project.commit(self.root, f"gov adopt --lite {self.stage}: {project.TITLES[self.stage]}",
                       {rel: text, **(extra or {})})
        return {"stage": self.stage, "record": rel, **result}


def run(root: Path, args, config: dict) -> dict:
    project.require_repository(root)
    tracked = project.tree(root)
    records, hashes = project.chain(root, tracked, args.stage)
    stage = STAGE[args.stage]
    return stage(Run(root, args, config, args.stage, tracked, records, hashes))


def a0(run: Run) -> dict:
    head = resolve(run.root, "HEAD")
    ref = f"{REFS}/backup/{head[:12]}"
    existed = resolve(run.root, ref)
    git(run.root, "update-ref", ref, head)
    try:
        return run.finish({"baseline_commit": head, "backup_ref": ref, "tree": "clean"}, backup_ref=ref)
    except (OSError, GovError):
        if existed is None:
            git(run.root, "update-ref", "-d", ref)
        raise


def a1(run: Run) -> dict:
    artefacts = [{"path": rel, "blob": blob} for rel, blob in sorted(run.tracked.items())
                 if not rel.startswith(FOLDER + "/")]
    return run.finish({"commit": resolve(run.root, "HEAD"), "excluded": [FOLDER + "/**"], "artefacts": artefacts})


def a2(run: Run) -> dict:
    spaces = project.classify(run.config, [item["path"] for item in run.records["A1"]["artefacts"]])
    unknown = [rel for rel, space in spaces.items() if space is None]
    packages = {rel: f"{FOLDER}/packages/DP-ADOPT-{project.sha256(rel.encode())[:8]}.md" for rel in unknown}
    new = {package: _package(rel, package) for rel, package in packages.items() if package not in run.tracked}
    data = {"artefacts": [{"path": rel, "namespace": space} for rel, space in spaces.items()], "unknown": unknown,
            "packages": sorted(packages.values())}
    return run.finish(data, new, packages=data["packages"], unknown=unknown)


def _package(rel: str, package: str) -> str:
    """The customer question an unknown artefact raises, in the kernel's decision-package form (DEC-093)."""
    ident = PurePosixPath(package).stem
    head = {"id": ident, "type": "decision-package", "status": "PROPOSED", "state_class": "AUTHORITATIVE",
            "title": f"What is {rel}, and where does it belong?", "rank": "P2", "constrains": []}
    return ("---\n" + yaml.safe_dump(head, sort_keys=False, allow_unicode=True) + f"---\n\n# {ident} — {head['title']}\n\n"
            f"## Question\n\nNo namespace of `governance/project/path-map.yaml` holds the tracked file `{rel}`. What is "
            "it, and which namespace does it belong to?\n\n"
            "## Why now\n\nAn unknown material artefact blocks the migration (A6) and the legacy retirement (A8) of "
            "the adoption as a whole (CAP-06.c).\n\n"
            "## Current state\n\nFound by `gov adopt --lite --stage A2`. The tool read its path, not its content.\n\n"
            "## Options\n\n- (a) Classify it: add its path to a namespace of the path map, then run A2 again.\n"
            "- (b) Remove it from the project in a change of its own, then run the stages again from A1.\n\n"
            "## Impact\n\nUntil it is answered, nothing is moved, retired or deleted by the adoption.\n\n"
            "## Reversibility\n\n(a) is a line of the path map; (b) stays in git history.\n\n"
            "## Cost of rework\n\nLow for (a).\n\n"
            "## Recommendation\n\n(a), once the owner has said what the file is.\n\n"
            "## Confidence\n\nlow: the tool knows only the path.\n\n"
            "## Exact permitted next actions\n\nStages A0 to A5 may run; the artefact itself may only be kept.\n\n"
            "## Answer\n\n- Option chosen:\n- Decision record:\n")


# --------------------------------------------------------------------------
# A3: the target path map, from the caller's proposal
# --------------------------------------------------------------------------

def _proposal(file: str | None) -> list[dict]:
    if not file:
        raise refuse("NO_PROPOSAL", "stage A3 needs --map <file>: the proposal of actions; the tool proposes none")
    try:
        document = yaml.safe_load(Path(file).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise refuse("PROPOSAL_UNREADABLE", f"the proposal {file} cannot be read: {' '.join(str(exc).split())}; "
                                            "an unreadable proposal is not an empty one") from None
    listed = document.get("artefacts") if isinstance(document, dict) else None
    if not isinstance(listed, list) or not all(isinstance(item, dict) for item in listed):
        raise refuse("PROPOSAL_UNREADABLE", f"the proposal {file} has no list 'artefacts' of mappings")
    return listed


def _native(rel: str, tracked: dict) -> str | None:
    """The package manifest whose layout holds ``rel``: the manifest itself, or a file under its ``src/``."""
    for manifest in (path for path in tracked if PurePosixPath(path).name in MANIFESTS):
        base = manifest.rpartition("/")[0]
        if rel == manifest or rel.startswith((base + "/" if base else "") + "src/"):
            return manifest
    return None


def _entry(run: Run, item: dict, inventory: dict, unknown: list, claimed: dict) -> tuple[dict, list[str]]:
    """The path map's entry for one item of the proposal, and every reason the item is refused for."""
    rel, action, said = item.get("path"), item.get("action"), []
    if not isinstance(rel, str):
        return {"path": str(rel), "action": action}, ["its path is not a string"]
    entry = {"path": rel, "blob": run.tracked.get(rel), "action": action}
    if rel not in inventory:
        said.append("the inventory (A1) does not hold it")
    elif run.tracked.get(rel) != inventory[rel]["blob"]:
        said.append("it changed or left since the inventory (A1): run the stages again from A1")
    if action not in ACTIONS:
        return entry, said + [f"its action {action!r} is none of {', '.join(ACTIONS)}"]
    if rel in unknown and action != "KEEP":
        said.append("no namespace of the path map holds it: an unknown material artefact is only kept (CAP-06.c)")
    wanted = "targets" if action == "SPLIT" else "target" if action in MOVING else None
    goals = item.get(wanted) if wanted else None
    if [key for key in ("target", "targets") if item.get(key) is not None] != ([wanted] if wanted else []):
        said.append(f"{action} takes " + (f"'{wanted}' and no other target" if wanted else "no target"))
    elif wanted:
        entry[wanted] = goals
        for goal in goals if isinstance(goals, list) else [goals]:
            if not isinstance(goal, str) or not goal or goal != PurePosixPath(goal).as_posix() \
                    or ".." in goal.split("/") or goal.startswith(("/", ".git/", FOLDER + "/")):
                said.append(f"its target {goal!r} is not a path inside the project")
                continue
            if goal in run.tracked or os.path.lexists(run.root / goal) \
                    or (goal in claimed and not (claimed[goal] == action == "MERGE")):
                said.append(f"its target {goal} is taken: two artefacts cannot end at one path")
            claimed.setdefault(goal, action)
        if action == "SPLIT" and not (isinstance(goals, list) and goals):
            said.append("SPLIT takes a non-empty list 'targets'")
    kind, batch, grounds = item.get("kind"), item.get("batch"), item.get("justification")
    if kind is not None or action == "RETIRE":
        entry["kind"] = kind
        if kind not in KINDS:
            said.append(f"its kind {kind!r} is none of {', '.join(KINDS)} (a retirement is proven by its kind)")
    entry["authority"] = "non_authoritative" if kind == "chat-database" else "not_assessed"
    if action in MOVING or action == "DELETE_FROM_ACTIVE_TREE":
        entry["batch"] = batch
        if batch is not None and not (type(batch) is int and batch > 0):
            said.append(f"its batch {batch!r} is not a positive number")
    elif batch is not None:
        said.append(f"{action} is in no batch of A6")
    if grounds is not None:
        entry["justification"] = grounds
    native = _native(rel, run.tracked) if action in MOVING and isinstance(rel, str) else None
    if native and not (isinstance(grounds, dict) and all(
            isinstance(grounds.get(key), str) and grounds[key].strip() for key in ("materially_better", "migration_risk"))):
        said.append(f"it lies in the native package layout of {native}: a move out of it states both grounds, "
                    "justification.materially_better and justification.migration_risk (CAP-44.j)")
    return entry, said


def _importers(root: Path, paths: list[str]) -> dict[str, list[str]]:
    """Path -> the files that use a symbol it defines, from a code graph built now. Refuses where none is read."""
    from gov import codeintel

    try:
        codeintel.index(root)
        nodes, users = codeintel._graph(root)  # the module answers by symbol name; by file there is only the graph
    except Exception as exc:  # whatever stops the index or the tool: no graph was read
        raise refuse("CODE_GRAPH_UNREADABLE", f"the code graph cannot be read ({codeintel.TOOL}): {exc}; no importer "
                                              "is established, so no path map with a move is recorded") from None
    absent = [rel for rel in paths if not (root / codeintel.BASE_REL / "files" / rel).is_file()]
    if absent:
        raise refuse("NOT_IN_CODE_GRAPH", "the code index leaves out " + ", ".join(absent) + " (the pre-index "
                     "filter): their importers cannot be established, so they are not moved", artefacts=absent)
    return {rel: sorted({nodes[user]["path"] for key, node in nodes.items() if node["path"] == rel
                         for user, _ in users[key]} - {rel}) for rel in paths}


def _dependents(run: Run, moving: list[dict]) -> None:
    """Add importers (code graph), references (record graph) and consumers (its frontmatter) to each entry."""
    importers = _importers(run.root, [entry["path"] for entry in moving])
    records, edges = project.record_graph(run.root)
    where = {record["id"]: record["path"] for record in records}
    for entry in moving:
        rel = entry["path"]
        ids = [record["id"] for record in records if record["path"] == rel]
        try:
            head = project.frontmatter(project.blob(run.root, run.tracked[rel]).decode("utf-8", "replace")) or {}
            consumers = head.get("consumers") or []
            if not isinstance(consumers, list) or not all(isinstance(item, str) for item in consumers):
                raise ValueError("'consumers' is not a list of names")
        except ValueError as exc:
            raise refuse("RECORD_UNREADABLE", f"{rel}: its consumers cannot be read: {exc}", record=rel) from None
        entry["importers"] = importers[rel]
        entry["references"] = [{"id": edge["source"], "path": where.get(edge["source"]), "type": edge["type"]}
                               for edge in edges if edge["target"] in ids and edge["source"] not in ids]
        entry["consumers"] = consumers


def a3(run: Run) -> dict:
    proposal = _proposal(run.args.map)
    inventory = {item["path"]: item for item in run.records["A1"]["artefacts"]}
    unknown, entries, claimed, problems = project.unknown(run.config, run.tracked), {}, {}, []
    for item in proposal:
        entry, said = _entry(run, item, inventory, unknown, claimed)
        if entry["path"] in entries:
            said.append("the proposal names it twice: an artefact has exactly one action")
        entries[entry["path"]] = entry
        problems += [{"path": entry["path"], "reason": reason} for reason in said]
    if problems:
        raise refuse("PROPOSAL_REFUSED", "the proposal is refused as a whole: "
                     + "; ".join(f"{item['path']}: {item['reason']}" for item in problems), problems=problems)
    moving = [entry for entry in entries.values() if entry["action"] in MOVING]
    if moving and not project.code_intelligence(run.config):
        paths = [entry["path"] for entry in moving]
        raise refuse("CODE_INTELLIGENCE_OFF", "code intelligence is off in the project's path map, so there is no code "
                     "graph and the importers of " + ", ".join(paths) + " cannot be established: nothing is moved "
                     "there, and the proposal is refused as a whole (DEC-517)", artefacts=paths)
    if moving:
        _dependents(run, moving)
    last = max((entry["batch"] for entry in entries.values() if entry.get("batch")), default=0) + 1
    for entry in entries.values():
        if "batch" in entry and entry["batch"] is None:
            entry["batch"] = last  # what A6 executes and the proposal put in no batch: one batch after the others
    artefacts = [entries.get(rel, {"path": rel, "action": "KEEP"}) for rel in inventory]
    return run.finish({"proposal_sha256": project.sha256(Path(run.args.map).read_bytes()),
                       "code_intelligence": project.code_intelligence(run.config), "artefacts": artefacts})


def _plan(run: Run) -> dict:
    """The batched plan of the path map (A3) as it stands: what A4 records, and what A6 and A8 hold A4's record to."""
    artefacts = run.records["A3"]["artefacts"]
    batches = {}
    for item in artefacts:
        if item["action"] in EXECUTED:
            batches.setdefault(item["batch"], []).append(
                {key: item[key] for key in ("path", "blob", "action", "target") if key in item})
    plan = [{"batch": number, "rollback_point": f"{REFS}/rollback/batch-{number}", "artefacts": batches[number]}
            for number in sorted(batches)]
    dependents = [{"artefact": item["path"], "relation": relation[:-1], "dependent": dependent, "handling": "flag"}
                  for item in artefacts for relation in ("importers", "references", "consumers")
                  for dependent in item.get(relation, [])]
    return {"path_map_hash": run.hashes["A3"], "batches": plan, "dependents": dependents,
            "retirements": [item["path"] for item in artefacts if item["action"] == "RETIRE"]}


def a4(run: Run) -> dict:
    artefacts = run.records["A3"]["artefacts"]
    content = [item["path"] for item in artefacts if item["action"] in ("SPLIT", "MERGE", "EXTRACT")]
    if content:
        raise refuse("CONTENT_CHANGE", "SPLIT, MERGE and EXTRACT change file content, which no batch of this tool "
                     "does: make them a change of their own, then run the stages again from A1 (" + ", ".join(content)
                     + ")", artefacts=content)
    return run.finish(_plan(run))


# --------------------------------------------------------------------------
# A5: the verdict of a fresh Independent Auditor; held again by A6 and A8
# --------------------------------------------------------------------------

def _verdict(run: Run, rel: str) -> dict:
    """What makes ``rel`` an accepted verdict on the path map as it stands; a refusal that names what does not."""
    head, data = project.read_record(run.root, run.tracked, rel)
    if head.get("verdict") != "pass":
        raise refuse("VERDICT_NOT_PASS", f"{rel}: the verdict is {head.get('verdict')!r}; only 'pass' passes", verdict=rel)
    if head.get("path_map_hash") != run.hashes["A3"]:
        raise refuse("VERDICT_OTHER_MAP", f"{rel}: its path_map_hash ({head.get('path_map_hash')!r}) is not the hash "
                     f"of the path map as it stands ({project.record_path('A3')}, {run.hashes['A3']})", verdict=rel)
    brought = git(run.root, "log", "-1", "--format=%H", "--", rel).strip()
    roles = git(run.root, "log", "-1", "--format=%(trailers:key=Role,valueonly)", brought).split()
    wrote = [path for path in git(run.root, "show", "--name-only", "--format=", brought).split("\n")
             if path.startswith(FOLDER + "/")]
    if roles != [AUDITOR] or wrote:
        raise refuse("VERDICT_NOT_INDEPENDENT", f"{rel}: the commit that brought it ({brought[:12]}) carries the Role "
                     f"trailer {roles}, not {AUDITOR} alone" + (f", and wrote {wrote}" if wrote else ""), verdict=rel)
    stages = {stage: record.get("session") for stage, record in run.records.items()}
    session = head.get("auditor_session")
    if not stages.get("A3") or not isinstance(session, str) or not session \
            or session in (*stages.values(), run.args.session):
        raise refuse("VERDICT_NOT_INDEPENDENT", f"{rel}: its auditor_session ({session!r}) must be named and differ "
                     f"from the sessions that ran the stages ({stages}, now {run.args.session!r}); the path map must "
                     "name its own (--session)", verdict=rel)
    return {"verdict": rel, "verdict_sha256": project.sha256(data), "verdict_commit": brought,
            "auditor_session": session, "path_map": project.record_path("A3"), "path_map_hash": run.hashes["A3"]}


def a5(run: Run) -> dict:
    if not run.args.verdict:
        raise refuse("NO_VERDICT", "stage A5 needs --verdict <path>: the Independent Auditor's committed record")
    return run.finish(_verdict(run, run.args.verdict))


def guard(run: Run) -> None:
    """Before anything leaves its place: the accepted verdict still holds, the plan is the audited path map's
    plan, and no artefact is unknown."""
    accepted = run.records["A5"]
    if _verdict(run, accepted["verdict"])["verdict_sha256"] != accepted.get("verdict_sha256"):
        raise refuse("VERDICT_CHANGED", f"{accepted['verdict']} is not the verdict A5 accepted: run A5 again")
    differs = [key for key, value in _plan(run).items() if run.records["A4"].get(key) != value]
    if differs:  # the verdict is about the path map: a plan that says anything else has none
        raise refuse("PLAN_NOT_THE_PATH_MAPS", f"{project.record_path('A4')} is not the plan of the audited path map "
                     f"({project.record_path('A3')}): its {', '.join(differs)} differ from what the path map yields; "
                     "nothing is moved, retired or deleted: run the stages again from A4", differs=differs)
    unknown = project.unknown(run.config, run.tracked)
    if unknown:
        raise refuse("UNKNOWN_ARTEFACT", "no namespace of the path map holds " + ", ".join(unknown) + ": while an "
                     "artefact is unknown nothing is moved, retired or deleted (CAP-06.c)", unknown=unknown)


def rebuild(run: Run, result: dict) -> dict:
    """The index refresh that follows the moves and the retirement: ``gov rebuild``, after the record's commit."""
    from gov.rebuild import command

    try:
        stores = command.run(run.root, run.args, run.config)["stores"]
        if stores["lexical"]["status"] != "recreated":
            raise refuse("INDEX_NOT_REFRESHED", str(stores["lexical"]))
    except GovError as exc:
        raise refuse("INDEX_REFRESH_FAILED", f"stage {run.stage} is done and committed ({result['record']}), but the "
                     f"index refresh that follows it (gov rebuild) failed: {exc.message}") from None
    return {**result, "rebuild": stores}


# --------------------------------------------------------------------------
# A6: the batches, each one commit with its rollback point
# --------------------------------------------------------------------------

def _batch(root: Path, batch: dict, before: list[int]) -> dict:
    number, point, start = batch["batch"], batch["rollback_point"], resolve(root, "HEAD")
    git(root, "update-ref", point, start)
    expected, made, artefact = project.tree(root), [], None
    try:
        for artefact in batch["artefacts"]:
            origin = artefact["path"]
            if artefact["action"] == "DELETE_FROM_ACTIVE_TREE":
                git(root, "rm", "-q", "--", origin)
            else:
                for folder in reversed((root / artefact["target"]).parents):
                    if not folder.exists():
                        folder.mkdir()
                        made.append(folder)
                git(root, "mv", "--", origin, artefact["target"])
                expected[artefact["target"]] = expected[origin]
            del expected[origin]
        git(root, "commit", "-q", "-m", f"gov adopt --lite A6: batch {number}")
        if project.tree(root) != expected:  # read from the commit itself: a commit hook is held to it as well
            raise refuse("CONTENT_CHANGED", "the batch's commit is not the planned moves and nothing else")
    except (OSError, GovError) as exc:
        project.restore(root, start)
        for folder in reversed(made):
            if folder.is_dir() and not any(folder.iterdir()):
                folder.rmdir()
        raise refuse("BATCH_FAILED", f"batch {number} failed at {artefact and artefact['path']} "
                     f"({artefact and artefact.get('target')}) and is rolled back to {point} ({start}): {exc}; the "
                     f"batches before it stay ({before}), the batches after it did not run",
                     batch=number, rollback_point=point, done=before) from None
    done = [{**{key: item[key] for key in ("path", "action", "target") if key in item},
             **({} if "target" in item else {"disposition": "deleted from the active tree as the path map says",
                                             "reachable_at": point})} for item in batch["artefacts"]]
    return {"batch": number, "status": "done", "rollback_point": point, "commit": resolve(root, "HEAD"),
            "artefacts": done}


def a6(run: Run) -> dict:
    guard(run)
    baseline, plan, problems = run.records["A0"], run.records["A4"]["batches"], []
    if resolve(run.root, baseline["backup_ref"]) != baseline["baseline_commit"]:
        raise refuse("BACKUP_REF", f"the backup ref {baseline['backup_ref']} does not resolve to the baseline commit "
                                   f"{baseline['baseline_commit']} that A0 recorded: nothing is moved without it")
    if project._run(run.root, ("merge-base", "--is-ancestor", baseline["baseline_commit"], "HEAD"), (0, 1))[0]:
        raise refuse("BACKUP_REF", f"the baseline commit {baseline['baseline_commit']} is no ancestor of HEAD")
    artefacts = [item for batch in plan for item in batch["artefacts"]]
    for item in artefacts:  # everything is examined before anything moves
        if item["action"] not in EXECUTED:
            problems.append(f"{item['path']}: {item['action']} is not what a batch executes")
        if run.tracked.get(item["path"]) != item["blob"]:
            problems.append(f"{item['path']} is not at its origin as the path map recorded it")
        if "target" in item and (item["target"] in run.tracked or os.path.lexists(run.root / item["target"])):
            problems.append(f"the target {item['target']} of {item['path']} is taken")
    if any("target" in item for item in artefacts) and not project.code_intelligence(run.config):
        problems.append("code intelligence is off in the path map: importers are not established, nothing is moved")
    if problems:
        raise refuse("PLAN_NOT_EXECUTABLE", "; ".join(problems) + ": run the stages again from A1", problems=problems)
    done = []
    for batch in plan:
        done.append(_batch(run.root, batch, [item["batch"] for item in done]))
    return rebuild(run, run.finish({"path_map_hash": run.hashes["A3"], "backup_ref": baseline["backup_ref"],
                                    "batches": done, "index_refresh": "gov rebuild, run after this record's commit"}))


def a8(run: Run) -> dict:
    from gov.adopt import legacy
    return legacy.retire(run)


STAGE = {"A0": a0, "A1": a1, "A2": a2, "A3": a3, "A4": a4, "A5": a5, "A6": a6, "A8": a8}
