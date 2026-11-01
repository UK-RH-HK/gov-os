"""Probe (not a test): does today's rebuild accept an integration_store key in rebuild.yaml?"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests/acceptance/W2-122"))
import w2_122_support as S

work = Path(tempfile.mkdtemp(prefix="w2122-key-"))
box = S.make_box(work)
project = S.make_base(box, settings=S.settings_text(box.lock, "/nowhere/base"))
run = S.rebuild(project, S.environment(box, S.closed_loopback_host()), "--no-embeddings")
print("exit", run.returncode, "ok", run.envelope().get("ok"), run.envelope().get("error"))
print("work:", work)
