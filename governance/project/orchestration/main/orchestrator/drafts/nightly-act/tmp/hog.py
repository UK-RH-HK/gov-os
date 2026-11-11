"""A planted memory hog: touches memory in 16 MB steps up to the given MB, then sleeps. Prints each step."""
import sys
import time

limit_mb = int(sys.argv[1])
held = []
for i in range(0, limit_mb, 16):
    held.append(bytearray(b"x" * (16 * 1024 * 1024)))
    print(f"hog holds {i + 16} MB", flush=True)
    time.sleep(0.05)
print("hog reached its target and sleeps", flush=True)
time.sleep(30)
