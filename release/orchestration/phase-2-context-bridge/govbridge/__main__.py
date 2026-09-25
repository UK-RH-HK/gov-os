"""``python -m govbridge <command> ...`` -- see govbridge/cli.py for the command list."""
import sys

from govbridge.cli import main

if __name__ == "__main__":
    sys.exit(main())
