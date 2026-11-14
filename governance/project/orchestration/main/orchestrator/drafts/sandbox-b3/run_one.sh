#!/bin/bash
# usage: run_one.sh VARIANT SCRIPT(probe.py|retr.py)   -- one headless claude -p, the settings file of VARIANT, one script in the sandbox
W=/tmp/claude-1000/b3-probe; V=$1; S=$2
mkdir -p $W/cwd $W/ct
cd $W/cwd || exit 9
export PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH
echo "Run exactly this one command with the Bash tool and reply with its complete output, nothing else: python3 -I $W/$S" | \
CLAUDE_CODE_TMPDIR=$W/ct timeout 400 $HOME/.local/bin/claude -p --output-format stream-json --verbose \
  --settings $W/settings-$V.json --setting-sources "" --tools Bash --strict-mcp-config --disable-slash-commands \
  --no-session-persistence --permission-prompts none --model haiku --max-budget-usd 0.5 > $W/stream-$V-${S%.py}.jsonl 2> $W/stderr-$V-${S%.py}.txt
echo "exit $?"
