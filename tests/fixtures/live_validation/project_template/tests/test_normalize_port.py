import pytest

from normalize_port import normalize_port


def test_accepts_upper_bound_port() -> None:
    assert normalize_port(65535) == 65535


def test_rejects_out_of_range_port() -> None:
    with pytest.raises(ValueError):
        normalize_port(65536)
