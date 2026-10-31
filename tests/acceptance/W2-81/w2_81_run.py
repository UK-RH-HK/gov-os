"""The real run of the W2-81 proving ground: one command, not collected as a test (DEC-728, DEC-941, DEC-953).

    PYTHONPATH=<a tree>/src python3 tests/acceptance/W2-81/w2_81_run.py --folder <path> --mode build|run|read
        [--seed N] [--gov <exe>] [--pinned-gov <exe>] [--close-ticket [<repository>=]<id>]...
        [--hidden <dir>] [--manifests <dir>] [--large-size <bytes>] [--stages A0,A1,A2]

- ``--folder``: the run folder, by literal path: a temporary folder, or ``~/gov-os-runs/W2-81/<run>`` (DEC-728).
  It is refused inside this repository or inside any git work tree the runner did not build.
- ``build``: build the five repositories and the clean variant under ``<folder>/repos/``, with their manifests under
  ``<manifests or folder>/manifests/``, and record the seed in ``<folder>/run.json``. Without ``--seed``, a fresh
  seed is drawn. A launched session then adopts each repository, leaving its logs and reports in
  ``<folder>/outputs/<repository>/``.
- ``read``: read what that adoption left, ask the question sets of ``gov retrieve`` (``--gov``), close a ticket in
  each repository (``--pinned-gov``), judge, and write the report. It only reads the adoption's outputs.
- ``run``: ``build``, then the adoption stages that need no session (``--stages``, by default A0, A1 and A2) run
  with ``--gov`` in each repository, then as ``read``.
- The report: ``<folder>/report.json`` and ``<folder>/report.md``; a log of steps, ``<folder>/run.log``.

The hidden half is read only from ``--hidden``, or from the default hidden folder when that exists. Its questions
are named by id only; its texts and answers are in no report, log or output. The secrets' values are drawn from the
seed in memory and are in no report, log or output either (checked before anything is written). The runner writes
nothing in this repository, never reads the workbench and never uses the dev-tier variable.
"""

from __future__ import annotations

import argparse
import json
import os
import secrets as random_source
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_81_build as build  # noqa: E402
import w2_81_git as gitlib  # noqa: E402
import w2_81_judge as judge  # noqa: E402
import w2_81_manifest as manifest_form  # noqa: E402
import w2_81_questions as questions  # noqa: E402
import w2_81_score as score  # noqa: E402
import yaml  # noqa: E402
from w2_81_secret import make_secret  # noqa: E402

EXPECTED = (*build.SHAPES, build.CLEAN)
BATCH_SIZE, BUNDLE_BUDGET, STACK_BUDGET, TOKEN_CHARS = 10, 6000, 24000, 4  # as gov.retrieval.measure (DEC-860)
DEFAULT_STAGES = ("A0", "A1", "A2")


class RunnerError(Exception):
    """The runner refuses: nothing is built or written."""


def _refuse_place(folder):
    folder = gitlib.outside_this_repository(Path(folder).expanduser())
    probe = folder
    while not probe.exists():
        probe = probe.parent
    done = subprocess.run(["git", "-C", str(probe), "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                          env=gitlib.git_env(probe))
    if done.returncode == 0:
        raise RunnerError(f"the run folder {folder} lies in a git work tree the runner did not build "
                          f"({done.stdout.strip()})")
    return folder


def _env(folder):
    home, tmp = folder / ".home", folder / ".tmp"
    home.mkdir(exist_ok=True)
    tmp.mkdir(exist_ok=True)
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home), "TMPDIR": str(tmp),
           "LC_ALL": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_AUTHOR_NAME": "W2-81 runner", "GIT_AUTHOR_EMAIL": "w2-81-runner@example.invalid",
           "GIT_COMMITTER_NAME": "W2-81 runner", "GIT_COMMITTER_EMAIL": "w2-81-runner@example.invalid"}
    env.update({k: v for k, v in os.environ.items() if k == "GOV_REBUILD_LOCK"})
    return env


class _Log:
    def __init__(self):
        self.lines = []

    def __call__(self, line):
        self.lines.append(line)


class _Repository:
    """A built repository as the runner reads it back: its manifest, root, outputs and held secrets."""

    def __init__(self, name, root, manifest, manifest_path, held):
        self.name, self.root, self.manifest, self.manifest_path, self.secrets = name, root, manifest, manifest_path, held


def held_secrets(manifest):
    """The planted secrets' values, drawn again from the seed (in memory only)."""
    return [make_secret(e["evidence"]["form"], manifest["seed"], e["evidence"].get("salt", manifest["repository"]))
            for e in manifest["planted"] if e["kind"] == "secret"]


def _hidden(options):
    folder = Path(options.hidden) if options.hidden else questions.HIDDEN_DEFAULT
    if not folder.is_dir():
        return None, [], {}
    variants = []
    if (folder / "variants.yaml").is_file():
        data = yaml.safe_load((folder / "variants.yaml").read_text(encoding="utf-8")) or {}
        variants = data.get("variants") or []
    sets = {path.stem: questions.load_set(path) for path in sorted(folder.glob("*.yaml")) if path.stem != "variants"}
    return folder, variants, sets


def _ask(gov, root, question, env, log):
    """The stacked context of one question, as gov.retrieval.measure stacks it: (path, start, end) items."""
    stacked, seen, used, token = [], set(), 0, None
    for _ in range(50):
        done = subprocess.run([gov, "retrieve", question.question, "--json", "--batch-size", str(BATCH_SIZE),
                               "--bundle-budget", str(BUNDLE_BUDGET), *(["--continue", token] if token else [])],
                              cwd=root, env=env, capture_output=True, text=True)
        try:
            doc = json.loads(done.stdout)
            bundle = doc["result"] if isinstance(doc.get("result"), dict) else doc
            items = [(str(i["path"]), int(i["start_line"]), int(i["end_line"]), str(i.get("text", "")))
                     for i in bundle["evidence"]]
        except (ValueError, KeyError, TypeError, AttributeError):
            items = None
        if done.returncode != 0 or items is None or doc.get("ok") is False:
            log(f"retrieve {question.id}: failed (exit {done.returncode})")
            return None
        full = False
        for item in items:
            if item[:3] in seen:
                continue
            size = -(-len(item[3]) // TOKEN_CHARS)
            if used + size > STACK_BUDGET:
                full = True
                break
            seen.add(item[:3])
            stacked.append(item[:3])
            used += size
        token = bundle.get("continuation")
        if full or not token:
            break
    log(f"retrieve {question.id}: {len(stacked)} items")
    return stacked


def _tickets(values):
    out, every = {}, None
    for value in values or []:
        if "=" in value:
            name, ticket = value.split("=", 1)
            out[name] = ticket
        else:
            every = value
    return {name: out.get(name, every) for name in EXPECTED}


def _build(options, folder, log):
    if folder.exists() and any(folder.iterdir()):
        raise RunnerError(f"the run folder {folder} is not empty: a build needs a new or empty folder")
    folder.mkdir(parents=True, exist_ok=True)
    seed = options.seed if options.seed is not None else random_source.randbelow(2 ** 31)
    _, variants, _ = _hidden(options)
    manifests = Path(options.manifests).expanduser() if options.manifests else folder
    built = build.build_all(folder, seed, options.large_size, manifests_root=manifests, variants=variants)
    record = {"form": "w2-81-run/1", "seed": seed, "large_size": options.large_size,
              "manifests": str(manifests / "manifests"), "hidden_variants": len(variants)}
    (folder / "run.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    log(f"build: seed {seed}, {len(built)} repositories, {len(variants)} hidden variants")
    return record


def _read_back(folder):
    try:
        record = json.loads((folder / "run.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise RunnerError(f"{folder} holds no run.json: build it first (--mode build)") from None
    out = {}
    for name in EXPECTED:
        path = Path(record["manifests"]) / f"{name}.json"
        manifest = manifest_form.load(path)
        out[name] = _Repository(name, folder / "repos" / name, manifest, path, held_secrets(manifest))
    return record, out


def run(options, built=None):
    """The run; returns the report (also written in the folder). ``built``: the capabilities counted as built (the
    judge's ``built``); the command leaves it to today's code, and only the self-tests pass it."""
    folder = _refuse_place(options.folder)
    log = _Log()
    if options.mode in ("build", "run"):
        _build(options, folder, log)
    if options.mode == "build":
        _write_log(folder, log, [])
        return {"mode": "build", "seed": json.loads((folder / "run.json").read_text())["seed"]}
    record, repos = _read_back(folder)
    env = _env(folder)
    held = [h for r in repos.values() for h in r.secrets]
    stage_runs = {}
    if options.mode == "run":
        for name, repo in repos.items():
            stage_runs[name] = []
            for stage in (options.stages.split(",") if options.stages else DEFAULT_STAGES):
                if not options.gov:
                    stage_runs[name].append({"stage": stage, "run": False})
                    break
                done = subprocess.run([options.gov, "adopt", "--lite", "--stage", stage], cwd=repo.root, env=env,
                                      capture_output=True, text=True)
                stage_runs[name].append({"stage": stage, "run": True, "exit": done.returncode})
                log(f"adopt {name} {stage}: exit {done.returncode}")
                if done.returncode != 0:
                    break
    hidden_folder, _, hidden_sets = _hidden(options)
    scores = []
    for name, repo in repos.items():
        asked = questions.resolve(questions.load_set(questions.VISIBLE / f"{name}.yaml"), repo.manifest, repo.root,
                                  "visible")
        if name in hidden_sets:
            asked += questions.resolve(hidden_sets[name], repo.manifest, repo.root, "hidden")
        answers = {q.id: _ask(options.gov, repo.root, q, env, log) for q in asked} if options.gov else {}
        scores.append(score.score_repository(name, asked, answers) if options.gov
                      else {"repository": name, "questions": len(asked), "hit_at_5": None, "stacked_share": None,
                            "per_question": []})
    tickets = _tickets(options.close_ticket)
    closes = {}
    for name, repo in repos.items():
        if not options.pinned_gov or not tickets.get(name):
            closes[name] = {"run": False}
            continue
        done = subprocess.run([options.pinned_gov, "close", tickets[name]], cwd=repo.root, env=env,
                              capture_output=True, text=True)
        closes[name] = {"run": True, "ticket": tickets[name], "exit": done.returncode}
        log(f"close {name} {tickets[name]}: exit {done.returncode}")
    cases = [(repo.manifest, repo.root, folder / "outputs" / name, repo.secrets) for name, repo in repos.items()]
    judged = judge.judge(cases, score.figures(scores), EXPECTED, built)
    reasons = list(judged["reasons"])
    for name in EXPECTED:
        close = closes[name]
        if not close["run"]:
            reasons.append(f"{name}: gov close was not run")
        elif close["exit"] != 0:
            reasons.append(f"{name}: gov close {close['ticket']} ended with exit {close['exit']}")
        failed = [s for s in stage_runs.get(name, []) if s.get("run") and s["exit"] != 0]
        reasons += [f"{name}: gov adopt --lite --stage {s['stage']} ended with exit {s['exit']}" for s in failed]
    verdict = judged["verdict"] if judged["verdict"] == judge.ERROR else (judge.NOT_READY if reasons else judge.READY)
    by_name = {j["repository"]: j for j in judged.get("repositories", [])}
    report = {"form": "w2-81-report/1", "mode": options.mode, "seed": record["seed"], "verdict": verdict,
              "reasons": reasons, "hidden_half": "present" if hidden_folder else "absent",
              "gov": options.gov, "pinned_gov": options.pinned_gov,
              "repositories": {name: {"judgement": by_name.get(name), "figures": next(
                  ({k: s[k] for k in ("questions", "hit_at_5", "stacked_share", "per_question")}
                   for s in scores if s["repository"] == name), None),
                  "not_built": (by_name.get(name) or {}).get("not_built"), "close": closes[name],
                  "stages_run": stage_runs.get(name, [])} for name in EXPECTED}}
    text = json.dumps(report, indent=2, sort_keys=True)
    markdown = _markdown(report)
    if any(h.found_in(t) for h in held for t in (text, markdown, "\n".join(log.lines))):
        report = {"form": "w2-81-report/1", "verdict": judge.ERROR, "seed": record["seed"],
                  "reasons": ["the report would hold a secret's value: it is not written"]}
        text, markdown, log.lines = json.dumps(report, indent=2), "# W2-81 report\n\nERROR\n", ["withheld"]
    (folder / "report.json").write_text(text + "\n", encoding="utf-8")
    (folder / "report.md").write_text(markdown, encoding="utf-8")
    _write_log(folder, log, reasons)
    return report


def _write_log(folder, log, reasons):
    (folder / "run.log").write_text("\n".join(log.lines + [f"reason: {r}" for r in reasons]) + "\n",
                                    encoding="utf-8")


def _markdown(report):
    rows = [f"# W2-81 proving ground: {report['verdict']}", "", f"Seed {report['seed']}; mode {report['mode']}; "
            f"hidden half {report['hidden_half']}.", ""]
    rows += [f"- {reason}" for reason in report["reasons"]] or ["- every planted problem handled, no control "
                                                                 "flagged, both figures met, every close at exit 0"]
    for name, repo in report["repositories"].items():
        j, f = repo["judgement"] or {}, repo["figures"] or {}
        rows += ["", f"## {name}", "", f"hit@5 {f.get('hit_at_5')} (floor {score.HIT_AT_5_FLOOR:g}); stacked share "
                 f"{f.get('stacked_share')} (target {score.STACKED_SHARE_TARGET:g}); {f.get('questions')} questions; "
                 f"gov close: {repo['close']}; not built: {', '.join(repo['not_built'] or []) or 'none'}", "",
                 "| Planted problem | Status | Evidence |", "|---|---|---|"]
        rows += [f"| `{p['id']}` | {p['status']} | {p['evidence'][0]['said']} |" for p in j.get("planted", [])]
        rows += ["", "| Control | Status |", "|---|---|"]
        rows += [f"| `{c['id']}` | {c['status']} |" for c in j.get("controls", [])]
    return "\n".join(rows) + "\n"


def parse(argv):
    parser = argparse.ArgumentParser(prog="w2_81_run.py", description="the W2-81 proving ground's real run")
    parser.add_argument("--folder", required=True)
    parser.add_argument("--mode", choices=("build", "run", "read"), default="run")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--gov", default=None)
    parser.add_argument("--pinned-gov", dest="pinned_gov", default=None)
    parser.add_argument("--close-ticket", dest="close_ticket", action="append", default=[])
    parser.add_argument("--hidden", default=None)
    parser.add_argument("--manifests", default=None)
    parser.add_argument("--large-size", dest="large_size", type=int, default=build.REAL_RUN_LARGE)
    parser.add_argument("--stages", default=None)
    return parser.parse_args(argv)


def main(argv=None):
    try:
        report = run(parse(argv))
    except (RunnerError, gitlib.InsideThisRepository) as refused:
        print(f"refused: {refused}", file=sys.stderr)
        return 2
    print(f"{report['verdict'] if 'verdict' in report else 'BUILT'} (seed {report['seed']})")
    return 0 if report.get("verdict", judge.READY) == judge.READY else 1


if __name__ == "__main__":
    sys.exit(main())
