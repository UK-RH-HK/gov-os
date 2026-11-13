p = "tests/unit/adopt/test_w2_88_fabric.py"
s = open(p).read()
old = s[s.index("def test_a_setting_other_than_the_standard_is_named_and_not_ok_without_a_decision"):s.index("def test_a_figure_over_the_budget_writes_a_proposal")]
new = '''def test_a_setting_other_than_the_standard_is_named_and_not_ok_without_a_decision(tmp_path, stand_ins, monkeypatch):
    from gov.retrieval import rerank, retrieve

    pool_off = yaml.safe_load(SHIPPED)
    pool_off["pool"]["meaning_uncut"] = False
    root = planted(tmp_path, retrieval=yaml.safe_dump(pool_off))
    monkeypatch.setattr(rerank, "SOCKET", "private.sock")  # a second reranker: the pin's constants (B-1.2)
    monkeypatch.setattr(retrieve, "BUNDLE_BUDGET", 8000)
    with pytest.raises(GovError) as raised:
        run_a9(root, tmp_path / "out")
    assert raised.value.code == "STANDARD_DEPARTURE"
    assert set(raised.value.details["settings"]) == {"pool", "reranker_service", "bundle_tokens"}
    done = run_a9(root, tmp_path / "out", decision=["DEC-1099"])
    head = yaml.safe_load((root / done["record"]).read_text().split("---\\n")[1])
    assert {item["setting"]: item["decision"] for item in head["standard"]["departures"]} == {
        "pool": "DEC-1099", "reranker_service": "DEC-1099", "bundle_tokens": "DEC-1099"}


'''
s = s.replace(old, new)
s = s.replace('''    def slow(where, question, refresh=False, top_k=None):
        time.sleep(0.02)
        return {}

    monkeypatch.setattr("gov.retrieval.semantic.search", slow)''', '''    def slow(where, question):
        time.sleep(0.02)
        return {"available": True, "reason": None}

    monkeypatch.setattr(fabric, "vector_scan", slow)''')
open(p, "w").write(s)
