from __future__ import annotations


def normalize_port(value: int | str) -> int:
    port = int(value)
    if port < 0:
        raise ValueError("port must be non-negative")
    if port >= 65535:
        raise ValueError("port must be <= 65535")
    return port
