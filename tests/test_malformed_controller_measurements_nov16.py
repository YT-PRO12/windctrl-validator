"""Malformed observed values must not silently pass controller checks."""
import pandas as pd

from windctrl.validation import ControllerValidator


def sample(actual):
    return pd.DataFrame([{
        "timestamp": "2026-11-16T09:00:00Z",
        "turbine_id": "WT-SYNTH",
        "wind_speed_mps": 10.0,
        "rotor_speed_rpm": 15.0,
        "blade_pitch_deg": 4.0,
        "generator_temp_c": 75.0,
        "expected_power_kw": 1000.0,
        "actual_power_kw": actual,
        "controller_output_kw": 1000.0,
        "controller_state": "RUNNING",
    }])


def test_nonfinite_or_boolean_measurement_fails_without_mutation():
    for invalid in (float("nan"), float("inf"), True, "not a number"):
        frame = sample(invalid)
        original = frame.copy(deep=True)
        checked = ControllerValidator().validate(frame)
        assert checked.loc[0, "status"] == "FAIL"
        assert "actual_power_kw: missing or non-finite number" in checked.loc[0, "failure_reasons"]
        pd.testing.assert_frame_equal(frame, original)


def test_valid_power_reference_remains_a_pass():
    checked = ControllerValidator().validate(sample(1000.0))
    assert checked.loc[0, "status"] == "PASS"
    assert checked.loc[0, "power_error_pct"] == 0
