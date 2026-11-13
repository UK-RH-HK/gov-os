### tests.acceptance.W2-171.test_w2_171_s4_fault::test_s4_a_fault_in_the_first_attempt_is_kept_never_counted_and_one_restart_passes[rerank-degraded]
```
world = <w2_171_world.World object at 0x70a52c45d310>, fault = 'rerank'
cause = 'degraded'

    @pytest.mark.parametrize("fault,cause", [("rerank", "degraded"), ("semantic_missing", "degraded"),
                                             ("pool", "degraded"), ("exit", "exit")])
    def test_s4_a_fault_in_the_first_attempt_is_kept_never_counted_and_one_restart_passes(world, fault, cause):
        SC.install(world, gov_edit=fault_at(1, fault=fault))
        run = world.measure()
        assert run.code == 0, run
        assert causes(world) == {"attempt-1": cause}, causes(world)
        assert not (world.attempt_dir(1) / "DONE").exists() and (world.attempt_dir(2) / "DONE").is_file()
        assert (world.run_dir / "COUNTS").read_text().strip() == "attempt-2"
        assert (world.run_dir / "control-1").is_dir() and (world.run_dir / "control-2").is_dir(), \
            "the ready check, the probe and a new control, again before the restart"
        expected = S.Expected(SC, world)
        assert [x for x in run.lines if x.startswith("RETRIEVAL")] == [expected.retrieval_line(2)], \
            "a faulted attempt's figures are never printed"
        states = [(e["n"], e["state"], e["cause"]) for e in world.events("attempt")]
        assert states == [(1, "start", None), (1, "fault", cause), (2, "start", None), (2, "done", None)], states
        assert [e["ok"] for e in world.events("ready")] == [True, True]
>       assert world.events("counts")[0]["attempt"] == "attempt-2"
E       AssertionError: assert 2 == 'attempt-2'

tests/acceptance/W2-171/test_w2_171_s4_fault.py:55: AssertionError
```

### tests.acceptance.W2-171.test_w2_171_s4_fault::test_s4_a_fault_in_the_first_attempt_is_kept_never_counted_and_one_restart_passes[semantic_missing-degraded]
```
world = <w2_171_world.World object at 0x70a524f7f170>
fault = 'semantic_missing', cause = 'degraded'

    @pytest.mark.parametrize("fault,cause", [("rerank", "degraded"), ("semantic_missing", "degraded"),
                                             ("pool", "degraded"), ("exit", "exit")])
    def test_s4_a_fault_in_the_first_attempt_is_kept_never_counted_and_one_restart_passes(world, fault, cause):
        SC.install(world, gov_edit=fault_at(1, fault=fault))
        run = world.measure()
        assert run.code == 0, run
        assert causes(world) == {"attempt-1": cause}, causes(world)
        assert not (world.attempt_dir(1) / "DONE").exists() and (world.attempt_dir(2) / "DONE").is_file()
        assert (world.run_dir / "COUNTS").read_text().strip() == "attempt-2"
        assert (world.run_dir / "control-1").is_dir() and (world.run_dir / "control-2").is_dir(), \
            "the ready check, the probe and a new control, again before the restart"
        expected = S.Expected(SC, world)
        assert [x for x in run.lines if x.startswith("RETRIEVAL")] == [expected.retrieval_line(2)], \
            "a faulted attempt's figures are never printed"
        states = [(e["n"], e["state"], e["cause"]) for e in world.events("attempt")]
        assert states == [(1, "start", None), (1, "fault", cause), (2, "start", None), (2, "done", None)], states
        assert [e["ok"] for e in world.events("ready")] == [True, True]
>       assert world.events("counts")[0]["attempt"] == "attempt-2"
E       AssertionError: assert 2 == 'attempt-2'

tests/acceptance/W2-171/test_w2_171_s4_fault.py:55: AssertionError
```

### tests.acceptance.W2-171.test_w2_171_s4_fault::test_s4_a_fault_in_the_first_attempt_is_kept_never_counted_and_one_restart_passes[pool-degraded]
```
world = <w2_171_world.World object at 0x70a52cb9b530>, fault = 'pool'
cause = 'degraded'

    @pytest.mark.parametrize("fault,cause", [("rerank", "degraded"), ("semantic_missing", "degraded"),
                                             ("pool", "degraded"), ("exit", "exit")])
    def test_s4_a_fault_in_the_first_attempt_is_kept_never_counted_and_one_restart_passes(world, fault, cause):
        SC.install(world, gov_edit=fault_at(1, fault=fault))
        run = world.measure()
        assert run.code == 0, run
        assert causes(world) == {"attempt-1": cause}, causes(world)
        assert not (world.attempt_dir(1) / "DONE").exists() and (world.attempt_dir(2) / "DONE").is_file()
        assert (world.run_dir / "COUNTS").read_text().strip() == "attempt-2"
        assert (world.run_dir / "control-1").is_dir() and (world.run_dir / "control-2").is_dir(), \
            "the ready check, the probe and a new control, again before the restart"
        expected = S.Expected(SC, world)
        assert [x for x in run.lines if x.startswith("RETRIEVAL")] == [expected.retrieval_line(2)], \
            "a faulted attempt's figures are never printed"
        states = [(e["n"], e["state"], e["cause"]) for e in world.events("attempt")]
        assert states == [(1, "start", None), (1, "fault", cause), (2, "start", None), (2, "done", None)], states
        assert [e["ok"] for e in world.events("ready")] == [True, True]
>       assert world.events("counts")[0]["attempt"] == "attempt-2"
E       AssertionError: assert 2 == 'attempt-2'

tests/acceptance/W2-171/test_w2_171_s4_fault.py:55: AssertionError
```

### tests.acceptance.W2-171.test_w2_171_s4_fault::test_s4_a_fault_in_the_first_attempt_is_kept_never_counted_and_one_restart_passes[exit-exit]
```
world = <w2_171_world.World object at 0x70a527ae5370>, fault = 'exit'
cause = 'exit'

    @pytest.mark.parametrize("fault,cause", [("rerank", "degraded"), ("semantic_missing", "degraded"),
                                             ("pool", "degraded"), ("exit", "exit")])
    def test_s4_a_fault_in_the_first_attempt_is_kept_never_counted_and_one_restart_passes(world, fault, cause):
        SC.install(world, gov_edit=fault_at(1, fault=fault))
        run = world.measure()
        assert run.code == 0, run
        assert causes(world) == {"attempt-1": cause}, causes(world)
        assert not (world.attempt_dir(1) / "DONE").exists() and (world.attempt_dir(2) / "DONE").is_file()
        assert (world.run_dir / "COUNTS").read_text().strip() == "attempt-2"
        assert (world.run_dir / "control-1").is_dir() and (world.run_dir / "control-2").is_dir(), \
            "the ready check, the probe and a new control, again before the restart"
        expected = S.Expected(SC, world)
        assert [x for x in run.lines if x.startswith("RETRIEVAL")] == [expected.retrieval_line(2)], \
            "a faulted attempt's figures are never printed"
        states = [(e["n"], e["state"], e["cause"]) for e in world.events("attempt")]
        assert states == [(1, "start", None), (1, "fault", cause), (2, "start", None), (2, "done", None)], states
        assert [e["ok"] for e in world.events("ready")] == [True, True]
>       assert world.events("counts")[0]["attempt"] == "attempt-2"
E       AssertionError: assert 2 == 'attempt-2'

tests/acceptance/W2-171/test_w2_171_s4_fault.py:55: AssertionError
```

### tests.acceptance.W2-171.test_w2_171_cli_layout_ledger::test_the_ledger_events_have_item_3s_fields
```
make_world = <function make_world.<locals>.make at 0x7b0c03206700>

    def test_the_ledger_events_have_item_3s_fields(make_world):
        world = make_world("judged:five")
        ledger = world.ledger()
        assert [e["seq"] for e in ledger] == list(range(1, len(ledger) + 1)), "seq consecutive"
        assert all(ISO.match(e["at"]) for e in ledger), "at is ISO UTC to the microsecond"
        by = {}
        for e in ledger:
            by.setdefault(e["event"], []).append(e)
        assert set(by) >= {"preflight", "declaration", "used", "ready", "control", "search", "attempt", "store", "counts",
                           "spend", "figures"}, sorted(by)
        ready = by["ready"]
        assert len(ready) == 1 and ready[0]["ok"] is True and ready[0]["why"] is None
        control = by["control"][0]
        assert {"k", "hit5", "of", "last", "last_audit", "ok"} <= set(control) and control["of"] == 40
        searches = by["search"]
        assert {"phase", "attempt", "call", "qid", "rc", "ms", "ok"} <= set(searches[0])
        phases = {p: [e for e in searches if e["phase"] == p] for p in ("ready", "control", "attempt", "later")}
        assert all(phases.values()) and {e["phase"] for e in searches} == set(phases)
        assert len(phases["ready"]) == 1 and len(phases["control"]) == 40
        kept = len(list((world.attempt_dir(1) / "kept").glob("*.json")))
        assert len(phases["attempt"]) == kept
        assert sorted(e["call"] for e in phases["attempt"]) == list(range(1, kept + 1)), "call is the kept number"
        assert all(e["qid"] is None for e in phases["attempt"]) and all(e["qid"] for e in phases["later"])
        assert all(isinstance(e["ms"], int) and e["ms"] >= 0 for e in searches)
        assert [(e["n"], e["state"], e["cause"]) for e in by["attempt"]] == [(1, "start", None), (1, "done", None)]
        store = by["store"][0]
        assert (store["n"], store["same"], store["sha256"]) == (1, True, W.sha_file(world.store))
>       assert by["counts"][0]["attempt"] == "attempt-1"
E       AssertionError: assert 1 == 'attempt-1'

tests/acceptance/W2-171/test_w2_171_cli_layout_ledger.py:118: AssertionError
```

### tests.acceptance.W2-171.test_w2_171_cli_layout_ledger::test_the_ledger_after_a_whole_measure_ends_with_counts
```
world = <w2_171_world.World object at 0x7b0c02d1be60>

    def test_the_ledger_after_a_whole_measure_ends_with_counts(world):
        S.SCENARIOS["five"].install(world)
        assert world.measure().code == 0
        ledger = world.ledger()
>       assert ledger[-1]["event"] == "counts" and ledger[-1]["attempt"] == "attempt-1"
E       AssertionError: assert ('counts' == 'counts'
E         
E           counts and 1 == 'attempt-1')

tests/acceptance/W2-171/test_w2_171_cli_layout_ledger.py:130: AssertionError
```

### tests.acceptance.W2-171.test_w2_171_s1_control::test_s1_a_missing_control_set_ends_the_ready_check
```
world = <w2_171_world.World object at 0x7b0c02d916d0>

    def test_s1_a_missing_control_set_ends_the_ready_check(world):
        """The CTO's ruling 9: no session opens the sets root to confirm the control's set; a missing set is
        ``STOPPED notready`` and the first live run shows it."""
        _scenario(34).install(world)
        shutil.rmtree(world.sets / "fixtures" / "evaluation" / "memory-retrieval" / "visible")
        run = world.measure()
>       assert run.code == 2 and "STOPPED notready" in run.lines, run
E       AssertionError: <exit 2; stdout 'DECLARED: audit commit a6cdbe0e00df, n 40, set digest acb780108dde
E         USED written
E         CONTROL control-1: hit@5 0 of 0; last 34; control out of range
E         STOPPED control
E         '; stderr ''>
E       assert (2 == 2 and 'STOPPED notready' in ['DECLARED: audit commit a6cdbe0e00df, n 40, set digest acb780108dde', 'USED written', 'CONTROL control-1: hit@5 0 of 0; last 34; control out of range', 'STOPPED control'])
E        +  where 2 = <exit 2; stdout 'DECLARED: audit commit a6cdbe0e00df, n 40, set digest acb780108dde\nUSED written\nCONTROL control-1: hit@5 0 of 0; last 34; control out of range\nSTOPPED control\n'; stderr ''>.code
E        +  and   ['DECLARED: audit commit a6cdbe0e00df, n 40, set digest acb780108dde', 'USED written', 'CONTROL control-1: hit@5 0 of 0; last 34; control out of range', 'STOPPED control'] = <exit 2; stdout 'DECLARED: audit commit a6cdbe0e00df, n 40, set digest acb780108dde\nUSED written\nCONTROL control-1: hit@5 0 of 0; last 34; control out of range\nSTOPPED control\n'; stderr ''>.lines

tests/acceptance/W2-171/test_w2_171_s1_control.py:123: AssertionError
```

### tests.acceptance.W2-171.test_w2_171_s2_measure::test_s2_the_counting_attempt_prints_the_planted_figures_and_keeps_every_output
```
world = <w2_171_world.World object at 0x7b0c02def710>

    def test_s2_the_counting_attempt_prints_the_planted_figures_and_keeps_every_output(world):
        SC.install(world)
        run = world.measure()
        assert run.code == 0, run
        expected = S.Expected(SC, world)
        retrieval = [x for x in run.lines if x.startswith("RETRIEVAL")]
        assert retrieval == [expected.retrieval_line(1)], (retrieval, expected.retrieval_line(1))
        attempt = world.attempt_dir(1)
        # the measure's own question lines carry the planted ranks, in file-name order
        lines = world.question_lines(attempt)
        assert [q for q, *_ in lines] == [f"q{i:02d}" for i in range(1, 41)]
        assert all(part == "hidden" for _, part, *_ in lines)
        assert {q: rank for q, _, _, rank, _, _ in lines} == dict(SC.ranks)
        assert {q: bundle for q, _, _, _, bundle, _ in lines} == {q: SC.in_bundle(q) for q in SC.ranks}
        # every search's output kept, in call order
        kept = sorted((attempt / "kept").glob("*.json"))
        calls_per_question = {q: len(S.calls_for(r)) for q, r in SC.ranks.items()}
        assert len(kept) == sum(calls_per_question.values())
        assert [p.name for p in kept] == [f"{i:05d}.json" for i in range(1, len(kept) + 1)]
        for path in kept:
            doc = json.loads(path.read_text())
            assert isinstance(doc["result"]["evidence"], list)
        ms = (attempt / "ms").read_text().split()
        assert len(ms) == len(kept) and all(x.replace(".", "", 1).isdigit() for x in ms)
        for name in ("measure.txt", "measure.err", "ENDED", "DONE"):
            assert (attempt / name).is_file(), name
        assert not (attempt / "FAULT").exists()
        assert (world.run_dir / "COUNTS").read_text().strip() == "attempt-1"
>       assert world.events("counts")[0]["attempt"] == "attempt-1"
E       AssertionError: assert 1 == 'attempt-1'

tests/acceptance/W2-171/test_w2_171_s2_measure.py:51: AssertionError
```
