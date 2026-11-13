"""Proofs (b) and (c) of W2-88b (DAEO-aks1): W2-88's tools run on a clone of a real repository, on copies only.

One repository per process (its peak RSS is its own). Usage::

    python3 experiments/W2-88/proof_bc.py --repo <name> --root <clone> --runs /home/usain/gov-os-runs/W2-88b
        [--assess-only] [--questions <file>] [--budget-ms <N>] [--origin <url or path>] [--licence <SPDX or text>]
        [--path-map proof|keep] [--stand-in]

A full run does, on the clone: the path map (one namespace, ``embedding_policy: embedded``, ``memory_class: governance``,
code intelligence on unless ``PROOF_CODE_GRAPH=0``) committed; A0, A1, A2; MA (``--out <runs>/out/<name>/``) and the
assessment alone in its own process (its own peak RSS); A3 with ``--assessment`` and a proposal with no action; A4; A5
with the proof's stand-in verdict commit (``Role: independent-auditor``); A6; A8; A9 with ``--out``, ``--questions`` and
``--budget-ms`` when given. ``--assess-only`` runs MA only (it is in no chain and writes nothing in the repository): no
A0..A9, no commit in the clone; the result says ``adoption: none``.

Writes only under ``--runs`` (which must lie under ``/home/usain/gov-os-runs/W2-88b/``) and, in a full run, in the clone
itself (commits and ``.gov-runtime/``: the clone is the copy). It refuses a ``--runs`` or ``--root`` inside the
repository or outside that folder. The result is ``<runs>/results/<name>.json``: counts, ids, digests and figures only;
no repository content and no secret value (no path of the repository either, except the licence file's).
``--stand-in`` (off by default; the sandbox's test only) replaces the embedder by one hash vector per chunk and is
recorded in the result as ``stand_in: true``.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[2]  # the repository this script is committed in (never written)
RUNS_BASE = Path("/home/usain/gov-os-runs/W2-88b")
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
LICENCE_NAME = re.compile(r"(?i)(licen[cs]e|copying|unlicense)(\..*)?")
PATH_MAP_REL = "governance/project/path-map.yaml"
VERDICT_REL = "audit/a5-verdict.md"
ENV = {**os.environ, "GIT_AUTHOR_NAME": "proof", "GIT_AUTHOR_EMAIL": "proof@example.invalid",
       "GIT_COMMITTER_NAME": "proof", "GIT_COMMITTER_EMAIL": "proof@example.invalid"}


def refuse(message):
    print(f"proof_bc: refused: {message}", file=sys.stderr)
    sys.exit(2)


def inside(path, folder):
    path, folder = Path(path).resolve(), Path(folder).resolve()
    return path == folder or folder in path.parents


def git(root, *args, check=True):
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=ENV)
    if check and done.returncode != 0:
        raise RuntimeError(f"git {args[0]} failed: {done.stderr.strip()[:300]}")
    return done.stdout.strip()


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def guard(runs, root, name, out):
    """The paths the script may touch; a refusal ends it before anything is read or written."""
    if not NAME.fullmatch(name):
        refuse(f"--repo {name!r} is not a plain name")
    for what, path in (("--runs", runs), ("--root", root)):
        if inside(path, REPO):
            refuse(f"{what} {path} lies inside the repository {REPO}")
        if not inside(path, RUNS_BASE):
            refuse(f"{what} {path} is not under {RUNS_BASE}")
    if inside(out, root) or inside(root, out):
        refuse("the output folder and the clone must be apart")
    if not (Path(root) / ".git").exists():
        refuse(f"--root {root} is not a git clone (no .git)")
    top = git(root, "rev-parse", "--show-toplevel", check=False)
    if not top or Path(top).resolve() != Path(root).resolve():
        refuse(f"--root {root} is not the top of its own git repository")


class Result:
    """The result file, rewritten atomically at every step: a run that is killed leaves the figures it had."""

    def __init__(self, file, data):
        self.file, self.data = Path(file), data
        self.file.parent.mkdir(parents=True, exist_ok=True)

    def save(self):
        tmp = self.file.with_name(f".{self.file.name}.tmp")
        tmp.write_text(json.dumps(self.data, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
        os.replace(tmp, self.file)


class Failed(Exception):
    pass


def store_hashes(root):
    """The sha256 of every file of the clone's store (``.gov-runtime/``). The code index's staged copies of the
    repository's files (``codeintel/files/``) are listed as a count and one digest over their ``path sha256`` lines."""
    base, entries, staged = Path(root) / ".gov-runtime", {}, []
    for place in sorted(base.rglob("*")) if base.is_dir() else []:
        if place.is_symlink() or not place.is_file():
            continue
        rel = place.relative_to(base).as_posix()
        digest = sha256_file(place)
        if rel.startswith("codeintel/files/"):
            staged.append(f"{rel} {digest}")
        else:
            entries[rel] = digest
    return {"files": len(entries) + len(staged), "entries": entries,
            "codeintel_files": {"count": len(staged),
                                "listing_sha256": hashlib.sha256("\n".join(staged).encode()).hexdigest()}}


def ma_alone(root, out):
    """The memory assessment alone in a fresh process: its peak RSS is its own, not the proof's."""
    from gov.adopt import assess

    done = assess.assess(Path(root), Path(out))
    print(json.dumps({"peak_rss_bytes": done["peak_rss_bytes"], "session_figure_bytes": done["session_figure_bytes"],
                      "under_session_figure": done["under_session_figure"], "seconds": done["seconds"],
                      "tracked_files": done["tracked_files"], "tracked_bytes": done["tracked_bytes"]}))


def describe(assessment):
    by = lambda kind: dict(Counter(item.get("by") for item in assessment[kind]))  # noqa: E731
    top = sorted(assessment["languages"].items(), key=lambda item: (-item[1], item[0]))[:20]
    return {
        "counts": {key: len(assessment[key]) for key in ("binary", "generated", "minified", "vendored", "secrets",
                                                         "no_route")},
        "by": {key: by(key) for key in ("binary", "generated", "minified", "vendored")},
        "no_route_reasons": dict(Counter(item["reason"] for item in assessment["no_route"])),
        "secret_rules": dict(Counter(item["rule"] for item in assessment["secrets"])),
        "secrets_scanned": assessment["secrets_scanned"], "secrets_unscanned_count": len(assessment["secrets_unscanned"]),
        "secrets_unscanned_reason": assessment["secrets_unscanned_reason"],
        "languages_top": dict(top), "languages_kinds": len(assessment["languages"]),
        "largest_bytes": [item["bytes"] for item in assessment["largest"]],
        "limits": assessment["limits"]["file_limit_bytes"], "estimate": assessment["estimate"],
        "peak_rss_bytes": assessment["peak_rss_bytes"], "session_figure_bytes": assessment["session_figure_bytes"],
        "under_session_figure": assessment["under_session_figure"], "seconds": assessment["seconds"]}


def licence_of(root, head, declared):
    found = []
    for name in git(root, "ls-tree", "--name-only", head).splitlines():
        if LICENCE_NAME.fullmatch(name):
            data = subprocess.run(["git", "-C", str(root), "cat-file", "blob", f"{head}:{name}"], capture_output=True,
                                  env=ENV).stdout
            found.append({"path": name, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    return {"declared": declared, "files": found[:8]}


def stores_of(record):
    out = {}
    for store, data in record["stores"].items():
        refused = data.get("refused") or []
        out[store] = {**{key: data.get(key) for key in ("judged", "chunks", "vectors", "nodes", "edges", "seconds",
                                                        "peak_rss_bytes", "requested", "built", "error")
                         if key in data},
                      "indexed": len(data.get("indexed") or []), "refused": len(refused),
                      "refused_reasons": dict(Counter(item["reason"] for item in refused)),
                      **({"binary_held": len(data["binary_held"])} if "binary_held" in data else {})}
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--repo", required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--runs", required=True)
    parser.add_argument("--assess-only", action="store_true")
    parser.add_argument("--questions", default=None)
    parser.add_argument("--budget-ms", type=int, default=None)
    parser.add_argument("--origin", default=None)
    parser.add_argument("--licence", default=None)
    parser.add_argument("--path-map", choices=("proof", "keep"), default="proof",
                        help="proof: the proof's one-namespace map is committed; keep: the clone's own map when it tracks one")
    parser.add_argument("--stand-in", action="store_true", help="the embedder's stand-in (the sandbox's test only)")
    parser.add_argument("--ma-alone", action="store_true", help=argparse.SUPPRESS)
    options = parser.parse_args()
    runs, root = Path(options.runs).resolve(), Path(options.root).resolve()
    name, out = options.repo, runs / "out" / options.repo
    guard(runs, root, name, out)
    sys.path.insert(0, str(REPO / "src"))
    if options.ma_alone:
        return ma_alone(root, runs / "out" / f"{name}-alone")
    if options.questions and not Path(options.questions).is_file():
        refuse(f"--questions {options.questions} is not a file")

    import yaml
    from gov.adopt import fabric, project, stages
    from gov.cli.errors import GovError
    from gov.config.loader import load_config
    import gov.retrieval.semantic as semantic

    result = Result(runs / "results" / f"{name}.json", {
        "repository": name, "mode": "assess-only" if options.assess_only else "full", "status": "running",
        "adoption": "none" if options.assess_only else "A0..A9 lite, no S12 to S14", "stand_in": options.stand_in,
        "tool_source": str(REPO), "tool_commit": git(REPO, "rev-parse", "HEAD", check=False), "python": sys.version.split()[0],
        "code_graph_requested": os.environ.get("PROOF_CODE_GRAPH", "1") == "1" and not options.assess_only,
        "origin": re.sub(r"//[^/@]+@", "//", options.origin or git(root, "config", "--get", "remote.origin.url", check=False)
                         or "none"),
        "steps": [], "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    data = result.data
    start = git(root, "rev-parse", "HEAD")
    data["pinned_commit"] = start  # the clone's HEAD before any proof commit
    data["shallow"] = git(root, "rev-parse", "--is-shallow-repository", check=False)
    data["licence"] = licence_of(root, start, options.licence)
    result.save()
    if options.stand_in:
        semantic.refresh = stand_in_semantic(semantic)  # the embedder's stand-in: no model runs in the sandbox

    def step(label, call):
        began = time.monotonic()
        row = {"step": label}
        data["steps"].append(row)
        try:
            found = call()
            row.update(ok=True, seconds=round(time.monotonic() - began, 1))
            result.save()
            return found
        except GovError as exc:
            row.update(ok=False, seconds=round(time.monotonic() - began, 1), code=exc.code, message=str(exc.message)[:400])
            result.save()
            raise Failed(label) from exc
        except Exception as exc:  # noqa: BLE001 - the figures of the steps before it stand
            row.update(ok=False, seconds=round(time.monotonic() - began, 1), code=type(exc).__name__,
                       message=str(exc)[:400])
            result.save()
            raise Failed(label) from exc

    def stage(label, **more):
        args = SimpleNamespace(**{"lite": True, "stage": label, "map": None, "verdict": None, "session": "proof-adopter",
                                  "out": None, "assessment": None, "decision": [], "questions": None, "budget_ms": None,
                                  **more})
        return step(label, lambda: stages.run(root, args, load_config(root)))

    try:
        if options.assess_only:
            assess_only(options, root, out, data, stage, result, start)
        else:
            full(options, root, out, runs, data, stage, step, result, start, yaml, project, fabric)
        data["status"] = "done"
    except Failed as stop:
        data["status"] = "failed"
        data["failed_at"] = str(stop)
    data["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    result.save()
    print(name, data["status"], flush=True)
    return 0 if data["status"] == "done" else 1


def stand_in_semantic(semantic):
    import sqlite3
    from gov.store import STORE_REL

    def refresh(root, *args, **more):
        """One hash vector per chunk, written as the real stage writes its table (no embedder manifest)."""
        db = sqlite3.connect(Path(root) / STORE_REL)
        db.executescript("CREATE TABLE IF NOT EXISTS semantic_vector (chunk_id TEXT PRIMARY KEY, embedding BLOB NOT NULL);"
                         "DELETE FROM semantic_vector;")
        for (chunk,) in db.execute("SELECT chunk_id FROM lexical_chunk").fetchall():
            db.execute("INSERT INTO semantic_vector VALUES (?, ?)", (chunk, hashlib.sha256(chunk.encode()).digest()))
        db.commit()
        db.close()
        return {"available": True}
    return refresh


def assessment_step(options, root, out, data, stage):
    """MA in the chain's process, then the assessment alone in its own (its own peak RSS). A scan that did not cover
    the repository (SECRETS_UNSCANNED) is the stage's refusal, recorded; the files are written all the same."""
    from gov.adopt import assess

    try:
        made = stage("MA", out=str(out))
        data["ma"] = {"ok": True, "proposals": made["proposals"], "kinds": made["kinds"]}
    except Failed:
        row = data["steps"][-1]
        if row.get("code") != "SECRETS_UNSCANNED" or not (out / assess.FILE).is_file():
            raise
        row["note"] = "refusal recorded; the assessment and the plan are written (B-1.5)"
        plan = sorted(p.name for p in (out / "refactor-plan").glob("RP-*.md"))
        data["ma"] = {"ok": False, "code": "SECRETS_UNSCANNED", "proposals": len(plan),
                      "kinds": [re.sub(r"^RP-\d+-|\.md$", "", n) for n in plan]}
    alone = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--ma-alone", "--repo", options.repo, "--root",
                            str(root), "--runs", options.runs], capture_output=True, text=True,
                           env={**os.environ, "PYTHONPATH": os.pathsep.join(filter(None, [str(REPO / "src"),
                                                                                         os.environ.get("PYTHONPATH")]))})
    data["assessment_alone"] = json.loads(alone.stdout.strip().splitlines()[-1]) if alone.returncode == 0 \
        else {"failed": alone.stderr[-300:]}
    assessment = json.loads((out / assess.FILE).read_text(encoding="utf-8"))
    data["assessed_commit"] = assessment["commit"]
    data["size"] = {"files": assessment["tracked_files"], "bytes": assessment["tracked_bytes"],
                    "commits": assessment["commits"]}
    data["assessment"] = describe(assessment)
    plan = data["ma"]
    data["plan"] = {"count": plan["proposals"], "kinds": plan["kinds"]}
    return assessment


def assess_only(options, root, out, data, stage, result, start):
    assessment_step(options, root, out, data, stage)
    data["clone_unchanged"] = {"head_same": git(root, "rev-parse", "HEAD") == start,
                               "status_clean": git(root, "status", "--porcelain") == ""}
    result.save()
    if not all(data["clone_unchanged"].values()):
        raise Failed("clone-changed")


def full(options, root, out, runs, data, stage, step, result, start, yaml, project, fabric):
    from gov.adopt import assess

    work = runs / "work" / options.repo
    work.mkdir(parents=True, exist_ok=True)
    PATH_MAP = {"namespaces": {"all": {"paths": ["**"], "embedding_policy": "embedded",
                                                   "memory_class": "governance"}},
                            "capabilities": {"code_intelligence": {"enabled": data["code_graph_requested"]}}}

    def path_map():
        git(root, "config", "--local", "user.name", "proof")
        git(root, "config", "--local", "user.email", "proof@example.invalid")
        tracked = git(root, "ls-files", "--", PATH_MAP_REL) != ""
        if tracked and options.path_map == "keep":
            data["path_map"] = {"kept": True, "sha256": sha256_file(root / PATH_MAP_REL), "committed": False}
            return
        text = yaml.safe_dump(PATH_MAP)
        (root / PATH_MAP_REL).parent.mkdir(parents=True, exist_ok=True)
        (root / PATH_MAP_REL).write_text(text, encoding="utf-8")
        git(root, "add", "--", PATH_MAP_REL)
        changed = subprocess.run(["git", "-C", str(root), "diff", "--cached", "--quiet"], env=ENV).returncode == 1
        if changed:
            git(root, "commit", "-q", "-m", "path map for the proof")
        data["path_map"] = {"kept": False, "sha256": sha256_file(root / PATH_MAP_REL), "committed": changed,
                            "replaced_a_tracked_map": tracked}

    step("path-map", path_map)
    for label in ("A0", "A1", "A2"):
        stage(label)
    assessment_step(options, root, out, data, stage)
    proposal = work / "proposal.yaml"
    proposal.write_text(yaml.safe_dump({"artefacts": []}), encoding="utf-8")  # a proposal with no action
    stage("A3", map=str(proposal), assessment=str(out))
    stage("A4")

    def verdict():
        head = {"id": "AV-PROOF", "type": "adoption-verdict", "status": "ACTIVE", "state_class": "EVIDENCE",
                "verdict": "pass", "auditor_session": "proof-auditor",
                "path_map_hash": project.sha256((root / project.record_path("A3")).read_bytes())}
        (root / VERDICT_REL).parent.mkdir(exist_ok=True)
        (root / VERDICT_REL).write_text("---\n" + yaml.safe_dump(head) + "---\n\n# AV-PROOF\n", encoding="utf-8")
        git(root, "add", "--", VERDICT_REL)
        git(root, "commit", "-q", "-m", "A5: review (the proof's stand-in for the independent auditor)",
            "--trailer", "Role: independent-auditor")

    step("A5-verdict-commit", verdict)
    data["a5_verdict"] = "the proof's stand-in (Role: independent-auditor), not an independent audit"
    stage("A5", verdict=VERDICT_REL)
    stage("A6")
    stage("A8")
    given = {}
    if options.questions:
        listed, cause = fabric.load_questions(options.questions)
        given = {"count": len(listed), "file_sha256": sha256_file(options.questions), "cause": cause}
    data["questions"] = given or {"count": 0, "cause": "no question set was given (--questions)"}
    began = time.monotonic()
    done = stage("A9", out=str(out), questions=options.questions, budget_ms=options.budget_ms)
    data["a9_seconds"] = round(time.monotonic() - began, 1)
    import resource
    data["a9_peak_rss_bytes"] = {"process": assess.peak_rss(),
                                 "children": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024}
    data["a9_commit"] = git(root, "rev-parse", "HEAD")
    first = store_hashes(root)  # S4: right after A9
    record = project.frontmatter((root / done["record"]).read_text(encoding="utf-8"))
    data["stores"] = stores_of(record)
    data["installed"] = {"count": len(record["installed"]), "kept": record["kept"], "retrieval_yaml": any(
        item["path"] == fabric.RETRIEVAL for item in record["installed"])}
    data["digests"] = record["digests"]
    data["standard"] = {key: value for key, value in record["standard"].items() if key != "pool"}
    scale = record["scale"]
    data["scale"] = {**scale, "over": fabric.over(scale), "scale_proposal": (out / "SCALE-PROPOSAL.md").is_file()}
    measure = record["measure"]
    data["measure"] = {**{key: measure.get(key) for key in ("right_e2e", "wrong_claims", "hit_at_5", "questions")},
                       "residuals": measure["residuals"]}
    data["digests_of_store_files"] = {"after_a9": first}
    result.save()
    second = store_hashes(root)  # again at the script's end: a proposal never changes the store
    data["digests_of_store_files"]["at_end"] = second
    quiet = lambda held: {key: value for key, value in held.items()  # noqa: E731 - the code tool's own logs are no store
                          if key != "entries"} | {"entries": {rel: sha for rel, sha in held["entries"].items()
                                                             if not rel.startswith("codeintel/home/logs/")}}
    data["store_unchanged_by_proposal"] = quiet(first) == quiet(second)
    data["tool_logs_changed"] = sorted(rel for rel in {*first["entries"], *second["entries"]}
                                       if rel.startswith("codeintel/home/logs/")
                                       and first["entries"].get(rel) != second["entries"].get(rel))
    data["clone_after"] = {"status_clean": git(root, "status", "--porcelain") == ""}
    result.save()
    if not data["store_unchanged_by_proposal"]:
        raise Failed("store-changed")


if __name__ == "__main__":
    sys.exit(main())
