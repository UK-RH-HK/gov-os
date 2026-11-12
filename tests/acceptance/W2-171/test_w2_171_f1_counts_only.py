"""F1: a question, gold answer, answer or source path in standard output, a log or an error text (Interface 1, 9, 10; F1's
Verify: a planted run on the fake reader and graders with a unique word in a question, a gold answer, an answer and a
source path: grep of standard output, standard error, every log and ``FIGURES.json`` finds each 0 times).

Only ids, counts and digests leave. The places a question or an answer is written are the ones item 9 names: ``misses.jsonl``,
the rows under ``reader/`` and (the retriever's own output) the kept outputs. The planted words: ``yarrowplinth`` in
question ``q07``, ``quibbletonmarsh`` in its gold answer, ``glimmerquaxt`` in its source path, ``marlowbrindle`` in the
reader's answer (and ``fennelwrisk`` in its heading); more in the classes' reasons, a pool question and the fakes'
standard error and broken output.
"""

from __future__ import annotations

import json

import w2_171_pool as P
import w2_171_scenario as S
import w2_171_world as W

CLASSWORD, POOLWORD, GOVERR, CLAUDEERR, GARBAGE = "reasonwordzq", "poolwordzq", "goverrwordzq", "claudeerrwordzq", \
    "garbagewordzq"


def allowed(path, run_dir) -> bool:
    rel = path.relative_to(run_dir)
    # miss-classes.json is the launch script's delivered copy of the auditor's classes: its reasons are its input
    return rel.parts[0] in ("reader", "misses.jsonl", "miss-classes.json") or "kept" in rel.parts


def scan_files(world, words):
    found = []
    for root in (world.sets / "runs", world.home):
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            if path.is_relative_to(world.run_dir) and allowed(path, world.run_dir):
                continue
            data = path.read_bytes().decode("utf-8", "replace")
            found += [(str(path.relative_to(world.base)), w) for w in words if w in data]
    return found


def test_f1_the_planted_words_reach_no_output_no_log_and_no_figures(world):
    sc = S.SCENARIOS["words"]
    sc.install(world)
    runs = [world.measure()]
    assert runs[-1].code == 0, runs[-1]
    runs.append(world.judge())
    assert runs[-1].code == 0, runs[-1]
    expected = S.Expected(sc, world).misses()
    assert any(m["id"] == "q07" for m in expected)
    (world.run_dir / "miss-classes.json").write_text(json.dumps(
        {m["id"]: {"class": "answer_wrong", "reason": f"{CLASSWORD} {m['id']}"} for m in expected}))
    runs.append(world.classes())
    assert runs[-1].code == 0, runs[-1]
    stems = P.plant_pool(world, 30, 20, 25, word=POOLWORD)
    runs.append(world.pool_run())
    assert runs[-1].code == 0, runs[-1]
    runs += [world.measure_kept(1), world.measure(), world.judge(), world.judge(gov=world.gov_other),
             world.pool_run(), world.run("measure", *world.measure_flags(commit="no-such-commit-zq"))]
    codes = [r.code for r in runs[4:]]
    # (a refusal's code where two refusals hold at once is the tool's order: 1 or 3, 3 or 4)
    assert codes[:3] == [0, 3, 3] and codes[3] in (1, 3) and codes[4] == 3 and codes[5] in (3, 4), codes
    words = [*W.UNIQUE, W.HWORD, CLASSWORD, POOLWORD]
    docs = world.docs()
    words += [d["question"] for d in docs.values()] + [d["gold_answer"] for d in docs.values()]
    words += sorted({d["sources"][0]["path"] for d in docs.values()}) + list(stems.values())[:3]
    for run in runs:
        leaked = [w for w in words if w in run.out or w in run.err]
        assert leaked == [], (run.argv[3:5], leaked)
    assert (world.run_dir / "misses.jsonl").read_text().count(W.AWORD) >= 1, "the planted answer is where it belongs"
    assert scan_files(world, words) == [], "every log and file outside misses.jsonl, reader/ and the kept outputs"
    assert W.QWORD not in (world.run_dir / "FIGURES.json").read_text()


def test_f1_a_child_s_standard_error_goes_to_a_file_and_a_broken_answer_is_never_quoted(world):
    sc = S.Scenario("noisy", garbage=f"{GARBAGE} {W.AWORD}", **{k: getattr(S.SCENARIOS["five"], k) for k in (
        "behaviour", "ranks", "routes", "disagree", "retried", "later_fail", "control_hits")})
    sc.install(world)
    env = {"W171_STDERR_WORDS": f"{GOVERR} {CLAUDEERR}"}
    measured = world.measure(env=env)
    judged = world.judge(env=env)
    assert measured.code == 0 and judged.code == 0, (measured, judged)
    for run in (measured, judged):
        assert not any(w in run.out + run.err for w in (GOVERR, CLAUDEERR, GARBAGE, W.AWORD)), run
    holders = [p for p in world.run_dir.rglob("*") if p.is_file() and CLAUDEERR in p.read_bytes().decode("utf-8", "replace")]
    assert holders, "every child's standard error goes to a file in the run folder (the readers' and graders')"
    assert not [p for p in holders if p.name in ("ledger.jsonl", "FIGURES.json", "DECLARATION.json")]
    assert not any(GARBAGE in (world.run_dir / n).read_text() for n in ("FIGURES.json", "ledger.jsonl"))
