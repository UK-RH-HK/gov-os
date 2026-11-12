"""S1 (and F1's bound): ``gov wait <exit-file> [<max-s>]`` blocks on the exit file, prints the log tail and the job's code."""

from __future__ import annotations

import json

import pytest

import w2_160_support as support


def test_s1_a_job_writing_its_exit_file_after_two_seconds_has_its_code_printed_and_returned(wait, procs):
    base = wait.base()
    procs.job(base, 3, lines=5, delay=2.0)
    result = wait.run(base + ".exit", 30)
    assert result.code == 3, result
    assert "wait: DONE exit 3" in result.out, result
    assert "job-line-5" in result.out, f"the log's tail is printed:\n{result}"
    assert result.elapsed < 20, result


def test_s1_a_never_written_exit_file_at_max_s_1_is_running_exit_124_inside_the_bound(wait):
    result = wait.run(wait.base("never") + ".exit", 1)
    assert result.code == 124, result
    assert "RUNNING" in result.out, result
    assert 0.9 <= result.elapsed < 6.0, f"the wait lasts its bound (1 s) and ends well inside a few seconds:\n{result}"


def test_s1_an_empty_exit_file_is_not_an_exit_file_yet(wait):
    base = wait.base()
    wait.write(base, ".exit", "")
    result = wait.run(base + ".exit", 1)
    assert result.code == 124 and "RUNNING" in result.out, result


@pytest.mark.parametrize("value, capped", [("9999", True), ("571", True), ("570", False), ("1", False)])
def test_s1_a_max_s_over_570_is_capped_and_says_so_on_stderr(wait, value, capped):
    base = wait.base()
    wait.write(base, ".exit", "0\n")
    result = wait.run(base + ".exit", value)
    assert result.code == 0, result
    assert ("capped at 570" in result.err) is capped, result
    if capped:
        assert value in result.err, f"the line names the value given:\n{result}"


@pytest.mark.parametrize("written, expected", [(0, 0), (3, 3), (255, 255), (256, 0), (300, 44)])
def test_s1_the_exit_code_is_the_jobs_code_modulo_256(wait, written, expected):
    base = wait.base()
    wait.write(base, ".exit", f"{written}\n")
    result = wait.run(base + ".exit", 5)
    assert result.code == expected, result
    assert "DONE exit" in result.out, result


def test_s1_a_json_log_prints_the_result_objects_session_id_and_is_error(wait):
    base = wait.base()
    result_object = {"type": "result", "subtype": "success", "session_id": "sess-7e1c4b", "is_error": True,
                     "num_turns": 4, "result": "the work stopped; MARK-END-OF-RESULT"}
    wait.write(base, ".json", "launcher: starting\nlauncher: model ready\n" + json.dumps(result_object) + "\n")
    wait.write(base, ".exit", "1\n")
    result = wait.run(base + ".exit", 5)
    assert result.code == 1, result
    assert "sess-7e1c4b" in result.out, f"the session_id of the last result object:\n{result}"
    assert "is_error" in result.out and "true" in result.out.lower(), f"is_error and its value:\n{result}"
    assert "MARK-END-OF-RESULT" in result.out, f"the end of the result:\n{result}"


def test_s1_the_summary_file_is_printed_when_there(wait):
    base = wait.base()
    wait.write(base, ".log", "a line\n")
    wait.write(base, ".summary", "SUMMARY-TOKEN-9d2: three tickets merged\n")
    wait.write(base, ".exit", "0\n")
    result = wait.run(base + ".exit", 5)
    assert result.code == 0 and "SUMMARY-TOKEN-9d2" in result.out, result


def test_s1_the_tail_is_the_last_30_lines_of_the_log_by_default(wait):
    base = wait.base()
    wait.write(base, ".log", "".join(f"row-{i:04d}\n" for i in range(1, 41)))
    wait.write(base, ".exit", "0\n")
    result = wait.run(base + ".exit", 5)
    assert "row-0040" in result.out and "row-0011" in result.out, result
    assert "row-0010" not in result.out and "row-0001" not in result.out, result


def test_s1_gov_wait_lines_sets_the_tail_length(wait):
    base = wait.base()
    wait.write(base, ".log", "".join(f"row-{i:04d}\n" for i in range(1, 41)))
    wait.write(base, ".exit", "0\n")
    result = wait.run(base + ".exit", 5, lines=5)
    assert "row-0040" in result.out and "row-0036" in result.out, result
    assert "row-0035" not in result.out, result


@pytest.mark.parametrize("suffix", [".log", ".json", ".txt"])
def test_s1_the_log_is_the_first_of_log_json_txt_that_exists(wait, suffix):
    base = wait.base()
    order = [".log", ".json", ".txt"]
    for each in order[order.index(suffix):]:
        wait.write(base, each, f"TOKEN-{each[1:]}-line\n")
    wait.write(base, ".exit", "0\n")
    result = wait.run(base + ".exit", 5)
    assert f"TOKEN-{suffix[1:]}-line" in result.out, result
    for later in order[order.index(suffix) + 1:]:
        assert f"TOKEN-{later[1:]}-line" not in result.out, f"only the first log that exists is the tail:\n{result}"


def test_s1_gov_wait_log_names_the_tail_file_instead(wait, tmp_path):
    base = wait.base()
    wait.write(base, ".log", "BESIDE-LOG-TOKEN\n")
    chosen = tmp_path / "elsewhere.txt"
    chosen.write_text("CHOSEN-LOG-TOKEN\n", encoding="utf-8")
    wait.write(base, ".exit", "0\n")
    result = wait.run(base + ".exit", 5, log=str(chosen))
    assert "CHOSEN-LOG-TOKEN" in result.out and "BESIDE-LOG-TOKEN" not in result.out, result


def test_s1_a_job_with_no_log_still_returns_its_code(wait):
    base = wait.base()
    wait.write(base, ".exit", "7\n")
    result = wait.run(base + ".exit", 5)
    assert result.code == 7 and "DONE exit 7" in result.out, result
