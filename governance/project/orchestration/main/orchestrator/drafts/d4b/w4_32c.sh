#!/usr/bin/env bash
# W2-32 round 2 with the pool OFF (the product as today, at the same commit as w4-32b): what S11 adds. One GPU job.
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/d4b
bash $D/w4_point.sh w4-32c 1aeae78874d1 0 && bash $D/w4_32_product.sh w4-32c w4-32c-product
