"""Probe (not a test): how many embed requests a cold rebuild of a 120-note tree sends to the stand-in."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests/acceptance/W2-122"))
import w2_122_support as S

work = Path(tempfile.mkdtemp(prefix="w2122-batch-"))
box = S.make_box(work)
end = S.OllamaStandIn()
try:
    env = S.environment(box, end.host)
    base = S.make_base(box)
    for number in range(120):
        S.write(base / f"docs/many/n{number:03d}.md", S.note(f"word{number:03d}x"))
    S.git(base, "add", "-A")
    S.git(base, "commit", "-q", "-m", "many")
    run = S.built(base, env)
    print("texts", len(end.embedded), "requests", end.embed_requests, "seconds", round(run.seconds, 1))
finally:
    end.close()
print("work:", work)
