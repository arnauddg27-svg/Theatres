import os

# Collection lanes refresh the holdover registry from Polymarket; never from
# a test run (holdover.py). Holdover tests opt back in explicitly.
os.environ.setdefault("HOLDOVER_COLLECTION", "0")
