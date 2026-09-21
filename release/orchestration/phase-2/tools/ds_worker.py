#!/usr/bin/env python3
"""DeepSeek worker adapter (non-product orchestration tooling, repair iteration 2 experiment).

Runs one bounded repair/analysis task on a provider model inside one git worktree, with a small
whitelisted tool surface, bounded context, summarised command output and per-run telemetry.

  ds_worker.py --packet PACKET.json [--model deepseek-v4-pro] [--max-steps 60] [--context-budget 150000]

The packet (JSON) carries: run_id, role, worktree, model, allow_write (globs), deny_write (globs),
brief (markdown), checks (named whitelisted commands the worker may run), context_budget_tokens.

Key handling: the API key is read from ~/.config/governance-os/deepseek.env (mode 0600) at call time,
held only in memory, never printed, logged, persisted, hashed or placed in any packet, transcript or
telemetry record. Nothing this tool writes contains it.

Not product code. Nothing here is evidence: the worker produces claims, which an independent role grades.
"""
import argparse, fnmatch, json, os, re, subprocess, sys, time, urllib.error, urllib.request

API = "https://api.deepseek.com/chat/completions"
KEY_FILE = os.path.expanduser("~/.config/governance-os/deepseek.env")
MAX_TOOL_CHARS = 6000          # per tool result injected into context
MAX_READ_LINES = 400


def api_key():
    with open(KEY_FILE) as fh:
        for line in fh:
            if line.startswith("DEEPSEEK_API_KEY="):
                return line.split("=", 1)[1].strip()
    sys.exit("provider key not found (expected DEEPSEEK_API_KEY in ~/.config/governance-os/deepseek.env)")


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
        self.max_steps = max_steps
        self.budget = budget
        self.telemetry_path = telemetry_path
        self.messages = []
        self.tool_calls = 0
        self.writes = []
        self.checks_run = []
        self.peak_prompt = 0
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

    def t_run_check(self, name):
        """Run one whitelisted command from the packet and return a summary, never a raw log."""
        checks = self.p.get("checks", {})
        if name not in checks:
            return f"REFUSED: unknown check {name!r}; available: {sorted(checks)}"
        cmd = checks[name]
        env = dict(os.environ, CARGO_BUILD_JOBS="2", PATH=os.path.expanduser("~/.cargo/bin") + ":" + os.environ["PATH"])
        t0 = time.time()
        r = subprocess.run(cmd, shell=True, cwd=self.root, capture_output=True, text=True, env=env, timeout=7200)
        dt = round(time.time() - t0, 1)
        out = (r.stdout or "") + "\n" + (r.stderr or "")
        self.checks_run.append({"name": name, "exit": r.returncode, "seconds": dt})
        body = summarise_cargo(out) if ("cargo" in cmd or "test" in cmd) else clip(out, 3000)
        return f"[{name}] exit={r.returncode} in {dt}s\n{body}"

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
        ("finish", "End the task with a structured result.", {"verdict": "string", "summary": "string", "items": "array", "remaining": "array"}, ["verdict", "summary"]),
    ]

    def tool_schema(self):
        out = []
        for name, desc, props, req in self.TOOLS:
            p = {k: ({"type": "array", "items": {"type": "string"}} if v == "array" else {"type": v}) for k, v in props.items()}
            out.append({"type": "function", "function": {"name": name, "description": desc,
                                                         "parameters": {"type": "object", "properties": p, "required": req}}})
        return out

    # ---------- provider ----------
    def call(self, key):
        body = {"model": self.model, "messages": self.messages, "tools": self.tool_schema(),
                "tool_choice": "auto", "max_tokens": 8000, "temperature": 0.2}
        req = urllib.request.Request(API, data=json.dumps(body).encode(),
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=900) as r:
                    return json.load(r)
            except urllib.error.HTTPError as e:
                detail = e.read().decode(errors="replace")[:300]
                if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                    time.sleep(6 * (attempt + 1)); continue
                raise RuntimeError(f"provider HTTP {e.code}: {detail}")
            except Exception:
                if attempt < 3:
                    time.sleep(6 * (attempt + 1)); continue
                raise

    def compact(self):
        """Keep the brief, the last exchanges, and a note; drop older tool payloads."""
        keep_head, keep_tail = 2, 12
        if len(self.messages) <= keep_head + keep_tail:
            return
        dropped = len(self.messages) - keep_head - keep_tail
        head, tail = self.messages[:keep_head], self.messages[-keep_tail:]
        while tail and tail[0].get("role") == "tool":
            tail = tail[1:]
        self.messages = head + [{"role": "user", "content": f"[context compacted: {dropped} earlier messages dropped. Re-read files if needed.]"}] + tail

    def run(self):
        key = api_key()
        self.messages = [
            {"role": "system", "content": self.p["system"]},
            {"role": "user", "content": self.p["brief"]},
        ]
        for step in range(self.max_steps):
            if self.peak_prompt > self.budget:
                self.compact()
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
                try:
                    args = json.loads(c["function"]["arguments"] or "{}")
                    out = getattr(self, "t_" + fn)(**args)
                except Exception as e:
                    out = f"ERROR {type(e).__name__}: {str(e)[:400]}"
                self.messages.append({"role": "tool", "tool_call_id": c["id"], "content": clip(out)})
            if self.result:
                break
        self.telemetry()
        return self.result

    def telemetry(self):
        rec = {
            "run_id": self.p["run_id"], "role": self.p.get("role"), "provider": "deepseek", "model": self.model,
            "reasoning_level": "provider default (reasoning_tokens reported)",
            "tokens": {"prompt_total": self.usage["prompt"], "cached_prompt": self.usage["cached"],
                       "completion_total": self.usage["completion"], "reasoning": self.usage["reasoning"],
                       "context_peak_prompt_tokens": self.peak_prompt,
                       "context_budget_tokens": self.budget},
            "tool_calls": self.tool_calls, "checks": self.checks_run, "files_written": sorted(set(self.writes)),
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
