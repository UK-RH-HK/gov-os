#!/usr/bin/env python3
"""Model-neutral API worker adapter (non-product orchestration tooling, repair iteration 2 experiment).

One substrate for every provider: DeepSeek (OpenAI-compatible wire) and Anthropic (messages wire) receive the
same governed bootstrap, task contract, tool surface, mutation restrictions, checkpoint and context-renewal
protocol and telemetry schema. A provider entry says only how to speak to the wire, never what the worker must do.

Runs one bounded repair/analysis task on a provider model inside one git worktree, with a small
whitelisted tool surface, bounded context, summarised command output and per-run telemetry.

  api_worker.py --packet PACKET.json [--model deepseek-v4-pro] [--max-steps 60] [--context-budget 150000]

The packet (JSON) carries: run_id, role, worktree, model, allow_write (globs), deny_write (globs),
brief (markdown), checks (named whitelisted commands the worker may run), context_budget_tokens.

Key handling: the API key is read from ~/.config/governance-os/deepseek.env (mode 0600) at call time,
held only in memory, never printed, logged, persisted, hashed or placed in any packet, transcript or
telemetry record. Nothing this tool writes contains it.

Not product code. Nothing here is evidence: the worker produces claims, which an independent role grades.
"""
import argparse, fnmatch, json, os, re, subprocess, sys, time, urllib.error, urllib.request

# ---------------------------------------------------------------------------
# Providers. One canon, one bootstrap, one task contract, one checkpoint protocol:
# a provider entry only says how to speak to the wire, never what the worker must do.
# ---------------------------------------------------------------------------
PROVIDERS = {
    "deepseek": {
        "url": "https://api.deepseek.com/chat/completions",
        "key_file": os.path.expanduser("~/.config/governance-os/deepseek.env"),
        "key_var": "DEEPSEEK_API_KEY",
        "wire": "openai",
        "models": ("deepseek-v4-pro", "deepseek-flash"),
    },
    "anthropic": {
        "url": "https://api.anthropic.com/v1/messages",
        "key_file": os.path.expanduser("~/.config/governance-os/anthropic.env"),
        "key_var": "ANTHROPIC_API_KEY",
        "wire": "anthropic",
        "models": ("claude-sonnet-5",),
        "version": "2023-06-01",
    },
}


def provider_for(model):
    for name, p in PROVIDERS.items():
        if model in p["models"] or model.startswith(name):
            return name, p
    if model.startswith("claude"):
        return "anthropic", PROVIDERS["anthropic"]
    return "deepseek", PROVIDERS["deepseek"]
MAX_TOOL_CHARS = 6000          # per tool result injected into context
MAX_READ_LINES = 400


def api_key(prov):
    """Read the provider key at call time. Never printed, logged, persisted or placed in any record."""
    path, var = prov["key_file"], prov["key_var"]
    if not os.path.isfile(path):
        sys.exit(f"provider key file missing: {path} (expected {var}=...). "
                 "Credentials are owner-supplied; this tool never invents or derives one.")
    for line in open(path):
        if line.startswith(var + "="):
            return line.split("=", 1)[1].strip()
    sys.exit(f"{var} not found in {path}")


def clip(text, limit=MAX_TOOL_CHARS):
    text = text if isinstance(text, str) else str(text)
    if len(text) <= limit:
        return text
    head, tail = text[: limit // 2], text[-limit // 4 :]
    return f"{head}\n...[{len(text) - len(head) - len(tail)} chars omitted]...\n{tail}"


def summarise_cargo(out):
    """Return counts and failures only - never the whole log."""
    results = re.findall(r"test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored", out)
    fails = re.findall(r"(?m)^(?:failures:|\s{4})(\S+)$", out)
    errs = [l for l in out.splitlines() if l.startswith("error") or "panicked at" in l][:15]
    warn = len([l for l in out.splitlines() if l.startswith("warning")])
    parts = []
    for status, p, f, i in results:
        parts.append(f"test result: {status}. {p} passed; {f} failed; {i} ignored")
    if errs:
        parts.append("errors:\n" + "\n".join(errs))
    failed_names = [f for f in fails if "::" in f][:25]
    if failed_names:
        parts.append("failing tests: " + ", ".join(sorted(set(failed_names))))
    parts.append(f"warnings: {warn}")
    return "\n".join(parts) if parts else clip(out, 2000)


class Worker:
    def __init__(self, packet, model, max_steps, budget, telemetry_path):
        self.p = packet
        self.root = os.path.abspath(packet["worktree"])
        self.model = model
        self.provider, self.prov = provider_for(model)
        self.wire, self.url = self.prov["wire"], self.prov["url"]
        self.max_steps = max_steps
        self.budget = budget
        self.telemetry_path = telemetry_path
        self.messages = []
        self.tool_calls = 0
        self.writes = []
        self.checks_run = []
        self.peak_prompt = 0
        self.compactions = 0
        self.nudges = 0
        self.calls_at_last_write = 0
        self.renewals = 0
        self.drift_events = []
        self.first_useful_call = None
        self.checkpoints = []
        self.seen_calls = {}
        self.scratch = os.path.join(packet.get("scratch_dir") or "/tmp", "ds-scratch", packet["run_id"])
        os.makedirs(self.scratch, exist_ok=True)
        self.checkpoint_path = packet.get("checkpoint_path") or os.path.join(self.scratch, "checkpoint.json")
        self.usage = {"prompt": 0, "cached": 0, "completion": 0, "reasoning": 0}
        self.started = time.time()
        self.result = None

    # ---------- guarded filesystem ----------
    def _abs(self, path):
        full = os.path.abspath(os.path.join(self.root, path))
        if not full.startswith(self.root + os.sep) and full != self.root:
            raise PermissionError(f"path escapes the worktree: {path}")
        return full

    def _writable(self, rel):
        rel = rel.replace(os.sep, "/")
        for pat in self.p.get("deny_write", []):
            if fnmatch.fnmatch(rel, pat):
                return False, f"denied by deny_write pattern {pat}"
        for pat in self.p.get("allow_write", []):
            if fnmatch.fnmatch(rel, pat):
                return True, ""
        return False, "path is not in this task's allow_write list"

    def t_read_file(self, path, start_line=1, max_lines=MAX_READ_LINES):
        full = self._abs(path)
        with open(full, errors="replace") as fh:
            lines = fh.readlines()
        start = max(1, int(start_line))
        chunk = lines[start - 1 : start - 1 + min(int(max_lines), MAX_READ_LINES)]
        body = "".join(f"{i}\t{l}" for i, l in enumerate(chunk, start))
        return clip(f"{path} ({len(lines)} lines total, showing from {start})\n{body}")

    def t_list_dir(self, path="."):
        full = self._abs(path)
        entries = sorted(os.listdir(full))
        return clip("\n".join(("%s/" % e if os.path.isdir(os.path.join(full, e)) else e) for e in entries))

    def t_grep(self, pattern, path=".", max_results=60):
        cmd = ["grep", "-rn", "--binary-files=without-match", "-I", "-E", pattern, self._abs(path)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        lines = [l.replace(self.root + "/", "") for l in r.stdout.splitlines()][: int(max_results)]
        return clip("\n".join(lines) or "(no match)")

    def t_edit_file(self, path, old, new):
        ok, why = self._writable(path)
        if not ok:
            return f"REFUSED: {why}"
        full = self._abs(path)
        with open(full, errors="surrogateescape") as fh:
            body = fh.read()
        if body.count(old) != 1:
            return f"REFUSED: old text occurs {body.count(old)} times; it must occur exactly once"
        with open(full, "w", errors="surrogateescape") as fh:
            fh.write(body.replace(old, new))
        self.writes.append(path)
        return f"edited {path}"

    def t_write_file(self, path, content):
        ok, why = self._writable(path)
        if not ok:
            return f"REFUSED: {why}"
        full = self._abs(path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as fh:
            fh.write(content)
        self.writes.append(path)
        return f"wrote {path} ({len(content)} bytes)"

    def externalise(self, label, body):
        """Write a large result to scratch and return a summary plus its path."""
        path = os.path.join(self.scratch, f"{label}-{len(os.listdir(self.scratch)):03d}.txt")
        with open(path, "w") as fh:
            fh.write(body)
        return (f"[externalised: {len(body)} chars written to {path}; read what you need with "
                f"read_scratch(path=...)]\n" + clip(body, 2500))

    def t_read_scratch(self, path, start_line=1, max_lines=200):
        if not os.path.abspath(path).startswith(self.scratch):
            return "REFUSED: read_scratch only reads this run's scratch directory"
        with open(path, errors="replace") as fh:
            lines = fh.readlines()
        start = max(1, int(start_line))
        return clip("".join(lines[start - 1 : start - 1 + min(int(max_lines), 400)]))

    def t_checkpoint(self, objective, completed=None, files_changed=None, checks=None, discoveries=None,
                     unresolved=None, decisions=None, next_action=""):
        cp = {"run_id": self.p["run_id"], "at_tool_call": self.tool_calls, "objective": objective,
              "completed": completed or [], "files_changed": files_changed or sorted(set(self.writes)),
              "checks": checks or self.checks_run, "discoveries": discoveries or [],
              "unresolved": unresolved or [], "decisions": decisions or [], "next_action": next_action,
              "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        self.checkpoints.append(cp)
        with open(self.checkpoint_path, "w") as fh:
            json.dump(cp, fh, indent=1)
        return f"checkpoint recorded (next action: {next_action[:120]})"

    def auto_checkpoint(self, why):
        self.t_checkpoint(objective=self.p["title"],
                          completed=[f"{len(set(self.writes))} file(s) written", f"{len(self.checks_run)} check(s) run"],
                          discoveries=[f"auto-checkpoint: {why}"],
                          next_action="continue the task contract from the files already changed")

    def t_run_check(self, name):
        """Run one whitelisted command from the packet and return a summary, never a raw log."""
        checks = self.p.get("checks", {})
        if name not in checks:
            return f"REFUSED: unknown check {name!r}; available: {sorted(checks)}"
        cmd = checks[name]
        env = dict(os.environ, CARGO_BUILD_JOBS="2", PATH=os.path.expanduser("~/.cargo/bin") + ":" + os.environ["PATH"])
        t0 = time.time()
        # bash + pipefail: a failing cargo run must surface as a non-zero exit even through a pipe
        r = subprocess.run("set -o pipefail; " + cmd, shell=True, executable="/bin/bash",
                           cwd=self.root, capture_output=True, text=True, env=env, timeout=7200)
        dt = round(time.time() - t0, 1)
        out = (r.stdout or "") + "\n" + (r.stderr or "")
        self.checks_run.append({"name": name, "exit": r.returncode, "seconds": dt})
        body = summarise_cargo(out) if ("cargo" in cmd or "test" in cmd) else out
        verdict = "PASS" if r.returncode == 0 else "FAIL"
        head = f"[{name}] {verdict} (exit={r.returncode}) in {dt}s\n"
        return head + (self.externalise(name, body) if len(body) > MAX_TOOL_CHARS else body)

    def t_finish(self, verdict, summary, items=None, remaining=None):
        self.result = {"verdict": verdict, "summary": summary, "items": items or [], "remaining": remaining or []}
        return "recorded"

    TOOLS = [
        ("read_file", "Read a file (bounded).", {"path": "string", "start_line": "integer", "max_lines": "integer"}, ["path"]),
        ("list_dir", "List a directory.", {"path": "string"}, []),
        ("grep", "Search with an extended regex under a path.", {"pattern": "string", "path": "string", "max_results": "integer"}, ["pattern"]),
        ("edit_file", "Replace text that occurs exactly once in a writable file.", {"path": "string", "old": "string", "new": "string"}, ["path", "old", "new"]),
        ("write_file", "Write a writable file in full.", {"path": "string", "content": "string"}, ["path", "content"]),
        ("run_check", "Run one named whitelisted check and get a summary.", {"name": "string"}, ["name"]),
        ("checkpoint", "Record progress so a replacement worker could continue from it alone. Call this after each material step.",
         {"objective": "string", "completed": "array", "files_changed": "array", "checks": "array",
          "discoveries": "array", "unresolved": "array", "decisions": "array", "next_action": "string"},
         ["objective", "next_action"]),
        ("read_scratch", "Read part of an externalised result.", {"path": "string", "start_line": "integer", "max_lines": "integer"}, ["path"]),
        ("finish", "End the task with a structured result.", {"verdict": "string", "summary": "string", "items": "array", "remaining": "array"}, ["verdict", "summary"]),
    ]

    def tool_schema(self):
        out = []
        for name, desc, props, req in self.TOOLS:
            p = {k: ({"type": "array", "items": {"type": "string"}} if v == "array" else {"type": v}) for k, v in props.items()}
            out.append({"type": "function", "function": {"name": name, "description": desc,
                                                         "parameters": {"type": "object", "properties": p, "required": req}}})
        return out

    # ---------- provider wire ----------
    def anthropic_body(self):
        """Translate the canonical message list into Anthropic's blocks. No instruction differs by provider."""
        system = self.messages[0]["content"]
        msgs, pending_tool_results = [], []
        for m in self.messages[1:]:
            if m["role"] == "tool":
                pending_tool_results.append({"type": "tool_result", "tool_use_id": m["tool_call_id"],
                                             "content": m["content"]})
                continue
            if pending_tool_results:
                msgs.append({"role": "user", "content": pending_tool_results})
                pending_tool_results = []
            if m["role"] == "assistant":
                blocks = []
                if m.get("content"):
                    blocks.append({"type": "text", "text": m["content"]})
                for c in (m.get("tool_calls") or []):
                    blocks.append({"type": "tool_use", "id": c["id"], "name": c["function"]["name"],
                                   "input": json.loads(c["function"]["arguments"] or "{}")})
                msgs.append({"role": "assistant", "content": blocks or [{"type": "text", "text": "..."}]})
            else:
                msgs.append({"role": "user", "content": m["content"]})
        if pending_tool_results:
            msgs.append({"role": "user", "content": pending_tool_results})
        tools = [{"name": f["function"]["name"], "description": f["function"]["description"],
                  "input_schema": f["function"]["parameters"]} for f in self.tool_schema()]
        return {"model": self.model, "system": system, "messages": msgs, "tools": tools,
                "max_tokens": 16000, "temperature": 0.2}

    def anthropic_to_canonical(self, d):
        """Present an Anthropic reply in the canonical shape the run loop already handles."""
        text, calls = [], []
        for b in d.get("content", []):
            if b["type"] == "text":
                text.append(b["text"])
            elif b["type"] == "tool_use":
                calls.append({"id": b["id"], "type": "function",
                              "function": {"name": b["name"], "arguments": json.dumps(b["input"])}})
        u = d.get("usage", {}) or {}
        return {"choices": [{"message": {"role": "assistant", "content": "\n".join(text) or None,
                                         "tool_calls": calls or None},
                             "finish_reason": d.get("stop_reason")}],
                "usage": {"prompt_tokens": u.get("input_tokens", 0),
                          "completion_tokens": u.get("output_tokens", 0),
                          "prompt_cache_hit_tokens": u.get("cache_read_input_tokens", 0),
                          "completion_tokens_details": {"reasoning_tokens": 0}}}

    def call(self, key):
        if self.wire == "anthropic":
            body = self.anthropic_body()
            headers = {"x-api-key": key, "anthropic-version": self.prov.get("version", "2023-06-01"),
                       "Content-Type": "application/json"}
        else:
            body = {"model": self.model, "messages": self.messages, "tools": self.tool_schema(),
                    "tool_choice": "auto", "max_tokens": 16000, "temperature": 0.2}
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        req = urllib.request.Request(self.url, data=json.dumps(body).encode(), headers=headers)
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=900) as r:
                    d = json.load(r)
                return self.anthropic_to_canonical(d) if self.wire == "anthropic" else d
            except urllib.error.HTTPError as e:
                detail = e.read().decode(errors="replace")[:300]
                if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                    time.sleep(6 * (attempt + 1)); continue
                raise RuntimeError(f"provider HTTP {e.code}: {detail}")
            except Exception:
                if attempt < 3:
                    time.sleep(6 * (attempt + 1)); continue
                raise

    def progress_note(self):
        return ("[progress so far] files written: " + (", ".join(sorted(set(self.writes))) or "none")
                + "; checks run: " + (", ".join(f"{c['name']}=exit{c['exit']}" for c in self.checks_run) or "none")
                + f"; tool calls: {self.tool_calls}. Re-read a file if you need its current content.")

    def renew(self, why):
        """Rebuild a fresh bounded context from the bootstrap and the latest checkpoint."""
        self.auto_checkpoint(why)
        cp = self.checkpoints[-1]
        self.messages = [
            self.messages[0],
            {"role": "user", "content": self.p["brief"]},
            {"role": "user", "content":
                "[context renewed: your earlier exploration history was discarded to keep you working in a clean "
                f"window. Reason: {why}.]\n\nYour checkpoint:\n" + json.dumps(cp, indent=1) +
                "\n\nContinue from `next_action`. Re-read any file you need; do not re-derive what the checkpoint "
                "already records."},
        ]
        self.renewals += 1
        self.drift_events.append({"at_tool_call": self.tool_calls, "event": "context_renewal", "why": why})

    def run(self):
        key = api_key(self.prov)
        self.messages = [
            {"role": "system", "content": self.p["system"]},
            {"role": "user", "content": self.p["brief"]},
        ]
        resume = self.p.get("resume_from")
        if resume and os.path.isfile(resume):
            self.messages.append({"role": "user", "content":
                "[resuming a previous worker on this task; its context is gone, this checkpoint is what survives]\n"
                + json.dumps(json.load(open(resume)), indent=1)
                + "\n\nVerify the state on disk matches it (the files it lists are already changed in your worktree), "
                  "then continue from `next_action`."})
        for step in range(self.max_steps):
            if self.peak_prompt > self.budget:
                self.renew(f"context reached {self.peak_prompt} tokens against a {self.budget} guidance budget")
                self.peak_prompt = 0
            d = self.call(key)
            u = d.get("usage", {}) or {}
            self.usage["prompt"] += u.get("prompt_tokens", 0)
            self.usage["cached"] += u.get("prompt_cache_hit_tokens", 0)
            self.usage["completion"] += u.get("completion_tokens", 0)
            self.usage["reasoning"] += (u.get("completion_tokens_details") or {}).get("reasoning_tokens", 0)
            self.peak_prompt = max(self.peak_prompt, u.get("prompt_tokens", 0))
            msg = d["choices"][0]["message"]
            self.messages.append({k: v for k, v in msg.items() if k in ("role", "content", "tool_calls")})
            calls = msg.get("tool_calls") or []
            if not calls:
                if self.result:
                    break
                self.messages.append({"role": "user", "content": "Continue, or call finish when the task is complete."})
                continue
            for c in calls:
                self.tool_calls += 1
                fn = c["function"]["name"]
                sig = fn + "|" + (c["function"].get("arguments") or "")[:200]
                self.seen_calls[sig] = self.seen_calls.get(sig, 0) + 1
                if self.seen_calls[sig] == 3:
                    self.drift_events.append({"at_tool_call": self.tool_calls, "event": "repeated_identical_call", "call": fn})
                try:
                    args = json.loads(c["function"]["arguments"] or "{}")
                    out = getattr(self, "t_" + fn)(**args)
                except Exception as e:
                    out = f"ERROR {type(e).__name__}: {str(e)[:400]}"
                if fn in ("edit_file", "write_file") and not out.startswith(("REFUSED", "ERROR")):
                    self.calls_at_last_write = self.tool_calls
                    if self.first_useful_call is None:
                        self.first_useful_call = self.tool_calls
                self.messages.append({"role": "tool", "tool_call_id": c["id"], "content": clip(out)})
            if self.result:
                break
            if not self.writes and self.tool_calls >= 20 and self.nudges < 3 and self.tool_calls % 20 == 0:
                self.drift_events.append({"at_tool_call": self.tool_calls, "event": "reads_without_mutation"})
                self.nudges += 1
                if self.nudges >= 2:
                    self.renew("exploration without mutation")
                self.messages.append({"role": "user", "content":
                    f"You have made {self.tool_calls} tool calls and written nothing yet. You have read enough to act: "
                    "make the smallest edit that moves the requirement forward now (edit_file or write_file), then run a "
                    "check. If the task cannot be done within your allow_write list, call finish and say exactly why."})
            elif self.writes and not self.checks_run and self.tool_calls - self.calls_at_last_write > 15:
                self.calls_at_last_write = self.tool_calls
                self.drift_events.append({"at_tool_call": self.tool_calls, "event": "edits_without_check"})
                self.messages.append({"role": "user", "content":
                    "You have changed files but run no check. Run the relevant check now so you know whether the tree "
                    "still builds and your change does what you intend, then checkpoint."})
            elif self.writes and self.tool_calls - self.calls_at_last_write > 30:
                self.calls_at_last_write = self.tool_calls
                self.nudges += 1
                self.messages.append({"role": "user", "content":
                    "Checkpoint: state in one line what is done and what remains, then continue with the next edit or "
                    "check. Do not re-read files you have already read."})
            if step == self.max_steps - 5:
                self.messages.append({"role": "user", "content":
                    "Your step budget is nearly exhausted. Land what you have: run the relevant check, then call finish "
                    "with an honest verdict (PARTIAL is fine) naming what remains."})
        if not self.result:
            self.auto_checkpoint("run ended without finish")
        self.telemetry()
        return self.result

    def telemetry(self):
        rec = {
            "run_id": self.p["run_id"], "role": self.p.get("role"), "provider": self.provider, "model": self.model,
            "reasoning_level": "provider default (reasoning_tokens reported)",
            "tokens": {"prompt_total": self.usage["prompt"], "cached_prompt": self.usage["cached"],
                       "completion_total": self.usage["completion"], "reasoning": self.usage["reasoning"],
                       "context_peak_prompt_tokens": self.peak_prompt,
                       "context_budget_tokens": self.budget},
            "bootstrap_chars": len(self.p["brief"]), "bootstrap_tokens_estimate": len(self.p["brief"]) // 4,
            "tool_calls": self.tool_calls, "tool_calls_before_first_write": self.first_useful_call,
            "context_renewals": self.renewals, "nudges": self.nudges, "drift_events": self.drift_events,
            "checkpoints": len(self.checkpoints), "checkpoint_path": self.checkpoint_path,
            "routing_note": self.p.get("routing_note"), "checks": self.checks_run, "files_written": sorted(set(self.writes)),
            "runtime_seconds": round(time.time() - self.started, 1),
            "result": (self.result or {"verdict": "INCOMPLETE", "summary": "max steps reached"}),
            "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        os.makedirs(os.path.dirname(self.telemetry_path), exist_ok=True)
        with open(self.telemetry_path, "a") as fh:
            fh.write(json.dumps(rec) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", required=True)
    ap.add_argument("--model")
    ap.add_argument("--max-steps", type=int, default=80)
    ap.add_argument("--context-budget", type=int)
    ap.add_argument("--telemetry", default="release/orchestration/phase-2/telemetry/P2-R2-MODEL-TELEMETRY.jsonl")
    a = ap.parse_args()
    packet = json.load(open(a.packet))
    model = a.model or packet.get("model", "deepseek-v4-pro")
    budget = a.context_budget or packet.get("context_budget_tokens", 150000)
    w = Worker(packet, model, a.max_steps, budget, a.telemetry)
    res = w.run()
    print(json.dumps({"run_id": packet["run_id"], "model": model, "result": res,
                      "tool_calls": w.tool_calls, "context_peak": w.peak_prompt,
                      "files_written": sorted(set(w.writes)), "checks": w.checks_run}, indent=1))


if __name__ == "__main__":
    main()
