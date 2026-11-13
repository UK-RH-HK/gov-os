p = "tests/unit/adopt/test_w2_88_run4.py"
s = open(p).read()

s = s.replace('''@pytest.mark.parametrize("attr, value, setting", [("MODEL", "Org/Other-Reranker", "reranker"),
                                                  ("SOCKET", "private.sock", "reranker_service"),
                                                  ("BUNDLE_BUDGET", 4000, "bundle_tokens")])
def test_a_changed_constant_is_a_departure_that_a_decision_names(tmp_path, monkeypatch, attr, value, setting):
    from gov.retrieval import rerank, retrieve

    monkeypatch.setattr(retrieve if attr == "BUNDLE_BUDGET" else rerank, attr, value)
    root = planted(tmp_path)
    with pytest.raises(GovError) as raised:
        fabric.read_standard(root, [])
    assert raised.value.code == "STANDARD_DEPARTURE" and raised.value.details["settings"] == [setting]
    for decision in (["DEC-1"], [f"DEC-1:{setting}"]):
        block = fabric.read_standard(root, decision)
        assert [item["decision"] for item in block["departures"]] == ["DEC-1"]
''', '''def test_a_changed_constant_is_a_departure_that_a_decision_names(tmp_path, monkeypatch):
    from gov.retrieval import rerank, retrieve

    root = planted(tmp_path)
    for attr, value, setting in (("MODEL", "Org/Other-Reranker", "reranker"), ("SOCKET", "private.sock", "reranker_service"),
                                 ("BUNDLE_BUDGET", 4000, "bundle_tokens")):
        with monkeypatch.context() as patch:
            patch.setattr(retrieve if attr == "BUNDLE_BUDGET" else rerank, attr, value)
            with pytest.raises(GovError) as raised:
                fabric.read_standard(root, [])
            assert raised.value.code == "STANDARD_DEPARTURE" and raised.value.details["settings"] == [setting]
            for decision in (["DEC-1"], [f"DEC-1:{setting}"]):
                block = fabric.read_standard(root, decision)
                assert [item["decision"] for item in block["departures"]] == ["DEC-1"]
''')

s = s.replace('''@pytest.mark.parametrize("key", ["rerank", "bundle"])
def test_a_retrieval_yaml_with_a_rerank_or_bundle_key_is_refused_even_with_a_decision(tmp_path, stand_ins, key):
    doc = {**yaml.safe_load(SHIPPED), key: {"model": "x", "tokens": 1}}
    root = planted(tmp_path, retrieval=yaml.safe_dump(doc))
    for decisions in ([], ["DEC-1099"]):
        with pytest.raises(GovError) as raised:
            run_a9(root, tmp_path / "out", decision=decisions)
        assert raised.value.code == "CONFIG_INVALID" and raised.value.details["keys"] == [key] and key in raised.value.message
    assert not (root / STORE_REL).exists()  # refused before any store is built
''', '''def test_a_retrieval_yaml_with_a_rerank_or_bundle_key_is_refused_even_with_a_decision(tmp_path, stand_ins):
    for key in ("rerank", "bundle"):
        doc = {**yaml.safe_load(SHIPPED), key: {"model": "x", "tokens": 1}}
        root = planted(tmp_path / key, retrieval=yaml.safe_dump(doc))
        for decisions in ([], ["DEC-1099"]):
            with pytest.raises(GovError) as raised:
                run_a9(root, tmp_path / "out", decision=decisions)
            assert raised.value.code == "CONFIG_INVALID" and raised.value.details["keys"] == [key]
            assert key in raised.value.message
        assert not (root / STORE_REL).exists()  # refused before any store is built
''')

s = s.replace('''@pytest.mark.parametrize("reply", [{"available": False, "reason": "FACET_UNAVAILABLE: planted"}, {}, RuntimeError("down")])
def test_an_unavailable_or_failed_vector_scan_is_null_with_its_reason_and_no_proposal(tmp_path, stand_ins, monkeypatch, reply):
    def scan(root, question):
        if isinstance(reply, Exception):
            raise reply
        time.sleep(0.02)
        return reply

    monkeypatch.setattr(fabric, "vector_scan", scan)
    root, out = planted(tmp_path), tmp_path / "out"
    done = run_a9(root, out, budget_ms=1)
    found = head_of(root, done)["scale"]
    assert found["vector_scan_ms"] is None and found["vector_scan_reason"]
    if isinstance(reply, Exception):
        assert "RuntimeError" in found["vector_scan_reason"]
    elif reply:
        assert "planted" in found["vector_scan_reason"]
    assert not (out / "SCALE-PROPOSAL.md").exists() and done["over"] == []
''', '''def test_an_unavailable_or_failed_vector_scan_is_null_with_its_reason_and_no_proposal(tmp_path, stand_ins, monkeypatch):
    for number, reply in enumerate(({"available": False, "reason": "FACET_UNAVAILABLE: planted"}, {}, RuntimeError("down"))):
        def scan(root, question, reply=reply):
            if isinstance(reply, Exception):
                raise reply
            time.sleep(0.02)
            return reply

        with monkeypatch.context() as patch:
            patch.setattr(fabric, "vector_scan", scan)
            root, out = planted(tmp_path / str(number)), tmp_path / f"out{number}"
            done = run_a9(root, out, budget_ms=1)
        found = head_of(root, done)["scale"]
        assert found["vector_scan_ms"] is None and found["vector_scan_reason"]
        if isinstance(reply, Exception):
            assert "RuntimeError" in found["vector_scan_reason"]
        elif reply:
            assert "planted" in found["vector_scan_reason"]
        assert not (out / "SCALE-PROPOSAL.md").exists() and done["over"] == []
''')
open(p, "w").write(s)
