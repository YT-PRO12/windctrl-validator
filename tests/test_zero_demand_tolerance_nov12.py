"""Zero demand uses absolute kW tolerance, never relative division by zero."""
import pandas as pd

from windctrl.validation import ControllerValidator, ValidationConfig


def input_frame(actual):
    return pd.DataFrame([{
        "timestamp": "2026-11-12T10:00:00Z",
        "turbine_id": "WT-SYNTH",
        "wind_speed_mps": 0,
        "rotor_speed_rpm": 0,
        "blade_pitch_deg": 0,
        "generator_temp_c": 25,
        "expected_power_kw": 0.0,
        "actual_power_kw": actual,
        "controller_output_kw": 0.0,
        "controller_state": "IDLE",
    }])


def test_deviation_below_absolute_tolerance_is_allowed():
    result = ControllerValidator(ValidationConfig(zero_tolerance_kw=0.5)).validate(
        input_frame(0.4)
    )
    assert result.loc[0, "status"] == "PASS"
    assert pd.isna(result.loc[0, "power_error_pct"])


def test_absolute_tolerance_above_limit_fails():
    result = ControllerValidator(ValidationConfig(zero_tolerance_kw=0.5)).validate(
        input_frame(0.6)
    )
    assert result.loc[0, "status"] == "FAIL"
    assert "power deviation exceeds tolerance" in result.loc[0, "failure_reasons"]
