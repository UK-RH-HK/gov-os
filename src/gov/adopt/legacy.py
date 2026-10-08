"""Stage A8 of ``gov adopt --lite``: the legacy import and the legacy retirement (W1-41; CAP-42, CAP-44.e; DEC-517).

What the audited path map retires leaves the active tree in one commit, and stays reachable at an archive ref:

- a **rule file** only once it is imported into ``.rulesync/``: ``.cursor/rules/*.mdc`` by ``rulesync import``, run
  in the project; ``.cursorrules``, ``.windsurfrules``, the sections of ``AGENTS.md`` one by one and the servers of
  an MCP tools file by this module. No import overwrites a file;
- a **memory store** only after the dependency proof: no active record and no rule cites it;
- a **chat database** only where a committed record cites it by path and current content hash (``extracted_from``).

Everything is established before anything is written, and one failure refuses the whole stage.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path, PurePosixPath

import yaml

from gov.adopt import project
from gov.adopt.project import FOLDER, git, refuse
from gov.cli.errors import GovError

RULESYNC_IMPORT = ("rulesync", "import", "--targets", "cursor", "--features", "rules")
GENERATE = "rulesync generate --targets claudecode,agentsmd --features rules,hooks,permissions,subagents,commands,skills"
RULES, TIME_LIMIT = ".rulesync/rules", 120  # seconds, for the one rulesync call
LOADED = (".rulesync/", ".claude/", ".cursor/")  # with the names below: where a rule that may cite the store stands
LOADED_NAMES = ("CLAUDE.md", "AGENTS.md", ".cursorrules", ".windsurfrules")  # a legacy rule file that is kept stays loaded
CIT_E = f"{FOLDER}/CIT-E-ADOPT-A8.md"


def _rule(source: str, body: str, **more) -> str:
    head = {"root": False, "targets": ["*"], "description": f"imported from {source} by gov adopt --lite (A8)",
            "globs": ["**/*"], **more}
    head = json.loads(json.dumps(head))  # plain copies: no YAML alias where two keys hold one list
    return "---\n" + yaml.safe_dump(head, sort_keys=False) + "---\n" + body.strip() + "\n"


def _body(text: str) -> str:
    return text.split("\n---", 1)[-1].strip() if text.startswith("---") else text.strip()


def _mdc(source: str, text: str) -> str:
    """The rule a Cursor ``.mdc`` file says, in rulesync's form: the tool's own import where rulesync writes none."""
    head = project.frontmatter(text) or {}
    globs = head.get("globs", ["**/*"] if head.get("alwaysApply") else [])
    globs = [glob.strip() for glob in globs.split(",")] if isinstance(globs, str) else globs
    if not isinstance(globs, list) or not all(isinstance(glob, str) for glob in globs):
        raise ValueError("its globs are neither a string nor a list of strings")
    cursor = {key: head[key] for key in ("alwaysApply", "description", "globs") if key in head}
    return _rule(source, _body(text), globs=globs, cursor=cursor,
                 **({"description": head["description"]} if isinstance(head.get("description"), str) else {}))


def _sections(text: str) -> dict[str, str]:
    """``AGENTS.md`` one section at a time: numbered slug -> text, for what stands before the first heading below
    the title and for each such heading. A section that is a heading and nothing else is structure, not a rule."""
    found, name = {}, "00-preamble"
    for line in text.split("\n"):
        if re.match(r"##+ ", line):
            name = f"{len(found) + 1:02d}-" + re.sub(r"[^a-z0-9]+", "-", line.lower()).strip("-")
        found[name] = found.get(name, "") + line + "\n"
    return {slug: body for slug, body in found.items()
            if any(line.strip() and not line.startswith("#") for line in body.split("\n"))}


def _imports(run, texts: dict[str, bytes]) -> tuple[dict, dict]:
    """Source -> {target under .rulesync/: the text this tool writes there}; and the flat map of targets."""
    plan, targets = {}, {}
    for source, data in texts.items():
        name = PurePosixPath(source).name
        try:
            text = data.decode("utf-8")
            if not text.strip():
                raise ValueError("it holds nothing to import")
            if _is_mdc(source):
                made = {f"{RULES}/{name[:-4]}.md": _mdc(source, text)}
            elif name in (".cursorrules", ".windsurfrules"):
                made = {f"{RULES}/legacy-{name[1:]}.md": _rule(source, text)}
            elif name == "AGENTS.md":
                made = {f"{RULES}/legacy-agents-{slug}.md": _rule(source, body) for slug, body in _sections(text).items()}
            elif name.endswith(".json"):
                document = json.loads(text)
                servers = document.get("mcpServers") if isinstance(document, dict) else None
                if isinstance(servers, dict) and servers:  # rulesync's own form of MCP servers
                    made = {".rulesync/mcp.json": json.dumps({"mcpServers": servers}, indent=2) + "\n"}
                else:  # a tools file of another form: kept word for word, since no rulesync form says the same
                    made = {f".rulesync/legacy/{source.strip('./').replace('/', '-')}": text}
            else:
                raise ValueError("this tool has no import for a rule file of this form")
        except (ValueError, AttributeError) as exc:  # not UTF-8, not JSON, not the form: not imported, so not retired
            raise refuse("RULE_FILE_NOT_IMPORTED", f"{source} cannot be imported into .rulesync/: {exc}; it is not "
                                                   "retired, and neither is anything else", source=source) from None
        taken = [target for target in made if target in run.tracked or target in targets]
        if taken:
            raise refuse("IMPORT_WOULD_OVERWRITE", f"the import of {source} would overwrite {', '.join(taken)}: "
                                                   "nothing is imported over a file", source=source)
        plan[source] = made
        targets.update(made)
    return plan, targets


def _is_mdc(source: str) -> bool:
    return source.startswith(".cursor/rules/") and source.endswith(".mdc") and source.count("/") == 2


def _rulesync(run, plan: dict, texts: dict) -> dict[str, str]:
    """Run ``rulesync import`` for the ``.mdc`` files, and hold it by what it wrote and nothing it said alone.

    Returns, for each ``.mdc`` file rulesync wrote no rule for, what rulesync said: that one is the tool's own
    import (DEC-517). A call that cannot run or fails, a path written that is no target, and a target that does
    not hold its source's text each refuse.
    """
    sources = {source: next(iter(made)) for source, made in plan.items() if _is_mdc(source)}
    if not sources:
        return {}
    try:
        done = subprocess.run(RULESYNC_IMPORT, cwd=run.root, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                              timeout=TIME_LIMIT)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise refuse("RULESYNC_FAILED", f"`{' '.join(RULESYNC_IMPORT)}` could not be run: {exc}") from None
    said, wrote = " ".join((done.stdout + done.stderr).split()), project.dirty(run.root)
    counted = re.search(r"Imported (\d+) file", done.stdout)
    if done.returncode != 0 or set(wrote) - set(sources.values()) or int(counted.group(1) if counted else 0) != len(wrote):
        raise refuse("RULESYNC_FAILED", f"`{' '.join(RULESYNC_IMPORT)}` ended with exit code {done.returncode}, wrote "
                                        f"{wrote} (the .mdc targets are {sorted(sources.values())}) and said {said!r}")
    for source, target in sources.items():
        if target in wrote and _body(texts[source].decode("utf-8")) not in (run.root / target).read_text("utf-8"):
            raise refuse("RULESYNC_FAILED", f"{target} does not hold the text of {source} after `rulesync import`")
    return {source: said for source, target in sources.items() if target not in wrote}


def _proof(run, store: list[str], retiring: set, rule_files: list[str]) -> dict:
    """The dependency proof of the memory store: what was read, and every active record and rule that cites it."""
    records, edges = project.record_graph(run.root)
    from gov.records import active

    ids = sorted({record["id"] for record in records if record["path"] in store})
    live, citers = set(active(run.root)), []
    read = [record for record in records if record["id"] in live and record["path"] not in retiring
            and not record["path"].startswith(FOLDER + "/")]
    for record in read:
        text = project.blob(run.root, run.tracked[record["path"]]).decode("utf-8", "replace")
        cited = sorted({edge["target"] for edge in edges if edge["source"] == record["id"] and edge["target"] in ids}
                       | {rel for rel in store if rel in text})
        if cited:
            citers.append({"record": record["id"], "path": record["path"], "cites": cited})
    declared = {item["path"] for item in run.records["A3"]["artefacts"] if item.get("kind") == "rule-file"}
    rules = sorted({rel for rel in run.tracked if rel.startswith(LOADED) or PurePosixPath(rel).name in LOADED_NAMES}
                   .union(rule_files, declared & set(run.tracked)) - set(store))
    for rel in rules:
        text = project.blob(run.root, run.tracked[rel]).decode("utf-8", "replace")
        cited = [name for name in (*store, *ids) if re.search(rf"(?<![\w/-]){re.escape(name)}(?![\w-])", text)]
        if cited:
            citers.append({"rule": rel, "cites": cited})
    proof = {"store": store, "ids": ids, "records_read": [record["id"] for record in read], "rules_read": rules,
             "citers": citers}
    if citers:
        raise refuse("STORE_STILL_CITED", "the legacy memory store is not retired, it is still cited by "
                     + ", ".join(f"{item.get('record') or item['rule']} ({item.get('path') or 'a rule'})"
                                 for item in citers) + ": nothing is retired", **proof)
    return proof


def _extractions(run, chats: dict[str, bytes], retiring: set) -> dict[str, list]:
    """Chat database -> the committed records that cite it by path and by the hash of what it holds now."""
    if not chats:
        return {}
    records, _ = project.record_graph(run.root, strict=False)  # only a record that can be read is a proof here
    found = {rel: [] for rel in chats}
    for record in records:
        if record["path"] in retiring or record["path"].startswith(FOLDER + "/"):
            continue
        head = project.frontmatter(project.blob(run.root, run.tracked[record["path"]]).decode("utf-8", "replace"))
        cited = (head or {}).get("extracted_from")
        for source in cited if isinstance(cited, list) else [cited]:
            rel = source.get("path") if isinstance(source, dict) else None
            if rel in chats and source.get("sha256") == project.sha256(chats[rel]):
                found[rel].append({"id": record["id"], "path": record["path"]})
    missing = [rel for rel, citing in found.items() if not citing]
    if missing:
        raise refuse("CHAT_NOT_EXTRACTED", "no committed record cites " + ", ".join(
            f"{rel} (sha256 {project.sha256(chats[rel])})" for rel in missing) + " by path and current content hash "
            "as `extracted_from`: its knowledge is not established as extracted, and nothing is retired",
            databases=missing)
    return found


def _cit_e(base: str, archive: str, retired: list[dict], proof: dict | None) -> str:
    head = {"id": "CIT-E-ADOPT-A8", "type": "change-execution-record", "status": "APPLIED", "state_class": "EVIDENCE",
            "stage": "A8", "base": base, "archive_ref": archive, "retired": [item["path"] for item in retired]}
    rows = "".join(f"| `{item['path']}` | {item['kind']} | {item['disposition']} | `{archive}` |\n" for item in retired)
    said = "No memory store is retired." if proof is None else (
        f"Store: {', '.join(proof['store'])}. Read: {len(proof['records_read'])} active records and "
        f"{len(proof['rules_read'])} rule files. Citers: none.")
    return ("---\n" + yaml.safe_dump(head, sort_keys=False) + "---\n\n# CIT-E: retirement of the legacy systems "
            "(adoption stage A8)\n\nWhat `gov adopt --lite --stage A8` took out of the active tree, file by file.\n\n"
            "| File | Kind | Disposition | Reachable at |\n|---|---|---|---|\n" + rows
            + f"\n## Dependency proof\n\n{said}\n\n## Index refresh\n\n`gov rebuild` follows the commit of this record.\n")


def retire(run) -> dict:
    from gov.adopt.stages import REFS, guard, rebuild

    guard(run)
    listed = [item for item in run.records["A3"]["artefacts"] if item["action"] == "RETIRE"]
    moved = [item["path"] for item in listed if run.tracked.get(item["path"]) != item["blob"]]
    if moved:
        raise refuse("PLAN_NOT_EXECUTABLE", ", ".join(moved) + ": not in the tree as the path map recorded them; "
                                                               "run the stages again from A1", artefacts=moved)
    texts, retiring = {}, {item["path"] for item in listed}
    for item in listed:
        try:
            texts[item["path"]] = (run.root / item["path"]).read_bytes()
        except OSError as exc:
            raise refuse("UNREADABLE", f"{item['path']} cannot be read ({exc}): it is not retired, and neither is "
                                       "anything else", artefact=item["path"]) from None
    of = {kind: [item["path"] for item in listed if item["kind"] == kind] for kind in ("rule-file", "memory-store",
                                                                                      "chat-database")}
    plan, targets = _imports(run, {rel: texts[rel] for rel in of["rule-file"]})
    proof = _proof(run, of["memory-store"], retiring, of["rule-file"]) if of["memory-store"] else None
    extracted = _extractions(run, {rel: texts[rel] for rel in of["chat-database"]}, retiring)
    said = {"rule-file": "imported into .rulesync/ and retired from the active tree",
            "memory-store": "retired after the dependency proof: no active record and no rule cites it (CIT-E)"}
    head = project.resolve(run.root, "HEAD")
    archive = f"{REFS}/archive/{head[:12]}"
    existed = project.resolve(run.root, archive)
    retired = [{"path": item["path"], "kind": item["kind"], "reachable_at": archive,
                "disposition": said.get(item["kind"]) or "retired as non-authoritative: its knowledge is extracted to "
                + ", ".join(f"{record['id']} ({record['path']})" for record in extracted[item["path"]])}
               for item in listed]
    data = {"path_map_hash": run.hashes["A3"], "archive_ref": archive if listed else None,
            "imported": [], "dependency_proof": proof, "cit_e": CIT_E if listed else None, "retired": retired,
            "adapter_generation": f"not run by this stage; the step that follows is `{GENERATE}` (DEC-488)",
            "index_refresh": "gov rebuild, run after this record's commit"}
    try:  # from here the stage writes; whatever fails, the tree and the refs are put back
        if listed:
            git(run.root, "update-ref", archive, head)
            left = _rulesync(run, plan, texts)
            data["imported"] = [
                {"source": source, "into": sorted(made), "by": "gov adopt",
                 **({"rulesync_import_said": left[source]} if source in left else {})}
                if source in left or not _is_mdc(source) else
                {"source": source, "into": sorted(made), "by": "rulesync import"} for source, made in plan.items()]
            for item in data["imported"]:
                for target in item["into"] if item["by"] == "gov adopt" else []:
                    (run.root / target).parent.mkdir(parents=True, exist_ok=True)
                    (run.root / target).write_text(targets[target], encoding="utf-8")
            git(run.root, "add", "--", *targets) if targets else None
            git(run.root, "rm", "-q", "--", *sorted(retiring))
        staged = project.tree(run.root, git(run.root, "write-tree").strip())
        expected = {rel: blob for rel, blob in run.tracked.items() if rel not in retiring}
        if {rel: blob for rel, blob in staged.items() if rel not in targets} != expected or set(targets) - set(staged):
            raise refuse("CONTENT_CHANGED", "the staged tree is not the retirement and the import and nothing else")
        result = run.finish(data, {CIT_E: _cit_e(head, archive, retired, proof)} if listed else None,
                            next_step=GENERATE, retired=sorted(retiring))
    except (OSError, GovError):
        project.restore(run.root, head)
        if listed and existed is None:
            git(run.root, "update-ref", "-d", archive)
        raise
    return rebuild(run, result)
