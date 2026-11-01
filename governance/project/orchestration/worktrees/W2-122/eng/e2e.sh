#!/usr/bin/env bash
# End-to-end check of gov rebuild --seed and the semantic failure, on a throwaway repository (W2-122 engineer).
set -u
WORK=$(mktemp -d /tmp/gov-os-lead-W2-122/e2e.XXXXXX)
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-122/src
export GOV_REBUILD_LOCK="$WORK/rebuild.lock" OLLAMA_HOST=127.0.0.1:9 GOV_QUERY_OLLAMA_HOST=127.0.0.1:9
export GOV_OLLAMA_BIN="$WORK/no-ollama-here" GOV_SECRETS_CACHE=""
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t.invalid GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t.invalid
mkdir -p "$WORK/repo/governance/project" "$WORK/repo/docs"
cd "$WORK/repo" || exit 1
git init -q -b main
printf '.gov-runtime/\n' > .gitignore
printf 'namespaces:\n  all: {paths: ["**"], embedding_policy: embedded}\n' > governance/project/path-map.yaml
printf 'pear trees\n' > docs/pear.md
cp /home/usain/gov-os-worktrees/W2-122/.gitleaks.toml .gitleaks.toml
git add -A && git commit -q -m one
echo "== --no-embeddings --seed (no key configured)"
python3 -m gov.cli.main rebuild --no-embeddings --seed --json > "$WORK/a.json" 2> "$WORK/a.err"; echo "exit=$?"
python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d['ok'], d['result'].get('seed'))" "$WORK/a.json"
echo "== --no-embeddings --seed <folder without a store>"
python3 -m gov.cli.main rebuild --no-embeddings --seed "$WORK" --json > "$WORK/b.json" 2> "$WORK/b.err"; echo "exit=$?"
python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d['ok'], d['result'].get('seed'))" "$WORK/b.json"
echo "== full rebuild, endpoint closed"
python3 -m gov.cli.main rebuild --json > "$WORK/c.json" 2> "$WORK/c.err"; echo "exit=$?"
python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d['ok'], d.get('error'))" "$WORK/c.json"
ls "$WORK/repo/.gov-runtime/rebuild"
rm -rf "$WORK"
