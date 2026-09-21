import pandas as pd
import pytest

@pytest.fixture
def row():
    return pd.DataFrame([{"timestamp": "2026-09-01T00:00:00Z", "turbine_id": "WT-001",
        "wind_speed_mps": 10.0, "rotor_speed_rpm": 15.0, "blade_pitch_deg": 3.0,
        "generator_temp_c": 75.0, "expected_power_kw": 1800.0, "actual_power_kw": 1760.0,
        "controller_output_kw": 1800.0, "controller_state": "RUNNING"}])
