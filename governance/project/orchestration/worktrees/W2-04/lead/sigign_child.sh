#!/usr/bin/env bash
echo "child (setsid ... &): $(grep SigIgn /proc/$$/status)"
python3 -c "import signal; print('python child SIGINT handler:', signal.getsignal(signal.SIGINT))"
