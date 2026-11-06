"""Tests of the trial worker's YesLogitReranker (ACT-RERANK-TRIAL-2 §5.1), on the CPU with the GPU hidden:
the template with zerank-1-small's real tokenizer (the downloaded snapshot, offline), the score path with a tiny
random Qwen3 model against a full forward pass. No real weights are loaded.

    CUDA_VISIBLE_DEVICES=-1 HF_HUB_OFFLINE=1 <trial venv>/bin/python -I test_yes_logit.py
"""
import importlib.util
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SNAP = Path.home() / ".cache/gov-os-trial/hf/hub/models--zeroentropy--zerank-1-small-reranker/snapshots" \
    / "a65fd51c450e9b47fdddab98e31166ecad21af8d"
spec = importlib.util.spec_from_file_location("trial_worker", HERE / "rerank_worker.py")
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)

import torch  # noqa: E402
from transformers import AutoTokenizer, Qwen3Config, Qwen3ForCausalLM  # noqa: E402

assert not torch.cuda.is_available(), "run with CUDA_VISIBLE_DEVICES=-1: these tests never touch the GPU"
results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"{'ok  ' if ok else 'FAIL'} {name}{': ' + detail if detail and not ok else ''}")


tok = AutoTokenizer.from_pretrained(SNAP, trust_remote_code=False)
torch.manual_seed(0)
cfg = Qwen3Config(vocab_size=len(tok), hidden_size=32, intermediate_size=64, num_hidden_layers=2,
                  num_attention_heads=2, num_key_value_heads=1, head_dim=16, max_position_embeddings=4096,
                  tie_word_embeddings=True)
tiny = Qwen3ForCausalLM(cfg).to(torch.float32)
r = worker.YesLogitReranker("unused", "unused", "cpu", model_obj=tiny, tokenizer=AutoTokenizer.from_pretrained(SNAP))

# 1. The template: the query as the system message, the passage as the user message, the generation prompt, no think
want = "<|im_start|>system\nWhat decides a close?<|im_end|>\n<|im_start|>user\nThe close gate.<|im_end|>\n" \
       "<|im_start|>assistant\n"
got = r.prompts([("What decides a close?", "The close gate.")])[0]
check("1 the published template (system = query, user = passage, generation prompt)", got == want, repr(got))
check("1b no empty think block", "<think>" not in got)

# 2. The cuts: query 2,000 and passage 10,000 characters
p = r.prompts([("q" * 2500, "d" * 12000)])[0]
check("2 query cut at 2,000 characters", "q" * 2000 in p and "q" * 2001 not in p)
check("2b passage cut at 10,000 characters", "d" * 10000 in p and "d" * 10001 not in p)

# 3. The Yes token and right padding
check("3 the Yes token is id 9454, the single token 'Yes' (a literal, read from the snapshot once)",
      r.yes == 9454 and tok.convert_ids_to_tokens([9454]) == ["Yes"])
from transformers import AutoConfig  # noqa: E402
c = AutoConfig.from_pretrained(SNAP, trust_remote_code=False)
check("3c the snapshot's config loads as the library's own Qwen3 (its auto_map ignored, no remote code)",
      type(c).__name__ == "Qwen3Config" and c.architectures == ["Qwen3ForCausalLM"])
check("3b right padding", r.tokenizer.padding_side == "right")

# 4. The score path equals a full forward pass at each pair's last real position (right padding, mixed lengths)
pairs = [("short?", "a"), ("a longer question about the guard?", "the guard refuses writes outside a ticket's paths " * 3),
         ("third", "x y z")]
enc = r.tokenizer(r.prompts(pairs), padding=True, return_tensors="pt")
with torch.inference_mode():
    full = tiny(input_ids=enc["input_ids"], attention_mask=enc["attention_mask"]).logits
last = enc["attention_mask"].sum(dim=1) - 1
ref = torch.stack([full[i, last[i], r.yes] for i in range(len(pairs))]).float()
mine = r.logits(pairs)
check("4 the Yes logit equals the full forward pass's at the last real position",
      torch.allclose(mine, ref, atol=1e-5), f"{mine.tolist()} vs {ref.tolist()}")
check("4b the lengths differ (the padding is exercised)", len(set(enc["attention_mask"].sum(dim=1).tolist())) == 3)

# 5. A pair scores the same in a batch as alone
alone = [r.predict([pair])[0] for pair in pairs]
batch = r.predict(pairs)
check("5 each pair's score in a batch equals its score alone",
      all(abs(a - b) < 1e-5 for a, b in zip(alone, batch)), f"{alone} vs {batch}")

# 6. The score is sigmoid(logit / 5), in the input order; an empty list gives none
check("6 predict = sigmoid(logit / 5), in order",
      all(abs(s - 1 / (1 + math.exp(-x / 5))) < 1e-6 for s, x in zip(batch, mine.tolist())))
check("6b an empty request gives []", r.predict([]) == [])

# 7. load(): the switch picks the loader; without it the cross-encoder path is taken
calls = []
worker_cls = worker.YesLogitReranker
worker.YesLogitReranker = lambda *a, **k: calls.append(a) or "yes-logit"
os.environ["GOV_RERANK_TRIAL_LOADER"] = "yes-logit"
check("7 GOV_RERANK_TRIAL_LOADER=yes-logit loads YesLogitReranker",
      worker.load("m", "rev") == "yes-logit" and calls == [("m", "rev", None)])
del os.environ["GOV_RERANK_TRIAL_LOADER"]
import sentence_transformers  # noqa: E402
sentence_transformers.CrossEncoder = lambda *a, **k: ("cross-encoder", a, k)
got = worker.load("m", "rev")
check("7b unset, the cross-encoder path as before", got[0] == "cross-encoder" and got[1] == ("m",) and got[2] == {"revision": "rev"})
worker.YesLogitReranker = worker_cls

# 8. No remote code: the snapshot holds no .py, and the loader passes trust_remote_code=False
check("8 the snapshot holds no code file", not list(SNAP.glob("*.py")))
src = (HERE / "rerank_worker.py").read_text()
check("8b the loader never passes trust_remote_code=True", "trust_remote_code=True" not in src
      and src.count("trust_remote_code=False") == 2)

print(f"{sum(results)} of {len(results)} passed")
sys.exit(0 if all(results) else 1)
