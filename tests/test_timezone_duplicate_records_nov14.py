"""Timestamps representing one instant must not become separate records."""
import pandas as pd

from windctrl.validation import ControllerValidator


def record(timestamp):
    return {
        "timestamp": timestamp,
        "turbine_id": "WT-SYNTHETIC",
        "wind_speed_mps": 10.0,
        "rotor_speed_rpm": 15.0,
        "blade_pitch_deg": 4.0,
        "generator_temp_c": 75.0,
        "expected_power_kw": 1000.0,
        "actual_power_kw": 1000.0,
        "controller_output_kw": 1000.0,
        "controller_state": "RUNNING",
    }


def test_same_instant_with_different_offsets_is_flagged_twice():
    frame = pd.DataFrame([
        record("2026-11-14T10:00:00Z"),
        record("2026-11-14T15:30:00+05:30"),
    ])
    evaluated = ControllerValidator().validate(frame)
    assert evaluated.status.tolist() == ["FAIL", "FAIL"]
    assert evaluated.failure_reasons.str.contains("duplicate turbine/timestamp").all()


def test_different_instants_remain_distinct():
    frame = pd.DataFrame([
        record("2026-11-14T10:00:00Z"),
        record("2026-11-14T10:01:00Z"),
    ])
    evaluated = ControllerValidator().validate(frame)
    assert evaluated.status.tolist() == ["PASS", "PASS"]
