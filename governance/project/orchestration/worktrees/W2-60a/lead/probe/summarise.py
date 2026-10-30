"""Summarise probe stream-json logs: session id, model, per-message usage, tool calls and results, result."""
import json
import sys


def main(paths):
    for path in paths:
        print("=====", path)
        for line in open(path, encoding="utf-8"):
            if not line.startswith("{"):
                print("  raw:", line.strip()[:300])
                continue
            event = json.loads(line)
            kind = event.get("type")
            if kind == "system" and event.get("subtype") == "init":
                print("  init session", event.get("session_id"), "model", event.get("model"),
                      "permissionMode", event.get("permissionMode"))
            elif kind == "assistant":
                message = event["message"]
                usage = message.get("usage", {})
                for part in message.get("content", []):
                    if part.get("type") == "tool_use":
                        print("  tool_use", part.get("name"), json.dumps(part.get("input"))[:300])
                    elif part.get("type") == "text":
                        print("  text", repr(part.get("text"))[:400])
                print("    usage in", usage.get("input_tokens"), "cache_create", usage.get("cache_creation_input_tokens"),
                      "cache_read", usage.get("cache_read_input_tokens"), "out", usage.get("output_tokens"))
            elif kind == "user":
                for part in event["message"].get("content", []):
                    if isinstance(part, dict) and part.get("type") == "tool_result":
                        content = part.get("content")
                        text = content if isinstance(content, str) else json.dumps(content)
                        print("  tool_result error=%s" % part.get("is_error"), repr(text)[:500])
            elif kind == "result":
                usage = event.get("usage", {})
                print("  RESULT", repr(event.get("result")), "cost", event.get("total_cost_usd"),
                      "turns", event.get("num_turns"), "duration_ms", event.get("duration_ms"))
                print("    total in", usage.get("input_tokens"), "cache_create", usage.get("cache_creation_input_tokens"),
                      "cache_read", usage.get("cache_read_input_tokens"), "out", usage.get("output_tokens"))
                print("    permission_denials", json.dumps(event.get("permission_denials"))[:600])


if __name__ == "__main__":
    main(sys.argv[1:])
