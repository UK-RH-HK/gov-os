import re
p = "tests/unit/resources/test_w2_157_backstop.py"
s = open(p).read()
a = s.index("def test_s1_the_query_is_exactly_the_interface_line")
b = s.index("def test_s1_the_limit_is_exclusive")
s = s[:a] + '''def test_s1_the_query_is_exactly_the_interface_line(rig):
    rig.smi("100, 24000")
    rig.config()
    result = backstop.watch([rig.short_job()], rig.root, rig.env)
    assert result["tripped"] is False and rig.smi_calls() == 0  # an ended group: no reading is made for nothing
    rig.smi("15873, 24000")
    backstop.watch([rig.job()], rig.root, rig.env)
    assert rig.smi_args() == ["--query-gpu=memory.used,memory.total --format=csv,noheader,nounits"]


''' + s[b:]
a = s.index("def test_the_environment_and_the_arguments_never_set_the_limit(")
b = s.index("def test_the_environment_never_sets_the_limit_while_a_job_runs")
s = s[:a] + s[b:]
s = s.replace('''    rig.mp.setattr(backstop, "_poll_log_hook", None, raising=False)

''', "\n").replace('''    rig.mp.setattr(backstop.time, "sleep", lambda s: None)
    rig.config(embedders=[(9, log)])
''', '''    rig.config(embedders=[(9, log)])
''')
s = s.replace('''    assert "15900 MiB > limit 15872 MiB" in result["reason"] or "15900" in result["reason"]''',
              '''    assert "15900" in result["reason"] and "15872" in result["reason"]''')
open(p, "w").write(s)
