"""Use self-contained synthetic telemetry to test independent control limits."""
import pandas as pd

from windctrl.validation import ControllerValidator, ValidationConfig


def frame(actual=1000.0, command=1000.0):
    return pd.DataFrame([{
        "timestamp": "2026-11-11T00:00:00Z",
        "turbine_id": "WT-TEST",
        "wind_speed_mps": 10,
        "rotor_speed_rpm": 15,
        "blade_pitch_deg": 4,
        "generator_temp_c": 75,
        "expected_power_kw": 1000,
        "actual_power_kw": actual,
        "controller_output_kw": command,
        "controller_state": "RUNNING",
    }])


def test_only_measured_output_is_outside_tolerance():
    result = ControllerValidator().validate(frame(actual=1100))
    assert result.loc[0, "status"] == "FAIL"
    assert "power deviation" in result.loc[0, "failure_reasons"]
    assert "controller deviation" not in result.loc[0, "failure_reasons"]


def test_only_controller_command_is_outside_tolerance():
    result = ControllerValidator().validate(frame(command=1100))
    assert result.loc[0, "status"] == "FAIL"
    assert "controller deviation" in result.loc[0, "failure_reasons"]
    assert "power deviation" not in result.loc[0, "failure_reasons"]


def test_configured_tolerance_changes_status_without_mutating_input():
    source = frame(actual=1030, command=1030)
    strict = ControllerValidator(ValidationConfig(tolerance_pct=2)).validate(source)
    relaxed = ControllerValidator(ValidationConfig(tolerance_pct=5)).validate(source)
    assert strict.loc[0, "status"] == "FAIL"
    assert relaxed.loc[0, "status"] == "PASS"
    assert source.loc[0, "actual_power_kw"] == 1030
