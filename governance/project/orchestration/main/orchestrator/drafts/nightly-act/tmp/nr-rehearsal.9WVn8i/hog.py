import sys, time
held = []
for i in range(0, int(sys.argv[1]), 16):
    held.append(bytearray(b"x" * (16 * 1024 * 1024))); time.sleep(0.03)
print("hog reached its target", flush=True); time.sleep(60)
