"""``govbridge.demo.extract_reads`` (ADAPT of telemetry_context_extract.py@6e7a2a3; I1/BR-AR-0009): a transcript's
file reads and sweep-shaped commands, generic and with no hard-coded run ids (both required changes named in the
DAG's own deliverable line)."""
import json

from govbridge.demo import extract_reads as ermod


def _transcript_line(tool_calls):
    blocks = [{"type": "tool_use", "id": f"t{i}", "name": name, "input": inp}
              for i, (name, inp) in enumerate(tool_calls)]
    return json.dumps({"type": "assistant", "message": {"content": blocks}})


def test_extract_finds_read_tool_calls(tmp_path):
    transcript = tmp_path / "t.jsonl"
    transcript.write_text(
        _transcript_line([("Read", {"file_path": "govbridge/core/exact.py"})]) + "\n", encoding="utf-8"
    )
    result = ermod.extract(str(transcript))
    assert {"path": "govbridge/core/exact.py", "tool": "Read"} in result["reads"]
    assert result["distinct_files_read"] == 1
    assert result["sweep_commands"] == []


def test_extract_finds_a_bash_cat_of_a_named_file(tmp_path):
    transcript = tmp_path / "t.jsonl"
    transcript.write_text(
        _transcript_line([("Bash", {"command": "cat config/corpus-rules.yaml"})]) + "\n", encoding="utf-8"
    )
    result = ermod.extract(str(transcript))
    assert any(r["path"] == "config/corpus-rules.yaml" for r in result["reads"])


def test_classify_bash_detects_sweep_patterns():
    assert ermod.classify_bash("grep -rn foo .")[0] == "sweep"
    assert ermod.classify_bash("find . -name '*.rs'")[0] == "sweep"
    assert ermod.classify_bash("ls -R")[0] == "sweep"
    assert ermod.classify_bash("git ls-tree -r HEAD")[0] == "sweep"
    assert ermod.classify_bash("git grep -n foo")[0] == "sweep"
    assert ermod.classify_bash("git grep -n foo -- govbridge/core")[0] != "sweep"


def test_classify_bash_does_not_flag_a_scoped_targeted_read():
    kind, files = ermod.classify_bash("cat config/corpus-rules.yaml")
    assert kind == "read"
    assert files == ["config/corpus-rules.yaml"]


def test_classify_bash_flags_more_than_25_files_in_one_command():
    files = " ".join(f"f{i}.py" for i in range(30))
    kind, detail = ermod.classify_bash(f"cat {files}")
    assert kind == "sweep"


def test_extract_ignores_non_assistant_lines(tmp_path):
    transcript = tmp_path / "t.jsonl"
    transcript.write_text('{"type": "user", "message": {"content": "hi"}}\n', encoding="utf-8")
    result = ermod.extract(str(transcript))
    assert result["reads"] == []
    assert result["tool_calls"] == {}
