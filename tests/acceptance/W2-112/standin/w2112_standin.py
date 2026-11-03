"""The stand-in reranker model of the W2-112 acceptance tests: no model, no GPU, no network.

The tests copy this file into a throwaway reranker environment (a real ``python -m venv`` under a temporary
``HOME``), beside two small packages that import from it: ``sentence_transformers`` (its ``CrossEncoder``) and
``torch`` (its ``cuda`` probes). A copy of it also serves as ``nvidia-smi`` on the searches' ``PATH``. So whatever
loads the reranker the way the library is used today (``CrossEncoder(MODEL, revision=REVISION)`` and ``predict``)
loads this one, and whatever asks how much GPU memory is free gets the figure the test set.

It is tolerant on purpose: any arguments are taken, ``rank`` works as well as ``predict``, the device can be given
by name or left to the library (then the GPU when the stand-in has one that is not hidden by
``CUDA_VISIBLE_DEVICES``), and unknown ``torch`` names answer harmlessly.

What it does is read from outside, through files in its state folder (named in ``w2112_standin.json`` beside it):

- ``config.json``, read again at every load and every scoring call: delays, failures, and the stand-in GPU, for
  every process or for one process id;
- ``log/``: one file per event (``load``, ``load-failed``, ``predict-begin``, ``predict-end``, ``move``), each with
  its process id, its time and what it was asked; a ``load`` also records how many of the test's private GPU slots
  (the lock files of the GPU slot rule, DEC-1033) were held when the model loaded.

A score is a function of the query and the text alone (``score``), so the same pair always gets the same score in
any process, in any batch, on any device.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys
import time
from pathlib import Path

__version__ = "6.1.0"  # the sentence-transformers pin of ADR-0002 §2
TORCH_VERSION = "2.14.1+cu130"
_SEQUENCE = itertools.count()


# ---------------------------------------------------------------- the state folder


def _state() -> Path:
    here = Path(__file__).resolve()
    named = here.with_name("w2112_standin.json")
    if named.is_file():
        return Path(json.loads(named.read_text(encoding="utf-8"))["state"])
    return here.parent  # the copy in the state folder itself


def config() -> dict:
    try:
        return json.loads((_state() / "config.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _mine(setting: str, default=None):
    """``setting`` for this process: its own entry under ``pids`` first, then the one for every process."""
    found = config()
    own = (found.get("pids") or {}).get(str(os.getpid())) or {}
    return own.get(setting, found.get(setting, default))


def log(event: str, **fields) -> None:
    folder = _state() / "log"
    folder.mkdir(parents=True, exist_ok=True)
    record = {"event": event, "pid": os.getpid(), "ppid": os.getppid(), "time": time.time(), **fields}
    name = f"{time.time_ns():020d}-{os.getpid()}-{next(_SEQUENCE):06d}-{event}.json"
    partial = folder / f".{name}.part"
    partial.write_text(json.dumps(record), encoding="utf-8")
    os.replace(partial, folder / name)


def slots_held():
    """How many of the GPU slots (``gov-os-rerank-gpu-<i>.lock`` in the test's private lock folder, named in
    ``config.json``) are held at this moment, by this process or another; None when the test named no folder."""
    found = config()
    folder = found.get("lock_dir")
    if not folder:
        return None
    import fcntl

    held = 0
    for number in range(int(found.get("slots", 2))):
        path = os.path.join(folder, f"gov-os-rerank-gpu-{number}.lock")
        try:
            descriptor = os.open(path, os.O_RDWR)  # never creates a slot's file
        except OSError:
            continue
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        except OSError:
            held += 1
        finally:
            os.close(descriptor)
    return held


def _attempt() -> int:
    """This load's number among every load attempted under this state folder, from 1."""
    folder = _state() / "attempts"
    folder.mkdir(parents=True, exist_ok=True)
    for number in itertools.count(1):
        try:
            os.close(os.open(folder / str(number), os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            return number
        except FileExistsError:
            continue
    raise AssertionError("unreachable")


# ---------------------------------------------------------------- the scores


def score(query: str, text: str) -> float:
    """The stand-in model's score of one pair: a number in [-10, 10) fixed by the pair alone."""
    digest = hashlib.sha256((str(query) + "\x1f" + str(text)).encode("utf-8")).digest()
    return int.from_bytes(digest[:6], "big") / float(1 << 48) * 20.0 - 10.0


def scores(query: str, texts) -> list[float]:
    """The scores a private reranker of this model gives ``texts`` for ``query``, in the order given (no log)."""
    return [score(query, text) for text in texts]


class Scores(list):
    """A list of floats that also answers ``tolist()``, as the library's arrays do."""

    def tolist(self):
        return list(self)


# ---------------------------------------------------------------- the stand-in GPU


def _gpu() -> dict:
    return config().get("gpu") or {}


def _hidden() -> bool:
    visible = os.environ.get("CUDA_VISIBLE_DEVICES")
    return visible is not None and visible.strip() in ("", "-1", "none", "None", "NoDevFiles")


def cuda_is_available() -> bool:
    return bool(_gpu().get("present")) and not _hidden()


def _need_cuda() -> None:
    if not cuda_is_available():
        raise RuntimeError("No CUDA GPUs are available")


def cuda_device_count() -> int:
    return 1 if cuda_is_available() else 0


def cuda_mem_get_info(device=None):
    _need_cuda()
    gpu = _gpu()
    return int(gpu.get("free", 0)), int(gpu.get("total", 0))


def cuda_get_device_name(device=None) -> str:
    _need_cuda()
    return str(_gpu().get("name", "Stand-in GPU"))


class _Properties:
    def __init__(self):
        gpu = _gpu()
        self.name = str(gpu.get("name", "Stand-in GPU"))
        self.total_memory = int(gpu.get("total", 0))
        self.major, self.minor, self.multi_processor_count = 12, 0, 70


def cuda_get_device_properties(device=None):
    _need_cuda()
    return _Properties()


def _device_name(device) -> str:
    """``cuda`` or ``cpu`` (or another type) from whatever names a device."""
    if device is None:
        return "cuda" if cuda_is_available() else "cpu"
    text = str(getattr(device, "type", None) or device).strip().lower()
    if text.isdigit():
        return "cuda"
    return text.split(":", 1)[0] or "cpu"


class Device:
    """``torch.device``: a type and an index."""

    def __init__(self, kind="cpu", index=None):
        text = str(getattr(kind, "type", kind))
        if ":" in text:
            text, _, number = text.partition(":")
            index = int(number)
        self.type, self.index = text, index

    def __str__(self):
        return self.type if self.index is None else f"{self.type}:{self.index}"

    __repr__ = __str__

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))


class Anything:
    """What an unknown ``torch`` name gives: callable, a context, falsy, and any attribute is another of it."""

    def __call__(self, *args, **kwargs):
        if len(args) == 1 and callable(args[0]) and not kwargs:
            return args[0]  # used as a decorator
        return self

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return self

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def __bool__(self):
        return False

    def __int__(self):
        return 0

    def __float__(self):
        return 0.0

    def __iter__(self):
        return iter(())


ANYTHING = Anything()


def nvidia_smi(argv) -> int:
    """``nvidia-smi`` for the stand-in GPU: the summary, ``-L``, ``--query-gpu`` and ``--query-compute-apps``."""
    gpu = _gpu()
    if not gpu.get("present"):
        print("NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver.", file=sys.stderr)
        return 9
    mib = 1024 * 1024
    total, free = int(gpu.get("total", 0)) // mib, int(gpu.get("free", 0)) // mib
    name = str(gpu.get("name", "Stand-in GPU"))
    fields = {"index": "0", "name": name, "uuid": "GPU-00000000-0000-0000-0000-000000000000",
              "memory.total": f"{total}", "memory.free": f"{free}", "memory.used": f"{total - free}",
              "memory.reserved": "0", "utilization.gpu": "0", "utilization.memory": "0", "temperature.gpu": "40",
              "driver_version": "000.00", "pci.bus_id": "00000000:01:00.0", "count": "1", "pstate": "P8",
              "power.draw": "10.00", "compute_mode": "Default"}
    units = {"memory.total": " MiB", "memory.free": " MiB", "memory.used": " MiB", "memory.reserved": " MiB",
             "utilization.gpu": " %", "utilization.memory": " %", "power.draw": " W"}
    query, csv_format = None, ""
    for index, argument in enumerate(argv):
        if argument.startswith("--query-gpu=") or argument.startswith("--query-compute-apps="):
            query = argument
        elif argument in ("--query-gpu", "--query-compute-apps") and index + 1 < len(argv):
            query = f"{argument}={argv[index + 1]}"
        elif argument.startswith("--format="):
            csv_format = argument.split("=", 1)[1]
        elif argument == "--format" and index + 1 < len(argv):
            csv_format = argv[index + 1]
    header, plain = "noheader" not in csv_format, "nounits" in csv_format
    if "-L" in argv or "--list-gpus" in argv:
        print(f"GPU 0: {name} (UUID: {fields['uuid']})")
        return 0
    if query and query.startswith("--query-gpu="):
        asked = [part.strip() for part in query.split("=", 1)[1].split(",") if part.strip()]
        if header:
            print(", ".join(asked if plain else [f"{part} [{units[part].strip()}]" if part in units else part
                                                 for part in asked]))
        print(", ".join(fields.get(part, "[N/A]") + ("" if plain else units.get(part, "")) for part in asked))
        return 0
    if query and query.startswith("--query-compute-apps="):
        asked = [part.strip() for part in query.split("=", 1)[1].split(",") if part.strip()]
        if header:
            print(", ".join(asked))
        for holder in gpu_holders():
            row = {"pid": str(holder), "process_name": "python", "used_memory": "2600" if plain else "2600 MiB",
                   "gpu_uuid": fields["uuid"], "name": "python"}
            print(", ".join(row.get(part, "[N/A]") for part in asked))
        return 0
    print(f"| NVIDIA-SMI stand-in | {name} | {total - free}MiB / {total}MiB |")
    return 0


def _alive(pid: int) -> bool:
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8") as handle:
            return handle.read().rsplit(")", 1)[1].split()[0] != "Z"
    except (OSError, IndexError):
        return False


def events(kind: str | None = None) -> list[dict]:
    folder = _state() / "log"
    found = []
    for path in sorted(folder.glob("[0-9]*.json")) if folder.is_dir() else []:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if kind is None or record.get("event") == kind:
            found.append(record)
    return found


def gpu_holders() -> list[int]:
    """The live processes that hold the stand-in model on the stand-in GPU."""
    device: dict[int, str] = {}
    for record in events():
        if record["event"] in ("load", "move"):
            device[record["pid"]] = record["device"]
    return [pid for pid, name in device.items() if name == "cuda" and _alive(pid)]


# ---------------------------------------------------------------- the model


def _texts_of(sentences):
    """``(pairs, single)``: the pairs asked, and whether one bare pair was given."""
    if isinstance(sentences, (list, tuple)) and len(sentences) == 2 and all(isinstance(s, str) for s in sentences):
        return [tuple(sentences)], True
    return [tuple(pair) for pair in sentences], False


def _scored(pairs, how: str):
    queries = []
    for query, _ in pairs:
        if query not in queries:
            queries.append(query)
    log("predict-begin", queries=queries, pairs=len(pairs), how=how, device=_device_name(None))
    delay = float(_mine("predict_delay", 0.0) or 0.0)
    if delay:
        time.sleep(delay)
    if _mine("predict_error", False):
        log("predict-end", queries=queries, pairs=len(pairs), error=True)
        raise RuntimeError("the stand-in model failed to score (the test asked it to)")
    result = [score(query, text) for query, text in pairs]
    log("predict-end", queries=queries, pairs=len(pairs), error=False)
    return result


class _Inner:
    """``CrossEncoder.model``: where the model's device can be read and changed."""

    def __init__(self, outer):
        self._outer = outer
        self.config = ANYTHING

    @property
    def device(self):
        return Device(self._outer._device)

    def to(self, *args, **kwargs):
        self._outer.to(*args, **kwargs)
        return self

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return ANYTHING


class CrossEncoder:
    """``sentence_transformers.CrossEncoder`` without a model."""

    def __init__(self, *args, **kwargs):
        model = args[0] if args else kwargs.get("model_name_or_path", kwargs.get("model_name"))
        requested = kwargs.get("device")
        attempt = _attempt()
        fail_first = int(config().get("fail_loads", 0) or 0)
        fields = {"attempt": attempt, "model": model, "revision": kwargs.get("revision"),
                  "args": [repr(value) for value in args], "kwargs": {key: repr(value) for key, value in kwargs.items()},
                  "requested_device": None if requested is None else str(requested),
                  "executable": sys.executable, "prefix": sys.prefix,
                  "hf_hub_offline": os.environ.get("HF_HUB_OFFLINE"),
                  "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"), "home": os.environ.get("HOME")}
        delay = float(_mine("load_delay", 0.0) or 0.0)
        if delay:
            time.sleep(delay)
        if config().get("fail_all_loads") or attempt <= fail_first:
            log("load-failed", **fields)
            raise OSError("the stand-in model could not be loaded (the test asked it to fail)")
        self._device = _device_name(requested)
        if self._device == "cuda" and not cuda_is_available():
            log("load-failed", **fields)
            raise RuntimeError("Found no NVIDIA driver on your system")
        log("load", device=self._device, slots_held=slots_held(), **fields)
        self.model = _Inner(self)
        self.tokenizer = ANYTHING
        self.max_length = kwargs.get("max_length", 512)
        self.config = ANYTHING

    @property
    def device(self):
        return Device(self._device)

    def to(self, *args, **kwargs):
        target = args[0] if args else kwargs.get("device")
        if target is not None and not isinstance(target, type) and not hasattr(target, "is_floating_point"):
            name = _device_name(target)
            if name in ("cuda", "cpu") and name != self._device:
                self._device = name
                log("move", device=name)
        return self

    def cpu(self):
        return self.to("cpu")

    def cuda(self, *args, **kwargs):
        return self.to("cuda")

    def eval(self):
        return self

    def half(self):
        return self

    def bfloat16(self):
        return self

    def float(self):
        return self

    def predict(self, sentences, *args, **kwargs):
        pairs, single = _texts_of(sentences)
        result = _scored(pairs, "predict")
        return result[0] if single else Scores(result)

    __call__ = predict

    def rank(self, query, documents, top_k=None, return_documents=False, *args, **kwargs):
        documents = list(documents)
        result = _scored([(query, document) for document in documents], "rank")
        ranked = sorted(range(len(documents)), key=lambda index: -result[index])
        answers = [{"corpus_id": index, "score": result[index],
                    **({"text": documents[index]} if return_documents else {})} for index in ranked]
        return answers[:top_k] if top_k else answers

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return ANYTHING
