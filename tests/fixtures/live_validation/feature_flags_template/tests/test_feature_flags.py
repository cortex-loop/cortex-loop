from __future__ import annotations

import pytest

from feature_flags.evaluator import is_flag_active
from feature_flags.models import FeatureFlag


def test_disabled_flag_is_inactive() -> None:
    flag = FeatureFlag(name="new-homepage", enabled=False)

    assert is_flag_active(flag, user_key="user-1", country="jp") is False


def test_deny_country_wins_over_allow_and_rollout() -> None:
    flag = FeatureFlag(
        name="promo-banner",
        rollout_percentage=100,
        allow_countries=("US", "CA"),
        deny_countries=("CA",),
    )

    assert is_flag_active(flag, user_key="user-1", country="ca") is False
    assert is_flag_active(flag, user_key="user-1", country="us") is True


def test_allow_country_restricts_evaluation() -> None:
    flag = FeatureFlag(
        name="regional-launch",
        allow_countries=("JP", "US"),
    )

    assert is_flag_active(flag, user_key="user-1", country="jp") is True
    assert is_flag_active(flag, user_key="user-1", country="de") is False


def test_rollout_edge_cases_zero_and_hundred() -> None:
    disabled_rollout = FeatureFlag(name="off-rollout", rollout_percentage=0)
    full_rollout = FeatureFlag(name="full-rollout", rollout_percentage=100)

    assert is_flag_active(disabled_rollout, user_key="user-1", country="us") is False
    assert is_flag_active(full_rollout, user_key="user-1", country="us") is True


def test_rollout_is_deterministic_for_same_user_key() -> None:
    flag = FeatureFlag(name="fifty-percent", rollout_percentage=50)

    first = is_flag_active(flag, user_key="stable-user", country="us")
    second = is_flag_active(flag, user_key="stable-user", country="us")
    third = is_flag_active(flag, user_key="stable-user", country="us")

    assert first is second is third


def test_feature_flag_validation_rejects_blank_name_and_invalid_rollout() -> None:
    with pytest.raises(ValueError, match="name must be non-empty"):
        FeatureFlag(name="   ")

    with pytest.raises(ValueError, match="rollout_percentage must be between 0 and 100"):
        FeatureFlag(name="bad-rollout", rollout_percentage=101)
