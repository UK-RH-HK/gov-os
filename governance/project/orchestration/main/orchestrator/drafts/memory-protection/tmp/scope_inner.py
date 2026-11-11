import os, subprocess, sys, time
# Runs INSIDE a transient user scope (TasksMax=40, MemoryHigh=150M, no MemoryMax, so no kernel kill is possible).
cg = '/sys/fs/cgroup' + open('/proc/self/cgroup').read().strip().split(':', 2)[2]
print('scope cgroup:', cg[len('/sys/fs/cgroup'):])
rd = lambda n: open(cg + '/' + n).read().strip()
print('pids.max=%s memory.high=%s memory.max=%s' % (rd('pids.max'), rd('memory.high'), rd('memory.max')))
kids = []
refused = 0
for i in range(100):
    try:
        kids.append(subprocess.Popen(['sleep', '5']))
    except OSError:
        refused += 1
print('100 spawn attempts: %d started, %d refused by the task limit; pids.current=%s; pids.events: %s' % (len(kids), refused, rd('pids.current'), rd('pids.events').replace('\n', ' ')))
for k in kids:
    k.kill()
for k in kids:
    k.wait()
buf = bytearray(400 * 1024 * 1024)
for i in range(0, len(buf), 4096):
    buf[i] = 1
time.sleep(1)
print('hog of 400 MB: memory.current %.0f MB, swapped out %.0f MB (limit high = 150 MB)' % (int(rd('memory.current')) / 1e6, int(rd('memory.swap.current')) / 1e6))
print('memory.events:', rd('memory.events').replace('\n', ' '))
