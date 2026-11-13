#!/bin/bash
# how each start form leaves SIGINT in a Python child: 1 = ignored
P='import signal; print(int(signal.getsignal(signal.SIGINT) == signal.SIG_IGN))'
echo "direct: $(python3 -c "$P")"
echo "bg-job: $(python3 -c "$P" & wait)"
echo "setsid-bg (lead_verify form): $(setsid python3 -c "$P" < /dev/null & wait)"
echo "setsid-fg: $(setsid -w python3 -c "$P")"
