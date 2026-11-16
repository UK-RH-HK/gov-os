# Rehearsal of P-EXAMIN-LEAD-1 (b) on a scratch session (2026-11-16 14:41-14:44)

Scratch only: a throwaway repository `/tmp/gov-os-exa-reh/repo`, a throwaway headless session, the tmux session
`exa-reh`. The real EXAMIN CTO session (9d3404b0-…) and its tmux session were not touched.

## Steps and results
1. Headless session: `claude -p "Say the single word marigold and nothing else." --output-format json --model claude-haiku-5-5`
   in the scratch repo -> session `2bb60cde-af60-4c72-a7fb-dfcba081c7df`, result `marigold`.
2. The package's start form, with a scratch name and ticket:
   ```
   tmux new -d -s exa-reh 'cd /tmp/gov-os-exa-reh/repo && env -u GOV_DEV_TIERS -u GOV_ROLE -u GOV_TICKET ~/.local/bin/claude --remote-control "EXAMIN CTO rehearsal" --resume 2bb60cde-af60-4c72-a7fb-dfcba081c7df --model claude-haiku-5-5 --settings "{\"env\":{\"GOV_ROLE\":\"orchestrator\",\"GOV_TICKET\":\"exa-reh\"}}"'
   ```
   - **The first interactive start in a folder shows the workspace-trust prompt** ("Is this a project you created or one
     you trust?"), default "No, exit". Accepted with Down, Enter. EXAMIN's copy ran interactively in tmux on 11-15
     (`examin-cto`), so it should already be trusted; the switch must check (capture the pane) and accept once if shown.
   - It **resumed with its context** (the earlier exchange shown) and printed `/remote-control is active · Continue here,
     on your phone, or at https://claude.ai/code/session_…`: the session is visible in the app.
3. **tmux wake:** `send-keys "<question>" Enter`: the text was typed but the first Enter was swallowed (the known quirk);
   a second `send-keys Enter` submitted it. Asked which word it said before: `marigold`. **Context kept.** The wake
   tool must send Enter twice (or text, a pause, then Enter) and check the pane.
4. **Cross-session wake:** the session appears to ListAgents as **`repo-e9`** (a name derived from its folder, not the
   `--remote-control` label). SendMessage to that name arrived as a message in the session and was acted on (`tulip`).
   **For the switch:** the real session's name will be derived from the copy's folder (e.g. `examin-…`); after the start,
   read it from ListAgents and write it to a name file (as `log/cto-name.txt`), which the waking side reads.
5. Ended by its tmux session name (`tmux kill-session -t exa-reh`, my own scratch session) and waited by pid
   (`proc.sh wait --max 20 3576773`): gone.

## Differences from the package
- The trust prompt on a first interactive start (check and accept once).
- The tmux wake needs a second Enter.
- The cross-session name is folder-derived; record it after the start.
- None blocks (b).
