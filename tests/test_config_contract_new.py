import pytest
from dataclasses import FrozenInstanceError

from windctrl.validation import ValidationConfig


def test_configuration_is_immutable():
    config = ValidationConfig()
    with pytest.raises(FrozenInstanceError):
        config.tolerance_pct = 2


@pytest.mark.parametrize("field", [
    "tolerance_pct", "zero_tolerance_kw", "max_generator_temp_c",
])
@pytest.mark.parametrize("bad", [float("inf"), float("-inf"), float("nan"), True])
def test_configuration_rejects_non_finite_or_boolean_parameters(field, bad):
    with pytest.raises(ValueError):
        ValidationConfig(**{field: bad})


def test_boundary_tolerance_is_inclusive():
    assert ValidationConfig(tolerance_pct=0).tolerance_pct == 0
    assert ValidationConfig(tolerance_pct=100).tolerance_pct == 100
