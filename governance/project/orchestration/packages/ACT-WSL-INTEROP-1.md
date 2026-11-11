# ACT-WSL-INTEROP-1: Windows programs run from WSL again, so the dispatcher reads the GPU's shared memory (DEC-1082 (4))

**For:** the owner's operator, in a plain WSL terminal with `sudo` (a machine setting: the operator's, P-ACT-SPLIT).
Prepared by the CTO, 2026-11-06. The CTO runs no `sudo`.

## Why the spill reading fails
- The dispatcher reads Windows' "Shared Usage" GPU counter through
  `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile` (`dispatch/dispatcher.py:2182`). Today
  every Windows program fails from WSL: `powershell.exe -NoProfile -Command 1` gives `cannot execute binary file:
  Exec format error` (exit 126).
- **The cause:** WSL runs a Windows `.exe` through a kernel binary-format entry named `WSLInterop` (it hands `MZ`
  files to `/init`). That entry is gone. `/proc/sys/fs/binfmt_misc/` holds only `register` and `status`, not even
  Python's entry.
- **When:** systemd (WSL runs with `systemd=true` in `/etc/wsl.conf`) mounted its own `binfmt_misc` at
  **2026-11-03 11:15:07** (`proc-sys-fs-binfmt_misc.mount`, "active (mounted) since"). That replaced the one WSL had
  filled. The last shared reading on record is 11-02 20:57 (660 MiB, P-LB-PRODUCT-1).
- **Why it stays broken:** `systemd-binfmt.service`, which would refill the table, is skipped under WSL on purpose
  (`ConditionVirtualization=!wsl`, "start condition unmet"). So nothing re-registers `WSLInterop` until WSL is
  restarted, and a restart can lose it again the same way.
- **What it costs:** the dispatcher's GPU rule cannot see a spill into shared memory ("shared GPU memory unread"). The
  backstop's other triggers still work: the budget, the backstop line, and an embedder losing layers.

## The fix (two steps; the second keeps it across restarts)
```
# 0. the state before (expect: no WSLInterop; powershell fails with Exec format error)
ls /proc/sys/fs/binfmt_misc/
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -Command 1

# 1. now: register WSL's own entry (WSL's standard registration string)
sudo sh -c 'echo ":WSLInterop:M::MZ::/init:PF" > /proc/sys/fs/binfmt_misc/register'
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -Command 1     # expect: 1

# 2. at every start: a one-shot unit that registers it after systemd's mount, only if it is missing
cd /home/usain/Dynamic-Agentic-Engineering-OS
sudo install -m 644 governance/project/orchestration/packages/ACT-WSL-INTEROP-1/wsl-interop-binfmt.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now wsl-interop-binfmt.service
systemctl is-active wsl-interop-binfmt.service                                          # expect: active
```
**The check after (the CTO):** within two minutes, `dispatch/status.txt`'s GPU rule line shows a shared reading
instead of "shared GPU memory unread".

## Undo
```
sudo systemctl disable --now wsl-interop-binfmt.service
sudo rm /etc/systemd/system/wsl-interop-binfmt.service
sudo systemctl daemon-reload
sudo sh -c 'echo -1 > /proc/sys/fs/binfmt_misc/WSLInterop'      # only to remove the entry itself (WSL's default has it)
```

## Rehearsal (DEC-1057), and what could not be rehearsed
- **Rehearsed:**
  - the failure (exit 126, Exec format error);
  - the empty table;
  - the mount's time and the skipped service, from `systemctl status`;
  - the unit file's syntax: `systemd-analyze verify` reports nothing for it.
- **Not rehearsed:** steps 1 and 2 write as root. The CTO has no `sudo`.
- **The unit does nothing when the entry exists** (`[ -e … ] ||`), so it cannot double-register, and it is skipped
  where `/init` is missing.

**Basis:** question 2 (a spill into shared memory is the failure the GPU rule exists to catch) and question 4 (the
smallest change: WSL's own default restored, no new package). **Note:** this restores WSL's default ability to run
Windows programs from Linux, which any session on this machine had before 11-03. Under our threat model the guard is
the check.
