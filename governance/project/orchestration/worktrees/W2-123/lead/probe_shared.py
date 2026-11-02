"""The ticket's health probe on the real servers, once each (a read: one fixed text; never a stop or a start)."""
import json

from gov.retrieval import ollama

for server in ("shared", "query"):
    print(json.dumps(ollama.probe(server)))
