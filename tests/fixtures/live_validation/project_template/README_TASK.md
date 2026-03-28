# Live Validation Task

Fix the port-normalization bug so the valid upper bound `65535` is accepted.

Run:

`python -m pytest -q tests/test_normalize_port.py`

Keep the change minimal and restricted to what the test requires.
