"""Row-level checks for demonstration controller test records."""
from dataclasses import dataclass
from math import isfinite
import numpy as np
import pandas as pd

RANGES = {
    "wind_speed_mps": (0, 50), "rotor_speed_rpm": (0, 30),
    "blade_pitch_deg": (0, 90), "generator_temp_c": (-20, 150),
    "expected_power_kw": (0, 2500), "actual_power_kw": (0, 2500),
    "controller_output_kw": (0, 2500),
}
COLUMNS = ["timestamp", "turbine_id", *RANGES, "controller_state"]
MAX_ROWS = 20000

@dataclass(frozen=True)
class ValidationConfig:
    tolerance_pct: float = 5.0
    zero_tolerance_kw: float = 0.5
    max_generator_temp_c: float = 100.0

    def __post_init__(self):
        for name, value in vars(self).items():
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
                raise ValueError(f"{name} must be a finite number")
        if not 0 <= self.tolerance_pct <= 100:
            raise ValueError("tolerance_pct must be within 0..100")
        if not 0 <= self.zero_tolerance_kw <= 100:
            raise ValueError("zero_tolerance_kw must be within 0..100")
        if not -20 <= self.max_generator_temp_c <= 150:
            raise ValueError("max_generator_temp_c must be within -20..150")

def load_csv(source):
    try:
        frame = pd.read_csv(source, nrows=MAX_ROWS + 1)
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeError) as exc:
        raise ValueError("CSV must be a readable UTF-8 table with a header") from exc
    _check_schema(frame)
    return frame

def _check_schema(frame):
    missing = set(COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
    if frame.columns.duplicated().any():
        raise ValueError("Duplicate column names are not allowed")
    if frame.empty:
        raise ValueError("No controller records found")
    if len(frame) > MAX_ROWS:
        raise ValueError(f"Maximum {MAX_ROWS:,} rows per validation")

class ControllerValidator:
    def __init__(self, config=None):
        self.config = config or ValidationConfig()

    def validate(self, frame):
        _check_schema(frame)
        result = frame[COLUMNS].copy().reset_index(drop=True)
        reasons = [[] for _ in range(len(result))]

        def flag(mask, message):
            for idx in np.flatnonzero(np.asarray(mask, dtype=bool)):
                reasons[idx].append(message)

        result["timestamp"] = pd.to_datetime(result["timestamp"], errors="coerce", utc=True, format="ISO8601")
        flag(result.timestamp.isna(), "invalid or missing timestamp")
        result["turbine_id"] = result.turbine_id.astype("string").str.strip()
        flag(result.turbine_id.isna() | result.turbine_id.eq("").fillna(False), "missing turbine ID")
        flag(result.duplicated(["timestamp", "turbine_id"], keep=False), "duplicate turbine/timestamp")
        for column, (low, high) in RANGES.items():
            numeric = pd.to_numeric(result[column], errors="coerce")
            is_bool = result[column].map(lambda x: isinstance(x, (bool, np.bool_)))
            result[column] = numeric.astype(float).mask(is_bool)
            flag(~np.isfinite(result[column]), f"{column}: missing or non-finite number")
            flag(np.isfinite(result[column]) & ~result[column].between(low, high),
                 f"{column}: outside demonstration range [{low}, {high}]")
        cfg = self.config
        flag(result.generator_temp_c.gt(cfg.max_generator_temp_c), "generator over-temperature")
        state = result.controller_state.astype("string").str.strip().str.upper()
        result["controller_state"] = state
        flag(~state.isin(["RUNNING", "IDLE", "SHUTDOWN"]), "unexpected controller state")
        expected = result.expected_power_kw
        flag((expected > 0) & state.ne("RUNNING").fillna(False), "positive demand requires RUNNING state")
        flag((expected == 0) & state.eq("RUNNING").fillna(False), "zero demand requires IDLE or SHUTDOWN")
        valid_expected = expected.between(0, 2500) & np.isfinite(expected)
        for observed, prefix in [("actual_power_kw", "power"), ("controller_output_kw", "controller")]:
            valid = valid_expected & result[observed].between(0, 2500) & np.isfinite(result[observed])
            difference = (result[observed] - expected).where(valid)
            denominator = expected.where(expected > 0)
            pct = difference.abs() / denominator * 100
            result[f"{prefix}_deviation_kw"] = difference.abs()
            result[f"{prefix}_error_pct"] = pct
            allowed = (expected * cfg.tolerance_pct / 100).where(expected > 0, cfg.zero_tolerance_kw)
            flag(valid & (difference.abs() > allowed + 1e-9), f"{prefix} deviation exceeds tolerance")
        result["status"] = ["FAIL" if entries else "PASS" for entries in reasons]
        result["failure_reasons"] = ["; ".join(entries) for entries in reasons]
        result.insert(0, "test_id", np.arange(1, len(result) + 1))
        return result

def summarize(result):
    total = len(result)
    passed = int(result.status.eq("PASS").sum())
    errors = result.power_error_pct.dropna()
    deviation = result.power_deviation_kw.dropna()
    return {
        "total_tests": total, "passed_tests": passed, "failed_tests": total - passed,
        "pass_pct": round(100 * passed / total, 2) if total else 0.0,
        "average_error_pct": round(float(errors.mean()), 4) if len(errors) else None,
        "maximum_error_pct": round(float(errors.max()), 4) if len(errors) else None,
        "maximum_deviation_kw": round(float(deviation.max()), 4) if len(deviation) else None,
        "percentage_comparable_rows": len(errors),
    }

def safe_csv(frame):
    """Neutralize spreadsheet formula prefixes in uploaded text cells."""
    out = frame.copy()
    for col in out.select_dtypes(include=["object", "string"]).columns:
        out[col] = out[col].map(lambda x: "'" + x if isinstance(x, str) and x.lstrip().startswith(("=", "+", "-", "@")) else x)
    return out.to_csv(index=False)
