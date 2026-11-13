"""Planted-transcript test of adoption_count.py. Run: python3 -I test_adoption_count.py"""
import json, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
def bash(cmd): return {"type": "tool_use", "name": "Bash", "input": {"command": cmd}}
def text(t): return {"type": "text", "text": t}
def write(path, prompt, blocks, ts="2026-11-10T10:00:00Z"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    recs = [{"type": "user", "timestamp": ts, "message": {"content": prompt}}]
    recs += [{"type": "assistant", "timestamp": ts, "message": {"content": [b]}} for b in blocks]
    with open(path, "w") as fh: fh.write("\n".join(json.dumps(r) for r in recs) + "\n")
def main():
    with tempfile.TemporaryDirectory(prefix="adoption-test-", dir=os.environ.get("TMPDIR")) as root:
        wt = os.path.join(root, "-home-usain-gov-os-worktrees-W2-1")
        # A: two different searches, then "not found" -> again, twice-first
        write(f"{wt}/a.jsonl", "You are a fresh engineer", [bash('gov retrieve "where is the guard"'),
              bash("cd x && GOV_ROLE=engineer gov retrieve --radius 1 'guard policy loader'"), text("Not found: the loader.")])
        # B: one search then a continuation (same search), then "may be incomplete" -> not again, not twice-first
        write(f"{wt}/b.jsonl", "You are the ticket lead for ticket W2-1", [bash('gov retrieve "x y"'),
              bash("gov retrieve --continue tok1 'x y'"), text("This may be incomplete.")])
        # C: grep mentioning gov retrieve is not a run; phrase without a retrieve is not counted
        write(f"{wt}/c.jsonl", "You are a fresh reviewer", [bash("grep -n 'gov retrieve' f.md"), text("not found")])
        # D: same words twice -> not again; old session outside the window is not scanned
        write(f"{wt}/d.jsonl", "You are a fresh independent test designer", [bash('gov retrieve "a b"'), bash("gov retrieve 'b a'")])
        write(f"{wt}/old.jsonl", "You are a fresh engineer", [bash('gov retrieve "q"')], ts="2026-11-01T00:00:00Z")
        # E: a subagent: one search, a second after the phrase -> again, not twice-first
        write(f"{wt}/s1/subagents/agent-1.jsonl", "Run gov retrieve", [bash("python3 -m gov.cli.main retrieve 'one'"),
              text("not found"), bash("timeout 60 /v/bin/gov retrieve 'two'")])
        write(os.path.join(root, "-home-usain-elsewhere", "z.jsonl"), "x", [bash('gov retrieve "q"')])
        out = subprocess.run([sys.executable, "-I", os.path.join(HERE, "adoption_count.py"), "--root", root],
                             capture_output=True, text=True, check=True).stdout
        r = json.loads(out)
        assert r["scanned"] == 5, r["scanned"]
        assert r["scanned_by_kind"] == {"top": 4, "sub": 1}, r
        assert r["count1_searched_again"] == "2/4", r["count1_searched_again"]
        assert r["count2_twice_before_phrase"] == "1/3", r["count2_twice_before_phrase"]
        assert r["threshold_hook_package"] is True
        assert r["per_role"]["engineer"] == 1 and r["per_role"]["lead"] == 1 and r["per_role"]["test-designer"] == 1
        assert r["per_day"] == {"2026-11-10": 5}
        assert "Not found" not in out and "loader" not in out  # no transcript content leaks
    print("ok")
if __name__ == "__main__": main()
