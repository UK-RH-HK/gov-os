"""The real run of the W2-81 proving ground: one command, not collected as a test (DEC-728, DEC-941, DEC-1221 (1)).

    PYTHONPATH=<the release candidate>/src python3 tests/acceptance/W2-81/w2_81_run.py --folder <path> \
        --mode build|run|read [--seed N] [--gov <exe>] [--pinned-gov <exe>] [--adopter-model <id>] [--claude <exe>] \
        [--queue-ticket [<repository>=]<id>]... [--hidden <dir> | --sets-root <root>] [--manifests <dir>] \
        [--large-size <bytes>] [--stages A0,A1,A2]

- ``--folder``: the run folder, by literal path: a temporary folder, or ``~/gov-os-runs/W2-81/<run>`` (DEC-728).
  It is refused inside this repository or inside any git work tree the runner did not build.
- ``build``: build the five repositories and the clean variant under ``<folder>/repos/``, with their manifests under
  ``<manifests or folder>/manifests/``, and record the seed in ``<folder>/run.json``. Without ``--seed``, a fresh
  seed is drawn. A launched session then adopts each repository (on Sonnet), leaving its logs and reports in
  ``<folder>/outputs/<repository>/``.
- ``read``: read what that adoption left; ask each question set of ``gov retrieve`` (``--gov``); start a reader and a
  grader session per question (``--claude``, both on ``claude-sonnet-5-5``) and judge memory end to end; land a
  ticket in each repository with ``<pinned gov> queue <ticket>`` (``--pinned-gov``, ``--queue-ticket``); judge; write
  the report. Only the sessions and the landing run: it never adopts.
- ``run``: ``build``, then the adoption stages that need no session (``--stages``, by default A0, A1 and A2) run
  with ``--gov`` in each repository, then as ``read``.
- ``--adopter-model <id>``: the model the adopting sessions ran; recorded in ``run.json``'s ``models`` block beside
  the reader's and the grader's, with the release version read from ``<pinned gov> --version`` (the pinned install,
  never a fixed number). A run record without that model line, or with any of the three not ``claude-sonnet-5-5``, is
  refused: ``refused: ...`` on standard error, exit 2, before any stage, search or session runs.
- The report: ``<folder>/report.json`` and ``<folder>/report.md`` (the end-to-end figure per repository first and
  decisive; hit@5 and the stacked share beside it, diagnostic); a log of steps, ``<folder>/run.log``; each question's
  verdict row (its answer text included) under ``<folder>/e2e/<repository>/``.

The hidden half is read only from ``--hidden``, or from the default hidden folder when that exists; a ``--hidden``
that names no existing folder is refused. ``--sets-root <root>`` (W2-93, DEC-1144 (6)) names the evaluation sets' root
instead, and the hidden folder is ``<root>/HIDDEN_UNDER_SETS_ROOT``, read exactly as ``--hidden`` is: a root without it
is refused (``--sets-root holds no hidden half: <that relative path>``, exit 2, in every mode, before anything is
built), and ``--sets-root`` with ``--hidden`` is refused, so neither a person nor a session names the hidden folder on
a command line. READY needs it present and asked in every repository: at least
``HIDDEN_NEEDED`` (10) hidden questions each. Its questions are named by id only, and its variants by number and id;
its texts and answers are in no report, log or output (only the verdict rows hold an answer). The secrets' values are
drawn from the seed in memory and are in no report, log or output either (checked before anything is written). The
runner writes nothing in this repository, never reads the workbench and never uses the dev-tier variable.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets as random_source
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_81_build as build  # noqa: E402
import w2_81_e2e as e2e  # noqa: E402
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
# The measurement half's size: at least 10 hidden questions per repository (docs/plan/WAVE_2_WBS.md, the card
# "W2-81's held-out half", its first KPI). A repository with fewer is not counted present (README, "The runner").
HIDDEN_NEEDED = 10
# Where the hidden half sits under an evaluation sets' root (the sets' convention, as gov.retrieval.measure and
# gov.memaudit use ``<sets-root>/fixtures/evaluation/<set>/hidden/``): the one place ``--sets-root`` reads.
HIDDEN_UNDER_SETS_ROOT = "fixtures/evaluation/adoption-proving-ground/hidden"


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


def _env(folder, notify=None):
    home, tmp = folder / ".home", folder / ".tmp"
    home.mkdir(exist_ok=True)
    tmp.mkdir(exist_ok=True)
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home), "TMPDIR": str(tmp),
           "LC_ALL": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_AUTHOR_NAME": "W2-81 runner", "GIT_AUTHOR_EMAIL": "w2-81-runner@example.invalid",
           "GIT_COMMITTER_NAME": "W2-81 runner", "GIT_COMMITTER_EMAIL": "w2-81-runner@example.invalid"}
    env.update({k: v for k, v in os.environ.items() if k == "GOV_REBUILD_LOCK"})
    if notify:  # the starter's inbox address: without it the product's launcher defaults to the live CTO's (T10)
        env["GOV_MSG_ADDRESS"] = notify
    return env


def _owner_exceptions(options):
    """The owner's exceptions (``--exceptions <file>``), checked, or None: a file that cannot be read, with no decision
    of the form DEC-<digits>, whose reasons are not a list of non-empty strings, or with a duplicate id is refused
    (``refused: <file>: <fault>``, exit 2), before anything is built, started or asked."""
    given = getattr(options, "exceptions", None)
    if not given:
        return None
    try:
        return judge.load_exceptions(Path(given).expanduser())
    except judge.ExceptionsError as refused:
        raise RunnerError(str(refused)) from None


def _queue_env(env):
    """The landing's environment: the run's own (``_env``) with the operator's ``HOME``, the runner process's own. The
    pinned ``gov queue`` runs the repository's tests, and the tools they need (pytest) live in the operator's user
    site; the scrubbed ``HOME`` suits retrieval's isolation, not the landing (the proving run on 0.1.4, T1)."""
    landing = {k: v for k, v in env.items() if k != "HOME"}
    if "HOME" in os.environ:
        landing["HOME"] = os.environ["HOME"]
    return landing


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


def _hidden_folder(options):
    """The folder the hidden half is read from, or None for the default; a refusal when the options name a wrong one.

    ``--sets-root`` and ``--hidden`` together are refused, and a sets root without its hidden folder is refused naming
    the folder relative to the root (never the root's own path)."""
    sets_root = getattr(options, "sets_root", None)
    if sets_root and options.hidden:
        raise RunnerError("--sets-root and --hidden are both given: name the sets root or the hidden folder, not both")
    if sets_root:
        folder = Path(sets_root).expanduser() / HIDDEN_UNDER_SETS_ROOT
        if not folder.is_dir():
            raise RunnerError(f"--sets-root holds no hidden half: {HIDDEN_UNDER_SETS_ROOT}")
        return folder
    if options.hidden and not Path(options.hidden).expanduser().is_dir():
        raise RunnerError("--hidden names no existing folder: the measurement half cannot be read")
    return Path(options.hidden).expanduser() if options.hidden else None


def _hidden(options):
    folder = _hidden_folder(options) or questions.HIDDEN_DEFAULT
    if not folder.is_dir():
        return None, [], {}
    variants = []
    if (folder / "variants.yaml").is_file():
        try:  # a hidden file that cannot be read is refused naming the file only: never its text
            data = yaml.safe_load((folder / "variants.yaml").read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, yaml.YAMLError):
            raise RunnerError("the hidden file variants.yaml cannot be read") from None
        variants = data.get("variants") if isinstance(data, dict) else None
        if not isinstance(variants, list) or not all(isinstance(v, dict) for v in variants):
            raise RunnerError("the hidden file variants.yaml holds no list `variants` of mappings")
    try:
        sets = {path.stem: questions.load_set(path) for path in sorted(folder.glob("*.yaml"))
                if path.stem != "variants"}
    except questions.QuestionError as refused:
        raise RunnerError(str(refused)) from None
    return folder, variants, sets


def _retrieve(gov, root, question, env, log):
    """The stacked context of one question, as gov.retrieval.measure stacks it: (path, start, end, text) items, in
    order, each taken once; None when ``gov retrieve`` failed. ``question`` holds ``id`` and ``question``."""
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
            stacked.append(item)
            used += size
        token = bundle.get("continuation")
        if full or not token:
            break
    log(f"retrieve {question.id}: {len(stacked)} items")
    return stacked


def _ask(gov, root, question, env, log):
    """The stacked context of one question: (path, start, end) items, or None when the retrieval failed."""
    items = _retrieve(gov, root, question, env, log)
    return None if items is None else [item[:3] for item in items]


def _search(gov, root, words, env):
    """The reader's one more search, in its own words: one ``gov retrieve`` bundle as (path, start, end, text)."""
    done = subprocess.run([gov, "retrieve", words, "--json"], cwd=root, env=env, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL)
    try:
        doc = json.loads(done.stdout)
        bundle = doc["result"] if isinstance(doc.get("result"), dict) else doc
        return [(str(i["path"]), int(i["start_line"]), int(i["end_line"]), str(i.get("text", "")))
                for i in bundle["evidence"]] if done.returncode == 0 and doc.get("ok") is not False else []
    except (ValueError, KeyError, TypeError, AttributeError):
        return []


def _judge_end_to_end(options, name, repo, asked, stacks, env, log, folder, session):
    """The reader and the grader on each question whose retrieval answered: ``{question id: verdicts}``. Each
    question's row (its answers included) is written under ``<folder>/e2e/<repository>/``, and nowhere else."""
    where = folder / "e2e"
    (where / name).mkdir(parents=True, exist_ok=True)
    caller = e2e.Caller(options.claude, session, where)
    todo = [q for q in asked if stacks.get(q.id) is not None]

    def one(question):
        return e2e.ask(question, stacks[question.id], lambda words: _search(options.gov, repo.root, words, env),
                       caller)
    with ThreadPoolExecutor(e2e.WORKERS) as pool:
        done = list(pool.map(one, todo))
    verdicts = {}
    for question, result in zip(todo, done):
        verdicts[question.id] = {"reader": result["reader"], "grader": result["grader"]}
        (where / name / f"{question.id}.json").write_text(json.dumps(result["row"], indent=2) + "\n",
                                                          encoding="utf-8")
        log(f"judge {question.id}: reader {result['reader']['verdict']}, grade {result['grader']}")
    return verdicts


_VERSION = re.compile(r"^gov (\d[0-9A-Za-z.+-]*)(?: |$)")


def _release(pinned_gov):
    """The release version read from the pinned install (``<pinned gov> --version``), or None."""
    if not pinned_gov:
        return None
    try:
        done = subprocess.run([pinned_gov, "--version"], capture_output=True, text=True, stdin=subprocess.DEVNULL,
                              env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C.UTF-8"})
    except OSError:
        return None
    found = _VERSION.match(done.stdout.strip()) if done.returncode == 0 else None
    return found.group(1) if found else None


def _model_line(options, record):
    """The run record with its model line: the adopter as ``--adopter-model`` says (else as the record says), the
    reader and the grader as the record says (else ``E2E_MODEL``, which this runner starts them on), and the release
    read from the pinned install. Refused unless every session is ``E2E_MODEL`` and a release is read."""
    given = record.get("models") if record.get("models") is not None else {}
    models = {"adopter": options.adopter_model or given.get("adopter"),
              "reader": given.get("reader", score.E2E_MODEL), "grader": given.get("grader", score.E2E_MODEL)
              } if isinstance(given, dict) else given  # a record's models that is no mapping is refused as it stands
    record = {**record, "models": models, "release": _release(options.pinned_gov)}
    reasons = score.check_models(record)
    if reasons:
        raise RunnerError("the run record's model line: " + "; ".join(reasons))
    return record


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
    manifests = gitlib.outside_this_repository(Path(options.manifests).expanduser()) if options.manifests else folder
    if (manifests / "manifests").is_dir() and any((manifests / "manifests").glob("*.json")):
        raise RunnerError(f"{manifests / 'manifests'} already holds manifests: a build needs a manifests folder "
                          "of its own (another run's would be overwritten)")
    try:
        built = build.build_all(folder, seed, options.large_size, manifests_root=manifests, variants=variants)
    except build.VariantError as refused:
        raise RunnerError(str(refused)) from None
    record = {"form": "w2-81-run/1", "seed": seed, "large_size": options.large_size,
              "manifests": str(manifests / "manifests"), "hidden_variants": len(variants),
              "heads": {name: b.manifest["head"] for name, b in built.items()}}
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
        try:
            manifest = manifest_form.load(path)
        except (OSError, ValueError, AssertionError):
            raise RunnerError(f"the manifest of {name} cannot be read") from None
        if manifest["seed"] != record["seed"] or manifest["head"] != (record.get("heads") or {}).get(name):
            raise RunnerError(f"the manifest of {name} is not this run's: its seed or head is not the run's record "
                              "(another build wrote its manifests folder)")
        out[name] = _Repository(name, folder / "repos" / name, manifest, path, held_secrets(manifest))
    return record, out


def follow_moves(asked, moves):
    """A planted file moved by a reviewed action is still itself: its forbidden citation and its gold source follow it
    to its new place (the judge holds the move to the file's content as built)."""
    for q in asked:
        q.forbidden = q.forbidden + [moves[p] for p in q.forbidden if p in moves]
        q.sources = [(moves.get(p, p), line, holds) for p, line, holds in q.sources]
    return asked


def run(options, built=None, session=None):
    """The run, with the starter's address in the environment of every process it starts. The address is
    ``--notify`` (``options.notify``), else the runner process's own ``$GOV_MSG_ADDRESS``, else none (then nothing is
    set: today's behaviour). The reader's and grader's sessions are started by the product's ``run_claude``, which
    inherits this process's environment, so the address is set here for the duration of the run and put back (or
    removed) when it ends, whether in a report or an error. See ``_run`` for the rest."""
    notify = getattr(options, "notify", None) or os.environ.get("GOV_MSG_ADDRESS") or None
    before = os.environ.get("GOV_MSG_ADDRESS")
    if notify:
        os.environ["GOV_MSG_ADDRESS"] = notify
    try:
        return _run(options, built, session, notify)
    finally:
        if before is None:
            os.environ.pop("GOV_MSG_ADDRESS", None)
        else:
            os.environ["GOV_MSG_ADDRESS"] = before


def _run(options, built, session, notify):
    """The run; returns the report (also written in the folder). ``built``: the capabilities counted as built (the
    judge's ``built``); the command leaves it to today's code, and only the self-tests pass it. ``session``: the
    function that starts a reader or grader session, ``start(argv, prompt, cwd) -> standard output``; the command
    leaves it to the product's ``run_claude``, and only the self-tests pass a stand-in (no model runs)."""
    exceptions = _owner_exceptions(options)  # a faulty exceptions file is refused before any work
    _hidden_folder(options)  # a wrong --sets-root or --hidden is refused first, before anything is built or written
    folder = _refuse_place(options.folder)
    if options.mode == "run":
        _model_line(options, {})  # a refused model line builds nothing
    log = _Log()
    if options.mode in ("build", "run"):
        _build(options, folder, log)
    if options.mode == "build":
        _write_log(folder, log, [])
        return {"mode": "build", "seed": json.loads((folder / "run.json").read_text())["seed"]}
    record, repos = _read_back(folder)
    if options.mode in ("read", "run"):  # before any stage, search or session: the model line, or a refusal
        record = _model_line(options, record)
        (folder / "run.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    env = _env(folder, notify)
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
    _, _, hidden_sets = _hidden(options)
    scores, hidden = [], {}
    for name, repo in repos.items():
        asked = questions.resolve(questions.load_set(questions.VISIBLE / f"{name}.yaml"), repo.manifest, repo.root,
                                  "visible")
        secret_half = questions.resolve(hidden_sets[name], repo.manifest, repo.root, "hidden") \
            if name in hidden_sets else []
        asked += secret_half
        count = len(secret_half)
        hidden[name] = {"questions": count, "asked": count if options.gov else 0, "needed": HIDDEN_NEEDED,
                        "present": bool(options.gov) and count >= HIDDEN_NEEDED}
        follow_moves(asked, judge.reviewed_moves(repo.root))
        if options.gov:
            stacks = {q.id: _retrieve(options.gov, repo.root, q, env, log) for q in asked}
            answers = {qid: None if items is None else [i[:3] for i in items] for qid, items in stacks.items()}
            verdicts = _judge_end_to_end(options, name, repo, asked, stacks, env, log, folder,
                                         session or e2e.run_claude)
            scores.append(score.score_repository(name, asked, answers, verdicts))
        else:  # no retrieval, no session: nothing measured, so no figure
            scores.append({"repository": name, "questions": len(asked), "end_to_end": None, "right": None,
                           "bar": score.E2E_BAR, "met": False, "per_question": [],
                           "diagnostic": {"hit_at_5": None, "stacked_share": None}})
    tickets = _tickets(options.queue_ticket)
    lands = {}  # the LITE ticket cycle ends at the landing, gov queue (EMERGENCY-2 4.3), never gov close
    for name, repo in repos.items():
        if not options.pinned_gov or not tickets.get(name):
            lands[name] = {"run": False}
            continue
        done = subprocess.run([options.pinned_gov, "queue", tickets[name]], cwd=repo.root, env=_queue_env(env),
                              capture_output=True, text=True)
        lands[name] = {"run": True, "ticket": tickets[name], "exit": done.returncode}
        log(f"queue {name} {tickets[name]}: exit {done.returncode}")
    cases = [(repo.manifest, repo.root, folder / "outputs" / name, repo.secrets) for name, repo in repos.items()]
    judged = judge.judge(cases, score.figures(scores), EXPECTED, built, run_folder=folder, exceptions=exceptions)
    own = []  # the runner's own reasons: no exceptions file excuses them (the landing, the hidden half, the stages)
    for name in EXPECTED:
        if not hidden[name]["present"]:
            own.append(f"{name}: the measurement (hidden) half is not present and asked: {hidden[name]['asked']} "
                       f"hidden questions asked, at least {HIDDEN_NEEDED} needed")
        land = lands[name]
        if not land["run"]:
            own.append(f"{name}: gov queue was not run")
        elif land["exit"] != 0:
            own.append(f"{name}: gov queue {land['ticket']} ended with exit {land['exit']}")
        failed = [s for s in stage_runs.get(name, []) if s.get("run") and s["exit"] != 0]
        own += [f"{name}: gov adopt --lite --stage {s['stage']} ended with exit {s['exit']}" for s in failed]
    reasons = list(judged["reasons"]) + own
    # in step with the reasons: the judge's ids, and none (null) for the runner's own, which no file can name
    reason_ids = list(judged.get("reason_ids") or []) + [None] * len(own)
    verdict = judged["verdict"] if judged["verdict"] == judge.ERROR else (
        judge.NOT_READY if own else judged["verdict"])  # READY, READY_WITH_EXCEPTIONS or NOT_READY, as the judge says
    by_name = {j["repository"]: j for j in judged.get("repositories", [])}
    report = {"form": "w2-81-report/1", "mode": options.mode, "seed": record["seed"], "verdict": verdict,
              "reasons": reasons, "reason_ids": reason_ids, "hidden_half": _hidden_summary(hidden),
              "gov": options.gov, "pinned_gov": options.pinned_gov,
              "models": record.get("models"), "release": record.get("release"), "bar": score.E2E_BAR,
              "repositories": {name: {"judgement": by_name.get(name), "figures": next(
                  ({k: s[k] for k in ("questions", "right", "end_to_end", "bar", "met", "diagnostic",
                                      "per_question")} for s in scores if s["repository"] == name), None),
                  "not_built": (by_name.get(name) or {}).get("not_built"), "queue": lands[name],
                  "hidden_half": hidden[name],
                  "stages_run": stage_runs.get(name, [])} for name in EXPECTED}}
    if exceptions is not None and judged.get("exceptions"):
        report["exceptions"] = judged["exceptions"]  # the decision and the ids named, unnamed and unused
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


def _hidden_summary(hidden):
    """The measurement half in one line: present and asked in how many repositories of all."""
    present = sum(1 for h in hidden.values() if h["present"])
    if present == len(hidden):
        return f"present and asked in {present} of {len(hidden)} repositories"
    return f"absent in {len(hidden) - present} of {len(hidden)} repositories"


def _write_log(folder, log, reasons):
    (folder / "run.log").write_text("\n".join(log.lines + [f"reason: {r}" for r in reasons]) + "\n",
                                    encoding="utf-8")


def _markdown(report):
    models = report.get("models") or {}
    rows = [f"# W2-81 proving ground: {report['verdict']}", "", f"Seed {report['seed']}; mode {report['mode']}; "
            f"hidden half {report['hidden_half']}.",
            f"Release {report.get('release')}; sessions: adopter {models.get('adopter')}, reader "
            f"{models.get('reader')}, grader {models.get('grader')}.", ""]
    rows += [f"- {reason}" for reason in report["reasons"]] or ["- every planted problem handled, no control "
                                                                 "flagged, every repository's end-to-end figure at "
                                                                 f"{score.E2E_BAR:g} or more, every landing at exit 0"]
    owner = report.get("exceptions")
    if owner:
        rows += ["", f"Exceptions named in {owner['decision']} (an owner's decision, one id each):"]
        rows += [f"- excepted: `{i}`" for i in owner["named"]] or ["- none of the reasons"]
        rows += [f"- not named, so still a reason: `{i}`" for i in owner.get("unnamed", [])]
        rows += [f"- named, matching no reason: `{i}`" for i in owner["unused"]]
    for name, repo in report["repositories"].items():
        j, f = repo["judgement"] or {}, repo["figures"] or {}
        diagnostic = f.get("diagnostic") or {}
        rows += ["", f"## {name}", "", f"End-to-end figure {f.get('end_to_end')} (bar {score.E2E_BAR:g}; "
                 f"{f.get('right')} of {f.get('questions')} questions judged right); diagnostic, never a bar: "
                 f"hit@5 {diagnostic.get('hit_at_5')}, stacked share {diagnostic.get('stacked_share')}; "
                 f"gov queue: {repo['queue']}; not built: {', '.join(repo['not_built'] or []) or 'none'}; "
                 f"hidden half: {_hidden_line(repo.get('hidden_half'))}", "",
                 "| Planted problem | Status | Evidence |", "|---|---|---|"]
        rows += [f"| `{p['id']}` | {p['status']} | {p['evidence'][0]['said']} |" for p in j.get("planted", [])]
        rows += [""] + [f"Not measured: {item}" for item in j.get("not_measured") or []]  # the JSON's own words
        rows += ["", "| Control | Status |", "|---|---|"]
        rows += [f"| `{c['id']}` | {c['status']} |" for c in j.get("controls", [])]
    return "\n".join(rows) + "\n"


def _hidden_line(half):
    if not half:
        return "not read"
    state = "present and asked" if half["present"] else "not present"
    return f"{state} ({half['asked']} hidden questions asked, at least {half['needed']} needed)"


def parse(argv):
    parser = argparse.ArgumentParser(prog="w2_81_run.py", description="the W2-81 proving ground's real run")
    parser.add_argument("--folder", required=True)
    parser.add_argument("--mode", choices=("build", "run", "read"), default="run")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--gov", default=None)
    parser.add_argument("--pinned-gov", dest="pinned_gov", default=None)
    parser.add_argument("--queue-ticket", dest="queue_ticket", action="append", default=[])
    parser.add_argument("--adopter-model", dest="adopter_model", default=None)
    parser.add_argument("--claude", default="claude")
    parser.add_argument("--hidden", default=None)
    parser.add_argument("--sets-root", dest="sets_root", default=None)
    parser.add_argument("--manifests", default=None)
    parser.add_argument("--large-size", dest="large_size", type=int, default=build.REAL_RUN_LARGE)
    parser.add_argument("--stages", default=None)
    parser.add_argument("--notify", default=None)
    parser.add_argument("--exceptions", default=None)
    return parser.parse_args(argv)


def main(argv=None):
    try:
        report = run(parse(argv))
    except (RunnerError, gitlib.InsideThisRepository, questions.QuestionError) as refused:
        print(f"refused: {refused}", file=sys.stderr)
        return 2
    if "verdict" not in report:
        print(f"BUILT (seed {report['seed']})")
        return 0
    excepted = f"; exceptions named in {report['exceptions']['decision']}" if report.get("exceptions") else ""
    print(f"{report['verdict']} (seed {report['seed']}; hidden half: {report.get('hidden_half', 'not read')}{excepted})")
    return 0 if report.get("verdict", judge.READY) in judge.READY_VERDICTS else 1


if __name__ == "__main__":
    sys.exit(main())
