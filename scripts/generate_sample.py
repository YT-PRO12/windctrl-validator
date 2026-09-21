"""Generate a reproducible synthetic fixture (not manufacturer telemetry)."""
from pathlib import Path
import numpy as np
import pandas as pd

rng = np.random.default_rng(20260921)
frames = []
for number in range(1, 4):
    n = 120
    wind = np.clip(10 + 3 * np.sin(np.linspace(0, 4 * np.pi, n)) + rng.normal(0, .2, n), 0, 25)
    expected = np.clip(1800 * (wind / 12)**3, 0, 2000)
    frame = pd.DataFrame({"timestamp": pd.date_range("2026-09-01", periods=n, freq="5min", tz="UTC").astype(str),
        "turbine_id": f"WT-{number:03d}", "wind_speed_mps": wind.round(2),
        "rotor_speed_rpm": (wind * 1.2).round(2), "blade_pitch_deg": np.clip((wind-10)*3, 0, 20).round(2),
        "generator_temp_c": (70 + 6 * np.sin(np.linspace(0,6,n))).round(2),
        "expected_power_kw": expected.round(2),
        "actual_power_kw": (expected * rng.normal(1,.014,n)).round(2),
        "controller_output_kw": (expected * rng.normal(1,.009,n)).round(2),
        "controller_state": "RUNNING"})
    # Known failure modes and an exact-zero passing case for demonstration.
    frame.loc[10:14, "actual_power_kw"] = (frame.loc[10:14,"expected_power_kw"] * .88).round(2)
    frame.loc[35:37, "generator_temp_c"] = 108
    frame.loc[55, "wind_speed_mps"] = np.nan
    frame.loc[65, "controller_state"] = "UNKNOWN"
    frame.loc[75, "rotor_speed_rpm"] = -2
    frame.loc[85, "controller_output_kw"] = 0
    frame.loc[100, ["expected_power_kw","actual_power_kw","controller_output_kw"]] = 0
    frame.loc[100, "controller_state"] = "IDLE"
    frames.append(frame)
target = Path(__file__).resolve().parents[1] / "data/controller_samples.csv"
target.parent.mkdir(exist_ok=True)
pd.concat(frames, ignore_index=True).to_csv(target, index=False)
print(target)
