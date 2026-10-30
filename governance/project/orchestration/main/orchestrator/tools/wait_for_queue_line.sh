#!/usr/bin/env bash
# Waits until a queue log gains a line matching a pattern (checked every 10 s), then exits printing it, so the
# orchestrator's session wakes at that moment (a background command's exit notifies it).
# Usage: wait_for_queue_line.sh <queue.txt> <grep -E pattern>
until grep -E -q "$2" "$1" 2>/dev/null; do sleep 10; done
grep -E "$2" "$1" | tail -1
