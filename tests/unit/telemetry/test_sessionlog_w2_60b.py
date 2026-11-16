"""W2-60b: the new readings of a session log (``sessionlog.measure``): turns, compactions, rate-limit events, cost,
effort, minutes, the main session's models and each sub-agent's model. Counts only, never content (DEC-495); a form
no specimen or brief shows is "not measured" (DEC-655). W1-31's ``read`` is not changed by them."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gov.cli.errors import GovError
from gov.telemetry import sessionlog

SESSION = "11111111-1111-4111-8111-111111111111"
SECRET = "MARK-OKAPI the one sentence no record may hold"


def _usage(n=10):
    return {"input_tokens": n, "output_tokens": 2, "cache_creation_input_tokens": 3, "cache_read_input_tokens": 4}


class Log:
    def __init__(self, session=SESSION, version="2.1.320"):
        self.session, self.version, self.lines, self.n = session, version, [], 0

    def full(self, kind, sidechain=False, **fields):
        self.n += 1
        line = {"type": kind, "isSidechain": sidechain, "uuid": f"u{self.n}",
                "timestamp": f"2026-11-16T10:{self.n:02d}:00.000Z", "sessionId": self.session,
                "version": self.version, **fields}
        self.lines.append(line)
        return self

    def user(self, text=SECRET, **kw):
        return self.full("user", message={"role": "user", "content": text}, **kw)

    def assistant(self, model="claude-opus-5-5", effort="high", mid=None, text=SECRET, **kw):
        mid = mid or f"msg_{self.n + 1}"
        return self.full("assistant", message={"model": model, "id": mid, "role": "assistant",
                                               "content": [{"type": "text", "text": text}], "usage": _usage()},
                         requestId=f"req_{mid}", perTurnEffort=effort, **kw)

    def compaction(self):
        return self.full("system", subtype="compact_boundary", content="Conversation compacted",
                         compactMetadata={"trigger": "auto", "preTokens": 900000})

    def api_error(self, status):
        return self.full("system", subtype="api_error", level="error", retryAttempt=1,
                         error={"message": SECRET, "status": status, "rateLimits": {"x": 1} if status == 429 else None})

    def rate_limit_message(self):
        return self.full("assistant", isApiErrorMessage=True, error="rate_limit",
                         message={"model": "<synthetic>", "id": f"msg_s{self.n}", "role": "assistant",
                                  "content": [{"type": "text", "text": SECRET}], "usage": _usage(0)})

    def cost(self, usd):
        self.lines.append({"type": "cost-state", "sessionId": self.session, "totalCostUSD": usd,
                           "totalAPIDuration": 1000})
        return self

    def write(self, config: Path, subagents=()) -> Path:
        path = config / "projects" / "-work-project" / f"{self.session}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(line) + "\n" for line in self.lines), encoding="utf-8")
        for index, sub in enumerate(subagents):
            folder = path.with_suffix("") / "subagents"
            folder.mkdir(parents=True, exist_ok=True)
            (folder / f"agent-a{index}.jsonl").write_text(
                "".join(json.dumps(line) + "\n" for line in sub.lines), encoding="utf-8")
            (folder / f"agent-a{index}.meta.json").write_text("{}", encoding="utf-8")
        return path


def _sub(model):
    sub = Log()
    sub.full("user", sidechain=True, message={"role": "user", "content": "task"})
    sub.full("assistant", sidechain=True, message={"model": model, "id": f"m-{model}", "role": "assistant",
                                                   "content": [{"type": "text", "text": "x"}], "usage": _usage()},
             requestId="r")
    return sub


def test_three_compactions_are_counted(tmp_path):
    log = Log().user().assistant().compaction().assistant().compaction().assistant().compaction().assistant()
    assert sessionlog.measure(log.write(tmp_path), SESSION)["compactions"] == 3


def test_a_log_without_compaction_counts_zero_compactions(tmp_path):
    assert sessionlog.measure(Log().user().assistant().write(tmp_path), SESSION)["compactions"] == 0


def test_turns_are_the_session_s_own_assistant_messages_each_once(tmp_path):
    log = Log().user().assistant(mid="m1").assistant(mid="m1").assistant(mid="m2").rate_limit_message()
    assert sessionlog.measure(log.write(tmp_path), SESSION)["turns"] == 2


def test_rate_limit_events_are_the_429_lines_and_the_rate_limit_messages_each_with_its_timestamp(tmp_path):
    log = Log().user().api_error(503).api_error(429).assistant().rate_limit_message()
    got = sessionlog.measure(log.write(tmp_path), SESSION)
    assert got["rate_limits"] == ["2026-11-16T10:03:00.000Z", "2026-11-16T10:05:00.000Z"]


def test_a_rate_limit_line_without_a_timestamp_makes_the_events_not_measured(tmp_path):
    log = Log().user().api_error(429)
    del log.lines[-1]["timestamp"]
    assert sessionlog.measure(log.write(tmp_path), SESSION)["rate_limits"] is None


def test_the_cost_is_the_last_cost_state_line_s_total(tmp_path):
    log = Log().user().assistant().cost(0.5).assistant().cost(1.25)
    assert sessionlog.measure(log.write(tmp_path), SESSION)["cost"] == 1.25


@pytest.mark.parametrize("usd", (None, "1.0", True, -1))
def test_no_cost_value_is_none_never_zero(tmp_path, usd):
    log = Log().user().assistant()
    if usd is not None:
        log.cost(usd)
    assert sessionlog.measure(log.write(tmp_path), SESSION)["cost"] is None


def test_effort_and_models_of_the_main_session_skip_the_synthetic_message(tmp_path):
    log = Log().user().assistant(effort="high").rate_limit_message().assistant(effort="high")
    got = sessionlog.measure(log.write(tmp_path), SESSION)
    assert got["efforts"] == ["high"] and got["models"] == ["claude-opus-5-5"]


def test_an_effort_of_no_known_value_is_left_out(tmp_path):
    got = sessionlog.measure(Log().user().assistant(effort=None).assistant(effort=SECRET).write(tmp_path), SESSION)
    assert got["efforts"] == []


def test_minutes_run_from_the_first_to_the_last_timestamp(tmp_path):
    log = Log().user().assistant().assistant().assistant()  # 10:01 .. 10:04
    assert sessionlog.measure(log.write(tmp_path), SESSION)["minutes"] == 3.0


def test_each_subagent_gives_one_model(tmp_path):
    path = Log().user().assistant().write(tmp_path, subagents=(_sub("claude-haiku-5-5"), _sub("claude-opus-5-5")))
    assert sessionlog.measure(path, SESSION)["subagents"] == ["claude-haiku-5-5", "claude-opus-5-5"]


def test_a_subagent_s_rate_limit_is_an_event_of_the_session(tmp_path):
    sub = _sub("claude-haiku-5-5")
    sub.full("system", sidechain=True, subtype="api_error", error={"status": 429})
    path = Log().user().assistant().write(tmp_path, subagents=(sub,))
    assert len(sessionlog.measure(path, SESSION)["rate_limits"]) == 1


def test_no_text_of_the_log_is_in_the_measures(tmp_path):
    log = Log().user().assistant().api_error(429).rate_limit_message().compaction()
    assert SECRET not in json.dumps(sessionlog.measure(log.write(tmp_path), SESSION))


def test_a_model_name_that_is_not_a_name_makes_the_models_not_measured(tmp_path):
    got = sessionlog.measure(Log().user().assistant(model=SECRET).write(tmp_path), SESSION)
    assert got["models"] is None and SECRET not in json.dumps(got)


def test_a_line_that_is_not_json_refuses(tmp_path):
    path = Log().user().write(tmp_path)
    path.write_text(path.read_text() + "not json\n", encoding="utf-8")
    with pytest.raises(GovError) as raised:
        sessionlog.measure(path, SESSION)
    assert "not json" not in raised.value.message


def test_a_line_of_another_session_refuses(tmp_path):
    log = Log().user()
    log.lines[-1]["sessionId"] = "22222222-2222-4222-8222-222222222222"
    with pytest.raises(GovError):
        sessionlog.measure(log.write(tmp_path), SESSION)


def test_w1_31_read_is_unchanged_for_a_429_line(tmp_path):
    """W1-31's rule stands: a system line of a kind no specimen shows makes the three sources not measured."""
    got = sessionlog.read(Log().user().api_error(429).write(tmp_path), SESSION)
    assert set(got["missing"]) == set(sessionlog.LOG_SOURCES)
