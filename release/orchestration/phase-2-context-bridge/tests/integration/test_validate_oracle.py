"""``govbridge.demo.validate_oracle`` (TA OI-3, closed by I1/BR-AR-0009): a thin subprocess wrapper over
``DEMONSTRATION/oracle-tools/check_oracle.py``, never a re-implementation. Tested only against a deliberately
INVALID, minimal synthetic oracle -- I1 never sees the real, held-out oracle (this run's own scope); proving
check_oracle.py's OWN acceptance logic is TA's job (DEMONSTRATION/oracle-tools/selftest_check_oracle.py), already
done. This test proves the WIRING: the subprocess call, exit code and output are surfaced correctly, and the
wrapper never echoes oracle content of its own."""
import yaml

from govbridge.demo import validate_oracle as vomod


def test_a_structurally_broken_oracle_is_reported_invalid(tmp_path):
    oracle_path = tmp_path / "oracle.yaml"
    oracle_path.write_text(yaml.safe_dump({"schema": "not-the-right-schema"}), encoding="utf-8")

    result = vomod.validate_oracle(str(oracle_path))
    assert result["valid"] is False
    assert result["exit_code"] == 1
    assert "RESULT: INVALID" in result["stdout"]
    # the wrapper's own output never echoes oracle CONTENT -- only the file's name/sha256/counts/problem
    # locations (check_oracle.py's own discipline); "not-the-right-schema" is a problem statement about the
    # schema field, not the oracle's substantive content, so this is a smoke check that nothing else leaks.
    assert oracle_path.read_text(encoding="utf-8") not in result["stdout"]


def test_command_is_the_real_check_oracle_script_via_subprocess(tmp_path):
    oracle_path = tmp_path / "oracle.yaml"
    oracle_path.write_text(yaml.safe_dump({"schema": "govbridge-oracle/1"}), encoding="utf-8")
    result = vomod.validate_oracle(str(oracle_path))
    assert result["command"][1].endswith("DEMONSTRATION/oracle-tools/check_oracle.py")
    assert result["command"][2] == str(oracle_path)


def test_main_json_mode_reports_exit_code(tmp_path, capsys):
    oracle_path = tmp_path / "oracle.yaml"
    oracle_path.write_text(yaml.safe_dump({"schema": "not-the-right-schema"}), encoding="utf-8")
    rc = vomod.main([str(oracle_path), "--json"])
    assert rc == 1
    out = capsys.readouterr().out
    assert '"valid": false' in out
